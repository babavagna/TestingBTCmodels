# Indicator sources and precise coverage

This is **not all TradingView indicators**. TradingView has an evolving public,
private, paid and invite-only library. Its website was blocked in this environment,
so a complete platform catalog could not be verified. There is no official
TradingView affiliation or native TradingView execution in this project.

- `indicator_catalog.json`: 147 attempted reproducible formulas (61 candlestick
  patterns, 60 other TA-Lib functions, 26 disclosed project formulas). Related
  formulas and parameterizations are not independent discoveries. Every entry is
  attempted on 5m, 15m and 60m candles. Use the results for completed-test counts.
- `talib/src/`: the actual C formula bodies used through TA-Lib 0.6.8 Python,
  bundled core 0.6.4, upstream commit `43f9d5042ecc4bd367941846494ad907bf20ea50`.
  BSD license retained. Functions that are duplicate configurations or require an
  independent period series are excluded explicitly in `features.py`.
- `everget/`: ALL 210 original Pine files from commit
  `8385cc421888bbf31f36407195796bc0eabafb19` of
  https://github.com/everget/tradingview-pinescript-indicators . Original bodies,
  copyright and license headers are retained; root GPL-3.0 license included.
  Individual headers include different licenses, including MIT.
- `runtime/`: optional **PineTS 0.13.0**, pinned by npm lockfile, for compatibility
  probes. This is an independent experimental Pine implementation, not the
  TradingView engine. AGPL-3.0 license retained. Do not infer native agreement.
- `pine_audit.json`: all 210 unchanged original scripts ACTUALLY attempted on 1,000
  real hourly candles. 194 failed this runtime (mostly old Pine versions); 16
  completed compatibility probes. **Neither outcome counts as a completed
  prediction backtest.** Some contain visual utilities rather than indicators.
- `provenance.json`: dependency versions, upstream identities and formula hashes.
- Python formulas and the trained readout are in `indicator_lab/`. A name shared
  with TradingView does not prove identical implementation or defaults.

Four weighted moving-average adaptations were also compared against the original
Pine executed in PineTS. See `reports/predictions/formula_agreement.json`.
This limited agreement is **not** native TradingView parity. The corpus Pine
scripts themselves were not converted or silently assigned TA-Lib results.

Private/invite-only scripts, order-book features, unavailable external markets,
and TradingView proprietary engines remain outside verified coverage. Extending
this catalog requires a disclosed formula, reproducible inputs and causality tests.

Data attribution: Binance spot BTCUSDT official monthly archive URLs and checksums
are in `data/predictions/manifest.json`. Data is used under the saved Binance dataset
terms and CC BY-NC-SA 4.0 conditions; see `sources/BINANCE_DATASET_TERMS.md` and
`sources/BINANCE_PUBLIC_DATA_README.md`. Price aggregates are derived from those
observations, not independent quotes from another exchange.
