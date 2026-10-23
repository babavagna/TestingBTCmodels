# Growing from 10 to 100 strategies

You do not need to edit the trading engine. A developer can add a strategy in
three steps. Do not create fake “new strategies” by copying a catalog entry
or merely renaming it.

1. Find a distinct, suitable open-source strategy on GitHub. Check its license,
   save the original file and license, and record the exact commit and SHA-256.
   Check for use of future prices, negative shifts and centered windows.
2. Add a function in `btc_lab/strategies/your_module.py`. It receives a Pandas
   DataFrame of UTC hourly `open, high, low, close, volume` and returns two Boolean
   Series with the same index: `(enter_long, exit_long)`. Use only the completed
   candle and earlier prices. Keep state/account sizing out of the function.
3. Add an entry to `sources/strategies.json` using an existing entry as the schema.
   Choose a unique id, module, function, title and description. Document every
   change from the source. Add original-signal parity and prefix-invariance tests.

The loader supports **up to 100 catalog entries**. The same downloader, trading
costs, indicators' gap resets, 200-hour warmup, cash budget, fills and reports
apply to every entry. Strategies requiring more than 200 warmup candles require
a documented increase of the **shared** warmup for every strategy, with tests.
The capacity test registers 100 entries to test the loader; it is not a claim
that this repository already contains 100 distinct strategies.

Run `bash setup.sh` to install dependencies and execute the tests, then use
`bash start.sh` to compare the expanded catalog. Comparisons grow roughly in
proportion to strategy count; do not run unrelated optimization jobs in parallel.

The initial strategies are **signal-only hourly adaptations**. A faithful
Freqtrade reproduction with native ROI/stoploss, multiple timeframes, shorts,
or intrabar execution would need a separate documented engine and tests.
