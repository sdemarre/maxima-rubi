# Matcher substrate — exact seen test, rules-only runs, SmartApart, IntegerPart: design

Date: 2026-09-15. Branch `matcher-substrate` @ `a64db1a` (translation-fixes plan stopped at Task 7
Step 5). Parent designs: `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md` (§3.5,
§4 P5) and `docs/superpowers/specs/2026-09-14-matcher-translation-fixes-design.md` (§3.3, §4).
Measurements stamped Maxima `branch_5_50_base_84_g4204fb669` (build date 2026-08-31 13:27:47) /
SBCL 2.6.7. Design brainstorm with the user 2026-09-15 (handoff
`handoffs/2026-09-15-matcher-translation-fixes-stop.md`), amended twice the same day while the plan
was pre-validated (§0.2, §0.3). File name kept from the first version.

## 0. Context

The translation-fixes plan (`docs/superpowers/plans/2026-09-14-matcher-translation-fixes.md`)
stopped at Task 7 Step 5, defect clearance. Probe 16 (`probes/matcher/16-seen-guard-trace.out`,
`.class1.out`) shows the collapse mechanism at non-9.1 sites: `mr_int`'s ratsimp seen comparison
(`%mr_seenp`, `maxima_rubi_utils.mac:201–211`) reads a rule's rewrite to an algebraically equal
form as a loop and takes the `integrate` fall-through. The fix had given the exact test only to
9.1's `Int` calls (`mr_int_exact`). Collapse groups: class 2 g1; class 3 g12, g21, g48; 36 class-1
groups. Under the probe-local exact-only control, 78 entries reach PASS (5 + 6 + 67). A sibling
finding stands beside it: `%mr_intPart_aux` / `%mr_fracPart_aux` read IntPart/FracPart by floor
where Rubi uses `IntegerPart`/`FractionalPart` (class 1 g27).

Pre-validating the first version of this design on the whole corpus (§2) showed what the ratsimp
cut had been hiding: about 1,300 P5b PASS entries were answered by Maxima's `integrate` on a nested
call the cut declared a loop, most of them right after a rule whose `ExpandIntegrand` does not do
Rubi's partial-fraction split (`SmartApart` is not ported). The user's goal is that Rubi handles
the corpus itself; the design therefore makes the nested `integrate` fall-through a switch, off by
default, makes the depth cap a switch with its hits counted, and ports `ExpandExpression` /
`SmartApart`.

### 0.1 Decisions made in the brainstorm (user, 2026-09-15)

| question | decision |
|---|---|
| seen-test scope | approach A: exact `member` on every `mr_int` call; `%mr_seenp` deleted (§3.1) |
| `mr_int_exact` | removed: the generator emits `mr_int` for 9.1 again (§3.1) |
| class 1 g27 | port Rubi's `IntegerPart`/`FractionalPart` reading (§3.2) |
| tickets 02 (GtQ/GeQ) and 03 (EqQ/NeQ) | a separate plan after this one's acceptance |
| undetermined / no-route groups | carried to the p5c attribution, not diagnosed in this plan |

Alternatives weighed and rejected for the seen test: (B) exact `member` after a float-to-rational
normalization of both sides — it guards a cycle with no substrate evidence (§2) at an O(depth)
normalization cost per dispatch; it is the fallback if probe 17 finds the cycle. (C) pop `f` from
`%mr_seen` before the rule's replacement runs (P0's pass-2 behaviour, generalized) — it also drops
the exact-repeat cut the identity re-sends (1_4_1_r18, 1_1_3_7_r45) rely on, which would then spin
to the depth cap.

### 0.2 First amendment (user, 2026-09-15, plan pre-validation)

| question | decision |
|---|---|
| P5b PASS entries that relied on the seen-cut `integrate` fall-through (class 2 prototype run) | proceed with approach A; attribute such groups at the acceptance stop (§4 step 6) |
| corpus queue runner | prototyped, measured, **dropped** (§3.6); ticket `.scratch/corpus-harness/issues/01-queue-runner.md` |

### 0.3 Second amendment (user, 2026-09-15, after the whole-corpus prototype runs)

