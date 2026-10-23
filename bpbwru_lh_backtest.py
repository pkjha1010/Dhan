"""bpbwru_lh_backtest.py - backtest of BPB SHORT and WRU SHORT with a PREVIOUS-DAY AFTERNOON filter, all F&O stock options (Dhan 1-minute data).

  python bpbwru_lh_backtest.py check     test Dhan access
  python bpbwru_lh_backtest.py run       full backtest (resumable - run again after a polite stop)
  python bpbwru_lh_backtest.py summary   rebuild every result file from the saved option data (no API calls)

STRATEGIES (both SHORT = buy PUT, nearest monthly expiry, strike locked at entry; same all8 engine / exit logic, imported)
  BPB   breakout -> pullback -> re-cross of the 10-day low (breakout_armed() of shape_live_plan.py)
  WRU   SHAPECMP daily signal (10-day low, 20-day window), signal candle RED + UPPER wick longer, closed above the line
ENTRY     first 1-minute candle from 09:15 to 10:00 that touches the level.
STRIKE    ATM first.  If the ATM series has no candle at the entry minute: ITM-1, then ITM-2 (a put: the 1st / 2nd strike ABOVE the spot).  strike_usage.csv shows how often each was used.
EXIT      time exit 09:20 / 09:30 / 10:00 (a trade entered at/after that minute is skipped for that exit)  x  stop-loss 0,10,20,40,60 (0 = none)  x  target 20,40,60,80,120 or 0 = none.
NEW: PREVIOUS-DAY AFTERNOON FILTER (the day before the entry day, from 1-minute stock candles)
  H = last half hour : price 15:30 (last close) vs price 15:00 (open of the 15:00 candle)     U = bullish (15:30 above 15:00)   D = bearish
  M = 13:00 - 15:00  : price 15:00 vs price 13:00                                              U = bullish                      D = bearish
  4 variants:  LHU_MU  last half hour bullish + 13:00-15:00 bullish      LHU_MD  bullish + bearish
               LHD_MU  last half hour bearish + 13:00-15:00 bullish      LHD_MD  bearish + bearish
  + ALL = no afternoon filter (baseline, to compare).   Days with incomplete minute data are only in ALL.
STRATEGY NAME in every result file = <BPB|WRU>_<variant>, e.g. BPB_LHU_MD, WRU_ALL.
Results go to bpbwru_lh_results/ : summary.csv, top_by_*.csv, best_per_strategy.csv, trades_summary.csv, all_trades/<strategy>.csv.gz, REPORT.txt, PROGRESS.txt, strike_usage.csv, lh_flags/ (the daily flags).
"""
import os, sys
from collections import Counter
os.environ.setdefault("A8_OUT", "bpbwru_lh_results"); os.environ.setdefault("A8_START", "2023-01-01"); os.environ.setdefault("A8_END", "2026-10-31")
os.environ.setdefault("A8_ENTRY_LAST", "10:00"); os.environ.setdefault("A8_TRADES_ALL", "1")
os.environ.setdefault("A8_SLS", "0,10,20,40,60"); os.environ.setdefault("A8_TPS", "20,40,60,80,120,0")
os.environ.setdefault("A8_PRE_TOL", "0.10")
import numpy as np, pandas as pd
from datetime import date, timedelta
import all8_backtest as A
import trend_filters as TF
import lh_logic as LH
from bpb_fno_backtest import Dhan, Stop, Fatal, stream, load_master
C, B, T = A.C, A.B, A.T

_pick = lambda env, allv, default=None: [x for x in (v.strip() for v in (os.environ.get(env) or default or "").replace(" ", ",").split(",")) if x in allv] or list(allv)
BASES = _pick("LH_BASES", ["BPB", "WRU"])
VARIANTS = {"LHU_MU": (1, 1), "LHU_MD": (1, -1), "LHD_MU": (-1, 1), "LHD_MD": (-1, -1)}      # name: (last half hour, 13:00-15:00)  +1 bullish / -1 bearish
VSEL = _pick("LH_VARIANTS", list(VARIANTS))
BASELINE = (os.environ.get("LH_BASELINE") or "1") != "0"
STRATS = [f"{b}_{v}" for b in BASES for v in (["ALL"] if BASELINE else []) + VSEL]
_ex = [x.strip() for x in (os.environ.get("LH_EXITS") or "09:20,09:30,10:00").replace(" ", ",").split(",") if x.strip()]
TEXITS = [x for x in _ex if len(x) == 5 and x[2] == ":"] or ["09:20", "09:30", "10:00"]
S_LOOKBACK = int(os.environ.get("LH_SHAPE_LOOKBACK") or 10); S_WINDOW = int(os.environ.get("LH_SHAPE_WINDOW") or 20); BPB_LOOKBACK = int(os.environ.get("BPB_LOOKBACK") or 10)
PRE_TOL = float(os.environ.get("A8_PRE_TOL") or 0.10)
WARM_DAYS = max(int(getattr(T, "WARMUP_DAYS", 0) or 0), 90)
COLS = ["source", "stock", "direction", "ref", "signal_date", "date", "yahoo_open", "breakout_date", "line", "green", "red", "upper_longer", "lower_longer"]


