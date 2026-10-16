"""combo_dayrisk_backtest.py - BPB + SHAPECMP strategies combined, with a DAY STOP-LOSS test, on ALL F&O stock options (Yahoo daily + Dhan 1-minute).

  python combo_dayrisk_backtest.py check     test Dhan access
  python combo_dayrisk_backtest.py run       full backtest for COMBO_START .. COMBO_END (resumable - run again after a polite stop)
  python combo_dayrisk_backtest.py summary   rebuild every table from the saved option data (no API calls); honours COMBO_START / COMBO_END and DAY_SLS

DATE RANGE : you enter it by hand - COMBO_START / COMBO_END (YYYY-MM-DD). In GitHub Actions: the "start" and "end" boxes of the workflow.

STRATEGIES (signals come from the Yahoo daily candles, the entry from the Dhan 1-minute stock candles)
  BPB       the breakout -> pullback -> re-cross strategy of bpb_fno_backtest.py, unchanged (10-day-high line, entry level = highest high since the
            breakout, pullback confirmed by a bearish day, one setup = one entry day).  Entry = first 1-minute candle touching the level.
  SHAPECMP  the swing-alert strategy: a daily candle closes beyond the 10-day high/low (breakout within the last 20 days), a later candle (the SIGNAL day)
            closes back on the other side of that line, and on the NEXT day the entry fires when price crosses the line again.
            Five variants, decided by the signal-day candle (the "previous candle" before the entry day):
              NO_SHAPE_RULE       every signal
              PREV_GREEN          signal candle green  (close > open)
              PREV_RED            signal candle red    (close < open)
              UPPER_WICK_LONGER   upper wick > lower wick
              LOWER_WICK_LONGER   lower wick > upper wick
            Each variant is run with the four entry types of the shapecmp study:
              ALL              first 1-minute touch of the line
              OPEN_0915        the 09:15 candle already touches the line
              FROM_0920_4C     from 09:20: a 1-minute close beyond the line after 4 closes on the other side
              RECROSS_0920_4C  that cross, then a close back, then the re-cross is the entry
  In EVERY strategy and entry type the entry candle must lie between 09:15 and 09:25.  LONG buys the ATM call, SHORT the ATM put
  (nearest monthly expiry, strike locked at the entry minute, option price = close of the entry-minute candle).

EXIT       trade stop-loss 10 / 20 / 30 % of the premium (first 1-minute low that touches it; a gap through it fills at the open) or the time exit at 09:30
           (close of the last option candle up to 09:30).  No profit target.
CAPITAL    at most Rs 60,000 per trade in every variant: lots = 60000 // (premium x lot size); a trade whose single lot costs more is skipped.
DAY STOP   (the new test) DAY_SLS = 0 (no day stop-loss), 5000, 6000, 12000, 18000, 24000, 30000.  All trades of one day are tracked together minute by minute:
           day P&L = realised P&L + open P&L at each 1-minute close.  The first minute it is <= -DAY_SL, every open trade is closed at that minute's
           close and no further entry is taken that day.  Every strategy variant is simulated on its own (its own trades, its own day total).
Charges, taxes and slippage are not included.  Lot sizes are today's values for all years.

Output folder combo_results/ : parts/ (option minute paths), events.csv, summary.csv (every strategy x entry type x trade SL x day SL), roi_matrix.csv,
  daily_pnl.csv.gz, summary_by_year.csv, summary_by_month.csv, trades_no_day_sl.csv.gz, REPORT.txt, PROGRESS.txt
"""
import os, sys, json, glob, subprocess, time, zlib
import numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

import bpb_fno_backtest as B                       # Dhan client, rate limiter, thread stream, bpb setup state machine (same code, nothing copied twice)
from bpb_fno_backtest import Dhan, Stop, Fatal, stream, eq_minute, rolling, load_master, find_setups, clusters, FNO

