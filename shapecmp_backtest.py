"""shapecmp_backtest.py - d3z strategy, WITH vs WITHOUT the previous-candle shape rule, in one run. Yahoo daily + Dhan 1-minute candles.
Self-contained, unique names. Default period: the last 4 years; choose any dates (inputs start / end).

  python shapecmp_backtest.py check     test Dhan access (run first)
  python shapecmp_backtest.py run       full backtest, resumable (stops politely before the time budget - just run again)
  python shapecmp_backtest.py summary   rebuild every table + the combined all-trades CSV from saved results (no API calls)
  python shapecmp_backtest.py range     tables + trade list for the entry dates in SHAPECMP_START / SHAPECMP_END only (own folder)

THE STRATEGY (as in the first d3z backtest)
  Reference line   : 10-day high (LONG) / 10-day low (SHORT). The stock broke it; then the PREVIOUS DAY CLOSED BACK beyond it
                     (LONG: close below the line, SHORT: close above it)  <- required in BOTH rules.
  Two rules        : NO_SHAPE_RULE   = every such previous day.
                     WITH_SHAPE_RULE = only if that previous candle also has a small body (< 45 % of its range) and a wick >= 2 x body.
                     (every trade carries shape = 1 / 0; all tables are produced for both rules and a side-by-side comparison file)
  Entry day        : the next trading day; option bought at the entry minute (ATM CE for LONG / PE for SHORT, nearest monthly expiry,
                     price = close of that option candle, as in d3z). Entry types (stock 1-minute candles):
                       OPEN_0915        line touched in the very first minute (09:15)
                       ALL              first minute the line is touched
                       FROM_0920_4C     from 09:20: the 4 previous candles fully on the wrong side of the line and this minute closes beyond it
                       RECROSS_0920_4C  same, but the line had ALREADY been touched before those 4 candles (second touch)
                     Only entries before 10:00 matter (the exits are 09:30 and 10:00).
  Exits            : time-based 09:30 or 10:00 (price = close of the last option candle up to that time) AND stop-loss 10 %, 20 % or 30 %
                     (first 1-minute low that touches it; a gap through it fills at the open). No target. An exit variant is skipped when the
                     entry is at/after its time.
  Capital          : equal risk - SL10 Rs 2,00,000 | SL20 Rs 1,00,000 | SL30 Rs 66,667 per trade; lots = cap // (price x lot size).
  Fewer Dhan calls : Yahoo gives the dates (maximum history); stock candles only for candidate days; option candles first for the ATM strike only,
                     the neighbouring strikes (+1, -1) are fetched only for trades whose ATM strike moved before the exit. Paced and parallel.
  Output           : shapecmp_results/  (parts, variants_combined.csv, compare_shape_vs_noshape.csv, by year / month / direction / stock,
                     all_trades_combined/ = every trade in plain CSV files + one .gz, PROGRESS.txt)
Charges, taxes and slippage are not included. Lot sizes are today's values for all years.

SPEED NOTES (Dhan Data API limit = 5 calls/second, 100,000/day - so the number of calls is what matters)
  * One global rate limiter at 1 call per 0.21 s (4.8/s); 16 calls in flight so latency never idles the limiter; a 429 pauses ALL threads together.
  * Persistent keep-alive HTTP sessions (no new TLS handshake per call). Rolling-option request asks only for the fields that are used.
  * Bigger windows = fewer calls: stock candles up to 85 days per call (limit 90), option candles up to 30 days per call, gaps merged (EQ_SPAN/EQ_GAP/OPT_GAP).
  * Continuous work queue (no waiting for a whole chunk); state/events saved every few seconds instead of after every call.
  * Vectorised summaries and one-pass combined CSV; Yahoo download limited to the chosen period (+ look-back).
"""
import os, sys, io, json, time, gzip, glob, subprocess, threading
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import requests, numpy as np, pandas as pd
from requests.adapters import HTTPAdapter
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
START = os.environ.get("SHAPECMP_START") or str(date.today() - timedelta(days=4 * 365))
END = os.environ.get("SHAPECMP_END") or str(date.today())
SLS = [10, 20, 30]
EXITS = ["09:30", "10:00"]
CAPS = {10: 200000, 20: 100000, 30: 66667}
ENTRY_LAST = "09:59"                                          # entries must come before the last exit time (10:00)
ENTRY_MIN = int(ENTRY_LAST[:2]) * 60 + int(ENTRY_LAST[3:])
PRE_TOL = float(os.environ.get("PRE_TOL") or 0.04)            # daily-open prefilter: open within 4 % of the line (entry must come in the first 45 minutes)
EXTRA = [int(x) for x in (os.environ.get("OFFSETS2") or "1,-1").split(",") if x.strip()]    # neighbouring strikes, fetched only when needed
GAP_S = float(os.environ.get("DHAN_GAP") or 0.21)             # seconds between the START of two Dhan calls, all threads together (limit is 5/second)
CONC = int(os.environ.get("DHAN_CONC") or 16)                 # Dhan calls in flight at the same time
BUDGET_MIN = float(os.environ.get("BUDGET_MIN") or 300)       # stop politely after this many minutes
DAY_CAP = int(os.environ.get("DAY_CAP") or 95000)             # Dhan Data API allows 100,000 calls per day
EQ_SPAN = int(os.environ.get("EQ_SPAN") or 85)                # stock 1-minute candles: days per call (Dhan max 90)
EQ_GAP = int(os.environ.get("EQ_GAP") or 30)                  # merge candidate days closer than this into one stock call
OPT_GAP = int(os.environ.get("OPT_GAP") or 15)                # merge option dates closer than this into one call (span max 30 days)
OUT = os.environ.get("SHAPECMP_OUT", "shapecmp_results")
BASE = "https://api.dhan.co/v2"
MASTER = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
T0 = time.time()
LAST_CP = time.time()
FLUSHER = [None]
EK = ["stock", "direction", "type", "date", "exit_rule", "sl"]    # one trade row
DK = ["stock", "direction", "type", "date"]                       # one entry event

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
        self.n, self.rl, self.errs = 0, 0, 0
        self.gap, self.next_t, self.pause_until = GAP_S, 0.0, 0.0
        self.lock = threading.Lock()
        self.loc = threading.local()                              # one keep-alive session per thread
        self.stats = {}                                           # path -> [calls, seconds]: shows where the time goes

    def _session(self):
        s = getattr(self.loc, "s", None)
        if s is None:
            s = requests.Session(); s.headers.update(self.h)
            s.mount("https://", HTTPAdapter(pool_connections=2, pool_maxsize=2, max_retries=0))
            self.loc.s = s
        return s

    def _slot(self):
        """Reserve the next call slot (one call may START every self.gap seconds, whichever thread); sleep OUTSIDE the lock."""
        with self.lock:
            now = time.monotonic()
            t = max(now, self.next_t)
            self.next_t = t + self.gap; self.n += 1
        if t > now: time.sleep(t - now)

    def post(self, path, body):
        if (time.time() - T0) / 60 > BUDGET_MIN: raise Stop(f"time budget of {BUDGET_MIN:.0f} min used")
        if self.n >= DAY_CAP: raise Stop(f"{DAY_CAP} calls used - Dhan's daily Data API limit is 100,000; run again tomorrow")
        for attempt in range(8):
            self._slot()
            try:
                t_req = time.time()
                r = self._session().post(BASE + path, json=body, timeout=(10, 90))
                with self.lock:
                    st_ = self.stats.setdefault(path, [0, 0.0]); st_[0] += 1; st_[1] += time.time() - t_req
            except Exception as e:
                print(f"[call {self.n}] network problem: {e}", flush=True); time.sleep(min(2 ** attempt, 20)); continue
            try: j = r.json()
            except Exception: j = None
            code = str(j.get("errorCode", "")) if isinstance(j, dict) else ""
            if r.status_code == 200 and j is not None and not code:
                with self.lock:
                    if time.monotonic() >= self.pause_until: self.rl = 0
                return j
            if r.status_code == 429 or code in self.RATE_CODES:
                with self.lock:                                   # the first thread to see it pauses everybody; the others just wait
                    now = time.monotonic(); first = now >= self.pause_until
                    if first:
                        self.rl += 1; s = min(10 * 2 ** (self.rl - 1), 300)
                        self.pause_until = now + s; self.next_t = max(self.next_t, self.pause_until)
                        self.gap = min(self.gap * 1.15, 0.5)      # and slow down a little for the rest of the run
                if first:
                    if self.rl > 6: raise Stop("Dhan keeps refusing (rate limit) - wait a while and run again")
                    print(f"[call {self.n}] rate limit ({code or r.status_code}) - all threads pause {s}s, gap now {self.gap:.2f}s", flush=True)
                continue
            if r.status_code in (401, 403) or code in self.AUTH_CODES:
                raise Fatal(f"Dhan refused the login/token: http {r.status_code} {code} {str(j)[:200]}")
            self.errs += 1
            if self.errs <= 8: print(f"[call {self.n}] Dhan says: http {r.status_code} {str(j or r.text)[:200]}", flush=True)
            return None
        raise Stop("Dhan not reachable")


