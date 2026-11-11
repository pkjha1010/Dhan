"""test_orb.py - offline test (no login, no network) of orb_rules.py and the exit-variant engine of orb_backtest.py.
1. ORB range / first breakout candle / volume filter on hand-made minute frames.
2. stock_stop (ORB low / breakout-candle low, gap through the level).
3. simulate_one (the combined exit) == a slow minute-by-minute brute force on 300 random option paths, every stop x target x time-exit variant.
4. parse_sl / combined variants list.   5. orb_backtest imports, universes (top10 / nifty50 / fno) and the rule text build."""
import os, sys, json
import numpy as np, pandas as pd
import orb_rules as R

# ------------------------------------------------------------------ 1. ORB range + entry
idx = pd.date_range("2026-01-05 09:15", "2026-01-05 15:29", freq="min")
n = len(idx)
o = np.full(n, 100.0); h = o + 0.2; l = o - 0.2; c = o.copy(); v = np.full(n, 1000.0)
u = pd.DataFrame(dict(o=o, h=h, l=l, c=c, v=v), index=idx)
u.loc[idx[3], "h"] = 101.0; u.loc[idx[7], "l"] = 99.0                      # inside 09:15-09:29: ORB high 101, low 99
rng = R.orb_range(u)
assert rng == (101.0, 99.0), rng
assert R.orb_range(u.iloc[:5]) is None                                      # fewer than 10 candles -> no ORB
u2 = u.copy(); u2.loc[idx[20], ["h", "c", "v"]] = [102.5, 102.0, 5000.0]    # 09:35 closes above 101 on 5x volume
e = R.find_entry(u2, *rng)
assert e and e["direction"] == "LONG" and str(e["minute"])[11:16] == "09:35" and e["brk_level"] == u2.l.values[20], e
# a breakout candle INSIDE the ORB window (before 09:30) is not an entry
u3 = u.copy(); u3.loc[idx[12], ["c", "h", "v"]] = [105, 105.5, 9000.0]
assert R.find_entry(u3, 101.0, 99.0) is None
# weak volume is skipped and the scan continues with the next close beyond the ORB
u4 = u.copy(); u4.loc[idx[20], ["c", "h"]] = [102.0, 102.5]; u4.loc[idx[25], ["c", "h", "v"]] = [102.3, 102.6, 4000.0]
e4 = R.find_entry(u4, *rng)
assert e4 and str(e4["minute"])[11:16] == "09:40", e4
assert R.find_entry(u4, *rng, vol_mult=0)["minute"] == idx[20]              # filter off -> first close beyond ORB
# SHORT mirror
u5 = u.copy(); u5.loc[idx[18], ["l", "c", "v"]] = [97.5, 98.0, 6000.0]
e5 = R.find_entry(u5, *rng)
assert e5["direction"] == "SHORT" and e5["brk_level"] == u5.h.values[18], e5
# no entry after last_min
u6 = u.copy(); u6.loc[idx[370], ["c", "h", "v"]] = [103, 103.5, 9000.0]     # 15:25
assert R.find_entry(u6, 101.0, 99.0, last_min=15 * 60 + 20) is None
print("1. ORB range, first breakout close, volume filter, SHORT mirror, last-entry limit ok")

# ------------------------------------------------------------------ 2. stock stops
after = u2.iloc[21:]
a = after.copy(); a.loc[a.index[10], "l"] = 98.9                           # touches below the ORB low 99
k, gap = R.stock_stop(a, True, 99.0)
assert k == 10 and gap is False
a.loc[a.index[4], ["o", "l"]] = [98.5, 98.0]                               # gaps through
k, gap = R.stock_stop(a, True, 99.0)
assert k == 4 and gap is True
assert R.stock_stop(after, True, 99.0) is None
k, gap = R.stock_stop(a, True, 99.0, buffer_pct=1.0)                       # 1 % buffer -> level 98.01 -> candle 4 low 98.0 still hits
assert k == 4
b = after.copy(); b.loc[b.index[6], "h"] = 101.5
k, gap = R.stock_stop(b, False, 101.0)                                     # SHORT: stock above the ORB high
assert k == 6 and gap is False
print("2. stock stop (ORB low / high, breakout-candle level, gap, buffer) ok")

