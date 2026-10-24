#!/usr/bin/env python3
"""Readable, per-indicator actual UP/DOWN results; missing evidence stays explicit."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from indicator_lab.data import ROOT
from directional_study.run import request
OUT=ROOT/'reports/selected_directional'

def pct(v):return 'N/A' if v is None else f'{100*v:.2f}%'
def cell(r,direction):
    n=r[direction+'_calls'];v=r[direction+'_accuracy']
    return 'N/A (0 guesses)' if v is None else f"{pct(v)} ({n:,} guesses){' ⚠' if n<100 else ''}"

def write():
    x=json.loads((OUT/'combined.json').read_text());original,ids,counts,c=request();final=[r for r in x['rows'] if r['period']=='retrospective'];events=[r for r in x['pattern_events'] if r['period']=='retrospective']
    lines=['# Your selected indicators: UP and DOWN accuracy', '',
      f"Your {len(original)} supplied entries contain **{len(ids)} distinct indicators** ({sum(c[n]['pattern'] for n in ids)} candlestick patterns). Repeated IDs were counted once. **{len(final)} indicator/timeframe predictions were re-executed** on 5m, 15m and 1h Binance spot BTC/USDT; **{len(x['failures'])} replay failures**.", '',
      '**What is being predicted:** once a candle closes, will the NEXT closing price be higher (UP) or lower (DOWN) than the current close? Equal closes are not scored. These are indicator-plus-trained-model forecasts; most of the indicators do not predict direction by themselves.', '',
      '**Dates:** training 2020–2024; 2025 previously chose the window profile; January–September 2026 is the user-requested RETROSPECTIVE comparison. Every formula feature was regenerated and each frozen model was executed again. No thresholds, coefficients or profiles were changed to improve these results. Newly regenerated probabilities, decisions and accuracy were checked against the earlier saved forecasts.', '',
      '**Not untouched evidence:** these dates were already examined, and the user chose this subset after earlier results were available. This introduces further selection bias. Native TradingView matching is unverified. The old whole-universe Holm correction is preserved; it is not reset to claim an independent new winner.', '',
      '## Read the direction percentages correctly', '',
      '- **UP accuracy:** of the guesses saying UP, how many were right?',
      '- **DOWN accuracy:** of the guesses saying DOWN, how many were right?',
      '- **Overall accuracy:** correct guesses divided by all scored UP and DOWN guesses.',
      '- **UP/DOWN moves found (recall):** a different question: how many actual moves of that kind were detected? These are also in Excel.',
      '- **N/A:** the model never guessed that direction, or there were no scorable pattern events. It never means an invented 0% or 100%.',
      '- **⚠:** fewer than 100 guesses in that direction. Look at counts, not only a large percentage. Above 100 still does not prove reliability.', '',
      f"**{sum(r['one_sided_forecasts'] for r in final)} of the {len(final)} final model/timeframe runs only predicted one direction.** Accuracy near 50% in such a model may mainly reflect guessing the usual direction. For candlesticks, also read the separate pattern-occurrence tables below: the main tables include ordinary candles where the pattern did not appear.", '',
      '## Best overall accuracy within your requested subset', '',
      '| Chart | Indicator + model | Overall correct | UP accuracy (guesses) | DOWN accuracy (guesses) |', '|---|---|---:|---|---|']
    for m in (5,15,60):
        r=max([r for r in final if r['timeframe_minutes']==m],key=lambda r:r['overall_accuracy'])
        lines.append(f"| {'1h' if m==60 else str(m)+'m'} | {r['name']} ({r['id']}) | {pct(r['overall_accuracy'])} | {cell(r,'up')} | {cell(r,'down')} |")
    lines += ['', 'These winners are selected by overall accuracy, not the largest UP-only or DOWN-only percentage. Conditional percentages can cover very different numbers of guesses. They do not identify a universally best indicator or prove future performance.', '',
      '## Every requested indicator: all eligible candles', '',
      'The following tables score the trained model on every eligible candle. For a candlestick pattern, a result here does NOT mean the pattern itself appeared that many times. Pattern-only results are separate. All three timeframe tables contain every distinct requested ID.']
    for m in (5,15,60):
        lines += ['',f"### {'1-hour' if m==60 else str(m)+'-minute'} chart", '', '| ID | Overall correct | UP accuracy (guesses) | DOWN accuracy (guesses) | Scored pattern occurrences |', '|---|---:|---|---|---:|']
        for n in ids:
            r=next((r for r in final if r['timeframe_minutes']==m and r['id']==n),None)
            if r is None:lines.append(f'| {n} | NOT EXECUTED | N/A | N/A | N/A |');continue
            occurrence='N/A: continuous indicator' if r['pattern_scored_count'] is None else str(r['pattern_scored_count'])
            lines.append(f"| {n} | {pct(r['overall_accuracy'])} | {cell(r,'up')} | {cell(r,'down')} | {occurrence} |")
    lines += ['', '## Candlestick patterns only when they actually appeared', '',
      'This is the SAME frozen model, restricted to a completed candle whose pattern output is nonzero. We do not assume a positive pattern code automatically means UP: for example, Doji codes can just identify a candle shape. The model was trained on all eligible training candles, not newly fitted only on event rows.', '',
      f"There are **{sum(r['forecasts']==0 for r in events)} pattern/timeframe cases with no scored 2026 occurrences**. Their pattern-only accuracy is N/A. Results based on few occurrences are not reliable rankings. Do not compare event-only percentages directly with all-candle percentages as if coverage were identical."]
    for m in (5,15,60):
        lines += ['',f"### {'1-hour' if m==60 else str(m)+'-minute'} pattern occurrences", '', '| ID | Scored events | Overall correct on events | UP accuracy (guesses) | DOWN accuracy (guesses) |', '|---|---:|---:|---|---|']
        for n in ids:
            if not c[n]['pattern']:continue
            r=next((r for r in events if r['id']==n and r['timeframe_minutes']==m),None)
            if r is None:lines.append(f'| {n} | NOT EXECUTED | N/A | N/A | N/A |');continue
            lines.append(f"| {n} | {r['forecasts']}{' ⚠' if r['forecasts']<100 else ''} | {pct(r['overall_accuracy'])} | {cell(r,'up')} | {cell(r,'down')} |")
    lines += ['', '## Inputs, costs and limits', '',
      '- ATR, NATR, TRANGE, variance, standard deviation and similar indicators measure activity or volatility, not a standalone future direction. The direction here comes from the disclosed trained readout.',
      '- CORREL and BETA retain the previously used BTC high/low series. They are NOT Bitcoin-versus-another-asset correlation or market beta; no reference asset was specified.',
      '- Archive checksums, price fingerprints, frozen models and source code were verified. Each selected profile passed numerical shorter-prefix and changed-future checks. All original UP/DOWN decisions matched on re-execution.',
      f"- Earlier walk-forward models were re-executed for 2022–2024: **{sum(r['status']=='FROZEN_FOLD_REEXECUTED' for r in x['walk_forward'])} successful folds**, **{sum(r['status']=='ORIGINAL_FOLD_FAILED' for r in x['walk_forward'])} original failed fit(s)**, recorded with reasons. Default settings are used in these earlier folds, not profiles chosen later using 2025.",
      '- Descriptive Wilson intervals for UP/DOWN rates are in Excel. They assume independent samples, while market observations can be correlated. No new claim of statistically proven future UP/DOWN skill is made.',
      '- Fees do not change whether a direction guess is correct. Separate portfolio returns still include 0.1% fee plus adverse 0.05% slippage per buy AND sell, 10,000 USDT start, next-adjacent-open long/cash trades and a final-close exit. DOWN means cash, not a short. Buy/hold pays identical entry/exit costs. Simplified fractional orders omit minimum size, rounding, latency and market impact.',
      '- A model can be more accurate and still lose money. Check the net return and buy/hold columns separately.', '',
      '## Open your focused workbook', '',
      '[BTC_UP_DOWN_ACCURACY.xlsx](https://github.com/babavagna/TestingBTCmodels/blob/main/BTC_UP_DOWN_ACCURACY.xlsx) is saved in the repository top folder. While signed in, open it and click **Download raw file**. If file downloads fail but the repository opens, **Code → Download ZIP**, unzip the project and open that filename.', '',
      'Start with **5m Results**, **15m Results** or **1h Results**. The headings are written in plain language; hover a header or read **Column Guide** for definitions. **Pattern Events** contains the actual-occurrence breakdown. **2025 Validation**, **Walk Forward**, **Failures**, **Integrity Checks**, **Reproduction**, **Request List** and **Source and Settings** preserve supporting evidence.', '',
      'The full machine-readable all-candle and pattern-only results are in the neighboring CSV/JSON files. [Fixed protocol](../../directional_study/PROTOCOL.md), [requested list](../../sources/selected_directional/request_ids.txt), and frozen-input/replay hashes are saved for reproducibility.', '']
    (OUT/'REPORT.md').write_text('\n'.join(lines));print('Report written for',len(final),'indicator/timeframe re-tests')
if __name__=='__main__':write()
