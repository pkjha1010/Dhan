"""test_bpb_bb.py - offline test (no login, no network) of bpb_bb_rules.py, the engine hooks of bpb_bb_backtest.py and bpb_bb_report.py.
Main checks: the 'enter from B+3' machine gives EXACTLY the trades of your attached skip-first-day script (loop copied below) on random price paths, LONG and SHORT; 'enter from B+2' equals the same
script without the day counter; B = breakout day and B+n are right."""
import numpy as np, pandas as pd
import bpb_bb_rules as R

LOOKBACK, BB_PERIOD, BB_STD = 5, 20, 2.0


def original_loop(df, min_days_armed):
    """Your script's per-ticker code, copied.  min_days_armed = 1 -> the condition `days_armed > 1` of your script (skip-first-day version); 0 -> no day counter (the previous version).
    -> list of (type, row index of the entry day, entry level, breakout row index)."""
    df = df.copy()
    df['High_Lookback'] = df['High'].shift(1).rolling(window=LOOKBACK).max()
    df['Low_Lookback'] = df['Low'].shift(1).rolling(window=LOOKBACK).min()
    df['BB_Mid'] = df['Close'].rolling(window=BB_PERIOD).mean()
    df['BB_Std'] = df['Close'].rolling(window=BB_PERIOD).std()
    df['BB_Upper'] = df['BB_Mid'] + (BB_STD * df['BB_Std'])
    df['BB_Lower'] = df['BB_Mid'] - (BB_STD * df['BB_Std'])
    l_state, l_line, l_entry_price, l_days_armed = "SEARCHING", 0.0, 0.0, 0
    s_state, s_line, s_entry_price, s_days_armed = "SEARCHING", 0.0, 0.0, 0
    lB = sB = -1
    trades = []
    start_idx = max(LOOKBACK, BB_PERIOD) + 5
    i = start_idx
    while i < len(df):
        y_close = df['Close'].iloc[i-1]; y_high = df['High'].iloc[i-1]; y_low = df['Low'].iloc[i-1]
        h_lb_y = df['High_Lookback'].iloc[i-1]; l_lb_y = df['Low_Lookback'].iloc[i-1]
        bb_upper_y = df['BB_Upper'].iloc[i-1]; bb_lower_y = df['BB_Lower'].iloc[i-1]
        c_high = df['High'].iloc[i]; c_low = df['Low'].iloc[i]
        if l_state == "SEARCHING":
            if y_close > h_lb_y:
                l_state = "ARMED"; l_line = h_lb_y; l_entry_price = y_high; l_days_armed = 0; lB = i - 1
        elif l_state == "ARMED":
            if y_close < l_line:
                l_state = "SEARCHING"
                if y_close > h_lb_y:
                    l_state = "ARMED"; l_line = h_lb_y; l_entry_price = y_high; l_days_armed = 0; lB = i - 1
            else:
                l_days_armed += 1
                if l_days_armed > min_days_armed:
                    if c_high >= l_entry_price:
                        if y_close > bb_upper_y: trades.append(("LONG", i, l_entry_price, lB))
                        l_state = "SEARCHING"
        if s_state == "SEARCHING":
            if y_close < l_lb_y:
                s_state = "ARMED"; s_line = l_lb_y; s_entry_price = y_low; s_days_armed = 0; sB = i - 1
        elif s_state == "ARMED":
            if y_close > s_line:
                s_state = "SEARCHING"
                if y_close < l_lb_y:
                    s_state = "ARMED"; s_line = l_lb_y; s_entry_price = y_low; s_days_armed = 0; sB = i - 1
            else:
                s_days_armed += 1
                if s_days_armed > min_days_armed:
                    if c_low <= s_entry_price:
                        if y_close < bb_lower_y: trades.append(("SHORT", i, s_entry_price, sB))
                        s_state = "SEARCHING"
        i += 1
    return trades


def random_df(rng, n=420):
    vol = rng.choice([0.008, 0.015, 0.03]); drift = rng.choice([-0.001, 0.0, 0.001])
    c = 100 * np.exp(np.cumsum(rng.normal(drift, vol, n)))
    o = np.r_[100, c[:-1]] * (1 + rng.normal(0, vol / 3, n))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, vol / 2, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, vol / 2, n)))
    return pd.DataFrame({"Open": o, "High": h, "Low": l, "Close": c})


