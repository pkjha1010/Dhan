import os, sys, io, json, time, gzip, glob, subprocess, threading
from concurrent.futures import ThreadPoolExecutor
import requests, numpy as np, pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
START = os.environ.get("SHAPECMP_START") or str(date.today() - timedelta(days=4 * 365))
END = os.environ.get("SHAPECMP_END") or str(date.today())
SLS = [10, 20, 30]
EXITS = ["09:30", "10:00"]
CAPS = {10: 200000, 20: 100000, 30: 66667}
ENTRY_LAST = "09:59"                                          # entries must come before the last exit time (10:00)
PRE_TOL = float(os.environ.get("PRE_TOL") or 0.04)            # daily-open prefilter: open within 4 % of the line (entry must come in the first 45 minutes)
EXTRA = [int(x) for x in (os.environ.get("OFFSETS2") or "1,-1").split(",") if x.strip()]    # neighbouring strikes, fetched only when needed
BUDGET_MIN = float(os.environ.get("BUDGET_MIN", "300"))       # stop politely after this many minutes
OUT = os.environ.get("SHAPECMP_OUT", "shapecmp_results")
BASE = "https://api.dhan.co/v2"
MASTER = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
T0 = time.time()
LAST_CP = time.time()
EK = ["stock", "direction", "type", "date", "exit_rule", "sl"]    # one trade row
DK = ["stock", "direction", "type", "date"]                       # one entry event

# Token Bucket Configurations
MAX_RATE = 4.8  # Target safely under Dhan's 5 requests/sec ceiling
CONC = 8        # Parallel threads to maintain deep request pipelines

UNIVERSE = """
    360ONE ABCAPITAL ADANIENSOL ABB ADANIPORTS AMBER ASIANPAINT AMBUJACEM
    ADANIENT BAJAJ-AUTO BAJAJHLDNG APLAPOLLO ADANIGREEN AUROPHARMA AXISBANK
    BOSCHLTD BRITANNIA CDSL BANDHANBNK BANKBARODA BDL BHARATFORG COALINDIA
    BHARTIARTL BLUESTARCO BPCL ALKEM CAMS CHOLAFIN CIPLA COCHINSHIP COLPAL
    COFORGE CROMPTON CONCOR DABUR ANGELONE APOLLOHOSP DELHIVERY DIVISLAB DLF
    DMART DRREDDY DIXON ETERNAL FORCEMOT FORTIS GLENMARK GODFRYPHLP BANKINDIA
    GODREJPROP GODREJCP HCLTECH HDFCBANK GRASIM GVT&D HAVELLS HDFCLIFE BEL
    BHEL HINDALCO BIOCON HINDUNILVR HINDZINC IDFCFIRSTB INDUSINDBK ICICIGI
    CGPOWER IRFC JINDALSTEL JIOFIN IEX INDHOTEL INDIANB JSWENERGY JSWSTEEL
    KAYNES KEI INFY INOXWIND ITC KPITTECH JUBLFOOD LT M&M KALYANKJIL MANKIND
    MARICO ADANIPOWER MCX NAM-INDIA KFINTECH NESTLEIND EICHERMOT LODHA
    FEDERALBNK OBEROIRLTY LTM LUPIN PAGEIND MANAPPURAM PAYTM PFC PGEL MARUTI
    MAXHEALTH PHOENIXLTD PNB MOTHERSON POLYCAB POWERINDIA NMDC OFSS PRESTIGE
    OIL ONGC PATANJALI RECLTD SBILIFE GMRAIRPORT SBIN SHREECEM TATACONSUM
    PETRONET TATAELXSI TATASTEEL TMPV UPL PIDILITIND WAAREEENER PIIND
    BAJAJFINSV POLICYBZR PREMIERENE RADICO RBLBANK SAIL SOLARINDS SUNPHARMA
    SUPREMEIND SUZLON SWIGGY TATAPOWER TCS TIINDIA TITAN TVSMOTOR UNIONBANK
    VBL VEDL ZYDUSLIFE HEROMOTOCO HYUNDAI ICICIBANK INDIGO BSE LICHSGFIN LTF
    HDFCAMC MOTILALOFS MPHASIS NATIONALUM NBCC NYKAA ICICIPRULI PERSISTENT
    PNBHOUSING POWERGRID LAURUSLABS RELIANCE MAZDOCK SONACOMS NAUKRI SRF TECHM
    ULTRACEMCO UNOMINDA VMM WIPRO ASTRAL BAJFINANCE UNITDSPR ASHOKLEY
    MUTHOOTFIN CUMMINSIND GAIL SIEMENS MFSL NHPC NTPC TORNTPHARM RVNL
    KOTAKBANK LICI AUBANK HAL IDEA INDUSTOWER IOC IREDA TRENT SBICARD
    SHRIRAMFIN CANBK YESBANK VOLTAS HINDPETRO ATHERENERG MAHABANK SAGILITY
""".split()


