"""Replace the old 90-entry backlog with measured full-universe statuses."""
import pandas as pd
from full_universe.audit import ROOT,OUT,read_report

def simple_reason(number,status,technical):
    if status=='completed_signal_backtest' and number in (7,23,98):return 'Completed the signal adaptation, but the published long-exit signal is empty/disabled. With native ROI and stops omitted, only the final scheduled liquidation closes a trade; the small sample is not strong evidence.'
    if status=='completed_signal_backtest':return 'Completed the shared hourly long/cash signal backtest and chronology checks. The full native bot is not reproduced.'
    if status=='quarantined_lookahead':return 'Later candles changed earlier indicator values. Excluded because this can make the strategy appear to know the future.'
    if number in (3,4):return 'The source drops real price rows. Its output no longer matches the shared candle clock, so no valid comparison is reported.'
    if 'Timeout' in technical or 'TIMEOUT' in technical:return 'The full calculation did not finish within the declared 120-second signal-call limit. Performance is unknown; this is not evidence that it lost money.'
    if number==53:return 'Needs a properly timed higher-timeframe anchor adapter. Substituting future completed daily prices would be unsafe.'
    if number==62:return 'Needs native trade callbacks, previous-trade state and pyramiding. These are not implemented by the shared signal-only account.'
    if number==76:return 'Contains a real price predictor, but its cluster/online-training interface is unsupported. No frozen-training forecast test or accuracy was executed.'
    if number in (79,80):return 'Reads native account or trade-history state and needs a coupled fill-state adapter. It cannot safely be replaced with an invented account history.'
    return 'Execution was incomplete. Read the preserved technical error in the candidate JSON; no performance is invented.'

def update():
    inventory,_,meta=read_report();lookup=inventory.set_index('number');p=ROOT/'sources/candidate_crosswalk.csv';cross=pd.read_csv(p,keep_default_na=False)
    for idx,row in cross.iterrows():
        n=int(row.list_number);r=lookup.loc[n];tested=r.status=='completed_signal_backtest'
        cross.loc[idx,'testing_status']=r.status
        cross.loc[idx,'performance_available']='YES — completed signal adaptation' if tested else 'NO — no valid completed backtest'
        cross.loc[idx,'native_bot_fully_reproduced']='NO — signal adaptation only' if tested else 'NO — blocked or quarantined'
        cross.loc[idx,'current_review_scope']='Full historical signal, chronology, leakage and sensitivity audit; native execution parity unverified' if tested else 'Source reviewed and execution attempted; see preserved failure evidence'
        cross.loc[idx,'rationale_or_remaining_work']=simple_reason(n,r.status,r.reason)
        cross.loc[idx,'expanded_adapter_id']=r.strategy_id
        cross.loc[idx,'expanded_report_path']=f'reports/full100/candidates/{r.strategy_id}.json'
    cross.to_csv(p,index=False)
    lines=['# Cross-check against the full supplied 100-strategy list','',
       f"All 100 supplied source paths were checked in pinned repository snapshots, and all 100 now have an expanded execution attempt: **{meta['completed']} valid completed signal backtests, {meta['blocked']} blocked or quarantined**.",'',
       'The original ten were a starter set, not winners of a 100-strategy screen. They match supplied entries #17–21, #25, #31–32, #34 and #39. The expanded audit now covers the complete supplied universe.','',
       'Source availability is different from successful execution. Completed rows mean the documented hourly long/cash signal adaptation ran; no full native bot reproduction is claimed. Every blocked strategy has N/A performance.','',
       'See the [full report](full100/REPORT.md), [Excel workbook](Bitcoin_Strategy_Leaderboard.xlsx), [100-row source crosswalk](../sources/candidate_crosswalk.csv), and [original source catalog](../sources/full100/catalog.json).','',
       '## Why any remain excluded','', '| List # | Strategy | Final status | Simple explanation |','|---:|---|---|---|']
    for r in inventory[inventory.status!='completed_signal_backtest'].sort_values('number').itertuples():lines.append(f'| {r.number} | {r.strategy} | {r.status} | {simple_reason(r.number,r.status,r.reason)} |')
    lines += ['', 'CCIStrategy and ReinforcedQuickie have confirmed future-dependent interpolation. Neural is recognized as a native predictor, with an incomplete frozen-training forecast runtime and no invented accuracy. Runtime limits do not prove financial failure.','',
       'No genuine unseen Top 10 is issued: 2025–September 2026 were examined earlier, and upstream optimization is unknown. Formula translations and source signal adapters can differ materially from complete native bots. All measured chronological comparisons are retrospective diagnostics.','']
    (ROOT/'reports/CANDIDATE_CROSSCHECK.md').write_text('\n'.join(lines))
    print(f"Updated source crosswalk: {meta['completed']} completed, {meta['blocked']} blocked/quarantined")

if __name__=='__main__':update()