| question | decision |
|---|---|
| the nested `integrate` fall-through | a switch `mr_nested_fallback`, **default off** (rules-only); on reproduces today's behaviour (§3.3) |
| the depth cap | a switch `mr_max_depth`, default 16; every run counts depth-cap hits so the default is chosen from data (§3.3) |
| the ExpandIntegrand gap | port Rubi's `ExpandExpression` / `SmartApart` / `ExpandCleanup` branch in this plan; the other unported `ExpandIntegrand` branches are ticketed (§3.4) |
| `Expand[u, x]` | `format(u, %poly(x))` from Maxima's `format` share package (user suggestion, measured §2) |
| plan structure | one plan, one p5c re-measurement |
| p5c arms | two arms: the defaults (rules-only) as the new baseline record, and `mr_nested_fallback=true` as the like-for-like comparison with P0/P5b that the acceptance attributes (§4) |

### 0.4 Third amendment (user, 2026-09-16, plan pre-validation)

| question | decision |
|---|---|
| the zero oracle for the §3.5 value checks | **`radcan`** (`ratsimp(radcan(d)) = 0`), not bare `ratsimp` |

Measured on the prototype (2026-09-16, build `branch_5_50_base_84_g4204fb669`): after
`%mr_expandCleanup` rewrites two conjugate-radical denominators, bare `ratsimp` cannot prove the
difference zero on three shapes — a nested-radical parameter
`1/((x-sqrt(1+sqrt(a)))(x+sqrt(1+sqrt(a))))`, its numeric sibling `sqrt(2+sqrt(3))`, and
`1/((x-sqrt(a))(x+sqrt(a))(x-1))` — reporting a residual whose numerator is
`(sqrt(a)+1)^2 - a - 2 sqrt(a) - 1`, i.e. 0. `radcan`, `ratsimp(radcan(…))` and a numeric
substitution (`a=7, x=2`: 2.7e-15, -8.3e-15, 7.1e-17) all close it; the per-stage trace puts the form
change at the `ratdisrep ∘ %mr_simplifyTerm` map, with each term alone still `ratsimp`-zero. Bare
`ratsimp` as the probe-18 oracle would therefore have recorded three false defects in a port that is
value-preserving. The corpus harness's own verification is the 8-stage zero chain, not a single
`ratsimp`, for the same reason.

## 1. Scope

In:

- the exact seen test for every dispatch and the removal of `%mr_seenp` and `mr_int_exact`;
- the `IntegerPart`/`FractionalPart` reading in `%mr_intPart_aux` / `%mr_fracPart_aux`;
- the run switches `mr_nested_fallback` and `mr_max_depth`, the depth-cap hit census and the run-record
  tooling they need;
- the `ExpandExpression` / `SmartApart` / `ExpandCleanup` port with its helpers and an `Expand[u, x]`
  port;
- probes 17 (seen test, drift targets, IntPart) and 18 (ExpandExpression / SmartApart), red/green;
  the unit checks and gate changes that prove each;
- the p5c re-measurement (two arms) and the acceptance stop, which replaces the translation-fixes
  plan's Task 7 Steps 6–10.

Out:

- tickets `.scratch/matcher-translation-fixes/issues/01` (case-fold order shim), `02` (GtQ/GeQ real
  reading), `03` (EqQ/NeQ zero test) — a separate plan;
- the other unported `ExpandIntegrand` rules (`IntegrationUtilityFunctions.m:3379–3757`: the log,
  exponential, binomial and trinomial branches), `CollectRecipTerms`, `ExpandBinomial` — ticketed
  with their usage counts;
- diagnosis of the undetermined / no-route groups (class 1 g1, g2, g15, g21, g196, g207,
  g247/g249/g250, the 16 part-B groups; class 2 g3; class 3 g20, g51) — re-attributed on the p5c
  records;
- the identity re-sends and single-term expansions probe 16 tagged `none` (1_4_1_r18,
  1_1_3_7_r45, 1_4_2_r19/r20, class 1 g9/g30);
- matcher changes (`maxima_rubi_match.lisp`, `maxima_rubi_tree.lisp`);
- the corpus queue runner (§3.6, ticketed);
- a top-level "rubi, then integrate" user mode (the endorsed later item; `rubi_fallback` stays as is);
- Plan 3 Tasks 5–6 (they resume after acceptance).

## 2. Measured basis

Committed evidence:

- Collapse at non-9.1 sites, exact-only control counts, P0 routes (pass 2/3, seen list empty):
  `probes/matcher/16-seen-guard-trace.out` (`Results: 32 passed, 1 failed`), `.class1.out`
  (`Results: 179 passed, 7 failed`; the failures are control arms that did not return in 30 s).
