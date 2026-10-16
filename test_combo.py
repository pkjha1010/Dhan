"""Offline logic test for combo_dayrisk_backtest.py (no Dhan / Yahoo login):  python test_combo.py"""
import os, json, tempfile
import numpy as np, pandas as pd

tmp = tempfile.mkdtemp()
os.environ.update(COMBO_OUT=tmp, COMBO_START="2026-01-01", COMBO_END="2026-12-31", DAY_SLS="0,5000,12000")
import combo_dayrisk_backtest as C

# ---- 1. shape_signals: breakout day, then a close back below the line -> signal, entry next day
H = np.array([10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12, 11, 11.5, 12.5, 12.0], float)
L = H - 1; O = H - .5; Cl = np.array([9.5] * 10 + [11.5, 11, 9.8, 9.9, 11.8, 11], float)      # day10 closes above ref 10; day12 closes back below it
sig = C.shape_signals(O, H, L, Cl, True)
assert [(n, r) for n, r, i in sig] == [(12, 10.0), (13, 10.0)], sig
assert all(i == 10 for _, _, i in sig)

# ---- 2. entry types
def mk(closes, highs=None, lows=None):
    idx = pd.date_range("2026-03-02 09:15", periods=len(closes), freq="min")
    c = np.array(closes, float); h = np.array(highs if highs is not None else closes, float) + .01; l = np.array(lows if lows is not None else closes, float) - .01
    return pd.DataFrame({"o": c, "h": h, "l": l, "c": c}, index=idx)
u = mk([99, 99, 99, 99, 99, 99, 101, 98, 99, 101, 102])                       # LONG, line 100: first close beyond at 09:21 (index 6)
e = C.entries_for(u, 100.0, True)
assert f"{e['ALL']:%H:%M}" == "09:21" and "OPEN_0915" not in e
assert f"{e['FROM_0920_4C']:%H:%M}" == "09:21" and f"{e['RECROSS_0920_4C']:%H:%M}" == "09:24", e
u = mk([101, 101, 101, 101, 101])
e = C.entries_for(u, 100.0, True)
assert f"{e['OPEN_0915']:%H:%M}" == "09:15" and "FROM_0920_4C" not in e                  # already beyond the line: no "4 closes on the other side"
u = mk([101, 101, 99, 99, 99, 99, 101, 99])                                          # SHORT mirror: line 100, below = beyond
e = C.entries_for(mk([99, 99, 101, 101, 101, 101, 99]), 100.0, False)
assert f"{e['ALL']:%H:%M}" == "09:15" and f"{e['FROM_0920_4C']:%H:%M}" == "09:21", e

# ---- 3. trade_curve
path = [[556, 10, 10.5, 9.5, 10], [557, 9.5, 9.6, 8.9, 9.0], [558, 9.0, 9.5, 8.8, 9.2]]
mark, ex = C.trade_curve(10.0, 555, path, 10)                                         # SL 10 % = 9.0, low 8.9 at 09:17 -> STOP at 9.0
assert ex == (557, 9.0, "STOP") and mark[557] == 9.0 and mark[570] == 9.0
mark, ex = C.trade_curve(10.0, 555, [[556, 8.0, 8.5, 7.5, 8.2]], 20)                  # gap down through SL 8.0? open 8.0 <= 8.0 -> gap fill at the open
assert ex[2] == "STOP (gap)" and ex[1] == 8.0
mark, ex = C.trade_curve(10.0, 555, [[556, 10, 10.4, 9.9, 10.3], [570, 10.3, 10.6, 10.2, 10.5]], 30)
assert ex == (570, 10.5, "TIME")

# ---- 4. day stop-loss simulation
G = len(C.GRID)
P = np.zeros((3, G)); em = np.array([0, 0, 2])
P[0, :] = [0, -3000, -6000, -6000] + [-6000] * (G - 4)                                # trade 1 loses 6000 by 09:18
P[1, :] = [0, -1000, -2000, -3000] + [-3000] * (G - 4)                                # trade 2 loses 3000 by 09:18
P[2, 2:] = [0, 500] + [800] * (G - 4)                                                 # trade 3 enters at 09:17
assert C.simulate_day(P, em, 0) == (-8200.0, 3, -1)
pnl, n, t = C.simulate_day(P, em, 5000)                                               # total <= -5000 first at column 2 (09:17): -6000-2000+0
assert (t, n, pnl) == (2, 3, -8000.0), (t, n, pnl)
pnl, n, t = C.simulate_day(P, em, 12000)
assert t == -1 and pnl == -8200.0

