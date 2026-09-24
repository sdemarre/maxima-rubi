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
# --- class 8 (2026-09-25) ---
# GAMMA( / Ei( by arity: the class-2 readings kept, the class-8 ones added
check("GAMMA 1-arg -> gamma", n("GAMMA(n)*log(x)"), "gamma(n)*log(x)")
check("GAMMA 2-arg still gamma_incomplete", n("GAMMA(n, a+b*x)"),
      "gamma_incomplete(n, a+b*x)")
check("GAMMA 1-arg whose argument holds a comma inside parens",
      n("GAMMA(f(a, b))"), "gamma(f(a, b))")
check("Ei 2-arg -> expintegral_e", n("-Ei(2,b*x)/b"), "-expintegral_e(2,b*x)/b")
check("Ei 1-arg still expintegral_ei", n("Ei(b*x)"), "expintegral_ei(b*x)")
check("Ei 1 and 2-arg in one line", n("Ei(1,b*x)+Ei(b*x)"),
      "expintegral_e(1,b*x)+expintegral_ei(b*x)")
check("GAMMA/Ei of arity 3 left as written", n("GAMMA(a,b,c)+Ei(a,b,c)"),
      "GAMMA(a,b,c)+Ei(a,b,c)")
# the class-8 native rows
check("ProductLog -> lambert_w", n("ProductLog(a+b*x)^2"), "lambert_w(a+b*x)^2")
check("FresnelS / FresnelC", n("FresnelS(b*x)+FresnelC(b*x)"),
      "fresnel_s(b*x)+fresnel_c(b*x)")
check("lnGAMMA -> log_gamma (and no GAMMA row inside it)",
      n("lnGAMMA(a+b*x)/b"), "log_gamma(a+b*x)/b")
check("HypergeometricPFQ -> hypergeometric, list args kept",
      n("HypergeometricPFQ([1,1,1],[2,2,2],-b*x)"),
      "hypergeometric([1,1,1],[2,2,2],-b*x)")
check("Factorial -> factorial", n("Factorial(a+b*x)^n"), "factorial(a+b*x)^n")
check("natives untouched", n("lambert_w(x)+fresnel_s(x)+log_gamma(x)+psi[0](x)"),
      "lambert_w(x)+fresnel_s(x)+log_gamma(x)+psi[0](x)")
check("Zeta untouched (inert, the AppellF1 precedent)", n("Zeta(2,a+b*x)"),
      "Zeta(2,a+b*x)")
# Psi(n, z) -> psi[n](z)
check("Psi -> psi[n](z)", n("x^2*Psi(0,a+b*x)/b"), "x^2*psi[0](a+b*x)/b")
check("Psi negative order", n("2*Psi(-2,a+b*x)/b^3"), "2*psi[-2](a+b*x)/b^3")
check("Psi 1-arg left as written", n("Psi(x)"), "Psi(x)")
check("Psi inside a longer name intact", n("MyPsi(0,x)"), "MyPsi(0,x)")
# Derivative(A)(B)(C) -> %mr_derivative(A, B, C)
check("Derivative order 1", n("Derivative(1)(f)(x)"), "%mr_derivative(1, f, x)")
check("Derivative symbolic order", n("Derivative(-1+m)(f)(x)"),
      "%mr_derivative(-1+m, f, x)")
check("Derivative at a composite point",
      n("Derivative(1)(F)(f(x)*g(x))"), "%mr_derivative(1, F, f(x)*g(x))")
check("Derivative nested in the point",
      n("Derivative(1)(F)(Derivative(-1+m)(f)(x)^2*Derivative(-1+n)(g)(x))"),
      "%mr_derivative(1, F, %mr_derivative(-1+m, f, x)^2*%mr_derivative(-1+n, g, x))")
check("Derivative inside a CannotIntegrate answer",
      n("CannotIntegrate(f(g(x))*Derivative(1)(g)(x),x)"),
      "CannotIntegrate(f(g(x))*%mr_derivative(1, g, x),x)")
check("Derivative powers and products",
      n("1/2*Derivative(1)(u)(x)^2"), "1/2*%mr_derivative(1, u, x)^2")
check("a Derivative( without three groups is left as written",
      n("Derivative(1)(f)"), "Derivative(1)(f)")
check("Derivative inside a longer name intact", n("MyDerivative(1)(f)(x)"),
      "MyDerivative(1)(f)(x)")
check("idempotent on a rewritten text",
      n(n("Derivative(2)(f)(x)*Psi(1,x)*GAMMA(z)*Ei(1,z)")),
      "%mr_derivative(2, f, x)*psi[1](x)*gamma(z)*expintegral_e(1,z)")
print(f"Results: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
