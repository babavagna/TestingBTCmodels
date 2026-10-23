# Published sources for all 100 supplied candidates

`catalog.json` preserves the supplied list numbers, immutable GitHub URLs, commit
IDs, upstream licenses and SHA-256 of every original strategy. Original strategy
files are unchanged. The Zenbot `lib/` files come from the same pinned Zenbot
commit and retain its MIT license. The offline `package.json`/lockfile are project
runtime configuration; the original Zenbot exchange daemon is never started.

The code in `full_universe/` is an explicit **hourly long/cash signal adaptation**.
It is not a claim that the original native bots were fully reproduced. All-in
position sizing, next-open fills and shared costs replace native execution.
Native stops, ROI schedules, shorts, leverage, pyramiding and custom position
management are omitted. A buy signal is not a next-hour prediction.

Freqtrade compatibility: parameters use published saved buy/sell settings where
provided, otherwise defaults; `.range` contains the selected value as in ordinary
backtesting. Numeric exposed parameters have fixed ±20% sensitivity neighbors.
For sources without exposed parameters, neighbors scale explicitly supplied
TA-Lib periods only. The timeframe alias is `60m`, representing the same hourly
bars while supporting old code which strips the last character to get minutes.
TA-Lib, `technical`, `ta` and SciPy calculations are real installed dependencies.
Unused `pandas_ta` imports receive an empty module: accessing a missing function
raises an error. Removed NumPy math/NaN names receive equivalent standard names.
No live data provider, exchange access, or informative-pair substitute is supplied.

Supported Jesse rules are documented TA-Lib/pandas formula translations. The
source-rule parity tests execute original entry/exit methods with that same
explicit indicator backend; this checks the translation, not complete equivalence
to every Jesse version. Type 11 moving averages in MAGen mean linear regression.
Ichimoku spans are shifted forward from past data. Native balance/quantity entry
guards are replaced by common all-in sizing. DUAL_THRUST and TurtleRules require
additional native state / timeframe adapters and fail closed.

Zenbot executes published `calculate`/`onPeriod` hooks and indicator helpers in
Node. Options use source defaults, then the period is set to one hour. Fixed
numeric-option neighbors vary by ±20%; period strings are unchanged. Native
account-state sources fail closed. Neural is a real native price predictor,
but its cluster/training interface is unsupported by the frozen-training adapter;
no accuracy or investment performance is claimed for it. Some upstream hooks
may have implementation defects; successful completion is not proof of a correct
or profitable native implementation. No source bug is silently repaired.

Full error messages, finite causality checks, source reviews, frozen training
choices and every completed trade are saved in `reports/full100/`. Known future
interpolation is quarantined even when sparse entry thresholds hide its effect.

Gap handling: one common initial warmup of 4,096 observed candles. Indicator
history is retained across gaps; a period counts observed bars, so its calendar
length can stretch. The price table is never filled; the trading engine refuses
a fill across a missing-hour gap. Positions remain held. The expanded policy
differs from the original ten-strategy study, which reset after gaps.
