"""bpb_bb_backtest.py - YOUR "PURE BREAKOUT STRATEGY (LONG & SHORT)" script (5-day-high breakout, no pullback, entry at the breakout day's High, previous-day Bollinger filter) on ATM options of ALL F&O
stocks, LONG (call) and SHORT (put), 3 years, Dhan 1-minute data, entry checked through the FULL DAY, nothing skipped on purpose.  Same engine as bpb_base_backtest.py / gap_backtest.py / all8_backtest.py
(ATM first, ITM-1..3 fallback, next-month series on the expiry day, entry-day-only option candles, resumable).

  python bpb_bb_backtest.py check     test Dhan access + print the rules
  python bpb_bb_backtest.py run       full backtest for BBB_START .. BBB_END (resumable - run again after a polite stop)
  python bpb_bb_backtest.py summary   rebuild every result file from the saved option data (no API calls)
  python bpb_bb_backtest.py rules     print the rules only
  then  python bpb_bb_report.py       LONG and SHORT reports per entry rule and per B+n (no API calls; the workflow runs it for you)

B = THE BREAKOUT DAY.  B+1 = the next trading day, B+2 = the day after ...  Every entry carries its B+n ('b_plus' = n, 'b_label' = 'B+n', 'breakout_date' = the date of B) in every file.

SETUP (daily chart, Yahoo; rules + the proof against your loop in bpb_bb_rules.py / test_bpb_bb.py)
  LONG   close above High_5 (highest High of the previous 5 days) = breakout day B -> line = that High_5, ENTRY LEVEL = the High of B -> a later close below the line cancels the setup -> entry day = the first
         day B+m (m >= FIRST_DAY) whose High reaches the level; the setup is used up on that touch.  Bollinger filter: the CLOSE OF THE DAY BEFORE the entry day above that day's upper band (20, 2 std).
         SHORT = exact mirror (5-day low, level = Low of B, previous close below the lower band).   No open-price prefilter.   Your script = FIRST_DAY 3 (see bpb_bb_rules.py: its day counter skips B+1 AND B+2).
  Three entry rules are built from the SAME fetched entries:  'enter from B+1' (no skip), 'enter from B+2' (skip only B+1) and 'enter from B+3' (YOUR SCRIPT EXACTLY).  Touches before the first allowed day are ignored.
ENTRY      the first 1-minute candle (09:15 .. BBB_ENTRY_LAST = 15:29, every minute of the session) of the entry day whose High (SHORT: Low) reaches the level; option price = close of that minute.
           A stock that opens beyond the level is entered at 09:15 at the real option price (your daily script assumed a fill AT the level).
OPTION     LONG = ATM CALL, SHORT = ATM PUT, nearest monthly expiry (next month's series on the expiry day itself); ITM-1 .. ITM-BBB_ITM_MAX (3) if the ATM series has no candle at the entry minute.
           Nothing is dropped for thin option data (BBB_COV_MIN = 0); every entry carries its data coverage 'cov' in entries.csv.
FILTER     BBB_BB_ONLY = 1 (default): only entries that pass the Bollinger filter are fetched (your strategy).  0 = fetch the others too (tagged bb_ok 0) for a with / without comparison (about 3x the Dhan calls).
EXIT GRID  stop-loss none / 20 / 40 / 60 % x target 40 / 60 / 80 / 120 % / none x time exit 09:30 / 10:00 / 12:00 / 15:00 / 15:30 the same day = 100 variants per direction (percent of the premium).
           Fills: stop / target = first 1-minute low / high touching the level; a gap through it fills at that candle's open; stop and target in the same minute = STOP.
           A trade entered at / after a time exit is skipped for that exit (it cannot exit before it entered).
CAPITAL    at most Rs BBB_CAP (60,000) per trade, whole lots.  Charges, taxes and slippage are not included.  Lot sizes are today's values for all years.

Results in bpb_bb_results/ (raw trades: long/ and short/ each with trades_all_variants.csv.gz + entries.csv + SUMMARY.md) and bpb_bb_report/ (the answers: long/ and short/ separately, per entry rule and per B+n).
"""
import os, sys, json, glob


def _env(name, default):
    return os.environ.get(name) or default


