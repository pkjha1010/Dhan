"""gap_survivors.py - which GAP variants SURVIVE?  Reads gap_results/{long,short}/trades_all_variants.csv.gz (no API calls) and scores every
direction x ENTRY TIME SLOT x time exit x stop-loss x target combination.

Sanity filter (default): entry premium > MIN_PRICE (Rs 5, same as the live rule) - buying Rs 0.02-0.05 options on an expiry day gives fake +5,000 % trades (one 8,000-lot trade made Rs 3.1 crore).
SURVIVOR = all of:  trades >= MIN_TRADES (30)  |  profit factor >= 1.3  |  total PnL > 0 AND still > 0 after removing the 3 best trades AND after removing the 3 best DAYS (market-wide crash / rally days count once)  |  profit in at least 2 of the 3 periods
(2023-24, 2025, 2026; a period counts only if it has >= 5 trades)  |  median trade not worse than -10 %.
Output: gap_results/survivors/ALL_COMBOS.csv, SURVIVORS.csv, BY_SLOT.csv, SURVIVORS.md.   python gap_survivors.py [min_price] [min_trades]
"""
import sys, os, numpy as np, pandas as pd

OUT = os.environ.get("GAP_SURV_DIR", "gap_results"); MIN_PRICE = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0; MIN_TRADES = int(sys.argv[2]) if len(sys.argv) > 2 else 30
SLOTS = [("09:15-09:29", "09:15", "09:29"), ("09:30-09:59", "09:30", "09:59"), ("10:00-10:59", "10:00", "10:59"), ("11:00-11:59", "11:00", "11:59"),
         ("12:00-12:59", "12:00", "12:59"), ("13:00-13:59", "13:00", "13:59"), ("14:00-15:20", "14:00", "15:20")]


def slot_of(t):
    for n, a, b in SLOTS:
        if a <= t <= b: return n
    return None


def period(d): return "2023-24" if d < "2025-01-01" else "2025" if d < "2026-01-01" else "2026"


def stats(g):
    p = g.pnl.values; w = p[p > 0].sum(); l = -p[p < 0].sum()
    per = {k: g.pnl[g.per == k] for k in ("2023-24", "2025", "2026")}
    ok = [(len(v) >= 5, v.sum() > 0) for v in per.values()]
    return pd.Series(dict(trades=len(g), win_pct=round((p > 0).mean() * 100, 1), total_pnl=round(p.sum()), pf=round(w / l, 2) if l > 0 else np.inf,
                          avg_ret_pct=round(g.ret_pct.mean(), 1), median_ret_pct=round(g.ret_pct.median(), 1), pnl_ex_top3=round(p.sum() - np.sort(p)[-3:].sum()), pnl_ex_top3_days=round(p.sum() - g.groupby('entry_date').pnl.sum().nlargest(3).sum()),
                          pnl_2023_24=round(per["2023-24"].sum()), pnl_2025=round(per["2025"].sum()), pnl_2026=round(per["2026"].sum()),
                          n_2023_24=len(per["2023-24"]), n_2025=len(per["2025"]), n_2026=len(per["2026"]), periods_positive=sum(a and b for a, b in ok)))


def main():
    rows = []
    for d in ("long", "short"):
        T = pd.read_csv(f"{OUT}/{d}/trades_all_variants.csv.gz")
        T = T[T.entry_price > MIN_PRICE].copy(); T["slot"] = T.entry_time.map(slot_of); T["per"] = T.entry_date.map(period)
        T = T.dropna(subset=["slot"])
        r = T.groupby(["slot", "exit_rule", "sl", "tp"]).apply(stats, include_groups=False).reset_index(); r.insert(0, "direction", d.upper()); rows.append(r)
    R = pd.concat(rows, ignore_index=True)
    R["survivor"] = ((R.trades >= MIN_TRADES) & (R.pf >= 1.3) & (R.total_pnl > 0) & (R.pnl_ex_top3 > 0) & (R.pnl_ex_top3_days > 0) & (R.periods_positive >= 2) & (R.median_ret_pct >= -10))
    R["sl"] = R.sl.map(lambda v: "none" if not v else f"{int(v)}%"); R["tp"] = R.tp.map(lambda v: "none" if not v else f"{int(v)}%")
    os.makedirs(f"{OUT}/survivors", exist_ok=True)
    R.sort_values(["direction", "slot", "exit_rule", "sl", "tp"]).to_csv(f"{OUT}/survivors/ALL_COMBOS.csv", index=False)
    S = R[R.survivor].sort_values(["direction", "pnl_ex_top3_days"], ascending=[True, False]); S.to_csv(f"{OUT}/survivors/SURVIVORS.csv", index=False)
    bs = R[R.trades >= MIN_TRADES].groupby(["direction", "slot"]).agg(combos=("survivor", "size"), survivors=("survivor", "sum"), best_pf=("pf", "max"), best_pnl=("total_pnl", "max")).reset_index()
    bs.to_csv(f"{OUT}/survivors/BY_SLOT.csv", index=False)
    cols = ["slot", "exit_rule", "sl", "tp", "trades", "win_pct", "total_pnl", "pf", "median_ret_pct", "pnl_ex_top3_days", "pnl_2023_24", "pnl_2025", "pnl_2026"]
    L = [f"# GAP survivors (entry premium > Rs {MIN_PRICE:g}, min {MIN_TRADES} trades)", "", f"{len(R)} combos scored ({int((R.trades >= MIN_TRADES).sum())} with enough trades); **{int(R.survivor.sum())} survivors**.", ""]
    for d in ("LONG", "SHORT"):
        s = S[S.direction == d]; L += [f"## {d}: {len(s)} survivors", "", s[cols].head(25).to_markdown(index=False) if len(s) else "(none)", ""]
    L += ["## Survivors per entry slot", "", bs.to_markdown(index=False), ""]
    open(f"{OUT}/survivors/SURVIVORS.md", "w").write("\n".join(L)); print("\n".join(L))


if __name__ == "__main__": main()
