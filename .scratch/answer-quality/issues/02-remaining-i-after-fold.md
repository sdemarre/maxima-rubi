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
