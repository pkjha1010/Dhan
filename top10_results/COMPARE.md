# TOP 10 stocks - every strategy, one grid

**Stocks:** HDFCBANK RELIANCE ICICIBANK INFY BHARTIARTL ITC LT TCS AXISBANK SBIN
**Entry dates:** 2025-11-13 to 2026-11-12  |  **Grid:** stop-loss 0,20,40,60 x target 0,40,60,80,120 (0 = none) x time exit 09:30,10:00,12:00,15:00,15:30  |  **Rs 60,000 per trade cap, no charges / slippage**

## Status of each strategy

- **opendrop**: PARTIAL - 58 of 59 request groups finished. Results cover only the finished part. Run again to continue.
- **gap**: PARTIAL - 88 of 117 request groups finished. Results cover only the finished part. Run again to continue.
- **bpb_base**: PARTIAL - 119 of 167 request groups finished. Results cover only the finished part. Run again to continue.
- **accum5**: PARTIAL - 40 of 41 request groups finished. Results cover only the finished part. Run again to continue.
- **accum10**: COMPLETE - all 36 request groups finished.
- **orb**: (no PROGRESS.txt)
- **all8**: PARTIAL - 124 of 239 request groups finished. Results cover only the finished part. Run again to continue.
- **pullback**: COMPLETE

## Best variant per strategy by total PnL (at least 10 trades)

| strategy       | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:---------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| PULLBACK_LONG  | 15:00       | SL 2000%  | no TP     |       33 |     30.3  |      189997 |     10.46 |            1.92 |        -100822 |
| GAP_SHORT      | 15:30       | no SL     | TP 60%    |       28 |     57.1  |      173881 |     11.38 |          nan    |            nan |
| GAP_LONG       | 12:00       | SL 40%    | TP 120%   |       16 |     56.2  |       97525 |     11.52 |          nan    |            nan |
| OPENDROP_LONG  | 15:30       | SL 20%    | TP 80%    |       28 |     46.4  |       77620 |      5.16 |          nan    |            nan |
| BPB_LONG       | 15:30       | no SL     | TP 80%    |       23 |     47.8  |       61880 |      5.01 |          nan    |            nan |
| PULLBACK_SHORT | 10:00       | SL 6000%  | TP 4000%  |       29 |     62.07 |       55829 |      3.65 |            1.56 |         -51925 |
| BPB_SHORT      | 10:00       | no SL     | TP 40%    |       24 |     62.5  |       40422 |      3.16 |          nan    |            nan |
| ACC10_SHORT    | 15:30       | SL 60%    | TP 80%    |       10 |     30    |       11799 |      2.19 |          nan    |            nan |

## Best variant per strategy by ROI (at least 10 trades)

| strategy       | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:---------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_LONG       | 12:00       | SL 40%    | TP 120%   |       16 |     56.2  |       97525 |     11.52 |          nan    |            nan |
| GAP_SHORT      | 15:30       | no SL     | TP 60%    |       28 |     57.1  |      173881 |     11.38 |          nan    |            nan |
| PULLBACK_LONG  | 15:00       | SL 2000%  | no TP     |       33 |     30.3  |      189997 |     10.46 |            1.92 |        -100822 |
| OPENDROP_LONG  | 15:30       | SL 20%    | TP 80%    |       28 |     46.4  |       77620 |      5.16 |          nan    |            nan |
| BPB_LONG       | 15:30       | no SL     | TP 80%    |       23 |     47.8  |       61880 |      5.01 |          nan    |            nan |
| PULLBACK_SHORT | 10:00       | SL 6000%  | TP 4000%  |       29 |     62.07 |       55829 |      3.65 |            1.56 |         -51925 |
| BPB_SHORT      | 10:00       | no SL     | TP 40%    |       24 |     62.5  |       40422 |      3.16 |          nan    |            nan |
| ACC10_SHORT    | 15:30       | SL 60%    | TP 80%    |       10 |     30    |       11799 |      2.19 |            1.22 |         -38914 |