# ---------------------------------------------------------------- settings -> the A8_* names the engine reads (must be set BEFORE the engine is imported)
OUT = _env("BBB_OUT", "bpb_bb_results")
os.environ["A8_OUT"] = OUT
os.environ["A8_START"] = _env("BBB_START", "2023-10-30")
os.environ["A8_END"] = _env("BBB_END", "2026-10-30")
if os.environ.get("BBB_SYMBOLS"): os.environ["A8_SYMBOLS"] = os.environ["BBB_SYMBOLS"]
if os.environ.get("BBB_CAP"): os.environ["A8_CAP"] = os.environ["BBB_CAP"]
os.environ["A8_SLS"] = _env("BBB_SLS", "0,20,40,60")                                 # 0 = no stop-loss
os.environ["A8_TPS"] = _env("BBB_TPS", "40,60,80,120,0")                            # 0 = no target
os.environ["A8_ENTRY_LAST"] = _env("BBB_ENTRY_LAST", "15:29")
os.environ["A8_MIN_TRADES"] = _env("BBB_MIN_TRADES", "30")
os.environ["A8_COV_MIN"] = _env("BBB_COV_MIN", "0")                                    # 0 = never drop an entry for thin option data
os.environ["A8_TRADES_ALL"] = "1"                                                # every trade of every variant, one file per strategy
os.environ["A8_SUM_ENTRY_FROM"] = os.environ["A8_SUM_ENTRY_TO"] = ""
LOOKBACK = int(_env("BBB_LOOKBACK", "5"))                                         # breakout window (days)
BB_ONLY = _env("BBB_BB_ONLY", "1") != "0"                                         # fetch only the entries that pass the Bollinger filter
ITM_MAX = int(_env("BBB_ITM_MAX", "3"))                                           # ATM first, then ITM-1 ... ITM-n (0 = ATM only)
TEXITS = [x.strip() for x in _env("BBB_EXITS", "09:30,10:00,12:00,15:00,15:30").replace(" ", ",").split(",") if len(x.strip()) == 5 and x.strip()[2] == ":"]

import numpy as np, pandas as pd
import all8_backtest as A
import gap_rules as GR
import bpb_bb_rules as R
C = A.C

STRAT_L, STRAT_S = "BPBBB_LONG", "BPBBB_SHORT"
STRAT_RULE = {
    STRAT_L: f"Pure breakout LONG: close above the {LOOKBACK}-day high = breakout day B, level = High of B, a close below the line cancels -> first 1-minute cross above the level on B+m (full day) -> buy CALL; previous-day close above the upper Bollinger band",
    STRAT_S: f"Pure breakout SHORT: close below the {LOOKBACK}-day low = breakdown day B, level = Low of B, a close above the line cancels -> first 1-minute cross below the level on B+m (full day) -> buy PUT; previous-day close below the lower Bollinger band"}
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
    return dict(version=2, bb_only=BB_ONLY, first_days=list(R.FIRST_DAYS), cov_min=A.COV_MIN, lookback=LOOKBACK, itm_max=ITM_MAX, entry_last=A.ENTRY_LAST, start=A.START, end=A.END, sls=A.SLS, tps=A.TPS, exits=A.EXITS, cap=A.CAP, symbols=len(A.UNIVERSE))


def rules_text():
    return (f"PURE BREAKOUT + BOLLINGER (your skip-first-day script).  B = breakout day.  LONG (ATM call): a daily close above the {LOOKBACK}-day high (the line) = B; entry level = the High of B; a later close "
            f"below the line cancels the setup; entry = the first 1-minute candle (09:15 to {A.ENTRY_LAST}) of a day B+m (m >= first allowed day) whose High reaches the level, only if the previous day's close is above "
            f"the previous day's upper Bollinger band (20, 2).  SHORT (ATM put) = mirror (breakdown day B, Low of B, previous close below the lower band).  Entry rules reported: enter from B+1, from B+2 (skip B+1 only), "
            f"from B+3 (your script exactly: its day counter skips B+1 and B+2).  Option = ATM of the entry day's month, ITM-1 .. ITM-{ITM_MAX} if the ATM series has no candle at the entry minute; no entry is dropped "
            f"for thin data.  Every entry is tagged with its B+n.")


def print_rules():
    print(rules_text(), flush=True)
    print(f"Grid: stop-loss {A.SLS} (0 = none) x target {A.TPS} (0 = none) x time exit {A.EXITS} = {len(A.VARS)} variants per direction; {len(A.UNIVERSE)} stocks; {A.START} .. {A.END}; cap Rs {A.CAP}", flush=True)


