"""orb_backtest.py - ORB (opening range breakout, 09:15-09:30) strategy on ATM OPTIONS, Dhan 1-minute data, LONG (call) and SHORT (put) separate.

  python orb_backtest.py check                          test Dhan access + print the rules + universe coverage
  python orb_backtest.py run     [options]              full backtest (resumable - run again after a polite stop / Dhan's daily call limit)
  python orb_backtest.py summary [options]              rebuild every result file from the saved data (no API calls) - also use it to narrow --start / --end afterwards
  python orb_backtest.py rules   [options]              print the rules only

  options (each also works as an environment variable, ORB_<NAME>):
    --universe top10 | nifty50 | fno     which stocks (default fno = all F&O stocks).  top10 = the 10 heaviest NIFTY50 stocks, nifty50 = the 50 index stocks (lists below, edit them if the index changed)
    --symbols RELIANCE,SBIN,...          your own list (overrides --universe)
    --start 2025-01-01 --end 2026-10-30  entry-date range (default: last 3 years)
    --sls none,ORB,BRK,20,40,60          stop-losses: none | ORB | BRK | % of premium    (default adds the mixes ORB+20 ... BRK+60 = combined exits; --no-combine drops them)
    --tps 0,20,40,60                     targets, % of premium, 0 = none
    --exits 10:00,12:00,15:00,15:30      same-day time exits
    --vol-mult 1.5 --vol-n 10            volume filter: breakout candle volume >= vol-mult x average of the previous vol-n candles (0 = filter off)
    --sl-buffer 0                        % beyond the ORB / breakout-candle level before the stock stop counts as hit
    --cap 60000  --itm-max 3  --entry-last 15:20  --out DIR

THE STRATEGY (table "Core Strategy Mechanics", on 1-minute candles)   details in orb_rules.py
  ORB = High / Low of the 1-minute candles from 09:15 to 09:30.   Entry = first 1-minute candle (from 09:30) that CLOSES above the ORB high (LONG, buy ATM call) / below the ORB low (SHORT, buy ATM put),
  with strong volume.  One trade per stock per day, the first side that signals.  Option price = close of that minute (ATM; ITM-1..3 if the ATM series has no candle; next month's series on the expiry day).
EXITS, every combination of   stop-loss  x  target  x  time exit   is one variant; the first of them to hit closes the trade (the COMBINED exit):
  stop-loss  none | ORB (stock beyond the ORB low / high) | BRK (stock beyond the breakout candle's low / high) | fixed 20 / 40 / 60 % of the premium | ORB+20 ... BRK+60 (whichever comes first)
  target     none | 20 | 40 | 60 % of the premium
  time exit  10:00 | 12:00 | 15:00 | 15:30 (close of the last option candle up to that minute; a trade entered at / after it is skipped for that exit)
CAPITAL    at most Rs 60,000 per trade, whole lots.  Charges, taxes and slippage are not included.  Lot sizes are today's values for all years.

Dhan Data API = 100,000 calls a day: the stock candles cost ~13 calls per stock for 3 years, the options 1-3 calls per ENTRY.  A big universe x long range takes several days (just run again - progress is saved).
Results in orb_results_<universe>/ : SUMMARY.md, long/ and short/ (SUMMARY.md, summary.csv, matrix_*.csv, trades_all_variants.csv.gz, trades_best_variant.csv, entries.csv).
"""
import os, sys, io, json, glob, zlib, argparse
from collections import Counter
from datetime import date, timedelta


def _env(name, default=""):
    return os.environ.get("ORB_" + name) or default


# ---------------------------------------------------------------- universes (NSE symbols as Dhan uses them)
TOP10 = "HDFCBANK RELIANCE ICICIBANK INFY BHARTIARTL ITC LT TCS AXISBANK SBIN".split()           # the 10 heaviest NIFTY50 stocks
NIFTY50 = """ADANIENT ADANIPORTS APOLLOHOSP ASIANPAINT AXISBANK BAJAJ-AUTO BAJFINANCE BAJAJFINSV BEL BHARTIARTL CIPLA COALINDIA DRREDDY EICHERMOT ETERNAL GRASIM HCLTECH HDFCBANK HDFCLIFE
             HINDALCO HINDUNILVR ICICIBANK INDIGO INFY ITC JIOFIN JSWSTEEL KOTAKBANK LT M&M MARUTI MAXHEALTH NESTLEIND NTPC ONGC POWERGRID RELIANCE SBILIFE SBIN SHRIRAMFIN SUNPHARMA
             TATACONSUM TATASTEEL TCS TECHM TITAN TMPV TRENT ULTRACEMCO WIPRO""".split()


