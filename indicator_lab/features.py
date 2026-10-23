# SPDX-License-Identifier: GPL-3.0-or-later
# Weighted MA adaptations: John McCormick / Alex Orekhov (everget), see preserved Pine headers.
"""Causal indicator formulas. Indicators are inputs to a forecast model, not forecasts.

TA-Lib parameters are explicit. Project formulas are disclosed Python implementations;
matching the proprietary TradingView calculation engine is NOT verified.
"""
import json,inspect
import numpy as np
import pandas as pd
import talib as ta
from talib import abstract
from indicator_lab.data import ROOT
GROUPS=['Cycle Indicators','Momentum Indicators','Overlap Studies','Statistic Functions','Volatility Indicators','Volume Indicators','Pattern Recognition']
# Avoid presenting algebraically equivalent ROC variants / duplicate MACD and SMA
# parameterizations as different discoveries. MAVP needs a separate period series.
EXCLUDED={'MA','MAVP','MACDEXT','MACDFIX','ROCP','ROCR','ROCR100'}
OVERRIDES={'BBANDS':{'timeperiod':20},'SMA':{'timeperiod':20},'EMA':{'timeperiod':20},'WMA':{'timeperiod':20}}
CUSTOM={
 'AO':('Awesome Oscillator','oscillator',{'fastperiod':5,'slowperiod':34}),
 'AC':('Accelerator Oscillator','oscillator',{'fastperiod':5,'slowperiod':34,'signalperiod':5}),
 'CMF':('Chaikin Money Flow','oscillator',{'timeperiod':20}),
 'EFI':('Elder Force Index','oscillator',{'timeperiod':13}),
 'EOM':('Ease of Movement','oscillator',{'timeperiod':14}),
 'VWMA':('Volume Weighted Moving Average','price',{'timeperiod':20}),
 'VWAP':('UTC daily VWAP','price',{}),
 'RVOL':('Relative Volume','oscillator',{'timeperiod':20}),
 'HMA':('Hull Moving Average','price',{'timeperiod':20}),
 'RMA':('Wilder Moving Average','price',{'timeperiod':14}),
 'DONCHIAN':('Donchian Channels','price',{'timeperiod':20}),
 'KELTNER':('Keltner Channels','price',{'timeperiod':20}),
 'ICHIMOKU':('Ichimoku (available-time lines, no backshift)','price',{'fastperiod':9,'timeperiod':26,'slowperiod':52}),
 'CHOP':('Choppiness Index','oscillator',{'timeperiod':14}),
 'TSI':('True Strength Index','oscillator',{'fastperiod':13,'slowperiod':25}),
 'COPPOCK':('Coppock Curve','oscillator',{'fastperiod':11,'slowperiod':14,'timeperiod':10}),
 'DPO':('Detrended Price Oscillator (causal)','oscillator',{'timeperiod':20}),
 'FISHER':('Fisher Transform','oscillator',{'timeperiod':10}),
 'VORTEX':('Vortex Indicator','oscillator',{'timeperiod':14}),
 'SUPERTREND':('Supertrend (ATR 10, multiplier 3)','price',{'timeperiod':10}),
 'BULLBEAR':('Bull/Bear Power','oscillator',{'timeperiod':13}),
 'WVF':('Williams Vix Fix','oscillator',{'timeperiod':22}),
 'FWMA':('Fibonacci Weighted Moving Average','price',{'timeperiod':14}),
 'SWMA':('Sine Weighted Moving Average','price',{'timeperiod':14}),
 'SHMMA':('Sharp Modified Moving Average','price',{'timeperiod':14}),
 'QMA':('Quick Moving Average','price',{'timeperiod':14}),
}
PINE_MATCH={'AO':'oscillators/awesome_oscillator.pine','AC':'oscillators/accelerator_oscillator.pine','TSI':'oscillators/tsi_true_strength_index.pine','COPPOCK':'oscillators/coppock_curve.pine','FWMA':'movings/fibonacci_weighted_moving_average.pine','SWMA':'movings/sine_weighted_moving_average.pine','SHMMA':'movings/sharp_modified_moving_average.pine','QMA':'movings/quick_moving_average.pine'}

