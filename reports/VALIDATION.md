# Executed validation

Validation performed in the actual cloud environment on 2026-10-23, with
Python 3.12.14 on Linux. No performance figures were invented.

- **88 automated tests passed; zero failed.** See [test-results.xml](test-results.xml).
- The chronological audit executed **381 backtests**: 120 training-candidate fits,
  30 walk-forward evaluations, 20 validation/nominal-test runs, 200 parameter/cost
  stress runs and 11 matching-cost benchmark runs. All completed. See
  [audit/run.json](audit/run.json) and [the audit report](audit/REPORT.md).
- **240 actual-data causal checks** tested seven chronological prefixes and one
  future-price/volume mutation for each of three settings across all ten rules.
  No future dependence was detected. This is evidence, not proof of absence.
- New negative controls deliberately introduce a future-row read and full-sample
  normalization leak; the dynamic comparisons detect both.
- New boundary tests enforce one-hour training purges, future-invariant parameter
  choice, no inherited training positions, correct period-only portfolio scores,
  source-default parity and monotonic cost stress. Saved audit integrity checks
  verify completed-run counts, train/validation/test boundaries and empty ranks.
- The 2025 and 2026 periods were already examined before the audit request. The
  audit never calls them genuinely untouched; all unseen ranks are null and the
  unseen leaderboard is empty. Unknown upstream optimization is disclosed.
- No strategy passed the diagnostic gate in both 2025 and January–September 2026.
  The gate requires positive return, beating same-cost buy-and-hold, and >=30 trades.
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
- Additional known-answer tests validate annualized hourly Sharpe, first-hour costs, idle cash hours, missing-hour exclusions, zero-volatility cases and the explicit low-trade threshold.
- Every saved strategy Sharpe is independently recomputed from its real portfolio history. The completed-execution ledger, ranked order, common benchmark return and three low-trade flags are checked.
- A separate directional-capability audit confirms that none of the ten adapters supplies a next-hour forecast. Zero forecast models were scored; all directional accuracies are N/A. Trading signals and trade win rates are not relabeled as prediction accuracy.
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