def parse_args(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("mode", nargs="?", default="")
    ap.add_argument("--universe", default=_env("UNIVERSE", "fno"), choices=["top10", "nifty50", "fno"])
    ap.add_argument("--symbols", default=_env("SYMBOLS"))
    ap.add_argument("--start", default=_env("START", str(date.today() - timedelta(days=3 * 365))))
    ap.add_argument("--end", default=_env("END", str(date.today())))
    ap.add_argument("--sls", default=_env("SLS", "none,ORB,BRK,20,40,60"))
    ap.add_argument("--no-combine", action="store_true", default=_env("NO_COMBINE") == "1")
    ap.add_argument("--tps", default=_env("TPS", "0,20,40,60"))
    ap.add_argument("--exits", default=_env("EXITS", "10:00,12:00,15:00,15:30"))
    ap.add_argument("--vol-mult", type=float, default=float(_env("VOL_MULT", "1.5")))
    ap.add_argument("--vol-n", type=int, default=int(_env("VOL_N", "10")))
    ap.add_argument("--sl-buffer", type=float, default=float(_env("SL_BUFFER", "0")))
    ap.add_argument("--cap", type=int, default=int(_env("CAP", "60000")))
    ap.add_argument("--itm-max", type=int, default=int(_env("ITM_MAX", "3")))
    ap.add_argument("--entry-last", default=_env("ENTRY_LAST", "15:20"))
    ap.add_argument("--out", default=_env("OUT"))
    return ap.parse_args(argv)


ARGS = parse_args(sys.argv[1:])
OUT = ARGS.out or f"orb_results_{ARGS.universe}"
os.environ["BPB_OUT"] = OUT                                                      # bpb_fno_backtest.checkpoint() saves this folder to the repo on GitHub Actions
import numpy as np, pandas as pd
import bpb_fno_backtest as B
import orb_rules as R

START, END = ARGS.start, ARGS.end
CAP = ARGS.cap
ITM_MAX = ARGS.itm_max
ENTRY_LAST = ARGS.entry_last
ENTRY_MIN = int(ENTRY_LAST[:2]) * 60 + int(ENTRY_LAST[3:5])
EXITS = [x.strip() for x in ARGS.exits.replace(" ", ",").split(",") if len(x.strip()) == 5 and x.strip()[2] == ":"]
TPS = [int(float(x)) for x in ARGS.tps.replace(" ", ",").split(",") if x.strip() != ""]
_sl_tokens = [x for x in ARGS.sls.replace(" ", ",").split(",") if x.strip() != ""]
SL_SPECS = []
for _t in _sl_tokens:
    _s = R.parse_sl(_t)
    if _s not in SL_SPECS: SL_SPECS.append(_s)
if not ARGS.no_combine and (any(k for k, f in SL_SPECS) and any(f for k, f in SL_SPECS)):
    for _k in [k for k in ("ORB", "BRK") if (k, 0) in SL_SPECS]:                 # the mixes: stock stop + fixed % stop, whichever comes first
        for _f in sorted({f for k, f in SL_SPECS if f}):
            if (_k, _f) not in SL_SPECS: SL_SPECS.append((_k, _f))
VARS = R.make_vars(EXITS, SL_SPECS, TPS)
COV_MIN = float(_env("COV_MIN", "0.9"))
OFFS_MAX, MAX_OFFS = int(_env("OFFS_MAX", "10")), int(_env("MAX_OFFS", "8"))
BATCH = int(_env("BATCH", "25"))                                                 # entries per option work group / parts file
MIN_TRADES = int(_env("MIN_TRADES", "30"))
TRADES_MAX = int(_env("TRADES_MAX", "2000000"))                                  # write every trade of every variant only up to this many rows, else the top variants
STRATS = ("ORB_LONG", "ORB_SHORT"); DIRNAME = {"ORB_LONG": "long", "ORB_SHORT": "short"}; DIRSTRAT = {"LONG": "ORB_LONG", "SHORT": "ORB_SHORT"}


def hm(t): return f"{t:%H:%M}"
def ekey(s, d, day, m): return f"{s}|{d}|{day}|{m}"


def universe(mst):
    if ARGS.symbols.strip(): u = [x.strip().upper() for x in ARGS.symbols.replace(",", " ").split() if x.strip()]
    elif ARGS.universe == "top10": u = list(TOP10)
    elif ARGS.universe == "nifty50": u = list(NIFTY50)
    else: u = list(B.FNO)
    seen = set(); u = [x for x in u if not (x in seen or seen.add(x))]
    miss = [x for x in u if mst is not None and x not in mst]
    if miss: print(f"not in Dhan's stock-option list - skipped ({len(miss)}): {miss}", flush=True)
    return [x for x in u if mst is None or x in mst]


# ---------------------------------------------------------------- rules text
def rule_dict():
    return dict(sls=[R.sl_label(s) for s in SL_SPECS], tps=TPS, exits=EXITS, cap=CAP, itm_max=ITM_MAX, entry_last=ENTRY_LAST, vol_mult=ARGS.vol_mult, vol_n=ARGS.vol_n, sl_buffer=ARGS.sl_buffer)


def rules_text():
    vol = f"breakout candle volume >= {ARGS.vol_mult:g} x the average of the previous {ARGS.vol_n} one-minute candles" if ARGS.vol_mult > 0 else "volume filter OFF"
    return (f"ORB.  ORB = High / Low of the 1-minute candles from 09:15 to 09:30.  LONG (ATM call): first 1-minute candle from 09:30 (to {ENTRY_LAST}) that CLOSES above the ORB high; SHORT (ATM put): "
            f"first one that CLOSES below the ORB low; volume filter: {vol}.  One trade per stock per day (first side to signal).  Option = ATM at the entry minute (ITM-1..{ITM_MAX} if the ATM series has no candle), "
            f"price = close of the entry minute.  Stop-loss ORB = stock beyond the ORB low (LONG) / high (SHORT); BRK = stock beyond the low (LONG) / high (SHORT) of the breakout candle"
            f"{f' (+{ARGS.sl_buffer:g}% buffer)' if ARGS.sl_buffer else ''}; fixed % = % of the option premium; mixes (ORB+20 ...) close at whichever hits first.")


def print_rules():
    print(rules_text(), flush=True)
    print(f"Grid: stop-loss {[R.sl_label(s) for s in SL_SPECS]} x target {[R.tp_label(t) for t in TPS]} x time exit {EXITS} = {len(VARS)} variants per direction; {START} .. {END}; "
          f"universe {ARGS.symbols or ARGS.universe}; cap Rs {CAP}", flush=True)


# ---------------------------------------------------------------- expiry calendar + Dhan client (next month's series on the monthly expiry day)
def last_dow(y, m, dow):
    d = date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)
    while d.weekday() != dow: d -= timedelta(days=1)
    return d


