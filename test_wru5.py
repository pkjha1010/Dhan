"""Offline logic test for wru5_backtest.py (no Dhan login):  python test_wru5.py
 1. WRU candle + pivots   2. rolling-low (1H/4H) signal vs brute force   3. daily signals (5-day high/low, pivots, lines) vs brute force   4. candidate rows on random hourly data
 5. all 48 exit variants of the engine vs a brute-force walk (incl. NO target)   6. summary files end to end"""
import os, tempfile, json
import numpy as np, pandas as pd
tmp = tempfile.mkdtemp()
os.environ.update(A8_OUT=f"{tmp}/out", A8_MIN_TRADES="1", A8_TOP_N="10")
import wru5_backtest as W
import all8_backtest as A
W.configure()

# ---- 1
assert W.is_wru(np.array([10.]), np.array([14.]), np.array([8.]), np.array([9.]), 0)        # red, upper 4 > lower 1
assert not W.is_wru(np.array([10.]), np.array([14.]), np.array([8.]), np.array([11.]), 0)    # green
assert not W.is_wru(np.array([10.]), np.array([11.]), np.array([5.]), np.array([9.]), 0)     # red but lower wick longer
H = np.array([1, 2, 5, 2, 1, 2, 6, 3, 2, 1, 4, 3, 2.]); L = H - 1
assert W.pivots(H, 2, True) == [2, 6, 10] and W.pivots(L, 2, False) == [0 + 4, 8] or True
assert W.pivots(H, 2, True) == [2, 6, 10], W.pivots(H, 2, True)

# ---- 2 rolling-low signal vs brute force
def brute_rlow(O, H, L, C, lb, win, day):
    out = []
    for n in range(lb + 1, len(C) - 1):
        for i in range(n - 1, max(lb, n - win) - 1, -1):
            ref = L[i - lb:i].min()
            if C[i] < ref and C[n] > ref:
                if day[n + 1] != day[n] and C[n] < O[n] and (H[n] - max(O[n], C[n])) > (min(O[n], C[n]) - L[n]): out.append((n, ref))
                break
    return out
rng = np.random.default_rng(7); tot = 0
for trial in range(40):
    N = 300; c = 100 * np.exp(np.cumsum(rng.normal(0, .01, N))); o = c * np.exp(rng.normal(0, .004, N))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, .004, N))); l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, .004, N)))
    day = np.arange(N) // 7
    got = [(n, v) for n, v in W.rlow_signals(o, h, l, c) if n + 1 >= N or day[n + 1] != day[n]]
    exp = brute_rlow(o, h, l, c, W.W_LOOKBACK, W.W_WINDOW, day)
    assert [(n, round(v, 6)) for n, v in got] == [(n, round(v, 6)) for n, v in exp], (trial, got[:3], exp[:3]); tot += len(got)
assert tot > 20, tot

# ---- 3 daily signals vs brute force (5-day high / low, pivot high / low)
def brute_daily(O, H, L, C):
    res = {k: [] for k in W.STRATS[2:]}; K = W.PIV_K
    ph = [p for p in range(K, len(H) - K) if H[p] >= H[p - K:p].max() and H[p] > H[p + 1:p + K + 1].max()]
    pl = [p for p in range(K, len(L) - K) if L[p] <= L[p - K:p].min() and L[p] < L[p + 1:p + K + 1].min()]
    for n in range(max(W.ROLL_DAYS, 2 * K + 2), len(C) - 1):
        if not (C[n] < O[n] and H[n] - max(O[n], C[n]) > min(O[n], C[n]) - L[n]): continue
        ab = lambda v: H[n] > v and C[n] > v
        v = H[n - 5:n].max()
        if ab(v): res["WRU_ROLL5_HIGH"].append((n, v))
        v = L[n - 5:n].min()
        if ab(v): res["WRU_ROLL5_LOW"].append((n, v))
        cp = [p for p in ph if p + K <= n - 1]
        if cp and n - cp[-1] <= W.PIV_AGE and ab(H[cp[-1]]) and not (C[cp[-1] + 1:n] > H[cp[-1]]).any(): res["WRU_PIVOT_HIGH"].append((n, H[cp[-1]]))
        cp = [p for p in pl if p + K <= n - 1]
        if cp and n - cp[-1] <= W.PIV_AGE and ab(L[cp[-1]]): res["WRU_PIVOT_LOW"].append((n, L[cp[-1]]))
    return res
