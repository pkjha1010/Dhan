# PULLBACK re-cross on options - Dhan data - LONG and SHORT reported separately

**Status:** COMPLETE  |  2023-11-03 .. 2026-11-03  |  Nifty filter: intraday  |  Cap Rs 60,000

LONG = breakout above the 10-day high, pullback, re-cross up -> buy the CALL (Nifty must be green).  SHORT = breakdown below the 10-day low, bounce, re-cross down -> buy the PUT (Nifty must be red).  ATM at the entry minute (else nearest ITM), strike locked, fill = close of the entry-minute option candle.

## LONG (calls) - 1838 entries

### Entries skipped / diagnostics

```
{
 "no_equity_id": 0,
 "too_little_daily": 0,
 "no_stock_minute_data": 20,
 "no_cross_minute": 198,
 "no_nifty_minute_data": 0,
 "nifty_filter_failed": 1596,
 "no_option_candle_atm_or_itm": 684,
 "no_lot_size": 0,
 "one_lot_too_expensive": 18,
 "premium_below_min": 37
}
```

### Top 15 variants by ROI (>= 30 trades)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| 10:00       | no SL     | no TP     |     1168 |     48.46 | 2.75059e+06 |      4.59 |            1.64 |        -197909 |
| 10:00       | SL 60%    | no TP     |     1168 |     48.46 | 2.71734e+06 |      4.53 |            1.63 |        -199864 |
| 12:00       | no SL     | no TP     |     1510 |     45.1  | 3.46623e+06 |      4.47 |            1.45 |        -261248 |
| 12:00       | no SL     | TP 120%   |     1510 |     45.3  | 3.46063e+06 |      4.46 |            1.45 |        -262737 |
| 10:00       | SL 40%    | no TP     |     1168 |     48.12 | 2.57856e+06 |      4.3  |            1.59 |        -177291 |
| 12:00       | no SL     | TP 40%    |     1510 |     48.61 | 3.18815e+06 |      4.11 |            1.47 |        -209422 |
| 12:00       | no SL     | TP 60%    |     1510 |     46.29 | 3.01388e+06 |      3.88 |            1.41 |        -236852 |
| 12:00       | SL 60%    | no TP     |     1510 |     44.77 | 3.00601e+06 |      3.87 |            1.37 |        -255346 |
| 12:00       | SL 60%    | TP 120%   |     1510 |     44.97 | 2.97774e+06 |      3.84 |            1.37 |        -255346 |
| 12:00       | SL 40%    | no TP     |     1510 |     44.24 | 2.92555e+06 |      3.77 |            1.37 |        -253270 |
| 10:00       | no SL     | TP 80%    |     1168 |     48.63 | 2.245e+06   |      3.75 |            1.53 |        -197909 |
| 12:00       | no SL     | TP 80%    |     1510 |     45.56 | 2.91347e+06 |      3.75 |            1.39 |        -278460 |
| 10:00       | SL 20%    | no TP     |     1168 |     45.63 | 2.22473e+06 |      3.71 |            1.51 |        -186314 |
| 10:00       | SL 60%    | TP 80%    |     1168 |     48.63 | 2.21219e+06 |      3.69 |            1.51 |        -199864 |
| 10:00       | no SL     | TP 120%   |     1168 |     48.46 | 2.19512e+06 |      3.66 |            1.51 |        -197909 |

### Best variant per time exit (by ROI)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| 10:00       | no SL     | no TP     |     1168 |     48.46 | 2.75059e+06 |      4.59 |            1.64 |        -197909 |
| 12:00       | no SL     | no TP     |     1510 |     45.1  | 3.46623e+06 |      4.47 |            1.45 |        -261248 |
| 09:30       | no SL     | no TP     |      980 |     47.86 | 1.70174e+06 |      3.39 |            1.63 |        -161651 |
| 15:30       | no SL     | TP 120%   |     1838 |     40.86 | 2.81618e+06 |      2.97 |            1.22 |        -610202 |

### Best variant by PnL: 12:00 | no SL | no TP - by year

|   year |   trades |              pnl |
|-------:|---------:|-----------------:|
|   2023 |      134 | 436964           |
|   2024 |      420 | 369010           |
|   2025 |      517 |      1.47329e+06 |
|   2026 |      439 |      1.18696e+06 |

