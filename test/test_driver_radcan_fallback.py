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
  3. rescue (Maxima): a zero-diff the stage chain cannot close is
     closed by zero_chain WITH the fallback and not closed WITHOUT
     it. Both arms are the same zero_chain, through its `fallback`
     parameter, so the check proves the fallback is the stage that
     closes it rather than assuming it.
  4. gate-blocks (Maxima): the SAME zero-diff multiplied by an
     elliptic factor is left unclosed — while ungated
     radcan(rat(.)) still returns 0 on it. That last clause is what
     makes this a gate test: the fallback WOULD close the diff, and
     only the elliptic gate stops it.

WITNESSES — 2026-09-21. Checks 3 and 4 used to run two measured CORPUS
entries end to end and read the driver's classification. That coupled
them to the rule set, which is not what they guard: `deferred` and
`contains-noun` are decided BEFORE the zero chain is built
(corpus_driver.build_text), so an entry that stops reaching the
zero-test silently stops exercising the fallback. Commit 29d237a
(2026-09-18, the faithful pair, class-1 +3,310) did exactly that —
1.2.1.4 e764 verified -> deferred, 1.1.3.8 e541/e543/e544 unverified ->
contains-noun — and the guard went red for weeks while the fallback it
guards was untouched (`.scratch/corpus-harness/issues/03`).

The witnesses are therefore synthetic and frozen, and depend on neither
the rule set nor the corpus:

    rescue      %e^(n*log(x)) - x^n
    gate-blocks elliptic_f(x, 1/2)*(%e^(n*log(x)) - x^n)

Both are identically zero. `n` is deliberately NOT one of the zero
chain's sweep parameters (a b c d e f g h A B C D p), so the leading
numeric stage evaluates to a float NOUN and declines — which is the
only way the symbolic stages, and then the fallback, are ever reached.
Measured 2026-09-21 on branch_5_50_base_84_g4204fb669 / SBCL 2.6.7:
the rescue witness is nofb=0, withfb=1, gate=true; the gated witness is
nofb=0, withfb=0, gate=false, and ungated radcan(rat(.)) = 0.

Re-runnable:  python3 test/test_driver_radcan_fallback.py
Exits nonzero if any check fails.
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# A zero-diff no ratsimp/factor stage closes and radcan(rat()) does.
# `n` is not a sweep parameter, so the leading numeric stage declines
# (see the module docstring); without that the numeric stage would
# close any true zero and the fallback would never be reached.
RESCUE_WITNESS = "%e^(n*log(x)) - x^n"
# The same zero-diff behind an elliptic factor: the gate must keep the
# fallback off it EVEN THOUGH radcan(rat()) would return 0.
GATED_WITNESS = "elliptic_f(x, 1/2)*(%e^(n*log(x)) - x^n)"
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


def _chain_probe(driver, witness):
    """(nofb, withfb, gate, ungated_radcan) for WITNESS, in one Maxima."""
    no_fb = driver.zero_chain(witness, "x", fallback=False)
    with_fb = driver.zero_chain(witness, "x", fallback=True)
    text = ("MR_N: (" + no_fb + ")$\n"
            "MR_W: (" + with_fb + ")$\n"
            f"MR_G: apply(freeof, [{GATE_SYMS}, ({witness})])$\n"
            f"MR_R: errcatch(radcan(rat({witness})))$\n"
            'disp(concat("RES ", string(MR_N), " ", string(MR_W), " ",\n'
            '            string(MR_G), " ",\n'
            '            string(if MR_R = [] then CRASH else part(MR_R, 1))))$\n')
    out, timed_out = driver.maxima_run(text, 120)
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) == 5 and parts[0] == "RES":
            return tuple(parts[1:])
    return ("timeout" if timed_out else "no-result",) * 4


def check_rescue(driver):
    """The fallback must close a zero-diff the stage chain cannot.

    Both arms are the SAME zero_chain, switched by its `fallback`
    parameter, so a witness that the chain closes on its own can never
    pass this check vacuously — which is how the previous, corpus-
    driven version of it rotted unnoticed."""
    failures = []
    nofb, withfb, gate, _rad = _chain_probe(driver, RESCUE_WITNESS)
    if gate != "true":
        failures.append(f"the rescue witness carries a gated symbol "
                        f"(gate printed {gate!r}); it cannot reach the "
                        "fallback at all, so the check would be vacuous")
    if nofb != "0":
        failures.append(f"zero_chain(fallback=False) printed {nofb!r}, want "
                        "'0' — the stage chain now closes the witness on "
                        "its own, so the witness no longer exercises the "
                        "fallback and must be replaced")
    if withfb != "1":
        failures.append(f"zero_chain(fallback=True) printed {withfb!r}, want "
                        "'1' — the radcan(rat()) fallback no longer closes "
                        "a diff that nothing else closes")
    return failures


def check_gate_blocks(driver):
    """The elliptic gate must keep the fallback off an elliptic-carrying
    diff — and the point is that radcan(rat()) WOULD have closed it.

    Without the last assertion this check passes on any diff the
    fallback merely fails to close, which says nothing about the gate."""
    failures = []
    nofb, withfb, gate, rad = _chain_probe(driver, GATED_WITNESS)
    if gate != "false":
        failures.append(f"the gate ADMITS the elliptic witness (gate "
                        f"printed {gate!r}, want 'false')")
    if rad != "0":
        failures.append(f"ungated radcan(rat()) printed {rad!r}, want '0' — "
                        "the witness is no longer a diff the fallback would "
                        "close, so blocking it proves nothing about the gate")
    if nofb != "0":
        failures.append(f"zero_chain(fallback=False) printed {nofb!r}, want "
                        "'0' — the stage chain closes the witness, so the "
                        "fallback is never consulted and the check is vacuous")
    if withfb != "0":
        failures.append(f"zero_chain(fallback=True) printed {withfb!r}, want "
                        "'0' — the gate let radcan(rat()) run on an "
                        "elliptic-carrying diff")
    return failures


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
               "the fallback closes a zero-diff the stage chain "
               "alone does not"),
              ("gate-blocks", check_gate_blocks,
               "the gate keeps the fallback off an elliptic diff "
               "radcan(rat()) would have closed")]
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
