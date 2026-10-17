"""strategy_reports.py - turns the trade list of a backtest into the result CSVs (shared by shaperule_backtest.py and trendline_backtest.py).

Files written into the result folder:
  all_trades.csv            every trade of every variant (one row per trade)
  summary.csv               one row per variant: trades, win rate, total PnL, ROI, profit factor, drawdown ...
  top_by_pnl.csv            variants ranked by total PnL
  top_by_roi.csv            ... by ROI (total PnL / capital used)
  top_by_profit_factor.csv  ... by profit factor (gross profit / gross loss)
  top_by_win_rate.csv       ... by win rate (% of trades with PnL > 0)
The four top_by_* files only list variants with at least MIN_TRADES trades (default 30), so a lucky 3-trade variant cannot top the list.
"""
import numpy as np, pandas as pd

MIN_TRADES = 30
TOP_N = 25


def max_drawdown(pnl):
    c = np.cumsum(pnl)
    return int((c - np.maximum.accumulate(np.concatenate([[0.0], c]))[1:]).min()) if len(c) else 0


def summarise_trades(t, keys=("variant",)):
    rows = []
    for k, g in t.groupby(list(keys), sort=False):
        g = g.sort_values(["date", "entry_time"]); p = g.pnl.values.astype(float); cap = float(g.cost.sum())
        gp, gl = p[p > 0].sum(), -p[p < 0].sum()
        rows.append(dict(zip(keys, k if isinstance(k, tuple) else (k,)),
                         trades=len(g), wins=int((p > 0).sum()), losses=int((p < 0).sum()), win_rate_pct=round((p > 0).mean() * 100, 2),
                         total_pnl=int(p.sum()), capital_used=int(cap), roi_pct=round(p.sum() / cap * 100, 2) if cap else np.nan,
                         avg_pnl=int(p.mean()), best_trade=int(p.max()), worst_trade=int(p.min()),
                         profit_factor=round(gp / gl, 2) if gl > 0 else np.nan, max_drawdown=max_drawdown(p),
                         stop_exits=int(g.reason.astype(str).str.startswith("STOP").sum()), time_exits=int((g.reason == "TIME").sum()),
                         first_date=g.date.min(), last_date=g.date.max()))
    return pd.DataFrame(rows)


def write_reports(t, out, min_trades=MIN_TRADES, top_n=TOP_N):
    """t = trades table with columns variant ('STRATEGY | setup | entry type'), stock, direction, date, entry_time, entry_price, lots, cost, sl, exit_time, exit_price, reason, pnl."""
    if t is None or len(t) == 0:
        print("No trades - nothing to write.", flush=True); return None, None
    t = t.copy()
    parts = t.variant.str.split(" \\| ", expand=True)
    t.insert(0, "entry_type", parts[2]); t.insert(0, "setup", parts[1]); t.insert(0, "strategy", parts[0])
    t["roi_pct"] = (t.pnl / t.cost * 100).round(2)
    t = t.sort_values(["strategy", "setup", "entry_type", "date", "entry_time", "stock"]).reset_index(drop=True)
    t.to_csv(f"{out}/all_trades.csv", index=False)
    s = summarise_trades(t, ("strategy", "setup", "entry_type", "sl"))
    s.insert(0, "variant", s.strategy + " | " + s.setup + " | " + s.entry_type + " | SL" + s.sl.astype(str))
    s = s.sort_values("total_pnl", ascending=False).reset_index(drop=True)
    s.to_csv(f"{out}/summary.csv", index=False)
    r = s[s.trades >= min_trades]
    for name, col in (("pnl", "total_pnl"), ("roi", "roi_pct"), ("profit_factor", "profit_factor"), ("win_rate", "win_rate_pct")):
        r.sort_values(col, ascending=False).head(top_n).to_csv(f"{out}/top_by_{name}.csv", index=False)
    cols = ["variant", "trades", "win_rate_pct", "total_pnl", "roi_pct", "profit_factor", "max_drawdown"]
    print(f"\n{len(t):,} trades in {len(s)} variants.  Top 10 by total PnL (min {min_trades} trades):\n" + r.sort_values("total_pnl", ascending=False).head(10)[cols].to_string(index=False), flush=True)
    return t, s
