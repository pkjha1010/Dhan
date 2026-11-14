# Pure breakout + Bollinger - LONG (call) - entry premium above Rs 5

**B = the breakout day. B+1 = the next trading day, B+2 = the day after, ...**

Entry rules: **B+1 onward** (no skip) | **B+2 onward** (skip only B+1) | **B+3 onward (your script)** (its day counter skips B+1 and B+2). 'noBB' = without the Bollinger filter (only if that data was fetched).

## Entries by entry day (distinct stock/day with option data)

| set                           |   entries |   B+1 |   B+2 |   B+3 |   B+4 |   B+5 |   B+6 or later |
|:------------------------------|----------:|------:|------:|------:|------:|------:|---------------:|
| B+1 onward                    |        24 |    22 |     1 |     1 |     0 |     0 |              0 |
| B+1 onward noBB               |        24 |    22 |     1 |     1 |     0 |     0 |              0 |
| B+2 onward                    |        26 |     0 |    26 |     0 |     0 |     0 |              0 |
| B+2 onward noBB               |        26 |     0 |    26 |     0 |     0 |     0 |              0 |
| B+3 onward (your script)      |        15 |     0 |     0 |    15 |     0 |     0 |              0 |
| B+3 onward (your script) noBB |        15 |     0 |     0 |    15 |     0 |     0 |              0 |

## LONG: no stop-loss, no target, exit 15:30 (hold to the close)

| set                           | exit_rule   | sl   | tp   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:------------------------------|:------------|:-----|:-----|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward                    | 15:30       | none | none |       24 |      41.7 |     -101861 |     -8.37 |            0.5  |         -7.6  |
| B+1 onward noBB               | 15:30       | none | none |       24 |      41.7 |     -101861 |     -8.37 |            0.5  |         -7.6  |
| B+2 onward                    | 15:30       | none | none |       26 |      26.9 |     -134009 |     -9.91 |            0.47 |         -8.21 |
| B+2 onward noBB               | 15:30       | none | none |       26 |      26.9 |     -134009 |     -9.91 |            0.47 |         -8.21 |
| B+3 onward (your script)      | 15:30       | none | none |       15 |      66.7 |      112930 |     14.97 |            2.12 |         16.52 |
| B+3 onward (your script) noBB | 15:30       | none | none |       15 |      66.7 |      112930 |     14.97 |            2.12 |         16.52 |

## LONG - B+1 onward: top 10 variants by total PnL (at least 30 trades)

(none)

## LONG - B+1 onward noBB: top 10 variants by total PnL (at least 30 trades)

(none)

## LONG - B+2 onward: top 10 variants by total PnL (at least 30 trades)

(none)

## LONG - B+2 onward noBB: top 10 variants by total PnL (at least 30 trades)

(none)

## LONG - B+3 onward (your script): top 10 variants by total PnL (at least 30 trades)

(none)

## LONG - B+3 onward (your script) noBB: top 10 variants by total PnL (at least 30 trades)

(none)

### LONG - B+1 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |     80% |    120% |    none |
|:-----|-------:|-------:|--------:|--------:|--------:|
| none | -88229 | -96071 | -101861 | -101861 | -101861 |
| 20%  | -52614 | -56354 |  -62144 |  -62144 |  -62144 |
| 40%  | -66116 | -73958 |  -79748 |  -79748 |  -79748 |
| 60%  | -79181 | -87023 |  -92813 |  -92813 |  -92813 |

### LONG - B+1 onward noBB: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |     80% |    120% |    none |
|:-----|-------:|-------:|--------:|--------:|--------:|
| none | -88229 | -96071 | -101861 | -101861 | -101861 |
| 20%  | -52614 | -56354 |  -62144 |  -62144 |  -62144 |
| 40%  | -66116 | -73958 |  -79748 |  -79748 |  -79748 |
| 60%  | -79181 | -87023 |  -92813 |  -92813 |  -92813 |

