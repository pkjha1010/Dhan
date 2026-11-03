# BPB BASE - survivors after cutting the top 10 % of trades (premium > Rs 5, min 30 trades, trimmed PF >= 1.2)

Survivors per set / direction (all-day = whole day pooled, by-slot = per entry-time slot):

| set       | direction   | scope   |   combos |   profitable_after_cut |   survivors |   month_survivors |   best_trim_pf |
|:----------|:------------|:--------|---------:|-----------------------:|------------:|------------------:|---------------:|
| nifty     | LONG        | all-day |       40 |                      0 |           0 |                 0 |           0.45 |
| nifty     | LONG        | by-slot |      260 |                     15 |          13 |                 1 |           1.75 |
| nifty     | SHORT       | all-day |       40 |                      0 |           0 |                 0 |           0.69 |
| nifty     | SHORT       | by-slot |      280 |                     12 |           5 |                 3 |           1.5  |
| no filter | LONG        | all-day |       40 |                      0 |           0 |                 0 |           0.59 |
| no filter | LONG        | by-slot |      280 |                      9 |           2 |                 0 |           1.24 |
| no filter | SHORT       | all-day |       40 |                      0 |           0 |                 0 |           0.63 |
| no filter | SHORT       | by-slot |      280 |                      4 |           0 |                 0 |           1.1  |

## no filter - LONG: top 10 survivors, whole day pooled

(none)

## no filter - LONG: top 10 survivors by entry-time slot

| set       | direction   | slot        | exit_rule   | sl   | tp   |   trades |   cut |   trim_pnl |   trim_pf |   trim_win_pct |   months_profit |   months_with_trades |   months_profit_pct |   worst_month |
|:----------|:------------|:------------|:------------|:-----|:-----|---------:|------:|-----------:|----------:|---------------:|----------------:|---------------------:|--------------------:|--------------:|
| no filter | LONG        | 12:00-12:59 | 15:00       | none | 60%  |       73 |     8 |      49343 |      1.24 |           50.8 |              16 |                   28 |                57.1 |        -21707 |
| no filter | LONG        | 12:00-12:59 | 15:00       | none | 80%  |       73 |     8 |      48593 |      1.24 |           50.8 |              16 |                   28 |                57.1 |        -21707 |

## no filter - SHORT: top 10 survivors, whole day pooled

(none)

## no filter - SHORT: top 10 survivors by entry-time slot

(none)

## nifty - LONG: top 10 survivors, whole day pooled

(none)

## nifty - LONG: top 10 survivors by entry-time slot

| set   | direction   | slot        | exit_rule   | sl   | tp   |   trades |   cut |   trim_pnl |   trim_pf |   trim_win_pct |   months_profit |   months_with_trades |   months_profit_pct |   worst_month |
|:------|:------------|:------------|:------------|:-----|:-----|---------:|------:|-----------:|----------:|---------------:|----------------:|---------------------:|--------------------:|--------------:|
| nifty | LONG        | 12:00-12:59 | 15:30       | none | 80%  |       48 |     5 |     118726 |      1.71 |           46.5 |              10 |                   21 |                47.6 |        -36357 |
| nifty | LONG        | 12:00-12:59 | 15:30       | none | 60%  |       48 |     5 |      99680 |      1.6  |           46.5 |               9 |                   21 |                42.9 |        -36357 |
| nifty | LONG        | 12:00-12:59 | 15:00       | none | 60%  |       48 |     5 |      98299 |      1.75 |           53.5 |              12 |                   21 |                57.1 |        -17077 |
| nifty | LONG        | 12:00-12:59 | 15:00       | none | 80%  |       48 |     5 |      86371 |      1.66 |           53.5 |              13 |                   21 |                61.9 |        -17077 |
| nifty | LONG        | 12:00-12:59 | 15:00       | 60%  | 60%  |       48 |     5 |      54323 |      1.33 |           51.2 |              11 |                   21 |                52.4 |        -35466 |
| nifty | LONG        | 12:00-12:59 | 15:30       | 40%  | 80%  |       48 |     5 |      52833 |      1.28 |           44.2 |              10 |                   21 |                47.6 |        -30582 |
| nifty | LONG        | 12:00-12:59 | 15:00       | 40%  | 60%  |       48 |     5 |      51684 |      1.31 |           51.2 |              11 |                   21 |                52.4 |        -27314 |
| nifty | LONG        | 12:00-12:59 | 15:30       | 40%  | 60%  |       48 |     5 |      44507 |      1.24 |           44.2 |               8 |                   21 |                38.1 |        -30582 |
| nifty | LONG        | 12:00-12:59 | 15:00       | 60%  | 80%  |       48 |     5 |      42395 |      1.26 |           51.2 |              12 |                   21 |                57.1 |        -35466 |
| nifty | LONG        | 12:00-12:59 | 15:00       | none | none |       48 |     5 |      39886 |      1.31 |           51.2 |              12 |                   21 |                57.1 |        -19360 |

## nifty - SHORT: top 10 survivors, whole day pooled

(none)

## nifty - SHORT: top 10 survivors by entry-time slot

| set   | direction   | slot        | exit_rule   | sl   | tp   |   trades |   cut |   trim_pnl |   trim_pf |   trim_win_pct |   months_profit |   months_with_trades |   months_profit_pct |   worst_month |
|:------|:------------|:------------|:------------|:-----|:-----|---------:|------:|-----------:|----------:|---------------:|----------------:|---------------------:|--------------------:|--------------:|
| nifty | SHORT       | 12:00-12:59 | 15:30       | 40%  | 60%  |       36 |     4 |      86064 |      1.5  |           53.1 |              11 |                   17 |                64.7 |        -52590 |
| nifty | SHORT       | 12:00-12:59 | 15:00       | 40%  | 60%  |       36 |     4 |      67165 |      1.38 |           50   |               9 |                   17 |                52.9 |        -51567 |
| nifty | SHORT       | 12:00-12:59 | 15:30       | 60%  | 60%  |       36 |     4 |      51331 |      1.25 |           53.1 |              11 |                   17 |                64.7 |        -56458 |
| nifty | SHORT       | 12:00-12:59 | 15:30       | 60%  | 80%  |       36 |     4 |      43825 |      1.21 |           53.1 |              11 |                   17 |                64.7 |        -56458 |
| nifty | SHORT       | 12:00-12:59 | 15:00       | 60%  | 60%  |       36 |     4 |      40582 |      1.2  |           50   |               9 |                   17 |                52.9 |        -58473 |
