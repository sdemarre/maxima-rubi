#!/usr/bin/env python3
"""probes/class-ports/class1/make_entries.py -- the class-1 PASS->FAIL set of
the class-ports measurement (mr-ports test/ports_ab_class1.out, 534 keys), as
record-format entry files with the BASE record's line (class, t) and the new
class appended as a comment-free second file:
  class1/c1-pf-timeout.entries  new class timeout  (base line)
  class1/c1-pf-answer.entries   new class not timeout (base line)
Each line: `<base class> t=<base t>s <key> L<n>  -> <new class> t=<new t>s`."""
import os, re
H = os.path.dirname(os.path.abspath(__file__))
AB = "/home/serge/src/mr-ports/test/ports_ab_class1.out"
BASE = "/home/serge/src/maxima-rubi/test/corpus_class1.s9b.out"
NEW = "/home/serge/src/mr-ports/test/corpus_class1.ports.out"
R = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$")
keys, sec = set(), False
for l in open(AB):
    if l.startswith("=== PASS->FAIL"):
        sec = True; continue
    if sec and l.startswith("==="):
        break
    m = re.match(r"\s*(\S+)\s+->\s+(\S+)\s+t=\S+\s+->\s+t=\S+\s+(.*) e(\d+)\s*$", l)
    if sec and m:
        keys.add((m.group(3), int(m.group(4))))
assert len(keys) == 534, len(keys)
def rd(p):
    return {(m.group(3), int(m.group(4))): m for m in map(R.match, open(p)) if m}
b, n = rd(BASE), rd(NEW)
out = {"timeout": [], "answer": []}
for k in sorted(keys, key=lambda k: (k[0], k[1])):
    mb, mn = b[k], n[k]
    line = (f"{mb.group(1):14s} t={float(mb.group(2)):6.1f}s {k[0]} e{k[1]} L{mb.group(5)}"
            f"  -> {mn.group(1)} t={float(mn.group(2)):.1f}s\n")
    out["timeout" if mn.group(1) == "timeout" else "answer"].append(line)
for kk, v in out.items():
    open(os.path.join(H, f"c1-pf-{kk}.entries"), "w").writelines(v)
    print(kk, len(v))