def expiry_calc(d):
    """Monthly stock-option expiry on or after d: last Thursday up to Aug 2025, last Tuesday from Sep 2025."""
    y, m = d.year, d.month
    for _ in range(14):
        e = last_dow(y, m, 3 if (y, m) < (2025, 9) else 1)
        if e >= d: return e
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def _has_data(j):
    d = (j.get("data") or {}) if isinstance(j, dict) else {}
    return any(isinstance(v, dict) and any(isinstance(x, list) and len(x) for x in v.values()) for v in d.values())


class StrictDhan(B.Dhan):
    """A FAILED option request is never stored as 'no option candles' (it stops politely and is retried next run).  An entry on the monthly expiry day asks for the next month's series first."""
    def post(self, path, body):
        if "rollingoption" in path:
            try:
                fd = date.fromisoformat(str(body.get("fromDate"))[:10])
                if expiry_calc(fd) == fd:
                    j2 = super().post(path, dict(body, expiryCode=2))
                    if j2 is not None and _has_data(j2): return j2
            except ValueError:
                pass
        j = super().post(path, body)
        if j is None and "rollingoption" in path:
            raise B.Stop(f"Dhan refused an option request ({body.get('fromDate')} .. {body.get('toDate')}, {body.get('strike')}) - see the 'Dhan says' line above; nothing was stored for it")
        return j


def eq_minute_vol(dh, sid, d0, d1):
    """1-minute stock candles (o h l c v) from d0 to d1, <= 90 days per request."""
    j = dh.post("/charts/intraday", {"securityId": str(sid), "exchangeSegment": "NSE_EQ", "instrument": "EQUITY", "interval": "1",
                                     "oi": False, "fromDate": f"{d0} 09:15:00", "toDate": f"{d1} 15:30:00"})
    if j is None: return None
    fr = B.frame(j.get("data", j) if isinstance(j.get("data", None), dict) else j, extra=("volume",))
    if fr is None:
        print(f"[stock candles {sid} {d0}..{d1}] Dhan answered but sent no candles: {str(j)[:300]}", flush=True)
        return pd.DataFrame(columns=["o", "h", "l", "c", "v"], index=pd.DatetimeIndex([]))
    if "volume" in fr.columns: fr = fr.rename(columns={"volume": "v"})
    else: fr["v"] = 0.0
    return fr


# ---------------------------------------------------------------- state
def load_state():
    p = f"{OUT}/state.json"
    s = json.load(open(p)) if os.path.exists(p) else {}
    s.setdefault("done", []); s["done"] = set(s["done"])
    return s


def save_state(s):
    tmp = f"{OUT}/state.json.tmp"
    json.dump({**s, "done": sorted(s["done"])}, open(tmp, "w")); os.replace(tmp, f"{OUT}/state.json")


LAST_SAVE = [0.0]


def flush(st, ev=None, force=False, every=10):
    import time
    if not force and time.time() - LAST_SAVE[0] < every: return
    if ev:
        pd.DataFrame(ev).drop_duplicates(["stock", "date"]).to_csv(f"{OUT}/events.csv", index=False)
    save_state(st); LAST_SAVE[0] = time.time()


def spans(d0, d1, n):
    out, a = [], d0
    while a <= d1:
        b = min(a + timedelta(days=n - 1), d1); out.append((a, b)); a = b + timedelta(days=1)
    return out


