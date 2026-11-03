"""bpb_base_backtest.py - BPB BASE strategy (10-day-high breakout -> pullback -> entry at the highest price) on ATM options of ALL F&O stocks, LONG (call) and SHORT (put), 3 years, Dhan 1-minute data,
entry checked through the FULL DAY, with the NIFTY50 direction filter.  Same engine as gap_backtest.py / all8_backtest.py (ATM first, ITM-1..3 fallback, next-month series on the expiry day,
entry-day-only option candles, resumable).

  python bpb_base_backtest.py check     test Dhan access + print the rules
  python bpb_base_backtest.py run       full backtest for BB_START .. BB_END (resumable - run again after a polite stop)
  python bpb_base_backtest.py summary   rebuild every result file from the saved option data (no API calls)
  python bpb_base_backtest.py rules     print the rules only
  then  python bpb_base_report.py       NIFTY50 filter (before / after) + survivors after cutting the top 10 % of trades (no API calls; the workflow runs it for you)

SETUP (daily chart, Yahoo; rules in bpb_base_rules.py = your BPB state machine)
  LONG   a daily close above the 10-day rolling high (the LINE) -> later candles must NOT close below the LINE (one bearish candle confirms the pullback) -> entry level = the highest High since the
         breakout -> entry day = the first later day whose High reaches the level.   SHORT = exact mirror (10-day low, no close above the line, lowest Low).   No open-price prefilter.
ENTRY      the first 1-minute candle (09:15 .. BB_ENTRY_LAST = 15:20) of the entry day whose High (SHORT: Low) reaches the level; option price = close of that minute.
NIFTY50    the filter is checked in the ENTRY MINUTE: LONG only when NIFTY50 > its open of the day, SHORT only when NIFTY50 < its open.  It only removes trades, so the engine fetches every entry once and
           bpb_base_report.py gives the numbers with and without the filter.
OPTION     LONG = ATM CALL, SHORT = ATM PUT, nearest monthly expiry (next month's series on the expiry day itself); ITM-1 .. ITM-BB_ITM_MAX if the ATM series has no candle at the entry minute.
EXIT GRID  stop-loss none / 20 / 40 / 60 % x target 60 / 80 / 100 / 120 % / none x time exit 15:00 / 15:30 the same day = 40 variants per direction (percent of the premium).
           Fills: stop / target = first 1-minute low / high touching the level; a gap through it fills at that candle's open; stop and target in the same minute = STOP.
           A trade entered at / after a time exit is skipped for that exit.
CAPITAL    at most Rs BB_CAP (60,000) per trade, whole lots.  Charges, taxes and slippage are not included.  Lot sizes are today's values for all years.

Results in bpb_base_results/ : SUMMARY.md, long/ and short/ (each with its own SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, entries.csv ...).
"""
import os, sys, json, glob


def _env(name, default):
    return os.environ.get(name) or default


# ---------------------------------------------------------------- settings -> the A8_* names the engine reads (must be set BEFORE the engine is imported)
OUT = _env("BB_OUT", "bpb_base_results")
os.environ["A8_OUT"] = OUT
os.environ["A8_START"] = _env("BB_START", "2023-10-30")
os.environ["A8_END"] = _env("BB_END", "2026-10-30")
if os.environ.get("BB_SYMBOLS"): os.environ["A8_SYMBOLS"] = os.environ["BB_SYMBOLS"]
if os.environ.get("BB_CAP"): os.environ["A8_CAP"] = os.environ["BB_CAP"]
os.environ["A8_SLS"] = _env("BB_SLS", "0,20,40,60")                                 # 0 = no stop-loss
os.environ["A8_TPS"] = _env("BB_TPS", "60,80,100,120,0")                            # 0 = no target
os.environ["A8_ENTRY_LAST"] = _env("BB_ENTRY_LAST", "15:20")
os.environ["A8_MIN_TRADES"] = _env("BB_MIN_TRADES", "30")
os.environ["A8_TRADES_ALL"] = "1"                                                # every trade of every variant, one file per strategy
os.environ["A8_SUM_ENTRY_FROM"] = os.environ["A8_SUM_ENTRY_TO"] = ""
LOOKBACK = int(_env("BB_LOOKBACK", "10"))                                        # rolling-high window (days)
ITM_MAX = int(_env("BB_ITM_MAX", "3"))                                           # ATM first, then ITM-1 ... ITM-n (0 = ATM only)
TEXITS = [x.strip() for x in _env("BB_EXITS", "15:00,15:30").replace(" ", ",").split(",") if len(x.strip()) == 5 and x.strip()[2] == ":"]

