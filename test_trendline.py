"""Offline logic test for trendline_backtest.py (no Dhan / Yahoo login):  python test_trendline.py"""
import os, json, tempfile
import numpy as np, pandas as pd

tmp = tempfile.mkdtemp()
os.environ.update(COMBO_OUT=tmp, COMBO_START="2026-01-01", COMBO_END="2026-12-31", DAY_SLS="0,5000")
import trendline_backtest as T
import combo_dayrisk_backtest as C

# ---- 1. LONG: falling line through swing highs at bar 3 (110) and bar 9 (106); slope -2/3 per bar
N = 22
H = np.full(N, 100.0); L = np.full(N, 95.0); O = np.full(N, 97.0); Cl = np.full(N, 98.0)
H[3], H[9] = 110, 106                                       # two swing highs, the 2nd lower -> falling resistance
for i in (0, 1, 2, 4, 5, 6): H[i] = 100
for i in (8, 10, 11, 12): H[i] = 101
# line(x) = 110 - (x-3)*4/6 ; line(14) = 110 - 11*0.6667 = 102.67
H[14], Cl[14], L[14], O[14] = 106.0, 104.0, 100.0, 101.0     # breakout candle: closes above the line (102.67); H_break = 106
H[15], L[15], Cl[15], O[15] = 105.0, 102.0, 103.5, 105.0   # pullback: low 102 <= line(15)=102.0 ; close 103.5 > line -> validated, high 105 < 106
H[13], Cl[13] = 101.5, 101.0
sig = T.tl_signals(O, H, L, Cl, True, k=3, min_gap=5, max_age=60, wait=15)
assert len(sig) == 1 and sig[0][0] == 15 and sig[0][1] == 106 and sig[0][2] == 14, sig
assert abs(sig[0][3] - (110 - 12 * 4 / 6)) < 1e-9, sig

# ---- 2. pullback closes BELOW the line -> setup cancelled, no signal
Cl2, L2 = Cl.copy(), L.copy(); Cl2[15] = 101.0
assert T.tl_signals(O, H, L2, Cl2, True, k=3) == []
# ---- 3. pullback never touches the line -> no signal
L3 = L.copy(); L3[15] = 103.0
assert T.tl_signals(O, H, L3, Cl, True, k=3) == []
# ---- 4. validation candle already traded above H_break -> trigger had happened, skipped
H4 = H.copy(); H4[15] = 107.0
assert T.tl_signals(O, H4, L, Cl, True, k=3) == []
# ---- 5. SHORT mirror: negate prices around a constant -> same bar numbers, levels mirrored
K = 300.0
sh = T.tl_signals(K - O, K - L, K - H, K - Cl, False, k=3)       # (K - x) of LONG data: highs <-> lows
assert len(sh) == 1 and sh[0][0] == 15 and abs(sh[0][1] - (K - 106)) < 1e-9, sh
# ---- 6. rising line (wrong slope for LONG) -> nothing
H6 = H.copy(); H6[3], H6[9] = 104, 110
assert T.tl_signals(O, H6, L, Cl, True, k=3) == []

# ---- 7. variants & shape flags
ev = pd.DataFrame([dict(source="TRENDLINE", type="ALL", green=1, red=0, upper_longer=1, lower_longer=0),
                   dict(source="TRENDLINE", type="OPEN_0915", green=0, red=1, upper_longer=0, lower_longer=1),
                   dict(source="SHAPE", type="ALL", green=1, red=0, upper_longer=1, lower_longer=0)])
v = dict(T.variants(ev))
assert len(v) == 5 * 4
assert v["TRENDLINE | NO_SHAPE_RULE | ALL"].sum() == 1 and v["TRENDLINE | PREV_GREEN | ALL"].sum() == 1
assert v["TRENDLINE | PREV_RED | ALL"].sum() == 0 and v["TRENDLINE | PREV_RED | OPEN_0915"].sum() == 1
assert v["TRENDLINE | LOWER_WICK_LONGER | OPEN_0915"].sum() == 1 and v["TRENDLINE | UPPER_WICK_LONGER | OPEN_0915"].sum() == 0

# ---- 8. end to end through the shared engine: 60,000 cap, 10 % SL, 09:30 exit
os.makedirs(f"{tmp}/parts")
def path_json(entry, lows):
    return json.dumps([[556 + k, entry, entry + .2, l, l + .1] for k, l in enumerate(lows)] + [[570, entry, entry, entry, entry]], separators=(",", ":"))
rows = [dict(stock="AAA", direction="LONG", date="2026-03-02", entry_minute="09:15", entry_time="09:15", strike=100, entry_price=10.0, lot=100, path=path_json(10, [9.9, 8.9])),
        dict(stock="CCC", direction="LONG", date="2026-03-03", entry_minute="09:20", entry_time="09:21", strike=300, entry_price=900.0, lot=200, path=path_json(900, [899]))]
pd.DataFrame(rows).to_csv(f"{tmp}/parts/x.csv.gz", index=False)
base = dict(source="TRENDLINE", ref=106, signal_date="2026-02-27", green=1, red=0, upper_longer=1, lower_longer=0, stock_price=1.0)
pd.DataFrame([dict(stock="AAA", direction="LONG", type="ALL", date="2026-03-02", entry_minute="09:15", **base),
              dict(stock="CCC", direction="LONG", type="ALL", date="2026-03-03", entry_minute="09:20", **base)]).to_csv(f"{tmp}/events.csv", index=False)
C.summary()
d = pd.read_csv(f"{tmp}/daily_pnl.csv.gz")
x = d[(d.variant == "TRENDLINE | NO_SHAPE_RULE | ALL") & (d.sl == 10) & (d.day_sl == 0)]
assert len(x) == 1 and x.trades.iloc[0] == 1, x                                   # CCC: one lot Rs 1,80,000 > Rs 60,000 -> skipped
assert x.pnl.iloc[0] == round((9.0 - 10.0) * 100 * 60), x                         # 60 lots, SL 9.0 touched by the 8.9 low
assert set(d.sl) == {10}
assert d[d.variant == "TRENDLINE | PREV_RED | ALL"].empty
print("ALL OFFLINE TESTS PASSED")
