# BPB BASE (LONG call + SHORT put) - SL x TP x time-exit grid, entry checked all day

**Status:** COMPLETE - all 4368 request groups finished.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

BPB BASE.  LONG (ATM call): a daily close above the 10-day high (the line); later candles must not close below the line (a bearish candle confirms the pullback); entry level = the highest High since the breakout; entry = the first 1-minute candle (09:15 to 09:16) of a later day whose High reaches the level.  SHORT (ATM put) = mirror (close below the 10-day low, lowest Low, first minute whose Low reaches it).  Option = ATM of the entry day's month, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute.  NIFTY50 filter (report): LONG only when NIFTY50 > its day open at the entry minute, SHORT only when it is below.

LONG and SHORT are reported separately: `long/` and `short/` each hold their own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                 |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-------------------------------------------------------------------------------------------------------------|
| BPB_LONG   |                  889 |                        689 |                     57 |                      200 | Dhan returned no option candles for this period = 190; no ATM / ITM-1..ITM-3 candle at the entry minute = 10 |
| BPB_SHORT  |                  571 |                        488 |                     34 |                       83 | Dhan returned no option candles for this period = 64; no ATM / ITM-1..ITM-3 candle at the entry minute = 19  |

## Best variant by total PnL (per direction)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 09:20       | no SL     | no TP     |      627 |     50.72 |     1175147 |      3.67 |            1.89 |        -139088 |
| BPB_SHORT  | 09:20       | no SL     | no TP     |      451 |     45.68 |      868743 |      3.68 |            1.71 |        -290809 |

## LONG (BPB_LONG) - top 10 by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 09:20       | no SL     | no TP     |      627 |     50.72 |     1175147 |      3.67 |            1.89 |        -139088 |
| BPB_LONG   | 09:20       | SL 40%    | no TP     |      627 |     50.72 |     1127760 |      3.52 |            1.82 |        -174595 |
| BPB_LONG   | 09:20       | SL 60%    | no TP     |      627 |     50.72 |     1119347 |      3.49 |            1.81 |        -183008 |
| BPB_LONG   | 09:20       | no SL     | TP 40%    |      627 |     51.04 |      819126 |      2.56 |            1.62 |        -139088 |
| BPB_LONG   | 09:20       | no SL     | TP 80%    |      627 |     50.72 |      796574 |      2.49 |            1.6  |        -139088 |
| BPB_LONG   | 09:20       | SL 40%    | TP 40%    |      627 |     51.04 |      771739 |      2.41 |            1.56 |        -156481 |
| BPB_LONG   | 09:20       | SL 60%    | TP 40%    |      627 |     51.04 |      763326 |      2.38 |            1.55 |        -166088 |
| BPB_LONG   | 09:20       | no SL     | TP 60%    |      627 |     50.72 |      762474 |      2.38 |            1.58 |        -139088 |
| BPB_LONG   | 09:20       | SL 40%    | TP 80%    |      627 |     50.72 |      749187 |      2.34 |            1.55 |        -174595 |
| BPB_LONG   | 09:20       | SL 60%    | TP 80%    |      627 |     50.72 |      740774 |      2.31 |            1.54 |        -183008 |

## SHORT (BPB_SHORT) - top 10 by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT  | 09:20       | no SL     | no TP     |      451 |     45.68 |      868743 |      3.68 |            1.71 |        -290809 |
| BPB_SHORT  | 09:20       | SL 60%    | no TP     |      451 |     45.68 |      868743 |      3.68 |            1.71 |        -290809 |
| BPB_SHORT  | 09:20       | SL 40%    | no TP     |      451 |     45.68 |      850149 |      3.6  |            1.69 |        -303269 |
| BPB_SHORT  | 09:20       | no SL     | TP 80%    |      451 |     45.68 |      794358 |      3.37 |            1.65 |        -284230 |
| BPB_SHORT  | 09:20       | SL 60%    | TP 80%    |      451 |     45.68 |      794358 |      3.37 |            1.65 |        -284230 |
| BPB_SHORT  | 09:20       | SL 40%    | TP 80%    |      451 |     45.68 |      775764 |      3.29 |            1.63 |        -296690 |
| BPB_SHORT  | 09:20       | no SL     | TP 60%    |      451 |     45.9  |      733419 |      3.11 |            1.6  |        -290809 |
| BPB_SHORT  | 09:20       | SL 60%    | TP 60%    |      451 |     45.9  |      733419 |      3.11 |            1.6  |        -290809 |
| BPB_SHORT  | 09:20       | SL 40%    | TP 60%    |      451 |     45.9  |      714825 |      3.03 |            1.58 |        -303269 |
| BPB_SHORT  | 09:20       | no SL     | TP 40%    |      451 |     46.12 |      643805 |      2.73 |            1.53 |        -307639 |

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
