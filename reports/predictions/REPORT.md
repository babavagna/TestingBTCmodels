# Which indicators predicted Bitcoin direction best?

**This is a retrospective formula benchmark, not a test of every TradingView indicator.**

Actually completed **410 indicator/timeframe forecast tests** from **441 attempts**: 147 formula entries on each of 5m, 15m and 60m. This includes 61 named candlestick patterns. 31 attempts could not produce a learned forecast; see the workbook. No missing results are invented.

The separate 210-script public Pine corpus audit found 194 runtime failures and 16 completed compatibility probes. **A compatibility probe is not a forecast backtest.** Native TradingView formula matching is unverified, and private, paid and inaccessible scripts are outside coverage.

The evaluated object is **each indicator plus the same trained logistic model**. Most indicators do not make predictions by themselves. We predict whether the next closing price is above or below the current close, once the current candle has completed. This can differ from predicting a green/red candle body.

**Training:** 2020–2024, with a shared 2,048-candle initial burn-in on each timeframe. **Validation:** 2025 selects among preset window lengths. **Retrospective test:** January–September 2026, chosen by the user. Those market dates were already examined in earlier work. They are held out from this fitting step but are not genuinely untouched research evidence.

## The highest measured accuracy on each timeframe

| Chart / next close | Highest measured formula | Correct directions | Training-majority baseline | 2025 accuracy | Net trading return | Buy and hold |
|---|---|---:|---:|---:|---:|---:|
| 5m | Elder Force Index (EFI) | 51.91% | 49.91% | 51.16% | -100.00% | -4.88% |
| 15m | Williams' %R (WILLR) | 53.03% | 49.68% | 52.13% | -99.96% | -4.88% |
| 60m | Minus Directional Movement (MINUS_DM) | 53.19% | 49.85% | 51.78% | -89.95% | -4.88% |

**Highest accuracy does not mean a good trading strategy.** Small correct moves can earn less than the fee and slippage. An almost -100% return means the simulated balance was almost wiped out. These idealized fractional-BTC simulations omit minimum order sizes, lot rounding, latency and market impact; actual exchange minimums would stop tiny balances earlier.

**179 of 410 completed tests passed the limited retrospective accuracy gate. 0 passed the separate financial gate in both 2025 and 2026.** Passing an accuracy gate is not a claim of profitable or independent future performance.

Accuracy gate: positive baseline lift in both 2025 and 2026, positive lower 2026 seven-day block interval, approximate Holm-adjusted p<0.05 across all completed final comparisons, positive mean earlier walk-forward lift, adequate forecast/event counts. Financial gate: positive net return, beating costed buy-and-hold and at least 30 trades in both periods.

## Retrospective top 10 by next-close accuracy

Each table uses exactly the same real exchange observations and label timing within its timeframe. Ranks are descriptive; choosing a winner after seeing this table creates selection bias. Related indicators and candlestick patterns are not independent discoveries.

### 5-minute chart

