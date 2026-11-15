# Pure breakout + Bollinger - LONG (call) - all premiums

**B = the breakout day. B+1 = the next trading day, B+2 = the day after, ...**

Entry rules: **B+1 onward** (no skip) | **B+2 onward** (skip only B+1) | **B+3 onward (your script)** (its day counter skips B+1 and B+2). 'noBB' = without the Bollinger filter (only if that data was fetched).

## Entries by entry day (distinct stock/day with option data)

| set                      |   entries |   B+1 |   B+2 |   B+3 |   B+4 |   B+5 |   B+6 or later |
|:-------------------------|----------:|------:|------:|------:|------:|------:|---------------:|
| B+1 onward               |        26 |    23 |     2 |     1 |     0 |     0 |              0 |
| B+2 onward               |        30 |     0 |    30 |     0 |     0 |     0 |              0 |
| B+3 onward (your script) |        21 |     0 |     0 |    21 |     0 |     0 |              0 |

## LONG: no stop-loss, no target, exit 15:30 (hold to the close)

| set                      | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward               | 15:30       | none | none |       26 |      42.3 |     -132309 |    -10.07 |            0.45 |         -8.73 |
| B+2 onward               | 15:30       | none | none |       30 |      23.3 |     -248949 |    -15.77 |            0.33 |        -13.85 |
| B+3 onward (your script) | 15:30       | none | none |       21 |      66.7 |      166096 |     15.69 |            2.1  |         17.11 |

## LONG - B+1 onward: top 10 variants by total PnL (at least 30 trades)

(none)

## LONG - B+2 onward: top 10 variants by total PnL (at least 30 trades)

| set        | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | 15:30       | 20%  | 40%  |       30 |      26.7 |      -93385 |     -5.92 |            0.56 |         -5.14 |
| B+2 onward | 15:00       | 20%  | 40%  |       30 |      26.7 |     -102474 |     -6.49 |            0.51 |         -5.92 |
| B+2 onward | 15:30       | 20%  | 60%  |       30 |      23.3 |     -106069 |     -6.72 |            0.53 |         -5.96 |
| B+2 onward | 15:30       | 40%  | 60%  |       30 |      30   |     -107151 |     -6.79 |            0.61 |         -5.71 |
| B+2 onward | 15:30       | 40%  | 40%  |       30 |      33.3 |     -109663 |     -6.95 |            0.6  |         -5.8  |
| B+2 onward | 15:00       | 20%  | 60%  |       30 |      23.3 |     -118108 |     -7.48 |            0.47 |         -6.93 |
| B+2 onward | 15:00       | 40%  | 40%  |       30 |      33.3 |     -122537 |     -7.76 |            0.55 |         -6.84 |
| B+2 onward | 15:00       | 40%  | 60%  |       30 |      30   |     -122855 |     -7.78 |            0.56 |         -6.92 |
| B+2 onward | 15:30       | 20%  | none |       30 |      20   |     -130816 |     -8.29 |            0.45 |         -7.21 |
| B+2 onward | 15:30       | 20%  | 120% |       30 |      20   |     -130816 |     -8.29 |            0.45 |         -7.21 |

## LONG - B+3 onward (your script): top 10 variants by total PnL (at least 30 trades)

(none)

### LONG - B+1 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |     40% |     60% |     80% |    120% |    none |
|:-----|--------:|--------:|--------:|--------:|--------:|
| none | -118677 | -126519 | -132309 | -132309 | -132309 |
| 20%  |  -59062 |  -62802 |  -68592 |  -68592 |  -68592 |
| 40%  |  -83764 |  -91606 |  -97396 |  -97396 |  -97396 |
| 60%  | -108029 | -115871 | -121661 | -121661 | -121661 |

### LONG - B+2 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |     40% |     60% |     80% |    120% |    none |
|:-----|--------:|--------:|--------:|--------:|--------:|
| none | -162164 | -159652 | -215906 | -248949 | -248949 |
| 20%  |  -93385 | -106069 | -142797 | -130816 | -130816 |
| 40%  | -109663 | -107151 | -144861 | -177904 | -177904 |
| 60%  | -141500 | -138988 | -188516 | -221559 | -221559 |

### LONG - B+3 onward (your script): total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |   60% |    80% |   120% |   none |
|:-----|-------:|------:|-------:|-------:|-------:|
| none |  82051 | 74770 | 110101 | 165151 | 166096 |
| 20%  | 100715 | 99578 | 126665 | 170711 | 171656 |
| 40%  |  90620 | 74639 | 109970 | 165020 | 165965 |
| 60%  |  87068 | 79787 | 115118 | 170168 | 171113 |

## LONG - B+1 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | B+1         |       23 |      39.1 |     -140871 |    -12.23 |            0.31 |        -11.02 |
| B+1 onward | B+2         |        2 |      50   |      -16000 |    -14.38 |            0.57 |        -11.02 |
| B+1 onward | B+3         |        1 |     100   |       24562 |     48.55 |          nan    |         48.55 |

## LONG - B+2 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |       30 |      23.3 |     -248949 |    -15.77 |            0.33 |        -13.85 |

## LONG - B+3 onward (your script): result by exact entry day B+n (no SL, no TP, exit 15:30)

| set                      | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | B+3         |       21 |      66.7 |      166096 |     15.69 |             2.1 |         17.11 |

## LONG - B+2 onward: its best variant (15:30 | SL 20% | TP 40%) by exact entry day B+n

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |       30 |      26.7 |      -93385 |     -5.92 |            0.56 |         -5.14 |

## LONG: best variant of every entry rule, year by year (is it one lucky year?)

| set        | variant               |   year |   trades |   total_pnl |   win_pct |
|:-----------|:----------------------|-------:|---------:|------------:|----------:|
| B+2 onward | 15:30 | SL 20 | TP 40 |   2026 |       30 |      -93385 |      26.7 |

The best variants are the best of 100 per entry rule, picked after seeing the results, so they are optimistic: check their neighbours (matrices) and the other exits. Charges, taxes, slippage not included. Rows with few trades (some B+n days) are noise. Lot sizes are today's values.
