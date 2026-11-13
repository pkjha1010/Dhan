# OPEN-DROP RETEST (LONG call) - SL x TP x time-exit grid

**Status:** PARTIAL - 58 of 59 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2025-11-13 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (10 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

OPEN-DROP RETEST (LONG, ATM call).  Setup day i: the first hourly candle (09:15-10:15) is red and falls more than 1% (open to close); its close is the LEVEL.  Drop day: the first day among i+1..i+3 that trades at or below 1% under the level.  Entry day: the first day among drop day+1..+5 that trades at or above the level; entry = the first 1-minute candle (09:15 to 15:20) whose High reaches the level.  NIFTY50 filter: the NIFTY50 hourly slope (20 candles, at the first hourly candle of day i) must be >= -0.5.  Option = ATM of the entry day's month, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute (the entry is never skipped for a missing option candle while any of these strikes has one).

Everything is in `long/`: SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy      |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:--------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| OPENDROP_LONG |                   34 |                         33 |                      4 |                        0 |            nan |

## Best variant by total PnL

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 15:30       | SL 20%    | TP 80%    |       29 |     44.83 |       66244 |      4.25 |            1.47 |         -55973 |

## Top 10 by ROI (at least 10 trades)

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 15:30       | SL 20%    | TP 80%    |       29 |     44.83 |       66244 |      4.25 |            1.47 |         -55973 |
| OPENDROP_LONG | 15:30       | SL 20%    | no TP     |       29 |     44.83 |       51986 |      3.33 |            1.37 |         -55973 |
| OPENDROP_LONG | 15:30       | SL 20%    | TP 120%   |       29 |     44.83 |       51986 |      3.33 |            1.37 |         -55973 |
| OPENDROP_LONG | 15:30       | SL 20%    | TP 60%    |       29 |     44.83 |       44876 |      2.88 |            1.32 |         -55973 |
| OPENDROP_LONG | 15:00       | SL 20%    | TP 80%    |       29 |     48.28 |       35916 |      2.3  |            1.25 |         -57468 |
| OPENDROP_LONG | 15:00       | SL 20%    | no TP     |       29 |     48.28 |       27396 |      1.76 |            1.19 |         -57468 |
| OPENDROP_LONG | 15:00       | SL 20%    | TP 120%   |       29 |     48.28 |       27396 |      1.76 |            1.19 |         -57468 |
| OPENDROP_LONG | 15:00       | SL 20%    | TP 60%    |       29 |     48.28 |       19349 |      1.24 |            1.13 |         -57468 |
| OPENDROP_LONG | 15:30       | SL 20%    | TP 40%    |       29 |     44.83 |       14199 |      0.91 |            1.1  |         -55973 |
| OPENDROP_LONG | 15:30       | SL 40%    | TP 80%    |       29 |     44.83 |       10146 |      0.65 |            1.05 |         -89688 |

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
