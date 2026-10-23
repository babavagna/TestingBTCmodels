"""Two-phase execution: fit/select on 2020–2025, freeze artifacts, then score 2026."""
import argparse,json,traceback,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from indicator_lab.data import ROOT,load
from indicator_lab.features import catalog,features,raw,parameters
from indicator_lab.model import targets,period_mask,fit,predict,BURN
from indicator_lab.metrics import accuracy,paired_evidence,portfolio,holm
from btc_lab.data import write_json,sha256,utc_now
OUT=ROOT/'reports/predictions'
PERIODS={'validation':('2025-01-01','2026-01-01'),'retrospective':('2026-01-01','2026-10-01')}

def fingerprint():
    paths=sorted((ROOT/'indicator_lab').glob('*.py'))+[ROOT/'indicator_lab/PROTOCOL.md',ROOT/'sources/tradingview/indicator_catalog.json',ROOT/'sources/tradingview/provenance.json']
    return {str(p.relative_to(ROOT)):sha256(p.read_bytes()) for p in paths}

def causality(row,d,profile):
    small=d.iloc[:3072];full=features(row,small,profile);checks=[]
    for cut in (512,1024,2048):
        before=features(row,small.iloc[:cut],profile)
        ok=np.allclose(before,full[:cut],rtol=1e-7,atol=1e-9,equal_nan=True)
        checks.append(dict(kind='prefix',cut=cut,passed=bool(ok)))
    changed=small.copy();changed.iloc[2048:,:4]*=1.7;changed.iloc[2048:,4]*=2.3
    mutation=features(row,changed,profile)
    checks.append(dict(kind='future_mutation',cut=2048,passed=bool(np.allclose(mutation[:2048],full[:2048],rtol=1e-7,atol=1e-9,equal_nan=True))))
    if not all(x['passed'] for x in checks):raise ValueError('CAUSALITY FAILURE: numerical indicator outputs changed in the past')
    return checks

def get_prediction(model,x):
    good=np.isfinite(x).all(axis=1);good[:BURN]=False
    result=np.full(len(x),np.nan);result[good]=predict(model,x[good]);return result,good

def choose_profile(profiles):
    order={'default':0,'short':1,'long':2}
    return min(profiles,key=lambda p:(-profiles[p]['validation']['accuracy'],order[p]))

def train(minutes):
    OUT.mkdir(parents=True,exist_ok=True);d,dm=load(minutes);y,valid,decision,end=targets(d,minutes)
    trainmask=period_mask(d,minutes,valid,'2020-01-01','2025-01-01',fit=True)
    valmask=period_mask(d,minutes,valid,*PERIODS['validation'])
    records=[];failures=[];checks=[];walk=[];models={}
    for row in catalog():
        ident=row['id'];print('FIT',minutes,ident,flush=True);profiles={};seen=set();default_x=None
        for profile in ('default','short','long'):
            pars=parameters(row,profile);key=json.dumps(pars,sort_keys=True)
            if key in seen:continue
            seen.add(key)
            try:
                audit=causality(row,d,profile);checks.extend(dict(id=ident,profile=profile,**c) for c in audit)
                x=features(row,d,profile);good=np.isfinite(x).all(axis=1);good[:BURN]=False
                eligible=np.arange(len(d))>=BURN
                coverage=float(good[eligible].mean())
                if coverage<.999:raise ValueError(f'Feature completeness {coverage:.4%} below 99.9%')
                model=fit(x,y,trainmask&good)
                vp=predict(model,x[valmask&good]);vm=accuracy(y[valmask&good],vp)
                r=raw(row,d,profile)
                events=int(np.any(r[trainmask&good]!=0,axis=1).sum()) if row['pattern'] else None
                profiles[profile]=dict(parameters=pars,model=model,validation=vm,coverage=coverage,nonzero_training_events=events,rare_training_events=bool(row['pattern'] and events<200))
                if profile=='default':default_x=x
            except Exception as e:
                failures.append(dict(id=ident,timeframe_minutes=minutes,profile=profile,stage='fit_or_causality',error=str(e),forecast_test_completed=False))
        if not profiles:
            records.append(dict(id=ident,timeframe_minutes=minutes,status='FAILED_NO_FORECAST_TEST',reason='; '.join(f['error'] for f in failures if f['id']==ident)));continue
        selected=choose_profile(profiles);models[ident]=dict(selected_profile=selected,profiles=profiles)
        records.append(dict(id=ident,timeframe_minutes=minutes,status='FIT_SELECTED_NOT_YET_2026_TESTED',selected_profile=selected,parameters=profiles[selected]['parameters']))
        # Default only: folds do not inherit a profile chosen using future 2025 data.
        if default_x is not None:
            good=np.isfinite(default_x).all(axis=1);good[:BURN]=False
            for year in (2022,2023,2024):
                try:
                    tm=period_mask(d,minutes,valid,'2020-01-01',f'{year}-01-01',fit=True)&good
                    em=period_mask(d,minutes,valid,f'{year}-01-01',f'{year+1}-01-01')&good
                    m=fit(default_x,y,tm);p=predict(m,default_x[em]);a=accuracy(y[em],p);base=max(float(y[tm].mean()),1-float(y[tm].mean()))
                    baseline=np.full(em.sum(),float(m['training_up_rate']>=.5));bm=accuracy(y[em],baseline)
                    walk.append(dict(id=ident,timeframe_minutes=minutes,evaluation_year=year,profile='default',train_target_end_exclusive=f'{year}-01-01T00:00:00+00:00',model=m,**a,baseline_accuracy=bm['accuracy'],lift=a['accuracy']-bm['accuracy'],status='completed'))
                except Exception as e:walk.append(dict(id=ident,timeframe_minutes=minutes,evaluation_year=year,status='failed',error=str(e)))
    artifact=dict(created_at=utc_now(),phase='FROZEN_BEFORE_2026_ACCURACY',timeframe_minutes=minutes,code_hashes=fingerprint(),data_manifest_sha256=sha256((ROOT/'data/predictions/manifest.json').read_bytes()),protocol_sha256=sha256((ROOT/'indicator_lab/PROTOCOL.md').read_bytes()),selection='Highest 2025 validation accuracy; no 2026 score used; retrospective dates previously examined',records=records,models=models,failures=failures,causality_checks=checks,walk_forward=walk)
    write_json(OUT/f'frozen_{minutes}m.json',artifact)
    print('FROZEN',minutes,len(models),'indicators',len(failures),'profile failures',flush=True)

