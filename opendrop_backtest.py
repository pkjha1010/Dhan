"""opendrop_backtest.py - OPEN-DROP RETEST, LONG (call) on ALL F&O stock options, 1 year, Dhan 1-minute data.  Same engine as gap_backtest.py / all8_backtest.py.
Your Nifty-50 stock backtest (Yahoo hourly, +2 % stock target, no stop-loss) tested on the real ATM / ITM options of every F&O stock.

  python opendrop_backtest.py check     test Dhan access + print the rules
  python opendrop_backtest.py run       full backtest for OD_START .. OD_END (resumable - run again after a polite stop)
  python opendrop_backtest.py summary   rebuild every result file from the saved option data (no API calls)
  python opendrop_backtest.py rules     print the rules only

SETUP (Yahoo HOURLY candles, rules in opendrop_rules.py; same as your original script)
  SETUP DAY i  the first hourly candle (09:15-10:15) is red and falls more than OD_DROP (1 %) from open to close; op_close = its close.  NIFTY50 filter: the NIFTY50 hourly slope
               (20 candles, value at the first hourly candle of day i, same formula as your script) must be >= OD_MIN_SLOPE (-0.5; 'off' = no filter).
  DROP DAY     first day among i+1 .. i+3 that trades at or below op_close x 0.99.
  ENTRY DAY    first day among drop_day+1 .. drop_day+5 that trades at or above op_close  ->  LONG: buy the ATM CALL.
ENTRY      the first 1-minute candle (09:15 .. 15:20) of the entry day whose High >= op_close (a gap through it = 09:15); the option price = close of that entry minute.
OPTION     ATM CALL of the nearest monthly expiry (on the monthly expiry day itself the NEXT month's series is used; nearest month if that has no data).  If the ATM series has no candle at the entry
           minute: ITM-1, ITM-2 ... ITM-OD_ITM_MAX (a call's ITM = lower strike).  Candles are fetched for the entry day only.  The strike used is stored per trade (strike_offset: 0 = ATM, -n = ITM-n).
EXIT GRID  stop-loss none / 20 / 40 / 60 % x target 40 / 60 / 80 / 120 % / none x time exit 09:30 / 10:00 / 12:00 / 15:00 / 15:30 the same day = 100 variants (percent of the premium).
           Fills: stop / target = first 1-minute low / high touching the level; a gap through it fills at that candle's open; stop and target in the same minute = STOP.
           A trade entered at / after a time exit is skipped for that exit (so the 09:30 / 10:00 / 12:00 exits only have the earlier entries).
CAPITAL    at most Rs OD_CAP (60,000) per trade, whole lots.  Charges, taxes and slippage are not included.  Lot sizes are today's values for the whole year.
ONE TRADE PER STOCK PER ENTRY DAY (engine rule): if two setup days of the same stock reach their entry on the same day, the earlier setup is kept.

Results in opendrop_results/ : SUMMARY.md and long/ (SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv, entries.csv).
"""
import os, sys, json, glob


def _env(name, default):
    return os.environ.get(name) or default


# ---------------------------------------------------------------- settings -> the A8_* names the engine reads (must be set BEFORE the engine is imported)
OUT = _env("OD_OUT", "opendrop_results")
os.environ["A8_OUT"] = OUT
os.environ["A8_START"] = _env("OD_START", "2025-11-12")
os.environ["A8_END"] = _env("OD_END", "2026-11-12")
if os.environ.get("OD_SYMBOLS"): os.environ["A8_SYMBOLS"] = os.environ["OD_SYMBOLS"]
if os.environ.get("OD_CAP"): os.environ["A8_CAP"] = os.environ["OD_CAP"]
os.environ["A8_SLS"] = _env("OD_SLS", "0,20,40,60")                                 # 0 = no stop-loss
os.environ["A8_TPS"] = _env("OD_TPS", "40,60,80,120,0")                             # 0 = no target
os.environ["A8_ENTRY_LAST"] = _env("OD_ENTRY_LAST", "15:20")
os.environ["A8_MIN_TRADES"] = _env("OD_MIN_TRADES", "30")
os.environ["A8_TRADES_ALL"] = "1"                                                # every trade of every variant, one file per strategy
os.environ["A8_SUM_ENTRY_FROM"] = os.environ["A8_SUM_ENTRY_TO"] = ""
DROP = float(_env("OD_DROP", "1")) / 100.0                                       # first hourly candle must fall MORE than this (1 = 1 %)
FALL = float(_env("OD_FALL", "1")) / 100.0                                       # later day must trade at or below op_close x (1 - FALL)
FALL_DAYS = int(_env("OD_FALL_DAYS", "3"))                                       # drop day = first of setup day + 1 .. + FALL_DAYS
ENTRY_DAYS = int(_env("OD_ENTRY_DAYS", "5"))                                     # entry day = first of drop day + 1 .. + ENTRY_DAYS
TAIL = int(_env("OD_TAIL", "8"))                                                 # original: setup days only in range(len(days) - 8)
SLOPE_N = int(_env("OD_SLOPE_N", "20"))                                          # NIFTY50 slope window (hourly candles)
_ms = _env("OD_MIN_SLOPE", "-0.5").strip().lower()
MIN_SLOPE = None if _ms in ("off", "none", "no") else float(_ms)                  # None = no NIFTY filter
ITM_MAX = int(_env("OD_ITM_MAX", "3"))                                           # ATM first, then ITM-1 ... ITM-n (0 = ATM only)
TEXITS = [x.strip() for x in _env("OD_EXITS", "09:30,10:00,12:00,15:00,15:30").replace(" ", ",").split(",") if len(x.strip()) == 5 and x.strip()[2] == ":"]

