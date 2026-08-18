#!/usr/bin/env python3
"""Compute the phase-2 resume arguments for probe-integrate-sample.py.

Usage: python3 probes/corpus/resume-info.py

Reads the streamed probes/corpus/probe-integrate-sample.out (phase 1,
filter "1 Algebraic functions/", all entries) and prints the two
arguments a killed or capped phase 1 needs to resume:

  START_INDEX   0-based index, in the sorted file list, of the first
                file whose entries are not all present in .out (the
                file that was in flight when the run died);
  SKIP_ENTRIES  number of that file's entry lines already in .out, so
                phase 2 starts exactly after them.

Launch phase 2 as (suite dir + the two numbers):
  python3 probes/corpus/probe-integrate-sample.py "1 Algebraic functions/" \
      999999 30 reference/maxima-syntax-test-suite \
      $START_INDEX append $SKIP_ENTRIES

If every file is fully covered, prints START_INDEX = len(files) with
SKIP_ENTRIES = 0 (nothing left to do).
"""

import importlib.util
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# load the sample driver as a module with its phase-1 argv (4 args), so
# file_list() reproduces phase 1's sorted file list exactly
sys.argv = ["probe-integrate-sample.py", "1 Algebraic functions/",
            "999999", "30"]
_spec = importlib.util.spec_from_file_location("smp",
                                              ROOT / "probes" / "corpus"
                                              / "probe-integrate-sample.py")
assert _spec is not None and _spec.loader is not None
_smp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_smp)

out_path = ROOT / "probes" / "corpus" / "probe-integrate-sample.out"
counts = Counter()
for line in out_path.read_text(encoding="utf-8").splitlines():
    m = re.match(r"^\S+\s+t=\s*[\d.]+s\s+(.*) e(\d+) L\d+$", line)
    if m:
        counts[m.group(1)] += 1

files = _smp.file_list()
start_index = len(files)
skip = 0
expected = 0
warned = False
for i, (_p, rel) in enumerate(files):
    try:
        entries, _ = _smp.extract_entries(_p)
        expected = len(entries)
    except (AssertionError, UnicodeDecodeError, IndexError):
        expected = 0
    have = counts.get(rel, 0)
    if have > expected:
        print(f"WARNING: {have} result lines for {rel} but only "
              f"{expected} entries in the file", file=sys.stderr)
        warned = True
    if have < expected:
        start_index = i
        skip = have
        break
if warned:
    sys.exit(2)
print(f"START_INDEX={start_index}")
print(f"SKIP_ENTRIES={skip}")
if start_index < len(files):
    print(f"in-flight file: {files[start_index][1]}", file=sys.stderr)
    print(f"  {skip}/{expected} entries already in .out", file=sys.stderr)
