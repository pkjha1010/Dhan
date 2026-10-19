"""wru5_backtest.py - backtest of 8 WRU-SHORT strategies (5 ideas) on all F&O stock options (Dhan 1-minute data), Jan 2023 .. Oct 2026.

  python wru5_backtest.py check     test Dhan access
  python wru5_backtest.py run       full backtest (resumable - run again after a polite stop)
  python wru5_backtest.py summary   rebuild every result file from the saved option data (no API calls)

WRU = the signal candle is RED (close < open) and its UPPER wick is longer than its LOWER wick.  Every strategy is a SHORT = buy the ATM PUT (nearest monthly expiry,
strike locked at entry), exactly like all8_backtest.py (same option data, same exit engine - it is imported, nothing is copied).

THE 8 STRATEGIES
  1) RLOW_1H_WRU / RLOW_4H_WRU     the SHAPECMP rolling-LOW rule run on the 1-hour / 4-hour chart: a candle closes below the ROLLING LOW of the previous 10 candles of that chart (W_LOOKBACK),
                                   a later candle (within 20 candles) closes back above that low = the signal candle; it must be a WRU candle.  The rolling low is the LINE.
                                   Entry on the NEXT trading day when price falls to the line (skipped if it already did so later on the signal day).
  2) WRU_RES_LINE / WRU_ROLL5_HIGH WRU DAILY candle whose HIGH is above and whose CLOSE is above the RESISTANCE (falling trendline through the last two daily pivot highs, 2 candles each side;
                                   the first close above it) / the 5-DAY ROLLING HIGH (highest high of the 5 days before).  Entry next day when price falls back to that level.
  3) WRU_SUP_LINE / WRU_ROLL5_LOW  the same WRU candle (high above and close above) with SUPPORT (rising trendline through the last two daily pivot lows) / the 5-DAY ROLLING LOW as the level.
                                   Entry next day when price falls to / through the level (a break of support).
  4) WRU_PIVOT_HIGH                WRU daily candle whose high and close are above the latest confirmed PIVOT HIGH (2 candles each side; first close above it).  Entry next day when price falls to the pivot.
  5) WRU_PIVOT_LOW                 the same with the latest confirmed PIVOT LOW.
  The line value used for the entry is the value of the line ON THE ENTRY DAY.
ENTRY      the first 1-minute candle from 09:15 to 09:30 whose LOW touches the level (a gap down through the level = entry at 09:15).  Option price = close of the entry-minute option candle.
EXIT       time exit 09:30 or 10:00 (a trade entered at/after that minute is skipped for that exit)  x  stop-loss 0 / 10 / 20 / 30 % of the premium (0 = none)
           x  target 10 / 20 / 30 / 40 / 60 % or 0 = NO target.   = 2 x 4 x 6 = 48 variants per strategy.
           Fills: stop / target = first 1-minute low / high touching the level, a gap through it fills at that candle's open, stop and target in the same minute = STOP.
CAPITAL    at most Rs 60,000 per trade (lots = 60000 // (premium x lot size)).  Charges and slippage are not included.  Lot sizes are today's values.

RESULTS in wru5_results/ (same files as all8_results/): summary.csv, top_by_*.csv, best_per_strategy.csv, trades_summary.csv, all_trades/<strategy>.csv.gz (EVERY variant), REPORT.txt, PROGRESS.txt.
  In summary.csv  tp = 0 means "no target".
"""
import os, sys
os.environ.setdefault("A8_OUT", "wru5_results"); os.environ.setdefault("A8_START", "2023-01-01"); os.environ.setdefault("A8_END", "2026-10-31")
os.environ.setdefault("A8_ENTRY_LAST", "09:30"); os.environ.setdefault("A8_TRADES_ALL", "1")
os.environ.setdefault("A8_SLS", "10,20,30,0"); os.environ.setdefault("A8_TPS", "10,20,30,40,60,0")
os.environ.setdefault("A8_PRE_TOL", "0.10")
import numpy as np, pandas as pd
from datetime import date, timedelta
import all8_backtest as A
from bpb_fno_backtest import Dhan, Stop, Fatal, stream, load_master
C, B, T = A.C, A.B, A.T

