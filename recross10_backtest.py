"""recross10_backtest.py - the 10 strategies, each entered ONLY on a confirmed 1-minute RE-CROSS (fake breakouts filtered), on ALL F&O stock options (Dhan 1-minute data).

  python recross10_backtest.py check     test Dhan access + expiry calendar
  python recross10_backtest.py run       full backtest (resumable - run again after a polite stop until PROGRESS.txt says COMPLETE)
  python recross10_backtest.py summary   rebuild every result file from the saved option data (no API calls)
  python recross10_backtest.py rules     print the re-cross rule and the settings in use

THE 10 STRATEGIES (LONG buys the ATM call, SHORT the ATM put; nearest monthly expiry, strike locked at entry; each strategy is separate, never mixed)
  BPB_LONG, BPB_SHORT                         breakout -> pullback -> re-cross: the daily BPB setup (bpb_fno_backtest.py rules) gives the entry LEVEL
  WICK_GREEN_UPPER_LONG / _SHORT              SHAPECMP daily signal (a daily close beyond the 10-day high/low, a later close back across it) gives the entry LEVEL,
  WICK_RED_UPPER_LONG / _SHORT                split by the signal candle ("previous candle"): green|red x upper wick longer|lower wick longer
  WICK_GREEN_LOWER_LONG / _SHORT
  WICK_RED_LOWER_LONG / _SHORT
  The daily rules, candidates and levels are exactly those of all8_backtest.py.  What is new here is the ENTRY: on the entry day the level must be RE-CROSSED on the
  1-minute chart by the rule below, in every one of the 10 strategies.

THE RE-CROSS RULE (the "correct" way to find a re-cross in minute candles, and what makes a breakout "fake").  Written for LONG; SHORT is the mirror image.
  A close is only a 1-minute CLOSE - a wick through the line never counts.  Let x = (close - level) / level.
    beyond   x >= +BAND      the close is clearly above the line         (BAND default 0.05 %)
    back     x <= -BAND      the close is clearly below the line
    inside the band (-BAND < x < +BAND) is noise: it neither breaks, nor pulls back, nor confirms.
  1. BASE      the BASE (4) one-minute closes right before the first break all closed below the line (no missing minutes in the data): the stock really came from below.
               A stock that opens above the line, or hovers on it, has no base -> no break.
  2. BREAK     the first close beyond the line, at 09:20 or later, after a base.                                   (a wick or a close inside the band is not a break)
  3. BACK      after the break, a close back below the line (outside the band) - the failed breakout / pullback.
  4. RE-CROSS  after BACK, HOLD (2) consecutive one-minute closes beyond the line (outside the band).  ENTRY = the close of the LAST of them: the option candle of
               that minute is the fill price.  One close beyond the line that is followed by a close back is a fake re-cross and is ignored (the count restarts).
  Entry is accepted from the re-cross minute up to ENTRY_LAST (default 15:20).  One entry per strategy, stock and day.  Nothing in the rule looks at a later candle.

EXIT GRID (every combination is simulated for every entry)
  stop-loss   none / 20 / 40 / 60 % of the premium
  target      none / 20 / 40 / 60 / 80 % of the premium
  time exit   09:30 | 10:00 | 12:00 | 15:30 the same day (close of the last option candle up to that minute; a trade entered at/after that minute is skipped for that exit)
  = 4 x 5 x 4 = 80 variants per strategy, 800 in all.   (no UNTIL_HIT: every trade is closed on the entry day)
  Fills      stop / target = first 1-minute low / high that touches the level; a gap through it fills at that candle's open; if stop and target fall in the same minute
             the STOP is taken.
CAPITAL    at most Rs 60,000 per trade: lots = 60000 // (premium x lot size); a trade whose single lot costs more is skipped.
Charges, taxes and slippage are not included.  Lot sizes are today's values for all years.

All the engine code (Dhan client, stock candles, option series, exit simulation, tables) is all8_backtest.py, unchanged; this file only swaps the entry rule, the strategy list
and the exit grid, and writes the extra summary / trade files.

RESULTS in recross10_results/ :
  SUMMARY.md                  start here: the 10 strategies, their best variants, and the file list
  summary.csv                 one row per strategy x time exit x stop-loss x target (trades, win %, PnL, ROI, profit factor, drawdown, exits by reason)
  trade_files/<STRATEGY>_best_trades.csv   every trade of the strategy's best variant (by PnL), one plain CSV per strategy (10 files)
  all_trades/<STRATEGY>.csv.gz             every trade of ALL 80 variants of the strategy (long format, filter by exit_rule / sl / tp)
  top_by_pnl.csv  top_by_roi.csv  top_by_win_rate.csv  top_by_profit_factor.csv  best_per_strategy.csv  trades_summary.csv  summary_by_year_top.csv  REPORT.txt  PROGRESS.txt
  (+ events.csv, parts/, skipped/, candidates_*.csv, rule.json)
"""
import os, sys, json


