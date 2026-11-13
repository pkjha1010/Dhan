# BPB BASE (LONG call + SHORT put) - SL x TP x time-exit grid, entry checked all day

**Status:** PARTIAL - 119 of 167 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2025-11-13 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (10 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

BPB BASE.  LONG (ATM call): a daily close above the 10-day high (the line); later candles must not close below the line (a bearish candle confirms the pullback); entry level = the highest High since the breakout; entry = the first 1-minute candle (09:15 to 15:20) of a later day whose High reaches the level.  SHORT (ATM put) = mirror (close below the 10-day low, lowest Low, first minute whose Low reaches it).  Option = ATM of the entry day's month, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute.  NIFTY50 filter (report): LONG only when NIFTY50 > its day open at the entry minute, SHORT only when it is below.

LONG and SHORT are reported separately: `long/` and `short/` each hold their own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| BPB_LONG   |                   50 |                         27 |                      2 |                        0 |            nan |
| BPB_SHORT  |                   65 |                         40 |                      4 |                        0 |            nan |

## Best variant by total PnL (per direction)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 15:00       | SL 20%    | TP 80%    |       25 |        40 |       35392 |      2.62 |            1.26 |         -48071 |
| BPB_SHORT  | 10:00       | no SL     | TP 40%    |       25 |        60 |       23174 |      1.74 |            1.26 |         -50573 |

## LONG (BPB_LONG) - top 10 by ROI (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 15:00       | SL 20%    | TP 80%    |       25 |     40    |       35392 |      2.62 |            1.26 |         -48071 |
| BPB_LONG   | 15:30       | SL 20%    | TP 80%    |       25 |     44    |       33812 |      2.51 |            1.24 |         -48071 |
| BPB_LONG   | 12:00       | no SL     | TP 80%    |       22 |     54.55 |       25941 |      2.14 |            1.23 |         -42499 |
| BPB_LONG   | 12:00       | no SL     | TP 120%   |       22 |     54.55 |       17916 |      1.48 |            1.16 |         -42499 |
| BPB_LONG   | 12:00       | no SL     | no TP     |       22 |     54.55 |       17916 |      1.48 |            1.16 |         -42499 |
| BPB_LONG   | 15:30       | no SL     | TP 80%    |       25 |     48    |       18286 |      1.36 |            1.11 |         -74419 |
| BPB_LONG   | 12:00       | no SL     | TP 60%    |       22 |     54.55 |       15966 |      1.32 |            1.14 |         -42499 |
| BPB_LONG   | 15:00       | no SL     | TP 80%    |       25 |     44    |       17564 |      1.3  |            1.11 |         -68066 |
| BPB_LONG   | 12:00       | no SL     | TP 40%    |       22 |     54.55 |       15746 |      1.3  |            1.14 |         -42499 |
| BPB_LONG   | 12:00       | SL 20%    | TP 80%    |       22 |     50    |       13850 |      1.14 |            1.12 |         -48071 |

## SHORT (BPB_SHORT) - top 10 by ROI (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT  | 10:00       | no SL     | TP 40%    |       25 |     60    |       23174 |      1.74 |            1.26 |         -50573 |
| BPB_SHORT  | 09:30       | SL 20%    | TP 40%    |       21 |     57.14 |       13270 |      1.18 |            1.2  |         -26038 |
| BPB_SHORT  | 10:00       | no SL     | TP 60%    |       25 |     60    |       14922 |      1.12 |            1.17 |         -50573 |
| BPB_SHORT  | 10:00       | SL 20%    | TP 40%    |       25 |     60    |       13191 |      0.99 |            1.13 |         -56070 |
| BPB_SHORT  | 09:30       | SL 60%    | TP 40%    |       21 |     57.14 |        9545 |      0.85 |            1.13 |         -29763 |
| BPB_SHORT  | 09:30       | no SL     | TP 40%    |       21 |     57.14 |        9545 |      0.85 |            1.13 |         -29763 |
| BPB_SHORT  | 09:30       | SL 40%    | TP 40%    |       21 |     57.14 |        9545 |      0.85 |            1.13 |         -29763 |
| BPB_SHORT  | 12:00       | no SL     | TP 40%    |       30 |     40    |        4768 |      0.3  |            1.03 |         -84484 |
| BPB_SHORT  | 10:00       | SL 40%    | TP 40%    |       25 |     60    |        3439 |      0.26 |            1.03 |         -70308 |
| BPB_SHORT  | 15:30       | no SL     | TP 40%    |       36 |     58.33 |        1773 |      0.09 |            1.01 |         -68205 |

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
