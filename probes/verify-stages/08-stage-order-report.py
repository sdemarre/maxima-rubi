#!/usr/bin/env python3
"""probes/verify-stages/08-stage-order-report.py -- reads the shards of
08-stage-order.sh and writes the A/B report to stdout
(-> probes/verify-stages/08-stage-order.out).

Per entry set (unverified, control): the class counts per arm, every class
transition A -> B, the closing stage per arm, the stages abandoned per arm
(`timeout:` in the proof tag, `(heap)` included), the entries whose tag
changed, and for the control sample the verdicts against the old checker's
record (every control entry was `verified` there). Wall per arm from the
run log's timestamps.
"""
import collections, glob, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "08-stage-order")
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) (e\d+) L\d+$")


def load(arm, kind):
    cls, tag = {}, {}
    for n in range(1, 9):
        d = os.path.join(OUT, f"arm{arm}", kind, f"class{n}")
        for p in sorted(glob.glob(os.path.join(d, "shard*.out"))):
            for l in open(p, encoding="utf-8"):
                m = RESULT.match(l.rstrip("\n"))
                if m:
                    cls[(m.group(3), m.group(4))] = (m.group(1), float(m.group(2)))
        for p in sorted(glob.glob(os.path.join(d, "shard*.proof"))):
            for l in open(p, encoding="utf-8"):
                t, rest = l.rstrip("\n").split(" ", 1)
                m = re.match(r"(.*) (e\d+) L\d+$", rest)
                tag[(m.group(1), m.group(2))] = t
    return cls, tag


def expected_keys(kind):
    keys = set()
    for n in range(1, 9):
        for l in open(os.path.join(OUT, "entries", f"class{n}.{kind}.out"), encoding="utf-8"):
            m = RESULT.match(l.rstrip("\n"))
            if m:
                keys.add((m.group(3), m.group(4)))
    return keys


def closing(t):
    return t.split("/")[0]


def abandoned(t):
    m = re.search(r"timeout:([^/]+)", t)
    return m.group(1).replace("(heap)", "").split(",") if m else []


def counter_lines(c, indent="    "):
    return [f"{indent}{v:>5} {k}" for k, v in c.most_common()]


def arm_walls():
    walls, start = collections.defaultdict(float), {}
    log = os.path.join(HERE, "08-stage-order.log")
    stamps = []
    for l in open(log, encoding="utf-8"):
        m = re.match(r"== arm (\w) (\w+) class \d+ (\d+):(\d+):(\d+)", l)
        n = re.match(r"ALL DONE (\d+):(\d+):(\d+)", l)
        if m:
            stamps.append(((m.group(1), m.group(2)),
                           int(m.group(3)) * 3600 + int(m.group(4)) * 60 + int(m.group(5))))
        elif n:
            stamps.append((None, int(n.group(1)) * 3600 + int(n.group(2)) * 60 + int(n.group(3))))
    for (k, t0), (_k2, t1) in zip(stamps, stamps[1:]):
        walls[k] += (t1 - t0) % 86400
    return walls


def main():
    walls = arm_walls()
    for kind in ("unverified", "control"):
        want = expected_keys(kind)
        (ca, ta), (cb, tb) = load("A", kind), load("B", kind)
        print(f"==== {kind}: {len(want)} entries")
        for arm, c in (("A", ca), ("B", cb)):
            miss = want - set(c)
            print(f"  arm {arm}: {len(c)} results, {len(miss)} missing, "
                  f"wall {walls.get((arm, kind), 0) / 60:.1f} min")
            print("   " + "  ".join(f"{k} {v}" for k, v in
                                    sorted(collections.Counter(v[0] for v in c.values()).items())))
        both = sorted(set(ca) & set(cb))
        trans = collections.Counter((ca[k][0], cb[k][0]) for k in both if ca[k][0] != cb[k][0])
        print(f"  class transitions A -> B ({sum(trans.values())}):")
        for (a, b), v in trans.most_common():
            print(f"    {v:>5} {a} -> {b}")
        for k in both:
            if ca[k][0] != cb[k][0]:
                print(f"      {ca[k][0]:<12} -> {cb[k][0]:<12} {ta.get(k, '-')} -> {tb.get(k, '-')}  {k[0]} {k[1]}")
        for arm, t in (("A", ta), ("B", tb)):
            print(f"  arm {arm} closing stage (proof tag's first part):")
            print("\n".join(counter_lines(collections.Counter(closing(v) for v in t.values()), "    ")))
            ab = collections.Counter(s for v in t.values() for s in abandoned(v))
            heap = sum("(heap)" in v for v in t.values())
            print(f"  arm {arm} stages abandoned ({sum(ab.values())} stage timeouts, "
                  f"{heap} entries with (heap)):")
            print("\n".join(counter_lines(ab, "    ")))
        tagch = collections.Counter((closing(ta[k]), closing(tb[k]))
                                    for k in set(ta) & set(tb) if closing(ta[k]) != closing(tb[k]))
        print(f"  closing stage changed A -> B ({sum(tagch.values())}):")
        print("\n".join(f"    {v:>5} {a} -> {b}" for (a, b), v in tagch.most_common()))
        if kind == "control":
            for arm, c, t in (("A", ca, ta), ("B", cb, tb)):
                # `expected` is a PASS: the self-diff is not proved, the
                # expected-diff is (symbolic proof of either beats a numeric one)
                lost = collections.Counter(v[0] for v in c.values()
                                           if v[0] not in ("verified", "expected"))
                relab = sum(1 for v in c.values() if v[0] == "expected")
                num = sum(1 for k, v in c.items() if v[0] in ("verified", "expected")
                          and closing(t.get(k, "")) == "numeric")
                print(f"  arm {arm} vs the old checker (all were verified): "
                      f"{sum(lost.values())} no longer pass "
                      f"({', '.join(f'{k} {v}' for k, v in lost.most_common()) or 'none'}); "
                      f"{relab} now `expected` (a PASS); numeric-only passes {num}")
                for k, v in sorted(c.items()):
                    if v[0] not in ("verified", "expected"):
                        print(f"      {v[0]:<12} t={v[1]:.1f}s {t.get(k, '-')}  {k[0]} {k[1]}")
        print()


main()
