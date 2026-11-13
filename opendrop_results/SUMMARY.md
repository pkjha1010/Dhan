# OPEN-DROP RETEST (LONG call) - SL x TP x time-exit grid

**Status:** PARTIAL - 1414 of 2421 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2025-11-12 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

OPEN-DROP RETEST (LONG, ATM call).  Setup day i: the first hourly candle (09:15-10:15) is red and falls more than 1% (open to close); its close is the LEVEL.  Drop day: the first day among i+1..i+3 that trades at or below 1% under the level.  Entry day: the first day among drop day+1..+5 that trades at or above the level; entry = the first 1-minute candle (09:15 to 15:20) whose High reaches the level.  NIFTY50 filter: the NIFTY50 hourly slope (20 candles, at the first hourly candle of day i) must be >= -0.5.  Option = ATM of the entry day's month, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute (the entry is never skipped for a missing option candle while any of these strikes has one).

Everything is in `long/`: SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.

## Entries found

| strategy      |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                               |
|:--------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-----------------------------------------------------------------------------------------------------------|
| OPENDROP_LONG |                 1550 |                        488 |                     26 |                       55 | Dhan returned no option candles for this period = 48; no ATM / ITM-1..ITM-3 candle at the entry minute = 7 |

## Best variant by total PnL

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 12:00       | SL 40%    | TP 80%    |      388 |     46.91 |      796784 |      4.05 |            1.49 |        -297996 |

## Top 10 by ROI (at least 30 trades)

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 09:30       | SL 60%    | TP 80%    |      280 |     53.93 |      617802 |      4.4  |            1.99 |        -124094 |
| OPENDROP_LONG | 09:30       | SL 40%    | TP 80%    |      280 |     53.93 |      613906 |      4.37 |            1.98 |        -123712 |
| OPENDROP_LONG | 09:30       | no SL     | TP 80%    |      280 |     53.93 |      614168 |      4.37 |            1.98 |        -124094 |
| OPENDROP_LONG | 09:30       | SL 60%    | no TP     |      280 |     53.93 |      609219 |      4.34 |            1.98 |        -124094 |
| OPENDROP_LONG | 09:30       | SL 60%    | TP 120%   |      280 |     53.93 |      610227 |      4.34 |            1.98 |        -124094 |
| OPENDROP_LONG | 09:30       | no SL     | TP 120%   |      280 |     53.93 |      606593 |      4.32 |            1.97 |        -124094 |
| OPENDROP_LONG | 09:30       | no SL     | no TP     |      280 |     53.93 |      605586 |      4.31 |            1.97 |        -124094 |
| OPENDROP_LONG | 09:30       | SL 40%    | TP 120%   |      280 |     53.93 |      606331 |      4.31 |            1.97 |        -123712 |
| OPENDROP_LONG | 09:30       | SL 40%    | no TP     |      280 |     53.93 |      605323 |      4.31 |            1.97 |        -123712 |
| OPENDROP_LONG | 10:00       | SL 40%    | TP 80%    |      320 |     51.56 |      684106 |      4.25 |            1.68 |        -147608 |

The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.