START = os.environ.get("COMBO_START") or str(date.today() - timedelta(days=3 * 365))
END = os.environ.get("COMBO_END") or str(date.today())
UNIVERSE = [s.strip().upper() for s in (os.environ.get("COMBO_SYMBOLS") or "").replace(",", " ").split()] or FNO
OUT = os.environ.get("COMBO_OUT", "combo_results")
E_FIRST, E_LAST, X_MIN = 9 * 60 + 15, 9 * 60 + 25, 9 * 60 + 30      # entry candles 09:15..09:25, time exit 09:30
SLS = [10, 20, 30]
CAP = int(os.environ.get("COMBO_CAP") or 60000)                      # max capital per trade
DAY_SLS = [int(x) for x in (os.environ.get("DAY_SLS") or "0,5000,6000,12000,18000,24000,30000").replace(",", " ").split()]   # 0 = no day stop-loss
PRE_TOL = float(os.environ.get("PRE_TOL") or 0.04)                   # daily-open prefilter: open within 4 % of the level on the entry side
OPT_GAP = int(os.environ.get("OPT_GAP") or 15)
EXTRA = [int(x) for x in (os.environ.get("OFFSETS2") or "1,-1").split(",") if x.strip()]
SHAPES = ["NO_SHAPE_RULE", "PREV_GREEN", "PREV_RED", "UPPER_WICK_LONGER", "LOWER_WICK_LONGER"]
TYPES = ["ALL", "OPEN_0915", "FROM_0920_4C", "RECROSS_0920_4C"]
GRID = list(range(E_FIRST, X_MIN + 1))                               # minute grid 09:15 .. 09:30
LAST_CP = [time.time()]
FLUSHER = [None]
LAST_SAVE = [0.0]
EVK = ["source", "stock", "direction", "type", "date"]
PCOLS = ["stock", "direction", "date", "entry_minute", "entry_time", "strike", "entry_price", "lot", "path"]


def hm(t): return f"{t:%H:%M}"
def mins_of(t): return t.hour * 60 + t.minute
def to_min(s): return int(s[:2]) * 60 + int(s[3:5])


# ------------------------------------------------------------------ step 1: daily candles -> candidate entry days
def shape_signals(O, H, L, C, long, lookback=10, window=20):
    """SHAPECMP daily rule (same as setup() of the swing alert, run on every day).  Day n is a SIGNAL day when a breakout candle i (n-i <= 20) closed beyond the
    10-day high/low `ref`, and day n closes back on the other side of it.  The LAST such breakout candle gives the line.  Entry is on day n+1.
    Returns [(n, ref, i)]."""
    if not long: O, H, L, C = -O, -L, -H, -C
    N = len(C); ref = np.full(N, np.nan)
    for i in range(lookback, N): ref[i] = H[i - lookback:i].max()
    out = []
    for n in range(lookback + 1, N - 1):
        for i in range(n - 1, max(lookback, n - window) - 1, -1):
            if C[i] > ref[i] and C[n] < ref[i]:
                out.append((n, ref[i], i)); break
    sg = 1.0 if long else -1.0
    return [(n, sg * r, i) for n, r, i in out]


