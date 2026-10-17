"""trendline_backtest.py - TRENDLINE break -> retest -> re-break strategy, trendline drawn on the 1-HOUR and the 4-HOUR chart, all F&O stock options (Dhan).
Separate from the shape-rule strategy: no candle-shape filter here.

  python trendline_backtest.py check     test Dhan access (also prints a sample of the hourly candles)
  python trendline_backtest.py run       full backtest for TL_START .. TL_END (resumable - run again after a polite stop)
  python trendline_backtest.py summary   rebuild the result CSVs from the saved option data (no API calls)

CHARTS     1H = Dhan 60-minute stock candles (09:15, 10:15 ... 15:15).  4H = those candles joined into 09:15-13:15 and 13:15-15:30.   Each is its own variant.
SETUP      written for LONG (resistance turns support); SHORT is the exact mirror (support turns resistance).
  Trendline   falling line through the last two swing highs (SHORT: rising line through the last two swing lows)
  Breakout    a candle of that chart CLOSES above the line (first close above it since the 2nd swing high)
  H_break     the HIGH of the breakout candle, stored   (SHORT: L_break = LOW of the breakdown candle)
  Pullback    a later candle touches the line: Low <= line  (SHORT: High >= line)
  Validation  that candle CLOSES above the line (SHORT: below) -> the line holds.  A close back through the line first, or too many candles, cancels the setup.
  Entry       the NEXT trading day, 09:15-09:25: price breaks above H_break (SHORT: below L_break).  One setup = one entry day.
              If price had already traded beyond H_break / L_break between the validation candle and the end of that day, the trigger has happened -> setup skipped.
  Swing high/low = highest high / lowest low of k candles on each side, usable only once confirmed (no look-ahead).  Swing points must be MIN_GAP candles apart, the
  line must slope the right way and no close may lie beyond it between the two swing points.  k, MIN_GAP, MAX_AGE, WAIT are in PARAMS below.
ENTRY TYPES  ALL (first 1-minute touch) | OPEN_0915 | FROM_0920_4C | RECROSS_0920_4C - always inside 09:15..09:25.   LONG buys the ATM call, SHORT the ATM put.
EXIT       trade stop-loss 10 % of the premium (TL_SLS) or the time exit at 09:30.   CAPITAL: at most Rs 60,000 per trade (lots = 60000 // (premium x lot)).
Charges, taxes and slippage are not included.  Lot sizes are today's values for all years.

Results in trendline_results/ : all_trades.csv, summary.csv, top_by_pnl.csv, top_by_roi.csv, top_by_profit_factor.csv, top_by_win_rate.csv
  (+ events.csv, parts/, candidates_*.csv, REPORT.txt)
"""
import os, sys, time
for k in ("START", "END", "SYMBOLS", "CAP"):                                # TL_* names -> the COMBO_* names the engine reads
    if os.environ.get("TL_" + k): os.environ["COMBO_" + k] = os.environ["TL_" + k]
os.environ["COMBO_OUT"] = os.environ.get("TL_OUT") or "trendline_results"
os.environ["DAY_SLS"] = "0"                                                # no day stop-loss in this test

import numpy as np, pandas as pd
from datetime import date, timedelta
import combo_dayrisk_backtest as C
import bpb_fno_backtest as B
import strategy_reports as R
from bpb_fno_backtest import Dhan, Stop, Fatal, stream, load_master, frame

C.SLS = [int(x) for x in (os.environ.get("TL_SLS") or "10").replace(",", " ").split()]
C.DAY_SLS = [0]
TFS = ["1H", "4H"]
# candles on each side of a swing point (k), min candles between the two swing points, max candles from the 2nd swing point to the breakout, max candles breakout -> validation
PARAMS = {"1H": dict(k=3, min_gap=7, max_age=100, wait=21),             # 7 candles = 1 trading day, 21 = 3 days
          "4H": dict(k=3, min_gap=4, max_age=40, wait=10)}              # 2 candles = 1 trading day
WARMUP_DAYS = 60                                                        # hourly history before the start date, so that lines exist on day one
SPAN = 85                                                               # days per Dhan request (max 90)
SPLIT_T = 13 * 60 + 15                                                  # 4H candle A = 09:15-13:15, B = 13:15-15:30