- g27 mechanism: `probes/matcher/10-p5b-attribution.mechanisms-class1-b.md` (1_2_3_2_r34 on
  e254/e604 p=-1/2, e255/e605 p=-3/2; floor reads (-1, 1/2) and (-2, 1/2), Rubi (0, -1/2) and
  (-1, -1/2)).
- The drift guard's origin: commit `891240b` and `.superpowers/sdd/progress.md:1618–1649`
  (2026-08-25), measured on the `defmatch` runner; the source of the floats was not identified.
- The dispatch entries (`maxima_rubi_utils.mac`): `%mr_max_depth : 16$` (:73); `mr_int(f, x) :=
  mr_top(f, x, true)` (:269) — every generated `Int` call and one utils call (:3462) take the
  `integrate` fall-through on a depth-cap hit, a seen hit or no rule; `rubi(f, x) := mr_top(f, x,
  false)` (:279) — the top level returns `mr_unintegrable`. The driver classes an answer holding
  `unintegrable` anywhere as `contains-noun` (`test/corpus_driver.py` `build_text`).
- `%mr_expandIntegrand2` (:3222): a positive-integer power of a sum expands, a linear-power product
  goes through `ExpandLinearProduct`, anything else is `expand(u)`; the header (:3072–3083) states
  `ExpandExpression / SmartApart … are NOT ported`. 291 generated lines call `%mr_expandIntegrand(`;
  `%mr_rationalFunctionExpand` (:3354, 2 generated callers) is the same function.
- Rubi: `ExpandIntegrand[u_,x_Symbol] := With[{v=ExpandExpression[u,x]}, v /; SumQ[v]]` (:3762, the
  catch-all after the specific rules :3379–3757); `ExpandExpression` (:3780); `ExpandCleanup`
  (:3805/:3810); `CollectReciprocals` (:3824–:3832); `SmartApart` (:3897/:3902) with `MakeAssocList`
  / `GensymSubst` / `KernelSubst` (:3908–:3955); `RationalFunctionFactors` (:1593);
  `NonrationalFunctionFactors` (:1606); `ExpandAlgebraicFunction` (:3980/:3984); `UnifySum` (:3996)
  and `SimplifyTerm` (:2168) are already ported (`maxima_rubi_utils.mac:3958`, `:3968`).
- `IntPart[u_,n_:1] := If[RationalQ[u], IntegerPart[n*u], …]`, `FracPart` likewise with
  `FractionalPart` (:2952–:2981). `Rubi.m` defines no loop guard of its own.
- P5b record lines (`test/corpus_class1.p5b-run1.out`): 1.1.1.4 e1, e3, e4, e5, e135 `verified`
  0.1 s; 1.1.1.7 e1 `timeout` 30.0 s. Wall medians (`test/record_medians.py`): P0
  (`test/corpus_class{1,2,3}.pre-matcher.out`) 1.3 / 4.3 / 3.9 s; P5b run 1 0.6 / 0.6 / 1.5 s.
- The run switches (`maxima_rubi_dispatch.lisp:58–67`: `mr_flat_wide`, `mr_cond_retry`,
  `mr_model_flags`, all `defmvar` booleans); `test/run_records.py` validates `true|false` only and
  its `SWITCHES_RE` reads booleans; `test/test_run_records.py:104` checks the defaults against
  `(defmvar $mr_… nil|t)`; `test/merge_class_shards.py:34` and `test/ab_records.py:34` anchor the
  result line at end of line.
