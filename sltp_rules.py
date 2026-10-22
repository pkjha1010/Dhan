"""sltp_rules.py - the SHORT entry rules of sltp_backtest.py, pure numpy/pandas (no Dhan, no engine), so test_sltp.py can check them on hand-made paths.

All rules work on ONE entry day of 1-minute STOCK candles `u` (index = candle start time, columns o h l c) and the entry LEVEL of the daily setup.  SHORT = the stock
falls to / through the level; the strategy then buys the ATM put.  A "touch" is a candle whose LOW is at or below the level (a gap down through the level is a touch at 09:15).
A "close above" is a 1-minute CLOSE above the level - a wick never counts.

  day_first_touch(u, level)                  the first candle of the day (from 09:15) that touches the level.
  valid_recross(u, level, k, n_above, band)  True when the n_above candles right before candle k are consecutive minutes (no hole) and every one CLOSED above the level.
  recross_entry(u, level, from_min, last_min, n_above, band)
                                             the first candle k in [from_min, last_min] that touches the level AND is a valid re-cross (see above).
  afternoon_first_touch(u, level, split, last_min)   TYPE 1 of the afternoon study: the day's FIRST touch is at / after `split` (12:00) -> that candle, else None.
  afternoon_recross(u, level, split, last_min, n_above, band)   TYPE 2: the day's first touch was BEFORE `split` -> the first valid re-cross from `split` on, else None.
  (Type 1 and type 2 never fire on the same day: one needs the first touch at / after 12:00, the other before 12:00.)
Every function returns the POSITION of the entry candle in `u` (so u.index[pos] is the entry minute) or None.
"""
import numpy as np


def _arr(u):
    m = u.index.hour.values * 60 + u.index.minute.values
    return m, u.l.values.astype(float), u.c.values.astype(float)


def hm_to_min(s):
    return int(s[:2]) * 60 + int(s[3:5])


def day_first_touch(u, level, from_min=9 * 60 + 15):
    if u is None or len(u) == 0 or not level > 0: return None
    m, lo, _ = _arr(u)
    for k in range(len(m)):
        if m[k] >= from_min and lo[k] <= level: return k
    return None


def valid_recross(u, level, k, n_above=5, band=0.0):
    """The n_above candles before candle k: consecutive minutes, each CLOSED above level * (1 + band)."""
    m, _, c = _arr(u)
    if k < n_above or k >= len(m): return False
    if m[k] - m[k - n_above] != n_above: return False                          # a missing minute inside the run breaks it
    return bool((c[k - n_above:k] > level * (1 + band)).all())


def recross_entry(u, level, from_min, last_min, n_above=5, band=0.0):
    if u is None or len(u) <= n_above or not level > 0: return None
    m, lo, c = _arr(u)
    thr = level * (1 + band)
    for k in range(n_above, len(m)):
        if m[k] < from_min: continue
        if m[k] > last_min: return None
        if lo[k] <= level and m[k] - m[k - n_above] == n_above and (c[k - n_above:k] > thr).all(): return k
    return None


def afternoon_first_touch(u, level, split=12 * 60, last_min=15 * 60 + 20):
    k = day_first_touch(u, level)
    if k is None: return None
    m = u.index.hour.values * 60 + u.index.minute.values
    return k if split <= m[k] <= last_min else None


def afternoon_recross(u, level, split=12 * 60, last_min=15 * 60 + 20, n_above=5, band=0.0):
    k0 = day_first_touch(u, level)
    if k0 is None: return None
    m = u.index.hour.values * 60 + u.index.minute.values
    if m[k0] >= split: return None                                               # the first touch is in the afternoon: that is type 1, not a re-cross day
    return recross_entry(u, level, split, last_min, n_above, band)
