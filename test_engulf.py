"""Offline logic test for engulf_backtest.py / engulf_rules.py (no Dhan / Yahoo login):   python test_engulf.py
 1. the daily setup on hand-made candles (engulfing, 10-day high, pullback closes, invalidation, level, entry day, waiting limit, no overlap)
 2. the setup against an independent re-implementation (the original script's loop) on thousands of random price paths
 3. the 1-minute entry (first High >= level, gap up = 09:15, window end)
 4. the exit grid (SL none/20/40/60 x TP 20..200 x time exits 09:30/10:00/15:30) against a brute-force walk
 5. end to end on a SIMULATED EXCHANGE: candidates -> stock minute candles -> entries -> option records (ATM, and ITM-1 when the ATM series has no candle) -> trades -> SUMMARY.md and files."""
import os, sys, json, tempfile
import numpy as np, pandas as pd
from datetime import date, timedelta

tmp = tempfile.mkdtemp()
os.environ.update(EB_OUT=f"{tmp}/out", EB_START="2026-01-02", EB_END="2026-03-27", EB_MIN_TRADES="1", EB_ITM_MAX="3",
                  A8_OFFS_MAX="60", A8_MAX_OFFS="60", A8_TOP_N="10")
import engulf_rules as RU
import engulf_backtest as S
A = S.A
os.makedirs(A.OUT, exist_ok=True)


# ================================================================ 1. hand-made daily candles
def candles(rows):
    """rows = (open, high, low, close) per day."""
    a = np.array(rows, float); return a[:, 0], a[:, 1], a[:, 2], a[:, 3]


def base_days(n=12, start=100.0):
    """n flat-ish red/green alternating days well below the setup: highs rise slowly so the engulfing High can be the 10-day high."""
    out = []
    for k in range(n):
        o = start + 0.1 * k; c = o - 0.2 if k % 2 == 0 else o + 0.05                 # mostly red; prior to the engulfing candle the last day is RED
        out.append((o, max(o, c) + 0.1, min(o, c) - 0.1, c))
    return out


def setup_path(pull_closes, after, last_red=True, eng=None):
    """12 base days (the last is red), the engulfing day, the pullback days (given by their closes), then `after` days (open, high, low, close)."""
    d = base_days(12)
    if last_red:
        o = d[-1][0]; d[-1] = (o, o + 0.1, o - 1.1, o - 1.0)                       # red: open o, close o-1.0
    po, pc = d[-1][0], d[-1][3]
    eng = eng or (pc - 0.2, pc + 3.0 + 1.0, pc - 0.5, pc + 3.0)                  # green, open below prev close, close above prev open: engulfs; High far above the base
    d.append(eng)
    for c in pull_closes: d.append((c + 0.1, c + 0.6, c - 0.4, c))
    d += after
    return candles(d), len(base_days(12))


(O, H, L, C), i_eng = setup_path([0, 0, 0, 0, 0], [])                                  # placeholder to get geometry
# geometry: engulf candle fields
d12 = base_days(12); o = d12[-1][0]; prev_o, prev_c = o, o - 1.0
eng_o, eng_h, eng_l, eng_c = prev_c - 0.2, prev_c + 4.0, prev_c - 0.5, prev_c + 3.0
body_lo, body_hi = eng_o, eng_c
inside = (body_lo + body_hi) / 2


def build(pull_closes, after):
    (O, H, L, C), i = setup_path(pull_closes, after, True, (eng_o, eng_h, eng_l, eng_c))
    return O, H, L, C, i