import numpy as np, pandas as pd
import all8_backtest as A
import gap_rules as GR
import opendrop_rules as R
C = A.C

STRAT_L = "OPENDROP_LONG"
STRAT_RULE = {STRAT_L: (f"first hourly candle falls > {DROP*100:g}% (red) on day i -> a day i+1..i+{FALL_DAYS} trades <= {FALL*100:g}% below its close -> first cross above that close on the next "
                        f"1..{ENTRY_DAYS} days (1-minute) -> buy CALL" + (f"; NIFTY50 hourly slope >= {MIN_SLOPE:g} on day i" if MIN_SLOPE is not None else ""))}
STRATS = list(STRAT_RULE)
DIRNAME = {STRAT_L: "long"}
_COLS = ["Open", "High", "Low", "Close"]


# ---------------------------------------------------------------- the entry rule used by the engine
def entries_for(u, level, long):
    """Replaces combo_dayrisk_backtest.entries_for.  -> {entry type: entry timestamp}   (ODL = LONG); the first 1-minute candle that reaches the level, 09:15 .. entry-last."""
    if u is None or len(u) == 0 or not long: return {}
    k = GR.first_cross_long(u, level, A.E_FIRST, A.ENTRY_MIN)
    return {} if k is None else {"ODL": u.index[k]}


def strategies_for(source, typ, green, red, up, lo):
    return [STRAT_L] if (source == "OD" and typ == "ODL") else []


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
NEXT_ON_EXPIRY = _env("OD_EXPIRY_NEXT", "1") != "0"                              # on the monthly expiry day itself use the NEXT month's series (expiryCode 2); fall back to the nearest if it has no data


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
    """Option candles are fetched PER ENTRY DAY (a 1-day window, 1-3 calls per entry).  Every trade of this study closes on the entry day, so the candles of the entry day are all that is needed."""
    A.expiry_calc = lambda d: d                                                  # step_options groups by (stock, direction, "expiry") -> now (stock, direction, entry day)
    try: return A.step_options(dh, ev, mst, st)
    finally: A.expiry_calc = EXPIRY_OF


install()


def rule_dict():
    return dict(drop=DROP, fall=FALL, fall_days=FALL_DAYS, entry_days=ENTRY_DAYS, tail=TAIL, min_slope=MIN_SLOPE, slope_n=SLOPE_N, itm_max=ITM_MAX, entry_last=A.ENTRY_LAST,
                start=A.START, end=A.END, sls=A.SLS, tps=A.TPS, exits=A.EXITS, cap=A.CAP, symbols=len(A.UNIVERSE))


def rules_text():
    return (f"OPEN-DROP RETEST (LONG, ATM call).  Setup day i: the first hourly candle (09:15-10:15) is red and falls more than {DROP*100:g}% (open to close); its close is the LEVEL.  "
            f"Drop day: the first day among i+1..i+{FALL_DAYS} that trades at or below {FALL*100:g}% under the level.  Entry day: the first day among drop day+1..+{ENTRY_DAYS} that trades at or above the level; "
            f"entry = the first 1-minute candle (09:15 to {A.ENTRY_LAST}) whose High reaches the level.  " +
            (f"NIFTY50 filter: the NIFTY50 hourly slope ({SLOPE_N} candles, at the first hourly candle of day i) must be >= {MIN_SLOPE:g}.  " if MIN_SLOPE is not None else "No NIFTY50 filter.  ") +
            f"Option = ATM of the entry day's month, ITM-1 .. ITM-{ITM_MAX} if the ATM series has no candle at the entry minute (the entry is never skipped for a missing option candle while any of these strikes has one).")


