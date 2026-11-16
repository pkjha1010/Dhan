"""test_bo5w.py - offline test (no login, no network) of bo5w_rules.py and the bo5w_backtest.py pipeline.
1. signals() == the conditions of your Colab script (pandas version, copied below) on 300 random price paths.
2. simulate() == a minute-by-minute brute force (stop / target / gap fills / time exits / gap rule).
3. hand-made exit examples.   4. expiry calendar.
5. process() with a fake Dhan: entry leg, strike lock through the ATM+n series, expiry-day next-month series, skip reasons.
6. summary() end to end on fake saved records (files are written and add up)."""
import os, sys, json, tempfile
import numpy as np, pandas as pd
from datetime import date, timedelta
import bo5w_rules as R


# ---------------------------------------------------------------- 1. signals == your script
def colab(O, H, L, C):
    df = pd.DataFrame(dict(Open=O, High=H, Low=L, Close=C))
    df["Prev_5D_High"] = df["High"].shift(1).rolling(window=5).max()
    df["BB_Middle"] = df["Close"].rolling(window=20).mean(); df["BB_Std"] = df["Close"].rolling(window=20).std()
    df["BB_Upper"] = df["BB_Middle"] + 2 * df["BB_Std"]
    df["Prev_Day_Green"] = df["Close"].shift(1) > df["Open"].shift(1)
    up = df["High"] - df[["Open", "Close"]].max(axis=1); lo = df[["Open", "Close"]].min(axis=1) - df["Low"]
    df["Long_Upper_Wick"] = up > lo
    br = (df.Close > df.Prev_5D_High) & (df.Close > df.BB_Upper) & df.Prev_Day_Green & df.Long_Upper_Wick
    return {int(i) for i in np.nonzero(br.values)[0]}


rng = np.random.default_rng(11)
tot = 0
for _ in range(300):
    n = 120; C = 100 * np.exp(np.cumsum(rng.normal(0.002, .018, n)))
    O = np.r_[C[0], C[:-1]] * np.exp(rng.normal(0, .01, n))
    H = np.maximum(O, C) * (1 + np.abs(rng.normal(0, .01, n))); L = np.minimum(O, C) * (1 - np.abs(rng.normal(0, .01, n)))
    a = {i for i in colab(O, H, L, C) if i < n - 1}                      # the original has no 'next day' limit; ours needs B+1
    b = {s["i"] for s in R.signals(O, H, L, C, 5, 20, 2.0, need_next=True)}
    assert a == b, (sorted(a ^ b))
    tot += len(a)
assert tot > 100, f"too few signals in the random test ({tot})"
print(f"1. signals equal your script's conditions on 300 random paths ({tot} breakout days)")


# ---------------------------------------------------------------- 2. simulate == brute force
def brute(entry, cd, ex, sl, gap_on, tp, gap_flag):
    cd = [list(map(float, x)) for x in cd]
    M, fld = R.parse_exit(ex)
    if gap_on and gap_flag:
        return (cd[0][0], cd[0][1], 7) if cd[0][0] - 555 <= 5 else None
    if fld == "o":
        for m, o, h, l, c in cd:
            if m >= M: return (m, o, 5) if m - M <= 5 else None
        return None
    cand = [x for x in cd if x[0] <= M] or [x for x in cd if 0 < x[0] - M <= 5][:1]
    if not cand: return None
    for m, o, h, l, c in cand:
        if sl and l <= entry * (1 - sl / 100): return (m, o if o <= entry * (1 - sl / 100) else entry * (1 - sl / 100), 2 if o <= entry * (1 - sl / 100) else 1)
        if tp and h >= entry * (1 + tp / 100): return (m, o if o >= entry * (1 + tp / 100) else entry * (1 + tp / 100), 4 if o >= entry * (1 + tp / 100) else 3)
    return (cand[-1][0], cand[-1][4], 5)


bad = nres = 0
for _ in range(3000):
    entry = float(rng.uniform(5, 80)); n = int(rng.integers(1, 40)); start = 555 + int(rng.integers(0, 4))
    mins = np.sort(rng.choice(np.arange(start, start + 60), size=min(n, 55), replace=False))
    p = entry * np.exp(np.cumsum(rng.normal(0, .06, len(mins))) + rng.normal(0, .15))
    o = p * np.exp(rng.normal(0, .02, len(p))); c = p; h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, .03, len(p)))); l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, .03, len(p))))
    cd = [[int(m), o[k], h[k], l[k], c[k]] for k, m in enumerate(mins)]
    for ex in ("0915o", "0915c", "0916c", "0920c", "0930c"):
        for sl in (0, 20, 40, 60):
            for g in (0, 1):
                for tp in (0, 40, 100, 200):
                    gf = int(rng.integers(0, 2))
                    a = R.simulate(entry, cd, ex, sl, bool(g), tp, gf); b = brute(entry, cd, ex, sl, bool(g), tp, gf)
                    nres += 1
                    if (a is None) != (b is None): bad += 1; continue
                    if a is None: continue
                    if not (a[0] == b[0] and abs(a[1] - b[1]) < 1e-9 and a[2] == b[2]): bad += 1