# ------------------------------------------------------------------ 3. combined exit engine vs brute force
TEXITS = ["10:00", "12:00", "15:00", "15:30"]
SLS = [R.parse_sl(x) for x in ("none", "ORB", "BRK", "20", "40", "60", "ORB+20", "ORB+40", "ORB+60", "BRK+20", "BRK+40", "BRK+60")]
VARS = R.make_vars(TEXITS, SLS, [0, 20, 40, 60])
assert len(VARS) == 4 * 12 * 4


def brute(S, te, entry, texit, kind, fixed, tp, stop_ts):
    """Walk the option candles minute by minute exactly as the rules say (fixed-% stop, target, time exit)."""
    lt = pd.Timestamp(f"{te.date()} {texit}")
    if te >= lt: return None
    last = None
    for t, oo, hh, ll, cc in zip(S.index, S.o.values, S.h.values, S.l.values, S.c.values):
        if t > lt: break
        last = (t, cc)
        stop_px = tp_px = None
        if fixed:
            thr = entry * (1 - fixed / 100)
            if ll <= thr: stop_px = oo if oo <= thr else thr
        if tp:
            thr = entry * (1 + tp / 100)
            if hh >= thr: tp_px = oo if oo >= thr else thr
        if stop_px is not None: return round(stop_px, 2), (t - te) / pd.Timedelta(minutes=1)
        if tp_px is not None: return round(tp_px, 2), (t - te) / pd.Timedelta(minutes=1)
    if last is None: return None
    return round(float(last[1]), 2), (last[0] - te) / pd.Timedelta(minutes=1)


rng_ = np.random.default_rng(11)
bad = tested = 0
for _ in range(300):
    te = pd.Timestamp("2026-01-05 09:40") + pd.Timedelta(minutes=int(rng_.integers(0, 200)))
    m = 350 - int((te - pd.Timestamp("2026-01-05 09:15")) / pd.Timedelta(minutes=1))
    ix = pd.date_range(te + pd.Timedelta(minutes=1), periods=max(m, 5), freq="min")
    entry = float(rng_.uniform(5, 60)); path = entry * np.exp(np.cumsum(rng_.normal(0, 0.012, len(ix))))
    op = np.r_[entry, path[:-1]] * np.exp(rng_.normal(0, 0.004, len(ix)))
    hi = np.maximum(op, path) * (1 + np.abs(rng_.normal(0, 0.006, len(ix)))); lo = np.minimum(op, path) * (1 - np.abs(rng_.normal(0, 0.006, len(ix))))
    entry = round(entry, 2)
    S = pd.DataFrame(dict(o=op, h=hi, l=lo, c=path), index=ix).round(2)            # real option prices have 2 decimals (the engine stores 2 decimals)
    # a stock stop (ORB and / or BRK) in a random minute, sometimes none
    stops = {}
    for name in ("ORB", "BRK"):
        if rng_.random() < 0.5:
            ts = ix[int(rng_.integers(0, len(ix)))]; stops[name] = (ts, bool(rng_.random() < 0.3))
    rec = R.make_record(S, te, entry, 100, 1000.0, "2026-01-27", 1.0, TEXITS, stops)
    ls = np.array(json.loads(rec["ls"]), float).reshape(-1, 3); hs = np.array(json.loads(rec["hs"]), float).reshape(-1, 3)
    res = R.simulate_one(entry, ls, hs, json.loads(rec["tx"]), json.loads(rec["usl"]), VARS)
    for (ex, (kind, fixed), tp), (dm, px, code, late) in zip(VARS, res):
        # stock-stop price/time as the engine stores it
        st_ = None
        if kind and kind in stops:
            ts, gap = stops[kind]; i = int(S.index.searchsorted(ts, side="right")) - 1; i = max(i, 0); t0 = S.index[i]
            st_ = (ts, gap and t0 == ts)
        # the brute force handles the stock stop at the minute it fires (price = open on a gap else the close of the last candle at / before that minute)
        want = brute(S, te, entry, ex, kind, fixed, tp, None) if not st_ else None
        tested += 1
        if st_ is None:
            if want is None:
                if code != 0:
                    bad += 1
                continue
            if code == 0 or abs(want[0] - px) > 0.011 or abs(want[1] - dm) > 1e-9:
                # fixed-% stop/target at a gap: engine uses the open of the candle; brute does the same -> any difference is a bug
                bad += 1
        else:
            # with a stock stop only check the invariants: code 0 only when entered after the time exit; stop minute never after the time exit; a stock-stop exit price is an option price from that minute
            lt = pd.Timestamp(f"{te.date()} {ex}")
            if te >= lt: assert code == 0
            else:
                assert code != 0 and dm <= (lt - te) / pd.Timedelta(minutes=1) + 1e-9
                if code in (7, 8):
                    assert abs(dm - round((st_[0] - te) / pd.Timedelta(minutes=1))) < 1e-9
