"""Public Kalshi margin history collector; contract prices never replaced by proxies."""
import argparse,concurrent.futures,json,time,urllib.error,urllib.parse,urllib.request,threading
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from btc_lab.data import sha256,write_json,utc_now,DataError
from multiasset.registry import ROOT,assets
ORIGIN='https://external-api.kalshi.com/trade-api/v2/margin'
OUT=ROOT/'data/kalshi';REPORT=ROOT/'reports/kalshi'
START=pd.Timestamp('2020-01-01',tz='UTC');STOP=pd.Timestamp('2026-10-01',tz='UTC')
LOCK=threading.Lock();LAST_REQUEST=0.

class ProviderError(RuntimeError):
    def __init__(self,message,status=None):super().__init__(message);self.status=status

def request(path):
    global LAST_REQUEST
    url=ORIGIN+path
    for attempt in range(3):
        with LOCK:
            delay=.15-(time.monotonic()-LAST_REQUEST)
            if delay>0:time.sleep(delay)
            LAST_REQUEST=time.monotonic()
        try:
            req=urllib.request.Request(url,headers={'Accept':'application/json','User-Agent':'MultiAssetResearch/1.0'})
            with urllib.request.urlopen(req,timeout=20) as r:
                body=r.read();payload=json.loads(body)
                if not isinstance(payload,dict):raise ProviderError('Kalshi response is not a JSON object',r.status)
                return payload,dict(url=url,http_status=r.status,retrieved_at=utc_now(),response_sha256=sha256(body),bytes=len(body))
        except urllib.error.HTTPError as e:
            detail=e.read(1000).decode(errors='replace')
            if e.code in [429,500,502,503,504] and attempt<2:time.sleep(attempt+1);continue
            raise ProviderError(f'Kalshi HTTP {e.code}: {detail}',e.code) from e
        except (urllib.error.URLError,TimeoutError) as e:
            if '403' in str(e) or 'blocked' in str(e).lower():raise ProviderError('Network policy blocked Kalshi: '+str(e),403) from e
            if attempt<2:time.sleep(attempt+1);continue
            raise ProviderError('Kalshi connection unavailable: '+str(e)) from e

def get_markets():
    payload,evidence=request('/markets');markets=payload.get('markets')
    if not isinstance(markets,list) or not markets:raise ProviderError('Kalshi returned no usable margin market catalog')
    seen=set()
    for m in markets:
        if not isinstance(m,dict) or not isinstance(m.get('ticker'),str) or m['ticker'] in seen:raise ProviderError('Malformed or duplicate Kalshi contract')
        if not m['ticker'].startswith('KX') or not m['ticker'].endswith(('PERP','FUTURE')):raise ProviderError('Unexpected non-margin contract returned; no binary-price substitution allowed')
        seen.add(m['ticker'])
    OUT.mkdir(exist_ok=True,parents=True)
    result=dict(created_at=utc_now(),fresh_retrieval=True,source_url=evidence['url'],evidence=evidence,markets=markets)
    write_json(OUT/'markets.json',result);return result

def number(v):
    if v is None or v=='':return None
    try:n=float(v)
    except (TypeError,ValueError):return None
    return n if np.isfinite(n) else None

def parse_candles(payload,minutes,start,stop):
    rows=payload.get('candlesticks')
    if not isinstance(rows,list):raise ProviderError('Candlestick response lacks the expected list')
    clean=[];quotes=[];errors=[];step=pd.Timedelta(minutes=minutes)
    for item in rows:
        timestamp=number(item.get('end_period_ts'))
        if timestamp is None:errors.append('Missing end_period_ts');continue
        end=pd.Timestamp(int(timestamp),unit='s',tz='UTC');opening=end-step
        if opening<start or end>stop:continue
        if opening!=opening.floor(f'{minutes}min'):raise ProviderError('Misaligned Kalshi candle end timestamps')
        price=item.get('price') or {};vals=[number(price.get(k)) for k in ['open','high','low','close']];volume=number(item.get('volume'))
        if all(x is not None and x>0 for x in vals) and volume is not None and volume>=0:
            o,h,l,c=vals
            if h<max(o,l,c) or l>min(o,h,c):raise ProviderError('Kalshi reported invalid OHLC bounds')
            clean.append(dict(timestamp=opening,open=o,high=h,low=l,close=c,volume=volume))
        bid=number((item.get('bid') or {}).get('close'));ask=number((item.get('ask') or {}).get('close'))
        # Sentinel/empty asks must not become enormous made-up midpoint prices.
        if bid is not None and ask is not None and 0<bid<=ask<1e12 and ask/bid<100:
            quotes.append(dict(timestamp=opening,close=(bid+ask)/2,bid=bid,ask=ask))
    def frame(values,columns):
        if not values:return pd.DataFrame(columns=columns,index=pd.DatetimeIndex([],tz='UTC',name='timestamp'))
        d=pd.DataFrame(values).set_index('timestamp').sort_index()
        if not d.index.is_unique:
            # Identical boundary repeats are tolerated; conflicting observations aren't.
            if any(len(g.drop_duplicates())>1 for _,g in d.groupby(level=0)):raise ProviderError('Conflicting duplicate candle timestamps')
            d=d.loc[~d.index.duplicated(keep='last')]
        return d
    return frame(clean,['open','high','low','close','volume']),frame(quotes,['close','bid','ask']),dict(returned_rows=len(rows),complete_trade_ohlcv=len(clean),valid_quote_closes=len(quotes),invalid_rows=len(errors),invalid_reasons=sorted(set(errors)))

