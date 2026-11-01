# GAP-FADE-REVERSAL - LONG (ATM call) - SL x TP x time-exit grid

**Status:** PARTIAL - 4632 of 6359 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

gap up > 1% on day i and day i+1 closes below day i close -> first cross above day i HIGH on day i+2..i+4 -> buy CALL

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 20%, TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:30 = 96 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                 |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-------------------------------------------------------------------------------------------------------------|
| GAP_LONG   |                 2703 |                       1117 |                     57 |                      490 | Dhan returned no option candles for this period = 478; no ATM / ITM-1..ITM-3 candle at the entry minute = 12 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): -1: 8, 0: 1109

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 444-444

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   715768 |   890156 |   928373 |   975615 |   1005723 |  984913 |
| SL 20%      |   623760 |   758042 |   769341 |   803407 |    833515 |  812704 |
| SL 40%      |   704738 |   885366 |   923583 |   970825 |   1000933 |  980123 |
| SL 60%      |   715768 |   886476 |   924693 |   971935 |   1002043 |  981233 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 444-444

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     3.19 |     3.96 |     4.13 |     4.34 |      4.48 |    4.39 |
| SL 20%      |     2.78 |     3.38 |     3.43 |     3.58 |      3.71 |    3.62 |
| SL 40%      |     3.14 |     3.94 |     4.11 |     4.32 |      4.46 |    4.37 |
| SL 60%      |     3.19 |     3.95 |     4.12 |     4.33 |      4.46 |    4.37 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 444-444

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    54.95 |    53.6  |    53.15 |    53.15 |     53.15 |   53.15 |
| SL 20%      |    54.05 |    52.48 |    52.03 |    52.03 |     52.03 |   52.03 |
| SL 40%      |    54.95 |    53.6  |    53.15 |    53.15 |     53.15 |   53.15 |
| SL 60%      |    54.95 |    53.6  |    53.15 |    53.15 |     53.15 |   53.15 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 593-593

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  1144892 |  1586246 |  1747829 |  1704523 |   1864137 | 1888190 |
| SL 20%      |  1034550 |  1377063 |  1456411 |  1377799 |   1505197 | 1485730 |
| SL 40%      |  1183301 |  1592485 |  1712983 |  1669677 |   1829291 | 1853343 |
| SL 60%      |  1140370 |  1568764 |  1730346 |  1687041 |   1846655 | 1870707 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 593-593

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     3.82 |     5.29 |     5.83 |     5.69 |      6.22 |    6.3  |
| SL 20%      |     3.45 |     4.59 |     4.86 |     4.6  |      5.02 |    4.96 |
| SL 40%      |     3.95 |     5.31 |     5.72 |     5.57 |      6.1  |    6.18 |
| SL 60%      |     3.81 |     5.23 |     5.77 |     5.63 |      6.16 |    6.24 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 593-593

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    56.16 |    53.79 |    52.95 |    52.61 |     52.61 |   52.61 |
| SL 20%      |    54.3  |    51.6  |    50.76 |    50.42 |     50.42 |   50.42 |
| SL 40%      |    56.16 |    53.63 |    52.78 |    52.45 |     52.45 |   52.45 |
| SL 60%      |    56.16 |    53.79 |    52.95 |    52.61 |     52.61 |   52.61 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 801-801

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  1700926 |  2505897 |  2777701 |  2444138 |   2767374 | 2098464 |
| SL 20%      |  1371722 |  1997903 |  2113800 |  1810261 |   2037865 | 1622223 |
| SL 40%      |  1611108 |  2342327 |  2488161 |  2181243 |   2504479 | 1770711 |
| SL 60%      |  1653192 |  2444083 |  2721287 |  2362112 |   2685348 | 1915495 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 801-801

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     4.18 |     6.16 |     6.82 |     6    |      6.8  |    5.15 |
| SL 20%      |     3.37 |     4.91 |     5.19 |     4.45 |      5.01 |    3.98 |
| SL 40%      |     3.96 |     5.75 |     6.11 |     5.36 |      6.15 |    4.35 |
| SL 60%      |     4.06 |     6    |     6.68 |     5.8  |      6.6  |    4.71 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 801-801

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    58.05 |    53.06 |    51.44 |    50.31 |     50.31 |   50.06 |
| SL 20%      |    54.43 |    49.44 |    47.82 |    46.82 |     46.82 |   46.44 |
| SL 40%      |    57.8  |    52.68 |    50.94 |    49.81 |     49.81 |   49.19 |
| SL 60%      |    58.05 |    53.06 |    51.44 |    50.31 |     50.31 |   49.81 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 1041-1041

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  2264839 |  3119521 |  3348867 |  3247995 |   3373938 | 3015477 |
| SL 20%      |  1641408 |  2213787 |  2399134 |  2267014 |   2108909 | 1579621 |
| SL 40%      |  1930429 |  2508163 |  2645939 |  2637488 |   2606262 | 1795133 |
| SL 60%      |  2230412 |  2983581 |  3283071 |  3181406 |   3102536 | 2446066 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 1041-1041

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     4.26 |     5.87 |     6.31 |     6.12 |      6.35 |    5.68 |
| SL 20%      |     3.09 |     4.17 |     4.52 |     4.27 |      3.97 |    2.97 |
| SL 40%      |     3.64 |     4.72 |     4.98 |     4.97 |      4.91 |    3.38 |
| SL 60%      |     4.2  |     5.62 |     6.18 |     5.99 |      5.84 |    4.61 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 1041-1041

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    59.75 |    51.49 |    49.18 |    48.13 |     47.65 |   46.97 |
| SL 20%      |    53.7  |    45.92 |    43.9  |    42.75 |     42.27 |   41.69 |
| SL 40%      |    58.5  |    50.24 |    48.22 |    47.26 |     46.69 |   45.92 |
| SL 60%      |    59.46 |    51.2  |    48.99 |    47.93 |     47.36 |   46.59 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 15:30       | no SL     | TP 120%   |     1041 |     47.65 |     3373938 |      6.35 |            1.63 |        -209091 |

