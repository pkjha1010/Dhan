"""bpb_bb_report.py - pure-breakout + Bollinger results, LONG and SHORT SEPARATELY, per entry rule and per exact entry day B+n.   No API calls.
  python bpb_bb_report.py [min_trades]

  B = the breakout day, B+1 = the next trading day, B+2 ... (every table says which).
  ENTRY RULES (sets, all made from the same fetched entries):
     B+1 onward   no skip: the first touch of the level from B+1 on
     B+2 onward   skip only B+1: touches on B+1 are ignored and do not use the setup up
     B+3 onward   YOUR SCRIPT EXACTLY (its day counter skips B+1 and B+2)
  and for every set the exact entry day:  B+1, B+2, B+3, B+4, B+5 and B+6 or later.
  If the data also holds entries that fail the Bollinger filter (BBB_BB_ONLY=0) every set also exists as '... noBB' = without the filter.
Reads   bpb_bb_results/{long,short}/trades_all_variants.csv.gz
Writes  bpb_bb_report/long/ and bpb_bb_report/short/ : COMPARE.md, ALL_SETS.csv, BY_BPLUS.csv, BEST_BY_YEAR.csv  (and the same with _prem_gt5 = entry premium above Rs 5), plus bpb_bb_report/SUMMARY.md
"""
import sys, os
import numpy as np, pandas as pd

SRC = os.environ.get("BBR_SRC") or "bpb_bb_results"
OUT = os.environ.get("BBR_OUT") or "bpb_bb_report"
DIRS = ("long", "short")
RULES = [("B+1 onward", "from_b1"), ("B+2 onward", "from_b2"), ("B+3 onward (your script)", "from_b3")]
MIN_TRADES = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 30
BPLUS_BUCKETS = [1, 2, 3, 4, 5, 6]                                              # 6 = B+6 or later


def md(df, index=False):
    try: return df.to_markdown(index=index)
    except Exception: return df.to_string(index=index)


def bucket(b):
    b = pd.to_numeric(b, errors="coerce")
    return b.clip(upper=BPLUS_BUCKETS[-1]).map(lambda v: "" if v != v else (f"B+{int(v)}" if v < BPLUS_BUCKETS[-1] else f"B+{BPLUS_BUCKETS[-1]} or later"))


def build_sets(T):
    """T = trades_all_variants of one direction.  -> {set name: trades}.  Needs b_plus, from_b1..3, bb_ok."""
    for c in ("from_b1", "from_b2", "from_b3", "bb_ok"): T[c] = pd.to_numeric(T[c], errors="coerce").fillna(0).astype(int)
    T = T.assign(entry_day=bucket(T.b_plus))
    sets = {}
    for name, col in RULES:
        sets[name] = T[(T[col] == 1) & (T.bb_ok == 1)]
        if (T.bb_ok == 0).any(): sets[name + " noBB"] = T[T[col] == 1]
    return sets


def _agg(T, keys):
    g = T.assign(win=(T.pnl > 0).astype(int), gp=T.pnl.clip(lower=0), gl=(-T.pnl).clip(lower=0)).groupby(keys)
    a = g.agg(trades=("pnl", "size"), wins=("win", "sum"), total_pnl=("pnl", "sum"), capital=("cost", "sum"), gp=("gp", "sum"), gl=("gl", "sum"), avg_ret_pct=("ret_pct", "mean")).reset_index()
    a["win_pct"] = (a.wins / a.trades * 100).round(1); a["roi_pct"] = (a.total_pnl / a.capital * 100).round(2)
    a["profit_factor"] = (a.gp / a.gl.replace(0, np.nan)).round(2); a["avg_ret_pct"] = a.avg_ret_pct.round(2); a["total_pnl"] = a.total_pnl.round()
    return a.drop(columns=["wins", "capital", "gp", "gl"])


