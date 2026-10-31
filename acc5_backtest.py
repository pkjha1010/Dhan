"""acc5_backtest.py - 5-DAY ACCUMULATION fake-break, LONG (call) and SHORT (put) on ALL F&O stock options, 3 years, Dhan 1-minute data.  Same engine as engulf_backtest.py / all8_backtest.py.

  python acc5_backtest.py check     test Dhan access + print the rules
  python acc5_backtest.py run       full backtest for AC_START .. AC_END (resumable - run again after a polite stop)
  python acc5_backtest.py summary   rebuild every result file from the saved option data (no API calls)
  python acc5_backtest.py rules     print the rules only

SETUP (daily chart, rules in acc5_rules.py)   Acc_High / Acc_Low = highest High / lowest Low of the prior 5 completed days
  LONG   1. a daily CLOSE below Acc_Low = breakdown.   2. within the next 3 days price crosses ABOVE Acc_High (Acc_High of that day)  ->  buy the ATM CALL.
  SHORT  1. a daily CLOSE above Acc_High = breakout.   2. within the next 3 days price crosses BELOW Acc_Low  (Acc_Low of that day)   ->  buy the ATM PUT.
  ENTRY  = the first 1-minute candle (09:15 .. 15:20) whose High >= level (LONG) / Low <= level (SHORT); the option price = close of that entry minute.
           (Your original script used the daily close and assumed a fill at the level; here the exact minute and the option price at that minute are used.)
OPTION     the ATM option of the nearest monthly expiry (strike locked at entry).  If the ATM series has no candle at the entry minute: ITM-1, ITM-2 ... ITM-AC_ITM_MAX
           (a call's ITM = lower strike, a put's ITM = higher strike).  The strike used is stored per trade (strike_offset: 0 = ATM, +-n = ITM-n).
EXIT GRID  stop-loss none / 20 / 40 % x target 20 / 40 / 60 / 80 / 120 % / none x time exit 09:30 / 10:00 / 12:00 / 15:30 the same day = 72 variants per direction (percent of the premium).
           Fills: stop / target = first 1-minute low / high touching the level; a gap through it fills at that candle's open; stop and target in the same minute = STOP.
           A trade entered at / after a time exit is skipped for that exit (so the 09:30 / 10:00 / 12:00 exits only have the earlier entries).
CAPITAL    at most Rs AC_CAP (60,000) per trade, whole lots.  Charges, taxes and slippage are not included.  Lot sizes are today's values for all years.

Results in acc5_results/ : SUMMARY.md (both directions), long/ and short/ (each with its own SUMMARY.md, summary.csv, matrix_*.csv, trades) ...
"""
import os, sys, json, glob


def _env(name, default):
    return os.environ.get(name) or default


# ---------------------------------------------------------------- settings -> the A8_* names the engine reads (must be set BEFORE the engine is imported)
OUT = _env("AC_OUT", "acc5_results")
os.environ["A8_OUT"] = OUT
os.environ["A8_START"] = _env("AC_START", "2023-10-30")
os.environ["A8_END"] = _env("AC_END", "2026-10-30")
if os.environ.get("AC_SYMBOLS"): os.environ["A8_SYMBOLS"] = os.environ["AC_SYMBOLS"]
if os.environ.get("AC_CAP"): os.environ["A8_CAP"] = os.environ["AC_CAP"]
os.environ["A8_SLS"] = _env("AC_SLS", "0,20,40")                                 # 0 = no stop-loss
os.environ["A8_TPS"] = _env("AC_TPS", "20,40,60,80,120,0")                       # 0 = no target
os.environ["A8_ENTRY_LAST"] = _env("AC_ENTRY_LAST", "15:20")
os.environ["A8_MIN_TRADES"] = _env("AC_MIN_TRADES", "30")
os.environ["A8_TRADES_ALL"] = "1"                                                # every trade of every variant, one file per strategy
os.environ["A8_SUM_ENTRY_FROM"] = os.environ["A8_SUM_ENTRY_TO"] = ""
ACC = int(_env("AC_ACC", "5"))                                                   # accumulation days (prior completed days)
WINDOW = int(_env("AC_WINDOW", "3"))                                             # candles allowed between the breakdown and the cross back
ITM_MAX = int(_env("AC_ITM_MAX", "3"))                                           # ATM first, then ITM-1 ... ITM-n (0 = ATM only)
TEXITS = [x.strip() for x in _env("AC_EXITS", "09:30,10:00,12:00,15:30").replace(" ", ",").split(",") if len(x.strip()) == 5 and x.strip()[2] == ":"]

