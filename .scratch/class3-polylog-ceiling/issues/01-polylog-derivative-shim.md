# polylog derivative shim — close the two-sided-expected-chain ceiling (go number: 638)

Status: needs-triage
Type: research (+ possible port)
Filed: 2026-08-30 (milestone-3 close — the M2-deferred
polylog/AppellF1 structural-ceiling decision, decided with the
class-3 numbers: the ceiling does NOT stand as-is)

## The measured basis (all class-3, build 2026-08-29 17:58:20 / SBCL
2.6.7; sources: `docs/corpus-class3-baseline-uplift.md` §2/§5,
`.superpowers/sdd/task-10-report.md` §8,
`probes/corpus/03-class3-answer-heads.out`)

- The class-3 polylog mass: **1,195 of 3,085 entries (38.7 %) /
  2,793 `polylog(` occurrences** (per file 3.1.4 187, 3.1.5 179,
  3.2.1 91, 3.2.2 106, 3.2.3 65, 3.3 243, 3.4 237, 3.5 87; 3.1.2 0)
  against the 17 PolyLog-emitting rules.
- Measured mechanism: `diff(polylog(·,·),·)` and
  `polylog(·,numeric)` are **nouns** in this build (probed
  2026-08-29: `diff(polylog(2,x),x)` stays a noun;
  `polylog(2,0.5)` / `polylog(3,0.5)` stay nouns). A polylog entry
  can therefore PASS only through the **two-sided expected chain on
  a form-identical answer** (identical polylog terms cancel before
  the diff — `diff(polylog(2,-x) - polylog(2,-x), x) = 0`
  measured); the self-diff and numeric stages cannot close.
- The measured split of the 1,195 (Task-10 report §8): **PASS 440
  (36.8 %: verified 379, expected 59, no-answer 2) | deferred 532,
  unverified 106, timeout 103, contains-noun 8, error 6** vs the
  record-wide PASS 56.3 %.
- **The unverified+deferred polylog mass is 638 — 53.4 % of the
  mass, 47.3 % of the class-3 FAIL mass of 1,349. That is the go
  number for this ticket.**

## Why the ceiling does not stand (the decision, recorded)

The 638 is not a verification gap a stronger zero chain can close —
the noun diff/numeric property is structural, so no chain-order or
fallback change reaches an entry whose package answer is not
form-identical to the corpus expected. It IS a
derivative-simplification gap: the harness cannot differentiate
`polylog(s, z)` at all, so a correct-but-rewritten package answer
(legitimate antiderivative, different form) can never verify. A
derivative shim converts the "form-identical or nothing" ceiling
into "any antiderivative whose polylog terms match under the
recursion".

## Shim candidates (to be triaged, not yet decided)

- **Order 2:** `d/dz polylog(2, z) = -log(1 - z)/z` — elementary;
  a two-sided rewrite of `diff(polylog(2, f(z)), z)` to
  `-log(1 - f(z)) * f'(z) / f(z)` (chain-rule form) would close the
  order-2 mass (2,081 of the 2,793 occurrences are order 2 —
  `probes/corpus/03-class3-answer-heads.out` order distribution:
  2 → 2081, 3 → 518, 4 → 138, 5 → 21, 6 → 1, 1 → 1, symbolic → 33).
- **General recursion:** `d/dz polylog(s, z) = polylog(s-1, z)/z` —
  lowers the order each differentiation; a terminal case is needed
  (order 2 → elementary, or order 1 → `log(1/(1-z))` derivative
  `1/(z(1-z))`).
- **Numeric fallback for the residual:** `polylog(s, numeric)` is
  also a noun — a numeric-evaluation shim (e.g. series or
  `sum(z^k/k^s)`-based) would let the chain's numeric stage close
  non-form-identical answers too; the cost/branching behavior of
  `ev`-level numeric simplification in this build is unmeasured.

## Open question — WHERE the shim lives

Two candidate loci, triage must choose (each has a different
blast radius):

1. **The driver's zero chain** (`test/corpus_driver.py`
   `zero_chain()`): a Maxima-level diff-simplification step
   (errcatched, like the radcan fallback) that rewrites
   `diff(polylog(·,·),·)` before the stage ladder. Local to the
   harness; the package's own `diff` behavior is untouched; but the
   shim then exists only in the harness — `rubi()` answers
   containing polylog remain undifferentiable for end users, and
   every future class-N run inherits the driver dependency.
2. **A Maxima-level simplification** (in the package or the build's
   `diff` handling): closes the gap for everyone, but is a
   core/build change — outside this repo's port scope unless the
   triage decides the gap is a Maxima bug worth a report; a
   package-level `diff` override is not idiomatic Maxima.

## Interactions (measured, must be in the triage)

- **OOM mass:** all 6 package-run `error`s and 8 of the 9 re-check
  OOMs sit in the polylog families (Task-10 §8; the 13 OOMs blow up
  in the driver's zero-chain VERIFICATION stage — see
  `.scratch/class3-verification-stage-oops/issues/01`). A shim that
  makes polylog diffs close EARLIER in the chain may shrink the
  blowup (the diff never reaches the heavy stages); one that adds a
  stage may enlarge it. The OOM ticket and this ticket should be
  triaged together.
- **Still-timeout concentrations:** 96 confirmed non-terminators at
  100 s, by family 3.3 44 / 3.1.5 22 / 3.1.4 12 / 3.4 5 / 3.2.1 5 /
  3.5 5 / 3.2.3 3 — the polylog-heavy files; a shim that turns
  some `unverified` into `verified` changes the timeout set's
  composition on re-run.
- **Later classes:** 8.8 Polylogarithm function is the class-8
  ticket's known interaction — the shim's locus decision should be
  made before class 8's Step 8 (normalization) so 8.8 runs on the
  final harness. Class 4 (4.7 Miscellaneous) carries
  trig-integral expected texts that may exercise the same
  special-function verification gap.

## Acceptance (for the research phase)

- A measured probe (committed under `probes/`, re-runnable,
  build-stamped) of the shim's closure rate on a sample of the 638
  (at minimum the order-2 subset of the unverified 106), with the
  locus decision (driver zero-chain vs Maxima-level) recorded with
  the measured basis; a port ticket (or a wontfix with the ceiling
  re-asserted) filed from that.
- Whatever the outcome: the class-3 record's polylog numbers
  (1,195 / 638 / the split above) are the before-state and must be
  cited in the after-state.

## Comments
