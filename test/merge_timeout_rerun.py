#!/usr/bin/env python3
"""Merge the timeout re-check shards (standing cap 100 s; the cap is
read from the shard headers) into test/corpus_class1.timeout100s.out
and report the transitions.

The re-check re-runs EXACTLY the entries the accepted run
(test/corpus_class1.out, commit 45fc9b8) classified `timeout`, at a
300 s per-entry cap instead of 30 s (24 shards, same rules core).
Completeness is asserted against that accepted set: the merged key set
must equal it exactly (no dupes, no missing, no extra) — unlike the
full-run merge, this is a SUBSET merge, so this script must not be used
on the full shard set.

Reports (stdout, captured by the watcher into
test/timeout_rerun_merge.out):
  - new class counts over the re-checked set (transition from timeout);
  - how many of the re-checked set were PASS in the run-5 baseline
    (test/corpus_class1.run5-accept.out) — separates the
    budget-starved correct answers (ticket 01) from the genuine
    non-terminators;
  - per-family breakdown of the still-timeout set (the non-termination
    hot spots, input to the matcher work).

Usage:
  merge_timeout_rerun.py [shard-glob] [out-file] [source-record]
Defaults: /tmp/opencode/timeout_recheck/shard*.out,
test/corpus_class1.timeout100s.out, test/corpus_class1.out (the accepted
record — the completeness set is its `timeout` class).
"""

import glob
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN5 = os.path.join(ROOT, "test", "corpus_class1.run5-accept.out")
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$")
PASS_CLASSES = {"expected", "verified", "no-answer"}

SHARD_GLOB = (sys.argv[1] if len(sys.argv) > 1
              else "/tmp/opencode/timeout_recheck/shard*.out")
OUT = (sys.argv[2] if len(sys.argv) > 2
       else os.path.join(ROOT, "test", "corpus_class1.timeout100s.out"))
ACCEPTED = (sys.argv[3] if len(sys.argv) > 3
            else os.path.join(ROOT, "test", "corpus_class1.out"))
# Section slug for the record header, from the source-record basename
# (the D3 $(basename "$SRC" .out) idiom in wait_timeout_rerun.sh):
# corpus_class1.out -> class-1, corpus_class2.out -> class-2.
SRC_BASE = os.path.basename(ACCEPTED)
SLUG = re.sub(r"^(class)(\d+)$", r"\1-\2",
              re.sub(r"^corpus_", "",
                     SRC_BASE[:-4] if SRC_BASE.endswith(".out") else SRC_BASE))


def parse(path):
    d = {}
    for line in open(path, encoding="utf-8"):
        m = RESULT.match(line.rstrip("\n"))
        if m:
            d[(m.group(3), int(m.group(4)))] = m
    return d


def family(rel):
    return os.path.basename(rel)[:-4]


accepted = parse(ACCEPTED)
expected = {k for k, m in accepted.items() if m.group(1) == "timeout"}
run5 = parse(RUN5) if os.path.exists(RUN5) else {}

seen = {}
dupes = 0
inputs = sorted(glob.glob(SHARD_GLOB))
assert inputs, f"no shard .out files match {SHARD_GLOB}"
for path in inputs:
    for line in open(path, encoding="utf-8"):
        m = RESULT.match(line.rstrip("\n"))
        if not m:
            continue
        k = (m.group(3), int(m.group(4)))
        if k in seen:
            dupes += 1
        seen[k] = m
# The per-entry cap, from the driver's shard header (each shard .out
# carries "timeout: <n>s") — the merge must not assume the cap.
cap = None
for path in inputs:
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^filter: .*timeout: (\d+)s", line)
        if m:
            cap = m.group(1)
            break
    if cap:
        break

