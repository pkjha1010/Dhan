"""sltp_backtest.py - STOP-LOSS x TARGET comparison for the BPB / WRU SHORT strategies, with the 5-close RE-CROSS entry check, on ALL F&O stock options (Dhan 1-minute data).

  SLTP_STUDY=pm python sltp_backtest.py run      afternoon study  (BPB SHORT, entries from 12:00, exits 15:00 / 15:30)   -> sltp_pm_results/
  SLTP_STUDY=am python sltp_backtest.py run      morning study    (BPB SHORT + WRU SHORT, entries 09:20-09:59, exit 10:00) -> sltp_am_results/
  python sltp_backtest.py check | rules | summary      (summary = rebuild every result file from the saved option data, no API calls)

SHORT = the stock falls to / through the entry LEVEL; the strategy buys the ATM PUT (nearest monthly expiry, strike locked at entry).  The daily setups (levels) are the
same as in all8_backtest.py / recross10_backtest.py: BPB = 10-day-low breakdown -> confirmed pullback -> level;  WRU = the SHAPECMP SHORT signal whose signal candle is RED with the
UPPER wick longer (WICK_RED_UPPER_SHORT).  The entry day is the first day after the signal on which the level is reachable.  Only the ENTRY RULE and the EXIT GRID are new.

ENTRY RULES (a "touch" = a 1-minute candle whose LOW is at / below the level; "closed above" = a 1-minute CLOSE above the level; wicks never count)
  AFTERNOON STUDY (pm)   entries from 12:00 to 15:20
    T1  FIRST TOUCH     the day's FIRST touch of the level is at / after 12:00  ->  enter on that candle.
    T2  RE-CROSS        the day's first touch was BEFORE 12:00  ->  from 12:00 on, enter on the first candle that touches the level after at least 5 CONSECUTIVE 1-minute
                        candles closed above it (no missing minute).  That is the "valid cross".
    T1+T2 COMBINED      one trade per signal day: T1 or T2 (they can never fire on the same day).
  MORNING STUDY (am)     entries 09:20 to 09:59 for BPB SHORT and for WRU SHORT, each separately
    RE-CROSS            the first candle from 09:20 to 09:59 that touches the level after at least 5 consecutive 1-minute candles closed above it (09:15-09:19 can be those 5).
  Entry price = close of the option candle of the entry minute.  The 5-close count, the 12:00 split and the windows are settings (see rule.json).

EXIT GRID (every combination is simulated for every entry; all percentages are % of the option PREMIUM)
  stop-loss   none / 20 / 40 / 60            target   60 / 80 / 100 / 120 / none
  time exit   pm: 15:00 and 15:30            am: 10:00        (close of the last option candle up to that minute; a trade entered at / after it is skipped for that exit)
  Fills       stop / target = first 1-minute low / high that touches the level; a gap through it fills at that candle's open; stop and target in the same minute = STOP.
CAPITAL     at most Rs 60,000 per trade (whole lots), the same for every stop-loss, so the PnL of the variants can be compared directly.  Charges / slippage are not included.
            Lot sizes are today's values for all years.

RESULTS in the output folder:
  SUMMARY.md               start here: rules, entries found, the SL x TP tables, best variants, file list
  summary.csv              one row per strategy x time exit x stop-loss x target (trades, win %, PnL, ROI, profit factor, drawdown, exits by reason)
  matrix_total_pnl.csv  matrix_roi_pct.csv  matrix_win_pct.csv  matrix_profit_factor.csv     rows = strategy / exit / stop-loss, columns = target
  trade_files/<STRATEGY>_all_variants_trades.csv    EVERY trade of EVERY variant (filter by exit_rule / sl / tp), plain CSV
  trade_files/<STRATEGY>_best_trades.csv            the trades of the best-PnL variant        trade_files/<STRATEGY>_entries.csv   one row per entry (level, first touch, strike, price)
  (+ all_trades/<STRATEGY>.csv.gz, events.csv, entry_log.csv, parts/, skipped/, trades_summary.csv, REPORT.txt, PROGRESS.txt, rule.json)
"""
import os, sys, json, glob, re, threading


def _env(name, default):
    return os.environ.get(name) or default


