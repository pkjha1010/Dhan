"""robustness_report.py - which variants SURVIVE after the best 10 % of their trades are cut, split by entry-time slot.

  python robustness_report.py <results_folder> [cut=0.10] [min_trades=30]

For every side (LONG / SHORT) found as all_trades_<SIDE>.csv.gz, every entry slot and every one of the 80 variants (time exit x stop-loss x target):
  - the normal result, and the result after removing the top `cut` share of that variant's trades by rupee PnL (the lucky outliers)
  - SURVIVOR = still profitable after the cut (PnL > 0 and profit factor > 1) with at least `min_trades` trades left
Slots (by the entry minute): 09:15 | 09:16 | 09:17-09:29 | 09:30-09:59 | 10:00-11:59 | 12:00+.  (Dhan labels the first candle 09:16 in the data seen so far; 09:15 is then empty.)
Writes robustness_<SIDE>.csv (every slot x variant), survivors_<SIDE>.csv and ROBUSTNESS.md.
"""
import sys, os, math
import numpy as np, pandas as pd

SLOTS = [("09:15", 0, 555), ("09:16", 556, 556), ("09:17-09:29", 557, 569), ("09:30-09:59", 570, 599), ("10:00-11:59", 600, 719), ("12:00+", 720, 10**6)]


def slot_of(m):
    for n, a, b in SLOTS:
        if a <= m <= b: return n
    return "other"


def stats(g, cut=0.0):
    g = g.sort_values("pnl", ascending=False)
    r = g.iloc[math.ceil(len(g) * cut):] if cut else g
    if r.empty: return dict(trades=0, win_pct=0.0, pnl=0.0, roi_pct=0.0, pf=0.0)
    p = r.pnl; w = p[p > 0].sum(); l = -p[p < 0].sum()
    return dict(trades=len(r), win_pct=round((p > 0).mean() * 100, 1), pnl=round(p.sum()), roi_pct=round(p.sum() / r.invested.sum() * 100, 2), pf=round(w / l, 2) if l > 0 else np.inf)


def md(df):
    try: return df.to_markdown(index=False)
    except Exception: return df.to_string(index=False)


def main(folder, cut=0.10, min_trades=30):
    L = [f"# Robustness: top {cut*100:g}% of trades cut, by entry-time slot", "",
         f"A variant SURVIVES if, after removing its best {cut*100:g}% of trades (by rupee PnL), it is still profitable (PnL > 0, profit factor > 1) with at least {min_trades} trades left. "
         "Survivors are not proof of an edge - they only show the result is not carried by a handful of lucky trades. Charges and slippage are not included.", ""]
    keys = ["exit_rule", "sl", "tp"]; found = False
    for side in ("LONG", "SHORT"):
        fp = f"{folder}/all_trades_{side}.csv.gz"
        if not os.path.exists(fp): continue
        found = True; T = pd.read_csv(fp)
        T["m"] = T.entry_time.str[:2].astype(int) * 60 + T.entry_time.str[3:5].astype(int)
        T["slot"] = T.m.map(slot_of)
        rows = []
        for sl_name, g in T.groupby("slot"):
            for k, h in g.groupby(keys):
                a = stats(h); b = stats(h, cut)
                rows.append(dict(slot=sl_name, exit_rule=k[0], sl=k[1], tp=k[2], trades=a["trades"], win_pct=a["win_pct"], pnl=a["pnl"], roi_pct=a["roi_pct"], pf=a["pf"],
                                 trades_cut=b["trades"], win_pct_cut=b["win_pct"], pnl_cut=b["pnl"], roi_pct_cut=b["roi_pct"], pf_cut=b["pf"]))
        R = pd.DataFrame(rows)
        R["sl_rule"] = R.sl.map(lambda v: "no SL" if not v else f"SL {v}%"); R["tp_rule"] = R.tp.map(lambda v: "no TP" if not v else f"TP {v}%")
        R["survivor"] = (R.pnl_cut > 0) & (R.pf_cut > 1) & (R.trades_cut >= min_trades)
        R.to_csv(f"{folder}/robustness_{side}.csv", index=False); S = R[R.survivor].sort_values("roi_pct_cut", ascending=False); S.to_csv(f"{folder}/survivors_{side}.csv", index=False)
        L += [f"## {side}", "", f"Total trades in the file: {len(T)} ({T.groupby(['stock','entry_date']).ngroups} entries)", ""]
        cnt = R.groupby("slot").agg(variants=("survivor", "size"), profitable_before=("pnl", lambda x: int((x > 0).sum())), survivors=("survivor", "sum"), median_trades=("trades", "median")).reset_index()
        L += ["### Variants per entry slot", "", md(cnt), ""]
        cols = ["slot", "exit_rule", "sl_rule", "tp_rule", "trades", "win_pct", "roi_pct", "pf", "trades_cut", "win_pct_cut", "roi_pct_cut", "pf_cut"]
        if S.empty: L += ["### Survivors", "", "None - every variant turns unprofitable (or too thin) once the best trades are cut.", ""]
        else:
            L += [f"### Survivors ({len(S)})", "", md(S.head(40)[cols]), ""]
            best = S.groupby("slot").head(3)[cols]; L += ["### Top 3 survivors per slot", "", md(best), ""]
    if not found: L += ["No all_trades_<SIDE>.csv.gz found in " + folder]
    open(f"{folder}/ROBUSTNESS.md", "w").write("\n".join(L)); print("\n".join(L[:60]))


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 0.10, int(sys.argv[3]) if len(sys.argv) > 3 else 30)
