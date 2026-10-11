"""n10y_backtest.py - Top-10 Nifty stocks "late-day cross, next-day entry" option backtest, last 3 years. Yahoo + DhanHQ, self-contained.

  python n10y_backtest.py check | run | summary | range

Strategy (daily candles from Yahoo; 1-minute candles of BOTH days from Dhan)
  LONG : reference line = 10-day high line (same as before: broke above, then closed back below).
         Signal day  : price crosses ABOVE the line at/after 14:00 (first 1-min touch >= 14:00) but the day CLOSES BELOW the line.
         Entry day   : next trading day, price crosses the line again -> buy ATM CALL.
  SHORT: mirror. Signal day: price crosses BELOW the line between 11:00 and 13:00 (first touch) but the day CLOSES ABOVE it.
         Entry day   : price crosses the line again -> buy ATM PUT.
  The old rule (small body + long wick on the signal-day candle) is NOT required, but every trade is flagged (shape=1/0) and all
  tables are produced twice: rule=NO_SHAPE_RULE (all signals) and rule=WITH_SHAPE_RULE (only signals that also pass it), to compare.
Entry types (entry day):
  ALL              first minute the line is touched (any cross, up to 15:00)
  FROM_0920_4C     first minute from 09:20 where the 4 previous candles stayed fully on the wrong side of the line (LONG: highs below,
                   SHORT: lows above) and this minute closes beyond the line = validated cross
  RECROSS_0920_4C  same validated cross from 09:20, but the line had ALREADY been touched before those 4 candles (second touch);
                   first_touch time is saved with every trade
Exits: SL 10/20 %, target 20..200 %, forced exit 09:30 / 10:00 / 12:00 / 15:30 same day, or UNTIL_HIT: hold the ATM option (strike fixed at entry)
until stop/target is hit, max HOLD_DAYS (5) trading days incl. entry day and never past the monthly expiry (last Tuesday); then 15:30 of the last day.
Overnight gaps through the stop fill at the open (reason STOP (gap), ret_pct shows the loss %). Capital cap Rs 2,00,000 (SL10) / 1,00,000 (SL20).
"""
import os, sys, io, json, time, gzip, glob, subprocess
import requests, numpy as np, pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
START = os.environ.get("N10Y_START") or str(date.today() - timedelta(days=1095))
END = os.environ.get("N10Y_END") or str(date.today())
SLS = [10, 20]
TPS = [20, 30, 40, 60, 80, 100, 120, 140, 200]
EXITS = ["09:30", "10:00", "12:00", "15:30"]
HOLD_DAYS = int(os.environ.get("HOLD_DAYS") or 5)      # UNTIL_HIT: hold the ATM option (entry strike) up to this many trading days (entry day = day 1)
CAPS = {10: 200000, 20: 100000}
ENTRY_LAST = "15:00"                                        # no entries after this time
OFFSETS = [int(x) for x in (os.environ.get("OFFSETS") or "0,1,-1,2,-2,3,-3").split(",")]    # ATM and neighbours (Dhan allows -3..+3 for stocks)
GAP_S = float(os.environ.get("DHAN_GAP", "0.35"))           # seconds between Dhan calls (limit is 5/second)
BUDGET_MIN = float(os.environ.get("BUDGET_MIN", "300"))     # stop politely after this many minutes
OUT = os.environ.get("N10Y_OUT", "n10y_results")
BASE = "https://api.dhan.co/v2"
MASTER = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
T0 = time.time()
LAST_CP = time.time()

UNIVERSE = """
    HDFCBANK RELIANCE ICICIBANK INFY BHARTIARTL ITC LT TCS AXISBANK SBIN
""".split()                                                    # the 10 biggest Nifty 50 stocks by weight - edit this list freely
SIG_LONG = ("14:00", "15:30")        # signal day: first cross above the line must be in this window
SIG_SHORT = ("11:00", "13:00")       # signal day: first cross below the line must be in this window


def shape(o, h, l, c):
    """Signal-day daily candle: body < 45% of range and a wick >= 2x body (the old rule). Only FLAGGED now, not required."""
    if h == l: return 0
    b = abs(c - o)
    return int(b / (h - l) < .45 and max(h - max(o, c), min(o, c) - l) >= 2 * b)


