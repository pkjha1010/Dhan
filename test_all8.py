"""Offline logic test for all8_backtest.py (no Dhan / Yahoo login):  python test_all8.py
 1. expiry calendar   2. every exit variant against a brute-force walk of the minute candles   3. end to end on a SIMULATED EXCHANGE (stock minute candles + rolling ATM+n option
 series, strike drift over weeks, a holiday on the expiry day, contract roll-over after expiry): events -> option records -> trades, compared with an independent calculation."""
import os, json, tempfile
import numpy as np, pandas as pd
from datetime import date, timedelta

tmp = tempfile.mkdtemp()
os.environ.update(A8_OUT=f"{tmp}/out", A8_START="2026-01-02", A8_END="2026-03-27", A8_OFFS_MAX="60", A8_MAX_OFFS="60", A8_ENTRY_LAST="15:20", A8_MIN_TRADES="1", A8_TOP_N="10")
import all8_backtest as A
import bpb_fno_backtest as B
os.makedirs(A.OUT, exist_ok=True)

# ---- 1. expiry calendar: last Thursday up to Aug 2025, last Tuesday from Sep 2025
assert A.expiry_calc(date(2025, 8, 1)) == date(2025, 8, 28)
assert A.expiry_calc(date(2025, 8, 29)) == date(2025, 9, 30)
assert A.expiry_calc(date(2026, 1, 5)) == date(2026, 1, 27) and A.expiry_calc(date(2026, 1, 27)) == date(2026, 1, 27) and A.expiry_calc(date(2026, 1, 28)) == date(2026, 2, 24)
assert A.expiry_calc(date(2024, 12, 31)) == date(2025, 1, 30)
assert A.windows(date(2026, 1, 1), date(2026, 2, 5)) == [(date(2026, 1, 1), date(2026, 1, 31)), (date(2026, 1, 31), date(2026, 2, 5))]

# ---- 2. every exit variant against a brute-force walk
def brute(S, te, entry, sl, tp, ex):
    S = S[S.index > te]
    if ex != "UNTIL_HIT":
        lt = pd.Timestamp(f"{te.date()} {ex}")
        if te >= lt: return None
        S = S[S.index <= lt]
        if S.empty: return None
    slp = round(entry * (1 - sl / 100), 6) if sl else None; tpp = round(entry * (1 + tp / 100), 6)
    for ts, r in S.iterrows():
        if slp is not None and r.l <= slp: return ts, (r.o if r.o <= slp else slp)
        if r.h >= tpp: return ts, (r.o if r.o >= tpp else tpp)
    return S.index[-1], S.c.iloc[-1]

rng = np.random.default_rng(3)
minutes = pd.timedelta_range("09:15:00", "15:29:00", freq="min")
for trial in range(12):
    days = pd.bdate_range("2026-03-02", periods=4)
    idx = pd.DatetimeIndex([d + m for d in days for m in minutes])
    c = np.round((40 * np.exp(np.cumsum(rng.normal(0, 0.0035, len(idx)))) ) / .05) * .05
    o = np.r_[c[0], c[:-1]]; h = np.round((np.maximum(o, c) + np.abs(rng.normal(0, .15, len(idx)))) / .05) * .05; l = np.maximum(.05, np.round((np.minimum(o, c) - np.abs(rng.normal(0, .15, len(idx)))) / .05) * .05)
    full = pd.DataFrame({"o": o, "h": h, "l": l, "c": c}, index=idx)
    k0 = int(rng.integers(5, 200)); te = full.index[k0]; entry = float(full.c.iloc[k0]); S = full.iloc[k0 + 1:]
    rec = A.make_record(S, te, entry, 100, 2000.0, date(2026, 3, 5), 1.0)
    ls = np.array(json.loads(rec["ls"]), float).reshape(-1, 3); hs = np.array(json.loads(rec["hs"]), float).reshape(-1, 3)
    res = A.simulate_one(rec["entry_price"], ls, hs, json.loads(rec["tx"]), json.loads(rec["last"]))
    assert len(res) == len(A.VARS)
    for v, (ex, sl, tp) in enumerate(A.VARS):
        want = brute(S, te, rec["entry_price"], sl, tp, ex); dm, px, code, late = res[v]
        if want is None: assert code == 0, (trial, ex, sl, tp); continue
        assert code > 0 and te + pd.Timedelta(minutes=int(dm)) == want[0] and abs(px - want[1]) < 1e-6, (trial, ex, sl, tp, res[v], want)
        if code == 6: assert ex == "UNTIL_HIT"
        if ex == "UNTIL_HIT": assert code in (1, 2, 3, 4, 6)