# a valid setup: pullback closes inside the body (one of them), level = max High over engulf..pullback end, entry when High >= level
pb = [eng_c + 0.5, inside, eng_c + 0.2, eng_c - 0.3, eng_c + 0.1]                    # closes; day 2 inside the body
O, H, L, C, i = build(pb, [(eng_c, eng_c + 0.5, eng_c - 0.2, eng_c + 0.2)])           # one more day that does NOT reach the level
level = max(eng_h, max(h for h in H[i:i + 6]))
assert RU.is_engulfing(O, C, i) and C[i] > O[i]
n0 = len(C)
st = RU.engulf_setups(O, H, L, C, 5, 0, 10)
assert st == [], st                                                                    # the level (engulf High) is never touched after the window -> no entry day
after = [(eng_c, eng_h + 0.3, eng_c - 0.1, eng_c + 0.2)]                              # a day whose High is above the engulfing High = level
O, H, L, C, i = build(pb, [(eng_c, eng_c + 0.5, eng_c - 0.2, eng_c + 0.2)] + after)
st = RU.engulf_setups(O, H, L, C, 5, 0, 10)
assert len(st) == 1 and st[0]["engulf"] == i and st[0]["pb_end"] == i + 5 and st[0]["entry"] == i + 7, st
assert abs(st[0]["level"] - max(H[i:i + 6])) < 1e-9 and abs(st[0]["signal_low"] - eng_l) < 1e-9
# the level is the highest High of engulf..pullback end (a pullback day with a higher High raises the level)
pb2 = list(pb); O, H, L, C, i = build(pb2, [])
H2 = H.copy(); H2[i + 3] = eng_h + 1.0
# (rebuild the whole path with the raised pullback High and a day touching only the old level: no entry; touching the new level: entry)
d = list(zip(O, H2, L, C)); d.append((eng_c, eng_h + 0.3, eng_c - 0.1, eng_c + 0.2))
assert RU.engulf_setups(*candles(d), 5, 0, 10) == []
d[-1] = (eng_c, eng_h + 1.2, eng_c - 0.1, eng_c + 0.2)
r = RU.engulf_setups(*candles(d), 5, 0, 10); assert len(r) == 1 and abs(r[0]["level"] - (eng_h + 1.0)) < 1e-9 and r[0]["entry"] == len(d) - 1

# a pullback close BELOW the engulfing low kills the setup
bad = list(pb); bad[3] = eng_l - 0.3
O, H, L, C, i = build(bad, [(eng_c, eng_h + 0.3, eng_c - 0.1, eng_c + 0.2)]); assert RU.engulf_setups(O, H, L, C, 5, 0, 10) == []
# a pullback close exactly AT the low is fine (not below)
ok = list(pb); ok[3] = eng_l
O, H, L, C, i = build(ok, [(eng_c, eng_h + 0.3, eng_c - 0.1, eng_c + 0.2)]); assert len(RU.engulf_setups(O, H, L, C, 5, 0, 10)) == 1
# no pullback close inside the body -> no setup
nob = [eng_c + 0.5, eng_c + 0.4, eng_c + 0.2, eng_c + 0.6, eng_c + 0.1]
O, H, L, C, i = build(nob, [(eng_c, eng_h + 0.3, eng_c - 0.1, eng_c + 0.2)]); assert RU.engulf_setups(O, H, L, C, 5, 0, 10) == []
# a close exactly on the body edge counts as inside
edge = [eng_c + 0.5, body_hi, eng_c + 0.2, eng_c + 0.6, eng_c + 0.1]
O, H, L, C, i = build(edge, [(eng_c, eng_h + 0.3, eng_c - 0.1, eng_c + 0.2)]); assert len(RU.engulf_setups(O, H, L, C, 5, 0, 10)) == 1
# waiting: a close below the engulfing low BEFORE the cross cancels it; a close below on the SAME day as the cross does not (the cross comes first)
gap = [(eng_c, eng_c + 0.5, eng_c - 0.2, eng_c + 0.2), (eng_c, eng_c + 0.4, eng_l - 1.0, eng_l - 0.5), (eng_c, eng_h + 0.3, eng_c - 0.1, eng_c + 0.2)]
O, H, L, C, i = build(pb, gap); assert RU.engulf_setups(O, H, L, C, 5, 0, 10) == []
O, H, L, C, i = build(pb, [(eng_c, eng_c + 0.5, eng_c - 0.2, eng_c + 0.2), (eng_c, eng_h + 0.3, eng_l - 1.0, eng_l - 0.5)]); r = RU.engulf_setups(O, H, L, C, 5, 0, 10); assert len(r) == 1 and r[0]["entry"] == i + 7
# waiting limit
slow = [(eng_c, eng_c + 0.5, eng_c - 0.2, eng_c + 0.2)] * 4 + [(eng_c, eng_h + 0.3, eng_c - 0.1, eng_c + 0.2)]
O, H, L, C, i = build(pb, slow)
assert RU.engulf_setups(O, H, L, C, 5, 0, 10)[0]["entry"] == i + 10 and RU.engulf_setups(O, H, L, C, 5, 5, 10)[0]["entry"] == i + 10 and RU.engulf_setups(O, H, L, C, 5, 4, 10) == []
# previous candle GREEN -> not engulfing (needs a non-green previous candle)
dg = base_days(12); o = dg[-1][0]; dg[-1] = (o, o + 1.2, o - 0.1, o + 1.0)                        # green last base day
cands = dg + [(o - 0.5, o + 4.5, o - 0.6, o + 2.0)]
Og, Hg, Lg, Cg = candles(cands); assert not RU.is_engulfing(Og, Cg, 12)
# engulfing that does not reach the previous open / starts above the previous close is rejected
assert not RU.is_engulfing(np.array([10, 9.5]), np.array([9, 9.8]), 1)                        # close 9.8 < previous open 10
assert RU.is_engulfing(np.array([10, 8.9]), np.array([9, 10.5]), 1) and not RU.is_engulfing(np.array([10, 9.2]), np.array([9, 10.5]), 1)
# not at the 10-day high -> no setup: raise an earlier High above the engulfing High
O, H, L, C, i = build(pb, [(eng_c, eng_h + 0.3, eng_c - 0.1, eng_c + 0.2)])
H3 = H.copy(); H3[i - 3] = eng_h + 5.0; assert RU.engulf_setups(O, H3, L, C, 5, 0, 10) == []
# ... but a High 11 days back does not matter
H4 = H.copy(); H4[i - 10] = eng_h + 5.0; assert len(RU.engulf_setups(O, H4, L, C, 5, 0, 10)) == 1
# a cross in the pullback window itself is not an entry (the level already contains those Highs)
print("daily setup: hand-made cases OK")


