# GAP-FADE-REVERSAL - SHORT (ATM put) - SL x TP x time-exit grid

**Status:** PARTIAL - 88 of 117 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2025-11-13 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (10 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

gap down > 1% on day i and day i+1 closes above day i close -> first cross below day i LOW on day i+2..i+4 -> buy PUT

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:00, 15:30 = 100 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| GAP_SHORT  |                   46 |                         32 |                      3 |                        0 |            nan |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 32

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 16-16

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    50611 |    79191 |    44941 |     30661 |   30661 |
| SL 20%      |    23131 |    43711 |    43711 |     29431 |   29431 |
| SL 40%      |    52113 |    80693 |    46443 |     32163 |   32163 |
| SL 60%      |    50611 |    79191 |    44941 |     30661 |   30661 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 16-16

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     5.82 |     9.1  |     5.17 |      3.52 |    3.52 |
| SL 20%      |     2.66 |     5.02 |     5.02 |      3.38 |    3.38 |
| SL 40%      |     5.99 |     9.27 |     5.34 |      3.7  |    3.7  |
| SL 60%      |     5.82 |     9.1  |     5.17 |      3.52 |    3.52 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 16-16

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    50    |    50    |    50    |     50    |   50    |
| SL 20%      |    43.75 |    43.75 |    43.75 |     43.75 |   43.75 |
| SL 40%      |    50    |    50    |    50    |     50    |   50    |
| SL 60%      |    50    |    50    |    50    |     50    |   50    |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 18-18

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    39944 |    86599 |    16280 |    -19840 |  -19840 |
| SL 20%      |     2751 |    41406 |    40337 |      4217 |    4217 |
| SL 40%      |    19768 |    66423 |     1104 |    -35016 |  -35016 |
| SL 60%      |    13424 |    60079 |   -10740 |    -46860 |  -46860 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 18-18

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     4.1  |     8.88 |     1.67 |     -2.04 |   -2.04 |
| SL 20%      |     0.28 |     4.25 |     4.14 |      0.43 |    0.43 |
| SL 40%      |     2.03 |     6.81 |     0.11 |     -3.59 |   -3.59 |
| SL 60%      |     1.38 |     6.16 |    -1.1  |     -4.81 |   -4.81 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 18-18

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    50    |    50    |    44.44 |     44.44 |   44.44 |
| SL 20%      |    44.44 |    44.44 |    44.44 |     44.44 |   44.44 |
| SL 40%      |    50    |    50    |    44.44 |     44.44 |   44.44 |
| SL 60%      |    50    |    50    |    44.44 |     44.44 |   44.44 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 22-22

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    16750 |    54310 |    56224 |    -23391 |  -23391 |
| SL 20%      |   -32506 |    12264 |    -2823 |    -33063 |  -33063 |
| SL 40%      |    19064 |    56624 |   -22712 |    -52952 |  -52952 |
| SL 60%      |     2190 |    39750 |   -45086 |    -75326 |  -75326 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 22-22

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     1.4  |     4.53 |     4.69 |     -1.95 |   -1.95 |
| SL 20%      |    -2.71 |     1.02 |    -0.24 |     -2.76 |   -2.76 |
| SL 40%      |     1.59 |     4.72 |    -1.89 |     -4.42 |   -4.42 |
| SL 60%      |     0.18 |     3.32 |    -3.76 |     -6.28 |   -6.28 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 22-22

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    36.36 |    36.36 |    36.36 |     36.36 |   36.36 |
| SL 20%      |    27.27 |    27.27 |    27.27 |     27.27 |   27.27 |
| SL 40%      |    36.36 |    36.36 |    31.82 |     31.82 |   31.82 |
| SL 60%      |    36.36 |    36.36 |    31.82 |     31.82 |   31.82 |

## Exit 15:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 28-28

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   115945 |   147992 |   139350 |     75735 |   75735 |
| SL 20%      |   -44444 |    -2799 |   -28442 |    -37682 |  -37682 |
| SL 40%      |    -2809 |    37476 |   -52416 |    -61656 |  -61656 |
| SL 60%      |   -17391 |    22894 |   -72499 |    -81739 |  -81739 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 28-28

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     7.58 |     9.67 |     9.11 |      4.95 |    4.95 |
| SL 20%      |    -2.9  |    -0.18 |    -1.86 |     -2.46 |   -2.46 |
| SL 40%      |    -0.18 |     2.45 |    -3.43 |     -4.03 |   -4.03 |
| SL 60%      |    -1.14 |     1.5  |    -4.74 |     -5.34 |   -5.34 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 28-28

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    53.57 |    53.57 |    53.57 |     50    |   50    |
| SL 20%      |    35.71 |    35.71 |    35.71 |     35.71 |   35.71 |
| SL 40%      |    46.43 |    46.43 |    42.86 |     42.86 |   42.86 |
| SL 60%      |    46.43 |    46.43 |    42.86 |     42.86 |   42.86 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 29-29

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   120907 |   167480 |   154022 |      7210 |  -45710 |
| SL 20%      |   -45751 |    -4231 |   -13275 |     12813 |  -40107 |
| SL 40%      |     5079 |    35879 |   -37415 |    -11327 |  -64247 |
| SL 60%      |   -12429 |    18371 |   -60422 |    -34335 |  -87255 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 29-29

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     7.62 |    10.55 |     9.7  |      0.45 |   -2.88 |
| SL 20%      |    -2.88 |    -0.27 |    -0.84 |      0.81 |   -2.53 |
| SL 40%      |     0.32 |     2.26 |    -2.36 |     -0.71 |   -4.05 |
| SL 60%      |    -0.78 |     1.16 |    -3.81 |     -2.16 |   -5.5  |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 29-29

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    55.17 |    55.17 |    55.17 |     48.28 |   48.28 |
| SL 20%      |    37.93 |    37.93 |    37.93 |     37.93 |   37.93 |
| SL 40%      |    48.28 |    48.28 |    44.83 |     44.83 |   44.83 |
| SL 60%      |    48.28 |    48.28 |    44.83 |     44.83 |   44.83 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT  | 15:30       | no SL     | TP 60%    |       29 |     55.17 |      167480 |     10.55 |            2.29 |         -60761 |

## Top 10 variants by ROI (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT  | 15:30       | no SL     | TP 60%    |       29 |     55.17 |      167480 |     10.55 |            2.29 |         -60761 |
| GAP_SHORT  | 15:30       | no SL     | TP 80%    |       29 |     55.17 |      154022 |      9.7  |            2.18 |         -60761 |
| GAP_SHORT  | 15:00       | no SL     | TP 60%    |       28 |     53.57 |      147992 |      9.67 |            2.3  |         -69865 |
| GAP_SHORT  | 09:30       | SL 40%    | TP 60%    |       16 |     50    |       80693 |      9.27 |            2.24 |         -25384 |
| GAP_SHORT  | 15:00       | no SL     | TP 80%    |       28 |     53.57 |      139350 |      9.11 |            2.23 |         -69865 |
| GAP_SHORT  | 09:30       | SL 60%    | TP 60%    |       16 |     50    |       79191 |      9.1  |            2.19 |         -26885 |
| GAP_SHORT  | 09:30       | no SL     | TP 60%    |       16 |     50    |       79191 |      9.1  |            2.19 |         -26885 |
| GAP_SHORT  | 10:00       | no SL     | TP 60%    |       18 |     50    |       86599 |      8.88 |            2.13 |         -40238 |
| GAP_SHORT  | 15:30       | no SL     | TP 40%    |       29 |     55.17 |      120907 |      7.62 |            1.93 |         -60761 |
| GAP_SHORT  | 15:00       | no SL     | TP 40%    |       28 |     53.57 |      115945 |      7.58 |            2.02 |         -69865 |

## Top 10 variants by total PnL (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT  | 15:30       | no SL     | TP 60%    |       29 |     55.17 |      167480 |     10.55 |            2.29 |         -60761 |
| GAP_SHORT  | 15:30       | no SL     | TP 80%    |       29 |     55.17 |      154022 |      9.7  |            2.18 |         -60761 |
| GAP_SHORT  | 15:00       | no SL     | TP 60%    |       28 |     53.57 |      147992 |      9.67 |            2.3  |         -69865 |
| GAP_SHORT  | 15:00       | no SL     | TP 80%    |       28 |     53.57 |      139350 |      9.11 |            2.23 |         -69865 |
| GAP_SHORT  | 15:30       | no SL     | TP 40%    |       29 |     55.17 |      120907 |      7.62 |            1.93 |         -60761 |
| GAP_SHORT  | 15:00       | no SL     | TP 40%    |       28 |     53.57 |      115945 |      7.58 |            2.02 |         -69865 |
| GAP_SHORT  | 10:00       | no SL     | TP 60%    |       18 |     50    |       86599 |      8.88 |            2.13 |         -40238 |
| GAP_SHORT  | 09:30       | SL 40%    | TP 60%    |       16 |     50    |       80693 |      9.27 |            2.24 |         -25384 |
| GAP_SHORT  | 09:30       | SL 60%    | TP 60%    |       16 |     50    |       79191 |      9.1  |            2.19 |         -26885 |
| GAP_SHORT  | 09:30       | no SL     | TP 60%    |       16 |     50    |       79191 |      9.1  |            2.19 |         -26885 |

## Files in this folder

`trades_all_variants.csv.gz` (2260 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (29 trades of the best-PnL variant), `entries.csv` (one row per entry: level, gap %, entry-day offset, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
