"""top10_all_backtest.py - ONE runner: every strategy of this repo on the TOP 10 stocks, 1 year, ONE common exit grid.  Dhan 1-minute option data (ATM call / put, ITM-1..3 fallback where the strategy has it).

  python top10_all_backtest.py rules              offline: print the settings every strategy will get (no Dhan, no Yahoo)
  python top10_all_backtest.py check              test Dhan access through every strategy
  python top10_all_backtest.py run                run every strategy one after the other (each one is resumable - run again until nothing says PARTIAL)
  python top10_all_backtest.py summary            rebuild each strategy's result files from the saved data (no API calls)
  python top10_all_backtest.py compare            combine all results -> top10_results/COMPARE.md, ALL_VARIANTS.csv, BEST_PER_STRATEGY.csv (no API calls; run / summary do it at the end)
  options: --only gap,orb,...     (names: opendrop gap bpb_base accum5 accum10 orb all8 pullback)      or env T10_ONLY

THE SAME SETTINGS FOR EVERY STRATEGY (environment variables, defaults in brackets)
  T10_SYMBOLS  [HDFCBANK RELIANCE ICICIBANK INFY BHARTIARTL ITC LT TCS AXISBANK SBIN]     the 10 heaviest NIFTY50 stocks (same list as orb_backtest.py)
  T10_START / T10_END  [2025-11-13 / 2026-11-12]   entry dates (1 year)
  T10_SLS  [0,20,40,60]    stop-loss % of the option premium (0 = none)
  T10_TPS  [0,40,60,80,120]  target % of the premium (0 = none)
  T10_EXITS  [09:30,10:00,12:00,15:00,15:30]   time exit, the same day
  T10_MIN_TRADES [10]  a variant needs this many trades to appear in the 'best' tables (10 stocks x 1 year = few trades)
  T10_OUT [top10_results]   T10_BUDGET_MIN [330]  total minutes; each strategy stops politely when its share is used (progress is saved)
Everything else is each strategy's own rule (setup, entry, ATM -> ITM fallback, Rs 60,000 per trade cap, no charges).  Results: top10_results/<strategy>/ (that strategy's usual files).
ALL8 = the 4 wick-shape strategies + 1H / 4H trendline + BPB breakout + SHAPECMP re-cross (all8_backtest.py rules) with the time exits above only (no UNTIL_HIT).
Not in this repo, so not included: the green-engulfing, WRU and live Zerodha strategies.
"""
import os, sys, time, glob, subprocess, json
import numpy as np, pandas as pd

TOP10 = "HDFCBANK RELIANCE ICICIBANK INFY BHARTIARTL ITC LT TCS AXISBANK SBIN"


def env(name, default): return os.environ.get(name) or default


SYMBOLS = " ".join(env("T10_SYMBOLS", TOP10).replace(",", " ").split())
START, END = env("T10_START", "2025-11-13"), env("T10_END", "2026-11-12")
SLS, TPS, EXITS = env("T10_SLS", "0,20,40,60"), env("T10_TPS", "0,40,60,80,120"), env("T10_EXITS", "09:30,10:00,12:00,15:00,15:30")
MIN_TRADES = env("T10_MIN_TRADES", "10")
OUT = env("T10_OUT", "top10_results")
BUDGET_MIN = float(env("T10_BUDGET_MIN", "330"))
CSV = lambda s: ",".join(s.replace(" ", ",").split(","))


def _common(prefix, **extra):
    """START / END / SYMBOLS / SLS / TPS / EXITS / MIN_TRADES in the <prefix>_ naming of one strategy."""
    e = {f"{prefix}_START": START, f"{prefix}_END": END, f"{prefix}_SYMBOLS": SYMBOLS, f"{prefix}_SLS": SLS, f"{prefix}_TPS": TPS, f"{prefix}_MIN_TRADES": MIN_TRADES}
    if prefix != "A8": e[f"{prefix}_EXITS"] = EXITS
    e.update(extra)
    return e


