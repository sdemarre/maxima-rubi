#!/usr/bin/env python3
"""Checks for test/ab_grades.py, the entry-level A/B of two grade sidecar
censuses (test/corpus_classN.grade.out). No Maxima; synthetic files.

Re-runnable:  python3 test/test_ab_grades.py
"""

import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test"))
import ab_grades  # noqa: E402

passed = failed = 0


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name} {detail}")


HEAD = ("=== maxima-rubi class6 grade census (24 sidecars merged) ===\n"
        "record: test/corpus_class6.out\n\n")
OLD = HEAD + ("C leaf=52/28 type=3/3 6 H/6.1.1 f.mac e1 L12\n"
              "A leaf=10/10 type=3/3 6 H/6.1.1 f.mac e2 L13\n"
              "B leaf=30/10 type=3/3 6 H/6.1.1 f.mac e3 L14\n"
              "- leaf=-/- type=-/- 6 H/6.1.1 f.mac e4 L15\n"
              "F(-1) leaf=-/17 type=-/1 6 H/6.1.1 f.mac e5 L16\n"
              "     A  4,055  79.8 %\n")
NEW = HEAD + ("A leaf=28/28 type=3/3 6 H/6.1.1 f.mac e1 L12\n"
              "B leaf=30/10 type=3/3 6 H/6.1.1 f.mac e2 L13\n"
              "B leaf=30/10 type=3/3 6 H/6.1.1 f.mac e3 L14\n"
              "A leaf=9/9 type=3/3 6 H/6.1.1 f.mac e4 L15\n"
              "F(-1) leaf=-/17 type=-/1 6 H/6.1.1 f.mac e5 L16\n")


def main():
    with tempfile.TemporaryDirectory() as d:
        o, n = os.path.join(d, "old.grade.out"), os.path.join(d, "new.grade.out")
        open(o, "w").write(OLD)
        open(n, "w").write(NEW)
        g = ab_grades.read_grades(o)
        check("entry lines parse, census and header lines skipped",
              g == {"6 H/6.1.1 f.mac e1 L12": "C", "6 H/6.1.1 f.mac e2 L13": "A",
                    "6 H/6.1.1 f.mac e3 L14": "B", "6 H/6.1.1 f.mac e4 L15": "-",
                    "6 H/6.1.1 f.mac e5 L16": "F(-1)"}, str(g))
        check("rank: A < B < C < F family",
              [ab_grades.RANK[x] for x in ("A", "B", "C", "F", "F(-1)", "F(-2)")]
              == [0, 1, 2, 3, 3, 3])
        p = subprocess.run([sys.executable, os.path.join(ROOT, "test", "ab_grades.py"), o, n],
                           capture_output=True, text=True)
        out = p.stdout
        check("the worse entry is listed", "WORSE A -> B 6 H/6.1.1 f.mac e2 L13" in out, out)
        check("a better entry is not listed as worse", "e1 L12" not in
              "".join(l for l in out.splitlines(True) if l.startswith("WORSE")), out)
        check("an ungraded side is skipped, not worse", "e4 L15" not in
              "".join(l for l in out.splitlines(True) if l.startswith("WORSE")), out)
        check("the transition table counts C->A", "C -> A: 1" in out, out)
        check("Results line and exit code", "Results: 1 worse, 0 missing" in out
              and p.returncode == 1, f"{out} rc={p.returncode}")
        open(n, "w").write(NEW.replace("A leaf=28/28 type=3/3 6 H/6.1.1 f.mac e1 L12\n", ""))
        p = subprocess.run([sys.executable, os.path.join(ROOT, "test", "ab_grades.py"), o, n],
                           capture_output=True, text=True)
        check("an entry missing from NEW is counted", "Results: 1 worse, 1 missing" in p.stdout,
              p.stdout)
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
