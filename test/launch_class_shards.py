#!/usr/bin/env python3
"""Build and (optionally) launch the balanced shards of the <SLUG>
corpus run (the SECTION positional, class-1 by default).

Balancing is COST-AWARE: when a previous merged run (MERGED,
test/corpus_class1.out by default) is present, each entry's measured
time is used to estimate its cost under the rules core (measured std
time minus the one-time rule load, which the core eliminates), and
files are packed so every process gets ~equal core seconds. Files whose
cost exceeds the per-process target are split into contiguous skip/cap
chunks; the remaining whole files are LPT-packed into non-contiguous
shard-file jobs (the driver's SHARD_FILE feature). Without a previous
run it falls back to the original entry-count balancing.

Each job is one driver invocation (one process), so the shard .out
files stay in the T3 line format and merge-shards carries over
unchanged.

Usage:
  launch_class_shards.py [SECTION] [MERGED] [DRIVER]
                         # dry run: print the plan
  launch_class_shards.py [SECTION] [MERGED] [DRIVER] --launch
                         # Popen one process per job
Env:
  MR_N_PROCS    process count (default: os.cpu_count(), here 24)
  MR_SWITCHES   the matcher-substrate switch arm the shards run
                (test/run_records.py; unset = the defaults)

A launch first deletes the previous run's shard files
(test/corpus_<slug>.shard*.{out,log,files} and the pids file) and refuses
while a pid of that run is alive: a stale shard of a run with more jobs
reached the merge before (the P0 class-3 run, 2026-09-12).
"""

import importlib.util
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTION = sys.argv[1] if len(sys.argv) > 1 else "1 Algebraic functions"
MERGED = sys.argv[2] if len(sys.argv) > 2 \
    else os.path.join(ROOT, "test", "corpus_class1.out")
DRIVER = sys.argv[3] if len(sys.argv) > 3 \
    else os.path.join("test", "corpus_class1_driver.py")
SLUG = "class" + SECTION.split()[0]     # "1 …" -> class1, "2 …" -> class2
SUITE_REL = "reference/maxima-syntax-test-suite"
N_PROCS = int(os.environ.get("MR_N_PROCS") or os.cpu_count() or 24)

# Cost model for the rules-core run. The one-time rule load (measured
# 6.12-6.19 s, probes/image/probe-rule-image.out part 4) is gone under the
# core, so an entry's core wall-time ~ its measured std time minus that
# load, floored at a small positive (a no-rule-fires entry still scans the
# table). T3 baseline average compute was ~3.5 s/entry; that is the
# per-entry cost used when no measured run is available.
LOAD_EST = 6.2
FLOOR = 0.05
EST_ENTRY = 3.5

RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)\s*$")

LAUNCH = "--launch" in sys.argv
# The suite-dir positional (the driver's 5th) is REQUIRED for any
# non-default section: without it the in-process driver's file_list()
# bounds the walk to SUITE/<its hardcoded class-1 SECTION> regardless
# of FILTER, so a class-2 plan resolved 0 files / 0 jobs and the
# balance-spread print crashed with ZeroDivisionError (measured
# 2026-08-28, task-9 fix round). merge_class_shards.py carries the
# same fix and the reason the form is relative.
sys.argv = [DRIVER, SECTION + "/", "999999", "30", SUITE_REL]
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

# Per-entry measured std times, keyed (rel, entry) -> t, from the last
# merged run if present.
measured = {}
if os.path.exists(MERGED):
    for line in open(MERGED, encoding="utf-8"):
        m = RESULT.match(line.rstrip("\n"))
        if m:
            measured[(m.group(3), int(m.group(4)))] = float(m.group(2))


def entry_cost(rel, entry_no, t_std):
    if t_std is None:
        return EST_ENTRY
    return max(t_std - LOAD_EST, FLOOR)


# Per-file cost (core seconds) and per-file per-entry cost list (in entry
# order) so heavy files can be split by cost, not just count.
file_cost = []
file_entry_costs = []
for i, (path, rel) in enumerate(files):
    n = counts[i]
    ecs = []
    for e in range(1, n + 1):
        ecs.append(entry_cost(rel, e, measured.get((rel, e))))
    file_entry_costs.append(ecs)
    file_cost.append(sum(ecs))