# ------------------------------------------------------------------ Dhan hourly candles
def eq_hourly(dh, sid, d0, d1):
    """60-minute stock candles d0..d1 (dates), <= 90 days per request.  None = call failed."""
    j = dh.post("/charts/intraday", {"securityId": str(sid), "exchangeSegment": "NSE_EQ", "instrument": "EQUITY", "interval": "60",
                                     "oi": False, "fromDate": f"{d0} 09:15:00", "toDate": f"{d1} 15:30:00"})
    if j is None: return None
    fr = frame(j.get("data", j) if isinstance(j.get("data", None), dict) else j)
    return fr if fr is not None else pd.DataFrame(columns=["o", "h", "l", "c"], index=pd.DatetimeIndex([]))


def hourly_range(dh, sid, d0, d1):
    out, a = [], d0
    while a <= d1:
        b = min(a + timedelta(days=SPAN - 1), d1)
        f = eq_hourly(dh, sid, a, b)
        if f is None: return None
        out.append(f); a = b + timedelta(days=1)
    f = pd.concat(out) if out else pd.DataFrame(columns=["o", "h", "l", "c"])
    return f[~f.index.duplicated()].sort_index()


def to_4h(h):
    """Hourly candles (indexed by start time) -> 4-hour candles 09:15-13:15 and 13:15-15:30."""
    if h.empty: return h
    mins = h.index.hour * 60 + h.index.minute
    key = pd.Series(h.index.strftime("%Y-%m-%d") + np.where(mins < SPLIT_T, "A", "B"), index=h.index)
    g = h.groupby(key.values, sort=False)
    out = g.agg(o=("o", "first"), h=("h", "max"), l=("l", "min"), c=("c", "last"))
    out.index = pd.DatetimeIndex([x.index[0] for _, x in g])
    return out.sort_index()


# ------------------------------------------------------------------ the trendline state machine (any chart)
def tl_signals(O, H, L, C_, long, k=3, min_gap=5, max_age=60, wait=15):
    """Trendline break-retest on candles of one chart.  Returns [(validation candle n, entry level, breakout candle, line value at n)].
    SHORT = mirror: the series are negated, the returned level / line are negated back."""
    if not long: O, H, L, C_ = -O, -L, -H, -C_
    N = len(C_); piv = []                                                # swing highs: index p, usable from candle p + k + 1
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


def signals_for(stock, hourly, tf, t0, t1, pre_tol=None):
    """One stock, one chart -> candidate entry-day rows.  hourly = raw 60-minute candles (also used for the day-open prefilter)."""
    pre_tol = C.PRE_TOL if pre_tol is None else pre_tol
    bars = hourly if tf == "1H" else to_4h(hourly)
    if len(bars) < 60: return []
    O, H, L, Cl = (bars[c].values.astype(float) for c in ("o", "h", "l", "c"))
    day = np.array(bars.index.strftime("%Y-%m-%d")); udays = sorted(set(day))
    nxt = {d: udays[i + 1] for i, d in enumerate(udays[:-1])}
    first = hourly.groupby(hourly.index.strftime("%Y-%m-%d")).first()    # first hourly candle of every day (09:15-10:15)
    rows = []
    for long in (True, False):
        for n, lvl, tb, ln in tl_signals(O, H, L, Cl, long, **PARAMS[tf]):
            e = nxt.get(day[n])
            if e is None or not (str(t0.date()) <= e <= str(t1.date())) or e not in first.index: continue
            same = day == day[n]; same[:n] = False                       # from the validation candle to the end of its day
            if (H[same].max() >= lvl) if long else (L[same].min() <= lvl): continue      # trigger had already happened that day
            f = first.loc[e]
            if not ((f.h >= lvl and f.o >= lvl * (1 - pre_tol)) if long else (f.l <= lvl and f.o <= lvl * (1 + pre_tol))): continue
            up, lo = H[n] - max(O[n], Cl[n]), min(O[n], Cl[n]) - L[n]
            rows.append(dict(source="TL_" + tf, stock=stock, direction="LONG" if long else "SHORT", ref=round(lvl, 2), signal_date=day[n], date=e,
                             yahoo_open=float(f.o), breakout_date=day[tb], line=round(ln, 2),
                             green=int(Cl[n] > O[n]), red=int(Cl[n] < O[n]), upper_longer=int(up > lo), lower_longer=int(lo > up)))
    return rows


