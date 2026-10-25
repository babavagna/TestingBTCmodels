"""Read actual checkpoints into venue-separated reports; never create missing scores."""
import json
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
from multiasset.registry import ROOT,assets
from directional_study.metrics import interval

def read_json(path,default=None):
    try:return json.loads(Path(path).read_text())
    except (OSError,ValueError):return default

def run_directory(status,root=ROOT):return root/status['run_directory'] if status.get('run_directory') else None

def case_status(root,ident,minutes,basis):
    return read_json(root/f'reports/multiasset/primary/{ident}_{minutes}m_{basis}/status.json',{})

def failure_kind(row):
    s=row.get('reason','').lower()
    if any(t in s for t in ['need','training targets','constant','selection forecasts','class support','only ','insufficient','fewer than']):return 'INSUFFICIENT_HISTORY_OR_VARIATION'
    if 'trade-volume' in s or 'tradable' in s:return 'NO_EXECUTABLE_TRADE_OBSERVATIONS'
    if any(t in s for t in ['unavailable ohlcv','requires actual ohlcv','requires unavailable','quote-only','formula requires']):return 'MISSING_REQUIRED_INPUT_FIELDS'
    if 'causality' in s or 'lookahead' in s:return 'CAUSALITY_EXCLUDED'
    if str(row.get('status','')).startswith('BLOCKED'):return 'AUDITED_SOURCE_BLOCKED'
    return 'EXECUTION_ERROR'

def case_records(status,root=ROOT):
    directory=run_directory(status,root)
    if not directory or not directory.exists():return []
    out=[]
    for p in sorted(directory.glob('*.json')):
        if not p.name.startswith(('SOURCE_','INDICATOR_')):continue
        r=read_json(p)
        if r is not None and r.get('identity')==status.get('identity'):out.append(r)
    return out

def flat_result(record,status):
    out=[]
    for period in ['validation','retrospective_test']:
        value=record.get('periods',{}).get(period,{})
        stats=value.get('stats',{});direction=value.get('direction',{})
        row=dict(asset=status['asset']['id'],contract=status['asset']['symbol'],provider='Kalshi',market_type=status['asset']['market_type'],timeframe_minutes=status['minutes'],price_basis=status['price_basis'],candidate_id=record['candidate_id'],strategy=record.get('name'),family=record.get('family'),period=period,status=record['status'],executed=bool(record.get('executed')),reason=record.get('reason'),failure_kind=None if record.get('executed') else failure_kind(record),selected_profile=record.get('selected_profile'),source_url=record.get('source_url'),license=record.get('license'),training_start=status.get('dates',{}).get('fit',{}).get('start'),training_stop=status.get('dates',{}).get('selection',{}).get('stop'),score_start=status.get('dates',{}).get(period,{}).get('start'),score_stop=status.get('dates',{}).get(period,{}).get('stop'),source_partial=status.get('source_partial'),fully_validated_rank_eligible=False,funding_status='MISSING: not included in cost-limited derivatives replay',source_identity=status.get('identity'),**stats)
        n=direction.get('forecasts',0);up_calls=direction.get('tp',0)+direction.get('fp',0);down_calls=direction.get('tn',0)+direction.get('fn',0)
        up_interval=interval(direction.get('tp',0),up_calls);down_interval=interval(direction.get('tn',0),down_calls)
        baseline_up=record.get('model',{}).get('training_up_rate',.5)>=.5
        actual_up=direction.get('actual_up_rate')
        baseline=(actual_up if baseline_up else 1-actual_up) if actual_up is not None else None
        row.update(directional_accuracy=direction.get('accuracy'),balanced_accuracy=direction.get('balanced_accuracy'),up_precision=direction.get('up_precision'),up_recall=direction.get('up_recall'),down_precision=direction.get('down_precision'),down_recall=direction.get('down_recall'),forecasts=direction.get('forecasts'),up_calls=up_calls if direction else None,down_calls=down_calls if direction else None,few_up_calls=up_calls<100 if direction else None,few_down_calls=down_calls<100 if direction else None,too_few_forecasts=n<1000 if direction else None,up_precision_ci_low=up_interval[0],up_precision_ci_high=up_interval[1],down_precision_ci_low=down_interval[0],down_precision_ci_high=down_interval[1],training_majority_baseline_accuracy=baseline,accuracy_ci_low=direction.get('wilson_low'),accuracy_ci_high=direction.get('wilson_high'),directional_definition='Binary next close; exact ties excluded' if direction else record.get('directional_forecast_status','No completed forecast evaluation'),untouched_test=False,out_of_sample_validation='NOT INDEPENDENTLY VALIDATED: retrospective, limited history/cost coverage',data_path=status.get('dataset',{}).get('path'),data_sha256=status.get('dataset',{}).get('sha256'),historical_data_url=status.get('dataset',{}).get('source_url'),fee_per_side=.001,slippage_per_side=.0005,initial_capital=10000,implementation_scope='Signal-only long/cash projection, not native leveraged bot' if record['candidate_id'].startswith('SOURCE:') else 'One indicator plus train-only binary logistic readout')
        row['case_job_status']=status.get('status')
        if not record.get('executed') and period!='retrospective_test':continue
        out.append(row)
    return out

