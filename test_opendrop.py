"""test_opendrop.py - offline test (no login, no network) of opendrop_rules.py and the opendrop_backtest.py runner.
1. rolling_slope / nifty_allowed_days == your ORIGINAL get_nifty_market_filter maths (copied below) on random hourly index data.
2. open_drop_setups == your ORIGINAL setup / drop / entry loop (copied below) on random hourly stock data (setup day, drop day, entry day, level).
3. hand-made example, the filter, the 'tail' rule, the 'fewer than 2 candles' rule.
4. runner imports with the engine, builds the rule text, the grid and the candidates rows (no network).
"""
import os, sys
import numpy as np, pandas as pd
import opendrop_rules as R


# ---------------------------------------------------------------- 1. NIFTY slope: the original maths
def orig_nifty_days(nifty_df, slope_lookback=20, min_slope=-0.5):
    closes = nifty_df["Close"]
    x = np.arange(slope_lookback)

    def calc_slope(ser):
        if len(ser) < slope_lookback: return 0.0
        y = ser.values
        return np.cov(x, y)[0, 1] / np.var(x)

    nifty_df = nifty_df.copy()
    nifty_df["Slope"] = closes.rolling(window=slope_lookback).apply(calc_slope, raw=False)
    nifty_df["Date"] = nifty_df.index.date
    daily_slope = nifty_df.groupby("Date")["Slope"].first()
    return set(str(d) for d in daily_slope[daily_slope >= min_slope].index.tolist())


def make_hourly(rng, ndays, start="2025-01-01", base=100.0, vol=0.004, bars=7):
    """random hourly candles on business days: bars at 09:15, 10:15 ... 15:15 (like Yahoo NSE)."""
    days = pd.bdate_range(start, periods=ndays)
    idx = [d + pd.Timedelta(hours=9, minutes=15) + pd.Timedelta(hours=h) for d in days for h in range(bars)]
    n = len(idx); c = base * np.exp(np.cumsum(rng.normal(0, vol, n)))
    o = np.r_[c[0], c[:-1]] * np.exp(rng.normal(0, vol / 2, n))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, vol / 2, n))); l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, vol / 2, n)))
    return pd.DataFrame(dict(Open=o, High=h, Low=l, Close=c), index=pd.DatetimeIndex(idx))


rng = np.random.default_rng(11)
for trial in range(30):
    nf = make_hourly(rng, 60, vol=0.003)
    for thr in (-0.5, 0.0, -0.1):
        a = orig_nifty_days(nf, 20, thr)
        b = R.nifty_allowed_days(nf.index.strftime("%Y-%m-%d"), nf.Close.values, 20, thr)
        assert a == b, (trial, thr, sorted(a ^ b)[:5])
print("1. NIFTY slope filter equals the original maths (30 random indices x 3 thresholds)")


# ---------------------------------------------------------------- 2. the original setup loop (detection only, no trade simulation)
def orig_setups(df, allowed_days):
    df = df.copy(); df["Date"] = df.index.date
    grouped = list(df.groupby("Date")); out = []
    for i in range(len(grouped) - 8):
        day_date, day_df = grouped[i]
        if str(day_date) not in allowed_days: continue
        day_df = day_df.sort_index()
        if len(day_df) < 2: continue
        open_candle = day_df.iloc[0]
        if open_candle["Close"] >= open_candle["Open"]: continue
        drop_pct = (open_candle["Open"] - open_candle["Close"]) / open_candle["Open"]
        if drop_pct <= 0.01: continue
        op_close = open_candle["Close"]; target_drop_price = op_close * 0.99
        drop_met = False; drop_day_idx = -1
        for d_offset in range(1, 4):
            if i + d_offset >= len(grouped): break
            check_date, check_df = grouped[i + d_offset]
            if (check_df.sort_index()["Low"] <= target_drop_price).any(): drop_met = True; drop_day_idx = i + d_offset; break
        if not drop_met: continue
        triggered = False
        for e_offset in range(1, 6):
            target_idx = drop_day_idx + e_offset
            if target_idx >= len(grouped): break
            trig_date, trig_day_df = grouped[target_idx]
            for idx, candle in trig_day_df.sort_index().iterrows():
                if candle["High"] >= op_close:
                    out.append((str(day_date), str(grouped[drop_day_idx][0]), str(trig_date), float(op_close))); triggered = True; break
            if triggered: break
    return out


