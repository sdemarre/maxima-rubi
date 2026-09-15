# Matcher substrate — exact seen test, IntegerPart reading, corpus queue: design

Date: 2026-09-15. Branch `matcher-substrate` @ `a64db1a` (translation-fixes plan stopped at Task 7
Step 5). Parent designs: `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md` (§3.5,
§4 P5) and `docs/superpowers/specs/2026-09-14-matcher-translation-fixes-design.md` (§3.3, §4).
Measurements stamped Maxima `branch_5_50_base_84_g4204fb669` (build date 2026-08-31 13:27:47) /
SBCL 2.6.7. Design brainstorm with the user 2026-09-15 (handoff
`handoffs/2026-09-15-matcher-translation-fixes-stop.md`).

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
| corpus sharding tail | a queue runner, Task 1 of this plan, validated before the p5c runs (§3.3) |

Alternatives weighed and rejected for the seen test: (B) exact `member` after a float-to-rational
normalization of both sides — it guards a cycle with no substrate evidence (§2) at an O(depth)
normalization cost per dispatch; it is the fallback if probe 17 finds the cycle. (C) pop `f` from
`%mr_seen` before the rule's replacement runs (P0's pass-2 behaviour, generalized) — it also drops
the exact-repeat cut the identity re-sends (1_4_1_r18, 1_1_3_7_r45) rely on, which would then spin
to the depth cap.

## 1. Scope

In:

- the exact seen test for every dispatch and the removal of `%mr_seenp` and `mr_int_exact`;
- the `IntegerPart`/`FractionalPart` reading in `%mr_intPart_aux` / `%mr_fracPart_aux`;
- the corpus queue runner (`test/run_corpus_queue.py`) and the driver refactor it needs;
- probes 17 (seen test and IntPart, red/green) and 18 (queue equivalence), the unit checks and the
  gate changes that prove each;
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
- probes 10/11/16's own worker pools (the queue replaces only the corpus launchers);
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
- Wall medians (`python3 test/record_medians.py`): P0 (`test/corpus_class{1,2,3}.out`) 1.3 / 4.3 /
  4.2 s; P5b run 1 0.6 / 0.6 / 1.5 s; P5b run 1 p90 5.7 / 2.1 / 8.4 s.
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
- Sharding tail, P5b run 4 shard `.out` mtimes (`test/corpus_class{1,2,3}.shard*.out`, launch
  times from the shard headers): class 1 launched 20:32 UTC, shards finished between +6 and
  +87 min, mean ≈ 46 min — all 24 processes busy for about 53 % of the wall; class 3 last shard
  +20 min, mean ≈ 7 min; class 2 last +4.6 min, mean ≈ 1 min. The launcher packs shards by the
  previous record's per-entry times (`test/launch_class_shards.py:86–191`), which go stale when
  routes change.
- Machine: 24 cores (AMD Ryzen 9 9900X, one thread per core), 62 GB RAM.

Ad-hoc measurements of this brainstorm (2026-09-15, same build). **Not evidence until committed**
— probe 17 commits them:

- `truncate` on `[-5/2, -3/2, -1/2, 0, 1/2, 3/2, -2, 2]` → `[-2, -1, 0, 0, 0, 1, -2, 2]`;
  `r - truncate(r)` → `[-1/2, -1/2, -1/2, 0, 1/2, 1/2, 0, 0]`; `floor` → `[-3, -2, -1, 0, 0, 1, -2,
  2]`. The first two equal Mathematica's `IntegerPart` / `FractionalPart` (the fractional part
  carries the sign of its argument).
- No `float(` in `maxima_rubi_utils.mac`, and no `numer` / `rationalize` / `bfloat` / `keepfloat` in
  the runtime sources (`maxima_rubi*.mac`, `maxima_rubi_*.lisp`), except `%mr_posAux` branch 2's
  `float(rectform(u))`, whose value decides a sign and never enters an integrand. A grep of each
  entry line's text before its first comma finds no decimal literal in classes 1 and 3 and one in
  class 2 (`%e^((-0.1)*x)*x`).

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
  watches its cost.
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

### 3.3 The corpus queue runner (harness)

