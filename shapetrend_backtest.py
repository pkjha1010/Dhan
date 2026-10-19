"""shapetrend_backtest.py - RE-BACKTEST of 5 strategies, each with 5 TREND FILTERS (+ the unfiltered baseline), all F&O stock options (Dhan 1-minute data).

  python shapetrend_backtest.py check     test Dhan access
  python shapetrend_backtest.py run       full backtest (resumable - run again after a polite stop)
  python shapetrend_backtest.py summary   rebuild every result file from the saved option data (no API calls)

BASE STRATEGIES (entry = buy ATM option of the nearest monthly expiry, strike locked at entry - the same all8 engine / exit logic as wru5_backtest.py, imported, not copied)
  FROM wru5_backtest.py / shape_live_plan.py (fixed direction):
  RLOW_1H_WRU    SHORT (PUT)  exactly as in wru5_backtest.py : 1-hour rolling-low signal, WRU candle = last candle of the day before
  WRU_ROLL5_LOW  SHORT (PUT)  exactly as in wru5_backtest.py : WRU daily candle closing above the 5-day rolling low; entry when price falls to it
  WRL            LONG  (CALL) shape_live_plan.py : SHAPECMP daily signal (10-day high/low, 20-day window), signal candle RED + LOWER wick longer; entry when price rises to the line
  WRU            SHORT (PUT)  shape_live_plan.py : SHAPECMP daily signal, signal candle RED + UPPER wick longer; entry when price falls to the line
  BPB            SHORT (PUT)  shape_live_plan.py : breakout -> pullback -> re-cross of the 10-day low (state machine of breakout_armed()), entry any time the day
  FROM all8_backtest.py (run in BOTH directions, reported separately: <name>_L = LONG / buy CALL, <name>_S = SHORT / buy PUT):
  WGU            SHAPECMP daily signal, signal candle GREEN + UPPER wick longer     (all8: WICK_GREEN_UPPER)
  WGL            SHAPECMP daily signal, signal candle GREEN + LOWER wick longer     (all8: WICK_GREEN_LOWER)
  TL_1H, TL_4H   break -> retest -> re-break of a trendline on the 1-hour / 4-hour chart   (all8: TRENDLINE_1H / TRENDLINE_4H, rows made by all8's own tl_rows_fullday)
  RC4C           SHAPECMP signal (no candle rule) entered with the RECROSS_0920_4C rule   (all8: SHAPECMP_RECROSS_4C)
TREND FILTERS (trend_filters.py, daily candles at the close of the signal day, direction aware: LONG needs an up-trend, SHORT a down-trend)
  MA50  MA2050  ROC10  ADXDI  STRUCT        + NOF = no filter (baseline, to see what each filter adds)
STRATEGY NAME in every result file = <BASE>__<FILTER>, e.g. WRL__ADXDI, BPB__NOF, TL_1H_L__MA50.  summary.csv is also written as shapetrend_summary_by_trend.csv (extra columns base, trend).
EXITS   time exit 09:30 / 10:00 / 15:30 (ST_EXITS can add 12:00 and UNTIL_HIT = hold until stop / target / expiry)  x  stop-loss list  x  target list (0 = none).  Live settings: WRL  exit 10:00, SL 0, TP 60 | WRU  exit 09:30, SL 20, TP 400 | BPB exit 15:30, SL 0, TP 60.
        Entry window is 09:15-15:20 for all; a trade entered at/after an exit minute is skipped for that exit, so the live windows (WRU 09:15-09:29, WRL 09:15-09:59) are inside the grid.
Results go to shapetrend_results/ (own folder - nothing of wru5_results/ is touched).
"""
import os, sys, hashlib
os.environ.setdefault("A8_OUT", "shapetrend_results"); os.environ.setdefault("A8_START", "2023-01-01"); os.environ.setdefault("A8_END", "2026-10-31")
os.environ.setdefault("A8_ENTRY_LAST", "15:20"); os.environ.setdefault("A8_TRADES_ALL", "0")
os.environ.setdefault("A8_SLS", "0,10,20,30"); os.environ.setdefault("A8_TPS", "10,20,30,40,60,400,0")
os.environ.setdefault("A8_PRE_TOL", "0.10")
import numpy as np, pandas as pd
from datetime import date, timedelta
import wru5_backtest as W
import trend_filters as TF
A, C, B, T = W.A, W.C, W.B, W.T
Dhan, Stop, Fatal, stream, load_master = W.Dhan, W.Stop, W.Fatal, W.stream, W.load_master

