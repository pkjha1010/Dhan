# GAP-FADE-REVERSAL - SHORT (ATM put) - SL x TP x time-exit grid

**Status:** PARTIAL - 4632 of 6359 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

gap down > 1% on day i and day i+1 closes above day i close -> first cross below day i LOW on day i+2..i+4 -> buy PUT

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 20%, TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:30 = 96 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                 |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-------------------------------------------------------------------------------------------------------------|
| GAP_SHORT  |                 1542 |                        764 |                     49 |                      147 | Dhan returned no option candles for this period = 127; no ATM / ITM-1..ITM-3 candle at the entry minute = 20 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 735, 1: 23, 2: 5, 3: 1

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 313-313

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |   971645 |  1006950 |  1049404 |  1050232 |    931559 |  802998 |
| SL 20%      |   734652 |   746546 |   817142 |   845902 |    778041 |  649480 |
| SL 40%      |   914402 |   949708 |   992161 |   992990 |    874317 |  737179 |
| SL 60%      |   942395 |   977700 |  1020154 |  1020982 |    902309 |  773748 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 313-313

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     6    |     6.22 |     6.48 |     6.48 |      5.75 |    4.96 |
| SL 20%      |     4.54 |     4.61 |     5.05 |     5.22 |      4.8  |    4.01 |
| SL 40%      |     5.65 |     5.86 |     6.13 |     6.13 |      5.4  |    4.55 |
| SL 60%      |     5.82 |     6.04 |     6.3  |     6.3  |      5.57 |    4.78 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 313-313

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    57.51 |    56.23 |    55.91 |    55.59 |     55.27 |   54.95 |
| SL 20%      |    55.27 |    53.99 |    53.99 |    53.67 |     53.67 |   53.35 |
| SL 40%      |    57.51 |    56.23 |    55.91 |    55.59 |     55.27 |   54.95 |
| SL 60%      |    57.51 |    56.23 |    55.91 |    55.59 |     55.27 |   54.95 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 376-376

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  1349321 |  1415232 |  1558705 |  1487560 |   1219884 |  895011 |
| SL 20%      |  1016942 |  1135150 |  1286456 |  1287520 |   1153126 |  842547 |
| SL 40%      |  1195702 |  1256682 |  1400156 |  1334011 |   1134772 |  815617 |
| SL 60%      |  1194303 |  1230094 |  1373567 |  1301922 |   1091246 |  766372 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 376-376

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     6.94 |     7.28 |     8.02 |     7.65 |      6.28 |    4.6  |
| SL 20%      |     5.23 |     5.84 |     6.62 |     6.62 |      5.93 |    4.33 |
| SL 40%      |     6.15 |     6.47 |     7.2  |     6.86 |      5.84 |    4.2  |
| SL 60%      |     6.14 |     6.33 |     7.07 |     6.7  |      5.61 |    3.94 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 376-376

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    63.83 |    59.04 |    58.78 |    58.24 |     57.71 |   57.45 |
| SL 20%      |    60.64 |    56.38 |    56.38 |    56.12 |     55.85 |   55.59 |
| SL 40%      |    63.3  |    58.51 |    58.24 |    57.71 |     57.18 |   56.91 |
| SL 60%      |    63.56 |    58.78 |    58.51 |    57.98 |     57.45 |   57.18 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 524-524

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  1453545 |  1554991 |  1538353 |  1638202 |   1289346 | 1116964 |
| SL 20%      |   789659 |   568783 |   511702 |   560306 |    444520 |  417430 |
| SL 40%      |  1166932 |  1117062 |  1011754 |  1007887 |    798083 |  732614 |
| SL 60%      |  1238320 |  1151516 |  1125743 |  1120074 |    909092 |  859188 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 524-524

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     5.32 |     5.69 |     5.63 |     5.99 |      4.72 |    4.09 |
| SL 20%      |     2.89 |     2.08 |     1.87 |     2.05 |      1.63 |    1.53 |
| SL 40%      |     4.27 |     4.09 |     3.7  |     3.69 |      2.92 |    2.68 |
| SL 60%      |     4.53 |     4.21 |     4.12 |     4.1  |      3.33 |    3.14 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 524-524

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    58.59 |    50.76 |    48.85 |    48.28 |     47.33 |   47.14 |
| SL 20%      |    51.72 |    43.32 |    41.41 |    40.84 |     40.46 |   40.27 |
| SL 40%      |    57.44 |    49.62 |    47.52 |    46.76 |     45.99 |   45.8  |
| SL 60%      |    58.02 |    50.19 |    48.28 |    47.52 |     46.76 |   46.56 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 710-710

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |    no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|---------:|
| no SL       |  3887901 |  4610138 |  4691420 |  4987819 |   5231173 | 41868896 |
| SL 20%      |  2103065 |  1814273 |  1817999 |  1990324 |   1959288 | 37043242 |
| SL 40%      |  2704263 |  3112610 |  3077094 |  3278718 |   3538277 | 40314935 |
| SL 60%      |  3273491 |  3667179 |  3792853 |  3996637 |   4308548 | 41088634 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 710-710

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    10.48 |    12.42 |    12.64 |    13.44 |     14.1  |  112.83 |
| SL 20%      |     5.67 |     4.89 |     4.9  |     5.36 |      5.28 |   99.83 |
| SL 40%      |     7.29 |     8.39 |     8.29 |     8.84 |      9.54 |  108.64 |
| SL 60%      |     8.82 |     9.88 |    10.22 |    10.77 |     11.61 |  110.73 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 710-710

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    64.65 |    55.35 |    52.25 |    51.69 |     50.7  |   49.44 |
| SL 20%      |    54.93 |    43.94 |    41.27 |    40.56 |     39.86 |   39.01 |
| SL 40%      |    61.97 |    52.39 |    49.3  |    48.59 |     47.75 |   46.76 |
| SL 60%      |    63.52 |    53.94 |    50.99 |    50.28 |     49.58 |   48.59 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT  | 15:30       | no SL     | no TP     |      710 |     49.44 |    41868896 |    112.83 |           11.31 |        -478911 |

