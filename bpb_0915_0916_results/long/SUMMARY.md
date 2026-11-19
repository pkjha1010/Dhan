# BPB BASE - LONG (ATM call) - SL x TP x time-exit grid, entry checked all day

**Status:** COMPLETE - all 4368 request groups finished.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

BPB base LONG: close above the 10-day high, no later close below it (pullback) -> first 1-minute cross above the highest High since the breakout (full day) -> buy CALL

**Grid:** stop-loss no SL, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, no TP x time exit 09:20 = 12 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                 |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-------------------------------------------------------------------------------------------------------------|
| BPB_LONG   |                  889 |                        689 |                     57 |                      200 | Dhan returned no option candles for this period = 190; no ATM / ITM-1..ITM-3 candle at the entry minute = 10 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): -3: 1, -2: 1, -1: 7, 0: 680

## Exit 09:20

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 627-627

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   no TP |
|:------------|---------:|---------:|---------:|--------:|
| no SL       |   819126 |   762474 |   796574 | 1175147 |
| SL 40%      |   771739 |   715087 |   749187 | 1127760 |
| SL 60%      |   763326 |   706674 |   740774 | 1119347 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 627-627

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   no TP |
|:------------|---------:|---------:|---------:|--------:|
| no SL       |     2.56 |     2.38 |     2.49 |    3.67 |
| SL 40%      |     2.41 |     2.23 |     2.34 |    3.52 |
| SL 60%      |     2.38 |     2.21 |     2.31 |    3.49 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 627-627

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   no TP |
|:------------|---------:|---------:|---------:|--------:|
| no SL       |    51.04 |    50.72 |    50.72 |   50.72 |
| SL 40%      |    51.04 |    50.72 |    50.72 |   50.72 |
| SL 60%      |    51.04 |    50.72 |    50.72 |   50.72 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_LONG   | 09:20       | no SL     | no TP     |      627 |     50.72 |     1175147 |      3.67 |            1.89 |        -139088 |

## Top 10 variants by ROI (at least 30 trades)

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

## Top 10 variants by total PnL (at least 30 trades)

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

## Files in this folder

`trades_all_variants.csv.gz` (7524 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (627 trades of the best-PnL variant), `entries.csv` (one row per entry: level, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