def catalog():
    rows=[]
    for group in GROUPS:
        for name in ta.get_function_groups()[group]:
            if name in EXCLUDED:continue
            f=abstract.Function(name);pars=dict(f.parameters);pars.update(OVERRIDES.get(name,{}))
            rows.append(dict(id=name,name=f.info['display_name'],group=group,implementation='TA-Lib 0.6.8 Python / 0.6.4 C',parameters=pars,github_url=f'https://github.com/TA-Lib/ta-lib/blob/v0.6.4/src/ta_func/ta_{name}.c',formula_status='Open-source formula; native TradingView parity UNVERIFIED',pattern=group=='Pattern Recognition'))
    for name,(title,kind,pars) in CUSTOM.items():
        url='https://github.com/babavagna/TestingBTCmodels/blob/main/indicator_lab/features.py'
        if name in PINE_MATCH:url='https://github.com/everget/tradingview-pinescript-indicators/blob/8385cc421888bbf31f36407195796bc0eabafb19/'+PINE_MATCH[name]
        rows.append(dict(id=name,name=title,group='Project formula',implementation='Disclosed Python formula',parameters=pars,github_url=url,formula_status='Formula adaptation; native TradingView parity UNVERIFIED',pattern=False))
    return rows

def parameters(row,profile='default'):
    p=row['parameters'].copy();factor={'short':.8,'default':1.,'long':1.2}[profile]
    for k,v in p.items():
        if 'period' in k and isinstance(v,int):p[k]=max(2,round(v*factor))
    return p

def _s(x,d):return pd.Series(np.asarray(x,dtype=float),index=d.index)
def _rma(s,n):
    a=s.to_numpy(float);out=np.full(len(a),np.nan);start=np.flatnonzero(np.isfinite(a))
    if len(start)==0:return _s(out,s.to_frame())
    i=start[0]+n-1
    if i<len(a):out[i]=np.mean(a[start[0]:i+1])
    for j in range(i+1,len(a)):out[j]=(out[j-1]*(n-1)+a[j])/n
    return pd.Series(out,index=s.index)
def _weighted(c,w):
    # Full windows; the shared 2048-bar burn-in removes different seed behavior.
    return c.rolling(len(w)).apply(lambda a:np.dot(a,w)/np.sum(w),raw=True)

