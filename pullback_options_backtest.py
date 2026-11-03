"""pullback_options_backtest.py - the daily "10-day-high breakout -> pullback -> re-cross" strategy, entered on the OPTION at the exact 1-minute of the re-cross.
Dhan data only: daily + 1-minute stock candles, 1-minute Nifty candles, expired-option 1-minute candles (rolling ATM series).

  python pullback_options_backtest.py check     test Dhan access (daily, minute, option series)
  python pullback_options_backtest.py run       full backtest (resumable: run again until PROGRESS.txt says COMPLETE)
  python pullback_options_backtest.py summary   rebuild the result files from saved trades (no API calls)

THE SIGNAL (daily, your rules)   breakout = Close > highest Close of the previous 10 days; peak = that day's High (rises with new highs); a Close below the breakout Close
  cancels it; Low < peak*(1-0.5%) = pullback; then the day the High reaches the peak again = RE-CROSS day, level = peak.
THE ENTRY MINUTE                 on the re-cross day, the first 1-minute stock candle (from 09:15, up to ENTRY_LAST) whose HIGH >= level.  Exact time is reported.
  NIFTY FILTER (NIFTY_MODE)      intraday (default) = built from Nifty 1-minute candles: Nifty's price at the entry minute (close of that minute) is above Nifty's day open,
                                 i.e. the Nifty day candle is green SO FAR - everything known at the entry minute, no look-ahead
                                 minute = the Nifty 1-minute candle of the entry minute itself is green (close > open)
                                 daily_close = Nifty's FINAL candle of the day is green (your first version; look-ahead)   |  none
  If the filter fails the setup stays alive and can fire on a later day (as in your script).
THE OPTION                       LONG = CALL, SHORT = PUT (the mirror image: breakdown below the 10-day low, bounce, re-cross down; Nifty must be red).  Reported separately.  Nearest monthly expiry.  ATM strike at the entry minute; if the ATM contract has no candle at that minute, the nearest ITM
  (one strike below) is used.  The strike is then LOCKED: the same contract is followed to the exit.  Fill = CLOSE of the option candle of the entry minute.
EXIT GRID                        stop-loss none/20/40/60 % x target none/40/60/80/120 % x time exit 09:30/10:00/12:00/15:30 same day = 80 variants.
  Option candles after the entry minute are scanned; stop / target = first candle whose low / high touches the level (a gap fills at the open); both in one candle -> STOP.
  Time exit = close of the last candle that starts before the exit minute; an entry at/after that minute is skipped for that exit.
CAPITAL                          lots = CAP // (premium x lot size) (CAP default Rs 60,000); one lot too expensive -> trade skipped.  Lot sizes are today's.
Charges, taxes, slippage are not included.  Stock universe = stocks that have options TODAY (stocks dropped from F&O earlier are missing = survivorship).
"""
import os, sys, io, re, time, json
import numpy as np, pandas as pd


def env(k, d): return os.environ.get(k) or d


OUT = env("PO_OUT", "pullback_options_results"); CACHE = f"{OUT}/cache"
_explicit = bool(os.environ.get("PO_START") or os.environ.get("PO_END"))
END = env("PO_END", pd.Timestamp.today().strftime("%Y-%m-%d"))
START = env("PO_START", (pd.Timestamp(END) - pd.DateOffset(years=3)).strftime("%Y-%m-%d"))
SLS = [float(x) / 100 for x in env("PO_SLS", "0,20,40,60").replace(" ", "").split(",")]
TPS = [float(x) / 100 for x in env("PO_TPS", "0,40,60,80,120").replace(" ", "").split(",")]
EXITS = env("PO_EXITS", "09:30,10:00,12:00,15:30").replace(" ", "").split(",")
hm = lambda s: int(s[:2]) * 60 + int(s[3:5])
EXIT_MIN = [hm(x) for x in EXITS]
ENTRY_LAST = env("PO_ENTRY_LAST", "15:20"); ENTRY_LAST_MIN = hm(ENTRY_LAST)
MIN_PREMIUM = float(env("PO_MIN_PREMIUM", "1.0"))                            # entry premium below this (Rs) is a tick-size artefact, not a tradable price
CAP = float(env("PO_CAP", "60000")); MIN_TRADES = int(env("PO_MIN_TRADES", "30"))
NIFTY_MODE = env("PO_NIFTY_MODE", "intraday")                               # intraday | daily_close | none
WINDOW = int(env("PO_WINDOW", "10")); DIP = float(env("PO_DIP_PCT", "0.5")) / 100; BUDGET = float(env("PO_BUDGET_MIN", "0")) * 60
SIDES = [x for x in env("PO_SIDES", "LONG,SHORT").replace(" ", "").upper().split(",") if x in ("LONG", "SHORT")]
SYMBOLS = [s.upper() for s in env("PO_SYMBOLS", "").replace(",", " ").split()]
CLIENT = os.environ.get("DHAN_CLIENT_ID", ""); TOKEN = os.environ.get("DHAN_ACCESS_TOKEN", "")
BASE = "https://api.dhan.co/v2"; MASTER = "https://images.dhan.co/api-data/api-scrip-master.csv"
OFFS = ["ATM", "ATM-1", "ATM+1", "ATM-2", "ATM+2", "ATM-3", "ATM+3"]
T0 = time.time()


