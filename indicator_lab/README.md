# Bitcoin indicator prediction study

Start with `reports/predictions/REPORT.md` or download
[`DOWNLOAD_BTC_INDICATOR_RESULTS.xlsx` in the repository's top folder](../DOWNLOAD_BTC_INDICATOR_RESULTS.xlsx).
Sign in with the GitHub account that has repository access, then use **Download
raw file** (down arrow). Save the file and open it in Excel or LibreOffice.
If you see **404**, first check whether the repository itself opens in the same
browser/account. GitHub can hide repositories from unauthorized accounts using
404, and the raw-file domain may not share your GitHub login. If the repository
opens but the file download fails, choose **Code → Download ZIP**, unzip the
whole project and open `DOWNLOAD_BTC_INDICATOR_RESULTS.xlsx` in its top folder.
The workbook also
exists at `reports/TradingView_Indicator_Predictions.xlsx` in the Codex workspace.
The dashboard has **Download indicator prediction Excel** and a timeframe
selector. No trading account, API key or coding is needed to read saved results.

**Every column is explained:** open the workbook's **Column Guide** tab beside
Read Me, or read [the column guide here](../WORKBOOK_COLUMN_GUIDE.md). It includes
examples and explains when TRUE is a warning rather than a passed check.

**This is a formula benchmark, not all TradingView indicators.** There are 147
formula entries attempted at three timeframes, plus a separate execution-compatibility
audit of 210 original public Pine scripts. Private and unavailable scripts cannot
be tested. Native TradingView formula matching is unverified.

Most indicators aren't predictions. Our experiment teaches the same small logistic
model to read each indicator's present and past values, using 2020–2024 data. It
chooses among default, 20% shorter and 20% longer windows using 2025 only. It then
compares next-closing-price UP/DOWN guesses during January–September 2026.
The user chose **retrospective** testing; those market dates were already examined
in the earlier strategy project. They are held out from this model fitting, but
cannot be presented as genuinely untouched research evidence.

Three separate questions:

1. Did it guess the next direction correctly? See **Prediction Accuracy**.
2. Was it consistently better than a simple guess? See **Baselines**, **Walk
   Forward**, **Monthly Accuracy**, **Robustness**, and the retrospective gate.
3. Did trading make money after costs? See **net_return**, **buy_hold_return** and
   the separate financial gate. A high hit rate can still lose most of the money.

All experiments use Binance spot BTC/USDT. The 15m and 60m candles aggregate the same
verified 5m prices. Buy and sell each cost a 0.1% fee and 0.05% slippage. Simulations
start with 10,000 USDT, buy or hold cash, and do not borrow. These are idealized
fractional-BTC simulations without exchange minimum order sizes, lot rounding,
latency or market impact. Results near -100% should be read as almost total loss;
real exchange order minimums would stop trading earlier. No real orders are sent.

Read the frozen [protocol](PROTOCOL.md) for label alignment, purging, missing data,
scaling, penalties, profile selection, causality checks, uncertainty and limitations.
N/A always means missing, not executed, unverified or mathematically undefined.

## Reproduce (for a technical helper)

The root `requirements.txt` already pins every Python dependency used here. Do
not change it to refresh old experiments; prior reports hash those versions.

```bash
bash setup.sh
# Optional Pine compatibility audit (Node.js required):
.venv/bin/python -m indicator_lab.pine_audit
# Download official prices; raw archives are cached locally, not committed:
.venv/bin/python -m indicator_lab.data
# Freeze training and validation choices before calculating test accuracy:
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m indicator_lab.runner train --minutes 5
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m indicator_lab.runner train --minutes 15
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m indicator_lab.runner train --minutes 60
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m indicator_lab.runner score --minutes 5
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m indicator_lab.runner score --minutes 15
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m indicator_lab.runner score --minutes 60
.venv/bin/python -m indicator_lab.runner combine
.venv/bin/python scripts/export_indicator_leaderboard.py
.venv/bin/python -m pytest -q
.venv/bin/streamlit run app.py
```

Do not edit the frozen protocol/code between fit and score: the runner verifies
hashes and refuses to mix versions. Rerun fitting after changes. Download manifests
include generation timestamps; keep the saved dataset and manifest for exact
artifact verification. Model coefficients and selection are reproducible from the
saved prices; generated-at timestamps and Excel package metadata can differ.

`reports/predictions/frozen_*m.json` contains coefficients, training scalers,
validation choices, internal walk-forward fits and numerical causality checks.
`combined.json` and `leaderboard.csv` contain measured scores.
`labels_*m.csv.gz` contains times, actual prices, ties and scoring eligibility.
`probabilities/ID_TFm.npz` contains FULL float64 probabilities, exact UP decisions
and feature eligibility, aligned row-for-row with the matching labels file.
The first training-data boundary forecast can exist in the labels file without
being scorable; apply `scorable_direction` and period target boundaries to recompute
accuracy. Do not suppress trades using future tie/gap labels.

The catalog is extensible: add a formula with its source and fixed settings, run
the same integrity checks, then retrain the full experiment. Newly comparing more
candidates creates additional multiple-testing risk. Do not tune on these 2026
scores and keep calling them fresh evidence. An independent future study needs
new, unexamined prices and a frozen protocol.
