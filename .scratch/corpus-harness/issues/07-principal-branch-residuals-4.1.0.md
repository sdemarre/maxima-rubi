# The 4.1.0 "wrong answers" are checker artefacts: default-flag residuals of complex powers, and 2F1 residuals no stage closes

Status: parked (user decision 2026-09-28: live with these results for now; no hypergeometric
special case in the checker)
Type: finding (checker limitation), no code change
Filed: 2026-09-28, from category 2 of `handoffs/2026-09-28-checker-wrong-answers.md`

## Entries

`4 Trig functions/4.1 Sine/4.1.0 (a sin)^m (b trg)^n.mac` e304 e305 e309 e310 e314 e315 e320,
`cos(e+f*x)^{2,4} * (b*sin(e+f*x))^{±1/3, ±5/3}`. The checker read them
`unverified none/numeric-mismatch`, and the 02 triage counted them as rubi wrong answers.

Evidence: `probes/verify-stages/06-principal-branch-4.1.0.{mac,sh,out}` (build
`branch_5_50_base_84_g4204fb669`, rules core `5ba5c2ed`, 2026-09-28).

## Findings

1. **rubi's answers are numerically right under principal values.** For all 7, a central difference
   of the answer (h = 1e-5), with both it and the integrand evaluated under
   `domain:complex, radexpand:false`, matches the integrand to 1e-11 to 4e-11 at x = 0.35 and 0.65
   (`FD` lines). That is an indication, not a proof.

2. **The checker's residual is wrong under Maxima's defaults.** `diff(r, x) - f` built and evaluated
   under `radexpand:true, domain:real` gives 2e-3 to 9e-2 (`RDEF`). Built and evaluated under
   `domain:complex, radexpand:false` it gives 1e-16 (`RFLG`). The mechanism: `radexpand:true`
   splits a power of a product with a numeric factor, so `(-0.8775*%i)^(1/3)` becomes
   `(-0.8775)^(1/3)*%i^(1/3)` = `-0.829-0.479i`. That is neither the real-domain value nor the
   principal one (`0.829-0.479i`). `domain:real` also takes the real root of a negative real,
   `(-1.89)^(1/3)` = `-1.236`, where Mathematica takes the principal value. The damage happens at
   BOTH steps: an arm that builds the residual under the defaults stays wrong under any evaluation
   flags, and one built under either flag stays right under either flag (measured on e304 at
   x = 0.35, scratch). So the `numeric-mismatch` verdict was not evidence of a wrong answer.

3. **No symbolic stage proves them, under either flag set** (`SYM def` / `SYM flg`, stage cap
   30 s). The answers come from 4_7_9 r42 (the exponential-form expansion) and 2_3 r96, and carry
   `hypergeometric([a, b], [b+1], %e^(2*%i*(f*x+e)))`. `diff` turns each into a 2F1 with shifted
   parameters, and cancelling that needs a contiguous relation none of the radcan-family stages
   applies. `hgfred` / `hypergeometric_simp` do not reduce these to elementary functions: they are
   incomplete beta functions.

4. **Diagnostic only: rewriting 2F1(a,b;b+1;z) to `b*z^(-b)*beta_incomplete(b,1-a,z)` BEFORE `diff`
   makes 5 of 7 provable** (`HB` lines): e304 e305 e314 e315 at `exponentialize` under the defaults,
   e320 at `exponentialize` only under the two flags. e309 and e310 (`^(5/3)`, 2F1s with a negative
   parameter, -5/6 or -11/6) stay unproved in both arms. In scratch, e310's rewritten residual was
   numerically nonzero (about 0.09) at x = 0.35, although the identity itself checks numerically at
   z = 0.3 for b = -5/6. The suspect is `beta_incomplete`'s branch at complex z on the unit circle
   for a negative first parameter (not confirmed). **Not adopted as a checker stage** (user decision
   2026-09-28).

5. **Why rubi takes 4_7_9 r42 here at all.** The corpus integrand is `(b*sin(e+f*x))^(1/3)`. Under
   `radexpand:true` Maxima reads it as `b^(1/3)*sin(e+f*x)^(1/3)`. 9_1 r12 pulls `b^(1/3)` out, and
   `cos^4*sin^(1/3)` matches 4.7.9's `Int[Cos[..]^p*Sin[..]^q]` (IGtQ[p, 0], q not an integer)
   before the tail's DeactivateTrig bridge. Rubi in Mathematica sees `(b*Sin[..])^(1/3)`, which that
   pattern does not match, so it goes through the bridge to 4.1.0.1's Hypergeometric2F1 rule (the
   corpus answer). The route differs because of how the input is read, not because of a rule defect.
   Both routes are valid.

## Open (not acted on)

- The checker builds residuals and evaluates numeric points under Maxima's defaults. Binding
  `radexpand:false` + `domain:complex` (Mathematica's principal branches) would remove the false
  mismatch, but it is a verdict-semantics change that needs a control-sample A/B first. It does not
  prove these 7 entries: finding 3 holds under both flag sets.
- e309/e310: the negative-parameter `beta_incomplete` branch.
