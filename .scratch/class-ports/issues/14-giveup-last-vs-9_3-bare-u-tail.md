# `mr_giveup_last` defers the Unintegrable markers behind 9.3's bare-`u_` tail — 189 PASS→FAIL

Status: fixed (2026-09-23); the four-class re-measure is pending
Type: bug (faithfulness — rule ordering; the whole of class 3's -96 in the section-9 measurement)
Filed: 2026-09-23 (section-9 port, Task 14 attribution; spec
`docs/superpowers/specs/2026-09-22-section9-port-design.md` A6.1)

## The finding

`mr_giveup_last` (default true, `maxima_rubi_dispatch.lisp`) walks
`mr_rule_table` in TWO passes: pass 1 skips every give-up rule (one whose
replacement answers `mr_unintegrable`), pass 2 runs them. Its docstring states
why: our table is LOAD order, Mathematica's is SPECIFICITY order, so a general
give-up that loads early must not pre-empt a specific rule that loads late.

**What the docstring does and does not claim.** It does NOT say the switch
recovers 318 class-1 entries. It says "reordering ALONE recovers nothing,
because the seen-cut self-recursion of `1_2_3_5` r12 blocks the same path
first", that the switch "is half of a PAIR with the seen-cut fall-through
(`maxima_rubi_utils.mac`, `%mr_top_body`)", and that the 318-of-341 figure is
the measurement of **the pair**, with 300/300 control entries unchanged. So the
switch's own cost is not on record and had to be measured here; see "What
flipping the switch off costs" below.

Section 9.3 inverts the premise. Its tail contributes **ten NON-give-up
bare-`u_` records** — r9, r37, r38, r51, r55, r56, r57, r62, r63, r66 (r67,
the `CannotIntegrate` catch-all, is the eleventh and IS a give-up) — and pass 1
reaches all ten before pass 2 reaches the **72 `Unintegrable` marker rules** of
classes 1/2/3. In Mathematica those marker rules are SPECIFIC patterns and beat
`Int[u_, x_Symbol]`; under `mr_giveup_last` they lose.

The symptom: an entry whose corpus answer is `Unintegrable`/`CannotIntegrate`
used to answer the TOP-LEVEL noun (driver class `no-answer`, a PASS class) and
now answers a partially reduced expression carrying the marker INSIDE it
(`contains-noun`), or burns the 30 s cap on the way (`timeout`).

## Measured (2026-09-23, build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7)

Section-9 measurement, reference core `0182d32c` (3,911 rules, `master`
`c95c6ed`) vs branch core `434c241a` (3,997 rules, `section9-port` `1f31a27`),
queue runner, 24 workers, 30 s cpu cap:

**189 of the 305 PASS→FAIL entries** — 115 of class 3's 118, 9 of class 2's 10,
65 of class 6's 162, plus 13 more that are also inert-head leaks (ticket 15).

The isolating experiment: the SAME branch core over exactly those PASS→FAIL
entries with `mr_giveup_last=false` and nothing else changed (12 workers, 30 s
cpu cap) puts all 189 back in a PASS class —
`test/section9_giveup_arm_class{1,2,3,6}.out`, scored by
`python3 test/section9_attribution.py` (`test/section9_attribution.out`).

Witness — **committed probe `probes/section9/01-giveup-ordering.{mac,run,out}`**,
`sh probes/section9/01-giveup-ordering.run`, three arms: reference core, branch
core, branch core with the switch off. `3 Logarithms/3.4` e635
`(a+b*log(c*(d+e/(f+g*x))^p))^n`, corpus `Unintegrable`, Rubi step count **0**
(so Rubi applies no rule at all):

| core | route | answer |
|---|---|---|
| reference | whole table declines, then the give-up pass: `3_4 r39` | `unintegrable((a+b log(c (d+e/(f+g x))^p))^n, x)` — PASS |
| branch | pass 1 reaches the tail: `9_3 r51` (`FunctionOfLinear`) substitutes `x -> (x-f)/g`; the inner integral falls to `3_4 r6`'s marker | `unintegrable((a+b log(c((d g x+d f+e)/(g x+f))^p))^n, g x+f)/g` — `contains-noun`, FAIL |

`3.4` e104 `1/(x*log(c*(a+b*x^2)^p))` is the same shape through a different 9.3
record: the reference answers the top-level noun through `3_4 r14`, the branch
fires **`9_3 r52`** (`PowerVariableExpn`). With `mr_giveup_last:false` the
branch core answers the clean top-level noun for both (probe 01's third arm).

## What flipping the switch off costs — MEASURED, not quoted

**Committed probe `probes/section9/06-giveup-switch-control.{py,run,out}`.** A
seeded random sample (seed 20260923) of 2,000 class-1 entries that PASS in the
branch record, run twice on the BRANCH core at the SAME worker count, differing
only in `mr_giveup_last` — so contention is held constant and the arms are
comparable with each other (not with the 24-worker record).

| arm | PASS of 2,000 |
|---|---|
| `mr_giveup_last=true` (shipping) | 2,000 |
| `mr_giveup_last=false` | **1,936** |

**64 lost, 0 gained.** Every loss is a verdict-CLASS change, not a cost one: 62
`verified -> contains-noun` and 2 `verified -> deferred`, with **0** going to
`timeout`, so the worker count plays no part in the result. 3.2 % of a class-1
PASS sample.

So the switch IS carrying real answers — just not the 318 the docstring is
sometimes quoted for, which is the pair's figure — and turning it off to fix
the 189 would trade them away. Hence the third tier below rather than a flip.

## Suggested fix (not applied here)

A THIRD tier in `%mr_dispatch_tree`: ordinary rules, then give-up rules, then
the bare-`u_` last-resort records; equivalently, keep the 9.x bare-`u_` tail
out of pass 1. It is a dispatcher change, not a re-port. Measure it the same
way (the 189 entries plus probe 06's control sample, then a full four-class
A/B), because the tier order interacts with the class-1 set the switch and the
seen-cut fall-through were introduced for as a pair, and with the class-4
bridge tail.

## Related, same root cause (load order vs specificity)

Spec A6.4's ten `route` entries, traced by **committed probe
`probes/section9/04-route-rules.{mac,run,out}`**: `9_3 r63` (`ExpandIntegrand`,
`9.3 …:560-563`, 4 entries), `9_3 r54` (the fractional-power substitution,
`9.3 …:463-466`, 2), `9_3 r51` then `9_3 r46` (4). Each condition is a
byte-faithful port; what differs is which rule gets there first.

One sub-question is OPEN and belongs here (probe 04's `EXPANDINTEGRAND` lines):
`%mr_expandIntegrand(x^2/(x+log(x)), x)` returns
`log(x)^2/(log(x)+x) - log(x) + x` and `%mr_expandIntegrand(x/(%e^x+x), x)`
returns `1 - %e^x/(x+%e^x)`, both `SumQ` true — it divides treating `log(x)`
and `%e^x` as indeterminates, which is what makes `9_3 r63`'s guard true. The
utility is PRE-EXISTING and prints identically on both cores in probe 04; what
is new is the 9.3 record that consumes it. Whether
Mathematica's `SmartApart` (`IntegrationUtilityFunctions.m:3897`, reached from
`ExpandExpression` at 3780 through its line 3785) does the same on that input
has NOT been measured — this repo has no Mathematica. If it does not,
`%mr_expandIntegrand` is itself wrong and those four entries have a second
cause.

Ticket 07 (bare-`u_` records mid-table) is the sibling ordering ticket.

## User decision, 2026-09-23

**Fix it — build the third dispatch tier.** Not shipped as a documented
regression: the project's measure is Rubi's own PASS counts, and class 3's
−96 is a real loss against them. Flipping `mr_giveup_last` is ruled out by
`probes/section9/06-giveup-switch-control.out` (the switch alone loses 64 of a
seeded 2,000-entry class-1 PASS sample, gains 0). The fix is measured against
the 189 give-up-bucket entries plus that 2,000-entry control.

## Fix (2026-09-23)

Two run switches in `maxima_rubi_dispatch.lisp`, both default true, and two
per-rule marks `mr_load_all` sets (`%mr_mark_tail` on
`mr_rule_table_tail_handles`, `%mr_mark_general` on `mr_rules_9_3`). Under
`mr_giveup_last` the walk becomes Mathematica's order by specificity
class, in four passes (`mr-rule-tier`):

1. specific ordinary rules (classes 1/2/3/6, 9.1, 9.2);
2. the specific give-ups (the 72 markers, 9.3's body give-ups r3/r4);
3. 9.3's general body, then every bare-`u_` tail record -- the class-4
   bridge included -- in table order;
4. the bare-`u_` give-ups: `4_7_5 r72`, then `9_3 r67`.

`mr_last_resort_tier` alone (tail only; the bridge's ordinary records stay
in pass 1) and `mr_general_after_giveups` (9.3's body AND the bridge to
pass 3) are separable for A/B.

**`4_7_5 r72` is in pass 4, not 2, on purpose.** It accepts ANY inert
integrand, so a plain third tier (ordinary -> give-ups -> 9.3 tail) would
run it before `9_3 r51`, which answers the inert integrand in ~600 class-6
entries (ticket 15's census).

**Measured, all paired on one core (12 + 12 workers, 30 s cpu cap):**

- `probes/section9/09-last-resort-tier.out` -- tail tier off vs on. The
  214-entry set (every PASS->FAIL the give-up experiment restored; it
  contains this ticket's 189): 14 -> 129 PASS, 0 lost. Probe 06's 2,000
  class-1 control: 0 lost, 1 gained. Of the 74 `no-answer` entries left, the
  top-level rule was a 9.3 BODY record in 49 (r52 `Int[u_/x,x]`, r54, r46,
  r53, r49, r41) and the bridge `4_1_0_1 r1` in 24.
- `probes/section9/10-general-body.bridge-pass1.out` -- first try at the
  body step, bridge left in pass 1: the bucket +49, but section 9's 1,132
  FAIL->PASS gains lost 25, 24 of them real slowdowns (0.8-5 s -> timeout,
  class 6): the bridge had jumped AHEAD of 9.3's body.
- `probes/section9/10-general-body.out` -- the shipped order (bridge moves
  with the body): the bucket **+51 / -0 (178 of 214 PASS)**, control
  unchanged, the 1,132 gains **+2 / -1** (the -1 `expected -> timeout` at
  29.8 s).

Not recovered (36 of 214): the 8 class-1 `verified -> timeout` entries at
the cap (a load effect in the section-9 record, not ordering), and entries
whose top-level route is the bridge `4_1_0_1 r1` -- 9.3 records act inside
the inert domain before `4_7_5 r72`'s give-up, where Mathematica has a
specific 4.x rule: that is class 4 proper (ticket 05).

Gates: dispatch 106/0 (+26), section-9 e2e 9/0 (+2: 3.4 e635/e104 answer
the top-level noun, RED 7/2 with both switches off), rule-table order 13/0
(+2: the marks equal the lists), Layer A 1293/0, no-inert-leak 5/0,
mr-match 57/0, mr-tree 58/0, generator P3 23/0, run-records 43/0, harness
guards unchanged.

The open sub-question above (`%mr_expandIntegrand` vs `SmartApart` on
`x^2/(x+log(x))`) is untouched.