def setup(df, long):
    n, res = len(df) - 1, None
    hi, lo, c = df.High.values, df.Low.values, df.Close.values
    for i in range(10, n):
        w = (hi if long else lo)[i - 10:i]
        k = w.argmax() if long else w.argmin()
        ref, sw = w[k], i - 10 + k
        if not (c[i] > ref if long else c[i] < ref): continue
        if i - sw > 20 or n - i > 20: continue
        if not (c[n] < ref if long else c[n] > ref): continue
        pb = next(j for j in range(i + 1, n + 1) if (c[j] < ref if long else c[j] > ref))
        res = (ref, df.index[sw], df.index[i], df.index[pb])
    return res


# ------------------------------------------------------------------ Dhan client (paced, with back-off)
class Stop(Exception): pass          # polite stop: time budget used, or Dhan keeps refusing; progress is saved
class Fatal(Exception): pass         # needs your action (token expired, API not subscribed)


class Dhan:
    RATE_CODES = {"DH-904", "805", "DH-805"}
    AUTH_CODES = {"DH-901", "DH-902", "807", "808", "809", "810", "811", "DH-807", "DH-808", "DH-809", "DH-810", "DH-811"}

    def __init__(self):
        cid, tok = os.environ.get("DHAN_CLIENT_ID"), os.environ.get("DHAN_ACCESS_TOKEN")
        if not cid or not tok: raise Fatal("Missing DHAN_CLIENT_ID or DHAN_ACCESS_TOKEN secret")
        self.h = {"Accept": "application/json", "Content-Type": "application/json", "access-token": tok, "client-id": cid}
        self.last, self.n, self.rl, self.errs = 0.0, 0, 0, 0

    def post(self, path, body):
        if (time.time() - T0) / 60 > BUDGET_MIN: raise Stop(f"time budget of {BUDGET_MIN:.0f} min used")
        for attempt in range(8):
            w = GAP_S - (time.time() - self.last)
            if w > 0: time.sleep(w)
            self.last = time.time(); self.n += 1
            try:
                r = requests.post(BASE + path, headers=self.h, json=body, timeout=120)
            except Exception as e:
                print(f"[call {self.n}] network problem: {e}", flush=True); time.sleep(5 * (attempt + 1)); continue
            try: j = r.json()
            except Exception: j = None
            code = str(j.get("errorCode", "")) if isinstance(j, dict) else ""
            if r.status_code == 200 and j is not None and not code:
                self.rl = 0; return j
            if r.status_code == 429 or code in self.RATE_CODES:
                self.rl += 1
                if self.rl > 6: raise Stop("Dhan keeps refusing (rate limit) - wait a while and run again")
                s = min(30 * 2 ** (self.rl - 1), 600)
                print(f"[call {self.n}] rate limit ({code or r.status_code}) - waiting {s}s", flush=True); time.sleep(s); continue
            if r.status_code in (401, 403) or code in self.AUTH_CODES:
                raise Fatal(f"Dhan refused the login/token: http {r.status_code} {code} {str(j)[:200]}")
            self.errs += 1
            if self.errs <= 8: print(f"[call {self.n}] Dhan says: http {r.status_code} {str(j or r.text)[:200]}", flush=True)
            return None
        raise Stop("Dhan not reachable")


def frame(d, extra=()):
    """Dhan arrays -> DataFrame o,h,l,c (+extra) indexed by IST time (naive)."""
    if not isinstance(d, dict) or not d.get("timestamp"): return None
    cols = {"open": "o", "high": "h", "low": "l", "close": "c"}
    df = pd.DataFrame({v: d[k] for k, v in cols.items() if k in d})
    for e in extra:
        if e in d and len(d[e]) == len(df): df[e] = d[e]
    df.index = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert(IST).tz_localize(None)
    return df.astype(float).sort_index()


def eq_minute(dh, sid, d0, d1):
    """1-minute stock candles from d0 to d1 (dates), <= 90 days per request."""
    j = dh.post("/charts/intraday", {"securityId": str(sid), "exchangeSegment": "NSE_EQ", "instrument": "EQUITY", "interval": "1",
                                     "oi": False, "fromDate": f"{d0} 09:15:00", "toDate": f"{d1} 15:30:00"})
    if j is None: return None
    return frame(j.get("data", j) if isinstance(j.get("data", None), dict) else j)


