"""Beginner dashboard. Opens no live exchange connections and places no real orders."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from btc_lab.data import DataError, download, load_verified
from btc_lab.runner import read_current_report, run_all
from btc_lab.strategies import ROOT, load_catalog

st.set_page_config(page_title='Bitcoin Strategy Lab', page_icon='₿', layout='wide')
st.title('₿ Bitcoin Strategy Lab')
st.write('Compare 10 open-source strategy adaptations using the same real Bitcoin prices. No coding or exchange account needed.')
st.info('Research only. These are hourly signal adaptations, not the original Freqtrade results. A profitable past does not guarantee a profitable future.')
st.caption('Binance spot • BTC/USDT • 1-hour candles • UTC • starting balance 10,000 USDT • fee 0.1% + slippage 0.05% on each side')

with st.expander('What do these words mean?'):
    st.markdown('**Backtest:** replay old prices to estimate how trading rules would have behaved.\n\n'
                '**Return:** the percentage change in the starting money, after costs.\n\n'
                '**Sharpe:** average hourly gain compared with how bumpy hourly results are, scaled to a year. Higher is generally better; this is not a percentage or a promise.\n\n'
                '**Profit factor:** total winning-trade money divided by total losing-trade money, after costs. Below 1 means losses outweighed gains. Blank means no losing-trade dollars to divide by.\n\n'
                '**Win rate:** the percentage of completed trades that earned money after costs. Big losses can outweigh many small wins.\n\n'
                '**Drawdown:** the biggest percentage fall from an earlier account high. Lower is better.\n\n'
                '**Trades:** completed buys followed by sells. Zero trades is a real outcome.\n\n'
                '**Slippage:** a deliberately worse execution price for each buy and sell.\n\n'
                '**Warmup:** the first 200 hours calculate indicators before trading begins.\n\n'
                '**Buy and hold:** buy once and sell at the end; a reference with the same costs and start date.')

st.subheader('1. Download prices')
st.write('Target: January 2020 through September 2026, where the exchange actually provides verified files. Missing prices are never filled in.')
if st.button('Download / refresh real prices', type='primary'):
    with st.spinner('Downloading official monthly files and checking their fingerprints. This may take a few minutes…'):
        try:
            report = download(ROOT)
            st.success(f"Downloaded {report['rows']:,} real hourly candles.")
        except Exception as exc:
            st.error(str(exc))
            st.write('If the error says 403 or “Tunnel connection failed”, allow data.binance.vision in environment settings, save the change, then try again. A 403 means blocked access, not missing price history.')

available = False
try:
    candles, manifest = load_verified(ROOT)
    available = True
    st.success(f"Verified prices: {candles.index[0]:%Y-%m-%d %H:%M} to {candles.index[-1]:%Y-%m-%d %H:%M} UTC ({len(candles):,} candles).")
    if manifest['status'] == 'partial':
        st.warning(f"The requested period is incomplete: {manifest['missing_hours']:,} hours are missing. Actual dates will appear on every result. During internal gaps, positions remain held and trading signals pause until 200 consecutive candles are available again.")
except (DataError, OSError, KeyError) as exc:
    st.warning(str(exc))
    st.write('No historical performance has been calculated. The app does not substitute made-up prices.')

st.subheader('2. Compare strategies')
custom_dates = st.checkbox('Choose a smaller date range', disabled=not available)
start, end = None, None
if custom_dates and available:
    a, b = st.columns(2)
    start = a.date_input('First day (UTC)', value=candles.index[0].date(), min_value=candles.index[0].date(), max_value=candles.index[-1].date()).isoformat()
    end = b.date_input('Last day (UTC)', value=candles.index[-1].date(), min_value=candles.index[0].date(), max_value=candles.index[-1].date()).isoformat()
if st.button('Run comparison', disabled=not available):
    with st.spinner('Running all strategies on identical prices…'):
        try:
            run_all(ROOT, start, end)
            st.success('Comparison completed using real archived prices.')
        except Exception as exc:
            st.error(str(exc))

if (ROOT/'reports/run.json').exists():
    try:
        summary, run = read_current_report(ROOT)
        st.subheader('3. Read your results')
        st.write(f"Actual candle range: {run['first_candle']} to {run['last_candle']}. First possible buy: {run['first_trade_opportunity']}.")
        if run['source_coverage_status'] == 'partial':
            st.warning('This is a comparison of the available dates, not complete coverage of January 2020–September 2026.')
        st.dataframe(summary[['rank_by_net_return', 'strategy', 'return_pct', 'sharpe_ratio', 'max_drawdown_pct', 'profit_factor', 'win_rate_pct', 'trades', 'buy_and_hold_return_pct', 'trade_count_flag']], hide_index=True, use_container_width=True)
        st.write(f"Missing-hour events in this range: {run['gap_events']}. No candles were invented. Indicators restart after gaps; existing positions stay held.")
        st.warning('Fewer than 30 completed trades is flagged as too little evidence. More trades alone do not establish reliability.')
        st.info('Next-hour directional accuracy: N/A. All current strategies provide trading signals; none provides next-hour up/down forecasts. No prediction models were scored.')
        st.caption('Sharpe uses annualized hourly net returns, zero risk-free rate, idle hours included, and gap-crossing changes excluded. Ranking is by net return. Return, drawdown and win rate are percentages. Blank win rates mean no completed trades. Strategy ranks describe this historical period only.')
        equity = pd.read_csv(ROOT/'reports/equity.csv.gz', index_col='timestamp', parse_dates=True)
        choices = st.multiselect('Lines to show', list(equity.columns), default=['buy_and_hold', load_catalog()[0]['id']])
        if choices:
            st.line_chart(equity[choices])
        st.download_button('Download results spreadsheet (CSV)', (ROOT/'reports/summary.csv').read_bytes(), 'bitcoin_results.csv', 'text/csv')
        with st.expander('Assumptions and reproducibility'):
            st.json(run)
    except (DataError, OSError, KeyError, ValueError) as exc:
        st.warning(str(exc))

with st.expander('See all 10 strategies and their original GitHub sources'):
    for s in load_catalog():
        st.markdown(f"**{s['title']}** — {s['description']} [Original source]({s['source_url']})")
    st.write('Every strategy uses the same signal-only rules here. The original ROI targets and stoploss settings are omitted. Original source files and licenses are saved in the repository.')
