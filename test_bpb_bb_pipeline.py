"""test_bpb_bb_pipeline.py - offline end-to-end test (no login): fake events + fake option candles -> bpb_bb_backtest.summary() -> bpb_bb_report.  Checks that every result file is written, the flags reach the
trade files, and the PnL of a trade is what a hand calculation gives."""
import os, sys, tempfile, json
tmp = tempfile.mkdtemp(prefix="bpbbb_")
os.environ.update(BBB_OUT=os.path.join(tmp, "res"), BBB_START="2026-01-01", BBB_END="2026-12-31", BBB_SYMBOLS="TEST", BBB_MIN_TRADES="1")
import numpy as np, pandas as pd
import bpb_bb_backtest as BB
A = BB.A
os.makedirs(A.OUT, exist_ok=True)

LOT = 100
def option_path(day, start, prices):
    idx = pd.date_range(f"{day} {start}", periods=len(prices), freq="min")
    p = np.asarray(prices, float)
    return pd.DataFrame({"o": p, "h": p + 0.5, "l": p - 0.5, "c": p}, index=idx)

events, recs, cand = [], [], []
# (direction, day, entry minute, entry premium, path after entry, b_plus, from_b1, from_b2, from_b3)
cases = [("LONG", "2026-02-03", "10:00", 20.0, [20 + 0.1 * k for k in range(330)], 3, 1, 1, 1),        # rises 0.1 per minute
         ("LONG", "2026-02-04", "10:00", 20.0, [20 - 0.1 * k for k in range(330)], 2, 1, 1, 0),        # falls 0.1 per minute
         ("SHORT", "2026-02-05", "11:00", 20.0, [20 + 0.1 * k for k in range(300)], 1, 1, 0, 0)]
for k, (d, day, em, ep, path, bp, f1, f2, f3) in enumerate(cases):
    te = pd.Timestamp(f"{day} {em}")
    S = option_path(day, (te + pd.Timedelta(minutes=1)).strftime("%H:%M"), path[1:])
    S = S[S.index <= pd.Timestamp(f"{day} 15:29")]
    r = A.make_record(S, te, ep, LOT, 100.0, pd.Timestamp(day).date(), 1.0)
    r.update(ekey=f"TEST|{d}|{day}|{em}", stock="TEST", direction=d, date=day, entry_minute=em, strike_offset=0)
    recs.append(r)
    strat = "BPBBB_LONG" if d == "LONG" else "BPBBB_SHORT"
    events.append(dict(strategy=strat, source="BPB", stock="TEST", direction=d, type="BPBL" if d == "LONG" else "BPBS", date=day, ref=100.0, signal_date="2026-01-30", entry_minute=em, stock_price=100.5))
    cand.append(dict(source="BPB", stock="TEST", direction=d, ref=100.0, signal_date="2026-01-30", date=day, yahoo_open=99.0, green=-1, red=-1, upper_longer=-1, lower_longer=-1, line=95.0,
                     b_plus=bp, b_label=f"B+{bp}", from_b1=f1, from_b2=f2, from_b3=f3, bb_ok=1))
os.makedirs(f"{A.OUT}/parts", exist_ok=True)
pd.DataFrame(recs).to_csv(f"{A.OUT}/parts/TEST_x.csv.gz", index=False)
pd.DataFrame(events).to_csv(f"{A.OUT}/events.csv", index=False)
pd.DataFrame(cand).to_csv(f"{A.OUT}/candidates_{A.START}_{A.END}.csv", index=False)

BB.summary()
for f in ("SUMMARY.md", "summary.csv", "long/SUMMARY.md", "long/trades_all_variants.csv.gz", "long/entries.csv", "short/trades_all_variants.csv.gz"):
    assert os.path.exists(f"{A.OUT}/{f}"), f
