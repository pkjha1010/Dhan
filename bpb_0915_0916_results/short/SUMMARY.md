# BPB BASE - SHORT (ATM put) - SL x TP x time-exit grid, entry checked all day

**Status:** COMPLETE - all 4368 request groups finished.

**Period (entry dates):** 2023-10-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

BPB base SHORT: close below the 10-day low, no later close above it (pullback) -> first 1-minute cross below the lowest Low since the breakdown (full day) -> buy PUT

**Grid:** stop-loss no SL, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, no TP x time exit 09:20 = 12 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                                |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:------------------------------------------------------------------------------------------------------------|
| BPB_SHORT  |                  571 |                        488 |                     34 |                       83 | Dhan returned no option candles for this period = 64; no ATM / ITM-1..ITM-3 candle at the entry minute = 19 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 456, 1: 23, 2: 7, 3: 2

## Exit 09:20

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 451-451

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   no TP |
|:------------|---------:|---------:|---------:|--------:|
| no SL       |   643805 |   733419 |   794358 |  868743 |
| SL 40%      |   625211 |   714825 |   775764 |  850149 |
| SL 60%      |   643805 |   733419 |   794358 |  868743 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 451-451

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   no TP |
|:------------|---------:|---------:|---------:|--------:|
| no SL       |     2.73 |     3.11 |     3.37 |    3.68 |
| SL 40%      |     2.65 |     3.03 |     3.29 |    3.6  |
| SL 60%      |     2.73 |     3.11 |     3.37 |    3.68 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 451-451

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   no TP |
|:------------|---------:|---------:|---------:|--------:|
| no SL       |    46.12 |     45.9 |    45.68 |   45.68 |
| SL 40%      |    46.12 |     45.9 |    45.68 |   45.68 |
| SL 60%      |    46.12 |     45.9 |    45.68 |   45.68 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT  | 09:20       | no SL     | no TP     |      451 |     45.68 |      868743 |      3.68 |            1.71 |        -290809 |

## Top 10 variants by ROI (at least 30 trades)

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

## Top 10 variants by total PnL (at least 30 trades)

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

## Files in this folder

`trades_all_variants.csv.gz` (5412 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (451 trades of the best-PnL variant), `entries.csv` (one row per entry: level, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
