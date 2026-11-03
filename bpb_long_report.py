"""bpb_long_report.py - BPB LONG results WITH and WITHOUT the NIFTY50 filter, and the survivors after CUTTING THE TOP 10 % of trades.   No API calls.
  python bpb_long_report.py [min_trades]

  NIFTY50 filter (same rule as the GAP study, gap_nifty_rules.py): LONG only when NIFTY50 price at the entry minute > NIFTY50 open of the same day.  Uses the cached NIFTY50 1-minute
  candles (gap_nifty_results/nifty_1min.csv.gz); the filter only removes trades, nothing is re-fetched.
  Trim10 (same as gap_trim_months.py): per combo (entry type x entry slot x time exit x SL x TP, entry premium > Rs 5) drop the best 10 % of trades (rounded up);
  SURVIVOR = trades >= 30, trimmed PnL > 0, trimmed PF >= 1.2;  MONTH SURVIVOR = survivor and >= 60 % of the months with trades profitable.
Reads   bpb_long_results/{type1,type2}/trades_all_variants.csv.gz
Writes  bpb_long_nifty_results/{type1,type2}/trades_all_variants.csv.gz (kept trades + nifty_open / nifty_price), COMPARE.md / compare.csv, TRIM10.md, ALL_COMBOS.csv, SURVIVORS.csv, nifty_days.csv
"""
import sys, os
_argv = sys.argv; sys.argv = sys.argv[:1]                                   # gap_trim_months / gap_survivors read sys.argv at import
import numpy as np, pandas as pd
import gap_nifty_rules as NR
import gap_trim_months as M, gap_survivors as G
sys.argv = _argv

SRC = os.environ.get("BR_SRC") or "bpb_long_results"
OUT = os.environ.get("BR_OUT") or "bpb_long_nifty_results"
NIFTY = os.environ.get("BR_NIFTY") or "gap_nifty_results/nifty_1min.csv.gz"
DIRS = ("type1", "type2")
MIN_PRICE = 5.0
MIN_TRADES = int(sys.argv[1]) if len(sys.argv) > 1 else 30


def load_nifty():
    d = pd.read_csv(NIFTY, parse_dates=["t"]).set_index("t"); return d[["o", "h", "l", "c"]].sort_index()


def stats(g):
    p = g.pnl.values
    if len(p) == 0: return dict(trades=0, win_pct=np.nan, total_pnl=0, pf=np.nan, median_ret_pct=np.nan)
    w = p[p > 0].sum(); l = -p[p < 0].sum()
    return dict(trades=len(p), win_pct=round((p > 0).mean() * 100, 1), total_pnl=round(p.sum()), pf=round(w / l, 2) if l > 0 else np.inf, median_ret_pct=round(g.ret_pct.median(), 1))


def compare(before, after):
    keys = ["type", "exit_rule", "sl", "tp"]; rows = []
    b = before[before.entry_price > MIN_PRICE]; a = after[after.entry_price > MIN_PRICE]; ga_ = {k: g for k, g in a.groupby(keys)}
    for k, g in b.groupby(keys):
        sb, sa = stats(g), stats(ga_.get(k, a.iloc[0:0]))
        rows.append({**dict(zip(keys, k)), **{f"before_{x}": v for x, v in sb.items()}, **{f"after_{x}": v for x, v in sa.items()}})
    return pd.DataFrame(rows)


def trim_table(sets):
    """sets = {name: trades DataFrame with a 'type' column} -> table of every combo (premium > Rs 5) with trimmed stats."""
    rows = []
    for name, T in sets.items():
        T = T[T.entry_price > MIN_PRICE].copy(); T["slot"] = T.entry_time.map(G.slot_of); T = T.dropna(subset=["slot"])
        for scope, sub in (("all-day", T.assign(slot="all-day")), ("by-slot", T)):
            r = sub.groupby(["type", "slot", "exit_rule", "sl", "tp"]).apply(M.stats, include_groups=False).reset_index(); r.insert(0, "scope", scope); r.insert(0, "set", name); rows.append(r)
    R = pd.concat(rows, ignore_index=True)
    R["sl"] = R.sl.map(lambda v: "none" if not v else f"{int(v)}%"); R["tp"] = R.tp.map(lambda v: "none" if not v else f"{int(v)}%")
    ok = R.trades >= MIN_TRADES
    R["survivor"] = ok & (R.trim_pnl > 0) & (R.trim_pf >= 1.2); R["month_survivor"] = R.survivor & (R.months_profit_pct >= 60)
    return R, ok


