#!/usr/bin/env python3
"""Class-7 answer-side identity probe (docs/class-porting.md Step 1(b) /
Step 2): the measurements behind the class-7 census's table decisions.

The class-7 answer-head census (probes/corpus/21-class7-answer-heads)
finds the section's answers spelled with NATIVE inverse-hyperbolic heads —
atanh( 8,769, asinh( 6,616, acosh( 5,854, acoth( 2,070, asech( 1,228,
acsch( 1,013 — and eleven non-native heads, every one already disposed
of by an existing HEAD_REWRITES row or marker reading. The rule side has
two heads the table does not yet translate, ArcSech and ArcCsch
(probes/translation/11-class7-syntax-census.out), and emits ArcTanh /
ArcSinh / ArcCosh through the RENAME table's %mr_ log-form shims. This
probe measures, in the installed build:

  (a) d/dz of each of the six inverse-hyperbolic natives closing to 0
      through the harness's OWN zero chain (test/corpus_driver.zero_chain);
  (b) each float-evaluable on its real domain, and complex off it (E7-E9);
  (c) the Mathematica conventions ArcSech[z] = ArcCosh[1/z],
      ArcCsch[z] = ArcSinh[1/z], ArcCoth[z] = ArcTanh[1/z] against Maxima's
      asech/acsch/acoth (zero chain on the difference's DERIVATIVE, and a
      float spot value of the difference);
  (d) what the simplifier does to a negated / reciprocal argument, and
      that logarc is off and ratsimp/radcan leave the heads alone (S) —
      the matcher sees the simplified form;
  (e) the singular points (N): Mathematica answers ComplexInfinity for
      ArcTanh[1]; Maxima's behaviour is recorded;
  (f) op() of an inverse-hyperbolic call is the native head symbol (H —
      7.3.7's EqQ[Head[tmp], ArcTanh|ArcCoth]), while the %mr_atanh /
      %mr_asinh shim BODIES are a product / a log (K), i.e. an integrand
      built through the shims no longer carries the head the class-7
      patterns look for.

Cited by: .scratch/class-ports/issues/04-class7-inverse-hyperbolic-functions.md
(the Step-1 census comment).

Run:
  sh probes/answer-side/06-class7-answer-side-identities.run
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
    ("A1 chain diff resid asinh", "diff(asinh(z), z) - 1/sqrt(1+z^2)", "chain"),
    ("A2 chain diff resid acosh", "diff(acosh(z), z) - 1/(sqrt(z-1)*sqrt(z+1))", "chain"),
    ("A3 chain diff resid atanh", "diff(atanh(z), z) - 1/(1-z^2)", "chain"),
    ("A4 chain diff resid acoth", "diff(acoth(z), z) - 1/(1-z^2)", "chain"),
    ("A5 chain diff resid asech", "diff(asech(z), z) + 1/(z*sqrt(1-z^2))", "chain"),
    ("A6 chain diff resid acsch", "diff(acsch(z), z) + 1/(z^2*sqrt(1+1/z^2))", "chain"),
    ("E1 ev asinh(0.7)", "float(asinh(0.7))", None),
    ("E2 ev acosh(1.7)", "float(acosh(1.7))", None),
    ("E3 ev atanh(0.7)", "float(atanh(0.7))", None),
    ("E4 ev acoth(1.7)", "float(acoth(1.7))", None),
    ("E5 ev asech(0.7)", "float(asech(0.7))", None),
    ("E6 ev acsch(0.7)", "float(acsch(0.7))", None),
    ("E7 ev acosh(0.7) (complex)", "rectform(float(acosh(0.7)))", None),
    ("E8 ev acoth(0.7) (complex)", "rectform(float(acoth(0.7)))", None),
    ("E9 ev asech(1.7) (complex)", "rectform(float(asech(1.7)))", None),
    ("C1 chain diff(asech(z)-acosh(1/z))", "diff(asech(z) - acosh(1/z), z)", "chain"),
    ("C2 chain diff(acsch(z)-asinh(1/z))", "diff(acsch(z) - asinh(1/z), z)", "chain"),
    ("C3 chain diff(acoth(z)-atanh(1/z))", "diff(acoth(z) - atanh(1/z), z)", "chain"),
    ("C4 asech(0.7)-acosh(1/0.7)", "float(asech(0.7) - acosh(1/0.7))", None),
    ("C5 acsch(1.7)-asinh(1/1.7)", "float(acsch(1.7) - asinh(1/1.7))", None),
    ("C6 acsch(-1.7)-asinh(-1/1.7)", "float(acsch(-1.7) - asinh(-1/1.7))", None),
    ("C7 acoth(1.7)-atanh(1/1.7)", "float(acoth(1.7) - atanh(1/1.7))", None),
    ("C8 acoth(-1.7)-atanh(-1/1.7)", "float(acoth(-1.7) - atanh(-1/1.7))", None),
    ("S1 asinh(-x)", "asinh(-x)", None),
    ("S2 acosh(-x)", "acosh(-x)", None),
    ("S3 atanh(-x)", "atanh(-x)", None),
    ("S4 acoth(-x)", "acoth(-x)", None),
    ("S5 asech(-x)", "asech(-x)", None),
    ("S6 acsch(-x)", "acsch(-x)", None),
    ("S7 atanh(1/x)", "atanh(1/x)", None),
    ("S8 acoth(1/x)", "acoth(1/x)", None),
    ("S9 asech(1/x)", "asech(1/x)", None),
    ("S10 acsch(1/x)", "acsch(1/x)", None),
    ("S11 logarc (the default)", "logarc", None),
    ("S12 ratsimp(atanh(c*x)^2+1)", "ratsimp(atanh(c*x)^2+1)", None),
    ("S13 radcan(acosh(c*x))", "radcan(acosh(c*x))", None),
    ("N1 errcatch(atanh(1))", "errcatch(atanh(1))", None),
    ("N2 errcatch(acoth(1))", "errcatch(acoth(1))", None),
    ("N3 acosh(1), asech(1), atanh(0)", "[acosh(1), asech(1), atanh(0)]", None),
    ("H1 op(atanh(1+2*x))", "op(atanh(1+2*x))", None),
    ("H2 op(acoth(1+2*x))", "op(acoth(1+2*x))", None),
    ("H3 op(asinh(1+2*x))", "op(asinh(1+2*x))", None),
    ("H4 op(acosh(1+2*x))", "op(acosh(1+2*x))", None),
    ("H5 op(asech(2*x))", "op(asech(2*x))", None),
    ("H6 op(acsch(2*x))", "op(acsch(2*x))", None),
    ("H7 is(op(atanh(1+2*x)) = atanh)", "is(op(atanh(1+2*x)) = atanh)", None),
    ("K1 op of the %mr_atanh shim body", "op(1/2*log((1+c*x)/(1-c*x)))", None),
    ("K2 op of the %mr_asinh shim body", "op(log(c*x+sqrt((c*x)^2+1)))", None),
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

print(f"probe: class7-answer-side-identities   "
      f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print("\n".join(kept))
