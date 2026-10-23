# Shared price data

`btcusdt_1h.csv.gz` contains real Binance spot BTC/USDT hourly candles, shared
by all strategies. Open timestamps are UTC. Each row includes open, high, low,
close and volume. The compressed file is readable by Pandas or any gzip tool.

`manifest.json` records exact requested and actual dates, every original ZIP and
checksum URL, verified SHA-256 fingerprints, row counts and every missing hour.
The downloader does not fill gaps. `raw/` is an ignored cache of official ZIPs.
The downloader revalidates cached ZIPs against the current published checksum.

The successful download obtained all 81 monthly archives from January 2020
through September 2026, with **59,129 candles**. There are **31 missing hours**
in 15 gaps. “Partial” in the manifest means these holes exist; it does not mean
an entire requested month was silently omitted.

Price attribution and license: **Binance Vision**, CC BY-NC-SA 4.0 plus
[saved dataset terms](../sources/BINANCE_DATASET_TERMS.md). See
[source and transformation notes](../sources/README.md). Research data and its
derived reports are separate from the application's GPL-licensed code.