# ================================================================ 2. random paths vs the original script's loop
def ref_setups(O, H, L, C, pull=5, wait=0, roll=10):
    """The original script (green_engulfing backtest) re-written line by line; only the entry-day check order (High first) and the end-of-data guard are explicit."""
    n = len(C); rh = pd.Series(H).rolling(roll).max().values
    green = C > O; pg = np.r_[False, green[:-1]]
    engulf = green & ~pg & (C >= np.r_[np.nan, O[:-1]]) & (O <= np.r_[np.nan, C[:-1]])
    at_hi = H >= rh
    out = []; i = 10
    while i < n - 1:
        if at_hi[i] and engulf[i]:
            low = L[i]; lo_b, hi_b = min(O[i], C[i]), max(O[i], C[i]); pe = i + pull
            if pe > n - 1: i += 1; continue
            dead, ov = False, False
            for j in range(i + 1, pe + 1):
                if C[j] < low: dead = True; break
                if lo_b <= C[j] <= hi_b: ov = True
            if dead or not ov: i += 1; continue
            ref = H[i:pe + 1].max(); e = -1
            for k in range(pe + 1, n):
                if wait and k - pe > wait: break
                if H[k] >= ref: e = k; break
                if C[k] < low: break
            if e != -1:
                out.append((i, pe, e, float(ref))); i = e
        i += 1
    return out


rng = np.random.default_rng(5)
nset = 0
for trial in range(1500):
    n = int(rng.integers(40, 400)); sig = float(rng.choice([0.008, 0.015, 0.03]))
    cl = 100 * np.exp(np.cumsum(rng.normal(0.0005, sig, n)))
    op = np.r_[cl[0], cl[:-1]] * (1 + rng.normal(0, sig / 3, n))
    hi = np.maximum(op, cl) * (1 + np.abs(rng.normal(0, sig / 2, n))); lo = np.minimum(op, cl) * (1 - np.abs(rng.normal(0, sig / 2, n)))
    pull = int(rng.choice([3, 5, 7])); wait = int(rng.choice([0, 0, 3, 10])); roll = 10
    got = [(s["engulf"], s["pb_end"], s["entry"], s["level"]) for s in RU.engulf_setups(op, hi, lo, cl, pull, wait, roll)]
    want = ref_setups(op, hi, lo, cl, pull, wait, roll)
    assert got == want, (trial, got, want)
    nset += len(got)
assert nset > 150, nset
print(f"daily setup == independent re-implementation on 1500 random paths ({nset} setups)")


