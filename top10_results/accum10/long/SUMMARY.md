# 10-DAY ACCUMULATION fake-break - LONG (ATM call) - SL x TP x time-exit grid

**Status:** COMPLETE - all 36 request groups finished.

**Period (entry dates):** 2025-11-13 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (10 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

close below the 10-day low (breakdown) -> within 3 days price crosses back above the 10-day high -> buy CALL

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:00, 15:30 = 100 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| ACC10_LONG |                    7 |                          7 |                      0 |                        0 |            nan |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 7

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 3-3

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -8662 |    -8662 |    -8662 |     -8662 |   -8662 |
| SL 20%      |    -8662 |    -8662 |    -8662 |     -8662 |   -8662 |
| SL 40%      |    -8662 |    -8662 |    -8662 |     -8662 |   -8662 |
| SL 60%      |    -8662 |    -8662 |    -8662 |     -8662 |   -8662 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 3-3

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     -5.5 |     -5.5 |     -5.5 |      -5.5 |    -5.5 |
| SL 20%      |     -5.5 |     -5.5 |     -5.5 |      -5.5 |    -5.5 |
| SL 40%      |     -5.5 |     -5.5 |     -5.5 |      -5.5 |    -5.5 |
| SL 60%      |     -5.5 |     -5.5 |     -5.5 |      -5.5 |    -5.5 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 3-3

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |        0 |        0 |        0 |         0 |       0 |
| SL 20%      |        0 |        0 |        0 |         0 |       0 |
| SL 40%      |        0 |        0 |        0 |         0 |       0 |
| SL 60%      |        0 |        0 |        0 |         0 |       0 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 4-4

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -21918 |   -21918 |   -21918 |    -21918 |  -21918 |
| SL 20%      |   -20942 |   -20942 |   -20942 |    -20942 |  -20942 |
| SL 40%      |   -21918 |   -21918 |   -21918 |    -21918 |  -21918 |
| SL 60%      |   -21918 |   -21918 |   -21918 |    -21918 |  -21918 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 4-4

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -10.11 |   -10.11 |   -10.11 |    -10.11 |  -10.11 |
| SL 20%      |    -9.66 |    -9.66 |    -9.66 |     -9.66 |   -9.66 |
| SL 40%      |   -10.11 |   -10.11 |   -10.11 |    -10.11 |  -10.11 |
| SL 60%      |   -10.11 |   -10.11 |   -10.11 |    -10.11 |  -10.11 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 4-4

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |        0 |        0 |        0 |         0 |       0 |
| SL 20%      |        0 |        0 |        0 |         0 |       0 |
| SL 40%      |        0 |        0 |        0 |         0 |       0 |
| SL 60%      |        0 |        0 |        0 |         0 |       0 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 7-7

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -31964 |   -31964 |   -31964 |    -31964 |  -31964 |
| SL 20%      |   -13408 |   -13408 |   -13408 |    -13408 |  -13408 |
| SL 40%      |   -31476 |   -31476 |   -31476 |    -31476 |  -31476 |
| SL 60%      |   -31964 |   -31964 |   -31964 |    -31964 |  -31964 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 7-7

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -8.54 |    -8.54 |    -8.54 |     -8.54 |   -8.54 |
| SL 20%      |    -3.58 |    -3.58 |    -3.58 |     -3.58 |   -3.58 |
| SL 40%      |    -8.41 |    -8.41 |    -8.41 |     -8.41 |   -8.41 |
| SL 60%      |    -8.54 |    -8.54 |    -8.54 |     -8.54 |   -8.54 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 7-7

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    42.86 |    42.86 |    42.86 |     42.86 |   42.86 |
| SL 20%      |    42.86 |    42.86 |    42.86 |     42.86 |   42.86 |
| SL 40%      |    42.86 |    42.86 |    42.86 |     42.86 |   42.86 |
| SL 60%      |    42.86 |    42.86 |    42.86 |     42.86 |   42.86 |

## Exit 15:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 7-7

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -30165 |   -63201 |   -63201 |    -63201 |  -63201 |
| SL 20%      |   -11464 |   -44500 |   -44500 |    -44500 |  -44500 |
| SL 40%      |   -19602 |   -52639 |   -52639 |    -52639 |  -52639 |
| SL 60%      |   -30165 |   -63201 |   -63201 |    -63201 |  -63201 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 7-7

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -8.06 |   -16.88 |   -16.88 |    -16.88 |  -16.88 |
| SL 20%      |    -3.06 |   -11.89 |   -11.89 |    -11.89 |  -11.89 |
| SL 40%      |    -5.24 |   -14.06 |   -14.06 |    -14.06 |  -14.06 |
| SL 60%      |    -8.06 |   -16.88 |   -16.88 |    -16.88 |  -16.88 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 7-7

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    28.57 |    14.29 |    14.29 |     14.29 |   14.29 |
| SL 20%      |    28.57 |    14.29 |    14.29 |     14.29 |   14.29 |
| SL 40%      |    28.57 |    14.29 |    14.29 |     14.29 |   14.29 |
| SL 60%      |    28.57 |    14.29 |    14.29 |     14.29 |   14.29 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 7-7

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -25780 |   -52404 |   -52404 |    -52404 |  -52404 |
| SL 20%      |    -6729 |   -42568 |   -42568 |    -42568 |  -42568 |
| SL 40%      |   -15542 |   -42166 |   -42166 |    -42166 |  -42166 |
| SL 60%      |   -26105 |   -52729 |   -52729 |    -52729 |  -52729 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 7-7

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -6.89 |   -14    |   -14    |    -14    |  -14    |
| SL 20%      |    -1.8  |   -11.37 |   -11.37 |    -11.37 |  -11.37 |
| SL 40%      |    -4.15 |   -11.26 |   -11.26 |    -11.26 |  -11.26 |
| SL 60%      |    -6.97 |   -14.09 |   -14.09 |    -14.09 |  -14.09 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 7-7

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    42.86 |    28.57 |    28.57 |     28.57 |   28.57 |
| SL 20%      |    42.86 |    28.57 |    28.57 |     28.57 |   28.57 |
| SL 40%      |    42.86 |    28.57 |    28.57 |     28.57 |   28.57 |
| SL 60%      |    42.86 |    28.57 |    28.57 |     28.57 |   28.57 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ACC10_LONG | 15:30       | SL 20%    | TP 40%    |        7 |     42.86 |       -6729 |      -1.8 |            0.83 |         -33562 |

## Top 10 variants by ROI (at least 10 trades)

(none yet)

## Top 10 variants by total PnL (at least 10 trades)

(none yet)

## Files in this folder

`trades_all_variants.csv.gz` (560 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (7 trades of the best-PnL variant), `entries.csv` (one row per entry: level, Acc high / low, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
