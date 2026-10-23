"""GPL-3.0-only. Modified signal adaptations of freqtrade/freqtrade-strategies.
See sources/strategies.json for immutable originals and authorship.
All native ROI/stoploss rules are intentionally replaced by a common signal-only engine.
"""
import pandas as pd
import talib.abstract as ta


def above(a, b):
    if not isinstance(b, pd.Series):
        b = pd.Series(b, index=a.index)
    return (a > b) & (a.shift(1) <= b.shift(1))


def bands(series, window=20):
    mean = series.rolling(window, min_periods=1).mean()
    std = series.rolling(window, min_periods=1).std(ddof=1)
    return mean - 2 * std, mean, mean + 2 * std


def average(d):
    short, long = ta.EMA(d, timeperiod=8), ta.EMA(d, timeperiod=21)
    return above(short, long) & (d.volume > 0), above(long, short) & (d.volume > 0)


def bband_rsi(d):
    rsi = ta.RSI(d, timeperiod=14)
    lower, _, _ = bands((d.high + d.low + d.close) / 3)
    return (rsi < 30) & (d.close < lower), rsi > 70


def macd_cci(d):
    m, cci = ta.MACD(d), ta.CCI(d)
    # Use the source's saved buy_params / sell_params, rather than search defaults.
    return ((m['macd'] > m['macdsignal']) & (cci <= -48) & (d.volume > 0),
            (m['macd'] < m['macdsignal']) & (cci >= 687) & (d.volume > 0))


def macd_cross(d):
    m, cci = ta.MACD(d), ta.CCI(d)
    return above(m['macd'], m['macdsignal']) & (cci <= -50), above(m['macdsignal'], m['macd']) & (cci >= 100)


def rockwell(d):
    m = ta.MACD(d)
    return (m['macd'] > 0) & (m['macd'] > m['macdsignal']), m['macd'] < m['macdsignal']


def awesome_macd(d):
    m = ta.MACD(d)
    median = (d.high + d.low) / 2
    ao = median.rolling(5).mean() - median.rolling(34).mean()
    return (m['macd'] > 0) & (ao > 0) & (ao.shift(1) < 0), (m['macd'] < 0) & (ao < 0) & (ao.shift(1) > 0)


def simple(d):
    m, rsi = ta.MACD(d), ta.RSI(d, timeperiod=7)
    _, _, upper = bands(d.close, 12)
    return (m['macd'] > 0) & (m['macd'] > m['macdsignal']) & (upper > upper.shift(1)) & (rsi > 70), rsi > 80


def quickie(d):
    tema, adx = ta.TEMA(d, timeperiod=9), ta.ADX(d)
    _, middle, _ = bands(d.close)
    return ((adx > 30) & (tema < middle) & (tema > tema.shift(1)) & (ta.SMA(d, timeperiod=200) > d.close),
            (adx > 70) & (tema > middle) & (tema < tema.shift(1)))


def cmc_winner(d):
    cci, mfi, cmo = ta.CCI(d).shift(1), ta.MFI(d).shift(1), ta.CMO(d).shift(1)
    return (cci < -100) & (mfi < 20) & (cmo < -50), (cci > 100) & (mfi > 80) & (cmo > 50)


def adx_smas(d):
    adx, short, long = ta.ADX(d, timeperiod=14), ta.SMA(d, timeperiod=3), ta.SMA(d, timeperiod=6)
    return (adx > 25) & above(short, long), (adx < 25) & above(long, short)