- **Driver refactor** (`test/corpus_driver.py`). The per-entry body of `main()`
  (`corpus_driver.py:711–747`) becomes `run_entry(rel, idx, entry_text, line_no)` returning
  `(cls, line)`; the header construction (:667–689) becomes `header_lines(extra)`. `main()` calls
  both and keeps its output format; the sharded launchers keep working unchanged. `REWRITE_STATS`
  updates take a lock.
- **Manager** `test/run_corpus_queue.py`:
  - Positional `SECTION`, `DRIVER`; options `--prev RECORD` (cost order), `--workers N` (default
    `MR_N_PROCS` or `os.cpu_count()`), `--cap S` (default 30), `--entries-from RECORD --class CLS`
    (a subset, e.g. a record's `timeout` class for the 100 s re-check), `--out-dir DIR` (default
    `test/`), `--launch` (without it: a dry run printing entries, workers, estimated core-seconds
    and estimated wall `max(total / N, longest)`).
  - Imports the driver as the launchers do (the `sys.argv` rewrite; `ensure_rules_core()` runs at
    import; `MR_SWITCHES` and `MR_RULES_CORE_PATH` are honoured by the driver as today).
  - Entry order: descending previous-record time; entries without a previous time first.
  - `N` worker threads pull from one queue; one job is one entry, i.e. one `maxima_run`
    subprocess (stdin `/dev/null`, inherited). Worker `k` owns
    `corpus_<slug>.shard<kk>.out`: the driver's header, one line per finished entry (flushed), the
    driver's summary block for its own lines. The format is the one `merge_class_shards.py` parses,
    so the merger, `wait_and_merge.sh`, `ab_records.py`, `p5_gate.py` and `record_medians.py` are
    unchanged.
  - `--launch` first calls `run_records.clear_stale_shards` (same refusal while a previous pid is
    alive), then re-executes itself detached (`start_new_session`) and writes
    `corpus_<slug>.shard-pids` with one line `queue <pid> -`, which `wait_and_merge.sh` waits on.
  - A Python exception around one entry writes that entry as `error t=0.0s <label>`, prints the
    traceback to the manager log, and the manager exits non-zero with the harness-failure count; the
    merge's completeness assertion still runs.
  - Timeout re-check mode writes its shard files into `--out-dir` with the cap in the header's
    `timeout:` field, in the layout `test/merge_timeout_rerun.py` reads; where that merger's
    expectations differ, the plan adapts the manager, not the merger.
- **Guards** (`test/test_run_records.py`, no Maxima): `run_entry` on a stubbed `maxima_run` gives the
  line `main()` gives; queue shard files of a synthetic run merge through `merge_class_shards.py`'s
  parser with complete keys and one stated switch arm; a harness exception yields an `error` line.
  Count 23 → 23 + k, k stated in the plan.
- **Equivalence (probe 18)** on the current core (fingerprint `b98e4748…`, switch defaults), before
  any runtime change: classes 2 and 3 through the queue →
  `test/corpus_class{2,3}.queue-check.out`. Criteria: `ab_records.py` against
  `test/corpus_class{2,3}.p5b-run1.out` exits 0 (same key set); every PASS/FAIL transition re-run
  three times through the driver's own mechanics (probe 11's `run_job`), and none reproduces under
  probe 11's noise rule (all three re-runs giving the queue record's side); median wall ≤ the
  p5b-run1 median (0.6 s / 1.5 s); the queue wall-clock recorded against the sharded run's
  (4.6 min / 20 min, §2). A reproducing transition stops the plan before the p5c runs.
- **Docs.** AGENTS.md's Layer B and timeout re-check invocations and `docs/class-porting.md`
  Steps 8–9 switch to the queue; `launch_class_shards.py`, `launch_class1_shards.py` and
  `launch_timeout_rerun.py` stay, documented as the previous mechanism.

### 3.4 Evidence

Red first: each probe section is run on the current tree (core `b98e4748…`) and its output
committed; the change follows; the probe re-runs on the changed tree and the green output is
committed beside the red one.