def rolling(dh, sid, d0, d1, side, offset):
    """Rolling option candles (strike relative to spot, nearest monthly expiry), d0 <= date < d1, <= 30 days per request."""
    strike = "ATM" if offset == 0 else f"ATM{offset:+d}"
    j = dh.post("/charts/rollingoption", {
        "exchangeSegment": "NSE_FNO", "interval": "1", "securityId": int(sid), "instrument": "OPTSTK", "expiryFlag": "MONTH",
        "expiryCode": 1, "strike": strike, "drvOptionType": "CALL" if side == "LONG" else "PUT",
        "requiredData": ["open", "high", "low", "close", "volume", "strike", "spot"], "fromDate": str(d0), "toDate": str(d1)})
    if j is None: return None
    d = (j.get("data") or {}).get("ce" if side == "LONG" else "pe")
    return frame(d, extra=("strike", "spot"))


def load_master():
    """stock symbol -> (underlying security id, lot size) from Dhan's instrument list (stock options)."""
    txt = requests.get(MASTER, timeout=180).text
    m = pd.read_csv(io.StringIO(txt), low_memory=False)
    up = {c.strip().upper(): c for c in m.columns}
    need = {k: next((up[n] for n in names if n in up), None) for k, names in {
        "exch": ("EXCH_ID", "SEM_EXM_EXCH_ID"), "ins": ("INSTRUMENT", "SEM_INSTRUMENT_NAME"),
        "usym": ("UNDERLYING_SYMBOL",), "usid": ("UNDERLYING_SECURITY_ID",), "lot": ("LOT_SIZE", "SEM_LOT_UNITS"),
        "exp": ("SM_EXPIRY_DATE", "SEM_EXPIRY_DATE")}.items()}
    if None in need.values():
        raise Fatal(f"Dhan instrument list has different column names than expected. Columns: {list(m.columns)[:40]}")
    o = m[(m[need["exch"]] == "NSE") & (m[need["ins"]] == "OPTSTK")].copy()
    o["_e"] = pd.to_datetime(o[need["exp"]], errors="coerce")
    o = o.sort_values("_e")
    cur = o[o["_e"] >= pd.Timestamp.now().normalize()]
    out = {}
    for sym, g in (cur if len(cur) else o).groupby(need["usym"]):
        r = g.iloc[0]
        out[str(sym).strip()] = (int(float(r[need["usid"]])), int(float(r[need["lot"]])))
    return out


