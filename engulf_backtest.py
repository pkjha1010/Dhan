"""engulf_backtest.py - GREEN-ENGULFING breakout (LONG) on ALL F&O stock options, 3 years, Dhan 1-minute data.  Same engine as sltp_backtest.py / all8_backtest.py.

  python engulf_backtest.py check     test Dhan access + print the rules
  python engulf_backtest.py run       full backtest for EB_START .. EB_END (resumable - run again after a polite stop)
  python engulf_backtest.py summary   rebuild every result file from the saved option data (no API calls)
  python engulf_backtest.py rules     print the rules only

SETUP (daily chart, rules in engulf_rules.py)
  1. A GREEN candle that engulfs the previous (not green) candle and whose High is the 10-day rolling high.
  2. Mini pullback, the next 5 days: no daily CLOSE below the engulfing candle's LOW, and at least one CLOSE inside the engulfing candle's BODY.
  3. LEVEL = the highest High from the engulfing candle to the end of the pullback.
  4. ENTRY = the first time price crosses ABOVE the level (1-minute High >= level, first candle from 09:15, last 15:20).  While waiting, a daily close below the engulfing low
     cancels the setup.
OPTION     buy the ATM CALL (nearest monthly expiry, strike locked at entry).  If the ATM series has no candle at the entry minute: ITM-1, ITM-2 ... ITM-EB_ITM_MAX (a call's ITM = lower strike)
           until a strike with a candle is found.  The strike used is stored per trade (strike_offset: 0 = ATM, -n = ITM-n).  Option price = close of the entry-minute candle.
EXIT GRID  stop-loss 0 (none) / 20 / 40 / 60 %  x  target 20 / 40 / 60 / 80 / 100 / 120 / 200 % of the premium  x  time exit 09:30 / 10:00 / 15:30 the same day.
           Fills: stop / target = first 1-minute low / high touching the level; a gap through it fills at that candle's open; stop and target in the same minute = STOP.
           A trade entered at / after a time exit is skipped for that exit (so the 09:30 and 10:00 exits only have the early entries).
CAPITAL    at most Rs EB_CAP (60,000) per trade, whole lots.  Charges, taxes and slippage are not included.  Lot sizes are today's values for all years.

Results in engulf_results/ : SUMMARY.md (start here), summary.csv, matrix_*.csv, trade_files/, top_by_*.csv, REPORT.txt ...
"""
import os, sys, json, glob


def _env(name, default):
    return os.environ.get(name) or default


# ---------------------------------------------------------------- settings -> the A8_* names the engine reads (must be set BEFORE the engine is imported)
OUT = _env("EB_OUT", "engulf_results")
os.environ["A8_OUT"] = OUT
os.environ["A8_START"] = _env("EB_START", "2023-10-27")
os.environ["A8_END"] = _env("EB_END", "2026-10-23")
if os.environ.get("EB_SYMBOLS"): os.environ["A8_SYMBOLS"] = os.environ["EB_SYMBOLS"]
if os.environ.get("EB_CAP"): os.environ["A8_CAP"] = os.environ["EB_CAP"]
os.environ["A8_SLS"] = _env("EB_SLS", "0,20,40,60")                              # 0 = no stop-loss
os.environ["A8_TPS"] = _env("EB_TPS", "20,40,60,80,100,120,200")
os.environ["A8_ENTRY_LAST"] = _env("EB_ENTRY_LAST", "15:20")
os.environ["A8_MIN_TRADES"] = _env("EB_MIN_TRADES", "30")
os.environ["A8_TRADES_ALL"] = "1"                                                # every trade of every variant, one file per strategy
os.environ["A8_SUM_ENTRY_FROM"] = os.environ["A8_SUM_ENTRY_TO"] = ""
ROLL = int(_env("EB_ROLL", "10"))                                                # rolling-high days
PULL = int(_env("EB_PULL", "5"))                                                 # pullback window (days after the engulfing candle)
WAIT = int(_env("EB_WAIT", "0"))                                                 # max waiting days for the breakout after the pullback (0 = no limit)
ITM_MAX = int(_env("EB_ITM_MAX", "3"))                                           # ATM first, then ITM-1 ... ITM-n (0 = ATM only)
TEXITS = [x.strip() for x in _env("EB_EXITS", "09:30,10:00,15:30").replace(" ", ",").split(",") if len(x.strip()) == 5 and x.strip()[2] == ":"]