| probe | kind | content |
|---|---|---|
| `probes/matcher/17-exact-seen-intpart` | driver entry text, `rubi_verbose`, 8 workers | SEEN: probe 16's collapse entries (class 2 g1 ×5, class 3 g12 ×4, g21 ×3, g48 ×1, the 67 class-1 control-PASS entries from `16-seen-guard-trace.class1.out`) — red: the P5b class; green: every entry that reached PASS under probe 16's exact-only control reaches PASS; a miss is listed with its fire trace and stops the plan unless the trace attributes it to the IntPart change (a fired replacement calling `%mr_intPart`/`%mr_fracPart`). DRIFT: 1.1.1.4 e1, e3, e4, e5, e135 and 1.1.1.7 e1 with the fire trace, the wall, the depth-cap hit count, and at each depth-cap hit whether `%mr_seen` holds a float — green: no class worse than red, no float at a cap hit; plus a scan of every class 1–3 corpus integrand (the parsed first element) for float literals. INTPART: `truncate`/`floor` on the §2 rationals; `%mr_intPart`/`%mr_fracPart` on -1/2, -3/2, -5/2, 3/2, `-3/2*x`, `3/2 + x`; g27 e254, e255, e604, e605 through 1_2_3_2_r34 with their answers — green: Rubi's values; the entries' classes recorded, not required to PASS (the AppellF1 verification gap is a separate mechanism) |
| `probes/matcher/18-queue-equivalence` | Python + the queue | §3.3's equivalence run: the two queue records, the `ab_records.py` tables, the three-run re-checks of every transition, the medians and wall-clocks; `Results:` requires the criteria |

### 3.5 Unit checks and tree gates

Layer A (`test_maxima_rubi.mac`, 957 → 957 + k, k stated in the plan):

- `test_translation_fixes_seen` rewritten: a ratsimp-equal seen form dispatches under `mr_int`
  (77); an exact repeat takes the fall-through; `%mr_seenp` and `mr_int_exact` are not defined.
- IntPart/FracPart: `iP -3/2` → -1 (was -2), `fP -3/2` → -1/2 (was 1/2); new checks `iP -1/2` → 0,
  `fP -1/2` → -1/2, `iP -5/2` → -2, `fP -5/2` → -1/2, `iP -3/2*x` → 0, `fP -3/2*x` → `-3/2*x`.
  Expectations derive from Rubi's definitions (§2), not from the port's output.

Tree gates on the changed tree:

- the static gate `Results: 14 passed, 0 failed`; regeneration byte-identical;
- `sh test/build_rules_core.sh`, fingerprint recorded in the ledger;
- probe 08 re-run flagless (utils and a rule file changed), record rewritten;
- matcher unit suites green (match 53, tree 51, dispatch 58);
- `test/test_run_records.py` at its new count;
- the matcher regression suite, 109 in both arms (never run on the translation-fixes tree).

Docs: AGENTS.md (Layer A, guard counts, Layer B invocations); the translation-fixes design §3.3 and
the parent spec §3.5 amended with a pointer to this design; the corrected utils and generator
comments.

## 4. Re-measurement and the acceptance stop

Plan 3's procedures, with the queue runner and the record prefix `p5c`:
`test/corpus_class<N>.p5c-run<K>.out`, `test/corpus_class<N>.p5c-final.timeout-rerun/`,
`probes/matcher/10-p5c-attribution.*`. Run numbers follow P5b's (run 4 = `mr_model_flags`
flipped).

1. **Preconditions.** Probe 18 green; the changed tree committed; the core built, its fingerprint in
   the ledger and checked before every launch; §3.5's gates green; probe 17 green.
2. **Run 1 (defaults)**, classes 2 → 3 → 1; `p5_gate.py gate` against the P0 records
   (`test/corpus_class{1,2,3}.out`) with Plan 3's stop rules. Informational, in the ledger:
   `ab_records.py test/corpus_class<N>.p5b-run1.out test/corpus_class<N>.p5c-run1.out`.
3. **Run 4 (`MR_SWITCHES="mr_model_flags=false"`)**, all three classes;
   `p5_gate.py winner mr_model_flags` over runs 1 and 4. Probe 11 on `mr_model_flags` only when the
   raw winner is the flip; a run 5 only when the noise-filtered winner is the flip. The other two
   switches keep P5b's noise-filtered winners (the defaults).
