#!/usr/bin/env python3
"""Entry-level A/B of two grade censuses (test/merge_grade.py output,
test/corpus_classN.grade.out): the grade transition table and every entry
whose grade got WORSE (A -> B/C/F, B -> C/F, C -> F). Ungraded entries
(`-`, an optimal that failed to evaluate) are skipped on either side.

    python3 test/ab_grades.py OLD.grade.out NEW.grade.out

Ends `Results: <k> worse, <m> missing` (an entry graded in OLD and absent
from NEW is missing); exit 1 when either is nonzero. The record A/B of the
same two runs is test/ab_records.py.
"""

import re
import sys

RANK = {"A": 0, "B": 1, "C": 2, "F": 3, "F(-1)": 3, "F(-2)": 3}
LINE_RE = re.compile(r"^(A|B|C|F|F\(-1\)|F\(-2\)|-) leaf=\S+ type=\S+ (.+?)\s*$")


def read_grades(path):
    grades = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = LINE_RE.match(line)
            if m:
                grades[m.group(2)] = m.group(1)
    return grades


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    old, new = read_grades(argv[1]), read_grades(argv[2])
    trans, worse, missing = {}, [], 0
    for label, g0 in old.items():
        if g0 == "-":
            continue
        g1 = new.get(label)
        if g1 is None:
            missing += 1
            print(f"MISSING {g0} {label}")
            continue
        if g1 == "-":
            continue
        trans[(g0, g1)] = trans.get((g0, g1), 0) + 1
        if RANK[g1] > RANK[g0]:
            worse.append((g0, g1, label))
    print(f"# {argv[1]} -> {argv[2]}: {sum(trans.values())} entries graded in both")
    for (g0, g1), k in sorted(trans.items(), key=lambda kv: (RANK[kv[0][0]], kv[0][0], RANK[kv[0][1]], kv[0][1])):
        print(f"{g0} -> {g1}: {k}")
    for g0, g1, label in worse:
        print(f"WORSE {g0} -> {g1} {label}")
    print(f"Results: {len(worse)} worse, {missing} missing")
    return 1 if worse or missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