STRATS = ["RLOW_1H_WRU", "RLOW_4H_WRU", "WRU_RES_LINE", "WRU_ROLL5_HIGH", "WRU_SUP_LINE", "WRU_ROLL5_LOW", "WRU_PIVOT_HIGH", "WRU_PIVOT_LOW"]
W_LOOKBACK = int(os.environ.get("W_LOOKBACK") or 10)          # rolling-low window, in candles of the chart (1H / 4H)
W_WINDOW = int(os.environ.get("W_WINDOW") or 20)              # how many candles back the closing-below candle may be
ROLL_DAYS = int(os.environ.get("W_ROLL_DAYS") or 5)           # rolling high / low of daily candles
PIV_K = int(os.environ.get("W_PIVOT_K") or 2)                 # candles on each side of a pivot
PIV_AGE = int(os.environ.get("W_PIVOT_AGE") or 60)            # a pivot / line older than this many days is not used
PRE_TOL = float(os.environ.get("A8_PRE_TOL") or 0.10)         # the entry day's first hour must start within 10 % above the level and touch it
TEXITS = ["09:30", "10:00"]


def configure():
    """Point the all8 engine at THIS strategy list / exit grid (its functions read these module values when they are called)."""
    A.STRATS[:] = STRATS
    A.ENTRY_TYPE.clear(); A.ENTRY_TYPE.update({s: "ALL" for s in STRATS})
    A.TEXITS[:] = TEXITS; A.EXITS[:] = TEXITS
    A.VARS[:] = [(ex, sl, tp) for ex in A.EXITS for sl in A.SLS for tp in A.TPS]
    A.strategies_for = lambda source, typ, green, red, up, lo: [source] if (typ == "ALL" and source in STRATS) else []


# ------------------------------------------------------------------ signals (pure numpy, tested offline)
def is_wru(O, H, L, C_, n):
    up, lo = H[n] - max(O[n], C_[n]), min(O[n], C_[n]) - L[n]
    return bool(C_[n] < O[n] and up > lo)


def pivots(X, k, high):
    """Indices p of pivot highs (high=True) / lows: the candle is the extreme of k candles on each side (left side may tie, right side strict).  A pivot is only KNOWN from candle p + k + 1."""
    out = []
    for p in range(k, len(X) - k):
        if high and X[p] >= X[p - k:p].max() and X[p] > X[p + 1:p + k + 1].max(): out.append(p)
        if (not high) and X[p] <= X[p - k:p].min() and X[p] < X[p + 1:p + k + 1].min(): out.append(p)
    return out


def rlow_signals(O, H, L, C_):
    """Rolling-LOW rule on one chart -> [(signal candle n, line)]  (WRU candles only).  Same rule as combo shape_signals(long=False)."""
    return [(n, lvl) for n, lvl, i in C.shape_signals(O, H, L, C_, False, W_LOOKBACK, W_WINDOW) if is_wru(O, H, L, C_, n)]


