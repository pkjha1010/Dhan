"""Offline logic test for sltp_backtest.py / sltp_rules.py (no Dhan / Yahoo login):   SLTP_STUDY=pm python test_sltp.py   and   SLTP_STUDY=am python test_sltp.py
 1. the entry rules on hand-made minute paths (first touch, 12:00 split, 5-close re-cross, missing minutes, window edges)
 2. the rules against an independent re-implementation on thousands of random paths
 3. the strategy mapping and the exit grid (SL none/20/40/60 x TP 60/80/100/120/none x the study's time exits) against a brute-force walk
 4. end to end on a SIMULATED EXCHANGE: stock minute candles + option series -> entries -> option records -> trades -> SUMMARY.md, matrices and trade files."""
import os, sys, json, tempfile
import numpy as np, pandas as pd
from datetime import date, timedelta

STUDY = (os.environ.get("SLTP_STUDY") or "pm").lower()
tmp = tempfile.mkdtemp()
os.environ.update(SLTP_STUDY=STUDY, SLTP_OUT=f"{tmp}/out", SLTP_START="2026-01-02", SLTP_END="2026-03-27", SLTP_MIN_TRADES="1",
                  A8_OFFS_MAX="60", A8_MAX_OFFS="60", A8_TOP_N="10")
import sltp_rules as RU
import sltp_backtest as S
A = S.A
os.makedirs(A.OUT, exist_ok=True)
D0 = pd.Timestamp("2026-03-03")


def mk(path, start="09:15", lows=None, drop=()):
    """path = closes; low = close unless `lows` gives a dict {position: low}."""
    h0, m0 = int(start[:2]), int(start[3:])
    idx = pd.DatetimeIndex([D0 + pd.Timedelta(hours=h0, minutes=m0 + i) for i in range(len(path))])
    c = np.array(path, float); lo = c.copy()
    for k, v in (lows or {}).items(): lo[k] = v
    df = pd.DataFrame({"o": c, "h": c + 0.0, "l": np.minimum(lo, c), "c": c}, index=idx)
    return df.drop(df.index[list(drop)]) if drop else df


def pos(u, hhmm): return int(np.nonzero(u.index.strftime("%H:%M") == hhmm)[0][0])
def at(u, k): return None if k is None else u.index[k].strftime("%H:%M")


LV = 100.0
# ---------------------------------------------------------------- 1. hand-made paths (SHORT: the stock falls to the level 100)
n_all = 375                                                                     # 09:15 .. 15:29
above = [101.0] * n_all
base = mk(above)                                                                # only used to look up positions of clock times
P = lambda hhmm: pos(base, hhmm)
SPLIT_, LASTM = 12 * 60, 15 * 60 + 20

# TYPE 1: the day's first touch is a wick at 13:00, everything before is above -> enter 13:00; type 2 does not fire
u = mk(above, lows={P("13:00"): 99.9})
assert at(u, RU.afternoon_first_touch(u, LV)) == "13:00" and RU.afternoon_recross(u, LV) is None
# first touch exactly at 12:00 is the afternoon (>= split)
u = mk(above, lows={P("12:00"): 99.5})
assert at(u, RU.afternoon_first_touch(u, LV)) == "12:00" and RU.afternoon_recross(u, LV) is None
# first touch at 11:59 is a morning touch: type 1 does not fire; nothing touches again -> no type-2 entry either
u = mk(above, lows={P("11:59"): 99.5})
assert RU.afternoon_first_touch(u, LV) is None and RU.afternoon_recross(u, LV) is None
# a touch at / after the last allowed minute is not taken
u = mk(above, lows={P("15:25"): 99.5})
assert RU.afternoon_first_touch(u, LV, SPLIT_, LASTM) is None and at(u, RU.afternoon_first_touch(u, LV, SPLIT_, 15 * 60 + 30)) == "15:25"
# no touch at all
assert RU.afternoon_first_touch(mk(above), LV) is None and RU.afternoon_recross(mk(above), LV) is None and RU.day_first_touch(mk(above), LV) is None

