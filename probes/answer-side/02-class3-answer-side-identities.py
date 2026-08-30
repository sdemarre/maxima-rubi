#!/usr/bin/env python3
"""Class-3 answer-side identity probe (milestone-3 close-out): the five
special-function conventions the class-3 answer normalization
(test/corpus_driver.py HEAD_REWRITES, the Chi(/Shi(/Si(/Ci(/Li( rows)
depends on, measured on the installed build rather than cited from the
generation smoke (which measured rule LOADING, not the identities):

  (a) d/dz expintegral_shi(z) = sinh(z)/z, d/dz expintegral_chi(z) =
      cosh(z)/z, d/dz expintegral_si(z) = sin(z)/z, d/dz
      expintegral_ci(z) = cos(z)/z, d/dz expintegral_li(z) = 1/log(z)
      — every residual closing to 0 within the harness zero chain;
  (b) all five are bound and float-evaluable (the plan recon's
      boundness idiom — this build has no boundp/functionp: boundp
      prints as the unevaluated noun boundp(gamma)), and the SHORT
      names shi/chi/si/ci are unbound nouns (the naming trap a naive
      `Shi(` -> `shi(` row would step in);
  (c) lowercase li is a DISTINCT bound token (the native
      polylogarithm, describe(li, exact): "Function: li [<s>] (<z>)"):
      the curried form li[s](z) float-evaluates while polylog(2, z)
      stays a noun — so the uppercase Li( row cannot collide with it,
      and the un-evaluability of polylog(2, .) is the measured locus
      of the deferred class-3 polylog-derivative work
      (.scratch/class3-polylog-ceiling/issues/).

The zero chain is the harness's own: test/corpus_driver.py's
zero_chain() is imported (MR_RULES_CORE=0 — the chain is pure text, no
core needed) and each residual is run through it exactly as the driver
would. Re-running on a build change is the standing check that the
normalization still maps onto differentiable native heads.

Cited by: docs/corpus-class3-baseline-uplift.md section 2 and
test/corpus_driver.py's HEAD_REWRITES comment.

Run:
  sh probes/answer-side/02-class3-answer-side-identities.run
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["MR_RULES_CORE"] = "0"  # zero_chain is pure text; skip the core
_spec = importlib.util.spec_from_file_location(
    "corpus_driver", os.path.join(ROOT, "test", "corpus_driver.py"))
assert _spec is not None and _spec.loader is not None
driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(driver)

# (label, expression, mode): mode "chain" runs the residual through
# the driver's zero_chain(); the other modes are the direct forms.
CHECKS = [
    ("S1 ev expintegral_shi(0.5)", "ev(expintegral_shi(0.5))", None),
    ("S2 chain diff resid shi",
     "diff(expintegral_shi(z), z) - sinh(z)/z", "chain"),
    ("C1 ev expintegral_chi(0.5)", "ev(expintegral_chi(0.5))", None),
    ("C2 chain diff resid chi",
     "diff(expintegral_chi(z), z) - cosh(z)/z", "chain"),
    ("I1 ev expintegral_si(0.5)", "ev(expintegral_si(0.5))", None),
    ("I2 chain diff resid si",
     "diff(expintegral_si(z), z) - sin(z)/z", "chain"),
    ("Q1 ev expintegral_ci(0.5)", "ev(expintegral_ci(0.5))", None),
    ("Q2 chain diff resid ci",
     "diff(expintegral_ci(z), z) - cos(z)/z", "chain"),
    ("L1 ev expintegral_li(0.5)", "ev(expintegral_li(0.5))", None),
    ("L2 chain diff resid li",
     "diff(expintegral_li(z), z) - 1/log(z)", "chain"),
    ("N1 ev shi(0.5) (naming trap)", "ev(shi(0.5))", None),
    ("N2 ev chi(0.5) (naming trap)", "ev(chi(0.5))", None),
    ("N3 ev si(0.5) (naming trap)", "ev(si(0.5))", None),
    ("N4 ev ci(0.5) (naming trap)", "ev(ci(0.5))", None),
    ("M1 ev li[2](0.5) (bound curried)", "ev(li[2](0.5))", None),
    ("M2 ev polylog(2,0.5) (stays noun)", "ev(polylog(2, 0.5))", None),
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

# The .out carries the build stamp and the measured values only (the
# batch-mode input echo of the inlined chain text is ~40 KB of
# deterministic driver output — the committed .py IS the input).
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

print(f"probe: class3-answer-side-identities   "
      f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print("\n".join(kept))