import numpy as np, pandas as pd
import all8_backtest as A
import acc5_rules as R
C = A.C

STRAT_L, STRAT_S = "ACC5_LONG", "ACC5_SHORT"
STRAT_RULE = {
    STRAT_L: f"close below the {ACC}-day low (breakdown) -> within {WINDOW} days price crosses back above the {ACC}-day high -> buy CALL",
    STRAT_S: f"close above the {ACC}-day high (breakout) -> within {WINDOW} days price crosses back below the {ACC}-day low -> buy PUT"}
STRATS = list(STRAT_RULE)
DIRNAME = {STRAT_L: "long", STRAT_S: "short"}
_YAHOO_COLS = ["Open", "High", "Low", "Close"]


# ---------------------------------------------------------------- the entry rule used by the engine
def entries_for(u, level, long):
    """Replaces combo_dayrisk_backtest.entries_for.  -> {entry type: entry timestamp}   (ACCL = LONG, ACCS = SHORT)"""
    if u is None or len(u) == 0: return {}
    k = R.first_cross_long(u, level, A.E_FIRST, A.ENTRY_MIN) if long else R.first_cross_short(u, level, A.E_FIRST, A.ENTRY_MIN)
    return {} if k is None else {("ACCL" if long else "ACCS"): u.index[k]}


def strategies_for(source, typ, green, red, up, lo):
    if source != "ACC5": return []
    return [STRAT_L] if typ == "ACCL" else [STRAT_S] if typ == "ACCS" else []


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
    return dict(acc=ACC, window=WINDOW, itm_max=ITM_MAX, entry_last=A.ENTRY_LAST, start=A.START, end=A.END, sls=A.SLS, tps=A.TPS, exits=A.EXITS, cap=A.CAP,
                symbols=len(A.UNIVERSE))


def rules_text():
    return (f"{ACC}-DAY ACCUMULATION fake-break.  Acc_High / Acc_Low = highest High / lowest Low of the prior {ACC} completed days.  LONG (ATM call): a daily close below Acc_Low, then "
            f"within {WINDOW} days price crosses back above Acc_High (that day's).  SHORT (ATM put): a daily close above Acc_High, then within {WINDOW} days price crosses back below "
            f"Acc_Low.  Entry = the first 1-minute candle (09:15 to {A.ENTRY_LAST}) that reaches the level; option = ATM, ITM-1 .. ITM-{ITM_MAX} if the ATM series has no candle at the entry minute.")


def print_rules():
    print(rules_text(), flush=True)
    print(f"Grid: stop-loss {A.SLS} (0 = none) x target {A.TPS} (0 = none) x time exit {A.EXITS} = {len(A.VARS)} variants per direction; {len(A.UNIVERSE)} stocks; {A.START} .. {A.END}; cap Rs {A.CAP}", flush=True)


# ---------------------------------------------------------------- step 1: daily candidates (Yahoo)
def setups_to_rows(stock, dates, O, H, L, C_, t0, t1, pre_tol):
    rows = []
    for long in (True, False):
        for s in R.acc_setups(O, H, L, C_, long, ACC, WINDOW):
            e = s["entry"]
            if not (t0 <= pd.Timestamp(dates[e]) <= t1): continue
            lvl = s["level"]
            if long and not (O[e] >= lvl * (1 - pre_tol)): continue                  # daily prefilter: the entry day opens within pre_tol of the level (entry side)
            if not long and not (O[e] <= lvl * (1 + pre_tol)): continue
            rows.append(dict(source="ACC5", stock=stock, direction="LONG" if long else "SHORT", ref=round(lvl, 2), signal_date=dates[s["signal"]], date=dates[e],
                             yahoo_open=float(O[e]), green=-1, red=-1, upper_longer=-1, lower_longer=-1,
                             acc_high=round(lvl if long else s["other"], 2), acc_low=round(s["other"] if long else lvl, 2)))
    return rows