# TYPE 2: morning touch at 10:00, all closes stay above, the afternoon candle at 13:10 touches -> valid cross (5 closes above right before it) -> enter 13:10
u = mk(above, lows={P("10:00"): 99.0, P("13:10"): 99.8})
assert RU.afternoon_first_touch(u, LV) is None and at(u, RU.afternoon_recross(u, LV)) == "13:10"
# morning touch, then the stock stays BELOW the level all day: the 5 closes above are missing -> no entry
low_path = list(above)
for k in range(P("10:00"), n_all): low_path[k] = 99.0
u = mk(low_path)
assert RU.afternoon_first_touch(u, LV) is None and RU.afternoon_recross(u, LV) is None
# below from 10:00 to 12:59, closes above from 13:00: a touch at 13:05 follows 5 closes above (13:00-13:04) = valid; a touch at 13:04 follows only 4 = not valid
p = list(above)
for k in range(P("10:00"), P("13:00")): p[k] = 99.0
u = mk(p, lows={P("13:05"): 99.9})
assert at(u, RU.afternoon_recross(u, LV)) == "13:05"
u = mk(p, lows={P("13:04"): 99.9})
assert RU.afternoon_recross(u, LV) is None
# a cross before the split does not count as type 2 (and the day's first touch was in the morning, so type 1 is off too)
u = mk(above, lows={P("10:00"): 99.0, P("11:30"): 99.5})
assert RU.afternoon_first_touch(u, LV) is None and RU.afternoon_recross(u, LV) is None
# a missing minute inside the 5 breaks the run (13:10 touch, 13:07 missing): not valid; with all minutes present it is
u = mk(above, lows={P("10:00"): 99.0, P("13:10"): 99.8}, drop=[P("13:07")])
assert RU.afternoon_recross(u, LV) is None
# only CLOSES count: wicks below the level in the 5 minutes before do not matter... but the first wick that has 5 closes above before it IS the entry (13:08 here)
u = mk(above, lows={P("10:00"): 99.0, P("13:08"): 99.5, P("13:10"): 99.8})
assert at(u, RU.afternoon_recross(u, LV)) == "13:08"
# a close exactly AT the level is not "above": check the helper on a run with one close at the level
w = mk([101.0, 101.0, 100.0, 101.0, 101.0, 101.0], lows={5: 99.0}); assert not RU.valid_recross(w, LV, 5, 5)
w = mk([101.0] * 6, lows={5: 99.0}); assert RU.valid_recross(w, LV, 5, 5) and not RU.valid_recross(w, LV, 4, 5) and RU.valid_recross(w, LV, 5, 3)
assert not RU.valid_recross(w, LV, 5, 5, band=0.02)                                   # a 2 % band: 101 is not clearly above 100 * 1.02

# MORNING rule: window 09:20-09:59, 5 closes above
am = RU.recross_entry
W0, W1 = 9 * 60 + 20, 9 * 60 + 59
u = mk(above, lows={P("09:20"): 99.5});  assert at(u, am(u, LV, W0, W1)) == "09:20"                      # 09:15-09:19 are the 5 closes above
u = mk(above, lows={P("09:19"): 99.5});  assert am(u, LV, W0, W1) is None                               # touch at 09:19 is before the window, nothing touches afterwards
u = mk(above, lows={P("09:19"): 99.5, P("09:40"): 99.5}); assert at(u, am(u, LV, W0, W1)) == "09:40"     # the 09:19 wick is no problem (closes only)
u = mk(above, lows={P("09:59"): 99.5});  assert at(u, am(u, LV, W0, W1)) == "09:59"                      # last minute of the window is allowed
u = mk(above, lows={P("10:00"): 99.5});  assert am(u, LV, W0, W1) is None                               # 10:00 is outside the window
p3 = list(above)
for k in range(0, 8): p3[k] = 99.0                                                                      # gap down: closes below until 09:22
assert am(mk(p3), LV, W0, W1) is None                                                                   # never above again for 5 minutes with a touch -> nothing (all closes above have low = close)
u = mk(p3, lows={P("09:26"): 99.7});     assert am(u, LV, W0, W1) is None                                # 09:26 touches but 09:21-09:25 are not all above (09:21, 09:22 below)
u = mk(p3, lows={P("09:28"): 99.7});     assert at(u, am(u, LV, W0, W1)) == "09:28"                      # 09:23-09:27 = 5 closes above, 09:28 touches: a valid RE-cross
print(f"entry rules: hand-made paths OK (study {STUDY})")


