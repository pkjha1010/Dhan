"""test_gap.py - offline test (no login, no network) of gap_rules.py.
1. gap_setups == the ORIGINAL script's loop (copied below) on 2,000 random price paths, LONG and SHORT: same signal day, same entry day, same level.
2. hand-made examples.   3. first_cross_long / first_cross_short on a small minute frame.   4. gap_backtest imports and the rule text / candidates build."""
import numpy as np, pandas as pd, os, sys
import gap_rules as R


def original(O, H, L, C):
    """Your original daily loop (entry-day detection only): returns {('LONG'|'SHORT', i, j, level)}."""
    out = set(); n = len(C)
    for i in range(2, n - 4):
        gap = (O[i] - C[i - 1]) / C[i - 1]
        if gap > 0.01 and C[i + 1] < C[i]:
            for j in range(i + 2, min(i + 5, n)):
                if H[j] >= H[i]: out.add(("LONG", i, j, float(H[i]))); break
        elif gap < -0.01 and C[i + 1] > C[i]:
            for j in range(i + 2, min(i + 5, n)):
                if L[j] <= L[i]: out.add(("SHORT", i, j, float(L[i]))); break
    return out


def mine(O, H, L, C):
    out = set()
    for long in (True, False):
        for s in R.gap_setups(O, H, L, C, long, 0.01, 2, 4):
            out.add(("LONG" if long else "SHORT", s["signal"], s["entry"], s["level"]))
    return out


rng = np.random.default_rng(7)
bad = tot = 0
for _ in range(2000):
    n = 80; C = 100 * np.exp(np.cumsum(rng.normal(0, .015, n)))
    O = np.r_[C[0], C[:-1]] * np.exp(rng.normal(0, .012, n))
    H = np.maximum(O, C) * (1 + np.abs(rng.normal(0, .008, n))); L = np.minimum(O, C) * (1 - np.abs(rng.normal(0, .008, n)))
    a, b = original(O, H, L, C), mine(O, H, L, C)
    # the original loop only looks at i in 2..n-5 (needs i+4 < n); gap_setups also allows later signals whose window is cut by the data end -> compare the common range
    b = {x for x in b if 2 <= x[1] < n - 4}
    tot += len(a); bad += (a != b)
assert bad == 0, f"{bad} paths differ from the original loop"
assert tot > 200, f"too few setups in the random test ({tot})"
print(f"1. equals the original loop on 2,000 random paths ({tot} setups)")

# 2. hand-made LONG: prev close 100, day 1 opens 102 (gap +2 %) high 105 close 103, day 2 closes 101 (<103), day 3 high 104 (<105), day 4 high 106 (>=105) -> entry day 4
O = [100, 102, 101, 102, 103, 100]; H = [101, 105, 103, 104, 106, 101]; L = [99, 101, 100, 101, 102, 99]; C = [100, 103, 101, 102, 104, 100]
s = R.gap_setups(O, H, L, C, True, 0.01, 2, 4)
assert [(x["signal"], x["entry"], x["level"]) for x in s] == [(1, 4, 105.0)], s
assert all(x['signal'] != 1 for x in R.gap_setups(O, H, L, C, False, 0.01, 2, 4))     # day 1 is a gap UP: never a SHORT signal
# no cross within i+2..i+4 -> no setup
H2 = list(H); H2[4] = 104.5
assert all(x['signal'] != 1 for x in R.gap_setups(O, H2, L, C, True, 0.01, 2, 4))
# SHORT mirror
O = [100, 98, 99, 98, 97, 100]; H = [101, 99, 100, 99, 98, 101]; L = [99, 95, 97, 96, 94, 99]; C = [100, 97, 99, 98, 96, 100]
s = R.gap_setups(O, H, L, C, False, 0.01, 2, 4)
assert [(x["signal"], x["entry"], x["level"]) for x in s] == [(1, 4, 95.0)], s
print("2. hand-made LONG / SHORT examples ok")

# 3. minute frame
idx = pd.date_range("2026-01-05 09:15", periods=6, freq="min")
u = pd.DataFrame(dict(o=[100, 100.5, 101, 101, 101.5, 102], h=[100.4, 100.9, 101.2, 101.6, 102.2, 102.5], l=[99.8, 100.2, 100.6, 100.8, 101.2, 101.7], c=[100.3, 100.8, 101, 101.5, 102, 102.4]), index=idx)
assert R.first_cross_long(u, 101.5) == 3 and R.first_cross_long(u, 99) == 0 and R.first_cross_long(u, 110) is None
assert R.first_cross_short(u, 99.8) == 0 and R.first_cross_short(u, 105) == 0 and R.first_cross_short(u, 99.0) is None
assert R.first_cross_long(u, 101.5, 9 * 60 + 15, 9 * 60 + 17) is None                  # entry window ends 09:17
print("3. first_cross_long / short ok")

# 4. runner imports with the engine and builds the rule text / candidates (no network)
os.environ.setdefault("GP_OUT", "gap_results_test")
import gap_backtest as G
assert G.GAP == 0.01 and G.FIRST == 2 and G.LAST == 4 and G.A.SLS == [0, 20, 40, 60] and G.A.TPS == [20, 40, 60, 80, 120, 0], (G.A.SLS, G.A.TPS)
assert len(G.A.VARS) == 4 * 6 * 4, len(G.A.VARS)
d = pd.bdate_range("2026-01-01", periods=7).strftime("%Y-%m-%d").tolist()
O = [100, 102, 101, 102, 103, 100, 100]; H = [101, 105, 103, 104, 106, 101, 101]; L = [99, 101, 100, 101, 102, 99, 99]; C = [100, 103, 101, 102, 104, 100, 100]
rows = G.setups_to_rows("TEST", d, np.array(O, float), np.array(H, float), np.array(L, float), np.array(C, float), pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31"))
rows = [r for r in rows if r["direction"] == "LONG"]
assert len(rows) == 1 and rows[0]["direction"] == "LONG" and rows[0]["ref"] == 105.0 and rows[0]["day_offset"] == 3 and rows[0]["gap_pct"] == 2.0, rows
print("4. runner builds candidates; grid =", len(G.A.VARS), "variants per direction")
import shutil; shutil.rmtree("gap_results_test", ignore_errors=True)
print("ALL OK")
