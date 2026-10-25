"""Resumable checksum-verified Binance data. No source substitutes or gap filling."""
import argparse,concurrent.futures,io,json,os,time,urllib.error,urllib.request,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from btc_lab.data import sha256,write_json,utc_now,month_range,verify_archive,DataError
from multiasset.registry import ROOT,supplementary_asset as asset,supplementary_assets as assets
OUT=ROOT/'data/multiasset';RAW=OUT/'raw';REPORT=ROOT/'reports/multiasset'
COLS=['open','high','low','close','volume'];START='2020-01';END='2026-09'

def fetch(url,timeout=30):
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'ReproducibleMultiAssetLab/1.0'})
            with urllib.request.urlopen(req,timeout=timeout) as r:return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in [429,500,502,503,504] or attempt==3:raise
            time.sleep(min(2**attempt,4))
        except (TimeoutError,urllib.error.URLError):
            if attempt==3:raise
            time.sleep(min(2**attempt,4))

def validate(d,minutes):
    if d.empty or not d.index.is_unique or not d.index.is_monotonic_increasing or d.index.tz is None:raise DataError('Empty, unordered, duplicate or timezone-naive price data')
    if not d.index.equals(d.index.floor(f'{minutes}min')):raise DataError('Misaligned timestamps')
    a=d[COLS].to_numpy(float)
    if not np.isfinite(a).all() or (a[:,:4]<=0).any() or (a[:,4]<0).any():raise DataError('Invalid OHLCV values')
    if (d.high<d[['open','close','low']].max(axis=1)).any() or (d.low>d[['open','close','high']].min(axis=1)).any():raise DataError('Invalid high/low bounds')

def parse(body,name,kind):
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        expected=name[:-4]+'.csv'
        if z.namelist()!=[expected] or z.getinfo(expected).file_size>25_000_000:raise DataError('Unexpected archive contents or size')
        a=pd.read_csv(z.open(expected),header=None)
    # Futures files may contain an official column-header row; never coerce bad data.
    if str(a.iloc[0,0]) in ['open_time','openTime','calc_time','fundingTime']:a=a.iloc[1:].reset_index(drop=True)
    if kind=='funding':
        if a.shape[1]<3:raise DataError('Funding file has too few columns')
        t=pd.to_numeric(a[0],errors='raise').to_numpy(np.int64)
        d=pd.DataFrame(dict(rate=pd.to_numeric(a.iloc[:,-1],errors='raise').to_numpy(float),interval_hours=pd.to_numeric(a[1],errors='raise').to_numpy(float)),index=pd.to_datetime(t,unit='ms',utc=True));d.index.name='timestamp'
        if not d.index.is_unique or not d.index.is_monotonic_increasing or not np.isfinite(d.to_numpy()).all():raise DataError('Invalid funding observations')
        return d
    if a.shape[1]!=12:raise DataError('Expected 12 kline columns')
    t=pd.to_numeric(a[0],errors='raise').to_numpy(np.int64)
    d=a.iloc[:,1:6].astype(float);d.columns=COLS;d.index=pd.DatetimeIndex(pd.to_datetime(np.where(t>=100_000_000_000_000,t*1000,t*1_000_000),utc=True),name='timestamp');validate(d,5)
    return d

def monthly(spec,month,kind='klines'):
    symbol=spec['symbol'];base=spec['archive_market'];part=f'{symbol}/5m/{symbol}-5m-{month}.zip' if kind=='klines' else f'{symbol}/{symbol}-fundingRate-{month}.zip'
    name=part.rsplit('/',1)[-1];url=f'https://data.binance.vision/data/{base}/monthly/{kind}/{part}'
    cache=RAW/spec['id']/kind;cache.mkdir(parents=True,exist_ok=True);path=cache/name;cp=cache/(name+'.CHECKSUM')
    try:
        checksum=cp.read_bytes() if cp.exists() else fetch(url+'.CHECKSUM')
        body=path.read_bytes() if path.exists() else fetch(url)
        try:digest=verify_archive(body,checksum,name)
        except DataError:
            # Corrupted interrupted cache entries are replaced, never trusted.
            body=fetch(url);digest=verify_archive(body,checksum,name)
            temp=path.with_suffix('.tmp.zip');temp.write_bytes(body);temp.replace(path)
        d=parse(body,name,'funding' if kind=='fundingRate' else 'prices')
        if (d.index.strftime('%Y-%m')!=month).any():raise DataError('Archive observations outside named month')
        if not path.exists():
            temp=path.with_suffix('.tmp.zip');temp.write_bytes(body);temp.replace(path)
        if not cp.exists():cp.write_bytes(checksum)
        return d,dict(month=month,kind=kind,url=url,checksum_url=url+'.CHECKSUM',sha256=digest,status='CHECKSUM_VERIFIED',rows=len(d),first=d.index[0].isoformat(),last=d.index[-1].isoformat())
    except urllib.error.HTTPError as e:
        if e.code==404:return None,dict(month=month,kind=kind,url=url,status='ARCHIVE_NOT_AVAILABLE',http_status=404)
        return None,dict(month=month,kind=kind,url=url,status='DOWNLOAD_FAILED',error=str(e))
    except Exception as e:return None,dict(month=month,kind=kind,url=url,status='DOWNLOAD_FAILED',error=type(e).__name__+': '+str(e))

