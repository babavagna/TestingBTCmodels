"""End-to-end tests run only in pytest temporary directories, with synthetic fixtures."""
import json
import shutil

import pandas as pd
import pytest

from btc_lab.data import DataError, sha256, write_json
from btc_lab.runner import WARMUP, read_current_report, run_all
from btc_lab.strategies import ROOT


def fixture_project(tmp_path, candles):
    (tmp_path/'data').mkdir()
    (tmp_path/'sources').mkdir()
    shutil.copy(ROOT/'sources/strategies.json', tmp_path/'sources/strategies.json')
    shutil.copytree(ROOT/'btc_lab', tmp_path/'btc_lab', ignore=shutil.ignore_patterns('__pycache__'))
    path = tmp_path/'data/btcusdt_1h.csv.gz'
    candles.to_csv(path, compression='gzip')
    write_json(tmp_path/'data/manifest.json', dict(status='complete', exchange='Binance spot', symbol='BTCUSDT', interval='1h',
               rows=len(candles), missing_hours=0, requested_start_month='2020-01', requested_end_month='2020-04',
               dataset_sha256=sha256(path.read_bytes()), fixture_notice='SYNTHETIC TEST FIXTURE ONLY'))
    return tmp_path


def test_all_ten_and_benchmark_same_data_costs_dates_and_reproducibility(tmp_path, candles):
    root = fixture_project(tmp_path, candles)
    summary, run = run_all(root)
    assert len(summary) == 11
    assert summary.trades.sum() > 0
    assert set(summary.initial_cash_usdt) == {10000}
    assert run['fee_per_side'] == .001
    assert run['slippage_per_side'] == .0005
    assert run['first_trade_opportunity'] == candles.index[WARMUP].isoformat()
    equity = pd.read_csv(root/'reports/equity.csv.gz', index_col=0)
    assert len(equity) == len(candles)-WARMUP
    assert len(equity.columns) == 11
    first_hashes = run['outputs_sha256']
    summary2, run2 = run_all(root)
    assert first_hashes == run2['outputs_sha256']
    pd.testing.assert_frame_equal(summary, summary2)
    read_current_report(root)
    # UI must refuse stale result tables rather than accidentally present old ranks.
    (root/'reports/summary.csv').write_text('changed')
    with pytest.raises(DataError, match='result file'):
        read_current_report(root)


def test_runner_stops_on_internal_missing_hours(tmp_path, candles):
    root = fixture_project(tmp_path, candles.drop(candles.index[300]))
    with pytest.raises(DataError, match='missing hours'):
        run_all(root, gap_policy='strict')
    assert not (root/'reports/run.json').exists()


def test_selected_range_is_shared(tmp_path, candles):
    root = fixture_project(tmp_path, candles)
    _, run = run_all(root, '2020-01-10', '2020-01-31')
    assert run['first_candle'] == '2020-01-10T00:00:00+00:00'
    assert run['last_candle'] == '2020-01-31T23:00:00+00:00'


def test_pause_policy_handles_realistic_gap_without_inventing_hours(tmp_path, candles):
    from btc_lab.runner import prepared_signals
    from btc_lab.strategies import load_catalog
    missing = candles.index[300]
    with_gap = candles.drop(missing)
    root = fixture_project(tmp_path, with_gap)
    summary, run = run_all(root)
    assert len(summary) == 11
    assert run['gap_events'] == 1
    equity = pd.read_csv(root/'reports/equity.csv.gz', index_col=0, parse_dates=True)
    assert len(equity) == len(with_gap)-WARMUP
    assert missing not in equity.index
    for s in load_catalog():
        en, ex = prepared_signals(s, with_gap)
        assert not en.iloc[300:499].any()
        assert not ex.iloc[300:499].any()
