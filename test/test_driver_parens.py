#!/usr/bin/env python3
"""Regression guard: the corpus driver must parenthesize the inlined
corpus expected answer in the expected-answer zero-test.

Root cause guarded (2026-08-24): build_text built the expected zero-test
as `diff(mr_r - <e_text>, x)` by inlining the expected text WITHOUT
parentheses. When the expected answer is a SUM `A + B`, that parses as
`mr_r - A + B` (every term after the first has its sign flipped), so a
CORRECT antiderivative fails the zero-test and the entry is misclassified
`unverified`. Measured on 1.3.2 e1: `mr_r - <e>` residual nonzero,
`mr_r - (<e>)` residual zero.

Two checks:
  1. construction (no Maxima): build_text emits `diff(mr_r - (<e_text>), x)`
     for both the primary and secondary expected chains.
  2. behavior (Maxima): the corpus entry that was broken, 1.3.2 e1, now
     classifies as a PASS class (expected / verified), not `unverified`.

Re-runnable:  python3 test/test_driver_parens.py
Exits nonzero if any check fails.
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _load_driver():
    # Import the driver the same way canary.py does, with a benign argv so
    # its module-level default parsing is well-defined.
    real = sys.argv[:]
    sys.argv = ["corpus_class1_driver.py", "1 Algebraic functions/", "1", "30"]
    try:
        spec = importlib.util.spec_from_file_location(
            "driver", os.path.join(ROOT, "test", "corpus_class1_driver.py"))
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.argv = real


def check_construction(driver):
    """build_text must wrap the inlined expected text in parentheses."""
    failures = []
    # A SUM-valued expected answer is the trigger: without parens the second
    # term's sign flips. Use distinct symbols so the string checks are exact.
    f_text, var_text = "1 + x", "x"
    e_sum = "u_(x) + v_(x)"
    e2_sum = "p_(x) + q_(x)"

    t1 = driver.build_text(f_text, var_text, e_sum, None)
    if f"diff(mr_r - ({e_sum}), {var_text})" not in t1:
        failures.append(f"primary expected chain not parenthesized "
                        f"(want `diff(mr_r - ({e_sum}), {var_text})`)")
    elif f"diff(mr_r - {e_sum}, {var_text})" in t1.replace(
            f"diff(mr_r - ({e_sum}), {var_text})", ""):
        failures.append("primary expected chain still has the "
                        "unparenthesized `mr_r - <e>` form")

    t2 = driver.build_text(f_text, var_text, e_sum, e2_sum)
    if f"diff(mr_r - ({e2_sum}), {var_text})" not in t2:
        failures.append(f"secondary expected chain not parenthesized "
                        f"(want `diff(mr_r - ({e2_sum}), {var_text})`)")
    return failures


def check_behavior(driver):
    """The corpus entry that was misclassified must now PASS."""
    failures = []
    # 1.3.2 e1: integrand 1/((2^(2/3)+x)*sqrt(1+x^3)); its expected answer
    # is a SUM (a tan^-1 term + an elliptic_f term) — the exact trigger.
    try:
        pf, cls, _dt, label, _out = _run_one(driver, "1.3.2 Algebraic functions", 1)
    except SystemExit as e:
        return [f"cannot resolve 1.3.2 e1: {e}"]
    if cls not in driver.PASS_CLASSES:
        failures.append(f"{label} classified {cls!r}, expected a PASS class "
                        f"(got misclassified `unverified` before the fix)")
    return failures


def _run_one(driver, filter, entry_no):
    files = driver.file_list()
    for path, rel in files:
        if filter in rel:
            entries, line_nos = driver.extract_entries(path)
            if 1 <= entry_no <= len(entries):
                els = driver.split_elements(entries[entry_no - 1][1:-1])
                f_text, var_text, _s, e_text = els[0], els[1], els[2], els[3]
                e_text2 = els[4] if len(els) == 5 else None
                label = f"{rel} e{entry_no} L{line_nos[entry_no - 1]}"
                out, timed_out = driver.maxima_run(
                    driver.build_text(f_text, var_text, e_text, e_text2),
                    45)
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
                pf = "PASS" if cls in driver.PASS_CLASSES else "FAIL"
                return pf, cls, 0.0, label, out
    raise SystemExit(f"target not found: {filter!r} e{entry_no}")


def main():
    driver = _load_driver()
    all_fail = []

    cf = check_construction(driver)
    if cf:
        all_fail += cf
    for msg in cf:
        print(f"FAIL [construction] {msg}")
    if not cf:
        print("PASS [construction] build_text parenthesizes both expected "
              "zero-chains")

    # Behavior check needs Maxima; if it is unavailable, report it as a
    # failure (the guard must not silently pass).
    try:
        bf = check_behavior(driver)
    except Exception as e:  # noqa: BLE001 - surface any harness break
        bf = [f"behavior check crashed: {e!r}"]
    for msg in bf:
        print(f"FAIL [behavior] {msg}")
    if not bf:
        print("PASS [behavior] 1.3.2 e1 now classifies as a PASS class")

    n_passed = (1 if not cf else 0) + (1 if not bf else 0)
    print(f"\nResults: {n_passed} passed, {2 - n_passed} failed")
    return 1 if all_fail else 0


if __name__ == "__main__":
    sys.exit(main())
