"""Targeted source review beyond thresholded buy/sell prefix comparisons."""
import ast
import numpy as np
import pandas as pd
from full_universe.freqtrade_adapter import load,ROOT

def static_review(item):
    path=ROOT/item['source_path']
    if path.suffix!='.py':return []
    tree=ast.parse(path.read_text());rows=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='interpolate':
            rows.append(dict(line=node.lineno,issue='Two-sided interpolation can use a later resampled indicator to fill an earlier value'))
    return rows

def indicator_proof(item,data):
    """A published interpolation must also preserve INDICATORS, not only signals.

    Sparse entry rules may never cross a threshold at a tested cutoff even when
    their input feature leaks. Compare the actual numerical indicator frames.
    """
    findings=static_review(item)
    if not findings:return dict(findings=[],checked=False,changed_cells=0)
    segment=data
    def frame(d):
        obj,_,_=load(item)
        f=d.reset_index().rename(columns={d.index.name or 'index':'date'})
        return obj.populate_indicators(f,{'pair':'BTC/USDT'}).set_index('date')
    full=frame(segment)
    attempted=[]
    for offset in range(12):
        cutoff=pd.Timestamp('2025-07-13',tz='UTC')+pd.Timedelta(hours=offset)
        earlier=frame(segment.loc[segment.index<cutoff])
        common=[c for c in earlier.select_dtypes(include='number') if c not in data.columns and c in full]
        delta=~np.isclose(earlier[common].to_numpy(dtype=float),full.loc[earlier.index,common].to_numpy(dtype=float),rtol=1e-10,atol=1e-10,equal_nan=True)
        attempted.append(cutoff.isoformat())
        examples=[]
        for i,j in list(zip(*np.where(delta)))[:8]:
            a,b=earlier.iloc[i][common[j]],full.loc[earlier.index[i],common[j]]
            examples.append(dict(timestamp=earlier.index[i].isoformat(),indicator=str(common[j]),prefix_value=None if pd.isna(a) else float(a),full_future_value=None if pd.isna(b) else float(b)))
        if delta.any():return dict(findings=findings,checked=True,cutoff=cutoff.isoformat(),cutoffs_attempted=attempted,changed_cells=int(delta.sum()),examples=examples)
    return dict(findings=findings,checked=True,cutoffs_attempted=attempted,changed_cells=0,examples=[])
