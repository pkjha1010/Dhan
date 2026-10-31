# SWG swing strategy – options backtest (Dhan 1-minute data)

Backtests the signals from `swing_alerts.py` by buying the ATM stock option
(LONG -> CE, SHORT -> PE) on the next trading day, using Dhan 1-minute candles.

## Setup
1. Add `backtest_options.py`, `requirements.txt` and `.github/workflows/options-backtest.yml` to your repo.
2. Repo secrets (Settings -> Secrets and variables -> Actions): `DHAN_ACCESS_TOKEN`, `DHAN_CLIENT_ID`.
   The Dhan token must still be valid when the run starts.
3. Actions -> "SWG options backtest (Dhan 1-min)" -> Run workflow.
   Quick test first: `symbols = RELIANCE,SBIN,INFY`, then run it again with `symbols` blank.

## What it does
| Step | Source |
|---|---|
| Trading calendar, daily candles, signals (same `shape()` + `setup()`) | Yahoo |
| Entry-day 1-minute stock candles (only if Yahoo's daily High/Low touched the line) | Dhan `/v2/charts/intraday` |
| 1-minute option candles, strike locked at the entry ATM | Dhan `/v2/charts/rollingoption` (expired options) |

Variants (3 x 2 x 9 x 4 = 216):
* Entry types: `ALERT` = first touch from 09:15, same as the Kite alert. `CONFIRM` = from 09:20, a 1-minute close
  crosses the line after 4 closes on the other side. `RECROSS` = the CONFIRM cross, then a close back, then entry on the re-cross.
* SL 10 / 20 % of premium; TP 20, 30, 40, 60, 80, 100, 120, 140, 200 %.
* Exit: 10:00, 12:00, 15:30 (the first one after entry; if that time has passed, the next day), or `HIT` (hold until SL/TP, capped at the expiry-day close).
* Capital per trade: up to ₹2,00,000 for SL10 and ₹1,00,000 for SL20, in whole lots.
* Fill: the option's next 1-minute open after the signal minute. SL wins if SL and TP fall in the same candle. A gap through SL or TP fills at the open.
* Costs: ₹20 per order, STT, exchange charges, SEBI fee, stamp duty and GST, plus 0.5% slippage per side.

## API limits
* Rate limiter at 4 requests per second (Dhan's data limit is 5/s and 100,000/day), with backoff on 429 / DH-904.
* Every response is cached in `cache/` and kept between runs with `actions/cache`. If a run stops at
  `max_requests` or 300 minutes, run it again and it continues from where it stopped.
* Rough cost of the full 2023-01 to 2026-09 run: about 7,400 entry-day candidates, about 30–40k calls.

## Outputs (run artifact `backtest-results-N`)
`summary.md` (also shown on the run page), `summary_by_variant.csv`, `trades_all_variants.csv.gz`,
`signals.csv`, `skipped.csv` (with the reason each setup was skipped).

## Known limitations
* Lot sizes come from today's Dhan scrip master. For historical lot sizes, add `lot_sizes.csv`
  (`symbol,from_date,lot`).
* Stocks that are no longer in F&O have no Dhan ID and are skipped.
* Dhan only serves ATM-3..ATM+3 for stock options. If the stock moves further than that while the trade
  is open, the trade exits on the last available candle with reason `DATA_GAP`.
* If entry happens on expiry day, the next month's contract is used (`--roll-on-expiry-day 0` turns this off).

## MR-POC backtest (mean reversion to POC + last-hour fade)

`mr_poc_backtest.py` - sideways stocks that gap into a low-volume node, revert to the session POC and print a small counter-trend last-hour candle.
Next morning the 1-minute stock candles (09:15 until just before the exit time) trigger an ATM option trade when Day-1 High / Low breaks; SL 10 % of premium, time exit 09:30.
Run it from GitHub: **Actions -> "MR-POC backtest (top 10 stocks, 3 years, Dhan 1-min)" -> Run workflow** (use `check` first). Results go to `mr_poc_results/`.
Offline logic test (no Dhan login): `python test_mr_poc.py`.

## COMBO day-SL backtest (BPB + SHAPECMP, all F&O stocks)

`combo_dayrisk_backtest.py` - runs the BPB strategy and the SHAPECMP swing-alert strategy (5 variants: no shape rule, previous candle green, previous candle red, upper wick longer, lower wick longer; each with entry types ALL / OPEN_0915 / FROM_0920_4C / RECROSS_0920_4C) on every F&O stock.
Entry 09:15-09:25, exit 09:30, trade stop-loss 10 / 20 / 30 %, at most Rs 60,000 per trade, and a **day stop-loss** test (no day SL, 5000, 6000, 12000, 18000, 24000, 30000): when the day P&L (realised + open) reaches the limit, all open trades are closed and no new entry is taken that day.
Run it from GitHub: **Actions -> "COMBO day-SL backtest" -> Run workflow**, type the start and end date (use `check` first). Results go to `combo_results/` (`summary.csv`, `roi_matrix.csv`, `daily_pnl.csv.gz`, `day_sl_vs_no_day_sl.csv`).
Offline logic test (no login): `python test_combo.py`. `mode = summary` rebuilds the tables from saved data for a new date range or a new day-SL list without calling Dhan.

## Two separate backtests: SHAPE-RULE (daily) and TRENDLINE (1H / 4H)

Both: all F&O stocks, entry 09:15-09:25 (4 entry types ALL / OPEN_0915 / FROM_0920_4C / RECROSS_0920_4C), exit 09:30, trade stop-loss 10 %, at most Rs 60,000 per trade, ATM option (LONG = call, SHORT = put). Engine = `combo_dayrisk_backtest.py`.
Result files in each folder: `all_trades.csv`, `summary.csv`, `top_by_pnl.csv`, `top_by_roi.csv`, `top_by_profit_factor.csv`, `top_by_win_rate.csv` (top lists need >= 30 trades per variant).

**`shaperule_backtest.py` -> `shaperule_results/`** - the SHAPECMP daily signal (10-day-high/low breakout, close back, re-cross next day) with the previous (signal) candle in four patterns, each its own strategy: GREEN_UPPER_WICK_LONGER, RED_UPPER_WICK_LONGER, GREEN_LOWER_WICK_LONGER, RED_LOWER_WICK_LONGER.
Actions -> "SHAPE-RULE backtest" -> Run workflow (use `check` first). Offline test: `python test_shaperule.py`.

**`trendline_backtest.py` -> `trendline_1h4h_results/`** - trendline through the last two swing highs (falling = resistance) / swing lows (rising = support), drawn on the 1-hour chart and on the 4-hour chart (Dhan 60-minute candles; 4H = 09:15-13:15 and 13:15-15:30). A close beyond the line stores the breakout candle's high (`H_break`) / low (`L_break`); a later candle touches the line and closes back on the breakout side; next morning the entry fires when price breaks `H_break` (LONG) / `L_break` (SHORT). No candle-shape filter.
Actions -> "TRENDLINE backtest" -> Run workflow (use `check` first). Offline test: `python test_trendline.py`. Swing / window settings: `PARAMS` at the top of the script.

## ALL-8 combined backtest (4 wick patterns + 2 trendlines + breakout + recross 4C)
`all8_backtest.py`, workflow **ALL-8 combined backtest**, results in `all8_results/`.  One run tests eight entry strategies on every F&O stock option from Jan 2023 to Aug 2026:
`WICK_GREEN_UPPER`, `WICK_RED_UPPER`, `WICK_GREEN_LOWER`, `WICK_RED_LOWER` (SHAPECMP daily signal, split by the previous candle), `TRENDLINE_1H`, `TRENDLINE_4H`, `BREAKOUT_BPB`, `SHAPECMP_RECROSS_4C`.

* **Entry** is checked through the whole day (09:15 to `entry_last`, default 15:20): the first 1-minute touch of the level (RECROSS_4C uses its own rule).
* **Exit variants** (all combined): stop-loss 10 / 20 / 30 / none x target 20 / 40 / 60 / 80 / 109 / 120 / 200 / 300 / 400 % x exit 09:30 / 10:00 / 12:00 / 15:30 / **UNTIL_HIT**.
  UNTIL_HIT has no time exit: the trade is held day after day until the stop or target is touched, or closed on the expiry day (`EXPIRY`).  Max Rs 60,000 per trade.
* **Files**: `summary.csv` (every strategy x exit variant, with **average / median / p90 / max days held**), `top_by_pnl.csv`, `top_by_roi.csv`, `top_by_win_rate.csv`, `top_by_profit_factor.csv`,
  `best_per_strategy.csv`, `until_hit_days_held.csv`, `trades_summary.csv` (signals, entries, option-data coverage, skip reasons per strategy), `all_trades_top_variants.csv.gz` (every trade of the top
  variants with strategy, entry type, `days_held`, `trading_days_held`), `summary_by_year_top.csv`, `REPORT.txt`.
* **Resumable**: it needs ~40,000+ Dhan calls; run the workflow again until `PROGRESS.txt` says COMPLETE.  `mode = check` first (also prints an expiry-calendar check), `mode = summary` rebuilds the files with no API calls
  (e.g. `sum_entry_to = 09:25` to summarise only entries up to 09:25).
* Option contract is locked at entry (strike + nearest monthly expiry; expiry = last Thursday up to Aug 2025, last Tuesday from Sep 2025) and followed to the end; charges, taxes and slippage are not included.

## RECROSS-10 backtest (BPB + 4 shape patterns, long and short, confirmed 1-minute re-cross)
`recross10_backtest.py`, workflow **RECROSS-10 backtest**, results in `recross10_results/` (start with `SUMMARY.md`).  Ten strategies, each entered ONLY on a confirmed re-cross of its level on the 1-minute chart:
`BPB_LONG`, `BPB_SHORT`, `WICK_GREEN_UPPER_LONG/SHORT`, `WICK_RED_UPPER_LONG/SHORT`, `WICK_GREEN_LOWER_LONG/SHORT`, `WICK_RED_LOWER_LONG/SHORT`.  The daily signals and levels are those of `all8_backtest.py` (its candidate file is reused when it covers the same dates); the engine (Dhan client, option series, exit simulation, tables) is `all8_backtest.py` itself.

* **Re-cross rule** (closes only, a wick never counts): a band of +/-0.05 % around the level (`band_pct`) turns small pokes into noise; a BASE of 4 consecutive closes on the far side comes first (no base = a gap-open or a hover on the line = no break); the first close beyond the band from 09:20 is the BREAK; a later close back across the level is the BACK; then `hold` = 2 consecutive closes beyond the band confirm the RE-CROSS, and the entry is the close of the last one (a single close beyond the line that is followed by a close back is a fake re-cross and is ignored).  Entry window to 15:20.  Nothing in the rule looks at a later candle.
* **Exit grid** (all combinations): stop-loss none / 20 / 40 / 60 % x target none / 20 / 40 / 60 / 80 % x time exit 09:30 / 10:00 / 12:00 / 15:30 = 80 variants per strategy; every trade closes on the entry day.  Max Rs 60,000 per trade; no charges / slippage.
* **Files**: `SUMMARY.md`, `summary.csv`, `trade_files/<STRATEGY>_best_trades.csv` (10 plain CSV files, every trade of the strategy's best variant), `all_trades/<STRATEGY>.csv.gz` (every trade of all 80 variants), `top_by_*.csv`, `best_per_strategy.csv`, `trades_summary.csv`, `summary_by_year_top.csv`.
* **Resumable**: run the workflow again until `PROGRESS.txt` says COMPLETE.  `mode = check` first, `mode = summary` rebuilds the files with no API calls.  Changing `band_pct` / `base` / `hold` / the dates needs another `out_dir` (the saved data belongs to one setting; the script refuses to mix them).
* Offline test (no login): `python test_recross10.py` - the rule on hand-made paths and against an independent state machine on 4,000 random paths, the 80-variant grid against a brute-force walk, and the whole pipeline on a simulated exchange.

## SLTP backtest (stop-loss x target grid for BPB / WRU SHORT, 5-close re-cross entry)

`sltp_backtest.py` (+ `sltp_rules.py` entry rules, `test_sltp.py` offline test, workflow **SLTP backtest**) compares stop-loss / target settings on the SHORT put trades of two studies. Run each study separately: Actions -> "SLTP backtest" -> study `pm` or `am` (use `check` first).

* **pm (afternoon)** - BPB SHORT, entries 12:00-15:20, time exits 15:00 and 15:30. Type 1: the day's first touch of the level is at/after 12:00, enter on it. Type 2: the first touch was before 12:00, enter from 12:00 on the first candle that touches the level after at least 5 consecutive 1-minute closes above it. Also reported combined (T1 or T2, one trade per signal day). Results in `sltp_pm_results/`.
* **am (morning)** - BPB SHORT and WRU SHORT (WICK_RED_UPPER_SHORT), entries 09:20-09:59 on the same 5-close re-cross rule, time exit 10:00. Results in `sltp_am_results/`.
* **Grid** (% of option premium): stop-loss none / 20 / 40 / 60 x target 60 / 80 / 100 / 120 / none x the study's time exits. Max Rs 60,000 per trade (whole lots), no charges / slippage.
* **Files**: `SUMMARY.md` (start here, SL x TP tables), `summary.csv`, `matrix_*.csv`, `trade_files/<STRATEGY>_all_variants_trades.csv` (every trade of every variant), `_best_trades.csv`, `_entries.csv`.
* Offline logic test (no login): `SLTP_STUDY=pm python test_sltp.py` and `SLTP_STUDY=am python test_sltp.py`.

## ENGULF backtest (green engulfing breakout, LONG, ATM call, SL x TP x time-exit grid)

`engulf_backtest.py` (+ `engulf_rules.py` rules, `test_engulf.py` offline test, workflow **ENGULF backtest**) on every F&O stock, entry dates 2023-10-27 to 2026-10-23. Actions -> "ENGULF backtest" -> `check` first, then `run` (resumable: run again until `PROGRESS.txt` says COMPLETE). Results in `engulf_results/` (start with `SUMMARY.md`).

* **Setup (daily)**: a GREEN candle that engulfs the previous non-green candle and whose High is the 10-day rolling high. Pullback = next 5 days: no daily close below the engulfing candle's low, at least one close inside its body. Level = highest High from the engulfing candle to the end of the pullback. A close below the engulfing low while waiting cancels the setup.
* **Entry**: the first 1-minute High >= level on the first later day that reaches it (09:15 to 15:20). Buy the ATM call (nearest monthly expiry); if the ATM series has no candle at the entry minute, ITM-1, ITM-2, ITM-3 (`itm_max`).
* **Grid**: stop-loss none / 20 / 40 / 60 % x target 20 / 40 / 60 / 80 / 100 / 120 / 200 % x time exit 09:30 / 10:00 / 15:30 (same day) = 84 variants. Max Rs 60,000 per trade, no charges / slippage.
* **Files**: `SUMMARY.md`, `summary.csv`, `matrix_*.csv`, `trade_files/GREEN_ENGULF_LONG_all_variants_trades.csv` (every trade of every variant), `_best_trades.csv`, `_entries.csv`.
* Offline test (no login): `python test_engulf.py`.

## ACC5 backtest (5-day accumulation fake-break, LONG call + SHORT put, SL x TP x time-exit grid)

`acc5_backtest.py` (+ `acc5_rules.py` rules, `test_acc5.py` offline test, workflow **ACC5 backtest**) on every F&O stock, entry dates 2023-10-30 to 2026-10-30. Actions -> "ACC5 backtest" -> `check` first, then `run` (resumable: run again until `PROGRESS.txt` says COMPLETE). Results in `acc5_results/` (start with `SUMMARY.md`; LONG and SHORT are separate folders `long/` and `short/`).

* **Setup (daily)**: Acc_High / Acc_Low = highest High / lowest Low of the prior 5 completed days. LONG: a daily close below Acc_Low (breakdown), then within 3 days price crosses back above that day's Acc_High. SHORT: mirror image (close above Acc_High, then within 3 days a cross back below Acc_Low).
* **Entry**: the first 1-minute candle (09:15 to 15:20) whose High >= level (LONG) / Low <= level (SHORT); the option price is the close of that minute. The original script used the daily close and assumed a fill at the level; this removes that look-ahead.
* **Option**: ATM call (LONG) / put (SHORT), nearest monthly expiry; if the ATM series has no candle at the entry minute, ITM-1, ITM-2, ITM-3.
* **Grid**: stop-loss none / 20 / 40 % x target 20 / 40 / 60 / 80 / 120 % / none x time exit 09:30 / 10:00 / 12:00 / 15:30 (same day) = 72 variants per direction. Max Rs 60,000 per trade, no charges / slippage.
* **Files** (in `long/` and `short/`): `SUMMARY.md`, `summary.csv`, `matrix_*.csv`, `trades_all_variants.csv.gz` (every trade of every variant), `trades_best_variant.csv`, `entries.csv`.
* Offline test (no login): `python test_acc5.py` - includes a check that the state machine equals the original script's loop on 3,000 random paths.