def configure():
    A.STRATS[:] = STRATS
    A.ENTRY_TYPE.clear(); A.ENTRY_TYPE.update({s: "ALL" for s in STRATS})
    A.TEXITS[:] = TEXITS; A.EXITS[:] = TEXITS
    A.VARS[:] = [(ex, sl, tp) for ex in A.EXITS for sl in A.SLS for tp in A.TPS]
    A.strategies_for = lambda source, typ, green, red, up, lo: [source] if (typ == "ALL" and source in STRATS) else []
    A.work_group = work_group                                                       # ATM -> ITM-1 -> ITM-2 strike fallback


# ------------------------------------------------------------------ step 1: candidate entry days of BPB and WRU (from hourly candles)
def candidate_rows(stock, hourly, t0, t1, pre_tol=PRE_TOL):
    if len(hourly) < 60: return []
    dkey = np.array(hourly.index.strftime("%Y-%m-%d")); g = hourly.groupby(dkey)
    dd = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last()}); first = g.first()
    udays = list(dd.index); nxt = {d: udays[i + 1] for i, d in enumerate(udays[:-1])}
    O, H, L, C_ = (dd[c].values.astype(float) for c in ("o", "h", "l", "c")); lo_d, hi_d = str(t0.date()), str(t1.date()); rows = []

    def add(src, lvl, n, e, first_check):
        if e is None or not (lo_d <= e <= hi_d) or e not in first.index: return
        f = first.loc[e]
        if first_check and not (f.l <= lvl and f.o <= lvl * (1 + pre_tol)): return          # the first hour must start near the level and reach it
        up, lo = H[n] - max(O[n], C_[n]), min(O[n], C_[n]) - L[n]
        rows.append(dict(source=src, stock=stock, direction="SHORT", ref=round(float(lvl), 2), signal_date=udays[n], date=e, yahoo_open=float(f.o), breakout_date=udays[n],
                         line=round(float(lvl), 2), green=0, red=1, upper_longer=int(up > lo), lower_longer=int(lo > up)))

    if "WRU" in BASES:
        for n, lvl, i in C.shape_signals(O, H, L, C_, False, S_LOOKBACK, S_WINDOW):
            up, lo = H[n] - max(O[n], C_[n]), min(O[n], C_[n]) - L[n]
            if C_[n] < O[n] and up > lo and C_[n] > lvl: add("WRU", lvl, n, nxt.get(udays[n]), True)
    if "BPB" in BASES:
        for i, line, level in TF.bpb_entries(O, H, L, C_, False, BPB_LOOKBACK): add("BPB", level, i - 1, udays[i], False)
    return rows


def build_candidates(dh, mst):
    t0, t1 = pd.Timestamp(A.START), pd.Timestamp(A.END)
    d0 = (t0 - pd.Timedelta(days=WARM_DAYS)).date(); d1 = min(t1.date(), date.today()) + timedelta(days=1)
    pdir = f"{A.OUT}/lh_candidates"; os.makedirs(pdir, exist_ok=True)
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
        pd.DataFrame(rows, columns=COLS).drop_duplicates(["source", "stock", "date", "ref"]).to_csv(path(s), index=False); A.checkpoint()
        print(f"hourly candles {s}: {nb} candles, {len(rows)} candidate days, calls {dh.n}", flush=True)

    A.FLUSHER[0] = None
    stream(todo, work, handle)
    if fails[0]: raise Stop(f"{fails[0]} stock(s) failed to download - run again to retry them")
    return pd.concat([pd.read_csv(path(s)) for s in stocks], ignore_index=True) if stocks else pd.DataFrame(columns=COLS)


