"""A small auditable long-only spot engine. No leverage or short selling."""
from dataclasses import dataclass
import numpy as np
import pandas as pd

from btc_lab.metrics import hourly_sharpe


@dataclass(frozen=True)
class Costs:
    fee: float = 0.001
    slippage: float = 0.0005

    def __post_init__(self):
        if not (0 <= self.fee < 1 and 0 <= self.slippage < 1):
            raise ValueError('Fee and slippage must be fractions between 0 and 1.')


TRADE_COLUMNS = ['entry_time', 'exit_time', 'entry_price', 'exit_price', 'quantity',
                 'entry_fee', 'exit_fee', 'net_pnl_usdt', 'return_pct', 'exit_reason']


def backtest(candles, entry, exit_, *, initial_cash=10000.0, warmup=200, costs=Costs(), gap_policy='pause', trade_start=None):
    """Close signal at t -> fill at t+1 open. All-in; no same-bar reentry.
    Conflicting entry+exit signals suppress entry; exit wins for an existing position.
    Final open position is liquidated at the final close, including both exit costs.
    """
    if not np.isfinite(initial_cash) or initial_cash <= 0:
        raise ValueError('Starting cash must be positive and finite.')
    if warmup < 1 or len(candles) <= warmup:
        raise ValueError('Not enough candles after the shared warmup.')
    if not entry.index.equals(candles.index) or not exit_.index.equals(candles.index):
        raise ValueError('Signal timestamps do not match prices.')
    if gap_policy not in ('pause', 'strict'):
        raise ValueError('Choose gap_policy pause or strict.')
    adjacent = candles.index.to_series().diff().eq(pd.Timedelta(hours=1)).to_numpy()
    if gap_policy == 'strict' and not adjacent[1:].all():
        raise ValueError('Strict gap policy refuses missing hours.')
    cash, qty, trades, values = float(initial_cash), 0.0, [], []
    entry_time, entry_price, entry_fee, invested = None, None, None, None
    opens, closes = candles.open.to_numpy(), candles.close.to_numpy()
    en, ex = entry.fillna(False).to_numpy(bool), exit_.fillna(False).to_numpy(bool)
    times = candles.index

    def sell(price, timestamp, reason):
        nonlocal cash, qty
        fill = float(price) * (1 - costs.slippage)
        gross = qty * fill
        fee = gross * costs.fee
        cash = gross - fee
        trades.append(dict(entry_time=entry_time, exit_time=timestamp, entry_price=entry_price,
                           exit_price=fill, quantity=qty, entry_fee=entry_fee, exit_fee=fee,
                           net_pnl_usdt=cash-invested, return_pct=(cash/invested-1)*100,
                           exit_reason=reason))
        qty = 0.0

    first_index = warmup
    if trade_start is not None:
        boundary = pd.Timestamp(trade_start)
        if boundary.tzinfo is None:
            raise ValueError('trade_start needs a timezone.')
        first_index = max(warmup, int(times.searchsorted(boundary)))
    if first_index >= len(candles):
        raise ValueError('No trading candles at or after trade_start.')
    for i in range(first_index, len(candles)):
        # t=warmup-1 is the first usable completed signal.
        if adjacent[i] and qty > 0 and ex[i-1]:
            sell(opens[i], times[i], 'signal')
        elif adjacent[i] and qty == 0 and en[i-1] and not ex[i-1] and i < len(candles)-1:
            entry_price = float(opens[i]) * (1 + costs.slippage)
            invested = cash
            qty = cash / (entry_price * (1 + costs.fee))
            entry_fee = qty * entry_price * costs.fee
            entry_time = times[i]
            cash = 0.0
        if i == len(candles)-1 and qty > 0:
            sell(closes[i], times[i] + pd.Timedelta(hours=1), 'end_of_data')
        values.append(cash + qty * closes[i])
    equity = pd.Series(values, index=times[first_index:], name='equity_usdt')
    equity.index.name = 'timestamp'
    trades = pd.DataFrame(trades, columns=TRADE_COLUMNS)
    # Include starting cash as an equity high so entry costs count in drawdown.
    peaks = np.maximum.accumulate(np.r_[initial_cash, equity.to_numpy()])[1:]
    drawdown = equity.to_numpy() / peaks - 1
    pnl = trades.net_pnl_usdt
    gross_loss = -pnl[pnl < 0].sum()
    sharpe, sharpe_samples = hourly_sharpe(equity, initial_cash)
    stats = dict(sharpe_ratio=sharpe, sharpe_hourly_samples=sharpe_samples, initial_cash_usdt=initial_cash, final_equity_usdt=float(equity.iloc[-1]),
                 return_pct=float((equity.iloc[-1]/initial_cash-1)*100),
                 max_drawdown_pct=float(-drawdown.min()*100), trades=len(trades),
                 win_rate_pct=float((pnl > 0).mean()*100) if len(trades) else None,
                 profit_factor=float(pnl[pnl > 0].sum()/gross_loss) if gross_loss > 0 else None,
                 total_fees_usdt=float((trades.entry_fee + trades.exit_fee).sum()))
    return stats, equity, trades
