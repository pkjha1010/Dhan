"""Offline logic test for recross10_backtest.py (no Dhan / Yahoo login):  python test_recross10.py
 1. the re-cross rule on hand-made minute paths (fake breakouts, gaps in the data, SHORT mirror)
 2. the rule against an independent state machine on thousands of random paths
 3. the strategy mapping (exactly the 10 strategies) and the exit grid (no / 20 / 40 / 60 SL x no / 20 / 40 / 60 / 80 TP x 4 time exits) against a brute-force walk
 4. end to end on a SIMULATED EXCHANGE: stock minute candles + option series -> re-cross entries -> option records -> trades -> SUMMARY.md and the 10 trade files."""
import os, json, tempfile
import numpy as np, pandas as pd
from datetime import date, timedelta

tmp = tempfile.mkdtemp()
os.environ.update(R10_OUT=f"{tmp}/out", R10_START="2026-01-02", R10_END="2026-03-27", R10_MIN_TRADES="1", R10_ENTRY_LAST="15:20",
                  A8_OFFS_MAX="60", A8_MAX_OFFS="60", A8_TOP_N="10")
import recross10_backtest as R
A = R.A
os.makedirs(A.OUT, exist_ok=True)

# ---------------------------------------------------------------- 1. hand-made paths
D0 = pd.Timestamp("2026-03-03")


def mk(closes, start="09:15", drop=(), highs=None):
    idx = [D0 + pd.Timedelta(hours=int(start[:2]), minutes=int(start[3:]) + i) for i in range(len(closes))]
    c = np.array(closes, float); h = np.array(highs if highs is not None else closes, float)
    df = pd.DataFrame({"o": c, "h": np.maximum(h, c), "l": c, "c": c}, index=pd.DatetimeIndex(idx))
    return df.drop(df.index[list(drop)]) if drop else df


LV = 100.0
#          09:15 09:16 09:17 09:18 09:19 | 09:20 break | 09:21 back | 09:22 | 09:23 | 09:24 | 09:25 -> entry
base = [99.0, 99.2, 99.3, 99.4, 99.5, 100.10, 99.8, 100.10, 99.9, 100.1, 100.2, 100.3]
u = mk(base)
assert R.recross_entry(u, LV, True) == 10, R.recross_entry(u, LV, True)            # two closes beyond the line after the pullback; the 09:22 single close does not count
assert u.index[10].strftime("%H:%M") == "09:25"
assert R.recross_entry(mk(base[:8]), LV, True) is None                              # only ONE close beyond the line after the pullback: fake re-cross
assert R.recross_entry(mk(base[:7]), LV, True) is None                              # break and pullback but no re-cross yet
assert R.recross_entry(mk(base[:6]), LV, True) is None                              # break only
# a wick through the line is not a break
w = [99.0, 99.2, 99.3, 99.4, 99.5, 99.9, 99.8, 99.7, 99.9, 99.8, 99.9, 99.9]            # the highs go through the line, every CLOSE stays below it
hi = list(w); hi[5] = 100.6; hi[8] = 100.7; hi[10] = 100.5
assert R.recross_entry(mk(w, highs=hi), LV, True) is None
# a close inside the band (0.03 % above the line) is not a break, and a base that touches the line is no base
w = list(base); w[5] = 100.03
assert R.recross_entry(mk(w), LV, True) is None
# the stock opens above the line and never was below it: no base, no break
assert R.recross_entry(mk([100.5, 100.6, 100.7, 100.6, 100.5, 100.6, 99.8, 100.1, 100.2]), LV, True) is None
# a dip that stays inside the band (99.97 is only 0.03 % below the line) is not a pullback: with no real pullback there is no re-cross
w = [99.0, 99.2, 99.3, 99.4, 99.5, 100.10, 99.97, 100.10, 100.2, 100.3]
assert R.recross_entry(mk(w), LV, True) is None
w2 = list(base); w2[6] = 99.97                                                      # ... and the real pullback at 09:23 (99.9) is what counts here
assert R.recross_entry(mk(w2), LV, True) == 10
# SHORT is the mirror image of LONG
assert R.recross_entry(mk([2 * LV - x for x in base]), LV, False) == 10
assert R.recross_entry(mk(base), LV, False) is None                                 # a LONG path is no SHORT path
# a missing minute: the base needs 4 CONTIGUOUS closes, the re-cross needs contiguous closes
assert R.recross_entry(mk(base, drop=[3]), LV, True) is None                        # a hole in the base (09:18 missing)
e = R.recross_entry(mk(base, drop=[9]), LV, True)                                   # 09:24 missing: 09:25 and 09:26 are contiguous -> entry at 09:26
assert e == 10 and mk(base, drop=[9]).index[e].strftime("%H:%M") == "09:26", e
w = [99.0, 99.2, 99.3, 99.4, 99.5, 100.10, 99.8, 100.1, 100.2]                     # beyond at 09:22 and 09:24 but 09:23 has no candle
assert R.recross_entry(mk(w, drop=[8]), LV, True) is None and R.recross_entry(mk(w), LV, True) == 8
# time limits
assert R.recross_entry(u, LV, True, last_min=9 * 60 + 24) is None and R.recross_entry(u, LV, True, last_min=9 * 60 + 25) == 10
assert R.recross_entry(u, LV, True, first_break=9 * 60 + 30) is None
# other settings: hold 1 = enter on the first close beyond the line after the pullback, band 0 = any close beyond
assert R.recross_entry(u, LV, True, hold_n=1) == 7 and R.recross_entry(u, LV, True, hold_n=3) == 11
assert R.recross_entry(mk([99, 99, 99, 99, 99, 100.01, 99.99, 100.01, 100.02]), LV, True, band=0.0) == 8
assert R.recross_entry(mk([99, 99, 99, 99, 99, 100.01, 99.99, 100.01, 100.02]), LV, True) is None
print("re-cross rule: hand-made paths OK")

