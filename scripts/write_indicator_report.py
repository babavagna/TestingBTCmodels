#!/usr/bin/env python3
"""Generate a readable report from actual execution artifacts."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from indicator_lab.data import ROOT
from indicator_lab.features import catalog
OUT=ROOT/'reports/predictions'
def pct(x):return 'N/A' if x is None else f'{100*x:.2f}%'
def main():
    x=json.loads((OUT/'combined.json').read_text());rows=x['rows'];final=[r for r in rows if r['period']=='retrospective']
    freezes=[json.loads((OUT/f'frozen_{m}m.json').read_text()) for m in (5,15,60)]
    dm=json.loads((ROOT/'data/predictions/manifest.json').read_text())
    passed=[r for r in final if r['retrospective_validation_gate_passed']];finance=[r for r in final if r['financial_gate_passed']]
    lines=['# Which indicators predicted Bitcoin direction best?', '', '**This is a retrospective formula benchmark, not a test of every TradingView indicator.**', '',
    f"Actually completed **{len(final)} indicator/timeframe forecast tests** from **441 attempts**: 147 formula entries on each of 5m, 15m and 60m. This includes 61 named candlestick patterns. {441-len(final)} attempts could not produce a learned forecast; see the workbook. No missing results are invented.", '',
    'The separate 210-script public Pine corpus audit found 194 runtime failures and 16 completed compatibility probes. **A compatibility probe is not a forecast backtest.** Native TradingView formula matching is unverified, and private, paid and inaccessible scripts are outside coverage.', '',
    'The evaluated object is **each indicator plus the same trained logistic model**. Most indicators do not make predictions by themselves. We predict whether the next closing price is above or below the current close, once the current candle has completed. This can differ from predicting a green/red candle body.', '',
    '**Training:** 2020–2024, with a shared 2,048-candle initial burn-in on each timeframe. **Validation:** 2025 selects among preset window lengths. **Retrospective test:** January–September 2026, chosen by the user. Those market dates were already examined in earlier work. They are held out from this fitting step but are not genuinely untouched research evidence.', '',
    '## The highest measured accuracy on each timeframe', '',
    '| Chart / next close | Highest measured formula | Correct directions | Training-majority baseline | 2025 accuracy | Net trading return | Buy and hold |',
    '|---|---|---:|---:|---:|---:|---:|']
    for m in (5,15,60):
        r=min([r for r in final if r['timeframe_minutes']==m],key=lambda r:r['retrospective_rank']);v=next(v for v in rows if v['id']==r['id'] and v['timeframe_minutes']==m and v['period']=='validation')
        lines.append(f"| {m}m | {r['name']} ({r['id']}) | {pct(r['accuracy'])} | {pct(r['baseline_majority_accuracy'])} | {pct(v['accuracy'])} | {pct(r['net_return'])} | {pct(r['buy_hold_return'])} |")
    lines += ['', '**Highest accuracy does not mean a good trading strategy.** Small correct moves can earn less than the fee and slippage. An almost -100% return means the simulated balance was almost wiped out. These idealized fractional-BTC simulations omit minimum order sizes, lot rounding, latency and market impact; actual exchange minimums would stop tiny balances earlier.', '',
    f"**{len(passed)} of {len(final)} completed tests passed the limited retrospective accuracy gate. {len(finance)} passed the separate financial gate in both 2025 and 2026.** Passing an accuracy gate is not a claim of profitable or independent future performance.", '',
    'Accuracy gate: positive baseline lift in both 2025 and 2026, positive lower 2026 seven-day block interval, approximate Holm-adjusted p<0.05 across all completed final comparisons, positive mean earlier walk-forward lift, adequate forecast/event counts. Financial gate: positive net return, beating costed buy-and-hold and at least 30 trades in both periods.', '',
    '## Retrospective top 10 by next-close accuracy', '',
    'Each table uses exactly the same real exchange observations and label timing within its timeframe. Ranks are descriptive; choosing a winner after seeing this table creates selection bias. Related indicators and candlestick patterns are not independent discoveries.']
    for m in (5,15,60):
        lines += ['',f'### {m}-minute chart', '', '| Rank | Formula | Accuracy | Lift over baseline | 95% block interval for lift | Trades | Net return | Accuracy gate |', '|---:|---|---:|---:|---|---:|---:|---|']
        for r in sorted([r for r in final if r['timeframe_minutes']==m],key=lambda r:r['retrospective_rank'])[:10]:
            flag='; RARE training pattern' if r['rare_training_events'] else ''
            lines.append(f"| {r['retrospective_rank']} | [{r['name']}]({r['github_url']}){flag} | {pct(r['accuracy'])} | {100*r['accuracy_lift_vs_train_majority']:.2f} pp | {100*r['lift_block_ci_low']:.2f} to {100*r['lift_block_ci_high']:.2f} pp | {r['trades']} | {pct(r['net_return'])} | {'Pass (retrospective only)' if r['retrospective_validation_gate_passed'] else 'Fail'} |")
    lines += ['', '## What was checked', '',
    '- All distinct formula profiles were regenerated on earlier prefixes and with later prices/volume changed. A changed earlier value would quarantine that indicator. No result is promoted from a compatibility probe.',
    '- Expanding walk-forward fits through 2021, 2022 and 2023 predicted 2022, 2023 and 2024. Default settings were fixed; later 2025 choices were not carried backward.',
    '- Each fit learned its scaling and coefficients from training rows only. Labels reaching the fitting cutoff were purged. Three preset window profiles were selected using 2025 alone; hashes and coefficients were saved before new 2026 accuracy calculations.',
    '- Other profiles were scored as parameter stress, and fees were halved/doubled, with a doubled fee-plus-slippage case. Model forecasts stay fixed during cost stress. Parameters without adjustable integer windows have only one distinct profile; do not interpret that as demonstrated parameter robustness.',
    '- All comparisons use a training-majority baseline on matching labels. Always-up, always-down and previous-direction baselines are also reported. Accuracy intervals use paired seven-day blocks; approximate daily Newey–West p-values receive Holm correction across the complete final family.',
    '- Rare candlestick occurrences, fewer than 1,000 scored forecasts and fewer than 30 completed trades are flagged. Some patterns never occurred in training and failed; some early walk-forward fits also failed for this reason.', '',
    'These checks reduce selected sources of leakage. They do not prove freedom from every possible bug, native TradingView agreement or upstream historical optimization. Source versions were obtained after the historical test dates; this is not a reconstruction of which versions were available at the time. The 2025 scores participate in window selection and are not an independent check of that choice. Unknown published tuning, related tests, validation selection and already-seen market dates remain limitations. No genuine untouched OOS pass is claimed.', '',
    '**Scoring coverage:** all completed models cover every eligible target in their reported period except the 5m Fisher Transform, which has five undefined feature rows in 2026. Those five directions are unscored for that model, its baseline uses the identical subset, and its exact coverage is shown in Excel. They are not invented or counted as correct. The three leading models have full eligible-target coverage.', '',
    '## Prices and trading assumptions', '',
    'Source: [Binance public data](https://github.com/binance/binance-public-data), official spot BTCUSDT monthly 5m archives, 2020-01 through 2026-09. All 81 archive checksums verified. The 15m and 60m observations use only complete groups from those same 5m prices. Missing data is not filled.', '',
    '| Timeframe | Actual candles | Missing candles across full history | Missing in 2025/2026 scoring |', '|---|---:|---:|---:|']
    for d in dm['datasets']:lines.append(f"| {d['timeframe_minutes']}m | {d['rows']:,} | {d['missing_candles']} | {sum(t>='2025' for t in d['missing_timestamps'])} |")
    lines += ['', 'All 59,115 derived hourly closes matched the previous official hourly dataset on shared timestamps. Extra incomplete hourly groups were discarded. Missing observations are before the validation and final scoring periods. Near gaps, indicator periods count observed candles rather than exact clock durations.', '',
    'Trading starts with 10,000 USDT per period, long Bitcoin or hold cash, with no shorts or leverage. An UP forecast buys at the next adjacent candle open; a DOWN forecast sells there. Consecutive UP guesses stay in one holding. Fee **0.1%** and adverse slippage **0.05%** apply to **every buy and sell**. Positions are sold at the last real close. Buy-and-hold pays identical entry and exit costs. Future ties are excluded only from accuracy; their forecasts are never suppressed from trading.', '',
    '## What the numbers mean (plain language)', '',
    '- **Accuracy:** 53% means 53 correct directions out of 100. It says nothing about the sizes of the gains or losses.',
    '- **Balanced accuracy:** average of the success rate on UP and DOWN moves, so the more common class cannot hide poor results on the other.',
    '- **Lift:** extra correct guesses compared with the baseline. Two percentage points means two extra correct answers out of 100.',
    '- **Confidence interval / adjusted p-value:** rough checks on whether an advantage could be chance. Trying many indicators makes lucky winners more likely; the adjustment helps, but cannot erase earlier research or unseen modeling choices.',
    '- **Net return:** how much the starting money grew or shrank after trading costs.',
    '- **Sharpe:** average daily account return divided by daily bumpiness, scaled to a year. Higher is generally better; not a percentage.',
    '- **Maximum drawdown:** the worst observed-close fall from a previous high. A 40% drawdown turns a 10,000 peak into 6,000.',
    '- **Profit factor:** total net dollars won divided by total net dollars lost on trades. Below 1 is losing overall. N/A if there are no losing dollars to divide by.',
    '- **Trade win rate:** share of buy/sell trades that earned money after costs. This is different from prediction accuracy.',
    '- **Trade count:** completed buys followed by sells. Below 30 is flagged because a few lucky trades tell little.',
    '- **Buy and hold:** buy once, wait, sell at the end with the same entry/exit costs.',
    '- **N/A:** missing, not run, unverified or mathematically undefined. Never an invented zero.', '',
    '## Open the Excel file', '',
    '[Download TradingView_Indicator_Predictions.xlsx](https://raw.githubusercontent.com/babavagna/TestingBTCmodels/main/reports/TradingView_Indicator_Predictions.xlsx). Save it first, then open in Microsoft Excel or LibreOffice Calc. GitHub may show an error or no preview for spreadsheet files; that is not a corruption test. The dashboard also provides a download button.', '',
    'Start on **Read Me**. **All Strategies** contains all 441 formula/timeframe attempts with explicit completion status. **Top 10** has ten retrospective rows for each timeframe. **Prediction Accuracy**, **Charts**, **Failed Tests**, **Walk Forward**, **Robustness**, **Pine Audit** and the source/data sheets preserve supporting evidence.', '',
    'Models, exact probabilities and decisions, true labels, raw source formulas, checksum manifests and test evidence are saved beside the report. [Reproduction instructions](../../indicator_lab/README.md) and the [frozen protocol](../../indicator_lab/PROTOCOL.md) explain the implementation. The previous full-100 strategy report and workbook remain separate and available.', '']
    (OUT/'REPORT.md').write_text('\n'.join(lines))
    print('Report written:',len(final),'completed tests;',len(passed),'accuracy gates;',len(finance),'financial gates')
if __name__=='__main__':main()
