# GAP-FADE-REVERSAL - LONG (ATM call) - SL x TP x time-exit grid

**Status:** COMPLETE - all 6359 request groups finished.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

gap up > 1% on day i and day i+1 closes below day i close -> first cross above day i HIGH on day i+2..i+4 -> buy CALL

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 20%, TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:30 = 96 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                                                        |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| GAP_LONG   |                 2703 |                       1840 |                    130 |                      863 | Dhan returned no option candles for this period = 838; no ATM / ITM-1..ITM-3 candle at the entry minute = 23; no option candles after the entry = 2 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): -3: 1, -2: 5, -1: 17, 0: 1817

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 715-715

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  1095312 |  1328205 |  1354378 |  1431210 |   1457894 | 1437083 |
| SL 20%      |   916536 |  1098739 |  1097993 |  1161649 |   1188333 | 1167522 |
| SL 40%      |  1034932 |  1267689 |  1293862 |  1370694 |   1397378 | 1376568 |
| SL 60%      |  1043356 |  1266194 |  1292366 |  1369199 |   1395882 | 1375072 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 715-715

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     3.04 |     3.69 |     3.76 |     3.97 |      4.05 |    3.99 |
| SL 20%      |     2.54 |     3.05 |     3.05 |     3.22 |      3.3  |    3.24 |
| SL 40%      |     2.87 |     3.52 |     3.59 |     3.8  |      3.88 |    3.82 |
| SL 60%      |     2.9  |     3.51 |     3.59 |     3.8  |      3.87 |    3.82 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 715-715

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    55.24 |    53.71 |    53.43 |    53.43 |     53.43 |   53.43 |
| SL 20%      |    54.27 |    52.59 |    52.31 |    52.31 |     52.31 |   52.31 |
| SL 40%      |    55.1  |    53.57 |    53.29 |    53.29 |     53.29 |   53.29 |
| SL 60%      |    55.1  |    53.57 |    53.29 |    53.29 |     53.29 |   53.29 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 941-941

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  1645845 |  1994413 |  2352026 |  2395346 |   2717797 | 2383219 |
| SL 20%      |  1487984 |  1731016 |  1855653 |  1854770 |   2163637 | 1932501 |
| SL 40%      |  1623224 |  1929613 |  2095400 |  2129823 |   2470905 | 2303671 |
| SL 60%      |  1574864 |  1904098 |  2119866 |  2163186 |   2485638 | 2318403 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 941-941

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     3.46 |     4.2  |     4.95 |     5.04 |      5.72 |    5.02 |
| SL 20%      |     3.13 |     3.64 |     3.91 |     3.9  |      4.55 |    4.07 |
| SL 40%      |     3.42 |     4.06 |     4.41 |     4.48 |      5.2  |    4.85 |
| SL 60%      |     3.31 |     4.01 |     4.46 |     4.55 |      5.23 |    4.88 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 941-941

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    56    |    53.35 |    52.82 |    52.6  |     52.6  |   52.5  |
| SL 20%      |    54.2  |    51.12 |    50.58 |    50.37 |     50.37 |   50.27 |
| SL 40%      |    55.79 |    53.03 |    52.5  |    52.28 |     52.28 |   52.28 |
| SL 60%      |    55.9  |    53.24 |    52.71 |    52.5  |     52.5  |   52.5  |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 1291-1291

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  2550472 |  3421835 |  4017398 |  3744213 |   3939330 | 2882951 |
| SL 20%      |  1931802 |  2530789 |  2802385 |  2492791 |   2692422 | 1929089 |
| SL 40%      |  2273187 |  3074259 |  3406583 |  3133360 |   3389464 | 2287186 |
| SL 60%      |  2410473 |  3275663 |  3742762 |  3443965 |   3639081 | 2480175 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 1291-1291

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     3.9  |     5.23 |     6.14 |     5.72 |      6.02 |    4.41 |
| SL 20%      |     2.95 |     3.87 |     4.28 |     3.81 |      4.11 |    2.95 |
| SL 40%      |     3.47 |     4.7  |     5.21 |     4.79 |      5.18 |    3.49 |
| SL 60%      |     3.68 |     5.01 |     5.72 |     5.26 |      5.56 |    3.79 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 1291-1291

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    57.47 |    51.9  |    50.74 |    49.96 |     49.57 |   49.34 |
| SL 20%      |    53.68 |    47.87 |    46.71 |    46.01 |     45.78 |   45.31 |
| SL 40%      |    57.01 |    51.36 |    50.12 |    49.34 |     49.03 |   48.49 |
| SL 60%      |    57.4  |    51.82 |    50.66 |    49.88 |     49.5  |   49.03 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 1687-1687

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  3717232 |  5004529 |  5518495 |  5675739 |   5627947 | 4987066 |
| SL 20%      |  2409144 |  3085943 |  3459654 |  3543551 |   3372962 | 1841930 |
| SL 40%      |  3103354 |  3974489 |  4265368 |  4460720 |   4384056 | 2560274 |
| SL 60%      |  3646211 |  4734995 |  5198547 |  5354997 |   5124433 | 3195871 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 1687-1687

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     4.33 |     5.83 |     6.43 |     6.61 |      6.56 |    5.81 |
| SL 20%      |     2.81 |     3.6  |     4.03 |     4.13 |      3.93 |    2.15 |
| SL 40%      |     3.62 |     4.63 |     4.97 |     5.2  |      5.11 |    2.98 |
| SL 60%      |     4.25 |     5.52 |     6.06 |     6.24 |      5.97 |    3.72 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 1687-1687

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    59.1  |    51.04 |    48.61 |    47.72 |     47.07 |   46.41 |
| SL 20%      |    52.87 |    44.75 |    42.74 |    41.85 |     41.26 |   40.43 |
| SL 40%      |    57.91 |    49.79 |    47.6  |    46.77 |     46.18 |   45.29 |
| SL 60%      |    58.86 |    50.74 |    48.37 |    47.48 |     46.77 |   45.76 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 15:30       | no SL     | TP 80%    |     1687 |     47.72 |     5675739 |      6.61 |            1.66 |        -317105 |