# ---------------------------------------------------------------- 2. independent re-implementation on random paths
def ref_pm(low, close, m, level, split, last, n):
    k0 = next((k for k in range(len(m)) if m[k] >= 555 and low[k] <= level), None)
    out = {}
    if k0 is None: return out
    if split <= m[k0] <= last: out["PM_T1"] = k0
    if m[k0] < split:
        for k in range(len(m)):
            if m[k] < split: continue
            if m[k] > last: break
            if k >= n and low[k] <= level and all(m[k - j] == m[k] - j and close[k - j] > level for j in range(1, n + 1)): out["PM_T2"] = k; break
    return out


def ref_am(low, close, m, level, a, b, n):
    for k in range(len(m)):
        if m[k] < a: continue
        if m[k] > b: break
        if k >= n and low[k] <= level and all(m[k - j] == m[k] - j and close[k - j] > level for j in range(1, n + 1)): return k
    return None


rng = np.random.default_rng(7)
hits = {"PM_T1": 0, "PM_T2": 0, "AM": 0}
for trial in range(3000):
    n = int(rng.integers(30, 375)); lvl = float(rng.uniform(50, 3000)); sig = float(rng.choice([0.0002, 0.0005, 0.001]))
    c = lvl * (1 + rng.normal(0, 0.003) + np.cumsum(rng.normal(0, sig, n)))
    lo = c * (1 - np.abs(rng.normal(0, 0.0004, n)))
    keep = rng.random(n) > rng.choice([0, 0.01, 0.05]); keep[0] = True
    idx = pd.DatetimeIndex([D0 + pd.Timedelta(hours=9, minutes=15 + i) for i in range(n)])[keep]
    u = pd.DataFrame({"o": c[keep], "h": c[keep], "l": lo[keep], "c": c[keep]}, index=idx)
    m = u.index.hour.values * 60 + u.index.minute.values
    nn = int(rng.choice([3, 5, 8])); last = int(rng.choice([12 * 60 + 30, 15 * 60 + 20]))
    want = ref_pm(u.l.values, u.c.values, m, lvl, 12 * 60, last, nn)
    got = {}
    k1 = RU.afternoon_first_touch(u, lvl, 12 * 60, last); k2 = RU.afternoon_recross(u, lvl, 12 * 60, last, nn)
    if k1 is not None: got["PM_T1"] = k1
    if k2 is not None: got["PM_T2"] = k2
    assert got == want, (trial, got, want)
    assert not (k1 is not None and k2 is not None)                                   # the two types never fire on the same day
    for t in got: hits[t] += 1
    wa, wb = int(rng.choice([9 * 60 + 20, 9 * 60 + 30])), int(rng.choice([9 * 60 + 45, 9 * 60 + 59]))
    ga, wa_ = RU.recross_entry(u, lvl, wa, wb, nn), ref_am(u.l.values, u.c.values, m, lvl, wa, wb, nn)
    assert ga == wa_, (trial, ga, wa_)
    hits["AM"] += ga is not None
assert hits["PM_T1"] > 20 and hits["PM_T2"] > 100 and hits["AM"] > 100, hits
print(f"entry rules == independent re-implementation on 3000 random paths {hits}")

# ---------------------------------------------------------------- 3. strategy mapping and the exit grid
if STUDY == "pm":
    assert S.STRATS == ["BPB_SHORT_T1_FIRST_TOUCH", "BPB_SHORT_T2_RECROSS", "BPB_SHORT_T1_T2_COMBINED"] and A.EXITS == ["15:00", "15:30"]
    assert S.strategies_for("BPB", "PM_T1", -1, -1, -1, -1) == ["BPB_SHORT_T1_FIRST_TOUCH", "BPB_SHORT_T1_T2_COMBINED"]
    assert S.strategies_for("BPB", "PM_T2", -1, -1, -1, -1) == ["BPB_SHORT_T2_RECROSS", "BPB_SHORT_T1_T2_COMBINED"]
    assert S.strategies_for("SHAPE", "PM_T1", 0, 1, 1, 0) == [] and S.strategies_for("BPB", "AM_RC", -1, -1, -1, -1) == []
