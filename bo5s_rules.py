"""bo5s_rules.py - rules of the SHORT mirror of bo5w: "10-day-low breakdown + Bollinger + previous day red + longer LOWER wick" (buy the ATM PUT at the breakdown day's close, exit the NEXT morning).
Pure numpy (no Dhan, no Yahoo, no engine), so test_bo5s.py can check every rule offline.  The exit simulation, exit grid and expiry calendar are the same code as the LONG study (bo5w_rules.py).

DAILY SETUP (day t = breakdown day B) = the exact mirror of your Colab script, with a 10-day window:
  1. Close[t] < lowest Low of the previous 10 days (day t itself not included)
  2. Close[t] < lower Bollinger band (20-day mean of Close - 2 x std, pandas std = ddof 1)
  3. day t-1 was red (Close < Open)
  4. lower wick of day t > upper wick of day t   (upper = High - max(Open, Close), lower = min(Open, Close) - Low)
  ENTRY  = buy the ATM PUT at the close of day t (short the stock via the put).   The next trading day (B+1) is the exit day.
  GAP RULE (one of the stop-loss options) = the stock OPENS on B+1 ABOVE the entry price (Open[B+1] > Close[B]) -> sell the put at its 09:15 open.
EXIT GRID: identical to bo5w (time exit 0915o / 0915c / 0916c / 0920c / 0930c, stop none / 20 / 40 / 60 % x gap rule off / on, target 40 / 60 / 80 / 100 / 120 / 200 % / none), all on the PUT's premium.
"""
import numpy as np
import bo5w_rules as W

REASON = dict(W.REASON); REASON[7] = "GAP RULE (stock opened above entry)"
simulate, variants, parse_exit, exit_label, expiry_calc, real_expiry = W.simulate, W.variants, W.parse_exit, W.exit_label, W.expiry_calc, W.real_expiry


def signals(O, H, L, C, lookback=10, bb_n=20, bb_k=2.0, need_next=True):
    """-> list of dicts {i, level_low, lower_bb, upper_wick, lower_wick} for every breakdown day i that meets all four rules.
    need_next: only days that have a following day (B+1) in the data."""
    O, H, L, C = (np.asarray(x, float) for x in (O, H, L, C))
    n = len(C); out = []
    for i in range(max(lookback, bb_n - 1), n - (1 if need_next else 0)):
        if i < 1: continue
        lo_n = L[i - lookback:i].min()
        win = C[i - bb_n + 1:i + 1]
        dn = win.mean() - bb_k * win.std(ddof=1)
        uw = H[i] - max(O[i], C[i]); lw = min(O[i], C[i]) - L[i]
        if C[i] < lo_n and C[i] < dn and C[i - 1] < O[i - 1] and lw > uw:
            out.append(dict(i=i, level_low=float(lo_n), lower_bb=float(dn), upper_wick=float(uw), lower_wick=float(lw)))
    return out
