#!/usr/bin/env python3
"""18-e438-mpmath.py -- 1.2.1.2 e438, (d+e*x)^m/(c*d*x+c*e*x^2): the final core's answer
A = -(2F1(1,m+1;m+2;e*x/d+1)*(e*x+d)^(m+1))/(c*d^2*(m+1)) - (e*x+d)^m/(c*d*m)
(fa.py trace final=final ... 438) has its 2F1 at z > 1 for d > 0, where Maxima's float()
does not evaluate it (numcheck.py: err). mpmath (analytic continuation) instead:
|dA/dx - f| at three parameter sets, two points each."""
import mpmath as mp
mp.mp.dps = 30
A = lambda x, c, d, e, m: (-(mp.hyp2f1(1, m + 1, m + 2, e * x / d + 1) * (e * x + d) ** (m + 1)) / (c * d ** 2 * (m + 1))
                           - (e * x + d) ** m / (c * d * m))
f = lambda x, c, d, e, m: (d + e * x) ** m / (c * d * x + c * e * x ** 2)
for (c, d, e, m) in [(0.7, -0.8, 0.5, 0.37), (1.3, -2.0, 0.6, 1.7), (0.5, 0.4, -0.3, 0.61)]:
    for x in (0.3, 0.5):
        print(f"c={c} d={d} e={e} m={m} x={x}  |dA/dx - f| =",
              mp.nstr(abs(mp.diff(lambda t: A(t, c, d, e, m), x) - f(x, c, d, e, m)), 5))
