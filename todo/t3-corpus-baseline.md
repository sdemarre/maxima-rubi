# T3 — Corpus and Maxima baseline

Status: open
Doc: `docs/corpus-baseline.md`
Depends on: — (its sample run starts in parallel with T1; the full
algebraic-section baseline waits for the timeout/format design it establishes)

## Questions to answer

1. The `MaximaSyntaxTestSuite` format: file layout, expected-answer
   convention, how "no elementary answer" is marked, what normalization
   comparison is allowed. Clone the repo, pin the commit in `todo/TODO.md`.
2. Baseline of today's `integrate` over the algebraic section:
   sample run first (time-bounded), then the section with an
   established per-integral timeout and an overall wall-clock cap.
   Per-integral timing; outcome class: expected-match / verified-by-derivative
   / no-answer / timeout.
3. Verification primitives: which Maxima operations (`diff`, `ratsimp`,
   `together`, `expand`, `factor`, …) suffice for
   "derivative of candidate equals the integrand".
4. The gap profile: what milestone 1's acceptance set is, and what
   fraction `integrate` already passes today (the uplift baseline).
5. `sympy_rubi` cross-check: where a corpus expected-answer is in
   doubt or its normalisation unclear, its answer is an independent
   oracle.

## Evidence

- 2026-08-17: cloned
  `https://github.com/RuleBasedIntegration/MaximaSyntaxTestSuite`
  into `reference/maxima-syntax-test-suite`, pinned commit
  `60295e21c571ca210ecfbb695f4af99947454adf` (2018-10-25, "Update
  test suite"). Pin recorded in `todo/TODO.md`.
- 2026-08-17 (branch_5_49_base_796_g60186bb22_dirty, 2026-07-28,
  SBCL 2.6.7): **load sweep** — `probes/corpus/probe-corpus-load-sweep.py`
  (→ `.out`), one fresh `maxima -b` per file: **205 of 215 files load;
  10 are FATAL** (a parse-time constant fold kills the whole batch load;
  bisection located exactly one fatal entry per file, e.g. 1.3.1 entry
  136 at line 199). Root cause measured: this build folds **`(-1)^(1/3)`
  → `-1`** and `(-1)^(2/3)` → `1` (real-root convention), so Rubi's
  cubic-factor denominators like `(1+(-1)^(1/3))^2` fold to `0` and the
  entry's parse dies with `expt: undefined: 0 to a negative exponent`.
  29 of 215 files contain `(-1)^` text. Totals over loadable files:
  67038 entries, 3047 `Unintegrable` noun expectations, 355
  `CannotIntegrate`, 124 bad step counts (non-integer or negative).
- 2026-08-17: **quoted lists do not protect parse-time folding.**
  `lst: '[1/0, x^(-2)]` still evaluates constant subexpressions (symbol
  elements stay inert). `1/0` alone is fatal in this build. The corpus
  only loads because its fatal subexpressions are few — and per-integral
  *text paste* (never `load`) isolates even those.
- 2026-08-17: **noun-integrate is a list-structured object**: `listp`
  false, `length(r)=2`, `part(r,1)=f`, `part(r,2)=x`; carries no
  `integrate` symbol (so `freeof(integrate, r)` does NOT detect it);
  `isatom(r)` on it stays *unevaluated* (freezes conditions), `atom(r)`
  → false is the safe guard. Detection:
  `is(length(r)=2) and is(part(r,1)=f) and is(part(r,2)=x)`.
- 2026-08-17: **`=` no longer auto-evaluates** a non-simplifying
  equation to true/false (`2 = 2` stays an equation); every boolean
  needs `is(...)`. `stringmatch`, `together`, `simplify` unbound.
- 2026-08-17: **`integrate` prompts** ("Is … positive or negative?"
  from `asksign`, "Is … equal to …?" from `askequal`) on a query
  stream, not stdin (piped stdin never reaches it). Fix: preload
  `batch_answers_from_file: true` (must be set **before** the batch
  starts; plain `-b` defaults false, `--batch-string`/`run_testsuite`
  default true) plus an answer pool in the batch file — `pos` lines
  for sign prompts, `no` for equality (generic assumptions). Manual:
  `? batch_answers_from_file`. Source: `~/src/external/maxima/src/`
  (compar.lisp `ensure-sign`/`$askequal`, macsys.lisp `retrieve`,
  mload.lisp:282).
- 2026-08-17: **corpus entries may be 5-element**
  `[integrand, x, steps, expected1, expected2]` — two alternative
  expected forms (e.g. 1.2.2.2 L18); the harness must accept either.
- 2026-08-17: **algebraic-section sample baseline** —
  `probes/corpus/probe-integrate-sample.py` (→ `.out`), 199 integrals
  (first 5 per class-1 file, per-integral subprocess, 30 s cap,
  zero-chain ratsimp → ratsimp∘expand → factor → ratsimp∘factor):
  expected 12, verified 106, unverified 23, no-answer 27, timeout 31,
  error 0. Wall 969 s here (this box runs Maxima startup ~0.1 s);
  the 30 s cap was arbitrary — a tuned cap is a T5 decision.
  "verified" = derivative matches the integrand within the chain,
  corpus expectation differs beyond it (branch/cosmetic); the
  unverified 23 are the chain-strength gap (T3-Q3).

