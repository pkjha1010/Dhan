"""gap_candle_filter.py - the GAP strategy RETESTED with a CORRECTION-CANDLE condition on the gap candle (day i).   python gap_candle_filter.py [n=5]
  Two conditions, tested SEPARATELY (the volume filter is gone):
    red      : the gap candle itself corrects.  LONG (gap up): day i closes BELOW its open (red).  SHORT (gap down): day i closes ABOVE its open (green).
    pullback : the gap comes after a correction.  LONG: the close before the gap C[i-1] < the close n (5) days earlier C[i-1-n] (price fell, then gapped up).  SHORT: C[i-1] > C[i-1-n].
  Nothing is re-fetched from Dhan: a kept trade is exactly the same trade as in gap_results (same entry, option, exits); the condition only removes trades.  Needs Yahoo daily candles
  (yfinance, unadjusted) -> run on GitHub Actions (workflow 'GAP candle filter').
Reads   gap_results/{long,short}/trades_all_variants.csv.gz + entries.csv
Writes  gap_candle_results/{red,pullback}/{long,short}/trades_all_variants.csv.gz, COMPARE.md / compare_{red,pullback}.csv (before vs after), survivors/ for each (premium > Rs 5, ex-top-3 trades / days, periods)
"""
import os, sys, subprocess
import numpy as np, pandas as pd
import gap_rules as R

SRC = "gap_results"; OUT = "gap_candle_results"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
MIN_PRICE = 5.0; MIN_TRADES = 30
VARIANTS = ("red", "pullback")


def load_daily(stocks, start, end):
    """-> {stock: (dates 'YYYY-MM-DD', open, close)} from Yahoo (unadjusted)."""
    import yfinance as yf
    raw = yf.download([s + ".NS" for s in stocks], start=start, end=end, group_by="ticker", auto_adjust=False, progress=False, threads=True)
    out = {}
    for s in stocks:
        try: d = raw[s + ".NS"][["Open", "Close"]].dropna()
        except KeyError: continue
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        out[s] = (d.index.strftime("%Y-%m-%d").values, d["Open"].values.astype(float), d["Close"].values.astype(float))
    return out


def flags(daily, stock, signal_date, direction, n=N):
    """-> dict(red=bool, pullback=bool) for the gap candle of this signal, or None when Yahoo has no such day."""
    if stock not in daily: return None
    dates, O, C = daily[stock]
    i = int(np.searchsorted(dates, signal_date))
    if i >= len(dates) or dates[i] != signal_date: return None
    long = direction == "LONG"
    return dict(red=R.red_gap_candle(O, C, i, long), pullback=R.after_pullback(C, i, long, n))


def add_flags(T, entries, daily, n=N):
    """trades + columns red / pullback (NaN when the gap candle is not in the Yahoo data)."""
    sig = entries[["stock", "date", "signal_date"]].drop_duplicates(["stock", "date"]).rename(columns={"date": "entry_date"})
    T = T.merge(sig, on=["stock", "entry_date"], how="left")
    cache = {}
    for r in T[["stock", "signal_date", "direction"]].drop_duplicates().itertuples():
        cache[(r.stock, r.signal_date, r.direction)] = flags(daily, r.stock, r.signal_date, r.direction, n)
    f = [cache[(a, b, c)] for a, b, c in zip(T.stock, T.signal_date, T.direction)]
    for v in VARIANTS: T[v] = [x[v] if x is not None else np.nan for x in f]
    return T


def stats(g):
    p = g.pnl.values
    if len(p) == 0: return dict(trades=0, win_pct=np.nan, total_pnl=0, pf=np.nan, median_ret_pct=np.nan, pnl_ex_top3=0)
    w = p[p > 0].sum(); l = -p[p < 0].sum()
    return dict(trades=len(p), win_pct=round((p > 0).mean() * 100, 1), total_pnl=round(p.sum()), pf=round(w / l, 2) if l > 0 else np.inf,
                median_ret_pct=round(g.ret_pct.median(), 1), pnl_ex_top3=round(p.sum() - np.sort(p)[-3:].sum()))


