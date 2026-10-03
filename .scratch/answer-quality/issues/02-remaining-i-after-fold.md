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
| complex-conjugate pair (atan/atanh, partial fractions, polylog args) | 87 | 6.2.7 23, 6.1.7 16, 6.4.2 12, 6.3.2 10, 6.6.2 9, 6.7.1 10 | complex-root split where the optimal keeps one real atanh/log; a route difference, not a fold |
| `%pi/2` shift | 63 | 6.2.2 21, 6.2.1 20, 6.1.1 8, 6.3.1 7, 6.4.1 7 | 6.1.1 e6: bridge `4_1_0_1 r1` -> `4_1_10 r8`, whose `Cos[(d e - c f)/d]` gets `e = %i*a + %pi/2`; Maxima keeps `(%i*(%i*a+%pi/2)*d+b*c)/d` as one quotient, so neither the `%pi/2` shift nor the `%i` factor reduces |
| elliptic `%i*asinh` | 57 | 6.1.7 55, 6.5.3 2 | `elliptic_f(%i*asinh(..), a/b)` against the optimal's `elliptic_f(atan(sinh u), 1-b/a)`; a route difference |
| `log(%i*u)` constant factor | 50 | 6.4.2 10, 6.7.1 10, 6.3.7 9, 6.1.1 7, 6.4.1 5 | 6.1.1 e30: `4_3_1_1 r3` returns `log(RemoveContent(cos(u+%pi/2)))` = `log(sin(%i*b*x+%i*a))`; Mathematica evaluates `Sin[I a + I b x]` to `I Sinh[a+b x]` before RemoveContent strips the `I`; here the top-level fold produces the `%i` after RemoveContent, inside the log |
| fractional power `(-%i*coth u)^(1/3)` | 20 | 6.4.2 14, 6.7.1 6 | issue 01's attributed family |
| no `%i` at all (hypergeometric vs elementary log) | 6 | 6.1.5, 6.2.5, 6.5.3, 6.6.3 | the older "hypergeometric C's" finding, not this ticket |

The two fold-shaped families (`%pi/2` shift 63, `log(%i*u)` 50: 113 entries) both come
from Mathematica evaluating `Sin[I u]`-type subterms at EVERY step (inside RemoveContent,
inside a rule's argument arithmetic), while `mr_ifold` acts once at depth 0. The other
170 are different integration routes or not `%i` at all.