# ------------------------------------------------------------------ step 2: previous-day afternoon flags (1-minute stock candles of the signal days)
def build_flags(dh, mst, base):
    fdir = f"{A.OUT}/lh_flags"; os.makedirs(fdir, exist_ok=True)
    path = lambda s: f"{fdir}/{s}_{A.START}_{A.END}.csv"
    sig = base.groupby("stock").signal_date.unique()
    stocks = [s for s in sig.index if s in mst]
    todo = [s for s in stocks if not os.path.exists(path(s))]
    print(f"Previous-day afternoon candles: {len(todo)} stocks to fetch ({len(stocks) - len(todo)} already done)", flush=True)

    def work(s):
        ds = sorted(date.fromisoformat(x) for x in sig[s]); rows = {}
        for d0, d1 in B.clusters(ds, B.EQ_SPAN, B.EQ_GAP):
            u_all = B.eq_minute(dh, mst[s][0], d0, d1)
            if u_all is None: return None
            days = {k: v for k, v in u_all.groupby(u_all.index.date)} if len(u_all) else {}
            for d in ds:
                if d0 <= d <= d1: rows[d] = LH.day_flags(days.get(d))
        return [dict(stock=s, signal_date=str(d), **rows.get(d, LH.day_flags(None))) for d in ds]

    fails = [0]

    def handle(s, res):
        if res is None:
            fails[0] += 1; print(f"afternoon candles {s}: FAILED (retried on the next run), calls {dh.n}", flush=True); return
        pd.DataFrame(res).to_csv(path(s), index=False); A.checkpoint()
        print(f"afternoon candles {s}: {len(res)} signal days, {sum(r['ok'] for r in res)} with full data, calls {dh.n}", flush=True)

    A.FLUSHER[0] = None
    stream(todo, work, handle)
    if fails[0]: raise Stop(f"{fails[0]} stock(s) failed to download - run again to retry them")
    fs = [pd.read_csv(path(s)) for s in stocks]
    return pd.concat(fs, ignore_index=True) if fs else pd.DataFrame(columns=["stock", "signal_date", "ok", "h", "m"])


def final_candidates(base, flags):
    c = base.merge(flags[["stock", "signal_date", "ok", "h", "m"]], on=["stock", "signal_date"], how="left")
    c[["ok", "h", "m"]] = c[["ok", "h", "m"]].fillna(0).astype(int); out = []
    for b in BASES:
        cb = c[c.source == b]
        if BASELINE: out.append(cb.assign(source=f"{b}_ALL"))
        for v in VSEL:
            h, m = VARIANTS[v]; out.append(cb[(cb.ok == 1) & (cb.h == h) & (cb.m == m)].assign(source=f"{b}_{v}"))
    return pd.concat(out, ignore_index=True)[COLS] if out else pd.DataFrame(columns=COLS)


# ------------------------------------------------------------------ step 3: option candles with the ATM -> ITM-1 -> ITM-2 fallback (replaces all8's work_group)
def work_group(dh, mst, t):
    """One (stock, direction, expiry).  For every entry: the ATM series first; if it has no candle at the entry minute (or a zero price) the ITM-1 series, then ITM-2
    (put: ATM+1 / ATM+2 = higher strikes; call: ATM-1 / ATM-2).  Everything after the entry is as in all8_backtest.work_group.  -> (records, skips)"""
    s, dr, E, ents, key = t
    sid, lot = mst[s]
    d0 = date.fromisoformat(min(d for d, _ in ents)); wins = A.windows(d0, E + timedelta(days=1))
    sgn = 1 if dr == "SHORT" else -1
    cache = {}

    def ser(off):
        if off not in cache:
            x = A.get_series(dh, sid, dr, wins, off)
            if x is not None and "strike" in x: x = x[x.index.date <= E]
            cache[off] = x if (x is not None and "strike" in x and len(x)) else None
        return cache[off]

    plans, skips = [], []
    for d, em in ents:
        m = pd.Timestamp(f"{d} {em}"); got, why = None, "no ATM / ITM-1 / ITM-2 candle at the entry minute"
        for off in (0, sgn, 2 * sgn):
            x = ser(off)
            if x is None: continue
            a = x[x.index >= m]
            if a.empty or (a.index[0] - m) > pd.Timedelta(minutes=3): continue
            te, K, entry = a.index[0], float(a.strike.iloc[0]), float(a.c.iloc[0])
            if not entry > 0: why = "zero price"; continue
            got = (off, te, K, entry); break
        if got is None:
            skips.append((A.ekey(s, dr, d, em), why if any(v is not None for v in cache.values()) else "Dhan returned no option candles for this period")); continue
        plans.append((d, em) + got)
    if not plans: return [], skips
    base_off = 0 if cache.get(0) is not None else plans[0][2]
    bx = cache[base_off]; Eeff = max(set(bx.index.date)); step = A.infer_step(bx.strike.values)
    cnt, rest = Counter(), []
    for d, em, off, te, K, entry in plans:
        after = bx[bx.index > te]
        if step > 0 and len(after):
            n = np.rint((K - (after.strike.values - base_off * step)) / step).astype(int)       # which ATM+n series holds the locked strike at each minute
            for v, k in zip(*np.unique(n, return_counts=True)):
                if v != 0 and abs(v) <= A.OFFS_MAX: cnt[int(v)] += int(k)
        rest.append((d, em, off, te, K, entry, len(after)))
    for v, _ in cnt.most_common(A.MAX_OFFS): ser(v)
    big = pd.concat([x[x.index.date <= Eeff] for x in cache.values() if x is not None])
    recs = []
    for d, em, off, te, K, entry, nexp in rest:
        S = big[((big.strike - K).abs() < 1e-6).values & (big.index > te)]
        S = S[~S.index.duplicated()].sort_index()
        if S.empty or nexp == 0: skips.append((A.ekey(s, dr, d, em), "no option candles after the entry")); continue
        r = A.make_record(S, te, entry, lot, K, Eeff, min(1.0, len(S) / nexp))
        r.update(ekey=A.ekey(s, dr, d, em), stock=s, direction=dr, date=d, entry_minute=em, strike_offset=off)
        recs.append(r)
    return recs, skips



