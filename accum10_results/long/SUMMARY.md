# 10-DAY ACCUMULATION fake-break - LONG (ATM call) - SL x TP x time-exit grid

**Status:** COMPLETE - all 1530 request groups finished.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

close below the 10-day low (breakdown) -> within 3 days price crosses back above the 10-day high -> buy CALL

**Grid:** stop-loss no SL, SL 20%, SL 40% x target TP 20%, TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:30 = 72 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                               |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-----------------------------------------------------------------------------------------------------------|
| ACC10_LONG |                  421 |                        342 |                     32 |                       79 | Dhan returned no option candles for this period = 78; no ATM / ITM-1..ITM-3 candle at the entry minute = 1 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 342

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 114-114

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -6742 |    39061 |     2801 |    22297 |     31384 |   31384 |
| SL 20%      |    10045 |    47336 |    14859 |    34355 |     43442 |   43442 |
| SL 40%      |   -35830 |     9974 |   -26286 |    -6790 |      2296 |    2296 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 114-114

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -0.11 |     0.66 |     0.05 |     0.38 |      0.53 |    0.53 |
| SL 20%      |     0.17 |     0.8  |     0.25 |     0.58 |      0.73 |    0.73 |
| SL 40%      |    -0.6  |     0.17 |    -0.44 |    -0.11 |      0.04 |    0.04 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 114-114

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    49.12 |    47.37 |    46.49 |    46.49 |     46.49 |   46.49 |
| SL 20%      |    49.12 |    47.37 |    46.49 |    46.49 |     46.49 |   46.49 |
| SL 40%      |    49.12 |    47.37 |    46.49 |    46.49 |     46.49 |   46.49 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 162-162

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    53386 |   164663 |   165839 |   241152 |    165623 |   97625 |
| SL 20%      |    51314 |    94993 |    73858 |   139172 |     81643 |   13645 |
| SL 40%      |   -21215 |    83912 |    73088 |   138401 |     80872 |   12874 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 162-162

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     0.63 |     1.96 |     1.97 |     2.87 |      1.97 |    1.16 |
| SL 20%      |     0.61 |     1.13 |     0.88 |     1.65 |      0.97 |    0.16 |
| SL 40%      |    -0.25 |     1    |     0.87 |     1.65 |      0.96 |    0.15 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 162-162

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    46.91 |    43.21 |    41.36 |    41.36 |     40.74 |   40.74 |
| SL 20%      |    45.68 |    40.74 |    38.27 |    38.27 |     37.65 |   37.65 |
| SL 40%      |    46.3  |    42.59 |    40.74 |    40.74 |     40.12 |   40.12 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 227-227

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   449641 |   439995 |   562457 |   590416 |    497506 |  460895 |
| SL 20%      |   314186 |   278360 |   285140 |   399910 |    331154 |  278020 |
| SL 40%      |   340885 |   347252 |   446231 |   459268 |    362310 |  236699 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 227-227

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     3.8  |     3.72 |     4.75 |     4.99 |      4.2  |    3.89 |
| SL 20%      |     2.65 |     2.35 |     2.41 |     3.38 |      2.8  |    2.35 |
| SL 40%      |     2.88 |     2.93 |     3.77 |     3.88 |      3.06 |    2    |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 227-227

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    59.47 |    50.66 |    48.46 |    47.14 |     45.81 |   45.81 |
| SL 20%      |    53.3  |    44.49 |    41.85 |    41.41 |     40.09 |   39.65 |
| SL 40%      |    58.15 |    49.78 |    47.58 |    46.26 |     44.93 |   44.49 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 305-305

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   635113 |   424481 |   336747 |   506955 |    202030 | -173050 |
| SL 20%      |   522286 |   286939 |   116741 |   169014 |     89963 | -181244 |
| SL 40%      |   581720 |   393681 |   220091 |   134970 |    -45843 | -399227 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 305-305

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     4.01 |     2.68 |     2.13 |     3.2  |      1.28 |   -1.09 |
| SL 20%      |     3.3  |     1.81 |     0.74 |     1.07 |      0.57 |   -1.15 |
| SL 40%      |     3.68 |     2.49 |     1.39 |     0.85 |     -0.29 |   -2.52 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 305-305

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    64.59 |    50.16 |    46.56 |    45.9  |     43.93 |   43.61 |
| SL 20%      |    55.74 |    42.3  |    38.69 |    38.03 |     36.72 |   36.39 |
| SL 40%      |    62.62 |    48.52 |    44.59 |    43.28 |     41.64 |   41.31 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_LONG | 15:30       | no SL     | TP 20%    |      305 |     64.59 |      635113 |      4.01 |            1.46 |        -142290 |

