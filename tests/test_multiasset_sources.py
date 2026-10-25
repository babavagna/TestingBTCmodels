"""Synthetic fixtures test source safeguards; they are never historical performance."""
import json
import pandas as pd
import pytest
from multiasset.registry import assets,supplementary_assets
from multiasset.kalshi import parse_candles,ProviderError
from multiasset.data import aggregate

def test_primary_registry_preserves_original_contracts_and_additional_assets():
    rows=assets();byid={r['id']:r for r in rows}
    assert len(rows)>=39 and sum(r['requested_by_name'] for r in rows)==28
    assert byid['KSHIB']['symbol']=='KXKSHIBPERP'
    assert byid['WTI']['symbol']=='KXWTIFUTURE' and byid['WTI']['market_type']=='dated future'
    assert byid['BTC']['contract_size']=='0.000100'
    assert all(r['provider']=='Kalshi' and r['is_primary_kalshi'] for r in rows)
    assert {'KPEPE','US2000','AAPL'}<=set(byid)

def test_external_binance_prices_are_explicitly_supplementary():
    r=supplementary_assets();assert len(r)==28
    assert all(not v['is_primary_kalshi'] and v['price_role']=='SUPPLEMENTARY_EXTERNAL_FEED' for v in r)
    assert not next(v for v in r if v['id']=='KSHIB')['data_enabled']

def boundaries():return pd.Timestamp('2026-09-01',tz='UTC'),pd.Timestamp('2026-09-02',tz='UTC')
def candle(**updates):
    x=dict(end_period_ts=int(pd.Timestamp('2026-09-01 00:01',tz='UTC').timestamp()),price=dict(open='10',high='11',low='9',close='10.5'),volume='2',bid={'close':'10.4'},ask={'close':'10.6'});x.update(updates);return x

def test_provider_end_times_become_real_candle_open_times():
    trades,quotes,m=parse_candles({'candlesticks':[candle()]},1,*boundaries())
    assert trades.index[0]==pd.Timestamp('2026-09-01',tz='UTC')
    assert trades.iloc[0].volume==2 and quotes.iloc[0].close==10.5

def test_midpoint_close_never_becomes_invented_ohlcv():
    trades,quotes,m=parse_candles({'candlesticks':[candle(price={'close':None},volume=None)]},1,*boundaries())
    assert trades.empty and len(quotes)==1
    assert 'high' not in quotes and 'volume' not in quotes

def test_unavailable_ask_sentinel_cannot_make_a_fake_huge_price():
    trades,quotes,m=parse_candles({'candlesticks':[candle(ask={'close':'922337203685477.5807'})]},1,*boundaries())
    assert len(trades)==1 and quotes.empty

def test_conflicting_duplicate_observations_are_rejected():
    with pytest.raises(ProviderError,match='duplicate'):
        parse_candles({'candlesticks':[candle(),candle(price=dict(open='10',high='12',low='9',close='11'))]},1,*boundaries())

def test_impossible_high_low_or_time_alignment_is_rejected():
    with pytest.raises(ProviderError,match='OHLC'):
        parse_candles({'candlesticks':[candle(price=dict(open='10',high='9',low='8',close='10'))]},1,*boundaries())
    with pytest.raises(ProviderError,match='Misaligned'):
        parse_candles({'candlesticks':[candle(end_period_ts=int(pd.Timestamp('2026-09-01 00:01:07',tz='UTC').timestamp()))]},1,*boundaries())