def _env(name, default):
    return os.environ.get(name) or default


# ---------------------------------------------------------------- settings -> the A8_* names the engine reads (must be set BEFORE the engine is imported)
OUT = _env("R10_OUT", "recross10_results")
os.environ["A8_OUT"] = OUT
for _k in ("START", "END", "SYMBOLS", "CAP"):
    if os.environ.get("R10_" + _k): os.environ["A8_" + _k] = os.environ["R10_" + _k]
os.environ["A8_SLS"] = _env("R10_SLS", "0,20,40,60")                         # 0 = no stop-loss
os.environ["A8_TPS"] = _env("R10_TPS", "0,20,40,60,80")                      # 0 = no target
os.environ["A8_ENTRY_LAST"] = _env("R10_ENTRY_LAST", "15:20")
os.environ["A8_MIN_TRADES"] = _env("R10_MIN_TRADES", "30")
os.environ["A8_TRADES_ALL"] = "1"                                            # every trade of every variant, one file per strategy
os.environ["A8_SUM_ENTRY_FROM"] = os.environ["A8_SUM_ENTRY_TO"] = ""

BAND_PCT = float(_env("R10_BAND_PCT", "0.05"))                               # the +/- band around the line, in percent of the line
BAND = BAND_PCT / 100.0
BASE_N = int(_env("R10_BASE", "4"))                                          # closes on the far side before the first break
HOLD_N = int(_env("R10_HOLD", "2"))                                          # consecutive closes beyond the line that confirm the re-cross
FIRST_BREAK = _env("R10_FIRST_BREAK", "09:20")                               # earliest minute of the first break

# ENTRY RULE: "standard" = the original rule (base, break at 09:20+, back, re-cross)
#             "touch"    = YOUR rule: first touch of the line, then a close at least EXT_PCT beyond it, then ANY re-cross during the day
ENTRY_RULE = _env("R10_RULE", "standard")
EXT_PCT = float(_env("R10_EXT_PCT", "0.10"))                                 # a close this far (percent of the level) beyond the line is needed after the first touch
EXT = EXT_PCT / 100.0

import numpy as np, pandas as pd
import all8_backtest as A
C = A.C

FIRST_BREAK_MIN = int(FIRST_BREAK[:2]) * 60 + int(FIRST_BREAK[3:5])
SIDES = ("LONG", "SHORT")
PATTERNS = ["WICK_GREEN_UPPER", "WICK_RED_UPPER", "WICK_GREEN_LOWER", "WICK_RED_LOWER"]
STRATS = [f"{p}_{s}" for p in ["BPB"] + PATTERNS for s in SIDES]             # 10 strategies
ENTRY_NAME = "RECROSS_V2"


# ---------------------------------------------------------------- the re-cross rule
def recross_touch(u, level, long, band=None, hold_n=None, last_min=None, ext=None):
    """YOUR rule (LONG shown, SHORT is the mirror image).  Returns (entry_pos, touch_pos, strong_pos, back_pos) as positions in u, or None.
      1. FIRST TOUCH   the first 1-minute candle (from 09:15) whose range reaches the line (high >= level).  Its time is reported in the trade files.
      2. STRONG CLOSE  from the touch on, at least one candle CLOSES `ext` (EXT_PCT %) or more beyond the line.
      3. BACK          later, a close back across the line (outside the +/- band).
      4. RE-CROSS      then `hold_n` consecutive closes beyond the line (outside the band); the last one is the entry.  ANY time of the day up to ENTRY_LAST.
    Fake-recross filter: only CLOSES count, +/- band around the line is noise, `hold_n` consecutive closes are needed (a single poke back above is ignored and the count restarts).
    If the re-cross attempt fails the rule simply waits for the next one; the first confirmed re-cross of the day is the entry."""
    band = BAND if band is None else band
    hold_n = HOLD_N if hold_n is None else hold_n
    last_min = A.ENTRY_MIN if last_min is None else last_min
    ext = max(EXT if ext is None else ext, band)
    if u is None or len(u) < 3 + hold_n or not level > 0: return None
    m = u.index.hour.values * 60 + u.index.minute.values
    c = u.c.values.astype(float); h = u.h.values.astype(float); lo = u.l.values.astype(float)
    x = (c - level) / level if long else (level - c) / level
    n = len(c)
    touched = (h >= level) if long else (lo <= level)
    kt = next((k for k in range(n) if m[k] >= 555 and touched[k]), None)
    if kt is None: return None
    ks = next((k for k in range(kt, n) if m[k] <= last_min and x[k] >= ext), None)
    if ks is None: return None
    jb = next((j for j in range(ks + 1, n) if m[j] <= last_min and x[j] <= -band), None)
    if jb is None: return None
    cnt = 0
    for k in range(jb + 1, n):
        if m[k] > last_min: return None
        if x[k] >= band:
            cnt = cnt + 1 if (cnt and m[k] - m[k - 1] == 1) else 1
            if cnt >= hold_n: return k, kt, ks, jb
        else:
            cnt = 0
    return None


