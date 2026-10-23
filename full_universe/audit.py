"""Execute and audit the complete user-supplied universe, without invented ranks."""
import argparse,contextlib,hashlib,json,os,signal,sys,time,traceback,warnings
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import numpy as np
import pandas as pd
from btc_lab.data import load_verified,sha256,utc_now,write_json,DataError
from btc_lab.engine import backtest,Costs
from btc_lab.robustness import static_findings,choose_candidate
from btc_lab.runner import implementation_hash
from full_universe.adapters import ROOT,WARMUP,prepared,parameters

OUT=ROOT/'reports/full100'
PROFILES={'original':1.,'lower_20pct':.8,'higher_20pct':1.2}
PERIODS={'validation_2025':('2025-01-01','2026-01-01'),'retrospective_test_2026':('2026-01-01','2026-10-01')}
CUTS=['2022-01-01','2023-01-01','2024-01-01','2025-01-01','2026-01-01']

def catalog():
    items=json.loads((ROOT/'sources/full100/catalog.json').read_text())
    if len(items)!=100 or len({i['id'] for i in items})!=100:raise DataError('Expected 100 distinct supplied candidates')
    for i in items:
        if sha256((ROOT/i['source_path']).read_bytes())!=i['source_sha256']:raise DataError('Original source checksum changed: '+i['id'])
    return items

def signals_hash():
    h=hashlib.sha256(implementation_hash(ROOT).encode())
    h.update((ROOT/'sources/full100/catalog.json').read_bytes())
    h.update((ROOT/'requirements.txt').read_bytes())
    for name in ('adapters.py','freqtrade_adapter.py','jesse_adapter.py','zenbot_runner.cjs'):
        h.update((ROOT/'full_universe'/name).read_bytes())
    for path in sorted((ROOT/'sources/full100/zenbot/lib').glob('*.js')):h.update(path.name.encode()+path.read_bytes())
    h.update((ROOT/'sources/full100/zenbot/package-lock.json').read_bytes())
    return h.hexdigest()

def code_hash():
    h=hashlib.sha256(signals_hash().encode())
    h.update(Path(__file__).read_bytes())
    h.update((ROOT/'full_universe/source_review.py').read_bytes())
    return h.hexdigest()

@contextlib.contextmanager
def timeout(seconds=120):
    def fail(*_):raise TimeoutError(f'Signal generation exceeded the declared {seconds}-second per-call limit')
    old=signal.signal(signal.SIGALRM,fail);signal.setitimer(signal.ITIMER_REAL,seconds)
    try:yield
    finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)

def checked_signals(item,data,factor):
    with timeout():return prepared(item,data,factor)

def period_run(data,prepared_signals,start,stop,costs=Costs()):
    start=pd.Timestamp(start,tz='UTC') if isinstance(start,str) else start
    stop=pd.Timestamp(stop,tz='UTC') if isinstance(stop,str) else stop
    prefix=data.loc[data.index<stop]
    if prepared_signals is None:
        en=pd.Series(False,index=prefix.index);ex=en.copy()
        first=max(WARMUP,int(prefix.index.searchsorted(start)))
        if first>=len(prefix)-1:raise DataError('Not enough evaluation candles')
        en.iloc[first-1]=True
    else:en,ex=(s.loc[prefix.index] for s in prepared_signals)
    return backtest(prefix,en,ex,warmup=WARMUP,trade_start=start,costs=costs)

def record(stats,*,item,period,variant,start,stop,**extra):
    return dict(strategy_id=item['id'],strategy=item['name'],period=period,variant=variant,
                start=str(start),stop_exclusive=str(stop),execution_status='completed',
                too_few_trades=stats['trades']<30,**stats,**extra)

