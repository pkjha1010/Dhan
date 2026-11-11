"""orb_rules.py - pure logic of the ORB (opening range breakout) backtest: no network, no files.  Used by orb_backtest.py and tested offline by test_orb.py.

SETUP (1-minute stock candles, one trade per stock per day)
  ORB      = highest High / lowest Low of the 1-minute candles that START from 09:15 up to (not including) 09:30.
  LONG     the first 1-minute candle (from 09:30) whose CLOSE is above the ORB high  (and passes the volume filter)  -> buy the ATM CALL at the close of that minute.
  SHORT    mirror: the first candle whose CLOSE is below the ORB low -> buy the ATM PUT.   Whichever side signals first is the trade of the day.
  VOLUME   (the "strong volume" filter of the strategy table): volume of the breakout candle >= vol_mult x the average volume of the previous vol_n one-minute candles.  vol_mult = 0 switches it off.
           A close beyond the ORB that fails the filter is skipped and the scan continues with the next candle.

STOP-LOSS TYPES (stock-price based, exactly the two of the strategy table)
  ORB   LONG: the stock trades below the ORB low   | SHORT: the stock trades above the ORB high
  BRK   LONG: the stock trades below the LOW of the breakout candle | SHORT: above the HIGH of the breakout candle
  The stop is touched when a later 1-minute stock candle's Low (SHORT: High) reaches the level (optionally a buffer in % beyond it).  The option is sold at the close of that minute
  (at the open of that minute when the stock gapped through the level).
  FIXED stop-loss / target are % of the option premium (first 1-minute option low / high that touches it, a gap through it fills at the open).  Time exit = close of the last option candle up to that minute.
  Any mix of them is a COMBINED exit: the first one that is hit closes the trade (stop beats target when both are inside the same minute).
"""
import json
import numpy as np, pandas as pd

ORB_START, ORB_END = 9 * 60 + 15, 9 * 60 + 30


def minutes(idx):
    return idx.hour.values * 60 + idx.minute.values


def orb_range(u, start_min=ORB_START, end_min=ORB_END, min_candles=10):
    """-> (ORB high, ORB low) from the candles starting in [start_min, end_min); None if the day has fewer than min_candles of them (holiday / missing data)."""
    if u is None or len(u) == 0: return None
    w = (minutes(u.index) >= start_min) & (minutes(u.index) < end_min)
    if int(w.sum()) < min_candles: return None
    return float(u.h.values[w].max()), float(u.l.values[w].min())


def find_entry(u, orb_hi, orb_lo, first_min=ORB_END, last_min=15 * 60 + 20, vol_mult=1.5, vol_n=10):
    """First breakout candle of the day.  u = one day of 1-minute stock candles (columns o h l c v, index = candle start).
    -> dict(pos, minute, direction, close, vol, vol_ref, orb_hi, orb_lo, brk_level)   brk_level = LOW of the breakout candle (LONG) / HIGH (SHORT);  or None."""
    m = minutes(u.index); c = u.c.values.astype(float)
    v = u.v.values.astype(float) if "v" in u.columns else np.zeros(len(u))
    for k in range(len(u)):
        if m[k] < first_min: continue
        if m[k] > last_min: return None
        long = c[k] > orb_hi; short = c[k] < orb_lo
        if not (long or short): continue
        prev = v[max(0, k - vol_n):k]; ref = float(prev.mean()) if len(prev) else 0.0
        if vol_mult and vol_mult > 0:
            if len(prev) < 3 or not ref > 0 or v[k] < vol_mult * ref: continue
        return dict(pos=k, minute=u.index[k], direction="LONG" if long else "SHORT", close=float(c[k]), vol=float(v[k]), vol_ref=round(ref, 1),
                    orb_hi=float(orb_hi), orb_lo=float(orb_lo), brk_level=float(u.l.values[k] if long else u.h.values[k]))
    return None


def stock_stop(u_after, long, level, buffer_pct=0.0):
    """First stock candle after the entry that touches the stop level.  -> (position in u_after, gap) or None.  gap = the candle OPENED beyond the level."""
    if u_after is None or len(u_after) == 0: return None
    if long:
        thr = level * (1 - buffer_pct / 100.0); hit = u_after.l.values <= thr; gapv = u_after.o.values <= thr
    else:
        thr = level * (1 + buffer_pct / 100.0); hit = u_after.h.values >= thr; gapv = u_after.o.values >= thr
    if not hit.any(): return None
    k = int(np.argmax(hit)); return k, bool(gapv[k])


def stairs(v, o, dm, low):
    """Running new lows (or highs): [minutes since entry, price, open of that candle].  The first candle that touches ANY level is always one of these."""
    run = np.minimum.accumulate(v) if low else np.maximum.accumulate(v)
    new = np.r_[True, (v[1:] < run[:-1]) if low else (v[1:] > run[:-1])]
    return [[int(dm[i]), round(float(v[i]), 2), round(float(o[i]), 2)] for i in np.nonzero(new)[0]]


def option_px_at(S, ts, gap):
    """Option price when the stock stop fires in the minute starting at ts: open of that minute's option candle on a gap, else the close of the last option candle at / before ts
    (the first one after it if the option has no candle yet).  -> (price, thin) thin = the candle used is more than 5 minutes away."""
    i = int(S.index.searchsorted(ts, side="right")) - 1
    if i < 0: i = 0
    t = S.index[i]
    px = float(S.o.iloc[i]) if (gap and t == ts) else float(S.c.iloc[i])
    return round(px, 2), int(abs(t - ts) > pd.Timedelta(minutes=5))


