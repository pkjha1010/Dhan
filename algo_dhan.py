"""Dhan backtest Jan-2025 .. Sep-2026: 3 entry types x ATM / ITM-1 option x 5 exit rules x SL10/20 x 9 targets.

  python algo_dhan.py test     one-time check of the Dhan API format + calibration (about 10 calls)
  python algo_dhan.py run      the backtest (resumable: run again until every stock is done)

Self-contained (no other file needed).  Secrets: DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN.

DATA SOURCES
  Yahoo daily : signal (10-day line, pullback candle) and the days on which the line is touched.
  Dhan 1-min  : stock minute candles ONLY for those touch days (Yahoo keeps just ~30 days of 1-minute history, so it cannot
                serve 2025-2026), then option minute candles from Dhan "expired options" (rolling ATM, monthly expiry).
  Both are range requests (28-90 days per call), cached on disk, so the number of calls stays far below 100,000 per day.

ENTRY TYPES (line = reference line; "wrong side" = below it for LONG, above it for SHORT)
  E1_all            first minute that touches the line, any time.
  E2_4candle_0920   first minute from 09:20 that touches the line while the 4 previous 1-min candles are all on the wrong side.
  E3_recross_0920   first touch is the "first cross" (its time is saved). Entry = a LATER minute from 09:20 whose 4 previous
                    candles are all on the wrong side and which closes across the line.
OPTION  : monthly expiry, ATM and ITM-1 (one strike in the money: lower strike for CE, higher for PE) chosen at the entry minute.
          The strike is then FIXED: later prices are those of the same strike (found through the rolling ATM+-3 series).
ENTRY PRICE : close of the first option candle at/after the stock entry minute (same day, within ENTRY_DELAY_MIN, else skipped).
EXIT CHECKS : price = close of the 1-min candle that ENDS at 10:00 / 11:00 / 12:00 / 15:30.
  D1000, D1100, D1200, D1530 : same-day rules - SL/TP tested at each check up to that time, otherwise time exit at that time.
  CARRY                      : the same checks on every following day until SL or TP is hit (or expiry / end of data).
  An exit is booked at the price seen at the check, so a stop can be worse than -SL% (gap) - that overshoot is visible in the
  results (avg_stop_ret_pct).  Returns are premium %, and P&L is shown on a fixed Rs 40,000 per trade (no lot rounding).
"""
import os, sys, io, re, json, glob, time, calendar
from datetime import date, datetime, timedelta, time as dtime
from functools import reduce
from math import gcd
import numpy as np
import pandas as pd
import requests
from types import SimpleNamespace
from zoneinfo import ZoneInfo

# ------------------------------------------------------------------ strategy helpers (copied from algo.py, so this file is self-contained)
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


def shape(o, h, l, c):
    """Last daily candle: body < 45% of range and a wick (upper or lower) >= 2x body."""
    if h == l: return False
    b = abs(c - o)
    return b / (h - l) < .45 and max(h - max(o, c), min(o, c) - l) >= 2 * b


def setup(df, long):
    """Most recent valid break-of-structure setup for the last candle, else None. Returns (ref_line, swing, bos, pullback dates)."""
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


def recross(u, ref, long, tc, a, b):
    """First minute in [a, b] after the first cross where the 4 candles before it stayed on the wrong side and this minute closes across."""
    for m in u.index:
        hm = f"{m:%H:%M}"
        if m <= tc or hm < a or hm > b: continue
        w = u[u.index < m].tail(4)
        if len(w) < 4: continue
        ltp = u.c[m]
        if ((w.h < ref).all() and ltp >= ref) if long else ((w.l > ref).all() and ltp <= ref): return m, ltp
    return None, None


A = SimpleNamespace(UNIVERSE=UNIVERSE, shape=shape, setup=setup, recross=recross, IST=ZoneInfo("Asia/Kolkata"))

ROOT, CACHE = "dhan_backtest", "dhan_cache"
BASE = "https://api.dhan.co/v2"
MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"
START = os.environ.get("BT_START") or "2025-01-01"
END = os.environ.get("BT_END") or "2026-09-30"
SLS, TPS = (10, 20), (20, 30, 40, 60, 80, 100, 120, 140, 200)
VARIANTS = [(s, t) for s in SLS for t in TPS]
CHECKS = [("1000", 9, 59), ("1100", 10, 59), ("1200", 11, 59), ("1530", 15, 29)]   # label, START minute of the candle ending at the label
MODES = ["D1000", "D1100", "D1200", "D1530", "CARRY"]
ENTRY_FROM, ENTRY_END = "09:20", "15:20"
STRIKES = ("ATM", "ITM1")
MAX_DELAY = int(os.environ.get("ENTRY_DELAY_MIN") or 5)          # max minutes between stock entry and first option candle
MAX_CALLS = int(os.environ.get("MAX_CALLS") or 60000)            # Dhan calls allowed in one run (daily limit is 100,000)
ONLY = [x.strip() for x in (os.environ.get("STOCKS") or "").split(",") if x.strip()]
MAX_OFF = 3                                                      # Dhan serves ATM+-3 for stock options
GAP_S = 0.25                                                     # 4 requests/second (limit is 5)
CAP = 40000

