# GAP-FADE-REVERSAL (LONG call + SHORT put) - SL x TP x time-exit grid

**Status:** PARTIAL - 88 of 117 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2025-11-13 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (10 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

GAP-FADE-REVERSAL.  LONG (ATM call): day i gaps up more than 1% vs the previous close and day i+1 closes below day i's close; entry = the first 1-minute candle (09:15 to 15:20) on the first day among i+2..i+4 whose High reaches day i's High.  SHORT (ATM put): day i gaps down more than 1% and day i+1 closes above day i's close; entry = first minute on the first day among i+2..i+4 that reaches day i's Low.  Option = ATM of the entry day's month, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute (the entry is never skipped for a missing option candle while any of these strikes has one).

LONG and SHORT are reported separately: `long/` and `short/` each hold their own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| GAP_LONG   |                   38 |                         23 |                      2 |                        0 |            nan |
| GAP_SHORT  |                   46 |                         32 |                      3 |                        0 |            nan |

## Best variant by total PnL (per direction)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 12:00       | SL 40%    | TP 120%   |       16 |     56.25 |       97525 |     11.52 |            2.73 |         -29020 |
| GAP_SHORT  | 15:30       | no SL     | TP 60%    |       29 |     55.17 |      167480 |     10.55 |            2.29 |         -60761 |

## LONG - top 10 by ROI (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG   | 12:00       | SL 40%    | TP 120%   |       16 |     56.25 |       97525 |     11.52 |            2.73 |         -29020 |
| GAP_LONG   | 12:00       | no SL     | TP 120%   |       16 |     56.25 |       89245 |     10.54 |            2.38 |         -37300 |
| GAP_LONG   | 12:00       | SL 20%    | TP 120%   |       16 |     50    |       88062 |     10.4  |            2.52 |         -31688 |
| GAP_LONG   | 12:00       | SL 60%    | TP 120%   |       16 |     56.25 |       86965 |     10.27 |            2.3  |         -39580 |
| GAP_LONG   | 12:00       | SL 40%    | TP 80%    |       16 |     56.25 |       73893 |      8.73 |            2.31 |         -29020 |
| GAP_LONG   | 15:30       | SL 40%    | TP 120%   |       21 |     42.86 |       93477 |      8.47 |            2.05 |         -28405 |
| GAP_LONG   | 15:30       | SL 40%    | no TP     |       21 |     42.86 |       91881 |      8.33 |            2.03 |         -28405 |
| GAP_LONG   | 12:00       | no SL     | TP 80%    |       16 |     56.25 |       65613 |      7.75 |            2.01 |         -37300 |
| GAP_LONG   | 12:00       | SL 20%    | TP 80%    |       16 |     50    |       64430 |      7.61 |            2.11 |         -31688 |
| GAP_LONG   | 12:00       | SL 60%    | TP 80%    |       16 |     56.25 |       63333 |      7.48 |            1.95 |         -39580 |

## SHORT - top 10 by ROI (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT  | 15:30       | no SL     | TP 60%    |       29 |     55.17 |      167480 |     10.55 |            2.29 |         -60761 |
| GAP_SHORT  | 15:30       | no SL     | TP 80%    |       29 |     55.17 |      154022 |      9.7  |            2.18 |         -60761 |
| GAP_SHORT  | 15:00       | no SL     | TP 60%    |       28 |     53.57 |      147992 |      9.67 |            2.3  |         -69865 |
| GAP_SHORT  | 09:30       | SL 40%    | TP 60%    |       16 |     50    |       80693 |      9.27 |            2.24 |         -25384 |
| GAP_SHORT  | 15:00       | no SL     | TP 80%    |       28 |     53.57 |      139350 |      9.11 |            2.23 |         -69865 |
| GAP_SHORT  | 09:30       | SL 60%    | TP 60%    |       16 |     50    |       79191 |      9.1  |            2.19 |         -26885 |
| GAP_SHORT  | 09:30       | no SL     | TP 60%    |       16 |     50    |       79191 |      9.1  |            2.19 |         -26885 |
| GAP_SHORT  | 10:00       | no SL     | TP 60%    |       18 |     50    |       86599 |      8.88 |            2.13 |         -40238 |
| GAP_SHORT  | 15:30       | no SL     | TP 40%    |       29 |     55.17 |      120907 |      7.62 |            1.93 |         -60761 |
| GAP_SHORT  | 15:00       | no SL     | TP 40%    |       28 |     53.57 |      115945 |      7.58 |            2.02 |         -69865 |

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