def print_rules():
    print(rules_text(), flush=True)
    print(f"Grid: stop-loss {A.SLS} (0 = none) x target {A.TPS} (0 = none) x time exit {A.EXITS} = {len(A.VARS)} variants; {len(A.UNIVERSE)} stocks; {A.START} .. {A.END}; cap Rs {A.CAP}", flush=True)


# ---------------------------------------------------------------- step 1: daily candidates (Yahoo hourly)
def _ist(df):
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df[_COLS].dropna().copy()
    df.index = pd.DatetimeIndex(df.index)
    df.index = df.index.tz_convert("Asia/Kolkata") if df.index.tz is not None else df.index.tz_localize("UTC").tz_convert("Asia/Kolkata")
    return df.sort_index()


def setups_to_rows(stock, day, allowed, t0, t1):
    """One candidate per setup whose entry day is in t0..t1: the first Yahoo day whose High reaches the level.  The exact minute check on Dhan decides the real entry.
    Two setups of one stock with the same entry day -> only the first (earlier setup day) is kept (the engine keeps one trade per stock per day)."""
    rows, seen, dup = [], set(), 0
    for s in R.open_drop_setups(day, allowed, DROP, FALL, FALL_DAYS, ENTRY_DAYS, TAIL):
        e = s["entry"]; d = str(day["date"][e])
        if not (t0 <= pd.Timestamp(d) <= t1): continue
        if d in seen: dup += 1; continue
        seen.add(d)
        rows.append(dict(source="OD", stock=stock, direction="LONG", ref=round(s["level"], 2), signal_date=str(day["date"][s["signal"]]), date=d, yahoo_open=float(day["fo"][e]),
                         green=-1, red=-1, upper_longer=-1, lower_longer=-1, drop_date=str(day["date"][s["drop_day"]]), drop_pct=round(s["drop_pct"] * 100, 2), day_offset=int(e - s["signal"])))
    return rows, dup


def yahoo_candidates():
    import yfinance as yf
    t0, t1 = pd.Timestamp(A.START), pd.Timestamp(A.END)
    ds = str((t0 - pd.Timedelta(days=60)).date()); de = str((t1 + pd.Timedelta(days=5)).date())
    allowed_days = None
    if MIN_SLOPE is not None:
        nf = yf.download("^NSEI", start=ds, end=de, interval="1h", auto_adjust=False, progress=False)
        if nf is None or nf.empty: raise A.Fatal("Yahoo gave no NIFTY50 hourly data (^NSEI) - run again later, or set the NIFTY filter to 'off'")
        nf = _ist(nf)
        allowed_days = R.nifty_allowed_days(nf.index.strftime("%Y-%m-%d"), nf.Close.values, SLOPE_N, MIN_SLOPE)
        print(f"NIFTY50 hourly: {len(nf)} candles, {nf.index.normalize().nunique()} days, {len(allowed_days)} days with slope >= {MIN_SLOPE:g}", flush=True)
    rows, nst, dups, ndays_f = [], 0, 0, 0
    names = list(A.UNIVERSE)
    for b in range(0, len(names), 40):
        batch = names[b:b + 40]
        raw = yf.download([s + ".NS" for s in batch], start=ds, end=de, interval="1h", group_by="ticker", auto_adjust=False, progress=False, threads=True)
        for s in batch:
            try: d = raw[s + ".NS"][_COLS].dropna()
            except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
            if len(d) < 30: continue
            nst += 1
            day = R.daily_from_hourly(_ist(d))
            allowed = None if allowed_days is None else np.array([x in allowed_days for x in day["date"]])
            r, du = setups_to_rows(s, day, allowed, t0, t1)
            rows += r; dups += du
        print(f"Yahoo hourly: {min(b + 40, len(names))} / {len(names)} stocks done, {len(rows)} setups so far", flush=True)
    if nst == 0: raise A.Fatal("Yahoo download gave no data for any stock - run again later")
    r = pd.DataFrame(rows)
    if len(r): r = r.sort_values(["stock", "date", "signal_date"]).reset_index(drop=True)
    print(f"Yahoo: {nst} stocks, {len(r)} setups with an entry day in {A.START}..{A.END} ({dups} dropped: same stock + same entry day as an earlier setup)", flush=True)
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
                     "\nUse the same settings, or give OD_OUT / the 'out_dir' box another folder name.")
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
    """One row per entry: the event + its option record + the setup info from the candidates file."""
    ep = f"{A.OUT}/events.csv"; recs = A.load_records()
    if recs.empty or not os.path.exists(ep): return pd.DataFrame()
    ev = pd.read_csv(ep, dtype={"entry_minute": str}); ev["ekey"] = ev.stock + "|" + ev.direction + "|" + ev.date + "|" + ev.entry_minute
    E = ev.merge(recs[[c for c in ("ekey", "strike", "expiry", "entry_price", "lot", "cov", "strike_offset") if c in recs.columns]], on="ekey", how="left")
    from datetime import date as _d
    E["expiry"] = E.date.map(lambda x: str(EXPIRY_OF(_d.fromisoformat(x))))                   # the stored 'expiry' is the entry day (1-day window); show the real monthly expiry
    cps = sorted(glob.glob(f"{A.OUT}/candidates_*.csv"))
    if cps and "drop_pct" in pd.read_csv(cps[-1], nrows=1).columns:
        cd = pd.read_csv(cps[-1])[["stock", "direction", "date", "drop_date", "drop_pct", "day_offset"]].drop_duplicates(["stock", "direction", "date"])
        E = E.merge(cd, on=["stock", "direction", "date"], how="left")
    return E