| Rank | Formula | Accuracy | Lift over baseline | 95% block interval for lift | Trades | Net return | Accuracy gate |
|---:|---|---:|---:|---|---:|---:|---|
| 1 | [Elder Force Index](https://github.com/babavagna/TestingBTCmodels/blob/main/indicator_lab/features.py) | 51.91% | 2.00 pp | 1.63 to 2.40 pp | 8715 | -100.00% | Pass (retrospective only) |
| 2 | [Wilder Moving Average](https://github.com/babavagna/TestingBTCmodels/blob/main/indicator_lab/features.py) | 51.88% | 1.97 pp | 1.58 to 2.41 pp | 11648 | -100.00% | Pass (retrospective only) |
| 3 | [Kaufman Adaptive Moving Average](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_KAMA.c) | 51.86% | 1.95 pp | 1.56 to 2.40 pp | 10664 | -100.00% | Pass (retrospective only) |
| 4 | [Exponential Moving Average](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_EMA.c) | 51.78% | 1.87 pp | 1.47 to 2.30 pp | 11178 | -100.00% | Pass (retrospective only) |
| 5 | [Keltner Channels](https://github.com/babavagna/TestingBTCmodels/blob/main/indicator_lab/features.py) | 51.77% | 1.86 pp | 1.49 to 2.26 pp | 11142 | -100.00% | Pass (retrospective only) |
| 6 | [Moving Average Convergence/Divergence](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_MACD.c) | 51.74% | 1.83 pp | 1.44 to 2.26 pp | 9733 | -100.00% | Pass (retrospective only) |
| 7 | [Chande Momentum Oscillator](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_CMO.c) | 51.73% | 1.82 pp | 1.46 to 2.24 pp | 9801 | -100.00% | Pass (retrospective only) |
| 8 | [Relative Strength Index](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_RSI.c) | 51.73% | 1.82 pp | 1.46 to 2.24 pp | 9801 | -100.00% | Pass (retrospective only) |
| 9 | [Chaikin A/D Oscillator](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_ADOSC.c) | 51.73% | 1.82 pp | 1.48 to 2.23 pp | 9517 | -100.00% | Pass (retrospective only) |
| 10 | [Triangular Moving Average](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_TRIMA.c) | 51.72% | 1.81 pp | 1.46 to 2.21 pp | 11620 | -100.00% | Pass (retrospective only) |

### 15-minute chart

| Rank | Formula | Accuracy | Lift over baseline | 95% block interval for lift | Trades | Net return | Accuracy gate |
|---:|---|---:|---:|---|---:|---:|---|
| 1 | [Williams' %R](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_WILLR.c) | 53.03% | 3.35 pp | 2.56 to 4.08 pp | 2720 | -99.96% | Pass (retrospective only) |
| 2 | [Volume Weighted Moving Average](https://github.com/babavagna/TestingBTCmodels/blob/main/indicator_lab/features.py) | 52.74% | 3.06 pp | 2.45 to 3.69 pp | 3139 | -99.99% | Pass (retrospective only) |
| 3 | [True Strength Index](https://github.com/everget/tradingview-pinescript-indicators/blob/8385cc421888bbf31f36407195796bc0eabafb19/oscillators/tsi_true_strength_index.pine) | 52.65% | 2.97 pp | 2.27 to 3.70 pp | 3044 | -99.99% | Pass (retrospective only) |
| 4 | [Bollinger Bands](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_BBANDS.c) | 52.60% | 2.92 pp | 2.32 to 3.54 pp | 3542 | -100.00% | Pass (retrospective only) |
| 5 | [Simple Moving Average](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_SMA.c) | 52.59% | 2.91 pp | 2.30 to 3.54 pp | 3537 | -100.00% | Pass (retrospective only) |
| 6 | [Weighted Moving Average](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_WMA.c) | 52.57% | 2.89 pp | 2.30 to 3.47 pp | 3340 | -99.99% | Pass (retrospective only) |
| 7 | [Commodity Channel Index](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_CCI.c) | 52.55% | 2.88 pp | 2.20 to 3.52 pp | 2185 | -99.84% | Pass (retrospective only) |
| 8 | [Moving Average Convergence/Divergence](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_MACD.c) | 52.54% | 2.86 pp | 2.30 to 3.50 pp | 3240 | -99.99% | Pass (retrospective only) |
| 9 | [Exponential Moving Average](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_EMA.c) | 52.53% | 2.85 pp | 2.26 to 3.52 pp | 3512 | -100.00% | Pass (retrospective only) |
| 10 | [Keltner Channels](https://github.com/babavagna/TestingBTCmodels/blob/main/indicator_lab/features.py) | 52.49% | 2.81 pp | 2.17 to 3.49 pp | 3412 | -100.00% | Pass (retrospective only) |

### 60-minute chart

| Rank | Formula | Accuracy | Lift over baseline | 95% block interval for lift | Trades | Net return | Accuracy gate |
|---:|---|---:|---:|---|---:|---:|---|
| 1 | [Minus Directional Movement](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_MINUS_DM.c) | 53.19% | 3.34 pp | 2.24 to 4.58 pp | 842 | -89.95% | Pass (retrospective only) |
| 2 | [Stochastic Fast](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_STOCHF.c) | 53.05% | 3.21 pp | 1.98 to 4.49 pp | 832 | -90.92% | Pass (retrospective only) |
| 3 | [Stochastic](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_STOCH.c) | 53.04% | 3.19 pp | 1.86 to 4.50 pp | 808 | -90.32% | Pass (retrospective only) |
| 4 | [Fisher Transform](https://github.com/babavagna/TestingBTCmodels/blob/main/indicator_lab/features.py) | 52.84% | 2.99 pp | 1.74 to 4.21 pp | 648 | -85.35% | Pass (retrospective only) |
| 5 | [Stochastic Relative Strength Index](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_STOCHRSI.c) | 52.76% | 2.92 pp | 1.71 to 4.09 pp | 780 | -89.90% | Pass (retrospective only) |
| 6 | [Williams' %R](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_WILLR.c) | 52.73% | 2.88 pp | 1.62 to 4.14 pp | 848 | -92.21% | Pass (retrospective only) |
| 7 | [Minus Directional Indicator](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_MINUS_DI.c) | 52.66% | 2.81 pp | 1.57 to 3.92 pp | 779 | -89.59% | Pass (retrospective only) |
| 8 | [True Strength Index](https://github.com/everget/tradingview-pinescript-indicators/blob/8385cc421888bbf31f36407195796bc0eabafb19/oscillators/tsi_true_strength_index.pine) | 52.64% | 2.79 pp | 1.63 to 3.95 pp | 659 | -87.82% | Pass (retrospective only) |
| 9 | [Balance Of Power](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_BOP.c) | 52.56% | 2.72 pp | 1.36 to 3.89 pp | 1298 | -97.86% | Pass (retrospective only) |
| 10 | [Chande Momentum Oscillator](https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_CMO.c) | 52.47% | 2.63 pp | 1.31 to 3.72 pp | 1062 | -95.67% | Pass (retrospective only) |

## What was checked

- All distinct formula profiles were regenerated on earlier prefixes and with later prices/volume changed. A changed earlier value would quarantine that indicator. No result is promoted from a compatibility probe.
- Expanding walk-forward fits through 2021, 2022 and 2023 predicted 2022, 2023 and 2024. Default settings were fixed; later 2025 choices were not carried backward.
- Each fit learned its scaling and coefficients from training rows only. Labels reaching the fitting cutoff were purged. Three preset window profiles were selected using 2025 alone; hashes and coefficients were saved before new 2026 accuracy calculations.
- Other profiles were scored as parameter stress, and fees were halved/doubled, with a doubled fee-plus-slippage case. Model forecasts stay fixed during cost stress. Parameters without adjustable integer windows have only one distinct profile; do not interpret that as demonstrated parameter robustness.
- All comparisons use a training-majority baseline on matching labels. Always-up, always-down and previous-direction baselines are also reported. Accuracy intervals use paired seven-day blocks; approximate daily Newey–West p-values receive Holm correction across the complete final family.
- Rare candlestick occurrences, fewer than 1,000 scored forecasts and fewer than 30 completed trades are flagged. Some patterns never occurred in training and failed; some early walk-forward fits also failed for this reason.

These checks reduce selected sources of leakage. They do not prove freedom from every possible bug, native TradingView agreement or upstream historical optimization. Source versions were obtained after the historical test dates; this is not a reconstruction of which versions were available at the time. The 2025 scores participate in window selection and are not an independent check of that choice. Unknown published tuning, related tests, validation selection and already-seen market dates remain limitations. No genuine untouched OOS pass is claimed.

**Scoring coverage:** all completed models cover every eligible target in their reported period except the 5m Fisher Transform, which has five undefined feature rows in 2026. Those five directions are unscored for that model, its baseline uses the identical subset, and its exact coverage is shown in Excel. They are not invented or counted as correct. The three leading models have full eligible-target coverage.

## Prices and trading assumptions

Source: [Binance public data](https://github.com/binance/binance-public-data), official spot BTCUSDT monthly 5m archives, 2020-01 through 2026-09. All 81 archive checksums verified. The 15m and 60m observations use only complete groups from those same 5m prices. Missing data is not filled.

| Timeframe | Actual candles | Missing candles across full history | Missing in 2025/2026 scoring |
|---|---:|---:|---:|
| 5m | 709,458 | 462 | 0 |
| 15m | 236,483 | 157 | 0 |
| 60m | 59,115 | 45 | 0 |

All 59,115 derived hourly closes matched the previous official hourly dataset on shared timestamps. Extra incomplete hourly groups were discarded. Missing observations are before the validation and final scoring periods. Near gaps, indicator periods count observed candles rather than exact clock durations.

Trading starts with 10,000 USDT per period, long Bitcoin or hold cash, with no shorts or leverage. An UP forecast buys at the next adjacent candle open; a DOWN forecast sells there. Consecutive UP guesses stay in one holding. Fee **0.1%** and adverse slippage **0.05%** apply to **every buy and sell**. Positions are sold at the last real close. Buy-and-hold pays identical entry and exit costs. Future ties are excluded only from accuracy; their forecasts are never suppressed from trading.

## What the numbers mean (plain language)

- **Accuracy:** 53% means 53 correct directions out of 100. It says nothing about the sizes of the gains or losses.
- **Balanced accuracy:** average of the success rate on UP and DOWN moves, so the more common class cannot hide poor results on the other.
- **Lift:** extra correct guesses compared with the baseline. Two percentage points means two extra correct answers out of 100.
- **Confidence interval / adjusted p-value:** rough checks on whether an advantage could be chance. Trying many indicators makes lucky winners more likely; the adjustment helps, but cannot erase earlier research or unseen modeling choices.
- **Net return:** how much the starting money grew or shrank after trading costs.
- **Sharpe:** average daily account return divided by daily bumpiness, scaled to a year. Higher is generally better; not a percentage.
- **Maximum drawdown:** the worst observed-close fall from a previous high. A 40% drawdown turns a 10,000 peak into 6,000.
- **Profit factor:** total net dollars won divided by total net dollars lost on trades. Below 1 is losing overall. N/A if there are no losing dollars to divide by.
- **Trade win rate:** share of buy/sell trades that earned money after costs. This is different from prediction accuracy.
- **Trade count:** completed buys followed by sells. Below 30 is flagged because a few lucky trades tell little.
- **Buy and hold:** buy once, wait, sell at the end with the same entry/exit costs.
- **N/A:** missing, not run, unverified or mathematically undefined. Never an invented zero.

## Open the Excel file

[Open TradingView_Indicator_Predictions.xlsx on GitHub](https://github.com/babavagna/TestingBTCmodels/blob/main/reports/TradingView_Indicator_Predictions.xlsx). Sign in with the GitHub account that has repository access, then choose **Download raw file** (down arrow). Save it first, then open in Microsoft Excel or LibreOffice Calc. If you see **404**, check that the repository itself opens in the same browser/account: GitHub can hide inaccessible repositories using 404, and the raw-file domain may not share your login. The same workbook is in the Codex workspace at `reports/TradingView_Indicator_Predictions.xlsx`; the dashboard also provides a download button. A successful cloud download does not verify browser access.

Start on **Read Me**. **All Strategies** contains all 441 formula/timeframe attempts with explicit completion status. **Top 10** has ten retrospective rows for each timeframe. **Prediction Accuracy**, **Charts**, **Failed Tests**, **Walk Forward**, **Robustness**, **Pine Audit** and the source/data sheets preserve supporting evidence.

Models, exact probabilities and decisions, true labels, raw source formulas, checksum manifests and test evidence are saved beside the report. [Reproduction instructions](../../indicator_lab/README.md) and the [frozen protocol](../../indicator_lab/PROTOCOL.md) explain the implementation. The previous full-100 strategy report and workbook remain separate and available.