# ---- 5. end to end on saved data: 2 days, 3 trades
os.makedirs(f"{tmp}/parts")
def path_json(entry, lows):
    return json.dumps([[556 + k, entry, entry + .2, l, l + .1] for k, l in enumerate(lows)] + [[570, entry, entry, entry * .8, entry * .8]], separators=(",", ":"))
rows = [dict(stock="AAA", direction="LONG", date="2026-03-02", entry_minute="09:15", entry_time="09:15", strike=100, entry_price=10.0, lot=100, path=path_json(10, [9.9])),
        dict(stock="BBB", direction="SHORT", date="2026-03-02", entry_minute="09:16", entry_time="09:16", strike=200, entry_price=20.0, lot=50, path=path_json(20, [19.9])),
        dict(stock="CCC", direction="LONG", date="2026-03-03", entry_minute="09:20", entry_time="09:21", strike=300, entry_price=900.0, lot=200, path=path_json(900, [899]))]  # one lot = 1,80,000 > 60,000
pd.DataFrame(rows).to_csv(f"{tmp}/parts/x.csv.gz", index=False)
base = dict(ref=1, signal_date="2026-03-01", green=1, red=0, upper_longer=1, lower_longer=0, stock_price=1.0)
ev = [dict(source="SHAPE", stock="AAA", direction="LONG", type="ALL", date="2026-03-02", entry_minute="09:15", **base),
      dict(source="SHAPE", stock="BBB", direction="SHORT", type="ALL", date="2026-03-02", entry_minute="09:16", **{**base, "green": 0, "red": 1, "upper_longer": 0, "lower_longer": 1}),
      dict(source="BPB", stock="AAA", direction="LONG", type="ALL", date="2026-03-02", entry_minute="09:15", **{**base, "green": -1, "red": -1, "upper_longer": -1, "lower_longer": -1}),
      dict(source="SHAPE", stock="CCC", direction="LONG", type="ALL", date="2026-03-03", entry_minute="09:20", **base)]
pd.DataFrame(ev).to_csv(f"{tmp}/events.csv", index=False)
C.summary()
s = pd.read_csv(f"{tmp}/summary.csv"); d = pd.read_csv(f"{tmp}/daily_pnl.csv.gz")
x = d[(d.variant == "SHAPECMP | NO_SHAPE_RULE | ALL") & (d.sl == 10) & (d.day_sl == 0)]
assert len(x) == 1 and x.trades.iloc[0] == 2, x                                       # CCC skipped: one lot dearer than Rs 60,000
y = d[(d.variant == "SHAPECMP | PREV_RED | ALL") & (d.sl == 10) & (d.day_sl == 0)]
assert y.trades.iloc[0] == 1                                                          # only BBB is a red signal candle
z = d[(d.variant == "BPB | ALL") & (d.sl == 10) & (d.day_sl == 0)]
assert z.trades.iloc[0] == 1
lots_a = 60000 // (10 * 100); assert lots_a == 60
a = d[(d.variant == "BPB | ALL") & (d.sl == 10) & (d.day_sl == 0)].pnl.iloc[0]       # AAA: the 09:30 candle's low (8.0) touches SL 10 % = 9.0 -> STOP fill at 9.0 -> (9-10)*100*60
assert a == (9.0 - 10.0) * 100 * lots_a, a
a5 = d[(d.variant == "BPB | ALL") & (d.sl == 10) & (d.day_sl == 5000)]
assert a5.day_sl_hit.iloc[0] in (0, 1)
assert os.path.exists(f"{tmp}/roi_matrix.csv") and os.path.exists(f"{tmp}/day_sl_vs_no_day_sl.csv")
print("ALL OFFLINE TESTS PASSED")
