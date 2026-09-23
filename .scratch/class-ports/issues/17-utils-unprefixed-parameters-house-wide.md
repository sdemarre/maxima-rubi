# Unprefixed parameters/locals are house-wide in `maxima_rubi_utils.mac`, and section 9 makes the trap a much hotter path

Status: open
Type: bug (capture risk -- silently wrong antiderivatives; same mechanism as
ticket 08, different surface)
Filed: 2026-09-23 (section-9 port, final whole-branch review, item 7)

## The finding

Ticket 08 fixed the CAPTURE trap (global-constraints.md trap 1: Maxima binds
function parameters and block locals dynamically, so re-evaluating an
expression containing the corpus's own symbol of the same name reads the
binding instead) for the GENERATED rule files' own With/Module locals and for
`mr_sum`'s locals. It did not touch the HAND-WRITTEN utility functions in
`maxima_rubi_utils.mac`: most of them still take unprefixed top-level
parameters (`%mr_derivativeDivides(y, u, x)` at this file's line ~5455, whose
own locals `v, cond` are unprefixed too) rather than the house style
`%mr_<abbr>_<name>` this branch's own new ports follow (spec
`docs/superpowers/specs/2026-09-22-section9-port-design.md`,
`.superpowers/sdd/2026-09-22-section9-port/global-constraints.md` trap 1).

**Measured** (2026-09-23, `grep -cE '^%mr_[A-Za-z_0-9]+\(' maxima_rubi_utils.mac`
plus a small script that extracts each definition's top-level parameter list,
including multi-line signatures, and flags any parameter other than `x` that
does not start with `%mr_`): 316 `%mr_*` function definitions in the file,
**242 of them** take at least one unprefixed top-level parameter. (The task
brief that filed this item quoted 239; this is the number this measurement's
method actually produces -- re-measure before relying on either figure, they
were not reconciled.) The **40 new section-9 utilities are clean**: scanning
from the file's first `section 9 (2026-09-22` marker (line 6502) to the end
finds 47 `%mr_*` definitions there (not all of which are section-9's own --
the marker recurs across several of this branch's tasks) and every one of
them takes only `%mr_<abbr>_<name>`-prefixed parameters (one,
`%mr_piecewiseLinearQ(%mr_plq_u, [%mr_plq_r])`, uses Maxima's `[name]`
rest-argument syntax and is prefixed inside the brackets; a naive comma-split
first misreads it as unprefixed).

Section 9 makes this a much hotter path than it was: 9.3's derivative-divides
family (r17-r24, issue 13's condition-assignment idiom) chains several of the
oldest, most heavily unprefixed cluster-B utilities --
`%mr_derivativeDivides`, `%mr_easyDQ`, `%mr_substForFractionalPower` and kin
(this file's ~5195-5476 block; see the "class-3 cluster B" comment there) --
on every integrand these new rules try, which is a much larger fraction of
the corpus than these utilities saw before section 9 existed.

## Why this is not fixed here

Ticket 08's own fix needed a dedicated generator switch, a P3 static-gate
exception (`undo_local_prefix`, 1,602 declarations) and a **four-class A/B**
(classes 1, 2, 3, 6) to measure the blast radius before it was accepted --
and that was for a MECHANICAL, generator-driven renaming across generated
files. This trap is spread across 316 **hand-written** functions with no
generator to lean on: each rename touches call sites throughout the file
(`%mr_derivativeDivides` alone is called from the 9.3 generated rules and
from other utilities), and a mis-rename is a silent-wrong-answer bug, not a
loud one. It needs its own scoped plan and its own four-class (or more, once
later classes exist) A/B before/after, not a drive-by edit alongside this
fix wave.

## Suggested next step (not applied here)

1. Enumerate the 242 (or however many a re-measurement finds) unprefixed
   functions and rank them by call-graph reach from a generated rule (the
   ones the corpus can actually exercise matter most; a utility only called
   by another utility that no rule reaches is lower priority).
2. Prefix top-level parameters and block/lambda locals function by function
   (or in batches sharing an `<abbr>`), verifying each batch against a
   probe of the mechanism ticket 08 used (`probes/maxima/probe-class4-with-
   capture.run`'s comparison: `rubi(f, x)` vs `subst(q=d, rubi(subst(d=q,
   f), x))` for a suspect symbol, and the numeric residual check).
3. Full four-class A/B (`python3 test/ab_records.py`) after each batch,
   attributing every PASS->FAIL and expecting some FAIL->PASS recoveries
   (ticket 08 found unprefixed locals were an ACTIVE source of wrong
   answers, not just a latent risk: `mr_sum`'s own locals cost class 1
   0.035-0.30 relative residual on several corpus families before the fix).

## Related

- Ticket 08 (generator With/Module locals + `mr_sum`) -- the same capture
  mechanism, already fixed for the generated side; this ticket is the
  hand-written-utility side it left open.
