"""Read-only, closed-candle BTC signal API. Run: python live_signal_server.py.
Reuses frozen research models and replays all verified history; never places orders.
"""
import hashlib, json, math, os, threading, time, urllib.request, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IDS = 'CDLSTICKSANDWICH CDLTRISTAR CDL3BLACKCROWS CDL3LINESTRIKE CDLGAPSIDESIDEWHITE CDLMORNINGDOJISTAR CDLMORNINGSTAR CDLRISEFALL3METHODS ADOSC CDLADVANCEBLOCK EFI CDLHANGINGMAN EOM CDLXSIDEGAP3METHODS CDLSEPARATINGLINES CDLMARUBOZU DPO CDLDOJISTAR CDLSTALLEDPATTERN CDL3OUTSIDE CDLHIGHWAVE CDLRICKSHAWMAN CDLGRAVESTONEDOJI CDLLONGLEGGEDDOJI ATR NATR CDLDOJI CDLTAKURI CDLHIKKAKE STDDEV CDLHARAMICROSS TRANGE RVOL CDLDRAGONFLYDOJI CORREL'.split()
API = 'https://data-api.binance.vision/api/v3'
STEP = 300000
lock = threading.Lock()
state = {'schema': 1, 'status': 'warming', 'message': 'Loading verified price history and frozen models.', 'models': []}

def get_json(path, params=None):
    url = API + path + ('?' + urllib.parse.urlencode(params) if params else '')
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.load(response)

def closed_rows(rows, server_ms):
    return [r for r in rows if int(r[0]) + STEP <= server_ms and int(r[6]) < server_ms]

def direction(p):
    return None if p is None or not math.isfinite(p) else ('UP' if p >= .5 else 'DOWN')

def infer(d, frozen):
    import numpy as np
    from indicator_lab.features import catalog, features, parameters
    from indicator_lab.model import predict, BURN
    catalog_by_id = {r['id']: r for r in catalog()}
    result = []
    for ident in IDS:
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

def run_loop():
    global state
    import pandas as pd
    from indicator_lab.data import load, validate, COLS
    frozen = json.loads((ROOT/'reports/predictions/frozen_5m.json').read_text())
    for path in ['indicator_lab/features.py', 'indicator_lab/model.py']:
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != frozen['code_hashes'][path]:
            raise ValueError('Research implementation hash mismatch: '+path)
    d, manifest = load(5)
    if hashlib.sha256((ROOT/'data/predictions/manifest.json').read_bytes()).hexdigest() != frozen['data_manifest_sha256']:
        raise ValueError('Research data manifest differs from frozen model source')
    last_computed = None
    while True:
        try:
            server_ms = int(get_json('/time')['serverTime'])
            latest_open = (server_ms//STEP-1)*STEP
            cursor = int(d.index[-1].timestamp()*1000)+STEP
            batches = []
            while cursor <= latest_open:
                rows = closed_rows(get_json('/klines', {'symbol':'BTCUSDT','interval':'5m','startTime':cursor,'endTime':latest_open+STEP-1,'limit':1000}), server_ms)
                if not rows:
                    raise ValueError('Binance has not supplied the required closed candles')
                times = [int(r[0]) for r in rows]
                # Fail closed on gaps in newly received history. Never fabricate missing candles.
                if times != list(range(cursor, times[-1]+STEP, STEP)):
                    raise ValueError('Gap in live Binance candle history')
                batch = pd.DataFrame([[float(v) for v in r[1:6]] for r in rows], columns=COLS,
                    index=pd.DatetimeIndex(pd.to_datetime(times, unit='ms', utc=True), name='timestamp'))
                validate(batch, 5); batches.append(batch); cursor=times[-1]+STEP
            if batches:
                d=pd.concat([d,*batches]); validate(d,5)
            if int(d.index[-1].timestamp()*1000) != latest_open:
                raise ValueError('Latest complete Binance candle unavailable')
            if last_computed != latest_open:
                models=infer(d,frozen)
                new={'schema':1,'status':'live','source':'Binance spot BTC/USDT','timeframe_minutes':5,
                    'target':'Next candle close versus latest completed candle close',
                    'candle_open_ms':latest_open,'as_of_ms':latest_open+STEP,'expires_at_ms':latest_open+2*STEP,
                    'generated_at_ms':int(time.time()*1000),'price':float(d.close.iloc[-1]),
                    'history_rows':len(d),'history_start':d.index[0].isoformat(),
                    'artifact_sha256':hashlib.sha256((ROOT/'reports/predictions/frozen_5m.json').read_bytes()).hexdigest(),
                    'message':'Automatic Python forecasts. Updated after each completed 5-minute candle.', 'models':models}
                with lock: state=new
                last_computed=latest_open
                print('Published closed-candle signals:', d.index[-1].isoformat(), flush=True)
            else:
                with lock:
                    state={**state,'status':'live','message':'Automatic Python forecasts. Updated after each completed 5-minute candle.'}
        except Exception as exc:
            with lock: state={**state,'status':'unavailable','message':str(exc)}
            print('Signal refresh failed:',str(exc),flush=True)
        time.sleep(15)

def start_loop():
    global state
    try: run_loop()
    except Exception as exc:
        with lock: state={**state,'status':'unavailable','message':str(exc)}
        print('Signal startup failed:',str(exc),flush=True)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=urllib.parse.urlsplit(self.path).path
        if path not in ('/', '/health', '/signals'):
            self.send_error(404); return
        with lock: body=dict(state)
        if body.get('expires_at_ms',0) <= time.time()*1000 and body.get('status')=='live':
            body={**body,'status':'stale','message':'Waiting for the next completed candle forecast.'}
        if path=='/health': body={'ok':True,'signal_status':body['status']}
        data=json.dumps(body,allow_nan=False).encode()
        self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)

if __name__=='__main__':
    threading.Thread(target=start_loop,daemon=True).start()
    ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','10000'))),Handler).serve_forever()
