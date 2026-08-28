#!/usr/bin/env python3
"""Launch the timeout re-check: re-run ONLY the entries a previous
class-1 run record classified `timeout`, at a larger per-entry cap,
in balanced shards.

Policy (decision 2026-08-27): the 30 s per-entry cap STAYS the
standard. This re-check is the standing verification for "is the 30 s
cap the limiting factor?" — run it on a record's timeout set whenever
that question is live. The first use (the 787-entry re-check of the
accepted run, 300 s cap) is recorded in test/corpus_class1.timeout5m.out
+ .scratch/class1-ab-remainders/issues/05.

Usage:
  launch_timeout_rerun.py [source-record] [cap-s] [run-dir] [section]
                          [--launch]
Defaults: test/corpus_class1.out (the accepted record), 300 s cap,
run-dir /tmp/opencode/timeout_recheck-<utc-stamp>, section "1 Algebraic
functions". Without --launch this is a dry run (prints the plan only).
Env: MR_N_PROCS process count (default os.cpu_count()).

Mechanics: the timeout entries of the source record (sorted by file,
entry) are dealt round-robin into N_PROCS shard files — one
`idx skip 1` line per entry, the driver's SHARD_FILE chunk format —
and each shard is one driver invocation at the cap. Completeness is
asserted against the source record at merge time (test/
merge_timeout_rerun.py), which also reports the transitions.

The driver module is imported for its file list and entry mechanics,
which runs ensure_rules_core() at import: the re-check runs the
CURRENT core. It is comparable to the source record only if the
fingerprint matches — check test/mr_rules.core.stamp against the
record's run before drawing conclusions.

After launching, start the watcher:
  setsid sh test/wait_timeout_rerun.sh <run-dir> \
      >> <run-dir>/wait.log 2>&1 &
"""

import importlib.util
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE_REL = "reference/maxima-syntax-test-suite"
N_PROCS = int(os.environ.get("MR_N_PROCS") or os.cpu_count() or 24)
RESULT = re.compile(r"^timeout\s+t=\s*[\d.]+s\s+(.*) e(\d+) L(\d+)\s*$")

LAUNCH = "--launch" in sys.argv
pos = [a for a in sys.argv[1:] if a != "--launch"]
SRC = os.path.abspath(pos[0] if len(pos) > 0 else
                      os.path.join(ROOT, "test", "corpus_class1.out"))
CAP = int(pos[1]) if len(pos) > 1 else 300
SECTION = pos[3] if len(pos) > 3 else "1 Algebraic functions"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
RUN_DIR = (pos[2] if len(pos) > 2
           else f"/tmp/opencode/timeout_recheck-{STAMP}")
# The class-1 section keeps the re-exporting shim (behaviorally the
# same module); class 2 points at the generalized driver directly.
# The path stays ABSOLUTE: the subprocess cmd below runs it by bare
# name (a bare filename here would not resolve).
DRIVER = os.path.join(ROOT, "test",
                      "corpus_class1_driver.py"
                      if SECTION == "1 Algebraic functions"
                      else "corpus_driver.py")

sys.argv = ["corpus_class1_driver.py", SECTION + "/", "999999", str(CAP),
            SUITE_REL]
_spec = importlib.util.spec_from_file_location("driver", DRIVER)
assert _spec is not None and _spec.loader is not None
driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(driver)

files = driver.file_list()
rel2idx = {rel: i for i, (_p, rel) in enumerate(files)}

to = []
for line in open(SRC, encoding="utf-8"):
    m = RESULT.match(line.rstrip("\n"))
    if m:
        to.append((m.group(1), int(m.group(2))))
assert to, f"no timeout entries in {SRC}"
bad = [t for t in to if t[0] not in rel2idx]
assert not bad, f"entries not in the current file list: {bad[:3]}"

shards = [[] for _ in range(N_PROCS)]
for n, (rel, e) in enumerate(sorted(to)):
    shards[n % N_PROCS].append(f"{rel2idx[rel]} {e - 1} 1")

plan = [
    "=== timeout re-check plan ===",
    f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    f"source record: {SRC}  timeout entries: {len(to)}  "
    f"cap: {CAP}s  procs: {N_PROCS}  run-dir: {RUN_DIR}",
    f"core fingerprint: "
    f"{open(os.path.join(ROOT, 'test', 'mr_rules.core.stamp')).read().splitlines()[0]}",
]
for idx, lines in enumerate(shards):
    plan.append(f"shard{idx:02d}  entries={len(lines)}")
print("\n".join(plan))

if not LAUNCH:
    sys.exit(0)

os.makedirs(RUN_DIR, exist_ok=True)
# Self-description for the watcher (test/wait_timeout_rerun.sh reads
# <run-dir>/source for the completeness set):
with open(os.path.join(RUN_DIR, "source"), "w", encoding="utf-8") as fh:
    fh.write(SRC + "\n")
pidfile = os.path.join(RUN_DIR, "pids")
with open(pidfile, "w", encoding="utf-8") as pf:
    for idx, lines in enumerate(shards):
        sfp = os.path.join(RUN_DIR, f"shard{idx:02d}.files")
        with open(sfp, "w", encoding="utf-8") as sf:
            for ln in lines:
                sf.write(ln + "\n")
        out = os.path.join(RUN_DIR, f"shard{idx:02d}.out")
        log = os.path.join(RUN_DIR, f"shard{idx:02d}.log")
        cmd = [sys.executable, DRIVER, SECTION + "/", "999999",
               str(CAP), SUITE_REL, "0", "", "0", out, "0", sfp]
        lf = open(log, "w", encoding="utf-8")
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=lf,
                             stderr=subprocess.STDOUT,
                             start_new_session=True)
        pf.write(f"shard{idx:02d} {p.pid} {out}\n")
print(f"launched {N_PROCS} shards; pids in {pidfile}")
print(f"next: setsid sh test/wait_timeout_rerun.sh {RUN_DIR} "
      f">> {RUN_DIR}/wait.log 2>&1 &")
