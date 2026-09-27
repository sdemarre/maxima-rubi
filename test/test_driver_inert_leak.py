#!/usr/bin/env python3
"""Regression guard: an answer that carries an inert trig head is an ERROR.

Motivation (inert-trig substrate design 3.1 invariant, 3.4; Task 10). The
bridge rule (4.1.0.1 r1) rewrites a trig/hyperbolic integrand into the six
inert heads %mr_isin %mr_icos %mr_itan %mr_icot %mr_isec %mr_icsc, and a
section-4 rule must ACTIVATE them again before it answers. An inert head is
not a function Maxima knows: diff() leaves it alone, so an answer that still
carries one can never verify, and it used to land silently in a FAIL class
-- `deferred` when rubi's whole answer is the unintegrable noun around the
inert integrand, `contains-noun` or `unverified` when the head sits inside.
MEASURED 2026-09-21 (Task 10 probe, full mr_load_all table):
rubi(1/(a+b*cos(x)), x) answered 'unintegrable[1/(b*%mr_isin(x+%pi/2)+a),x]
before the Weierstrass record was ported. That is a package defect, not a
coverage gap, and it must fail LOUDLY.

The driver therefore classifies such an answer `error` -- a class the
mergers already know -- and names the leaked heads. NOT a new class: a new
class would break the mergers' agreement with the driver (KNOWN_CLASSES).

Five checks. The Maxima checks inject a SYNTHETIC answer in place of the
rubi call, so they depend on neither the rule set nor the corpus (the
test_driver_radcan_fallback lesson: corpus-driven witnesses rot).

  1. [no-new-class] KNOWN_CLASSES is exactly the nine classes it was.
  2. [top-level-leak] a leaked answer that is itself the unintegrable noun
     (was `deferred`) classifies `error`, and the driver names %mr_isin.
  3. [interior-leak] a leaked head inside an otherwise ordinary answer
     (was `unverified`) classifies `error`, and the driver names %mr_icos.
  4. [unintegrable-expected] the leak test also runs in the branch for an
     entry whose expected answer is Unintegrable (was `no-answer`).
  5. [control] a clean, correct answer still classifies `verified`.

Re-runnable:  python3 test/test_driver_inert_leak.py
Exits nonzero if any check fails.
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

NINE = {"expected", "verified", "unverified", "contains-noun", "no-answer",
        "deferred", "unexpected", "error", "timeout"}


def _load_driver():
    real = sys.argv[:]
    sys.argv = ["corpus_driver.py", "ZZ no such section ZZ", "1", "30"]
    try:
        spec = importlib.util.spec_from_file_location(
            "driver", os.path.join(HERE, "corpus_driver.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.argv = real


def _run(driver, f_text, answer, e_text):
    """(class, leaked heads) of a driver entry text whose rubi call is
    replaced by the synthetic ANSWER."""
    text = driver.build_text(f_text, "x", e_text)
    call = "mr_r: rubi(mr_f, x)$"
    if text.count(call) != 1:
        return "no-call-line", []
    text = text.replace(call, f"mr_r: {answer}$")
    out, timed_out = driver.maxima_run(text, 120)
    cls, _caps = driver.classify_output(out, timed_out)
    heads = (driver.inert_leak_heads(out)
             if hasattr(driver, "inert_leak_heads") else None)
    return cls, heads


def main():
    driver = _load_driver()
    failures = []

    # --- 1: no new class.
    if set(driver.KNOWN_CLASSES) != NINE:
        failures.append(f"[no-new-class] KNOWN_CLASSES changed: "
                        f"{sorted(set(driver.KNOWN_CLASSES) ^ NINE)}")
    else:
        print("PASS [no-new-class] KNOWN_CLASSES is the nine classes")

    cases = [
        ("top-level-leak", "sin(x)^2", "'unintegrable(%mr_isin(x)^2, x)",
         "x/2 - sin(2*x)/4", "error", ["%mr_isin"]),
        ("interior-leak", "sin(x)^2", "x/2 - %mr_icos(2*x)/4",
         "x/2 - sin(2*x)/4", "error", ["%mr_icos"]),
        ("unintegrable-expected", "f(x)", "'unintegrable(%mr_itan(x)*f(x), x)",
         "Unintegrable[f(x), x]", "error", ["%mr_itan"]),
        ("control", "sin(x)", "-cos(x)", "-cos(x)", "verified", []),
    ]
    for name, f_text, answer, e_text, want_cls, want_heads in cases:
        cls, heads = _run(driver, f_text, answer, e_text)
        if cls != want_cls:
            failures.append(f"[{name}] answer {answer!r} classified {cls!r}, "
                            f"want {want_cls!r}")
        elif heads != want_heads:
            failures.append(f"[{name}] leaked heads named {heads!r}, "
                            f"want {want_heads!r}")
        else:
            print(f"PASS [{name}] {answer!r} -> {cls}"
                  + (f", names {', '.join(heads)}" if heads else ""))

    for f in failures:
        print(f"FAIL {f}")
    print(f"Results: {5 - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
