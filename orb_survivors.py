"""orb_survivors.py - which ORB LONG variants SURVIVE after the best 10 % of trades are removed?  Reads orb_results_top10/long/trades_all_variants.csv.gz (no API calls)
and scores every ENTRY TIME SLOT (and ALL slots together) x time exit x stop-loss x target combination.

TRIM   = the best TRIM_PCT (10 %) of the trades by PnL are dropped (ceil), then the rest is re-summed.  Also reported: trim of the best 10 % of DAYS (a market-wide rally day counts once).
SURVIVOR = trades >= MIN_TRADES (30) | total PnL > 0 AND PnL after removing the top 10 % trades > 0 | profit factor after trim >= 1.0 | positive in >= 2 of 3 periods
(2025-11..2026-02, 2026-03..2026-06, 2026-07..2026-11; a period counts only if it has >= 5 trades).
Sanity filter: entry premium > MIN_PRICE (default Rs 5).
Output: orb_results_top10/survivors/ALL_COMBOS.csv, SURVIVORS.csv, BY_SLOT.csv.   python orb_survivors.py [min_price] [min_trades] [trim_pct] [direction]
"""
import sys, os, math, numpy as np, pandas as pd

OUT = os.environ.get("ORB_DIR", "orb_results_top10")
MIN_PRICE = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
MIN_TRADES = int(sys.argv[2]) if len(sys.argv) > 2 else 30
TRIM_PCT = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
DIRECTION = sys.argv[4].lower() if len(sys.argv) > 4 else "long"
SLOTS = [("09:30-09:59", "09:30", "09:59"), ("10:00-10:59", "10:00", "10:59"), ("11:00-11:59", "11:00", "11:59"),
         ("12:00-12:59", "12:00", "12:59"), ("13:00-13:59", "13:00", "13:59"), ("14:00-15:20", "14:00", "15:20")]


def slot_of(t):
    for n, a, b in SLOTS:
        if a <= t <= b: return n
    return None


def period(d): return "P1 25-11..26-02" if d < "2026-03-01" else "P2 26-03..26-06" if d < "2026-07-01" else "P3 26-07..26-11"


def pf(p):
    w = p[p > 0].sum(); l = -p[p < 0].sum()
    return round(w / l, 2) if l > 0 else np.inf


def stats(g):
    p = g.pnl.values; n = len(p); k = math.ceil(n * TRIM_PCT / 100.0)
    trimmed = np.sort(p)[:n - k]
    dsum = g.groupby("entry_date").pnl.sum(); nd = len(dsum); kd = math.ceil(nd * TRIM_PCT / 100.0)
    per = {k_: g.pnl[g.per == k_] for k_ in sorted(g.per.unique())}
    ok = [(len(v) >= 5, v.sum() > 0) for v in per.values()]
    return pd.Series(dict(trades=n, win_pct=round((p > 0).mean() * 100, 1), total_pnl=round(p.sum()), pf=pf(p), removed=k,
                          pnl_ex_top10=round(trimmed.sum()), pf_ex_top10=pf(trimmed), top10_share_pct=round(100 * np.sort(p)[n - k:].sum() / p.sum(), 0) if p.sum() > 0 else np.nan,
                          pnl_ex_top10_days=round(p.sum() - dsum.nlargest(kd).sum()), median_ret_pct=round(g.ret_pct.median(), 1),
                          pnl_p1=round(per.get("P1 25-11..26-02", pd.Series(dtype=float)).sum()), pnl_p2=round(per.get("P2 26-03..26-06", pd.Series(dtype=float)).sum()),
                          pnl_p3=round(per.get("P3 26-07..26-11", pd.Series(dtype=float)).sum()), periods_positive=sum(a and b for a, b in ok)))


def main():
    T = pd.read_csv(f"{OUT}/{DIRECTION}/trades_all_variants.csv.gz")
    T = T[T.entry_price > MIN_PRICE].copy(); T["slot"] = T.entry_time.map(slot_of); T["per"] = T.entry_date.map(period); T = T.dropna(subset=["slot"])
    keys = ["exit_rule", "sl", "tp"]
    by_slot = T.groupby(["slot"] + keys).apply(stats, include_groups=False).reset_index()
    allday = T.assign(slot="ALL 09:30-15:20").groupby(["slot"] + keys).apply(stats, include_groups=False).reset_index()
    R = pd.concat([allday, by_slot], ignore_index=True)
    R["survivor"] = ((R.trades >= MIN_TRADES) & (R.total_pnl > 0) & (R.pnl_ex_top10 > 0) & (R.pf_ex_top10 >= 1.0) & (R.periods_positive >= 2))
    R["sl"] = R.sl.map(lambda v: v if isinstance(v, str) else ("no SL" if not v else f"{int(v)}%"))
    os.makedirs(f"{OUT}/survivors", exist_ok=True)
    R.to_csv(f"{OUT}/survivors/ALL_COMBOS_{DIRECTION}.csv", index=False)
    S = R[R.survivor].sort_values("pnl_ex_top10", ascending=False); S.to_csv(f"{OUT}/survivors/SURVIVORS_{DIRECTION}.csv", index=False)
    bs = R[R.trades >= MIN_TRADES].groupby("slot").agg(combos=("survivor", "size"), survivors=("survivor", "sum"), positive_total=("total_pnl", lambda s: int((s > 0).sum())),
                                                       positive_ex_top10=("pnl_ex_top10", lambda s: int((s > 0).sum())), best_pnl_ex_top10=("pnl_ex_top10", "max")).reset_index()
    bs.to_csv(f"{OUT}/survivors/BY_SLOT_{DIRECTION}.csv", index=False)
    print(f"{DIRECTION.upper()} | price > Rs {MIN_PRICE:g} | min {MIN_TRADES} trades | trim best {TRIM_PCT:g}% | combos {len(R)} (>= min trades: {int((R.trades >= MIN_TRADES).sum())}) | survivors {int(R.survivor.sum())}")
    print(bs.to_string(index=False))
    cols = ["slot", "exit_rule", "sl", "tp", "trades", "win_pct", "total_pnl", "pf", "pnl_ex_top10", "pf_ex_top10", "top10_share_pct", "pnl_ex_top10_days", "pnl_p1", "pnl_p2", "pnl_p3"]
    print(S[cols].head(40).to_string(index=False))


if __name__ == "__main__": main()
