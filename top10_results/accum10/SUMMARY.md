# 10-DAY ACCUMULATION fake-break (LONG call + SHORT put) - SL x TP x time-exit grid

**Status:** COMPLETE - all 36 request groups finished.

**Period (entry dates):** 2025-11-13 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (10 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

10-DAY ACCUMULATION fake-break.  Acc_High / Acc_Low = highest High / lowest Low of the prior 10 completed days.  LONG (ATM call): a daily close below Acc_Low, then within 3 days price crosses back above Acc_High (that day's).  SHORT (ATM put): a daily close above Acc_High, then within 3 days price crosses back below Acc_Low.  Entry = the first 1-minute candle (09:15 to 15:20) that reaches the level; option = ATM, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute.

LONG and SHORT are reported separately: `long/` and `short/` each hold their own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy    |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| ACC10_LONG  |                    7 |                          7 |                      0 |                        0 |            nan |
| ACC10_SHORT |                   11 |                         11 |                      1 |                        0 |            nan |

## Best variant by total PnL (per direction)

| strategy    | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_LONG  | 15:30       | SL 20%    | TP 40%    |        7 |     42.86 |       -6729 |     -1.8  |            0.83 |         -33562 |
| ACC10_SHORT | 15:30       | SL 60%    | TP 80%    |       10 |     30    |       11799 |      2.19 |            1.22 |         -38914 |

## LONG - top 10 by ROI (at least 10 trades)

(none yet)

## SHORT - top 10 by ROI (at least 10 trades)

| strategy    | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_SHORT | 15:30       | SL 60%    | TP 80%    |       10 |        30 |       11799 |      2.19 |            1.22 |         -38914 |
| ACC10_SHORT | 15:30       | no SL     | TP 80%    |       10 |        30 |       11799 |      2.19 |            1.22 |         -38914 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 80%    |       10 |        30 |       11334 |      2.11 |            1.21 |         -39379 |
| ACC10_SHORT | 15:30       | no SL     | TP 120%   |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | SL 60%    | TP 120%   |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | no SL     | no TP     |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | SL 60%    | no TP     |       10 |        30 |        5861 |      1.09 |            1.11 |         -38914 |
| ACC10_SHORT | 15:30       | SL 40%    | TP 120%   |       10 |        30 |        5396 |      1    |            1.1  |         -39379 |
| ACC10_SHORT | 15:30       | SL 40%    | no TP     |       10 |        30 |        5396 |      1    |            1.1  |         -39379 |
| ACC10_SHORT | 15:30       | no SL     | TP 60%    |       10 |        30 |         -76 |     -0.01 |            1    |         -38914 |

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
