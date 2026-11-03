"""bpb_base_rules.py - the BPB BASE strategy rules (LONG and SHORT), pure numpy (no Dhan, no Yahoo, no engine), so test_bpb_base.py can check them.

  LONG   1. BREAKOUT : a daily candle closes above the 10-day rolling high (highest High of the previous 10 days) = the LINE.
         2. PULLBACK : the candles after the breakout day must NOT close below the LINE (the first one that does makes the setup invalid); a bearish candle (close < open) confirms the pullback.
         3. ENTRY LEVEL = the highest price (High) made since the breakout day (the breakout day included).
         4. ENTRY    : on a later day, the first 1-minute candle (09:15 .. 15:20) whose High reaches the ENTRY LEVEL -> buy the ATM CALL (a gap through the level = 09:15).
  SHORT  exact mirror: close below the 10-day rolling LOW; pullback candles must not close above the line; entry level = the lowest Low since the breakdown; first 1-minute candle whose Low
         reaches it -> buy the ATM PUT.
  NIFTY50 FILTER (in the entry minute, see gap_nifty_rules.py): LONG only when NIFTY50 > its open of the day, SHORT only when NIFTY50 < its open of the day.

The daily state machine is bpb_fno_backtest.find_setups (your BPB code); SHORT calls it on the mirrored arrays (-O, -L, -H, -C).
"""
import numpy as np


def bpb_setups(O, H, L, C, long=True, lookback=10):
    """-> list of dicts: entry (index of the entry day), level (entry level), line (the rolling high / low at the breakout), breakout (index of the breakout day), all in REAL prices."""
    import bpb_fno_backtest as B
    O, H, L, C = (np.asarray(x, float) for x in (O, H, L, C))
    if long: res = B.find_setups(O, H, L, C, lookback)
    else: res = B.find_setups(-O, -L, -H, -C, lookback)
    sg = 1.0 if long else -1.0
    return [dict(entry=int(i), level=float(sg * lvl), line=float(sg * line), breakout=int(b)) for i, lvl, line, b in res]
