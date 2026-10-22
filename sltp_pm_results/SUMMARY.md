# SL x TP comparison - AFTERNOON (BPB SHORT, entries from 12:00)

**Status:** COMPLETE - all 985 request groups finished.

**Period (entry dates):** 2026-01-01 to 2026-10-21  |  **Stocks:** all F&O stocks with Dhan data  |  **Capital per trade:** up to Rs 60,000 (whole lots), SHORT = ATM put

## Entry rule

AFTERNOON study, SHORT, BPB.  T1: the day's first touch of the level is at/after 12:00 -> enter on it.  T2: the first touch was before 12:00 -> from 12:00 on, enter on the first candle that touches the level after >= 5 consecutive 1-minute closes above it (no missing minute).  Entries up to 15:20.

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 60%, TP 80%, TP 100%, TP 120%, no TP x time exit 15:00, 15:30 = 40 variants per strategy. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so trade counts can differ between exits.

## Entries found

| strategy                 |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |
|:-------------------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|
| BPB_SHORT_T1_FIRST_TOUCH |                  213 |                         77 |                     35 |                      136 |
| BPB_SHORT_T2_RECROSS     |                  254 |                         81 |                     40 |                      173 |
| BPB_SHORT_T1_T2_COMBINED |                  467 |                        158 |                     75 |                      309 |

`signals_with_entry` = entries found on the 1-minute stock chart; `skipped_no_option_data` / `dropped_low_coverage` = entries Dhan has no usable option candles for (they are not in any result).

## BPB_SHORT_T1_FIRST_TOUCH - exit 15:00

_T1 first touch of the day at/after 12:00_

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 35-35

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |   396884 |   369438 |    303706 |    261511 | 1588671 |
| SL 20%      |   360219 |   374253 |    320401 |    290446 |  564126 |
| SL 40%      |   336552 |   332386 |    270734 |    240779 |  502469 |
| SL 60%      |   336085 |   343439 |    277706 |    246311 | 1573471 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 35-35

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    19.94 |    18.56 |     15.26 |     13.14 |   79.82 |
| SL 20%      |    18.1  |    18.8  |     16.1  |     14.59 |   28.34 |
| SL 40%      |    16.91 |    16.7  |     13.6  |     12.1  |   25.24 |
| SL 60%      |    16.88 |    17.25 |     13.95 |     12.37 |   79.05 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 35-35

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    54.29 |    51.43 |     48.57 |     45.71 |   42.86 |
| SL 20%      |    45.71 |    42.86 |     40    |     37.14 |   34.29 |
| SL 40%      |    48.57 |    45.71 |     42.86 |     40    |   37.14 |
| SL 60%      |    51.43 |    48.57 |     45.71 |     42.86 |   40    |

## BPB_SHORT_T1_FIRST_TOUCH - exit 15:30

_T1 first touch of the day at/after 12:00_

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 42-42

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |   515950 |   425036 |    403199 |    272492 |  815801 |
| SL 20%      |   400401 |   444387 |    448080 |    338253 | 1025907 |
| SL 40%      |   372535 |   398321 |    394214 |    284387 |  960051 |
| SL 60%      |   422118 |   450324 |    442137 |    330870 |  890379 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 42-42

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    21.51 |    17.72 |     16.81 |     11.36 |   34.02 |
| SL 20%      |    16.7  |    18.53 |     18.68 |     14.1  |   42.78 |
| SL 40%      |    15.53 |    16.61 |     16.44 |     11.86 |   40.03 |
| SL 60%      |    17.6  |    18.78 |     18.44 |     13.8  |   37.13 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 42-42

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    69.05 |    64.29 |     61.9  |     57.14 |   52.38 |
| SL 20%      |    57.14 |    54.76 |     52.38 |     47.62 |   45.24 |
| SL 40%      |    59.52 |    57.14 |     54.76 |     50    |   47.62 |
| SL 60%      |    64.29 |    61.9  |     59.52 |     54.76 |   50    |

## BPB_SHORT_T2_RECROSS - exit 15:00

