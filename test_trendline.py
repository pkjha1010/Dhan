"""Offline logic test for trendline_backtest.py (no Dhan login):  python test_trendline.py"""
import os, json, tempfile
import numpy as np, pandas as pd

tmp = tempfile.mkdtemp()
os.environ.update(TL_OUT=tmp, TL_START="2026-01-01", TL_END="2026-12-31")
import trendline_backtest as T
import combo_dayrisk_backtest as C

# ---- 1. LONG: falling line through swing highs at bar 3 (110) and bar 9 (106)
N = 22
H = np.full(N, 100.0); L = np.full(N, 95.0); O = np.full(N, 97.0); Cl = np.full(N, 98.0)
H[3], H[9] = 110, 106
for i in (8, 10, 11, 12): H[i] = 101
H[14], Cl[14], L[14], O[14] = 106.0, 104.0, 100.0, 101.0     # breakout: closes above line(14)=102.67; H_break = 106
H[15], L[15], Cl[15], O[15] = 105.0, 102.0, 103.5, 105.0    # pullback: low 102 <= line(15)=102.0, close 103.5 > line, high 105 < 106 -> validated
H[13], Cl[13] = 101.5, 101.0
sig = T.tl_signals(O, H, L, Cl, True, k=3, min_gap=5, max_age=60, wait=15)
assert len(sig) == 1 and sig[0][0] == 15 and sig[0][1] == 106 and sig[0][2] == 14, sig
assert abs(sig[0][3] - (110 - 12 * 4 / 6)) < 1e-9, sig
Cl2 = Cl.copy(); Cl2[15] = 101.0
assert T.tl_signals(O, H, L, Cl2, True, k=3) == []                       # pullback closes below the line -> cancelled
L3 = L.copy(); L3[15] = 103.0
assert T.tl_signals(O, H, L3, Cl, True, k=3) == []                       # never touches the line
H4 = H.copy(); H4[15] = 107.0
assert T.tl_signals(O, H4, L, Cl, True, k=3) == []                       # validation candle already above H_break
K = 300.0
sh = T.tl_signals(K - O, K - L, K - H, K - Cl, False, k=3)                # SHORT mirror
assert len(sh) == 1 and sh[0][0] == 15 and abs(sh[0][1] - (K - 106)) < 1e-9, sh
H6 = H.copy(); H6[3], H6[9] = 104, 110
assert T.tl_signals(O, H6, L, Cl, True, k=3) == []                       # rising line is no resistance

# ---- 2. 4H candles from hourly: 09:15-13:15 and 13:15-15:30
days = pd.bdate_range("2026-01-05", periods=2)
idx = pd.DatetimeIndex([d + pd.Timedelta(hours=9, minutes=15) + pd.Timedelta(hours=k) for d in days for k in range(7)])
hh = pd.DataFrame({"o": np.arange(14) + 100.0, "h": np.arange(14) + 101.0, "l": np.arange(14) + 99.0, "c": np.arange(14) + 100.5}, index=idx)
f = T.to_4h(hh)
assert len(f) == 4 and f.index[0].strftime("%H:%M") == "09:15" and f.index[1].strftime("%H:%M") == "13:15", f
assert f.o.iloc[0] == 100 and f.h.iloc[0] == 104 and f.l.iloc[0] == 99 and f.c.iloc[0] == 103.5      # candles 09:15,10:15,11:15,12:15
assert f.o.iloc[1] == 104 and f.h.iloc[1] == 107 and f.c.iloc[1] == 106.5                              # candles 13:15,14:15,15:15

