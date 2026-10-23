"""Beginner-readable narrative derived only from saved expanded execution."""
import json
from pathlib import Path
import pandas as pd
from full_universe.audit import ROOT,OUT,read_report,catalog
from btc_lab.data import sha256,write_json

def make_report():
    inventory,periods,meta=read_report();stress=pd.read_csv(OUT/'sensitivity.csv');wf=pd.read_csv(OUT/'walk_forward.csv');items=catalog()
    def n(v):return 'N/A' if pd.isna(v) else f'{v:.2f}'
    lines=['# Full supplied list: 100-candidate execution and integrity audit','',
      f"**100 candidates attempted; {meta['completed']} completed valid hourly signal backtests; {meta['blocked']} blocked or quarantined.** Original native bots are not fully reproduced. No blocked candidate is reported as successfully tested.",'',
      '**No genuine unseen-data ranking is available.** Earlier project work examined 2025 and January–September 2026. These chronological replays hold those years out of the new fitting step, but cannot restore an untouched test. All tables below are alphabetical diagnostics; no Top 10 winner is claimed. Upstream tuning history is unknown.','',
      'Open [the Excel workbook](../Bitcoin_Strategy_Leaderboard.xlsx) and choose **Read Me**, then **All Strategies**. On GitHub use **Download raw** to save the file. All 100 supplied entries have a row, including failures.','',
      '## Same prices and account rules','',
      '- Binance **spot BTC/USDT, 1-hour candles**, January 2020 through September 2026: 59,129 real candles from 81 official monthly archives. SHA-256 checksums were verified. There are 31 missing hours in 15 gaps before 2025; none are filled. The 2025 and 2026 scoring periods have no missing hours.',
      '- Start each scored period with **10,000 USDT**. Buy Bitcoin or hold cash; no shorts or leverage. Pay **0.1% fee + 0.05% slippage on each side**. A signal from a completed hour trades at the next adjacent hour’s open. An open position is sold at the final close, including costs.',
      '- The account assumes fills at the modeled prices. Order-book liquidity, partial fills, exchange quantity rounding and the intrahour price path are not simulated; these are not proof of real exchange fills.',
      '- These are **signal-only adaptations**. Native profit targets, stoplosses, shorts, leverage, pyramiding and position sizing are omitted. The Freqtrade and Zenbot source hooks run through compatibility adapters. Eight supported Jesse entries are TA-Lib/pandas formula translations; exact native indicator/engine equivalence remains unverified.',
      '- The common initial warmup is **4,096 observed candles**, covering long indicator histories. After that, indicators retain past observations across gaps; their periods count observed bars, not invented hourly rows. The engine forbids a trade across a missing-hour gap and holds any existing position. The first scored training hour is 2020-06-20 01:00 UTC; initial warmup hours are excluded from hourly return samples. Later idle cash hours are included. A gap can stretch a nominal indicator window in calendar time; all candidates receive the same observed prices.',
      '- Training receives only 2020–2024 prices. Each fold records whether its candidates reach 30 completed training trades. A fold with too few trades retains the original profile; that fallback is not claimed as a qualified fit. The long initial warmup reduces the early training sample, but does not repeatedly discard entire years after short data gaps.','',
      '## Training, walk-forward and robustness checks','',
      'Three profiles were declared: original, lower 20%, higher 20%. For Freqtrade, numeric exposed parameters vary; if there are none, explicitly supplied TA-Lib periods vary. For Jesse, documented numeric rule settings vary. For Zenbot, numeric options vary, with the hourly period held fixed. Not every source exposes meaningful settings; duplicate behavior is not evidence of robustness.',
      'Select using **training-only hourly Sharpe with at least 30 trades**, otherwise retain original. Purge the final fitting hour. Fit through 2021 and evaluate 2022; through 2022/evaluate 2023; through 2023/evaluate 2024. Final fitting ends at **2024-12-31 22:00 UTC**, and selected profiles are saved before 2025/2026 scoring. No validation/test score selects parameters.',
      'All completed profiles are stressed with half/base/double fees (slippage 0.05%); the selected profile also gets double fee and double slippage. See [sensitivity.csv](sensitivity.csv), [walk_forward.csv](walk_forward.csv), [training_candidates.csv](training_candidates.csv), and per-candidate frozen selections and trades in [candidates/](candidates/). Losing money is not a software failure.',
      'The [robustness summary](robustness_summary.csv) counts profitable parameter/cost scenarios, their return range, and profitable or benchmark-beating walk-forward folds. These overlapping scenarios are not independent evidence and are not used to pick a test winner.','',
      'A **diagnostic pass** requires positive net return, beating same-period buy and hold, and at least 30 completed trades. This rule was not changed to obtain more winners. It is not a proof of genuine out-of-sample success.','',
      '## Cheating and leakage review','',
      'Each completed profile passed five independently regenerated historical-prefix signal comparisons and one future-price mutation. In a causal rule, adding or changing later candles must not change an earlier decision. These are finite checks, not proof that every possible leak is absent.',
      '**CCIStrategy (#24) and ReinforcedQuickie (#36) were quarantined.** Their published two-sided interpolation changed earlier numerical indicator values when later candles were included. Checking buy/sell signals alone can miss this because an indicator can change without crossing an entry threshold. Numerical examples and cutoffs are saved in each candidate JSON. Their previous intermediate financial files were removed from the valid comparison.',
      '**Overfitting** is like memorizing a practice exam instead of learning the subject. Trying 100 strategies can produce lucky winners. Source selection and published hyperparameters may already reflect optimization over the same history. Neither good walk-forward numbers nor a small parameter grid eliminates that overfitting risk. No significance claim or guarantee of future profit is made.','',
      '## Next-hour directional prediction accuracy','',
      '**Zero forecast models were scored.** Neural (#76) really contains a price predictor, so it is not labeled “no forecast model.” Its native cluster/online-training interface is unsupported by the frozen-training adapter. Accuracy is **N/A — runtime incomplete**, with no fabricated percentage. The native strategy retrains each hour; silently training it on final-test prices would violate the requested separation.',
      'Other evaluated adapters expose trading entry/exit rules, not an explicit next-hour forecast. Buying for a week does not mean predicting the next hour correctly. Trade win rate is not prediction accuracy. A future forecasting implementation needs adjacent-hour targets, timestamped forecasts, ties/coverage, class balance and an always-up baseline.','']
    for period,title in [('validation_2025','2025 validation diagnostics'),('retrospective_test_2026','January–September 2026 diagnostics')]:
        frame=periods[periods.period==period].sort_values('strategy',key=lambda s:s.str.lower());bh=frame.buy_and_hold_return_pct.iloc[0]
        lines += [f'## {title}','',f"**{len(frame)} completed candidates. Buy and hold: {n(bh)}%.** {int(frame.diagnostic_gate_pass.sum())} meet this period’s diagnostic gate. These are previously seen dates, not an untouched ranking.",'',
          '| Strategy | Net return % | Sharpe | Max drawdown % | Profit factor | Win rate % | Trades | Buy/hold % | Sample | Gate |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---|---|']
        for r in frame.itertuples():
            lines.append(f"| {r.strategy} | {n(r.return_pct)} | {n(r.sharpe_ratio)} | {n(r.max_drawdown_pct)} | {n(r.profit_factor)} | {n(r.win_rate_pct)} | {r.trades} | {n(r.buy_and_hold_return_pct)} | {'TOO FEW' if r.trades<30 else '≥30'} | {'PASS' if r.diagnostic_gate_pass else 'FAIL'} |")
        selected={r['strategy_id']:r['variant'] for r in json.loads((OUT/'frozen_selection.json').read_text())}
        s=stress[stress.period==period];both=s[s.cost_case=='double_both'];positive=int(both.return_pct.gt(0).sum())
        lines += ['',f"With **both costs doubled**, {positive}/{len(both)} selected profiles remain profitable. This is a sensitivity check, not a new selection step.",'']
    passed=inventory[inventory.passes_both_diagnostic_gates.fillna(False).astype(bool)] if 'passes_both_diagnostic_gates' in inventory else inventory.iloc[:0]
    lines += [f'**{len(passed)} candidates pass both period-specific diagnostic gates.** No candidate has verified genuinely untouched OOS validation.','',
      '## Failed or incomplete candidates','', '| List # | Candidate | Status | Recorded reason |','|---:|---|---|---|']
    for r in inventory[inventory.status!='completed_signal_backtest'].sort_values('number').itertuples():
        reason=r.reason.replace('\n',' ').replace('|','/');lines.append(f'| {r.number} | {r.strategy} | {r.status} | {reason[:450]} |')
    lines += ['', 'The 120-second limit applies to each complete signal-generation call. A timeout means the calculation did not finish here; it is not evidence that the strategy loses money. Missing runtime adapters mean the original program needs additional integration, not that a replacement model was tested.','',
      '## Metrics explained simply','',
      '- **Net return:** change in your starting money after costs. +20% turns 100 into 120.',
      '- **Sharpe:** average hourly gain compared with bumpiness, scaled to a year using sqrt(8,760). Higher often means a smoother ride; it is not a percentage or a promise. Zero risk-free rate, idle cash hours and first-entry costs are included. Changes spanning missing hours are excluded from this ratio only.',
      '- **Maximum drawdown:** biggest recorded fall from a previous account peak. A 30% fall turns a peak of 100 into 70. Hourly closes miss intrahour losses.',
      '- **Profit factor:** total winning-trade dollars divided by total losing-trade dollars. Above 1 means wins outweighed losses. N/A means no loss dollars to divide by; it does not mean unlimited profit.',
      '- **Win rate:** fraction of completed trades that made money. Many tiny wins can still be wiped out by one big loss.',
      'A positive Sharpe can coexist with a losing compounded balance: average hourly changes and multiplied account growth measure different things. The gap exclusion also changes the Sharpe sample.','',
      '- **Trades:** completed buy/sell pairs. Fewer than 30 is flagged as too little evidence. Zero trades is a measured outcome, with undefined win rate.',
      '- **Buy and hold:** buy once and sell at the end with identical costs. It is the yardstick.',
      '- **Prediction accuracy:** how often a genuine next-hour up/down forecast was correct. Different from trade win rate. No such accuracy was measured here.','',
      '## Reproduce and verify','',
      'Run `bash setup.sh`, then `.venv/bin/python -m full_universe.audit --workers 3`, `.venv/bin/python -m pytest -q --junitxml=reports/test-results.xml`, and `.venv/bin/python -m scripts.export_full_leaderboard`. Node.js 24 and build tools are required for the old native Zenbot indicator libraries. Saved reports open without executing those libraries.',
      'The manifest [run.json](run.json) fingerprints the code, all original sources, dataset and saved outputs. [inventory.csv](inventory.csv) records all 100 attempts. [failed_tests.csv](failed_tests.csv) preserves execution errors. [causality.csv](causality.csv) records executed checks. The same-source price evidence is in [data/manifest.json](../../data/manifest.json).',
      'Data and derived research retain the saved Binance CC BY-NC-SA 4.0 terms; upstream strategy code retains its stated license.','']
    (OUT/'REPORT.md').write_text('\n'.join(lines))
    meta['outputs_sha256']['REPORT.md']=sha256((OUT/'REPORT.md').read_bytes())
    write_json(OUT/'run.json',meta)
    return meta

if __name__=='__main__':print(make_report())