- Corpus step counts (the third element of every corpus entry, Rubi's rule applications): class 1
  median 4, p90 9, p99 17, max 46, 272 entries over 16; class 2 3 / 9 / 24 / 48, 24; class 3
  5 / 18 / 42 / 148, 358.

Ad-hoc measurements of the pre-validation (2026-09-15, same build, scratch worktrees, the first
version of this design: exact seen test + IntegerPart, fall-through on). **Not evidence until
committed** — probes 17 and 18 commit the value and entry measurements; the p5c records and
attribution re-measure the corpus figures:

- **The whole corpus on the prototype** (classes 1 and 3 through the sharded launcher; class 1's
  last shard, 1,249 entries of 1.1.1.3, re-dealt over 20 processes; class 2 through a 24-worker queue,
  contended): PASS 21,542 / 771 / 2,145 against P5b run 1's 22,513 / 774 / 2,269; PASS→FAIL 1,160 /
  16 / 138, FAIL→PASS 189 / 13 / 14; class 1 timeouts 2,451 (P5b 1,294), 1,091 `verified → timeout`
  of which 988 took under 5 s in P5b.
- **Mechanism count** (probe 16's trace arm on the unchanged tree, every PASS→FAIL entry): a ratsimp
  seen cut on the P5b route in 1,150 of class 1's 1,160 (805 at rules whose replacement calls
  `%mr_expandIntegrand`, 345 at other rules; the other 10 had P5b walls of 22–30 s and re-run
  `verified`: cap noise), class 3 93 + 45 of 138, class 2 5 + 8 of 16 (3 cap noise). Top cutting
  rules, class 1: 1_4_1_r18 217, 1_1_1_3_r5 213, 1_1_1_2_r12 84, 1_2_1_2_r73 76, 1_2_1_3_r15 65,
  1_2_1_3_r20 60. Per rule against probe 16's gains: 16 rules gain more than they lose (44 gains,
  5 losses); 14 gain but lose as much or more (1_4_1_r18 8 / 225, 1_2_1_3_r20 8 / 60); 78 rules with
  no gain carry 896 losses.
- **1.1.1.4 e4** (`(a+b x)/((c+d x)(e+f x)(g+h x))`): on the unchanged tree 1_1_1_4_r7's
  `ExpandIntegrand` gives `b*x/(cubic) + a/(cubic)` over the expanded denominator; the ratsimp cut
  sends it to `integrate`, `verified` in 0.1 s. With the exact test the expanded form dispatches:
  at least 794 `cond not accepted` in 60 s, no fire, no depth-cap hit, no float; `timeout` at 120 s.
  Rubi's `ExpandExpression` → `SmartApart` splits it into partial fractions instead.
