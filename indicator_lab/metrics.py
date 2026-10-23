"""Accuracy evidence and separate, costed long/cash portfolio diagnostics."""
import numpy as np
import pandas as pd
from scipy.special import ndtr

def accuracy(y,p):
    y=np.asarray(y,int);p=np.asarray(p,float);up=p>=.5
    if not len(y):raise ValueError('No forecast observations')
    tp=int(np.sum(up&(y==1)));tn=int(np.sum(~up&(y==0)));fp=int(np.sum(up&(y==0)));fn=int(np.sum(~up&(y==1)))
    n=len(y);acc=(tp+tn)/n;z=1.95996398454;den=1+z*z/n;centre=(acc+z*z/(2*n))/den;half=z*np.sqrt(acc*(1-acc)/n+z*z/(4*n*n))/den
    recall=tp/(tp+fn) if tp+fn else None;spec=tn/(tn+fp) if tn+fp else None
    mccden=np.sqrt(float((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)))
    q=np.clip(p,1e-12,1-1e-12)
    return dict(forecasts=n,accuracy=acc,balanced_accuracy=(recall+spec)/2 if recall is not None and spec is not None else None,up_precision=tp/(tp+fp) if tp+fp else None,up_recall=recall,mcc=(tp*tn-fp*fn)/mccden if mccden else None,brier=float(np.mean((p-y)**2)),log_loss=float(-np.mean(y*np.log(q)+(1-y)*np.log1p(-q))),actual_up_rate=float(y.mean()),predicted_up_rate=float(up.mean()),tp=tp,tn=tn,fp=fp,fn=fn,wilson_low=centre-half,wilson_high=centre+half)

def paired_evidence(y,p,baseline,times,replicates=2000):
    # Compare on identical target rows. Daily counts, 7-day moving-block bootstrap.
    diff=((p>=.5)==y).astype(float)-((baseline>=.5)==y).astype(float)
    s=pd.DataFrame({'diff':diff,'n':1},index=times-pd.Timedelta(nanoseconds=1)).resample('D').sum();s=s[s.n>0]
    observed=float(diff.mean());influence=(s['diff']-observed*s.n).to_numpy();days=len(s)
    # Newey-West standard error of the ratio, allowing seven daily autocorrelation lags.
    variance=float(np.dot(influence,influence))
    for lag in range(1,min(8,days)):variance+=2*(1-lag/8)*float(np.dot(influence[lag:],influence[:-lag]))
    se=np.sqrt(max(0,variance))/len(y)
    pvalue=float(2*ndtr(-abs(observed)/se)) if se>0 else (1. if observed==0 else 0.)
    # Non-circular blocks. Counts weight varying daily observation totals correctly.
    k=min(7,days);sums=np.convolve(s['diff'],np.ones(k),mode='valid');counts=np.convolve(s.n,np.ones(k),mode='valid')
    rng=np.random.default_rng(20261023);draw=rng.integers(0,len(sums),size=(replicates,int(np.ceil(days/k))))
    estimates=sums[draw].sum(axis=1)/counts[draw].sum(axis=1)
    lo,hi=np.quantile(estimates,[.025,.975])
    return dict(accuracy_lift_vs_train_majority=observed,lift_block_ci_low=float(lo),lift_block_ci_high=float(hi),daily_hac_se=float(se),pvalue=pvalue,independent_day_blocks=days,bootstrap_replicates=replicates)

def holm(pvalues):
    p=np.asarray(pvalues,float);order=np.argsort(p);n=len(p);out=np.empty(n);last=0.
    for j,i in enumerate(order):last=max(last,min(1.,(n-j)*p[i]));out[i]=last
    return out

def portfolio(d,minutes,predictions,start,stop,fee=.001,slippage=.0005):
    """A t-close forecast fills at the next adjacent candle open, long/cash.

    PnL includes open-to-close price changes. The forecast label is close-to-close;
    candle-boundary price gaps can therefore make direction and trade PnL differ.
    Every continuous run of UP forecasts is one trade, not one trade per bar.
    """
    ix=d.index;step=pd.Timedelta(minutes=minutes);start=pd.Timestamp(start,tz='UTC');stop=pd.Timestamp(stop,tz='UTC')
    choose=(ix>=start)&(ix+step<=stop);positions=np.flatnonzero(choose)
    if not len(positions):raise ValueError('Empty portfolio period')
    opens=d.open.to_numpy(float)[positions];closes=d.close.to_numpy(float)[positions]
    previous=positions-1;adjacent=(previous>=0)
    adjacent[adjacent] &= (ix.asi8[positions[adjacent]]-ix.asi8[previous[adjacent]])==step.value
    signals=np.full(len(positions),np.nan)
    signals[adjacent]=predictions[previous[adjacent]]
    known=np.isfinite(signals)
    last=np.maximum.accumulate(np.where(known,np.arange(len(signals)),-1))
    state=np.zeros(len(signals),bool);has=last>=0;state[has]=signals[last[has]]>=.5
    before=np.r_[False,state[:-1]]
    enters=state&~before;exits=~state&before;holds=state&before
    factor=np.ones(len(state));previous_close=np.r_[opens[0],closes[:-1]]
    factor[holds]=closes[holds]/previous_close[holds]
    factor[enters]=closes[enters]/(opens[enters]*(1+slippage)*(1+fee))
    factor[exits]=opens[exits]*(1-slippage)*(1-fee)/previous_close[exits]
    if state[-1]:factor[-1]*=(1-slippage)*(1-fee)
    e=10000.*np.cumprod(factor)
    entry_capital=np.r_[10000.,e[:-1]][enters]
    exits_at=np.flatnonzero(exits).tolist()
    if state[-1]:exits_at.append(len(state)-1)
    profits=e[exits_at]-entry_capital
    daily=pd.Series(e,index=ix[positions]+step-pd.Timedelta(nanoseconds=1)).resample('D').last().dropna()
    daily_returns=daily/np.r_[10000.,daily.to_numpy()[:-1]]-1
    std=float(daily_returns.std(ddof=1));sharpe=float(daily_returns.mean()/std*np.sqrt(365)) if std>0 else None
    peak=np.maximum.accumulate(np.r_[10000.,e]);draw=np.r_[10000.,e]/peak-1
    gains=float(profits[profits>0].sum());loss=-float(profits[profits<0].sum())
    bh=closes[-1]/opens[0]*(1-slippage)*(1-fee)/((1+slippage)*(1+fee))-1
    return dict(net_return=float(e[-1]/10000.-1),sharpe=sharpe,max_drawdown=float(-draw.min()),profit_factor=float(gains/loss) if loss>0 else None,profit_factor_note='undefined: no losing trades' if loss==0 else '',win_rate=float(np.mean(profits>0)) if len(profits) else None,trades=len(profits),too_few_trades=len(profits)<30,buy_hold_return=float(bh),excess_vs_buy_hold=float(e[-1]/10000.-1-bh),fee=fee,slippage=slippage),daily