### LONG - B+2 onward: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |     80% |    120% |    none |
|:-----|-------:|-------:|--------:|--------:|--------:|
| none | -47224 | -44712 | -100966 | -134009 | -134009 |
| 20%  | -49905 | -62589 |  -99317 |  -87336 |  -87336 |
| 40%  | -29723 | -27211 |  -64921 |  -97964 |  -97964 |
| 60%  | -36320 | -33808 |  -83336 | -116379 | -116379 |

### LONG - B+2 onward noBB: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |    40% |    60% |     80% |    120% |    none |
|:-----|-------:|-------:|--------:|--------:|--------:|
| none | -47224 | -44712 | -100966 | -134009 | -134009 |
| 20%  | -49905 | -62589 |  -99317 |  -87336 |  -87336 |
| 40%  | -29723 | -27211 |  -64921 |  -97964 |  -97964 |
| 60%  | -36320 | -33808 |  -83336 | -116379 | -116379 |

### LONG - B+3 onward (your script): total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |   40% |   60% |   80% |   120% |   none |
|:-----|------:|------:|------:|-------:|-------:|
| none | 28075 | 53836 | 77671 | 111985 | 112930 |
| 20%  | 58894 | 51679 | 67270 |  90580 |  91525 |
| 40%  | 24769 | 50530 | 74365 | 108679 | 109624 |
| 60%  | 32467 | 58228 | 82063 | 116377 | 117322 |

### LONG - B+3 onward (your script) noBB: total PnL (Rs), exit 15:30, rows stop-loss, columns target

| sl   |   40% |   60% |   80% |   120% |   none |
|:-----|------:|------:|------:|-------:|-------:|
| none | 28075 | 53836 | 77671 | 111985 | 112930 |
| 20%  | 58894 | 51679 | 67270 |  90580 |  91525 |
| 40%  | 24769 | 50530 | 74365 | 108679 | 109624 |
| 60%  | 32467 | 58228 | 82063 | 116377 | 117322 |

## LONG - B+1 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward | B+1         |       22 |      36.4 |     -148023 |    -13.28 |            0.27 |        -12.39 |
| B+1 onward | B+2         |        1 |     100   |       21600 |     41.47 |          nan    |         41.47 |
| B+1 onward | B+3         |        1 |     100   |       24562 |     48.55 |          nan    |         48.55 |

## LONG - B+1 onward noBB: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set             | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+1 onward noBB | B+1         |       22 |      36.4 |     -148023 |    -13.28 |            0.27 |        -12.39 |
| B+1 onward noBB | B+2         |        1 |     100   |       21600 |     41.47 |          nan    |         41.47 |
| B+1 onward noBB | B+3         |        1 |     100   |       24562 |     48.55 |          nan    |         48.55 |

## LONG - B+2 onward: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set        | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-----------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward | B+2         |       26 |      26.9 |     -134009 |     -9.91 |            0.47 |         -8.21 |

## LONG - B+2 onward noBB: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set             | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:----------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+2 onward noBB | B+2         |       26 |      26.9 |     -134009 |     -9.91 |            0.47 |         -8.21 |

## LONG - B+3 onward (your script): result by exact entry day B+n (no SL, no TP, exit 15:30)

| set                      | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:-------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) | B+3         |       15 |      66.7 |      112930 |     14.97 |            2.12 |         16.52 |

## LONG - B+3 onward (your script) noBB: result by exact entry day B+n (no SL, no TP, exit 15:30)

| set                           | entry_day   |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   avg_ret_pct |
|:------------------------------|:------------|---------:|----------:|------------:|----------:|----------------:|--------------:|
| B+3 onward (your script) noBB | B+3         |       15 |      66.7 |      112930 |     14.97 |            2.12 |         16.52 |

The best variants are the best of 100 per entry rule, picked after seeing the results, so they are optimistic: check their neighbours (matrices) and the other exits. Charges, taxes, slippage not included. Rows with few trades (some B+n days) are noise. Lot sizes are today's values.
