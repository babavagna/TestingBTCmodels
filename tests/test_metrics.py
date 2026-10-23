"""Known-answer metric checks use synthetic numbers, not claimed performance."""
import math

import numpy as np
import pandas as pd
import pytest

from btc_lab.metrics import directional_audit, hourly_sharpe, trade_count_flag
from btc_lab.strategies import load_catalog


def equity_from_returns(returns):
    return pd.Series(100*np.cumprod(1+np.array(returns)),
                     index=pd.date_range('2020-01-01', periods=len(returns), freq='h', tz='UTC'))


def test_sharpe_hand_calculated_includes_first_hour():
    returns = [.01, -.02, .03]
    equity = equity_from_returns(returns)
    score, count = hourly_sharpe(equity, 100)
    expected = (sum(returns)/3) / math.sqrt(sum((r-sum(returns)/3)**2 for r in returns)/2) * math.sqrt(8760)
    assert score == pytest.approx(expected)
    assert count == 3


def test_missing_hour_transition_is_excluded_not_treated_as_hourly():
    equity = equity_from_returns([.01, -.02, .03, .04])
    equity.index = pd.DatetimeIndex(['2020-01-01T00:00Z', '2020-01-01T01:00Z',
                                   '2020-01-01T04:00Z', '2020-01-01T05:00Z'])
    score, count = hourly_sharpe(equity, 100)
    included = np.array([.01, -.02, .04])
    assert count == 3
    assert score == pytest.approx(included.mean()/included.std(ddof=1)*np.sqrt(8760))


def test_idle_cash_hours_and_entry_costs_are_not_dropped():
    returns = [0, 0, -.003, .01, 0]
    score, count = hourly_sharpe(equity_from_returns(returns), 100)
    assert count == 5
    assert score == pytest.approx(np.mean(returns)/np.std(returns, ddof=1)*np.sqrt(8760))


def test_zero_volatility_and_too_few_samples_are_undefined():
    assert hourly_sharpe(equity_from_returns([0, 0, 0]), 100) == (None, 3)
    assert hourly_sharpe(equity_from_returns([.01]), 100) == (None, 1)


def test_low_trade_threshold_is_explicit_and_benchmark_separate():
    for n in (0, 1, 9, 15, 29):
        assert trade_count_flag(n).startswith('TOO FEW')
    assert trade_count_flag(30).startswith('not flagged')
    assert trade_count_flag(1, benchmark=True).startswith('benchmark')


def test_current_trading_rules_are_not_reported_as_prediction_models():
    audit = directional_audit(load_catalog())
    assert len(audit) == 10
    assert not audit.forecast_provided.any()
    assert audit.scored_forecasts.sum() == 0
    assert audit.next_hour_accuracy_pct.isna().all()
    assert audit.directional_evaluation_status.str.startswith('not_applicable').all()


def test_unsupported_future_model_cannot_silently_be_reported_as_evaluated():
    strategy = dict(load_catalog()[0], provides_directional_forecast=True)
    with pytest.raises(ValueError, match='no validated forecast scorer'):
        directional_audit([strategy])
