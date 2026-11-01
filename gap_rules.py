"""gap_rules.py - the GAP-FADE-REVERSAL rules (LONG and SHORT), pure numpy (no Dhan, no Yahoo, no engine), so test_gap.py can check them.

Your original script (daily candles, Yahoo) did this:
  LONG  setup : day i opens > 1 % above the previous close (gap up) AND day i+1 closes BELOW day i's close.
                level = High of day i.  Entry = first day among i+2 .. i+4 whose High >= level, entry at the level.
  SHORT setup : day i opens > 1 % below the previous close (gap down) AND day i+1 closes ABOVE day i's close.
                level = Low of day i.   Entry = first day among i+2 .. i+4 whose Low <= level, entry at the level.
  Exit (original) : +2 % target on the stock, else the entry day's close.
  (LONG and SHORT cannot both fire on the same day i, so the original `elif` changes nothing.)

HERE (options version): the setup, the level and the entry days are exactly the same.  The only changes:
  * the entry is the first 1-MINUTE candle (09:15 .. last allowed minute) of the entry day whose High >= level (LONG) / Low <= level (SHORT); a gap through the level = 09:15;
  * LONG buys the ATM CALL, SHORT buys the ATM PUT (option price = close of the entry minute), exits on the option premium (SL x TP x time exit).
"""
import numpy as np


def gap_setups(O, H, L, C, long=True, gap=0.01, first=2, last=4, trigger="touch"):
    """-> list of dicts: signal (day i), entry (entry-day index), level.
    LONG : (O[i]-C[i-1])/C[i-1] > gap and C[i+1] < C[i];  level = H[i];  entry day = first j in i+first .. i+last with H[j] >= level.
    SHORT: (O[i]-C[i-1])/C[i-1] < -gap and C[i+1] > C[i]; level = L[i];  entry day = first j in i+first .. i+last with L[j] <= level.
    The original loop `range(i+2, min(i+5, n))` = first=2, last=4.  Days after the data end are not available (like the original).
    trigger='touch' : the intraday cross decides (Yahoo High / Low);  'close' is not used (the original also used High / Low)."""
    O, H, L, C = (np.asarray(x, float) for x in (O, H, L, C))
    n = len(C); out = []
    for i in range(1, n - 1):
        g = (O[i] - C[i - 1]) / C[i - 1]
        if long:
            if not (g > gap and C[i + 1] < C[i]): continue
            lvl = H[i]
            for j in range(i + first, min(i + last + 1, n)):
                if H[j] >= lvl: out.append(dict(signal=i, entry=j, level=float(lvl))); break
        else:
            if not (g < -gap and C[i + 1] > C[i]): continue
            lvl = L[i]
            for j in range(i + first, min(i + last + 1, n)):
                if L[j] <= lvl: out.append(dict(signal=i, entry=j, level=float(lvl))); break
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
