"""bpb_fno_backtest.py - ALL F&O STOCKS version of bpb_backtest.py (same strategy, same exits, only the stock list differs). BREAKOUT + PULLBACK + RE-CROSS strategy on stock options. Yahoo daily + Dhan 1-minute candles.
Self-contained. Default: every F&O-eligible stock in the list below (210 stocks), last 3 years, ATM option (CE for LONG / PE for SHORT), entry 09:15-09:59,
every combination of  stop-loss 10/20/30 %  x  target 10/20/40/60/80/120/160/200 % (+ "no target" baseline, tp = 0)  x  time exit 09:30/09:40/10:00.

  python bpb_fno_backtest.py check     test Dhan access + compare the stock list with Dhan's live stock-option list (run first)
  python bpb_fno_backtest.py run       full backtest, resumable (stops politely before the time budget - just run again)
  python bpb_fno_backtest.py summary   rebuild every table + all-trades CSV from saved results (no API calls)
  python bpb_fno_backtest.py range     tables + trade list for the entry dates in BPB_START / BPB_END only

THE STRATEGY (daily candles decide the setup, 1-minute candles decide the entry)
  LONG
    1. BREAKOUT   : a daily candle closes above the 10-day rolling high (highest High of the previous 10 days).  That 10-day high = the LINE.
    2. ENTRY LEVEL: the highest High made since the breakout day (the breakout day included).  It rises if later candles make new highs.
    3. PULLBACK   : every candle after the breakout day must CLOSE at or above the LINE.  The first candle that closes below the LINE
                    makes the setup invalid for good.
    4. CONFIRMED  : the pullback counts only after at least one BEARISH daily candle (close < open) after the breakout day.
    5. ENTRY      : on a later day, the first 1-minute candle between 09:15 and 09:20 whose High reaches the ENTRY LEVEL -> buy the ATM call.
                    (If the price is already above the level at the open, the 09:15 candle is the entry.)
    6. ONE SETUP = ONE ENTRY DAY: the first day on which price crosses the entry level (after the pullback is confirmed) uses the setup up,
                    whether or not the cross happens inside 09:15-09:20.  A new breakout can start a new setup.
  SHORT  : exact mirror - close below the 10-day rolling LOW; entry level = lowest Low since the breakdown; pullback candles must not CLOSE
           above the line; confirmed by a BULLISH candle; entry when a 1-minute Low reaches the level; buy the ATM put.
  Detail : the LINE is fixed at the FIRST breakout candle's 10-day high; later higher candles only raise the entry level.
           (Optional: BPB_RESET_LINE=1 moves the line up to the newest 10-day high when another breakout candle comes before any pullback.)

  Entry window : the first 1-minute candle from 09:15 to 09:59 whose High (SHORT: Low) reaches the entry level.
  Option price : close of the option candle of the entry minute (nearest monthly expiry, ATM strike at that moment, strike locked afterwards).
  Exit         : whichever comes first - stop-loss (% of premium, first 1-minute low that touches it), target (first 1-minute high that touches it),
                 or the time exit (close of the last option candle up to 09:30 / 09:40 / 10:00). A gap through the stop or target fills at the open.
                 If stop and target are inside the same 1-minute candle the STOP is taken. A time exit is skipped when the entry is at/after it.
  Capital      : equal risk - SL10 Rs 2,00,000 | SL20 Rs 1,00,000 | SL30 Rs 66,667 per trade; lots = capital // (price x lot size).
Charges, taxes and slippage are not included. Lot sizes are today's values for all years.

Dhan Data API limit = 5 calls/second, 100,000/day: one global rate limiter, parallel threads, merged date windows, resumable state.
Output folder: bpb_fno_results/  (parts, trades_all.csv, summary.csv = every variant, roi_matrix.csv, by_year/month/direction/stock, skipped.csv, REPORT.txt, PROGRESS.txt)
"""
import os, sys, io, json, time, glob, subprocess, threading
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import requests, numpy as np, pandas as pd
from requests.adapters import HTTPAdapter
from datetime import date, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
START = os.environ.get("BPB_START") or str(date.today() - timedelta(days=3 * 365))
END = os.environ.get("BPB_END") or str(date.today())
FNO = """
    360ONE ABCAPITAL ADANIENSOL ABB ADANIPORTS AMBER ASIANPAINT AMBUJACEM
    ADANIENT BAJAJ-AUTO BAJAJHLDNG APLAPOLLO ADANIGREEN AUROPHARMA AXISBANK BOSCHLTD
    BRITANNIA CDSL BANDHANBNK BANKBARODA BDL BHARATFORG COALINDIA BHARTIARTL
    BLUESTARCO BPCL ALKEM CAMS CHOLAFIN CIPLA COCHINSHIP COLPAL
    COFORGE CROMPTON CONCOR DABUR ANGELONE APOLLOHOSP DELHIVERY DIVISLAB
    DLF DMART DRREDDY DIXON ETERNAL FORCEMOT FORTIS GLENMARK
    GODFRYPHLP BANKINDIA GODREJPROP GODREJCP HCLTECH HDFCBANK GRASIM GVT&D
    HAVELLS HDFCLIFE BEL BHEL HINDALCO BIOCON HINDUNILVR HINDZINC
    IDFCFIRSTB INDUSINDBK ICICIGI CGPOWER IRFC JINDALSTEL JIOFIN IEX
    INDHOTEL INDIANB JSWENERGY JSWSTEEL KAYNES KEI INFY INOXWIND
    ITC KPITTECH JUBLFOOD LT M&M KALYANKJIL MANKIND MARICO
    ADANIPOWER MCX NAM-INDIA KFINTECH NESTLEIND EICHERMOT LODHA FEDERALBNK
    OBEROIRLTY LTM LUPIN PAGEIND MANAPPURAM PAYTM PFC PGEL
    MARUTI MAXHEALTH PHOENIXLTD PNB MOTHERSON POLYCAB POWERINDIA NMDC
    OFSS PRESTIGE OIL ONGC PATANJALI RECLTD SBILIFE GMRAIRPORT
    SBIN SHREECEM TATACONSUM PETRONET TATAELXSI TATASTEEL TMPV UPL
    PIDILITIND WAAREEENER PIIND BAJAJFINSV POLICYBZR PREMIERENE RADICO RBLBANK
    SAIL SOLARINDS SUNPHARMA SUPREMEIND SUZLON SWIGGY TATAPOWER TCS
    TIINDIA TITAN TVSMOTOR UNIONBANK VBL VEDL ZYDUSLIFE HEROMOTOCO
    HYUNDAI ICICIBANK INDIGO BSE LICHSGFIN LTF HDFCAMC MOTILALOFS
    MPHASIS NATIONALUM NBCC NYKAA ICICIPRULI PERSISTENT PNBHOUSING POWERGRID
    LAURUSLABS RELIANCE MAZDOCK SONACOMS NAUKRI SRF TECHM ULTRACEMCO
    UNOMINDA VMM WIPRO ASTRAL BAJFINANCE UNITDSPR ASHOKLEY MUTHOOTFIN
    CUMMINSIND GAIL SIEMENS MFSL NHPC NTPC TORNTPHARM RVNL
    KOTAKBANK LICI AUBANK HAL IDEA INDUSTOWER IOC IREDA
    TRENT SBICARD SHRIRAMFIN CANBK YESBANK VOLTAS HINDPETRO ATHERENERG
    MAHABANK SAGILITY
""".split()                           # F&O-eligible stocks (NSE symbols as used by Dhan; Yahoo uses SYMBOL.NS)
UNIVERSE = [s.strip().upper() for s in (os.environ.get("BPB_SYMBOLS") or "").replace(",", " ").split()] or FNO
LOOKBACK = int(os.environ.get("BPB_LOOKBACK") or 10)          # rolling-high window (days)
RESET_LINE = os.environ.get("BPB_RESET_LINE") == "1"          # 1 = a fresh breakout candle before any pullback moves the line up to the newest 10-day high
SLS = [10, 20, 30]                                            # stop-loss, % of the option premium
TPS = [0, 10, 20, 40, 60, 80, 120, 160, 200]                  # target, % of the option premium (0 = no target, shown as a baseline)
EXITS = ["09:30", "09:40", "10:00"]                           # time exits
CAPS = {10: 200000, 20: 100000, 30: 66667}                    # equal risk per trade: capital per stop-loss
ENTRY_LAST = os.environ.get("BPB_ENTRY_LAST") or "09:59"      # entry candles: 09:15 .. 09:59 (an entry needs a later exit time)
ENTRY_MIN = int(ENTRY_LAST[:2]) * 60 + int(ENTRY_LAST[3:])
PRE_TOL = float(os.environ.get("PRE_TOL") or 0.04)            # daily-open prefilter: open within 4 % below the level (entry is only in the first minutes)
EXTRA = [int(x) for x in (os.environ.get("OFFSETS2") or "1,-1").split(",") if x.strip()]    # neighbouring strikes, fetched only when needed
GAP_S = float(os.environ.get("DHAN_GAP") or 0.21)             # seconds between the START of two Dhan calls, all threads together
CONC = int(os.environ.get("DHAN_CONC") or 16)                 # Dhan calls in flight at the same time
BUDGET_MIN = float(os.environ.get("BUDGET_MIN") or 300)       # stop politely after this many minutes
DAY_CAP = int(os.environ.get("DAY_CAP") or 95000)             # Dhan Data API allows 100,000 calls per day
EQ_SPAN = int(os.environ.get("EQ_SPAN") or 85)                # stock 1-minute candles: days per call (Dhan max 90)
EQ_GAP = int(os.environ.get("EQ_GAP") or 30)                  # merge candidate days closer than this into one stock call
OPT_GAP = int(os.environ.get("OPT_GAP") or 15)                # merge option dates closer than this into one call (span max 30 days)
OUT = os.environ.get("BPB_OUT", "bpb_fno_results")
BASE = "https://api.dhan.co/v2"
MASTER = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
T0 = time.time()
LAST_CP = time.time()
FLUSHER = [None]
EK = ["stock", "direction", "date", "exit_rule", "sl", "tp"]            # one trade row
DK = ["stock", "direction", "date"]                               # one entry event


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
        self.stats = {}                                           # path -> [calls, seconds]

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
            failed_body = isinstance(j, dict) and str(j.get("status", "")).lower() == "failed"
            if r.status_code == 200 and j is not None and not code and not failed_body:
                with self.lock:
                    if time.monotonic() >= self.pause_until: self.rl = 0
                return j
            if r.status_code == 429 or code in self.RATE_CODES:
                with self.lock:                                   # the first thread to see it pauses everybody; the others just wait
                    now = time.monotonic(); first = now >= self.pause_until
                    if first:
                        self.rl += 1; s = min(10 * 2 ** (self.rl - 1), 300)
                        self.pause_until = now + s; self.next_t = max(self.next_t, self.pause_until)
                        self.gap = min(self.gap * 1.15, 0.5)
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
    """Run fn(task) in CONC threads with a continuously refilled queue; handle(task, result) runs in the main thread."""
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
    if j is None: return None                                    # call failed (reason printed by Dhan.post)
    fr = frame(j.get("data", j) if isinstance(j.get("data", None), dict) else j)
    if fr is None:
        print(f"[stock candles {sid} {d0}..{d1}] Dhan answered but sent no candles: {str(j)[:300]}", flush=True)
        return pd.DataFrame(columns=["o", "h", "l", "c"], index=pd.DatetimeIndex([]))
    return fr


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


