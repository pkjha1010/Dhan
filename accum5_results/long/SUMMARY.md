# 5-DAY ACCUMULATION fake-break - LONG (ATM call) - SL x TP x time-exit grid

**Status:** PARTIAL - 3245 of 6548 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

close below the 5-day low (breakdown) -> within 3 days price crosses back above the 5-day high -> buy CALL

**Grid:** stop-loss no SL, SL 20%, SL 40% x target TP 20%, TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:30 = 72 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                               |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-----------------------------------------------------------------------------------------------------------|
| ACC5_LONG  |                 2194 |                        315 |                     14 |                       71 | Dhan returned no option candles for this period = 66; no ATM / ITM-1..ITM-3 candle at the entry minute = 5 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): -1: 2, 0: 313

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 108-108

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    86983 |   132330 |   104819 |   150312 |    130334 |  130334 |
| SL 20%      |   114757 |   155514 |   117163 |   151816 |    162798 |  162798 |
| SL 40%      |   100315 |   145662 |   118151 |   163644 |    143666 |  143666 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 108-108

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     1.55 |     2.35 |     1.86 |     2.67 |      2.32 |    2.32 |
| SL 20%      |     2.04 |     2.77 |     2.08 |     2.7  |      2.9  |    2.9  |
| SL 40%      |     1.78 |     2.59 |     2.1  |     2.91 |      2.56 |    2.56 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 108-108

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    50    |    47.22 |    46.3  |    46.3  |     46.3  |   46.3  |
| SL 20%      |    49.07 |    46.3  |    45.37 |    45.37 |     45.37 |   45.37 |
| SL 40%      |    50    |    47.22 |    46.3  |    46.3  |     46.3  |   46.3  |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 147-147

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   165191 |   271728 |   179410 |   242957 |    232879 |  289256 |
| SL 20%      |   159890 |   270956 |   165938 |   218645 |    257327 |  313704 |
| SL 40%      |   161518 |   264654 |   172336 |   235883 |    225806 |  282182 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 147-147

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     2.17 |     3.57 |     2.36 |     3.2  |      3.06 |    3.8  |
| SL 20%      |     2.1  |     3.56 |     2.18 |     2.88 |      3.38 |    4.13 |
| SL 40%      |     2.12 |     3.48 |     2.27 |     3.1  |      2.97 |    3.71 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 147-147

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    53.06 |    47.62 |    44.9  |    44.9  |     44.22 |   44.22 |
| SL 20%      |    50.34 |    44.9  |    42.18 |    42.18 |     42.18 |   42.18 |
| SL 40%      |    53.06 |    47.62 |    44.9  |    44.9  |     44.22 |   44.22 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 220-220

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   319476 |   461000 |   541619 |   737493 |    843912 |  855487 |
| SL 20%      |   223095 |   261649 |   316785 |   466269 |    513752 |  573437 |
| SL 40%      |   205094 |   304428 |   365515 |   561389 |    626459 |  631034 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 220-220

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     2.81 |     4.05 |     4.76 |     6.48 |      7.42 |    7.52 |
| SL 20%      |     1.96 |     2.3  |     2.79 |     4.1  |      4.52 |    5.04 |
| SL 40%      |     1.8  |     2.68 |     3.21 |     4.94 |      5.51 |    5.55 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 220-220

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    55.45 |    49.55 |    47.73 |    47.73 |     46.82 |   46.82 |
| SL 20%      |    50.91 |    44.55 |    42.73 |    42.27 |     41.36 |   41.36 |
| SL 40%      |    54.55 |    48.64 |    46.82 |    46.82 |     45.91 |   45.91 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 294-294

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   503085 |   598604 |   638011 |   914491 |   1082564 | 1412012 |
| SL 20%      |   368223 |   432131 |   445449 |   625375 |    508465 |  664863 |
| SL 40%      |   415802 |   447668 |   420494 |   699880 |    581059 |  787856 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 294-294

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     3.3  |     3.92 |     4.18 |     5.99 |      7.09 |    9.25 |
| SL 20%      |     2.41 |     2.83 |     2.92 |     4.1  |      3.33 |    4.36 |
| SL 40%      |     2.72 |     2.93 |     2.76 |     4.59 |      3.81 |    5.16 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 294-294

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    61.56 |    50    |    47.28 |    46.94 |     45.92 |   45.92 |
| SL 20%      |    53.74 |    43.54 |    41.16 |    40.48 |     39.12 |   39.12 |
| SL 40%      |    60.2  |    48.64 |    45.92 |    45.58 |     44.22 |   44.22 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_LONG  | 15:30       | no SL     | no TP     |      294 |     45.92 |     1412012 |      9.25 |            1.76 |        -310080 |

