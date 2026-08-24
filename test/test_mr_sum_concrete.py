#!/usr/bin/env python3
"""Regression guard: mr_sum must concretize constant-bounded sums.

Root cause guarded (2026-08-25): the generated even/odd-split rules
(1.2.2.5 r3 family and siblings) emit mr_sum(<summand>, k, lo, hi) where
the summand contains a TOTAL package function of the summation index,
e.g. %mr_coeff(Pq, x, 2*k)*x^(2*k). Maxima evaluates function arguments
eagerly, so the summand is evaluated ONCE with k free before mr_sum sees
it; %mr_coeff with a symbolic exponent returns 0 (it is total), so every
such sum is born as the contentless noun mr_sum[0, k, lo, hi]. The
contentless noun still passes the %mr_polyQ guards, so the same rule
family re-fires on it, drains the bounds toward 0, and the final answer
carries a degenerate mr_sum[0, k, 0, 0] — the zero-tests cannot close and
the corpus entries are misclassified `unverified` (measured 2026-08-25:
1.2.2.5 e44/e94, 1.2.2.6 e123; same cascade times out 1.2.2.7 e1/e17).
Mathematica's finite Sum evaluates the summand for each integer value of
the index, which is what the corpus expected answers assume.

Fix under test: the generator wraps every non-identifier summand in
lambda([<var>], <summand>) so the summand survives unevaluated, and
mr_sum concretizes over numeric bounds — per integer i, apply(lambda,
[i]) for a lambda summand, ev(subst(i, var, ev(fun))) for an atom
summand (the 1.1.3.1 r13 Module-local-u shape, whose value carries the
index; a bare lambda body of one symbol does NOT get the index bound
into its value — measured 2026-08-25, probe mech_decisive D1). Symbolic
bounds keep the noun.

Seams (the project's established test surfaces):
  1. construction (no Maxima): every mr_sum( call in the generated
     rules/class1/*.mac is either lambda-wrapped or a bare identifier
     (the u-locals of the 1.1.3.1/1.1.3.2 r13 family).
  2. behavior (Maxima, package API): the package function mr_sum
     concretizes as specified (semantics SEM1-SEM7).
  3. behavior (Maxima, corpus driver): the corpus entry that was
     misclassified, 1.2.2.5 e44, now classifies as a PASS class.

Re-runnable:  python3 test/test_mr_sum_concrete.py
Exits nonzero if any check fails.
"""

import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RULES = os.path.join(ROOT, "rules", "class1")

SUM_CALL = re.compile(r"mr_sum\(")
LEGAL_FORM = re.compile(r"mr_sum\((?:lambda\(\[|\w+,)")


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


def check_sweep():
    """Every generated mr_sum( call is lambda-wrapped or a bare identifier."""
    failures = []
    files = sorted(f for f in os.listdir(RULES) if f.endswith(".mac"))
    for fn in files:
        with open(os.path.join(RULES, fn), encoding="utf-8") as fh:
            for ln, line in enumerate(fh, 1):
                for m in SUM_CALL.finditer(line):
                    if not LEGAL_FORM.match(line, m.start()):
                        snippet = line[m.start():m.start() + 60].strip()
                        failures.append(f"{fn}:{ln} unwrapped mr_sum summand: "
                                        f"{snippet!r}")
    return failures


