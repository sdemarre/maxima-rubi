#!/usr/bin/env python3
"""probes/verify-stages/08-stage-order-entries.py -- the entry lists of the
stage-order A/B (.scratch/corpus-harness/issues/06 items 1 and 4).

Per class N, from master's latest records test/corpus_class<N>.geteqr.out
(the old checker), two record-format files the queue runner's subset mode
reads (--entries-from FILE --class C):
  08-stage-order/entries/class<N>.unverified.out -- every `unverified` line;
  08-stage-order/entries/class<N>.control.out    -- the control sample: 1,000
      `verified` entries over classes 1-8, proportional to each class's
      verified count with a floor of 25, drawn with random.Random(20260929).
Re-runnable; the output is deterministic.
"""
import os, random, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "08-stage-order", "entries")
TOTAL, FLOOR, SEED = 1000, 25, 20260929


def lines(n):
    path = os.path.join(ROOT, "test", f"corpus_class{n}.geteqr.out")
    head, body = [], []
    for l in open(path, encoding="utf-8"):
        if re.match(r"\S+\s+t=", l):
            body.append(l)
        elif not body:
            head.append(l)
    return head, body


os.makedirs(OUT, exist_ok=True)
recs = {n: lines(n) for n in range(1, 9)}
ver = {n: [l for l in b if l.startswith("verified ")] for n, (_h, b) in recs.items()}
nver = sum(len(v) for v in ver.values())
quota = {n: max(FLOOR, round(TOTAL * len(v) / nver)) for n, v in ver.items()}
# trim the largest quota so the sample is exactly TOTAL
quota[max(quota, key=quota.get)] -= sum(quota.values()) - TOTAL
rng = random.Random(SEED)
for n, (head, body) in recs.items():
    unv = [l for l in body if l.startswith("unverified ")]
    ctl = rng.sample(ver[n], quota[n])
    ctl.sort(key=body.index)
    for kind, rows in (("unverified", unv), ("control", ctl)):
        with open(os.path.join(OUT, f"class{n}.{kind}.out"), "w", encoding="utf-8") as fh:
            fh.writelines(head + rows)
    print(f"class {n}: unverified {len(unv):>4}  control {len(ctl):>4}")
