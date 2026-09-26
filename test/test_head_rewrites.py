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
# --- class 5 (2026-09-25): no new row. The section's answers are native
# inverse-trig texts plus heads earlier rows already cover
# (probes/corpus/18-class5-answer-heads.out); corpus excerpts, verbatim.
check("class 5: Si/Ci of an acos argument, acos kept",
      n("-5/64*Si(acos(a*x))/a^7-9/64*Si(3*acos(a*x))/a^7"),
      "-5/64*expintegral_si(acos(a*x))/a^7-9/64*expintegral_si(3*acos(a*x))/a^7")
check("class 5: 2-arg GAMMA of an acos argument",
      n("2^(-4-n)*acos(a*x)^n*GAMMA(1+n,-2*%i*acos(a*x))/(a^4*(-%i*acos(a*x))^n)"),
      "2^(-4-n)*acos(a*x)^n*gamma_incomplete(1+n,-2*%i*acos(a*x))/(a^4*(-%i*acos(a*x))^n)")
check("class 5: FresnelC of sqrt(acos), acos kept",
      n("-1/80*FresnelC(sqrt(10/%pi)*sqrt(acos(a*x)))*sqrt(1/10*%pi)/a^5"),
      "-1/80*fresnel_c(sqrt(10/%pi)*sqrt(acos(a*x)))*sqrt(1/10*%pi)/a^5")
check("class 5: asec/polylog answer untouched",
      n("1/10*%i*asec(a*x^5)^2-1/5*asec(a*x^5)*log(1+%e^(2*%i*asec(a*x^5)))"
        "+1/10*%i*polylog(2,-%e^(2*%i*asec(a*x^5)))"),
      "1/10*%i*asec(a*x^5)^2-1/5*asec(a*x^5)*log(1+%e^(2*%i*asec(a*x^5)))"
      "+1/10*%i*polylog(2,-%e^(2*%i*asec(a*x^5)))")
check("class 5: the six inverse-trig natives untouched",
      n("asin(x)+acos(x)+atan(x)+acot(x)+asec(x)+acsc(x)"),
      "asin(x)+acos(x)+atan(x)+acot(x)+asec(x)+acsc(x)")
# --- class 7 (2026-09-25): no new row. The section's answers are native
# inverse-hyperbolic texts plus heads earlier rows already cover
# (probes/corpus/21-class7-answer-heads.out); corpus excerpts, verbatim.
check("class 7: Chi/Shi of an asinh argument, asinh kept",
      n("+9/64*Chi(3*asinh(a*x))/a^7-5/64*Shi(asinh(a*x))/a^7"),
      "+9/64*expintegral_chi(3*asinh(a*x))/a^7-5/64*expintegral_shi(asinh(a*x))/a^7")
check("class 7: 2-arg GAMMA of an asinh argument",
      n("asinh(a*x)^n*GAMMA(1+n,-3*asinh(a*x))/(3^n*a^5*(-asinh(a*x))^n)"),
      "asinh(a*x)^n*gamma_incomplete(1+n,-3*asinh(a*x))/(3^n*a^5*(-asinh(a*x))^n)")
check("class 7: HypergeometricPFQ of an atanh-section argument",
      n("HypergeometricPFQ([1,13/4,13/4],[15/4,17/4],-(c+d*x)^2)/(d*e^3)"),
      "hypergeometric([1,13/4,13/4],[15/4,17/4],-(c+d*x)^2)/(d*e^3)")
check("class 7: asech/acsch/acoth answers untouched",
      n("-1/4*a^4*acsch(a+b*x)/b^4+1/4*x^4*asech(a+b*x)+1/6*x^6*acoth(a*x)"),
      "-1/4*a^4*acsch(a+b*x)/b^4+1/4*x^4*asech(a+b*x)+1/6*x^6*acoth(a*x)")
check("class 7: the six inverse-hyperbolic natives untouched",
      n("asinh(x)+acosh(x)+atanh(x)+acoth(x)+asech(x)+acsch(x)"),
      "asinh(x)+acosh(x)+atanh(x)+acoth(x)+asech(x)+acsch(x)")
# --- class 4 (2026-09-25): one STRUCTURAL rewrite, Hypergeometric2F1(a,b,c,z)
# -> hypergeometric([a,b],[c],z) -- the list reshape the rules' emitter case
# makes (generator/generate_rules.py, Hypergeometric2F1). Three
# occurrences over two corpus entries, both in 4.1.1.3 (probes/corpus/14-...).
check("class 4: Hypergeometric2F1 reshaped to hypergeometric([a,b],[c],z)",
      n("x*Hypergeometric2F1(1/2,1/2,3/2,x^2)"),
      "x*hypergeometric([1/2,1/2],[3/2],x^2)")
check("class 4: a corpus excerpt, nested parentheses in the arguments",
      n("Hypergeometric2F1(1/2*(1-p),1/2*(1-p),1/2*(3-p),(cos(e+f*x)^2-b^2)/(1-b^2))*g"),
      "hypergeometric([1/2*(1-p),1/2*(1-p)],[1/2*(3-p)],(cos(e+f*x)^2-b^2)/(1-b^2))*g")
check("class 4: a Hypergeometric2F1 argument rewritten inside (FresnelC)",
      n("Hypergeometric2F1(1,2,3,FresnelC(x))"),
      "hypergeometric([1,2],[3],fresnel_c(x))")
check("class 4: a wrong-arity Hypergeometric2F1 is left as written",
      n("Hypergeometric2F1(1,2,x)"), "Hypergeometric2F1(1,2,x)")
check("class 4: a longer name is left alone",
      n("MyHypergeometric2F1(1,2,3,x)"), "MyHypergeometric2F1(1,2,3,x)")
check("class 4: AppellF1 untouched (no native: the ceiling)",
      n("AppellF1(1/2,-1/2*p,1,3/2,cos(e+f*x)^2,x)"),
      "AppellF1(1/2,-1/2*p,1,3/2,cos(e+f*x)^2,x)")
check("class 4: the six trig natives and Si/Ci answers",
      n("sin(x)+cos(x)+tan(x)+cot(x)+sec(x)+csc(x)+Si(2*x)-Ci(x)"),
      "sin(x)+cos(x)+tan(x)+cot(x)+sec(x)+csc(x)+expintegral_si(2*x)-expintegral_ci(x)")
print(f"Results: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
