# Section-9 port — design: Rubi's always-loaded 9.2 and 9.3 rules

Date: 2026-09-22. Designed on branch `master` @ `e2166be` (ticket 08, the
capture-trap fix, merged). Reference clones pinned at Rubi
`61e9c18ea248061cd83c67882f7c91a73cef912d` and MaximaSyntaxTestSuite
`60295e21c571ca210ecfbb695f4af99947454adf`. Maxima
`branch_5_50_base_84_g4204fb669` / SBCL 2.6.7. Design brainstorm with the
user 2026-09-22. Supersedes the scope of
`.scratch/class-ports/issues/06-section9-core-rules-9_2-9_3.md`.

## 0. Context

### 0.1 What section 9 is in the pinned Rubi

`Rubi.m` loads three section-9 files
(`probes/rubi/04-section9-load-and-legacy.out` §A):

| file | rules | `Rubi.m` | position |
|---|---:|---|---|
| 9.2 Piecewise linear functions | 19 | L204 | right after class 1, ALWAYS loaded |
| 9.1 Derivative integration rules | 21 | L354 | last file inside the `$LoadElementaryFunctionRules` block (classes 2-8) |
| 9.3 Miscellaneous integration rules | 76 | L356 | the last file loaded, ALWAYS loaded |

None of them is ported. The clone also holds four section-9 files `Rubi.m`
does not load: the December-2023 "posthumous release" (`f7fa0fd`)
renumbered the section and stopped loading `9.1 Integrand simplification
rules` (§B).

### 0.2 The legacy 9.1 file, and the standing policy it follows