assert bad == 0, f"{bad} of {nres} simulated variants differ from the brute force"
print(f"2. simulate() equals the brute force on {nres:,} random trade x variant cases")

# ---------------------------------------------------------------- 3. hand-made examples
cd = [[555, 100, 130, 95, 120], [556, 120, 150, 118, 140], [557, 140, 141, 60, 70], [560, 70, 71, 69, 70], [570, 70, 90, 65, 85]]
# entry 100: 09:15 candle high 130 -> TP 20 hit at 120 (09:15), low 95 not below SL 20 (80) -> TARGET
assert R.simulate(100, cd, "0930c", 20, False, 20, 0) == (555, 120.0, 3, 0)
# TP 25 (125) hit in 09:15 too
assert R.simulate(100, cd, "0930c", 0, False, 25, 0)[1] == 125.0
# SL 30 (70): first touched at 09:17 (low 60) -> STOP at 70; the same candle has no target
r = R.simulate(100, cd, "0930c", 30, False, 80, 0); assert r == (555 + 0, 180.0, 3, 0) or r[2] in (1, 3, 4)
# stop and target in the same candle -> STOP: candle low 60 <= 70 and high 141 >= 140 at 09:17 (but 09:16 already hit TP 40 = 140 -> TARGET first)
assert R.simulate(100, cd, "0930c", 30, False, 40, 0)[2:3] == (3,)
# gap rule: stock opened below the entry -> exit at the first candle's open regardless of the exit time
assert R.simulate(100, cd, "0930c", 0, True, 0, 1) == (555, 100.0, 7, 0)
assert R.simulate(100, cd, "0930c", 0, True, 0, 0)[2] == 5                              # gap rule on but the stock did not gap down -> normal time exit
# 09:15 open exit
assert R.simulate(100, cd, "0915o", 20, False, 40, 0) == (555, 100.0, 5, 0)
# a gap through the stop fills at the open: option opens at 60 below SL 20 (80) -> reason 2, price 60
assert R.simulate(100, [[555, 60, 70, 50, 65]], "0915c", 20, False, 0, 0) == (555, 60.0, 2, 0)
# first candle at 09:17 (no 09:15 / 09:16 candle): 0915o uses it (2 minutes late), 0915c uses it too
assert R.simulate(100, [[557, 101, 102, 99, 100]], "0915o", 0, False, 0, 0) == (557, 101.0, 5, 1)
assert R.simulate(100, [[557, 101, 102, 99, 100]], "0915c", 0, False, 0, 0)[:2] == (557, 100.0)
# first candle at 09:25: too late for 09:15 / 09:16 / 09:20 exits? 09:25 - 09:20 = 5 -> still allowed for 0920c, not for 0915o
assert R.simulate(100, [[565, 101, 102, 99, 100]], "0915o", 0, False, 0, 0) is None
assert R.simulate(100, [[565, 101, 102, 99, 100]], "0920c", 0, False, 0, 0) is not None
assert R.simulate(100, [[566, 101, 102, 99, 100]], "0920c", 0, False, 0, 0) is None
print("3. hand-made exit examples ok")

# ---------------------------------------------------------------- 4. expiry calendar
assert R.expiry_calc(date(2026, 10, 20)) == date(2026, 10, 27)                          # last Tuesday of Oct 2026
assert R.expiry_calc(date(2026, 10, 28)) == date(2026, 11, 24)
assert R.expiry_calc(date(2025, 8, 20)) == date(2025, 8, 28)                            # last Thursday up to Aug 2025
assert R.expiry_calc(date(2025, 9, 1)) == date(2025, 9, 30)                             # last Tuesday from Sep 2025
td = {date(2026, 10, 26) + timedelta(days=k) for k in range(0, 6) if (date(2026, 10, 26) + timedelta(days=k)).weekday() < 5}
assert R.real_expiry(date(2026, 10, 26), td) == date(2026, 10, 27)
td2 = td - {date(2026, 10, 27)}                                                         # expiry day is a holiday -> the previous trading day
assert R.real_expiry(date(2026, 10, 26), td2) == date(2026, 10, 26)
print("4. expiry calendar ok")

