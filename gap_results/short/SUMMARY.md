# GAP-FADE-REVERSAL - SHORT (ATM put) - SL x TP x time-exit grid

**Status:** COMPLETE - all 6359 request groups finished.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

gap down > 1% on day i and day i+1 closes above day i close -> first cross below day i LOW on day i+2..i+4 -> buy PUT

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 20%, TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:30 = 96 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                 |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-------------------------------------------------------------------------------------------------------------|
| GAP_SHORT  |                 1542 |                       1254 |                     80 |                      288 | Dhan returned no option candles for this period = 251; no ATM / ITM-1..ITM-3 candle at the entry minute = 37 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 1196, 1: 42, 2: 13, 3: 3

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 533-533

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  1538451 |  1722832 |  1774050 |  1742369 |   1712226 | 1719138 |
| SL 20%      |  1321592 |  1481666 |  1561027 |  1557277 |   1577947 | 1584858 |
| SL 40%      |  1438269 |  1621754 |  1672972 |  1641291 |   1611148 | 1609483 |
| SL 60%      |  1509902 |  1694283 |  1745501 |  1713820 |   1683678 | 1690589 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 533-533

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     5.58 |     6.24 |     6.43 |     6.32 |      6.21 |    6.23 |
| SL 20%      |     4.79 |     5.37 |     5.66 |     5.64 |      5.72 |    5.74 |
| SL 40%      |     5.21 |     5.88 |     6.06 |     5.95 |      5.84 |    5.83 |
| SL 60%      |     5.47 |     6.14 |     6.33 |     6.21 |      6.1  |    6.13 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 533-533

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    57.97 |    57.04 |    56.85 |    56.66 |     56.47 |   56.29 |
| SL 20%      |    56.47 |    55.53 |    55.53 |    55.35 |     55.35 |   55.16 |
| SL 40%      |    57.79 |    56.85 |    56.66 |    56.47 |     56.29 |   56.1  |
| SL 60%      |    57.97 |    57.04 |    56.85 |    56.66 |     56.47 |   56.29 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 628-628

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  2196661 |  2357457 |  2537022 |  2399271 |   2242778 | 1779046 |
| SL 20%      |  1895585 |  2123872 |  2311270 |  2259325 |   2236114 | 1716477 |
| SL 40%      |  1983068 |  2159317 |  2338883 |  2208652 |   2120596 | 1592381 |
| SL 60%      |  2052709 |  2183385 |  2362950 |  2224699 |   2125206 | 1661473 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 628-628

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     6.77 |     7.27 |     7.82 |     7.4  |      6.91 |    5.48 |
| SL 20%      |     5.84 |     6.55 |     7.13 |     6.97 |      6.89 |    5.29 |
| SL 40%      |     6.11 |     6.66 |     7.21 |     6.81 |      6.54 |    4.91 |
| SL 60%      |     6.33 |     6.73 |     7.28 |     6.86 |      6.55 |    5.12 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 628-628

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    64.65 |    60.35 |    60.19 |    59.55 |     59.24 |   59.08 |
| SL 20%      |    62.26 |    58.44 |    58.44 |    57.96 |     57.8  |   57.48 |
| SL 40%      |    64.17 |    60.03 |    59.87 |    59.24 |     58.92 |   58.6  |
| SL 60%      |    64.49 |    60.19 |    60.03 |    59.39 |     59.08 |   58.92 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 873-873

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |  2507304 |  2715271 |  2749697 |  2769646 |   2350933 | 2190152 |
| SL 20%      |  1740122 |  1591921 |  1599864 |  1594083 |   1414790 | 1127957 |
| SL 40%      |  2156957 |  2268264 |  2214020 |  2140978 |   1803267 | 1451560 |
| SL 60%      |  2306211 |  2325929 |  2351220 |  2263813 |   1924924 | 1886621 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 873-873

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     5.52 |     5.98 |     6.06 |     6.1  |      5.18 |    4.82 |
| SL 20%      |     3.83 |     3.51 |     3.52 |     3.51 |      3.12 |    2.48 |
| SL 40%      |     4.75 |     5    |     4.88 |     4.72 |      3.97 |    3.2  |
| SL 60%      |     5.08 |     5.12 |     5.18 |     4.99 |      4.24 |    4.16 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 873-873

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    59.34 |    52    |    50.4  |    49.71 |     49.03 |   48.68 |
| SL 20%      |    53.95 |    46.16 |    44.56 |    43.87 |     43.53 |   42.96 |
| SL 40%      |    58.3  |    51.2  |    49.48 |    48.68 |     48    |   47.42 |
| SL 60%      |    58.99 |    51.66 |    50.06 |    49.26 |     48.57 |   48.22 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 1169-1169

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |    no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|---------:|
| no SL       |  5886185 |  6912492 |  6937150 |  7368620 |   7724165 | 44552760 |
| SL 20%      |  3569278 |  3303682 |  3466118 |  3782871 |   3750700 | 38273560 |
| SL 40%      |  4507260 |  5138628 |  5070333 |  5402043 |   5668489 | 41913677 |
| SL 60%      |  5118929 |  5823220 |  5871632 |  6185139 |   6556904 | 43515406 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 1169-1169

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |     9.66 |    11.35 |    11.39 |    12.09 |     12.68 |   73.13 |
| SL 20%      |     5.86 |     5.42 |     5.69 |     6.21 |      6.16 |   62.82 |
| SL 40%      |     7.4  |     8.43 |     8.32 |     8.87 |      9.3  |   68.79 |
| SL 60%      |     8.4  |     9.56 |     9.64 |    10.15 |     10.76 |   71.42 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 1169-1169

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|---------:|----------:|--------:|
| no SL       |    64.84 |    56.2  |    53.46 |    52.78 |     52.01 |   50.98 |
| SL 20%      |    56.12 |    45.94 |    43.63 |    42.86 |     42.26 |   41.32 |
| SL 40%      |    62.7  |    53.81 |    50.98 |    50.21 |     49.53 |   48.42 |
| SL 60%      |    63.9  |    55.09 |    52.35 |    51.58 |     50.98 |   50.13 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT  | 15:30       | no SL     | no TP     |     1169 |     50.98 |    44552760 |     73.13 |            7.75 |        -725247 |

