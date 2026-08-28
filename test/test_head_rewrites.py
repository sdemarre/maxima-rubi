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
print(f"Results: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
