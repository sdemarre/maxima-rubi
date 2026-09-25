#!/usr/bin/env python3
"""probes/class-ports/class1/ratio.py -- per-entry t= ratio new/base over the
class-1 entries that PASS in both records, by base-time band (is the new
record's cpu uniformly inflated?)."""
import re, statistics
B = "/home/serge/src/maxima-rubi/test/corpus_class1.s9b.out"
N = "/home/serge/src/mr-ports/test/corpus_class1.ports.out"
R = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L\d+")
PASS = {"verified", "expected", "no-answer"}
def rd(p):
    o = {}
    for l in open(p):
        m = R.match(l)
        if m: o[(m.group(3), int(m.group(4)))] = (m.group(1), float(m.group(2)))
    return o
b, n = rd(B), rd(N)
bands = [(0.5, 1), (1, 3), (3, 10), (10, 20), (20, 31)]
for lo, hi in bands:
    rs = [n[k][1] / b[k][1] for k in b if b[k][0] in PASS and n[k][0] in PASS and lo <= b[k][1] < hi]
    if rs: print(f"base {lo:>4}-{hi:<3}s  n={len(rs):5d}  median new/base {statistics.median(rs):.2f}  q1 {statistics.quantiles(rs)[0]:.2f} q3 {statistics.quantiles(rs)[2]:.2f}")
for cls in ("verified",):
    tb = sum(b[k][1] for k in b if b[k][0] in PASS and n[k][0] in PASS)
    tn = sum(n[k][1] for k in b if b[k][0] in PASS and n[k][0] in PASS)
    print(f"total cpu over PASS->PASS: base {tb:.0f}s new {tn:.0f}s ratio {tn/tb:.2f}")