## SHORT (puts) - 1498 entries

### Entries skipped / diagnostics

```
{
 "no_equity_id": 0,
 "too_little_daily": 0,
 "no_stock_minute_data": 2,
 "no_cross_minute": 381,
 "no_nifty_minute_data": 0,
 "nifty_filter_failed": 1013,
 "no_option_candle_atm_or_itm": 513,
 "no_lot_size": 0,
 "one_lot_too_expensive": 11,
 "premium_below_min": 58
}
```

### Top 15 variants by ROI (>= 30 trades)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |      max_drawdown |
|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|------------------:|
| 15:30       | no SL     | TP 120%   |     1498 |     47.86 | 7.90001e+06 |      9.94 |            1.8  | -488640           |
| 15:30       | no SL     | no TP     |     1498 |     46.4  | 7.86352e+06 |      9.89 |            1.74 | -953428           |
| 15:30       | no SL     | TP 80%    |     1498 |     48.53 | 6.68511e+06 |      8.41 |            1.7  | -471081           |
| 15:30       | no SL     | TP 60%    |     1498 |     49.33 | 5.99827e+06 |      7.55 |            1.64 | -469658           |
| 15:30       | no SL     | TP 40%    |     1498 |     52.6  | 4.96675e+06 |      6.25 |            1.58 | -283797           |
| 15:30       | SL 60%    | TP 120%   |     1498 |     46.13 | 4.37701e+06 |      5.51 |            1.41 | -896830           |
| 15:30       | SL 60%    | TP 80%    |     1498 |     47    | 4.15842e+06 |      5.23 |            1.4  | -679366           |
| 15:30       | SL 60%    | TP 60%    |     1498 |     48    | 3.96536e+06 |      4.99 |            1.4  | -570667           |
| 15:30       | SL 60%    | TP 40%    |     1498 |     51.4  | 3.72036e+06 |      4.68 |            1.4  | -388508           |
| 15:30       | SL 40%    | TP 120%   |     1498 |     44.46 | 3.35841e+06 |      4.23 |            1.32 | -693181           |
| 15:30       | SL 60%    | no TP     |     1498 |     44.93 | 3.32343e+06 |      4.18 |            1.3  |      -1.20038e+06 |
| 15:30       | SL 40%    | TP 80%    |     1498 |     45.26 | 3.20907e+06 |      4.04 |            1.31 | -612123           |
| 15:30       | SL 40%    | TP 60%    |     1498 |     46.4  | 3.19501e+06 |      4.02 |            1.32 | -523374           |
| 15:30       | SL 40%    | TP 40%    |     1498 |     49.8  | 3.10734e+06 |      3.91 |            1.34 | -322715           |
| 15:30       | SL 40%    | no TP     |     1498 |     43.39 | 3.01124e+06 |      3.79 |            1.28 | -990398           |

### Best variant per time exit (by ROI)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |        total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:----------|:----------|---------:|----------:|-----------------:|----------:|----------------:|---------------:|
| 15:30       | no SL     | TP 120%   |     1498 |     47.86 |      7.90001e+06 |      9.94 |            1.8  |        -488640 |
| 10:00       | no SL     | TP 80%    |      808 |     50.12 |      1.23625e+06 |      2.9  |            1.37 |        -460658 |
| 12:00       | no SL     | TP 40%    |     1124 |     49.29 |      1.60836e+06 |      2.71 |            1.27 |        -523179 |
| 09:30       | SL 20%    | TP 80%    |      627 |     52.31 | 834991           |      2.54 |            1.44 |        -123989 |

### Best variant by PnL: 15:30 | no SL | TP 120% - by year

|   year |   trades |             pnl |
|-------:|---------:|----------------:|
|   2023 |        5 | 58086           |
|   2024 |      318 |     1.8144e+06  |
|   2025 |      510 |     2.94768e+06 |
|   2026 |      665 |     3.07985e+06 |

The best of 80 variants is chosen after seeing the results, so it is optimistic: check that neighbouring variants and every year look similar. Charges and slippage are not included; option candles with no trade in a minute are missing, so illiquid-stock fills can be better than real. Files per side: summary_<SIDE>.csv, all_trades_<SIDE>.csv.gz, entries_<SIDE>.csv, best_variant_trades_<SIDE>.csv.