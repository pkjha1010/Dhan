"""itm_fallback.py - strike choice for the backtests: ATM first; if the ATM series has no candle at the entry minute (or a zero price), ITM-1, then ITM-2, ITM-3 ... until
a strike with a candle is found (up to max_itm).  A put (SHORT) goes ITM = higher strikes (ATM+1, ATM+2 ...), a call (LONG) = lower strikes.
Drop-in replacement for all8_backtest.work_group (same signature and result); the used offset is stored in each record (strike_offset: 0 = ATM, +-n = ITM-n).
"""
from collections import Counter
from datetime import date, timedelta
import numpy as np, pandas as pd


def make_work_group(A, max_itm):
    def work_group(dh, mst, t):
        s, dr, E, ents, key = t
        sid, lot = mst[s]
        d0 = date.fromisoformat(min(d for d, _ in ents)); wins = A.windows(d0, E + timedelta(days=1))
        sgn = 1 if dr == "SHORT" else -1
        cache = {}

        def ser(off):
            if off not in cache:
                x = A.get_series(dh, sid, dr, wins, off)
                if x is not None and "strike" in x: x = x[x.index.date <= E]
                cache[off] = x if (x is not None and "strike" in x and len(x)) else None
            return cache[off]

        offsets = [k * sgn for k in range(max_itm + 1)]                         # 0, then ITM-1, ITM-2 ...
        plans, skips = [], []
        for d, em in ents:
            m = pd.Timestamp(f"{d} {em}"); got, why = None, f"no ATM / ITM-1..ITM-{max_itm} candle at the entry minute"
            for off in offsets:
                x = ser(off)
                if x is None: continue
                a = x[x.index >= m]
                if a.empty or (a.index[0] - m) > pd.Timedelta(minutes=3): continue
                te, K, entry = a.index[0], float(a.strike.iloc[0]), float(a.c.iloc[0])
                if not entry > 0: why = "zero price"; continue
                got = (off, te, K, entry); break
            if got is None:
                skips.append((A.ekey(s, dr, d, em), why if any(v is not None for v in cache.values()) else "Dhan returned no option candles for this period")); continue
            plans.append((d, em) + got)
        if not plans: return [], skips
        base_off = 0 if cache.get(0) is not None else plans[0][2]
        bx = cache[base_off]; Eeff = max(set(bx.index.date)); step = A.infer_step(bx.strike.values)
        cnt, rest = Counter(), []
        for d, em, off, te, K, entry in plans:
            after = bx[bx.index > te]
            if step > 0 and len(after):
                n = np.rint((K - (after.strike.values - base_off * step)) / step).astype(int)       # which ATM+n series holds the locked strike at each minute
                for v, k in zip(*np.unique(n, return_counts=True)):
                    if v != 0 and abs(v) <= A.OFFS_MAX: cnt[int(v)] += int(k)
            rest.append((d, em, off, te, K, entry, len(after)))
        for v, _ in cnt.most_common(A.MAX_OFFS): ser(v)
        big = pd.concat([x[x.index.date <= Eeff] for x in cache.values() if x is not None])
        recs = []
        for d, em, off, te, K, entry, nexp in rest:
            S = big[((big.strike - K).abs() < 1e-6).values & (big.index > te)]
            S = S[~S.index.duplicated()].sort_index()
            if S.empty or nexp == 0: skips.append((A.ekey(s, dr, d, em), "no option candles after the entry")); continue
            r = A.make_record(S, te, entry, lot, K, Eeff, min(1.0, len(S) / nexp))
            r.update(ekey=A.ekey(s, dr, d, em), stock=s, direction=dr, date=d, entry_minute=em, strike_offset=off)
            recs.append(r)
        return recs, skips
    return work_group
