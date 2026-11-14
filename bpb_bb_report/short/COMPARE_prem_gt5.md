# Pure breakout + Bollinger - SHORT (put) - entry premium above Rs 5

**B = the breakout day. B+1 = the next trading day, B+2 = the day after, ...**

Entry rules: **B+1 onward** (no skip) | **B+2 onward** (skip only B+1) | **B+3 onward (your script)** (its day counter skips B+1 and B+2). 'noBB' = without the Bollinger filter (only if that data was fetched).

## Entries by entry day (distinct stock/day with option data)

| set                           |   entries |   B+1 |   B+2 |   B+3 |   B+4 |   B+5 |   B+6 or later |
|:------------------------------|----------:|------:|------:|------:|------:|------:|---------------:|
| B+1 onward                    |        70 |    61 |     5 |     4 |     0 |     0 |              0 |
| B+1 onward noBB               |        70 |    61 |     5 |     4 |     0 |     0 |              0 |
| B+2 onward                    |        80 |     0 |    75 |     5 |     0 |     0 |              0 |
| B+2 onward noBB               |        80 |     0 |    75 |     5 |     0 |     0 |              0 |
| B+3 onward (your script)      |        59 |     0 |     0 |    59 |     0 |     0 |              0 |
| B+3 onward (your script) noBB |        59 |     0 |     0 |    59 |     0 |     0 |              0 |

## SHORT: no stop-loss, no target, exit 15:30 (hold to the close)

| set                           | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:------------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward                    | 15:30       | none | none |       70 |      44.3 |        1399 |      0.04 |            1    |          0.5  |
| B+1 onward noBB               | 15:30       | none | none |       70 |      44.3 |        1399 |      0.04 |            1    |          0.5  |
| B+2 onward                    | 15:30       | none | none |       80 |      53.8 |      573134 |     13.51 |            2.06 |         12.83 |
| B+2 onward noBB               | 15:30       | none | none |       80 |      53.8 |      573134 |     13.51 |            2.06 |         12.83 |
| B+3 onward (your script)      | 15:30       | none | none |       59 |      35.6 |     -498886 |    -15.84 |            0.38 |        -14.47 |
| B+3 onward (your script) noBB | 15:30       | none | none |       59 |      35.6 |     -498886 |    -15.84 |            0.38 |        -14.47 |

## SHORT - B+1 onward: top 10 variants by total PnL (at least 30 trades)

| set        | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | 15:30       | 20%  | 120% |       70 |      38.6 |      376858 |     10.17 |            1.82 |         10.15 |
| B+1 onward | 15:00       | 20%  | 120% |       70 |      40   |      376464 |     10.16 |            1.83 |         10.1  |
| B+1 onward | 15:00       | 20%  | none |       70 |      38.6 |      299272 |      8.08 |            1.64 |          8.29 |
| B+1 onward | 15:30       | 20%  | 60%  |       70 |      41.4 |      297653 |      8.03 |            1.68 |          7.87 |
| B+1 onward | 15:00       | 20%  | 60%  |       70 |      42.9 |      287219 |      7.75 |            1.67 |          7.54 |
| B+1 onward | 15:30       | 20%  | 80%  |       70 |      38.6 |      281405 |      7.6  |            1.61 |          7.55 |
| B+1 onward | 15:00       | 20%  | 80%  |       70 |      40   |      279411 |      7.54 |            1.62 |          7.42 |
| B+1 onward | 15:00       | 40%  | 120% |       70 |      45.7 |      248328 |      6.7  |            1.4  |          6.51 |
| B+1 onward | 15:30       | 40%  | 120% |       70 |      44.3 |      240420 |      6.49 |            1.38 |          6.35 |
| B+1 onward | 15:30       | 20%  | none |       70 |      37.1 |      229781 |      6.2  |            1.48 |          6.5  |

## SHORT - B+1 onward noBB: top 10 variants by total PnL (at least 30 trades)

