#!/usr/bin/env python3
"""Regression guard: an exploratory corpus_driver.py run cannot destroy a
committed record.

Motivation (.scratch/corpus-harness/issues/02, three hits): the driver's
OUT_FILE is sys.argv[8], and when it was absent the driver wrote
test/corpus_class1_driver.out — a COMMITTED record — plus its .caps
sidecar. Any exploratory invocation from the repo root silently destroyed
them, and the written file looks plausible (correct header, correct
summary block), so a stale clobber survives review.

  2026-09-18, twice: `python3 test/corpus_driver.py --help` (there is no
  --help, so the string became the FILTER and matched 0 files) replaced a
  real 77-entry 1.2.1.6 record with a 0-entry `filter: '--help'` stub.
  2026-09-20, class-6 Step 7: an exploratory slice with no out-file
  positional overwrote the same record with class-6 content; caught by a
  `git status` sweep fifteen commits later.

The ticket's conclusion is that the fix belongs in the DEFAULT, not in a
discipline reminder. Four checks (no Maxima entries — the runs use a
filter that matches no file):

  1. a first argument starting with `-` is refused with a usage message
     on stderr and a nonzero exit — the reflex that caused hit 1 now
     prints how to call the driver instead of running with FILTER='-...'.
  2. that refusal writes NOTHING: the committed record and its sidecar
     keep their bytes.
  3. the no-out-file default resolves to a path that is neither tracked
     nor writable-by-accident-into-git: `git ls-files` does not know it
     and `git check-ignore` does.
  4. a real no-out-file run writes that default and leaves the committed
     record byte-identical.

Re-runnable:  python3 test/test_driver_out_default.py
Exits nonzero if any check fails.
"""

import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DRIVER = os.path.join(HERE, "corpus_driver.py")

# The record the three hits destroyed. It is the canary here: whatever the
# default becomes, this file must not move when no out-file is named.
RECORD = os.path.join(ROOT, "test", "corpus_class1_driver.out")

# A filter no suite file can match, so a run costs no Maxima entry.
NO_MATCH_FILTER = "ZZ no such section ZZ"


def digest(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def default_out_file():
    """The out path the driver resolves when argv has no out-file."""
    out = subprocess.run(
        [sys.executable, "-c", (
            "import importlib.util, sys\n"
            "sys.argv = ['corpus_driver.py', %r, '1', '30']\n"
            "spec = importlib.util.spec_from_file_location('drv', %r)\n"
            "d = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(d)\n"
            "print(d.DEFAULT_OUT_FILE)\n" % (NO_MATCH_FILTER, DRIVER)
        )], capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        return None, out.stderr[-600:]
    return out.stdout.strip(), ""


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args],
                          capture_output=True, text=True)


def main():
    failures = []

    # --- 1/2: a dash-led first argument is refused, and writes nothing.
    before = digest(RECORD)
    before_caps = digest(os.path.splitext(RECORD)[0] + ".caps")
    p = subprocess.run([sys.executable, DRIVER, "--help"],
                       capture_output=True, text=True, cwd=ROOT)
    if p.returncode == 0 or "usage" not in (p.stderr + p.stdout).lower():
        failures.append("[usage] `--help` did not print a usage message and "
                        f"exit nonzero (rc={p.returncode}, "
                        f"err={p.stderr[-300:]!r})")
    else:
        print("PASS [usage] a dash-led first argument prints usage, exits "
              f"{p.returncode}")

    if digest(RECORD) != before:
        failures.append("[usage-writes-nothing] the committed record moved")
    elif digest(os.path.splitext(RECORD)[0] + ".caps") != before_caps:
        failures.append("[usage-writes-nothing] the .caps sidecar moved")
    else:
        print("PASS [usage-writes-nothing] committed record and sidecar "
              "byte-identical")

    # --- 3: the default out path is untracked and gitignored.
    default, err = default_out_file()
    if default is None:
        failures.append(f"[default-path] driver has no DEFAULT_OUT_FILE: {err}")
    else:
        rel = os.path.relpath(default, ROOT)
        tracked = git("ls-files", "--error-unmatch", rel).returncode == 0
        ignored = git("check-ignore", "-q", rel).returncode == 0
        if tracked:
            failures.append(f"[default-path] {rel} is TRACKED — a no-out-file "
                            "run would still destroy a committed file")
        elif not ignored:
            failures.append(f"[default-path] {rel} is not gitignored — a "
                            "no-out-file run would litter `git status`, which "
                            "is the sweep that caught hit 3")
        else:
            print(f"PASS [default-path] {rel} untracked and gitignored")

    # --- 4: a real no-out-file run writes the default, not the record.
    if default is not None:
        before = digest(RECORD)
        if os.path.exists(default):
            os.unlink(default)
        p = subprocess.run(
            [sys.executable, DRIVER, NO_MATCH_FILTER, "1", "30"],
            capture_output=True, text=True, cwd=ROOT)
        if digest(RECORD) != before:
            failures.append("[no-out-file] the run overwrote the committed "
                            "record test/corpus_class1_driver.out")
        elif not os.path.exists(default):
            failures.append(f"[no-out-file] the run wrote no {default} "
                            f"(rc={p.returncode}, err={p.stderr[-300:]!r})")
        else:
            print("PASS [no-out-file] run wrote the scratch default, record "
                  "byte-identical")

    for f in failures:
        print(f"FAIL {f}")
    print(f"Results: {4 - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
