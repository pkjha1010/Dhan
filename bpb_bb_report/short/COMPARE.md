# Pure breakout + Bollinger - SHORT (put) - all premiums

**B = the breakout day. B+1 = the next trading day, B+2 = the day after, ...**

Entry rules: **B+1 onward** (no skip) | **B+2 onward** (skip only B+1) | **B+3 onward (your script)** (its day counter skips B+1 and B+2). 'noBB' = without the Bollinger filter (only if that data was fetched).

## Entries by entry day (distinct stock/day with option data)

| set                           |   entries |   B+1 |   B+2 |   B+3 |   B+4 |   B+5 |   B+6 or later |
|:------------------------------|----------:|------:|------:|------:|------:|------:|---------------:|
| B+1 onward                    |        86 |    74 |     7 |     4 |     1 |     0 |              0 |
| B+1 onward noBB               |        86 |    74 |     7 |     4 |     1 |     0 |              0 |
| B+2 onward                    |       101 |     0 |    95 |     5 |     1 |     0 |              0 |
| B+2 onward noBB               |       101 |     0 |    95 |     5 |     1 |     0 |              0 |
| B+3 onward (your script)      |        72 |     0 |     0 |    71 |     1 |     0 |              0 |
| B+3 onward (your script) noBB |        72 |     0 |     0 |    71 |     1 |     0 |              0 |

## SHORT: no stop-loss, no target, exit 15:30 (hold to the close)

| set                           | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:------------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward                    | 15:30       | none | none |       86 |      40.7 |      -95891 |     -2.12 |            0.9  |         -1.7  |
| B+1 onward noBB               | 15:30       | none | none |       86 |      40.7 |      -95891 |     -2.12 |            0.9  |         -1.7  |
| B+2 onward                    | 15:30       | none | none |      101 |      48.5 |      470405 |      8.8  |            1.62 |          8.44 |
| B+2 onward noBB               | 15:30       | none | none |      101 |      48.5 |      470405 |      8.8  |            1.62 |          8.44 |
| B+3 onward (your script)      | 15:30       | none | none |       72 |      38.9 |     -468189 |    -12.17 |            0.54 |        -10.77 |
| B+3 onward (your script) noBB | 15:30       | none | none |       72 |      38.9 |     -468189 |    -12.17 |            0.54 |        -10.77 |

## SHORT - B+1 onward: top 10 variants by total PnL (at least 30 trades)

| set        | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | 15:30       | 20%  | 120% |       86 |      36   |      393640 |      8.69 |            1.67 |          8.71 |
| B+1 onward | 15:00       | 20%  | 120% |       86 |      37.2 |      391914 |      8.65 |            1.68 |          8.65 |
| B+1 onward | 15:00       | 40%  | 120% |       86 |      43   |      288153 |      6.36 |            1.38 |          6.22 |
| B+1 onward | 15:30       | 40%  | 120% |       86 |      41.9 |      284137 |      6.27 |            1.36 |          6.14 |
| B+1 onward | 15:00       | 20%  | 80%  |       86 |      37.2 |      279782 |      6.18 |            1.48 |          6.14 |
| B+1 onward | 15:30       | 20%  | 80%  |       86 |      36   |      279688 |      6.17 |            1.48 |          6.18 |
| B+1 onward | 15:30       | 20%  | 60%  |       86 |      38.4 |      270664 |      5.97 |            1.48 |          5.88 |
| B+1 onward | 15:00       | 20%  | 60%  |       86 |      39.5 |      262318 |      5.79 |            1.47 |          5.67 |
| B+1 onward | 15:00       | 20%  | none |       86 |      34.9 |      239038 |      5.28 |            1.39 |          5.48 |
| B+1 onward | 15:00       | 60%  | 120% |       86 |      44.2 |      219413 |      4.84 |            1.26 |          4.86 |

## SHORT - B+1 onward noBB: top 10 variants by total PnL (at least 30 trades)

