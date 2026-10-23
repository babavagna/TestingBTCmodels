"""Run the original signal methods, with only the Freqtrade framework stubbed.
TA-Lib and independently retained official QTPyLib calculations remain real.
This tests signals, not the original Freqtrade trading engine or native exits.
"""
import importlib.util
import json
import sys
import types
from pathlib import Path

import pandas as pd
import pytest

from btc_lab.data import sha256
from btc_lab.strategies import ROOT, load_catalog, signals

CATALOG = load_catalog()


@pytest.fixture
def upstream_framework(monkeypatch):
    spec = importlib.util.spec_from_file_location('reference_qtpylib', ROOT/'sources/reference/qtpylib_indicators.py')
    qtpylib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qtpylib)
    class Parameter:
        def __init__(self, *args, default=None, **kwargs):
            self.value = default
            self.range = [default]
    modules = {name: types.ModuleType(name) for name in ['freqtrade', 'freqtrade.strategy', 'freqtrade.vendor', 'freqtrade.vendor.qtpylib']}
    modules['freqtrade.vendor.qtpylib.indicators'] = qtpylib
    modules['freqtrade.vendor'].qtpylib = modules['freqtrade.vendor.qtpylib']
    modules['freqtrade.vendor.qtpylib'].indicators = qtpylib
    strategy = modules['freqtrade.strategy']
    strategy.IStrategy = type('IStrategy', (), {})
    for name in ['IntParameter', 'DecimalParameter', 'CategoricalParameter']:
        setattr(strategy, name, Parameter)
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)


@pytest.mark.parametrize('s', CATALOG, ids=lambda s: s['id'])
def test_adapter_matches_original_signals(s, candles, upstream_framework):
    source = ROOT/s['local_source']
    assert sha256(source.read_bytes()) == s['source_sha256']
    spec = importlib.util.spec_from_file_location('upstream_'+s['id'], source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = getattr(module, s['original_class'])()
    for space in ['buy', 'sell']:
        for name, value in getattr(original, space+'_params', {}).items():
            getattr(original, name).value = value
    df = original.populate_indicators(candles.copy(), {})
    df = original.populate_entry_trend(df, {})
    df = original.populate_exit_trend(df, {})
    entry, exit_ = signals(s, candles)
    # Uniform warmup is enforced by the engine, so compare all usable signals.
    pd.testing.assert_series_equal(entry.iloc[199:], df.enter_long.fillna(0).eq(1).iloc[199:], check_names=False)
    pd.testing.assert_series_equal(exit_.iloc[199:], df.exit_long.fillna(0).eq(1).iloc[199:], check_names=False)


@pytest.mark.parametrize('s', CATALOG, ids=lambda s: s['id'])
def test_no_future_candles_used_by_any_strategy(s, candles):
    full_entry, full_exit = signals(s, candles)
    for cutoff in (250, 700, 1600):
        entry, exit_ = signals(s, candles.iloc[:cutoff])
        pd.testing.assert_series_equal(entry, full_entry.iloc[:cutoff])
        pd.testing.assert_series_equal(exit_, full_exit.iloc[:cutoff])


def test_catalog_supports_100_without_engine_changes(tmp_path):
    catalog = [dict(CATALOG[i % 10], id=f'extension_{i}') for i in range(100)]
    path = tmp_path/'catalog.json'
    path.write_text(json.dumps(catalog))
    assert len(load_catalog(path)) == 100
    catalog.append(dict(CATALOG[0], id='one_too_many'))
    path.write_text(json.dumps(catalog))
    with pytest.raises(ValueError, match='100'):
        load_catalog(path)


def test_duplicate_ids_rejected(tmp_path):
    path = tmp_path/'catalog.json'
    path.write_text(json.dumps([CATALOG[0], CATALOG[0]]))
    with pytest.raises(ValueError, match='unique'):
        load_catalog(path)