import numpy as np, pandas as pd
import all8_backtest as A
import gap_rules as GR
import bpb_base_rules as R
C = A.C

STRAT_L, STRAT_S = "BPB_LONG", "BPB_SHORT"
STRAT_RULE = {
    STRAT_L: f"BPB base LONG: close above the {LOOKBACK}-day high, no later close below it (pullback) -> first 1-minute cross above the highest High since the breakout (full day) -> buy CALL",
    STRAT_S: f"BPB base SHORT: close below the {LOOKBACK}-day low, no later close above it (pullback) -> first 1-minute cross below the lowest Low since the breakdown (full day) -> buy PUT"}
STRATS = list(STRAT_RULE)
DIRNAME = {STRAT_L: "long", STRAT_S: "short"}


# ---------------------------------------------------------------- the entry rule used by the engine
def entries_for(u, level, long):
    """Replaces combo_dayrisk_backtest.entries_for.  -> {entry type: entry timestamp}   (BPBL = LONG, BPBS = SHORT); the first 1-minute candle that reaches the level, 09:15 .. entry-last."""
    if u is None or len(u) == 0: return {}
    k = GR.first_cross_long(u, level, A.E_FIRST, A.ENTRY_MIN) if long else GR.first_cross_short(u, level, A.E_FIRST, A.ENTRY_MIN)
    return {} if k is None else {("BPBL" if long else "BPBS"): u.index[k]}


def strategies_for(source, typ, green, red, up, lo):
    if source != "BPB": return []
    return [STRAT_L] if typ == "BPBL" else [STRAT_S] if typ == "BPBS" else []


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


EXPIRY_OF = A.expiry_calc                                                        # the real monthly expiry of a date (kept for the entries file)


NEXT_ON_EXPIRY = _env("BL_EXPIRY_NEXT", "1") != "0"                              # on the monthly expiry day itself use the NEXT month's series (expiryCode 2); fall back to the nearest if it has no data


def _has_data(j):
    d = (j.get("data") or {}) if isinstance(j, dict) else {}
    return any(isinstance(v, dict) and any(isinstance(x, list) and len(x) for x in v.values()) for v in d.values())


class StrictDhan(A.Dhan):
    """A FAILED option request (HTTP 400 / DH-905 ...) must never be stored as 'no option candles': it stops the run politely and the group stays NOT done, so the next run retries it.
    An entry on the monthly expiry day asks for the next month's series first (expiryCode 2); if that comes back empty the nearest month (expiryCode 1) is used, so an entry is never lost to the expiry."""
    def post(self, path, body):
        if NEXT_ON_EXPIRY and "rollingoption" in path:
            try:
                from datetime import date as _d
                fd = _d.fromisoformat(str(body.get("fromDate"))[:10])
                if EXPIRY_OF(fd) == fd:
                    j2 = super().post(path, dict(body, expiryCode=2))
                    if j2 is not None and _has_data(j2): return j2
            except ValueError:
                pass
        j = super().post(path, body)
        if j is None and "rollingoption" in path:
            raise A.Stop(f"Dhan refused an option request ({body.get('fromDate')} .. {body.get('toDate')}, {body.get('strike')}) - see the 'Dhan says' line above; nothing was stored for it")
        return j