CAL, CALSET, LAST_DAY, DAILY, SECID, CALIB = [], set(), None, {}, {}, {}


# ------------------------------------------------------------------ Dhan HTTP (paced)
class StopRun(Exception):
    pass


CALLS, LAST_CALL, SEEN_ERR = 0, 0.0, set()


def post(path, body):
    """-> (True, json) or (False, text). Waits for the rate limit, retries temporary errors, stops on bad token."""
    global CALLS, LAST_CALL
    h = {"access-token": os.environ["DHAN_ACCESS_TOKEN"], "client-id": os.environ.get("DHAN_CLIENT_ID", ""),
         "Content-Type": "application/json", "Accept": "application/json"}
    for k in range(6):
        if CALLS >= MAX_CALLS: raise StopRun()
        w = GAP_S - (time.time() - LAST_CALL)
        if w > 0: time.sleep(w)
        LAST_CALL = time.time(); CALLS += 1
        try:
            r = requests.post(BASE + path, headers=h, json=body, timeout=90)
        except Exception as e:
            print(f"  network error {e!r} - retrying", flush=True); time.sleep(5 * (k + 1)); continue
        txt = r.text[:300]
        if r.status_code == 200:
            try: return True, r.json()
            except Exception: return False, "not json: " + txt
        if r.status_code == 429 or re.search(r"\b805\b|DH-904", txt):
            print("  Dhan rate limit - waiting 60 s", flush=True); time.sleep(60); continue
        if r.status_code in (401, 403) or re.search(r"DH-90[123]\b|\b80[6-9]\b|\b810\b", txt):
            sys.exit(f"Dhan refused the request ({r.status_code}): {txt}\nCheck DHAN_ACCESS_TOKEN (it expires) and that the Data API is subscribed.")
        if r.status_code >= 500: time.sleep(5 * (k + 1)); continue
        if txt not in SEEN_ERR and len(SEEN_ERR) < 8:
            SEEN_ERR.add(txt); print(f"  Dhan {r.status_code}: {txt}", flush=True)
        return False, txt
    raise RuntimeError("Dhan request kept failing")


def nodata(txt):
    return "DH-907" in txt or "no data" in txt.lower()


def parse_ts(arr):
    """Epoch seconds -> IST clock times. Handles 1970/1980 epoch and UTC/IST-shifted epochs by looking at the data."""
    if arr is None or len(arr) == 0: return pd.DatetimeIndex([])
    s = pd.Series(np.rint(pd.to_numeric(pd.Series(arr), errors="coerce").fillna(0)).astype("int64"))
    s = s.where(s > 1.5e9, s + 315532800)
    t = pd.to_datetime(s, unit="s")
    if (t.dt.hour * 60 + t.dt.minute).min() < 480: t = t + pd.Timedelta(hours=5, minutes=30)     # UTC epoch -> IST
    return pd.DatetimeIndex(t)


def read_cached(p):
    df = pd.read_csv(p, index_col=0, parse_dates=True)
    return df if len(df) else None


def write_cached(p, df, cols):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    (df if df is not None else pd.DataFrame(columns=cols)).to_csv(p)


# ------------------------------------------------------------------ stock minute candles
def equity_days(stock, secid, days):
    """{day: DataFrame(o,h,l,c) or None}. One call covers up to 85 days; every day is saved on its own."""
    out, need = {}, []
    for d in days:
        p = f"{CACHE}/eq/{stock}/{d}.csv.gz"
        if os.path.exists(p): out[d] = read_cached(p)
        else: need.append(d)
    i = 0
    while i < len(need):
        j = i
        while j + 1 < len(need) and (need[j + 1] - need[i]).days <= 85: j += 1
        a, b = need[i], need[j]
        ok, jj = post("/charts/intraday", {"securityId": str(secid), "exchangeSegment": "NSE_EQ", "instrument": "EQUITY",
                                           "interval": "1", "oi": False, "fromDate": f"{a} 09:15:00", "toDate": f"{b} 15:30:00"})
        whole = None
        if ok and jj.get("timestamp"):
            ts = parse_ts(jj["timestamp"]); n = len(ts)
            cols = {k: pd.to_numeric(pd.Series(jj.get(src) or []), errors="coerce").values
                    for k, src in (("o", "open"), ("h", "high"), ("l", "low"), ("c", "close"))}
            if all(len(v) == n for v in cols.values()):
                whole = pd.DataFrame(cols, index=ts).dropna()
                whole = whole[~whole.index.duplicated()].sort_index()
        elif not ok and not nodata(jj):
            i = j + 1; continue                                    # temporary/unknown failure: do not cache
        for d in need[i:j + 1]:
            x = None
            if whole is not None:
                x = whole[whole.index.normalize() == pd.Timestamp(d)]
                x = x if len(x) else None
            write_cached(f"{CACHE}/eq/{stock}/{d}.csv.gz", x, ["o", "h", "l", "c"])
            out[d] = x
        i = j + 1
    return out


