# PULLBACK re-cross on options - Dhan data - LONG and SHORT reported separately

**Status:** COMPLETE  |  2025-11-13 .. 2026-11-12  |  Nifty filter: intraday  |  Cap Rs 60,000

LONG = breakout above the 10-day high, pullback, re-cross up -> buy the CALL (Nifty must be green).  SHORT = breakdown below the 10-day low, bounce, re-cross down -> buy the PUT (Nifty must be red).  ATM at the entry minute (else nearest ITM), strike locked, fill = close of the entry-minute option candle.

## LONG (calls) - 35 entries

### Entries skipped / diagnostics

```
{
 "no_equity_id": 0,
 "too_little_daily": 0,
 "no_stock_minute_data": 0,
 "no_cross_minute": 2,
 "no_nifty_minute_data": 0,
 "nifty_filter_failed": 14,
 "no_option_candle_atm_or_itm": 0,
 "no_lot_size": 0,
 "one_lot_too_expensive": 0
}
```

### Top 15 variants by ROI (>= 10 trades)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| 15:00       | SL 20%    | no TP     |       33 |     30.3  |      189997 |     10.46 |            1.92 |        -100822 |
| 12:00       | SL 20%    | no TP     |       28 |     35.71 |      149735 |      9.8  |            1.89 |         -99030 |
| 15:30       | SL 20%    | no TP     |       35 |     34.29 |      183176 |      9.53 |            1.89 |        -103202 |
| 15:00       | no SL     | no TP     |       33 |     33.33 |      131954 |      7.27 |            1.49 |        -139300 |
| 12:00       | no SL     | no TP     |       28 |     35.71 |      110767 |      7.25 |            1.53 |        -114209 |
| 12:00       | SL 60%    | no TP     |       28 |     35.71 |      110767 |      7.25 |            1.53 |        -114209 |
| 15:00       | SL 60%    | no TP     |       33 |     33.33 |      131414 |      7.24 |            1.49 |        -139300 |
| 15:00       | SL 40%    | no TP     |       33 |     33.33 |      127482 |      7.02 |            1.47 |        -142730 |
| 12:00       | SL 40%    | no TP     |       28 |     35.71 |      106606 |      6.98 |            1.5  |        -112809 |
| 15:30       | SL 60%    | no TP     |       35 |     40    |      132756 |      6.91 |            1.51 |        -137741 |
| 15:30       | no SL     | no TP     |       35 |     40    |      132036 |      6.87 |            1.5  |        -137741 |
| 15:30       | SL 40%    | no TP     |       35 |     37.14 |      111653 |      5.81 |            1.4  |        -150620 |
| 15:30       | SL 20%    | TP 120%   |       35 |     34.29 |       13315 |      0.69 |            1.06 |        -103202 |
| 12:00       | SL 20%    | TP 120%   |       28 |     35.71 |        7235 |      0.47 |            1.04 |         -99030 |
| 12:00       | SL 20%    | TP 80%    |       28 |     35.71 |      -11765 |     -0.77 |            0.93 |         -99030 |

### Best variant per time exit (by ROI)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| 15:00       | SL 20%    | no TP     |       33 |     30.3  |      189997 |     10.46 |            1.92 |        -100822 |
| 12:00       | SL 20%    | no TP     |       28 |     35.71 |      149735 |      9.8  |            1.89 |         -99030 |
| 15:30       | SL 20%    | no TP     |       35 |     34.29 |      183176 |      9.53 |            1.89 |        -103202 |
| 09:30       | no SL     | TP 120%   |       19 |     42.11 |      -11097 |     -1.08 |            0.81 |         -50368 |
| 10:00       | SL 20%    | TP 40%    |       22 |     22.73 |      -27693 |     -2.3  |            0.71 |         -59630 |

### Best variant by PnL: 15:00 | SL 20% | no TP - by year

|   year |   trades |    pnl |
|-------:|---------:|-------:|
|   2025 |        5 | -29317 |
|   2026 |       28 | 219314 |