| set             | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward noBB | 15:30       | 20%  | 120% |       70 |      38.6 |      376858 |     10.17 |            1.82 |         10.15 |
| B+1 onward noBB | 15:00       | 20%  | 120% |       70 |      40   |      376464 |     10.16 |            1.83 |         10.1  |
| B+1 onward noBB | 15:00       | 20%  | none |       70 |      38.6 |      299272 |      8.08 |            1.64 |          8.29 |
| B+1 onward noBB | 15:30       | 20%  | 60%  |       70 |      41.4 |      297653 |      8.03 |            1.68 |          7.87 |
| B+1 onward noBB | 15:00       | 20%  | 60%  |       70 |      42.9 |      287219 |      7.75 |            1.67 |          7.54 |
| B+1 onward noBB | 15:30       | 20%  | 80%  |       70 |      38.6 |      281405 |      7.6  |            1.61 |          7.55 |
| B+1 onward noBB | 15:00       | 20%  | 80%  |       70 |      40   |      279411 |      7.54 |            1.62 |          7.42 |
| B+1 onward noBB | 15:00       | 40%  | 120% |       70 |      45.7 |      248328 |      6.7  |            1.4  |          6.51 |
| B+1 onward noBB | 15:30       | 40%  | 120% |       70 |      44.3 |      240420 |      6.49 |            1.38 |          6.35 |
| B+1 onward noBB | 15:30       | 20%  | none |       70 |      37.1 |      229781 |      6.2  |            1.48 |          6.5  |

## SHORT - B+2 onward: top 10 variants by total PnL (at least 30 trades)

| set        | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | 15:00       | none | none |       79 |      57   |      701443 |     16.77 |            2.43 |         16.01 |
| B+2 onward | 15:00       | 60%  | none |       79 |      55.7 |      664231 |     15.88 |            2.29 |         15.23 |
| B+2 onward | 15:00       | 40%  | none |       79 |      54.4 |      664143 |     15.88 |            2.3  |         15.13 |
| B+2 onward | 12:00       | none | none |       75 |      42.7 |      649055 |     16.2  |            2.61 |         14.88 |
| B+2 onward | 12:00       | 60%  | none |       75 |      41.3 |      588046 |     14.68 |            2.28 |         13.46 |
| B+2 onward | 12:00       | 40%  | none |       75 |      41.3 |      584078 |     14.58 |            2.26 |         13.37 |
| B+2 onward | 15:00       | none | 120% |       79 |      57   |      574105 |     13.73 |            2.17 |         12.95 |
| B+2 onward | 15:30       | none | none |       80 |      53.8 |      573134 |     13.51 |            2.06 |         12.83 |
| B+2 onward | 15:30       | 40%  | none |       80 |      51.2 |      551305 |     13    |            2.01 |         12.34 |
| B+2 onward | 15:00       | 60%  | 120% |       79 |      55.7 |      536893 |     12.84 |            2.04 |         12.17 |

## SHORT - B+2 onward noBB: top 10 variants by total PnL (at least 30 trades)

| set             | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward noBB | 15:00       | none | none |       79 |      57   |      701443 |     16.77 |            2.43 |         16.01 |
| B+2 onward noBB | 15:00       | 60%  | none |       79 |      55.7 |      664231 |     15.88 |            2.29 |         15.23 |
| B+2 onward noBB | 15:00       | 40%  | none |       79 |      54.4 |      664143 |     15.88 |            2.3  |         15.13 |
| B+2 onward noBB | 12:00       | none | none |       75 |      42.7 |      649055 |     16.2  |            2.61 |         14.88 |
| B+2 onward noBB | 12:00       | 60%  | none |       75 |      41.3 |      588046 |     14.68 |            2.28 |         13.46 |
| B+2 onward noBB | 12:00       | 40%  | none |       75 |      41.3 |      584078 |     14.58 |            2.26 |         13.37 |
| B+2 onward noBB | 15:00       | none | 120% |       79 |      57   |      574105 |     13.73 |            2.17 |         12.95 |
| B+2 onward noBB | 15:30       | none | none |       80 |      53.8 |      573134 |     13.51 |            2.06 |         12.83 |
| B+2 onward noBB | 15:30       | 40%  | none |       80 |      51.2 |      551305 |     13    |            2.01 |         12.34 |
| B+2 onward noBB | 15:00       | 60%  | 120% |       79 |      55.7 |      536893 |     12.84 |            2.04 |         12.17 |