# ---------------------------------------------------------------- 2. independent state machine on random paths
def ref_entry(c, m, level, long, band, base_n, hold_n, first_break, last_min):
    x = [((v - level) if long else (level - v)) / level for v in c]
    state, cnt, kb = 0, 0, None
    for k in range(len(c)):
        if m[k] > last_min: return None
        if state == 0:
            if k >= base_n and m[k] >= first_break and x[k] >= band and m[k] - m[k - base_n] == base_n and all(x[k - i] < 0 for i in range(1, base_n + 1)): state = 1
        elif state == 1:
            if x[k] <= -band: state, cnt = 2, 0
        else:
            if x[k] >= band:
                cnt = cnt + 1 if (cnt and m[k] - m[k - 1] == 1) else 1
                if cnt >= hold_n: return k
            else: cnt = 0
    return None


rng = np.random.default_rng(5)
hits = 0
for trial in range(4000):
    n = int(rng.integers(30, 375)); lvl = float(rng.uniform(50, 3000)); sig = float(rng.choice([0.0002, 0.0005, 0.001]))
    c = lvl * (1 + rng.normal(0, 0.0015) + np.cumsum(rng.normal(0, sig, n)))
    keep = rng.random(n) > rng.choice([0, 0.01, 0.05]); keep[0] = True
    idx = pd.DatetimeIndex([D0 + pd.Timedelta(hours=9, minutes=15 + i) for i in range(n)])[keep]
    u = pd.DataFrame({"o": c[keep], "h": c[keep], "l": c[keep], "c": c[keep]}, index=idx)
    m = u.index.hour.values * 60 + u.index.minute.values
    long = bool(rng.integers(2)); band = float(rng.choice([0.0, 0.0005, 0.001])); bn = int(rng.choice([2, 4])); hn = int(rng.choice([1, 2, 3])); lm = int(rng.choice([9 * 60 + 30, 12 * 60, 15 * 60 + 20]))
    got = R.recross_entry(u, lvl, long, band=band, base_n=bn, hold_n=hn, first_break=9 * 60 + 20, last_min=lm)
    want = ref_entry(u.c.values, m, lvl, long, band, bn, hn, 9 * 60 + 20, lm)
    assert got == want, (trial, got, want)
    hits += got is not None
assert hits > 200, hits
print(f"re-cross rule == independent state machine on 4000 random paths ({hits} with an entry)")

