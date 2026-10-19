"""Offline logic test (no broker, no engine): python test_shapetrend.py"""
import numpy as np
import trend_filters as TF

def series(drift, n=120, seed=1):
    r = np.random.RandomState(seed); c = 100 + np.cumsum(drift + r.randn(n) * 0.4)
    o = np.r_[c[0], c[:-1]]; h = np.maximum(o, c) + 0.3; l = np.minimum(o, c) - 0.3
    return o, h, l, c

# 1) steady up-trend: every LONG filter passes at the end, no SHORT filter does; steady down-trend = the opposite
f = TF.trend_flags(*series(+0.8))
for k in TF.TRENDS: assert f[k][0][-1] and not f[k][1][-1], ("uptrend", k)
f = TF.trend_flags(*series(-0.8))
for k in TF.TRENDS: assert f[k][1][-1] and not f[k][0][-1], ("downtrend", k)
# 2) no history -> nothing passes
f = TF.trend_flags(*series(+0.8, n=25))
assert not f["MA50"][0].any() and not f["ADXDI"][0].any()
# 3) filters never look ahead: changing the future does not change earlier values
o, h, l, c = series(+0.5); a = TF.trend_flags(o, h, l, c)
c2 = c.copy(); c2[100:] += 50; h2 = h.copy(); h2[100:] += 50; l2 = l.copy(); l2[100:] += 50; o2 = o.copy(); o2[100:] += 50
b = TF.trend_flags(o2, h2, l2, c2)
for k in TF.TRENDS: assert (a[k][0][:99] == b[k][0][:99]).all() and (a[k][1][:99] == b[k][1][:99]).all(), k
# 4) BPB short: 10 flat days, breakdown day, bounce (green) day, then a day that dips below the lowest low
O = [100] * 10 + [99.5, 97.4, 97.5]; H = [101] * 10 + [99.8, 98.2, 98.0]; L = [99] * 10 + [96.5, 97.2, 96.4]; C = [100] * 10 + [97.0, 98.0, 97.0]
e = TF.bpb_entries(O, H, L, C, False)
assert e == [(12, 99.0, 96.5)], e
# a bounce that closes back above the line kills the setup
C2 = C[:]; C2[11] = 99.5; O2 = O[:]; O2[11] = 97.4
assert TF.bpb_entries(O2, H, L, C2, False) == []
# 5) BPB long = mirror image
e = TF.bpb_entries([200 - x for x in O], [200 - x for x in L], [200 - x for x in H], [200 - x for x in C], True)
assert e == [(12, 101.0, 103.5)], e
print("OFFLINE TEST OK")