_T2 first touch before 12:00, re-cross after 5 closes above, from 12:00_

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 38-38

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |   112607 |   100055 |    125599 |    171436 |  259372 |
| SL 20%      |  -124079 |  -189037 |   -179117 |   -163245 |  102135 |
| SL 40%      |   -81800 |  -146759 |   -207591 |   -275621 |  -10241 |
| SL 60%      |     8088 |   -56870 |    -70950 |    -25113 |  171789 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 38-38

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |     5.28 |     4.7  |      5.89 |      8.05 |   12.17 |
| SL 20%      |    -5.82 |    -8.87 |     -8.41 |     -7.66 |    4.79 |
| SL 40%      |    -3.84 |    -6.89 |     -9.74 |    -12.93 |   -0.48 |
| SL 60%      |     0.38 |    -2.67 |     -3.33 |     -1.18 |    8.06 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 38-38

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    47.37 |    47.37 |     47.37 |     47.37 |   42.11 |
| SL 20%      |    36.84 |    34.21 |     34.21 |     34.21 |   34.21 |
| SL 40%      |    42.11 |    39.47 |     36.84 |     34.21 |   34.21 |
| SL 60%      |    44.74 |    42.11 |     42.11 |     42.11 |   39.47 |

## BPB_SHORT_T2_RECROSS - exit 15:30

_T2 first touch before 12:00, re-cross after 5 closes above, from 12:00_

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 41-41

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |   161527 |   211862 |    156286 |    202124 | -320054 |
| SL 20%      |   -90419 |  -155377 |   -145457 |   -129585 | -331385 |
| SL 40%      |   -53405 |  -118364 |   -179196 |   -247226 | -449026 |
| SL 60%      |    56873 |    -8085 |    -89365 |    -43528 | -346502 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 41-41

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |     7    |     9.18 |      6.77 |      8.76 |  -13.87 |
| SL 20%      |    -3.92 |    -6.73 |     -6.3  |     -5.62 |  -14.36 |
| SL 40%      |    -2.31 |    -5.13 |     -7.77 |    -10.72 |  -19.46 |
| SL 60%      |     2.47 |    -0.35 |     -3.87 |     -1.89 |  -15.02 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 41-41

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    48.78 |    48.78 |     46.34 |     46.34 |   34.15 |
| SL 20%      |    39.02 |    36.59 |     36.59 |     36.59 |   31.71 |
| SL 40%      |    43.9  |    41.46 |     39.02 |     36.59 |   31.71 |
| SL 60%      |    46.34 |    43.9  |     41.46 |     41.46 |   34.15 |

## BPB_SHORT_T1_T2_COMBINED - exit 15:00

_T1 or T2 (one trade per signal day)_

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 73-73

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |   509492 |   469493 |    429305 |    432947 | 1848043 |
| SL 20%      |   236141 |   185216 |    141284 |    127200 |  666260 |
| SL 40%      |   254752 |   185628 |     63143 |    -34842 |  492228 |
| SL 60%      |   344173 |   286569 |    206756 |    221198 | 1745260 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 73-73

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    12.36 |    11.39 |     10.42 |     10.51 |   44.84 |
| SL 20%      |     5.73 |     4.49 |      3.43 |      3.09 |   16.17 |
| SL 40%      |     6.18 |     4.5  |      1.53 |     -0.85 |   11.94 |
| SL 60%      |     8.35 |     6.95 |      5.02 |      5.37 |   42.35 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 73-73

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    50.68 |    49.32 |     47.95 |     46.58 |   42.47 |
| SL 20%      |    41.1  |    38.36 |     36.99 |     35.62 |   34.25 |
| SL 40%      |    45.21 |    42.47 |     39.73 |     36.99 |   35.62 |
| SL 60%      |    47.95 |    45.21 |     43.84 |     42.47 |   39.73 |

## BPB_SHORT_T1_T2_COMBINED - exit 15:30

_T1 or T2 (one trade per signal day)_

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 83-83

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |   677477 |   636898 |    559486 |    474616 |  495747 |
| SL 20%      |   309982 |   289010 |    302623 |    208668 |  694522 |
| SL 40%      |   319130 |   279957 |    215018 |     37162 |  511026 |
| SL 60%      |   478991 |   442238 |    352772 |    287342 |  543877 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 83-83

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    14.4  |    13.54 |     11.89 |     10.09 |   10.54 |
| SL 20%      |     6.59 |     6.14 |      6.43 |      4.43 |   14.76 |
| SL 40%      |     6.78 |     5.95 |      4.57 |      0.79 |   10.86 |
| SL 60%      |    10.18 |     9.4  |      7.5  |      6.11 |   11.56 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 83-83