STUDY = _env("SLTP_STUDY", "pm").lower()
if STUDY not in ("pm", "am"): sys.exit("SLTP_STUDY must be pm or am")
# ---------------------------------------------------------------- settings -> the A8_* names the engine reads (must be set BEFORE the engine is imported)
OUT = _env("SLTP_OUT", f"sltp_{STUDY}_results")
os.environ["A8_OUT"] = OUT
os.environ["A8_START"] = _env("SLTP_START", "2024-01-01")
os.environ["A8_END"] = _env("SLTP_END", "2026-10-21")
if os.environ.get("SLTP_SYMBOLS"): os.environ["A8_SYMBOLS"] = os.environ["SLTP_SYMBOLS"]
if os.environ.get("SLTP_CAP"): os.environ["A8_CAP"] = os.environ["SLTP_CAP"]
os.environ["A8_SLS"] = _env("SLTP_SLS", "0,20,40,60")                         # 0 = no stop-loss
os.environ["A8_TPS"] = _env("SLTP_TPS", "60,80,100,120,0")                    # 0 = no target
SPLIT_S = _env("SLTP_SPLIT", "12:00")                                         # pm: first touch at / after this = type 1, before = type 2
AM_FROM_S, AM_TO_S = _env("SLTP_AM_FROM", "09:20"), _env("SLTP_AM_TO", "09:59")
os.environ["A8_ENTRY_LAST"] = _env("SLTP_ENTRY_LAST", "15:20") if STUDY == "pm" else AM_TO_S
os.environ["A8_MIN_TRADES"] = _env("SLTP_MIN_TRADES", "30")
os.environ["A8_TRADES_ALL"] = "1"                                             # every trade of every variant, one file per strategy
os.environ["A8_SUM_ENTRY_FROM"] = os.environ["A8_SUM_ENTRY_TO"] = ""
N_ABOVE = int(_env("SLTP_ABOVE", "5"))                                        # consecutive 1-minute closes above the level before the entry candle
BAND_PCT = float(_env("SLTP_BAND_PCT", "0"))                                  # optional band: a close counts as "above" only when this far above the level (default none)
BAND = BAND_PCT / 100.0

import numpy as np, pandas as pd
import all8_backtest as A
import sltp_rules as R
C = A.C

SPLIT, AM_FROM, AM_TO = R.hm_to_min(SPLIT_S), R.hm_to_min(AM_FROM_S), R.hm_to_min(AM_TO_S)
if STUDY == "pm":
    TEXITS = ["15:00", "15:30"]
    STRAT_RULE = {"BPB_SHORT_T1_FIRST_TOUCH": f"T1 first touch of the day at/after {SPLIT_S}",
                  "BPB_SHORT_T2_RECROSS": f"T2 first touch before {SPLIT_S}, re-cross after {N_ABOVE} closes above, from {SPLIT_S}",
                  "BPB_SHORT_T1_T2_COMBINED": "T1 or T2 (one trade per signal day)"}
else:
    TEXITS = ["10:00"]
    STRAT_RULE = {"BPB_SHORT_AM_RECROSS": f"re-cross after {N_ABOVE} closes above, {AM_FROM_S}-{AM_TO_S}",
                  "WRU_SHORT_AM_RECROSS": f"re-cross after {N_ABOVE} closes above, {AM_FROM_S}-{AM_TO_S}"}
STRATS = list(STRAT_RULE)
_LOCK = threading.Lock()


# ---------------------------------------------------------------- the entry rule used by the engine
def _log(u, level, typ, k, k0):
    """entry_log.csv: one line per entry found (merged into the entries files later on date + entry minute + level)."""
    os.makedirs(A.OUT, exist_ok=True)
    lp = f"{A.OUT}/entry_log.csv"
    t = lambda i: u.index[i].strftime("%H:%M")
    with _LOCK:
        new = not os.path.exists(lp)
        with open(lp, "a") as fh:
            if new: fh.write("date,entry_minute,ref,type,first_touch_time\n")
            fh.write(f"{u.index[k].strftime('%Y-%m-%d')},{t(k)},{level:.2f},{typ},{t(k0) if k0 is not None else ''}\n")