def stream(tasks, fn, handle, window=None):
    """Run fn(task) in CONC threads with a continuously refilled queue (no chunk barriers); handle(task, result) runs in the main thread."""
    it, pending, err = iter(tasks), {}, None
    window = window or CONC * 3
    with ThreadPoolExecutor(CONC) as pool:
        def fill():
            while err is None and len(pending) < window:
                t = next(it, None)
                if t is None: return
                pending[pool.submit(fn, t)] = t
        fill()
        while pending:
            done, _ = wait(pending, return_when=FIRST_COMPLETED)
            for f in done:
                t = pending.pop(f)
                try: res = f.result()
                except Exception as e: err = err or e; continue
                handle(t, res)
            fill()
    if err: raise err


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
        "requiredData": ["open", "high", "low", "close", "strike"], "fromDate": str(d0), "toDate": str(d1)})
    if j is None: return None
    d = (j.get("data") or {}).get("ce" if side == "LONG" else "pe")
    return frame(d, extra=("strike",))


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


# ------------------------------------------------------------------ step 1: Yahoo daily -> valid entry dates



def shape(o, h, l, c):
    """Previous-candle shape rule: body < 45 % of the range and a wick >= 2 x body."""
    if h == l: return 0
    b = abs(c - o)
    return int(b / (h - l) < .45 and max(h - max(o, c), min(o, c) - l) >= 2 * b)


