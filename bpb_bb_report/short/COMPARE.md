# Pure breakout + Bollinger - SHORT (put) - all premiums

**B = the breakout day. B+1 = the next trading day, B+2 = the day after, ...**

Entry rules: **B+1 onward** (no skip) | **B+2 onward** (skip only B+1) | **B+3 onward (your script)** (its day counter skips B+1 and B+2). 'noBB' = without the Bollinger filter (only if that data was fetched).

## Entries by entry day (distinct stock/day with option data)

| set                      |   entries |   B+1 |   B+2 |   B+3 |   B+4 |   B+5 |   B+6 or later |
|:-------------------------|----------:|------:|------:|------:|------:|------:|---------------:|
| B+1 onward               |        92 |    80 |     7 |     4 |     1 |     0 |              0 |
| B+2 onward               |       129 |     0 |   123 |     5 |     1 |     0 |              0 |
| B+3 onward (your script) |       104 |     0 |     0 |   103 |     1 |     0 |              0 |

## SHORT: no stop-loss, no target, exit 15:30 (hold to the close)

| set                      | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward               | 15:30       | none | none |       92 |      41.3 |     -189288 |     -3.89 |            0.83 |         -3.33 |
| B+2 onward               | 15:30       | none | none |      129 |      46.5 |      405460 |      5.97 |            1.38 |          5.69 |
| B+3 onward (your script) | 15:30       | none | none |      104 |      38.5 |     -478868 |     -8.73 |            0.65 |         -7.81 |

## SHORT - B+1 onward: top 10 variants by total PnL (at least 30 trades)

| set        | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | 15:30       | 20%  | 120% |       92 |      35.9 |      407679 |      8.38 |            1.63 |          8.49 |
| B+1 onward | 15:00       | 20%  | 120% |       92 |      35.9 |      399893 |      8.22 |            1.63 |          8.31 |
| B+1 onward | 15:00       | 40%  | 120% |       92 |      42.4 |      301248 |      6.19 |            1.36 |          6.13 |
| B+1 onward | 15:30       | 20%  | 60%  |       92 |      39.1 |      299877 |      6.17 |            1.49 |          6.11 |
| B+1 onward | 15:30       | 40%  | 120% |       92 |      42.4 |      299070 |      6.15 |            1.35 |          6.12 |
| B+1 onward | 15:00       | 20%  | 60%  |       92 |      39.1 |      285471 |      5.87 |            1.47 |          5.78 |
| B+1 onward | 15:30       | 20%  | 80%  |       92 |      35.9 |      270507 |      5.56 |            1.42 |          5.66 |
| B+1 onward | 15:00       | 20%  | 80%  |       92 |      35.9 |      264541 |      5.44 |            1.42 |          5.49 |
| B+1 onward | 09:30       | 60%  | 120% |       71 |      50.7 |      225856 |      5.97 |            2.14 |          5.72 |
| B+1 onward | 09:30       | none | 120% |       71 |      50.7 |      225856 |      5.97 |            2.14 |          5.72 |

## SHORT - B+2 onward: top 10 variants by total PnL (at least 30 trades)

| set        | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | 15:00       | 40%  | none |      128 |      46.9 |      578314 |      8.6  |            1.62 |          8.24 |
| B+2 onward | 12:00       | none | none |      123 |      39   |      574130 |      8.83 |            1.75 |          7.91 |
| B+2 onward | 15:00       | 60%  | none |      128 |      47.7 |      532562 |      7.92 |            1.54 |          7.65 |
| B+2 onward | 15:00       | none | none |      128 |      48.4 |      530951 |      7.89 |            1.53 |          7.61 |
| B+2 onward | 12:00       | 60%  | none |      123 |      38.2 |      518821 |      7.98 |            1.64 |          7.13 |
| B+2 onward | 15:00       | 40%  | 120% |      128 |      46.9 |      484581 |      7.2  |            1.52 |          6.8  |
| B+2 onward | 12:00       | 40%  | none |      123 |      37.4 |      463267 |      7.13 |            1.53 |          6.36 |
| B+2 onward | 15:30       | 40%  | none |      129 |      45   |      454890 |      6.7  |            1.45 |          6.39 |
| B+2 onward | 15:00       | none | 40%  |      128 |      55.5 |      452791 |      6.73 |            1.68 |          6.13 |
| B+2 onward | 15:00       | 60%  | 120% |      128 |      47.7 |      438829 |      6.52 |            1.45 |          6.21 |

## SHORT - B+3 onward (your script): top 10 variants by total PnL (at least 30 trades)

