"""bo5w_backtest.py - "5-day-high breakout + Bollinger + previous day green + longer upper wick" (your Colab script) on ATM CALL options of ALL F&O stocks, year 2026, Dhan 1-minute data.
Entry = the option at the CLOSE of the breakout day B (daily candle decides), exit = the NEXT trading day B+1 morning (1-minute option candles decide).  Every exit variation is combined.

  python bo5w_backtest.py check     test Dhan access + print the rules
  python bo5w_backtest.py run       Yahoo daily signals -> Dhan option candles (resumable - run again after a polite stop) -> every result file
  python bo5w_backtest.py summary   rebuild every result file from the saved option candles (no API calls) - use it to change the exit grid / capital
  python bo5w_backtest.py rules     print the rules only

SETUP (daily candles, Yahoo, day t = breakout day B)   see bo5w_rules.py (proved equal to your script's conditions by test_bo5w.py)
  close > highest High of the previous 5 days  AND  close > upper Bollinger band (20, 2 std)  AND  day t-1 green (close > open)  AND  upper wick > lower wick of day t.
ENTRY      buy the ATM call at the close of B: the option price is the close of the last 1-minute option candle up to 15:29 (it must be from 15:19 or later; if the ATM series has no such candle ITM-1, ITM-2, ITM-3
           are tried).  The strike is locked.  Nearest monthly expiry; if B is itself the monthly expiry day the NEXT month's series is used (the contract must survive the night).
EXIT       on B+1 (the next trading day), option 1-minute candles of the locked strike (the ATM+n series that holds it is fetched):
           time exit   09:15 open | 09:15 close | 09:16 close | 09:20 close | 09:30 close
           stop-loss   none / 20 / 40 / 60 % of the premium  x  gap rule off / on.  GAP RULE = the stock opens on B+1 BELOW the entry price (Yahoo Open[B+1] < Close[B]) -> sell the option at its 09:15 open.
                       (gap rule on + 'none' = your "stop-loss at 09:15 if the market opens below the entry price" alone; the other 3 combine it with the percent stop.)
           target      40 / 60 / 80 / 100 / 120 / 200 % of the premium or none
           = 5 x 8 x 7 = 280 variants.  Stop / target fill at the first 1-minute low / high touching the level, a gap through it fills at that candle's open, stop and target in the same minute = STOP.
CAPITAL    at most Rs 60,000 per trade (whole lots, today's lot sizes), no charges / slippage.
All settings of the grid are applied at summary time from the saved raw candles: change BO5_EXITS / BO5_SLS / BO5_GAPS / BO5_TPS / BO5_CAP and run `summary` - no new API calls.

Results in bo5w_results/: SUMMARY.md (start here), summary.csv (every variant), matrix_*.csv, signals.csv (one row per signal), trades_all_variants.csv.gz (every trade of every variant),
trades_best_variant.csv, by_month_best.csv, PROGRESS.txt, REPORT.txt  (+ parts/ = saved option candles, skipped/, candidates_*.csv)
"""
import os, sys, json, glob, time, subprocess
from collections import Counter
from datetime import date, datetime, timedelta


def _env(name, default):
    return os.environ.get(name) or default


OUT = _env("BO5_OUT", "bo5w_results")
START = _env("BO5_START", "2026-01-01")
END = _env("BO5_END", str(date.today()))
LOOKBACK = int(_env("BO5_LOOKBACK", "5"))
BB_N, BB_K = 20, 2.0
ITM_MAX = int(_env("BO5_ITM_MAX", "3"))
OFFS_MAX, MAX_OFFS = 10, 6
CAP = int(_env("BO5_CAP", "60000"))
EXITS = [x for x in _env("BO5_EXITS", "0915o,0915c,0916c,0920c,0930c").replace(" ", ",").split(",") if x]
SLS = [int(x) for x in _env("BO5_SLS", "0,20,40,60").replace(" ", ",").split(",") if x]            # 0 = no percent stop
GAPS = [int(x) for x in _env("BO5_GAPS", "0,1").replace(" ", ",").split(",") if x]                  # 0 = gap rule off, 1 = on
TPS = [int(x) for x in _env("BO5_TPS", "40,60,80,100,120,200,0").replace(" ", ",").split(",") if x]  # 0 = no target
MIN_TRADES = int(_env("BO5_MIN_TRADES", "10"))
STORE_FROM, STORE_TO = 9 * 60 + 15, 10 * 60                                                          # option candles saved for B+1: 09:15 .. 10:00
ENTRY_LAST, ENTRY_STALE = 15 * 60 + 29, 10                                                           # entry candle: last one up to 15:29, at most 10 minutes old
SYMBOLS = _env("BO5_SYMBOLS", "")
LAST_CP = [time.time()]

