"""all8_backtest.py - ONE combined backtest of EIGHT entry strategies on ALL F&O stock options (Dhan 1-minute data), many exit variants, trades held until stop / target.

  python all8_backtest.py check     test Dhan access + print a small expiry-calendar check
  python all8_backtest.py run       full backtest for A8_START .. A8_END (resumable - run again after a polite stop)
  python all8_backtest.py summary   rebuild every result file from the saved option data (no API calls)

THE 8 ENTRY STRATEGIES (each is its own strategy, never mixed; LONG buys the ATM call, SHORT the ATM put, nearest monthly expiry, strike locked at entry)
  WICK_GREEN_UPPER / WICK_RED_UPPER / WICK_GREEN_LOWER / WICK_RED_LOWER
        SHAPECMP daily signal (a daily close beyond the 10-day high/low, a later close back across it, entry the next day when price crosses the line again);
        split by the pattern of the signal candle ("previous candle"): green|red  x  upper wick longer|lower wick longer   (4 strategies, no overlap)
  TRENDLINE_1H / TRENDLINE_4H   break -> retest -> re-break of a falling (rising) trendline drawn on the 1-hour / 4-hour chart (trendline_backtest.py rules)
  BREAKOUT_BPB                  10-day-high breakout -> confirmed pullback -> re-cross (bpb_fno_backtest.py rules)
  SHAPECMP_RECROSS_4C           the SHAPECMP signal (no shape rule) entered with the RECROSS_0920_4C rule: from 09:20, 4 one-minute closes on the other side of the
                                line, a 1-minute close beyond it, a close back, and the re-cross is the entry
ENTRY      checked through the WHOLE DAY: the first 1-minute candle from 09:15 to A8_ENTRY_LAST (default 15:20) that touches the level (RECROSS_4C: its own rule).
           Option price = close of the entry-minute option candle.  One entry per signal.

EXIT VARIANTS (every combination is simulated for every entry)
  stop-loss   10 / 20 / 30 % of the premium, or 0 = NO stop-loss
  target      20 / 40 / 60 / 80 / 109 / 120 / 200 / 300 / 400 % of the premium
  time exit   09:30 | 10:00 | 12:00 | 15:30 the same day (close of the last option candle up to that minute; a trade entered at/after that minute is skipped),
              or UNTIL_HIT = no time exit: the trade is held, day after day, until the stop-loss or target is touched.  If neither is touched the trade is closed at the
              last candle of the contract's expiry day (reason EXPIRY).
  Fills      stop / target = first 1-minute low / high that touches the level; a gap through the level fills at that candle's open; if stop and target fall in the
             same minute the STOP is taken.
CAPITAL    at most Rs 60,000 per trade: lots = 60000 // (premium x lot size); a trade whose single lot costs more is skipped.
Charges, taxes and slippage are not included.  Lot sizes are today's values for all years.

HOW A TRADE IS HELD: the option contract is locked at entry (strike + nearest monthly expiry).  The monthly expiry is last Thursday of the month up to Aug 2025 and last Tuesday from
Sep 2025 (earlier day if that day is a holiday: the last day with data is used).  When the stock moves, the locked strike is no longer the ATM strike, so Dhan's rolling ATM+n / ATM-n
series are fetched as needed (A8_OFFS_MAX, A8_MAX_OFFS).  A trade whose option data covers less than A8_COV_MIN (0.9) of the minutes is dropped and counted in trades_summary.csv.

RESULTS in all8_results/ :
  summary.csv                 one row per strategy x time exit x stop-loss x target: trades, win %, PnL, ROI, profit factor, drawdown, DAYS HELD (avg / median / p90 / max, calendar
                              and trading days), exits by reason
  top_by_pnl.csv  top_by_roi.csv  top_by_win_rate.csv  top_by_profit_factor.csv   (variants with at least A8_MIN_TRADES = 30 trades)
  best_per_strategy.csv       the best variant of every strategy by PnL / ROI / win rate
  until_hit_days_held.csv     the UNTIL_HIT variants with the holding-days statistics
  trades_summary.csv          per strategy: signals, entries, entries with option data, skipped (and why), LONG / SHORT trades
  all_trades_top_variants.csv.gz   every trade of the top variants (strategy, entry type, days held ...); A8_TRADES_ALL=1 writes ALL variants (very large)
  summary_by_year_top.csv, REPORT.txt, PROGRESS.txt  (+ events.csv, parts/, skipped/, candidates_*.csv)
"""
import os, sys, json, time, glob, subprocess, zlib
from collections import Counter
for k in ("START", "END", "SYMBOLS", "CAP"):                                # A8_* names -> the COMBO_* names the engine reads
    if os.environ.get("A8_" + k): os.environ["COMBO_" + k] = os.environ["A8_" + k]
OUT = os.environ.get("A8_OUT") or "all8_results"
os.environ["TL_OUT"] = OUT                                                   # trendline_backtest sets COMBO_OUT from it
os.environ.setdefault("COMBO_START", "2023-01-01"); os.environ.setdefault("COMBO_END", "2026-08-31")

import numpy as np, pandas as pd
from datetime import date, datetime, timedelta
import trendline_backtest as T
C, B = T.C, T.B
from bpb_fno_backtest import Dhan, Stop, Fatal, stream, load_master