def recross_entry(u, level, long, band=None, base_n=None, hold_n=None, first_break=None, last_min=None):
    """The entry candle position for the selected rule."""
    if ENTRY_RULE == "touch":
        r = recross_touch(u, level, long, band, hold_n, last_min)
        return None if r is None else r[0]
    return _recross_standard(u, level, long, band, base_n, hold_n, first_break, last_min)


def _recross_standard(u, level, long, band=None, base_n=None, hold_n=None, first_break=None, last_min=None):
    """u = one-minute candles of the entry day (index = candle start, columns o h l c).  -> position of the ENTRY candle in u, or None.
    See the module docstring for the rule: closes only, +/- band, a base on the far side, break, back, then `hold_n` closes beyond the line."""
    band = BAND if band is None else band
    base_n = BASE_N if base_n is None else base_n
    hold_n = HOLD_N if hold_n is None else hold_n
    first_break = FIRST_BREAK_MIN if first_break is None else first_break
    last_min = A.ENTRY_MIN if last_min is None else last_min
    if u is None or len(u) < base_n + 1 + 1 + hold_n or not level > 0: return None
    m = u.index.hour.values * 60 + u.index.minute.values
    c = u.c.values.astype(float)
    x = (c - level) / level if long else (level - c) / level                  # > 0 : on the breakout side of the line
    n = len(c)
    kb = None
    for k in range(base_n, n):                                                # 1 + 2: a base, then the first close beyond the band
        if m[k] > last_min: return None
        if m[k] >= first_break and x[k] >= band and m[k] - m[k - base_n] == base_n and (x[k - base_n:k] < 0).all():
            kb = k; break
    if kb is None: return None
    j = next((j for j in range(kb + 1, n) if m[j] <= last_min and x[j] <= -band), None)    # 3: a close back across the line
    if j is None: return None
    cnt = 0
    for k in range(j + 1, n):                                                 # 4: hold_n consecutive closes beyond the line; the last one is the entry
        if m[k] > last_min: return None
        if x[k] >= band:
            cnt = cnt + 1 if (cnt and m[k] - m[k - 1] == 1) else 1
            if cnt >= hold_n: return k
        else:
            cnt = 0
    return None


def _stock_name():
    """Best effort: find the stock symbol in the engine's calling frames (the engine's own code is not edited)."""
    try:
        f = sys._getframe(2)
        for _ in range(6):
            if f is None: break
            for key in ("stock", "sym", "symbol", "ticker", "name"):
                v = f.f_locals.get(key)
                if isinstance(v, str) and 0 < len(v) < 30: return v
            f = f.f_back
    except Exception:
        pass
    return ""


def _log_touch(u, long, level, r):
    k, kt, ks, jb = r
    os.makedirs(A.OUT, exist_ok=True)
    lp = f"{A.OUT}/touch_log.csv"
    new = not os.path.exists(lp)
    with open(lp, "a") as fh:
        if new: fh.write("entry_date,entry_time,side,stock,level,first_touch_time,strong_close_time,back_time\n")
        t = lambda i: u.index[i].strftime("%H:%M")
        fh.write(f"{u.index[k].strftime('%Y-%m-%d')},{t(k)},{'LONG' if long else 'SHORT'},{_stock_name()},{level:.4f},{t(kt)},{t(ks)},{t(jb)}\n")