## Top 10 variants by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT  | 15:30       | no SL     | no TP     |      710 |     49.44 |    41868896 |    112.83 |           11.31 |        -478911 |
| GAP_SHORT  | 15:30       | SL 60%    | no TP     |      710 |     48.59 |    41088634 |    110.73 |           10.48 |        -482775 |
| GAP_SHORT  | 15:30       | SL 40%    | no TP     |      710 |     46.76 |    40314935 |    108.64 |           10.07 |        -493938 |
| GAP_SHORT  | 15:30       | SL 20%    | no TP     |      710 |     39.01 |    37043242 |     99.83 |            9.63 |        -855987 |
| GAP_SHORT  | 15:30       | no SL     | TP 120%   |      710 |     50.7  |     5231173 |     14.1  |            2.35 |        -478911 |
| GAP_SHORT  | 15:30       | no SL     | TP 80%    |      710 |     51.69 |     4987819 |     13.44 |            2.39 |        -414968 |
| GAP_SHORT  | 15:30       | no SL     | TP 60%    |      710 |     52.25 |     4691420 |     12.64 |            2.34 |        -418902 |
| GAP_SHORT  | 15:30       | no SL     | TP 40%    |      710 |     55.35 |     4610138 |     12.42 |            2.42 |        -405421 |
| GAP_SHORT  | 15:30       | SL 60%    | TP 120%   |      710 |     49.58 |     4308548 |     11.61 |            2.01 |        -478911 |
| GAP_SHORT  | 15:30       | SL 60%    | TP 80%    |      710 |     50.28 |     3996637 |     10.77 |            1.98 |        -414968 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT  | 15:30       | no SL     | no TP     |      710 |     49.44 |    41868896 |    112.83 |           11.31 |        -478911 |
| GAP_SHORT  | 15:30       | SL 60%    | no TP     |      710 |     48.59 |    41088634 |    110.73 |           10.48 |        -482775 |
| GAP_SHORT  | 15:30       | SL 40%    | no TP     |      710 |     46.76 |    40314935 |    108.64 |           10.07 |        -493938 |
| GAP_SHORT  | 15:30       | SL 20%    | no TP     |      710 |     39.01 |    37043242 |     99.83 |            9.63 |        -855987 |
| GAP_SHORT  | 15:30       | no SL     | TP 120%   |      710 |     50.7  |     5231173 |     14.1  |            2.35 |        -478911 |
| GAP_SHORT  | 15:30       | no SL     | TP 80%    |      710 |     51.69 |     4987819 |     13.44 |            2.39 |        -414968 |
| GAP_SHORT  | 15:30       | no SL     | TP 60%    |      710 |     52.25 |     4691420 |     12.64 |            2.34 |        -418902 |
| GAP_SHORT  | 15:30       | no SL     | TP 40%    |      710 |     55.35 |     4610138 |     12.42 |            2.42 |        -405421 |
| GAP_SHORT  | 15:30       | SL 60%    | TP 120%   |      710 |     49.58 |     4308548 |     11.61 |            2.01 |        -478911 |
| GAP_SHORT  | 15:30       | SL 60%    | TP 80%    |      710 |     50.28 |     3996637 |     10.77 |            1.98 |        -414968 |

## Files in this folder

`trades_all_variants.csv.gz` (46152 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (710 trades of the best-PnL variant), `entries.csv` (one row per entry: level, gap %, entry-day offset, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