FIXED = {"RLOW_1H_WRU": "SHORT", "WRU_ROLL5_LOW": "SHORT", "WRL": "LONG", "WRU": "SHORT", "BPB": "SHORT"}      # one direction (as in the live plan / wru5)
BOTH = ["WGU", "WGL", "TL_1H", "TL_4H", "RC4C"]                                                                 # from all8: both directions, one strategy name per direction
ALL_BASES = list(FIXED) + BOTH
_pick = lambda env, allv: [x for x in (v.strip() for v in (os.environ.get(env) or "").replace(" ", ",").split(",")) if x in allv] or list(allv)
BASES = _pick("ST_BASES", ALL_BASES)
TREND_SET = (["NOF"] if (os.environ.get("ST_BASELINE") or "1") != "0" else []) + _pick("ST_TRENDS", TF.TRENDS)
LABELS, DIRECTION, TYP = [], {}, {}                    # label = strategy name without the filter, e.g. WRL, WGU_L, TL_4H_S
for _b in BASES:
    for _lab, _d in (((_b, FIXED[_b]),) if _b in FIXED else ((_b + "_L", "LONG"), (_b + "_S", "SHORT"))):
        LABELS.append(_lab); DIRECTION[_lab] = _d; TYP[_lab] = "RECROSS_0920_4C" if _b == "RC4C" else "ALL"
STRATS = [f"{l}__{t}" for l in LABELS for t in TREND_SET]
_EX = [x.strip() for x in (os.environ.get("ST_EXITS") or "09:30,10:00,15:30").replace(" ", ",").split(",") if x.strip()]
TEXITS = [x for x in ("09:30", "10:00", "12:00", "15:30") if x in _EX] or ["09:30", "10:00", "15:30"]
EXITS_ALL = TEXITS + (["UNTIL_HIT"] if "UNTIL_HIT" in _EX else [])
PRE_TOL = float(os.environ.get("A8_PRE_TOL") or 0.10)
S_LOOKBACK = int(os.environ.get("ST_SHAPE_LOOKBACK") or 10)       # SHAPECMP: 10-day high / low, same as shape_live_plan.py
S_WINDOW = int(os.environ.get("ST_SHAPE_WINDOW") or 20)           # SHAPECMP: closing-beyond candle at most 20 candles back
BPB_LOOKBACK = int(os.environ.get("BPB_LOOKBACK") or 10)
TAG = hashlib.md5(",".join(STRATS).encode()).hexdigest()[:6]      # candidate files are specific to the chosen strategies / filters
WARM_DAYS = max(int(getattr(T, "WARMUP_DAYS", 0) or 0), 150)      # SMA50 / ADX need ~100 trading days of history


def configure():
    A.STRATS[:] = STRATS
    A.ENTRY_TYPE.clear(); A.ENTRY_TYPE.update({f"{l}__{t}": TYP[l] for l in LABELS for t in TREND_SET})
    A.TEXITS[:] = TEXITS; A.EXITS[:] = EXITS_ALL
    A.VARS[:] = [(ex, sl, tp) for ex in A.EXITS for sl in A.SLS for tp in A.TPS]
    src_typ = {f"{l}__{t}": TYP[l] for l in LABELS for t in TREND_SET}
    A.strategies_for = lambda source, typ, green, red, up, lo: [source] if src_typ.get(source) == typ else []     # the engine returns every entry type; keep the one the strategy uses


def wicks(O, H, L, C_, n):
    return H[n] - max(O[n], C_[n]), min(O[n], C_[n]) - L[n]


