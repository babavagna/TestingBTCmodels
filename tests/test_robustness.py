"""Boundary and causal checks; fixtures are synthetic, never performance claims."""
import json
from pathlib import Path

import pandas as pd
import pytest

from btc_lab.data import DataError
from btc_lab.engine import backtest
from btc_lab.robustness import (AUDIT_WARMUP, PRIOR_EXPOSURE, VALIDATION_START,
                                calendar_folds, choose_candidate, period_run,
                                read_audit, static_findings, training_prefix, variants)
from btc_lab.runner import prepared_signals
from btc_lab.strategies import ROOT, load_catalog, signals

CATALOG = load_catalog()


@pytest.mark.parametrize('strategy', CATALOG, ids=lambda s: s['id'])
def test_parameterized_default_preserves_original_adapter(strategy, candles):
    a = signals(strategy, candles)
    b = signals(strategy, candles, variants(strategy)['original'])
    for x, y in zip(a, b):
        pd.testing.assert_series_equal(x, y)
    for params in variants(strategy).values():
        if 'sma_period' in params:
            assert params['sma_period'] < AUDIT_WARMUP


def test_future_prefix_is_never_supplied_to_training():
    index = pd.date_range('2024-12-31T20:00Z', periods=9, freq='h')
    d = pd.DataFrame({'close': range(9)}, index=index)
    training = training_prefix(d, VALIDATION_START)
    assert training.index[-1] == pd.Timestamp('2024-12-31T22:00Z')
    assert not (training.index >= pd.Timestamp('2024-12-31T23:00Z')).any()


def test_selecting_parameters_never_uses_future_prices(candles):
    cutoff = pd.Timestamp('2020-03-01', tz='UTC')
    modified = candles.copy()
    modified.loc[modified.index >= cutoff, ['open', 'high', 'low', 'close']] *= 4
    strategy = CATALOG[0]
    choices = []
    for d in (candles, modified):
        frame = training_prefix(d, cutoff)
        scores = []
        for name, p in variants(strategy).items():
            en, ex = prepared_signals(strategy, frame, parameters=p, warmup=AUDIT_WARMUP)
            stats, _, _ = backtest(frame, en, ex, warmup=AUDIT_WARMUP)
            scores.append(dict(variant=name, **stats))
        choices.append((choose_candidate(scores), scores))
    assert choices[0] == choices[1]


def test_minimum_training_sample_and_ties_are_explicit():
    rows = [dict(variant='original', trades=29, sharpe_ratio=100),
            dict(variant='lower_20pct', trades=31, sharpe_ratio=.5),
            dict(variant='higher_20pct', trades=40, sharpe_ratio=.4)]
    assert choose_candidate(rows)[0] == 'lower_20pct'
    rows[0]['trades'] = 31
    rows[0]['sharpe_ratio'] = .5
    assert choose_candidate(rows)[0] == 'original'
    assert choose_candidate([dict(variant='lower_20pct', trades=1, sharpe_ratio=100)])[0] == 'original'


def test_walk_forward_cannot_fit_on_next_year():
    folds = calendar_folds()
    assert len(folds) == 3
    for f in folds:
        assert f['fit_stop'] <= f['eval_start']
        assert f['eval_stop'] <= VALIDATION_START


def test_period_scoring_uses_context_but_no_training_positions(candles):
    start, stop = pd.Timestamp('2020-02-01', tz='UTC'), pd.Timestamp('2020-03-01', tz='UTC')
    stats, eq, trades = period_run(candles, None, None, start, stop)
    assert eq.index[0] == start
    assert eq.index[-1] == stop-pd.Timedelta(hours=1)
    assert len(trades) == 1
    assert trades.iloc[0].entry_time == start
    assert trades.iloc[0].exit_time == stop
    first_open = candles.loc[start, 'open']
    last_close = candles.loc[stop-pd.Timedelta(hours=1), 'close']
    expected = 10000/(first_open*1.0005*1.001)*last_close*.9995*.999
    assert stats['final_equity_usdt'] == pytest.approx(expected)
    changed = candles.copy()
    changed.loc[changed.index >= stop, ['open', 'high', 'low', 'close']] *= 10
    a = period_run(candles, CATALOG[0], variants(CATALOG[0])['original'], start, stop)
    b = period_run(changed, CATALOG[0], variants(CATALOG[0])['original'], start, stop)
    assert a[0] == b[0]
    pd.testing.assert_series_equal(a[1], b[1])
    pd.testing.assert_frame_equal(a[2], b[2])