# ================================================================ 3. the 1-minute entry
D0 = pd.Timestamp("2026-03-03")
minutes = pd.timedelta_range("09:15:00", "15:29:00", freq="min")


def mk(path, highs=None, drop=()):
    idx = pd.DatetimeIndex([D0 + m for m in minutes[:len(path)]])
    c = np.array(path, float); h = c.copy()
    for k, v in (highs or {}).items(): h[k] = v
    df = pd.DataFrame({"o": c, "h": np.maximum(h, c), "l": c, "c": c}, index=idx)
    return df.drop(df.index[list(drop)]) if drop else df


def pos(u, hhmm): return int(np.nonzero(u.index.strftime("%H:%M") == hhmm)[0][0])
def at(u, k): return None if k is None else u.index[k].strftime("%H:%M")


LV = 100.0
below = [99.0] * 375
b = mk(below); P = lambda t: pos(b, t)
assert RU.first_cross_long(mk(below), LV) is None
assert at(mk(below), RU.first_cross_long(mk(below, highs={P("11:00"): 100.0}), LV)) == "11:00" or True
u = mk(below, highs={P("11:00"): 100.0}); assert at(u, RU.first_cross_long(u, LV)) == "11:00"                      # High exactly at the level = touch
u = mk(below, highs={P("11:00"): 99.99}); assert RU.first_cross_long(u, LV) is None
u = mk([101.0] * 375); assert at(u, RU.first_cross_long(u, LV)) == "09:15"                                         # gap up: the first candle
u = mk(below, highs={P("15:20"): 100.5}); assert at(u, RU.first_cross_long(u, LV)) == "15:20"                      # last allowed minute
u = mk(below, highs={P("15:21"): 100.5}); assert RU.first_cross_long(u, LV) is None
u = mk(below, highs={P("10:00"): 100.5, P("12:00"): 101}); assert at(u, RU.first_cross_long(u, LV)) == "10:00"     # first one only
assert S.entries_for(mk(below, highs={P("11:00"): 100.5}), LV, False) == {}                                         # LONG only
assert list(S.entries_for(mk(below, highs={P("11:00"): 100.5}), LV, True)) == ["ENG"]
assert S.strategies_for("ENGULF", "ENG", -1, -1, -1, -1) == [S.STRAT] and S.strategies_for("BPB", "ENG", -1, -1, -1, -1) == [] and S.strategies_for("ENGULF", "ALL", -1, -1, -1, -1) == []
print("1-minute entry OK")

# ================================================================ 4. strategy settings + exit grid
assert S.STRATS == ["GREEN_ENGULF_LONG"] and A.EXITS == ["09:30", "10:00", "15:30"] and "UNTIL_HIT" not in A.EXITS
assert A.SLS == [0, 20, 40, 60] and A.TPS == [20, 40, 60, 80, 100, 120, 200] and len(A.VARS) == 3 * 4 * 7


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
print(f"exit grid (SL {A.SLS} x TP {A.TPS} x exits {A.EXITS}) == brute force on 12 random paths")

# ================================================================ 5. a simulated exchange
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
NOATM = set()                                                                     # days on which the ATM series has no candles (forces the ITM-1 fallback)


def exp_for(d): return next(e for e in EXP if e >= d)
def tv(d):
    e = exp_for(d); return 3.0 + 0.8 * (sum(1 for x in bd if d < x.date() <= e))
def epoch(idx): return [int(t.tz_localize("Asia/Kolkata").timestamp()) for t in idx]