import numpy as np, pandas as pd
import bpb_fno_backtest as B
import bo5w_rules as R

Stop, Fatal = B.Stop, B.Fatal
UNIVERSE = [s.strip().upper() for s in SYMBOLS.replace(",", " ").split()] or list(B.FNO)
VARS = R.variants(EXITS, SLS, GAPS, TPS)


class CallFailed(Exception):
    """A Dhan request failed (HTTP 400 ...): nothing is stored for this signal, the next run retries it."""


# ---------------------------------------------------------------- rules text
def rules_text():
    return (f"5-DAY-HIGH BREAKOUT + BOLLINGER + PREVIOUS DAY GREEN + LONGER UPPER WICK (LONG, ATM call).  B = breakout day: close above the highest High of the previous {LOOKBACK} days, close above the upper "
            f"Bollinger band ({BB_N}, {BB_K:g} std), day B-1 green, upper wick > lower wick.  ENTRY at the close of B (option price = last 1-minute candle up to 15:29, ATM then ITM-1..{ITM_MAX}; next month's series when "
            f"B is the monthly expiry).  EXIT on B+1: time exit {', '.join(R.exit_label(e) for e in EXITS)}; stop-loss {', '.join('none' if not s else str(s) + '%' for s in SLS)} x gap rule "
            f"{'/'.join('on' if g else 'off' for g in GAPS)} (gap rule = stock opens below the entry price -> sell at the 09:15 option open); target "
            f"{', '.join('none' if not t else str(t) + '%' for t in TPS)}.  {len(VARS)} variants.  Rs {CAP:,} per trade.")


def print_rules():
    print(rules_text(), flush=True)
    print(f"{len(UNIVERSE)} stocks; entry dates {START} .. {END}", flush=True)


# ---------------------------------------------------------------- step 1: daily signals (Yahoo)
def yahoo_candidates():
    import yfinance as yf
    t0, t1 = pd.Timestamp(START), pd.Timestamp(END)
    raw = yf.download([s + ".NS" for s in UNIVERSE], start=str((t0 - pd.Timedelta(days=120)).date()), end=str((t1 + pd.Timedelta(days=8)).date()),
                      group_by="ticker", auto_adjust=False, progress=False, threads=True)
    frames, nst = {}, 0
    for s in UNIVERSE:
        try: d = raw[s + ".NS"][["Open", "High", "Low", "Close"]].dropna()
        except KeyError: print(f"{s}: no Yahoo data", flush=True); continue
        if len(d) < BB_N + LOOKBACK + 5: continue
        d.index = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
        frames[s] = d; nst += 1
    if nst == 0: raise Fatal("Yahoo download gave no data for any stock - run again later")
    tradedays = set()
    for d in frames.values(): tradedays |= {x.date() for x in d.index}
    rows = []
    for s, d in frames.items():
        O, H, L, C = (d[k].values.astype(float) for k in ("Open", "High", "Low", "Close"))
        dates = d.index
        for sg in R.signals(O, H, L, C, LOOKBACK, BB_N, BB_K, need_next=True):
            i = sg["i"]
            if not (t0 <= dates[i] <= t1): continue
            b, b1 = dates[i].date(), dates[i + 1].date()
            rows.append(dict(stock=s, date=str(b), next_date=str(b1), close=round(C[i], 2), open=round(O[i], 2), high=round(H[i], 2), low=round(L[i], 2),
                             level5=round(sg["level5"], 2), upper_bb=round(sg["upper_bb"], 2), upper_wick=round(sg["upper_wick"], 2), lower_wick=round(sg["lower_wick"], 2),
                             next_open=round(O[i + 1], 2), gap_flag=int(O[i + 1] < C[i]), gap_pct=round((O[i + 1] / C[i] - 1) * 100, 2),
                             expiry_day=int(R.real_expiry(b, tradedays) == b)))
    r = pd.DataFrame(rows)
    print(f"Yahoo: {nst} stocks, {len(r)} breakout days with a next trading day in {START}..{END}", flush=True)
    return r


