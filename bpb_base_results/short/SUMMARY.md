# BPB BASE - SHORT (ATM put) - SL x TP x time-exit grid, entry checked all day

**Status:** PARTIAL - 5234 of 8878 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

BPB base SHORT: close below the 10-day low, no later close above it (pullback) -> first 1-minute cross below the lowest Low since the breakdown (full day) -> buy PUT

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 60%, TP 80%, TP 100%, TP 120%, no TP x time exit 15:00, 15:30 = 40 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                                                        |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| BPB_SHORT  |                 2404 |                        763 |                     58 |                      148 | Dhan returned no option candles for this period = 132; no ATM / ITM-1..ITM-3 candle at the entry minute = 14; no option candles after the entry = 2 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 731, 1: 21, 2: 9, 3: 2

## Exit 15:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 675-675

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |  1987022 |  2683031 |   2811013 |   2567418 | 2970532 |
| SL 20%      |  1008821 |  1141973 |   1253881 |   1193559 |  602628 |
| SL 40%      |  1381364 |  1568428 |   1831627 |   1837466 | 1178743 |
| SL 60%      |  1669627 |  2021109 |   2069620 |   1986340 | 2355822 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 675-675

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |     5.53 |     7.47 |      7.83 |      7.15 |    8.27 |
| SL 20%      |     2.81 |     3.18 |      3.49 |      3.32 |    1.68 |
| SL 40%      |     3.85 |     4.37 |      5.1  |      5.12 |    3.28 |
| SL 60%      |     4.65 |     5.63 |      5.76 |      5.53 |    6.56 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 675-675

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    48    |    47.41 |     46.81 |     46.22 |   45.33 |
| SL 20%      |    39.7  |    38.52 |     37.78 |     37.48 |   36.59 |
| SL 40%      |    45.78 |    44.74 |     44.15 |     43.85 |   42.96 |
| SL 60%      |    47.41 |    46.52 |     45.78 |     45.33 |   44.44 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 699-699

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |  3529158 |  4240204 |   4280055 |   4131955 | 3292636 |
| SL 20%      |  2582310 |  2708186 |   2739351 |   2752096 | 2536541 |
| SL 40%      |  2946346 |  3130231 |   3322299 |   3425729 | 2889440 |
| SL 60%      |  3172113 |  3528472 |   3524552 |   3554955 | 2870051 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 699-699

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |     9.48 |    11.39 |     11.5  |     11.1  |    8.84 |
| SL 20%      |     6.94 |     7.27 |      7.36 |      7.39 |    6.81 |
| SL 40%      |     7.91 |     8.41 |      8.92 |      9.2  |    7.76 |
| SL 60%      |     8.52 |     9.48 |      9.47 |      9.55 |    7.71 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 699-699

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    48.21 |    47.5  |     46.49 |     45.78 |   44.49 |
| SL 20%      |    40.2  |    38.91 |     37.91 |     37.48 |   36.62 |
| SL 40%      |    46.21 |    45.06 |     44.35 |     43.92 |   42.92 |
| SL 60%      |    47.5  |    46.49 |     45.49 |     44.92 |   43.78 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT  | 15:30       | no SL     | TP 100%   |      699 |     46.49 |     4280055 |      11.5 |            1.92 |        -360884 |

## Top 10 variants by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT  | 15:30       | no SL     | TP 100%   |      699 |     46.49 |     4280055 |     11.5  |            1.92 |        -360884 |
| BPB_SHORT  | 15:30       | no SL     | TP 80%    |      699 |     47.5  |     4240204 |     11.39 |            1.95 |        -401223 |
| BPB_SHORT  | 15:30       | no SL     | TP 120%   |      699 |     45.78 |     4131955 |     11.1  |            1.86 |        -349151 |
| BPB_SHORT  | 15:30       | SL 60%    | TP 120%   |      699 |     44.92 |     3554955 |      9.55 |            1.71 |        -344003 |
| BPB_SHORT  | 15:30       | no SL     | TP 60%    |      699 |     48.21 |     3529158 |      9.48 |            1.8  |        -403587 |
| BPB_SHORT  | 15:30       | SL 60%    | TP 80%    |      699 |     46.49 |     3528472 |      9.48 |            1.75 |        -396076 |
| BPB_SHORT  | 15:30       | SL 60%    | TP 100%   |      699 |     45.49 |     3524552 |      9.47 |            1.72 |        -355737 |
| BPB_SHORT  | 15:30       | SL 40%    | TP 120%   |      699 |     43.92 |     3425729 |      9.2  |            1.71 |        -356172 |
| BPB_SHORT  | 15:30       | SL 40%    | TP 100%   |      699 |     44.35 |     3322299 |      8.92 |            1.7  |        -356172 |
| BPB_SHORT  | 15:30       | no SL     | no TP     |      699 |     44.49 |     3292636 |      8.84 |            1.65 |        -628310 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT  | 15:30       | no SL     | TP 100%   |      699 |     46.49 |     4280055 |     11.5  |            1.92 |        -360884 |
| BPB_SHORT  | 15:30       | no SL     | TP 80%    |      699 |     47.5  |     4240204 |     11.39 |            1.95 |        -401223 |
| BPB_SHORT  | 15:30       | no SL     | TP 120%   |      699 |     45.78 |     4131955 |     11.1  |            1.86 |        -349151 |
| BPB_SHORT  | 15:30       | SL 60%    | TP 120%   |      699 |     44.92 |     3554955 |      9.55 |            1.71 |        -344003 |
| BPB_SHORT  | 15:30       | no SL     | TP 60%    |      699 |     48.21 |     3529158 |      9.48 |            1.8  |        -403587 |
| BPB_SHORT  | 15:30       | SL 60%    | TP 80%    |      699 |     46.49 |     3528472 |      9.48 |            1.75 |        -396076 |
| BPB_SHORT  | 15:30       | SL 60%    | TP 100%   |      699 |     45.49 |     3524552 |      9.47 |            1.72 |        -355737 |
| BPB_SHORT  | 15:30       | SL 40%    | TP 120%   |      699 |     43.92 |     3425729 |      9.2  |            1.71 |        -356172 |
| BPB_SHORT  | 15:30       | SL 40%    | TP 100%   |      699 |     44.35 |     3322299 |      8.92 |            1.7  |        -356172 |
| BPB_SHORT  | 15:30       | no SL     | no TP     |      699 |     44.49 |     3292636 |      8.84 |            1.65 |        -628310 |

## Files in this folder

`trades_all_variants.csv.gz` (27480 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (699 trades of the best-PnL variant), `entries.csv` (one row per entry: level, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
