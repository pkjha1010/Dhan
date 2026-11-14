"""test_bpb_bb.py - offline test (no login, no network) of bpb_bb_rules.py and the engine hooks of bpb_bb_backtest.py.
The main check: bpb_bb_rules.orig_setups(eod_check=True) + the Bollinger flag give EXACTLY the trades of your attached script's loop (copied below) on random price paths, LONG and SHORT."""
import numpy as np, pandas as pd
import bpb_bb_rules as R

LOOKBACK, BB_PERIOD, BB_STD = 10, 20, 2.0


def original_loop(df, FILTER_MODE):
    """Your script's per-ticker code, copied (FILTER_MODE NONE / BOLLINGER).  -> list of (type, row index, entry price)."""
    df = df.copy()
    df['High_10'] = df['High'].shift(1).rolling(window=LOOKBACK).max()
    df['Low_10'] = df['Low'].shift(1).rolling(window=LOOKBACK).min()
    if FILTER_MODE == "BOLLINGER":
        df['BB_Mid'] = df['Close'].rolling(window=BB_PERIOD).mean()
        df['BB_Std'] = df['Close'].rolling(window=BB_PERIOD).std()
        df['Filter_Upper'] = df['BB_Mid'] + (BB_STD * df['BB_Std'])
        df['Filter_Lower'] = df['BB_Mid'] - (BB_STD * df['BB_Std'])
    else:
        df['Filter_Upper'] = np.inf
        df['Filter_Lower'] = -np.inf
    l_state, l_line, l_highest = "SEARCHING", 0.0, 0.0
    s_state, s_line, s_lowest = "SEARCHING", 0.0, 0.0
    trades = []
    start_idx = max(LOOKBACK, BB_PERIOD) + 5
    for i in range(start_idx, len(df)):
        c_close = df['Close'].iloc[i]; c_high = df['High'].iloc[i]; c_low = df['Low'].iloc[i]
        h10 = df['High_10'].iloc[i]; l10 = df['Low_10'].iloc[i]
        f_upper = df['Filter_Upper'].iloc[i]; f_lower = df['Filter_Lower'].iloc[i]
        if l_state == "SEARCHING":
            if c_close > h10:
                l_state = "PULLBACK_PHASE"; l_line = h10; l_highest = c_high
        elif l_state == "PULLBACK_PHASE":
            if c_close < l_line:
                l_state = "SEARCHING"
                if c_close > h10:
                    l_state = "PULLBACK_PHASE"; l_line = h10; l_highest = c_high
            else:
                if c_high >= l_highest:
                    if FILTER_MODE == "NONE" or c_close > f_upper:
                        trades.append(("LONG", i, l_highest))
                    l_state = "SEARCHING"
                else:
                    if c_high > l_highest: l_highest = c_high
        if s_state == "SEARCHING":
            if c_close < l10:
                s_state = "PULLBACK_PHASE"; s_line = l10; s_lowest = c_low
        elif s_state == "PULLBACK_PHASE":
            if c_close > s_line:
                s_state = "SEARCHING"
                if c_close < l10:
                    s_state = "PULLBACK_PHASE"; s_line = l10; s_lowest = c_low
            else:
                if c_low <= s_lowest:
                    if FILTER_MODE == "NONE" or c_close < f_lower:
                        trades.append(("SHORT", i, s_lowest))
                    s_state = "SEARCHING"
                else:
                    if c_low < s_lowest: s_lowest = c_low
    return trades


def random_df(rng, n=420):
    vol = rng.choice([0.008, 0.015, 0.03]); drift = rng.choice([-0.001, 0.0, 0.001])
    c = 100 * np.exp(np.cumsum(rng.normal(drift, vol, n)))
    o = np.r_[100, c[:-1]] * (1 + rng.normal(0, vol / 3, n))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, vol / 2, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, vol / 2, n)))
    return pd.DataFrame({"Open": o, "High": h, "Low": l, "Close": c})


rng = np.random.default_rng(7)
n_paths = n_entries = n_bb = 0
for p in range(400):
    df = random_df(rng)
    O, H, L, C = (df[k].values for k in ("Open", "High", "Low", "Close"))
    for long in (True, False):
        t = "LONG" if long else "SHORT"
        ref_none = [(i, round(x, 9)) for ty, i, x in original_loop(df, "NONE") if ty == t]
        ref_bb = [(i, round(x, 9)) for ty, i, x in original_loop(df, "BOLLINGER") if ty == t]
        mine = R.orig_setups(O, H, L, C, long, 10, eod_check=True)
        got_none = [(s["entry"], round(s["level"], 9)) for s in mine]
        got_bb = [(s["entry"], round(s["level"], 9)) for s in mine if R.bb_flags(C, s["entry"], long)[0]]
        assert got_none == ref_none, (p, t, got_none[:5], ref_none[:5])
        assert got_bb == ref_bb, (p, t, got_bb[:5], ref_bb[:5])
        n_entries += len(ref_none); n_bb += len(ref_bb)
        # union candidates: every original entry is there with in_orig, bb_eod agrees with the original filter
        cs = R.candidates(O, H, L, C, long, 10)
        orig_in = [(c["entry"], round(c["level"], 9)) for c in cs if c["in_orig"]]
        assert [(c["entry"], round(c["level"], 9)) for c in cs if c["in_orig"] and c["bb_eod"]] == [x for x in ref_bb if x in orig_in]
    n_paths += 1
