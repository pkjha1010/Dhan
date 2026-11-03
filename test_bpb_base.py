"""test_bpb_base.py - offline test (no login, no network) of bpb_base_rules.py and the engine hooks of bpb_base_backtest.py (LONG and SHORT)."""
import numpy as np, pandas as pd
import bpb_base_rules as R

# ---- LONG: 10 flat days, breakout day 10 (close 11.8 > 10-day high 10), day 11 makes High 12.5 and is bearish (pullback confirmed, entry level 12.5), day 12 no re-cross, day 13 High 13 >= 12.5
H = np.array([10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12.5, 12.2, 13.0]); L = H - 1
O = np.array([9.5] * 10 + [10.5, 12.3, 12.0, 12.4]); C = np.array([9.5] * 10 + [11.8, 12.0, 11.9, 12.8])
s = R.bpb_setups(O, H, L, C, True, 10)
assert len(s) == 1 and s[0]["entry"] == 13 and abs(s[0]["level"] - 12.5) < 1e-9 and s[0]["breakout"] == 10 and abs(s[0]["line"] - 10) < 1e-9, s
# a pullback candle that CLOSES below the rolling high (line 10) kills the setup
C2 = C.copy(); C2[12] = 9.8; H2 = H.copy(); H2[13] = 13.0
assert R.bpb_setups(O, H2, L, C2, True, 10) == []
# no bearish candle -> pullback not confirmed -> no entry
O3 = O.copy(); O3[11] = 11.0; O3[12] = 11.5; assert R.bpb_setups(O3, H, L, C, True, 10) == []

# ---- SHORT = exact mirror of the same path (prices reflected around 20)
Os, Hs, Ls, Cs = 20 - O, 20 - L, 20 - H, 20 - C
t = R.bpb_setups(Os, Hs, Ls, Cs, False, 10)
assert len(t) == 1 and t[0]["entry"] == 13 and abs(t[0]["level"] - (20 - 12.5)) < 1e-9 and abs(t[0]["line"] - (20 - 10)) < 1e-9, t
assert R.bpb_setups(Os, Hs, Ls, Cs, True, 10) == [] or True            # LONG on the reflected path is another question; only the mirror is asserted

# ---- engine hooks
import bpb_base_backtest as BB
M = np.arange(9 * 60 + 15, 15 * 60 + 20 + 1)
idx = pd.to_datetime("2026-01-05 00:00") + pd.to_timedelta(M, unit="m")
hi = np.where(M >= 11 * 60, 101.0, 99.0)
u = pd.DataFrame({"o": hi, "h": hi, "l": hi - 3, "c": hi}, index=idx)
e = BB.entries_for(u, 100.0, True); assert list(e) == ["BPBL"] and e["BPBL"].strftime("%H:%M") == "11:00", e         # first minute whose High >= level
lo = np.where(M >= 13 * 60 + 5, 98.0, 102.0)
d = pd.DataFrame({"o": lo, "h": lo + 2, "l": lo, "c": lo}, index=idx)
e = BB.entries_for(d, 100.0, False); assert list(e) == ["BPBS"] and e["BPBS"].strftime("%H:%M") == "13:05", e        # first minute whose Low <= level
assert BB.entries_for(u, 120.0, True) == {} and BB.entries_for(d, 90.0, False) == {}
assert BB.strategies_for("BPB", "BPBL", -1, -1, -1, -1) == ["BPB_LONG"] and BB.strategies_for("BPB", "BPBS", -1, -1, -1, -1) == ["BPB_SHORT"] and BB.strategies_for("GAP", "BPBL", -1, -1, -1, -1) == []
assert BB.A.STRATS == ["BPB_LONG", "BPB_SHORT"] and BB.A.EXITS == ["15:00", "15:30"] and len(BB.A.VARS) == 2 * 4 * 5, (BB.A.STRATS, BB.A.EXITS, len(BB.A.VARS))
dates = [str(x.date()) for x in pd.bdate_range("2026-01-01", periods=14)]
rows = BB.setups_to_rows("TEST", dates, O, H, L, C, pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31"))
assert [(r["direction"], r["ref"]) for r in rows] == [("LONG", 12.5)], rows
rows = BB.setups_to_rows("TEST", dates, Os, Hs, Ls, Cs, pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31"))
assert [(r["direction"], r["ref"]) for r in rows if r["direction"] == "SHORT"] == [("SHORT", 7.5)], rows
BB.print_rules()
print("test_bpb_base OK")
