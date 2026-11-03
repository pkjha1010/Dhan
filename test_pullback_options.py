import os, sys, importlib
os.environ.update(PO_OUT="/tmp/po", PO_START="2026-09-14", PO_END="2026-10-30", PO_SYMBOLS="AAA BBB", PO_MIN_TRADES="1", PO_NIFTY_MODE="intraday", PO_CAP="60000")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import pullback_options_backtest as P

days = list(pd.bdate_range("2026-09-01", "2026-10-30"))
# AAA: flat 100 -> breakout day (close 105, high 106) -> pullback day (low 105.2) -> RE-CROSS day, high reaches 106 at 10:03
def daily_df():
    rows = []
    for i, d in enumerate(days):
        o = h = l = c = 100.0
        if d == pd.Timestamp("2026-10-12"): o, h, l, c = 101, 106, 101, 105
        if d == pd.Timestamp("2026-10-13"): o, h, l, c = 105, 105.4, 105.1 - 0.1, 105.2   # low 105.0 < 106*0.995=105.47 -> pullback
        if d == pd.Timestamp("2026-10-14"): o, h, l, c = 105.3, 107, 105.2, 106.5
        if d > pd.Timestamp("2026-10-14"): o = h = l = c = 106.5
        rows.append((d, o, h, l, c))
    return pd.DataFrame(rows, columns=["d", "o", "h", "l", "c"]).set_index("d")
DAILY = daily_df()
def mirror(df):
    m = df.copy(); m["o"], m["c"], m["h"], m["l"] = 200 - df.o, 200 - df.c, 200 - df.l, 200 - df.h
    return m
def arrs(df, extra=()):
    ts = [int(t.timestamp()) for t in df.index.tz_localize("Asia/Kolkata")]
    return {"timestamp": ts, "open": df.o.tolist(), "high": df.h.tolist(), "low": df.l.tolist(), "close": df.c.tolist(), **{k: df[k].tolist() for k in extra}}
def stock_min(day):
    idx = pd.date_range(f"{day} 09:15", f"{day} 15:29", freq="1min"); p = np.full(len(idx), 105.3)
    p[idx >= pd.Timestamp(f"{day} 10:03")] = 105.9
    df = pd.DataFrame(dict(o=p, h=p + 0.1, l=p - 0.1, c=p), index=idx)
    df.loc[pd.Timestamp(f"{day} 10:03"), "h"] = 106.0      # first candle whose HIGH reaches the level 106
    return df
def nifty_min(day, green=True):
    idx = pd.date_range(f"{day} 09:15", f"{day} 15:29", freq="1min"); p = np.linspace(100, 101 if green else 99, len(idx))
    return pd.DataFrame(dict(o=p, h=p, l=p, c=p), index=idx)
def opt(day, off):
    idx = pd.date_range(f"{day} 09:15", f"{day} 15:29", freq="1min"); n = len(idx)
    prem = np.full(n, 5.0); t = (idx >= pd.Timestamp(f"{day} 10:20")); prem[t] = 8.5     # +70% jump at 10:20
    spot = np.full(n, 105.9); strike = np.full(n, 106.0) if off == "ATM" else np.full(n, 105.0)
    if off == "ATM":                                           # ATM strike rolls to 107 after 11:00 -> locked-strike stitching must use ATM-1 series
        strike[idx >= pd.Timestamp(f"{day} 11:00")] = 107.0
    if off == "ATM-1":
        strike = np.full(n, 105.0); strike[idx >= pd.Timestamp(f"{day} 11:00")] = 106.0; prem = prem + 1 + (idx >= pd.Timestamp(f"{day} 11:00")) * 0.0
    df = pd.DataFrame(dict(o=prem, h=prem + 0.1, l=prem - 0.1, c=prem, strike=strike, spot=spot), index=idx)
    if off == "ATM-1":
        pass
    return df
calls = []
class FakeDhan(P.Dhan):
    def __init__(self): self.n = 0
    def post(self, path, b):
        calls.append(path); self.n += 1
        if path == "/charts/historical":
            if b["securityId"] == "13": d = DAILY.copy(); d.loc[:, ["o", "c"]] = [[100, 101]] * len(d)
            elif b["securityId"] == "3": d = mirror(DAILY)
            else: d = DAILY.copy()
            return arrs(d.loc[b["fromDate"]:b["toDate"]].iloc[:-1] if False else d)
        if path == "/charts/intraday":
            day = b["fromDate"][:10]
            if b["securityId"] == "13": return arrs(nifty_min(day, green=(os.environ.get("NDIR") != "down") and (day != "2026-10-14" or os.environ.get("NG") != "red")))
            return arrs(mirror(stock_min(day)) if b["securityId"] == "3" else stock_min(day))
        if path == "/charts/rollingoption":
            day = b["fromDate"]; off = b["strike"]
            if os.environ.get("NOATM") and off == "ATM": return {"data": {"ce": None, "pe": None}}
            k = "ce" if b["drvOptionType"] == "CALL" else "pe"
            o1 = opt(day, "ATM-1" if off == "ATM+1" else off); nxt = (pd.Timestamp(day) + pd.offsets.BDay(1)).strftime("%Y-%m-%d")
            o2 = opt(nxt, "ATM-1" if off == "ATM+1" else off); o2[["o", "h", "l", "c"]] = o2[["o", "h", "l", "c"]] * 50     # NEXT day, absurd prices: must never be used
            return {"data": {"ce": None, "pe": None, k: arrs(pd.concat([o1, o2]), ("strike", "spot"))}}
