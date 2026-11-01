# GAP-FADE-REVERSAL (LONG call + SHORT put) - SL x TP x time-exit grid

**Status:** COMPLETE - all 6359 request groups finished.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

GAP-FADE-REVERSAL.  LONG (ATM call): day i gaps up more than 1% vs the previous close and day i+1 closes below day i's close; entry = the first 1-minute candle (09:15 to 15:20) on the first day among i+2..i+4 whose High reaches day i's High.  SHORT (ATM put): day i gaps down more than 1% and day i+1 closes above day i's close; entry = first minute on the first day among i+2..i+4 that reaches day i's Low.  Option = ATM of the entry day's month, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute (the entry is never skipped for a missing option candle while any of these strikes has one).

LONG and SHORT are reported separately: `long/` and `short/` each hold their own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                                                        |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| GAP_LONG   |                 2703 |                       1840 |                    130 |                      863 | Dhan returned no option candles for this period = 838; no ATM / ITM-1..ITM-3 candle at the entry minute = 23; no option candles after the entry = 2 |
| GAP_SHORT  |                 1542 |                       1254 |                     80 |                      288 | Dhan returned no option candles for this period = 251; no ATM / ITM-1..ITM-3 candle at the entry minute = 37                                        |

## Best variant by total PnL (per direction)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 15:30       | no SL     | TP 80%    |     1687 |     47.72 |     5675739 |      6.61 |            1.66 |        -317105 |
| GAP_SHORT  | 15:30       | no SL     | no TP     |     1169 |     50.98 |    44552760 |     73.13 |            7.75 |        -725247 |

## LONG - top 10 by ROI (at least 30 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 15:30       | no SL     | TP 80%    |     1687 |     47.72 |     5675739 |      6.61 |            1.66 |        -317105 |
| GAP_LONG   | 15:30       | no SL     | TP 120%   |     1687 |     47.07 |     5627947 |      6.56 |            1.64 |        -366690 |
| GAP_LONG   | 15:30       | no SL     | TP 60%    |     1687 |     48.61 |     5518495 |      6.43 |            1.66 |        -251742 |
| GAP_LONG   | 15:30       | SL 60%    | TP 80%    |     1687 |     47.48 |     5354997 |      6.24 |            1.62 |        -295095 |
| GAP_LONG   | 12:00       | no SL     | TP 60%    |     1291 |     50.74 |     4017398 |      6.14 |            1.83 |        -145680 |
| GAP_LONG   | 15:30       | SL 60%    | TP 60%    |     1687 |     48.37 |     5198547 |      6.06 |            1.62 |        -234738 |
| GAP_LONG   | 12:00       | no SL     | TP 120%   |     1291 |     49.57 |     3939330 |      6.02 |            1.78 |        -174864 |
| GAP_LONG   | 15:30       | SL 60%    | TP 120%   |     1687 |     46.77 |     5124433 |      5.97 |            1.58 |        -344680 |
| GAP_LONG   | 15:30       | no SL     | TP 40%    |     1687 |     51.04 |     5004529 |      5.83 |            1.65 |        -194494 |
| GAP_LONG   | 15:30       | no SL     | no TP     |     1687 |     46.41 |     4987066 |      5.81 |            1.56 |        -474420 |

## SHORT - top 10 by ROI (at least 30 trades)

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

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