class Stop(Exception): pass          # polite stop: time budget used, or Dhan keeps refusing; progress is saved
class Fatal(Exception): pass         # needs your action (token expired, API not subscribed)


class Dhan:
    RATE_CODES = {"DH-904", "805", "DH-805"}
    AUTH_CODES = {"DH-901", "DH-902", "807", "808", "809", "810", "811", "DH-807", "DH-808", "DH-809", "DH-810", "DH-811"}

    def __init__(self):
        cid, tok = os.environ.get("DHAN_CLIENT_ID"), os.environ.get("DHAN_ACCESS_TOKEN")
        if not cid or not tok: raise Fatal("Missing DHAN_CLIENT_ID or DHAN_ACCESS_TOKEN secret")
        self.h = {"Accept": "application/json", "Content-Type": "application/json", "access-token": tok, "client-id": cid}
        self.n = 0
        self.errs = 0
        self.lock = threading.Lock()
        self.stats = {}
        
        # Token Bucket State Management
        self.tokens = MAX_RATE
        self.updated_at = time.time()

    def _wait_for_token(self):
        """Executes algorithmic pacing based on fractional token slices to prevent request drift."""
        with self.lock:
            while True:
                now = time.time()
                self.tokens = min(MAX_RATE, self.tokens + (now - self.updated_at) * MAX_RATE)
                self.updated_at = now
                
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    self.n += 1
                    return
                
                # Precise math sleep down to target slice boundary
                sleep_time = (1.0 - self.tokens) / MAX_RATE
                time.sleep(sleep_time)

    def post(self, path, body):
        if (time.time() - T0) / 60 > BUDGET_MIN: raise Stop(f"time budget of {BUDGET_MIN:.0f} min used")
        for attempt in range(5):
            self._wait_for_token()
            try:
                t_req = time.time()
                r = requests.post(BASE + path, headers=self.h, json=body, timeout=30)
                with self.lock:
                    st_ = self.stats.setdefault(path, [0, 0.0]); st_[0] += 1; st_[1] += time.time() - t_req
            except Exception as e:
                print(f"[call {self.n}] network problem: {e}", flush=True)
                time.sleep(1)
                continue
            try: j = r.json()
            except Exception: j = None
            code = str(j.get("errorCode", "")) if isinstance(j, dict) else ""
            if r.status_code == 200 and j is not None and not code:
                return j
            if r.status_code == 429 or code in self.RATE_CODES:
                print(f"[call {self.n}] micro rate limit hit ({code or r.status_code}) - backing off 0.5s", flush=True)
                time.sleep(0.5)
                continue
            if r.status_code in (401, 403) or code in self.AUTH_CODES:
                raise Fatal(f"Dhan refused the login/token: http {r.status_code} {code} {str(j)[:200]}")
            self.errs += 1
            if self.errs <= 8: print(f"[call {self.n}] Dhan says: http {r.status_code} {str(j or r.text)[:200]}", flush=True)
            return None
        raise Stop("Dhan not reachable or constantly rate-limiting")


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


