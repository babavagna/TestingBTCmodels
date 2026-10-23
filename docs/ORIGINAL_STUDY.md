# Archived original ten-strategy study

This is historical documentation. See the [current full-list project](../README.md). Counts and protocols below refer to the original starter study.

# Bitcoin Strategy Lab

A beginner-friendly project for comparing **10 open-source GitHub strategy
adaptations** on the same real Bitcoin prices. Includes a browser dashboard,
verified data, downloadable results, individual trade records and automated tests.
It supports adding up to 100 strategies without changing the trading engine.

**Read the [integrity and chronological audit](../reports/audit/REPORT.md) first.**
Earlier comparisons already examined 2025 and January–September 2026, so those
dates cannot honestly be called an untouched test. No unseen-data ranking is
issued. The dashboard shows chronological diagnostics alphabetically.

**This is personal, noncommercial research. It does not place real trades.**

## Coverage against the supplied 100-strategy list

The original ten were a starter implementation, not the winners of a 100-entry
screen. [The source cross-check](../reports/CANDIDATE_CROSSCHECK.md) maps all ten to
the supplied list and explains why the other 90 remain untested. All 100 source
paths were found in checked repository snapshots; source availability does not
establish runtime compatibility or performance.

[Download the complete candidate/status CSV](../sources/candidate_crosswalk.csv).
This source-only review adds no strategies or results to the tested leaderboard.

## Download the Excel report

Open [Bitcoin_Strategy_Leaderboard.xlsx](../reports/Bitcoin_Strategy_Leaderboard.xlsx)
on GitHub and click **Download raw** (the downward-arrow button). Open the saved
file in Microsoft Excel or LibreOffice Calc. If GitHub asks you to sign in, use
the GitHub account that can access this repository. The workbook has no macros
and does not need an exchange login or API key.

Start with **Read Me**, then **All Strategies**. The five requested sheets are
**All Strategies**, **Top 10**, **Prediction Accuracy**, **Charts**, and **Failed Tests**.
Supporting sheets preserve walk-forward, sensitivity and training records,
archive sources, and chart inputs. There are 10 distinct strategies and 30
protocol-specific result rows; do not mix exploratory and chronological results.

**Top 10 has no eligible genuine unseen ranks**, and lists why the strategies
are excluded. No existing test period is falsely relabeled untouched.
**Prediction Accuracy is N/A** because these rules provide no directional
forecasts. **Failed Tests** distinguishes failed investment gates from software
errors. Missing hours, unknown upstream training history and unverified live
performance are explicit, not silently filled in.

The workbook is a dated snapshot of verified saved reports. To refresh it after
running research, use:

```bash
.venv/bin/python -m scripts.export_leaderboard
```

The neighboring `Bitcoin_Strategy_Leaderboard.json` records workbook and input
fingerprints, sheet counts and the source of the export. Exporting does not
rerun strategies or create new performance claims.

## Start here — no coding knowledge needed

The integrity audit, walk-forward evaluations and parameter/fee checks have been run.
Their [plain-language report](../reports/audit/REPORT.md) explains what failed and what remains uncertain.
The earlier exploratory comparison has also been run. Open [the plain-language results](../reports/RESULTS.md)
or [the results spreadsheet](../reports/summary.csv) on GitHub.
Use [the source list](../sources/strategies.json) to see where every strategy came from.

To use the dashboard in a Python development environment, open a terminal in
this repository and paste these commands, one at a time:

```bash
bash setup.sh
bash start.sh
```

The first installs dependencies and runs the tests. The second starts the dashboard.
Use your development environment's supported port-opening feature for port 8501.
This cloud onboarding chat does not provide browser previews; the server can
still run here, and all saved results are readable directly on GitHub.
In the dashboard, use **Download / refresh real prices**, then **Run comparison**.
The already saved verified dataset works without downloading it again.
Stop the dashboard with Ctrl+C. No Binance login, API key or money is required.

On GitHub, the **Actions** tab also has a **Refresh prices and compare** workflow.
Choose **Run workflow**. It runs the tests, downloads verified data and uploads a
`bitcoin-research-results` ZIP under the completed run's **Artifacts** section.
It never trades, deploys or overwrites repository files. Its current run's reports
can be compared with the saved baseline; it does not automatically commit updates.
GitHub may ask you to enable Actions before this button is available.

