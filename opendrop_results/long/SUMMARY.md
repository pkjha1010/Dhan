# OPEN-DROP RETEST - LONG (ATM call) - SL x TP x time-exit grid

**Status:** PARTIAL - 1463 of 2421 request groups finished. Results cover only the finished part. Run again to continue.

**Period (entry dates):** 2025-11-12 to 2026-11-12  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rule

first hourly candle falls > 1% (red) on day i -> a day i+1..i+3 trades <= 1% below its close -> first cross above that close on the next 1..5 days (1-minute) -> buy CALL; NIFTY50 hourly slope >= -0.5 on day i

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:00, 15:30 = 100 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found

| strategy      |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                               |
|:--------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-----------------------------------------------------------------------------------------------------------|
| OPENDROP_LONG |                 1550 |                        536 |                     30 |                       56 | Dhan returned no option candles for this period = 49; no ATM / ITM-1..ITM-3 candle at the entry minute = 7 |

## Strike used

strike_offset 0 = ATM, -n = ITM-n (the ATM series had no candle at the entry minute): -2: 1, -1: 5, 0: 530

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 309-309

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   556401 |   567228 |   612074 |    604499 |  603492 |
| SL 20%      |   511571 |   522398 |   567244 |    559669 |  558662 |
| SL 40%      |   550342 |   561170 |   606016 |    598441 |  597434 |
| SL 60%      |   560034 |   570862 |   615708 |    608133 |  607126 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 309-309

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     3.58 |     3.65 |     3.94 |      3.89 |    3.88 |
| SL 20%      |     3.29 |     3.36 |     3.65 |      3.6  |    3.59 |
| SL 40%      |     3.54 |     3.61 |     3.9  |      3.85 |    3.84 |
| SL 60%      |     3.6  |     3.67 |     3.96 |      3.91 |    3.91 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 309-309

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    53.4  |    53.07 |    53.07 |     53.07 |   53.07 |
| SL 20%      |    52.43 |    52.1  |    52.1  |     52.1  |   52.1  |
| SL 40%      |    53.4  |    53.07 |    53.07 |     53.07 |   53.07 |
| SL 60%      |    53.4  |    53.07 |    53.07 |     53.07 |   53.07 |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 354-354

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   392622 |   487858 |   555977 |    525450 |  495225 |
| SL 20%      |   417872 |   515698 |   569237 |    540870 |  510645 |
| SL 40%      |   421226 |   516462 |   584582 |    554054 |  523829 |
| SL 60%      |   386329 |   481566 |   549685 |    519157 |  488932 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 354-354

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     2.2  |     2.73 |     3.11 |      2.94 |    2.77 |
| SL 20%      |     2.34 |     2.89 |     3.19 |      3.03 |    2.86 |
| SL 40%      |     2.36 |     2.89 |     3.27 |      3.1  |    2.93 |
| SL 60%      |     2.16 |     2.7  |     3.08 |      2.91 |    2.74 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 354-354

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    50.85 |    50.56 |    50.56 |     50.56 |   50.56 |
| SL 20%      |    49.72 |    49.44 |    49.44 |     49.44 |   49.44 |
| SL 40%      |    50.85 |    50.56 |    50.56 |     50.56 |   50.56 |
| SL 60%      |    50.85 |    50.56 |    50.56 |     50.56 |   50.56 |

## Exit 12:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 426-426

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   376183 |   387895 |   518082 |    466109 |  322211 |
| SL 20%      |   328652 |   362359 |   482458 |    409425 |  269847 |
| SL 40%      |   466502 |   486950 |   617137 |    565164 |  421266 |
| SL 60%      |   397895 |   409607 |   539793 |    487821 |  343922 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 426-426

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     1.74 |     1.79 |     2.39 |      2.15 |    1.49 |
| SL 20%      |     1.52 |     1.67 |     2.23 |      1.89 |    1.25 |
| SL 40%      |     2.16 |     2.25 |     2.85 |      2.61 |    1.95 |
| SL 60%      |     1.84 |     1.89 |     2.49 |      2.25 |    1.59 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 426-426

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    46.24 |    45.31 |    45.31 |     45.31 |   45.31 |
| SL 20%      |    43.43 |    42.49 |    42.49 |     42.49 |   42.49 |
| SL 40%      |    46.24 |    45.31 |    45.31 |     45.31 |   45.31 |
| SL 60%      |    46.24 |    45.31 |    45.31 |     45.31 |   45.31 |

