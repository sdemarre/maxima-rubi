# Matcher substrate — translation fixes: design (the P5 acceptance stop's fix)

Date: 2026-09-14. Branch `matcher-substrate` @ `9a4d4d5` (Plan 3 stopped at Task 4 Step 9).
Parent spec: `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md` (§3.4, §3.5, §4 P5,
§5). Measurements stamped Maxima `branch_5_50_base_84_g4204fb669` (build date 2026-08-31
13:27:47) / SBCL 2.6.7. Design brainstorm with the user 2026-09-14 (handoff
`handoffs/2026-09-14-matcher-translation-defects-fix-plan.md`).

## 0. Context

Plan 3 (`docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.md`) ran the P5 corpus runs and
attributed every PASS→FAIL entry of the final records (`test/corpus_class{1,2,3}.p5-run1.out`)
against P0 (`probes/matcher/10-p5-attribution.acceptance.md`). At the acceptance stop the user
decided (2026-09-14):

1. **Fix defects first.** The defect-tagged groups are rejected. Four translation defects get a fix
   plan with committed probes proving each; the final records and probe 10 are re-run; the
   acceptance stop is repeated. Untagged groups and new timeouts are not accepted yet (their routes
   change).
2. **Restore the exact seen comparison** for the 9.1 collapse family (parent §3.5: "brings back the
   exact comparison as a translation fix, not as a pass").

The defects are pre-existing: the generated cond/repl bodies are byte-identical to P0 (`0a6664c`)
outside the P3 static gate's closed exception list. The substrate's binding made the rules reach
corpus entries. Entries carrying at least one defect tag: class 1 1,072 of 1,833 PASS→FAIL, class 2
3 of 24, class 3 7 of 181 (acceptance document §2).

### 0.1 Decisions made in the brainstorm (user, 2026-09-14)

| question | decision |
|---|---|
| PosQ / NegQ semantics | port Rubi's `PosAux` faithfully into `%mr_posQ`; `%mr_negQ` keeps Rubi's form over it; the strict-sign deviation is retired |
| exact seen comparison scope | every `Int` call of the 9.1 source |
| switch A/B after the fix | re-run P5 runs 1–4 on the fixed tree (winners re-measured), not only the final arm |
| scope beyond the known sites | the four defects plus shape scans; same-mechanism siblings fixed in this plan, others ticketed |
| approach | named predicate entries; static gate keeps base `0a6664c` with new exceptions, each checked by undoing it |
| order oracle | Maxima's internal order (`orderlessp`), measured against the corpus answers' Mathematica order |
| sequence | design §5 below (runs 1–4, noise re-check on every switch, final gates, probe 10, acceptance stop) |

## 1. Scope

In:

- the four translation defects: integer comparisons without the integer test, `%mr_negQ` on
  unknown-sign expressions, `!=` read as a factorial, space as multiplication;
- their same-mechanism siblings found by the shape scans (§3.5), including the utils ports that read
  a Rubi `First`/`Rest` in Maxima's display order;
- the exact seen entry for 9.1 and the deletion of `rubi_hybrid` / `rubi_hybrid_exact` /
  `%mr_hybrid_body`;
- the probes, unit checks and gate changes that prove each;
- re-running P5 (runs 1–4, winners, run 5 if needed, final gates, re-checks, attribution) and
  returning to the acceptance stop.

Out:

- an audit of every translated Rubi predicate against its `.m` definition (e.g. `GtQ`'s
  `RealNumberQ`/`N` reading) — siblings outside the four shapes are ticketed, not fixed;
- matcher changes (`maxima_rubi_match.lisp`, `maxima_rubi_tree.lisp`);
- Plan 3 Tasks 5–6 (they resume after acceptance);
- the rules core's cost-benefit (the "right-size the process" item, raised later).

## 2. Measured basis

Committed evidence:

- Defect evidence and scope: acceptance document §2; mechanism files
  `probes/matcher/10-p5-attribution.mechanisms-*.md` (NEGQ: Rubi's `PosAux`,
  `IntegrationUtilityFunctions.m:608–634`, reads `NegQ[a/c]`, `NegQ[e^2 b^2]`, `NegQ[4 a c e^2]`,
  `NegQ[2(a+b)]` as False; `%mr_negQ` reads them true).
- Rubi definitions (pinned clone): `IGtQ[u_,n_] := IntegerQ[u] && u>n`, likewise `ILtQ`, `IGeQ`,
  `ILeQ` (`IntegrationUtilityFunctions.m:379–395`); `PosQ[u_] := PosAux[TogetherSimplify[u]]`
  (:605–606); `PosAux` (:608–634); `NegQ` (:642).
- Generator: `CMP_OPS` (`generator/generate_rules.py:816–817`) maps `IGtQ`/`ILtQ`/`ILeQ` to bare
  `>`/`<`/`<=`, emitted as `is(a op b)` (:1129–1137); `IGeQ` is absent. `_gap_join` (:98–140) keeps
  a space between `)` and `(`, citing a 2026-08-22 measurement that `(x) (y)` is "the only legal
  spaced form (a product)". The atom walk translates `==` to `=` (:627–636) and has no `!=` case.
- Utils: `%mr_posQ` strict (`maxima_rubi_utils.mac:430–444`, "undecidable sign → false … documented
  deviation"); `%mr_negQ` (:446–449); `%mr_seenp` (:201–212) with exact `member` then a ratsimp
  comparison; `%mr_hybrid_body` / `rubi_hybrid` / `rubi_hybrid_exact` (:277–326), no caller since
  Plan 2; the `OrderedQ` comment (:966) claims "Maxima has no canonical-order predicate".
- Generated call counts (`grep -o`): `%mr_negQ(` class 1 153, class 2 1, class 3 1; `%mr_posQ(`
  class 1 266, class 2 1, class 3 1. Ten class-1 lines contain ` != ` (acceptance document §2).
- Load: `probes/matcher/08-runtime-load.out` (2026-09-13) — standard load 1.4 s wall, `mr_load_all`
  1.0 s, core build 2.8 s.

Ad-hoc measurements of this brainstorm (2026-09-14, scratchpad batch runs, same build). **Not
evidence until committed** — the plan's first task commits each as a probe (§3.5):

- `errcatch((x) (y))` → `[x(y)]` (a noun call, not a product); with `n:5, j:2, p:3`,
  `errcatch((n - j) (p + 1))` → `[]`; the unsimplified form is `MQAPPLY` of `n - j` to `p + 1`.
- `is(a # 1)` → `true`; `is(notequal(a, 1))` → `unknown`; `is(notequal(2, 1))` → `true`;
  `is(notequal(1, 1))` → `false`; `is(notequal(1/2, 0.5))` → `false`. `k != 1` evaluates as
  `k! = 1`: `true` for `k:1`, `false` for `k:2`; `is(3 != 0)` → `false`.
- `part(e, 1)` in display order vs `inflag:true`: `b - a` → `b` vs `-a`; `-a*b` → `a*b` vs `-1`;
  `a - 2*b + c` → `c` vs `a`.
- Internal order (`args` under `inflag:true`) on 21 shapes: `b^2 - 4*a*c` → `[b^2, -(4*a*c)]`;
  `a*d - b*c` → `[-(b*c), a*d]`; `b*c - a*d` → `[b*c, -(a*d)]`; `2*x - 1` → `[-1, 2*x]`;
  `c*x^2 + b*x + a` → `[a, b*x, c*x^2]`; `sqrt(a) - b` → `[sqrt(a), -b]`. Each agrees with the
  Mathematica stored order as recalled, not measured here.
- Corpus answer text keeps Mathematica's `Plus` order (raw grep over all of
  `reference/maxima-syntax-test-suite`, every field): `(-1+x)` 1,004 vs `(x-1)` 0; `(-a+b)` 128 vs
  `(b-a)` 0; `-b*c+a*d` 274 vs `a*d-b*c` 23.
- `describe("ordergreatp", exact)`: `orderlessp`/`ordergreatp` test Maxima's canonical order;
  `orderless`/`ordergreat` change it globally.
- Both `IGeQ[` sites in the class 1–3 sources (1.2.2.2, 3.1.4) are inside `(* … *)`
  (commented-out rules).
- P0's manual 9.1 (`git show 0a6664c:rules/class1/9_1.mac`) calls `rubi_hybrid_exact` in P0 rules
  r6, r21–r25, r27, r28 and `rubi_hybrid` in the others; the generated 9.1 has 25 `mr_int(` calls.
- Standard load without the core, two runs: `maxima_rubi.mac` 0.39–0.42 s, `mr_load_all`
  1.27–1.32 s, process wall 1.72–1.80 s.

## 3. Design

### 3.1 Translation fixes (generator)

1. **Integer comparisons.** `IGtQ`, `ILtQ`, `ILeQ` leave `CMP_OPS`; with `IGeQ` they translate to
   `%mr_iGtQ(u, n)`, `%mr_iLtQ(u, n)`, `%mr_iLeQ(u, n)`, `%mr_iGeQ(u, n)`. Utils defines each as
   `if integerp(u) then is(u OP n) = true else false` (Rubi :379–395), so the result is always
   `true`/`false` and `u` (often a `%mr_simp(…)` call) is evaluated once. Rubi's integer
   comparisons take two arguments; a three-argument call is a `GenError`. `IGeQ` has no live site
   in classes 1–3 and is mapped for classes 4+ (5.3.4, 7.3.x, 4.7.9 use it).
2. **`!=`.** Translated to `notequal(A, B)`. The relational partition of `_expand_chains` (:678)
   gains `!=` as a two-character operator, and a relation whose operator is `!=` is emitted as
   `notequal(L, R)` whether or not it belongs to a chain (a lone relation is otherwise left
   untouched there). `notequal` has
   Mathematica `Unequal`'s reading: numbers compare by value, a symbolic operand gives `unknown`,
   which the dispatcher rejects (`is(r) = true` accepts). Ten sites; the two `3 != 0` conditions
   (1_2_2_4 r29/r30), false until now, become true.
3. **Juxtaposition.** `_gap_join` drops the `)`-then-`(` exception and emits `)*(`. Its docstring's
   2026-08-22 claim is replaced by probe 12's measurement.
4. **9.1 `Int`.** For the 9.1 source (key `9_1`), `Int` and `IntHide` translate to
   `mr_int_exact(…)` (§3.3); every other source keeps `mr_int`.
5. **Siblings.** Probe 13's scans (§3.5) list every site of each shape; a site with the same
   mechanism is fixed by the same translation rule, anything else is ticketed under
   `.scratch/`.

Regeneration stays deterministic: a second `generate_rules.py --class <1|2|3>` leaves
`git status --porcelain rules/` empty.

### 3.2 The PosAux port (utils)

- `%mr_posQ(u) := %mr_posAux(%mr_togetherSimplify(u))` (Rubi :605–606).
- `%mr_negQ(u)`: `not %mr_posQ(u) and %mr_neQ(u, 0)`, strictly `true`/`false` (Rubi :642) —
  unchanged in form, correct once `%mr_posQ` is.
- `%mr_posAux(u)`, branch by branch (Rubi :608–634):
  1. an explicit number (`numberp`, or a complex number with explicit real and imaginary parts):
     complex → `%mr_posAux` of the imaginary part if the real part is 0, else of the real part;
     real → `is(u > 0)`;
  2. a numeric constant (`constantp(u)`, e.g. `%pi - 3`): simplify the real part; if it is a
     number, decide on it (on the simplified imaginary part when it is 0); otherwise
     `w : float(u)`, and the result is: `w` is an explicit number in branch 1's sense (real or
     complex) and `%mr_posAux(w)`;
  3. otherwise `v : is(u > 0)`; `true` or `false` decides (Rubi's `Refine[u>0]`);
  4. a power: integer exponent → `evenp(exponent) or %mr_posAux(base)`; otherwise `true`;
  5. a product: factors in internal order; `%mr_posAux(first)` → `%mr_posAux(rest)`, else
     `not %mr_posAux(rest)`, where rest is the product of the remaining factors;
  6. a sum: `%mr_posAux(first term)`, internal order;
  7. anything else (a symbol, a function call): `true`.
- **Order.** First/Rest read Maxima's internal argument order (`args` / `part` under
  `inflag:true`), which is the canonical order `orderlessp` tests. `orderless`/`ordergreat` are not
  used (they change every stored form of the session). Agreement with Mathematica's order is
  measured by probe 14; frequent disagreeing shapes get an ordering shim, rare ones are recorded as
  a deviation.
