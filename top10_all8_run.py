"""top10_all8_run.py - all8_backtest.py (4 wick shapes + 1H / 4H trendline + BPB breakout + SHAPECMP re-cross) with the SAME time exits as the other strategies (env T10_EXITS) and no UNTIL_HIT variant.
Used by top10_all_backtest.py; settings come from the A8_* variables it sets.   python top10_all8_run.py check | run | summary"""
import os, sys
_ex = [x.strip() for x in os.environ.get("T10_EXITS", "09:30,10:00,12:00,15:00,15:30").replace(" ", ",").split(",") if len(x.strip()) == 5 and x.strip()[2] == ":"]
import all8_backtest as A

A.TEXITS = list(_ex)
A.EXITS = list(_ex)                                              # time exits only, no UNTIL_HIT
A.VARS = [(ex, sl, tp) for ex in A.EXITS for sl in A.SLS for tp in A.TPS]

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        print(f"ALL8 on {len(A.UNIVERSE)} stocks {A.START}..{A.END}: SL {A.SLS} x TP {A.TPS} x exits {A.EXITS} = {len(A.VARS)} variants per strategy", flush=True)
        if mode == "check": A.check()
        elif mode == "run": A.run()
        elif mode in ("summary", "range"):
            try: A.summary()
            except ValueError as e:
                print(f"note: no variant has {A.MIN_TRADES} trades yet ({e}); rebuilding with a minimum of 1", flush=True); A.MIN_TRADES = 1; A.summary()
        else: sys.exit("use: python top10_all8_run.py check | run | summary")
    except A.Fatal as e:
        sys.exit(f"STOP - needs your action: {e}")