class Stop(Exception): pass
class Fatal(Exception): pass


def budget():
    if BUDGET and time.time() - T0 > BUDGET: raise Stop("time budget used")


# ---------------------------------------------------------------- Dhan
def frame(j, extra=()):
    """Dhan column arrays -> DataFrame, index = candle start (IST, naive)."""
    if not j or not j.get("timestamp"): return pd.DataFrame(columns=["o", "h", "l", "c", *extra])
    ts = np.array(j["timestamp"], dtype=float)
    if ts.max() < 1.2e9: ts = ts + 315532800
    idx = pd.to_datetime(ts, unit="s", utc=True).tz_convert("Asia/Kolkata").tz_localize(None)
    d = pd.DataFrame({"o": j["open"], "h": j["high"], "l": j["low"], "c": j["close"], **{k: j.get(k) for k in extra}}, index=idx)
    d = d[~d.index.duplicated(keep="last")].sort_index()
    return d.apply(pd.to_numeric, errors="coerce")


def rd(fp):
    try: return pd.read_csv(fp, index_col=0, parse_dates=True)
    except pd.errors.EmptyDataError: return pd.DataFrame(columns=["o", "h", "l", "c"])


class Dhan:
    def __init__(self):
        import requests
        self.s = requests.Session(); self.n = 0
        self.s.headers.update({"access-token": TOKEN, "client-id": CLIENT, "Content-Type": "application/json", "Accept": "application/json"})

    def post(self, path, body):
        budget()
        for a in range(5):
            time.sleep(0.22)
            r = self.s.post(BASE + path, data=json.dumps(body), timeout=60); self.n += 1
            if r.status_code == 200: return r.json()
            if r.status_code in (401, 403): raise Fatal(f"Dhan {r.status_code}: {r.text[:200]} - the access token is probably expired")
            if r.status_code == 429 or r.status_code >= 500: time.sleep(2 + 3 * a); continue
            return {}                                                      # 400 = no data for that request
        raise Stop(f"Dhan keeps failing ({r.status_code}) - run again later")

    def daily(self, sec, seg, instr, a, b):
        parts = []
        for y in range(pd.Timestamp(a).year, pd.Timestamp(b).year + 1):
            f = max(pd.Timestamp(a), pd.Timestamp(f"{y}-01-01")); t = min(pd.Timestamp(b), pd.Timestamp(f"{y}-12-31"))
            j = self.post("/charts/historical", {"securityId": str(sec), "exchangeSegment": seg, "instrument": instr, "expiryCode": 0, "oi": False,
                                                  "fromDate": f.strftime("%Y-%m-%d"), "toDate": (t + pd.Timedelta(days=1)).strftime("%Y-%m-%d")})
            d = frame(j)
            if len(d): parts.append(d.set_index(d.index.normalize()))
        if not parts: return pd.DataFrame(columns=["o", "h", "l", "c"], index=pd.DatetimeIndex([]))
        d = pd.concat(parts); d = d[~d.index.duplicated(keep="last")].sort_index()
        return d[(d.index >= pd.Timestamp(a)) & (d.index <= pd.Timestamp(b))]

    def minute(self, sec, seg, instr, day):
        j = self.post("/charts/intraday", {"securityId": str(sec), "exchangeSegment": seg, "instrument": instr, "interval": "1", "oi": False,
                                           "fromDate": f"{day} 09:15:00", "toDate": f"{day} 15:30:00"})
        return frame(j)

    def option(self, sec, day, off, side="LONG"):
        nd = (pd.Timestamp(day) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        j = self.post("/charts/rollingoption", {"exchangeSegment": "NSE_FNO", "interval": "1", "securityId": int(sec), "instrument": "OPTSTK", "expiryFlag": "MONTH",
                                                "expiryCode": 1, "strike": off, "drvOptionType": "CALL" if side == "LONG" else "PUT", "requiredData": ["open", "high", "low", "close", "volume", "strike", "spot"],
                                                "fromDate": day, "toDate": nd})
        d = (j or {}).get("data") or j or {}
        x = (d.get("ce") or d.get("CALL")) if side == "LONG" else (d.get("pe") or d.get("PUT"))
        return frame(x or {}, extra=("strike", "spot"))


def sameday(d, day):
    """Dhan returns the NEXT trading day's candles too (toDate is inclusive); a same-day trade must never see them."""
    return d[d.index.strftime("%Y-%m-%d") == str(day)[:10]] if len(d) else d


def cached(fp, fn):
    if os.path.exists(fp): return rd(fp)
    d = fn(); os.makedirs(os.path.dirname(fp), exist_ok=True); d.to_csv(fp); return d


def load_master():
    import requests
    fp = f"{CACHE}/scrip_master.csv.gz"
    if os.path.exists(fp): m = pd.read_csv(fp, low_memory=False)
    else:
        r = requests.get(MASTER, timeout=180); r.raise_for_status(); m = pd.read_csv(io.StringIO(r.text), low_memory=False)
        os.makedirs(CACHE, exist_ok=True); m.to_csv(fp, index=False)
    eq = m[(m.SEM_EXM_EXCH_ID == "NSE") & (m.SEM_SEGMENT == "E") & (m.SEM_INSTRUMENT_NAME == "EQUITY")]
    if "SEM_SERIES" in eq.columns: eq = eq[eq.SEM_SERIES == "EQ"]
    eqid = dict(zip(eq.SEM_TRADING_SYMBOL.astype(str).str.upper(), eq.SEM_SMST_SECURITY_ID.astype(int).astype(str)))
    fo = m[(m.SEM_EXM_EXCH_ID == "NSE") & (m.SEM_SEGMENT == "D") & (m.SEM_INSTRUMENT_NAME == "OPTSTK")].copy()
    fo["u"] = fo.SEM_TRADING_SYMBOL.astype(str).str.upper().str.replace(r"-[A-Za-z]{3}\d{4}-.*$", "", regex=True)
    fo = fo.sort_values("SEM_EXPIRY_DATE")
    lots = fo.groupby("u").SEM_LOT_UNITS.first().astype(int).to_dict()
    return eqid, lots


# ---------------------------------------------------------------- daily signal
def signals(df, try_entry, start, side="LONG"):
    """Your state machine; SHORT is its mirror image.  try_entry(day, level) -> True if a trade was taken (setup resets), False to keep the setup alive.
    LONG : Close > highest close of the previous WINDOW days -> peak = High; Close < breakout close cancels; Low < peak*(1-DIP) = pullback; High >= peak = re-cross, level = peak.
    SHORT: Close < lowest close of the previous WINDOW days  -> trough = Low; Close > breakdown close cancels; High > trough*(1+DIP) = bounce; Low <= trough = re-cross, level = trough."""
    L_ = side == "LONG"
    roll = (df["c"].shift(1).rolling(WINDOW).max() if L_ else df["c"].shift(1).rolling(WINDOW).min()).values
    H, L, C = df.h.values, df.l.values, df.c.values
    state = 0; bc = pk = 0.0; pulled = False
    for i in range(WINDOW, len(df)):
        day = df.index[i]
        if state == 0:
            if (C[i] > roll[i]) if L_ else (C[i] < roll[i]): bc, pk, pulled, state = C[i], (H[i] if L_ else L[i]), False, 1
            continue
        if (C[i] < bc) if L_ else (C[i] > bc): state = 0; continue
        if not pulled:
            if L_:
                if H[i] > pk: pk = H[i]
                elif L[i] < pk * (1 - DIP): pulled = True
            else:
                if L[i] < pk: pk = L[i]
                elif H[i] > pk * (1 + DIP): pulled = True
        if pulled and ((H[i] >= pk) if L_ else (L[i] <= pk)):
            if day < pd.Timestamp(start) or try_entry(day.strftime("%Y-%m-%d"), pk): state = 0


# ---------------------------------------------------------------- phase 1: entry minute
def find_events(dh, eqid, lots, universe, stats, side="LONG"):
    ev = []; nd = f"{CACHE}/NIFTY"; ngreen = None
    nif = cached(f"{CACHE}/NIFTY_daily.csv.gz", lambda: dh.daily("13", "IDX_I", "INDEX", (pd.Timestamp(START) - pd.Timedelta(days=5)).strftime("%Y-%m-%d"), END))
    ngreen = (nif.c > nif.o).to_dict()
    for k, s in enumerate(universe):
        sid = eqid.get(s)
        if sid is None: stats["no_equity_id"] += 1; continue
        wstart = (pd.Timestamp(START) - pd.Timedelta(days=45)).strftime("%Y-%m-%d")
        try: df = cached(f"{CACHE}/daily/{s}.csv.gz", lambda: dh.daily(sid, "NSE_EQ", "EQUITY", wstart, END))
        except (Stop, Fatal): raise
        except Exception as e: print(f"  {s}: daily data error {type(e).__name__}: {e}", flush=True); stats["too_little_daily"] += 1; continue
        if len(df) < WINDOW + 5: stats["too_little_daily"] += 1; continue

        def try_entry(day, level):
            u = cached(f"{CACHE}/min/{s}/{day}.csv.gz", lambda: dh.minute(sid, "NSE_EQ", "EQUITY", day))
            if u.empty: stats["no_stock_minute_data"] += 1; return False
            m = u.index.hour * 60 + u.index.minute
            hit = (u.h.values >= level) if side == "LONG" else (u.l.values <= level)
            ok = np.where(hit & (m >= 555) & (m <= ENTRY_LAST_MIN))[0]
            if not len(ok):
                stats["no_cross_minute"] += 1
                if stats["no_cross_minute"] <= 5:
                    print(f"  DIAG no cross {s} {day} {side}: level {level:.2f}; minute candles {len(u)} {u.index[0].strftime('%H:%M')}-{u.index[-1].strftime('%H:%M')}, "
                          f"minute high {u.h.max():.2f} low {u.l.min():.2f}; daily row H {df.h.get(pd.Timestamp(day))} L {df.l.get(pd.Timestamp(day))}", flush=True)
                return False
            kt = int(ok[0]); ets = u.index[kt]
            if NIFTY_MODE == "intraday":
                nm = cached(f"{nd}/{day}.csv.gz", lambda: dh.minute("13", "IDX_I", "INDEX", day))
                if nm.empty: stats["no_nifty_minute_data"] += 1; return False
                pos = nm.index.searchsorted(ets, side="right") - 1
                green = pos >= 0 and ((nm.c.iloc[pos] > nm.o.iloc[0]) if side == "LONG" else (nm.c.iloc[pos] < nm.o.iloc[0]))
            elif NIFTY_MODE == "minute":
                nm = cached(f"{nd}/{day}.csv.gz", lambda: dh.minute("13", "IDX_I", "INDEX", day))
                if nm.empty: stats["no_nifty_minute_data"] += 1; return False
                pos = nm.index.searchsorted(ets, side="right") - 1
                green = pos >= 0 and ((nm.c.iloc[pos] > nm.o.iloc[pos]) if side == "LONG" else (nm.c.iloc[pos] < nm.o.iloc[pos]))
            elif NIFTY_MODE == "daily_close": green = bool(ngreen.get(pd.Timestamp(day), True)) == (side == "LONG")
            else: green = True
            if not green: stats["nifty_filter_failed"] += 1; return False
            ev.append(dict(side=side, stock=s, sec_id=sid, date=day, level=float(level), entry_ts=ets, stock_close=float(u.c.iloc[kt]), lot=lots.get(s, 0)))
            return True
        signals(df, try_entry, START, side)
        print(f"[{side} {k+1}/{len(universe)}] {s}: events so far {len(ev)}", flush=True)
    return pd.DataFrame(ev)


# ---------------------------------------------------------------- phase 2: option + exits
def pick_contract(dh, sid, day, ets, side="LONG"):
    for off, label in (("ATM", "ATM"), ("ATM-1" if side == "LONG" else "ATM+1", "ITM1")):          # ITM: call = one strike below, put = one strike above
        d = sameday(cached(f"{CACHE}/opt/{sid}/{day}_{off}_{side}.csv.gz", lambda: dh.option(sid, day, off, side)), day)
        if len(d) and ets in d.index and d.c[ets] > 0: return off, label, d
    return None


def locked_series(dh, sid, day, off, d, ets, side="LONG"):
    k = d.strike[ets]; a = d[d.index >= ets]; same = (a.strike - k).abs() < 1e-6
    if same.all(): return a, k
    parts = [a[same]]
    for o in OFFS:
        if o == off: continue
        x = sameday(cached(f"{CACHE}/opt/{sid}/{day}_{o}_{side}.csv.gz", lambda: dh.option(sid, day, o, side)), day)
        if len(x): parts.append(x[(x.index >= ets) & ((x.strike - k).abs() < 1e-6)])
    s = pd.concat(parts); return s[~s.index.duplicated()].sort_index(), k


def simulate(s, ets, e):
    """s: option candles (index start, o h l c) of the locked contract.  -> {(exit, sl, tp): (exit_price, exit_time, reason)} for every variant."""
    a = s[(s.index > ets) & (s.index.strftime("%Y-%m-%d") == ets.strftime("%Y-%m-%d"))]; res = {}      # same day only
    em = ets.hour * 60 + ets.minute
    for ex, xm in zip(EXITS, EXIT_MIN):
        if em >= xm: continue
        w = a[(a.index.hour * 60 + a.index.minute) < xm]
        if w.empty: continue
        o, h, l, c = w.o.values, w.h.values, w.l.values, w.c.values
        for sl in SLS:
            isl = np.where(l <= e * (1 - sl))[0][0] if sl and (l <= e * (1 - sl)).any() else None
            for tp in TPS:
                itp = np.where(h >= e * (1 + tp))[0][0] if tp and (h >= e * (1 + tp)).any() else None
                if isl is not None and (itp is None or isl <= itp):
                    lv = e * (1 - sl); res[(ex, sl, tp)] = (min(o[isl], lv), w.index[isl], "SL")
                elif itp is not None:
                    lv = e * (1 + tp); res[(ex, sl, tp)] = (max(o[itp], lv), w.index[itp], "TP")
                else: res[(ex, sl, tp)] = (c[-1], w.index[-1], "TIME")
    return res


def trade_rows(dh, ev, stats):
    rows, ent = [], []
    for k, r in ev.iterrows():
        budget()
        ets = pd.Timestamp(r.entry_ts); sid = r.sec_id
        side = r.side; pc = pick_contract(dh, sid, r.date, ets, side)
        if pc is None: stats[side]["no_option_candle_atm_or_itm"] += 1; continue
        off, label, d = pc; s, strike = locked_series(dh, sid, r.date, off, d, ets, side); e = float(d.c[ets])
        if e < MIN_PREMIUM: stats[side]["premium_below_min"] = stats[side].get("premium_below_min", 0) + 1; continue
        if not r.lot: stats[side]["no_lot_size"] += 1; continue
        lots = int(CAP // (e * r.lot))
        if lots < 1: stats[side]["one_lot_too_expensive"] += 1; continue
        qty = lots * r.lot
        ent.append(dict(side=side, stock=r.stock, date=r.date, entry_time=ets.strftime("%H:%M"), stock_level=r.level, stock_price=r.stock_close, contract=label, strike=strike,
                        premium=e, lot=r.lot, lots=lots, invested=round(e * qty)))
        for (ex, sl, tp), (x, xt, why) in simulate(s, ets, e).items():
            rows.append(dict(side=side, stock=r.stock, entry_date=r.date, entry_time=ets.strftime("%H:%M"), strike=strike, contract=label, entry=e, exit_rule=ex, sl=int(sl * 100), tp=int(tp * 100),
                             exit=x, exit_time=xt.strftime("%H:%M"), reason=why, lots=lots, invested=e * qty, pnl=(x - e) * qty, ret_pct=(x / e - 1) * 100))
    return pd.DataFrame(rows), pd.DataFrame(ent)


# ---------------------------------------------------------------- results
def lab(v, n): return f"no {n}" if not v else f"{n} {int(v)}%"


def stats_of(g):
    p = g.pnl; w = p[p > 0].sum(); l = -p[p < 0].sum(); eq = p.cumsum(); inv = g.invested.sum()
    return pd.Series(dict(trades=len(g), win_pct=round((p > 0).mean() * 100, 2), total_pnl=round(p.sum()), roi_pct=round(p.sum() / inv * 100, 2) if inv else 0,
                          avg_ret_pct=round(g.ret_pct.mean(), 2), profit_factor=round(w / l, 2) if l > 0 else np.inf, max_drawdown=round((eq - eq.cummax()).min()),
                          sl_exits=int((g.reason == "SL").sum()), tp_exits=int((g.reason == "TP").sum()), time_exits=int((g.reason == "TIME").sum())))


def md(df):
    try: return df.to_markdown(index=False)
    except Exception: return df.to_string(index=False)


def side_report(T, E, st, side):
    """Files + markdown lines of ONE side (LONG = calls, SHORT = puts)."""
    names = "calls" if side == "LONG" else "puts"
    if T is None or T.empty: return [f"## {side} ({names})", "", "No trades.", "", "```", json.dumps(st, indent=1), "```", ""]
    T.to_csv(f"{OUT}/all_trades_{side}.csv.gz", index=False); E.to_csv(f"{OUT}/entries_{side}.csv", index=False)
    S = T.groupby(["exit_rule", "sl", "tp"]).apply(stats_of).reset_index()
    S["sl_rule"] = S.sl.map(lambda v: lab(v, "SL")); S["tp_rule"] = S.tp.map(lambda v: lab(v, "TP")); S.to_csv(f"{OUT}/summary_{side}.csv", index=False)
    good = S[S.trades >= MIN_TRADES]; good = good if len(good) else S
    cols = ["exit_rule", "sl_rule", "tp_rule", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "max_drawdown"]
    bp = good.sort_values("total_pnl", ascending=False).iloc[0]
    bt = T[(T.exit_rule == bp.exit_rule) & (T.sl == bp.sl) & (T.tp == bp.tp)].sort_values(["entry_date", "entry_time"]); bt.to_csv(f"{OUT}/best_variant_trades_{side}.csv", index=False)
    yr = bt.assign(year=bt.entry_date.str[:4]).groupby("year").pnl.agg(["count", "sum"]).round().reset_index()
    per_exit = good.sort_values("roi_pct", ascending=False).groupby("exit_rule").head(1)[cols]
    return [f"## {side} ({names}) - {len(E)} entries", "", "### Entries skipped / diagnostics", "", "```", json.dumps(st, indent=1), "```", "",
            f"### Top 15 variants by ROI (>= {MIN_TRADES} trades)", "", md(good.sort_values("roi_pct", ascending=False).head(15)[cols]), "",
            "### Best variant per time exit (by ROI)", "", md(per_exit), "",
            f"### Best variant by PnL: {bp.exit_rule} | {bp.sl_rule} | {bp.tp_rule} - by year", "", md(yr.rename(columns={"count": "trades", "sum": "pnl"})), ""]


def write_results(T, E, stats, done):
    os.makedirs(OUT, exist_ok=True)
    L = ["# PULLBACK re-cross on options - Dhan data - LONG and SHORT reported separately", "",
         f"**Status:** {'COMPLETE' if done else 'PARTIAL - run again'}  |  {START} .. {END}  |  Nifty filter: {NIFTY_MODE}  |  Cap Rs {CAP:,.0f}", "",
         "LONG = breakout above the 10-day high, pullback, re-cross up -> buy the CALL (Nifty must be green).  SHORT = breakdown below the 10-day low, bounce, re-cross down -> buy the PUT (Nifty must be red).  "
         "ATM at the entry minute (else nearest ITM), strike locked, fill = close of the entry-minute option candle.", ""]
    for side in SIDES:
        Ts = T[T.side == side] if T is not None and len(T) else None; Es = E[E.side == side] if E is not None and len(E) else None
        L += side_report(Ts, Es, stats.get(side, {}), side)
    L += ["The best of 80 variants is chosen after seeing the results, so it is optimistic: check that neighbouring variants and every year look similar. Charges and slippage are not included; "
          "option candles with no trade in a minute are missing, so illiquid-stock fills can be better than real. Files per side: summary_<SIDE>.csv, all_trades_<SIDE>.csv.gz, entries_<SIDE>.csv, best_variant_trades_<SIDE>.csv."]
    open(f"{OUT}/SUMMARY.md", "w").write("\n".join(L)); print("\n".join(L[:12]), flush=True)


def run(only_summary=False):
    global START, END
    os.makedirs(OUT, exist_ok=True); rp = f"{OUT}/rule.json"
    if os.path.exists(rp) and not _explicit:
        o = json.load(open(rp)); START, END = o["start"], o["end"]
    rule = dict(start=START, end=END, sls=SLS, tps=TPS, exits=EXITS, nifty=NIFTY_MODE, cap=CAP, window=WINDOW, dip=DIP, entry_last=ENTRY_LAST, sides=SIDES)
    if os.path.exists(rp) and json.load(open(rp)) != rule: sys.exit("STOP - saved data in " + OUT + " belongs to other settings:\n" + open(rp).read() + "\nuse another out_dir")
    json.dump(rule, open(rp, "w"), indent=1)
    keys = ["no_equity_id", "too_little_daily", "no_stock_minute_data", "no_cross_minute", "no_nifty_minute_data", "nifty_filter_failed",
            "no_option_candle_atm_or_itm", "no_lot_size", "one_lot_too_expensive"]
    stats = {sd: {k: 0 for k in keys} for sd in SIDES}
    dh = Dhan(); done = False; Ts, Es = [], []
    try:
        eqid, lots = load_master(); universe = SYMBOLS or sorted(lots)
        print(f"F&O stocks: {len(universe)}  | {START}..{END} | Nifty filter {NIFTY_MODE} | sides {SIDES}", flush=True)
        for sd in SIDES:
            ev = find_events(dh, eqid, lots, universe, stats[sd], sd)
            print(f"{sd}: entry minutes found: {len(ev)}", flush=True)
            if len(ev): t, e = trade_rows(dh, ev, stats); Ts.append(t); Es.append(e)
        done = True
    except Stop as e: print(f"STOPPED POLITELY: {e}. Run again to continue.", flush=True)
    finally:
        T = pd.concat(Ts) if Ts else None; E = pd.concat(Es) if Es else None
        write_results(T, E, stats, done); open(f"{OUT}/PROGRESS.txt", "w").write("COMPLETE" if done else "PARTIAL - run again"); print(f"API calls: {dh.n}")


def align_test(dh, sid, sym, n=6):
    """Compare the DAILY candle with the max/min of the 1-minute candles of the same day (and of the days before / after) - finds date or time shifts."""
    a = (pd.Timestamp(END) - pd.Timedelta(days=20)).strftime("%Y-%m-%d"); d = dh.daily(sid, "NSE_EQ", "EQUITY", a, END)
    print("daily candles (date, high, low, close):"); print(d.tail(n))
    for day in [x.strftime("%Y-%m-%d") for x in d.index[-n:-1]]:
        u = dh.minute(sid, "NSE_EQ", "EQUITY", day)
        if u.empty: print(day, "no minute data"); continue
        row = d.loc[pd.Timestamp(day)]
        print(f"{day}: minute candles {len(u)} {u.index[0].strftime('%H:%M')}..{u.index[-1].strftime('%H:%M')}  minute max high {u.h.max():.2f} min low {u.l.min():.2f}  | daily row high {row.h:.2f} low {row.l:.2f}  "
              f"{'OK' if abs(u.h.max() - row.h) < 0.01 * row.h else 'MISMATCH'}")


def check():
    dh = Dhan(); eqid, lots = load_master(); s = (SYMBOLS or ["RELIANCE"])[0]
    print(f"F&O stocks in the master: {len(lots)}; {s} lot {lots.get(s)}, equity id {eqid.get(s)}")
    a = (pd.Timestamp(END) - pd.Timedelta(days=12)).strftime("%Y-%m-%d"); print(dh.daily(eqid[s], "NSE_EQ", "EQUITY", a, END).tail(3))
    align_test(dh, eqid[s], s)
    day = dh.daily(eqid[s], "NSE_EQ", "EQUITY", a, END).index[-2].strftime("%Y-%m-%d")
    print("stock minute", day, len(dh.minute(eqid[s], "NSE_EQ", "EQUITY", day)), "| nifty minute", len(dh.minute("13", "IDX_I", "INDEX", day)))
    for sd, off in (("LONG", "ATM"), ("LONG", "ATM-1"), ("SHORT", "ATM"), ("SHORT", "ATM+1")): o = dh.option(eqid[s], day, off, sd); print("option", sd, off, len(o)); print(o.head(2))


if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if m == "check": check()
        elif m == "run": run()
        else: sys.exit("use: python pullback_options_backtest.py check | run")
    except Fatal as e: sys.exit(f"STOP - needs your action: {e}")
