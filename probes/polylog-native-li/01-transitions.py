#!/usr/bin/env python3
"""probes/polylog-native-li/01-transitions.py -- the verdict transitions of
the native-li measure (.scratch/polylog-native-li/issues/01), split by
whether the corpus entry carries polylog( (integrand or expected answer).

For each class N in 2..8 it reads the promoted record test/corpus_classN.out
(old: polylog emitted and read as written) and test/corpus_classN.li.out
(new: li[s](z) emitted, corpus rewritten polylog(A, B) -> li[A](B)), and
prints, for the polylog entries and for the rest: the PASS/FAIL 2x2 and every
class transition with its count.

    python3 probes/polylog-native-li/01-transitions.py > probes/polylog-native-li/01-transitions.out
"""
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
R = re.compile(r"^(\S+)\s+t=\s*[\d.]+s\s+(.*\.mac) e(\d+) L(\d+)\s*$")
PASS = {"verified", "expected"}


def record(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        m = R.match(line.rstrip("\n"))
        if m:
            out[(m.group(2), int(m.group(3)))] = (m.group(1), int(m.group(4)))
    return out


def main():
    lines_cache = {}
    tot = collections.Counter()
    for n in range(2, 9):
        old_p = os.path.join(ROOT, "test", "corpus_class%d.out" % n)
        new_p = os.path.join(ROOT, "test", "corpus_class%d.li.out" % n)
        if not os.path.exists(new_p):
            print("class %d: no %s" % (n, os.path.relpath(new_p, ROOT)))
            continue
        old, new = record(old_p), record(new_p)
        if set(old) != set(new):
            print("class %d: KEY SETS DIFFER (%d vs %d)" % (n, len(old), len(new)))
            continue
        groups = {"polylog": collections.Counter(), "other": collections.Counter()}
        trans = {"polylog": collections.Counter(), "other": collections.Counter()}
        for key, (vo, ln) in old.items():
            rel = key[0]
            if rel not in lines_cache:
                lines_cache[rel] = open(os.path.join(SUITE, rel), encoding="utf-8").read().split("\n")
            g = "polylog" if "polylog(" in lines_cache[rel][ln - 1] else "other"
            vn = new[key][0]
            cell = "%s->%s" % ("PASS" if vo in PASS else "FAIL", "PASS" if vn in PASS else "FAIL")
            groups[g][cell] += 1
            tot[(g, cell)] += 1
            if vo != vn:
                trans[g]["%s -> %s" % (vo, vn)] += 1
        print("=== class %d ===" % n)
        for g in ("polylog", "other"):
            c = groups[g]
            print("  %-8s entries %5d  PASS %5d -> %5d  | PASS->FAIL %d  FAIL->PASS %d" % (
                g, sum(c.values()), c["PASS->PASS"] + c["PASS->FAIL"],
                c["PASS->PASS"] + c["FAIL->PASS"], c["PASS->FAIL"], c["FAIL->PASS"]))
            for t, k in trans[g].most_common():
                print("      %5d  %s" % (k, t))
    print("=== total (classes with a .li record) ===")
    for g in ("polylog", "other"):
        pp, pf, fp = tot[(g, "PASS->PASS")], tot[(g, "PASS->FAIL")], tot[(g, "FAIL->PASS")]
        ff = tot[(g, "FAIL->FAIL")]
        print("  %-8s entries %5d  PASS %5d -> %5d  | PASS->FAIL %d  FAIL->PASS %d" % (
            g, pp + pf + fp + ff, pp + pf, pp + fp, pf, fp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
