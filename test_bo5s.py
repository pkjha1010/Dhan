"""test_bo5s.py - offline test (no login, no network) of bo5s_rules.py and the bo5s_backtest.py pipeline (SHORT mirror: 10-day-low breakdown, lower Bollinger band, previous day red, longer lower wick, ATM PUT).
1. signals() == the mirrored conditions of your Colab script (pandas version below) on 300 random paths, and == the LONG rule applied to the price-negated series (a true mirror).
2. expiry / exit simulation are the shared bo5w code (tested by test_bo5w.py): here only the gap-rule label and flag direction.
3. process() with a fake Dhan: PUT entry leg, ITM = HIGHER strikes, strike lock through the ATM+n series after a fall, expiry-day next-month series, skip reasons.
4. summary() end to end on fake saved records."""
import os, json, tempfile
import numpy as np, pandas as pd
from datetime import date, timedelta
import bo5w_rules as RW
import bo5s_rules as R


def colab_short(O, H, L, C, n=10):
    df = pd.DataFrame(dict(Open=O, High=H, Low=L, Close=C))
    df["Prev_N_Low"] = df["Low"].shift(1).rolling(window=n).min()
    df["BB_Middle"] = df["Close"].rolling(window=20).mean(); df["BB_Std"] = df["Close"].rolling(window=20).std()
    df["BB_Lower"] = df["BB_Middle"] - 2 * df["BB_Std"]
    df["Prev_Day_Red"] = df["Close"].shift(1) < df["Open"].shift(1)
    up = df["High"] - df[["Open", "Close"]].max(axis=1); lo = df[["Open", "Close"]].min(axis=1) - df["Low"]
    df["Long_Lower_Wick"] = lo > up
    br = (df.Close < df.Prev_N_Low) & (df.Close < df.BB_Lower) & df.Prev_Day_Red & df.Long_Lower_Wick
    return {int(i) for i in np.nonzero(br.values)[0]}


rng = np.random.default_rng(5); tot = 0
for _ in range(300):
    n = 140; C = 100 * np.exp(np.cumsum(rng.normal(-0.002, .018, n)))
    O = np.r_[C[0], C[:-1]] * np.exp(rng.normal(0, .01, n))
    H = np.maximum(O, C) * (1 + np.abs(rng.normal(0, .01, n))); L = np.minimum(O, C) * (1 - np.abs(rng.normal(0, .01, n)))
    a = {i for i in colab_short(O, H, L, C, 10) if i < n - 1}
    b = {s["i"] for s in R.signals(O, H, L, C, 10, 20, 2.0, need_next=True)}
    assert a == b, sorted(a ^ b)
    m = {s["i"] for s in RW.signals(-O, -L, -H, -C, 10, 20, 2.0, need_next=True)}   # LONG rule on the negated series = SHORT rule
    assert m == b, sorted(m ^ b)
    tot += len(a)
assert tot > 100, tot
print(f"1. signals equal the mirrored script conditions AND the negated-series LONG rule on 300 random paths ({tot} breakdown days)")
assert R.REASON[7].startswith("GAP RULE (stock opened above") and R.simulate(100, [[555, 100, 130, 95, 120]], "0930c", 0, True, 0, 1) == (555, 100.0, 7, 0)
print("2. gap rule label / flag ok")

import bo5s_backtest as W
assert W.LOOKBACK == 10 and W.OUT == "bo5s_results"
B_DAY, B1 = date(2026, 3, 10), date(2026, 3, 11)
STEP = 10.0


def mk_day(day, spot_by_min, price_fn):
    mins = sorted(spot_by_min); idx = pd.DatetimeIndex([pd.Timestamp(f"{day} 00:00") + pd.Timedelta(minutes=m) for m in mins])

    def frame(off):
        atm = np.array([np.round(spot_by_min[m] / STEP) * STEP for m in mins]); K = atm + off * STEP
        p = np.array([price_fn(k, m) for k, m in zip(K, mins)])
        return pd.DataFrame(dict(o=p, h=p * 1.02, l=p * 0.98, c=p, strike=K), index=idx)
    return frame


price = lambda k, m: max(1.0, 1000 + 40 + k * 0.5 + (m % 7) * 0.1)                  # a put gets dearer with a higher strike
spot_b = {m: 996 for m in range(555, 930)}                                           # B: ATM strike 1000
spot_b1 = {m: (996 if m < 560 else max(968, 996 - (m - 559) * 3)) for m in range(555, 931)}   # B+1: spot falls -> ATM 1000, 990, 980, 970
calls = []


def fetch_ok(sid, d, off, code):
    calls.append((d, off, code))
    return mk_day(d, spot_b if d == B_DAY else spot_b1, price)(off)


mst = {"TEST": (1, 100)}
row = dict(stock="TEST", date=str(B_DAY), next_date=str(B1), expiry_day=0, gap_flag=1)
kind, rec = W.process(fetch_ok, mst, row)
assert kind == "ok", rec
assert rec["strike"] == 1000.0 and rec["strike_offset"] == 0 and rec["entry_time"] == "15:29", rec
cd = json.loads(rec["cd"])
assert cd[0][0] == 555 and len(cd) == 46 and all(abs(x[1] - price(1000, x[0])) < 0.01 for x in cd), "strike 1000 must be held at every minute"
assert any(d == B1 and off == 3 for d, off, c in calls), "after the fall strike 1000 is ATM+3 on B+1 (a put's strike is above the new ATM)"
assert not any(d == B_DAY and off != 0 for d, off, _ in calls)
print("3a. process(): PUT entry at 15:29, strike locked through ATM+3 on B+1, 46 candles ok")