def strike_usage():
    """strategy x (ATM / ITM-1 / ITM-2): how many entries used which strike."""
    try:
        recs, ep = A.load_records(), f"{A.OUT}/events.csv"
        if recs.empty or "strike_offset" not in recs or not os.path.exists(ep): return
        ev = pd.read_csv(ep, dtype={"entry_minute": str}); ev["ekey"] = ev.stock + "|" + ev.direction + "|" + ev.date + "|" + ev.entry_minute
        m = ev[["strategy", "ekey"]].merge(recs[["ekey", "strike_offset"]], on="ekey")
        m["strike"] = m.strike_offset.abs().map({0: "ATM", 1: "ITM-1", 2: "ITM-2"})
        m.groupby(["strategy", "strike"]).size().unstack(fill_value=0).to_csv(f"{A.OUT}/strike_usage.csv")
        print(f"wrote {A.OUT}/strike_usage.csv", flush=True)
    except Exception as e:
        print(f"(strike usage skipped: {e!r})", flush=True)


# ------------------------------------------------------------------ modes
def check():
    C.check()
    dh = Dhan(); mst = load_master(); d1 = date.today(); d0 = d1 - timedelta(days=10)
    u = B.eq_minute(dh, mst["RELIANCE"][0], d0, d1)
    if u is None or u.empty: print("Minute call: no data")
    else:
        print(f"Minute call: {len(u)} candles; afternoon flags of the last day:", LH.day_flags(u[u.index.date == max(u.index.date)]))
    B.print_stats(dh)


def run():
    configure(); os.makedirs(A.OUT, exist_ok=True); st = A.load_state()
    print(f"Strategies ({len(STRATS)}): {STRATS}; exits {TEXITS}; SL {A.SLS}; TP {A.TPS}; entries 09:15-{A.ENTRY_LAST}", flush=True)
    dh = Dhan(); mst = load_master()
    try:
        base = build_candidates(dh, mst)
        if base.empty: print("No candidate days in this range."); return
        flags = build_flags(dh, mst, base)
        cand = final_candidates(base, flags)
        print(f"Candidate days {A.START}..{A.END}: {len(cand)} ({', '.join(f'{k} = {v}' for k, v in cand.groupby('source').size().items())})", flush=True)
        ev = A.step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= A.START) & (ev["date"] <= A.END)] if len(ev) else ev
        print(f"Entries (09:15-{A.ENTRY_LAST}): {len(ev)}" + (f"  ({', '.join(f'{k} = {v}' for k, v in ev.groupby('strategy').size().items())})" if len(ev) else ""), flush=True)
        if len(ev): A.step_options(dh, ev, mst, st)
        print("ALL STEPS FINISHED", flush=True)
    except Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        B.print_stats(dh); A.progress(); A.summary(); strike_usage(); A.checkpoint(True)


if __name__ == "__main__":
    configure(); mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": check()
        elif mode == "run": run()
        elif mode in ("summary", "range"): A.summary(); strike_usage()
        else: sys.exit("use: python bpbwru_lh_backtest.py check | run | summary")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
