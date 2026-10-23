# Full supplied list: 100-candidate execution and integrity audit

**100 candidates attempted; 83 completed valid hourly signal backtests; 17 blocked or quarantined.** Original native bots are not fully reproduced. No blocked candidate is reported as successfully tested.

**No genuine unseen-data ranking is available.** Earlier project work examined 2025 and January–September 2026. These chronological replays hold those years out of the new fitting step, but cannot restore an untouched test. All tables below are alphabetical diagnostics; no Top 10 winner is claimed. Upstream tuning history is unknown.

Open [the Excel workbook](../Bitcoin_Strategy_Leaderboard.xlsx) and choose **Read Me**, then **All Strategies**. On GitHub use **Download raw** to save the file. All 100 supplied entries have a row, including failures.

## Same prices and account rules

- Binance **spot BTC/USDT, 1-hour candles**, January 2020 through September 2026: 59,129 real candles from 81 official monthly archives. SHA-256 checksums were verified. There are 31 missing hours in 15 gaps before 2025; none are filled. The 2025 and 2026 scoring periods have no missing hours.
- Start each scored period with **10,000 USDT**. Buy Bitcoin or hold cash; no shorts or leverage. Pay **0.1% fee + 0.05% slippage on each side**. A signal from a completed hour trades at the next adjacent hour’s open. An open position is sold at the final close, including costs.
- The account assumes fills at the modeled prices. Order-book liquidity, partial fills, exchange quantity rounding and the intrahour price path are not simulated; these are not proof of real exchange fills.
- These are **signal-only adaptations**. Native profit targets, stoplosses, shorts, leverage, pyramiding and position sizing are omitted. The Freqtrade and Zenbot source hooks run through compatibility adapters. Eight supported Jesse entries are TA-Lib/pandas formula translations; exact native indicator/engine equivalence remains unverified.
- The common initial warmup is **4,096 observed candles**, covering long indicator histories. After that, indicators retain past observations across gaps; their periods count observed bars, not invented hourly rows. The engine forbids a trade across a missing-hour gap and holds any existing position. The first scored training hour is 2020-06-20 01:00 UTC; initial warmup hours are excluded from hourly return samples. Later idle cash hours are included. A gap can stretch a nominal indicator window in calendar time; all candidates receive the same observed prices.
- Training receives only 2020–2024 prices. Each fold records whether its candidates reach 30 completed training trades. A fold with too few trades retains the original profile; that fallback is not claimed as a qualified fit. The long initial warmup reduces the early training sample, but does not repeatedly discard entire years after short data gaps.

## Training, walk-forward and robustness checks

Three profiles were declared: original, lower 20%, higher 20%. For Freqtrade, numeric exposed parameters vary; if there are none, explicitly supplied TA-Lib periods vary. For Jesse, documented numeric rule settings vary. For Zenbot, numeric options vary, with the hourly period held fixed. Not every source exposes meaningful settings; duplicate behavior is not evidence of robustness.
Select using **training-only hourly Sharpe with at least 30 trades**, otherwise retain original. Purge the final fitting hour. Fit through 2021 and evaluate 2022; through 2022/evaluate 2023; through 2023/evaluate 2024. Final fitting ends at **2024-12-31 22:00 UTC**, and selected profiles are saved before 2025/2026 scoring. No validation/test score selects parameters.
All completed profiles are stressed with half/base/double fees (slippage 0.05%); the selected profile also gets double fee and double slippage. See [sensitivity.csv](sensitivity.csv), [walk_forward.csv](walk_forward.csv), [training_candidates.csv](training_candidates.csv), and per-candidate frozen selections and trades in [candidates/](candidates/). Losing money is not a software failure.
The [robustness summary](robustness_summary.csv) counts profitable parameter/cost scenarios, their return range, and profitable or benchmark-beating walk-forward folds. These overlapping scenarios are not independent evidence and are not used to pick a test winner.

A **diagnostic pass** requires positive net return, beating same-period buy and hold, and at least 30 completed trades. This rule was not changed to obtain more winners. It is not a proof of genuine out-of-sample success.

## Cheating and leakage review

