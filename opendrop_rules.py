"""opendrop_rules.py - the OPEN-DROP RETEST rules (LONG only), pure numpy / pandas (no Dhan, no Yahoo, no engine), so test_opendrop.py can check them against your original script.

Your original script (Yahoo HOURLY candles, Nifty 50 stocks, stock trade, +2 % target, no stop-loss):
  SETUP DAY i   : the FIRST hourly candle of the day (09:15 - 10:15) is red and falls more than 1 % (open -> close).   op_close = close of that first hourly candle.
                  Nifty filter: the NIFTY50 hourly slope (20 candles, value at the first hourly candle of day i) must be >= -0.5.
  DROP DAY      : the first day among i+1 .. i+3 that trades at or below op_close x 0.99 (any hourly Low).
  ENTRY DAY     : the first day among drop_day+1 .. drop_day+5 that trades at or above op_close (any hourly High).  Entry = op_close (a LONG).
  The original only looks at setup days i in range(len(days) - 8) so that all later windows exist.
  Exit (original): +2 % on the stock, else the last hourly close of the entry day.

HERE (options version): the setup day, drop day, entry day and level are exactly the same.  The only changes:
  * the entry is the first 1-MINUTE candle (09:15 .. last allowed minute) of the entry day whose High >= op_close (a gap through the level = 09:15);
  * the trade is the ATM CALL (ITM-1 .. ITM-3 if the ATM has no candle), option price = close of the entry minute, exits on the option premium (SL x TP x time exit).
"""
import numpy as np
import pandas as pd


# ---------------------------------------------------------------- NIFTY50 slope filter (same numbers as the original get_nifty_market_filter)
def rolling_slope(closes, n=20):
    """Slope of the last n closes against 0..n-1, written exactly like the original:  np.cov(x, y)[0, 1] / np.var(x)  (cov uses ddof=1, var ddof=0, so the value is n/(n-1) times the
    plain regression slope; the -0.5 threshold was found with this formula).  NaN for the first n-1 values (like pandas rolling)."""
    c = np.asarray(closes, float); x = np.arange(n); vx = np.var(x)
    out = np.full(len(c), np.nan)
    for k in range(n - 1, len(c)):
        out[k] = np.cov(x, c[k - n + 1:k + 1])[0, 1] / vx
    return out


def nifty_allowed_days(dates, closes, n=20, min_slope=-0.5):
    """dates = date (string) of every hourly candle of the index, closes = its closes (same order).  The slope of a day = the slope at its FIRST candle that has one (pandas groupby.first()
    skips NaN, like the original).  -> set of day strings with slope >= min_slope (days without any slope are not allowed)."""
    s = pd.Series(rolling_slope(closes, n), index=pd.Index(list(dates)))
    d = s.groupby(level=0).first()
    return set(d[d >= min_slope].index.tolist())


# ---------------------------------------------------------------- hourly candles -> one row per day
def daily_from_hourly(df):
    """df = hourly candles (index = candle start, columns Open High Low Close).  -> dict of numpy arrays per trading day, sorted: date (str), fo / fc (open / close of the FIRST hourly candle),
    nb (number of hourly candles), hi / lo (day High / Low).  Day High >= level is the same test as 'some hourly High >= level'."""
    df = df.sort_index()
    key = df.index.strftime("%Y-%m-%d")
    g = df.groupby(key, sort=True)
    return dict(date=np.array(g["Open"].first().index.tolist()), fo=g["Open"].first().values.astype(float), fc=g["Close"].first().values.astype(float),
                nb=g["Close"].size().values.astype(int), hi=g["High"].max().values.astype(float), lo=g["Low"].min().values.astype(float))


# ---------------------------------------------------------------- the daily state machine
def open_drop_setups(day, allowed=None, drop=0.01, fall=0.01, fall_days=3, entry_days=5, tail=8):
    """day = daily_from_hourly(...) (or the same dict built by hand).  allowed = bool per day (NIFTY filter on the SETUP day), None = no filter.
    -> list of dicts: signal (setup day i), drop_day, entry (entry-day index), level (= op_close), drop_pct (the first-candle drop of day i).
    Same loop as the original: i in range(n - tail); the first candle must be red and fall MORE than `drop`; a day needs >= 2 hourly candles to be a setup day;
    drop day = first of i+1..i+fall_days with Low <= op_close*(1-fall); entry day = first of drop_day+1..drop_day+entry_days with High >= op_close."""
    fo, fc, nb, hi, lo = (np.asarray(day[k]) for k in ("fo", "fc", "nb", "hi", "lo"))
    n = len(fo); out = []
    for i in range(n - tail):
        if allowed is not None and not allowed[i]: continue
        if nb[i] < 2: continue
        if fc[i] >= fo[i]: continue
        dp = (fo[i] - fc[i]) / fo[i]
        if dp <= drop: continue
        lvl = float(fc[i]); tgt = lvl * (1 - fall)
        k = -1
        for off in range(1, fall_days + 1):
            if i + off >= n: break
            if lo[i + off] <= tgt: k = i + off; break
        if k < 0: continue
        for off in range(1, entry_days + 1):
            j = k + off
            if j >= n: break
            if hi[j] >= lvl: out.append(dict(signal=i, drop_day=k, entry=j, level=lvl, drop_pct=float(dp))); break
    return out