# ---------------------------------------------------------------- step 1: daily candidates (Yahoo)
def setups_to_rows(stock, dates, O, H, L, C_, t0, t1):
    """One candidate per entry DAY and direction = the union of the three machines (enter from B+1 / B+2 / B+3, bpb_bb_rules.candidates), each tagged with its B+n.  Only entries that pass the Bollinger
    filter unless BBB_BB_ONLY=0.  No open-price prefilter; the exact minute check on Dhan decides the entry."""
    rows = []
    for long in (True, False):
        for s in R.candidates(H, L, C_, long, LOOKBACK, BB_ONLY):
            i = s["entry"]
            if not (t0 <= pd.Timestamp(dates[i]) <= t1): continue
            rows.append(dict(source="BPB", stock=stock, direction="LONG" if long else "SHORT", ref=round(s["level"], 2), signal_date=dates[s["breakout"]], date=dates[i], yahoo_open=float(O[i]),
                             green=-1, red=-1, upper_longer=-1, lower_longer=-1, line=round(s["line"], 2), b_plus=s["b_plus"], b_label=f"B+{s['b_plus']}",
                             from_b1=s["from_b1"], from_b2=s["from_b2"], from_b3=s["from_b3"], bb_ok=s["bb_ok"]))
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
    print(f"Yahoo: {nst} stocks, {nl} LONG + {len(r) - nl} SHORT pure-breakout entry days (union of enter-from-B+1 / B+2 / B+3) with an entry day in {A.START}..{A.END}", flush=True)
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
                     "\nUse the same settings, or give BBB_OUT / the 'out_dir' box another folder name.")
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
    if cps:
        cd = pd.read_csv(cps[-1])
        keep = [c for c in ("stock", "direction", "date", "b_plus", "b_label", "from_b1", "from_b2", "from_b3", "bb_ok", "line", "ref") if c in cd.columns]
        cd = cd[keep].drop_duplicates(["stock", "direction", "date"]).rename(columns={"ref": "ref_yahoo"})
        E = E.merge(cd, on=["stock", "direction", "date"], how="left")
    return E