T.PARAMS["1H"] = dict(k=3, min_gap=5, max_age=60, wait=15)                  # the toy pattern is small: use small windows
# ---- 3. 1H chart end to end: the pattern above spread over trading days (7 candles a day), entry on the next morning
pad = 40; M = pad + N + 7
Hh = np.full(M, 100.0); Ll = np.full(M, 95.0); Oo = np.full(M, 97.0); Cc = np.full(M, 98.0)
for a, b in ((Hh, H), (Ll, L), (Oo, O), (Cc, Cl)): a[pad:pad + N] = b
b0 = pad + 16                                                             # = first candle of the day after the validation candle (index 55 = last candle of its day)
Oo[b0], Hh[b0], Ll[b0], Cc[b0] = 105.0, 107.0, 104.0, 106.0               # 09:15 candle already trades above H_break 106
days = pd.bdate_range("2026-01-05", periods=M // 7 + 2)
idx = pd.DatetimeIndex([d + pd.Timedelta(hours=9, minutes=15) + pd.Timedelta(hours=k) for d in days for k in range(7)])[:M]
hr = pd.DataFrame({"o": Oo, "h": Hh, "l": Ll, "c": Cc}, index=idx)
rows = T.signals_for("AAA", hr, "1H", pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31"))
r = [x for x in rows if x["direction"] == "LONG"]
assert len(r) == 1, rows
r = r[0]
assert r["source"] == "TL_1H" and r["ref"] == 106.0 and r["signal_date"] == str(idx[pad + 15].date()) and r["date"] == str(idx[b0].date()), r
assert r["signal_date"] < r["date"] and r["breakout_date"] <= r["signal_date"]
assert T.signals_for("AAA", hr, "1H", pd.Timestamp("2026-06-01"), pd.Timestamp("2026-12-31")) == []            # entry date outside the range
Hx = Hh.copy(); Hx[pad + 15 + 0] = 105.0; Hx[b0 - 1] = 105.0
hx = hr.copy(); hx.iloc[b0 - 3, hx.columns.get_loc("h")] = 106.5                     # but if price ALREADY traded above H_break before the day ended ... (only after validation)
assert T.signals_for("AAA", hx, "1H", pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31")) is not None
assert T.signals_for("AAA", hr, "4H", pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31")) == []         # < 60 four-hour candles: nothing

# ---- 4. variants
ev = pd.DataFrame([dict(source="TL_1H", type="ALL"), dict(source="TL_4H", type="ALL"), dict(source="TL_4H", type="OPEN_0915"), dict(source="SHAPE", type="ALL")])
v = dict(T.variants(ev))
assert len(v) == 2 * 4 and v["TRENDLINE | 1H | ALL"].sum() == 1 and v["TRENDLINE | 4H | ALL"].sum() == 1 and v["TRENDLINE | 4H | OPEN_0915"].sum() == 1

# ---- 5. engine + result files: 60,000 cap, 10 % SL, 09:30 exit
os.makedirs(f"{tmp}/parts")
def path_json(entry, lows):
    return json.dumps([[556 + k, entry, entry + .2, l, l + .1] for k, l in enumerate(lows)] + [[570, entry, entry, entry, entry]], separators=(",", ":"))
pr = [dict(stock="AAA", direction="LONG", date="2026-03-02", entry_minute="09:15", entry_time="09:15", strike=100, entry_price=10.0, lot=100, path=path_json(10, [9.9, 8.9])),
      dict(stock="BBB", direction="SHORT", date="2026-03-02", entry_minute="09:16", entry_time="09:16", strike=200, entry_price=20.0, lot=50, path=path_json(20, [19.9, 19.9])),
      dict(stock="CCC", direction="LONG", date="2026-03-03", entry_minute="09:20", entry_time="09:21", strike=300, entry_price=900.0, lot=200, path=path_json(900, [899]))]
pd.DataFrame(pr).to_csv(f"{tmp}/parts/x.csv.gz", index=False)
base = dict(ref=106, signal_date="2026-02-27", green=1, red=0, upper_longer=1, lower_longer=0, stock_price=1.0)
pd.DataFrame([dict(source="TL_1H", stock="AAA", direction="LONG", type="ALL", date="2026-03-02", entry_minute="09:15", **base),
              dict(source="TL_4H", stock="BBB", direction="SHORT", type="ALL", date="2026-03-02", entry_minute="09:16", **base),
              dict(source="TL_1H", stock="CCC", direction="LONG", type="ALL", date="2026-03-03", entry_minute="09:20", **base)]).to_csv(f"{tmp}/events.csv", index=False)
T.summary()
t = pd.read_csv(f"{tmp}/all_trades.csv"); s = pd.read_csv(f"{tmp}/summary.csv")
assert set(t.strategy) == {"TRENDLINE"} and set(t.setup) == {"1H", "4H"} and len(t) == 2, t          # CCC: one lot Rs 1,80,000 > Rs 60,000 -> skipped
a = t[t.stock == "AAA"].iloc[0]
assert a.lots == 60 and a.pnl == round((9.0 - 10.0) * 100 * 60) and a.reason == "STOP" and a.roi_pct == round(-6000 / 60000 * 100, 2), a    # SL 10 % = 9.0 touched by the 8.9 low
b = t[t.stock == "BBB"].iloc[0]
assert b.reason == "TIME" and b.exit_time == "09:30" and b.lots == 60000 // (20 * 50), b
x = s[s.variant == "TRENDLINE | 1H | ALL | SL10"].iloc[0]
assert x.trades == 1 and x.win_rate_pct == 0 and x.total_pnl == -6000
for f_ in ("top_by_pnl", "top_by_roi", "top_by_profit_factor", "top_by_win_rate"): assert os.path.exists(f"{tmp}/{f_}.csv")
print("ALL OFFLINE TESTS PASSED")
