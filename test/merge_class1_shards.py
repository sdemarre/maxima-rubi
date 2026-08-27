#!/usr/bin/env python3
"""Merge the class-1 shard .out files into one canonical
test/corpus_class1.out and verify completeness against the corpus.

The shard result lines are in the T3 format
    <class>  t=<s>s <relpath> e<entry> L<line>
so the merge parses every result line, asserts the (file, entry) key
set is exactly the full class-1 corpus, re-sorts into canonical
(file, entry) order, and writes one header + all lines + one summary.
"""

import glob
import importlib.util
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVER = os.path.join("test", "corpus_class1_driver.py")
SECTION = "1 Algebraic functions"
OUT = os.path.join("test", "corpus_class1.out")
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)$")
# Keep in sync with corpus_class1_driver.py (guarded by
# test/test_merge_classes.py): the driver gained `deferred` (ddc88ef) and
# `contains-noun` (2a0ff92) after this merge was written; both are FAIL
# classes, as there.
KNOWN_CLASSES = {"expected", "verified", "unverified",
                 "no-answer", "unexpected", "error", "timeout",
                 "deferred", "contains-noun"}
PASS_CLASSES = {"expected", "verified", "no-answer"}

sys.argv = ["corpus_class1_driver.py", SECTION + "/", "999999", "30"]
_spec = importlib.util.spec_from_file_location("driver",
                                               os.path.join(ROOT, DRIVER))
assert _spec is not None and _spec.loader is not None
driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(driver)

files = driver.file_list()
counts = {}
for path, rel in files:
    entries, _ = driver.extract_entries(path)
    counts[rel] = len(entries)
expected = {(rel, i) for rel, n in counts.items() for i in range(1, n + 1)}

seen = []
keys = {}
dupes = 0
bad = 0
inputs = sorted(glob.glob(os.path.join(ROOT, "test",
                                       "corpus_class1.shard*.out")))
assert inputs, "no shard .out files found"
for path in inputs:
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = RESULT.match(line)
        if not m:
            if (line.strip()
                    and not re.match(r"^\S+\s+\d+$", line)
                    and not line.startswith(("=", "date:", "merge date:",
                                             "filter:", "maxima:", "total",
                                             "wall", "Results:", "SKIP"))):
                bad += 1
            continue
        cls, _t, rel, e, _l = m.groups()
        k = (rel, int(e))
        if k in keys:
            dupes += 1
        seen.append((k, cls, line))
        keys[k] = True

missing = expected - set(keys)
extra = set(keys) - expected
if bad or dupes or missing or extra:
    print(f"INCOMPLETE: unparsed={bad} dupes={dupes} "
          f"missing={len(missing)} extra={len(extra)}", file=sys.stderr)
    for k in sorted(missing)[:10]:
        print("  missing", k, file=sys.stderr)
    for k in sorted(extra)[:10]:
        print("  extra  ", k, file=sys.stderr)
    sys.exit(1)

by_key = {}
cls_of = {}
for k, cls, line in seen:
    by_key[k] = line
    cls_of[k] = cls

out_lines = [
    f"=== maxima-rubi class-1 corpus run (full, {len(inputs)} shards merged) ===",
    f"merge date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
]
r = subprocess.run(
    ["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
    capture_output=True, text=True, timeout=120, cwd=ROOT,
)
for line in r.stdout.splitlines():
    line = line.strip()
    if line.startswith(("Maxima", "Lisp ", "Host ")):
        out_lines.append(f"maxima: {line}")
out_lines.append(f"filter: {SECTION + '/'!r}  full run  timeout: 30s  "
                 f"({len(inputs)} shards, merged here)")
out_lines.append("")

for rel in sorted(counts):
    for i in range(1, counts[rel] + 1):
        out_lines.append(by_key[(rel, i)])

cls_counts = Counter(cls_of.values())
out_lines.append("")
out_lines.append("=== summary ===")
for k in sorted(cls_counts):
    assert k in KNOWN_CLASSES, k
    v = cls_counts[k]
    out_lines.append(f"{k:14s} {v:6d}  "
                     f"{100 * v / sum(cls_counts.values()):5.1f}%")
total = sum(cls_counts.values())
passed = sum(v for k, v in cls_counts.items() if k in PASS_CLASSES)
failed = total - passed
out_lines.append(f"{'total':14s} {total:6d}")
out_lines.append(f"Results: {passed} passed, {failed} failed")

open(OUT, "w", encoding="utf-8").write("\n".join(out_lines) + "\n")
print(f"OK: {total}/{len(expected)} entries, {len(files)} files, "
      f"no dupes/missing/extra")
for k in sorted(cls_counts):
    print(f"  {k:14s} {cls_counts[k]}")
print(f"  {'Results':14s} {passed} passed, {failed} failed")
print(f"wrote {OUT}")