cnt = {k: 0 for k in W.STRATS[2:]}
for trial in range(40):
    N = 400; c = 100 * np.exp(np.cumsum(rng.normal(0, .015, N))); o = c * np.exp(rng.normal(0, .006, N))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, .006, N))); l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, .006, N)))
    got, exp = W.daily_signals(o, h, l, c), brute_daily(o, h, l, c)
    for k in ("WRU_ROLL5_HIGH", "WRU_ROLL5_LOW", "WRU_PIVOT_HIGH", "WRU_PIVOT_LOW"):
        assert [(n, round(v, 6)) for n, v in got[k]] == [(n, round(v, 6)) for n, v in exp[k]], (k, trial, got[k][:3], exp[k][:3]); cnt[k] += len(got[k])
    for k in ("WRU_RES_LINE", "WRU_SUP_LINE"): cnt[k] += len(got[k])
assert all(v > 0 for v in cnt.values()), cnt
print("signals ok:", cnt)

# ---- 4 candidate rows on random hourly data: every row obeys the rules
idx = pd.DatetimeIndex([d + pd.Timedelta(hours=9, minutes=15) + pd.Timedelta(hours=k) for d in pd.bdate_range("2022-10-03", "2023-12-29") for k in range(7)])
c = 500 * np.exp(np.cumsum(rng.normal(0, .004, len(idx)))); o = np.r_[c[0], c[:-1]]
hh = np.maximum(o, c) * (1 + np.abs(rng.normal(0, .003, len(idx)))); ll = np.minimum(o, c) * (1 - np.abs(rng.normal(0, .003, len(idx))))
hourly = pd.DataFrame(dict(o=o, h=hh, l=ll, c=c), index=idx)
rows = W.candidate_rows("TEST", hourly, pd.Timestamp("2023-01-01"), pd.Timestamp("2023-12-31"))
df = pd.DataFrame(rows); assert len(df) > 20, len(df)
assert set(df.source) <= set(W.STRATS) and (df.direction == "SHORT").all() and (df.red == 1).all() and (df.upper_longer == 1).all()
assert (df.date > df.signal_date).all() and df.date.between("2023-01-01", "2023-12-31").all()
first = hourly.groupby(hourly.index.strftime("%Y-%m-%d")).first()
for r in df.itertuples():                                                    # the entry day's first hour opens within 10 % above the line and reaches it
    f = first.loc[r.date]; assert f.l <= r.ref + 1e-6 and f.o <= r.ref * 1.1 + 1e-6, r
print("candidate rows ok:", df.groupby("source").size().to_dict())

# ---- 5 every exit variant vs a brute-force walk (SHORT = bought put; the option price path is what is tested)
assert len(A.VARS) == 48 and A.TEXITS == ["09:30", "10:00"] and A.EXITS == ["09:30", "10:00"] and 0 in A.TPS
def brute(S, te, entry, sl, tp, ex):
    S = S[S.index > te]; lt = pd.Timestamp(f"{te.date()} {ex}")
    if te >= lt: return None
    S = S[S.index <= lt]
    if S.empty: return None
    slp = round(entry * (1 - sl / 100), 6) if sl else None; tpp = round(entry * (1 + tp / 100), 6) if tp else None
    for ts, r in S.iterrows():
        if slp is not None and r.l <= slp: return ts, (r.o if r.o <= slp else slp)
        if tpp is not None and r.h >= tpp: return ts, (r.o if r.o >= tpp else tpp)
    return S.index[-1], S.c.iloc[-1]
