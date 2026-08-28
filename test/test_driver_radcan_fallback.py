#!/usr/bin/env python3
"""Regression guard: the corpus driver's zero-test must carry a
radcan(rat()) fallback for when the numeric + ratsimp/factor stage
chain does not close (measured 2026-08-28, 5.50.0/SBCL).

Motivation: the redundant algebraic-generator zero-divisor bug
(`quotient' by 'zero' in ratsimp's gcd reduction — minimal hand-typed
repro: probes/maxima/probe-ratsimp-zero-divisor.mac) and sibling
rat-machinery crashes can defeat every ratsimp/factor/expand stage of
the zero-test while `radcan(rat(<zero-diff>))` closes the same diff.
Measured 2026-08-28 on currently-`unverified` entries (zc_triage over
the 2026-08-27 merged record): 1.1.3.8 e541/e543/e544 and 1.2.1.4
e764 self-diffs close under radcan(rat()).

The fallback is gated on a no-elliptic diff: radcan(rat()) crashes on
elliptic-family zero-diffs with `PTPTQUOTIENT: Polynomial quotient is
not exact' after burning 30-100 s (1.2.1.3 e455-e484 family,
measured 2026-08-28), and rat() cannot close an elliptic-carrying diff
anyway (the numeric stage owns those). The other measured crash
classes on unverified-entry zero-diffs are immediate and errcatched:
`expt: undefined: 0 to a negative exponent' (1.3.1 e147) and the
`quotient' by 'zero' zero-divisor bug via the fallback itself
(1.1.1.2 e1501).

The gate is `apply(freeof, [syms..., MR_de])` — the documented
variadic freeof (manual: freeof(x1, ..., xn, expr) == freeof(x1,
expr) and ... and freeof(xn, expr)) spliced over the symbol list.
The original list-first-arg form freeof([syms], expr) is not a
documented freeof call: it tests "does the LIST occur in expr" and
returned true on elliptic-carrying diffs (measured 2026-08-28:
freeof([elliptic_f], elliptic_f(x, -4)) = true) — a silently no-op
gate, fixed 2026-08-28.

Four checks:
  1. construction (no Maxima): zero_chain emits the gated, errcatched
     radcan(rat(MR_de)) fallback after the outer errcatch, short-
     circuits to 1 when the chain closed, and stays paren-balanced.
  2. gate semantics (Maxima): the apply(freeof, ...) gate is false on
     an elliptic-carrying expression and true on a plain one — the
     exact regression the no-op list form failed to catch.
  3. rescue (Maxima): measured entries with NON-elliptic zero-diffs
     that the stage chain cannot close classify as a PASS class
     (verified / expected) via the fallback.
  4. gate-blocks (Maxima): measured entries whose zero-diff carries
     elliptic functions classify `unverified` — the gate must keep
     the fallback off them (their chain crash is errcatched, the
     gated fallback returns 0).

Re-runnable:  python3 test/test_driver_radcan_fallback.py
Exits nonzero if any check fails.
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Non-elliptic zero-diffs the stage chain cannot close but
# radcan(rat()) does (measured 2026-08-28): the fallback must rescue
# them to a PASS class.
RESCUE_TARGETS = [
    ("1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p", 2588),
    ("1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p", 764),
]
# Zero-diffs carrying elliptic functions the stage chain crashes on
# (1.1.3.8 quartic family, measured 2026-08-28): the gate must keep
# the fallback off them -> `unverified`, not a PASS class.
GATED_TARGETS = [
    ("1.1.3.8 P(x) (c x)^m (a+b x^n)^p", 541),
    ("1.1.3.8 P(x) (c x)^m (a+b x^n)^p", 543),
    ("1.1.3.8 P(x) (c x)^m (a+b x^n)^p", 544),
]
GATE_SYMS = ("elliptic_f, elliptic_e, elliptic_pi, "
             "elliptic_ec, elliptic_eu, elliptic_kc")


def _load_driver():
    # Import the driver the same way canary.py does, with a benign argv
    # so its module-level default parsing is well-defined.
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
    """The zero_chain text must carry the gated errcatched fallback."""
    failures = []
    text = driver.zero_chain("MR_diff", "x")
    if "errcatch(radcan(rat(MR_de)))" not in text:
        failures.append("zero_chain lacks the errcatched "
                        "radcan(rat(MR_de)) fallback stage")
    gate = (f"apply(freeof, [{GATE_SYMS}, MR_de])")
    if gate not in text:
        failures.append("fallback not gated on the no-elliptic freeof "
                        f"(want {gate!r})")
    if "freeof([" in text:
        failures.append("zero_chain carries a list-first-arg freeof "
                        "call (not a documented freeof form; silently "
                        "no-op gate — measured 2026-08-28)")
    if "part(MR_zr, 1) = 1 then 1" not in text:
        failures.append("fallback not short-circuited: a chain that "
                        "closed must return 1 without running the "
                        "fallback")
    # Paren balance: the nested hand-built string miscounted twice
    # before (measured 2026-08-25); keep it checked.
    if text.count("(") != text.count(")"):
        failures.append(f"zero_chain text paren imbalance: "
                        f"{text.count('(')} ( vs {text.count(')')} )")
    return failures


def check_gate_semantics(driver):
    """The gate expression itself must discriminate elliptic from
    plain — the exact regression the no-op list form failed to
    catch (freeof([elliptic_f], elliptic_f(x, -4)) = true, measured
    2026-08-28)."""
    # Note: printf does not force a top-level `=` relation to a
    # boolean (measured 2026-08-28: printf("~a", 1 = 1) prints
    # `1 = 1` in 5.50.0), so pass the freeof result directly —
    # freeof returns the boolean itself.
    failures = []
    text = (f"GE: 1 + x*elliptic_f(x, -4)$\n"
            f"printf(true, \"== ELL: ~a~%\", "
            f"apply(freeof, [{GATE_SYMS}, GE]))$\n"
            f"GP: 1 + x*sqrt(2)$\n"
            f"printf(true, \"== PLAIN: ~a~%\", "
            f"apply(freeof, [{GATE_SYMS}, GP]))$\n")
    out, _timed_out = driver.maxima_run(text, 30)
    ell = plain = None
    for line in out.splitlines():
        ls = line.strip()
        if ls.startswith("== ELL:"):
            ell = ls.split()[-1]
        elif ls.startswith("== PLAIN:"):
            plain = ls.split()[-1]
    if ell != "false":
        failures.append(f"gate ADMITS an elliptic-carrying expression "
                        f"(freeof printed {ell!r}, want 'false')")
    if plain != "true":
        failures.append(f"gate BLOCKS a plain expression (freeof "
                        f"printed {plain!r}, want 'true')")
    return failures


def check_rescue(driver):
    """Non-elliptic crashing/non-closing zero-diffs must classify as
    a PASS class via the fallback."""
    failures = []
    for filt, entry_no in RESCUE_TARGETS:
        try:
            pf, cls, _dt, label, _out = _run_one(driver, filt, entry_no)
        except SystemExit as e:
            return [f"cannot resolve {filt} e{entry_no}: {e}"]
        if cls not in driver.PASS_CLASSES:
            failures.append(f"{label} classified {cls!r}, expected a PASS "
                            f"class (unverified before the fallback)")
    return failures


def check_gate_blocks(driver):
    """Elliptic-carrying zero-diffs must stay out of the fallback:
    `unverified` (chain crash errcatched, gated fallback returns 0),
    not a PASS class."""
    failures = []
    for filt, entry_no in GATED_TARGETS:
        try:
            pf, cls, _dt, label, _out = _run_one(driver, filt, entry_no)
        except SystemExit as e:
            return [f"cannot resolve {filt} e{entry_no}: {e}"]
        if cls != "unverified":
            failures.append(f"{label} classified {cls!r}, expected "
                            f"'unverified' (elliptic diff must be "
                            f"gated out of the fallback)")
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
    n_passed = 0

    cf = check_construction(driver)
    all_fail += cf
    for msg in cf:
        print(f"FAIL [construction] {msg}")
    if not cf:
        n_passed += 1
        print("PASS [construction] zero_chain carries the gated "
              "errcatched radcan(rat()) fallback")

    checks = [("gate-semantics", check_gate_semantics,
               "the apply(freeof, ...) gate discriminates elliptic "
               "from plain expressions"),
              ("rescue", check_rescue,
               "the non-elliptic measured entries now classify as "
               "PASS classes via the fallback"),
              ("gate-blocks", check_gate_blocks,
               "the elliptic-carrying measured entries stay "
               "`unverified` (gated out of the fallback)")]
    for name, fn, okmsg in checks:
        try:
            fails = fn(driver)
        except Exception as e:  # noqa: BLE001 - surface any harness break
            fails = [f"{name} check crashed: {e!r}"]
        all_fail += fails
        for msg in fails:
            print(f"FAIL [{name}] {msg}")
        if not fails:
            n_passed += 1
            print(f"PASS [{name}] {okmsg}")

    total = 1 + len(checks)
    print(f"\nResults: {n_passed} passed, {total - n_passed} failed")
    return 1 if all_fail else 0


if __name__ == "__main__":
    sys.exit(main())
