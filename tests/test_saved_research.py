"""Independently audit the real archived research artifacts when included in checkout."""
import pandas as pd
import pytest

from btc_lab.data import load_verified
from btc_lab.runner import read_current_report
from btc_lab.strategies import ROOT


def test_saved_real_prices_and_buy_hold_accounting():
    if not (ROOT/'reports/run.json').exists():
        pytest.skip('No saved real-data run in this checkout.')
    candles, manifest = load_verified(ROOT)
    summary, run = read_current_report(ROOT)
    assert len(summary) == 11
    first = pd.Timestamp(run['first_trade_opportunity'])
    last = pd.Timestamp(run['last_candle'])
    quantity = run['initial_cash_usdt'] / (candles.loc[first, 'open']*1.0005*1.001)
    expected = quantity*candles.loc[last, 'close']*.9995*.999
    actual = summary.loc[summary.strategy_id == 'buy_and_hold'].iloc[0]
    assert actual.final_equity_usdt == pytest.approx(expected)
    assert actual.trades == 1
    assert sum(m['rows'] for m in manifest['months'] if m['status'] == 'verified') == manifest['rows']
    assert manifest['rows'] + manifest['missing_hours'] == manifest['expected_rows']
    assert len(manifest['missing_timestamps']) == manifest['missing_hours']


def test_saved_ranked_metrics_match_raw_equity_and_execution_ledger():
    import numpy as np
    if not (ROOT/'reports/run.json').exists():
        pytest.skip('No saved real-data run in this checkout.')
    summary, run = read_current_report(ROOT)
    equity = pd.read_csv(ROOT/'reports/equity.csv.gz', index_col='timestamp', parse_dates=True)
    adjacent = equity.index.to_series().diff().eq(pd.Timedelta(hours=1))
    adjacent.iloc[0] = True
    for row in summary.itertuples():
        values = equity[row.strategy_id]
        returns = values.pct_change(fill_method=None)
        returns.iloc[0] = values.iloc[0]/run['initial_cash_usdt']-1
        returns = returns.loc[adjacent]
        expected = returns.mean()/returns.std(ddof=1)*np.sqrt(8760)
        assert row.sharpe_ratio == pytest.approx(expected)
        assert row.sharpe_hourly_samples == len(returns)
        assert row.execution_status == 'completed'
    ranked = summary[summary.kind != 'benchmark'].sort_values('rank_by_net_return')
    assert len(ranked) == 10
    assert ranked.return_pct.is_monotonic_decreasing
    assert set(ranked.loc[ranked.trades < 30, 'strategy_id']) == {'macd_cci', 'macd_cross', 'quickie'}
    assert len(run['strategy_execution']) == 10
    assert all(r['status'] == 'completed' for r in run['strategy_execution'])
    assert run['directional_forecast_models_scored'] == 0
    assert summary.buy_and_hold_return_pct.nunique() == 1
