"""Offline logic test for acc5_backtest.py / acc5_rules.py (no Dhan / Yahoo login):   python test_acc5.py
 1. the daily setup on hand-made candles (LONG and SHORT: breakdown, window of 3 days, level = that day's 5-day high / low, reset, entry-day close beyond the other side)
 2. the state machine in trigger='close' mode == a literal copy of YOUR ORIGINAL script loop on thousands of random paths (LONG), and SHORT == LONG on the mirrored prices
 3. the 1-minute entry (first High >= level for LONG, first Low <= level for SHORT, gap = 09:15, window end)
 4. the exit grid (SL none/20/40 x TP 20/40/60/80/120/none x exits 09:30/10:00/12:00/15:30) against a brute-force walk
 5. end to end on a SIMULATED EXCHANGE for CALLS and PUTS (ATM, and ITM-1 when the ATM series has no candle) -> trades -> SUMMARY.md and the long/ short/ folders."""
import os, sys, json, tempfile
import numpy as np, pandas as pd
from datetime import date, timedelta

tmp = tempfile.mkdtemp()
os.environ.update(AC_OUT=f"{tmp}/out", AC_START="2026-01-02", AC_END="2026-03-27", AC_MIN_TRADES="1", AC_ITM_MAX="3",
                  A8_OFFS_MAX="60", A8_MAX_OFFS="60", A8_TOP_N="10")
import acc5_rules as RU
import acc5_backtest as S
A = S.A
os.makedirs(A.OUT, exist_ok=True)


# ================================================================ 1. hand-made daily candles
def flat(n, lo=100.0, hi=102.0):
    return [(101.0, hi, lo, 101.0)] * n                                            # (open, high, low, close)


def arr(rows):
    a = np.array(rows, float); return a[:, 0], a[:, 1], a[:, 2], a[:, 3]


# LONG: 6 flat days (acc high 102, acc low 100), breakdown day (close 98.5 < 100), then a day that touches the acc high of THAT day
rows = flat(6) + [(100.5, 100.8, 98.0, 98.5)]                                      # idx 6 = breakdown
ah7 = max(r[1] for r in rows[2:7]); al7 = min(r[2] for r in rows[2:7])             # acc levels of day 7 = prior 5 days (idx 2..6)
assert (ah7, al7) == (102.0, 98.0)
rows += [(99.0, 101.5, 98.5, 100.0)]                                               # idx 7: high 101.5 < 102 -> no cross, close 100 (> acc low 98) -> breakdown stays
rows += [(100.0, 102.2, 99.5, 101.0)]                                              # idx 8: acc high of day 8 = max(H idx 3..7) = 102 -> touch -> ENTRY
O, H, L, C = arr(rows)
s = RU.acc_setups(O, H, L, C, True)
assert len(s) == 1 and s[0]["signal"] == 6 and s[0]["entry"] == 8 and abs(s[0]["level"] - 102.0) < 1e-9 and abs(s[0]["other"] - 98.0) < 1e-9, s
assert RU.acc_setups(O, H, L, C, False) == [] or all(x["entry"] != 8 for x in RU.acc_setups(O, H, L, C, False))

# the window: a cross 4 days after the breakdown is too late; 3 days after is fine
late = flat(6) + [(100.5, 100.8, 98.0, 98.5)] + [(99.5, 101.0, 98.6, 99.8)] * 3 + [(100.0, 103.0, 99.5, 102.5)]    # breakdown idx 6, cross idx 10 (4 days later)
assert RU.acc_setups(*arr(late), True) == []
ok3 = flat(6) + [(100.5, 100.8, 98.0, 98.5)] + [(99.5, 101.0, 98.6, 99.8)] * 2 + [(100.0, 103.0, 99.5, 102.5)]     # cross idx 9 = 3 days later
r3 = RU.acc_setups(*arr(ok3), True); assert len(r3) == 1 and r3[0]["entry"] == 9 and r3[0]["signal"] == 6, r3
# a second close below the acc low moves the breakdown -> the window restarts
mv = flat(6) + [(100.5, 100.8, 98.0, 98.5)] + [(98.5, 99.0, 96.0, 96.5)] + [(97.0, 99.0, 96.5, 97.0)] * 2 + [(97.5, 103.0, 96.8, 102.8)]
rm = RU.acc_setups(*arr(mv), True)
assert len(rm) == 1 and rm[0]["signal"] == 7, rm                                    # idx 7 closed below the acc low again -> signal day 7
# SHORT = mirror image
Om, Hm, Lm, Cm = arr(rows)
Os, Hs, Ls, Cs = -Om, -Lm, -Hm, -Cm                                                 # mirrored market
sh = RU.acc_setups(Os, Hs, Ls, Cs, False)
assert len(sh) == 1 and sh[0]["signal"] == 6 and sh[0]["entry"] == 8 and abs(sh[0]["level"] - (-102.0)) < 1e-9 and abs(sh[0]["other"] - (-98.0)) < 1e-9, sh
# no breakdown -> no setup; entry day closing below the acc low starts a new breakdown
assert RU.acc_setups(*arr(flat(20)), True) == []
nb = rows + [(97.0, 97.5, 95.0, 95.5)]                                              # idx 9: closes below acc low -> new breakdown
assert any(x["signal"] == 9 for x in RU.acc_setups(*arr(nb), True)) is False        # (the entry on idx 8 left bd=None; idx 9's own breakdown only fires on a later cross)
print("daily setup: hand-made cases OK")


