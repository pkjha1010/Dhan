"""mr_poc_backtest.py - MEAN REVERSION TO POC + LAST-HOUR FADE, traded next morning with ATM stock options (Dhan 1-minute data).
Reuses the Dhan client / rate limiter / helpers of bpb_fno_backtest.py. Default: top-10 large caps, last 3 years, SL 10 % of premium, time exit 09:30.

  python mr_poc_backtest.py check     test Dhan access (stock candles incl. volume + one ATM option call) and the stock list
  python mr_poc_backtest.py run       full backtest
  python mr_poc_backtest.py summary   rebuild tables + REPORT.txt from saved trades.csv (no API calls)

THE STRATEGY  (everything is built from Dhan 1-minute stock candles: 1-hour and daily candles and the volume profiles are resampled from them)
  Day D = setup day. Day D+1 = trade day.
  0. SIDEWAYS FILTER (the SIDE_DAYS sessions BEFORE D, all must hold)
       - high-low range of those sessions <= SIDE_RANGE % of price (low volatility)
       - daily SMA10 is flat: |change over SIDE_DAYS sessions| <= SMA_FLAT %
       - 1-hour ADX(14) at the end of D-1 <= ADX_MAX (no trend on the 1-hour chart)
  1. RANGE PROFILE  = volume profile (typical price, bins of BIN_PCT % of price) of those same sessions -> POC, Value Area (70 %) VAL / VAH.
  2. LONG SETUP on D
       a. LVN OPEN      : the first-hour low (09:15-10:14) is below the range VAL and sits in a Low Volume Node (bin volume <= LVN_FRAC x POC-bin volume).
       b. REVERSION     : D closes at least MIN_REV % above that low and back at/above the range VAL (price returned to value).
       c. CLOSE AT POC  : D close is within CLOSE_TOL % of D's own session POC.
       d. LAST-HOUR FADE: the last hour (14:30-15:29) is a small red candle: close below open by 0 < drop <= LAST_MAX %.
     SHORT SETUP = exact mirror (first-hour high above range VAH in an LVN, closes back inside, close at session POC, small GREEN last hour).
  3. TRADE DAY D+1 (only 1-minute candles 09:15 .. exit-2 min are checked; with exit 09:30 that is 09:15-09:28)
       LONG  : first 1-minute candle whose High > Day-1 High  -> buy ATM CALL.   (price already above at the open -> filled at that open)
       SHORT : first 1-minute candle whose Low  < Day-1 Low   -> buy ATM PUT.
       Option: nearest monthly expiry, ATM strike at the entry minute, strike locked afterwards. Entry price = close of the option candle of the entry minute.
  4. EXIT   : stop-loss = SL % below the entry premium (first 1-minute low that touches it; gap through it fills at the open), else the close of the
              last option candle before EXIT time (candle stamped 09:29 closes at 09:30). No trade is taken after the exit time.
  Capital   : CAP rupees per trade -> lots = max(1, CAP // (premium x lot size)). Charges, taxes, slippage not included. Lot sizes are today's values.
Output folder: mr_poc_results/  (setups.csv, trades.csv, funnel.csv, summary tables, skipped.csv, REPORT.txt)
"""
import os, sys, time
import numpy as np, pandas as pd
from datetime import date, timedelta

import bpb_fno_backtest as B
from bpb_fno_backtest import Dhan, Fatal, Stop, stream, frame, rolling, load_master, hm, exit_walk

TOP10 = "RELIANCE HDFCBANK ICICIBANK TCS BHARTIARTL INFY SBIN ITC HINDUNILVR LT".split()      # large caps, all in the F&O list
UNIVERSE = [s.strip().upper() for s in (os.environ.get("MR_SYMBOLS") or "").replace(",", " ").split()] or TOP10
START = os.environ.get("MR_START") or str(date.today() - timedelta(days=3 * 365))
END = os.environ.get("MR_END") or str(date.today())
OUT = os.environ.get("MR_OUT", "mr_poc_results")