## Exit 09:30: best variant of each strategy by total PnL

| strategy       | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:---------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT      | 09:30       | SL 40%    | TP 60%    |       16 |     50    |       80693 |      9.27 |            2.24 |         -25384 |
| PULLBACK_SHORT | 09:30       | SL 6000%  | TP 4000%  |       26 |     57.69 |       41940 |      3.07 |            1.78 |         -14480 |
| BPB_SHORT      | 09:30       | SL 20%    | TP 40%    |       21 |     57.14 |       13270 |      1.18 |            1.2  |         -26038 |
| BPB_LONG       | 09:30       | SL 20%    | no TP     |       12 |     66.67 |        4972 |      0.77 |            1.19 |         -16175 |
| GAP_LONG       | 09:30       | SL 20%    | no TP     |       10 |     40    |       -7520 |     -1.43 |            0.79 |         -25847 |
| PULLBACK_LONG  | 09:30       | SL 4000%  | TP 6000%  |       19 |     42.11 |      -11097 |     -1.08 |            0.81 |         -50368 |
| OPENDROP_LONG  | 09:30       | SL 20%    | no TP     |       19 |     42.11 |      -26913 |     -2.62 |            0.62 |         -53067 |

## Exit 10:00: best variant of each strategy by total PnL

| strategy       | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:---------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| GAP_SHORT      | 10:00       | no SL     | TP 60%    |       18 |     50    |       86599 |      8.88 |            2.13 |         -40238 |
| PULLBACK_SHORT | 10:00       | no SL     | TP 4000%  |       29 |     62.07 |       55829 |      3.65 |            1.56 |         -51925 |
| BPB_SHORT      | 10:00       | no SL     | TP 40%    |       24 |     62.5  |       40422 |      3.16 |          nan    |            nan |
| GAP_LONG       | 10:00       | SL 20%    | TP 80%    |       13 |     46.15 |       29083 |      4.18 |            1.61 |         -22552 |
| BPB_LONG       | 10:00       | SL 20%    | TP 80%    |       13 |     38.46 |      -16522 |     -2.34 |            0.73 |         -31324 |
| PULLBACK_LONG  | 10:00       | SL 2000%  | TP 4000%  |       22 |     22.73 |      -27693 |     -2.3  |            0.71 |         -59630 |
| OPENDROP_LONG  | 10:00       | no SL     | TP 40%    |       22 |     45.45 |      -36922 |     -3.11 |            0.59 |         -57005 |

## Exit 12:00: best variant of each strategy by total PnL

| strategy       | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:---------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| PULLBACK_LONG  | 12:00       | SL 2000%  | no TP     |       28 |     35.71 |      149735 |      9.8  |            1.89 |         -99030 |
| GAP_LONG       | 12:00       | SL 40%    | TP 120%   |       16 |     56.25 |       97525 |     11.52 |            2.73 |         -29020 |
| GAP_SHORT      | 12:00       | SL 40%    | TP 60%    |       22 |     36.36 |       56624 |      4.72 |            1.39 |         -92871 |
| BPB_LONG       | 12:00       | no SL     | TP 80%    |       20 |     55    |       44223 |      4.02 |          nan    |            nan |
| BPB_SHORT      | 12:00       | no SL     | TP 40%    |       30 |     40    |        4768 |      0.3  |            1.03 |         -84484 |
| OPENDROP_LONG  | 12:00       | SL 40%    | TP 40%    |       26 |     53.85 |       -6229 |     -0.45 |            0.94 |         -68104 |
| PULLBACK_SHORT | 12:00       | SL 4000%  | TP 4000%  |       36 |     47.22 |      -25709 |     -1.35 |            0.87 |         -72607 |

## Exit 15:00: best variant of each strategy by total PnL

