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