| stop_loss   |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   no TP |
|:------------|---------:|---------:|----------:|----------:|--------:|
| no SL       |    59.04 |    56.63 |     54.22 |     51.81 |   43.37 |
| SL 20%      |    48.19 |    45.78 |     44.58 |     42.17 |   38.55 |
| SL 40%      |    51.81 |    49.4  |     46.99 |     43.37 |   39.76 |
| SL 60%      |    55.42 |    53.01 |     50.6  |     48.19 |   42.17 |

## Best variant of each strategy - by total PnL

| strategy                 | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-------------------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT_T1_FIRST_TOUCH | 15:00       | no SL     | no TP     |       35 |     42.86 |     1588671 |     79.82 |            5.01 |        -131805 |
| BPB_SHORT_T2_RECROSS     | 15:00       | no SL     | no TP     |       38 |     42.11 |      259372 |     12.17 |            1.67 |        -269686 |
| BPB_SHORT_T1_T2_COMBINED | 15:00       | no SL     | no TP     |       73 |     42.47 |     1848043 |     44.84 |            3.35 |        -346170 |

## Top 10 variants overall by ROI (at least 30 trades)

| strategy                 | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-------------------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| BPB_SHORT_T1_FIRST_TOUCH | 15:00       | no SL     | no TP     |       35 |     42.86 |     1588671 |     79.82 |            5.01 |        -131805 |
| BPB_SHORT_T1_FIRST_TOUCH | 15:00       | SL 60%    | no TP     |       35 |     40    |     1573471 |     79.05 |            4.93 |        -148157 |
| BPB_SHORT_T1_T2_COMBINED | 15:00       | no SL     | no TP     |       73 |     42.47 |     1848043 |     44.84 |            3.35 |        -346170 |
| BPB_SHORT_T1_FIRST_TOUCH | 15:30       | SL 20%    | no TP     |       42 |     45.24 |     1025907 |     42.78 |            3.99 |        -227685 |
| BPB_SHORT_T1_T2_COMBINED | 15:00       | SL 60%    | no TP     |       73 |     39.73 |     1745260 |     42.35 |            3.02 |        -391527 |
| BPB_SHORT_T1_FIRST_TOUCH | 15:30       | SL 40%    | no TP     |       42 |     47.62 |      960051 |     40.03 |            3.26 |        -254093 |
| BPB_SHORT_T1_FIRST_TOUCH | 15:30       | SL 60%    | no TP     |       42 |     50    |      890379 |     37.13 |            2.8  |        -331409 |
| BPB_SHORT_T1_FIRST_TOUCH | 15:30       | no SL     | no TP     |       42 |     52.38 |      815801 |     34.02 |            2.43 |        -376137 |
| BPB_SHORT_T1_FIRST_TOUCH | 15:00       | SL 20%    | no TP     |       35 |     34.29 |      564126 |     28.34 |            3.17 |        -167032 |
| BPB_SHORT_T1_FIRST_TOUCH | 15:00       | SL 40%    | no TP     |       35 |     37.14 |      502469 |     25.24 |            2.51 |        -217596 |

## Trade files

In `trade_files/`: `<STRATEGY>_all_variants_trades.csv` (every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `<STRATEGY>_best_trades.csv` (best-PnL variant) and `<STRATEGY>_entries.csv` (one row per entry: level, first-touch time, strike, expiry, option price).

- `BPB_SHORT_T1_FIRST_TOUCH`: best variant BPB_SHORT_T1_FIRST_TOUCH | exit 15:00 | no SL | no TP - 35 trades; 40 variants in the all-variants file
- `BPB_SHORT_T2_RECROSS`: best variant BPB_SHORT_T2_RECROSS | exit 15:00 | no SL | no TP - 38 trades; 40 variants in the all-variants file
- `BPB_SHORT_T1_T2_COMBINED`: best variant BPB_SHORT_T1_T2_COMBINED | exit 15:00 | no SL | no TP - 73 trades; 40 variants in the all-variants file

The best variant is the best of several dozen chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at `summary_by_year_top.csv`; a grid that is smooth around the winner is more believable than one isolated peak. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. Past results do not promise future results.
