# Sources, attribution and licenses

## Ten strategy sources

The ten strategies come from **freqtrade/freqtrade-strategies**, directory
`user_data/strategies/berlinguyinca`, at immutable commit
`f3340ce11f5bdf62f598522e64d1f5638eaa13f5`.

[strategies.json](strategies.json) records each file's original class, immutable
GitHub URL, original timeframe, SHA-256, local path and adaptation notes.
The untouched source files are in [upstream](upstream). They are GPL-3.0;
see the project [LICENSE](../LICENSE). Original authorship and links remain
in the files. Most identify Gert Wohlgemuth; CMCWinner retains its original
unattributed template. These are ten distinct strategies from **one repository**,
not ten independent research teams or ten separate GitHub repositories.

The executable adaptations in `btc_lab/strategies/hourly.py` are modified works.
They retain entry/exit signal formulas, use hourly candles, and **omit all native
Freqtrade ROI targets, stoploss, and execution logic**. This common signal-only
comparison is not an exact reproduction of the authors' full trading bots.
MACDStrategy uses saved `buy_cci=-48` and `sell_cci=687`; AverageStrategy uses
EMA 8/21. No tuning was done against the downloaded Bitcoin data.
Tests execute each original signal method with real TA-Lib and official QTPyLib
calculations, stubbing only Freqtrade framework/parameter objects.

## Indicator reference for tests

`reference/qtpylib_indicators.py` is retained unchanged from
[freqtrade/technical](https://github.com/freqtrade/technical/blob/5852e5407588ad04d539f5d5071c60d9dc69b95a/technical/vendor/qtpylib/indicators.py),
commit `5852e5407588ad04d539f5d5071c60d9dc69b95a`.
Copyright 2016–2018 Ran Aroussi; Apache-2.0. Its license is saved alongside it.
This file is used only in parity tests. The application uses TA-Lib and its
own small rolling-window/crossing helpers. The production Freqtrade project
re-exports these QTPyLib indicators through `technical`.

## Prices and derived research output

**Attribution: Binance Vision, Binance spot BTCUSDT 1-hour klines.**
[Official archive](https://data.binance.vision/) ·
[Official GitHub documentation](https://github.com/binance/binance-public-data)

The source documentation and dataset terms are preserved here from commit
`d571690eb66760763b0bd6e27e8cd35603c7e244` of `binance/binance-public-data`.
The documentation's MIT label refers to repository software. The dataset has
separate terms: **CC BY-NC-SA 4.0**, plus the published dataset terms.
See [BINANCE_DATASET_TERMS.md](BINANCE_DATASET_TERMS.md) and
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
The data and data-derived reports in this project are provided under those
terms for noncommercial personal/educational research; they are not relicensed
under the source code's GPL. Binance does not sponsor or endorse this project.

Transformations: select timestamp/open/high/low/close/volume, normalize source
millisecond/microsecond timestamps to UTC, concatenate months in order and
compress the CSV. No candle prices are interpolated or invented.
The per-month original URLs, SHA-256 fingerprints, row counts and missing hours
are in [data/manifest.json](../data/manifest.json). The cleaned verified dataset
is included in the repository. Original ZIPs are an ignored download cache;
the downloader fetches and verifies them again when needed.
Binance may revise archives; later downloads can produce different data. The
saved manifest identifies exactly the version used for the saved results.
