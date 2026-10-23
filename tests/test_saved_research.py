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