def run_one(item):
    warnings.filterwarnings('ignore')
    data,manifest=load_verified(ROOT);sid=item['id'];out=OUT/'candidates';out.mkdir(exist_ok=True)
    cache=OUT/'cache';cache.mkdir(exist_ok=True)
    identity=sha256((signals_hash()+item['source_sha256']+manifest['dataset_sha256']).encode())
    status=dict(strategy_id=sid,strategy=item['name'],number=item['number'],framework=item['framework'],source_url=item['source_url'],
                native_execution_reproduced=False,unseen_rank_eligible=False,historical_test_previously_seen=True,
                native_parameter_optimization_provenance='unknown',signal_identity=identity)
    fits=[];walk=[];periods=[];stress=[];checks=[];errors=[];profiles={};selected=None
    tick=time.monotonic()
    try:
        for name,factor in PROFILES.items():
            cachefile=cache/f'{sid}_{name}.pkl'
            metadata=cache/f'{sid}_{name}.json'
            try:
                if cachefile.exists() and metadata.exists() and json.loads(metadata.read_text()).get('identity')==identity and json.loads(metadata.read_text()).get('file_hash')==sha256(cachefile.read_bytes()):
                    raw=pd.read_pickle(cachefile);full=(raw.entry,raw.exit)
                    previous=json.loads(metadata.read_text());checks.extend(previous['checks'])
                else:
                    full=checked_signals(item,data,factor);profile_checks=[]
                    for cutstr in CUTS:
                        stop=pd.Timestamp(cutstr,tz='UTC')-pd.Timedelta(hours=1)
                        prefix=data.loc[data.index<stop]
                        actual=checked_signals(item,prefix,factor)
                        equal=all(a.equals(b.loc[prefix.index]) for a,b in zip(actual,full))
                        profile_checks.append(dict(strategy_id=sid,variant=name,check='prefix',cutoff=cutstr,passed=equal))
                    changed=data.copy();cut=pd.Timestamp('2026-01-01',tz='UTC');future=changed.index>=cut
                    changed.loc[future,['open','high','low','close']]*=3.7;changed.loc[future,'volume']*=.23
                    altered=checked_signals(item,changed,factor);past=data.index<cut
                    equal=all(a.loc[past].equals(b.loc[past]) for a,b in zip(altered,full))
                    profile_checks.append(dict(strategy_id=sid,variant=name,check='future_price_mutation',cutoff=str(cut),passed=equal))
                    checks.extend(profile_checks)
                    if not all(r['passed'] for r in profile_checks):raise DataError('LOOKAHEAD_DETECTED: later candles changed earlier trading signals')
                    pd.DataFrame(dict(entry=full[0],exit=full[1])).to_pickle(cachefile)
                    write_json(metadata,dict(identity=identity,file_hash=sha256(cachefile.read_bytes()),checks=profile_checks))
                if not all(r['passed'] for r in checks if r['variant']==name):raise DataError('LOOKAHEAD_DETECTED in saved prefix checks')
                profiles[name]=full
            except Exception as e:
                errors.append(dict(strategy_id=sid,variant=name,stage='signals_and_causality',error=type(e).__name__+': '+str(e),traceback=traceback.format_exc()))
                if name=='original':raise
        if not profiles:raise DataError('No causal signal profile completed')
        from full_universe.source_review import indicator_proof
        proof=indicator_proof(item,data) if item['framework']=='freqtrade' else dict(findings=[],checked=False,changed_cells=0)
        status['indicator_review']=json.dumps(proof)
        if proof['changed_cells']:
            checks.append(dict(strategy_id=sid,variant='original',check='numerical_indicator_prefix',cutoff=proof['cutoff'],passed=False))
            raise DataError('LOOKAHEAD_DETECTED: published two-sided interpolation changed '+str(proof['changed_cells'])+' earlier indicator cells when future candles were added; original signals are quarantined even if a threshold did not cross')
        static=static_findings(ROOT/item['source_path']) if item['framework']!='zenbot' else []
        status['static_findings']=json.dumps(static)
        status['causality_status']='prefix_and_mutation_checks_passed; limited audit, not proof'
        # Every fit uses an independently regenerated, purged historical prefix.
        # Cache prefixes above were verified exactly equal, making reuse valid.
        for year in (2022,2023,2024,2025):
            stop=pd.Timestamp(f'{year}-01-01',tz='UTC');purged=stop-pd.Timedelta(hours=1)
            rows=[]
            for name,sigs in profiles.items():
                stats,_,_=period_run(data,sigs,'2020-01-01',purged)
                row=record(stats,item=item,period=f'fit_before_{year}',variant=name,start='2020-01-01',stop=purged)
                rows.append(row);fits.append(row)
            chosen,reason=choose_candidate(rows)
            if chosen not in profiles:chosen='original'
            if year==2025:
                selected=dict(strategy_id=sid,variant=chosen,parameters=parameters(item,PROFILES[chosen]) or {'explicit_talib_period_multiplier':PROFILES[chosen]},last_fit_candle=(purged-pd.Timedelta(hours=1)).isoformat(),selection_reason=reason)
                # Save the freeze BEFORE accessing either later performance.
                write_json(out/f'{sid}_frozen.json',selected)
            else:
                stats,_,_=period_run(data,profiles[chosen],f'{year}-01-01',f'{year+1}-01-01')
                walk.append(record(stats,item=item,period=f'walk_forward_{year}',variant=chosen,start=f'{year}-01-01',stop=f'{year+1}-01-01'))
        for period,(start,stop) in PERIODS.items():
            stats,equity,trades=period_run(data,profiles[selected['variant']],start,stop)
            bh,_,_=period_run(data,None,start,stop)
            row=record(stats,item=item,period=period,variant=selected['variant'],start=start,stop=stop,
                       buy_and_hold_return_pct=bh['return_pct'],diagnostic_gate_pass=bool(stats['return_pct']>0 and stats['return_pct']>bh['return_pct'] and stats['trades']>=30))
            periods.append(row)
            trades.to_csv(out/f'{sid}_{period}_trades.csv',index=False)
            equity.resample('D').last().to_csv(out/f'{sid}_{period}_daily_equity.csv')
            # All completed parameter neighbors, base fee + two fee stresses.
            for variant,sigs in profiles.items():
                for fee,slip,label in ((.0005,.0005,'half_fee'),(.001,.0005,'base'),(.002,.0005,'double_fee')):
                    stats,_,_=period_run(data,sigs,start,stop,Costs(fee,slip))
                    stress.append(record(stats,item=item,period=period,variant=variant,start=start,stop=stop,fee_per_side=fee,slippage_per_side=slip,cost_case=label))
            stats,_,_=period_run(data,profiles[selected['variant']],start,stop,Costs(.002,.001))
            stress.append(record(stats,item=item,period=period,variant=selected['variant'],start=start,stop=stop,fee_per_side=.002,slippage_per_side=.001,cost_case='double_both'))
        status.update(status='completed_signal_backtest',completed_profiles=len(profiles),validation_2025_gate_pass=periods[0]['diagnostic_gate_pass'],test_2026_gate_pass=periods[1]['diagnostic_gate_pass'],passes_both_diagnostic_gates=all(r['diagnostic_gate_pass'] for r in periods),reason='Completed under shared long/cash signal-projection assumptions; not a native bot or untouched OOS validation.')
    except Exception as e:
        status.update(status='quarantined_lookahead' if 'LOOKAHEAD' in str(e) else 'blocked_execution',reason=type(e).__name__+': '+str(e))
        # Remove earlier successful artifacts if a stronger audit quarantines them.
        for stale in out.glob(sid+'_*.csv'):stale.unlink()
        frozen_path=out/f'{sid}_frozen.json'
        if frozen_path.exists():frozen_path.unlink()
        # No partial / invalid performance can reach the comparison tables.
        fits=[];walk=[];periods=[];stress=[];selected=None
        if not errors:errors.append(dict(strategy_id=sid,variant='original',stage='execution',error=status['reason'],traceback=traceback.format_exc()))
    status['protocol_signal_hash']=signals_hash()
    status['elapsed_seconds']=round(time.monotonic()-tick,2)
    status['dynamic_checks_executed']=len(checks);status['dynamic_checks_failed']=sum(not r['passed'] for r in checks)
    status['directional_forecast_status']='N/A — model runtime incomplete; native neural predictor requires a separate frozen-training forecast adapter' if item['number']==76 else 'N/A — no explicit next-hour directional forecast interface in this adaptation'
    result=dict(status=status,training=fits,walk_forward=walk,period_results=periods,sensitivity=stress,checks=checks,errors=errors,frozen=selected)
    write_json(out/f'{sid}.json',result)
    return sid,status['status'],status.get('reason','')[:180]