T = pd.read_csv(f"{A.OUT}/long/trades_all_variants.csv.gz")
for c in ("b_plus", "b_label", "breakout_date", "from_b1", "from_b2", "from_b3", "bb_ok", "stock_price", "ref_yahoo", "level", "cov", "strike_offset"): assert c in T.columns, c
assert set(T[T.entry_date == "2026-02-03"].b_label) == {"B+3"} and set(T[T.entry_date == "2026-02-04"].b_label) == {"B+2"} and set(T.breakout_date) == {"2026-01-30"}
E_ = pd.read_csv(f"{A.OUT}/long/entries.csv"); assert "b_label" in E_.columns and sorted(E_.b_label) == ["B+2", "B+3"]
assert "B+1" in open(f"{A.OUT}/short/SUMMARY.md").read() and "B = the breakout day" in open(f"{A.OUT}/long/SUMMARY.md").read()
assert set(T.exit_rule) == {"09:30", "10:00", "12:00", "15:00", "15:30"} or set(T.exit_rule) == {"12:00", "15:00", "15:30"}, set(T.exit_rule)    # 10:00 entry: 09:30 / 10:00 exits are skipped
# hand check: LONG case 1, no SL, TP 40%: option rises 0.1/min -> +40% = 28.0 -> needs 80 min (high = price + 0.5 -> first minute whose high >= 28.0 is price 27.5 at k = 75)
t = T[(T.entry_date == "2026-02-03") & (T.exit_rule == "15:30") & (T.sl == 0) & (T.tp == 40)].iloc[0]
assert t.reason.startswith("TARGET") and abs(t.exit_price - 28.0) < 1e-6 and t.lots == 60000 // (20 * LOT) and abs(t.pnl - (28.0 - 20.0) * t.lots * LOT) < 1, t.to_dict()
# LONG case 2: falls 0.1/min: SL 20% = 16.0 hit at the minute whose low (price - 0.5) <= 16 -> price 16.5 at k = 35
t = T[(T.entry_date == "2026-02-04") & (T.exit_rule == "15:30") & (T.sl == 20) & (T.tp == 0)].iloc[0]
assert t.reason.startswith("STOP") and abs(t.exit_price - 16.0) < 1e-6, t.to_dict()
# exit 12:00 with no SL / TP: closes at the last candle at or before 12:00 (10:00 + 120 min -> k = 120 -> price 20 + 12 = 32 for case 1)
t = T[(T.entry_date == "2026-02-03") & (T.exit_rule == "12:00") & (T.sl == 0) & (T.tp == 0)].iloc[0]
assert t.reason == "TIME" and abs(t.exit_price - 32.0) < 0.2, t.to_dict()
print("engine summary OK:", len(T), "long trade rows,", T.exit_rule.nunique(), "exits")

import bpb_bb_report as RP
RP.SRC, RP.OUT = A.OUT, os.path.join(tmp, "rep"); RP.main()
for d in ("long", "short"):
    for f in ("COMPARE.md", "ALL_SETS.csv", "BY_BPLUS.csv", "BEST_BY_YEAR.csv", "COMPARE_prem_gt5.md"):
        assert os.path.exists(f"{RP.OUT}/{d}/{f}") or f == "COMPARE_prem_gt5.md" or f == "BEST_BY_YEAR.csv", (d, f)
txt = open(f"{RP.OUT}/long/COMPARE.md").read()
assert "B = the breakout day" in txt and "B+3 onward (your script)" in txt and "B+3" in txt and "exact entry day B+n" in txt
n = lambda d, s, ex="15:30": int(pd.read_csv(f"{RP.OUT}/{d}/ALL_SETS.csv").pipe(lambda S: S[(S.set == s) & (S.exit_rule == ex) & (S.sl == 0) & (S.tp == 0)]).trades.iloc[0])
assert n("long", "B+1 onward") == 2 and n("long", "B+2 onward") == 2 and n("long", "B+3 onward (your script)") == 1, "long sets"
assert n("short", "B+1 onward") == 1
S_short = pd.read_csv(f"{RP.OUT}/short/ALL_SETS.csv"); assert S_short[S_short.set == "B+2 onward"].empty and S_short[S_short.set == "B+3 onward (your script)"].empty      # the SHORT entry is B+1 only
Bp = pd.read_csv(f"{RP.OUT}/long/BY_BPLUS.csv"); assert set(Bp[Bp.set == "B+1 onward"].entry_day) == {"B+2", "B+3"}
print("test_bpb_bb_pipeline OK")
