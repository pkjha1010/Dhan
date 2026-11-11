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

## BPB BASE backtest (10-day breakout + pullback, entry at the highest price, LONG call + SHORT put, NIFTY50 filter)

`bpb_base_backtest.py` (+ `bpb_base_rules.py`, `test_bpb_base.py`, `bpb_base_report.py`, workflow **BPB BASE backtest**) - your BPB base strategy on the real ATM / ITM options with Dhan 1-minute candles, all F&O stocks, entry dates 2023-10-30 to 2026-10-30, LONG and SHORT separate. Same engine, option rule (ATM, ITM-1..3 fallback, next-month series on the expiry day, entry-day candles only) and Rs 60,000 cap as the GAP study.

* **Setup (Yahoo daily, your BPB state machine = `bpb_fno_backtest.find_setups`)**: LONG - a close above the 10-day rolling high (the line); later candles must not close below the line (a bearish candle confirms the pullback); entry level = the highest High since the breakout; entry day = first later day whose High reaches it. SHORT = mirror (10-day low, no close above the line, lowest Low). No open-price prefilter.
* **Entry, full day (09:15 to 15:20)**: the first 1-minute candle whose High (SHORT: Low) reaches the level; option price = close of that minute. LONG buys the ATM call, SHORT the ATM put.
* **NIFTY50 filter, checked in the entry minute**: LONG only when NIFTY50 > its day open, SHORT only when NIFTY50 < its day open (cached candles in `gap_nifty_results/`). It only removes trades, so the engine fetches each entry once and the report shows both numbers.
* **Grid**: stop-loss none / 20 / 40 / 60 % x target 60 / 80 / 100 / 120 % / none x time exit 15:00 / 15:30 = 40 variants per direction. A trade entered at / after a time exit is skipped for that exit.
* **Run**: Actions -> "BPB BASE backtest" -> `check`, then `run` (repeat until `PROGRESS.txt` says COMPLETE). Results in `bpb_base_results/` (`long/`, `short/`). After `run` / `summary` the report runs by itself (or use mode `report`): `bpb_base_nifty_results/` has `COMPARE.md` (before vs after the filter), `TRIM10.md` / `SURVIVORS.csv` (survivors after cutting the best 10 % of trades, no-filter and NIFTY sets, whole day and per entry-time slot), `{long,short}/trades_all_variants.csv.gz` (the kept trades).
* Offline test: `python test_bpb_base.py`.

## ORB backtest (opening range breakout 09:15-09:30, LONG call + SHORT put, combined exits)

`orb_backtest.py` (+ `orb_rules.py`, `test_orb.py`, workflow **ORB backtest**) - the "Core Strategy Mechanics" table (ORB, close above the ORB high on strong volume, stop below the ORB low or the breakout candle low) on **1-minute candles**, tested on real ATM / ITM options from Dhan.

* **ORB**: High / Low of the 1-minute candles from 09:15 up to 09:30. **Entry**: the first 1-minute candle from 09:30 (to 15:20) whose **close** is above the ORB high (LONG, buy ATM call) / below the ORB low (SHORT, buy ATM put); option price = close of that minute. One trade per stock per day (first side that signals). **Volume filter**: breakout candle volume >= 1.5 x the average of the previous 10 candles (`--vol-mult 0` = off); a close beyond the ORB that fails the filter is skipped and the scan continues.
* **Stop-loss, both from the image (stock price)**: `ORB` = stock trades below the ORB low (SHORT: above the ORB high); `BRK` = stock trades below the low of the breakout candle (SHORT: above its high). **Fixed stop-loss** 20 / 40 / 60 % of the option premium. **Target** 20 / 40 / 60 % (or none). **Time exit** 10:00 / 12:00 / 15:00 / 15:30.
* **Combined exit**: every stop-loss x target x time-exit combination is one variant and the first rule that hits closes the trade (stop wins when stop and target are inside the same minute). Plus the combined stop-loss mixes `ORB+20 ... BRK+60` (stock stop OR fixed %, whichever first; `--no-combine` drops them) = 12 stops x 4 targets x 4 time exits = 192 variants per direction.
* **Universe**: `--universe top10` (10 heaviest NIFTY50 stocks) / `nifty50` (50 index stocks) / `fno` (all F&O stocks) or your own `--symbols RELIANCE,SBIN,...`. The lists are at the top of `orb_backtest.py`; edit them if the index changes. **Date range**: `--start YYYY-MM-DD --end YYYY-MM-DD` (entry dates). Each universe has its own result folder `orb_results_<universe>/`.
* **Run**: Actions -> "ORB backtest" -> `check` first, then `run` (resumable: run again until it says ALL STEPS FINISHED). Mode `summary` rebuilds all files from the saved data without API calls - use it to narrow the date range afterwards. Locally: `python orb_backtest.py run --universe top10 --start 2025-11-01 --end 2026-11-10`.
* **Results** (`long/` and `short/` separate): `SUMMARY.md` (PnL / ROI / win % matrices per time exit, best variants), `summary.csv`, `matrix_*.csv`, `trades_all_variants.csv.gz`, `trades_best_variant.csv`, `entries.csv`. Max Rs 60,000 per trade (whole lots), no charges / slippage, today's lot sizes.
* Data limits: Dhan allows 100,000 data calls a day. A big universe x long range (fno x 3 years) takes several days - progress is saved, just run again. Start with `top10` and a short range.
* Offline test (no login): `python test_orb.py` - the combined exit is checked against a minute-by-minute brute force.
