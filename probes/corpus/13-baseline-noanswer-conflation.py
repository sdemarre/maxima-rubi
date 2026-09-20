#!/usr/bin/env python3
"""The native-`integrate` baseline probe over-credits itself, and the
class-6 A/B is where it finally changes a verdict.

probes/corpus/probe-integrate-sample.py classifies an entry `no-answer`
whenever `integrate` comes back as its own noun — in BOTH branches of its
classifier. That is right in one branch and wrong in the other:

  corpus expects a noun  -> integrate returns a noun -> no-answer.  CORRECT:
      declining a genuinely unintegrable entry is the right answer, PASS.
  corpus expects an ANSWER -> integrate returns a noun -> no-answer.  WRONG:
      `integrate` simply failed, and the entry is scored PASS anyway.

test/corpus_driver.py splits exactly that second case out as `deferred`
(FAIL) and says so in its own class table: "deferred: rubi returned a
TOP-LEVEL no-answer noun; corpus expects an ANSWER (a coverage gap ...
distinct from no-answer, which is the honest match on a noun-expected
entry; T5's table predates this distinction". The distinction was added
to the DRIVER on 2026-08-25 and never back-ported to the BASELINE PROBE,
so every Step-8 baseline since has been scored on the older, looser
scheme while its Step-9 package counterpart was scored on the stricter
one. The runbook's A/B therefore compares two different rulers, in the
baseline's favour.

This probe re-scores each committed baseline under the DRIVER's scheme by
reading the corpus expectation for every entry the baseline called
`no-answer` (an expectation beginning Unintegrable/CannotIntegrate is the
honest case; anything else is a `deferred` in driver terms) and prints the
recorded and corrected figures beside the package's.

It reads committed records only: no Maxima, no re-run.

SINCE THE FIX AND THE 2026-09-20 BASELINE RE-RUNS THIS IS A GUARD, not a
finding: all three sections now report 0 over-credited entries and the
recorded and corrected columns agree. A nonzero count means a baseline
record was produced by a probe without the `deferred` split — i.e. the
regression came back, or an old record was resurrected.

Run:  sh probes/corpus/13-baseline-noanswer-conflation.run
"""
import importlib.util
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
_argv = sys.argv[:]
sys.argv = [_argv[0]]                      # corpus_driver reads argv AT IMPORT
os.environ["MR_RULES_CORE"] = "0"
try:
    _spec = importlib.util.spec_from_file_location(
        "corpus_driver", os.path.join(ROOT, "test", "corpus_driver.py"))
    driver = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(driver)
finally:
    sys.argv = _argv

SUITE = os.path.join("reference", "maxima-syntax-test-suite")
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$")
PASS = {"expected", "verified", "no-answer"}

ROWS = [("2 Exponentials", "test/corpus_class2.baseline.out", "test/corpus_class2.out"),
        ("3 Logarithms", "test/corpus_class3.baseline.out", "test/corpus_class3.out"),
        ("6 Hyperbolic functions", "test/corpus_class6.baseline.out",
         "test/corpus_class6.out")]


def load(path):
    out = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = RESULT.match(line.rstrip("\n"))
            if m:
                out[(m.group(3), m.group(4))] = m.group(1)
    return out


def noun_expected(section):
    """(rel, entry) -> True when the corpus expectation is itself a noun."""
    out = {}
    for dirpath, _d, fns in os.walk(os.path.join(SUITE, section)):
        for fn in sorted(fns):
            if not fn.endswith(".mac"):
                continue
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, SUITE)
            entries, _ = driver.extract_entries(p)
            for i, text in enumerate(entries, 1):
                els = driver.split_elements(text[1:-1])
                if len(els) in (4, 5):
                    e = driver.normalize_heads(els[3]).lstrip()
                    out[(rel, str(i))] = e.startswith(
                        ("Unintegrable", "CannotIntegrate"))
    return out


print(f"probe: baseline-noanswer-conflation   "
      f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print(f"{'section':24s} {'N':>6s} {'base recorded':>16s} {'base corrected':>16s} "
      f"{'package':>15s}")
for section, bpath, ppath in ROWS:
    if not (os.path.exists(bpath) and os.path.exists(ppath)):
        print(f"{section:24s}  record missing — skipped")
        continue
    nm = noun_expected(section)
    base, pkg = load(bpath), load(ppath)
    n = len(base)
    over = sum(1 for k, v in base.items() if v == "no-answer" and not nm.get(k))
    braw = sum(1 for k in base if base[k] in PASS)
    praw = sum(1 for k in pkg if pkg[k] in PASS)
    print(f"{section:24s} {n:6d} {braw:7d} {braw/n:7.1%} {braw - over:7d} "
          f"{(braw - over)/n:7.1%} {praw:6d} {praw/n:7.1%}")
    print(f"{'':24s} {'':6s} over-credited `no-answer` entries: {over}")
