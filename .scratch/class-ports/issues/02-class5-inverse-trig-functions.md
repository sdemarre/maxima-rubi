# Class 5 (inverse trig functions) port — 4,585 entries

Status: in prog — Steps 1–9 done; Step 10 record written (`docs/corpus-class5-baseline-uplift.md`, 2026-09-26); closes on the merge of `class-ports`
Type: task (port, runbook-driven)
Filed: 2026-08-30 (milestone-3 close; the M2 TODO's class-5 item, now
against the instantiated runbook)

## Scope

Port the "5 Inverse trig functions" section (section name VERIFIED
against `reference/maxima-syntax-test-suite/5 Inverse trig
functions/` — 18 `.mac` files under subdirs 5.1 Inverse sine … 5.6
Inverse cosecant) and its rule files
(`reference/rubi/Rubi/IntegrationRules/5 Inverse trig functions/`)
per `docs/class-porting.md` Steps 1–10. The milestone-3
instantiation (`docs/corpus-class3-baseline-uplift.md`) is the
template; its standing constraints bind (byte-identity gate for
every accepted class, 30 s per-entry cap, 100 s timeout re-check,
A/B vs the `integrate` baseline, acceptance record per the
class-2/class-3 template, TLS probe on the core rebuild).

## Recon numbers (measured 2026-08-30 — PRE-CENSUS; the runbook
Step-1 census probe is the first act of the port and supersedes
these)

- **Corpus: 4,585 entries** — counted over the section's 18 `.mac`
  files (lines starting with `[`); matches the M2 TODO's figure.
- Rule files: 15 `.m` files; 15 `Rubi.m` LoadRules entries (all
  loaded, as in class 3's 11/11).
- Rule count: **665 `Int[... ] :=` lines** across the 15 `.m` files
  (recon count of rule-shaped lines; the Step-1 census probe is the
  authoritative count).

## Known interactions

- The inverse-trig heads (`asin`/`acos`/`atan`/`acot`/`asinh`/
  `acosh`/`atanh`/`acoth`) are the class-3 headvar allow-list heads —
  the native bound spellings are already probed and tabled
  (class-3 Task 3; `arccot`/`arcoth` unbound-noun adjudication);
  the Step-1 answer-head census decides which `HEAD_REWRITES` rows
  (if any) the expected texts need (`ArcTan(`-style Rubi paren
  spellings may occur in expected answers — the class-3
  bracket-sweep precedent).
- Queue position: second (8 → 5 → 6 → 7 → 4).

## Acceptance

Per the runbook: merged records complete (4,585/4,585), A/B
triaged with nothing unexplained, re-check read, acceptance record
committed, the byte-identity gates for classes 1–3 (and 8 if
accepted earlier) green, Layer A green.

## Comments

### 2026-09-25 — Step 1 (census) COMPLETE; status needs-triage -> ready

Build `branch_5_50_base_84_g4204fb669` (2026-08-31 13:27:47), SBCL 2.6.7.
Branch `class-ports` (worktree `mr-ports`), on top of the class-8 port
(`be6b1af..4f8144a`, base `cd0a421`).

**Probes committed (re-runnable):**

- `probes/translation/10-class5-syntax-census.{run,out}` — Step 1(a): the
  01 census over the loaded "5 " files, then
  `probes/translation/10-class5-table-closure.py "5 "`, the closure against
  `generator/translation_table.py` AND its **transitive closure through
  `IntegrationUtilityFunctions.m`** (ticket 05's CENSUS TRAP — the first
  census probe to take it; the script takes the section as its argument, so
  classes 7 and 4 can reuse it). It counts rules the generator's way (after
  `unwrap_showsteps_lines`), and splits the table-less tokens into
  EMITTER-dispatched (the generator names them) and truly UNLISTED.
- `probes/corpus/18-class5-answer-heads.{run,out}` — Step 1(b) (the class-6
  script with the section as its argument).