- **Stated deviation.** Maxima's `is()` treats symbols as real and consults the `assume` database;
  Rubi's `Refine` runs without assumptions. The corpus driver makes no assumptions. The cases where
  "symbols are real" decides before the structural branches are covered by the unit checks.
- **Siblings.** Every utils port of a Rubi `First`/`Rest` over a sum or product that reads display
  order (`part(u, 1)`, `first`, `rest` without `inflag:true`) switches to internal order —
  `%mr_rt_negSumBaseQ`, `%mr_rt_allNegTermQ`, `%mr_rt_someNegTermQ`, `%mr_splitSum_aux` and every
  other site probe 13 lists. Their internal `%mr_posQ`/`%mr_negQ` calls (Rt, SplitProduct, the
  TestAux sign flip at :4271/:4282) follow the port.
- The strict-sign comments (:430–435, :4076) and the `OrderedQ` comment (:966) are corrected.

### 3.3 The exact seen entry (runtime)

- `mr_top` gains a seen mode through one shared body. `mr_int(f, x)` keeps `%mr_seenp` (exact
  `member`, then the ratsimp comparison that guards the float/rational drift cycle, 891240b).
  `mr_int_exact(f, x)` tests exact `member` only. Everything else is the same path: the depth cap
  (`%mr_max_depth` 16), the `%mr_seen` push/pop, the `mr_model_flags` binding around
  `%mr_dispatch_tree`, and the `integrate` fall-through on a depth-cap hit, a seen hit or no rule.
  This is P0's `rubi_hybrid_exact` without the pass gates it once lifted.