def candidate_rows(stock, hourly, t0, t1, pre_tol=PRE_TOL):
    """One stock: raw 60-minute candles (09:15..15:15) -> candidate entry-day rows (one row per base strategy x trend filter that passes)."""
    if len(hourly) < 60: return []
    dkey = np.array(hourly.index.strftime("%Y-%m-%d"))
    g = hourly.groupby(dkey)
    dd = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last()})
    first = g.first()
    udays = list(dd.index); nxt = {d: udays[i + 1] for i, d in enumerate(udays[:-1])}; didx = {d: i for i, d in enumerate(udays)}
    dO, dH, dL, dC = (dd[c].values.astype(float) for c in ("o", "h", "l", "c"))
    flags = TF.trend_flags(dO, dH, dL, dC)
    lo_d, hi_d = str(t0.date()), str(t1.date()); rows = []

    def fan(label, row):                                                        # one row per trend filter that passes (+ NOF)
        di = didx.get(row["signal_date"])
        if di is None: return
        k = 0 if row["direction"] == "LONG" else 1
        for tn in TREND_SET:
            if tn != "NOF" and not flags[tn][k][di]: continue
            rows.append(dict(row, source=f"{label}__{tn}"))

    def emit(label, lvl, sig_day, up, lo, e, first_check=True, green=0):
        direction = DIRECTION[label]
        if e is None or not (lo_d <= e <= hi_d) or e not in first.index: return
        f = first.loc[e]
        if first_check:                                                         # the first hour must start near the level and reach it
            if direction == "SHORT" and not (f.l <= lvl and f.o <= lvl * (1 + pre_tol)): return
            if direction == "LONG" and not (f.h >= lvl and f.o >= lvl * (1 - pre_tol)): return
        fan(label, dict(stock=stock, direction=direction, ref=round(float(lvl), 2), signal_date=sig_day, date=e, yahoo_open=float(f.o),
                        breakout_date=sig_day, line=round(float(lvl), 2), green=int(green), red=int(not green), upper_longer=int(up > lo), lower_longer=int(lo > up)))

    if "RLOW_1H_WRU" in BASES:                                                  # 1-hour rolling low, WRU candle = last hourly candle of the day before the entry day
        O, H, L, C_ = (hourly[c].values.astype(float) for c in ("o", "h", "l", "c")); day = dkey
        for n, lvl in W.rlow_signals(O, H, L, C_):
            if n + 1 < len(day) and day[n + 1] == day[n]: continue
            up, lo = wicks(O, H, L, C_, n); emit("RLOW_1H_WRU", lvl, day[n], up, lo, nxt.get(day[n]))
    if "WRU_ROLL5_LOW" in BASES:
        for n, lvl in W.daily_signals(dO, dH, dL, dC)["WRU_ROLL5_LOW"]:
            up, lo = wicks(dO, dH, dL, dC, n); emit("WRU_ROLL5_LOW", lvl, udays[n], up, lo, nxt.get(udays[n]))
    shape_bases = [b for b in ("WRL", "WRU", "WGU", "WGL", "RC4C") if b in BASES]
    if shape_bases:                                                             # SHAPECMP daily signals (live-plan rule); candle rules per strategy
        for long in (True, False):
            for n, lvl, i in C.shape_signals(dO, dH, dL, dC, long, S_LOOKBACK, S_WINDOW):
                up, lo = wicks(dO, dH, dL, dC, n); red, green = dC[n] < dO[n], dC[n] > dO[n]
                for b in shape_bases:
                    if b == "WRL" and long and red and lo > up and dC[n] < lvl: lab = "WRL"                 # live plan: LONG only
                    elif b == "WRU" and (not long) and red and up > lo and dC[n] > lvl: lab = "WRU"        # live plan: SHORT only
                    elif b == "WGU" and green and up > lo: lab = "WGU_" + ("L" if long else "S")
                    elif b == "WGL" and green and lo > up: lab = "WGL_" + ("L" if long else "S")
                    elif b == "RC4C": lab = "RC4C_" + ("L" if long else "S")
                    else: continue
                    emit(lab, lvl, udays[n], up, lo, nxt.get(udays[n]), green=green)
    for tf, b in (("1H", "TL_1H"), ("4H", "TL_4H")):                            # trendlines: all8's own row builder (both directions)
        if b in BASES:
            for r in A.tl_rows_fullday(stock, hourly, tf, t0, t1, pre_tol): fan(f"{b}_{r['direction'][0]}", r)
    if "BPB" in BASES:                                                          # breakout -> pullback -> re-cross of the 10-day low; entry day = the day price reaches the level
        for i, line, level in TF.bpb_entries(dO, dH, dL, dC, False, BPB_LOOKBACK):
            up, lo = wicks(dO, dH, dL, dC, i - 1); emit("BPB", level, udays[i - 1], up, lo, udays[i], first_check=False)
    return rows