## What was actually obtained

- Exchange: **Binance spot**, pair **BTC/USDT**, timeframe **1 hour**, timestamps UTC.
- Requested and obtained boundaries: **2020-01-01 00:00 through 2026-09-30 23:00 UTC**.
- **81 monthly archives**, each verified against Binance's published SHA-256 checksum.
- **59,129 real candles** out of 59,160 calendar hours: **31 hours are missing**.
- All ten strategies and buy-and-hold use the exact same cleaned price file.

See [data/manifest.json](../data/manifest.json) for every source URL, fingerprint
and missing timestamp. The downloader handles Binance's January 2025 timestamp
change from milliseconds to microseconds. It validates timestamps, duplicates,
OHLC consistency, positive prices and nonnegative volume.
A checksum proves the download matches Binance's published archive; it cannot
prove that the exchange's historical records themselves have no errors.

## How the comparison works

| Setting | Shared rule |
| --- | --- |
| Starting money | 10,000 USDT per strategy |
| Trading fee | **0.1% per side**, on both buys and sells |
| Slippage | **0.05% per side**: buy higher, sell lower |
| Decisions | Use completed candles only; fill at the next available **adjacent hourly** open |
| Position sizing | Use available cash for one long Bitcoin position; no leverage or shorts |
| First trade opportunity | After 200 hourly candles, 2020-01-09 08:00 UTC for the saved run |
| Conflicting signals | Suppress a buy; allow a sell for an existing position |
| Last candle | No new entry; liquidate any remaining position at the last close, with exit costs |
| Missing hours | Never fill prices; cancel a pending order crossing a gap; restart indicators and wait 200 consecutive candles |
| Position during gaps | Remains held, including during the new indicator warmup; no assumed exit at an unknown price |
| Benchmark | Buy once after the same initial warmup, hold and sell at the end, with the same costs |

The buy price is `open × 1.0005`. Bitcoin quantity is
`cash ÷ (buy price × 1.001)`. A sell returns
`quantity × reference price × 0.9995 × 0.999`. Fees are charged in USDT.
Portfolio value between transactions is cash plus Bitcoin valued at the recorded
close. Drawdown includes initial trading costs and observes recorded prices only.
It cannot see losses inside missing hours or inside a candle.