calls.clear(); kind, rec = W.process(fetch_ok, mst, dict(row, expiry_day=1))
assert kind == "ok" and all(c == 2 for d, o, c in calls if d == B_DAY) and all(c == 1 for d, o, c in calls if d == B1), calls
print("3b. expiry day: next-month series for the entry leg (code 2), nearest for the exit day (code 1)")


def fetch_itm(sid, d, off, code):
    fr = fetch_ok(sid, d, off, code)
    return fr.iloc[0:0] if (d == B_DAY and off == 0) else fr


kind, rec = W.process(fetch_itm, mst, row)
assert kind == "ok" and rec["strike_offset"] == 1 and rec["strike"] == 1010.0, rec            # put ITM-1 = the next HIGHER strike
kind, why = W.process(lambda sid, d, off, code: fetch_ok(sid, d, off, code).iloc[0:0] if d == B_DAY else fetch_ok(sid, d, off, code), mst, row)
assert kind == "skip" and "near the close" in why, (kind, why)
kind, why = W.process(lambda sid, d, off, code: fetch_ok(sid, d, off, code) if d == B_DAY else fetch_ok(sid, d, off, code).iloc[0:0], mst, row)
assert kind == "skip" and "exit day" in why, (kind, why)
def fetch_fail(sid, d, off, code): raise W.CallFailed("x")
try: W.process(fetch_fail, mst, row); raise SystemExit("CallFailed not raised")
except W.CallFailed: pass
print("3c. ITM-1 = higher strike, skip reasons, failed-request handling ok")

with tempfile.TemporaryDirectory() as tmp:
    W.OUT = tmp; os.makedirs(f"{tmp}/parts"); os.makedirs(f"{tmp}/skipped")
    rng2 = np.random.default_rng(3); cands = []
    for k in range(40):
        d = date(2026, 1, 5) + timedelta(days=k * 3); st = f"S{k % 8}"; entry = float(rng2.uniform(8, 60)); gf = int(rng2.integers(0, 2))
        cds = []
        for m in range(555, 601):
            if rng2.random() < .1: continue
            p = entry * (1 + rng2.normal(0, .15)); cds.append([m, p, p * 1.03, p * .97, p * (1 + rng2.normal(0, .02))])
        json.dump(dict(stock=st, date=str(d), next_date=str(d + timedelta(days=1)), strike=100.0, strike_offset=0, entry_time="15:29", entry_price=round(entry, 2), lot=int(rng2.choice([250, 500, 1000, 1500])),
                       expiry_day=0, gap_flag=gf, cd=json.dumps(cds)), open(f"{tmp}/parts/{st}_{d}.json", "w"))
        cands.append(dict(stock=st, date=str(d), next_date=str(d + timedelta(days=1)), close=entry, open=entry, high=entry, low=entry, level_low=entry, lower_bb=entry, upper_wick=.5, lower_wick=1.0,
                          next_open=entry, gap_flag=gf, gap_pct=1.0 if gf else -1.0, expiry_day=0))
    json.dump(dict(stock="SK", date="2026-02-01", reason="no ATM / ITM option candle near the close of the breakdown day"), open(f"{tmp}/skipped/SK_2026-02-01.json", "w"))
    cands.append(dict(stock="SK", date="2026-02-01", next_date="2026-02-02", close=1, open=1, high=1, low=1, level_low=1, lower_bb=1, upper_wick=0, lower_wick=1, next_open=1, gap_flag=0, gap_pct=0, expiry_day=0))
    pd.DataFrame(cands).to_csv(f"{tmp}/candidates_{W.START}_{W.END}.csv", index=False)
    W.summary()
    for f in ("SUMMARY.md", "summary.csv", "signals.csv", "trades_all_variants.csv.gz", "trades_best_variant.csv", "by_month_best.csv", "matrix_total_pnl.csv", "PROGRESS.txt", "REPORT.txt"):
        assert os.path.exists(f"{tmp}/{f}"), f"missing {f}"
    S = pd.read_csv(f"{tmp}/summary.csv"); T = pd.read_csv(f"{tmp}/trades_all_variants.csv.gz")
    assert len(S) == len(W.VARS) == 280
    one = T[(T.exit_rule == "0915o") & (T.sl == 0) & (T.gap_rule == 1) & (T.tp == 0)]
    g = S[(S.sl == 0) & (S.gap_rule == 1) & (S.tp == 0)]
    assert (g.gap_rule_exits == int(one.stock_gap_down.sum())).all() and g.gap_rule_exits.iloc[0] > 0
    assert (S[S.gap_rule == 0].gap_rule_exits == 0).all()
    assert "SHORT" in open(f"{tmp}/SUMMARY.md").read() and "breakdown" in open(f"{tmp}/SUMMARY.md").read()
print("4. summary(): all result files written, 280 variants, gap rule counted")
print("ALL TESTS PASSED")
