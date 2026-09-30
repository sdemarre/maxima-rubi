#!/usr/bin/env python3
"""Our grades on the independent test suites against the reference report's
(12000.org, summer 2022 edition; probes/leaf-size/01-scrape-reference.tsv):

  Rubi 4.16.1 in Mathematica (reference)   vs  maxima-rubi (test/corpus_class0.grade.out)
  Maxima 5.45 via SageMath (reference)     vs  Maxima integrate+risch
                                               (test/corpus_class0.baseline.grade.out)

Problem N of a report is entry eN of the corpus file. Differences in the
setup: the reference caps each integral at 3 minutes (we: 30 s CPU plus 30 s
of verification), did not verify Maxima's answers (we verify both), and sizes
Maxima's answers with SageMath's tree_size (we: Mathematica's LeafCount for
every system, test/mr_grade.lisp).

    python3 probes/leaf-size/03-compare-with-reference.py > probes/leaf-size/03-compare-with-reference.out

The story these measurements belong to: docs/grading-and-leaf-size.md.
"""

import os
import re
import statistics
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Problem N of a report is entry eN of the corpus file -- except in Welz: its
# report has 116 problems and the corpus file 93, and the two part ways after
# problem 57 (measured 2026-09-30: e1-e57 agree on the optimal text and, 5
# entries aside, on the leaf size; from e58 on the leaf sizes are a shifted
# sequence). Welz rows past 57 are left out.
ALIGNED_UPTO = {"11_Welz_Problems": 57}
TSV = os.path.join(ROOT, "probes", "leaf-size", "01-scrape-reference.tsv")
GRADE = re.compile(r"^(A|B|C|F|F\(-1\)|F\(-2\)|-) leaf=(\d+|-)/(\d+|-) type=\S+ (.*) e(\d+) L\d+$")
ORDER = ("A", "B", "C", "F", "F(-1)", "F(-2)", "-")


def ours(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        m = GRADE.match(line.rstrip("\n"))
        if m:
            out[(m.group(4), int(m.group(5)))] = (m.group(1), m.group(2), m.group(3))
    return out


def dist(c, n):
    return "  ".join(f"{g} {c[g]} ({100 * c[g] / n:.1f}%)" for g in ORDER if c[g])


def main():
    rows = [l.rstrip("\n").split("\t") for l in open(TSV, encoding="utf-8")][1:]
    arms = [("Rubi", 3, 4, "maxima-rubi", ours(os.path.join(ROOT, "test", "corpus_class0.grade.out"))),
            ("Maxima 5.45 (SageMath)", 5, 6, "Maxima 5.50 integrate+risch",
             ours(os.path.join(ROOT, "test", "corpus_class0.baseline.grade.out")))]
    print("=== grades on the independent test suites: the reference report against ours ===")
    print(f"reference rows: {len(rows)} ({TSV})")
    for ref_name, gi, si, our_name, our in arms:
        keyed = []
        for r in rows:
            name = "0 Independent test suites/" + r[0].split("_", 1)[1].replace("_", " ") + ".mac"
            key = (name, int(r[1]))
            if key in our and int(r[1]) <= ALIGNED_UPTO.get(r[0], int(r[1])):
                keyed.append((r, key))
        n = len(keyed)
        ref_c = Counter(r[gi] if r[gi] in ORDER else "-" for r, _ in keyed)
        our_c = Counter(our[k][0] for _, k in keyed)
        print(f"\n--- {ref_name} (reference) vs {our_name} (ours), {n} integrals ---")
        print(f"reference: {dist(ref_c, n)}")
        print(f"ours:      {dist(our_c, n)}")
        solved_ref = sum(ref_c[g] for g in "ABC")
        solved_our = sum(our_c[g] for g in "ABC")
        print(f"solved (A/B/C): reference {solved_ref} ({100 * solved_ref / n:.1f}%), "
              f"ours {solved_our} ({100 * solved_our / n:.1f}%)")
        x = Counter((r[gi] if r[gi] in ORDER else "-", our[k][0]) for r, k in keyed)
        print("transitions reference -> ours (changed only):")
        for (a, b), v in sorted(x.items(), key=lambda kv: -kv[1]):
            if a != b:
                print(f"  {a:6s} -> {b:6s} {v}")
        both = [(r, k) for r, k in keyed if r[gi] in ("A", "B", "C") and our[k][0] in ("A", "B", "C")
                and r[si].isdigit() and our[k][1] != "-" and our[k][2] not in ("-", "0")]
        if both:
            rn = [int(r[si]) / int(r[2]) for r, _ in both]
            on = [int(our[k][1]) / int(our[k][2]) for _, k in both]
            print(f"normalized size where both solved ({len(both)}): reference mean {statistics.mean(rn):.2f} "
                  f"median {statistics.median(rn):.2f}; ours mean {statistics.mean(on):.2f} "
                  f"median {statistics.median(on):.2f}")
        per = {}
        for r, k in keyed:
            per.setdefault(r[0], [Counter(), Counter()])
            per[r[0]][0][r[gi]] += 1
            per[r[0]][1][our[k][0]] += 1
        print("per suite, A / solved: reference | ours")
        for s, (a, b) in per.items():
            m = sum(a.values())
            print(f"  {s:22s} {m:4d}   {a['A']:4d} / {a['A'] + a['B'] + a['C']:4d}   |   "
                  f"{b['A']:4d} / {b['A'] + b['B'] + b['C']:4d}")


if __name__ == "__main__":
    main()
