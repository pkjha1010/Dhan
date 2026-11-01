"""gap_trim_months.py - survivors after CUTTING THE TOP 10 % OF TRADES, plus month-wise survival.  No API calls.
For every direction x entry slot x time exit x SL x TP combo (entry premium > MIN_PRICE, default Rs 5):
  1. sort the combo's trades by PnL, drop the best 10 % (rounded up, min 1);  2. trimmed total PnL / profit factor of the rest;
  3. month-wise on the trimmed trades: months with trades, months with profit, % of months profitable.
SURVIVOR (trimmed) = trades >= MIN_TRADES, trimmed PnL > 0, trimmed PF >= 1.2 (PF >= 1.0 also reported).   MONTH SURVIVOR = >= 60 % of the months with trades are profitable.
Output gap_results/survivors_trim10/: ALL_COMBOS.csv, SURVIVORS.csv, MONTHLY_<dir>.csv (month x best combos), TRIM10.md.   python gap_trim_months.py [min_price] [min_trades]
"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gap_survivors as G

OUT = "gap_results"; MIN_PRICE = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0; MIN_TRADES = int(sys.argv[2]) if len(sys.argv) > 2 else 30


def pf(p):
    w = p[p > 0].sum(); l = -p[p < 0].sum(); return round(w / l, 2) if l > 0 else np.inf


def stats(g):
    p = g.pnl.sort_values(ascending=False); k = max(1, int(np.ceil(len(p) * 0.10))); keep = g.loc[p.index[k:]]
    m = keep.groupby(keep.entry_date.str[:7]).pnl.sum(); allm = g.entry_date.str[:7].nunique()
    return pd.Series(dict(trades=len(g), cut=k, total_pnl=round(g.pnl.sum()), pf=pf(g.pnl.values), trim_pnl=round(keep.pnl.sum()), trim_pf=pf(keep.pnl.values),
                          trim_win_pct=round((keep.pnl > 0).mean() * 100, 1), trim_avg_ret_pct=round(keep.ret_pct.mean(), 1),
                          months_with_trades=allm, months_profit=int((m > 0).sum()), months_loss=int((m <= 0).sum()) + max(0, allm - len(m)),
                          months_profit_pct=round((m > 0).sum() / allm * 100, 1) if allm else 0, worst_month=round(m.min()) if len(m) else 0))


def main():
    rows, MON = [], {}
    for d in ("long", "short"):
        T = pd.read_csv(f"{OUT}/{d}/trades_all_variants.csv.gz"); T = T[T.entry_price > MIN_PRICE].copy(); T["slot"] = T.entry_time.map(G.slot_of); T = T.dropna(subset=["slot"])
        r = T.groupby(["slot", "exit_rule", "sl", "tp"]).apply(stats, include_groups=False).reset_index(); r.insert(0, "direction", d.upper()); rows.append(r); MON[d] = T
    R = pd.concat(rows, ignore_index=True)
    R["sl"] = R.sl.map(lambda v: "none" if not v else f"{int(v)}%"); R["tp"] = R.tp.map(lambda v: "none" if not v else f"{int(v)}%")
    ok = R.trades >= MIN_TRADES
    R["survivor_pf1"] = ok & (R.trim_pnl > 0); R["survivor"] = ok & (R.trim_pnl > 0) & (R.trim_pf >= 1.2); R["month_survivor"] = R.survivor & (R.months_profit_pct >= 60)
    o = f"{OUT}/survivors_trim10"; os.makedirs(o, exist_ok=True)
    R.sort_values(["direction", "slot", "exit_rule", "sl", "tp"]).to_csv(f"{o}/ALL_COMBOS.csv", index=False)
    S = R[R.survivor].sort_values(["direction", "trim_pnl"], ascending=[True, False]); S.to_csv(f"{o}/SURVIVORS.csv", index=False)
    cols = ["slot", "exit_rule", "sl", "tp", "trades", "trim_pnl", "trim_pf", "trim_win_pct", "months_profit", "months_with_trades", "months_profit_pct", "worst_month"]
    L = [f"# GAP after cutting the top 10 % of trades (entry premium > Rs {MIN_PRICE:g}, min {MIN_TRADES} trades)", "",
         f"{int(ok.sum())} combos with enough trades. Still profitable after the cut: **{int(R.survivor_pf1.sum())}**; with trimmed PF >= 1.2: **{int(R.survivor.sum())}**; and >= 60 % of months profitable: **{int(R.month_survivor.sum())}**.", "",
         "## Survivors per direction / entry slot", "", R[ok].groupby(["direction", "slot"]).agg(combos=("survivor", "size"), profitable=("survivor_pf1", "sum"), pf12=("survivor", "sum"),
                                                                                                  month_ok=("month_survivor", "sum"), best_trim_pf=("trim_pf", "max"), best_months_pct=("months_profit_pct", "max")).reset_index().to_markdown(index=False), ""]
    for d in ("LONG", "SHORT"):
        s = S[S.direction == d]; L += [f"## {d}: top 15 survivors by trimmed PnL", "", s[cols].head(15).to_markdown(index=False) if len(s) else "(none)", ""]
        b = s.sort_values(["months_profit_pct", "trim_pnl"], ascending=False).head(10); L += [f"## {d}: top 10 by months profitable", "", b[cols].to_markdown(index=False) if len(b) else "(none)", ""]
        if len(s):
            t = s.iloc[0]; T = MON[d.lower()]; sl = {"none": 0}.get(t.sl, None); sl = 0 if t.sl == "none" else int(t.sl[:-1]); tp = 0 if t.tp == "none" else int(t.tp[:-1])
            g = T[(T.slot == t.slot) & (T.exit_rule == t.exit_rule) & (T.sl == sl) & (T.tp == tp)]; p = g.pnl.sort_values(ascending=False); keep = g.loc[p.index[max(1, int(np.ceil(len(p) * .1))):]]
            mm = keep.groupby(keep.entry_date.str[:7]).agg(trades=("pnl", "size"), pnl=("pnl", "sum")).round(0); mm.to_csv(f"{o}/MONTHLY_{d}_best.csv")
            L += [f"### {d} month-wise for the best survivor ({t.slot} | exit {t.exit_rule} | SL {t.sl} | TP {t.tp}) after the cut", "", mm.reset_index().to_markdown(index=False), ""]
    open(f"{o}/TRIM10.md", "w").write("\n".join(L)); print("\n".join(L))


if __name__ == "__main__": main()
