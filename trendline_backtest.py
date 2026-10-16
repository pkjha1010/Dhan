"""trendline_backtest.py - TRENDLINE BREAK -> RETEST -> RE-BREAK strategy on ALL F&O stock options (Yahoo daily + Dhan 1-minute).

  python trendline_backtest.py check     test Dhan access
  python trendline_backtest.py run       full backtest for TL_START .. TL_END (resumable - run again after a polite stop)
  python trendline_backtest.py summary   rebuild every table from the saved option data (no API calls)

It re-uses the engine of combo_dayrisk_backtest.py (Dhan client, 1-minute stock candles, ATM option paths, trade stop-loss, day stop-loss, tables);
only the daily signal is new.

SETUP (daily candles, written for LONG; SHORT is the exact mirror)
  LONG  : resistance turns support                         SHORT : support turns resistance
    Trendline   falling line through the last two swing highs   (SHORT: rising line through the last two swing lows)
    Breakout    a daily candle CLOSES above the line (the previous close was on/below it, and the line was intact since the 2nd swing high)
    H_break     the HIGH of that breakout candle, stored   (SHORT: L_break = LOW of the breakdown candle)
    Pullback    a later candle touches the line: Low <= line  (SHORT: High >= line)
    Validation  that same candle CLOSES above the line      (SHORT: below) -> the line holds.  It is the SIGNAL candle ("previous candle").
                A close back through the line before the validation cancels the setup (also after WAIT days).
    Entry       NEXT day, 09:15-09:25: price breaks above H_break  (SHORT: below L_break).  One setup = one entry day.
  Swing high/low = highest high / lowest low of PIVOT_K bars on each side, usable only once confirmed (no look-ahead).  The two swing points must be
  at least MIN_GAP bars apart, the line must slope the right way, and no close may lie beyond the line between the two swing points.
  If the signal candle itself already traded beyond H_break / L_break the trigger had already happened -> setup skipped.

SHAPE FILTER (the "previous candle" = the validation candle the day before the entry), 5 variants, as in the shapecmp study:
  NO_SHAPE_RULE | PREV_GREEN | PREV_RED | UPPER_WICK_LONGER | LOWER_WICK_LONGER
ENTRY TYPES (as in the shapecmp study): ALL | OPEN_0915 | FROM_0920_4C | RECROSS_0920_4C - always inside 09:15..09:25.
OPTION     LONG buys the ATM call, SHORT the ATM put (nearest monthly expiry), price = close of the entry-minute candle.
EXIT       trade stop-loss 10 % of the premium (TL_SLS) or the time exit at 09:30.   CAPITAL: at most Rs 60,000 per trade (lots = 60000 // (premium x lot)).
Charges, taxes and slippage are not included.  Lot sizes are today's values for all years.

Output folder trendline_results/ - same files as combo_results/ (summary.csv, roi_matrix.csv, daily_pnl.csv.gz, trades_no_day_sl.csv.gz, REPORT.txt ...).
"""
import os, sys
for k in ("START", "END", "SYMBOLS", "OUT", "CAP"):                        # TL_* names -> the COMBO_* names the engine reads
    if os.environ.get("TL_" + k): os.environ["COMBO_" + k] = os.environ["TL_" + k]
os.environ.setdefault("COMBO_OUT", "trendline_results")
os.environ.setdefault("DAY_SLS", "0")                                       # trade SL only; set DAY_SLS="0,6000,12000" to test a day stop-loss too

import numpy as np, pandas as pd
import combo_dayrisk_backtest as C
from bpb_fno_backtest import Fatal

C.SLS = [int(x) for x in (os.environ.get("TL_SLS") or "10").replace(",", " ").split()]
PIVOT_K = int(os.environ.get("PIVOT_K") or 3)           # bars on each side of a swing point
MIN_GAP = int(os.environ.get("MIN_GAP") or 5)           # min bars between the two swing points
MAX_AGE = int(os.environ.get("MAX_AGE") or 60)          # a trendline is used for a breakout only this many bars after its 2nd swing point
WAIT = int(os.environ.get("WAIT") or 15)                # max bars from the breakout to the validated pullback
SRC = "TRENDLINE"