def candle_window(ticker,minutes,start,stop):
    query=urllib.parse.urlencode(dict(start_ts=int(start.timestamp()),end_ts=int(stop.timestamp()),period_interval=minutes))
    path='/markets/'+urllib.parse.quote(ticker,safe='')+'/candlesticks?'+query
    payload,evidence=request(path);pages=[dict(evidence)];seen=set()
    while payload.get('next_cursor'):
        cursor=payload['next_cursor']
        if cursor in seen or len(pages)>=100:raise ProviderError('Repeated/excessive history pagination; window not marked complete')
        seen.add(cursor);nextpage,proof=request(path+'&'+urllib.parse.urlencode({'cursor':cursor}))
        if not isinstance(nextpage.get('candlesticks'),list):raise ProviderError('Malformed history page')
        payload['candlesticks'].extend(nextpage['candlesticks']);payload['next_cursor']=nextpage.get('next_cursor');pages.append(proof)
    evidence.update(pages=pages.copy() if len(pages)>1 else None,page_count=len(pages))
    trades,quotes,stats=parse_candles(payload,minutes,start,stop)
    return trades,quotes,dict(**evidence,**stats,start=start.isoformat(),stop=stop.isoformat(),timeframe_minutes=minutes)

def save_frame(d,path):
    temp=path.with_suffix('.tmp.parquet');d.to_parquet(temp,index=True,compression='zstd');temp.replace(path)
    return dict(path=str(path.relative_to(ROOT)),sha256=sha256(path.read_bytes()),rows=len(d),first=d.index[0].isoformat() if len(d) else None,last=d.index[-1].isoformat() if len(d) else None)

def collect_market(spec,max_windows=180):
    ticker=spec['symbol'];directory=OUT/ticker;directory.mkdir(exist_ok=True,parents=True);checkpoint=directory/'checkpoint.json'
    ledger=json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(windows={})
    # Begin at the requested end and walk backward. Hourly monthly windows locate
    # actual availability without guessing a listing date from a ticker or UUID.
    months=list(pd.period_range('2020-01','2026-09',freq='M'))[::-1];new=0
    for period in months:
        key='60:'+str(period)
        if key in ledger['windows'] and ledger['windows'][key].get('status')=='COMPLETED':continue
        start=period.start_time.tz_localize('UTC');stop=(period+1).start_time.tz_localize('UTC')
        try:
            trades,quotes,evidence=candle_window(ticker,60,start,stop)
            entry=dict(status='COMPLETED',evidence=evidence)
            for kind,d in [('trades',trades),('quotes',quotes)]:
                if len(d):entry[kind]=save_frame(d,directory/f'{kind}_60m_{period}.parquet')
            ledger['windows'][key]=entry;write_json(checkpoint,ledger);new+=1
            print('KALSHI',ticker,key,'trades',len(trades),'quotes',len(quotes),flush=True)
        except Exception as e:
            ledger['windows'][key]=dict(status='REQUEST_FAILED',reason=str(e),attempted_at=utc_now());write_json(checkpoint,ledger)
            # A blocked API or invalid interval is not evidence of zero history.
            return finalize(spec,ledger,str(e))
        if new>=max_windows:return finalize(spec,ledger,'Historical scan budget reached; automatic job resumes remaining windows')
    # Retrieve 1m originals only in months where native 1h bars establish actual
    # history. Do not synthesize OHLC from midpoint closes or fill no-trade minutes.
    available=[p for p in months if any(ledger['windows'].get('60:'+str(p),{}).get(k) for k in ['trades','quotes'])]
    for period in available:
        days=pd.date_range(period.start_time.tz_localize('UTC'),(period+1).start_time.tz_localize('UTC'),freq='D',inclusive='left')
        for start in days:
            key='1:'+start.strftime('%Y-%m-%d')
            if key in ledger['windows'] and ledger['windows'][key].get('status')=='COMPLETED':continue
            stop=start+pd.Timedelta(days=1)
            try:
                trades,quotes,evidence=candle_window(ticker,1,start,stop);entry=dict(status='COMPLETED',evidence=evidence)
                for kind,d in [('trades',trades),('quotes',quotes)]:
                    if len(d):entry[kind]=save_frame(d,directory/f'{kind}_1m_{start:%Y-%m-%d}.parquet')
                ledger['windows'][key]=entry;write_json(checkpoint,ledger);new+=1
            except Exception as e:
                ledger['windows'][key]=dict(status='REQUEST_FAILED',reason=str(e),attempted_at=utc_now());write_json(checkpoint,ledger);return finalize(spec,ledger,str(e))
            if new>=max_windows:return finalize(spec,ledger,'Historical scan budget reached; automatic job resumes remaining windows')
    return finalize(spec,ledger,None)

