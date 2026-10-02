#!/usr/bin/env python3
"""How many rubi FAILs does radexpand's sqrt(x^2) -> abs(x) cause, in the
current records?

04-radexpand-parse-set.tsv (2026-09-28) lists the 1,390 integrands that Maxima's
default radexpand:true rewrites (column 3: 1 when only the default result carries
`abs`). This probe reads them against the current rubi records
(test/corpus_class<N>.out) and against the 04 A/B's `whole` arm
(radexpand:false for the whole entry; rule set of master a7ee2a3), which says
whether the entry passes once the rewrite is gone.

    python3 probes/integrate-beats-rubi/05-abs-fails-current-records.py \\
        > probes/integrate-beats-rubi/05-abs-fails-current-records.out

Ticket: .scratch/integrate-beats-rubi/issues/02-sqrt-c-x2-abs.md.
"""

import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.join(ROOT, "probes", "integrate-beats-rubi")
PAT = re.compile(r"^(?:PASS: |FAIL: )?(\S+)\s+t=\s*\S+\s+(.*\.mac) (e\d+) L\d+$")
sys.argv = sys.argv[:1]
sys.path.insert(0, os.path.join(ROOT, "test"))
from corpus_driver import PASS_CLASSES as PASS  # noqa: E402 -- the driver's own PASS set


def record(path):
    out = {}
    for line in open(path):
        m = PAT.match(line.strip())
        if m:
            out[(m.group(2), m.group(3))] = m.group(1)
    return out


def main():
    cur = {}
    for n in range(1, 9):
        cur.update(record(os.path.join(ROOT, "test", f"corpus_class{n}.out")))
    whole = record(os.path.join(HERE, "04-radexpand-ab.whole.out"))
    fails = sum(1 for v in cur.values() if v not in PASS)
    t = collections.Counter()
    per_class = collections.Counter()
    verdicts = collections.Counter()
    for line in open(os.path.join(HERE, "04-radexpand-parse-set.tsv")):
        cls, _old, has_abs, rel, e, _f = line.rstrip("\n").split("\t")
        now = cur[(rel, e)]
        kind = "abs" if has_abs == "1" else "other rewrite"
        if now in PASS:
            t[(kind, "PASS")] += 1
            continue
        w = whole.get((rel, e))
        t[(kind, "FAIL")] += 1
        t[(kind, "FAIL, whole arm " + ("PASS" if w in PASS else "FAIL"))] += 1
        if kind == "abs":
            per_class[cls] += 1
            verdicts[now] += 1
    print(f"# rubi records test/corpus_class1..8.out: {len(cur)} entries, {fails} FAIL")
    for k in sorted(t):
        print(f"{' / '.join(k):40s} {t[k]:5d}")
    print("abs FAIL by class:   " + ", ".join(f"{c}: {per_class[c]}" for c in sorted(per_class)))
    print("abs FAIL by verdict: " + ", ".join(f"{v}: {k}" for v, k in verdicts.most_common()))
    c1 = sum(1 for (rel, _e), v in cur.items() if rel.startswith("1 ") and v not in PASS)
    print(f"class 1: {per_class['1']} of its {c1} FAILs carry the abs rewrite")


if __name__ == "__main__":
    main()
