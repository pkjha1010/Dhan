"""Offline checks for mr_poc_backtest.py on synthetic data (no Dhan login needed).  Run:  python test_mr_poc.py"""
import os
os.environ["MR_START"] = "2026-01-01"; os.environ["MR_END"] = "2026-12-31"
import numpy as np, pandas as pd
from datetime import date, timedelta
import mr_poc_backtest as M


def session(day, prices, vols):
    ix = pd.date_range(f"{day} 09:15", periods=375, freq="min")
    p = np.asarray(prices, float)
    return pd.DataFrame({"o": p, "h": p + .3, "l": p - .3, "c": np.r_[p[1:], p[-1]], "volume": vols}, index=ix)


def make(mirror=False, n_days=40):
    days = [d.date() for d in pd.bdate_range("2026-06-01", periods=n_days)]
    parts, t = [], np.arange(375)
    for k, d in enumerate(days):
        if k < 34 or k > 35:                                            # sideways: sine wave 992..1008, even volume
            p, v = 1000 + 8 * np.sin(2 * np.pi * t / 150 + k), np.full(375, 1000.0)
        elif k == 34:                                                   # setup day: gap-down into thin zone, climbs to POC, red last hour
            p = np.r_[np.full(60, 975.0) + np.linspace(0, 10, 60), np.linspace(985, 998, 120), 998.5 + 0.2 * np.sin(t[180:315]), np.linspace(999, 996.6, 60)]
            v = np.where((t >= 180) & (t < 315), 3000.0, 600.0)
        else:                                                           # trade day: flat, then breaks Day-1 high at 09:20
            p = np.r_[np.full(5, 998.0), np.full(370, 1001.0)]; v = np.full(375, 1000.0)
        if mirror: p = 2000 - p
        parts.append(session(d, p, v))
    df = pd.concat(parts)
    if mirror: df[["h", "l"]] = df[["l", "h"]].values
    return M.clean(df), days


def test_setup_and_signal(mirror):
    df, days = make(mirror)
    st, fun = M.scan_setups(df)
    side = "SHORT" if mirror else "LONG"
    print(side, "funnel:", fun[side]); print(st.T if len(st) else "no setups")
    assert len(st) == 1 and st.direction.iloc[0] == side and st.setup_date.iloc[0] == str(days[34]), "setup not found"
    r = st.iloc[0]
    g1 = df[df.index.date == days[35]]
    lvl = r.day_low if mirror else r.day_high
    sig = M.entry_signal(g1, lvl, not mirror)
    assert sig is not None and sig[0].strftime("%H:%M") == "09:20", sig
    print(side, "entry:", sig)


def fake_option(strike_move=False, crash=False):
    ix = pd.date_range("2026-07-27 09:15", periods=375, freq="min")
    c = np.full(375, 20.0)
    if crash: c[7:] = 17.0                                              # 09:22 candle falls 15 %
    df = pd.DataFrame({"o": c, "h": c + .2, "l": c - .2, "c": c, "strike": 1000.0}, index=ix)
    if crash: df.loc[ix[7], "l"] = 17.0
    def fetch(dh, sid, d0, d1, side, off):
        x = df.copy()
        if strike_move:
            if off == 0: x.loc[x.index >= "2026-07-27 09:24", "strike"] = 1050.0
            else:
                if off == 1: return None
                x = x[x.index >= "2026-07-27 09:24"]                    # neighbour series still carries strike 1000
        elif off != 0: return None
        return x
    return fetch


def test_option():
    ts = pd.Timestamp("2026-07-27 09:20"); d = date(2026, 7, 27)
    s, x = M.option_trade(1, 100, "LONG", d, ts, fetch=fake_option(crash=True)); print(x)
    assert s == "ok" and x["exit_reason"].startswith("STOP") and abs(x["exit_price"] - 18.0) < 1e-6 or x["exit_price"] == 17.0, x
    s, x = M.option_trade(1, 100, "LONG", d, ts, fetch=fake_option()); print(x)
    assert s == "ok" and x["exit_reason"] == "TIME" and x["exit_time"] == "09:29" and x["entry_time"] == "09:20", x
    s, x = M.option_trade(1, 100, "LONG", d, ts, fetch=fake_option(strike_move=True)); print(x)
    assert s == "ok" and x["strike"] == 1000.0 and x["option_coverage"] > 0.9, x
    s, x = M.option_trade(1, 100, "LONG", d, pd.Timestamp("2026-07-27 09:29"), fetch=fake_option()); print(s, x)
    assert s == "skip"


if __name__ == "__main__":
    test_setup_and_signal(False); test_setup_and_signal(True); test_option(); print("ALL OK")
