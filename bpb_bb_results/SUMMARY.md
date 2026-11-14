# Pure breakout + Bollinger (LONG call + SHORT put) - raw results, entry checked all day

**Status:** COMPLETE - all 574 request groups finished.

**Period (entry dates):** 2026-09-30 to 2026-10-30  |  **Stocks:** all F&O stocks with Dhan data (210 tried)  |  **Capital per trade:** up to Rs 60,000 (whole lots)

**B = the breakout day; every entry carries its B+n.**

## Rules

PURE BREAKOUT + BOLLINGER (your skip-first-day script).  B = breakout day.  LONG (ATM call): a daily close above the 5-day high (the line) = B; entry level = the High of B; a later close below the line cancels the setup; entry = the first 1-minute candle (09:15 to 15:29) of a day B+m (m >= first allowed day) whose High reaches the level, only if the previous day's close is above the previous day's upper Bollinger band (20, 2).  SHORT (ATM put) = mirror (breakdown day B, Low of B, previous close below the lower band).  Entry rules reported: enter from B+1, from B+2 (skip B+1 only), from B+3 (your script exactly: its day counter skips B+1 and B+2).  Option = ATM of the entry day's month, ITM-1 .. ITM-3 if the ATM series has no candle at the entry minute; no entry is dropped for thin data.  Every entry is tagged with its B+n.

LONG and SHORT are separate: `long/` and `short/` each hold their SUMMARY.md, trades_all_variants.csv.gz and entries.csv.  The strategy results (per entry rule B+1 / B+2 / B+3 and per exact B+n) are in `bpb_bb_report/long/` and `bpb_bb_report/short/`.

## Entries found

| strategy    |   signals_with_entry |   entries_with_option_data |   dropped_low_coverage |   skipped_no_option_data | skip_reasons                                                                                               |
|:------------|---------------------:|---------------------------:|-----------------------:|-------------------------:|:-----------------------------------------------------------------------------------------------------------|
| BPBBB_LONG  |                   76 |                         76 |                      0 |                        0 | nan                                                                                                        |
| BPBBB_SHORT |                  333 |                        313 |                      0 |                       20 | no ATM / ITM-1..ITM-3 candle at the entry minute = 19; Dhan returned no option candles for this period = 1 |
