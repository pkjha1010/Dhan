"""engulf_rules.py - the GREEN-ENGULFING breakout rules, pure numpy (no Dhan, no Yahoo, no engine), so test_engulf.py can check them on hand-made and random paths.

DAILY SETUP (LONG only)
  1. ENGULFING candle (day i): a GREEN candle (close > open) whose High is the highest High of the last `roll` days (10, the candle itself included),
     and that engulfs the previous candle: the previous candle is NOT green (red or flat), close >= previous open, open <= previous close.
  2. MINI PULLBACK: in the next `pull` days (i+1 .. i+pull, default 5)
       - no daily CLOSE below the engulfing candle's LOW  (otherwise the setup is dead), and
       - at least one daily CLOSE inside the engulfing candle's BODY (min(open, close) <= close <= max(open, close)).
  3. LEVEL = the highest High from the engulfing candle up to the end of the pullback window (days i .. i+pull).
  4. ENTRY DAY = the first day after the pullback window whose High reaches the level.  While waiting, a daily close below the engulfing candle's low kills the setup.
     `wait` limits the waiting time in trading days after the window (0 = no limit).  The High is checked BEFORE the close of the same day: the cross happens during the
     day, the close comes later.
  After a setup has produced an entry day, the scan continues AFTER that entry day (no overlapping setups of one stock); a rejected candle moves the scan on by one day.
The intraday entry (1-minute candles of the entry day): the first candle from 09:15 to the last allowed minute whose HIGH is at or above the level (a gap up through the
level is a touch at 09:15).
"""
import numpy as np


def hm_to_min(s):
    return int(s[:2]) * 60 + int(s[3:5])


def is_engulfing(O, C, i):
    """GREEN candle i that engulfs a previous candle which is not green."""
    if i < 1: return False
    return bool(C[i] > O[i] and not (C[i - 1] > O[i - 1]) and C[i] >= O[i - 1] and O[i] <= C[i - 1])


def engulf_setups(O, H, L, C, pull=5, wait=0, roll=10):
    """-> list of dicts: engulf (index i), pb_end, entry (daily entry-day index), level, signal_low, body_lo, body_hi."""
    O, H, L, C = (np.asarray(x, float) for x in (O, H, L, C))
    n = len(C); out = []
    if n < roll + pull + 2: return out
    rh = np.full(n, np.nan)
    for i in range(roll - 1, n): rh[i] = H[i - roll + 1:i + 1].max()
    i = roll
    while i < n - 1:
        if not (H[i] >= rh[i] and is_engulfing(O, C, i)):
            i += 1; continue
        pe = i + pull
        if pe > n - 1: i += 1; continue
        low = L[i]; lo_b, hi_b = min(O[i], C[i]), max(O[i], C[i])
        dead, overlap = False, False
        for j in range(i + 1, pe + 1):
            if C[j] < low: dead = True; break
            if lo_b <= C[j] <= hi_b: overlap = True
        if dead or not overlap:
            i += 1; continue
        level = float(H[i:pe + 1].max())
        entry = None
        for k in range(pe + 1, n):
            if wait and k - pe > wait: break
            if H[k] >= level: entry = k; break
            if C[k] < low: break
        if entry is None:
            i += 1; continue
        out.append(dict(engulf=i, pb_end=pe, entry=entry, level=level, signal_low=float(low), body_lo=float(lo_b), body_hi=float(hi_b)))
        i = entry + 1
    return out


def first_cross_long(u, level, from_min=9 * 60 + 15, last_min=15 * 60 + 20):
    """u = one day of 1-minute candles (index = candle start, columns o h l c).  -> position of the first candle whose HIGH >= level in [from_min, last_min], else None."""
    if u is None or len(u) == 0 or not level > 0: return None
    m = u.index.hour.values * 60 + u.index.minute.values
    h = u.h.values.astype(float)
    for k in range(len(m)):
        if m[k] < from_min: continue
        if m[k] > last_min: return None
        if h[k] >= level: return k
    return None
