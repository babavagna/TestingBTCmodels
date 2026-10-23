"""Run unchanged published indicator and long-signal methods, without a trading daemon.

This is a SIGNAL projection: one-hour bars, all-in long/cash, no native ROI,
stoploss, shorts, leverage, pyramiding or custom position management. Compatibility
imports do not supply invented indicators. Missing APIs raise an error.
"""
import copy
import importlib.util
import math
import sys
import types
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

class Parameter:
    def __init__(self, *args, default=None, **kwargs):
        self.value = default
        self.default = default
    @property
    def range(self):
        return [self.value]

class IStrategy:
    def __init__(self):
        for name in dir(type(self)):
            val = getattr(type(self), name)
            if isinstance(val, Parameter):
                setattr(self, name, copy.deepcopy(val))
        for space in ('buy_params','sell_params'):
            for key,value in getattr(self,space,{}).items():
                if isinstance(getattr(self,key,None),Parameter):
                    getattr(self,key).value=value
        self.config = {'stake_currency':'USDT','trading_mode':'spot'}
    def populate_indicators(self, d, metadata): return d

def minutes(timeframe):
    return int(timeframe[:-1])*{'m':1,'h':60,'d':1440,'w':10080}[timeframe[-1]]

def install_imports():
    # Old source expects names removed in NumPy 2. The mathematical functions
    # themselves are unchanged. pandas_ta is unused by the two importing files;
    # an attempted function access fails instead of manufacturing an indicator.
    import numpy.lib
    numpy.lib.math=math
    np.NAN=np.nan
    np.NaN=np.nan
    spec=importlib.util.spec_from_file_location('qtpylib_original',ROOT/'sources/reference/qtpylib_indicators.py')
    q=importlib.util.module_from_spec(spec); spec.loader.exec_module(q)
    for name in ('freqtrade','freqtrade.strategy','freqtrade.strategy.interface','freqtrade.vendor','freqtrade.vendor.qtpylib','freqtrade.exchange','freqtrade.persistence','pandas_ta'):
        sys.modules[name]=types.ModuleType(name)
    sys.modules['freqtrade.vendor.qtpylib.indicators']=q
    strategy=sys.modules['freqtrade.strategy']
    strategy.IStrategy=IStrategy
    for name in ('IntParameter','DecimalParameter','BooleanParameter','CategoricalParameter','RealParameter'):
        setattr(strategy,name,Parameter)
    def unsupported(*args,**kwargs): raise NotImplementedError('Native informative-pair API is not supported by the signal projection')
    strategy.merge_informative_pair=unsupported
    strategy.timeframe_to_minutes=minutes
    sys.modules['freqtrade.strategy.interface'].IStrategy=IStrategy
    sys.modules['freqtrade.exchange'].timeframe_to_minutes=minutes
    sys.modules['freqtrade.persistence'].Trade=type('Trade',(),{})
    strategy.date_minus_candles=lambda tf,n,date:date-pd.Timedelta(minutes=minutes(tf)*n)
    sys.modules['freqtrade.exchange'].date_minus_candles=strategy.date_minus_candles

_INSTALLED=False

def load(item, factor=1.0):
    global _INSTALLED
    if not _INSTALLED:
        install_imports();_INSTALLED=True
    spec=importlib.util.spec_from_file_location('source_'+item['id'],ROOT/item['source_path'])
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    classes=[v for v in vars(mod).values() if isinstance(v,type) and issubclass(v,IStrategy) and v is not IStrategy]
    if len(classes)!=1: raise ValueError('Expected exactly one source strategy class')
    strategy=classes[0]()
    original_timeframe=getattr(strategy,'timeframe','unspecified')
    strategy.timeframe='60m'
    params={}
    # Fixed +/-20% neighbors only for actual exposed numeric Parameters. No
    # categorical changes or wholesale textual replacement of source constants.
    for name in dir(strategy):
        p=getattr(strategy,name)
        if isinstance(p,Parameter):
            if factor!=1 and isinstance(p.value,(int,float)) and not isinstance(p.value,bool):
                p.value=max(1,int(round(p.value*factor))) if isinstance(p.value,int) and p.value>0 else round(p.value*factor,6)
            params[name]=p.value
    return strategy,params,original_timeframe

def generate(item,candles,factor=1.0):
    strategy,params,timeframe=load(item,factor)
    if factor != 1 and not params:
        # For fixed-rule sources, vary explicitly supplied TA-Lib periods only.
        # Default path executes the original calls unchanged. No source rewrites.
        import talib.abstract as abstract
        class PeriodNeighbor:
            def __getattr__(self,name):
                fn=getattr(abstract,name)
                def call(*args,**kwargs):
                    args=list(args)
                    if len(args)>1 and isinstance(args[1],int):args[1]=max(2,round(args[1]*factor))
                    for key in list(kwargs):
                        if key.endswith('period') and isinstance(kwargs[key],int):kwargs[key]=max(2,round(kwargs[key]*factor))
                    return fn(*args,**kwargs)
                return call
        # The function's globals belong to its isolated source module.
        for method in ('populate_indicators','populate_entry_trend','populate_exit_trend','supertrend','resample'):
            fn=getattr(strategy,method,None)
            if fn is not None and hasattr(fn,'__globals__') and fn.__globals__.get('ta') is abstract:
                fn.__globals__['ta']=PeriodNeighbor()
    # Framework uses RangeIndex and a date column. Preserve that contract.
    frame=candles.reset_index().rename(columns={candles.index.name or 'index':'date'})
    frame=strategy.populate_indicators(frame,{'pair':'BTC/USDT'})
    if not isinstance(frame,pd.DataFrame) or len(frame)!=len(candles): raise ValueError('Indicator method changed candle count')
    for method,old,col,oldcol in [('populate_entry_trend','populate_buy_trend','enter_long','buy'),('populate_exit_trend','populate_sell_trend','exit_long','sell')]:
        fn=getattr(strategy,method,None) or getattr(strategy,old,None)
        if fn is None: raise NotImplementedError('Source has no '+method+' or '+old)
        frame=fn(frame,{'pair':'BTC/USDT'})
        if not isinstance(frame,pd.DataFrame) or len(frame)!=len(candles): raise ValueError(method+' changed candle count')
        if col not in frame and oldcol in frame:frame[col]=frame[oldcol]
        if col not in frame: frame[col]=0
    return tuple(pd.Series(frame[col].fillna(0).eq(1).to_numpy(),index=candles.index) for col in ('enter_long','exit_long'))
