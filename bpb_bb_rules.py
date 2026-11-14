"""bpb_bb_rules.py - the rules of YOUR attached script "5-YEAR BPB STRATEGY BACKTEST (LONG & SHORT)" (10-day breakout, pullback, entry at the breakout day's High, Bollinger filter), pure numpy / pandas
(no Dhan, no Yahoo, no engine), so test_bpb_bb.py can prove them against the original loop.

YOUR SCRIPT (daily candles) - LONG:
  SEARCHING        a close above High_10 (highest High of the PREVIOUS 10 days)  -> PULLBACK_PHASE, line = that High_10, level = the High of the breakout day
  PULLBACK_PHASE   close < line  -> back to SEARCHING (and if that same close is above that day's High_10 a NEW setup starts at once)
                   else if High >= level -> ENTRY at the level (the trade is taken only if close > Bollinger upper band (20, 2 std) when FILTER_MODE = BOLLINGER); the setup is used up either way
  (the original's "if c_high > l_highest: l_highest = c_high" can never run - a higher High has already triggered the entry - so the level is always the breakout day's High.)
  SHORT = exact mirror (close below Low_10, level = Low of the breakdown day, entry when Low <= level, filter: close < lower band).  Original loop starts at index max(10, 20) + 5 = 25.
  Exit in the original: +2 % on the stock, else the day's close.  HERE: options on 1-minute candles (see bpb_bb_backtest.py).

LOOK-AHEAD IN THE ORIGINAL (what a live trader cannot know when the level is touched):
  (a) the entry is allowed only if the ENTRY DAY CLOSES at or above the line (a day that touches the level but closes below the line = no trade, setup reset);
  (b) the Bollinger filter uses the ENTRY DAY'S CLOSE (and the band includes that close).
So this module gives two machines and two filters:
  orig_setups(..., eod_check=True)   exactly your loop (a) included.
  orig_setups(..., eod_check=False)  LIVE machine: identical, but the entry fires on the touch no matter how the day closes (no (a)).  Later days: a close below the line still kills the setup.
  bb_flags()  bb_eod = your filter (entry-day close vs the band of the entry day)   |   up_prev / lo_prev = the band of the PREVIOUS day (closes d-20 .. d-1): the live filter compares the entry price with it.
"""
import numpy as np
import pandas as pd

BB_PERIOD = 20
BB_STD = 2.0


def _roll_ref(H, L, lookback):
    """High_10 / Low_10 exactly like df['High'].shift(1).rolling(10).max() / min()  (NaN for the first `lookback` rows)."""
    h = pd.Series(np.asarray(H, float)).shift(1).rolling(window=lookback).max().values
    l = pd.Series(np.asarray(L, float)).shift(1).rolling(window=lookback).min().values
    return h, l


def bollinger(C, period=BB_PERIOD, k=BB_STD):
    """-> (upper, lower, upper_prev, lower_prev).  upper / lower = your Filter_Upper / Filter_Lower (the band INCLUDING day i).  *_prev = the same band of day i-1 (what is known before day i)."""
    s = pd.Series(np.asarray(C, float))
    mid = s.rolling(window=period).mean(); sd = s.rolling(window=period).std()
    up, lo = (mid + k * sd).values, (mid - k * sd).values
    return up, lo, np.r_[np.nan, up[:-1]], np.r_[np.nan, lo[:-1]]


def _long_machine(O, H, L, C, lookback, start, eod_check):
    """LONG state machine.  -> list of (entry day index, level, line, breakout day index).  (SHORT = this on the mirrored arrays.)"""
    n = len(C)
    h10, _ = _roll_ref(H, L, lookback)
    out = []
    state, line, level, bidx = "SEARCHING", 0.0, 0.0, -1
    for i in range(start, n):
        c, h = C[i], H[i]
        if state == "SEARCHING":
            if c > h10[i]: state, line, level, bidx = "PULLBACK_PHASE", h10[i], h, i
        else:
            if eod_check and c < line:                                            # original: the close decides first -> reset (maybe a new setup right away)
                state = "SEARCHING"
                if c > h10[i]: state, line, level, bidx = "PULLBACK_PHASE", h10[i], h, i
            elif h >= level:                                                      # touch of the level -> entry day (setup used up)
                out.append((i, float(level), float(line), bidx)); state = "SEARCHING"
            elif c < line:                                                        # live machine: no touch today and the close is below the line -> invalid
                state = "SEARCHING"
                if c > h10[i]: state, line, level, bidx = "PULLBACK_PHASE", h10[i], h, i
    return out


def orig_setups(O, H, L, C, long=True, lookback=10, start=None, eod_check=True):
    """-> list of dicts: entry (index of the entry day), level, line, breakout (index of the breakout day), all REAL prices.
    start = first index looked at (None = your script's max(lookback, 20) + 5)."""
    O, H, L, C = (np.asarray(x, float) for x in (O, H, L, C))
    st = max(lookback, BB_PERIOD) + 5 if start is None else start
    if long: res = _long_machine(O, H, L, C, lookback, st, eod_check)
    else: res = _long_machine(-O, -L, -H, -C, lookback, st, eod_check)
    sg = 1.0 if long else -1.0
    return [dict(entry=int(i), level=sg * lvl, line=sg * ln, breakout=int(b)) for i, lvl, ln, b in res]


def bb_flags(C, i, long=True):
    """-> (bb_eod, up_prev) for entry day index i.   LONG: bb_eod = close[i] > upper band (your filter), up_prev = upper band of day i-1.   SHORT: bb_eod = close[i] < lower band, up_prev = LOWER band of day i-1
    (the column is called 'band_prev' in the candidates file).  NaN band -> (False, nan)."""
    up, lo, upp, lop = bollinger(C)
    if long: return bool(C[i] > up[i]) if np.isfinite(up[i]) else False, float(upp[i]) if np.isfinite(upp[i]) else float("nan")
    return bool(C[i] < lo[i]) if np.isfinite(lo[i]) else False, float(lop[i]) if np.isfinite(lop[i]) else float("nan")


def candidates(O, H, L, C, long=True, lookback=10):
    """UNION of the original machine and the live machine for one stock and one direction (one row per entry DAY).
    -> list of dicts: entry, level, line, breakout, in_orig (your exact loop would take this entry day), in_live (the live machine would), bb_eod (your Bollinger filter passes), band_prev (prior-day band).
    The live machine sees every entry of the original loop except the days it resets; where both give a different level for the same day the live one is kept (in_orig False)."""
    o = {s["entry"]: s for s in orig_setups(O, H, L, C, long, lookback, eod_check=True)}
    v = {s["entry"]: s for s in orig_setups(O, H, L, C, long, lookback, eod_check=False)}
    C_ = np.asarray(C, float)
    rows = []
    for i in sorted(set(o) | set(v)):
        s = v.get(i) or o[i]
        same = i in o and abs(o[i]["level"] - s["level"]) < 1e-9
        eod, band = bb_flags(C_, i, long)
        rows.append(dict(entry=i, level=s["level"], line=s["line"], breakout=s["breakout"], in_orig=bool(same), in_live=i in v, bb_eod=eod, band_prev=band))
    return rows