- `probes/answer-side/05-class5-answer-side-identities.{py,run,out}` — the
  native inverse-trig heads through the harness's own zero chain, the
  Mathematica conventions, the simplifier's negated-argument rewrites,
  `poly_discriminant`, and `op()` of an inverse-trig call.

**Counts.** 15 loaded files (5.1 Inverse sine 6 files, 5.3 Inverse tangent
7, 5.5 Inverse secant 2 — Rubi has no separate arccos/arccot/arccsc files:
each file carries both members of its pair). The 01 census counts **665**
rules (the recon's figure), but 5.3.7 carries TWO single-line
`If[TrueQ[$LoadShowSteps], <ShowStep rule>, <plain rule>]` wrappers (L30,
L31) which the census's `rule_runs` glues onto the rule before them; the
generator unwraps them to their plain branch, so the port total is **667**
(5.3.7 79, not 77) — the class-3/9 `EXPECTED_TOTAL` adjustment, in the other
direction from 9.3's. Every rule has a `/;` condition. AUTO 361 / MANUAL 304
by the census's own tiers. Corpus **4,585** entries over 18 `.mac` files
(the recon's figure). No head variables. No bare-`u_` record (none of the
15 files has an `Int[u_, x_Symbol]` rule), so class 5 adds nothing to the
tail.

**Token closure — 83 tokens; 72 already have rows; 2 are emitter-dispatched
(`ReplaceAll` 4 rules — `ReplaceAll[u, x -> …]` -> `subst`, two each in
5.1.6 and 5.5.2; `IGeQ` 2 — `INT_CMP` -> `%mr_iGeQ`, ported since the matcher
translation fixes and first reached here); 8 UNLISTED, all adjudicated:**

*A. Native heads — 2 tokens, 62 rule-uses. Step 2 rows.* `ArcSec` 31 rules
-> `asec`, `ArcCsc` 31 -> `acsc`. Both differentiate through the zero chain
(probe 05 A5/A6) and float-evaluate on their real domain (E5/E6; at 0.7 they
are complex, E7/E8, as Mathematica's are). The conventions agree with
Mathematica's: `asec(z) = acos(1/z)`, `acsc(z) = asin(1/z)` (C1/C2 through
the chain, C4-C6 at +-1.7), and `acot(z) = atan(1/z)` (C3, C7 — `acot` is
Mathematica's real-valued ArcCot, the class-3 row stands). mr-tree already
maps both heads (`maxima_rubi_tree.lisp` `+functions+`), and
`%mr_inverseFunctionQ` already lists them.

*B. `HalfIntegerQ` — 8 rules (5.1.3/5.1.4, the `(d+e x)^p (f+g x)^q` pair
products). Step 4 port*, variadic like Rubi's (every argument an explicit
rational with denominator 2).

*C. `ExpandExpression` — 2 rules (5.1.5 r9/r10). A table row only:*
`%mr_expandExpression` is ported (class 1, the ExpandIntegrand catch-all,
`maxima_rubi_utils.mac`), no rule called it by name until now.

*D. 5.3.7 r27/r28 (the two ShowSteps rules, `Int[u_*v_^n_., x]` with
`v` a quadratic of negative discriminant) — 4 tokens, 2 rules each.*
`InverseFunctionOfLinear` and `SubstForInverseFunction` (3-arg; its 4-arg
worker and Mathematica's `InverseFunction[Head[v]]`) are Step-4 ports.
`Discriminant` -> the native `poly_discriminant` (a Step 2 row): it equals
Mathematica's `b^2-4ac` on a symbolic quadratic and the 5-term cubic
formula (probe 05 D1-D3). `Head` -> a `%mr_head` port (Step 4): `op()` of
an inverse-trig call is the head symbol the table emits for the bare head
atom (H1-H3), so `EqQ[Head[tmp], ArcTan]` compares `atan` with `atan`.

**Transitive closure (the CENSUS TRAP check).** 195 utilities are reachable
from the rule tokens through `IntegrationUtilityFunctions.m` (41 rule-side,
154 transitive-only); by the probe's name test 67 have table rows, 69 have
`%mr_` ports, 59 are ABSENT. None of the 59 is a class-5 gap:

1. The **three rule-side ABSENTs** are exactly B and D above
   (`HalfIntegerQ`, `InverseFunctionOfLinear`, `SubstForInverseFunction`).
2. **Named differently / inlined, not absent:** `InverseTrigQ` /
   `InverseHyperbolicQ` (via `InverseFunctionQ`, which the 26
   `InverseFunctionFreeQ` rules reach) are inlined head lists in
   `%mr_inverseFunctionQ`, ArcSec/ArcCsc included;
   `FunctionOfExponentialTest(Aux)` are `%mr_foE_test(2)/%mr_foE_testAux`
   (the class-2 port of the 8 `FunctionOfExponentialQ` rules);
   `PureFunctionOf{Sin,Cos,Tan,Cot}Q` are the generic
   `%mr_pureFunctionOfTrigQ`.
3. **FunctionOfQ's hyperbolic arms** (`FunctionOf{Sinh,Cosh,Tanh}Q`,
   `PureFunctionOf{Sinh,Cosh,Tanh,Coth}Q`, `OddHyperbolicPowerQ`,
   `ReapList`) — the standing deviation (a). Not reached: class 5's six
   `FunctionOfQ` calls are all `FunctionOfQ[(c+d*x)^(m+1), u, x]`, a power
   `v`, which takes the general `FunctionOfExpnQ` arm class 8 ported.
4. **The algebra substrate the port approximates since class 1** — 41 names
   reached only through `Simp`/`SimpHelp`, `Subst`
   (`SubstAux`, `SimplifyAntiderivative`, `RectifyTangent`/`Cotangent`,
   `SmartNumerator`/`Denominator`), `ExpandIntegrand` (`CollectRecipTerms`,
   `DistributeOverTerms`, `ExpandBinomial`), `SmartApart` (`GensymSubst`,
   `KernelSubst`, `MakeAssocList`), `ContentFactor`, `Rt` (`NthRoot`),
   `FreeQ`/`GeQ`/`IntegerQ` (`ComplexFreeQ`, `RealNumberQ`,
   `SqrtNumber(Sum)Q`). Their parents are ported as wholes on Maxima's own
   simplifier (house deviation). One of them touches this class's answers:
   Rubi's `Subst` runs `SimplifyAntiderivative`, whose `RectifyTangent` /
   `RectifyCotangent` rewrite a discontinuous `ArcTan[…]` into a continuous
   one. The port does not, so a class-5 answer may differ from the expected
   text by a piecewise constant — invisible to verification by
   differentiation, visible only to the `expected` (form-identical) class.

**Answer side (Step 7 input): no new `HEAD_REWRITES` row.** The discovery
pass finds 29 native heads (`sqrt(` 23,694, `atan(` 9,087, `asin(` 8,859,
`polylog(` 3,441, `acos(` 1,739, `acsc(` 1,121, `asec(` 1,057, `acot(` 731,
…) and 9 non-native ones, every one already disposed of:

| head | uses | disposition |
|---|---|---|
| `Unintegrable(` 1,168, `CannotIntegrate(` 35 | 1,203 | corpus markers |
| `FresnelC(` 403, `FresnelS(` 383 | 786 | class-8 rows |
| `Ci(` 386, `Si(` 380 | 766 | class-3 rows |
| `GAMMA(` 92 (all 2-arg) | 92 | class-2 reading of the arity-dispatched row |
| `HypergeometricPFQ(` 36 | 36 | class-8 row |
| `AppellF1(` 22 | 22 | no native — the structural ceiling |

The six inverse-trig natives the answers are made of differentiate through
the zero chain and float-evaluate (probe 05 A1-A6, E1-E6), so "no rewrite"
is sound. Step 7 is therefore the no-op check and the rewrite totals for
section 5.

**Simplifier facts the matcher will see (probe 05 S1-S8):** Maxima rewrites
a syntactically negated argument — `asin(-x) = -asin(x)`, `atan(-x) =
-atan(x)`, `acot(-x) = -acot(x)`, `acsc(-x) = -acsc(x)`, and `acos(-x) =
%pi - acos(x)`, `asec(-x) = %pi - asec(x)`; `atan(1/x)`/`acot(1/x)` stay.
So `(a+b*acos(-c*x))^n` reaches the matcher as `(a+%pi*b - b*acos(c*x))^n`
— the same rule shape with shifted captures, not a miss.

### 2026-09-25 — Steps 2-7 complete (branch `class-ports`)

Build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7. Steps 8-10 (baseline,
package corpus run, close) are the coordinator's.

- **Step 2** (`0667f47`): 8 rows — `ArcSec`/`ArcCsc` -> `asec`/`acsc`,
  `Discriminant` -> `poly_discriminant`, `ExpandExpression` (ported since
  class 1), and the four Step-4 ports `HalfIntegerQ`,
  `InverseFunctionOfLinear`, `SubstForInverseFunction`, `Head`. The closure
  probe then reports 0 UNLISTED. Byte-identity EMPTY for 1/2/3/4/6/8/9 +
  rewrites.
- **Step 3** (`db3840a`): **667 rules** over 15 files (5.1.1 6, 5.1.2 14,
  5.1.3 30, 5.1.4 60, 5.1.5 62, 5.1.6 43, 5.3.1 10, 5.3.2 24, 5.3.3 22, 5.3.4
  161, 5.3.5 20, 5.3.6 76, 5.3.7 79, 5.5.1 36, 5.5.2 24). The only generator
  change is `configure()` (EXPECTED_TOTAL 667 = the census's 665 + 5.3.7's two
  ShowSteps records). No new emitter case, no G-9 LHS risk, no bare-`u_`
  record. P3 static 24 -> **25/0** (all 5,178 pattern strings prepare).
- **Step 4** (`03e7699`): `%mr_halfIntegerQ`, `%mr_head`,
  `%mr_inverseFunctionOfLinear`, `%mr_substForInverseFunction` (+
  `%mr_inverseHead`, `%mr_sfi_aux`), and class-5 files end to end on sibling
  tables (5.3.7 r27/r28, 5.5.1 r1/r2, 5.1.5 r9). Layer A 1350 -> RED 1358/28
  -> **GREEN 1387/0**.
- **Step 5** (with Step 3): per-file counts equal the census; no raw `$`;
  the new rows landed (asec 31, acsc 31, poly_discriminant 6,
  %mr_halfIntegerQ 8, %mr_expandExpression 2, %mr_inverseFunctionOfLinear 4,
  %mr_substForInverseFunction 2, %mr_head 2 call sites).
- **Step 6** (`4a5820e`): `mr_load_all` loads class 5 right after class 3 and
  before class 6 (Rubi.m: section 5 after 4 and before 6; class 4's ported
  bridge records have empty bodies, so section 5 follows section 3 in the
  body order). Table **4,992** (4,325 + 667); tail unchanged. Rule-table
  order **15/0** (+1: class 5's bodies contiguous between `3_5` and
  `6_1_10`). The full table loads without the TLS flag (that gate runs flagless).
  Core rebuilt in the `mr-ports` worktree: `rules=4992`, fingerprint
  **`8e57b2901075a7fb8cf63a3198d79b4b`** (driver agrees:
  `test_driver_core_pin` 7/0).
- **Step 7**: **no `HEAD_REWRITES` row** (Step 1). `test/test_head_rewrites.py`
  47 -> **52/0** (five class-5 corpus excerpts: Si/Ci/GAMMA/FresnelC over
  `acos`, and the six inverse-trig natives untouched). No-op over EVERY entry
  (`probes/corpus/19-class5-head-rewrite-noop.out`): the driver is unchanged
  by this port, so 0 normalized texts differ from `4f8144a` in all eight
  sections; section 5's rewrite totals equal the Step-1 census (Ci 386, Si
  380, FresnelC 403, FresnelS 383, GAMMA 92, HypergeometricPFQ 36). Slice
  A/B (`probes/corpus/20-class5-slice-ab.out`: 63 entries of classes
  1/2/3/6/8 on a core built at `4f8144a` against the class-5 core): **0
  transitions** either way. The 2-per-file class-5 slice (36 entries, 18
  files): **32/36 PASS** (32 verified), 4 contains-noun — 5.2.5 e1/e2
  (`x^k (a+b acos(c x))/(d-c^2 d x^2)`) and 5.5.2/5.6.2 e1 (`asec(a x^5)/x`,
  `acsc(a x^5)/x`), whose Rubi routes substitute to `x tan(x)`/`x cot(x)`
  sub-integrals (likely the unported section-4 bodies).