def execute(workers=3,only=None):
    OUT.mkdir(exist_ok=True);items=catalog();data,manifest=load_verified(ROOT)
    if data.index[0]!=pd.Timestamp('2020-01-01',tz='UTC') or data.index[-1]!=pd.Timestamp('2026-09-30T23:00:00Z'):
        raise DataError('This fixed-date audit requires actual coverage from 2020-01-01 through 2026-09-30 23:00 UTC; available '+str(data.index[0])+' through '+str(data.index[-1])+'. No missing end dates will be invented.')
    write_json(OUT/'protocol.json',dict(created_at=utc_now(),data_sha256=manifest['dataset_sha256'],profiles=PROFILES,train='2020–2024',validation='2025',retrospective_test='2026-01-01 through 2026-09-30 UTC',warmup_candles=WARMUP,
        execution='Completed signal -> next adjacent open; all-in long/cash; no shorts/leverage/native ROI/stoploss/pyramiding; final close liquidation; 10,000 USDT fresh cash each scored period',
        fee_per_side=.001,slippage_per_side=.0005,gaps='No filling; no execution across gaps; indicator periods count observed candles, with history retained across gaps; positions held; one shared initial 4096-observation warmup',
        minimum_trades=30,diagnostic_gate='positive return AND beat buy/hold AND at least 30 completed trades',
        genuinely_untouched=False,ranking='No genuinely unseen ranks: 2025–2026 were inspected in earlier work. All comparisons are retrospective diagnostics.',
        source_history='All source snapshots fixed before this expanded execution; upstream parameter tuning provenance is unknown; all 100 candidates are selected retrospectively',
        limits='Signal adaptations, not full native bot reproductions. TA-Lib/pandas translations for supported Jesse rules; some native hooks cannot run under a common spot signal interface. Prefix checks are finite tests, not a mathematical proof.'))
    chosen=[i for i in items if only is None or i['id'] in only]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(run_one,i) for i in chosen]
        for f in as_completed(futures):print(*f.result(),flush=True)
    aggregate()

