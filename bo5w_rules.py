"""bo5w_rules.py - rules of the "5-day-high breakout + Bollinger + previous day green + longer upper wick" study (LONG call, entry at the breakout day's close, exit the NEXT morning).
Pure numpy / pandas (no Dhan, no Yahoo, no engine), so test_bo5w.py can check every rule offline.

DAILY SETUP (day t = breakout day B), exactly your Colab script:
  1. Close[t] > highest High of the previous 5 days (day t itself not included)
  2. Close[t] > upper Bollinger band (20-day mean of Close + 2 x std, pandas std = ddof 1)
  3. day t-1 was green (Close > Open)
  4. upper wick of day t > lower wick of day t   (upper = High - max(Open, Close), lower = min(Open, Close) - Low)
  ENTRY  = buy the ATM call at the close of day t.      The next trading day (B+1) is the exit day.
  GAP RULE (one of the stop-loss options) = the stock OPENS on B+1 below the entry price (Open[B+1] < Close[B]) -> sell the option at its 09:15 open.

EXIT GRID (all on B+1, option 1-minute candles):
  time exit  0915o = open of the 09:15 candle | 0915c = close of the 09:15 candle | 0916c | 0920c | 0930c
  stop-loss  none / 20 / 40 / 60 % of the premium, each with the gap rule off or on (gap rule alone = 'none' + gap on)
  target     40 / 60 / 80 / 100 / 120 / 200 % of the premium or none
  Fills      stop / target = first 1-minute low / high that touches the level; a gap through it fills at that candle's open; stop and target in the same minute -> STOP.
"""
import numpy as np
from datetime import date, timedelta

REASON = {1: "STOP", 2: "STOP (gap through)", 3: "TARGET", 4: "TARGET (gap through)", 5: "TIME", 7: "GAP RULE (stock opened below entry)"}
OPEN_TOL = 5            # minutes: the 09:15 candle may be missing; the first candle within 5 minutes is used
STALE = 5               # minutes: a time-exit candle older than this is flagged thin


# ------------------------------------------------------------------ daily setup
def signals(O, H, L, C, lookback=5, bb_n=20, bb_k=2.0, need_next=True):
    """-> list of dicts {i, level5, upper_bb, upper_wick, lower_wick} for every breakout day i that meets all four rules.
    need_next: only days that have a following day (B+1) in the data."""
    O, H, L, C = (np.asarray(x, float) for x in (O, H, L, C))
    n = len(C); out = []
    for i in range(max(lookback, bb_n - 1), n - (1 if need_next else 0)):
        if i < 1: continue
        hi5 = H[i - lookback:i].max()
        win = C[i - bb_n + 1:i + 1]
        up = win.mean() + bb_k * win.std(ddof=1)
        uw = H[i] - max(O[i], C[i]); lw = min(O[i], C[i]) - L[i]
        if C[i] > hi5 and C[i] > up and C[i - 1] > O[i - 1] and uw > lw:
            out.append(dict(i=i, level5=float(hi5), upper_bb=float(up), upper_wick=float(uw), lower_wick=float(lw)))
    return out


# ------------------------------------------------------------------ monthly expiry calendar (stock options)
def _last_dow(y, m, dow):
    d = date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)
    while d.weekday() != dow: d -= timedelta(days=1)
    return d


def expiry_calc(d):
    """Monthly stock-option expiry on or after d: last Thursday up to Aug 2025, last Tuesday from Sep 2025 (before any holiday shift)."""
    y, m = d.year, d.month
    for _ in range(14):
        e = _last_dow(y, m, 3 if (y, m) < (2025, 9) else 1)
        if e >= d: return e
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def real_expiry(d, tradedays):
    """The monthly expiry of the contract that is 'nearest' on day d, moved to the previous trading day when the calendar day is a holiday.  tradedays = set of date objects."""
    e = expiry_calc(d)
    for _ in range(7):
        if e in tradedays or e > max(tradedays): break
        e -= timedelta(days=1)
    return e


# ------------------------------------------------------------------ exit variants
def parse_exit(tag):
    """'0915o' -> (555, 'o'),  '0920c' -> (560, 'c')."""
    tag = tag.strip().lower()
    if len(tag) != 5 or tag[4] not in "oc" or not tag[:4].isdigit(): raise ValueError(f"bad exit {tag!r} - use e.g. 0915o, 0915c, 0916c, 0920c, 0930c")
    return int(tag[:2]) * 60 + int(tag[2:4]), tag[4]


def exit_label(tag):
    m, f = parse_exit(tag)
    return f"{m // 60:02d}:{m % 60:02d} {'open' if f == 'o' else 'close'}"


def variants(exits, sls, gaps, tps):
    """-> list of (exit tag, sl % (0 = none), gap rule 0/1, tp % (0 = none))"""
    return [(ex, sl, g, tp) for ex in exits for sl in sls for g in gaps for tp in tps]


def simulate(entry, cd, ex_tag, sl, gap_on, tp, gap_flag):
    """One trade, one variant.
    entry = option entry price; cd = array of next-day option candles [[minute of day, o, h, l, c], ...] sorted by time (only the first ~35 minutes are needed);
    ex_tag = time exit; sl / tp in % of the premium (0 = none); gap_on = the stock-gap rule is part of the stop; gap_flag = the stock opened below the entry price.
    -> (exit minute of day, exit price, reason code, thin flag) or None when there is no candle to exit on (variant not available for this trade)."""
    if cd is None or len(cd) == 0: return None
    cd = np.asarray(cd, float)
    mm, o, h, l, c = cd[:, 0], cd[:, 1], cd[:, 2], cd[:, 3], cd[:, 4]
    M, fld = parse_exit(ex_tag)
    first_ok = mm[0] - 555 <= OPEN_TOL                                    # first candle of the day within 5 minutes of 09:15
    if gap_on and gap_flag:
        if not first_ok: return None
        return int(mm[0]), float(o[0]), 7, int(mm[0] > 555)
    if fld == "o":                                                        # exit at the open of the first candle at / after M
        j = int(np.searchsorted(mm, M, side="left"))
        if j >= len(mm) or mm[j] - M > OPEN_TOL: return None
        return int(mm[j]), float(o[j]), 5, int(mm[j] > M)
    j = int(np.searchsorted(mm, M, side="right")) - 1                     # last candle at / before M
    if j < 0:
        j = 0
        if mm[0] - M > OPEN_TOL: return None                              # nothing within 5 minutes after M either
    thin = int(M - mm[j] > STALE)
    sthr = entry * (1 - sl / 100) if sl else None
    tthr = entry * (1 + tp / 100) if tp else None
    for k in range(j + 1):
        if sthr is not None and l[k] <= sthr:
            gap = o[k] <= sthr; return int(mm[k]), float(o[k] if gap else sthr), 2 if gap else 1, 0
        if tthr is not None and h[k] >= tthr:
            gap = o[k] >= tthr; return int(mm[k]), float(o[k] if gap else tthr), 4 if gap else 3, 0
    return int(mm[j]), float(c[j]), 5, thin