Other gates at the end: section-9 e2e 9/0, mr-match 57/0, mr-tree 84/0,
dispatch 106/0, generator section-9 unit 26/0, run-records 43/0, every
harness guard at its figure, byte-identity EMPTY for 1/2/3/4/5/6/8/9 +
rewrites.

**Findings for Step 9 / follow-ups.**

1. **EqQ's syntactic zero test limits 5.3.7 r27/r28** (the ShowSteps pair).
   Their condition `EqQ[Discriminant[v,x]*tmp[[1]]^2 + D[v,x]^2, 0]` is an
   identity in x. `%mr_eqQ` reads it without expanding
   (`.scratch/matcher-translation-fixes/issues/03`, open, awaiting the
   user's decision), so the pair fires only when the identity cancels on
   simplification (`v = 1+x^2`) and declines on a shifted quadratic
   (`4x^2+4x+2` with `atan(2x+1)`, measured in the Step-4 scratch run). Not a
   new ticket: a class-5 site of issue 03's defect, noted there by this
   comment.
2. **No `SimplifyAntiderivative`.** Rubi's `Subst` rectifies a discontinuous
   `ArcTan`/`ArcCot` (`RectifyTangent`/`RectifyCotangent`); the port does
   not (Step 1, transitive closure item 4). A class-5 answer can then differ
   from the expected text by a piecewise constant: it can still verify by
   differentiation but not be `expected` (form-identical).
3. **The simplifier rewrites a negated inverse-trig argument**
   (`acos(-x) = %pi - acos(x)`, `asec(-x) = %pi - asec(x)`, the other four
   odd; probe 05 S1-S6). The matcher sees the rewritten form, the same rule
   shape with shifted captures. Nothing to fix. It is the likely reading if
   an `acos`/`asec` entry with a negative coefficient answers in an
   unexpected form.

**Decided by judgment** (recorded here, not asked): `Discriminant` as the
native `poly_discriminant` rather than a port (it measures equal to
Mathematica's); `Head` as a narrow `%mr_head` (Mathematica's atom heads for
atoms, the stored operator otherwise) rather than a general one; the
x-free short cut in `SubstForInverseFunction`'s walk (sound: v carries x);
no new ticket for finding 1 (issue 03 already owns the defect).

### 2026-09-26 — Steps 8–9 measured, Step 10 record written

Record: `docs/corpus-class5-baseline-uplift.md` (the PASS→FAIL
attribution section is added separately). Final package record
`test/corpus_class5.final.out` (core `89bec424`, 7,776 rules, `c2deb32`;
queue runner, 24 workers, 30 s cpu cap): **3,629 / 4,585 (79.1 %) against the native baseline's 1,234 (26.9 %)**; the pre-fix run
(core `4daae7ac`) read 2,915, and the class-ports fixes moved 15 entries
PASS→FAIL against it. 100 s re-check of the timeouts: 195: 52 now-PASS, 74 still timeout. Figures:
`probes/corpus/28-class-ports-acceptance.out`.
