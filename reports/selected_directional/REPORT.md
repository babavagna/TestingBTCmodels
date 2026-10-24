# Your selected indicators: UP and DOWN accuracy

Your 90 supplied entries contain **52 distinct indicators** (35 candlestick patterns). Repeated IDs were counted once. **156 indicator/timeframe predictions were re-executed** on 5m, 15m and 1h Binance spot BTC/USDT; **0 replay failures**.

**What is being predicted:** once a candle closes, will the NEXT closing price be higher (UP) or lower (DOWN) than the current close? Equal closes are not scored. These are indicator-plus-trained-model forecasts; most of the indicators do not predict direction by themselves.

**Dates:** training 2020–2024; 2025 previously chose the window profile; January–September 2026 is the user-requested RETROSPECTIVE comparison. Every formula feature was regenerated and each frozen model was executed again. No thresholds, coefficients or profiles were changed to improve these results. Newly regenerated probabilities, decisions and accuracy were checked against the earlier saved forecasts.

**Not untouched evidence:** these dates were already examined, and the user chose this subset after earlier results were available. This introduces further selection bias. Native TradingView matching is unverified. The old whole-universe Holm correction is preserved; it is not reset to claim an independent new winner.

## Read the direction percentages correctly

- **UP accuracy:** of the guesses saying UP, how many were right?
- **DOWN accuracy:** of the guesses saying DOWN, how many were right?
- **Overall accuracy:** correct guesses divided by all scored UP and DOWN guesses.
- **UP/DOWN moves found (recall):** a different question: how many actual moves of that kind were detected? These are also in Excel.
- **N/A:** the model never guessed that direction, or there were no scorable pattern events. It never means an invented 0% or 100%.
- **⚠:** fewer than 100 guesses in that direction. Look at counts, not only a large percentage. Above 100 still does not prove reliability.

**28 of the 156 final model/timeframe runs only predicted one direction.** Accuracy near 50% in such a model may mainly reflect guessing the usual direction. For candlesticks, also read the separate pattern-occurrence tables below: the main tables include ordinary candles where the pattern did not appear.

## Best overall accuracy within your requested subset

| Chart | Indicator + model | Overall correct | UP accuracy (guesses) | DOWN accuracy (guesses) |
|---|---|---:|---|---|
| 5m | Elder Force Index (EFI) | 51.91% | 51.56% (45,829 guesses) | 52.41% (32,523 guesses) |
| 15m | Elder Force Index (EFI) | 51.47% | 50.72% (21,060 guesses) | 54.58% (5,128 guesses) |
| 1h | Chaikin A/D Oscillator (ADOSC) | 50.52% | 50.21% (5,714 guesses) | 52.63% (838 guesses) |

These winners are selected by overall accuracy, not the largest UP-only or DOWN-only percentage. Conditional percentages can cover very different numbers of guesses. They do not identify a universally best indicator or prove future performance.

## Every requested indicator: all eligible candles

The following tables score the trained model on every eligible candle. For a candlestick pattern, a result here does NOT mean the pattern itself appeared that many times. Pattern-only results are separate. All three timeframe tables contain every distinct requested ID.

### 5-minute chart

