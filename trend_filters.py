"""trend_filters.py - the 5 trend filters + the BPB state machine (pure numpy/pandas, no broker / engine imports, tested offline).

Every filter is evaluated on DAILY candles at the CLOSE of the signal day (the day before the entry day) -> no look-ahead.
Every filter is DIRECTION-AWARE: a LONG (buy CALL) trade needs an UP-trend, a SHORT (buy PUT) trade needs a DOWN-trend.
Not enough history (NaN) = the filter does NOT pass.

  MA50    close above (LONG) / below (SHORT) the 50-day simple average
  MA2050  20-day average above (LONG) / below (SHORT) the 50-day average          (moving-average stack)
  ROC10   close above (LONG) / below (SHORT) the close 10 days ago                (momentum direction)
  ADXDI   ADX(14) >= 20 AND +DI > -DI (LONG) / -DI > +DI (SHORT)                  (a trend that has strength)
  STRUCT  market structure over 10-day blocks: higher high + higher low (LONG) / lower high + lower low (SHORT)
"""
import numpy as np, pandas as pd

TRENDS = ["MA50", "MA2050", "ROC10", "ADXDI", "STRUCT"]


def _sma(x, n): return pd.Series(x).rolling(n).mean().values


def _wilder(x, n):
    out = np.full(len(x), np.nan)
    if len(x) < n: return out
    out[n - 1] = x[:n].sum()
    for i in range(n, len(x)): out[i] = out[i - 1] - out[i - 1] / n + x[i]
    return out


def adx_di(H, L, C, n=14):
    """Wilder ADX / +DI / -DI -> three arrays (NaN until enough candles)."""
    N = len(C); pdi, mdi, adx = (np.full(N, np.nan) for _ in range(3))
    if N < 2 * n + 1: return pdi, mdi, adx
    up, dn = H[1:] - H[:-1], L[:-1] - L[1:]
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = np.maximum.reduce([H[1:] - L[1:], np.abs(H[1:] - C[:-1]), np.abs(L[1:] - C[:-1])])
    st, sp, sm = _wilder(tr, n), _wilder(pdm, n), _wilder(mdm, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        p, m = 100 * sp / st, 100 * sm / st
        dx = 100 * np.abs(p - m) / (p + m)
    a = np.full(len(dx), np.nan)
    a[2 * n - 2] = np.nanmean(dx[n - 1:2 * n - 1])
    for i in range(2 * n - 1, len(dx)): a[i] = (a[i - 1] * (n - 1) + dx[i]) / n
    pdi[1:], mdi[1:], adx[1:] = p, m, a
    return pdi, mdi, adx


def trend_flags(O, H, L, C):
    """{filter: (long_ok[], short_ok[])} - boolean arrays, one value per daily candle (value at that candle's close)."""
    H, L, C = (np.asarray(x, float) for x in (H, L, C)); N = len(C)
    s20, s50 = _sma(C, 20), _sma(C, 50)
    roc = np.full(N, np.nan)
    if N > 10: roc[10:] = C[10:] - C[:-10]
    pdi, mdi, adx = adx_di(H, L, C)
    rh, rl = pd.Series(H).rolling(10).max().values, pd.Series(L).rolling(10).min().values
    prh, prl = np.r_[np.full(10, np.nan), rh[:-10]][:N], np.r_[np.full(10, np.nan), rl[:-10]][:N]
    with np.errstate(invalid="ignore"):
        return {
            "MA50":   (C > s50, C < s50),
            "MA2050": (s20 > s50, s20 < s50),
            "ROC10":  (roc > 0, roc < 0),
            "ADXDI":  ((adx >= 20) & (pdi > mdi), (adx >= 20) & (mdi > pdi)),
            "STRUCT": ((rh > prh) & (rl > prl), (rh < prh) & (rl < prl)),
        }


def bpb_entries(O, H, L, C, long, lookback=10):
    """BPB state machine (same as breakout_armed() in shape_live_plan.py / find_setups() of bpb_fno_backtest.py) run over the WHOLE history.
    -> [(entry day index, line, entry level)].  The entry day is a day on which price reaches the entry level after a confirmed pullback.
    SHORT = the mirror (negated prices, negated back)."""
    O, H, L, C = (np.asarray(x, float) for x in (O, H, L, C))
    if not long: O, H, L, C = -O, -L, -H, -C
    n = len(C); ref = np.full(n, np.nan)
    for i in range(lookback, n): ref[i] = H[i - lookback:i].max()
    sg = 1.0 if long else -1.0
    out, st = [], None                                    # st = [line, highest high since breakout, bearish seen]
    for i in range(lookback, n):
        if st is not None and st[2] and H[i] >= st[1]:
            out.append((i, sg * st[0], sg * st[1])); st = None          # entry day -> setup used up
        elif st is not None and st[2]:
            if C[i] < st[0]: st = None
            continue
        elif st is not None:
            if C[i] < st[0]: st = None
            else:
                st[1] = max(st[1], H[i])
                if C[i] < O[i]: st[2] = True
                continue
        if st is None and C[i] > ref[i]: st = [ref[i], H[i], False]
    return out