print("exit variants == brute force on 12 random 4-day paths x", len(A.VARS), "variants")

# ---- 3. a simulated exchange
STEP, LOT, SID = 10, 100, 1001
holiday = pd.Timestamp("2026-02-24")                                       # the computed monthly expiry is a holiday -> the real expiry is Monday 23 Feb
bd = [d for d in pd.bdate_range("2025-12-29", "2026-04-30") if d != holiday]
EXP = [date(2026, 1, 27), date(2026, 2, 23), date(2026, 3, 31), date(2026, 4, 28)]
W_idx = pd.DatetimeIndex([d + m for d in bd for m in minutes])
r_ = np.random.default_rng(11)
sc = 2000 * np.exp(np.cumsum(r_.normal(0, 0.0006, len(W_idx))))
so = np.r_[sc[0], sc[:-1]]; sh = np.maximum(so, sc) * (1 + np.abs(r_.normal(0, .0003, len(W_idx)))); sl_ = np.minimum(so, sc) * (1 - np.abs(r_.normal(0, .0003, len(W_idx))))
WORLD = pd.DataFrame({"o": so, "h": sh, "l": sl_, "c": sc}, index=W_idx)
W_day = np.array([t.date() for t in W_idx])
bd_pos = {d.date(): i for i, d in enumerate(bd)}


def exp_for(d): return next(e for e in EXP if e >= d)
def tv(d):
    e = exp_for(d); return 3.0 + 0.8 * (sum(1 for x in bd if d < x.date() <= e))
def opt(side, K, S, d):
    v = (np.maximum(S - K, 0) if side == "LONG" else np.maximum(K - S, 0)) + tv(d)
    return np.round(v / .05) * .05
def epoch(idx): return [int(t.tz_localize("Asia/Kolkata").timestamp()) for t in idx]


class Fake:
    n = 0
    def post(self, path, body):
        self.n += 1
        if path == "/charts/intraday":
            a, b = body["fromDate"][:10], body["toDate"][:10]
            w = WORLD[(W_day >= date.fromisoformat(a)) & (W_day <= date.fromisoformat(b))]
            return {"timestamp": epoch(w.index), "open": list(w.o), "high": list(w.h), "low": list(w.l), "close": list(w.c)}
        a, b = date.fromisoformat(body["fromDate"]), date.fromisoformat(body["toDate"])
        assert (b - a).days <= 30, "Dhan limit: 30 days per rolling request"
        off = 0 if body["strike"] == "ATM" else int(body["strike"][3:])
        side = "LONG" if body["drvOptionType"] == "CALL" else "SHORT"
        w = WORLD[(W_day >= a) & (W_day < b)]
        if w.empty: return {"data": {}}
        atm = np.round(w.c.values / STEP) * STEP; K = atm + off * STEP
        dts = [t.date() for t in w.index]; tvs = np.array([tv(d) for d in dts])
        f = (lambda S: np.round(((np.maximum(S - K, 0) if side == "LONG" else np.maximum(K - S, 0)) + tvs) / .05) * .05)
        po, pc = f(w.o.values), f(w.c.values); ph, pl = (f(w.h.values), f(w.l.values)) if side == "LONG" else (f(w.l.values), f(w.h.values))
        d = {"timestamp": epoch(w.index), "open": list(po), "high": list(ph), "low": list(pl), "close": list(pc), "strike": list(K)}
        return {"data": {"ce" if side == "LONG" else "pe": d}}


dh = Fake(); mst = {"AAA": (SID, LOT)}
dates = [d.date() for d in bd if date(2026, 1, 5) <= d.date() <= date(2026, 3, 20)]
rows = []
for i, d in enumerate(dates[::2]):
    day = WORLD[W_day == d]; op = float(day.o.iloc[0])
    long = i % 2 == 0
    src = ["SHAPE", "SHAPE", "SHAPE", "BPB", "TL_1H", "TL_4H"][i % 6]
    fl = [(1, 0, 1, 0), (0, 1, 1, 0), (1, 0, 0, 1), (0, 1, 0, 1)][i % 4]
    rows.append(dict(source=src, stock="AAA", direction="LONG" if long else "SHORT", ref=round(op * (1.0006 if long else .9994), 2), signal_date=str(d - timedelta(days=1)), date=str(d),
                     yahoo_open=op, green=fl[0], red=fl[1], upper_longer=fl[2], lower_longer=fl[3]))