| ID | Overall correct | UP accuracy (guesses) | DOWN accuracy (guesses) | Scored pattern occurrences |
|---|---:|---|---|---:|
| CDLDRAGONFLYDOJI | 49.93% | 49.92% (74,163 guesses) | 50.18% (4,189 guesses) | 2201 |
| ADOSC | 51.73% | 51.26% (51,267 guesses) | 52.63% (27,085 guesses) | N/A: continuous indicator |
| EFI | 51.91% | 51.56% (45,829 guesses) | 52.41% (32,523 guesses) | N/A: continuous indicator |
| CDLTAKURI | 49.94% | 49.92% (74,156 guesses) | 50.29% (4,196 guesses) | 2211 |
| HT_TRENDMODE | 49.85% | 49.87% (69,464 guesses) | 49.75% (8,888 guesses) | N/A: continuous indicator |
| ATR | 50.38% | 50.30% (37,245 guesses) | 50.44% (41,107 guesses) | N/A: continuous indicator |
| NATR | 50.38% | 50.30% (37,245 guesses) | 50.44% (41,107 guesses) | N/A: continuous indicator |
| CDLMARUBOZU | 50.18% | 50.05% (67,574 guesses) | 50.98% (10,778 guesses) | 8168 |
| TRANGE | 50.19% | 50.15% (24,948 guesses) | 50.20% (53,404 guesses) | N/A: continuous indicator |
| CDLADVANCEBLOCK | 50.12% | 50.02% (75,034 guesses) | 52.50% (3,318 guesses) | 1130 |
| ADX | 49.67% | 49.64% (45,319 guesses) | 49.72% (33,033 guesses) | N/A: continuous indicator |
| VAR | 49.91% | 49.91% (78,352 guesses) | N/A (0 guesses) | N/A: continuous indicator |
| DPO | 50.64% | 50.47% (45,933 guesses) | 50.88% (32,419 guesses) | N/A: continuous indicator |
| CDLHANGINGMAN | 50.10% | 50.01% (74,378 guesses) | 51.91% (3,974 guesses) | 2025 |
| ADXR | 49.67% | 49.68% (51,553 guesses) | 49.65% (26,799 guesses) | N/A: continuous indicator |
| CDLSTALLEDPATTERN | 49.93% | 49.92% (77,239 guesses) | 50.85% (1,113 guesses) | 370 |
| CDLDOJISTAR | 49.93% | 49.92% (77,603 guesses) | 50.87% (749 guesses) | 490 |
| CDLDOJI | 50.08% | 49.99% (61,432 guesses) | 50.39% (16,920 guesses) | 10444 |
| STDDEV | 50.18% | 50.10% (34,416 guesses) | 50.24% (43,936 guesses) | N/A: continuous indicator |
| CDL3LINESTRIKE | 49.96% | 49.94% (78,006 guesses) | 55.78% (346 guesses) | 235 |
| CDLMORNINGSTAR | 49.95% | 49.93% (77,955 guesses) | 53.90% (397 guesses) | 199 |
| EOM | 50.71% | 50.40% (61,048 guesses) | 51.82% (17,304 guesses) | N/A: continuous indicator |
| CDLLONGLEGGEDDOJI | 50.10% | 50.01% (62,024 guesses) | 50.45% (16,328 guesses) | 10102 |
| CDLGAPSIDESIDEWHITE | 49.92% | 49.92% (78,241 guesses) | 54.95% (111 guesses) | 55 |
| CDLHARAMICROSS | 49.92% | 49.91% (76,131 guesses) | 50.20% (2,221 guesses) | 1560 |
| CDLEVENINGSTAR | 49.91% | 49.91% (78,176 guesses) | 48.86% (176 guesses) | 176 |
| CDLMORNINGDOJISTAR | 49.92% | 49.92% (78,227 guesses) | 54.40% (125 guesses) | 42 |
| CDLGRAVESTONEDOJI | 49.94% | 49.92% (76,191 guesses) | 50.58% (2,161 guesses) | 2161 |
| CDLXSIDEGAP3METHODS | 49.92% | 49.92% (78,034 guesses) | 51.57% (318 guesses) | 318 |
| CORREL | 49.95% | 49.92% (62,936 guesses) | 50.11% (15,416 guesses) | N/A: continuous indicator |
| CDLRISEFALL3METHODS | 49.91% | 49.91% (78,313 guesses) | 53.85% (39 guesses) ⚠ | 22 |
| CDL3BLACKCROWS | 49.91% | 49.91% (78,336 guesses) | 56.25% (16 guesses) ⚠ | 16 |
| CDLIDENTICAL3CROWS | 49.91% | 49.91% (78,352 guesses) | N/A (0 guesses) | 738 |
| CDLSEPARATINGLINES | 49.94% | 49.92% (77,323 guesses) | 51.02% (1,029 guesses) | 712 |
| CDL3WHITESOLDIERS | 49.91% | 49.91% (77,741 guesses) | 49.75% (611 guesses) | 211 |
| CDLDARKCLOUDCOVER | 49.91% | 49.91% (78,338 guesses) | 50.00% (14 guesses) ⚠ | 14 |
| CDLEVENINGDOJISTAR | 49.90% | 49.90% (78,300 guesses) | 40.38% (52 guesses) ⚠ | 52 |
| CDLHAMMER | 49.91% | 49.91% (78,352 guesses) | N/A (0 guesses) | 3288 |
| CDLHOMINGPIGEON | 49.91% | 49.91% (78,352 guesses) | N/A (0 guesses) | 0 |
| CDLINVERTEDHAMMER | 49.91% | 49.91% (78,352 guesses) | N/A (0 guesses) | 467 |
| CDLMATCHINGLOW | 49.91% | 49.91% (78,352 guesses) | N/A (0 guesses) | 1348 |
| CDLRICKSHAWMAN | 50.00% | 49.95% (72,946 guesses) | 50.67% (5,406 guesses) | 5406 |
| CDLSTICKSANDWICH | 49.91% | 49.91% (78,337 guesses) | 60.00% (15 guesses) ⚠ | 15 |
| CDLTASUKIGAP | 49.91% | 49.91% (78,352 guesses) | N/A (0 guesses) | 0 |
| CDLTRISTAR | 49.91% | 49.91% (78,345 guesses) | 57.14% (7 guesses) ⚠ | 4 |
| RVOL | 50.10% | 50.01% (41,485 guesses) | 50.20% (36,867 guesses) | N/A: continuous indicator |
| CHOP | 49.91% | 49.90% (72,008 guesses) | 49.98% (6,344 guesses) | N/A: continuous indicator |
| CDLHIKKAKE | 49.98% | 49.94% (68,033 guesses) | 50.26% (10,319 guesses) | 10471 |
| CDL3OUTSIDE | 49.98% | 49.94% (75,279 guesses) | 50.83% (3,073 guesses) | 2279 |
| CDLHIGHWAVE | 49.97% | 49.94% (75,016 guesses) | 50.75% (3,336 guesses) | 6579 |
| HT_DCPERIOD | 49.90% | 49.90% (74,051 guesses) | 49.90% (4,301 guesses) | N/A: continuous indicator |
| BETA | 49.91% | 49.91% (78,352 guesses) | N/A (0 guesses) | N/A: continuous indicator |

### 15-minute chart

