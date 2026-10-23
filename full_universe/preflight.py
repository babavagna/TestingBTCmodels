"""Real import/indicator execution, preserving failures as evidence."""
import json,traceback,warnings
from pathlib import Path
from btc_lab.data import load_verified
from full_universe.freqtrade_adapter import generate,load
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    warnings.filterwarnings('ignore')
    data,_=load_verified(ROOT); data=data.loc['2024-01-01':'2024-06-01'].iloc[:3600]
    rows=[]
    for item in json.loads((ROOT/'sources/full100/catalog.json').read_text()):
        if item['framework']!='freqtrade':continue
        try:
            obj,params,tf=load(item);en,ex=generate(item,data)
            row=dict(id=item['id'],name=item['name'],status='signal_preflight_completed',entries=int(en.sum()),exits=int(ex.sum()),parameters=params,native_timeframe=tf)
        except Exception as e:
            row=dict(id=item['id'],name=item['name'],status='preflight_failed',error=type(e).__name__+': '+str(e),traceback=traceback.format_exc())
        rows.append(row);print(row['id'],row['name'],row['status'],row.get('error',''),flush=True)
    out=ROOT/'reports/full100';out.mkdir(exist_ok=True)
    (out/'preflight.json').write_text(json.dumps(rows,indent=2)+'\n')