def entries_for(u, level, long):
    """Replaces combo_dayrisk_backtest.entries_for: the only entry type is the confirmed re-cross of the selected rule."""
    if ENTRY_RULE == "touch":
        r = recross_touch(u, level, long)
        if r is None: return {}
        _log_touch(u, long, level, r)
        return {"RC2_" + ("LONG" if long else "SHORT"): u.index[r[0]]}
    k = recross_entry(u, level, long)
    return {} if k is None else {"RC2_" + ("LONG" if long else "SHORT"): u.index[k]}


def strategies_for(source, typ, green, red, up, lo):
    """Replaces all8_backtest.strategies_for: which of the 10 strategies an entry belongs to."""
    side = {"RC2_LONG": "LONG", "RC2_SHORT": "SHORT"}.get(typ)
    if side is None: return []
    if source == "BPB": return ["BPB_" + side]
    if source != "SHAPE": return []
    out = []
    if green == 1 and up == 1: out.append("WICK_GREEN_UPPER_" + side)
    if red == 1 and up == 1: out.append("WICK_RED_UPPER_" + side)
    if green == 1 and lo == 1: out.append("WICK_GREEN_LOWER_" + side)
    if red == 1 and lo == 1: out.append("WICK_RED_LOWER_" + side)
    return out


def install():
    """Swap the entry rule, the strategy list and the exit grid inside the engine (its functions read these module globals when they run)."""
    C.entries_for = entries_for
    A.strategies_for = strategies_for
    A.STRATS = list(STRATS)
    A.ENTRY_TYPE = {s: ENTRY_NAME for s in STRATS}
    A.EXITS = list(A.TEXITS)                                                  # 09:30 / 10:00 / 12:00 / 15:30 - no UNTIL_HIT
    A.VARS = [(ex, sl, tp) for ex in A.EXITS for sl in A.SLS for tp in A.TPS]


install()


def rule_dict():
    return dict(band_pct=BAND_PCT, base=BASE_N, hold=HOLD_N, first_break=FIRST_BREAK, entry_last=A.ENTRY_LAST,
                entry_rule=ENTRY_RULE, ext_pct=EXT_PCT, start=A.START, end=A.END, sls=A.SLS, tps=A.TPS,
                exits=A.EXITS, cap=A.CAP)


def print_rules():
    d = rule_dict()
    if ENTRY_RULE == "touch":
        print(f"TOUCH rule: first touch of the line; then a close >= {EXT_PCT}% beyond it; then ANY re-cross in the day = {HOLD_N} consecutive closes beyond the line "
              f"(band +/-{BAND_PCT}%) after a close back across it.  Entry window up to {A.ENTRY_LAST}.", flush=True)
    else:
        print(f"RE-CROSS rule: closes only; band +/-{BAND_PCT}% of the line; base = {BASE_N} closes on the far side; first break at {FIRST_BREAK} or later; "
              f"then a close back; then {HOLD_N} consecutive closes beyond the line = entry (close of the last).  Entry window up to {A.ENTRY_LAST}.", flush=True)
    print(f"Grid: stop-loss {A.SLS} (0 = none) x target {A.TPS} (0 = none) x time exit {A.EXITS} = {len(A.VARS)} variants per strategy; {len(STRATS)} strategies; "
          f"{d['start']} .. {d['end']}; cap Rs {A.CAP}", flush=True)


# ---------------------------------------------------------------- candidates (daily signals): reuse the ALL-8 file when it covers the same dates
def get_candidates():
    cp = f"{A.OUT}/candidates_{A.START}_{A.END}.csv"
    if os.path.exists(cp):
        cand = pd.read_csv(cp)
    else:
        old = f"all8_results/candidates_{A.START}_{A.END}.csv"
        if os.path.exists(old):
            cand = pd.read_csv(old); print(f"daily candidates reused from {old}", flush=True)
        else:
            cand = C.yahoo_candidates()
        cand = cand[cand.source.isin(["BPB", "SHAPE"])].reset_index(drop=True)             # no trendline strategies here
        cand.to_csv(cp, index=False)
    return cand[cand.source.isin(["BPB", "SHAPE"])].reset_index(drop=True)


