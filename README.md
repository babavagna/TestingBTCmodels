# Bitcoin strategy and indicator prediction lab

**New: next-candle indicator predictions on 5-minute, 15-minute and 1-hour
Binance BTC/USDT charts.** Read the [plain-language prediction results](reports/predictions/REPORT.md)
or [open DOWNLOAD_BTC_INDICATOR_RESULTS.xlsx](DOWNLOAD_BTC_INDICATOR_RESULTS.xlsx)
in this repository's top folder.
While signed in to the GitHub account with repository access, use **Download raw
file** (the down-arrow button). Save the `.xlsx` file, then open it in Excel or
LibreOffice. GitHub may not preview it.

**If you see 404:** first open [the repository](https://github.com/babavagna/TestingBTCmodels)
in the same browser. GitHub can show 404 when an account does not have access;
the raw-download domain may not share your signed-in session. Navigate to
**DOWNLOAD_BTC_INDICATOR_RESULTS.xlsx → Download raw file** from the repository's
top folder after signing in. This copy is identical to
`reports/TradingView_Indicator_Predictions.xlsx`. If the file download still fails,
use **Code → Download ZIP** on the repository home page, unzip the project, and
open `DOWNLOAD_BTC_INDICATOR_RESULTS.xlsx` inside it. This fallback downloads the
whole project. In the Codex workspace, the same file is already in `reports/`;
the dashboard also has **Download indicator prediction Excel**. A successful
download from the cloud environment does not verify access from your own browser.

**Executed: 410 completed forecast tests from 441 formula/timeframe attempts;
31 unscorable attempts. All 150 automated tests passed.** The Excel file has 20
sheets. No tested model passed the financial gate in both 2025 and 2026.

**What do the columns mean?** Open **Column Guide**, the workbook's second tab,
or read [the complete plain-language column guide](WORKBOOK_COLUMN_GUIDE.md).

This is a reproducible formula benchmark, **not every TradingView indicator**.
Private and unavailable scripts are outside coverage, and native TradingView
formula agreement is unverified. Each indicator feeds the same trained forecast
model. The report separates direction accuracy from trading profits after costs.
Training uses 2020–2024; 2025 selects settings; January–September 2026 is a
**retrospective comparison**, as requested. Those market dates were already examined.
No genuine untouched-test success is claimed. Sources, prices, frozen models,
forecasts, failures and tests are saved in [the prediction study](indicator_lab/README.md).

## Earlier full 100-candidate strategy study

A beginner-friendly Bitcoin research project using real **Binance spot BTC/USDT
1-hour prices, January 2020–September 2026**. All 100 supplied GitHub entries are
included in the source catalog and execution audit. Completed signal backtests,
blocked programs and leakage failures are clearly separated. No results are invented.

**Executed here: 83 completed signal backtests, 15 blocked candidates and two
confirmed leakage exclusions. All 117 automated tests passed. The audit ran
3,242 portfolio simulations; no candidate passed both yearly diagnostic gates.**

**Start with the [plain-language full-list report](reports/full100/REPORT.md)** or
[download the Excel workbook](https://raw.githubusercontent.com/babavagna/TestingBTCmodels/main/reports/Bitcoin_Strategy_Leaderboard.xlsx).

**These are signal adaptations, not full reproductions of the original trading
bots.** They buy Bitcoin or hold cash using shared account rules. Native shorts,
leverage, stops, profit targets, pyramiding and risk sizing are omitted. Supported
Jesse entries use documented formula translations; full native parity is unverified.
Every row discloses its implementation scope.

**There is no genuine untouched-data Top 10.** Earlier work already examined 2025
and January–September 2026. They are held out from the new fitting step, but replay
cannot erase that earlier exposure. The report and dashboard show retrospective
diagnostics alphabetically. Upstream optimization history is unknown.

This project never places real trades or requires an exchange account or API key.

## Download and open Excel

1. Click **[Download the Excel file directly](https://raw.githubusercontent.com/babavagna/TestingBTCmodels/main/reports/Bitcoin_Strategy_Leaderboard.xlsx)**.
2. Save `Bitcoin_Strategy_Leaderboard.xlsx`, then open it in Microsoft Excel or
   LibreOffice Calc. No macros are used.
3. Read **Read Me**, then **All Strategies**. Filter the execution-status column to
   distinguish completed backtests from blocked or quarantined candidates.

GitHub's file page may show an error or no spreadsheet preview. That does not
mean the Excel file is damaged; use the direct download above. If GitHub still
shows **404**, sign in with the account that owns or has access to this repository.
You can also use the dashboard's **Download full Excel leaderboard** button.

The workbook includes every supplied candidate and its immutable GitHub URL,
metrics where actually executed, scoring dates, source data, costs, sample flags,
leakage checks, validation status and prediction capability. **N/A means missing,
not executed, unverified or mathematically undefined; it does not mean zero.**

The requested sheets are **All Strategies**, **Top 10**, **Prediction Accuracy**,
**Charts**, and **Failed Tests**. Supporting sheets preserve both scored periods,
walk-forward runs, training fits, sensitivity runs, monthly archive evidence, robustness summaries,
causality checks and chart inputs. The Top 10 sheet explains why no genuine unseen
rank can be issued. Neural is recognized as a predictor, but its unsupported
forecast runtime has no measured accuracy. Trade win rate is not prediction accuracy.

The neighboring [Excel manifest](reports/Bitcoin_Strategy_Leaderboard.json) records
the workbook fingerprint, input manifest and software test evidence.

## What all strategies share

- **Prices:** the same 59,129 observed Binance spot BTCUSDT hourly candles from 81
  official monthly archives, each checked against its published SHA-256 checksum.
- **Costs per buy AND sell:** 0.1% trading fee plus 0.05% slippage, meaning a slightly
  worse execution price. Start each scoring period with 10,000 USDT.
- **Trading:** a completed-hour signal fills at the next adjacent hour’s open.
  Long/cash, all-in, no borrowing. Final positions close with exit costs.
- **Missing hours:** 31 hours in 15 gaps before 2025; no missing 2025/2026 scoring
  hours. No prices are fabricated. Positions stay held across gaps and no fill
  crosses a missing-hour gap. Indicators retain observed history; a period counts
  observed bars and can stretch in calendar time when hours are missing.
- **Warmup:** one common initial 4,096-observation warmup, covering long indicators.
  First eligible fill: **2020-06-20 01:00 UTC**. This reduces early training evidence.
  We do not repeatedly discard years of history after a short gap.

Source evidence and all missing timestamps: [data/manifest.json](data/manifest.json).
The 100 original source bodies, pinned commits and licenses are in
[sources/full100/](sources/full100/). [Adapter details](sources/full100/README.md)
explain exactly what is and is not reproduced.

## Training and integrity checks

Training receives **2020–2024 only**. The fixed candidate profiles are original
settings and supported numeric neighbors at −20%/+20%. Select the highest training
Sharpe with at least 30 completed trades, otherwise retain the original profile.
Purge the last training hour; the final fitting candle is **2024-12-31 22:00 UTC**.
Save the choice before scoring **2025 validation** and **January–September 2026**.
Neither later score selects the settings.

Walk forward: fit through 2021, evaluate 2022; fit through 2022, evaluate 2023;
fit through 2023, evaluate 2024. Every scored period starts with fresh cash.
The saved training records identify folds without enough trades for a qualified fit.

Check every completed parameter profile with independently regenerated historical
prefixes and changed future prices. Also review source code: **CCIStrategy and
ReinforcedQuickie are quarantined for confirmed future-dependent interpolation**,
even when a buy/sell threshold masks the change. This is a limited audit, not proof
that every possible source bug or historical optimization has been excluded.

Stress half/base/double trading fees, plus doubled fee AND slippage for each
selected profile. A diagnostic gate requires a positive return, beating buy and
hold, and at least 30 trades. A financial failure is different from a software error.
Testing many strategies and published tuned settings still creates overfitting risk.

## Understand the numbers

- **Net return:** what your original money gained or lost after costs. +20% turns
  100 into 120.
- **Sharpe:** average reward compared with how bumpy hourly changes are, scaled
  to a year. Higher often means smoother reward; it is not a percentage or promise.
- **Maximum drawdown:** the biggest recorded fall from an earlier account peak.
  A 30% fall turns a peak of 100 into 70.
- **Profit factor:** total winning-trade dollars divided by losing-trade dollars.
  Below 1 means losses outweighed wins. No loss dollars makes this undefined.
- **Win rate:** percentage of completed trades that made money. Many tiny wins
  can still be outweighed by a large loss.
- **Trades:** completed buy-and-sell pairs. Fewer than **30** is flagged as too
  little evidence, like judging a player after too few games.
- **Buy-and-hold return:** buy once at the same scoring start and sell at the end
  with the same costs. This is the yardstick.
- **Directional accuracy:** correct explicit next-hour up/down forecasts divided
  by forecasts scored. No supported frozen-training forecast model was executed;
  accuracy remains N/A, including the native neural predictor’s incomplete runtime.

## Run it without coding

Saved reports and Excel open immediately. To use the browser dashboard, open the
project terminal and paste one line at a time:

```bash
bash setup.sh
bash start.sh
```

Setup installs pinned Python dependencies, installs the offline Node dependencies
when Node/npm are available, and executes the tests. Node.js **24.19.0**, npm and
C/C++ build tools are needed to rerun the old native Zenbot indicator libraries.
The tested cloud runtime uses Python 3.12. Setup does not start any trading daemon.

Open your environment’s supported preview for port **8501**. The dashboard shows
the verified 100-candidate audit first and offers Excel/CSV downloads. Its lower
section preserves the separate original ten-strategy study; do not mix protocols.

To reproduce the full saved research:

```bash
.venv/bin/python -m full_universe.audit --workers 3
.venv/bin/python -m pytest -q --junitxml=reports/test-results.xml
.venv/bin/python -m scripts.report_full_universe
.venv/bin/python -m scripts.export_full_leaderboard
```

This can take a while. A declared **120-second limit per full signal-generation
call** records unfinished calculations as blocked, with N/A performance. It does
not mean the strategy lost money. Unchanged causal signal caches can be reused;
source, dependency, adapter and dataset fingerprints prevent reuse after changes.

GitHub **Actions → Replay full 100-candidate audit → Run workflow** runs the same
research and uploads the files as an artifact. This workflow is provided for
reproduction; a successful remote run is not claimed unless actually executed.
It does not trade, deploy, or automatically commit updates.

## Files and the original study

- [Full-list report](reports/full100/REPORT.md), [all 100 statuses](reports/full100/inventory.csv),
  [both scored periods](reports/full100/period_results.csv),
  [walk forward](reports/full100/walk_forward.csv),
  [sensitivity](reports/full100/sensitivity.csv), and
  [runtime/causality failures](reports/full100/failed_tests.csv).
- [Per-candidate original trade logs and frozen selections](reports/full100/candidates/),
  [result fingerprints](reports/full100/run.json), and [software checks](reports/test-results.xml).
- [Supplied-list crosswalk](sources/candidate_crosswalk.csv) retains all original
  links and list numbers, now linked to expanded execution status.
- [Archived ten-strategy documentation](docs/ORIGINAL_STUDY.md) and
  [original chronological audit](reports/audit/REPORT.md) remain historical evidence.
  Their shorter warmups and parameters differ from the expanded audit.

Code retains GPL-3.0 and upstream source licenses; Binance data and derived research
retain the saved **CC BY-NC-SA 4.0** terms. See [data terms](sources/BINANCE_DATASET_TERMS.md)
and [source documentation](sources/full100/README.md). This is personal,
noncommercial research, not a claim of future profits or verified live execution.

The cloud startup instructions have also been updated in an environment draft.
To activate them for future sessions, review and save the changes in Environment
settings, then publish the environment. Saving that draft does not itself publish
or restart the current environment.