def yahoo_candidates():
    import yfinance as yf
    t0, t1 = pd.Timestamp(A.START), pd.Timestamp(A.END)
    raw = yf.download([s + ".NS" for s in A.UNIVERSE], start=str((t0 - pd.Timedelta(days=60)).date()), end=str((t1 + pd.Timedelta(days=5)).date()),
                      group_by="ticker", auto_adjust=False, progress=False, threads=True)
    rows, nst = [], 0
    for s in A.UNIVERSE:
        try: d = raw[s + ".NS"][_YAHOO_COLS].dropna()
        except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
        if len(d) < 30: continue
        nst += 1
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        O, H, L, C_ = (d[k].values.astype(float) for k in _YAHOO_COLS)
        rows += setups_to_rows(s, d.index.strftime("%Y-%m-%d"), O, H, L, C_, t0, t1, C.PRE_TOL)
    if nst == 0: raise A.Fatal("Yahoo download gave no data for any stock - run again later")
    r = pd.DataFrame(rows)
    nl = int((r.direction == "LONG").sum()) if len(r) else 0
    print(f"Yahoo: {nst} stocks, {nl} LONG + {len(r) - nl} SHORT setups with an entry day in {A.START}..{A.END}", flush=True)
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
                     "\nUse the same settings, or give AC_OUT / the 'out_dir' box another folder name.")
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
    """One row per entry: the event + its option record + the Acc levels from the candidates file."""
    ep = f"{A.OUT}/events.csv"; recs = A.load_records()
    if recs.empty or not os.path.exists(ep): return pd.DataFrame()
    ev = pd.read_csv(ep, dtype={"entry_minute": str}); ev["ekey"] = ev.stock + "|" + ev.direction + "|" + ev.date + "|" + ev.entry_minute
    E = ev.merge(recs[[c for c in ("ekey", "strike", "expiry", "entry_price", "lot", "cov", "strike_offset") if c in recs.columns]], on="ekey", how="left")
    cps = sorted(glob.glob(f"{A.OUT}/candidates_*.csv"))
    if cps and "acc_high" in pd.read_csv(cps[-1], nrows=1).columns:
        cd = pd.read_csv(cps[-1])[["stock", "direction", "date", "acc_high", "acc_low"]].drop_duplicates(["stock", "direction", "date"])
        E = E.merge(cd, on=["stock", "direction", "date"], how="left")
    return E