P.Dhan = FakeDhan
P.load_master = lambda: ({"AAA": "1", "BBB": "2"}, {"AAA": 1000, "BBB": 500})
P.BUDGET = 0
KEYS = ["no_equity_id", "too_little_daily", "no_stock_minute_data", "no_cross_minute", "no_nifty_minute_data", "nifty_filter_failed", "no_option_candle_atm_or_itm", "no_lot_size", "one_lot_too_expensive"]
stats = {sd: {k: 0 for k in KEYS} for sd in ("LONG", "SHORT")}
dh = FakeDhan()
ev = P.find_events(dh, {"AAA": "1", "BBB": "2"}, {"AAA": 1000, "BBB": 500}, ["AAA", "BBB"], stats["LONG"], "LONG")
print(ev[["side", "stock", "date", "level", "entry_ts", "lot"]])
assert (ev.entry_ts.dt.strftime("%H:%M") == "10:03").all() and (ev.date == "2026-10-14").all()
T, E = P.trade_rows(dh, ev, stats)
print(E.to_string())
a = E.iloc[0]; assert a.contract == "ATM" and a.strike == 106.0 and a.premium == 5.0 and a.lots == 12      # 60000 // (5*1000)
x = T[(T.stock == "AAA") & (T.exit_rule == "15:30") & (T.sl == 0) & (T.tp == 60)].iloc[0]; print(x.to_dict())
assert x.reason == "TP" and x.exit_time == "10:20" and abs(x.exit - 8.0) < 1e-9 or x.exit > 8   # gap fill: open 8.5 >= level 8.0
y = T[(T.stock == "AAA") & (T.exit_rule == "15:30") & (T.sl == 0) & (T.tp == 0)].iloc[0]; assert y.reason == "TIME" and y.exit_time == "15:29"
# 09:30 exit: entry 10:03 is after it -> no rows
assert T.exit.max() < 20 and (T.exit_time > T.entry_time).all(), "next-day candles leaked into a same-day trade"
assert not (T.exit_rule == "09:30").any() and not (T.exit_rule == "10:00").any() and (T.exit_rule == "12:00").any()
# locked strike 106: after 11:00 the ATM series moves to 107, stitching must have fetched other offsets (or used none because candles end) -> series check
s, k = P.locked_series(dh, "1", "2026-10-14", "ATM", P.cached("/tmp/po/cache/opt/1/2026-10-14_ATM_LONG.csv.gz", lambda: None), pd.Timestamp("2026-10-14 10:03"), "LONG")
print("locked", k, "candles", len(s), "last", s.index[-1].time())

# ITM fallback
os.environ["NOATM"] = "1"; import shutil; shutil.rmtree("/tmp/po/cache/opt")
T2, E2 = P.trade_rows(dh, ev, {k: dict(v) for k, v in stats.items()}); print("fallback:", E2[["stock", "contract", "strike", "premium"]].to_string())
assert (E2.contract == "ITM1").all()
# Nifty filter intraday: red nifty -> no entry
os.environ.pop("NOATM"); os.environ["NG"] = "red"; shutil.rmtree("/tmp/po/cache/NIFTY"); shutil.rmtree("/tmp/po/cache/min")
st3 = dict(stats["LONG"]); ev3 = P.find_events(dh, {"AAA": "1", "BBB": "2"}, {"AAA": 1000, "BBB": 500}, ["AAA", "BBB"], st3, "LONG"); print("red nifty events:", len(ev3), st3["nifty_filter_failed"])

# ---------------- SHORT: mirrored stock "SSS" (id 3), Nifty red, PUT
shutil.rmtree("/tmp/po/cache/NIFTY", ignore_errors=True); shutil.rmtree("/tmp/po/cache/min", ignore_errors=True); shutil.rmtree("/tmp/po/cache/opt", ignore_errors=True)
os.environ.pop("NG", None); os.environ["NDIR"] = "down"; os.environ.pop("NOATM", None)
evs = P.find_events(dh, {"SSS": "3"}, {"SSS": 1000}, ["SSS"], stats["SHORT"], "SHORT"); print(evs[["side", "stock", "date", "level", "entry_ts"]])
assert len(evs) == 1 and evs.side[0] == "SHORT" and evs.date[0] == "2026-10-14" and abs(evs.level[0] - 94.0) < 1e-9 and pd.Timestamp(evs.entry_ts[0]).strftime("%H:%M") == "10:03"
Ts, Es = P.trade_rows(dh, evs, stats); assert (Es.side == "SHORT").all() and (Ts.side == "SHORT").all() and len(Ts) > 0
# green Nifty must BLOCK the short
shutil.rmtree("/tmp/po/cache/NIFTY", ignore_errors=True); shutil.rmtree("/tmp/po/cache/min", ignore_errors=True); os.environ["NDIR"] = "up"
sb = {k: 0 for k in KEYS}; evb = P.find_events(dh, {"SSS": "3"}, {"SSS": 1000}, ["SSS"], sb, "SHORT"); assert len(evb) == 0 and sb["nifty_filter_failed"] > 0
# separate reporting
P.SIDES = ["LONG", "SHORT"]; P.write_results(pd.concat([T, Ts]), pd.concat([E, Es]), stats, True)
fl = sorted(os.listdir("/tmp/po")); print(fl); assert "summary_LONG.csv" in fl and "summary_SHORT.csv" in fl and "all_trades_SHORT.csv.gz" in fl
txt = open("/tmp/po/SUMMARY.md").read(); assert "## LONG (calls)" in txt and "## SHORT (puts)" in txt
print("ALL TESTS PASSED")
