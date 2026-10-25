"""Resumable real-data strategy/model jobs, with strict primary-price provenance."""
import argparse,concurrent.futures,hashlib,json,signal,time,traceback,warnings
from contextlib import contextmanager
from pathlib import Path
import numpy as np
import pandas as pd
from btc_lab.data import write_json,sha256,utc_now
from indicator_lab.features import catalog as indicator_catalog,parameters as indicator_parameters
from indicator_lab.model import fit as binary_fit,predict as binary_predict
from indicator_lab.metrics import accuracy as binary_metrics
from full_universe.audit import catalog as source_catalog
from multiasset.registry import ROOT,assets
from multiasset.engine import WARMUP,portfolio,desired_from_signals
from multiasset.strategy_adapters import original_signals,feature_frame,freq_frame
from multiasset import probability as tri
OUT=ROOT/'reports/multiasset';BASE=OUT/'primary'


def code_hash():
    paths=sorted((ROOT/'multiasset').glob('*.py'))+[ROOT/'multiasset/PROTOCOL.md',ROOT/'multiasset/zenbot.cjs']
    for p in [ROOT/'indicator_lab/features.py',ROOT/'indicator_lab/model.py',ROOT/'sources/full100/catalog.json']:paths.append(p)
    return sha256(''.join(str(p.relative_to(ROOT))+sha256(p.read_bytes()) for p in paths).encode())

@contextmanager
def limit(seconds):
    def fail(*_):raise TimeoutError(f'Bounded call exceeded {seconds} seconds')
    old=signal.signal(signal.SIGALRM,fail);signal.setitimer(signal.ITIMER_REAL,seconds)
    try:yield
    finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)


def sources():
    inventory=pd.read_csv(ROOT/'reports/full100/inventory.csv').set_index('strategy_id')
    result=[]
    for row in source_catalog():
        old=inventory.loc[row['id']]
        row=dict(row);row['previous_runtime_status']=old['status'];row['previous_runtime_reason']=old['reason'];result.append(row)
    return result


def load_case(spec,minutes,basis):
    path=ROOT/'data/kalshi'/spec['symbol']/'manifest.json'
    if not path.exists():raise ValueError('No Kalshi source manifest has been collected')
    manifest=json.loads(path.read_text())
    if manifest.get('primary_venue')!='Kalshi':raise ValueError('Non-Kalshi observations cannot become primary contract history')
    key='TRADED_CONTRACT_OHLCV' if basis=='trades' else 'OBSERVED_BID_ASK_MIDPOINT_CLOSE_ONLY'
    matches=[r for r in manifest.get('datasets',[]) if r['timeframe_minutes']==minutes and r['price_basis']==key]
    if not matches:raise ValueError('No verified '+key+' observations: '+str(manifest.get('error') or manifest.get('status')))
    meta=matches[0];p=ROOT/meta['path']
    if sha256(p.read_bytes())!=meta['sha256']:raise ValueError('Primary dataset fingerprint changed')
    d=pd.read_parquet(p)
    if not d.index.is_unique or not d.index.is_monotonic_increasing or d.index.tz is None:raise ValueError('Primary timestamps are invalid')
    if not np.isfinite(d.close).all() or (d.close<=0).any():raise ValueError('Invalid primary closes')
    if basis=='quotes':d=d[['close']]
    return d,manifest,meta


def eligible_cases():
    cases=[]
    for spec in assets():
        for minutes in [5,15,60]:
            for basis in ['trades','quotes']:
                try:
                    d,m,meta=load_case(spec,minutes,basis)
                    if len(d)<=WARMUP+100:raise ValueError(f'Only {len(d)} observations; need more than {WARMUP+100} for warmup and chronological analysis')
                    cases.append(dict(spec=spec,minutes=minutes,basis=basis,status='READY',data_meta=meta))
                except Exception as e:cases.append(dict(spec=spec,minutes=minutes,basis=basis,status='BLOCKED_PRIMARY_DATA',reason=str(e)))
    return cases