The original strategies come from the GPL-licensed
[freqtrade/freqtrade-strategies](https://github.com/freqtrade/freqtrade-strategies)
collection. Original files, authorship, immutable commits and licenses are saved.
There are ten distinct strategies from **one GitHub repository**, including EMA,
Bollinger/RSI, MACD/CCI, oscillator, momentum and ADX rules.

**These are hourly signal adaptations, not exact reproductions of the full original
Freqtrade bots.** Native ROI targets and stoploss rules are omitted for all
strategies; entry and exit signal formulas are preserved. Most originals used
other timeframes. This makes a transparent, common signal comparison, but results
must not be attributed to the original bots' complete trading behavior. In
particular, a strategy can hold for years if no sell signal occurs.

## Understanding the results

- **Return:** percentage gained or lost after trading costs.
- **Sharpe ratio:** average hourly gain compared with how bumpy hourly results are, scaled to a year. Higher is generally better; it is not a percentage or a safety guarantee. We use 8,760 hours/year, 0% risk-free rate, sample standard deviation and include idle cash hours. Changes spanning missing hours are excluded from Sharpe only.
- **Drawdown:** largest fall from an earlier portfolio high. A 77% drawdown means
  a 10,000 USDT peak could fall to about 2,300 USDT before recovering.
- **Trades:** completed buys and sells. One winning trade is weak evidence.
- **Win rate:** fraction of completed trades that made money, after costs.
- **Profit factor:** total winning-trade profits divided by losses. Blank means
  there were no losses to divide by; it does not mean unlimited expected profit.

The earlier full-period exploratory CSV records return order for reproduction only; it is not an unseen-data leaderboard. The current audit ranks no previously examined period. Fewer than 30 completed trades is explicitly flagged; this is a caution rule, not a statistical guarantee. Every row includes the same buy-and-hold return.

**Next-hour directional prediction accuracy is N/A for all ten strategies.** They produce entry/exit signals, not next-hour up/down forecasts. Trade win rate is not forecast accuracy. The separate audit is in [directional_predictions.csv](../reports/directional_predictions.csv); zero forecast models were scored.

No parameters were optimized against this dataset. These are descriptive
historical comparisons, not independently validated predictions. Costs assume
fixed slippage rather than a real order book. There is no lot-size rounding,
partial-fill model, spread model, intrabar stop execution, funding or borrowing.
See the [actual results and limitations](../reports/RESULTS.md).

## Optional terminal commands

After setup, these commands refresh prices, run comparisons and inspect coverage:

```bash
.venv/bin/python -m btc_lab download --start 2020-01 --end 2026-09
.venv/bin/python -m btc_lab run
.venv/bin/python -m btc_lab audit
.venv/bin/python -m btc_lab strategies
.venv/bin/python -m pytest -q
```

To refuse any missing hours, use `run --gap-policy strict`. The full dataset
will then be refused because of the documented gaps. Choose a continuous range
from `audit`, for example `run --start 2024-01-01 --end 2024-12-31 --gap-policy strict`.
Date-only end dates include the entire UTC day. Every run overwrites the reports
with its actual dates; old results cannot silently appear under a new date range.

## Integrity, walk-forward testing and sensitivity

The audit uses 2020–2024 for parameter selection, 2025 for validation and
January–September 2026 as a **nominal test excluded from this fit**. This last
period is not genuinely untouched because prior project results already used it.

These strategies are indicator rules, not learning models. Training selects
among three predeclared settings: original and roughly 20% lower/higher values.
Only training scores select a setting; validation/test results never rescue or
retune it. Unknown upstream tuning history is another limitation.

Walk-forward means “practice on past years, then check the next year”: fit
2020–2021 -> evaluate 2022; fit 2020–2022 -> evaluate 2023; fit 2020–2023 ->
evaluate 2024. The final fit uses 2020–2024, validates on 2025, and uses the same
frozen settings for 2026. Training ends are purged by one hour; scoring starts
with fresh cash, past-only indicator context and no inherited positions.
The audit uses a shared 300-hour warmup so even the 240-hour sensitivity variant
has enough history. The old exploratory comparison retains its original 200-hour
warmup; compare strategies within a protocol, not across different protocols.

Nine parameter/fee combinations per period, plus one doubled-fee/slippage case,
check fragility. Every case has the same-cost buy-and-hold reference. Stress
results are diagnostic; the best stress setting is never promoted as a winner.
No later candles were downloaded and no future test has been executed.

To rerun this audit:

```bash
.venv/bin/python -m btc_lab robustness
```

[Protocol](../reports/audit/protocol.json), [frozen choices](../reports/audit/frozen_selection.json),
[walk-forward rows](../reports/audit/walk_forward.csv), [stress cases](../reports/audit/sensitivity.csv)
and [causality checks](../reports/audit/causality.csv) are saved for inspection.
The untouched-data leaderboard is intentionally empty. A genuine final test
requires freezing the rules now and observing new future data without retuning.

## Problems explained simply

- **403 / Tunnel connection failed:** the environment blocked the website. Allow
  `data.binance.vision` in environment settings, save, then retry. This does not
  mean those dates are unavailable. The initial block was resolved during setup.
- **404 on a month's published checksum:** that verified archive is unavailable.
  The manifest records it; no invented data replaces it.
- **Checksum mismatch:** a file is damaged or the upstream archive changed.
  The file is not used. Remove that month's ZIP from `data/raw/` and download again.
- **Changed result/data file:** rerun the comparison. The app refuses changed or
  stale files instead of showing unreliable old numbers.
- **No trades:** the rules did not produce an executable trade. It is not a
  hidden winning result or an installation error.

## For a developer helping you later

[Expansion guide](docs/EXPANDING.md) explains how to add genuinely distinct
strategies up to 100. [Validation report](../reports/VALIDATION.md) describes actual
checks. Dependencies, including transitive packages, are pinned in
`requirements.txt`; `requirements.in` lists direct choices. Tested on Python
3.12.14 on Linux; use Python 3.12 for the closest reproduction.

Source code: GPL-3.0; retained QTPyLib test reference: Apache-2.0.
Data and data-derived outputs: Binance Vision **CC BY-NC-SA 4.0**, plus its
[dataset terms](../sources/BINANCE_DATASET_TERMS.md), for noncommercial research.
[Attribution and source details](../sources/README.md).
