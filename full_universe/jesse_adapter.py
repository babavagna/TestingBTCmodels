"""Documented TA-Lib/pandas long-signal translations of Jesse source rules.

These are formula adaptations, not execution of the Jesse engine. Native risk
sizing, shorts, stop/target orders and account-dependent filters are omitted.
DUAL_THRUST and TurtleRules fail closed rather than inventing missing state.
"""
import pandas as pd
import talib.abstract as ta

def defaults(item,factor=1.):
    values={
      'Donchian':dict(channel=20,trend=200),
      'IFR2':dict(rsi=2,oversold=10,conversion=20,base=30,span=120,displacement=60),
      'MACD_EMA':dict(ema=100,fast=12,slow=26,signal=9),
      'MAGen':dict(fast=5,slow=20,adx_period=8,adx_entry=13,adx_exit=15),
      'RSI2':dict(fast=5,slow=200,rsi=2,oversold=10),
      'SMACrossover':dict(fast=50,slow=200),
      'SimpleBollinger':dict(window=20,std=2,conversion=9,base=26,span=52,displacement=26),
      'TradingView_RSI':dict(rsi=5,entry=35,exit=75,emergency=10)}
    if item['name'] not in values:
        raise NotImplementedError('UNSUPPORTED_NATIVE_STATE: '+item['name']+' needs anchored multi-timeframe bars or pyramiding/fill callbacks; no substitute strategy was invented')
    return {k:(max(2,int(round(v*factor))) if isinstance(v,int) else v*factor) for k,v in values[item['name']].items()}

def generate(item,d,factor=1.):
    p=defaults(item,factor);c=d.close
    name=item['name']
    def cloud():
        mid=lambda n:(d.high.rolling(n).max()+d.low.rolling(n).min())/2
        # Only previously computed spans shifted forward; never shift future
        # closing prices back into the predictor.
        return ((mid(p['conversion'])+mid(p['base']))/2).shift(p['displacement']),mid(p['span']).shift(p['displacement'])
    if name=='Donchian':
        return (c>d.high.rolling(p['channel']).max().shift())&(c>ta.SMA(d,timeperiod=p['trend'])),c<d.low.rolling(p['channel']).min().shift()
    if name=='MACD_EMA':
        m=ta.MACD(d,fastperiod=p['fast'],slowperiod=p['slow'],signalperiod=p['signal']);ema=ta.EMA(d,timeperiod=p['ema'])
        return (c>ema)&(m['macd']>m['macdsignal']),(c<ema)&(m['macd']<m['macdsignal'])
    if name=='RSI2':
        return (c>ta.SMA(d,timeperiod=p['slow']))&(ta.RSI(d,timeperiod=p['rsi'])<=p['oversold']),c>ta.SMA(d,timeperiod=p['fast'])
    if name=='SMACrossover':
        fast=ta.SMA(d,timeperiod=p['fast']);slow=ta.SMA(d,timeperiod=p['slow'])
        return fast>slow,fast<slow
    if name=='MAGen':
        # Published MA type 11 is linear regression, not TA-Lib MA type 11.
        fast=ta.LINEARREG(d,timeperiod=p['fast']);slow=ta.LINEARREG(d,timeperiod=p['slow']);adx=ta.ADX(d,timeperiod=p['adx_period'])
        return (fast>slow)&(fast.shift()<=slow.shift())&(adx>p['adx_entry']),(fast<slow)&(adx<p['adx_exit'])
    if name=='TradingView_RSI':
        r=ta.RSI(d,timeperiod=p['rsi'])
        return (r>p['entry'])&(r.shift()<=p['entry']),((r<p['exit'])&(r.shift()>=p['exit']))|((r<p['emergency'])&(r.shift()>=p['emergency']))
    if name=='IFR2':
        a,b=cloud()
        return (ta.RSI(d,timeperiod=p['rsi'])<p['oversold'])&(c>a)&(c>b)&ta.HT_TRENDMODE(d).eq(1),(c>d.high.shift(1))&(c>d.high.shift(2))
    if name=='SimpleBollinger':
        a,b=cloud();hl2=(d.high+d.low)/2
        upper,middle,lower=__import__('talib').BBANDS(hl2.to_numpy(),timeperiod=p['window'],nbdevup=p['std'],nbdevdn=p['std'],matype=0)
        return (c>upper)&(c>a)&(c>b),c<middle
    raise AssertionError('Missing adapter')
