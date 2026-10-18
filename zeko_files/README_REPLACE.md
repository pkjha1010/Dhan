# Replace these files in the `zeko` repo (same names as before)

| copy this file | to the repo |
|---|---|
| `shape_live_plan.py`          | repo root |
| `shape_live_manager.py`       | repo root |
| `shape_live_offline_test.py`  | repo root |
| `.github/workflows/shape_live_plan.yml`          | `.github/workflows/` |
| `.github/workflows/shape_live_manager.yml`       | `.github/workflows/` |
| `.github/workflows/shape_live_offline_test.yml`  | `.github/workflows/` |
| `CRON_JOB_ORG.md`  | repo root (the cron-job.org setup) |

No new secrets are needed (same KITE_*, ZERODHA_*, ANGEL_*, ORDER_PROXY).  Run `shape_live_offline_test.yml` first - it must print `ALL OFFLINE TESTS PASSED`.

## What the three strategies are (+60 % target for WRL and BPB, +400 % for WRU; backtest = no gap-fill trades)
| code | strategy | direction | stop-loss | entries | square off |
|---|---|---|---|---|---|
| WRL | WICK_RED_LOWER  (red signal candle, lower wick longer) | LONG (buy call)  | none | 09:15 - 09:59 | 10:00:00 |
| WRU | WICK_RED_UPPER  (red signal candle, upper wick longer), target +400 % | SHORT (buy put)  | -20 % | 09:15 - 09:29 | 09:30:00 |
| BPB | BREAKOUT_BPB (breakout -> pullback -> re-cross of the 10-day low) | SHORT (buy put) | none | 09:15 - 15:28 | 15:30:00 |
Change a percentage or time with an environment value on the plan step, e.g. `WRU_TP=60`, `WRU_SL=20`, `BPB_EXIT_AT=15:30:00`.  Per trade capital: 10 % of the funds available in your Kite account (`capital_pct`, as in your old plan; optional `total_funds` or a fixed `max_cost`).

## Safety rules in the manager
1. an unfilled BUY order is cancelled after 0.5 s;
2. an unfilled stop-loss SELL is cancelled after 0.5 s and the position is squared off at once (MARKET, then ever more aggressive LIMIT orders until flat);
   an unfilled target SELL is treated the same after 3 s (`TP_WAIT_S`, -1 = leave it);
3. more than 30 % of the total funds in use -> all waiting SHP| alerts deleted, waiting BUYs cancelled; when the used funds are back under 30 % the alerts are re-created
   (only strategies still inside their entry time, only setups that have not traded yet, only if the trade still fits the limit);
4. each strategy has its own entry end and square-off; a BUY that is filled after the entry end is sold at once;
5. only plan options / SHP* orders are touched; SWG alerts, swing positions and other orders are never touched (`SWEEP_ALL=0`);
6. `DRY_RUN=1` sends nothing.  The manager can be started again at any time: it rebuilds its state from Kite.

## What the backtest says (Jan 2023 - Aug 2026, partial data, gap-target trades removed)
WRL (10:00 exit) ROI about 6 %, BPB short (15:30) ROI about 9 %, WRU (09:30, SL20, target 400 %) ROI about 15 % on only 58 trades, most of it from a few trades - all three are small samples and were chosen
from over 1,600 variants, so treat them as a paper-trading candidate first.  The strategies were NOT tested with the 30 % fund rule.
