# 10-DAY ACCUMULATION fake-break - SHORT (ATM put) - SL x TP x time-exit grid

**Status:** COMPLETE - all 1530 request groups finished.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

close above the 10-day high (breakout) -> within 3 days price crosses back below the 10-day low -> buy PUT

**Grid:** stop-loss no SL, SL 20%, SL 40% x target TP 20%, TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:30 = 72 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy    |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                               |
|:------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-----------------------------------------------------------------------------------------------------------|
| ACC10_SHORT |                  345 |                        298 |                     30 |                       47 | Dhan returned no option candles for this period = 44; no ATM / ITM-1..ITM-3 candle at the entry minute = 3 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 292, 1: 4, 3: 2

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 84-84

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   116654 |   163169 |   184483 |   231417 |    197139 |  190140 |
| SL 20%      |   132871 |   179386 |   196332 |   243266 |    208988 |  201989 |
| SL 40%      |    98448 |   144963 |   166276 |   213211 |    178932 |  171934 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 84-84

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     2.71 |     3.79 |     4.29 |     5.38 |      4.58 |    4.42 |
| SL 20%      |     3.09 |     4.17 |     4.56 |     5.65 |      4.86 |    4.69 |
| SL 40%      |     2.29 |     3.37 |     3.86 |     4.95 |      4.16 |    3.99 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 84-84

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    48.81 |    46.43 |    45.24 |    45.24 |     45.24 |   45.24 |
| SL 20%      |    47.62 |    45.24 |    44.05 |    44.05 |     44.05 |   44.05 |
| SL 40%      |    48.81 |    46.43 |    45.24 |    45.24 |     45.24 |   45.24 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 117-117

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   195218 |   178490 |   204997 |   249933 |    215965 |  161427 |
| SL 20%      |   200497 |   196140 |   235983 |   280918 |    242331 |  187792 |
| SL 40%      |   169104 |   159876 |   193247 |   238183 |    204215 |  149677 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 117-117

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     3.26 |     2.98 |     3.42 |     4.17 |      3.61 |    2.7  |
| SL 20%      |     3.35 |     3.28 |     3.94 |     4.69 |      4.05 |    3.14 |
| SL 40%      |     2.82 |     2.67 |     3.23 |     3.98 |      3.41 |    2.5  |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 117-117

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    50.43 |    46.15 |    44.44 |    44.44 |     43.59 |   43.59 |
| SL 20%      |    47.01 |    42.74 |    41.03 |    41.03 |     40.17 |   40.17 |
| SL 40%      |    50.43 |    46.15 |    44.44 |    44.44 |     43.59 |   43.59 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 171-171

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   584021 |   613360 |   703892 |   697938 |    820587 |  792205 |
| SL 20%      |   277071 |   164019 |   210951 |   246345 |    233270 |  165391 |
| SL 40%      |   419093 |   398273 |   467402 |   509806 |    583086 |  565288 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 171-171

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     6.61 |     6.94 |     7.97 |     7.9  |      9.29 |    8.97 |
| SL 20%      |     3.14 |     1.86 |     2.39 |     2.79 |      2.64 |    1.87 |
| SL 40%      |     4.75 |     4.51 |     5.29 |     5.77 |      6.6  |    6.4  |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 171-171

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    63.74 |    54.97 |    52.05 |    50.88 |     50.88 |   50.88 |
| SL 20%      |    50.29 |    40.94 |    39.18 |    38.6  |     37.43 |   37.43 |
| SL 40%      |    61.4  |    52.05 |    49.71 |    49.12 |     48.54 |   48.54 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 264-264

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  1117586 |  1119257 |  1292223 |  1098545 |   1391283 |  492768 |
| SL 20%      |   368054 |   197623 |   522009 |   412755 |    478496 | -401398 |
| SL 40%      |   814668 |   779163 |   994935 |   847245 |   1054603 |  155118 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 264-264

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     8.2  |     8.21 |     9.48 |     8.06 |     10.2  |    3.61 |
| SL 20%      |     2.7  |     1.45 |     3.83 |     3.03 |      3.51 |   -2.94 |
| SL 40%      |     5.97 |     5.71 |     7.3  |     6.21 |      7.73 |    1.14 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 264-264

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    65.91 |    53.41 |    47.73 |    44.7  |     43.94 |   42.8  |
| SL 20%      |    48.86 |    35.61 |    32.2  |    29.92 |     29.17 |   27.65 |
| SL 40%      |    63.26 |    50.38 |    44.7  |    41.67 |     40.91 |   39.39 |

