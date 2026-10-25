"""Synthetic software fixtures, never used as published market performance."""
import numpy as np
import pandas as pd
import pytest
from multiasset import probability as tri
from multiasset.engine import portfolio,desired_from_signals
from multiasset.strategy_adapters import feature_frame
from indicator_lab.features import catalog

def prices(n=3500):
    rng=np.random.default_rng(61);c=100*np.exp(np.cumsum(rng.normal(0,.005,n)));o=np.r_[c[0],c[:-1]]
    return pd.DataFrame(dict(open=o,high=np.maximum(o,c)*1.002,low=np.minimum(o,c)*.998,close=c,volume=np.full(n,100.)),index=pd.date_range('2026-01-01',periods=n,freq='h',tz='UTC',name='timestamp'))
def spec():return dict(is_primary_kalshi=True,contract_size='0.0001',underlying_multiplier='1',tick_size='.0001',fractional_trading_enabled=False,market_type='perpetual future',trading_days_per_year=365)

def test_whole_contract_fill_costs_and_unverified_funding_are_explicit():
    d=prices(520);d.loc[:,['open','close']]=100.;d['high']=130.;d['low']=90.;d.iloc[512,d.columns.get_loc('close')]=110;d.iloc[513,d.columns.get_loc('open')]=120;d.iloc[513,d.columns.get_loc('close')]=120
    signal=np.zeros(len(d));signal[511]=1
    start=d.index[512];stop=d.index[514]
    r,_,_,_=portfolio(d,signal,60,spec(),start,stop)
    units=np.floor(10000/(100*1.0005*1.001));expected=(10000-units*100*1.0005*1.001+units*120*.9995*.999)/10000-1
    assert r['net_return']==pytest.approx(expected)
    assert r['trades']==1 and r['whole_contracts']
    assert not r['funding_included'] and not r['rank_eligible'] and r['missing_costs']
    # Quotes are already per contract: multiplying the underlying size again is wrong.
    changed=spec();changed['contract_size']='.1'
    assert portfolio(d,signal,60,changed,start,stop)[0]['net_return']==r['net_return']

def test_missing_contract_specs_or_missing_ohlcv_cannot_fake_financial_results():
    d=prices();s=spec();s['contract_size']=None
    with pytest.raises(ValueError,match='specification'):portfolio(d,np.ones(len(d)),60,s,d.index[1000],d.index[1500])
    with pytest.raises(ValueError,match='OHLCV'):portfolio(d[['close']],np.ones(len(d)),60,spec(),d.index[1000],d.index[1500])

def test_signals_are_not_executed_across_a_missing_candle_gap():
    d=prices(520);signal=np.zeros(len(d));signal[511]=1;d=d.drop(d.index[512]);signal=np.delete(signal,512)
    r,_,_,_=portfolio(d,signal,60,spec(),d.index[512],d.index[514])
    assert r['trades']==0

def test_three_class_targets_include_flat_prices_and_do_not_bridge_gaps():
    d=prices(530);d.iloc[515,d.columns.get_loc('close')]=d.iloc[514].close;d=d.drop(d.index[520])
    y,valid,_,_,_=tri.targets(d,60,.001)
    assert valid[514] and y[514]==1
    assert not valid[519] and not valid[-1] and not valid[:512].any()

def test_chronological_partitions_purge_boundary_answers():
    d=prices();m,dates=tri.split(d,60);_,_,decision,end,_=tri.targets(d,60)
    names=['fit','selection','calibration','validation','retrospective_test']
    for i,name in enumerate(names[:-1]):
        assert end[m[name]].max()<pd.Timestamp(dates[name]['stop'])
        assert (m[name]&m[names[i+1]]).sum()==0

def test_close_only_formulas_work_without_inventing_ohlcv():
    d=prices()[['close']];rows={r['id']:r for r in catalog()}
    assert np.isfinite(feature_frame(rows['RSI'],d,'default')[-1]).all()
    assert list(d.columns)==['close']
    with pytest.raises(ValueError,match='unavailable'):feature_frame(rows['ATR'],d,'default')

def test_probability_features_are_causal_under_prefix_and_future_mutation():
    d=prices();a=tri.features(d);b=tri.features(d.iloc[:2000]);assert np.allclose(a[:2000],b,equal_nan=True)
    changed=d.copy();changed.iloc[2000:]*=3;assert np.allclose(a[:2000],tri.features(changed)[:2000],equal_nan=True)

def test_joint_outcomes_count_correlated_votes_instead_of_multiplying_probabilities():
    votes=np.r_[np.ones((90,2),int),np.zeros((10,2),int)];y=np.r_[np.zeros(90,int),np.full(10,2)];current=np.ones(2,int)
    r=tri.joint_outcomes(votes,y,[0,1],current,min_matches=5)
    assert r['observations']==90 and r['probabilities']==[1.,0.,0.]
    none=tri.joint_outcomes(votes,y,[0,1],np.zeros(2,int))
    assert none['probabilities'] is None and none['observations']==10

def test_multiclass_fit_uses_only_its_training_rows_and_predicts_a_simplex():
    rng=np.random.default_rng(77);x=rng.normal(size=(1000,4));y=np.argmax(np.column_stack([x[:,0],x[:,1],-x[:,0]-x[:,1]]),axis=1);mask=np.arange(len(y))<700
    m=tri.fit(x,y,mask);pred=tri.predict(m,x[700:]);assert np.allclose(pred.sum(1),1) and (pred>=0).all()
    x[700:]=1e6;y[700:]=0;assert tri.fit(x,y,mask)==m

def test_model_metrics_distinguish_class_precision_from_recall():
    y=np.array([0,0,1,2]);p=np.array([[.8,.1,.1],[.1,.8,.1],[.1,.8,.1],[.1,.1,.8]])
    r=tri.metrics(y,p);assert r['accuracy']==.75 and r['classes'][0]['recall']==.5
    assert r['classes'][0]['precision']==1


def test_current_predictions_expire_and_cannot_cross_model_identities(tmp_path):
    import json
    from multiasset_report import current_record
    status=dict(identity='model-A',asset=dict(id='BTC'),minutes=5,basis='trades')
    directory=tmp_path/'reports/multiasset/current';directory.mkdir(parents=True)
    path=directory/'BTC_5m_trades.json'
    row=dict(identity='model-A',status='CURRENT',as_of=pd.Timestamp.now(tz='UTC').isoformat(),probabilities=[.2,.5,.3])
    path.write_text(json.dumps(row));assert current_record(status,tmp_path)['status']=='CURRENT'
    row['as_of']=(pd.Timestamp.now(tz='UTC')-pd.Timedelta(hours=1)).isoformat();path.write_text(json.dumps(row))
    expired=current_record(status,tmp_path);assert expired['status']=='STALE' and expired['probabilities'] is None
    row['identity']='model-B';path.write_text(json.dumps(row));assert current_record(status,tmp_path)=={}
