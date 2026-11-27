"""live_gap_backtest.py - backtest of the LIVE zeko strategy (GAP LONG + GAP SHORT, gap_live_plan.py / gap_live_manager.py of 23-Nov-2026), last 3 months by default.
Put it in the Dhan repo next to bpb_fno_backtest.py (it uses that file's Dhan client and stock list).  Yahoo daily candles + Dhan 1-minute candles.

  python live_gap_backtest.py            run (API answers are cached in live_bt_cache/, so a second run is quick)

LIVE RULES REPLAYED
  Setup   LONG : day i opens > 1 % above the previous close and day i+1 closes below day i close; level = High of day i; entry days i+2..i+4 (used up on first touch).
          SHORT: mirror (gap down, next close higher, level = Low).  One setup per stock per direction (the level price reaches first).
  GAPL    buy CALL, entry 09:15-09:29.            GAPS  buy PUT, entry 09:30-13:59, only if the level was NOT touched 09:15-09:29.
  Option  first OTM strike (call >= level, put < level), up to 2 further OTM if it fails the price / OI test; next month when <= 5 trading days to expiry.
  Size    7 % of funds // (planning price x lot).  GAPS sizes on the funds left after open GAPL premium.
  Exit    SL 60 % / TP 40 % of premium, else 15:30.
  Limits  GAPL max 4 open; GAPS max 3 (4th if >= 2 open shorts are at -5 % or better); premium in use <= 30 % of funds; no new trades after day loss > 30 % of funds or of premium invested today.

WHAT A BACKTEST CANNOT COPY (differences from live)
  Fill = close of the entry-minute option candle.  Planning price = 09:15 open (GAPL) / last close before 09:30 (GAPS).  No bid-ask spread / depth test, BUY chase, margin check or F&O ban list.
  Today's F&O list and lot sizes.  Stop and target in the same minute = STOP.  Costs are a rough estimate (COST_PCT, BROKERAGE) - set them to your contract-note figures.
"""
import os, sys, json, math
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd
import bpb_fno_backtest as B


def env(name, default):
    return type(default)(os.environ.get(name) or default)


TODAY = datetime.now(ZoneInfo("Asia/Kolkata")).date()
END = env("LB_END", str(TODAY - timedelta(days=1)))
START = env("LB_START", str((pd.Timestamp(END) - pd.DateOffset(months=3) + pd.Timedelta(days=1)).date()))
FUNDS = env("LB_FUNDS", 1000000.0)             # starting funds, Rs
COMPOUND = env("LB_COMPOUND", 1)               # 1 = funds grow / shrink with net PnL, 0 = same funds every day
CAP_PCT = env("LB_CAP_PCT", 7.0)
FUND_LIMIT_PCT = env("LB_FUND_LIMIT_PCT", 30.0)   # 0 = off
LOSS_STOP_PCT = env("LB_LOSS_STOP_PCT", 30.0)     # 0 = off
COST_PCT = env("LB_COST_PCT", 0.5)             # estimate: taxes + exchange fees + slippage, % of (buy value + sell value) / 2
BROKERAGE = env("LB_BROKERAGE", 47.0)          # estimate: Rs per round trip (brokerage incl. GST)
OUT = env("LB_OUT", "live_bt_results")
CACHE = env("LB_CACHE", "live_bt_cache")
SYMBOLS = [s.upper() for s in env("LB_SYMBOLS", "").replace(",", " ").split()] or B.FNO

SL_PCT, TP_PCT = 60.0, 40.0
GAP_MIN, GAP_FIRST, GAP_LAST = 0.01, 2, 4
LOW_MIN_PRICE, STRICT_PRICE, STRICT_OI_LOTS, OI_X_QTY, OTM_STEPS, ROLL_DAYS = 1.0, 5.0, 1000, 10, 2, 5
OFFS_MAX, COV_MIN = 10, 0.9


def mm(h, m): return h * 60 + m


STRATS = {"GAPL": dict(long=True, first=mm(9, 15), last=mm(9, 29), max_open=4),
          "GAPS": dict(long=False, first=mm(9, 30), last=mm(13, 59), max_open=3)}
