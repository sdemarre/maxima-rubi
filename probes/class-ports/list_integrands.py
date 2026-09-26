#!/usr/bin/env python3
"""Print new-class, file tail, entry and integrand for each PASS->FAIL entry."""
import re, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
SUITE = "/home/serge/src/mr-attr/reference/maxima-syntax-test-suite"
def entries(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    return [l.strip().rstrip("$").rstrip(",") for l in lines if l.strip().startswith("[")]
def first_el(t):
    t = t[1:]; depth = 0
    for i, ch in enumerate(t):
        if ch in "[(": depth += 1
        elif ch in "])": depth -= 1
        elif ch == "," and depth == 0: return t[:i]
cache = {}
for fn in sys.argv[1:]:
    for l in open(fn):
        m = re.match(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)", l)
        rel, i = m.group(3), int(m.group(4))
        if rel not in cache: cache[rel] = entries(os.path.join(SUITE, rel))
        short = rel.split("/")[-1].split(" ")[0]
        print(f"{short:7s} e{i:<5d} {m.group(2):>5s} {first_el(cache[rel][i-1])}")