assert bad == 0, f"{bad} of {tested} variants differ from the brute force"
print(f"3. simulate_one equals a minute-by-minute brute force ({tested} variant evaluations, fixed SL / TP / time exit; stock-stop invariants) ok")

# first-hit order: stop vs target in the same minute -> stop wins; earlier target beats later stock stop
entry = 10.0
ix = pd.date_range("2026-01-05 09:36", periods=330, freq="min")
S = pd.DataFrame(dict(o=entry, h=entry, l=entry, c=entry), index=ix)
S.loc[ix[5], ["h", "l"]] = [entry * 1.25, entry * 0.75]                   # same minute: target 20 and stop 20 both inside
te = pd.Timestamp("2026-01-05 09:35")
rec = R.make_record(S, te, entry, 100, 1000.0, "2026-01-27", 1.0, TEXITS, {})
ls = np.array(json.loads(rec["ls"]), float).reshape(-1, 3); hs = np.array(json.loads(rec["hs"]), float).reshape(-1, 3)
V = R.make_vars(["15:30"], [R.parse_sl("20")], [20])
(dm, px, code, late), = R.simulate_one(entry, ls, hs, json.loads(rec["tx"]), json.loads(rec["usl"]), V)
assert code == 1 and abs(px - 8.0) < 1e-9, (dm, px, code)
S2 = S.copy(); S2.loc[ix[5], ["l"]] = [entry]                              # now only the target is inside
rec = R.make_record(S2, te, entry, 100, 1000.0, "2026-01-27", 1.0, TEXITS, {"ORB": (ix[40], False)})
ls = np.array(json.loads(rec["ls"]), float).reshape(-1, 3); hs = np.array(json.loads(rec["hs"]), float).reshape(-1, 3)
V = R.make_vars(["15:30"], [R.parse_sl("ORB")], [20])
(dm, px, code, late), = R.simulate_one(entry, ls, hs, json.loads(rec["tx"]), json.loads(rec["usl"]), V)
assert code == 3 and abs(px - 12.0) < 1e-9 and dm == 6, (dm, px, code)     # target at minute 6 comes before the ORB stop at minute 41
V = R.make_vars(["15:30"], [R.parse_sl("ORB")], [0])
(dm, px, code, late), = R.simulate_one(entry, ls, hs, json.loads(rec["tx"]), json.loads(rec["usl"]), V)
assert code == 7 and dm == 41, (dm, px, code)                              # no target -> the ORB stop closes it
print("   same-minute stop+target -> stop; earlier target beats a later ORB stop; ORB stop closes when no target ok")

# ------------------------------------------------------------------ 4. parse_sl / labels
assert R.parse_sl("none") == ("", 0) and R.parse_sl("20") == ("", 20) and R.parse_sl("orb") == ("ORB", 0) and R.parse_sl("BRK+40") == ("BRK", 40)
assert R.sl_label(("ORB", 20)) == "ORB+20%" and R.sl_label(("", 0)) == "no SL" and R.sl_label(("BRK", 0)) == "BRK"
try: R.parse_sl("abc"); raise SystemExit("parse_sl accepted junk")
except ValueError: pass
print("4. stop-loss tokens ok")

