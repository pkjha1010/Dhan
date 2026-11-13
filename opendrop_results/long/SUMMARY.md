# OPEN-DROP RETEST - LONG (ATM call) - SL x TP x time-exit grid

**Status:** PARTIAL - 1414 of 2421 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2025-11-12 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

first hourly candle falls > 1% (red) on day i -> a day i+1..i+3 trades <= 1% below its close -> first cross above that close on the next 1..5 days (1-minute) -> buy CALL; NIFTY50 hourly slope >= -0.5 on day i

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:00, 15:30 = 100 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy      |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                               |
|:--------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-----------------------------------------------------------------------------------------------------------|
| OPENDROP_LONG |                 1550 |                        488 |                     26 |                       55 | Dhan returned no option candles for this period = 48; no ATM / ITM-1..ITM-3 candle at the entry minute = 7 |

## Strike used

strike_offset 0 = ATM, -n = ITM-n (the ATM series had no candle at the entry minute): -2: 1, -1: 3, 0: 484

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 280-280

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   526751 |   569322 |   614168 |    606593 |  605586 |
| SL 20%      |   480639 |   523210 |   568055 |    560481 |  559473 |
| SL 40%      |   526489 |   569060 |   613906 |    606331 |  605323 |
| SL 60%      |   530385 |   572956 |   617802 |    610227 |  609219 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 280-280

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     3.75 |     4.05 |     4.37 |      4.32 |    4.31 |
| SL 20%      |     3.42 |     3.72 |     4.04 |      3.99 |    3.98 |
| SL 40%      |     3.75 |     4.05 |     4.37 |      4.31 |    4.31 |
| SL 60%      |     3.77 |     4.08 |     4.4  |      4.34 |    4.34 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 280-280

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    53.93 |    53.93 |    53.93 |     53.93 |   53.93 |
| SL 20%      |    52.86 |    52.86 |    52.86 |     52.86 |   52.86 |
| SL 40%      |    53.93 |    53.93 |    53.93 |     53.93 |   53.93 |
| SL 60%      |    53.93 |    53.93 |    53.93 |     53.93 |   53.93 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 320-320

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   430817 |   574567 |   642686 |    612159 |  581934 |
| SL 20%      |   456501 |   599102 |   652642 |    624274 |  594049 |
| SL 40%      |   472238 |   615987 |   684106 |    653579 |  623354 |
| SL 60%      |   424525 |   568274 |   636394 |    605866 |  575641 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 320-320

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     2.68 |     3.57 |     3.99 |      3.8  |    3.61 |
| SL 20%      |     2.84 |     3.72 |     4.05 |      3.88 |    3.69 |
| SL 40%      |     2.93 |     3.83 |     4.25 |      4.06 |    3.87 |
| SL 60%      |     2.64 |     3.53 |     3.95 |      3.76 |    3.58 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 320-320

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    51.56 |    51.56 |    51.56 |     51.56 |   51.56 |
| SL 20%      |    50.31 |    50.31 |    50.31 |     50.31 |   50.31 |
| SL 40%      |    51.56 |    51.56 |    51.56 |     51.56 |   51.56 |
| SL 60%      |    51.56 |    51.56 |    51.56 |     51.56 |   51.56 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 388-388

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   483293 |   549600 |   679787 |    627814 |  483916 |
| SL 20%      |   448572 |   516441 |   636540 |    563507 |  423929 |
| SL 40%      |   600290 |   666597 |   796784 |    744811 |  600913 |
| SL 60%      |   505004 |   571312 |   701498 |    649526 |  505627 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 388-388

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     2.46 |     2.8  |     3.46 |      3.19 |    2.46 |
| SL 20%      |     2.28 |     2.63 |     3.24 |      2.87 |    2.16 |
| SL 40%      |     3.05 |     3.39 |     4.05 |      3.79 |    3.06 |
| SL 60%      |     2.57 |     2.91 |     3.57 |      3.3  |    2.57 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 388-388

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    47.68 |    46.91 |    46.91 |     46.91 |   46.91 |
| SL 20%      |    44.85 |    44.07 |    44.07 |     44.07 |   44.07 |
| SL 40%      |    47.68 |    46.91 |    46.91 |     46.91 |   46.91 |
| SL 60%      |    47.68 |    46.91 |    46.91 |     46.91 |   46.91 |