import numpy as np, pandas as pd
import all8_backtest as A
import engulf_rules as R
C = A.C

STRAT = "GREEN_ENGULF_LONG"
STRAT_RULE = {STRAT: f"green engulfing at the {ROLL}-day high -> {PULL}-day pullback (closes in the body, none below the low) -> cross above the highest point"}
STRATS = list(STRAT_RULE)
_YAHOO_COLS = ["Open", "High", "Low", "Close"]


# ---------------------------------------------------------------- the entry rule used by the engine
def entries_for(u, level, long):
    """Replaces combo_dayrisk_backtest.entries_for.  LONG only.  -> {entry type: entry timestamp}"""
    if not long or u is None or len(u) == 0: return {}
    k = R.first_cross_long(u, level, A.E_FIRST, A.ENTRY_MIN)
    return {} if k is None else {"ENG": u.index[k]}


def strategies_for(source, typ, green, red, up, lo):
    return [STRAT] if (source == "ENGULF" and typ == "ENG") else []


def install():
    C.entries_for = entries_for
    A.strategies_for = strategies_for
    A.STRATS = list(STRATS)
    A.ENTRY_TYPE = {s: STRAT_RULE[s] for s in STRATS}
    A.TEXITS = list(TEXITS)
    A.EXITS = list(A.TEXITS)                                                     # time exits only, no UNTIL_HIT
    A.VARS = [(ex, sl, tp) for ex in A.EXITS for sl in A.SLS for tp in A.TPS]
    if ITM_MAX > 0:
        import itm_fallback as IF
        A.work_group = IF.make_work_group(A, ITM_MAX)                            # ATM -> ITM-1 -> ... -> ITM-n


install()


def rule_dict():
    return dict(roll=ROLL, pull=PULL, wait=WAIT, itm_max=ITM_MAX, entry_last=A.ENTRY_LAST, start=A.START, end=A.END, sls=A.SLS, tps=A.TPS, exits=A.EXITS, cap=A.CAP,
                symbols=len(A.UNIVERSE))


def rules_text():
    return (f"GREEN ENGULFING breakout, LONG, ATM call (ITM fallback up to ITM-{ITM_MAX}).  Green candle engulfing a non-green candle at the {ROLL}-day high; next {PULL} days: no close below the "
            f"engulfing low and at least one close inside its body; level = highest High from the engulfing candle to the end of the pullback; entry = first 1-minute High >= level "
            f"(09:15 to {A.ENTRY_LAST}); a daily close below the engulfing low while waiting cancels the setup" + (f"; waiting limited to {WAIT} days." if WAIT else "; no limit on the waiting time."))


def print_rules():
    print(rules_text(), flush=True)
    print(f"Grid: stop-loss {A.SLS} (0 = none) x target {A.TPS} x time exit {A.EXITS} = {len(A.VARS)} variants; {len(A.UNIVERSE)} stocks; {A.START} .. {A.END}; cap Rs {A.CAP}", flush=True)


# ---------------------------------------------------------------- step 1: daily candidates (Yahoo)
def setups_to_rows(stock, dates, O, H, L, C_, t0, t1, pre_tol):
    rows = []
    for s in R.engulf_setups(O, H, L, C_, PULL, WAIT, ROLL):
        e = s["entry"]
        if not (t0 <= pd.Timestamp(dates[e]) <= t1): continue
        if not (O[e] >= s["level"] * (1 - pre_tol)): continue                      # daily prefilter: the entry day opens within pre_tol below the level
        rows.append(dict(source="ENGULF", stock=stock, direction="LONG", ref=round(s["level"], 2), signal_date=dates[s["engulf"]], date=dates[e], yahoo_open=float(O[e]),
                         green=-1, red=-1, upper_longer=-1, lower_longer=-1, engulf_date=dates[s["engulf"]], pullback_end=dates[s["pb_end"]],
                         engulf_low=round(s["signal_low"], 2), body_low=round(s["body_lo"], 2), body_high=round(s["body_hi"], 2)))
    return rows


