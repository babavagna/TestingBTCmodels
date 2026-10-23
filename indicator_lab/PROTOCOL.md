# Frozen indicator prediction protocol

Registered before model fitting and the new 2026 accuracy calculations. This is
**retrospective research**, at the user's request: 2025 and January–September 2026
were already examined in the earlier strategy project. A replay cannot erase that
exposure. No claim of genuinely untouched future evidence is made.

## Coverage

“All TradingView indicators” is not an enumerable, accessible open-source universe.
It includes changing community, protected, paid, private and invite-only scripts.
The TradingView website is blocked in this execution environment. This study is a
**reproducible indicator formula benchmark**, not an exhaustive TradingView ranking.

1. Audit every original script in the pinned 210-file everget public Pine corpus.
   Attempt each unchanged on 1,000 real hourly candles in PineTS 0.13.0. A
   compatibility probe is NOT a forecast test. Save failures and probe results.
2. Execute the catalog from `features.catalog()`: TA-Lib cycle, momentum, overlap,
   statistics, volatility, volume and candlestick functions, excluding seven
   duplicate or extra-input functions, plus disclosed project formulas. Candlestick
   patterns are labeled separately. Some functions are related parameterizations;
   they are not independent economic discoveries.
3. Formula-engine agreement with native TradingView is UNVERIFIED throughout.
   Identically named formulas, initialization, defaults and exchange data may differ.
   The evaluated object is **indicator + our trained logistic readout**, not an
   author's native forecasting system. Published formulas may have been optimized
   on past Bitcoin data before we obtained them; that history is unknown.

## Prices and timing

- Official Binance spot BTCUSDT 5-minute monthly archives, January 2020–September
  2026, individually SHA-256 checked against published checksums. Aggregate the
  same observations into 15-minute and 60-minute candles; discard incomplete bins.
- UTC throughout. No invented prices and no filling gaps. Indicators count observed
  bars, so their lookbacks can span more clock time around missing data.
- At the END of candle t, predict whether close(t+1) is higher than close(t).
  The target is next **close-to-close direction**, not necessarily next candle's
  green/red body. Equal closes are unscored ties; their forecasts still exist and
  may drive the portfolio. Do not use a future flat label to suppress a trade.
- Only adjacent complete candles get a direction label. Shared initial burn-in:
  2,048 observed candles per timeframe. Scored coverage is reported per model;
  exclude a model if feature completeness after burn-in is below 99.9%.
- Training 2020–2024; validation 2025; retrospective test January–September 2026.
  Scoring requires target close <= end; fitting strictly purges target close >= end.
  The first eligible test forecast is the December 31 candle ending at January 1,
  using only information available at that boundary. No fit sees its target.

## Forecast construction and selection

Each indicator output is normalized using only current/past prices or volumes
where units require it. Provide its level, one-bar change, previous level, and
three-bar lag to the same logistic regression. No other indicator is added.
Price overlays use distance from current close. Full formulas are in `features.py`.

Fit mean/standard deviation ONLY on each fit's training rows; discard constant
columns. Clip standardized values to [-10,10]. Penalized mean log loss with
ridge=0.01 on coefficients, intercept unpenalized, L-BFGS-B with fixed tolerances.
Use ALL eligible training rows, no random split. A constant-only indicator fails
rather than receiving a fabricated informative forecast. Predict UP at probability
>= 0.5 on every eligible feature row; no confidence threshold cherry-picking.

Predeclare default, 0.8x and 1.2x integer window lengths (minimum 2). Leave other
parameters unchanged. Deduplicate identical profiles. Fit each on 2020–2024, select
highest 2025 validation accuracy; exact ties favor default, then short, then long.
Save models, settings, code hashes and the choice BEFORE 2026 labels are scored.
No choice uses 2026 performance. Scores for the two unselected profiles are
sensitivity diagnostics, not alternative winners.

Walk-forward: default profile only, expanding fits through 2021/2022/2023 and
separate evaluations on 2022/2023/2024. These folds stay within the training era.
Never choose a fold's settings using later validation or retrospective test scores.

## Integrity checks

For every distinct formula profile, regenerate 512/1,024/2,048-bar prefixes and
compare all previous numerical feature values with a 3,072-bar run. Change prices
and volume strictly after bar 2,048 and verify earlier outputs do not change.
Compare with tolerance rtol=1e-7, atol=1e-9, equal_nan=True; a failure quarantines
that indicator/timeframe. These checks cover selected paths and cutoffs, not every
possible bug. Tests include a deliberately cheating negative control and exact
hand-calculated metrics, timing, missing data, cost and selection cases.

## Accuracy and evidence

Report accuracy, balanced accuracy, up precision/recall, MCC, Brier, log loss and
confusion counts; distinguish these from trade win rate. Baselines: always up,
always down, training-majority direction, and previous-candle direction, all on the
same labels. Save complete probabilities and actual labels for scored periods.

Rank by 2026 retrospective accuracy within each timeframe, ID breaks exact ties.
These ranks describe this dataset; selecting a winner creates further selection
bias. Wilson intervals assume independent observations and are descriptive only.
For baseline accuracy lift, use paired 7-day moving-block bootstrap (2,000 draws,
fixed seed) and a daily Newey–West standard error (lags 1–7). Approximate two-sided
normal p-values receive Holm correction across ALL successful indicator/timeframe
final comparisons, including patterns. This does not correct unobserved earlier
research or every possible modeling choice.

A **retrospective validation gate**, not proof of independent OOS success, requires
positive accuracy lift over the training-majority baseline in BOTH 2025 and 2026,
positive lower block-CI bound in 2026, Holm p<0.05, positive mean walk-forward lift,
>=1,000 scored 2026 predictions, and no rare-training-event flag. Flag patterns
with fewer than 200 nonzero training occurrences and all models with fewer than
1,000 final forecasts. Report financial gates separately.

## Trading diagnostics and stress

Accuracy is before costs. Separate long/cash simulations: start 10,000 USDT for
each period; UP means long, DOWN means cash; maintain consecutive long holdings.
Trade at the next adjacent observed candle open after the forecast. A missing
forecast holds the existing position. Never trade across a missing candle gap;
mark held Bitcoin using actual observed closes. Sell any final position at the
last actual close. No shorts, borrowing, stops or leverage.

Fee 0.1% AND slippage 0.05% on EVERY buy and sell. Fees reduce proceeds/increase
purchase cost; slippage worsens purchase/sale prices. Buy-and-hold receives identical
entry/exit costs over the same period. Stress half fee, double fee and double fee
plus double slippage, with forecasts unchanged. Net return, daily-return annualized
Sharpe (365 days, risk-free=0), maximum observed-close drawdown, net-trade profit
factor, net-trade win rate, trades and costed buy-and-hold are reported. Flat/no-loss
undefined ratios remain N/A, never infinity or zero. Flag fewer than 30 trades.
A financial gate requires positive net return, beating buy-and-hold and >=30 trades
in both 2025 and 2026. High prediction accuracy need not imply profitable trading.