| ID | Overall correct | UP accuracy (guesses) | DOWN accuracy (guesses) | Scored pattern occurrences |
|---|---:|---|---|---:|
| CDLDRAGONFLYDOJI | 50.03% | 49.85% (25,176 guesses) | 54.55% (1,012 guesses) | 512 |
| ADOSC | 51.11% | 50.50% (20,544 guesses) | 53.31% (5,644 guesses) | N/A: continuous indicator |
| EFI | 51.47% | 50.72% (21,060 guesses) | 54.58% (5,128 guesses) | N/A: continuous indicator |
| CDLTAKURI | 50.02% | 49.85% (25,202 guesses) | 54.56% (986 guesses) | 500 |
| HT_TRENDMODE | 49.68% | 49.68% (26,188 guesses) | N/A (0 guesses) | N/A: continuous indicator |
| ATR | 50.31% | 49.99% (22,013 guesses) | 51.98% (4,175 guesses) | N/A: continuous indicator |
| NATR | 50.31% | 49.99% (22,013 guesses) | 51.98% (4,175 guesses) | N/A: continuous indicator |
| CDLMARUBOZU | 49.93% | 49.79% (23,778 guesses) | 51.37% (2,410 guesses) | 1732 |
| TRANGE | 50.21% | 49.94% (22,654 guesses) | 51.98% (3,534 guesses) | N/A: continuous indicator |
| CDLADVANCEBLOCK | 49.77% | 49.71% (25,218 guesses) | 51.24% (970 guesses) | 332 |
| ADX | 49.63% | 49.59% (22,002 guesses) | 49.83% (4,186 guesses) | N/A: continuous indicator |
| VAR | 49.68% | 49.68% (26,188 guesses) | N/A (0 guesses) | N/A: continuous indicator |
| DPO | 49.86% | 49.74% (22,812 guesses) | 50.71% (3,376 guesses) | N/A: continuous indicator |
| CDLHANGINGMAN | 49.83% | 49.75% (25,424 guesses) | 52.62% (764 guesses) | 395 |
| ADXR | 49.81% | 49.69% (21,779 guesses) | 50.37% (4,409 guesses) | N/A: continuous indicator |
| CDLSTALLEDPATTERN | 49.73% | 49.70% (25,998 guesses) | 53.68% (190 guesses) | 95 |
| CDLDOJISTAR | 49.74% | 49.71% (25,958 guesses) | 53.48% (230 guesses) | 144 |
| CDLDOJI | 49.78% | 49.69% (23,142 guesses) | 50.43% (3,046 guesses) | 3443 |
| STDDEV | 49.68% | 49.68% (26,188 guesses) | N/A (0 guesses) | N/A: continuous indicator |
| CDL3LINESTRIKE | 49.67% | 49.67% (26,153 guesses) | 45.71% (35 guesses) ⚠ | 66 |
| CDLMORNINGSTAR | 49.63% | 49.65% (26,042 guesses) | 45.89% (146 guesses) | 49 |
| EOM | 50.19% | 49.93% (24,432 guesses) | 53.82% (1,756 guesses) | N/A: continuous indicator |
| CDLLONGLEGGEDDOJI | 49.84% | 49.70% (20,591 guesses) | 50.38% (5,597 guesses) | 3414 |
| CDLGAPSIDESIDEWHITE | 49.65% | 49.66% (26,162 guesses) | 34.62% (26 guesses) ⚠ | 13 |
| CDLHARAMICROSS | 49.89% | 49.78% (25,315 guesses) | 53.15% (873 guesses) | 541 |
| CDLEVENINGSTAR | 49.71% | 49.69% (26,056 guesses) | 53.03% (132 guesses) | 66 |
| CDLMORNINGDOJISTAR | 49.66% | 49.67% (26,162 guesses) | 38.46% (26 guesses) ⚠ | 13 |
| CDLGRAVESTONEDOJI | 49.68% | 49.68% (26,188 guesses) | N/A (0 guesses) | 511 |
| CDLXSIDEGAP3METHODS | 49.69% | 49.68% (26,090 guesses) | 51.02% (98 guesses) ⚠ | 98 |
| CORREL | 49.68% | 49.68% (26,187 guesses) | 100.00% (1 guesses) ⚠ | N/A: continuous indicator |
| CDLRISEFALL3METHODS | 49.69% | 49.69% (26,170 guesses) | 61.11% (18 guesses) ⚠ | 10 |
| CDL3BLACKCROWS | 49.68% | 49.68% (26,178 guesses) | 50.00% (10 guesses) ⚠ | 5 |
| CDLIDENTICAL3CROWS | 49.71% | 49.69% (26,114 guesses) | 55.41% (74 guesses) ⚠ | 74 |
| CDLSEPARATINGLINES | 49.73% | 49.70% (26,034 guesses) | 53.90% (154 guesses) | 155 |
| CDL3WHITESOLDIERS | 49.66% | 49.67% (26,144 guesses) | 43.18% (44 guesses) ⚠ | 23 |
| CDLDARKCLOUDCOVER | 49.68% | 49.68% (26,186 guesses) | 50.00% (2 guesses) ⚠ | 2 |
| CDLEVENINGDOJISTAR | 49.67% | 49.67% (26,148 guesses) | 47.50% (40 guesses) ⚠ | 20 |
| CDLHAMMER | 49.76% | 49.71% (25,379 guesses) | 51.30% (809 guesses) | 809 |
| CDLHOMINGPIGEON | 49.68% | 49.68% (26,188 guesses) | N/A (0 guesses) | 0 |
| CDLINVERTEDHAMMER | 49.68% | 49.68% (26,188 guesses) | N/A (0 guesses) | 111 |
| CDLMATCHINGLOW | 49.68% | 49.67% (25,811 guesses) | 49.87% (377 guesses) | 384 |
| CDLRICKSHAWMAN | 49.66% | 49.64% (23,654 guesses) | 49.92% (2,534 guesses) | 2327 |
| CDLSTICKSANDWICH | 49.68% | 49.68% (26,185 guesses) | 33.33% (3 guesses) ⚠ | 3 |
| CDLTASUKIGAP | 49.68% | 49.68% (26,188 guesses) | N/A (0 guesses) | 0 |
| CDLTRISTAR | 49.67% | 49.68% (26,186 guesses) | 0.00% (2 guesses) ⚠ | 1 |
| RVOL | 49.82% | 49.74% (24,590 guesses) | 51.19% (1,598 guesses) | N/A: continuous indicator |
| CHOP | 49.79% | 49.72% (25,014 guesses) | 51.19% (1,174 guesses) | N/A: continuous indicator |
| CDLHIKKAKE | 50.00% | 49.82% (24,063 guesses) | 51.95% (2,125 guesses) | 3935 |
| CDL3OUTSIDE | 49.76% | 49.71% (25,099 guesses) | 50.96% (1,089 guesses) | 778 |
| CDLHIGHWAVE | 49.98% | 49.81% (23,666 guesses) | 51.55% (2,522 guesses) | 2774 |
| HT_DCPERIOD | 49.65% | 49.62% (23,126 guesses) | 49.87% (3,062 guesses) | N/A: continuous indicator |
| BETA | 49.94% | 49.78% (22,911 guesses) | 51.05% (3,277 guesses) | N/A: continuous indicator |