EXIT_MIN = mm(15, 29)                          # last candle of the day = the 15:30 square-off


def minutes(ix): return ix.hour.values * 60 + ix.minute.values


def hhmm(m): return f"{m // 60:02d}:{m % 60:02d}"


# ------------------------------------------------------------------ setups: copied unchanged in logic from gap_live_plan.py
def gap_armed(O, H, L, C, long, gap=GAP_MIN, first=GAP_FIRST, last=GAP_LAST):
    O, H, L, C = (np.asarray(x, float) for x in (O, H, L, C))
    n = len(C); out = []
    for i in range(max(1, n - last), n - 1):
        if i + first > n: continue
        g = (O[i] - C[i - 1]) / C[i - 1]
        if long:
            if not (g > gap and C[i + 1] < C[i]): continue
            lvl = H[i]
            if any(H[j] >= lvl for j in range(i + first, n)): continue
        else:
            if not (g < -gap and C[i + 1] > C[i]): continue
            lvl = L[i]
            if any(L[j] <= lvl for j in range(i + first, n)): continue
        out.append(dict(signal=i, level=float(lvl), day=n - i))
    return out


def gap_pick(arm, long):
    if not arm: return None
    return min(arm, key=lambda x: x["level"]) if long else max(arm, key=lambda x: x["level"])


def candidates(daily, t0, t1):
    """daily = {stock: DataFrame Open High Low Close}.  One row per stock-day whose daily High / Low reaches the armed level (0.5 % tolerance; Dhan minutes decide)."""
    rows = []
    for s, d in daily.items():
        O, H, L, C = (d[k].values.astype(float) for k in ("Open", "High", "Low", "Close"))
        for n in range(10, len(d)):
            day = d.index[n]
            if not (t0 <= day <= t1): continue
            for code, r in STRATS.items():
                x = gap_pick(gap_armed(O[:n], H[:n], L[:n], C[:n], r["long"]), r["long"])
                if not x: continue
                lvl = x["level"]
                if (H[n] >= lvl * 0.995) if r["long"] else (L[n] <= lvl * 1.005):
                    rows.append(dict(stock=s, strategy=code, date=day.date(), level=lvl, signal_date=d.index[x["signal"]].date(), entry_day=x["day"], yahoo_open=O[n]))
    return pd.DataFrame(rows)


def yahoo_daily():
    import yfinance as yf
    raw = yf.download([s + ".NS" for s in SYMBOLS], start=str((pd.Timestamp(START) - pd.Timedelta(days=60)).date()),
                      end=str((pd.Timestamp(END) + pd.Timedelta(days=1)).date()), group_by="ticker", auto_adjust=False, progress=False, threads=True)
    out = {}
    for s in SYMBOLS:
        try: d = raw[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
        if len(d) < 15: continue
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        out[s] = d
    if not out: raise B.Fatal("Yahoo gave no data - run again later")
    return out


# ------------------------------------------------------------------ cached Dhan data
def cached(name, fetch):
    """DataFrame from the cache, else fetch() and store it.  A failed call (None) is not stored, so the next run retries it."""
    p = f"{CACHE}/{name}.pkl"
    if os.path.exists(p): return pd.read_pickle(p)
    df = fetch()
    if df is not None and TODAY > date.fromisoformat(END): df.to_pickle(p)
    return df


def option_day(dh, sid, d, long, off, code):
    side = "CALL" if long else "PUT"

    def fetch():
        j = dh.post("/charts/rollingoption", {
            "exchangeSegment": "NSE_FNO", "interval": "1", "securityId": int(sid), "instrument": "OPTSTK", "expiryFlag": "MONTH", "expiryCode": code,
            "strike": "ATM" if off == 0 else f"ATM{off:+d}", "drvOptionType": side, "requiredData": ["open", "high", "low", "close", "strike", "oi", "volume"],
            "fromDate": str(d), "toDate": str(d + timedelta(days=1))})
        if j is None: return None
        fr = B.frame((j.get("data") or {}).get("ce" if long else "pe"), extra=("strike", "oi", "volume"))
        if fr is None or "strike" not in fr: return pd.DataFrame(columns=["o", "h", "l", "c", "strike", "oi"], index=pd.DatetimeIndex([]), dtype=float)
        return fr[fr.index.date == d]

    return cached(f"OPT_{sid}_{d}_{side}_{off}_{code}", fetch)


def last_tuesday(y, m):
    d = date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)
    while d.weekday() != 1: d -= timedelta(days=1)
    return d


