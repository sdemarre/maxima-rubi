# Numeric check: substitute exact rationals and evaluate in bigfloat, not plain floats

Status: needs-triage
Type: idea (checker change; verdict-affecting, so A/B-gated)
Filed: 2026-09-29 (user request: record as an idea, not implement)

## Today

`mr_numeric_point` (`test/mr_verify.mac`) substitutes FLOAT parameters (`mr_numeric_subs`:
`a=0.9, b=1.3, …`) and FLOAT points (`x = 0.35, 0.65`) into the residual `diff(r, x) - f`,
evaluates with `float`/`rectform`, and compares `cabs` with the absolute tolerance
`mr_numeric_tol` = 1e-9. Everything is double precision from the first substitution on, so
catastrophic cancellation in a large residual reads as a mismatch.

## The witness

4.1.1.2 e466, `sec(c+d*x)^3/(a+b*sin(c+d*x))^8`: rubi's answer has coefficients of degree about 18 in
a and b. The checker read `none/numeric-mismatch` with residual 4.5e-8. Measured by hand on
2026-09-28 (category 7 of `handoffs/2026-09-28-checker-wrong-answers.md`, issue 06 comment), with the
same parameter values and points substituted as exact rationals (`rationalize`):

| evaluation | residual at x = 0.35 | at x = 0.65 |
|---|---|---|
| float parameters (the checker) | 4.5e-8 | 2.8e-8 |
| rationals, then `float` | 5.1e-13 | 1.2e-12 |
| rationals, then `bfloat`, `fpprec: 50` | 2.5e-47 | 8.5e-48 |
| rationals, then `bfloat`, `fpprec: 100` | 1.0e-97 | 1.1e-97 |

The answer is exact, and the mismatch is float noise only. SymPy's check of e96/e50/e865 on
2026-09-29 used the same approach (rationals, then `N(…, 40)`) and read 0 or about 1e-175.

## The idea

Substitute exact rationals, evaluate in bigfloat (e.g. `fpprec: 50`), and keep the tolerance, or
scale it to the precision. It stays an indication, not a proof (user decision 2026-09-28), with the
same place in the verdict, just far less noise.

## Cautions before doing it

- Not every function evaluates in bigfloat: `hypergeometric`, `elliptic_*`, `li[s]` with complex
  arguments, AppellF1. Fall back to the float path when the bigfloat value is not a number.
- Cost: bigfloat evaluation of large residuals is slower. It must fit the verification budget
  (`MR_VERIFY_CAP`) and the stage timer.
- Branches: the flags question from issue 07 (`radexpand:false` / `domain:complex` for
  principal values) is separate but touches the same function; decide them together or one at a
  time, never mixed in one A/B.
- Gate: measure on the `unverified` set (`probes/verify-stages/01`) and on a control sample of
  `verified` entries, and attribute every verdict change.
