# 5-DAY ACCUMULATION fake-break - SHORT (ATM put) - SL x TP x time-exit grid

**Status:** PARTIAL - 3245 of 6548 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

close above the 5-day high (breakout) -> within 3 days price crosses back below the 5-day low -> buy PUT

**Grid:** stop-loss no SL, SL 20%, SL 40% x target TP 20%, TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:30 = 72 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                               |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-----------------------------------------------------------------------------------------------------------|
| ACC5_SHORT |                 1799 |                        268 |                     20 |                       36 | Dhan returned no option candles for this period = 33; no ATM / ITM-1..ITM-3 candle at the entry minute = 3 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 263, 1: 3, 2: 1, 3: 1

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 97-97

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   227990 |   286233 |   246724 |   276123 |    248631 |  131895 |
| SL 20%      |   156684 |   196456 |   180972 |   198821 |    215218 |   98482 |
| SL 40%      |   221175 |   279418 |   239909 |   269309 |    216406 |   99670 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 97-97

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     4.46 |     5.6  |     4.83 |     5.4  |      4.86 |    2.58 |
| SL 20%      |     3.06 |     3.84 |     3.54 |     3.89 |      4.21 |    1.93 |
| SL 40%      |     4.33 |     5.46 |     4.69 |     5.27 |      4.23 |    1.95 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 97-97

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    53.61 |    50.52 |    48.45 |    48.45 |     48.45 |   47.42 |
| SL 20%      |    50.52 |    47.42 |    45.36 |    45.36 |     45.36 |   44.33 |
| SL 40%      |    53.61 |    50.52 |    48.45 |    48.45 |     47.42 |   46.39 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 116-116

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   227163 |   187909 |    77535 |    85142 |    106663 |  -88037 |
| SL 20%      |   174175 |   154035 |    99473 |    95890 |    139356 |  -40464 |
| SL 40%      |   228852 |   201495 |    81720 |    78572 |     52738 | -141962 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 116-116

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     3.73 |     3.09 |     1.27 |     1.4  |      1.75 |   -1.45 |
| SL 20%      |     2.86 |     2.53 |     1.63 |     1.57 |      2.29 |   -0.66 |
| SL 40%      |     3.76 |     3.31 |     1.34 |     1.29 |      0.87 |   -2.33 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 116-116

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    55.17 |    48.28 |    45.69 |    44.83 |     44.83 |   43.97 |
| SL 20%      |    50.86 |    43.97 |    42.24 |    41.38 |     41.38 |   40.52 |
| SL 40%      |    55.17 |    48.28 |    45.69 |    44.83 |     43.97 |   43.1  |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 174-174

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   532730 |   683469 |   699088 |   747788 |    793410 |  734826 |
| SL 20%      |   316215 |   370141 |   319287 |   304506 |    323633 |  159129 |
| SL 40%      |   476224 |   579416 |   533871 |   544292 |    519914 |  346770 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 174-174

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     5.88 |     7.54 |     7.71 |     8.25 |      8.75 |    8.11 |
| SL 20%      |     3.49 |     4.08 |     3.52 |     3.36 |      3.57 |    1.76 |
| SL 40%      |     5.25 |     6.39 |     5.89 |     6.01 |      5.74 |    3.83 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 174-174

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    60.92 |    54.6  |    51.72 |    50.57 |     50    |   50    |
| SL 20%      |    53.45 |    45.4  |    41.95 |    40.23 |     39.66 |   39.08 |
| SL 40%      |    60.92 |    54.02 |    50.57 |    48.85 |     47.7  |   47.13 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 243-243

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   831043 |  1069797 |   934522 |  1071103 |    909519 | 4196429 |
| SL 20%      |   369762 |   488129 |   350886 |   375056 |    437392 | 3728588 |
| SL 40%      |   798209 |   935933 |   743505 |   829061 |    755829 | 4034459 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 243-243

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     6.53 |     8.4  |     7.34 |     8.41 |      7.14 |   32.96 |
| SL 20%      |     2.9  |     3.83 |     2.76 |     2.95 |      3.44 |   29.29 |
| SL 40%      |     6.27 |     7.35 |     5.84 |     6.51 |      5.94 |   31.69 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 243-243

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    64.61 |    56.38 |    52.26 |    51.03 |     48.97 |   47.74 |
| SL 20%      |    51.03 |    42.39 |    38.27 |    36.63 |     35.39 |   34.16 |
| SL 40%      |    62.96 |    53.91 |    48.97 |    47.74 |     46.09 |   44.86 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_SHORT | 15:30       | no SL     | no TP     |      243 |     47.74 |     4196429 |     32.96 |            3.42 |        -422502 |

