#!/usr/bin/env python3
"""Merge the parallel-shard .out files of the class-1 corpus baseline into
one canonical probe-integrate-sample.out and verify completeness.

The baseline was run in waves (serial phase 1 capped at a wall, a serial
phase-2 resume, then N parallel shards, each a disjoint slice of the
sorted file list - possibly splitting one file across two shards via the
per-file cap and skip-first-entries). Every shard appends self-contained
result lines:

    <class>  t=<s>s <relpath> e<entry> L<line>

to its own .out. Merging therefore parses every result line across all
.out files, asserts the (file, entry) key set is exactly the full corpus
(25,697 entries at 2026-08-18), re-sorts into canonical (file, entry)
order, and writes one header + all lines + one combined summary.

Usage: merge-shards.py [extra .out file ...]
(mandatory inputs: probe-integrate-sample.out and the existing
probe-integrate-sample.shard*.out in this directory; extras appended)
"""

import glob
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = "/home/serge/src/maxima-rubi"
SUITE_REL = "reference/maxima-syntax-test-suite"
SECTION = "1 Algebraic functions"
HERE = os.path.dirname(os.path.abspath(__file__))
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)$")
KNOWN_CLASSES = {"expected", "verified", "unverified",
                 "no-answer", "unexpected", "error", "timeout"}


def file_list():
    files = []
    for dirpath, _dn, fnames in os.walk(SUITE_REL):
        for fn in fnames:
            if fn.endswith(".mac"):
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, SUITE_REL)
                if SECTION + "/" in rel:
                    files.append(rel)
    files.sort()
    return files


def n_entries(rel):
    return sum(1 for l in open(os.path.join(SUITE_REL, rel),
                               encoding="utf-8")
               if l.strip().startswith("["))


def main():
    os.chdir(ROOT)
    inputs = [os.path.join(HERE, "probe-integrate-sample.out")]
    inputs += sorted(glob.glob(os.path.join(HERE,
                                            "probe-integrate-sample.shard*.out")))
    inputs += sys.argv[1:]
    seen = []
    keys = {}
    dupes = 0
    bad = 0
    for path in inputs:
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            m = RESULT.match(line)
            if not m:
                if (line.strip()
                        and not re.match(r"^\S+\s+\d+$", line)  # summary count
                        and not line.startswith(("=", "date:", "merge date:",
                                                 "filter:", "maxima:", "total",
                                                 "wall", "integrate", "SKIP"))):
                    bad += 1
                continue
            cls, _t, rel, e, _l = m.groups()
            k = (rel, int(e))
            if k in keys:
                dupes += 1
            seen.append((k, cls, line))
            keys[k] = True
    files = file_list()
    counts = {r: n_entries(r) for r in files}
    expected = {(r, i) for r in files for i in range(1, counts[r] + 1)}
    missing = expected - set(keys)
    extra = set(keys) - expected
    if bad or dupes or missing or extra:
        print(f"INCOMPLETE: unparsed={bad} dupes={dupes} "
              f"missing={len(missing)} extra={len(extra)}")
        for k in sorted(missing)[:10]:
            print("  missing", k)
        for k in sorted(extra)[:10]:
            print("  extra  ", k)
        sys.exit(1)
    by_key, cls_of = {}, {}
    for k, cls, line in seen:
        by_key[k] = line
        cls_of[k] = cls
    out_lines = [
        "=== maxima-rubi integrate baseline, corpus section 1 (full) ===",
        f"merge date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    r = subprocess.run(
        ["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
        capture_output=True, text=True, timeout=120,
    )
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.startswith(("Maxima", "Lisp ", "Host ")):
            out_lines.append(f"maxima: {line}")
    out_lines.append("filter: '1 Algebraic functions/'  full run  "
                     "timeout: 30s  (serial phases + parallel shards, "
                     "merged here)")
    out_lines.append("")
    for r in files:
        for i in range(1, counts[r] + 1):
            out_lines.append(by_key[(r, i)])
    cls_counts = Counter(cls_of.values())
    out_lines.append("")
    out_lines.append("=== summary ===")
    for k in sorted(cls_counts):
        assert k in KNOWN_CLASSES, k
        v = cls_counts[k]
        out_lines.append(f"{k:14s} {v:6d}  {100 * v / sum(cls_counts.values()):5.1f}%")
    out_lines.append(f"{'total':14s} {sum(cls_counts.values()):6d}")
    open(os.path.join(HERE, "probe-integrate-sample.out"), "w",
         encoding="utf-8").write("\n".join(out_lines) + "\n")
    print(f"OK: {len(by_key)}/{sum(counts.values())} entries, "
          f"{len(files)} files, no dupes/missing/extra")
    for k in sorted(cls_counts):
        print(f"  {k:14s} {cls_counts[k]}")
    print("shard .out files consumed:", ", ".join(os.path.basename(p) for p in inputs))


if __name__ == "__main__":
    main()