def raw(row,d,profile='default'):
    name=row['id'];p=parameters(row,profile);n=p.get('timeperiod',14)
    o,h,l,c,v=[d[k] for k in ['open','high','low','close','volume']];hl=(h+l)/2
    if name not in CUSTOM:
        f=abstract.Function(name);out=f({k:d[k].to_numpy(float) for k in d.columns},**p)
        a=np.asarray(out,dtype=float)
        return a.T if a.ndim==2 else a[:,None]
    if name in ('AO','AC'):
        a=hl.rolling(p['fastperiod']).mean()-hl.rolling(p['slowperiod']).mean()
        out=a if name=='AO' else a-a.rolling(p['signalperiod']).mean()
    elif name=='CMF':out=((2*c-h-l)/(h-l).replace(0,np.nan)*v).rolling(n).sum()/v.rolling(n).sum()
    elif name=='EFI':out=(c.diff()*v).ewm(span=n,adjust=False,min_periods=n).mean()
    elif name=='EOM':out=(hl.diff()*(h-l)/v.replace(0,np.nan)).rolling(n).mean()
    elif name=='VWMA':out=(c*v).rolling(n).sum()/v.rolling(n).sum()
    elif name=='VWAP':out=(((h+l+c)/3*v).groupby(d.index.floor('D')).cumsum()/v.groupby(d.index.floor('D')).cumsum())
    elif name=='RVOL':out=v/v.rolling(n).mean()
    elif name=='HMA':out=_s(ta.WMA(2*ta.WMA(c,n//2)-ta.WMA(c,n),max(2,int(np.sqrt(n)))),d)
    elif name=='RMA':out=_rma(c,n)
    elif name=='DONCHIAN':out=pd.concat([h.rolling(n).max(),l.rolling(n).min()],axis=1)
    elif name=='KELTNER':
        mid=_s(ta.EMA(c,n),d);a=_s(ta.ATR(h,l,c,n),d);out=pd.concat([mid,mid+2*a,mid-2*a],axis=1)
    elif name=='ICHIMOKU':
        f=(h.rolling(p['fastperiod']).max()+l.rolling(p['fastperiod']).min())/2
        b=(h.rolling(n).max()+l.rolling(n).min())/2
        spanb=(h.rolling(p['slowperiod']).max()+l.rolling(p['slowperiod']).min())/2
        # Unshifted values are available now; chart display shifts have no future inputs.
        out=pd.concat([f,b,(f+b)/2,spanb],axis=1)
    elif name=='CHOP':out=100*np.log10(_s(ta.TRANGE(h,l,c),d).rolling(n).sum()/(h.rolling(n).max()-l.rolling(n).min()))/np.log10(n)
    elif name=='TSI':
        diff=c.diff();a=diff.ewm(span=p['slowperiod'],adjust=False).mean().ewm(span=p['fastperiod'],adjust=False).mean()
        b=diff.abs().ewm(span=p['slowperiod'],adjust=False).mean().ewm(span=p['fastperiod'],adjust=False).mean();out=100*a/b
    elif name=='COPPOCK':out=_s(ta.WMA(ta.ROC(c,p['fastperiod'])+ta.ROC(c,p['slowperiod']),n),d)
    elif name=='DPO':out=c.shift(n//2+1)-c.rolling(n).mean()
    elif name=='FISHER':
        z=(hl-hl.rolling(n).min())/(hl.rolling(n).max()-hl.rolling(n).min())
        vals=np.full(len(d),np.nan);f=np.full(len(d),np.nan);prev=0.;last=0.
        for i,x in enumerate(z.to_numpy()):
            if np.isfinite(x):
                prev=np.clip(.66*(x-.5)+.67*prev,-.999,.999);last=.5*np.log((1+prev)/(1-prev))+.5*last;vals[i]=prev;f[i]=last
        out=_s(f,d)
    elif name=='VORTEX':
        tr=_s(ta.TRANGE(h,l,c),d).rolling(n).sum();out=pd.concat([(h-l.shift()).abs().rolling(n).sum()/tr,(l-h.shift()).abs().rolling(n).sum()/tr],axis=1)
    elif name=='SUPERTREND':
        atr=np.asarray(ta.ATR(h,l,c,n));up=np.asarray(hl)+3*atr;lo=np.asarray(hl)-3*atr;close=c.to_numpy();line=np.full(len(d),np.nan);trend=True
        for i in range(n,len(d)):
            if i>n:
                if lo[i]<lo[i-1] and close[i-1]>lo[i-1]:lo[i]=lo[i-1]
                if up[i]>up[i-1] and close[i-1]<up[i-1]:up[i]=up[i-1]
                if close[i]>up[i-1]:trend=True
                elif close[i]<lo[i-1]:trend=False
            line[i]=lo[i] if trend else up[i]
        out=_s(line,d)
    elif name=='BULLBEAR':
        e=_s(ta.EMA(c,n),d);out=pd.concat([h-e,l-e],axis=1)
    elif name=='WVF':out=100*(c.rolling(n).max()-l)/c.rolling(n).max()
    elif name=='FWMA':
        w=[];a,b=0.,1.
        for i in range(n):w.append(b);a,b=b,a+b
        out=_s(np.convolve(c.to_numpy(),np.asarray(w[::-1])/sum(w),mode='full')[:len(c)],d);out.iloc[:n-1]=np.nan
    elif name=='SWMA':
        w=np.sin(np.arange(1,n+1)*np.pi/(n+1));out=_s(np.convolve(c.to_numpy(),w/sum(w),mode='full')[:len(c)],d);out.iloc[:n-1]=np.nan
    elif name=='SHMMA':out=_s(3*ta.WMA(c,n)-2*ta.SMA(c,n),d)
    elif name=='QMA':
        i=np.arange(1,n+1);peak=n/3
        w=np.where(i<=peak,i/peak,(n+1-i)/(n+1-peak))
        out=_s(np.convolve(c.to_numpy(),w/sum(w),mode='full')[:len(c)],d);out.iloc[:n-1]=np.nan
    else:raise ValueError(name)
    a=np.asarray(out,dtype=float);return a if a.ndim==2 else a[:,None]

PRICE_UNIT={'APO','MACD','MOM','MINUS_DM','PLUS_DM','ATR','TRANGE','STDDEV','LINEARREG_SLOPE','BULLBEAR','AO','AC','DPO'}
PRICE_LEVEL={'LINEARREG','LINEARREG_INTERCEPT','TSF'}

def features(row,d,profile='default'):
    a=raw(row,d,profile);c=d.close.to_numpy()[:,None]
    kind=CUSTOM.get(row['id'],('',None))[1];name=row['id']
    if row['group']=='Overlap Studies' or kind=='price' or name in PRICE_LEVEL:a=a/c-1
    elif name in PRICE_UNIT:a=a/c
    elif name=='VAR':a=a/(c*c)
    elif name in {'AD','OBV'}:
        a=pd.DataFrame(a).diff().to_numpy()/d.volume.rolling(20).mean().to_numpy()[:,None]
    elif name in {'ADOSC','EFI'}:a=a/(d.volume.rolling(20).mean().to_numpy()[:,None]*c)
    elif name=='EOM':a=a*d.volume.rolling(20).mean().to_numpy()[:,None]/(c*c)
    # Four causal views of each output, same readout for every indicator.
    b=pd.DataFrame(a);return np.column_stack([a,b.diff().to_numpy(),b.shift(1).to_numpy(),b.shift(3).to_numpy()])