def entries_for(u, level, long):
    """Replaces combo_dayrisk_backtest.entries_for.  SHORT only.  -> {entry type: entry timestamp}"""
    if long or u is None or len(u) == 0: return {}
    last = A.ENTRY_MIN
    k0 = R.day_first_touch(u, level)
    if k0 is None: return {}
    found = {}
    if STUDY == "pm":
        k = R.afternoon_first_touch(u, level, SPLIT, last)
        if k is not None: found["PM_T1"] = k
        k = R.afternoon_recross(u, level, SPLIT, last, N_ABOVE, BAND)
        if k is not None: found["PM_T2"] = k
    else:
        k = R.recross_entry(u, level, AM_FROM, min(AM_TO, last), N_ABOVE, BAND)
        if k is not None: found["AM_RC"] = k
    for typ, k in found.items(): _log(u, level, typ, k, k0)
    return {typ: u.index[k] for typ, k in found.items()}


def strategies_for(source, typ, green, red, up, lo):
    """Replaces all8_backtest.strategies_for: which strategies an entry belongs to."""
    if STUDY == "pm":
        if source != "BPB": return []
        if typ == "PM_T1": return ["BPB_SHORT_T1_FIRST_TOUCH", "BPB_SHORT_T1_T2_COMBINED"]
        if typ == "PM_T2": return ["BPB_SHORT_T2_RECROSS", "BPB_SHORT_T1_T2_COMBINED"]
        return []
    if typ != "AM_RC": return []
    if source == "BPB": return ["BPB_SHORT_AM_RECROSS"]
    if source == "SHAPE" and red == 1 and up == 1: return ["WRU_SHORT_AM_RECROSS"]                  # WRU = red signal candle, upper wick longer
    return []


def install():
    C.entries_for = entries_for
    A.strategies_for = strategies_for
    A.STRATS = list(STRATS)
    A.ENTRY_TYPE = {s: STRAT_RULE[s] for s in STRATS}
    A.TEXITS = list(TEXITS)
    A.EXITS = list(A.TEXITS)                                                  # time exits only, no UNTIL_HIT
    A.VARS = [(ex, sl, tp) for ex in A.EXITS for sl in A.SLS for tp in A.TPS]


install()


def rule_dict():
    return dict(study=STUDY, split=SPLIT_S, am_from=AM_FROM_S, am_to=AM_TO_S, n_above=N_ABOVE, band_pct=BAND_PCT, entry_last=A.ENTRY_LAST, start=A.START, end=A.END,
                sls=A.SLS, tps=A.TPS, exits=A.EXITS, cap=A.CAP, strategies=STRATS)


def rules_text():
    if STUDY == "pm":
        return (f"AFTERNOON study, SHORT, BPB.  T1: the day's first touch of the level is at/after {SPLIT_S} -> enter on it.  T2: the first touch was before {SPLIT_S} -> from {SPLIT_S} on, "
                f"enter on the first candle that touches the level after >= {N_ABOVE} consecutive 1-minute closes above it (no missing minute).  Entries up to {A.ENTRY_LAST}.")
    return (f"MORNING study, SHORT, BPB and WRU.  Enter on the first candle from {AM_FROM_S} to {min(AM_TO_S, A.ENTRY_LAST)} that touches the level after >= {N_ABOVE} consecutive 1-minute "
            f"closes above it (no missing minute).")


def print_rules():
    print(rules_text(), flush=True)
    print(f"Grid: stop-loss {A.SLS} (0 = none) x target {A.TPS} (0 = none) x time exit {A.EXITS} = {len(A.VARS)} variants per strategy; strategies {STRATS}; "
          f"{A.START} .. {A.END}; cap Rs {A.CAP}", flush=True)


# ---------------------------------------------------------------- candidates (daily setups): reuse a saved file of the same engine when it covers the dates
KNOWN = ("all8_results/candidates_*.csv", "recross10*_results/candidates_*.csv", "sltp_*_results/candidates_*.csv")
NEED = {"source", "stock", "direction", "ref", "signal_date", "date", "yahoo_open", "green", "red", "upper_longer", "lower_longer"}


def saved_candidates():
    best = None
    for pat in KNOWN:
        for f in glob.glob(pat):
            mt = re.search(r"candidates_(\d{4}-\d\d-\d\d)_(\d{4}-\d\d-\d\d)\.csv$", f)
            if not mt or not (mt.group(1) <= A.START and mt.group(2) >= A.END): continue
            if not NEED <= set(pd.read_csv(f, nrows=1).columns): continue
            span = (pd.Timestamp(mt.group(2)) - pd.Timestamp(mt.group(1))).days
            if best is None or span < best[0]: best = (span, f)
    return best[1] if best else None


