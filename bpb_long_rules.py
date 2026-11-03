"""bpb_long_rules.py - the BPB LONG (breakout -> confirmed pullback -> re-cross) entry rules, checked through the FULL DAY (09:15 .. last allowed minute, default 15:20).
Pure numpy (no Dhan, no Yahoo, no engine), so test_bpb_long.py can check them.

DAILY SETUP (same state machine as bpb_fno_backtest.find_setups, LONG side)
  1. BREAKOUT  : a daily candle closes above the 10-day rolling high (highest High of the previous 10 days) = the LINE.
  2. LEVEL     : the highest High made since the breakout day (the breakout day included).
  3. PULLBACK  : every candle after the breakout day must CLOSE at or above the LINE; confirmed by one bearish candle (close < open).
  4. ENTRY DAY : the first later day whose High reaches the LEVEL (the setup is used up that day).

ENTRY ON THE ENTRY DAY (1-minute candles, whole day 09:15 .. last allowed minute)
  TYPE 1 : the FIRST 1-minute candle of the day whose High >= LEVEL (a gap through the level = 09:15) is the entry.
  TYPE 2 : re-cross entry that avoids fake breakouts.  After the first touch wait for >= 5 consecutive 1-minute CLOSES below the level; the first later candle whose
           High >= LEVEL is the entry.  A touch candle that closes below the level counts as a close below.  Needs a first touch to exist; the same day can also have a TYPE 1 entry
           (they are separate strategies, reported separately, never mixed).
  Option price = close of the entry-minute option candle (done by the engine).
"""
import numpy as np

MIN_CLOSES = 5


def first_touch(h, level):
    """position of the first candle whose HIGH >= level, else None."""
    for k in range(len(h)):
        if h[k] >= level: return k
    return None


def entries_long(m, h, c, level, last_min, n_closes=MIN_CLOSES):
    """m = minutes since midnight of the day's 1-minute candles, h / c = High / Close arrays, level = entry level.
    -> dict {'T1': position, 'T2': position} (either may be missing); position = index into the candle arrays; entries after last_min are not accepted."""
    m = np.asarray(m, int); h = np.asarray(h, float); c = np.asarray(c, float)
    if len(m) == 0 or not level > 0: return {}
    k = first_touch(h, level)
    if k is None or m[k] > last_min: return {}
    out = {"T1": k}
    run = 1 if c[k] < level else 0                         # the touch candle itself may already close below the level
    for j in range(k + 1, len(m)):
        if m[j] > last_min: break
        if run >= n_closes and h[j] >= level:
            out["T2"] = j; break
        run = run + 1 if c[j] < level else 0
    return out