else:
    assert S.STRATS == ["BPB_SHORT_AM_RECROSS", "WRU_SHORT_AM_RECROSS"] and A.EXITS == ["10:00"]
    assert S.strategies_for("BPB", "AM_RC", -1, -1, -1, -1) == ["BPB_SHORT_AM_RECROSS"]
    assert S.strategies_for("SHAPE", "AM_RC", 0, 1, 1, 0) == ["WRU_SHORT_AM_RECROSS"]                    # red + upper wick longer = WRU
    assert S.strategies_for("SHAPE", "AM_RC", 1, 0, 1, 0) == [] and S.strategies_for("SHAPE", "AM_RC", 0, 1, 0, 1) == [] and S.strategies_for("BPB", "PM_T1", -1, -1, -1, -1) == []
assert A.SLS == [0, 20, 40, 60] and A.TPS == [60, 80, 100, 120, 0] and len(A.VARS) == 20 * len(A.EXITS) and "UNTIL_HIT" not in A.EXITS
assert S.entries_for(mk(above, lows={pos(mk(above), "13:00"): 99.0}), LV, True) == {}                    # SHORT only

minutes = pd.timedelta_range("09:15:00", "15:29:00", freq="min")


def brute(Sx, te, entry, sl, tp, ex):
    Sx = Sx[Sx.index > te]
    lt = pd.Timestamp(f"{te.date()} {ex}")
    if te >= lt: return None
    Sx = Sx[Sx.index <= lt]
    if Sx.empty: return None
    slp = round(entry * (1 - sl / 100), 6) if sl else None; tpp = round(entry * (1 + tp / 100), 6) if tp else None
    for ts, r in Sx.iterrows():
        if slp is not None and r.l <= slp: return ts, (r.o if r.o <= slp else slp)
        if tpp is not None and r.h >= tpp: return ts, (r.o if r.o >= tpp else tpp)
    return Sx.index[-1], Sx.c.iloc[-1]


rng = np.random.default_rng(3)
for trial in range(12):
    days = pd.bdate_range("2026-03-02", periods=4)
    idx = pd.DatetimeIndex([d + m for d in days for m in minutes])
    c = np.round((40 * np.exp(np.cumsum(rng.normal(0, 0.0035, len(idx))))) / .05) * .05
    o = np.r_[c[0], c[:-1]]; h = np.round((np.maximum(o, c) + np.abs(rng.normal(0, .15, len(idx)))) / .05) * .05; l = np.maximum(.05, np.round((np.minimum(o, c) - np.abs(rng.normal(0, .15, len(idx)))) / .05) * .05)
    full = pd.DataFrame({"o": o, "h": h, "l": l, "c": c}, index=idx).round(2)
    k0 = int(rng.integers(5, 200)); te = full.index[k0]; entry = float(full.c.iloc[k0]); Sx = full.iloc[k0 + 1:]
    rec = A.make_record(Sx, te, entry, 100, 2000.0, date(2026, 3, 5), 1.0)
    ls = np.array(json.loads(rec["ls"]), float).reshape(-1, 3); hs = np.array(json.loads(rec["hs"]), float).reshape(-1, 3)
    res = A.simulate_one(rec["entry_price"], ls, hs, json.loads(rec["tx"]), json.loads(rec["last"]))
    assert len(res) == len(A.VARS)
    for v, (ex, sl, tp) in enumerate(A.VARS):
        want = brute(Sx, te, rec["entry_price"], sl, tp, ex); dm, px, code, late = res[v]
        if want is None: assert code == 0, (trial, ex, sl, tp); continue
        assert code > 0 and te + pd.Timedelta(minutes=int(dm)) == want[0] and abs(px - want[1]) < 1e-6, (trial, ex, sl, tp, res[v], want)
        if not sl and not tp: assert code == 5
