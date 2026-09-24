#!/usr/bin/env python3
"""Class-5 answer-side identity probe (docs/class-porting.md Step 1(b) /
Step 2): the measurements behind the class-5 census's table decisions.

The class-5 answer-head census (probes/corpus/18-class5-answer-heads)
finds the section's answers spelled with NATIVE inverse-trig heads —
asin( 8,859, acos( 1,739, atan( 9,087, acot( 731, asec( 1,057, acsc(
1,121 — and nine non-native heads, every one already disposed of by an
existing HEAD_REWRITES row or marker reading. The rule side has two
heads the table does not yet translate, ArcSec and ArcCsc (31 rules
each, probes/translation/10-class5-syntax-census.out). This probe
measures, in the installed build:

  (a) d/dz of each of the six inverse-trig natives closing to 0 through
      the harness's OWN zero chain (test/corpus_driver.zero_chain);
  (b) each float-evaluable (asec/acsc at 1.7: their real domain is
      |z| >= 1; at 0.7 they are complex, recorded too);
  (c) the Mathematica conventions ArcSec[z] = ArcCos[1/z],
      ArcCsc[z] = ArcSin[1/z], ArcCot[z] = ArcTan[1/z] against Maxima's
      asec/acsc/acot (zero chain on the difference's DERIVATIVE, and a
      float spot value of the difference at 1.7 and -1.7);
  (d) what the simplifier does to a negated argument (S rows) — the
      matcher sees the simplified form, so an odd-function rewrite
      changes which rule shape an integrand presents;
  (e) Discriminant (5.3.7 r27/r28): Maxima's poly_discriminant against
      Mathematica's Discriminant on a symbolic quadratic and cubic
      (Mathematica: b^2-4ac; and b^2c^2-4ac^3-4b^3d+18abcd-27a^2d^2);
  (f) op() of an inverse-trig call is the head symbol the table emits
      for the bare head atom (EqQ[Head[tmp], ArcTan], 5.3.7 r27/r28).

Cited by: .scratch/class-ports/issues/02-class5-inverse-trig-functions.md
(the Step-1 census comment).

Run:
  sh probes/answer-side/05-class5-answer-side-identities.run
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
# driver's zero_chain(); None runs the expression directly.
CHECKS = [
    ("A1 chain diff resid asin", "diff(asin(z), z) - 1/sqrt(1-z^2)", "chain"),
    ("A2 chain diff resid acos", "diff(acos(z), z) + 1/sqrt(1-z^2)", "chain"),
    ("A3 chain diff resid atan", "diff(atan(z), z) - 1/(1+z^2)", "chain"),
    ("A4 chain diff resid acot", "diff(acot(z), z) + 1/(1+z^2)", "chain"),
    ("A5 chain diff resid asec", "diff(asec(z), z) - 1/(z^2*sqrt(1-1/z^2))", "chain"),
    ("A6 chain diff resid acsc", "diff(acsc(z), z) + 1/(z^2*sqrt(1-1/z^2))", "chain"),
    ("E1 ev asin(0.7)", "float(asin(0.7))", None),
    ("E2 ev acos(0.7)", "float(acos(0.7))", None),
    ("E3 ev atan(0.7)", "float(atan(0.7))", None),
    ("E4 ev acot(0.7)", "float(acot(0.7))", None),
    ("E5 ev asec(1.7)", "float(asec(1.7))", None),
    ("E6 ev acsc(1.7)", "float(acsc(1.7))", None),
    ("E7 ev asec(0.7) (complex)", "rectform(float(asec(0.7)))", None),
    ("E8 ev acsc(0.7) (complex)", "rectform(float(acsc(0.7)))", None),
    ("C1 chain diff(asec(z)-acos(1/z))", "diff(asec(z) - acos(1/z), z)", "chain"),
    ("C2 chain diff(acsc(z)-asin(1/z))", "diff(acsc(z) - asin(1/z), z)", "chain"),
    ("C3 chain diff(acot(z)-atan(1/z))", "diff(acot(z) - atan(1/z), z)", "chain"),
    ("C4 asec(1.7)-acos(1/1.7)", "float(asec(1.7) - acos(1/1.7))", None),
    ("C5 asec(-1.7)-acos(-1/1.7)", "float(asec(-1.7) - acos(-1/1.7))", None),
    ("C6 acsc(-1.7)-asin(-1/1.7)", "float(acsc(-1.7) - asin(-1/1.7))", None),
    ("C7 acot(-1.7)-atan(-1/1.7)", "float(acot(-1.7) - atan(-1/1.7))", None),
    ("S1 asin(-x)", "asin(-x)", None),
    ("S2 acos(-x)", "acos(-x)", None),
    ("S3 atan(-x)", "atan(-x)", None),
    ("S4 acot(-x)", "acot(-x)", None),
    ("S5 asec(-x)", "asec(-x)", None),
    ("S6 acsc(-x)", "acsc(-x)", None),
    ("S7 atan(1/x)", "atan(1/x)", None),
    ("S8 acot(1/x)", "acot(1/x)", None),
    ("D1 poly_discriminant quadratic", "expand(poly_discriminant(a*x^2+b*x+c, x))", None),
    ("D2 quadratic minus b^2-4ac", "expand(poly_discriminant(a*x^2+b*x+c, x) - (b^2-4*a*c))", None),
    ("D3 cubic minus Mathematica", "expand(poly_discriminant(a*x^3+b*x^2+c*x+d, x) - (b^2*c^2-4*a*c^3-4*b^3*d+18*a*b*c*d-27*a^2*d^2))", None),
    ("D4 quadratic 1+x^2 (numeric)", "poly_discriminant(1+x^2, x)", None),
    ("H1 op(atan(1+2*x))", "op(atan(1+2*x))", None),
    ("H2 op(acot(1+2*x))", "op(acot(1+2*x))", None),
    ("H3 is(op(atan(1+2*x)) = atan)", "is(op(atan(1+2*x)) = atan)", None),
]

lines = ["disp(build_info())$"]
for label, expr, mode in CHECKS:
    body = driver.zero_chain(expr, "z") if mode == "chain" else expr
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

print(f"probe: class5-answer-side-identities   "
      f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print("\n".join(kept))
