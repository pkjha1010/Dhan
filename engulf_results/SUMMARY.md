# GREEN ENGULFING breakout (LONG, ATM call) - SL x TP x time-exit grid

**Status:** COMPLETE - all 467 request groups finished.

**Period (entry dates):** 2024-10-27 to 2026-10-23  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

## Rules

GREEN ENGULFING breakout, LONG, ATM call (ITM fallback up to ITM-3).  Green candle engulfing a non-green candle at the 10-day high; next 5 days: no close below the engulfing low and at least one close inside its body; level = highest High from the engulfing candle to the end of the pullback; entry = first 1-minute High >= level (09:15 to 15:20); a daily close below the engulfing low while waiting cancels the setup; no limit on the waiting time.

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 20%, TP 40%, TP 60%, TP 80%, TP 100%, TP 120%, TP 200% x time exit 09:30, 10:00, 15:30 = 84 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the 09:30 and 10:00 exits have fewer trades than 15:30.

## Entries found

| strategy          |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                               |
|:------------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-----------------------------------------------------------------------------------------------------------|
| GREEN_ENGULF_LONG |                  235 |                        200 |                     90 |                       35 | Dhan returned no option candles for this period = 27; no ATM / ITM-1..ITM-3 candle at the entry minute = 8 |

## Strike used

strike_offset 0 = ATM, -n = ITM-n (the ATM series had no candle at the entry minute): 0: 200

## Exit 09:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 40-40

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   TP 200% |
|:------------|---------:|---------:|---------:|---------:|----------:|----------:|----------:|
| no SL       |   185298 |   226336 |   230979 |   265934 |    229102 |    183683 |    150615 |
| SL 20%      |   148730 |   185588 |   179128 |   214082 |    178976 |    133557 |    100489 |
| SL 40%      |   185298 |   226336 |   230979 |   265934 |    219214 |    173794 |    140726 |
| SL 60%      |   185298 |   226336 |   230979 |   265934 |    229102 |    183683 |    150615 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 40-40

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   TP 200% |
|:------------|---------:|---------:|---------:|---------:|----------:|----------:|----------:|
| no SL       |     8.71 |    10.64 |    10.85 |    12.5  |     10.77 |      8.63 |      7.08 |
| SL 20%      |     6.99 |     8.72 |     8.42 |    10.06 |      8.41 |      6.28 |      4.72 |
| SL 40%      |     8.71 |    10.64 |    10.85 |    12.5  |     10.3  |      8.17 |      6.61 |
| SL 60%      |     8.71 |    10.64 |    10.85 |    12.5  |     10.77 |      8.63 |      7.08 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 40-40

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   TP 200% |
|:------------|---------:|---------:|---------:|---------:|----------:|----------:|----------:|
| no SL       |     62.5 |       60 |     57.5 |     57.5 |      55   |      55   |      55   |
| SL 20%      |     57.5 |       55 |     50   |     50   |      47.5 |      47.5 |      47.5 |
| SL 40%      |     62.5 |       60 |     57.5 |     57.5 |      55   |      55   |      55   |
| SL 60%      |     62.5 |       60 |     57.5 |     57.5 |      55   |      55   |      55   |

## Exit 10:00

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 60-60

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   TP 200% |
|:------------|---------:|---------:|---------:|---------:|----------:|----------:|----------:|
| no SL       |   247756 |   368565 |   400724 |   437868 |    410167 |    406039 |    350011 |
| SL 20%      |   167519 |   210430 |   263553 |   300697 |    272184 |    268056 |    212028 |
| SL 40%      |   245506 |   320335 |   353539 |   390683 |    350556 |    346427 |    290399 |
| SL 60%      |   235156 |   298490 |   331694 |   368838 |    341137 |    337009 |    280981 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 60-60

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   TP 200% |
|:------------|---------:|---------:|---------:|---------:|----------:|----------:|----------:|
| no SL       |     7.83 |    11.65 |    12.67 |    13.84 |     12.97 |     12.84 |     11.07 |
| SL 20%      |     5.3  |     6.65 |     8.33 |     9.51 |      8.61 |      8.48 |      6.7  |
| SL 40%      |     7.76 |    10.13 |    11.18 |    12.35 |     11.08 |     10.95 |      9.18 |
| SL 60%      |     7.44 |     9.44 |    10.49 |    11.66 |     10.79 |     10.66 |      8.88 |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 60-60

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   TP 200% |
|:------------|---------:|---------:|---------:|---------:|----------:|----------:|----------:|
| no SL       |       60 |    55    |    53.33 |    53.33 |     51.67 |     51.67 |     51.67 |
| SL 20%      |       55 |    48.33 |    46.67 |    46.67 |     45    |     45    |     45    |
| SL 40%      |       60 |    53.33 |    51.67 |    51.67 |     50    |     50    |     50    |
| SL 60%      |       60 |    53.33 |    51.67 |    51.67 |     50    |     50    |     50    |