def finalize(spec,ledger,error):
    directory=OUT/spec['symbol'];datasets=[]
    for minutes in [5,15,60]:
        for basis in ['trades','quotes']:
            # Hourly native OHLC remains actual provider bars; other intervals are
            # built only from complete actual 1m groups, never invented extrema.
            matching=[r[basis] for key,r in ledger['windows'].items() if r.get('status')=='COMPLETED' and key.startswith('60:' if minutes==60 else '1:') and basis in r]
            if not matching:continue
            d=pd.concat([pd.read_parquet(ROOT/m['path']) for m in matching]).sort_index()
            if not d.index.is_unique:
                if any(len(g.drop_duplicates())>1 for _,g in d.groupby(level=0)):raise DataError('Conflicting history while merging Kalshi observations')
                d=d.loc[~d.index.duplicated(keep='last')]
            if minutes!=60:
                r=d.resample(f'{minutes}min',origin='epoch',closed='left',label='left');count=r.size()
                if basis=='trades':d=r.agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})
                else:d=r.last()
                d=d.loc[count.eq(minutes)]
            if d.empty:continue
            p=directory/f'{basis}_{minutes}m.parquet';meta=save_frame(d,p)
            gaps=pd.date_range(d.index[0],d.index[-1],freq=f'{minutes}min').difference(d.index)
            datasets.append(dict(**meta,timeframe_minutes=minutes,price_basis='TRADED_CONTRACT_OHLCV' if basis=='trades' else 'OBSERVED_BID_ASK_MIDPOINT_CLOSE_ONLY',provider='Kalshi',market_type=spec['market_type'],quote_currency='USD',contract_ticker=spec['symbol'],missing_calendar_slots=len(gaps),missing_slot_policy='May include closures/no trades; historical session calendar not verified. Never fill; no next-interval target crosses a gap.',ohlcv_complete=basis=='trades',source_url=ORIGIN+'/markets/'+spec['symbol']+'/candlesticks'))
    status='HISTORY_READY' if datasets and not error else ('PARTIAL_HISTORY' if datasets else ('RETRIEVAL_FAILED' if error else 'NO_OBSERVATIONS_IN_REQUESTED_PERIOD'))
    m=dict(created_at=utc_now(),asset=spec,primary_venue='Kalshi',status=status,error=error,datasets=datasets,windows_completed=sum(v.get('status')=='COMPLETED' for v in ledger['windows'].values()),requested_start=START.isoformat(),requested_stop_exclusive=STOP.isoformat(),history_policy='Primary Kalshi contract quotes/trades only. No Binance/spot/CFD substitution. Missing provider rows are not invented.',funding_status='Historical per-contract funding/rollover/financing series not yet verified; financial validation must fail closed',session_status='Source contract schedule preserved; historical holiday/session calendar unverified')
    write_json(directory/'manifest.json',m);return m

def collect(workers=3,max_windows=180,only=None):
    OUT.mkdir(exist_ok=True,parents=True);REPORT.mkdir(exist_ok=True,parents=True)
    try:get_markets()
    except Exception as e:
        # An earlier observed registry can support the UI, never current prices.
        failure=dict(attempted_at=utc_now(),status='KALSHI_MARKET_DISCOVERY_BLOCKED',reason=str(e),source_url=ORIGIN+'/markets',fresh_quotes_available=False)
        write_json(REPORT/'discovery.json',failure)
        rows=[]
        for spec in assets():
            directory=OUT/spec['symbol'];directory.mkdir(exist_ok=True,parents=True)
            m=dict(created_at=utc_now(),asset=spec,primary_venue='Kalshi',status='BLOCKED_NETWORK_OR_PROVIDER',error=str(e),datasets=[],requested_start=START.isoformat(),requested_stop_exclusive=STOP.isoformat(),fresh_quotes_available=False)
            # Never destroy previously retrieved and audited candles on failure.
            existing=directory/'manifest.json'
            if not existing.exists():write_json(existing,m)
            rows.append(dict(id=spec['id'],symbol=spec['symbol'],status=m['status'],reason=str(e)))
        write_json(REPORT/'collection_status.json',dict(updated_at=utc_now(),markets=rows,discovery=failure));print('PRIMARY_COLLECTION_BLOCKED',str(e),flush=True);return
    specs=[s for s in assets() if not only or s['id']==only or s['symbol']==only]
    rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(collect_market,s,max_windows):s for s in specs}
        for future in concurrent.futures.as_completed(futures):
            spec=futures[future]
            try:m=future.result();rows.append(dict(id=spec['id'],symbol=spec['symbol'],status=m['status'],reason=m.get('error')))
            except Exception as e:rows.append(dict(id=spec['id'],symbol=spec['symbol'],status='COLLECTION_ERROR',reason=str(e)))
            write_json(REPORT/'collection_status.json',dict(updated_at=utc_now(),markets=rows))
    print('PRIMARY_COLLECTION_FINISHED',len(rows),'contracts',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--asset');p.add_argument('--workers',type=int,default=3);p.add_argument('--max-windows',type=int,default=180);a=p.parse_args();collect(a.workers,a.max_windows,a.asset)
