# Cross-check against the full supplied 100-strategy list

All 100 supplied source paths were checked in pinned repository snapshots, and all 100 now have an expanded execution attempt: **83 valid completed signal backtests, 17 blocked or quarantined**.

The original ten were a starter set, not winners of a 100-strategy screen. They match supplied entries #17–21, #25, #31–32, #34 and #39. The expanded audit now covers the complete supplied universe.

Source availability is different from successful execution. Completed rows mean the documented hourly long/cash signal adaptation ran; no full native bot reproduction is claimed. Every blocked strategy has N/A performance.

See the [full report](full100/REPORT.md), [Excel workbook](Bitcoin_Strategy_Leaderboard.xlsx), [100-row source crosswalk](../sources/candidate_crosswalk.csv), and [original source catalog](../sources/full100/catalog.json).

## Why any remain excluded

| List # | Strategy | Final status | Simple explanation |
|---:|---|---|---|
| 3 | GodStra | blocked_execution | The source drops real price rows. Its output no longer matches the shared candle clock, so no valid comparison is reported. |
| 4 | Heracles | blocked_execution | The source drops real price rows. Its output no longer matches the shared candle clock, so no valid comparison is reported. |
| 24 | CCIStrategy | quarantined_lookahead | Later candles changed earlier indicator values. Excluded because this can make the strategy appear to know the future. |
| 36 | ReinforcedQuickie | quarantined_lookahead | Later candles changed earlier indicator values. Excluded because this can make the strategy appear to know the future. |
| 45 | FOttStrategy | blocked_execution | The full calculation did not finish within the declared 120-second signal-call limit. Performance is unknown; this is not evidence that it lost money. |
| 53 | DUAL_THRUST | blocked_execution | Needs a properly timed higher-timeframe anchor adapter. Substituting future completed daily prices would be unsafe. |
| 62 | TurtleRules | blocked_execution | Needs native trade callbacks, previous-trade state and pyramiding. These are not implemented by the shared signal-only account. |
| 76 | neural | blocked_execution | Contains a real price predictor, but its cluster/online-training interface is unsupported. No frozen-training forecast test or accuracy was executed. |
| 79 | rsi | blocked_execution | Reads native account or trade-history state and needs a coupled fill-state adapter. It cannot safely be replaced with an invented account history. |
| 80 | sar | blocked_execution | Reads native account or trade-history state and needs a coupled fill-state adapter. It cannot safely be replaced with an invented account history. |
| 84 | ta_ema | blocked_execution | The full calculation did not finish within the declared 120-second signal-call limit. Performance is unknown; this is not evidence that it lost money. |
| 85 | ta_macd | blocked_execution | The full calculation did not finish within the declared 120-second signal-call limit. Performance is unknown; this is not evidence that it lost money. |
| 86 | ta_macd_ext | blocked_execution | The full calculation did not finish within the declared 120-second signal-call limit. Performance is unknown; this is not evidence that it lost money. |
| 87 | ta_ppo | blocked_execution | The full calculation did not finish within the declared 120-second signal-call limit. Performance is unknown; this is not evidence that it lost money. |
| 90 | ta_trix | blocked_execution | The full calculation did not finish within the declared 120-second signal-call limit. Performance is unknown; this is not evidence that it lost money. |
| 91 | ta_ultosc | blocked_execution | The full calculation did not finish within the declared 120-second signal-call limit. Performance is unknown; this is not evidence that it lost money. |
| 93 | ti_hma | blocked_execution | The full calculation did not finish within the declared 120-second signal-call limit. Performance is unknown; this is not evidence that it lost money. |

CCIStrategy and ReinforcedQuickie have confirmed future-dependent interpolation. Neural is recognized as a native predictor, with an incomplete frozen-training forecast runtime and no invented accuracy. Runtime limits do not prove financial failure.

No genuine unseen Top 10 is issued: 2025–September 2026 were examined earlier, and upstream optimization is unknown. Formula translations and source signal adapters can differ materially from complete native bots. All measured chronological comparisons are retrospective diagnostics.
