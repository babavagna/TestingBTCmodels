import numpy as np
import pandas as pd
import pytest

from btc_lab.engine import Costs, backtest


def prices(opens, closes=None):
    closes = opens if closes is None else closes
    return pd.DataFrame({'open': opens, 'close': closes}, index=pd.date_range('2020-01-01', periods=len(opens), freq='h', tz='UTC'))


def sig(d, *points):
    s = pd.Series(False, index=d.index)
    for i in points:
        s.iloc[i] = True
    return s


def test_exact_fees_slippage_and_next_open():
    d = prices([40, 100, 120, 80])
    stats, equity, trades = backtest(d, sig(d, 0), sig(d, 1), warmup=1)
    buy, sell = 100*1.0005, 120*0.9995
    quantity = 10000/(buy*1.001)
    expected = quantity*sell*0.999
    assert trades.iloc[0].entry_price == pytest.approx(buy)
    assert trades.iloc[0].exit_price == pytest.approx(sell)
    assert trades.iloc[0].entry_time == d.index[1]
    assert trades.iloc[0].exit_time == d.index[2]
    assert stats['final_equity_usdt'] == pytest.approx(expected)
    assert stats['total_fees_usdt'] == pytest.approx(quantity*buy*.001 + quantity*sell*.001)
    assert stats['return_pct'] == pytest.approx((expected/10000-1)*100)
    assert equity.iloc[-1] == pytest.approx(expected)


def test_flat_price_round_trip_loses_both_sides_costs():
    d = prices([100]*4)
    stats, _, trades = backtest(d, sig(d, 0), sig(d, 1), warmup=1)
    expected = 10000*(.9995*.999)/(1.0005*1.001)
    assert stats['final_equity_usdt'] == pytest.approx(expected)
    assert stats['return_pct'] < 0
    assert stats['max_drawdown_pct'] == pytest.approx((1-expected/10000)*100)


def test_no_cost_round_trip():
    d = prices([50, 100, 150, 100])
    stats, _, _ = backtest(d, sig(d, 0), sig(d, 1), warmup=1, costs=Costs(0, 0))
    assert stats['final_equity_usdt'] == 15000


def test_final_close_liquidation_uses_exit_costs():
    d = prices([100]*4, [100, 110, 120, 130])
    stats, _, trades = backtest(d, sig(d, 0), sig(d), warmup=1)
    assert stats['final_equity_usdt'] == pytest.approx(10000*(130*.9995*.999)/(100*1.0005*1.001))
    assert trades.iloc[0].exit_reason == 'end_of_data'
    assert trades.iloc[0].exit_time == d.index[-1] + pd.Timedelta(hours=1)


def test_conflicting_signals_do_not_enter():
    d = prices([100]*5)
    stats, _, trades = backtest(d, sig(d, 0), sig(d, 0), warmup=1)
    assert stats['trades'] == 0
    assert stats['final_equity_usdt'] == 10000
    assert stats['win_rate_pct'] is None


def test_existing_position_exits_on_conflict_without_reentry():
    d = prices([100]*6)
    _, _, trades = backtest(d, sig(d, 0, 1), sig(d, 1), warmup=1)
    assert len(trades) == 1
    assert trades.iloc[0].exit_time == d.index[2]


def test_future_prices_cannot_change_earlier_fills():
    d = prices([100]*7)
    en, ex = sig(d, 0), sig(d, 2)
    _, equity, trades = backtest(d, en, ex, warmup=1)
    d2 = d.copy()
    d2.iloc[4:] *= 100
    _, equity2, trades2 = backtest(d2, en, ex, warmup=1)
    pd.testing.assert_frame_equal(trades, trades2)
    pd.testing.assert_series_equal(equity.iloc[:3], equity2.iloc[:3])


def test_no_trade_before_shared_warmup():
    d = prices([100]*205)
    _, _, trades = backtest(d, sig(d, 0, 199), sig(d, 200), warmup=200)
    assert len(trades) == 1
    assert trades.iloc[0].entry_time == d.index[200]


def test_multiple_trades_cash_pnl_reconcile():
    d = prices([100, 110, 120, 90, 130, 80, 70, 60])
    stats, _, trades = backtest(d, sig(d, 0, 3, 5), sig(d, 1, 4), warmup=1)
    assert len(trades) == 3
    assert trades.net_pnl_usdt.sum() == pytest.approx(stats['final_equity_usdt']-10000)
    assert (trades.quantity > 0).all()


@pytest.mark.parametrize('costs', [(-.01, 0), (0, -1), (1, 0)])
def test_bad_costs_rejected(costs):
    with pytest.raises(ValueError):
        Costs(*costs)


@pytest.mark.parametrize('cash', [0, -1, float('nan'), float('inf')])
def test_bad_balance_rejected(cash):
    d = prices([100]*4)
    with pytest.raises(ValueError):
        backtest(d, sig(d), sig(d), warmup=1, initial_cash=cash)


def test_zero_warmup_cannot_read_final_signal_as_past():
    d = prices([100]*4)
    with pytest.raises(ValueError):
        backtest(d, sig(d, 3), sig(d), warmup=0)


def test_pending_signals_cannot_execute_at_unknown_missing_open():
    d = prices([100]*7)
    en, ex = sig(d, 1), sig(d)
    d = d.drop(d.index[2])
    en, ex = en.loc[d.index], ex.loc[d.index]
    stats, _, trades = backtest(d, en, ex, warmup=1)
    assert stats['trades'] == 0


def test_open_position_held_through_gap_without_fictitious_sell():
    d = prices([100, 100, 100, 120, 130, 130, 140])
    en, ex = sig(d, 0), sig(d, 1, 4)
    d = d.drop(d.index[2])
    _, _, trades = backtest(d, en.loc[d.index], ex.loc[d.index], warmup=1)
    assert len(trades) == 1
    assert trades.iloc[0].exit_time == pd.Timestamp('2020-01-01T05:00:00Z')
