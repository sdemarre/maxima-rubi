#!/usr/bin/env python3
"""Build and (optionally) launch the balanced shards of the class-1
corpus run.

The plan is a list of driver jobs.  Files longer than the per-shard
target are split into single-file partial jobs (skip-first + per-file
cap); the remaining whole files are grouped into contiguous ranges.
Each job is one driver invocation, so the shard .out files stay in the
T3 line format and merge-shards carries over.

Usage:
  launch_class1_shards.py            # dry run: print the plan
  launch_class1_shards.py --launch   # Popen one process per job
"""

import importlib.util
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVER = os.path.join("test", "corpus_class1_driver.py")
SECTION = "1 Algebraic functions"
SUITE_REL = "reference/maxima-syntax-test-suite"
N_SHARDS = 18

sys.argv = ["corpus_class1_driver.py", SECTION + "/", "999999", "30"]
_spec = importlib.util.spec_from_file_location("driver",
                                               os.path.join(ROOT, DRIVER))
assert _spec is not None and _spec.loader is not None
driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(driver)

files = driver.file_list()
counts = []
for path, _rel in files:
    entries, _ = driver.extract_entries(path)
    counts.append(len(entries))
total = sum(counts)


def build_jobs(target):
    jobs = []
    i = 0
    while i < len(files):
        c = counts[i]
        if c > target:
            s = 0
            while s < c:
                n = min(target, c - s)
                jobs.append((i, i + 1, s, n))
                s += n
            i += 1
        else:
            a = i
            acc = 0
            while i < len(files) and acc + counts[i] <= target:
                acc += counts[i]
                i += 1
            jobs.append((a, i, 0, 999999))
    return jobs


target = max(1, total // N_SHARDS)
jobs = build_jobs(target)
while len(jobs) > N_SHARDS:
    target = int(target * 1.15) + 1
    jobs = build_jobs(target)

plan_lines = [
    "=== class-1 shard plan ===",
    f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    f"files: {len(files)}  entries: {total}  jobs: {len(jobs)}  "
    f"target: {target}",
    "",
]
covered = 0
for idx, (a, b, skip, per) in enumerate(jobs):
    if b - a == 1 and per != 999999:
        n = min(per, counts[a] - skip)
        kind = f"file {os.path.basename(files[a][1])} e{skip + 1}-e{skip + n}"
    else:
        n = sum(counts[a:b])
        kind = f"files[{a}:{b}] ({b - a} files)"
    covered += n
    plan_lines.append(f"shard{idx:02d}  entries={n:6d}  {kind}")
plan_lines.append(f"covered entries: {covered}")

print("\n".join(plan_lines))

if "--launch" in sys.argv:
    pidfile = os.path.join(ROOT, "test", "corpus_class1.shard-pids")
    with open(pidfile, "w", encoding="utf-8") as pf:
        for idx, (a, b, skip, per) in enumerate(jobs):
            out = os.path.join("test", f"corpus_class1.shard{idx:02d}.out")
            log = os.path.join("test", f"corpus_class1.shard{idx:02d}.log")
            cmd = ["python3", DRIVER,
                   SECTION + "/", str(per), "30",
                   SUITE_REL, str(a), "", str(skip), out, str(b)]
            lf = open(os.path.join(ROOT, log), "w", encoding="utf-8")
            p = subprocess.Popen(cmd, cwd=ROOT,
                                 stdout=lf, stderr=subprocess.STDOUT,
                                 start_new_session=True)
            pf.write(f"shard{idx:02d} {p.pid} {out}\n")
    print(f"launched {len(jobs)} shards; pids in {pidfile}")