def pick(cand):
    c = cand[(cand.direction == "SHORT") & cand.source.isin(["BPB", "SHAPE"])]
    if STUDY == "pm": c = c[c.source == "BPB"]
    else: c = c[(c.source == "BPB") | ((c.source == "SHAPE") & (c.red == 1) & (c.upper_longer == 1))]
    return c[(c.date >= A.START) & (c.date <= A.END)].reset_index(drop=True)


def get_candidates():
    cp = f"{A.OUT}/candidates_{A.START}_{A.END}.csv"
    if os.path.exists(cp): return pd.read_csv(cp)
    old = saved_candidates()
    if old:
        cand = pd.read_csv(old); print(f"daily candidates reused from {old}", flush=True)
    else:
        cand = C.yahoo_candidates()
    cand = pick(cand)
    cand.to_csv(cp, index=False)
    return cand


def run():
    os.makedirs(A.OUT, exist_ok=True)
    rp = f"{A.OUT}/rule.json"; rule = json.loads(json.dumps(rule_dict()))
    if os.path.exists(rp):
        old = json.load(open(rp))
        if old != rule:
            sys.exit("STOP - the saved data in " + A.OUT + " was made with other settings:\n  saved: " + json.dumps(old) + "\n  now:   " + json.dumps(rule) +
                     "\nUse the same settings, or give SLTP_OUT / the 'out_dir' box another folder name.")
    json.dump(rule, open(rp, "w"), indent=1)
    print_rules()
    st = A.load_state(); dh = A.Dhan(); mst = A.load_master()
    try:
        cand = get_candidates()
        if cand.empty: print("No candidate days in this range."); return
        print(f"Candidate days {A.START}..{A.END}: {len(cand)} ({', '.join(f'{k} = {v}' for k, v in cand.groupby('source').size().items())})", flush=True)
        ev = A.step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= A.START) & (ev["date"] <= A.END)] if len(ev) else ev
        print(f"Entries: {len(ev)}" + (f"  ({', '.join(f'{k} = {v}' for k, v in ev.groupby('strategy').size().items())})" if len(ev) else ""), flush=True)
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
    """rows strategy / exit / stop-loss, columns target."""
    P = S.pivot_table(index=["strategy", "exit_rule", "sl"], columns="tp", values=metric, aggfunc="first")
    P = P.reindex(columns=[t for t in tp_order() if t in P.columns])
    P.columns = [label_tp(t) for t in P.columns]
    P = P.reset_index(); P.insert(3, "stop_loss", P.sl.map(label_sl)); P = P.drop(columns="sl")
    return P


