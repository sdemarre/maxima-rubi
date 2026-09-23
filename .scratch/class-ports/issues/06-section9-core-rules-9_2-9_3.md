# Section 9.2 + 9.3 port — Rubi's always-loaded core rules missing from our table

Status: done (2026-09-23 — see Resolution)
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

2026-09-13 — first half of the e733 check (an ad-hoc session trace,
not a committed probe; matcher-substrate tree `af64cf2`, build
2026-08-31 13:27:47, load path, table 3,513 rules):
`rubi_verbose : true; rubi((1+%e^x)/(%e^x+x), x)` answers
`unintegrable((%e^x+1)/(%e^x+x), x)` in ~2 s. The 175 verbose lines
are all `cond not accepted`: no rule fires, declines or misfires. The
rules whose pattern matched but whose cond refused are in 1.4.1 (33),
1.4.2 (27), 1.3.4 (22), 1.3.3 (19), 1.1.1.7 (16), 2.1 (10), 9.1 (9,
rules r1/r2/r7/r8/r12/r13/r21: integrand-simplification rules —
zero-coefficient, sum-splitting and `(a+b x)`/`(c+d x)` reductions,
none a derivative-divides rule), 1.1.3.7 (9), 2.3 (8), and smaller
counts. So nothing in the current table handles the
numerator-is-the-denominator's-derivative shape. The second half
(9.3's rule answering once ported) needs the port.

2026-09-22 — **Specced**: `docs/superpowers/specs/2026-09-22-section9-port-design.md`
(reviewed with the user 2026-09-22; review fixes applied). Scope 9.2 + 9.3
from the pinned files; the legacy `rules/class1/9_1.mac` stays; 9.1
Derivative integration moves to ticket 01. **Candidate legacy addition**,
to be measured, not ported blind: old `9.4` L58 (pre-renumbering Rubi,
`f7fa0fd^`), `Int[x_^m_*u_, x] := With[{k=Denominator[m]},
k*Subst[Int[x^(k*(m+1)-1)*ReplaceAll[u, x->x^k], x], x, x^(1/k)]] /;
FractionQ[m]`: the general fractional-power substitution, the only old
left-hand side with no pinned successor (`probes/rubi/04-section9-load-and-legacy.out` §F).

## Resolution (2026-09-23, branch `section9-port`, Tasks 1-14)

Status: **done**. 9.2 (19 rules) and 9.3 (67) are ported and loaded —
`rules/class9/9_2.mac`, `rules/class9/9_3.mac`, 86 rules, in `Rubi.m` LoadRules
positions (9.2 right after class 1, 9.3 last of all; `mr_load_all`,
`maxima_rubi.mac`). The rule table is 3,997 records.

**The measurement and the full attribution are spec amendment A6**,
`docs/superpowers/specs/2026-09-22-section9-port-design.md` (records in `test/`:
`corpus_class{1,2,3,6}.s9-ref.out` / `.s9.out`, `section9_ab_class{N}.out`,
`section9_paired_class{N}.{ref,new}/`, `section9_giveup_arm_class{N}.out`,
`section9_timing_ab.out`, `section9_attribution.py` / `.out`). Headline, four
classes, 34,827 entries, reference core `0182d32c` -> branch core `434c241a`:
**PASS 22,189 -> 23,016 (+827)**, 1,132 FAIL->PASS, 305 PASS->FAIL, all 305
attributed (A6.0.1).

**This ticket's motivating entry.** `2 Exponentials/2.3` e733
`(1+%e^x)/(%e^x+x)`: `deferred` -> **`verified`** in 0.4 s, through 9.3's
derivative-divides rule — the second half of the 2026-09-13 check, as predicted.

**Old 9.4 L58 stays recorded as a candidate legacy addition** (the general
fractional-power substitution `Int[x_^m_*u_,x] := With[{k=Denominator[m]}, …]
/; FractionQ[m]`, `probes/rubi/04-section9-load-and-legacy.out` §F). It was NOT
ported here — the pinned 9.3 has its own `Int[x_^m_*Fx_,x_]` (r54), and A6.4
shows r54 already changing routes on two entries, so adding another general
substitution rule needs its own measurement.

**Three defects the measurement found are open as their own tickets**, and two
of them are recommended as fixes BEFORE the branch merges:

- `14-giveup-last-vs-9_3-bare-u-tail.md` — 189 PASS->FAIL, the whole of class
  3's -96: `mr_giveup_last` defers classes 1/2/3's `Unintegrable` markers behind
  9.3's ten non-give-up bare-`u_` tail records.
- `15-class9-body-rules-leak-inert-trig-heads.md` — 281 class-6 answers carry
  `%mr_itan` & co, 89 of them previously PASS and 69 previously CORRECT:
  `9_3 r41` fires inside the class-4 inert-trig domain and its prefactor is
  never re-activated. **Blocking.**
- `16-9_3-r41-match-enumeration-blowup.md` — `1.3.1` e190/e238 go from 1.7 s
  and 6.2 s to over 120 s; the same rule, but through match enumeration.

Tickets 09, 10, 11 and 12 (filed during this port) stay open; ticket 13 (the
condition-assignment idiom) was fixed in Task 12b.
