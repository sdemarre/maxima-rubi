#!/usr/bin/env python3
"""Class-2 corpus answer-head census: which Rubi-notation special-function
heads the 2 Exponentials section carries, with arity, so the driver's
answer normalization (test/corpus_driver.py HEAD_REWRITES) is built from
measured need. Commits the counts the rewrites are justified by."""
import glob
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECTION = sys.argv[1] if len(sys.argv) > 1 else "2 Exponentials"
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite", SECTION)

HEADS = ["GAMMA", "Ei", "E1", "E", "F0", "ProductLog", "FresnelC",
         "FresnelS", "Chi", "Shi", "Si", "Ci", "Li", "Erf", "Erfi", "Erfc"]

def call_arity(s, head):
    """Top-level argument counts of every head(… call in s."""
    out = []
    for m in re.finditer(re.escape(head) + r"\(", s):
        i, depth, args = m.end() - 1, 0, 0
        while i < len(s):
            c = s[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            elif c == "," and depth == 1:
                args += 1
            i += 1
        out.append(args + 1)
    return out

print(f"section: {SECTION!r}   date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
total_entries = 0
arity = {h: {} for h in HEADS}
for f in sorted(glob.glob(os.path.join(SUITE, "*.mac"))):
    s = open(f, encoding="utf-8").read()
    total_entries += sum(1 for ln in s.splitlines() if ln.lstrip().startswith("["))
    for h in HEADS:
        for n in call_arity(s, h):
            arity[h][n] = arity[h].get(n, 0) + 1
    for nat in ["gamma_incomplete(", "expintegral_ei(", "erf(", "erfi(",
                "lambert_w(", "exp(", "%e^"]:
        c = len(re.findall(re.escape(nat), s))
        if c:
            print(f"{nat:22s} {c}")
print(f"entries: {total_entries}")
for h in HEADS:
    if arity[h]:
        print(f"{h + '(':8s} {dict(sorted(arity[h].items()))}")