### 1-hour chart

| ID | Overall correct | UP accuracy (guesses) | DOWN accuracy (guesses) | Scored pattern occurrences |
|---|---:|---|---|---:|
| CDLDRAGONFLYDOJI | 49.98% | 49.91% (6,305 guesses) | 51.82% (247 guesses) | 128 |
| ADOSC | 50.52% | 50.21% (5,714 guesses) | 52.63% (838 guesses) | N/A: continuous indicator |
| EFI | 50.20% | 50.03% (5,909 guesses) | 51.79% (643 guesses) | N/A: continuous indicator |
| CDLTAKURI | 49.95% | 49.90% (6,317 guesses) | 51.49% (235 guesses) | 121 |
| HT_TRENDMODE | 48.99% | 49.39% (6,246 guesses) | 40.85% (306 guesses) | N/A: continuous indicator |
| ATR | 50.18% | 50.02% (6,376 guesses) | 56.25% (176 guesses) | N/A: continuous indicator |
| NATR | 50.18% | 50.02% (6,376 guesses) | 56.25% (176 guesses) | N/A: continuous indicator |
| CDLMARUBOZU | 50.21% | 50.03% (6,422 guesses) | 59.23% (130 guesses) | 267 |
| TRANGE | 49.86% | 49.85% (6,345 guesses) | 50.24% (207 guesses) | N/A: continuous indicator |
| CDLADVANCEBLOCK | 49.95% | 49.90% (6,327 guesses) | 51.56% (225 guesses) | 76 |
| ADX | 49.83% | 49.84% (6,527 guesses) | 48.00% (25 guesses) ⚠ | N/A: continuous indicator |
| VAR | 49.65% | 49.75% (6,519 guesses) | 30.30% (33 guesses) ⚠ | N/A: continuous indicator |
| DPO | 50.12% | 49.98% (6,326 guesses) | 53.98% (226 guesses) | N/A: continuous indicator |
| CDLHANGINGMAN | 50.21% | 50.03% (6,366 guesses) | 56.45% (186 guesses) | 94 |
| ADXR | 49.88% | 49.86% (6,538 guesses) | 57.14% (14 guesses) ⚠ | N/A: continuous indicator |
| CDLSTALLEDPATTERN | 49.86% | 49.85% (6,519 guesses) | 51.52% (33 guesses) ⚠ | 11 |
| CDLDOJISTAR | 50.06% | 49.95% (6,510 guesses) | 66.67% (42 guesses) ⚠ | 29 |
| CDLDOJI | 50.24% | 50.05% (6,396 guesses) | 58.33% (156 guesses) | 1015 |
| STDDEV | 49.60% | 49.72% (6,432 guesses) | 43.33% (120 guesses) | N/A: continuous indicator |
| CDL3LINESTRIKE | 49.80% | 49.82% (6,525 guesses) | 44.44% (27 guesses) ⚠ | 20 |
| CDLMORNINGSTAR | 49.76% | 49.80% (6,522 guesses) | 40.00% (30 guesses) ⚠ | 15 |
| EOM | 50.43% | 50.15% (6,198 guesses) | 55.37% (354 guesses) | N/A: continuous indicator |
| CDLLONGLEGGEDDOJI | 50.38% | 50.12% (6,367 guesses) | 59.46% (185 guesses) | 1013 |
| CDLGAPSIDESIDEWHITE | 49.89% | 49.87% (6,537 guesses) | 60.00% (15 guesses) ⚠ | 5 |
| CDLHARAMICROSS | 50.05% | 49.95% (6,479 guesses) | 58.90% (73 guesses) ⚠ | 151 |
| CDLEVENINGSTAR | 49.82% | 49.83% (6,536 guesses) | 43.75% (16 guesses) ⚠ | 16 |
| CDLMORNINGDOJISTAR | 49.80% | 49.82% (6,549 guesses) | 0.00% (3 guesses) ⚠ | 3 |
| CDLGRAVESTONEDOJI | 49.94% | 49.89% (6,398 guesses) | 51.95% (154 guesses) | 160 |
| CDLXSIDEGAP3METHODS | 49.92% | 49.89% (6,527 guesses) | 60.00% (25 guesses) ⚠ | 25 |
| CORREL | 49.92% | 49.88% (6,377 guesses) | 51.43% (175 guesses) | N/A: continuous indicator |
| CDLRISEFALL3METHODS | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | 0 |
| CDL3BLACKCROWS | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | 0 |
| CDLIDENTICAL3CROWS | 49.82% | 49.83% (6,546 guesses) | 33.33% (6 guesses) ⚠ | 6 |
| CDLSEPARATINGLINES | 49.82% | 49.83% (6,516 guesses) | 47.22% (36 guesses) ⚠ | 36 |
| CDL3WHITESOLDIERS | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | 1 |
| CDLDARKCLOUDCOVER | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | 0 |
| CDLEVENINGDOJISTAR | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | 2 |
| CDLHAMMER | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | 191 |
| CDLHOMINGPIGEON | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | 0 |
| CDLINVERTEDHAMMER | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | 23 |
| CDLMATCHINGLOW | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | 132 |
| CDLRICKSHAWMAN | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | 745 |
| CDLSTICKSANDWICH | 49.83% | 49.84% (6,551 guesses) | 0.00% (1 guesses) ⚠ | 1 |
| CDLTASUKIGAP | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | 0 |
| CDLTRISTAR | 49.85% | 49.85% (6,550 guesses) | 50.00% (2 guesses) ⚠ | 2 |
| RVOL | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | N/A: continuous indicator |
| CHOP | 49.85% | 49.85% (6,552 guesses) | N/A (0 guesses) | N/A: continuous indicator |
| CDLHIKKAKE | 49.45% | 49.64% (6,458 guesses) | 36.17% (94 guesses) ⚠ | 1055 |
| CDL3OUTSIDE | 49.88% | 49.86% (6,322 guesses) | 50.43% (230 guesses) | 188 |
| CDLHIGHWAVE | 50.02% | 49.93% (6,157 guesses) | 51.39% (395 guesses) | 851 |
| HT_DCPERIOD | 49.83% | 49.84% (6,549 guesses) | 33.33% (3 guesses) ⚠ | N/A: continuous indicator |
| BETA | 50.00% | 49.92% (6,440 guesses) | 54.46% (112 guesses) | N/A: continuous indicator |

