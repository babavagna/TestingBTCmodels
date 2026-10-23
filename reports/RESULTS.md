# Actual historical comparison

Source: **Binance Vision** spot BTC/USDT 1-hour candles. Derived research output: CC BY-NC-SA 4.0; see [data terms](../sources/BINANCE_DATASET_TERMS.md).

Candle range: **2020-01-01T00:00:00+00:00 through 2026-09-30T23:00:00+00:00**.
First possible trade: 2020-01-09T08:00:00+00:00. Starting balance: 10,000 USDT per strategy.
Real candles used: 59,129. Gap events in this selection: 15. Missing hours across the requested source period: 31.

**Costs on each buy and each sell:** 0.1% fee plus 0.05% slippage.

| Strategy | Return after costs | Largest drawdown | Completed trades |
| --- | ---: | ---: | ---: |
| MACD + CCI | 966.46% | 77.20% | 1 |
| Buy and hold (reference) | 948.78% | 77.20% | 1 |
| MACD crossover + CCI | 491.33% | 75.90% | 15 |
| Quickie trend reversal | 163.05% | 77.75% | 9 |
| Bollinger + RSI | 47.46% | 76.52% | 208 |
| CCI + money flow + momentum | -23.69% | 66.47% | 76 |
| Simple momentum | -26.02% | 80.71% | 795 |
| Awesome Oscillator + MACD | -61.05% | 72.19% | 375 |
| ADX + moving averages | -83.57% | 95.33% | 708 |
| EMA crossover | -93.91% | 95.82% | 1347 |
| Rockwell MACD | -97.77% | 98.21% | 1585 |

**Read this before interpreting the ranking:**

- A high return based on one trade is weak evidence. It can largely reflect holding Bitcoin for years.
- Drawdown measures losses from an earlier high. The strategies can suffer very large losses even when their final return is positive.
- These are hourly entry/exit signal adaptations. Original bot ROI targets and stoploss rules are omitted for every strategy.
- Missing candles are never filled. Pending signals crossing gaps are canceled; indicators restart with 200 consecutive candles. Existing positions stay held during gaps and warmup.
- This is descriptive history without parameter optimization, not a forecast or a recommendation.

Download [summary.csv](summary.csv) for more metrics, [equity.csv.gz](equity.csv.gz) for portfolio history,
and the individual `*_trades.csv` files for each buy and sell.
[run.json](run.json) records assumptions and data/code/output fingerprints.
[data/manifest.json](../data/manifest.json) lists all official source files and missing hours.
