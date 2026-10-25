# Source of the accuracy table — handoff for Perpetual Edge

**There is no TradingView indicator link or Pine Script that produced this table.**
The results come from the Python formulas and frozen trained models in
`babavagna/TestingBTCmodels`. An alert from a similarly named TradingView indicator
does not reproduce these forecasts. A TradingView/webhook connection for these
models has not been installed in this repository.

The links below pin the exact existing source version used by the sortable table:

- [Indicator formulas and feature construction](https://github.com/babavagna/TestingBTCmodels/blob/1ccf89c80d315965945e894d3ba81cb3f7ec9622/indicator_lab/features.py)
- [Trained-model probability calculation](https://github.com/babavagna/TestingBTCmodels/blob/1ccf89c80d315965945e894d3ba81cb3f7ec9622/indicator_lab/model.py)
- [Forecast eligibility and historical execution](https://github.com/babavagna/TestingBTCmodels/blob/1ccf89c80d315965945e894d3ba81cb3f7ec9622/indicator_lab/runner.py)
- [The 52 requested indicator IDs, including original repeated entries](https://github.com/babavagna/TestingBTCmodels/blob/1ccf89c80d315965945e894d3ba81cb3f7ec9622/sources/selected_directional/request_ids.txt)
- [Executed UP/DOWN results, counts and scope](https://github.com/babavagna/TestingBTCmodels/blob/1ccf89c80d315965945e894d3ba81cb3f7ec9622/reports/selected_directional/REPORT.md)

## Exact UP/DOWN rule

After each completed candle, calculate the selected indicator's feature vector
using `indicator_lab.features.features`. Use that indicator and timeframe's saved
training mean, standard deviation, retained-column mask and model coefficients.
Standardize with those saved values, clip standardized inputs to [-10, 10], then
apply the saved logistic model through `indicator_lab.model.predict`.

- **UP:** finite predicted UP probability `p_up >= 0.5`.
- **DOWN:** finite predicted UP probability `p_up < 0.5`.
- **No forecast:** incomplete initial warmup or non-finite required features.
  Missing probabilities must not be converted into DOWN.

The initial 2,048 observed candles are excluded. This is a minimum warmup rule,
not proof that replaying only the latest 2,048 candles reproduces every indicator's
historical state exactly. Preserve/replay the matching history and validate outputs.

This is **not** a rule such as “positive pattern code = UP,” “RSI below 30 = UP,”
or a generic TradingView crossover alert. Most of the requested indicators have
no standalone directional forecast in this experiment.

## Frozen settings and model coefficients

Use the correct file for the chart timeframe:

| Chart | Frozen models, settings and scalers |
|---|---|
| 5 minutes | [frozen_5m.json](https://github.com/babavagna/TestingBTCmodels/blob/1ccf89c80d315965945e894d3ba81cb3f7ec9622/reports/predictions/frozen_5m.json) |
| 15 minutes | [frozen_15m.json](https://github.com/babavagna/TestingBTCmodels/blob/1ccf89c80d315965945e894d3ba81cb3f7ec9622/reports/predictions/frozen_15m.json) |
| 1 hour | [frozen_60m.json](https://github.com/babavagna/TestingBTCmodels/blob/1ccf89c80d315965945e894d3ba81cb3f7ec9622/reports/predictions/frozen_60m.json) |

Within each JSON file, select `models[INDICATOR_ID]`, read `selected_profile`,
then use that entry under `profiles`. Its `parameters` contains indicator settings;
its `model` contains `mean`, `scale`, `keep` and `weights`. Do not refit, substitute
default settings or choose a different profile from the 2026 scores.

For example, EFI uses period **10 on 5m**, **13 on 15m**, and **10 on 1h**, plus
different fitted coefficients/scalers for each timeframe. A default EFI chart
alone is therefore insufficient to reproduce the table.

## Price and timing contract

- Binance **spot BTC/USDT**, UTC, closed candles only. The study built 15m and 1h
  candles from complete groups of the same Binance 5m observations.
- A feature candle opening at time `t` becomes available at `t + timeframe`.
  Predict whether the next candle's closing price, available at
  `t + 2 × timeframe`, is above or below the feature candle's close.
- This is next **close-to-close direction**, which can differ from the next
  candle's green/red body. Equal next closes are unscored ties in the historical
  accuracy calculation, not grounds to suppress a forecast in advance.
- The principal table scores every eligible candle. The separate Pattern Events
  table restricts the same forecasts to actual pattern occurrences. Neither is
  an independently authored native TradingView alert strategy.
- CORREL and BETA use BTC high/low inputs, not another asset or market benchmark.

## Connecting it to a dashboard

To reproduce the table's signal source, the receiving application must either run
the existing Python inference with matching data/state, or use a separately
implemented Pine port that has first been checked against the saved model outputs.
TradingView can transport alerts, but it does not automatically supply these models.
No native Pine port or TradingView parity verification currently exists for this
complete forecasting pipeline.

The historical UP/DOWN accuracy percentage is an aggregate evaluation score,
**not the probability of an individual incoming signal**. A dashboard must not
substitute that percentage for the model's current `p_up`, or assume that current
probabilities are calibrated. No Perpetual Edge score-combination rule is defined
by this backtesting repository.

The models were trained on 2020–2024, with window selection using 2025. The user
chose January–September 2026 as a retrospective comparison; these dates were
already examined. The published accuracies are not verified live TradingView
performance or genuinely untouched future results. The costed portfolio uses
DOWN to hold cash, not to open a short position.