def align(u, yh, yl, yc):
    """Dhan prices must match Yahoo's daily candle of the same day (splits/bonus make them differ). Rescales big ratios, rejects the rest."""
    dh, dl, dc = float(u.h.max()), float(u.l.min()), float(u.c.iloc[-1])
    f = yc / dc if dc > 0 and abs(yc / dc - 1) > .08 else 1.0
    if abs(dh * f / yh - 1) > .03 or abs(dl * f / yl - 1) > .03: return None
    return u if f == 1.0 else u * f


# ------------------------------------------------------------------ entries (stock minute candles)
def touch4(u, ref, long, a, b):
    """First minute in [a, b] that touches the line while the 4 candles before it were all on the wrong side."""
    for m in u.index:
        hm = f"{m:%H:%M}"
        if hm < a or hm > b: continue
        w = u[u.index < m].tail(4)
        if len(w) < 4: continue
        if (u.h[m] >= ref and (w.h < ref).all()) if long else (u.l[m] <= ref and (w.l > ref).all()):
            return m, float(u.c[m])
    return None, None


def entries(u, ref, long):
    """-> (first touch minute, {entry type: (minute, stock price at entry)})"""
    hit = u[(u.h >= ref) if long else (u.l <= ref)]
    if hit.empty: return None, {}
    tc, out = hit.index[0], {}
    if f"{tc:%H:%M}" <= ENTRY_END: out["E1_all"] = (tc, float(u.c[tc]))
    m, p = touch4(u, ref, long, ENTRY_FROM, ENTRY_END)
    if m is not None: out["E2_4candle_0920"] = (m, p)
    m, p = A.recross(u, ref, long, tc, ENTRY_FROM, ENTRY_END)
    if m is not None: out["E3_recross_0920"] = (m, float(p))
    return tc, out


def find_signals(df, days):
    """Daily scan (same rules as algo.py) -> [(date, direction, line, day high, day low, day close)] where the line is touched that day."""
    out, idx = [], df.index
    for T in days:
        Ts = pd.Timestamp(T)
        pos = idx.searchsorted(Ts)
        if pos >= len(idx) or idx[pos] != Ts or pos < 40: continue
        sub = df.iloc[:pos].tail(80)
        o, h, l, c = sub.iloc[-1][["Open", "High", "Low", "Close"]]
        if not A.shape(o, h, l, c): continue
        day = df.iloc[pos]
        for long in (True, False):
            r = A.setup(sub, long)
            if r is None: continue
            ref = round(float(r[0]), 2)
            if (day.High >= ref) if long else (day.Low <= ref):
                out.append((T, "LONG" if long else "SHORT", ref, float(day.High), float(day.Low), float(day.Close)))
    return out


# ------------------------------------------------------------------ expiry calendar
def month_expiry(y, m):
    """Monthly stock expiry: last Thursday until Aug-2025, last Tuesday from Sep-2025; holiday -> previous trading day."""
    wd = 3 if (y, m) < (2025, 9) else 1
    d = date(y, m, calendar.monthrange(y, m)[1])
    while d.weekday() != wd: d -= timedelta(days=1)
    while CAL and CAL[0] <= d <= LAST_DAY and d not in CALSET: d -= timedelta(days=1)
    return d


def expiry_on_or_after(T):
    y, m = T.year, T.month
    while True:
        E = month_expiry(y, m)
        if E >= T: return E
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


