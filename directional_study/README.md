# Your selected indicators: directional UP and DOWN accuracy

Open `BTC_UP_DOWN_ACCURACY.xlsx` in the repository's top folder, or read
[every measured result online](../reports/selected_directional/REPORT.md).
While signed in to GitHub, click the workbook then **Download raw file**. If
that fails but the repository opens, **Code → Download ZIP**, unzip the whole
project and open the workbook in Excel or LibreOffice.

You supplied 90 entries covering 52 distinct IDs, including 35 candlestick
patterns. Repeated IDs are preserved in Request List but counted once per chart.
All 52 were re-executed on 5m, 15m and 60m Binance spot BTCUSDT candles.

**Correct UP guesses** asks: of the predictions saying UP, how many were correct?
**Correct DOWN guesses** asks the same for DOWN. Look at the adjacent counts.
**N/A** means the model made no such guesses, or no pattern events were scorable.
It is not zero, 50%, 100% or an execution failure. Predictions with equal next
closes are unscored ties; their guesses are not suppressed from trading.

The main tables score every eligible candle. **Pattern Events** separately scores
the SAME frozen model only on candles where that pattern actually appeared.
A Doji's positive pattern code does not automatically mean bullish. The model
was not refitted only on pattern occurrences. ATR and other volatility formulas
do not forecast UP/DOWN on their own; every percentage is indicator + trained
logistic readout. CORREL/BETA use BTC high/low series, not a reference market.

The models were trained on 2020–2024, with profiles selected using 2025. The user
chose January–September 2026 as a **retrospective** comparison. Those dates were
already examined, and the requested subset was chosen after the earlier results
were available. This is not a new independent or genuinely untouched test.
Native TradingView formula agreement is unverified. Direction confidence intervals
are descriptive; market observations can be correlated. Flags below 100 direction
calls or 100 scored events are warnings, not a proof of reliability above 100.

Actual re-execution regenerates every formula, re-runs all frozen models and
compares original probabilities and decisions. The saved run also replays
available default-profile walk-forward models on 2022/2023/2024. Original failed
fits remain failures. See [the fixed protocol](PROTOCOL.md).

To rerun with the existing installed/pinned dependencies and saved verified prices:

```bash
.venv/bin/python -m directional_study.run freeze
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m directional_study.run score --minutes 5
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m directional_study.run score --minutes 15
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m directional_study.run score --minutes 60
.venv/bin/python -m directional_study.run combine
.venv/bin/python scripts/write_requested_direction_report.py
.venv/bin/python scripts/export_requested_directions.py
.venv/bin/python -m pytest -q
```

Keep the original frozen models/price manifests and the run's source code intact.
The input manifest verifies their hashes. Accuracy does not include costs; the
separate long/cash returns still charge 0.1% fee and adverse 0.05% slippage on every
buy and sell, with 10,000 USDT per period. DOWN means cash, not a short. This
idealized fractional-order model omits minimum order sizes, rounding, latency and
market impact. The source list, data sources, forecasts, failures and actual
verification evidence are saved under `sources/selected_directional` and
`reports/selected_directional`.