def _f(name, default): return float(os.environ.get(name) or default)

SIDE_DAYS = int(_f("SIDE_DAYS", 5))        # sessions that must look sideways before the setup day
SIDE_RANGE = _f("SIDE_RANGE", 4.0)         # max (high-low) of those sessions, % of price
SMA_FLAT = _f("SMA_FLAT", 1.0)             # max |change| of daily SMA10 over SIDE_DAYS sessions, %
ADX_MAX = _f("ADX_MAX", 25.0)              # max 1-hour ADX(14) at the end of D-1
BIN_PCT = _f("BIN_PCT", 0.10)              # volume-profile bin height, % of price
LVN_FRAC = _f("LVN_FRAC", 0.35)            # a bin is a Low Volume Node if its volume <= this x the POC bin
MIN_REV = _f("MIN_REV", 0.5)               # min move from the first-hour extreme to the close, %
CLOSE_TOL = _f("CLOSE_TOL", 0.30)          # close within this % of the session POC
LAST_MAX = _f("LAST_MAX", 0.60)            # last-hour candle body, max %
SL_PCT = _f("SL_PCT", 10.0)                # stop-loss, % of option premium
EXIT = os.environ.get("EXIT_TIME") or "09:30"
EXIT_MIN = int(EXIT[:2]) * 60 + int(EXIT[3:])
CAP = _f("CAP", 200000)                    # rupees per trade
EQ_SPAN = 85                               # days per stock 1-minute call (Dhan max 90)
OPEN_MIN, CLOSE_MIN = 9 * 60 + 15, 15 * 60 + 29


def mins(ix): return np.asarray(ix.hour) * 60 + np.asarray(ix.minute)


# ------------------------------------------------------------------ data
def eq_minute_vol(dh, sid, d0, d1):
    j = dh.post("/charts/intraday", {"securityId": str(sid), "exchangeSegment": "NSE_EQ", "instrument": "EQUITY", "interval": "1",
                                     "oi": False, "fromDate": f"{d0} 09:15:00", "toDate": f"{d1} 15:30:00"})
    if j is None: return None
    d = j.get("data") if isinstance(j.get("data"), dict) else j
    fr = frame(d, extra=("volume",))
    return fr if fr is not None else pd.DataFrame(columns=["o", "h", "l", "c", "volume"], index=pd.DatetimeIndex([]))


def clean(df):
    """Regular session only (09:15-15:29), no duplicate minutes, drop part-sessions (< 300 candles, e.g. special sessions)."""
    if "volume" not in df: df["volume"] = 1.0
    df = df[~df.index.duplicated()].sort_index()
    m = mins(df.index)
    df = df[(m >= OPEN_MIN) & (m <= CLOSE_MIN)]
    cnt = df.groupby(df.index.date).size()
    return df[pd.Index(df.index.date).isin(cnt[cnt >= 300].index)]


def load_stock(dh, sid, start, end):
    d0 = pd.Timestamp(start).date() - timedelta(days=30)             # warm-up for SMA10 / ADX / range profile
    d1 = pd.Timestamp(end).date()
    chunks, d = [], d0
    while d <= d1:
        chunks.append((d, min(d + timedelta(days=EQ_SPAN - 1), d1))); d += timedelta(days=EQ_SPAN)
    parts, failed = [], [0]

    def work(t): return eq_minute_vol(dh, sid, *t)

    def handle(t, r):
        if r is None: failed[0] += 1
        elif len(r): parts.append(r)

    stream(chunks, work, handle)
    if failed[0] or not parts: return None
    return clean(pd.concat(parts))


# ------------------------------------------------------------------ volume profile
def value_area(vol, frac=0.70):
    poc = int(np.argmax(vol)); tot, acc, a, b = vol.sum(), vol[poc], poc, poc
    while acc < frac * tot and (a > 0 or b < len(vol) - 1):
        up = vol[b + 1] if b < len(vol) - 1 else -1.0
        dn = vol[a - 1] if a > 0 else -1.0
        if up >= dn: b += 1; acc += up
        else: a -= 1; acc += dn
    return poc, a, b


