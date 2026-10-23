"""Attempt every pinned original Pine script offline; never confuse this with a forecast test."""
import concurrent.futures,json,re,subprocess
from pathlib import Path
from btc_lab.data import sha256,write_json,utc_now
from indicator_lab.data import ROOT,load
S=ROOT/'sources/tradingview'
COMMIT='8385cc421888bbf31f36407195796bc0eabafb19'
def check(p):
    code=p.read_text();rel=p.relative_to(S/'everget').as_posix()
    row=dict(id='PINE:'+rel,name=p.stem.replace('_',' ').title(),path=str(p.relative_to(ROOT)),github_url=f'https://github.com/everget/tradingview-pinescript-indicators/blob/{COMMIT}/{rel}',sha256=sha256(p.read_bytes()),pine_version=(re.search(r'@version=(\d+)',code).group(1) if re.search(r'@version=(\d+)',code) else 'unspecified'),forecast_status='NOT_FORECAST_TESTED',native_tradingview_parity='UNVERIFIED',risk_flags=[])
    for pattern,label in [(r'\bsecurity\s*\(|request\.','external_or_other_timeframe_data'),(r'lookahead_on','lookahead_setting'),(r'barstate\.islast|timenow','last_bar_or_clock_dependent'),(r'offset\s*=\s*-','backshifted_display'),(r'\bpivot(high|low)\s*\(','pivot_confirmation_needed')]:
        if re.search(pattern,code):row['risk_flags'].append(label)
    try:
        r=subprocess.run(['node',str(S/'runtime/check.mjs'),str(p),'/tmp/pine-sample.json'],capture_output=True,text=True,timeout=20)
        lines=[x for x in r.stdout.splitlines() if x.startswith('{')]
        row.update(json.loads(lines[-1]) if lines else dict(status='runtime_failed',error=(r.stderr or r.stdout)[-1800:]))
    except subprocess.TimeoutExpired:row.update(status='runtime_timeout',error='20 second compatibility-probe limit')
    return row

def main():
    d,_=load(60);d=d.iloc[:1000]
    candles=[dict(openTime=int(t.timestamp()*1000),closeTime=int((t.timestamp()+3600)*1000)-1,**r.to_dict()) for t,r in d.iterrows()]
    Path('/tmp/pine-sample.json').write_text(json.dumps(candles))
    files=sorted((S/'everget').rglob('*.pine'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,files))
    write_json(S/'pine_audit.json',dict(created_at=utc_now(),source_commit=COMMIT,runtime='PineTS 0.13.0 (independent experimental runtime, not TradingView)',probe='1000 real 2020 hourly Binance candles; original source unchanged; successful probes NOT counted as prediction tests',scripts=rows))
    from collections import Counter
    print(Counter(x['status'] for x in rows))
if __name__=='__main__':main()