| strategy       | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:---------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| PULLBACK_LONG  | 15:00       | SL 2000%  | no TP     |       33 |     30.3  |      189997 |     10.46 |            1.92 |        -100822 |
| GAP_SHORT      | 15:00       | no SL     | TP 60%    |       27 |     55.6  |      155593 |     10.58 |          nan    |            nan |
| GAP_LONG       | 15:00       | SL 40%    | TP 120%   |       21 |     47.62 |       77030 |      6.98 |            1.77 |         -27188 |
| BPB_LONG       | 15:00       | SL 20%    | TP 80%    |       23 |     43.5  |       60048 |      4.86 |          nan    |            nan |
| OPENDROP_LONG  | 15:00       | SL 20%    | TP 80%    |       28 |     50    |       47291 |      3.15 |          nan    |            nan |
| BPB_SHORT      | 15:00       | no SL     | TP 40%    |       34 |     47.06 |      -34246 |     -1.86 |            0.85 |         -69674 |
| PULLBACK_SHORT | 15:00       | SL 2000%  | TP 4000%  |       45 |     37.78 |      -57166 |     -2.38 |            0.8  |         -72861 |

## Exit 15:30: best variant of each strategy by total PnL

| strategy       | exit_rule   | sl_rule   | tp_rule   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:---------------|:------------|:----------|:----------|---------:|----------:|------------:|----------:|----------------:|---------------:|
| PULLBACK_LONG  | 15:30       | SL 2000%  | no TP     |       35 |     34.29 |      183176 |      9.53 |            1.89 |        -103202 |
| GAP_SHORT      | 15:30       | no SL     | TP 60%    |       28 |     57.1  |      173881 |     11.38 |          nan    |            nan |
| GAP_LONG       | 15:30       | SL 40%    | TP 120%   |       21 |     42.9  |       93477 |      8.47 |          nan    |            nan |
| OPENDROP_LONG  | 15:30       | SL 20%    | TP 80%    |       28 |     46.4  |       77620 |      5.16 |          nan    |            nan |
| BPB_LONG       | 15:30       | no SL     | TP 80%    |       23 |     47.8  |       61880 |      5.01 |          nan    |            nan |
| ACC10_SHORT    | 15:30       | no SL     | TP 80%    |       10 |     30    |       11799 |      2.19 |          nan    |            nan |
| BPB_SHORT      | 15:30       | no SL     | TP 40%    |       36 |     58.33 |        1773 |      0.09 |            1.01 |         -68205 |
| PULLBACK_SHORT | 15:30       | SL 2000%  | TP 4000%  |       47 |     36.17 |      -80215 |     -3.18 |            0.77 |        -102752 |

## Same variant for all strategies - no SL / no TP: Total PnL (Rs) by time exit

| strategy       |   09:30 |   10:00 |   12:00 |   15:00 |   15:30 |
|:---------------|--------:|--------:|--------:|--------:|--------:|
| ACC10_SHORT    |     nan |     nan |     nan |     nan |    5861 |
| BPB_LONG       |    1295 |  -40029 |   17916 |  -38144 |  -32476 |
| BPB_SHORT      |  -19435 |   -3453 |  -35591 |  -87182 | -103449 |
| GAP_LONG       |   -8105 |   13504 |   40049 |   40514 |   70681 |
| GAP_SHORT      |   30661 |  -19840 |  -23391 |   75735 |  -45710 |
| OPENDROP_LONG  |  -37400 |  -36922 |  -31666 |  -63720 |  -35551 |
| PULLBACK_LONG  |  -11097 |  -37658 |  110767 |  131954 |  132036 |
| PULLBACK_SHORT |   17640 |  -30583 | -129544 | -247009 | -403621 |

## Same variant for all strategies - no SL / no TP: Win % by time exit

| strategy       |   09:30 |   10:00 |   12:00 |   15:00 |   15:30 |
|:---------------|--------:|--------:|--------:|--------:|--------:|
| ACC10_SHORT    |   nan   |   nan   |   nan   |   nan   |    30   |
| BPB_LONG       |    66.7 |    38.5 |    54.6 |    40   |    48   |
| BPB_SHORT      |    52.4 |    60   |    40   |    44.1 |    52.8 |
| GAP_LONG       |    40   |    53.8 |    56.2 |    47.6 |    42.9 |
| GAP_SHORT      |    50   |    44.4 |    36.4 |    50   |    48.3 |
| OPENDROP_LONG  |    42.1 |    45.4 |    53.8 |    48.3 |    44.8 |
| PULLBACK_LONG  |    42.1 |    22.7 |    35.7 |    33.3 |    40   |
| PULLBACK_SHORT |    57.7 |    55.2 |    44.4 |    35.6 |    31.9 |