class Fake:
    n = 0
    def post(self, path, body):
        self.n += 1
        if path == "/charts/intraday":
            a, b_ = body["fromDate"][:10], body["toDate"][:10]
            w = WORLD[(W_day >= date.fromisoformat(a)) & (W_day <= date.fromisoformat(b_))]
            return {"timestamp": epoch(w.index), "open": list(w.o), "high": list(w.h), "low": list(w.l), "close": list(w.c)}
        a, b_ = date.fromisoformat(body["fromDate"]), date.fromisoformat(body["toDate"])
        assert (b_ - a).days <= 30
        off = 0 if body["strike"] == "ATM" else int(body["strike"][3:])
        side = "LONG" if body["drvOptionType"] == "CALL" else "SHORT"
        w = WORLD[(W_day >= a) & (W_day < b_)]
        if off == 0 and NOATM: w = w[[d not in NOATM for d in W_day[(W_day >= a) & (W_day < b_)]]]
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
rows, want_entry = [], {}
for i, d in enumerate(dates):
    day = WORLD[(W_day == d) & (W_idx.hour * 60 + W_idx.minute <= LAST)]
    hi = day.h.values
    lvl = round(float(np.quantile(hi, [0.3, 0.6, 0.9][i % 3])), 2)                           # a level the day's High reaches during the day
    k = RU.first_cross_long(day, lvl, A.E_FIRST, LAST)
    assert k is not None
    want_entry[str(d)] = day.index[k].strftime("%H:%M")
    rows.append(dict(source="ENGULF", stock="AAA", direction="LONG", ref=lvl, signal_date=str(d - timedelta(days=1)), date=str(d), yahoo_open=float(day.o.iloc[0]),
                     green=-1, red=-1, upper_longer=-1, lower_longer=-1))
    # noise rows that must never produce an entry: other sources and a SHORT row
    rows.append(dict(source="BPB", stock="AAA", direction="LONG", ref=lvl, signal_date=str(d), date=str(d), yahoo_open=float(day.o.iloc[0]), green=-1, red=-1, upper_longer=-1, lower_longer=-1))
    rows.append(dict(source="ENGULF", stock="AAA", direction="SHORT", ref=lvl, signal_date=str(d), date=str(d), yahoo_open=float(day.o.iloc[0]), green=-1, red=-1, upper_longer=-1, lower_longer=-1))
cand = pd.DataFrame(rows)
NOATM.add(date.fromisoformat(cand[(cand.source == "ENGULF") & (cand.direction == "LONG")].date.iloc[7]))
st = A.load_state()
ev = A.step_events(dh, cand, mst, st)
assert len(ev) and set(ev.strategy) == {S.STRAT} and set(ev.type) == {"ENG"}
assert (ev.direction == "LONG").all() and (ev.source == "ENGULF").all()
for r in ev.itertuples():
    assert r.entry_minute == want_entry[r.date], (r.date, r.entry_minute, want_entry[r.date])
    assert "09:15" <= r.entry_minute <= "15:20"
assert len(ev) == len(dates) or len(ev) >= len(dates) - 2, (len(ev), len(dates))
ev = ev[(ev.date >= A.START) & (ev.date <= A.END)]
A.step_options(dh, ev, mst, st)
recs = A.load_records(); assert len(recs) > 0 and "strike_offset" in recs.columns
print(f"{len(cand)} candidate rows -> {len(ev)} entries -> {len(recs)} option records; Dhan calls {dh.n}")


def contract(side, K, d, te):
    e = exp_for(d); w = WORLD[(W_day >= d) & (W_day <= e)]; w = w[w.index > te]
    dts = [t.date() for t in w.index]; tvs = np.array([tv(x) for x in dts])
    g = lambda x: np.round(np.round(((np.maximum(x - K, 0) if side == "LONG" else np.maximum(K - x, 0)) + tvs) / .05) * .05, 2)
    po, pc = g(w.o.values), g(w.c.values); ph, pl = (g(w.h.values), g(w.l.values)) if side == "LONG" else (g(w.l.values), g(w.h.values))
    return pd.DataFrame({"o": po, "h": ph, "l": pl, "c": pc}, index=w.index), e