SEMANTICS_MAC = """
/* SEM batch: the public mr_sum contract (package preloaded). */
Pq : d + e*x + f*x^2 + g*x^3$
R1 : mr_sum(lambda([k], %mr_coeff(Pq, x, 2*k)*x^(2*k)), k, 0, 3/2)$
disp(concat("SEM1 ", string(is(ratsimp(R1 - (d + f*x^2)) = 0))))$
R2 : x*mr_sum(lambda([k], %mr_coeff(Pq, x, 2*k+1)*x^(2*k)), k, 0, 1)$
disp(concat("SEM2 ", string(is(ratsimp(R2 - (e*x + g*x^3)) = 0))))$
R3 : mr_sum(lambda([k], k^2), k, 0, -1/2)$
disp(concat("SEM3 ", string(is(ratsimp(R3 - 0) = 0))))$
R4 : mr_sum(lambda([k], k^2), k, 0, n/2)$
disp(concat("SEM4 ", string(is(string(op(R4)) = "mr_sum"))))$
R5 : mr_sum(zq, k, 1, 3)$
disp(concat("SEM5 ", string(is(ratsimp(R5 - 3*zq) = 0))))$
R6 : block([u, kk], u : (2*kk - 1)*x, mr_sum(u, kk, 1, 2))$
disp(concat("SEM6 ", string(is(ratsimp(R6 - 4*x) = 0))))$
R7 : mr_sum(lambda([j], x^j*mr_sum(lambda([k], (k+1)*j), k, 0, 1)), j, 0, 1)$
disp(concat("SEM7 ", string(is(ratsimp(R7 - 3*x) = 0))))$
"""


def check_semantics(driver):
    """mr_sum concretizes per the measured contract (SEM1-SEM7 all true)."""
    out, timed_out = driver.maxima_run(SEMANTICS_MAC, 120)
    if timed_out:
        return ["semantics batch timed out (120s)"]
    got = {}
    for line in out.splitlines():
        line = line.strip()
        m = re.fullmatch(r"SEM([1-7]) (true|false|unknown)", line)
        if m:
            got[m.group(1)] = m.group(2)
    failures = []
    for n in "1234567":
        v = got.get(n)
        if v != "true":
            failures.append(f"SEM{n} is {v!r}, expected true")
    return failures


def _run_one(driver, filtf, entry_no):
    files = driver.file_list()
    for path, rel in files:
        if filtf in rel:
            entries, line_nos = driver.extract_entries(path)
            if 1 <= entry_no <= len(entries):
                els = driver.split_elements(entries[entry_no - 1][1:-1])
                f_text, var_text, _s, e_text = els[0], els[1], els[2], els[3]
                e_text2 = els[4] if len(els) == 5 else None
                label = f"{rel} e{entry_no} L{line_nos[entry_no - 1]}"
                out, timed_out = driver.maxima_run(
                    driver.build_text(f_text, var_text, e_text, e_text2), 45)
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
                return cls, label
    raise SystemExit(f"target not found: {filtf!r} e{entry_no}")


def check_behavior(driver):
    """The corpus entry that was misclassified must now PASS."""
    cls, label = _run_one(driver, "1.2.2.5", 44)
    if cls not in driver.PASS_CLASSES:
        return [f"{label} classified {cls!r}, expected a PASS class "
                f"(got `unverified` with the degenerate mr_sum[0,k,0,0] "
                f"before the fix)"]
    return []


def main():
    driver = _load_driver()
    all_fail = []

    sf = check_sweep()
    for msg in sf:
        print(f"FAIL [sweep] {msg}")
    if sf:
        all_fail += sf
    else:
        print("PASS [sweep] every generated mr_sum call is lambda-wrapped "
              "or a bare identifier")

    try:
        mf = check_semantics(driver)
    except Exception as e:  # noqa: BLE001 - surface any harness break
        mf = [f"semantics check crashed: {e!r}"]
    for msg in mf:
        print(f"FAIL [semantics] {msg}")
    if mf:
        all_fail += mf
    else:
        print("PASS [semantics] SEM1-SEM7 all true")

    try:
        bf = check_behavior(driver)
    except Exception as e:  # noqa: BLE001 - surface any harness break
        bf = [f"behavior check crashed: {e!r}"]
    for msg in bf:
        print(f"FAIL [behavior] {msg}")
    if bf:
        all_fail += bf
    else:
        print("PASS [behavior] 1.2.2.5 e44 classifies as a PASS class")

    n_passed = 3 - len([1 for _ in (sf, mf, bf) if _])
    print(f"\nResults: {n_passed} passed, {3 - n_passed} failed")
    return 1 if all_fail else 0


if __name__ == "__main__":
    sys.exit(main())
