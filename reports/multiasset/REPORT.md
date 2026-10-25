# Kalshi multi-asset research

Generated 2026-10-25T19:51:39.457678+00:00. These are executed retrospective studies, not independently validated live trading models.

{
  "asset_timeframes": 117,
  "candidate_case_records": 7163,
  "completed_trade_replays": 1844,
  "completed_quote_forecasters": 546,
  "fully_validated_financial_strategies": 0,
  "failed_or_blocked_candidates": 4773,
  "calibrated_main_models": 21
}

The requested 28 names expand to 39 actual Kalshi contracts after inspecting the original dashboard. The asset headings in the request had inconsistent category counts; the named assets and the additional original contracts are preserved.

Kalshi per-contract prices are primary. Binance data is supplementary. Derivative funding/financing, rollover, historical liquidation rules and historical session/specification changes are unverified, so **there is no fully validated financial winner or top 10**.

Trade replays project published entries/exits into unleveraged long/cash decisions. They do not reproduce native stops, targets, shorts or leverage. Bid/ask midpoint close-only models are listed separately and never receive a trading return.

Target dates are January 2020 through September 2026. Actual retrieved Kalshi contract observations start in 2026. Short histories use chronological fit, selection, calibration, validation and retrospective-test stages; no unavailable older prices are invented. All exact scoring dates appear in the CSV and workbook.

September model snapshots are historical in October. No current probability is claimed without a fresh separate inference buffer. Individual binary accuracy excludes exact flats; the three-class model includes a STAY band of ±0.10%.

## All assets and chart timeframes

| Asset | Chart | Traded bars | Quote closes | Completed trade methods | Completed quote models | Source status |
|---|---:|---:|---:|---:|---:|---|
| AAPL | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| AAPL | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| AAPL | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| AAVE | 5m | 118 | 9327 | 0 | 42 | HISTORY_READY |
| AAVE | 15m | 0 | 3039 | 0 | 42 | HISTORY_READY |
| AAVE | 60m | 792 | 794 | 83 | 0 | HISTORY_READY |
| ADA | 5m | 249 | 8340 | 0 | 42 | HISTORY_READY |
| ADA | 15m | 1 | 2641 | 0 | 42 | HISTORY_READY |
| ADA | 60m | 720 | 721 | 83 | 0 | HISTORY_READY |
| ALUMINUM | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| ALUMINUM | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| ALUMINUM | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| BCH | 5m | 4492 | 24453 | 220 | 42 | PARTIAL_HISTORY |
| BCH | 15m | 623 | 7357 | 0 | 42 | PARTIAL_HISTORY |
| BCH | 60m | 2690 | 2694 | 214 | 42 | PARTIAL_HISTORY |
| BNB | 5m | 206 | 6936 | 0 | 42 | HISTORY_READY |
| BNB | 15m | 2 | 1789 | 0 | 0 | HISTORY_READY |
| BNB | 60m | 721 | 720 | 83 | 0 | HISTORY_READY |
| BTC | 5m | 27654 | 28000 | 222 | 42 | PARTIAL_HISTORY |
| BTC | 15m | 9152 | 9330 | 221 | 42 | PARTIAL_HISTORY |
| BTC | 60m | 2836 | 2848 | 211 | 42 | PARTIAL_HISTORY |
| COPPER | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| COPPER | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| COPPER | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| COST | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| COST | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| COST | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| DOGE | 5m | 0 | 0 | 0 | 0 | PARTIAL_HISTORY |
| DOGE | 15m | 0 | 0 | 0 | 0 | PARTIAL_HISTORY |
| DOGE | 60m | 2689 | 2691 | 213 | 42 | PARTIAL_HISTORY |
| ETH | 5m | 0 | 0 | 0 | 0 | PARTIAL_HISTORY |
| ETH | 15m | 0 | 0 | 0 | 0 | PARTIAL_HISTORY |
| ETH | 60m | 2834 | 2849 | 211 | 42 | PARTIAL_HISTORY |
| GOLD | 5m | 0 | 0 | 0 | 0 | PARTIAL_HISTORY |
| GOLD | 15m | 0 | 0 | 0 | 0 | PARTIAL_HISTORY |
| GOLD | 60m | 487 | 489 | 0 | 0 | PARTIAL_HISTORY |
| GOOGL | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| GOOGL | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| GOOGL | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| HYPE | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| HYPE | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| HYPE | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| KPEPE | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| KPEPE | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| KPEPE | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| KSHIB | 5m | 0 | 0 | 0 | 0 | PARTIAL_HISTORY |
| KSHIB | 15m | 0 | 0 | 0 | 0 | PARTIAL_HISTORY |
| KSHIB | 60m | 708 | 714 | 83 | 0 | PARTIAL_HISTORY |
| LINK | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| LINK | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| LINK | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| LTC | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| LTC | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| LTC | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| META | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| META | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| META | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| MU | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| MU | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| MU | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| NEAR | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| NEAR | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| NEAR | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| NVDA | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| NVDA | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| NVDA | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| PALLADIUM | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| PALLADIUM | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| PALLADIUM | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| PLATINUM | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| PLATINUM | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| PLATINUM | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| PLTR | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| PLTR | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| PLTR | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| SILVER | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| SILVER | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| SILVER | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| SOL | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| SOL | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| SOL | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| SUI | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| SUI | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| SUI | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| TSLA | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| TSLA | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| TSLA | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| UNI | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| UNI | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| UNI | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| US2000 | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| US2000 | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| US2000 | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| US500 | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| US500 | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| US500 | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| USTECH100 | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| USTECH100 | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| USTECH100 | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| VVV | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| VVV | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| VVV | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| WLD | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| WLD | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| WLD | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| WTI | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| WTI | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| WTI | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| XOM | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| XOM | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| XOM | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| XRP | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| XRP | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| XRP | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| ZEC | 5m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| ZEC | 15m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |
| ZEC | 60m | 0 | 0 | 0 | 0 | RETRIEVAL_FAILED |

