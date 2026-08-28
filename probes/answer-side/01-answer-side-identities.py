#!/usr/bin/env python3
"""Answer-side identity probe (milestone-2 close-out): the two
special-function conventions the class-2 answer normalization
(test/corpus_driver.py HEAD_REWRITES) depends on, measured on the
installed build rather than cited from the answer-head census (a
static head count that measures nothing about the identities):

  (a) the corpus GAMMA(a, z) is the UPPER incomplete gamma, and this
      build's gamma_incomplete(a, z) is the same: its symbolic diff
      wrt z is -z^(a-1) %e^-z (the general-a rule), and the value pins
      gamma_incomplete(1, z) = %e^-z and gamma_incomplete(2, z) =
      (z+1) %e^-z close within the harness zero chain (the pins do not
      close symbolically in this build — gamma_incomplete(1, z) is not
      auto-reduced — they close on the chain's numeric stage, which is
      how the driver verifies them);
  (b) d/dz expintegral_ei(z) = %e^z/z, the residual closing to 0
      within the chain.

The zero chain is the harness's own: test/corpus_driver.py's
zero_chain() is imported (MR_RULES_CORE=0 — the chain is pure text, no
core needed) and each residual is run through it exactly as the driver
would. Re-running on a build change is the standing check that the
normalization still maps onto differentiable native heads.

Cited by: docs/corpus-class2-baseline-uplift.md section 2 and
test/corpus_driver.py's HEAD_REWRITES comment.

Run:
  sh probes/answer-side/01-answer-side-identities.run
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

G_DIFF = "diff(gamma_incomplete(a, z), z)"
# (label, expression, mode): mode "chain" runs the residual through
# the driver's zero_chain(); the other modes are the direct
# ratsimp/display forms.
CHECKS = [
    ("A1 diff rule general a", G_DIFF, None),
    ("A2 ratsimp diff resid general a",
     f"ratsimp({G_DIFF} + z^(a-1)*%e^(-z))", None),
    ("A3 chain diff resid general a",
     f"{G_DIFF} + z^(a-1)*%e^(-z)", "chain"),
    ("A4 ratsimp gamma(1,z) - %e^-z",
     "ratsimp(gamma_incomplete(1, z) - %e^(-z))", None),
    ("A4 chain gamma(1,z) - %e^-z",
     "gamma_incomplete(1, z) - %e^(-z)", "chain"),
    ("A5 ratsimp gamma(2,z) - (z+1)%e^-z",
     "ratsimp(gamma_incomplete(2, z) - (z+1)*%e^(-z))", None),
    ("A5 chain gamma(2,z) - (z+1)%e^-z",
     "gamma_incomplete(2, z) - (z+1)*%e^(-z)", "chain"),
    ("B1 diff rule Ei", "diff(expintegral_ei(z), z)", None),
    ("B2 ratsimp diff resid Ei",
     "ratsimp(diff(expintegral_ei(z), z) - %e^z/z)", None),
    ("B3 chain diff resid Ei",
     "diff(expintegral_ei(z), z) - %e^z/z", "chain"),
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

print(f"probe: answer-side-identities   "
      f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print("\n".join(kept))
