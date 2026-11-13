# BPB BASE - LONG (ATM call) - SL x TP x time-exit grid, entry checked all day

**Status:** PARTIAL - 119 of 167 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2025-11-13 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (10 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

BPB base LONG: close above the 10-day high, no later close below it (pullback) -> first 1-minute cross above the highest High since the breakout (full day) -> buy CALL

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:00, 15:30 = 100 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| BPB_LONG   |                   50 |                         27 |                      2 |                        0 |            nan |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 27

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 12-12

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     1295 |     1295 |     1295 |      1295 |    1295 |
| SL 20%      |     4972 |     4972 |     4972 |      4972 |    4972 |
| SL 40%      |     1295 |     1295 |     1295 |      1295 |    1295 |
| SL 60%      |     1295 |     1295 |     1295 |      1295 |    1295 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 12-12

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     0.2  |     0.2  |     0.2  |      0.2  |    0.2  |
| SL 20%      |     0.77 |     0.77 |     0.77 |      0.77 |    0.77 |
| SL 40%      |     0.2  |     0.2  |     0.2  |      0.2  |    0.2  |
| SL 60%      |     0.2  |     0.2  |     0.2  |      0.2  |    0.2  |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 12-12

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    66.67 |    66.67 |    66.67 |     66.67 |   66.67 |
| SL 20%      |    66.67 |    66.67 |    66.67 |     66.67 |   66.67 |
| SL 40%      |    66.67 |    66.67 |    66.67 |     66.67 |   66.67 |
| SL 60%      |    66.67 |    66.67 |    66.67 |     66.67 |   66.67 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 13-13

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -40029 |   -40029 |   -40029 |    -40029 |  -40029 |
| SL 20%      |   -16522 |   -16522 |   -16522 |    -16522 |  -16522 |
| SL 40%      |   -35979 |   -35979 |   -35979 |    -35979 |  -35979 |
| SL 60%      |   -46891 |   -46891 |   -46891 |    -46891 |  -46891 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 13-13

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -5.68 |    -5.68 |    -5.68 |     -5.68 |   -5.68 |
| SL 20%      |    -2.34 |    -2.34 |    -2.34 |     -2.34 |   -2.34 |
| SL 40%      |    -5.1  |    -5.1  |    -5.1  |     -5.1  |   -5.1  |
| SL 60%      |    -6.65 |    -6.65 |    -6.65 |     -6.65 |   -6.65 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 13-13

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    38.46 |    38.46 |    38.46 |     38.46 |   38.46 |
| SL 20%      |    38.46 |    38.46 |    38.46 |     38.46 |   38.46 |
| SL 40%      |    38.46 |    38.46 |    38.46 |     38.46 |   38.46 |
| SL 60%      |    38.46 |    38.46 |    38.46 |     38.46 |   38.46 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 22-22

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    15746 |    15966 |    25941 |     17916 |   17916 |
| SL 20%      |     3655 |     3875 |    13850 |      5825 |    5825 |
| SL 40%      |   -23466 |   -23245 |   -13270 |    -21295 |  -21295 |
| SL 60%      |   -28242 |   -28021 |   -18046 |    -26071 |  -26071 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 22-22

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     1.3  |     1.32 |     2.14 |      1.48 |    1.48 |
| SL 20%      |     0.3  |     0.32 |     1.14 |      0.48 |    0.48 |
| SL 40%      |    -1.93 |    -1.92 |    -1.09 |     -1.75 |   -1.75 |
| SL 60%      |    -2.33 |    -2.31 |    -1.49 |     -2.15 |   -2.15 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 22-22

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    54.55 |    54.55 |    54.55 |     54.55 |   54.55 |
| SL 20%      |    50    |    50    |    50    |     50    |   50    |
| SL 40%      |    50    |    50    |    50    |     50    |   50    |
| SL 60%      |    50    |    50    |    50    |     50    |   50    |

## Exit 15:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 25-25

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -49256 |   -16937 |    17564 |    -26947 |  -38144 |
| SL 20%      |   -31428 |      891 |    35392 |     -9119 |  -20316 |
| SL 40%      |   -66570 |   -34251 |      249 |    -44262 |  -55458 |
| SL 60%      |   -77962 |   -45643 |   -11143 |    -55654 |  -66850 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 25-25

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -3.65 |    -1.26 |     1.3  |     -2    |   -2.83 |
| SL 20%      |    -2.33 |     0.07 |     2.62 |     -0.68 |   -1.51 |
| SL 40%      |    -4.94 |    -2.54 |     0.02 |     -3.28 |   -4.11 |
| SL 60%      |    -5.78 |    -3.38 |    -0.83 |     -4.13 |   -4.96 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 25-25

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |       44 |       44 |       44 |        40 |      40 |
| SL 20%      |       40 |       40 |       40 |        36 |      36 |
| SL 40%      |       40 |       40 |       40 |        36 |      36 |
| SL 60%      |       40 |       40 |       40 |        36 |      36 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 25-25

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -48533 |   -16214 |    18286 |    -12337 |  -32476 |
| SL 20%      |   -33008 |     -689 |    33812 |      3188 |  -16951 |
| SL 40%      |   -71371 |   -39052 |    -4552 |    -35175 |  -55314 |
| SL 60%      |   -74427 |   -42108 |    -7607 |    -38231 |  -58370 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 25-25

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -3.6  |    -1.2  |     1.36 |     -0.91 |   -2.41 |
| SL 20%      |    -2.45 |    -0.05 |     2.51 |      0.24 |   -1.26 |
| SL 40%      |    -5.29 |    -2.9  |    -0.34 |     -2.61 |   -4.1  |
| SL 60%      |    -5.52 |    -3.12 |    -0.56 |     -2.83 |   -4.33 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 25-25

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |       48 |       48 |       48 |        48 |      48 |
| SL 20%      |       44 |       44 |       44 |        44 |      44 |
| SL 40%      |       44 |       44 |       44 |        44 |      44 |
| SL 60%      |       44 |       44 |       44 |        44 |      44 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 15:00       | SL 20%    | TP 80%    |       25 |        40 |       35392 |      2.62 |            1.26 |         -48071 |

## Top 10 variants by ROI (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 15:00       | SL 20%    | TP 80%    |       25 |     40    |       35392 |      2.62 |            1.26 |         -48071 |
| BPB_LONG   | 15:30       | SL 20%    | TP 80%    |       25 |     44    |       33812 |      2.51 |            1.24 |         -48071 |
| BPB_LONG   | 12:00       | no SL     | TP 80%    |       22 |     54.55 |       25941 |      2.14 |            1.23 |         -42499 |
| BPB_LONG   | 12:00       | no SL     | TP 120%   |       22 |     54.55 |       17916 |      1.48 |            1.16 |         -42499 |
| BPB_LONG   | 12:00       | no SL     | no TP     |       22 |     54.55 |       17916 |      1.48 |            1.16 |         -42499 |
| BPB_LONG   | 15:30       | no SL     | TP 80%    |       25 |     48    |       18286 |      1.36 |            1.11 |         -74419 |
| BPB_LONG   | 12:00       | no SL     | TP 60%    |       22 |     54.55 |       15966 |      1.32 |            1.14 |         -42499 |
| BPB_LONG   | 15:00       | no SL     | TP 80%    |       25 |     44    |       17564 |      1.3  |            1.11 |         -68066 |
| BPB_LONG   | 12:00       | no SL     | TP 40%    |       22 |     54.55 |       15746 |      1.3  |            1.14 |         -42499 |
| BPB_LONG   | 12:00       | SL 20%    | TP 80%    |       22 |     50    |       13850 |      1.14 |            1.12 |         -48071 |

## Top 10 variants by total PnL (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 15:00       | SL 20%    | TP 80%    |       25 |     40    |       35392 |      2.62 |            1.26 |         -48071 |
| BPB_LONG   | 15:30       | SL 20%    | TP 80%    |       25 |     44    |       33812 |      2.51 |            1.24 |         -48071 |
| BPB_LONG   | 12:00       | no SL     | TP 80%    |       22 |     54.55 |       25941 |      2.14 |            1.23 |         -42499 |
| BPB_LONG   | 15:30       | no SL     | TP 80%    |       25 |     48    |       18286 |      1.36 |            1.11 |         -74419 |
| BPB_LONG   | 12:00       | no SL     | TP 120%   |       22 |     54.55 |       17916 |      1.48 |            1.16 |         -42499 |
| BPB_LONG   | 12:00       | no SL     | no TP     |       22 |     54.55 |       17916 |      1.48 |            1.16 |         -42499 |
| BPB_LONG   | 15:00       | no SL     | TP 80%    |       25 |     44    |       17564 |      1.3  |            1.11 |         -68066 |
| BPB_LONG   | 12:00       | no SL     | TP 60%    |       22 |     54.55 |       15966 |      1.32 |            1.14 |         -42499 |
| BPB_LONG   | 12:00       | no SL     | TP 40%    |       22 |     54.55 |       15746 |      1.3  |            1.14 |         -42499 |
| BPB_LONG   | 12:00       | SL 20%    | TP 80%    |       22 |     50    |       13850 |      1.14 |            1.12 |         -48071 |

## Files in this folder

`trades_all_variants.csv.gz` (1940 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (25 trades of the best-PnL variant), `entries.csv` (one row per entry: level, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
