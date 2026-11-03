# BPB BASE (LONG call + SHORT put) - SL x TP x time-exit grid, entry checked all day

**Status:** PARTIAL - 5234 of 8878 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

BPB BASE.  LONG (ATM call): a daily close above the 10-day high (the line); later candles must not close below the line (a bearish candle confirms the pullback); entry level = the highest High since the breakout; entry = the first 1-minute candle (09:15 to 15:20) of a later day whose High reaches the level.  SHORT (ATM put) = mirror (close below the 10-day low, lowest Low, first minute whose Low reaches it).  Option = ATM of the entry day's month, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute.  NIFTY50 filter (report): LONG only when NIFTY50 > its day open at the entry minute, SHORT only when it is below.

LONG and SHORT are reported separately: `long/` and `short/` each hold their own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                                                        |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| BPB_LONG   |                 3566 |                       1102 |                     73 |                      313 | Dhan returned no option candles for this period = 305; no ATM / ITM-1..ITM-3 candle at the entry minute = 8                                         |
| BPB_SHORT  |                 2404 |                        763 |                     58 |                      148 | Dhan returned no option candles for this period = 132; no ATM / ITM-1..ITM-3 candle at the entry minute = 14; no option candles after the entry = 2 |

## Best variant by total PnL (per direction)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 15:30       | no SL     | TP 120%   |     1016 |     41.54 |     2579447 |      4.89 |            1.39 |        -741369 |
| BPB_SHORT  | 15:30       | no SL     | TP 100%   |      699 |     46.49 |     4280055 |     11.5  |            1.92 |        -360884 |

## LONG (BPB_LONG) - top 10 by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 15:30       | no SL     | TP 120%   |     1016 |     41.54 |     2579447 |      4.89 |            1.39 |        -741369 |
| BPB_LONG   | 15:00       | no SL     | TP 120%   |      994 |     43.36 |     2385777 |      4.63 |            1.4  |        -598532 |
| BPB_LONG   | 15:00       | no SL     | TP 80%    |      994 |     44.16 |     2272616 |      4.41 |            1.39 |        -485284 |
| BPB_LONG   | 15:30       | no SL     | TP 100%   |     1016 |     41.54 |     2289860 |      4.34 |            1.35 |        -771693 |
| BPB_LONG   | 15:30       | no SL     | TP 80%    |     1016 |     42.42 |     2237946 |      4.25 |            1.35 |        -633649 |
| BPB_LONG   | 15:00       | no SL     | TP 100%   |      994 |     43.36 |     2027499 |      3.93 |            1.34 |        -579554 |
| BPB_LONG   | 15:00       | SL 60%    | TP 120%   |      994 |     42.86 |     2025206 |      3.93 |            1.33 |        -649345 |
| BPB_LONG   | 15:00       | no SL     | TP 60%    |      994 |     45.07 |     1930594 |      3.75 |            1.34 |        -520953 |
| BPB_LONG   | 15:00       | SL 60%    | TP 80%    |      994 |     43.66 |     1929774 |      3.74 |            1.32 |        -536097 |
| BPB_LONG   | 15:30       | no SL     | TP 60%    |     1016 |     43.11 |     1743202 |      3.31 |            1.28 |        -649807 |

## SHORT (BPB_SHORT) - top 10 by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT  | 15:30       | no SL     | TP 100%   |      699 |     46.49 |     4280055 |     11.5  |            1.92 |        -360884 |
| BPB_SHORT  | 15:30       | no SL     | TP 80%    |      699 |     47.5  |     4240204 |     11.39 |            1.95 |        -401223 |
| BPB_SHORT  | 15:30       | no SL     | TP 120%   |      699 |     45.78 |     4131955 |     11.1  |            1.86 |        -349151 |
| BPB_SHORT  | 15:30       | SL 60%    | TP 120%   |      699 |     44.92 |     3554955 |      9.55 |            1.71 |        -344003 |
| BPB_SHORT  | 15:30       | no SL     | TP 60%    |      699 |     48.21 |     3529158 |      9.48 |            1.8  |        -403587 |
| BPB_SHORT  | 15:30       | SL 60%    | TP 80%    |      699 |     46.49 |     3528472 |      9.48 |            1.75 |        -396076 |
| BPB_SHORT  | 15:30       | SL 60%    | TP 100%   |      699 |     45.49 |     3524552 |      9.47 |            1.72 |        -355737 |
| BPB_SHORT  | 15:30       | SL 40%    | TP 120%   |      699 |     43.92 |     3425729 |      9.2  |            1.71 |        -356172 |
| BPB_SHORT  | 15:30       | SL 40%    | TP 100%   |      699 |     44.35 |     3322299 |      8.92 |            1.7  |        -356172 |
| BPB_SHORT  | 15:30       | no SL     | no TP     |      699 |     44.49 |     3292636 |      8.84 |            1.65 |        -628310 |

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