def get_candidates():
    cp = f"{OUT}/candidates_{START}_{END}.csv"
    if os.path.exists(cp): return pd.read_csv(cp)
    cand = yahoo_candidates()
    cand.to_csv(cp, index=False)
    return cand


# ---------------------------------------------------------------- step 2: Dhan option candles for one signal
def rolling_ex(dh, sid, d0, offset, code):
    """Rolling CALL candles of one day (d0 <= date < d0+1), nearest monthly series (code 1) or the next month (code 2)."""
    strike = "ATM" if offset == 0 else f"ATM{offset:+d}"
    j = dh.post("/charts/rollingoption", {
        "exchangeSegment": "NSE_FNO", "interval": "1", "securityId": int(sid), "instrument": "OPTSTK", "expiryFlag": "MONTH", "expiryCode": code, "strike": strike,
        "drvOptionType": "CALL", "requiredData": ["open", "high", "low", "close", "strike"], "fromDate": str(d0), "toDate": str(d0 + timedelta(days=1))})
    if j is None: raise CallFailed(f"{d0} {strike} code {code}")
    fr = B.frame((j.get("data") or {}).get("ce"), extra=("strike",))
    if fr is None: return pd.DataFrame(columns=["o", "h", "l", "c", "strike"], index=pd.DatetimeIndex([]))
    return fr


def minutes(x): return x.index.hour.values * 60 + x.index.minute.values


def infer_step(strikes):
    u = np.unique(np.round(np.asarray(strikes, float), 4)); d = np.diff(u); d = d[d > 1e-9]
    return float(d.min()) if len(d) else 0.0


def entry_leg(fetch, b, code):
    """-> dict(offset, strike, price, time) of the option at the close of B, or (None, reason)."""
    why = "no ATM / ITM option candle near the close of the breakout day"
    for k in range(ITM_MAX + 1):
        off = -k                                                              # call: ITM = lower strikes
        x = fetch(b, off, code)
        if x.empty: continue
        x = x[x.index.date == b]
        mm = minutes(x); w = x[mm <= ENTRY_LAST]
        if w.empty or ENTRY_LAST - int(minutes(w)[-1]) > ENTRY_STALE: continue
        price = float(w.c.iloc[-1])
        if not price > 0: why = "zero option price at the close"; continue
        return dict(offset=off, strike=float(w.strike.iloc[-1]), price=price, time=f"{w.index[-1]:%H:%M}"), None
    return None, why


def next_leg(fetch, b1, strike):
    """Candles (09:15..10:00) of the LOCKED strike on B+1: the ATM series first, then the ATM+n series that hold the strike."""
    x0 = fetch(b1, 0, 1)
    if x0.empty: return None, "Dhan returned no option candles on the exit day"
    x0 = x0[x0.index.date == b1]
    step = infer_step(np.r_[x0.strike.values, strike])                        # strike distance from the WHOLE day's ATM strikes (the first 45 minutes alone may hold only 1-2 strikes)
    x0 = x0[(minutes(x0) >= STORE_FROM) & (minutes(x0) <= STORE_TO)]
    if x0.empty: return None, "no option candles 09:15-10:00 on the exit day"
    parts = [x0[(x0.strike - strike).abs() < 1e-6]]
    if step > 0:
        n = np.rint((strike - x0.strike.values) / step).astype(int)
        for v, _ in Counter(n[n != 0].tolist()).most_common(MAX_OFFS):
            if abs(v) > OFFS_MAX: continue
            x = fetch(b1, int(v), 1)
            if x.empty: continue
            x = x[(x.index.date == b1) & (minutes(x) >= STORE_FROM) & (minutes(x) <= STORE_TO)]
            parts.append(x[(x.strike - strike).abs() < 1e-6])
    S = pd.concat(parts)
    S = S[~S.index.duplicated()].sort_index()
    if S.empty: return None, "no option candles of the locked strike on the exit day"
    return S, None


