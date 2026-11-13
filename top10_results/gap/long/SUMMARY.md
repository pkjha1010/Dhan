# GAP-FADE-REVERSAL - LONG (ATM call) - SL x TP x time-exit grid

**Status:** PARTIAL - 88 of 117 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2025-11-13 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (10 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

gap up > 1% on day i and day i+1 closes below day i close -> first cross above day i HIGH on day i+2..i+4 -> buy CALL

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:00, 15:30 = 100 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| GAP_LONG   |                   38 |                         23 |                      2 |                        0 |            nan |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 23

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 10-10

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -8105 |    -8105 |    -8105 |     -8105 |   -8105 |
| SL 20%      |    -7520 |    -7520 |    -7520 |     -7520 |   -7520 |
| SL 40%      |    -8105 |    -8105 |    -8105 |     -8105 |   -8105 |
| SL 60%      |    -8105 |    -8105 |    -8105 |     -8105 |   -8105 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 10-10

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -1.54 |    -1.54 |    -1.54 |     -1.54 |   -1.54 |
| SL 20%      |    -1.43 |    -1.43 |    -1.43 |     -1.43 |   -1.43 |
| SL 40%      |    -1.54 |    -1.54 |    -1.54 |     -1.54 |   -1.54 |
| SL 60%      |    -1.54 |    -1.54 |    -1.54 |     -1.54 |   -1.54 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 10-10

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |       40 |       40 |       40 |        40 |      40 |
| SL 20%      |       40 |       40 |       40 |        40 |      40 |
| SL 40%      |       40 |       40 |       40 |        40 |      40 |
| SL 60%      |       40 |       40 |       40 |        40 |      40 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 13-13

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    10712 |    12272 |    24088 |     13504 |   13504 |
| SL 20%      |    15708 |    17267 |    29083 |     18499 |   18499 |
| SL 40%      |    14192 |    15752 |    27568 |     16984 |   16984 |
| SL 60%      |    10712 |    12272 |    24088 |     13504 |   13504 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 13-13

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     1.54 |     1.77 |     3.47 |      1.94 |    1.94 |
| SL 20%      |     2.26 |     2.48 |     4.18 |      2.66 |    2.66 |
| SL 40%      |     2.04 |     2.27 |     3.97 |      2.44 |    2.44 |
| SL 60%      |     1.54 |     1.77 |     3.47 |      1.94 |    1.94 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 13-13

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    53.85 |    53.85 |    53.85 |     53.85 |   53.85 |
| SL 20%      |    46.15 |    46.15 |    46.15 |     46.15 |   46.15 |
| SL 40%      |    53.85 |    53.85 |    53.85 |     53.85 |   53.85 |
| SL 60%      |    53.85 |    53.85 |    53.85 |     53.85 |   53.85 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 16-16

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    38085 |    53797 |    65613 |     89245 |   40049 |
| SL 20%      |    36903 |    52614 |    64430 |     88062 |   38866 |
| SL 40%      |    46365 |    62077 |    73893 |     97525 |   48329 |
| SL 60%      |    35805 |    51517 |    63333 |     86965 |   37769 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 16-16

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     4.5  |     6.35 |     7.75 |     10.54 |    4.73 |
| SL 20%      |     4.36 |     6.21 |     7.61 |     10.4  |    4.59 |
| SL 40%      |     5.48 |     7.33 |     8.73 |     11.52 |    5.71 |
| SL 60%      |     4.23 |     6.08 |     7.48 |     10.27 |    4.46 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 16-16

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    56.25 |    56.25 |    56.25 |     56.25 |   56.25 |
| SL 20%      |    50    |    50    |    50    |     50    |   50    |
| SL 40%      |    56.25 |    56.25 |    56.25 |     56.25 |   56.25 |
| SL 60%      |    56.25 |    56.25 |    56.25 |     56.25 |   56.25 |

## Exit 15:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 21-21

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    26035 |    48799 |    43118 |     66750 |   40514 |
| SL 20%      |    21433 |    35197 |    34766 |     58398 |  -25798 |
| SL 40%      |    36315 |    59079 |    53398 |     77030 |   50794 |
| SL 60%      |    23155 |    45919 |    40238 |     63870 |   37634 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 21-21

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     2.36 |     4.42 |     3.91 |      6.05 |    3.67 |
| SL 20%      |     1.94 |     3.19 |     3.15 |      5.29 |   -2.34 |
| SL 40%      |     3.29 |     5.35 |     4.84 |      6.98 |    4.6  |
| SL 60%      |     2.1  |     4.16 |     3.65 |      5.79 |    3.41 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 21-21

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    47.62 |    47.62 |    47.62 |     47.62 |   47.62 |
| SL 20%      |    42.86 |    42.86 |    42.86 |     42.86 |   38.1  |
| SL 40%      |    47.62 |    47.62 |    47.62 |     47.62 |   47.62 |
| SL 60%      |    47.62 |    47.62 |    47.62 |     47.62 |   47.62 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 21-21

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    27972 |    47193 |    48645 |     72277 |   70681 |
| SL 20%      |    23083 |    33303 |    35037 |     58669 |  -25527 |
| SL 40%      |    49172 |    68393 |    69845 |     93477 |   91881 |
| SL 60%      |    31812 |    51033 |    52485 |     76117 |   74521 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 21-21

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     2.54 |     4.28 |     4.41 |      6.55 |    6.41 |
| SL 20%      |     2.09 |     3.02 |     3.18 |      5.32 |   -2.31 |
| SL 40%      |     4.46 |     6.2  |     6.33 |      8.47 |    8.33 |
| SL 60%      |     2.88 |     4.63 |     4.76 |      6.9  |    6.75 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 21-21

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    47.62 |    42.86 |    42.86 |     42.86 |   42.86 |
| SL 20%      |    42.86 |    38.1  |    38.1  |     38.1  |   33.33 |
| SL 40%      |    47.62 |    42.86 |    42.86 |     42.86 |   42.86 |
| SL 60%      |    47.62 |    42.86 |    42.86 |     42.86 |   42.86 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 12:00       | SL 40%    | TP 120%   |       16 |     56.25 |       97525 |     11.52 |            2.73 |         -29020 |

## Top 10 variants by ROI (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 12:00       | SL 40%    | TP 120%   |       16 |     56.25 |       97525 |     11.52 |            2.73 |         -29020 |
| GAP_LONG   | 12:00       | no SL     | TP 120%   |       16 |     56.25 |       89245 |     10.54 |            2.38 |         -37300 |
| GAP_LONG   | 12:00       | SL 20%    | TP 120%   |       16 |     50    |       88062 |     10.4  |            2.52 |         -31688 |
| GAP_LONG   | 12:00       | SL 60%    | TP 120%   |       16 |     56.25 |       86965 |     10.27 |            2.3  |         -39580 |
| GAP_LONG   | 12:00       | SL 40%    | TP 80%    |       16 |     56.25 |       73893 |      8.73 |            2.31 |         -29020 |
| GAP_LONG   | 15:30       | SL 40%    | TP 120%   |       21 |     42.86 |       93477 |      8.47 |            2.05 |         -28405 |
| GAP_LONG   | 15:30       | SL 40%    | no TP     |       21 |     42.86 |       91881 |      8.33 |            2.03 |         -28405 |
| GAP_LONG   | 12:00       | no SL     | TP 80%    |       16 |     56.25 |       65613 |      7.75 |            2.01 |         -37300 |
| GAP_LONG   | 12:00       | SL 20%    | TP 80%    |       16 |     50    |       64430 |      7.61 |            2.11 |         -31688 |
| GAP_LONG   | 12:00       | SL 60%    | TP 80%    |       16 |     56.25 |       63333 |      7.48 |            1.95 |         -39580 |

## Top 10 variants by total PnL (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 12:00       | SL 40%    | TP 120%   |       16 |     56.25 |       97525 |     11.52 |            2.73 |         -29020 |
| GAP_LONG   | 15:30       | SL 40%    | TP 120%   |       21 |     42.86 |       93477 |      8.47 |            2.05 |         -28405 |
| GAP_LONG   | 15:30       | SL 40%    | no TP     |       21 |     42.86 |       91881 |      8.33 |            2.03 |         -28405 |
| GAP_LONG   | 12:00       | no SL     | TP 120%   |       16 |     56.25 |       89245 |     10.54 |            2.38 |         -37300 |
| GAP_LONG   | 12:00       | SL 20%    | TP 120%   |       16 |     50    |       88062 |     10.4  |            2.52 |         -31688 |
| GAP_LONG   | 12:00       | SL 60%    | TP 120%   |       16 |     56.25 |       86965 |     10.27 |            2.3  |         -39580 |
| GAP_LONG   | 15:00       | SL 40%    | TP 120%   |       21 |     47.62 |       77030 |      6.98 |            1.77 |         -27188 |
| GAP_LONG   | 15:30       | SL 60%    | TP 120%   |       21 |     42.86 |       76117 |      6.9  |            1.72 |         -35205 |
| GAP_LONG   | 15:30       | SL 60%    | no TP     |       21 |     42.86 |       74521 |      6.75 |            1.7  |         -35205 |
| GAP_LONG   | 12:00       | SL 40%    | TP 80%    |       16 |     56.25 |       73893 |      8.73 |            2.31 |         -29020 |

## Files in this folder

`trades_all_variants.csv.gz` (1620 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (16 trades of the best-PnL variant), `entries.csv` (one row per entry: level, gap %, entry-day offset, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
