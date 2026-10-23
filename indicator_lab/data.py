"""Official checksum-verified five-minute prices; complete-candle aggregation only."""
import concurrent.futures,io,json,urllib.error,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from btc_lab.data import fetch,verify_archive,sha256,write_json,utc_now,month_range,DataError
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/predictions'
COLS=['open','high','low','close','volume']
START=pd.Timestamp('2020-01-01',tz='UTC');STOP=pd.Timestamp('2026-10-01',tz='UTC')

def validate(d,minutes):
    if d.empty or not d.index.is_monotonic_increasing or not d.index.is_unique or d.index.tz is None:raise DataError('Bad timestamp ordering or empty prices')
    if not d.index.equals(d.index.floor(f'{minutes}min')):raise DataError('Candles are not aligned to their interval')
    a=d[COLS].to_numpy(float)
    if not np.isfinite(a).all() or (a[:,:4]<=0).any() or (a[:,4]<0).any():raise DataError('Invalid price/volume data')
    if (d.high<d[['open','low','close']].max(axis=1)).any() or (d.low>d[['open','high','close']].min(axis=1)).any():raise DataError('Invalid OHLC range')

def one_month(month):
    cache=OUT/'raw';cache.mkdir(parents=True,exist_ok=True)
    name=f'BTCUSDT-5m-{month}.zip';url=f'https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/5m/{name}'
    checksum=fetch(url+'.CHECKSUM');p=cache/name
    body=p.read_bytes() if p.exists() else fetch(url)
    digest=verify_archive(body,checksum,name)
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        expected=name[:-4]+'.csv'
        if z.namelist()!=[expected] or z.getinfo(expected).file_size>20_000_000:raise DataError('Unexpected five-minute archive contents')
        a=pd.read_csv(z.open(expected),header=None)
    if a.shape[1]!=12:raise DataError('Expected 12 Binance kline columns')
    t=pd.to_numeric(a[0],errors='raise').to_numpy(np.int64)
    ns=np.where(t>=100_000_000_000_000,t*1000,t*1_000_000)
    d=a.iloc[:,1:6].astype(float);d.columns=COLS;d.index=pd.DatetimeIndex(pd.to_datetime(ns,utc=True),name='timestamp')
    validate(d,5)
    if not (d.index.strftime('%Y-%m')==month).all():raise DataError('Wrong archive month')
    if not p.exists():p.write_bytes(body)
    (cache/(name+'.CHECKSUM')).write_bytes(checksum)
    print(month,len(d),'checksum verified',flush=True)
    return d,dict(month=month,url=url,checksum_url=url+'.CHECKSUM',archive_sha256=digest,rows=len(d),first=d.index[0].isoformat(),last=d.index[-1].isoformat(),status='verified')

def aggregate(d,minutes):
    if minutes==5:return d.copy()
    ratio=minutes//5
    grouped=d.resample(f'{minutes}min',origin='epoch',label='left',closed='left')
    result=grouped.agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})
    counts=grouped.size()
    # A bin needs every expected five-minute timestamp. No partially formed or
    # gap-filled 15m/1h candle may enter forecasts.
    result=result.loc[counts.eq(ratio)]
    validate(result,minutes)
    return result

def download():
    OUT.mkdir(parents=True,exist_ok=True);items=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(one_month,month_range('2020-01','2026-09')):items.append(result)
    d=pd.concat([x[0] for x in items]);validate(d,5)
    if d.index[0]!=START or d.index[-1]!=STOP-pd.Timedelta(minutes=5):raise DataError('Requested first/last five-minute candle unavailable; refusing to invent coverage')
    datasets=[]
    for minutes in (5,15,60):
        frame=aggregate(d,minutes);path=OUT/f'btcusdt_{minutes}m.csv.gz';frame.to_csv(path,compression={'method':'gzip','mtime':0})
        expected=pd.date_range(START,STOP,freq=f'{minutes}min',inclusive='left')
        missing=expected.difference(frame.index)
        datasets.append(dict(timeframe_minutes=minutes,path=str(path.relative_to(ROOT)),sha256=sha256(path.read_bytes()),rows=len(frame),first=frame.index[0].isoformat(),last=frame.index[-1].isoformat(),missing_candles=len(missing),missing_timestamps=[t.isoformat() for t in missing],derivation='Official 5m observations' if minutes==5 else f'Aggregate only complete groups of {minutes//5} verified 5m observations'))
    manifest=dict(created_at=utc_now(),exchange='Binance spot',symbol='BTCUSDT',source='https://github.com/binance/binance-public-data',license='CC BY-NC-SA 4.0 and saved Binance dataset terms',start=START.isoformat(),stop_exclusive=STOP.isoformat(),months=[x[1] for x in items],datasets=datasets,gap_policy='No filling; discard incomplete aggregation bins; indicator periods count observed bars; score labels only across adjacent complete candles')
    write_json(OUT/'manifest.json',manifest)
    return manifest

def load(minutes):
    m=json.loads((OUT/'manifest.json').read_text());s=next(x for x in m['datasets'] if x['timeframe_minutes']==minutes);p=ROOT/s['path']
    if sha256(p.read_bytes())!=s['sha256']:raise DataError('Forecast price file changed')
    d=pd.read_csv(p,index_col='timestamp',parse_dates=True);d.index=pd.to_datetime(d.index,utc=True);validate(d,minutes)
    if len(d)!=s['rows']:raise DataError('Row count differs from verified manifest')
    return d,m

if __name__=='__main__':download()