def process(fetch, mst, r):
    """One signal -> ('ok', record) | ('skip', reason).  fetch(day, offset, code) -> candle frame; raises CallFailed."""
    s = r["stock"]; sid, lot = mst[s]
    b, b1 = date.fromisoformat(r["date"]), date.fromisoformat(r["next_date"])
    code = 2 if r["expiry_day"] else 1                                          # B is the monthly expiry: take next month's contract, it must live through the night
    f = lambda d, off, c: fetch(sid, d, off, c)
    ent, why = entry_leg(f, b, code)
    if ent is None: return "skip", why + (" (next-month series)" if code == 2 else "")
    S, why = next_leg(f, b1, ent["strike"])
    if S is None: return "skip", why
    cd = [[int(m), round(float(o), 2), round(float(h), 2), round(float(l), 2), round(float(c), 2)] for m, o, h, l, c in zip(minutes(S), S.o, S.h, S.l, S.c)]
    return "ok", dict(stock=s, date=r["date"], next_date=r["next_date"], strike=ent["strike"], strike_offset=ent["offset"], entry_time=ent["time"], entry_price=round(ent["price"], 2), lot=int(lot),
                      expiry_day=int(r["expiry_day"]), gap_flag=int(r["gap_flag"]), cd=json.dumps(cd, separators=(",", ":")))


# ---------------------------------------------------------------- files / resume / checkpoint
def pkey(r): return f"{r['stock']}_{r['date']}"


def done_keys():
    return {os.path.basename(f).rsplit(".", 1)[0] for f in glob.glob(f"{OUT}/parts/*.json") + glob.glob(f"{OUT}/skipped/*.json")}


def checkpoint(force=False):
    """On GitHub Actions: save progress to the repo every ~15 minutes."""
    if not os.environ.get("GITHUB_ACTIONS"): return
    if not force and time.time() - LAST_CP[0] < 900: return
    LAST_CP[0] = time.time()
    for c in (["git", "config", "user.name", "bo5w-bot"], ["git", "config", "user.email", "bo5w-bot@users.noreply.github.com"], ["git", "add", OUT],
              ["git", "commit", "-m", "bo5w progress"], ["git", "pull", "--no-rebase", "-X", "ours", "--no-edit"], ["git", "push"]):
        r = subprocess.run(c, capture_output=True, text=True)
        if r.returncode and c[1] != "commit":
            print(f"checkpoint: '{' '.join(c)}' failed: {(r.stdout + r.stderr)[-300:]}", flush=True); return
    print("checkpoint: progress saved to the repo", flush=True)


def rule_dict():
    return dict(version=1, lookback=LOOKBACK, bb=[BB_N, BB_K], itm_max=ITM_MAX, start=START, end=END, symbols=len(UNIVERSE))


def run():
    os.makedirs(f"{OUT}/parts", exist_ok=True); os.makedirs(f"{OUT}/skipped", exist_ok=True)
    rp = f"{OUT}/rule.json"; rule = json.loads(json.dumps(rule_dict()))
    if os.path.exists(rp):
        old = json.load(open(rp))
        if old != rule:
            sys.exit(f"STOP - the saved data in {OUT} was made with other settings:\n  saved: {json.dumps(old)}\n  now:   {json.dumps(rule)}\nUse the same settings or give BO5_OUT another folder name.")
    json.dump(rule, open(rp, "w"), indent=1)
    print_rules()
    cand = get_candidates()
    if cand.empty: print("No breakout days in this range."); return
    dh = B.Dhan(); mst = B.load_master()
    miss = sorted(set(cand.stock) - set(mst))
    if miss: print(f"not in Dhan's stock-option list - skipped: {miss}", flush=True)
    cand = cand[cand.stock.isin(mst)]
    done = done_keys()
    todo = [r for r in cand.to_dict("records") if pkey(r) not in done]
    print(f"Breakout days: {len(cand)}  |  already done: {len(cand) - len(todo)}  |  to do now: {len(todo)}", flush=True)
    fails = [0]

    def fetch(sid, d, off, code):
        return rolling_ex(dh, sid, d, off, code)

    def work(r):
        try: return process(fetch, mst, r)
        except CallFailed as e: return "fail", str(e)

    def handle(r, res):
        kind, val = res
        if kind == "fail":
            fails[0] += 1; print(f"{r['stock']} {r['date']}: Dhan request FAILED ({val}) - retried on the next run", flush=True); return
        if kind == "ok":
            json.dump(val, open(f"{OUT}/parts/{pkey(r)}.json", "w"))
            print(f"{r['stock']} {r['date']}: option {val['strike']:g} entry {val['entry_price']} lot {val['lot']} ({len(json.loads(val['cd']))} candles on {r['next_date']}), calls {dh.n}", flush=True)
        else:
            json.dump(dict(stock=r["stock"], date=r["date"], reason=val), open(f"{OUT}/skipped/{pkey(r)}.json", "w"))
            print(f"{r['stock']} {r['date']}: skipped - {val}", flush=True)
        checkpoint()

    try:
        B.stream(todo, work, handle)
        if fails[0]: print(f"WARNING: {fails[0]} signal(s) had a failed Dhan request - run again to retry them.", flush=True)
        print("ALL STEPS FINISHED", flush=True)
    except Stop as e:
        print(f"\nSTOPPED POLITELY: {e}. Progress is saved - run again to continue.", flush=True)
    finally:
        B.print_stats(dh); summary(); checkpoint(True)


