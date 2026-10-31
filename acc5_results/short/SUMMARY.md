# 5-DAY ACCUMULATION fake-break - SHORT (ATM put) - SL x TP x time-exit grid

**Status:** PARTIAL - 4536 of 6295 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

close above the 5-day high (breakout) -> within 3 days price crosses back below the 5-day low -> buy PUT

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 20%, TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:30 = 96 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:------------------------------------------------------------------------------------------------------------|
| ACC5_SHORT |                 1799 |                         37 |                      5 |                      897 | Dhan returned no option candles for this period = 894; no ATM / ITM-1..ITM-3 candle at the entry minute = 3 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 36, 1: 1

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 12-12

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   245952 |   210906 |   198541 |   240876 |    184371 |   -4974 |
| SL 20%      |   154299 |    89397 |    80447 |    99847 |     99847 |  -89498 |
| SL 40%      |   211797 |   165366 |   141616 |   172566 |    103266 |  -94656 |
| SL 60%      |   200412 |   153981 |   130231 |   161181 |    117291 |  -72054 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 12-12

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    36.24 |    31.07 |    29.25 |    35.49 |     27.16 |   -0.73 |
| SL 20%      |    22.73 |    13.17 |    11.85 |    14.71 |     14.71 |  -13.19 |
| SL 40%      |    31.2  |    24.36 |    20.86 |    25.42 |     15.21 |  -13.95 |
| SL 60%      |    29.53 |    22.69 |    19.19 |    23.75 |     17.28 |  -10.62 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 12-12

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    83.33 |    66.67 |    66.67 |    66.67 |     66.67 |   50    |
| SL 20%      |    58.33 |    41.67 |    41.67 |    41.67 |     41.67 |   25    |
| SL 40%      |    75    |    58.33 |    58.33 |    58.33 |     50    |   33.33 |
| SL 60%      |    75    |    58.33 |    58.33 |    58.33 |     58.33 |   41.67 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 13-13

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   418254 |   350130 |   204919 |   176454 |    209579 |  -92111 |
| SL 20%      |   265652 |   210321 |   103674 |   123074 |    155374 |  -80931 |
| SL 40%      |   310637 |   254959 |    93563 |   124513 |     87513 | -172249 |
| SL 60%      |   372714 |   302977 |   125298 |    85448 |     95803 | -169677 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 13-13

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    56.71 |    47.48 |    27.79 |    23.93 |     28.42 |  -12.49 |
| SL 20%      |    36.02 |    28.52 |    14.06 |    16.69 |     21.07 |  -10.97 |
| SL 40%      |    42.12 |    34.57 |    12.69 |    16.88 |     11.87 |  -23.36 |
| SL 60%      |    50.54 |    41.08 |    16.99 |    11.59 |     12.99 |  -23.01 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 13-13

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    92.31 |    76.92 |    53.85 |    46.15 |     46.15 |   30.77 |
| SL 20%      |    61.54 |    46.15 |    30.77 |    30.77 |     30.77 |   15.38 |
| SL 40%      |    76.92 |    61.54 |    38.46 |    38.46 |     30.77 |   15.38 |
| SL 60%      |    84.62 |    69.23 |    46.15 |    38.46 |     38.46 |   23.08 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 23-23

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   511309 |  1131714 |  1040186 |  1118938 |   1130673 |  548751 |
| SL 20%      |   301776 |   202577 |   119188 |   152291 |    207901 |     886 |
| SL 40%      |   313056 |   202261 |    64122 |   108775 |     95085 | -135387 |
| SL 60%      |   379362 |   439983 |   274311 |   244564 |    189849 |  247048 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 23-23

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    38.63 |    85.5  |    78.59 |    84.54 |     85.43 |   41.46 |
| SL 20%      |    22.8  |    15.31 |     9.01 |    11.51 |     15.71 |    0.07 |
| SL 40%      |    23.65 |    15.28 |     4.84 |     8.22 |      7.18 |  -10.23 |
| SL 60%      |    28.66 |    33.24 |    20.72 |    18.48 |     14.34 |   18.67 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 23-23

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    82.61 |    78.26 |    69.57 |    69.57 |     65.22 |   52.17 |
| SL 20%      |    56.52 |    39.13 |    30.43 |    30.43 |     30.43 |   21.74 |
| SL 40%      |    65.22 |    47.83 |    34.78 |    34.78 |     30.43 |   21.74 |
| SL 60%      |    73.91 |    65.22 |    52.17 |    47.83 |     43.48 |   39.13 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 32-32

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   734406 |  1286924 |  1248218 |  1388693 |   1579248 | 4668862 |
| SL 20%      |   494353 |   382965 |   258175 |   254532 |    526136 | 3974370 |
| SL 40%      |   458909 |   322659 |   143118 |   151025 |    353329 | 3766458 |
| SL 60%      |   565289 |   545625 |   369748 |   217199 |    341224 | 3667099 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 32-32

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    39.58 |    69.37 |    67.28 |    74.85 |     85.12 |  251.65 |
| SL 20%      |    26.65 |    20.64 |    13.92 |    13.72 |     28.36 |  214.22 |
| SL 40%      |    24.74 |    17.39 |     7.71 |     8.14 |     19.04 |  203.01 |
| SL 60%      |    30.47 |    29.41 |    19.93 |    11.71 |     18.39 |  197.66 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 32-32

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    87.5  |    78.12 |    71.88 |    71.88 |     62.5  |   40.62 |
| SL 20%      |    56.25 |    40.62 |    31.25 |    28.12 |     28.12 |   12.5  |
| SL 40%      |    62.5  |    46.88 |    34.38 |    31.25 |     28.12 |   12.5  |
| SL 60%      |    75    |    62.5  |    50    |    40.62 |     34.38 |   15.62 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_SHORT | 15:30       | no SL     | no TP     |       32 |     40.62 |     4668862 |    251.65 |            6.04 |        -340934 |

