# Pure breakout + Bollinger - LONG (call) - entry premium above Rs 5

**B = the breakout day. B+1 = the next trading day, B+2 = the day after, ...**

Entry rules: **B+1 onward** (no skip) | **B+2 onward** (skip only B+1) | **B+3 onward (your script)** (its day counter skips B+1 and B+2). 'noBB' = without the Bollinger filter (only if that data was fetched).

## Entries by entry day (distinct stock/day with option data)

| set                      |   entries |   B+1 |   B+2 |   B+3 |   B+4 |   B+5 |   B+6 or later |
|:-------------------------|----------:|------:|------:|------:|------:|------:|---------------:|
| B+1 onward               |        25 |    23 |     1 |     1 |     0 |     0 |              0 |
| B+2 onward               |        26 |     0 |    26 |     0 |     0 |     0 |              0 |
| B+3 onward (your script) |        17 |     0 |     0 |    17 |     0 |     0 |              0 |

## LONG: no stop-loss, no target, exit 15:30 (hold to the close)

| set                      | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward               | 15:30       | none | none |       25 |      44   |      -94709 |     -7.55 |            0.53 |         -6.54 |
| B+2 onward               | 15:30       | none | none |       26 |      26.9 |     -134009 |     -9.91 |            0.47 |         -8.21 |
| B+3 onward (your script) | 15:30       | none | none |       17 |      70.6 |      142053 |     16.96 |            2.41 |         18.58 |

## LONG - B+1 onward: top 10 variants by total PnL (at least 30 trades)

(none)

## LONG - B+2 onward: top 10 variants by total PnL (at least 30 trades)

(none)

## LONG - B+3 onward (your script): top 10 variants by total PnL (at least 30 trades)

(none)

### LONG - B+1 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |    80% |   120% |   none |
|:-----|-------:|-------:|-------:|-------:|-------:|
| none | -81077 | -88919 | -94709 | -94709 | -94709 |
| 20%  | -45462 | -49202 | -54992 | -54992 | -54992 |
| 40%  | -58964 | -66806 | -72596 | -72596 | -72596 |
| 60%  | -72029 | -79871 | -85661 | -85661 | -85661 |

### LONG - B+2 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |     80% |    120% |    none |
|:-----|-------:|-------:|--------:|--------:|--------:|
| none | -47224 | -44712 | -100966 | -134009 | -134009 |
| 20%  | -49905 | -62589 |  -99317 |  -87336 |  -87336 |
| 40%  | -29723 | -27211 |  -64921 |  -97964 |  -97964 |
| 60%  | -36320 | -33808 |  -83336 | -116379 | -116379 |

### LONG - B+3 onward (your script): total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |   40% |   60% |    80% |   120% |   none |
|:-----|------:|------:|-------:|-------:|-------:|
| none | 62568 | 82959 | 106794 | 141108 | 142053 |
| 20%  | 93387 | 80802 |  96393 | 119703 | 120648 |
| 40%  | 59262 | 79653 | 103488 | 137802 | 138747 |
| 60%  | 66960 | 87351 | 111186 | 145500 | 146445 |

## LONG - B+1 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | B+1         |       23 |      39.1 |     -140871 |    -12.23 |            0.31 |        -11.02 |
| B+1 onward | B+2         |        1 |     100   |       21600 |     41.47 |          nan    |         41.47 |
| B+1 onward | B+3         |        1 |     100   |       24562 |     48.55 |          nan    |         48.55 |

## LONG - B+2 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |       26 |      26.9 |     -134009 |     -9.91 |            0.47 |         -8.21 |

## LONG - B+3 onward (your script): result by exact entry day B+n (no SL, no TP, exit 15:30)

| set                      | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | B+3         |       17 |      70.6 |      142053 |     16.96 |            2.41 |         18.58 |

The best variants are the best of 100 per entry rule, picked after seeing the results, so they are optimistic: check their neighbours (matrices) and the other exits. Charges, taxes, slippage not included. Rows with few trades (some B+n days) are noise. Lot sizes are today's values.
