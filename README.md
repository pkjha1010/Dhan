# ACC5 backtest (Dhan 1-minute data)

The repo keeps only the ACC5 backtest, the engine modules it imports (`all8_backtest.py`, `trendline_backtest.py`, `combo_dayrisk_backtest.py`, `bpb_fno_backtest.py`, `strategy_reports.py`, `itm_fallback.py`) and the CSV.GZ decompress workflow.
Setup: repo secrets `DHAN_ACCESS_TOKEN`, `DHAN_CLIENT_ID` (Settings -> Secrets and variables -> Actions).

## What it does (5-day accumulation fake-break, LONG call + SHORT put, SL x TP x time-exit grid)

`accum5_backtest.py` (+ `accum5_rules.py` rules, `test_accum5.py` offline test, workflow **ACC5 backtest**) on every F&O stock, entry dates 2023-10-30 to 2026-10-30. Actions -> "ACC5 backtest" -> `check` first, then `run` (resumable: run again until `PROGRESS.txt` says COMPLETE). Results in `accum5_results/` (start with `SUMMARY.md`; LONG and SHORT are separate folders `long/` and `short/`).

* **Setup (daily)**: Acc_High / Acc_Low = highest High / lowest Low of the prior 5 completed days. LONG: a daily close below Acc_Low (breakdown), then within 3 days price crosses back above that day's Acc_High. SHORT: mirror image (close above Acc_High, then within 3 days a cross back below Acc_Low).
* **Entry**: the first 1-minute candle (09:15 to 15:20) whose High >= level (LONG) / Low <= level (SHORT); the option price is the close of that minute. The original script used the daily close and assumed a fill at the level; this removes that look-ahead.
* **Option**: ATM call (LONG) / put (SHORT), nearest monthly expiry; if the ATM series has no candle at the entry minute, ITM-1, ITM-2, ITM-3.
* **Grid**: stop-loss none / 20 / 40 % x target 20 / 40 / 60 / 80 / 120 % / none x time exit 09:30 / 10:00 / 12:00 / 15:30 (same day) = 72 variants per direction. Max Rs 60,000 per trade, no charges / slippage.
* **Files** (in `long/` and `short/`): `SUMMARY.md`, `summary.csv`, `matrix_*.csv`, `trades_all_variants.csv.gz` (every trade of every variant), `trades_best_variant.csv`, `entries.csv`.
* Offline test (no login): `python test_accum5.py` - includes a check that the state machine equals the original script's loop on 3,000 random paths.

## ACCUM10 backtest (same as ACCUM5 but a 10-day accumulation)

`accum10_backtest.py` (+ `accum10_rules.py`, `test_accum10.py`, workflow **ACC10 backtest**) - identical rules, option handling, exit grid and ₹60,000 cap as ACCUM5, but Acc_High / Acc_Low are the highest High / lowest Low of the prior **10** completed days. Its own result folder `accum10_results/` (with `long/` and `short/`) and its own strategy names `ACC10_LONG` / `ACC10_SHORT`, so nothing is mixed with the 5-day results. Actions -> "ACC10 backtest" -> `check`, then `run` (repeat until `PROGRESS.txt` says COMPLETE). Offline test: `python test_accum10.py`.

## GAP backtest (gap-fade reversal, LONG call + SHORT put, SL x TP x time-exit grid)

`gap_backtest.py` (+ `gap_rules.py`, `test_gap.py`, workflow **GAP backtest**) - your daily-candle gap script tested on the real ATM / ITM options with Dhan 1-minute candles, all F&O stocks, entry dates 2023-10-30 to 2026-10-30.

