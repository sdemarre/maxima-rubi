# Section-6 answers still graded C after the %i fold

Status: needs-triage
Type: answer quality (grade C, verdict unaffected) -- section 6, 283 entries
Filed: 2026-10-03

## Symptom

After the %i fold (issue 01, `mr_ifold`), section 6 still grades **C on 283 of
5,080** rubi answers (`test/corpus_class6.grade.out`, records `2988844`): the
answer carries `%i`, the optimal does not. By file: 6.1.7 71, 6.4.2 36, 6.7.1 26,
6.2.7 23, 6.2.2 21, 6.2.1 20, 6.1.1 15, 6.3.2 13, the rest under 10.

Named example: 6.3.7 e56 (`csch(c+d*x)^4*(a+b*tanh(c+d*x)^3)`), whose answer keeps
`log(tan(%i*d*x+%i*c))`-type terms: the fold rewrites the tan, but the `%i` it
leaves cancels only across the log (`log(%i*u) - log(%i*v)`), which neither
`%iargs` nor the fold's sum rule reaches.

## Where to start

- The list: `grep "^C " test/corpus_class6.grade.out`; probe 05's `C->C` lines
  (`probes/leaf-size/05-ifold-all-sections.out`) carry the folded grades.
- Classify a sample by why the `%i` stays: across a log (above), inside a
  fractional power (the 9 attributed entries of issue 01 are of this family:
  `(-%i*coth(u))^(1/3)`), a genuinely complex constant, other.
- Any further fold must keep issue 01's constraint: a simplification
  Mathematica's evaluator does on its own, not a new integration step, measured
  on every entry it can act on (probe 05's harness takes a fold as text).

## Triage, 2026-10-03

Probes `probes/leaf-size/07-remaining-i-answers.{py,out}` (re-runs the 283 C entries
at the current defaults, `mr_ifold` true, dumps `ANSWER`/`OPTIMAL1`; all 283 still grade
C) and `08-classify-remaining-i.{mac,out}` (walks each answer, tags the nearest context
of every `%i`). Build `branch_5_50_base_84_g4204fb669`. One family per entry:

| family | n | where | cause (traced) |
|---|---|---|---|
| complex-conjugate pair (atan/atanh, partial fractions, polylog args) | 92 | 6.2.7 23, 6.1.7 16, 6.4.2 12, 6.3.2 10, 6.6.2 9, 6.7.1 10 | complex-root split where the optimal keeps one real atanh/log; a route difference, not a fold |
| `%pi/2` shift | 63 | 6.2.2 21, 6.2.1 20, 6.1.1 8, 6.3.1 7, 6.4.1 7 | 6.1.1 e6: bridge `4_1_0_1 r1` -> `4_1_10 r8`, whose `Cos[(d e - c f)/d]` gets `e = %i*a + %pi/2`; Maxima keeps `(%i*(%i*a+%pi/2)*d+b*c)/d` as one quotient, so neither the `%pi/2` shift nor the `%i` factor reduces |
| elliptic `%i*asinh` | 57 | 6.1.7 55, 6.5.3 2 | `elliptic_f(%i*asinh(..), a/b)` against the optimal's `elliptic_f(atan(sinh u), 1-b/a)`; a route difference |
| `log(%i*u)` constant factor | 45 | 6.4.2 10, 6.7.1 10, 6.3.7 9, 6.1.1 7, 6.4.1 5 | 6.1.1 e30: `4_3_1_1 r3` returns `log(RemoveContent(cos(u+%pi/2)))` = `log(sin(%i*b*x+%i*a))`; Mathematica evaluates `Sin[I a + I b x]` to `I Sinh[a+b x]` before RemoveContent strips the `I`; here the top-level fold produces the `%i` after RemoveContent, inside the log |
| fractional power `(-%i*coth u)^(1/3)` | 20 | 6.4.2 14, 6.7.1 6 | issue 01's attributed family |
| no `%i` at all (hypergeometric vs elementary log) | 6 | 6.1.5, 6.2.5, 6.5.3, 6.6.3 | the older "hypergeometric C's" finding, not this ticket |

The two fold-shaped families (`%pi/2` shift 63, `log(%i*u)` 50: 113 entries) both come
from Mathematica evaluating `Sin[I u]`-type subterms at EVERY step (inside RemoveContent,
inside a rule's argument arithmetic), while `mr_ifold` acts once at depth 0. The other
170 are different integration routes or not `%i` at all.

Correction (2026-10-03, probe 09): 5 of the census's 50 `log(%i*u)` entries hold a
complex SUM in the log (`log(%i*sqrt(b)*sinh(u)+sqrt(a)*cosh(u))`, 6.3.7
e171/e173/e175, 6.4.7 e5/e50); they belong to the complex-conjugate family (table
above corrected: 45 / 92).

### 2026-10-03 -- RemoveContent fold accepted

Spec `docs/superpowers/specs/2026-10-03-removecontent-ifold-design.md`, plan
`docs/superpowers/plans/2026-10-03-removecontent-ifold.md`, branch `rcfold`.
`%mr_removeContent` folds `%i` out of its argument (`%mr_ifold_safe`, switch
`mr_ifold`). Every section re-run (`.scratch/answer-quality/rcfold_ab/`): section 6
C -> A 33, C -> B 1 (C 283 -> 249); all other grade and verdict changes are the 30 s
cap or the checker's budget under 24 workers, each re-checked alone in both switch
arms (4.1.1.2 e537/e567/e568/e571, 4.5.1.4 e310, 4.7.2 e258: verify at 17.4-18.1 s
in both; 5.3.6 e167/e170/e224 timeout -> contains-noun, FAIL both; 5.3.6 e243 verify
timeout, proved alone in both). Probe 07/08 re-run on the 249: per-context counts
log 111 -> 77, the rest unchanged.

Left in this ticket: the `%pi/2` shift (63), the complex-conjugate pairs (92), the
elliptic `%i*asinh` (57), the fractional powers (20, issue 01's family), 11
`log(%i*tanh(u))` (ticket 03), 6 hypergeometric (not `%i`).

Note for the next A/B against these records: the committed `test/corpus_class4.out`
carries six timeouts caused by load (4.1.1.2 e537/e567/e568/e571, 4.5.1.4 e310, 4.7.2
e258; 30.1-31.2 s under 24 workers, ~18 s alone in both switch arms). Expect them to
flip back to verified; they are not a change's effect.
