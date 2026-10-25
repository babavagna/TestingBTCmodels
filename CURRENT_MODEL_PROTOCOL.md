# Current Kalshi probabilities and frozen historical tests

The September backtests remain frozen under `multiasset/PROTOCOL.md`. Current
predictions use a separate recent-price buffer and separate model files. Updating
a current model never changes a September score or its saved prices.

For each asset/timeframe/price basis with a fingerprinted historical input:

1. Retrieve actual recent Kalshi contract observations. Hourly prices remain
   native hourly candles; 5m/15m use complete groups of actual 1m observations.
   Quotes remain close-only. Binance is never substituted.
2. Join the recent observations to the fingerprinted historical input for feature
   warmup. Keep the recent source separately, with source requests and fingerprints.
3. Use valid adjacent next-candle targets from the preceding 30 days: first 60%
   train a new three-class model, next 15% calibrate temperature, final 25% provide
   retrospective diagnostics. Purge earlier labels crossing the next stage.
   The threshold stays fixed at ±0.10%; there is no tuning on diagnostic scores.
   Current calibration can become feasible after additional October data even
   when the frozen September sample was too short; those results stay separate.
4. Require 500 recent eligible targets, at least 256 fitting targets and adequate
   support for every outcome, plus at least 100 calibration cases. Otherwise show
   the exact missing-evidence reason and no current probability.
5. Forecast only from the latest completed primary candle. Never replace a missing
   latest feature with a convenient earlier candle. Require age below one chart
   interval: the forecast expires as soon as its next-candle target closes.
   Reject future timestamps and already-closed targets.
6. Display training/calibration cutoffs, the price as-of time and recent diagnostic
   accuracy against its baseline. These are not independently untouched results.
   Store the new coefficients and their fingerprint separately from frozen models.

Historical binary indicator readouts remain frozen for the joint-agreement query.
Their current indicator values are calculated on recent prices, but their weights
and parameter choices remain the same as in their historical joint-calibration
cache. This preserves the meaning of the earlier empirical joint configurations.
Their agreement is not independent evidence and is not multiplied into a score.
Arbitrary selections are exploratory. `scripts/joint_multiasset.py` separately
replays three fixed illustrative groups on later held-out data; those groups were
specified after earlier historical results existed, so no pre-registration claim
is made.

The dashboard rechecks forecast age and input identity on every display. Static
Excel/CSV files contain snapshots current only at their recorded export/as-of
time. They do not become a live feed when opened later. Scheduled workflows and
the dashboard's refresh button retry retrieval; provider/network failures remain
visible and never create replacement prices or percentages.

`scripts/sensitivity_multiasset_indicators.py` refits
each successfully fitted fixed parameter neighbor using the same earlier training
rows and then scores validation/final periods. It does not choose a new winner
from those scores. Source-rule parameter/fee stress tests are already stored in
each original-source replay. All derivative financial results still omit the
explicitly listed unverified costs and cannot enter a fully validated ranking.