## Candlestick patterns only when they actually appeared

This is the SAME frozen model, restricted to a completed candle whose pattern output is nonzero. We do not assume a positive pattern code automatically means UP: for example, Doji codes can just identify a candle shape. The model was trained on all eligible training candles, not newly fitted only on event rows.

There are **9 pattern/timeframe cases with no scored 2026 occurrences**. Their pattern-only accuracy is N/A. Results based on few occurrences are not reliable rankings. Do not compare event-only percentages directly with all-candle percentages as if coverage were identical.

### 5-minute pattern occurrences

| ID | Scored events | Overall correct on events | UP accuracy (guesses) | DOWN accuracy (guesses) |
|---|---:|---:|---|---|
| CDLDRAGONFLYDOJI | 2201 | 48.30% | 48.29% (2,195 guesses) | 50.00% (6 guesses) ⚠ |
| CDLTAKURI | 2211 | 48.12% | 48.07% (2,205 guesses) | 66.67% (6 guesses) ⚠ |
| CDLMARUBOZU | 8168 | 50.60% | 51.07% (4,053 guesses) | 50.13% (4,115 guesses) |
| CDLADVANCEBLOCK | 1130 | 53.36% | N/A (0 guesses) | 53.36% (1,130 guesses) |
| CDLHANGINGMAN | 2025 | 49.63% | 48.62% (1,738 guesses) | 55.75% (287 guesses) |
| CDLSTALLEDPATTERN | 370 | 52.43% | N/A (0 guesses) | 52.43% (370 guesses) |
| CDLDOJISTAR | 490 | 53.47% | 54.81% (239 guesses) | 52.19% (251 guesses) |
| CDLDOJI | 10444 | 50.69% | 50.99% (1,210 guesses) | 50.65% (9,234 guesses) |
| CDL3LINESTRIKE | 235 | 53.62% | 50.00% (120 guesses) | 57.39% (115 guesses) |
| CDLMORNINGSTAR | 199 | 56.28% | N/A (0 guesses) | 56.28% (199 guesses) |
| CDLLONGLEGGEDDOJI | 10102 | 50.90% | 51.31% (1,331 guesses) | 50.84% (8,771 guesses) |
| CDLGAPSIDESIDEWHITE | 55 ⚠ | 49.09% | 49.09% (55 guesses) ⚠ | N/A (0 guesses) |
| CDLHARAMICROSS | 1560 | 49.74% | 50.06% (809 guesses) | 49.40% (751 guesses) |
| CDLEVENINGSTAR | 176 | 48.86% | 48.86% (176 guesses) | N/A (0 guesses) |
| CDLMORNINGDOJISTAR | 42 ⚠ | 54.76% | N/A (0 guesses) | 54.76% (42 guesses) ⚠ |
| CDLGRAVESTONEDOJI | 2161 | 50.58% | N/A (0 guesses) | 50.58% (2,161 guesses) |
| CDLXSIDEGAP3METHODS | 318 | 49.37% | 50.00% (160 guesses) | 48.73% (158 guesses) |
| CDLRISEFALL3METHODS | 22 ⚠ | 54.55% | 66.67% (9 guesses) ⚠ | 46.15% (13 guesses) ⚠ |
| CDL3BLACKCROWS | 16 ⚠ | 56.25% | N/A (0 guesses) | 56.25% (16 guesses) ⚠ |
| CDLIDENTICAL3CROWS | 738 | 51.63% | 51.63% (738 guesses) | N/A (0 guesses) |
| CDLSEPARATINGLINES | 712 | 51.83% | 53.55% (366 guesses) | 50.00% (346 guesses) |
| CDL3WHITESOLDIERS | 211 | 50.24% | N/A (0 guesses) | 50.24% (211 guesses) |
| CDLDARKCLOUDCOVER | 14 ⚠ | 50.00% | N/A (0 guesses) | 50.00% (14 guesses) ⚠ |
| CDLEVENINGDOJISTAR | 52 ⚠ | 48.08% | 48.08% (52 guesses) ⚠ | N/A (0 guesses) |
| CDLHAMMER | 3288 | 48.51% | 48.51% (3,288 guesses) | N/A (0 guesses) |
| CDLHOMINGPIGEON | 0 ⚠ | N/A | N/A (0 guesses) | N/A (0 guesses) |
| CDLINVERTEDHAMMER | 467 | 54.82% | 54.82% (467 guesses) | N/A (0 guesses) |
| CDLMATCHINGLOW | 1348 | 52.60% | 52.60% (1,348 guesses) | N/A (0 guesses) |
| CDLRICKSHAWMAN | 5406 | 50.67% | N/A (0 guesses) | 50.67% (5,406 guesses) |
| CDLSTICKSANDWICH | 15 ⚠ | 86.67% | 86.67% (15 guesses) ⚠ | N/A (0 guesses) |
| CDLTASUKIGAP | 0 ⚠ | N/A | N/A (0 guesses) | N/A (0 guesses) |
| CDLTRISTAR | 4 ⚠ | 50.00% | 33.33% (3 guesses) ⚠ | 100.00% (1 guesses) ⚠ |
| CDLHIKKAKE | 10471 | 50.44% | 51.14% (5,428 guesses) | 49.69% (5,043 guesses) |
| CDL3OUTSIDE | 2279 | 50.59% | 50.24% (1,236 guesses) | 51.01% (1,043 guesses) |
| CDLHIGHWAVE | 6579 | 50.54% | 50.32% (3,243 guesses) | 50.75% (3,336 guesses) |