print(f"exit grid (SL {A.SLS} x TP {A.TPS} x exits {A.EXITS}) == brute force on 12 random paths")

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
        f = (lambda Sx: np.round(((np.maximum(Sx - K, 0) if side == "LONG" else np.maximum(K - Sx, 0)) + tvs) / .05) * .05)
        po, pc = f(w.o.values), f(w.c.values); ph, pl = (f(w.h.values), f(w.l.values)) if side == "LONG" else (f(w.l.values), f(w.h.values))
        d = {"timestamp": epoch(w.index), "open": list(po), "high": list(ph), "low": list(pl), "close": list(pc), "strike": list(K)}
        return {"data": {"ce" if side == "LONG" else "pe": d}}


dh = Fake(); mst = {"AAA": (SID, LOT)}
dates = [d.date() for d in bd if date(2026, 1, 5) <= d.date() <= date(2026, 3, 20)]
LAST = A.ENTRY_MIN
rows, want_entry = [], {}                                                          # want_entry[(strategy-type, date)] = entry minute


def day_entries(day, lvl):
    m = day.index.hour.values * 60 + day.index.minute.values
    if STUDY == "pm": return {t: k for t, k in ref_pm(day.l.values, day.c.values, m, lvl, 12 * 60, LAST, 5).items()}
    k = ref_am(day.l.values, day.c.values, m, lvl, 9 * 60 + 20, min(9 * 60 + 59, LAST), 5)
    return {} if k is None else {"AM_RC": k}


kinds = {"PM_T1": 0, "PM_T2": 0, "AM_RC": 0}
for i, d in enumerate(dates):
    day = WORLD[(W_day == d) & (W_idx.hour * 60 + W_idx.minute <= LAST)]
    cl = day.c.values
    wanted = (["PM_T1", "PM_T2"][i % 2], ["PM_T2", "PM_T1"][i % 2]) if STUDY == "pm" else ("AM_RC",)
    for w_ in wanted:
        lvl = next((round(float(np.quantile(cl, q)), 2) for q in np.linspace(0.02, 0.98, 49) if w_ in day_entries(day, round(float(np.quantile(cl, q)), 2))), None)
        if lvl is None: continue
        ent = day_entries(day, lvl)
        src = "BPB" if (STUDY == "pm" or i % 2 == 0) else "SHAPE"
        g, rd, up, lo = (-1, -1, -1, -1) if src == "BPB" else (0, 1, 1, 0)
        rows.append(dict(source=src, stock="AAA", direction="SHORT", ref=lvl, signal_date=str(d - timedelta(days=1)), date=str(d), yahoo_open=float(day.o.iloc[0]), green=g, red=rd, upper_longer=up, lower_longer=lo))
        for t, k in ent.items(): want_entry[(t, str(d))] = day.index[k].strftime("%H:%M"); kinds[t] += 1
        break
    # noise rows that must be ignored: a LONG row, and (morning study) a green-upper SHAPE row / (afternoon study) a SHAPE row
    rows.append(dict(source="SHAPE", stock="AAA", direction="LONG", ref=round(float(np.quantile(cl, .5)), 2), signal_date=str(d), date=str(d), yahoo_open=float(day.o.iloc[0]), green=0, red=1, upper_longer=1, lower_longer=0))
    rows.append(dict(source="SHAPE", stock="AAA", direction="SHORT", ref=round(float(np.quantile(cl, .4)), 2), signal_date=str(d), date=str(d), yahoo_open=float(day.o.iloc[0]), green=1, red=0, upper_longer=1, lower_longer=0))
cand_all = pd.DataFrame(rows)
cand = S.pick(cand_all)                                                             # the production filter
assert (cand.direction == "SHORT").all() and (cand.source == "BPB").all() if STUDY == "pm" else ((cand.direction == "SHORT").all() and set(cand.source) <= {"BPB", "SHAPE"})
if STUDY == "am": assert ((cand.source == "BPB") | ((cand.red == 1) & (cand.upper_longer == 1))).all()
assert len(cand) > 25 and sum(kinds.values()) > 25, (len(cand), kinds)
if STUDY == "pm": assert kinds["PM_T1"] > 8 and kinds["PM_T2"] > 8, kinds
st = A.load_state()
ev = A.step_events(dh, cand, mst, st)
assert len(ev) and set(ev.strategy) <= set(S.STRATS)
if STUDY == "pm":
    assert set(ev.strategy) == set(S.STRATS)
    t1 = ev[ev.strategy == "BPB_SHORT_T1_FIRST_TOUCH"]; t2 = ev[ev.strategy == "BPB_SHORT_T2_RECROSS"]; cb = ev[ev.strategy == "BPB_SHORT_T1_T2_COMBINED"]
    assert len(cb) == len(t1) + len(t2) and not (set(t1.date) & set(t2.date)) and set(cb.date) == set(t1.date) | set(t2.date)
    assert (t1.type == "PM_T1").all() and (t2.type == "PM_T2").all()