def expiry_code(d):
    """1 = nearest monthly series, 2 = next month (<= ROLL_DAYS weekdays to expiry, same count as the live code).  Expiry = last Tuesday; holiday shifts are ignored."""
    e = last_tuesday(d.year, d.month)
    if e < d: e = last_tuesday(d.year + (d.month == 12), d.month % 12 + 1)
    n = int(np.busday_count(d + timedelta(days=1), e + timedelta(days=1)))
    return 2 if (e <= d or n <= ROLL_DAYS) else 1


# ------------------------------------------------------------------ one candidate -> entry + option outcomes
def find_entry(u, level, code):
    """u = stock 1-minute candles of the day.  -> (timestamp, None) or (None, reason)."""
    r = STRATS[code]; m = minutes(u.index)
    touch = (u.h.values >= level) if r["long"] else (u.l.values <= level)
    if code == "GAPS":
        early = m < r["first"]
        if not early.any(): return None, "no candles before 09:30"
        if (touch & early).any(): return None, "touched before 09:30"
    ok = touch & (m >= r["first"]) & (m <= r["last"])
    if not ok.any(): return None, "level not touched in the entry window"
    return u.index[int(np.argmax(ok))], None


def exit_walk(w, entry):
    sl, tp = entry * (1 - SL_PCT / 100), entry * (1 + TP_PCT / 100)
    for t, o, h, l in zip(w.index, w.o.values, w.h.values, w.l.values):
        if l <= sl: return t, float(min(o, sl)), "STOP"
        if h >= tp: return t, float(max(o, tp)), "TARGET"
    return w.index[-1], float(w.c.iloc[-1]), "TIME"


def contracts(dh, sid, d, level, code, te):
    """The live strike choice: [first OTM, OTM+1, OTM+2] with planning price, OI, entry and exit.  -> (list, reason)."""
    r = STRATS[code]; long = r["long"]; sg = 1 if long else -1
    ecode = expiry_code(d); fallback = 0
    atm = option_day(dh, sid, d, long, 0, ecode)
    if ecode == 2 and (atm is None or atm.empty):
        ecode, fallback = 1, 1; atm = option_day(dh, sid, d, long, 0, ecode)
    if atm is None: return [], "Dhan request failed"
    if atm.empty: return [], "no option candles"
    atm = atm[~atm.index.duplicated()]
    one = option_day(dh, sid, d, long, sg, ecode)
    if one is None or one.empty: return [], "no neighbouring strike (strike step unknown)"
    one = one[~one.index.duplicated()]
    diff = (one.strike - atm.strike).dropna().abs()
    diff = diff[diff > 0]
    if diff.empty: return [], "strike step unknown"
    step = float(diff.mode().iloc[0])
    near = atm[(atm.index <= te)]
    if near.empty: return [], "no ATM candle at the entry"
    ka = float(near.strike.iloc[-1])
    k = math.ceil((level - ka) / step - 1e-9)
    k0 = ka + (k if long else k - 1) * step
    series = {0: atm, sg: one}
    out = []
    for i in range(OTM_STEPS + 1):
        K = round(k0 + sg * i * step, 2)
        need = np.unique(np.rint((K - atm.strike.values) / step).astype(int))        # which ATM+n series holds strike K during the day
        for n in need:
            if abs(n) <= OFFS_MAX and int(n) not in series: series[int(n)] = option_day(dh, sid, d, long, int(n), ecode)
        parts = [x for x in series.values() if x is not None and len(x)]
        S = pd.concat(parts)
        S = S[(S.strike - K).abs() < 1e-6]
        S = S[~S.index.duplicated()].sort_index()
        S = S[minutes(S.index) <= EXIT_MIN]
        if S.empty: continue
        if code == "GAPL":
            plan_px, plan_oi = float(S.o.iloc[0]), float(S.oi.iloc[0]) if "oi" in S else 0.0
            if minutes(S.index)[0] > r["last"]: continue
        else:
            P = S[minutes(S.index) < r["first"]]
            if P.empty: continue
            plan_px, plan_oi = float(P.c.iloc[-1]), float(P.oi.iloc[-1]) if "oi" in P else 0.0
        a = S[(S.index >= te) & (S.index <= te + pd.Timedelta(minutes=3))]
        if a.empty: continue
        t_in, entry = a.index[0], float(a.c.iloc[0])
        w = S[S.index > t_in]
        if w.empty or not entry > 0: continue
        expected = int(((atm.index > t_in) & (minutes(atm.index) <= EXIT_MIN)).sum())
        cov = min(1.0, len(w) / expected) if expected else 1.0
        if cov < COV_MIN: continue
        t_out, px_out, why = exit_walk(w, entry)
        marks = w[w.index <= t_out]
        out.append(dict(otm_step=i, strike=K, expiry_code=ecode, expiry_fallback=fallback, plan_price=plan_px, plan_oi=plan_oi, entry_min=int(minutes(pd.DatetimeIndex([t_in]))[0]),
                        entry_price=entry, exit_min=int(minutes(pd.DatetimeIndex([t_out]))[0]), exit_price=px_out, reason=why, coverage=round(cov, 3),
                        marks=dict(zip(minutes(marks.index).tolist(), marks.c.values.tolist()))))
    return out, None if out else "no usable option candles for the OTM strikes"