def prep_lines(d, long):
    """Reference line candidates for every day (max of the previous 10 highs / min of the previous 10 lows) and whether that day broke it."""
    c = d.Close.values
    if long: ref = d.High.shift(1).rolling(10).max().values; brk = c > ref
    else: ref = d.Low.shift(1).rolling(10).min().values; brk = c < ref
    return ref, brk & ~np.isnan(ref)


def pick_line(ref, brk, c, n, long):
    """Same result as setup(): latest breakout day i in [n-20, n-1] whose line the signal day n closed back through."""
    ii = np.arange(max(10, n - 20), n)
    if not len(ii): return None
    m = brk[ii] & ((c[n] < ref[ii]) if long else (c[n] > ref[ii]))
    return float(ref[ii[m][-1]]) if m.any() else None


def shape(o, h, l, c):
    """Previous-candle shape rule: body < 45 % of the range and a wick >= 2 x body."""
    if h == l: return 0
    b = abs(c - o)
    return int(b / (h - l) < .45 and max(h - max(o, c), min(o, c) - l) >= 2 * b)


def yahoo_candidates():
    import yfinance as yf
    raw = yf.download([s + ".NS" for s in UNIVERSE], period="max", group_by="ticker", auto_adjust=False, progress=False, threads=True)
    rows, nst = [], 0
    for s in UNIVERSE:
        try: d = raw[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
        if len(d) < 60: continue
        nst += 1
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        c, O, H, L = d.Close.values, d.Open.values, d.High.values, d.Low.values
        lines = {True: prep_lines(d, True), False: prep_lines(d, False)}
        for k in range(40, len(d) - 1):                                  # k = previous day (signal), k+1 = entry day
            T = d.index[k + 1]
            if not (pd.Timestamp(START) <= T <= pd.Timestamp(END)): continue
            for long in (True, False):
                ref = pick_line(lines[long][0], lines[long][1], c, k, long)          # previous day closed back beyond the line
                if ref is None: continue
                if long and not (H[k + 1] >= ref and O[k + 1] >= ref * (1 - PRE_TOL)): continue
                if not long and not (L[k + 1] <= ref and O[k + 1] <= ref * (1 + PRE_TOL)): continue
                rows.append(dict(stock=s, direction="LONG" if long else "SHORT", ref=round(ref, 2), signal_date=str(d.index[k].date()),
                                 date=str(T.date()), shape=shape(O[k], H[k], L[k], c[k]), yahoo_open=float(O[k + 1]), yahoo_close=float(c[k + 1])))
    if nst == 0: raise Fatal("Yahoo download gave no data for any stock (see the 'Failed downloads' lines above) - run again later")
    r = pd.DataFrame(rows)
    print(f"Yahoo: {nst} stocks, {len(r)} candidate days ({int(r['shape'].sum()) if len(r) else 0} of them also pass the shape rule)", flush=True)
    return r


def hm(t): return f"{t:%H:%M}"


def clusters(dates, span=30, gap=6):
    """Group dates into few Dhan requests: a group ends when it would cover > span days or when the next date is > gap days away."""
    out = []
    for d in sorted(dates):
        if out and (d - out[-1][1]).days <= gap and (d - out[-1][0]).days < span: out[-1][1] = d
        else: out.append([d, d])
    return out


def checkpoint(force=False):
    """On GitHub Actions: save progress to the repo every ~15 minutes, so a crash or timeout never loses hours of work."""
    global LAST_CP
    if not os.environ.get("GITHUB_ACTIONS"): return
    if not force and time.time() - LAST_CP < 900: return
    LAST_CP = time.time()
    steps = [["git", "config", "user.name", "shapecmp-bot"], ["git", "config", "user.email", "shapecmp-bot@users.noreply.github.com"],
             ["git", "add", OUT], ["git", "commit", "-m", "shapecmp progress"],
             ["git", "pull", "--no-rebase", "-X", "ours", "--no-edit"], ["git", "push"]]
    for c in steps:
        r = subprocess.run(c, capture_output=True, text=True)
        if r.returncode and c[1] != "commit":
            print(f"checkpoint: '{' '.join(c)}' failed: {(r.stdout + r.stderr)[-300:]}", flush=True); return
    print("checkpoint: progress saved to the repo", flush=True)


def load_state():
    p = f"{OUT}/state.json"
    s = json.load(open(p)) if os.path.exists(p) else {}
    s.setdefault("done", []); s.setdefault("expected", []); s.setdefault("expected_eq", [])
    return s


def save_state(s): json.dump(s, open(f"{OUT}/state.json", "w"))


def find_events(u, ref, long):
    """u = entry-day 1-minute candles (09:15-09:59). -> {entry type: (entry minute, first touch minute)}"""
    touch = ((u.h >= ref) if long else (u.l <= ref)).values
    ev = {}
    if not touch.any(): return ev
    idx, h, l, c = u.index, u.h.values, u.l.values, u.c.values
    tc = idx[np.argmax(touch)]
    if hm(tc) <= ENTRY_LAST: ev["ALL"] = (tc, tc)
    if hm(tc) == "09:15": ev["OPEN_0915"] = (tc, tc)
    for k in range(4, len(u)):
        t = hm(idx[k])
        if t < "09:20": continue
        if t > ENTRY_LAST: break
        if not ((h[k - 4:k] < ref).all() if long else (l[k - 4:k] > ref).all()): continue      # 4 previous candles fully on the wrong side
        if not (c[k] >= ref if long else c[k] <= ref): continue                                 # this minute closes beyond the line
        ev.setdefault("FROM_0920_4C", (idx[k], tc))
        if tc < idx[k - 4]: ev.setdefault("RECROSS_0920_4C", (idx[k], tc))                     # touched before those 4 candles = second touch
        if "RECROSS_0920_4C" in ev: break
    return ev


def clean_events(ev):
    if not len(ev): return pd.DataFrame()
    return pd.DataFrame(ev).drop_duplicates(DK).reset_index(drop=True)


def step_events(dh, cand, mst, st):
    ep = f"{OUT}/events.csv"
    ev = pd.read_csv(ep).to_dict("records") if os.path.exists(ep) else []
    tasks, expected = [], []
    for s, g in cand.groupby("stock"):
        if s not in mst: continue
        g = g.copy(); g["d"] = pd.to_datetime(g["date"]).dt.date
        # Maximised span from 60 to 90 days to capture Dhan's exact cap ceiling for EQ Intraday
        for d0, d1 in clusters(g.d.unique().tolist(), 90, 10):
            key = f"EQ|{s}|{d0}|{d1}"; expected.append(key)
            if key not in st["done"]: tasks.append((s, g[(g.d >= d0) & (g.d <= d1)], d0, d1, key))
    st["expected_eq"] = sorted(expected); save_state(st)
    skipped = sorted(set(cand.stock) - set(mst))
    if skipped: print(f"not in Dhan stock-option list - skipped: {skipped}", flush=True)
    print(f"Dhan stock-candle work: {len(tasks)} request groups to do ({len(expected) - len(tasks)} already done)", flush=True)

    def fetch(t): return eq_minute(dh, mst[t[0]][0], t[2], t[3])

    with ThreadPoolExecutor(CONC) as pool:
        for i in range(0, len(tasks), CONC * 2):
            chunk = tasks[i:i + CONC * 2]
            futs = [pool.submit(fetch, t) for t in chunk]
            for (s, g, d0, d1, key), fu in zip(chunk, futs):
                u_all = fu.result(); n_ev = 0
                if u_all is not None:
                    for r in g.itertuples():
                        u = u_all[u_all.index.date == r.d]
                        u = u[[hm(x) <= ENTRY_LAST for x in u.index]]
                        if u.empty: continue
                        ratio = float(u.o.iloc[0]) / float(r.yahoo_open)
                        ref = float(r.ref) * ratio if abs(ratio - 1) > .2 else float(r.ref)       # split/bonus: Yahoo prices adjusted, Dhan raw
                        for typ, (m, ft) in find_events(u, ref, r.direction == "LONG").items():
                            ev.append(dict(stock=s, direction=r.direction, ref=round(ref, 2), date=r.date, signal_date=r.signal_date, shape=int(r.shape),
                                           type=typ, entry_minute=hm(m), first_touch=hm(ft), stock_price=float(u.c[m]))); n_ev += 1
                st["done"].append(key)
                evdf = clean_events(ev); ev = evdf.to_dict("records")
                if len(evdf): evdf.to_csv(ep, index=False)
                save_state(st); checkpoint()
                print(f"stock candles {s} {d0}..{d1}: {len(g)} candidate days, {n_ev} entry events", flush=True)
    return clean_events(ev)


def stop_walk(o, l, entry, sl_pct):
    sl = entry * (1 - sl_pct / 100)
    hit = l <= sl
    if not hit.any(): return None
    i = int(np.argmax(hit))
    return (i, float(o[i]), "STOP (gap)") if o[i] <= sl else (i, float(sl), "STOP")


def build(e, allr, lot, strict):
    D = allr[allr.day == e.d]
    atm = D[D.off == 0].drop_duplicates("ts").sort_values("ts")
    m = pd.Timestamp(f"{e.date} {e.entry_minute}")
    a = atm[atm.ts >= m]
    if a.empty or (a.ts.iloc[0] - m) > pd.Timedelta(minutes=10): return "skip", "no ATM candle at the entry minute"
    te, K, entry = a.ts.iloc[0], float(a.strike.iloc[0]), float(a.c.iloc[0])
    if not entry > 0: return "skip", "zero price"
    ser = D[(D.strike == K) & (D.ts > te)].drop_duplicates("ts").sort_values("ts")
    mins = ser.ts.dt.hour.values * 60 + ser.ts.dt.minute.values
    last = max(int(x[:2]) * 60 + int(x[3:]) for x in EXITS if hm(te) < x) if any(hm(te) < x for x in EXITS) else None
    if last is None: return "skip", "entry at/after the last exit time"
    amins = atm.ts.dt.hour.values * 60 + atm.ts.dt.minute.values
    expected = int(((atm.ts > te).values & (amins <= last)).sum())
    if strict and expected and (mins <= last).sum() < 0.98 * expected: return "retry", None
    rows = []
    for ex in EXITS:
        lim = int(ex[:2]) * 60 + int(ex[3:])
        if hm(te) >= ex: continue
        w = ser[mins <= lim]
        if w.empty: continue
        o, l, cc = w.o.values, w.l.values, w.c.values
        for sl in SLS:
            lots = int(CAPS[sl] // (entry * lot))
            if lots < 1: continue
            qty, cost = lot * lots, entry * lot * lots
            r = stop_walk(o, l, entry, sl)
            if r: i, px, why = r; xt = w.ts.iloc[i]
            else: i, px, why = len(w) - 1, float(cc[-1]), "TIME"; xt = w.ts.iloc[-1]
            late = int(why == "TIME" and (lim - (xt.hour * 60 + xt.minute)) > 5)           # option data thin near the exit time
            rows.append((e.stock, e.direction, e.type, e.date, e.signal_date, int(e.shape), e.first_touch, hm(te), K, round(entry, 2), ex, sl, lots, round(cost),
                         hm(xt), round(px, 2), why, round((px - entry) * qty), round((px / entry - 1) * 100, 1), late, round(float(e.stock_price), 2)))
    return "ok", rows


COLS = ["stock", "direction", "type", "date", "signal_date", "shape", "first_touch", "entry_time", "strike", "entry_price", "exit_rule", "sl", "lots", "cost",
        "exit_time", "exit_price", "reason", "pnl", "ret_pct", "thin_data", "stock_price"]


def prep_series(series):
    allr = pd.concat(series).reset_index().rename(columns={"index": "ts"})
    allr["day"] = allr.ts.dt.date
    return allr


def work_options(dh, mst, t):
    s, dr, g, d0, d1, key = t
    lot, sid = mst[s][1], mst[s][0]
    # Standardised span=30 days mapping perfectly to Dhan's exact rolling option limit bounds
    x0 = rolling(dh, sid, d0, d1 + timedelta(days=1), dr, 0)
    if x0 is None: return [], {"no option data": len(g)}
    x0["off"] = 0
    if "strike" not in x0: return [], {"Dhan sent no strike column": len(g)}
    allr = prep_series([x0])
    rows, miss, retry = [], {}, []
    for e in g.itertuples():
        st_, r = build(e, allr, lot, True)
        if st_ == "ok": rows += r
        elif st_ == "retry": retry.append(e)
        else: miss[r] = miss.get(r, 0) + 1
    if retry and EXTRA:
        series = [x0]
        for a, b in clusters([e.d for e in retry]):
            for off in EXTRA:
                x = rolling(dh, sid, a, b + timedelta(days=1), dr, off)
                if x is not None: x["off"] = off; series.append(x)
        allr = prep_series(series)
        for e in retry:
            st_, r = build(e, allr, lot, False)
            if st_ == "ok": rows += r
            else: miss[r] = miss.get(r, 0) + 1
    elif retry:
        for e in retry:
            st_, r = build(e, allr, lot, False)
            if st_ == "ok": rows += r
    return rows, miss


def step_options(dh, ev, mst, st):
    os.makedirs(f"{OUT}/parts", exist_ok=True)
    tasks, expected = [], []
    for (s, dr), g in ev.groupby(["stock", "direction"]):
        if s not in mst: continue
        g = g.copy(); g["d"] = pd.to_datetime(g["date"]).dt.date
        for d0, d1 in clusters(g.d.unique().tolist()):
            key = f"{s}|{dr}|{d0}|{d1}"; expected.append(key)
            if key not in st["done"]: tasks.append((s, dr, g[(g.d >= d0) & (g.d <= d1)], d0, d1, key))
    st["expected"] = sorted(expected); save_state(st)
    print(f"Dhan option work: {len(tasks)} request groups to do ({len(expected) - len(tasks)} already done)", flush=True)
    with ThreadPoolExecutor(CONC) as pool:
        for i in range(0, len(tasks), CONC * 2):
            chunk = tasks[i:i + CONC * 2]
            futs = [pool.submit(work_options, dh, mst, t) for t in chunk]
            for (s, dr, g, d0, d1, key), fu in zip(chunk, futs):
                rows, miss = fu.result()
                if rows: pd.DataFrame(rows, columns=COLS).to_csv(f"{OUT}/parts/{s}_{dr}_{d0}_{d1}.csv.gz", index=False, compression="gzip")
                st["done"].append(key); save_state(st); checkpoint()
                print(f"options {s} {dr} {d0}..{d1}: {len(g)} entry events, {len(rows)} result rows" + (f", skipped {miss}" if miss else "") + f", calls so far {dh.n}", flush=True)


def with_variants(t):
    a = t.copy(); a["rule"] = "NO_SHAPE_RULE"
    b = t[t["shape"] == 1].copy(); b["rule"] = "WITH_SHAPE_RULE"
    return pd.concat([a, b], ignore_index=True)


def load_parts(fs):
    return pd.concat([pd.read_csv(f) for f in fs], ignore_index=True).drop_duplicates(EK)


def combine_all(fs):
    out = f"{OUT}/all_trades_combined"; os.makedirs(out, exist_ok=True)
    for f in glob.glob(f"{out}/all_trades*"): os.remove(f)
    seen, lim, header, n_rows, n_part, size, fh = set(), 45 * 1024 * 1024, None, 0, 0, 0, None
    gz = gzip.open(f"{out}/all_trades.csv.gz", "wt", newline="", compresslevel=6)
    try:
        for f in fs:
            df = pd.read_csv(f)
            k = list(zip(*(df[c] for c in EK)))
            keep = [x not in seen for x in k]; seen.update(k)
            df = df[keep]
            if df.empty: continue
            if header is None: header = list(df.columns); gz.write(",".join(header) + "
")
            text = df.reindex(columns=header).to_csv(index=False, header=False)
            gz.write(text)
            if fh is None or size + len(text) > lim:
                if fh: fh.close()
                n_part += 1; fh = open(f"{out}/all_trades_{n_part:02d}.csv", "w", newline=""); fh.write(",".join(header) + "
"); size = 0
            fh.write(text); size += len(text); n_rows += len(df)
    finally:
        gz.close()
        if fh: fh.close()
    if n_part == 1: os.rename(f"{out}/all_trades_01.csv", f"{out}/all_trades.csv")
    print(f"ALL TRADES: {n_rows:,} rows -> {out}/ ({n_part} CSV file(s) + all_trades.csv.gz)", flush=True)


def agg(g):
    w = g.pnl > 0
    gain, loss = g.pnl[w].sum(), -g.pnl[~w].sum()
    return pd.Series(dict(trades=len(g), wins=int(w.sum()), win_pct=round(w.mean() * 100, 1), stops=int(g.reason.str.startswith("STOP").sum()),
                          gap_stops=int((g.reason == "STOP (gap)").sum()), time_exits=int((g.reason == "TIME").sum()),
                          total_pnl=int(g.pnl.sum()), capital=int(g.cost.sum()), roi_pct=round(g.pnl.sum() / g.cost.sum() * 100, 2),
                          avg_pnl=int(g.pnl.mean()), avg_ret_pct=round(g.ret_pct.mean(), 2),
                          profit_factor=round(gain / loss, 2) if loss > 0 else None, thin_data=int(g.thin_data.sum())))


def tables(t, out, mt):
    os.makedirs(out, exist_ok=True)
    t = with_variants(t); t["year"] = t.date.str[:4]
    key = ["rule", "type", "exit_rule", "sl"]
    a = t.groupby(key).apply(agg).reset_index()
    a["variant"] = a.rule + " | " + a.type + " | exit " + a.exit_rule + " | SL" + a.sl.astype(str)
    a.sort_values("roi_pct", ascending=False).to_csv(f"{out}/variants_combined.csv", index=False)
    n, w = a[a.rule == "NO_SHAPE_RULE"].set_index(key[1:]), a[a.rule == "WITH_SHAPE_RULE"].set_index(key[1:])
    cols = ["trades", "win_pct", "stops", "total_pnl", "roi_pct", "avg_ret_pct", "profit_factor"]
    cmp_ = n[cols].add_prefix("noshape_").join(w[cols].add_prefix("shape_"), how="outer")
    cmp_["roi_diff_shape_minus_noshape"] = (cmp_.shape_roi_pct - cmp_.noshape_roi_pct).round(2)
    cmp_.reset_index().to_csv(f"{out}/compare_shape_vs_noshape.csv", index=False)
    t.groupby(key + ["year"]).apply(agg).reset_index().to_csv(f"{out}/by_year.csv", index=False)
    t.assign(month=t.date.str[:7]).groupby(key + ["month"]).apply(agg).reset_index().to_csv(f"{out}/by_month.csv", index=False)
    t.groupby(key + ["direction"]).apply(agg).reset_index().to_csv(f"{out}/by_direction.csv", index=False)
    t.groupby(key + ["stock"]).apply(agg).reset_index().to_csv(f"{out}/by_stock.csv", index=False)
    ok = a[a.trades >= mt]
    print(f"\n{len(t):,} trade rows (both rules)\nSHAPE RULE vs NO SHAPE RULE (same variant, ROI %):\n" +
          cmp_.reset_index()[["type", "exit_rule", "sl", "noshape_trades", "noshape_roi_pct", "shape_trades", "shape_roi_pct", "roi_diff_shape_minus_noshape"]].to_string(index=False), flush=True)
    print("\nBEST 15 VARIANTS BY ROI (min %d trades):\n" % mt + ok.sort_values("roi_pct", ascending=False).head(15)[["variant", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor"]].to_string(index=False), flush=True)


def progress():
    st = load_state(); exp = set(st.get("expected", [])) | set(st.get("expected_eq", []))
    if not exp: return
    done = len(exp & set(st["done"]))
    msg = (f"COMPLETE - all {len(exp)} request groups finished." if done >= len(exp) else
           f"PARTIAL - {done} of {len(exp)} request groups finished ({done / len(exp) * 100:.0f}%). Results cover only the finished part. Run again to continue.")
    open(f"{OUT}/PROGRESS.txt", "w").write(msg + "
"); print("\n*** " + msg + " ***", flush=True)


def summary():
    progress()
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    if not fs: print("No results yet"); return
    combine_all(fs)
    tables(load_parts(fs), OUT, int(os.environ.get("MIN_TRADES") or 30))


def range_summary(start, end):
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    if not fs: sys.exit(f"No saved results in {OUT}/parts - run the backtest first")
    t = load_parts(fs); t = t[(t.date >= start) & (t.date <= end)]
    if t.empty: sys.exit(f"No trades with entry date between {start} and {end}")
    out = f"shapecmp_range_out/{start}_to_{end}"; os.makedirs(out, exist_ok=True)
    t.sort_values(["date", "stock", "type", "exit_rule", "sl"]).to_csv(f"{out}/trades_in_range.csv", index=False)
    tables(t, out, int(os.environ.get("MIN_TRADES") or 5)); print(f"\nSaved in {out}/")


def check():
    dh = Dhan(); mst = load_master()
    print(f"Instrument list OK: {len(mst)} stocks with options. RELIANCE ->", mst.get("RELIANCE"), flush=True)
    miss = [s for s in UNIVERSE if s not in mst]
    print(f"{len(UNIVERSE) - len(miss)} of {len(UNIVERSE)} universe stocks found in Dhan list. Missing: {miss[:30]}", flush=True)
    sid = mst["RELIANCE"][0]
    d1 = date.today(); d0 = d1 - timedelta(days=10)
    u = eq_minute(dh, sid, d0, d1)
    print("Stock minute call:", "no data" if u is None else f"{len(u)} candles, {u.index[0]} .. {u.index[-1]}")
    x = rolling(dh, sid, d0, d1, "LONG", 0)
    print("Rolling option call:", "no data" if x is None else f"{len(x)} candles, columns {list(x.columns)}")
    if x is not None: print(x.tail(3))
    print_stats(dh)


def print_stats(dh):
    print(f"Dhan calls: {dh.n}", flush=True)
    for path, (n, sec) in dh.stats.items(): print(f"  {path}: {n} calls, average {sec / n:.2f} s per call", flush=True)


def run():
    os.makedirs(OUT, exist_ok=True)
    st = load_state()
    cp = f"{OUT}/candidates_{START}_{END}.csv"
    if os.path.exists(cp): cand = pd.read_csv(cp)
    else:
        cand = yahoo_candidates()
        if cand.empty: print("No candidate days found for this period - nothing to test."); return
        cand.to_csv(cp, index=False)
    print(f"Candidate days {START} to {END}: {len(cand)}", flush=True)
    dh = Dhan(); mst = load_master()
    try:
        ev = step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= START) & (ev["date"] <= END)] if len(ev) else ev
        print(f"Entry events: {len(ev)}", flush=True)
        if len(ev): step_options(dh, ev, mst, st)
        print("ALL STEPS FINISHED", flush=True)
    except Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        print_stats(dh)
        summary()
        checkpoint(True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": check()
        elif mode == "run": run()
        elif mode == "summary": summary()
        elif mode == "range": range_summary(START, END)
        else: sys.exit("use: python shapecmp_backtest.py check | run | summary | range")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
