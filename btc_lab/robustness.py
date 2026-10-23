"""Chronological audit with explicit prior exposure; never fabricate an untouched test.

Training functions receive only a historical prefix. Validation/test never select
parameters. Neighbor settings and costs are predeclared, not searched for a new
holdout winner. The existing 2025/2026 exposure makes every unseen rank ineligible.
"""
import ast
import inspect
import json
from pathlib import Path

import numpy as np
import pandas as pd

from btc_lab.data import DataError, load_verified, sha256, utc_now, write_json
from btc_lab.engine import Costs, backtest
from btc_lab.metrics import LOW_TRADE_THRESHOLD
from btc_lab.runner import implementation_hash, prepared_signals
from btc_lab.strategies import load_catalog
from btc_lab.strategies import hourly

AUDIT_WARMUP = 300  # Covers every candidate, including the 240-hour SMA.
TRAIN_START = pd.Timestamp('2020-01-01', tz='UTC')
VALIDATION_START = pd.Timestamp('2025-01-01', tz='UTC')
TEST_START = pd.Timestamp('2026-01-01', tz='UTC')
TEST_STOP = pd.Timestamp('2026-10-01', tz='UTC')
FEES = (0.0005, 0.001, 0.002)
PRIOR_EXPOSURE = dict(
    genuinely_untouched=False,
    evidence_commits=['6d588bc29149a45ee19e337489480f53cfcb9399', 'b5d5651ebd9a3f889e547791c03e0c662cdfeddd'],
    explanation='The previous full-period backtests and rankings already examined 2025 and Jan-Sep 2026. A chronological rerun cannot erase that exposure.',
    upstream_training_provenance='Unknown. Published upstream hyperparameters and strategy selection may already reflect historical optimization; source chronology alone cannot rule it out.',
    ranking_policy='No genuine unseen-data ranks. Retrospective held-out-from-fitting tables are alphabetical, never presented as untouched results.')


def variants(strategy):
    """One original setting plus two fixed neighbors; no result-dependent grid."""
    fn = getattr(hourly, strategy['function'])
    base = {name: p.default for name, p in inspect.signature(fn).parameters.items() if name != 'd'}
    result = {'original': base}
    for name, factor in [('lower_20pct', .8), ('higher_20pct', 1.2)]:
        result[name] = {key: max(2, int(round(value*factor))) if isinstance(value, int) and value > 0 and ('period' in key or key in ('short', 'long', 'fast', 'slow', 'signal', 'window', 'ao_fast', 'ao_slow'))
                       else round(value*factor, 4) for key, value in base.items()}
    return result


def calendar_folds():
    """Three expanding-window folds wholly inside the user's training era."""
    return [dict(fold=f'train_to_{year-1}_evaluate_{year}', fit_stop=pd.Timestamp(f'{year}-01-01', tz='UTC'),
                 eval_start=pd.Timestamp(f'{year}-01-01', tz='UTC'), eval_stop=pd.Timestamp(f'{year+1}-01-01', tz='UTC'))
            for year in (2022, 2023, 2024)]


def training_prefix(candles, stop):
    """Purge the last training hour; all scored training trades close before stop."""
    cutoff = pd.Timestamp(stop)-pd.Timedelta(hours=1)
    prefix = candles.loc[(candles.index >= TRAIN_START) & (candles.index < cutoff)]
    if prefix.empty or prefix.index[-1]+pd.Timedelta(hours=1) > cutoff:
        raise DataError('Training boundary/purge failed.')
    return prefix


def choose_candidate(rows):
    """Fixed objective, minimum sample, deterministic tie break; no holdout input."""
    eligible = [r for r in rows if r['trades'] >= LOW_TRADE_THRESHOLD and pd.notna(r['sharpe_ratio'])]
    if not eligible:
        return 'original', 'No candidate has 30 completed training trades; original retained, not a qualified fit.'
    # rows arrive original / lower / higher, preserving original on exact ties.
    selected = max(eligible, key=lambda r: r['sharpe_ratio'])
    return selected['variant'], 'Highest training-only net hourly Sharpe among candidates with >=30 trades.'