4. **Final gates.** `p5_gate.py gate` on the final records; the 100 s timeout re-checks through the
   queue; a P0-core worktree at `0a6664c`; probe 10's `final30`, `p0`, `final120` and `newerror`
   legs and summaries.
5. **Defect clearance.** Each p5c PASS→FAIL group gets a mechanism line. A group still explained by
   collapse (a ratsimp-type seen cut cannot occur any more; an equal-form route cut by the depth
   cap is reported as ping-pong), by the floor IntPart reading, or by one of the four
   translation-fixes defects (IGT, NEGQ, NE, MUL) or a listed sibling is a fix failure: **stop and
   report**. A group explained by tickets 01–03 is tagged `none` with the ticket named. Undetermined
   groups are listed.
6. **Final-tree suites** (§3.5 counts).
7. **Acceptance document** `probes/matcher/10-p5c-attribution.acceptance.md` in the format of the
   earlier ones (per group, entries rejectable by id, new timeouts, new errors). **Stop for the
   user's acceptance.** It replaces the translation-fixes plan's Task 7 Steps 6–10; that plan's
   ledger records the supersession.
8. **After acceptance:** Plan 3 Task 5 (`p6_hardwire.py --check` first; its anchors are re-validated
   after this plan touches the generator, the utils and `9_1.mac`), then Task 6 (the acceptance
   record cites the `p5c` records); then the tickets 02/03 plan.

Machine time, estimated from P5b and §2's tail figures: probe 18 ~0.5 h; runs 1 and 4 ~2 h with the
queue; 100 s re-checks ~1–1.5 h; probe 10 ~3 h; probe 11 on one switch, if needed, 1–3 h.

## 5. Acceptance criteria

1. Probes 17 and 18 committed; probe 17 with red and green outputs.
2. Layer A, the static gate, the matcher unit suites, `test/test_run_records.py` and the regression
   suite green on the changed tree at their new counts; regeneration byte-identical; probe 08
   flagless.
3. The `p5c` final records pass `p5_gate.py gate` against P0 (complete, arm, pass floor, wall
   ceiling).
4. Every `p5c` PASS→FAIL entry attributed; no group explained by collapse, the floor IntPart
   reading, a translation-fixes defect or a listed sibling (§4 step 5).
5. The user's per-group acceptance recorded in the ledger.

## 6. Risks and sharp edges

- **Form-sensitive seen test.** Exact `member` compares stored forms, so a pair of rules alternating
  between two equal forms runs to depth 16 before the fall-through — up to 16 table dispatches per
  cycle. The wall-ceiling gate, probe 17's cap-hit counts and probe 10's fire traces watch it.
- **The drift cycle may be real on the substrate.** No float source is known (§2), but it was never
  identified on `defmatch` either. Probe 17 checks the recorded targets; the p5c attribution reads
  new timeouts. The fallback is approach B by amendment (§3.1).
- **`mr_model_flags` interacts with the exact test.** `radexpand:false` / `logexpand:false` change
  stored forms, which the exact test now reads; run 4 measures the switch again (§4 step 3).
- **IntPart forms change nested routes** at up to 204 replacement sites; the attribution reads
  every PASS→FAIL.
- **Queue fidelity.** Different entry ordering changes which entries run concurrently; per-entry
  wall under load is what the 30 s cap sees. Probe 18's re-checks and median comparison bound the
  effect before any p5c run.
- **Disk.** `/` had 3.6 GB free on 2026-09-15 after removing old cores; each run's shard files are
  small, the P0-core worktree and core ~0.2 GB. Check `df` before the probe 10 legs.
- **Probe 16 does not run on the changed tree** (it asserts `%mr_seenp`'s source); it stays the
  committed record of the stop.

## 7. Deliverables

- this design (committed);
- plan `docs/superpowers/plans/2026-09-15-matcher-seen-test-intpart.md`, written next (just in
  time), in about six tasks: the queue runner, guards and probe 18; red probe 17; the seen test,
  generator and IntPart changes with Layer A; regeneration, core, probe 08, green probe 17, tree
  gates, docs; p5c runs 1 and 4 and the winner; final gates, attribution, clearance, final-tree
  suites and the acceptance stop;
- the records, probes and acceptance document named in §3.4 and §4.