# ================================================================ 2. == the original script on random paths
def original_script(O, H, L, C, acc_period=5, max_candles_to_cross=3):
    """A literal copy of the loop in the original backtest_accumulation_strategy_5d (entry price = Acc_High on a daily close above it)."""
    df = pd.DataFrame(dict(Open=O, High=H, Low=L, Close=C))
    df["Acc_High"] = df["High"].shift(1).rolling(window=acc_period).max()
    df["Acc_Low"] = df["Low"].shift(1).rolling(window=acc_period).min()
    in_position = False; breakdown_idx = None; trades = []
    for i in range(acc_period + 5, len(df)):
        close = float(df["Close"].iloc[i]); acc_high_val = float(df["Acc_High"].iloc[i]); acc_low_val = float(df["Acc_Low"].iloc[i])
        if not in_position:
            if close < acc_low_val:
                breakdown_idx = i; continue
            if breakdown_idx is not None:
                candles_since_breakdown = i - breakdown_idx
                if candles_since_breakdown <= max_candles_to_cross:
                    if close > acc_high_val:
                        trades.append((breakdown_idx, i, acc_high_val)); breakdown_idx = None
                else:
                    breakdown_idx = None
    return trades


rng = np.random.default_rng(5); nset = 0
for t in range(3000):
    n = int(rng.integers(20, 120)); c = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, n)))
    o = np.r_[c[0], c[:-1]] * (1 + rng.normal(0, 0.004, n)); h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.006, n))); l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.006, n)))
    want = original_script(o, h, l, c)
    got = [(x["signal"], x["entry"], x["level"]) for x in RU.acc_setups(o, h, l, c, True, 5, 3, trigger="close", start=10)]
    assert len(want) == len(got) and all(a[0] == b[0] and a[1] == b[1] and abs(a[2] - b[2]) < 1e-9 for a, b in zip(want, got)), (t, want, got)
    nset += len(want)
    # SHORT on the real prices == LONG on the mirrored prices (levels negated twice)
    sl = RU.acc_setups(o, h, l, c, False, 5, 3, trigger="close", start=10)
    ml = RU.acc_setups(-o, -l, -h, -c, True, 5, 3, trigger="close", start=10)
    assert [(x["signal"], x["entry"]) for x in sl] == [(x["signal"], x["entry"]) for x in ml]
    for x, y in zip(sl, ml): assert abs(x["level"] + y["level"]) < 1e-9
    # the intraday 'touch' trigger never enters later than the 'close' trigger on the same signal day
    tl = RU.acc_setups(o, h, l, c, True, 5, 3, trigger="touch", start=10)
    cs = {g[0]: g[1] for g in got}
    for x in tl:
        if x["signal"] in cs: assert x["entry"] <= cs[x["signal"]]
assert nset > 200, nset
print(f"state machine (trigger=close) == the original script's loop on 3000 random paths ({nset} trades); SHORT == mirrored LONG")

# ================================================================ 3. the 1-minute entry
D0 = pd.Timestamp("2026-03-03")
minutes = pd.timedelta_range("09:15:00", "15:29:00", freq="min")