def compare(before, after):
    keys = ["direction", "exit_rule", "sl", "tp"]; rows = []
    b = before[before.entry_price > MIN_PRICE]; a = after[after.entry_price > MIN_PRICE]
    for k, g in b.groupby(keys):
        ga = a[(a.direction == k[0]) & (a.exit_rule == k[1]) & (a.sl == k[2]) & (a.tp == k[3])]
        sb, sa = stats(g), stats(ga)
        rows.append({**dict(zip(keys, k)), **{f"before_{x}": v for x, v in sb.items()}, **{f"after_{x}": v for x, v in sa.items()}})
    return pd.DataFrame(rows)


def main():
    both = {d: (pd.read_csv(f"{SRC}/{d}/trades_all_variants.csv.gz"), pd.read_csv(f"{SRC}/{d}/entries.csv")) for d in ("long", "short")}
    stocks = sorted(set(both["long"][0].stock) | set(both["short"][0].stock))
    first = min(e.signal_date.min() for _, e in both.values()); last = max(t.entry_date.max() for t, _ in both.values())
    daily = load_daily(stocks, str((pd.Timestamp(first) - pd.Timedelta(days=30)).date()), str((pd.Timestamp(last) + pd.Timedelta(days=5)).date()))
    print(f"Yahoo daily candles for {len(daily)} of {len(stocks)} stocks", flush=True)
    flagged = {d: add_flags(t, e, daily, N) for d, (t, e) in both.items()}
    L = [f"# GAP with a correction-candle condition on the gap candle (pullback lookback n = {N})", "",
         f"Trades with entry premium > Rs {MIN_PRICE:g} only (the live rule).  Same trades as gap_results, filtered.  red = gap candle closes against its gap (LONG: red, SHORT: green);  pullback = the close before the gap is below (LONG) / above (SHORT) the close {N} days earlier.", ""]
    cols = ["direction", "exit_rule", "sl", "tp", "before_trades", "before_total_pnl", "before_pf", "after_trades", "after_win_pct", "after_total_pnl", "after_pf", "after_median_ret_pct", "after_pnl_ex_top3"]
    for v in VARIANTS:
        bs, as_ = [], []
        for d in ("long", "short"):
            F = flagged[d]; A = F[F[v] == True].drop(columns=list(VARIANTS)).copy()
            os.makedirs(f"{OUT}/{v}/{d}", exist_ok=True); A.to_csv(f"{OUT}/{v}/{d}/trades_all_variants.csv.gz", index=False)
            bs.append(F); as_.append(A)
            sigs = F.drop_duplicates(["stock", "signal_date"]); k = len(sigs)
            L.append(f"- **{v}** {d.upper()}: {int((sigs[v] == True).sum())} of {k} gap signals pass, {int(sigs[v].isna().sum())} not judgeable (gap candle missing in Yahoo data) are dropped")
        C = compare(pd.concat(bs), pd.concat(as_)); C.to_csv(f"{OUT}/compare_{v}.csv", index=False)
        sel = C[(C.before_trades >= MIN_TRADES) | (C.after_trades >= 10)]
        for dd in ("LONG", "SHORT"):
            s = sel[sel.direction == dd].sort_values("after_total_pnl", ascending=False)
            L += ["", f"## {v.upper()} - {dd}: top 20 variants after the filter (by total PnL)", "", s[cols].head(20).to_markdown(index=False)]
        subprocess.run([sys.executable, "gap_survivors.py", str(MIN_PRICE), "20"], env=dict(os.environ, GAP_SURV_DIR=f"{OUT}/{v}"), check=False)
    open(f"{OUT}/COMPARE.md", "w").write("\n".join(L)); print("\n".join(L))


if __name__ == "__main__": main()