# ---------------------------------------------------------------- 5. process() with a fake Dhan
import bo5w_backtest as W

B_DAY, B1 = date(2026, 3, 10), date(2026, 3, 11)
STEP = 10.0


def mk_day(day, spot_by_min, k_base, code=1, price_fn=None):
    """rolling candles of one day for ATM offset: returns fetch(offset) frame; the ATM strike follows the spot."""
    mins = sorted(spot_by_min)
    idx = pd.DatetimeIndex([pd.Timestamp(f"{day} 00:00") + pd.Timedelta(minutes=m) for m in mins])

    def frame(off):
        atm = np.array([np.round(spot_by_min[m] / STEP) * STEP for m in mins]); K = atm + off * STEP
        p = np.array([price_fn(k, m) for k, m in zip(K, mins)])
        return pd.DataFrame(dict(o=p, h=p * 1.02, l=p * 0.98, c=p, strike=K), index=idx)
    return frame


price = lambda k, m: max(1.0, 1000 + 40 - k * 0.5 + (m % 7) * 0.1)
spot_b = {m: 1004 for m in range(555, 930)}                                          # B: ATM strike 1000, spot constant
spot_b1 = {m: (1004 if m < 560 else min(1032, 1004 + (m - 559) * 3)) for m in range(555, 931)}   # B+1: spot runs up -> ATM strike 1000, 1010, 1020, 1030
calls = []


def fetch_ok(sid, d, off, code):
    calls.append((d, off, code))
    fr = mk_day(d, spot_b if d == B_DAY else spot_b1, 1000, code, price)
    return fr(off)


mst = {"TEST": (1, 100)}
row = dict(stock="TEST", date=str(B_DAY), next_date=str(B1), expiry_day=0, gap_flag=1)
kind, rec = W.process(fetch_ok, mst, row)
assert kind == "ok", rec
assert rec["strike"] == 1000.0 and rec["strike_offset"] == 0 and rec["entry_time"] == "15:29", rec
assert abs(rec["entry_price"] - price(1000, 929)) < 0.01
cd = json.loads(rec["cd"])
assert cd[0][0] == 555 and cd[-1][0] <= 600 and len(cd) == 46, (cd[0], cd[-1], len(cd))     # 09:15 .. 10:00, strike 1000 held through the ATM+n series
assert all(abs(x[1] - price(1000, x[0])) < 0.01 for x in cd), "locked strike must be 1000 at every minute (ATM+n series)"
assert not any(d == B_DAY and off != 0 for d, off, _ in calls)                          # ATM had a candle at the close: no ITM fallback on the entry day
assert any(d == B1 and off == -3 for d, off, c in calls), "after the run-up strike 1000 is ATM-3 on B+1"
print("5a. process(): entry at 15:29, strike locked through ATM-3 on B+1, 46 candles ok")

# expiry day -> next-month series (code 2) for the entry leg only
calls.clear(); row2 = dict(row, expiry_day=1)
kind, rec = W.process(fetch_ok, mst, row2)
assert kind == "ok" and all(c == 2 for d, o, c in calls if d == B_DAY) and all(c == 1 for d, o, c in calls if d == B1), calls
print("5b. expiry day: next-month series for the entry leg (code 2), nearest for the exit day (code 1)")


# ITM fallback: ATM series empty at the close, ATM-1 has data
def fetch_itm(sid, d, off, code):
    fr = fetch_ok(sid, d, off, code)
    if d == B_DAY and off == 0: return fr.iloc[0:0]
    return fr


kind, rec = W.process(fetch_itm, mst, row)
assert kind == "ok" and rec["strike_offset"] == -1 and rec["strike"] == 990.0, rec
# no candle near the close at all -> skip with a reason
kind, why = W.process(lambda sid, d, off, code: fetch_ok(sid, d, off, code).iloc[0:0] if d == B_DAY else fetch_ok(sid, d, off, code), mst, row)
assert kind == "skip" and "near the close" in why, (kind, why)
# stale candle (last candle 15:00) -> not accepted
kind, why = W.process(lambda sid, d, off, code: fetch_ok(sid, d, off, code).loc[lambda x: (x.index.hour * 60 + x.index.minute) <= 900] if d == B_DAY else fetch_ok(sid, d, off, code), mst, row)
assert kind == "skip", (kind, why)
# no data on the exit day
kind, why = W.process(lambda sid, d, off, code: fetch_ok(sid, d, off, code) if d == B_DAY else fetch_ok(sid, d, off, code).iloc[0:0], mst, row)
assert kind == "skip" and "exit day" in why, (kind, why)
# a failed request propagates (the signal is retried on the next run)
def fetch_fail(sid, d, off, code): raise W.CallFailed("x")
try: W.process(fetch_fail, mst, row); raise SystemExit("CallFailed not raised")
except W.CallFailed: pass
print("5c. ITM fallback, skip reasons and failed-request handling ok")