def run():
    os.makedirs(A.OUT, exist_ok=True)
    rp = f"{A.OUT}/rule.json"; rule = json.loads(json.dumps(rule_dict()))
    if os.path.exists(rp):
        old = json.load(open(rp))
        if old != rule:
            sys.exit("STOP - the saved data in " + A.OUT + " was made with other settings:\n  saved: " + json.dumps(old) + "\n  now:   " + json.dumps(rule) +
                     "\nUse the same settings, or give R10_OUT / the 'out_dir' box another folder name.")
    json.dump(rule, open(rp, "w"), indent=1)
    print_rules()
    st = A.load_state(); dh = A.Dhan(); mst = A.load_master()
    try:
        cand = get_candidates()
        if cand.empty: print("No candidate days in this range."); return
        print(f"Candidate days {A.START}..{A.END}: {len(cand)} ({', '.join(f'{k} = {v}' for k, v in cand.groupby('source').size().items())})", flush=True)
        ev = A.step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= A.START) & (ev["date"] <= A.END)] if len(ev) else ev
        print(f"Re-cross entries (09:20-{A.ENTRY_LAST}): {len(ev)}" + (f"  ({', '.join(f'{k} = {v}' for k, v in ev.groupby('strategy').size().items())})" if len(ev) else ""), flush=True)
        if len(ev): A.step_options(dh, ev, mst, st)
        print("ALL STEPS FINISHED", flush=True)
    except A.Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        A.B.print_stats(dh); A.progress(); summary(); A.checkpoint(True)


# ---------------------------------------------------------------- result files
def label_sl(v): return "no SL" if not v else f"SL {int(v)}%"
def label_tp(v): return "no TP" if not v else f"TP {int(v)}%"


def md(df):
    try: return df.to_markdown(index=False)
    except Exception: return df.to_string(index=False)


TOUCH_COLS = ["first_touch_time", "strong_close_time", "back_time", "recross_level"]


def add_touch_times(T, log):
    """Add first_touch_time / strong_close_time / back_time to a trades table (matched on date + entry minute + side [+ stock])."""
    T = T.drop(columns=[c for c in TOUCH_COLS if c in T.columns])
    if log is None or not len(log) or "entry_date" not in T.columns or "entry_time" not in T.columns: return T
    T = T.copy()
    side = T["strategy"].astype(str).str.rsplit("_", n=1).str[-1] if "strategy" in T.columns else pd.Series("", index=T.index)
    T["_d"] = T.entry_date.astype(str).str[:10]; T["_t"] = T.entry_time.astype(str).str[-8:].str[:5] if T.entry_time.astype(str).str.len().max() > 5 else T.entry_time.astype(str).str[:5]
    T["_s"] = side
    L = log.rename(columns={"entry_date": "_d", "entry_time": "_t", "side": "_s", "level": "recross_level"})
    L["_t"] = L["_t"].astype(str).str[:5]
    use_stock = "stock" in T.columns and L["stock"].fillna("").astype(str).str.len().max() > 0
    keys = ["_d", "_t", "_s"] + (["stock"] if use_stock else [])
    if use_stock: L["stock"] = L["stock"].astype(str)
    L = L.drop_duplicates(keys, keep="first")
    out = T.merge(L[keys + ["recross_level", "first_touch_time", "strong_close_time", "back_time"]], on=keys, how="left")
    return out.drop(columns=["_d", "_t", "_s"])


