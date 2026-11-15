"""Offline test of gap_prev_day_check.analyse (no login)."""
import numpy as np, pandas as pd
import gap_prev_day_check as G

def day(d, closes_from_open, start="09:15"):
    idx = pd.date_range(f"{d} {start}", f"{d} 15:29", freq="min"); n = len(idx)
    c = np.linspace(closes_from_open[0], closes_from_open[1], n)
    return pd.DataFrame({"o": c, "h": c + .5, "l": c - .5, "c": c}, index=idx)
# breakout day 2026-10-12 closes 100 (high 102 = level); previous day 10-14 drifts 100 -> 104 (closes above the level 102), last half hour averages ~103.8
u = pd.concat([day("2026-10-12", (98, 100)), day("2026-10-13", (100, 101)), day("2026-10-14", (100, 104))])
a = G.analyse(u, "2026-10-15", "2026-10-12", 102.0, True, 106.0)
assert a["prev_day"] == "2026-10-14" and a["prev_close"] == 104.0 and a["prev_close_beyond_level"] is True
assert a["last30_between_level_and_prev_close"] is True and a["last30_between_level_and_breakout_close"] is False     # avg ~103.8: between 102 and 104, not between 102 and 100
assert abs(a["open_vs_prev_close_pct"] - (106 / 104 - 1) * 100) < 0.01
# SHORT mirror: level 98, previous close 96 (below the level), entry price 94
u2 = pd.concat([day("2026-10-12", (102, 100)), day("2026-10-14", (100, 96))])
b = G.analyse(u2, "2026-10-15", "2026-10-12", 98.0, False, 94.0)
assert b["prev_close_beyond_level"] is True and b["last30_between_level_and_prev_close"] is True and b["open_vs_prev_close_pct"] > 0
# previous close still BELOW the level (LONG): the gap is a real gap from yesterday
u3 = pd.concat([day("2026-10-12", (98, 100)), day("2026-10-14", (99, 101))])
c = G.analyse(u3, "2026-10-15", "2026-10-12", 102.0, True, 105.0)
assert c["prev_close_beyond_level"] is False and c["open_vs_prev_close_pct"] > 3
assert G.analyse(pd.DataFrame(columns=["o", "h", "l", "c"], index=pd.DatetimeIndex([])), "2026-10-15", "2026-10-12", 102.0, True, 105.0) is None
print("test_gap_prev_day OK")
