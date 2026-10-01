#!/usr/bin/env python3
"""The grade report over classes: rubi against the native baseline, in the
shape of the reference's tables 1.3 and 1.5 (docs/grading-and-leaf-size.md).

For each class N it reads the two grade censuses test/merge_grade.py writes,
test/corpus_class<N>.grade.out (rubi) and test/corpus_class<N>.baseline.grade.out
(integrate+risch), with the records they belong to for the times (the
record's t= is the integrator's CPU seconds), and prints markdown:

  1. per arm, one row per class and a total: the grade distribution, the
     solved share (A/B/C), and over the solved entries the mean time, the
     mean and median leaf size and their normalized values (per entry,
     result's leaf size over the optimal's);
  2. rubi's grade against the baseline's, entry by entry: how many entries
     each arm grades better (A < B < C < F; the F kinds are one level), per
     class;
  3. the entries the baseline grades A and rubi does not, counted by rubi's
     grade and corpus file (the grade-level "integrate beats rubi" list).

    python3 test/grade_report.py [N ...] > <report>.md      (default: 0-8)

A class whose two censuses are not both there is listed as missing.
"""

import os
import re
import statistics
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)$")
GRADE = re.compile(r"^(A|B|C|F|F\(-1\)|F\(-2\)|-) leaf=(\d+|-)/(\d+|-) type=\S+ (.*) e(\d+) L\d+$")
GRADES = ("A", "B", "C", "F", "F(-1)", "F(-2)", "-")
RANK = {"A": 0, "B": 1, "C": 2, "F": 3, "F(-1)": 3, "F(-2)": 3, "-": 4}
ARMS = (("rubi", ""), ("integrate+risch", ".baseline"))


def load(n, suffix):
    """{key: (grade, leaf, optimal leaf, seconds)} or None if missing."""
    census = os.path.join(ROOT, "test", f"corpus_class{n}{suffix}.grade.out")
    record = os.path.join(ROOT, "test", f"corpus_class{n}{suffix}.out")
    if not (os.path.exists(census) and os.path.exists(record)):
        return None
    t = {}
    for line in open(record, encoding="utf-8"):
        m = RESULT.match(line.rstrip("\n"))
        if m:
            t[(m.group(3), int(m.group(4)))] = float(m.group(2))
    out = {}
    for line in open(census, encoding="utf-8"):
        m = GRADE.match(line.rstrip("\n"))
        if m:
            key = (m.group(4), int(m.group(5)))
            out[key] = (m.group(1), m.group(2), m.group(3), t.get(key))
    return out if out and set(out) == set(t) else None


def row(label, rows):
    n = len(rows)
    g = Counter(v[0] for v in rows)
    solved = [v for v in rows if v[0] in ("A", "B", "C")]
    sizes = [int(v[1]) for v in solved if v[1] != "-"]
    ratios = [int(v[1]) / int(v[2]) for v in solved if v[1] != "-" and v[2] not in ("-", "0")]
    times = [v[3] for v in solved if v[3] is not None]

    def f(xs, fn, d=2):
        return f"{fn(xs):.{d}f}" if xs else "-"
    cells = [label, str(n)] + [f"{g[x]} ({100 * g[x] / n:.1f}%)" if g[x] else "0"
                               for x in GRADES]
    cells += [f"{100 * len(solved) / n:.1f}%", f(times, statistics.mean),
              f(sizes, statistics.mean, 1), f(ratios, statistics.mean),
              f(sizes, statistics.median, 1), f(ratios, statistics.median)]
    return "| " + " | ".join(cells) + " |"


def main(argv):
    classes = argv or [str(n) for n in range(9)]
    data = {}
    missing = []
    for n in classes:
        arms = [load(n, s) for _name, s in ARMS]
        if any(a is None for a in arms):
            missing.append(n)
        else:
            data[n] = arms
    print("# Grades: maxima-rubi against Maxima integrate+risch\n")
    print("Grades as in docs/grading-and-leaf-size.md; times are the integrator's CPU "
          "seconds (the record's t=), over the solved (A/B/C) entries; sizes are "
          "Mathematica's LeafCount (test/mr_grade.lisp), normalized = the result's over "
          "the optimal's, per entry.\n")
    if missing:
        print(f"Missing (no grade census for both arms): class {', '.join(missing)}\n")
    head = ("| class | entries | " + " | ".join(GRADES)
            + " | solved | mean time (s) | mean size | normalized mean | median size | normalized median |")
    sep = "|" + "---|" * (2 + len(GRADES) + 6)
    for i, (name, _s) in enumerate(ARMS):
        print(f"## {name}\n")
        print(head)
        print(sep)
        allrows = []
        for n, arms in data.items():
            rows = list(arms[i].values())
            allrows += rows
            print(row(n, rows))
        if len(data) > 1:
            print(row("**all**", allrows))
        print()
    print("## rubi against integrate+risch, entry by entry\n")
    print("| class | same grade | rubi better | integrate+risch better | of which integrate+risch A, rubi F |")
    print("|---|---|---|---|---|")
    beats = defaultdict(Counter)
    tot = Counter()
    for n, (r, b) in data.items():
        c = Counter()
        for k, rv in r.items():
            bv = b[k]
            if RANK[rv[0]] == RANK[bv[0]]:
                c["same"] += 1
            elif RANK[rv[0]] < RANK[bv[0]]:
                c["rubi"] += 1
            else:
                c["base"] += 1
                if bv[0] == "A" and RANK[rv[0]] == 3:
                    c["af"] += 1
            if bv[0] == "A" and rv[0] != "A":
                beats[(n, k[0].split("/")[-1].removesuffix(".mac"))][rv[0]] += 1
        tot.update(c)
        print(f"| {n} | {c['same']} | {c['rubi']} | {c['base']} | {c['af']} |")
    if len(data) > 1:
        print(f"| **all** | {tot['same']} | {tot['rubi']} | {tot['base']} | {tot['af']} |")
    print("\n## integrate+risch A, rubi not A: by corpus file\n")
    print("| class | file | entries | rubi's grades |")
    print("|---|---|---|---|")
    for (n, f), c in sorted(beats.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"| {n} | {f} | {sum(c.values())} | "
              + ", ".join(f"{g} {v}" for g, v in c.most_common()) + " |")


if __name__ == "__main__":
    main(sys.argv[1:])
