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
# 60 s per target: the zero chain runs BOTH stage orders (factor-first
# and ratsimp-first — closure is order-dependent, measured 2026-08-25)
# and the slow non-closing stage of the radical-diff family alone
# exceeds 30 s. See zero_chain in corpus_class1_driver.py.
TIMEOUT = 60

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


def _load(listfile):
    # <filter ...> <entry> — the filter may contain spaces (a full file
    # name), so the last whitespace-separated token is the entry number.
    targets = []
    for line in open(listfile, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        targets.append((" ".join(parts[:-1]), int(parts[-1])))
    return targets


def main():
    args = [a for a in REAL_ARGV[1:]]
    parallel = 1
    if "--parallel" in args:
        i = args.index("--parallel")
        parallel = int(args[i + 1])
        del args[i:i + 2]
    if len(args) == 2 and args[1].isdigit():
        targets = [(args[0], int(args[1]))]
    elif len(args) == 1 and os.path.exists(args[0]):
        targets = _load(args[0])
    elif not args and os.path.exists(CANARY):
        targets = _load(CANARY)
    else:
        print("usage: canary.py [listfile | file-substring entry] "
              "[--parallel N]")
        return
    if not targets:
        print("no canary targets (empty list)")
        return

    from concurrent.futures import ThreadPoolExecutor
    npass = nfail = 0
    if parallel > 1:
        with ThreadPoolExecutor(max_workers=parallel) as ex:
            results = list(ex.map(lambda t: run_target(*t), targets))
    else:
        results = [run_target(*t) for t in targets]
    for pf, cls, dt, label, _out in results:
        if pf == "PASS":
            npass += 1
        else:
            nfail += 1
        print(f"{pf}: {cls:12s} t={dt:5.1f}s {label}")
    print(f"\nResults: {npass} passed, {nfail} failed  "
          f"({len(targets)} targets)")


if __name__ == "__main__":
    main()
