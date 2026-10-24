"""Offline test of itm_fallback.make_work_group with fake option series (no Dhan)."""
import os
os.environ.setdefault("A8_OUT", "/tmp/_itm_test"); os.environ.setdefault("A8_START", "2026-01-01"); os.environ.setdefault("A8_END", "2026-10-31")
import pandas as pd, numpy as np
from datetime import date
import all8_backtest as A
import itm_fallback as IF

E = date(2026, 10, 27); LOT = 100
idx = pd.date_range("2026-10-21 09:15", "2026-10-21 15:29", freq="min")
def series(off, strike, missing_at=None, hole=False):
    x = pd.DataFrame({"o": 10.0, "h": 10.0, "l": 10.0, "c": 10.0 + off, "strike": float(strike)}, index=idx)
    if missing_at is not None: x = x[(x.index < missing_at) | (x.index >= missing_at + pd.Timedelta(minutes=30))]   # hole of 30 min at the entry minute
    return x
em = "12:30"; hole = pd.Timestamp("2026-10-21 12:25")
DATA = {0: series(0, 100, hole), 1: series(1, 105, hole), 2: series(2, 110), 3: series(3, 115)}       # ATM and ITM-1 have no candle at 12:30; ITM-2 has
calls = []
A.get_series = lambda dh, sid, dr, wins, off: (calls.append(off), DATA.get(off))[1]
A.windows = lambda a, b: []
A.infer_step = lambda s: 5.0
A.make_record = lambda S, te, entry, lot, K, Eeff, cov: dict(strike=K, entry=entry, te=te)
A.ekey = lambda s, dr, d, m: f"{s}|{dr}|{d}|{m}"
wg = IF.make_work_group(A, 4)
recs, skips = wg(None, {"XYZ": ("1", LOT)}, ("XYZ", "SHORT", E, [("2026-10-21", em)], "k"))
assert not skips and len(recs) == 1, (recs, skips)
assert recs[0]["strike_offset"] == 2 and recs[0]["strike"] == 110.0 and recs[0]["entry"] == 12.0, recs[0]      # ATM, ITM-1 skipped, ITM-2 taken
# entry minute where ATM exists -> ATM taken, no other series asked for the entry
calls.clear(); recs, skips = wg(None, {"XYZ": ("1", LOT)}, ("XYZ", "SHORT", E, [("2026-10-21", "14:00")], "k"))
assert recs[0]["strike_offset"] == 0 and recs[0]["strike"] == 100.0, recs[0]
# nothing within max_itm -> skipped with a reason
DATA2 = {k: series(k, 100 + 5 * k, hole) for k in range(5)}; A.get_series = lambda dh, sid, dr, wins, off: DATA2.get(off)
recs, skips = IF.make_work_group(A, 4)(None, {"XYZ": ("1", LOT)}, ("XYZ", "SHORT", E, [("2026-10-21", em)], "k"))
assert not recs and len(skips) == 1 and "ITM-4" in skips[0][1], skips
# a CALL goes the other way (lower strikes)
A.get_series = lambda dh, sid, dr, wins, off: {0: series(0, 100, hole), -1: series(-1, 95)}.get(off)
recs, skips = IF.make_work_group(A, 2)(None, {"XYZ": ("1", LOT)}, ("XYZ", "LONG", E, [("2026-10-21", em)], "k"))
assert len(recs) == 1 and recs[0]["strike_offset"] == -1 and recs[0]["strike"] == 95.0, (recs, skips)
print("OK itm_fallback")