Each completed profile passed five independently regenerated historical-prefix signal comparisons and one future-price mutation. In a causal rule, adding or changing later candles must not change an earlier decision. These are finite checks, not proof that every possible leak is absent.
**CCIStrategy (#24) and ReinforcedQuickie (#36) were quarantined.** Their published two-sided interpolation changed earlier numerical indicator values when later candles were included. Checking buy/sell signals alone can miss this because an indicator can change without crossing an entry threshold. Numerical examples and cutoffs are saved in each candidate JSON. Their previous intermediate financial files were removed from the valid comparison.
**Overfitting** is like memorizing a practice exam instead of learning the subject. Trying 100 strategies can produce lucky winners. Source selection and published hyperparameters may already reflect optimization over the same history. Neither good walk-forward numbers nor a small parameter grid eliminates that overfitting risk. No significance claim or guarantee of future profit is made.

## Next-hour directional prediction accuracy

**Zero forecast models were scored.** Neural (#76) really contains a price predictor, so it is not labeled “no forecast model.” Its native cluster/online-training interface is unsupported by the frozen-training adapter. Accuracy is **N/A — runtime incomplete**, with no fabricated percentage. The native strategy retrains each hour; silently training it on final-test prices would violate the requested separation.
Other evaluated adapters expose trading entry/exit rules, not an explicit next-hour forecast. Buying for a week does not mean predicting the next hour correctly. Trade win rate is not prediction accuracy. A future forecasting implementation needs adjacent-hour targets, timestamped forecasts, ties/coverage, class balance and an always-up baseline.

## 2025 validation diagnostics

**83 completed candidates. Buy and hold: -6.62%.** 2 meet this period’s diagnostic gate. These are previously seen dates, not an untouched ranking.

| Strategy | Net return % | Sharpe | Max drawdown % | Profit factor | Win rate % | Trades | Buy/hold % | Sample | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| ADXMomentum | -2.57 | 0.04 | 24.82 | 0.95 | 38.46 | 26 | -6.62 | TOO FEW | FAIL |
| AdxSmas | -33.73 | -1.22 | 39.00 | 0.59 | 32.94 | 85 | -6.62 | ≥30 | FAIL |
| ASDTSRockwellTrading | -60.96 | -3.94 | 62.81 | 0.52 | 25.61 | 246 | -6.62 | ≥30 | FAIL |
| AverageStrategy | -50.95 | -2.22 | 56.99 | 0.60 | 23.95 | 167 | -6.62 | ≥30 | FAIL |
| AwesomeMacd | -44.88 | -2.02 | 49.16 | 0.42 | 20.63 | 63 | -6.62 | ≥30 | FAIL |
| Bandtastic | -30.65 | -0.81 | 48.09 | 0.73 | 63.43 | 134 | -6.62 | ≥30 | FAIL |
| BbandRsi | -2.50 | 0.09 | 31.35 | 0.92 | 63.64 | 22 | -6.62 | TOO FEW | FAIL |
| BinHV27 | -7.89 | -0.30 | 15.92 | 0.69 | 47.37 | 19 | -6.62 | TOO FEW | FAIL |
| BinHV45 | -14.85 | -0.18 | 34.76 | 0.00 | 0.00 | 1 | -6.62 | TOO FEW | FAIL |
| bollinger | -15.48 | -0.33 | 34.42 | 0.85 | 63.11 | 103 | -6.62 | ≥30 | FAIL |
| cci_srsi | -10.82 | -0.12 | 32.39 | 0.75 | 47.37 | 19 | -6.62 | TOO FEW | FAIL |
| ClucMay72018 | 3.51 | 0.32 | 9.51 | 1.20 | 53.85 | 13 | -6.62 | TOO FEW | FAIL |
| CMCWinner | 4.94 | 0.31 | 25.44 | 1.19 | 53.85 | 13 | -6.62 | TOO FEW | FAIL |
| CofiBitStrategy | -11.06 | -0.73 | 18.86 | 0.69 | 54.24 | 59 | -6.62 | ≥30 | FAIL |
| CombinedBinHAndCluc | 9.87 | 0.67 | 10.53 | 1.41 | 61.54 | 26 | -6.62 | TOO FEW | FAIL |
| crossover_vwap | -5.67 | -0.05 | 20.71 | 0.71 | 60.00 | 10 | -6.62 | TOO FEW | FAIL |
| dema | -53.04 | -2.35 | 58.27 | 0.58 | 24.18 | 153 | -6.62 | ≥30 | FAIL |
| Diamond | 0.00 | N/A | -0.00 | N/A | N/A | 0 | -6.62 | TOO FEW | FAIL |
| Donchian | -18.41 | -0.68 | 24.80 | 0.72 | 34.48 | 58 | -6.62 | ≥30 | FAIL |
| ehlers_ft | -89.39 | -6.64 | 89.86 | 0.54 | 26.29 | 814 | -6.62 | ≥30 | FAIL |
| ehlers_mama | 0.00 | N/A | -0.00 | N/A | N/A | 0 | -6.62 | TOO FEW | FAIL |
| ehlers_trend | 0.00 | N/A | -0.00 | N/A | N/A | 0 | -6.62 | TOO FEW | FAIL |
| EMASkipPump | -22.63 | -0.57 | 35.49 | 0.79 | 61.40 | 114 | -6.62 | ≥30 | FAIL |
| FAdxSmaStrategy | -11.27 | -2.40 | 11.27 | 0.00 | 0.00 | 7 | -6.62 | TOO FEW | FAIL |
| FReinforcedStrategy | -4.96 | -2.31 | 5.29 | 0.04 | 14.29 | 7 | -6.62 | TOO FEW | FAIL |
| FSampleStrategy | -7.86 | 0.03 | 34.76 | 0.76 | 50.00 | 2 | -6.62 | TOO FEW | FAIL |
| FSupertrendStrategy | -27.67 | -1.23 | 34.39 | 0.59 | 28.57 | 49 | -6.62 | ≥30 | FAIL |
| HLHB | -32.56 | -0.93 | 39.57 | 0.55 | 25.93 | 27 | -6.62 | TOO FEW | FAIL |
| HourBasedStrategy | -6.62 | 0.07 | 34.76 | 0.00 | 0.00 | 1 | -6.62 | TOO FEW | FAIL |
| ichimoku | -74.20 | -4.80 | 75.06 | 0.49 | 16.09 | 404 | -6.62 | ≥30 | FAIL |
| ichimoku_score | -48.48 | -2.83 | 50.99 | 0.53 | 19.46 | 185 | -6.62 | ≥30 | FAIL |
| IFR2 | -10.09 | -1.27 | 12.66 | 0.48 | 50.00 | 48 | -6.62 | ≥30 | FAIL |
| kc | -27.51 | -0.81 | 40.83 | 0.77 | 63.69 | 157 | -6.62 | ≥30 | FAIL |
| Low_BB | 0.44 | 0.10 | 10.30 | N/A | 100.00 | 1 | -6.62 | TOO FEW | FAIL |
| mabStra | -6.62 | 0.07 | 34.76 | 0.00 | 0.00 | 1 | -6.62 | TOO FEW | FAIL |
| macd | -62.31 | -3.08 | 64.52 | 0.61 | 28.27 | 283 | -6.62 | ≥30 | FAIL |
| MACD_EMA | -50.24 | -2.32 | 55.05 | 0.51 | 21.19 | 118 | -6.62 | ≥30 | FAIL |
| MACDStrategy | -8.94 | 0.01 | 34.76 | 0.00 | 0.00 | 1 | -6.62 | TOO FEW | FAIL |
| MACDStrategy_crossed | -7.46 | 0.04 | 34.76 | 0.72 | 50.00 | 2 | -6.62 | TOO FEW | FAIL |
| MAGen | -13.03 | -0.10 | 35.43 | 0.83 | 51.11 | 45 | -6.62 | ≥30 | FAIL |
| momentum | -90.77 | -7.35 | 90.87 | 0.51 | 21.96 | 856 | -6.62 | ≥30 | FAIL |
| multi | -81.34 | -5.76 | 83.13 | 0.51 | 27.68 | 578 | -6.62 | ≥30 | FAIL |
| MultiMa | 6.84 | 1.19 | 3.63 | 4.31 | 50.00 | 4 | -6.62 | TOO FEW | FAIL |
| MultiRSI | -1.35 | -0.00 | 11.17 | 0.96 | 50.00 | 36 | -6.62 | ≥30 | FAIL |
| PatternRecognition | -6.45 | 0.07 | 34.76 | 0.00 | 0.00 | 1 | -6.62 | TOO FEW | FAIL |
| pivot | -53.58 | -2.70 | 56.67 | 0.62 | 26.05 | 261 | -6.62 | ≥30 | FAIL |
| Quickie | -9.87 | -0.01 | 34.76 | 0.00 | 0.00 | 1 | -6.62 | TOO FEW | FAIL |
| ReinforcedAverageStrategy | -24.93 | -1.50 | 27.73 | 0.61 | 18.67 | 75 | -6.62 | ≥30 | FAIL |
| ReinforcedSmoothScalp | -0.55 | 0.03 | 12.84 | 0.83 | 50.00 | 4 | -6.62 | TOO FEW | FAIL |
| renko | -49.18 | -2.34 | 50.66 | 0.41 | 15.17 | 145 | -6.62 | ≥30 | FAIL |
| RSI2 | -50.49 | -5.12 | 50.49 | 0.22 | 34.05 | 185 | -6.62 | ≥30 | FAIL |
| Scalp | -17.22 | -1.40 | 19.47 | 0.50 | 47.14 | 70 | -6.62 | ≥30 | FAIL |
| Simple | -12.05 | -0.11 | 36.40 | 0.90 | 66.99 | 103 | -6.62 | ≥30 | FAIL |
| SimpleBollinger | -50.23 | -3.17 | 52.49 | 0.45 | 24.81 | 133 | -6.62 | ≥30 | FAIL |
| SMACrossover | -17.74 | -0.51 | 27.85 | 0.68 | 24.32 | 37 | -6.62 | ≥30 | FAIL |
| SmoothOperator | -8.43 | -0.14 | 29.57 | 0.80 | 51.85 | 27 | -6.62 | TOO FEW | FAIL |
| SmoothScalp | 8.10 | 0.49 | 18.08 | 1.37 | 62.50 | 24 | -6.62 | TOO FEW | FAIL |
| speed | -50.87 | -2.06 | 54.87 | 0.65 | 27.60 | 192 | -6.62 | ≥30 | FAIL |
| srsi_macd | -14.84 | -0.37 | 26.81 | 0.72 | 37.04 | 27 | -6.62 | TOO FEW | FAIL |
| stddev | -21.47 | -1.17 | 25.88 | 0.64 | 30.77 | 52 | -6.62 | ≥30 | FAIL |
| Strategy001 | -7.46 | 0.05 | 34.76 | 0.00 | 0.00 | 1 | -6.62 | TOO FEW | FAIL |
| Strategy002 | -4.69 | -0.56 | 9.94 | 0.33 | 33.33 | 3 | -6.62 | TOO FEW | FAIL |
| Strategy003 | -13.76 | -0.85 | 23.14 | 0.39 | 55.56 | 9 | -6.62 | TOO FEW | FAIL |
| Strategy004 | 12.71 | 0.87 | 12.05 | 2.67 | 69.23 | 13 | -6.62 | TOO FEW | FAIL |
| Strategy005 | 6.62 | 0.38 | 18.71 | 1.29 | 60.00 | 15 | -6.62 | TOO FEW | FAIL |
| Supertrend | -22.46 | -0.75 | 37.12 | 0.61 | 33.33 | 33 | -6.62 | ≥30 | FAIL |
| SwingHighToSky | -1.75 | 0.16 | 33.22 | 0.95 | 55.56 | 9 | -6.62 | TOO FEW | FAIL |
| ta_srsi_bollinger | -36.39 | -1.51 | 45.18 | 0.47 | 49.06 | 53 | -6.62 | ≥30 | FAIL |
| ta_stoch_bollinger | 6.52 | 0.36 | 30.03 | 1.09 | 56.10 | 41 | -6.62 | ≥30 | PASS |
| TDSequentialStrategy | -33.40 | -1.15 | 42.40 | 0.56 | 49.28 | 69 | -6.62 | ≥30 | FAIL |
| TechnicalExampleStrategy | -79.16 | -4.69 | 80.46 | 0.42 | 33.33 | 453 | -6.62 | ≥30 | FAIL |
| ti_bollinger | -17.53 | -0.39 | 34.36 | 0.86 | 60.39 | 154 | -6.62 | ≥30 | FAIL |
| ti_stoch | 0.51 | 0.12 | 12.11 | 1.02 | 58.97 | 39 | -6.62 | ≥30 | PASS |
| ti_stoch_bollinger | 11.51 | 0.57 | 16.95 | 2.12 | 75.00 | 4 | -6.62 | TOO FEW | FAIL |
| TradingView_RSI | -18.23 | -0.27 | 39.88 | 0.87 | 42.86 | 63 | -6.62 | ≥30 | FAIL |
| trend_bollinger | -14.01 | -0.28 | 38.43 | 0.87 | 59.18 | 98 | -6.62 | ≥30 | FAIL |
| trend_ema | -44.39 | -1.83 | 49.27 | 0.64 | 22.09 | 163 | -6.62 | ≥30 | FAIL |
| TrendFollowingStrategy | -7.43 | 0.05 | 34.76 | 0.00 | 0.00 | 1 | -6.62 | TOO FEW | FAIL |
| trendline | -10.85 | -0.04 | 34.76 | 0.00 | 0.00 | 1 | -6.62 | TOO FEW | FAIL |
| trust_distrust | 0.00 | N/A | -0.00 | N/A | N/A | 0 | -6.62 | TOO FEW | FAIL |
| UniversalMACD | -11.69 | -0.09 | 34.76 | 0.00 | 0.00 | 1 | -6.62 | TOO FEW | FAIL |
| VolatilitySystem | -10.38 | -0.24 | 29.37 | 0.73 | 38.89 | 18 | -6.62 | TOO FEW | FAIL |
| wavetrend | -1.99 | 0.03 | 19.08 | 0.87 | 55.56 | 18 | -6.62 | TOO FEW | FAIL |

With **both costs doubled**, 8/83 selected profiles remain profitable. This is a sensitivity check, not a new selection step.

## January–September 2026 diagnostics

**83 completed candidates. Buy and hold: -4.88%.** 1 meet this period’s diagnostic gate. These are previously seen dates, not an untouched ranking.

| Strategy | Net return % | Sharpe | Max drawdown % | Profit factor | Win rate % | Trades | Buy/hold % | Sample | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| ADXMomentum | -22.31 | -1.02 | 37.55 | 0.58 | 28.57 | 28 | -4.88 | TOO FEW | FAIL |
| AdxSmas | -14.70 | -0.56 | 34.66 | 0.75 | 45.31 | 64 | -4.88 | ≥30 | FAIL |
| ASDTSRockwellTrading | -24.62 | -1.54 | 37.46 | 0.72 | 29.71 | 175 | -4.88 | ≥30 | FAIL |
| AverageStrategy | -25.06 | -1.22 | 39.56 | 0.70 | 27.48 | 131 | -4.88 | ≥30 | FAIL |
| AwesomeMacd | -17.46 | -0.75 | 39.90 | 0.70 | 25.64 | 39 | -4.88 | ≥30 | FAIL |
| Bandtastic | -45.55 | -2.14 | 49.25 | 0.49 | 54.17 | 96 | -4.88 | ≥30 | FAIL |
| BbandRsi | -6.42 | -0.10 | 33.04 | 0.85 | 81.25 | 16 | -4.88 | TOO FEW | FAIL |
| BinHV27 | -32.37 | -2.03 | 36.23 | 0.14 | 40.00 | 15 | -4.88 | TOO FEW | FAIL |
| BinHV45 | -4.83 | 0.05 | 35.66 | 0.00 | 0.00 | 1 | -4.88 | TOO FEW | FAIL |
| bollinger | -42.35 | -2.13 | 47.45 | 0.39 | 50.00 | 72 | -4.88 | ≥30 | FAIL |
| cci_srsi | 0.45 | 0.18 | 26.84 | 1.01 | 37.50 | 16 | -4.88 | TOO FEW | FAIL |
| ClucMay72018 | 9.48 | 1.06 | 5.84 | 4.01 | 70.00 | 10 | -4.88 | TOO FEW | FAIL |
| CMCWinner | -28.73 | -1.16 | 38.74 | 0.32 | 50.00 | 6 | -4.88 | TOO FEW | FAIL |
| CofiBitStrategy | -20.79 | -1.86 | 22.40 | 0.35 | 53.66 | 41 | -4.88 | ≥30 | FAIL |
| CombinedBinHAndCluc | 10.94 | 1.00 | 7.89 | 2.68 | 62.50 | 16 | -4.88 | TOO FEW | FAIL |
| crossover_vwap | -22.56 | -0.69 | 34.65 | 0.31 | 66.67 | 9 | -4.88 | TOO FEW | FAIL |
| dema | -21.20 | -0.97 | 37.99 | 0.74 | 26.89 | 119 | -4.88 | ≥30 | FAIL |
| Diamond | 0.00 | N/A | -0.00 | N/A | N/A | 0 | -4.88 | TOO FEW | FAIL |
| Donchian | -11.79 | -0.55 | 26.65 | 0.79 | 31.37 | 51 | -4.88 | ≥30 | FAIL |
| ehlers_ft | -86.14 | -8.63 | 86.34 | 0.42 | 23.11 | 623 | -4.88 | ≥30 | FAIL |
| ehlers_mama | 0.00 | N/A | -0.00 | N/A | N/A | 0 | -4.88 | TOO FEW | FAIL |
| ehlers_trend | 0.00 | N/A | -0.00 | N/A | N/A | 0 | -4.88 | TOO FEW | FAIL |
| EMASkipPump | -36.53 | -1.72 | 43.27 | 0.50 | 50.63 | 79 | -4.88 | ≥30 | FAIL |
| FAdxSmaStrategy | -5.78 | -1.21 | 8.03 | 0.07 | 16.67 | 6 | -4.88 | TOO FEW | FAIL |
| FReinforcedStrategy | -1.55 | -0.33 | 4.27 | 0.60 | 28.57 | 7 | -4.88 | TOO FEW | FAIL |
| FSampleStrategy | -5.77 | 0.02 | 42.02 | 0.76 | 66.67 | 3 | -4.88 | TOO FEW | FAIL |
| FSupertrendStrategy | -7.69 | -0.32 | 24.93 | 0.82 | 32.50 | 40 | -4.88 | ≥30 | FAIL |
| HLHB | -37.45 | -1.78 | 42.34 | 0.32 | 40.00 | 25 | -4.88 | TOO FEW | FAIL |
| HourBasedStrategy | -4.88 | 0.06 | 40.31 | 0.00 | 0.00 | 1 | -4.88 | TOO FEW | FAIL |
| ichimoku | -55.43 | -3.90 | 62.43 | 0.49 | 17.59 | 290 | -4.88 | ≥30 | FAIL |
| ichimoku_score | -31.13 | -2.14 | 47.27 | 0.58 | 17.99 | 139 | -4.88 | ≥30 | FAIL |
| IFR2 | -1.70 | -0.27 | 7.14 | 0.86 | 56.82 | 44 | -4.88 | ≥30 | FAIL |
| kc | -37.65 | -1.83 | 41.08 | 0.57 | 57.66 | 111 | -4.88 | ≥30 | FAIL |
| Low_BB | 13.99 | 0.63 | 29.36 | N/A | 100.00 | 1 | -4.88 | TOO FEW | FAIL |
| mabStra | -4.88 | 0.06 | 40.31 | 0.00 | 0.00 | 1 | -4.88 | TOO FEW | FAIL |
| macd | -32.50 | -1.58 | 46.30 | 0.73 | 29.70 | 202 | -4.88 | ≥30 | FAIL |
| MACD_EMA | -2.82 | 0.00 | 25.10 | 0.95 | 27.63 | 76 | -4.88 | ≥30 | FAIL |
| MACDStrategy | -8.34 | -0.06 | 40.31 | 0.00 | 0.00 | 1 | -4.88 | TOO FEW | FAIL |
| MACDStrategy_crossed | -11.27 | -0.21 | 38.03 | 0.66 | 33.33 | 3 | -4.88 | TOO FEW | FAIL |
| MAGen | -25.63 | -0.73 | 47.23 | 0.63 | 39.47 | 38 | -4.88 | ≥30 | FAIL |
| momentum | -88.05 | -9.31 | 88.14 | 0.39 | 17.44 | 665 | -4.88 | ≥30 | FAIL |
| multi | -77.39 | -7.40 | 77.90 | 0.43 | 23.16 | 449 | -4.88 | ≥30 | FAIL |
| MultiMa | 0.49 | 0.11 | 10.38 | 1.06 | 33.33 | 6 | -4.88 | TOO FEW | FAIL |
| MultiRSI | -6.00 | -0.56 | 17.62 | 0.72 | 45.45 | 22 | -4.88 | TOO FEW | FAIL |
| PatternRecognition | -5.17 | 0.05 | 40.31 | 0.00 | 0.00 | 1 | -4.88 | TOO FEW | FAIL |
| pivot | -29.93 | -1.63 | 44.38 | 0.72 | 27.49 | 171 | -4.88 | ≥30 | FAIL |
| Quickie | -9.42 | -0.10 | 40.31 | 0.39 | 50.00 | 2 | -4.88 | TOO FEW | FAIL |
| ReinforcedAverageStrategy | -6.80 | -0.35 | 15.82 | 0.86 | 28.57 | 70 | -4.88 | ≥30 | FAIL |
| ReinforcedSmoothScalp | 2.10 | 0.47 | 5.12 | N/A | 100.00 | 2 | -4.88 | TOO FEW | FAIL |
| renko | -20.93 | -0.96 | 35.33 | 0.64 | 15.79 | 95 | -4.88 | ≥30 | FAIL |
| RSI2 | -27.59 | -3.90 | 27.71 | 0.32 | 34.25 | 146 | -4.88 | ≥30 | FAIL |
| Scalp | -17.25 | -1.66 | 23.02 | 0.40 | 52.00 | 50 | -4.88 | ≥30 | FAIL |
| Simple | -33.59 | -1.15 | 43.35 | 0.59 | 65.67 | 67 | -4.88 | ≥30 | FAIL |
| SimpleBollinger | -14.27 | -0.85 | 29.38 | 0.77 | 31.46 | 89 | -4.88 | ≥30 | FAIL |
| SMACrossover | 11.17 | 0.66 | 18.90 | 1.42 | 42.11 | 19 | -4.88 | TOO FEW | FAIL |
| SmoothOperator | -16.90 | -0.65 | 32.57 | 0.61 | 71.43 | 21 | -4.88 | TOO FEW | FAIL |
| SmoothScalp | -17.12 | -1.17 | 22.86 | 0.45 | 62.50 | 16 | -4.88 | TOO FEW | FAIL |
| speed | -33.47 | -1.59 | 47.90 | 0.68 | 31.21 | 141 | -4.88 | ≥30 | FAIL |
| srsi_macd | -9.41 | -0.34 | 34.04 | 0.77 | 38.46 | 26 | -4.88 | TOO FEW | FAIL |
| stddev | -15.35 | -1.03 | 27.46 | 0.60 | 25.00 | 44 | -4.88 | ≥30 | FAIL |
| Strategy001 | -5.53 | 0.04 | 40.31 | 0.00 | 0.00 | 1 | -4.88 | TOO FEW | FAIL |
| Strategy002 | 0.00 | N/A | -0.00 | N/A | N/A | 0 | -4.88 | TOO FEW | FAIL |
| Strategy003 | -5.88 | -1.02 | 9.13 | 0.11 | 33.33 | 3 | -4.88 | TOO FEW | FAIL |
| Strategy004 | -20.11 | -1.46 | 25.54 | 0.00 | 0.00 | 3 | -4.88 | TOO FEW | FAIL |
| Strategy005 | -22.95 | -1.43 | 32.45 | 0.26 | 33.33 | 9 | -4.88 | TOO FEW | FAIL |
| Supertrend | -19.47 | -0.91 | 38.22 | 0.61 | 37.93 | 29 | -4.88 | TOO FEW | FAIL |
| SwingHighToSky | -27.21 | -0.83 | 40.31 | 0.06 | 33.33 | 3 | -4.88 | TOO FEW | FAIL |
| ta_srsi_bollinger | 9.81 | 0.56 | 28.01 | 1.23 | 43.33 | 30 | -4.88 | ≥30 | PASS |
| ta_stoch_bollinger | -12.17 | -0.28 | 34.40 | 0.78 | 66.67 | 27 | -4.88 | TOO FEW | FAIL |
| TDSequentialStrategy | -35.78 | -1.89 | 38.13 | 0.37 | 46.34 | 41 | -4.88 | ≥30 | FAIL |
| TechnicalExampleStrategy | -73.95 | -5.68 | 74.67 | 0.35 | 32.62 | 374 | -4.88 | ≥30 | FAIL |
| ti_bollinger | -29.63 | -1.27 | 41.61 | 0.63 | 57.84 | 102 | -4.88 | ≥30 | FAIL |
| ti_stoch | -6.58 | -0.40 | 17.94 | 0.71 | 54.55 | 22 | -4.88 | TOO FEW | FAIL |
| ti_stoch_bollinger | -32.37 | -1.49 | 44.85 | 0.07 | 25.00 | 4 | -4.88 | TOO FEW | FAIL |
| TradingView_RSI | -33.45 | -1.17 | 45.59 | 0.65 | 36.54 | 52 | -4.88 | ≥30 | FAIL |
| trend_bollinger | -32.29 | -1.40 | 37.30 | 0.55 | 51.43 | 70 | -4.88 | ≥30 | FAIL |
| trend_ema | -27.78 | -1.38 | 43.93 | 0.67 | 23.81 | 126 | -4.88 | ≥30 | FAIL |
| TrendFollowingStrategy | -5.13 | 0.05 | 40.31 | 0.00 | 0.00 | 1 | -4.88 | TOO FEW | FAIL |
| trendline | -4.88 | 0.06 | 40.31 | 0.00 | 0.00 | 1 | -4.88 | TOO FEW | FAIL |
| trust_distrust | 0.00 | N/A | -0.00 | N/A | N/A | 0 | -4.88 | TOO FEW | FAIL |
| UniversalMACD | -0.12 | 0.20 | 31.14 | 0.00 | 0.00 | 1 | -4.88 | TOO FEW | FAIL |
| VolatilitySystem | 1.93 | 0.23 | 23.83 | 1.06 | 33.33 | 12 | -4.88 | TOO FEW | FAIL |
| wavetrend | -28.77 | -1.29 | 39.43 | 0.39 | 52.94 | 17 | -4.88 | TOO FEW | FAIL |

With **both costs doubled**, 6/83 selected profiles remain profitable. This is a sensitivity check, not a new selection step.

**0 candidates pass both period-specific diagnostic gates.** No candidate has verified genuinely untouched OOS validation.

## Failed or incomplete candidates

| List # | Candidate | Status | Recorded reason |
|---:|---|---|---|
| 3 | GodStra | blocked_execution | ValueError: Indicator method changed candle count |
| 4 | Heracles | blocked_execution | ValueError: Indicator method changed candle count |
| 24 | CCIStrategy | quarantined_lookahead | DataError: LOOKAHEAD_DETECTED: published two-sided interpolation changed 4 earlier indicator cells when future candles were added; original signals are quarantined even if a threshold did not cross |
| 36 | ReinforcedQuickie | quarantined_lookahead | DataError: LOOKAHEAD_DETECTED: published two-sided interpolation changed 1 earlier indicator cells when future candles were added; original signals are quarantined even if a threshold did not cross |
| 45 | FOttStrategy | blocked_execution | TimeoutError: Signal generation exceeded the declared 120-second per-call limit |
| 53 | DUAL_THRUST | blocked_execution | NotImplementedError: UNSUPPORTED_NATIVE_STATE: DUAL_THRUST needs anchored multi-timeframe bars or pyramiding/fill callbacks; no substitute strategy was invented |
| 62 | TurtleRules | blocked_execution | NotImplementedError: UNSUPPORTED_NATIVE_STATE: TurtleRules needs anchored multi-timeframe bars or pyramiding/fill callbacks; no substitute strategy was invented |
| 76 | neural | blocked_execution | RuntimeError: Error: UNSUPPORTED_FORECAST_RUNTIME: native predictor forks a cluster and retrains each scoring hour; frozen training/forecast adapter is required before directional accuracy can be measured     at main (/workspace/TestingBTCmodels/full_universe/zenbot_runner.cjs:25:36)     at Object.<anonymous> (/workspace/TestingBTCmodels/full_universe/zenbot_runner.cjs:45:1)     at Module._compile (node:internal/modules/cjs/loader:1872:14)     at |
| 79 | rsi | blocked_execution | RuntimeError: Error: Cannot find module 'timebucket' Require stack: - /workspace/TestingBTCmodels/sources/full100/zenbot/lib/engine.js - /workspace/TestingBTCmodels/sources/full100/zenbot/extensions/strategies/rsi/strategy.js - /workspace/TestingBTCmodels/full_universe/zenbot_runner.cjs     at Module._resolveFilename (node:internal/modules/cjs/loader:1517:15)     at wrapResolveFilename (node:internal/modules/cjs/loader:1071:27)     at defaultReso |
| 80 | sar | blocked_execution | RuntimeError: Error: UNSUPPORTED_STATE: source reads native account/trade history; coupled fill-state adapter required     at main (/workspace/TestingBTCmodels/full_universe/zenbot_runner.cjs:26:49)     at Object.<anonymous> (/workspace/TestingBTCmodels/full_universe/zenbot_runner.cjs:45:1)     at Module._compile (node:internal/modules/cjs/loader:1872:14)     at Object..js (node:internal/modules/cjs/loader:2003:10)     at Module.load (node:intern |
| 84 | ta_ema | blocked_execution | TimeoutError: Signal generation exceeded the declared 120-second per-call limit |
| 85 | ta_macd | blocked_execution | TimeoutError: Signal generation exceeded the declared 120-second per-call limit |
| 86 | ta_macd_ext | blocked_execution | TimeoutError: Signal generation exceeded the declared 120-second per-call limit |
| 87 | ta_ppo | blocked_execution | TimeoutError: Signal generation exceeded the declared 120-second per-call limit |
| 90 | ta_trix | blocked_execution | TimeoutError: Signal generation exceeded the declared 120-second per-call limit |
| 91 | ta_ultosc | blocked_execution | TimeoutError: Signal generation exceeded the declared 120-second per-call limit |
| 93 | ti_hma | blocked_execution | TimeoutError: Signal generation exceeded the declared 120-second per-call limit |

The 120-second limit applies to each complete signal-generation call. A timeout means the calculation did not finish here; it is not evidence that the strategy loses money. Missing runtime adapters mean the original program needs additional integration, not that a replacement model was tested.

## Metrics explained simply

- **Net return:** change in your starting money after costs. +20% turns 100 into 120.
- **Sharpe:** average hourly gain compared with bumpiness, scaled to a year using sqrt(8,760). Higher often means a smoother ride; it is not a percentage or a promise. Zero risk-free rate, idle cash hours and first-entry costs are included. Changes spanning missing hours are excluded from this ratio only.
- **Maximum drawdown:** biggest recorded fall from a previous account peak. A 30% fall turns a peak of 100 into 70. Hourly closes miss intrahour losses.
- **Profit factor:** total winning-trade dollars divided by total losing-trade dollars. Above 1 means wins outweighed losses. N/A means no loss dollars to divide by; it does not mean unlimited profit.
- **Win rate:** fraction of completed trades that made money. Many tiny wins can still be wiped out by one big loss.
A positive Sharpe can coexist with a losing compounded balance: average hourly changes and multiplied account growth measure different things. The gap exclusion also changes the Sharpe sample.

- **Trades:** completed buy/sell pairs. Fewer than 30 is flagged as too little evidence. Zero trades is a measured outcome, with undefined win rate.
- **Buy and hold:** buy once and sell at the end with identical costs. It is the yardstick.
- **Prediction accuracy:** how often a genuine next-hour up/down forecast was correct. Different from trade win rate. No such accuracy was measured here.

## Reproduce and verify

Run `bash setup.sh`, then `.venv/bin/python -m full_universe.audit --workers 3`, `.venv/bin/python -m pytest -q --junitxml=reports/test-results.xml`, and `.venv/bin/python -m scripts.export_full_leaderboard`. Node.js 24 and build tools are required for the old native Zenbot indicator libraries. Saved reports open without executing those libraries.
The manifest [run.json](run.json) fingerprints the code, all original sources, dataset and saved outputs. [inventory.csv](inventory.csv) records all 100 attempts. [failed_tests.csv](failed_tests.csv) preserves execution errors. [causality.csv](causality.csv) records executed checks. The same-source price evidence is in [data/manifest.json](../../data/manifest.json).
Data and derived research retain the saved Binance CC BY-NC-SA 4.0 terms; upstream strategy code retains its stated license.
