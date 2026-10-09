"""
Options backtest for the SWG break-of-structure swing strategy (swing_alerts.py).

Pipeline
  1. Yahoo daily candles -> trading calendar + the same signals swing_alerts.py makes
     after market close (shape() + setup() copied verbatim).
  2. Next trading day, only if Yahoo's daily High/Low actually reached the ref line,
     fetch that day's 1-minute EQUITY candles from Dhan to find the exact entry minute.
  3. Fetch 1-minute ATM option candles from Dhan's expired-options API
     (/v2/charts/rollingoption), lock the strike that was ATM at entry, and follow that
     same strike until exit (LONG -> CE, SHORT -> PE, buying options).
  4. Simulate every variant:
        entry type : ALERT    - first touch of ref line from 09:15 (what the Kite alert does)
                     CONFIRM  - from 09:20, close crosses the line and the previous
                                4 one-minute closes were on the other side
                     RECROSS  - same validated cross as CONFIRM, then wait for a
                                close back below/above the line and enter on the re-cross
        stop loss  : 10%, 20% of option premium
        target     : 20,30,40,60,80,100,120,140,200 %
        exit       : 10:00, 12:00, 15:30 (first occurrence after entry) or HIT
                     (hold until SL/TP, capped at expiry day close / --max-hold-days)
        capital    : <= 200,000 per trade for SL10, <= 100,000 for SL20 (whole lots)

API economy (Dhan data APIs: 5 req/s, 100,000 req/day)
  * Global rate limiter (default 4 req/s), retry/backoff on 429 / DH-904.
  * Every response is cached on disk (cache/). The GitHub workflow persists the cache,
    so a run that stops on --max-requests resumes where it left off.
  * Equity minute data is fetched only for days where Yahoo shows the line was hit.
  * Option data: one ATM call per <=30-day chunk of the holding window; an ATM+/-k
    series is fetched only if the locked strike stops being ATM before the last
    variant has exited.

Env: DHAN_ACCESS_TOKEN, DHAN_CLIENT_ID
"""
import argparse, gzip, json, math, os, sys, time
from datetime import date, datetime, timedelta, time as dtime
from zoneinfo import ZoneInfo

import numpy as np, pandas as pd, requests, yfinance as yf

IST = ZoneInfo("Asia/Kolkata")
API = "https://api.dhan.co/v2"
MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"

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

ENTRY_TYPES = ("ALERT", "CONFIRM", "RECROSS")
SL_LIST = (10, 20)
TP_LIST = (20, 30, 40, 60, 80, 100, 120, 140, 200)
EXIT_MODES = ("10:00", "12:00", "15:30", "HIT")
CAPITAL = {10: 200_000, 20: 100_000}
MAX_OFFSET = 3  # Dhan allows ATM-3..ATM+3 for stock options
NEAR_CODE = [0]  # expiryCode of the nearest monthly expiry (Dhan annexure: 0 = current); auto-checked


# ----------------------------------------------------------------------------------
# Strategy logic - copied verbatim from swing_alerts.py
# ----------------------------------------------------------------------------------
def shape(o, h, l, c):
    """Last candle: body < 45% of range and a wick (upper or lower) >= 2x body."""
    if h == l: return False
    b = abs(c - o)
    return b / (h - l) < .45 and max(h - max(o, c), min(o, c) - l) >= 2 * b


def setup(df, long):
    """Most recent valid break-of-structure setup for the last candle, else None.
    Returns (ref_line, swing_date, bos_date, pullback_date)."""
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


# ----------------------------------------------------------------------------------
# Dhan client with rate limit, retries, disk cache and a request budget
# ----------------------------------------------------------------------------------
class BudgetExhausted(Exception):
    pass


class DhanError(Exception):
    pass


