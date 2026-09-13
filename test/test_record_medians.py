#!/usr/bin/env python3
"""Checks for test/record_medians.py (no Maxima; synthetic records).

  1. summarize(): entries, PASS count (driver PASS_CLASSES), median, p90,
     timeout count on an odd-sized record.
  2. median of an even-sized record is the mean of the two middle values.
  3. CLI prints one summary line per record, in the documented format.

Re-runnable:  python3 test/test_record_medians.py
"""

import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("record_medians", os.path.join(HERE, "record_medians.py"))
rm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rm)

HEADER = "=== maxima-rubi class3 corpus run (full, 24 shards merged) ===\nfilter: '3 Logarithms/'\n\n"
ODD = HEADER + """\
verified       t=   1.0s 3 Logarithms/a b.mac e1 L10
verified       t=   2.0s 3 Logarithms/a b.mac e2 L11
deferred       t=   3.0s 3 Logarithms/a b.mac e3 L12
no-answer      t=   4.0s 3 Logarithms/a b.mac e4 L13
timeout        t=  30.0s 3 Logarithms/a b.mac e5 L14
Results: 3 passed, 2 failed
"""
EVEN = HEADER + """\
verified       t=   1.0s 3 Logarithms/a b.mac e1 L10
verified       t=   2.0s 3 Logarithms/a b.mac e2 L11
verified       t=   4.0s 3 Logarithms/a b.mac e3 L12
verified       t=   9.0s 3 Logarithms/a b.mac e4 L13
"""


def write(tmp, name, text):
    p = os.path.join(tmp, name)
    with open(p, "w") as f:
        f.write(text)
    return p


def main():
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        odd, even = write(tmp, "odd.out", ODD), write(tmp, "even.out", EVEN)
        s = rm.summarize(odd, rm.ab.driver_pass_classes())
        want = {"entries": 5, "pass": 3, "median": 3.0, "p90": 30.0, "timeouts": 1}
        print(("PASS:" if s == want else "FAIL:"), "summarize odd record", s)
        if s != want:
            failures.append("summarize odd")
        s = rm.summarize(even, rm.ab.driver_pass_classes())
        ok = s["median"] == 3.0 and s["entries"] == 4
        print(("PASS:" if ok else "FAIL:"), "even median", s)
        if not ok:
            failures.append("even median")
        out = subprocess.run([sys.executable, os.path.join(HERE, "record_medians.py"), odd, even],
                             capture_output=True, text=True).stdout.splitlines()
        want_line = f"{odd}: entries 5  PASS 3  median 3.0s  p90 30.0s  timeout 1"
        ok = len(out) == 2 and out[0] == want_line
        print(("PASS:" if ok else "FAIL:"), "CLI lines", out)
        if not ok:
            failures.append("cli")
    print(f"Results: {3 - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