## Top 10 variants by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 15:30       | no SL     | TP 80%    |     1687 |     47.72 |     5675739 |      6.61 |            1.66 |        -317105 |
| GAP_LONG   | 15:30       | no SL     | TP 120%   |     1687 |     47.07 |     5627947 |      6.56 |            1.64 |        -366690 |
| GAP_LONG   | 15:30       | no SL     | TP 60%    |     1687 |     48.61 |     5518495 |      6.43 |            1.66 |        -251742 |
| GAP_LONG   | 15:30       | SL 60%    | TP 80%    |     1687 |     47.48 |     5354997 |      6.24 |            1.62 |        -295095 |
| GAP_LONG   | 12:00       | no SL     | TP 60%    |     1291 |     50.74 |     4017398 |      6.14 |            1.83 |        -145680 |
| GAP_LONG   | 15:30       | SL 60%    | TP 60%    |     1687 |     48.37 |     5198547 |      6.06 |            1.62 |        -234738 |
| GAP_LONG   | 12:00       | no SL     | TP 120%   |     1291 |     49.57 |     3939330 |      6.02 |            1.78 |        -174864 |
| GAP_LONG   | 15:30       | SL 60%    | TP 120%   |     1687 |     46.77 |     5124433 |      5.97 |            1.58 |        -344680 |
| GAP_LONG   | 15:30       | no SL     | TP 40%    |     1687 |     51.04 |     5004529 |      5.83 |            1.65 |        -194494 |
| GAP_LONG   | 15:30       | no SL     | no TP     |     1687 |     46.41 |     4987066 |      5.81 |            1.56 |        -474420 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 15:30       | no SL     | TP 80%    |     1687 |     47.72 |     5675739 |      6.61 |            1.66 |        -317105 |
| GAP_LONG   | 15:30       | no SL     | TP 120%   |     1687 |     47.07 |     5627947 |      6.56 |            1.64 |        -366690 |
| GAP_LONG   | 15:30       | no SL     | TP 60%    |     1687 |     48.61 |     5518495 |      6.43 |            1.66 |        -251742 |
| GAP_LONG   | 15:30       | SL 60%    | TP 80%    |     1687 |     47.48 |     5354997 |      6.24 |            1.62 |        -295095 |
| GAP_LONG   | 15:30       | SL 60%    | TP 60%    |     1687 |     48.37 |     5198547 |      6.06 |            1.62 |        -234738 |
| GAP_LONG   | 15:30       | SL 60%    | TP 120%   |     1687 |     46.77 |     5124433 |      5.97 |            1.58 |        -344680 |
| GAP_LONG   | 15:30       | no SL     | TP 40%    |     1687 |     51.04 |     5004529 |      5.83 |            1.65 |        -194494 |
| GAP_LONG   | 15:30       | no SL     | no TP     |     1687 |     46.41 |     4987066 |      5.81 |            1.56 |        -474420 |
| GAP_LONG   | 15:30       | SL 60%    | TP 40%    |     1687 |     50.74 |     4734995 |      5.52 |            1.61 |        -203700 |
| GAP_LONG   | 15:30       | SL 40%    | TP 80%    |     1687 |     46.77 |     4460720 |      5.2  |            1.51 |        -297282 |

## Files in this folder

`trades_all_variants.csv.gz` (111216 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (1687 trades of the best-PnL variant), `entries.csv` (one row per entry: level, gap %, entry-day offset, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