## Top 10 variants by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 12:00       | no SL     | TP 60%    |      801 |     51.44 |     2777701 |      6.82 |            1.95 |        -122678 |
| GAP_LONG   | 12:00       | no SL     | TP 120%   |      801 |     50.31 |     2767374 |      6.8  |            1.91 |        -122678 |
| GAP_LONG   | 12:00       | SL 60%    | TP 60%    |      801 |     51.44 |     2721287 |      6.68 |            1.91 |        -139904 |
| GAP_LONG   | 12:00       | SL 60%    | TP 120%   |      801 |     50.31 |     2685348 |      6.6  |            1.86 |        -124780 |
| GAP_LONG   | 15:30       | no SL     | TP 120%   |     1041 |     47.65 |     3373938 |      6.35 |            1.63 |        -209091 |
| GAP_LONG   | 15:30       | no SL     | TP 60%    |     1041 |     49.18 |     3348867 |      6.31 |            1.65 |        -175156 |
| GAP_LONG   | 10:00       | no SL     | no TP     |      593 |     52.61 |     1888190 |      6.3  |            2.08 |        -144270 |
| GAP_LONG   | 10:00       | SL 60%    | no TP     |      593 |     52.61 |     1870707 |      6.24 |            2.06 |        -144270 |
| GAP_LONG   | 10:00       | no SL     | TP 120%   |      593 |     52.61 |     1864137 |      6.22 |            2.07 |        -144270 |
| GAP_LONG   | 10:00       | SL 40%    | no TP     |      593 |     52.45 |     1853343 |      6.18 |            2.05 |        -142070 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 15:30       | no SL     | TP 120%   |     1041 |     47.65 |     3373938 |      6.35 |            1.63 |        -209091 |
| GAP_LONG   | 15:30       | no SL     | TP 60%    |     1041 |     49.18 |     3348867 |      6.31 |            1.65 |        -175156 |
| GAP_LONG   | 15:30       | SL 60%    | TP 60%    |     1041 |     48.99 |     3283071 |      6.18 |            1.64 |        -213195 |
| GAP_LONG   | 15:30       | no SL     | TP 80%    |     1041 |     48.13 |     3247995 |      6.12 |            1.61 |        -163816 |
| GAP_LONG   | 15:30       | SL 60%    | TP 80%    |     1041 |     47.93 |     3181406 |      5.99 |            1.6  |        -190655 |
| GAP_LONG   | 15:30       | no SL     | TP 40%    |     1041 |     51.49 |     3119521 |      5.87 |            1.67 |        -173585 |
| GAP_LONG   | 15:30       | SL 60%    | TP 120%   |     1041 |     47.36 |     3102536 |      5.84 |            1.58 |        -204143 |
| GAP_LONG   | 15:30       | no SL     | no TP     |     1041 |     46.97 |     3015477 |      5.68 |            1.55 |        -316821 |
| GAP_LONG   | 15:30       | SL 60%    | TP 40%    |     1041 |     51.2  |     2983581 |      5.62 |            1.64 |        -199898 |
| GAP_LONG   | 12:00       | no SL     | TP 60%    |      801 |     51.44 |     2777701 |      6.82 |            1.95 |        -122678 |

## Files in this folder

`trades_all_variants.csv.gz` (69096 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (1041 trades of the best-PnL variant), `entries.csv` (one row per entry: level, gap %, entry-day offset, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