def stats_tables(sets, min_price):
    """-> (all sets table, by exact B+n table)."""
    A_, B_ = [], []
    for name, T in sets.items():
        if min_price: T = T[T.entry_price > min_price]
        if T.empty: continue
        a = _agg(T, ["exit_rule", "sl", "tp"]); a.insert(0, "set", name); A_.append(a)
        b = _agg(T, ["entry_day", "exit_rule", "sl", "tp"]); b.insert(0, "set", name); B_.append(b)
    return (pd.concat(A_, ignore_index=True) if A_ else pd.DataFrame(), pd.concat(B_, ignore_index=True) if B_ else pd.DataFrame())


def best_by_year(sets, S, min_price):
    out = []
    for name, g in S[S.trades >= MIN_TRADES].groupby("set"):
        b = g.sort_values("total_pnl", ascending=False).iloc[0]
        T = sets[name]; T = T[(T.exit_rule == b.exit_rule) & (T.sl == b.sl) & (T.tp == b.tp)]
        if min_price: T = T[T.entry_price > min_price]
        y = T.assign(year=T.entry_date.str[:4]).groupby("year").agg(trades=("pnl", "size"), total_pnl=("pnl", "sum"), win_pct=("pnl", lambda x: round((x > 0).mean() * 100, 1))).reset_index()
        y.insert(0, "variant", f"{b.exit_rule} | SL {int(b.sl) or 'none'} | TP {int(b.tp) or 'none'}"); y.insert(0, "set", name); y["total_pnl"] = y.total_pnl.round(); out.append(y)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def lab(v): return "none" if not v else f"{int(v)}%"


def entries_table(sets, min_price):
    rows = []
    for name, T in sets.items():
        if min_price: T = T[T.entry_price > min_price]
        e = T.drop_duplicates(["stock", "entry_date", "entry_time"])
        rows.append(dict(set=name, entries=len(e), **{k: int((e.entry_day == k).sum()) for k in [f"B+{i}" for i in BPLUS_BUCKETS[:-1]] + [f"B+{BPLUS_BUCKETS[-1]} or later"]}))
    return pd.DataFrame(rows)


