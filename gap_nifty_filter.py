"""gap_nifty_filter.py - the GAP strategy RETESTED with a NIFTY50 day-direction filter.

  python gap_nifty_filter.py check     test Dhan access (downloads one week of NIFTY50 1-minute candles)
  python gap_nifty_filter.py run       fetch NIFTY50 1-minute candles (cached, resumable) and filter every GAP trade        (default)
  python gap_nifty_filter.py filter    filter only, from the cached NIFTY candles (no Dhan call)

  LONG  trade kept only when NIFTY50 price (at the entry minute) > NIFTY50 open of the same day.
  SHORT trade kept only when NIFTY50 price (at the entry minute) < NIFTY50 open of the same day.     (rules in gap_nifty_rules.py)
  Nothing is re-fetched for the options: a kept trade is exactly the same trade as in gap_results (same entry, option, exits, SL / TP); the filter only removes trades.
  Trades on a day without NIFTY candles are dropped and counted.

Reads   gap_results/{long,short}/trades_all_variants.csv.gz
Needs   DHAN_CLIENT_ID / DHAN_ACCESS_TOKEN (only to download NIFTY50 candles; NIFTY50 = security id 13, segment IDX_I)
Writes  gap_nifty_results/nifty_1min.csv.gz (cache), {long,short}/trades_all_variants.csv.gz (kept trades, + nifty_open / nifty_price), COMPARE.md / compare.csv (before vs after),
        survivors/ (premium > Rs 5, top-10 % trimmed, months), per-day filter table nifty_days.csv
"""
import os, sys, subprocess
import numpy as np, pandas as pd
import gap_nifty_rules as NR

SRC = os.environ.get("GN_SRC") or "gap_results"
OUT = os.environ.get("GN_OUT") or "gap_nifty_results"
START = os.environ.get("GN_START") or "2023-10-30"
END = os.environ.get("GN_END") or "2026-10-30"
NIFTY_ID = os.environ.get("GN_NIFTY_ID") or "13"
CACHE = f"{OUT}/nifty_1min.csv.gz"
MIN_PRICE = 5.0; MIN_TRADES = 30
WINDOW_DAYS = 60                                     # Dhan allows <= 90 days of 1-minute candles per request


def fetch_nifty(dh, d0, d1):
    """1-minute NIFTY50 candles d0 .. d1 (dates), one request."""
    import bpb_fno_backtest as B
    j = dh.post("/charts/intraday", {"securityId": str(NIFTY_ID), "exchangeSegment": "IDX_I", "instrument": "INDEX", "interval": "1",
                                     "oi": False, "fromDate": f"{d0} 09:15:00", "toDate": f"{d1} 15:30:00"})
    if j is None: return None
    fr = B.frame(j.get("data", j) if isinstance(j.get("data", None), dict) else j)
    if fr is None:
        print(f"[NIFTY {d0}..{d1}] Dhan answered but sent no candles: {str(j)[:300]}", flush=True)
        return pd.DataFrame(columns=["o", "h", "l", "c"], index=pd.DatetimeIndex([]))
    return fr


def load_cache():
    if not os.path.exists(CACHE): return pd.DataFrame(columns=["o", "h", "l", "c"], index=pd.DatetimeIndex([]))
    d = pd.read_csv(CACHE, parse_dates=["t"]).set_index("t"); return d[["o", "h", "l", "c"]].sort_index()


def save_cache(df):
    os.makedirs(OUT, exist_ok=True); df = df[~df.index.duplicated(keep="last")].sort_index(); df.index.name = "t"; df.to_csv(CACHE)


def download(d0, d1):
    """Fill the cache for d0 .. d1 in windows; windows that are already in the cache (a candle on its first / last weekday) are skipped, so a re-run costs nothing."""
    import bpb_fno_backtest as B
    have = load_cache(); dh = B.Dhan(); frames = [have]
    a = pd.Timestamp(d0)
    while a <= pd.Timestamp(d1):
        b = min(a + pd.Timedelta(days=WINDOW_DAYS - 1), pd.Timestamp(d1))
        days = pd.bdate_range(a, b)
        got = set(have.index.strftime("%Y-%m-%d")) if len(have) else set()
        need = [x for x in days.strftime("%Y-%m-%d") if x not in got]
        if len(need) > 0.1 * len(days) + 12:                  # more than the usual number of holidays missing -> fetch the window
            fr = fetch_nifty(dh, a.date(), b.date())
            if fr is None: raise SystemExit(f"Dhan refused the NIFTY request {a.date()}..{b.date()} - see the 'Dhan says' line above")
            print(f"NIFTY {a.date()}..{b.date()}: {len(fr)} candles", flush=True); frames.append(fr)
            save_cache(pd.concat(frames))
        a = b + pd.Timedelta(days=1)
    out = pd.concat(frames); out = out[~out.index.duplicated(keep="last")].sort_index(); save_cache(out); return out