def build_events(dh, cand, mst):
    events, skips = [], []

    def skip(row, why): skips.append(dict(stock=row.stock, strategy=row.strategy, date=row.date, level=round(row.level, 2), reason=why))

    def work(t):
        s, g = t
        if s not in mst: return [(row, None, [], "not in the Dhan stock-option list") for row in g.itertuples()]
        sid = mst[s][0]; res = []
        stock = []
        for d0, d1 in B.clusters(sorted(set(g.date)), 85, 30):
            u = cached(f"EQ_{sid}_{d0}_{d1}", lambda: B.eq_minute(dh, sid, d0, d1))
            if u is not None and len(u): stock.append(u)
        days = {k: v for u in stock for k, v in u.groupby(u.index.date)}
        for row in g.itertuples():
            u = days.get(row.date)
            if u is None: res.append((row, None, [], "no stock minute candles")); continue
            ratio = float(u.o.iloc[0]) / float(row.yahoo_open)                   # split / bonus: Yahoo adjusted, Dhan raw
            level = row.level * (ratio if abs(ratio - 1) > 0.2 else 1.0)
            te, why = find_entry(u, level, row.strategy)
            if te is None: res.append((row, None, [], why)); continue
            cs, why = contracts(dh, sid, row.date, level, row.strategy, te)
            res.append((row, te, cs, why))
        return res

    done = [0]
    groups = list(cand.groupby("stock"))

    def handle(t, res):
        for row, te, cs, why in res:
            if not cs: skip(row, why); continue
            events.append(dict(stock=row.stock, strategy=row.strategy, date=row.date, level=round(row.level, 2), signal_date=row.signal_date, entry_day=int(row.entry_day),
                               lot=mst[row.stock][1], touch_min=int(te.hour * 60 + te.minute), contracts=cs))
        done[0] += 1
        print(f"[{done[0]}/{len(groups)}] {t[0]}: {len(res)} candidate days, Dhan calls so far {dh.n}", flush=True)

    B.stream(groups, work, handle)
    return events, skips