else:
    assert set(ev.strategy) == set(S.STRATS), ev.strategy.value_counts()
for r in ev.itertuples():
    key = ("PM_T1" if r.strategy.startswith("BPB_SHORT_T1_FIRST") else "PM_T2" if r.strategy.endswith("T2_RECROSS") else r.type, r.date)
    assert r.type in ("PM_T1", "PM_T2", "AM_RC") and r.direction == "SHORT"
    assert r.entry_minute == want_entry[(r.type, r.date)], (r.strategy, r.date, r.entry_minute, want_entry[(r.type, r.date)])
    assert "09:20" <= r.entry_minute <= "09:59" if STUDY == "am" else ("12:00" <= r.entry_minute <= "15:20")
ev = ev[(ev.date >= A.START) & (ev.date <= A.END)]
A.step_options(dh, ev, mst, st)
recs = A.load_records(); assert len(recs) > 0
print(f"{len(cand)} candidate days -> {len(ev)} entries ({dict(ev.groupby('strategy').size())}) -> {len(recs)} option records; Dhan calls {dh.n}")


def contract(side, K, d, te):
    e = exp_for(d); w = WORLD[(W_day >= d) & (W_day <= e)]; w = w[w.index > te]
    dts = [t.date() for t in w.index]; tvs = np.array([tv(x) for x in dts])
    g = lambda x: np.round(np.round(((np.maximum(x - K, 0) if side == "LONG" else np.maximum(K - x, 0)) + tvs) / .05) * .05, 2)
    po, pc = g(w.o.values), g(w.c.values); ph, pl = (g(w.h.values), g(w.l.values)) if side == "LONG" else (g(w.l.values), g(w.h.values))
    return pd.DataFrame({"o": po, "h": ph, "l": pl, "c": pc}, index=w.index), e


checked = 0
for r in recs.itertuples():
    te = pd.Timestamp(f"{r.date} {r.entry_minute}"); d = date.fromisoformat(r.date)
    K = float(np.round(WORLD.c[te] / STEP) * STEP); entry = float(np.round(((max(WORLD.c[te] - K, 0) if r.direction == "LONG" else max(K - WORLD.c[te], 0)) + tv(d)) / .05) * .05)
    Sx, e = contract(r.direction, K, d, te)
    assert r.direction == "SHORT" and abs(r.strike - K) < 1e-9 and abs(r.entry_price - entry) < 1e-9 and r.cov >= 0.999, (r.ekey, r.strike, K, r.entry_price, entry, r.cov)
    ls = np.array(json.loads(r.ls), float).reshape(-1, 3); hs = np.array(json.loads(r.hs), float).reshape(-1, 3)
    res = A.simulate_one(r.entry_price, ls, hs, json.loads(r.tx), json.loads(r.last))
    for v, (ex, sl, tp) in enumerate(A.VARS):
        want = brute(Sx, te, float(r.entry_price), sl, tp, ex); dm, px, code, late = res[v]
        if want is None: assert code == 0; continue
        assert code > 0 and te + pd.Timedelta(minutes=int(dm)) == want[0] and abs(px - want[1]) < 1e-6, (r.ekey, ex, sl, tp, res[v], want)
        checked += 1
print(f"{checked} trade outcomes ({len(A.VARS)} variants per entry) match the independent calculation")

# ---------------------------------------------------------------- result files
S.summary()
for f in ("SUMMARY.md", "summary.csv", "trades_summary.csv", "REPORT.txt", "matrix_total_pnl.csv", "matrix_roi_pct.csv", "matrix_win_pct.csv", "matrix_profit_factor.csv", "entry_log.csv"):
    assert os.path.exists(f"{A.OUT}/{f}"), f
