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

**`trendline_backtest.py` -> `trendline_results/`** - trendline through the last two swing highs (falling = resistance) / swing lows (rising = support), drawn on the 1-hour chart and on the 4-hour chart (Dhan 60-minute candles; 4H = 09:15-13:15 and 13:15-15:30). A close beyond the line stores the breakout candle's high (`H_break`) / low (`L_break`); a later candle touches the line and closes back on the breakout side; next morning the entry fires when price breaks `H_break` (LONG) / `L_break` (SHORT). No candle-shape filter.
Actions -> "TRENDLINE backtest" -> Run workflow (use `check` first). Offline test: `python test_trendline.py`. Swing / window settings: `PARAMS` at the top of the script.