START, END, UNIVERSE, CAP = C.START, C.END, C.UNIVERSE, C.CAP
C.PRE_TOL = float(os.environ.get("A8_PRE_TOL") or 0.10)                      # daily prefilter: the day's open within 10 % of the level (entry is now checked all day)
STRATS = ["WICK_GREEN_UPPER", "WICK_RED_UPPER", "WICK_GREEN_LOWER", "WICK_RED_LOWER", "TRENDLINE_1H", "TRENDLINE_4H", "BREAKOUT_BPB", "SHAPECMP_RECROSS_4C"]
ENTRY_TYPE = {s: "ALL" for s in STRATS}; ENTRY_TYPE["SHAPECMP_RECROSS_4C"] = "RECROSS_0920_4C"
def ints(name, default): return [int(x) for x in (os.environ.get(name) or default).replace(",", " ").split()]
SLS = ints("A8_SLS", "10,20,30,0")                                           # 0 = no stop-loss
TPS = ints("A8_TPS", "20,40,60,80,109,120,200,300,400")
TEXITS = ["09:30", "10:00", "12:00", "15:30"]
EXITS = TEXITS + ["UNTIL_HIT"]
VARS = [(ex, sl, tp) for ex in EXITS for sl in SLS for tp in TPS]
ENTRY_LAST = os.environ.get("A8_ENTRY_LAST") or "15:20"
ENTRY_MIN = int(ENTRY_LAST[:2]) * 60 + int(ENTRY_LAST[3:5])
E_FIRST = 9 * 60 + 15
OFFS_MAX = int(os.environ.get("A8_OFFS_MAX") or 10)                          # largest strike distance (in steps) from ATM that is fetched
MAX_OFFS = int(os.environ.get("A8_MAX_OFFS") or 8)                           # most extra strike series fetched per request group
COV_MIN = float(os.environ.get("A8_COV_MIN") or 0.9)
MIN_TRADES = int(os.environ.get("A8_MIN_TRADES") or 30)
TOP_N = int(os.environ.get("A8_TOP_N") or 50)
SUM_FROM, SUM_TO = os.environ.get("A8_SUM_ENTRY_FROM") or "", os.environ.get("A8_SUM_ENTRY_TO") or ""   # optional: summarise only entries between these times (HH:MM)
REASON = {1: "STOP", 2: "STOP (gap)", 3: "TARGET", 4: "TARGET (gap)", 5: "TIME", 6: "EXPIRY"}
EVK = ["strategy", "stock", "direction", "date"]
LAST_CP, LAST_SAVE, FLUSHER = [time.time()], [0.0], [None]


def hm(t): return f"{t:%H:%M}"
def ekey(s, d, day, m): return f"{s}|{d}|{day}|{m}"


# ------------------------------------------------------------------ expiry calendar
def last_dow(y, m, dow):
    d = date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)
    while d.weekday() != dow: d -= timedelta(days=1)
    return d


def expiry_calc(d):
    """Monthly stock-option expiry on or after date d: last Thursday up to Aug 2025, last Tuesday from Sep 2025 (a holiday moves it to the day before - found from the data)."""
    y, m = d.year, d.month
    for _ in range(14):
        e = last_dow(y, m, 3 if (y, m) < (2025, 9) else 1)
        if e >= d: return e
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def windows(d0, d1, span=30):
    """Dhan rolling-option windows (to-date exclusive), at most `span` days each."""
    out, a = [], d0
    while a < d1:
        b = min(a + timedelta(days=span), d1); out.append((a, b)); a = b
    return out


# ------------------------------------------------------------------ step 1: candidates (daily signals + trendlines)
def tl_rows_fullday(stock, hourly, tf, t0, t1, pre_tol=None):
    """Same trendline signals as trendline_backtest.signals_for, but the entry day only has to REACH the level at some time of the day (not in its first hour)."""
    pre_tol = C.PRE_TOL if pre_tol is None else pre_tol
    bars = hourly if tf == "1H" else T.to_4h(hourly)
    if len(bars) < 60: return []
    O, H, L, Cl = (bars[c].values.astype(float) for c in ("o", "h", "l", "c"))
    day = np.array(bars.index.strftime("%Y-%m-%d")); udays = sorted(set(day))
    nxt = {d: udays[i + 1] for i, d in enumerate(udays[:-1])}
    g = hourly.groupby(hourly.index.strftime("%Y-%m-%d"))
    dd = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min()})
    rows = []
    for long in (True, False):
        for n, lvl, tb, ln in T.tl_signals(O, H, L, Cl, long, **T.PARAMS[tf]):
            e = nxt.get(day[n])
            if e is None or not (str(t0.date()) <= e <= str(t1.date())) or e not in dd.index: continue
            same = day == day[n]; same[:n] = False
            if (H[same].max() >= lvl) if long else (L[same].min() <= lvl): continue
            f = dd.loc[e]
            if not ((f.h >= lvl and f.o >= lvl * (1 - pre_tol)) if long else (f.l <= lvl and f.o <= lvl * (1 + pre_tol))): continue
            up, lo = H[n] - max(O[n], Cl[n]), min(O[n], Cl[n]) - L[n]
            rows.append(dict(source="TL_" + tf, stock=stock, direction="LONG" if long else "SHORT", ref=round(lvl, 2), signal_date=day[n], date=e,
                             yahoo_open=float(f.o), breakout_date=day[tb], line=round(ln, 2),
                             green=int(Cl[n] > O[n]), red=int(Cl[n] < O[n]), upper_longer=int(up > lo), lower_longer=int(lo > up)))
    return rows


