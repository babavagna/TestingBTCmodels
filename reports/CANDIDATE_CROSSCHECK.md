# Cross-check against the user-supplied 100-strategy list

**The original ten were not selected by screening this complete 100-entry list.** This cross-check was performed after the list was supplied.
The original project was a small, auditable starter implementation under one framework, not a search for the best ten of one hundred. No performance evidence justified rejecting the other ninety.

## Verified overlap

All ten current adapters map to entries in the supplied list. A source-path match does not mean that the complete native bot was reproduced: our adapters omit native ROI/stoploss rules.

| List number | Original source | Tested adapter |
| ---: | --- | --- |
| 17 | [ASDTSRockwellTrading](https://github.com/freqtrade/freqtrade-strategies/blob/f3340ce11f5bdf62f598522e64d1f5638eaa13f5/user_data/strategies/berlinguyinca/ASDTSRockwellTrading.py) | Rockwell MACD |
| 18 | [AdxSmas](https://github.com/freqtrade/freqtrade-strategies/blob/f3340ce11f5bdf62f598522e64d1f5638eaa13f5/user_data/strategies/berlinguyinca/AdxSmas.py) | ADX + moving averages |
| 19 | [AverageStrategy](https://github.com/freqtrade/freqtrade-strategies/blob/f3340ce11f5bdf62f598522e64d1f5638eaa13f5/user_data/strategies/berlinguyinca/AverageStrategy.py) | EMA crossover |
| 20 | [AwesomeMacd](https://github.com/freqtrade/freqtrade-strategies/blob/f3340ce11f5bdf62f598522e64d1f5638eaa13f5/user_data/strategies/berlinguyinca/AwesomeMacd.py) | Awesome Oscillator + MACD |
| 21 | [BbandRsi](https://github.com/freqtrade/freqtrade-strategies/blob/f3340ce11f5bdf62f598522e64d1f5638eaa13f5/user_data/strategies/berlinguyinca/BbandRsi.py) | Bollinger + RSI |
| 25 | [CMCWinner](https://github.com/freqtrade/freqtrade-strategies/blob/f3340ce11f5bdf62f598522e64d1f5638eaa13f5/user_data/strategies/berlinguyinca/CMCWinner.py) | CCI + money flow + momentum |
| 31 | [MACDStrategy](https://github.com/freqtrade/freqtrade-strategies/blob/f3340ce11f5bdf62f598522e64d1f5638eaa13f5/user_data/strategies/berlinguyinca/MACDStrategy.py) | MACD + CCI |
| 32 | [MACDStrategy_crossed](https://github.com/freqtrade/freqtrade-strategies/blob/f3340ce11f5bdf62f598522e64d1f5638eaa13f5/user_data/strategies/berlinguyinca/MACDStrategy_crossed.py) | MACD crossover + CCI |
| 34 | [Quickie](https://github.com/freqtrade/freqtrade-strategies/blob/f3340ce11f5bdf62f598522e64d1f5638eaa13f5/user_data/strategies/berlinguyinca/Quickie.py) | Quickie trend reversal |
| 39 | [Simple](https://github.com/freqtrade/freqtrade-strategies/blob/f3340ce11f5bdf62f598522e64d1f5638eaa13f5/user_data/strategies/berlinguyinca/Simple.py) | Simple momentum |

## What the ninety omissions mean

| Remaining group | Count | Actual status / work needed |
| --- | ---: | --- |
| Freqtrade outside the futures folder | 35 | Untested backlog. No individual performance rejection. Requires adapters, native-exit review and execution/leakage tests. |
| Freqtrade futures folder | 7 | Untested. Review trading modes, shorts/margin/funding and exits before comparing with long-only spot. Not every file necessarily enables every futures feature. |
| Jesse | 10 | Untested. Separate framework and order/position APIs. Source needs explicit adapters; some rules include shorts or different risk management. |
| Zenbot | 38 | Untested. JavaScript and legacy framework. README confirms no active maintenance. Porting and dependency review needed; this is not evidence of poor strategy performance. |

The shortlist favored readable indicator-based rules with a common framework and license to make the first pipeline executable and auditable. That was an engineering choice, not a balanced strategy-universe review. It is heavily concentrated in MACD-related rules and does not establish which method families are best.

In particular, **Donchian (#54)** and **SMACrossover (#59)** were omitted, even though the supplied list names them as simple starting examples. Donchian’s inspected source is long-only. The inspected SMACrossover source uses both longs and shorts, so a long-only adaptation would need to be labeled accordingly. Neither has been backtested in this project.

**Neural (#76)** uses convnetjs and predicted prices. It was not tested. The workbook’s “no directional forecasts” conclusion applies only to the ten tested adapters, not all hundred listed candidates. Neural requires a separate causal training/forecast evaluation before any accuracy claim.

**Trendline (#98)** has a commented-out sell signal in the checked source. That is a newly observed review item, not a retroactive claim that it was previously tested and failed.

## Scope of this cross-check

- Parsed all 100 numbered entries and matched exact repository/file paths, not similar indicator names.
- 100 of 100 paths exist in the checked Git snapshots.
- Verified repository-level GPL-3.0/MIT licensing metadata. This is not a complete dependency-license audit.
- Read representative Jesse and Zenbot source and maintainer documentation. Did not install those frameworks or run any new candidate strategy.
- Current Freqtrade main matched the already retained source snapshot at cross-check time. Listed branch URLs can move; the CSV includes immutable snapshot links and Git blob SHA-1 identifiers.
- Checked source availability is not proof of runtime compatibility, causal correctness, profitability or accuracy.
- Prior contamination of the 2025/2026 historical holdout still applies. Adding these candidates does not create a genuinely untouched test.

Checked repository snapshots:

- `freqtrade/freqtrade-strategies`: `f3340ce11f5bdf62f598522e64d1f5638eaa13f5`
- `jesse-ai/example-strategies`: `7c91e0a37bf62165790120d730442e4f6eb00364`
- `DeviaVir/zenbot`: `52872fb4b5f9d10e2f891d95daec05da0b721ceb`

See [the complete 100-entry CSV](../sources/candidate_crosswalk.csv) for an explicit status and remaining work for every item.
No workbook performance table, tested-strategy count or historical result was expanded by this source-only review.
