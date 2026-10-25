"""Generic-timeframe signal projections; original source bodies stay unchanged."""
import json,subprocess
import numpy as np
import pandas as pd
from multiasset.registry import ROOT
from multiasset.engine import WARMUP
from full_universe import freqtrade_adapter as freq
from full_universe.jesse_adapter import generate as jesse_generate,defaults as jesse_defaults

class PeriodNeighbor:
    def __init__(self,factor):self.factor=factor
    def __getattr__(self,name):
        import talib.abstract as abstract
        fn=getattr(abstract,name)
        def call(*args,**kwargs):
            args=list(args)
            if len(args)>1 and isinstance(args[1],int):args[1]=max(2,round(args[1]*self.factor))
            for key in list(kwargs):
                if key.endswith('period') and isinstance(kwargs[key],int):kwargs[key]=max(2,round(kwargs[key]*self.factor))
            return fn(*args,**kwargs)
        return call

def freq_frame(item,d,factor,minutes,symbol):
    strategy,params,original=freq.load(item,factor);strategy.timeframe=f'{minutes}m'
    strategy.config.update(stake_currency='USD',trading_mode='futures')
    if factor!=1 and not params:
        import talib.abstract as abstract
        for method in ['populate_indicators','populate_entry_trend','populate_exit_trend','supertrend','resample']:
            fn=getattr(strategy,method,None)
            if fn is not None and hasattr(fn,'__globals__') and fn.__globals__.get('ta') is abstract:fn.__globals__['ta']=PeriodNeighbor(factor)
    data=d.reset_index().rename(columns={d.index.name or 'index':'date'})
    data=strategy.populate_indicators(data,{'pair':symbol})
    if not isinstance(data,pd.DataFrame) or len(data)!=len(d):raise ValueError('Original indicators changed observation count')
    return strategy,data,params,original

def original_signals(item,d,factor,minutes,symbol):
    if item['framework']=='freqtrade':
        strategy,frame,params,original=freq_frame(item,d,factor,minutes,symbol)
        for method,old,column,oldcolumn in [('populate_entry_trend','populate_buy_trend','enter_long','buy'),('populate_exit_trend','populate_sell_trend','exit_long','sell')]:
            fn=getattr(strategy,method,None) or getattr(strategy,old,None)
            if fn is None:raise NotImplementedError('Original source lacks '+method)
            frame=fn(frame,{'pair':symbol})
            if not isinstance(frame,pd.DataFrame) or len(frame)!=len(d):raise ValueError('Original signals changed observation count')
            if column not in frame:frame[column]=frame[oldcolumn] if oldcolumn in frame else 0
        out=[frame[c].fillna(0).eq(1).to_numpy() for c in ['enter_long','exit_long']]
    elif item['framework']=='jesse':out=[np.asarray(v,bool) for v in jesse_generate(item,d,factor)]
    else:
        records=[[int(t.timestamp()*1000),*v] for t,v in zip(d.index,d[['open','high','low','close','volume']].to_numpy().tolist())]
        value=dict(source_path=item['source_path'],candles=records,factor=factor,warmup=WARMUP,minutes=minutes)
        p=subprocess.run(['node',str(ROOT/'multiasset/zenbot.cjs')],input=json.dumps(value),capture_output=True,text=True,timeout=45)
        if p.returncode:raise RuntimeError(p.stderr[-1800:])
        result=json.loads(p.stdout);out=[np.array(result[k],bool) for k in ['entry','exit']]
    for v in out:v[:WARMUP-1]=False
    return tuple(out)

def feature_frame(item,d,profile):
    from indicator_lab.features import features,catalog
    # Unknown OHLCV stays NaN. Only explicitly close-compatible functions can
    # use quote-only data; no financial replay ever receives this temporary frame.
    row=item;close_only=set(d.columns)=={'close'} or not {'open','high','low','volume'}<=set(d.columns)
    if close_only:
        from talib import abstract
        from indicator_lab.features import CUSTOM
        if row['id'] not in CUSTOM:
            names=abstract.Function(row['id']).input_names
            fields=set(v for value in names.values() for v in (value if isinstance(value,list) else [value]))
            if fields-{'close'}:raise ValueError('Formula requires unavailable OHLCV fields: '+str(sorted(fields-{'close'})))
        elif row['id'] not in {'HMA','RMA','DPO','FWMA','SWMA','SHMMA','QMA','COPPOCK','TSI'}:raise ValueError('Formula requires actual OHLCV; quote-only data has none')
        context=d.copy()
        for key in ['open','high','low','volume']:context[key]=np.nan
    else:context=d
    return features(row,context,profile)