# ---------------------------------------------------------------- step 1: stock candles -> one entry event per stock and day
def step_events(dh, mst, uni, st):
    ep = f"{OUT}/events.csv"
    ev = pd.read_csv(ep, dtype={"entry_minute": str, "orb_sl_time": str, "brk_sl_time": str}).to_dict("records") if os.path.exists(ep) else []
    t0, t1 = date.fromisoformat(START), date.fromisoformat(END)
    tasks, expected = [], 0
    for s in uni:
        for d0, d1 in spans(t0, t1, B.EQ_SPAN):
            expected += 1; key = f"EQ|ORB|{s}|{d0}|{d1}"
            if key not in st["done"]: tasks.append((s, d0, d1, key))
    print(f"Dhan stock-candle work: {len(tasks)} request groups to do ({expected - len(tasks)} already done)", flush=True)

    def work(t):
        s, d0, d1, key = t
        u_all = eq_minute_vol(dh, mst[s][0], d0, d1)
        if u_all is None: return None
        if u_all.empty: return [], 0
        mm = minutes_of(u_all.index)
        u_all = u_all[(mm >= R.ORB_START) & (mm < 15 * 60 + 30)]
        out, nd = [], 0
        for dday, u in u_all.groupby(u_all.index.date):
            nd += 1
            rng = R.orb_range(u)
            if rng is None: continue
            e = R.find_entry(u, rng[0], rng[1], R.ORB_END, ENTRY_MIN, ARGS.vol_mult, ARGS.vol_n)
            if e is None: continue
            long = e["direction"] == "LONG"
            after = u.iloc[e["pos"] + 1:]
            row = dict(stock=s, direction=e["direction"], date=str(dday), entry_minute=hm(e["minute"]), stock_price=round(e["close"], 2), orb_hi=round(rng[0], 2), orb_lo=round(rng[1], 2),
                       brk_level=round(e["brk_level"], 2), vol=e["vol"], vol_ref=e["vol_ref"])
            for name, level in (("orb", rng[1] if long else rng[0]), ("brk", e["brk_level"])):
                r = R.stock_stop(after, long, level, ARGS.sl_buffer)
                row[f"{name}_sl_time"] = hm(after.index[r[0]]) if r else ""
                row[f"{name}_sl_gap"] = int(r[1]) if r else 0
            out.append(row)
        return out, nd

    fails = [0]

    def handle(t, res):
        s, d0, d1, key = t
        if res is None:
            fails[0] += 1; print(f"stock candles {s} {d0}..{d1}: FAILED (retried on the next run), calls {dh.n}", flush=True); return
        out, nd = res
        ev.extend(out); st["done"].add(key); flush(st, ev); B.checkpoint()
        print(f"stock candles {s} {d0}..{d1}: minute data on {nd} days, {len(out)} ORB entries, calls {dh.n}", flush=True)

    B.FLUSHER[0] = lambda: flush(st, ev, force=True)
    try: B.stream(tasks, work, handle)
    finally: flush(st, ev, force=True)
    if fails[0]: print(f"WARNING: {fails[0]} stock-candle request(s) failed - run again to retry them.", flush=True)
    return pd.DataFrame(ev).drop_duplicates(["stock", "date"]).reset_index(drop=True) if ev else pd.DataFrame()


def minutes_of(idx):
    return idx.hour.values * 60 + idx.minute.values


