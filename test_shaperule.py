"""Offline logic test for shaperule_backtest.py (no Dhan / Yahoo login):  python test_shaperule.py"""
import os, json, tempfile
import pandas as pd

tmp = tempfile.mkdtemp()
os.environ.update(SR_OUT=tmp, SR_START="2026-01-01", SR_END="2026-12-31")
import shaperule_backtest as S

# ---- 1. the four patterns are separate, exclusive strategies
ev = pd.DataFrame([dict(source="SHAPE", type="ALL", green=1, red=0, upper_longer=1, lower_longer=0),     # green + upper wick longer
                   dict(source="SHAPE", type="ALL", green=0, red=1, upper_longer=1, lower_longer=0),     # red + upper
                   dict(source="SHAPE", type="ALL", green=1, red=0, upper_longer=0, lower_longer=1),     # green + lower
                   dict(source="SHAPE", type="ALL", green=0, red=1, upper_longer=0, lower_longer=1),     # red + lower
                   dict(source="SHAPE", type="ALL", green=0, red=0, upper_longer=1, lower_longer=0),     # doji with upper wick: no pattern
                   dict(source="BPB", type="ALL", green=1, red=0, upper_longer=1, lower_longer=0)])
v = dict(S.variants(ev))
assert len(v) == 4 * 4
tot = 0
for p in S.PATTERNS:
    n = int(v[f"SHAPERULE | {p} | ALL"].sum()); assert n == 1, (p, n); tot += n
assert tot == 4
assert v["SHAPERULE | GREEN_UPPER_WICK_LONGER | ALL"].tolist() == [True, False, False, False, False, False]
assert v["SHAPERULE | RED_LOWER_WICK_LONGER | ALL"].tolist() == [False, False, False, True, False, False]

# ---- 2. engine + result files
os.makedirs(f"{tmp}/parts")
def path_json(entry, lows):
    return json.dumps([[556 + k, entry, entry + .2, l, l + .1] for k, l in enumerate(lows)] + [[570, entry, entry, entry * 1.1, entry * 1.1]], separators=(",", ":"))
pr = [dict(stock="AAA", direction="LONG", date="2026-03-02", entry_minute="09:15", entry_time="09:15", strike=100, entry_price=10.0, lot=100, path=path_json(10, [9.9, 8.9])),
      dict(stock="BBB", direction="SHORT", date="2026-03-02", entry_minute="09:16", entry_time="09:16", strike=200, entry_price=20.0, lot=50, path=path_json(20, [19.9, 19.9])),
      dict(stock="DDD", direction="LONG", date="2026-03-04", entry_minute="09:17", entry_time="09:17", strike=100, entry_price=10.0, lot=100, path=path_json(10, [9.9, 9.8]))]
pd.DataFrame(pr).to_csv(f"{tmp}/parts/x.csv.gz", index=False)
base = dict(source="SHAPE", ref=1, signal_date="2026-02-27", stock_price=1.0)
pd.DataFrame([dict(stock="AAA", direction="LONG", type="ALL", date="2026-03-02", entry_minute="09:15", green=1, red=0, upper_longer=1, lower_longer=0, **base),
              dict(stock="BBB", direction="SHORT", type="ALL", date="2026-03-02", entry_minute="09:16", green=0, red=1, upper_longer=0, lower_longer=1, **base),
              dict(stock="DDD", direction="LONG", type="ALL", date="2026-03-04", entry_minute="09:17", green=1, red=0, upper_longer=1, lower_longer=0, **base)]).to_csv(f"{tmp}/events.csv", index=False)
S.summary()
t = pd.read_csv(f"{tmp}/all_trades.csv"); s = pd.read_csv(f"{tmp}/summary.csv")
assert set(t.strategy) == {"SHAPERULE"} and set(t.setup) == {"GREEN_UPPER_WICK_LONGER", "RED_LOWER_WICK_LONGER"} and len(t) == 3, t
g = s[s.variant == "SHAPERULE | GREEN_UPPER_WICK_LONGER | ALL | SL10"].iloc[0]
assert g.trades == 2 and g.wins == 1 and g.losses == 1 and g.win_rate_pct == 50.0, g                  # AAA stopped (-6000), DDD time exit +10 %: (11-10)*100*60 = +6000
assert g.total_pnl == 0 and g.profit_factor == 1.0 and g.capital_used == 120000 and g.roi_pct == 0.0, g
r = s[s.variant == "SHAPERULE | RED_LOWER_WICK_LONGER | ALL | SL10"].iloc[0]
assert r.trades == 1 and r.total_pnl == round((22.0 - 20.0) * 50 * 60), r                              # SHORT = ATM put bought: premium 20 -> 22 at 09:30 = +2 per unit x 50 x 60 lots
print("ALL OFFLINE TESTS PASSED")
