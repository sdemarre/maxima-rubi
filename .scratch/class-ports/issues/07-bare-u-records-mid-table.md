# Six legacy bare-`u_` Int records sit mid-table, not last

Status: open
Type: task (faithfulness — rule ordering)
Filed: 2026-09-21 (inert-trig substrate plan, Task 8 pre-flight)

## The finding

Classes 1/2/3 carry **six** Int records whose integrand pattern is a bare
`u_` (or `a_`), i.e. `Int[u_, x_Symbol] := … /; cond`. They are emitted into their
class files' BODY lists, at their source position, so they sit in the middle of
`mr_rule_table`:

| record | cond |
|---|---|
| `1_4_1` r7 | `mr_simplify_flag` and `SumQ[u]` |
| `1_4_1` r8 | `SumQ[u]` |
| `9_1` r8 | `FreeQ[a, x]` (bare `a_`) |
| `9_1` r13 | `SumQ[u]` |
| `2_3` r96 | `FunctionOfExponentialQ[u, x]` and not a `MatchQ` shape |
| `3_5` r42 | `NonsumQ[u]` and `FunctionOfLog[Cancel[x u], x]` not false |

Found by a scan of `rules/class*/*.mac` for `(Int (Pattern <name> (Blank)) …)`.
The inert-trig substrate plan (Task 8) had assumed there were none.

## Why it may be unfaithful

Our dispatcher walks `mr_rule_table` in load order and takes the first rule
that answers. Mathematica orders `DownValues` by pattern SPECIFICITY: a bare
`Int[u_, x_Symbol]` is the most general `Int` pattern there is, so it is tried
after every more specific `Int` rule; rules with IDENTICAL left-hand sides keep
their load order among themselves. So the faithful placement is plausibly: every
specific rule of every class, then every bare-`u_` rule, in Rubi's `LoadRules`
order. (This is the argument the inert-trig spec §3.3 makes for the class-4
bridge records. It comes from Mathematica's documented ordering, not a
measurement against Mathematica.)

Today a class-1 or class-2 bare-`u_` rule is tried before every specific rule
of a later class. The one to look at first is `2_3` r96: if
`FunctionOfExponentialQ` holds for some class-3/6 integrand, that rule
intercepts it before the later class's own specific rules. Measured
2026-09-21 on ONE integrand only, the class-6 acceptance integrand
`sinh(c+d*x)*(a+b*sinh(c+d*x)^2)`: `%mr_functionOfExponentialQ` → `false` and
`%mr_sumQ` → `false`, so nothing intercepts that one. Nothing is known yet
about the rest.

## Why it was not changed in the substrate plan

Moving these records changes what classes 1/2/3/6 do, and those results are
accepted baselines. It needs a corpus A/B with every PASS→FAIL attributed. The
substrate plan applies the tail convention to NEW (class-4) records only. Its
static gate lists these six (key, n) as a closed, named exception list, so that
a seventh bare-`u_` record in a body list fails the gate.

## First moves

1. Once the tail mechanism has landed, move the six into the tail, in Rubi's
   `LoadRules` order (9.1 loads first). Regenerate, then A/B classes 1, 2, 3
   and 6 against their committed records with `test/ab_records.py`.
2. Attribute every transition. If the move is a net loss, check whether any
   deviation is intended (e.g. the `SumQ` split being early on purpose) before
   deciding.
3. Remove the gate's exception list once the six are in the tail.

2026-09-22 — **Related redundancy, same records**: `1_4_1` r7/r8 are the two
branches of one multi-line `If[TrueQ[$LoadShowSteps], <ShowStep rule>,
<plain rule>]` wrapper. The single-line unwrapper (class-3 decision C6b:
keep the plain branch) never saw the multi-line form, so both branches
were ported; r7 is the ShowStep branch (`mr_simplify_flag and ...`, always
true in the port), making r8 dead. The section-9 port adds a multi-line
unwrapper but scopes it to class 9 (spec
`docs/superpowers/specs/2026-09-22-section9-port-design.md` A2.2): applied
to class 1 it drops one record (3,054 -> 3,053,
`probes/translation/08-section9-generator-dryrun.py` part C notes it).
Whoever moves these records should drop the duplicate in the same A/B.
