"""Catalog-driven strategy loader: add entries and modules, not engine branches."""
import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_catalog(path=None):
    catalog = json.loads(Path(path or ROOT / 'sources/strategies.json').read_text())
    if not 1 <= len(catalog) <= 100:
        raise ValueError('The catalog must contain 1 to 100 strategies.')
    ids = [s['id'] for s in catalog]
    if len(set(ids)) != len(ids):
        raise ValueError('Each strategy needs a unique id.')
    for s in catalog:
        if not s['module'].startswith('btc_lab.strategies.'):
            raise ValueError('Strategy modules must be inside btc_lab.strategies.')
        if not s.get('source_url') or not s.get('license'):
            raise ValueError('Each strategy needs its source URL and license.')
        fn = getattr(importlib.import_module(s['module']), s['function'])
        if not callable(fn):
            raise ValueError('Strategy function is not callable.')
    return catalog


def signals(strategy, candles, parameters=None):
    fn = getattr(importlib.import_module(strategy['module']), strategy['function'])
    entry, exit_ = fn(candles.copy(), **(parameters or {}))
    for s in (entry, exit_):
        if not s.index.equals(candles.index) or len(s) != len(candles):
            raise ValueError('Strategy signals must match every candle in order.')
    return entry.fillna(False).astype(bool), exit_.fillna(False).astype(bool)
