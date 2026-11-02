"""gap_candle_trim.py - survivors after CUTTING THE TOP 10 % OF TRADES for the GAP candle-filter sets (base = no filter, red, pullback), by entry minute 09:16 and by slot 09:15-09:29.  No API calls.
Same rule as gap_trim_months.py: per combo (direction x entry x exit x SL x TP, premium > Rs 5) drop the best 10 % of trades (rounded up), then SURVIVOR = trades >= 30, trimmed PnL > 0, trimmed PF >= 1.2;
month survivor = survivor and >= 60 % of the months with trades profitable.   Output gap_candle_results/trim10/ALL_COMBOS.csv, SURVIVORS.csv, TRIM10.md.   python gap_candle_trim.py [min_trades]"""
import sys, os, numpy as np, pandas as pd
import gap_trim_months as M, gap_survivors as G

SETS = {"base": "gap_results", "red": "gap_candle_results/red", "pullback": "gap_candle_results/pullback"}
MIN_TRADES = int(sys.argv[1]) if len(sys.argv) > 1 else 30
OUT = "gap_candle_results/trim10"


def main():
    rows = []
    for name, path in SETS.items():
        for d in ("long", "short"):
            T = pd.read_csv(f"{path}/{d}/trades_all_variants.csv.gz"); T = T[T.entry_price > 5].copy(); T["slot"] = T.entry_time.map(G.slot_of)
            for ent, sub in (("09:16", T[T.entry_time == "09:16"]), ("09:15-09:29", T[T.slot == "09:15-09:29"])):
                r = sub.groupby(["exit_rule", "sl", "tp"]).apply(M.stats, include_groups=False).reset_index()
                r.insert(0, "entry", ent); r.insert(0, "direction", d.upper()); r.insert(0, "set", name); rows.append(r)
    R = pd.concat(rows, ignore_index=True)
    R["sl"] = R.sl.map(lambda v: "none" if not v else f"{int(v)}%"); R["tp"] = R.tp.map(lambda v: "none" if not v else f"{int(v)}%")
    ok = R.trades >= MIN_TRADES
    R["survivor"] = ok & (R.trim_pnl > 0) & (R.trim_pf >= 1.2); R["month_survivor"] = R.survivor & (R.months_profit_pct >= 60)
    os.makedirs(OUT, exist_ok=True); R.to_csv(f"{OUT}/ALL_COMBOS.csv", index=False)
    S = R[R.survivor].sort_values(["set", "direction", "entry", "trim_pnl"], ascending=[True, True, True, False]); S.to_csv(f"{OUT}/SURVIVORS.csv", index=False)
    cols = ["set", "exit_rule", "sl", "tp", "trades", "cut", "trim_pnl", "trim_pf", "trim_win_pct", "months_profit", "months_with_trades", "months_profit_pct", "worst_month"]
    L = [f"# GAP candle filters - survivors after cutting the top 10 % of trades (premium > Rs 5, min {MIN_TRADES} trades, trimmed PF >= 1.2)", "",
         R[ok].groupby(["direction", "entry", "set"]).agg(combos=("survivor", "size"), survivors=("survivor", "sum"), month_survivors=("month_survivor", "sum"), best_trim_pf=("trim_pf", "max")).reset_index().to_markdown(index=False), ""]
    for d in ("LONG", "SHORT"):
        for e in ("09:16", "09:15-09:29"):
            s = S[(S.direction == d) & (S.entry == e)].sort_values("trim_pnl", ascending=False)
            L += [f"## {d} entry {e}: best 8 survivors by trimmed PnL (all sets)", "", s[cols].head(8).to_markdown(index=False) if len(s) else "(none)", ""]
    open(f"{OUT}/TRIM10.md", "w").write("\n".join(L)); print("\n".join(L))


if __name__ == "__main__": main()
