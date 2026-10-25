"""Evaluate fixed exploratory agreement groups using calibration joint frequencies."""
import json
import numpy as np
from btc_lab.data import write_json,utc_now
from multiasset.registry import ROOT,assets
from multiasset.probability import metrics
from multiasset_report import case_status,run_directory
from directional_study.metrics import interval
GROUPS={'RSI_MACD_EMA':['INDICATOR:RSI','INDICATOR:MACD','INDICATOR:EMA'],'RSI_ROC':['INDICATOR:RSI','INDICATOR:ROC'],'DOJI_ADX_ADOSC':['INDICATOR:CDLDOJI','INDICATOR:ADX','INDICATOR:ADOSC']}


def audit():
    rows=[]
    for spec in assets():
        for minutes in [5,15,60]:
            for basis in ['trades','quotes']:
                status=case_status(ROOT,spec['id'],minutes,basis);directory=run_directory(status)
                if not directory or status['status']!='COMPLETED_WITH_EXPLICIT_LIMITATIONS' or not (directory/'joint_calibration.npz').exists():continue
                with np.load(directory/'joint_calibration.npz') as c:ids=c['candidate_ids'].tolist();votes=c['votes'];y=c['outcomes']
                for name,members in GROUPS.items():
                    base=dict(asset=spec['id'],minutes=minutes,basis=basis,group=name,members=members,identity=status['identity'],independent_untouched_validation=False,minimum_joint_matches=100,scope='Fixed exploratory retrospective groups; not independently pre-registered before earlier data inspection')
                    if any(cid not in ids for cid in members):rows.append(dict(base,status='BLOCKED_REQUIRED_MODELS_UNAVAILABLE'));continue
                    columns=[ids.index(cid) for cid in members];configurations={}
                    for number in range(2**len(columns)):
                        query=np.array([(number>>j)&1 for j in range(len(columns))]);mask=np.all(votes[:,columns]==query,axis=1);n=int(mask.sum())
                        if n>=100:configurations[tuple(query)]=(np.bincount(y[mask],minlength=3)/n).tolist()
                    if not configurations:rows.append(dict(base,status='INSUFFICIENT_JOINT_CALIBRATION_MATCHES'));continue
                    counts=np.bincount(y,minlength=3);baseline=counts/counts.sum()
                    for period in ['validation','retrospective_test']:
                        with np.load(directory/f'joint_{period}.npz') as e:v=e['votes'];actual=e['outcomes']
                        p=[];truth=[]
                        for number,row in enumerate(v[:,columns]):
                            probability=configurations.get(tuple(row))
                            if probability is not None:p.append(probability);truth.append(actual[number])
                        measured=metrics(np.array(truth),np.array(p));reference=metrics(np.array(truth),np.tile(baseline,(len(truth),1)));n=len(truth)
                        ci=interval(round(n*measured['accuracy']),n) if n else (None,None)
                        rows.append(dict(base,status='COMPLETED_EXPLORATORY_JOINT_REPLAY' if n else 'INSUFFICIENT_HELDOUT_MATCHES',period=period,total_eligible_outcomes=len(actual),covered_forecasts=n,coverage=n/len(actual) if len(actual) else None,accuracy=measured.get('accuracy'),balanced_accuracy=measured.get('balanced_accuracy'),baseline_accuracy=reference.get('accuracy'),accuracy_ci_low=ci[0],accuracy_ci_high=ci[1],brier=measured.get('brier'),log_loss=measured.get('log_loss'),configuration_probabilities={','.join(map(str,k)):value for k,value in configurations.items()},method='Actual JOINT calibration frequencies; no marginal probability multiplication'))
    result=dict(updated_at=utc_now(),groups=GROUPS,rows=rows);write_json(ROOT/'reports/multiasset/joint_audit.json',result);print('Joint agreement records',len(rows));return result

if __name__=='__main__':audit()