COLS = ["source", "stock", "direction", "ref", "signal_date", "date", "yahoo_open", "breakout_date", "line", "green", "red", "upper_longer", "lower_longer"]


def build_candidates(dh, mst):
    t0, t1 = pd.Timestamp(A.START), pd.Timestamp(A.END)
    d0 = (t0 - pd.Timedelta(days=WARM_DAYS)).date(); d1 = min(t1.date(), date.today()) + timedelta(days=1)
    pdir = f"{A.OUT}/st_candidates"; os.makedirs(pdir, exist_ok=True)
    stocks = [s for s in A.UNIVERSE if s in mst]
    miss = [s for s in A.UNIVERSE if s not in mst]
    if miss: print(f"not in Dhan stock-option list - skipped: {miss}", flush=True)
    path = lambda s: f"{pdir}/{s}_{TAG}_{A.START}_{A.END}.csv"
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
        print(f"hourly candles {s}: {nb} candles, {len(rows)} candidate rows, calls {dh.n}", flush=True)

    A.FLUSHER[0] = None
    stream(todo, work, handle)
    if fails[0]: raise Stop(f"{fails[0]} stock(s) failed to download - run again to retry them")
    cand = pd.concat([pd.read_csv(path(s)) for s in stocks], ignore_index=True) if stocks else pd.DataFrame(columns=COLS)
    print(f"Candidates: {len(cand)} rows ({', '.join(f'{k} = {v}' for k, v in cand.groupby('source').size().items())})", flush=True)
    return cand


def split_summary():
    """summary.csv -> shapetrend_summary_by_trend.csv with extra columns base / trend (the strategy name is <BASE>__<FILTER>)."""
    try:
        p = f"{A.OUT}/summary.csv"
        if not os.path.exists(p): return
        df = pd.read_csv(p); col = next((c for c in ("strategy", "source") if c in df.columns), None)
        if col is None: return
        parts = df[col].astype(str).str.split("__", n=1, expand=True)
        df.insert(0, "trend", parts[1] if parts.shape[1] > 1 else ""); df.insert(0, "base", parts[0])
        df.to_csv(f"{A.OUT}/shapetrend_summary_by_trend.csv", index=False)
        print(f"wrote {A.OUT}/shapetrend_summary_by_trend.csv ({len(df)} rows)", flush=True)
    except Exception as e:
        print(f"(summary split skipped: {e!r})", flush=True)


def check():
    W.check()


def run():
    configure(); os.makedirs(A.OUT, exist_ok=True); st = A.load_state()
    print(f"Strategies ({len(STRATS)}): {LABELS} x filters {TREND_SET}; exits {EXITS_ALL}; SL {A.SLS}; TP {A.TPS}", flush=True)
    dh = Dhan(); mst = load_master()
    try:
        cp = f"{A.OUT}/candidates_{TAG}_{A.START}_{A.END}.csv"
        if os.path.exists(cp): cand = pd.read_csv(cp)
        else:
            cand = build_candidates(dh, mst)
            if cand.empty: print("No candidate days in this range."); return
            cand.to_csv(cp, index=False)
        print(f"Candidate rows {A.START}..{A.END}: {len(cand)} ({', '.join(f'{k} = {v}' for k, v in cand.groupby('source').size().items())})", flush=True)
        ev = A.step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= A.START) & (ev["date"] <= A.END)] if len(ev) else ev
        print(f"Entries (09:15-{A.ENTRY_LAST}): {len(ev)}" + (f"  ({', '.join(f'{k} = {v}' for k, v in ev.groupby('strategy').size().items())})" if len(ev) else ""), flush=True)
        if len(ev): A.step_options(dh, ev, mst, st)
        print("ALL STEPS FINISHED", flush=True)
    except Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        B.print_stats(dh); A.progress(); A.summary(); split_summary(); A.checkpoint(True)


if __name__ == "__main__":
    configure(); mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": check()
        elif mode == "run": run()
        elif mode in ("summary", "range"): A.summary(); split_summary()
        else: sys.exit("use: python shapetrend_backtest.py check | run | summary")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