# ------------------------------------------------------------------ step 1: daily candles -> breakout / pullback setups
def find_setups(O, H, L, C, lookback=LOOKBACK):
    """Breakout -> pullback -> re-cross state machine on daily candles, written for the LONG side.
    SHORT is the mirror: call it with (-O, -L, -H, -C) and negate the returned level / line.
    Returns [(day index i, entry level, line, breakout day index)]: day i is a day on which price may re-cross the entry level
    (the pullback was already confirmed by the days BEFORE i). The cross itself is checked later on 1-minute candles."""
    n = len(C)
    ref = np.full(n, np.nan)
    for i in range(lookback, n): ref[i] = H[i - lookback:i].max()          # highest High of the previous `lookback` days
    out, st = [], None                                                     # st = [line, highest high since breakout, bearish seen, breakout index]
    for i in range(lookback, n):
        if st is not None and st[2] and H[i] >= st[1]:                     # confirmed pullback, price re-crosses the high -> entry day
            out.append((i, st[1], st[0], st[3])); st = None                # setup used up
        elif st is not None and st[2]:                                     # confirmed pullback, no re-cross today
            if C[i] < st[0]: st = None                                     # pullback candle closed below the line -> invalid
            continue
        elif st is not None:                                               # breakout seen, pullback not yet confirmed
            if RESET_LINE and C[i] > ref[i]: st = [ref[i], H[i], False, i]; continue   # optional: pull back to the newest line
            if C[i] < st[0]: st = None                                     # closed below the line -> invalid (may start a new setup below)
            else:
                st[1] = max(st[1], H[i])
                if C[i] < O[i]: st[2] = True                               # bearish candle after the breakout = pullback confirmed
                continue
        if st is None and C[i] > ref[i]: st = [ref[i], H[i], False, i]     # a new breakout day
    return out