def check():
    dh = B.Dhan(); mst = B.load_master()
    print(f"Instrument list OK: {len(mst)} stocks with options. RELIANCE ->", mst.get("RELIANCE"), flush=True)
    miss = [s for s in UNIVERSE if s not in mst]
    print(f"{len(UNIVERSE) - len(miss)} of {len(UNIVERSE)} stocks found in Dhan's list. NOT in it: {miss}", flush=True)
    d = date.today() - timedelta(days=1)
    while d.weekday() >= 5: d -= timedelta(days=1)
    x = rolling_ex(dh, mst["RELIANCE"][0], d, 0, 1)
    print(f"Rolling ATM call, {d}: {len(x)} candles", flush=True)
    if len(x): print(x.tail(3))
    B.print_stats(dh)


# ---------------------------------------------------------------- step 3: simulate every variant, write the results
def load_records():
    fs = sorted(glob.glob(f"{OUT}/parts/*.json"))
    return pd.DataFrame([json.load(open(f)) for f in fs]) if fs else pd.DataFrame()


def load_skips():
    fs = sorted(glob.glob(f"{OUT}/skipped/*.json"))
    return pd.DataFrame([json.load(open(f)) for f in fs]) if fs else pd.DataFrame(columns=["stock", "date", "reason"])


def label_sl(sl, gap):
    p = "no SL" if not sl else f"SL {sl}%"
    return (("GAP rule" if not sl else f"GAP rule + {p}") if gap else p)


def label_tp(tp): return "no TP" if not tp else f"TP {tp}%"


def md(df, index=False):
    try: return df.to_markdown(index=index)
    except Exception: return df.to_string(index=index)


