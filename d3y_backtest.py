"""d3y_backtest.py - 3-year intraday option backtest (Jan 2023 - Sep 2026) with Yahoo + DhanHQ. Self-contained.

  python d3y_backtest.py check      test Dhan access (master file, 1 equity call, 1 rolling-option call) - run this first
  python d3y_backtest.py run        full backtest; resumable; stops by itself before the time budget; run again to continue
  python d3y_backtest.py summary    rebuild the summary tables from saved results (no API calls)

How it keeps Dhan requests low
  1. Yahoo daily candles (no Dhan) -> signal days (your pattern) where the NEXT day's daily candle touches the line.
  2. Dhan 1-minute STOCK candles only for those stock/days; one request covers up to 85 days of one stock.
  3. Dhan rolling-option 1-minute candles (ATM and neighbours) only for stock/days that produced an entry;
     one request covers up to 30 days of one stock and one side (CE for LONG, PE for SHORT); all variants share it.
  4. Every finished piece is saved; re-running skips it. Calls are paced under Dhan's limit (5/second) with back-off.

Entry types (per stock/day, direction from the daily signal, line = reference line):
  ALL              first minute the line is touched (any time up to ENTRY_LAST)
  OPEN_0915        line touched in the very first minute (09:15)
  FROM_0920_4C     first minute from 09:20 where the 4 previous candles stayed on the wrong side of the line
                   (LONG: highs below, SHORT: lows above) and this minute closes beyond it
  RECROSS_0920_4C  same as above but the line had ALREADY been touched before those 4 candles (second touch);
                   first_touch time is saved with every row
Exits: stop SL 10/20 %, target 20..200 % on the option price, forced exit at 10:00, 12:00 or 15:30 same day.
Capital per trade: Rs 2,00,000 for SL10, Rs 1,00,000 for SL20 (lots = cap // (price x lot size)).
"""
import os, sys, io, json, time, gzip, glob
import requests, numpy as np, pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
START, END = "2023-01-01", "2026-09-30"
SLS = [10, 20]
TPS = [20, 30, 40, 60, 80, 100, 120, 140, 200]
EXITS = ["10:00", "12:00", "15:30"]
CAPS = {10: 200000, 20: 100000}
ENTRY_LAST = "15:00"                                        # no entries after this time
OFFSETS = [int(x) for x in os.environ.get("OFFSETS", "0,1,-1").split(",")]    # ATM and neighbours (Dhan allows -3..+3 for stocks)
GAP_S = float(os.environ.get("DHAN_GAP", "0.35"))           # seconds between Dhan calls (limit is 5/second)
BUDGET_MIN = float(os.environ.get("BUDGET_MIN", "300"))     # stop politely after this many minutes
OUT = os.environ.get("D3Y_OUT", "d3y_results")
BASE = "https://api.dhan.co/v2"
MASTER = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
T0 = time.time()

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
    if h == l: return False
    b = abs(c - o)
    return b / (h - l) < .45 and max(h - max(o, c), min(o, c) - l) >= 2 * b


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
    raw = yf.download([s + ".NS" for s in UNIVERSE], start="2022-06-01", end=end, group_by="ticker",
                      auto_adjust=False, progress=False, threads=True)
    rows, nst = [], 0
    for s in UNIVERSE:
        try: d = raw[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except KeyError: continue
        if len(d) < 60: continue
        nst += 1
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        o, h, l, c = (d[k].values for k in ("Open", "High", "Low", "Close"))
        rng, body = h - l, np.abs(c - o)
        wick = np.maximum(h - np.maximum(o, c), np.minimum(o, c) - l)
        shp = (rng > 0) & (body < .45 * rng) & (wick >= 2 * body)
        for k in np.where(shp)[0]:
            if k < 40 or k + 1 >= len(d): continue
            T = d.index[k + 1]
            if not (pd.Timestamp(START) <= T <= pd.Timestamp(END)): continue
            sub = d.iloc[:k + 1]
            for long in (True, False):
                r = setup(sub, long)
                if not r: continue
                ref, nx = float(r[0]), d.iloc[k + 1]
                if (nx.High >= ref) if long else (nx.Low <= ref):
                    rows.append(dict(stock=s, direction="LONG" if long else "SHORT", ref=round(ref, 2),
                                     signal_date=str(d.index[k].date()), date=str(T.date()), yahoo_close=float(nx.Close)))
    print(f"Yahoo: {nst} stocks, {len(rows)} candidate stock-days (signal day before, line touched on the day)", flush=True)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ step 2: entries from Dhan stock minutes
def hm(t): return f"{t:%H:%M}"


def find_events(u, ref, long):
    """u = one day of 1-minute stock candles. -> {entry type: (entry minute, first touch minute)}"""
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
        if not ((h[k - 4:k] < ref).all() if long else (l[k - 4:k] > ref).all()): continue      # 4 previous candles on the wrong side
        if not (c[k] >= ref if long else c[k] <= ref): continue                                 # this minute closes beyond the line
        ev.setdefault("FROM_0920_4C", (idx[k], tc))
        if tc < idx[k - 4]: ev.setdefault("RECROSS_0920_4C", (idx[k], tc))                     # touched before those 4 candles = second touch
        if "RECROSS_0920_4C" in ev: break
    return ev


def windows(dates, span):
    out = []
    for d in sorted(dates):
        if out and (d - out[-1][0]).days < span: out[-1][1] = d
        else: out.append([d, d])
    return out


def load_state():
    p = f"{OUT}/state.json"
    s = json.load(open(p)) if os.path.exists(p) else {}
    s.setdefault("eq_done", []); s.setdefault("opt_done", [])
    return s


def save_state(s): json.dump(s, open(f"{OUT}/state.json", "w"))


def step_events(dh, cand, mst, st):
    ep = f"{OUT}/events.csv"
    ev = pd.read_csv(ep).to_dict("records") if os.path.exists(ep) else []
    todo = 0
    for s, g in cand.groupby("stock"):
        if s not in mst: print(f"{s}: not in Dhan stock-option list - skipped", flush=True); continue
        g = g.copy(); g["d"] = pd.to_datetime(g["date"]).dt.date
        for d0, d1 in windows(g.d.tolist(), 85):
            key = f"{s}|{d0}"
            if key in st["eq_done"]: continue
            u_all = eq_minute(dh, mst[s][0], d0, d1)
            n_ev = 0
            if u_all is not None:
                for r in g[(g.d >= d0) & (g.d <= d1)].itertuples():
                    u = u_all[u_all.index.date == r.d]
                    if u.empty: continue
                    ref, ratio = float(r.ref), float(u.c.iloc[-1]) / float(r.yahoo_close)
                    if abs(ratio - 1) > .2: ref *= ratio                       # split/bonus: Yahoo prices adjusted, Dhan raw
                    for typ, (m, ft) in find_events(u, ref, r.direction == "LONG").items():
                        ev.append(dict(stock=s, direction=r.direction, ref=round(ref, 2), date=str(r.d), type=typ,
                                       entry_minute=hm(m), first_touch=hm(ft), stock_price=float(u.c[m]))); n_ev += 1
            st["eq_done"].append(key)
            pd.DataFrame(ev).to_csv(ep, index=False); save_state(st)
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


def step_options(dh, ev, mst, st):
    os.makedirs(f"{OUT}/parts", exist_ok=True)
    for (s, dr), g in ev.groupby(["stock", "direction"]):
        g = g.copy(); g["d"] = pd.to_datetime(g["date"]).dt.date
        for d0, d1 in windows(g.d.unique().tolist(), 30):
            key = f"{s}|{dr}|{d0}"
            if key in st["opt_done"]: continue
            sid, lot = mst[s]
            series = []
            for off in OFFSETS:
                x = rolling(dh, sid, d0, d1 + timedelta(days=1), dr, off)
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
                    te, K, entry = a.ts.iloc[0], float(a.strike.iloc[0]), float(a.c.iloc[0])
                    if not entry > 0: continue
                    ser = D[(D.strike == K) & (D.ts > te)].drop_duplicates("ts").sort_values("ts")
                    mins = ser.ts.dt.hour.values * 60 + ser.ts.dt.minute.values
                    for ex in EXITS:
                        lim = int(ex[:2]) * 60 + int(ex[3:])
                        if hm(te) >= ex: continue                             # entered after this square-off time
                        w = ser[mins <= lim]
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
                                rows.append((s, dr, e.type, e.date, e.first_touch, hm(te), K, round(entry, 2), ex, sl, tp, lots, round(cost),
                                             hm(xt), round(px, 2), why, round((px - entry) * qty), int(late), round(float(e.stock_price), 2)))
            if rows:
                cols = ["stock", "direction", "type", "date", "first_touch", "entry_time", "strike", "entry", "exit_rule", "sl", "tp", "lots",
                        "cost", "exit_time", "exit_price", "reason", "pnl", "thin_data", "stock_price"]
                pd.DataFrame(rows, columns=cols).to_csv(f"{OUT}/parts/{s}_{dr}_{d0}.csv.gz", index=False, compression="gzip")
            st["opt_done"].append(key); save_state(st)
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


def summary():
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    if not fs: print("No results yet"); return
    t = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    t["year"] = t.date.str[:4]
    key = ["type", "exit_rule", "sl", "tp"]
    a = t.groupby(key).apply(agg).reset_index()
    a.to_csv(f"{OUT}/summary_all.csv", index=False)
    a[a.trades >= 30].sort_values("roi_pct", ascending=False).head(60).to_csv(f"{OUT}/summary_top60_roi.csv", index=False)
    a[a.trades >= 30].sort_values("total_pnl", ascending=False).head(60).to_csv(f"{OUT}/summary_top60_pnl.csv", index=False)
    a.loc[a[a.trades >= 30].groupby("type").roi_pct.idxmax()].to_csv(f"{OUT}/summary_best_per_type.csv", index=False)
    t.groupby(["type", "year"]).apply(agg).reset_index().to_csv(f"{OUT}/summary_type_by_year.csv", index=False)
    print(f"{len(t):,} result rows from {len(fs)} files")
    print("\nBEST COMBINATION PER ENTRY TYPE (>=30 trades, by ROI):\n" + pd.read_csv(f"{OUT}/summary_best_per_type.csv").to_string(index=False))
    print("\nTOP 15 BY ROI:\n" + a[a.trades >= 30].sort_values("roi_pct", ascending=False).head(15).to_string(index=False))


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
    cp = f"{OUT}/candidates.csv"
    if os.path.exists(cp): cand = pd.read_csv(cp)
    else:
        cand = yahoo_candidates(); cand.to_csv(cp, index=False)
    print(f"Candidates: {len(cand)} stock-days", flush=True)
    dh = Dhan(); mst = load_master()
    try:
        ev = step_events(dh, cand, mst, st)
        print(f"Entry events: {len(ev)}", flush=True)
        if len(ev): step_options(dh, ev, mst, st)
        print("ALL STEPS FINISHED", flush=True)
    except Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        print(f"Dhan calls this run: {dh.n}", flush=True)
        summary()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": check()
        elif mode == "run": run()
        elif mode == "summary": summary()
        else: sys.exit("use: python d3y_backtest.py check | run | summary")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
