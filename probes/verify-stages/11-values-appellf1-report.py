#!/usr/bin/env python3
"""probes/verify-stages/11-values-appellf1-report.py -- probe 11 (checker
024c263) against probe 08's arm B (the checker before it), entry by entry,
on both entry sets. Prints the class counts, every class transition with
both proof tags, the new proof tags, and whether the entry carries AppellF1
or a free m/n/q/F (from the corpus line, 09's static reading).
  python3 probes/verify-stages/11-values-appellf1-report.py > probes/verify-stages/11-values-appellf1.out
"""
import collections, glob, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) (e\d+) L(\d+)$")


def load(base):
    cls, tag = {}, {}
    for p in glob.glob(os.path.join(base, "class*", "shard*.out")):
        for l in open(p, encoding="utf-8"):
            m = RESULT.match(l.rstrip("\n"))
            if m:
                cls[(m.group(3), m.group(4))] = (m.group(1), int(m.group(5)))
    for p in glob.glob(os.path.join(base, "class*", "shard*.proof")):
        for l in open(p, encoding="utf-8"):
            t, rest = l.rstrip("\n").split(" ", 1)
            m = re.match(r"(.*) (e\d+) L\d+$", rest)
            tag[(m.group(1), m.group(2))] = t
    return cls, tag


lines = {}
def feature(rel, line):
    if rel not in lines:
        lines[rel] = open(os.path.join(SUITE, rel), encoding="utf-8").read().splitlines()
    t = lines[rel][line - 1]
    f1 = "AppellF1" in t
    free = bool(re.search(r"(?<![A-Za-z_%])[mnqF](?![A-Za-z_0-9(])", t))
    return ("F1" if f1 else "") + ("+" if f1 and free else "") + ("mnqF" if free else "") or "-"


def short(t):
    return re.sub(r"/timeout:.*", "/timeout", t or "-")


for kind in ("unverified", "control"):
    (ca, ta) = load(os.path.join(HERE, "08-stage-order", "armB", kind))
    (cb, tb) = load(os.path.join(HERE, "11-values-appellf1", kind))
    print(f"==== {kind}: base {len(ca)} entries, new {len(cb)}, missing {len(set(ca) - set(cb))}")
    for name, c in (("base (08 arm B)", ca), ("new (024c263)", cb)):
        print(f"  {name}: " + "  ".join(f"{k} {v}" for k, v in
                                          sorted(collections.Counter(v[0] for v in c.values()).items())))
    both = sorted(set(ca) & set(cb))
    tr = collections.Counter((ca[k][0], cb[k][0], feature(k[0], ca[k][1])) for k in both if ca[k][0] != cb[k][0])
    print(f"  transitions ({sum(tr.values())}), by what the corpus line carries:")
    for (a, b, f), v in tr.most_common():
        print(f"    {v:>5} {a:11s} -> {b:11s} {f}")
    newtags = collections.Counter(short(tb.get(k)) for k in both if ca[k][0] != cb[k][0])
    print("  new proof tags of the transitions:")
    for k, v in newtags.most_common():
        print(f"    {v:>5} {k}")
    left = collections.Counter((short(tb.get(k)), feature(k[0], cb[k][1])) for k in cb
                               if cb[k][0] not in ("verified", "expected"))
    print("  still failing, by proof tag and feature:")
    for (t, f), v in left.most_common(20):
        print(f"    {v:>5} {t:45s} {f}")
    print("  entries:")
    for k in both:
        if ca[k][0] != cb[k][0]:
            print(f"    {ca[k][0]:11s} -> {cb[k][0]:11s} {short(ta.get(k)):35s} -> {short(tb.get(k)):35s} {k[0]} {k[1]}")
    print()