T.signals_for = tl_rows_fullday


# ------------------------------------------------------------------ housekeeping
def load_state():
    p = f"{OUT}/state.json"
    s = json.load(open(p)) if os.path.exists(p) else {}
    s.setdefault("done", []); s.setdefault("expected", []); s["done"] = set(s["done"])
    return s


def save_state(s):
    tmp = f"{OUT}/state.json.tmp"
    json.dump({"done": sorted(s["done"]), "expected": sorted(set(s.get("expected", [])))}, open(tmp, "w")); os.replace(tmp, f"{OUT}/state.json")


def flush(st, ev=None, force=False, every=10):
    if not force and time.time() - LAST_SAVE[0] < every: return
    if ev: pd.DataFrame(ev).drop_duplicates(EVK).to_csv(f"{OUT}/events.csv", index=False)
    save_state(st); LAST_SAVE[0] = time.time()


def checkpoint(force=False):
    """On GitHub Actions: save progress to the repo every ~15 minutes."""
    if not os.environ.get("GITHUB_ACTIONS"): return
    if not force and time.time() - LAST_CP[0] < 900: return
    LAST_CP[0] = time.time()
    if FLUSHER[0]: FLUSHER[0]()
    steps = [["git", "config", "user.name", "all8-bot"], ["git", "config", "user.email", "all8-bot@users.noreply.github.com"], ["git", "add", OUT],
             ["git", "commit", "-m", "all8 progress"], ["git", "pull", "--no-rebase", "-X", "ours", "--no-edit"], ["git", "push"]]
    for c in steps:
        r = subprocess.run(c, capture_output=True, text=True)
        if r.returncode and c[1] != "commit": print(f"checkpoint: '{' '.join(c)}' failed: {(r.stdout + r.stderr)[-300:]}", flush=True); return
    print("checkpoint: progress saved to the repo", flush=True)


def progress():
    st = load_state(); exp = set(st.get("expected", []))
    if not exp: return
    done = len(exp & st["done"])
    msg = f"COMPLETE - all {len(exp)} request groups finished." if done >= len(exp) else f"PARTIAL - {done} of {len(exp)} request groups finished. Results cover only the finished part. Run again to continue."
    open(f"{OUT}/PROGRESS.txt", "w").write(msg + "\n"); print("\n*** " + msg + " ***", flush=True)


# ------------------------------------------------------------------ step 2: 1-minute stock candles -> entries of the 8 strategies
def strategies_for(source, typ, green, red, up, lo):
    if source == "BPB": return ["BREAKOUT_BPB"] if typ == "ALL" else []
    if source in ("TL_1H", "TL_4H"): return ["TRENDLINE_" + source[3:]] if typ == "ALL" else []
    out = []
    if source == "SHAPE":
        if typ == "ALL":
            if green == 1 and up == 1: out.append("WICK_GREEN_UPPER")
            if red == 1 and up == 1: out.append("WICK_RED_UPPER")
            if green == 1 and lo == 1: out.append("WICK_GREEN_LOWER")
            if red == 1 and lo == 1: out.append("WICK_RED_LOWER")
        if typ == "RECROSS_0920_4C": out.append("SHAPECMP_RECROSS_4C")
    return out


def step_events(dh, cand, mst, st):
    ep = f"{OUT}/events.csv"
    ev = pd.read_csv(ep).to_dict("records") if os.path.exists(ep) else []
    tasks, expected = [], []
    c2 = cand[cand.stock.isin(mst)].copy(); c2["d"] = pd.to_datetime(c2["date"]).dt.date
    for s, g in c2.groupby("stock"):
        for d0, d1 in B.clusters(g.d.unique().tolist(), B.EQ_SPAN, B.EQ_GAP):
            key = f"EQ|A8|{ENTRY_LAST}|{START}|{END}|{s}|{d0}|{d1}"; expected.append(key)
            if key not in st["done"]: tasks.append((s, g[(g.d >= d0) & (g.d <= d1)], d0, d1, key))
    st["expected"] = sorted(set(st.get("expected", [])) | set(expected))
    miss = sorted(set(cand.stock) - set(mst))
    if miss: print(f"not in Dhan stock-option list - skipped: {miss}", flush=True)
    print(f"Dhan stock-candle work: {len(tasks)} request groups to do ({len(expected) - len(tasks)} already done)", flush=True)

    def work(t):
        s, g, d0, d1, key = t
        u_all = B.eq_minute(dh, mst[s][0], d0, d1)
        if u_all is None: return None
        if u_all.empty: return [], 0
        mm = u_all.index.hour.values * 60 + u_all.index.minute.values
        u_all = u_all[(mm >= E_FIRST) & (mm <= ENTRY_MIN)]
        days = {k: v for k, v in u_all.groupby(u_all.index.date)}
        out = []
        for r in g.itertuples():
            u = days.get(r.d)
            if u is None or u.empty: continue
            ratio = float(u.o.iloc[0]) / float(r.yahoo_open)
            lvl = float(r.ref) * (ratio if abs(ratio - 1) > .2 else 1.0)                 # split / bonus: Yahoo adjusted, Dhan raw
            for typ, m in C.entries_for(u, lvl, r.direction == "LONG").items():
                for strat in strategies_for(r.source, typ, r.green, r.red, r.upper_longer, r.lower_longer):
                    out.append(dict(strategy=strat, source=r.source, stock=s, direction=r.direction, type=typ, date=r.date, ref=round(lvl, 2),
                                    signal_date=r.signal_date, entry_minute=hm(m), stock_price=float(u.c[m])))
        return out, len(days)

    fails = [0]

    def handle(t, res):
        s, g, d0, d1, key = t
        if res is None:
            fails[0] += 1; print(f"stock candles {s} {d0}..{d1}: FAILED (retried on the next run), calls {dh.n}", flush=True); return
        out, nd = res
        ev.extend(out); st["done"].add(key); flush(st, ev); checkpoint()
        print(f"stock candles {s} {d0}..{d1}: {len(g)} candidate days, minute data on {nd} days, {len(out)} entries, calls {dh.n}", flush=True)

    FLUSHER[0] = lambda: flush(st, ev, force=True)
    try: stream(tasks, work, handle)
    finally: flush(st, ev, force=True)
    if fails[0]: print(f"WARNING: {fails[0]} stock-candle request(s) failed - run again to retry them.", flush=True)
    return pd.DataFrame(ev).drop_duplicates(EVK).reset_index(drop=True) if ev else pd.DataFrame()


