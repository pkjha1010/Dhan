"""gap_nifty_rules.py - the NIFTY50 DAY-DIRECTION filter for the GAP strategy, pure numpy / pandas (no Dhan, no Yahoo), so test_gap_nifty.py can check it.

  LONG  trade is taken only when, at the entry minute, the NIFTY50 price is ABOVE the NIFTY50 open of the SAME day.
  SHORT trade is taken only when, at the entry minute, the NIFTY50 price is BELOW the NIFTY50 open of the SAME day.
  Equal (price == open) passes neither side.

  nifty open  = Open of the first 1-minute NIFTY candle of the day (09:15).
  nifty price = Close of the 1-minute NIFTY candle that starts at the entry minute (the same candle the option entry price is taken from).  If that minute is
                missing the last candle at or before it is used.  A day with no NIFTY candles (or none up to the entry minute) is "not judgeable" and the trade is dropped.
"""
import numpy as np
import pandas as pd


def day_tables(nifty):
    """nifty = DataFrame indexed by candle start (naive IST), columns o h l c.  -> {'YYYY-MM-DD': (minutes since midnight array, open of the day, close array)}"""
    out = {}
    if nifty is None or len(nifty) == 0: return out
    nifty = nifty.sort_index()
    for day, g in nifty.groupby(nifty.index.strftime("%Y-%m-%d")):
        m = (g.index.hour.values * 60 + g.index.minute.values).astype(int)
        out[day] = (m, float(g.o.values[0]), g.c.values.astype(float))
    return out


def hm_to_min(t):
    """'09:16' -> 556"""
    h, m = str(t).split(":")[:2]
    return int(h) * 60 + int(m)


def nifty_open_price(tables, date, entry_time):
    """-> (nifty open of the day, nifty price at the entry minute) or None when it can not be judged."""
    t = tables.get(str(date))
    if t is None: return None
    m, o, c = t
    k = int(np.searchsorted(m, hm_to_min(entry_time), side="right")) - 1       # last candle starting at or before the entry minute
    if k < 0: return None
    return o, float(c[k])


def passes(nifty_open, nifty_price, direction):
    """LONG: price > open.  SHORT: price < open."""
    return bool(nifty_price > nifty_open) if str(direction).upper() == "LONG" else bool(nifty_price < nifty_open)


def add_nifty_flag(T, tables):
    """trades (columns entry_date, entry_time, direction) + columns nifty_open, nifty_price, nifty_ok (True / False / NaN when not judgeable)."""
    T = T.copy()
    cache = {}
    for d, t in T[["entry_date", "entry_time"]].drop_duplicates().itertuples(index=False):
        cache[(d, t)] = nifty_open_price(tables, d, t)
    op = [cache[(d, t)] for d, t in zip(T.entry_date, T.entry_time)]
    T["nifty_open"] = [x[0] if x else np.nan for x in op]
    T["nifty_price"] = [x[1] if x else np.nan for x in op]
    T["nifty_ok"] = [passes(x[0], x[1], dr) if x else np.nan for x, dr in zip(op, T.direction)]
    return T
