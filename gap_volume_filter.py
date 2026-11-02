"""gap_volume_filter.py - the GAP strategy RETESTED with a VOLUME FILTER on the gap candle.   python gap_volume_filter.py [mult=2] [n=10]

  GAP candle = day i, the daily candle that gapped (> 1 % above / below the previous close) and started the setup (signal_date in the trades files).
  FILTER     = volume of day i >= mult (2) x the average volume of the n (10) daily candles BEFORE day i.   Only trades whose gap candle passes are kept.
  Nothing is re-fetched from Dhan: a filtered trade is exactly the same trade as in gap_results (same entry, option, exits), the filter only removes some of them.
  Needs Yahoo daily volumes (yfinance, unadjusted - the same source as the candidate step), so run it on GitHub Actions (workflow 'GAP volume filter').

Reads   gap_results/{long,short}/trades_all_variants.csv.gz and entries.csv
Writes  gap_vol_results/{long,short}/trades_all_variants.csv.gz (+ column vol_ratio), COMPARE.md / compare.csv (before vs after for every variant with enough trades),
        gap_vol_results/survivors/ (the same survivor scoring as gap_survivors.py: premium > Rs 5, ex-top-3 trades, ex-top-3 days, periods, median)
"""
import os, sys, subprocess
import numpy as np, pandas as pd
import gap_rules as R

SRC = "gap_results"; OUT = "gap_vol_results"
MULT = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
N = int(sys.argv[2]) if len(sys.argv) > 2 else 10
MIN_PRICE = 5.0; MIN_TRADES = 30


def load_volumes(stocks, start, end):
    """-> {stock: (dates 'YYYY-MM-DD' array, volume array)} from Yahoo (unadjusted)."""
    import yfinance as yf
    raw = yf.download([s + ".NS" for s in stocks], start=start, end=end, group_by="ticker", auto_adjust=False, progress=False, threads=True)
    out = {}
    for s in stocks:
        try: d = raw[s + ".NS"][["Volume"]].dropna()
        except KeyError: continue
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        out[s] = (d.index.strftime("%Y-%m-%d").values, d["Volume"].values.astype(float))
    return out


def signal_ratio(vols, stock, signal_date, n=N):
    """volume of the gap candle / average volume of the n candles before it (None = cannot judge)."""
    if stock not in vols: return None
    dates, V = vols[stock]
    i = int(np.searchsorted(dates, signal_date))
    if i >= len(dates) or dates[i] != signal_date or i < n: return None
    avg = float(np.mean(V[i - n:i]))
    return float(V[i]) / avg if avg > 0 else None


def filter_trades(T, entries, vols, mult=MULT, n=N):
    """T = trades (stock, entry_date, ...), entries = entries.csv (stock, date, signal_date).  -> (trades that pass, with column vol_ratio ; number of signals judged / passed / unjudgeable)."""
    sig = entries[["stock", "date", "signal_date"]].drop_duplicates(["stock", "date"]).rename(columns={"date": "entry_date"})
    T = T.merge(sig, on=["stock", "entry_date"], how="left")
    keys = T[["stock", "signal_date"]].drop_duplicates()
    ratio = {(r.stock, r.signal_date): signal_ratio(vols, r.stock, r.signal_date, n) for r in keys.itertuples()}
    T["vol_ratio"] = [ratio[(a, b)] for a, b in zip(T.stock, T.signal_date)]
    ok = T.vol_ratio.notna() & (T.vol_ratio >= mult) if mult > 0 else pd.Series(True, index=T.index)
    return T[ok].copy(), dict(signals=len(ratio), passed=sum(1 for v in ratio.values() if v is not None and (mult <= 0 or v >= mult)), unjudged=sum(1 for v in ratio.values() if v is None))