## Best variant by total PnL

| strategy    | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_SHORT | 15:30       | no SL     | TP 120%   |      264 |     43.94 |     1391283 |      10.2 |            1.79 |        -266468 |

## Top 10 variants by ROI (at least 30 trades)

| strategy    | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_SHORT | 15:30       | no SL     | TP 120%   |      264 |     43.94 |     1391283 |     10.2  |            1.79 |        -266468 |
| ACC10_SHORT | 15:30       | no SL     | TP 60%    |      264 |     47.73 |     1292223 |      9.48 |            1.8  |        -219379 |
| ACC10_SHORT | 12:00       | no SL     | TP 120%   |      171 |     50.88 |      820587 |      9.29 |            1.93 |        -220005 |
| ACC10_SHORT | 12:00       | no SL     | no TP     |      171 |     50.88 |      792205 |      8.97 |            1.89 |        -222440 |
| ACC10_SHORT | 15:30       | no SL     | TP 40%    |      264 |     53.41 |     1119257 |      8.21 |            1.81 |        -151701 |
| ACC10_SHORT | 15:30       | no SL     | TP 20%    |      264 |     65.91 |     1117586 |      8.2  |            2.17 |        -115308 |
| ACC10_SHORT | 15:30       | no SL     | TP 80%    |      264 |     44.7  |     1098545 |      8.06 |            1.63 |        -251620 |
| ACC10_SHORT | 12:00       | no SL     | TP 60%    |      171 |     52.05 |      703892 |      7.97 |            1.84 |        -169151 |
| ACC10_SHORT | 12:00       | no SL     | TP 80%    |      171 |     50.88 |      697938 |      7.9  |            1.79 |        -173147 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 120%   |      264 |     40.91 |     1054603 |      7.73 |            1.55 |        -269755 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy    | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_SHORT | 15:30       | no SL     | TP 120%   |      264 |     43.94 |     1391283 |     10.2  |            1.79 |        -266468 |
| ACC10_SHORT | 15:30       | no SL     | TP 60%    |      264 |     47.73 |     1292223 |      9.48 |            1.8  |        -219379 |
| ACC10_SHORT | 15:30       | no SL     | TP 40%    |      264 |     53.41 |     1119257 |      8.21 |            1.81 |        -151701 |
| ACC10_SHORT | 15:30       | no SL     | TP 20%    |      264 |     65.91 |     1117586 |      8.2  |            2.17 |        -115308 |
| ACC10_SHORT | 15:30       | no SL     | TP 80%    |      264 |     44.7  |     1098545 |      8.06 |            1.63 |        -251620 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 120%   |      264 |     40.91 |     1054603 |      7.73 |            1.55 |        -269755 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 60%    |      264 |     44.7  |      994935 |      7.3  |            1.56 |        -222665 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 80%    |      264 |     41.67 |      847245 |      6.21 |            1.45 |        -254907 |
| ACC10_SHORT | 12:00       | no SL     | TP 120%   |      171 |     50.88 |      820587 |      9.29 |            1.93 |        -220005 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 20%    |      264 |     63.26 |      814668 |      5.97 |            1.7  |        -102644 |

## Files in this folder

`trades_all_variants.csv.gz` (11448 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (264 trades of the best-PnL variant), `entries.csv` (one row per entry: level, Acc high / low, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
