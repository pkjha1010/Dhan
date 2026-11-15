# Pure breakout + Bollinger - SHORT (put) - entry premium above Rs 5

**B = the breakout day. B+1 = the next trading day, B+2 = the day after, ...**

Entry rules: **B+1 onward** (no skip) | **B+2 onward** (skip only B+1) | **B+3 onward (your script)** (its day counter skips B+1 and B+2). 'noBB' = without the Bollinger filter (only if that data was fetched).

## Entries by entry day (distinct stock/day with option data)

| set                      |   entries |   B+1 |   B+2 |   B+3 |   B+4 |   B+5 |   B+6 or later |
|:-------------------------|----------:|------:|------:|------:|------:|------:|---------------:|
| B+1 onward               |        73 |    64 |     5 |     4 |     0 |     0 |              0 |
| B+2 onward               |       100 |     0 |    95 |     5 |     0 |     0 |              0 |
| B+3 onward (your script) |        85 |     0 |     0 |    85 |     0 |     0 |              0 |

## SHORT: no stop-loss, no target, exit 15:30 (hold to the close)

| set                      | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward               | 15:30       | none | none |       73 |      46.6 |       41749 |      1.08 |            1.06 |          1.49 |
| B+2 onward               | 15:30       | none | none |      100 |      51   |      603558 |     11.5  |            1.86 |         10.72 |
| B+3 onward (your script) | 15:30       | none | none |       85 |      36.5 |     -443031 |     -9.91 |            0.57 |         -9.1  |

## SHORT - B+1 onward: top 10 variants by total PnL (at least 30 trades)

| set        | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | 15:30       | 20%  | 120% |       73 |      39.7 |      433933 |     11.22 |            1.92 |         11.2  |
| B+1 onward | 15:00       | 20%  | 120% |       73 |      39.7 |      427479 |     11.06 |            1.91 |         10.99 |
| B+1 onward | 15:30       | 40%  | 120% |       73 |      46.6 |      325050 |      8.41 |            1.51 |          8.24 |
| B+1 onward | 15:00       | 40%  | 120% |       73 |      46.6 |      323788 |      8.37 |            1.52 |          8.16 |
| B+1 onward | 15:30       | 20%  | 60%  |       73 |      42.5 |      319502 |      8.26 |            1.71 |          8.12 |
| B+1 onward | 15:30       | 20%  | 80%  |       73 |      39.7 |      315260 |      8.15 |            1.67 |          8.12 |
| B+1 onward | 15:00       | 20%  | 80%  |       73 |      39.7 |      307206 |      7.95 |            1.66 |          7.84 |
| B+1 onward | 15:00       | 20%  | 60%  |       73 |      42.5 |      303008 |      7.84 |            1.68 |          7.64 |
| B+1 onward | 15:00       | 20%  | none |       73 |      38.4 |      296197 |      7.66 |            1.61 |          7.88 |
| B+1 onward | 15:30       | 60%  | 120% |       73 |      47.9 |      288723 |      7.47 |            1.43 |          7.43 |

## SHORT - B+2 onward: top 10 variants by total PnL (at least 30 trades)

| set        | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | 15:00       | none | none |       99 |      54.5 |      730512 |     14.08 |            2.16 |         13.24 |
| B+2 onward | 15:00       | 40%  | none |       99 |      52.5 |      715707 |     13.79 |            2.14 |         12.94 |
| B+2 onward | 15:00       | 60%  | none |       99 |      53.5 |      698415 |     13.46 |            2.08 |         12.71 |
| B+2 onward | 12:00       | none | none |       95 |      40   |      676666 |     13.5  |            2.26 |         12.09 |
| B+2 onward | 15:00       | none | 120% |       99 |      54.5 |      636779 |     12.27 |            2.01 |         11.38 |
| B+2 onward | 15:00       | 40%  | 120% |       99 |      52.5 |      621974 |     11.99 |            2    |         11.08 |
| B+2 onward | 12:00       | 40%  | none |       95 |      38.9 |      613477 |     12.24 |            2.03 |         10.94 |
| B+2 onward | 15:30       | 40%  | none |      100 |      49   |      610982 |     11.64 |            1.9  |         10.84 |
| B+2 onward | 15:00       | 60%  | 120% |       99 |      53.5 |      604682 |     11.65 |            1.93 |         10.84 |
| B+2 onward | 15:30       | none | none |      100 |      51   |      603558 |     11.5  |            1.86 |         10.72 |

## SHORT - B+3 onward (your script): top 10 variants by total PnL (at least 30 trades)

