"""long_survivors_all.py - LONG survivors of ALL strategy backtests in this repo, one common test.  Reads the existing long/trades_all_variants.csv.gz files (no API calls).

Datasets: gap (plain, Nifty filter, red candle, pullback candle, volume filter), bpb_base (plain, Nifty filter), accum5, accum10, orb (top10), pullback_options.
Every combination = dataset x entry-time slot (and ALL slots together) x [entry_type] x time exit x stop-loss x target.

TRIM    = the best TRIM_PCT (10 %) of the trades by PnL are dropped (ceil), the rest is re-summed.  Also the best 10 % of DAYS are dropped (a rally day counts once).
SURVIVOR = trades >= MIN_TRADES (30) | total PnL > 0 | PnL after the trim > 0 | profit factor after the trim >= 1.0 | positive in >= 2 of 3 periods (2023-24, 2025, 2026; period needs >= 5 trades).
STRONG   = survivor AND profit factor after the trim >= 1.3 AND PnL after dropping the best 10 % days > 0 AND median trade >= -10 %.
Sanity filter: entry premium > MIN_PRICE (Rs 5).
Output: long_survivors/ALL_COMBOS.csv, SURVIVORS.csv, STRONG.csv, BY_DATASET_SLOT.csv.     python long_survivors_all.py [min_price] [min_trades] [trim_pct]
"""
import sys, os, math, numpy as np, pandas as pd

MIN_PRICE = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
MIN_TRADES = int(sys.argv[2]) if len(sys.argv) > 2 else 30
TRIM_PCT = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
OUT = "long_survivors"
DATASETS = [("gap", "gap_results/long/trades_all_variants.csv.gz"), ("gap_nifty", "gap_nifty_results/long/trades_all_variants.csv.gz"),
            ("gap_red_candle", "gap_candle_results/red/long/trades_all_variants.csv.gz"), ("gap_pullback_candle", "gap_candle_results/pullback/long/trades_all_variants.csv.gz"),
            ("gap_vol", "gap_vol_results/long/trades_all_variants.csv.gz"), ("bpb_base", "bpb_base_results/long/trades_all_variants.csv.gz"),
            ("bpb_base_nifty", "bpb_base_nifty_results/long/trades_all_variants.csv.gz"), ("accum5", "accum5_results/long/trades_all_variants.csv.gz"),
            ("accum10", "accum10_results/long/trades_all_variants.csv.gz"), ("orb_top10", "orb_results_top10/long/trades_all_variants.csv.gz"),
            ("pullback_options", "pullback_options_results/all_trades_LONG.csv.gz")]
SLOTS = [("09:15-09:29", "09:15", "09:29"), ("09:30-09:59", "09:30", "09:59"), ("10:00-10:59", "10:00", "10:59"), ("11:00-11:59", "11:00", "11:59"),
         ("12:00-12:59", "12:00", "12:59"), ("13:00-13:59", "13:00", "13:59"), ("14:00-15:20", "14:00", "15:20")]


def slot_of(t):
    for n, a, b in SLOTS:
        if a <= t <= b: return n
    return None


def period(d): return "2023-24" if d < "2025-01-01" else "2025" if d < "2026-01-01" else "2026"


def pf(p):
    w = p[p > 0].sum(); l = -p[p < 0].sum()
    return round(w / l, 2) if l > 0 else np.inf


def stats(g):
    p = g.pnl.values; n = len(p); k = math.ceil(n * TRIM_PCT / 100.0); srt = np.sort(p); trimmed = srt[:n - k]
    dsum = g.groupby("entry_date").pnl.sum(); kd = math.ceil(len(dsum) * TRIM_PCT / 100.0)
    per = {k_: g.pnl[g.per == k_] for k_ in ("2023-24", "2025", "2026")}
    ok = [(len(v) >= 5, v.sum() > 0) for v in per.values()]
    return pd.Series(dict(trades=n, win_pct=round((p > 0).mean() * 100, 1), total_pnl=round(p.sum()), pf=pf(p), removed=k, pnl_ex_top10=round(trimmed.sum()), pf_ex_top10=pf(trimmed),
                          top10_share_pct=round(100 * srt[n - k:].sum() / p.sum()) if p.sum() > 0 else np.nan, pnl_ex_top10_days=round(p.sum() - dsum.nlargest(kd).sum()),
                          median_ret_pct=round(g.ret_pct.median(), 1), pnl_2023_24=round(per["2023-24"].sum()), pnl_2025=round(per["2025"].sum()), pnl_2026=round(per["2026"].sum()),
                          n_2023_24=len(per["2023-24"]), n_2025=len(per["2025"]), n_2026=len(per["2026"]), periods_positive=sum(a and b for a, b in ok)))


def load(name, path):
    T = pd.read_csv(path)
    if "entry_price" not in T.columns and "entry" in T.columns: T = T.rename(columns={"entry": "entry_price"})        # pullback_options naming
    if "entry_type" not in T.columns: T["entry_type"] = "-"
    T["entry_type"] = T.entry_type.astype(str)
    T = T[T.entry_price > MIN_PRICE].copy(); T["slot"] = T.entry_time.str[:5].map(slot_of); T["per"] = T.entry_date.map(period)
    return T.dropna(subset=["slot"])


def main():
    rows = []
    for name, path in DATASETS:
        T = load(name, path); keys = ["entry_type", "exit_rule", "sl", "tp"]
        for part in (T.assign(slot="ALL"), T):
            r = part.groupby(["slot"] + keys).apply(stats, include_groups=False).reset_index(); r.insert(0, "dataset", name); rows.append(r)
        print(f"{name}: {len(T)} trades after the Rs {MIN_PRICE:g} filter", flush=True)
    R = pd.concat(rows, ignore_index=True)
    R["survivor"] = ((R.trades >= MIN_TRADES) & (R.total_pnl > 0) & (R.pnl_ex_top10 > 0) & (R.pf_ex_top10 >= 1.0) & (R.periods_positive >= 2))
    R["strong"] = R.survivor & (R.pf_ex_top10 >= 1.3) & (R.pnl_ex_top10_days > 0) & (R.median_ret_pct >= -10)
    for c in ("sl", "tp"): R[c] = R[c].map(lambda v: v if isinstance(v, str) else ("none" if not v else f"{int(v)}%"))
    os.makedirs(OUT, exist_ok=True)
    R.to_csv(f"{OUT}/ALL_COMBOS.csv", index=False)
    S = R[R.survivor].sort_values("pnl_ex_top10", ascending=False); S.to_csv(f"{OUT}/SURVIVORS.csv", index=False)
    St = R[R.strong].sort_values("pnl_ex_top10", ascending=False); St.to_csv(f"{OUT}/STRONG.csv", index=False)
    ok = R[R.trades >= MIN_TRADES]
    bs = ok.groupby(["dataset", "slot"]).agg(combos=("survivor", "size"), survivors=("survivor", "sum"), strong=("strong", "sum"), best_pnl_ex_top10=("pnl_ex_top10", "max")).reset_index()
    bs.to_csv(f"{OUT}/BY_DATASET_SLOT.csv", index=False)
    print(f"\ncombos {len(R)} | with >= {MIN_TRADES} trades {len(ok)} | survivors {int(R.survivor.sum())} | strong {int(R.strong.sum())}")
    print(bs[bs.survivors > 0].to_string(index=False))


if __name__ == "__main__": main()
