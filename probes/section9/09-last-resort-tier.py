#!/usr/bin/env python3
"""probes/section9/09-last-resort-tier.py -- ticket 14: what does the
last-resort tier (mr_last_resort_tier) recover, and what does it cost?

SETS.
  giveup  : every section-9 PASS->FAIL entry (reference record -> branch
            record, classes 1/2/3/6) that the give-up experiment put back in
            a PASS class (test/section9_giveup_arm_class<N>.out): 214. It
            contains ticket 14's 189-entry give-up bucket; the rest are
            entries test/section9_attribution.py files under an earlier
            bucket (inert-leak, cap, cost) that the arm ALSO restored.
  control : probe 06's seeded 2,000-entry sample of class-1 entries that PASS
            in the branch record (same seed, same record) -- what the
            give-up-last machinery was introduced to protect.

ARMS. The SAME core (this tree), run concurrently at the same worker count,
differing only in mr_last_resort_tier: `off` is the pre-ticket ordering (the
two passes of mr_giveup_last), `on` the four-tier walk.

  python3 probes/section9/09-last-resort-tier.py --write-subsets DIR
  python3 probes/section9/09-last-resort-tier.py --score DIR
  sh probes/section9/09-last-resort-tier.run      (the whole thing)
"""

import argparse
import collections
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "test"))
sys.path.insert(0, HERE)
import ab_records as ab  # noqa: E402

_argv, sys.argv = sys.argv, sys.argv[:1]
from corpus_driver import PASS_CLASSES  # noqa: E402
sys.argv = _argv

import importlib  # noqa: E402
p06 = importlib.import_module("06-giveup-switch-control")

CLASSES = {1: "1 Algebraic functions", 2: "2 Exponentials",
           3: "3 Logarithms", 6: "6 Hyperbolic functions"}
RX = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$")


def giveup_set():
    out = {}
    for n in CLASSES:
        base = ab.load_record(os.path.join(ROOT, f"test/corpus_class{n}.s9-ref.out"))
        new = ab.load_record(os.path.join(ROOT, f"test/corpus_class{n}.s9.out"))
        gl = ab.load_record(os.path.join(ROOT, f"test/section9_giveup_arm_class{n}.out"))
        for k in base:
            if (k in new and base[k][0] in PASS_CLASSES
                    and new[k][0] not in PASS_CLASSES
                    and k in gl and gl[k][0] in PASS_CLASSES):
                out[k] = (n, base[k][0], new[k][0])
    return out


def write_subsets(d):
    os.makedirs(d, exist_ok=True)
    g = giveup_set()
    _, control = p06.sample_keys()
    for n in CLASSES:
        keys = sorted(k for k, v in g.items() if v[0] == n)
        if n == 1:
            keys = sorted(set(keys) | set(control))
        with open(os.path.join(d, f"subset_class{n}.out"), "w", encoding="utf-8") as fh:
            for rel, e in keys:
                fh.write(f"timeout        t=   0.0s {rel} e{e} L0\n")
        print(f"class {n}: {len(keys)} entries")


def read_arm(d):
    out = {}
    for p in glob.glob(os.path.join(d, "*", "shard*.out")):
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                m = RX.match(line.rstrip("\n"))
                if m:
                    out[(m.group(3), int(m.group(4)))] = (m.group(1), float(m.group(2)))
    return out


def score(d):
    g = giveup_set()
    _, control = p06.sample_keys()
    off, on = read_arm(os.path.join(d, "off")), read_arm(os.path.join(d, "on"))
    P = PASS_CLASSES

    def table(name, keys, ref=None):
        keys = [k for k in keys if k in off and k in on]
        t = collections.Counter()
        tr = collections.Counter()
        for k in keys:
            a, b = off[k][0] in P, on[k][0] in P
            t[("P" if a else "F") + "->" + ("P" if b else "F")] += 1
            if off[k][0] != on[k][0]:
                tr[(off[k][0], on[k][0])] += 1
        print(f"{name}: {len(keys)} entries finished in both arms")
        print(f"  PASS off {sum(off[k][0] in P for k in keys)}  on {sum(on[k][0] in P for k in keys)}"
              f"   P->F {t['P->F']}  F->P {t['F->P']}")
        for (x, y), c in tr.most_common():
            print(f"    {c:4d}  {x} -> {y}")
        return keys

    print("== give-up bucket (reference PASS, branch FAIL, restored by mr_giveup_last=false)")
    keys = table("giveup", sorted(g))
    by = collections.Counter((g[k][0], on[k][0] in P) for k in keys)
    for n in CLASSES:
        tot = by[(n, True)] + by[(n, False)]
        if tot:
            print(f"  class {n}: {by[(n, True)]} of {tot} back in a PASS class with the tier")
    still = [k for k in keys if on[k][0] not in P]
    print(f"  NOT recovered by the tier: {len(still)}")
    for k in still:
        print(f"    {g[k][1]} -> {on[k][0]} (off: {off[k][0]})  {k[0]} e{k[1]}")
    print()
    print("== control: probe 06's class-1 PASS sample")
    ck = table("control", sorted(control))
    for k in ck:
        if off[k][0] in P and on[k][0] not in P:
            print(f"    LOST {off[k][0]} -> {on[k][0]}  {off[k][1]}s -> {on[k][1]}s  {k[0]} e{k[1]}")


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
        print(f"give-up set: {len(giveup_set())} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
