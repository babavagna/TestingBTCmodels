"""Fixtures here are synthetic; historical accuracy comes only from executed reports."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from indicator_lab.data import aggregate,load,ROOT
from indicator_lab.features import catalog,features,raw
from indicator_lab.model import targets,period_mask,fit,predict
from indicator_lab.metrics import accuracy,holm,portfolio,paired_evidence
from indicator_lab.runner import causality,choose_profile

def frame(n=4000,minutes=60):
    rng=np.random.default_rng(41);c=100*np.exp(np.cumsum(rng.normal(0,.01,n)));o=np.r_[c[0],c[:-1]]
    return pd.DataFrame(dict(open=o,high=np.maximum(o,c)*1.01,low=np.minimum(o,c)*.99,close=c,volume=rng.uniform(100,200,n)),index=pd.date_range('2020-01-01',periods=n,freq=f'{minutes}min',tz='UTC',name='timestamp'))

def test_incomplete_aggregate_is_discarded():
    d=frame(12,5).drop(pd.Timestamp('2020-01-01 00:05Z'))
    result=aggregate(d,15)
    assert list(result.index.minute)==[15,30,45]
    assert result.iloc[0].open==d.loc['2020-01-01 00:15Z','open']
    assert result.iloc[0].close==d.loc['2020-01-01 00:25Z','close']

def test_label_timing_ties_and_gap():
    d=frame(2060,5);d.iloc[2051,d.columns.get_loc('close')]=d.iloc[2050].close
    d=d.drop(d.index[2054]);y,ok,decision,end=targets(d,5)
    assert not ok[:2048].any()
    assert not ok[2050] # next close is equal
    assert not ok[2053] # missing target candle
    assert not ok[-1]
    i=2049
    assert y[i]==int(d.close.iloc[i+1]>d.close.iloc[i])
    assert decision[i]==d.index[i]+pd.Timedelta(minutes=5)
    assert end[i]==d.index[i+1]+pd.Timedelta(minutes=5)

def test_training_boundary_purges_label_at_midnight():
    d=frame(10000);_,ok,_,end=targets(d,60)
    m=period_mask(d,60,ok,'2020-01-01','2021-01-01',fit=True)
    assert end[m].max()<pd.Timestamp('2021-01-01',tz='UTC')
    v=period_mask(d,60,ok,'2020-01-01','2021-01-01')
    assert end[v].max()==pd.Timestamp('2021-01-01',tz='UTC')
    assert v.sum()==m.sum()+1

def test_future_rows_do_not_change_fit():
    rng=np.random.default_rng(9);x=rng.normal(size=(4000,3));y=(x[:,0]+rng.normal(size=4000)>.2).astype(int);m=np.arange(4000)<3000
    first=fit(x,y,m);x[~m]=1e9;y[~m]=1-y[~m];second=fit(x,y,m)
    assert first==second
    assert predict(first,np.array([[1.,0,0]]))[0]>.5

def test_constant_indicator_is_a_failed_model():
    with pytest.raises(ValueError,match='constant'):fit(np.zeros((1200,4)),np.arange(1200)%2,np.ones(1200,bool))

def test_selection_uses_validation_and_default_tie():
    p={k:dict(validation={'accuracy':v},future_test_accuracy=1-v) for k,v in [('short',.6),('long',.6),('default',.6)]}
    assert choose_profile(p)=='default'
    p['long']['validation']['accuracy']=.61
    assert choose_profile(p)=='long'

def test_accuracy_confusion_and_brier_are_hand_calculated():
    r=accuracy(np.array([1,1,0,0]),np.array([.9,.4,.6,.1]))
    assert r['accuracy']==.5 and r['tp']==r['tn']==r['fp']==r['fn']==1
    assert r['balanced_accuracy']==.5 and r['mcc']==0
    assert r['brier']==pytest.approx(.185)
    assert .15<r['wilson_low']<.16 and .84<r['wilson_high']<.85

def test_holm_controls_the_whole_family():
    assert holm([.01,.04,.03]).tolist()==pytest.approx([.03,.06,.06])

def simple_prices():
    return pd.DataFrame(dict(open=[100.,100.,120.,120.],high=[101.,111.,121.,121.],low=[99.,99.,119.,119.],close=[100.,110.,120.,120.],volume=[1.]*4),index=pd.date_range('2025-01-01',periods=4,freq='5min',tz='UTC'))

def test_next_open_fill_and_both_sides_costs():
    d=simple_prices();r,_=portfolio(d,5,np.array([1.,0.,0.,0.]),'2025-01-01 00:05','2025-01-01 00:15')
    exact=1.2*(1-.0005)*(1-.001)/((1+.0005)*(1+.001))-1
    assert r['net_return']==pytest.approx(exact)
    assert r['buy_hold_return']==pytest.approx(exact)
    assert r['trades']==1 and r['win_rate']==1 and r['profit_factor'] is None
    costly,_=portfolio(d,5,np.array([1.,0.,0.,0.]),'2025-01-01 00:05','2025-01-01 00:15',fee=.002,slippage=.001)
    assert costly['net_return']<r['net_return']

def test_forced_exit_and_consecutive_ups_are_one_trade():
    d=simple_prices();r,_=portfolio(d,5,np.ones(4),'2025-01-01 00:05','2025-01-01 00:15')
    assert r['trades']==1
    assert r['net_return']==pytest.approx(r['buy_hold_return'])

def test_missing_bar_prevents_fill_and_nan_holds_position():
    d=simple_prices().drop(pd.Timestamp('2025-01-01 00:05Z'))
    r,_=portfolio(d,5,np.array([1.,0.,0.]),'2025-01-01 00:10','2025-01-01 00:15')
    assert r['trades']==0 and r['net_return']==0
    d=simple_prices();r,_=portfolio(d,5,np.array([1.,np.nan,0.,0.]),'2025-01-01 00:05','2025-01-01 00:15')
    assert r['trades']==1 and r['net_return']==pytest.approx(r['buy_hold_return'])

def test_prefix_audit_rejects_deliberate_future_cheat(monkeypatch):
    import indicator_lab.runner as r
    def cheat(row,d,profile):return d.close.shift(-1).to_numpy()[:,None]
    monkeypatch.setattr(r,'features',cheat)
    with pytest.raises(ValueError,match='CAUSALITY'):r.causality({'id':'cheat'},frame(),'default')

@pytest.mark.parametrize('name',['EMA','RSI','MACD','BBANDS','AD','CDLENGULFING','AO','VWAP','FWMA','SUPERTREND','ICHIMOKU','DPO'])
def test_real_formula_causal_prefix_and_future_mutation(name):
    row=next(r for r in catalog() if r['id']==name)
    assert all(c['passed'] for c in causality(row,frame(),'default'))

def test_paired_test_identical_baseline_is_no_lift():
    y=np.tile([0,1],2000);p=np.full(len(y),.6);times=pd.date_range('2026-01-01',periods=len(y),freq='h',tz='UTC')
    r=paired_evidence(y,p,p,times)
    assert r['accuracy_lift_vs_train_majority']==0 and r['pvalue']==1
    assert r['lift_block_ci_low']==r['lift_block_ci_high']==0

def test_source_audit_does_not_invent_forecast_results():
    a=json.loads((ROOT/'sources/tradingview/pine_audit.json').read_text())
    assert len(a['scripts'])==210
    assert all(r['forecast_status']=='NOT_FORECAST_TESTED' for r in a['scripts'])
    assert all('accuracy' not in r for r in a['scripts'])
    assert len(catalog())==len(set(r['id'] for r in catalog()))
