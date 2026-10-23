"""Offline logic test (no broker, no engine): python test_bpbwru_lh.py"""
import numpy as np, pandas as pd
import lh_logic as LH

def day(p13, p15, p30):
    idx = pd.date_range("2024-03-05 09:15", "2024-03-05 15:29", freq="min"); n = len(idx)
    px = np.interp(np.arange(n), [0, (13 - 9) * 60 - 15, (15 - 9) * 60 - 15, n - 1], [p13, p13, p15, p30])
    return pd.DataFrame({"o": px, "c": px}, index=idx)

for (a, b, c, h, m) in [(100, 102, 103, 1, 1), (100, 98, 99, 1, -1), (100, 102, 101, -1, 1), (100, 98, 97, -1, -1)]:
    f = LH.day_flags(day(a, b, c)); assert f["ok"] == 1 and f["h"] == h and f["m"] == m, (a, b, c, f)
assert LH.day_flags(day(100, 100, 100))["h"] == 0                                   # flat = neither bullish nor bearish
assert LH.day_flags(day(100, 102, 103).between_time("09:15", "14:00"))["ok"] == 0   # day cut off before 15:00 -> unknown
assert LH.day_flags(None)["ok"] == 0
print("OFFLINE TEST OK")