def mine(df, allowed_days):
    day = R.daily_from_hourly(df)
    allowed = np.array([x in allowed_days for x in day["date"]])
    return [(str(day["date"][s["signal"]]), str(day["date"][s["drop_day"]]), str(day["date"][s["entry"]]), s["level"]) for s in R.open_drop_setups(day, allowed, 0.01, 0.01, 3, 5, 8)]


tot = 0
for trial in range(300):
    st = make_hourly(rng, 120, base=500, vol=float(rng.choice([0.004, 0.006, 0.008])))
    nf = make_hourly(rng, 120, vol=0.003)
    allowed = orig_nifty_days(nf, 20, -0.5)
    a, b = orig_setups(st, allowed), mine(st, allowed)
    assert a == b, (trial, a[:3], b[:3])
    tot += len(a)
assert tot > 100, f"too few setups in the random test ({tot})"
print(f"2. setups equal the original loop on 300 random stocks ({tot} setups)")


# ---------------------------------------------------------------- 3. hand-made example
def hand(rows):
    """rows = per day (first open, first close, n candles, high, low)"""
    a = np.array(rows, float)
    return dict(date=np.array([f"2026-02-{i + 2:02d}" for i in range(len(rows))]), fo=a[:, 0], fc=a[:, 1], nb=a[:, 2].astype(int), hi=a[:, 3], lo=a[:, 4])


base = [(100, 98.5, 7, 101, 98.0),      # day 0: first candle red -1.5 %, op_close 98.5, target 97.515
        (98, 98, 7, 99, 97.0),          # day 1: low 97.0 <= 97.515 -> drop day
        (97, 97, 7, 98.0, 96.0),        # day 2: high 98.0 < 98.5 -> no entry
        (97, 97, 7, 98.4, 96.5),        # day 3: no entry (98.4 < 98.5)
        (97, 98, 7, 98.6, 96.8),        # day 4: high 98.6 >= 98.5 -> ENTRY
        ] + [(100, 100, 7, 100.5, 99.5)] * 9
d = hand(base)
s = R.open_drop_setups(d)
assert [(x["signal"], x["drop_day"], x["entry"], x["level"]) for x in s] == [(0, 1, 4, 98.5)], s
assert abs(s[0]["drop_pct"] - 0.015) < 1e-12
# a Nifty filter that blocks day 0 removes it
al = np.ones(len(base), bool); al[0] = False
assert R.open_drop_setups(d, al) == []
# tail rule: only i in range(n - 8)
assert R.open_drop_setups(hand(base[:8])) == [] and len(R.open_drop_setups(hand(base[:9]))) == 1   # n=8 -> range(0); n=9 -> day 0 allowed
# the first candle must fall MORE than 1 %: exactly 1 % is not enough
b2 = list(base); b2[0] = (100, 99.0, 7, 101, 98.0)
assert R.open_drop_setups(hand(b2)) == []
# a green first candle is no setup
b3 = list(base); b3[0] = (100, 101.5, 7, 102, 98.0)
assert R.open_drop_setups(hand(b3)) == []
# a setup day with a single hourly candle is skipped
b4 = list(base); b4[0] = (100, 98.5, 1, 101, 98.0)
assert R.open_drop_setups(hand(b4)) == []
# no drop within 3 days -> no setup;  drop on day 4 is too late
b5 = list(base); b5[1] = (98, 98, 7, 99, 97.6); b5[2] = (97, 97, 7, 98.0, 97.6); b5[3] = (97, 97, 7, 98.4, 97.6); b5[4] = (97, 98, 7, 98.6, 96.0)
assert R.open_drop_setups(hand(b5)) == []
# entry window is 5 days after the drop day: day 1 drop -> days 2..6; entry on day 7 is too late
b6 = list(base); b6[4] = (97, 98, 7, 98.0, 96.8); b6[5] = (97, 97, 7, 98.0, 96.8); b6[6] = (97, 97, 7, 98.0, 96.8); b6[7] = (97, 98, 7, 98.6, 96.8)
assert R.open_drop_setups(hand(b6)) == []
b6[6] = (97, 98, 7, 98.6, 96.8); b6[7] = (97, 98, 7, 98.0, 96.8)
assert [x["entry"] for x in R.open_drop_setups(hand(b6))] == [6]
print("3. hand-made examples ok")

