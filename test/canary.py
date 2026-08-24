#!/usr/bin/env python3
"""Fast canary loop for the class-1 divergence chase.

Re-runs a small explicit set of (file, entry) targets — the entries that
are currently failing — in fresh Maxima subprocesses, so a fix gets
~1-minute feedback instead of a 3-hour full run. The full sharded run is
reserved for the final confidence gate.

The canary set lives in test/canary.entries, one target per line:
    <file-substring> <1-based entry number>
Blank lines and #-comments are ignored. Grow it as new failures appear.

Usage:
    python3 test/canary.py              # run the whole canary set
    python3 test/canary.py 1.1.1.3 3    # run one ad-hoc target
"""

import importlib.util
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVER = os.path.join("test", "corpus_class1_driver.py")
SECTION = "1 Algebraic functions"
CANARY = os.path.join("test", "canary.entries")
TIMEOUT = 30

REAL_ARGV = sys.argv[:]
sys.argv = ["corpus_class1_driver.py", SECTION + "/", "999999", "30"]
_spec = importlib.util.spec_from_file_location("driver",
                                               os.path.join(ROOT, DRIVER))
assert _spec is not None and _spec.loader is not None
driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(driver)

PASS_CLASSES = {"expected", "verified", "no-answer"}


def resolve(filter, entry_no):
    files = driver.file_list()
    for path, rel in files:
        if filter in rel:
            entries, line_nos = driver.extract_entries(path)
            if 1 <= entry_no <= len(entries):
                return path, rel, entries, line_nos, entry_no
    raise SystemExit(f"canary target not found: {filter!r} e{entry_no}")


def run_target(filter, entry_no):
    path, rel, entries, line_nos, entry_no = resolve(filter, entry_no)
    els = driver.split_elements(entries[entry_no - 1][1:-1])
    f_text, var_text, _steps, e_text = els[0], els[1], els[2], els[3]
    e_text2 = els[4] if len(els) == 5 else None
    label = f"{filter} e{entry_no} L{line_nos[entry_no - 1]}"
    t0 = time.time()
    out, timed_out = driver.maxima_run(
        driver.build_text(f_text, var_text, e_text, e_text2), TIMEOUT)
    dt = time.time() - t0
    cls = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("CLASS "):
            cls = line[6:].strip()
            break
    if cls is None:
        cls = "timeout" if timed_out else "error"
    if cls not in driver.KNOWN_CLASSES:
        cls = "error"
    pf = "PASS" if cls in PASS_CLASSES else "FAIL"
    return pf, cls, dt, label, out


def main():
    targets = []
    if len(REAL_ARGV) >= 3 and REAL_ARGV[1] != "":
        targets.append((REAL_ARGV[1], int(REAL_ARGV[2])))
    elif os.path.exists(CANARY):
        for line in open(CANARY, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            filt, no = line.split(None, 1)
            targets.append((filt, int(no)))
    if not targets:
        print("no canary targets (empty test/canary.entries)")
        return

    npass = nfail = 0
    for filt, no in targets:
        pf, cls, dt, label, _out = run_target(filt, no)
        if pf == "PASS":
            npass += 1
        else:
            nfail += 1
        print(f"{pf}: {cls:12s} t={dt:5.1f}s {label}")
    print(f"\nResults: {npass} passed, {nfail} failed  "
          f"({len(targets)} targets)")


if __name__ == "__main__":
    main()
