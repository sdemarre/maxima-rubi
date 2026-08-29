#!/usr/bin/env python3
"""Unit test for the answer-head rewrites (test/corpus_driver.py
HEAD_REWRITES). Pure Python — no Maxima needed."""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "corpus_driver", os.path.join(ROOT, "test", "corpus_driver.py"))
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

passed = failed = 0
def check(name, actual, expected):
    global passed, failed
    if actual == expected:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name}\n  expected: {expected!r}\n  actual:   {actual!r}")

n = m.normalize_heads
check("GAMMA 2-arg", n("GAMMA(m + 1, -f*g*log(F)/d*(c + d*x))"),
      "gamma_incomplete(m + 1, -f*g*log(F)/d*(c + d*x))")
check("Ei 1-arg", n("F^(g*(e - c*f/d))/d*Ei(f*g*(c + d*x)*log(F)/d)"),
      "F^(g*(e - c*f/d))/d*expintegral_ei(f*g*(c + d*x)*log(F)/d)")
check("longer name intact", n("XEi(2)"), "XEi(2)")
check("free F0 untouched", n("F0(x)/(x + F0(x))"), "F0(x)/(x + F0(x))")
check("erf lowercase untouched", n("2*erf(z)"), "2*erf(z)")
check("native already-native untouched",
      n("gamma_incomplete(2, z)"), "gamma_incomplete(2, z)")
check("both in one line", n("GAMMA(a, z)*Ei(w)"),
      "gamma_incomplete(a, z)*expintegral_ei(w)")
check("Chi positive", n("Chi(x)"), "expintegral_chi(x)")
check("Shi positive", n("Shi(x)"), "expintegral_shi(x)")
check("Si positive", n("Si(2*b*x)/b"), "expintegral_si(2*b*x)/b")
check("Ci positive", n("Ci(b*x)*cos(a)/b"), "expintegral_ci(b*x)*cos(a)/b")
check("Li positive", n("Li(d*x)/d"), "expintegral_li(d*x)/d")
check("all five in one line",
      n("Chi(a)+Shi(b)+Si(c)+Ci(d)+Li(e)"),
      "expintegral_chi(a)+expintegral_shi(b)+expintegral_si(c)"
      "+expintegral_ci(d)+expintegral_li(e)")
check("expintegral_li native untouched",
      n("expintegral_li(x)"), "expintegral_li(x)")
check("expintegral_si native untouched",
      n("expintegral_si(x)"), "expintegral_si(x)")
check("Si inside longer name intact", n("MySi(x)"), "MySi(x)")
check("Chi inside longer name intact", n("XChi(2)"), "XChi(2)")
check("Li inside longer name intact", n("Li2(x)"), "Li2(x)")
check("Sin untouched (Si row guard)", n("Sin(x)"), "Sin(x)")
check("LogGamma untouched (GAMMA row guard)",
      n("LogGamma(x)"), "LogGamma(x)")
print(f"Results: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
