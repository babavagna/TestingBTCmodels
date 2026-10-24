# Requested UP/DOWN study — fixed before this re-execution

The user supplied 90 entries with 52 distinct IDs, including 35 candlestick
patterns. Preserve all input rows and duplicate counts; do not pretend repeated
names are separate independent strategies. Evaluate each distinct ID on Binance
spot BTCUSDT 5m, 15m and 60m observations, predicting the next close relative to the
current close, once the current candle is complete. Dates and labels remain UTC.

Reuse the existing verified price files and the FROZEN 2020–2024-trained models.
Window profiles were previously chosen using 2025 only. Regenerate indicator
features, re-run every frozen model and verify its probabilities and decisions
against the saved forecasts. Recalculate scores and identical-cost portfolios.
This is actual model re-execution, not a new refit or an independent future test.
January–September 2026 remains RETROSPECTIVE as the user requested. The subset was
requested after the earlier results were available: selection creates additional
bias. Do not reset statistical significance to a smaller 52-indicator universe;
retain the original whole-universe Holm results only as historical diagnostics.

## Exactly what UP/DOWN accuracy means

- UP accuracy (precision): correct UP guesses / all UP guesses.
- DOWN accuracy (precision): correct DOWN guesses / all DOWN guesses.
- Also report UP moves found (recall), DOWN moves found (recall), overall accuracy,
  balanced accuracy, confusion counts, actual/predicted class shares and coverage.
- A model that never guesses DOWN has DOWN accuracy N/A, not zero or 100%.
- Flag fewer than 100 guesses in either direction. This threshold is only a
  warning rule, not a claim that 100 guesses prove reliability. Preserve the
  earlier rare-pattern flag (fewer than 200 nonzero training occurrences).
- Wilson 95% intervals are DESCRIPTIVE and assume independent observations.
  Financial observations can be correlated. No new UP/DOWN significance or
  independent future-performance claim is made from these intervals.
- Equal next closes are unscored ties. No forecast or trade is suppressed using
  a future flat label. Missing target candles never receive invented answers.

## Every candle versus actual pattern occurrences

The main directional tables score the model on every eligible candle, including
candles on which a pattern did not appear. Separately score the SAME frozen
model on candles where a candlestick pattern's current output is nonzero. Show
raw occurrences, scored occurrences, flat targets and missing/invalid exclusions.
Zero occurrences means no event-only accuracy, not a fabricated 0% or 50% result.
Flag fewer than 100 scored occurrences. Do not rank pattern-event results against
all-candle results or pretend different pattern coverage is identical.

A positive TA-Lib pattern code does NOT always mean bullish; Doji codes in
particular can simply mark a shape. Never assign UP automatically from that code.
The prediction comes from the disclosed trained readout in both tables. The
model was trained on all eligible training candles, not refitted only on events.
These are not standalone native pattern forecasts.

ATR, NATR, TRANGE, variance, standard deviation and similar indicators measure
volatility or activity; they have no standalone UP/DOWN forecast in this study.
Their direction comes from the same trained logistic model used previously.
CORREL and BETA retain TA-Lib's original high/low input series: they do not measure
Bitcoin's correlation or beta against another asset. Market-relative beta was
not evaluated because no reference asset was specified. Native TradingView
matching remains UNVERIFIED for every formula.

## Validation and integrity

Recheck the frozen code and price manifest hashes and run numerical prefix and
changed-future checks for each selected formula profile on each timeframe.
Cross-check all regenerated probabilities/decisions and 2025/2026 accuracies with
the earlier artifacts. Re-execute available default-profile expanding walk-forward
models on 2022/2023/2024. Failed early fits remain failed, with their actual reasons.
Do not change model coefficients, thresholds or profiles after seeing new scores.

Fees and slippage affect portfolio results, not directional accuracy: 0.1% fee
and adverse 0.05% slippage on EVERY buy and sell, 10,000 USDT per period,
next-adjacent-open fills, long/cash, final-close exit and identical-cost buy/hold.
DOWN forecasts mean lower next closes; the portfolio holds cash rather than
shorting Bitcoin. The idealized account omits minimum order sizes, lot rounding,
latency and market impact. Do not interpret high accuracy as profitable trading.

Freeze a run-input manifest with this protocol, new scoring code, original source
IDs, old frozen models and verified price hashes. Save results, actual failures,
workbook, plain-language definitions and execution/test evidence to GitHub.
