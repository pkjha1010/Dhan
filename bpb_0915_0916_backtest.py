"""bpb_0915_0916_backtest.py - BPB BASE LONG (ATM call) + SHORT (ATM put), entries ONLY at the 09:15 and 09:16 minute, exit 09:20 only.

Uses the same engine as bpb_base_backtest.py (same BPB rules, same ATM / ITM fallback, same Dhan 1-minute data, same fills), only the settings differ:
  ENTRY  the first 1-minute candle of the day that reaches the BPB entry level, but ONLY if it is the 09:15 or the 09:16 candle (entry price = close of that minute).
         Entries at 09:15 and 09:16 are reported separately and together (entry_time column + SUMMARY_0915_0916.md).
  EXIT   09:20 only (close of the last option candle up to 09:20), nothing else.
  SL     none / 40 / 60 %      TP  none / 40 / 60 / 80 %      (percent of the option premium)  = 3 x 4 = 12 variants per direction.
         Stop and target in the same minute = STOP.  A gap through the level fills at that candle's open.

Put this file in the Dhan repo next to bpb_base_backtest.py and run (needs your Dhan token like the other backtests):
  python bpb_0915_0916_backtest.py run       full backtest (resumable)
  python bpb_0915_0916_backtest.py summary   rebuild result files from saved data (no API calls)
Results: bpb_0915_0916_results/  (long/ and short/ with trades_all_variants.csv.gz, entries.csv, matrices; SUMMARY.md)
"""
import os, sys

# settings must be set BEFORE bpb_base_backtest is imported (it reads them at import time)
for k, v in {"BB_OUT": "bpb_0915_0916_results", "BB_ENTRY_LAST": "09:16", "BB_EXITS": "09:20",
             "BB_SLS": "0,40,60", "BB_TPS": "40,60,80,0", "BB_MIN_TRADES": "30"}.items():
    if not os.environ.get(k): os.environ[k] = v          # blank (e.g. an empty workflow box) = default

import numpy as np, pandas as pd
import bpb_base_backtest as B
import all8_backtest as A


def slot_report():
    """09:15 vs 09:16 vs both, per direction x SL x TP (exit 09:20), from the saved trades."""
    rows = []
    for d in ("long", "short"):
        p = f"{A.OUT}/{d}/trades_all_variants.csv.gz"
        if not os.path.exists(p): continue
        T = pd.read_csv(p, dtype={"entry_time": str})
        for name, mins in {"09:15": ["09:15"], "09:16": ["09:16"], "09:15+09:16": ["09:15", "09:16"]}.items():
            U = T[T.entry_time.isin(mins)]
            for (sl, tp), g in U.groupby(["sl", "tp"]):
                w, l = g.pnl[g.pnl > 0].sum(), -g.pnl[g.pnl < 0].sum()
                rows.append(dict(direction=d.upper(), entry=name, sl="none" if not sl else f"{int(sl)}%", tp="none" if not tp else f"{int(tp)}%",
                                 trades=len(g), win_pct=round((g.pnl > 0).mean() * 100, 1), total_pnl=round(g.pnl.sum()),
                                 profit_factor=round(w / l, 2) if l > 0 else np.inf, avg_pnl=round(g.pnl.mean())))
    if not rows: return
    R = pd.DataFrame(rows); R.to_csv(f"{A.OUT}/slot_summary_0915_0916.csv", index=False)
    L = ["# BPB BASE - entries 09:15 / 09:16, exit 09:20", ""]
    for d in ("LONG", "SHORT"):
        for e in ("09:15", "09:16", "09:15+09:16"):
            g = R[(R.direction == d) & (R.entry == e)].sort_values("total_pnl", ascending=False)
            L += [f"## {d} {e}", "", B.md(g.drop(columns=["direction", "entry"])), ""]
    open(f"{A.OUT}/SUMMARY_0915_0916.md", "w").write("\n".join(L))
    print("\n".join(L), flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": B.print_rules(); A.check()
        elif mode == "run": B.run(); slot_report()
        elif mode == "summary": B.print_rules(); B.summary(); slot_report()
        else: sys.exit("use: python bpb_0915_0916_backtest.py run | summary | check")
    except A.Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
