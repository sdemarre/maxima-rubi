# Section 9.2 + 9.3 port — Rubi's always-loaded core rules missing from our table

Status: needs-triage
Type: task (port, runbook-driven)
Filed: 2026-09-13 (found while reading P5 run-1 `deferred` entries of
the matcher substrate, Plan 3; user: port before class 4+)

## Problem

`Rubi.m` (pinned `61e9c18`) always loads two section-9 files. Classes
2–8 load only when `$LoadElementaryFunctionRules` is true, but these two
do not depend on it:

- `9 Miscellaneous/9.2 Piecewise linear functions`: `Rubi.m` line 204,
  right after class 1 and before the `If[$LoadElementaryFunctionRules===True, …]`
  block;
- `9 Miscellaneous/9.3 Miscellaneous integration rules`: `Rubi.m` line
  356, after that block closes, the last file loaded.

`docs/rubi-architecture.md` §3 records the same layering: the
always-loaded core is "class 1 (algebraic) + 9.2 + 9.3" (2,805 rules).

Our table (`maxima_rubi.mac` `mr_load_all`) loads classes 1–3 plus
`rules/class1/9_1.mac` only. There is no 9.2 or 9.3 rule file under
`rules/`. The milestone-2 spec
(`docs/superpowers/specs/2026-08-28-milestone-2-class2-pilot-design.md`)
listed "the section-9.3 port" as a standing out-of-scope ticket, but
the ticket was never filed in `.scratch/` or `todo/TODO.md`. This file
is that ticket, widened to 9.2.

Consequence: `deferred` entries in classes 1–3 include integrands whose
Rubi route ends in a 9.2/9.3 rule. The package's PASS rates understate
the ported rule set's reach against reference Rubi. The P0 → P5 A/B of
the matcher substrate is unaffected (same rule set on both sides).

## Motivating example (hypothesis, not yet traced)

`2 Exponentials/2.3 Exponential functions.mac` e733 (L852):
`[(1+%e^x)/(%e^x+x),x,1,log(%e^x+x)]`. It is `deferred` in both
`test/corpus_class2.pre-matcher.out` and `test/corpus_class2.p5-run1.out`.
The corpus step count is 1. The candidate rule is 9.3's derivative-divides
rule (file line 47):

```mathematica
Int[u_/y_,x_Symbol] :=
  With[{q=DerivativeDivides[y,u,x]},
    q*Log[RemoveContent[y,x]] /;
 Not[FalseQ[q]]]
```

`1+e^x` is the derivative of `e^x+x`. To confirm: a `rubi_verbose`
trace of e733 on the current core (no rule fires at the top level),
then the same entry with the ported 9.3 loaded.

## Recon numbers (2026-09-13, PRE-CENSUS: the runbook Step-1 census
is authoritative)

- Rule-shaped lines (`grep -c '^Int\['`): 9.2 **19**, 9.3 **76**.
- 9.3 calls `DerivativeDivides` 20 times. `DerivativeDivides` is already
  ported (`maxima_rubi_utils.mac`, used by `rules/class3/3_5.mac`). The
  other utilities the two files need are unknown until the census runs.
- No corpus section of its own: the test suite has sections 0–8 only.
  9.2/9.3 are measured through the class 1–3 corpora (and later
  classes).
- `docs/rubi-architecture.md` §3 notes stale 9.1/9.3/9.4 duplicate
  `.m` files on disk that `Rubi.m` does not load
  (`9 Miscellaneous/9.4 Miscellaneous integration rules.m` holds the same
  derivative-divides family). Port only the files `Rubi.m` loads.

## Questions for the port

- **Load order.** Our dispatcher is first-match-wins in LoadRules
  order. 9.2 goes between the class-1 and class-2 files, 9.3 last, as in
  `Rubi.m`. Check that the generator's LoadRules replay places them
  there.
- **Generator coverage.** 9.3 is `With`/`Module`-heavy (moved inner
  conditions, spec §3.4 of the matcher substrate design). The P3
  static check's "moved inner condition calls `mr_int`" list may grow.
- **Measurement.** Full class 1–3 A/B against the standing records
  (after the matcher substrate's P6 makes them the final records):
  FAIL→PASS expected mostly from `deferred`; every PASS→FAIL attributed
  (a catch-all section can change routes that currently verify).

## Acceptance

Per `docs/class-porting.md` (the parts that apply to a section without
its own corpus): census, generated rule files under the static gate,
full-table load (probe 08), Layer A green, class 1–3 records A/B'd
with every PASS→FAIL attributed, acceptance record committed.

Order: before the class 4+ ports (every class falls through to 9.3).
Blocked by: the matcher substrate close (Plan 3 P6) — the port targets
the substrate's generator and dispatcher.

## Comments