def make_record(S, te, entry, lot, K, expiry, cov, texits, stops):
    """S = option candles after the entry minute (o,h,l,c, index = time).  stops = {"ORB": (stock candle start Timestamp, gap) or None, "BRK": ...} from stock_stop().
    Everything the exit variants need, in a few hundred numbers."""
    dm = np.asarray((S.index - te) / pd.Timedelta(minutes=1)).astype(np.int64)
    o, h, l, c = (S[x].values.astype(float) for x in ("o", "h", "l", "c"))
    tx = {}
    for lim in texits:
        lt = pd.Timestamp(f"{te.date()} {lim}")
        if te >= lt: continue
        w = S.index <= lt
        if not w.any(): continue
        j = int(np.nonzero(w)[0][-1])
        tx[lim] = [int(dm[j]), round(float(c[j]), 2), int((lt - S.index[j]) > pd.Timedelta(minutes=5))]
    usl = {}
    for name in ("ORB", "BRK"):
        r = (stops or {}).get(name)
        if r is None: continue
        ts, gap = r
        px, thin = option_px_at(S, ts, gap)
        usl[name] = [int(round((ts - te) / pd.Timedelta(minutes=1))), px, thin]
    return dict(entry_time=f"{te:%H:%M}", strike=K, entry_price=round(entry, 2), lot=int(lot), expiry=str(expiry), cov=round(cov, 3), bars=len(S),
                ls=json.dumps(stairs(l, o, dm, True), separators=(",", ":")), hs=json.dumps(stairs(h, o, dm, False), separators=(",", ":")),
                tx=json.dumps(tx, separators=(",", ":")), usl=json.dumps(usl, separators=(",", ":")))


# ---------------------------------------------------------------- exit variants
def parse_sl(token):
    """'none' | 'ORB' | 'BRK' | '20' | 'ORB+20' | 'BRK+40'  ->  (kind, fixed %)   kind '' / 'ORB' / 'BRK',  fixed 0 = none."""
    t = str(token).strip().upper().replace(" ", "")
    if t in ("", "NONE", "0"): return ("", 0)
    kind, fixed = "", 0
    for p in t.split("+"):
        if p in ("ORB", "BRK"): kind = p
        elif p.replace(".", "", 1).isdigit(): fixed = int(float(p))
        else: raise ValueError(f"unknown stop-loss '{token}' (use none, ORB, BRK, a % like 20, or a mix like ORB+20)")
    return (kind, fixed)


def sl_label(spec):
    kind, fixed = spec
    return "+".join([x for x in (kind, f"{fixed}%" if fixed else "") if x]) or "no SL"


def tp_label(tp):
    return f"TP {int(tp)}%" if tp else "no TP"


def make_vars(texits, sl_specs, tps):
    return [(ex, spec, tp) for ex in texits for spec in sl_specs for tp in tps]


REASON = {1: "STOP %", 2: "STOP % (gap)", 3: "TARGET", 4: "TARGET (gap)", 5: "TIME", 7: "STOP ORB", 8: "STOP BREAKOUT CANDLE"}


def simulate_one(entry, ls, hs, tx, usl, vars_):
    """-> list over vars_ of (exit minute since entry, exit price, reason code, thin flag); code 0 = not available (entered at / after the time exit)."""
    fixed_all = sorted({f for _, (k, f), _ in vars_ if f})
    slh, tph = {}, {}
    for f in fixed_all:
        thr = round(entry * (1 - f / 100), 6); i = int(np.searchsorted(-ls[:, 1], -thr, side="left")) if len(ls) else 0
        if len(ls) and i < len(ls): gap = ls[i, 2] <= thr; slh[f] = (int(ls[i, 0]), float(ls[i, 2]) if gap else thr, 2 if gap else 1, 0)
    for tp in sorted({t for _, _, t in vars_ if t}):
        thr = round(entry * (1 + tp / 100), 6); i = int(np.searchsorted(hs[:, 1], thr, side="left")) if len(hs) else 0
        if len(hs) and i < len(hs): gap = hs[i, 2] >= thr; tph[tp] = (int(hs[i, 0]), float(hs[i, 2]) if gap else thr, 4 if gap else 3, 0)
    ush = {k: (int(v[0]), float(v[1]), 7 if k == "ORB" else 8, int(v[2])) for k, v in (usl or {}).items()}
    out = []
    for ex, (kind, fixed), tp in vars_:
        t = tx.get(ex)
        if t is None: out.append((0, 0.0, 0, 0)); continue
        lim = t[0]; stops = []
        if fixed and fixed in slh and slh[fixed][0] <= lim: stops.append(slh[fixed])
        if kind and kind in ush and ush[kind][0] <= lim: stops.append(ush[kind])
        sh = min(stops, key=lambda x: (x[0], x[1])) if stops else None             # earliest stop; on a tie the lower (worse) price
        th = tph.get(tp) if tp else None
        if th is not None and th[0] > lim: th = None
        if sh is not None and (th is None or sh[0] <= th[0]): out.append(sh)         # stop first (also on a tie)
        elif th is not None: out.append(th)
        else: out.append((lim, t[1], 5, t[2]))
    return out


def max_drawdown(p):
    c = np.cumsum(p); peak = np.maximum.accumulate(np.r_[0.0, c])[1:]
    return float((c - peak).min()) if len(c) else 0.0
