#!/usr/bin/env python3
"""probes/section9/06-giveup-switch-control.py -- spec A6.1 / ticket 14:
what does turning mr_giveup_last OFF cost on class 1?

WHY this probe exists. The switch's docstring (maxima_rubi_dispatch.lisp)
says reordering ALONE recovers nothing and that the 318-of-341 class-1
figure is the measurement of a PAIR -- the reordering together with the
seen-cut fall-through (%mr_top_body). So "the switch recovers 318" is not a
claim the docstring supports, and a recommendation against flipping it
cannot rest on it. This probe measures the flip itself.

METHOD. Take a seeded random sample of class-1 entries that PASS in the
branch record (test/corpus_class1.s9.out), re-run exactly those on the
BRANCH core with mr_giveup_last=false and nothing else changed, and count
what stops passing. Two arms are written, both at the SAME worker count, so
the only difference between them is the switch:

  control : mr_giveup_last=true  (the shipping default)
  flipped : mr_giveup_last=false

Comparing the two arms with each other -- not with the 24-worker record --
is what keeps the contention constant.

  python3 probes/section9/06-giveup-switch-control.py --plan      (list only)
  sh probes/section9/06-giveup-switch-control.run                 (run it)
"""

import argparse
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "test"))
import ab_records as ab  # noqa: E402

# corpus_driver parses sys.argv at IMPORT time (ten positionals, no options),
# so hide this probe's own options from it while it loads.
_argv, sys.argv = sys.argv, sys.argv[:1]
from corpus_driver import PASS_CLASSES  # noqa: E402
sys.argv = _argv

RECORD = os.path.join(ROOT, "test", "corpus_class1.s9.out")
SEED = 20260923
SAMPLE = 2000


def sample_keys():
    rec = ab.load_record(RECORD)
    passing = sorted(k for k, v in rec.items() if v[0] in PASS_CLASSES)
    rng = random.Random(SEED)
    return rec, rng.sample(passing, min(SAMPLE, len(passing)))


def write_subset(path):
    rec, keys = sample_keys()
    with open(path, "w", encoding="utf-8") as fh:
        for rel, e in keys:
            fh.write(f"timeout        t=   {rec[(rel, e)][1]:.1f}s {rel} e{e} L0\n")
    return len(keys)


def score(control_dir, flipped_dir):
    import glob
    import re
    rx = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$")

    def read(d):
        out = {}
        for p in sorted(glob.glob(os.path.join(d, "shard*.out"))):
            with open(p, encoding="utf-8") as fh:
                for line in fh:
                    m = rx.match(line.rstrip("\n"))
                    if m:
                        out[(m.group(3), int(m.group(4)))] = (m.group(1),
                                                              float(m.group(2)))
        return out

    control, flipped = read(control_dir), read(flipped_dir)
    shared = sorted(set(control) & set(flipped))
    lost, lost_timeout, gained = [], [], []
    for k in shared:
        c, f = control[k][0], flipped[k][0]
        if c in PASS_CLASSES and f not in PASS_CLASSES:
            (lost_timeout if f == "timeout" else lost).append((k, c, f))
        elif c not in PASS_CLASSES and f in PASS_CLASSES:
            gained.append((k, c, f))
    print(f"sample: {len(shared)} class-1 entries that PASS in the branch record")
    print(f"        (seeded random, seed {SEED}, of {RECORD})")
    print(f"control arm mr_giveup_last=true  PASS: "
          f"{sum(1 for k in shared if control[k][0] in PASS_CLASSES)}")
    print(f"flipped arm mr_giveup_last=false PASS: "
          f"{sum(1 for k in shared if flipped[k][0] in PASS_CLASSES)}")
    print(f"LOST to the flip, verdict-class change: {len(lost)}")
    for k, c, f in lost:
        print(f"    {c} -> {f}  {k[0]} e{k[1]}")
    print(f"LOST to the flip, but the new verdict is `timeout` "
          f"(a cost change, not a routing change): {len(lost_timeout)}")
    for k, c, f in lost_timeout:
        print(f"    {c} -> {f}  {control[k][1]}s -> {flipped[k][1]}s  {k[0]} e{k[1]}")
    print(f"GAINED by the flip: {len(gained)}")
    for k, c, f in gained:
        print(f"    {c} -> {f}  {k[0]} e{k[1]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--write-subset")
    ap.add_argument("--score", nargs=2, metavar=("CONTROL_DIR", "FLIPPED_DIR"))
    a = ap.parse_args()
    if a.write_subset:
        print(f"wrote {write_subset(a.write_subset)} entries to {a.write_subset}")
    elif a.score:
        score(*a.score)
    else:
        _, keys = sample_keys()
        print(f"plan: {len(keys)} class-1 PASS entries, seed {SEED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
