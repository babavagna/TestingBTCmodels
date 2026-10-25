"""Read-only, closed-candle BTC signal API. Run: python live_signal_server.py.
Reuses frozen research models and replays all verified history; never places orders.
"""
import hashlib, json, math, os, threading, time, urllib.request, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IDS = 'CDLSTICKSANDWICH CDLTRISTAR CDL3BLACKCROWS CDL3LINESTRIKE CDLGAPSIDESIDEWHITE CDLMORNINGDOJISTAR CDLMORNINGSTAR CDLRISEFALL3METHODS ADOSC CDLADVANCEBLOCK EFI CDLHANGINGMAN EOM CDLXSIDEGAP3METHODS CDLSEPARATINGLINES CDLMARUBOZU DPO CDLDOJISTAR CDLSTALLEDPATTERN CDL3OUTSIDE CDLHIGHWAVE CDLRICKSHAWMAN CDLGRAVESTONEDOJI CDLLONGLEGGEDDOJI ATR NATR CDLDOJI CDLTAKURI CDLHIKKAKE STDDEV CDLHARAMICROSS TRANGE RVOL CDLDRAGONFLYDOJI CORREL'.split()
IDS_15 = 'CORREL CDLRISEFALL3METHODS CDLIDENTICAL3CROWS EFI CDLTAKURI CDLDRAGONFLYDOJI CDLSEPARATINGLINES EOM CDLSTALLEDPATTERN CDLDOJISTAR ADOSC CDLHARAMICROSS CDLEVENINGSTAR CDLHANGINGMAN TRANGE ATR NATR CDLHIKKAKE CDLHIGHWAVE CDLMARUBOZU CDLHAMMER CDLADVANCEBLOCK CHOP RVOL BETA CDLXSIDEGAP3METHODS'.split()
IDS_60 = 'CDLDOJISTAR CDLXSIDEGAP3METHODS CDLGAPSIDESIDEWHITE CDLLONGLEGGEDDOJI CDLMARUBOZU CDLHARAMICROSS CDLDOJI ADXR CDLHANGINGMAN ATR NATR EOM BETA DPO ADOSC CDLGRAVESTONEDOJI CDLDRAGONFLYDOJI EFI CDLADVANCEBLOCK CDLSTALLEDPATTERN CDLTAKURI CORREL CDLHIGHWAVE CDL3OUTSIDE TRANGE'.split()
API = 'https://data-api.binance.vision/api/v3'
STEP = 300000
lock = threading.Lock()
states = {tf: {'schema': 1, 'timeframe_minutes': tf, 'status': 'warming', 'message': 'Loading verified price history and frozen models.', 'models': []} for tf in (5, 15, 60)}
compute_lock = threading.Lock()

def get_json(path, params=None):
    url = API + path + ('?' + urllib.parse.urlencode(params) if params else '')
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.load(response)

def closed_rows(rows, server_ms, step=STEP):
    return [r for r in rows if int(r[0]) + step <= server_ms and int(r[6]) < server_ms]

def direction(p):
    return None if p is None or not math.isfinite(p) else ('UP' if p >= .5 else 'DOWN')

def infer(d, frozen, ids=IDS):
    import numpy as np
    from indicator_lab.features import catalog, features, parameters
    from indicator_lab.model import predict, BURN
    catalog_by_id = {r['id']: r for r in catalog()}
    result = []
    for ident in ids:
        out = {'id': ident, 'direction': None, 'p_up': None, 'p_down': None}
        try:
            entry = frozen['models'][ident]
            profile = entry['selected_profile']; fitted = entry['profiles'][profile]
            if parameters(catalog_by_id[ident], profile) != fitted['parameters']:
                raise ValueError('Indicator settings do not match the frozen artifact')
            out.update(profile=profile, validation=fitted['validation'])
            if len(d) <= BURN:
                raise ValueError('Insufficient warmup history')
            x = features(catalog_by_id[ident], d, profile)[-1:]
            if not np.isfinite(x).all():
                raise ValueError('Required indicator inputs unavailable')
            p = float(predict(fitted['model'], x)[0])
            if not math.isfinite(p):
                raise ValueError('Model probability unavailable')
            out.update(direction=direction(p), p_up=p, p_down=1-p)
        except (ValueError, KeyError) as exc:
            out['reason'] = str(exc)
        result.append(out)
    return result