def period_run(candles, strategy, variant, start, stop, costs=Costs(), *, prepared=None):
    """Use past context for indicators, fresh cash for scoring, no future bars."""
    stop, start = pd.Timestamp(stop), pd.Timestamp(start)
    prefix = candles.loc[candles.index < stop]
    if prefix.empty or prefix.index[-1]+pd.Timedelta(hours=1) > stop:
        raise DataError('Evaluation boundary failed.')
    if prepared is None:
        if strategy is None:
            entry = pd.Series(False, index=prefix.index)
            exit_ = entry.copy()
            first = max(AUDIT_WARMUP, int(prefix.index.searchsorted(start)))
            if first >= len(prefix)-1 or prefix.index[first]-prefix.index[first-1] != pd.Timedelta(hours=1):
                raise DataError('Benchmark lacks an adjacent preceding context candle.')
            entry.iloc[first-1] = True
        else:
            entry, exit_ = prepared_signals(strategy, prefix, parameters=variant, warmup=AUDIT_WARMUP)
    else:
        entry, exit_ = (s.loc[prefix.index] for s in prepared)
    stats, equity, trades = backtest(prefix, entry, exit_, warmup=AUDIT_WARMUP, trade_start=start, costs=costs)
    if (equity.index < start).any() or (equity.index >= stop).any():
        raise DataError('Equity crossed scoring boundaries.')
    if len(trades) and ((trades.entry_time < start).any() or (trades.exit_time > stop).any()):
        raise DataError('Trade crossed scoring boundaries.')
    return stats, equity, trades


def static_findings(path):
    """A limited syntax heuristic, not a proof of absence of cheating."""
    tree = ast.parse(Path(path).read_text())
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.attr if isinstance(node.func, ast.Attribute) else ''
            if name == 'shift':
                arg = node.args[0] if node.args else next((kw.value for kw in node.keywords if kw.arg == 'periods'), None)
                if isinstance(arg, ast.UnaryOp) and isinstance(arg.op, ast.USub):
                    findings.append(f'line {node.lineno}: negative shift can read future rows')
            if name in ('bfill', 'backfill'):
                findings.append(f'line {node.lineno}: backward filling can leak later values')
            if name == 'rolling' and any(kw.arg == 'center' and isinstance(kw.value, ast.Constant) and kw.value.value for kw in node.keywords):
                findings.append(f'line {node.lineno}: centered rolling window can include future rows')
    return findings


def causality_audit(candles, catalog, root):
    """Compare prefixes and radically changed future prices on actual price data."""
    cut_dates = ['2021-01-01', '2023-01-01', '2025-01-01', '2025-07-01', '2026-01-01', '2026-04-01', '2026-09-01']
    rows = []
    for strategy in catalog:
        full_checks, failures = 0, []
        for name, parameters in variants(strategy).items():
            reference = prepared_signals(strategy, candles, parameters=parameters, warmup=AUDIT_WARMUP)
            for date in cut_dates:
                earlier = candles.loc[candles.index < pd.Timestamp(date, tz='UTC')]
                actual = prepared_signals(strategy, earlier, parameters=parameters, warmup=AUDIT_WARMUP)
                full_checks += 1
                if not all(a.equals(b.loc[earlier.index]) for a, b in zip(actual, reference)):
                    failures.append(f'{name}: prefix differs before {date}')
            cut = TEST_START
            changed = candles.copy()
            future = changed.index >= cut
            changed.loc[future, ['open', 'high', 'low', 'close']] *= 3.7
            changed.loc[future, 'volume'] *= .23
            actual = prepared_signals(strategy, changed, parameters=parameters, warmup=AUDIT_WARMUP)
            full_checks += 1
            past = candles.index < cut
            if not all(a.loc[past].equals(b.loc[past]) for a, b in zip(actual, reference)):
                failures.append(f'{name}: changed future altered earlier signals')
        original = Path(root)/strategy['local_source']
        source_intact = sha256(original.read_bytes()) == strategy['source_sha256']
        findings = static_findings(original)+static_findings(Path(root)/'btc_lab/strategies/hourly.py')
        rows.append(dict(strategy_id=strategy['id'], strategy=strategy['title'], status='no_future_dependency_detected' if not failures and source_intact and not findings else 'investigate',
                         dynamic_checks_executed=full_checks, dynamic_failures=len(failures), source_checksum_matches=source_intact,
                         static_suspicious_patterns=len(findings), details=json.dumps(failures+findings),
                         upstream_optimization_provenance='unknown', historical_holdout_previously_exposed=True,
                         untouched_rank_eligible=False))
        print(f"Causality: {strategy['id']} — {full_checks} executed checks, {len(failures)} failures", flush=True)
    return pd.DataFrame(rows)