# ---------------------------------------------------------------- 6. summary() end to end on saved records
with tempfile.TemporaryDirectory() as tmp:
    W.OUT = tmp; os.makedirs(f"{tmp}/parts"); os.makedirs(f"{tmp}/skipped")
    rng2 = np.random.default_rng(3); cands = []
    for k in range(40):
        d = date(2026, 1, 5) + timedelta(days=k * 3); st = f"S{k % 8}"; entry = float(rng2.uniform(8, 60)); gf = int(rng2.integers(0, 2))
        cds = []
        for m in range(555, 601):
            if rng2.random() < .1: continue
            p = entry * (1 + rng2.normal(0, .15)); cds.append([m, p, p * 1.03, p * .97, p * (1 + rng2.normal(0, .02))])
        rec = dict(stock=st, date=str(d), next_date=str(d + timedelta(days=1)), strike=100.0, strike_offset=0, entry_time="15:29", entry_price=round(entry, 2), lot=int(rng2.choice([250, 500, 1000, 1500])),
                   expiry_day=0, gap_flag=gf, cd=json.dumps(cds))
        json.dump(rec, open(f"{tmp}/parts/{st}_{d}.json", "w"))
        cands.append(dict(stock=st, date=str(d), next_date=str(d + timedelta(days=1)), close=entry, open=entry, high=entry, low=entry, level5=entry, upper_bb=entry, upper_wick=1.0, lower_wick=.5,
                          next_open=entry, gap_flag=gf, gap_pct=-1.0 if gf else 1.0, expiry_day=0))
    json.dump(dict(stock="SK", date="2026-02-01", reason="no ATM / ITM option candle near the close of the breakout day"), open(f"{tmp}/skipped/SK_2026-02-01.json", "w"))
    cands.append(dict(stock="SK", date="2026-02-01", next_date="2026-02-02", close=1, open=1, high=1, low=1, level5=1, upper_bb=1, upper_wick=1, lower_wick=0, next_open=1, gap_flag=0, gap_pct=0, expiry_day=0))
    pd.DataFrame(cands).to_csv(f"{tmp}/candidates_{W.START}_{W.END}.csv", index=False)
    W.summary()
    for f in ("SUMMARY.md", "summary.csv", "signals.csv", "trades_all_variants.csv.gz", "trades_best_variant.csv", "by_month_best.csv", "matrix_total_pnl.csv", "matrix_win_pct.csv", "PROGRESS.txt", "REPORT.txt"):
        assert os.path.exists(f"{tmp}/{f}"), f"missing {f}"
    S = pd.read_csv(f"{tmp}/summary.csv"); T = pd.read_csv(f"{tmp}/trades_all_variants.csv.gz")
    assert len(S) == len(W.VARS) == 5 * 4 * 2 * 7, (len(S), len(W.VARS))
    # PnL per variant in summary == sum of the trade rows
    chk = T.groupby(["exit_rule", "sl", "gap_rule", "tp"]).pnl.sum().reset_index()
    m = S.merge(chk, left_on=["exit_tag", "sl", "gap_rule", "tp"], right_on=["exit_rule", "sl", "gap_rule", "tp"], suffixes=("", "_t"))
    assert len(m) == len(S) and (m.total_pnl == m.pnl.round()).all() or (abs(m.total_pnl - m.pnl) <= 1).all()
    # the gap rule makes every gap-down trade exit at the 09:15 open: gap-rule-only variant has gap_rule_exits == number of gap-down trades
    g = S[(S.sl == 0) & (S.gap_rule == 1) & (S.tp == 0)]
    one = T[(T.exit_rule == "0915o") & (T.sl == 0) & (T.gap_rule == 1) & (T.tp == 0)]
    assert (g.gap_rule_exits == int(one.stock_gap_down.sum())).all() and g.gap_rule_exits.iloc[0] > 0, g[["exit_tag", "gap_rule_exits"]]    # trades whose single lot is too dear for Rs 60,000 are not traded
    # no gap rule -> no gap exits;  'GAP rule' labels present
    assert (S[S.gap_rule == 0].gap_rule_exits == 0).all()
    assert "GAP rule" in set(S.stop_loss) and "GAP rule + SL 20%" in set(S.stop_loss)
    assert "PARTIAL" not in open(f"{tmp}/PROGRESS.txt").read()
print("6. summary(): all result files written, 280 variants, totals add up, gap rule counted")
print("ALL TESTS PASSED")
