"""bpb_bb_report.py - BPB + BOLLINGER results for the four entry sets, LONG and SHORT.   No API calls.
  python bpb_bb_report.py [min_trades]

  ALL      every live signal (a live machine that enters on the touch of the level), no Bollinger filter
  ORIG     only the entries your attached loop would take (entry-day close on the right side of the line), no Bollinger filter
  BB_EOD   ORIG + your Bollinger filter (close of the ENTRY DAY above the upper band / below the lower band) = look-ahead, an UPPER BOUND, not tradeable
  BB_LIVE  ALL + a Bollinger filter that is known at the entry: the entry-minute stock price above the upper band (SHORT: below the lower band) of the PREVIOUS day (closes d-20 .. d-1)
Every set is a subset of the same fetched trades, so the numbers differ only by which entries are kept.   Run for all premiums and for premium > Rs 5 (tiny premiums move in 0.05 ticks and flatter % results).
Reads   bpb_bb_results/{long,short}/trades_all_variants.csv.gz
Writes  bpb_bb_report/COMPARE.md, ALL_SETS.csv, BEST_BY_YEAR.csv (+ the same with _prem_gt5)
"""
import sys, os
import numpy as np, pandas as pd

SRC = os.environ.get("BBR_SRC") or "bpb_bb_results"
OUT = os.environ.get("BBR_OUT") or "bpb_bb_report"
DIRS = ("long", "short")
SETS = ["ALL", "ORIG", "BB_EOD", "BB_LIVE"]
MIN_TRADES = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 30


def md(df, index=False):
    try: return df.to_markdown(index=index)
    except Exception: return df.to_string(index=index)


def build_sets(T):
    """T = trades_all_variants of one direction (needs in_orig, in_live, bb_eod, band_prev, stock_price, ref_yahoo, level).  -> {set name: trades}"""
    for c in ("in_orig", "in_live", "bb_eod"): T[c] = pd.to_numeric(T[c], errors="coerce").fillna(0).astype(int)
    lvl = pd.to_numeric(T["level"], errors="coerce"); ry = pd.to_numeric(T["ref_yahoo"], errors="coerce")
    px_y = pd.to_numeric(T["stock_price"], errors="coerce") * ry / lvl                      # entry-minute price in Yahoo's (split-adjusted) price space, the space the bands are in
    band = pd.to_numeric(T["band_prev"], errors="coerce")
    long = T["direction"].eq("LONG")
    live_ok = np.where(long, px_y > band, px_y < band) & band.notna() & px_y.notna()
    return {"ALL": T[T.in_live == 1], "ORIG": T[T.in_orig == 1], "BB_EOD": T[(T.in_orig == 1) & (T.bb_eod == 1)], "BB_LIVE": T[(T.in_live == 1) & live_ok]}


def stats_table(sets, min_price):
    rows = []
    for name, T in sets.items():
        if min_price: T = T[T.entry_price > min_price]
        if T.empty: continue
        g = T.assign(win=(T.pnl > 0).astype(int), gp=T.pnl.clip(lower=0), gl=(-T.pnl).clip(lower=0)).groupby(["direction", "exit_rule", "sl", "tp"])
        a = g.agg(trades=("pnl", "size"), wins=("win", "sum"), total_pnl=("pnl", "sum"), capital=("cost", "sum"), gp=("gp", "sum"), gl=("gl", "sum"), avg_ret_pct=("ret_pct", "mean")).reset_index()
        a["win_pct"] = (a.wins / a.trades * 100).round(1); a["roi_pct"] = (a.total_pnl / a.capital * 100).round(2)
        a["profit_factor"] = (a.gp / a.gl.replace(0, np.nan)).round(2); a["avg_ret_pct"] = a.avg_ret_pct.round(2); a["total_pnl"] = a.total_pnl.round()
        a.insert(0, "set", name); rows.append(a.drop(columns=["wins", "capital", "gp", "gl"]))
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def best_by_year(sets, S, min_price):
    out = []
    for (name, d), g in S[S.trades >= MIN_TRADES].groupby(["set", "direction"]):
        b = g.sort_values("total_pnl", ascending=False).iloc[0]
        T = sets[name]; T = T[(T.direction == d) & (T.exit_rule == b.exit_rule) & (T.sl == b.sl) & (T.tp == b.tp)]
        if min_price: T = T[T.entry_price > min_price]
        y = T.assign(year=T.entry_date.str[:4]).groupby("year").agg(trades=("pnl", "size"), total_pnl=("pnl", "sum"), win_pct=("pnl", lambda x: round((x > 0).mean() * 100, 1))).reset_index()
        y.insert(0, "variant", f"{b.exit_rule} | SL {int(b.sl) or 'none'} | TP {int(b.tp) or 'none'}"); y.insert(0, "direction", d); y.insert(0, "set", name); y["total_pnl"] = y.total_pnl.round(); out.append(y)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def lab(v): return "none" if not v else f"{int(v)}%"