| set                      | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | 15:00       | 20%  | 40%  |       85 |      48.2 |      230012 |      5.14 |            1.49 |          5.33 |
| B+3 onward (your script) | 15:00       | 20%  | 60%  |       85 |      42.4 |      216681 |      4.85 |            1.41 |          4.64 |
| B+3 onward (your script) | 15:30       | 20%  | 40%  |       85 |      47.1 |      213567 |      4.78 |            1.44 |          5.02 |
| B+3 onward (your script) | 09:30       | none | 60%  |       82 |      46.3 |      194336 |      4.52 |            1.69 |          4.38 |
| B+3 onward (your script) | 15:30       | 20%  | 60%  |       85 |      41.2 |      189171 |      4.23 |            1.35 |          3.97 |
| B+3 onward (your script) | 09:30       | 40%  | 60%  |       82 |      46.3 |      184970 |      4.3  |            1.64 |          4.19 |
| B+3 onward (your script) | 15:00       | 40%  | 40%  |       85 |      49.4 |      181563 |      4.06 |            1.33 |          4.39 |
| B+3 onward (your script) | 09:30       | 60%  | 60%  |       82 |      46.3 |      178436 |      4.15 |            1.6  |          4.06 |
| B+3 onward (your script) | 09:30       | none | 40%  |       82 |      47.6 |      174187 |      4.05 |            1.63 |          4.14 |
| B+3 onward (your script) | 09:30       | 40%  | 40%  |       82 |      47.6 |      164821 |      3.83 |            1.57 |          3.95 |

### SHORT - B+1 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |    80% |   120% |   none |
|:-----|-------:|-------:|-------:|-------:|-------:|
| none |  -5919 | 159968 | 148532 | 267205 |  41749 |
| 20%  | 183098 | 319502 | 315260 | 433933 | 242576 |
| 40%  |  51542 | 194301 | 206377 | 325050 | 126331 |
| 60%  |   4627 | 170514 | 170050 | 288723 |  76441 |

### SHORT - B+2 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |    80% |   120% |   none |
|:-----|-------:|-------:|-------:|-------:|-------:|
| none | 373923 | 425566 | 367237 | 532316 | 603558 |
| 20%  | 173019 | 306043 | 268897 | 347489 | 378668 |
| 40%  | 296758 | 437598 | 406791 | 539740 | 610982 |
| 60%  | 316895 | 434024 | 380826 | 501963 | 573205 |

### SHORT - B+3 onward (your script): total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |     80% |    120% |    none |
|:-----|-------:|-------:|--------:|--------:|--------:|
| none |  38311 | -22585 | -186130 | -284851 | -443031 |
| 20%  | 213567 | 189171 |   55394 |   42118 | -121687 |
| 40%  | 153964 |  95730 |  -78345 | -166584 | -324764 |
| 60%  |  76993 |  22524 | -125689 | -211347 | -369527 |

## SHORT - B+1 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | B+1         |       64 |      48.4 |       73302 |      2.16 |            1.11 |          2.48 |
| B+1 onward | B+2         |        5 |      40   |       -9504 |     -3.61 |            0.81 |         -1.57 |
| B+1 onward | B+3         |        4 |      25   |      -22049 |    -10.33 |            0.19 |        -10.52 |

## SHORT - B+2 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |       95 |      51.6 |      624531 |     12.55 |            1.92 |         11.71 |
| B+2 onward | B+3         |        5 |      40   |      -20973 |     -7.72 |            0.22 |         -7.94 |

## SHORT - B+3 onward (your script): result by exact entry day B+n (no SL, no TP, exit 15:30)

| set                      | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | B+3         |       85 |      36.5 |     -443031 |     -9.91 |            0.57 |          -9.1 |

## SHORT - B+1 onward: its best variant (15:30 | SL 20% | TP 120%) by exact entry day B+n

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | B+1         |       64 |      40.6 |      451011 |     13.3  |            2.1  |         13.14 |
| B+1 onward | B+2         |        5 |      40   |       11211 |      4.26 |            1.37 |          6.14 |
| B+1 onward | B+3         |        4 |      25   |      -28289 |    -13.25 |            0.16 |        -13.45 |

## SHORT - B+2 onward: its best variant (15:00 | SL none | TP none) by exact entry day B+n

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |       94 |      55.3 |      741121 |     15.07 |            2.22 |         14.17 |
| B+2 onward | B+3         |        5 |      40   |      -10609 |     -3.91 |            0.51 |         -4.2  |

## SHORT - B+3 onward (your script): its best variant (15:00 | SL 20% | TP 40%) by exact entry day B+n

| set                      | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | B+3         |       85 |      48.2 |      230012 |      5.14 |            1.49 |          5.33 |

## SHORT: best variant of every entry rule, year by year (is it one lucky year?)

| set                      | variant                   |   year |   trades |   total_pnl |   win_pct |
|:-------------------------|:--------------------------|-------:|---------:|------------:|----------:|
| B+1 onward               | 15:30 | SL 20 | TP 120    |   2026 |       73 |      433933 |      39.7 |
| B+2 onward               | 15:00 | SL none | TP none |   2026 |       99 |      730512 |      54.5 |
| B+3 onward (your script) | 15:00 | SL 20 | TP 40     |   2026 |       85 |      230012 |      48.2 |

The best variants are the best of 100 per entry rule, picked after seeing the results, so they are optimistic: check their neighbours (matrices) and the other exits. Charges, taxes, slippage not included. Rows with few trades (some B+n days) are noise. Lot sizes are today's values.
