"""colab_opendrop_diag.py - WHY is the win rate of the open-drop retest lower than your Colab 70 %?   Stock-only, Yahoo hourly, same 15 stocks as your Colab file.

Run in Colab:
    !pip install yfinance pandas numpy -q
    !wget -q https://raw.githubusercontent.com/pkjha1010/Dhan/main/colab_opendrop_diag.py
    %run colab_opendrop_diag.py
(or paste this file into one cell).  Needs only Yahoo - no Dhan login.

STEP 1  SETUP + ENTRY = exactly your Colab code (NIFTY slope >= -0.5, first hourly candle red > 1 %, drop day within 3 days, first hourly candle with High >= op_close within 5 days).
        The first hourly candle that crosses the level is the entry candle (one entry per setup).  Scenario A must give your 58 trades / 70.7 % win rate.
STEP 2  The SAME trades are re-simulated with one change at a time, so the drop in win rate is split into its causes:
        A  original              fill at the level, +2 % target checked from the entry candle (its own High counts), exit = last hourly close of the day
        B  real fill             if the entry candle OPENS above the level (gap through), the fill is the open, not the level
        C  B + target later      target only checked from the candle AFTER the entry candle (the entry candle's High may have come before the cross)
        D  A, no target          win = day close > level   (comparable with the option 15:30 / no-TP win rate)
        E  B, no target          win = day close > real fill
        F  B with +1 % / +3 % target
STEP 3  Breakdown of the scenario-A wins (gap-instant / same-candle / later target / EOD) and win % by entry candle (first hourly candle = 09:15-10:15 vs later).
STEP 4  (optional) the stock trades are joined with the Dhan option trades (15:30 exit, no SL, no TP) from GitHub: stock return vs option return per trade.
Set FIRST_HOUR_ONLY = True to keep only trades whose cross happened in the first hourly candle (09:15-10:15).
"""
import numpy as np, pandas as pd
import yfinance as yf

SYMBOLS = ["SBIN.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "ITC.NS", "AXISBANK.NS", "LT.NS", "KOTAKBANK.NS",
           "BHARTIARTL.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS"]
PERIOD = "1y"
SLOPE_N, MIN_SLOPE = 20, -0.5
FIRST_HOUR_ONLY = False
DHAN_TRADES_URL = "https://raw.githubusercontent.com/pkjha1010/Dhan/main/opendrop_results/long/trades_all_variants.csv.gz"   # step 4 (skipped if unreachable)


def _clean(df):
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.dropna().copy()
    df.index = df.index.tz_convert("Asia/Kolkata") if df.index.tz is not None else df.index.tz_localize("UTC").tz_convert("Asia/Kolkata")
    return df


def nifty_allowed_days(period=PERIOD, n=SLOPE_N, min_slope=MIN_SLOPE):
    """Same as your get_nifty_market_filter."""
    nd = _clean(yf.download("^NSEI", period=period, interval="1h", progress=False))
    x = np.arange(n)
    def calc_slope(ser):
        if len(ser) < n: return 0.0
        return np.cov(x, ser.values)[0, 1] / np.var(x)
    nd["Slope"] = nd["Close"].rolling(window=n).apply(calc_slope, raw=False)
    nd["Date"] = nd.index.date
    ds = nd.groupby("Date")["Slope"].first()
    return set(ds[ds >= min_slope].index.tolist())