| set                      | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | 15:00       | 20%  | 60%  |      104 |      45.2 |      487837 |      8.9  |            1.75 |          8.49 |
| B+3 onward (your script) | 15:30       | 20%  | 60%  |      104 |      43.3 |      459067 |      8.37 |            1.69 |          7.92 |
| B+3 onward (your script) | 15:00       | 20%  | 40%  |      104 |      51   |      449039 |      8.19 |            1.77 |          8.15 |
| B+3 onward (your script) | 15:00       | 20%  | 80%  |      104 |      41.3 |      447425 |      8.16 |            1.64 |          7.92 |
| B+3 onward (your script) | 15:30       | 20%  | 40%  |      104 |      49   |      431334 |      7.87 |            1.72 |          7.87 |
| B+3 onward (your script) | 15:30       | 20%  | 80%  |      104 |      39.4 |      418937 |      7.64 |            1.59 |          7.36 |
| B+3 onward (your script) | 09:30       | none | 40%  |      101 |      51.5 |      402374 |      7.57 |            2.21 |          7.45 |
| B+3 onward (your script) | 09:30       | 60%  | 40%  |      101 |      51.5 |      385569 |      7.25 |            2.1  |          7.17 |
| B+3 onward (your script) | 09:30       | 40%  | 40%  |      101 |      51.5 |      383890 |      7.22 |            2.09 |          7.14 |
| B+3 onward (your script) | 09:30       | none | 60%  |      101 |      50.5 |      382995 |      7.21 |            2.14 |          6.9  |

### SHORT - B+1 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |     40% |    60% |    80% |   120% |    none |
|:-----|--------:|-------:|-------:|-------:|--------:|
| none | -103410 |  34603 | -21392 | 110182 | -189288 |
| 20%  |  172513 | 299877 | 270507 | 407679 |  140638 |
| 40%  |   36416 | 174779 | 167496 | 299070 |   15207 |
| 60%  |  -61640 |  87995 |  56359 | 187933 |  -98363 |

### SHORT - B+2 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |    80% |   120% |   none |
|:-----|-------:|-------:|-------:|-------:|-------:|
| none | 364918 | 308741 | 191375 | 334218 | 405460 |
| 20%  | 249231 | 309277 | 243819 | 300175 | 331354 |
| 40%  | 311922 | 343258 | 272935 | 383648 | 454890 |
| 60%  | 321145 | 312914 | 207469 | 306370 | 377612 |

### SHORT - B+3 onward (your script): total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |    80% |    120% |    none |
|:-----|-------:|-------:|-------:|--------:|--------:|
| none | 157078 | 146871 |  76973 | -149498 | -478868 |
| 20%  | 431334 | 459067 | 418937 |  305692 |    1297 |
| 40%  | 345857 | 338312 | 257884 |   63803 | -242617 |
| 60%  | 223053 | 219273 | 164707 |  -38382 | -355002 |

## SHORT - B+1 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | B+1         |       80 |      40   |     -260714 |     -6.17 |            0.75 |         -5.6  |
| B+1 onward | B+2         |        7 |      57.1 |       46165 |     12.35 |            1.91 |         13.16 |
| B+1 onward | B+3         |        4 |      25   |      -22049 |    -10.33 |            0.19 |        -10.52 |
| B+1 onward | B+4         |        1 |     100   |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+2 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |      123 |      46.3 |      379123 |      5.87 |            1.36 |          5.55 |
| B+2 onward | B+3         |        5 |      40   |      -20973 |     -7.72 |            0.22 |         -7.94 |
| B+2 onward | B+4         |        1 |     100   |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+3 onward (your script): result by exact entry day B+n (no SL, no TP, exit 15:30)

| set                      | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | B+3         |      103 |      37.9 |     -526178 |     -9.69 |            0.61 |         -8.77 |
| B+3 onward (your script) | B+4         |        1 |     100   |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+1 onward: its best variant (15:30 | SL 20% | TP 120%) by exact entry day B+n

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | B+1         |       80 |      35   |      377758 |      8.94 |            1.67 |          8.91 |
| B+1 onward | B+2         |        7 |      42.9 |       10900 |      2.92 |            1.26 |          4.39 |
| B+1 onward | B+3         |        4 |      25   |      -28289 |    -13.25 |            0.16 |        -13.45 |
| B+1 onward | B+4         |        1 |     100   |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+2 onward: its best variant (15:00 | SL 40% | TP none) by exact entry day B+n

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |      122 |      46.7 |      545033 |      8.51 |            1.6  |          8.12 |
| B+2 onward | B+3         |        5 |      40   |      -10609 |     -3.91 |            0.51 |         -4.2  |
| B+2 onward | B+4         |        1 |     100   |       43890 |     84.62 |          nan    |         84.62 |

## SHORT - B+3 onward (your script): its best variant (15:00 | SL 20% | TP 60%) by exact entry day B+n

| set                      | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | B+3         |      103 |      44.7 |      455917 |      8.4  |             1.7 |          7.98 |
| B+3 onward (your script) | B+4         |        1 |     100   |       31920 |     61.54 |           nan   |         61.54 |

## SHORT: best variant of every entry rule, year by year (is it one lucky year?)

| set                      | variant                 |   year |   trades |   total_pnl |   win_pct |
|:-------------------------|:------------------------|-------:|---------:|------------:|----------:|
| B+1 onward               | 15:30 | SL 20 | TP 120  |   2026 |       92 |      407679 |      35.9 |
| B+2 onward               | 15:00 | SL 40 | TP none |   2026 |      128 |      578314 |      46.9 |
| B+3 onward (your script) | 15:00 | SL 20 | TP 60   |   2026 |      104 |      487837 |      45.2 |

The best variants are the best of 100 per entry rule, picked after seeing the results, so they are optimistic: check their neighbours (matrices) and the other exits. Charges, taxes, slippage not included. Rows with few trades (some B+n days) are noise. Lot sizes are today's values.