# ------------------------------------------------------------------ portfolio replay
def size(ev, cap):
    """The live strike / lot choice for a given per-trade cap.  -> (contract, lots, None) or (None, 0, reason)."""
    why = []
    for c in ev["contracts"]:
        p, lot = c["plan_price"], ev["lot"]
        if p <= LOW_MIN_PRICE: why.append("price at or below Rs 1"); continue
        lots = int(cap // (p * lot))
        if lots < 1: why.append("1 lot costs more than the cap"); continue
        oi = c["plan_oi"]
        if oi > 0:                                                             # no OI in the data -> cannot test
            if p <= STRICT_PRICE and oi / lot < STRICT_OI_LOTS: why.append("cheap option, OI below 1000 lots"); continue
            if oi < OI_X_QTY * lots * lot: why.append("OI below 10 x quantity"); continue
        return c, lots, None
    return None, 0, "; ".join(sorted(set(why))) or "no option"


def mark(t, m):
    """Option price of an open trade at minute m (last close up to m)."""
    ks = [k for k in t["marks"] if k <= m]
    return t["marks"][max(ks)] if ks else t["entry_price"]


def trade_cost(t):
    return (t["entry_price"] + t["exit_price"]) * t["qty"] / 2 * COST_PCT / 100 + BROKERAGE


def replay_day(day_events, equity):
    """Minute by minute, like the manager.  -> (trades, skips)."""
    trades, skips = [], []
    evs = sorted(day_events, key=lambda e: (e["touch_min"], e["strategy"] != "GAPL", e["stock"]))
    stopped = False
    for m in range(mm(9, 15), EXIT_MIN + 1):
        if LOSS_STOP_PCT and trades and not stopped:
            pnl = sum(((t["exit_price"] if t["exit_min"] <= m else mark(t, m)) - t["entry_price"]) * t["qty"] for t in trades)
            invested = sum(t["cost"] for t in trades)
            stopped = -pnl > equity * LOSS_STOP_PCT / 100 or -pnl > invested * LOSS_STOP_PCT / 100
        for e in (x for x in evs if x["touch_min"] == m):
            code = e["strategy"]
            def no(why): skips.append(dict(stock=e["stock"], strategy=code, date=e["date"], level=e["level"], reason=why))
            funds = equity
            if code == "GAPS": funds = equity - sum(t["cost"] for t in trades if t["strategy"] == "GAPL" and t["entry_min"] < mm(9, 30) <= t["exit_min"])
            c, lots, why = size(e, funds * CAP_PCT / 100)
            if c is None: no(why); continue
            if stopped: no("day loss stop"); continue
            open_ = [t for t in trades if t["touch_min"] <= m <= t["exit_min"]]
            held = [t for t in open_ if t["strategy"] == code]
            limit = STRATS[code]["max_open"]
            if code == "GAPS" and len(held) >= limit and sum(mark(t, m) >= t["entry_price"] * 0.95 for t in held) >= 2: limit = 4
            if len(held) >= limit: no("max open trades"); continue
            qty = lots * e["lot"]; cost = qty * c["entry_price"]
            if FUND_LIMIT_PCT and sum(t["cost"] for t in open_) + cost > equity * FUND_LIMIT_PCT / 100: no("30% fund limit"); continue
            t = dict({k: v for k, v in e.items() if k != "contracts"}, **c, lots=lots, qty=qty, cost=cost)
            t["gross_pnl"] = (t["exit_price"] - t["entry_price"]) * qty
            t["costs"] = trade_cost(t); t["net_pnl"] = t["gross_pnl"] - t["costs"]
            t["ret_pct"] = (t["exit_price"] / t["entry_price"] - 1) * 100
            trades.append(t)
    return trades, skips


def replay(events, trade_days):
    equity, trades, skips, daily = FUNDS, [], [], []
    for d in trade_days:
        base = equity if COMPOUND else FUNDS
        t, s = replay_day([e for e in events if e["date"] == d], base)
        pnl = sum(x["net_pnl"] for x in t); equity += pnl
        trades += t; skips += s; daily.append(dict(date=d, trades=len(t), net_pnl=round(pnl, 2), equity=round(equity, 2)))
    return pd.DataFrame(trades), skips, pd.DataFrame(daily)


# ------------------------------------------------------------------ report
def stats(g):
    w, l = g.net_pnl[g.net_pnl > 0].sum(), -g.net_pnl[g.net_pnl < 0].sum()
    return dict(trades=len(g), win_pct=round((g.net_pnl > 0).mean() * 100, 1), gross_pnl=round(g.gross_pnl.sum()), costs=round(g.costs.sum()), net_pnl=round(g.net_pnl.sum()),
                avg_ret_pct=round(g.ret_pct.mean(), 2), profit_factor=round(w / l, 2) if l else float("inf"))


def table(rows):
    if not rows: return "(none)"
    k = list(rows[0])
    return "\n".join(["| " + " | ".join(k) + " |", "|" + "---|" * len(k)] + ["| " + " | ".join(str(r[c]) for c in k) + " |" for r in rows])


def report(T, skips, D):
    S = pd.DataFrame(skips)
    L = [f"# Live GAP strategy backtest: {START} to {END}", "", f"Funds Rs {FUNDS:,.0f} ({'compounding' if COMPOUND else 'fixed'}), {CAP_PCT:g}% per trade, costs {COST_PCT:g}% + Rs {BROKERAGE:g} per trade (estimate)", ""]
    if T.empty:
        L.append("No trades.")
    else:
        eq = np.r_[FUNDS, D.equity.values]; peak = np.maximum.accumulate(eq); dd = (eq - peak)
        L += [f"**Net PnL Rs {T.net_pnl.sum():,.0f} ({T.net_pnl.sum() / FUNDS * 100:.1f}% on funds)**, max drawdown Rs {dd.min():,.0f} ({(dd / peak).min() * 100:.1f}%, day-end), "
              f"winning days {int((D.net_pnl > 0).sum())} / {int((D.trades > 0).sum())}", ""]
        L += ["## By strategy", "", table([dict(strategy="ALL", **stats(T))] + [dict(strategy=k, **stats(g)) for k, g in T.groupby("strategy")]), ""]
        mon = T.assign(month=T.date.astype(str).str[:7])
        L += ["## By month", "", table([dict(month=a, strategy=b, **stats(g)) for (a, b), g in mon.groupby(["month", "strategy"])]), ""]
        L += ["## Exit reasons", "", table([dict(strategy=a, reason=b, **stats(g)) for (a, b), g in T.groupby(["strategy", "reason"])]), ""]
        L += [f"Trades that used the nearest month because next-month data was missing: {int(T.expiry_fallback.sum())}", ""]
    if len(S):
        L += ["## Setups not traded", "", table([dict(strategy=a, reason=b, count=int(n)) for (a, b), n in S.groupby(["strategy", "reason"]).size().items()]), ""]
    return "\n".join(L)


def main():
    os.makedirs(OUT, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
    print(f"Backtest {START} .. {END}, {len(SYMBOLS)} stocks, funds Rs {FUNDS:,.0f}", flush=True)
    daily = yahoo_daily()
    cand = candidates(daily, pd.Timestamp(START), pd.Timestamp(END))
    if cand.empty: sys.exit("No setups in this period")
    print(f"{len(cand)} candidate stock-days", flush=True)
    dh = B.Dhan(); mst = B.load_master()
    events, skips = build_events(dh, cand, mst)
    days = sorted({x.date() for d in daily.values() for x in d.index if pd.Timestamp(START) <= x <= pd.Timestamp(END)})
    T, s2, D = replay(events, days)
    skips += s2
    if len(T):
        out = T.drop(columns=["marks"]).copy()
        for c in ("touch_min", "entry_min", "exit_min"): out[c.replace("_min", "_time")] = out.pop(c).map(hhmm)
        out.round(2).to_csv(f"{OUT}/trades.csv", index=False)
    pd.DataFrame(skips).to_csv(f"{OUT}/skipped.csv", index=False)
    D.to_csv(f"{OUT}/daily.csv", index=False)
    text = report(T, skips, D)
    open(f"{OUT}/REPORT.md", "w").write(text)
    print(text, flush=True)
    failed = sum(1 for s in skips if s["reason"] == "Dhan request failed")
    if failed: print(f"WARNING: {failed} setups skipped because a Dhan request failed - run again to retry them", flush=True)


if __name__ == "__main__":
    try: main()
    except (B.Fatal, B.Stop) as e: sys.exit(f"STOP: {e}")