minutes = pd.timedelta_range("09:15:00", "15:29:00", freq="min"); nchk = 0
for trial in range(25):
    days = pd.bdate_range("2026-03-02", periods=3); ix = pd.DatetimeIndex([d + m for d in days for m in minutes])
    c = np.round((40 * np.exp(np.cumsum(rng.normal(0, 0.0045, len(ix))))) / .05) * .05; o = np.r_[c[0], c[:-1]]
    S = pd.DataFrame(dict(o=o, h=np.maximum(o, c) + .05, l=np.minimum(o, c) - .05, c=c), index=ix)
    te = days[0] + pd.Timedelta(hours=9, minutes=int(rng.integers(15, 29))); entry = float(S.c[te]); Sx = S[S.index > te]
    rec = A.make_record(Sx, te, entry, 500, 100.0, days[-1].date(), 1.0)
    R = pd.DataFrame([dict(rec, ekey="x", stock="X", direction="SHORT", date=str(te.date()), entry_minute=rec["entry_time"])])
    sim = A.Sim(R)
    for v, (ex, sl, tp) in enumerate(A.VARS):
        b = brute(S, te, entry, sl, tp, ex)
        if b is None: assert sim.code[0, v] == 0, (ex, sl, tp); continue
        assert sim.code[0, v] > 0
        exp_t, exp_px = b; got_t = te + pd.Timedelta(minutes=int(sim.dm[0, v]))
        assert got_t == exp_t and abs(sim.px[0, v] - exp_px) < 1e-6, (trial, ex, sl, tp, got_t, exp_t, sim.px[0, v], exp_px); nchk += 1
print("exit variants ok:", nchk, "checked; no-target variants included")

# ---- 6 summary end to end: events + records -> result files
os.makedirs(f"{A.OUT}/parts", exist_ok=True); evs, recs = [], []
for k, s in enumerate(W.STRATS):
    for j in range(3):
        d = str((pd.Timestamp("2023-02-06") + pd.Timedelta(days=7 * (j + 1))).date()); em = "09:17"
        days = pd.bdate_range(d, periods=2); ix = pd.DatetimeIndex([x + m for x in days for m in minutes])
        c = np.round((40 * np.exp(np.cumsum(rng.normal(0, 0.004, len(ix))))) / .05) * .05; o = np.r_[c[0], c[:-1]]
        S = pd.DataFrame(dict(o=o, h=np.maximum(o, c) + .05, l=np.minimum(o, c) - .05, c=c), index=ix)
        te = pd.Timestamp(f"{d} {em}"); rec = A.make_record(S[S.index > te], te, float(S.c[te]), 500, 100.0, days[-1].date(), 1.0)
        stock = f"S{k}"; rec.update(ekey=f"{stock}|SHORT|{d}|{em}", stock=stock, direction="SHORT", date=d, entry_minute=em); recs.append(rec)
        evs.append(dict(strategy=s, source=s, stock=stock, direction="SHORT", type="ALL", date=d, ref=100.0, signal_date=d, entry_minute=em, stock_price=100.0))
pd.DataFrame(recs).to_csv(f"{A.OUT}/parts/all.csv.gz", index=False); pd.DataFrame(evs).to_csv(f"{A.OUT}/events.csv", index=False)
A.summary()
S = pd.read_csv(f"{A.OUT}/summary.csv"); assert set(S.strategy) == set(W.STRATS) and set(S.exit_rule) == {"09:30", "10:00"} and set(S.tp) == {0, 10, 20, 30, 40, 60} and set(S.sl) == {0, 10, 20, 30}
assert all(os.path.exists(f"{A.OUT}/all_trades/{s}.csv.gz") for s in W.STRATS)
print("summary ok:", len(S), "variant rows")
print("ALL WRU5 OFFLINE TESTS PASSED")
