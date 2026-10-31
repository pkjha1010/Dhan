# 5-DAY ACCUMULATION fake-break (LONG call + SHORT put) - SL x TP x time-exit grid

**Status:** PARTIAL - 4536 of 6295 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

5-DAY ACCUMULATION fake-break.  Acc_High / Acc_Low = highest High / lowest Low of the prior 5 completed days.  LONG (ATM call): a daily close below Acc_Low, then within 3 days price crosses back above Acc_High (that day's).  SHORT (ATM put): a daily close above Acc_High, then within 3 days price crosses back below Acc_Low.  Entry = the first 1-minute candle (09:15 to 15:20) that reaches the level; option = ATM, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute.

LONG and SHORT are reported separately: `long/` and `short/` each hold their own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                 |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-------------------------------------------------------------------------------------------------------------|
| ACC5_LONG  |                 2194 |                         18 |                      2 |                     1171 | Dhan returned no option candles for this period = 1163; no ATM / ITM-1..ITM-3 candle at the entry minute = 8 |
| ACC5_SHORT |                 1799 |                         37 |                      5 |                      897 | Dhan returned no option candles for this period = 894; no ATM / ITM-1..ITM-3 candle at the entry minute = 3  |

## Best variant by total PnL (per direction)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_LONG  | 15:30       | SL 60%    | TP 120%   |       16 |     37.5  |      300111 |     32.39 |            1.87 |        -182837 |
| ACC5_SHORT | 15:30       | no SL     | no TP     |       32 |     40.62 |     4668862 |    251.65 |            6.04 |        -340934 |

## LONG - top 10 by ROI (at least 30 trades)

(none yet)

## SHORT - top 10 by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC5_SHORT | 15:30       | no SL     | no TP     |       32 |     40.62 |     4668862 |    251.65 |            6.04 |        -340934 |
| ACC5_SHORT | 15:30       | SL 20%    | no TP     |       32 |     12.5  |     3974370 |    214.22 |            8.16 |        -248464 |
| ACC5_SHORT | 15:30       | SL 40%    | no TP     |       32 |     12.5  |     3766458 |    203.01 |            5.94 |        -349453 |
| ACC5_SHORT | 15:30       | SL 60%    | no TP     |       32 |     15.62 |     3667099 |    197.66 |            4.63 |        -496493 |
| ACC5_SHORT | 15:30       | no SL     | TP 120%   |       32 |     62.5  |     1579248 |     85.12 |            3.59 |        -172519 |
| ACC5_SHORT | 15:30       | no SL     | TP 80%    |       32 |     71.88 |     1388693 |     74.85 |            4.06 |        -172519 |
| ACC5_SHORT | 15:30       | no SL     | TP 40%    |       32 |     78.12 |     1286924 |     69.37 |            4.8  |        -111342 |
| ACC5_SHORT | 15:30       | no SL     | TP 60%    |       32 |     71.88 |     1248218 |     67.28 |            3.75 |        -172519 |
| ACC5_SHORT | 15:30       | no SL     | TP 20%    |       32 |     87.5  |      734406 |     39.58 |            4.76 |         -79028 |
| ACC5_SHORT | 15:30       | SL 60%    | TP 20%    |       32 |     75    |      565289 |     30.47 |            2.96 |        -114610 |

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