# ------------------------------------------------------------------ option candles (rolling ATM series)
def rolling(secid, otype, code, strike, a, b):
    """One call, dates a..b inclusive (<= 28 days). -> ('ok', df or None) | ('err', text). df: close, strike, spot."""
    ok, j = post("/charts/rollingoption", {
        "exchangeSegment": "NSE_FNO", "interval": "1", "securityId": str(secid), "instrument": "OPTSTK", "expiryFlag": "MONTH",
        "expiryCode": int(code), "strike": strike, "drvOptionType": "CALL" if otype == "CE" else "PUT",
        "requiredData": ["open", "high", "low", "close", "volume", "strike", "spot"],
        "fromDate": str(a), "toDate": str(b + timedelta(days=1))})                 # toDate is non-inclusive
    if not ok: return "err", j
    side = ((j or {}).get("data") or {}).get("ce" if otype == "CE" else "pe")
    if not side or not side.get("timestamp"): return "ok", None
    ts = parse_ts(side["timestamp"]); n = len(ts)
    d = {c: pd.to_numeric(pd.Series(side.get(c) or []), errors="coerce").values for c in ("close", "strike", "spot")}
    if len(d["spot"]) == 0: d["spot"] = np.full(n, np.nan)
    if any(len(v) != n for v in d.values()): return "err", "unexpected array lengths in response"
    df = pd.DataFrame(d, index=ts).dropna(subset=["close", "strike"])
    df = df[~df.index.duplicated()].sort_index()
    return "ok", df


def at(df, ts, tol=5):
    """Last candle at or before ts on the same day (not older than tol minutes)."""
    if df is None or df.empty: return None
    i = df.index.searchsorted(ts, side="right") - 1
    if i < 0: return None
    t = df.index[i]
    if t.date() != ts.date() or (ts - t) > pd.Timedelta(minutes=tol): return None
    return df.iloc[i]


class Opt:
    """Option series of one stock / CE-PE / monthly expiry. Frames are cached on disk and shared by every trade of that cycle."""

    def __init__(self, stock, secid, otype, E):
        self.stock, self.secid, self.otype, self.E = stock, secid, otype, E
        self.code = CALIB["code"]
        self.sgn = CALIB["sign_ce" if otype == "CE" else "sign_pe"]          # API offset per strike step upwards
        self.itm_off = -self.sgn if otype == "CE" else self.sgn              # ITM-1: lower strike for CE, higher for PE
        self.mem = {}
        self.hint = None                                                     # exact strike step, learned from the ITM-1 entry

    def frame(self, off, d):
        k = (self.E - d).days // 28
        if (off, k) in self.mem: return self.mem[(off, k)]
        end = self.E - timedelta(days=28 * k); start = end - timedelta(days=27)
        p = f"{CACHE}/opt/{self.stock}_{self.otype}_{self.E}_{self.code}_{off}_{k}.csv.gz"
        complete = end <= LAST_DAY
        if os.path.exists(p): df = read_cached(p)
        else:
            st, df = rolling(self.secid, self.otype, self.code, "ATM" if off == 0 else f"ATM{off:+d}", start, end)
            if st == "err":
                if complete and nodata(df): write_cached(p, None, ["close", "strike", "spot"])
                df = None
            else:
                if df is not None:
                    ix = df.index.normalize()
                    df = df[(ix >= pd.Timestamp(start)) & (ix <= pd.Timestamp(end))]
                    df = df if len(df) else None
                if complete: write_cached(p, df, ["close", "strike", "spot"])
        self.mem[(off, k)] = df
        return df

    def entry(self, m, sel):
        """First candle at/after the stock entry minute m -> ((time, strike, price), None) or (None, reason)."""
        d = m.date()
        df = self.frame(0 if sel == "ATM" else self.itm_off, d)
        if df is None: return None, "no option data"
        i = df.index.searchsorted(m, side="left")
        if i >= len(df): return None, "no option candle after the signal"
        t, r = df.index[i], df.iloc[i]
        if t.date() != d or (t - m) > pd.Timedelta(minutes=MAX_DELAY):
            return None, f"first option candle {t:%d-%b %H:%M} too late for signal {m:%H:%M}"
        if not r.close > 0: return None, "zero option price"
        if sel == "ITM1":                                                    # one strike in the money: learn the step, check the direction
            a = at(self.frame(0, d), t)
            if a is not None and abs(a.strike - r.strike) > 1e-6:
                if (r.strike < a.strike) != (self.otype == "CE"): return None, "ITM-1 strike is on the wrong side of ATM"
                self.hint = self.hint or abs(float(a.strike - r.strike))
        return (t, float(r.strike), round(max(round(float(r.close) / .05) * .05, .05), 2)), None

    def step(self, base, d):
        """Strike spacing: exact value learned from the ITM-1 entry, else the greatest common divisor of the strikes seen."""
        if self.hint: return self.hint
        day = base[base.index.normalize() == pd.Timestamp(d)]
        for fr in (day, base):
            u = np.diff(np.unique(np.round(fr.strike.values * 100).astype(np.int64)))
            if len(u): return reduce(gcd, [int(x) for x in u]) / 100
        return None

    def price(self, K0, ts):
        """Close of strike K0 at ts (via the ATM series, or the ATM+-n series that holds K0 at that moment)."""
        d = ts.date()
        base = self.frame(0, d)
        r0 = at(base, ts)
        if r0 is None: return None
        if abs(r0.strike - K0) < 1e-6: return float(r0.close)
        step = self.step(base, d)
        if not step: return None
        n = int(round((K0 - r0.strike) / step))
        if n == 0 or abs(n) > MAX_OFF: return None
        for off in (self.sgn * n, -self.sgn * n):
            r = at(self.frame(off, d), ts)
            if r is not None and abs(r.strike - K0) < 1e-6: return float(r.close)
        return None


