"""test_bpb_long.py - offline test (no login, no network) of bpb_long_rules.py, the daily setups and the engine hooks of bpb_long_backtest.py."""
import numpy as np, pandas as pd
import bpb_long_rules as R

def mins(h, m): return h * 60 + m
# 1-minute candles 09:15 .. 15:20 (366), High / Close arrays
M = np.arange(mins(9, 15), mins(15, 20) + 1)
def flat(price): return np.full(len(M), float(price))
# no touch -> nothing
assert R.entries_long(M, flat(99), flat(99), 100.0, mins(15, 20)) == {}
# T1 only: first touch at 11:00 (High 100), closes stay above -> no T2
h, c = flat(99), flat(99); i = int(np.where(M == mins(11, 0))[0][0]); h[i:] = 101; c[i:] = 101
r = R.entries_long(M, h, c, 100.0, mins(15, 20)); assert r == {"T1": i}, r
# gap through the level at 09:15 -> T1 at position 0
h, c = flat(101), flat(101); assert R.entries_long(M, h, c, 100.0, mins(15, 20)) == {"T1": 0}
# T2: touch at 09:30 (close back below), 5+ closes below, then re-cross at 10:10
h, c = flat(99), flat(99); t = int(np.where(M == mins(9, 30))[0][0]); h[t] = 100.5; c[t] = 99.5
j = int(np.where(M == mins(10, 10))[0][0]); h[j] = 100.2; c[j] = 100.1
r = R.entries_long(M, h, c, 100.0, mins(15, 20)); assert r == {"T1": t, "T2": j}, r
# only 4 closes below before the re-cross (touch candle closes ABOVE -> run restarts) -> no T2
h, c = flat(99), flat(99); t = 10; h[t] = 100.5; c[t] = 100.4
for k in range(t + 1, t + 5): h[k] = 99; c[k] = 99                         # 4 closes below
h[t + 5] = 100.3; c[t + 5] = 100.2                                          # re-cross after only 4
h[t + 6:] = 99; c[t + 6:] = 99
r = R.entries_long(M, h, c, 100.0, mins(15, 20)); assert r == {"T1": t}, r
# exactly 5 closes below (touch candle closes above) then re-cross -> T2
h, c = flat(99), flat(99); t = 10; h[t] = 100.5; c[t] = 100.4
for k in range(t + 1, t + 6): h[k] = 99; c[k] = 99                         # 5 closes below
h[t + 6] = 100.3; c[t + 6] = 100.2; h[t + 7:] = 99; c[t + 7:] = 99
r = R.entries_long(M, h, c, 100.0, mins(15, 20)); assert r == {"T1": t, "T2": t + 6}, r
# entries after the last allowed minute are not accepted
h, c = flat(99), flat(99); h[-1] = 101; c[-1] = 101
assert R.entries_long(M, h, c, 100.0, mins(15, 19)) == {}
assert R.entries_long(M, h, c, 100.0, mins(15, 20)) == {"T1": len(M) - 1}

# daily setups: the state machine of bpb_fno_backtest on a hand-made path -> breakout, bearish pullback, re-cross
import bpb_fno_backtest as BP
n = 14
H = np.array([10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12.5, 12.2, 13.0]); L = H - 1
O = np.array([9.5] * 10 + [10.5, 12.3, 12.0, 12.4]); C = np.array([9.5] * 10 + [11.8, 12.0, 11.9, 12.8])
# day 10: close 11.8 > 10-day high 10 (breakout, level 12);  day 11: High 12.5 (new level 12.5), bearish (close 12.0 < open 12.3) -> pullback confirmed;  day 12: no re-cross;  day 13: High 13 >= 12.5 -> entry
s = BP.find_setups(O, H, L, C, 10); assert [x[0] for x in s] == [13] and abs(s[0][1] - 12.5) < 1e-9, s

# engine hooks
import bpb_long_backtest as BL
u = pd.DataFrame({"o": np.where(M >= mins(11, 0), 101.0, 99.0), "h": np.where(M >= mins(11, 0), 101.0, 99.0), "l": 98.0, "c": np.where(M >= mins(11, 0), 101.0, 99.0)},
                 index=pd.to_datetime("2026-01-05 00:00") + pd.to_timedelta(M, unit="m"))
e = BL.entries_for(u, 100.0, True); assert list(e) == ["BPBT1"] and e["BPBT1"].strftime("%H:%M") == "11:00", e
assert BL.entries_for(u, 100.0, False) == {}                                  # LONG only
assert BL.strategies_for("BPB", "BPBT1", -1, -1, -1, -1) == ["BPBL_T1"] and BL.strategies_for("BPB", "BPBT2", -1, -1, -1, -1) == ["BPBL_T2"]
assert BL.strategies_for("GAP", "BPBT1", -1, -1, -1, -1) == []
assert BL.A.STRATS == ["BPBL_T1", "BPBL_T2"] and BL.A.EXITS == ["15:00", "15:30"], (BL.A.STRATS, BL.A.EXITS)
assert len(BL.A.VARS) == 2 * 4 * 5, len(BL.A.VARS)                              # 2 exits x 4 SL x 5 TP = 40
rows = BL.setups_to_rows("TEST", [str(d.date()) for d in pd.bdate_range("2026-01-01", periods=n)], O, H, L, C, pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31"))
assert len(rows) == 1 and rows[0]["direction"] == "LONG" and rows[0]["source"] == "BPB" and rows[0]["ref"] == 12.5, rows
BL.print_rules()
print("test_bpb_long OK")