def score(minutes):
    frozen_path=OUT/f'frozen_{minutes}m.json';f=json.loads(frozen_path.read_text())
    if f['code_hashes']!=fingerprint():raise ValueError('Code or protocol changed after fit; rerun training before scoring')
    if f['data_manifest_sha256']!=sha256((ROOT/'data/predictions/manifest.json').read_bytes()):raise ValueError('Data changed after fitting')
    d,dm=load(minutes);y,valid,decision,end=targets(d,minutes);rows=[];stress=[];monthly=[];curves={};failures=[]
    masks={k:period_mask(d,minutes,valid,*dates) for k,dates in PERIODS.items()}
    # Store shared true labels once. Include ties/gaps in the full eligibility audit.
    rawdelta=d.close.shift(-1)-d.close
    label_frame=pd.DataFrame(dict(feature_candle_open=d.index,forecast_available_at=decision,target_close_at=end,close=d.close.to_numpy(),next_close=d.close.shift(-1).to_numpy(),actual_up=y,scorable_direction=valid,flat_target=(rawdelta==0).to_numpy()))
    sample=(decision>=pd.Timestamp('2025-01-01',tz='UTC'))&(end<=pd.Timestamp('2026-10-01',tz='UTC'))
    (OUT/'probabilities').mkdir(exist_ok=True)
    label_frame.loc[sample].to_csv(OUT/f'labels_{minutes}m.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    for row in catalog():
        ident=row['id']
        if ident not in f['models']:continue
        print('SCORE',minutes,ident,flush=True)
        try:
            record=f['models'][ident];selected=record['selected_profile'];preds={}
            for profile,pf in record['profiles'].items():
                x=features(row,d,profile);p,good=get_prediction(pf['model'],x);preds[profile]=(p,good)
                em=masks['retrospective']&good;a=accuracy(y[em],p[em]);fin,_=portfolio(d,minutes,p,*PERIODS['retrospective'])
                stress.append(dict(id=ident,timeframe_minutes=minutes,kind='parameter',profile=profile,selected=profile==selected,parameters=pf['parameters'],**a,**fin))
            p,good=preds[selected];pf=record['profiles'][selected];train_up=pf['model']['training_up_rate'];majority=float(train_up>=.5)
            # Full feature-eligible probabilities. Future ties are NEVER used to suppress trades.
            np.savez_compressed(OUT/'probabilities'/f'{ident}_{minutes}m.npz',probability=p[sample],predicted_up=p[sample]>=.5,eligible_features=good[sample])
            for period,(start,stop) in PERIODS.items():
                mask=masks[period]&good;ac=accuracy(y[mask],p[mask]);base=np.full(mask.sum(),majority)
                ev=paired_evidence(y[mask],p[mask],base,end[mask]);bm=accuracy(y[mask],base)
                fin,daily=portfolio(d,minutes,p,start,stop)
                fold=[w['lift'] for w in f['walk_forward'] if w['id']==ident and w['status']=='completed']
                r=dict(**row,timeframe_minutes=minutes,period=period,status='FORECAST_TEST_COMPLETED',selected_profile=selected,selected_parameters=pf['parameters'],score_start=start,score_stop_exclusive=stop,first_forecast_at=decision[mask][0].isoformat(),last_target_close=end[mask][-1].isoformat(),eligible_target_count=int(masks[period].sum()),coverage=mask.sum()/masks[period].sum(),baseline_majority_direction='UP' if majority else 'DOWN',baseline_majority_accuracy=bm['accuracy'],mean_walk_forward_lift=float(np.mean(fold)) if len(fold)==3 else None,walk_forward_completed=len(fold),nonzero_training_events=pf['nonzero_training_events'],rare_training_events=pf['rare_training_events'],too_few_forecasts=ac['forecasts']<1000,**ac,**ev,**fin)
                rows.append(r);curves[f'{ident}_{period}']=dict(date=[t.isoformat() for t in daily.index],equity=daily.tolist())
                months=pd.DatetimeIndex(end[mask]-pd.Timedelta(nanoseconds=1)).strftime('%Y-%m')
                for month in sorted(set(months)):
                    sel=months==month
                    monthly.append(dict(id=ident,timeframe_minutes=minutes,period=period,month=month,**accuracy(y[mask][sel],p[mask][sel]),baseline_accuracy=accuracy(y[mask][sel],base[sel])['accuracy']))
            for fee,slip,label in [(.0005,.0005,'half_fee'),(.001,.0005,'base'),(.002,.0005,'double_fee'),(.002,.001,'double_fee_and_slippage')]:
                fin,_=portfolio(d,minutes,p,*PERIODS['retrospective'],fee=fee,slippage=slip)
                stress.append(dict(id=ident,timeframe_minutes=minutes,kind='cost',case=label,profile=selected,**fin))
        except Exception as e:
            failures.append(dict(id=ident,timeframe_minutes=minutes,stage='score',error=str(e),traceback=traceback.format_exc(),forecast_test_completed=False))
    baselines=[]
    train=period_mask(d,minutes,valid,'2020-01-01','2025-01-01',fit=True);majority=float(y[train].mean()>=.5)
    last_return=d.close.diff().to_numpy();persistence=(last_return>=0).astype(float)
    baseline_predictions={'Always UP':np.ones(len(d)),'Always DOWN':np.zeros(len(d)),'Training-majority direction':np.full(len(d),majority),'Previous-candle direction':persistence}
    for name,p in baseline_predictions.items():
        p[:BURN]=np.nan
        for period,dates in PERIODS.items():
            mask=masks[period]&np.isfinite(p);fin,_=portfolio(d,minutes,p,*dates)
            baselines.append(dict(name=name,timeframe_minutes=minutes,period=period,**accuracy(y[mask],p[mask]),**fin))
    write_json(OUT/f'results_{minutes}m.json',dict(created_at=utc_now(),frozen_artifact_sha256=sha256(frozen_path.read_bytes()),code_hashes=fingerprint(),rows=rows,robustness=stress,monthly=monthly,baselines=baselines,score_failures=failures))
    write_json(OUT/f'curves_{minutes}m.json',curves)
    print('SCORED',minutes,len(rows),'period results',len(failures),'errors',flush=True)

def combine():
    results=[json.loads((OUT/f'results_{m}m.json').read_text()) for m in (5,15,60)]
    rows=[r for x in results for r in x['rows']];final=[r for r in rows if r['period']=='retrospective'];adjusted=holm([r['pvalue'] for r in final])
    for r,p in zip(final,adjusted):
        val=next(x for x in rows if x['id']==r['id'] and x['timeframe_minutes']==r['timeframe_minutes'] and x['period']=='validation')
        r['holm_pvalue']=float(p)
        r['retrospective_validation_gate_passed']=bool(r['accuracy_lift_vs_train_majority']>0 and val['accuracy_lift_vs_train_majority']>0 and r['lift_block_ci_low']>0 and p<.05 and r['mean_walk_forward_lift'] is not None and r['mean_walk_forward_lift']>0 and not r['too_few_forecasts'] and not r['rare_training_events'])
        r['genuine_untouched_oos_status']='NOT AVAILABLE: dates already examined; user chose retrospective test'
        r['financial_gate_passed']=bool(r['net_return']>0 and r['excess_vs_buy_hold']>0 and r['trades']>=30 and val['net_return']>0 and val['excess_vs_buy_hold']>0 and val['trades']>=30)
    for minutes in (5,15,60):
        ranked=sorted([r for r in final if r['timeframe_minutes']==minutes],key=lambda r:(-r['accuracy'],r['id']))
        for i,r in enumerate(ranked,1):r['retrospective_rank']=i
    write_json(OUT/'combined.json',dict(created_at=utc_now(),ranking='2026 retrospective next-close accuracy; NEVER genuine untouched OOS rank',holm_family_size=len(final),rows=rows,baselines=[r for x in results for r in x['baselines']],robustness=[r for x in results for r in x['robustness']],monthly=[r for x in results for r in x['monthly']],score_failures=[r for x in results for r in x['score_failures']]))
    pd.DataFrame(final).drop(columns=['parameters'],errors='ignore').to_csv(OUT/'leaderboard.csv',index=False)
    for minutes in (5,15,60):
        r=sorted([r for r in final if r['timeframe_minutes']==minutes],key=lambda r:r['retrospective_rank'])[0]
        print(minutes,r['id'],r['accuracy'],r['baseline_majority_accuracy'],r['net_return'],r['retrospective_validation_gate_passed'])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['train','score','combine']);ap.add_argument('--minutes',type=int,choices=[5,15,60]);args=ap.parse_args()
    if args.phase=='train':train(args.minutes)
    elif args.phase=='score':score(args.minutes)
    else:combine()
