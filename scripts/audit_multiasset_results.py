"""Post-run source integrity and paired prediction diagnostics; no winner selection."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from btc_lab.data import sha256,write_json,utc_now
from indicator_lab.metrics import paired_evidence,holm
from multiasset.registry import ROOT,assets
from multiasset.probability import targets,split
from multiasset_report import case_status,case_records,run_directory

OUT=ROOT/'reports/multiasset'


def audit():
    integrity=[];evidence=[];causality=[];parameters=[]
    for spec in assets():
        manifest_path=ROOT/'data/kalshi'/spec['symbol']/'manifest.json'
        if not manifest_path.exists():continue
        manifest=json.loads(manifest_path.read_text())
        for meta in manifest.get('datasets',[]):
            file=ROOT/meta['path'];d=pd.read_parquet(file);step=pd.Timedelta(minutes=meta['timeframe_minutes'])
            adjacent=d.index.to_series().diff().eq(step).to_numpy();jumps=np.abs(d.close.pct_change().to_numpy())>.5
            bad=not d.index.is_unique or not d.index.is_monotonic_increasing or d.index.tz is None or not np.isfinite(d.close).all() or (d.close<=0).any()
            if 'high' in d:bad=bad or (d.high<d[['open','low','close']].max(axis=1)).any() or (d.low>d[['open','high','close']].min(axis=1)).any() or (d.volume<0).any()
            integrity.append(dict(asset=spec['id'],contract=spec['symbol'],timeframe_minutes=meta['timeframe_minutes'],price_basis=meta['price_basis'],path=meta['path'],rows=len(d),first=d.index[0].isoformat(),last=d.index[-1].isoformat(),fingerprint_verified=sha256(file.read_bytes())==meta['sha256'],timestamp_ohlcv_checks_passed=not bool(bad),missing_calendar_slots=meta['missing_calendar_slots'],adjacent_price_jumps_over_50_percent=int((jumps&adjacent).sum()),jump_action='Flag only; real observations are never smoothed or deleted',session_calendar='Not historically verified; missing slots can include closures/no trades'))
        for minutes in [5,15,60]:
            for basis in ['trades','quotes']:
                status=case_status(ROOT,spec['id'],minutes,basis);records=case_records(status);directory=run_directory(status)
                if not records or status.get('status')!='COMPLETED_WITH_EXPLICIT_LIMITATIONS':continue
                d=pd.read_parquet(ROOT/status['dataset']['path']);_,valid,decision,_,delta=targets(d,minutes);masks,_=split(d,minutes)
                for r in records:
                    for check in r.get('causality_checks',[]):causality.append(dict(asset=spec['id'],minutes=minutes,basis=basis,candidate_id=r['candidate_id'],**check))
                    for profile,value in r.get('profiles',{}).items():parameters.append(dict(asset=spec['id'],minutes=minutes,basis=basis,candidate_id=r['candidate_id'],profile=profile,selected=profile==r.get('selected_profile'),selection_accuracy=value.get('selection_accuracy'),parameters=value.get('parameters'),selection_period='Earlier internal parameter selection; not held-out test',**value.get('fit',{})))
                    if not r.get('executed') or not r['candidate_id'].startswith('INDICATOR:'):continue
                    file=directory/(r['candidate_id'].replace(':','_')+'.npz')
                    if sha256(file.read_bytes())!=r['signal_cache_sha256']:raise ValueError('Prediction cache fingerprint mismatch')
                    with np.load(file) as a:signal=a['signal']
                    for period in ['validation','retrospective_test']:
                        mask=masks[period]&valid&(delta!=0)&(signal>=0);n=int(mask.sum())
                        if n==0:continue
                        y=(delta[mask]>0).astype(int);p=signal[mask];baseline=np.full(n,r['model']['training_up_rate'])
                        result=paired_evidence(y,p,baseline,decision[mask],replicates=2000)
                        evidence.append(dict(asset=spec['id'],minutes=minutes,basis=basis,candidate_id=r['candidate_id'],period=period,forecasts=n,**result))
    if evidence:
        adjusted=holm([r['pvalue'] for r in evidence])
        for r,p in zip(evidence,adjusted):
            r['holm_adjusted_pvalue_global']=float(p);r['multiplicity_family_size']=len(evidence)
            r['limited_chronological_gate']=bool(r['forecasts']>=1000 and r['independent_day_blocks']>=60 and r['accuracy_lift_vs_train_majority']>0 and p<=.05 and r['lift_block_ci_low']>0)
            r['independent_untouched_validation']=False
            r['gate_description']='Descriptive only: >=1000 forecasts, >=60 observed days, positive block-bootstrap lift and global Holm p<=0.05. Historical reused periods are never independently validated.'
    result=dict(updated_at=utc_now(),data_integrity=integrity,paired_prediction_evidence=evidence,causality_checks=causality,parameter_selection=parameters,summary=dict(datasets_checked=len(integrity),source_or_integrity_failures=sum(not(r['fingerprint_verified'] and r['timestamp_ohlcv_checks_passed']) for r in integrity),numeric_causality_checks=len(causality),failed_numeric_checks=sum(not r['passed'] for r in causality),paired_prediction_comparisons=len(evidence),limited_chronological_gates_passed=sum(r['limited_chronological_gate'] for r in evidence),independently_validated_strategies=0))
    OUT.mkdir(exist_ok=True,parents=True);write_json(OUT/'audit.json',result)
    for key in ['data_integrity','paired_prediction_evidence','causality_checks','parameter_selection']:pd.DataFrame(result[key]).to_csv(OUT/(key+'.csv'),index=False)
    print(json.dumps(result['summary'],indent=2));return result

if __name__=='__main__':audit()