def write_direction(strat, S, E, prog):
    """Raw files for ONE direction into OUT/<long|short>/ : trades_all_variants.csv.gz (every trade of every variant, with B+n), entries.csv, SUMMARY.md.  The strategy tables are made by bpb_bb_report.py."""
    d = f"{A.OUT}/{DIRNAME[strat]}"; os.makedirs(d, exist_ok=True)
    G = S[S.strategy == strat]
    if G.empty: return False
    tp = f"{A.OUT}/all_trades/{strat}.csv.gz"; nT = 0
    if os.path.exists(tp):
        T = pd.read_csv(tp).sort_values(["exit_rule", "sl", "tp", "entry_date", "entry_time", "stock"])
        if len(E):
            sub = E[E.strategy == strat].rename(columns={"date": "entry_date", "entry_minute": "entry_time", "ref": "level", "signal_date": "breakout_date"})
            keep = [c for c in ("stock", "entry_date", "entry_time", "breakout_date", "b_plus", "b_label", "from_b1", "from_b2", "from_b3", "bb_ok", "level", "ref_yahoo", "stock_price", "line", "strike_offset", "cov") if c in sub.columns]
            T = T.merge(sub[keep].drop_duplicates(["stock", "entry_date", "entry_time"]), on=["stock", "entry_date", "entry_time"], how="left")
        T.to_csv(f"{d}/trades_all_variants.csv.gz", index=False); nT = len(T)
    byb = pd.DataFrame()
    if len(E):
        Es = E[E.strategy == strat].rename(columns={"signal_date": "breakout_date"})
        Es.sort_values(["date", "entry_minute", "stock"]).drop(columns=["ekey"]).to_csv(f"{d}/entries.csv", index=False)
        if "b_plus" in Es.columns:
            have = Es[Es.entry_price.notna()]
            byb = pd.DataFrame({"entries_found": Es.groupby("b_plus").size(), "with_option_data": have.groupby("b_plus").size()}).fillna(0).astype(int).reset_index()
            byb.insert(0, "entry_day", "B+" + byb.b_plus.astype(int).astype(str))
    ts = pd.read_csv(f"{A.OUT}/trades_summary.csv") if os.path.exists(f"{A.OUT}/trades_summary.csv") else pd.DataFrame()
    L = [f"# Pure breakout + Bollinger - {DIRNAME[strat].upper()} ({'ATM call' if strat == STRAT_L else 'ATM put'}) - raw trades, entry checked all day", "",
         f"**Status:** {prog}", "",
         f"**Period (entry dates):** {A.START} to {A.END}  |  **Stocks:** all F&O stocks with Dhan data ({len(A.UNIVERSE)} tried)  |  **Capital per trade:** up to Rs {A.CAP:,} (whole lots)", "",
         "**B = the breakout day.** B+1 = the next trading day, B+2 = the day after, ... every entry below carries its B+n (`b_plus`, `b_label`, `breakout_date`).", "",
         "## Rule", "", STRAT_RULE[strat], "",
         f"**Grid:** stop-loss {', '.join(label_sl(v) for v in A.SLS)} x target {', '.join(label_tp(v) for v in tp_order())} x time exit {', '.join(A.EXITS)} = {len(A.VARS)} variants. "
         "Percentages are % of the option premium. A trade entered at/after a time exit is skipped for that exit, so the early exits have fewer trades than 15:30.", ""]
    if len(ts):
        t2 = ts[ts.strategy == strat][[c for c in ("strategy", "signals_with_entry", "entries_with_option_data", "dropped_low_coverage", "skipped_no_option_data", "skip_reasons") if c in ts.columns]]
        if len(t2): L += ["## Entries found (all three entry rules together, each entry once)", "", md(t2), ""]
    if len(byb): L += ["## Entries by entry day (B+n)", "", md(byb), ""]
    if len(E) and "strike_offset" in E.columns:
        vc = E[(E.strategy == strat) & E.entry_price.notna()].strike_offset.value_counts().sort_index()
        L += ["## Strike used", "", "strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): " + ", ".join(f"{int(k)}: {int(v)}" for k, v in vc.items()), ""]
    L += ["## Where are the results?", "",
          f"`bpb_bb_report/{DIRNAME[strat]}/COMPARE.md` (enter from B+1 / B+2 / B+3, every exit x stop-loss x target, and by exact entry day B+n). This folder holds the raw material: "
          f"`trades_all_variants.csv.gz` ({nT} rows: every trade of every variant, filter by exit_rule / sl / tp, sl 0 = none, tp 0 = none; columns from_b1 / from_b2 / from_b3 = 1 when that entry rule takes the entry) "
          "and `entries.csv` (one row per entry: breakout date, B+n, level, strike, expiry, option price, coverage). The pooled summary.csv in the parent folder mixes the three entry rules - do not read it as a strategy.", "",
          "Charges, taxes and slippage are not included. Lot sizes are today's values for all years. The stock list is today's F&O list (stocks that left F&O are missing). Past results do not promise future results.", ""]
    open(f"{d}/SUMMARY.md", "w").write("\n".join(L))
    return True


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
    E = read_entries()
    prog = open(f"{A.OUT}/PROGRESS.txt").read().strip() if os.path.exists(f"{A.OUT}/PROGRESS.txt") else "(no progress file)"
    for s_ in STRATS: write_direction(s_, S, E, prog)
    L = ["# Pure breakout + Bollinger (LONG call + SHORT put) - raw results, entry checked all day", "",
         f"**Status:** {prog}", "",
         f"**Period (entry dates):** {A.START} to {A.END}  |  **Stocks:** all F&O stocks with Dhan data ({len(A.UNIVERSE)} tried)  |  **Capital per trade:** up to Rs {A.CAP:,} (whole lots)", "",
         "**B = the breakout day; every entry carries its B+n.**", "",
         "## Rules", "", rules_text(), "",
         "LONG and SHORT are separate: `long/` and `short/` each hold their SUMMARY.md, trades_all_variants.csv.gz and entries.csv.  The strategy results (per entry rule B+1 / B+2 / B+3 and per exact B+n) are in `bpb_bb_report/long/` and `bpb_bb_report/short/`.", ""]
    ts = pd.read_csv(f"{A.OUT}/trades_summary.csv") if os.path.exists(f"{A.OUT}/trades_summary.csv") else pd.DataFrame()
    if len(ts):
        L += ["## Entries found", "", md(ts[[c for c in ("strategy", "signals_with_entry", "entries_with_option_data", "dropped_low_coverage", "skipped_no_option_data", "skip_reasons") if c in ts.columns]]), ""]
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
        else: sys.exit("use: python bpb_bb_backtest.py check | run | summary | rules")
    except A.Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