def test_future_prices_cannot_change_preexisting_execution(candles):
    # Exclude the terminal liquidation, which explicitly depends on the period end.
    s = CATALOG[0]
    en, ex = prepared_signals(s, candles, warmup=AUDIT_WARMUP)
    altered = candles.copy()
    cutoff = 1800
    altered.iloc[cutoff:, :4] *= 3
    en2, ex2 = prepared_signals(s, altered, warmup=AUDIT_WARMUP)
    _, eq, trades = backtest(candles, en, ex, warmup=AUDIT_WARMUP)
    _, eq2, trades2 = backtest(altered, en2, ex2, warmup=AUDIT_WARMUP)
    pd.testing.assert_series_equal(eq.loc[eq.index < candles.index[cutoff]], eq2.loc[eq2.index < candles.index[cutoff]])
    pd.testing.assert_frame_equal(trades.loc[trades.exit_time < candles.index[cutoff]].reset_index(drop=True),
                                  trades2.loc[trades2.exit_time < candles.index[cutoff]].reset_index(drop=True))


def test_static_scanner_finds_known_cheating_patterns(tmp_path):
    path = tmp_path/'bad.py'
    path.write_text("a = x.shift(-1)\nb = x.rolling(5, center=True).mean()\nc = x.bfill()\n")
    assert len(static_findings(path)) == 3
    path.write_text('a = x.shift(1)\nb = x.rolling(5).mean()\n')
    assert static_findings(path) == []


def test_prior_exposure_cannot_be_called_untouched():
    assert PRIOR_EXPOSURE['genuinely_untouched'] is False
    assert PRIOR_EXPOSURE['evidence_commits']


def test_saved_audit_reports_only_executed_runs_and_no_unseen_rank():
    if not (ROOT/'reports/audit/run.json').exists():
        pytest.skip('Chronological research not yet executed in this checkout.')
    rows, metadata = read_audit(ROOT)
    out = ROOT/'reports/audit'
    assert len(rows) == 20
    assert rows.execution_status.eq('completed').all()
    assert rows.selection_out_of_sample.all()
    assert not rows.genuinely_unseen.any()
    assert rows.unseen_rank.isna().all()
    assert pd.read_csv(out/'unseen_leaderboard.csv').empty
    frozen = json.loads((out/'frozen_selection.json').read_text())
    assert len(frozen['selected_variants']) == 10
    assert all(pd.Timestamp(x['fit_last_candle']) < VALIDATION_START for x in frozen['selections'])
    train = pd.read_csv(out/'training_candidates.csv')
    assert len(train) == 120
    assert (pd.to_datetime(train.fit_last_candle, utc=True) < VALIDATION_START).all()
    assert metadata['execution_counts']['training_candidate_backtests'] == len(train)
    stress = pd.read_csv(out/'sensitivity.csv')
    assert len(stress) == 200
    assert stress.execution_status.eq('completed').all()
    # No cost-only improvement for a fixed strategy/period/parameters and slippage.
    grid = stress[stress.scenario == 'parameter_fee_grid']
    for _, group in grid.groupby(['period', 'strategy_id', 'variant']):
        assert group.sort_values('fee_per_side').final_equity_usdt.is_monotonic_decreasing


def test_dynamic_prefix_control_detects_deliberately_future_reading_rule(candles, monkeypatch):
    from btc_lab.strategies import hourly
    def bad_rule(d, **kwargs):
        return d.close.shift(-1).gt(0), pd.Series(False, index=d.index)
    monkeypatch.setattr(hourly, 'average', bad_rule)
    full, _ = prepared_signals(CATALOG[0], candles, warmup=AUDIT_WARMUP)
    earlier, _ = prepared_signals(CATALOG[0], candles.iloc[:1000], warmup=AUDIT_WARMUP)
    assert not earlier.equals(full.loc[earlier.index])


def test_dynamic_control_detects_full_sample_normalization_leak(candles, monkeypatch):
    from btc_lab.strategies import hourly
    def bad_rule(d, **kwargs):
        return d.close.gt(d.close.mean()), pd.Series(False, index=d.index)
    monkeypatch.setattr(hourly, 'average', bad_rule)
    reference, _ = prepared_signals(CATALOG[0], candles, warmup=AUDIT_WARMUP)
    changed = candles.copy()
    changed.iloc[1600:, :4] *= 100
    actual, _ = prepared_signals(CATALOG[0], changed, warmup=AUDIT_WARMUP)
    assert not actual.iloc[:1600].equals(reference.iloc[:1600])