def run_audit(root):
    root = Path(root)
    out = root/'reports/audit'
    out.mkdir(parents=True, exist_ok=True)
    candles, manifest = load_verified(root)
    catalog = load_catalog(root/'sources/strategies.json')
    if candles.index.min() != TRAIN_START or candles.index.max() != TEST_STOP-pd.Timedelta(hours=1):
        raise DataError('This audit requires the requested 2020-01 through 2026-09 dataset boundaries.')
    protocol = dict(created_at=utc_now(), train='2020-01-01 through 2024-12-31; final hour purged',
                    validation='2025-01-01 through 2025-12-31', nominal_test='2026-01-01 through 2026-09-30',
                    prior_exposure=PRIOR_EXPOSURE, shared_warmup=AUDIT_WARMUP, initial_cash=10000,
                    original_fee=.001, fees_per_side=list(FEES), slippage_per_side=.0005,
                    extra_cost_stress=dict(fee=.002, slippage=.001), candidate_parameters={s['id']: variants(s) for s in catalog},
                    selection='Training-only highest net hourly Sharpe with >=30 completed trades; otherwise retain original and flag.',
                    validation_gate='Positive net return, beats same-cost buy-and-hold, >=30 completed trades; diagnostic only, no retuning.',
                    walk_forward='Expanding fits 2020-21 -> 2022, 2020-22 -> 2023, 2020-23 -> 2024. Then 2020-24 -> 2025; same frozen 2020-24 settings -> 2026.',
                    boundary='Past prices may warm indicators; no pre-period cash PnL or positions carry into evaluation. Training last hour purged; train trades liquidated before evaluation.',
                    sensitivity='All 3 predeclared parameter variants x 3 fees in each validation/test period, plus selected variant at doubled fee/slippage. Diagnostic only; no holdout-based selection.',
                    dataset_sha256=manifest['dataset_sha256'], implementation_sha256=implementation_hash(root),
                    catalog_sha256=sha256((root/'sources/strategies.json').read_bytes()))
    # Persist definitions before any new scores; do not pretend earlier exposure disappeared.
    write_json(out/'protocol.json', protocol)
    causal = causality_audit(candles, catalog, root)
    causal.to_csv(out/'causality.csv', index=False)
    if (causal.status != 'no_future_dependency_detected').any():
        raise DataError('Causality audit needs investigation. No new performance table or ranking issued.')
    training_rows, selections, walk_rows, performance, sensitivities = [], [], [], [], []
    equity_outputs, trade_outputs = {}, {}
    signal_cache, benchmark_cache = {}, {}

    def prepared(strategy, name, frame, key):
        cache_key = (strategy['id'], name, key)
        if cache_key not in signal_cache:
            signal_cache[cache_key] = prepared_signals(strategy, frame, parameters=variants(strategy)[name], warmup=AUDIT_WARMUP)
        return signal_cache[cache_key]

    def fit(strategy, fit_stop, label):
        frame = training_prefix(candles, fit_stop)
        assert frame.index.max() < fit_stop-pd.Timedelta(hours=1)
        rows = []
        for name, params in variants(strategy).items():
            en, ex = prepared(strategy, name, frame, str(frame.index[-1]))
            stats, _, _ = backtest(frame, en, ex, warmup=AUDIT_WARMUP)
            row = dict(strategy_id=strategy['id'], fit_label=label, fit_first_candle=frame.index[0].isoformat(),
                       fit_last_candle=frame.index[-1].isoformat(), fit_stop_exclusive=fit_stop.isoformat(),
                       variant=name, parameters=json.dumps(params, sort_keys=True), execution_status='completed', **stats)
            rows.append(row)
            training_rows.append(row)
        chosen, reason = choose_candidate(rows)
        selection = dict(strategy_id=strategy['id'], fit_label=label, variant=chosen, reason=reason,
                         parameters=variants(strategy)[chosen], fit_first_candle=frame.index[0].isoformat(),
                         fit_last_candle=frame.index[-1].isoformat(), fit_stop_exclusive=fit_stop.isoformat())
        selections.append(selection)
        return chosen

    def benchmark(start, stop, costs):
        key = (start, stop, costs.fee, costs.slippage)
        if key not in benchmark_cache:
            benchmark_cache[key] = period_run(candles, None, None, start, stop, costs)
        return benchmark_cache[key]

    def evaluate(strategy, name, start, stop, costs=Costs()):
        frame = candles.loc[candles.index < stop]
        en, ex = prepared(strategy, name, frame, str(frame.index[-1]))
        return period_run(candles, strategy, variants(strategy)[name], start, stop, costs, prepared=(en, ex))

    for fold in calendar_folds():
        bh, _, _ = benchmark(fold['eval_start'], fold['eval_stop'], Costs())
        for strategy in catalog:
            name = fit(strategy, fold['fit_stop'], fold['fold'])
            stats, _, _ = evaluate(strategy, name, fold['eval_start'], fold['eval_stop'])
            walk_rows.append(dict(strategy_id=strategy['id'], strategy=strategy['title'], fold=fold['fold'],
                                  fit_stop_exclusive=fold['fit_stop'].isoformat(), eval_start=fold['eval_start'].isoformat(), eval_stop_exclusive=fold['eval_stop'].isoformat(),
                                  variant=name, buy_and_hold_return_pct=bh['return_pct'], excess_return_pp=stats['return_pct']-bh['return_pct'],
                                  selection_out_of_sample=True, genuinely_unseen=False, execution_status='completed', **stats))
        print(f"Walk-forward: {fold['fold']} — all {len(catalog)} backtests completed", flush=True)

    frozen = {s['id']: fit(s, VALIDATION_START, 'final_training_2020_2024') for s in catalog}
    # Written before validation/test scores; neither may change frozen settings.
    freeze = dict(created_at=utc_now(), prior_exposure=PRIOR_EXPOSURE, selected_variants=frozen,
                  parameters={s['id']: variants(s)[frozen[s['id']]] for s in catalog},
                  protocol_sha256=sha256((out/'protocol.json').read_bytes()),
                  selections=[s for s in selections if s['fit_label'] == 'final_training_2020_2024'])
    write_json(out/'frozen_selection.json', freeze)

    for label, start, stop in [('validation_2025', VALIDATION_START, TEST_START), ('nominal_test_2026', TEST_START, TEST_STOP)]:
        bh, bh_equity, bh_trades = benchmark(start, stop, Costs())
        equity_outputs[label+'_buy_and_hold'] = bh_equity
        trade_outputs[label+'_buy_and_hold'] = bh_trades
        for strategy in catalog:
            name = frozen[strategy['id']]
            stats, equity, trades = evaluate(strategy, name, start, stop)
            key = label+'_'+strategy['id']
            equity_outputs[key], trade_outputs[key] = equity, trades
            performance.append(dict(period=label, strategy_id=strategy['id'], strategy=strategy['title'], variant=name,
                                    start=start.isoformat(), stop_exclusive=stop.isoformat(), execution_status='completed',
                                    buy_and_hold_return_pct=bh['return_pct'], buy_and_hold_sharpe=bh['sharpe_ratio'],
                                    excess_return_pp=stats['return_pct']-bh['return_pct'], low_trade_count=stats['trades'] < LOW_TRADE_THRESHOLD,
                                    selection_out_of_sample=True, genuinely_unseen=False, unseen_rank=None,
                                    diagnostic_gate_pass=stats['return_pct'] > 0 and stats['return_pct'] > bh['return_pct'] and stats['trades'] >= LOW_TRADE_THRESHOLD,
                                    **stats))
            for variant_name in variants(strategy):
                for fee in FEES:
                    costs = Costs(fee, .0005)
                    stress, _, _ = evaluate(strategy, variant_name, start, stop, costs)
                    ref, _, _ = benchmark(start, stop, costs)
                    sensitivities.append(dict(period=label, strategy_id=strategy['id'], variant=variant_name,
                                              fee_per_side=fee, slippage_per_side=.0005, scenario='parameter_fee_grid',
                                              buy_and_hold_return_pct=ref['return_pct'], excess_return_pp=stress['return_pct']-ref['return_pct'],
                                              execution_status='completed', **stress))
            costs = Costs(.002, .001)
            stress, _, _ = evaluate(strategy, name, start, stop, costs)
            ref, _, _ = benchmark(start, stop, costs)
            sensitivities.append(dict(period=label, strategy_id=strategy['id'], variant=name,
                                      fee_per_side=costs.fee, slippage_per_side=costs.slippage, scenario='double_fee_and_slippage',
                                      buy_and_hold_return_pct=ref['return_pct'], excess_return_pp=stress['return_pct']-ref['return_pct'],
                                      execution_status='completed', **stress))
        print(f"{label}: {len(catalog)} frozen-parameter backtests and {len(catalog)*10} cost/parameter stress runs completed", flush=True)

    frames = dict(training_candidates=pd.DataFrame(training_rows), walk_forward=pd.DataFrame(walk_rows),
                  period_results=pd.DataFrame(performance), sensitivity=pd.DataFrame(sensitivities))
    summary = []
    for strategy in catalog:
        sid = strategy['id']
        wf = frames['walk_forward'].loc[frames['walk_forward'].strategy_id == sid]
        for label in ('validation_2025', 'nominal_test_2026'):
            grid = frames['sensitivity'].loc[(frames['sensitivity'].strategy_id == sid) & (frames['sensitivity'].period == label) & (frames['sensitivity'].scenario == 'parameter_fee_grid')]
            summary.append(dict(strategy_id=sid, strategy=strategy['title'], period=label,
                                scenarios_executed=len(grid), profitable_scenarios=int((grid.return_pct > 0).sum()),
                                beat_hold_scenarios=int((grid.excess_return_pp > 0).sum()),
                                worst_return_pct=float(grid.return_pct.min()), best_return_pct=float(grid.return_pct.max()),
                                walk_forward_folds=len(wf), walk_forward_positive_folds=int((wf.return_pct > 0).sum()),
                                walk_forward_beat_hold_folds=int((wf.excess_return_pp > 0).sum()),
                                selected_variant=frozen[sid],
                                fee_low_return_pct=float(grid.loc[(grid.variant == frozen[sid]) & (grid.fee_per_side == .0005), 'return_pct'].iloc[0]),
                                fee_base_return_pct=float(grid.loc[(grid.variant == frozen[sid]) & (grid.fee_per_side == .001), 'return_pct'].iloc[0]),
                                fee_high_return_pct=float(grid.loc[(grid.variant == frozen[sid]) & (grid.fee_per_side == .002), 'return_pct'].iloc[0]),
                                double_cost_return_pct=float(frames['sensitivity'].loc[(frames['sensitivity'].strategy_id == sid) & (frames['sensitivity'].period == label) & (frames['sensitivity'].scenario == 'double_fee_and_slippage'), 'return_pct'].iloc[0]),
                                parameter_only_profitable_cases=int((grid.loc[grid.fee_per_side == .001, 'return_pct'] > 0).sum()),
                                genuinely_unseen=False, unseen_rank=None))
    frames['robustness_summary'] = pd.DataFrame(summary)
    verdicts = []
    for strategy in catalog:
        sid = strategy['id']
        val = frames['period_results'].loc[(frames['period_results'].strategy_id == sid) & (frames['period_results'].period == 'validation_2025')].iloc[0]
        test = frames['period_results'].loc[(frames['period_results'].strategy_id == sid) & (frames['period_results'].period == 'nominal_test_2026')].iloc[0]
        risk = frames['robustness_summary'].loc[(frames['robustness_summary'].strategy_id == sid) & (frames['robustness_summary'].period == 'nominal_test_2026')].iloc[0]
        train = frames['training_candidates'].loc[(frames['training_candidates'].strategy_id == sid) & (frames['training_candidates'].fit_label == 'final_training_2020_2024') & (frames['training_candidates'].variant == frozen[sid])].iloc[0]
        reasons = []
        if not val.diagnostic_gate_pass:
            reasons.append('failed 2025 validation gate')
        if test.return_pct <= 0:
            reasons.append('lost money in nominal 2026 test')
        if test.return_pct <= test.buy_and_hold_return_pct:
            reasons.append('did not beat holding Bitcoin in 2026')
        if test.low_trade_count:
            reasons.append('fewer than 30 nominal-test trades')
        if risk.profitable_scenarios < 9:
            reasons.append(f'only {risk.profitable_scenarios}/9 profitable 2026 parameter/fee cases')
        verdicts.append(dict(strategy_id=sid, strategy=strategy['title'], train_return_pct=train.return_pct,
                             train_sharpe=train.sharpe_ratio, train_trades=int(train.trades), validation_return_pct=val.return_pct,
                             nominal_test_return_pct=test.return_pct, passed_both_period_gates=bool(val.diagnostic_gate_pass and test.diagnostic_gate_pass),
                             genuinely_unseen=False, unseen_rank=None, failure_reasons='; '.join(reasons),
                             conclusion='No verified robust unseen edge; prior exposure prevents untouched ranking.'))
    frames['strategy_verdicts'] = pd.DataFrame(verdicts)
    # No outcome-based leaderboard when the requested holdout has already been seen.
    frames['unseen_leaderboard'] = pd.DataFrame(columns=['unseen_rank', 'strategy_id', 'return_pct', 'eligibility'])
    for name, frame in frames.items():
        frame.to_csv(out/f'{name}.csv', index=False)
    for name, trades in trade_outputs.items():
        trades.to_csv(out/f'{name}_trades.csv', index=False)
    pd.DataFrame(equity_outputs).to_csv(out/'period_equity.csv.gz', compression={'method': 'gzip', 'mtime': 0})
    manifest = dict(status='completed_retrospective_chronological_audit', created_at=utc_now(), prior_exposure=PRIOR_EXPOSURE,
                    dataset_sha256=protocol['dataset_sha256'], implementation_sha256=implementation_hash(root),
                    frozen_selection_sha256=sha256((out/'frozen_selection.json').read_bytes()),
                    execution_counts=dict(causality_checks=int(causal.dynamic_checks_executed.sum()),
                                          training_candidate_backtests=len(training_rows), walk_forward_backtests=len(walk_rows),
                                          validation_and_test_backtests=len(performance), sensitivity_backtests=len(sensitivities),
                                          benchmark_backtests=len(benchmark_cache)),
                    output_sha256={p.name: sha256(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file() and p.name not in ('run.json', 'REPORT.md')})
    write_report(out, frames, manifest)
    manifest['output_sha256']['REPORT.md'] = sha256((out/'REPORT.md').read_bytes())
    write_json(out/'run.json', manifest)
    return frames, manifest


def write_report(out, frames, manifest):
    def n(x):
        return 'N/A' if pd.isna(x) else f'{x:.2f}'
    lines = ['# Strategy integrity and chronological robustness audit', '',
             '**No strategy qualifies for a genuinely unseen-data ranking.** The previous full-period study already inspected 2025 and January–September 2026.',
             'These are retrospective chronological diagnostics. Parameters are selected without those periods in this audit, but this cannot erase earlier exposure.',
             'All tables below are alphabetical, not performance rankings. The unseen leaderboard is intentionally empty.', '',
             '## What was checked', '',
             f"- Executed {manifest['execution_counts']['causality_checks']} actual-data prefix/future-mutation checks across all ten strategies and all three settings.",
             '- Checked saved upstream source fingerprints and syntax patterns for future shifts, centered windows and backward filling. This is evidence of causal behavior, not a mathematical proof or an accusation of intent.',
             '- Training chooses from original / roughly -20% / roughly +20% parameter settings using only 2020–2024. These are rules, not fitted machine-learning models.',
             '- Walk-forward: fit through 2021 then evaluate 2022; fit through 2022 then evaluate 2023; fit through 2023 then evaluate 2024. Each fit sees past candles only.',
             '- Fit through 2024 once, freeze the settings, evaluate 2025 for validation, then January–September 2026 without refitting on 2025 or rescuing failures.',
             '- Training last hour is purged; trades are closed within training. Historical candles may initialize indicators, but scoring starts with fresh cash and no inherited positions.',
             '- Shared 300-hour warmup covers all variants (including a 240-hour moving average); historical gaps reset it. No candles are filled.',
             '- Neighbor profiles change numeric settings jointly by roughly 20%; this is a small predeclared stress test, not an exhaustive one-at-a-time or combinatorial search.',
             '- Fees per side: 0.05%, 0.10%, 0.20%; slippage 0.05%. A further run doubles both base fee and slippage. Every scenario has a matching same-cost buy-and-hold reference.',
             '- No scalers, target encoders, train/test shuffling or learned weights exist in these adapters. Upstream parameter tuning history remains unknown.', '',
             f"**Strategies passing both the 2025 and 2026 diagnostic gates: {int(frames['strategy_verdicts'].passed_both_period_gates.sum())}/{len(frames['strategy_verdicts'])}.** No robust unseen winner is established.", '',
             '## Split results — held out from this fit, previously seen by the project', '']
    for label, title in [('validation_2025', '2025 validation'), ('nominal_test_2026', 'January–September 2026 nominal test (not untouched)')]:
        table = frames['period_results'].loc[frames['period_results'].period == label].sort_values('strategy')
        lines += [f'### {title}', '', '| Strategy | Setting selected on training | Net return | Sharpe | Max drawdown | Trades | Hold return | Gate |',
                  '| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |']
        for row in table.itertuples():
            flag = ' ⚠' if row.low_trade_count else ''
            lines.append(f'| {row.strategy} | {row.variant} | {n(row.return_pct)}% | {n(row.sharpe_ratio)} | {n(row.max_drawdown_pct)}% | {row.trades}{flag} | {n(row.buy_and_hold_return_pct)}% | {"pass" if row.diagnostic_gate_pass else "fail"} |')
        lines += ['', '⚠ Fewer than 30 trades. The diagnostic gate requires positive return, beating buy-and-hold, and at least 30 trades. Passing it is not proof of a real edge.', '']
    lines += ['## Walk-forward and sensitivity findings', '',
              '| Strategy | Positive walk-forward years / 3 | Beat hold years / 3 | Profitable 2026 grid cases / 9 | Beat hold 2026 cases / 9 | 2026 grid return range |',
              '| --- | ---: | ---: | ---: | ---: | --- |']
    table = frames['robustness_summary'].loc[frames['robustness_summary'].period == 'nominal_test_2026'].sort_values('strategy')
    for r in table.itertuples():
        lines.append(f'| {r.strategy} | {r.walk_forward_positive_folds}/3 | {r.walk_forward_beat_hold_folds}/3 | {r.profitable_scenarios}/9 | {r.beat_hold_scenarios}/9 | {n(r.worst_return_pct)}% to {n(r.best_return_pct)}% |')
    lines += ['', '### Fee sensitivity with training-selected parameters fixed (2026)', '',
              '| Strategy | Fee 0.05% | Fee 0.10% | Fee 0.20% | Fee 0.20% + slip 0.10% |',
              '| --- | ---: | ---: | ---: | ---: |']
    for r in table.itertuples():
        lines.append(f'| {r.strategy} | {n(r.fee_low_return_pct)}% | {n(r.fee_base_return_pct)}% | {n(r.fee_high_return_pct)}% | {n(r.double_cost_return_pct)}% |')
    lines += ['', 'Fee percentages are per side. Slippage is 0.05% except in the last column. Corresponding same-cost buy-and-hold outcomes are saved for every case in sensitivity.csv.', '', 'These nine scenarios are diagnostics, not a search for a new winner. Period-specific detailed rows and the doubled-fee/slippage cases are in sensitivity.csv.', '',
              '## Failures explained simply', '',
              '- **Previously seen test:** it is like seeing the exam answers before taking a practice exam. Reordering the questions does not make it a fresh exam. No untouched-test claim or unseen rank is issued.',
              '- **Look-ahead bias:** making a trade with information from tomorrow. Prefix and mutation checks look for earlier decisions changing when tomorrow changes. No detected dependency does not guarantee every possible code path is clean.',
              '- **Overfitting:** a rule memorizes one stretch of history but struggles later. Training-vs-later-year and nearby-setting comparisons expose this risk; they cannot prove its absence.',
              '- **Tiny sample:** a strategy can look brilliant because it held Bitcoin through one rise. Fewer than 30 trades is flagged; more trades alone do not prove reliability.',
              '- **Parameter fragility:** changing a few settings can turn a gain into a loss. The full range is reported rather than choosing the prettiest result.',
              '- **Fee fragility:** frequent small gains can disappear when trading becomes more expensive.',
              '- **Why a weak later year matters:** strong training results followed by losses can indicate overfitting or a changed market. These observations cannot distinguish those causes with certainty. Three walk-forward years are a limited sample; no formal significance or probability-of-overfitting claim is made.',
              '- **Upstream uncertainty:** published settings may have been optimized before we obtained them. We do not know the original training data, so cannot certify historical independence.',
              '- **Simulation limits:** the original bots\' ROI/stoploss rules are omitted; cash/long all-in execution, close-based drawdown and constant slippage are simplified. No real trading performance is established.', '',
              '## How to get a genuinely new test', '',
              'Freeze settings and rules now, record them in Git, and paper-test later candles that were not used to build or inspect this project. Do not retune on those results or repeatedly select winners.',
              'The 2026 diagnostic here is not used to pick a new strategy. No later price data was downloaded for this audit.', '',
              '## Reproduce and inspect', '',
              'Run `.venv/bin/python -m btc_lab robustness`. `protocol.json` is written before scoring; `frozen_selection.json` is written before validation/test scores.',
              'See training_candidates.csv, walk_forward.csv, period_results.csv, sensitivity.csv, robustness_summary.csv, strategy_verdicts.csv, causality.csv, period_equity.csv.gz and per-period trade logs.',
              'All data-derived output: Binance Vision attribution, CC BY-NC-SA 4.0 plus the [saved dataset terms](../../sources/BINANCE_DATASET_TERMS.md).', '']
    (out/'REPORT.md').write_text('\n'.join(lines))


def read_audit(root):
    """Reject stale/tampered audit results before showing them in the dashboard."""
    root = Path(root)
    out = root/'reports/audit'
    metadata = json.loads((out/'run.json').read_text())
    _, source = load_verified(root)
    if metadata['status'] != 'completed_retrospective_chronological_audit':
        raise DataError('The chronological audit did not complete.')
    if metadata['dataset_sha256'] != source['dataset_sha256'] or metadata['implementation_sha256'] != implementation_hash(root):
        raise DataError('Prices or code changed. Rerun the chronological audit.')
    for filename, digest in metadata['output_sha256'].items():
        path = out/filename
        if not path.exists() or sha256(path.read_bytes()) != digest:
            raise DataError('An audit output changed or is missing. Rerun the chronological audit.')
    protocol = json.loads((out/'protocol.json').read_text())
    if protocol['catalog_sha256'] != sha256((root/'sources/strategies.json').read_bytes()):
        raise DataError('The strategy catalog changed. Rerun the chronological audit.')
    return pd.read_csv(out/'period_results.csv'), metadata