`rules/class1/9_1.mac` (28 rules) is generated from the no-longer-loaded
`9.1 Integrand simplification rules.m`. That is deliberate: the
matcher-substrate design (`2026-09-12-matcher-substrate-design.md` §3.4)
kept it because the 2018 Rubi the Maxima-syntax corpus was generated with
loaded it, and the five `EXTRA_CLASS1` 1.2.1 `b` files are kept on the same
grounds. **The standing policy: port the pinned files, plus the legacy files
the 2018 corpus needs.** Of its 27 `Int[` left-hand sides, 12 moved into the
pinned `1.4.1 Algebraic function simplification` (§C). It is also the ONLY
source of constant-factor extraction (`Int[Complex[0,a]*u]`, `Int[a_*u_]`,
`Int[-u_]`): no loaded pinned file has such a rule (§D), and the class-6
bridge chain uses its r11 (`test_maxima_rubi.mac`, the inert-trig acceptance
target's comment).

### 0.3 Decisions made in the brainstorm (user, 2026-09-22)

1. **Scope: 9.2 and 9.3.** Port them from the pinned files.
2. **The legacy 9.1 stays**, under the standing policy (§0.2). (An earlier
   answer to remove it was given on a wrong premise, that its presence was
   undocumented; it was re-asked with the §3.4 record and changed to keep.)
3. **9.1 Derivative integration goes to class 8** (ticket 01). Its only
   corpus is `8 Special functions/8.10 Formal derivatives.mac` (94 entries,
   §E), it needs a representation of `Derivative[n][f][x]` that only that
   corpus can test, and `Rubi.m` loads it after class 8.
4. **Placement follows `Rubi.m` load order and the existing bare-`u_` tail
   convention** (§3.2).

## 1. Scope

In:
- `9.2 Piecewise linear functions` (19 rules) and `9.3 Miscellaneous
  integration rules` (76 rules), generated like classes 1-6 into
  `rules/class9/9_2.mac` and `rules/class9/9_3.mac`;
- every utility their conditions and replacements need, transitively
  (§3.3);
- the loader, the rules core, the static gates and Layer A for the new
  files;
- the four-class corpus measurement (§4).

Out:
- 9.1 Derivative integration (to ticket 01);
- any change to the legacy `rules/class1/9_1.mac`;
- the one 2018-era rule the pinned 9.3 dropped, old `9.4` L58
  `Int[x_^m_*u_, x] := With[{k=Denominator[m]}, k*Subst[Int[x^(k*(m+1)-1)*
  ReplaceAll[u, x->x^k], x], x, x^(1/k)]] /; FractionQ[m]` (§F: the only old
  left-hand side absent from its pinned successor; the pinned set keeps the
  specialised 1.1.x forms). It is a CANDIDATE legacy addition under §0.2 and
  is recorded on ticket 06 for measurement, not ported here.

## 2. Measured basis

- `probes/rubi/04-section9-load-and-legacy.{run,out}`: §A load lines and
  rule counts; §B the `f7fa0fd` renumbering; §C where the legacy 9.1
  left-hand sides went (12/27 into 1.4.1); §D constant-factor rules exist
  only in the legacy file; §E the formal-derivative corpus (94 entries, one
  file); §F old-numbered files against their pinned successors (every old
  left-hand side survives except old 9.4 L58).
- `probes/translation/07-section9-syntax-census.{run,out}`: the Step-1(a)
  census over the three loaded files, 116 rules. Its UNLISTED tokens,
  checked against the translation table and `maxima_rubi_utils.mac` on
  2026-09-22:

  | status | tokens |
  |---|---|
  | already ported | `FalseQ`, `DerivativeDivides`, `FunctionOfQ`, `NormalizeIntegrand`, `NonsumQ`, `SubstForFractionalPowerOfLinear` |
  | 9.1 Derivative only (out of scope) | `Derivative`, `F` |
  | missing | `PiecewiseLinearQ`, `Divides`, `EulerIntegrandQ`, `FunctionOfLinear`, `FunctionOfSquareRootOfQuadratic`, `PolynomialInQ`, `PolynomialInSubst`, `PowerVariableExpn`, `SimplerIntegrandQ`, `SubstForFractionalPowerOfQuotientOfLinears`, `SubstForFractionalPowerQ` |

  This is the census's first-level list. The closure (§3.3) is taken
  transitively and is expected to grow: the inert-trig substrate found five
  utility ports only through the utility file.

## 3. Design

### 3.1 Files and generation

A `configure(9)` path in `generator/generate_rules.py` reads the class-9
file list from `Rubi.m` (the two in-scope files, in load order) and writes
`rules/class9/9_2.mac` and `rules/class9/9_3.mac` with the same emitter as
classes 1-6: `%mr_defrule` records, prefixed With/Module locals (ticket 08),
`_tail` lists for bare-`u_` records. The legacy `NINE_ONE` path is
untouched. Regeneration is byte-stable (`--class 9` leaves `git status
--porcelain rules/` empty).

### 3.2 Rule-table placement

Rule priority is table order, and the table follows `Rubi.m` LoadRules
order, with bare-`u_` records collected in the tail (inert-trig substrate
design 3.3):

- **9.2 body**: immediately after the class-1 table (after the legacy
  `9_1`, which ends class 1) and before class 2 (`Rubi.m` L204).
- **9.3 body**: always the LAST body entry, after every class's body
  (today after class 6 and class 4's empty body; it stays last as classes
  5, 7 and 8 are ported). `Rubi.m` loads 9.3 last.
- **9.3 tail**: 9.3's bare-`u_` records go in the tail AFTER the eight
  class-4 bridge records, in load order. The pinned file has 18: 17
  `Int[u_,x_Symbol]` left-hand sides and one `Int[u_,x_]` (the
  generator's bare-`u_` test is authoritative).
- **9.3's global give-up.** The file's last record (L596) is
  `Int[u_,x_] := CannotIntegrate[u,x]`, Rubi's final catch-all. The
  dispatcher already classifies a `CannotIntegrate` replacement as a
  give-up (`mr-giveup-repl-p`; `CannotIntegrate` and `Unintegrable` map
  to the same package noun), so it is ported like any other record and
  becomes the LAST record of the tail. Two body records (L36, L42) also
  answer `Unintegrable[...]`; they are give-ups too, and they stay in the body.
- **Give-ups** run in a second pass after every ordinary rule, wherever
  they sit (`mr_giveup_last`, default true). Within that pass table order
  holds, so `4_7_5` r72 (which re-activates the inert trig heads) still
  runs before 9.3's catch-all, as in `Rubi.m`.

`mr_load_all` (and the rules core built from it) is the only loader that
changes. `test/test_rule_table_order.mac` changes with it:
- "the tail is exactly the eight bridge records" becomes "the tail is the
  eight bridge records followed by 9.3's 18 tail records, in load order";
- "`4_7_5` r72 is the tail's only give-up record" becomes "the tail's
  give-up records are exactly `4_7_5` r72 and 9.3's `CannotIntegrate`
  record, in that order, and the latter is the tail's last record";
- the body-before-tail and bare-`u_` checks stay as they are, and a new
  check asserts that 9.3's body is the last body entry.

### 3.3 Utilities and the dependency closure

Runbook Step 1c, before any generation: starting from the §2 missing list,
walk every call through `IntegrationUtilityFunctions.m` until no new name
appears. Each name is then one of:

- a translation-table entry (a Maxima builtin or an existing port);
- a hand port in `maxima_rubi_utils.mac`;
- upstream-undefined: the call-site contract with documented decline-safe
  semantics (the class-2 `PowerOfLinear` precedent).

The completed closure table is written into this spec's amendments before
any port starts.

Every hand port obeys the three wrong-not-failing Maxima traps
(inert-trig substrate amendments; ticket 08): prefix every bound name
(block local, loop variable, lambda parameter); read operators with
`inflag:true`; never rely on `is(equal(b, 0))` for a free symbol. A
utility that re-evaluates an expression (`ev`) is flagged in review.

### 3.4 Static gates

- `test/check_generated_rules.py`: class 9 is a post-P0 class, so it is
  covered by check 7 (the generator's `EXPECTED_TOTAL` for class 9, 95) and
  check 6 (every pattern prepares); checks 1-5 over classes 1-3 are
  unchanged, since no class-1/2/3 file changes.
- The closed bare-`u_` exception list (six records, ticket 07) does not
  change: none of the new records is a mid-table bare-`u_` record.

## 4. Measurement

1. **Re-baseline first, on a quiet host.** The accepted records predate
   ticket 08, and its full-run records were taken under an emulator's load
   (ticket 08, Measurement). Before 9.x lands, run classes 1, 2, 3 and 6 on
   `master` with the queue runner at **24 workers for every class** (user
   decision 2026-09-22: the accepted class-1 record's worker count; this is
   above the 12 physical cores, so step 2 must use the same count for the
   A/B to hold concurrency constant), on a host with nothing else heavy
   running. These are the reference records for step 2 and the candidate
   official records for ticket 08 (promotion is the user's decision).
2. **9.2 + 9.3**: the same four classes on the branch, same conditions,
   A/B'd against step 1 with `test/ab_records.py`.
3. **Attribution**: every entry whose verdict changed is rerun as a PAIRED
   run (step-1 core and branch core concurrently, same load) for VERDICT
   attribution; any TIMING claim comes only from alternating sequential
   runs (memory: timing-ab-alternate-not-concurrent). Every PASS->FAIL is
   attributed before acceptance.
4. **Run discipline**: steps 1-3 are chained in one detached script, so the
   paired rerun starts when the last class merges.

## 5. Tests

- Layer A: unit targets for every hand-ported utility, each RED before its
  port; end-to-end targets per new file, at least: 9.3's derivative-divides
  rule on `2 Exponentials/2.3` e733 `(1+%e^x)/(%e^x+x)` (ticket 06's
  motivating example, `deferred` today) answering `log(%e^x+x)`; one 9.2
  piecewise-linear target (a `PiecewiseLinearQ` integrand); and one target
  that exercises 9.3's `Int[u_, x] := Int[SimplifyIntegrand[u, x], x] /;
  SimplerIntegrandQ[...]` tail record. Each is RED against `master`.
- `test/test_rule_table_order.mac`: updated per §3.2.
- `test/check_generated_rules.py`: green with the class-9 check-7 line.
- The harness guards and matcher suites stay green (no harness or matcher
  change is planned).

## 6. Acceptance

- All gates green; counts recorded in AGENTS.md.
- The step-2 records A/B'd against step 1 with every PASS->FAIL attributed.
- Tickets: 06 closed (with old 9.4 L58 recorded as a candidate legacy
  addition), 01 carries 9.1 Derivative with §0.3.3's evidence.
- Promoting records is the user's decision, not part of acceptance.

## 7. Risks

- **The closure is larger than the census shows.** Mitigation: §3.3 is
  complete before porting starts.
- **9.3's bare `SimplifyIntegrand` record changes routing broadly.** It is
  a tail record that fires on any integrand every other rule declined, so it
  can turn today's `deferred`/`contains-noun` answers into new paths, and
  cost time. The step-2 A/B measures it; runaway growth shows as new
  `timeout`s.
- **Interaction with the legacy 9.1.** Both carry simplification rules. The
  legacy file sits earlier in our table (the end of class 1), so it keeps
  priority where both apply. That is NOT the 2018 placement: the
  pre-renumbering `Rubi.m` (`f7fa0fd^`, L100) loads 9.1 Integrand
  simplification FIRST, before 1.1.1.1. Moving it is out of scope here and
  is recorded as its own ticket, to be measured before it moves.
- **Hand-port traps.** §3.3's three traps each produced plausible wrong
  answers, not errors, in the last two campaigns.

## 8. Process

This spec, then a plan (`superpowers:writing-plans`) executed on a branch
`section9-port` with subagent-driven development, per-task review, and a
final review before merge. The runbook (`docs/class-porting.md`) applies
from Step 1c.

## Amendments

### A1. The dependency closure (2026-09-22, before the plan)

`probes/rubi/05-section9-utility-closure.{py,run,out}` walks the eleven
missing names of §2 through `IntegrationUtilityFunctions.m`, following a
name whether it is called (`Name[`) or passed as a value
(`Map[Name, lst]`). The result is **40 missing utilities** (0 unknown),
which call 11 utilities that are already ported (`CalculusQ`, `NonfreeTerms`,
`FreeTerms`, `SubstForFractionalPower`, `FractionalPowerQ`, `EveryQ`, `LogQ`,
`ComplexNumberQ`, `NumericFactor`, `NonnumericFactors`, `OrderedQ`). The 40
fall into six groups, and each group is one plan task:

| group | entry points (called by rules) | helpers |
|---|---|---|
| G1 piecewise / quotient | `PiecewiseLinearQ`, `Divides` | — |
| G2 structural predicates | `EulerIntegrandQ`, `SimplerIntegrandQ`, `SubstForFractionalPowerQ`, `PolynomialInQ`, `PolynomialInSubst` | `CancelCommonFactors`, `SubstForFractionalPowerAuxQ`, `PolynomialInAuxQ`, `PolynomialInSubstAux` |
| G3 power variable | `PowerVariableExpn` | `PowerVariableDegree`, `PowerVariableSubst` |
| G4 square root of quadratic | `FunctionOfSquareRootOfQuadratic` | `SquareRootOfQuadraticSubst` |
| G5 quotient of linears | `SubstForFractionalPowerOfQuotientOfLinears` | `FractionalPowerOfQuotientOfLinears` |
| G6 function of linear | `FunctionOfLinear` | `FunctionOfLinearSubst`, `MonomialFactor`, `MinimumDegree`, `DivideDegreesOfFactors`, `LeadFactor`, `LeadBase`, `LeadDegree`, `RemainingFactors`, `CommonFactors`, `Smallest`, `MostMainFactorPosition`, `FactorOrder`, `Map2`, `ReapList`, `AbsurdNumberQ`, `AbsurdNumberFactors`, `NonabsurdNumberFactors`, `AbsurdNumberGCD`, `AbsurdNumberGCDList`, `FactorAbsurdNumber`, `CombineExponents` |

Each name is a hand port in `maxima_rubi_utils.mac` under `%mr_<name>`,
except two:
- `Map2` and `ReapList` are Mathematica list plumbing (`Reap`/`Sow` over a
  `Do`). `CommonFactors` uses Maxima's `map(f, l1, l2)` in their place and
  records that in a comment. They get no `%mr_` port.
- `FactorOrder` wraps Mathematica's `Order`, whose canonical order is not
  Maxima's. The port uses `ordergreatp`/`orderlessp`, and the comment
  records the deviation. It decides only which factor `CommonFactors`
  treats as "most main" when no other branch applies, so a different choice
  changes the form of a common factor, not whether one is found.

The closure is larger than §2's first-level list (11 names) because of G6.
`FunctionOfLinear` calls `CommonFactors`, which calls Rubi's
"absurd number" family.

### A2. Generator gaps (2026-09-22)

`probes/translation/08-section9-generator-dryrun.{py,run,out}` runs the
unchanged emitter over 9.2 and 9.3 (writing only to a temporary
directory). Besides the 11 unlisted heads of §2, it stops on four
structural gaps. Each is a generator change in the plan:

1. **A whole-line comment inside a multi-line condition** (9.2 r12, the
   `(* ILtQ[n,0] && ... || *)` line). Comment stripping leaves a blank
   line, and `rule_runs` splits rules at blank lines, so the condition is
   cut in half. Fix: drop comment-only lines before stripping. Measured
   byte-neutral: classes 1/2/3/6 regenerate identical, 100 files (probe
   part C).
2. **The multi-line `If[TrueQ[$LoadShowSteps], <ShowStep rule>, <plain
   rule>]` wrapper** (nine in 9.3). The single-line unwrapper
   (`unwrap_showsteps_line`, class-3 decision C6b: keep the plain branch)
   does not see it. Fix: reduce each wrapper to its plain branch. This is
   **scoped to class 9**: class 1's `1_4_1.mac` carries both branches of
   the same wrapper (r7/r8), and making the fix general changes that file
   (3,054 → 3,053 rules), which §1 rules out. The redundancy in 1.4.1 is
   recorded on ticket 07's family, not fixed here.
3. **`v=!=u` (UnsameQ)** in 9.3's `NormalizeIntegrand` record. The walk
   reads it as `=` followed by `!=`. Fix: an `=!=` emitter case producing
   `%mr_unsameQ(v, u)`, a syntactic `not(is(a = b))`. No class-1/2/3/6
   `.m` file uses `=!=`, so nothing already generated changes.
4. **`Int[u_,x_]`**, 9.3's final give-up, written with `x_`, not
   `x_Symbol`. Fix: accept it and emit the `x_Symbol` pattern. The
   dispatcher always passes a symbol as `x`, so the two match the same
   calls here. This also keeps the record a bare-`u_` pattern
   (`(Pattern x (Blank Symbol))`), which the tail convention and
   `test/test_rule_table_order.mac` rely on.

With stand-ins for these four and placeholder rows for the 11 heads, the
emitter produces **86 records**, and every pattern string prepares in
MR-MATCH (86/86, probe part D).

### A3. Corrected counts, and the tail (supersedes §1, §3.2 and §3.4 where they differ)

- **9.3 is 67 rules, not 76.** `grep -c '^Int\['` counts both branches of
  the nine ShowSteps wrappers. The port keeps one per wrapper (A2.2).
  Class 9 is therefore **19 + 67 = 86**, and the generator's
  `EXPECTED_TOTAL` for class 9 is 86. The census's 116 double-counts the
  same nine wrappers.
- **The 9.3 tail is 11 records, not 18**: r9, r37, r38, r51, r55, r56,
  r57, r62, r63, r66, and r67, the `CannotIntegrate` give-up, which is
  last. Seven of the 18 counted in review were the ShowStep duplicates.
- **9.3's body interleaves with its tail**. Body records r64 and r65 come
  after tail record r63 in the file, so they are *registered* after some
  tail records. The dispatcher walks list order, not handle order
  (`%mr_dispatch_tree`), so the table is still correct. But
  `test/test_rule_table_order.mac`'s check "every tail handle is registered
  after every body handle" becomes false and is replaced by a check on
  list position: every tail handle's position in `mr_rule_table` is
  greater than the position of every body handle. Its other changes are
  the ones §3.2 lists, with the tail being the eight bridge records
  followed by the eleven 9.3 records above, and the give-up pair being
  `4_7_5` r72 and `9_3` r67.
- 9.3 r3/r4 (L36/L42, `Unintegrable[...]` answers) are body give-ups.

### A4. End-to-end targets, measured RED (2026-09-22)

`probes/rubi/06-section9-red-targets.{mac,run,out}` (`641e0e1`, build
`branch_5_50_base_84_g4204fb669`, SBCL 2.6.7):

| target | rule | master |
|---|---|---|
| `atan(tan(x))` | 9.2 r1 (`PiecewiseLinearQ`, `{ArcTan,Tan}`) | `unintegrable` |
| `(1+%e^x)/(%e^x+x)` (2.3 e733) | 9.3 derivative-divides | `unintegrable` |
| `%e^x*(1+x)/(x*%e^x+1)` | 9.3 derivative-divides | `unintegrable` |
| `1/(x+sqrt((1+x)/(1-x)))` | 9.3 `SubstForFractionalPowerOfQuotientOfLinears` | `unintegrable` |
| `x/(1+sqrt(2+3*x))` | 9.3 r38 (`SubstForFractionalPowerOfLinear`) | `'unintegrable[(3*x)/(sqrt(3*x+2)+1), 3*x+2]/9` |
| `log(2*%e^x)^2` (control) | — | `log(2*%e^x)^3/3` |

These replace §5's target list. §5's "one target that exercises the bare
`SimplifyIntegrand` record" stays, with its integrand found during the
plan from `rubi_verbose` traces, because no measured RED candidate is
known to reach r9.

The r38 row shows an existing `master` defect: the answer is a noun whose
integration variable is `3*x+2`, an expression. A substitution rule
rewrote the variable slot of an `unintegrable` noun. It is out of scope
here. The port may change that entry's route (the tail's r38 could answer
the inner integral), and the plan records what happens to it.

### A5. End-to-end results (2026-09-22, `346c513` + this commit)

`test/test_section9_e2e.mac`: **`Results: 4 passed, 0 failed`** (5.4 s wall,
build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7). Run it with stdin from
`/dev/null` — see "The ldb trap" below.

| target | route (verbose-traced) | answer |
|---|---|---|
| `atan(tan(x))` | 9.2 r1 | `(tan(x)^2+1)*atan(tan(x))^2/(2*sec(x)^2)` |
| `(1+%e^x)/(%e^x+x)` (2.3 e733) | 9.3 derivative-divides | `log(x+%e^x)` |
| `%e^x*(1+x)/(x*%e^x+1)` | 9.3 derivative-divides | `log(%e^x*x+1)` |
| `1/(1+sqrt((1+x)/(1-x)))` | **9_3 r38** (`SubstForFractionalPowerOfQuotientOfLinears`) | `-(2*log(sqrt(-((x+1)/(x-1)))+1)+(x-1)*sqrt(-((x+1)/(x-1)))-x-log(-(2/(x-1)))+1)/2` |

Each verifies at `x = 0.3` and `x = 0.7` to under `1.0e-10`.

**A4's fourth integrand is replaced, and why.** A4 lists
`1/(x + sqrt((1+x)/(1-x)))` for the `SubstForFractionalPowerOfQuotientOfLinears`
record. The record fires on it and substitutes CORRECTLY —
`%mr_substForFractionalPowerOfQuotientOfLinears(1/(x+sqrt((1+x)/(1-x))), x)`
returns `[x/(x^5+x^4+2*x^3+x-1), 2, (x+1)/(1-x), 2]` — but the rational integral
it leaves, `2*x/((x^2+1)*(x^3+x^2+x-1))`, never returns: it allocates until the
SBCL heap is exhausted and the runtime dies (`Heap exhausted, game over`), at
394.7 s on this branch and at **402.2 s on `master`**, where no class-9 rule is
loaded at all. So it is a pre-existing class-1 cost that section 9 merely gives
a new route to (`.scratch/class-ports/issues/11-class1-heap-exhaustion-quintic-rational.md`).
The gate therefore uses `1/(1 + sqrt((1+x)/(1-x)))`, which `rubi_verbose` shows
going through the same record (`rubi: rule 9_3 r38 fired on 1/(sqrt((x+1)/(1-x))+1)`),
is equally RED on master (`'unintegrable[1/(sqrt((x+1)/(1-x))+1),x]`, measured),
and answers in 2 s. (A4's own row labels `9_3 r38` as
`SubstForFractionalPowerOfLinear`; in the generated table r37 is
`SubstForFractionalPowerOfLinear` and **r38** is
`SubstForFractionalPowerOfQuotientOfLinears`.)

**The `ldb` trap.** The first attempt at this task reported the gate as a hang:
no output, no CPU, both SBCL threads parked in `futex_do_wait`. It was not a
hang. A fatal SBCL error drops into the `ldb` low-level debugger, which reads
from stdin, so with an inherited terminal stdin the dead process sits there
forever. Redirecting stdin from `/dev/null` turns it into a visible
`Heap exhausted, game over` — the same reason the dispatch suite is run
`< /dev/null` and the corpus driver gives entry subprocesses `/dev/null`
(AGENTS.md; `probes/matcher/09-harness-fault-verdict.out`). Note also that
`timeout` does not kill maxima's `sbcl` grandchild: use `setsid` + `killpg`.

**Step 3, the `SimplifyIntegrand` record (9.3 r9): no target found, gate stays
at 4.** Each of §5/A4's four candidates was run on the full table with
`rubi_verbose`; all four are answered by an EARLIER body record, so the tail's
r9 is never reached (it does not even appear as a decline):

| candidate | answered by | answer |
|---|---|---|
| `(x^2-1)/(x-1)*%e^(x^2)*x` | `1_4_1 r1` | `-sqrt(%pi)*erfi(x)/4+%e^(x^2)*x/2+%e^(x^2)/2` |
| `(x^3-1)/((x-1)*(x^2+x+1)^2)` | `1_4_1 r18` | `2*atan((2*x+1)/sqrt(3))/sqrt(3)` |
| `(%e^(2*x)-1)/((%e^x-1)*(%e^x+1))` | `2_3 r96` | `x` |
| `((x+1)^2-x^2-2*x)/(x^2+1)` | `1_4_1 r18` | `atan(x)` |

That is A4's stated fallback: r9's reach is left to the Task 13 corpus A/B.

**Step 4, the r38 observation entry `x/(1+sqrt(2+3*x))`.** On `master` it
reproduces A4 exactly: `'unintegrable[(3*x)/(sqrt(3*x+2)+1),3*x+2]/9` in 2 s.
On this branch it **no longer returns**: 280.5 s and then
`Heap exhausted, game over`. The trace's last two firings are `9_3 r18` on
`((sqrt(x)+1)*x-2*sqrt(x)-2)/(sqrt(x)+1)^2` and then `9_1 r28` on the same
expression with the square expanded. This is a section-9 REGRESSION for that
entry, and its cause is a port defect in the record, below.

**Found while tracing Step 4 — 9.3 r18/r22/r23/r24 are unguarded and leak
(`.scratch/class-ports/issues/13-9_3-condition-assignment-idiom-q-r.md`).**
These four records use Rubi's condition-assignment idiom
(`... /; Not[FalseQ[r=Divides[...]]] && Not[FalseQ[q=DerivativeDivides[...]]]`,
with `q*r` on the right-hand side). The generator emitted `=` as Maxima
EQUALITY, so (1) `%mr_falseQ(<equation>)` is never true and the guard is
VACUOUS — the record fires whenever its pattern matches — and (2) the repl
re-declares `q`/`r` as fresh unassigned block locals, so the answer is
multiplied by two unbound symbols. Witness, measured:
`rubi(((sqrt(x)+1)*x-2*sqrt(x)-2)/(sqrt(x)+1)^2, x)` returns
`_mr_9_3_r18_q*_mr_9_3_r18_r*<degree-49 rational mess>` on this branch, against
a 2 s `unintegrable` on master. A scan of every generated rule file
(`grep -o "%mr_falseQ(_mr_[A-Za-z0-9_]*=" rules/class*/*.mac`) finds this shape
in exactly these four records and nowhere else. It is NOT fixed here — Task 12
regenerates no rule file — but the gate now rejects any answer containing a
symbol whose name starts `_mr_` (`mr_e2e_no_locals`, the one addition to the
brief's gate code), so a fix can be pinned by adding a target that routes
through r18.

### A6. The measured result (2026-09-23) — §6 acceptance

**Stamp.** Reference arm: worktree `../mr-s9-ref` at `master` `c95c6ed`, core
fingerprint `0182d32c`, 3,911 rules. Branch arm: `section9-port` `1f31a27`,
core fingerprint `434c241a`, 3,997 rules. Both arms: queue runner, 24 workers
(§4's user decision), 30 s **cpu** cap, switches `mr_flat_wide=false
mr_cond_retry=true mr_model_flags=true mr_nested_fallback=false
mr_giveup_last=true mr_max_depth=16`. `build_info()`: Maxima
`branch_5_50_base_84_g4204fb669`, build date 2026-08-31 13:27:47,
`x86_64-pc-linux-gnu`, SBCL 2.6.7. Quiet host (the script refuses above
1-minute load 2). Chain `test/section9_measure.sh`, launched 2026-09-22
23:55 CEST, `ALL DONE` 2026-09-23 06:51 CEST; log `test/section9_measure.log`.

**Records.** `test/corpus_class{1,2,3,6}.s9-ref.out` and `.s9.out`; the A/B
`test/section9_ab_class{1,2,3,6}.out`; the paired rerun of every entry whose
verdict class changed, both cores concurrently at 12 workers each,
`test/section9_paired_class{N}.{ref,new}/`; the give-up experiment
`test/section9_giveup_arm_class{N}.out`; the attribution itself,
`python3 test/section9_attribution.py` -> `test/section9_attribution.out`.

**Probes.** Every traced claim below has a committed, re-runnable probe under
`probes/section9/` (research discipline, AGENTS.md). Each takes its arms from
the two rules cores — `test/mr_rules.core` and `../mr-s9-ref/test/mr_rules.core`
— and each runs its Maxima with stdin from `/dev/null` (the `ldb` trap, A5).

| probe | what it measures | amendment |
|---|---|---|
| `01-giveup-ordering.{mac,run,out}` | `3.4` e635 and e104 on both cores and with `mr_giveup_last=false`: which rule fires, and whether the noun is top level | A6.1 |
| `02-inert-leak.{mac,run,out}` | `6.3.2` e13 on both cores: which rule fires, and which inert heads the answer carries | A6.2 |
| `03-r41-bisect.{mac,run,out}` | the 16-arm bisection of 9.3 over `1.3.1` e190, one Maxima per arm under `timeout` | A6.3 |
| `04-route-rules.{mac,run,out}` | the ten route entries on both cores, plus `%mr_expandIntegrand` on two of them | A6.4 |
| `05-timing-ab.run` -> `.out` | the ALTERNATING SEQUENTIAL timing A/B (this file is what `section9_attribution.py` reads) | A6.3 |
| `06-giveup-switch-control.{py,run,out}` | what turning `mr_giveup_last` OFF costs on a seeded class-1 control sample, both arms at the same worker count | A6.1 |

**The core the measurement ran on.** `test/mr_rules.core.stamp` as written
during the Task-13 run said `git_dirty 1`, because the run's own untracked
records were in the tree while the core was built. Rebuilt on the clean tree at
`f547a03` (`sh test/build_rules_core.sh`): fingerprint
`434c241ad6c11e1b152b9b1bc1469214`, `rules 3997`, `git_dirty 0` — **identical
fingerprint**, so the measured core is the committed tree's rule set. (The
fingerprint is computed over the rule files, which untracked records do not
touch.)

#### A6.0 The result

| class | entries | PASS ref | PASS branch | net | F->P | P->F |
|---|---|---|---|---|---|---|
| 1 Algebraic | 25,697 | 18,170 | 18,409 | **+239** | 254 | 15 |
| 2 Exponentials | 965 | 716 | 749 | **+33** | 43 | 10 |
| 3 Logarithms | 3,085 | 1,673 | 1,577 | **-96** | 22 | 118 |
| 6 Hyperbolic | 5,080 | 1,630 | 2,281 | **+651** | 813 | 162 |
| all four | 34,827 | 22,189 | 23,016 | **+827** | 1,132 | 305 |

Ticket 06's motivating entry, `2 Exponentials/2.3` e733 `(1+%e^x)/(%e^x+x)`:
`deferred` -> **`verified`** in 0.4 s, through 9.3's derivative-divides rule,
exactly as the ticket predicted (`test/corpus_class2.s9.out`).

**New `timeout`s (§7's `SimplifyIntegrand` risk).** `contains-noun -> timeout`
/ `deferred -> timeout`: class 1 258 / 128, class 2 11 / 3, class 3 104 / 25,
class 6 384 / 391. Every one of these was already FAIL. The cost of the entries
that verify in BOTH arms is essentially flat: total cpu over them 41,949 ->
43,012 s (1.03x) in class 1, 982 -> 1,055 s (1.07x) in class 2, 3,262 ->
3,400 s (1.04x) in class 3, 3,997 -> 4,287 s (1.07x) in class 6; median
per-entry ratio over entries of 1 s or more 1.02 / 1.08 / 1.04 / 1.07. So the
new records' much larger whole-record totals are entries that used to give up
early and now run to the cap, not a broad slowdown.

#### A6.0.1 Attribution of all 305 PASS->FAIL

`test/section9_attribution.out`. Nothing is unattributed.

| cause | count | class 1 / 2 / 3 / 6 |
|---|---|---|
| A6.1 give-up ordering | 189 | 0 / 9 / 115 / 65 |
| A6.2 inert-head leak | 89 | 0 / 0 / 0 / 89 |
| 30 s cap boundary | 12 | 8 / 0 / 0 / 4 |
| A6.3 cost | 5 | 5 / 0 / 0 / 0 |
| A6.4 route | 10 | 2 / 1 / 3 / 4 |

13 of the 89 inert-leak entries are ALSO recovered by the give-up experiment;
the script counts each entry once, under the leak.

**Cap boundary (12).** Each is `verified`/`expected` at 27.9-30.0 s on the
reference core and 30.0-30.1 s on the branch. What was measured for each:

- **2 of the 12** have a sequential timing row that puts the branch inside the
  30 s cap at essentially the reference cost — `1.2.1.2` e404 21.5 -> 21.9 s,
  `1.2.1.3` e1154 21.8 -> 22.3 s (probe 05). For these two the rule set is
  ruled out as the cause.
- **The other 10** rest on the paired rerun at 12 workers: the BRANCH core
  verifies the entry there (`1.1.1.3` e1100, `1.2.1.3` e1276, `1.2.1.4` e341,
  `1.2.2.3` e259/e260 and class 6's `6.1.3` e69/e80, `6.1.7` e339, `6.3.7`
  e191), or the REFERENCE core already fails it there (`1.2.1.3` e969). That
  shows a lower-contention run of the SAME branch core gets them, which is
  consistent with the cap deciding them; it does NOT measure their cost against
  the reference core, and no sequential row was taken for them.

All 12 also return to a PASS class in the give-up experiment, but that arm ran
at 12 workers rather than the record's 24, so it cannot separate the switch from
the lower contention and is not used for them.

#### A6.1 The give-up ordering defect — 189 entries, the whole of class 3's loss

Every one is an entry whose corpus answer is `Unintegrable` /
`CannotIntegrate`: the reference answers the top-level noun (`no-answer`, a
PASS class) and the branch answers a partially reduced expression carrying the
marker INSIDE it (`contains-noun`), or runs to the cap on the way.

MEASURED: the branch core over exactly the 305 PASS->FAIL entries with
`mr_giveup_last=false` and nothing else changed (12 workers, 30 s cpu cap,
`test/section9_giveup_arm_class{N}.out`) puts 189 of them back in a PASS class
— 115 of class 3's 118, 9 of class 2's 10, 65 of class 6's 162 — plus 13 of the
89 leak entries.

That arm ran at 12 workers against the record's 24, so for an entry whose
branch symptom is a TIMEOUT the lower contention could be part of why it
finishes. 182 of the 189 are not of that kind: their branch verdict is
`contains-noun`, a verdict CLASS that contention cannot turn into `no-answer`.
The remaining 7 (class 3, `no-answer -> timeout`, 30.0-30.1 s on the branch
against 1.2-2.7 s on the reference) are the ones where the confound is open;
they are PASS->FAIL caused by the port either way.

CAUSE. `mr_giveup_last` (default true, `maxima_rubi_dispatch.lisp`) walks the
table in two passes: pass 1 skips every give-up rule (a replacement answering
`mr_unintegrable`), pass 2 runs them. It exists because our table is LOAD order
where Mathematica's is SPECIFICITY order, so a general give-up that loads early
must not pre-empt a specific rule that loads late. Section 9.3 inverts the
premise: its tail contributes TEN non-give-up bare-`u_` records (r9, r37, r38,
r51, r55, r56, r57, r62, r63, r66 — r67, the `CannotIntegrate` catch-all, is
the eleventh and IS a give-up), and pass 1 now reaches them before pass 2
reaches the 72 `Unintegrable` marker rules of classes 1/2/3. In Mathematica
those marker rules are SPECIFIC patterns and beat `Int[u_, x_Symbol]`; here
they lose.

WITNESS — probe `probes/section9/01-giveup-ordering.{mac,run,out}`,
`rubi_verbose` on both cores and on the branch core with the switch off.
`3 Logarithms/3.4` e635 `(a+b*log(c*(d+e/(f+g*x))^p))^n`, corpus
`Unintegrable`, Rubi step count **0** (Rubi applies no rule at all):

| core | route | answer |
|---|---|---|
| reference `0182d32c` | the whole table declines, then the give-up pass: `3_4 r39` | `unintegrable((a+b log(c (d+e/(f+g x))^p))^n, x)` — `no-answer`, PASS |
| branch `434c241a` | pass 1 reaches the 9.3 tail: **`9_3 r51`** (`FunctionOfLinear`) substitutes `x -> (x-f)/g`; the inner integral falls to `3_4 r6`'s marker | `unintegrable((a+b log(c((d g x+d f+e)/(g x+f))^p))^n, g x+f)/g` — `contains-noun`, FAIL |

`3.4` e104 `1/(x*log(c*(a+b*x^2)^p))` is the same shape with a different 9.3
record: the reference answers the top-level noun through `3_4 r14`, the branch
fires **`9_3 r52`** (`PowerVariableExpn`) and buries the marker. With
`mr_giveup_last:false` the branch core answers the clean top-level noun for
both entries (probe 01's third arm).

**What flipping the switch off would cost — measured, not quoted.** The
switch's docstring does NOT say the switch recovers 318 class-1 entries. It says
the opposite about the switch alone: "reordering ALONE recovers nothing, because
the seen-cut self-recursion of `1_2_3_5` r12 blocks the same path first", and
the 318-of-341 figure is the measurement of a **PAIR** — the reordering together
with the seen-cut fall-through (`%mr_top_body`). So the switch's own cost had to
be measured. Probe `probes/section9/06-giveup-switch-control.{py,run,out}` runs
a seeded random sample (seed 20260923) of 2,000 class-1 entries that PASS in
the branch record, twice on the BRANCH core at the same worker count (12) and
the same 30 s cpu cap, differing only in `mr_giveup_last`:

| arm | PASS of 2,000 |
|---|---|
| `mr_giveup_last=true` (shipping) | 2,000 |
| `mr_giveup_last=false` | **1,936** |

**64 entries lost, 0 gained**, and every loss is a verdict-CLASS change, not a
cost one — 62 `verified -> contains-noun` and 2 `verified -> deferred`, with 0
going to `timeout`, so contention plays no part. That is 3.2 % of a class-1
PASS sample; the switch is carrying real answers and must not simply be turned
off.

The indicated fix is a THIRD tier — ordinary rules, then give-up rules, then the
bare-`u_` last-resort records — or equivalently keeping the 9.x bare-`u_` tail
out of pass 1. It is a dispatcher change, not a re-port. Ticket
`.scratch/class-ports/issues/14-giveup-last-vs-9_3-bare-u-tail.md`.

#### A6.2 The inert-trig head leak — 89 entries, all class 6, 69 of them previously CORRECT

**281 of the branch's class-6 answers carry one of the six inert trig heads**
(over the paired rerun's 286: `%mr_isin` 112, `%mr_itan` 92, `%mr_icsc` 46,
`%mr_icos` 32, `%mr_isec` 2, and 2 with two heads). The reference core produced
ZERO. The driver classifies such an answer `error`
(`test/test_driver_inert_leak.py`), and EVERY `error` in the branch's class-6
record is one of these; 89 were PASS before — **39 `verified`**, **30
`expected`**, 20 `no-answer` — and all 69 of the previously-CORRECT ones carry
`%mr_itan` (the `(b tanh)^(n/2)` and `(b coth)^(n/2)` families, 6.3.2 / 6.4.2).

WITNESS — probe `probes/section9/02-inert-leak.{mac,run,out}`. `6.3.2` e13
`(b*tanh(c+d*x))^(7/2)` (corpus: a closed form in 7 steps), `rubi_verbose` on
both cores:

- reference: `4_1_0_1 r1` deactivates the trig, `4_7_5 r22` (the pure-tan
  substitution) answers, the answer verifies.
- branch: `4_1_0_1 r1` deactivates, then **`9_3 r41`** — Rubi's
  `Int[u_.*(a_.*v_^m_.)^p_,x] := a^IntPart[p]*(a*v^m)^FracPart[p]/v^(m*FracPart[p]) * Int[u*v^(m*p),x]`
  — fires on the DEACTIVATED integrand `(-%i*%mr_itan(%i*(c+d*x)))^(7/2)` and
  emits `(-%i)^IntPart(p)*(-%i*%mr_itan(...))^FracPart(p)/%mr_itan(...)^FracPart(p)`
  as a factor OUTSIDE the recursive `mr_int`. Nothing re-activates that factor,
  so the answer reads
  `-(b^3 sqrt(b tanh(d x+c)) sqrt(-%i %mr_itan(%i d x+%i c))(...))/(20 d sqrt(tanh(d x+c)) sqrt(%mr_itan(%i d x+%i c)))`.

The rule's condition is a byte-faithful port of its upstream line. The defect is
that a class-9 BODY record is reachable INSIDE the class-4 inert domain, where
only class-4/6 records (which re-activate as they emit) are meant to run, and
where Mathematica would try 4.3.2's specific `Int[(b_.*tan[c_.+d_.*x_])^n_,x_]`
rules first. Class 4 is not ported, so our table has nothing between the
deactivation and 9.3's body.

The leaked expression is not a WRONG antiderivative — re-activating `%mr_itan`
would give a correct one — but `%mr_itan` has no meaning outside the bridge, so
the answer cannot be differentiated, verified or used. Ticket
`.scratch/class-ports/issues/15-class9-body-rules-leak-inert-trig-heads.md`.

#### A6.3 Cost — 5 class-1 entries, and one rule behind them

Probe `probes/section9/05-timing-ab.run` -> `probes/section9/05-timing-ab.out`,
ALTERNATING SEQUENTIAL (one entry at a time, one process at a time, reference
core then branch core, 120 s cpu cap) — never the concurrent pair (memory:
timing-ab-alternate-not-concurrent). `test/section9_attribution.py` reads this
file to split the `cap` and `cost` buckets:

| entry | reference | branch | ratio | bucket |
|---|---|---|---|---|
| `1.2.1.2` e335 | 18.0 s verified | 27.8 s verified | 1.54x | cost |
| `1.2.1.4` e585 | 18.4 s verified | 43.0 s verified | 2.34x | cost |
| `1.2.1.9` e61 | 19.2 s verified | 29.1 s verified | 1.52x | cost |
| `1.3.1` e190 | 1.7 s verified | **>120 s timeout** | >70x | cost |
| `1.3.1` e238 | 6.2 s verified | **>120 s timeout** | >19x | cost |
| `1.2.1.2` e404 | 21.5 s verified | 21.9 s verified | 1.02x | cap |
| `1.2.1.3` e1154 | 21.8 s verified | 22.2 s verified | 1.02x | cap |

The last two are the reason this probe covers seven entries and not five: the
paired rerun could not tell them apart from the five, and the sequential rows
put them at the reference cost, so they are `cap`, not `cost`.

The first three are entries already near the cap that the branch pushes over.
`1.3.1` e190 `x*(2*c+3*d*x)*(a+c*x^2+d*x^3)^n` and e238 are different in kind,
and the cause is **`9_3 r41` again**. Bisected on the branch core by removing
handles from `mr_rule_table` and timing `rubi` — probe
`probes/section9/03-r41-bisect.{mac,run,out}`, 16 arms, one Maxima process per
arm under `timeout`, arms that do not return recorded HUNG:

| arm (9.3 handles KEPT) | elapsed |
|---|---|
| `none-removed` — the shipping table | **HUNG** (no return inside 90 s) |
| `all-9_3-out` | 2.09 s, answer `(a+c x^2+d x^3)^(n+1)/(n+1)` |
| `body-out` (9.3 tail kept) | 15.88 s, same answer |
| `tail-out` (9.3 body kept) | **HUNG** |
| `body-first-28` | 1.86 s |
| `block-r30-r36` / `block-r46-r53` / `block-r54-r65` | 1.91 / 1.76 / 1.77 s |
| `block-r39-r45` | **HUNG** |
| `only-r39` / `only-r40` / `only-r42` / `only-r43` / `only-r44` / `only-r45` | 1.81 / 1.78 / 1.76 / 1.77 / 1.77 / 1.76 s |
| **`only-r41`** | **HUNG** |

So the 9.3 tail costs about 14 s on this entry on its own (2.09 -> 15.88 s), and
**r41 alone** is what stops it returning. Under `rubi_verbose` r41's condition is
rejected ONCE and then no further verbose line appears for 70 s, so the time
goes into the matcher's `mr_cond_retry` binding ENUMERATION for r41's pattern
`u_.*(a_.*v_^m_.)^p_`, not into the condition and not into a firing. Ticket
`.scratch/class-ports/issues/16-9_3-r41-match-enumeration-blowup.md`.

#### A6.4 Route — 10 entries

Ten entries whose corpus answer is `Unintegrable`/`CannotIntegrate` with a Rubi
step count of 0 or 1 now take a 9.3 route that leaves an interior marker. The
rule that answers first, `rubi_verbose`-traced on both cores — probe
`probes/section9/04-route-rules.{mac,run,out}`:

| entries | rule | upstream |
|---|---|---|
| `3.5` e286/e287/e290, `2.3` e758 | `9_3 r63` | `9.3 …:560-563` `Int[u_,x_] := With[{v=ExpandIntegrand[u,x]}, Int[v,x] /; SumQ[v]]` |
| `1.3.2` e760/e761 | `9_3 r54` | `9.3 …:463-466` `Int[x_^m_*Fx_,x_] := With[{k=Denominator[m]}, k*Subst[Int[x^(k*(m+1)-1)*SubstPower[Fx,x,k],x],x,x^(1/k)]] /; FractionQ[m]` |
| `6.7.1` e1014-e1017 | `9_3 r51`, then `9_3 r46` | `FunctionOfLinear`, then `RationalFunctionExpand` |

Each condition is a byte-faithful port of its upstream line; what differs is
which rule gets there first, the same load-order-vs-specificity gap as A6.1.
One sub-question is left open and is recorded in ticket 14 (probe 04's
`EXPANDINTEGRAND` lines): `%mr_expandIntegrand(x^2/(x+log(x)), x)` returns
`log(x)^2/(log(x)+x) - log(x) + x` and `%mr_expandIntegrand(x/(%e^x+x), x)`
returns `1 - %e^x/(x+%e^x)`, both `SumQ` true — it divides treating `log(x)`
and `%e^x` as indeterminates, which is what makes `9_3 r63`'s guard true. The
utility is PRE-EXISTING and behaves identically on both cores (probe 04 prints
the same two lines on each); what is new is the 9.3 record that consumes it. Whether
Mathematica's `SmartApart` (`IntegrationUtilityFunctions.m:3897`, reached from
`ExpandExpression`:3780 at its line 3785) does the same on that input is NOT
measured here — this repo has no Mathematica.

#### A6.5 Gates, re-measured 2026-09-23 at Task 14

| gate | Results |
|---|---|
| `maxima --very-quiet -b test_maxima_rubi.mac` | `1292 passed, 0 failed` |
| `maxima --very-quiet -b test/test_rule_table_order.mac` | `11 passed, 0 failed` |
| `maxima --very-quiet -b test/test_section9_e2e.mac < /dev/null` | `6 passed, 0 failed` |
| `python3 test/check_generated_rules.py` | `23 passed, 0 failed` |
| `python3 test/test_generator_section9.py` | `21 passed, 0 failed` |
| `test/matcher/test_mr_match.mac` / `test_mr_tree.mac` / `test_mr_dispatch.mac` | `57` / `58` / `71 passed, 0 failed` |

#### A6.6 Verdict

The port is a large net gain (+827 PASS, 1,132 FAIL->PASS) and ticket 06's
target entry verifies. Two of the defects this measurement found are NOT
acceptable as they stand:

1. **A6.2, the inert-head leak** (ticket 15) — at least 281 class-6 answers
   carry a placeholder operator (286 entries leak in the paired rerun; 281 of
   them reach `error` in the full record and 5 hit the cap first); 69 of those
   entries previously produced a CORRECT, verified antiderivative. **Blocking.**
2. **A6.1, the give-up ordering** (ticket 14) — 189 entries lose a clean
   give-up, which is the whole of class 3's -96. A dispatcher fix.

A6.3's `1.3.1` e190/e238 (ticket 16, a >70x cost explosion on cheap entries,
same rule as A6.2) and A6.4's ten route changes are recorded with the same
evidence but are smaller in scale. §6's "every PASS->FAIL attributed" is met,
each cause by a committed probe under `probes/section9/`; its "all gates green"
is met (A6.5). The acceptance decision, and the merge, are the user's, and this
amendment recommends the two fixes first.