def probability_record(status,root=ROOT):
    directory=run_directory(status,root)
    if not directory:return None
    models=read_json(directory/'probabilities.json',[]) or []
    main=next((r for r in models if r['threshold']==.001),None)
    if main:
        main=dict(main);main['asset']=status['asset']['id'];main['contract']=status['asset']['symbol'];main['minutes']=status['minutes'];main['price_basis']=status['price_basis']
    return main

def current_record(status,root=ROOT):
    if not status or not status.get('identity'):return {}
    asset=status['asset']['id'];minutes=status['minutes'];basis=status['basis']
    row=read_json(root/f'reports/multiasset/current/{asset}_{minutes}m_{basis}.json',{}) or {}
    if row.get('identity')!=status['identity']:return {}
    if row.get('status')=='CURRENT':
        age=(pd.Timestamp.now(tz='UTC')-pd.Timestamp(row['as_of'])).total_seconds()
        if not 0<=age<minutes*60:return dict(row,status='STALE',probabilities=None,reason='Saved next-candle prediction target has closed; automated refresh required')
    return row

def build(root=ROOT):
    summary=[];results=[];probabilities=[];failures=[];sources=[];monthly=[];annual=[];robust=[];walk=[];correlations=[]
    for spec in assets():
        manifest=read_json(root/'data/kalshi'/spec['symbol']/'manifest.json',{}) or {}
        for minutes in [5,15,60]:
            statuses={b:case_status(root,spec['id'],minutes,b) for b in ['trades','quotes']}
            available={b:next((d for d in manifest.get('datasets',[]) if d['timeframe_minutes']==minutes and (('TRADED' in d['price_basis'])==(b=='trades'))),None) for b in ['trades','quotes']}
            counts={};proba=[]
            for basis,status in statuses.items():
                records=case_records(status,root);counts[basis]=dict(discovered=247,attempted=len(records),completed=sum(bool(r.get('executed')) for r in records),blocked=sum(not bool(r.get('executed')) for r in records))
                if status:
                    model=probability_record(status,root)
                    if model:probabilities.append(model);proba.append(model)
                directory=run_directory(status,root)
                if directory:
                    for cluster in read_json(directory/'signal_clusters.json',[]) or []:correlations.append(dict(asset=spec['id'],minutes=minutes,basis=basis,**cluster))
                for record in records:
                    results.extend(flat_result(record,status))
                    if not record.get('executed'):failures.append(dict(asset=spec['id'],contract=spec['symbol'],minutes=minutes,basis=basis,candidate_id=record['candidate_id'],name=record.get('name'),status=record['status'],failure_kind=failure_kind(record),reason=record.get('reason'),source_url=record.get('source_url')))
                    for period,p in record.get('periods',{}).items():
                        for row in p.get('monthly',[]):monthly.append(dict(asset=spec['id'],minutes=minutes,basis=basis,candidate_id=record['candidate_id'],period=period,**row))
                        for row in p.get('annual',[]):annual.append(dict(asset=spec['id'],minutes=minutes,basis=basis,candidate_id=record['candidate_id'],period=period,**row))
                    for row in record.get('sensitivity',[]):robust.append(dict(asset=spec['id'],minutes=minutes,basis=basis,candidate_id=record['candidate_id'],**row))
                    for row in record.get('walk_forward',[]):walk.append(dict(asset=spec['id'],minutes=minutes,basis=basis,candidate_id=record['candidate_id'],**row))
            chosen=next((m for m in proba if m['status']=='FITTED_AND_CALIBRATED' and 'TRADED' in m['price_basis']),None) or next((m for m in proba if m['status']=='FITTED_AND_CALIBRATED'),None)
            current={}
            if chosen:
                chosen_basis='trades' if chosen['price_basis']=='TRADED_CONTRACT_OHLCV' else 'quotes'
                current=current_record(statuses[chosen_basis],root)
            live=next((current_record(statuses[b],root) for b in ['trades','quotes'] if current_record(statuses[b],root).get('status')=='CURRENT'),None)
            if live:current=live
            reason=manifest.get('error') or (None if any(available.values()) else manifest.get('status','No primary Kalshi collection yet'))
            state='RUNNING_WITH_SAVED_CHECKPOINTS' if any(v.get('status')=='RUNNING' for v in statuses.values()) else ('RESULTS_AVAILABLE_WITH_LIMITATIONS' if any(v['completed'] for v in counts.values()) else 'NO_COMPLETED_MODEL_OR_BACKTEST')
            if not any(available.values()):state='NO_PRIMARY_OBSERVATIONS' if manifest.get('status')=='NO_OBSERVATIONS_IN_REQUESTED_PERIOD' else 'PRIMARY_RETRIEVAL_FAILED'
            summary.append(dict(asset=spec['id'],name=spec['name'],contract=spec['symbol'],category=spec['category'],market_type=spec['market_type'],requested_by_name=spec['requested_by_name'],timeframe_minutes=minutes,primary_provider='Kalshi',status=state,source_status=manifest.get('status'),source_error=reason,trade_candles=available['trades']['rows'] if available['trades'] else 0,trade_first=available['trades']['first'] if available['trades'] else None,trade_last=available['trades']['last'] if available['trades'] else None,quote_closes=available['quotes']['rows'] if available['quotes'] else 0,quote_first=available['quotes']['first'] if available['quotes'] else None,quote_last=available['quotes']['last'] if available['quotes'] else None,completed_trade_methods=counts['trades']['completed'],completed_quote_forecasters=counts['quotes']['completed'],attempted_trade_methods=counts['trades']['attempted'],attempted_quote_methods=counts['quotes']['attempted'],discovered_candidate_implementations=247,fully_validated_financial_strategies=0,probability_status=chosen['status'] if chosen else (proba[0]['status'] if proba else 'NO_FITTED_CALIBRATED_MODEL'),current_probability_status=chosen.get('current_status') if chosen else 'UNAVAILABLE',current_probabilities=chosen.get('current_probabilities') if chosen else None,historical_probabilities=chosen.get('historical_snapshot_probabilities') if chosen else None,last_price_as_of=chosen.get('last_price_as_of') if chosen else None,last_successful_model_update=chosen.get('last_successful_model_update') if chosen else None,contract_size=spec.get('contract_size'),underlying_multiplier=spec.get('underlying_multiplier'),tick_size=spec.get('tick_size'),source_url=spec['source_url']))
            for d in manifest.get('datasets',[]):
                if d['timeframe_minutes']==minutes:sources.append(dict(asset=spec['id'],contract=spec['symbol'],**d))
            if current:
                summary[-1].update(current_probability_status=current['status'],current_probability_reason=current.get('reason'),current_probability_price_basis=current.get('basis'),current_probabilities=current.get('probabilities') if current['status']=='CURRENT' else None,last_current_prediction_as_of=current.get('as_of'))
            summary[-1].update(trade_job_status=statuses['trades'].get('status'),quote_job_status=statuses['quotes'].get('status'),trade_job_reason=statuses['trades'].get('reason'),quote_job_reason=statuses['quotes'].get('reason'))
    return dict(updated_at=pd.Timestamp.now(tz='UTC').isoformat(),primary_venue='Kalshi',named_assets=28,discovered_contracts=len(assets()),summary=summary,results=results,probability_models=probabilities,failures=failures,data_sources=sources,monthly=monthly,annual=annual,robustness=robust,walk_forward=walk,correlations=correlations,fully_validated_financial_ranking=[],limitations=['Derivative funding/rollover/financing not verified; no fully validated financial ranking','Some contracts have no observations before September 2026','Partial retrieval and session gaps are explicit; no synthetic prices','Binance datasets are supplementary and never substituted for Kalshi','Three-class STAY threshold is ±0.10%; sensitivity ±0.05% and ±0.20%','Historical September snapshots are never labelled current in October'])