def stats(g):
    p = g.pnl.values
    if len(p) == 0: return dict(trades=0, win_pct=np.nan, total_pnl=0, pf=np.nan, median_ret_pct=np.nan, pnl_ex_top3=0)
    w = p[p > 0].sum(); l = -p[p < 0].sum()
    return dict(trades=len(p), win_pct=round((p > 0).mean() * 100, 1), total_pnl=round(p.sum()), pf=round(w / l, 2) if l > 0 else np.inf,
                median_ret_pct=round(g.ret_pct.median(), 1), pnl_ex_top3=round(p.sum() - np.sort(p)[-3:].sum()))


def compare(before, after):
    """one row per direction x entry slot-free variant (exit, sl, tp) on trades with premium > MIN_PRICE: before vs after the filter."""
    keys = ["direction", "exit_rule", "sl", "tp"]
    rows = []
    b = before[before.entry_price > MIN_PRICE]; a = after[after.entry_price > MIN_PRICE]
    for k, g in b.groupby(keys):
        ga = a[(a.direction == k[0]) & (a.exit_rule == k[1]) & (a.sl == k[2]) & (a.tp == k[3])]
        sb, sa = stats(g), stats(ga)
        rows.append({**dict(zip(keys, k)), **{f"before_{x}": v for x, v in sb.items()}, **{f"after_{x}": v for x, v in sa.items()}})
    return pd.DataFrame(rows)


def main():
    both = {}
    for d in ("long", "short"):
        both[d] = (pd.read_csv(f"{SRC}/{d}/trades_all_variants.csv.gz"), pd.read_csv(f"{SRC}/{d}/entries.csv"))
    stocks = sorted(set(both["long"][0].stock) | set(both["short"][0].stock))
    first = min(min(t.entry_date.min(), e.signal_date.min()) for t, e in both.values())
    start = str((pd.Timestamp(first) - pd.Timedelta(days=45)).date()); end = str((pd.Timestamp(max(t.entry_date.max() for t, _ in both.values())) + pd.Timedelta(days=5)).date())
    vols = load_volumes(stocks, start, end)
    print(f"Yahoo volumes for {len(vols)} of {len(stocks)} stocks ({start} .. {end}); filter: gap candle volume >= {MULT:g} x average of the previous {N} daily candles", flush=True)
    all_b, all_a, info = [], [], []
    for d in ("long", "short"):
        T, E = both[d]
        A, inf = filter_trades(T, E, vols, MULT, N)
        os.makedirs(f"{OUT}/{d}", exist_ok=True)
        A.to_csv(f"{OUT}/{d}/trades_all_variants.csv.gz", index=False)
        all_b.append(T); all_a.append(A)
        info.append(f"- {d.upper()}: {inf['signals']} gap signals with a trade, {inf['passed']} pass the volume filter, {inf['unjudged']} could not be judged (no Yahoo volume / fewer than {N} earlier candles) and are dropped")
    C = compare(pd.concat(all_b), pd.concat(all_a)); C.to_csv(f"{OUT}/compare.csv", index=False)
    sel = C[(C.before_trades >= MIN_TRADES) | (C.after_trades >= 10)]
    cols = ["direction", "exit_rule", "sl", "tp", "before_trades", "before_total_pnl", "before_pf", "after_trades", "after_win_pct", "after_total_pnl", "after_pf", "after_median_ret_pct", "after_pnl_ex_top3"]
    L = [f"# GAP with volume filter: gap candle volume >= {MULT:g} x average of the previous {N} daily candles", "", *info, "",
         f"Trades with entry premium > Rs {MIN_PRICE:g} only (the live rule).  Same trades as gap_results, filtered.", ""]
    for dd in ("LONG", "SHORT"):
        s = sel[sel.direction == dd].sort_values("after_total_pnl", ascending=False)
        L += [f"## {dd} - top 20 variants after the filter (by total PnL)", "", s[cols].head(20).to_markdown(index=False), ""]
    open(f"{OUT}/COMPARE.md", "w").write("\n".join(L)); print("\n".join(L))
    env = dict(os.environ, GAP_SURV_DIR=OUT)
    subprocess.run([sys.executable, "gap_survivors.py", str(MIN_PRICE), "20"], env=env, check=False)   # min 20 trades: the filter leaves fewer trades


if __name__ == "__main__": main()