# ------------------------------------------------------------------ step 1: Yahoo daily -> candidate days
def yahoo_candidates():
    import yfinance as yf
    end = (date.today() + timedelta(days=1)).isoformat()
    raw = yf.download([s + ".NS" for s in UNIVERSE], start=str(pd.Timestamp(START) - pd.Timedelta(days=400)), end=end, group_by="ticker",
                      auto_adjust=False, progress=False, threads=True)
    rows, nst = [], 0
    for s in UNIVERSE:
        try: d = raw[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
        if len(d) < 60: continue
        nst += 1
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        for k in range(40, len(d) - 1):
            T = d.index[k + 1]
            if not (pd.Timestamp(START) <= T <= pd.Timestamp(END)): continue
            sub, nx, sg = d.iloc[:k + 1], d.iloc[k + 1], d.iloc[k]
            for long in (True, False):
                r = setup(sub, long)                                   # line + signal-day close on the wrong side already required
                if not r: continue
                ref = float(r[0])
                if not (sg.High >= ref if long else sg.Low <= ref): continue      # signal day crossed the line (but closed back)
                if not (nx.High >= ref if long else nx.Low <= ref): continue      # entry day touches the line
                rows.append(dict(stock=s, direction="LONG" if long else "SHORT", ref=round(ref, 2),
                                 signal_date=str(d.index[k].date()), signal_close=float(sg.Close), shape=shape(sg.Open, sg.High, sg.Low, sg.Close), date=str(T.date()), yahoo_close=float(nx.Close)))
    print(f"Yahoo: {nst} stocks, {len(rows)} candidate stock-days (signal day crossed and closed back; entry day touches the line)", flush=True)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ step 2: entries from Dhan stock minutes
def hm(t): return f"{t:%H:%M}"


def sig_cross(u, ref, long):
    """Signal day, 1-minute candles: time of the first touch of the line and whether it falls in the allowed window."""
    touch = ((u.h >= ref) if long else (u.l <= ref)).values
    if not touch.any(): return None
    t = hm(u.index[np.argmax(touch)])
    lo, hi = SIG_LONG if long else SIG_SHORT
    return t if lo <= t <= hi else None


def find_events(u, ref, long):
    """u = entry-day 1-minute candles. -> {entry type: (entry minute, first touch minute)}"""
    touch = ((u.h >= ref) if long else (u.l <= ref)).values
    ev = {}
    if not touch.any(): return ev
    idx, h, l, c = u.index, u.h.values, u.l.values, u.c.values
    tc = idx[np.argmax(touch)]
    if hm(tc) <= ENTRY_LAST: ev["ALL"] = (tc, tc)                       # every cross: first touch of the line
    for k in range(4, len(u)):
        t = hm(idx[k])
        if t < "09:20": continue
        if t > ENTRY_LAST: break
        if not ((h[k - 4:k] < ref).all() if long else (l[k - 4:k] > ref).all()): continue     # 4 previous candles fully on the wrong side
        if not (c[k] >= ref if long else c[k] <= ref): continue                                # this minute closes beyond the line
        ev.setdefault("FROM_0920_4C", (idx[k], tc))                                            # validated cross after 09:20
        if tc < idx[k - 4]: ev.setdefault("RECROSS_0920_4C", (idx[k], tc))                     # line was touched earlier = second touch
        if "RECROSS_0920_4C" in ev: break
    return ev


def windows(dates, span):
    out = []
    for d in sorted(dates):
        if out and (d - out[-1][0]).days < span: out[-1][1] = d
        else: out.append([d, d])
    return out


def checkpoint(force=False):
    """On GitHub Actions: save progress to the repo every ~15 minutes, so a crash or timeout never loses hours of work."""
    global LAST_CP
    if not os.environ.get("GITHUB_ACTIONS"): return
    if not force and time.time() - LAST_CP < 900: return
    LAST_CP = time.time()
    steps = [["git", "config", "user.name", "n10y-bot"], ["git", "config", "user.email", "n10y-bot@users.noreply.github.com"],
             ["git", "add", OUT], ["git", "commit", "-m", "n10y progress"],
             ["git", "pull", "--no-rebase", "-X", "ours", "--no-edit"], ["git", "push"]]
    for c in steps:
        r = subprocess.run(c, capture_output=True, text=True)
        if r.returncode and c[1] != "commit":
            print(f"checkpoint: '{' '.join(c)}' failed: {(r.stdout + r.stderr)[-300:]}", flush=True); return
    print("checkpoint: progress saved to the repo", flush=True)


def load_state():
    p = f"{OUT}/state.json"
    s = json.load(open(p)) if os.path.exists(p) else {}
    s.setdefault("eq_done", []); s.setdefault("opt_done", [])
    return s


def save_state(s): json.dump(s, open(f"{OUT}/state.json", "w"))


def step_events(dh, cand, mst, st):
    ep = f"{OUT}/events.csv"
    ev = pd.read_csv(ep).to_dict("records") if os.path.exists(ep) else []
    for s, g in cand.groupby("stock"):
        if s not in mst: print(f"{s}: not in Dhan stock-option list - skipped", flush=True); continue
        g = g.copy(); g["d"] = pd.to_datetime(g["date"]).dt.date
        for d0, d1 in windows(g.d.tolist(), 80):
            key = f"{s}|{d0}|{d1}"
            if key in st["eq_done"]: continue
            u_all = eq_minute(dh, mst[s][0], d0 - timedelta(days=6), d1)       # also covers the signal day before the first entry day
            n_ev = 0
            if u_all is not None:
                for r in g[(g.d >= d0) & (g.d <= d1)].itertuples():
                    u = u_all[u_all.index.date == r.d]
                    us = u_all[u_all.index.date == pd.Timestamp(r.signal_date).date()]
                    if u.empty or us.empty: continue
                    long = r.direction == "LONG"
                    ref, ratio = float(r.ref), float(u.c.iloc[-1]) / float(r.yahoo_close)
                    if abs(ratio - 1) > .2: ref *= ratio                       # split/bonus: Yahoo prices adjusted, Dhan raw
                    sc = sig_cross(us, ref, long)
                    if sc is None: continue                                     # signal-day cross not in the required time window
                    if not (us.c.iloc[-1] < ref if long else us.c.iloc[-1] > ref): continue    # and the day really closed back
                    for typ, (m, ft) in find_events(u, ref, long).items():
                        ev.append(dict(stock=s, direction=r.direction, ref=round(ref, 2), date=str(r.d), signal_date=r.signal_date,
                                       signal_cross=sc, shape=int(r.shape), type=typ, entry_minute=hm(m), first_touch=hm(ft), stock_price=float(u.c[m]))); n_ev += 1
            st["eq_done"].append(key)
            pd.DataFrame(ev).to_csv(ep, index=False); save_state(st); checkpoint()
            print(f"stock minutes {s} {d0}..{d1}: {n_ev} entry events", flush=True)
    return pd.DataFrame(ev)


# ------------------------------------------------------------------ step 3: option candles -> trades
def simulate(o, h, l, c, ts, entry, sl_pct, tp_pct):
    """Walk candles after entry. -> (index, price, reason) ; index None = no hit."""
    sl, tp = entry * (1 - sl_pct / 100), entry * (1 + tp_pct / 100)
    hit = (l <= sl) | (h >= tp)
    if not hit.any(): return None
    i = int(np.argmax(hit))
    if o[i] <= sl: return i, o[i], "STOP (gap)"
    if l[i] <= sl: return i, sl, "STOP"
    if o[i] >= tp: return i, tp, "TARGET (gap)"          # gap-up fills are capped at the target price
    return i, tp, "TARGET"


def expiry_of(d):
    """Monthly stock-option expiry that Dhan's 'nearest month' contract has on day d (last Tuesday of the month; next month once passed)."""
    def last_tue(y, m):
        x = date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)
        while x.weekday() != 1: x -= timedelta(days=1)
        return x
    e = last_tue(d.year, d.month)
    return e if d <= e else last_tue(d.year + (d.month == 12), d.month % 12 + 1)


