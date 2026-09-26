#!/usr/bin/env python3
"""Class-8 answer-side identity probe (docs/class-porting.md Step 1(b) /
Step 2 / Step 7), and the measurement behind the class-8 port's
Derivative[n][f][x] representation decision.

(a) The native heads the class-8 RULES emit (translation-table rows) and
    the corpus answer heads Step 7 rewrites onto them: each must
    differentiate through the harness's OWN zero chain
    (test/corpus_driver.zero_chain) and, where Maxima evaluates it,
    float-evaluate at 0.7.
(b) Mathematica's formal derivative Derivative[n][f][u] (corpus spelling
    Derivative(n)(f)(u)): how the corpus spelling parses, and whether
    Maxima's own derivative noun 'diff(f(u), u, n) closes the zero chain
    for every order the 8.10 corpus uses (1, 2, 3, symbolic m / -1+m /
    1+m, negative -1/-2/-3), and where it does NOT (a composite argument
    u: Maxima applies no chain rule to an undeclared function).

Cited by: .scratch/class-ports/issues/01-class8-special-functions.md
(the Step-1 census comment and the Derivative design section).

Run:
  sh probes/answer-side/04-class8-answer-side-identities.run
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["MR_RULES_CORE"] = "0"  # zero_chain is pure text; skip the core
_argv = sys.argv[:]                # corpus_driver reads sys.argv AT IMPORT
sys.argv = [_argv[0]]
try:
    _spec = importlib.util.spec_from_file_location(
        "corpus_driver", os.path.join(ROOT, "test", "corpus_driver.py"))
    assert _spec is not None and _spec.loader is not None
    driver = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(driver)
finally:
    sys.argv = _argv

# (label, expression, mode): mode "chain" runs the residual through the
# driver's zero_chain(); None evaluates the expression and prints string().
CHECKS = [
    # (a) native heads
    ("A1 chain diff resid fresnel_s", "diff(fresnel_s(z), z) - sin(%pi*z^2/2)", "chain"),
    ("A2 chain diff resid fresnel_c", "diff(fresnel_c(z), z) - cos(%pi*z^2/2)", "chain"),
    ("A3 chain diff resid erfc", "diff(erfc(z), z) + 2*exp(-z^2)/sqrt(%pi)", "chain"),
    ("A4 chain diff resid expintegral_si", "diff(expintegral_si(z), z) - sin(z)/z", "chain"),
    ("A5 chain diff resid expintegral_ci", "diff(expintegral_ci(z), z) - cos(z)/z", "chain"),
    ("A6 chain diff resid expintegral_e", "diff(expintegral_e(n, z), z) + expintegral_e(n-1, z)", "chain"),
    ("A7 chain diff resid lambert_w", "diff(lambert_w(z), z) - lambert_w(z)/(z*(1+lambert_w(z)))", "chain"),
    ("A8 chain diff resid psi[n]", "diff(psi[n](z), z) - psi[n+1](z)", "chain"),
    ("A9 chain diff resid psi[-2]", "diff(psi[-2](z), z) - psi[-1](z)", "chain"),
    ("A10 chain diff resid log_gamma", "diff(log_gamma(z), z) - psi[0](z)", "chain"),
    ("A11 chain diff resid factorial", "diff(factorial(z), z) - factorial(z)*psi[0](z+1)", "chain"),
    ("A12 chain diff resid gamma", "diff(gamma(z), z) - gamma(z)*psi[0](z)", "chain"),
    ("A13 chain diff resid hypergeometric 3F3", "diff(hypergeometric([1,1,1],[2,2,2],z), z) - hypergeometric([2,2,2],[3,3,3],z)/8", "chain"),
    ("A14 expintegral_e(1,z) stays", "expintegral_e(1, z)", None),
    ("A15 hypergeometric([1,1],[3/2,2],z) stays", "hypergeometric([1,1],[3/2,2],z)", None),
    ("A16 Zeta(2,z) (no Hurwitz native)", "Zeta(2, z)", None),
    ("A17 diff Zeta(2,z) (a noun)", "diff(Zeta(2, z), z)", None),
    ("E1 ev fresnel_s(0.7)", "float(fresnel_s(0.7))", None),
    ("E2 ev fresnel_c(0.7)", "float(fresnel_c(0.7))", None),
    ("E3 ev erfc(0.7)", "float(erfc(0.7))", None),
    ("E4 ev expintegral_e(2,0.7)", "float(expintegral_e(2, 0.7))", None),
    ("E5 ev lambert_w(0.7)", "float(lambert_w(0.7))", None),
    ("E6 ev log_gamma(0.7)", "float(log_gamma(0.7))", None),
    ("E7 ev psi[0](0.7)", "float(psi[0](0.7))", None),
    ("E8 ev psi[-2](0.7) (stays a noun)", "float(psi[-2](0.7))", None),
    ("E9 ev hypergeometric 3F3(0.7)", "float(hypergeometric([1,1,1],[2,2,2],0.7))", None),
    # (b) the formal derivative
    ("D1 corpus spelling, outer op", "?caar(Derivative(1)(f)(x))", None),
    ("D2 corpus spelling, innermost op", "?caar(?cadr(?cadr(Derivative(1)(f)(x))))", None),
    ("D3 chain corpus spelling d/dx D1 = D2", "diff(Derivative(1)(f)(x), x) - Derivative(2)(f)(x)", "chain"),
    ("N1 native noun op", "string(op('diff(f(x), x, 1)))", None),
    ("N2 native noun args", "args('diff(f(x), x, 1))", None),
    ("N3 chain d/dx f(x) = 'diff(f(x),x,1)", "diff(f(x), x) - 'diff(f(x), x, 1)", "chain"),
    ("N4 chain d/dx order 1 -> 2", "diff('diff(f(x), x, 1), x) - 'diff(f(x), x, 2)", "chain"),
    ("N5 chain d/dx order m -> m+1", "diff('diff(f(x), x, m), x) - 'diff(f(x), x, m+1)", "chain"),
    ("N6 chain d/dx order -1+m -> m", "diff('diff(f(x), x, -1+m), x) - 'diff(f(x), x, m)", "chain"),
    ("N7 chain d/dx order -1 -> f(x)", "diff('diff(f(x), x, -1), x) - f(x)", "chain"),
    ("N8 chain d/dx order -3 -> -2", "diff('diff(f(x), x, -3), x) - 'diff(f(x), x, -2)", "chain"),
    ("N9 order 0 built by funmake", "funmake(nounify(diff), [f(x), x, 0])", None),
    ("N10 order -1 noun is holdable", "'diff(f(x), x, -1)", None),
    ("N11 diff() refuses order -1", "errcatch(diff(f(x), x, -1))", None),
    ("N12 subst composite point", "subst(f(x)*g(x), x, 'diff(F(x), x, 1))", None),
    ("N13 chain no chain rule (composite)", "diff(F(f(x)*g(x)), x) - 'diff(F(f(x)*g(x)), f(x)*g(x), 1)*diff(f(x)*g(x), x)", "chain"),
    ("N14 chain identical answers cancel", "diff(F(f(x)*g(x)) - F(f(x)*g(x)), x)", "chain"),
    ("N15 numeric stage declines on a noun", "errcatch(float(ev('diff(f(x), x, 1), x=0.35)))", None),
    ("N16 subst of the noun by a symbol", "subst(y, 'diff(f(x), x, 1), 'diff(f(x), x, 1)*g(x))", None),
    ("N17 subst of a product misses its power", "subst(y, f(x)*g(x), 1/(1+f(x)^2*g(x)^2))", None),
]

lines = ["disp(build_info())$"]
for label, expr, mode in CHECKS:
    var = "x" if label[0] in "DN" else "z"
    body = driver.zero_chain(expr, var) if mode == "chain" else expr
    lines.append(f'disp(concat("{label:32s} = ", string({body})))$')

fd, mac = tempfile.mkstemp(prefix="mr-answer-side-", suffix=".mac")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    r = subprocess.run(
        ["maxima", "--very-quiet", "-b", mac],
        capture_output=True, text=True, timeout=600, cwd=ROOT)
finally:
    os.unlink(mac)
if r.returncode != 0:
    sys.stderr.write(r.stdout[-2000:] + r.stderr[-2000:])
    raise SystemExit(f"maxima exited {r.returncode}")

BUILD_PREFIXES = ("Maxima-version", "Maxima build date", "Host type",
                  "Lisp implementation type", "Lisp implementation version")
labels = [c[0] for c in CHECKS]
kept = []
for raw in r.stdout.splitlines():
    line = raw.strip()
    if line.startswith(BUILD_PREFIXES):
        kept.append(line)
        continue
    for lab in labels:
        if line.startswith(lab) and " = " in line:
            lab_part, val = line.split(" = ", 1)
            kept.append(f"{lab_part.strip()} = {val.strip()}")
            break
# Self-flag if the maxima output shape moves (house probe discipline).
assert len(kept) == len(BUILD_PREFIXES) + len(labels), kept

print(f"probe: class8-answer-side-identities   "
      f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print("\n".join(kept))
