"""bpb_bb_rules.py - the rules of YOUR "PURE BREAKOUT STRATEGY (LONG & SHORT)" script (5-day breakout, no pullback, zero look-ahead, previous-day Bollinger filter), pure numpy / pandas
(no Dhan, no Yahoo, no engine), so test_bpb_bb.py can prove them against your loop.

B = the BREAKOUT DAY (the daily candle that closes above the 5-day high).  B+1 = the next trading day, B+2 = the day after that ...   "B+n" is written on every entry.

LONG
  breakout   close[B] > High_5[B]  (High_5 = highest High of the 5 days BEFORE B)  -> ARMED, line = High_5[B], ENTRY LEVEL = High[B]
  cancel     a later close below the line (that close may itself be a new breakout -> a new setup, new B)
  entry day  the first day B+m (m >= FIRST_DAY) whose High reaches the level.  The setup is USED UP on that touch whether or not the Bollinger filter lets the trade through.
  filter     bb_ok = close of the day BEFORE the entry day > the upper Bollinger band (20, 2 std) of that same day      (all known before the open)
SHORT = exact mirror (close below the 5-day low, level = Low[B], entry when Low <= level, filter: previous close < lower band).

FIRST_DAY = the earliest B+m on which a touch counts.  Touches on earlier days are ignored and do NOT use the setup up.
  FIRST_DAY 3 = YOUR SCRIPT EXACTLY (its day counter "l_days_armed > 1" also skips B+2: the iteration that arms the setup can not enter (B+1) and the counter skips one more (B+2)).
  FIRST_DAY 2 = skip only B+1 (what the counter was meant to do; same as your script before the counter was added).
  FIRST_DAY 1 = no skip - the order can already be placed for B+1 (live trading can do that).
All three are built here, so every result can be read as "enter from B+1 / B+2 / B+3" and by the exact B+n of each entry.
"""
import numpy as np
import pandas as pd

BB_PERIOD = 20
BB_STD = 2.0
FIRST_DAYS = (1, 2, 3)


def _bands(C, period=BB_PERIOD, k=BB_STD):
    s = pd.Series(np.asarray(C, float))
    mid = s.rolling(window=period).mean(); sd = s.rolling(window=period).std()
    return (mid + k * sd).values, (mid - k * sd).values


def _long_machine(H, C, lookback, start, first_day):
    """LONG state machine on arrays already oriented for LONG.  Iteration d = 'today' = day d; yesterday y = d-1 is the finished candle.
    -> list of dict(entry, level, line, breakout, b_plus, bb_ok)."""
    n = len(C)
    hlb = pd.Series(np.asarray(H, float)).shift(1).rolling(window=lookback).max().values          # High_Lookback = highest High of the previous `lookback` days
    up, _ = _bands(C)
    out = []
    armed, line, level, B = False, 0.0, 0.0, -1
    for d in range(max(start, 1), n):
        y = d - 1
        if not armed:
            if C[y] > hlb[y]: armed, line, level, B = True, hlb[y], H[y], y
        elif C[y] < line:                                                          # invalidation: a close below the line
            armed = False
            if C[y] > hlb[y]: armed, line, level, B = True, hlb[y], H[y], y        # ... that is itself a new breakout
        if armed:
            m = d - B
            if m >= first_day and H[d] >= level:                                   # touch of the level today
                out.append(dict(entry=d, level=float(level), line=float(line), breakout=int(B), b_plus=int(m), bb_ok=bool(np.isfinite(up[y]) and C[y] > up[y])))
                armed = False                                                      # used up, filter passed or not
    return out


def setups(H, L, C, long=True, lookback=5, first_day=3, start=None):
    """-> list of dicts: entry (index of the entry day), level, line, breakout (index of the breakout day B), b_plus (entry day = B + b_plus trading days), bb_ok, all in REAL prices.
    start = first index looked at (None = your script's max(lookback, 20) + 5)."""
    H, L, C = (np.asarray(x, float) for x in (H, L, C))
    st = max(lookback, BB_PERIOD) + 5 if start is None else start
    if long: res = _long_machine(H, C, lookback, st, first_day)
    else: res = _long_machine(-L, -C, lookback, st, first_day)                    # mirror: High' = -Low, Close' = -Close  (the band test becomes close < lower band)
    sg = 1.0 if long else -1.0
    return [dict(r, level=sg * r["level"], line=sg * r["line"]) for r in res]


def candidates(H, L, C, long=True, lookback=5, bb_only=True):
    """UNION of the three machines (FIRST_DAY 1, 2, 3) for one stock and one direction - one row per entry DAY, so every entry is fetched from Dhan only once.
    -> list of dicts: entry, level, line, breakout, b_plus, bb_ok, from_b1, from_b2, from_b3 (1 = that machine takes this entry).
    bb_only = keep only entries that pass the Bollinger filter (your strategy); False keeps the others too (tagged bb_ok 0) for a with / without comparison.
    Where machines give a different level for the same day the one of the highest FIRST_DAY wins (your script first) and the others do not get the flag."""
    ms = {k: {s["entry"]: s for s in setups(H, L, C, long, lookback, k)} for k in FIRST_DAYS}
    rows = []
    for d in sorted(set().union(*[set(m) for m in ms.values()])):
        base = next(ms[k][d] for k in (3, 2, 1) if d in ms[k])
        r = dict(base)
        for k in FIRST_DAYS: r[f"from_b{k}"] = int(d in ms[k] and abs(ms[k][d]["level"] - base["level"]) < 1e-9)
        if bb_only and not r["bb_ok"]: continue
        r["bb_ok"] = int(r["bb_ok"]); rows.append(r)
    return rows
