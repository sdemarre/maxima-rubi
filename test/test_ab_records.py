#!/usr/bin/env python3
"""Checks for test/ab_records.py, the entry-level A/B of two merged
corpus records (no Maxima; synthetic records in a temp dir).

  1. result lines parse (padded t=, relpaths with spaces); header and
     summary lines are skipped.
  2. a duplicate (rel, entry) key is an error, not a silent overwrite.
  3. the PASS/FAIL 2x2 table and the PASS->FAIL list are exact.
  4. key-set mismatches (missing/extra entries) are reported and make
     the CLI exit nonzero.
  5. the PASS classes are read from corpus_driver.py (single source of
     truth), not a copied set.
  6. CLI end to end: the report carries the 2x2 table and every
     PASS->FAIL line.

Re-runnable:  python3 test/test_ab_records.py
Exits nonzero if any check fails.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

_spec = importlib.util.spec_from_file_location(
    "ab_records", os.path.join(HERE, "ab_records.py"))
ab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ab)

HEADER = """=== maxima-rubi class3 corpus run (full, 24 shards merged) ===
merge date: 2026-09-04 15:06 UTC
filter: '3 Logarithms/'  full run  timeout: 30s  (24 shards, merged here)

"""
SUMMARY = """
=== summary ===
verified            2   66.7%
total               3
Results: 2 passed, 1 failed
"""

BASE = HEADER + """\
verified       t=   1.7s 3 Logarithms/3.1.2 (d x)^m (a+b log(c x^n))^p.mac e1 L10
verified       t=  28.1s 3 Logarithms/3.1.5 u (a+b log(c x^n))^p.mac e44 L60
deferred       t=   0.4s 3 Logarithms/3.5 Logarithm functions.mac e7 L20
no-answer      t=   4.8s 3 Logarithms/3.5 Logarithm functions.mac e8 L21
""" + SUMMARY

NEW = HEADER + """\
verified       t=  12.9s 3 Logarithms/3.1.2 (d x)^m (a+b log(c x^n))^p.mac e1 L10
timeout        t=  30.0s 3 Logarithms/3.1.5 u (a+b log(c x^n))^p.mac e44 L60
expected       t=   0.9s 3 Logarithms/3.5 Logarithm functions.mac e7 L20
no-answer      t=   4.1s 3 Logarithms/3.5 Logarithm functions.mac e8 L21
""" + SUMMARY

K1 = ("3 Logarithms/3.1.2 (d x)^m (a+b log(c x^n))^p.mac", 1)
K44 = ("3 Logarithms/3.1.5 u (a+b log(c x^n))^p.mac", 44)
K7 = ("3 Logarithms/3.5 Logarithm functions.mac", 7)
K8 = ("3 Logarithms/3.5 Logarithm functions.mac", 8)


def _write(tmp, name, text):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def check_parse(tmp, failures):
    rec = ab.load_record(_write(tmp, "base.out", BASE))
    want = {K1: ("verified", 1.7), K44: ("verified", 28.1),
            K7: ("deferred", 0.4), K8: ("no-answer", 4.8)}
    if rec != want:
        failures.append(f"[parse] got {rec}")
    else:
        print("PASS [parse] 4 result lines, header/summary skipped")


def check_duplicate(tmp, failures):
    dup = BASE.replace(SUMMARY, "verified       t=   2.0s "
                       "3 Logarithms/3.5 Logarithm functions.mac e7 L20\n")
    try:
        ab.load_record(_write(tmp, "dup.out", dup))
    except ValueError as exc:
        print(f"PASS [duplicate] rejected: {exc}")
    else:
        failures.append("[duplicate] duplicate key accepted silently")


def check_table(tmp, failures):
    a = ab.load_record(_write(tmp, "base.out", BASE))
    b = ab.load_record(_write(tmp, "new.out", NEW))
    r = ab.compare(a, b, {"expected", "verified", "no-answer"})
    table = {"PASS->PASS": 2, "PASS->FAIL": 1, "FAIL->PASS": 1,
             "FAIL->FAIL": 0}
    if r["table"] != table:
        failures.append(f"[table] got {r['table']}, want {table}")
    elif [k for k, _, _ in r["pass_fail"]] != [K44]:
        failures.append(f"[table] pass_fail {r['pass_fail']}")
    elif [k for k, _, _ in r["fail_pass"]] != [K7]:
        failures.append(f"[table] fail_pass {r['fail_pass']}")
    elif r["missing"] or r["extra"]:
        failures.append(f"[table] spurious key diff {r['missing']} "
                        f"{r['extra']}")
    else:
        print("PASS [table] 2x2 exact; PASS->FAIL = [e44]; FAIL->PASS = [e7]")


def check_keyset(tmp, failures):
    short = NEW.replace(
        "no-answer      t=   4.1s 3 Logarithms/3.5 Logarithm functions.mac"
        " e8 L21\n", "")
    a = ab.load_record(_write(tmp, "base.out", BASE))
    b = ab.load_record(_write(tmp, "short.out", short))
    r = ab.compare(a, b, {"expected", "verified", "no-answer"})
    if r["missing"] != [K8] or r["extra"]:
        failures.append(f"[keyset] missing {r['missing']} extra {r['extra']}")
        return
    proc = subprocess.run(
        [sys.executable, os.path.join(HERE, "ab_records.py"),
         os.path.join(tmp, "base.out"), os.path.join(tmp, "short.out")],
        capture_output=True, text=True)
    if proc.returncode == 0:
        failures.append("[keyset] CLI exit 0 on a key-set mismatch")
    else:
        print(f"PASS [keyset] missing=[e8] reported; CLI exit "
              f"{proc.returncode}")


def check_driver_pass_classes(failures):
    got = ab.driver_pass_classes()
    if got != {"expected", "verified", "no-answer"}:
        failures.append(f"[driver] PASS classes {got}")
    else:
        print(f"PASS [driver] PASS classes from corpus_driver.py: "
              f"{sorted(got)}")


def check_cli(tmp, failures):
    proc = subprocess.run(
        [sys.executable, os.path.join(HERE, "ab_records.py"),
         os.path.join(tmp, "base.out"), os.path.join(tmp, "new.out")],
        capture_output=True, text=True)
    out = proc.stdout
    needles = ["PASS->FAIL      1", "FAIL->PASS      1",
               "verified -> timeout",
               "t=28.1s -> t=30.0s 3 Logarithms/3.1.5 u (a+b log(c x^n))^p.mac"
               " e44"]
    missing = [n for n in needles if n not in out]
    if proc.returncode != 0 or missing:
        failures.append(f"[cli] exit {proc.returncode}, missing {missing}\n"
                        f"{out}{proc.stderr}")
    else:
        print("PASS [cli] report carries the table and the PASS->FAIL line")


def main():
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        check_parse(tmp, failures)
        check_duplicate(tmp, failures)
        check_table(tmp, failures)
        check_keyset(tmp, failures)
        check_driver_pass_classes(failures)
        check_cli(tmp, failures)
    for f in failures:
        print(f"FAIL {f}")
    print(f"Results: {6 - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