assert n_entries > 300 and n_bb > 20, (n_entries, n_bb)
print(f"original loop == rules on {n_paths} random paths x LONG/SHORT: {n_entries} entries, {n_bb} pass the Bollinger filter")

# ---- hand-made case: the day touches the level but closes BELOW the line -> original: no trade; live machine: entry
H = np.array([10.0] * 30 + [12.0, 12.5, 12.6]); L = H - 1.0
O = np.array([9.5] * 30 + [10.5, 12.0, 11.0]); C = np.array([9.5] * 30 + [11.8, 12.0, 9.0])
lo = R.orig_setups(O, H, L, C, True, 10, eod_check=False); og = R.orig_setups(O, H, L, C, True, 10, eod_check=True)
assert [s["entry"] for s in lo] == [31] , lo            # day 31: High 12.5 >= 12.0 (breakout day High), live entry
# day 31 closes at 12.0 >= line 10 so the original also enters; make day 31 close below the line instead:
C2 = C.copy(); C2[31] = 9.0; O2 = O.copy()
lo = R.orig_setups(O2, H, L, C2, True, 10, eod_check=False); og = R.orig_setups(O2, H, L, C2, True, 10, eod_check=True)
assert [s["entry"] for s in lo] == [31] and [s["entry"] for s in og] == [], (lo, og)
cs = R.candidates(O2, H, L, C2, True, 10)
assert len(cs) == 1 and cs[0]["in_live"] and not cs[0]["in_orig"] and abs(cs[0]["level"] - 12.0) < 1e-9, cs
# SHORT mirror of the same path
Os, Hs, Ls, Cs = 20 - O2, 20 - L, 20 - H, 20 - C2
cs = R.candidates(Os, Hs, Ls, Cs, False, 10)
assert len(cs) == 1 and cs[0]["in_live"] and not cs[0]["in_orig"] and abs(cs[0]["level"] - 8.0) < 1e-9, cs
print("look-ahead case OK (original skips, live machine enters)")

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
assert BB.entries_for(late, 100.0, True)["BPBL"].strftime("%H:%M") == "15:29"          # the last minute of the day is still an entry (nothing skipped)
assert BB.entries_for(u, 120.0, True) == {} and BB.entries_for(d, 90.0, False) == {}
assert BB.strategies_for("BPB", "BPBL", -1, -1, -1, -1) == ["BPBBB_LONG"] and BB.strategies_for("BPB", "BPBS", -1, -1, -1, -1) == ["BPBBB_SHORT"]
assert BB.A.STRATS == ["BPBBB_LONG", "BPBBB_SHORT"] and BB.A.EXITS == ["09:30", "10:00", "12:00", "15:00", "15:30"], (BB.A.STRATS, BB.A.EXITS)
assert BB.A.SLS == [0, 20, 40, 60] and BB.A.TPS == [40, 60, 80, 120, 0] and len(BB.A.VARS) == 5 * 4 * 5, (BB.A.SLS, BB.A.TPS, len(BB.A.VARS))
assert BB.A.ENTRY_LAST == "15:29" and BB.A.COV_MIN == 0.0
dates = [str(x.date()) for x in pd.bdate_range("2026-01-01", periods=33)]
rows = BB.setups_to_rows("TEST", dates, O2, H, L, C2, pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31"))
assert [(r["direction"], r["ref"], r["in_live"], r["in_orig"]) for r in rows if r["direction"] == "LONG"] == [("LONG", 12.0, True, False)], rows
BB.print_rules()

# ---- report: the four sets are subsets of the same trades
import bpb_bb_report as RP
rows = []
for k, (io, il, eod, px, band, d) in enumerate([(1, 1, 1, 105, 100, "LONG"), (1, 1, 0, 95, 100, "LONG"), (0, 1, 0, 106, 100, "LONG"), (1, 1, 1, 95, 100, "SHORT"), (0, 1, 0, 105, 100, "SHORT")]):
    for ex in ("15:30", "09:30"):
        rows.append(dict(direction=d, exit_rule=ex, sl=0, tp=0, stock="S%d" % k, entry_date="2026-01-0%d" % (k + 1), entry_time="10:00", entry_price=10.0, cost=1000.0, pnl=100.0 * (k + 1), ret_pct=10.0,
                         in_orig=io, in_live=il, bb_eod=eod, band_prev=band, stock_price=px * 2, ref_yahoo=50.0, level=100.0 if d == "LONG" else 100.0))
T = pd.DataFrame(rows)
sets = {}
S_ = RP.build_sets(T.copy())
assert len(S_["ALL"]) == 10 and len(S_["ORIG"]) == 6 and len(S_["BB_EOD"]) == 4, {k: len(v) for k, v in S_.items()}
# BB_LIVE: stock_price*ref_yahoo/level = px  -> LONG keeps px > band (rows 0 and 2), SHORT keeps px < band (row 3)
assert sorted(S_["BB_LIVE"].stock.unique()) == ["S0", "S2", "S3"], S_["BB_LIVE"].stock.unique()
tab = RP.stats_table(S_, 0); assert set(tab.set) == {"ALL", "ORIG", "BB_EOD", "BB_LIVE"} and tab[(tab.set == "BB_EOD") & (tab.direction == "LONG") & (tab.exit_rule == "15:30")].trades.iloc[0] == 1
print("report sets OK")
print("test_bpb_bb OK")
