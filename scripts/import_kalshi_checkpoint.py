"""Import a trusted collector snapshot while preserving every old price filename.

Use after merging its Git commit. Original aliases must first be restored from
an immutable local backup so earlier run manifests keep their exact fingerprints.
Incoming files are copied to content-addressed versions before their manifests
are used. Both source checkpoint snapshots are retained.
"""
import argparse,json,shutil
from pathlib import Path
import pandas as pd
from btc_lab.data import sha256,write_json,utc_now
from multiasset.registry import ROOT,assets
from multiasset.kalshi import finalize


def materialize_snapshot(snapshot):
    mapping={}
    for file in (snapshot/'data/kalshi').rglob('*.parquet'):
        if 'current' in file.relative_to(snapshot/'data/kalshi').parts:continue
        relative=file.relative_to(snapshot);digest=sha256(file.read_bytes())
        # Even originally mutable aliases become immutable inputs on import.
        if file.parent.name=='versions':destination=ROOT/relative
        else:destination=ROOT/relative.parent/'versions'/(file.stem+'_'+digest[:16]+'.parquet')
        destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists() and sha256(destination.read_bytes())!=digest:raise ValueError('Content-addressed price collision')
        if not destination.exists():shutil.copyfile(file,destination)
        mapping[str(relative)]=str(destination.relative_to(ROOT))
    return mapping


def rewrite(value,mapping):
    if isinstance(value,list):return [rewrite(v,mapping) for v in value]
    if isinstance(value,dict):return {k:(mapping.get(v,v) if k=='path' and isinstance(v,str) else rewrite(v,mapping)) for k,v in value.items()}
    return value


def choose(a,b):
    if a is None:return b
    if b is None:return a
    ac=a.get('status')=='COMPLETED';bc=b.get('status')=='COMPLETED'
    if ac!=bc:return a if ac else b
    return max([a,b],key=lambda row:row.get('evidence',{}).get('retrieved_at',row.get('attempted_at','')))


def merge(local_snapshot,incoming_snapshot):
    local_snapshot=Path(local_snapshot);incoming_snapshot=Path(incoming_snapshot)
    local_map=materialize_snapshot(local_snapshot);incoming_map=materialize_snapshot(incoming_snapshot)
    registries=[json.loads((p/'data/kalshi/markets.json').read_text()) for p in [local_snapshot,incoming_snapshot]]
    newest=max(registries,key=lambda row:row['created_at']);write_json(ROOT/'data/kalshi/markets.json',newest)
    output=[]
    for spec in assets():
        ledgers=[]
        directory=ROOT/'data/kalshi'/spec['symbol'];directory.mkdir(parents=True,exist_ok=True)
        for snapshot,mapping in [(local_snapshot,local_map),(incoming_snapshot,incoming_map)]:
            file=snapshot/'data/kalshi'/spec['symbol']/'checkpoint.json'
            if not file.exists():continue
            raw=file.read_bytes();backup=directory/'checkpoint_snapshots'/('checkpoint_'+sha256(raw)[:16]+'.json');backup.parent.mkdir(exist_ok=True)
            if not backup.exists():backup.write_bytes(raw)
            ledgers.append(rewrite(json.loads(raw),mapping))
        keys=set().union(*(row['windows'] for row in ledgers)) if ledgers else set()
        ledger=dict(windows={key:None for key in sorted(keys)})
        for key in keys:
            selected=None
            for row in ledgers:selected=choose(selected,row['windows'].get(key))
            ledger['windows'][key]=selected
        write_json(directory/'checkpoint.json',ledger)
        required=['60:'+str(p) for p in pd.period_range('2020-01','2026-09',freq='M')]
        for period in pd.period_range('2020-01','2026-09',freq='M'):
            hourly=ledger['windows'].get('60:'+str(period),{})
            if any(hourly.get(kind) for kind in ['trades','quotes']):
                required.extend('1:'+d.strftime('%Y-%m-%d') for d in pd.date_range(period.start_time,(period+1).start_time,freq='D',inclusive='left'))
        pending=sum(ledger['windows'].get(key,{}).get('status')!='COMPLETED' for key in required)
        error=f'{pending} source windows remain; automated collection will resume them' if pending else None
        manifest=finalize(spec,ledger,error)
        output.append(dict(asset=spec['id'],contract=spec['symbol'],status=manifest['status'],pending_windows=pending,datasets=len(manifest['datasets'])))
    result=dict(updated_at=utc_now(),policy='Both source ledgers retained; newest successful windows selected; incoming prices content-addressed; pre-existing aliases preserved for earlier audited runs',contracts=output)
    write_json(ROOT/'reports/kalshi/checkpoint_import.json',result);print(json.dumps(result,indent=2));return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('local_snapshot');p.add_argument('incoming_snapshot');a=p.parse_args();merge(a.local_snapshot,a.incoming_snapshot)