def main():
    nifty = load_nifty(); tables = NR.day_tables(nifty)
    base, kept, days = [], [], []
    for d in DIRS:
        p = f"{SRC}/{d}/trades_all_variants.csv.gz"
        if not os.path.exists(p): print(f"no {p} yet - run the backtest first"); continue
        T = pd.read_csv(p); T["type"] = d
        F = NR.add_nifty_flag(T, tables)
        A = F[F.nifty_ok == True].drop(columns=["nifty_ok"]).copy()
        os.makedirs(f"{OUT}/{d}", exist_ok=True); A.drop(columns=["type"]).to_csv(f"{OUT}/{d}/trades_all_variants.csv.gz", index=False)
        base.append(T); kept.append(A)
        ent = F.drop_duplicates(["stock", "entry_date", "entry_time"]); days.append(ent[["entry_date", "type", "nifty_ok"]])
        print(f"{d}: {int((ent.nifty_ok == True).sum())} of {len(ent)} entries pass the NIFTY filter, {int((ent.nifty_ok == False).sum())} removed, {int(ent.nifty_ok.isna().sum())} not judgeable (dropped)", flush=True)
    if not base: return
    B, K = pd.concat(base), pd.concat(kept)
    os.makedirs(OUT, exist_ok=True)
    pd.concat(days).groupby(["entry_date", "type"]).nifty_ok.agg(entries="size", pass_n=lambda s: int((s == True).sum())).reset_index().to_csv(f"{OUT}/nifty_days.csv", index=False)
    Cmp = compare(B, K); Cmp.to_csv(f"{OUT}/compare.csv", index=False)
    cols = ["type", "exit_rule", "sl", "tp", "before_trades", "before_total_pnl", "before_pf", "after_trades", "after_win_pct", "after_total_pnl", "after_pf", "after_median_ret_pct"]
    L = ["# BPB LONG: without vs with the NIFTY50 filter (entry premium > Rs 5, full-day entries)", "",
         "Filter: LONG only when NIFTY50 price at the entry minute > NIFTY50 open of the day.  type1 = first touch, type2 = re-cross after 5 closes below the level.", "",
         "## All variants, before vs after", "", Cmp.sort_values(["type", "after_total_pnl"], ascending=[True, False])[cols].to_markdown(index=False)]
    open(f"{OUT}/COMPARE.md", "w").write("\n".join(L))
    R, ok = trim_table({"no filter": B, "nifty": K}); R.to_csv(f"{OUT}/ALL_COMBOS.csv", index=False)
    S = R[R.survivor].sort_values(["set", "scope", "trim_pnl"], ascending=[True, True, False]); S.to_csv(f"{OUT}/SURVIVORS.csv", index=False)
    sc = ["set", "type", "slot", "exit_rule", "sl", "tp", "trades", "cut", "trim_pnl", "trim_pf", "trim_win_pct", "months_profit", "months_with_trades", "months_profit_pct", "worst_month"]
    T = [f"# BPB LONG - survivors after cutting the top 10 % of trades (premium > Rs 5, min {MIN_TRADES} trades, trimmed PF >= 1.2)", "",
         "Survivors per set / entry type (all-day = whole day pooled, by-slot = per entry-time slot):", "",
         R[ok].groupby(["set", "type", "scope"]).agg(combos=("survivor", "size"), profitable_after_cut=("trim_pnl", lambda s: int((s > 0).sum())), survivors=("survivor", "sum"),
                                                     month_survivors=("month_survivor", "sum"), best_trim_pf=("trim_pf", "max")).reset_index().to_markdown(index=False), ""]
    for name in ("no filter", "nifty"):
        s = S[(S.set == name) & (S.scope == "all-day")]
        T += [f"## {name}: top 10 survivors, whole day pooled", "", s[sc].head(10).to_markdown(index=False) if len(s) else "(none)", ""]
        s = S[(S.set == name) & (S.scope == "by-slot")]
        T += [f"## {name}: top 10 survivors by entry-time slot", "", s[sc].head(10).to_markdown(index=False) if len(s) else "(none)", ""]
    open(f"{OUT}/TRIM10.md", "w").write("\n".join(T)); print("\n".join(T))


if __name__ == "__main__": main()
