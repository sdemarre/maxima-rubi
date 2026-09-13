#!/usr/bin/env python3
"""Per-record wall-time summary of merged corpus records.

The matcher substrate migration's performance gate (spec
docs/superpowers/specs/2026-09-12-matcher-substrate-design.md section 4)
compares the per-class median per-entry wall of a new record with the P0
baseline. For each record this prints: entries, PASS count (the driver's
PASS_CLASSES, read through test/ab_records.py), median and p90 of the t=
field over ALL entries, and the timeout count.

Usage:  python3 test/record_medians.py RECORD [RECORD ...]
"""

import importlib.util
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("ab_records", os.path.join(HERE, "ab_records.py"))
ab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ab)


def summarize(path, pass_classes):
    rec = ab.load_record(path)
    times = sorted(t for _cls, t in rec.values())
    n = len(times)
    return {
        "entries": n,
        "pass": sum(1 for cls, _t in rec.values() if cls in pass_classes),
        "median": statistics.median(times) if n else 0.0,
        "p90": times[min(n - 1, int(0.9 * n))] if n else 0.0,
        "timeouts": sum(1 for cls, _t in rec.values() if cls == "timeout"),
    }


def main(argv):
    if not argv:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 64
    pass_classes = ab.driver_pass_classes()
    for path in argv:
        s = summarize(path, pass_classes)
        print(f"{path}: entries {s['entries']}  PASS {s['pass']}  median {s['median']:.1f}s  "
              f"p90 {s['p90']:.1f}s  timeout {s['timeouts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