# ---------------------------------------------------------------- step 2: option candles -> one compact record per entry
def option_record(dh, mst, e):
    """ATM first, ITM-1 .. ITM-n if the ATM series has no candle at the entry minute; the strike is locked at entry and followed through the day.  -> (record or None, skip reason or None)"""
    s, dr, d, em = e["stock"], e["direction"], e["date"], e["entry_minute"]
    sid, lot = mst[s]; d0 = date.fromisoformat(d); wins = [(d0, d0 + timedelta(days=1))]
    sgn = 1 if dr == "SHORT" else -1; cache = {}

    def ser(off):
        if off not in cache:
            parts = []
            for a, b in wins:
                x = B.rolling(dh, sid, a, b, dr, off)
                if x is not None and len(x): parts.append(x)
            x = pd.concat(parts) if parts else None
            if x is not None and "strike" in x: x = x[~x.index.duplicated()].sort_index(); x = x[x.index.date <= d0]
            cache[off] = x if (x is not None and "strike" in x and len(x)) else None
        return cache[off]

    m = pd.Timestamp(f"{d} {em}"); got = None; why = f"no ATM / ITM-1..ITM-{ITM_MAX} candle at the entry minute"
    for off in [k * sgn for k in range(ITM_MAX + 1)]:
        x = ser(off)
        if x is None: continue
        a = x[x.index >= m]
        if a.empty or (a.index[0] - m) > pd.Timedelta(minutes=3): continue
        te, K, entry = a.index[0], float(a.strike.iloc[0]), float(a.c.iloc[0])
        if not entry > 0: why = "zero price"; continue
        got = (off, te, K, entry); break
    if got is None:
        return None, (why if any(v is not None for v in cache.values()) else "Dhan returned no option candles for this day")
    off, te, K, entry = got
    base_off = 0 if cache.get(0) is not None else off
    bx = cache[base_off]; step = B_infer_step(bx.strike.values); after = bx[bx.index > te]
    cnt = Counter()
    if step > 0 and len(after):
        n = np.rint((K - (after.strike.values - base_off * step)) / step).astype(int)           # which ATM+n series holds the locked strike at each minute
        for v, k in zip(*np.unique(n, return_counts=True)):
            if v != 0 and abs(v) <= OFFS_MAX: cnt[int(v)] += int(k)
    for v, _ in cnt.most_common(MAX_OFFS): ser(v)
    big = pd.concat([x for x in cache.values() if x is not None])
    S = big[((big.strike - K).abs() < 1e-6).values & (big.index > te)]
    S = S[~S.index.duplicated()].sort_index()
    if S.empty or len(after) == 0: return None, "no option candles after the entry"
    stops = {}
    for name, key in (("ORB", "orb"), ("BRK", "brk")):
        t = e.get(f"{key}_sl_time")
        if isinstance(t, str) and len(t) == 5: stops[name] = (pd.Timestamp(f"{d} {t}"), bool(int(e.get(f"{key}_sl_gap") or 0)))
    r = R.make_record(S, te, entry, lot, K, expiry_calc(d0), min(1.0, len(S) / len(after)), EXITS, stops)
    r.update(ekey=ekey(s, dr, d, em), stock=s, direction=dr, date=d, entry_minute=em, strike_offset=off)
    return r, None


def B_infer_step(strikes):
    u = np.unique(np.round(np.asarray(strikes, float), 4)); d = np.diff(u); d = d[d > 1e-9]
    return float(d.min()) if len(d) else 0.0


def step_options(dh, ev, mst, st):
    os.makedirs(f"{OUT}/parts", exist_ok=True); os.makedirs(f"{OUT}/skipped", exist_ok=True)
    ev = ev[(ev["date"] >= START) & (ev["date"] <= END)].sort_values(["stock", "date"])
    tasks, expected = [], 0
    for s, g in ev.groupby("stock"):
        rows = g.to_dict("records")
        for i in range(0, len(rows), BATCH):
            b = rows[i:i + BATCH]; sig = zlib.crc32(json.dumps([(r["date"], r["entry_minute"], r["direction"]) for r in b]).encode())
            key = f"OPT|ORB|{s}|{b[0]['date']}|{b[-1]['date']}|{sig:08x}"; expected += 1
            if key not in st["done"]: tasks.append((s, b, key))
    print(f"Dhan option work: {len(tasks)} request groups to do ({expected - len(tasks)} already done), {BATCH} entries each", flush=True)

    def work(t):
        s, b, key = t; recs, skips = [], []
        for e in b:
            r, why = option_record(dh, mst, e)
            if r is not None: recs.append(r)
            else: skips.append((ekey(s, e["direction"], e["date"], e["entry_minute"]), why))
        fn = f"{s}_{b[0]['date']}_{b[-1]['date']}"
        if recs: pd.DataFrame(recs).to_csv(f"{OUT}/parts/{fn}.csv.gz", index=False, compression={"method": "gzip", "compresslevel": 1})
        if skips: pd.DataFrame(skips, columns=["ekey", "reason"]).to_csv(f"{OUT}/skipped/{fn}.csv", index=False)
        return len(recs), len(skips)

    def handle(t, res):
        s, b, key = t
        st["done"].add(key); flush(st); B.checkpoint()
        print(f"options {s} {b[0]['date']}..{b[-1]['date']}: {len(b)} entries, {res[0]} with option data, {res[1]} skipped, calls so far {dh.n}", flush=True)

    B.FLUSHER[0] = lambda: flush(st, force=True)
    try: B.stream(tasks, work, handle)
    finally: flush(st, force=True)


# ---------------------------------------------------------------- step 3: simulate every exit variant
def load_records():
    fs = sorted(glob.glob(f"{OUT}/parts/*.csv.gz"))
    if not fs: return pd.DataFrame()
    return pd.concat([pd.read_csv(f, dtype={"entry_time": str, "entry_minute": str}) for f in fs], ignore_index=True).drop_duplicates("ekey")


def load_skips():
    fs = sorted(glob.glob(f"{OUT}/skipped/*.csv"))
    return pd.concat([pd.read_csv(f) for f in fs], ignore_index=True).drop_duplicates("ekey") if fs else pd.DataFrame(columns=["ekey", "reason"])


