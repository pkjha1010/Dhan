"""gap_combo_report.py - one exact combo: python gap_combo_report.py LONG 09:16 15:30 40 80 [min_price]   (entry minute, time exit, SL %, TP %; 0 = none)
Writes gap_results/combo_reports/<name>/trades.csv, monthly.csv, REPORT.md (all trades, then after cutting the top 10 % of trades)."""
import sys, os, numpy as np, pandas as pd
D, EM, EX, SL, TP = sys.argv[1].upper(), sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]); MP = float(sys.argv[6]) if len(sys.argv) > 6 else 5.0
OUT = "gap_results"
T = pd.read_csv(f"{OUT}/{D.lower()}/trades_all_variants.csv.gz"); T = T[(T.entry_time == EM) & (T.exit_rule == EX) & (T.sl == SL) & (T.tp == TP)]
raw = len(T); T = T[T.entry_price > MP].sort_values(["entry_date", "stock"]).reset_index(drop=True)


def pf(p): w = p[p > 0].sum(); l = -p[p < 0].sum(); return round(w / l, 2) if l > 0 else float("inf")


def block(g):
    return dict(trades=len(g), win_pct=round((g.pnl > 0).mean() * 100, 1), total_pnl=round(g.pnl.sum()), pf=pf(g.pnl.values), avg_pnl=round(g.pnl.mean()), avg_ret_pct=round(g.ret_pct.mean(), 1), median_ret_pct=round(g.ret_pct.median(), 1),
                best=round(g.pnl.max()), worst=round(g.pnl.min()), tp_hits=int(g.reason.str.startswith("TARGET").sum()) if "reason" in g else 0, sl_hits=int(g.reason.str.startswith("STOP").sum()) if "reason" in g else 0)


p = T.pnl.sort_values(ascending=False); k = max(1, int(np.ceil(len(p) * .1))); K = T.loc[p.index[k:]]
mo = T.groupby(T.entry_date.str[:7]).agg(trades=("pnl", "size"), pnl=("pnl", "sum")).round(0); mk = K.groupby(K.entry_date.str[:7]).agg(trades_after_cut=("pnl", "size"), pnl_after_cut=("pnl", "sum")).round(0)
M = mo.join(mk, how="left").fillna(0).reset_index().rename(columns={"entry_date": "month"})
yr = lambda d: "2023-24" if d < "2025-01-01" else "2025" if d < "2026-01-01" else "2026"
Y = pd.DataFrame({"all": T.groupby(T.entry_date.map(yr)).pnl.agg(["size", "sum"]).round(0).stack(), "after_cut": K.groupby(K.entry_date.map(yr)).pnl.agg(["size", "sum"]).round(0).stack()}).unstack().T if len(T) else pd.DataFrame()
name = f"{D}_{EM.replace(':', '')}_{EX.replace(':', '')}_SL{SL}_TP{TP}"; o = f"{OUT}/combo_reports/{name}"; os.makedirs(o, exist_ok=True)
T.drop(columns=[c for c in ("entry_type", "strategy") if c in T]).to_csv(f"{o}/trades.csv", index=False); M.to_csv(f"{o}/monthly.csv", index=False)
a, b = block(T), block(K); st = T.groupby("stock").pnl.sum().sort_values(ascending=False)
L = [f"# {D} entry {EM} | exit {EX} | SL {SL or 'none'}% | TP {TP or 'none'}%  (premium > Rs {MP:g}; {raw - len(T)} of {raw} entries dropped by the premium filter)", "",
     "| | trades | win % | total PnL | PF | avg PnL | avg ret % | median ret % | best | worst | TP hits | SL hits |", "|---|---|---|---|---|---|---|---|---|---|---|---|",
     "| all | " + " | ".join(str(a[x]) for x in a) + " |", f"| after top 10% cut ({k} trades removed) | " + " | ".join(str(b[x]) for x in b) + " |", "",
     f"Months with trades: {len(M)}; profitable (all trades): {int((M.pnl > 0).sum())}; profitable after the cut: {int((M.pnl_after_cut > 0).sum())} (months left with no trades count as not profitable).", "",
     f"Stocks: {T.stock.nunique()}; entry days: {T.entry_date.nunique()}; best 5 stocks = {st.head(5).sum() / max(T.pnl.sum(), 1):.0%} of total PnL; best 3 days = {T.groupby('entry_date').pnl.sum().nlargest(3).sum() / max(T.pnl.sum(), 1):.0%}.", "",
     "## By period", "", Y.to_markdown() if len(Y) else "", "", "## Month-wise", "", M.to_markdown(index=False), ""]
open(f"{o}/REPORT.md", "w").write("\n".join(L)); print("\n".join(L))
