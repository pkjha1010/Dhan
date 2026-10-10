"""d3y_range_summary.py - summary tables of the saved d3y results for a date range YOU choose. No API calls.
  python d3y_range_summary.py 2025-01-01 2025-12-31 [min_trades]
Reads  d3y_results/parts/*.csv.gz   (made by d3y_backtest.py)
Writes d3y_range_out/<start>_to_<end>/...   (its own folder per range, so nothing is overwritten and nothing conflicts)
Filter is on the ENTRY date (both dates included)."""
import sys, os, glob
import pandas as pd

SRC = os.environ.get("D3Y_SRC", "d3y_results")
start = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("RANGE_START", "")
end = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("RANGE_END", "")
mt = int((sys.argv[3] if len(sys.argv) > 3 else os.environ.get("MIN_TRADES", "")) or 30)
if not start or not end: sys.exit("give start and end date, like: python d3y_range_summary.py 2025-01-01 2025-12-31")
pd.Timestamp(start); pd.Timestamp(end)                                   # fail early on a bad date
out = f"d3y_range_out/{start}_to_{end}"
os.makedirs(out, exist_ok=True)

fs = sorted(glob.glob(f"{SRC}/parts/*.csv.gz"))
if not fs: sys.exit(f"No saved results found in {SRC}/parts")
t = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
t = t[(t.date >= start) & (t.date <= end)]
if t.empty: sys.exit(f"No trades with entry date between {start} and {end}")
print(f"{len(t):,} result rows, entry dates {t.date.min()} to {t.date.max()}, {t[['stock', 'date', 'type']].drop_duplicates().shape[0]:,} entries")


def agg(g):
    w = g.pnl > 0
    gain, loss = g.pnl[w].sum(), -g.pnl[~w].sum()
    return pd.Series(dict(trades=len(g), wins=int(w.sum()), win_pct=round(w.mean() * 100, 1),
                          stops=int(g.reason.str.startswith("STOP").sum()), targets=int(g.reason.str.startswith("TARGET").sum()),
                          time_exits=int((g.reason == "TIME").sum()), total_pnl=int(g.pnl.sum()), capital=int(g.cost.sum()),
                          roi_pct=round(g.pnl.sum() / g.cost.sum() * 100, 2), avg_pnl=int(g.pnl.mean()),
                          profit_factor=round(gain / loss, 2) if loss > 0 else None, thin_data=int(g.thin_data.sum())))


def agg_hit(g):
    h, tm = g[g.reason != "TIME"], g[g.reason == "TIME"]
    tg, sp = h[h.reason.str.startswith("TARGET")], h[h.reason.str.startswith("STOP")]
    return pd.Series(dict(all_trades=len(g), hit_trades=len(h), targets=len(tg), stops=len(sp),
                          hit_win_pct=round(len(tg) / len(h) * 100, 1) if len(h) else None, hit_pnl=int(h.pnl.sum()), hit_capital=int(h.cost.sum()),
                          hit_roi_pct=round(h.pnl.sum() / h.cost.sum() * 100, 2) if len(h) else None,
                          time_exits=len(tm), time_exit_pnl=int(tm.pnl.sum()), time_exit_win_pct=round((tm.pnl > 0).mean() * 100, 1) if len(tm) else None,
                          all_pnl=int(g.pnl.sum()), all_roi_pct=round(g.pnl.sum() / g.cost.sum() * 100, 2)))


key = ["type", "exit_rule", "sl", "tp"]
a = t.groupby(key).apply(agg).reset_index()
h = t.groupby(key).apply(agg_hit).reset_index()
a.to_csv(f"{out}/all_trades_all.csv", index=False)
a[a.trades >= mt].sort_values("roi_pct", ascending=False).head(60).to_csv(f"{out}/all_trades_top60_roi.csv", index=False)
a[a.trades >= mt].sort_values("total_pnl", ascending=False).head(60).to_csv(f"{out}/all_trades_top60_pnl.csv", index=False)
h.to_csv(f"{out}/hit_only_all.csv", index=False)
h[h.hit_trades >= mt].sort_values("hit_roi_pct", ascending=False).head(60).to_csv(f"{out}/hit_only_top60_roi.csv", index=False)
good = a[a.trades >= mt]
if len(good): good.loc[good.groupby("type").roi_pct.idxmax()].to_csv(f"{out}/best_per_entry_type.csv", index=False)
print(f"\nSaved in {out}/")
if len(good):
    print("\nBEST COMBINATION PER ENTRY TYPE (by ROI, at least", mt, "trades):\n" + pd.read_csv(f"{out}/best_per_entry_type.csv").to_string(index=False))
    print("\nTOP 10 BY ROI:\n" + good.sort_values("roi_pct", ascending=False).head(10).to_string(index=False))
else:
    print(f"No combination has {mt} trades in this range - lower the minimum trades.")
