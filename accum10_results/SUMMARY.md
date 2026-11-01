# 10-DAY ACCUMULATION fake-break (LONG call + SHORT put) - SL x TP x time-exit grid

**Status:** COMPLETE - all 1530 request groups finished.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

10-DAY ACCUMULATION fake-break.  Acc_High / Acc_Low = highest High / lowest Low of the prior 10 completed days.  LONG (ATM call): a daily close below Acc_Low, then within 3 days price crosses back above Acc_High (that day's).  SHORT (ATM put): a daily close above Acc_High, then within 3 days price crosses back below Acc_Low.  Entry = the first 1-minute candle (09:15 to 15:20) that reaches the level; option = ATM, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute.

LONG and SHORT are reported separately: `long/` and `short/` each hold their own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy    |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                               |
|:------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-----------------------------------------------------------------------------------------------------------|
| ACC10_LONG  |                  421 |                        342 |                     32 |                       79 | Dhan returned no option candles for this period = 78; no ATM / ITM-1..ITM-3 candle at the entry minute = 1 |
| ACC10_SHORT |                  345 |                        298 |                     30 |                       47 | Dhan returned no option candles for this period = 44; no ATM / ITM-1..ITM-3 candle at the entry minute = 3 |

## Best variant by total PnL (per direction)

| strategy    | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_LONG  | 15:30       | no SL     | TP 20%    |      305 |     64.59 |      635113 |      4.01 |            1.46 |        -142290 |
| ACC10_SHORT | 15:30       | no SL     | TP 120%   |      264 |     43.94 |     1391283 |     10.2  |            1.79 |        -266468 |

## LONG - top 10 by ROI (at least 30 trades)

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

## SHORT - top 10 by ROI (at least 30 trades)

| strategy    | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_SHORT | 15:30       | no SL     | TP 120%   |      264 |     43.94 |     1391283 |     10.2  |            1.79 |        -266468 |
| ACC10_SHORT | 15:30       | no SL     | TP 60%    |      264 |     47.73 |     1292223 |      9.48 |            1.8  |        -219379 |
| ACC10_SHORT | 12:00       | no SL     | TP 120%   |      171 |     50.88 |      820587 |      9.29 |            1.93 |        -220005 |
| ACC10_SHORT | 12:00       | no SL     | no TP     |      171 |     50.88 |      792205 |      8.97 |            1.89 |        -222440 |
| ACC10_SHORT | 15:30       | no SL     | TP 40%    |      264 |     53.41 |     1119257 |      8.21 |            1.81 |        -151701 |
| ACC10_SHORT | 15:30       | no SL     | TP 20%    |      264 |     65.91 |     1117586 |      8.2  |            2.17 |        -115308 |
| ACC10_SHORT | 15:30       | no SL     | TP 80%    |      264 |     44.7  |     1098545 |      8.06 |            1.63 |        -251620 |
| ACC10_SHORT | 12:00       | no SL     | TP 60%    |      171 |     52.05 |      703892 |      7.97 |            1.84 |        -169151 |
| ACC10_SHORT | 12:00       | no SL     | TP 80%    |      171 |     50.88 |      697938 |      7.9  |            1.79 |        -173147 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 120%   |      264 |     40.91 |     1054603 |      7.73 |            1.55 |        -269755 |

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
