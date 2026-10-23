# Actual historical comparison

Source: **Binance Vision** spot BTC/USDT 1-hour candles. Derived research output: CC BY-NC-SA 4.0; see [data terms](../sources/BINANCE_DATASET_TERMS.md).

**10 strategy backtests completed successfully**, plus the buy-and-hold benchmark. Only completed runs are ranked.
Candle range: **2020-01-01T00:00:00+00:00 through 2026-09-30T23:00:00+00:00**.
First possible trade: 2020-01-09T08:00:00+00:00. Starting balance: 10,000 USDT per strategy.
Real candles used: 59,129. Gap events: 15. Missing hours in the requested source period: 31.

**Identical costs:** 0.1% fee plus 0.05% slippage on each buy and each sell. Same prices, warmup, gap policy and long/cash execution.

Ranked by total net return over the full period (not annual return), not by overall quality. The benchmark is unranked.

| Rank | Strategy | Net return | Sharpe | Max drawdown | Profit factor | Win rate | Trades | Buy-and-hold return | Sample flag |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | MACD + CCI | 966.46% | 0.87 | 77.20% | N/A | 100.00% | 1 | 948.78% | **TOO FEW** |
| 2 | MACD crossover + CCI | 491.33% | 0.73 | 75.90% | 1.61 | 73.33% | 15 | 948.78% | **TOO FEW** |
| 3 | Quickie trend reversal | 163.05% | 0.53 | 77.75% | 2.00 | 66.67% | 9 | 948.78% | **TOO FEW** |
| 4 | Bollinger + RSI | 47.46% | 0.34 | 76.52% | 1.04 | 63.94% | 208 | 948.78% | — |
| 5 | CCI + money flow + momentum | -23.69% | 0.11 | 66.47% | 0.93 | 56.58% | 76 | 948.78% | — |
| 6 | Simple momentum | -26.02% | 0.18 | 80.71% | 0.98 | 71.19% | 795 | 948.78% | — |
| 7 | Awesome Oscillator + MACD | -61.05% | -0.12 | 72.19% | 0.86 | 25.60% | 375 | 948.78% | — |
| 8 | ADX + moving averages | -83.57% | -0.40 | 95.33% | 0.91 | 38.98% | 708 | 948.78% | — |
| 9 | EMA crossover | -93.91% | -0.76 | 95.82% | 0.84 | 24.42% | 1347 | 948.78% | — |
| 10 | Rockwell MACD | -97.77% | -1.60 | 98.21% | 0.76 | 28.96% | 1585 | 948.78% | — |
| — | Buy and hold (reference) | 948.78% | 0.87 | 77.20% | N/A | 100.00% | 1 | 948.78% | benchmark |

**Too few trades:** fewer than 30 completed trades is flagged as a caution rule, not a statistical guarantee. More trades do not prove reliability.
N/A profit factor means no losing-trade dollars to divide by; it is not a claim of unlimited profit.

## Next-hour directional prediction accuracy

**No current strategy provides a next-hour directional forecast. Zero forecast models were scored.**
All ten produce trading entry/exit signals. A decision to buy can mean holding for years; it is not a claim that the next hour will rise.
Accuracy is therefore **N/A for every strategy**, not 0%, not 50%, and not the trade win rate.
The per-strategy audit is saved in [directional_predictions.csv](directional_predictions.csv).

A future forecast evaluation must compare a prediction made after hour t with the sign of close(t+1)/close(t)-1, only for adjacent hours.
It must also disclose scored forecasts, ties, abstentions, coverage, up/down class balance, a same-sample always-up baseline, and out-of-sample separation.

## What the numbers mean, in plain language

- **Net return:** how much the original money grew or shrank after costs. +50% turns 100 into 150; -50% turns 100 into 50.
- **Sharpe ratio:** average hourly gain divided by how much hourly gains jump around, scaled to a year. Think reward compared with bumpiness; higher is generally better. It is not a percentage, a guarantee, or a maximum-loss measure.
- **Maximum drawdown:** the worst recorded fall from an earlier account high. A 77% drawdown turns a peak of 100 into about 23 before any recovery.
- **Profit factor:** total money won on profitable trades divided by total money lost on losing trades, after costs. 1.5 means 1.50 won for each 1 lost. Below 1 means losses outweighed gains.
- **Win rate:** the percentage of completed trades that made money after costs. Many small wins can still be outweighed by a few big losses.
- **Trades:** completed buy-and-sell pairs. One winning trade is like judging a player after one game: too little evidence.
- **Buy-and-hold return:** what happened if you bought once at the shared start and sold at the end, paying the same costs. It is the comparison yardstick.
- **Directional accuracy:** the percentage of explicit next-hour up/down predictions that were right. This differs from winning a trade held for many hours.

## Calculation details and limits

Sharpe = mean(hourly simple net returns) / sample standard deviation × sqrt(8760); risk-free rate is 0%. Cash/idle hours and first-hour entry costs are included.
Returns spanning missing hours are excluded from Sharpe because they are not one-hour observations. They remain in total return and drawdown. This is a qualified Sharpe estimate on observed hours; no autocorrelation adjustment is applied.

A positive Sharpe can coexist with a negative compounded return. For example, +50% then -40% averages +5% per period, but 100 ends at 90. Gap exclusions also make the Sharpe sample different from the full return calculation.

- All strategies use the same observation timestamps. No prices are filled. Indicators restart with a shared 200-candle warmup after gaps; existing positions stay held.
- These are hourly signal adaptations, not exact native Freqtrade bots. Original ROI targets and stoploss rules are omitted for every strategy.
- Drawdown uses recorded closes and cannot measure losses within candles or missing hours.
- No parameters were optimized here. This is historical description, not independently validated future performance.

See [summary.csv](summary.csv), [equity.csv.gz](equity.csv.gz), individual `*_trades.csv` files and [run.json](run.json).
Source fingerprints and all missing timestamps: [data/manifest.json](../data/manifest.json).
