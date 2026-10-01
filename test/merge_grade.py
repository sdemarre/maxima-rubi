#!/usr/bin/env python3
"""Merge a run's per-shard .grade sidecars into one grade census (the grade of
the independent CAS integration tests, test/mr_grade.lisp; user request
2026-09-30; the definitions and how to read them: docs/grading-and-leaf-size.md).

The driver writes one line per entry (corpus_driver.grade_line)

    <grade> leaf=<result>/<optimal> type=<result>/<optimal> <relpath> e<entry> L<line>

<grade> is A, B, C, F, F(-1) (timeout), F(-2) (error) or `-` (an answer
whose optimal failed to evaluate); `-` also stands for an unknown leaf size
or type.

The census must be COMPLETE against the merged record: one line per entry,
no line for an entry the record lacks. It states, like the reference's
tables 1.3 and 1.5:
  - the grade distribution, over all entries;
  - for the solved entries (grade A, B or C): mean time (the record's t=),
    mean and median leaf size, and the normalized mean and median -- the
    result's leaf size over the optimal's, per entry, then averaged;
  - the grade distribution per corpus file;
then every entry's line in record order.

Usage:
  merge_grade.py RECORD OUT SHARD-GLOB
"""

import glob
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)$")
GRADE = re.compile(r"^(A|B|C|F|F\(-1\)|F\(-2\)|-) leaf=(\d+|-)/(\d+|-) type=(\d+|-)/(\d+|-) "
                   r"(.*) e(\d+) L(\d+)$")
GRADES = ("A", "B", "C", "F", "F(-1)", "F(-2)", "-")


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 64
    record, out, pattern = argv
    slug = os.path.basename(record).replace("corpus_", "").replace(".out", "")
    rec = {}
    order = []
    header = None
    for line in open(record, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("filter:"):
            header = line
        m = RESULT.match(line)
        if m:
            key = (m.group(3), int(m.group(4)))
            rec[key] = (m.group(1), float(m.group(2)))
            order.append(key)
    if not order:
        raise SystemExit(f"merge_grade: no result lines in {record}")
    inputs = sorted(glob.glob(os.path.join(ROOT, "test", pattern)))
    if not inputs:
        raise SystemExit(f"merge_grade: no sidecars match {pattern}")
    rows = {}
    problems = []
    for path in inputs:
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            m = GRADE.match(line)
            if not m:
                raise SystemExit(f"merge_grade: bad line in {os.path.basename(path)}: {line!r}")
            key = (m.group(6), int(m.group(7)))
            if key not in rec:
                problems.append(f"not in {os.path.basename(record)}: {line}")
            elif key in rows:
                problems.append(f"duplicate: {line}")
            else:
                rows[key] = (m.group(1), m.group(2), m.group(3), line)
    for key in order:
        if key not in rows:
            problems.append(f"missing: {rec[key][0]} {key[0]} e{key[1]}")
    if problems:
        print(f"INCOMPLETE: {len(problems)} problems", file=sys.stderr)
        for p in problems[:20]:
            print(f"  {p}", file=sys.stderr)
        return 1

    n = len(order)
    grades = Counter(rows[k][0] for k in order)
    solved = [k for k in order if rows[k][0] in ("A", "B", "C")]
    sizes = [int(rows[k][1]) for k in solved if rows[k][1] != "-"]
    ratios = [int(rows[k][1]) / int(rows[k][2]) for k in solved
              if rows[k][1] != "-" and rows[k][2] not in ("-", "0")]
    times = [rec[k][1] for k in solved]
    per_file = defaultdict(Counter)
    for k in order:
        per_file[k[0]][rows[k][0]] += 1

    def pct(c):
        return f"{c} ({100 * c / n:.2f}%)"

    lines = [
        f"=== maxima-rubi {slug} grade census ({len(inputs)} sidecars merged) ===",
        f"merge date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"record: {record}",
        header or "filter: ?",
        "",
        f"entries: {n}",
        "grades: " + "  ".join(f"{g} {pct(grades[g])}" for g in GRADES if grades[g]),
        f"solved (A/B/C): {pct(len(solved))}",
    ]
    if solved:
        lines += [
            f"mean time (s): {statistics.mean(times):.2f}",
            f"mean size: {statistics.mean(sizes):.2f}" if sizes else "mean size: -",
            f"normalized mean: {statistics.mean(ratios):.2f}" if ratios else "normalized mean: -",
            f"median size: {statistics.median(sizes):.2f}" if sizes else "median size: -",
            f"normalized median: {statistics.median(ratios):.2f}" if ratios else "normalized median: -",
        ]
    lines.append("")
    lines.append("per file: " + " ".join(GRADES))
    for rel in sorted(per_file):
        c = per_file[rel]
        lines.append(f"  {rel}: " + " ".join(str(c[g]) for g in GRADES))
    lines.append("")
    lines += [rows[k][3] for k in order]
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"OK: {n} entries ({len(inputs)} sidecars); "
          + " ".join(f"{g} {grades[g]}" for g in GRADES if grades[g]))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
