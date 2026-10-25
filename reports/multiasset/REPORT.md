# Kalshi multi-asset research

Generated 2026-10-25T21:36:10.890896+00:00. These are executed retrospective studies, not independently validated live trading models.

{
  "asset_timeframes": 117,
  "candidate_case_records": 25441,
  "completed_trade_replays": 7104,
  "completed_quote_forecasters": 2016,
  "unique_executed_source_strategies": 83,
  "unique_executed_indicator_readouts": 146,
  "fully_validated_financial_strategies": 0,
  "failed_or_blocked_candidates": 16321,
  "calibrated_main_models": 89
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
| BCH | 5m | 4771 | 30132 | 220 | 42 | HISTORY_READY |
| BCH | 15m | 645 | 9246 | 0 | 42 | HISTORY_READY |
| BCH | 60m | 2690 | 2694 | 214 | 42 | HISTORY_READY |
| BNB | 5m | 206 | 6936 | 0 | 42 | HISTORY_READY |
| BNB | 15m | 2 | 1789 | 0 | 0 | HISTORY_READY |
| BNB | 60m | 721 | 720 | 83 | 0 | HISTORY_READY |
| BTC | 5m | 33625 | 33973 | 222 | 42 | HISTORY_READY |
| BTC | 15m | 11141 | 11321 | 220 | 42 | HISTORY_READY |
| BTC | 60m | 2836 | 2848 | 211 | 42 | HISTORY_READY |
| COPPER | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| COPPER | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| COPPER | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| COST | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| COST | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| COST | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| DOGE | 5m | 5220 | 30824 | 222 | 42 | HISTORY_READY |
| DOGE | 15m | 885 | 9706 | 83 | 42 | HISTORY_READY |
| DOGE | 60m | 2689 | 2691 | 213 | 42 | HISTORY_READY |
| ETH | 5m | 31953 | 33950 | 222 | 42 | HISTORY_READY |
| ETH | 15m | 10125 | 11302 | 220 | 42 | HISTORY_READY |
| ETH | 60m | 2834 | 2849 | 211 | 42 | HISTORY_READY |
| GOLD | 5m | 5312 | 5616 | 221 | 42 | HISTORY_READY |
| GOLD | 15m | 1634 | 1809 | 83 | 0 | HISTORY_READY |
| GOLD | 60m | 487 | 489 | 0 | 0 | HISTORY_READY |
| GOOGL | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| GOOGL | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| GOOGL | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| HYPE | 5m | 16435 | 26085 | 223 | 42 | PARTIAL_HISTORY |
| HYPE | 15m | 4084 | 8640 | 218 | 42 | PARTIAL_HISTORY |
| HYPE | 60m | 2715 | 2726 | 211 | 42 | PARTIAL_HISTORY |
| KPEPE | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| KPEPE | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| KPEPE | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| KSHIB | 5m | 2781 | 25601 | 83 | 42 | PARTIAL_HISTORY |
| KSHIB | 15m | 309 | 8230 | 0 | 42 | PARTIAL_HISTORY |
| KSHIB | 60m | 2685 | 2696 | 215 | 42 | PARTIAL_HISTORY |
| LINK | 5m | 2485 | 25036 | 83 | 42 | PARTIAL_HISTORY |
| LINK | 15m | 231 | 7827 | 0 | 42 | PARTIAL_HISTORY |
| LINK | 60m | 2707 | 2714 | 216 | 42 | PARTIAL_HISTORY |
| LTC | 5m | 4149 | 24119 | 83 | 42 | PARTIAL_HISTORY |
| LTC | 15m | 402 | 7286 | 0 | 42 | PARTIAL_HISTORY |
| LTC | 60m | 2688 | 2700 | 218 | 42 | PARTIAL_HISTORY |
| META | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| META | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| META | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| MU | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| MU | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| MU | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| NEAR | 5m | 8094 | 24723 | 226 | 42 | PARTIAL_HISTORY |
| NEAR | 15m | 1042 | 7649 | 83 | 42 | PARTIAL_HISTORY |
| NEAR | 60m | 2352 | 2359 | 83 | 0 | PARTIAL_HISTORY |
| NVDA | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| NVDA | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| NVDA | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| PALLADIUM | 5m | 65 | 1459 | 0 | 0 | HISTORY_READY |
| PALLADIUM | 15m | 2 | 458 | 0 | 0 | HISTORY_READY |
| PALLADIUM | 60m | 129 | 129 | 0 | 0 | HISTORY_READY |
| PLATINUM | 5m | 136 | 1482 | 0 | 0 | HISTORY_READY |
| PLATINUM | 15m | 3 | 482 | 0 | 0 | HISTORY_READY |
| PLATINUM | 60m | 128 | 131 | 0 | 0 | HISTORY_READY |
| PLTR | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| PLTR | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| PLTR | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| SILVER | 5m | 3330 | 5134 | 222 | 42 | HISTORY_READY |
| SILVER | 15m | 718 | 1556 | 83 | 0 | HISTORY_READY |
| SILVER | 60m | 488 | 487 | 0 | 0 | HISTORY_READY |
| SOL | 5m | 9713 | 26857 | 227 | 42 | PARTIAL_HISTORY |
| SOL | 15m | 1866 | 8679 | 83 | 42 | PARTIAL_HISTORY |
| SOL | 60m | 2831 | 2846 | 218 | 42 | PARTIAL_HISTORY |
| SUI | 5m | 5183 | 25693 | 219 | 42 | PARTIAL_HISTORY |
| SUI | 15m | 679 | 8308 | 0 | 42 | PARTIAL_HISTORY |
| SUI | 60m | 2689 | 2697 | 217 | 42 | PARTIAL_HISTORY |
| TSLA | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| TSLA | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| TSLA | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| UNI | 5m | 0 | 70 | 0 | 0 | HISTORY_READY |
| UNI | 15m | 0 | 19 | 0 | 0 | HISTORY_READY |
| UNI | 60m | 9 | 10 | 0 | 0 | HISTORY_READY |
| US2000 | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| US2000 | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| US2000 | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| US500 | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| US500 | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| US500 | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| USTECH100 | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| USTECH100 | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| USTECH100 | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| VVV | 5m | 714 | 9397 | 0 | 42 | HISTORY_READY |
| VVV | 15m | 65 | 3101 | 0 | 42 | HISTORY_READY |
| VVV | 60m | 794 | 794 | 83 | 0 | HISTORY_READY |
| WLD | 5m | 453 | 9334 | 0 | 42 | HISTORY_READY |
| WLD | 15m | 24 | 3054 | 0 | 42 | HISTORY_READY |
| WLD | 60m | 788 | 791 | 83 | 0 | HISTORY_READY |
| WTI | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| WTI | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| WTI | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| XOM | 5m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| XOM | 15m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| XOM | 60m | 0 | 0 | 0 | 0 | NO_OBSERVATIONS_IN_REQUESTED_PERIOD |
| XRP | 5m | 10287 | 26580 | 225 | 42 | PARTIAL_HISTORY |
| XRP | 15m | 1892 | 8490 | 83 | 42 | PARTIAL_HISTORY |
| XRP | 60m | 2828 | 2848 | 217 | 42 | PARTIAL_HISTORY |
| ZEC | 5m | 7954 | 26174 | 225 | 42 | PARTIAL_HISTORY |
| ZEC | 15m | 1144 | 8721 | 83 | 42 | PARTIAL_HISTORY |
| ZEC | 60m | 2352 | 2358 | 83 | 0 | PARTIAL_HISTORY |

Exact source failures, missing fields, insufficient sample sizes and quarantined code appear in `coverage.csv`, `failed_tests.csv`, the workbook and the per-case JSON checkpoints. Failed cases have no invented metrics.

## Actual three-outcome prediction results

The following are held-out chronological retrospective scores of the calibrated ±0.10% STAY models. They are separate from binary indicator accuracy and trade win rate. Price bases are never pooled. Snapshot probabilities are historical, not current.

| Asset | Chart | Price basis | Forecasts | Accuracy | Training-majority baseline | Balanced accuracy | Historical DOWN / STAY / UP |
|---|---:|---|---:|---:|---:|---:|---|
| AAVE | 5m | quotes | 1312 | 34.60% | 33.16% | 34.69% | 32.54% / 36.53% / 30.92% |
| AAVE | 15m | quotes | 372 | 40.59% | 43.01% | 32.58% | 39.78% / 24.16% / 36.06% |
| ADA | 5m | quotes | 1145 | 30.04% | 29.96% | 33.13% | 33.13% / 34.37% / 32.50% |
| ADA | 15m | quotes | 309 | 44.01% | 41.42% | 35.06% | 36.30% / 19.70% / 43.99% |
| BCH | 5m | trades | 359 | 37.88% | 41.50% | 35.53% | 32.18% / 38.36% / 29.46% |
| BCH | 5m | quotes | 4237 | 37.36% | 37.36% | 33.33% | 29.88% / 40.36% / 29.76% |
| BCH | 15m | quotes | 1208 | 41.80% | 41.31% | 34.91% | 33.85% / 29.83% / 36.33% |
| BCH | 60m | trades | 325 | 47.69% | 45.23% | 35.98% | 40.64% / 16.56% / 42.80% |
| BCH | 60m | quotes | 326 | 48.77% | 47.55% | 35.30% | 39.65% / 16.07% / 44.28% |
| BNB | 5m | quotes | 833 | 63.51% | 63.51% | 33.33% | 24.59% / 51.34% / 24.07% |
| BNB | 15m | quotes | 147 | 41.50% | 38.10% | 39.48% | 33.50% / 28.30% / 38.20% |
| BTC | 5m | trades | 4955 | 73.91% | 73.91% | 33.33% | 14.41% / 71.12% / 14.47% |
| BTC | 5m | quotes | 5017 | 73.71% | 73.71% | 33.33% | 14.03% / 71.90% / 14.07% |
| BTC | 15m | trades | 1590 | 54.47% | 54.47% | 33.33% | 23.62% / 51.33% / 25.04% |
| BTC | 15m | quotes | 1619 | 54.29% | 54.29% | 33.33% | 23.41% / 51.88% / 24.70% |
| BTC | 60m | trades | 347 | 33.14% | 33.72% | 33.40% | 30.28% / 37.73% / 31.99% |
| BTC | 60m | quotes | 349 | 32.38% | 33.52% | 32.58% | 28.41% / 40.11% / 31.47% |
| DOGE | 5m | trades | 451 | 23.73% | 23.73% | 33.33% | 18.83% / 61.67% / 19.50% |
| DOGE | 5m | quotes | 4400 | 41.52% | 41.52% | 33.33% | 29.21% / 42.10% / 28.69% |
| DOGE | 15m | quotes | 1297 | 27.91% | 24.83% | 34.37% | 32.77% / 34.21% / 33.02% |
| DOGE | 60m | trades | 325 | 47.08% | 45.85% | 35.39% | 30.60% / 22.80% / 46.60% |
| DOGE | 60m | quotes | 325 | 44.31% | 46.77% | 33.53% | 27.73% / 29.87% / 42.40% |
| ETH | 5m | trades | 4607 | 62.04% | 62.04% | 33.33% | 20.61% / 58.64% / 20.75% |
| ETH | 5m | quotes | 5010 | 62.63% | 62.63% | 33.33% | 17.87% / 64.31% / 17.83% |
| ETH | 15m | trades | 1392 | 42.53% | 42.53% | 33.33% | 28.38% / 41.76% / 29.86% |
| ETH | 15m | quotes | 1614 | 42.13% | 42.01% | 33.47% | 27.59% / 42.48% / 29.93% |
| ETH | 60m | trades | 347 | 33.14% | 38.04% | 30.22% | 33.40% / 27.82% / 38.78% |
| ETH | 60m | quotes | 349 | 32.95% | 38.11% | 30.08% | 32.64% / 29.13% / 38.24% |
| GOLD | 5m | trades | 688 | 89.39% | 89.39% | 33.33% | 6.95% / 86.71% / 6.34% |
| GOLD | 5m | quotes | 753 | 88.84% | 88.84% | 33.33% | 5.39% / 90.01% / 4.60% |
| GOLD | 15m | trades | 158 | 72.15% | 72.15% | 33.33% | 16.62% / 69.11% / 14.27% |
| GOLD | 15m | quotes | 189 | 74.07% | 74.07% | 33.33% | 10.67% / 83.24% / 6.08% |
| HYPE | 5m | trades | 1991 | 39.03% | 39.03% | 33.33% | 30.14% / 41.11% / 28.75% |
| HYPE | 5m | quotes | 3821 | 42.45% | 42.45% | 33.33% | 27.85% / 45.25% / 26.89% |
| HYPE | 15m | trades | 420 | 39.76% | 36.43% | 34.71% | 38.18% / 31.03% / 30.79% |
| HYPE | 15m | quotes | 1206 | 37.40% | 35.82% | 33.32% | 35.14% / 30.57% / 34.30% |
| HYPE | 60m | trades | 329 | 44.98% | 47.11% | 34.77% | 42.34% / 14.94% / 42.71% |
| HYPE | 60m | quotes | 330 | 46.67% | 47.27% | 36.31% | 41.76% / 15.48% / 42.77% |
| KSHIB | 5m | trades | 160 | 26.88% | 26.25% | 28.13% | 33.15% / 25.77% / 41.07% |
| KSHIB | 5m | quotes | 3689 | 39.03% | 39.03% | 33.33% | 23.69% / 51.43% / 24.87% |
| KSHIB | 15m | quotes | 1104 | 37.68% | 19.93% | 37.71% | 30.58% / 36.57% / 32.85% |
| KSHIB | 60m | trades | 324 | 48.46% | 44.44% | 36.74% | 37.03% / 16.91% / 46.06% |
| KSHIB | 60m | quotes | 326 | 49.69% | 46.93% | 37.27% | 35.33% / 21.69% / 42.98% |
| LINK | 5m | trades | 145 | 31.72% | 34.48% | 27.57% | 33.85% / 32.02% / 34.13% |
| LINK | 5m | quotes | 3549 | 34.80% | 34.80% | 33.33% | 26.64% / 46.47% / 26.89% |
| LINK | 15m | quotes | 1021 | 35.06% | 41.53% | 34.64% | 32.50% / 34.37% / 33.14% |
| LINK | 60m | trades | 328 | 46.95% | 46.04% | 35.37% | 43.15% / 16.99% / 39.86% |
| LINK | 60m | quotes | 329 | 46.81% | 46.81% | 34.69% | 42.29% / 17.95% / 39.76% |
| LTC | 5m | trades | 251 | 20.72% | 20.72% | 33.33% | 22.97% / 50.69% / 26.35% |
| LTC | 5m | quotes | 3343 | 38.62% | 38.62% | 33.33% | 24.25% / 52.49% / 23.27% |
| LTC | 15m | quotes | 926 | 25.49% | 21.38% | 35.79% | 32.80% / 33.97% / 33.24% |
| LTC | 60m | trades | 325 | 46.77% | 43.69% | 36.57% | 39.85% / 17.75% / 42.40% |
| LTC | 60m | quotes | 327 | 47.71% | 47.40% | 35.26% | 35.77% / 22.06% / 42.17% |
| NEAR | 5m | trades | 660 | 45.00% | 45.00% | 34.62% | 42.80% / 21.84% / 35.36% |
| NEAR | 5m | quotes | 3479 | 18.08% | 18.02% | 33.29% | 32.25% / 35.33% / 32.42% |
| NEAR | 15m | quotes | 986 | 48.68% | 47.26% | 35.61% | 40.26% / 16.55% / 43.19% |
| NEAR | 60m | trades | 275 | 46.18% | 51.27% | 32.63% | 44.87% / 7.01% / 48.12% |
| NEAR | 60m | quotes | 276 | 46.74% | 51.09% | 31.98% | 44.94% / 8.63% / 46.43% |
| PALLADIUM | 5m | quotes | 139 | 74.10% | 74.82% | 33.01% | 8.94% / 79.46% / 11.60% |
| PLATINUM | 5m | quotes | 144 | 68.75% | 68.75% | 33.33% | 10.49% / 81.05% / 8.47% |
| SILVER | 5m | trades | 331 | 62.24% | 62.24% | 33.33% | 19.78% / 61.52% / 18.69% |
| SILVER | 5m | quotes | 656 | 70.12% | 70.12% | 33.33% | 20.06% / 61.57% / 18.37% |
| SILVER | 15m | quotes | 148 | 52.03% | 52.03% | 33.33% | 24.37% / 55.10% / 20.53% |
| SOL | 5m | trades | 967 | 49.02% | 49.02% | 33.73% | 27.23% / 45.84% / 26.93% |
| SOL | 5m | quotes | 3883 | 48.80% | 48.80% | 33.33% | 24.22% / 51.86% / 23.93% |
| SOL | 15m | trades | 147 | 26.53% | 34.69% | 25.33% | 33.02% / 25.45% / 41.53% |
| SOL | 15m | quotes | 1180 | 31.86% | 30.42% | 34.72% | 31.59% / 36.19% / 32.22% |
| SOL | 60m | trades | 346 | 43.93% | 43.93% | 34.85% | 35.43% / 21.93% / 42.63% |
| SOL | 60m | quotes | 348 | 44.25% | 44.54% | 34.75% | 35.98% / 20.87% / 43.15% |
| SUI | 5m | trades | 400 | 27.25% | 27.00% | 33.57% | 32.08% / 36.26% / 31.66% |
| SUI | 5m | quotes | 3714 | 25.63% | 25.63% | 33.33% | 30.57% / 38.57% / 30.86% |
| SUI | 15m | quotes | 1123 | 26.98% | 13.71% | 35.78% | 32.08% / 34.74% / 33.18% |
| SUI | 60m | trades | 325 | 46.77% | 48.00% | 33.92% | 41.64% / 12.36% / 46.00% |
| SUI | 60m | quotes | 326 | 48.77% | 50.00% | 34.23% | 43.51% / 14.16% / 42.33% |
| VVV | 5m | quotes | 1329 | 33.41% | 34.39% | 32.73% | 39.53% / 24.97% / 35.50% |
| VVV | 15m | quotes | 385 | 43.38% | 45.45% | 33.03% | 44.92% / 15.15% / 39.93% |
| WLD | 5m | quotes | 1315 | 23.57% | 19.47% | 33.30% | 32.93% / 34.18% / 32.89% |
| WLD | 15m | quotes | 374 | 47.06% | 44.12% | 34.53% | 37.43% / 19.80% / 42.77% |
| XRP | 5m | trades | 1021 | 35.65% | 32.22% | 36.52% | 32.39% / 37.23% / 30.38% |
| XRP | 5m | quotes | 3816 | 42.11% | 42.11% | 33.33% | 25.59% / 49.61% / 24.79% |
| XRP | 15m | trades | 141 | 44.68% | 41.84% | 33.66% | 34.79% / 24.80% / 40.41% |
| XRP | 15m | quotes | 1141 | 27.78% | 25.85% | 34.76% | 31.95% / 36.21% / 31.84% |
| XRP | 60m | trades | 346 | 41.91% | 43.35% | 31.43% | 33.75% / 25.30% / 40.95% |
| XRP | 60m | quotes | 349 | 43.55% | 45.85% | 33.38% | 36.25% / 24.52% / 39.23% |
| ZEC | 5m | trades | 683 | 40.41% | 39.39% | 35.99% | 34.72% / 21.27% / 44.01% |
| ZEC | 5m | quotes | 3847 | 30.73% | 30.13% | 33.75% | 32.92% / 34.72% / 32.36% |
| ZEC | 15m | quotes | 1229 | 43.21% | 42.39% | 34.77% | 38.22% / 22.77% / 39.02% |
| ZEC | 60m | trades | 275 | 46.18% | 48.36% | 33.99% | 44.90% / 9.38% / 45.72% |
| ZEC | 60m | quotes | 276 | 42.75% | 49.64% | 31.34% | 47.00% / 8.64% / 44.36% |

These are model/asset/timeframe tests, not a claim of thousands of independent strategies. Trying many methods can find lucky percentages. The paired-evidence sheets include day-block uncertainty and a global Holm multiple-comparison adjustment. Short validation periods do not support a validated prediction winner.

Order-book depth, partial fills and execution price rounding to the tick are not reproduced. Available whole-contract sizes are respected. Funding, financing, liquidation and historical contract changes remain missing; reported returns are explicitly limited to fees/slippage.

## Access and reproduce

- Open the repository dashboard with `bash run_dashboard.sh`; choose the Multi-asset timeframe and the contract tab. Existing BTC studies remain available below.
- Download `KALSHI_MULTI_ASSET_RESEARCH.xlsx` with GitHub’s **Download raw file** button; GitHub itself does not preview workbooks.
- Resume collection: `.venv/bin/python -m multiasset.kalshi --workers 3 --max-windows 240`.
- Resume research: `OPENBLAS_NUM_THREADS=1 .venv/bin/python -m multiasset.pipeline --workers 4`.
- Refresh separate current buffers: `.venv/bin/python -m scripts.refresh_kalshi_current`.
- Audit executed results: `.venv/bin/python -m scripts.audit_multiasset_results`.
- Export actual checkpoints: `.venv/bin/python -m scripts.export_multiasset`.
- Software tests: `.venv/bin/python -m pytest -q tests test_live_signal_server.py`.

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

**Overfitting:** Like memorizing answers to a practice exam instead of learning. A rule can look smart on old prices and fail later. Separate later tests and fixed setting changes help detect this, but cannot prove future success.

**Look-ahead and leakage:** Peeking at tomorrow’s price while deciding today makes a backtest cheat. Checks recompute earlier outputs without later data. Known leaking sources remain excluded.

**Held-out versus untouched:** Held-out means not used to fit that model. Untouched also means nobody inspected or selected against those dates earlier. These historical comparisons cannot meet that stronger claim.

**Brier/log loss:** Scores for probability quality; smaller is better. Log loss strongly penalizes confident wrong predictions. Three-class Brier sums squared errors across all three classes.

**Calibration:** A model that says 60% should succeed about 60 times out of 100 similar cases. Temperature is fitted only on a separate earlier calibration segment. Calibration is not guaranteed in later markets.

**Joint outcomes:** When selected indicators agree, count what actually happened after their joint historical configuration. Do not multiply individual accuracy percentages or treat correlated indicators as independent votes.

**Freshness:** September snapshots are historical. Current probabilities require fresh primary prices and a separate rolling 30-day model refit/calibration. Static workbook probabilities are current only at the recorded export/as-of time; the dashboard checks age again every time it displays them.

**Walk forward:** Repeatedly learn on earlier observations, then score later ones. Small folds can fail for lack of history; failures remain visible.

**Sensitivity:** Fixed parameter neighbors are selected before held-out scoring. Fee stresses halve/double fees and double fees plus slippage. Parameter selection records and earlier-fold results are retained.

**Cheating checks:** Past-prefix and future-mutation checks look for later prices changing earlier signals. Known leaking original sources remain quarantined. Finite checks cannot prove the absence of every possible bias.

**Duplicates:** Exact sampled training signal duplicates and very high correlations are recorded. Repeated signals are not counted as independent evidence.

**N/A:** Missing, undefined, insufficient or unverified. N/A is never silently converted to a real zero.

**Workbook access:** GitHub does not preview Excel. Open the workbook page, choose Download raw file, then open the downloaded .xlsx in Excel or LibreOffice. Do not save a GitHub HTML page with an Excel extension.

**Original dashboard:** This repository adds tabs to its existing Streamlit lab. The separate hosted Perpetual Edge Site project was inspected read-only; it was not deployed or modified by this task.
