"""All test candles are synthetic fixtures, never published as historical results."""
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def candles():
    rng = np.random.default_rng(2451)
    n = 2400
    close = 100 * np.exp(np.cumsum(rng.normal(0.00005, 0.015, n)))
    opens = np.r_[close[0], close[:-1]]
    return pd.DataFrame(dict(open=opens, high=np.maximum(opens, close)*1.006,
                             low=np.minimum(opens, close)*0.994, close=close,
                             volume=rng.uniform(10, 1000, n)),
                        index=pd.date_range('2020-01-01', periods=n, freq='h', tz='UTC', name='timestamp'))