# ---------------------------------------------------------------- 3. strategy mapping and the exit grid
assert len(R.STRATS) == 10 and len(set(R.STRATS)) == 10 and A.STRATS == R.STRATS
assert set(R.STRATS) == {"BPB_LONG", "BPB_SHORT"} | {f"WICK_{a}_{b}_{s}" for a in ("GREEN", "RED") for b in ("UPPER", "LOWER") for s in ("LONG", "SHORT")}
assert R.strategies_for("BPB", "RC2_LONG", -1, -1, -1, -1) == ["BPB_LONG"] and R.strategies_for("BPB", "RC2_SHORT", -1, -1, -1, -1) == ["BPB_SHORT"]
assert R.strategies_for("SHAPE", "RC2_LONG", 1, 0, 1, 0) == ["WICK_GREEN_UPPER_LONG"] and R.strategies_for("SHAPE", "RC2_SHORT", 0, 1, 0, 1) == ["WICK_RED_LOWER_SHORT"]
assert R.strategies_for("SHAPE", "RC2_LONG", 0, 0, 1, 0) == [] and R.strategies_for("SHAPE", "ALL", 1, 0, 1, 0) == [] and R.strategies_for("TL_1H", "RC2_LONG", 1, 0, 1, 0) == []
assert A.SLS == [0, 20, 40, 60] and A.TPS == [0, 20, 40, 60, 80] and A.EXITS == ["09:30", "10:00", "12:00", "15:30"] and len(A.VARS) == 80
assert "UNTIL_HIT" not in A.EXITS


def brute(S, te, entry, sl, tp, ex):
    S = S[S.index > te]
    lt = pd.Timestamp(f"{te.date()} {ex}")
    if te >= lt: return None
    S = S[S.index <= lt]
    if S.empty: return None
    slp = round(entry * (1 - sl / 100), 6) if sl else None; tpp = round(entry * (1 + tp / 100), 6) if tp else None
    for ts, r in S.iterrows():
        if slp is not None and r.l <= slp: return ts, (r.o if r.o <= slp else slp)
        if tpp is not None and r.h >= tpp: return ts, (r.o if r.o >= tpp else tpp)
    return S.index[-1], S.c.iloc[-1]


rng = np.random.default_rng(3)
minutes = pd.timedelta_range("09:15:00", "15:29:00", freq="min")
for trial in range(12):
    days = pd.bdate_range("2026-03-02", periods=4)
    idx = pd.DatetimeIndex([d + m for d in days for m in minutes])
    c = np.round((40 * np.exp(np.cumsum(rng.normal(0, 0.0035, len(idx))))) / .05) * .05
    o = np.r_[c[0], c[:-1]]; h = np.round((np.maximum(o, c) + np.abs(rng.normal(0, .15, len(idx)))) / .05) * .05; l = np.maximum(.05, np.round((np.minimum(o, c) - np.abs(rng.normal(0, .15, len(idx)))) / .05) * .05)
    full = pd.DataFrame({"o": o, "h": h, "l": l, "c": c}, index=idx).round(2)
    k0 = int(rng.integers(5, 200)); te = full.index[k0]; entry = float(full.c.iloc[k0]); S = full.iloc[k0 + 1:]
    rec = A.make_record(S, te, entry, 100, 2000.0, date(2026, 3, 5), 1.0)
    ls = np.array(json.loads(rec["ls"]), float).reshape(-1, 3); hs = np.array(json.loads(rec["hs"]), float).reshape(-1, 3)
    res = A.simulate_one(rec["entry_price"], ls, hs, json.loads(rec["tx"]), json.loads(rec["last"]))
    assert len(res) == len(A.VARS) == 80
    for v, (ex, sl, tp) in enumerate(A.VARS):
        want = brute(S, te, rec["entry_price"], sl, tp, ex); dm, px, code, late = res[v]
        if want is None: assert code == 0, (trial, ex, sl, tp); continue
        assert code > 0 and te + pd.Timedelta(minutes=int(dm)) == want[0] and abs(px - want[1]) < 1e-6, (trial, ex, sl, tp, res[v], want)
        assert code in (1, 2, 3, 4, 5)
        if not sl and not tp: assert code == 5                                       # no stop and no target = a pure time exit