| set             | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward noBB | 15:30       | 20%  | 120% |       86 |      36   |      393640 |      8.69 |            1.67 |          8.71 |
| B+1 onward noBB | 15:00       | 20%  | 120% |       86 |      37.2 |      391914 |      8.65 |            1.68 |          8.65 |
| B+1 onward noBB | 15:00       | 40%  | 120% |       86 |      43   |      288153 |      6.36 |            1.38 |          6.22 |
| B+1 onward noBB | 15:30       | 40%  | 120% |       86 |      41.9 |      284137 |      6.27 |            1.36 |          6.14 |
| B+1 onward noBB | 15:00       | 20%  | 80%  |       86 |      37.2 |      279782 |      6.18 |            1.48 |          6.14 |
| B+1 onward noBB | 15:30       | 20%  | 80%  |       86 |      36   |      279688 |      6.17 |            1.48 |          6.18 |
| B+1 onward noBB | 15:30       | 20%  | 60%  |       86 |      38.4 |      270664 |      5.97 |            1.48 |          5.88 |
| B+1 onward noBB | 15:00       | 20%  | 60%  |       86 |      39.5 |      262318 |      5.79 |            1.47 |          5.67 |
| B+1 onward noBB | 15:00       | 20%  | none |       86 |      34.9 |      239038 |      5.28 |            1.39 |          5.48 |
| B+1 onward noBB | 15:00       | 60%  | 120% |       86 |      44.2 |      219413 |      4.84 |            1.26 |          4.86 |

## SHORT - B+2 onward: top 10 variants by total PnL (at least 30 trades)

| set        | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | 12:00       | none | none |       95 |      40   |      582943 |     11.52 |            2.11 |         10.53 |
| B+2 onward | 15:00       | none | none |      100 |      50   |      561689 |     10.62 |            1.76 |         10.26 |
| B+2 onward | 15:00       | 40%  | none |      100 |      48   |      535232 |     10.12 |            1.71 |          9.78 |
| B+2 onward | 15:00       | 60%  | none |      100 |      49   |      525815 |      9.94 |            1.69 |          9.67 |
| B+2 onward | 12:00       | 60%  | none |       95 |      38.9 |      521934 |     10.32 |            1.9  |          9.41 |
| B+2 onward | 15:30       | none | none |      101 |      48.5 |      470405 |      8.8  |            1.62 |          8.44 |
| B+2 onward | 15:00       | none | 120% |      100 |      50   |      434351 |      8.21 |            1.59 |          7.84 |
| B+2 onward | 12:00       | 40%  | none |       95 |      37.9 |      429467 |      8.49 |            1.64 |          7.73 |
| B+2 onward | 15:30       | 40%  | none |      101 |      46.5 |      428345 |      8.01 |            1.54 |          7.74 |
| B+2 onward | 15:00       | 60%  | 60%  |      100 |      53   |      409401 |      7.74 |            1.66 |          7.33 |

## SHORT - B+2 onward noBB: top 10 variants by total PnL (at least 30 trades)

| set             | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward noBB | 12:00       | none | none |       95 |      40   |      582943 |     11.52 |            2.11 |         10.53 |
| B+2 onward noBB | 15:00       | none | none |      100 |      50   |      561689 |     10.62 |            1.76 |         10.26 |
| B+2 onward noBB | 15:00       | 40%  | none |      100 |      48   |      535232 |     10.12 |            1.71 |          9.78 |
| B+2 onward noBB | 15:00       | 60%  | none |      100 |      49   |      525815 |      9.94 |            1.69 |          9.67 |
| B+2 onward noBB | 12:00       | 60%  | none |       95 |      38.9 |      521934 |     10.32 |            1.9  |          9.41 |
| B+2 onward noBB | 15:30       | none | none |      101 |      48.5 |      470405 |      8.8  |            1.62 |          8.44 |
| B+2 onward noBB | 15:00       | none | 120% |      100 |      50   |      434351 |      8.21 |            1.59 |          7.84 |
| B+2 onward noBB | 12:00       | 40%  | none |       95 |      37.9 |      429467 |      8.49 |            1.64 |          7.73 |
| B+2 onward noBB | 15:30       | 40%  | none |      101 |      46.5 |      428345 |      8.01 |            1.54 |          7.74 |
| B+2 onward noBB | 15:00       | 60%  | 60%  |      100 |      53   |      409401 |      7.74 |            1.66 |          7.33 |

