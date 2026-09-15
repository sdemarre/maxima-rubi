# Matcher substrate — exact seen test and IntegerPart reading: design

Date: 2026-09-15. Branch `matcher-substrate` @ `a64db1a` (translation-fixes plan stopped at Task 7
Step 5). Parent designs: `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md` (§3.5,
§4 P5) and `docs/superpowers/specs/2026-09-14-matcher-translation-fixes-design.md` (§3.3, §4).
Measurements stamped Maxima `branch_5_50_base_84_g4204fb669` (build date 2026-08-31 13:27:47) /
SBCL 2.6.7. Design brainstorm with the user 2026-09-15 (handoff
`handoffs/2026-09-15-matcher-translation-fixes-stop.md`); amended the same day while the plan was
written and pre-validated (§0.2).

## 0. Context

The translation-fixes plan (`docs/superpowers/plans/2026-09-14-matcher-translation-fixes.md`)
stopped at Task 7 Step 5, defect clearance. Probe 16 (`probes/matcher/16-seen-guard-trace.out`,
`.class1.out`) shows the collapse mechanism at non-9.1 sites: `mr_int`'s ratsimp seen comparison
(`%mr_seenp`, `maxima_rubi_utils.mac:201–211`) reads a rule's rewrite to an algebraically equal
form as a loop and takes the `integrate` fall-through. The fix had given the exact test only to
9.1's `Int` calls (`mr_int_exact`). Collapse groups: class 2 g1; class 3 g12, g21, g48; 36 class-1
groups. Under the probe-local exact-only control, 78 entries reach PASS (5 + 6 + 67). P0 dodged
the comparison only because those rules fired in pass 2 or 3, after `mr_top` had popped
`%mr_seen`. A sibling finding stands beside it: `%mr_intPart_aux` / `%mr_fracPart_aux` read
IntPart/FracPart by floor where Rubi uses `IntegerPart`/`FractionalPart` (class 1 g27).

### 0.1 Decisions made in the brainstorm (user, 2026-09-15)

| question | decision |
|---|---|
| seen-test scope | approach A: exact `member` on every `mr_int` call; `%mr_seenp` deleted (§3.1) |
| `mr_int_exact` | removed: the generator emits `mr_int` for 9.1 again (§3.1) |
| class 1 g27 | port Rubi's `IntegerPart`/`FractionalPart` reading (§3.2) |
| tickets 02 (GtQ/GeQ) and 03 (EqQ/NeQ) | a separate plan after this one's acceptance |
| undetermined / no-route groups | carried to the p5c attribution, not diagnosed in this plan |
| re-measurement | run 1 (defaults) + one `mr_model_flags` flip run (§4) |

Alternatives weighed and rejected for the seen test: (B) exact `member` after a float-to-rational
normalization of both sides — it guards a cycle with no substrate evidence (§2) at an O(depth)
normalization cost per dispatch; it is the fallback if probe 17 finds the cycle. (C) pop `f` from
`%mr_seen` before the rule's replacement runs (P0's pass-2 behaviour, generalized) — it also drops
the exact-repeat cut the identity re-sends (1_4_1_r18, 1_1_3_7_r45) rely on, which would then spin
to the depth cap.

### 0.2 Decisions made while the plan was written (user, 2026-09-15)

| question | decision |
|---|---|
| P5b PASS entries that relied on the seen-cut `integrate` fall-through (§2, class 2 prototype run) | proceed with approach A; the p5c attribution tags such groups `route dispatched (was seen-cut integrate fall-through)`, not a defect, and the user judges them at the acceptance stop (§4 step 5) |
| corpus queue runner (proposed in the brainstorm to cut the sharding tail) | prototyped and measured, then **dropped** from this plan (§3.3); ticket `.scratch/corpus-harness/issues/01-queue-runner.md` |

## 1. Scope

In:

- the exact seen test for every dispatch and the removal of `%mr_seenp` and `mr_int_exact`;
- the `IntegerPart`/`FractionalPart` reading in `%mr_intPart_aux` / `%mr_fracPart_aux`;
- probe 17 (seen test, drift targets, IntPart; red/green), the unit checks and the gate changes that
  prove each;
- the p5c re-measurement and the acceptance stop, which replaces the translation-fixes plan's
  Task 7 Steps 6–10.

Out:

- tickets `.scratch/matcher-translation-fixes/issues/01` (case-fold order shim), `02` (GtQ/GeQ real
  reading), `03` (EqQ/NeQ zero test) — a separate plan;
- diagnosis of the undetermined / no-route groups (class 1 g1, g2, g15, g21, g196, g207,
  g247/g249/g250, the 16 part-B groups; class 2 g3; class 3 g20, g51) — re-attributed on the p5c
  records;