# ------------------------------------------------------------------ step 3: option candles -> one compact record per entry
def get_series(dh, sid, dr, wins, off):
    parts = []
    for a, b in wins:
        x = B.rolling(dh, sid, a, b, dr, off)
        if x is not None and len(x): parts.append(x)
    if not parts: return None
    x = pd.concat(parts)
    return x[~x.index.duplicated()].sort_index()


def infer_step(strikes):
    u = np.unique(np.round(np.asarray(strikes, float), 4)); d = np.diff(u); d = d[d > 1e-9]
    return float(d.min()) if len(d) else 0.0


def stairs(v, o, dm, low):
    """Running new lows (or highs): [minutes since entry, price, open of that candle].  The first candle that touches ANY level is always one of these."""
    run = np.minimum.accumulate(v) if low else np.maximum.accumulate(v)
    new = np.r_[True, (v[1:] < run[:-1]) if low else (v[1:] > run[:-1])]
    return [[int(dm[i]), round(float(v[i]), 2), round(float(o[i]), 2)] for i in np.nonzero(new)[0]]


def make_record(S, te, entry, lot, K, expiry, cov):
    """S = option candles after the entry minute (o,h,l,c, index = time), up to the expiry.  Everything the exit variants need, in a few hundred numbers."""
    dm = np.asarray((S.index - te) / pd.Timedelta(minutes=1)).astype(np.int64)
    o, h, l, c = (S[x].values.astype(float) for x in ("o", "h", "l", "c"))
    days = S.index.normalize().values
    bnd = np.nonzero(np.r_[days[0] != np.datetime64(te.normalize()), days[1:] != days[:-1]])[0]          # first candle of every later trading day
    tx = {}
    for lim in TEXITS:
        lt = pd.Timestamp(f"{te.date()} {lim}")
        if te >= lt: continue
        w = S.index <= lt
        if not w.any(): continue
        j = int(np.nonzero(w)[0][-1])
        tx[lim] = [int(dm[j]), round(float(c[j]), 2), int((lt - S.index[j]) > pd.Timedelta(minutes=5))]
    return dict(entry_time=hm(te), strike=K, entry_price=round(entry, 2), lot=int(lot), expiry=str(expiry), cov=round(cov, 3), bars=len(S),
                ls=json.dumps(stairs(l, o, dm, True), separators=(",", ":")), hs=json.dumps(stairs(h, o, dm, False), separators=(",", ":")),
                db=json.dumps([int(dm[i]) for i in bnd], separators=(",", ":")), tx=json.dumps(tx, separators=(",", ":")),
                last=json.dumps([int(dm[-1]), round(float(c[-1]), 2)], separators=(",", ":")))