# ------------------------------------------------------------------ exits
def walk(opt, K0, P0, te, E):
    """Checks at 10:00 / 11:00 / 12:00 / 15:30 -> columns for every exit mode x SL x TP (ret %, reason letter)."""
    d1 = te.date()
    pts, carry, missing = [], {v: None for v in VARIANTS}, 0
    for d in [x for x in CAL if d1 <= x <= min(E, LAST_DAY)]:
        for label, hh, mm in CHECKS:
            ts = pd.Timestamp(d.year, d.month, d.day, hh, mm)
            if ts <= te: continue
            px = opt.price(K0, ts)
            if px is None: missing += 1; continue
            ret = (px / P0 - 1) * 100
            pts.append((d, label, ret))
            for v in VARIANTS:
                if carry[v] is None:
                    if ret <= -v[0]: carry[v] = (ret, "S")
                    elif ret >= v[1]: carry[v] = (ret, "T")
        if all(carry[v] is not None for v in VARIANTS): break
    out, last = {"missing": missing}, (pts[-1] if pts else None)
    day1 = [(l, r) for dd, l, r in pts if dd == d1]
    for label, _, _ in CHECKS:
        out[f"ret_{label}"] = next((round(r, 1) for l, r in day1 if l == label), np.nan)
    for sl, tp in VARIANTS:
        v, tag = (sl, tp), f"SL{sl}_TP{tp}"
        if carry[v] is not None: ret, code = carry[v]
        elif last is None: ret, code = np.nan, "N"
        else: ret, code = last[2], ("E" if last[0] >= E else ("O" if E > LAST_DAY else "M"))
        out[f"r_CARRY_{tag}"], out[f"x_CARRY_{tag}"] = (round(ret, 1) if ret == ret else np.nan), code
        for label, _, _ in CHECKS:
            seq = [(l, r) for l, r in day1 if l <= label]
            ret, code = np.nan, "N"
            for l, r in seq:
                if r <= -sl: ret, code = r, "S"; break
                if r >= tp: ret, code = r, "T"; break
            else:
                fin = [r for l, r in seq if l == label]
                if fin: ret, code = fin[0], "X"
            out[f"r_D{label}_{tag}"], out[f"x_D{label}_{tag}"] = (round(ret, 1) if ret == ret else np.nan), code
    return out


# ------------------------------------------------------------------ one stock
def run_stock(stock):
    df, secid = DAILY.get(stock), SECID.get(stock)
    if df is None or secid is None: return [], [dict(stock=stock, reason="no Yahoo data or no Dhan security id")]
    days = [d for d in CAL if date.fromisoformat(START) <= d <= date.fromisoformat(END)]
    sigs = find_signals(df, days)
    if not sigs: return [], []
    eq = equity_days(stock, secid, sorted({s[0] for s in sigs}))
    opts, rows, skips = {}, [], []
    for T, direction, ref, yh, yl, yc in sigs:
        long = direction == "LONG"

        def skip(why, etype=""):
            skips.append(dict(date=str(T), stock=stock, direction=direction, entry=etype, reason=why))

        u = eq.get(T)
        if u is None: skip("no Dhan minute data"); continue
        u = align(u, yh, yl, yc)
        if u is None: skip("price mismatch with Yahoo (split / bonus?)"); continue
        tc, ent = entries(u, ref, long)
        if not ent: continue
        otype, E = ("CE" if long else "PE"), expiry_on_or_after(T)
        if E == T: skip("expiry day"); continue
        opt = opts.setdefault((otype, E), Opt(stock, secid, otype, E))
        for etype, (m, sp) in ent.items():
            found = {sel: opt.entry(m, sel) for sel in reversed(STRIKES)}      # ITM-1 first: it teaches the strike spacing
            for sel in STRIKES:
                res, why = found[sel]
                if res is None: skip(f"{sel}: {why}", etype); continue
                te, K0, P0 = res
                row = dict(date=str(T), entry=etype, strike_sel=sel, stock=stock, direction=direction, ref=ref,
                           first_cross=f"{tc:%H:%M}", stock_entry_time=f"{m:%H:%M}", stock_entry_price=round(sp, 2),
                           opt_entry_time=f"{te:%H:%M}", strike=K0, expiry=str(E), opt_entry_price=P0)
                row.update(walk(opt, K0, P0, te, E))
                rows.append(row)
    return rows, skips


