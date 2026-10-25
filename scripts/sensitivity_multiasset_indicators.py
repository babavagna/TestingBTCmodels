"""Frozen fixed-neighbor holdout replays; never select parameters on these scores."""
import argparse,concurrent.futures,json
import numpy as np
import pandas as pd
from btc_lab.data import sha256,write_json,utc_now
from indicator_lab.features import catalog
from indicator_lab.model import fit,predict
from indicator_lab.metrics import accuracy
from multiasset.engine import WARMUP,portfolio
from multiasset.probability import targets,split
from multiasset.strategy_adapters import feature_frame
from multiasset.registry import ROOT,assets
from multiasset_report import case_status,case_records
OUT=ROOT/'reports/multiasset/parameter_sensitivity'


def run(status):
    audit_sha=sha256(__import__('pathlib').Path(__file__).read_bytes());path=OUT/(status['identity'][:20]+'_'+audit_sha[:12]+'.json')
    if path.exists():return
    meta=status['dataset'];file=ROOT/meta['path']
    if sha256(file.read_bytes())!=meta['sha256']:raise ValueError('Price fingerprint changed')
    d=pd.read_parquet(file);d=d[['close']] if status['basis']=='quotes' else d
    _,valid,_,_,delta=targets(d,status['minutes']);masks,_=split(d,status['minutes']);target=(delta>0).astype(int);lookup={r['id']:r for r in catalog()};rows=[]
    for record in case_records(status):
        if not record.get('executed') or not record['candidate_id'].startswith('INDICATOR:'):continue
        for profile,value in record['profiles'].items():
            base=dict(asset=status['asset']['id'],minutes=status['minutes'],basis=status['basis'],identity=status['identity'],candidate_id=record['candidate_id'],profile=profile,parameters=value['parameters'],selected_profile=profile==record['selected_profile'],no_reselection_on_holdout=True)
            try:
                x=feature_frame(lookup[record['candidate_id'].split(':')[1]],d,profile);good=np.isfinite(x).all(1);good[:WARMUP]=False
                training=(masks['fit']|masks['selection'])&valid&(delta!=0)&good;model=fit(x,target,training)
                p=np.full(len(d),np.nan);p[good]=predict(model,x[good])
                for period in ['validation','retrospective_test']:
                    mask=masks[period]&valid&(delta!=0)&good;m=accuracy(target[mask],p[mask]);stats={}
                    if status['basis']=='trades':stats=portfolio(d,p,status['minutes'],status['asset'],status['dates'][period]['start'],status['dates'][period]['stop'])[0]
                    rows.append(dict(base,status='COMPLETED_FIXED_PARAMETER_REPLAY',period=period,directional_accuracy=m['accuracy'],forecasts=m['forecasts'],up_precision=m['up_precision'],up_recall=m['up_recall'],down_precision=m['tn']/(m['tn']+m['fn']) if m['tn']+m['fn'] else None,down_recall=m['tn']/(m['tn']+m['fp']) if m['tn']+m['fp'] else None,**stats))
            except Exception as e:rows.append(dict(base,status='FAILED_OR_INSUFFICIENT_VARIANT',reason=str(e)))
    write_json(path,dict(updated_at=utc_now(),identity=status['identity'],audit_sha256=audit_sha,rows=rows));print('PARAMETER_DONE',status['asset']['id'],status['minutes'],status['basis'],len(rows),flush=True)


def main(workers=2):
    OUT.mkdir(parents=True,exist_ok=True);cases=[]
    for spec in assets():
        for minutes in [5,15,60]:
            for basis in ['trades','quotes']:
                status=case_status(ROOT,spec['id'],minutes,basis)
                if status.get('status')=='COMPLETED_WITH_EXPLICIT_LIMITATIONS':cases.append(status)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(run,status) for status in cases]
        for future in concurrent.futures.as_completed(futures):future.result()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=2);a=p.parse_args();main(a.workers)