def daily_signals(O, H, L, C_):
    """WRU daily candles above a level -> {strategy: [(signal day n, level on the entry day n+1)]}."""
    N = len(C_); out = {s: [] for s in STRATS[2:]}
    ph, pl = pivots(H, PIV_K, True), pivots(L, PIV_K, False)
    for n in range(max(ROLL_DAYS, 2 * PIV_K + 2), N - 1):
        if not is_wru(O, H, L, C_, n): continue
        def above(v): return H[n] > v and C_[n] > v
        hi5, lo5 = H[n - ROLL_DAYS:n].max(), L[n - ROLL_DAYS:n].min()
        if above(hi5): out["WRU_ROLL5_HIGH"].append((n, hi5))
        if above(lo5): out["WRU_ROLL5_LOW"].append((n, lo5))
        for name, pv, X, res in (("WRU_RES_LINE", ph, H, True), ("WRU_SUP_LINE", pl, L, False)):
            conf = [p for p in pv if p + PIV_K <= n - 1]
            if len(conf) < 2: continue
            p1, p2 = conf[-2], conf[-1]
            if p2 - p1 < 3 or n - p2 > PIV_AGE: continue
            if (res and not X[p2] < X[p1]) or ((not res) and not X[p2] > X[p1]): continue          # resistance falls, support rises
            sl = (X[p2] - X[p1]) / (p2 - p1); v = lambda t: X[p1] + sl * (t - p1)
            if not above(v(n)): continue
            if res and C_[n - 1] > v(n - 1): continue                                              # the FIRST close above the resistance line
            out[name].append((n, v(n + 1)))
        for name, pv, X, hi in (("WRU_PIVOT_HIGH", ph, H, True), ("WRU_PIVOT_LOW", pl, L, False)):
            conf = [p for p in pv if p + PIV_K <= n - 1]
            if not conf: continue
            p = conf[-1]; lvl = X[p]
            if n - p > PIV_AGE or not above(lvl): continue
            if hi and (C_[p + 1:n] > lvl).any(): continue                                          # the FIRST close above the pivot high
            out[name].append((n, lvl))
    return out


def candidate_rows(stock, hourly, t0, t1, pre_tol=PRE_TOL):
    """One stock: raw 60-minute candles (09:15..15:15) -> candidate entry-day rows for all 8 strategies."""
    if len(hourly) < 60: return []
    dkey = np.array(hourly.index.strftime("%Y-%m-%d"))
    g = hourly.groupby(dkey)
    dd = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last()})
    first = g.first()                                                         # first hourly candle of every day (09:15-10:15)
    udays = list(dd.index); nxt = {d: udays[i + 1] for i, d in enumerate(udays[:-1])}
    rows = []

    def add(strat, lvl, sig_day, sig_idx, O, H, L, C_, e):
        if e is None or not (str(t0.date()) <= e <= str(t1.date())) or e not in first.index: return
        f = first.loc[e]
        if not (f.l <= lvl and f.o <= lvl * (1 + pre_tol)): return                # the first hour must start near the level and reach it
        n = sig_idx
        up, lo = H[n] - max(O[n], C_[n]), min(O[n], C_[n]) - L[n]
        rows.append(dict(source=strat, stock=stock, direction="SHORT", ref=round(float(lvl), 2), signal_date=sig_day, date=e, yahoo_open=float(f.o),
                         breakout_date=sig_day, line=round(float(lvl), 2), green=0, red=1, upper_longer=int(up > lo), lower_longer=int(lo > up)))

    for tf, name in (("1H", "RLOW_1H_WRU"), ("4H", "RLOW_4H_WRU")):
        bars = hourly if tf == "1H" else T.to_4h(hourly)
        if len(bars) < 60: continue
        O, H, L, C_ = (bars[c].values.astype(float) for c in ("o", "h", "l", "c")); day = np.array(bars.index.strftime("%Y-%m-%d"))
        for n, lvl in rlow_signals(O, H, L, C_):
            same = day == day[n]; same[:n + 1] = False
            if same.any() and L[same].min() <= lvl: continue                    # the line was already crossed later on the signal day
            add(name, lvl, day[n], n, O, H, L, C_, nxt.get(day[n]))
    O, H, L, C_ = (dd[c].values.astype(float) for c in ("o", "h", "l", "c"))
    for name, sigs in daily_signals(O, H, L, C_).items():
        for n, lvl in sigs: add(name, lvl, udays[n], n, O, H, L, C_, nxt.get(udays[n]))
    return rows


# ------------------------------------------------------------------ step 1: hourly candles -> candidate entry days (resumable, one file per stock)
COLS = ["source", "stock", "direction", "ref", "signal_date", "date", "yahoo_open", "breakout_date", "line", "green", "red", "upper_longer", "lower_longer"]


