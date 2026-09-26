#!/usr/bin/env python3
"""probes/class-ports/make_entries.py -- the class-6 PASS->FAIL set of the
class-ports measurement, as subset-mode entry files for
test/run_corpus_queue.py (class field relabelled `pf`).

Reads the A/B (test/ports_ab_class6.out in mr-ports) for the 190 keys and the
new record for their result lines. Writes
  probes/class-ports/c6-pf-timeout.entries   (new class timeout, 97)
  probes/class-ports/c6-pf-answer.entries    (new class contains-noun/unverified, 93)
"""
import re, sys
AB = "/home/serge/src/mr-ports/test/ports_ab_class6.out"
NEW = "/home/serge/src/mr-ports/test/corpus_class6.ports.out"
keys = {}
sec = False
for l in open(AB):
    if l.startswith("=== PASS->FAIL"):
        sec = True; continue
    if sec and l.startswith("==="):
        break
    m = re.match(r"\s*(\S+)\s+->\s+(\S+)\s+t=\S+\s+->\s+t=\S+\s+(.*) e(\d+)\s*$", l)
    if sec and m:
        keys[(m.group(3), int(m.group(4)))] = (m.group(1), m.group(2))
assert len(keys) == 190, len(keys)
out = {"timeout": [], "answer": []}
for l in open(NEW):
    m = re.match(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$", l)
    if m and (m.group(3), int(m.group(4))) in keys:
        k = "timeout" if m.group(1) == "timeout" else "answer"
        out[k].append("pf" + l[2:] if len(m.group(1)) >= 2 else l)
for k, v in out.items():
    with open(f"probes/class-ports/c6-pf-{k}.entries", "w") as fh:
        for l in v:
            fh.write(re.sub(r"^\S+(\s+)", lambda m: "pf" + " " * (len(m.group(0)) - 2), l, count=1))
    print(k, len(v))