def write_report(d, S, Bp, Y, ent, suffix, title):
    cols = ["set", "exit_rule", "sl", "tp", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "avg_ret_pct"]
    S = S.copy(); S["sl"] = S.sl.map(lab); S["tp"] = S.tp.map(lab); Bp = Bp.copy(); Bp["sl"] = Bp.sl.map(lab); Bp["tp"] = Bp.tp.map(lab)
    DIR = d.upper()
    L = [f"# Pure breakout + Bollinger - {DIR} ({'call' if d == 'long' else 'put'}) - {title}", "",
         "**B = the breakout day. B+1 = the next trading day, B+2 = the day after, ...**", "",
         "Entry rules: **B+1 onward** (no skip) | **B+2 onward** (skip only B+1) | **B+3 onward (your script)** (its day counter skips B+1 and B+2). 'noBB' = without the Bollinger filter (only if that data was fetched).", "",
         "## Entries by entry day (distinct stock/day with option data)", "", md(ent), ""]
    base = S[(S.exit_rule == "15:30") & (S.sl == "none") & (S.tp == "none")][cols]
    L += [f"## {DIR}: no stop-loss, no target, exit 15:30 (hold to the close)", "", md(base), ""]
    for name in S.set.unique():
        g = S[(S.set == name) & (S.trades >= MIN_TRADES)]
        L += [f"## {DIR} - {name}: top 10 variants by total PnL (at least {MIN_TRADES} trades)", "", md(g.sort_values("total_pnl", ascending=False).head(10)[cols]) if len(g) else "(none)", ""]
    for name in S.set.unique():
        g = S[(S.set == name) & (S.exit_rule == "15:30")]
        if g.empty: continue
        P = g.pivot_table(index="sl", columns="tp", values="total_pnl", aggfunc="first")
        P = P.reindex(index=[x for x in ("none", "20%", "40%", "60%") if x in P.index], columns=[x for x in ("40%", "60%", "80%", "120%", "none") if x in P.columns])
        L += [f"### {DIR} - {name}: total PnL (Rs), exit 15:30, rows stop-loss, columns target", "", md(P, index=True), ""]
    c2 = ["set", "entry_day", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "avg_ret_pct"]
    for name in S.set.unique():
        g = Bp[(Bp.set == name) & (Bp.exit_rule == "15:30") & (Bp.sl == "none") & (Bp.tp == "none")]
        if len(g): L += [f"## {DIR} - {name}: result by exact entry day B+n (no SL, no TP, exit 15:30)", "", md(g.sort_values("entry_day")[c2]), ""]
    bestrow = S[S.trades >= MIN_TRADES].sort_values("total_pnl", ascending=False)
    for name in S.set.unique():
        g = bestrow[bestrow.set == name]
        if g.empty: continue
        b = g.iloc[0]; x = Bp[(Bp.set == name) & (Bp.exit_rule == b.exit_rule) & (Bp.sl == b.sl) & (Bp.tp == b.tp)]
        L += [f"## {DIR} - {name}: its best variant ({b.exit_rule} | SL {b.sl} | TP {b.tp}) by exact entry day B+n", "", md(x.sort_values("entry_day")[c2]), ""]
    if len(Y): L += [f"## {DIR}: best variant of every entry rule, year by year (is it one lucky year?)", "", md(Y), ""]
    L += ["The best variants are the best of 100 per entry rule, picked after seeing the results, so they are optimistic: check their neighbours (matrices) and the other exits. Charges, taxes, slippage not included. "
          "Rows with few trades (some B+n days) are noise. Lot sizes are today's values.", ""]
    open(f"{OUT}/{d}/COMPARE{suffix}.md", "w").write("\n".join(L))


def main():
    found = []
    for d in DIRS:
        p = f"{SRC}/{d}/trades_all_variants.csv.gz"
        if not os.path.exists(p): print(f"no {p} yet - run the backtest first"); continue
        T = pd.read_csv(p)
        if "b_plus" not in T.columns or "from_b1" not in T.columns: print(f"{p} has no b_plus / from_b1 column - it was not made by bpb_bb_backtest.py"); continue
        os.makedirs(f"{OUT}/{d}", exist_ok=True); sets = build_sets(T); found.append(d)
        for min_price, suffix, title in ((0, "", "all premiums"), (5, "_prem_gt5", "entry premium above Rs 5")):
            S, Bp = stats_tables(sets, min_price)
            if S.empty: continue
            S.to_csv(f"{OUT}/{d}/ALL_SETS{suffix}.csv", index=False); Bp.to_csv(f"{OUT}/{d}/BY_BPLUS{suffix}.csv", index=False)
            Y = best_by_year(sets, S, min_price); Y.to_csv(f"{OUT}/{d}/BEST_BY_YEAR{suffix}.csv", index=False)
            write_report(d, S, Bp, Y, entries_table(sets, min_price), suffix, title)
            print(f"wrote {OUT}/{d}/COMPARE{suffix}.md ({len(S)} rows)", flush=True)
    if found:
        L = ["# Pure breakout + Bollinger - reports", "", "B = the breakout day, B+n = n trading days after it.  LONG and SHORT are separate:", ""] + [f"- `{d}/COMPARE.md` ({d.upper()}), `{d}/COMPARE_prem_gt5.md`, `{d}/ALL_SETS.csv`, `{d}/BY_BPLUS.csv`, `{d}/BEST_BY_YEAR.csv`" for d in found]
        open(f"{OUT}/SUMMARY.md", "w").write("\n".join(L) + "\n")
        print(open(f"{OUT}/{found[0]}/COMPARE.md").read()[:5000])


if __name__ == "__main__": main()
