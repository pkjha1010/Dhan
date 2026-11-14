# Pure breakout + Bollinger - LONG (ATM call) - raw trades, entry checked all day

**Status:** COMPLETE - all 574 request groups finished.

**Period (entry dates):** 2026-09-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

**B = the breakout day.** B+1 = the next trading day, B+2 = the day after, ... every entry below carries its B+n (`b_plus`, `b_label`, `breakout_date`).

## Rule

Pure breakout LONG: close above the 5-day high = breakout day B, level = High of B, a close below the line cancels -> first 1-minute cross above the level on B+m (full day) -> buy CALL; previous-day close above the upper Bollinger band

**Grid:** stop-loss no SL, SL 20%, SL 40%, SL 60% x target TP 40%, TP 60%, TP 80%, TP 120%, no TP x time exit 09:30, 10:00, 12:00, 15:00, 15:30 = 100 variants. Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.

## Entries found (all three entry rules together, each entry once)

| strategy   |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data |   skip_reasons |
|:-----------|---------------------:|---------------------------:|-----------------------:|-------------------------:|---------------:|
| BPBBB_LONG |                   76 |                         76 |                      0 |                        0 |            nan |

## Entries by entry day (B+n)

| entry_day   |   b_plus |   entries_found |   with_option_data |
|:------------|---------:|----------------:|-------------------:|
| B+1         |        1 |              23 |                 23 |
| B+2         |        2 |              31 |                 31 |
| B+3         |        3 |              22 |                 22 |

## Strike used

strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): 0: 76

## Where are the results?

`bpb_bb_report/long/COMPARE.md` (enter from B+1 / B+2 / B+3, every exit x stop-loss x target, and by exact entry day B+n). This folder holds the raw material: `trades_all_variants.csv.gz` (7220 rows: every trade of every variant, filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none; columns from_b1 / from_b2 / from_b3 = 1 when that entry rule takes the entry) and `entries.csv` (one row per entry: breakout date, B+n, level, strike, expiry, option price, coverage). The pooled summary.csv in the parent folder mixes the three entry rules - do not read it as a strategy.

Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.
