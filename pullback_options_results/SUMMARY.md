# PULLBACK re-cross on options - Dhan data - LONG and SHORT reported separately

**Status:** COMPLETE  |  2023-11-03 .. 2026-11-03  |  Nifty filter: intraday  |  Cap Rs 60,000

LONG = breakout above the 10-day high, pullback, re-cross up -> buy the CALL (Nifty must be green).  SHORT = breakdown below the 10-day low, bounce, re-cross down -> buy the PUT (Nifty must be red).  ATM at the entry minute (else nearest ITM), strike locked, fill = close of the entry-minute option candle.

## LONG (calls) - 1875 entries

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
 "one_lot_too_expensive": 18
}
```

### Top 15 variants by ROI (>= 30 trades)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |      max_drawdown |
|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|------------------:|
| 15:30       | no SL     | no TP     |     1875 |     40.48 | 5.51837e+08 |    569.26 |           31.08 | -492629           |
| 15:30       | no SL     | TP 120%   |     1875 |     41.71 | 5.3768e+08  |    554.66 |           31.31 | -388316           |
| 15:30       | no SL     | TP 80%    |     1875 |     43.36 | 5.35753e+08 |    552.67 |           32.31 | -402017           |
| 15:30       | no SL     | TP 60%    |     1875 |     45.23 | 5.32255e+08 |    549.06 |           33.7  | -396795           |
| 15:30       | no SL     | TP 40%    |     1875 |     49.87 | 5.30575e+08 |    547.33 |           37.54 | -422690           |
| 15:30       | SL 60%    | TP 80%    |     1875 |     40.21 | 5.15185e+08 |    531.45 |           28.97 |      -1.58216e+06 |
| 15:30       | SL 60%    | TP 120%   |     1875 |     38.35 | 5.15e+08    |    531.26 |           27.78 |      -1.64402e+06 |
| 15:30       | SL 60%    | TP 60%    |     1875 |     42.4  | 5.14898e+08 |    531.16 |           30.4  | -997541           |
| 15:30       | SL 60%    | TP 40%    |     1875 |     47.09 | 5.14868e+08 |    531.12 |           33.2  |      -1.02952e+06 |
| 15:30       | SL 60%    | no TP     |     1875 |     36.53 | 5.0505e+08  |    521    |           25.99 |      -1.60378e+06 |
| 15:30       | SL 20%    | TP 40%    |     1875 |     35.73 | 4.86289e+08 |    501.64 |           39.54 | -728394           |
| 15:30       | SL 40%    | TP 80%    |     1875 |     38.35 | 4.86254e+08 |    501.61 |           28.86 |      -1.46359e+06 |
| 15:30       | SL 40%    | TP 60%    |     1875 |     40.64 | 4.86234e+08 |    501.59 |           30.15 | -873924           |
| 15:30       | SL 20%    | TP 60%    |     1875 |     31.57 | 4.86216e+08 |    501.57 |           37.24 | -700899           |
| 15:30       | SL 40%    | TP 40%    |     1875 |     45.28 | 4.86207e+08 |    501.56 |           32.47 | -903751           |

### Best variant per time exit (by ROI)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| 15:30       | no SL     | no TP     |     1875 |     40.48 | 5.51837e+08 |    569.26 |           31.08 |        -492629 |
| 12:00       | no SL     | no TP     |     1533 |     42.92 | 3.90841e+07 |     49.57 |            4.07 |        -476132 |
| 10:00       | no SL     | no TP     |     1186 |     46.04 | 2.99114e+07 |     49.14 |            4.72 |        -379774 |
| 09:30       | no SL     | no TP     |      994 |     46.88 | 2.08088e+07 |     40.85 |            4.23 |        -310300 |

### Best variant by PnL: 15:30 | no SL | no TP - by year

|   year |   trades |         pnl |
|-------:|---------:|------------:|
|   2023 |      169 | 5.89297e+06 |
|   2024 |      523 | 8.88909e+06 |
|   2025 |      656 | 5.90908e+07 |
|   2026 |      527 | 4.77964e+08 |

## SHORT (puts) - 1556 entries

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
 "one_lot_too_expensive": 11
}
```

### Top 15 variants by ROI (>= 30 trades)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| 15:30       | no SL     | no TP     |     1556 |     43.57 | 3.18036e+07 |     38.46 |            3.03 |        -463557 |
| 12:00       | no SL     | no TP     |     1160 |     42.59 | 1.60072e+07 |     26.05 |            2.44 |        -520272 |
| 10:00       | no SL     | no TP     |      837 |     42.41 | 1.12925e+07 |     25.56 |            2.6  |        -487818 |
| 15:30       | no SL     | TP 120%   |     1556 |     45.89 | 1.98555e+07 |     24.01 |            2.35 |        -365682 |
| 09:30       | no SL     | TP 120%   |      652 |     43.56 | 7.37516e+06 |     21.51 |            2.44 |        -403304 |
| 09:30       | no SL     | no TP     |      652 |     43.25 | 7.29274e+06 |     21.27 |            2.41 |        -403304 |
| 10:00       | SL 60%    | no TP     |      837 |     41.58 | 9.35644e+06 |     21.18 |            2.28 |        -515370 |
| 09:30       | SL 60%    | TP 120%   |      652 |     43.4  | 7.06915e+06 |     20.62 |            2.37 |        -477964 |
| 15:30       | no SL     | TP 80%    |     1556 |     47.62 | 1.68804e+07 |     20.41 |            2.2  |        -331890 |
| 09:30       | SL 60%    | no TP     |      652 |     43.1  | 6.97191e+06 |     20.34 |            2.33 |        -466540 |
| 15:30       | no SL     | TP 60%    |     1556 |     49.55 | 1.57659e+07 |     19.06 |            2.17 |        -350295 |
| 09:30       | SL 40%    | no TP     |      652 |     41.87 | 6.32282e+06 |     18.44 |            2.2  |        -612367 |
| 09:30       | SL 40%    | TP 120%   |      652 |     42.18 | 6.23888e+06 |     18.2  |            2.19 |        -618891 |
| 10:00       | SL 40%    | no TP     |      837 |     39.19 | 7.88968e+06 |     17.86 |            2.05 |        -804409 |
| 12:00       | no SL     | TP 120%   |     1160 |     43.45 | 1.01524e+07 |     16.52 |            1.93 |        -534346 |

### Best variant per time exit (by ROI)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| 15:30       | no SL     | no TP     |     1556 |     43.57 | 3.18036e+07 |     38.46 |            3.03 |        -463557 |
| 12:00       | no SL     | no TP     |     1160 |     42.59 | 1.60072e+07 |     26.05 |            2.44 |        -520272 |
| 10:00       | no SL     | no TP     |      837 |     42.41 | 1.12925e+07 |     25.56 |            2.6  |        -487818 |
| 09:30       | no SL     | TP 120%   |      652 |     43.56 | 7.37516e+06 |     21.51 |            2.44 |        -403304 |

### Best variant by PnL: 15:30 | no SL | no TP - by year

|   year |   trades |              pnl |
|-------:|---------:|-----------------:|
|   2023 |        6 | 589024           |
|   2024 |      335 | -55854           |
|   2025 |      524 |      1.14751e+07 |
|   2026 |      691 |      1.97954e+07 |

The best of 80 variants is chosen after seeing the results, so it is optimistic: check that neighbouring variants and every year look similar. Charges and slippage are not included; option candles with no trade in a minute are missing, so illiquid-stock fills can be better than real. Files per side: summary_<SIDE>.csv, all_trades_<SIDE>.csv.gz, entries_<SIDE>.csv, best_variant_trades_<SIDE>.csv.