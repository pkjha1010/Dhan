"""gap_slot_range.py - GAP combos for ONE direction and an entry-minute RANGE (inclusive), top 10 % of trades cut, month-wise.  No API calls.
python gap_slot_range.py LONG 09:20 09:30 [min_price] [min_trades]      -> gap_results/slot_range/<DIR>_<from>_<to>/ALL_COMBOS.csv, SURVIVORS.csv, REPORT.md, MONTHLY_best.csv
SURVIVOR = trades >= min_trades, trimmed PnL > 0, trimmed PF >= 1.2, >= 60 % of months profitable after the cut."""
import sys, os, numpy as np, pandas as pd
D = sys.argv[1].upper(); A = sys.argv[2]; B = sys.argv[3]; MIN_PRICE = float(sys.argv[4]) if len(sys.argv) > 4 else 5.0; MIN_TRADES = int(sys.argv[5]) if len(sys.argv) > 5 else 30
OUT = "gap_results"


def pf(p):
    w = p[p > 0].sum(); l = -p[p < 0].sum(); return round(w / l, 2) if l > 0 else np.inf


def per(d): return "2023-24" if d < "2025-01-01" else "2025" if d < "2026-01-01" else "2026"


def trim(g):
    p = g.pnl.sort_values(ascending=False); return g.loc[p.index[max(1, int(np.ceil(len(p) * .1))):]]


def stats(g):
    keep = trim(g); m = keep.groupby(keep.entry_date.str[:7]).pnl.sum(); allm = g.entry_date.str[:7].nunique()
    pp = keep.groupby(keep.entry_date.map(per)).pnl.sum()
    return pd.Series(dict(trades=len(g), win_pct=round((g.pnl > 0).mean() * 100, 1), total_pnl=round(g.pnl.sum()), pf=pf(g.pnl.values), trim_pnl=round(keep.pnl.sum()), trim_pf=pf(keep.pnl.values),
                          trim_win_pct=round((keep.pnl > 0).mean() * 100, 1), trim_median_ret_pct=round(keep.ret_pct.median(), 1), months=allm, months_profit=int((m > 0).sum()),
                          months_profit_pct=round((m > 0).sum() / allm * 100, 1), worst_month=round(m.min()), trim_2023_24=round(pp.get("2023-24", 0)), trim_2025=round(pp.get("2025", 0)), trim_2026=round(pp.get("2026", 0))))


T = pd.read_csv(f"{OUT}/{D.lower()}/trades_all_variants.csv.gz"); T = T[(T.entry_price > MIN_PRICE) & (T.entry_time >= A) & (T.entry_time <= B)]
R = T.groupby(["exit_rule", "sl", "tp"]).apply(stats, include_groups=False).reset_index()
R["sl"] = R.sl.map(lambda v: "none" if not v else f"{int(v)}%"); R["tp"] = R.tp.map(lambda v: "none" if not v else f"{int(v)}%")
R["survivor"] = (R.trades >= MIN_TRADES) & (R.trim_pnl > 0) & (R.trim_pf >= 1.2) & (R.months_profit_pct >= 60)
o = f"{OUT}/slot_range/{D}_{A.replace(':', '')}_{B.replace(':', '')}"; os.makedirs(o, exist_ok=True)
R = R.sort_values("trim_pnl", ascending=False); R.to_csv(f"{o}/ALL_COMBOS.csv", index=False); R[R.survivor].to_csv(f"{o}/SURVIVORS.csv", index=False)
cols = ["exit_rule", "sl", "tp", "trades", "win_pct", "total_pnl", "pf", "trim_pnl", "trim_pf", "trim_win_pct", "months_profit", "months", "months_profit_pct", "worst_month", "trim_2023_24", "trim_2025", "trim_2026"]
L = [f"# GAP {D} entries {A}-{B} (premium > Rs {MIN_PRICE:g}), top 10 % of trades cut", "",
     f"{len(T[['stock','entry_date','entry_time']].drop_duplicates())} entries; {len(R)} combos; profitable before cut {int((R.total_pnl > 0).sum())}; after cut {int((R.trim_pnl > 0).sum())}; trimmed PF>=1.2 {int(((R.trim_pnl > 0) & (R.trim_pf >= 1.2)).sum())}; with >=60% months profitable **{int(R.survivor.sum())}**.", "",
     "## Top 15 by trimmed PnL", "", R[cols].head(15).to_markdown(index=False), "", "## Top 10 by months profitable (trimmed PnL > 0)", "", R[R.trim_pnl > 0].sort_values(["months_profit_pct", "trim_pnl"], ascending=False)[cols].head(10).to_markdown(index=False), ""]
b = R.iloc[0]; g = T[(T.exit_rule == b.exit_rule) & (T.sl == (0 if b.sl == "none" else int(b.sl[:-1]))) & (T.tp == (0 if b.tp == "none" else int(b.tp[:-1])))]
k = trim(g); mm = k.groupby(k.entry_date.str[:7]).agg(trades=("pnl", "size"), pnl=("pnl", "sum")).round(0); mm.to_csv(f"{o}/MONTHLY_best.csv")
L += [f"## Month-wise, best combo (exit {b.exit_rule} | SL {b.sl} | TP {b.tp}) after the cut", "", mm.reset_index().to_markdown(index=False), ""]
open(f"{o}/REPORT.md", "w").write("\n".join(L)); print("\n".join(L))