def yahoo_candidates():
    import yfinance as yf
    t0, t1 = pd.Timestamp(START), pd.Timestamp(END)
    raw = yf.download([s + ".NS" for s in UNIVERSE], start=str((t0 - pd.Timedelta(days=200)).date()), end=str((t1 + pd.Timedelta(days=3)).date()),
                      group_by="ticker", auto_adjust=False, progress=False, threads=True)
    rows, nst = [], 0
    for s in UNIVERSE:
        try: d = raw[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
        if len(d) < 60: continue
        nst += 1
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        O, H, L, C = (d[k].values.astype(float) for k in ("Open", "High", "Low", "Close"))
        dates = d.index.strftime("%Y-%m-%d")
        for long in (True, False):
            sg = 1.0 if long else -1.0
            def near(e, lvl): return (H[e] >= lvl and O[e] >= lvl * (1 - PRE_TOL)) if long else (L[e] <= lvl and O[e] <= lvl * (1 + PRE_TOL))
            args = (O, H, L, C) if long else (-O, -L, -H, -C)
            for i, lvl, line, b in find_setups(*args):                                   # --- BPB (identical state machine to bpb_fno_backtest.py)
                if not (t0 <= d.index[i] <= t1): continue
                lvl, line = sg * lvl, sg * line
                if not near(i, lvl): continue
                rows.append(dict(source="BPB", stock=s, direction="LONG" if long else "SHORT", ref=round(lvl, 2), signal_date=dates[b], date=dates[i],
                                 yahoo_open=float(O[i]), green=-1, red=-1, upper_longer=-1, lower_longer=-1))
            for n, lvl, i in shape_signals(O, H, L, C, long):                              # --- SHAPECMP signals
                e = n + 1
                if not (t0 <= d.index[e] <= t1) or not near(e, lvl): continue
                up, lo = H[n] - max(O[n], C[n]), min(O[n], C[n]) - L[n]
                rows.append(dict(source="SHAPE", stock=s, direction="LONG" if long else "SHORT", ref=round(lvl, 2), signal_date=dates[n], date=dates[e],
                                 yahoo_open=float(O[e]), green=int(C[n] > O[n]), red=int(C[n] < O[n]), upper_longer=int(up > lo), lower_longer=int(lo > up)))
    if nst == 0: raise Fatal("Yahoo download gave no data for any stock - run again later")
    r = pd.DataFrame(rows)
    print(f"Yahoo: {nst} stocks, {len(r)} candidate entry days ({(r.source == 'BPB').sum()} BPB, {(r.source == 'SHAPE').sum()} SHAPECMP)", flush=True)
    return r


# ------------------------------------------------------------------ housekeeping: state, checkpoints
def load_state():
    p = f"{OUT}/state.json"
    s = json.load(open(p)) if os.path.exists(p) else {}
    s.setdefault("done", []); s["done"] = set(s["done"])
    return s


def save_state(s):
    tmp = f"{OUT}/state.json.tmp"
    json.dump({"done": sorted(s["done"])}, open(tmp, "w")); os.replace(tmp, f"{OUT}/state.json")


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
    steps = [["git", "config", "user.name", "combo-bot"], ["git", "config", "user.email", "combo-bot@users.noreply.github.com"], ["git", "add", OUT],
             ["git", "commit", "-m", "combo progress"], ["git", "pull", "--no-rebase", "-X", "ours", "--no-edit"], ["git", "push"]]
    for c in steps:
        r = subprocess.run(c, capture_output=True, text=True)
        if r.returncode and c[1] != "commit": print(f"checkpoint: '{' '.join(c)}' failed: {(r.stdout + r.stderr)[-300:]}", flush=True); return
    print("checkpoint: progress saved to the repo", flush=True)


# ------------------------------------------------------------------ step 2: 1-minute stock candles -> entry events (all entry types)
def entries_for(u, level, long):
    """u = candles of the entry day, 09:15..09:25.  -> {entry type: entry minute (Timestamp)}."""
    out = {}
    if u.empty: return out
    idx, h, l, c = u.index, u.h.values, u.l.values, u.c.values
    m = np.array([mins_of(t) for t in idx])
    touch = (h >= level) if long else (l <= level)
    if touch.any():
        k = int(np.argmax(touch)); out["ALL"] = idx[k]
        if m[k] == E_FIRST: out["OPEN_0915"] = idx[k]
    beyond = (c >= level) if long else (c <= level)                  # 1-minute CLOSE beyond the line
    k0 = next((k for k in range(4, len(u)) if m[k] >= 9 * 60 + 20 and beyond[k] and m[k] - m[k - 4] == 4 and not beyond[k - 4:k].any()), None)
    if k0 is not None:
        out["FROM_0920_4C"] = idx[k0]
        j = next((j for j in range(k0 + 1, len(u)) if not beyond[j]), None)           # a close back on the other side ...
        if j is not None:
            k1 = next((k for k in range(j + 1, len(u)) if beyond[k]), None)             # ... and the re-cross is the entry
            if k1 is not None: out["RECROSS_0920_4C"] = idx[k1]
    return out


def step_events(dh, cand, mst, st):
    ep = f"{OUT}/events.csv"
    ev = pd.read_csv(ep).to_dict("records") if os.path.exists(ep) else []
    tasks, expected = [], []
    c2 = cand[cand.stock.isin(mst)].copy(); c2["d"] = pd.to_datetime(c2["date"]).dt.date
    for s, g in c2.groupby("stock"):
        for d0, d1 in clusters(g.d.unique().tolist(), B.EQ_SPAN, B.EQ_GAP):
            key = f"EQ|{START}|{END}|{s}|{d0}|{d1}"; expected.append(key)
            if key not in st["done"]: tasks.append((s, g[(g.d >= d0) & (g.d <= d1)], d0, d1, key))
    st["expected"] = sorted(set(st.get("expected", [])) | set(expected))
    miss = sorted(set(cand.stock) - set(mst))
    if miss: print(f"not in Dhan stock-option list - skipped: {miss}", flush=True)
    print(f"Dhan stock-candle work: {len(tasks)} request groups to do ({len(expected) - len(tasks)} already done)", flush=True)

    def work(t):
        s, g, d0, d1, key = t
        u_all = eq_minute(dh, mst[s][0], d0, d1)
        if u_all is None: return None
        if u_all.empty: return [], 0
        mm = u_all.index.hour.values * 60 + u_all.index.minute.values
        u_all = u_all[(mm >= E_FIRST) & (mm <= E_LAST)]
        days = {k: v for k, v in u_all.groupby(u_all.index.date)}
        out = []
        for r in g.itertuples():
            u = days.get(r.d)
            if u is None or u.empty: continue
            ratio = float(u.o.iloc[0]) / float(r.yahoo_open)
            lvl = float(r.ref) * (ratio if abs(ratio - 1) > .2 else 1.0)                 # split / bonus: Yahoo adjusted, Dhan raw
            es = entries_for(u, lvl, r.direction == "LONG")
            for typ, m in es.items():
                if r.source == "BPB" and typ != "ALL": continue                          # BPB = first touch only (as in bpb_fno_backtest.py)
                out.append(dict(source=r.source, stock=s, direction=r.direction, type=typ, date=r.date, ref=round(lvl, 2), signal_date=r.signal_date,
                                green=r.green, red=r.red, upper_longer=r.upper_longer, lower_longer=r.lower_longer,
                                entry_minute=hm(m), stock_price=float(u.c[m])))
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


# ------------------------------------------------------------------ step 3: ATM option candles -> one minute path per entry
def build_path(e, allr, lot, strict):
    """One entry (stock, direction, date, entry minute) -> ('ok', record) | ('retry', None) | ('skip', reason)."""
    D = allr.get(e.d)
    if D is None: return "skip", "no ATM candle at the entry minute"
    atm = D[D.off == 0].drop_duplicates("ts").sort_values("ts")
    m = pd.Timestamp(f"{e.date} {e.entry_minute}")
    a = atm[atm.ts >= m]
    if a.empty or (a.ts.iloc[0] - m) > pd.Timedelta(minutes=3): return "skip", "no ATM candle at the entry minute"
    te, K, entry = a.ts.iloc[0], float(a.strike.iloc[0]), float(a.c.iloc[0])
    if not entry > 0: return "skip", "zero price"
    if mins_of(te) >= X_MIN: return "skip", "entry at/after the exit time"
    ser = D[(D.strike == K) & (D.ts > te)].drop_duplicates("ts").sort_values("ts")
    mins = ser.ts.dt.hour.values * 60 + ser.ts.dt.minute.values
    amins = atm.ts.dt.hour.values * 60 + atm.ts.dt.minute.values
    expected = int(((atm.ts > te).values & (amins <= X_MIN)).sum())
    if strict and expected and (mins <= X_MIN).sum() < 0.98 * expected: return "retry", None
    w = ser[mins <= X_MIN]
    if w.empty: return "skip", "no option candles between entry and exit"
    wm = w.ts.dt.hour.values * 60 + w.ts.dt.minute.values
    path = [[int(x), round(float(o), 2), round(float(h), 2), round(float(l), 2), round(float(c), 2)] for x, o, h, l, c in zip(wm, w.o, w.h, w.l, w.c)]
    return "ok", dict(stock=e.stock, direction=e.direction, date=e.date, entry_minute=e.entry_minute, entry_time=hm(te), strike=K, entry_price=round(entry, 2), lot=lot, path=json.dumps(path, separators=(",", ":")))


def work_options(dh, mst, t):
    s, dr, g, d0, d1, key = t
    sid, lot = mst[s][0], mst[s][1]
    x0 = rolling(dh, sid, d0, d1 + timedelta(days=1), dr, 0)
    if x0 is None or "strike" not in x0:
        return [], [(e.stock, e.direction, e.date, e.entry_minute, "Dhan returned no option candles for this period") for e in g.itertuples()]
    x0["off"] = 0
    allr = B.prep_series([x0])
    rows, skips, retry = [], [], []
    def note(e, r): skips.append((e.stock, e.direction, e.date, e.entry_minute, r))
    for e in g.itertuples():
        s_, r = build_path(e, allr, lot, True)
        if s_ == "ok": rows.append(r)
        elif s_ == "retry": retry.append(e)
        else: note(e, r)
    if retry:
        if EXTRA:
            series = [x0]
            for a, b in clusters([e.d for e in retry], 30, OPT_GAP):
                for off in EXTRA:
                    x = rolling(dh, sid, a, b + timedelta(days=1), dr, off)
                    if x is not None: x["off"] = off; series.append(x)
            allr = B.prep_series(series)
        for e in retry:
            s_, r = build_path(e, allr, lot, False)
            if s_ == "ok": rows.append(r)
            else: note(e, r)
    return rows, skips


def step_options(dh, ev, mst, st):
    os.makedirs(f"{OUT}/parts", exist_ok=True); os.makedirs(f"{OUT}/skipped", exist_ok=True)
    tasks, expected = [], []
    u = ev.drop_duplicates(["stock", "direction", "date", "entry_minute"]).copy()
    for (s, dr), g in u.groupby(["stock", "direction"]):
        if s not in mst: continue
        g = g.copy(); g["d"] = pd.to_datetime(g["date"]).dt.date
        for d0, d1 in clusters(g.d.unique().tolist(), 30, OPT_GAP):
            sub = g[(g.d >= d0) & (g.d <= d1)]
            key = f"OPT|{s}|{dr}|{d0}|{d1}|{zlib.crc32(','.join(sorted(sub.date + '_' + sub.entry_minute)).encode()):08x}"; expected.append(key)   # new entry minutes -> new key
            if key not in st["done"]: tasks.append((s, dr, sub, d0, d1, key))
    st["expected"] = sorted(set(st.get("expected", [])) | set(expected))
    print(f"Dhan option work: {len(tasks)} request groups to do ({len(expected) - len(tasks)} already done)", flush=True)

    def work(t):
        rows, skips = work_options(dh, mst, t)
        s, dr, g, d0, d1, key = t
        if rows: pd.DataFrame(rows, columns=PCOLS).to_csv(f"{OUT}/parts/{s}_{dr}_{d0}_{d1}.csv.gz", index=False, compression={"method": "gzip", "compresslevel": 1})
        if skips: pd.DataFrame(skips, columns=["stock", "direction", "date", "entry_minute", "reason"]).to_csv(f"{OUT}/skipped/{s}_{dr}_{d0}_{d1}.csv", index=False)
        return len(rows), len(skips)

    def handle(t, res):
        s, dr, g, d0, d1, key = t
        st["done"].add(key); flush(st); checkpoint()
        print(f"options {s} {dr} {d0}..{d1}: {len(g)} entries, {res[0]} paths saved, {res[1]} skipped, calls {dh.n}", flush=True)

    FLUSHER[0] = lambda: flush(st, force=True)
    try: stream(tasks, work, handle)
    finally: flush(st, force=True)


# ------------------------------------------------------------------ step 4: trade curves + day stop-loss simulation (no API calls)
def trade_curve(entry, em, path, sl_pct):
    """Per-unit option price on every grid minute (>= entry minute), the trade's own exit (minute, price, reason).
    Stop-loss: first candle whose low touches it (gap through it fills at the open); otherwise the close of the last candle up to 09:30."""
    sl = entry * (1 - sl_pct / 100)
    cd = {p[0]: p for p in path}
    mark = {}; last = entry; stop = None
    for m in range(em, X_MIN + 1):
        if m > em and stop is None and m in cd:
            _, o, h, l, c = cd[m]
            if l <= sl: stop = (m, o, "STOP (gap)") if o <= sl else (m, sl, "STOP")
            else: last = c
        mark[m] = stop[1] if stop else last
    ex = stop if stop else (X_MIN, last, "TIME")
    return mark, ex


WRITE_TRADES = os.environ.get("WRITE_TRADES", "1") == "1"


def load_paths():
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    if not fs: return pd.DataFrame(columns=PCOLS)
    with ThreadPoolExecutor(8) as pool: dfs = list(pool.map(pd.read_csv, fs))
    return pd.concat(dfs, ignore_index=True).drop_duplicates(["stock", "direction", "date", "entry_minute"])


def variants(ev):
    """(label, source, shape filter, entry type) -> boolean mask over the events table."""
    out = []
    out.append(("BPB | ALL", ev.source.eq("BPB") & ev.type.eq("ALL")))
    flt = {"NO_SHAPE_RULE": lambda e: e.source.eq("SHAPE"), "PREV_GREEN": lambda e: e.source.eq("SHAPE") & e.green.eq(1), "PREV_RED": lambda e: e.source.eq("SHAPE") & e.red.eq(1),
           "UPPER_WICK_LONGER": lambda e: e.source.eq("SHAPE") & e.upper_longer.eq(1), "LOWER_WICK_LONGER": lambda e: e.source.eq("SHAPE") & e.lower_longer.eq(1)}
    for sh in SHAPES:
        for ty in TYPES: out.append((f"SHAPECMP | {sh} | {ty}", flt[sh](ev) & ev.type.eq(ty)))
    return out


def simulate_day(P, em_idx, X):
    """P = pnl matrix (trades x grid minutes, 0 before entry), em_idx = entry column of each trade.  Returns (day pnl, trades taken, hit column or -1)."""
    if X <= 0: return float(P[:, -1].sum()), len(P), -1
    entered = np.arange(P.shape[1])[None, :] >= em_idx[:, None]
    tot = np.where(entered, P, 0.0).sum(axis=0)
    hit = np.nonzero(tot <= -X)[0]
    if hit.size == 0: return float(tot[-1]), len(P), -1
    t = int(hit[0]); taken = em_idx <= t
    return float(P[taken, t].sum()), int(taken.sum()), t


def prepare(ev, paths):
    ev = ev[(ev.date >= START) & (ev.date <= END)].copy()
    j = ev.merge(paths, on=["stock", "direction", "date", "entry_minute"], how="inner")
    print(f"Simulating: {len(ev):,} events, {len(j):,} with option paths", flush=True)
    j["em"] = j.entry_time.map(to_min); j["pth"] = j.path.map(json.loads)
    j["lots"] = (CAP // (j.entry_price * j.lot)).astype(int)
    j = j[j.lots >= 1].reset_index(drop=True)                       # one lot dearer than the capital -> trade skipped
    curves = {}
    for r in j.drop_duplicates(["stock", "direction", "date", "entry_minute"]).itertuples():
        for sl in SLS: curves[(r.stock, r.direction, r.date, r.entry_minute, sl)] = trade_curve(r.entry_price, r.em, r.pth, sl)
    return j, curves


def main_simulation(ev, paths):
    j, curves = prepare(ev, paths)
    daily, trade_rows = [], []
    ev_masks = variants(j)
    for label, mask in ev_masks:
        g = j[mask]
        if g.empty: continue
        for sl in SLS:
            for date_, gd in g.groupby("date"):
                P = np.zeros((len(gd), len(GRID))); emi = np.zeros(len(gd), dtype=int); meta = []
                for k, r in enumerate(gd.itertuples()):
                    mark, ex = curves[(r.stock, r.direction, r.date, r.entry_minute, sl)]
                    qty = r.lot * r.lots; emi[k] = r.em - E_FIRST
                    for c, m in enumerate(GRID):
                        P[k, c] = (mark[m] - r.entry_price) * qty if m >= r.em else 0.0
                    meta.append((r.stock, r.direction, r.entry_time, r.entry_price, r.lots, round(r.entry_price * qty), ex, qty))
                cost = np.array([x[5] for x in meta], dtype=float)
                for X in DAY_SLS:
                    pnl, taken, t = simulate_day(P, emi, X)
                    daily.append((label, sl, X, date_, round(pnl), taken, int(t >= 0), float(cost[emi <= t].sum() if t >= 0 else cost.sum())))
                    if X == 0 and WRITE_TRADES:
                        for k, (s, dr, et, ep, lots, cst, ex, qty) in enumerate(meta):
                            trade_rows.append((label, s, dr, date_, et, ep, lots, cst, sl, f"{ex[0] // 60:02d}:{ex[0] % 60:02d}", ex[1], ex[2], round(P[k, -1])))
    d = pd.DataFrame(daily, columns=["variant", "sl", "day_sl", "date", "pnl", "trades", "day_sl_hit", "capital"])
    t = pd.DataFrame(trade_rows, columns=["variant", "stock", "direction", "date", "entry_time", "entry_price", "lots", "cost", "sl", "exit_time", "exit_price", "reason", "pnl"])
    return d, t


def max_dd(x):
    c = np.cumsum(x); return int((c - np.maximum.accumulate(np.concatenate([[0], c]))[1:]).min()) if len(c) else 0


def summarise(d, keys):
    rows = []
    for k, g in d.groupby(keys):
        p = g.pnl.values; cap = g.capital.sum()
        rows.append(dict(zip(keys, k if isinstance(k, tuple) else (k,)),
                         trades=int(g.trades.sum()), days=len(g), day_sl_hit_days=int(g.day_sl_hit.sum()), win_days_pct=round((p > 0).mean() * 100, 1),
                         total_pnl=int(p.sum()), capital=int(cap), roi_pct=round(p.sum() / cap * 100, 2) if cap else np.nan, avg_day_pnl=int(p.mean()),
                         best_day=int(p.max()), worst_day=int(p.min()), max_drawdown=max_dd(g.sort_values("date").pnl.values),
                         profit_factor=round(p[p > 0].sum() / -p[p < 0].sum(), 2) if (p < 0).any() else np.nan))
    return pd.DataFrame(rows)


def summary():
    paths = load_paths(); ep = f"{OUT}/events.csv"
    if paths.empty or not os.path.exists(ep): print("No saved option data yet - run the backtest first.", flush=True); return
    ev = pd.read_csv(ep)
    d, t = main_simulation(ev, paths)
    if d.empty: print(f"No trades with entry dates {START}..{END}", flush=True); return
    d["day_sl"] = d.day_sl.astype(int)
    d.to_csv(f"{OUT}/daily_pnl.csv.gz", index=False, compression="gzip")
    if len(t): t.to_csv(f"{OUT}/trades_no_day_sl.csv.gz", index=False, compression="gzip")
    keys = ["variant", "sl", "day_sl"]
    s = summarise(d, keys).sort_values("roi_pct", ascending=False); s.to_csv(f"{OUT}/summary.csv", index=False)
    s.pivot_table(index=["variant", "sl"], columns="day_sl", values="roi_pct").rename(columns=lambda x: "no_day_sl" if x == 0 else f"day_sl_{x}").to_csv(f"{OUT}/roi_matrix.csv")
    d["year"], d["month"] = d.date.str[:4], d.date.str[:7]
    summarise(d, keys + ["year"]).to_csv(f"{OUT}/summary_by_year.csv", index=False)
    summarise(d, keys + ["month"]).to_csv(f"{OUT}/summary_by_month.csv", index=False)
    cols = ["variant", "sl", "day_sl", "trades", "days", "day_sl_hit_days", "total_pnl", "roi_pct", "max_drawdown", "worst_day", "profit_factor"]
    print(f"\n{START} .. {END}: {len(s)} combinations (variant x trade SL x day SL; day_sl 0 = no day stop-loss)\n\nBEST 20 BY ROI (min 30 trades):\n"
          + s[s.trades >= 30].head(20)[cols].to_string(index=False), flush=True)
    nd = s[s.day_sl == 0].set_index(["variant", "sl"]); wd = s[s.day_sl > 0]
    wd = wd.join(nd[["total_pnl", "max_drawdown"]].add_prefix("no_day_sl_"), on=["variant", "sl"])
    wd.assign(pnl_change=wd.total_pnl - wd.no_day_sl_total_pnl).to_csv(f"{OUT}/day_sl_vs_no_day_sl.csv", index=False)
    report(len(d))


def report(n):
    ep = f"{OUT}/events.csv"; ev = pd.read_csv(ep) if os.path.exists(ep) else pd.DataFrame()
    lines = [f"Range {START} .. {END}; universe {len(UNIVERSE)} stocks; entry 09:15-09:25; exit 09:30; trade SL {SLS}; capital per trade Rs {CAP}; day SL {DAY_SLS} (0 = none)"]
    if len(ev):
        ev = ev[(ev.date >= START) & (ev.date <= END)]
        lines.append("Entry events: " + "; ".join(f"{k[0]}/{k[1]} = {v}" for k, v in ev.groupby(["source", "type"]).size().items()))
    sk = sorted(glob.glob(f"{OUT}/skipped/*.csv"))
    if sk:
        k = pd.concat([pd.read_csv(f) for f in sk], ignore_index=True).drop_duplicates(["stock", "direction", "date", "entry_minute"])
        lines.append(f"Entries with NO option path: {len(k)} - " + "; ".join(f"{r} = {c}" for r, c in k.reason.value_counts().items()))
    open(f"{OUT}/REPORT.txt", "w").write("\n".join(lines) + "\n"); print("\n" + "\n".join(lines), flush=True)


def progress():
    st = load_state(); exp = set(st.get("expected", []))
    if not exp: return
    done = len(exp & st["done"])
    msg = f"COMPLETE - all {len(exp)} request groups finished." if done >= len(exp) else f"PARTIAL - {done} of {len(exp)} request groups finished. Run again to continue."
    open(f"{OUT}/PROGRESS.txt", "w").write(msg + "\n"); print("\n*** " + msg + " ***", flush=True)


# ------------------------------------------------------------------ modes
def check():
    dh = Dhan(); mst = load_master()
    print(f"Instrument list OK: {len(mst)} stocks with options. RELIANCE ->", mst.get("RELIANCE"), flush=True)
    print(f"Universe {len(UNIVERSE)} stocks, {len([s for s in UNIVERSE if s not in mst])} not in Dhan's list: {[s for s in UNIVERSE if s not in mst]}", flush=True)
    sid = mst["RELIANCE"][0]; d1 = date.today(); d0 = d1 - timedelta(days=10)
    u = eq_minute(dh, sid, d0, d1); print("Stock minute call:", "no data" if u is None else f"{len(u)} candles")
    x = rolling(dh, sid, d0, d1, "LONG", 0); print("Rolling option call:", "no data" if x is None else f"{len(x)} candles")
    B.print_stats(dh)


def run():
    os.makedirs(OUT, exist_ok=True); st = load_state()
    cp = f"{OUT}/candidates_{START}_{END}.csv"
    if os.path.exists(cp): cand = pd.read_csv(cp)
    else:
        cand = yahoo_candidates()
        if cand.empty: print("No candidate days in this range."); return
        cand.to_csv(cp, index=False)
    print(f"Candidate days {START}..{END}: {len(cand)}", flush=True)
    dh = Dhan(); mst = load_master()
    try:
        ev = step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= START) & (ev["date"] <= END)] if len(ev) else ev
        print(f"Entry events (09:15-09:25): {len(ev)}", flush=True)
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
        elif mode in ("summary", "range"): os.makedirs(OUT, exist_ok=True); progress(); summary()
        else: sys.exit("use: python combo_dayrisk_backtest.py check | run | summary")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