def run_loop(timeframe=5):
    step = timeframe * 60000
    ids = {5: IDS, 15: IDS_15, 60: IDS_60}[timeframe]
    import pandas as pd
    from indicator_lab.data import load, validate, COLS
    frozen = json.loads((ROOT/f'reports/predictions/frozen_{timeframe}m.json').read_text())
    for path in ['indicator_lab/features.py', 'indicator_lab/model.py']:
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != frozen['code_hashes'][path]:
            raise ValueError('Research implementation hash mismatch: '+path)
    d, manifest = load(timeframe)
    if hashlib.sha256((ROOT/'data/predictions/manifest.json').read_bytes()).hexdigest() != frozen['data_manifest_sha256']:
        raise ValueError('Research data manifest differs from frozen model source')
    last_computed = None
    while True:
        try:
            server_ms = int(get_json('/time')['serverTime'])
            latest_open = (server_ms//step-1)*step
            cursor = int(d.index[-1].timestamp()*1000)+step
            batches = []
            while cursor <= latest_open:
                rows = closed_rows(get_json('/klines', {'symbol':'BTCUSDT','interval':('1h' if timeframe == 60 else f'{timeframe}m'),'startTime':cursor,'endTime':latest_open+step-1,'limit':1000}), server_ms, step)
                if not rows:
                    raise ValueError('Binance has not supplied the required closed candles')
                times = [int(r[0]) for r in rows]
                # Fail closed on gaps in newly received history. Never fabricate missing candles.
                if times != list(range(cursor, times[-1]+step, step)):
                    raise ValueError('Gap in live Binance candle history')
                batch = pd.DataFrame([[float(v) for v in r[1:6]] for r in rows], columns=COLS,
                    index=pd.DatetimeIndex(pd.to_datetime(times, unit='ms', utc=True), name='timestamp'))
                validate(batch, timeframe); batches.append(batch); cursor=times[-1]+step
            if batches:
                d=pd.concat([d,*batches]); validate(d,timeframe)
            if int(d.index[-1].timestamp()*1000) != latest_open:
                raise ValueError('Latest complete Binance candle unavailable')
            if last_computed != latest_open:
                with compute_lock: models=infer(d,frozen,ids)
                new={'schema':1,'status':'live','source':'Binance spot BTC/USDT','timeframe_minutes':timeframe,
                    'target':'Next candle close versus latest completed candle close',
                    'candle_open_ms':latest_open,'as_of_ms':latest_open+step,'expires_at_ms':latest_open+2*step,
                    'generated_at_ms':int(time.time()*1000),'price':float(d.close.iloc[-1]),
                    'history_rows':len(d),'history_start':d.index[0].isoformat(),
                    'artifact_sha256':hashlib.sha256((ROOT/f'reports/predictions/frozen_{timeframe}m.json').read_bytes()).hexdigest(),
                    'message':f'Automatic Python forecasts. Updated after each completed {timeframe}-minute candle.', 'models':models}
                with lock: states[timeframe]=new
                last_computed=latest_open
                print('Published closed-candle signals:', d.index[-1].isoformat(), flush=True)
            else:
                with lock:
                    states[timeframe]={**states[timeframe],'status':'live','message':f'Automatic Python forecasts. Updated after each completed {timeframe}-minute candle.'}
        except Exception as exc:
            with lock: states[timeframe]={**states[timeframe],'status':'unavailable','message':str(exc)}
            print('Signal refresh failed:',str(exc),flush=True)
        time.sleep(15)

def start_loop(timeframe=5):
    try: run_loop(timeframe)
    except Exception as exc:
        with lock: states[timeframe]={**states[timeframe],'status':'unavailable','message':str(exc)}
        print('Signal startup failed:',str(exc),flush=True)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url=urllib.parse.urlsplit(self.path)
        path=url.path
        value=urllib.parse.parse_qs(url.query).get('timeframe',['5'])[0]
        if value not in ('5','15','60'):
            self.send_error(400, 'Supported timeframes: 5, 15, 60'); return
        timeframe=int(value)
        if path not in ('/', '/health', '/signals'):
            self.send_error(404); return
        with lock: body=dict(states[timeframe])
        if body.get('expires_at_ms',0) <= time.time()*1000 and body.get('status')=='live':
            body={**body,'status':'stale','message':'Waiting for the next completed candle forecast.'}
        if path=='/health': body={'ok':True,'signal_status':body['status']}
        data=json.dumps(body,allow_nan=False).encode()
        self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)

if __name__=='__main__':
    for timeframe in (5,15,60):
        threading.Thread(target=start_loop,args=(timeframe,),daemon=True).start()
    ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','10000'))),Handler).serve_forever()