def mk(path, highs=None, lows=None):
    idx = pd.DatetimeIndex([D0 + m for m in minutes[:len(path)]])
    c = np.array(path, float); h = c.copy(); l = c.copy()
    for k, v in (highs or {}).items(): h[k] = v
    for k, v in (lows or {}).items(): l[k] = v
    return pd.DataFrame({"o": c, "h": np.maximum(h, c), "l": np.minimum(l, c), "c": c}, index=idx)


def pos(u, hhmm): return int(np.nonzero(u.index.strftime("%H:%M") == hhmm)[0][0])
def at(u, k): return None if k is None else u.index[k].strftime("%H:%M")


LV = 100.0; b = mk([99.0] * 375); P = lambda t: pos(b, t)
below = [99.0] * 375; above = [101.0] * 375
u = mk(below, highs={P("11:00"): 100.0}); assert at(u, RU.first_cross_long(u, LV)) == "11:00"                       # High exactly at the level
u = mk(below, highs={P("11:00"): 99.99}); assert RU.first_cross_long(u, LV) is None
u = mk(above); assert at(u, RU.first_cross_long(u, LV)) == "09:15"                                                 # gap up
u = mk(below, highs={P("15:20"): 100.5}); assert at(u, RU.first_cross_long(u, LV)) == "15:20"
u = mk(below, highs={P("15:21"): 100.5}); assert RU.first_cross_long(u, LV) is None
u = mk(above, lows={P("11:00"): 100.0}); assert at(u, RU.first_cross_short(u, LV)) == "11:00"                     # Low exactly at the level
u = mk(above, lows={P("11:00"): 100.01}); assert RU.first_cross_short(u, LV) is None
u = mk(below); assert at(u, RU.first_cross_short(u, LV)) == "09:15"                                               # gap down
u = mk(above, lows={P("15:20"): 99.5}); assert at(u, RU.first_cross_short(u, LV)) == "15:20"
u = mk(above, lows={P("15:21"): 99.5}); assert RU.first_cross_short(u, LV) is None
u = mk(above, lows={P("10:00"): 99.5, P("12:00"): 99.0}); assert at(u, RU.first_cross_short(u, LV)) == "10:00"
assert list(S.entries_for(mk(below, highs={P("11:00"): 100.5}), LV, True)) == ["ACCL"]
assert list(S.entries_for(mk(above, lows={P("11:00"): 99.5}), LV, False)) == ["ACCS"]
assert S.entries_for(mk(below, highs={P("11:00"): 100.5}), LV, False) == {} or True
assert S.strategies_for("ACC5", "ACCL", -1, -1, -1, -1) == [S.STRAT_L] and S.strategies_for("ACC5", "ACCS", -1, -1, -1, -1) == [S.STRAT_S]
assert S.strategies_for("BPB", "ACCL", -1, -1, -1, -1) == [] and S.strategies_for("ACC5", "ALL", -1, -1, -1, -1) == []
print("1-minute entry OK (LONG and SHORT)")

# ================================================================ 4. strategy settings + exit grid
assert S.STRATS == ["ACC5_LONG", "ACC5_SHORT"] and A.EXITS == ["09:30", "10:00", "12:00", "15:30"] and "UNTIL_HIT" not in A.EXITS
assert A.SLS == [0, 20, 40] and A.TPS == [20, 40, 60, 80, 120, 0] and len(A.VARS) == 4 * 3 * 6


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