## SHORT - B+3 onward (your script): top 10 variants by total PnL (at least 30 trades)

| set                      | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | 15:00       | 20%  | 80%  |       72 |      38.9 |      206580 |      5.37 |            1.42 |          5.38 |
| B+3 onward (your script) | 15:30       | 20%  | 80%  |       72 |      38.9 |      205900 |      5.35 |            1.41 |          5.44 |
| B+3 onward (your script) | 15:00       | 20%  | 60%  |       72 |      41.7 |      205062 |      5.33 |            1.43 |          5.24 |
| B+3 onward (your script) | 15:30       | 20%  | 60%  |       72 |      41.7 |      204100 |      5.31 |            1.43 |          5.29 |
| B+3 onward (your script) | 09:30       | none | 40%  |       69 |      49.3 |      199472 |      5.42 |            1.83 |          5.36 |
| B+3 onward (your script) | 09:30       | none | 60%  |       69 |      47.8 |      198007 |      5.38 |            1.82 |          5.25 |
| B+3 onward (your script) | 09:30       | 40%  | 40%  |       69 |      49.3 |      185653 |      5.05 |            1.73 |          5.03 |
| B+3 onward (your script) | 09:30       | 40%  | 60%  |       69 |      47.8 |      184188 |      5.01 |            1.72 |          4.92 |
| B+3 onward (your script) | 09:30       | 60%  | 40%  |       69 |      49.3 |      183572 |      4.99 |            1.72 |          4.97 |
| B+3 onward (your script) | 09:30       | 60%  | 60%  |       69 |      47.8 |      182107 |      4.95 |            1.71 |          4.86 |

## SHORT - B+3 onward (your script) noBB: top 10 variants by total PnL (at least 30 trades)

| set                           | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:------------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) noBB | 15:00       | 20%  | 80%  |       72 |      38.9 |      206580 |      5.37 |            1.42 |          5.38 |
| B+3 onward (your script) noBB | 15:30       | 20%  | 80%  |       72 |      38.9 |      205900 |      5.35 |            1.41 |          5.44 |
| B+3 onward (your script) noBB | 15:00       | 20%  | 60%  |       72 |      41.7 |      205062 |      5.33 |            1.43 |          5.24 |
| B+3 onward (your script) noBB | 15:30       | 20%  | 60%  |       72 |      41.7 |      204100 |      5.31 |            1.43 |          5.29 |
| B+3 onward (your script) noBB | 09:30       | none | 40%  |       69 |      49.3 |      199472 |      5.42 |            1.83 |          5.36 |
| B+3 onward (your script) noBB | 09:30       | none | 60%  |       69 |      47.8 |      198007 |      5.38 |            1.82 |          5.25 |
| B+3 onward (your script) noBB | 09:30       | 40%  | 40%  |       69 |      49.3 |      185653 |      5.05 |            1.73 |          5.03 |
| B+3 onward (your script) noBB | 09:30       | 40%  | 60%  |       69 |      47.8 |      184188 |      5.01 |            1.72 |          4.92 |
| B+3 onward (your script) noBB | 09:30       | 60%  | 40%  |       69 |      49.3 |      183572 |      4.99 |            1.72 |          4.97 |
| B+3 onward (your script) noBB | 09:30       | 60%  | 60%  |       69 |      47.8 |      182107 |      4.95 |            1.71 |          4.86 |

### SHORT - B+1 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |     40% |    60% |    80% |   120% |   none |
|:-----|--------:|-------:|-------:|-------:|-------:|
| none | -163920 |  32321 |  50945 | 159299 | -95891 |
| 20%  |   87547 | 270664 | 279688 | 393640 | 170879 |
| 40%  |  -39466 | 133647 | 175783 | 284137 |  44554 |
| 60%  | -126342 |  69899 |  99495 | 207849 | -34167 |

