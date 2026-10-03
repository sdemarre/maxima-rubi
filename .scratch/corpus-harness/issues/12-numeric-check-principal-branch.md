# The numeric check rejects correct answers: evaluate on principal branches

Status: needs-triage
Type: checker fidelity (verdict-affecting, so A/B-gated)
Filed: 2026-10-03 (user request). Re-raises the open item of
`07-principal-branch-residuals-4.1.0.md` (parked 2026-09-28) with new witnesses;
related idea: `08-numeric-check-exact-rationals-bigfloat.md`.

## Symptom

Correct answers are recorded `unverified none/numeric-mismatch`: no symbolic stage
proves them, and the numeric check, the last word, says they are wrong.

- **4 Trig functions/4.2.10 e71**, `cos(a+b*x)/(c+d*x)^(2/3)`. rubi's answer IS
  Rubi's reference answer: built under `radexpand:false` the two are the same
  expression (`is(rubi = ref)` true, strings identical; 2026-10-03). Its
  derivative matches the integrand to 1e-17 under mpmath principal-branch
  arithmetic (a,b,c,d = 1,2,3,5; x = 0.3, 0.7, 2.0). rubi's record:
  `unverified none/numeric-mismatch` (grade A, leaf 135 = the optimal's).
- **The nine section-6 answers** of answer-quality issue 01 (6.4.2
  e14/e22/e26/e47, 6.7.1 e57/e58/e64/e65/e66; cube roots of `coth`/`sinh`):
  right under principal-branch arithmetic (`probes/leaf-size/06-ifold-principal-branch.py`),
  `unverified` in the records.
- The 7 entries of ticket 07 (4.1.0 e304 e305 e309 e310 e314 e315 e320).

## Cause (measured on 4.2.10 e71, 2026-10-03)

The checker (`test/mr_verify.mac`, `mr_numeric_point`) builds the residual
`diff(r, x) - f` and evaluates it at the sweep values (`mr_numeric_subs`,
x = 0.35, 0.65) under Maxima's defaults, `radexpand:true, domain:real`. Those
split a power of a product, `(%i*y)^(2/3)` -> `%i^(2/3)*y^(2/3)`, onto a non-
principal branch, and take real roots of negative reals, while rubi's answers
(built under the model flags) and the corpus answers (Mathematica) mean the
principal value. On rubi's answer object for e71, at x = 0.35:

| residual built and evaluated under | cabs |
|---|---|
| defaults (what the checker does) | 0.81 -> `mismatch` |
| `radexpand:false, domain:complex` | 2.8e-17 -> ok |

Ticket 07 found the same split on 4.1.0 and that the damage happens at BOTH
steps: a residual built under the defaults stays wrong under any evaluation
flags.

Two traps found on the way, for the implementation:
- Under the flags, the evaluated value can keep exact `sin(%pi/3)`-type terms,
  so the current point reads it as `declined`; the evaluation must float
  everything (e.g. `rectform(float(...))` applied until `numberp`, or
  `numer:true`).
- Re-reading an answer from its string at a default prompt rewrites it into a
  different, self-consistent form that passes; tests must use the answer
  OBJECT, as the driver does.

## Wanted

The numeric check builds the residual and evaluates its points under
`radexpand:false, domain:complex` (Mathematica's principal branches), with the
evaluation forced fully numeric. The symbolic stages are not touched.

## Acceptance

- A guard in `test/test_mr_verify.mac`: e71's answer object reads `ok` at both
  points; the 4.1.0 and section-6 witnesses likewise; a deliberately wrong
  answer (e.g. `integrate`'s e71 answer, wrong by 0.16-0.32 under mpmath) still
  reads `mismatch` -- the flags must not make the check accept wrong answers.
- Ticket 07's precondition: a control-sample A/B first. Then re-run every
  section's `unverified` class in both arms with the subset mode
  (`run_corpus_queue.py --entries-from <record> --class unverified`) and report
  the transitions; any `verified -> unverified` in the full A/B is a blocker.
- The population, counted 2026-10-03 from the `.proof.out` censuses (records
  `57371e4` rubi, 2026-09-30/10-01 native): proof tags containing
  `numeric-mismatch` -- **rubi 154** (55 `none/numeric-mismatch`, 90 with symbolic
  stages timed out, 9 `verify-timeout`), **native 348** (88, 152, 108). Not all
  are wrong-branch false negatives: some are genuinely wrong answers (native
  4.2.10 e71's `integrate` answer is one). The A/B decides which.