### 15-minute pattern occurrences

| ID | Scored events | Overall correct on events | UP accuracy (guesses) | DOWN accuracy (guesses) |
|---|---:|---:|---|---|
| CDLDRAGONFLYDOJI | 512 | 55.47% | N/A (0 guesses) | 55.47% (512 guesses) |
| CDLTAKURI | 500 | 55.80% | N/A (0 guesses) | 55.80% (500 guesses) |
| CDLMARUBOZU | 1732 | 52.77% | 53.63% (867 guesses) | 51.91% (865 guesses) |
| CDLADVANCEBLOCK | 332 | 48.80% | N/A (0 guesses) | 48.80% (332 guesses) |
| CDLHANGINGMAN | 395 | 54.68% | N/A (0 guesses) | 54.68% (395 guesses) |
| CDLSTALLEDPATTERN | 95 ⚠ | 51.58% | N/A (0 guesses) | 51.58% (95 guesses) ⚠ |
| CDLDOJISTAR | 144 | 59.72% | 56.72% (67 guesses) ⚠ | 62.34% (77 guesses) ⚠ |
| CDLDOJI | 3443 | 50.16% | 48.11% (397 guesses) | 50.43% (3,046 guesses) |
| CDL3LINESTRIKE | 66 ⚠ | 53.03% | 53.85% (65 guesses) ⚠ | 0.00% (1 guesses) ⚠ |
| CDLMORNINGSTAR | 49 ⚠ | 51.02% | N/A (0 guesses) | 51.02% (49 guesses) ⚠ |
| CDLLONGLEGGEDDOJI | 3414 | 50.21% | 47.94% (388 guesses) | 50.50% (3,026 guesses) |
| CDLGAPSIDESIDEWHITE | 13 ⚠ | 38.46% | 38.46% (13 guesses) ⚠ | N/A (0 guesses) |
| CDLHARAMICROSS | 541 | 48.98% | 45.53% (246 guesses) | 51.86% (295 guesses) |
| CDLEVENINGSTAR | 66 ⚠ | 54.55% | N/A (0 guesses) | 54.55% (66 guesses) ⚠ |
| CDLMORNINGDOJISTAR | 13 ⚠ | 46.15% | N/A (0 guesses) | 46.15% (13 guesses) ⚠ |
| CDLGRAVESTONEDOJI | 511 | 51.47% | 51.47% (511 guesses) | N/A (0 guesses) |
| CDLXSIDEGAP3METHODS | 98 ⚠ | 47.96% | 47.96% (98 guesses) ⚠ | N/A (0 guesses) |
| CDLRISEFALL3METHODS | 10 ⚠ | 60.00% | 75.00% (4 guesses) ⚠ | 50.00% (6 guesses) ⚠ |
| CDL3BLACKCROWS | 5 ⚠ | 20.00% | 20.00% (5 guesses) ⚠ | N/A (0 guesses) |
| CDLIDENTICAL3CROWS | 74 ⚠ | 47.30% | 47.30% (74 guesses) ⚠ | N/A (0 guesses) |
| CDLSEPARATINGLINES | 155 | 52.90% | 48.72% (78 guesses) ⚠ | 57.14% (77 guesses) ⚠ |
| CDL3WHITESOLDIERS | 23 ⚠ | 26.09% | N/A (0 guesses) | 26.09% (23 guesses) ⚠ |
| CDLDARKCLOUDCOVER | 2 ⚠ | 0.00% | 0.00% (2 guesses) ⚠ | N/A (0 guesses) |
| CDLEVENINGDOJISTAR | 20 ⚠ | 45.00% | N/A (0 guesses) | 45.00% (20 guesses) ⚠ |
| CDLHAMMER | 809 | 51.30% | N/A (0 guesses) | 51.30% (809 guesses) |
| CDLHOMINGPIGEON | 0 ⚠ | N/A | N/A (0 guesses) | N/A (0 guesses) |
| CDLINVERTEDHAMMER | 111 | 57.66% | 57.66% (111 guesses) | N/A (0 guesses) |
| CDLMATCHINGLOW | 384 | 47.66% | 47.66% (384 guesses) | N/A (0 guesses) |
| CDLRICKSHAWMAN | 2327 | 50.06% | N/A (0 guesses) | 50.06% (2,327 guesses) |
| CDLSTICKSANDWICH | 3 ⚠ | 0.00% | 0.00% (3 guesses) ⚠ | N/A (0 guesses) |
| CDLTASUKIGAP | 0 ⚠ | N/A | N/A (0 guesses) | N/A (0 guesses) |
| CDLTRISTAR | 1 ⚠ | 100.00% | 100.00% (1 guesses) ⚠ | N/A (0 guesses) |
| CDLHIKKAKE | 3935 | 49.45% | 49.45% (3,735 guesses) | 49.50% (200 guesses) |
| CDL3OUTSIDE | 778 | 53.60% | 54.03% (409 guesses) | 53.12% (369 guesses) |
| CDLHIGHWAVE | 2774 | 50.90% | 51.34% (1,414 guesses) | 50.44% (1,360 guesses) |

