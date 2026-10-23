"""Comparison metrics with explicit time, gap and sample-size conventions."""
import math

import numpy as np
import pandas as pd

HOURS_PER_YEAR = 365 * 24
LOW_TRADE_THRESHOLD = 30


def hourly_sharpe(equity, initial_cash):
    """Annualized arithmetic Sharpe, 0% risk-free, sample standard deviation.

    Include cash/idle hours and the first hour's entry costs. Exclude transitions
    crossing missing hours: those changes are not one-hour returns. Do not fill
    missing prices or spread a multi-hour return over invented hourly samples.
    Total return and drawdown still include value changes spanning gaps.
    """
    if not isinstance(equity.index, pd.DatetimeIndex) or equity.index.tz is None:
        raise ValueError('Sharpe needs timezone-aware timestamps.')
    if equity.empty or not equity.index.is_unique or not equity.index.is_monotonic_increasing:
        raise ValueError('Sharpe needs nonempty equity in timestamp order.')
    values = equity.to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any() or not np.isfinite(initial_cash) or initial_cash <= 0:
        raise ValueError('Equity and initial cash must be finite and positive.')
    returns = equity.astype(float).pct_change(fill_method=None)
    returns.iloc[0] = values[0]/initial_cash - 1
    keep = equity.index.to_series().diff().eq(pd.Timedelta(hours=1))
    keep.iloc[0] = True
    samples = returns.loc[keep]
    if len(samples) < 2:
        return None, len(samples)
    volatility = float(samples.std(ddof=1))
    if volatility == 0:
        return None, len(samples)
    score = float(samples.mean()/volatility*math.sqrt(HOURS_PER_YEAR))
    return score if np.isfinite(score) else None, len(samples)


def trade_count_flag(count, benchmark=False):
    if benchmark:
        return 'benchmark: one planned holding period'
    if count < LOW_TRADE_THRESHOLD:
        return f'TOO FEW TRADES (<{LOW_TRADE_THRESHOLD})'
    return 'not flagged; trade count alone does not prove reliability'


def directional_audit(catalog):
    """Audit actual forecast capability; never relabel trading actions as forecasts.

    Current catalog functions return exactly entry/exit signal Series, validated
    during each completed backtest. No current adapter provides a prediction of
    next-hour price direction or a prediction probability. A future forecast
    interface must have its own scorer before it can appear as evaluated here.
    """
    rows = []
    for strategy in catalog:
        if strategy.get('provides_directional_forecast', False):
            raise ValueError('A directional forecast was declared, but no validated forecast scorer is installed. No accuracy will be reported.')
        rows.append(dict(strategy_id=strategy['id'], strategy=strategy['title'],
                         trading_backtest_status='completed', forecast_provided=False,
                         directional_evaluation_status='not_applicable_no_directional_forecasts',
                         scored_forecasts=0, next_hour_accuracy_pct=None,
                         reason='Provides buy/sell signals, not next-hour up/down predictions.'))
    return pd.DataFrame(rows)
