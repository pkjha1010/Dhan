# 10-DAY ACCUMULATION fake-break - SHORT (ATM put) - SL x TP x time-exit grid

**Status:** COMPLETE - all 36 request groups finished.

**Period (entry dates):** 2025-11-13 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (10 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

close above the 10-day high (breakout) -> within 3 days price crosses back below the 10-day low -> buy PUT

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:00, 15:30 = 100 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy    |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| ACC10_SHORT |                   11 |                         11 |                      1 |                        0 |            nan |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 11

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 2-2

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -18206 |   -18206 |   -18206 |    -18206 |  -18206 |
| SL 20%      |   -18825 |   -18825 |   -18825 |    -18825 |  -18825 |
| SL 40%      |   -18206 |   -18206 |   -18206 |    -18206 |  -18206 |
| SL 60%      |   -18206 |   -18206 |   -18206 |    -18206 |  -18206 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 2-2

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -19.93 |   -19.93 |   -19.93 |    -19.93 |  -19.93 |
| SL 20%      |   -20.61 |   -20.61 |   -20.61 |    -20.61 |  -20.61 |
| SL 40%      |   -19.93 |   -19.93 |   -19.93 |    -19.93 |  -19.93 |
| SL 60%      |   -19.93 |   -19.93 |   -19.93 |    -19.93 |  -19.93 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 2-2

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |        0 |        0 |        0 |         0 |       0 |
| SL 20%      |        0 |        0 |        0 |         0 |       0 |
| SL 40%      |        0 |        0 |        0 |         0 |       0 |
| SL 60%      |        0 |        0 |        0 |         0 |       0 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 2-2

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -11779 |   -11779 |   -11779 |    -11779 |  -11779 |
| SL 20%      |   -18825 |   -18825 |   -18825 |    -18825 |  -18825 |
| SL 40%      |   -11779 |   -11779 |   -11779 |    -11779 |  -11779 |
| SL 60%      |   -11779 |   -11779 |   -11779 |    -11779 |  -11779 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 2-2

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -12.89 |   -12.89 |   -12.89 |    -12.89 |  -12.89 |
| SL 20%      |   -20.61 |   -20.61 |   -20.61 |    -20.61 |  -20.61 |
| SL 40%      |   -12.89 |   -12.89 |   -12.89 |    -12.89 |  -12.89 |
| SL 60%      |   -12.89 |   -12.89 |   -12.89 |    -12.89 |  -12.89 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 2-2

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |        0 |        0 |        0 |         0 |       0 |
| SL 20%      |        0 |        0 |        0 |         0 |       0 |
| SL 40%      |        0 |        0 |        0 |         0 |       0 |
| SL 60%      |        0 |        0 |        0 |         0 |       0 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 4-4

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    30473 |    43035 |    41160 |     41160 |   41160 |
| SL 20%      |   -29486 |   -29486 |   -29486 |    -29486 |  -29486 |
| SL 40%      |    30473 |    43035 |    41160 |     41160 |   41160 |
| SL 60%      |    30473 |    43035 |    41160 |     41160 |   41160 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 4-4

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    14.92 |    21.07 |    20.15 |     20.15 |   20.15 |
| SL 20%      |   -14.44 |   -14.44 |   -14.44 |    -14.44 |  -14.44 |
| SL 40%      |    14.92 |    21.07 |    20.15 |     20.15 |   20.15 |
| SL 60%      |    14.92 |    21.07 |    20.15 |     20.15 |   20.15 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 4-4

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |       75 |       75 |       75 |        75 |      75 |
| SL 20%      |       25 |       25 |       25 |        25 |      25 |
| SL 40%      |       75 |       75 |       75 |        75 |      75 |
| SL 60%      |       75 |       75 |       75 |        75 |      75 |

## Exit 15:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 8-8

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     4079 |     6179 |    18054 |      7116 |    7116 |
| SL 20%      |   -64630 |   -64630 |   -64630 |    -64630 |  -64630 |
| SL 40%      |     3614 |     5714 |    17589 |      6651 |    6651 |
| SL 60%      |     4079 |     6179 |    18054 |      7116 |    7116 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 8-8

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     0.96 |     1.46 |     4.27 |      1.68 |    1.68 |
| SL 20%      |   -15.29 |   -15.29 |   -15.29 |    -15.29 |  -15.29 |
| SL 40%      |     0.85 |     1.35 |     4.16 |      1.57 |    1.57 |
| SL 60%      |     0.96 |     1.46 |     4.27 |      1.68 |    1.68 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 8-8

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     37.5 |     37.5 |     37.5 |      37.5 |    37.5 |
| SL 20%      |     12.5 |     12.5 |     12.5 |      12.5 |    12.5 |
| SL 40%      |     37.5 |     37.5 |     37.5 |      37.5 |    37.5 |
| SL 60%      |     37.5 |     37.5 |     37.5 |      37.5 |    37.5 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 10-10

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -6125 |      -76 |    11799 |      5861 |    5861 |
| SL 20%      |   -66105 |   -66105 |   -66105 |    -66105 |  -66105 |
| SL 40%      |    -6590 |     -541 |    11334 |      5396 |    5396 |
| SL 60%      |    -6125 |      -76 |    11799 |      5861 |    5861 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 10-10

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -1.14 |    -0.01 |     2.19 |      1.09 |    1.09 |
| SL 20%      |   -12.28 |   -12.28 |   -12.28 |    -12.28 |  -12.28 |
| SL 40%      |    -1.22 |    -0.1  |     2.11 |      1    |    1    |
| SL 60%      |    -1.14 |    -0.01 |     2.19 |      1.09 |    1.09 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 10-10

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |       30 |       30 |       30 |        30 |      30 |
| SL 20%      |       10 |       10 |       10 |        10 |      10 |
| SL 40%      |       30 |       30 |       30 |        30 |      30 |
| SL 60%      |       30 |       30 |       30 |        30 |      30 |

## Best variant by total PnL

| strategy    | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_SHORT | 15:30       | SL 60%    | TP 80%    |       10 |        30 |       11799 |      2.19 |            1.22 |         -38914 |

## Top 10 variants by ROI (at least 10 trades)

| strategy    | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_SHORT | 15:30       | SL 60%    | TP 80%    |       10 |        30 |       11799 |      2.19 |            1.22 |         -38914 |
| ACC10_SHORT | 15:30       | no SL     | TP 80%    |       10 |        30 |       11799 |      2.19 |            1.22 |         -38914 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 80%    |       10 |        30 |       11334 |      2.11 |            1.21 |         -39379 |
| ACC10_SHORT | 15:30       | no SL     | TP 120%   |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | SL 60%    | TP 120%   |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | no SL     | no TP     |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | SL 60%    | no TP     |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 120%   |       10 |        30 |        5396 |      1    |            1.1  |         -39379 |
| ACC10_SHORT | 15:30       | SL 40%    | no TP     |       10 |        30 |        5396 |      1    |            1.1  |         -39379 |
| ACC10_SHORT | 15:30       | no SL     | TP 60%    |       10 |        30 |         -76 |     -0.01 |            1    |         -38914 |

## Top 10 variants by total PnL (at least 10 trades)

| strategy    | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_SHORT | 15:30       | SL 60%    | TP 80%    |       10 |        30 |       11799 |      2.19 |            1.22 |         -38914 |
| ACC10_SHORT | 15:30       | no SL     | TP 80%    |       10 |        30 |       11799 |      2.19 |            1.22 |         -38914 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 80%    |       10 |        30 |       11334 |      2.11 |            1.21 |         -39379 |
| ACC10_SHORT | 15:30       | no SL     | TP 120%   |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | SL 60%    | TP 120%   |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | no SL     | no TP     |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | SL 60%    | no TP     |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 120%   |       10 |        30 |        5396 |      1    |            1.1  |         -39379 |
| ACC10_SHORT | 15:30       | SL 40%    | no TP     |       10 |        30 |        5396 |      1    |            1.1  |         -39379 |
| ACC10_SHORT | 15:30       | no SL     | TP 60%    |       10 |        30 |         -76 |     -0.01 |            1    |         -38914 |

## Files in this folder

`trades_all_variants.csv.gz` (520 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (10 trades of the best-PnL variant), `entries.csv` (one row per entry: level, Acc high / low, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