def read_entries():
    """One row per entry (variant independent): the event + its option record + the first-touch time from entry_log.csv."""
    ep = f"{A.OUT}/events.csv"; recs = A.load_records()
    if recs.empty or not os.path.exists(ep): return pd.DataFrame()
    ev = pd.read_csv(ep, dtype={"entry_minute": str}); ev["ekey"] = ev.stock + "|" + ev.direction + "|" + ev.date + "|" + ev.entry_minute
    E = ev.merge(recs[["ekey", "strike", "expiry", "entry_price", "lot", "cov"]], on="ekey", how="left")
    lg = f"{A.OUT}/entry_log.csv"
    if os.path.exists(lg):
        L = pd.read_csv(lg, dtype={"entry_minute": str, "first_touch_time": str}).rename(columns={"type": "log_type"})
        L["ref"] = L.ref.round(2); E["ref"] = E.ref.round(2)
        L = L.drop_duplicates(["date", "entry_minute", "ref"], keep="first")
        E = E.merge(L[["date", "entry_minute", "ref", "first_touch_time"]], on=["date", "entry_minute", "ref"], how="left")
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
        sub = E[E.strategy == s][["stock", "date", "entry_minute", "ref", "first_touch_time"]].rename(columns={"date": "entry_date", "entry_minute": "entry_time", "ref": "level"}) if len(E) and "first_touch_time" in E.columns else None
        if sub is not None and len(sub): T = T.merge(sub.drop_duplicates(["stock", "entry_date", "entry_time"]), on=["stock", "entry_date", "entry_time"], how="left")
        T.to_csv(f"{A.OUT}/trade_files/{s}_all_variants_trades.csv", index=False)
        B = T[(T.exit_rule == bp.exit_rule) & (T.sl == bp.sl) & (T.tp == bp.tp)]
        B.insert(0, "variant", bp.variant); B.to_csv(f"{A.OUT}/trade_files/{s}_best_trades.csv", index=False)
        if len(E):
            Es = E[E.strategy == s].sort_values(["date", "entry_minute", "stock"])
            Es.drop(columns=[c for c in ("ekey",) if c in Es.columns]).to_csv(f"{A.OUT}/trade_files/{s}_entries.csv", index=False)
        files.append((s, len(B), bp.variant, int(T[["exit_rule", "sl", "tp"]].drop_duplicates().shape[0])))
    cols = ["strategy", "exit_rule", "sl_rule", "tp_rule", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "max_drawdown"]
    ts = pd.read_csv(f"{A.OUT}/trades_summary.csv") if os.path.exists(f"{A.OUT}/trades_summary.csv") else pd.DataFrame()
    prog = open(f"{A.OUT}/PROGRESS.txt").read().strip() if os.path.exists(f"{A.OUT}/PROGRESS.txt") else "(no progress file)"
    L = [f"# SL x TP comparison - {'AFTERNOON (BPB SHORT, entries from ' + SPLIT_S + ')' if STUDY == 'pm' else 'MORNING (BPB SHORT + WRU SHORT, entries ' + AM_FROM_S + '-' + AM_TO_S + ')'}", "",
         f"**Status:** {prog}", "",
         f"**Period (entry dates):** {A.START} to {A.END}  |  **Stocks:** all F&O stocks with Dhan data  |  **Capital per trade:** up to Rs {A.CAP:,} (whole lots), SHORT = ATM put", "",
         "## Entry rule", "", rules_text(), "",
         f"**Grid:** stop-loss {', '.join(label_sl(v) for v in A.SLS)} x target {', '.join(label_tp(v) for v in tp_order())} x time exit {', '.join(A.EXITS)} = {len(A.VARS)} variants per strategy. "
         "Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so trade counts can differ between exits.", ""]
    if len(ts):
        t2 = ts[[c for c in ("strategy", "signals_with_entry", "entries_with_option_data", "dropped_low_coverage", "skipped_no_option_data") if c in ts.columns]]
        L += ["## Entries found", "", md(t2),
              "", "`signals_with_entry` = entries found on the 1-minute stock chart; `skipped_no_option_data` / `dropped_low_coverage` = entries Dhan has no usable option candles for (they are not in any result).", ""]
    for s in STRATS:
        for ex in A.EXITS:
            g = S[(S.strategy == s) & (S.exit_rule == ex)]
            if g.empty: continue
            L += [f"## {s} - exit {ex}", "", f"_{STRAT_RULE[s]}_", ""]
            for metric, title in (("total_pnl", "Total PnL (Rs)"), ("roi_pct", "ROI % on capital used"), ("win_pct", "Win %")):
                M = matrices(g, metric).drop(columns=["strategy", "exit_rule"])
                L += [f"**{title}** (rows stop-loss, columns target)  -  trades per variant: {int(g.trades.min())}-{int(g.trades.max())}", "", md(M), ""]
    if best: L += ["## Best variant of each strategy - by total PnL", "", md(pd.DataFrame(best)[cols]), ""]
    L += [f"## Top 10 variants overall by ROI (at least {A.MIN_TRADES} trades)", "", md(good.sort_values("roi_pct", ascending=False).head(10)[cols]) if len(good) else "(none yet)", "",
          "## Trade files", "",
          "In `trade_files/`: `<STRATEGY>_all_variants_trades.csv` (every trade of every variant - filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none), "
          "`<STRATEGY>_best_trades.csv` (best-PnL variant) and `<STRATEGY>_entries.csv` (one row per entry: level, first-touch time, strike, expiry, option price).", ""]
    L += [f"- `{s}`: best variant {v} - {n} trades; {nv} variants in the all-variants file" for s, n, v, nv in files]
    L += ["", "The best variant is the best of several dozen chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at `summary_by_year_top.csv`; "
          "a grid that is smooth around the winner is more believable than one isolated peak. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. "
          "Past results do not promise future results.", ""]
    open(f"{A.OUT}/SUMMARY.md", "w").write("\n".join(L))
    print("\n".join(L[:8]), flush=True)


def summary():
    try:
        A.summary()
    except ValueError as e:                                                   # too few trades for MIN_TRADES (e.g. a quick test with a few stocks)
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
        else: sys.exit("use: SLTP_STUDY=pm|am python sltp_backtest.py check | run | summary | rules")
    except A.Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