# ------------------------------------------------------------------ calibration (expiry code, strike direction)
def calibrate(force=False):
    p = f"{CACHE}/calib.json"
    if not force and os.path.exists(p):
        CALIB.update(json.load(open(p))); print("Calibration (saved):", CALIB, flush=True); return
    sid = SECID.get("RELIANCE") or next(iter(SECID.values()))
    env = (os.environ.get("EXPIRY_CODE") or "").strip()
    print(f"Calibrating on RELIANCE (security id {sid}) ...", flush=True)
    near = fr = None
    for a, b in ((date(2025, 3, 3), date(2025, 3, 12)), (date(2025, 6, 2), date(2025, 6, 11))):
        fr = {}
        for code in ((int(env),) if env else (0, 1, 2)):
            st, df = rolling(sid, "CE", code, "ATM", a, b)
            print(f"  expiryCode {code}: {st}, {'no rows' if df is None else (df[:120] if isinstance(df, str) else str(len(df)) + ' candles')}", flush=True)
            if st == "ok" and df is not None and len(df) > 50: fr[code] = df
        if env and fr: near = int(env); break
        if len(fr) >= 2:
            common = sorted(set.intersection(*[set(f.index) for f in fr.values()]))
            means = {c: (f.close.reindex(common) if common else f.close).mean() for c, f in fr.items()}
            print("  mean ATM premium by expiryCode:", {c: round(v, 2) for c, v in means.items()}, "-> lowest = nearest expiry", flush=True)
            near = min(means, key=means.get); break
    if near is None:
        sys.exit("Calibration failed: Dhan returned no usable option data. Check the Data API subscription, the 'Expired options' access, "
                 "and the lines above. You can force the near-month code with the EXPIRY_CODE input.")
    sign = {}
    for ot in ("CE", "PE"):
        _, atm = (("ok", fr[near]) if ot == "CE" else rolling(sid, "PE", near, "ATM", a, b))
        _, up = rolling(sid, ot, near, "ATM+1", a, b)
        if atm is None or up is None or isinstance(atm, str) or isinstance(up, str):
            sys.exit(f"Calibration failed for {ot}: ATM / ATM+1 data missing")
        idx = atm.index.intersection(up.index)
        diff = (up.strike.reindex(idx) - atm.strike.reindex(idx)).median()
        if not diff == diff or diff == 0: sys.exit(f"Calibration failed for {ot}: could not compare strikes")
        sign[ot] = 1 if diff > 0 else -1
        print(f"  {ot}: 'ATM+1' is {'a HIGHER' if diff > 0 else 'a LOWER'} strike (median step {abs(diff):g})", flush=True)
    CALIB.update(code=int(near), sign_ce=sign["CE"], sign_pe=sign["PE"])
    os.makedirs(CACHE, exist_ok=True); json.dump(CALIB, open(p, "w"))
    print("Calibration:", CALIB, flush=True)


# ------------------------------------------------------------------ setup of data
def load_master():
    r = requests.get(MASTER_URL, timeout=180); r.raise_for_status()
    m = pd.read_csv(io.StringIO(r.text), low_memory=False)
    c = {x.strip(): x for x in m.columns}
    pick = lambda *n: next((c[x] for x in n if x in c), None)
    exch, seg, sid = pick("SEM_EXM_EXCH_ID", "EXCH_ID"), pick("SEM_SEGMENT", "SEGMENT"), pick("SEM_SMST_SECURITY_ID", "SECURITY_ID")
    sym, inst, ser = pick("SEM_TRADING_SYMBOL", "UNDERLYING_SYMBOL"), pick("SEM_INSTRUMENT_NAME", "INSTRUMENT"), pick("SEM_SERIES", "SERIES")
    if None in (exch, seg, sid, sym): sys.exit(f"Unexpected scrip master columns: {list(m.columns)[:25]}")
    q = m[(m[exch] == "NSE") & (m[seg] == "E")]
    if inst: q = q[q[inst] == "EQUITY"]
    if ser: q = q[q[ser].astype(str).str.strip() == "EQ"]
    return {str(s).strip(): int(i) for s, i in zip(q[sym], q[sid])}


