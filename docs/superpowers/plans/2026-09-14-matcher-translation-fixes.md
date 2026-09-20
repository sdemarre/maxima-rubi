# Matcher Substrate — Translation Fixes Implementation Plan (the P5 acceptance stop's fix)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the four translation defects the P5 acceptance stop rejected (integer comparisons
without the integer test, `%mr_negQ` on unknown-sign expressions, `!=` read as a factorial, space
as multiplication) and their same-mechanism siblings, restore the exact seen comparison for the
9.1 rules, prove each with committed red/green probes, then re-run P5 on the fixed tree (runs 1–4,
noise-filtered winners, final gates, attribution) and return to the acceptance stop.

**Architecture:** Task 1 commits the red records of probes 12, 13 and 15 on the unfixed tree.
Tasks 2–4 change the code test-first, each from one attachment patch whose Layer A part is applied
before its code part: the exact seen entry `mr_int_exact` (Task 2), the generator's translation of
the integer comparisons, `!=`, juxtaposition and the 9.1 `Int` calls, with the utils entries they
emit, the static gate's new exceptions and the regenerated rule files (Task 3), and the PosAux port
with the First/Rest siblings (Task 4). Task 5 takes the fixed tree's evidence (probe 08, the green
records, the Plan 3 P6 script update) and the docs. Tasks 6–7 re-run P5 with Plan 3's procedures
under `p5b` record names, attribute every PASS→FAIL with an extended probe 10, check that no group is
still explained by a fixed defect, and stop for the user's acceptance.

**Tech Stack:** Maxima `branch_5_50_base_84_g4204fb669` (build date 2026-08-31 13:27:47) /
SBCL 2.6.7; Python 3 generator, gates and probes.

**Spec:** `docs/superpowers/specs/2026-09-14-matcher-translation-fixes-design.md` (committed
`1b8ee12`, review amendment `cff760b`) — §3 design, §4 re-measurement and the acceptance stop, §5
acceptance criteria, §6 risks. Parent spec `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`
(§3.4, §3.5, §4 P5). Plan 3 (`docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.md`) is
stopped at Task 4 Step 9; its Tasks 2–4 procedures are reused here; its Tasks 5–6 resume after this
plan's acceptance. Handoff: `handoffs/2026-09-14-matcher-translation-fixes-plan.md`.

**Attachments:** `docs/superpowers/plans/2026-09-14-matcher-translation-fixes.files/`, committed with
this plan (below `A=docs/superpowers/plans/2026-09-14-matcher-translation-fixes.files`):

| attachment | content | used by |
|---|---|---|
| `probes/12-translation-defects.mac`, `.sh` | NE / MUL / IGT / NEGQ checks, NORM measurements (Maxima) | Task 1 Step 2 |
| `probes/13-translation-shape-scan.py` | IGT counts, leftover operators, juxtaposition gaps, the First/Rest table (no Maxima) | Task 1 Step 2 |
| `probes/15-collapse-exact.py` | the collapse entries through the driver's entry text, per core | Task 1 Step 2 |
| `probes/14-mma-order-agreement.py` | Maxima internal order vs the corpus answers' Mathematica order; PosAux flips | Task 4 Step 6 |
| `patches/task2-seen-entry.patch` | `maxima_rubi_utils.mac` (`%mr_top_body`, `mr_int_exact`, the hybrid deletion), `test_maxima_rubi.mac` (5 checks) | Task 2 |
| `patches/task3-translation.patch` | `generator/generate_rules.py`, `maxima_rubi_utils.mac` (`%mr_i*Q`), `test/check_generated_rules.py`, `test_maxima_rubi.mac` (17 checks) | Task 3 |
| `patches/task4-posaux.patch` | `maxima_rubi_utils.mac` (PosAux port, siblings, IntPart/FracPart, comments), `test_maxima_rubi.mac` (35 checks, one flipped) | Task 4 |
| `tickets/01-case-fold-order-shim.md` | the case-fold order shim ticket | Task 4 Step 7 |
| `patches/task5-p6-hardwire.patch` | Plan 3's `p6/p6_hardwire.py` without the hybrid and `ENTRY_CALL` steps | Task 5 Step 1 |
| `patches/task7-probe10-extension.patch` | probe 10: answers of `unverified` rows, error text of `error` rows, the summary's `--newerror` block | Task 7 Step 3 |

**User decisions taken while writing (2026-09-14):**

1. Design file reviewed; `%mr_togetherSimplify` kept with the normalizer deviation stated (design
   `cff760b`).
2. Pre-validation: every code change, probe and gate of Tasks 1–5 and the probe 10 extension ran in
   a throwaway worktree before this plan was written; Tasks 6–7 are measurement.
3. Execution: `superpowers:subagent-driven-development`; recovery workspace (gitignored)
   `.superpowers/sdd/2026-09-14-matcher-translation-fixes/`; tracked ledger section
   `## Plan: 2026-09-14 matcher translation fixes (branch matcher-substrate)` in
   `.superpowers/sdd/progress.md`.