missing = expected - set(seen)
extra = set(seen) - expected
if dupes or missing or extra:
    print(f"INCOMPLETE: dupes={dupes} missing={len(missing)} "
          f"extra={len(extra)}", file=sys.stderr)
    for k in sorted(missing)[:10]:
        print("  missing", k, file=sys.stderr)
    for k in sorted(extra)[:10]:
        print("  extra  ", k, file=sys.stderr)
    sys.exit(1)

out_lines = [
    f"=== maxima-rubi {SLUG} corpus: {cap} s timeout re-check "
    f"({len(inputs)} shards merged) ===",
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
# The MERGED record carries the source path RELATIVE to the repo root
# (the class-1 precedent form); the launcher's <run-dir>/source file
# may hold an absolute path (the watcher relies on it resolving).
try:
    accepted_rel = os.path.relpath(ACCEPTED, ROOT)
except ValueError:
    accepted_rel = ACCEPTED
out_lines.append(
    f"re-check of the {len(expected)} `timeout` entries of {accepted_rel} "
    f"(30 s cap) at a {cap} s per-entry cap, same rules core")
out_lines.append("")

cls_of = {k: seen[k].group(1) for k in expected}
for k in sorted(expected):
    m = seen[k]
    out_lines.append(f"{m.group(1):14s} t={float(m.group(2)):6.1f}s "
                     f"{m.group(3)} e{m.group(4)} L{m.group(5)}")

cls_counts = Counter(cls_of.values())
out_lines.append("")
out_lines.append("=== summary ===")
for k in sorted(cls_counts):
    v = cls_counts[k]
    out_lines.append(f"{k:14s} {v:6d}  "
                     f"{100 * v / sum(cls_counts.values()):5.1f}%")
total = sum(cls_counts.values())
passed = sum(v for k, v in cls_counts.items() if k in PASS_CLASSES)
out_lines.append(f"{'total':14s} {total:6d}")
out_lines.append(f"Results: {passed} passed, {total - passed} failed")

open(OUT, "w", encoding="utf-8").write("\n".join(out_lines) + "\n")

# --- reports -------------------------------------------------------------
print(f"OK: {total}/{len(expected)} re-checked, no dupes/missing/extra")
print(f"wrote {OUT}")
print()
print("=== transitions (all were `timeout` in the accepted run) ===")
for k in sorted(cls_counts):
    print(f"  {k:14s} {cls_counts[k]}")
print(f"  now-PASS: {passed}")
print()
run5_of = Counter(run5[k].group(1) for k in expected if k in run5)
run5_pass = sum(v for c, v in run5_of.items() if c in PASS_CLASSES)
print(f"=== run-5 baseline status of the {len(expected)} re-checked ===")
for k in sorted(run5_of):
    print(f"  {k:14s} {run5_of[k]}")
print(f"  PASS in run-5: {run5_pass}")
regressed = [k for k in expected
             if k in run5 and run5[k].group(1) in PASS_CLASSES
             and cls_of[k] not in PASS_CLASSES]
still = [k for k in regressed if cls_of[k] == "timeout"]
print(f"  run-5 PASS still failing now: {len(regressed)} "
      f"({len(still)} of them still timeout at {cap} s)")
for k in sorted(still):
    print(f"    {family(k[0])} e{k[1]}: run-5 "
          f"{run5[k].group(1)} t={run5[k].group(2)}s -> timeout "
          f"t={seen[k].group(2)}s")
print()
st_timeout = [k for k in expected if cls_of[k] == "timeout"]
by_family = Counter(family(k[0]) for k in st_timeout)
print(f"=== still timeout at {cap} s: {len(st_timeout)} entries, "
      "by family ===")
for fam, n in by_family.most_common():
    print(f"  {n:5d}  {fam}")
unv = [k for k in expected if cls_of[k] == "unverified"]
by_family = Counter(family(k[0]) for k in unv)
print(f"=== unverified at {cap} s: {len(unv)} entries, by family ===")
for fam, n in by_family.most_common(12):
    print(f"  {n:5d}  {fam}")
