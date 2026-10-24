"""maxopen_backtest.py - how many trades may be open at the same time?  (BPB SHORT, entry after 12:00 on the FIRST touch, SL 0, TP 60, exit 15:30)

Offline (no API calls): it re-uses the trades of the SLTP backtest (sltp_pm_results/trade_files/BPB_SHORT_T1_FIRST_TOUCH_all_variants_trades.csv), where every
entry is already sized to at most Rs 60,000 and exits at the target (+60 % of premium) or at 15:30.

  python maxopen_backtest.py                  caps 2,3,4 and no cap
  CAPS=1,2,3,5,0 MIN_PRICE=0 python maxopen_backtest.py      (0 = no cap / no minimum price)

RULE (same as the live manager): trades are taken in the order their entry candle comes (same minute -> alphabetical stock name = arbitrary).  A signal is
SKIPPED when `cap` trades are already open at that minute (a trade is open from its entry minute until its exit minute; a slot freed at minute X is usable at minute X).
MIN_PRICE (default 2): options priced at or below it are dropped BEFORE the cap is applied (same as the live planner, which never creates those alerts).
Net = pnl - 1 tick (0.05) each side - Rs 40 per order - 0.1 % STT on the sell value.
Results: maxopen_results/summary.csv, SUMMARY.md, monthly.csv, trades_cap_<n>.csv
"""
import os, sys
import numpy as np, pandas as pd

SRC = os.environ.get("SRC", "sltp_pm_results/trade_files/BPB_SHORT_T1_FIRST_TOUCH_all_variants_trades.csv")
OUT = os.environ.get("OUT", "maxopen_results")
EXIT_RULE, SL, TP = os.environ.get("EXIT", "15:30"), float(os.environ.get("SL", 0)), float(os.environ.get("TP", 60))
CAPS = [int(x) for x in os.environ.get("CAPS", "2,3,4,0").replace(" ", "").split(",") if x != ""]
MIN_PRICE = float(os.environ.get("MIN_PRICE", 2))


def load(src=SRC, exit_rule=EXIT_RULE, sl=SL, tp=TP, min_price=MIN_PRICE):
    d = pd.read_csv(src)
    d = d[(d.exit_rule == exit_rule) & (d.sl == sl) & (d.tp == tp)].copy()
    d["t_in"] = pd.to_datetime(d.entry_date + " " + d.entry_time.astype(str).str[:5])
    d["t_out"] = pd.to_datetime(d.exit_date + " " + d.exit_time.astype(str).str[:5])
    d["qty"] = d.cost / d.entry_price
    d["net"] = d.pnl - 0.05 * 2 * d.qty - 80 - 0.001 * d.exit_price * d.qty
    if min_price > 0: d = d[d.entry_price > min_price]
    return d.sort_values(["t_in", "stock"]).reset_index(drop=True)


def apply_cap(d, cap):
    """cap 0 = no cap.  Returns (taken trades, number skipped, peak open at once)."""
    open_out, taken, peak = [], [], 0                      # exit times of the trades now open
    for r in d.itertuples():
        open_out = [t for t in open_out if t > r.t_in]     # a slot freed at minute X is usable at minute X
        if cap and len(open_out) >= cap: continue
        open_out.append(r.t_out); taken.append(r.Index); peak = max(peak, len(open_out))
    return d.loc[taken], len(d) - len(taken), peak


def peak_capital(t):
    ev = sorted([(a, r.cost) for r in t.itertuples() for a in [r.t_in]] + [(r.t_out, -r.cost) for r in t.itertuples()], key=lambda x: (x[0], x[1]))
    cur = best = 0
    for _, c in ev: cur += c; best = max(best, cur)
    return best


def stats(t, skipped, peak, cap, signals):
    if len(t) == 0: return dict(cap=cap or "none", signals=signals, taken=0, skipped=skipped)
    p = t.pnl.values; day = t.groupby("entry_date").pnl.sum(); eq = np.cumsum(t.sort_values("t_out").pnl.values)
    return dict(cap=cap or "none", signals=signals, taken=len(t), skipped=skipped, peak_open=peak, win_pct=round((p > 0).mean() * 100, 1),
                total_pnl=round(p.sum()), net_pnl=round(t.net.sum()), avg_pnl=round(p.mean()), profit_factor=round(p[p > 0].sum() / max(-p[p < 0].sum(), 1), 2),
                drop_top3=round(np.sort(p)[:-3].sum()) if len(p) > 3 else None, drop_best_day=round(day.sum() - day.max()),
                worst_trade=round(p.min()), worst_day=round(day.min()), max_drawdown=round((np.maximum.accumulate(eq) - eq).max()), peak_capital=round(peak_capital(t)),
                months_profitable=f"{int((t.groupby(t.entry_date.str[:7]).pnl.sum() > 0).sum())}/{t.entry_date.str[:7].nunique()}")


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, monthly = [], {}
    for mp in sorted({MIN_PRICE, 0}, reverse=True):
        d = load(min_price=mp)
        for cap in CAPS:
            t, sk, peak = apply_cap(d, cap)
            s = stats(t, sk, peak, cap, len(d)); s["min_price"] = mp; rows.append(s)
            if mp == MIN_PRICE:
                t.drop(columns=["t_in", "t_out", "qty"]).to_csv(f"{OUT}/trades_cap_{cap or 'none'}.csv", index=False)
                monthly[cap or "none"] = t.groupby(t.entry_date.str[:7]).pnl.sum().round()
    s = pd.DataFrame(rows); s.to_csv(f"{OUT}/summary.csv", index=False)
    pd.DataFrame(monthly).fillna(0).to_csv(f"{OUT}/monthly.csv")
    with open(f"{OUT}/SUMMARY.md", "w") as f:
        f.write(f"# Max open trades - BPB SHORT, first touch after 12:00, SL{SL:g} / TP{TP:g}, exit {EXIT_RULE}, Rs 60,000 max per trade\n\n")
        for mp in sorted({MIN_PRICE, 0}, reverse=True):
            f.write(f"## Options priced above Rs {mp:g}\n\n" if mp else "## No minimum price (for comparison)\n\n"); f.write(s[s.min_price == mp].drop(columns="min_price").to_markdown(index=False) + "\n\n")
        f.write("Monthly pnl (min price applied):\n\n" + pd.DataFrame(monthly).fillna(0).to_markdown() + "\n")
    print(open(f"{OUT}/SUMMARY.md").read())


if __name__ == "__main__":
    main()