total_cost = sum(file_cost)
using_measured = bool(measured)

target = total_cost / N_PROCS if using_measured else total / N_PROCS


def split_file(i, cap):
    """Contiguous (skip, n) chunks of file i whose cost stays <= cap."""
    ecs = file_entry_costs[i]
    chunks, s, acc = [], 0, 0.0
    for k, c in enumerate(ecs):
        if acc + c > cap and k > s:
            chunks.append((s, k - s))
            s, acc = k, c
        else:
            acc += c
    if len(ecs) - s:
        chunks.append((s, len(ecs) - s))
    return chunks


jobs = []  # each: ("range", a, b, skip, per) or ("shard", (line, ...))
if using_measured:
    # Units: heavy files split into cost-bounded chunks (a chunk is a slice
    # of ONE file, so it must be the sole chunk in its process); light files
    # are whole. LPT-pack into N_PROCS processes: each process takes at most
    # one chunk (as its annotated first file) plus whole files, filling it
    # toward the target.
    units = []  # (cost, kind, payload)
    # A process holds at most ONE chunk, so the heavy-file chunk count must
    # not exceed N_PROCS. Cost concentrated in a few heavy files (the
    # measured run-5 times give 25 chunks > 24 procs, 2026-08-27) overflows
    # it: re-split with a growing cap until it fits.
    heavy = [i for i in range(len(files)) if file_cost[i] > target]
    chunked = {}
    if heavy:
        cap = target
        while True:
            chunked = {i: split_file(i, cap) for i in heavy}
            nch = sum(len(v) for v in chunked.values())
            if nch <= N_PROCS:
                break
            if cap >= max(file_cost[i] for i in heavy):
                break  # each heavy file is one chunk; cannot do better
            cap *= 1.25
        if sum(len(v) for v in chunked.values()) > N_PROCS:
            raise SystemExit("launch_class_shards: too many heavy files "
                             f"({sum(len(v) for v in chunked.values())}) "
                             f"for {N_PROCS} processes")
    for i in range(len(files)):
        if file_cost[i] > target:
            for skip, n in chunked[i]:
                c = sum(file_entry_costs[i][skip:skip + n])
                units.append((c, "chunk", (i, skip, n)))
        else:
            units.append((file_cost[i], "whole", i))
    procs = [{"cost": 0.0, "chunk": None, "files": []}
             for _ in range(N_PROCS)]
    for cost, kind, payload in sorted(units, key=lambda u: -u[0]):
        if kind == "chunk":
            cands = [p for p in procs if p["chunk"] is None]
        else:
            cands = procs
        p = min(cands, key=lambda q: q["cost"])
        if kind == "chunk":
            p["chunk"] = payload
        else:
            p["files"].append(payload)
        p["cost"] += cost
    for p in procs:
        if p["chunk"] is None and not p["files"]:
            continue
        lines = []
        if p["chunk"] is not None:
            i, skip, n = p["chunk"]
            lines.append(f"{i} {skip} {n}")
        for k in sorted(p["files"]):
            lines.append(f"{k}")
        jobs.append(("shard", tuple(lines)))