def build_profile(d):
    ref = float(d.c.mean()); w = max(ref * BIN_PCT / 100, 0.01)
    tp = ((d.h + d.l + d.c) / 3).values; lo = float(tp.min())
    idx = np.floor((tp - lo) / w).astype(int)
    vol = np.bincount(idx, weights=d.volume.values.astype(float), minlength=int(idx.max()) + 1)
    poc, a, b = value_area(vol)
    return dict(lo=lo, w=w, vol=vol, poc=lo + (poc + .5) * w, val=lo + a * w, vah=lo + (b + 1) * w, pocvol=float(vol[poc]))


def vol_at(p, price):
    i = int(np.floor((price - p["lo"]) / p["w"]))
    return float(p["vol"][i]) if 0 <= i < len(p["vol"]) else 0.0            # outside the traded range = no volume = LVN


def adx_series(h, l, c, n=14):
    up, dn = h.diff(), -l.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=h.index)
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=h.index)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    a = 1.0 / n
    atr = tr.ewm(alpha=a, adjust=False).mean()
    pdi, mdi = 100 * pdm.ewm(alpha=a, adjust=False).mean() / atr, 100 * mdm.ewm(alpha=a, adjust=False).mean() / atr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.ewm(alpha=a, adjust=False).mean()


# ------------------------------------------------------------------ step 1: find setup days
FUN = ["days", "sideways", "lvn_open", "reverted", "close_at_poc", "last_hour_fade"]


def scan_setups(df):
    """-> (setups DataFrame, funnel {direction: {stage: count}}). Pure function of the 1-minute candles."""
    by = {d: g for d, g in df.groupby(df.index.date)}
    days = sorted(by)
    daily = pd.DataFrame({"o": [by[d].o.iloc[0] for d in days], "h": [by[d].h.max() for d in days],
                          "l": [by[d].l.min() for d in days], "c": [by[d].c.iloc[-1] for d in days]}, index=days)
    sma = daily.c.rolling(10).mean()
    h1 = df.resample("60min", offset="9h15min").agg({"o": "first", "h": "max", "l": "min", "c": "last"})
    cnt = df.o.resample("60min", offset="9h15min").size()
    h1 = h1[cnt.reindex(h1.index).fillna(0) >= 30]                           # drop the 15-minute stub at the close
    h1["adx"] = adx_series(h1.h, h1.l, h1.c)
    adx_by = h1.adx.groupby(h1.index.date).last()
    rows, fun = [], {s: dict.fromkeys(FUN, 0) for s in ("LONG", "SHORT")}
    start = pd.Timestamp(START).date()
    for k in range(SIDE_DAYS + 10, len(days)):
        D = days[k]
        if D < start: continue
        prev = days[k - SIDE_DAYS:k]; pd_ = daily.loc[prev]
        rng = (pd_.h.max() - pd_.l.min()) / pd_.c.mean() * 100
        slope = (sma.iloc[k - 1] / sma.iloc[k - 1 - SIDE_DAYS] - 1) * 100
        adx = float(adx_by.get(days[k - 1], np.nan))
        for s in fun: fun[s]["days"] += 1
        if not (rng <= SIDE_RANGE and abs(slope) <= SMA_FLAT and adx <= ADX_MAX): continue     # NaN fails every comparison
        rp = build_profile(pd.concat([by[d] for d in prev]))
        g = by[D]; fh = g.between_time("09:15", "10:14"); lh = g.between_time("14:30", "15:29")
        if fh.empty or lh.empty: continue
        sp = build_profile(g)
        O, C = float(g.o.iloc[0]), float(g.c.iloc[-1])
        lo_, lc_ = float(lh.o.iloc[0]), float(lh.c.iloc[-1])
        for side in ("LONG", "SHORT"):
            f, lg = fun[side], side == "LONG"
            f["sideways"] += 1
            ext = float(fh.l.min()) if lg else float(fh.h.max())                # first-hour extreme = move into the zone
            outside = ext < rp["val"] if lg else ext > rp["vah"]
            if not (outside and vol_at(rp, ext) <= LVN_FRAC * rp["pocvol"]): continue
            f["lvn_open"] += 1
            rev = (C / ext - 1) * 100 if lg else (ext / C - 1) * 100
            back = C >= rp["val"] if lg else C <= rp["vah"]
            if not (rev >= MIN_REV and back): continue
            f["reverted"] += 1
            near = abs(C - sp["poc"]) / sp["poc"] * 100
            if near > CLOSE_TOL: continue
            f["close_at_poc"] += 1
            drop = (lo_ - lc_) / lo_ * 100 if lg else (lc_ - lo_) / lo_ * 100   # LONG: red last hour, SHORT: green last hour
            if not (0 < drop <= LAST_MAX): continue
            f["last_hour_fade"] += 1
            nxt = days[k + 1] if k + 1 < len(days) else None
            rows.append(dict(direction=side, setup_date=str(D), trade_date=str(nxt) if nxt else "", day_high=float(daily.h.iloc[k]),
                             day_low=float(daily.l.iloc[k]), side_range_pct=round(rng, 2), sma_slope_pct=round(slope, 2), adx_1h=round(adx, 1),
                             range_poc=round(rp["poc"], 2), range_val=round(rp["val"], 2), range_vah=round(rp["vah"], 2), zone_extreme=round(ext, 2),
                             session_poc=round(sp["poc"], 2), close=round(C, 2), close_to_poc_pct=round(near, 2), reversion_pct=round(rev, 2),
                             last_hour_move_pct=round(drop, 2)))
    return pd.DataFrame(rows), fun


