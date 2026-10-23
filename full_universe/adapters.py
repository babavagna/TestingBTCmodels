"""Uniform completed-candle signals; failures never become performance rows."""
import json,subprocess
from pathlib import Path
import pandas as pd
from full_universe.freqtrade_adapter import generate as freq_signals,load as freq_load
ROOT=Path(__file__).resolve().parents[1]
WARMUP=4096

def generate(item,candles,factor=1.):
    if item['framework']=='freqtrade':return freq_signals(item,candles,factor)
    if item['framework']=='jesse':
        from full_universe.jesse_adapter import generate as jesse_signals
        return jesse_signals(item,candles,factor)
    rows=[[int(t.timestamp()*1000),*row] for t,row in zip(candles.index,candles[['open','high','low','close','volume']].to_numpy().tolist())]
    payload=json.dumps(dict(source_path=item['source_path'],candles=rows,factor=factor,warmup=WARMUP))
    try:
        p=subprocess.run(['node',str(ROOT/'full_universe/zenbot_runner.cjs')],input=payload,text=True,capture_output=True,timeout=120,start_new_session=True)
    except subprocess.TimeoutExpired as e:
        # No normal runtime should leave child processes behind (neural forks).
        raise RuntimeError('RUNTIME_TIMEOUT: native source did not finish within 120 seconds') from e
    if p.returncode:raise RuntimeError(p.stderr[-2500:])
    try:out=json.loads(p.stdout)
    except ValueError as e:raise RuntimeError('Native source did not emit valid signals: '+p.stdout[:200]) from e
    return tuple(pd.Series(out[key],index=candles.index,dtype=bool) for key in ('entry','exit'))

def parameters(item,factor=1.):
    if item['framework']=='freqtrade':
        _,params,tf=freq_load(item,factor);return params
    if item['framework']=='jesse':
        from full_universe.jesse_adapter import defaults
        return defaults(item,factor)
    return {'numeric_option_factor':factor}

def prepared(item,candles,factor=1.):
    # Periods count observed candles. Never fabricate OHLC rows. Retain available
    # history across gaps; the engine independently forbids fills across a gap.
    # All candidates share the same one-time initial warmup and scoring dates.
    if len(candles)<=WARMUP:
        empty=pd.Series(False,index=candles.index);return empty,empty.copy()
    en,ex=generate(item,candles,factor)
    en=en.fillna(False).astype(bool);ex=ex.fillna(False).astype(bool)
    en.iloc[:WARMUP-1]=False;ex.iloc[:WARMUP-1]=False
    return en,ex