class Dhan:
    def __init__(self, cache_dir, rate, max_requests, max_minutes=0):
        tok, cid = os.environ.get("DHAN_ACCESS_TOKEN"), os.environ.get("DHAN_CLIENT_ID")
        if not tok or not cid:
            sys.exit("Set DHAN_ACCESS_TOKEN and DHAN_CLIENT_ID")
        self.h = {"access-token": tok.strip(), "client-id": cid.strip(),
                  "Content-Type": "application/json", "Accept": "application/json"}
        self.cache_dir, self.gap, self.max = cache_dir, 1.0 / rate, max_requests
        self.used, self.hits, self.last, self.fail_streak = 0, 0, 0.0, 0
        self.s = requests.Session()
        self.deadline = time.monotonic() + max_minutes * 60 if max_minutes else None

    def _path(self, key):
        return os.path.join(self.cache_dir, key[:4], key + ".json.gz")

    def raw(self, path, body):
        """One rate-limited call, no cache (used by --probe)."""
        wait = self.gap - (time.monotonic() - self.last)
        if wait > 0: time.sleep(wait)
        self.last = time.monotonic(); self.used += 1
        return self.s.post(API + path, headers=self.h, json=body, timeout=60)

    def post(self, path, body, key):
        f = self._path(key)
        if os.path.exists(f):
            with gzip.open(f, "rt") as fh:
                data = json.load(fh)
            # older versions cached failed calls; only "no data" (DH-907) is trusted now
            if not (isinstance(data, dict) and "_error" in data and "DH-907" not in data["_error"]):
                self.hits += 1
                return data
        if self.used >= self.max or (self.deadline and time.monotonic() > self.deadline):
            raise BudgetExhausted
        last = ""
        for attempt in range(5):
            try:
                r = self.raw(path, body)
            except requests.RequestException as e:
                last = f"network: {e}"; print(f"  ! {path} try {attempt + 1}: {last}", flush=True)
                time.sleep(2 ** attempt); continue
            txt = r.text
            if r.ok:
                try:
                    data = r.json()
                except ValueError:
                    data = {}
                self.fail_streak = 0
                self._save(f, data)
                return data
            if r.status_code in (401, 403) or "DH-901" in txt or "DH-902" in txt:
                sys.exit(f"Dhan auth/subscription error ({r.status_code}): {txt[:300]}")
            if r.status_code == 429 or "DH-904" in txt or '"805"' in txt or "Too many" in txt:
                last = f"rate limit {r.status_code}: {txt[:200]}"
                print(f"  ! {path} try {attempt + 1}: {last}", flush=True)
                time.sleep(min(60, 5 * 2 ** attempt)); continue
            last = f"HTTP {r.status_code}: {txt[:300]}"
            print(f"  ! {path} try {attempt + 1}: {last}", flush=True)
            if "DH-907" in txt:                    # no data for these params -> remember it
                self.fail_streak = 0
                self._save(f, {"_error": txt[:300]})
                return {"_error": txt[:300]}
            if r.status_code < 500 and "DH-908" not in txt and "DH-909" not in txt:
                break                               # bad input: retrying won't help
            time.sleep(2 ** attempt)
        self.fail_streak += 1
        if self.fail_streak >= 15:
            print("15 Dhan failures in a row - stopping, results so far are saved", flush=True)
            raise BudgetExhausted
        raise DhanError(f"{path} failed: {last} | body={body}")

    def _save(self, f, data):
        os.makedirs(os.path.dirname(f), exist_ok=True)
        with gzip.open(f, "wt") as fh:
            json.dump(data, fh)


def to_frame(d, cols=("open", "high", "low", "close")):
    """Dhan array response -> DataFrame indexed by IST minute."""
    if not isinstance(d, dict): return pd.DataFrame()
    if "timestamp" not in d and isinstance(d.get("data"), dict):
        d = d["data"]
    ts = d.get("timestamp") or []
    if not ts: return pd.DataFrame()
    out = {c: d.get(c) for c in cols if d.get(c) is not None and len(d.get(c)) == len(ts)}
    df = pd.DataFrame(out, index=pd.to_datetime(ts, unit="s", utc=True).tz_convert(IST))
    df = df[~df.index.duplicated()].sort_index()
    return df


def equity_minutes(dh, secid, day):
    ds = day.isoformat()
    body = {"securityId": str(secid), "exchangeSegment": "NSE_EQ", "instrument": "EQUITY",
            "interval": "1", "oi": False,
            "fromDate": f"{ds} 09:15:00", "toDate": f"{ds} 15:30:00"}
    df = to_frame(dh.post("/charts/intraday", body, f"eq_{secid}_{ds}"))
    if len(df):
        df = df[(df.index.date == day) & (df.index.time >= dtime(9, 15)) & (df.index.time < dtime(15, 30))]
    return df