rng = np.random.default_rng(11)
tot = {2: 0, 3: 0}; minb = {1: 99, 2: 99, 3: 99}
for p in range(500):
    df = random_df(rng)
    O, H, L, C = (df[k].values for k in ("Open", "High", "Low", "Close"))
    for long in (True, False):
        t = "LONG" if long else "SHORT"
        for k, skip in ((3, 1), (2, 0)):
            ref = [(i, round(x, 9), b) for ty, i, x, b in original_loop(df, skip) if ty == t]
            got = [(s["entry"], round(s["level"], 9), s["breakout"]) for s in R.setups(H, L, C, long, 5, k) if s["bb_ok"]]
            assert got == ref, (p, t, k, got[:4], ref[:4])
            tot[k] += len(ref)
        for k in (1, 2, 3):
            for s in R.setups(H, L, C, long, 5, k):
                assert s["b_plus"] == s["entry"] - s["breakout"] and s["b_plus"] >= k, s
                minb[k] = min(minb[k], s["b_plus"])
        cs = R.candidates(H, L, C, long, 5, bb_only=False)
        for r in cs:
            assert r["b_plus"] == r["entry"] - r["breakout"]
        cs2 = R.candidates(H, L, C, long, 5, bb_only=True)
        assert [r["entry"] for r in cs2] == [r["entry"] for r in cs if r["bb_ok"]] and all(r["bb_ok"] == 1 for r in cs2)
assert tot[3] > 200 and tot[2] > 200 and minb == {1: 1, 2: 2, 3: 3}, (tot, minb)
print(f"'enter from B+3' == your script and 'enter from B+2' == the version without the day counter on 500 random paths x LONG/SHORT ({tot[3]} / {tot[2]} trades); earliest entry day per rule: {minb}")

# ---- hand-made path: breakout day B = 50, every later day touches the level -> B+1 / B+2 / B+3 per rule
n, B = 80, 50
c = np.full(n, 100.0) + np.random.default_rng(1).normal(0, .2, n)
for k in range(B, n): c[k] = 106 + 2 * (k - B)
h = c + 1.0; l = c - 1.0; h[B] = 106.5
for k, want in ((1, 51), (2, 52), (3, 53)):
    s = R.setups(h, l, c, True, 5, k)[0]
    assert s["breakout"] == B and s["entry"] == want and s["b_plus"] == want - B and abs(s["level"] - 106.5) < 1e-9 and s["bb_ok"], (k, s)
cs = R.candidates(h, l, c, True, 5)
first = [r for r in cs if r["breakout"] == B]
assert [(r["b_plus"], r["from_b1"], r["from_b2"], r["from_b3"]) for r in first] == [(1, 1, 0, 0), (2, 0, 1, 0), (3, 0, 0, 1)], first
# the SHORT mirror of the same path (prices reflected around 200)
c2, h2, l2 = 200 - c, 200 - l, 200 - h
for k, want in ((1, 51), (2, 52), (3, 53)):
    s = R.setups(h2, l2, c2, False, 5, k)[0]
    assert s["breakout"] == B and s["entry"] == want and abs(s["level"] - (200 - 106.5)) < 1e-9 and s["bb_ok"], (k, s)
print("hand-made B+1 / B+2 / B+3 case OK (LONG and SHORT)")