def simple_causality(row,d,profile):
    n=min(len(d),3072);full=d.iloc[:n];features=feature_frame(row,full,profile)
    cuts=sorted(set([max(128,n//3),max(256,2*n//3)]));checks=[]
    for cut in cuts:
        if cut>=n:continue
        actual=feature_frame(row,full.iloc[:cut],profile)
        checks.append(dict(check='numeric_prefix',cut=cut,passed=bool(np.allclose(actual,features[:cut],rtol=1e-7,atol=1e-9,equal_nan=True))))
    cut=cuts[-1];changed=full.copy();changed.iloc[cut:]*=1.7;mutated=feature_frame(row,changed,profile)
    checks.append(dict(check='numeric_future_mutation',cut=cut,passed=bool(np.allclose(mutated[:cut],features[:cut],rtol=1e-7,atol=1e-9,equal_nan=True))))
    if not checks or not all(c['passed'] for c in checks):raise ValueError('Causality failure in numerical predictor features')
    return checks


def source_causality(item,d,factor,minutes,symbol):
    n=min(len(d),1800);small=d.iloc[:n];cut=max(256,2*n//3)
    with limit(30):
        full=original_signals(item,small,factor,minutes,symbol);prefix=original_signals(item,small.iloc[:cut],factor,minutes,symbol)
        ok=all(np.array_equal(a[:cut],b) for a,b in zip(full,prefix))
        if item['framework']=='freqtrade':
            _,a,_,_=freq_frame(item,small,factor,minutes,symbol);_,b,_,_=freq_frame(item,small.iloc[:cut],factor,minutes,symbol)
            cols=[c for c in b.select_dtypes(include='number').columns if c in a]
            ok=ok and all(np.allclose(a[c].to_numpy()[:cut],b[c].to_numpy(),rtol=1e-7,atol=1e-9,equal_nan=True) for c in cols)
        changed=small.copy();changed.iloc[cut:,:4]*=2.1;changed.iloc[cut:,4]*=.7
        mutation=original_signals(item,changed,factor,minutes,symbol)
        ok2=all(np.array_equal(a[:cut],b[:cut]) for a,b in zip(full,mutation))
    if not ok or not ok2:raise ValueError('Source numerical/signal prefix or future-mutation causality failure')
    return [dict(check='source_prefix_and_numeric',cut=cut,passed=bool(ok)),dict(check='source_future_mutation',cut=cut,passed=bool(ok2))]


def fit_binary(row,d,minutes,masks,valid,delta):
    y=(delta>0).astype(int);binary_valid=valid&(delta!=0);profiles={};errors=[];seen=set();checks=[]
    for profile in ['default','short','long']:
        params=indicator_parameters(row,profile);identity=json.dumps(params,sort_keys=True)
        if identity in seen:continue
        seen.add(identity)
        try:
            with limit(35):
                checks.extend(dict(profile=profile,**c) for c in simple_causality(row,d,profile))
                x=feature_frame(row,d,profile);good=np.isfinite(x).all(1);good[:WARMUP]=False
                fitmask=masks['fit']&binary_valid&good;sel=masks['selection']&binary_valid&good
                model=binary_fit(x,y,fitmask)
                if sel.sum()<30:raise ValueError(f'Only {int(sel.sum())} parameter-selection forecasts; need 30')
                scored=binary_metrics(y[sel],binary_predict(model,x[sel]))
                profiles[profile]=dict(parameters=params,selection_accuracy=scored['accuracy'])
        except Exception as e:errors.append(dict(profile=profile,error=str(e)))
    if not profiles:raise ValueError('; '.join(e['error'] for e in errors)[:2000])
    order={'default':0,'short':1,'long':2};selected=min(profiles,key=lambda p:(-profiles[p]['selection_accuracy'],order[p]));x=feature_frame(row,d,selected)
    good=np.isfinite(x).all(1);good[:WARMUP]=False
    model=binary_fit(x,y,(masks['fit']|masks['selection'])&binary_valid&good)
    p=np.full(len(d),np.nan);p[good]=binary_predict(model,x[good])
    return dict(selected_profile=selected,parameters=profiles[selected]['parameters'],model=model,profiles=profiles,profile_failures=errors,causality_checks=checks),p,good


def cost_record(d,desired,minutes,spec,dates):
    stats,curve,monthly,annual=portfolio(d,desired,minutes,spec,dates['start'],dates['stop'])
    return dict(stats=stats,curve=curve,monthly=monthly,annual=annual)


def run_source(item,d,minutes,spec,masks,dates):
    if item['previous_runtime_status']!='completed_signal_backtest':
        return dict(candidate_id='SOURCE:'+item['id'],name=item['name'],family='original signal strategy',status='BLOCKED_AUDITED_SOURCE',reason=item['previous_runtime_reason'],source_url=item['source_url'],license=item.get('license'),executed=False)
    profiles={};errors=[];checks=[]
    for label,factor in [('default',1.),('short',.8),('long',1.2)]:
        try:
            with limit(45):
                checks.extend(dict(profile=label,**v) for v in source_causality(item,d,factor,minutes,spec['symbol']))
                en,ex=original_signals(item,d,factor,minutes,spec['symbol']);desired=desired_from_signals(en,ex)
                training=dict(start=dates['fit']['start'],stop=dates['selection']['stop'])
                fit=cost_record(d,desired,minutes,spec,training)
                profiles[label]=dict(factor=factor,desired=desired,fit=fit['stats'])
        except Exception as e:errors.append(dict(profile=label,error=type(e).__name__+': '+str(e)))
    if not profiles:raise ValueError('; '.join(e['error'] for e in errors)[:1800])
    eligible=[p for p,v in profiles.items() if v['fit']['trades']>=30 and v['fit']['sharpe'] is not None]
    selected=max(eligible,key=lambda p:profiles[p]['fit']['sharpe']) if eligible else ('default' if 'default' in profiles else next(iter(profiles)))
    out=dict(candidate_id='SOURCE:'+item['id'],name=item['name'],family='original signal strategy',status='COMPLETED_COST_LIMITED_BACKTEST',source_url=item['source_url'],license=item.get('license'),selected_profile=selected,parameter_selection='Highest earlier training Sharpe with >=30 trades, otherwise default',profile_failures=errors,causality_checks=checks,executed=True,directional_accuracy=None,directional_forecast_status='N/A: native trading entries/exits are not per-candle directional forecasts',periods={},sensitivity=[])
    desired=profiles[selected]['desired']
    for period in ['validation','retrospective_test']:out['periods'][period]=cost_record(d,desired,minutes,spec,dates[period])
    for p,r in profiles.items():
        v=cost_record(d,r['desired'],minutes,spec,dates['retrospective_test']);out['sensitivity'].append(dict(kind='parameter',profile=p,**v['stats']))
    for label,fee,slip in [('half_fee',.0005,.0005),('double_fee',.002,.0005),('double_both',.002,.001)]:
        s,_,_,_=portfolio(d,desired,minutes,spec,dates['retrospective_test']['start'],dates['retrospective_test']['stop'],fee,slip);out['sensitivity'].append(dict(kind='cost',case=label,**s))
    pos=np.flatnonzero(masks['fit']|masks['selection']);out['walk_forward']=[]
    for fraction in [.25,.5,.75]:
        cut=int(len(pos)*fraction);last=min(len(pos)-1,cut+max(10,len(pos)//4))
        if cut<2 or last<=cut:
            out['walk_forward'].append(dict(status='INSUFFICIENT_FOLD',reason='Fewer than two chronological fold observations'));continue
        start=d.index[pos[0]].isoformat();stop=d.index[pos[cut]].isoformat()
        try:
            scored={}
            for profile,v in profiles.items():scored[profile]=cost_record(d,v['desired'],minutes,spec,dict(start=start,stop=stop))['stats']
            qualified=[profile for profile,s in scored.items() if s['trades']>=30 and s['sharpe'] is not None]
            chosen=max(qualified,key=lambda profile:scored[profile]['sharpe']) if qualified else ('default' if 'default' in profiles else next(iter(profiles)))
            evaluated=cost_record(d,profiles[chosen]['desired'],minutes,spec,dict(start=d.index[pos[cut]].isoformat(),stop=d.index[pos[last]].isoformat()))
            out['walk_forward'].append(dict(status='COMPLETED',profile=chosen,training_stop=stop,**evaluated['stats']))
        except Exception as e:out['walk_forward'].append(dict(status='INSUFFICIENT_FOLD_OR_EXECUTION_FAILED',reason=str(e)))
    return out,desired


def run_indicator(row,d,minutes,spec,masks,dates,valid,delta,basis):
    record,p,good=fit_binary(row,d,minutes,masks,valid,delta);target=(delta>0).astype(int)
    out=dict(candidate_id='INDICATOR:'+row['id'],name=row['name'],family='indicator + trained binary readout',status='COMPLETED_COST_LIMITED_BACKTEST' if basis=='trades' else 'COMPLETED_PREDICTION_ONLY',source_url=row['github_url'],license='See pinned formula source and retained upstream license',executed=True,**record,periods={},sensitivity=[])
    for period in ['validation','retrospective_test']:
        sm=masks[period]&valid&(delta!=0)&good
        if not sm.any():raise ValueError('No eligible directional labels in '+period)
        metrics=binary_metrics(target[sm],p[sm]);tn=metrics['tn'];fn=metrics['fn'];metrics['down_precision']=tn/(tn+fn) if tn+fn else None;metrics['down_recall']=tn/(tn+metrics['fp']) if tn+metrics['fp'] else None
        out['periods'][period]=dict(direction=metrics)
        if basis=='trades':out['periods'][period].update(cost_record(d,p,minutes,spec,dates[period]))
    if basis=='trades':
        for label,fee,slip in [('half_fee',.0005,.0005),('double_fee',.002,.0005),('double_both',.002,.001)]:
            s,_,_,_=portfolio(d,p,minutes,spec,dates['retrospective_test']['start'],dates['retrospective_test']['stop'],fee,slip);out['sensitivity'].append(dict(kind='cost',case=label,**s))
    votes=np.full(len(p),-1,np.int8);votes[good]=(p[good]>=.5).astype(np.int8)
    return out,votes


def walk_indicator(row,model_record,d,minutes,valid,delta,masks):
    # All folds stay earlier than the final calibration/validation/test segments.
    x=feature_frame(row,d,'default');good=np.isfinite(x).all(1);good[:WARMUP]=False
    pos=np.flatnonzero((masks['fit']|masks['selection'])&valid&(delta!=0)&good);out=[];target=(delta>0).astype(int)
    for fraction in [.25,.5,.75]:
        cut=int(len(pos)*fraction);end=min(len(pos),cut+max(30,len(pos)//4));tm=np.zeros(len(d),bool);em=tm.copy();tm[pos[:max(0,cut-1)]]=True;em[pos[cut:end]]=True
        try:
            model=binary_fit(x,target,tm);p=binary_predict(model,x[em]);m=binary_metrics(target[em],p);out.append(dict(status='COMPLETED',training_rows=int(tm.sum()),evaluation_start=d.index[pos[cut]].isoformat(),**m))
        except Exception as e:out.append(dict(status='INSUFFICIENT_FOLD_OR_FIT_FAILED',training_rows=int(tm.sum()),reason=str(e)))
    return out


def probability_models(d,minutes,masks,dates,identity):
    features=tri.features(d);good=np.isfinite(features).all(1);models=[]
    for threshold in tri.THRESHOLDS:
        y,valid,decision,end,_=tri.targets(d,minutes,threshold);sm=masks['fit']|masks['selection']
        record=dict(threshold=threshold,status='NOT_FITTED',identity=identity,dates=dates)
        try:
            model=tri.fit(features,y,sm&valid&good);record['model']=model
            try:record['model']=tri.calibrate(model,features,y,masks['calibration']&valid&good);record['status']='FITTED_AND_CALIBRATED'
            except Exception as e:record.update(status='FITTED_UNCALIBRATED',calibration_error=str(e))
            model=record['model'];record['periods']={}
            traincounts=np.asarray(model['training_counts']);baseline=np.tile(traincounts/traincounts.sum(),(len(d),1))
            for period in ['validation','retrospective_test']:
                mask=masks[period]&valid&good;p=tri.predict(model,features[mask]);raw=tri.predict(model,features[mask],calibrated=False)
                record['periods'][period]=dict(calibrated=tri.metrics(y[mask],p),uncalibrated=tri.metrics(y[mask],raw),training_frequency_baseline=tri.metrics(y[mask],baseline[mask]))
            last=np.flatnonzero(good)
            if len(last):
                j=last[-1];asof=decision[j];now=pd.Timestamp.now(tz='UTC');fresh=(now-asof).total_seconds()<=max(minutes*120,600)
                snapshot=tri.predict(model,features[j:j+1])[0].tolist()
                record.update(last_price_as_of=asof.isoformat(),historical_snapshot_probabilities=snapshot,current_probabilities=snapshot if fresh and model.get('calibrated') else None,current_status='CURRENT' if fresh and model.get('calibrated') else ('UNCALIBRATED' if not model.get('calibrated') else 'HISTORICAL_ONLY_NOT_CURRENT'),last_successful_model_update=pd.Timestamp.now(tz='UTC').isoformat(),training_end=dates['selection']['stop'],calibration_end=dates['calibration']['stop'])
        except Exception as e:record.update(status='BLOCKED_INSUFFICIENT_MODEL_EVIDENCE',reason=str(e),current_probabilities=None,current_status='NO_CURRENT_MODEL')
        models.append(record)
    return models


def clusters(signals,masks):
    if not signals:return []
    keys=list(signals);idx=np.flatnonzero(masks['fit']|masks['selection']);sample=idx[np.linspace(0,len(idx)-1,min(2048,len(idx))).astype(int)]
    hashes={};records=[];matrix=[]
    for key in keys:
        a=np.asarray(signals[key])[sample];valid=a>=0;v=np.where(valid,a,.5);matrix.append(v)
        digest=sha256(np.asarray(a,dtype=np.int8).tobytes());same=hashes.get(digest);hashes.setdefault(digest,key)
        records.append(dict(candidate_id=key,training_signature=digest,exact_sample_duplicate_of=same,correlated_with=[],independent_evidence_claim=False,sampled_training_observations=len(sample)))
    a=np.asarray(matrix,float);sd=a.std(1);nonconstant=sd>1e-10
    if nonconstant.sum()>1:
        corr=np.corrcoef(a[nonconstant]);indices=np.flatnonzero(nonconstant)
        for j,i in enumerate(indices):records[i]['correlated_with']=[keys[indices[k]] for k in range(len(indices)) if k!=j and abs(corr[j,k])>=.98]
    return records


def run_case(case,max_candidates=None):
    warnings.filterwarnings('ignore',category=pd.errors.PerformanceWarning)
    spec=case['spec'];minutes=case['minutes'];basis=case['basis'];directory=BASE/f'{spec["id"]}_{minutes}m_{basis}';directory.mkdir(exist_ok=True,parents=True)
    status_path=directory/'status.json'
    if case['status']!='READY':
        write_json(status_path,dict(updated_at=utc_now(),asset=spec,minutes=minutes,basis=basis,status=case['status'],reason=case.get('reason'),executed_candidates=0,fully_validated_rank_count=0));return
    try:
        d,manifest,meta=load_case(spec,minutes,basis);masks,dates=tri.split(d,minutes)
    except Exception as e:
        write_json(status_path,dict(updated_at=utc_now(),asset=spec,minutes=minutes,basis=basis,status='BLOCKED_INSUFFICIENT_PRIMARY_HISTORY',reason=str(e),executed_candidates=0,fully_validated_rank_count=0));return
    stable_spec={k:spec.get(k) for k in ['id','symbol','provider','market_type','market_id','market_version','contract_size','underlying_multiplier','tick_size','fractional_trading_enabled']}
    identity=sha256((code_hash()+meta['sha256']+json.dumps(stable_spec,sort_keys=True)).encode());state=dict(updated_at=utc_now(),identity=identity,asset=spec,minutes=minutes,basis=basis,price_basis=meta['price_basis'],dataset=meta,source_manifest_status=manifest['status'],source_partial=manifest['status']!='HISTORY_READY',dates=dates,status='RUNNING',completed=0,failed=0,blocked=0,fully_validated_rank_count=0)
    directory=directory/'runs'/identity[:20];directory.mkdir(exist_ok=True,parents=True)
    state['run_directory']=str(directory.relative_to(ROOT));state['implementation_sha256']=code_hash()
    write_json(status_path,state);write_json(directory/'inputs.json',state);y,valid,decision,end,delta=tri.targets(d,minutes)
    original=sources();first=[r for r in original if r['previous_runtime_status']=='completed_signal_backtest'][:10]
    ordered=[('source',r) for r in first]+[('indicator',r) for r in indicator_catalog()]+[('source',r) for r in original if r not in first]
    if max_candidates:ordered=ordered[:max_candidates]
    predictions={};results=[]
    for number,(kind,item) in enumerate(ordered,1):
        cid=('SOURCE:' if kind=='source' else 'INDICATOR:')+item['id'];path=directory/(cid.replace(':','_')+'.json');cache=directory/(cid.replace(':','_')+'.npz')
        print('CANDIDATE',spec['id'],minutes,basis,number,cid,flush=True)
        try:
            if path.exists():
                previous=json.loads(path.read_text())
                if previous.get('identity')==identity:
                    result=previous
                    if cache.exists() and result.get('signal_cache_sha256')==sha256(cache.read_bytes()):
                        with np.load(cache) as c:predictions[cid]=c['signal']
                    results.append(result);continue
            if kind=='source' and basis!='trades':result=dict(candidate_id=cid,name=item['name'],family='original signal strategy',status='BLOCKED_INPUT_FIELDS',reason='Original source trading projection requires actual OHLCV; midpoint close-only data is not fabricated into candles',executed=False,source_url=item['source_url'])
            elif kind=='source':
                value=run_source(item,d,minutes,spec,masks,dates)
                if isinstance(value,tuple):result,signal=value;predictions[cid]=signal.astype(np.int8)
                else:result=value
            else:
                result,signal=run_indicator(item,d,minutes,spec,masks,dates,valid,delta,basis);predictions[cid]=signal
                result['walk_forward']=walk_indicator(item,result,d,minutes,valid,delta,masks)
            result.update(identity=identity,asset_id=spec['id'],contract=spec['symbol'],minutes=minutes,basis=basis,price_basis=meta['price_basis'],historical_test_status='RETROSPECTIVE_SHORT_HISTORY_HOLDOUT',fully_validated_financial_rank_eligible=False,finished_at=utc_now())
            if cid in predictions:
                np.savez_compressed(cache,signal=predictions[cid]);result['signal_cache_sha256']=sha256(cache.read_bytes())
            write_json(path,result);results.append(result)
        except Exception as e:
            result=dict(identity=identity,candidate_id=cid,name=item.get('name'),asset_id=spec['id'],contract=spec['symbol'],minutes=minutes,basis=basis,status='FAILED_OR_INSUFFICIENT_EVIDENCE',executed=False,reason=type(e).__name__+': '+str(e),source_url=item.get('source_url',item.get('github_url')),finished_at=utc_now());write_json(path,result);results.append(result)
        state.update(updated_at=utc_now(),attempted=number,completed=sum(bool(r.get('executed')) for r in results),blocked=sum(str(r['status']).startswith('BLOCKED') for r in results),failed=sum(str(r['status']).startswith('FAILED') for r in results),last_candidate=cid)
        write_json(status_path,state)
    # Conditional estimates use actual calibration outcome co-occurrences.
    keys=list(predictions);matrix=np.column_stack([predictions[k] for k in keys]) if keys else np.empty((len(d),0),np.int8)
    for segment in ['calibration','validation','retrospective_test']:
        mask=masks[segment]&valid
        np.savez_compressed(directory/f'joint_{segment}.npz',votes=matrix[mask].astype(np.int8),outcomes=y[mask],timestamps=decision.asi8[mask],candidate_ids=np.array(keys,dtype=str))
    write_json(directory/'signal_clusters.json',clusters(predictions,masks))
    models=probability_models(d,minutes,masks,dates,identity);write_json(directory/'probabilities.json',models)
    state.update(status='PARTIAL_CANDIDATE_CHECKPOINT' if max_candidates and len(results)<247 else 'COMPLETED_WITH_EXPLICIT_LIMITATIONS',updated_at=utc_now(),attempted=len(results),candidate_target=247,completed=sum(bool(r.get('executed')) for r in results),blocked=sum(str(r['status']).startswith('BLOCKED') for r in results),failed=sum(str(r['status']).startswith('FAILED') for r in results),probability_models_calibrated=sum(m['status']=='FITTED_AND_CALIBRATED' for m in models),calibration_thresholds=tri.THRESHOLDS)
    write_json(directory/'status.json',state);write_json(status_path,state);print('CASE_DONE',spec['id'],minutes,basis,state['completed'],state['failed'],flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset');p.add_argument('--minutes',type=int,choices=[5,15,60]);p.add_argument('--basis',choices=['trades','quotes']);p.add_argument('--workers',type=int,default=3);p.add_argument('--max-candidates',type=int);a=p.parse_args()
    cases=[c for c in eligible_cases() if (not a.asset or c['spec']['id']==a.asset) and (not a.minutes or c['minutes']==a.minutes) and (not a.basis or c['basis']==a.basis)]
    OUT.mkdir(exist_ok=True,parents=True);write_json(OUT/'case_registry.json',dict(created_at=utc_now(),primary_venue='Kalshi',named_assets=28,observed_contracts=len(assets()),cases=[dict(asset_id=c['spec']['id'],contract=c['spec']['symbol'],minutes=c['minutes'],basis=c['basis'],status=c['status'],reason=c.get('reason')) for c in cases]))
    if a.workers==1:
        for case in cases:run_case(case,a.max_candidates)
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:
            futures={pool.submit(run_case,c,a.max_candidates):c for c in cases}
            for future in concurrent.futures.as_completed(futures):
                c=futures[future]
                try:future.result()
                except Exception as e:print('CASE_FAILED',c['spec']['id'],c['minutes'],c['basis'],str(e),flush=True)
if __name__=='__main__':main()
