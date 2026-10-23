"""Export all 100 candidates, with numbers only for verified completed runs."""
import argparse,json
from pathlib import Path
import pandas as pd
from btc_lab.data import load_verified,write_json,sha256
from full_universe.audit import ROOT,OUT,catalog,read_report,WARMUP
from scripts.export_leaderboard import ExcelReport,junit_summary
from scripts.update_candidate_crosswalk import simple_reason

NOTE='All 100 supplied candidates are included. Numbers describe hourly long/cash signal adaptations, not the full original bots. Blocked and leaking candidates have N/A performance. 2025–2026 were previously seen: no genuine unseen ranks.'
METRICS=[('return_pct','Net return','pct',16),('sharpe_ratio','Sharpe','ratio',12),('max_drawdown_pct','Max drawdown','pct',16),('profit_factor','Profit factor','ratio',14),('win_rate_pct','Win rate','pct',14),('trades','Completed trades','int',14),('buy_and_hold_return_pct','Buy-and-hold return','pct',19)]

def records():
    inventory,periods,meta=read_report();items=catalog();status=inventory.set_index('strategy_id');rows=[]
    robust=pd.read_csv(OUT/'robustness_summary.csv')
    frozen={r['strategy_id']:r for r in json.loads((OUT/'frozen_selection.json').read_text())}
    for item in items:
        sid=item['id'];s=status.loc[sid];p=periods[(periods.strategy_id==sid)&(periods.period=='retrospective_test_2026')];v=periods[(periods.strategy_id==sid)&(periods.period=='validation_2025')]
        completed=s.status=='completed_signal_backtest'
        row=dict(number=item['number'],strategy_id=sid,strategy=item['name'],framework=item['framework'],execution=s.status,source_url=item['source_url'],source_sha256=item['source_sha256'],reason=simple_reason(item['number'],s.status,s.reason),technical_reason=s.reason,
            period='2026 Jan–Sep retrospective diagnostic' if completed else 'N/A — no valid scored run',start=pd.Timestamp('2026-01-01',tz='UTC') if completed else None,last=pd.Timestamp('2026-09-30T23:00Z') if completed else None,deadline=pd.Timestamp('2026-10-01',tz='UTC') if completed else None,
            fee=.001,slippage=.0005,initial_cash=10000,warmup=WARMUP,data='Binance Vision spot BTCUSDT, 1h; checksum-verified monthly archives',data_url='https://data.binance.vision/?prefix=data/spot/monthly/klines/BTCUSDT/1h/',
            assumptions='Signals at completed close; fill next adjacent open; long/cash all-in; no native shorts, leverage, ROI, stops or pyramiding; final close liquidation',
            gaps='31 hours missing before 2025; no filling; indicators retain observed history across gaps. Zero missing hours in 2025/2026.',
            genuinely_untouched='NO — historical prices already inspected',unseen_rank='NOT ISSUED',accuracy=s.directional_forecast_status,forecasts_scored=0,
            forecasts_available='YES — native neural price predictor; not yet supported by the frozen-training runtime' if item['number']==76 else 'No supported explicit next-hour forecast',
            oos_validation='UNVERIFIED — previous holdout exposure and unknown upstream tuning',
            gate_2025='PASS — retrospective diagnostic only' if completed and s.validation_2025_gate_pass else ('FAIL — retrospective diagnostic' if completed else 'N/A — not executed'),
            both_gates='PASS — retrospective only' if completed and s.passes_both_diagnostic_gates else ('FAIL — diagnostic criterion' if completed else 'N/A — not executed'),
            completed_profiles=s.get('completed_profiles'),parameter_check='All three profiles completed' if completed and s.get('completed_profiles')==3 else 'INCOMPLETE — inspect Failed Tests',causality=s.get('causality_status','N/A — run did not complete'),checks=int(s.dynamic_checks_executed),failed_checks=int(s.dynamic_checks_failed),native=False,
            implementation_scope='TA-Lib/pandas formula translation; native indicator/engine parity not fully verified' if item['framework']=='jesse' else ('Long-side spot projection of a futures source; native shorts, leverage and risk management omitted' if '/futures/' in item['source_path'] else 'Unchanged published signal hooks; standalone framework compatibility adapter; not a native engine reproduction'),
            last_training=pd.Timestamp(frozen[sid]['last_fit_candle']) if sid in frozen else None,profile=frozen.get(sid,{}).get('variant','N/A'),parameters=json.dumps(frozen.get(sid,{}).get('parameters',{})),
            validation_return_pct=v.iloc[0].return_pct if len(v) else None,
            low_trades='CAUTION — fewer than 30 trades' if len(p) and p.iloc[0].trades<30 else ('Not flagged; count alone proves nothing' if len(p) else 'N/A — no valid run'))
        for key,_,_,_ in METRICS:row[key]=p.iloc[0][key] if len(p) else None
        r=robust[robust.strategy_id.eq(sid)&robust.period.eq('retrospective_test_2026')]
        row['profitable_scenarios']=f"{int(r.iloc[0].profitable_scenarios)}/{int(r.iloc[0].completed_scenarios)}" if len(r) else None
        for key in ('lowest_return_pct','highest_return_pct','selected_double_cost_return_pct','profitable_walk_forward_folds','beat_hold_walk_forward_folds'):
            row[key]=r.iloc[0][key] if len(r) else None
        rows.append(row)
    return rows,meta