def work_group(dh, mst, t):
    """One (stock, direction, expiry): the ATM series first, then the strike series the locked contracts need.  -> (records, skips)"""
    s, dr, E, ents, key = t
    sid, lot = mst[s]
    d0 = date.fromisoformat(min(d for d, _ in ents)); wins = windows(d0, E + timedelta(days=1))
    x0 = get_series(dh, sid, dr, wins, 0)
    if x0 is None or "strike" not in x0:
        return [], [(ekey(s, dr, d, m), "Dhan returned no option candles for this period") for d, m in ents]
    x0 = x0[x0.index.date <= E]
    if x0.empty: return [], [(ekey(s, dr, d, m), "no option candles up to the expiry") for d, m in ents]
    Eeff = max(set(x0.index.date))                                                   # E itself, or the last trading day before it (holiday)
    step = infer_step(x0.strike.values)
    plans, cnt, skips = [], Counter(), []
    for d, em in ents:
        m = pd.Timestamp(f"{d} {em}"); a = x0[x0.index >= m]
        if a.empty or (a.index[0] - m) > pd.Timedelta(minutes=3): skips.append((ekey(s, dr, d, em), "no ATM candle at the entry minute")); continue
        te, K, entry = a.index[0], float(a.strike.iloc[0]), float(a.c.iloc[0])
        if not entry > 0: skips.append((ekey(s, dr, d, em), "zero price")); continue
        after = x0[x0.index > te]
        if step > 0 and len(after):
            n = np.rint((K - after.strike.values) / step).astype(int)                 # which ATM+n series holds the locked strike at each minute
            for v, k in zip(*np.unique(n, return_counts=True)):
                if v != 0 and abs(v) <= OFFS_MAX: cnt[int(v)] += int(k)
        plans.append((d, em, te, K, entry, len(after)))
    allr = [x0]
    for v, _ in cnt.most_common(MAX_OFFS):
        x = get_series(dh, sid, dr, wins, v)
        if x is not None and "strike" in x: allr.append(x[x.index.date <= Eeff])
    big = pd.concat(allr)
    recs = []
    for d, em, te, K, entry, nexp in plans:
        S = big[((big.strike - K).abs() < 1e-6).values & (big.index > te)]
        S = S[~S.index.duplicated()].sort_index()
        if S.empty or nexp == 0: skips.append((ekey(s, dr, d, em), "no option candles after the entry")); continue
        r = make_record(S, te, entry, lot, K, Eeff, min(1.0, len(S) / nexp))
        r.update(ekey=ekey(s, dr, d, em), stock=s, direction=dr, date=d, entry_minute=em)
        recs.append(r)
    return recs, skips


def step_options(dh, ev, mst, st):
    os.makedirs(f"{OUT}/parts", exist_ok=True); os.makedirs(f"{OUT}/skipped", exist_ok=True)
    ent = ev.drop_duplicates(["stock", "direction", "date", "entry_minute"])[["stock", "direction", "date", "entry_minute"]].copy()
    ent["E"] = ent.date.map(lambda x: expiry_calc(date.fromisoformat(x)))
    tasks, expected = [], []
    for (s, dr, E), g in ent.groupby(["stock", "direction", "E"]):
        if s not in mst: continue
        ents = sorted(zip(g.date, g.entry_minute))
        key = f"OPT|{s}|{dr}|{E}|{zlib.crc32(json.dumps(ents).encode()):08x}"; expected.append(key)
        if key not in st["done"]: tasks.append((s, dr, E, ents, key))
    st["expected"] = sorted(set(st.get("expected", [])) | set(expected))
    print(f"Dhan option work: {len(tasks)} request groups to do ({len(expected) - len(tasks)} already done)", flush=True)

    def work(t):
        recs, skips = work_group(dh, mst, t)
        s, dr, E = t[0], t[1], t[2]
        if recs: pd.DataFrame(recs).to_csv(f"{OUT}/parts/{s}_{dr}_{E}.csv.gz", index=False, compression={"method": "gzip", "compresslevel": 1})
        if skips: pd.DataFrame(skips, columns=["ekey", "reason"]).to_csv(f"{OUT}/skipped/{s}_{dr}_{E}.csv", index=False)
        return len(recs), len(skips)

    def handle(t, res):
        s, dr, E, ents, key = t
        st["done"].add(key); flush(st); checkpoint()
        print(f"options {s} {dr} expiry {E}: {len(ents)} entries, {res[0]} with option data, {res[1]} skipped, calls so far {dh.n}", flush=True)

    FLUSHER[0] = lambda: flush(st, force=True)
    try: stream(tasks, work, handle)
    finally: flush(st, force=True)


# ------------------------------------------------------------------ step 4: simulate every exit variant
def simulate_one(entry, ls, hs, tx, last):
    """-> list over VARS of (exit minute since entry, exit price, reason code, thin flag); code 0 = variant not available for this entry."""
    slh, tph = {}, {}
    for s in SLS:
        if not s: continue
        thr = round(entry * (1 - s / 100), 6); i = int(np.searchsorted(-ls[:, 1], -thr, side="left"))
        if i < len(ls): gap = ls[i, 2] <= thr; slh[s] = (int(ls[i, 0]), float(ls[i, 2]) if gap else thr, 2 if gap else 1)
    for tp in TPS:
        thr = round(entry * (1 + tp / 100), 6); i = int(np.searchsorted(hs[:, 1], thr, side="left"))
        if i < len(hs): gap = hs[i, 2] >= thr; tph[tp] = (int(hs[i, 0]), float(hs[i, 2]) if gap else thr, 4 if gap else 3)
    out = []
    for ex in EXITS:
        if ex == "UNTIL_HIT": lim, end = last[0], (last[0], last[1], 6, 0)
        else:
            t = tx.get(ex)
            if t is None: out += [(0, 0.0, 0, 0)] * (len(SLS) * len(TPS)); continue
            lim, end = t[0], (t[0], t[1], 5, t[2])
        for s in SLS:
            sh = slh.get(s) if s else None; sh_ok = sh is not None and sh[0] <= lim
            for tp in TPS:
                th = tph.get(tp); th_ok = th is not None and th[0] <= lim
                if sh_ok and (not th_ok or sh[0] <= th[0]): out.append((sh[0], sh[1], sh[2], 0))        # stop first (also on a tie)
                elif th_ok: out.append((th[0], th[1], th[2], 0))
                else: out.append(end)
    return out