def simulate_all(RC):
    """-> trades DataFrame (one row per trade x available variant)."""
    rows = []
    for r in RC.itertuples():
        lots = int(CAP // (r.entry_price * r.lot))
        if lots < 1: continue
        qty = lots * r.lot; cost = r.entry_price * qty; cd = json.loads(r.cd)
        for (ex, sl, g, tp) in VARS:
            res = R.simulate(r.entry_price, cd, ex, sl, bool(g), tp, bool(r.gap_flag))
            if res is None: continue
            m, px, code, thin = res
            rows.append((r.stock, r.date, r.next_date, r.entry_time, r.strike, r.strike_offset, r.entry_price, r.lot, lots, round(cost), r.gap_flag, ex, sl, g, tp,
                         f"{m // 60:02d}:{m % 60:02d}", round(px, 2), R.REASON[code], round((px - r.entry_price) * qty), round((px / r.entry_price - 1) * 100, 2), thin))
    cols = ["stock", "entry_date", "exit_date", "entry_time", "strike", "strike_offset", "entry_price", "lot", "lots", "cost", "stock_gap_down", "exit_rule", "sl", "gap_rule", "tp",
            "exit_time", "exit_price", "reason", "pnl", "ret_pct", "thin_exit"]
    return pd.DataFrame(rows, columns=cols)


def aggregate(T, n_entries):
    rows = []
    for (ex, sl, g, tp), G in T.groupby(["exit_rule", "sl", "gap_rule", "tp"], sort=False):
        G = G.sort_values(["entry_date", "stock"]); p = G.pnl.values.astype(float); n = len(G)
        gp, gl = p[p > 0].sum(), -p[p < 0].sum(); cum = np.cumsum(p); dd = (cum - np.maximum.accumulate(np.r_[0.0, cum])[1:]).min()
        rc = G.reason.value_counts()
        rows.append(dict(exit_rule=R.exit_label(ex), exit_tag=ex, stop_loss=label_sl(sl, g), sl=sl, gap_rule=g, target=label_tp(tp), tp=tp, trades=n, entries=n_entries, wins=int((p > 0).sum()),
                         win_pct=round((p > 0).mean() * 100, 2), total_pnl=int(round(p.sum())), capital_used=int(G.cost.sum()), roi_pct=round(p.sum() / G.cost.sum() * 100, 2),
                         avg_ret_pct=round(G.ret_pct.mean(), 2), avg_pnl=int(round(p.mean())), profit_factor=round(gp / gl, 2) if gl > 0 else np.nan, max_drawdown=int(round(dd)),
                         stop_exits=int(rc.filter(like="STOP").sum()), target_exits=int(rc.filter(like="TARGET").sum()), gap_rule_exits=int(rc.filter(like="GAP RULE").sum()),
                         time_exits=int(rc.get("TIME", 0)), thin_exits=int(G.thin_exit.sum())))
    return pd.DataFrame(rows)


def matrix(S, metric, ex):
    P = S[S.exit_tag == ex].pivot_table(index=["gap_rule", "sl"], columns="tp", values=metric, aggfunc="first")
    P = P.reindex(columns=[t for t in TPS if t in P.columns]); P.columns = [label_tp(t) for t in P.columns]
    P = P.reset_index(); P.insert(0, "stop_loss", [label_sl(s, g) for s, g in zip(P.sl, P.gap_rule)]); return P.drop(columns=["gap_rule", "sl"])


def summary():
    os.makedirs(OUT, exist_ok=True)
    RC = load_records(); SK = load_skips()
    cps = sorted(glob.glob(f"{OUT}/candidates_*.csv")); cand = pd.read_csv(cps[-1]) if cps else pd.DataFrame()
    n_sig = len(cand)
    prog = f"{len(RC) + len(SK)} of {n_sig} breakout days processed" if n_sig else "no candidates yet"
    status = "COMPLETE" if n_sig and len(RC) + len(SK) >= n_sig else "PARTIAL - run again to continue"
    open(f"{OUT}/PROGRESS.txt", "w").write(f"{status}: {prog}\n"); print(f"\n*** {status}: {prog} ***", flush=True)
    rep = [f"Breakout days found (Yahoo daily, all four rules, with a next trading day): {n_sig}", f"With option data (a trade): {len(RC)}", f"Skipped: {len(SK)}"]
    if len(SK): rep += ["  reasons: " + "; ".join(f"{k} = {v}" for k, v in SK.reason.value_counts().items())]
    open(f"{OUT}/REPORT.txt", "w").write("\n".join(rep) + "\n"); print("\n".join(rep), flush=True)
    if len(SK): SK.to_csv(f"{OUT}/skipped.csv", index=False)
    if RC.empty: print("No saved option data yet - run the backtest first.", flush=True); return
    RC = RC.merge(cand[["stock", "date", "close", "next_open", "gap_pct", "level5", "upper_bb", "upper_wick", "lower_wick"]], on=["stock", "date"], how="left") if n_sig else RC
    T = simulate_all(RC)
    if T.empty: print("No trade could be simulated (Rs 60,000 buys no lot?).", flush=True); return
    S = aggregate(T, len(RC)); S.to_csv(f"{OUT}/summary.csv", index=False)
    T.sort_values(["exit_rule", "sl", "gap_rule", "tp", "entry_date", "stock"]).to_csv(f"{OUT}/trades_all_variants.csv.gz", index=False)
    sig = RC.drop(columns=["cd"]).copy()
    first = {}
    for r in RC.itertuples():
        cd = json.loads(r.cd)
        for ex in EXITS:
            q = R.simulate(r.entry_price, cd, ex, 0, False, 0, False)
            first.setdefault(ex, []).append(round((q[1] / r.entry_price - 1) * 100, 2) if q else np.nan)
    for ex in EXITS: sig["ret_pct_" + ex] = first[ex]                           # plain return per time exit, no stop / target / gap rule
    sig.sort_values(["date", "stock"]).to_csv(f"{OUT}/signals.csv", index=False)
    ok = S[S.trades >= MIN_TRADES]
    best = (ok if len(ok) else S).sort_values("total_pnl", ascending=False).iloc[0]
    bt = T[(T.exit_rule == best.exit_tag) & (T.sl == best.sl) & (T.gap_rule == best.gap_rule) & (T.tp == best.tp)].sort_values(["entry_date", "stock"])
    bt.to_csv(f"{OUT}/trades_best_variant.csv", index=False)
    bm = bt.assign(month=bt.entry_date.str[:7]).groupby("month").agg(trades=("pnl", "size"), pnl=("pnl", "sum"), win_pct=("pnl", lambda x: round((x > 0).mean() * 100, 1))).reset_index()
    bm.to_csv(f"{OUT}/by_month_best.csv", index=False)
    for metric in ("total_pnl", "roi_pct", "win_pct"):
        pd.concat([matrix(S, metric, ex).assign(exit_rule=R.exit_label(ex)) for ex in EXITS]).to_csv(f"{OUT}/matrix_{metric}.csv", index=False)
    show = ["exit_rule", "stop_loss", "target", "trades", "win_pct", "total_pnl", "roi_pct", "avg_ret_pct", "profit_factor", "max_drawdown", "stop_exits", "target_exits", "gap_rule_exits"]
    L = ["# 5-day-high breakout + Bollinger + prev day green + longer upper wick - LONG ATM call, entry at the breakout day's close, exit on the next morning", "",
         f"**Status:** {status} ({prog})", "", f"**Entry dates:** {START} to {END}  |  **Stocks tried:** {len(UNIVERSE)} F&O stocks  |  **Capital per trade:** up to Rs {CAP:,} (whole lots)", "",
         "## Rules", "", rules_text(), "", "## Funnel", "", "\n".join("- " + x.strip() for x in rep), "",
         f"## Best variant by total PnL (at least {MIN_TRADES} trades)", "", md(S.loc[[best.name], show]), "",
         f"## Top 20 by total PnL (at least {MIN_TRADES} trades)", "", md(ok.sort_values("total_pnl", ascending=False).head(20)[show]), "",
         f"## Top 20 by ROI % (at least {MIN_TRADES} trades)", "", md(ok.sort_values("roi_pct", ascending=False).head(20)[show]), "",
         f"## Top 20 by win % (at least {MIN_TRADES} trades, PnL > 0)", "", md(ok[ok.total_pnl > 0].sort_values(["win_pct", "total_pnl"], ascending=False).head(20)[show]), "",
         "## Best variant of every time exit (by total PnL)", "", md(S.sort_values("total_pnl", ascending=False).drop_duplicates("exit_tag")[show]), "",
         "## Plain return per time exit (no stop, no target, no gap rule)", "",
         md(pd.DataFrame([dict(exit=R.exit_label(ex), trades=int(sig["ret_pct_" + ex].notna().sum()), avg_ret_pct=round(sig["ret_pct_" + ex].mean(), 2), win_pct=round((sig["ret_pct_" + ex].dropna() > 0).mean() * 100, 1)) for ex in EXITS])), "",
         "## By month (best variant)", "", md(bm), ""]
    for ex in EXITS:
        L += [f"## Total PnL (Rs) - exit {R.exit_label(ex)}", "", md(matrix(S, "total_pnl", ex)), "", f"## Win % - exit {R.exit_label(ex)}", "", md(matrix(S, "win_pct", ex)), ""]
    L += ["Charges, taxes and slippage are not included. Lot sizes are today's values. The stock list is today's F&O list. A trade needs an option candle near the close of the breakout day and on the exit day; "
          "the exit candle may be up to 5 minutes away from the asked minute (flagged thin_exit when older). Past results do not promise future results.", ""]
    open(f"{OUT}/SUMMARY.md", "w").write("\n".join(L))
    print("\n".join(L[:14]), flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "check": print_rules(); check()
        elif mode == "run": run()
        elif mode == "summary": print_rules(); summary()
        elif mode == "rules": print_rules()
        else: sys.exit("use: python bo5w_backtest.py check | run | summary | rules")
    except Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