def options_step(dh, ev, mst, st):
    """Option candles are fetched PER ENTRY DAY (a 1-day window, 1-3 calls per entry).  Every trade of this study closes on the entry day, so the candles of the entry day are all that is
    needed.  The old 'entry day .. expiry' window (up to 34 days) was refused by Dhan with HTTP 400 DH-905 (only 1-day windows worked: 55 of 55 successes were entries on expiry day)."""
    A.expiry_calc = lambda d: d                                                  # step_options groups by (stock, direction, "expiry") -> now (stock, direction, entry day)
    try: return A.step_options(dh, ev, mst, st)
    finally: A.expiry_calc = EXPIRY_OF


install()


def rule_dict():
    return dict(lookback=LOOKBACK, itm_max=ITM_MAX, entry_last=A.ENTRY_LAST, start=A.START, end=A.END, sls=A.SLS, tps=A.TPS, exits=A.EXITS, cap=A.CAP, symbols=len(A.UNIVERSE))


def rules_text():
    return (f"BPB BASE.  LONG (ATM call): a daily close above the {LOOKBACK}-day high (the line); later candles must not close below the line (a bearish candle confirms the pullback); entry level = the highest "
            f"High since the breakout; entry = the first 1-minute candle (09:15 to {A.ENTRY_LAST}) of a later day whose High reaches the level.  SHORT (ATM put) = mirror (close below the {LOOKBACK}-day low, "
            f"lowest Low, first minute whose Low reaches it).  Option = ATM of the entry day's month, ITM-1 .. ITM-{ITM_MAX} if the ATM series has no candle at the entry minute.  NIFTY50 filter (report): LONG "
            f"only when NIFTY50 > its day open at the entry minute, SHORT only when it is below.")


def print_rules():
    print(rules_text(), flush=True)
    print(f"Grid: stop-loss {A.SLS} (0 = none) x target {A.TPS} (0 = none) x time exit {A.EXITS} = {len(A.VARS)} variants per direction; {len(A.UNIVERSE)} stocks; {A.START} .. {A.END}; cap Rs {A.CAP}", flush=True)


# ---------------------------------------------------------------- step 1: daily candidates (Yahoo)
def setups_to_rows(stock, dates, O, H, L, C_, t0, t1):
    """One candidate per BPB setup and direction: the entry day (first day after the confirmed pullback whose High / Low reaches the level).  No open-price prefilter; the exact minute check on Dhan decides the entry."""
    rows = []
    for long in (True, False):
        for s in R.bpb_setups(O, H, L, C_, long, LOOKBACK):
            i = s["entry"]
            if not (t0 <= pd.Timestamp(dates[i]) <= t1): continue
            rows.append(dict(source="BPB", stock=stock, direction="LONG" if long else "SHORT", ref=round(s["level"], 2), signal_date=dates[s["breakout"]], date=dates[i], yahoo_open=float(O[i]),
                             green=-1, red=-1, upper_longer=-1, lower_longer=-1, line=round(s["line"], 2)))
    return rows