# ---------------------------------------------------------------- 4. the runner imports with the engine (no network)
os.environ.setdefault("OD_OUT", "opendrop_results_test")
import opendrop_backtest as O
assert O.DROP == 0.01 and O.FALL == 0.01 and O.FALL_DAYS == 3 and O.ENTRY_DAYS == 5 and O.TAIL == 8 and O.MIN_SLOPE == -0.5 and O.SLOPE_N == 20
assert O.A.SLS == [0, 20, 40, 60] and O.A.TPS == [40, 60, 80, 120, 0], (O.A.SLS, O.A.TPS)
assert O.A.EXITS == ["09:30", "10:00", "12:00", "15:00", "15:30"], O.A.EXITS
assert len(O.A.VARS) == 5 * 4 * 5, len(O.A.VARS)
assert O.A.STRATS == ["OPENDROP_LONG"] and O.strategies_for("OD", "ODL", -1, -1, -1, -1) == ["OPENDROP_LONG"] and O.strategies_for("GAP", "GAPL", 0, 0, 0, 0) == []
assert "NIFTY50 hourly slope >= -0.5" in O.rules_text() or "slope" in O.rules_text()
# the candidate rows
dd = hand(base); dd["date"] = np.array(pd.bdate_range("2026-02-02", periods=len(base)).strftime("%Y-%m-%d"))
rows, dup = O.setups_to_rows("TEST", dd, None, pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31"))
assert dup == 0 and len(rows) == 1 and rows[0]["direction"] == "LONG" and rows[0]["ref"] == 98.5 and rows[0]["day_offset"] == 4 and rows[0]["drop_pct"] == 1.5 and rows[0]["source"] == "OD", rows
assert rows[0]["date"] == dd["date"][4] and rows[0]["signal_date"] == dd["date"][0] and rows[0]["drop_date"] == dd["date"][1] and rows[0]["yahoo_open"] == 97.0, rows
rows2, _ = O.setups_to_rows("TEST", dd, None, pd.Timestamp("2026-06-01"), pd.Timestamp("2026-12-31"))      # entry day outside the range
assert rows2 == []
# the entry rule: first 1-minute High >= level; SHORT never
idx = pd.date_range("2026-01-05 09:15", periods=6, freq="min")
u = pd.DataFrame(dict(o=[100, 100.5, 101, 101, 101.5, 102], h=[100.4, 100.9, 101.2, 101.6, 102.2, 102.5], l=[99.8, 100.2, 100.6, 100.8, 101.2, 101.7], c=[100.3, 100.8, 101, 101.5, 102, 102.4]), index=idx)
assert O.entries_for(u, 101.5, True) == {"ODL": idx[3]} and O.entries_for(u, 101.5, False) == {} and O.entries_for(u, 120, True) == {}
print("4. runner builds candidates; grid =", len(O.A.VARS), "variants")
import shutil; shutil.rmtree("opendrop_results_test", ignore_errors=True)
print("ALL OK")