### SHORT - B+1 onward noBB: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |     40% |    60% |    80% |   120% |   none |
|:-----|--------:|-------:|-------:|-------:|-------:|
| none | -163920 |  32321 |  50945 | 159299 | -95891 |
| 20%  |   87547 | 270664 | 279688 | 393640 | 170879 |
| 40%  |  -39466 | 133647 | 175783 | 284137 |  44554 |
| 60%  | -126342 |  69899 |  99495 | 207849 | -34167 |

### SHORT - B+2 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |    80% |   120% |   none |
|:-----|-------:|-------:|-------:|-------:|-------:|
| none | 353841 | 391179 | 269701 | 392403 | 470405 |
| 20%  | 201433 | 283799 | 214229 | 250444 | 288383 |
| 40%  | 258731 | 334206 | 259771 | 350343 | 428345 |
| 60%  | 297395 | 356284 | 246727 | 325487 | 403489 |

### SHORT - B+2 onward noBB: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |    80% |   120% |   none |
|:-----|-------:|-------:|-------:|-------:|-------:|
| none | 353841 | 391179 | 269701 | 392403 | 470405 |
| 20%  | 201433 | 283799 | 214229 | 250444 | 288383 |
| 40%  | 258731 | 334206 | 259771 | 350343 | 428345 |
| 60%  | 297395 | 356284 | 246727 | 325487 | 403489 |

### SHORT - B+3 onward (your script): total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |     80% |    120% |    none |
|:-----|-------:|-------:|--------:|--------:|--------:|
| none | -76156 | -73272 | -122829 | -284354 | -468189 |
| 20%  | 170169 | 204100 |  205900 |  169161 |  -20299 |
| 40%  | 126083 | 139234 |  118567 |  -10568 | -194403 |
| 60%  | -33961 | -25175 |  -59400 | -197543 | -381378 |

### SHORT - B+3 onward (your script) noBB: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |     80% |    120% |    none |
|:-----|-------:|-------:|--------:|--------:|--------:|
| none | -76156 | -73272 | -122829 | -284354 | -468189 |
| 20%  | 170169 | 204100 |  205900 |  169161 |  -20299 |
| 40%  | 126083 | 139234 |  118567 |  -10568 | -194403 |
| 60%  | -33961 | -25175 |  -59400 | -197543 | -381378 |

## SHORT - B+1 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | B+1         |       74 |      39.2 |     -167317 |     -4.3  |            0.81 |         -3.88 |
| B+1 onward | B+2         |        7 |      57.1 |       46165 |     12.35 |            1.91 |         13.16 |
| B+1 onward | B+3         |        4 |      25   |      -22049 |    -10.33 |            0.19 |        -10.52 |
| B+1 onward | B+4         |        1 |     100   |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+1 onward noBB: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set             | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward noBB | B+1         |       74 |      39.2 |     -167317 |     -4.3  |            0.81 |         -3.88 |
| B+1 onward noBB | B+2         |        7 |      57.1 |       46165 |     12.35 |            1.91 |         13.16 |
| B+1 onward noBB | B+3         |        4 |      25   |      -22049 |    -10.33 |            0.19 |        -10.52 |
| B+1 onward noBB | B+4         |        1 |     100   |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+2 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |       95 |      48.4 |      444068 |      8.84 |            1.6  |          8.43 |
| B+2 onward | B+3         |        5 |      40   |      -20973 |     -7.72 |            0.22 |         -7.94 |
| B+2 onward | B+4         |        1 |     100   |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+2 onward noBB: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set             | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward noBB | B+2         |       95 |      48.4 |      444068 |      8.84 |            1.6  |          8.43 |
| B+2 onward noBB | B+3         |        5 |      40   |      -20973 |     -7.72 |            0.22 |         -7.94 |
| B+2 onward noBB | B+4         |        1 |     100   |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+3 onward (your script): result by exact entry day B+n (no SL, no TP, exit 15:30)