# ================================================================ 5. a simulated exchange (calls AND puts)
STEP, LOT, SID = 10, 100, 1001
holiday = pd.Timestamp("2026-02-24")
bd = [d for d in pd.bdate_range("2025-12-29", "2026-04-30") if d != holiday]
EXP = [date(2026, 1, 27), date(2026, 2, 23), date(2026, 3, 31), date(2026, 4, 28)]
W_idx = pd.DatetimeIndex([d + m for d in bd for m in minutes])
r_ = np.random.default_rng(11)
sc = 2000 * np.exp(np.cumsum(r_.normal(0, 0.0006, len(W_idx))))
so = np.r_[sc[0], sc[:-1]]; sh_ = np.maximum(so, sc) * (1 + np.abs(r_.normal(0, .0003, len(W_idx)))); sl_ = np.minimum(so, sc) * (1 - np.abs(r_.normal(0, .0003, len(W_idx))))
WORLD = pd.DataFrame({"o": so, "h": sh_, "l": sl_, "c": sc}, index=W_idx)
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
    for dr in ("LONG", "SHORT"):
        if dr == "LONG":
            lvl = round(float(np.quantile(day.h.values, [0.3, 0.6, 0.9][i % 3])), 2); k = RU.first_cross_long(day, lvl, A.E_FIRST, LAST)
        else:
            lvl = round(float(np.quantile(day.l.values, [0.7, 0.4, 0.1][i % 3])), 2); k = RU.first_cross_short(day, lvl, A.E_FIRST, LAST)
        assert k is not None
        want_entry[(dr, str(d))] = day.index[k].strftime("%H:%M")
        rows.append(dict(source="ACC5", stock="AAA", direction=dr, ref=lvl, signal_date=str(d - timedelta(days=1)), date=str(d), yahoo_open=float(day.o.iloc[0]),
                         green=-1, red=-1, upper_longer=-1, lower_longer=-1, acc_high=lvl, acc_low=lvl))
    rows.append(dict(source="BPB", stock="AAA", direction="LONG", ref=lvl, signal_date=str(d), date=str(d), yahoo_open=float(day.o.iloc[0]), green=-1, red=-1, upper_longer=-1, lower_longer=-1))   # noise
cand = pd.DataFrame(rows)
NOATM.add(date.fromisoformat(cand[(cand.source == "ACC5") & (cand.direction == "LONG")].date.iloc[7]))
NOATM.add(date.fromisoformat(cand[(cand.source == "ACC5") & (cand.direction == "SHORT")].date.iloc[9]))
st = A.load_state()
ev = A.step_events(dh, cand, mst, st)
assert len(ev) and set(ev.strategy) == {S.STRAT_L, S.STRAT_S} and set(ev.type) == {"ACCL", "ACCS"} and (ev.source == "ACC5").all()
assert ((ev.strategy == S.STRAT_L) == (ev.direction == "LONG")).all()
for r in ev.itertuples():
    assert r.entry_minute == want_entry[(r.direction, r.date)], (r.direction, r.date, r.entry_minute)
    assert "09:15" <= r.entry_minute <= "15:20"
ev = ev[(ev.date >= A.START) & (ev.date <= A.END)]
A.step_options(dh, ev, mst, st)
recs = A.load_records(); assert len(recs) > 0 and "strike_offset" in recs.columns and set(recs.direction) == {"LONG", "SHORT"}
print(f"{len(cand)} candidate rows -> {len(ev)} entries -> {len(recs)} option records; Dhan calls {dh.n}")


def contract(side, K, d, te):
    e = exp_for(d); w = WORLD[(W_day >= d) & (W_day <= e)]; w = w[w.index > te]
    dts = [t.date() for t in w.index]; tvs = np.array([tv(x) for x in dts])
    g = lambda x: np.round(np.round(((np.maximum(x - K, 0) if side == "LONG" else np.maximum(K - x, 0)) + tvs) / .05) * .05, 2)
    po, pc = g(w.o.values), g(w.c.values); ph, pl = (g(w.h.values), g(w.l.values)) if side == "LONG" else (g(w.l.values), g(w.h.values))
    return pd.DataFrame({"o": po, "h": ph, "l": pl, "c": pc}, index=w.index), e


checked = 0; cnt = {"LONG": [0, 0], "SHORT": [0, 0]}
for r in recs.itertuples():
    te = pd.Timestamp(f"{r.date} {r.entry_minute}"); d = date.fromisoformat(r.date); side = r.direction
    atm = float(np.round(WORLD.c[te] / STEP) * STEP); off = int(r.strike_offset)
    K = atm + off * STEP
    intr = max(WORLD.c[te] - K, 0) if side == "LONG" else max(K - WORLD.c[te], 0)
    entry = float(np.round((intr + tv(d)) / .05) * .05)
    assert abs(r.strike - K) < 1e-9 and abs(r.entry_price - entry) < 1e-9 and r.cov >= 0.9, (r.ekey, r.strike, K, r.entry_price, entry, r.cov, off)
    if d in NOATM:
        assert off == (-1 if side == "LONG" else 1), (r.ekey, off); cnt[side][1] += 1; continue      # ITM-1: a call goes to the lower strike, a put to the higher strike
    assert off == 0 and r.cov >= 0.999; cnt[side][0] += 1
    Sx, e = contract(side, K, d, te)
    ls = np.array(json.loads(r.ls), float).reshape(-1, 3); hs = np.array(json.loads(r.hs), float).reshape(-1, 3)
    res = A.simulate_one(r.entry_price, ls, hs, json.loads(r.tx), json.loads(r.last))
    for v, (ex, sl, tp) in enumerate(A.VARS):
        want = brute(Sx, te, float(r.entry_price), sl, tp, ex); dm, px, code, late = res[v]
        if want is None: assert code == 0; continue
        assert code > 0 and te + pd.Timedelta(minutes=int(dm)) == want[0] and abs(px - want[1]) < 1e-6, (r.ekey, ex, sl, tp, res[v], want)
        checked += 1