## Exit 15:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 492-492

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   465547 |   311405 |   453287 |    316503 |  172445 |
| SL 20%      |   454619 |   345561 |   418607 |    249909 |   83905 |
| SL 40%      |   536644 |   428766 |   570648 |    431178 |  281590 |
| SL 60%      |   426114 |   256536 |   398418 |    261634 |  117576 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 492-492

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     1.86 |     1.24 |     1.81 |      1.26 |    0.69 |
| SL 20%      |     1.81 |     1.38 |     1.67 |      1    |    0.33 |
| SL 40%      |     2.14 |     1.71 |     2.28 |      1.72 |    1.12 |
| SL 60%      |     1.7  |     1.02 |     1.59 |      1.04 |    0.47 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 492-492

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    45.93 |    43.7  |    43.29 |     42.89 |   42.68 |
| SL 20%      |    41.26 |    39.63 |    39.23 |     38.62 |   38.21 |
| SL 40%      |    45.53 |    43.5  |    43.09 |     42.68 |   42.48 |
| SL 60%      |    45.73 |    43.5  |    43.09 |     42.68 |   42.48 |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 504-504

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |   430047 |   215705 |   340010 |    245352 |   93508 |
| SL 20%      |   559833 |   423227 |   500386 |    375758 |  133875 |
| SL 40%      |   548641 |   393769 |   518762 |    427688 |  250959 |
| SL 60%      |   432627 |   207943 |   332248 |    237590 |   85746 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 504-504

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |     1.68 |     0.84 |     1.33 |      0.96 |    0.36 |
| SL 20%      |     2.18 |     1.65 |     1.95 |      1.46 |    0.52 |
| SL 40%      |     2.14 |     1.53 |     2.02 |      1.67 |    0.98 |
| SL 60%      |     1.69 |     0.81 |     1.29 |      0.93 |    0.33 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 504-504

| stop_loss   |   TP 40% |   TP 60% |   TP 80% |   TP 120% |   no TP |
|:------------|---------:|---------:|---------:|----------:|--------:|
| no SL       |    47.22 |    44.84 |    44.44 |     44.05 |   44.05 |
| SL 20%      |    43.25 |    41.07 |    40.67 |     40.08 |   39.68 |
| SL 40%      |    46.83 |    44.64 |    44.25 |     43.85 |   43.65 |
| SL 60%      |    47.02 |    44.64 |    44.25 |     43.85 |   43.85 |

## Best variant by total PnL

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 12:00       | SL 40%    | TP 80%    |      426 |     45.31 |      617137 |      2.85 |            1.33 |        -360970 |

## Top 10 variants by ROI (at least 30 trades)

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 09:30       | SL 60%    | TP 80%    |      309 |     53.07 |      615708 |      3.96 |            1.88 |        -145016 |
| OPENDROP_LONG | 09:30       | no SL     | TP 80%    |      309 |     53.07 |      612074 |      3.94 |            1.87 |        -145016 |
| OPENDROP_LONG | 09:30       | SL 60%    | TP 120%   |      309 |     53.07 |      608133 |      3.91 |            1.87 |        -145016 |
| OPENDROP_LONG | 09:30       | SL 60%    | no TP     |      309 |     53.07 |      607126 |      3.91 |            1.87 |        -145016 |
| OPENDROP_LONG | 09:30       | SL 40%    | TP 80%    |      309 |     53.07 |      606016 |      3.9  |            1.86 |        -150429 |
| OPENDROP_LONG | 09:30       | no SL     | TP 120%   |      309 |     53.07 |      604499 |      3.89 |            1.86 |        -145016 |
| OPENDROP_LONG | 09:30       | no SL     | no TP     |      309 |     53.07 |      603492 |      3.88 |            1.86 |        -145016 |
| OPENDROP_LONG | 09:30       | SL 40%    | TP 120%   |      309 |     53.07 |      598441 |      3.85 |            1.84 |        -150429 |
| OPENDROP_LONG | 09:30       | SL 40%    | no TP     |      309 |     53.07 |      597434 |      3.84 |            1.84 |        -150429 |
| OPENDROP_LONG | 09:30       | SL 60%    | TP 60%    |      309 |     53.07 |      570862 |      3.67 |            1.82 |        -145016 |

## Top 10 variants by total PnL (at least 30 trades)

| strategy      | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:--------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| OPENDROP_LONG | 12:00       | SL 40%    | TP 80%    |      426 |     45.31 |      617137 |      2.85 |            1.33 |        -360970 |
| OPENDROP_LONG | 09:30       | SL 60%    | TP 80%    |      309 |     53.07 |      615708 |      3.96 |            1.88 |        -145016 |
| OPENDROP_LONG | 09:30       | no SL     | TP 80%    |      309 |     53.07 |      612074 |      3.94 |            1.87 |        -145016 |
| OPENDROP_LONG | 09:30       | SL 60%    | TP 120%   |      309 |     53.07 |      608133 |      3.91 |            1.87 |        -145016 |
| OPENDROP_LONG | 09:30       | SL 60%    | no TP     |      309 |     53.07 |      607126 |      3.91 |            1.87 |        -145016 |
| OPENDROP_LONG | 09:30       | SL 40%    | TP 80%    |      309 |     53.07 |      606016 |      3.9  |            1.86 |        -150429 |
| OPENDROP_LONG | 09:30       | no SL     | TP 120%   |      309 |     53.07 |      604499 |      3.89 |            1.86 |        -145016 |
| OPENDROP_LONG | 09:30       | no SL     | no TP     |      309 |     53.07 |      603492 |      3.88 |            1.86 |        -145016 |
| OPENDROP_LONG | 09:30       | SL 40%    | TP 120%   |      309 |     53.07 |      598441 |      3.85 |            1.84 |        -150429 |
| OPENDROP_LONG | 09:30       | SL 40%    | no TP     |      309 |     53.07 |      597434 |      3.84 |            1.84 |        -150429 |

## Files in this folder

`trades_all_variants.csv.gz` (41700 rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` (426 trades of the best-PnL variant), `entries.csv` (one row per entry: level, setup / drop day, first-candle drop %, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. Charges, taxes and slippage are not included. Lot sizes are today's values for the whole year. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
