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
# (direction, day, entry minute, entry premium, path after entry, in_orig, in_live, bb_eod)
cases = [("LONG", "2026-02-03", "10:00", 20.0, [20 + 0.1 * k for k in range(330)], 1, 1, 1),        # rises 1% per 10 min: hits TP 40/60 ..., 
         ("LONG", "2026-02-04", "10:00", 20.0, [20 - 0.1 * k for k in range(330)], 1, 1, 0),
         ("SHORT", "2026-02-05", "11:00", 20.0, [20 + 0.1 * k for k in range(300)], 0, 1, 0)]
for k, (d, day, em, ep, path, io, il, eod) in enumerate(cases):
    te = pd.Timestamp(f"{day} {em}")
    S = option_path(day, (te + pd.Timedelta(minutes=1)).strftime("%H:%M"), path[1:])
    S = S[S.index <= pd.Timestamp(f"{day} 15:29")]
    r = A.make_record(S, te, ep, LOT, 100.0, pd.Timestamp(day).date(), 1.0)
    r.update(ekey=f"TEST|{d}|{day}|{em}", stock="TEST", direction=d, date=day, entry_minute=em, strike_offset=0)
    recs.append(r)
    strat = "BPBBB_LONG" if d == "LONG" else "BPBBB_SHORT"
    events.append(dict(strategy=strat, source="BPB", stock="TEST", direction=d, type="BPBL" if d == "LONG" else "BPBS", date=day, ref=100.0, signal_date="2026-01-30", entry_minute=em, stock_price=100.5))
    cand.append(dict(source="BPB", stock="TEST", direction=d, ref=100.0, signal_date="2026-01-30", date=day, yahoo_open=99.0, green=-1, red=-1, upper_longer=-1, lower_longer=-1, line=95.0,
                     in_orig=io, in_live=il, bb_eod=eod, band_prev=99.0))
os.makedirs(f"{A.OUT}/parts", exist_ok=True)
pd.DataFrame(recs).to_csv(f"{A.OUT}/parts/TEST_x.csv.gz", index=False)
pd.DataFrame(events).to_csv(f"{A.OUT}/events.csv", index=False)
pd.DataFrame(cand).to_csv(f"{A.OUT}/candidates_{A.START}_{A.END}.csv", index=False)

BB.summary()
for f in ("SUMMARY.md", "summary.csv", "long/SUMMARY.md", "long/trades_all_variants.csv.gz", "long/entries.csv", "short/trades_all_variants.csv.gz"):
    assert os.path.exists(f"{A.OUT}/{f}"), f
T = pd.read_csv(f"{A.OUT}/long/trades_all_variants.csv.gz")
for c in ("in_orig", "in_live", "bb_eod", "band_prev", "stock_price", "ref_yahoo", "level", "cov", "strike_offset"): assert c in T.columns, c
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
txt = open(f"{RP.OUT}/COMPARE.md").read()
assert "BB_LIVE" in txt and os.path.exists(f"{RP.OUT}/ALL_SETS.csv") and os.path.exists(f"{RP.OUT}/ALL_SETS_prem_gt5.csv")
S = pd.read_csv(f"{RP.OUT}/ALL_SETS.csv")
n = lambda s, d: int(S[(S.set == s) & (S.direction == d) & (S.exit_rule == "15:30") & (S.sl == 0) & (S.tp == 0)].trades.iloc[0])
assert n("ALL", "LONG") == 2 and n("ORIG", "LONG") == 2 and n("BB_EOD", "LONG") == 1 and n("ALL", "SHORT") == 1, S.head()
assert S[(S.set == "ORIG") & (S.direction == "SHORT")].empty and S[(S.set == "BB_EOD") & (S.direction == "SHORT")].empty        # the SHORT entry is live-only
print("test_bpb_bb_pipeline OK")