def yahoo_candidates():
    import yfinance as yf
    t0, t1 = pd.Timestamp(A.START), pd.Timestamp(A.END)
    raw = yf.download([s + ".NS" for s in A.UNIVERSE], start=str((t0 - pd.Timedelta(days=120)).date()), end=str((t1 + pd.Timedelta(days=45)).date()),
                      group_by="ticker", auto_adjust=False, progress=False, threads=True)
    rows, nst = [], 0
    for s in A.UNIVERSE:
        try: d = raw[s + ".NS"][_YAHOO_COLS].dropna()
        except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
        if len(d) < 60: continue
        nst += 1
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        O, H, L, C_ = (d[k].values.astype(float) for k in _YAHOO_COLS)
        rows += setups_to_rows(s, d.index.strftime("%Y-%m-%d"), O, H, L, C_, t0, t1, C.PRE_TOL)
    if nst == 0: raise A.Fatal("Yahoo download gave no data for any stock - run again later")
    r = pd.DataFrame(rows)
    print(f"Yahoo: {nst} stocks, {len(r)} green-engulfing setups with an entry day in {A.START}..{A.END}", flush=True)
    return r


def get_candidates():
    cp = f"{A.OUT}/candidates_{A.START}_{A.END}.csv"
    if os.path.exists(cp): return pd.read_csv(cp)
    cand = yahoo_candidates()
    cand.to_csv(cp, index=False)
    return cand


def run():
    os.makedirs(A.OUT, exist_ok=True)
    rp = f"{A.OUT}/rule.json"; rule = json.loads(json.dumps(rule_dict()))
    if os.path.exists(rp):
        old = json.load(open(rp))
        if old != rule:
            sys.exit("STOP - the saved data in " + A.OUT + " was made with other settings:\n  saved: " + json.dumps(old) + "\n  now:   " + json.dumps(rule) +
                     "\nUse the same settings, or give EB_OUT / the 'out_dir' box another folder name.")
    json.dump(rule, open(rp, "w"), indent=1)
    print_rules()
    st = A.load_state(); dh = A.Dhan(); mst = A.load_master()
    try:
        cand = get_candidates()
        if cand.empty: print("No candidate days in this range."); return
        print(f"Candidate entry days {A.START}..{A.END}: {len(cand)}", flush=True)
        ev = A.step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= A.START) & (ev["date"] <= A.END)] if len(ev) else ev
        print(f"Entries (09:15-{A.ENTRY_LAST}): {len(ev)}", flush=True)
        if len(ev): A.step_options(dh, ev, mst, st)
        print("ALL STEPS FINISHED", flush=True)
    except A.Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        A.B.print_stats(dh); A.progress(); summary(); A.checkpoint(True)


# ---------------------------------------------------------------- result files
def label_sl(v): return "no SL" if not v else f"SL {int(v)}%"
def label_tp(v): return "no TP" if not v else f"TP {int(v)}%"


def md(df, index=False):
    try: return df.to_markdown(index=index)
    except Exception: return df.to_string(index=index)


def tp_order():
    return [t for t in A.TPS if t] + ([0] if 0 in A.TPS else [])


def matrices(S, metric):
    """rows exit / stop-loss, columns target."""
    P = S.pivot_table(index=["strategy", "exit_rule", "sl"], columns="tp", values=metric, aggfunc="first")
    P = P.reindex(columns=[t for t in tp_order() if t in P.columns])
    P.columns = [label_tp(t) for t in P.columns]
    P = P.reset_index(); P.insert(3, "stop_loss", P.sl.map(label_sl)); P = P.drop(columns="sl")
    return P