def aggregate():
    items=catalog();results=[]
    for item in items:
        p=OUT/'candidates'/f"{item['id']}.json"
        if p.exists():
            r=json.loads(p.read_text())
            if r['status'].get('protocol_signal_hash')==signals_hash():results.append(r)
    # Partial runs remain visibly partial; export requires all 100 attempts.
    for key,file in [('status','inventory.csv'),('training','training_candidates.csv'),('walk_forward','walk_forward.csv'),('period_results','period_results.csv'),('sensitivity','sensitivity.csv'),('checks','causality.csv'),('errors','failed_tests.csv')]:
        rows=[r[key] for r in results] if key=='status' else [v for r in results for v in r[key]]
        pd.DataFrame(rows).to_csv(OUT/file,index=False)
    write_json(OUT/'frozen_selection.json',[r['frozen'] for r in results if r['frozen']])
    # Buy/hold is run separately with the identical scoring boundaries and costs.
    data,manifest=load_verified(ROOT);bench=[]
    for period,(start,stop) in PERIODS.items():
        stats,eq,tr=period_run(data,None,start,stop)
        bench.append(dict(period=period,start=start,stop_exclusive=stop,**stats));eq.resample('D').last().to_csv(OUT/f'buy_hold_{period}_daily.csv')
    pd.DataFrame(bench).to_csv(OUT/'benchmark.csv',index=False)
    walk=pd.read_csv(OUT/'walk_forward.csv')
    training=pd.read_csv(OUT/'training_candidates.csv')
    if len(walk):
        for year in (2022,2023,2024):
            stats,_,_=period_run(data,None,f'{year}-01-01',f'{year+1}-01-01')
            which=walk.period.eq(f'walk_forward_{year}')
            walk.loc[which,'buy_and_hold_return_pct']=stats['return_pct']
            fitted=training[training.period.eq(f'fit_before_{year}')]
            qualified=set(fitted.loc[(fitted.trades>=30)&fitted.sharpe_ratio.notna(),'strategy_id'])
            walk.loc[which,'qualified_training_fit']=walk.loc[which,'strategy_id'].isin(qualified)
        walk.to_csv(OUT/'walk_forward.csv',index=False)
    stress=pd.read_csv(OUT/'sensitivity.csv')
    bh={r['period']:r['return_pct'] for r in bench}
    robust=[]
    for (sid,period),cases in stress.groupby(['strategy_id','period']):
        wf=walk[walk.strategy_id.eq(sid)]
        doubled=cases[cases.cost_case.eq('double_both')]
        robust.append(dict(strategy_id=sid,strategy=cases.strategy.iloc[0],period=period,
            completed_scenarios=len(cases),expected_scenarios=10,
            profitable_scenarios=int(cases.return_pct.gt(0).sum()),profitable_fraction=float(cases.return_pct.gt(0).mean()),
            beat_hold_scenarios=int(cases.return_pct.gt(bh[period]).sum()),
            lowest_return_pct=float(cases.return_pct.min()),highest_return_pct=float(cases.return_pct.max()),
            positive_profiles_at_base_fee=int(cases[cases.cost_case.eq('base')].return_pct.gt(0).sum()),
            selected_double_cost_return_pct=float(doubled.return_pct.iloc[0]),
            profitable_walk_forward_folds=int(wf.return_pct.gt(0).sum()),
            beat_hold_walk_forward_folds=int(wf.return_pct.gt(wf.buy_and_hold_return_pct).sum()),
            qualified_training_folds=int(wf.qualified_training_fit.astype(bool).sum())))
    pd.DataFrame(robust).to_csv(OUT/'robustness_summary.csv',index=False)
    outputs={str(p.relative_to(OUT)):sha256(p.read_bytes()) for p in sorted(OUT.rglob('*')) if p.is_file() and 'cache' not in p.parts and p.name not in ('run.json','REPORT.md')}
    completed=sum(r['status']['status']=='completed_signal_backtest' for r in results)
    write_json(OUT/'run.json',dict(created_at=utc_now(),dependency_versions={name:__import__('importlib.metadata',fromlist=['version']).version(name) for name in ('numpy','pandas','TA-Lib','technical','ta','scipy')},python_version=sys.version.split()[0],node_version=__import__('subprocess').check_output(['node','--version'],text=True).strip(),attempted=len(results),completed=completed,blocked=len(results)-completed,signal_hash=signals_hash(),implementation_hash=code_hash(),catalog_hash=sha256((ROOT/'sources/full100/catalog.json').read_bytes()),dataset_sha256=manifest['dataset_sha256'],first_input_candle=data.index[0].isoformat(),last_input_candle=data.index[-1].isoformat(),observed_candles=len(data),missing_source_hours=manifest['missing_hours'],outputs_sha256=outputs,untouched_ranks=0,directional_models_scored=0,model_status='Neural forecast runtime incomplete; accuracy unmeasured, not zero',
        backtests_completed=sum(len(r['training'])+len(r['walk_forward'])+2*len(r['period_results'])+len(r['sensitivity']) for r in results)+5))

def read_report():
    meta=json.loads((OUT/'run.json').read_text());_,manifest=load_verified(ROOT)
    if meta['attempted']!=100:raise DataError('The full-list run has not attempted all 100 candidates')
    if meta['dataset_sha256']!=manifest['dataset_sha256'] or meta['implementation_hash']!=code_hash() or meta['catalog_hash']!=sha256((ROOT/'sources/full100/catalog.json').read_bytes()):raise DataError('Expanded report is stale; rerun the full-list audit')
    catalog()
    for rel,digest in meta['outputs_sha256'].items():
        if sha256((OUT/rel).read_bytes())!=digest:raise DataError('Expanded result was changed: '+rel)
    return pd.read_csv(OUT/'inventory.csv'),pd.read_csv(OUT/'period_results.csv'),meta

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=3);p.add_argument('--only',nargs='*');p.add_argument('--aggregate',action='store_true');a=p.parse_args()
    if a.aggregate:aggregate()
    else:execute(a.workers,a.only)