def post_process():
    """Readable labels, one plain CSV of trades per strategy, SUMMARY.md."""
    sp = f"{A.OUT}/summary.csv"
    if not os.path.exists(sp): return
    S = pd.read_csv(sp)
    if S.empty: return
    S["sl_rule"] = S.sl.map(label_sl); S["tp_rule"] = S.tp.map(label_tp)
    S["variant"] = S.strategy + " | exit " + S.exit_rule + " | " + S.sl_rule + " | " + S.tp_rule
    S.to_csv(sp, index=False)
    old = f"{A.OUT}/until_hit_days_held.csv"
    if os.path.exists(old): os.remove(old)                                    # there is no UNTIL_HIT variant in this study
    good = S[S.trades >= A.MIN_TRADES]
    base = good if len(good) else S
    os.makedirs(f"{A.OUT}/trade_files", exist_ok=True)
    lg = f"{A.OUT}/touch_log.csv"
    log = pd.read_csv(lg) if os.path.exists(lg) else None
    best_pnl, best_roi, files = [], [], []
    for s in STRATS:
        g = base[base.strategy == s]
        if g.empty: continue
        bp = g.sort_values(["total_pnl", "trades"], ascending=False).iloc[0]; best_pnl.append(bp)
        best_roi.append(g.sort_values(["roi_pct", "trades"], ascending=False).iloc[0])
        tp = f"{A.OUT}/all_trades/{s}.csv.gz"
        if not os.path.exists(tp): continue
        T = pd.read_csv(tp)
        T = T[(T.exit_rule == bp.exit_rule) & (T.sl == bp.sl) & (T.tp == bp.tp)].sort_values(["entry_date", "entry_time", "stock"])
        T = add_touch_times(T, log)
        if log is not None and len(T) and T["first_touch_time"].isna().any():
            print(f"note: {s}: {int(T['first_touch_time'].isna().sum())} of {len(T)} trades have no first-touch time (log did not match - see the README note)", flush=True)
        T.insert(0, "variant", bp.variant)
        T.to_csv(f"{A.OUT}/trade_files/{s}_best_trades.csv", index=False)
        files.append((s, len(T), bp.variant))
    cols = ["strategy", "exit_rule", "sl_rule", "tp_rule", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "max_drawdown"]
    ts = pd.read_csv(f"{A.OUT}/trades_summary.csv") if os.path.exists(f"{A.OUT}/trades_summary.csv") else pd.DataFrame()
    prog = open(f"{A.OUT}/PROGRESS.txt").read().strip() if os.path.exists(f"{A.OUT}/PROGRESS.txt") else "(no progress file)"
    L = [f"# RECROSS-10 backtest summary", "",
         f"**Status:** {prog}", "",
         f"**Period (entry dates):** {A.START} to {A.END}  |  **Stocks:** all F&O stocks with Dhan data  |  **Capital per trade:** up to Rs {A.CAP:,} (whole lots)",
         "", "## The re-cross rule", "",
         (f"**Rule used: TOUCH** - first touch of the line (from 09:15), then at least one close >= {EXT_PCT}% beyond the line, then ANY later re-cross of the day "
         f"(a close back across the line, then {HOLD_N} consecutive closes beyond it, band +/-{BAND_PCT}%). The trade files carry first_touch_time, strong_close_time and back_time.", "") if ENTRY_RULE == "touch" else "",
         f"Closes of 1-minute candles only. Band = +/-{BAND_PCT}% around the level (a close inside the band is noise). Base = {BASE_N} closes on the far side before the first break. "
         f"Break = first close beyond the band at {FIRST_BREAK} or later. Back = a later close across the level on the far side. Re-cross = {HOLD_N} consecutive closes beyond the band; "
         f"entry = close of the last one (option price of that minute). Entry window to {A.ENTRY_LAST}. Applied to all 10 strategies.", "",
         f"**Grid:** stop-loss {', '.join(label_sl(v) for v in A.SLS)} x target {', '.join(label_tp(v) for v in A.TPS)} x time exit {', '.join(A.EXITS)} = {len(A.VARS)} variants per strategy.",
         f"Variants with fewer than {A.MIN_TRADES} trades are left out of the 'best' tables (a 09:30 exit only has the entries made before 09:30).", ""]
    if len(ts):
        t2 = ts[[c for c in ("strategy", "signals_with_entry", "entries_with_option_data", "dropped_low_coverage", "skipped_no_option_data", "long_trades", "short_trades") if c in ts.columns]]
        L += ["## Re-cross entries found (variant independent)", "", md(t2), ""]
    if best_pnl: L += ["## Best variant of each strategy - by total PnL", "", md(pd.DataFrame(best_pnl)[cols]), ""]
    if best_roi: L += ["## Best variant of each strategy - by ROI", "", md(pd.DataFrame(best_roi)[cols]), ""]
    L += [f"## Top 15 variants overall by ROI (at least {A.MIN_TRADES} trades)", "", md(good.sort_values("roi_pct", ascending=False).head(15)[cols]) if len(good) else "(none yet)", "",
          "## Trade files", "",
          "One plain CSV per strategy with every trade of its best-PnL variant is in `trade_files/`; the trades of ALL 80 variants of each strategy are in `all_trades/<STRATEGY>.csv.gz`.", ""]
    L += [f"- `trade_files/{s}_best_trades.csv` - {n} trades - {v}" for s, n, v in files]
    L += ["", "The 'best variant' is the best of 80 chosen after seeing the results, so it is optimistic. Check that its neighbours (the next stop-loss / target / exit) look similar and that "
          "`summary_by_year_top.csv` is not carried by one year. Charges, taxes and slippage are not included. Lot sizes are today's values for all years. Past results do not promise future results.", ""]
    open(f"{A.OUT}/SUMMARY.md", "w").write("\n".join(L))
    print("\n".join(L[:6]), flush=True)


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
        else: sys.exit("use: python recross10_backtest.py check | run | summary | rules")
    except A.Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
