"""Offline test: colab_opendrop_diag scenario A == your ORIGINAL Colab code (nifty_backtest source) on synthetic hourly data (yfinance is faked, no network)."""
import numpy as np, pandas as pd, types, sys, re
import types as _t
yf = _t.ModuleType('yfinance'); sys.modules['yfinance'] = yf          # no network / no install needed: a fake yfinance

ORIG = "/mnt/user-data/uploads/attachment.txt"
src = open(ORIG).read() if len(sys.argv) < 2 else open(sys.argv[1]).read()

def fake_frame(seed, base, vol, drift=0.0, days=330):
    rng = np.random.default_rng(seed); idx = []
    d = pd.bdate_range("2025-11-13", periods=days)
    for day in d:
        for h in range(7):
            idx.append(pd.Timestamp(day.strftime("%Y-%m-%d") + " 03:45") + pd.Timedelta(hours=h))   # 09:15 IST + h hours, stored as UTC
    idx = pd.DatetimeIndex(idx).tz_localize("UTC")
    r = rng.normal(drift, vol, len(idx)); c = base * np.exp(np.cumsum(r)); o = np.r_[base, c[:-1]] * (1 + rng.normal(0, vol / 2, len(idx)))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, vol / 2, len(idx)))); l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, vol / 2, len(idx))))
    return pd.DataFrame(dict(Open=o, High=h, Low=l, Close=c, Volume=1000), index=idx)

def fake_download(tk, *a, **k):
    if tk == "^NSEI": return fake_frame(1, 20000, 0.003, 0.00002)
    return fake_frame(abs(hash(tk)) % 10000 + 5, 500, 0.008)
yf.download = fake_download

# the original code, without the !pip line and the final call; capture its trades table
code = src.replace("!pip install yfinance pandas numpy -q", "").replace("\nrun_backtest()\n", "\n")
code = code.replace("    trades_df = pd.DataFrame(all_trades)\n", "    trades_df = pd.DataFrame(all_trades); globals()['_TRADES'] = trades_df\n")
ns = {"__name__": "orig"}; exec(compile(code, "orig", "exec"), ns)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()): ns["run_backtest"]()
O = ns["_TRADES"].sort_values(["Ticker", "Setup_Date", "Entry_Date"]).reset_index(drop=True)

import colab_opendrop_diag as D
syms = ns["nifty_symbols"]
tr = D.run(syms)
M = pd.DataFrame([dict(Ticker=t["Ticker"], Setup_Date=t["Setup_Date"], Entry_Date=t["Entry_Date"], Return_Pct=D.simulate(t, "level", 2, "entry")[0],
                       st=D.simulate(t, "level", 2, "entry")[1]) for t in tr]).sort_values(["Ticker", "Setup_Date", "Entry_Date"]).reset_index(drop=True)
print("original trades", len(O), " diag scenario A trades", len(M))
assert len(O) > 25, "too few synthetic trades for a real test"
assert list(O.Ticker) == list(M.Ticker) and list(O.Setup_Date) == list(M.Setup_Date) and list(O.Entry_Date) == list(M.Entry_Date)
assert np.allclose(O.Return_Pct.values, M.Return_Pct.values, atol=0.011), (O.Return_Pct.values - M.Return_Pct.values)
assert ((O.Return_Pct == 2.0) == (M.st == "TP")).all()
print("win % original", round((O.Return_Pct > 0).mean() * 100, 1), " diag A", round((M.Return_Pct > 0).mean() * 100, 1))
D.report(tr)
print("ALL OK")