* **Setup (same as the original script)**: LONG - day i opens > 1 % above the previous close and day i+1 closes below day i's close; level = High of day i. SHORT - day i opens > 1 % below the previous close and day i+1 closes above day i's close; level = Low of day i. Entry day = the first day among i+2 .. i+4 whose High (LONG) / Low (SHORT) reaches the level. `test_gap.py` proves the setups equal the original loop on 2,000 random paths.
* **Entry**: the first 1-minute candle (09:15 to 15:20) of the entry day that reaches the level (a gap through the level = 09:15); the option price is the close of that minute. No open-price prefilter, so a stock that opens far from the level but crosses it later is not lost.
* **Option**: LONG = call, SHORT = put. ATM first; if the ATM series has no candle at the entry minute, ITM-1, ITM-2, ITM-3. Candles are fetched for the **entry day only** (1-day window). On the monthly-expiry day itself the next month's series is used (nearest month if that has no data). The strike offset used is stored per trade (`strike_offset`: 0 = ATM, +-n = ITM-n); entries that still have no option candle are listed with the reason in the summary.
* **Grid**: stop-loss none / 20 / 40 / 60 % x target 20 / 40 / 60 / 80 / 120 % / none x time exit 09:30 / 10:00 / 12:00 / 15:30 (same day) = 96 variants per direction. Max Rs 60,000 per trade, no charges / slippage.
* **Files** in `gap_results/` (`long/` and `short/` separate): `SUMMARY.md`, `summary.csv`, `matrix_*.csv`, `trades_all_variants.csv.gz`, `trades_best_variant.csv`, `entries.csv`. Actions -> "GAP backtest" -> `check`, then `run` (repeat until `PROGRESS.txt` says COMPLETE).

## GAP NIFTY filter (market-direction condition on the GAP trades)

`gap_nifty_filter.py` (+ `gap_nifty_rules.py`, `test_gap_nifty.py`, workflow **GAP NIFTY filter**) - retests the existing `gap_results` trades with a NIFTY50 day-direction filter: **LONG only when NIFTY50 price at the entry minute is above the NIFTY50 open of the same day; SHORT only when it is below it** (equal = no trade).

* NIFTY50 1-minute candles come from Dhan (security id 13, segment IDX_I), downloaded once and cached in `gap_nifty_results/nifty_1min.csv.gz`. Nifty open = Open of the 09:15 candle; Nifty price = Close of the candle that starts at the entry minute (last candle at or before it if that minute is missing).
* No option data is re-fetched: a kept trade is exactly the same trade as in `gap_results`; the filter only removes trades. Days without NIFTY candles are dropped and counted.
* Output in `gap_nifty_results/`: `COMPARE.md` / `compare.csv` (before vs after for every direction x exit x SL x TP), `{long,short}/trades_all_variants.csv.gz` (kept trades + `nifty_open`, `nifty_price`), `nifty_days.csv`, `survivors/`.
* Actions -> "GAP NIFTY filter" -> `check` first, then `run`. Offline test: `python test_gap_nifty.py`.

## BPB LONG backtest (breakout -> confirmed pullback -> re-cross, ATM call, full-day entry)

`bpb_long_backtest.py` (+ `bpb_long_rules.py`, `test_bpb_long.py`, `bpb_long_report.py`, workflow **BPB LONG backtest**) - the BPB LONG setup on the real ATM / ITM calls with Dhan 1-minute candles, all F&O stocks, entry dates 2023-10-30 to 2026-10-30. Same engine, option rule (ATM, ITM-1..3 fallback, next-month series on the expiry day, entry-day candles only) and Rs 60,000 cap as the GAP study.

* **Setup (Yahoo daily, same state machine as `bpb_fno_backtest.find_setups`)**: a close above the 10-day high (the line) -> entry level = highest High since the breakout -> candles must close at / above the line, one bearish candle confirms the pullback -> entry day = first later day whose High reaches the level. No open-price prefilter.
* **Entry, checked the FULL DAY (09:15 to 15:20)**, two separate strategies: **type1** = first 1-minute candle whose High >= level; **type2** = after the first touch, >= 5 consecutive 1-minute closes below the level, then the first candle whose High >= level (avoids fake breakouts). The option price is the close of the entry minute.
* **Grid**: stop-loss none / 20 / 40 / 60 % x target 60 / 80 / 100 / 120 % / none x time exit 15:00 / 15:30 = 40 variants per entry type. A trade entered at / after a time exit is skipped for that exit.
* **Run**: Actions -> "BPB LONG backtest" -> `check`, then `run` (repeat until `PROGRESS.txt` says COMPLETE). Results in `bpb_long_results/` (`type1/`, `type2/`).
* **NIFTY50 filter + top-10 % trim** (`bpb_long_report.py`, mode `report`, no API calls; runs automatically after `run` / `summary`): LONG only when NIFTY50 at the entry minute is above its day open (cached candles in `gap_nifty_results/`). Writes `bpb_long_nifty_results/` with `COMPARE.md` (before vs after), `TRIM10.md` / `SURVIVORS.csv` (survivors after cutting the best 10 % of trades, for no-filter and Nifty sets, whole day and per entry-time slot).
* Offline test: `python test_bpb_long.py`.