# name -> (script, label, env builder(out_dir), modes the script understands)
def _strategies():
    S = {}
    S["opendrop"] = ("opendrop_backtest.py", "OPENDROP (first-hour drop retest, LONG call, Nifty slope filter)", lambda o: _common("OD", OD_OUT=o), ("check", "run", "summary", "rules"))
    S["gap"] = ("gap_backtest.py", "GAP (gap-fade reversal, LONG call + SHORT put)", lambda o: _common("GP", GP_OUT=o), ("check", "run", "summary", "rules"))
    S["bpb_base"] = ("bpb_base_backtest.py", "BPB BASE (10-day breakout + pullback, LONG call + SHORT put)", lambda o: _common("BB", BB_OUT=o), ("check", "run", "summary", "rules"))
    S["accum5"] = ("accum5_backtest.py", "ACC5 (5-day accumulation fake-break)", lambda o: _common("AC", AC_OUT=o), ("check", "run", "summary", "rules"))
    S["accum10"] = ("accum10_backtest.py", "ACC10 (10-day accumulation fake-break)", lambda o: _common("AC", AC_OUT=o), ("check", "run", "summary", "rules"))
    S["orb"] = ("orb_backtest.py", "ORB (opening range breakout, LONG call + SHORT put)",
                lambda o: {"ORB_SYMBOLS": SYMBOLS, "ORB_START": START, "ORB_END": END, "ORB_SLS": ",".join("none" if x == "0" else x for x in SLS.split(",")), "ORB_TPS": TPS,
                           "ORB_EXITS": EXITS, "ORB_NO_COMBINE": "1", "ORB_MIN_TRADES": MIN_TRADES, "ORB_OUT": o, "ORB_TRADES_ALL": "1"}, ("check", "run", "summary", "rules"))
    S["all8"] = ("top10_all8_run.py", "ALL8 (4 wick shapes + 1H/4H trendline + BPB + SHAPECMP re-cross)",
                 lambda o: _common("A8", A8_OUT=o, A8_TRADES_ALL="1", T10_EXITS=EXITS), ("check", "run", "summary"))
    S["pullback"] = ("pullback_options_backtest.py", "PULLBACK options (10-day breakout -> pullback -> re-cross, Nifty intraday filter)",
                     lambda o: _common("PO", PO_OUT=o), ("check", "run"))
    return S


STRATS = _strategies()
ORDER = ["opendrop", "gap", "bpb_base", "accum5", "accum10", "orb", "all8", "pullback"]


def selected(argv):
    only = env("T10_ONLY", "")
    if "--only" in argv: only = argv[argv.index("--only") + 1]
    names = [x.strip().lower() for x in only.replace(" ", ",").split(",") if x.strip()] or list(ORDER)
    bad = [n for n in names if n not in STRATS]
    if bad: sys.exit(f"unknown strategy {bad}; choose from {ORDER}")
    return [n for n in ORDER if n in names]


def child_env(name, remaining_min):
    script, label, build, modes = STRATS[name]
    e = dict(os.environ); e.update(build(f"{OUT}/{name}"))
    e["BUDGET_MIN"] = str(max(3.0, remaining_min)); e["PO_BUDGET_MIN"] = str(max(3.0, remaining_min))
    return e


def run_one(name, mode, remaining_min):
    script, label, build, modes = STRATS[name]
    if mode not in modes:
        print(f"[{name}] has no '{mode}' mode - skipped", flush=True); return 0
    print(f"\n{'=' * 100}\n[{name}] {label}  -  python {script} {mode}\n{'=' * 100}", flush=True)
    r = subprocess.run([sys.executable, script, mode], env=child_env(name, remaining_min))
    if r.returncode != 0: print(f"[{name}] exited with code {r.returncode} (see the lines above) - the other strategies continue", flush=True)
    return r.returncode


def progress_of(name):
    p = f"{OUT}/{name}/PROGRESS.txt"
    return open(p).read().strip().splitlines()[0] if os.path.exists(p) else ("(no PROGRESS.txt)" if os.path.isdir(f"{OUT}/{name}") else "not run yet")


# ---------------------------------------------------------------- compare
KEEP = ["strategy", "exit_rule", "sl", "tp", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "max_drawdown"]


def load_summaries():
    rows = []
    for name in ORDER:
        d = f"{OUT}/{name}"
        files = sorted(set(glob.glob(f"{d}/summary.csv") + glob.glob(f"{d}/*/summary.csv") + glob.glob(f"{d}/summary_*.csv")))
        # ORB writes OUT/summary.csv (both sides) AND long|short/summary.csv; keep the folder files only when both exist (same rows)
        if f"{d}/summary.csv" in files and any(f.startswith(f"{d}/long") or f.startswith(f"{d}/short") for f in files) and name == "orb":
            files = [f for f in files if f != f"{d}/summary.csv"]
        for f in files:
            try: S = pd.read_csv(f)
            except Exception: continue
            if S.empty or "exit_rule" not in S.columns: continue
            if "strategy" not in S.columns:
                side = "LONG" if "LONG" in os.path.basename(f).upper() else "SHORT" if "SHORT" in os.path.basename(f).upper() else ""
                S["strategy"] = f"PULLBACK_{side}".rstrip("_")
            if name == "pullback":                                            # this file stores sl / tp as fractions (0.2 = 20 %)
                for c in ("sl", "tp"):
                    if c in S.columns: S[c] = (S[c].astype(float) * 100).round().astype(int)
            S = S[[c for c in KEEP if c in S.columns]].copy()
            S.insert(0, "module", name); S["file"] = f
            rows.append(S)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def lab_sl(v): return "no SL" if str(v) in ("0", "0.0", "none", "nan") else (f"SL {v}" if not str(v).replace('.', '').isdigit() else f"SL {int(float(v))}%")
def lab_tp(v): return "no TP" if str(v) in ("0", "0.0", "none", "nan") else f"TP {int(float(v))}%"


def md(df):
    try: return df.to_markdown(index=False)
    except Exception: return df.to_string(index=False)


