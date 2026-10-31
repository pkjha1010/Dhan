# 5-DAY ACCUMULATION fake-break - LONG (ATM call) - SL x TP x time-exit grid

**Status:** PARTIAL - 4536 of 6295 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

close below the 5-day low (breakdown) -> within 3 days price crosses back above the 5-day high -> buy CALL

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 20%, TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:30 = 96 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                 |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-------------------------------------------------------------------------------------------------------------|
| ACC5_LONG  |                 2194 |                         18 |                      2 |                     1171 | Dhan returned no option candles for this period = 1163; no ATM / ITM-1..ITM-3 candle at the entry minute = 8 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): -2: 1, 0: 17

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 8-8

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -57462 |   -55033 |   -43273 |   -31513 |     -7993 |  -35953 |
| SL 20%      |   -36838 |   -19921 |    -8161 |     3599 |     27119 |    -841 |
| SL 40%      |   -51226 |   -48798 |   -37038 |   -25278 |     -1758 |  -29718 |
| SL 60%      |   -63076 |   -60648 |   -48888 |   -37128 |    -13608 |  -41568 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 8-8

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -12.59 |   -12.06 |    -9.48 |    -6.91 |     -1.75 |   -7.88 |
| SL 20%      |    -8.07 |    -4.37 |    -1.79 |     0.79 |      5.94 |   -0.18 |
| SL 40%      |   -11.23 |   -10.69 |    -8.12 |    -5.54 |     -0.39 |   -6.51 |
| SL 60%      |   -13.82 |   -13.29 |   -10.71 |    -8.14 |     -2.98 |   -9.11 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 8-8

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     37.5 |       25 |       25 |       25 |        25 |      25 |
| SL 20%      |     25   |       25 |       25 |       25 |        25 |      25 |
| SL 40%      |     37.5 |       25 |       25 |       25 |        25 |      25 |
| SL 60%      |     37.5 |       25 |       25 |       25 |        25 |      25 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 10-10

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -78643 |   -40759 |   -29822 |     3110 |     18271 |  -61289 |
| SL 20%      |   -23392 |    42516 |    53453 |    86385 |    101546 |    8786 |
| SL 40%      |   -52790 |   -20528 |    -9592 |    23341 |     38502 |  -55578 |
| SL 60%      |   -78483 |   -40599 |   -29662 |     3270 |     18431 |  -87409 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 10-10

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -13.77 |    -7.14 |    -5.22 |     0.54 |      3.2  |  -10.73 |
| SL 20%      |    -4.1  |     7.44 |     9.36 |    15.12 |     17.78 |    1.54 |
| SL 40%      |    -9.24 |    -3.59 |    -1.68 |     4.09 |      6.74 |   -9.73 |
| SL 60%      |   -13.74 |    -7.11 |    -5.19 |     0.57 |      3.23 |  -15.3  |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 10-10

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |       50 |       40 |       40 |       40 |        40 |      30 |
| SL 20%      |       40 |       40 |       40 |       40 |        40 |      30 |
| SL 40%      |       50 |       40 |       40 |       40 |        40 |      30 |
| SL 60%      |       50 |       40 |       40 |       40 |        40 |      30 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 12-12

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  -142995 |   -65871 |    14859 |    69047 |     63908 |  -42617 |
| SL 20%      |   -46458 |    19450 |    54560 |    99436 |     66972 |   -7654 |
| SL 40%      |  -105356 |   -73095 |   -37984 |     6891 |    -16067 |  -92012 |
| SL 60%      |   -97725 |   -20601 |    60130 |   114317 |    109178 |    3973 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 12-12

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -20.73 |    -9.55 |     2.15 |    10.01 |      9.27 |   -6.18 |
| SL 20%      |    -6.74 |     2.82 |     7.91 |    14.42 |      9.71 |   -1.11 |
| SL 40%      |   -15.28 |   -10.6  |    -5.51 |     1    |     -2.33 |  -13.34 |
| SL 60%      |   -14.17 |    -2.99 |     8.72 |    16.58 |     15.83 |    0.58 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 12-12

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    50    |    50    |    50    |    50    |     41.67 |   33.33 |
| SL 20%      |    33.33 |    33.33 |    33.33 |    33.33 |     25    |   16.67 |
| SL 40%      |    41.67 |    33.33 |    33.33 |    33.33 |     25    |   16.67 |
| SL 60%      |    50    |    50    |    50    |    50    |     41.67 |   33.33 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 16-16

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -50808 |    48441 |   154672 |   225921 |    257428 |  259998 |
| SL 20%      |   -39643 |    38265 |    85376 |   142251 |     25943 |   -8526 |
| SL 40%      |  -107623 |   -63362 |   -16252 |    40624 |   -104338 | -152128 |
| SL 60%      |   -58502 |    40747 |   146977 |   218227 |    300111 |  241313 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 16-16

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -5.48 |     5.23 |    16.69 |    24.38 |     27.78 |   28.06 |
| SL 20%      |    -4.28 |     4.13 |     9.21 |    15.35 |      2.8  |   -0.92 |
| SL 40%      |   -11.61 |    -6.84 |    -1.75 |     4.38 |    -11.26 |  -16.42 |
| SL 60%      |    -6.31 |     4.4  |    15.86 |    23.55 |     32.39 |   26.04 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 16-16

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    62.5  |    62.5  |    62.5  |    62.5  |     43.75 |   37.5  |
| SL 20%      |    37.5  |    37.5  |    37.5  |    37.5  |     18.75 |    6.25 |
| SL 40%      |    43.75 |    37.5  |    37.5  |    37.5  |     18.75 |    6.25 |
| SL 60%      |    56.25 |    56.25 |    56.25 |    56.25 |     37.5  |   25    |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_LONG  | 15:30       | SL 60%    | TP 120%   |       16 |      37.5 |      300111 |     32.39 |            1.87 |        -182837 |

## Top 10 variants by ROI (at least 30 trades)

(none yet)

## Top 10 variants by total PnL (at least 30 trades)

(none yet)

## Files in this folder

`trades_all_variants.csv.gz` (1104 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (16 trades of the best-PnL variant), `entries.csv` (one row per entry: level, Acc high / low, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
