import pandas as pd, maxopen_backtest as M
def mk(rows):
    d = pd.DataFrame(rows, columns=["stock", "i", "o", "pnl"]); d["t_in"] = pd.to_datetime("2026-01-05 " + d.i); d["t_out"] = pd.to_datetime("2026-01-05 " + d.o); return d.sort_values(["t_in", "stock"]).reset_index(drop=True)
d = mk([("A", "12:00", "15:30", 1), ("B", "12:10", "12:40", 2), ("C", "12:20", "15:30", 3), ("D", "12:40", "13:00", 4), ("E", "12:30", "12:35", 5)])
t, sk, pk = M.apply_cap(d, 2); assert list(t.stock) == ["A", "B", "D"] and sk == 2 and pk == 2, (list(t.stock), sk, pk)   # C and E blocked (A,B open); D takes B's slot freed at 12:40
t, sk, pk = M.apply_cap(d, 3); assert list(t.stock) == ["A", "B", "C", "D"] and sk == 1, (list(t.stock), sk)              # E blocked (A,B,C open at 12:30)
t, sk, pk = M.apply_cap(d, 0); assert len(t) == 5 and sk == 0 and pk == 4, pk
t, sk, pk = M.apply_cap(d, 1); assert list(t.stock) == ["A"] and pk == 1
d2 = mk([("A", "12:00", "12:30", 1), ("B", "12:30", "13:00", 1)]); assert len(M.apply_cap(d2, 1)[0]) == 2        # a slot freed at 12:30 is usable at 12:30
print("OK")
