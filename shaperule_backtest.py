"""shaperule_backtest.py - SHAPE-RULE strategies on the DAILY chart, all F&O stock options (Yahoo daily + Dhan 1-minute).  Separate from the trendline strategy.

  python shaperule_backtest.py check     test Dhan access
  python shaperule_backtest.py run       full backtest for SR_START .. SR_END (resumable - run again after a polite stop)
  python shaperule_backtest.py summary   rebuild the result CSVs from the saved option data (no API calls)

FOUR strategies, one per pattern of the "previous candle" (the daily SIGNAL candle, the candle before the entry day):
  GREEN_UPPER_WICK_LONGER   close > open and upper wick > lower wick
  RED_UPPER_WICK_LONGER     close < open and upper wick > lower wick
  GREEN_LOWER_WICK_LONGER   close > open and lower wick > upper wick
  RED_LOWER_WICK_LONGER     close < open and lower wick > upper wick
Upper wick = high - max(open, close); lower wick = min(open, close) - low.  Each pattern is its own strategy with its own trades and its own results.

DAILY SIGNAL (the SHAPECMP swing-alert rule of combo_dayrisk_backtest.py): a daily candle closes beyond the 10-day high (LONG) / low (SHORT) - the breakout, within the
last 20 days; a later candle (the SIGNAL candle) closes back on the other side of that line; on the NEXT day the entry fires when price crosses the line again.
ENTRY      09:15-09:25 only, four entry types: ALL (first 1-minute touch) | OPEN_0915 | FROM_0920_4C | RECROSS_0920_4C.  LONG buys the ATM call, SHORT the ATM put
           (nearest monthly expiry), option price = close of the entry-minute candle.
EXIT       trade stop-loss 10 % of the premium (SR_SLS) or the time exit at 09:30.   CAPITAL: at most Rs 60,000 per trade (lots = 60000 // (premium x lot)).
Charges, taxes and slippage are not included.  Lot sizes are today's values for all years.

Results in shaperule_results/ : all_trades.csv, summary.csv, top_by_pnl.csv, top_by_roi.csv, top_by_profit_factor.csv, top_by_win_rate.csv  (+ events.csv, parts/, REPORT.txt)
"""
import os, sys
for k in ("START", "END", "SYMBOLS", "CAP"):                                # SR_* names -> the COMBO_* names the engine reads
    if os.environ.get("SR_" + k): os.environ["COMBO_" + k] = os.environ["SR_" + k]
os.environ["COMBO_OUT"] = os.environ.get("SR_OUT") or "shaperule_results"
os.environ["DAY_SLS"] = "0"                                                # no day stop-loss in this test

import pandas as pd
import combo_dayrisk_backtest as C
import strategy_reports as R
from bpb_fno_backtest import Fatal

C.SLS = [int(x) for x in (os.environ.get("SR_SLS") or "10").replace(",", " ").split()]
C.DAY_SLS = [0]
_YAHOO = C.yahoo_candidates                                                # the engine's daily-candle step (SHAPE + BPB rows); only the SHAPE rows are used
PATTERNS = ["GREEN_UPPER_WICK_LONGER", "RED_UPPER_WICK_LONGER", "GREEN_LOWER_WICK_LONGER", "RED_LOWER_WICK_LONGER"]


def candidates():
    r = _YAHOO()
    r = r[r.source == "SHAPE"].reset_index(drop=True)
    print(f"Shape-rule candidate entry days: {len(r)}", flush=True)
    return r


def pattern_masks(e):
    return {"GREEN_UPPER_WICK_LONGER": e.green.eq(1) & e.upper_longer.eq(1), "RED_UPPER_WICK_LONGER": e.red.eq(1) & e.upper_longer.eq(1),
            "GREEN_LOWER_WICK_LONGER": e.green.eq(1) & e.lower_longer.eq(1), "RED_LOWER_WICK_LONGER": e.red.eq(1) & e.lower_longer.eq(1)}


def variants(ev):
    pm = pattern_masks(ev)
    return [(f"SHAPERULE | {p} | {ty}", ev.source.eq("SHAPE") & pm[p] & ev.type.eq(ty)) for p in PATTERNS for ty in C.TYPES]


def summary():
    paths = C.load_paths(); ep = f"{C.OUT}/events.csv"
    if paths.empty or not os.path.exists(ep): print("No saved option data yet - run the backtest first.", flush=True); return
    ev = pd.read_csv(ep); ev = ev[ev.source == "SHAPE"]
    d, t = C.main_simulation(ev, paths)
    R.write_reports(t, C.OUT)
    C.report(len(d))


C.yahoo_candidates = candidates
C.variants = variants
C.summary = summary

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": C.check()
        elif mode == "run": C.run()
        elif mode in ("summary", "range"): os.makedirs(C.OUT, exist_ok=True); C.progress(); summary()
        else: sys.exit("use: python shaperule_backtest.py check | run | summary")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