def option_chunk(dh, secid, opt, offset, code, frm, to_excl):
    strike = "ATM" if offset == 0 else f"ATM{offset:+d}"
    body = {"exchangeSegment": "NSE_FNO", "interval": "1", "securityId": str(int(secid)),
            "instrument": "OPTSTK", "expiryFlag": "MONTH", "expiryCode": int(code),
            "strike": strike, "drvOptionType": "CALL" if opt == "CE" else "PUT",
            "requiredData": ["open", "high", "low", "close", "strike"],
            "fromDate": frm.isoformat(), "toDate": to_excl.isoformat()}
    key = f"op_{secid}_{opt}_{strike}_{code}_{frm}_{to_excl}"
    raw = dh.post("/charts/rollingoption", body, key)
    d = (raw.get("data") or {}) if isinstance(raw, dict) else {}
    d = d.get("ce" if opt == "CE" else "pe") or {}
    return to_frame(d, ("open", "high", "low", "close", "strike"))


# ----------------------------------------------------------------------------------
# Calendar / expiries
# ----------------------------------------------------------------------------------
def monthly_expiries(trading_days, first, last):
    """NSE stock-option monthly expiry: last Thursday (till Aug-2025), last Tuesday
    (from Sep-2025); moved to the previous trading day on holidays."""
    td, out = set(trading_days), []
    y, m = first.year, first.month
    while (y, m) <= (last.year, last.month):
        wd = 3 if (y, m) < (2025, 9) else 1
        nxt = date(y + (m == 12), m % 12 + 1, 1)
        d = nxt - timedelta(days=1)
        while d.weekday() != wd: d -= timedelta(days=1)
        if d <= max(td):
            while d not in td: d -= timedelta(days=1)
        out.append(d)
        y, m = nxt.year, nxt.month
    return out