4. **Order** (design §3.2: "frequent disagreeing shapes get an ordering shim, rare ones are recorded
   as a deviation"): Maxima's internal order stays, recorded as a stated deviation; the case-fold
   shim is ticketed (`.scratch/matcher-translation-fixes/issues/01-case-fold-order-shim.md`, Task 4).
   Probe 14's pre-validation figures: PosAux sum-branch flips 3.6 % / 2.6 % / 2.3 % of the corpus
   answers' sum nodes (classes 1 / 2 / 3); a case-fold rename removes 3,265 / 1 / 0 of them; the rest
   follow Mathematica's product-ordering rules.
5. **1.2.1.4 e810** (probe 15): still `deferred` on the fixed core (only `1_2_1_3_r15` fires; the P0
   route started with `1_1_1_4_r40`). Not diagnosed while writing; attributed in Task 7 like any
   other group — if its mechanism is a fixed defect or a listed sibling, Task 7's defect clearance
   stops.

**Deviations from the design's wording (stated, not silent):**

1. *Task order* (design §7). `mr_int_exact` comes first (Task 2): the regenerated 9.1 calls it.
   Regeneration is part of Task 3 (the static gate reads the regenerated files), and each code task
   carries its own Layer A checks (tests first) instead of one Layer A step in Task 5.
2. *Probe 14 placement* (design §3.5, §7 "red probes 12–14"). Probe 14 has no red state and counts
   PosAux verdict flips, which needs the port: it runs in Task 4.
3. *Probe 13 IGT* (design §3.5). Nine source calls (8 `IGtQ`, 1 `ILtQ`) sit in rule-file utility
   definitions (`IntLinearQ` 1.1.1.2, `IntBinomialQ` 1.1.3.2/1.1.3.3/1.1.3.4, `IntQuadraticQ`
   1.2.1.2), which the generator does not emit: they are hand-ported (`%mr_intLinearQ`,
   `%mr_intBinomialQ7/8/10`, `%mr_intQuadraticQ`) through `%mr_IGtQ` / `%mr_ILtQ`, which keep the
   integer test. Probe 13 checks those ports instead of an emitted count. `%mr_i*Q` sit next to
   `%mr_IGtQ` / `%mr_ILtQ` (their callers are unchanged).
4. *Siblings* (design §3.2 names four). Probe 13's First/Rest table classifies the 45 Rubi utility
   functions that read `First`/`Rest`/`Last`: 10 internal-order readers (PosAux, NegSumBaseQ,
   RemoveContentAux, SignOfFactor, ContentFactorAux, SplitProduct, RtAux, SplitSum, UnifyTerm,
   UnifyTerms — ports `%mr_posAux`, `%mr_rt_negSumBaseQ`, `%mr_removeContentAux`,
   `%mr_signOfFactor`, `%mr_contentFactor`, `%mr_product_factors`, `%mr_splitSum_aux`,
   `%mr_unifySum`), 14 order-independent ports (AllNegTermQ and SomeNegTermQ among them: And/Or over
   every term, so they keep display order), 21 unported. `%mr_removeContentAux` also read the strict
   `%mr_sign` where Rubi reads `NegQ` (the NEGQ mechanism) and now calls `%mr_negQ`.
   `%mr_intPart_aux` / `%mr_fracPart_aux` test `RationalQ` first: they reached a negative rational
   through the display `-` node, which the internal-order `%mr_product_factors` no longer shows (a
   Rational is atomic in the `.m` too). No sibling needed a ticket.
5. *PosAux branch 3* (design §3.2). `is(u > 0)` runs only on an expression free of `%i`:
   `is(%i*a > 0)` answers `false` (probe 12 NEGQ, `PosQ %i a`), where `Refine` stays undecided and
   Rubi's structural branches read True.
6. *Static gate juxtaposition exception* (design §3.4 table "`)*(` → `) (`"). Checked by redoing
   `) (` → `)*(` on the base body, the same transformation in the other direction; the three
   exception counts are pinned: 1,283 integer comparisons, 10 `notequal`, 1 juxtaposition.
7. *Probe 15 records* (design §3.5 "against their P0 routes"): three records — P0 core, the unfixed
   core (red), the fixed core (green).
8. *Plan 3's P6 script* (design §3.3 "Plan 3 Task 5's `rubi_hybrid` deletion becomes a no-op").
   `p6_hardwire.py --check` fails on the fixed tree (its hybrid block markers are gone), so Task 5
   patches the script: the hybrid deletion and the `ENTRY_CALL` edit are removed (pre-validated:
   `anchors ok: 8 combinations`). Plan 3 Task 5 still re-runs `--check` first after acceptance.
9. *Probe 10 extension* (design §4 step 5): every entry prints its answer (cut at 300 characters)
   after the CLASS line; an `unverified` row ends `ans=<answer>`, an `error` row ends `err=<message>`;
   the summary prints both under the entry and, with `--newerror`, a `NEW ERRORS` block. The
   `newerror` leg runs for every class.
10. *Records* (design §4): `test/corpus_class<N>.p5b-run<K>.out`,
    `test/corpus_class<N>.p5b-final.timeout-rerun/`, `probes/matcher/11-arm-noise-recheck.p5b.<switch>.out`,
    `probes/matcher/10-p5b-attribution.*`; the probe 10 and 11 scripts keep their names.

## Pre-validation (plan-writing session 2026-09-14, build `branch_5_50_base_84_g4204fb669` / SBCL 2.6.7)

Expectations, not citations: Tasks 1–7 re-take and commit every figure.

- *Prototype*: throwaway worktree `.claude/worktrees/fixes-proto` (branch `fixes-prevalidation`, never
  merged) on `cff760b`. Final tree: Layer A `955 passed, 0 failed` (flagless and with the flag, probe
  08); matcher suites 53 / 51 / 58; static gate 14 / 0; probe 12 59 / 0; probe 13 90 / 0; matcher
  regression suite `Results: 109 passed, 0 failed` in both arms; regeneration byte-identical;
  `p6_hardwire.py --check` → `anchors ok: 8 combinations`; probe 10 extension on class 2 `passfail`
  (24 entries, `ans=` rows) and class 3 `newerror` (3 entries, all `err=Heap exhausted during garbage
  collection … Heap exhausted, game over.`).
- *Replay*: a fresh worktree at `cff760b`, only this plan's attachments, applied as Tasks 1–5 and
  Task 7 Step 3 say (tests part, then code part): every changed file and all 87 rule files
  byte-identical to the prototype, and the per-task figures in the steps below.
- *Measurement figures of the prototype* (design §2's ad-hoc list, now probe outputs): probe 14 —
  class 1 first-term agreement 0.9254, whole-order 0.8909, PosAux flips 10,104 of 279,107 sum nodes
  (case fold removes 3,265); class 2 0.9495 / 0.9376 / 138 of 5,421 (1); class 3 0.9584 / 0.9493 /
  970 of 41,899 (0); answer-level errors 22 / 0 / 11. Probe 12 NORM — `%mr_togetherSimplify` 0.40 /
  1.85 ms per call on the two expanded polynomials, the factor-of-num/denom fallback 2.05 / 6.55 ms.

## Global Constraints

Every task's requirements implicitly include this section.

- **Build (stamp, never pin):** every committed measurement output carries `build_info()` (version and
  timestamp) or, for a no-Maxima script, the run date and git HEAD; corpus records carry the merge's
  `maxima:` lines.
- **Branch `matcher-substrate`**; the base is this plan's commit (parent `cff760b`). Default branch
  `master`; push only when asked.
- **Tests first:** in Tasks 2–4 the patch's `test_maxima_rubi.mac` part is applied and run (red)
  before its code part.
- **30 s corpus cap STAYS** (user decision 2026-08-27); the 100 s timeout re-check answers "is the cap
  the limit?".
- **One corpus-scale run at a time; walls are gates.** While a sharded run, a timeout re-check, probe
  10, 11 or 14 is live, run nothing heavier than reading files. Busy check before every launch:
  `ps -eo args | grep -E '(^|/)python3 .*(corpus_driver|corpus_class1_driver|10-p5-attribution|11-arm-noise|14-mma-order)' | grep -v grep`
  prints nothing.
- **Long runs detached, never blocking a tool call:** launch with `setsid … &` (or the launchers) and
  wait with one `run_in_background` loop whose exit notifies. **Launch the next run before asking the
  user a question** (a question in the same tool batch as a launch left the machine idle ~2 h in
  Plan 3).
- **stdin `/dev/null`** for every direct maxima/sbcl invocation (a fatal SBCL error drops into `ldb`,
  which reads stdin — probe 09).
- **TLS:** no flag required (`probes/matcher/08-runtime-load.out`); Task 5 re-measures it flagless.
- **The human gate:** Task 7 ends at a stop; every PASS→FAIL of the `p5b` final records is accepted
  per group by the user (entries rejectable by id); no subagent or controller ruling accepts one.
  Plan 3 Tasks 5–6 start only after the acceptance is recorded.
- **Stop rules are stops:** where a step says *stop and report to the user*, the task ends there
  with its evidence committed; nothing downstream starts.
- **Git:** never `git add -A` (untracked campaign logs); commit messages end with the executing
  session's `Claude-Session:` trailer and never `Co-Authored-By`; `git merge -F -` does not read stdin
  here (write the message to a file).
- **Test protocol:** every suite prints `PASS:`/`FAIL:` lines and ends `Results: <n> passed, <m>
  failed`; a missing Results line is a failure.

## File structure

| file | responsibility | task |
|---|---|---|
| `probes/matcher/12-translation-defects.{mac,sh}` (create), `.red.out`, `.out` | the four defects' behaviour, red then green; NORM | 1, 5 |
| `probes/matcher/13-translation-shape-scan.py` (create), `.red.out`, `.out` | the shape scans, red then green | 1, 5 |
| `probes/matcher/15-collapse-exact.py` (create), `.p0.out`, `.red.out`, `.out` | the collapse entries per core | 1, 5 |
| `probes/matcher/14-mma-order-agreement.{py,out}` (create) | internal vs Mathematica order; PosAux flips | 4 |
| `maxima_rubi_utils.mac` (modify) | `%mr_top_body` / `mr_int_exact`, hybrid deleted (2); `%mr_i*Q` (3); `%mr_posAux` / `%mr_posQ`, `%mr_rest_in` / `%mr_args_in`, siblings, IntPart/FracPart, comments (4) | 2, 3, 4 |
| `generator/generate_rules.py` (modify) | `INT_CMP`, `_relation_items` and the `!=` pass, `_gap_join`, the 9.1 `Int` entry | 3 |
| `rules/class{1,2,3}/*.mac` (regenerate) | 79 files | 3 |
| `test/check_generated_rules.py` (modify) | `ENTRY_CALL`; the three exception undos and counts (11 → 14) | 3 |
| `test_maxima_rubi.mac` (modify) | `test_translation_fixes_seen` (5), `_generator` (17), `_posaux` (35); `posQ a` flips (898 → 955) | 2, 3, 4 |
| `.scratch/matcher-translation-fixes/issues/01-case-fold-order-shim.md` (create) | the order-shim ticket | 4 |
| `docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.files/p6/p6_hardwire.py` (modify) | no hybrid / `ENTRY_CALL` steps | 5 |
| `probes/matcher/08-runtime-load.out` (regenerate) | load, TLS, Layer A, core on the fixed tree | 5 |
| `AGENTS.md`, `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`, `todo/TODO.md` (modify) | counts; §3.4 / §3.5 amendments; status | 5, 7 |
| `test/corpus_class{1,2,3}.p5b-run{1,2,3,4[,5]}.out` (create) | the P5b records | 6 |
| `probes/matcher/11-arm-noise-recheck.p5b.{mr_flat_wide,mr_cond_retry,mr_model_flags}.out` (create) | noise-filtered winners | 6 |
| `probes/matcher/10-p5-attribution.py`, `.summary.py` (modify) | the extension | 7 |
| `test/corpus_class{1,2,3}.p5b-final.timeout-rerun/` (create) | 100 s re-checks | 7 |
| `probes/matcher/10-p5b-attribution.*` (create) | legs, summaries, mechanism lines, acceptance document | 7 |
| `test/matcher/{roundtrip,controls,spike01,gate}.out`, `{roundtrip,gate}.flags.out` (regenerate) | regression suite on the final tree | 7 |
| `.superpowers/sdd/progress.md` (modify) | the ledger | 1–7 |

## Task overview

| task | deliverable | gate |
|---|---|---|
| 1 | red records of probes 12, 13, 15 (P0 and red cores) | probe 12 16 / 43; probe 13 71 / 19; probe 15 P0 6 / 0, red 1 / 5 |
| 2 | `mr_int_exact`; hybrid deleted | Layer A red 899 / 4 → 903 / 0; dispatch 58 / 0 |
| 3 | generator fixes; `%mr_i*Q`; static gate exceptions; rules regenerated | Layer A red 906 / 14 → 920 / 0; static gate 11 / 3 before regeneration → 14 / 0; regeneration byte-identical; probe 13 80 / 10; probe 12 42 / 17 |
| 4 | PosAux port; siblings; probe 14; ticket | Layer A red 934 / 21 → 955 / 0; probe 12 59 / 0; probe 13 90 / 0; suites 53 / 51 / 58; static gate 14 / 0 |
| 5 | fixed-tree evidence; P6 script patch; docs | probe 08 flagless 955 / 58; green records 12 (59/0), 13 (90/0), 15 (5/1); `anchors ok: 8 combinations` |
| 6 | P5b runs 1–4 (+5); probe 11 on the three switches; final arm | complete records; `p5_gate.py gate` wall ceiling PASS on run 1 (else stop) |
| 7 | final gates; 100 s re-checks; probe 10 (extended); defect clearance; final-tree suites; acceptance document; **stop** | gates 4 / 0; summaries `0 failed`; no group explained by a fixed defect (else stop); suites green; user acceptance |

---

### Task 1: Red records — probes 12, 13 and 15 on the unfixed tree

Branch: `matcher-substrate`. No source file changes.

**Files:**
- Create: `probes/matcher/12-translation-defects.mac`, `12-translation-defects.sh`,
  `12-translation-defects.red.out`; `probes/matcher/13-translation-shape-scan.py`,
  `13-translation-shape-scan.red.out`; `probes/matcher/15-collapse-exact.py`,
  `15-collapse-exact.p0.out`, `15-collapse-exact.red.out`
- Modify: `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: attachments `probes/`; the P0 commit `0a6664c`.
- Produces: the red records Task 5's green records are read against; the probes Tasks 3–5 re-run.
  Probe 12 checks the fixed behaviour through the names Tasks 3–4 define: `%mr_iGtQ(u, n)`,
  `%mr_iLtQ`, `%mr_iLeQ`, `%mr_iGeQ` (true/false), `%mr_posQ(u)`, `%mr_negQ(u)`,
  `%mr_rt_negSumBaseQ(u)`, `%mr_rt_someNegTermQ(u)`, `%mr_rt_allNegTermQ(u)`, and the generated
  `_mr_cond_<key>_r<n>(mm, x)` / `_mr_repl_1_1_4_1_r1(mm, x)`.

- [ ] **Step 1: Preconditions**

```bash
git status --porcelain -- '*.py' '*.lisp' '*.mac' '*.sh' | grep -v '^??'   # must print nothing
git log --oneline -1                                                        # this plan's commit
sh test/build_rules_core.sh
```

Expected build line: `built test/mr_rules.core (… bytes) rules=3513
fingerprint=6c396cf8be7a1fe5060d4d17bd37cc58` (byte size varies; the unfixed tree's core, the P5
run-1 records' core).

- [ ] **Step 2: The probes**

```bash
A=docs/superpowers/plans/2026-09-14-matcher-translation-fixes.files
cp $A/probes/12-translation-defects.mac $A/probes/12-translation-defects.sh \
   $A/probes/13-translation-shape-scan.py $A/probes/15-collapse-exact.py probes/matcher/
```

- [ ] **Step 3: Probe 12 red**

```bash
sh probes/matcher/12-translation-defects.sh > probes/matcher/12-translation-defects.red.out
tail -1 probes/matcher/12-translation-defects.red.out
```

Expected: `Results: 16 passed, 43 failed`. The 43 FAIL lines: the ten `NE cond` checks (`=> [false]`),
`MUL repl 1_1_4_1 r1` (`=> ERROR`), the fourteen `IGT %mr_i…` checks (the calls stay nouns) and
`IGT cond 2_1 r10 p = -1/2` (`=> [true]`), and seventeen NEGQ checks (`NegQ a/c`, `b^2 e^2`,
`4 a c e^2`, `2 (a+b)`, `b^2-4ac` `=> [true]`; `PosQ a` `=> [false]`; `PosQ %i`, `-%i`, `2-3%i`,
`%i a` `=> []` — `sign` errors on `%i`; `PosQ log(a)`, `(a-b)^3`, `(a-b)^3 c`, `a/c-b/c`,
`sqrt(a-b)(c-d)` `=> [false]`; `NegSumBaseQ a-b`, `SomeNegTermQ a+b` `=> [true]`). The NE section
also prints `R is(k != 1) with k = 1 => true` and `R is(3 != 0) => false`; MUL prints
`R parse (x) (y) => [x,[y]]`.

- [ ] **Step 4: Probe 13 red**

```bash
python3 probes/matcher/13-translation-shape-scan.py > probes/matcher/13-translation-shape-scan.red.out
tail -1 probes/matcher/13-translation-shape-scan.red.out
```

Expected: `Results: 71 passed, 19 failed` — seven `IGT class <N> <head>: source <n> = emitted 0`
(class 1 IGtQ 730, ILtQ 414, ILeQ 1; class 2 IGtQ 18, ILtQ 10; class 3 IGtQ 122, ILtQ 12),
`OPS class 1 !=: 0 sites (10)`, `GAP class 1: 0 juxtapositions (1)` (`1_1_4_1 r1 repl`), and ten
FIRST lines (`PosAux -> %mr_posAux defined` and the nine other internal-order ports).

- [ ] **Step 5: Probe 15 on the P0 core and on the unfixed core**

```bash
git worktree add --detach "${TMPDIR:-/tmp}/mr-p0-tree" 0a6664c
(cd "${TMPDIR:-/tmp}/mr-p0-tree" && sh test/build_rules_core.sh)
MR_RULES_CORE_PATH="${TMPDIR:-/tmp}/mr-p0-tree/test/mr_rules.core" \
  python3 probes/matcher/15-collapse-exact.py > probes/matcher/15-collapse-exact.p0.out
python3 probes/matcher/15-collapse-exact.py > probes/matcher/15-collapse-exact.red.out
tail -8 probes/matcher/15-collapse-exact.p0.out probes/matcher/15-collapse-exact.red.out
git worktree remove --force "${TMPDIR:-/tmp}/mr-p0-tree"
```

Expected build line `… rules=3514 fingerprint=5ef9b3bc5ee07ffac0e76f1fea54fbac` (byte size varies).
Expected rows (walls vary):

| entry | P0 core | unfixed core |
|---|---|---|
| 2.1 e15 | `verified` fires `2_1_r4,9_1_r28` | `deferred` fires `9_1_r27` |
| 1.2.1.2 e1734 / e1735 / e1736 | `expected` fires `1_1_1_2_r37,9_1_r28` | `deferred` fires `9_1_r27` |
| 1.2.1.4 e810 | `verified` top `1_2_1_3_r15` (12 fires from `1_1_1_4_r40`) | `deferred` fires `1_2_1_3_r15` |
| 1.2.1.3 e839 | `verified` fires `1_3_4_r1,1_1_1_3_r8,9_1_r28` | `expected` fires `1_1_1_2_r33,1_1_1_3_r6,1_2_1_3_r4` |

and `Results: 6 passed, 0 failed` (P0), `Results: 1 passed, 5 failed` (unfixed). (P0's 9.1 had a 29th,
dead rule, so its r28 is the generated r27.)

- [ ] **Step 6: Commit**

```bash
git add probes/matcher/12-translation-defects.mac probes/matcher/12-translation-defects.sh \
        probes/matcher/12-translation-defects.red.out probes/matcher/13-translation-shape-scan.py \
        probes/matcher/13-translation-shape-scan.red.out probes/matcher/15-collapse-exact.py \
        probes/matcher/15-collapse-exact.p0.out probes/matcher/15-collapse-exact.red.out
git commit -m "probe: matcher 12, 13, 15 — translation defects, shape scans, collapse entries (red records)"
```

- [ ] **Step 7: The ledger**

Append to `.superpowers/sdd/progress.md`:

```markdown
## Plan: 2026-09-14 matcher translation fixes (branch matcher-substrate)

Spec: docs/superpowers/specs/2026-09-14-matcher-translation-fixes-design.md
Plan: docs/superpowers/plans/2026-09-14-matcher-translation-fixes.md (+ .files/ attachments)

### Task 1 — red records
- build: <build line of probe 12's record>; unfixed core: <Step 1 build line>; P0 core: <Step 5 build line>
- probe 12 red: <Results line>; probe 13 red: <Results line>
- probe 15: P0 <Results line>; unfixed <Results line>; e810 on the unfixed core: <row>
```

```bash
git add .superpowers/sdd/progress.md
git commit -m "docs: ledger — translation fixes Task 1 (red records)"
```

### Task 2: The exact seen entry — `mr_int_exact`; `rubi_hybrid` deleted

**Files:**
- Modify: `maxima_rubi_utils.mac` (the `mr_top` block and the legacy hybrid block)
- Test: `test_maxima_rubi.mac` (`test_translation_fixes_seen`, 5 checks)
- Modify: `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: `mr_top(f, x, fb)`'s body (`maxima_rubi_utils.mac:213-259` at `cff760b`), `%mr_seenp(f)`,
  `%mr_dispatch_tree`, `%mr_defrule`.
- Produces: `%mr_top_body(f, x, fb, exact)` (exact = true: exact `member` only); `mr_top(f, x, fb) :=
  %mr_top_body(f, x, fb, false)`; `mr_int_exact(f, x) := %mr_top_body(f, x, true, true)` — the entry
  Task 3's generator emits for every 9.1 `Int`/`IntHide`. Deleted: `rubi_hybrid`, `rubi_hybrid_exact`,
  `%mr_hybrid_body`.

- [ ] **Step 1: The tests**

```bash
A=docs/superpowers/plans/2026-09-14-matcher-translation-fixes.files
git apply --include=test_maxima_rubi.mac $A/patches/task2-seen-entry.patch
```

The section (in the patch) installs a one-rule table whose repl answers 77 for any integrand, then:

```maxima
  %mr_seen : [x^2 + 2*x + 1],
  check("mr_int: a ratsimp-equal seen form takes the fall-through",
        mr_int((x + 1)^2, x), integrate((x + 1)^2, x)),
  check("mr_int_exact: the same form dispatches", mr_int_exact((x + 1)^2, x), 77),
  %mr_seen : [(x + 1)^2],
  check("mr_int_exact: an exact repeat takes the fall-through",
        mr_int_exact((x + 1)^2, x), integrate((x + 1)^2, x)),
  …
  check_not("rubi_hybrid deleted", member('rubi_hybrid, map(op, functions))),
  check_not("rubi_hybrid_exact deleted", member('rubi_hybrid_exact, map(op, functions))),
```

- [ ] **Step 2: Run Layer A — red**

```bash
maxima --very-quiet -b test_maxima_rubi.mac < /dev/null | grep -a -E '^  FAIL|^Results'
```

Expected: four FAIL lines — `mr_int_exact: the same form dispatches`, `mr_int_exact: an exact repeat
takes the fall-through` (the entry is undefined: the call stays a noun), `rubi_hybrid deleted`,
`rubi_hybrid_exact deleted` — then `Results:  899  passed,  4  failed`.

- [ ] **Step 3: The code**

```bash
git apply --exclude=test_maxima_rubi.mac $A/patches/task2-seen-entry.patch
```

What the patch does in `maxima_rubi_utils.mac`: `mr_top(f, x, fb) := block([ans], …` becomes
`%mr_top_body(f, x, fb, exact) := block([ans], …` with one changed line,

```maxima
  if (if exact then member(f, %mr_seen) else %mr_seenp(f)) then (
```

followed by `mr_top(f, x, fb) := %mr_top_body(f, x, fb, false)$`; the legacy block from
`/* The legacy 9.1 re-dispatch entry.` to `rubi_hybrid_exact(f, x) := %mr_hybrid_body(f, x, "exact")$`
is replaced by its rationale (origin 1.2.1.3 e839; the P5 acceptance entries; cycle bound = the depth
cap) and

```maxima
mr_int_exact(f, x) := %mr_top_body(f, x, true, true)$
```

- [ ] **Step 4: Run Layer A and the dispatch suite — green**

```bash
maxima --very-quiet -b test_maxima_rubi.mac < /dev/null | grep -a -E '^  FAIL|^Results'
maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null | grep -a '^Results'
grep -n 'rubi_hybrid' maxima_rubi_utils.mac rules/class*/*.mac test/matcher/*.mac | grep -v ':/\*\| \* '
```

Expected: `Results:  903  passed,  0  failed`; `Results:  58  passed,  0  failed`; the grep prints
nothing (the two remaining mentions are ` * ` comment lines of the `mr_int_exact` rationale). (`test/check_generated_rules.py`'s
`ENTRY_CALL` still names the deleted entries until Task 3; `probes/matcher/04-tree-counts.py` is a
committed historical probe and keeps its text.)

- [ ] **Step 5: Probe 12 (unchanged)**

`sh probes/matcher/12-translation-defects.sh | tail -1` → `Results: 16 passed, 43 failed` (no probe-12
defect is fixed by this task).

- [ ] **Step 6: Commit**

```bash
git add maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "fix: mr_int_exact — the exact seen entry for the 9.1 rules; rubi_hybrid deleted"
```

- [ ] **Step 7: The ledger**

```markdown
### Task 2 — the exact seen entry
- red: <Step 2's FAIL lines and Results line>
- green: <Step 4's Results lines>; probe 12: <Results line>
```

(commit with `git commit -m "docs: ledger — translation fixes Task 2"`)

### Task 3: The generator's translation fixes; `%mr_i*Q`; the static gate's exceptions; regeneration

**Files:**
- Modify: `generator/generate_rules.py` (`_gap_join`, `_relation_items` + `_expand_chains`, `CMP_OPS` /
  `INT_CMP`, `emit_head`)
- Modify: `maxima_rubi_utils.mac` (`%mr_iGtQ` / `%mr_iLtQ` / `%mr_iGeQ` / `%mr_iLeQ` after `%mr_ILtQ`)
- Modify: `test/check_generated_rules.py` (`ENTRY_CALL`, the undo functions, three checks)
- Regenerate: `rules/class{1,2,3}/*.mac`
- Test: `test_maxima_rubi.mac` (`test_translation_fixes_generator`, 17 checks)
- Modify: `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: `mr_int_exact` (Task 2); `%mr_load_sibling`; the P0 base `0a6664c` of the static gate.
- Produces: generated calls `%mr_iGtQ(A, B)` etc. (true/false); `notequal(L, R)` for Rubi `!=`;
  `)*(` for juxtaposition; `mr_int_exact(…)` in `rules/class1/9_1.mac`. Static gate constants
  `INT_CMP_SITES = 1283`, `NOTEQUAL_SITES = 10`, `JUXTA_SITES = 1`.

- [ ] **Step 1: The tests**

```bash
A=docs/superpowers/plans/2026-09-14-matcher-translation-fixes.files
git apply --include=test_maxima_rubi.mac $A/patches/task3-translation.patch
```

The section checks the four entries on integer / fraction / float / symbol arguments (`iGtQ 3 0` true,
`iGtQ 1/2 0` false, `iGtQ 2.0 0` false, `iGtQ n 0` false, …), `notequal` (2 1 true, 1 1 false, a 1
unknown), loads `rules/class1/1_1_3_2.mac` and `1_1_4_1.mac` through `%mr_load_sibling`, and runs
`_mr_cond_1_1_3_2_r17` on n = 2 (gcd 2, true) and n = 3 (gcd 1, false) and
`errcatch(ratsimp(_mr_repl_1_1_4_1_r1(…a=1, b=2, j=1, n=3, p=2…) - (x + 2*x^3)^3/(12*x^2)))` = `[0]`.

- [ ] **Step 2: Run Layer A — red**

```bash
maxima --very-quiet -b test_maxima_rubi.mac < /dev/null | grep -a -E '^  FAIL|^Results'
```

Expected: fourteen FAIL lines — the eleven `iGtQ` / `iLtQ` / `iLeQ` / `iGeQ` checks (the entries are
undefined), `1_1_3_2 r17 cond: gcd(m+1, n) = 2, k != 1 holds` and `… = 1, k != 1 fails` (the rule
still reads `is(k != 1)`, i.e. `k! = 1`), `1_1_4_1 r1 repl on numbers` (`errcatch` → `[]`) — then
`Results:  906  passed,  14  failed`. The three `notequal` checks pass (Maxima's own function).

- [ ] **Step 3: The code**

```bash
git apply --exclude=test_maxima_rubi.mac $A/patches/task3-translation.patch
```

What the patch does:

- `generator/generate_rules.py` — `CMP_OPS` keeps `GtQ`/`LtQ`/`LeQ`/`GeQ`; the integer heads map to the
  named entries and `emit_head` checks them before `CMP_OPS`:

```python
INT_CMP = {"IGtQ": "%mr_iGtQ", "ILtQ": "%mr_iLtQ", "ILeQ": "%mr_iLeQ",
           "IGeQ": "%mr_iGeQ"}
…
    if head in INT_CMP:
        if len(arglist) != 2:
            raise GenError(f"{key} r{n}: {head} arity {len(arglist)}")
        return f"{INT_CMP[head]}({arglist[0]}, {arglist[1]})"
```

  `_expand_chains`'s partition moves into `_relation_items(s)` (which also knows the two-character
  `!=`); before the chain pass, every `!=` relation becomes `notequal(L, R)` right to left, keeping the
  spacing outside the relation; a `!=` next to another relational operator is a `GenError`.
  `_gap_join` adds `R == "("` to the `)`/`]` branch (juxtaposition → `*`) and its docstring cites
  probe 12 MUL. The `Int`/`IntHide` emitter:

```python
        entry = "mr_int_exact" if key == "9_1" else "mr_int"
        return f"{entry}({arglist[0]}, {arglist[1]})"