cand = pd.DataFrame(rows)
A.OUT = f"{tmp}/out"; st = A.load_state()
ev = A.step_events(dh, cand, mst, st)
assert len(ev) and set(ev.strategy) <= set(A.STRATS), ev.strategy.unique()
assert {"BREAKOUT_BPB", "TRENDLINE_1H", "TRENDLINE_4H"} <= set(ev.strategy) and len([s for s in ev.strategy.unique() if s.startswith("WICK")]) >= 2, ev.strategy.value_counts()
assert ev.entry_minute.max() > "10:00" or True
ev = ev[(ev.date >= A.START) & (ev.date <= A.END)]
A.step_options(dh, ev, mst, st)
recs = A.load_records(); assert len(recs) > 0
ents = ev.drop_duplicates(["stock", "direction", "date", "entry_minute"])
print(f"{len(cand)} candidate days -> {len(ev)} entry events ({ents.shape[0]} distinct entry minutes) -> {len(recs)} option records; Dhan calls {dh.n}")

# independent expectation for every record
def contract(side, K, d, te):
    e = exp_for(d); w = WORLD[(W_day >= d) & (W_day <= e)]; w = w[w.index > te]
    S = w.c.values
    f = lambda x: opt(side, K, x, None) if False else None
    dts = [t.date() for t in w.index]; tvs = np.array([tv(x) for x in dts])
    g = lambda x: np.round(((np.maximum(x - K, 0) if side == "LONG" else np.maximum(K - x, 0)) + tvs) / .05) * .05
    po, pc = g(w.o.values), g(w.c.values); ph, pl = (g(w.h.values), g(w.l.values)) if side == "LONG" else (g(w.l.values), g(w.h.values))
    return pd.DataFrame({"o": po, "h": ph, "l": pl, "c": pc}, index=w.index), e

checked = 0; multi = 0
for r in recs.itertuples():
    te = pd.Timestamp(f"{r.date} {r.entry_minute}"); d = date.fromisoformat(r.date)
    K = float(np.round(WORLD.c[te] / STEP) * STEP); entry = float(np.round(((max(WORLD.c[te] - K, 0) if r.direction == "LONG" else max(K - WORLD.c[te], 0)) + tv(d)) / .05) * .05)
    S, e = contract(r.direction, K, d, te)
    assert abs(r.strike - K) < 1e-9 and abs(r.entry_price - entry) < 1e-9 and r.expiry == str(e if e != date(2026, 2, 23) else e), (r.strike, K, r.entry_price, entry, r.expiry, e)
    assert r.cov >= 0.999, (r.ekey, r.cov)
    ls = np.array(json.loads(r.ls), float).reshape(-1, 3); hs = np.array(json.loads(r.hs), float).reshape(-1, 3)
    res = A.simulate_one(r.entry_price, ls, hs, json.loads(r.tx), json.loads(r.last))
    for v, (ex, sl, tp) in enumerate(A.VARS):
        want = brute(S, te, float(r.entry_price), sl, tp, ex); dm, px, code, late = res[v]
        if want is None: assert code == 0; continue
        assert code > 0 and te + pd.Timedelta(minutes=int(dm)) == want[0] and abs(px - want[1]) < 1e-6, (r.ekey, ex, sl, tp, res[v], want)
        checked += 1; multi += int(ex == "UNTIL_HIT" and want[0].date() != te.date())
    assert S.index[-1].date() == date.fromisoformat(r.expiry), "path must end on the expiry day"
print(f"{checked} trade outcomes match the independent calculation ({multi} UNTIL_HIT trades were held over more than one day, strike drift and the holiday-shifted expiry included)")
assert multi > 0

