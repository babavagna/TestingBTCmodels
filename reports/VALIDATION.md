# Executed validation

Validation performed in the actual cloud environment on 2026-10-23, with
Python 3.12.14 on Linux. No performance figures were invented.

- **59 automated tests passed; zero failed.** See [test-results.xml](test-results.xml).
- Ten signal-parity tests execute the saved original GitHub strategy methods,
  using real TA-Lib and the retained official QTPyLib implementation. Only
  Freqtrade's framework/parameter containers are stubbed. These tests compare
  entry and exit signals, not native Freqtrade engine outcomes.
- Ten strategy tests verify that removing future candles cannot change earlier
  signals, across three different cutoffs for every strategy.
- Small, explicitly synthetic test fixtures verify exact entry/exit fees,
  slippage, next-hour fills, conflicting signals, cash reconciliation,
  final liquidation and missing-hour behavior. These fixtures never become
  repository performance results.
- Downloader tests cover milliseconds and microseconds, checksum mismatches,
  cached file tampering, unavailable months versus access denials, malformed
  prices, missing hours and preservation of an earlier valid dataset.
- Full-pipeline tests exercise all ten adapters and buy-and-hold, deterministic
  output fingerprints, consistent dates/costs, gaps and stale-result rejection.
- Capacity and validation tests cover a 100-entry catalog and duplicate ids.
  This tests capacity; it is not 100 distinct implemented strategies.
- Streamlit tests render the actual dashboard with the saved real comparison,
  and separately render an empty-data state that cannot show fabricated ranks.
- A separate saved-research test independently recomputes buy-and-hold proceeds
  from the real starting open, ending close, fees and slippage.
- `pip check` found no broken dependency requirements. `bash setup.sh` installed
  the pinned dependencies into `.venv` and executed the tests successfully.
- The Streamlit server was started with `bash start.sh`; its health endpoint
  returned HTTP 200 with `ok`, and its root returned the application shell.
  Dashboard contents were validated through Streamlit's application test runner.
- All 81 official monthly ZIPs were downloaded and checked against their
  published SHA-256 fingerprints. A second download reverified the cached ZIPs
  and reproduced the same cleaned dataset fingerprint.
- The actual 2020–September 2026 comparison executed all ten strategies and the
  benchmark on 59,129 real shared candles. Full results and trade logs are saved.

The chart library emitted one upstream deprecation warning during dashboard
rendering. It is a notice about a future library API change; it did not prevent
the chart or tests from working. No failing checks were hidden or disabled.

The data itself has 31 missing hours in 15 gaps. That is a source-data limitation,
not a failed installation. The documented pause/reset policy was used; no
replacement prices were created. Drawdown inside missing hours is unknown.

GitHub Actions workflows are included for future tests and optional research
refresh. Their remote execution is separate from the local checks above and
has not been claimed as validated here.
