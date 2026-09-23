#!/usr/bin/env python3
"""probes/section9/10-general-body.py -- ticket 14, second step: does moving
9.3's general BODY records behind the specific give-ups
(mr_general_after_giveups) recover the rest of the give-up bucket, and what
does it cost section 9's own gains?

SETS (the same core, both arms with mr_last_resort_tier on):
  giveup  : probe 09's give-up bucket (214)
  control : probe 06's seeded 2,000-entry class-1 PASS sample
  gains   : every section-9 FAIL->PASS entry (reference record -> branch
            record, classes 1/2/3/6: 1,132) -- what the switch could give back
ARMS: `tail` = mr_general_after_giveups=false, `body` = true.

  python3 probes/section9/10-general-body.py --write-subsets DIR
  python3 probes/section9/10-general-body.py --score DIR
  sh probes/section9/10-general-body.run
"""

import argparse
import collections
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
p09 = importlib.import_module("09-last-resort-tier")
p06 = p09.p06
ab, PASS_CLASSES, CLASSES = p09.ab, p09.PASS_CLASSES, p09.CLASSES


def gains_set():
    out = {}
    for n in CLASSES:
        base = ab.load_record(os.path.join(ROOT, f"test/corpus_class{n}.s9-ref.out"))
        new = ab.load_record(os.path.join(ROOT, f"test/corpus_class{n}.s9.out"))
        for k in base:
            if k in new and base[k][0] not in PASS_CLASSES and new[k][0] in PASS_CLASSES:
                out[k] = n
    return out


def sets():
    g = {k: v[0] for k, v in p09.giveup_set().items()}
    _, control = p06.sample_keys()
    return g, set(control), gains_set()


def write_subsets(d):
    os.makedirs(d, exist_ok=True)
    g, c, w = sets()
    for n in CLASSES:
        keys = {k for k, m in g.items() if m == n} | {k for k, m in w.items() if m == n}
        if n == 1:
            keys |= c
        with open(os.path.join(d, f"subset_class{n}.out"), "w", encoding="utf-8") as fh:
            for rel, e in sorted(keys):
                fh.write(f"timeout        t=   0.0s {rel} e{e} L0\n")
        print(f"class {n}: {len(keys)} entries")


def score(d):
    g, c, w = sets()
    A, B = p09.read_arm(os.path.join(d, "tail")), p09.read_arm(os.path.join(d, "body"))
    P = PASS_CLASSES
    for name, keys in (("giveup bucket", sorted(g)), ("control", sorted(c)),
                       ("section-9 gains", sorted(w))):
        keys = [k for k in keys if k in A and k in B]
        t = collections.Counter()
        tr = collections.Counter()
        lost = []
        for k in keys:
            a, b = A[k][0] in P, B[k][0] in P
            t[("P" if a else "F") + "->" + ("P" if b else "F")] += 1
            if A[k][0] != B[k][0]:
                tr[(A[k][0], B[k][0])] += 1
            if a and not b:
                lost.append(k)
        print(f"== {name}: {len(keys)} entries finished in both arms")
        print(f"  PASS tail {sum(A[k][0] in P for k in keys)}  body {sum(B[k][0] in P for k in keys)}"
              f"   P->F {t['P->F']}  F->P {t['F->P']}")
        for (x, y), n in tr.most_common():
            print(f"    {n:4d}  {x} -> {y}")
        for k in lost:
            print(f"    LOST {A[k][0]} -> {B[k][0]}  {A[k][1]}s -> {B[k][1]}s  {k[0]} e{k[1]}")
        print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-subsets")
    ap.add_argument("--score")
    a = ap.parse_args()
    if a.write_subsets:
        write_subsets(a.write_subsets)
    elif a.score:
        score(a.score)
    else:
        g, c, w = sets()
        print(f"giveup {len(g)}  control {len(c)}  gains {len(w)}  union {len(set(g) | c | set(w))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