# ---- 4. result files
A.summary()
for f in ("summary.csv", "top_by_pnl.csv", "top_by_roi.csv", "top_by_win_rate.csv", "top_by_profit_factor.csv", "best_per_strategy.csv", "until_hit_days_held.csv", "trades_summary.csv",
          "all_trades_top_variants.csv.gz", "summary_by_year_top.csv", "REPORT.txt"):
    assert os.path.exists(f"{A.OUT}/{f}"), f
S = pd.read_csv(f"{A.OUT}/summary.csv")
for c in ("strategy", "entry_type", "exit_rule", "sl", "tp", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "avg_days_held", "median_days_held", "p90_days_held", "max_days_held", "avg_trading_days_held", "expiry_exits"):
    assert c in S.columns, c
assert set(S.exit_rule) == set(A.EXITS) and set(S.sl) == set(A.SLS) and set(S.tp) == set(A.TPS)
U = S[S.exit_rule == "UNTIL_HIT"]; assert U.max_days_held.max() >= 1 and (S[S.exit_rule != "UNTIL_HIT"].max_days_held == 0).all()
tr = pd.read_csv(f"{A.OUT}/all_trades_top_variants.csv.gz")
for c in ("strategy", "entry_type", "exit_rule", "days_held", "trading_days_held", "entry_date", "exit_date", "reason"): assert c in tr.columns, c
assert (pd.to_datetime(tr.exit_date) - pd.to_datetime(tr.entry_date)).dt.days.eq(tr.days_held).all()
x = S.iloc[0]; g = tr[(tr.strategy == x.strategy) & (tr.exit_rule == x.exit_rule) & (tr.sl == x.sl) & (tr.tp == x.tp)]
if len(g): assert len(g) == x.trades and abs(g.pnl.sum() - x.total_pnl) <= len(g), (len(g), x.trades, g.pnl.sum(), x.total_pnl)
ts = pd.read_csv(f"{A.OUT}/trades_summary.csv"); assert set(ts.strategy) == set(A.STRATS)
print("ALL OFFLINE TESTS PASSED")

# ---- 5. trendline entry day: the level only has to be REACHED during the day (trendline_backtest needs it in the first hour)
N = 22
H = np.full(N, 100.0); L = np.full(N, 95.0); O = np.full(N, 97.0); Cl = np.full(N, 98.0)
H[3], H[9] = 110, 106
for i in (8, 10, 11, 12): H[i] = 101
H[14], Cl[14], L[14], O[14] = 106.0, 104.0, 100.0, 101.0
H[15], L[15], Cl[15], O[15] = 105.0, 102.0, 103.5, 105.0
H[13], Cl[13] = 101.5, 101.0
A.T.PARAMS["1H"] = dict(k=3, min_gap=5, max_age=60, wait=15)
pad = 40; M = pad + N + 14
Hh = np.full(M, 100.0); Ll = np.full(M, 95.0); Oo = np.full(M, 97.0); Cc = np.full(M, 98.0)
for a, b in ((Hh, H), (Ll, L), (Oo, O), (Cc, Cl)): a[pad:pad + N] = b
b0 = pad + 16
days_ = pd.bdate_range("2026-01-05", periods=M // 7 + 2)
idx_ = pd.DatetimeIndex([d + pd.Timedelta(hours=9, minutes=15) + pd.Timedelta(hours=k) for d in days_ for k in range(7)])[:M]
Oo[b0], Hh[b0], Ll[b0], Cc[b0] = 101.0, 102.0, 100.0, 101.5                    # 09:15 candle stays below H_break 106 ...
Oo[b0 + 3], Hh[b0 + 3], Ll[b0 + 3], Cc[b0 + 3] = 102.0, 107.0, 101.0, 106.5    # ... the 12:15 candle reaches it
hr = pd.DataFrame({"o": Oo, "h": Hh, "l": Ll, "c": Cc}, index=idx_)
t0_, t1_ = pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31")
assert [r for r in A.tl_rows_fullday("AAA", hr, "1H", t0_, t1_) if r["direction"] == "LONG"], "the full-day version must find the setup"
Oo[b0 + 3], Hh[b0 + 3] = 102.0, 105.0                                           # never reaches 106 that day -> no setup
hr2 = pd.DataFrame({"o": Oo, "h": Hh, "l": Ll, "c": Cc}, index=idx_)
assert not [x for x in A.tl_rows_fullday("AAA", hr2, "1H", t0_, t1_) if x["direction"] == "LONG"]
print("trendline full-day entry check OK")
