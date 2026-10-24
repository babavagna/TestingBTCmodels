"""Regenerate actual forecasts for the requested list; never retune on 2026."""
import argparse,json,traceback
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from talib import abstract
from btc_lab.data import sha256,write_json,utc_now
from indicator_lab.data import ROOT,load
from indicator_lab.features import catalog,features,raw
from indicator_lab.model import targets,period_mask,predict
from indicator_lab.metrics import portfolio
from indicator_lab.runner import fingerprint,causality,get_prediction,PERIODS
from directional_study.metrics import directions
OUT=ROOT/'reports/selected_directional';SOURCE=ROOT/'sources/selected_directional'

def request():
    original=(SOURCE/'request_ids.txt').read_text().split();unique=list(dict.fromkeys(original));counts=Counter(original)
    known={r['id']:r for r in catalog()}
    if set(unique)-set(known):raise ValueError('Unknown requested IDs: '+str(set(unique)-set(known)))
    return original,unique,counts,known

def freeze_inputs():
    OUT.mkdir(exist_ok=True,parents=True);original,ids,counts,c=request()
    files=sorted((ROOT/'directional_study').glob('*.py'))+[ROOT/'directional_study/PROTOCOL.md',SOURCE/'request_ids.txt',ROOT/'data/predictions/manifest.json',ROOT/'reports/predictions/combined.json']
    files += [ROOT/f'reports/predictions/frozen_{m}m.json' for m in (5,15,60)]
    write_json(OUT/'inputs.json',dict(created_at=utc_now(),scope='Re-execute frozen indicator+logistic models; retrospective, not new fitting or untouched data',input_rows=len(original),unique_indicators=len(ids),duplicate_rows=len(original)-len(ids),patterns=sum(c[n]['pattern'] for n in ids),hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()) for p in files},original_frozen_code_hashes=fingerprint(),threshold=.5,direction_warning_minimum=100,periods=PERIODS))
    write_json(SOURCE/'catalog.json',dict(created_at=utc_now(),rows=[dict(**c[n],input_occurrences=counts[n],original_input_rows=[i+1 for i,v in enumerate(original) if v==n]) for n in ids]))

def verify_inputs():
    f=json.loads((OUT/'inputs.json').read_text())
    for p,digest in f['hashes'].items():
        if sha256((ROOT/p).read_bytes())!=digest:raise ValueError('Run input changed: '+p)
    if f['original_frozen_code_hashes']!=fingerprint():raise ValueError('Original experiment code changed')
    return f

def input_description(row):
    if row['implementation'].startswith('TA-Lib'):
        source=dict(abstract.Function(row['id']).input_names)
        return json.dumps(source,sort_keys=True)
    return 'Disclosed Python formula using current/past Binance OHLCV; see formula source'