## Exit 15:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 449-449

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   632153 |   495102 |   614687 |    487511 |  343453 |
| SL 20%      |   587025 |   500557 |   564063 |    394645 |  228641 |
| SL 40%      |   708952 |   621085 |   740670 |    610807 |  461219 |
| SL 60%      |   592719 |   455669 |   575253 |    448077 |  304019 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 449-449

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     2.77 |     2.17 |     2.69 |      2.13 |    1.5  |
| SL 20%      |     2.57 |     2.19 |     2.47 |      1.73 |    1    |
| SL 40%      |     3.1  |     2.72 |     3.24 |      2.67 |    2.02 |
| SL 60%      |     2.59 |     1.99 |     2.52 |      1.96 |    1.33 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 449-449

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    47.22 |    44.99 |    44.54 |     44.1  |   43.88 |
| SL 20%      |    42.32 |    40.76 |    40.31 |     39.64 |   39.2  |
| SL 40%      |    46.77 |    44.77 |    44.32 |     43.88 |   43.65 |
| SL 60%      |    46.99 |    44.77 |    44.32 |     43.88 |   43.65 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 460-460

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   572653 |   389623 |   491630 |    399875 |  248031 |
| SL 20%      |   671360 |   569360 |   636979 |    512216 |  270333 |
| SL 40%      |   683985 |   561139 |   663834 |    575663 |  398934 |
| SL 60%      |   576493 |   396351 |   498358 |    406603 |  254759 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 460-460

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     2.45 |     1.67 |     2.1  |      1.71 |    1.06 |
| SL 20%      |     2.87 |     2.43 |     2.72 |      2.19 |    1.16 |
| SL 40%      |     2.92 |     2.4  |     2.84 |      2.46 |    1.71 |
| SL 60%      |     2.46 |     1.69 |     2.13 |      1.74 |    1.09 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 460-460

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    48.26 |    45.87 |    45.43 |     45    |   45    |
| SL 20%      |    44.13 |    41.96 |    41.52 |     40.87 |   40.43 |
| SL 40%      |    47.83 |    45.65 |    45.22 |     44.78 |   44.57 |
| SL 60%      |    48.04 |    45.65 |    45.22 |     44.78 |   44.78 |

## Best variant by total PnL

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 12:00       | SL 40%    | TP 80%    |      388 |     46.91 |      796784 |      4.05 |            1.49 |        -297996 |

## Top 10 variants by ROI (at least 30 trades)

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 09:30       | SL 60%    | TP 80%    |      280 |     53.93 |      617802 |      4.4  |            1.99 |        -124094 |
| OPENDROP_LONG | 09:30       | SL 40%    | TP 80%    |      280 |     53.93 |      613906 |      4.37 |            1.98 |        -123712 |
| OPENDROP_LONG | 09:30       | no SL     | TP 80%    |      280 |     53.93 |      614168 |      4.37 |            1.98 |        -124094 |
| OPENDROP_LONG | 09:30       | SL 60%    | no TP     |      280 |     53.93 |      609219 |      4.34 |            1.98 |        -124094 |
| OPENDROP_LONG | 09:30       | SL 60%    | TP 120%   |      280 |     53.93 |      610227 |      4.34 |            1.98 |        -124094 |
| OPENDROP_LONG | 09:30       | no SL     | TP 120%   |      280 |     53.93 |      606593 |      4.32 |            1.97 |        -124094 |
| OPENDROP_LONG | 09:30       | no SL     | no TP     |      280 |     53.93 |      605586 |      4.31 |            1.97 |        -124094 |
| OPENDROP_LONG | 09:30       | SL 40%    | TP 120%   |      280 |     53.93 |      606331 |      4.31 |            1.97 |        -123712 |
| OPENDROP_LONG | 09:30       | SL 40%    | no TP     |      280 |     53.93 |      605323 |      4.31 |            1.97 |        -123712 |
| OPENDROP_LONG | 10:00       | SL 40%    | TP 80%    |      320 |     51.56 |      684106 |      4.25 |            1.68 |        -147608 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 12:00       | SL 40%    | TP 80%    |      388 |     46.91 |      796784 |      4.05 |            1.49 |        -297996 |
| OPENDROP_LONG | 12:00       | SL 40%    | TP 120%   |      388 |     46.91 |      744811 |      3.79 |            1.45 |        -299184 |
| OPENDROP_LONG | 15:00       | SL 40%    | TP 80%    |      449 |     44.32 |      740670 |      3.24 |            1.33 |        -380226 |
| OPENDROP_LONG | 15:00       | SL 40%    | TP 40%    |      449 |     46.77 |      708952 |      3.1  |            1.32 |        -333133 |
| OPENDROP_LONG | 12:00       | SL 60%    | TP 80%    |      388 |     46.91 |      701498 |      3.57 |            1.4  |        -328013 |
| OPENDROP_LONG | 10:00       | SL 40%    | TP 80%    |      320 |     51.56 |      684106 |      4.25 |            1.68 |        -147608 |
| OPENDROP_LONG | 15:30       | SL 40%    | TP 40%    |      460 |     47.83 |      683985 |      2.92 |            1.29 |        -367506 |
| OPENDROP_LONG | 12:00       | no SL     | TP 80%    |      388 |     46.91 |      679787 |      3.46 |            1.39 |        -335593 |
| OPENDROP_LONG | 15:30       | SL 20%    | TP 40%    |      460 |     44.13 |      671360 |      2.87 |            1.32 |        -244370 |
| OPENDROP_LONG | 12:00       | SL 40%    | TP 60%    |      388 |     46.91 |      666597 |      3.39 |            1.41 |        -291497 |

## Files in this folder

`trades_all_variants.csv.gz` (37940 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (388 trades of the best-PnL variant), `entries.csv` (one row per entry: level, setup / drop day, first-candle drop %, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for the whole year. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