## Top 10 variants by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_LONG  | 15:30       | no SL     | no TP     |      294 |     45.92 |     1412012 |      9.25 |            1.76 |        -310080 |
| ACC5_LONG  | 12:00       | no SL     | no TP     |      220 |     46.82 |      855487 |      7.52 |            1.78 |        -125252 |
| ACC5_LONG  | 12:00       | no SL     | TP 120%   |      220 |     46.82 |      843912 |      7.42 |            1.77 |        -125252 |
| ACC5_LONG  | 15:30       | no SL     | TP 120%   |      294 |     45.92 |     1082564 |      7.09 |            1.58 |        -312400 |
| ACC5_LONG  | 12:00       | no SL     | TP 80%    |      220 |     47.73 |      737493 |      6.48 |            1.7  |        -125252 |
| ACC5_LONG  | 15:30       | no SL     | TP 80%    |      294 |     46.94 |      914491 |      5.99 |            1.53 |        -263528 |
| ACC5_LONG  | 12:00       | SL 40%    | no TP     |      220 |     45.91 |      631034 |      5.55 |            1.55 |        -236796 |
| ACC5_LONG  | 12:00       | SL 40%    | TP 120%   |      220 |     45.91 |      626459 |      5.51 |            1.54 |        -236796 |
| ACC5_LONG  | 15:30       | SL 40%    | no TP     |      294 |     44.22 |      787856 |      5.16 |            1.42 |        -346430 |
| ACC5_LONG  | 12:00       | SL 20%    | no TP     |      220 |     41.36 |      573437 |      5.04 |            1.56 |        -215202 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_LONG  | 15:30       | no SL     | no TP     |      294 |     45.92 |     1412012 |      9.25 |            1.76 |        -310080 |
| ACC5_LONG  | 15:30       | no SL     | TP 120%   |      294 |     45.92 |     1082564 |      7.09 |            1.58 |        -312400 |
| ACC5_LONG  | 15:30       | no SL     | TP 80%    |      294 |     46.94 |      914491 |      5.99 |            1.53 |        -263528 |
| ACC5_LONG  | 12:00       | no SL     | no TP     |      220 |     46.82 |      855487 |      7.52 |            1.78 |        -125252 |
| ACC5_LONG  | 12:00       | no SL     | TP 120%   |      220 |     46.82 |      843912 |      7.42 |            1.77 |        -125252 |
| ACC5_LONG  | 15:30       | SL 40%    | no TP     |      294 |     44.22 |      787856 |      5.16 |            1.42 |        -346430 |
| ACC5_LONG  | 12:00       | no SL     | TP 80%    |      220 |     47.73 |      737493 |      6.48 |            1.7  |        -125252 |
| ACC5_LONG  | 15:30       | SL 40%    | TP 80%    |      294 |     45.58 |      699880 |      4.59 |            1.4  |        -289479 |
| ACC5_LONG  | 15:30       | SL 20%    | no TP     |      294 |     39.12 |      664863 |      4.36 |            1.43 |        -276636 |
| ACC5_LONG  | 15:30       | no SL     | TP 60%    |      294 |     47.28 |      638011 |      4.18 |            1.37 |        -252370 |

## Files in this folder

`trades_all_variants.csv.gz` (13842 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (294 trades of the best-PnL variant), `entries.csv` (one row per entry: level, Acc high / low, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
