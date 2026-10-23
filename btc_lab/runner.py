"""Run every strategy against one immutable shared price table."""
import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path

import pandas as pd

from btc_lab.data import DataError, load_verified, sha256, utc_now, validate_prices, write_json
from btc_lab.engine import Costs, backtest
from btc_lab.metrics import HOURS_PER_YEAR, LOW_TRADE_THRESHOLD, directional_audit, trade_count_flag
from btc_lab.strategies import load_catalog, signals

WARMUP = 200


def implementation_hash(root):
    digest = hashlib.sha256()
    for path in sorted((Path(root)/'btc_lab').rglob('*.py')):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def prepared_signals(strategy, candles, *, parameters=None, warmup=WARMUP):
    """Reset indicators at every gap and mask the shared warmup in each segment."""
    entry = pd.Series(False, index=candles.index)
    exit_ = pd.Series(False, index=candles.index)
    groups = candles.index.to_series().diff().ne(pd.Timedelta(hours=1)).cumsum()
    for _, segment in candles.groupby(groups):
        if len(segment) < warmup:
            continue
        en, ex = signals(strategy, segment, parameters)
        entry.loc[segment.index[warmup-1:]] = en.iloc[warmup-1:]
        exit_.loc[segment.index[warmup-1:]] = ex.iloc[warmup-1:]
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
        stats.update(strategy_id=strategy['id'], strategy=strategy['title'], kind='hourly signal adaptation',
                     execution_status='completed', trade_count_flag=trade_count_flag(stats['trades']))
        results.append(stats)
        all_equity[strategy['id']] = equity
        all_trades[strategy['id']] = trades
    entry = pd.Series(False, index=candles.index)
    entry.loc[first_opportunity-pd.Timedelta(hours=1)] = True
    stats, equity, trades = backtest(candles, entry, pd.Series(False, index=candles.index),
                                     initial_cash=initial_cash, warmup=WARMUP, gap_policy=gap_policy)
    stats.update(strategy_id='buy_and_hold', strategy='Buy and hold (reference)', kind='benchmark',
                 execution_status='completed', trade_count_flag=trade_count_flag(stats['trades'], benchmark=True))
    results.append(stats)
    all_equity['buy_and_hold'], all_trades['buy_and_hold'] = equity, trades
    summary = pd.DataFrame(results).sort_values('return_pct', ascending=False, kind='stable')
    summary['buy_and_hold_return_pct'] = stats['return_pct']
    summary['rank_by_net_return'] = summary.loc[summary.kind != 'benchmark', 'return_pct'].rank(method='first', ascending=False).astype('Int64')
    directions = directional_audit(catalog)
    report_dir = root/'reports'
    report_dir.mkdir(exist_ok=True)
    outputs = {}
    directions.to_csv(report_dir/'directional_predictions.csv', index=False)
    outputs['directional_predictions.csv'] = sha256((report_dir/'directional_predictions.csv').read_bytes())
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
               ranking='Exploratory descending total return on previously inspected full-period data; not eligible for an unseen leaderboard.',
               low_trade_threshold=LOW_TRADE_THRESHOLD,
               sharpe_definition=dict(annualization_hours=HOURS_PER_YEAR, risk_free_annual_rate=0.0,
                                      standard_deviation='sample, ddof=1', returns='arithmetic hourly portfolio returns after trading costs; idle cash hours included',
                                      gap_policy='Exclude multi-hour changes spanning missing candles from Sharpe only; do not fill missing hours.',
                                      first_return='First recorded trading hour versus initial cash, including entry costs',
                                      zero_volatility='undefined, saved as null', autocorrelation_adjustment=False),
               strategy_execution=[dict(strategy_id=r['strategy_id'], status=r['execution_status'], completed_trades=r['trades']) for r in results if r['kind'] != 'benchmark'],
               directional_forecast_models_scored=0, directional_forecast_status='No current strategy provides next-hour forecasts; trading signals were not converted to predictions.',
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
    def number(value, digits=2, suffix=''):
        return 'N/A' if pd.isna(value) else f'{value:.{digits}f}{suffix}'

    lines = ['# Exploratory historical comparison — not an unseen-data ranking', '',
             '**This full-period comparison used 2025 and 2026 before the chronological audit was requested. It cannot validate an untouched test. See [the audit](audit/REPORT.md).**', '',
             'Source: **Binance Vision** spot BTC/USDT 1-hour candles. Derived research output: CC BY-NC-SA 4.0; see [data terms](../sources/BINANCE_DATASET_TERMS.md).', '',
             f"**{len(catalog)} strategy backtests completed successfully**, plus the buy-and-hold benchmark. Only completed runs are ranked.",
             f"Candle range: **{run['first_candle']} through {run['last_candle']}**.",
             f"First possible trade: {run['first_trade_opportunity']}. Starting balance: {initial_cash:,.0f} USDT per strategy.",
             f"Real candles used: {len(candles):,}. Gap events: {run['gap_events']}. Missing hours in the requested source period: {manifest['missing_hours']}.", '',
             '**Identical costs:** 0.1% fee plus 0.05% slippage on each buy and each sell. Same prices, warmup, gap policy and long/cash execution.', '',
             'Ranked by total net return over the full period (not annual return), not by overall quality. The benchmark is unranked.', '',
             '| Rank | Strategy | Net return | Sharpe | Max drawdown | Profit factor | Win rate | Trades | Buy-and-hold return | Sample flag |',
             '| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    display = pd.concat([summary[summary.kind != 'benchmark'], summary[summary.kind == 'benchmark']])
    for row in display.itertuples():
        rank = '—' if pd.isna(row.rank_by_net_return) else str(int(row.rank_by_net_return))
        flag = 'benchmark' if row.kind == 'benchmark' else ('**TOO FEW**' if row.trades < LOW_TRADE_THRESHOLD else '—')
        lines.append(f"| {rank} | {row.strategy} | {number(row.return_pct, suffix='%')} | {number(row.sharpe_ratio)} | {number(row.max_drawdown_pct, suffix='%')} | {number(row.profit_factor)} | {number(row.win_rate_pct, suffix='%')} | {row.trades} | {number(row.buy_and_hold_return_pct, suffix='%')} | {flag} |")
    lines += ['', f'**Too few trades:** fewer than {LOW_TRADE_THRESHOLD} completed trades is flagged as a caution rule, not a statistical guarantee. More trades do not prove reliability.',
              'N/A profit factor means no losing-trade dollars to divide by; it is not a claim of unlimited profit.', '',
              '## Next-hour directional prediction accuracy', '',
              '**No current strategy provides a next-hour directional forecast. Zero forecast models were scored.**',
              'All ten produce trading entry/exit signals. A decision to buy can mean holding for years; it is not a claim that the next hour will rise.',
              'Accuracy is therefore **N/A for every strategy**, not 0%, not 50%, and not the trade win rate.',
              'The per-strategy audit is saved in [directional_predictions.csv](directional_predictions.csv).', '',
              'A future forecast evaluation must compare a prediction made after hour t with the sign of close(t+1)/close(t)-1, only for adjacent hours.',
              'It must also disclose scored forecasts, ties, abstentions, coverage, up/down class balance, a same-sample always-up baseline, and out-of-sample separation.', '',
              '## What the numbers mean, in plain language', '',
              '- **Net return:** how much the original money grew or shrank after costs. +50% turns 100 into 150; -50% turns 100 into 50.',
              '- **Sharpe ratio:** average hourly gain divided by how much hourly gains jump around, scaled to a year. Think reward compared with bumpiness; higher is generally better. It is not a percentage, a guarantee, or a maximum-loss measure.',
              '- **Maximum drawdown:** the worst recorded fall from an earlier account high. A 77% drawdown turns a peak of 100 into about 23 before any recovery.',
              '- **Profit factor:** total money won on profitable trades divided by total money lost on losing trades, after costs. 1.5 means 1.50 won for each 1 lost. Below 1 means losses outweighed gains.',
              '- **Win rate:** the percentage of completed trades that made money after costs. Many small wins can still be outweighed by a few big losses.',
              '- **Trades:** completed buy-and-sell pairs. One winning trade is like judging a player after one game: too little evidence.',
              '- **Buy-and-hold return:** what happened if you bought once at the shared start and sold at the end, paying the same costs. It is the comparison yardstick.',
              '- **Directional accuracy:** the percentage of explicit next-hour up/down predictions that were right. This differs from winning a trade held for many hours.', '',
              '## Calculation details and limits', '',
              f"Sharpe = mean(hourly simple net returns) / sample standard deviation × sqrt({HOURS_PER_YEAR}); risk-free rate is 0%. Cash/idle hours and first-hour entry costs are included.",
              'Returns spanning missing hours are excluded from Sharpe because they are not one-hour observations. They remain in total return and drawdown. This is a qualified Sharpe estimate on observed hours; no autocorrelation adjustment is applied.', '',
              'A positive Sharpe can coexist with a negative compounded return. For example, +50% then -40% averages +5% per period, but 100 ends at 90. Gap exclusions also make the Sharpe sample different from the full return calculation.', '',
              '- All strategies use the same observation timestamps. No prices are filled. Indicators restart with a shared 200-candle warmup after gaps; existing positions stay held.',
              '- These are hourly signal adaptations, not exact native Freqtrade bots. Original ROI targets and stoploss rules are omitted for every strategy.',
              '- Drawdown uses recorded closes and cannot measure losses within candles or missing hours.',
              '- No parameters were optimized here. This is historical description, not independently validated future performance.', '',
              'See [summary.csv](summary.csv), [equity.csv.gz](equity.csv.gz), individual `*_trades.csv` files and [run.json](run.json).',
              'Source fingerprints and all missing timestamps: [data/manifest.json](../data/manifest.json).', '']
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