class Sim:
    """All trades of one direction: arrays (entries x variants)."""
    def __init__(self, Rr):
        n, V = len(Rr), len(VARS)
        self.R = Rr.sort_values(["date", "entry_time", "stock"]).reset_index(drop=True)
        self.pnl = np.full((n, V), np.nan); self.px = np.zeros((n, V)); self.dm = np.zeros((n, V), np.int32)
        self.code = np.zeros((n, V), np.int8); self.late = np.zeros((n, V), np.int8)
        self.lots = np.zeros(n, np.int64); self.cost = np.zeros(n)
        for i, r in enumerate(self.R.itertuples()):
            lots = int(CAP // (r.entry_price * r.lot)); self.lots[i] = lots
            if lots < 1: continue
            qty = lots * r.lot; self.cost[i] = r.entry_price * qty
            ls = np.array(json.loads(r.ls), float).reshape(-1, 3); hs = np.array(json.loads(r.hs), float).reshape(-1, 3)
            res = R.simulate_one(r.entry_price, ls, hs, json.loads(r.tx), json.loads(r.usl), VARS)
            for v, (dm, px, code, late) in enumerate(res):
                if not code: continue
                self.px[i, v], self.dm[i, v], self.code[i, v], self.late[i, v] = px, dm, code, late
                self.pnl[i, v] = (px - r.entry_price) * qty

    def aggregate(self, strat):
        ok = self.code > 0; p = np.where(ok, self.pnl, 0.0); cost = np.where(ok, self.cost[:, None], 0.0)
        n = ok.sum(0); wins = (p > 0).sum(0); cap = cost.sum(0); tot = p.sum(0)
        gp = np.where(p > 0, p, 0).sum(0); gl = -np.where(p < 0, p, 0).sum(0)
        rows = []
        for v, (ex, spec, tp) in enumerate(VARS):
            if n[v] == 0: continue
            cd = self.code[:, v]
            rows.append(dict(strategy=strat, exit_rule=ex, sl=R.sl_label(spec), tp=tp, trades=int(n[v]), wins=int(wins[v]), win_pct=round(wins[v] / n[v] * 100, 2), total_pnl=int(round(tot[v])),
                             capital_used=int(round(cap[v])), roi_pct=round(tot[v] / cap[v] * 100, 2) if cap[v] else np.nan, profit_factor=round(gp[v] / gl[v], 2) if gl[v] > 0 else np.nan,
                             avg_pnl=int(round(tot[v] / n[v])), max_drawdown=int(round(R.max_drawdown(p[ok[:, v], v]))),
                             stop_pct_exits=int(np.isin(cd, (1, 2)).sum()), orb_stop_exits=int((cd == 7).sum()), brk_stop_exits=int((cd == 8).sum()),
                             target_exits=int(np.isin(cd, (3, 4)).sum()), time_exits=int((cd == 5).sum()), thin_exits=int(self.late[:, v].sum())))
        return rows

    def trades(self, vs, strat):
        out = []
        te = pd.to_datetime(self.R.date + " " + self.R.entry_time)
        for v in vs:
            m = self.code[:, v] > 0
            if not m.any(): continue
            Rr = self.R[m]; ex, spec, tp = VARS[v]; xt = te[m] + pd.to_timedelta(self.dm[m, v].astype(np.int64), unit="m")
            out.append(pd.DataFrame(dict(
                strategy=strat, exit_rule=ex, sl=R.sl_label(spec), tp=tp, stock=Rr.stock.values, direction=Rr.direction.values, entry_date=Rr.date.values, entry_time=Rr.entry_time.values,
                strike=Rr.strike.values, entry_price=Rr.entry_price.values, lots=self.lots[m], cost=self.cost[m].round(), exit_time=xt.dt.strftime("%H:%M").values,
                exit_price=self.px[m, v].round(2), reason=[R.REASON[x] for x in self.code[m, v]], pnl=self.pnl[m, v].round(),
                ret_pct=((self.px[m, v] / Rr.entry_price.values - 1) * 100).round(2), thin_exit=self.late[m, v])))
        return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


# ---------------------------------------------------------------- result files
def md(df, index=False):
    try: return df.to_markdown(index=index)
    except Exception: return df.to_string(index=index)


def tp_cols(P):
    order = [t for t in TPS if t] + ([0] if 0 in TPS else [])
    P = P.reindex(columns=[t for t in order if t in P.columns]); P.columns = [R.tp_label(t) for t in P.columns]
    return P


def matrices(S, metric):
    P = S.pivot_table(index=["exit_rule", "sl"], columns="tp", values=metric, aggfunc="first")
    sl_order = [R.sl_label(s) for s in SL_SPECS]
    P = tp_cols(P).reset_index(); P["_o"] = P.sl.map({s: i for i, s in enumerate(sl_order)}); P["_e"] = P.exit_rule.map({e: i for i, e in enumerate(EXITS)})
    return P.sort_values(["_e", "_o"]).drop(columns=["_o", "_e"])


def summary():
    recs = load_records(); skips = load_skips(); ep = f"{OUT}/events.csv"
    if recs.empty or not os.path.exists(ep): print("No saved option data yet - run first.", flush=True); return
    ev = pd.read_csv(ep, dtype={"entry_minute": str, "orb_sl_time": str, "brk_sl_time": str})
    ev = ev[(ev.date >= START) & (ev.date <= END)]
    ev["ekey"] = ev.stock + "|" + ev.direction + "|" + ev.date + "|" + ev.entry_minute
    if "date" in recs.columns: recs = recs[(recs.date >= START) & (recs.date <= END)]
    n_all = len(recs); thin_cov = int((recs["cov"] < COV_MIN).sum()); recs = recs[recs["cov"] >= COV_MIN]
    E = ev.merge(recs[["ekey", "strike", "entry_price", "lot", "cov", "strike_offset"]], on="ekey", how="left")
    prog = f"{len(ev)} ORB entries in {START}..{END}, {n_all} with option data ({thin_cov} dropped for option-candle coverage < {COV_MIN:.0%}), {len(skips[skips.ekey.isin(ev.ekey)])} skipped"
    open(f"{OUT}/PROGRESS.txt", "w").write(prog + "\n")
    cols = ["strategy", "exit_rule", "sl", "tp", "trades", "win_pct", "total_pnl", "roi_pct", "profit_factor", "max_drawdown"]
    allS, best = [], []
    for strat in STRATS:
        dr = "LONG" if strat == "ORB_LONG" else "SHORT"
        G = recs[recs.direction == dr]
        if G.empty: continue
        sim = Sim(G); rows = sim.aggregate(strat)
        if not rows: continue
        S = pd.DataFrame(rows); S["tp_rule"] = S.tp.map(R.tp_label); S["variant"] = S.strategy + " | exit " + S.exit_rule + " | " + S.sl + " | " + S.tp_rule
        allS.append(S)
        d = f"{OUT}/{DIRNAME[strat]}"; os.makedirs(d, exist_ok=True)
        S.to_csv(f"{d}/summary.csv", index=False)
        for metric in ("total_pnl", "roi_pct", "win_pct", "profit_factor"): matrices(S, metric).to_csv(f"{d}/matrix_{metric}.csv", index=False)
        good = S[S.trades >= MIN_TRADES]; base = good if len(good) else S
        bp = base.sort_values(["total_pnl", "trades"], ascending=False).iloc[0]; best.append(bp)
        key = {VARS[v]: v for v in range(len(VARS))}
        tot_rows = int((sim.code > 0).sum())
        if tot_rows <= TRADES_MAX or os.environ.get("ORB_TRADES_ALL") == "1":
            vs = list(range(len(VARS))); note = "every trade of every variant"
        else:
            top = base.sort_values("total_pnl", ascending=False).head(15).variant.tolist()
            vs = [v for v in range(len(VARS)) if f"{strat} | exit {VARS[v][0]} | {R.sl_label(VARS[v][1])} | {R.tp_label(VARS[v][2])}" in top]
            note = f"only the 15 best variants by PnL ({tot_rows} rows for all variants is too big; set ORB_TRADES_ALL=1 to write everything)"
        T = sim.trades(vs, strat); T.to_csv(f"{d}/trades_all_variants.csv.gz", index=False)
        B_ = T[(T.exit_rule == bp.exit_rule) & (T.sl == bp.sl) & (T.tp == bp.tp)] if len(T) else T
        B_.to_csv(f"{d}/trades_best_variant.csv", index=False)
        E[E.direction == dr].sort_values(["date", "entry_minute", "stock"]).drop(columns=["ekey"]).to_csv(f"{d}/entries.csv", index=False)
        L = [f"# ORB - {DIRNAME[strat].upper()} ({'ATM call' if dr == 'LONG' else 'ATM put'}) - stop-loss x target x time-exit grid", "", f"**Status:** {prog}", "",
             f"**Period (entry dates):** {START} to {END}  |  **Stocks:** {ARGS.symbols or ARGS.universe} ({G.stock.nunique()} with trades)  |  **Capital per trade:** up to Rs {CAP:,} (whole lots)", "",
             "## Rule", "", rules_text(), "",
             f"**Grid:** stop-loss {', '.join(R.sl_label(s) for s in SL_SPECS)} x target {', '.join(R.tp_label(t) for t in TPS)} x time exit {', '.join(EXITS)} = {len(VARS)} variants. "
             "Percentages are % of the option premium; ORB / BRK are stock-price stops. A trade entered at / after a time exit is skipped for that exit, so the early exits have fewer trades.", ""]
        if "strike_offset" in E.columns:
            vc = E[(E.direction == dr) & E.entry_price.notna()].strike_offset.value_counts().sort_index()
            L += ["## Strike used", "", "strike_offset 0 = ATM, +-n = ITM-n (the ATM series had no candle at the entry minute): " + ", ".join(f"{int(k)}: {int(v)}" for k, v in vc.items()), ""]
        for ex in EXITS:
            gx = S[S.exit_rule == ex]
            if gx.empty: continue
            L += [f"## Exit {ex}", ""]
            for metric, title in (("total_pnl", "Total PnL (Rs)"), ("roi_pct", "ROI % on capital used"), ("win_pct", "Win %")):
                M = matrices(gx, metric).drop(columns=["exit_rule"])
                L += [f"**{title}** (rows stop-loss, columns target) - trades per variant: {int(gx.trades.min())}-{int(gx.trades.max())}", "", md(M), ""]
        L += ["## Best variant by total PnL", "", md(pd.DataFrame([bp])[cols]), "",
              f"## Top 10 variants by ROI (at least {MIN_TRADES} trades)", "", md(base.sort_values("roi_pct", ascending=False).head(10)[cols]), "",
              f"## Top 10 variants by total PnL (at least {MIN_TRADES} trades)", "", md(base.sort_values("total_pnl", ascending=False).head(10)[cols]), "",
              "## Files in this folder", "", f"`trades_all_variants.csv.gz` ({len(T)} rows: {note}), `trades_best_variant.csv` ({len(B_)} trades), `entries.csv` (one row per ORB entry), `summary.csv`, `matrix_*.csv`.", "",
              "The best variant is the best of many, chosen after seeing the results, so it is optimistic: look at its neighbours and at the other exits. Charges, taxes and slippage are not included. "
              "Lot sizes are today's values for all years. The stock list is today's list. Past results do not promise future results.", ""]
        open(f"{d}/SUMMARY.md", "w").write("\n".join(L))
    if not allS: print("No variant has trades yet.", flush=True); return
    pd.concat(allS).to_csv(f"{OUT}/summary.csv", index=False)
    L = ["# ORB (LONG call + SHORT put) - stop-loss x target x time-exit grid", "", f"**Status:** {prog}", "", f"**Period (entry dates):** {START} to {END}  |  **Stocks:** {ARGS.symbols or ARGS.universe}", "",
         "## Rules", "", rules_text(), "", "LONG and SHORT are reported separately: `long/` and `short/`.", "",
         "## Best variant by total PnL (per direction)", "", md(pd.DataFrame(best)[cols]), ""]
    open(f"{OUT}/SUMMARY.md", "w").write("\n".join(L)); print("\n".join(L[:12]), flush=True)


# ---------------------------------------------------------------- modes
def check():
    dh = B.Dhan(); mst = B.load_master()
    print(f"Instrument list OK: {len(mst)} stocks with options. RELIANCE ->", mst.get("RELIANCE"), flush=True)
    uni = universe(mst); print(f"Universe '{ARGS.symbols or ARGS.universe}': {len(uni)} stocks usable", flush=True)
    sid = mst["RELIANCE"][0]; d1 = date.today(); d0 = d1 - timedelta(days=10)
    u = eq_minute_vol(dh, sid, d0, d1)
    print("Stock minute call:", "no data" if u is None else f"{len(u)} candles, {u.index[0]} .. {u.index[-1]}, volume column sum {u.v.sum():.0f}")
    x = B.rolling(dh, sid, d0, d1, "LONG", 0)
    print("Rolling option call:", "no data" if x is None else f"{len(x)} candles, columns {list(x.columns)}")
    B.print_stats(dh)


def run():
    os.makedirs(OUT, exist_ok=True)
    rp = f"{OUT}/rule.json"; rule = json.loads(json.dumps(rule_dict()))
    if os.path.exists(rp):
        old = json.load(open(rp))
        if old != rule:
            sys.exit("STOP - the saved data in " + OUT + " was made with other settings:\n  saved: " + json.dumps(old) + "\n  now:   " + json.dumps(rule) + "\nUse the same settings or another --out folder.")
    json.dump(rule, open(rp, "w"), indent=1)
    print_rules()
    st = load_state(); dh = StrictDhan(); mst = B.load_master(); uni = universe(mst)
    try:
        ev = step_events(dh, mst, uni, st)
        ev = ev[(ev["date"] >= START) & (ev["date"] <= END) & ev.stock.isin(uni)] if len(ev) else ev
        print(f"ORB entries (09:30-{ENTRY_LAST}): {len(ev)}", flush=True)
        if not len(ev): print("NO ENTRIES - if the lines above show FAILED / 'Dhan says', the stock candles were not downloaded (token / Data API).", flush=True)
        else: step_options(dh, ev, mst, st)
        print("ALL STEPS FINISHED", flush=True)
    except B.Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        B.print_stats(dh); summary(); B.checkpoint(True)


if __name__ == "__main__":
    mode = ARGS.mode
    try:
        if mode == "check": print_rules(); check()
        elif mode == "run": run()
        elif mode == "summary": print_rules(); summary()
        elif mode == "rules": print_rules()
        else: sys.exit("use: python orb_backtest.py check | run | summary | rules   [--universe top10|nifty50|fno] [--start YYYY-MM-DD] [--end YYYY-MM-DD] ...")
    except B.Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