def find_trades(ticker, df, allowed):
    """Your original loops.  One record per setup that reaches an entry; 'sub' = hourly candles from the entry candle to the end of the entry day."""
    df = df.copy(); df["Date"] = df.index.date
    grouped = list(df.groupby("Date")); out = []
    for i in range(len(grouped) - 8):
        day_date, day_df = grouped[i]
        if day_date not in allowed: continue
        day_df = day_df.sort_index()
        if len(day_df) < 2: continue
        oc = day_df.iloc[0]
        if oc["Close"] >= oc["Open"]: continue
        if (oc["Open"] - oc["Close"]) / oc["Open"] <= 0.01: continue
        lvl = oc["Close"]; tgt_drop = lvl * 0.99
        drop_idx = -1
        for d in range(1, 4):
            if i + d >= len(grouped): break
            cd = grouped[i + d][1].sort_index()
            if (cd["Low"] <= tgt_drop).any(): drop_idx = i + d; break
        if drop_idx < 0: continue
        done = False
        for e in range(1, 6):
            t = drop_idx + e
            if t >= len(grouped): break
            tdate, tdf = grouped[t]; tdf = tdf.sort_index()
            for k in range(len(tdf)):
                if tdf.iloc[k]["High"] >= lvl:
                    out.append(dict(Ticker=ticker, Setup_Date=str(day_date), Entry_Date=str(tdate), level=float(lvl), cross_candle=k, cross_time=tdf.index[k].strftime("%H:%M"),
                                    sub=tdf.iloc[k:][["Open", "High", "Low", "Close"]].copy()))
                    done = True; break
            if done: break
    return out


def simulate(tr, fill="level", tp=2.0, tp_from="entry"):
    """-> (return %, status).  fill: 'level' (original) or 'real' (gap through -> open).  tp = % target (0 = none).  tp_from: 'entry' (original, entry candle's High counts) or 'next'."""
    sub, lvl = tr["sub"], tr["level"]
    entry = lvl if fill == "level" else max(lvl, float(sub.iloc[0]["Open"]))
    if tp:
        tgt = entry * (1 + tp / 100.0)
        chk = sub if tp_from == "entry" else sub.iloc[1:]
        if (chk["High"] >= tgt).any(): return round(tp, 2), "TP"
    return round((float(sub.iloc[-1]["Close"]) - entry) / entry * 100, 2), "EOD"


def run(symbols=SYMBOLS, period=PERIOD):
    allowed = nifty_allowed_days(period)
    trades = []
    for s in symbols:
        df = yf.download(s, period=period, interval="1h", progress=False)
        if df is None or df.empty or len(df) < 50: continue
        trades += find_trades(s, _clean(df), allowed)
    return trades


SCENARIOS = [("A original (fill at level, +2% from entry candle, EOD exit)", dict(fill="level", tp=2, tp_from="entry")),
             ("B real fill (gap through -> open)", dict(fill="real", tp=2, tp_from="entry")),
             ("C B + target checked only AFTER the entry candle", dict(fill="real", tp=2, tp_from="next")),
             ("D A without target (close > level)", dict(fill="level", tp=0)),
             ("E B without target (close > real fill)", dict(fill="real", tp=0)),
             ("F1 B, +1 % target", dict(fill="real", tp=1, tp_from="entry")),
             ("F3 B, +3 % target", dict(fill="real", tp=3, tp_from="entry"))]


