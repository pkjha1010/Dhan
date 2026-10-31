# ACC5 backtest (Dhan 1-minute data)

The repo keeps only the ACC5 backtest, the engine modules it imports (`all8_backtest.py`, `trendline_backtest.py`, `combo_dayrisk_backtest.py`, `bpb_fno_backtest.py`, `strategy_reports.py`, `itm_fallback.py`) and the CSV.GZ decompress workflow.
Setup: repo secrets `DHAN_ACCESS_TOKEN`, `DHAN_CLIENT_ID` (Settings -> Secrets and variables -> Actions).

## What it does (5-day accumulation fake-break, LONG call + SHORT put, SL x TP x time-exit grid)

`acc5_backtest.py` (+ `acc5_rules.py` rules, `test_acc5.py` offline test, workflow **ACC5 backtest**) on every F&O stock, entry dates 2023-10-30 to 2026-10-30. Actions -> "ACC5 backtest" -> `check` first, then `run` (resumable: run again until `PROGRESS.txt` says COMPLETE). Results in `acc5_results/` (start with `SUMMARY.md`; LONG and SHORT are separate folders `long/` and `short/`).

* **Setup (daily)**: Acc_High / Acc_Low = highest High / lowest Low of the prior 5 completed days. LONG: a daily close below Acc_Low (breakdown), then within 3 days price crosses back above that day's Acc_High. SHORT: mirror image (close above Acc_High, then within 3 days a cross back below Acc_Low).
* **Entry**: the first 1-minute candle (09:15 to 15:20) whose High >= level (LONG) / Low <= level (SHORT); the option price is the close of that minute. The original script used the daily close and assumed a fill at the level; this removes that look-ahead.
* **Option**: ATM call (LONG) / put (SHORT), nearest monthly expiry; if the ATM series has no candle at the entry minute, ITM-1, ITM-2, ITM-3.
* **Grid**: stop-loss none / 20 / 40 % x target 20 / 40 / 60 / 80 / 120 % / none x time exit 09:30 / 10:00 / 12:00 / 15:30 (same day) = 72 variants per direction. Max Rs 60,000 per trade, no charges / slippage.
* **Files** (in `long/` and `short/`): `SUMMARY.md`, `summary.csv`, `matrix_*.csv`, `trades_all_variants.csv.gz` (every trade of every variant), `trades_best_variant.csv`, `entries.csv`.
* Offline test (no login): `python test_acc5.py` - includes a check that the state machine equals the original script's loop on 3,000 random paths.
