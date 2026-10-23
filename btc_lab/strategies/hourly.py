"""GPL-3.0-only. Modified signal adaptations of freqtrade/freqtrade-strategies.
See sources/strategies.json for immutable originals and authorship.
Native ROI/stoploss rules are omitted. Keyword defaults preserve source signals;
neighboring settings are used only by the separately labeled robustness audit.
"""
import pandas as pd
import talib.abstract as ta


def above(a, b):
    if not isinstance(b, pd.Series):
        b = pd.Series(b, index=a.index)
    return (a > b) & (a.shift(1) <= b.shift(1))


def bands(series, window=20, stds=2):
    mean = series.rolling(window, min_periods=1).mean()
    std = series.rolling(window, min_periods=1).std(ddof=1)
    return mean - stds * std, mean, mean + stds * std


def macd(d, fast=12, slow=26, signal=9):
    return ta.MACD(d, fastperiod=fast, slowperiod=slow, signalperiod=signal)


def average(d, short=8, long=21):
    short, long = ta.EMA(d, timeperiod=short), ta.EMA(d, timeperiod=long)
    return above(short, long) & (d.volume > 0), above(long, short) & (d.volume > 0)


def bband_rsi(d, rsi_period=14, entry_rsi=30, exit_rsi=70, window=20, stds=2.0):
    rsi = ta.RSI(d, timeperiod=rsi_period)
    lower, _, _ = bands((d.high + d.low + d.close) / 3, window, stds)
    return (rsi < entry_rsi) & (d.close < lower), rsi > exit_rsi


def macd_cci(d, fast=12, slow=26, signal=9, cci_period=14, entry_cci=-48, exit_cci=687):
    m, cci = macd(d, fast, slow, signal), ta.CCI(d, timeperiod=cci_period)
    return ((m['macd'] > m['macdsignal']) & (cci <= entry_cci) & (d.volume > 0),
            (m['macd'] < m['macdsignal']) & (cci >= exit_cci) & (d.volume > 0))


def macd_cross(d, fast=12, slow=26, signal=9, cci_period=14, entry_cci=-50, exit_cci=100):
    m, cci = macd(d, fast, slow, signal), ta.CCI(d, timeperiod=cci_period)
    return above(m['macd'], m['macdsignal']) & (cci <= entry_cci), above(m['macdsignal'], m['macd']) & (cci >= exit_cci)


def rockwell(d, fast=12, slow=26, signal=9):
    m = macd(d, fast, slow, signal)
    return (m['macd'] > 0) & (m['macd'] > m['macdsignal']), m['macd'] < m['macdsignal']


def awesome_macd(d, fast=12, slow=26, signal=9, ao_fast=5, ao_slow=34):
    m = macd(d, fast, slow, signal)
    median = (d.high + d.low) / 2
    ao = median.rolling(ao_fast).mean() - median.rolling(ao_slow).mean()
    return (m['macd'] > 0) & (ao > 0) & (ao.shift(1) < 0), (m['macd'] < 0) & (ao < 0) & (ao.shift(1) > 0)


def simple(d, fast=12, slow=26, signal=9, rsi_period=7, window=12, stds=2.0, entry_rsi=70, exit_rsi=80):
    m, rsi = macd(d, fast, slow, signal), ta.RSI(d, timeperiod=rsi_period)
    _, _, upper = bands(d.close, window, stds)
    return (m['macd'] > 0) & (m['macd'] > m['macdsignal']) & (upper > upper.shift(1)) & (rsi > entry_rsi), rsi > exit_rsi


def quickie(d, tema_period=9, sma_period=200, adx_period=14, entry_adx=30, exit_adx=70, window=20, stds=2.0):
    tema, adx = ta.TEMA(d, timeperiod=tema_period), ta.ADX(d, timeperiod=adx_period)
    _, middle, _ = bands(d.close, window, stds)
    return ((adx > entry_adx) & (tema < middle) & (tema > tema.shift(1)) & (ta.SMA(d, timeperiod=sma_period) > d.close),
            (adx > exit_adx) & (tema > middle) & (tema < tema.shift(1)))


def cmc_winner(d, cci_period=14, mfi_period=14, cmo_period=14, entry_cci=-100, exit_cci=100,
               entry_mfi=20, exit_mfi=80, entry_cmo=-50, exit_cmo=50):
    cci = ta.CCI(d, timeperiod=cci_period).shift(1)
    mfi = ta.MFI(d, timeperiod=mfi_period).shift(1)
    cmo = ta.CMO(d, timeperiod=cmo_period).shift(1)
    return (cci < entry_cci) & (mfi < entry_mfi) & (cmo < entry_cmo), (cci > exit_cci) & (mfi > exit_mfi) & (cmo > exit_cmo)


def adx_smas(d, adx_period=14, short=3, long=6, threshold=25):
    adx = ta.ADX(d, timeperiod=adx_period)
    short, long = ta.SMA(d, timeperiod=short), ta.SMA(d, timeperiod=long)
    return (adx > threshold) & above(short, long), (adx < threshold) & above(long, short)