## SHORT - B+3 onward (your script): top 10 variants by total PnL (at least 30 trades)

| set                      | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | 09:30       | none | 60%  |       56 |      42.9 |       89940 |      3.02 |            1.41 |          2.97 |
| B+3 onward (your script) | 09:30       | 40%  | 60%  |       56 |      42.9 |       84334 |      2.83 |            1.37 |          2.82 |
| B+3 onward (your script) | 09:30       | 60%  | 60%  |       56 |      42.9 |       74040 |      2.48 |            1.31 |          2.5  |
| B+3 onward (your script) | 09:30       | none | 120% |       56 |      42.9 |       63167 |      2.12 |            1.29 |          2.18 |
| B+3 onward (your script) | 09:30       | none | 40%  |       56 |      44.6 |       62401 |      2.09 |            1.28 |          2.11 |
| B+3 onward (your script) | 15:00       | 20%  | 60%  |       59 |      39   |       57806 |      1.84 |            1.15 |          1.8  |
| B+3 onward (your script) | 09:30       | 40%  | 120% |       56 |      42.9 |       57561 |      1.93 |            1.25 |          2.02 |
| B+3 onward (your script) | 09:30       | 40%  | 40%  |       56 |      44.6 |       56795 |      1.9  |            1.25 |          1.96 |
| B+3 onward (your script) | 15:30       | 20%  | 60%  |       59 |      39   |       56304 |      1.79 |            1.14 |          1.84 |
| B+3 onward (your script) | 15:00       | 20%  | 40%  |       59 |      44.1 |       51640 |      1.64 |            1.14 |          1.65 |

## SHORT - B+3 onward (your script) noBB: top 10 variants by total PnL (at least 30 trades)

| set                           | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:------------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) noBB | 09:30       | none | 60%  |       56 |      42.9 |       89940 |      3.02 |            1.41 |          2.97 |
| B+3 onward (your script) noBB | 09:30       | 40%  | 60%  |       56 |      42.9 |       84334 |      2.83 |            1.37 |          2.82 |
| B+3 onward (your script) noBB | 09:30       | 60%  | 60%  |       56 |      42.9 |       74040 |      2.48 |            1.31 |          2.5  |
| B+3 onward (your script) noBB | 09:30       | none | 120% |       56 |      42.9 |       63167 |      2.12 |            1.29 |          2.18 |
| B+3 onward (your script) noBB | 09:30       | none | 40%  |       56 |      44.6 |       62401 |      2.09 |            1.28 |          2.11 |
| B+3 onward (your script) noBB | 15:00       | 20%  | 60%  |       59 |      39   |       57806 |      1.84 |            1.15 |          1.8  |
| B+3 onward (your script) noBB | 09:30       | 40%  | 120% |       56 |      42.9 |       57561 |      1.93 |            1.25 |          2.02 |
| B+3 onward (your script) noBB | 09:30       | 40%  | 40%  |       56 |      44.6 |       56795 |      1.9  |            1.25 |          1.96 |
| B+3 onward (your script) noBB | 15:30       | 20%  | 60%  |       59 |      39   |       56304 |      1.79 |            1.14 |          1.84 |
| B+3 onward (your script) noBB | 15:00       | 20%  | 40%  |       59 |      44.1 |       51640 |      1.64 |            1.14 |          1.65 |