# ------------------------------------------------------------------ step 2: next-day 1-minute trigger on the stock
def entry_signal(g1, level, long):
    """First 1-minute candle (09:15 .. EXIT-2) that breaks Day-1 High (long) / Low (short) -> (timestamp, fill price, gap) or None."""
    w = g1[mins(g1.index) <= EXIT_MIN - 2]
    if w.empty: return None
    touch = (w.h > level) if long else (w.l < level)
    if not touch.any(): return None
    k = int(np.argmax(touch.values)); o = float(w.o.iloc[k])
    px = max(level, o) if long else min(level, o)                                # stop order: a gap fills at the open
    return w.index[k], px, bool(o > level) if long else bool(o < level)


# ------------------------------------------------------------------ step 3: ATM option on the entry minute -> trade
def option_trade(sid, lot, side, d, ts, fetch=rolling, dh=None):
    """-> (status, dict). status: 'ok' | 'skip' (with reason)."""
    nxt = d + timedelta(days=1)
    atm = fetch(dh, sid, d, nxt, side, 0)
    if atm is None or atm.empty: return "skip", "no option data from Dhan"
    a = atm[atm.index >= ts]
    if a.empty or (a.index[0] - ts) > pd.Timedelta(minutes=5): return "skip", "no ATM candle at the entry minute"
    te, K, entry = a.index[0], float(a.strike.iloc[0]), float(a.c.iloc[0])
    if not entry > 0: return "skip", "zero option price"
    last = EXIT_MIN - 1                                                          # last candle stamp used (09:29 for a 09:30 exit)
    tm = te.hour * 60 + te.minute
    if tm >= last: return "skip", "entry too close to the exit time"
    win = lambda x: x[(x.index > te) & (mins(x.index) <= last)]
    if (win(atm).strike != K).any():                                             # ATM strike moved: fetch neighbours to follow the locked strike
        parts = [atm] + [x for x in (fetch(dh, sid, d, nxt, side, o) for o in (1, -1)) if x is not None]
        allr = pd.concat(parts)
    else: allr = atm
    allr = allr[allr.strike == K]; allr = allr[~allr.index.duplicated()].sort_index()
    ser = win(allr)
    if ser.empty: return "skip", "no option candles after the entry"
    res = exit_walk(ser.o.values, ser.h.values, ser.l.values, entry, SL_PCT, 0)
    if res: i, px, why = res; tx = ser.index[i]
    else: px, why, tx = float(ser.c.iloc[-1]), "TIME", ser.index[-1]
    lots = max(1, int(CAP // (entry * lot)))
    expected = last - tm
    return "ok", dict(strike=K, entry_time=hm(te), entry_price=round(entry, 2), exit_time=hm(tx), exit_price=round(px, 2), exit_reason=why,
                      lot_size=lot, lots=lots, capital=round(entry * lot * lots), pnl=round((px - entry) * lot * lots),
                      roi_pct=round((px / entry - 1) * 100, 2), option_coverage=round(len(ser) / max(expected, 1), 2))


# ------------------------------------------------------------------ reporting
def stats(t):
    if t.empty: return {}
    t = t.sort_values(["trade_date", "entry_time"]); cum = t.pnl.cumsum()
    gl = abs(t.pnl[t.pnl < 0].sum())
    return dict(trades=len(t), win_pct=round(100 * (t.pnl > 0).mean(), 1), avg_roi_pct=round(t.roi_pct.mean(), 2),
                total_pnl=int(t.pnl.sum()), profit_factor=round(t.pnl[t.pnl > 0].sum() / gl, 2) if gl else np.inf,
                stop_pct=round(100 * t.exit_reason.str.startswith("STOP").mean(), 1), max_drawdown=int((cum.cummax() - cum).max()))


def by_table(t, key):
    if t.empty: return pd.DataFrame()
    return pd.DataFrame({k: stats(g) for k, g in t.groupby(key)}).T


def write_report(trades, setups, funnel):
    parts = [f"MEAN REVERSION TO POC + LAST-HOUR FADE   {START} .. {END}   stocks: {' '.join(UNIVERSE)}",
             f"SL {SL_PCT:g} % of premium | time exit {EXIT} | capital per trade Rs {CAP:,.0f} | setups found {len(setups)} | trades taken {len(trades)}", ""]
    if len(trades):
        parts += ["OVERALL", pd.DataFrame([stats(trades)]).to_string(index=False), ""]
        trades = trades.assign(year=trades.trade_date.str[:4])
        for key in ("stock", "direction", "year"):
            tb = by_table(trades, key); tb.to_csv(f"{OUT}/by_{key}.csv"); parts += [f"BY {key.upper()}", tb.to_string(), ""]
    else: parts += ["No trades.", ""]
    if len(funnel): parts += ["FUNNEL (how many days survive each filter)", funnel.to_string(index=False), ""]
    open(f"{OUT}/REPORT.txt", "w").write("\n".join(parts)); print("\n".join(parts), flush=True)


# ------------------------------------------------------------------ modes
def check():
    mst = load_master(); dh = Dhan()
    miss = [s for s in UNIVERSE if s not in mst]
    print(f"Stocks: {UNIVERSE}\nNot in Dhan stock-option list: {miss or 'none'}", flush=True)
    s = next(x for x in UNIVERSE if x in mst); sid, lot = mst[s]
    d1 = date.today(); d0 = d1 - timedelta(days=10)
    u = eq_minute_vol(dh, sid, d0, d1)
    print(f"{s}: {0 if u is None else len(u)} one-minute candles, volume column {'present' if u is not None and 'volume' in u and u.volume.sum() > 0 else 'MISSING'}", flush=True)
    if u is not None and len(u):
        day = u.index[-1].date(); o = rolling(dh, sid, day, day + timedelta(days=1), "LONG", 0)
        print(f"{s} ATM call candles on {day}: {0 if o is None else len(o)}  (lot size {lot})", flush=True)
    print(f"Dhan calls used: {dh.n}", flush=True)


def run():
    os.makedirs(OUT, exist_ok=True)
    mst = load_master(); dh = Dhan()
    skipped, setups, funnel, cands = [], [], [], []
    data = {}
    for s in UNIVERSE:
        if s not in mst: skipped.append((s, "not in Dhan stock-option list")); continue
        df = load_stock(dh, mst[s][0], START, END)
        if df is None or df.empty: skipped.append((s, "stock candles missing/incomplete from Dhan")); print(f"{s}: SKIPPED (candles)", flush=True); continue
        data[s] = df
        st, fun = scan_setups(df)
        for side, f in fun.items(): funnel.append(dict(stock=s, direction=side, **f))
        print(f"{s}: {len(df.index.normalize().unique())} sessions, {len(st)} setups, calls {dh.n}", flush=True)
        if st.empty: continue
        st.insert(0, "stock", s); st["triggered"] = 0
        for i, r in st.iterrows():
            if not r.trade_date: continue
            g1 = df[df.index.date == pd.Timestamp(r.trade_date).date()]
            if g1.empty: continue
            sig = entry_signal(g1, r.day_high if r.direction == "LONG" else r.day_low, r.direction == "LONG")
            if sig is None: continue
            st.at[i, "triggered"] = 1
            cands.append(dict(stock=s, direction=r.direction, setup_date=r.setup_date, trade_date=r.trade_date, level=r.day_high if r.direction == "LONG" else r.day_low,
                              stock_entry_time=hm(sig[0]), stock_entry_price=round(sig[1], 2), gap_open=int(sig[2]), ts=sig[0]))
        setups.append(st)
    S = pd.concat(setups) if setups else pd.DataFrame()
    S.to_csv(f"{OUT}/setups.csv", index=False)
    F = pd.DataFrame(funnel); F.to_csv(f"{OUT}/funnel.csv", index=False)
    print(f"{len(S)} setups, {len(cands)} triggered next morning -> fetching ATM option candles", flush=True)
    trades = []

    def work(c):
        side = "LONG" if c["direction"] == "LONG" else "SHORT"
        return option_trade(mst[c["stock"]][0], mst[c["stock"]][1], side, pd.Timestamp(c["trade_date"]).date(), c["ts"], dh=dh)

    def handle(c, res):
        status, x = res
        if status == "ok": trades.append({**{k: v for k, v in c.items() if k != "ts"}, **x})
        else: skipped.append((f"{c['stock']} {c['trade_date']} {c['direction']}", x))

    try: stream(cands, work, handle)
    except Stop as e: print(f"STOPPED EARLY: {e}", flush=True)
    T = pd.DataFrame(trades)
    if len(T): T = T.sort_values(["trade_date", "stock"]).reset_index(drop=True)
    T.to_csv(f"{OUT}/trades.csv", index=False)
    pd.DataFrame(skipped, columns=["item", "reason"]).to_csv(f"{OUT}/skipped.csv", index=False)
    print(f"Dhan calls used: {dh.n}; skipped {len(skipped)} (see skipped.csv)", flush=True)
    write_report(T, S, F)


def summary():
    T = pd.read_csv(f"{OUT}/trades.csv") if os.path.exists(f"{OUT}/trades.csv") else pd.DataFrame()
    S = pd.read_csv(f"{OUT}/setups.csv") if os.path.exists(f"{OUT}/setups.csv") else pd.DataFrame()
    F = pd.read_csv(f"{OUT}/funnel.csv") if os.path.exists(f"{OUT}/funnel.csv") else pd.DataFrame()
    write_report(T, S, F)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    try:
        {"check": check, "run": run, "summary": summary}[mode]()
    except Fatal as e:
        print(f"STOP - needs your action: {e}", flush=True); sys.exit(1)
    except Stop as e:
        print(f"Stopped politely: {e}", flush=True)