- the identity re-sends and single-term expansions probe 16 tagged `none` (1_4_1_r18,
  1_1_3_7_r45, 1_4_2_r19/r20, class 1 g9/g30) — exact repeats, unchanged by this design;
- matcher changes (`maxima_rubi_match.lisp`, `maxima_rubi_tree.lisp`);
- the corpus queue runner (§3.3, ticketed);
- Plan 3 Tasks 5–6 (they resume after acceptance).

## 2. Measured basis

Committed evidence:

- Collapse at non-9.1 sites, exact-only control counts, P0 routes (pass 2/3, seen list empty):
  `probes/matcher/16-seen-guard-trace.out` (`Results: 32 passed, 1 failed`), `.class1.out`
  (`Results: 179 passed, 7 failed`; the failures are control arms that did not return in 30 s).
- g27 mechanism: `probes/matcher/10-p5b-attribution.mechanisms-class1-b.md` (g27: 1_2_3_2_r34 on
  e254/e604 p=-1/2, e255/e605 p=-3/2; floor reads (-1, 1/2) and (-2, 1/2), Rubi (0, -1/2) and
  (-1, -1/2)).
- The drift guard's origin: commit `891240b` and `.superpowers/sdd/progress.md:1618–1649`
  (2026-08-25). The cycle `(104*(3/10*x+17/10)^4)/3` vs `(104*(0.3*x+1.7)^4)/3` was measured on
  the `defmatch` runner, in the session that also found `defmatch` binding unfilled slots to
  `false` and rebuilding garbage integrands through 1.1.1.7 r25's `mr_int` sub-dispatch. The
  source of the floats was not identified.
- P5b record lines (`test/corpus_class1.p5b-run1.out`): 1.1.1.4 e1, e3, e4, e5, e135 `verified`
  0.1 s; 1.1.1.7 e1 `timeout` 30.0 s.
- Wall medians (`python3 test/record_medians.py`): P0 (`test/corpus_class{1,2,3}.pre-matcher.out`,
  commit `0a6664c`) 1.3 / 4.3 / 3.9 s; P5b run 1 0.6 / 0.6 / 1.5 s; P5b run 1 p90 5.7 / 2.1 / 8.4 s.
- Probe 11 (`probes/matcher/11-arm-noise-recheck.p5b.*.out`): non-reproducing changed entries per
  switch, class 1 15–23, class 2 0, class 3 2–7.
- Rubi: `IntPart[u_,n_:1] := If[RationalQ[u], IntegerPart[n*u], …]`,
  `FracPart[u_,n_:1] := If[RationalQ[u], FractionalPart[n*u], …]`, each with an
  `m_*u_ /; RationalQ[m]` arm (`IntegrationUtilityFunctions.m:2952–2981`). `Rubi.m` defines no
  loop guard of its own (grep for `RecursionLimit`/`IterationLimit`: only `Steps`' use of
  `$IterationLimit`, :392).
- Call sites (`git grep`): `%mr_intPart(` / `%mr_fracPart(` 204 lines, all in replacements, none in
  conditions (class 1 mostly; 9_1 2, 2_1 1, 3_1_4 1, 3_1_5 1). `mr_int_exact(` 25 calls, all in
  `rules/class1/9_1.mac`, emitted by `generator/generate_rules.py:1191`; `ENTRY_CALL` in
  `test/check_generated_rules.py:50`; Layer A `test_translation_fixes_seen`
  (`test_maxima_rubi.mac:2942–2961`); no reference in the matcher unit suites.

Ad-hoc measurements of this brainstorm and the plan's pre-validation (2026-09-15, same build, scratch
worktrees). **Not evidence until committed** — probe 17 commits the first two; the p5c attribution
reads the third on the full corpus:

- `truncate` on `[-5/2, -3/2, -1/2, 0, 1/2, 3/2, -2, 2]` → `[-2, -1, 0, 0, 0, 1, -2, 2]`;
  `r - truncate(r)` → `[-1/2, -1/2, -1/2, 0, 1/2, 1/2, 0, 0]`; `floor` → `[-3, -2, -1, 0, 0, 1, -2,
  2]`. The first two equal Mathematica's `IntegerPart` / `FractionalPart` (the fractional part
  carries the sign of its argument).
- No `float(` in `maxima_rubi_utils.mac`, and no `numer` / `rationalize` / `bfloat` / `keepfloat` in
  the runtime sources (`maxima_rubi*.mac`, `maxima_rubi_*.lisp`), except `%mr_posAux` branch 2's
  `float(rectform(u))`, whose value decides a sign and never enters an integrand. A grep of each
  entry line's text before its first comma finds no decimal literal in classes 1 and 3 and one in
  class 2 (`%e^((-0.1)*x)*x`).