def init(stocks):
    global CAL, CALSET, LAST_DAY, DAILY, SECID
    import yfinance as yf
    SECID = load_master()
    now = datetime.now(A.IST)
    names = sorted(set(stocks) | {"RELIANCE"})
    raw = None
    for k in range(3):
        try:
            raw = yf.download([s + ".NS" for s in names], start="2024-08-01", end=str(now.date() + timedelta(days=1)),
                              group_by="ticker", auto_adjust=False, progress=False, threads=True); break
        except Exception as e:
            print("Yahoo problem:", e, flush=True); time.sleep(10)
    if raw is None: sys.exit("Yahoo download failed")
    for s in names:
        try: d = raw[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except Exception: continue
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        if len(d) and d.index[-1].date() == now.date() and now.time() < dtime(15, 45): d = d.iloc[:-1]
        DAILY[s] = d
    if "RELIANCE" not in DAILY: sys.exit("No Yahoo data for RELIANCE (needed as the trading calendar)")
    CAL = sorted({x.date() for x in DAILY["RELIANCE"].index}); CALSET = set(CAL); LAST_DAY = CAL[-1]
    print(f"Yahoo: {len(DAILY)} stocks, calendar {CAL[0]} .. {LAST_DAY}; Dhan equity ids: {sum(1 for s in stocks if s in SECID)}/{len(stocks)}", flush=True)


# ------------------------------------------------------------------ reports
def stat(r, x):
    m = r.notna(); r, x = r[m], x[m]
    if len(r) == 0: return None
    pos, neg, s = r[r > 0].sum(), -r[r < 0].sum(), x == "S"
    return dict(trades=len(r), win_pct=round((r > 0).mean() * 100, 1), avg_ret_pct=round(r.mean(), 2), total_ret_pct=round(r.sum(), 1),
                profit_factor=round(pos / neg, 2) if neg > 0 else np.nan, targets=int((x == "T").sum()), stops=int(s.sum()),
                time_exit=int((x == "X").sum()), expiry=int((x == "E").sum()), open_or_missing=int(x.isin(["O", "M"]).sum()),
                avg_stop_ret_pct=round(r[s].mean(), 1) if s.any() else np.nan, pnl_on_40k=int(r.sum() / 100 * CAP))


def read_all(pattern):
    fr = []
    for f in sorted(glob.glob(pattern)):
        try: fr.append(pd.read_csv(f))
        except pd.errors.EmptyDataError: pass
    return pd.concat(fr, ignore_index=True) if fr else pd.DataFrame()


def summarize():
    t = read_all(f"{ROOT}/by_stock/*.csv")
    if t.empty: print("No trades yet"); return
    t["quarter"] = pd.PeriodIndex(pd.to_datetime(t.date), freq="Q").astype(str)
    rows, qrows = [], []
    for (et, sel), g in t.groupby(["entry", "strike_sel"]):
        for mode in MODES:
            for sl, tp in VARIANTS:
                r, x = g[f"r_{mode}_SL{sl}_TP{tp}"], g[f"x_{mode}_SL{sl}_TP{tp}"]
                s = stat(r, x)
                if s is None: continue
                key = dict(entry=et, strike_sel=sel, exit_mode=mode, variant=f"SL{sl}/TP{tp}")
                rows.append({**key, **s})
                for q, gq in g.groupby("quarter"):
                    sq = stat(gq[r.name], gq[x.name])
                    if sq: qrows.append({**key, "quarter": q, "trades": sq["trades"], "win_pct": sq["win_pct"], "avg_ret_pct": sq["avg_ret_pct"]})
    S = pd.DataFrame(rows)
    S.to_csv(f"{ROOT}/dhan_summary.csv", index=False)
    pd.DataFrame(qrows).to_csv(f"{ROOT}/dhan_summary_by_quarter.csv", index=False)
    order = [f"SL{sl}/TP{tp}" for sl, tp in VARIANTS]
    for col, name in (("win_pct", "win_pct"), ("avg_ret_pct", "avg_ret")):
        S.pivot_table(index=["entry", "strike_sel", "exit_mode"], columns="variant", values=col)[order].to_csv(f"{ROOT}/dhan_matrix_{name}.csv")
    tt = []
    for (et, sel), g in t.groupby(["entry", "strike_sel"]):
        tt.append(dict(entry=et, strike_sel=sel, trades=len(g), **{f"avg_ret_{l}": round(g[f"ret_{l}"].mean(), 2) for l, _, _ in CHECKS},
                       **{f"win_pct_{l}": round((g[f"ret_{l}"].dropna() > 0).mean() * 100, 1) for l, _, _ in CHECKS}))
    pd.DataFrame(tt).to_csv(f"{ROOT}/dhan_time_exit_no_sl_tp.csv", index=False)
    best = S[S.trades >= 30].sort_values("total_ret_pct", ascending=False).head(25)
    best.to_csv(f"{ROOT}/dhan_best_combos.csv", index=False)
    print(f"\n===== TRADES (entries) per type =====\n{t.groupby(['entry', 'strike_sel']).size().to_string()}")
    print("\n===== AVG RETURN % PER TRADE, CARRY exit =====")
    print(S[S.exit_mode == "CARRY"].pivot_table(index=["entry", "strike_sel"], columns="variant", values="avg_ret_pct")[order].to_string())
    print("\n===== WIN %, CARRY exit =====")
    print(S[S.exit_mode == "CARRY"].pivot_table(index=["entry", "strike_sel"], columns="variant", values="win_pct")[order].to_string())
    print("\n===== TOP 25 COMBINATIONS BY TOTAL RETURN (>= 30 trades) =====")
    print(best[["entry", "strike_sel", "exit_mode", "variant", "trades", "win_pct", "avg_ret_pct", "total_ret_pct", "profit_factor", "pnl_on_40k"]].to_string(index=False))
    s = read_all(f"{ROOT}/skipped/*.csv")
    if not s.empty:
        s["why"] = s.reason.astype(str).str.replace(r"\d{2}:\d{2}|\d{2}-\w{3}", "", regex=True).str[:60]
        print("\n===== WHY ENTRIES WERE SKIPPED =====\n" + s.why.value_counts().head(12).to_string())


# ------------------------------------------------------------------ modes
def test():
    stocks = ["RELIANCE"]
    init(stocks)
    sid = SECID.get("RELIANCE")
    print(f"RELIANCE equity id in Dhan master: {sid}")
    d = [x for x in CAL if x <= date(2026, 9, 24)][-1]
    print(f"\nStock minute candles for {d}:")
    ok, j = post("/charts/intraday", {"securityId": str(sid), "exchangeSegment": "NSE_EQ", "instrument": "EQUITY", "interval": "1",
                                      "oi": False, "fromDate": f"{d} 09:15:00", "toDate": f"{d} 15:30:00"})
    if ok:
        ts = parse_ts(j.get("timestamp") or [])
        print(f"  keys {list(j.keys())}, {len(ts)} candles, first {ts[0] if len(ts) else None}, last {ts[-1] if len(ts) else None}")
        print(f"  raw first timestamp {(j.get('timestamp') or [None])[0]}, first close {(j.get('close') or [None])[0]}")
    else: print("  failed:", j)
    calibrate(force=True)
    print("\nOption candles (CE ATM, near expiry), first rows of 2025-03-03:")
    st, df = rolling(sid, "CE", CALIB["code"], "ATM", date(2025, 3, 3), date(2025, 3, 3))
    print(df.head(5).to_string() if df is not None and not isinstance(df, str) else (st, df))
    print("\nMonthly expiry dates used by the script (check these against NSE):")
    print("  " + ", ".join(f"{y}-{m:02d}:{month_expiry(y, m):%d-%b-%a}" for y in (2025, 2026) for m in range(1, 13)))
    print(f"\nDhan calls used: {CALLS}")


def run():
    stocks = [s for s in A.UNIVERSE if not ONLY or s in ONLY]
    os.makedirs(f"{ROOT}/by_stock", exist_ok=True); os.makedirs(f"{ROOT}/skipped", exist_ok=True); os.makedirs(CACHE, exist_ok=True)
    init(stocks)
    missing = [s for s in stocks if s not in SECID]
    if missing: print("No Dhan equity id for:", ", ".join(missing), flush=True)
    calibrate()
    sp = f"{ROOT}/state.json"
    done = set(json.load(open(sp))["done"]) if os.path.exists(sp) else set()
    print(f"{START} .. {END}   done stocks {len(done & set(stocks))}/{len(stocks)}   Dhan call limit this run {MAX_CALLS}", flush=True)
    stopped = False
    for n, s in enumerate(stocks, 1):
        if s in done: continue
        try:
            rows, skips = run_stock(s)
        except StopRun:
            print(f"\nCALL LIMIT ({MAX_CALLS}) reached at {s} - progress saved, run again to continue", flush=True); stopped = True; break
        if rows: pd.DataFrame(rows).to_csv(f"{ROOT}/by_stock/{s}.csv", index=False)
        if skips: pd.DataFrame(skips).to_csv(f"{ROOT}/skipped/{s}.csv", index=False)
        done.add(s); json.dump({"done": sorted(done)}, open(sp, "w"))
        print(f"[{n}/{len(stocks)}] {s}: {len(rows)} trade rows, {len(skips)} skipped, Dhan calls so far {CALLS}", flush=True)
    summarize()
    left = [s for s in stocks if s not in done]
    if left: print(f"\nNOT DONE YET: {len(left)} stock(s) - run the workflow again ({left[0]} ...)", flush=True)
    print(f"\nDhan calls this run: {CALLS}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "test": test()
    elif mode == "run": run()
    else: sys.exit("use: python algo_dhan.py test | run")
