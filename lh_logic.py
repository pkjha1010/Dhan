"""lh_logic.py - previous-day afternoon direction from 1-minute stock candles (pure numpy/pandas, tested offline).

  last half hour  (H) : price at 15:30 (close of the day's last candle)  vs  price at 15:00 (open of the 15:00 candle)
  13:00 - 15:00   (M) : price at 15:00 (open of the 15:00 candle)        vs  price at 13:00 (open of the 13:00 candle)
  h / m = +1 bullish (end price above start price), -1 bearish (below), 0 flat.   ok = 0 when the day's data is incomplete.
"""
import numpy as np


def _first_at(mm, hh, mi, tol=5):
    t = hh * 60 + mi; sel = mm >= t
    if not sel.any(): return None
    i = int(np.argmax(sel))
    return i if mm[i] - t <= tol else None


def day_flags(u):
    """u = one day of 1-minute candles (columns o, c; DatetimeIndex) -> dict(ok, p1300, p1500, p1530, h, m)."""
    out = dict(ok=0, p1300=np.nan, p1500=np.nan, p1530=np.nan, h=0, m=0)
    if u is None or len(u) == 0: return out
    u = u.sort_index(); mm = u.index.hour.values * 60 + u.index.minute.values
    i13, i15 = _first_at(mm, 13, 0), _first_at(mm, 15, 0)
    if i13 is None or i15 is None or mm[-1] < 15 * 60 + 25: return out          # the day must cover 13:00, 15:00 and run to ~15:30
    p13, p15, p30 = float(u.o.iloc[i13]), float(u.o.iloc[i15]), float(u.c.iloc[-1])
    out.update(ok=1, p1300=round(p13, 2), p1500=round(p15, 2), p1530=round(p30, 2), h=int(np.sign(p30 - p15)), m=int(np.sign(p15 - p13)))
    return out