### 1-hour pattern occurrences

| ID | Scored events | Overall correct on events | UP accuracy (guesses) | DOWN accuracy (guesses) |
|---|---:|---:|---|---|
| CDLDRAGONFLYDOJI | 128 | 50.00% | N/A (0 guesses) | 50.00% (128 guesses) |
| CDLTAKURI | 121 | 48.76% | N/A (0 guesses) | 48.76% (121 guesses) |
| CDLMARUBOZU | 267 | 55.43% | 51.43% (140 guesses) | 59.84% (127 guesses) |
| CDLADVANCEBLOCK | 76 ⚠ | 47.37% | N/A (0 guesses) | 47.37% (76 guesses) ⚠ |
| CDLHANGINGMAN | 94 ⚠ | 59.57% | N/A (0 guesses) | 59.57% (94 guesses) ⚠ |
| CDLSTALLEDPATTERN | 11 ⚠ | 63.64% | N/A (0 guesses) | 63.64% (11 guesses) ⚠ |
| CDLDOJISTAR | 29 ⚠ | 41.38% | 33.33% (15 guesses) ⚠ | 50.00% (14 guesses) ⚠ |
| CDLDOJI | 1015 | 49.56% | 47.96% (859 guesses) | 58.33% (156 guesses) |
| CDL3LINESTRIKE | 20 ⚠ | 55.00% | 53.85% (13 guesses) ⚠ | 57.14% (7 guesses) ⚠ |
| CDLMORNINGSTAR | 15 ⚠ | 46.67% | 46.67% (15 guesses) ⚠ | N/A (0 guesses) |
| CDLLONGLEGGEDDOJI | 1013 | 50.44% | 48.43% (828 guesses) | 59.46% (185 guesses) |
| CDLGAPSIDESIDEWHITE | 5 ⚠ | 60.00% | N/A (0 guesses) | 60.00% (5 guesses) ⚠ |
| CDLHARAMICROSS | 151 | 56.29% | 53.85% (78 guesses) ⚠ | 58.90% (73 guesses) ⚠ |
| CDLEVENINGSTAR | 16 ⚠ | 62.50% | 62.50% (16 guesses) ⚠ | N/A (0 guesses) |
| CDLMORNINGDOJISTAR | 3 ⚠ | 0.00% | 0.00% (3 guesses) ⚠ | N/A (0 guesses) |
| CDLGRAVESTONEDOJI | 160 | 51.25% | 51.25% (160 guesses) | N/A (0 guesses) |
| CDLXSIDEGAP3METHODS | 25 ⚠ | 52.00% | 35.71% (14 guesses) ⚠ | 72.73% (11 guesses) ⚠ |
| CDLRISEFALL3METHODS | 0 ⚠ | N/A | N/A (0 guesses) | N/A (0 guesses) |
| CDL3BLACKCROWS | 0 ⚠ | N/A | N/A (0 guesses) | N/A (0 guesses) |
| CDLIDENTICAL3CROWS | 6 ⚠ | 66.67% | 66.67% (6 guesses) ⚠ | N/A (0 guesses) |
| CDLSEPARATINGLINES | 36 ⚠ | 52.78% | 53.33% (15 guesses) ⚠ | 52.38% (21 guesses) ⚠ |
| CDL3WHITESOLDIERS | 1 ⚠ | 100.00% | 100.00% (1 guesses) ⚠ | N/A (0 guesses) |
| CDLDARKCLOUDCOVER | 0 ⚠ | N/A | N/A (0 guesses) | N/A (0 guesses) |
| CDLEVENINGDOJISTAR | 2 ⚠ | 100.00% | 100.00% (2 guesses) ⚠ | N/A (0 guesses) |
| CDLHAMMER | 191 | 58.12% | 58.12% (191 guesses) | N/A (0 guesses) |
| CDLHOMINGPIGEON | 0 ⚠ | N/A | N/A (0 guesses) | N/A (0 guesses) |
| CDLINVERTEDHAMMER | 23 ⚠ | 60.87% | 60.87% (23 guesses) ⚠ | N/A (0 guesses) |
| CDLMATCHINGLOW | 132 | 52.27% | 52.27% (132 guesses) | N/A (0 guesses) |
| CDLRICKSHAWMAN | 745 | 46.31% | 46.31% (745 guesses) | N/A (0 guesses) |
| CDLSTICKSANDWICH | 1 ⚠ | 0.00% | N/A (0 guesses) | 0.00% (1 guesses) ⚠ |
| CDLTASUKIGAP | 0 ⚠ | N/A | N/A (0 guesses) | N/A (0 guesses) |
| CDLTRISTAR | 2 ⚠ | 0.00% | 0.00% (2 guesses) ⚠ | N/A (0 guesses) |
| CDLHIKKAKE | 1055 | 48.34% | 48.39% (1,054 guesses) | 0.00% (1 guesses) ⚠ |
| CDL3OUTSIDE | 188 | 57.98% | 60.36% (111 guesses) | 54.55% (77 guesses) ⚠ |
| CDLHIGHWAVE | 851 | 46.18% | 46.34% (807 guesses) | 43.18% (44 guesses) ⚠ |