def write_report(S, Y, n_entries, suffix, title):
    cols = ["set", "exit_rule", "sl", "tp", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "avg_ret_pct"]
    S = S.copy(); S["sl"] = S.sl.map(lab); S["tp"] = S.tp.map(lab)
    L = [f"# BPB + BOLLINGER - {title}", "",
         "Sets: **ALL** every live signal | **ORIG** your exact loop | **BB_EOD** ORIG + your Bollinger filter (entry-day close = look-ahead, upper bound) | **BB_LIVE** ALL + previous-day Bollinger vs the entry price (tradeable).", "",
         "## Entries (distinct stock/day, with option data)", "", md(n_entries), ""]
    for d in ("LONG", "SHORT"):
        G = S[S.direction == d]
        if G.empty: continue
        base = G[(G.exit_rule == "15:30") & (G.sl == "none") & (G.tp == "none")][cols]
        L += [f"## {d}: no stop-loss, no target, exit 15:30 (the plain 'hold to the close')", "", md(base), ""]
        for name in SETS:
            g = G[(G.set == name) & (G.trades >= MIN_TRADES)]
            L += [f"### {d} - {name}: top 10 by total PnL (at least {MIN_TRADES} trades)", "", md(g.sort_values("total_pnl", ascending=False).head(10)[cols]) if len(g) else "(none)", ""]
        for name in SETS:
            g = G[(G.set == name) & (G.exit_rule == "15:30")]
            if g.empty: continue
            P = g.pivot_table(index="sl", columns="tp", values="total_pnl", aggfunc="first")
            P = P.reindex(index=[x for x in ("none", "20%", "40%", "60%") if x in P.index], columns=[x for x in ("40%", "60%", "80%", "120%", "none") if x in P.columns])
            L += [f"### {d} - {name}: total PnL (Rs), exit 15:30, rows stop-loss, columns target", "", md(P, index=True), ""]
    if len(Y): L += ["## Best variant of every set and direction, year by year (is it one lucky year?)", "", md(Y), ""]
    L += ["The best variants are the best of 100 per set, picked after seeing the results, so they are optimistic: check their neighbours (matrices) and the other exits. Charges, taxes, slippage not included. "
          "BB_EOD uses the entry day's closing price and can not be traded live. Lot sizes are today's values.", ""]
    open(f"{OUT}/COMPARE{suffix}.md", "w").write("\n".join(L))


def main():
    sets_all = {s: [] for s in SETS}
    for d in DIRS:
        p = f"{SRC}/{d}/trades_all_variants.csv.gz"
        if not os.path.exists(p): print(f"no {p} yet - run the backtest first"); continue
        T = pd.read_csv(p)
        if "in_orig" not in T.columns: print(f"{p} has no in_orig column - it was not made by bpb_bb_backtest.py"); continue
        for k, v in build_sets(T).items(): sets_all[k].append(v)
    sets = {k: pd.concat(v, ignore_index=True) for k, v in sets_all.items() if v}
    if not sets: return
    os.makedirs(OUT, exist_ok=True)
    for min_price, suffix, title in ((0, "", "all premiums"), (5, "_prem_gt5", "entry premium above Rs 5")):
        S = stats_table(sets, min_price)
        if S.empty: continue
        S.to_csv(f"{OUT}/ALL_SETS{suffix}.csv", index=False)
        Y = best_by_year(sets, S, min_price); Y.to_csv(f"{OUT}/BEST_BY_YEAR{suffix}.csv", index=False)
        ne = pd.DataFrame([dict(set=k, direction=d, entries=int(g[g.direction == d].drop_duplicates(["stock", "entry_date", "entry_time"]).shape[0]) if min_price == 0 else
                                int(g[(g.direction == d) & (g.entry_price > min_price)].drop_duplicates(["stock", "entry_date", "entry_time"]).shape[0])) for k, g in sets.items() for d in ("LONG", "SHORT")])
        write_report(S, Y, ne, suffix, title)
        print(f"wrote {OUT}/COMPARE{suffix}.md ({len(S)} rows)", flush=True)
    print(open(f"{OUT}/COMPARE.md").read()[:6000])


if __name__ == "__main__": main()
