#!/usr/bin/env python3
"""Are the 9 section-6 entries the %i fold "loses" actually wrong?

Probe 05 (05-ifold-all-sections.out, fold under radexpand:false,
logexpand:false) finds 9 entries whose record class is PASS and whose folded
answer the checker classes `unverified`: 6.4.2 e14/e22/e26/e47 and 6.7.1
e57/e58/e64/e65/e66, all fractional powers of cot/sin of an imaginary
argument. Their ORIGINAL answers also mismatch in the checker's numeric
check; they pass only by the symbolic proof chainA.1, which times out on the
folded shape. Maxima's own float evaluation is no referee here: substituting
numbers re-simplifies powers such as (%i*c)^(4/3) under the default
radexpand:true.

So this probe evaluates outside Maxima: rubi's answer (R0), the folded
answer (R1) and the integrand are printed by Maxima (string()), translated
to Python, and evaluated with cmath -- principal branches throughout. For
each entry at three real points it prints both values and
|d/dx answer - integrand| by a central difference (h = 1e-6).

    python3 probes/leaf-size/06-ifold-principal-branch.py \\
        > probes/leaf-size/06-ifold-principal-branch.out

The fold is probe 05's (same flags, same text).
"""

import cmath
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.argv = [sys.argv[0]]
sys.path.insert(0, os.path.join(ROOT, "test"))
sys.path.insert(0, os.path.join(ROOT, "probes", "leaf-size"))
os.chdir(ROOT)
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "p05", os.path.join(ROOT, "probes", "leaf-size", "05-ifold-all-sections.py"))
p05 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p05)
d = p05.d

LABELS = [
    "6 Hyperbolic functions/6.4 Hyperbolic cotangent/6.4.2 Hyperbolic cotangent functions.mac e14 L25",
    "6 Hyperbolic functions/6.4 Hyperbolic cotangent/6.4.2 Hyperbolic cotangent functions.mac e22 L39",
    "6 Hyperbolic functions/6.4 Hyperbolic cotangent/6.4.2 Hyperbolic cotangent functions.mac e26 L43",
    "6 Hyperbolic functions/6.4 Hyperbolic cotangent/6.4.2 Hyperbolic cotangent functions.mac e47 L68",
    "6 Hyperbolic functions/6.7 Miscellaneous/6.7.1 Hyperbolic functions.mac e57 L72",
    "6 Hyperbolic functions/6.7 Miscellaneous/6.7.1 Hyperbolic functions.mac e58 L73",
    "6 Hyperbolic functions/6.7 Miscellaneous/6.7.1 Hyperbolic functions.mac e64 L79",
    "6 Hyperbolic functions/6.7 Miscellaneous/6.7.1 Hyperbolic functions.mac e65 L80",
    "6 Hyperbolic functions/6.7 Miscellaneous/6.7.1 Hyperbolic functions.mac e66 L81",
]
POINTS = [(0.7, 0.3, 1.3), (0.2, 1.7, 0.6), (1.2, 0.4, 0.5)]   # (a, b, x); c = a, d = b

ENV = {k: getattr(cmath, k) for k in ("sin", "cos", "tan", "sinh", "cosh", "tanh", "log",
                                       "atan", "sqrt", "atanh", "asinh", "acosh", "asin", "acos")}
ENV.update(cot=lambda z: 1 / cmath.tan(z), coth=lambda z: 1 / cmath.tanh(z),
           sec=lambda z: 1 / cmath.cos(z), csc=lambda z: 1 / cmath.sin(z),
           sech=lambda z: 1 / cmath.cosh(z), csch=lambda z: 1 / cmath.sinh(z))


def py(s):
    return s.replace("^", "**").replace("%i", "1j")


def texts(label):
    els = p05.elements(label)
    text = d.build_text(d.normalize_heads(els[0]), els[1], d.normalize_heads(els[3]), None, None)
    call = f"mr_r: rubi(mr_f, {els[1]})$"
    assert text.count(call) == 1 and text.count(p05.LOADS) == 1
    text = text.replace(call, f"mr_r0: rubi(mr_f, {els[1]})$")
    text = text.replace(p05.LOADS, p05.LOADS + p05.IFOLD + p05.FOLD
                        + 'linel: 100000$ print("R0", string(mr_r0))$ '
                          'print("R1", string(mr_r))$ print("F", string(mr_f))$ quit()$\n')
    out, _ = d.maxima_run(text, 60, [])
    ex = {}
    for ln in (x.strip() for x in out.splitlines()):
        for t in ("R0", "R1", "F"):
            if ln.startswith(t + " ") and t not in ex:
                ex[t] = ln[len(t) + 1:]
    return ex


def main():
    print(f"# {len(LABELS)} entries; R0 rubi's answer, R1 folded (probe 05, flags {p05.FLAGS});"
          " cmath principal branches")
    worst = 0.0
    for label in LABELS:
        ex = texts(label)
        print(f"== {label}")
        for a, b, x in POINTS:
            e = dict(ENV, a=a, b=b, c=a, d=b)
            vals = {}
            for t in ("R0", "R1"):
                f = lambda xx, t=t: eval(py(ex[t]), dict(e, x=xx))  # noqa: E731
                der = (f(x + 1e-6) - f(x - 1e-6)) / 2e-6
                err = abs(der - eval(py(ex["F"]), dict(e, x=x)))
                vals[t] = f(x)
                worst = max(worst, err)
                print(f"   {t} x={x} value={f(x):.10g} |d/dx - integrand|={err:.2e}")
            print(f"   |R0 - R1| = {abs(vals['R0'] - vals['R1']):.2e}")
    print(f"# worst |d/dx - integrand| over all: {worst:.2e}")


if __name__ == "__main__":
    main()
