#!/usr/bin/env python3
"""11-deferred-close-class1-ticket-entries — the campaign plan's Task 5
Step 4 explicit check (spec §5.3): the ticket-02 7-entry matcher-state
families and the ticket-01 slow-form entries, each read from the class-1
A/B records of the class-3 deferred campaign close
(docs/corpus-class3-deferred-uplift.md §5.4).

Tickets: .scratch/class1-ab-remainders/issues/01-slow-zero-chain-forms.md
(9 entries), .scratch/class1-ab-remainders/issues/02-matcher-state-91-pattern-load.md
(7 entries); the entry lists below are transcribed from their tables.

Inputs (committed records only — no Maxima subprocess):
  test/corpus_class1.campaign-baseline.out   pre-campaign class-1 record
  test/corpus_class1.out                     campaign-close class-1 record

Output: probes/corpus/11-deferred-close-class1-ticket-entries.out
Re-run: deterministic (the run-date / HEAD line aside)."""

import hashlib
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLUG = "11-deferred-close-class1-ticket-entries"
OUT = os.path.join(ROOT, "probes", "corpus", SLUG + ".out")
PRE = os.path.join(ROOT, "test", "corpus_class1.campaign-baseline.out")
FIN = os.path.join(ROOT, "test", "corpus_class1.out")
PASS = {"verified", "expected", "no-answer"}   # test/corpus_driver.py PASS_CLASSES
REC = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s (.+) e(\d+) L\d+\s*$")

TICKETS = [
    ("01 slow zero-chain forms", [
        ("1.1.4.3", 228), ("1.2.1.3", 1979), ("1.2.1.4", 686), ("1.2.1.4", 687),
        ("1.2.1.5", 59), ("1.2.1.5", 66), ("1.2.1.5", 73), ("1.2.1.9", 308),
        ("1.2.2.3", 149)]),
    ("02 matcher-state 9.1 load", [
        ("1.2.2.4", 223), ("1.2.1.2", 2514), ("1.2.1.2", 2567), ("1.2.1.2", 2568),
        ("1.2.1.2", 2569), ("1.2.1.2", 2572), ("1.2.1.2", 2573)]),
]


def record(path):
    d = {}
    for ln in open(path, encoding="utf-8"):
        m = REC.match(ln.rstrip("\n"))
        if m:
            fam = m.group(3).split("/")[-1].split(" ", 1)[0]
            key = (fam, int(m.group(4)))
            assert key not in d, key
            d[key] = (m.group(1), float(m.group(2)))
    return d


def results(path):
    return next(ln.strip() for ln in open(path) if ln.startswith("Results:"))


def main():
    pre, fin = record(PRE), record(FIN)
    assert len(pre) == len(fin) == 25697 and set(pre) == set(fin)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    L = [f"=== class-1 ticket 01/02 entries across the campaign A/B ({SLUG}) ===",
         f"run date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
         f"  git HEAD: {head or 'n/a'}  (no Maxima subprocess)"]
    for label, path in (("pre  ", PRE), ("close", FIN)):
        md5 = hashlib.md5(open(path, "rb").read()).hexdigest()
        L.append(f"record {label} {os.path.relpath(path, ROOT)}  md5 {md5}  {results(path)}")
    L.append("")
    tot = Counter()
    for name, keys in TICKETS:
        L.append(f"--- ticket {name} ({len(keys)} entries) ---")
        for key in keys:
            (a, ta), (b, tb) = pre[key], fin[key]
            tr = ("PASS->PASS" if a in PASS and b in PASS else
                  "PASS->FAIL" if a in PASS else
                  "FAIL->PASS" if b in PASS else "FAIL->FAIL")
            tot[tr] += 1
            same = "unchanged" if a == b else "changed"
            L.append(f"{key[0]:8s} e{key[1]:<5d} {a}/{ta:.1f}s -> {b}/{tb:.1f}s  "
                     f"{tr}  class {same}")
        L.append("")
    L.append("totals over the 16: " + " ".join(f"{k}={tot[k]}" for k in
             ("PASS->PASS", "PASS->FAIL", "FAIL->PASS", "FAIL->FAIL")))
    txt = "\n".join(L) + "\n"
    open(OUT, "w", encoding="utf-8").write(txt)
    print(txt, end="")


if __name__ == "__main__":
    main()