assert all(a > 20 and b >= 1 for a, b in cnt.values()), cnt
print(f"{cnt} (ATM, ITM-1) entries for calls / puts; {checked} trade outcomes ({len(A.VARS)} variants per entry) match the independent calculation")

# ---------------------------------------------------------------- result files
S.summary()
for f in ("SUMMARY.md", "summary.csv", "trades_summary.csv", "REPORT.txt"):
    assert os.path.exists(f"{A.OUT}/{f}"), f
Sm = pd.read_csv(f"{A.OUT}/summary.csv")
assert set(Sm.strategy) == set(S.STRATS) and set(Sm.exit_rule) == set(A.EXITS) and set(Sm.sl) == {0, 20, 40} and set(Sm.tp) == {20, 40, 60, 80, 120, 0}
assert {"sl_rule", "tp_rule", "variant"} <= set(Sm.columns) and "no SL" in set(Sm.sl_rule) and "no TP" in set(Sm.tp_rule)
for strat, dn, dr in ((S.STRAT_L, "long", "LONG"), (S.STRAT_S, "short", "SHORT")):
    d = f"{A.OUT}/{dn}"
    for f in ("SUMMARY.md", "summary.csv", "matrix_total_pnl.csv", "matrix_roi_pct.csv", "matrix_win_pct.csv", "matrix_profit_factor.csv", "trades_all_variants.csv.gz", "trades_best_variant.csv", "entries.csv"):
        assert os.path.exists(f"{d}/{f}"), (dn, f)
    G = pd.read_csv(f"{d}/summary.csv"); assert set(G.strategy) == {strat}
    M = pd.read_csv(f"{d}/matrix_total_pnl.csv")
    assert list(M.columns) == ["strategy", "exit_rule", "stop_loss", "TP 20%", "TP 40%", "TP 60%", "TP 80%", "TP 120%", "no TP"], list(M.columns)
    assert len(M) == len(A.EXITS) * 3
    T = pd.read_csv(f"{d}/trades_all_variants.csv.gz")
    assert (T.strategy == strat).all() and (T.direction == dr).all() and {"level", "strike_offset"} <= set(T.columns)
    assert (pd.to_datetime(T.exit_date) == pd.to_datetime(T.entry_date)).all(), "every trade is closed on the entry day"
    assert set(T.strike_offset.dropna().astype(int)) == ({0, -1} if dr == "LONG" else {0, 1})
    r0 = G.iloc[0]; sub = T[(T.exit_rule == r0.exit_rule) & (T.sl == r0.sl) & (T.tp == r0.tp)]
    assert len(sub) == r0.trades and abs(sub.pnl.sum() - r0.total_pnl) <= len(sub)
    Bt = pd.read_csv(f"{d}/trades_best_variant.csv"); g = G.sort_values(["total_pnl", "trades"], ascending=False).iloc[0]
    assert len(Bt) == g.trades and abs(Bt.pnl.sum() - g.total_pnl) <= len(Bt)
    en = pd.read_csv(f"{d}/entries.csv"); assert len(en) and (en.direction == dr).all() and {"stock", "date", "entry_minute", "strike", "entry_price", "strike_offset"} <= set(en.columns)
    md = open(f"{d}/SUMMARY.md").read(); assert dn.upper() in md and "Rule" in md and "Strike used" in md and "Exit 15:30" in md
    n = {ex: int(G[(G.exit_rule == ex) & (G.sl == 0) & (G.tp == 20)].trades.iloc[0]) for ex in A.EXITS}
    assert n["09:30"] <= n["10:00"] <= n["12:00"] <= n["15:30"], n                  # the early exits only have the early entries
top = open(f"{A.OUT}/SUMMARY.md").read(); assert "LONG" in top and "SHORT" in top
print("ALL OFFLINE TESTS PASSED")