```

- `maxima_rubi_utils.mac`, after `%mr_ILtQ(u, n) := %mr_integerQ(u) and is(u < n)$`:

```maxima
%mr_iGtQ(u, n) := if integerp(u) and is(u > n) = true then true else false$
%mr_iLtQ(u, n) := if integerp(u) and is(u < n) = true then true else false$
%mr_iGeQ(u, n) := if integerp(u) and is(u >= n) = true then true else false$
%mr_iLeQ(u, n) := if integerp(u) and is(u <= n) = true then true else false$
```

- `test/check_generated_rules.py` — `ENTRY_CALL` gains `mr_int_exact` and loses the hybrid entries;
  `undo_fixes` maps `%mr_i*Q(A, B)` → `is(A op B)` and `notequal(A, B)` → `A != B` on the new body
  line, `redo_juxtaposition` maps `) (` → `)*(` on the base body line, both before the MatchQ masking;
  three checks pin the counts.

- [ ] **Step 4: The static gate before regeneration — red**

```bash
python3 test/check_generated_rules.py | grep -E '^FAIL|^Results'
```

Expected: `FAIL: no defmatch/matchdeclare; one %mr_defrule per rule; every cond/repl explained` (the
base `) (` is redone, the unregenerated file still has it), `FAIL: integer comparisons %mr_i*Q(A, B)
undone to is(A op B): 1283 sites` (0 found), `FAIL: notequal(A, B) undone to A != B: 10 sites` (0
found), `Results: 11 passed, 3 failed`.

- [ ] **Step 5: Regenerate classes 1–3**

```bash
for c in 1 2 3; do python3 generator/generate_rules.py --class $c > /dev/null || echo "class $c FAILED"; done
git status --porcelain rules/ | wc -l
git diff --shortstat rules/
find rules -name '*.mac' -type f | sort | xargs md5sum > "${TMPDIR:-/tmp}/rules.1"
for c in 1 2 3; do python3 generator/generate_rules.py --class $c > /dev/null; done
find rules -name '*.mac' -type f | sort | xargs md5sum > "${TMPDIR:-/tmp}/rules.2"
cmp "${TMPDIR:-/tmp}/rules.1" "${TMPDIR:-/tmp}/rules.2" && echo "regeneration byte-identical"
```

Expected: `79`; ` 79 files changed, 1030 insertions(+), 1030 deletions(-)`; `regeneration
byte-identical`.

- [ ] **Step 6: The gates — green**

```bash
python3 test/check_generated_rules.py | grep -E '^FAIL|^INFO: bodies|^Results'
python3 probes/matcher/13-translation-shape-scan.py | grep -E '^FAIL|^Results'
maxima --very-quiet -b test_maxima_rubi.mac < /dev/null | grep -a -E '^  FAIL|^Results'
sh probes/matcher/12-translation-defects.sh | grep -E '^FAIL|^Results'
```

Expected: static gate `Results: 14 passed, 0 failed`; probe 13 `Results: 80 passed, 10 failed` (only
the ten FIRST lines — Task 4); Layer A `Results:  920  passed,  0  failed`; probe 12
`Results: 42 passed, 17 failed` (only the seventeen NEGQ lines of Task 1 Step 3 — Task 4).

- [ ] **Step 7: Commit**

```bash
git add generator/generate_rules.py maxima_rubi_utils.mac test/check_generated_rules.py \
        test_maxima_rubi.mac rules/class1 rules/class2 rules/class3
git commit -m "fix: generator — integer comparisons, notequal, juxtaposition, the 9.1 exact entry; static gate exceptions; classes 1-3 regenerated"
```

- [ ] **Step 8: The ledger**

```markdown
### Task 3 — generator translation fixes
- red: <Step 2 FAIL/Results lines>; static gate before regeneration: <Step 4 lines>
- regeneration: <Step 5's three lines>
- green: static gate <Results>; probe 13 <Results>; Layer A <Results>; probe 12 <Results>
```

(commit with `git commit -m "docs: ledger — translation fixes Task 3"`)

### Task 4: The PosAux port and the First/Rest siblings; probe 14; the order ticket

**Files:**
- Modify: `maxima_rubi_utils.mac` (the sign/posQ/negQ block, `%mr_intPart_aux`, `%mr_fracPart_aux`,
  `%mr_removeContentAux`, `%mr_product_factors`, `%mr_rt_negSumBaseQ`, `%mr_splitSum_aux`,
  `%mr_contentFactor`, `%mr_signOfFactor`, `%mr_unifySum`, the OrderedQ and TestAux comments)
- Test: `test_maxima_rubi.mac` (`test_translation_fixes_posaux`, 35 checks; `posQ a` flipped)
- Create: `probes/matcher/14-mma-order-agreement.py`, `.out`;
  `.scratch/matcher-translation-fixes/issues/01-case-fold-order-shim.md`
- Modify: `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: `%mr_togetherSimplify`, `%mr_complexNumberQ`, `%mr_simp`, `%mr_eqQ`, `%mr_neQ`,
  `%mr_rationalQ`.
- Produces: `%mr_posAux(u)` (true/false), `%mr_posQ(u) := %mr_posAux(%mr_togetherSimplify(u))` under
  `errcatch`, `%mr_negQ` unchanged in form; `%mr_rest_in(u)`, `%mr_args_in(u)` (internal order,
  `inflag` bound only around the extraction); `%mr_product_factors(u)` = the internal factor list
  (`a/b` → `[a, 1/b]`, `-a*b` → `[-1, a, b]`, anything else `[u]`).

- [ ] **Step 1: The tests**

```bash
A=docs/superpowers/plans/2026-09-14-matcher-translation-fixes.files
git apply --include=test_maxima_rubi.mac $A/patches/task4-posaux.patch
```

The section's expectations are Rubi's PosAux worked by hand (design §3.6): `negQ a/c`, `e^2 b^2`,
`4 a c e^2`, `2 (a+b)`, `b^2-4ac`, `0` false; `negQ -a`, `-4 e^2` true; `posQ -2/3` false, `0.5` true,
`%pi-4` false, `%pi-3` true, `%i` / `2-3%i` / `%i a` true and `-%i` false (under `errcatch`),
`exp(a)` / `log(a)` / `1/c` true, `-a^2` false; the factored inputs `negQ (b-a)(c+d)`, `-(a-b)^2`,
`(x-1)(x+2)` true and `posQ (a-b)^3`, `(a-b)^3 c`, `a/c-b/c`, `sqrt(a-b)(c-d)` true; the siblings
`negSumBaseQ a-b` false / `b-a` true, `someNegTermQ a+b` false, `splitSum` with a function that
answers every term → `[[-a], b]` on `b - a`, `product_factors a/b` → `[a, 1/b]`, `-a*b` →
`[-1, a, b]`, `removeContentAux x-1` → `1 - x`, `a-b` → `a - b`. The existing `posQ a` check becomes
`check_bool("posQ a (PosAux: a symbol is positive)", %mr_posQ(a))`.

- [ ] **Step 2: Run Layer A — red**

```bash
maxima --very-quiet -b test_maxima_rubi.mac < /dev/null | grep -a -E '^  FAIL|^Results'
```

Expected: twenty-one FAIL lines — `posQ a (PosAux: a symbol is positive)`; `negQ a/c`, `e^2 b^2`,
`4 a c e^2`, `2 (a+b)`, `b^2-4ac`; `posQ %i`, `-%i`, `2-3%i`, `%i a` (the strict `sign` reading errors
on `%i`); `posQ log(a)`, `1/c`, `(a-b)^3`, `(a-b)^3 c`, `a/c-b/c`, `sqrt(a-b)(c-d)`;
`negSumBaseQ a-b (First = a)`, `someNegTermQ a+b`, `splitSum takes the first term (internal order)`,
`product_factors a/b`, `removeContentAux -1+x (NegQ[First] -> -u)` — then
`Results:  934  passed,  21  failed`.

- [ ] **Step 3: The code**

```bash
git apply --exclude=test_maxima_rubi.mac $A/patches/task4-posaux.patch
```

The port (the patch's central hunk; the comment block above it lists the branches and the two stated
deviations):

```maxima
%mr_rest_in(u) := block([inflag : true], rest(u))$
%mr_args_in(u) := block([inflag : true], args(u))$
%mr_posAux(u) := block([v, w],
  if numberp(u) then is(u > 0)
  else if %mr_complexNumberQ(u) then (
    if is(realpart(u) = 0) then %mr_posAux(imagpart(u))
    else %mr_posAux(realpart(u)))
  else if constantp(u) then (
    v : %mr_simp(realpart(u)),
    if numberp(v) then (
      if %mr_eqQ(v, 0) then %mr_posAux(%mr_simp(imagpart(u)))
      else is(v > 0))
    else (
      w : float(u),
      if numberp(w) or %mr_complexNumberQ(w) then %mr_posAux(w) else false))
  else (
    v : if freeof(%i, u) then errcatch(is(u > 0)) else [],
    if v = [true] then true
    else if v = [false] then false
    else if atom(u) then true
    else if inpart(u, 0) = "^" then (
      if integerp(inpart(u, 2))
      then (evenp(inpart(u, 2)) or %mr_posAux(inpart(u, 1)))
      else true)
    else if inpart(u, 0) = "*" then (
      if %mr_posAux(inpart(u, 1)) then %mr_posAux(%mr_rest_in(u))
      else not %mr_posAux(%mr_rest_in(u)))
    else if inpart(u, 0) = "+" then %mr_posAux(inpart(u, 1))
    else true))$
%mr_posQ(u) := block([t],
  t : errcatch(%mr_togetherSimplify(u)),
  %mr_posAux(if t = [] then u else first(t)))$
```

The siblings read the internal order: `%mr_rt_negSumBaseQ` `%mr_negQ(inpart(u, 1))`;
`%mr_splitSum_aux` `inpart(u, 1)` / `%mr_rest_in(u)`; `%mr_removeContentAux` `-u` when
`%mr_negQ(inpart(u, 1))` on a sum; `%mr_product_factors(u) := if not atom(u) and inpart(u, 0) = "*"
then %mr_args_in(u) else [u]`; `%mr_signOfFactor` and `%mr_contentFactor` `inpart(…, 1)` for the
first term; `%mr_unifySum` `%mr_args_in(u)`. `%mr_intPart_aux` / `%mr_fracPart_aux` test
`%mr_rationalQ(u)` first. The strict-sign comments and the OrderedQ comment are corrected.

- [ ] **Step 4: Run Layer A and probe 12 — green**

```bash
maxima --very-quiet -b test_maxima_rubi.mac < /dev/null | grep -a -E '^  FAIL|^Results'
sh probes/matcher/12-translation-defects.sh | grep -E '^FAIL|^Results'
```

Expected: `Results:  955  passed,  0  failed`; `Results: 59 passed, 0 failed`.

- [ ] **Step 5: The scans and suites**

```bash
python3 probes/matcher/13-translation-shape-scan.py | tail -1
maxima --very-quiet -b test/matcher/test_mr_match.mac < /dev/null | grep -a '^Results'
maxima --very-quiet -b test/matcher/test_mr_tree.mac < /dev/null | grep -a '^Results'
maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null | grep -a '^Results'
python3 test/check_generated_rules.py | tail -1
```

Expected: `Results: 90 passed, 0 failed`; `Results: 53 passed, 0 failed`; `Results: 51 passed, 0
failed`; `Results:  58  passed,  0  failed`; `Results: 14 passed, 0 failed`.

- [ ] **Step 6: Probe 14** (busy check first; ~1 min wall on 8 workers)

```bash
cp $A/probes/14-mma-order-agreement.py probes/matcher/
python3 probes/matcher/14-mma-order-agreement.py > probes/matcher/14-mma-order-agreement.out
grep -E '^CLASS [0-9] (answers|Plus|first-term|PosAux flips)' probes/matcher/14-mma-order-agreement.out
```

Expected (pre-validation): class 1 `answers 25697 done 25697 parse-errors 0 answer-errors 22`,
`Plus comparable 279107: agree 248655, first-only 9635, first-dis 20817 (PosAux flip 10104)`,
`first-term agreement 0.9254, whole-order agreement 0.8909, PosAux flip rate 0.0362`,
`PosAux flips removed by the case-fold rename 3265, remaining 6839`; class 2 `answer-errors 0`,
`0.9495, … 0.9376, … 0.0255`, `… 1, remaining 137`; class 3 `answer-errors 11`,
`0.9584, … 0.9493, … 0.0232`, `… 0, remaining 970`.

- [ ] **Step 7: The ticket**

```bash
mkdir -p .scratch/matcher-translation-fixes/issues
cp $A/tickets/01-case-fold-order-shim.md .scratch/matcher-translation-fixes/issues/
```

If Step 6's figures differ from the ticket's table, replace the table's figures with Step 6's and
drop the "(Pre-validation figures …)" sentence's pre-validation wording.

- [ ] **Step 8: Commit**

```bash
git add maxima_rubi_utils.mac test_maxima_rubi.mac probes/matcher/14-mma-order-agreement.py \
        probes/matcher/14-mma-order-agreement.out .scratch/matcher-translation-fixes/issues/01-case-fold-order-shim.md
git commit -m "fix: PosQ/NegQ — port Rubi's PosAux; First/Rest siblings read the internal order; probe 14; order-shim ticket"
```

- [ ] **Step 9: The ledger**

```markdown
### Task 4 — the PosAux port and siblings
- red: <Step 2 lines>; green: <Step 4 and Step 5 Results lines>
- probe 14: <Step 6's twelve lines>
- ticket: .scratch/matcher-translation-fixes/issues/01-case-fold-order-shim.md
```

(commit with `git commit -m "docs: ledger — translation fixes Task 4"`)

### Task 5: The fixed tree's evidence; Plan 3's P6 script; the docs

**Files:**
- Modify: `docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.files/p6/p6_hardwire.py`
- Regenerate: `probes/matcher/08-runtime-load.out`
- Create: `probes/matcher/12-translation-defects.out`, `13-translation-shape-scan.out`,
  `15-collapse-exact.out`
- Modify: `AGENTS.md`, `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`, `todo/TODO.md`,
  `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: the Task 2–4 tree.
- Produces: the fixed core's fingerprint (Tasks 6–7 check it before every launch); the green records.

- [ ] **Step 1: The P6 script**

```bash
A=docs/superpowers/plans/2026-09-14-matcher-translation-fixes.files
git apply $A/patches/task5-p6-hardwire.patch
python3 docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.files/p6/p6_hardwire.py --check
```

Expected: `anchors ok: 8 combinations`.

- [ ] **Step 2: Probe 08** (flagless load, Layer A both arms, dispatch suite, core build)

```bash
sh probes/matcher/08-runtime-load.sh > probes/matcher/08-runtime-load.out 2>&1
grep -a -E '^(LOAD|LAYER-A|DISPATCH|CORE-BUILD|R load)' probes/matcher/08-runtime-load.out
```

Expected: `LOAD flagless wall 1.5 s; TLS lines 0` (walls vary), `R load maxima_rubi.mac s … mr_load_all s …
rules 3513`, both `LAYER-A … TLS lines 0: Results:  955  passed,  0  failed`,
`DISPATCH-SUITE flagless … Results:  58  passed,  0  failed`, `CORE-BUILD … exit 0: built
test/mr_rules.core (… bytes) rules=3513 fingerprint=<the fixed core>`.

- [ ] **Step 3: The green records**

```bash
sh probes/matcher/12-translation-defects.sh > probes/matcher/12-translation-defects.out
python3 probes/matcher/13-translation-shape-scan.py > probes/matcher/13-translation-shape-scan.out
python3 probes/matcher/15-collapse-exact.py > probes/matcher/15-collapse-exact.out
tail -1 probes/matcher/12-translation-defects.out probes/matcher/13-translation-shape-scan.out
tail -8 probes/matcher/15-collapse-exact.out
```

Expected: `Results: 59 passed, 0 failed`; `Results: 90 passed, 0 failed`; probe 15 on the fixed core:
2.1 e15 `verified` fires `2_1_r3,2_1_r2,9_1_r27`; 1.2.1.2 e1734/e1735/e1736 `expected` fires
`1_1_1_2_r37,9_1_r27`; 1.2.1.4 e810 `deferred` fires `1_2_1_3_r15` (user decision 5); 1.2.1.3 e839
`expected` fires `1_1_1_2_r33,1_1_1_3_r6,1_2_1_3_r4`; `Results: 5 passed, 1 failed`.

- [ ] **Step 4: AGENTS.md**

In § Tests, Layer A: replace `898 targets (green: \`Results: 898 passed, 0 failed\`; the` with
`955 targets (green: \`Results: 955 passed, 0 failed\`; the`, and replace the closing
`plan-2 final review (1.4.2 r17 MatchQ exponent part folding)).` with
`plan-2 final review (1.4.2 r17 MatchQ exponent part folding), → 955 matcher translation fixes
(docs/superpowers/plans/2026-09-14-matcher-translation-fixes.md: the exact seen entry 5, integer
comparisons / notequal / juxtaposition 17, the PosAux port and the First/Rest siblings 35 checks)).`

In § Generator — P3 static gate: replace `Green: \`Results: 11 passed, 0 failed\`. It compares` with
`Green: \`Results: 14 passed, 0 failed\` (11 + the three translation-fix exception counts, 2026-09-14).
It compares`, and `except the
spec's closed exception list (each exception checked as the exact text
transformation it claims to be)` with `except the
spec's closed exception list (each exception checked as the exact text
transformation it claims to be; the list includes the matcher translation
fixes' 1,283 integer comparisons, 10 \`notequal\` and 1 juxtaposition)`.

- [ ] **Step 5: The parent spec amendments** (`docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`)

§3.4: after `the 52 rules that had a workaround emitter.` append
` Amended 2026-09-14 (docs/superpowers/specs/2026-09-14-matcher-translation-fixes-design.md §3.4):
the 1,283 integer comparisons \`%mr_i*Q(A, B)\` (undone to \`is(A op B)\`), the 10
\`notequal(A, B)\` (undone to \`A != B\`) and the juxtaposition \`)*(\` (1 site).`; and after
`Its repl \`Int\` calls
translate to \`mr_int\` as everywhere else.` append ` (Amended 2026-09-14: to \`mr_int_exact\`, the exact
seen entry — translation fixes design §3.3.)`

§3.5, the `rubi_hybrid` paragraph: append ` **Amended 2026-09-14:** the P5 acceptance stop found the
collapse family regressed (2.1 e15, 1.2.1.2 e1734–e1736); \`mr_int_exact\` restores the exact
comparison as a translation fix and \`rubi_hybrid\` / \`rubi_hybrid_exact\` / \`%mr_hybrid_body\` are
deleted (translation fixes design §3.3).`

- [ ] **Step 6: TODO**

In `todo/TODO.md` § Matcher substrate, replace `Plan 3 Tasks 5–6 wait. Next: write that fix plan — open`
with `Plan 3 Tasks 5–6 wait — done (the fix plan
\`docs/superpowers/plans/2026-09-14-matcher-translation-fixes.md\`)` and add the item
`- Translation fixes plan (2026-09-14): Tasks 1–5 fixed the four defects and their siblings (probes
12/13/15 red→green, probe 14, Layer A 955, static gate 14); Tasks 6–7 re-run P5 as p5b and return to
the acceptance stop; the case-fold order shim is ticketed
(\`.scratch/matcher-translation-fixes/issues/01-case-fold-order-shim.md\`) — open`.

- [ ] **Step 7: Commit**

```bash
git add docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.files/p6/p6_hardwire.py \
        probes/matcher/08-runtime-load.out probes/matcher/12-translation-defects.out \
        probes/matcher/13-translation-shape-scan.out probes/matcher/15-collapse-exact.out \
        AGENTS.md docs/superpowers/specs/2026-09-12-matcher-substrate-design.md todo/TODO.md
git commit -m "record: translation fixes — green probes 12/13/15, probe 08 on the fixed tree; P6 script, AGENTS.md, spec amendments"
```

- [ ] **Step 8: The ledger**

```markdown
### Task 5 — fixed-tree evidence
- p6 check: <line>; probe 08: <Step 2's lines>; fixed core: <CORE-BUILD fingerprint>
- green: probe 12 <Results>; probe 13 <Results>; probe 15 <Results> and its six rows
```

(commit with `git commit -m "docs: ledger — translation fixes Task 5"`)

### Task 6: P5b — runs 1–4, the noise-filtered winners, run 5 when needed

Measurement only; no source changes. ~10–15 h machine time.

**Files:**
- Create: `test/corpus_class{2,3,1}.p5b-run{1,2,3,4}.out` (and `p5b-run5` when `FINAL_ARM` is not
  empty); `probes/matcher/11-arm-noise-recheck.p5b.{mr_flat_wide,mr_cond_retry,mr_model_flags}.out`
- Modify: `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: the Task 5 core (fingerprint in the Task 5 ledger); Plan 3's run procedure (Plan 3 Task 2
  preamble and Steps 2–4), `test/p5_gate.py`, `test/ab_records.py`, probe 11; the P0 records
  `test/corpus_class{1,2,3}.pre-matcher.out`; the defective tree's P5 run-1 records
  `test/corpus_class{1,2,3}.p5-run1.out` (informational A/B only).
- Produces: `FINAL_ARM` and the final records `$F1 $F2 $F3` (`test/corpus_class<N>.p5b-run1.out` or
  `p5b-run5`) in the ledger.

The run procedure is Plan 3's (`docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.md` Task 2,
the block after "The run procedure") with the record and merge-log names changed to `p5b`:

```bash
# RUN=<k>  ARM="<MR_SWITCHES value, empty for the defaults>"
# C=<1|2|3>  SECTION="<1 Algebraic functions|2 Exponentials|3 Logarithms>"
# DRIVER=<test/corpus_class1_driver.py for class 1, test/corpus_driver.py otherwise>
ps -eo args | grep -E '(^|/)python3 .*(corpus_driver|corpus_class1_driver|10-p5-attribution|11-arm-noise|14-mma-order)' | grep -v grep   # nothing
head -1 test/mr_rules.core.stamp      # the Task 5 fingerprint
MR_SWITCHES="$ARM" python3 test/launch_class_shards.py "$SECTION" test/corpus_class$C.pre-matcher.out $DRIVER --launch < /dev/null
setsid sh test/wait_and_merge.sh test/corpus_class$C.shard-pids test/merge_class_shards.py \
    test/class${C}_merge.p5b-run$RUN.log "$SECTION" test/corpus_class$C.p5b-run$RUN.out $DRIVER \
    "corpus_class$C.shard*.out" < /dev/null > /dev/null 2>&1 &
```

Waiter (`run_in_background`): `until grep -q 'merge rc=' test/class${C}_merge.p5b-run$RUN.log 2>/dev/null; do sleep 60; done; cat test/class${C}_merge.p5b-run$RUN.log`.
A class's run is read only as Plan 3 Task 2 says (the `OK: <N>/<N> entries … no dupes/missing/extra`
line with N = 965 / 3,085 / 25,697, `switches: <the intended arm>`, `merge rc=0`, the launcher's
`switches:` and `removed <n> shard files` lines); a stale pids file and an `INCOMPLETE` merge are
handled as it says.

- [ ] **Step 1: Run 1 (defaults), classes 2 → 3 → 1**

For each class: the procedure with `RUN=1 ARM=""`, then

```bash
python3 test/p5_gate.py gate test/corpus_class$C.pre-matcher.out test/corpus_class$C.p5b-run1.out
python3 test/ab_records.py test/corpus_class$C.p5-run1.out test/corpus_class$C.p5b-run1.out | sed -n '/PASS\/FAIL table/,/per file/p'
```

`FAIL: wall ceiling …` → **stop and report to the user**; `FAIL: complete` / `FAIL: switches` → harness
failure, stop and report; `FAIL: pass floor` → record and continue (Task 7 judges the final records).
The `ab_records.py` table (defective run 1 → fixed run 1) is informational: what the fixes moved.

- [ ] **Step 2: Commit run 1**

```bash
git add test/corpus_class2.p5b-run1.out test/corpus_class3.p5b-run1.out test/corpus_class1.p5b-run1.out
git commit -m "record: P5b run 1 (switch defaults, fixed tree) — classes 1-3"
```

- [ ] **Step 3: Runs 2–4** — the procedure for `RUN=2 ARM="mr_flat_wide=true"`, `RUN=3
  ARM="mr_cond_retry=false"`, `RUN=4 ARM="mr_model_flags=false"`, each classes 2, 3, 1, each class
  followed by `p5_gate.py gate` (recorded; a flipped arm's wall-ceiling FAIL is not a stop). Then

```bash
git add test/corpus_class[123].p5b-run[234].out
git commit -m "record: P5b runs 2-4 (mr_flat_wide, mr_cond_retry, mr_model_flags flipped) — classes 1-3"
```

- [ ] **Step 4: The raw winners**

```bash
R() { echo test/corpus_class1.p5b-run$1.out test/corpus_class2.p5b-run$1.out test/corpus_class3.p5b-run$1.out; }
python3 test/p5_gate.py winner mr_flat_wide   $(R 1) $(R 2)
python3 test/p5_gate.py winner mr_cond_retry  $(R 1) $(R 3)
python3 test/p5_gate.py winner mr_model_flags $(R 1) $(R 4)
```

- [ ] **Step 5: Probe 11 on all three switches** (design §4 step 4; one at a time, each detached,
  busy check first; 1–3 h each — `mr_cond_retry` re-runs ~2,000 entries)

```bash
S=mr_flat_wide; K=2      # then S=mr_cond_retry K=3, then S=mr_model_flags K=4
setsid python3 probes/matcher/11-arm-noise-recheck.py $S probes/matcher/11-arm-noise-recheck.p5b.$S.out \
    --base $(R 1) --flip $(R $K) --reps 3 --cap 30 --workers 24 < /dev/null \
    > "${TMPDIR:-/tmp}/p5b-probe11-$S.log" 2>&1 &
```

Waiter: `until ! pgrep -f "11-arm-noise-recheck.py $S" > /dev/null; do sleep 60; done; tail -5 probes/matcher/11-arm-noise-recheck.p5b.$S.out`.
Each output ends with its `WINNER (noise-filtered) <switch>=<value> (<reason>)` line and a `Results:`
line (`0 failed`; a failed rep is a harness failure — stop and report).

- [ ] **Step 6: The final arm; run 5 when needed**

`FINAL_ARM` = the space-separated noise-filtered winners that differ from the defaults (the user's
2026-09-13 noise rule: the winner rule applied to what reproduces). When `FINAL_ARM` is not empty, run
the procedure with `RUN=5 ARM="$FINAL_ARM"`, classes 2, 3, 1, each followed by `p5_gate.py gate` (a
wall-ceiling FAIL is now a **stop and report**), and commit:

```bash
git add test/corpus_class[123].p5b-run5.out probes/matcher/11-arm-noise-recheck.p5b.*.out
git commit -m "record: P5b probe 11 (three switches) and run 5 (the winning arm: $FINAL_ARM) — classes 1-3"
```

When `FINAL_ARM` is empty: commit only `probes/matcher/11-arm-noise-recheck.p5b.*.out`
(`git commit -m "probe: matcher 11 — P5b arm noise re-checks, three switches"`); the final records are
`p5b-run1`.

- [ ] **Step 7: The arms' A/B tables** (Plan 3 Task 3 Step 7 with `p5b-run` names)

```bash
for k in 2 3 4; do for c in 2 3 1; do
  echo "== run 1 -> run $k, class $c"
  python3 test/ab_records.py test/corpus_class$c.p5b-run1.out test/corpus_class$c.p5b-run$k.out | sed -n '/PASS\/FAIL table/,/per file/p'
done; done
```

- [ ] **Step 8: The ledger**

```markdown
### Task 6 — P5b runs
- core: <fingerprint>
- run 1: per class <merge OK + switches; merge rc; gate PASS:/FAIL:/INFO: lines and Results>; defective run 1 -> fixed run 1: <PASS/FAIL table>
- runs 2-4: <per run, per class as above>
- raw winners: <three WINNER lines>
- probe 11: <per switch, the per-class repro/noise line and the WINNER (noise-filtered) line>
- FINAL_ARM: "<value>"; final records: <F1 F2 F3>; run 5: <per class, or "not taken">
- arm A/B (run 1 -> run k): <twelve lines: k, class, PASS->PASS, PASS->FAIL, FAIL->PASS, FAIL->FAIL>
```

(commit with `git commit -m "docs: ledger — translation fixes Task 6 (P5b runs, winners)"`)

### Task 7: P5b gate — final records, re-checks, attribution, defect clearance, final tree; the user's acceptance

No source changes except the probe 10 extension. Ends at a **stop**.

**Files:**
- Modify: `probes/matcher/10-p5-attribution.py`, `probes/matcher/10-p5-attribution.summary.py`
- Create: `test/corpus_class<N>.p5b-final.timeout-rerun/` (launcher files, `merge.out`, the
  `*.timeout100s.out` record); `probes/matcher/10-p5b-attribution.class<N>-{final30,p0,final120,newerror}.out`,
  `…class<N>.summary.out`, `…mechanisms-*.md`, `probes/matcher/10-p5b-attribution.acceptance.md`
- Regenerate: `test/matcher/{roundtrip,controls,spike01,gate}.out`, `test/matcher/{roundtrip,gate}.flags.out`
- Modify: `todo/TODO.md`, `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: `FINAL_ARM`, `$F1 $F2 $F3` (Task 6 ledger); the P0 records; Plan 3 Task 4's procedures;
  probe 13's sibling list (`probes/matcher/13-translation-shape-scan.out`).
- Produces: the acceptance document; the user's per-group decisions in the ledger.

Throughout: `export FINAL_ARM="<ledger value>"`, `F1 F2 F3` set, and `head -1 test/mr_rules.core.stamp`
equal to the Task 5 fingerprint before each launch.

- [ ] **Step 1: The final-record gates**

```bash
python3 test/p5_gate.py gate test/corpus_class2.pre-matcher.out $F2
python3 test/p5_gate.py gate test/corpus_class3.pre-matcher.out $F3
python3 test/p5_gate.py gate test/corpus_class1.pre-matcher.out $F1
```

Each must end `Results: 4 passed, 0 failed` with `switches:` equal to the final arm; a pass-floor or
wall-ceiling FAIL is a **stop and report**.

- [ ] **Step 2: The 100 s timeout re-checks** (classes 2, 3, 1; one at a time; each detached)

```bash
# C=<N>  SECTION="<section>"  F=<the class's final record>
D=test/corpus_class$C.p5b-final.timeout-rerun
MR_SWITCHES="$FINAL_ARM" python3 test/launch_timeout_rerun.py $F 100 $D "$SECTION" --launch < /dev/null
setsid sh test/wait_timeout_rerun.sh $D >> $D/wait.log 2>&1 < /dev/null &
```

Waiter: `until grep -q 'merge rc=' $D/merge.out 2>/dev/null; do sleep 60; done; head -20 $D/merge.out`.
Must hold: `OK: <n>/<n> re-checked, no dupes/missing/extra` (n = the gate's timeout count), `merge
rc=0`, the record's description line ending `switches: <the final arm>`.

- [ ] **Step 3: Probe 10 — the extension, the P0 core, the legs**

```bash
A=docs/superpowers/plans/2026-09-14-matcher-translation-fixes.files
git apply $A/patches/task7-probe10-extension.patch
git worktree add --detach "${TMPDIR:-/tmp}/mr-p0-tree" 0a6664c
(cd "${TMPDIR:-/tmp}/mr-p0-tree" && sh test/build_rules_core.sh)
```

Per class (2, 3, 1), nothing else running, the five commands in one `run_in_background` call:

```bash
P=probes/matcher/10-p5-attribution; O=probes/matcher/10-p5b-attribution; P0R=test/corpus_class$C.pre-matcher.out
P0CORE="${TMPDIR:-/tmp}/mr-p0-tree/test/mr_rules.core"
REC=test/corpus_class$C.p5b-final.timeout-rerun/$(basename $F .out).timeout100s.out
MR_SWITCHES="$FINAL_ARM" python3 $P.py "$SECTION" $P0R $F passfail $O.class$C-final30.out 30 24
MR_SWITCHES="$FINAL_ARM" MR_RULES_CORE_PATH=$P0CORE python3 $P.py "$SECTION" $P0R $F passfail $O.class$C-p0.out 30 24
MR_SWITCHES="$FINAL_ARM" python3 $P.py "$SECTION" $P0R $F passfail-timeout $O.class$C-final120.out 120 24
MR_SWITCHES="$FINAL_ARM" python3 $P.py "$SECTION" $P0R $F newerror $O.class$C-newerror.out 30 24
python3 $P.summary.py $P0R $F --final30 $O.class$C-final30.out --p0 $O.class$C-p0.out \
    --final120 $O.class$C-final120.out --recheck $REC --newerror $O.class$C-newerror.out > $O.class$C.summary.out
tail -1 $O.class$C.summary.out
```

The summary must end `Results: <n> passed, 0 failed` with n = the class's PASS→FAIL count; its
`NEW ERRORS` block carries each new error's message; an `unverified` entry's answer is printed under
it (`answer final:`).

- [ ] **Step 4: The mechanism lines** (Plan 3 Task 4 Step 5, written to
  `probes/matcher/10-p5b-attribution.mechanisms-class<N>[-a|-b|…].md`)

One line per `GROUP`: id, entries, the mechanism from the fire traces (the final core's answering rule
against the P0 route, the answer; for `unverified`, wrong vs unverifiable from `answer final:`; for
`error`, the error kind), the substrate change it follows from, and a clearance tag
`[fixed-defect: none | IGT | NEGQ | NE | MUL | collapse | sibling:<probe 13 port>]`. 1.2.1.4 e810, if
PASS→FAIL, gets its own line (user decision 5). New timeouts: one line per class with the 100 s
transition counts; new errors: one line per entry with its error message.

- [ ] **Step 5: Defect clearance** (design §4 step 6)

A group whose tag is not `none` — a fixed defect or a probe-13 sibling still explains it — is a fix
failure: **stop and report to the user** with the group, its traces and the defect; it is not
presented for acceptance.

- [ ] **Step 6: The final tree's suites** (nothing else running)

| command | expected |
|---|---|
| `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null \| grep -a '^Results'` | `Results:  955  passed,  0  failed` |
| `maxima --very-quiet -b test/matcher/test_mr_match.mac < /dev/null \| grep -a '^Results'` | `Results: 53 passed, 0 failed` |
| `maxima --very-quiet -b test/matcher/test_mr_tree.mac < /dev/null \| grep -a '^Results'` | `Results: 51 passed, 0 failed` |
| `maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null \| grep -a '^Results'` | `Results:  58  passed,  0  failed` |
| `python3 test/check_generated_rules.py \| tail -1` | `Results: 14 passed, 0 failed` |
| `python3 test/test_run_records.py \| tail -1` | `Results: 23 passed, 0 failed` |
| `python3 probes/matcher/13-translation-shape-scan.py \| tail -1` | `Results: 90 passed, 0 failed` |

Then the regression suite, two arms one after the other, each `run_in_background` (~70 s):

```bash
MR_LEGS=tree,maxima MR_SPIKE=1 sh test/matcher/run.sh > "${TMPDIR:-/tmp}/p5b-defaults.log" 2>&1
MR_LEGS=tree,maxima MR_MODEL_FLAGS=1 MR_SPIKE=1 sh test/matcher/run.sh > "${TMPDIR:-/tmp}/p5b-flags.log" 2>&1
grep -a 'Results' "${TMPDIR:-/tmp}/p5b-defaults.log" "${TMPDIR:-/tmp}/p5b-flags.log"
```

Expected: `Results: 109 passed, 0 failed` twice (pre-validation: both arms 109 / 0 on the fixed tree).
(`test/test_driver_radcan_fallback.py` stays 3 / 1 — a fixture since P4, not a gate.)

- [ ] **Step 7: Commit the evidence**

```bash
git add probes/matcher/10-p5-attribution.py probes/matcher/10-p5-attribution.summary.py \
        probes/matcher/10-p5b-attribution.class[123]-*.out probes/matcher/10-p5b-attribution.class[123].summary.out \
        probes/matcher/10-p5b-attribution.mechanisms-*.md \
        test/corpus_class[123].p5b-final.timeout-rerun/*.timeout100s.out \
        test/corpus_class[123].p5b-final.timeout-rerun/merge.out \
        test/matcher/roundtrip.out test/matcher/roundtrip.flags.out test/matcher/controls.out \
        test/matcher/spike01.out test/matcher/gate.out test/matcher/gate.flags.out
git commit -m "probe: matcher 10 (extended) — P5b attribution, 100 s re-checks, mechanism lines, final-tree suites"
git worktree remove --force "${TMPDIR:-/tmp}/mr-p0-tree"
```

- [ ] **Step 8: The acceptance document** `probes/matcher/10-p5b-attribution.acceptance.md`

The format of `probes/matcher/10-p5-attribution.acceptance.md`: §1 header (final records and arm, P0
records, build, cores, evidence paths, how to answer); §2 defect clearance (the four defects and the
collapse fix: their probe 12/13/15 red→green lines, and "no group tagged" per class); §3 per class
(gate lines, probe 10 totals, 100 s re-check, family table, new timeouts, new errors with their
messages); §4 1.2.1.4 e810 and the order deviation (probe 14 figures, ticket 01); §5 appendix, every
group with its entries; §6 the acceptance template. Commit:

```bash
git add probes/matcher/10-p5b-attribution.acceptance.md
git commit -m "docs: P5b acceptance document — translation fixes"
```

- [ ] **Step 9: The ledger and TODO**

```markdown
### Task 7 — P5b gate
- final arm / records: <FINAL_ARM; F1 F2 F3>
- gates: <three p5_gate.py outputs' PASS:/FAIL:/INFO: count lines and Results>
- 100 s re-checks: <per class, merge.out's OK line and transitions>
- attribution: <per class, the summary totals and Results; NEW ERRORS count>
- defect clearance: <per class, "no group tagged">
- final tree: <Step 6's Results lines>
```

In `todo/TODO.md` set the translation-fixes item to "Tasks 1–7 done; P5b acceptance stop — open". Commit
(`git commit -m "docs: ledger — translation fixes Task 7 (P5b gate)"`).

- [ ] **Step 10: Stop — the user's acceptance**

Present, class by class, as Plan 3 Task 4 Step 9 did: the gate lines; the summary totals; every
`GROUP` once (id, disposition, size, mechanism line, clearance tag, two or three samples) with the
summary path; the new timeouts (counts, 100 s transitions) and the new errors (messages). The user
accepts or rejects per group, individual entries rejectable by id. Record verbatim:

```markdown
### Task 7 — user acceptance (<date>)
- class <N> <group id> (<size> entries): accepted | accepted except <entries> | rejected
- new timeouts: accepted | rejected: <entries>
```

Every PASS→FAIL accepted → Plan 3 Task 5 (run `p6_hardwire.py --check` first; the winners select its
variants), then Plan 3 Task 6 (its acceptance record cites the `p5b` records). Any rejection →
**stop**: the rejected entries are the input of a plan written then.