def compare():
    A = load_summaries()
    if A.empty: print("compare: no summary files found under", OUT); return
    A["sl_rule"] = A.sl.map(lab_sl); A["tp_rule"] = A.tp.map(lab_tp)
    os.makedirs(OUT, exist_ok=True)
    A.drop(columns=["file"]).to_csv(f"{OUT}/ALL_VARIANTS.csv", index=False)
    mt = int(MIN_TRADES)
    good = A[A.trades >= mt]
    cols = ["strategy", "exit_rule", "sl_rule", "tp_rule", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "max_drawdown"]
    cols = [c for c in cols if c in A.columns]
    best = good.sort_values("total_pnl", ascending=False).groupby("strategy").head(1).sort_values("total_pnl", ascending=False)
    bestr = good.sort_values("roi_pct", ascending=False).groupby("strategy").head(1).sort_values("roi_pct", ascending=False)
    best[cols].to_csv(f"{OUT}/BEST_PER_STRATEGY.csv", index=False)
    L = [f"# TOP 10 stocks - every strategy, one grid", "",
         f"**Stocks:** {SYMBOLS}", f"**Entry dates:** {START} to {END}  |  **Grid:** stop-loss {SLS} x target {TPS} (0 = none) x time exit {EXITS}  |  **Rs 60,000 per trade cap, no charges / slippage**", "",
         "## Status of each strategy", ""]
    L += [f"- **{n}**: {progress_of(n)}" for n in ORDER if os.path.isdir(f"{OUT}/{n}")]
    L += ["", f"## Best variant per strategy by total PnL (at least {mt} trades)", "", md(best[cols].round(2)), "",
          f"## Best variant per strategy by ROI (at least {mt} trades)", "", md(bestr[cols].round(2)), ""]
    for ex in sorted(A.exit_rule.unique()):
        g = good[good.exit_rule == ex]
        if g.empty: continue
        L += [f"## Exit {ex}: best variant of each strategy by total PnL", "",
              md(g.sort_values("total_pnl", ascending=False).groupby("strategy").head(1).sort_values("total_pnl", ascending=False)[cols].round(2)), ""]
    # the SAME variant for every strategy: PnL and win % matrix for no SL / no TP at each exit
    for sl_l, tp_l in (("no SL", "no TP"), ("no SL", "TP 40%")):
        g = good[(good.sl_rule == sl_l) & (good.tp_rule == tp_l)]
        if g.empty: continue
        for metric, title in (("total_pnl", "Total PnL (Rs)"), ("win_pct", "Win %"), ("trades", "Trades")):
            P = g.pivot_table(index="strategy", columns="exit_rule", values=metric, aggfunc="first").round(1).reset_index()
            L += [f"## Same variant for all strategies - {sl_l} / {tp_l}: {title} by time exit", "", md(P), ""]
    L += ["Everything is in `ALL_VARIANTS.csv` (every strategy x exit x SL x TP). The best variant is the best of many, chosen after seeing the results, so it is optimistic; 10 stocks x 1 year gives few trades, "
          "so look at the trade counts. Charges, taxes and slippage are not included. Past results do not promise future results.", ""]
    open(f"{OUT}/COMPARE.md", "w").write("\n".join(L))
    print("\n".join(L[:30]), flush=True)


# ---------------------------------------------------------------- main
def main():
    argv = sys.argv[1:]
    mode = next((a for a in argv if not a.startswith("--")), "")
    if mode == "compare": compare(); return
    names = selected(argv)
    if mode == "rules":
        print(f"stocks   : {SYMBOLS}\nperiod   : {START} .. {END}\ngrid     : SL {SLS} x TP {TPS} (0 = none) x exits {EXITS}\nmin trades for 'best' tables: {MIN_TRADES}\nout      : {OUT}/<strategy>/\n")
        for n in names:
            script, label, build, modes = STRATS[n]
            print(f"- {n:9s} {label}\n    python {script} <{'|'.join(modes)}>   env: " + json.dumps(build(f"{OUT}/{n}")))
        return
    if mode not in ("check", "run", "summary"): sys.exit("use: python top10_all_backtest.py rules | check | run | summary | compare   [--only gap,orb,...]")
    t0 = time.time(); fails = []
    for i, n in enumerate(names):
        left = BUDGET_MIN - (time.time() - t0) / 60 - 4
        if mode == "run" and left < 3: print(f"[{n}] no time left in this run - run again", flush=True); continue
        share = left if mode != "run" else max(3.0, left / 1.0)      # a finished strategy returns early, so the next one gets the rest
        if run_one(n, mode, share) != 0: fails.append(n)
    if mode in ("run", "summary"):
        compare()
        print("\nSTATUS:", flush=True)
        for n in names: print(f"  {n:9s} {progress_of(n)}", flush=True)
        print("\nrun again until nothing says PARTIAL." + (f"  (failed: {fails})" if fails else ""), flush=True)


if __name__ == "__main__":
    main()