def write_direction(strat, S, E, base, cols, prog):
    """Everything for ONE direction into OUT/<long|short>/ ; returns the best row (or None)."""
    d = f"{A.OUT}/{DIRNAME[strat]}"; os.makedirs(d, exist_ok=True)
    G = S[S.strategy == strat]
    if G.empty: return None
    G.to_csv(f"{d}/summary.csv", index=False)
    for metric in ("total_pnl", "roi_pct", "win_pct", "profit_factor"): matrices(G, metric).to_csv(f"{d}/matrix_{metric}.csv", index=False)
    g = base[base.strategy == strat]; g = g if len(g) else G
    bp = g.sort_values(["total_pnl", "trades"], ascending=False).iloc[0]
    tp = f"{A.OUT}/all_trades/{strat}.csv.gz"; nT = nB = 0
    if os.path.exists(tp):
        T = pd.read_csv(tp).sort_values(["exit_rule", "sl", "tp", "entry_date", "entry_time", "stock"])
        if len(E):
            sub = E[E.strategy == strat].rename(columns={"date": "entry_date", "entry_minute": "entry_time", "ref": "level"})
            keep = [c for c in ("stock", "entry_date", "entry_time", "level", "acc_high", "acc_low", "strike_offset") if c in sub.columns]
            T = T.merge(sub[keep].drop_duplicates(["stock", "entry_date", "entry_time"]), on=["stock", "entry_date", "entry_time"], how="left")
        T.to_csv(f"{d}/trades_all_variants.csv.gz", index=False); nT = len(T)
        B = T[(T.exit_rule == bp.exit_rule) & (T.sl == bp.sl) & (T.tp == bp.tp)]
        B.insert(0, "variant", bp.variant); B.to_csv(f"{d}/trades_best_variant.csv", index=False); nB = len(B)
    if len(E):
        E[E.strategy == strat].sort_values(["date", "entry_minute", "stock"]).drop(columns=["ekey"]).to_csv(f"{d}/entries.csv", index=False)
    ts = pd.read_csv(f"{A.OUT}/trades_summary.csv") if os.path.exists(f"{A.OUT}/trades_summary.csv") else pd.DataFrame()
    L = [f"# 5-DAY ACCUMULATION fake-break - {DIRNAME[strat].upper()} ({'ATM call' if strat == STRAT_L else 'ATM put'}) - SL x TP x time-exit grid", "",
         f"**Status:** {prog}", "",
         f"**Period (entry dates):** {A.START} to {A.END}  |  **Stocks:** all F&O stocks with Dhan data ({len(A.UNIVERSE)} tried)  |  **Capital per trade:** up to Rs {A.CAP:,} (whole lots)", "",
         "## Rule", "", STRAT_RULE[strat], "",
         f"**Grid:** stop-loss {', '.join(label_sl(v) for v in A.SLS)} x target {', '.join(label_tp(v) for v in tp_order())} x time exit {', '.join(A.EXITS)} = {len(A.VARS)} variants. "
         "Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.", ""]
    if len(ts):
        t2 = ts[ts.strategy == strat][[c for c in ("strategy", "signals_with_entry", "entries_with_option_data", "dropped_low_coverage", "skipped_no_option_data", "skip_reasons") if c in ts.columns]]
        if len(t2): L += ["## Entries found", "", md(t2), ""]
    if len(E) and "strike_offset" in E.columns:
        vc = E[(E.strategy == strat) & E.entry_price.notna()].strike_offset.value_counts().sort_index()
        L += ["## Strike used", "", "strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): " + ", ".join(f"{int(k)}: {int(v)}" for k, v in vc.items()), ""]
    for ex in A.EXITS:
        gx = G[G.exit_rule == ex]
        if gx.empty: continue
        L += [f"## Exit {ex}", ""]
        for metric, title in (("total_pnl", "Total PnL (Rs)"), ("roi_pct", "ROI % on capital used"), ("win_pct", "Win %")):
            M = matrices(gx, metric).drop(columns=["strategy", "exit_rule"])
            L += [f"**{title}** (rows stop-loss, columns target)  -  trades per variant: {int(gx.trades.min())}-{int(gx.trades.max())}", "", md(M), ""]
    gg = base[base.strategy == strat]
    L += ["## Best variant by total PnL", "", md(pd.DataFrame([bp])[cols]), "",
          f"## Top 10 variants by ROI (at least {A.MIN_TRADES} trades)", "", md(gg.sort_values("roi_pct", ascending=False).head(10)[cols]) if len(gg) else "(none yet)", "",
          f"## Top 10 variants by total PnL (at least {A.MIN_TRADES} trades)", "", md(gg.sort_values("total_pnl", ascending=False).head(10)[cols]) if len(gg) else "(none yet)", "",
          "## Files in this folder", "",
          f"`trades_all_variants.csv.gz` ({nT} rows: every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), `trades_best_variant.csv` ({nB} trades of the best-PnL variant), "
          "`entries.csv` (one row per entry: level, Acc high / low, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.", "",
          "The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. "
          "Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.", ""]
    open(f"{d}/SUMMARY.md", "w").write("\n".join(L))
    return bp


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
    good = S[S.trades >= A.MIN_TRADES]; base = good if len(good) else S
    E = read_entries()
    cols = ["strategy", "exit_rule", "sl_rule", "tp_rule", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "max_drawdown"]
    prog = open(f"{A.OUT}/PROGRESS.txt").read().strip() if os.path.exists(f"{A.OUT}/PROGRESS.txt") else "(no progress file)"
    best = [b for b in (write_direction(s, S, E, base, cols, prog) for s in STRATS) if b is not None]
    L = ["# 5-DAY ACCUMULATION fake-break (LONG call + SHORT put) - SL x TP x time-exit grid", "",
         f"**Status:** {prog}", "",
         f"**Period (entry dates):** {A.START} to {A.END}  |  **Stocks:** all F&O stocks with Dhan data ({len(A.UNIVERSE)} tried)  |  **Capital per trade:** up to Rs {A.CAP:,} (whole lots)", "",
         "## Rules", "", rules_text(), "",
         "LONG and SHORT are reported separately: `long/` and `short/` each hold their own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.", ""]
    ts = pd.read_csv(f"{A.OUT}/trades_summary.csv") if os.path.exists(f"{A.OUT}/trades_summary.csv") else pd.DataFrame()
    if len(ts):
        L += ["## Entries found", "", md(ts[[c for c in ("strategy", "signals_with_entry", "entries_with_option_data", "dropped_low_coverage", "skipped_no_option_data", "skip_reasons") if c in ts.columns]]), ""]
    if best: L += ["## Best variant by total PnL (per direction)", "", md(pd.DataFrame(best)[cols]), ""]
    for s in STRATS:
        gg = base[base.strategy == s]
        L += [f"## {DIRNAME[s].upper()} - top 10 by ROI (at least {A.MIN_TRADES} trades)", "", md(gg.sort_values("roi_pct", ascending=False).head(10)[cols]) if len(gg) else "(none yet)", ""]
    L += ["The best variants are the best of many, chosen after seeing the results, so they are optimistic. Charges, taxes and slippage are not included.", ""]
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
        else: sys.exit("use: python acc5_backtest.py check | run | summary | rules")
    except A.Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