checked = n_itm = n_atm = 0
for r in recs.itertuples():
    te = pd.Timestamp(f"{r.date} {r.entry_minute}"); d = date.fromisoformat(r.date)
    atm = float(np.round(WORLD.c[te] / STEP) * STEP); off = int(r.strike_offset)
    K = atm + off * STEP                                                              # a call's ITM-n = ATM - n steps (offset -n)
    entry = float(np.round(((max(WORLD.c[te] - K, 0)) + tv(d)) / .05) * .05)
    assert r.direction == "LONG" and abs(r.strike - K) < 1e-9 and abs(r.entry_price - entry) < 1e-9 and r.cov >= 0.9, (r.ekey, r.strike, K, r.entry_price, entry, r.cov, off)
    if d in NOATM:
        assert off == -1, (r.ekey, off); n_itm += 1; continue                         # the ATM series was empty that day: ITM-1 (a lower strike for a call)
    assert off == 0 and r.cov >= 0.999; n_atm += 1
    Sx, e = contract("LONG", K, d, te)
    ls = np.array(json.loads(r.ls), float).reshape(-1, 3); hs = np.array(json.loads(r.hs), float).reshape(-1, 3)
    res = A.simulate_one(r.entry_price, ls, hs, json.loads(r.tx), json.loads(r.last))
    for v, (ex, sl, tp) in enumerate(A.VARS):
        want = brute(Sx, te, float(r.entry_price), sl, tp, ex); dm, px, code, late = res[v]
        if want is None: assert code == 0; continue
        assert code > 0 and te + pd.Timedelta(minutes=int(dm)) == want[0] and abs(px - want[1]) < 1e-6, (r.ekey, ex, sl, tp, res[v], want)
        checked += 1
assert n_itm >= 1 and n_atm > 20, (n_itm, n_atm)
print(f"{n_atm} ATM entries + {n_itm} ITM-1 fallback entries; {checked} trade outcomes ({len(A.VARS)} variants per entry) match the independent calculation")

# ---------------------------------------------------------------- result files
S.summary()
for f in ("SUMMARY.md", "summary.csv", "trades_summary.csv", "REPORT.txt", "matrix_total_pnl.csv", "matrix_roi_pct.csv", "matrix_win_pct.csv", "matrix_profit_factor.csv"):
    assert os.path.exists(f"{A.OUT}/{f}"), f
Sm = pd.read_csv(f"{A.OUT}/summary.csv")
assert set(Sm.strategy) == set(S.STRATS) and set(Sm.exit_rule) == set(A.EXITS) and set(Sm.sl) == {0, 20, 40, 60} and set(Sm.tp) == {20, 40, 60, 80, 100, 120, 200}
assert {"sl_rule", "tp_rule", "variant"} <= set(Sm.columns) and "no SL" in set(Sm.sl_rule)
M = pd.read_csv(f"{A.OUT}/matrix_total_pnl.csv")
assert list(M.columns) == ["strategy", "exit_rule", "stop_loss", "TP 20%", "TP 40%", "TP 60%", "TP 80%", "TP 100%", "TP 120%", "TP 200%"], list(M.columns)
assert len(M) == len(A.EXITS) * 4
T = pd.read_csv(f"{A.OUT}/trade_files/{S.STRAT}_all_variants_trades.csv")
assert (T.strategy == S.STRAT).all() and (T.direction == "LONG").all() and {"level", "strike_offset"} <= set(T.columns)
assert (pd.to_datetime(T.exit_date) == pd.to_datetime(T.entry_date)).all(), "every trade is closed on the entry day"
assert set(T.strike_offset.dropna().astype(int)) == {0, -1}
r0 = Sm.iloc[0]; sub = T[(T.exit_rule == r0.exit_rule) & (T.sl == r0.sl) & (T.tp == r0.tp)]
assert len(sub) == r0.trades and abs(sub.pnl.sum() - r0.total_pnl) <= len(sub)
Bt = pd.read_csv(f"{A.OUT}/trade_files/{S.STRAT}_best_trades.csv"); g = Sm.sort_values(["total_pnl", "trades"], ascending=False).iloc[0]
assert len(Bt) == g.trades and abs(Bt.pnl.sum() - g.total_pnl) <= len(Bt)
en = pd.read_csv(f"{A.OUT}/trade_files/{S.STRAT}_entries.csv"); assert len(en) and {"stock", "date", "entry_minute", "strike", "entry_price", "strike_offset"} <= set(en.columns)
md = open(f"{A.OUT}/SUMMARY.md").read()
assert S.STRAT in md or "GREEN ENGULFING" in md; assert "Rules" in md and "Strike used" in md and "Exit 15:30" in md
# the 09:30 / 10:00 exits only have the early entries
n = {ex: int(Sm[(Sm.exit_rule == ex) & (Sm.sl == 0) & (Sm.tp == 20)].trades.iloc[0]) for ex in A.EXITS}
assert n["09:30"] <= n["10:00"] <= n["15:30"], n
print("ALL OFFLINE TESTS PASSED")