def build_candidates(dh, mst):
    t0, t1 = pd.Timestamp(A.START), pd.Timestamp(A.END)
    d0 = (t0 - pd.Timedelta(days=T.WARMUP_DAYS)).date(); d1 = min(t1.date(), date.today()) + timedelta(days=1)
    pdir = f"{A.OUT}/wru_candidates"; os.makedirs(pdir, exist_ok=True)
    stocks = [s for s in A.UNIVERSE if s in mst]
    miss = [s for s in A.UNIVERSE if s not in mst]
    if miss: print(f"not in Dhan stock-option list - skipped: {miss}", flush=True)
    path = lambda s: f"{pdir}/{s}_{A.START}_{A.END}.csv"
    todo = [s for s in stocks if not os.path.exists(path(s))]
    print(f"Hourly candles: {len(todo)} stocks to fetch ({len(stocks) - len(todo)} already done), {d0} .. {d1}", flush=True)

    def work(s):
        h = T.hourly_range(dh, mst[s][0], d0, d1)
        if h is None: return None
        if h.empty: return [], 0
        mm = h.index.hour * 60 + h.index.minute
        h = h[(mm >= 9 * 60 + 15) & (mm <= 15 * 60 + 15)]
        return candidate_rows(s, h, t0, t1), len(h)

    fails = [0]

    def handle(s, res):
        if res is None:
            fails[0] += 1; print(f"hourly candles {s}: FAILED (retried on the next run), calls {dh.n}", flush=True); return
        rows, nb = res
        pd.DataFrame(rows, columns=COLS).to_csv(path(s), index=False); A.checkpoint()
        print(f"hourly candles {s}: {nb} candles, {len(rows)} candidate days, calls {dh.n}", flush=True)

    A.FLUSHER[0] = None
    stream(todo, work, handle)
    if fails[0]: raise Stop(f"{fails[0]} stock(s) failed to download - run again to retry them")
    cand = pd.concat([pd.read_csv(path(s)) for s in stocks], ignore_index=True) if stocks else pd.DataFrame(columns=COLS)
    print(f"WRU candidates: {len(cand)} entry days ({', '.join(f'{k} = {v}' for k, v in cand.groupby('source').size().items())})", flush=True)
    return cand


# ------------------------------------------------------------------ modes
def check():
    C.check()
    dh = Dhan(); mst = load_master(); d1 = date.today(); d0 = d1 - timedelta(days=10)
    h = T.eq_hourly(dh, mst["RELIANCE"][0], d0, d1)
    print("Hourly call:", "no data" if h is None or h.empty else f"{len(h)} candles")
    B.print_stats(dh)


def run():
    configure(); os.makedirs(A.OUT, exist_ok=True); st = A.load_state()
    dh = Dhan(); mst = load_master()
    try:
        cp = f"{A.OUT}/candidates_{A.START}_{A.END}.csv"
        if os.path.exists(cp): cand = pd.read_csv(cp)
        else:
            cand = build_candidates(dh, mst)
            if cand.empty: print("No candidate days in this range."); return
            cand.to_csv(cp, index=False)
        print(f"Candidate days {A.START}..{A.END}: {len(cand)} ({', '.join(f'{k} = {v}' for k, v in cand.groupby('source').size().items())})", flush=True)
        ev = A.step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= A.START) & (ev["date"] <= A.END)] if len(ev) else ev
        print(f"Entries (09:15-{A.ENTRY_LAST}): {len(ev)}" + (f"  ({', '.join(f'{k} = {v}' for k, v in ev.groupby('strategy').size().items())})" if len(ev) else ""), flush=True)
        if len(ev): A.step_options(dh, ev, mst, st)
        print("ALL STEPS FINISHED", flush=True)
    except Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        B.print_stats(dh); A.progress(); A.summary(); A.checkpoint(True)


if __name__ == "__main__":
    configure(); mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": check()
        elif mode == "run": run()
        elif mode in ("summary", "range"): A.summary()
        else: sys.exit("use: python wru5_backtest.py check | run | summary")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