## Top 10 variants by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_LONG | 12:00       | no SL     | TP 80%    |      227 |     47.14 |      590416 |      4.99 |            1.49 |        -178689 |
| ACC10_LONG | 12:00       | no SL     | TP 60%    |      227 |     48.46 |      562457 |      4.75 |            1.5  |        -153187 |
| ACC10_LONG | 12:00       | no SL     | TP 120%   |      227 |     45.81 |      497506 |      4.2  |            1.39 |        -178689 |
| ACC10_LONG | 15:30       | no SL     | TP 20%    |      305 |     64.59 |      635113 |      4.01 |            1.46 |        -142290 |
| ACC10_LONG | 12:00       | no SL     | no TP     |      227 |     45.81 |      460895 |      3.89 |            1.37 |        -178689 |
| ACC10_LONG | 12:00       | SL 40%    | TP 80%    |      227 |     46.26 |      459268 |      3.88 |            1.37 |        -209698 |
| ACC10_LONG | 12:00       | no SL     | TP 20%    |      227 |     59.47 |      449641 |      3.8  |            1.49 |         -95006 |
| ACC10_LONG | 12:00       | SL 40%    | TP 60%    |      227 |     47.58 |      446231 |      3.77 |            1.38 |        -188592 |
| ACC10_LONG | 12:00       | no SL     | TP 40%    |      227 |     50.66 |      439995 |      3.72 |            1.4  |        -173396 |
| ACC10_LONG | 15:30       | SL 40%    | TP 20%    |      305 |     62.62 |      581720 |      3.68 |            1.43 |        -132530 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_LONG | 15:30       | no SL     | TP 20%    |      305 |     64.59 |      635113 |      4.01 |            1.46 |        -142290 |
| ACC10_LONG | 12:00       | no SL     | TP 80%    |      227 |     47.14 |      590416 |      4.99 |            1.49 |        -178689 |
| ACC10_LONG | 15:30       | SL 40%    | TP 20%    |      305 |     62.62 |      581720 |      3.68 |            1.43 |        -132530 |
| ACC10_LONG | 12:00       | no SL     | TP 60%    |      227 |     48.46 |      562457 |      4.75 |            1.5  |        -153187 |
| ACC10_LONG | 15:30       | SL 20%    | TP 20%    |      305 |     55.74 |      522286 |      3.3  |            1.43 |        -133487 |
| ACC10_LONG | 15:30       | no SL     | TP 80%    |      305 |     45.9  |      506955 |      3.2  |            1.25 |        -267589 |
| ACC10_LONG | 12:00       | no SL     | TP 120%   |      227 |     45.81 |      497506 |      4.2  |            1.39 |        -178689 |
| ACC10_LONG | 12:00       | no SL     | no TP     |      227 |     45.81 |      460895 |      3.89 |            1.37 |        -178689 |
| ACC10_LONG | 12:00       | SL 40%    | TP 80%    |      227 |     46.26 |      459268 |      3.88 |            1.37 |        -209698 |
| ACC10_LONG | 12:00       | no SL     | TP 20%    |      227 |     59.47 |      449641 |      3.8  |            1.49 |         -95006 |

## Files in this folder

`trades_all_variants.csv.gz` (14544 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (305 trades of the best-PnL variant), `entries.csv` (one row per entry: level, Acc high / low, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