## Exit 15:30

**Total PnL (Rs)** (rows stop-loss, columns target)  -  trades per variant: 107-107

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   TP 200% |
|:------------|---------:|---------:|---------:|---------:|----------:|----------:|----------:|
| no SL       |   313780 |   544920 |   642773 |   744302 |    972107 |    792364 |    876861 |
| SL 20%      |   203945 |   296983 |   332207 |   357700 |    312797 |    160824 |    -25964 |
| SL 40%      |   219048 |   352195 |   340431 |   383299 |    317781 |    144182 |    -84548 |
| SL 60%      |   163303 |   289407 |   253812 |   284680 |    198548 |      2779 |   -251564 |

**ROI % on capital used** (rows stop-loss, columns target)  -  trades per variant: 107-107

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   TP 200% |
|:------------|---------:|---------:|---------:|---------:|----------:|----------:|----------:|
| no SL       |     5.49 |     9.53 |    11.24 |    13.02 |     17    |     13.86 |     15.34 |
| SL 20%      |     3.57 |     5.19 |     5.81 |     6.26 |      5.47 |      2.81 |     -0.45 |
| SL 40%      |     3.83 |     6.16 |     5.95 |     6.7  |      5.56 |      2.52 |     -1.48 |
| SL 60%      |     2.86 |     5.06 |     4.44 |     4.98 |      3.47 |      0.05 |     -4.4  |

**Win %** (rows stop-loss, columns target)  -  trades per variant: 107-107

| stop_loss   |   TP 20% |   TP 40% |   TP 60% |   TP 80% |   TP 100% |   TP 120% |   TP 200% |
|:------------|---------:|---------:|---------:|---------:|----------:|----------:|----------:|
| no SL       |    68.22 |    60.75 |    56.07 |    54.21 |     53.27 |     50.47 |     46.73 |
| SL 20%      |    57.01 |    48.6  |    43.93 |    42.06 |     40.19 |     37.38 |     35.51 |
| SL 40%      |    64.49 |    56.07 |    50.47 |    48.6  |     46.73 |     43.93 |     42.06 |
| SL 60%      |    64.49 |    56.07 |    50.47 |    48.6  |     46.73 |     43.93 |     42.06 |

## Best variant by total PnL

| strategy          | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GREEN_ENGULF_LONG | 15:30       | no SL     | TP 100%   |      107 |     53.27 |      972107 |        17 |            2.21 |        -138562 |

## Top 10 variants by ROI (at least 30 trades)

| strategy          | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GREEN_ENGULF_LONG | 15:30       | no SL     | TP 100%   |      107 |     53.27 |      972107 |     17    |            2.21 |        -138562 |
| GREEN_ENGULF_LONG | 15:30       | no SL     | TP 200%   |      107 |     46.73 |      876861 |     15.34 |            1.77 |        -290458 |
| GREEN_ENGULF_LONG | 15:30       | no SL     | TP 120%   |      107 |     50.47 |      792364 |     13.86 |            1.86 |        -176050 |
| GREEN_ENGULF_LONG | 10:00       | no SL     | TP 80%    |       60 |     53.33 |      437868 |     13.84 |            3.92 |         -33800 |
| GREEN_ENGULF_LONG | 15:30       | no SL     | TP 80%    |      107 |     54.21 |      744302 |     13.02 |            1.99 |        -138562 |
| GREEN_ENGULF_LONG | 10:00       | no SL     | TP 100%   |       60 |     51.67 |      410167 |     12.97 |            3.55 |         -33800 |
| GREEN_ENGULF_LONG | 10:00       | no SL     | TP 120%   |       60 |     51.67 |      406039 |     12.84 |            3.53 |         -33800 |
| GREEN_ENGULF_LONG | 10:00       | no SL     | TP 60%    |       60 |     53.33 |      400724 |     12.67 |            3.67 |         -33800 |
| GREEN_ENGULF_LONG | 09:30       | SL 60%    | TP 80%    |       40 |     57.5  |      265934 |     12.5  |            4.01 |         -34877 |
| GREEN_ENGULF_LONG | 09:30       | no SL     | TP 80%    |       40 |     57.5  |      265934 |     12.5  |            4.01 |         -34877 |

## Trade files

In `trade_files/`: `GREEN_ENGULF_LONG_all_variants_trades.csv` (every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none), `..._best_trades.csv` (best-PnL variant) and `..._entries.csv` (one row per entry: level, engulfing date, pullback end, engulfing low, strike, expiry, option price).

- `GREEN_ENGULF_LONG`: best variant GREEN_ENGULF_LONG | exit 15:30 | no SL | TP 100% - 107 trades; 84 variants in the all-variants file

The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at `summary_by_year_top.csv`. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
