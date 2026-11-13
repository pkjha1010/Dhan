# BPB BASE - SHORT (ATM put) - SL x TP x time-exit grid, entry checked all day

**Status:** PARTIAL - 119 of 167 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2025-11-13 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (10 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

BPB base SHORT: close below the 10-day low, no later close above it (pullback) -> first 1-minute cross below the lowest Low since the breakdown (full day) -> buy PUT

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:00, 15:30 = 100 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| BPB_SHORT  |                   65 |                         40 |                      4 |                        0 |            nan |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 40

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 21-21

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     9545 |   -19435 |   -19435 |    -19435 |  -19435 |
| SL 20%      |    13270 |   -15710 |   -15710 |    -15710 |  -15710 |
| SL 40%      |     9545 |   -19435 |   -19435 |    -19435 |  -19435 |
| SL 60%      |     9545 |   -19435 |   -19435 |    -19435 |  -19435 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 21-21

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     0.85 |    -1.72 |    -1.72 |     -1.72 |   -1.72 |
| SL 20%      |     1.18 |    -1.39 |    -1.39 |     -1.39 |   -1.39 |
| SL 40%      |     0.85 |    -1.72 |    -1.72 |     -1.72 |   -1.72 |
| SL 60%      |     0.85 |    -1.72 |    -1.72 |     -1.72 |   -1.72 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 21-21

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    57.14 |    52.38 |    52.38 |     52.38 |   52.38 |
| SL 20%      |    57.14 |    52.38 |    52.38 |     52.38 |   52.38 |
| SL 40%      |    57.14 |    52.38 |    52.38 |     52.38 |   52.38 |
| SL 60%      |    57.14 |    52.38 |    52.38 |     52.38 |   52.38 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 25-25

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    23174 |    14922 |    -3453 |     -3453 |   -3453 |
| SL 20%      |    13191 |   -11125 |   -29500 |    -29500 |  -29500 |
| SL 40%      |     3439 |    -4813 |   -23188 |    -23188 |  -23188 |
| SL 60%      |    -3346 |   -11598 |   -29973 |    -29973 |  -29973 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 25-25

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     1.74 |     1.12 |    -0.26 |     -0.26 |   -0.26 |
| SL 20%      |     0.99 |    -0.83 |    -2.21 |     -2.21 |   -2.21 |
| SL 40%      |     0.26 |    -0.36 |    -1.74 |     -1.74 |   -1.74 |
| SL 60%      |    -0.25 |    -0.87 |    -2.25 |     -2.25 |   -2.25 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 25-25

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |       60 |       60 |       60 |        60 |      60 |
| SL 20%      |       60 |       56 |       56 |        56 |      56 |
| SL 40%      |       60 |       60 |       60 |        60 |      60 |
| SL 60%      |       60 |       60 |       60 |        60 |      60 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 30-30

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     4768 |   -16591 |   -35591 |    -35591 |  -35591 |
| SL 20%      |   -15772 |   -62208 |   -81208 |    -81208 |  -81208 |
| SL 40%      |    -8257 |   -29616 |   -48616 |    -48616 |  -48616 |
| SL 60%      |    -9792 |   -31151 |   -50151 |    -50151 |  -50151 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 30-30

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     0.3  |    -1.03 |    -2.21 |     -2.21 |   -2.21 |
| SL 20%      |    -0.98 |    -3.85 |    -5.03 |     -5.03 |   -5.03 |
| SL 40%      |    -0.51 |    -1.84 |    -3.01 |     -3.01 |   -3.01 |
| SL 60%      |    -0.61 |    -1.93 |    -3.11 |     -3.11 |   -3.11 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 30-30

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    40    |    40    |    40    |     40    |   40    |
| SL 20%      |    36.67 |    33.33 |    33.33 |     33.33 |   33.33 |
| SL 40%      |    40    |    40    |    40    |     40    |   40    |
| SL 60%      |    40    |    40    |    40    |     40    |   40    |

## Exit 15:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 34-34

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   -34246 |   -48383 |   -87182 |    -87182 |  -87182 |
| SL 20%      |   -60799 |  -123991 |  -140804 |   -140804 | -140804 |
| SL 40%      |   -69797 |   -88094 |  -126894 |   -126894 | -126894 |
| SL 60%      |   -94753 |  -113051 |  -151850 |   -151850 | -151850 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 34-34

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    -1.86 |    -2.63 |    -4.73 |     -4.73 |   -4.73 |
| SL 20%      |    -3.3  |    -6.73 |    -7.64 |     -7.64 |   -7.64 |
| SL 40%      |    -3.79 |    -4.78 |    -6.89 |     -6.89 |   -6.89 |
| SL 60%      |    -5.14 |    -6.14 |    -8.24 |     -8.24 |   -8.24 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 34-34

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    47.06 |    44.12 |    44.12 |     44.12 |   44.12 |
| SL 20%      |    35.29 |    29.41 |    29.41 |     29.41 |   29.41 |
| SL 40%      |    44.12 |    41.18 |    41.18 |     41.18 |   41.18 |
| SL 60%      |    44.12 |    41.18 |    41.18 |     41.18 |   41.18 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 36-36

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     1773 |    -2541 |   -28049 |   -103449 | -103449 |
| SL 20%      |    -9745 |   -63553 |   -90784 |    -90784 |  -90784 |
| SL 40%      |   -13580 |   -27253 |   -65762 |    -65762 |  -65762 |
| SL 60%      |   -55882 |   -69556 |  -108064 |   -108064 | -108064 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 36-36

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     0.09 |    -0.13 |    -1.44 |     -5.3  |   -5.3  |
| SL 20%      |    -0.5  |    -3.25 |    -4.65 |     -4.65 |   -4.65 |
| SL 40%      |    -0.7  |    -1.4  |    -3.37 |     -3.37 |   -3.37 |
| SL 60%      |    -2.86 |    -3.56 |    -5.53 |     -5.53 |   -5.53 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 36-36

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    58.33 |    55.56 |    55.56 |     52.78 |   52.78 |
| SL 20%      |    47.22 |    41.67 |    41.67 |     41.67 |   41.67 |
| SL 40%      |    55.56 |    52.78 |    52.78 |     52.78 |   52.78 |
| SL 60%      |    55.56 |    52.78 |    52.78 |     52.78 |   52.78 |

## Best variant by total PnL

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT  | 10:00       | no SL     | TP 40%    |       25 |        60 |       23174 |      1.74 |            1.26 |         -50573 |

## Top 10 variants by ROI (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT  | 10:00       | no SL     | TP 40%    |       25 |     60    |       23174 |      1.74 |            1.26 |         -50573 |
| BPB_SHORT  | 09:30       | SL 20%    | TP 40%    |       21 |     57.14 |       13270 |      1.18 |            1.2  |         -26038 |
| BPB_SHORT  | 10:00       | no SL     | TP 60%    |       25 |     60    |       14922 |      1.12 |            1.17 |         -50573 |
| BPB_SHORT  | 10:00       | SL 20%    | TP 40%    |       25 |     60    |       13191 |      0.99 |            1.13 |         -56070 |
| BPB_SHORT  | 09:30       | SL 60%    | TP 40%    |       21 |     57.14 |        9545 |      0.85 |            1.13 |         -29763 |
| BPB_SHORT  | 09:30       | no SL     | TP 40%    |       21 |     57.14 |        9545 |      0.85 |            1.13 |         -29763 |
| BPB_SHORT  | 09:30       | SL 40%    | TP 40%    |       21 |     57.14 |        9545 |      0.85 |            1.13 |         -29763 |
| BPB_SHORT  | 12:00       | no SL     | TP 40%    |       30 |     40    |        4768 |      0.3  |            1.03 |         -84484 |
| BPB_SHORT  | 10:00       | SL 40%    | TP 40%    |       25 |     60    |        3439 |      0.26 |            1.03 |         -70308 |
| BPB_SHORT  | 15:30       | no SL     | TP 40%    |       36 |     58.33 |        1773 |      0.09 |            1.01 |         -68205 |

## Top 10 variants by total PnL (at least 10 trades)

| strategy   | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT  | 10:00       | no SL     | TP 40%    |       25 |     60    |       23174 |      1.74 |            1.26 |         -50573 |
| BPB_SHORT  | 10:00       | no SL     | TP 60%    |       25 |     60    |       14922 |      1.12 |            1.17 |         -50573 |
| BPB_SHORT  | 09:30       | SL 20%    | TP 40%    |       21 |     57.14 |       13270 |      1.18 |            1.2  |         -26038 |
| BPB_SHORT  | 10:00       | SL 20%    | TP 40%    |       25 |     60    |       13191 |      0.99 |            1.13 |         -56070 |
| BPB_SHORT  | 09:30       | SL 60%    | TP 40%    |       21 |     57.14 |        9545 |      0.85 |            1.13 |         -29763 |
| BPB_SHORT  | 09:30       | no SL     | TP 40%    |       21 |     57.14 |        9545 |      0.85 |            1.13 |         -29763 |
| BPB_SHORT  | 09:30       | SL 40%    | TP 40%    |       21 |     57.14 |        9545 |      0.85 |            1.13 |         -29763 |
| BPB_SHORT  | 12:00       | no SL     | TP 40%    |       30 |     40    |        4768 |      0.3  |            1.03 |         -84484 |
| BPB_SHORT  | 10:00       | SL 40%    | TP 40%    |       25 |     60    |        3439 |      0.26 |            1.03 |         -70308 |
| BPB_SHORT  | 15:30       | no SL     | TP 40%    |       36 |     58.33 |        1773 |      0.09 |            1.01 |         -68205 |

## Files in this folder

`trades_all_variants.csv.gz` (2920 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (25 trades of the best-PnL variant), `entries.csv` (one row per entry: level, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