def read_entries():
    """One row per entry: the event + its option record + the engulfing-candle details from the candidates file."""
    ep = f"{A.OUT}/events.csv"; recs = A.load_records()
    if recs.empty or not os.path.exists(ep): return pd.DataFrame()
    ev = pd.read_csv(ep, dtype={"entry_minute": str}); ev["ekey"] = ev.stock + "|" + ev.direction + "|" + ev.date + "|" + ev.entry_minute
    E = ev.merge(recs[[c for c in ("ekey", "strike", "expiry", "entry_price", "lot", "cov", "strike_offset") if c in recs.columns]], on="ekey", how="left")
    cps = sorted(glob.glob(f"{A.OUT}/candidates_*.csv"))
    if cps and "engulf_date" in pd.read_csv(cps[-1], nrows=1).columns:
        cd = pd.read_csv(cps[-1])[["stock", "date", "engulf_date", "pullback_end", "engulf_low", "body_low", "body_high"]].drop_duplicates(["stock", "date"])
        E = E.merge(cd, on=["stock", "date"], how="left")
    return E


def post_process():
    sp = f"{A.OUT}/summary.csv"
    if not os.path.exists(sp): return
    S = pd.read_csv(sp)
    if S.empty: return
    S["sl_rule"] = S.sl.map(label_sl); S["tp_rule"] = S.tp.map(label_tp)
    S["variant"] = S.strategy + " | exit " + S.exit_rule + " | " + S.sl_rule + " | " + S.tp_rule
    S.to_csv(sp, index=False)
    old = f"{A.OUT}/until_hit_days_held.csv"
    if os.path.exists(old): os.remove(old)
    for metric in ("total_pnl", "roi_pct", "win_pct", "profit_factor"): matrices(S, metric).to_csv(f"{A.OUT}/matrix_{metric}.csv", index=False)
    good = S[S.trades >= A.MIN_TRADES]; base = good if len(good) else S
    os.makedirs(f"{A.OUT}/trade_files", exist_ok=True)
    E = read_entries()
    best, files = [], []
    for s in STRATS:
        g = base[base.strategy == s]
        if g.empty: continue
        bp = g.sort_values(["total_pnl", "trades"], ascending=False).iloc[0]; best.append(bp)
        tp = f"{A.OUT}/all_trades/{s}.csv.gz"
        if not os.path.exists(tp): continue
        T = pd.read_csv(tp).sort_values(["exit_rule", "sl", "tp", "entry_date", "entry_time", "stock"])
        if len(E):
            sub = E[E.strategy == s].rename(columns={"date": "entry_date", "entry_minute": "entry_time", "ref": "level"})
            keep = [c for c in ("stock", "entry_date", "entry_time", "level", "engulf_date", "pullback_end", "engulf_low", "body_low", "body_high", "strike_offset") if c in sub.columns]
            T = T.merge(sub[keep].drop_duplicates(["stock", "entry_date", "entry_time"]), on=["stock", "entry_date", "entry_time"], how="left")
        T.to_csv(f"{A.OUT}/trade_files/{s}_all_variants_trades.csv", index=False)
        B = T[(T.exit_rule == bp.exit_rule) & (T.sl == bp.sl) & (T.tp == bp.tp)]
        B.insert(0, "variant", bp.variant); B.to_csv(f"{A.OUT}/trade_files/{s}_best_trades.csv", index=False)
        if len(E):
            E[E.strategy == s].sort_values(["date", "entry_minute", "stock"]).drop(columns=["ekey"]).to_csv(f"{A.OUT}/trade_files/{s}_entries.csv", index=False)
        files.append((s, len(B), bp.variant, int(T[["exit_rule", "sl", "tp"]].drop_duplicates().shape[0])))
    cols = ["strategy", "exit_rule", "sl_rule", "tp_rule", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "max_drawdown"]
    ts = pd.read_csv(f"{A.OUT}/trades_summary.csv") if os.path.exists(f"{A.OUT}/trades_summary.csv") else pd.DataFrame()
    prog = open(f"{A.OUT}/PROGRESS.txt").read().strip() if os.path.exists(f"{A.OUT}/PROGRESS.txt") else "(no progress file)"
    L = ["# GREEN ENGULFING breakout (LONG, ATM call) - SL x TP x time-exit grid", "",
         f"**Status:** {prog}", "",
         f"**Period (entry dates):** {A.START} to {A.END}  |  **Stocks:** all F&O stocks with Dhan data ({len(A.UNIVERSE)} tried)  |  **Capital per trade:** up to Rs {A.CAP:,} (whole lots)", "",
         "## Rules", "", rules_text(), "",
         f"**Grid:** stop-loss {', '.join(label_sl(v) for v in A.SLS)} x target {', '.join(label_tp(v) for v in tp_order())} x time exit {', '.join(A.EXITS)} = {len(A.VARS)} variants. "
         "Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the 09:30 and 10:00 exits have fewer trades than 15:30.", ""]
    if len(ts):
        t2 = ts[[c for c in ("strategy", "signals_with_entry", "entries_with_option_data", "dropped_low_coverage", "skipped_no_option_data", "skip_reasons") if c in ts.columns]]
        L += ["## Entries found", "", md(t2), ""]
    if len(E) and "strike_offset" in E.columns:
        vc = E[E.entry_price.notna()].strike_offset.value_counts().sort_index()
        L += ["## Strike used", "", "strike_offset 0 = ATM, -n = ITM-n (the ATM series had no candle at the entry minute): " + ", ".join(f"{int(k)}: {int(v)}" for k, v in vc.items()), ""]
    for ex in A.EXITS:
        g = S[(S.strategy == STRAT) & (S.exit_rule == ex)]
        if g.empty: continue
        L += [f"## Exit {ex}", ""]
        for metric, title in (("total_pnl", "Total PnL (Rs)"), ("roi_pct", "ROI % on capital used"), ("win_pct", "Win %")):
            M = matrices(g, metric).drop(columns=["strategy", "exit_rule"])
            L += [f"**{title}** (rows stop-loss, columns target)  -  trades per variant: {int(g.trades.min())}-{int(g.trades.max())}", "", md(M), ""]
    if best: L += ["## Best variant by total PnL", "", md(pd.DataFrame(best)[cols]), ""]
    L += [f"## Top 10 variants by ROI (at least {A.MIN_TRADES} trades)", "", md(good.sort_values("roi_pct", ascending=False).head(10)[cols]) if len(good) else "(none yet)", "",
          "## Trade files", "",
          "In `trade_files/`: `GREEN_ENGULF_LONG_all_variants_trades.csv` (every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none), `..._best_trades.csv` (best-PnL variant) and "
          "`..._entries.csv` (one row per entry: level, engulfing date, pullback end, engulfing low, strike, expiry, option price).", ""]
    L += [f"- `{s}`: best variant {v} - {n} trades; {nv} variants in the all-variants file" for s, n, v, nv in files]
    L += ["", "The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at `summary_by_year_top.csv`. "
          "Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.", ""]
    open(f"{A.OUT}/SUMMARY.md", "w").write("\n".join(L))
    print("\n".join(L[:8]), flush=True)


def summary():
    try:
        A.summary()
    except ValueError as e:                                                      # too few trades for MIN_TRADES (e.g. a quick test with a few stocks)
        print(f"note: no variant has {A.MIN_TRADES} trades yet ({e}); rebuilding the tables with a minimum of 1", flush=True)
        A.MIN_TRADES = 1; A.summary()
    post_process()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": print_rules(); A.check()
        elif mode == "run": run()
        elif mode in ("summary", "range"): print_rules(); summary()
        elif mode == "rules": print_rules()
        else: sys.exit("use: python engulf_backtest.py check | run | summary | rules")
    except A.Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