def score(minutes):
    verify_inputs();original,ids,counts,c=request();d,manifest=load(minutes)
    oldpath=ROOT/f'reports/predictions/frozen_{minutes}m.json';f=json.loads(oldpath.read_text())
    if f['code_hashes']!=fingerprint():raise ValueError('Frozen formula/model code fingerprint changed')
    y,valid,decision,end=targets(d,minutes)
    allsample=(decision>=pd.Timestamp('2025-01-01',tz='UTC'))&(end<=pd.Timestamp('2026-10-01',tz='UTC'))
    prior=json.loads((ROOT/'reports/predictions/combined.json').read_text())
    rows=[];events=[];walk=[];failures=[];audit=[];reproductions=[]
    masks={key:period_mask(d,minutes,valid,*dates) for key,dates in PERIODS.items()}
    for ident in ids:
        print('REEXECUTE',minutes,ident,flush=True)
        try:
            row=c[ident];rec=f['models'][ident];profile=rec['selected_profile'];pf=rec['profiles'][profile]
            checks=causality(row,d,profile);audit.extend(dict(id=ident,timeframe_minutes=minutes,profile=profile,**a) for a in checks)
            x=features(row,d,profile);p,good=get_prediction(pf['model'],x)
            reference_path=ROOT/'reports/predictions/probabilities'/f'{ident}_{minutes}m.npz'
            with np.load(reference_path) as previous:
                q=previous['probability'];eligible=previous['eligible_features']
                same=np.allclose(p[allsample],q,rtol=0,atol=1e-12,equal_nan=True)
                if not same or not np.array_equal(good[allsample],eligible) or not np.array_equal(p[allsample]>=.5,previous['predicted_up']):raise ValueError('Regenerated forecasts disagree with the saved frozen forecast artifact')
                err=np.abs(p[allsample]-q);maxerr=float(np.nanmax(err))
            reproductions.append(dict(id=ident,timeframe_minutes=minutes,compared_probabilities=int(allsample.sum()),same_decisions=True,maximum_probability_difference=maxerr,saved_probability_sha256=sha256(reference_path.read_bytes())))
            output=raw(row,d,profile);active=np.isfinite(output).all(axis=1)&np.any(output!=0,axis=1)
            for period,(start,stop) in PERIODS.items():
                sample=masks[period]&good;old=next(v for v in prior['rows'] if v['id']==ident and v['timeframe_minutes']==minutes and v['period']==period)
                scores=directions(y[sample],p[sample]);fin,_=portfolio(d,minutes,p,start,stop)
                if scores['overall_accuracy']!=old['accuracy'] or scores['forecasts']!=old['forecasts']:raise ValueError('New accuracy does not reproduce earlier measured score')
                if not np.isclose(fin['net_return'],old['net_return'],rtol=0,atol=1e-12):raise ValueError('Trading-cost replay disagrees with earlier portfolio')
                result=dict(id=ident,name=row['name'],pattern=row['pattern'],timeframe_minutes=minutes,period=period,scope='ALL_ELIGIBLE_CANDLES',status='REEXECUTED_AND_VERIFIED',input_occurrences=counts[ident],selected_profile=profile,parameters=pf['parameters'],input_series=input_description(row),source_url=row['github_url'],formula_status=row['formula_status'],score_start=start,score_stop_exclusive=stop,**scores,**fin,coverage=scores['forecasts']/masks[period].sum(),training_samples=pf['model']['training_samples'],rare_training_events=pf['rare_training_events'],nonzero_training_events=pf['nonzero_training_events'],baseline_accuracy=old['baseline_majority_accuracy'],accuracy_lift=old['accuracy_lift_vs_train_majority'],mean_walk_forward_lift=old['mean_walk_forward_lift'],original_universe_holm_pvalue=old.get('holm_pvalue'),original_retrospective_gate=old.get('retrospective_validation_gate_passed'),original_financial_gate=old.get('financial_gate_passed'),frozen_models_sha256=sha256(oldpath.read_bytes()))
                if row['pattern']:
                    timemask=(decision>=pd.Timestamp(start,tz='UTC'))&(end<=pd.Timestamp(stop,tz='UTC'))
                    eventmask=sample&active;ev=directions(y[eventmask],p[eventmask]);flat=(d.close.shift(-1).to_numpy()==d.close.to_numpy())
                    result.update(pattern_fired_count=int((timemask&active).sum()),pattern_scored_count=int(eventmask.sum()),pattern_few_scored=int(eventmask.sum())<100)
                    events.append(dict(id=ident,name=row['name'],timeframe_minutes=minutes,period=period,scope='CURRENT_CANDLE_PATTERN_FIRED_ONLY',status='EVENT_FORECASTS_SCORED' if eventmask.any() else 'NO_SCORED_EVENTS',selected_profile=profile,parameters=pf['parameters'],pattern_fired_count=result['pattern_fired_count'],pattern_scored_count=int(eventmask.sum()),pattern_flat_targets=int((timemask&active&flat).sum()),pattern_other_unscored=int((timemask&active&~flat&~eventmask).sum()),pattern_few_scored=int(eventmask.sum())<100,rare_training_events=pf['rare_training_events'],nonzero_training_events=pf['nonzero_training_events'],source_url=row['github_url'],**ev))
                else:result.update(pattern_fired_count=None,pattern_scored_count=None,pattern_few_scored=None)
                rows.append(result)
            # Default-profile folds were fitted using only earlier training years.
            dx=features(row,d,'default');dgood=np.isfinite(dx).all(axis=1)
            for w in [v for v in f['walk_forward'] if v['id']==ident]:
                year=w['evaluation_year']
                if w['status']!='completed':
                    walk.append(dict(id=ident,timeframe_minutes=minutes,evaluation_year=year,status='ORIGINAL_FOLD_FAILED',error=w['error']));continue
                sm=period_mask(d,minutes,valid,f'{year}-01-01',f'{year+1}-01-01')&dgood
                sp=predict(w['model'],dx[sm]);a=directions(y[sm],sp)
                if a['overall_accuracy']!=w['accuracy']:raise ValueError('Walk-forward accuracy mismatch')
                walk.append(dict(id=ident,timeframe_minutes=minutes,evaluation_year=year,status='FROZEN_FOLD_REEXECUTED',profile='default',baseline_accuracy=w['baseline_accuracy'],lift=a['overall_accuracy']-w['baseline_accuracy'],**a))
        except Exception as e:
            rows=[r for r in rows if r['id']!=ident]
            events=[r for r in events if r['id']!=ident]
            walk=[r for r in walk if r['id']!=ident]
            failures.append(dict(id=ident,timeframe_minutes=minutes,status='REEXECUTION_FAILED',error=str(e),traceback=traceback.format_exc()))
    write_json(OUT/f'results_{minutes}m.json',dict(created_at=utc_now(),input_manifest_sha256=sha256((OUT/'inputs.json').read_bytes()),rows=rows,pattern_events=events,walk_forward=walk,failures=failures,causality=audit,reproduction=reproductions))
    print('COMPLETED',minutes,len(rows)//2,'indicator pairs;',len(failures),'failures',flush=True)

def combine():
    verify_inputs();original,ids,counts,c=request();parts=[json.loads((OUT/f'results_{m}m.json').read_text()) for m in (5,15,60)]
    output=dict(created_at=utc_now(),request_rows=len(original),unique_indicators=len(ids),duplicate_rows=len(original)-len(ids),input_manifest_sha256=sha256((OUT/'inputs.json').read_bytes()))
    for key in ('rows','pattern_events','walk_forward','failures','causality','reproduction'):output[key]=[v for p in parts for v in p[key]]
    for m in (5,15,60):
        candidates=[v for v in output['rows'] if v['period']=='retrospective' and v['timeframe_minutes']==m]
        for rank,row in enumerate(sorted(candidates,key=lambda v:(-v['overall_accuracy'],v['id'])),1):row['requested_subset_rank']=rank
    write_json(OUT/'combined.json',output)
    pd.DataFrame(output['rows']).to_csv(OUT/'all_candle_directions.csv',index=False)
    pd.DataFrame(output['pattern_events']).to_csv(OUT/'pattern_event_directions.csv',index=False)
    print('Combined',len(output['rows'])//2,'requested indicator/timeframe tests;',len(output['failures']),'failures')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['freeze','score','combine']);p.add_argument('--minutes',type=int,choices=[5,15,60]);a=p.parse_args()
    if a.phase=='freeze':freeze_inputs()
    elif a.phase=='score':score(a.minutes)
    else:combine()