print("exit grid (no/20/40/60 SL x no/20/40/60/80 TP x 4 time exits = 80) == brute force on 12 random paths")

# ---------------------------------------------------------------- 4. a simulated exchange
STEP, LOT, SID = 10, 100, 1001
holiday = pd.Timestamp("2026-02-24")
bd = [d for d in pd.bdate_range("2025-12-29", "2026-04-30") if d != holiday]
EXP = [date(2026, 1, 27), date(2026, 2, 23), date(2026, 3, 31), date(2026, 4, 28)]
W_idx = pd.DatetimeIndex([d + m for d in bd for m in minutes])
r_ = np.random.default_rng(11)
sc = 2000 * np.exp(np.cumsum(r_.normal(0, 0.0006, len(W_idx))))
so = np.r_[sc[0], sc[:-1]]; sh = np.maximum(so, sc) * (1 + np.abs(r_.normal(0, .0003, len(W_idx)))); sl_ = np.minimum(so, sc) * (1 - np.abs(r_.normal(0, .0003, len(W_idx))))
WORLD = pd.DataFrame({"o": so, "h": sh, "l": sl_, "c": sc}, index=W_idx)
W_day = np.array([t.date() for t in W_idx])


def exp_for(d): return next(e for e in EXP if e >= d)
def tv(d):
    e = exp_for(d); return 3.0 + 0.8 * (sum(1 for x in bd if d < x.date() <= e))
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
        assert (b - a).days <= 30
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
FL = [("BPB", -1, -1, -1, -1), ("SHAPE", 1, 0, 1, 0), ("SHAPE", 0, 1, 1, 0), ("SHAPE", 1, 0, 0, 1), ("SHAPE", 0, 1, 0, 1)]
rows, want_min = [], {}
for i, d in enumerate(dates):
    day = WORLD[(W_day == d) & (W_idx.hour * 60 + W_idx.minute <= 15 * 60 + 20)]
    cl = day.c.values
    for long in (True, False):
        for q in np.linspace(0.05, 0.95, 19):                                    # a level for which the day really contains a re-cross
            lvl = round(float(np.quantile(cl, q)), 2)
            k = R.recross_entry(day, lvl, long)
            if k is not None: break
        else: continue
        src, g, rd, up, lo = FL[(i + (0 if long else 2)) % 5]
        rows.append(dict(source=src, stock="AAA", direction="LONG" if long else "SHORT", ref=lvl, signal_date=str(d - timedelta(days=1)), date=str(d),
                         yahoo_open=float(day.o.iloc[0]), green=g, red=rd, upper_longer=up, lower_longer=lo))
        want_min[(("LONG" if long else "SHORT"), str(d))] = day.index[k].strftime("%H:%M")
cand = pd.DataFrame(rows)
assert len(cand) > 40, len(cand)
st = A.load_state()
ev = A.step_events(dh, cand, mst, st)
assert len(ev) and set(ev.strategy) <= set(R.STRATS) and len(set(ev.strategy)) == 10, ev.strategy.value_counts()
assert set(ev.type) <= {"RC2_LONG", "RC2_SHORT"}
for r in ev.itertuples():
    assert r.entry_minute == want_min[(r.direction, r.date)], (r.strategy, r.date, r.entry_minute, want_min[(r.direction, r.date)])
    assert r.strategy.endswith("_" + r.direction)
ev = ev[(ev.date >= A.START) & (ev.date <= A.END)]
A.step_options(dh, ev, mst, st)
recs = A.load_records(); assert len(recs) > 0
print(f"{len(cand)} candidate days -> {len(ev)} re-cross entries in all 10 strategies -> {len(recs)} option records; Dhan calls {dh.n}")


def contract(side, K, d, te):
    e = exp_for(d); w = WORLD[(W_day >= d) & (W_day <= e)]; w = w[w.index > te]
    dts = [t.date() for t in w.index]; tvs = np.array([tv(x) for x in dts])
    g = lambda x: np.round(np.round(((np.maximum(x - K, 0) if side == "LONG" else np.maximum(K - x, 0)) + tvs) / .05) * .05, 2)       # 2 decimals, like real prices
    po, pc = g(w.o.values), g(w.c.values); ph, pl = (g(w.h.values), g(w.l.values)) if side == "LONG" else (g(w.l.values), g(w.h.values))
    return pd.DataFrame({"o": po, "h": ph, "l": pl, "c": pc}, index=w.index), e