- Why every 9.1 call: each 9.1 rule rewrites the integrand to an algebraically equal form, so the
  ratsimp comparison reads the rewrite as a loop by construction (class 2 g10 = 2.1 e15; class 1
  g106 = 1.2.1.2 e1734–e1736; 1.2.1.4 e810's P0 route).
- **Cycle bound.** An exact repeat is cut by `member`; two 9.1 rules rewriting back and forth
  between different equal forms stop at the depth cap and fall through to `integrate`. The cost is
  watched by the median-wall gate; probe 10's fire traces show any 9.1 ping-pong.
- **Deleted in this plan:** `rubi_hybrid`, `rubi_hybrid_exact`, `%mr_hybrid_body`. No rule file
  calls them; `rubi_hybrid` equals `mr_int` now that the passes are gone; the exact mode lives on
  in `mr_int_exact`. The rationale block (origin 1.2.1.3 e839; the collapse rules cannot re-trigger
  on their own output) moves onto `mr_int_exact`. Any dispatch-suite reference is updated with the
  deletion. Plan 3 Task 5's `rubi_hybrid` deletion becomes a no-op, confirmed by its
  `p6_hardwire.py --check` re-run.

### 3.4 The P3 static gate

`test/check_generated_rules.py` keeps base `0a6664c`. New closed exceptions, each verified by
undoing the transformation on the new body and comparing with the base body:

| exception | undo |
|---|---|
| integer comparisons | `%mr_iGtQ(A, B)` → `is(A > B)`; likewise `%mr_iLtQ` `<`, `%mr_iLeQ` `<=` |
| `!=` | `notequal(A, B)` → `A != B` |
| juxtaposition | `)*(` → `) (` at the sites probe 13 lists |

Each exception's count is pinned to probe 13's measured count. 9.1 stays exempt. `ENTRY_CALL` gains
`mr_int_exact` and loses `rubi_hybrid` / `rubi_hybrid_exact`. The gate's `Results:` count grows by
the number of new checks, stated in the plan.

### 3.5 Evidence

**Red first.** Each defect's probe is written and run on the unfixed tree and its output committed;
the fix follows; the probe re-runs and the green output is committed beside the red one.

| probe | kind | content |
|---|---|---|
| `probes/matcher/12-translation-defects` | Maxima batch | NE: `k != 1` parse form, `is(k != 1)` for k = 0, 1, 2, `is(3 != 0)`, `notequal` on symbol / numbers / rational vs float, the 10 generated conds on a k ≠ 1 binding (red false → green true). MUL: `(x) (y)`, `(n - j) (p + 1)` on numbers, `] (`, `) x`, `2 (x)`, `x (y)`; `1_1_4_1_r1`'s repl on a binding (red error → green value). IGT: the four `%mr_i*Q` on integer / fraction / float / symbol / integer-valued expression; `2_1_r10`'s cond with fractional `p` (red true → green false). NEGQ: `%mr_posQ` / `%mr_negQ` on the §3.6 cases |
| `probes/matcher/13-translation-shape-scan` | Python, no Maxima | integer-comparison heads, source count vs emitted count per class; leftover Mathematica operators (`!=`, `===`, `=!=`, prefix `!`, `@`, `/@`, `->`, `:>`); every surviving whitespace gap between two terms; utils First/Rest ports reading display order. Output: the sibling list; `Results:` requires 0 residual sites per shape after the fix, ticketed sites excepted |
| `probes/matcher/14-mma-order-agreement` | Maxima batch | every expected answer of classes 1–3 parsed with `simp:false` (Mathematica's printed order), simplified, each `Plus` node's term order compared with the internal order; `Times` compared on its leading numeric coefficient only (the printed form splits off the denominator). Output: agreement rate, every disagreeing shape |
| `probes/matcher/15-collapse-exact` | driver entry text, `rubi_verbose` | 2.1 e15, 1.2.1.2 e1734–e1736, 1.2.1.4 e810, 1.2.1.3 e839 on the fixed core; verdicts and routes against their P0 routes |

### 3.6 Unit checks and tree gates

Layer A (`test_maxima_rubi.mac`, 898 → 898 + k, k stated in the plan):

- the four `%mr_i*Q` heads on integer, non-integer and symbolic arguments;
- a `notequal` condition; `1_1_4_1_r1`'s repl on numbers;
- every `PosAux` branch, with Rubi-derived expectations: `NegQ[a/c]`, `NegQ[e^2 b^2]`,
  `NegQ[4 a c e^2]`, `NegQ[2(a+b)]`, `NegQ[b^2-4ac]` false; `NegQ[-a]`, `NegQ[-4 e^2]` true;
  `PosQ[%pi-4]` false; `PosQ[%i]` true; the existing `posQ a (undecidable -> false)` check flips
  to true;
- the sibling ports in internal order (e.g. `%mr_rt_negSumBaseQ(b - a)`);
- `mr_int_exact` vs `mr_int`: a ratsimp-identical rewrite with a different stored form dispatches
  under `mr_int_exact` and is a seen hit under `mr_int`; an exact repeat under `mr_int_exact` takes
  the fall-through.

Tree gates on the fixed tree:

- the static gate green (§3.4); regeneration byte-identical;
- `sh test/build_rules_core.sh`, fingerprint recorded;
- probe 08 re-run flagless (utils and rule files changed), record rewritten;
- matcher unit suites (match 53, tree 51, dispatch 58 ± the §3.3 reference update) green;
- the matcher regression suite, 109 in both arms, on the final tree (Plan 3 Task 4 Step 6);
- `test/test_driver_radcan_fallback.py` stays outside the gates (red since P4, fixture).

Docs: AGENTS.md (Layer A and static-gate counts); parent spec §3.4's exception list and §3.5's
`rubi_hybrid` paragraph amended with a pointer to this design; the corrected generator and utils
comments.

## 4. Re-measurement and the acceptance stop

Plan 3's procedures are reused verbatim with new record names. The defective tree's records stay
committed; the new ones use the prefix `p5b`: `test/corpus_class<N>.p5b-run<K>.out`,
`test/corpus_class<N>.p5b-final.timeout-rerun/`, `probes/matcher/10-p5b-attribution.*`.

1. **Preconditions.** The fixed tree committed; the core built; its fingerprint in the ledger and
   checked before every launch.
2. **Run 1 (defaults)**, classes 2 → 3 → 1 (Plan 3 Task 2 procedure); `p5_gate.py gate` against
   the P0 records with Plan 3's stop rules (a wall-ceiling FAIL or a harness failure stops).
   Informational, not a gate: `ab_records.py test/corpus_class<N>.p5-run1.out
   test/corpus_class<N>.p5b-run1.out` per class — what the fix moved — in the ledger.
3. **Runs 2–4**, one switch flipped per run, all three classes (Plan 3 Task 3 Steps 1–4).
4. **Winners.** The raw `p5_gate.py winner` per switch, then probe 11
   (`probes/matcher/11-arm-noise-recheck.py`) on **all three switches**: the changed entries re-run
   3× per arm, interleaved, and the winner rule applied to what reproduces. `FINAL_ARM` comes from
   the noise-filtered winners; run 5 only when it is not empty.
5. **Final gates** (Plan 3 Task 4 Steps 1, 3, 4): `p5_gate.py gate` on the final records against
   P0; the 100 s timeout re-checks; a P0-core worktree at `0a6664c`; probe 10's `final30`, `p0`,
   `final120` and `newerror` legs and summaries. Extension: the `newerror` leg also captures the
   error text, and the attribution captures the answer of `unverified` entries, so the error kind
   and "wrong vs unverifiable" are recorded.
6. **Defect clearance.** Each group's mechanism line states whether a fixed defect (IGT, NEGQ, NE,
   MUL, collapse) or a probe-13 sibling still explains it. **A group that does is a fix failure:
   stop and report** — it is not presented for acceptance.
7. **Final-tree suites** (Plan 3 Task 4 Step 6, with the new counts).
8. **Acceptance document** `probes/matcher/10-p5b-attribution.acceptance.md` in the format of the
   first one (per group, entries rejectable by id, new timeouts, new errors). **Stop for the user's
   acceptance.**
9. **After acceptance:** Plan 3 Task 5 (`p6_hardwire.py --check` first; the `rubi_hybrid` step is a
   no-op; the variants follow the new winners), then Task 6 (the acceptance record cites the `p5b`
   records).

Machine time, estimated from Plan 3's runs: ~15–20 h — four full runs ~2 h each (a fifth if the
winners change), probe 11 on three switches 1–3 h each (`mr_cond_retry` changes ~2,000 entries),
the 100 s re-checks ~2 h, probe 10 ~3 h.

