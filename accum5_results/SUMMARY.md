# 5-DAY ACCUMULATION fake-break (LONG call + SHORT put) - SL x TP x time-exit grid

**Status:** PARTIAL - 3245 of 6548 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

5-DAY ACCUMULATION fake-break.  Acc_High / Acc_Low = highest High / lowest Low of the prior 5 completed days.  LONG (ATM call): a daily close below Acc_Low, then within 3 days price crosses back above Acc_High (that day's).  SHORT (ATM put): a daily close above Acc_High, then within 3 days price crosses back below Acc_Low.  Entry = the first 1-minute candle (09:15 to 15:20) that reaches the level; option = ATM, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute.

LONG and SHORT are reported separately: `long/` and `short/` each hold their own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                               |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-----------------------------------------------------------------------------------------------------------|
| ACC5_LONG  |                 2194 |                        315 |                     14 |                       71 | Dhan returned no option candles for this period = 66; no ATM / ITM-1..ITM-3 candle at the entry minute = 5 |
| ACC5_SHORT |                 1799 |                        268 |                     20 |                       36 | Dhan returned no option candles for this period = 33; no ATM / ITM-1..ITM-3 candle at the entry minute = 3 |

## Best variant by total PnL (per direction)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_LONG  | 15:30       | no SL     | no TP     |      294 |     45.92 |     1412012 |      9.25 |            1.76 |        -310080 |
| ACC5_SHORT | 15:30       | no SL     | no TP     |      243 |     47.74 |     4196429 |     32.96 |            3.42 |        -422502 |

## LONG - top 10 by ROI (at least 30 trades)

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

## SHORT - top 10 by ROI (at least 30 trades)

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

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