## Top 10 variants by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_SHORT | 15:30       | no SL     | no TP     |       32 |     40.62 |     4668862 |    251.65 |            6.04 |        -340934 |
| ACC5_SHORT | 15:30       | SL 20%    | no TP     |       32 |     12.5  |     3974370 |    214.22 |            8.16 |        -248464 |
| ACC5_SHORT | 15:30       | SL 40%    | no TP     |       32 |     12.5  |     3766458 |    203.01 |            5.94 |        -349453 |
| ACC5_SHORT | 15:30       | SL 60%    | no TP     |       32 |     15.62 |     3667099 |    197.66 |            4.63 |        -496493 |
| ACC5_SHORT | 15:30       | no SL     | TP 120%   |       32 |     62.5  |     1579248 |     85.12 |            3.59 |        -172519 |
| ACC5_SHORT | 15:30       | no SL     | TP 80%    |       32 |     71.88 |     1388693 |     74.85 |            4.06 |        -172519 |
| ACC5_SHORT | 15:30       | no SL     | TP 40%    |       32 |     78.12 |     1286924 |     69.37 |            4.8  |        -111342 |
| ACC5_SHORT | 15:30       | no SL     | TP 60%    |       32 |     71.88 |     1248218 |     67.28 |            3.75 |        -172519 |
| ACC5_SHORT | 15:30       | no SL     | TP 20%    |       32 |     87.5  |      734406 |     39.58 |            4.76 |         -79028 |
| ACC5_SHORT | 15:30       | SL 60%    | TP 20%    |       32 |     75    |      565289 |     30.47 |            2.96 |        -114610 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_SHORT | 15:30       | no SL     | no TP     |       32 |     40.62 |     4668862 |    251.65 |            6.04 |        -340934 |
| ACC5_SHORT | 15:30       | SL 20%    | no TP     |       32 |     12.5  |     3974370 |    214.22 |            8.16 |        -248464 |
| ACC5_SHORT | 15:30       | SL 40%    | no TP     |       32 |     12.5  |     3766458 |    203.01 |            5.94 |        -349453 |
| ACC5_SHORT | 15:30       | SL 60%    | no TP     |       32 |     15.62 |     3667099 |    197.66 |            4.63 |        -496493 |
| ACC5_SHORT | 15:30       | no SL     | TP 120%   |       32 |     62.5  |     1579248 |     85.12 |            3.59 |        -172519 |
| ACC5_SHORT | 15:30       | no SL     | TP 80%    |       32 |     71.88 |     1388693 |     74.85 |            4.06 |        -172519 |
| ACC5_SHORT | 15:30       | no SL     | TP 40%    |       32 |     78.12 |     1286924 |     69.37 |            4.8  |        -111342 |
| ACC5_SHORT | 15:30       | no SL     | TP 60%    |       32 |     71.88 |     1248218 |     67.28 |            3.75 |        -172519 |
| ACC5_SHORT | 15:30       | no SL     | TP 20%    |       32 |     87.5  |      734406 |     39.58 |            4.76 |         -79028 |
| ACC5_SHORT | 15:30       | SL 60%    | TP 20%    |       32 |     75    |      565289 |     30.47 |            2.96 |        -114610 |

## Files in this folder

`trades_all_variants.csv.gz` (1920 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (32 trades of the best-PnL variant), `entries.csv` (one row per entry: level, Acc high / low, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
