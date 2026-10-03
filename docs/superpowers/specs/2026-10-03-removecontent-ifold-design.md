# RemoveContent folds %i out of its argument — design

Date: 2026-10-03. Ticket: `.scratch/answer-quality/issues/02-remaining-i-after-fold.md`
(triaged 2026-10-03). Evidence: `probes/leaf-size/07-remaining-i-answers.{py,out}`,
`08-classify-remaining-i.{mac,out}`, `09-removecontent-ifold.{py,out}`, build
`branch_5_50_base_84_g4204fb669`. Builds on the depth-0 fold,
`docs/superpowers/specs/2026-10-02-ifold-answer-design.md`.

## 1. Goal

After the depth-0 `%i` fold, 283 section-6 answers still grade C. Probe 08's
triage puts 50 of them in the `log(%i*u)` family: an answer term
`log(%i*sinh(u))` (or `log(-%i*..)`) where Rubi's optimal has `log(sinh(u))`.

Traced on 6.1.1 e30, `(c+d*x)*csch(a+b*x)^2` (`rubi_verbose : 'matches`): the
bridge `4_1_0_1 r1` and `4_5_10 r5` reach `4_3_1_1 r3`,
`Int[Tan[c+d x]] -> -Log[RemoveContent[Cos[c+d x], x]]/d`, with the argument
`%i*b*x + %i*a + %pi/2`. In Mathematica the argument of `RemoveContent` is
evaluated first: `Cos[I a + I b x + Pi/2]` becomes `-I Sinh[a + b x]`, and
RemoveContent strips the content `-I`. In the port `cos(.. + %pi/2)` simplifies
to `-sin(%i*b*x+%i*a)`; nothing folds the `%i` out of the sine, RemoveContent
strips only the `-1`, and the depth-0 fold later rewrites the result to
`log(%i*sinh(b*x+a))` — the `%i` is then inside the log, out of the fold's reach.

The fix makes RemoveContent see what Mathematica's RemoveContent sees: its
argument with `%i` folded out, as Mathematica's evaluator would have left it.

## 2. Why this boundary is safe

The depth-0 fold's design rejected folding intermediate expressions because
folded integrands would change which rules match. RemoveContent's value is not
an integrand: all 25 call sites in `rules/` are `log(%mr_removeContent(..))`
(class 1: 9 files, class 4: 4, classes 5/7/9: 1 each; `grep -o
"log(%mr_removeContent" rules/class*/*.mac`), so its value only ever lands in
the answer, inside a log.

## 3. The change

`%mr_removeContent(u, x)` (`maxima_rubi_utils.mac`, the RemoveContent family),
as its first step, when `mr_ifold` is true:

    u : %mr_ifold(u)    under radexpand:false, logexpand:false, inside errcatch
                        with errormsg false; on error u is kept

— the wrapper `%mr_top_final` already uses (the flags are mandatory, see the
depth-0 spec section 1: under the defaults the fold splits folded powers onto
the wrong branch). The wrapper is factored out of `%mr_top_final` into one
helper both callers use, so the two cannot drift.

- `%mr_ifold`'s fast path returns an `%i`-free argument itself: only arguments
  holding `%i` can change.
- **Switch: `mr_ifold`** (user decision 2026-10-03). False turns off both folds
  and reproduces the earlier answers; no new switch, so existing records'
  `filter:` lines stay readable as arms.
- RemoveContent keeps every other step; `%mr_removeContentAux` is not touched.

## 4. Measured (probe 09)

The 50 `log(+-%i*..)` candidates of probe 07, rubi as shipped against rubi with
the redefinition above: **34 fixed** (no `log(+-%i*..)` left, e.g. 6.1.1 e30 ->
`d*log(sinh(b*x+a))/b^2 + ..`, Rubi's optimal), 16 unchanged:

- 11 are `log(%i*tanh(u))` from a substitution rule (6.7.1 e24: `4_1_0_3 r2`,
  `Subst[Int[1/x, x], x, Tan[u]]`), never through RemoveContent. Rubi's `Subst`
  wraps its result in `SimplifyAntiderivative`
  (`IntegrationUtilityFunctions.m:5147-5149`), whose rule
  `Log[c_*u_] -> Log[u] /; FreeQ[c,x]` (`:5291`) removes this content.
  SimplifyAntiderivative is **not ported** (no occurrence in the package);
  porting it is a separate ticket (section 7).
- 5 are not constant content: the log holds a complex sum
  (`log(%i*sqrt(b)*sinh(u)+sqrt(a)*cosh(u))`, 6.3.7 e171/e173/e175, 6.4.7
  e5/e50) — probe 08's complex-conjugate family, misfiled by the census regex.

Probe 09 checks the answer's shape only; the verdicts and grades are measured
by the acceptance run (section 6).

## 5. Tests (Layer A, `test_maxima_rubi.mac`, beside the RemoveContent checks)

- `%mr_removeContent(sin(%i*b*x+%i*a), x)` is `sinh(b*x+a)`, and
  `%mr_removeContent(cos(%i*b*x+%i*a+%pi/2), x)` — 4_3_1_1 r3's shape — is
  `sinh(b*x+a)` (measured 2026-10-03 with probe 09's redefinition; shipped:
  `sin(%i*b*x+%i*a)` for both).
- An `%i`-free argument: the existing RemoveContent checks stay green
  (`3*(x+1)` -> `x+1` measured under the redefinition).
- `mr_ifold : false`: both `%i` arguments above return `sin(%i*b*x+%i*a)`, the
  shipped value.
- End to end: 6.1.1 e30 answers with `log(sinh(b*x+a))` and no `%i`.

## 6. Acceptance

Every section re-run (rubi arm, `mr_ifold` true, 24 workers, as the depth-0
fold's acceptance), then `test/ab_records.py` and `test/ab_grades.py` against
the current records: every PASS -> FAIL and every grade that gets worse
attributed. Probe 07 re-run on the remaining C's for the new census. All gates
listed in AGENTS.md green; Layer A's count updated there.

## 7. Out of scope (follow-ups)

- A ticket: port `SimplifyAntiderivative` (`IntegrationUtilityFunctions.m:5265-`,
  about 40 rules plus helpers) into `%mr_subst` — the 11 `log(%i*tanh(u))`
  entries, and every other answer Rubi's Subst normalises; 1,194 `%mr_subst`
  call sites across the classes.
- Ticket 02's triage table: move the 5 misfiled entries to the complex-conjugate
  family (log-family 45, of which this change fixes 34).
- The `%pi/2`-shift family (63) and the other families of ticket 02.