else:
    # Count-based fallback (original behaviour).
    tgt = max(1, total // N_PROCS)
    i = 0
    while i < len(files):
        c = counts[i]
        if c > tgt:
            s = 0
            while s < c:
                n = min(tgt, c - s)
                jobs.append(("range", i, i + 1, s, n))
                s += n
            i += 1
        else:
            a = i
            acc = 0
            while i < len(files) and acc + counts[i] <= tgt:
                acc += counts[i]
                i += 1
            jobs.append(("range", a, i, 0, 999999))

# --- plan report ---------------------------------------------------------
def job_cost(job):
    if job[0] == "range":
        _, a, b, skip, per = job
        if b - a == 1 and per != 999999:
            return sum(file_entry_costs[a][skip:skip + per])
        return sum(file_cost[a:b])
    c = 0.0
    for ln in job[1]:
        parts = ln.split()
        if len(parts) == 1:
            c += file_cost[int(parts[0])]
        else:
            i, skip, n = (int(x) for x in parts)
            c += sum(file_entry_costs[i][skip:skip + n])
    return c


def job_entries(job):
    if job[0] == "range":
        _, a, b, skip, per = job
        if b - a == 1 and per != 999999:
            return min(per, counts[a] - skip)
        return sum(counts[a:b])
    e = 0
    for ln in job[1]:
        parts = ln.split()
        if len(parts) == 1:
            e += counts[int(parts[0])]
        else:
            _i, skip, n = (int(x) for x in parts)
            e += n
    return e


plan_lines = [
    f"=== {SLUG} shard plan ===",
    f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    f"files: {len(files)}  entries: {total}  jobs: {len(jobs)}  "
    f"procs: {N_PROCS}  cost-model: {'measured' if using_measured else 'count'}",
    f"total core-sec estimate: {total_cost:.0f}  "
    f"target/job: {target:.0f}s",
    "",
]
maxc = 0.0
for idx, job in enumerate(jobs):
    jc = job_cost(job)
    maxc = max(maxc, jc)
    je = job_entries(job)
    if job[0] == "range":
        _, a, b, skip, per = job
        if b - a == 1 and per != 999999:
            kind = f"file {os.path.basename(files[a][1])} e{skip+1}-e{skip+je}"
        else:
            kind = f"files[{a}:{b}] ({b-a} files)"
    else:
        nchunk = sum(1 for ln in job[1] if len(ln.split()) == 3)
        nwhole = len(job[1]) - nchunk
        kind = (f"shard ({nchunk} chunk"
                + (f" + {nwhole} file" if nwhole else "")
                + ("" if (nchunk + nwhole) == 1 else "s") + ")")
    plan_lines.append(f"shard{idx:02d}  cost={jc:8.0f}s  entries={je:6d}  {kind}")
plan_lines.append(f"max job cost: {maxc:.0f}s  (balance spread "
                  f"{maxc / (total_cost / len(jobs)):.2f}x)")

print("\n".join(plan_lines))
print(f"switches: {driver.run_records.switches_text(driver.SWITCH_SETTINGS)}")

if LAUNCH:
    try:
        removed = driver.run_records.clear_stale_shards(os.path.join(ROOT, "test"), SLUG)
    except RuntimeError as exc:
        raise SystemExit(f"launch_class_shards: {exc}")
    print(f"removed {removed} shard files of the previous run")
    pidfile = os.path.join(ROOT, "test", f"corpus_{SLUG}.shard-pids")
    shardfile_dir = os.path.join(ROOT, "test")
    with open(pidfile, "w", encoding="utf-8") as pf:
        for idx, job in enumerate(jobs):
            out = os.path.join("test", f"corpus_{SLUG}.shard{idx:02d}.out")
            log = os.path.join("test", f"corpus_{SLUG}.shard{idx:02d}.log")
            if job[0] == "range":
                _, a, b, skip, per = job
                cmd = ["python3", DRIVER, SECTION + "/", str(per), "30",
                       SUITE_REL, str(a), "", str(skip), out, str(b)]
            else:
                sfp = os.path.join(shardfile_dir,
                                   f"corpus_{SLUG}.shard{idx:02d}.files")
                with open(sfp, "w", encoding="utf-8") as sf:
                    for ln in job[1]:
                        sf.write(ln + "\n")
                cmd = ["python3", DRIVER, SECTION + "/", "999999", "30",
                       SUITE_REL, "0", "", "0", out, "0", sfp]
            lf = open(os.path.join(ROOT, log), "w", encoding="utf-8")
            p = subprocess.Popen(cmd, cwd=ROOT,
                                 stdout=lf, stderr=subprocess.STDOUT,
                                 start_new_session=True)
            pf.write(f"shard{idx:02d} {p.pid} {out}\n")
    print(f"launched {len(jobs)} shards; pids in {pidfile}")
