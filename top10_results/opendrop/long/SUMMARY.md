# OPEN-DROP RETEST - LONG (ATM call) - SL x TP x time-exit grid

**Status:** PARTIAL - 58 of 59 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2025-11-13 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (10 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

first hourly candle falls > 1% (red) on day i -> a day i+1..i+3 trades <= 1% below its close -> first cross above that close on the next 1..5 days (1-minute) -> buy CALL; NIFTY50 hourly slope >= -0.5 on day i

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:00, 15:30 = 100 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy      |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:--------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| OPENDROP_LONG |                   34 |                         33 |                      4 |                        0 |            nan |

## Strike used

strike_offset 0 = ATM, -n = ITM-n (the ATM series had no candle at the entry minute): 0: 33

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 19-19

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -37400 |   -37400 |   -37400 |    -37400 |  -37400 |
| SL 20%      |   -26913 |   -26913 |   -26913 |    -26913 |  -26913 |
| SL 40%      |   -37400 |   -37400 |   -37400 |    -37400 |  -37400 |
| SL 60%      |   -37400 |   -37400 |   -37400 |    -37400 |  -37400 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 19-19

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -3.64 |    -3.64 |    -3.64 |     -3.64 |   -3.64 |
| SL 20%      |    -2.62 |    -2.62 |    -2.62 |     -2.62 |   -2.62 |
| SL 40%      |    -3.64 |    -3.64 |    -3.64 |     -3.64 |   -3.64 |
| SL 60%      |    -3.64 |    -3.64 |    -3.64 |     -3.64 |   -3.64 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 19-19

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    42.11 |    42.11 |    42.11 |     42.11 |   42.11 |
| SL 20%      |    42.11 |    42.11 |    42.11 |     42.11 |   42.11 |
| SL 40%      |    42.11 |    42.11 |    42.11 |     42.11 |   42.11 |
| SL 60%      |    42.11 |    42.11 |    42.11 |     42.11 |   42.11 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 22-22

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -36922 |   -36922 |   -36922 |    -36922 |  -36922 |
| SL 20%      |   -44925 |   -44925 |   -44925 |    -44925 |  -44925 |
| SL 40%      |   -36922 |   -36922 |   -36922 |    -36922 |  -36922 |
| SL 60%      |   -36922 |   -36922 |   -36922 |    -36922 |  -36922 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 22-22

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -3.11 |    -3.11 |    -3.11 |     -3.11 |   -3.11 |
| SL 20%      |    -3.79 |    -3.79 |    -3.79 |     -3.79 |   -3.79 |
| SL 40%      |    -3.11 |    -3.11 |    -3.11 |     -3.11 |   -3.11 |
| SL 60%      |    -3.11 |    -3.11 |    -3.11 |     -3.11 |   -3.11 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 22-22

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    45.45 |    45.45 |    45.45 |     45.45 |   45.45 |
| SL 20%      |    40.91 |    40.91 |    40.91 |     40.91 |   40.91 |
| SL 40%      |    45.45 |    45.45 |    45.45 |     45.45 |   45.45 |
| SL 60%      |    45.45 |    45.45 |    45.45 |     45.45 |   45.45 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 26-26

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -15405 |   -31666 |   -31666 |    -31666 |  -31666 |
| SL 20%      |   -13787 |   -13787 |   -13787 |    -13787 |  -13787 |
| SL 40%      |    -6229 |   -22490 |   -22490 |    -22490 |  -22490 |
| SL 60%      |   -15405 |   -31666 |   -31666 |    -31666 |  -31666 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 26-26

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -1.1  |    -2.27 |    -2.27 |     -2.27 |   -2.27 |
| SL 20%      |    -0.99 |    -0.99 |    -0.99 |     -0.99 |   -0.99 |
| SL 40%      |    -0.45 |    -1.61 |    -1.61 |     -1.61 |   -1.61 |
| SL 60%      |    -1.1  |    -2.27 |    -2.27 |     -2.27 |   -2.27 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 26-26

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    53.85 |    53.85 |    53.85 |     53.85 |   53.85 |
| SL 20%      |    50    |    50    |    50    |     50    |   50    |
| SL 40%      |    53.85 |    53.85 |    53.85 |     53.85 |   53.85 |
| SL 60%      |    53.85 |    53.85 |    53.85 |     53.85 |   53.85 |

## Exit 15:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 29-29

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -33864 |   -71767 |   -55200 |    -63720 |  -63720 |
| SL 20%      |    -1129 |    19349 |    35916 |     27396 |   27396 |
| SL 40%      |   -11357 |   -36968 |   -20401 |    -28921 |  -28921 |
| SL 60%      |   -33261 |   -70394 |   -53827 |    -62347 |  -62347 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 29-29

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -2.17 |    -4.6  |    -3.54 |     -4.09 |   -4.09 |
| SL 20%      |    -0.07 |     1.24 |     2.3  |      1.76 |    1.76 |
| SL 40%      |    -0.73 |    -2.37 |    -1.31 |     -1.85 |   -1.85 |
| SL 60%      |    -2.13 |    -4.51 |    -3.45 |     -4    |   -4    |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 29-29

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    51.72 |    48.28 |    48.28 |     48.28 |   48.28 |
| SL 20%      |    48.28 |    48.28 |    48.28 |     48.28 |   48.28 |
| SL 40%      |    51.72 |    48.28 |    48.28 |     48.28 |   48.28 |
| SL 60%      |    51.72 |    48.28 |    48.28 |     48.28 |   48.28 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 29-29

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -17793 |   -42661 |   -21294 |    -35551 |  -35551 |
| SL 20%      |    14199 |    44876 |    66244 |     51986 |   51986 |
| SL 40%      |     4189 |   -11222 |    10146 |     -4112 |   -4112 |
| SL 60%      |   -17793 |   -44727 |   -23359 |    -37617 |  -37617 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 29-29

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -1.14 |    -2.74 |    -1.37 |     -2.28 |   -2.28 |
| SL 20%      |     0.91 |     2.88 |     4.25 |      3.33 |    3.33 |
| SL 40%      |     0.27 |    -0.72 |     0.65 |     -0.26 |   -0.26 |
| SL 60%      |    -1.14 |    -2.87 |    -1.5  |     -2.41 |   -2.41 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 29-29

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    48.28 |    44.83 |    44.83 |     44.83 |   44.83 |
| SL 20%      |    44.83 |    44.83 |    44.83 |     44.83 |   44.83 |
| SL 40%      |    48.28 |    44.83 |    44.83 |     44.83 |   44.83 |
| SL 60%      |    48.28 |    44.83 |    44.83 |     44.83 |   44.83 |

## Best variant by total PnL

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 15:30       | SL 20%    | TP 80%    |       29 |     44.83 |       66244 |      4.25 |            1.47 |         -55973 |

## Top 10 variants by ROI (at least 10 trades)

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 15:30       | SL 20%    | TP 80%    |       29 |     44.83 |       66244 |      4.25 |            1.47 |         -55973 |
| OPENDROP_LONG | 15:30       | SL 20%    | no TP     |       29 |     44.83 |       51986 |      3.33 |            1.37 |         -55973 |
| OPENDROP_LONG | 15:30       | SL 20%    | TP 120%   |       29 |     44.83 |       51986 |      3.33 |            1.37 |         -55973 |
| OPENDROP_LONG | 15:30       | SL 20%    | TP 60%    |       29 |     44.83 |       44876 |      2.88 |            1.32 |         -55973 |
| OPENDROP_LONG | 15:00       | SL 20%    | TP 80%    |       29 |     48.28 |       35916 |      2.3  |            1.25 |         -57468 |
| OPENDROP_LONG | 15:00       | SL 20%    | no TP     |       29 |     48.28 |       27396 |      1.76 |            1.19 |         -57468 |
| OPENDROP_LONG | 15:00       | SL 20%    | TP 120%   |       29 |     48.28 |       27396 |      1.76 |            1.19 |         -57468 |
| OPENDROP_LONG | 15:00       | SL 20%    | TP 60%    |       29 |     48.28 |       19349 |      1.24 |            1.13 |         -57468 |
| OPENDROP_LONG | 15:30       | SL 20%    | TP 40%    |       29 |     44.83 |       14199 |      0.91 |            1.1  |         -55973 |
| OPENDROP_LONG | 15:30       | SL 40%    | TP 80%    |       29 |     44.83 |       10146 |      0.65 |            1.05 |         -89688 |

## Top 10 variants by total PnL (at least 10 trades)

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 15:30       | SL 20%    | TP 80%    |       29 |     44.83 |       66244 |      4.25 |            1.47 |         -55973 |
| OPENDROP_LONG | 15:30       | SL 20%    | no TP     |       29 |     44.83 |       51986 |      3.33 |            1.37 |         -55973 |
| OPENDROP_LONG | 15:30       | SL 20%    | TP 120%   |       29 |     44.83 |       51986 |      3.33 |            1.37 |         -55973 |
| OPENDROP_LONG | 15:30       | SL 20%    | TP 60%    |       29 |     44.83 |       44876 |      2.88 |            1.32 |         -55973 |
| OPENDROP_LONG | 15:00       | SL 20%    | TP 80%    |       29 |     48.28 |       35916 |      2.3  |            1.25 |         -57468 |
| OPENDROP_LONG | 15:00       | SL 20%    | no TP     |       29 |     48.28 |       27396 |      1.76 |            1.19 |         -57468 |
| OPENDROP_LONG | 15:00       | SL 20%    | TP 120%   |       29 |     48.28 |       27396 |      1.76 |            1.19 |         -57468 |
| OPENDROP_LONG | 15:00       | SL 20%    | TP 60%    |       29 |     48.28 |       19349 |      1.24 |            1.13 |         -57468 |
| OPENDROP_LONG | 15:30       | SL 20%    | TP 40%    |       29 |     44.83 |       14199 |      0.91 |            1.1  |         -55973 |
| OPENDROP_LONG | 15:30       | SL 40%    | TP 80%    |       29 |     44.83 |       10146 |      0.65 |            1.05 |         -89688 |

## Files in this folder

`trades_all_variants.csv.gz` (2500 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (29 trades of the best-PnL variant), `entries.csv` (one row per entry: level, setup / drop day, first-candle drop %, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for the whole year. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