def yahoo_candidates():
    import yfinance as yf
    t0, t1 = pd.Timestamp(A.START), pd.Timestamp(A.END)
    raw = yf.download([s + ".NS" for s in A.UNIVERSE], start=str((t0 - pd.Timedelta(days=200)).date()), end=str((t1 + pd.Timedelta(days=5)).date()),
                      group_by="ticker", auto_adjust=False, progress=False, threads=True)
    rows, nst = [], 0
    for s in A.UNIVERSE:
        try: d = raw[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
        if len(d) < LOOKBACK + 30: continue
        nst += 1
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        O, H, L, C_ = (d[k].values.astype(float) for k in ("Open", "High", "Low", "Close"))
        rows += setups_to_rows(s, d.index.strftime("%Y-%m-%d"), O, H, L, C_, t0, t1)
    if nst == 0: raise A.Fatal("Yahoo download gave no data for any stock - run again later")
    r = pd.DataFrame(rows)
    nl = int((r.direction == "LONG").sum()) if len(r) else 0
    print(f"Yahoo: {nst} stocks, {nl} LONG + {len(r) - nl} SHORT BPB setups with an entry day in {A.START}..{A.END}", flush=True)
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
                     "\nUse the same settings, or give BB_OUT / the 'out_dir' box another folder name.")
    json.dump(rule, open(rp, "w"), indent=1)
    print_rules()
    st = A.load_state(); dh = StrictDhan(); mst = A.load_master()
    try:
        cand = get_candidates()
        if cand.empty: print("No candidate days in this range."); return
        print(f"Candidate entry days {A.START}..{A.END}: {len(cand)}", flush=True)
        ev = A.step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= A.START) & (ev["date"] <= A.END)] if len(ev) else ev
        print(f"Entries (09:15-{A.ENTRY_LAST}): {len(ev)}", flush=True)
        if len(ev): options_step(dh, ev, mst, st)
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
    """One row per entry: the event + its option record + the gap info from the candidates file."""
    ep = f"{A.OUT}/events.csv"; recs = A.load_records()
    if recs.empty or not os.path.exists(ep): return pd.DataFrame()
    ev = pd.read_csv(ep, dtype={"entry_minute": str}); ev["ekey"] = ev.stock + "|" + ev.direction + "|" + ev.date + "|" + ev.entry_minute
    E = ev.merge(recs[[c for c in ("ekey", "strike", "expiry", "entry_price", "lot", "cov", "strike_offset") if c in recs.columns]], on="ekey", how="left")
    from datetime import date as _d
    E["expiry"] = E.date.map(lambda x: str(EXPIRY_OF(_d.fromisoformat(x))))                   # the stored 'expiry' is the entry day (1-day window); show the real monthly expiry
    cps = sorted(glob.glob(f"{A.OUT}/candidates_*.csv"))
    if cps and "gap_pct" in pd.read_csv(cps[-1], nrows=1).columns:
        cd = pd.read_csv(cps[-1])[["stock", "direction", "date", "gap_pct", "day_offset"]].drop_duplicates(["stock", "direction", "date"])
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
            keep = [c for c in ("stock", "entry_date", "entry_time", "level", "gap_pct", "day_offset", "strike_offset") if c in sub.columns]
            T = T.merge(sub[keep].drop_duplicates(["stock", "entry_date", "entry_time"]), on=["stock", "entry_date", "entry_time"], how="left")
        T.to_csv(f"{d}/trades_all_variants.csv.gz", index=False); nT = len(T)
        B = T[(T.exit_rule == bp.exit_rule) & (T.sl == bp.sl) & (T.tp == bp.tp)]
        B.insert(0, "variant", bp.variant); B.to_csv(f"{d}/trades_best_variant.csv", index=False); nB = len(B)
    if len(E):
        E[E.strategy == strat].sort_values(["date", "entry_minute", "stock"]).drop(columns=["ekey"]).to_csv(f"{d}/entries.csv", index=False)
    ts = pd.read_csv(f"{A.OUT}/trades_summary.csv") if os.path.exists(f"{A.OUT}/trades_summary.csv") else pd.DataFrame()
    L = [f"# BPB BASE - {DIRNAME[strat].upper()} ({'ATM call' if strat == STRAT_L else 'ATM put'}) - SL x TP x time-exit grid, entry checked all day", "",
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
          "`entries.csv` (one row per entry: level, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.", "",
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
    L = ["# BPB BASE (LONG call + SHORT put) - SL x TP x time-exit grid, entry checked all day", "",
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
        L += [f"## {DIRNAME[s].upper()} ({s}) - top 10 by ROI (at least {A.MIN_TRADES} trades)", "", md(gg.sort_values("roi_pct", ascending=False).head(10)[cols]) if len(gg) else "(none yet)", ""]
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
        else: sys.exit("use: python bpb_base_backtest.py check | run | summary | rules")
    except A.Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
