"""Separate recent inference buffer; never append October to September backtests."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from btc_lab.data import write_json,utc_now,sha256
from multiasset.registry import ROOT,assets
from multiasset.kalshi import candle_window,ProviderError,save_frame,get_markets
from multiasset_report import case_status,case_records,run_directory,probability_record,read_json,current_record
from multiasset.probability import features,predict,targets,fit,calibrate,metrics
from multiasset.strategy_adapters import feature_frame
from indicator_lab.features import catalog
from indicator_lab.model import predict as binary_predict

OUT=ROOT/'reports/multiasset/current'
IMPLEMENTATION=sha256(Path(__file__).read_bytes())

def recent_window(ticker,minutes,start,stop):
    """Cache completed days, checkpointing every request so refreshes can resume."""
    from btc_lab.data import sha256
    directory=ROOT/'data/kalshi/current'/ticker;directory.mkdir(parents=True,exist_ok=True)
    path=directory/'recent_windows.json';ledger=read_json(path,{}) or {};key=str(minutes)+':'+start.isoformat()
    cached=ledger.get(key)
    if cached and cached['stop']==stop.isoformat() and minutes==1 and stop<=pd.Timestamp.now(tz='UTC').floor('D'):
        good=all((ROOT/cached[k]['path']).exists() and sha256((ROOT/cached[k]['path']).read_bytes())==cached[k]['sha256'] for k in ['trades','quotes'])
        if good:return pd.read_parquet(ROOT/cached['trades']['path']),pd.read_parquet(ROOT/cached['quotes']['path']),cached['evidence']
    trades,quotes,evidence=candle_window(ticker,minutes,start,stop)
    entry=dict(stop=stop.isoformat(),evidence=evidence)
    for kind,d in [('trades',trades),('quotes',quotes)]:entry[kind]=save_frame(d,directory/f'recent_{kind}_{minutes}m_{start:%Y-%m-%d}.parquet')
    ledger[key]=entry;write_json(path,ledger)
    return trades,quotes,evidence

def refit_recent(d,x,minutes):
    """Current-only rolling refit; frozen September results never change."""
    y,valid,decision,end,_=targets(d,minutes)
    valid &= np.isfinite(x).all(1)
    asof=d.index[-1]+pd.Timedelta(minutes=minutes)
    valid &= (decision>=asof-pd.Timedelta(days=30)) & (end<=asof)
    pos=np.flatnonzero(valid)
    if len(pos)<500:raise ValueError(f'Recent refit needs 500 valid targets in the past 30 days; got {len(pos)}')
    train_stop=decision[pos[int(len(pos)*.60)]];calibration_stop=decision[pos[int(len(pos)*.75)]]
    training=valid&(end<train_stop)
    calibration=valid&(decision>=train_stop)&(end<calibration_stop)
    evaluation=valid&(decision>=calibration_stop)
    model=calibrate(fit(x,y,training),x,y,calibration)
    scored=metrics(y[evaluation],predict(model,x[evaluation]))
    counts=np.asarray(model['training_counts']);baseline=np.tile(counts/counts.sum(),(int(evaluation.sum()),1))
    return model,dict(protocol='CURRENT_ONLY_ROLLING_30D: first60% fit, next15% calibration, last25% retrospective diagnostics. No selection on diagnostics; boundary labels purged.',training_start=decision[pos[0]].isoformat(),training_end=train_stop.isoformat(),calibration_end=calibration_stop.isoformat(),diagnostic_start=calibration_stop.isoformat(),diagnostic_stop=asof.isoformat(),diagnostic=scored,training_frequency_baseline=metrics(y[evaluation],baseline),independent_untouched_validation=False)


def infer(status,model,new,spec):
    from btc_lab.data import sha256
    if (spec.get('schedule') or {}).get('is_open') is False:raise ValueError('Kalshi reports this market closed; no current tradable prediction is displayed')
    if any(spec.get(key)!=status['asset'].get(key) for key in ['symbol','market_id','market_version','contract_size','underlying_multiplier','tick_size']):raise ValueError('Current contract specifications differ from the historical model identity; a new historical job is required')
    dataset=ROOT/status['dataset']['path']
    if sha256(dataset.read_bytes())!=status['dataset']['sha256']:raise ValueError('Historical dataset fingerprint changed')
    old=pd.read_parquet(dataset);d=pd.concat([old,new]).sort_index();d=d[~d.index.duplicated(keep='last')]
    if status['basis']=='quotes':d=d[['close']]
    x=features(d)
    if not np.isfinite(x[-1]).all():raise ValueError('Latest probability features unavailable; no earlier candle substituted')
    minutes=status['minutes'];asof=d.index[-1]+pd.Timedelta(minutes=minutes);now=pd.Timestamp.now(tz='UTC');age=(now-asof).total_seconds()
    if not 0<=age<minutes*60:raise ValueError('The next-candle prediction target has already closed, or its timestamp is invalid. Latest primary candle: '+asof.isoformat())
    current_model,refit=refit_recent(d,x,minutes)
    p=predict(current_model,x[-1:])[0].tolist();votes={};errors={};formulas={r['id']:r for r in catalog()}
    for record in case_records(status):
        cid=record['candidate_id']
        if not record.get('executed') or not cid.startswith('INDICATOR:'):continue
        try:
            a=feature_frame(formulas[cid.split(':',1)[1]],d,record['selected_profile'])
            if not np.isfinite(a[-1]).all():raise ValueError('Latest indicator features unavailable')
            votes[cid]=int(binary_predict(record['model'],a[-1:])[0]>=.5)
        except Exception as e:errors[cid]=str(e)
    buffer=ROOT/'data/kalshi/current'/spec['symbol'];buffer.mkdir(exist_ok=True,parents=True)
    source=save_frame(new,buffer/f'{status["basis"]}_{minutes}m.parquet')
    if pd.Timestamp.now(tz='UTC')>=asof+pd.Timedelta(minutes=minutes):raise ValueError('Prediction target closed while preparing the model; waiting for a newer completed candle')
    return dict(status='CURRENT',asset=spec['id'],contract=spec['symbol'],minutes=minutes,basis=status['basis'],identity=status['identity'],current_implementation_sha256=IMPLEMENTATION,updated_at=utc_now(),as_of=asof.isoformat(),forecast_target_at=(asof+pd.Timedelta(minutes=minutes)).isoformat(),probabilities=p,classes=['DOWN','STAY SIMILAR','UP'],predicted_direction=['DOWN','STAY SIMILAR','UP'][int(np.argmax(p))],threshold=.001,indicator_votes=votes,indicator_errors=errors,indicator_model_policy='Frozen earlier indicator readouts, preserving exact historical joint-configuration rules; no independence claim',training_end=refit['training_end'],calibration_end=refit['calibration_end'],current_model=current_model,current_model_sha256=sha256(json.dumps(current_model,sort_keys=True).encode()),rolling_refit=refit,source=source,historical_source=status['dataset'],price_role='PRIMARY_KALSHI_CONTRACT',backtest_history_unchanged=True)


def refresh(only_asset=None,only_minutes=None):
    OUT.mkdir(exist_ok=True,parents=True);now=pd.Timestamp.now(tz='UTC');stop=now.floor('min');models=[];breaker=None
    try:get_markets()
    except Exception as e:breaker='Cannot verify current contract metadata: '+str(e)
    for spec in assets():
        if only_asset and spec['id']!=only_asset:continue
        for minutes in [5,15,60]:
            if only_minutes and minutes!=only_minutes:continue
            for basis in ['trades','quotes']:
                status=case_status(ROOT,spec['id'],minutes,basis);model=probability_record(status)
                if status.get('identity') and status.get('dataset'):models.append((spec,status,model))
    count=0
    for spec in assets():
        selected=[(s,m) for a,s,m in models if a['id']==spec['id']]
        if not selected:continue
        stop=pd.Timestamp.now(tz='UTC').floor('min')
        history={};proof=[]
        try:
            if breaker:raise ProviderError('Recent collection paused after source failure; automatic scheduled retry: '+breaker)
            if any(s['minutes']==60 for s,m in selected):
                end=stop.floor('h');start=end-pd.Timedelta(days=30)
                t,q,e=recent_window(spec['symbol'],60,start,end);history[60]=(t,q);proof.append(e)
            if any(s['minutes']!=60 for s,m in selected):
                traded=[];quoted=[];begin=stop.floor('D')-pd.Timedelta(days=30)
                for start in pd.date_range(begin,stop,freq='D',inclusive='left'):
                    end=min(start+pd.Timedelta(days=1),stop)
                    t,q,e=recent_window(spec['symbol'],1,start,end);traded.append(t);quoted.append(q);proof.append(e)
                for minutes in [5,15]:
                    result=[]
                    for frames,basis in [(traded,'trades'),(quoted,'quotes')]:
                        d=pd.concat(frames).sort_index();r=d.resample(f'{minutes}min',origin='epoch');n=r.size()
                        a=r.agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}) if basis=='trades' else r.last()
                        result.append(a[n.eq(minutes)])
                    history[minutes]=tuple(result)
            for status,model in selected:
                path=OUT/f'{spec["id"]}_{status["minutes"]}m_{status["basis"]}.json'
                try:
                    new=history[status['minutes']][0 if status['basis']=='trades' else 1]
                    if not len(new):raise ValueError('Source returned no complete recent observations for this price basis')
                    result=infer(status,model,new,spec);result['source_requests']=proof;write_json(path,result);count+=1
                except Exception as e:write_json(path,dict(status='UNAVAILABLE',asset=spec['id'],identity=status['identity'],updated_at=utc_now(),reason=str(e),probabilities=None,source_requests=proof))
        except Exception as e:
            if isinstance(e,ProviderError) and not breaker:breaker=str(e)
            for status,model in selected:write_json(OUT/f'{spec["id"]}_{status["minutes"]}m_{status["basis"]}.json',dict(status='UNAVAILABLE',asset=spec['id'],identity=status['identity'],updated_at=utc_now(),reason=str(e),probabilities=None))
    fresh=sum(current_record(status).get('status')=='CURRENT' for _,status,_ in models)
    write_json(OUT/'status.json',dict(updated_at=utc_now(),scope_asset=only_asset,scope_minutes=only_minutes,eligible_models=len(models),generated_models=count,current_models=fresh,source_failure=breaker,history_policy='Separate recent inference buffers; never overwrite retrospective backtest inputs'))
    print('CURRENT_REFRESH generated',count,'of',len(models),'models; still current:',fresh,'; source failure:',breaker)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--asset');parser.add_argument('--minutes',type=int,choices=[5,15,60]);args=parser.parse_args();refresh(args.asset,args.minutes)