## Top 10 variants by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT  | 15:30       | no SL     | no TP     |     1169 |     50.98 |    44552760 |     73.13 |            7.75 |        -725247 |
| GAP_SHORT  | 15:30       | SL 60%    | no TP     |     1169 |     50.13 |    43515406 |     71.42 |            7.27 |        -713583 |
| GAP_SHORT  | 15:30       | SL 40%    | no TP     |     1169 |     48.42 |    41913677 |     68.79 |            6.92 |        -715559 |
| GAP_SHORT  | 15:30       | SL 20%    | no TP     |     1169 |     41.32 |    38273560 |     62.82 |            6.69 |        -971647 |
| GAP_SHORT  | 15:30       | no SL     | TP 120%   |     1169 |     52.01 |     7724165 |     12.68 |            2.23 |        -698172 |
| GAP_SHORT  | 15:30       | no SL     | TP 80%    |     1169 |     52.78 |     7368620 |     12.09 |            2.24 |        -634230 |
| GAP_SHORT  | 15:30       | no SL     | TP 60%    |     1169 |     53.46 |     6937150 |     11.39 |            2.22 |        -638163 |
| GAP_SHORT  | 15:30       | no SL     | TP 40%    |     1169 |     56.2  |     6912492 |     11.35 |            2.33 |        -612136 |
| GAP_SHORT  | 15:30       | SL 60%    | TP 120%   |     1169 |     50.98 |     6556904 |     10.76 |            1.97 |        -698172 |
| GAP_SHORT  | 15:30       | SL 60%    | TP 80%    |     1169 |     51.58 |     6185139 |     10.15 |            1.95 |        -634230 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT  | 15:30       | no SL     | no TP     |     1169 |     50.98 |    44552760 |     73.13 |            7.75 |        -725247 |
| GAP_SHORT  | 15:30       | SL 60%    | no TP     |     1169 |     50.13 |    43515406 |     71.42 |            7.27 |        -713583 |
| GAP_SHORT  | 15:30       | SL 40%    | no TP     |     1169 |     48.42 |    41913677 |     68.79 |            6.92 |        -715559 |
| GAP_SHORT  | 15:30       | SL 20%    | no TP     |     1169 |     41.32 |    38273560 |     62.82 |            6.69 |        -971647 |
| GAP_SHORT  | 15:30       | no SL     | TP 120%   |     1169 |     52.01 |     7724165 |     12.68 |            2.23 |        -698172 |
| GAP_SHORT  | 15:30       | no SL     | TP 80%    |     1169 |     52.78 |     7368620 |     12.09 |            2.24 |        -634230 |
| GAP_SHORT  | 15:30       | no SL     | TP 60%    |     1169 |     53.46 |     6937150 |     11.39 |            2.22 |        -638163 |
| GAP_SHORT  | 15:30       | no SL     | TP 40%    |     1169 |     56.2  |     6912492 |     11.35 |            2.33 |        -612136 |
| GAP_SHORT  | 15:30       | SL 60%    | TP 120%   |     1169 |     50.98 |     6556904 |     10.76 |            1.97 |        -698172 |
| GAP_SHORT  | 15:30       | SL 60%    | TP 80%    |     1169 |     51.58 |     6185139 |     10.15 |            1.95 |        -634230 |

## Files in this folder

`trades_all_variants.csv.gz` (76872 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (1169 trades of the best-PnL variant), `entries.csv` (one row per entry: level, gap %, entry-day offset, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
