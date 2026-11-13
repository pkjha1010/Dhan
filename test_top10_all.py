"""Offline test of top10_all_backtest.py: every strategy receives the common grid + the 10 stocks, and compare() merges every summary format."""
import os, sys, subprocess, tempfile
import numpy as np, pandas as pd
sys.argv = ["x"]
import top10_all_backtest as T

assert T.SYMBOLS.split() == "HDFCBANK RELIANCE ICICIBANK INFY BHARTIARTL ITC LT TCS AXISBANK SBIN".split()
assert T.ORDER == list(T.STRATS) or set(T.ORDER) == set(T.STRATS)
# 1. each strategy's own 'rules' mode shows the common grid (100 variants) and 10 stocks
for n in ["opendrop", "gap", "bpb_base", "accum5", "accum10", "orb"]:
    r = subprocess.run([sys.executable, T.STRATS[n][0], "rules"], env=T.child_env(n, 30), capture_output=True, text=True)
    out = r.stdout + r.stderr
    assert r.returncode == 0 and "= 100 variants" in out, (n, out[-400:])
    assert ("10 stocks" in out) or all(s in out for s in T.SYMBOLS.split()), (n, out[-400:])
    assert "'09:30', '10:00', '12:00', '15:00', '15:30'" in out, n
print("1. opendrop / gap / bpb_base / accum5 / accum10 / orb get the grid + 10 stocks")
r = subprocess.run([sys.executable, "-c", "import top10_all8_run as A8;print(len(A8.A.UNIVERSE), A8.A.SLS, A8.A.TPS, A8.A.EXITS, len(A8.A.VARS))"], env=T.child_env("all8", 30), capture_output=True, text=True)
assert r.stdout.strip() == "10 [0, 20, 40, 60] [0, 40, 60, 80, 120] ['09:30', '10:00', '12:00', '15:00', '15:30'] 100", r.stdout + r.stderr
r = subprocess.run([sys.executable, "-c", "import pullback_options_backtest as P;print(len(P.SYMBOLS), P.SLS, P.TPS, P.EXITS)"], env=T.child_env("pullback", 30), capture_output=True, text=True)
assert r.stdout.strip() == "10 [0.0, 0.2, 0.4, 0.6] [0.0, 0.4, 0.6, 0.8, 1.2] ['09:30', '10:00', '12:00', '15:00', '15:30']", r.stdout + r.stderr
print("2. all8 (time exits only, no UNTIL_HIT) and pullback get the grid + 10 stocks")

# 3. compare() on synthetic summaries in every format the strategies write
d = tempfile.mkdtemp(); T.OUT = d; rng = np.random.default_rng(1)
def mk(strat, frac=False, strsl=False):
    rows = [dict(strategy=strat, exit_rule=ex, sl=("none" if strsl and sl == 0 else (sl / 100 if frac else sl)), tp=(tp / 100 if frac else tp), trades=int(rng.integers(5, 40)),
                 win_pct=round(rng.uniform(30, 60), 1), total_pnl=round(rng.normal(0, 1e5)), roi_pct=round(rng.normal(0, 5), 2), profit_factor=1.1, max_drawdown=-1)
            for ex in ("09:30", "15:30") for sl in (0, 20, 40, 60) for tp in (0, 40, 60, 80, 120)]
    return pd.DataFrame(rows)
for sub, name, df in (("gap/long", "summary.csv", mk("GAP_LONG")), ("gap/short", "summary.csv", mk("GAP_SHORT")), ("all8", "summary.csv", mk("WICK_RED_LOWER")),
                      ("orb/long", "summary.csv", mk("ORB_LONG", strsl=True)), ("orb", "summary.csv", mk("ORB_LONG", strsl=True)), ("pullback", "summary_LONG.csv", mk("X", frac=True).drop(columns="strategy"))):
    os.makedirs(f"{d}/{sub}", exist_ok=True); df.to_csv(f"{d}/{sub}/{name}", index=False)
T.compare()
A = pd.read_csv(f"{d}/ALL_VARIANTS.csv")
assert A.groupby("strategy").size().to_dict() == {"GAP_LONG": 40, "GAP_SHORT": 40, "ORB_LONG": 40, "PULLBACK_LONG": 40, "WICK_RED_LOWER": 40}, A.groupby("strategy").size().to_dict()
assert {int(float(x)) for x in A[A.module == "pullback"].sl} == {0, 20, 40, 60} and {int(float(x)) for x in A[A.module == "pullback"].tp} == {0, 40, 60, 80, 120}
assert os.path.exists(f"{d}/COMPARE.md") and os.path.exists(f"{d}/BEST_PER_STRATEGY.csv")
print("3. compare() merges every summary format (fractions -> %, ORB 'none', no double count)")
print("ALL OK")