## Top 10 variants by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_SHORT | 15:30       | no SL     | no TP     |      243 |     47.74 |     4196429 |     32.96 |            3.42 |        -422502 |
| ACC5_SHORT | 15:30       | SL 40%    | no TP     |      243 |     44.86 |     4034459 |     31.69 |            3.33 |        -334110 |
| ACC5_SHORT | 15:30       | SL 20%    | no TP     |      243 |     34.16 |     3728588 |     29.29 |            3.29 |        -612013 |
| ACC5_SHORT | 12:00       | no SL     | TP 120%   |      174 |     50    |      793410 |      8.75 |            1.83 |        -142700 |
| ACC5_SHORT | 15:30       | no SL     | TP 80%    |      243 |     51.03 |     1071103 |      8.41 |            1.69 |        -231528 |
| ACC5_SHORT | 15:30       | no SL     | TP 40%    |      243 |     56.38 |     1069797 |      8.4  |            1.81 |        -136118 |
| ACC5_SHORT | 12:00       | no SL     | TP 80%    |      174 |     50.57 |      747788 |      8.25 |            1.79 |        -145010 |
| ACC5_SHORT | 12:00       | no SL     | no TP     |      174 |     50    |      734826 |      8.11 |            1.77 |        -142700 |
| ACC5_SHORT | 12:00       | no SL     | TP 60%    |      174 |     51.72 |      699088 |      7.71 |            1.77 |        -154838 |
| ACC5_SHORT | 12:00       | no SL     | TP 40%    |      174 |     54.6  |      683469 |      7.54 |            1.81 |        -128275 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_SHORT | 15:30       | no SL     | no TP     |      243 |     47.74 |     4196429 |     32.96 |            3.42 |        -422502 |
| ACC5_SHORT | 15:30       | SL 40%    | no TP     |      243 |     44.86 |     4034459 |     31.69 |            3.33 |        -334110 |
| ACC5_SHORT | 15:30       | SL 20%    | no TP     |      243 |     34.16 |     3728588 |     29.29 |            3.29 |        -612013 |
| ACC5_SHORT | 15:30       | no SL     | TP 80%    |      243 |     51.03 |     1071103 |      8.41 |            1.69 |        -231528 |
| ACC5_SHORT | 15:30       | no SL     | TP 40%    |      243 |     56.38 |     1069797 |      8.4  |            1.81 |        -136118 |
| ACC5_SHORT | 15:30       | SL 40%    | TP 40%    |      243 |     53.91 |      935933 |      7.35 |            1.69 |        -143458 |
| ACC5_SHORT | 15:30       | no SL     | TP 60%    |      243 |     52.26 |      934522 |      7.34 |            1.62 |        -218038 |
| ACC5_SHORT | 15:30       | no SL     | TP 120%   |      243 |     48.97 |      909519 |      7.14 |            1.55 |        -388912 |
| ACC5_SHORT | 15:30       | no SL     | TP 20%    |      243 |     64.61 |      831043 |      6.53 |            1.78 |        -145710 |
| ACC5_SHORT | 15:30       | SL 40%    | TP 80%    |      243 |     47.74 |      829061 |      6.51 |            1.51 |        -194382 |

## Files in this folder

`trades_all_variants.csv.gz` (11340 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (243 trades of the best-PnL variant), `entries.csv` (one row per entry: level, Acc high / low, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
