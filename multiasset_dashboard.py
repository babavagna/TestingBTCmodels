"""Beginner UI for actual venue-separated results. No orders or invented forecasts."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
from multiasset.registry import assets
from multiasset_report import read_json,case_status,case_records,run_directory,probability_record,current_record
from multiasset.probability import joint_outcomes
from directional_study.metrics import interval

def pct(v):return 'N/A' if v is None else f'{v:.2%}'

def plain_problem(reason):
    value=str(reason)
    if '503' in value:return 'This environment could not reach Kalshi (HTTP 503). Automatic retries are enabled; missing prices are not invented.'
    if '403' in value:return 'Access to Kalshi was blocked (HTTP 403). The source error is saved in the coverage report.'
    if value=='NO_OBSERVATIONS_IN_REQUESTED_PERIOD':return 'Kalshi returned no observations during the requested January 2020–September 2026 period.'
    return value

def render(root):
    root=Path(root)
    if not (root/'sources/multiasset/original_dashboard_markets.json').exists():return
    st.subheader('Multi-asset research · primary Kalshi contracts')
    st.caption('28 requested assets plus 11 contracts discovered in the original dashboard. Binance research is supplementary, not Kalshi contract evidence. No live orders are placed.')
    report=read_json(root/'reports/multiasset/summary.json',{}) or {}
    st.warning('Financial results are exploratory: verified historical funding, financing and rollover costs are missing. No strategy is ranked as fully validated for live Kalshi execution.')
    if st.button('Refresh current Kalshi probabilities',key='refresh_kalshi_current'):
        import subprocess,sys
        with st.status('Requesting recent Kalshi prices; this request has a two-minute limit.',expanded=True) as progress:
            try:
                process=subprocess.run([sys.executable,'-m','scripts.refresh_kalshi_current'],cwd=root,capture_output=True,text=True,timeout=120)
                current_status=read_json(root/'reports/multiasset/current/status.json',{}) or {}
                count=current_status.get('current_models',0)
                if process.returncode or not count:progress.update(label='No fresh predictions available: '+plain_problem(current_status.get('source_failure') or process.stderr[-300:] or 'Insufficient recent observations'),state='error')
                else:progress.update(label=f'{count} calibrated models updated from primary Kalshi prices.',state='complete')
            except subprocess.TimeoutExpired:progress.update(label='Time limit reached. Saved checkpoints remain available; automatic retries continue.',state='error')
    minutes=st.selectbox('Multi-asset timeframe',[5,15,60],format_func=lambda n:'1 hour' if n==60 else f'{n} minutes',key='multi_tf')
    for filename,label in [('KALSHI_MULTI_ASSET_RESEARCH.xlsx','Download multi-asset Excel'),('reports/multiasset/primary_results.csv','Download multi-asset CSV')]:
        path=root/filename
        if path.exists():st.download_button(label,path.read_bytes(),file_name=path.name,key='multi_download_'+path.name)
    specs=assets();tabs=st.tabs([s['id'] for s in specs])
    for tab,spec in zip(tabs,specs):
        with tab:
            st.write(f"**{spec['name']} · {spec['symbol']}** · {spec['market_type']}")
            st.caption(f"Kalshi · contract size {spec.get('contract_size','unverified')} · underlying multiplier {spec.get('underlying_multiplier','unverified')} · tick {spec.get('tick_size','unverified')}")
            manifest=read_json(root/'data/kalshi'/spec['symbol']/'manifest.json',{}) or {}
            datasets=[d for d in manifest.get('datasets',[]) if d['timeframe_minutes']==minutes]
            if not datasets:
                reason=manifest.get('error') or manifest.get('status','Primary source has not been retrieved')
                st.info('No primary Kalshi observations available for this chart. '+plain_problem(reason));st.caption('No strategy score or current probability is invented for this case.');continue
            coverage=pd.DataFrame([dict(Basis=d['price_basis'],Observations=d['rows'],First=d['first'],Last=d['last']) for d in datasets]);st.dataframe(coverage,hide_index=True,use_container_width=True)
            choices=['trades' if d['price_basis']=='TRADED_CONTRACT_OHLCV' else 'quotes' for d in datasets]
            basis=st.radio('Price basis · '+spec['id'],choices,format_func=lambda b:'Actual traded OHLCV' if b=='trades' else 'Observed bid/ask midpoint close only',horizontal=True,key='basis_'+spec['id'])
            status=case_status(root,spec['id'],minutes,basis)
            if not status:
                st.info('No completed job for this primary dataset yet. The automated resumable runner records each candidate as it finishes.');continue
            if status.get('status')=='RUNNING':
                age=(pd.Timestamp.now(tz='UTC')-pd.Timestamp(status['updated_at'])).total_seconds()
                st.info(('Testing' if age<600 else 'Checkpoint saved; worker may be paused')+f" · {status.get('attempted',0)} / 247 candidates · last: {status.get('last_candidate','starting')}")
            elif str(status.get('status','')).startswith('BLOCKED'):
                st.info(status.get('reason',status['status']));continue
            else:st.caption(f"{status.get('completed',0)} methods completed; {status.get('blocked',0)} blocked; {status.get('failed',0)} insufficient/failed attempts. All limitations remain visible.")
            model=probability_record(status,root)
            if model and model.get('status')=='FITTED_AND_CALIBRATED':
                fresh=current_record(status,root)
                current=fresh.get('probabilities') if fresh.get('status')=='CURRENT' else model.get('current_probabilities');asof=fresh.get('as_of') if fresh.get('status')=='CURRENT' else model.get('last_price_as_of')
                # Recheck age at display time; a saved CURRENT flag never remains current forever.
                age=(pd.Timestamp.now(tz='UTC')-pd.Timestamp(asof)).total_seconds() if asof else float('inf')
                if age>max(minutes*120,600):current=None
                if current is not None:
                    a,b,c=st.columns(3);a.metric('UP',pct(current[2]));b.metric('STAY SIMILAR',pct(current[1]));c.metric('DOWN',pct(current[0]));st.caption('Calibrated model estimate, not guaranteed accuracy. Latest closed candle: '+str(asof))
                    if fresh.get('rolling_refit'):
                        refit=fresh['rolling_refit'];measured=refit['diagnostic'];baseline=refit['training_frequency_baseline']
                        st.caption('Current model refitted on the preceding 30 days; training ends '+refit['training_end']+'. Recent held-out diagnostic: '+pct(measured.get('accuracy'))+' versus baseline '+pct(baseline.get('accuracy'))+' on '+str(measured.get('observations'))+' forecasts. September results below remain a separate frozen study.')
                else:
                    st.info('No current probability: latest stored prediction uses '+str(asof)+'. Historical results are available below; stale percentages are not shown as current.')
                    if fresh.get('reason'):st.caption('Latest automatic refresh: '+plain_problem(fresh['reason']))
                with st.expander('Historical three-outcome model and calibration · '+spec['id']):
                    st.write('STAY SIMILAR means a next-close change between −0.10% and +0.10%. Sensitivity uses ±0.05% and ±0.20%.')
                    p=model.get('historical_snapshot_probabilities');st.write('Historical snapshot: UP '+pct(p[2])+' · STAY '+pct(p[1])+' · DOWN '+pct(p[0]))
                    for period in ['validation','retrospective_test']:
                        block=model.get('periods',{}).get(period,{});m=block.get('calibrated',{});base=block.get('training_frequency_baseline',{})
                        n=m.get('observations',0);ci=interval(round(m['accuracy']*n),n) if m.get('accuracy') is not None else (None,None)
                        st.write(f"{period}: {n} forecasts · accuracy {pct(m.get('accuracy'))} · majority baseline {pct(base.get('accuracy'))} · balanced accuracy {pct(m.get('balanced_accuracy'))} · descriptive 95% interval {pct(ci[0])}–{pct(ci[1])}")
                        st.caption('Brier '+str(m.get('brier'))+' · log loss '+str(m.get('log_loss'))+' · calibration error '+str(m.get('ece')))
                    st.caption('Fit ends '+model.get('training_end','N/A')+'; calibration ends '+model.get('calibration_end','N/A')+'. High STAY accuracy is not automatically directional skill.')
            else:st.info('No calibrated model for this dataset: '+str((model or {}).get('calibration_error') or (model or {}).get('reason') or 'A fitted/calibrated checkpoint is not available'))
            records=case_records(status,root);completed=[r for r in records if r.get('executed')];directory=run_directory(status,root)
            if not completed:
                reasons=[r.get('reason') for r in records if r.get('reason')];st.info('No methods completed with sufficient inputs. '+str(reasons[0] if reasons else status.get('reason','See source status.')));continue
            rows=[]
            for r in completed:
                p=r.get('periods',{}).get('retrospective_test',{});s=p.get('stats',{});a=p.get('direction',{})
                rows.append(dict(ID=r['candidate_id'],Strategy=r['name'],Status=r['status'],Accuracy=a.get('accuracy'),Forecasts=a.get('forecasts',0),UP_precision=a.get('up_precision'),DOWN_precision=a.get('down_precision'),UP_recall=a.get('up_recall'),DOWN_recall=a.get('down_recall'),Fee_slippage_return=s.get('net_return'),Sharpe=s.get('sharpe'),Sortino=s.get('sortino'),Drawdown=s.get('max_drawdown'),Profit_factor=s.get('profit_factor'),Trade_win_rate=s.get('win_rate'),Trades=s.get('trades'),Buy_and_hold=s.get('buy_hold_return')))
            frame=pd.DataFrame(rows)
            minimum=st.slider('Minimum measured accuracy · '+spec['id'],0,100,0,key='accuracy_'+spec['id'])/100
            sample=st.number_input('Minimum forecasts · '+spec['id'],min_value=0,value=0,step=100,key='sample_'+spec['id'])
            filtered=frame[(frame.Forecasts>=sample)&((frame.Accuracy>=minimum)|(frame.Accuracy.isna()&(minimum==0)))]
            st.dataframe(filtered,hide_index=True,use_container_width=True)
            st.caption('Indicator accuracy belongs to the indicator plus a trained prediction rule. Native trading entries/exits have no per-candle prediction accuracy. Returns exclude unverified derivative funding/financing. Methods are not ranked as fully validated.')
            st.download_button('Download these rows · '+spec['id'],filtered.to_csv(index=False).encode(),file_name=f'{spec["id"]}_{minutes}m_{basis}.csv',mime='text/csv',key='csv_'+spec['id'])
            with st.expander('Compare equity curves · '+spec['id']):
                choices=[r['candidate_id'] for r in completed if r.get('periods',{}).get('retrospective_test',{}).get('curve')]
                selected=st.multiselect('Strategies · '+spec['id'],choices,default=choices[:min(2,len(choices))],key='curves_'+spec['id'])
                curves={}
                for cid in selected:
                    r=next(r for r in completed if r['candidate_id']==cid);curve=r['periods']['retrospective_test']['curve'];curves[cid]=pd.Series(curve['equity'],index=pd.to_datetime(curve['date'],utc=True))
                if curves:st.line_chart(pd.DataFrame(curves));st.caption('Actual saved daily account curves; fees/slippage and whole-contract sizing included. Funding/rollover omitted.')
                if basis=='trades' and choices:
                    pick=st.selectbox('Strategy for date replay · '+spec['id'],choices,key='replay_pick_'+spec['id'])
                    bounds=status['dates']['retrospective_test'];lo=pd.Timestamp(bounds['start']).date();hi=(pd.Timestamp(bounds['stop'])-pd.Timedelta(nanoseconds=1)).date()
                    left,right=st.columns(2)
                    start=left.date_input('Replay start · '+spec['id'],lo,min_value=lo,max_value=hi,key='start_'+spec['id']);end=right.date_input('Replay end · '+spec['id'],hi,min_value=lo,max_value=hi,key='end_'+spec['id'])
                    if st.button('Replay chosen dates · '+spec['id'],key='replay_'+spec['id']):
                        try:
                            from multiasset.engine import portfolio
                            if end<start:raise ValueError('End must not precede start')
                            dataset=root/status['dataset']['path']
                            from btc_lab.data import sha256
                            if sha256(dataset.read_bytes())!=status['dataset']['sha256']:raise ValueError('Audited price fingerprint changed')
                            d=pd.read_parquet(dataset);r=next(r for r in completed if r['candidate_id']==pick);cache=directory/(pick.replace(':','_')+'.npz')
                            if sha256(cache.read_bytes())!=r['signal_cache_sha256']:raise ValueError('Saved signal fingerprint changed')
                            with np.load(cache) as a:signal=a['signal'].astype(float)
                            signal[signal<0]=np.nan
                            begin=max(pd.Timestamp(start,tz='UTC'),pd.Timestamp(bounds['start']));finish=min(pd.Timestamp(end,tz='UTC')+pd.Timedelta(days=1),pd.Timestamp(bounds['stop']))
                            stats,curve,_,_=portfolio(d,signal,minutes,spec,begin,finish);st.json(stats);st.line_chart(pd.Series(curve['equity'],index=pd.to_datetime(curve['date'])))
                        except Exception as e:st.error(str(e))
                    st.caption('Date replay is restricted to the already-heldout period, so saved models are not evaluated before their training cutoffs.')
            if directory and (directory/'joint_calibration.npz').exists():
                with st.expander('Indicator selection and joint outcomes · '+spec['id']):
                    with np.load(directory/'joint_calibration.npz') as j:
                        ids=j['candidate_ids'].tolist();votes=j['votes'];outcomes=j['outcomes']
                    available=[i for i in ids if i.startswith('INDICATOR:')]
                    selected=st.multiselect('Indicators used together · '+spec['id'],available,default=available[:min(3,len(available))],key='joint_'+spec['id'])
                    selected=[cid for cid in selected if st.checkbox('Include '+cid+' · '+spec['id'],value=True,key='include_'+spec['id']+'_'+cid)]
                    if selected:
                        current=np.full(len(ids),-1,np.int8)
                        fresh=current_record(status,root)
                        for cid in selected:
                            p=directory/(cid.replace(':','_')+'.npz')
                            if fresh.get('status')=='CURRENT':current[ids.index(cid)]=fresh.get('indicator_votes',{}).get(cid,-1)
                            elif p.exists():
                                with np.load(p) as a:current[ids.index(cid)]=a['signal'][-1]
                        estimate=joint_outcomes(votes,outcomes,[ids.index(cid) for cid in selected],current)
                        st.write(('Current indicator agreement' if fresh.get('status')=='CURRENT' else 'HISTORICAL-SNAPSHOT agreement, not current')+': '+str(estimate['observations'])+' matching calibration cases.')
                        st.caption('Selected votes: '+', '.join(cid+' '+({0:'DOWN',1:'UP'}.get(int(current[ids.index(cid)]),'unavailable')) for cid in selected))
                        if estimate['probabilities'] is not None:
                            p=estimate['probabilities'];st.write('DOWN '+pct(p[0])+' · STAY '+pct(p[1])+' · UP '+pct(p[2]))
                            ranges=[interval(n,estimate['observations']) for n in estimate['counts']];st.caption('Descriptive class intervals: '+str(ranges))
                        else:st.info(estimate['status']+': needs at least 100 matching cases and available selected signals.')
                        st.caption('Uses historically observed JOINT outcomes. No multiplication or independence assumption. New selections remain exploratory.')
    with st.expander('Supplementary external data inventory — not Kalshi backtests'):
        entries=[]
        for path in sorted((root/'data/multiasset').glob('*/manifest.json')):
            m=read_json(path,{}) or {}
            for d in m.get('datasets',[]):entries.append(dict(Asset=path.parent.name,Provider=m['asset']['provider'],Market=m['asset']['market_type'],Chart=d['timeframe_minutes'],Rows=d['rows'],First=d['first'],Last=d['last']))
        if entries:st.dataframe(pd.DataFrame(entries),hide_index=True,use_container_width=True)
        st.caption('These Binance observations are source-verified supplementary research only. No row above substitutes them for a Kalshi contract.')
