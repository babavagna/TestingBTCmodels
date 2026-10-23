# Strategy integrity and chronological robustness audit

**No strategy qualifies for a genuinely unseen-data ranking.** The previous full-period study already inspected 2025 and January–September 2026.
These are retrospective chronological diagnostics. Parameters are selected without those periods in this audit, but this cannot erase earlier exposure.
All tables below are alphabetical, not performance rankings. The unseen leaderboard is intentionally empty.

## What was checked

- Executed 240 actual-data prefix/future-mutation checks across all ten strategies and all three settings.
- Checked saved upstream source fingerprints and syntax patterns for future shifts, centered windows and backward filling. This is evidence of causal behavior, not a mathematical proof or an accusation of intent.
- Training chooses from original / roughly -20% / roughly +20% parameter settings using only 2020–2024. These are rules, not fitted machine-learning models.
- Walk-forward: fit through 2021 then evaluate 2022; fit through 2022 then evaluate 2023; fit through 2023 then evaluate 2024. Each fit sees past candles only.
- Fit through 2024 once, freeze the settings, evaluate 2025 for validation, then January–September 2026 without refitting on 2025 or rescuing failures.
- Training last hour is purged; trades are closed within training. Historical candles may initialize indicators, but scoring starts with fresh cash and no inherited positions.
- Shared 300-hour warmup covers all variants (including a 240-hour moving average); historical gaps reset it. No candles are filled.
- Neighbor profiles change numeric settings jointly by roughly 20%; this is a small predeclared stress test, not an exhaustive one-at-a-time or combinatorial search.
- Fees per side: 0.05%, 0.10%, 0.20%; slippage 0.05%. A further run doubles both base fee and slippage. Every scenario has a matching same-cost buy-and-hold reference.
- No scalers, target encoders, train/test shuffling or learned weights exist in these adapters. Upstream parameter tuning history remains unknown.

**Strategies passing both the 2025 and 2026 diagnostic gates: 0/10.** No robust unseen winner is established.

## Split results — held out from this fit, previously seen by the project

### 2025 validation

| Strategy | Setting selected on training | Net return | Sharpe | Max drawdown | Trades | Hold return | Gate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| ADX + moving averages | lower_20pct | -28.73% | -0.63 | 39.89% | 115 | -6.62% | fail |
| Awesome Oscillator + MACD | higher_20pct | -36.89% | -1.52 | 41.91% | 52 | -6.62% | fail |
| Bollinger + RSI | original | 11.08% | 0.48 | 34.14% | 34 | -6.62% | pass |
| CCI + money flow + momentum | original | 4.94% | 0.31 | 25.44% | 13 ⚠ | -6.62% | fail |
| EMA crossover | higher_20pct | -50.95% | -2.22 | 56.99% | 167 | -6.62% | fail |
| MACD + CCI | original | -8.94% | 0.01 | 34.76% | 1 ⚠ | -6.62% | fail |
| MACD crossover + CCI | lower_20pct | -10.73% | -0.08 | 32.05% | 7 ⚠ | -6.62% | fail |
| Quickie trend reversal | lower_20pct | -5.95% | 0.06 | 34.40% | 14 ⚠ | -6.62% | fail |
| Rockwell MACD | higher_20pct | -62.16% | -4.08 | 64.29% | 209 | -6.62% | fail |
| Simple momentum | original | -3.10% | 0.11 | 41.26% | 133 | -6.62% | fail |

⚠ Fewer than 30 trades. The diagnostic gate requires positive return, beating buy-and-hold, and at least 30 trades. Passing it is not proof of a real edge.

### January–September 2026 nominal test (not untouched)

| Strategy | Setting selected on training | Net return | Sharpe | Max drawdown | Trades | Hold return | Gate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| ADX + moving averages | lower_20pct | -29.95% | -1.02 | 48.22% | 85 | -4.88% | fail |
| Awesome Oscillator + MACD | higher_20pct | 13.59% | 0.69 | 21.02% | 34 | -4.88% | pass |
| Bollinger + RSI | original | -16.30% | -0.55 | 35.56% | 25 ⚠ | -4.88% | fail |
| CCI + money flow + momentum | original | -28.73% | -1.16 | 38.74% | 6 ⚠ | -4.88% | fail |
| EMA crossover | higher_20pct | -25.06% | -1.22 | 39.56% | 131 | -4.88% | fail |
| MACD + CCI | original | -8.34% | -0.06 | 40.31% | 1 ⚠ | -4.88% | fail |
| MACD crossover + CCI | lower_20pct | -12.61% | -0.28 | 34.00% | 4 ⚠ | -4.88% | fail |
| Quickie trend reversal | lower_20pct | -15.82% | -0.36 | 37.55% | 8 ⚠ | -4.88% | fail |
| Rockwell MACD | higher_20pct | -15.45% | -0.85 | 27.86% | 144 | -4.88% | fail |
| Simple momentum | original | -28.41% | -0.97 | 40.47% | 86 | -4.88% | fail |

⚠ Fewer than 30 trades. The diagnostic gate requires positive return, beating buy-and-hold, and at least 30 trades. Passing it is not proof of a real edge.