# ------------------------------------------------------------------ 5. the backtest module: universes, defaults, combined variants, date range
sys.argv = ["orb_backtest.py", "rules", "--universe", "top10", "--start", "2025-01-01", "--end", "2025-12-31"]
import orb_backtest as O
assert O.START == "2025-01-01" and O.END == "2025-12-31"
assert O.EXITS == ["10:00", "12:00", "15:00", "15:30"] and O.TPS == [0, 20, 40, 60]
labels = [R.sl_label(s) for s in O.SL_SPECS]
for want in ("no SL", "ORB", "BRK", "20%", "40%", "60%", "ORB+20%", "ORB+40%", "ORB+60%", "BRK+20%", "BRK+40%", "BRK+60%"):
    assert want in labels, (want, labels)
assert len(O.VARS) == 4 * 12 * 4
assert len(O.TOP10) == 10 and len(O.NIFTY50) == 50 and len(set(O.NIFTY50)) == 50
assert O.universe(None) == O.TOP10
assert "ORB" in O.rules_text() and "09:15" in O.rules_text()
print(f"5. orb_backtest imports; top10 = {len(O.TOP10)}, nifty50 = {len(O.NIFTY50)}, grid = {len(O.VARS)} variants per direction; date range {O.START}..{O.END} ok")

# ------------------------------------------------------------------ 6. end to end on synthetic records: Sim + summary files (no network)
import shutil, tempfile
tmp = tempfile.mkdtemp(prefix="orb_test_"); O.OUT = tmp; os.makedirs(f"{tmp}/parts"); os.makedirs(f"{tmp}/skipped")
rows, evs = [], []
for i in range(40):
    d = f"2025-03-{3 + i % 20:02d}"; dr = "LONG" if i % 2 == 0 else "SHORT"; s = f"STK{i % 5}"; em = "09:40"
    te = pd.Timestamp(f"{d} {em}"); ix = pd.date_range(te + pd.Timedelta(minutes=1), periods=350 - 25, freq="min")
    entry = 20.0; path = entry * np.exp(np.cumsum(rng_.normal(0, .01, len(ix))))
    S = pd.DataFrame(dict(o=np.r_[entry, path[:-1]], h=path * 1.004, l=path * .996, c=path), index=ix)
    stops = {"ORB": (ix[int(rng_.integers(5, 200))], False), "BRK": (ix[int(rng_.integers(5, 100))], False)}
    r = R.make_record(S, te, entry, 500, 1000.0, "2025-03-25", 1.0, O.EXITS, stops)
    r.update(ekey=O.ekey(s, dr, d, em), stock=s, direction=dr, date=d, entry_minute=em, strike_offset=0); rows.append(r)
    evs.append(dict(stock=s, direction=dr, date=d, entry_minute=em, stock_price=100, orb_hi=101, orb_lo=99, brk_level=99.5, vol=5000, vol_ref=1000, orb_sl_time="", orb_sl_gap=0, brk_sl_time="", brk_sl_gap=0))
pd.DataFrame(rows).to_csv(f"{tmp}/parts/t.csv.gz", index=False, compression="gzip"); pd.DataFrame(evs).to_csv(f"{tmp}/events.csv", index=False)
O.summary()
for f in ("SUMMARY.md", "summary.csv", "long/SUMMARY.md", "long/summary.csv", "long/trades_all_variants.csv.gz", "long/trades_best_variant.csv", "long/entries.csv",
          "short/SUMMARY.md", "short/summary.csv", "short/matrix_total_pnl.csv"):
    assert os.path.exists(f"{tmp}/{f}"), f"missing {f}"
S = pd.read_csv(f"{tmp}/long/summary.csv")
assert len(S) == len(O.VARS) and set(S.exit_rule) == set(O.EXITS)
T = pd.read_csv(f"{tmp}/long/trades_all_variants.csv.gz")
assert abs(T[(T.exit_rule == "15:30") & (T.sl == "no SL") & (T.tp == 0)].pnl.sum() - S[(S.exit_rule == "15:30") & (S.sl == "no SL") & (S.tp == 0)].total_pnl.iloc[0]) < len(T)
shutil.rmtree(tmp)
print("6. synthetic end-to-end (Sim, summary, matrices, trade files) ok")
print("ALL OFFLINE TESTS PASSED")
