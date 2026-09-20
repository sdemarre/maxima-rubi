#!/usr/bin/env python3
"""Class-6 answer-side identity probe (docs/class-porting.md Step 1(b) /
Step 2): the measurement behind the class-6 census's headline claim that
the section needs **no new HEAD_REWRITES row**.

The class-6 answer-head census (probes/corpus/12-class6-answer-heads)
finds exactly ten non-native call heads on the section's 5,080 entry
lines. Six are Rubi-notation special functions already rewritten by rows
that classes 2 and 3 installed (GAMMA 266, Ei 6 -> probes/answer-side/01;
Chi 611, Shi 605, Si 32, Ci 32 -> probes/answer-side/02). The other four
are not rewrite candidates: Unintegrable( 364 and CannotIntegrate( 47 are
the corpus's own markers (test/corpus_driver.py:655 reads them before
normalization), AppellF1( 24 has no native (the class-3 structural
ceiling, unchanged), and F( 8 is a FREE function symbol in the integrand
(the class-2 F0( reading) whose entries carry a CannotIntegrate answer.

What is NOT yet on the record is the other side: the 28,000-odd native
hyperbolic occurrences the section's answers are actually made of. This
probe measures them, because "no rewrite needed" is only sound if the
heads both sides already spell natively are differentiable and
float-evaluable in the installed build — the same bar Step 2 sets for a
renamed head:

  (a) d/dz of each of cosh, sinh, tanh, coth, sech, csch, closing to 0
      through the harness's OWN zero chain (test/corpus_driver.zero_chain),
      not by eyeball;
  (b) each float-evaluable at 0.7 (the boundness idiom: this build has no
      working boundp/functionp);
  (c) the two class-6 RULE-side special heads, CoshIntegral and
      SinhIntegral, map onto expintegral_chi / expintegral_shi — the
      derivatives probe 02 measured for the class-3 ANSWER side, re-run
      here because class 6 is the first section to emit them from a
      replacement.

Re-running on a build change is the standing check that class 6's
answer side still needs no normalization.

Cited by: .scratch/class-ports/issues/03-class6-hyperbolic-functions.md
(the Step-1 census comment).

Run:
  sh probes/answer-side/03-class6-answer-side-identities.run
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
    ("H1 chain diff resid cosh", "diff(cosh(z), z) - sinh(z)", "chain"),
    ("H2 chain diff resid sinh", "diff(sinh(z), z) - cosh(z)", "chain"),
    ("H3 chain diff resid tanh", "diff(tanh(z), z) - sech(z)^2", "chain"),
    ("H4 chain diff resid coth", "diff(coth(z), z) + csch(z)^2", "chain"),
    ("H5 chain diff resid sech", "diff(sech(z), z) + sech(z)*tanh(z)", "chain"),
    ("H6 chain diff resid csch", "diff(csch(z), z) + csch(z)*coth(z)", "chain"),
    ("E1 ev cosh(0.7)", "ev(cosh(0.7))", None),
    ("E2 ev sinh(0.7)", "ev(sinh(0.7))", None),
    ("E3 ev tanh(0.7)", "ev(tanh(0.7))", None),
    ("E4 ev coth(0.7)", "ev(coth(0.7))", None),
    ("E5 ev sech(0.7)", "ev(sech(0.7))", None),
    ("E6 ev csch(0.7)", "ev(csch(0.7))", None),
    # the two rule-side special heads class 6 emits from replacements
    ("R1 chain diff resid chi",
     "diff(expintegral_chi(z), z) - cosh(z)/z", "chain"),
    ("R2 chain diff resid shi",
     "diff(expintegral_shi(z), z) - sinh(z)/z", "chain"),
    ("R3 ev expintegral_chi(0.7)", "ev(expintegral_chi(0.7))", None),
    ("R4 ev expintegral_shi(0.7)", "ev(expintegral_shi(0.7))", None),
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

print(f"probe: class6-answer-side-identities   "
      f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print("\n".join(kept))