Exact source failures, missing fields, insufficient sample sizes and quarantined code appear in `coverage.csv`, `failed_tests.csv`, the workbook and the per-case JSON checkpoints. Failed cases have no invented metrics.

## Access and reproduce

- Open the repository dashboard with `bash run_dashboard.sh`; choose the Multi-asset timeframe and the contract tab. Existing BTC studies remain available below.
- Download `KALSHI_MULTI_ASSET_RESEARCH.xlsx` with GitHub’s **Download raw file** button; GitHub itself does not preview workbooks.
- Resume collection: `.venv/bin/python -m multiasset.kalshi --workers 3 --max-windows 240`.
- Resume research: `OPENBLAS_NUM_THREADS=1 .venv/bin/python -m multiasset.pipeline --workers 4`.
- Export actual checkpoints: `.venv/bin/python -m scripts.export_multiasset`.
- Software tests: `.venv/bin/python -m pytest -q`.

The existing separate Perpetual Edge public Site was inspected read-only. New tabs belong to this repository’s Streamlit dashboard; no external Site deployment is claimed.

## Metrics in plain language

**Quote-only inputs:** Observed bid/ask midpoint closes are marked separately. They support only formulas that need closes. No artificial open/high/low/volume is created and no financial backtest is run on quote-only data.

**Net return:** How much the starting money changed after modeled fees/slippage. +20% turns 100 into 120. Missing derivative costs can change this result.

**Sharpe:** Average daily gain compared with how bumpy daily gains are, scaled to one year (365 crypto, 252 other markets). A high value from a short sample can be misleading.

**Sortino:** Like Sharpe, but counts only downward bumps as risk. N/A when there are no downward observations to divide by.

**Maximum drawdown:** Largest fall from an earlier account high. A 30% drawdown means 100 fell to 70. Only observed candle closes are measured.

**Profit factor:** Money from winning trades divided by money lost on losing trades. Above 1 means gains outweighed losses. N/A if there are no losing-trade dollars.

**Trade win rate:** Share of completed buy/sell pairs that made money after costs. A big loss can outweigh many small wins. Fewer than 30 trades is flagged.

**Buy and hold:** Buy once and sell at the same scoring end, with the same costs and whole-contract sizing. This is the comparison yardstick.

**Directional accuracy:** Correct next-candle UP/DOWN forecasts divided by forecasts scored. Exact flat closes are excluded in binary scores. Trading entries/exits are not forecasts; their accuracy is N/A.

**UP/DOWN precision:** UP precision: among UP guesses, how many were right? DOWN precision: among DOWN guesses, how many were right? Separate numeric columns let you sort each.

**Recall:** Of all actual UP moves, how many did the model find? DOWN recall asks the same question for falls. Precision and recall have different denominators.

**STAY SIMILAR:** Three-class model uses next-close movement within −0.10% to +0.10%. Threshold sensitivity repeats ±0.05% and ±0.20%. A quiet market can make always guessing STAY appear accurate; compare the baseline and balanced accuracy.

**Baseline:** The most frequent class in training predicts every held-out candle. Compare on the same eligible rows. High raw accuracy alone does not establish useful prediction.

**Confidence interval:** An uncertainty range around a measured percentage. Wilson ranges are descriptive: nearby candles can be correlated, and trying many models creates lucky winners.

**Brier/log loss:** Scores for probability quality; smaller is better. Log loss strongly penalizes confident wrong predictions. Three-class Brier sums squared errors across all three classes.

**Calibration:** A model that says 60% should succeed about 60 times out of 100 similar cases. Temperature is fitted only on a separate earlier calibration segment. Calibration is not guaranteed in later markets.

**Joint outcomes:** When selected indicators agree, count what actually happened after their joint historical configuration. Do not multiply individual accuracy percentages or treat correlated indicators as independent votes.

**Freshness:** September historical snapshots are not current in October. Current probability cells remain N/A until a separate recent buffer is retrieved and a fresh calibrated model output is checked.

**Walk forward:** Repeatedly learn on earlier observations, then score later ones. Small folds can fail for lack of history; failures remain visible.

**Sensitivity:** Fixed parameter neighbors are selected before held-out scoring. Fee stresses halve/double fees and double fees plus slippage. Parameter selection records and earlier-fold results are retained.

**Cheating checks:** Past-prefix and future-mutation checks look for later prices changing earlier signals. Known leaking original sources remain quarantined. Finite checks cannot prove the absence of every possible bias.

**Duplicates:** Exact sampled training signal duplicates and very high correlations are recorded. Repeated signals are not counted as independent evidence.

**N/A:** Missing, undefined, insufficient or unverified. N/A is never silently converted to a real zero.

**Workbook access:** GitHub does not preview Excel. Open the workbook page, choose Download raw file, then open the downloaded .xlsx in Excel or LibreOffice. Do not save a GitHub HTML page with an Excel extension.

**Original dashboard:** This repository adds tabs to its existing Streamlit lab. The separate hosted Perpetual Edge Site project was inspected read-only; it was not deployed or modified by this task.

