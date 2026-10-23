"""Run every strategy against one immutable shared price table."""
import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path

import pandas as pd

from btc_lab.data import DataError, load_verified, sha256, utc_now, validate_prices, write_json
from btc_lab.engine import Costs, backtest
from btc_lab.strategies import load_catalog, signals

WARMUP = 200


def implementation_hash(root):
    digest = hashlib.sha256()
    for path in sorted((Path(root)/'btc_lab').rglob('*.py')):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def prepared_signals(strategy, candles):
    """Reset indicators at every gap and mask the shared warmup in each segment."""
    entry = pd.Series(False, index=candles.index)
    exit_ = pd.Series(False, index=candles.index)
    groups = candles.index.to_series().diff().ne(pd.Timedelta(hours=1)).cumsum()
    for _, segment in candles.groupby(groups):
        if len(segment) < WARMUP:
            continue
        en, ex = signals(strategy, segment)
        entry.loc[segment.index[WARMUP-1:]] = en.iloc[WARMUP-1:]
        exit_.loc[segment.index[WARMUP-1:]] = ex.iloc[WARMUP-1:]
    return entry, exit_


def run_all(root, start=None, end=None, initial_cash=10000.0, gap_policy='pause'):
    root = Path(root)
    candles, manifest = load_verified(root)
    # Date-only end means all hours in that UTC calendar day; datetimes are inclusive.
    if start:
        candles = candles.loc[pd.Timestamp(start, tz='UTC'):]
    if end:
        stop = pd.Timestamp(end, tz='UTC')
        if len(end) == 10:
            stop += pd.Timedelta(hours=23)
        candles = candles.loc[:stop]
    validate_prices(candles, contiguous=(gap_policy == 'strict'))
    if len(candles) <= WARMUP+1:
        raise DataError('Choose more than 201 hours so indicators can warm up before trading.')
    segments = candles.index.to_series().diff().ne(pd.Timedelta(hours=1)).cumsum()
    candidates = [segment.index[WARMUP] for _, segment in candles.groupby(segments) if len(segment) > WARMUP]
    if not candidates or candidates[0] == candles.index[-1]:
        raise DataError('No segment has enough consecutive hourly candles after warmup to begin trading.')
    first_opportunity = candidates[0]
    catalog = load_catalog(root/'sources/strategies.json')
    results, all_equity, all_trades = [], {}, {}
    for strategy in catalog:
        entry, exit_ = prepared_signals(strategy, candles)
        stats, equity, trades = backtest(candles, entry, exit_, initial_cash=initial_cash, warmup=WARMUP, gap_policy=gap_policy)
        stats.update(strategy_id=strategy['id'], strategy=strategy['title'], kind='hourly signal adaptation')
        results.append(stats)
        all_equity[strategy['id']] = equity
        all_trades[strategy['id']] = trades
    entry = pd.Series(False, index=candles.index)
    entry.loc[first_opportunity-pd.Timedelta(hours=1)] = True
    stats, equity, trades = backtest(candles, entry, pd.Series(False, index=candles.index),
                                     initial_cash=initial_cash, warmup=WARMUP, gap_policy=gap_policy)
    stats.update(strategy_id='buy_and_hold', strategy='Buy and hold (reference)', kind='benchmark')
    results.append(stats)
    all_equity['buy_and_hold'], all_trades['buy_and_hold'] = equity, trades
    summary = pd.DataFrame(results).sort_values('return_pct', ascending=False)
    report_dir = root/'reports'
    report_dir.mkdir(exist_ok=True)
    outputs = {}
    for strategy_id, trade_table in all_trades.items():
        trade_table.to_csv(report_dir/f'{strategy_id}_trades.csv', index=False)
        outputs[f'{strategy_id}_trades.csv'] = sha256((report_dir/f'{strategy_id}_trades.csv').read_bytes())
    summary.to_csv(report_dir/'summary.csv', index=False)
    pd.DataFrame(all_equity).to_csv(report_dir/'equity.csv.gz', compression={'method': 'gzip', 'mtime': 0})
    for name in ('summary.csv', 'equity.csv.gz'):
        outputs[name] = sha256((report_dir/name).read_bytes())
    run = dict(status='completed_on_real_archived_prices', created_at=utc_now(),
               exchange='Binance spot', symbol='BTCUSDT', interval='1h',
               requested_start_month=manifest['requested_start_month'], requested_end_month=manifest['requested_end_month'],
               source_coverage_status=manifest['status'], source_missing_hours=manifest['missing_hours'],
               first_candle=candles.index[0].isoformat(), last_candle=candles.index[-1].isoformat(),
               first_trade_opportunity=first_opportunity.isoformat(), rows=len(candles),
               gap_policy=gap_policy, gap_events=int(candles.index.to_series().diff().gt(pd.Timedelta(hours=1)).sum()),
               gap_handling='No filling; no execution across gaps; reset indicators and wait 200 consecutive candles; existing positions stay held.',
               warmup_candles=WARMUP, strategies=len(catalog), benchmark='buy_and_hold',
               initial_cash_usdt=initial_cash, fee_per_side=Costs().fee, slippage_per_side=Costs().slippage,
               execution='Completed-candle signals; next open; long/cash; all-in; no leverage. Final close liquidation.',
               dataset_sha256=manifest['dataset_sha256'], catalog_sha256=sha256((root/'sources/strategies.json').read_bytes()),
               implementation_sha256=implementation_hash(root), python_version=platform.python_version(),
               dependency_versions={name: version(name) for name in ('numpy', 'pandas', 'TA-Lib')},
               outputs_sha256=outputs,
               limitations=['Hourly signal adaptations, not exact native Freqtrade backtests.',
                            'Native strategy ROI targets and stoploss rules are omitted for all strategies.',
                            'No intrabar price path, partial fills, exchange lot rounding, spread model or funding.',
                            'Missing hours are not filled. Positions remain held during missing hours and indicator warmup; drawdown during gaps cannot be observed.',
                            'Historical comparisons do not predict future profits; no parameter optimization was performed.'])
    write_json(report_dir/'run.json', run)
    lines = ['# Actual historical comparison', '',
             'Source: **Binance Vision** spot BTC/USDT 1-hour candles. Derived research output: CC BY-NC-SA 4.0; see [data terms](../sources/BINANCE_DATASET_TERMS.md).', '',
             f"Candle range: **{run['first_candle']} through {run['last_candle']}**.",
             f"First possible trade: {run['first_trade_opportunity']}. Starting balance: {initial_cash:,.0f} USDT per strategy.",
             f"Real candles used: {len(candles):,}. Gap events in this selection: {run['gap_events']}. Missing hours across the requested source period: {manifest['missing_hours']}.", '',
             '**Costs on each buy and each sell:** 0.1% fee plus 0.05% slippage.', '',
             '| Strategy | Return after costs | Largest drawdown | Completed trades |',
             '| --- | ---: | ---: | ---: |']
    for row in summary.itertuples():
        lines.append(f'| {row.strategy} | {row.return_pct:.2f}% | {row.max_drawdown_pct:.2f}% | {row.trades} |')
    lines += ['', '**Read this before interpreting the ranking:**', '',
              '- A high return based on one trade is weak evidence. It can largely reflect holding Bitcoin for years.',
              '- Drawdown measures losses from an earlier high. The strategies can suffer very large losses even when their final return is positive.',
              '- These are hourly entry/exit signal adaptations. Original bot ROI targets and stoploss rules are omitted for every strategy.',
              '- Missing candles are never filled. Pending signals crossing gaps are canceled; indicators restart with 200 consecutive candles. Existing positions stay held during gaps and warmup.',
              '- This is descriptive history without parameter optimization, not a forecast or a recommendation.', '',
              'Download [summary.csv](summary.csv) for more metrics, [equity.csv.gz](equity.csv.gz) for portfolio history,',
              'and the individual `*_trades.csv` files for each buy and sell.',
              '[run.json](run.json) records assumptions and data/code/output fingerprints.',
              '[data/manifest.json](../data/manifest.json) lists all official source files and missing hours.', '']
    (report_dir/'RESULTS.md').write_text('\n'.join(lines))
    return summary, run


def read_current_report(root):
    """Refuse stale or changed results in the dashboard."""
    root = Path(root)
    run = json.loads((root/'reports/run.json').read_text())
    _, manifest = load_verified(root)
    if (run['dataset_sha256'] != manifest['dataset_sha256'] or
        run['catalog_sha256'] != sha256((root/'sources/strategies.json').read_bytes()) or
        run['implementation_sha256'] != implementation_hash(root)):
        raise DataError('Prices or strategy code changed. Run the comparison again to refresh results.')
    for name, digest in run['outputs_sha256'].items():
        path = root/'reports'/name
        if not path.exists() or sha256(path.read_bytes()) != digest:
            raise DataError('A result file changed or is missing. Run the comparison again.')
    return pd.read_csv(root/'reports/summary.csv'), run
