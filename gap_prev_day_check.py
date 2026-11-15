"""gap_prev_day_check.py - for every entry that OPENS beyond the entry level (gap-up through the breakout high for LONG, gap-down through the breakdown low for SHORT): where was the stock in the LAST HALF HOUR
(15:00 - 15:29) of the previous trading day, relative to the breakout high (the entry level), the previous day's close and the breakout day's close?   Dhan 1-minute stock candles, a handful of calls.

  python gap_prev_day_check.py           reads bpb_bb_results/{long,short}/entries.csv, writes gap_prev_day_results/results.csv + SUMMARY.md

For every gap entry (stock, direction, entry day, level = High of the breakout day B (SHORT: Low), B's date):
  prev_close                 close of the previous trading day (last 1-minute candle)
  last30_avg / low / high    the average of the 1-minute closes 15:00-15:29 of the previous day, and their low / high
  prev_close_beyond_level    the previous day ALREADY closed beyond the level (LONG above it, SHORT below it) = the 'gap' is not a new gap, the stock was already through the level
  last30_between_level_and_prev_close      the last-half-hour average lies between the level and the previous close (your question)
  last30_between_level_and_breakout_close  the same against the breakout day's close
  open_vs_prev_close_pct     entry-minute price vs the previous close, in the trade direction (a true gap from yesterday's close when clearly > 0)
Settings (env):  GPD_SRC (bpb_bb_results)  GPD_OUT (gap_prev_day_results)  GPD_RULE (from_b3 = your script; from_b2 / from_b1)  GPD_MIN_GAP (0.5 = entry-minute price at least 0.5 % beyond the level)
"""
import os, sys
from datetime import date, timedelta
import numpy as np, pandas as pd

SRC = os.environ.get("GPD_SRC") or "bpb_bb_results"
OUT = os.environ.get("GPD_OUT") or "gap_prev_day_results"
RULE = os.environ.get("GPD_RULE") or "from_b3"
MIN_GAP = float(os.environ.get("GPD_MIN_GAP") or 0.5)
LAST30_FROM = 15 * 60


def between(x, a, b):
    return bool(np.isfinite(x) and np.isfinite(a) and np.isfinite(b) and min(a, b) <= x <= max(a, b))


def analyse(u, entry_date, breakout_date, level, long, entry_px):
    """u = 1-minute stock candles (index = candle start, columns o h l c) from the breakout day to the day before the entry.  -> dict or None."""
    if u is None or len(u) == 0: return None
    days = {k: v for k, v in u.groupby(u.index.strftime("%Y-%m-%d"))}
    prev = [k for k in sorted(days) if k < entry_date]
    if not prev: return None
    p = days[prev[-1]]
    l30 = p[(p.index.hour * 60 + p.index.minute) >= LAST30_FROM]
    if l30.empty: return None
    sg = 1.0 if long else -1.0
    prev_close = float(p.c.iloc[-1]); avg = float(l30.c.mean())
    b = days.get(breakout_date); b_close = float(b.c.iloc[-1]) if b is not None and len(b) else float("nan")
    return dict(prev_day=prev[-1], prev_close=round(prev_close, 2), last30_avg=round(avg, 2), last30_low=round(float(l30.l.min()), 2), last30_high=round(float(l30.h.max()), 2),
                breakout_close=round(b_close, 2) if b_close == b_close else np.nan,
                prev_close_beyond_level=bool(sg * (prev_close - level) > 0),
                last30_between_level_and_prev_close=between(avg, level, prev_close),
                last30_between_level_and_breakout_close=between(avg, level, b_close),
                open_vs_prev_close_pct=round((entry_px / prev_close - 1) * 100 * sg, 2), last30_vs_level_pct=round((avg / level - 1) * 100 * sg, 2), prev_close_vs_level_pct=round((prev_close / level - 1) * 100 * sg, 2))


def gap_entries():
    rows = []
    for d in ("long", "short"):
        p = f"{SRC}/{d}/entries.csv"
        if os.path.exists(p): rows.append(pd.read_csv(p))
    if not rows: raise SystemExit(f"no {SRC}/long|short/entries.csv - run the backtest first")
    E = pd.concat(rows, ignore_index=True)
    E = E[(E[RULE] == 1) & E.entry_minute.isin(["09:15", "09:16"])].copy()
    sg = np.where(E.direction == "LONG", 1.0, -1.0)
    E["beyond_pct"] = (E.stock_price / E.ref - 1) * 100 * sg
    return E[E.beyond_pct >= MIN_GAP].reset_index(drop=True)


def summary_md(R):
    L = ["# Gap entries: where was the stock in the last half hour of the previous day?", "",
         f"Entries that OPEN beyond the entry level (entry-minute price at least {MIN_GAP} % beyond it), rule `{RULE}`. Level = High of the breakout day B (SHORT: Low). Last half hour = 1-minute closes 15:00-15:29 of the previous trading day.", ""]
    for d in ("LONG", "SHORT", "ALL"):
        g = R if d == "ALL" else R[R.direction == d]
        if g.empty: continue
        n = len(g)
        L += [f"## {d}: {n} gap entries", "",
              f"- previous day ALREADY closed beyond the level: **{int(g.prev_close_beyond_level.sum())}** of {n}",
              f"- last-half-hour average between the level and the previous close: **{int(g.last30_between_level_and_prev_close.sum())}** of {n}",
              f"- last-half-hour average between the level and the breakout day's close: **{int(g.last30_between_level_and_breakout_close.sum())}** of {n}",
              f"- open vs previous close (trade direction), median: {g.open_vs_prev_close_pct.median():.2f} %; a real gap from yesterday's close (> 0.5 %): {int((g.open_vs_prev_close_pct > 0.5).sum())} of {n}", ""]
    cols = ["stock", "direction", "date", "b_label", "ref", "prev_close", "last30_avg", "prev_close_beyond_level", "last30_between_level_and_prev_close", "last30_between_level_and_breakout_close", "open_vs_prev_close_pct"]
    L += ["## Every entry", "", R[[c for c in cols if c in R.columns]].to_markdown(index=False) if hasattr(R, "to_markdown") else R.to_string(index=False), ""]
    return "\n".join(L)


def main():
    os.environ.setdefault("A8_OUT", OUT)
    import all8_backtest as A
    B = A.B
    G = gap_entries()
    print(f"{len(G)} gap entries (rule {RULE}, at least {MIN_GAP} % beyond the level)", flush=True)
    dh = A.Dhan(); mst = A.load_master(); rows = []
    for r in G.itertuples():
        if r.stock not in mst: print(f"{r.stock}: not in the Dhan list", flush=True); continue
        d1 = date.fromisoformat(r.date) - timedelta(days=1)
        u = B.eq_minute(dh, mst[r.stock][0], r.breakout_date, str(d1))
        a = analyse(u, r.date, r.breakout_date, float(r.ref), r.direction == "LONG", float(r.stock_price))
        if a is None: print(f"{r.stock} {r.date}: no previous-day candles", flush=True); continue
        rows.append({**dict(stock=r.stock, direction=r.direction, date=r.date, b_label=r.b_label, breakout_date=r.breakout_date, ref=r.ref, entry_price_stock=r.stock_price), **a})
    os.makedirs(OUT, exist_ok=True)
    R = pd.DataFrame(rows); R.to_csv(f"{OUT}/results.csv", index=False)
    if len(R):
        open(f"{OUT}/SUMMARY.md", "w").write(summary_md(R)); print(summary_md(R)[:4000])


if __name__ == "__main__": main()