class Sim:
    """All trades of one strategy: arrays (entries x variants)."""
    def __init__(self, R):
        n, V = len(R), len(VARS)
        self.R = R.reset_index(drop=True)
        self.pnl = np.full((n, V), np.nan); self.px = np.zeros((n, V)); self.dm = np.zeros((n, V), np.int32)
        self.code = np.zeros((n, V), np.int8); self.late = np.zeros((n, V), np.int8)
        self.days = np.full((n, V), np.nan); self.tdays = np.full((n, V), np.nan)
        self.lots = np.zeros(n, np.int64); self.cost = np.zeros(n)
        for i, r in enumerate(self.R.itertuples()):
            lots = int(CAP // (r.entry_price * r.lot)); self.lots[i] = lots
            if lots < 1: continue
            qty = lots * r.lot; self.cost[i] = r.entry_price * qty
            ls = np.array(json.loads(r.ls), float).reshape(-1, 3); hs = np.array(json.loads(r.hs), float).reshape(-1, 3)
            db = np.array(json.loads(r.db), np.int64); res = simulate_one(r.entry_price, ls, hs, json.loads(r.tx), json.loads(r.last))
            te = datetime.strptime(f"{r.date} {r.entry_time}", "%Y-%m-%d %H:%M"); t0o = te.toordinal()
            for v, (dm, px, code, late) in enumerate(res):
                if not code: continue
                self.px[i, v], self.dm[i, v], self.code[i, v], self.late[i, v] = px, dm, code, late
                self.pnl[i, v] = (px - r.entry_price) * qty
                self.days[i, v] = (te + timedelta(minutes=int(dm))).toordinal() - t0o
                self.tdays[i, v] = int(np.searchsorted(db, dm, side="right"))

    def aggregate(self, strat):
        ok = self.code > 0; p = np.where(ok, self.pnl, 0.0); cost = np.where(ok, self.cost[:, None], 0.0)
        n = ok.sum(0); wins = (p > 0).sum(0); cap = cost.sum(0); tot = p.sum(0)
        gp = np.where(p > 0, p, 0).sum(0); gl = -np.where(p < 0, p, 0).sum(0)
        c = np.cumsum(p, axis=0); peak = np.maximum.accumulate(np.vstack([np.zeros((1, c.shape[1])), c]), axis=0)[1:]; dd = (c - peak).min(0) if len(c) else np.zeros(len(VARS))
        dk = np.where(ok, self.days, np.nan); tk = np.where(ok, self.tdays, np.nan)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            avg_d, med_d, p90_d, max_d, avg_t = (np.nanmean(dk, 0), np.nanmedian(dk, 0), np.nanpercentile(dk, 90, axis=0), np.nanmax(dk, 0), np.nanmean(tk, 0)) if len(dk) else (np.full(len(VARS), np.nan),) * 5
        rows = []
        for v, (ex, sl, tp) in enumerate(VARS):
            if n[v] == 0: continue
            cd = self.code[:, v]
            rows.append(dict(strategy=strat, entry_type=ENTRY_TYPE[strat], exit_rule=ex, sl=sl, tp=tp, trades=int(n[v]), wins=int(wins[v]), win_pct=round(wins[v] / n[v] * 100, 2),
                             total_pnl=int(round(tot[v])), capital_used=int(round(cap[v])), roi_pct=round(tot[v] / cap[v] * 100, 2) if cap[v] else np.nan,
                             profit_factor=round(gp[v] / gl[v], 2) if gl[v] > 0 else np.nan, avg_pnl=int(round(tot[v] / n[v])), max_drawdown=int(round(dd[v])),
                             avg_days_held=round(float(avg_d[v]), 2), median_days_held=float(med_d[v]), p90_days_held=float(p90_d[v]), max_days_held=int(max_d[v]),
                             avg_trading_days_held=round(float(avg_t[v]), 2), stop_exits=int(np.isin(cd, (1, 2)).sum()), target_exits=int(np.isin(cd, (3, 4)).sum()),
                             time_exits=int((cd == 5).sum()), expiry_exits=int((cd == 6).sum()), thin_exits=int(self.late[:, v].sum())))
        return rows

    def trades(self, vs, strat):
        """Trade rows of the variants (column indices) vs."""
        out = []
        te = pd.to_datetime(self.R.date + " " + self.R.entry_time)
        for v in vs:
            m = self.code[:, v] > 0
            if not m.any(): continue
            R = self.R[m]; ex, sl, tp = VARS[v]; xt = te[m] + pd.to_timedelta(self.dm[m, v].astype(np.int64), unit="m")
            out.append(pd.DataFrame(dict(
                strategy=strat, entry_type=ENTRY_TYPE[strat], exit_rule=ex, sl=sl, tp=tp, stock=R.stock.values, direction=R.direction.values, entry_date=R.date.values,
                entry_time=R.entry_time.values, strike=R.strike.values, expiry=R.expiry.values, entry_price=R.entry_price.values, lots=self.lots[m], cost=self.cost[m].round(),
                exit_date=xt.dt.strftime("%Y-%m-%d").values, exit_time=xt.dt.strftime("%H:%M").values, exit_price=self.px[m, v].round(2),
                reason=[REASON[x] for x in self.code[m, v]], pnl=self.pnl[m, v].round(), ret_pct=((self.px[m, v] / R.entry_price.values - 1) * 100).round(2),
                days_held=self.days[m, v].astype(int), trading_days_held=self.tdays[m, v].astype(int), thin_exit=self.late[m, v])))
        return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


# ------------------------------------------------------------------ step 5: result files
def load_records():
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    if not fs: return pd.DataFrame()
    return pd.concat([pd.read_csv(f) for f in fs], ignore_index=True).drop_duplicates("ekey")


def load_skips():
    fs = sorted(glob.glob(f"{OUT}/skipped/*.csv"))
    return pd.concat([pd.read_csv(f) for f in fs], ignore_index=True).drop_duplicates("ekey") if fs else pd.DataFrame(columns=["ekey", "reason"])


def summary():
    progress(); os.makedirs(OUT, exist_ok=True)
    ep = f"{OUT}/events.csv"; recs = load_records()
    if recs.empty or not os.path.exists(ep): print("No saved option data yet - run the backtest first.", flush=True); return
    ev = pd.read_csv(ep, dtype={"entry_minute": str}); sk = load_skips()
    ev["ekey"] = ev.stock + "|" + ev.direction + "|" + ev.date + "|" + ev.entry_minute
    if SUM_FROM: recs = recs[recs.entry_time >= SUM_FROM]
    if SUM_TO: recs = recs[recs.entry_time <= SUM_TO]
    sims, rows, cov = {}, [], []
    for s in STRATS:
        e = ev[ev.strategy == s].drop_duplicates(["stock", "direction", "date"])
        R = e[["ekey", "strategy"]].merge(recs, on="ekey", how="inner")
        reason = sk[sk.ekey.isin(e.ekey)].reason.value_counts().to_dict()
        has = len(R); low = int((R["cov"] < COV_MIN).sum()) if has else 0
        R = R[R["cov"] >= COV_MIN].sort_values(["date", "entry_time", "stock"]) if has else R
        c = dict(strategy=s, entry_type=ENTRY_TYPE[s], signals_with_entry=len(e), entries_with_option_data=has, dropped_low_coverage=low,
                 skipped_no_option_data=int(sum(reason.values())), skip_reasons="; ".join(f"{k} = {v}" for k, v in reason.items()))
        if len(R):
            sim = Sim(R); sims[s] = sim; rows += sim.aggregate(s)
            c.update(trades_one_lot_affordable=int((sim.lots > 0).sum()), long_trades=int((sim.R.direction == "LONG").sum()), short_trades=int((sim.R.direction == "SHORT").sum()),
                     first_entry=sim.R.date.min(), last_entry=sim.R.date.max(), avg_option_price=round(float(sim.R.entry_price.mean()), 2))
        cov.append(c)
    pd.DataFrame(cov).to_csv(f"{OUT}/trades_summary.csv", index=False)
    if not rows: print("No trades could be simulated yet.", flush=True); return
    S = pd.DataFrame(rows).sort_values("total_pnl", ascending=False).reset_index(drop=True)
    S.insert(0, "variant", S.strategy + " | " + S.exit_rule + " | SL" + S.sl.astype(str) + " | TP" + S.tp.astype(str))
    S.to_csv(f"{OUT}/summary.csv", index=False)
    good = S[S.trades >= MIN_TRADES]
    for name, col in (("pnl", "total_pnl"), ("roi", "roi_pct"), ("win_rate", "win_pct"), ("profit_factor", "profit_factor")):
        good.sort_values(col, ascending=False).head(TOP_N).to_csv(f"{OUT}/top_by_{name}.csv", index=False)
    best = []
    for s, g in good.groupby("strategy", sort=False):
        for lab, col in (("PNL", "total_pnl"), ("ROI", "roi_pct"), ("WIN_RATE", "win_pct")): best.append(g.sort_values(col, ascending=False).iloc[0].to_dict() | {"best_by": lab})
    pd.DataFrame(best).to_csv(f"{OUT}/best_per_strategy.csv", index=False)
    u = S[S.exit_rule == "UNTIL_HIT"].sort_values(["strategy", "sl", "tp"])
    u[["strategy", "entry_type", "sl", "tp", "trades", "win_pct", "total_pnl", "roi_pct", "avg_days_held", "median_days_held", "p90_days_held", "max_days_held", "avg_trading_days_held",
       "stop_exits", "target_exits", "expiry_exits"]].to_csv(f"{OUT}/until_hit_days_held.csv", index=False)
    # trades of the top variants (every trade: strategy, entry type, days held ...)
    vi = {(ex, sl, tp): i for i, (ex, sl, tp) in enumerate(VARS)}
    if os.environ.get("A8_TRADES_ALL") == "1": pick = {s: list(range(len(VARS))) for s in sims}
    else:
        top = int(os.environ.get("A8_TRADES_TOP") or 10); chosen = pd.concat([good.sort_values("total_pnl", ascending=False).head(top), good.sort_values("roi_pct", ascending=False).head(top),
                                                                          pd.DataFrame(best)]).drop_duplicates(["strategy", "exit_rule", "sl", "tp"])
        pick = {}
        for r in chosen.itertuples(): pick.setdefault(r.strategy, []).append(vi[(r.exit_rule, int(r.sl), int(r.tp))])
    if os.environ.get("A8_TRADES_ALL") == "1":   # every trade of every variant, one file per strategy (keeps each file small enough for GitHub)
        os.makedirs(f"{OUT}/all_trades", exist_ok=True)
        for s, vs in pick.items():
            if s in sims: sims[s].trades(vs, s).to_csv(f"{OUT}/all_trades/{s}.csv.gz", index=False, compression={"method": "gzip", "compresslevel": 6})
        print("all-variant trade files written to", f"{OUT}/all_trades/", flush=True)
        pick = {}
        for r in pd.concat([good.sort_values("total_pnl", ascending=False).head(10), good.sort_values("roi_pct", ascending=False).head(10), pd.DataFrame(best)]).drop_duplicates(["strategy", "exit_rule", "sl", "tp"]).itertuples():
            pick.setdefault(r.strategy, []).append(vi[(r.exit_rule, int(r.sl), int(r.tp))])
    T_ = pd.concat([sims[s].trades(vs, s) for s, vs in pick.items() if s in sims], ignore_index=True)
    T_.to_csv(f"{OUT}/all_trades_top_variants.csv.gz", index=False, compression={"method": "gzip", "compresslevel": 6})
    yr = T_.assign(year=T_.entry_date.str[:4]).groupby(["strategy", "exit_rule", "sl", "tp", "year"]).agg(trades=("pnl", "size"), win_pct=("pnl", lambda x: round((x > 0).mean() * 100, 1)),
                                                                                                         total_pnl=("pnl", "sum"), capital=("cost", "sum"), avg_days_held=("days_held", "mean")).reset_index()
    yr["roi_pct"] = (yr.total_pnl / yr.capital * 100).round(2); yr["avg_days_held"] = yr.avg_days_held.round(2)
    yr.to_csv(f"{OUT}/summary_by_year_top.csv", index=False)
    cols = ["variant", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "avg_days_held", "max_days_held"]
    lines = [f"Stocks tested: {len(UNIVERSE)}; entry dates {START} .. {END}; entry checked 09:15 .. {ENTRY_LAST}" + (f"; summary limited to entries {SUM_FROM or '09:15'}..{SUM_TO or ENTRY_LAST}" if SUM_FROM or SUM_TO else ""),
             f"Variants: {len(SLS)} stop-loss x {len(TPS)} targets x {len(EXITS)} exits = {len(VARS)} per strategy, {len(STRATS)} strategies; {len(S)} variant rows with trades.",
             "", "Entries by strategy:", pd.DataFrame(cov)[["strategy", "signals_with_entry", "entries_with_option_data", "dropped_low_coverage", "skipped_no_option_data"]].to_string(index=False),
             "", f"TOP 15 BY TOTAL PnL (min {MIN_TRADES} trades):", good.sort_values("total_pnl", ascending=False).head(15)[cols].to_string(index=False),
             "", f"TOP 15 BY ROI (min {MIN_TRADES} trades):", good.sort_values("roi_pct", ascending=False).head(15)[cols].to_string(index=False)]
    open(f"{OUT}/REPORT.txt", "w").write("\n".join(lines) + "\n"); print("\n" + "\n".join(lines), flush=True)


# ------------------------------------------------------------------ modes
def check():
    C.check()
    dh = Dhan(); mst = load_master(); sid = mst["RELIANCE"][0]
    e = expiry_calc(date.today() - timedelta(days=45)); e2 = expiry_calc(e + timedelta(days=1))
    print(f"\nExpiry calendar check (computed monthly expiries {e} and {e2}): the ATM strike / price should jump on the day AFTER each expiry, because the series then moves to the next month.", flush=True)
    for ex in (e, e2):
        x = B.rolling(dh, sid, ex - timedelta(days=4), ex + timedelta(days=5), "LONG", 0)
        if x is None or x.empty: print(f"  {ex}: no data"); continue
        d = x.groupby(x.index.date).agg(first_strike=("strike", "first"), last_close=("c", "last"), candles=("c", "size"))
        print(f"  expiry {ex} ({ex:%A}):\n" + d.to_string(), flush=True)
    B.print_stats(dh)


def run():
    os.makedirs(OUT, exist_ok=True); st = load_state()
    dh = Dhan(); mst = load_master()
    try:
        cp = f"{OUT}/candidates_{START}_{END}.csv"
        if os.path.exists(cp): cand = pd.read_csv(cp)
        else:
            yc = C.yahoo_candidates(); tl = T.build_candidates(dh, mst, st)
            cand = pd.concat([yc, tl], ignore_index=True)
            if cand.empty: print("No candidate days in this range."); return
            cand.to_csv(cp, index=False)
        print(f"Candidate days {START}..{END}: {len(cand)} ({', '.join(f'{k} = {v}' for k, v in cand.groupby('source').size().items())})", flush=True)
        ev = step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= START) & (ev["date"] <= END)] if len(ev) else ev
        print(f"Entries (09:15-{ENTRY_LAST}): {len(ev)}" + (f"  ({', '.join(f'{k} = {v}' for k, v in ev.groupby('strategy').size().items())})" if len(ev) else ""), flush=True)
        if len(ev): step_options(dh, ev, mst, st)
        print("ALL STEPS FINISHED", flush=True)
    except Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        B.print_stats(dh); progress(); summary(); checkpoint(True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": check()
        elif mode == "run": run()
        elif mode in ("summary", "range"): summary()
        else: sys.exit("use: python all8_backtest.py check | run | summary")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