- **The seen-cut fall-through.** Class 2 on the changed tree (prototype, 24 queue workers) against
  `test/corpus_class2.p5b-run1.out`: PASS 771 vs 774, PASS→FAIL 16, FAIL→PASS 13; after removing the
  3 near-cap contention entries (2.3 e527, e528, e575, which fail identically on the unchanged tree
  under the same load), about 13 lost and 13 gained. Traced on both trees (probe 17's run with the
  cap trace): 2.1 e74/e79 and 2.3 e60/e195/e382/e487 verify on the unchanged tree in 0.5–1.6 s with
  one or two fires — the ratsimp seen test cuts the rule's equal-form nested `mr_int` call and
  Maxima's `integrate` answers it (2.3 e195 and e382 keep an `'integrate` noun that differentiates
  back). On the changed tree the nested call dispatches Rubi's route: 2.1 e74 verifies after 28
  fires (15 × 2_1_r1) in 21.9 s; e79, 2.3 e382, e487 time out; e195, e60 end `unverified`. No
  depth-cap hit and no float on any of them.

## 3. Design

### 3.1 The exact seen test (runtime + generator)

- `%mr_top_body(f, x, fb)` loses its `exact` argument. The seen test is `member(f, %mr_seen)` on
  every call. Unchanged: the depth cap (`%mr_max_depth` 16), the `%mr_seen` push/pop around the
  dispatch, the `mr_model_flags` binding, the `integrate` fall-through on a depth-cap hit, a seen
  hit or no rule (its load-bearing rationale comment stays).
- `mr_top(f, x, fb) := %mr_top_body(f, x, fb)`; `mr_int`, `rubi`, `rubi_fallback` keep their
  definitions.
- Deleted: `%mr_seenp` and its rationale comment (replaced by a pointer to probe 17 and this
  design); `mr_int_exact` and its comment block (the 9.1 equal-form rationale moves, shortened, to
  the seen-test comment: every rule's equal-form rewrite now dispatches).
- `generator/generate_rules.py:1191`: `Int`/`IntHide` translate to `mr_int` for every source key.
  `rules/class1/9_1.mac` is regenerated (9.1 is exempt from the static gate's body comparison);
  a second generation leaves `git status --porcelain rules/` empty.
- `test/check_generated_rules.py`: `ENTRY_CALL` drops `mr_int_exact`. The gate's count stays 14.
- Behaviour. Equal-form rewrites dispatch at every site. An exact repeat is still cut. Two rules
  rewriting back and forth between different equal forms stop at the depth cap and fall through;
  probe 17 and the fire traces of probe 10 show any such ping-pong, and the wall-ceiling gate
  watches its cost. Entries that passed only because the ratsimp cut handed an equal-form nested
  call to `integrate` now take Rubi's route (§2, §0.2).
- **Fallback trigger.** If probe 17 or the p5c attribution shows an integrand cycling between float
  and rational forms of the same expression up to the depth cap, stop and report: the design then
  moves to approach B (§0.1) by amendment.

### 3.2 The IntegerPart reading (utils)

- `%mr_intPart_aux(u, n)`: the rational branch is `truncate(n*u)`. `%mr_fracPart_aux(u, n)`: the
  rational branch is `r - truncate(r)` with `r : n*u`. The second, unreachable `%mr_rationalQ(u)`
  branch after the product arm is removed from both. The comments stating "IntegerPart is the floor
  reading" and "FractionalPart is the floor complement, so FracPart[-3/2] = 1/2" are corrected.
- Invariant kept: `IntPart[u] + FracPart[u] = u` for a rational `u`, so the rewritten integrands
  stay algebraically equal. Their form changes for negative non-integer exponents (p = -3/2:
  (-1, -1/2), was (-2, 1/2)); a nested integrand can carry the new exponent (e.g. 1_4_1 r37's
  `(…)^FracPart(p)`), so downstream routes can change. The p5c records read the effect.

### 3.3 The corpus queue runner (dropped)

The brainstorm proposed a manager with one queue and N worker threads (one entry per job) to remove
the sharding tail (P5b run 4, class 1: shards finished between +6 and +87 min). It was prototyped and
measured before the plan was written, on the unchanged tree against the P5b run-1 records (ad hoc,
ticket `.scratch/corpus-harness/issues/01-queue-runner.md`, prototype patch beside it): this VM's 24
vCPUs are 12 cores × 2 threads, and 24 busy workers slow every entry — class 3 in 9.7 min (sharded
20) but median 1.8 s vs 1.5, 29 more timeouts and 17 PASS→FAIL, all timeouts; 12 workers keep the
per-entry walls (class 2: median 0.6 s, p90 2.1 s, as P5b) but project class 1 at ~101 min against
87 sharded. The user dropped it from this plan (§0.2). The p5c runs use the sharded launchers.

### 3.4 Evidence

Red first: probe 17 runs on the current tree (core `b98e4748…`) and its output is committed; the
change follows; the probe re-runs on the changed tree and the green output is committed beside the
red one.

| probe | kind | content |
|---|---|---|
| `probes/matcher/17-exact-seen-intpart` | driver entry text, `rubi_verbose`, a depth-cap trace, 8 workers | SEEN: probe 16's collapse entries (class 2 g1 ×5, class 3 g12 ×4, g21 ×3, g48 ×1, the 67 class-1 control-PASS entries from `16-seen-guard-trace.class1.out`) — red: the P5b class; green: every entry that reached PASS under probe 16's exact-only control reaches PASS; a miss is listed with its fire trace and stops the plan unless the trace attributes it to the IntPart change (a fired replacement calling `%mr_intPart`/`%mr_fracPart`). DRIFT: 1.1.1.4 e1, e3, e4, e5, e135 and 1.1.1.7 e1 with the fire trace, the wall, the depth-cap hit count, and at each depth-cap hit whether the integrand or `%mr_seen` holds a float — green: no class on a worse side than P5b run 1, no float at a cap hit; plus a scan of every class 1–3 corpus integrand (the parsed first element) for float literals. INTPART: `truncate`/`floor` on the §2 rationals; `%mr_intPart`/`%mr_fracPart` on -1/2, -3/2, -5/2, 3/2, `-3/2*x`, `3/2 + x`; g27 e254, e255, e604, e605 through 1_2_3_2_r34 with their answers — green: Rubi's values; the entries' classes recorded, not required to PASS (the AppellF1 verification gap is a separate mechanism) |

### 3.5 Unit checks and tree gates

Layer A (`test_maxima_rubi.mac`, 957 → 964):

- `test_translation_fixes_seen` rewritten (5 → 6 checks): a ratsimp-equal seen form dispatches under
  `mr_int` (77); an exact repeat takes the fall-through; `%mr_seenp`, `mr_int_exact`, `rubi_hybrid`,
  `rubi_hybrid_exact` are not defined.
- IntPart/FracPart: `iP -3/2` → -1 (was -2), `fP -3/2` → -1/2 (was 1/2); new checks `iP -1/2` → 0,
  `fP -1/2` → -1/2, `iP -5/2` → -2, `fP -5/2` → -1/2, `iP -3/2*x` → 0, `fP -3/2*x` → `-3/2*x`.
  Expectations derive from Rubi's definitions (§2), not from the port's output.

Tree gates on the changed tree:

- the static gate `Results: 14 passed, 0 failed`; regeneration byte-identical;
- `sh test/build_rules_core.sh`, fingerprint recorded in the ledger;
- probe 08 re-run flagless (utils and a rule file changed), record rewritten;
- matcher unit suites green (match 53, tree 51, dispatch 58); `test/test_run_records.py` 23;
- the matcher regression suite, 109 in both arms (never run on the translation-fixes tree).

Docs: AGENTS.md (Layer A count); the translation-fixes design §3.3 and the parent spec §3.5 amended
with a pointer to this design; the corrected utils and generator comments.

## 4. Re-measurement and the acceptance stop

Plan 3's procedures with the sharded launchers and the record prefix `p5c`:
`test/corpus_class<N>.p5c-run<K>.out`, `test/corpus_class<N>.p5c-final.timeout-rerun/`,
`probes/matcher/10-p5c-attribution.*`. Run numbers follow P5b's (run 4 = `mr_model_flags`
flipped).

1. **Preconditions.** The changed tree committed; the core built, its fingerprint in the ledger and
   checked before every launch; §3.5's gates green; probe 17 green.
2. **Run 1 (defaults)**, classes 2 → 3 → 1; `p5_gate.py gate` against the P0 records
   (`test/corpus_class{1,2,3}.pre-matcher.out`) with Plan 3's stop rules. Informational, in the ledger:
   `ab_records.py test/corpus_class<N>.p5b-run1.out test/corpus_class<N>.p5c-run1.out`.
3. **Run 4 (`MR_SWITCHES="mr_model_flags=false"`)**, all three classes;
   `p5_gate.py winner mr_model_flags` over runs 1 and 4. Probe 11 on `mr_model_flags` only when the
   raw winner is the flip; a run 5 only when the noise-filtered winner is the flip. The other two
   switches keep P5b's noise-filtered winners (the defaults).
4. **Final gates.** `p5_gate.py gate` on the final records; the 100 s timeout re-checks; a P0-core
   worktree at `0a6664c`; probe 10's `final30`, `p0`, `final120` and `newerror` legs and summaries.
5. **Defect clearance.** Each p5c PASS→FAIL group gets a mechanism line. A group still explained by
   collapse (a ratsimp-type seen cut cannot occur any more; an equal-form route cut by the depth
   cap is reported as ping-pong), by the floor IntPart reading, or by one of the four
   translation-fixes defects (IGT, NEGQ, NE, MUL) or a listed sibling is a fix failure: **stop and
   report**. A group whose P5b PASS came from the seen-cut `integrate` fall-through and whose p5c
   route is Rubi's is tagged `route dispatched (was seen-cut integrate fall-through)` and presented
   for acceptance (§0.2). A group explained by tickets 01–03 is tagged `none` with the ticket named.
   Undetermined groups are listed.
6. **Final-tree suites** (§3.5 counts).
7. **Acceptance document** `probes/matcher/10-p5c-attribution.acceptance.md` in the format of the
   earlier ones (per group, entries rejectable by id, new timeouts, new errors). **Stop for the
   user's acceptance.** It replaces the translation-fixes plan's Task 7 Steps 6–10; that plan's
   ledger records the supersession.
8. **After acceptance:** Plan 3 Task 5 (`p6_hardwire.py --check` first; its anchors are re-validated
   after this plan touches the generator, the utils and `9_1.mac`), then Task 6 (the acceptance
   record cites the `p5c` records); then the tickets 02/03 plan.

Machine time, estimated from P5b: runs 1 and 4 ~2 h each (class 1 ~87 min, class 3 ~20, class 2
~5); 100 s re-checks ~1–1.5 h; probe 10 ~3 h; probe 11 on one switch, if needed, 1–3 h.

## 5. Acceptance criteria

1. Probe 17 committed with red and green outputs.
2. Layer A, the static gate, the matcher unit suites and the regression suite green on the changed
   tree at their new counts; regeneration byte-identical; probe 08 flagless.
3. The `p5c` final records pass `p5_gate.py gate` against P0 (complete, arm, pass floor, wall
   ceiling).
4. Every `p5c` PASS→FAIL entry attributed; no group explained by collapse, the floor IntPart
   reading, a translation-fixes defect or a listed sibling (§4 step 5).
5. The user's per-group acceptance recorded in the ledger.

## 6. Risks and sharp edges

- **Form-sensitive seen test.** Exact `member` compares stored forms, so a pair of rules alternating
  between two equal forms runs to depth 16 before the fall-through — up to 16 table dispatches per
  cycle. The wall-ceiling gate, probe 17's cap-hit counts and probe 10's fire traces watch it.
- **The seen-cut fall-through entries.** Entries that passed only through the ratsimp cut's
  `integrate` answer now follow Rubi's route, which can be slower, time out or end unverified (§2:
  about 13 in class 2). The pass floor against P0 still gates the records; the attribution tags the
  groups (§4 step 5).
- **The drift cycle may be real on the substrate.** No float source is known (§2), but it was never
  identified on `defmatch` either. Probe 17 checks the recorded targets; the p5c attribution reads
  new timeouts. The fallback is approach B by amendment (§3.1).
- **`mr_model_flags` interacts with the exact test.** `radexpand:false` / `logexpand:false` change
  stored forms, which the exact test now reads; run 4 measures the switch again (§4 step 3).
- **IntPart forms change nested routes** at up to 204 replacement sites; the attribution reads
  every PASS→FAIL.
- **Disk.** `/` had 3.6 GB free on 2026-09-15 after removing old cores; each run's shard files are
  small, the P0-core worktree and core ~0.2 GB. Check `df` before the probe 10 legs.
- **Probe 16 does not run on the changed tree** (it asserts `%mr_seenp`'s source); it stays the
  committed record of the stop.

## 7. Deliverables

- this design (committed);
- plan `docs/superpowers/plans/2026-09-15-matcher-seen-test-intpart.md`, written next (just in
  time): red probe 17; the seen test and generator with Layer A; the IntPart reading with Layer A;
  the changed tree's evidence (core, probe 08, green probe 17, tree gates, docs); p5c runs 1 and 4
  and the winner; final gates, attribution, clearance, final-tree suites and the acceptance stop;
- the records, probes and acceptance document named in §3.4 and §4.