def step_options(dh, ev, mst, st):
    os.makedirs(f"{OUT}/parts", exist_ok=True)
    for (s, dr), g in ev.groupby(["stock", "direction"]):
        g = g.copy(); g["d"] = pd.to_datetime(g["date"]).dt.date
        for d0, d1 in windows(g.d.unique().tolist(), 20):          # +10 days of option data after the last entry day (hold up to 5 trading days)
            key = f"{s}|{dr}|{d0}"
            if key in st["opt_done"]: continue
            sid, lot = mst[s]
            series = []
            for off in OFFSETS:
                x = rolling(dh, sid, d0, min(d1 + timedelta(days=11), date.today() + timedelta(days=1)), dr, off)
                if x is not None: x["off"] = off; series.append(x)
            rows = []
            if series and any(x["off"].iloc[0] == 0 for x in series):
                allr = pd.concat(series).reset_index().rename(columns={"index": "ts"})
                if "strike" not in allr: print(f"{s}: Dhan sent no strike column - skipped", flush=True); st["opt_done"].append(key); save_state(st); continue
                allr["day"] = allr.ts.dt.date
                for e in g[(g.d >= d0) & (g.d <= d1)].itertuples():
                    D = allr[allr.day == e.d]
                    atm = D[D.off == 0].drop_duplicates("ts").sort_values("ts")
                    m = pd.Timestamp(f"{e.date} {e.entry_minute}")
                    a = atm[atm.ts >= m]
                    if a.empty or (a.ts.iloc[0] - m) > pd.Timedelta(minutes=10): continue
                    te, K, entry = a.ts.iloc[0], float(a.strike.iloc[0]), float(a.c.iloc[0])      # ATM strike at the entry minute
                    if not entry > 0: continue
                    exp = expiry_of(e.d)
                    days = sorted(x for x in allr[(allr.day >= e.d) & (allr.day <= exp)].day.unique())[:HOLD_DAYS]
                    full = allr[(allr.strike == K) & (allr.ts > te) & allr.day.isin(days)].drop_duplicates("ts").sort_values("ts")
                    ser = full[full.day == e.d]
                    mins = ser.ts.dt.hour.values * 60 + ser.ts.dt.minute.values
                    variants = []
                    for ex in EXITS:
                        lim = int(ex[:2]) * 60 + int(ex[3:])
                        if hm(te) >= ex: continue                             # entered after this square-off time
                        variants.append((ex, ser[mins <= lim], lim))
                    variants.append(("UNTIL_HIT", full, 15 * 60 + 30))        # stays open up to HOLD_DAYS days; last day closes at 15:30
                    for ex, w, lim in variants:
                        if w.empty: continue
                        o, hh, ll, cc = (w[k].values for k in ("o", "h", "l", "c"))
                        for sl in SLS:
                            lots = int(CAPS[sl] // (entry * lot))
                            if lots < 1: continue
                            qty, cost = lot * lots, entry * lot * lots
                            for tp in TPS:
                                r = simulate(o, hh, ll, cc, w.ts.values, entry, sl, tp)
                                if r: i, px, why = r; xt = w.ts.iloc[i]
                                else: i, px, why = len(w) - 1, cc[-1], "TIME"; xt = w.ts.iloc[-1]
                                late = why == "TIME" and (lim - (xt.hour * 60 + xt.minute)) > 5      # strike data thin near the exit time
                                nd = sum(1 for x in days if e.d <= x <= xt.date())
                                rows.append((s, dr, e.type, e.date, e.signal_date, e.signal_cross, int(e.shape), e.first_touch, hm(te), K, round(entry, 2), ex, sl, tp, lots, round(cost),
                                             hm(xt), round(px, 2), why, round((px - entry) * qty), int(late), round(float(e.stock_price), 2),
                                             str(xt.date()), nd, round((px / entry - 1) * 100, 1)))
            if rows:
                cols = ["stock", "direction", "type", "date", "signal_date", "signal_cross", "shape", "first_touch", "entry_time", "strike", "entry", "exit_rule", "sl", "tp", "lots",
                        "cost", "exit_time", "exit_price", "reason", "pnl", "thin_data", "stock_price", "exit_date", "days_held", "ret_pct"]
                pd.DataFrame(rows, columns=cols).to_csv(f"{OUT}/parts/{s}_{dr}_{d0}.csv.gz", index=False, compression="gzip")
            st["opt_done"].append(key); save_state(st); checkpoint()
            print(f"options {s} {dr} {d0}..{d1}: {len(rows)} result rows, calls so far {dh.n}", flush=True)


# ------------------------------------------------------------------ step 4: summary
def agg(g):
    w = g.pnl > 0
    gain, loss = g.pnl[w].sum(), -g.pnl[~w].sum()
    return pd.Series(dict(trades=len(g), wins=int(w.sum()), win_pct=round(w.mean() * 100, 1),
                          stops=int(g.reason.str.startswith("STOP").sum()), targets=int(g.reason.str.startswith("TARGET").sum()),
                          time_exits=int((g.reason == "TIME").sum()), total_pnl=int(g.pnl.sum()), capital=int(g.cost.sum()),
                          roi_pct=round(g.pnl.sum() / g.cost.sum() * 100, 2), avg_pnl=int(g.pnl.mean()),
                          profit_factor=round(gain / loss, 2) if loss > 0 else None, thin_data=int(g.thin_data.sum())))


def agg_hit(g):
    """Only trades that ended by a stop or a target hit (time-based exits left out)."""
    h = g[g.reason != "TIME"]
    t = g[g.reason == "TIME"]
    tg, st_ = h[h.reason.str.startswith("TARGET")], h[h.reason.str.startswith("STOP")]
    return pd.Series(dict(all_trades=len(g), hit_trades=len(h), targets=len(tg), stops=len(st_),
                          hit_win_pct=round(len(tg) / len(h) * 100, 1) if len(h) else None,
                          hit_pnl=int(h.pnl.sum()), hit_capital=int(h.cost.sum()),
                          hit_roi_pct=round(h.pnl.sum() / h.cost.sum() * 100, 2) if len(h) else None,
                          avg_target_pnl=int(tg.pnl.mean()) if len(tg) else None, avg_stop_pnl=int(st_.pnl.mean()) if len(st_) else None,
                          time_exits=len(t), time_exit_pnl=int(t.pnl.sum()), time_exit_win_pct=round((t.pnl > 0).mean() * 100, 1) if len(t) else None,
                          all_pnl=int(g.pnl.sum()), all_roi_pct=round(g.pnl.sum() / g.cost.sum() * 100, 2)))


def with_variants(t):
    """NO_SHAPE_RULE = every signal; WITH_SHAPE_RULE = only signals whose previous-day candle also has small body + long wick."""
    a = t.copy(); a["rule"] = "NO_SHAPE_RULE"
    b = t[t["shape"] == 1].copy(); b["rule"] = "WITH_SHAPE_RULE"
    return pd.concat([a, b], ignore_index=True)


def combine_all(fs):
    """Every trade row of every stock in plain CSV files (each < 45 MB) + one .gz, in <OUT>/all_trades_combined/ - to filter yourself."""
    out = f"{OUT}/all_trades_combined"; os.makedirs(out, exist_ok=True)
    for f in glob.glob(f"{out}/all_trades*"): os.remove(f)
    lim, header, n_rows, n_part, size, fh = 45 * 1024 * 1024, None, 0, 0, 0, None
    gz = gzip.open(f"{out}/all_trades.csv.gz", "wt", newline="", compresslevel=6)
    try:
        for f in fs:
            df = pd.read_csv(f)
            if header is None: header = list(df.columns); gz.write(",".join(header) + "\n")
            text = df.reindex(columns=header).to_csv(index=False, header=False)
            gz.write(text)
            if fh is None or size + len(text) > lim:
                if fh: fh.close()
                n_part += 1; fh = open(f"{out}/all_trades_{n_part:02d}.csv", "w", newline=""); fh.write(",".join(header) + "\n"); size = 0
            fh.write(text); size += len(text); n_rows += len(df)
    finally:
        gz.close()
        if fh: fh.close()
    if n_part == 1: os.rename(f"{out}/all_trades_01.csv", f"{out}/all_trades.csv")
    print(f"ALL TRADES: {n_rows:,} rows -> {out}/ ({n_part} CSV file(s) + all_trades.csv.gz)", flush=True)


def summary():
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    if not fs: print("No results yet"); return
    combine_all(fs)
    t = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    t = with_variants(t)
    t["year"] = t.date.str[:4]
    key = ["rule", "type", "exit_rule", "sl", "tp"]
    mt = int(os.environ.get("MIN_TRADES") or 5)
    a = t.groupby(key).apply(agg).reset_index()
    a.to_csv(f"{OUT}/summary_all.csv", index=False)
    a[a.trades >= mt].sort_values("roi_pct", ascending=False).head(60).to_csv(f"{OUT}/summary_top60_roi.csv", index=False)
    a[a.trades >= mt].sort_values("total_pnl", ascending=False).head(60).to_csv(f"{OUT}/summary_top60_pnl.csv", index=False)
    a.loc[a[a.trades >= mt].groupby(["rule", "type"]).roi_pct.idxmax()].to_csv(f"{OUT}/summary_best_per_type.csv", index=False)
    hh = t.groupby(key).apply(agg_hit).reset_index()
    hh.to_csv(f"{OUT}/summary_hit_only_all.csv", index=False)
    hh[hh.hit_trades >= mt].sort_values("hit_roi_pct", ascending=False).head(60).to_csv(f"{OUT}/summary_hit_only_top60_roi.csv", index=False)
    hh[hh.hit_trades >= mt].sort_values("hit_pnl", ascending=False).head(60).to_csv(f"{OUT}/summary_hit_only_top60_pnl.csv", index=False)
    t.groupby(["rule", "type", "year"]).apply(agg).reset_index().to_csv(f"{OUT}/summary_type_by_year.csv", index=False)
    print(f"{len(t):,} result rows from {len(fs)} files")
    print("\nBEST COMBINATION PER ENTRY TYPE (>= min trades, by ROI):\n" + pd.read_csv(f"{OUT}/summary_best_per_type.csv").to_string(index=False))
    print("\nHIT-ONLY (stop or target hit; time exits left out) TOP 15 BY ROI:\n" + hh[hh.hit_trades >= mt].sort_values("hit_roi_pct", ascending=False).head(15).to_string(index=False))
    print("\nTOP 15 BY ROI:\n" + a[a.trades >= mt].sort_values("roi_pct", ascending=False).head(15).to_string(index=False))


def range_summary(start, end, mt):
    """Tables + trade lists for the entry dates you choose (no API calls). Own folder per range."""
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    if not fs: sys.exit(f"No saved results in {OUT}/parts - run the backtest first")
    t = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    t = t[(t.date >= start) & (t.date <= end)]
    t = with_variants(t)
    if t.empty: sys.exit(f"No trades with entry date between {start} and {end}")
    out = f"n10y_range_out/{start}_to_{end}"; os.makedirs(out, exist_ok=True)
    print(f"{len(t):,} result rows, entry dates {t.date.min()} to {t.date.max()}")
    ecols = ["date", "stock", "direction", "type", "signal_date", "signal_cross", "shape", "first_touch", "entry_time", "strike", "entry", "stock_price"]
    t.drop_duplicates(["rule", "stock", "date", "type"])[["rule"] + ecols].sort_values(["date", "stock", "type", "rule"]).to_csv(f"{out}/entries_in_range.csv", index=False)
    sel, chosen = t, False
    for col, env in (("rule", "SHAPE_RULE"), ("type", "ENTRY_TYPE"), ("exit_rule", "EXIT_RULE"), ("sl", "SL"), ("tp", "TP")):
        v = os.environ.get(env, "").strip()
        if v and v.lower() != "all": sel = sel[sel[col].astype(str) == v]; chosen = True
    if chosen:
        sel.sort_values(["rule", "date", "stock", "entry_time"]).to_csv(f"{out}/trades_selected.csv", index=False)
        print(f"trades_selected.csv: {len(sel):,} trades")
    key = ["rule", "type", "exit_rule", "sl", "tp"]
    a, h = t.groupby(key).apply(agg).reset_index(), t.groupby(key).apply(agg_hit).reset_index()
    a.to_csv(f"{out}/all_trades_all.csv", index=False); h.to_csv(f"{out}/hit_only_all.csv", index=False)
    g = a[a.trades >= mt]
    g.sort_values("roi_pct", ascending=False).head(60).to_csv(f"{out}/all_trades_top60_roi.csv", index=False)
    g.sort_values("total_pnl", ascending=False).head(60).to_csv(f"{out}/all_trades_top60_pnl.csv", index=False)
    h[h.hit_trades >= mt].sort_values("hit_roi_pct", ascending=False).head(60).to_csv(f"{out}/hit_only_top60_roi.csv", index=False)
    if len(g):
        g.loc[g.groupby(["rule", "type"]).roi_pct.idxmax()].to_csv(f"{out}/best_per_entry_type.csv", index=False)
        print("\nBEST COMBINATION PER ENTRY TYPE (by ROI):\n" + pd.read_csv(f"{out}/best_per_entry_type.csv").to_string(index=False))
    else: print(f"No combination has {mt} trades - lower the minimum trades")
    print(f"\nSaved in {out}/")


# ------------------------------------------------------------------ modes
def check():
    dh = Dhan()
    mst = load_master()
    print(f"Instrument list OK: {len(mst)} stocks with options. RELIANCE ->", mst.get("RELIANCE"), flush=True)
    miss = [s for s in UNIVERSE if s not in mst]
    print(f"{len(UNIVERSE) - len(miss)} of {len(UNIVERSE)} universe stocks found in Dhan list. Missing: {miss[:30]}", flush=True)
    sid = mst["RELIANCE"][0]
    d1 = date.today(); d0 = d1 - timedelta(days=10)
    u = eq_minute(dh, sid, d0, d1)
    print("Stock minute call:", "no data" if u is None else f"{len(u)} candles, {u.index[0]} .. {u.index[-1]}")
    if u is not None: print(u.tail(3))
    x = rolling(dh, sid, d0, d1, "LONG", 0)
    print("Rolling option call:", "no data" if x is None else f"{len(x)} candles")
    if x is not None: print(x.tail(3))
    print(f"Dhan calls used: {dh.n}")


def run():
    os.makedirs(OUT, exist_ok=True)
    st = load_state()
    cp = f"{OUT}/candidates_{START}_{END}.csv"
    if os.path.exists(cp): cand = pd.read_csv(cp)
    else:
        cand = yahoo_candidates(); cand.to_csv(cp, index=False)
    cand = cand[(cand["date"] >= START) & (cand["date"] <= END)]
    print(f"Candidates {START} to {END}: {len(cand)} stock-days", flush=True)
    dh = Dhan(); mst = load_master()
    try:
        ev = step_events(dh, cand, mst, st)
        if len(ev): ev = ev[(ev["date"] >= START) & (ev["date"] <= END)]
        print(f"Entry events: {len(ev)}", flush=True)
        if len(ev): step_options(dh, ev, mst, st)
        print("ALL STEPS FINISHED", flush=True)
    except Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        print(f"Dhan calls this run: {dh.n}", flush=True)
        summary()
        checkpoint(True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": check()
        elif mode == "run": run()
        elif mode == "summary": summary()
        elif mode == "range": range_summary(START, END, int(os.environ.get("MIN_TRADES") or 5))
        else: sys.exit("use: python n10y_backtest.py check | run | summary | range")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