def table_from_csv(writer,name,path):
    frame=pd.read_csv(path)
    writer.banner(name,name,NOTE)
    columns=[]
    for key in frame.columns:
        kind='pct' if key.endswith('_pct') else 'ratio' if key in ('sharpe_ratio','profit_factor') else 'int' if key in ('trades','sharpe_hourly_samples') else 'rate' if key in ('fee_per_side','slippage_per_side') else 'text'
        columns.append((key,key.replace('_',' '),kind,18 if kind!='text' else 27))
    writer.table(name,columns,frame.to_dict('records'))

def export(path=None):
    rows,meta=records();_,data_meta=load_verified(ROOT)
    path=Path(path or ROOT/'reports/Bitcoin_Strategy_Leaderboard.xlsx');path.parent.mkdir(exist_ok=True,parents=True)
    temporary=path.with_name(path.stem+'.building.xlsx')
    w=ExcelReport(temporary)
    read=w.banner('Read Me','Bitcoin Strategy Lab — full 100-candidate list',NOTE)
    explanations=[('Scope',f"100 candidates attempted; {meta['completed']} completed valid signal backtests; {meta['blocked']} blocked or quarantined. No failed strategy is counted as tested."),
      ('Overfitting','Like memorizing a practice exam instead of learning the subject. Trying 100 strategies can produce lucky historical winners; later checks and fee stresses do not remove that risk.'),
      ('Look-ahead / leakage','Using a later price to help an earlier decision is like seeing an exam answer before taking the test. Prefix and future-mutation checks look for that problem.'),
      ('Out-of-sample','Prices kept out of this run’s parameter fitting. Genuinely untouched means they were not inspected earlier either; that stronger condition is unavailable for these historical dates.'),
      ('Training','2020–2024 only. Three fixed parameter profiles; select highest training Sharpe with at least 30 trades; otherwise keep original. Last fitting candle: 2024-12-31 22:00 UTC. No fitting on 2025/2026.'),
      ('Walk forward','Fit through 2021, replay 2022; fit through 2022, replay 2023; fit through 2023, replay 2024. Each scored period starts with fresh 10,000 USDT.'),
      ('Test honesty','2025 and Jan–Sep 2026 were examined earlier. They are held out from this fitting step but cannot be called untouched. Upstream tuning and selection bias remain unknown. Top 10 has no eligible ranks.'),
      ('Shared costs','0.1% trading fee and 0.05% slippage on EVERY buy and sell; same Binance spot BTCUSDT hourly candles; no leverage.'),
      ('Warmup',f'{WARMUP} observed candles initially, shared by all candidates. History is retained across gaps; periods count observed bars. No execution across a gap, no invented prices. The first scored training hour is 2020-06-20 01:00 UTC; initial warmup hours are excluded from hourly return samples. Later idle cash hours are included.'),
      ('Net return','How much the starting money grew after trading costs. +20% means 100 became 120.'),
      ('Sharpe','Average hourly reward compared with how bumpy hourly changes are, scaled by sqrt(8760). Higher usually means smoother reward; it is not a percentage or a promise. Idle hours and first-entry costs are included; multi-hour gaps excluded from this ratio.'),
      ('Maximum drawdown','Biggest recorded fall from an earlier account peak. A 30% drawdown means a peak of 100 fell to 70. Hourly closes cannot show every intrahour loss.'),
      ('Profit factor','All money won on winning trades divided by all money lost on losing trades, after costs. 1.5 means 1.50 won for each 1 lost. N/A when there are no losing-trade dollars.'),
      ('Win rate','Share of completed trades that made money. Many small wins can still be outweighed by a big loss.'),
      ('Trades / few trades','Completed buy-and-sell pairs. Fewer than 30 is a warning, like judging a player after too few games. Zero trades is a real outcome.'),
      ('Buy and hold','Buy once at the same scoring start and sell at the end, with the same costs. This is the yardstick.'),
      ('Prediction accuracy','Share of explicit next-hour up/down forecasts that are correct. It is different from trade win rate. Neural has a native predictor, but its frozen-training forecasting runtime is incomplete; no forecast accuracy was measured.'),
      ('Diagnostic gate','Pass only if return is positive, exceeds buy and hold, and includes at least 30 completed trades. Passing is descriptive and does not establish untouched out-of-sample success.'),
      ('Sensitivity','Original settings and fixed ±20% neighbors where supported, tested with half/base/double fee; selected profile also has doubled fee AND slippage. Neighbor errors are retained; they are never replaced with winning guesses.'),
      ('Leakage checks','For each completed profile, five independently regenerated past prefixes and one future-price mutation. Failures quarantine the entire original strategy. Finite checks do not prove every possible absence of cheating.'),
      ('Execution limits','The simulator assumes orders can fill at modeled prices. It does not model order-book liquidity, partial fills, quantity rounding or the price path inside an hour. Results are not proof of real exchange fills.'),
      ('Source limitations','Freqtrade/Zenbot: published source hooks executed through compatibility adapters. Supported Jesse: documented TA-Lib/pandas formula translations; exact native parity unverified. Original stops, targets, shorts and position sizing are omitted; these are not the full published bots.'),
      ('Data gaps','59,129 observed candles; 81 verified monthly archives. 31 hours missing in 15 gaps before 2025. All missing timestamps are in data/manifest.json. No gaps in 2025 or 2026 scoring periods.'),
      ('Files','All Strategies: one row per supplied candidate, 2026 diagnostics where valid. Period Results: both years. Failed Tests: runtime/leakage and financial criteria separated. Source paths and hashes are preserved.'),
      ('Percentage caution','A positive Sharpe can coexist with a negative net return: Sharpe averages hourly simple changes, while the account compounds gains and losses. Gap-crossing returns are excluded from Sharpe only.'),
      ('Data license','Binance data and derived research: CC BY-NC-SA 4.0, subject to saved source terms. Strategy code retains its upstream license.'),
      ('Results manifest','reports/full100/run.json verifies model, source, data and every saved output. N/A is missing or undefined; it is never zero.')]
    for row,(label,value) in enumerate(explanations,7):w.value(read,row,0,label);w.value(read,row,1,value);read.set_row(row,65)
    read.set_column(0,0,24);read.set_column(1,1,110)
    columns=[('number','List #','int',8),('strategy','Strategy','text',26),('execution','Execution status','text',29)]+METRICS+[
      ('low_trades','Sample flag','text',28),('profitable_scenarios','Profitable 2026 stress cases','text',24),('lowest_return_pct','Lowest stress return','pct',20),('highest_return_pct','Highest stress return','pct',20),('selected_double_cost_return_pct','Selected double-cost return','pct',24),('profitable_walk_forward_folds','Profitable walk-forward folds out of 3','int',27),('beat_hold_walk_forward_folds','Beat hold walk-forward folds out of 3','int',27),('validation_return_pct','2025 net return','pct',17),('gate_2025','2025 validation gate','text',34),('both_gates','Passed both diagnostic gates','text',30),('oos_validation','Genuine OOS validation','text',42),('unseen_rank','Unseen rank','text',17),
      ('source_url','Original GitHub strategy URL','url',55),('framework','Framework','text',15),('start','Test start UTC','date',21),('last','Last input hour UTC','date',21),('deadline','Final close deadline UTC','date',23),('last_training','Last training candle UTC','date',23),
      ('data','Historical data source','text',48),('data_url','Official data URL','url',55),('fee','Trading fee per side','rate',18),('slippage','Slippage per side','rate',18),('initial_cash','Initial cash USDT','money',18),('warmup','Warmup candles','int',18),('profile','Selected profile','text',22),('completed_profiles','Completed profiles out of 3','int',22),('parameter_check','Parameter check coverage','text',35),('parameters','Parameters / factor','text',50),
      ('accuracy','Directional accuracy','text',55),('forecasts_available','Forecast capability','text',48),('checks','Dynamic checks','int',16),('failed_checks','Failed dynamic checks','int',19),('causality','Causality audit','text',48),('implementation_scope','Implementation scope','text',65),('native','Full native bot reproduced?','text',23),('assumptions','Trading assumptions','text',75),('gaps','Missing data','text',60),('reason','Completion / failure explanation','text',80),('technical_reason','Preserved technical status','text',90),('source_sha256','Original source SHA-256','text',67)]
    w.banner('All Strategies','All 100 supplied candidates — status and 2026 diagnostics',NOTE);w.table('All Strategies',columns,rows)
    w.banner('Top 10','Top 10 — no eligible untouched-data ranks','The requested historical test was already inspected. A replay cannot undo that exposure. No top ten is claimed.')
    w.table('Top 10',[('strategy','Strategy','text',28),('unseen_rank','Genuine unseen rank','text',22),('genuinely_untouched','Eligible?','text',55),('execution','Execution status','text',32)],rows)
    w.banner('Prediction Accuracy','Prediction accuracy — separately audited','No next-hour forecast accuracy was executed. Trading buy/sell signals are not predictions. Neural is explicitly marked as an unsupported forecast runtime.')
    w.table('Prediction Accuracy',[('number','List #','int',9),('strategy','Strategy','text',27),('forecasts_available','Provides forecasts?','text',65),('accuracy','Directional accuracy','text',90),('forecasts_scored','Forecasts scored','int',18),('source_url','GitHub source','url',65)],rows)
    failures=pd.read_csv(OUT/'failed_tests.csv').to_dict('records')
    for row in failures:
        row['category']='Runtime or causality failure';row['status']='FAILED / BLOCKED'
        row['technical_error']=row['error']
        sid=row['strategy_id'];source_row=next(r for r in rows if r['strategy_id']==sid)
        row['error']=source_row['reason']
    for r in pd.read_csv(OUT/'period_results.csv').to_dict('records'):
        if not r['diagnostic_gate_pass']:failures.append(dict(category='Financial diagnostic criterion',strategy_id=r['strategy_id'],variant=r['variant'],stage=r['period'],status='FAIL — investment criterion, not software',error=f"Return {r['return_pct']:.4f}%; buy/hold {r['buy_and_hold_return_pct']:.4f}%; trades {r['trades']}. Requires positive return, beat buy/hold and >=30 trades."))
    failures.extend([dict(category='Data limitation',status='MISSING',error='31 actual hours missing before 2025; not filled.'),dict(category='Validation limitation',status='UNVERIFIED',error='Previously inspected 2025–2026 and unknown upstream optimization; no genuine untouched test.'),dict(category='Prediction limitation',strategy_id='s076',status='NOT EXECUTED',error='Neural forecasting runtime incomplete. Accuracy N/A; zero forecasts scored.')])
    software=junit_summary(ROOT/'reports/test-results.xml')
    for f in software['failures']:failures.append(dict(category='Software test',status='FAIL',error=f['explanation']))
    w.banner('Failed Tests','Failures and limitations','Runtime and leakage failures are separated from a strategy losing money. Missing results are not replaced with zero.')
    w.table('Failed Tests',[(k,k.replace('_',' ').title(),'text',25 if k!='error' else 110) for k in ['category','strategy_id','variant','stage','status','error','technical_error']],failures)
    for name,file in [('Walk Forward','walk_forward.csv'),('Sensitivity','sensitivity.csv'),('Training Fits','training_candidates.csv')]:table_from_csv(w,name,OUT/file)
    # Extra worksheets keep both scored periods and the detailed causal evidence.
    for name,file in [('Period Results','period_results.csv'),('Causality Audit','causality.csv'),('Robustness Summary','robustness_summary.csv')]:
        w.sheets[name]=w.book.add_worksheet(name);table_from_csv(w,name,OUT/file)
    months=data_meta['months']
    source_rows=[dict(month=m,**v) for m,v in months.items()] if isinstance(months,dict) else months
    w.banner('Data Sources','Official monthly archives — verified checksums','Same 81 monthly archives and same prices for every strategy. Complete gap list: data/manifest.json.')
    keys=sorted(set().union(*(r.keys() for r in source_rows)))
    w.table('Data Sources',[(k,k.replace('_',' ').title(),'url' if 'url' in k else 'text',55 if 'url' in k or 'sha256' in k else 24) for k in keys],[{k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in source_rows])
    # Charts contain every successful strategy, alphabetically, with buy/hold.
    chart_rows=sorted([r for r in rows if r['execution']=='completed_signal_backtest'],key=lambda r:r['strategy'].lower())
    bench=pd.read_csv(OUT/'benchmark.csv').query("period=='retrospective_test_2026'").iloc[0]
    chart_rows.append(dict(strategy='Buy and hold (reference)',return_pct=bench.return_pct,max_drawdown_pct=bench.max_drawdown_pct,sharpe_ratio=bench.sharpe_ratio,trades=bench.trades))
    w.banner('Chart Data','Chart data — saved executed results',NOTE)
    w.table('Chart Data',[('strategy','Strategy','text',30),('return_pct','2026 net return','pct',20),('max_drawdown_pct','2026 max drawdown','pct',22),('sharpe_ratio','2026 Sharpe','ratio',18),('trades','Completed trades','int',19)],chart_rows)
    charts=w.banner('Charts','Executed 2026 diagnostics — alphabetical, no ranks',NOTE)
    for j,(col,title) in enumerate([(1,'Net return after costs'),(2,'Maximum drawdown'),(3,'Hourly Sharpe ratio'),(4,'Completed trades (under 30: small sample)')]):
        chart=w.book.add_chart({'type':'bar'});chart.add_series({'name':title,'categories':['Chart Data',8,0,7+len(chart_rows),0],'values':['Chart Data',8,col,7+len(chart_rows),col]});chart.set_title({'name':title+' — retrospective 2026'});chart.set_legend({'none':True});chart.set_size({'width':1050,'height':max(600,len(chart_rows)*19)});chart.set_y_axis({'reverse':True});
        if col in (1,2):chart.set_x_axis({'num_format':'0%'})
        charts.insert_chart(8+j*(len(chart_rows)+12),0,chart)
    w.book.set_properties({'title':'Bitcoin Strategy Lab: full 100-candidate audit','comments':NOTE});w.book.close()
    temporary.replace(path)
    metadata=dict(created_at=meta['created_at'],workbook_sha256=sha256(path.read_bytes()),all_candidates=100,completed_strategy_backtests=meta['completed'],blocked_candidates=meta['blocked'],eligible_top_10=0,forecast_models_scored=0,software_tests=software,input_manifest_sha256=sha256((OUT/'run.json').read_bytes()),exporter_sha256=sha256(Path(__file__).read_bytes()),sheets=list(w.sheets))
    write_json(path.with_suffix('.json'),metadata)
    return metadata

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output');args=p.parse_args();print(json.dumps(export(args.output),indent=2))