- **`partfrac(u, x)`** (Maxima's partial-fraction function, `describe("partfrac")`): e4's integrand
  in three linear-denominator terms, `ratsimp` difference 0, instant; the expanded-denominator form
  back to the same three terms; `1/((x-sqrt(a))(x+sqrt(a)))` identical with and without a gensym
  substitution of `sqrt(a)`; a radical coefficient `x/((x+sqrt(2))(x-1))` split; a non-rational
  factor `sqrt(x)/((x+1)(x+2))` split around `sqrt(x)`; a polynomial part split off; an irreducible
  quadratic `(x+1)/((x^2+x+1)(x-2))` kept; a symbolic exponent `1/((x+a)^m (x+b))` unchanged;
  `1/(a+b x^2)` unchanged.
- **`format(u, %poly(x))`** (`load("format")`, `share/contrib/format`): `(a+b)^2 (x+1)^2` →
  `(b+a)^2 x^2 + 2 (b+a)^2 x + (b+a)^2` (x-free factors kept, as Mathematica's `Expand[u, x]`);
  `(x+1)^2/(x+2)` → `x^2/(x+2) + 2x/(x+2) + 1/(x+2)`; `sqrt(x) (x+1)^2` → `x^(5/2) + 2 x^(3/2) +
  sqrt(x)`; `(a+b)(c+d)` unchanged; `(x+1)^m (x+2)^2` → powers of x times `(x+1)^m`; it collects
  coefficients per power of x (`(a d + b c) x`, where `Expand` keeps `a d x + b c x`). `expand` and
  `ratexpand` multiply out the x-free factors too.
- No `float(` / `numer` / `rationalize` / `bfloat` / `keepfloat` enters an integrand in the runtime
  sources; no class 1 or 3 corpus integrand has a decimal literal (class 2 one: 2.3 e194).
- `truncate` on `[-5/2, -3/2, -1/2, 0, 1/2, 3/2, -2, 2]` → `[-2, -1, 0, 0, 0, 1, -2, 2]`,
  `r - truncate(r)` → `[-1/2, -1/2, -1/2, 0, 1/2, 1/2, 0, 0]`.
- Prototype gates (first version): Layer A 957 → 964 (red 955 / 3 with only the seen checks, 958 / 6
  with only the IntPart checks); static gate 14 / 0 before and after regenerating 9.1; matcher suites
  53 / 51 / 58; probe 17 red 25 / 84, green 108 / 1 (the failure: e4 above).

## 3. Design

### 3.1 The exact seen test (runtime + generator)

- `%mr_top_body(f, x, fb)` loses its `exact` argument. The seen test is `member(f, %mr_seen)` on
  every call. Unchanged: the `%mr_seen` push/pop around the dispatch, the `mr_model_flags` binding.
- Deleted: `%mr_seenp` and its rationale comment (replaced by a pointer to probe 17 and this
  design); `mr_int_exact` and its comment block.
- `generator/generate_rules.py:1191`: `Int`/`IntHide` translate to `mr_int` for every source key;
  `rules/class1/9_1.mac` is regenerated; `test/check_generated_rules.py` `ENTRY_CALL` drops
  `mr_int_exact` (count stays 14).
- Behaviour: equal-form rewrites dispatch at every site; an exact repeat is still cut; two rules
  alternating between different equal forms stop at the depth cap.
- **Fallback trigger.** If probe 17 or the p5c attribution shows an integrand cycling between float
  and rational forms up to the depth cap, stop and report: the design moves to approach B by
  amendment.

### 3.2 The IntegerPart reading (utils)

- `%mr_intPart_aux(u, n)`: the rational branch is `truncate(n*u)`; `%mr_fracPart_aux(u, n)`:
  `r - truncate(r)` with `r : n*u`. The unreachable second `%mr_rationalQ(u)` branch is removed from
  both; the floor comments are corrected.
- `IntPart[u] + FracPart[u] = u` is kept; the form changes for negative non-integer exponents, so
  nested routes can change (204 replacement sites).

### 3.3 The run switches and the depth-cap census

- **`mr_nested_fallback`** — `(defmvar $mr_nested_fallback nil …)` in
  `maxima_rubi_dispatch.lisp` beside the three switches. `mr_int(f, x) := mr_top(f, x,
  mr_nested_fallback)`. False (default): a nested failure (depth cap, seen hit, no rule) returns
  `mr_unintegrable(f, x)`, which the driver already classes `contains-noun`. True: today's `integrate`
  fall-through. The top-level `rubi` / `rubi_fallback` entries are unchanged.
- **`mr_max_depth`** — `(defmvar $mr_max_depth 16 …)`; `%mr_max_depth` is deleted and
  `%mr_top_body` reads `mr_max_depth`.
- **Run records** (`test/run_records.py`): `SWITCHES` gains both names in record order;
  `SWITCH_DEFAULTS` `mr_nested_fallback=false`, `mr_max_depth=16`; `switch_settings` accepts
  `true|false` for the booleans and a positive integer for `mr_max_depth`; `SWITCHES_RE` reads both
  kinds. The driver keeps assigning every switch at the head of each entry text and stating the arm
  on the `filter:` line, so the mergers' one-arm check covers the new switches.
  `test/test_run_records.py`'s defaults check reads integer `defmvar`s too.
- **Depth-cap census** — `%mr_top_body` increments `mr_depth_cap_hits` (a global, reset to 0 by the
  entry text) at the cap branch. The driver prints it after the `rubi` call (`DEPTHCAP <n>`), parses
  it, and writes one line `<n> <label>` per entry with n > 0 to a per-shard sidecar
  (`corpus_<slug>.shard<kk>.caps`, next to the shard `.out`); the record line format is unchanged.
  `test/merge_caps.py` concatenates a run's sidecars into `test/corpus_class<N>.<tag>.caps` with a
  header (entries with hits, total hits, the maximum) and asserts every label is a record entry.
  `run_records.clear_stale_shards` also removes stale `.caps`.
- The P6 hard-wiring script (`p6_hardwire.py`) covers the three migration switches only; the two
  run switches are not hard-wired.

### 3.4 ExpandExpression / SmartApart (utils)

- `%mr_expandIntegrand2(u, x)`: the two specific branches stay; the final `expand(u)` becomes the
  port of Rubi's catch-all `ExpandIntegrand[u_,x_]` (:3762): `v : %mr_expandExpression(u, x)`, `v`
  if `%mr_sumQ(v)`, else `u`.
- New ports, each citing its `.m` line:
  - `%mr_expandExpression(u, x)` (:3780): the `.m` cascade — `ExpandAlgebraicFunction` when `u` is an
    algebraic, non-rational function; else `SmartApart(u)`; else `SmartApart` of the rational factors
    times the non-rational factors; else `Expand[u, x]`; else `Expand[u]`; else `SimplifyTerm`; each
    sum result through `ExpandCleanup`.
  - `%mr_smartApart(u, x)` / `%mr_smartApart(u, v, x)` (:3897/:3902) → `partfrac(u, x)` (the
    3-argument form's `v` is the variable, as in the `.m` call site).
  - `%mr_expandCleanup(u, x)` (:3805/:3810) and `%mr_collectReciprocals(u, x)` (:3824–:3832), with the
    `EqQ` conditions through `%mr_eqQ`.
  - `%mr_rationalFunctionFactors(u, x)` (:1593), `%mr_nonrationalFunctionFactors(u, x)` (:1606).
  - `%mr_expandAlgebraicFunction(u, x)` (:3980/:3984).
  - `%mr_expand_x(u, x)` (Mathematica `Expand[u, x]`) → `format(u, %poly(x))`; `load("format")` in
    `maxima_rubi.mac` (the core build and the fingerprint follow the loader).
- **Stated deviations.** (a) No `MakeAssocList` / `GensymSubst` / `KernelSubst` substitution around
  `partfrac`: measured unnecessary on radical parameters, radical coefficients, a non-rational factor
  and a symbolic exponent (§2); a unit check on a nested-radical parameter watches it, with `radcan`
  as its zero oracle (§0.4). (b) `partfrac` may order or group terms differently from `Apart`.
  (c) `format(…, %poly(x))` collects the coefficients of each power of x, where `Expand` leaves
  like-power terms separate; `ExpandCleanup`'s `UnifySum` collects them anyway. (d) `ExpandCleanup`
  applies `ratdisrep` to each `SimplifyTerm` result before re-summing: `%mr_simplifyTerm` returns a
  CRE (`%mr_together`'s `rat()`, `maxima_rubi_utils.mac:372`; `?caar` = `MRAT`) and Maxima's `+`
  combines CRE operands into ONE canonical fraction, where Mathematica's `Plus` never recombines.
  Without it the cascade is a no-op — measured 2026-09-16: mapping `SimplifyTerm` over e4's three
  partial fractions rebuilt the single quotient `(b x + a)/(cubic)`, `SumQ` false. The CRE is not
  removed from `%mr_together` itself (200+ call sites depend on its behaviour).
- Tickets (§1 Out): the remaining `ExpandIntegrand` branches, filed with their generated call counts.

### 3.5 Evidence

Red first: probes 17 and 18 run on the current tree (core `b98e4748…`, switch defaults) and their
outputs are committed; the changes follow; the probes re-run on the changed tree and the green
outputs are committed beside the red ones. Both probes run their entries through the driver's entry
text with the tree's default switches, so the green records run rules-only.

| probe | content |
|---|---|
| `probes/matcher/17-exact-seen-intpart` | SEEN: probe 16's 78 exact-only-control PASS entries — green: PASS, unless the fire trace attributes a miss to the IntPart change or the entry's P5b PASS came from a nested `integrate` fall-through (the answer then holds `unintegrable` under the rules-only default, which the probe reports as its own category, not a failure). DRIFT: 1.1.1.4 e1, e3, e4, e5, e135 and 1.1.1.7 e1 with the fire trace, the depth-cap hits and whether a float sits on `%mr_seen` at a cap hit — green: no float at a cap hit; the class is recorded. A float-scan of every class 1–3 integrand. INTPART: `truncate` / `floor` on the rationals; `%mr_intPart` / `%mr_fracPart` against Rubi's values; g27 e254, e255, e604, e605 through 1_2_3_2_r34. |
| `probes/matcher/18-expand-expression` | VALUES: `%mr_expandIntegrand` / `%mr_expandExpression` / `%mr_smartApart` / `%mr_expand_x` on e4's integrand, its expanded-denominator form, a repeated linear factor, a polynomial part, an irreducible quadratic (kept), `1/(a+b x^2)` (kept), a radical parameter, a nested-radical parameter, a non-rational factor (`sqrt(x)` times a rational function), an algebraic function `(u_Plus) v` and `(u_Plus)^n v`, `ExpandCleanup`'s reciprocal pair `e/(a+b x) + f/(a-b x)` — expectations derived by hand from the `.m` definitions, compared with the expected term count and a **`radcan`** difference of 0 (`ratsimp(radcan(d))`, §0.4: bare `ratsimp` is too weak on the radical shapes and reports three false defects). ENTRIES: 1.1.1.4 e4 and a fixed sample of 60 of the 805 losses cut at an `%mr_expandIntegrand` rule (the pre-validation list, committed with the probe) — red: the P5b class; green: the class and fire trace recorded, `Results:` counting e4 PASS. |

### 3.6 The corpus queue runner (dropped)

Prototyped and measured on the unchanged tree (ticket `.scratch/corpus-harness/issues/01-queue-runner.md`,
prototype patch beside it): this VM's 24 vCPUs are 12 cores × 2 threads, and 24 busy workers slow
every entry (class 3 in 9.7 min against 20 sharded, but 29 more timeouts and 17 PASS→FAIL); 12
workers keep the walls but project class 1 at ~101 min against 87 sharded. Dropped by the user; the
p5c runs use the sharded launchers.

### 3.7 Unit checks and tree gates

Layer A (`test_maxima_rubi.mac`, 957 → 957 + k, k stated in the plan): the rewritten seen checks
(§3.1); the IntPart/FracPart checks (§3.2); `mr_nested_fallback` both ways on a stub table (a nested
no-rule call returns `mr_unintegrable` / `integrate`); `mr_max_depth` (a cap of 1 hits on a
one-level nesting, the census counter counts it); the §3.4 ports on probe 18's value cases.

Tree gates on the changed tree: the static gate 14 / 0 and byte-identical regeneration;
`test/test_run_records.py` at its new count (the integer switch, the `.caps` merge); `sh
test/build_rules_core.sh` with the fingerprint in the ledger; probe 08 flagless (the loader now
loads `format`); matcher unit suites 53 / 51 / 58; the matcher regression suite 109 in both arms;
`p6_hardwire.py --check` (its anchors re-validated).

Docs: AGENTS.md (Layer A and guard counts, the two run switches and the `.caps` census in the Layer B
and switch-arm sections); the translation-fixes design §3.3 and the parent spec §3.5 pointers; the
utils header of cluster I (the ported cascade); `todo/TODO.md`.

## 4. Re-measurement and the acceptance stop

Plan 3's procedures with the sharded launchers and the prefix `p5c`. Records:
`test/corpus_class<N>.p5c-run1.out` (defaults: rules-only), `p5c-run4.out` (`mr_model_flags`
flipped on the defaults), `p5c-fallback.out` (`mr_nested_fallback=true` with the winning
`mr_model_flags`), each with its `.caps`; `test/corpus_class<N>.p5c-fallback.timeout-rerun/`;
`probes/matcher/10-p5c-attribution.*`.

1. **Preconditions.** The changed tree committed; the core built, its fingerprint in the ledger and
   checked before every launch; §3.7's gates green; probes 17 and 18 green.
2. **Run 1 — the rules-only baseline**, classes 2 → 3 → 1. `p5_gate.py gate` against P0
   (`test/corpus_class{1,2,3}.pre-matcher.out`): complete, switches and wall ceiling must PASS; the
   pass-floor line is informational on this arm (P0 ran with the fall-through). Informational in the
   ledger: `ab_records.py` P5b run 1 → p5c run 1, the `.caps` header lines.
3. **Run 4 — `mr_model_flags=false`** on the defaults, all classes; `p5_gate.py winner
   mr_model_flags` over runs 1 and 4; probe 11 only when the raw winner is the flip. `MF` = the
   noise-filtered winner.
4. **The fall-through arm — `mr_nested_fallback=true`, `mr_model_flags=MF`**, all classes;
   `p5_gate.py gate` against P0 with all four checks required (a pass-floor or wall-ceiling FAIL
   stops); `ab_records.py` P5b run 1 → p5c-fallback and p5c run 1 → p5c-fallback in the ledger (the
   second is how much of the PASS count the fall-through supplies).
5. **Final gates on the fall-through arm.** The 100 s timeout re-checks; a P0-core worktree at
   `0a6664c`; probe 10's `final30`, `p0`, `final120`, `newerror` legs and summaries against P0.
6. **Defect clearance.** Each p5c-fallback PASS→FAIL group gets a mechanism line. A group still
   explained by collapse (ratsimp-type cuts cannot occur; an equal-form route cut by the depth cap is
   reported as ping-pong), by the floor IntPart reading, by the unported `SmartApart` (a nested call on
   an expanded-denominator form), by one of the four translation-fixes defects or a listed sibling is a
   fix failure: **stop and report**. A group whose P5b PASS came from the seen-cut `integrate`
   fall-through and whose p5c route is Rubi's is tagged `route dispatched (was seen-cut integrate
   fall-through)` and presented for acceptance (§0.2). Groups explained by tickets 01–03 or by the
   ticketed `ExpandIntegrand` branches are tagged `none` with the ticket named. Undetermined groups
   are listed.
7. **Final-tree suites** (§3.7 counts).
8. **Acceptance document** `probes/matcher/10-p5c-attribution.acceptance.md`: per class the two arms'
   gate lines, the rules-only PASS count and its `.caps` census beside the fall-through arm's, then
   the fall-through arm's groups in the earlier format (entries rejectable by id, new timeouts, new
   errors). **Stop for the user's acceptance.** It replaces the translation-fixes plan's Task 7 Steps
   6–10; that plan's ledger records the supersession.
9. **After acceptance:** Plan 3 Task 5 (`p6_hardwire.py --check` first), then Task 6 (its acceptance
   record cites the `p5c` records); then the tickets 02/03 plan.

Machine time, estimated from P5b: three full runs ~2 h each (class 1 ~87 min, class 3 ~20, class 2
~5); the 100 s re-checks ~1–1.5 h; probe 10 ~3 h; probe 11 on one switch, if needed, 1–3 h.

## 5. Acceptance criteria

1. Probes 17 and 18 committed with red and green outputs.
2. Layer A, the static gate, `test/test_run_records.py`, the matcher unit suites and the regression
   suite green on the changed tree at their new counts; regeneration byte-identical; probe 08
   flagless.
3. Run 1 passes the gate's complete, switches and wall-ceiling checks; the fall-through arm passes all
   four against P0.
4. Every p5c-fallback PASS→FAIL entry attributed; no group explained by a fix-failure mechanism
   (§4 step 6).
5. The user's per-group acceptance recorded in the ledger.

## 6. Risks and sharp edges

- **Rules-only records are not comparable with P0/P5b.** PASS drops wherever `integrate` answered a
  nested call; the fall-through arm carries the comparison, the rules-only arm is the new baseline.
- **SmartApart changes routes widely.** 291 generated `%mr_expandIntegrand` lines now split rational
  functions; more terms can mean more nested calls and new timeouts. The attribution reads them.
- **`partfrac` and `format` are Maxima's, not Mathematica's.** Term order and grouping differ (§3.4
  deviations); probe 18's value checks compare by `ratsimp` difference and term count, not text.
- **The `format` share package becomes a load dependency** of the loader and the core; probe 08
  re-measures the load and TLS, and the core fingerprint covers `maxima_rubi.mac`.
- **Form-sensitive seen test.** Two rules alternating between two equal forms run to the depth cap;
  the `.caps` census now shows every cap hit.
- **The depth cap may bind.** Rubi's step counts exceed 16 on 272 / 24 / 358 entries; the census
  decides whether the default moves (a later decision, not in this plan).
- **The drift cycle may be real on the substrate.** Probe 17 checks the recorded targets; the
  fallback is approach B by amendment.
- **`mr_model_flags` interacts with the exact test** (stored forms): run 4 re-measures the switch.
- **IntPart forms change nested routes** at up to 204 replacement sites.
- **Disk.** `/` had 5.0 GB free on 2026-09-15; check `df` before the probe 10 legs.
- **Probe 16 does not run on the changed tree** (it asserts `%mr_seenp`); it stays the record of the
  stop.

## 7. Deliverables

- this design (committed);
- plan `docs/superpowers/plans/2026-09-15-matcher-seen-test-intpart.md`, written next (just in
  time): red probes 17 and 18; the run switches and the census (tooling first); the seen test and
  generator; the IntPart reading; the ExpandExpression / SmartApart port; the changed tree's evidence
  and docs; p5c runs 1 and 4 and the winner; the fall-through arm; final gates, attribution, clearance,
  final-tree suites and the acceptance stop;
- the tickets named in §1 Out;
- the records, probes and acceptance document named in §3.5 and §4.