def aggregate(d,minutes):
    if minutes==5:return d.copy()
    r=d.resample(f'{minutes}min',origin='epoch',closed='left',label='left')
    out=r.agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).loc[r.size().eq(minutes//5)]
    validate(out,minutes);return out

def frame_meta(d,path,minutes):
    expected=pd.date_range(d.index[0],d.index[-1],freq=f'{minutes}min');missing=expected.difference(d.index)
    ret=d.close.pct_change();adjacent=d.index.to_series().diff().eq(pd.Timedelta(minutes=minutes));jumps=d.index[(ret.abs()>.5)&adjacent.to_numpy()]
    return dict(timeframe_minutes=minutes,path=str(path.relative_to(ROOT)),sha256=sha256(path.read_bytes()),rows=len(d),first=d.index[0].isoformat(),last=d.index[-1].isoformat(),internal_missing_candles=len(missing),missing_timestamps=[v.isoformat() for v in missing],large_adjacent_close_jumps_over_50pct=[t.isoformat() for t in jumps],large_jump_policy='Flag actual observations, do not smooth or fill; audit source archive evidence',aggregation='Original 5m prices' if minutes==5 else f'Only complete sets of {minutes//5} actual 5m candles')

def collect(ident,workers=8):
    spec=asset(ident);directory=OUT/ident;directory.mkdir(exist_ok=True,parents=True);mp=directory/'manifest.json'
    if mp.exists():
        existing=json.loads(mp.read_text())
        if existing.get('status')=='DATA_VERIFIED' and all((ROOT/x['path']).exists() and sha256((ROOT/x['path']).read_bytes())==x['sha256'] for x in existing['datasets']):
            print('REUSE',ident,flush=True);return existing
    if not spec['data_enabled']:
        m=dict(created_at=utc_now(),asset=spec,status='BLOCKED_INSTRUMENT_MAPPING',reason=spec['mapping_note'],datasets=[],archives=[]);write_json(mp,m);return m
    if ident=='BTC':
        from indicator_lab.data import load
        d,parent=load(5);records=parent['months'];frames=[d]
    else:
        items=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            for d,record in pool.map(lambda m:monthly(spec,m),month_range(START,END)):
                items.append((d,record));print('DATA',ident,record['month'],record['status'],flush=True)
        records=[r for d,r in items];frames=[d for d,r in items if d is not None]
    if not frames:
        m=dict(created_at=utc_now(),asset=spec,status='NO_VERIFIED_HISTORY',reason='No monthly source archive could be verified; inspect actual download failures',datasets=[],archives=records);write_json(mp,m);return m
    d=pd.concat(frames) if ident!='BTC' else frames[0];validate(d,5)
    datasets=[]
    for minutes in [5,15,60]:
        f=aggregate(d,minutes);p=directory/f'{ident}_{minutes}m.parquet';tmp=p.with_suffix('.tmp.parquet');f.to_parquet(tmp,compression='zstd',index=True);tmp.replace(p);datasets.append(frame_meta(f,p,minutes))
    funding=None
    if spec['market_type']=='USDT-margined perpetual':
        first=d.index[0].strftime('%Y-%m');items=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            for frame,rec in pool.map(lambda m:monthly(spec,m,'fundingRate'),month_range(first,END)):items.append((frame,rec))
        available=[frame for frame,r in items if frame is not None]
        if available:
            fd=pd.concat(available);p=directory/'funding.parquet';fd.to_parquet(p,compression='zstd');funding=dict(path=str(p.relative_to(ROOT)),sha256=sha256(p.read_bytes()),rows=len(fd),first=fd.index[0].isoformat(),last=fd.index[-1].isoformat(),archives=[r for _,r in items],status='RATES_VERIFIED_MARK_PRICE_PROXY_REQUIRED',limitations='Exact historical mark prices and liquidation/lot specifications are unavailable; funding can be estimated using observed candle opens, not presented as exact derivative execution')
        else:funding=dict(status='FUNDING_NOT_AVAILABLE',archives=[r for _,r in items])
    failures=[r for r in records if r.get('status')=='DOWNLOAD_FAILED']
    m=dict(created_at=utc_now(),asset=spec,status='DATA_VERIFIED' if not failures else 'PARTIAL_DOWNLOAD_FAILURES',requested_start='2020-01-01T00:00:00+00:00',requested_stop_exclusive='2026-10-01T00:00:00+00:00',history_before_first_observation='Unavailable; not filled or spliced from another market/token',archives=records,datasets=datasets,funding=funding,license='Binance dataset terms and CC BY-NC-SA 4.0; see sources/BINANCE_DATASET_TERMS.md',data_policy='No filling; only complete aggregate bars; gaps invalidate next-interval targets; independent source metadata retained')
    write_json(mp,m);return m

def load(ident,minutes):
    m=json.loads((OUT/ident/'manifest.json').read_text());item=next(x for x in m['datasets'] if x['timeframe_minutes']==minutes);p=ROOT/item['path']
    if sha256(p.read_bytes())!=item['sha256']:raise DataError('Price fingerprint changed: '+str(p))
    d=pd.read_parquet(p);validate(d,minutes)
    if len(d)!=item['rows']:raise DataError('Wrong price row count')
    return d,m

def main():
    p=argparse.ArgumentParser();p.add_argument('--asset');p.add_argument('--workers',type=int,default=8);a=p.parse_args()
    allrows=[]
    for spec in assets() if not a.asset else [asset(a.asset)]:
        try:allrows.append(collect(spec['id'],a.workers))
        except Exception as e:
            print('ASSET_DATA_ERROR',spec['id'],type(e).__name__,str(e),flush=True)
            write_json(OUT/spec['id']/'manifest.json',dict(created_at=utc_now(),asset=spec,status='DATA_COLLECTION_FAILED',reason=type(e).__name__+': '+str(e),datasets=[]))
    write_json(REPORT/'data_progress.json',dict(updated_at=utc_now(),assets=[dict(id=s['id'],manifest_path=f'data/multiasset/{s["id"]}/manifest.json') for s in assets()]))
if __name__=='__main__':main()
