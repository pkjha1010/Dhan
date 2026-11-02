"""test_gap_nifty.py - offline test (no login, no network) of gap_nifty_rules.py and the filter flow of gap_nifty_filter.py."""
import os, tempfile, numpy as np, pandas as pd
import gap_nifty_rules as NR


def day(date, o, closes, start="09:15"):
    idx = pd.date_range(f"{date} {start}", periods=len(closes), freq="min")
    return pd.DataFrame({"o": [o] + list(closes[:-1]), "h": closes, "l": closes, "c": closes}, index=idx)


# day A: NIFTY opens 100, rises -> above the open from 09:16 on;  day B: opens 100, falls;  day C: flat (price == open)
nifty = pd.concat([day("2026-01-05", 100.0, [100.5, 101, 102]), day("2026-01-06", 100.0, [99.5, 99, 98]), day("2026-01-07", 100.0, [100.0, 100.0, 100.0])])
tb = NR.day_tables(nifty)
assert NR.hm_to_min("09:16") == 556
assert NR.nifty_open_price(tb, "2026-01-05", "09:16") == (100.0, 101.0)
assert NR.nifty_open_price(tb, "2026-01-05", "09:15") == (100.0, 100.5)
assert NR.nifty_open_price(tb, "2026-01-05", "11:00") == (100.0, 102.0)            # last candle at or before the entry minute
assert NR.nifty_open_price(tb, "2026-01-05", "09:10") is None                      # before the first candle
assert NR.nifty_open_price(tb, "2026-02-01", "10:00") is None                      # no NIFTY data that day
# rule: LONG needs price > open, SHORT needs price < open, equal passes neither
assert NR.passes(100, 101, "LONG") and not NR.passes(100, 99, "LONG") and not NR.passes(100, 100, "LONG")
assert NR.passes(100, 99, "SHORT") and not NR.passes(100, 101, "SHORT") and not NR.passes(100, 100, "SHORT")

T = pd.DataFrame({"stock": list("abcdefgh"), "direction": ["LONG", "SHORT", "LONG", "SHORT", "LONG", "SHORT", "LONG", "SHORT"],
                  "entry_date": ["2026-01-05", "2026-01-05", "2026-01-06", "2026-01-06", "2026-01-07", "2026-01-07", "2026-02-01", "2026-02-01"],
                  "entry_time": ["09:16"] * 8})
F = NR.add_nifty_flag(T, tb)
assert list(F.nifty_ok.map(lambda x: x if x == x else None)) == [True, False, False, True, False, False, None, None], list(F.nifty_ok)

# end to end with the real filter module on a tiny fake gap_results
import gap_nifty_filter as GF
tmp = tempfile.mkdtemp(); os.makedirs(f"{tmp}/src/long"); os.makedirs(f"{tmp}/src/short")
def mk(direction, rows):
    return pd.DataFrame([dict(strategy="GAP_" + direction, exit_rule="15:30", sl=60, tp=40, stock=s, direction=direction, entry_date=d, entry_time="09:16", entry_price=20.0, pnl=p, ret_pct=r) for s, d, p, r in rows])
mk("LONG", [("a", "2026-01-05", 1000, 10), ("c", "2026-01-06", -500, -5)]).to_csv(f"{tmp}/src/long/trades_all_variants.csv.gz", index=False)
mk("SHORT", [("b", "2026-01-05", 800, 8), ("d", "2026-01-06", 300, 3)]).to_csv(f"{tmp}/src/short/trades_all_variants.csv.gz", index=False)
GF.SRC, GF.OUT = f"{tmp}/src", f"{tmp}/out"
import subprocess; subprocess.run = lambda *a, **k: None                              # skip the survivors script in the test
GF.filter_all(nifty)
kl = pd.read_csv(f"{tmp}/out/long/trades_all_variants.csv.gz"); ks = pd.read_csv(f"{tmp}/out/short/trades_all_variants.csv.gz")
assert list(kl.stock) == ["a"] and list(ks.stock) == ["d"], (list(kl.stock), list(ks.stock))   # a: LONG on a rising day, d: SHORT on a falling day
print("test_gap_nifty OK")