def yahoo_candidates():
    import yfinance as yf
    t0, t1 = pd.Timestamp(START), pd.Timestamp(END)
    raw = yf.download([s + ".NS" for s in UNIVERSE], start=str((t0 - pd.Timedelta(days=200)).date()), end=str((t1 + pd.Timedelta(days=3)).date()),
                      group_by="ticker", auto_adjust=False, progress=False, threads=True)
    rows, nst = [], 0
    for s in UNIVERSE:
        try: d = raw[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
        if len(d) < 60: continue
        nst += 1
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        O, H, L, C = (d[k].values.astype(float) for k in ("Open", "High", "Low", "Close"))
        dates = d.index.strftime("%Y-%m-%d")
        for long in (True, False):
            sg = 1.0 if long else -1.0
            args = (O, H, L, C) if long else (-O, -L, -H, -C)
            for i, lvl, line, b in find_setups(*args):
                if not (t0 <= d.index[i] <= t1): continue
                lvl, line = sg * lvl, sg * line                                          # back to real prices
                if (long and not (H[i] >= lvl and O[i] >= lvl * (1 - PRE_TOL))) or \
                   (not long and not (L[i] <= lvl and O[i] <= lvl * (1 + PRE_TOL))): continue   # entry is in the first minutes: open must be near the level
                rows.append(dict(stock=s, direction="LONG" if long else "SHORT", ref=round(lvl, 2), line=round(line, 2),
                                 breakout_date=dates[b], date=dates[i], yahoo_open=float(O[i])))
    if nst == 0: raise Fatal("Yahoo download gave no data for any stock (see the 'Failed downloads' lines above) - run again later")
    r = pd.DataFrame(rows)
    print(f"Yahoo: {nst} stocks, {len(r)} candidate entry days (pullback confirmed, high/low reachable)", flush=True)
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
    if FLUSHER[0]: FLUSHER[0]()
    steps = [["git", "config", "user.name", "bpbfno-bot"], ["git", "config", "user.email", "bpbfno-bot@users.noreply.github.com"],
             ["git", "add", OUT], ["git", "commit", "-m", "bpb fno progress"],
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
    s["done"] = set(s["done"])
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
def find_entry(u, level, long):
    """u = entry-day 1-minute candles (09:15 .. ENTRY_LAST). -> (entry minute, gap_open) of the first candle that reaches the level, else None."""
    idx, h, l, o = u.index, u.h.values, u.l.values, u.o.values
    touch = (h >= level) if long else (l <= level)
    if not touch.any(): return None
    k = int(np.argmax(touch))
    gap = bool(o[k] >= level) if long else bool(o[k] <= level)           # already beyond the level when that candle opened
    return idx[k], gap


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

    def work(t):
        s, g, d0, d1, key = t
        u_all = eq_minute(dh, mst[s][0], d0, d1)
        if u_all is None: return None                             # failed -> NOT marked done, retried on the next run
        if u_all.empty: return [], 0
        u_all = u_all[(u_all.index.hour.values * 60 + u_all.index.minute.values) <= ENTRY_MIN]
        days = {k: v for k, v in u_all.groupby(u_all.index.date)}
        out = []
        for r in g.itertuples():
            u = days.get(r.d)
            if u is None or u.empty: continue
            ratio = float(u.o.iloc[0]) / float(r.yahoo_open)
            k = ratio if abs(ratio - 1) > .2 else 1.0                                  # split/bonus: Yahoo prices adjusted, Dhan raw
            lvl, line = float(r.ref) * k, float(r.line) * k
            e = find_entry(u, lvl, r.direction == "LONG")
            if e is None: continue
            m, gap = e
            out.append(dict(stock=s, direction=r.direction, ref=round(lvl, 2), line=round(line, 2), breakout_date=r.breakout_date, date=r.date,
                            entry_minute=hm(m), gap_open=int(gap), stock_price=float(u.c[m])))
        return out, len(days)

    fails = [0]

    def handle(t, res):
        s, g, d0, d1, key = t
        if res is None:
            fails[0] += 1
            print(f"stock candles {s} {d0}..{d1}: FAILED (will be retried on the next run), calls so far {dh.n}", flush=True); return
        out, nd = res
        if out: ev.extend(out)
        st["done"].add(key); flush(st, ev, ep); checkpoint()
        print(f"stock candles {s} {d0}..{d1}: {len(g)} candidate days, minute data on {nd} days, {len(out)} entries, calls so far {dh.n}", flush=True)

    FLUSHER[0] = lambda: flush(st, ev, ep, force=True)
    try: stream(tasks, work, handle)
    finally: flush(st, ev, ep, force=True)
    if fails[0]: print(f"WARNING: {fails[0]} stock-candle request(s) failed - see the 'Dhan says' lines above; run again to retry them.", flush=True)
    return clean_events(ev)


# ------------------------------------------------------------------ step 3: ATM option candles -> trades
def exit_walk(o, h, l, entry, sl_pct, tp_pct):
    """First stop-loss / target touch on 1-minute option candles. Gap through the level fills at the open. If stop and target fall in the same
    candle the STOP wins (cannot know the order inside a minute). Returns (candle index, price, reason) or None = no touch before the exit time."""
    sl = entry * (1 - sl_pct / 100)
    sh = l <= sl; i_s = int(np.argmax(sh)) if sh.any() else None
    i_t, tp = None, None
    if tp_pct:
        tp = entry * (1 + tp_pct / 100); th = h >= tp; i_t = int(np.argmax(th)) if th.any() else None
    if i_s is None and i_t is None: return None
    if i_t is None or (i_s is not None and i_s <= i_t):
        return (i_s, float(o[i_s]), "STOP (gap)") if o[i_s] <= sl else (i_s, float(sl), "STOP")
    return (i_t, float(o[i_t]), "TARGET (gap)") if o[i_t] >= tp else (i_t, float(tp), "TARGET")


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
    if last is None: return "skip", "entry at/after the exit time"
    amins = atm.ts.dt.hour.values * 60 + atm.ts.dt.minute.values
    expected = int(((atm.ts > te).values & (amins <= last)).sum())
    if strict and expected and (mins <= last).sum() < 0.98 * expected: return "retry", None
    rows = []
    for ex in EXITS:
        lim = int(ex[:2]) * 60 + int(ex[3:])
        if hm(te) >= ex: continue
        w = ser[mins <= lim]
        if w.empty: continue
        o, h, l, cc = w.o.values, w.h.values, w.l.values, w.c.values
        for sl in SLS:
            lots = int(CAPS[sl] // (entry * lot))
            if lots < 1: continue
            qty, cost = lot * lots, entry * lot * lots
            for tp in TPS:
                r = exit_walk(o, h, l, entry, sl, tp)
                if r: i, px, why = r; xt = w.ts.iloc[i]
                else: i, px, why = len(w) - 1, float(cc[-1]), "TIME"; xt = w.ts.iloc[-1]
                late = int(why == "TIME" and (lim - (xt.hour * 60 + xt.minute)) > 5)           # option data thin near the exit time
                rows.append((e.stock, e.direction, e.date, e.breakout_date, e.line, e.ref, int(e.gap_open), hm(te), K, round(entry, 2), ex, sl, tp, lots, round(cost),
                             hm(xt), round(px, 2), why, round((px - entry) * qty), round((px / entry - 1) * 100, 1), late, round(float(e.stock_price), 2)))
    if not rows: return "skip", "no option candles between entry and exit (or one lot costs more than the capital)"
    return "ok", rows


COLS = ["stock", "direction", "date", "breakout_date", "line", "entry_level", "gap_open", "entry_time", "strike", "entry_price", "exit_rule", "sl", "tp", "lots", "cost",
        "exit_time", "exit_price", "reason", "pnl", "ret_pct", "thin_data", "stock_price"]


def prep_series(series):
    allr = pd.concat(series).reset_index().rename(columns={"index": "ts"})
    return {d: g for d, g in allr.groupby(allr.ts.dt.date)}        # day -> that day's candles (all strikes)


def work_options(dh, mst, t):
    """One request group: ATM candles first; neighbouring strikes only for the trades that need them."""
    s, dr, g, d0, d1, key = t
    lot, sid = mst[s][1], mst[s][0]
    x0 = rolling(dh, sid, d0, d1 + timedelta(days=1), dr, 0)
    skips = []
    if x0 is None:
        return [], {"no option data": len(g)}, [(e.stock, e.direction, e.date, "Dhan returned no option candles for this period") for e in g.itertuples()]
    x0["off"] = 0
    if "strike" not in x0:
        return [], {"Dhan sent no strike column": len(g)}, [(e.stock, e.direction, e.date, "Dhan sent no strike column") for e in g.itertuples()]
    allr = prep_series([x0])
    rows, miss, retry = [], {}, []

    def note(e, r): miss[r] = miss.get(r, 0) + 1; skips.append((e.stock, e.direction, e.date, r))
    for e in g.itertuples():
        st_, r = build(e, allr, lot, True)
        if st_ == "ok": rows += r
        elif st_ == "retry": retry.append(e)
        else: note(e, r)
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
            else: note(e, r)
    elif retry:
        for e in retry:
            st_, r = build(e, allr, lot, False)
            if st_ == "ok": rows += r
            else: note(e, r)
    return rows, miss, skips


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

    def work(t):
        rows, miss, skips = work_options(dh, mst, t)
        s, dr, g, d0, d1, key = t
        if rows:
            pd.DataFrame(rows, columns=COLS).to_csv(f"{OUT}/parts/{s}_{dr}_{d0}_{d1}.csv.gz", index=False, compression={"method": "gzip", "compresslevel": 1})
        if skips:
            os.makedirs(f"{OUT}/skipped", exist_ok=True)
            pd.DataFrame(skips, columns=["stock", "direction", "date", "reason"]).to_csv(f"{OUT}/skipped/{s}_{dr}_{d0}_{d1}.csv", index=False)
        return len(rows), miss

    def handle(t, res):
        s, dr, g, d0, d1, key = t; n_rows, miss = res
        st["done"].add(key); flush(st); checkpoint()
        print(f"options {s} {dr} {d0}..{d1}: {len(g)} entries, {n_rows} result rows" + (f", skipped {miss}" if miss else "") + f", calls so far {dh.n}", flush=True)

    FLUSHER[0] = lambda: flush(st, force=True)
    try: stream(tasks, work, handle)
    finally: flush(st, force=True)


# ------------------------------------------------------------------ step 4: summaries
def load_parts(fs):
    with ThreadPoolExecutor(8) as pool: dfs = list(pool.map(pd.read_csv, fs))
    return pd.concat(dfs, ignore_index=True).drop_duplicates(EK)


AGG_COLS = ["trades", "wins", "win_pct", "stops", "targets", "gap_stops", "time_exits", "total_pnl", "capital", "roi_pct", "avg_pnl", "avg_ret_pct", "profit_factor", "thin_data"]


def agg_by(t, keys):
    p = t.pnl
    x = t.assign(_w=p > 0, _gain=p.clip(lower=0), _loss=(-p).clip(lower=0), _st=t.reason.str.startswith("STOP"), _tg=t.reason.str.startswith("TARGET"),
                 _gap=t.reason == "STOP (gap)", _tm=t.reason == "TIME")
    g = x.groupby(keys).agg(trades=("pnl", "size"), wins=("_w", "sum"), stops=("_st", "sum"), targets=("_tg", "sum"), gap_stops=("_gap", "sum"), time_exits=("_tm", "sum"),
                            total_pnl=("pnl", "sum"), capital=("cost", "sum"), avg_pnl=("pnl", "mean"), avg_ret_pct=("ret_pct", "mean"),
                            gain=("_gain", "sum"), loss=("_loss", "sum"), thin_data=("thin_data", "sum"))
    g["win_pct"] = (g.wins / g.trades * 100).round(1)
    g["roi_pct"] = (g.total_pnl / g.capital * 100).round(2)
    g["profit_factor"] = (g.gain / g.loss.where(g.loss > 0)).round(2)
    g["avg_ret_pct"] = g.avg_ret_pct.round(2)
    for c in ("wins", "stops", "targets", "gap_stops", "time_exits", "total_pnl", "capital", "avg_pnl", "thin_data"): g[c] = g[c].astype(np.int64)
    return g[AGG_COLS]


def max_drawdown(t):
    """Largest peak-to-trough fall of the cumulative P&L, trades taken in date / entry-time order."""
    c = t.sort_values(["date", "entry_time"]).pnl.cumsum().values
    return int((c - np.maximum.accumulate(np.concatenate([[0], c]))[1:]).min()) if len(c) else 0


def tables(t, out, mt):
    """Summary tables for the trades in t (every TP x SL x exit-time variant), written into folder out."""
    os.makedirs(out, exist_ok=True)
    t = t.copy(); t["year"] = t.date.str[:4]; t["month"] = t.date.str[:7]
    base = ["exit_rule", "sl", "tp"]
    tot = agg_by(t, base).reset_index().sort_values("roi_pct", ascending=False)
    tot.to_csv(f"{out}/summary.csv", index=False)
    tot.pivot_table(index=["exit_rule", "sl"], columns="tp", values="roi_pct").to_csv(f"{out}/roi_matrix.csv")       # ROI % : rows exit/SL, columns TP
    for name, extra in (("by_year", "year"), ("by_month", "month"), ("by_direction", "direction"), ("by_stock", "stock")):
        agg_by(t, base + [extra]).reset_index().to_csv(f"{out}/{name}.csv", index=False)
    cols = ["exit_rule", "sl", "tp", "trades", "win_pct", "stops", "targets", "total_pnl", "roi_pct", "profit_factor"]
    ok = tot[tot.trades >= mt]
    print(f"\n{t.drop_duplicates(DK).shape[0]:,} entries, {len(t):,} trade rows over {len(tot)} variants (tp 0 = no target)\n"
          f"\nBEST 15 VARIANTS BY ROI (min {mt} trades):\n" + ok.head(15)[cols].to_string(index=False) +
          f"\n\nWORST 5:\n" + ok.tail(5)[cols].to_string(index=False), flush=True)


def progress():
    st = load_state(); exp = set(st.get("expected", [])) | set(st.get("expected_eq", []))
    if not exp: return
    done = len(exp & set(st["done"]))
    msg = (f"COMPLETE - all {len(exp)} request groups finished." if done >= len(exp) else
           f"PARTIAL - {done} of {len(exp)} request groups finished ({done / len(exp) * 100:.0f}%). Results cover only the finished part. Run again to continue.")
    open(f"{OUT}/PROGRESS.txt", "w").write(msg + "\n"); print("\n*** " + msg + " ***", flush=True)


def report(n_trades):
    """REPORT.txt: how many setups survived each step, so an empty result can be explained."""
    def rows(p): return len(pd.read_csv(p)) if os.path.exists(p) else 0
    cand = glob.glob(f"{OUT}/candidates_*.csv")
    lines = [f"Top stocks tested: {' '.join(UNIVERSE)}",
             f"1. Daily setups (breakout + confirmed pullback + entry level reachable that day): {rows(cand[0]) if cand else 0}",
             f"2. Entries (1-minute stock price reached the level between 09:15 and {ENTRY_LAST}): {rows(f'{OUT}/events.csv')}",
             f"3. Trade rows with option results ({len(SLS)} SL x {len(TPS)} TP x {len(EXITS)} exit times per entry): {n_trades}"]
    sk = sorted(glob.glob(f"{OUT}/skipped/*.csv"))
    if sk:
        k = pd.concat([pd.read_csv(f) for f in sk], ignore_index=True).drop_duplicates(["stock", "direction", "date"])
        k.to_csv(f"{OUT}/skipped.csv", index=False)
        lines.append(f"4. Entries with NO option trade: {len(k)} - reasons: " + "; ".join(f"{r} = {n}" for r, n in k.reason.value_counts().items()))
    open(f"{OUT}/REPORT.txt", "w").write("\n".join(lines) + "\n"); print("\n" + "\n".join(lines), flush=True)


def summary():
    progress()
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    os.makedirs(OUT, exist_ok=True)
    if not fs:
        pd.DataFrame(columns=COLS).to_csv(f"{OUT}/trades_all.csv", index=False)
        report(0); print("No trades yet - see REPORT.txt and the log above (failed Dhan calls print 'Dhan says').", flush=True); return
    t = load_parts(fs)
    t.sort_values(["date", "stock", "direction"]).to_csv(f"{OUT}/trades_all.csv", index=False)
    print(f"ALL TRADES: {len(t):,} rows -> {OUT}/trades_all.csv", flush=True)
    report(len(t)); tables(t, OUT, int(os.environ.get("MIN_TRADES") or 30))


def range_summary(start, end):
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    if not fs: sys.exit(f"No saved results in {OUT}/parts - run the backtest first")
    t = load_parts(fs); t = t[(t.date >= start) & (t.date <= end)]
    if t.empty: sys.exit(f"No trades with entry date between {start} and {end}")
    out = f"bpb_range_out/{start}_to_{end}"; os.makedirs(out, exist_ok=True)
    t.sort_values(["date", "stock"]).to_csv(f"{out}/trades_in_range.csv", index=False)
    tables(t, out, int(os.environ.get("MIN_TRADES") or 5)); print(f"\nSaved in {out}/")


# ------------------------------------------------------------------ modes
def check():
    dh = Dhan(); mst = load_master()
    print(f"Instrument list OK: {len(mst)} stocks with options. RELIANCE ->", mst.get("RELIANCE"), flush=True)
    miss = [s for s in UNIVERSE if s not in mst]
    print(f"{len(UNIVERSE) - len(miss)} of {len(UNIVERSE)} universe stocks found in Dhan list. In the script list but NOT in Dhan's stock-option list: {miss}", flush=True)
    new = sorted(set(mst) - set(UNIVERSE))
    print(f"In Dhan's stock-option list but NOT in the script list ({len(new)}): {new}  -> add any you want tested to FNO, or pass BPB_SYMBOLS.", flush=True)
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
    print(f"Candidate days {START} to {END}: {len(cand)} for {UNIVERSE}", flush=True)
    dh = Dhan(); mst = load_master()
    try:
        ev = step_events(dh, cand, mst, st)
        ev = ev[(ev["date"] >= START) & (ev["date"] <= END)] if len(ev) else ev
        print(f"Entries (price reached the level between 09:15 and {ENTRY_LAST}): {len(ev)}", flush=True)
        if not len(ev): print("NO ENTRIES - if the lines above show FAILED / 'Dhan says', the stock candles were not downloaded (token / Data API); otherwise no setup reached its level in the window.", flush=True)
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
        else: sys.exit("use: python bpb_fno_backtest.py check | run | summary | range")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
