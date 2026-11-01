# GAP-FADE-REVERSAL (LONG call + SHORT put) - SL x TP x time-exit grid

**Status:** PARTIAL - 4632 of 6359 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

GAP-FADE-REVERSAL.  LONG (ATM call): day i gaps up more than 1% vs the previous close and day i+1 closes below day i's close; entry = the first 1-minute candle (09:15 to 15:20) on the first day among i+2..i+4 whose High reaches day i's High.  SHORT (ATM put): day i gaps down more than 1% and day i+1 closes above day i's close; entry = first minute on the first day among i+2..i+4 that reaches day i's Low.  Option = ATM of the entry day's month, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute (the entry is never skipped for a missing option candle while any of these strikes has one).

LONG and SHORT are reported separately: `long/` and `short/` each hold their own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                 |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-------------------------------------------------------------------------------------------------------------|
| GAP_LONG   |                 2703 |                       1117 |                     57 |                      490 | Dhan returned no option candles for this period = 478; no ATM / ITM-1..ITM-3 candle at the entry minute = 12 |
| GAP_SHORT  |                 1542 |                        764 |                     49 |                      147 | Dhan returned no option candles for this period = 127; no ATM / ITM-1..ITM-3 candle at the entry minute = 20 |

## Best variant by total PnL (per direction)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 15:30       | no SL     | TP 120%   |     1041 |     47.65 |     3373938 |      6.35 |            1.63 |        -209091 |
| GAP_SHORT  | 15:30       | no SL     | no TP     |      710 |     49.44 |    41868896 |    112.83 |           11.31 |        -478911 |

## LONG - top 10 by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 12:00       | no SL     | TP 60%    |      801 |     51.44 |     2777701 |      6.82 |            1.95 |        -122678 |
| GAP_LONG   | 12:00       | no SL     | TP 120%   |      801 |     50.31 |     2767374 |      6.8  |            1.91 |        -122678 |
| GAP_LONG   | 12:00       | SL 60%    | TP 60%    |      801 |     51.44 |     2721287 |      6.68 |            1.91 |        -139904 |
| GAP_LONG   | 12:00       | SL 60%    | TP 120%   |      801 |     50.31 |     2685348 |      6.6  |            1.86 |        -124780 |
| GAP_LONG   | 15:30       | no SL     | TP 120%   |     1041 |     47.65 |     3373938 |      6.35 |            1.63 |        -209091 |
| GAP_LONG   | 15:30       | no SL     | TP 60%    |     1041 |     49.18 |     3348867 |      6.31 |            1.65 |        -175156 |
| GAP_LONG   | 10:00       | no SL     | no TP     |      593 |     52.61 |     1888190 |      6.3  |            2.08 |        -144270 |
| GAP_LONG   | 10:00       | SL 60%    | no TP     |      593 |     52.61 |     1870707 |      6.24 |            2.06 |        -144270 |
| GAP_LONG   | 10:00       | no SL     | TP 120%   |      593 |     52.61 |     1864137 |      6.22 |            2.07 |        -144270 |
| GAP_LONG   | 10:00       | SL 40%    | no TP     |      593 |     52.45 |     1853343 |      6.18 |            2.05 |        -142070 |

## SHORT - top 10 by ROI (at least 30 trades)

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

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