def stats(g):
    p = g.pnl.values
    if len(p) == 0: return dict(trades=0, win_pct=np.nan, total_pnl=0, pf=np.nan, median_ret_pct=np.nan, pnl_ex_top3=0)
    w = p[p > 0].sum(); l = -p[p < 0].sum()
    return dict(trades=len(p), win_pct=round((p > 0).mean() * 100, 1), total_pnl=round(p.sum()), pf=round(w / l, 2) if l > 0 else np.inf,
                median_ret_pct=round(g.ret_pct.median(), 1), pnl_ex_top3=round(p.sum() - np.sort(p)[-3:].sum()))


def compare(before, after):
    keys = ["direction", "exit_rule", "sl", "tp"]; rows = []
    b = before[before.entry_price > MIN_PRICE]; a = after[after.entry_price > MIN_PRICE]
    ga_ = {k: g for k, g in a.groupby(keys)}
    for k, g in b.groupby(keys):
        ga = ga_.get(k, a.iloc[0:0])
        sb, sa = stats(g), stats(ga)
        rows.append({**dict(zip(keys, k)), **{f"before_{x}": v for x, v in sb.items()}, **{f"after_{x}": v for x, v in sa.items()}})
    return pd.DataFrame(rows)


def filter_all(nifty):
    tables = NR.day_tables(nifty)
    print(f"NIFTY candles for {len(tables)} days", flush=True)
    os.makedirs(OUT, exist_ok=True)
    L = ["# GAP with a NIFTY50 day-direction filter", "",
         f"Trades with entry premium > Rs {MIN_PRICE:g} only (the live rule).  Same trades as {SRC}, filtered: **LONG only when NIFTY50 price at the entry minute > NIFTY50 open of the day; SHORT only when it is < the open.**", ""]
    bs, as_ = [], []; days = []
    for d in ("long", "short"):
        T = pd.read_csv(f"{SRC}/{d}/trades_all_variants.csv.gz")
        F = NR.add_nifty_flag(T, tables)
        A = F[F.nifty_ok == True].drop(columns=["nifty_ok"]).copy()
        os.makedirs(f"{OUT}/{d}", exist_ok=True); A.to_csv(f"{OUT}/{d}/trades_all_variants.csv.gz", index=False)
        bs.append(F.drop(columns=["nifty_ok"])); as_.append(A)
        ent = F.drop_duplicates(["stock", "entry_date", "entry_time"]); n = len(ent)
        L.append(f"- {d.upper()}: {int((ent.nifty_ok == True).sum())} of {n} entries pass the NIFTY filter, {int((ent.nifty_ok == False).sum())} are removed, {int(ent.nifty_ok.isna().sum())} not judgeable (no NIFTY candle) are dropped")
        e = ent.assign(direction=d.upper())[["entry_date", "direction", "nifty_ok"]]; days.append(e)
    pd.concat(days).groupby(["entry_date", "direction"]).nifty_ok.agg(entries="size", pass_n=lambda s: int((s == True).sum())).reset_index().to_csv(f"{OUT}/nifty_days.csv", index=False)
    C = compare(pd.concat(bs), pd.concat(as_)); C.to_csv(f"{OUT}/compare.csv", index=False)
    cols = ["direction", "exit_rule", "sl", "tp", "before_trades", "before_total_pnl", "before_pf", "after_trades", "after_win_pct", "after_total_pnl", "after_pf", "after_median_ret_pct", "after_pnl_ex_top3"]
    sel = C[(C.before_trades >= MIN_TRADES) | (C.after_trades >= 10)]
    for dd in ("LONG", "SHORT"):
        s = sel[sel.direction == dd].sort_values("after_total_pnl", ascending=False)
        L += ["", f"## {dd}: top 20 variants after the NIFTY filter (by total PnL)", "", s[cols].head(20).to_markdown(index=False)]
    open(f"{OUT}/COMPARE.md", "w").write("\n".join(L)); print("\n".join(L))
    subprocess.run([sys.executable, "gap_survivors.py", str(MIN_PRICE), "20"], env=dict(os.environ, GAP_SURV_DIR=OUT), check=False)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "check":
        import bpb_fno_backtest as B
        fr = fetch_nifty(B.Dhan(), pd.Timestamp(END).date() - pd.Timedelta(days=9), pd.Timestamp(END).date())
        print("NIFTY50 candles:", 0 if fr is None else len(fr)); print(fr.head() if fr is not None else "no data"); return
    nifty = download(START, END) if mode == "run" else load_cache()
    if len(nifty) == 0: raise SystemExit(f"no NIFTY candles in {CACHE} - run 'python gap_nifty_filter.py run' first")
    filter_all(nifty)


if __name__ == "__main__": main()