# ------------------------------------------------------------------ step 1: Yahoo daily (maximum history) -> candidate entry days
def yahoo_candidates():
    import yfinance as yf
    t0, t1 = pd.Timestamp(START), pd.Timestamp(END)
    raw = yf.download([s + ".NS" for s in UNIVERSE], start=str((t0 - pd.Timedelta(days=150)).date()), end=str((t1 + pd.Timedelta(days=3)).date()),
                      group_by="ticker", auto_adjust=False, progress=False, threads=True)       # 150 days look-back is plenty for the 10-day line + 20-day window
    rows, nst = [], 0
    for s in UNIVERSE:
        try: d = raw[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
        if len(d) < 60: continue
        nst += 1
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        c, O, H, L = d.Close.values, d.Open.values, d.High.values, d.Low.values
        lines = {True: prep_lines(d, True), False: prep_lines(d, False)}
        i0, i1 = d.index.searchsorted(t0, "left"), d.index.searchsorted(t1, "right")            # entry days j in [i0, i1) -> signal day k = j-1
        dates = d.index.strftime("%Y-%m-%d")
        for k in range(max(40, i0 - 1), min(len(d) - 1, i1 - 1)):                # k = previous day (signal), k+1 = entry day
            for long in (True, False):
                ref = pick_line(lines[long][0], lines[long][1], c, k, long)          # previous day closed back beyond the line
                if ref is None: continue
                if long and not (H[k + 1] >= ref and O[k + 1] >= ref * (1 - PRE_TOL)): continue
                if not long and not (L[k + 1] <= ref and O[k + 1] <= ref * (1 + PRE_TOL)): continue
                rows.append(dict(stock=s, direction="LONG" if long else "SHORT", ref=round(ref, 2), signal_date=dates[k],
                                 date=dates[k + 1], shape=shape(O[k], H[k], L[k], c[k]), yahoo_open=float(O[k + 1]), yahoo_close=float(c[k + 1])))
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
    if FLUSHER[0]: FLUSHER[0]()                                   # make sure events/state on disk are current before committing
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
    s["done"] = set(s["done"])                                    # O(1) lookups
    return s


def save_state(s):
    tmp = f"{OUT}/state.json.tmp"
    json.dump({**s, "done": sorted(s["done"])}, open(tmp, "w")); os.replace(tmp, f"{OUT}/state.json")


LAST_SAVE = [0.0]


def flush(st, ev=None, ep=None, force=False, every=10):
    """Write events + state at most every `every` seconds (events first, so 'done' never gets ahead of its events)."""
    if not force and time.time() - LAST_SAVE[0] < every: return
    if ev:
        evdf = clean_events(ev)
        if len(evdf): evdf.to_csv(ep, index=False)
    save_state(st); LAST_SAVE[0] = time.time()


# ------------------------------------------------------------------ step 2: stock 1-minute candles -> entry events
def find_events(u, ref, long):
    """u = entry-day 1-minute candles (09:15-09:59). -> {entry type: (entry minute, first touch minute)}"""
    touch = ((u.h >= ref) if long else (u.l <= ref)).values
    ev = {}
    if not touch.any(): return ev
    idx, h, l, c = u.index, u.h.values, u.l.values, u.c.values
    mn = idx.hour.values * 60 + idx.minute.values
    i0 = int(np.argmax(touch)); tc = idx[i0]
    if mn[i0] <= ENTRY_MIN: ev["ALL"] = (tc, tc)
    if mn[i0] == 555: ev["OPEN_0915"] = (tc, tc)                                              # 09:15
    for k in range(4, len(u)):
        if mn[k] < 560: continue                                                              # before 09:20
        if mn[k] > ENTRY_MIN: break
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
        for d0, d1 in clusters(g.d.unique().tolist(), EQ_SPAN, EQ_GAP):
            key = f"EQ|{s}|{d0}|{d1}"; expected.append(key)
            if key not in st["done"]: tasks.append((s, g[(g.d >= d0) & (g.d <= d1)], d0, d1, key))
    st["expected_eq"] = sorted(expected); save_state(st)
    skipped = sorted(set(cand.stock) - set(mst))
    if skipped: print(f"not in Dhan stock-option list - skipped: {skipped}", flush=True)
    print(f"Dhan stock-candle work: {len(tasks)} request groups to do ({len(expected) - len(tasks)} already done)", flush=True)

    def work(t):                                                  # runs in a worker thread: fetch + find the entry events
        s, g, d0, d1, key = t
        u_all = eq_minute(dh, mst[s][0], d0, d1)
        if u_all is None: return None
        u_all = u_all[(u_all.index.hour.values * 60 + u_all.index.minute.values) <= ENTRY_MIN]
        days = {k: v for k, v in u_all.groupby(u_all.index.date)}
        out = []
        for r in g.itertuples():
            u = days.get(r.d)
            if u is None or u.empty: continue
            ratio = float(u.o.iloc[0]) / float(r.yahoo_open)
            ref = float(r.ref) * ratio if abs(ratio - 1) > .2 else float(r.ref)       # split/bonus: Yahoo prices adjusted, Dhan raw
            for typ, (m, ft) in find_events(u, ref, r.direction == "LONG").items():
                out.append(dict(stock=s, direction=r.direction, ref=round(ref, 2), date=r.date, signal_date=r.signal_date, shape=int(r.shape),
                                type=typ, entry_minute=hm(m), first_touch=hm(ft), stock_price=float(u.c[m])))
        return out

    def handle(t, out):
        s, g, d0, d1, key = t
        if out: ev.extend(out)
        st["done"].add(key); flush(st, ev, ep); checkpoint()
        print(f"stock candles {s} {d0}..{d1}: {len(g)} candidate days, {len(out or [])} entry events, calls so far {dh.n}", flush=True)

    FLUSHER[0] = lambda: flush(st, ev, ep, force=True)
    try: stream(tasks, work, handle)
    finally: flush(st, ev, ep, force=True)
    return clean_events(ev)


# ------------------------------------------------------------------ step 3: ATM option candles -> trades
def stop_walk(o, l, entry, sl_pct):
    sl = entry * (1 - sl_pct / 100)
    hit = l <= sl
    if not hit.any(): return None
    i = int(np.argmax(hit))
    return (i, float(o[i]), "STOP (gap)") if o[i] <= sl else (i, float(sl), "STOP")


def build(e, allr, lot, strict):
    """One entry event -> (status, rows). status 'retry' = the ATM strike moved before the exit and the neighbouring strikes are still needed."""
    D = allr.get(e.d)
    if D is None: return "skip", "no ATM candle at the entry minute"
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
    return {d: g for d, g in allr.groupby(allr.ts.dt.date)}        # day -> that day's candles (all strikes)


def work_options(dh, mst, t):
    """One request group: ATM candles first; neighbouring strikes only for the trades that need them."""
    s, dr, g, d0, d1, key = t
    lot, sid = mst[s][1], mst[s][0]
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
        for a, b in clusters([e.d for e in retry], 30, OPT_GAP):
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
        for d0, d1 in clusters(g.d.unique().tolist(), 30, OPT_GAP):
            key = f"{s}|{dr}|{d0}|{d1}"; expected.append(key)
            if key not in st["done"]: tasks.append((s, dr, g[(g.d >= d0) & (g.d <= d1)], d0, d1, key))
    st["expected"] = sorted(expected); save_state(st)
    print(f"Dhan option work: {len(tasks)} request groups to do ({len(expected) - len(tasks)} already done)", flush=True)

    def work(t):                                                  # worker thread: fetch, build trades, write this group's part file
        rows, miss = work_options(dh, mst, t)
        if rows:
            s, dr, g, d0, d1, key = t
            pd.DataFrame(rows, columns=COLS).to_csv(f"{OUT}/parts/{s}_{dr}_{d0}_{d1}.csv.gz", index=False, compression={"method": "gzip", "compresslevel": 1})
        return len(rows), miss

    def handle(t, res):
        s, dr, g, d0, d1, key = t; n_rows, miss = res
        st["done"].add(key); flush(st); checkpoint()
        print(f"options {s} {dr} {d0}..{d1}: {len(g)} entry events, {n_rows} result rows" + (f", skipped {miss}" if miss else "") + f", calls so far {dh.n}", flush=True)

    FLUSHER[0] = lambda: flush(st, force=True)
    try: stream(tasks, work, handle)
    finally: flush(st, force=True)


# ------------------------------------------------------------------ step 4: summaries + combined CSV
def with_variants(t):
    """NO_SHAPE_RULE = every trade; WITH_SHAPE_RULE = only trades whose previous candle also passes the shape rule."""
    a = t.copy(); a["rule"] = "NO_SHAPE_RULE"
    b = t[t["shape"] == 1].copy(); b["rule"] = "WITH_SHAPE_RULE"
    return pd.concat([a, b], ignore_index=True)


def load_parts(fs):
    with ThreadPoolExecutor(8) as pool: dfs = list(pool.map(pd.read_csv, fs))
    return pd.concat(dfs, ignore_index=True).drop_duplicates(EK)


def combine_all(t):
    """Every trade (already de-duplicated) in plain CSV files (each < 45 MB) + one .gz, in <OUT>/all_trades_combined/ - to filter yourself."""
    out = f"{OUT}/all_trades_combined"; os.makedirs(out, exist_ok=True)
    for f in glob.glob(f"{out}/all_trades*"): os.remove(f)
    lim, header, n_part, size, fh, step = 45 * 1024 * 1024, ",".join(t.columns) + "\n", 0, 0, None, 100000
    gz = gzip.open(f"{out}/all_trades.csv.gz", "wt", newline="", compresslevel=3); gz.write(header)
    try:
        for i in range(0, len(t), step):
            text = t.iloc[i:i + step].to_csv(index=False, header=False)
            gz.write(text)
            if fh is None or size + len(text) > lim:
                if fh: fh.close()
                n_part += 1; fh = open(f"{out}/all_trades_{n_part:02d}.csv", "w", newline=""); fh.write(header); size = 0
            fh.write(text); size += len(text)
    finally:
        gz.close()
        if fh: fh.close()
    if n_part == 1: os.rename(f"{out}/all_trades_01.csv", f"{out}/all_trades.csv")
    print(f"ALL TRADES: {len(t):,} rows -> {out}/ ({n_part} CSV file(s) + all_trades.csv.gz)", flush=True)


AGG_COLS = ["trades", "wins", "win_pct", "stops", "gap_stops", "time_exits", "total_pnl", "capital", "roi_pct", "avg_pnl", "avg_ret_pct", "profit_factor", "thin_data"]


def agg_by(t, keys):
    """Vectorised version of the per-group statistics (same columns and rounding as before)."""
    p = t.pnl
    x = t.assign(_w=p > 0, _gain=p.clip(lower=0), _loss=(-p).clip(lower=0), _st=t.reason.str.startswith("STOP"),
                 _gap=t.reason == "STOP (gap)", _tm=t.reason == "TIME")
    g = x.groupby(keys).agg(trades=("pnl", "size"), wins=("_w", "sum"), stops=("_st", "sum"), gap_stops=("_gap", "sum"), time_exits=("_tm", "sum"),
                            total_pnl=("pnl", "sum"), capital=("cost", "sum"), avg_pnl=("pnl", "mean"), avg_ret_pct=("ret_pct", "mean"),
                            gain=("_gain", "sum"), loss=("_loss", "sum"), thin_data=("thin_data", "sum"))
    g["win_pct"] = (g.wins / g.trades * 100).round(1)
    g["roi_pct"] = (g.total_pnl / g.capital * 100).round(2)
    g["profit_factor"] = (g.gain / g.loss.where(g.loss > 0)).round(2)
    g["avg_ret_pct"] = g.avg_ret_pct.round(2)
    for c in ("wins", "stops", "gap_stops", "time_exits", "total_pnl", "capital", "avg_pnl", "thin_data"): g[c] = g[c].astype(np.int64)
    return g[AGG_COLS]


def tables(t, out, mt):
    """All summary tables for the trades in t, written into folder out."""
    os.makedirs(out, exist_ok=True)
    t = with_variants(t); t["year"] = t.date.str[:4]; t["month"] = t.date.str[:7]
    key = ["rule", "type", "exit_rule", "sl"]
    a = agg_by(t, key).reset_index()
    a["variant"] = a.rule + " | " + a.type + " | exit " + a.exit_rule + " | SL" + a.sl.astype(str)
    a.sort_values("roi_pct", ascending=False).to_csv(f"{out}/variants_combined.csv", index=False)
    # side-by-side: the same variant with and without the shape rule
    n, w = a[a.rule == "NO_SHAPE_RULE"].set_index(key[1:]), a[a.rule == "WITH_SHAPE_RULE"].set_index(key[1:])
    cols = ["trades", "win_pct", "stops", "total_pnl", "roi_pct", "avg_ret_pct", "profit_factor"]
    cmp_ = n[cols].add_prefix("noshape_").join(w[cols].add_prefix("shape_"), how="outer")
    cmp_["roi_diff_shape_minus_noshape"] = (cmp_.shape_roi_pct - cmp_.noshape_roi_pct).round(2)
    cmp_.reset_index().to_csv(f"{out}/compare_shape_vs_noshape.csv", index=False)
    for name, extra in (("by_year", "year"), ("by_month", "month"), ("by_direction", "direction"), ("by_stock", "stock")):
        agg_by(t, key + [extra]).reset_index().to_csv(f"{out}/{name}.csv", index=False)
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
    open(f"{OUT}/PROGRESS.txt", "w").write(msg + "\n"); print("\n*** " + msg + " ***", flush=True)


def summary():
    progress()
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    if not fs: print("No results yet"); return
    t = load_parts(fs); combine_all(t)
    tables(t, OUT, int(os.environ.get("MIN_TRADES") or 30))


def range_summary(start, end):
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    if not fs: sys.exit(f"No saved results in {OUT}/parts - run the backtest first")
    t = load_parts(fs); t = t[(t.date >= start) & (t.date <= end)]
    if t.empty: sys.exit(f"No trades with entry date between {start} and {end}")
    out = f"shapecmp_range_out/{start}_to_{end}"; os.makedirs(out, exist_ok=True)
    t.sort_values(["date", "stock", "type", "exit_rule", "sl"]).to_csv(f"{out}/trades_in_range.csv", index=False)
    tables(t, out, int(os.environ.get("MIN_TRADES") or 5)); print(f"\nSaved in {out}/")


# ------------------------------------------------------------------ modes
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
