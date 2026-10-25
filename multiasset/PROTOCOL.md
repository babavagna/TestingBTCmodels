# Multi-asset, venue-separated research protocol

The user's later clarification makes **Kalshi margin contracts the PRIMARY market**.
The 28 named assets remain authoritative. The original dashboard's observed market
catalog contains 39 contracts; preserve those 28 plus 11 explicitly identified
extras. Preserve exact tickers, contract_size, underlying_multiplier, tick_size,
fractional_trading_enabled, market_version and schedules. WTI is KXWTIFUTURE, a
dated future, not silently a perpetual or WTI spot proxy. Binance observations
are SUPPLEMENTARY EXTERNAL DATA ONLY, never Kalshi history or Kalshi validation.

Never overwrite old frozen Bitcoin data, source code or validated reports.
All new outputs use the multiasset/kalshi namespaces and input fingerprints.
Historical price data are actual provider observations. Empty API responses,
blocked requests and missing fields are distinct. No interpolation, forward-fill,
spot/perpetual splicing, midpoint-derived invented high/low, or assumed volume.
Trade OHLCV and observed bid/ask-midpoint CLOSE-ONLY data are separate streams.
Aggregated 5m/15m trade bars require every actual 1m observation; native 1h provider
bars remain native observations. Next-interval labels require adjacent bars,
never a weekend/closure/gap jump. Missing calendar slots may be closures, not
necessarily vendor errors; historical session calendars are unverified.

## Candidates and execution

Attempt the existing 100-source strategy catalog and the existing 147 disclosed
indicator+binary-readout candidates on each feasible contract/timeframe/price-basis.
These are not 247 independent economic discoveries. Preserve source licenses,
parameters and the original implementation-scope limitations. Known source-level
leakage/native-state/runtime failures stay blocked with their audited reason;
never reuse their old Bitcoin performance as a new contract test. Re-execute
supported implementations on the actual current dataset. Close-only inputs permit
only close-compatible formulas; unknown OHLCV stays missing, not synthetic.
Native stops, shorts, leverage and position-management callbacks are not reproduced.

One initial common 512-observation warmup. Signals use completed candles; fill
only at the next adjacent observed tradable bar's open. Initial capital USD 10,000.
Fee 0.10% and adverse slippage 0.05% on EACH buy and sell. For Kalshi, use quote
prices PER CONTRACT and whole contracts when fractional trading is disabled.
Never apply underlying_multiplier a second time to a price already per contract.
Final position closes on the final observed tradable candle. No short positions;
DOWN/cash signals exit long exposure. Exact historical funding/financing/rollover,
maintenance margin and historical contract-version changes must be verified or
explicitly marked missing. Missing derivative costs EXCLUDE a result from a fully
validated primary financial ranking. Measured cost-limited backtests may be shown
as exploratory, with their omissions, not passed off as complete execution proof.

First ten runnable source candidates are the initial execution checkpoint; then
continue the full catalog. Every candidate receives a terminal result or a precise
blocked/failed status. Candidate checkpoints identify dataset/source/settings/code
hashes so completed runs can be resumed without stale reuse. Numerical prefix and
changed-future checks protect selected formula paths; static confirmed leakage
exclusions remain quarantined even if a threshold hides the numerical difference.

## Chronological splits and new instruments

Kalshi contracts do not have January 2020 data merely because the underlying asset
existed. Use actual available observations. New Kalshi histories are generally
within 2026, so the old 2020–2024 fit / 2025 validation cannot be claimed here.
Default adaptive chronological partitions, after warmup, are: earliest 50% fit,
next 10% parameter selection, next 15% calibration, next 10% independent validation,
last 15% retrospective final test. Boundaries are actual timestamp boundaries;
purge labels reaching the next fit/selection boundary. Save all dates and counts.
Require at least 1,000 eligible training rows for inherited binary readouts;
insufficient inputs produce no fitted forecast, not invented scores. Source-rule
backtests can run on shorter samples but are flagged for fewer than 30 trades.

Source variants are default and supported numeric neighbors at -20%/+20%, selected
on the earlier fit/selection part only. Binary readouts use training-only scaling,
fixed ridge=0.01 and threshold 0.5; select on the dedicated selection part, then
refit on fit+selection and freeze. Walk-forward uses three expanding earlier
training/evaluation folds when sample sizes permit; otherwise state why absent.
Never tune or rank on fit/calibration data. All Jan–Sep 2026 comparisons are labelled
RETROSPECTIVE: the calendar period and published candidate families were examined
before this expansion. Upstream optimization history remains unknown.

## Three outcomes, calibration and joint estimates

For every feasible primary asset/chart, predict next close-to-close returns:
DOWN < -0.10%, STAY SIMILAR between -0.10% and +0.10% inclusive, UP > +0.10%.
Sensitivity thresholds: 0.05%, 0.10%, 0.20%, fixed across assets/timeframes.
A separate three-class regularized softmax model uses only current/past price
features. Fit its scaler/weights on the fitting segment; temperature calibration
uses only the later calibration segment. Report raw/calibrated multiclass Brier,
log loss, accuracy, balanced accuracy, class counts and reliability/ECE on the
separate validation and final segments. Insufficient class/calibration samples
block a calibrated-probability claim. High STAY accuracy is compared with the
training-majority baseline; it is not automatically directional skill.

For selected indicator agreement, count HISTORICAL JOINT outcomes where every
selected model's direction matches the query/current direction pattern. Never
multiply marginal probabilities or assume independent indicators. Use calibration
observations only to estimate that joint distribution, show its actual n and
intervals, and withhold the estimate below 100 matching observations. Evaluate
predeclared agreement groups on later data. An arbitrary user selection is an
exploratory conditional estimate, not independently validated new evidence.

## Freshness and status

Historical snapshots and current inference have different data roles. A September
snapshot is never labelled current in October. Show price as-of, model fit end,
calibration end, last successful retrieval and age. Current probabilities require
actual closed recent Kalshi candles, matching instrument/model identity and a
freshness window. Market closures/stale inputs/provider failures produce explicit
status and no CURRENT probability, retaining historical results separately.
No service has placed real orders. External Perpetual Edge deployment is separate
from this repository's Streamlit interface and needs its own verified integration.
