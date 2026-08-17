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

## Evidence