def report(trades):
    if FIRST_HOUR_ONLY: trades = [t for t in trades if t["cross_candle"] == 0]
    n = len(trades); print(f"\nTrades (setup -> entry candle): {n}   FIRST_HOUR_ONLY={FIRST_HOUR_ONLY}")
    if not n: return None
    rows = []
    for name, kw in SCENARIOS:
        r = [simulate(t, **kw) for t in trades]; ret = np.array([x[0] for x in r])
        rows.append(dict(scenario=name, trades=n, win_pct=round((ret > 0).mean() * 100, 1), avg_ret=round(ret.mean(), 2), tp_hits=sum(x[1] == "TP" for x in r)))
    print("\n== 1. SCENARIOS (same trades, one change at a time) =="); print(pd.DataFrame(rows).to_string(index=False))

    # breakdown of scenario A
    gi = sc = lt = eodw = eodl = 0
    for t in trades:
        ret, st = simulate(t, "level", 2, "entry"); sub, lvl = t["sub"], t["level"]; tgt = lvl * 1.02
        if st == "TP":
            if sub.iloc[0]["Open"] >= tgt: gi += 1
            elif sub.iloc[0]["High"] >= tgt: sc += 1
            else: lt += 1
        elif ret > 0: eodw += 1
        else: eodl += 1
    print("\n== 2. WHERE THE SCENARIO-A WINS COME FROM ==")
    print(f"target hit because the entry candle OPENED >= +2 % above the level (instant, gap): {gi}")
    print(f"target hit inside the entry candle itself (High, order unknown):                  {sc}")
    print(f"target hit in a later candle:                                                      {lt}")
    print(f"EOD exit, close above level (win):                                                 {eodw}")
    print(f"EOD exit, close at / below level (loss):                                           {eodl}")

    # by entry candle
    print("\n== 3. WIN % BY ENTRY CANDLE (first hourly candle = 09:15-10:15) ==")
    rows = []
    for lab, f in (("cross in FIRST hourly candle", lambda t: t["cross_candle"] == 0), ("cross in a later candle", lambda t: t["cross_candle"] > 0)):
        g = [t for t in trades if f(t)]
        if not g: continue
        a = np.array([simulate(t, "level", 2, "entry")[0] for t in g]); b = np.array([simulate(t, "real", 2, "entry")[0] for t in g]); e = np.array([simulate(t, "real", 0)[0] for t in g])
        rows.append(dict(group=lab, trades=len(g), A_win=round((a > 0).mean() * 100, 1), B_win=round((b > 0).mean() * 100, 1), E_noTP_win=round((e > 0).mean() * 100, 1)))
    print(pd.DataFrame(rows).to_string(index=False))

    # table of trades (scenario A like your csv + scenario B / E)
    T = pd.DataFrame([dict(Ticker=t["Ticker"], Setup_Date=t["Setup_Date"], Entry_Date=t["Entry_Date"], level=round(t["level"], 2), cross_time=t["cross_time"],
                           entry_candle_open=round(float(t["sub"].iloc[0]["Open"]), 2),
                           A_ret=simulate(t, "level", 2)[0], A_status=simulate(t, "level", 2)[1], B_ret=simulate(t, "real", 2)[0], E_ret=simulate(t, "real", 0)[0]) for t in trades])
    T.to_csv("diag_trades.csv", index=False)
    print("\nsaved diag_trades.csv  (compare scenario A with your nifty_long_trades_log.csv)")
    return T


def join_dhan(T):
    try:
        D = pd.read_csv(DHAN_TRADES_URL)
    except Exception as ex:
        print("\n(step 4 skipped: could not read the Dhan trades:", str(ex)[:80], ")"); return
    D = D[(D.exit_rule == "15:30") & (D.sl == 0) & (D.tp == 0)][["stock", "entry_date", "entry_time", "entry_price", "ret_pct"]]
    T = T.assign(stock=T.Ticker.str.replace(".NS", "", regex=False))
    J = T.merge(D, left_on=["stock", "Entry_Date"], right_on=["stock", "entry_date"], how="inner").rename(columns={"ret_pct": "option_ret"})
    print(f"\n== 4. STOCK vs OPTION on the same trades (Dhan option, 15:30 exit, no SL / TP): {len(J)} of {len(T)} trades have option results ==")
    if J.empty: return
    print(f"stock win % (E, no TP): {(J.E_ret > 0).mean() * 100:.1f}   option win %: {(J.option_ret > 0).mean() * 100:.1f}   same win/loss: {((J.E_ret > 0) == (J.option_ret > 0)).sum()} of {len(J)}")
    print(f"avg stock return {J.E_ret.mean():.2f} %   avg option return {J.option_ret.mean():.2f} %")
    print(J[["Ticker", "Entry_Date", "cross_time", "entry_time", "A_ret", "E_ret", "option_ret"]].to_string(index=False))


if __name__ == "__main__":
    tr = run()
    T = report(tr)
    if T is not None: join_dhan(T)
