"""gap_slots_0915_0916.py - GAP combos for ONLY the entry minutes 09:15 and 09:16 (separately and together).  No API calls.
Per direction x entry minute(s) x time exit x SL x TP: trades, win %, PnL, PF, PnL after cutting the top 10 % of trades (trim), months profitable (on the trimmed trades), PnL per period.
Entry premium > MIN_PRICE (Rs 5).   Output gap_results/slots_0915_0916/ALL_COMBOS.csv, SURVIVORS.csv, SLOTS_0915_0916.md.   python gap_slots_0915_0916.py [min_price] [min_trades]
SURVIVOR = trades >= MIN_TRADES, total PnL > 0, PF >= 1.3, trimmed PnL > 0 and trimmed PF >= 1.2, >= 60 % of months profitable after the cut."""
import sys, os, numpy as np, pandas as pd
OUT = "gap_results"; MIN_PRICE = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0; MIN_TRADES = int(sys.argv[2]) if len(sys.argv) > 2 else 30
SETS = {"09:15": ["09:15"], "09:16": ["09:16"], "09:15+09:16": ["09:15", "09:16"]}


def pf(p):
    w = p[p > 0].sum(); l = -p[p < 0].sum(); return round(w / l, 2) if l > 0 else np.inf


def per(d): return "2023-24" if d < "2025-01-01" else "2025" if d < "2026-01-01" else "2026"


def stats(g):
    p = g.pnl.sort_values(ascending=False); k = max(1, int(np.ceil(len(p) * .1))); keep = g.loc[p.index[k:]]
    m = keep.groupby(keep.entry_date.str[:7]).pnl.sum(); allm = g.entry_date.str[:7].nunique(); pp = g.groupby(g.entry_date.map(per)).pnl.sum()
    return pd.Series(dict(trades=len(g), win_pct=round((g.pnl > 0).mean() * 100, 1), total_pnl=round(g.pnl.sum()), pf=pf(g.pnl.values), median_ret_pct=round(g.ret_pct.median(), 1),
                          trim_pnl=round(keep.pnl.sum()), trim_pf=pf(keep.pnl.values), months=allm, months_profit=int((m > 0).sum()), months_profit_pct=round((m > 0).sum() / allm * 100, 1),
                          pnl_2023_24=round(pp.get("2023-24", 0)), pnl_2025=round(pp.get("2025", 0)), pnl_2026=round(pp.get("2026", 0))))


def main():
    rows = []
    for d in ("long", "short"):
        T = pd.read_csv(f"{OUT}/{d}/trades_all_variants.csv.gz"); T = T[T.entry_price > MIN_PRICE]
        for name, mins in SETS.items():
            U = T[T.entry_time.isin(mins)]
            r = U.groupby(["exit_rule", "sl", "tp"]).apply(stats, include_groups=False).reset_index(); r.insert(0, "slot", name); r.insert(0, "direction", d.upper()); rows.append(r)
    R = pd.concat(rows, ignore_index=True); R["sl"] = R.sl.map(lambda v: "none" if not v else f"{int(v)}%"); R["tp"] = R.tp.map(lambda v: "none" if not v else f"{int(v)}%")
    R["survivor"] = (R.trades >= MIN_TRADES) & (R.total_pnl > 0) & (R.pf >= 1.3) & (R.trim_pnl > 0) & (R.trim_pf >= 1.2) & (R.months_profit_pct >= 60)
    o = f"{OUT}/slots_0915_0916"; os.makedirs(o, exist_ok=True); R.to_csv(f"{o}/ALL_COMBOS.csv", index=False); S = R[R.survivor].sort_values(["direction", "slot", "trim_pnl"], ascending=[True, True, False]); S.to_csv(f"{o}/SURVIVORS.csv", index=False)
    cols = ["exit_rule", "sl", "tp", "trades", "win_pct", "total_pnl", "pf", "trim_pnl", "trim_pf", "months_profit", "months", "pnl_2023_24", "pnl_2025", "pnl_2026"]
    L = [f"# GAP entries at 09:15 / 09:16 only (premium > Rs {MIN_PRICE:g}, min {MIN_TRADES} trades)", "", "## Overview", "",
         R.groupby(["direction", "slot"]).agg(combos=("survivor", "size"), trades=("trades", "max"), profitable=("total_pnl", lambda x: int((x > 0).sum())), trim_profitable=("trim_pnl", lambda x: int((x > 0).sum())),
                                              survivors=("survivor", "sum"), best_pf=("pf", "max"), best_trim_pf=("trim_pf", "max")).reset_index().to_markdown(index=False), ""]
    for d in ("LONG", "SHORT"):
        for name in SETS:
            g = R[(R.direction == d) & (R.slot == name)]; s = g[g.survivor]
            L += [f"## {d} {name}: {len(s)} survivors; top 8 by trimmed PnL", "", g.sort_values("trim_pnl", ascending=False).head(8)[cols].to_markdown(index=False), ""]
    open(f"{o}/SLOTS_0915_0916.md", "w").write("\n".join(L)); print("\n".join(L))


if __name__ == "__main__": main()