checked = 0
for r in recs.itertuples():
    te = pd.Timestamp(f"{r.date} {r.entry_minute}"); d = date.fromisoformat(r.date)
    K = float(np.round(WORLD.c[te] / STEP) * STEP); entry = float(np.round(((max(WORLD.c[te] - K, 0) if r.direction == "LONG" else max(K - WORLD.c[te], 0)) + tv(d)) / .05) * .05)
    S, e = contract(r.direction, K, d, te)
    assert abs(r.strike - K) < 1e-9 and abs(r.entry_price - entry) < 1e-9 and r.cov >= 0.999, (r.ekey, r.strike, K, r.entry_price, entry, r.cov)
    ls = np.array(json.loads(r.ls), float).reshape(-1, 3); hs = np.array(json.loads(r.hs), float).reshape(-1, 3)
    res = A.simulate_one(r.entry_price, ls, hs, json.loads(r.tx), json.loads(r.last))
    for v, (ex, sl, tp) in enumerate(A.VARS):
        want = brute(S, te, float(r.entry_price), sl, tp, ex); dm, px, code, late = res[v]
        if want is None: assert code == 0; continue
        assert code > 0 and te + pd.Timedelta(minutes=int(dm)) == want[0] and abs(px - want[1]) < 1e-6, (r.ekey, ex, sl, tp, res[v], want)
        checked += 1
print(f"{checked} trade outcomes (80 variants per entry) match the independent calculation")

# ---------------------------------------------------------------- result files
R.summary()
for f in ("SUMMARY.md", "summary.csv", "top_by_pnl.csv", "top_by_roi.csv", "best_per_strategy.csv", "trades_summary.csv", "REPORT.txt"):
    assert os.path.exists(f"{A.OUT}/{f}"), f
assert not os.path.exists(f"{A.OUT}/until_hit_days_held.csv")
S = pd.read_csv(f"{A.OUT}/summary.csv")
assert set(S.strategy) <= set(R.STRATS) and set(S.exit_rule) <= set(A.EXITS) and set(S.sl) == {0, 20, 40, 60} and set(S.tp) == {0, 20, 40, 60, 80}, (set(S.strategy), set(S.exit_rule), set(S.sl), set(S.tp))
assert {"12:00", "15:30"} <= set(S.exit_rule) and "UNTIL_HIT" not in set(S.exit_rule)
assert {"sl_rule", "tp_rule", "variant"} <= set(S.columns) and "no SL" in set(S.sl_rule) and "no TP" in set(S.tp_rule)
for s in R.STRATS:
    f = f"{A.OUT}/all_trades/{s}.csv.gz"; assert os.path.exists(f), f
    T = pd.read_csv(f)
    assert (T.strategy == s).all() and len(T[["exit_rule", "sl", "tp"]].drop_duplicates()) <= 80
    bf = f"{A.OUT}/trade_files/{s}_best_trades.csv"; assert os.path.exists(bf), bf
    B = pd.read_csv(bf); g = S[S.strategy == s].sort_values(["total_pnl", "trades"], ascending=False).iloc[0]
    assert len(B) == g.trades and abs(B.pnl.sum() - g.total_pnl) <= len(B), (s, len(B), g.trades, B.pnl.sum(), g.total_pnl)
    assert (pd.to_datetime(B.exit_date) == pd.to_datetime(B.entry_date)).all(), "every trade is closed on the entry day"
md = open(f"{A.OUT}/SUMMARY.md").read()
for s in R.STRATS: assert s in md, s
assert "re-cross rule" in md.lower() and "trade_files/" in md
assert json.load(open(f"{A.OUT}/rule.json")) == json.loads(json.dumps(R.rule_dict())) if os.path.exists(f"{A.OUT}/rule.json") else True
print("ALL OFFLINE TESTS PASSED")