# ---- engine hooks
import bpb_bb_backtest as BB
M = np.arange(9 * 60 + 15, 15 * 60 + 29 + 1)
idx = pd.to_datetime("2026-01-05 00:00") + pd.to_timedelta(M, unit="m")
hi = np.where(M >= 11 * 60, 101.0, 99.0)
u = pd.DataFrame({"o": hi, "h": hi, "l": hi - 3, "c": hi}, index=idx)
e = BB.entries_for(u, 100.0, True); assert list(e) == ["BPBL"] and e["BPBL"].strftime("%H:%M") == "11:00", e
lo_ = np.where(M >= 13 * 60 + 5, 98.0, 102.0)
d = pd.DataFrame({"o": lo_, "h": lo_ + 2, "l": lo_, "c": lo_}, index=idx)
e = BB.entries_for(d, 100.0, False); assert list(e) == ["BPBS"] and e["BPBS"].strftime("%H:%M") == "13:05", e
late = pd.DataFrame({"o": 99.0, "h": np.where(M == 15 * 60 + 29, 101.0, 99.0), "l": 98.0, "c": 99.0}, index=idx)
assert BB.entries_for(late, 100.0, True)["BPBL"].strftime("%H:%M") == "15:29"
assert BB.entries_for(u, 120.0, True) == {} and BB.entries_for(d, 90.0, False) == {}
assert BB.strategies_for("BPB", "BPBL", -1, -1, -1, -1) == ["BPBBB_LONG"] and BB.strategies_for("BPB", "BPBS", -1, -1, -1, -1) == ["BPBBB_SHORT"]
assert BB.A.STRATS == ["BPBBB_LONG", "BPBBB_SHORT"] and BB.A.EXITS == ["09:30", "10:00", "12:00", "15:00", "15:30"], (BB.A.STRATS, BB.A.EXITS)
assert BB.A.SLS == [0, 20, 40, 60] and BB.A.TPS == [40, 60, 80, 120, 0] and len(BB.A.VARS) == 5 * 4 * 5
assert BB.A.ENTRY_LAST == "15:29" and BB.A.COV_MIN == 0.0 and BB.LOOKBACK == 5 and BB.BB_ONLY
dates = [str(x.date()) for x in pd.bdate_range("2025-01-01", periods=n)]
O = c - 0.5
rows = BB.setups_to_rows("TEST", dates, O, h, l, c, pd.Timestamp("2025-01-01"), pd.Timestamp("2026-12-31"))
r0 = [r for r in rows if r["direction"] == "LONG" and r["signal_date"] == dates[B]]
assert [(r["b_label"], r["date"], r["from_b1"], r["from_b2"], r["from_b3"]) for r in r0] == [("B+1", dates[51], 1, 0, 0), ("B+2", dates[52], 0, 1, 0), ("B+3", dates[53], 0, 0, 1)], r0
assert all(r["ref"] == 106.5 and r["bb_ok"] == 1 for r in r0)
BB.print_rules()

# ---- report: sets, per-direction files, B+n columns
import bpb_bb_report as RP
rows = []
for k, (b, f1, f2, f3, ok, d_) in enumerate([(3, 1, 1, 1, 1, "LONG"), (2, 1, 1, 0, 1, "LONG"), (1, 1, 0, 0, 1, "LONG"), (7, 1, 1, 1, 1, "LONG"), (3, 1, 1, 1, 0, "LONG")]):
    for ex in ("15:30", "09:30"):
        rows.append(dict(direction=d_, exit_rule=ex, sl=0, tp=0, stock="S%d" % k, entry_date="2026-01-0%d" % (k + 1), entry_time="10:00", entry_price=10.0, cost=1000.0, pnl=100.0 * (k + 1), ret_pct=10.0,
                         b_plus=b, b_label=f"B+{b}", from_b1=f1, from_b2=f2, from_b3=f3, bb_ok=ok))
T = pd.DataFrame(rows)
S_ = RP.build_sets(T.copy())
assert {k: len(v) for k, v in S_.items() if "noBB" not in k} == {"B+1 onward": 8, "B+2 onward": 6, "B+3 onward (your script)": 4}, {k: len(v) for k, v in S_.items()}
assert len(S_["B+3 onward (your script) noBB"]) == 6 and set(S_["B+1 onward"].entry_day) == {"B+1", "B+2", "B+3", "B+6 or later"}
S, Bp = RP.stats_tables(S_, 0)
assert S[(S.set == "B+3 onward (your script)") & (S.exit_rule == "15:30")].trades.iloc[0] == 2
assert set(Bp[Bp.set == "B+1 onward"].entry_day) == {"B+1", "B+2", "B+3", "B+6 or later"}
print("report sets OK")
print("test_bpb_bb OK")
