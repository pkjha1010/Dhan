# BPB BASE - LONG (ATM call) - SL x TP x time-exit grid, entry checked all day

**Status:** PARTIAL - 5234 of 8878 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

BPB base LONG: close above the 10-day high, no later close below it (pullback) -> first 1-minute cross above the highest High since the breakout (full day) -> buy CALL

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 60%, TP 80%, TP 100%, TP 120%, no TP x time exit 15:00, 15:30 = 40 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:------------------------------------------------------------------------------------------------------------|
| BPB_LONG   |                 3566 |                       1102 |                     73 |                      313 | Dhan returned no option candles for this period = 305; no ATM / ITM-1..ITM-3 candle at the entry minute = 8 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): -1: 2, 0: 1100

## Exit 15:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 994-994

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |  1930594 |  2272616 |   2027499 |   2385777 | 1537060 |
| SL 20%      |   619980 |   652593 |    237189 |    451778 |    8069 |
| SL 40%      |  1361718 |  1638946 |   1392449 |   1685340 |  567391 |
| SL 60%      |  1550033 |  1929774 |   1690179 |   2025206 |  535234 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 994-994

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |     3.75 |     4.41 |      3.93 |      4.63 |    2.98 |
| SL 20%      |     1.2  |     1.27 |      0.46 |      0.88 |    0.02 |
| SL 40%      |     2.64 |     3.18 |      2.7  |      3.27 |    1.1  |
| SL 60%      |     3.01 |     3.74 |      3.28 |      3.93 |    1.04 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 994-994

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    45.07 |    44.16 |     43.36 |     43.36 |   43.06 |
| SL 20%      |    37.83 |    36.92 |     36.12 |     36.12 |   35.61 |
| SL 40%      |    43.76 |    43.06 |     42.25 |     42.25 |   41.55 |
| SL 60%      |    44.47 |    43.66 |     42.86 |     42.86 |   42.05 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 1016-1016

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |  1743202 |  2237946 |   2289860 |   2579447 | 1568431 |
| SL 20%      |   614317 |   623366 |    297039 |    467652 |  -36108 |
| SL 40%      |  1121891 |  1368979 |   1244914 |   1457143 |  188731 |
| SL 60%      |  1223422 |  1600493 |   1465705 |   1720070 |   95043 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 1016-1016

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |     3.31 |     4.25 |      4.34 |      4.89 |    2.98 |
| SL 20%      |     1.17 |     1.18 |      0.56 |      0.89 |   -0.07 |
| SL 40%      |     2.13 |     2.6  |      2.36 |      2.76 |    0.36 |
| SL 60%      |     2.32 |     3.04 |      2.78 |      3.26 |    0.18 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 1016-1016

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    43.11 |    42.42 |     41.54 |     41.54 |   40.94 |
| SL 20%      |    36.22 |    35.24 |     34.35 |     34.35 |   33.66 |
| SL 40%      |    41.63 |    40.85 |     39.96 |     39.96 |   38.98 |
| SL 60%      |    42.32 |    41.54 |     40.65 |     40.65 |   39.67 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 15:30       | no SL     | TP 120%   |     1016 |     41.54 |     2579447 |      4.89 |            1.39 |        -741369 |

## Top 10 variants by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 15:30       | no SL     | TP 120%   |     1016 |     41.54 |     2579447 |      4.89 |            1.39 |        -741369 |
| BPB_LONG   | 15:00       | no SL     | TP 120%   |      994 |     43.36 |     2385777 |      4.63 |            1.4  |        -598532 |
| BPB_LONG   | 15:00       | no SL     | TP 80%    |      994 |     44.16 |     2272616 |      4.41 |            1.39 |        -485284 |
| BPB_LONG   | 15:30       | no SL     | TP 100%   |     1016 |     41.54 |     2289860 |      4.34 |            1.35 |        -771693 |
| BPB_LONG   | 15:30       | no SL     | TP 80%    |     1016 |     42.42 |     2237946 |      4.25 |            1.35 |        -633649 |
| BPB_LONG   | 15:00       | no SL     | TP 100%   |      994 |     43.36 |     2027499 |      3.93 |            1.34 |        -579554 |
| BPB_LONG   | 15:00       | SL 60%    | TP 120%   |      994 |     42.86 |     2025206 |      3.93 |            1.33 |        -649345 |
| BPB_LONG   | 15:00       | no SL     | TP 60%    |      994 |     45.07 |     1930594 |      3.75 |            1.34 |        -520953 |
| BPB_LONG   | 15:00       | SL 60%    | TP 80%    |      994 |     43.66 |     1929774 |      3.74 |            1.32 |        -536097 |
| BPB_LONG   | 15:30       | no SL     | TP 60%    |     1016 |     43.11 |     1743202 |      3.31 |            1.28 |        -649807 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 15:30       | no SL     | TP 120%   |     1016 |     41.54 |     2579447 |      4.89 |            1.39 |        -741369 |
| BPB_LONG   | 15:00       | no SL     | TP 120%   |      994 |     43.36 |     2385777 |      4.63 |            1.4  |        -598532 |
| BPB_LONG   | 15:30       | no SL     | TP 100%   |     1016 |     41.54 |     2289860 |      4.34 |            1.35 |        -771693 |
| BPB_LONG   | 15:00       | no SL     | TP 80%    |      994 |     44.16 |     2272616 |      4.41 |            1.39 |        -485284 |
| BPB_LONG   | 15:30       | no SL     | TP 80%    |     1016 |     42.42 |     2237946 |      4.25 |            1.35 |        -633649 |
| BPB_LONG   | 15:00       | no SL     | TP 100%   |      994 |     43.36 |     2027499 |      3.93 |            1.34 |        -579554 |
| BPB_LONG   | 15:00       | SL 60%    | TP 120%   |      994 |     42.86 |     2025206 |      3.93 |            1.33 |        -649345 |
| BPB_LONG   | 15:00       | no SL     | TP 60%    |      994 |     45.07 |     1930594 |      3.75 |            1.34 |        -520953 |
| BPB_LONG   | 15:00       | SL 60%    | TP 80%    |      994 |     43.66 |     1929774 |      3.74 |            1.32 |        -536097 |
| BPB_LONG   | 15:30       | no SL     | TP 60%    |     1016 |     43.11 |     1743202 |      3.31 |            1.28 |        -649807 |

## Files in this folder

`trades_all_variants.csv.gz` (40200 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (1016 trades of the best-PnL variant), `entries.csv` (one row per entry: level, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