def write_direction(strat, S, E, base, cols, prog):
    """Everything for the LONG direction into OUT/long/ ; returns the best row (or None)."""
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
            keep = [c for c in ("stock", "entry_date", "entry_time", "level", "signal_date", "drop_date", "drop_pct", "day_offset", "strike_offset") if c in sub.columns]
            T = T.merge(sub[keep].drop_duplicates(["stock", "entry_date", "entry_time"]), on=["stock", "entry_date", "entry_time"], how="left")
        T.to_csv(f"{d}/trades_all_variants.csv.gz", index=False); nT = len(T)
        B = T[(T.exit_rule == bp.exit_rule) & (T.sl == bp.sl) & (T.tp == bp.tp)]
        B.insert(0, "variant", bp.variant); B.to_csv(f"{d}/trades_best_variant.csv", index=False); nB = len(B)
    if len(E):
        E[E.strategy == strat].sort_values(["date", "entry_minute", "stock"]).drop(columns=["ekey"]).to_csv(f"{d}/entries.csv", index=False)
    ts = pd.read_csv(f"{A.OUT}/trades_summary.csv") if os.path.exists(f"{A.OUT}/trades_summary.csv") else pd.DataFrame()
    L = [f"# OPEN-DROP RETEST - LONG (ATM call) - SL x TP x time-exit grid", "",
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
        L += ["## Strike used", "", "strike_offset 0 = ATM, -n = ITM-n (the ATM series had no candle at the entry minute): " + ", ".join(f"{int(k)}: {int(v)}" for k, v in vc.items()), ""]
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
          "`entries.csv` (one row per entry: level, setup / drop day, first-candle drop %, strike, expiry, option price), `summary.csv`, `matrix_*.csv`.", "",
          "The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours (next stop-loss / target) and at the other exits. "
          "Charges, taxes and slippage are not included. Lot sizes are today's values for the whole year. The stock list is today's F&O list (stocks that left F&O are missing). "
          "Past results do not promise future results.", ""]
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
    L = ["# OPEN-DROP RETEST (LONG call) - SL x TP x time-exit grid", "",
         f"**Status:** {prog}", "",
         f"**Period (entry dates):** {A.START} to {A.END}  |  **Stocks:** all F&O stocks with Dhan data ({len(A.UNIVERSE)} tried)  |  **Capital per trade:** up to Rs {A.CAP:,} (whole lots)", "",
         "## Rules", "", rules_text(), "",
         "Everything is in `long/`: SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv and entries.csv.", ""]
    ts = pd.read_csv(f"{A.OUT}/trades_summary.csv") if os.path.exists(f"{A.OUT}/trades_summary.csv") else pd.DataFrame()
    if len(ts):
        L += ["## Entries found", "", md(ts[[c for c in ("strategy", "signals_with_entry", "entries_with_option_data", "dropped_low_coverage", "skipped_no_option_data", "skip_reasons") if c in ts.columns]]), ""]
    if best: L += ["## Best variant by total PnL", "", md(pd.DataFrame(best)[cols]), ""]
    for s in STRATS:
        gg = base[base.strategy == s]
        L += [f"## Top 10 by ROI (at least {A.MIN_TRADES} trades)", "", md(gg.sort_values("roi_pct", ascending=False).head(10)[cols]) if len(gg) else "(none yet)", ""]
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
        else: sys.exit("use: python opendrop_backtest.py check | run | summary | rules")
    except A.Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