# ------------------------------------------------------------------ step 1: hourly candles -> candidate entry days (resumable, one file per stock)
def build_candidates(dh, mst, st):
    t0, t1 = pd.Timestamp(C.START), pd.Timestamp(C.END)
    d0 = (t0 - pd.Timedelta(days=WARMUP_DAYS)).date(); d1 = min(t1.date(), date.today()) + timedelta(days=1)
    pdir = f"{C.OUT}/tl_candidates"; os.makedirs(pdir, exist_ok=True)
    stocks = [s for s in C.UNIVERSE if s in mst]
    miss = [s for s in C.UNIVERSE if s not in mst]
    if miss: print(f"not in Dhan stock-option list - skipped: {miss}", flush=True)
    todo = [s for s in stocks if not os.path.exists(f"{pdir}/{s}_{C.START}_{C.END}.csv")]
    print(f"Hourly candles: {len(todo)} stocks to fetch ({len(stocks) - len(todo)} already done), {d0} .. {d1}", flush=True)

    def work(s):
        h = hourly_range(dh, mst[s][0], d0, d1)
        if h is None: return None
        if h.empty: return [], 0
        mm = h.index.hour * 60 + h.index.minute
        h = h[(mm >= 9 * 60 + 15) & (mm <= 15 * 60 + 15)]
        return [r for tf in TFS for r in signals_for(s, h, tf, t0, t1)], len(h)

    fails = [0]

    def handle(s, res):
        if res is None:
            fails[0] += 1; print(f"hourly candles {s}: FAILED (retried on the next run), calls {dh.n}", flush=True); return
        rows, nb = res
        cols = ["source", "stock", "direction", "ref", "signal_date", "date", "yahoo_open", "breakout_date", "line", "green", "red", "upper_longer", "lower_longer"]
        pd.DataFrame(rows, columns=cols).to_csv(f"{pdir}/{s}_{C.START}_{C.END}.csv", index=False)
        C.checkpoint()
        print(f"hourly candles {s}: {nb} candles, {len(rows)} candidate days, calls {dh.n}", flush=True)

    C.FLUSHER[0] = None
    stream(todo, work, handle)
    if fails[0]: raise Stop(f"{fails[0]} stock(s) failed to download - run again to retry them")
    parts = [pd.read_csv(f"{pdir}/{s}_{C.START}_{C.END}.csv") for s in stocks]
    cand = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    print(f"Trendline candidates: {len(cand)} entry days ({', '.join(f'{k} = {v}' for k, v in cand.groupby('source').size().items())})", flush=True)
    return cand


# ------------------------------------------------------------------ variants, reports
def variants(ev):
    return [(f"TRENDLINE | {tf} | {ty}", ev.source.eq("TL_" + tf) & ev.type.eq(ty)) for tf in TFS for ty in C.TYPES]


def summary():
    paths = C.load_paths(); ep = f"{C.OUT}/events.csv"
    if paths.empty or not os.path.exists(ep): print("No saved option data yet - run the backtest first.", flush=True); return
    ev = pd.read_csv(ep); ev = ev[ev.source.isin(["TL_" + tf for tf in TFS])]
    d, t = C.main_simulation(ev, paths)
    R.write_reports(t, C.OUT)
    C.report(len(d))


# ------------------------------------------------------------------ modes
def check():
    C.check()
    dh = Dhan(); mst = load_master(); d1 = date.today(); d0 = d1 - timedelta(days=10)
    h = eq_hourly(dh, mst["RELIANCE"][0], d0, d1)
    if h is None or h.empty: print("Hourly call: no data"); return
    print(f"Hourly call: {len(h)} candles; start times on the last day: {[f'{x:%H:%M}' for x in h.index[h.index.date == h.index[-1].date()]]}  (expected 09:15 .. 15:15)")
    print("4H candles on the last day:\n" + to_4h(h[h.index.date == h.index[-1].date()]).to_string())


def run():
    os.makedirs(C.OUT, exist_ok=True); st = C.load_state()
    dh = Dhan(); mst = load_master()
    try:
        cp = f"{C.OUT}/candidates_{C.START}_{C.END}.csv"
        if os.path.exists(cp): cand = pd.read_csv(cp)
        else:
            cand = build_candidates(dh, mst, st)
            if cand.empty: print("No candidate days in this range."); return
            cand.to_csv(cp, index=False)
        print(f"Candidate days {C.START}..{C.END}: {len(cand)}", flush=True)
        ev = C.step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= C.START) & (ev["date"] <= C.END)] if len(ev) else ev
        print(f"Entry events (09:15-09:25): {len(ev)}", flush=True)
        if len(ev): C.step_options(dh, ev, mst, st)
        print("ALL STEPS FINISHED", flush=True)
    except Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        B.print_stats(dh); C.progress(); summary(); C.checkpoint(True)


C.variants = variants
C.summary = summary

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": check()
        elif mode == "run": run()
        elif mode in ("summary", "range"): os.makedirs(C.OUT, exist_ok=True); C.progress(); summary()
        else: sys.exit("use: python trendline_backtest.py check | run | summary")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