## 5. Acceptance criteria

1. Probes 12–15 committed with red (where a red state exists) and green outputs; probe 13 reads 0
   residual sites per shape outside its ticket list.
2. Layer A, the static gate, the matcher unit suites and the regression suite green on the fixed
   tree at their new counts; regeneration byte-identical; probe 08 flagless.
3. The `p5b` final records pass `p5_gate.py gate` against P0 (complete, arm, pass floor, wall
   ceiling).
4. Every `p5b` PASS→FAIL entry attributed; no group explained by a fixed defect or a listed sibling
   (§4 step 6).
5. The user's per-group acceptance recorded in the ledger.

## 6. Risks and sharp edges

- **PosAux moves 268 posQ and 155 negQ generated sites, plus the utils that call them.** Entries
  verified today through the strict reading may fail; the acceptance stop against P0 reads them.
- **Order.** Maxima's internal order and Mathematica's canonical order can disagree on shapes probe
  14 has not seen; `PosAux`'s sum branch reads only the first term, so one disagreement flips a
  sign. Probe 14 bounds it on the corpus answers; integrands in the middle of a chain are not in
  that sample.
- **`is()` assumes real symbols.** Branch 3 can decide a sign that Rubi's `Refine` leaves open,
  skipping the structural branches Rubi takes. On the shapes reasoned through while designing (not
  measured) — `-(a^2+1)`, `exp(a)`, `-a^2`, `a^2 + 1` — the decided value equals Rubi's structural
  result; no differing shape is known. The unit checks include decided-by-`is()` cases, and a
  disagreement any check finds is recorded as a deviation.
- **Dead conditions become live.** `3 != 0` (1_2_2_4 r29/r30) and every condition with a narrowed
  integer test change routes; new timeouts or errors are attributed like any other.
- **9.1 ping-pong** under `mr_int_exact` costs up to 16 dispatch levels before the fall-through;
  the median-wall gate and the fire traces watch it.
- **The winners may change**, which selects other Task 5 variants; `p6_hardwire.py --check`
  re-validates its anchors after this plan touches the generator, the utils and the rule files.
- **Probe 13's shape list is finite.** A juxtaposition or operator shape it does not scan stays
  undetected; its scan list is committed so it can be extended.

## 7. Deliverables

- this design (committed);
- plan `docs/superpowers/plans/2026-09-14-matcher-translation-fixes.md`, written next (just in time),
  in about seven tasks: red probes 12–14; generator fixes and gate exceptions; the PosAux port and
  siblings; `mr_int_exact` and the deletions; regeneration, core, probe 08, green probes, Layer A,
  docs; P5 runs 1–4 and the winners; final gates, attribution, the acceptance stop;
- the records, probes and acceptance document named in §3.5 and §4.