assert not os.path.exists(f"{A.OUT}/until_hit_days_held.csv")
Sm = pd.read_csv(f"{A.OUT}/summary.csv")
assert set(Sm.strategy) == set(S.STRATS) and set(Sm.exit_rule) == set(A.EXITS) and set(Sm.sl) == {0, 20, 40, 60} and set(Sm.tp) == {0, 60, 80, 100, 120}, (set(Sm.strategy), set(Sm.exit_rule), set(Sm.sl), set(Sm.tp))
assert {"sl_rule", "tp_rule", "variant"} <= set(Sm.columns) and "no SL" in set(Sm.sl_rule) and "no TP" in set(Sm.tp_rule)
M = pd.read_csv(f"{A.OUT}/matrix_total_pnl.csv")
assert list(M.columns) == ["strategy", "exit_rule", "stop_loss", "TP 60%", "TP 80%", "TP 100%", "TP 120%", "no TP"], list(M.columns)
assert len(M) == len(S.STRATS) * len(A.EXITS) * 4
for s in S.STRATS:
    f = f"{A.OUT}/trade_files/{s}_all_variants_trades.csv"; assert os.path.exists(f), f
    T = pd.read_csv(f)
    assert (T.strategy == s).all() and len(T[["exit_rule", "sl", "tp"]].drop_duplicates()) <= len(A.VARS) and {"first_touch_time", "level"} <= set(T.columns)
    assert T.first_touch_time.notna().all(), s
    if STUDY == "pm": assert (T.first_touch_time >= "12:00").all() if s.endswith("T1_FIRST_TOUCH") else True
    bf = f"{A.OUT}/trade_files/{s}_best_trades.csv"; assert os.path.exists(bf), bf
    B = pd.read_csv(bf); g = Sm[Sm.strategy == s].sort_values(["total_pnl", "trades"], ascending=False).iloc[0]
    assert len(B) == g.trades and abs(B.pnl.sum() - g.total_pnl) <= len(B), (s, len(B), g.trades, B.pnl.sum(), g.total_pnl)
    assert (pd.to_datetime(B.exit_date) == pd.to_datetime(B.entry_date)).all(), "every trade is closed on the entry day"
    en = pd.read_csv(f"{A.OUT}/trade_files/{s}_entries.csv"); assert len(en) and {"stock", "date", "entry_minute", "strike", "entry_price", "first_touch_time"} <= set(en.columns)
    # one matrix cell == the summary row == the sum of the all-variants trades
    r0 = Sm[Sm.strategy == s].iloc[0]
    sub = T[(T.exit_rule == r0.exit_rule) & (T.sl == r0.sl) & (T.tp == r0.tp)]
    assert len(sub) == r0.trades and abs(sub.pnl.sum() - r0.total_pnl) <= len(sub)
md = open(f"{A.OUT}/SUMMARY.md").read()
for s in S.STRATS: assert s in md, s
assert "Entry rule" in md and "trade_files/" in md or "`trade_files/`" in md
if STUDY == "pm":
    assert "15:00" in set(Sm.exit_rule) and "15:30" in set(Sm.exit_rule)
    c = Sm[Sm.strategy == "BPB_SHORT_T1_T2_COMBINED"]; a = Sm[Sm.strategy == "BPB_SHORT_T1_FIRST_TOUCH"]; b = Sm[Sm.strategy == "BPB_SHORT_T2_RECROSS"]
    k = (c.exit_rule == "15:30") & (c.sl == 0) & (c.tp == 0)
    k1 = (a.exit_rule == "15:30") & (a.sl == 0) & (a.tp == 0); k2 = (b.exit_rule == "15:30") & (b.sl == 0) & (b.tp == 0)
    assert int(c[k].trades.iloc[0]) == int(a[k1].trades.iloc[0]) + int(b[k2].trades.iloc[0])
    assert abs(float(c[k].total_pnl.iloc[0]) - float(a[k1].total_pnl.iloc[0]) - float(b[k2].total_pnl.iloc[0])) <= 5            # combined = T1 + T2
print("ALL OFFLINE TESTS PASSED (study " + STUDY + ")")