# ----------------------------------------------------------------------------------
# Signals from Yahoo daily candles
# ----------------------------------------------------------------------------------
def build_signals(symbols, start, end, tol):
    data = yf.download([s + ".NS" for s in symbols], start=(start - timedelta(days=150)).isoformat(),
                       end=(end + timedelta(days=5)).isoformat(), group_by="ticker",
                       auto_adjust=False, progress=False, threads=True)
    days, sigs, daily = set(), [], {}
    for s in symbols:
        try:
            df = data[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except KeyError:
            continue
        if len(df) < 41: continue
        df.index = pd.to_datetime(df.index).date
        daily[s] = df
        days.update(df.index)
        o, h, l, c = (df[x].values for x in ("Open", "High", "Low", "Close"))
        for n in range(39, len(df) - 1):
            nd = df.index[n + 1]
            if not (start <= nd <= end): continue
            if not shape(o[n], h[n], l[n], c[n]): continue
            win = df.iloc[max(0, n - 59):n + 1]     # ~same depth as the live 90-day download
            for long in (True, False):
                r = setup(win, long)
                if r is None: continue
                ref = round(float(r[0]), 2)
                touched = h[n + 1] >= ref * (1 - tol) if long else l[n + 1] <= ref * (1 + tol)
                sigs.append(dict(stock=s, dir="LONG" if long else "SHORT", ref=ref,
                                 signal_date=df.index[n], entry_date=nd, swing=r[1], bos=r[2],
                                 pullback=r[3], sig_low=l[n], sig_high=h[n],
                                 y_open=o[n + 1], y_high=h[n + 1], y_low=l[n + 1],
                                 daily_touch=bool(touched)))
    return pd.DataFrame(sigs), sorted(days), daily


# ----------------------------------------------------------------------------------
# Entry detection on 1-minute spot candles
# ----------------------------------------------------------------------------------
def find_entries(m, ref, long, last_entry):
    """Return {entry_type: signal-minute index} for the three entry styles."""
    if m.empty: return {}
    t = m.index.time
    o, h, l, c = (m[x].values for x in ("open", "high", "low", "close"))
    hit = (h >= ref) if long else (l <= ref)                 # touch
    over = (c >= ref) if long else (c <= ref)                # close across
    under = ~over                                            # close still on the old side
    ok_time = np.array([x <= last_entry for x in t])
    from920 = np.array([x >= dtime(9, 20) for x in t])
    out = {}
    idx = np.flatnonzero(hit & ok_time)
    if len(idx): out["ALERT"] = int(idx[0])
    n = len(m)
    valid4 = np.zeros(n, bool)
    for i in range(4, n):
        valid4[i] = under[i - 4:i].all()
    idx = np.flatnonzero(over & valid4 & from920 & ok_time)
    if len(idx): out["CONFIRM"] = int(idx[0])
    if "CONFIRM" in out:          # first validated cross, then a close back, then re-cross
        for i in range(out["CONFIRM"] + 2, n):
            if not ok_time[i]: break
            if over[i] and under[i - 1]:
                out["RECROSS"] = i; break
    return out


# ----------------------------------------------------------------------------------
# Locked-strike option series
# ----------------------------------------------------------------------------------
def chunks_for(window, expiries, target):
    """Split the holding window into Dhan calls: same expiryCode, <=30 calendar days."""
    ti, out = expiries.index(target), []
    for d in window:
        code = ti - next(i for i, e in enumerate(expiries) if e >= d) + NEAR_CODE[0]
        if out and out[-1][0] == code and (d - out[-1][1]).days < 30:
            out[-1][2] = d
        else:
            out.append([code, d, d])
    return [(c, f, t + timedelta(days=1)) for c, f, t in out]   # toDate is exclusive


def locked_series(dh, secid, opt, window, expiries, target, entry_ts, evaluate):
    """1-minute candles of the strike that was ATM at entry_ts, for the whole window.
    Only the ATM series is fetched up front; another ATM+/-k series is fetched only if
    the locked strike stops being ATM BEFORE the last variant has exited (evaluate(s)
    returns that time), so most trades cost 1 call per <=30-day chunk."""
    chunks = chunks_for(window, expiries, target)
    days = set(window)
    base = []
    for code, f, t in chunks:
        x = option_chunk(dh, secid, opt, 0, code, f, t)
        if len(x) and "strike" in x:
            base.append((code, f, t, x[np.isin(x.index.date, list(days))]))
    allb = pd.concat([x for *_, x in base]) if base else pd.DataFrame()
    if allb.empty: return pd.DataFrame(), None, 0
    row = allb[allb.index <= entry_ts]
    K = float((row if len(row) else allb).strike.iloc[-1])
    u = np.unique(allb.strike.values)
    step = float(np.diff(u).min()) if len(u) > 1 else None
    have = allb[allb.strike == K]
    fetched, extra_calls = set(), 0
    while step:
        s = have[~have.index.duplicated()].sort_index()
        until = evaluate(s)
        if until is None: return s, K, extra_calls
        miss = allb[(allb.strike != K) & (allb.index <= until) & ~allb.index.isin(s.index)]
        if miss.empty: return s, K, extra_calls
        ts0 = miss.index[0]
        j = int(round((K - miss.strike.iloc[0]) / step))
        code, f, t, _ = next(c for c in base if c[1] <= ts0.date() < c[2])
        todo = [k for k in (j, -j) if 0 < abs(k) <= MAX_OFFSET and (code, f, k) not in fetched]
        got = False
        for k in todo:                       # +j first; -j only if Dhan's sign is reversed
            fetched.add((code, f, k)); extra_calls += 1
            x = option_chunk(dh, secid, opt, k, code, f, t)
            x = x[(x.strike == K)] if len(x) and "strike" in x else x.iloc[0:0]
            if len(x) and ts0 in x.index:
                have = pd.concat([have, x[np.isin(x.index.date, list(days))]]); got = True; break
        if not got:                          # strike beyond ATM+/-3 or no data: leave the gap
            allb = allb.drop(allb.index[(allb.index.date == ts0.date()) & (allb.strike == miss.strike.iloc[0])])
    s = have[~have.index.duplicated()].sort_index()
    return s, K, extra_calls


# ----------------------------------------------------------------------------------
# Exit simulation (numpy; 2 SL x 9 TP x 4 exit modes from 15 scans)
# ----------------------------------------------------------------------------------
def costs(buy_val, sell_val, day):
    stt = 0.001 if day >= date(2024, 10, 1) else 0.000625
    txn = 0.0003503 if day >= date(2024, 10, 1) else 0.000495
    brok = 40.0
    exch = (buy_val + sell_val) * txn
    sebi = (buy_val + sell_val) * 1e-6
    return brok + exch + sebi + sell_val * stt + buy_val * 0.00003 + 0.18 * (brok + exch + sebi)


def simulate(s, fill_i, fill_px, deadlines, lot, slip, trade_day):
    """s: option frame; position opened at fill_px at bar fill_i (bar fill_i still checked
    for SL/TP when filled at its open). deadlines: {mode: tz-aware datetime}."""
    ts = s.index[fill_i:]
    o, h, l, c = (s[x].values[fill_i:] for x in ("open", "high", "low", "close"))
    n, out = len(ts), []
    first = lambda m: int(np.argmax(m)) if m.any() else n
    sl_hit = {p: first(l <= fill_px * (1 - p / 100)) for p in SL_LIST}
    tp_hit = {p: first(h >= fill_px * (1 + p / 100)) for p in TP_LIST}
    dl_idx = {m: int(np.searchsorted(ts.values, np.datetime64(d.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)), "left")) - 1
              for m, d in deadlines.items()}
    entry_px = fill_px * (1 + slip)
    for sl in SL_LIST:
        lots = int(CAPITAL[sl] // (entry_px * lot)) if entry_px > 0 else 0
        for tp in TP_LIST:
            for mode, di in dl_idx.items():
                si, ti = sl_hit[sl], tp_hit[tp]
                slp, tpp = fill_px * (1 - sl / 100), fill_px * (1 + tp / 100)
                if si <= di and si <= ti and si < n:          # SL first (also wins ties)
                    i, px, why = si, min(o[si], slp), "SL"        # gap through SL -> open
                elif ti <= di and ti < n:
                    i, px, why = ti, max(o[ti], tpp), "TP"        # gap through TP -> open
                elif di >= 0:
                    i, px = di, c[di]
                    late = (deadlines[mode] - ts[di].to_pydatetime()).total_seconds() > 1800
                    why = "DATA_GAP" if late else ("TIME" if mode != "HIT" else "EXPIRY/MAXHOLD")
                else:
                    i, px, why = 0, fill_px, "NO_DATA"
                exit_px = px * (1 - slip)
                qty = lots * lot
                gross = (exit_px - entry_px) * qty
                cst = costs(entry_px * qty, exit_px * qty, trade_day) if qty else 0.0
                out.append(dict(sl=sl, tp=tp, exit_mode=mode, exit_ts=ts[i] if n else None,
                                exit_px=round(exit_px, 2), reason=why, lots=lots, qty=qty,
                                capital=round(entry_px * qty, 2), gross=round(gross, 2),
                                costs=round(cst, 2), net=round(gross - cst, 2),
                                ret_pct=round((exit_px / entry_px - 1) * 100, 2)))
    return out


# ----------------------------------------------------------------------------------
def summarize(tr):
    tr = tr[tr.qty > 0].copy()
    if tr.empty: return pd.DataFrame()
    tr["exit_day"] = pd.to_datetime(tr.exit_ts.astype(str).str[:10])
    rows = []
    for k, g in tr.groupby(["entry_type", "sl", "tp", "exit_mode"]):
        g = g.sort_values("exit_ts")
        eq = g.net.cumsum()
        dd = (eq - eq.cummax()).min()
        w, lsum = g.net[g.net > 0].sum(), -g.net[g.net <= 0].sum()
        rows.append(dict(entry_type=k[0], sl=k[1], tp=k[2], exit_mode=k[3], trades=len(g),
                         win_pct=round((g.net > 0).mean() * 100, 1),
                         net_pnl=round(g.net.sum()), avg_pnl=round(g.net.mean()),
                         avg_ret_pct=round(g.ret_pct.mean(), 2),
                         profit_factor=round(w / lsum, 2) if lsum else np.inf,
                         max_dd=round(dd), tp_hits=int((g.reason == "TP").sum()),
                         sl_hits=int((g.reason == "SL").sum()),
                         long_pnl=round(g.net[g.dir == "LONG"].sum()),
                         short_pnl=round(g.net[g.dir == "SHORT"].sum())))
    return pd.DataFrame(rows).sort_values("net_pnl", ascending=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2023-01-01")
    ap.add_argument("--end", default="2026-09-30")
    ap.add_argument("--symbols", default="", help="comma list to test a subset")
    ap.add_argument("--max-requests", type=int, default=60_000, help="Dhan calls this run (day cap 100k)")
    ap.add_argument("--max-minutes", type=int, default=0, help="stop fetching after N minutes (0 = no limit)")
    ap.add_argument("--rate", type=float, default=4.0, help="requests/second (Dhan data limit 5)")
    ap.add_argument("--slippage", type=float, default=0.5, help="%% of premium per side")
    ap.add_argument("--entry-fill", choices=["next_open", "close"], default="next_open")
    ap.add_argument("--last-entry", default="15:00")
    ap.add_argument("--max-hold-days", type=int, default=0, help="0 = hold till expiry for HIT mode")
    ap.add_argument("--roll-on-expiry-day", type=int, default=1, help="1 = entry on expiry day uses next month")
    ap.add_argument("--yahoo-tol", type=float, default=0.003, help="tolerance for Yahoo touch pre-filter")
    ap.add_argument("--cache", default="cache")
    ap.add_argument("--out", default="results")
    ap.add_argument("--near-code", default="auto", help="expiryCode of nearest expiry: auto, 0 or 1")
    ap.add_argument("--probe", action="store_true", help="print raw Dhan replies for SBIN and exit")
    a = ap.parse_args()
    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    last_entry = dtime(*map(int, a.last_entry.split(":")))
    slip = a.slippage / 100
    os.makedirs(a.out, exist_ok=True)
    symbols = [x.strip() for x in a.symbols.split(",") if x.strip()] or UNIVERSE

    # instrument master -> underlying security id + lot size
    mpath = os.path.join(a.cache, "scrip_master.csv")
    if not os.path.exists(mpath) or time.time() - os.path.getmtime(mpath) > 86400:
        os.makedirs(a.cache, exist_ok=True)
        with open(mpath, "wb") as fh: fh.write(requests.get(MASTER_URL, timeout=120).content)
    mst = pd.read_csv(mpath, low_memory=False)
    op = mst[(mst.EXCH_ID == "NSE") & (mst.INSTRUMENT == "OPTSTK")].sort_values("SM_EXPIRY_DATE")
    op = op.drop_duplicates("UNDERLYING_SYMBOL")
    SEC = dict(zip(op.UNDERLYING_SYMBOL, op.UNDERLYING_SECURITY_ID.astype(int)))
    LOT = dict(zip(op.UNDERLYING_SYMBOL, op.LOT_SIZE.astype(int)))
    # optional historical lot sizes: lot_sizes.csv with columns symbol,from_date,lot
    lot_hist = pd.read_csv("lot_sizes.csv", parse_dates=["from_date"]) if os.path.exists("lot_sizes.csv") else None

    def lot_for(sym, d):
        if lot_hist is not None:
            h = lot_hist[(lot_hist.symbol == sym) & (lot_hist.from_date.dt.date <= d)]
            if len(h): return int(h.sort_values("from_date").lot.iloc[-1])
        return LOT.get(sym)

    print("Downloading Yahoo daily candles ...", flush=True)
    sigs, tdays, daily = build_signals(symbols, start, end, a.yahoo_tol)
    if sigs.empty: sys.exit("No signals")
    sigs.to_csv(os.path.join(a.out, "signals.csv"), index=False)
    expiries = monthly_expiries(tdays, start - timedelta(days=40), end + timedelta(days=70))
    tdi = {d: i for i, d in enumerate(tdays)}

    def next_tday(d):
        i = tdi.get(d)
        return tdays[i + 1] if i is not None and i + 1 < len(tdays) else d + timedelta(days=1)

    def utc64(t):
        return np.datetime64(t.astimezone(ZoneInfo("UTC")).replace(tzinfo=None))
    print(f"signals={len(sigs)} touched_next_day={sigs.daily_touch.sum()} stocks={len(daily)}", flush=True)

    dh = Dhan(a.cache, a.rate, a.max_requests, a.max_minutes)

    # a mid-cycle trading day (6 trading days after an expiry) for probing/calibration
    e0 = next(e for e in expiries if e >= start)
    pday = tdays[min(tdi.get(e0, 0) + 6, len(tdays) - 1)] if e0 in tdi else tdays[0]
    psec = SEC.get("SBIN", next(iter(SEC.values())))

    if a.probe:
        print(f"PROBE day={pday} secid={psec}", flush=True)
        r = dh.raw("/charts/intraday", {"securityId": str(psec), "exchangeSegment": "NSE_EQ",
                   "instrument": "EQUITY", "interval": "1", "oi": False,
                   "fromDate": f"{pday} 09:15:00", "toDate": f"{pday} 15:30:00"})
        print("equity intraday:", r.status_code, r.text[:300], flush=True)
        for c in (0, 1):
            r = dh.raw("/charts/rollingoption", {"exchangeSegment": "NSE_FNO", "interval": "1",
                       "securityId": str(psec), "instrument": "OPTSTK", "expiryFlag": "MONTH",
                       "expiryCode": c, "strike": "ATM", "drvOptionType": "CALL",
                       "requiredData": ["open", "high", "low", "close", "strike"],
                       "fromDate": pday.isoformat(), "toDate": (pday + timedelta(days=1)).isoformat()})
            print(f"rollingoption expiryCode={c}:", r.status_code, r.text[:400], flush=True)
        return

    # which expiryCode is the nearest month? near month = lower premium for the same ATM
    if a.near_code == "auto":
        med = {}
        for c in (0, 1):
            try:
                x = option_chunk(dh, psec, "CE", 0, c, pday, pday + timedelta(days=1))
                med[c] = float(x.close.median()) if len(x) else None
            except DhanError as e:
                print(f"calibration expiryCode={c} failed: {e}", flush=True); med[c] = None
        if med[0] and med[1]:
            NEAR_CODE[0] = 0 if med[0] <= med[1] else 1
        elif med[1] and not med[0]:
            NEAR_CODE[0] = 1
        elif not med[0] and not med[1]:
            sys.exit("Dhan rollingoption returned no data for expiryCode 0 or 1 - run with --probe and check the reply")
        print(f"ATM CE premium on {pday}: code0={med[0]} code1={med[1]} -> nearest expiryCode={NEAR_CODE[0]}", flush=True)
    else:
        NEAR_CODE[0] = int(a.near_code)
    trades, skipped, used_keys, pending = [], [], set(), 0
    cand = sigs[sigs.daily_touch].sort_values(["entry_date", "stock"])
    for k, r in enumerate(cand.itertuples(index=False)):
        long, sym, day = r.dir == "LONG", r.stock, r.entry_date
        key = (sym, r.dir, r.ref)
        if key in used_keys:   # live script keeps a same-name alert, so it can't fire twice
            skipped.append(dict(r._asdict(), why="same alert already triggered")); continue
        if sym not in SEC:
            skipped.append(dict(r._asdict(), why="no Dhan F&O id")); continue
        try:
            m = equity_minutes(dh, SEC[sym], day)
            if m.empty:
                skipped.append(dict(r._asdict(), why="no equity minute data")); continue
            ratio = m.open.iloc[0] / r.y_open if r.y_open else 1.0
            ref = r.ref * ratio if abs(ratio - 1) > 0.03 else r.ref   # split/bonus adjust
            ent = find_entries(m, ref, long, last_entry)
            if not ent:
                skipped.append(dict(r._asdict(), why="line not reached intraday")); continue
            used_keys.add(key)
            # expiry / holding window
            nxt = [e for e in expiries if e >= day]
            target = nxt[1] if (a.roll_on_expiry_day and nxt[0] == day) else nxt[0]
            cap = target
            if a.max_hold_days > 0:
                j = min(tdi[day] + a.max_hold_days, len(tdays) - 1)
                cap = min(cap, tdays[j])
            window = [d for d in tdays if day <= d <= cap] or [day]
            if cap > tdays[-1]:
                window += [d for d in pd.bdate_range(tdays[-1] + timedelta(1), cap).date]
            opt = "CE" if long else "PE"
            first_ts = m.index[min(ent.values())]
            lot = lot_for(sym, day)
            cap_dl = datetime.combine(window[-1], dtime(15, 30), IST)

            def run_all(s):
                rows = []
                for et, mi in ent.items():
                    sig_ts = m.index[mi]
                    if a.entry_fill == "next_open":
                        fi = int(np.searchsorted(s.index.values, utc64(sig_ts), "right"))
                        if fi >= len(s): continue
                        fill_px, fill_ts = float(s.open.iloc[fi]), s.index[fi]
                    else:
                        fi = int(np.searchsorted(s.index.values, utc64(sig_ts), "right")) - 1
                        if fi < 0 or s.index[fi].date() != day: continue
                        fill_px, fill_ts = float(s.close.iloc[fi]), s.index[fi]
                        fi += 1
                    if fill_px <= 0 or fi >= len(s) or fill_ts.date() != day: continue
                    dls = {"HIT": cap_dl}
                    for mode in ("10:00", "12:00", "15:30"):
                        hh, mm = map(int, mode.split(":"))
                        dl = datetime.combine(fill_ts.date(), dtime(hh, mm), IST)
                        if fill_ts >= dl:                  # time already passed -> next day
                            dl = datetime.combine(next_tday(fill_ts.date()), dtime(hh, mm), IST)
                        dls[mode] = min(dl, cap_dl)
                    base = dict(entry_type=et, stock=sym, dir=r.dir, signal_date=r.signal_date,
                                entry_date=day, ref=round(ref, 2), spot_signal_ts=sig_ts,
                                spot_entry=round(float(m.close.iloc[mi]), 2), option=opt,
                                expiry=target, lot_size=lot, entry_ts=fill_ts,
                                entry_px=round(fill_px * (1 + slip), 2))
                    rows += [{**base, **x} for x in simulate(s, fi, fill_px, dls, lot, slip, day)]
                return rows

            def evaluate(s):
                rows = run_all(s)
                return max(x["exit_ts"] for x in rows) if rows else None

            s, K, extra = locked_series(dh, SEC[sym], opt, window, expiries, target, first_ts, evaluate)
            if s.empty:
                skipped.append(dict(r._asdict(), why="no option data")); continue
            rows = run_all(s)
            if not rows:
                skipped.append(dict(r._asdict(), why="no option candle after entry")); continue
            for x in rows: x["strike"] = K
            trades += rows
        except DhanError as e:
            print(f"  skip {sym} {day}: {e}", flush=True)
            skipped.append(dict(r._asdict(), why=f"Dhan error: {str(e)[:200]}")); continue
        except BudgetExhausted:
            pending = len(cand) - k
            print(f"Request/time budget reached - {pending} candidate signals left for the next run", flush=True)
            break
        if k % 25 == 0:
            print(f"[{k + 1}/{len(cand)}] {day} {sym} {r.dir} api_calls={dh.used} cache_hits={dh.hits}", flush=True)

    tr = pd.DataFrame(trades)
    pd.DataFrame(skipped).to_csv(os.path.join(a.out, "skipped.csv"), index=False)
    if tr.empty: sys.exit("No trades simulated")
    tr.to_csv(os.path.join(a.out, "trades_all_variants.csv.gz"), index=False, compression="gzip")
    sm = summarize(tr)
    sm.to_csv(os.path.join(a.out, "summary_by_variant.csv"), index=False)
    md = [f"# SWG options backtest {start} -> {end}",
          f"Dhan API calls this run: {dh.used} (cache hits {dh.hits})" + (f" - INCOMPLETE, {pending} signals pending, re-run to resume" if pending else ""),
          f"Signals: {len(sigs)}, entered setups: {tr.groupby('entry_type').stock.count().div(len(SL_LIST)*len(TP_LIST)*len(EXIT_MODES)).astype(int).to_dict()}",
          "", "## Top 25 variants by net P&L", sm.head(25).to_markdown(index=False),
          "", "## Best variant per entry type",
          sm.groupby("entry_type").head(1).to_markdown(index=False)]
    open(os.path.join(a.out, "summary.md"), "w").write("\n".join(md))
    print("\n".join(md))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        open(os.environ["GITHUB_STEP_SUMMARY"], "a").write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
