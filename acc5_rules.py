"""acc5_rules.py - the 5-DAY ACCUMULATION fake-break rules (LONG and SHORT), pure numpy (no Dhan, no Yahoo, no engine), so test_acc5.py can check them.

Your original script (daily candles, 5 years, Nifty 50) did this for the LONG side:
  Acc_High / Acc_Low = highest High / lowest Low of the PRIOR `acc` completed days (default 5).
  BREAKDOWN = a daily CLOSE below Acc_Low.      A later close below Acc_Low moves the breakdown to that day.
  ENTRY     = within `window` (3) candles after the breakdown, a daily CLOSE above Acc_High; entry price = Acc_High; one trade per breakdown.

DAILY SETUP here
  LONG  (buy the CALL) : breakdown = close < Acc_Low;  within 3 days price crosses back ABOVE Acc_High      -> level = Acc_High of the entry day
  SHORT (buy the PUT)  : mirror image: breakout = close > Acc_High; within 3 days price crosses back BELOW Acc_Low -> level = Acc_Low of the entry day
  The level is known before the entry day opens (prior `acc` days only), so nothing looks ahead.
  CHANGE vs the original: the daily CLOSE above the level is replaced by the INTRADAY cross (a 1-minute High >= level for LONG, Low <= level for SHORT), so the entry minute and
  the entry price are real and tradable (the original needed the day's close to decide, then assumed a fill at the level).  `trigger="close"` gives the original rule exactly
  (used by the test to prove the state machine is the same as your script).
  On a day that both touches the level and closes beyond the opposite side, the touch wins (the cross happens during the day, the close comes later).
  After an entry the scan continues on the NEXT day; if the entry day itself closed beyond the opposite side it starts a new breakdown / breakout.
The intraday entry = the first 1-minute candle from 09:15 to the last allowed minute whose High >= level (LONG) / Low <= level (SHORT); a gap through the level = 09:15.
"""
import numpy as np


def acc_levels(H, L, acc=5):
    """Acc_High[i] = max(H[i-acc:i]), Acc_Low[i] = min(L[i-acc:i]) (prior days only); NaN for i < acc."""
    H = np.asarray(H, float); L = np.asarray(L, float); n = len(H)
    ah = np.full(n, np.nan); al = np.full(n, np.nan)
    for i in range(acc, n):
        ah[i] = H[i - acc:i].max(); al[i] = L[i - acc:i].min()
    return ah, al


def acc_setups(O, H, L, C, long=True, acc=5, window=3, trigger="touch", start=None):
    """-> list of dicts: signal (index of the breakdown / breakout day), entry (entry-day index), level, other (the opposite Acc level of the entry day).
    long=False is the mirror image (prices negated, High and Low swapped), so one state machine serves both sides.
    trigger='touch' : entry day = first day whose High (LONG) / Low (SHORT) reaches the level (intraday cross);  'close' : the original script's daily close beyond the level."""
    O, H, L, C = (np.asarray(x, float) for x in (O, H, L, C))
    if not long: O, H, L, C = -O, -L, -H, -C
    n = len(C); out = []
    ah, al = acc_levels(H, L, acc)
    bd = None
    for i in range(acc if start is None else start, n):
        if bd is not None and i - bd > window: bd = None
        cross = (H[i] >= ah[i]) if trigger == "touch" else (C[i] > ah[i])
        if bd is not None and cross:
            sg = 1.0 if long else -1.0
            out.append(dict(signal=bd, entry=i, level=sg * float(ah[i]), other=sg * float(al[i])))
            bd = i if (trigger == "touch" and C[i] < al[i]) else None
            continue
        if C[i] < al[i]: bd = i
    return out


def hm_to_min(s):
    return int(s[:2]) * 60 + int(s[3:5])


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


def first_cross_short(u, level, from_min=9 * 60 + 15, last_min=15 * 60 + 20):
    """-> position of the first candle whose LOW <= level in [from_min, last_min], else None."""
    if u is None or len(u) == 0 or not level > 0: return None
    m = u.index.hour.values * 60 + u.index.minute.values
    l = u.l.values.astype(float)
    for k in range(len(m)):
        if m[k] < from_min: continue
        if m[k] > last_min: return None
        if l[k] <= level: return k
    return None