## Same variant for all strategies - no SL / no TP: Trades by time exit

| strategy       |   09:30 |   10:00 |   12:00 |   15:00 |   15:30 |
|:---------------|--------:|--------:|--------:|--------:|--------:|
| ACC10_SHORT    |     nan |     nan |     nan |     nan |      10 |
| BPB_LONG       |      12 |      13 |      22 |      25 |      25 |
| BPB_SHORT      |      21 |      25 |      30 |      34 |      36 |
| GAP_LONG       |      10 |      13 |      16 |      21 |      21 |
| GAP_SHORT      |      16 |      18 |      22 |      28 |      29 |
| OPENDROP_LONG  |      19 |      22 |      26 |      29 |      29 |
| PULLBACK_LONG  |      19 |      22 |      28 |      33 |      35 |
| PULLBACK_SHORT |      26 |      29 |      36 |      45 |      47 |

## Same variant for all strategies - no SL / TP 40%: Total PnL (Rs) by time exit

| strategy      |   09:30 |   10:00 |   12:00 |   15:00 |   15:30 |
|:--------------|--------:|--------:|--------:|--------:|--------:|
| ACC10_SHORT   |     nan |     nan |     nan |     nan |   -6125 |
| BPB_LONG      |    1295 |  -40029 |   15746 |  -49256 |  -48533 |
| BPB_SHORT     |    9545 |   23174 |    4768 |  -34246 |    1773 |
| GAP_LONG      |   -8105 |   10712 |   38085 |   26035 |   27972 |
| GAP_SHORT     |   50611 |   39944 |   16750 |  115945 |  120907 |
| OPENDROP_LONG |  -37400 |  -36922 |  -15405 |  -33864 |  -17793 |

## Same variant for all strategies - no SL / TP 40%: Win % by time exit

| strategy      |   09:30 |   10:00 |   12:00 |   15:00 |   15:30 |
|:--------------|--------:|--------:|--------:|--------:|--------:|
| ACC10_SHORT   |   nan   |   nan   |   nan   |   nan   |    30   |
| BPB_LONG      |    66.7 |    38.5 |    54.6 |    44   |    48   |
| BPB_SHORT     |    57.1 |    60   |    40   |    47.1 |    58.3 |
| GAP_LONG      |    40   |    53.8 |    56.2 |    47.6 |    47.6 |
| GAP_SHORT     |    50   |    50   |    36.4 |    53.6 |    55.2 |
| OPENDROP_LONG |    42.1 |    45.4 |    53.8 |    51.7 |    48.3 |

## Same variant for all strategies - no SL / TP 40%: Trades by time exit

| strategy      |   09:30 |   10:00 |   12:00 |   15:00 |   15:30 |
|:--------------|--------:|--------:|--------:|--------:|--------:|
| ACC10_SHORT   |     nan |     nan |     nan |     nan |      10 |
| BPB_LONG      |      12 |      13 |      22 |      25 |      25 |
| BPB_SHORT     |      21 |      25 |      30 |      34 |      36 |
| GAP_LONG      |      10 |      13 |      16 |      21 |      21 |
| GAP_SHORT     |      16 |      18 |      22 |      28 |      29 |
| OPENDROP_LONG |      19 |      22 |      26 |      29 |      29 |

Everything is in `ALL_VARIANTS.csv` (every strategy x exit x SL x TP). The best variant is the best of many, chosen after seeing the results, so it is optimistic; 10 stocks x 1 year gives few trades, so look at the trade counts. Charges, taxes and slippage are not included. Past results do not promise future results.
