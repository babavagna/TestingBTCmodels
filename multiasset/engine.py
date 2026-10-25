"""Contract-aware, completed-signal long/cash replay using ACTUAL traded OHLCV."""
import numpy as np
import pandas as pd
CAPITAL=10000.;FEE=.001;SLIPPAGE=.0005;WARMUP=512

def desired_from_signals(entry,exit):
    en=np.asarray(entry,bool);ex=np.asarray(exit,bool)
    action=np.full(len(en),np.nan);action[en]=1.;action[ex]=0.
    last=np.maximum.accumulate(np.where(np.isfinite(action),np.arange(len(action)),-1))
    out=np.zeros(len(en));valid=last>=0;out[valid]=action[last[valid]];return out

def portfolio(d,desired,minutes,spec,start,stop,fee=FEE,slippage=SLIPPAGE):
    if not {'open','high','low','close','volume'}<=set(d):raise ValueError('Financial replay requires actual traded OHLCV, not quote-only closes')
    if not np.isfinite(d[['open','high','low','close','volume']].to_numpy()).all():raise ValueError('Missing OHLCV cannot be invented for financial replay')
    desired=np.asarray(desired,float)
    if len(desired)!=len(d):raise ValueError('Signal/data length mismatch')
    if not 0<=fee<1 or not 0<=slippage<1:raise ValueError('Invalid friction')
    start=pd.Timestamp(start);stop=pd.Timestamp(stop)
    start=start.tz_localize('UTC') if start.tzinfo is None else start.tz_convert('UTC')
    stop=stop.tz_localize('UTC') if stop.tzinfo is None else stop.tz_convert('UTC')
    ix=d.index;step=pd.Timedelta(minutes=minutes)
    chosen=(ix>=start)&(ix+step<=stop)&(np.arange(len(d))>=WARMUP)
    positions=np.flatnonzero(chosen)
    if len(positions)<2:raise ValueError('Fewer than two eligible portfolio bars')
    tradable=d.volume.to_numpy()[positions]>0
    if not tradable.any():raise ValueError('No actual trade-volume observations for executable fills')
    # A final close is taken only on an actually traded bar, common to all methods.
    positions=positions[:np.flatnonzero(tradable)[-1]+1]
    opening=d.open.to_numpy(float);closing=d.close.to_numpy(float);volume=d.volume.to_numpy(float)
    if spec.get('is_primary_kalshi'):
        if any(spec.get(k) is None for k in ['contract_size','underlying_multiplier','tick_size']) or not isinstance(spec.get('fractional_trading_enabled'),bool):raise ValueError('Kalshi contract specifications are unverified')
        if any(float(spec[k])<=0 for k in ['contract_size','underlying_multiplier','tick_size']):raise ValueError('Invalid Kalshi contract specifications')
    whole=spec.get('is_primary_kalshi',False) and spec.get('fractional_trading_enabled') is not True
    cash=CAPITAL;qty=0.;entry_cost=0.;profits=[];equity=np.empty(len(positions));skipped=0
    for i,j in enumerate(positions):
        adjacent=j>0 and ix.asi8[j]-ix.asi8[j-1]==step.value
        signal=desired[j-1] if adjacent else np.nan
        if j>0 and volume[j]>0 and np.isfinite(signal):
            if signal<.5 and qty:
                proceeds=qty*opening[j]*(1-slippage)*(1-fee);cash+=proceeds;profits.append(proceeds-entry_cost);qty=0.
            elif signal>=.5 and qty==0:
                unit_cost=opening[j]*(1+slippage)*(1+fee)
                bought=np.floor(cash/unit_cost) if whole else cash/unit_cost
                if bought>0:
                    qty=float(bought);entry_cost=qty*unit_cost;cash-=entry_cost
                else:skipped+=1
        equity[i]=cash+qty*closing[j]
    if qty:
        proceeds=qty*closing[positions[-1]]*(1-slippage)*(1-fee);cash+=proceeds;profits.append(proceeds-entry_cost);equity[-1]=cash
    series=pd.Series(equity,index=ix[positions]+step-pd.Timedelta(nanoseconds=1),name='equity')
    daily=series.resample('D').last().dropna();r=daily.to_numpy()/np.r_[CAPITAL,daily.to_numpy()[:-1]]-1
    years=spec.get('trading_days_per_year',365);std=r.std(ddof=1) if len(r)>1 else 0.
    downside=np.sqrt(np.mean(np.minimum(r,0.)**2));p=np.asarray(profits,float);gain=p[p>0].sum();loss=-p[p<0].sum()
    peak=np.maximum.accumulate(np.r_[CAPITAL,equity]);draw=1-np.r_[CAPITAL,equity]/peak
    first=positions[np.flatnonzero(volume[positions]>0)[0]];unit=opening[first]*(1+slippage)*(1+fee)
    bhqty=np.floor(CAPITAL/unit) if whole else CAPITAL/unit
    hold=(CAPITAL-bhqty*unit+bhqty*closing[positions[-1]]*(1-slippage)*(1-fee))/CAPITAL-1
    derivative='future' in spec.get('market_type','')
    missing=[]
    if derivative:missing=['Historical funding/financing not verified','Rollover/expiry costs not verified' if spec.get('market_type')=='dated future' else 'Historical margin/liquidation rules not reproduced','Historical contract-version changes not verified']
    stats=dict(net_return=float(equity[-1]/CAPITAL-1),sharpe=float(r.mean()/std*np.sqrt(years)) if std>0 else None,sortino=float(r.mean()/downside*np.sqrt(years)) if downside>0 else None,max_drawdown=float(draw.max()),profit_factor=float(gain/loss) if loss>0 else None,win_rate=float(np.mean(p>0)) if len(p) else None,trades=len(p),too_few_trades=len(p)<30,buy_hold_return=float(hold),excess_vs_buy_hold=float(equity[-1]/CAPITAL-1-hold),fee=fee,slippage=slippage,whole_contracts=whole,unaffordable_entry_attempts=skipped,funding_included=False if derivative else None,missing_costs=missing,fully_cost_validated=not missing,rank_eligible=not missing,capital=CAPITAL,first_bar=ix[positions[0]].isoformat(),last_bar_close=(ix[positions[-1]]+step).isoformat(),observations=len(positions),assumptions='Signal-only long/cash, next adjacent tradable open; actual contracts when Kalshi. Excludes unverified derivative funding/rollover; not native leveraged execution.')
    monthly=[];previous=CAPITAL
    for month,endvalue in daily.groupby(daily.index.strftime('%Y-%m')).last().items():
        monthly.append(dict(month=month,return_value=float(endvalue/previous-1)));previous=float(endvalue)
    annual=[];previous=CAPITAL
    for year,endvalue in daily.groupby(daily.index.year).last().items():
        annual.append(dict(year=int(year),return_value=float(endvalue/previous-1)));previous=float(endvalue)
    return stats,dict(date=[x.isoformat() for x in daily.index],equity=daily.tolist()),monthly,annual