### SHORT - B+1 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |    80% |   120% |   none |
|:-----|-------:|-------:|-------:|-------:|-------:|
| none | -51249 | 110564 |  87122 | 182575 |   1399 |
| 20%  | 137768 | 297653 | 281405 | 376858 | 229781 |
| 40%  |   6212 | 144897 | 144967 | 240420 |  85981 |
| 60%  | -40703 | 121110 | 108640 | 204093 |  36091 |

### SHORT - B+1 onward noBB: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |    80% |   120% |   none |
|:-----|-------:|-------:|-------:|-------:|-------:|
| none | -51249 | 110564 |  87122 | 182575 |   1399 |
| 20%  | 137768 | 297653 | 281405 | 376858 | 229781 |
| 40%  |   6212 | 144897 | 144967 | 240420 |  85981 |
| 60%  | -40703 | 121110 | 108640 | 204093 |  36091 |

### SHORT - B+2 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |    80% |   120% |   none |
|:-----|-------:|-------:|-------:|-------:|-------:|
| none | 349646 | 440571 | 378130 | 495132 | 573134 |
| 20%  | 160444 | 301235 | 259977 | 290492 | 328431 |
| 40%  | 264084 | 423350 | 388431 | 473303 | 551305 |
| 60%  | 294408 | 442404 | 385094 | 458154 | 536156 |

### SHORT - B+2 onward noBB: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |    80% |   120% |   none |
|:-----|-------:|-------:|-------:|-------:|-------:|
| none | 349646 | 440571 | 378130 | 495132 | 573134 |
| 20%  | 160444 | 301235 | 259977 | 290492 | 328431 |
| 40%  | 264084 | 423350 | 388431 | 473303 | 551305 |
| 60%  | 294408 | 442404 | 385094 | 458154 | 536156 |

### SHORT - B+3 onward (your script): total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |     40% |     60% |     80% |    120% |    none |
|:-----|--------:|--------:|--------:|--------:|--------:|
| none | -115934 | -138678 | -261268 | -343441 | -498886 |
| 20%  |   49441 |   56304 |  -14929 |     -97 | -161167 |
| 40%  |   25849 |   13372 |  -80328 | -152019 | -307464 |
| 60%  |  -88362 | -105204 | -212462 | -281572 | -437017 |

### SHORT - B+3 onward (your script) noBB: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |     40% |     60% |     80% |    120% |    none |
|:-----|--------:|--------:|--------:|--------:|--------:|
| none | -115934 | -138678 | -261268 | -343441 | -498886 |
| 20%  |   49441 |   56304 |  -14929 |     -97 | -161167 |
| 40%  |   25849 |   13372 |  -80328 | -152019 | -307464 |
| 60%  |  -88362 | -105204 | -212462 | -281572 | -437017 |

## SHORT - B+1 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | B+1         |       61 |      45.9 |       32952 |      1.02 |            1.05 |          1.39 |
| B+1 onward | B+2         |        5 |      40   |       -9504 |     -3.61 |            0.81 |         -1.57 |
| B+1 onward | B+3         |        4 |      25   |      -22049 |    -10.33 |            0.19 |        -10.52 |

## SHORT - B+1 onward noBB: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set             | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward noBB | B+1         |       61 |      45.9 |       32952 |      1.02 |            1.05 |          1.39 |
| B+1 onward noBB | B+2         |        5 |      40   |       -9504 |     -3.61 |            0.81 |         -1.57 |
| B+1 onward noBB | B+3         |        4 |      25   |      -22049 |    -10.33 |            0.19 |        -10.52 |

## SHORT - B+2 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |       75 |      54.7 |      594107 |     14.97 |            2.16 |         14.22 |
| B+2 onward | B+3         |        5 |      40   |      -20973 |     -7.72 |            0.22 |         -7.94 |