## SHORT (puts) - 47 entries

### Entries skipped / diagnostics

```
{
 "no_equity_id": 0,
 "too_little_daily": 0,
 "no_stock_minute_data": 0,
 "no_cross_minute": 3,
 "no_nifty_minute_data": 0,
 "nifty_filter_failed": 26,
 "no_option_candle_atm_or_itm": 1,
 "no_lot_size": 0,
 "one_lot_too_expensive": 0,
 "premium_below_min": 1
}
```

### Top 15 variants by ROI (>= 10 trades)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| 10:00       | no SL     | TP 40%    |       29 |     62.07 |       55829 |      3.65 |            1.56 |         -51925 |
| 10:00       | SL 60%    | TP 40%    |       29 |     62.07 |       55829 |      3.65 |            1.56 |         -51925 |
| 10:00       | SL 40%    | TP 40%    |       29 |     62.07 |       49072 |      3.21 |            1.46 |         -58682 |
| 09:30       | no SL     | TP 40%    |       26 |     57.69 |       41940 |      3.07 |            1.78 |         -14480 |
| 09:30       | SL 60%    | TP 40%    |       26 |     57.69 |       41940 |      3.07 |            1.78 |         -14480 |
| 09:30       | SL 40%    | TP 40%    |       26 |     57.69 |       41940 |      3.07 |            1.78 |         -14480 |
| 09:30       | SL 20%    | TP 40%    |       26 |     57.69 |       41212 |      3.02 |            1.76 |         -14480 |
| 09:30       | no SL     | no TP     |       26 |     57.69 |       17640 |      1.29 |            1.33 |         -14480 |
| 09:30       | no SL     | TP 80%    |       26 |     57.69 |       17640 |      1.29 |            1.33 |         -14480 |
| 09:30       | SL 40%    | TP 120%   |       26 |     57.69 |       17640 |      1.29 |            1.33 |         -14480 |
| 09:30       | SL 40%    | TP 80%    |       26 |     57.69 |       17640 |      1.29 |            1.33 |         -14480 |
| 09:30       | no SL     | TP 60%    |       26 |     57.69 |       17640 |      1.29 |            1.33 |         -14480 |
| 09:30       | SL 60%    | no TP     |       26 |     57.69 |       17640 |      1.29 |            1.33 |         -14480 |
| 09:30       | SL 60%    | TP 60%    |       26 |     57.69 |       17640 |      1.29 |            1.33 |         -14480 |
| 09:30       | SL 60%    | TP 80%    |       26 |     57.69 |       17640 |      1.29 |            1.33 |         -14480 |

### Best variant per time exit (by ROI)

| exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| 10:00       | no SL     | TP 40%    |       29 |     62.07 |       55829 |      3.65 |            1.56 |         -51925 |
| 09:30       | no SL     | TP 40%    |       26 |     57.69 |       41940 |      3.07 |            1.78 |         -14480 |
| 12:00       | SL 40%    | TP 40%    |       36 |     47.22 |      -25709 |     -1.35 |            0.87 |         -72607 |
| 15:00       | SL 20%    | TP 40%    |       45 |     37.78 |      -57166 |     -2.38 |            0.8  |         -72861 |
| 15:30       | SL 20%    | TP 40%    |       47 |     36.17 |      -80215 |     -3.18 |            0.77 |        -102752 |

### Best variant by PnL: 10:00 | no SL | TP 40% - by year

|   year |   trades |    pnl |
|-------:|---------:|-------:|
|   2025 |        1 | -15525 |
|   2026 |       28 |  71354 |

The best of 80 variants is chosen after seeing the results, so it is optimistic: check that neighbouring variants and every year look similar. Charges and slippage are not included; option candles with no trade in a minute are missing, so illiquid-stock fills can be better than real. Files per side: summary_<SIDE>.csv, all_trades_<SIDE>.csv.gz, entries_<SIDE>.csv, best_variant_trades_<SIDE>.csv.