## Inputs, costs and limits

- ATR, NATR, TRANGE, variance, standard deviation and similar indicators measure activity or volatility, not a standalone future direction. The direction here comes from the disclosed trained readout.
- CORREL and BETA retain the previously used BTC high/low series. They are NOT Bitcoin-versus-another-asset correlation or market beta; no reference asset was specified.
- Archive checksums, price fingerprints, frozen models and source code were verified. Each selected profile passed numerical shorter-prefix and changed-future checks. All original UP/DOWN decisions matched on re-execution.
- Earlier walk-forward models were re-executed for 2022–2024: **467 successful folds**, **1 original failed fit(s)**, recorded with reasons. Default settings are used in these earlier folds, not profiles chosen later using 2025.
- Descriptive Wilson intervals for UP/DOWN rates are in Excel. They assume independent samples, while market observations can be correlated. No new claim of statistically proven future UP/DOWN skill is made.
- Fees do not change whether a direction guess is correct. Separate portfolio returns still include 0.1% fee plus adverse 0.05% slippage per buy AND sell, 10,000 USDT start, next-adjacent-open long/cash trades and a final-close exit. DOWN means cash, not a short. Buy/hold pays identical entry/exit costs. Simplified fractional orders omit minimum size, rounding, latency and market impact.
- A model can be more accurate and still lose money. Check the net return and buy/hold columns separately.

## Open your focused workbook

[BTC_UP_DOWN_ACCURACY.xlsx](https://github.com/babavagna/TestingBTCmodels/blob/main/BTC_UP_DOWN_ACCURACY.xlsx) is saved in the repository top folder. While signed in, open it and click **Download raw file**. If file downloads fail but the repository opens, **Code → Download ZIP**, unzip the project and open that filename.

Start with **5m Results**, **15m Results** or **1h Results**. The headings are written in plain language; hover a header or read **Column Guide** for definitions. **Pattern Events** contains the actual-occurrence breakdown. **2025 Validation**, **Walk Forward**, **Failures**, **Integrity Checks**, **Reproduction**, **Request List** and **Source and Settings** preserve supporting evidence.

The full machine-readable all-candle and pattern-only results are in the neighboring CSV/JSON files. [Fixed protocol](../../directional_study/PROTOCOL.md), [requested list](../../sources/selected_directional/request_ids.txt), and frozen-input/replay hashes are saved for reproducibility.