## Walk-forward and sensitivity findings

| Strategy | Positive walk-forward years / 3 | Beat hold years / 3 | Profitable 2026 grid cases / 9 | Beat hold 2026 cases / 9 | 2026 grid return range |
| --- | ---: | ---: | ---: | ---: | --- |
| ADX + moving averages | 2/3 | 1/3 | 0/9 | 0/9 | -42.76% to -18.56% |
| Awesome Oscillator + MACD | 2/3 | 1/3 | 3/9 | 4/9 | -23.66% to 17.52% |
| Bollinger + RSI | 1/3 | 1/3 | 0/9 | 0/9 | -24.63% to -11.05% |
| CCI + money flow + momentum | 2/3 | 1/3 | 0/9 | 0/9 | -29.58% to -5.62% |
| EMA crossover | 1/3 | 0/3 | 0/9 | 0/9 | -62.15% to -14.58% |
| MACD + CCI | 2/3 | 0/3 | 0/9 | 3/9 | -8.52% to -4.72% |
| MACD crossover + CCI | 2/3 | 1/3 | 3/9 | 3/9 | -13.30% to 22.62% |
| Quickie trend reversal | 2/3 | 1/3 | 0/9 | 0/9 | -17.16% to -9.24% |
| Rockwell MACD | 0/3 | 1/3 | 0/9 | 1/9 | -59.97% to -2.36% |
| Simple momentum | 2/3 | 1/3 | 0/9 | 0/9 | -55.39% to -8.70% |

### Fee sensitivity with training-selected parameters fixed (2026)

| Strategy | Fee 0.05% | Fee 0.10% | Fee 0.20% | Fee 0.20% + slip 0.10% |
| --- | ---: | ---: | ---: | ---: |
| ADX + moving averages | -23.73% | -29.95% | -40.90% | -45.71% |
| Awesome Oscillator + MACD | 17.52% | 13.59% | 6.12% | 2.57% |
| Bollinger + RSI | -14.18% | -16.30% | -20.38% | -22.34% |
| CCI + money flow + momentum | -28.30% | -28.73% | -29.58% | -30.00% |
| EMA crossover | -14.58% | -25.06% | -42.34% | -49.42% |
| MACD + CCI | -8.25% | -8.34% | -8.52% | -8.61% |
| MACD crossover + CCI | -12.26% | -12.61% | -13.30% | -13.65% |
| Quickie trend reversal | -15.15% | -15.82% | -17.16% | -17.82% |
| Rockwell MACD | -2.36% | -15.45% | -36.61% | -45.11% |
| Simple momentum | -21.99% | -28.41% | -39.73% | -44.69% |

Fee percentages are per side. Slippage is 0.05% except in the last column. Corresponding same-cost buy-and-hold outcomes are saved for every case in sensitivity.csv.

These nine scenarios are diagnostics, not a search for a new winner. Period-specific detailed rows and the doubled-fee/slippage cases are in sensitivity.csv.

## Failures explained simply

- **Previously seen test:** it is like seeing the exam answers before taking a practice exam. Reordering the questions does not make it a fresh exam. No untouched-test claim or unseen rank is issued.
- **Look-ahead bias:** making a trade with information from tomorrow. Prefix and mutation checks look for earlier decisions changing when tomorrow changes. No detected dependency does not guarantee every possible code path is clean.
- **Overfitting:** a rule memorizes one stretch of history but struggles later. Training-vs-later-year and nearby-setting comparisons expose this risk; they cannot prove its absence.
- **Tiny sample:** a strategy can look brilliant because it held Bitcoin through one rise. Fewer than 30 trades is flagged; more trades alone do not prove reliability.
- **Parameter fragility:** changing a few settings can turn a gain into a loss. The full range is reported rather than choosing the prettiest result.
- **Fee fragility:** frequent small gains can disappear when trading becomes more expensive.
- **Why a weak later year matters:** strong training results followed by losses can indicate overfitting or a changed market. These observations cannot distinguish those causes with certainty. Three walk-forward years are a limited sample; no formal significance or probability-of-overfitting claim is made.
- **Upstream uncertainty:** published settings may have been optimized before we obtained them. We do not know the original training data, so cannot certify historical independence.
- **Simulation limits:** the original bots' ROI/stoploss rules are omitted; cash/long all-in execution, close-based drawdown and constant slippage are simplified. No real trading performance is established.

## How to get a genuinely new test

Freeze settings and rules now, record them in Git, and paper-test later candles that were not used to build or inspect this project. Do not retune on those results or repeatedly select winners.
The 2026 diagnostic here is not used to pick a new strategy. No later price data was downloaded for this audit.

## Reproduce and inspect

Run `.venv/bin/python -m btc_lab robustness`. `protocol.json` is written before scoring; `frozen_selection.json` is written before validation/test scores.
See training_candidates.csv, walk_forward.csv, period_results.csv, sensitivity.csv, robustness_summary.csv, strategy_verdicts.csv, causality.csv, period_equity.csv.gz and per-period trade logs.
All data-derived output: Binance Vision attribution, CC BY-NC-SA 4.0 plus the [saved dataset terms](../../sources/BINANCE_DATASET_TERMS.md).