def tl_signals(O, H, L, C_, long, k=None, min_gap=None, max_age=None, wait=None):
    """Trendline break-retest state machine on daily candles.  Returns [(signal day n, entry level, breakout day, line value on day n)]; entry is on day n+1.
    SHORT = mirror: the series are negated, the returned level / line are negated back."""
    k = PIVOT_K if k is None else k; min_gap = MIN_GAP if min_gap is None else min_gap
    max_age = MAX_AGE if max_age is None else max_age; wait = WAIT if wait is None else wait
    if not long: O, H, L, C_ = -O, -L, -H, -C_
    N = len(C_); piv = []                                                # swing highs: (index p, confirmed on bar p + k)
    for p in range(k, N - k):
        if H[p] >= H[p - k:p].max() and H[p] > H[p + 1:p + k + 1].max(): piv.append(p)
    out, st = [], None
    for t in range(2 * k + 1, N):
        if st is not None:                                               # ---- broken out: wait for the pullback to the line
            p1, p2, hb, tb = st; sl = (H[p2] - H[p1]) / (p2 - p1); ln = H[p1] + sl * (t - p1)
            if C_[t] < ln or t - tb > wait: st = None                    # closed back through the line / waited too long
            elif L[t] <= ln and C_[t] > ln:                              # touched the line and closed above it -> validated
                if H[t] < hb: out.append((t, hb, tb, ln))
                st = None
            continue
        conf = [p for p in piv if p + k <= t - 1]
        if len(conf) < 2: continue
        p1, p2 = conf[-2], conf[-1]
        if H[p2] >= H[p1] or p2 - p1 < min_gap or t - p2 > max_age: continue
        sl = (H[p2] - H[p1]) / (p2 - p1)
        xs = np.arange(p1 + 1, t); lv = H[p1] + sl * (xs - p1)
        if (C_[p1 + 1:p2] > lv[:p2 - p1 - 1]).any(): continue           # the line must hold between its two swing points ...
        if (C_[p2 + 1:t] > lv[p2 - p1:]).any(): continue                # ... and since the 2nd one: this candle is the FIRST close above it
        if C_[t] > H[p1] + sl * (t - p1): st = (p1, p2, H[t], t)
    sg = 1.0 if long else -1.0
    return [(n, sg * hb, tb, sg * ln) for n, hb, tb, ln in out]


def candidates():
    import yfinance as yf
    t0, t1 = pd.Timestamp(C.START), pd.Timestamp(C.END)
    raw = yf.download([s + ".NS" for s in C.UNIVERSE], start=str((t0 - pd.Timedelta(days=250)).date()), end=str((t1 + pd.Timedelta(days=3)).date()),
                      group_by="ticker", auto_adjust=False, progress=False, threads=True)
    rows, nst = [], 0
    for s in C.UNIVERSE:
        try: d = raw[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
        if len(d) < 60: continue
        nst += 1
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        O, H, L, Cl = (d[c].values.astype(float) for c in ("Open", "High", "Low", "Close"))
        dates = d.index.strftime("%Y-%m-%d")
        for long in (True, False):
            for n, lvl, tb, ln in tl_signals(O, H, L, Cl, long):
                e = n + 1
                if e >= len(d) or not (t0 <= d.index[e] <= t1): continue
                if not ((H[e] >= lvl and O[e] >= lvl * (1 - C.PRE_TOL)) if long else (L[e] <= lvl and O[e] <= lvl * (1 + C.PRE_TOL))): continue
                up, lo = H[n] - max(O[n], Cl[n]), min(O[n], Cl[n]) - L[n]
                rows.append(dict(source=SRC, stock=s, direction="LONG" if long else "SHORT", ref=round(lvl, 2), signal_date=dates[n], date=dates[e],
                                 yahoo_open=float(O[e]), breakout_date=dates[tb], line=round(ln, 2),
                                 green=int(Cl[n] > O[n]), red=int(Cl[n] < O[n]), upper_longer=int(up > lo), lower_longer=int(lo > up)))
    if nst == 0: raise Fatal("Yahoo download gave no data for any stock - run again later")
    r = pd.DataFrame(rows)
    print(f"Yahoo: {nst} stocks, {len(r)} trendline candidate entry days", flush=True)
    return r


def variants(ev):
    flt = {"NO_SHAPE_RULE": lambda e: e.source.eq(SRC), "PREV_GREEN": lambda e: e.source.eq(SRC) & e.green.eq(1), "PREV_RED": lambda e: e.source.eq(SRC) & e.red.eq(1),
           "UPPER_WICK_LONGER": lambda e: e.source.eq(SRC) & e.upper_longer.eq(1), "LOWER_WICK_LONGER": lambda e: e.source.eq(SRC) & e.lower_longer.eq(1)}
    return [(f"TRENDLINE | {sh} | {ty}", flt[sh](ev) & ev.type.eq(ty)) for sh in C.SHAPES for ty in C.TYPES]


C.yahoo_candidates = candidates                                          # the engine's run() / summary() now use the trendline signal
C.variants = variants

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": C.check()
        elif mode == "run": C.run()
        elif mode in ("summary", "range"): os.makedirs(C.OUT, exist_ok=True); C.progress(); C.summary()
        else: sys.exit("use: python trendline_backtest.py check | run | summary")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