| set                      | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | B+3         |       71 |        38 |     -515499 |    -13.58 |            0.49 |        -12.2  |
| B+3 onward (your script) | B+4         |        1 |       100 |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+3 onward (your script) noBB: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set                           | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:------------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) noBB | B+3         |       71 |        38 |     -515499 |    -13.58 |            0.49 |        -12.2  |
| B+3 onward (your script) noBB | B+4         |        1 |       100 |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+1 onward: its best variant (15:30 | SL 20% | TP 120%) by exact entry day B+n

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | B+1         |       74 |      35.1 |      363719 |      9.35 |            1.71 |          9.21 |
| B+1 onward | B+2         |        7 |      42.9 |       10900 |      2.92 |            1.26 |          4.39 |
| B+1 onward | B+3         |        4 |      25   |      -28289 |    -13.25 |            0.16 |        -13.45 |
| B+1 onward | B+4         |        1 |     100   |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+1 onward noBB: its best variant (15:30 | SL 20% | TP 120%) by exact entry day B+n

| set             | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward noBB | B+1         |       74 |      35.1 |      363719 |      9.35 |            1.71 |          9.21 |
| B+1 onward noBB | B+2         |        7 |      42.9 |       10900 |      2.92 |            1.26 |          4.39 |
| B+1 onward noBB | B+3         |        4 |      25   |      -28289 |    -13.25 |            0.16 |        -13.45 |
| B+1 onward noBB | B+4         |        1 |     100   |       47310 |     91.21 |          nan    |         91.21 |

## SHORT - B+2 onward: its best variant (12:00 | SL none | TP none) by exact entry day B+n

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |       89 |      38.2 |      542958 |     11.46 |            2.06 |         10.41 |
| B+2 onward | B+3         |        5 |      60   |        5785 |      2.13 |            1.38 |          1.42 |
| B+2 onward | B+4         |        1 |     100   |       34200 |     65.93 |          nan    |         65.93 |

## SHORT - B+2 onward noBB: its best variant (12:00 | SL none | TP none) by exact entry day B+n

| set             | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward noBB | B+2         |       89 |      38.2 |      542958 |     11.46 |            2.06 |         10.41 |
| B+2 onward noBB | B+3         |        5 |      60   |        5785 |      2.13 |            1.38 |          1.42 |
| B+2 onward noBB | B+4         |        1 |     100   |       34200 |     65.93 |          nan    |         65.93 |

## SHORT - B+3 onward (your script): its best variant (15:00 | SL 20% | TP 80%) by exact entry day B+n

| set                      | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | B+3         |       71 |        38 |      164970 |      4.35 |            1.33 |          4.33 |
| B+3 onward (your script) | B+4         |        1 |       100 |       41610 |     80.22 |          nan    |         80.22 |

## SHORT - B+3 onward (your script) noBB: its best variant (15:00 | SL 20% | TP 80%) by exact entry day B+n

| set                           | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:------------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) noBB | B+3         |       71 |        38 |      164970 |      4.35 |            1.33 |          4.33 |
| B+3 onward (your script) noBB | B+4         |        1 |       100 |       41610 |     80.22 |          nan    |         80.22 |

## SHORT: best variant of every entry rule, year by year (is it one lucky year?)

| set                           | variant                   |   year |   trades |   total_pnl |   win_pct |
|:------------------------------|:--------------------------|-------:|---------:|------------:|----------:|
| B+1 onward                    | 15:30 | SL 20 | TP 120    |   2026 |       86 |      393640 |      36   |
| B+1 onward noBB               | 15:30 | SL 20 | TP 120    |   2026 |       86 |      393640 |      36   |
| B+2 onward                    | 12:00 | SL none | TP none |   2026 |       95 |      582943 |      40   |
| B+2 onward noBB               | 12:00 | SL none | TP none |   2026 |       95 |      582943 |      40   |
| B+3 onward (your script)      | 15:00 | SL 20 | TP 80     |   2026 |       72 |      206580 |      38.9 |
| B+3 onward (your script) noBB | 15:00 | SL 20 | TP 80     |   2026 |       72 |      206580 |      38.9 |

The best variants are the best of 100 per entry rule, picked after seeing the results, so they are optimistic: check their neighbours (matrices) and the other exits. Charges, taxes, slippage not included. Rows with few trades (some B+n days) are noise. Lot sizes are today's values.