## SHORT - B+2 onward noBB: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set             | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward noBB | B+2         |       75 |      54.7 |      594107 |     14.97 |            2.16 |         14.22 |
| B+2 onward noBB | B+3         |        5 |      40   |      -20973 |     -7.72 |            0.22 |         -7.94 |

## SHORT - B+3 onward (your script): result by exact entry day B+n (no SL, no TP, exit 15:30)

| set                      | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | B+3         |       59 |      35.6 |     -498886 |    -15.84 |            0.38 |        -14.47 |

## SHORT - B+3 onward (your script) noBB: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set                           | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:------------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) noBB | B+3         |       59 |      35.6 |     -498886 |    -15.84 |            0.38 |        -14.47 |

## SHORT - B+1 onward: its best variant (15:30 | SL 20% | TP 120%) by exact entry day B+n

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | B+1         |       61 |      39.3 |      393936 |     12.2  |            1.99 |         12.03 |
| B+1 onward | B+2         |        5 |      40   |       11211 |      4.26 |            1.37 |          6.14 |
| B+1 onward | B+3         |        4 |      25   |      -28289 |    -13.25 |            0.16 |        -13.45 |

## SHORT - B+1 onward noBB: its best variant (15:30 | SL 20% | TP 120%) by exact entry day B+n

| set             | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward noBB | B+1         |       61 |      39.3 |      393936 |     12.2  |            1.99 |         12.03 |
| B+1 onward noBB | B+2         |        5 |      40   |       11211 |      4.26 |            1.37 |          6.14 |
| B+1 onward noBB | B+3         |        4 |      25   |      -28289 |    -13.25 |            0.16 |        -13.45 |

## SHORT - B+2 onward: its best variant (15:00 | SL none | TP none) by exact entry day B+n

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |       74 |      58.1 |      712052 |     18.21 |            2.51 |         17.38 |
| B+2 onward | B+3         |        5 |      40   |      -10609 |     -3.91 |            0.51 |         -4.2  |

## SHORT - B+2 onward noBB: its best variant (15:00 | SL none | TP none) by exact entry day B+n

| set             | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward noBB | B+2         |       74 |      58.1 |      712052 |     18.21 |            2.51 |         17.38 |
| B+2 onward noBB | B+3         |        5 |      40   |      -10609 |     -3.91 |            0.51 |         -4.2  |

## SHORT - B+3 onward (your script): its best variant (09:30 | SL none | TP 60%) by exact entry day B+n

| set                      | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | B+3         |       56 |      42.9 |       89940 |      3.02 |            1.41 |          2.97 |

## SHORT - B+3 onward (your script) noBB: its best variant (09:30 | SL none | TP 60%) by exact entry day B+n

| set                           | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:------------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) noBB | B+3         |       56 |      42.9 |       89940 |      3.02 |            1.41 |          2.97 |

## SHORT: best variant of every entry rule, year by year (is it one lucky year?)

| set                           | variant                   |   year |   trades |   total_pnl |   win_pct |
|:------------------------------|:--------------------------|-------:|---------:|------------:|----------:|
| B+1 onward                    | 15:30 | SL 20 | TP 120    |   2026 |       70 |      376858 |      38.6 |
| B+1 onward noBB               | 15:30 | SL 20 | TP 120    |   2026 |       70 |      376858 |      38.6 |
| B+2 onward                    | 15:00 | SL none | TP none |   2026 |       79 |      701443 |      57   |
| B+2 onward noBB               | 15:00 | SL none | TP none |   2026 |       79 |      701443 |      57   |
| B+3 onward (your script)      | 09:30 | SL none | TP 60   |   2026 |       56 |       89940 |      42.9 |
| B+3 onward (your script) noBB | 09:30 | SL none | TP 60   |   2026 |       56 |       89940 |      42.9 |

The best variants are the best of 100 per entry rule, picked after seeing the results, so they are optimistic: check their neighbours (matrices) and the other exits. Charges, taxes, slippage not included. Rows with few trades (some B+n days) are noise. Lot sizes are today's values.
