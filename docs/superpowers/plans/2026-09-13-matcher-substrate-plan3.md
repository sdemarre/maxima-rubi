# Matcher Substrate — Plan 3 (P5–P6): migration A/B and close

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the full class 1–3 corpus under each migration switch arm, keep the winning arm of
each switch by the spec's rule, hold the final records to the P0 parity and performance gates with
every PASS→FAIL attributed and accepted by the user, then hard-wire the winners, delete the
switches and write the acceptance record and the documentation (spec §4 P5–P6, §5).

**Architecture:** Task 1 makes every corpus record state the switch arm it ran (`MR_SWITCHES` →
the driver's entry text and `filter:` line → the merged record), fixes the harness's crash verdict
(an inherited stdin turned a fatal SBCL error into `timeout`) and the launcher's stale shards, and
adds the P5 gate script. Tasks 2–3 are measurement on an unchanged tree: sharded runs whose arm is
an environment variable, winners picked by a committed rule. Task 4 gates the final records,
attributes every PASS→FAIL on the P0 core against the final core, and stops for the user's
acceptance. Tasks 5–6 remove the switches (one variant per possible winner, spelled out) and write
the record and the docs.

**Tech Stack:** Maxima `branch_5_50_base_84_g4204fb669` (build date 2026-08-31 13:27:47) /
SBCL 2.6.7; Common Lisp loaded into Maxima; Python 3 harness scripts.

**Spec:** `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md` (committed `48c61b8`) —
§3.5 (head index fallback, `rubi_hybrid`), §3.6 (switches), §4 P5/P6 (gates), §5 (acceptance),
§6 (risks), §7 (deletions, P6 rows). This is Plan 3 of three (user decision 2026-09-12: Plan 3 =
P5–P6). Plans 1–2 are executed and merged into `master` (`8764c2a`); their figures are in
`.superpowers/sdd/progress.md` § "Plan: 2026-09-12 matcher substrate plan 1" and § "Plan:
2026-09-13 matcher substrate plan 2"; the writing handoff is
`handoffs/2026-09-13-matcher-plan3-writing.md`.

**Attachments:** `docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.files/`, committed with
this plan — the verbatim inputs too long to repeat inline:

| attachment | used by |
|---|---|
| `tooling/run_records.py`, `tooling/p5_gate.py`, `tooling/test_run_records.py` | Task 1 Step 2 |
| `tooling/p5-tooling.patch` (driver, launcher, the two mergers, the dispatch suite) | Task 1 Step 3 |
| `probes/09-harness-fault-verdict.sh` | Task 1 Step 6 |
| `probes/10-p5-attribution.py`, `probes/10-p5-attribution.summary.py` | Task 4 Step 4 |
| `p6/p6_hardwire.py` (the winner-selected P6 edits, `--check` for its anchors) | Task 5 Steps 1–3 |
| `tooling/p6-switch-plumbing.patch` (driver, launcher, mergers, `run_records`, its guard, probe 10) | Task 5 Step 3 |

**User decisions taken while writing (2026-09-13):** branch `matcher-substrate`, re-cut from
`master` @ `8764c2a`; pre-validation = the Task 1 tooling in a throwaway worktree plus P5 run-1
scouts of classes 2, 3 and 1 on the `master` tree; the push-access fix deferred; the PASS→FAIL
list presented as groups in the terminal (mechanism, size, samples) with every entry in committed
summary files, accepted per group with individual entries rejectable by id (revised after the
class-1 scout's 1,826 PASS→FAIL); every P5 run full, no early stop; a failing
median-wall gate stops the plan and the spec §3.5 head index gets its own just-in-time plan; the
regression suite's alternative arms stay as suite-only knobs; the MODEL-LOST figures are explained
only if the `mr_model_flags` arm's attribution needs them.

**Deviations from the spec's wording (stated, not silent):**

1. *Switch arm on every record* (§3.6 "set by the driver, which writes them into each record's
   `filter:` line"). The arm comes from one environment variable, `MR_SWITCHES`
   (space-separated `<switch>=true|false`; unset switches keep the dispatcher's defaults). The
   driver assigns all three switches at the head of every entry text and appends
   `switches: mr_flat_wide=<v> mr_cond_retry=<v> mr_model_flags=<v>` to its `filter:` line;
   `merge_class_shards.py` refuses shards that state no arm or two arms and carries the arm into
   the merged record; `merge_timeout_rerun.py` refuses a re-check whose shards ran another arm than
   the source record. (A separate name, not `MR_MODEL_FLAGS`: the regression suite already uses
   that one for its converter arm.)
2. *Crash verdict* (carried: "crash-class counts vs P0"). The driver's crash verdict is `error`
   (no CLASS line, not timed out). Probe 09 (Task 1) measured two facts the carried item did not
   know: (a) under the rules core — the image every corpus run uses — probe 07's fatal
   control-stack shape is survived (SBCL unprotects the guard page, the MatchQ returns false), so
   it reads as an ordinary class, not a crash; (b) on the standard-load path the same shape dies
   into SBCL's `ldb` monitor, which reads stdin — with the stdin the driver's subprocess inherited
   (a pipe) the entry waited for the 30 s cap and read `timeout`, with `/dev/null` it reads
   `error` in ~2 s. The driver now gives every entry subprocess stdin `/dev/null` (the batch
   answers its prompts from the batch file). `test/p5_gate.py` counts `error` per record against
   P0 and lists every entry that is `error` only in the new record.
3. *Speed-gate definition* (carried). "Per-class median per-entry wall" is the median of the `t=`
   field over every entry of the merged record (the figure `test/record_medians.py` prints to
   0.1 s), compared unrounded with the P0 record's: new ≤ P0. No noise tolerance is added: the
   same-core class-3 noise band (`probes/matcher/05-p0-wall-noise.out`, a −7.1 % median shift) is
   cited when a result sits within 10 % of the ceiling, and such a result is reported to the user,
   not re-run silently.
4. *Head index* (§3.5 "else the head index … then re-run"; §4 P5). Not in this plan (user decision
   2026-09-13): a wall-ceiling FAIL on a run-1 record (Task 2) or on a final record (Task 4) stops
   execution and is reported; the head index gets its own plan, written then.
5. *Suite-only knobs* (§7 "losing switch arms, the switches | P6"). P6 deletes the three Maxima
   option variables and every runtime path of a losing arm. The matcher regression suite keeps
   measuring both G-6 readings and both simplifier arms (user decision 2026-09-13): `mr-match`
   keeps `*flat-wide*` (default `nil`, bound only by `test/matcher/roundtrip.lisp` and
   `controls.lisp`) — G-6 has no Mathematica oracle (§6), so the measurement stays re-runnable for
   class 4+ — and `test/matcher/run.sh` keeps `MR_MODEL_FLAGS`. The suite's gate count stays
   109.
6. *MODEL-LOST* (carried: 1,166 / 395 measured vs the spec's 1,142 / 312). Explained only if the
   `mr_model_flags` arm's attribution (Task 3 Step 8) needs it (user decision 2026-09-13);
   otherwise the acceptance record states the figures as measured and unexplained.
7. *`rubi_hybrid` criterion* (§3.5). No rule file calls `rubi_hybrid` / `rubi_hybrid_exact` since
   Plan 2 (the static gate's `ENTRY_CALL` check). They are deleted in Task 5 unless 1.2.1.3 e839
   (the collapse-family entry the exact seen comparison was written for) is PASS→FAIL in the
   final class-1 record; if it is, Task 4 stops — the exact comparison as a translation fix is a
   design change outside this plan.
8. *Attribution method* (§4 P5 "every PASS→FAIL attributed"). Probe 10 (Task 4) is the class-3
   campaign's probe-09 method (`docs/corpus-class3-deferred-uplift.md` §5.3) on two cores under one
   build: each PASS→FAIL entry re-run through the driver's exact entry text on the final core (at
   30 s, and at 120 s when the final record reads `timeout`) and on the P0 core (built from
   `0a6664c`), with `rubi_verbose` fire traces; a mechanical disposition (noise / p0-noise /
   near-cap / slow-correct / deterministic) and deterministic entries grouped by the final core's
   class and top-level rule. The implementer writes one mechanism line per group from the traces;
   the user accepts per group and may reject individual entries by id — accepting a group accepts
   each entry its committed summary lists (the spec's "individually accepted", at the ~2,030
   entries the scouts preview).
9. *MatchQ residuals* (plan-2 final review, parked). Numeric folding in MatchQ part substitution
   and a parts-keyed compiled-pattern cache are carried to `todo/TODO.md` (Task 1), not built: the
   cache's need is what the P5 wall gate measures, and a passing gate leaves it unmeasured-need.
10. *Records.* P5 records are `test/corpus_class<N>.p5-run<K>.out` (K = 1–4, 5 when the winners
    differ from run 1), all committed (the winner rule cites them). The final records are copied to
    the standing `test/corpus_class<N>.out` in Task 6.
11. *Switch plumbing after P6.* Task 5 removes the Task 1 switch plumbing from the driver and the
    mergers (the switches no longer exist); `test/run_records.py` keeps `record_switches` and
    `clear_stale_shards`; `test/p5_gate.py` and probe 10 stay as the P5 tools over the committed
    P5 records, whose `switches:` lines remain.
12. *Pre-validation scope* (user decision 2026-09-13): Task 1's code was run before this plan was
    written; Tasks 2–4 are measurement (the scouts below preview them); Task 5's variant code and
    Task 6's documents are not pre-validated.

## Global Constraints

Every task's requirements implicitly include this section.

- **Build (stamp, never pin):** every committed measurement output carries `build_info()`
  (`build_info()@version`, `build_info()@timestamp`) or, for a no-Maxima script, the run date and
  git HEAD. Corpus records carry the merge's `maxima:` lines.
- **30 s corpus cap STAYS** (user decision 2026-08-27). The 100 s timeout re-check is the standing
  answer to "is the cap the limit?".
- **One corpus-scale run at a time; walls are gates.** While a sharded run, a timeout re-check or
  probe 10 is live, run nothing else heavier than reading files — no Layer A, no unit suite, no
  core build, no second run. Check before every launch:
  `ps -eo args | grep -E '^python3 .*(corpus_driver|corpus_class1_driver)\.py' | grep -v grep`
  prints nothing.
- **Long runs detached, never blocking a tool call:** launch with `setsid … &` (or the launcher,
  whose shards are already detached) and wait with one `run_in_background` Bash loop whose exit
  notifies (`until grep -q 'merge rc=' <merge-log>; do sleep 60; done`), not with fixed-interval
  polling. The Bash tool's own cap is 120 s by default, 600 s at most.
- **A killed or crashing maxima needs stdin from `/dev/null`:** a fatal SBCL error drops into
  `ldb`, which otherwise waits for input; every direct maxima/sbcl invocation in this plan uses
  `< /dev/null` (probe 09).
- **TLS:** no flag is required (`probes/matcher/08-runtime-load.out`); `test/build_rules_core.sh`
  and `test/corpus_driver.py` still pass it, harmlessly.
- **The human gate:** every PASS→FAIL of a final record is accepted by the user (spec §4 P5; per
  group, each group's entries listed in a committed summary file, any entry rejectable by id —
  deviation 8). No subagent and no controller ruling accepts one. Task 4 ends at a stop; Tasks 5–6
  start only after the user's acceptance is recorded in the ledger.
- **Git:** no `git add -A` (the tree carries untracked campaign logs and baselines); commit
  messages end with the executing session's `Claude-Session:` trailer and never
  `Co-Authored-By`; push only when asked (origin access is broken as of 2026-09-13); default
  branch `master`; work on `matcher-substrate`.
- **Test protocol:** every suite prints `PASS:`/`FAIL:` lines and ends with
  `Results: <n> passed, <m> failed`; a missing Results line is a failure.
- **Stop rules are stops:** where a step says *stop and report to the user*, the task ends there
  with its evidence committed; nothing downstream is started.

## File structure

| file | responsibility | task |
|---|---|---|
| `test/run_records.py` (create) | switch-arm helpers (`switch_settings`, `switches_text`, `record_switches`, `common_switches`), `clear_stale_shards` | 1; trimmed in 5 |
| `test/p5_gate.py` (create) | the P5 record gate (`gate`) and the per-switch winner rule (`winner`) | 1 |
| `test/test_run_records.py` (create) | guard for the two above and the driver's switch plumbing (23 checks) | 1; trimmed in 5 |
| `test/corpus_driver.py` (modify) | switch assignments and `switches:` header; entry subprocess stdin `/dev/null` | 1; switch parts removed in 5 |
| `test/launch_class_shards.py` (modify) | stale-shard cleanup before a launch; prints the arm | 1; arm print removed in 5 |
| `test/merge_class_shards.py`, `test/merge_timeout_rerun.py` (modify) | carry and check the arm | 1; removed in 5 |
| `test/matcher/test_mr_dispatch.mac` (modify) | switch-default check (57 → 58) | 1; switch checks rewritten in 5 |
| `probes/matcher/09-harness-fault-verdict.{sh,out}` (create) | the harness's verdict on a fatal SBCL error | 1 |
| `test/corpus_class{1,2,3}.p5-run{1,2,3,4[,5]}.out` (create) | the P5 records | 2, 3 |
| `test/corpus_class{1,2,3}.p5-final.timeout-rerun/` (create) | the 100 s re-checks of the final records | 4 |
| `probes/matcher/10-p5-attribution.py`, `10-p5-attribution.summary.py` and their outputs (create) | per-entry attribution runs and the grouped disposition table | 4 |
| `maxima_rubi_match.lisp`, `maxima_rubi_dispatch.lisp`, `maxima_rubi_utils.mac` (modify) | winners hard-wired; the three switches and the losing runtime paths deleted; `rubi_hybrid` deleted | 5 |
| `test_maxima_rubi.mac`, `test/matcher/test_mr_match.lisp` (modify) | switch checks rewritten to the hard-wired behaviour | 5 |
| `test/check_generated_rules.py` (modify) | `ENTRY_CALL` without the deleted entries | 5 |
| `test/corpus_class2.p6-noop.out` (create) | the hard-wired tree reproduces the final arm on class 2 | 5 |
| `probes/matcher/08-runtime-load.out` (regenerate) | TLS / load / Layer A on the final tree (§5 criterion 5) | 6 |
| `docs/matcher-substrate-migration.md` (create) | the acceptance record | 6 |
| `test/corpus_class{1,2,3}.out` (replace) | standing records = the final records | 6 |
| `AGENTS.md`, `README.md`, `docs/class-porting.md`, `generator/generate_rules.py` (comments), `todo/TODO.md`, `.superpowers/sdd/progress.md` (modify) | commands, counts, runbook, status, ledger | 1–6 |

## Task overview

| task | phase | deliverable | gate |
|---|---|---|---|
| 1 | P5 prep | run tooling (arm on every record, crash verdict, stale shards, gate script); probe 09; carried items in TODO | `test_run_records` 23/0; dispatch suite 58/0; Layer A 898/0; the existing Python guards green; probe 09 record as expected |
| 2 | P5 | run 1 (all defaults), classes 2 → 3 → 1 | three complete records; `p5_gate.py gate` wall ceiling PASS in every class (else stop) |
| 3 | P5 | runs 2–4 (one switch flipped each); three winners; run 5 when the winners differ from run 1 | nine (or twelve) complete records; three `WINNER` lines; the final records named |
| 4 | P5 gate | final-record gates; 100 s re-checks; probe 10 attribution; the final tree's suites; **stop for the user's acceptance** | `p5_gate.py gate` 4/0 in every class; every PASS→FAIL attributed (probe 10 summaries `0 failed`) and accepted by the user; suites green |
| 5 | P6 | winners hard-wired; switches, losing runtime paths, switch plumbing and `rubi_hybrid` deleted; class-2 no-op run | unit suites, Layer A 897, regression suite both arms, static gate, Python guards green; the no-op record matches the final class-2 record up to re-run noise |
| 6 | P6 | probe 08 on the final tree; acceptance record; AGENTS.md, README, runbook, generator comments, TODO, ledger; standing records | spec §5 criteria 1–6, each checked in Step 9 |

**Pre-validation (plan-writing session 2026-09-13, build `branch_5_50_base_84_g4204fb669` /
SBCL 2.6.7).** Expectations, not citations: Tasks 1–4 re-take and commit every figure.

- *Task 1*, in the throwaway worktree `.claude/worktrees/plan3-proto` (branch
  `plan3-prevalidation`, never merged) on `8764c2a`: `test_run_records` 23/0; the existing Python
  guards as in Task 1 Step 4 (radcan-fallback 3/1 also on untouched `master`); dispatch suite
  58/0; Layer A 898/0; probe 09's table as in Task 1 Step 6. The mergers, on the class-2 scout's
  22 shard files with an arm added to their `filter:` lines: `OK: 965/965 entries, 3 files, no
  dupes/missing/extra` / `switches: mr_flat_wide=false mr_cond_retry=true mr_model_flags=true`; with
  one shard on another arm: `INCOMPLETE … shards ran different switch arms …`, exit 1; the timeout
  merge refusing shards whose arm differs from the source record's; the launcher's dry run under
  `MR_SWITCHES="mr_flat_wide=true"` printing that arm.
- *Task 4*: the P0 core rebuilt from `0a6664c` in 15 s (`rules=3514
  fingerprint=5ef9b3bc5ee07ffac0e76f1fea54fbac`); probe 10 on the class-2 scout record (4
  workers, ~2 min): every PASS→FAIL attributed (Task 4 Step 4's expectation).
- *Task 5*: `p6/p6_hardwire.py --check` → `anchors ok: 8 combinations` on the Task 1 tree; the
  switch-plumbing patch applied after Task 1 + probe 10: `test_run_records` 15/0 and the other
  Python guards green. The Lisp/Maxima variant edits were not run (deviation 12).
- *Replay*: a fresh worktree at `8764c2a` plus only this plan's attachments, applied as Task 1
  Steps 1–3 and 6, Task 4 Step 4 and Task 5 Step 3 say — every file byte-identical to the
  prototype, and `--check` green on it.
- *Scouts* — P5 run 1 (the defaults) on the `master` tree before Task 1: no `switches:` line, the
  launcher's stdin `/dev/null`, core `6c396cf8be7a1fe5060d4d17bd37cc58`, one class at a time, the
  imaxima session idle. Merge times include the watcher's 120 s poll.

| class | launched → merged (UTC) | PASS (P0) | median s (P0) | p90 s (P0) | timeouts (P0) | `error` (P0) | PASS→FAIL / FAIL→PASS |
|---|---|---|---|---|---|---|---|
| 2 | 10:23:29 → 10:29:29 | 770 (614) | 0.60 (4.30) | 2.3 (8.1) | 20 (6) | 0 (1) | 24 / 180 |
| 3 | 10:36:02 → 10:58:02 | 2,288 (2,058) | 1.20 (3.90) | 6.5 (16.2) | 136 (201) | 7 (4) | 181 / 411 |
| 1 | 10:58:02 → 12:24:02 | 21,209 (20,125) | 0.40 (1.30) | 4.2 (7.0) | 1,207 (778) | 66 (23) | 1,826 / 2,910 |

Reading: every class clears the PASS floor and the wall ceiling by a wide margin, so the head
index (deviation 4) is not expected. The timeout class is where the cost went: class 1's grew
778 → 1,207 (700 entries `verified` at P0), and its run took 86 min against P0's ~80 despite the
lower median — a full three-class run is ~2 h. 1.2.1.3 e839 is not PASS→FAIL (deviation 7). The
PASS→FAIL volume Task 4 attributes and the user accepts is ~2,030 entries.

---

### Task 1: P5 run tooling — the arm on every record, the crash verdict, stale shards, the gate script

Branch: `matcher-substrate`. No corpus run is taken in this task.

**Files:**
- Create: `test/run_records.py`, `test/p5_gate.py`, `test/test_run_records.py` (attachments `tooling/`)
- Modify: `test/corpus_driver.py`, `test/launch_class_shards.py`, `test/merge_class_shards.py`,
  `test/merge_timeout_rerun.py`, `test/matcher/test_mr_dispatch.mac` (attachment
  `tooling/p5-tooling.patch`)
- Create: `probes/matcher/09-harness-fault-verdict.sh` (attachment `probes/`) and its `.out`
- Modify: `AGENTS.md` (§ Tests), `todo/TODO.md` (§ "Matcher substrate"),
  `.superpowers/sdd/progress.md` (a new Plan 3 section)

**Interfaces:**
- Consumes: `test/corpus_driver.py` — `build_text(f_text, var_text, e_text, e_text2=None)`,
  `core_header()`, `maxima_run(text, timeout)`, `file_list()`, `ROOT`; `test/ab_records.py` —
  `load_record(path) -> {(rel, entry): (class, seconds)}`, `compare(base, new, pass_classes)`,
  `driver_pass_classes()`; the dispatcher's defmvars `$mr_flat_wide` `nil`, `$mr_cond_retry` `t`,
  `$mr_model_flags` `t` (`maxima_rubi_dispatch.lisp`).
- Produces:
  - the environment contract `MR_SWITCHES="<switch>=true|false …"` (unset = the defaults);
  - `test/run_records.py`: `SWITCHES` (tuple, record order), `SWITCH_DEFAULTS` (dict of
    `"true"`/`"false"`), `switch_settings(env) -> dict` (ValueError on a malformed item),
    `switches_text(settings) -> "mr_flat_wide=<v> mr_cond_retry=<v> mr_model_flags=<v>"`,
    `record_switches(path) -> str | None`, `common_switches(paths) -> str` (ValueError: no arm
    / two arms / no paths), `clear_stale_shards(test_dir, slug) -> int` (RuntimeError while a pid
    of the previous run's pids file is alive);
  - `test/corpus_driver.py`: module attributes `run_records`, `SWITCH_SETTINGS`, `switch_header()`;
    every entry text starts with the three `<switch> : <value>$` lines; the `filter:` line carries
    `  switches: <switches_text>` before any `  core: pinned …`;
  - merged records: `filter: '<section>/'  full run  timeout: 30s  (<n> shards, merged here)  switches: <switches_text>`;
  - `test/p5_gate.py`: `gate P0 NEW` (checks `complete`, `switches`, `pass floor`,
    `wall ceiling`; `INFO:` lines; exit 1 on a FAIL), `winner SWITCH B1 B2 B3 F1 F2 F3` (prints
    `WINNER <switch>=<value> (<reason>); same as|differs from run 1 (<switch>=<v>)`),
    `winning_value(switch, base_value, flip_value, base_pass, flip_pass) -> (value, reason)`.

- [ ] **Step 1: Write the failing guard**

```bash
A=docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.files
cp $A/tooling/test_run_records.py test/
python3 test/test_run_records.py; echo "exit=$?"
```

Expected: a traceback ending `FileNotFoundError: [Errno 2] No such file or directory: '…/test/run_records.py'`,
no `Results:` line, `exit=1`.

The guard (23 checks, no Maxima) holds: the driver-side defaults equal the dispatcher's defmvars;
`switch_settings` defaults, one override and two malformed items; `record_switches` /
`common_switches` on one arm, a shard without an arm and two arms; `clear_stale_shards` removing
exactly the run's `.shardNN.{out,log,files}` and pids file and refusing while a pid is alive;
the driver (imported in a child with `MR_RULES_CORE=0`, so nothing is built) stating the arm on
its header and assigning the switches ahead of `mr_f` in the entry text, and exiting nonzero on
`MR_SWITCHES="mr_cond_retry=off"`; `gate` green, wall-ceiling FAIL and PASS-floor FAIL on
synthetic records, and its crash listing; `winning_value` on an every-class win for each arm, a
tie, a split, and the `mr_model_flags` split.

- [ ] **Step 2: Add the two modules**

```bash
cp $A/tooling/run_records.py $A/tooling/p5_gate.py test/
```

`test/run_records.py` is the shared helper (its docstring states the contract above).
`test/p5_gate.py`'s two commands implement deviations 3 and the spec's winner rule:

- `gate`: `complete` = the key sets of the two records are equal; `switches` = the new record's
  `filter:` line states an arm; `pass floor` = PASS(new) ≥ PASS(P0) with PASS read from the
  driver's `PASS_CLASSES`; `wall ceiling` = `statistics.median` of every `t=` in the new record ≤
  the same over the P0 record. `INFO:` lines: PASS→FAIL / FAIL→PASS counts, p90, the timeout class
  P0 → new with every entry `timeout` only in the new record, and the same for `error`.
- `winner`: both record triples must each state one arm and differ in exactly the named switch;
  the flipped arm wins only with more PASS in all three classes, run 1's arm wins only with more
  PASS in all three; otherwise `mr_flat_wide=false`, `mr_cond_retry=true`,
  `mr_model_flags=false` (spec §4 P5: "on a tie or a split across classes, the documented default
  wins (narrow, retry on) and for `mr_model_flags` Maxima defaults win").

- [ ] **Step 3: Apply the harness patch**

```bash
git apply $A/tooling/p5-tooling.patch
git diff --stat
```

Expected: exactly `test/corpus_driver.py`, `test/launch_class_shards.py`,
`test/matcher/test_mr_dispatch.mac`, `test/merge_class_shards.py`, `test/merge_timeout_rerun.py`
changed. What the patch does:

- `test/corpus_driver.py`: imports `test/run_records.py` (by path, as the driver is itself loaded
  by path from the launchers and probes), computes `SWITCH_SETTINGS` from the environment
  (a malformed `MR_SWITCHES` is a `SystemExit` naming it), adds `switch_header()`, prepends the
  three assignments to `build_text`'s head, appends `switch_header()` to the `filter:` line, and
  passes `stdin=subprocess.DEVNULL` to the entry subprocess (comment cites probe 07/09).
- `test/launch_class_shards.py`: prints `switches: <arm>` after the plan; with `--launch`, calls
  `clear_stale_shards(test/, <slug>)` first (a live pid is a `SystemExit`) and prints
  `removed <n> shard files of the previous run`.
- `test/merge_class_shards.py`: `common_switches(inputs)`; a `ValueError` joins the `INCOMPLETE`
  exit with a `  switches: <reason>` line; the merged `filter:` line and the `OK` report carry the
  arm.
- `test/merge_timeout_rerun.py`: the shards' common arm must equal the source record's arm when
  the source states one; the record's description line ends `switches: <arm>`.
- `test/matcher/test_mr_dispatch.mac`: in `test_records`, the check
  `switch defaults: mr_flat_wide false, mr_cond_retry true, mr_model_flags true`.

- [ ] **Step 4: Run the guards**

| command | expected |
|---|---|
| `python3 test/test_run_records.py \| tail -1` | `Results: 23 passed, 0 failed` |
| `python3 test/test_merge_classes.py \| tail -1` | `Results: 2 passed, 0 failed` |
| `python3 test/test_driver_core_pin.py \| tail -1` | `Results: 5 passed, 0 failed` |
| `python3 test/test_ab_records.py \| tail -1` | `Results: 6 passed, 0 failed` |
| `python3 test/test_record_medians.py \| tail -1` | `Results: 3 passed, 0 failed` |
| `python3 test/test_driver_parens.py \| tail -1` | `Results: 2 passed, 0 failed` |
| `python3 test/test_mr_sum_concrete.py \| tail -1` | `Results: 3 passed, 0 failed` |
| `python3 test/test_head_rewrites.py \| tail -1` | `Results: 20 passed, 0 failed` |
| `python3 test/test_driver_radcan_fallback.py < /dev/null \| tail -1` | `Results: 3 passed, 1 failed` — **pre-existing, not this task's gate**: red on `master` @ `8764c2a` before any Plan 3 change (measured while writing: its `[gate-blocks]` fixture entries 1.1.3.8 e541/e543/e544 classify `verified` on the substrate — all three on `master`, e543/e544 on the patched tree — so the elliptic-gate fixture no longer reaches the fallback); carried to TODO in Step 8 |
| `maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null \| grep -a '^Results'` | `Results:  58  passed,  0  failed` |
| `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null \| grep -a '^Results'` | `Results:  898  passed,  0  failed` |

The Maxima-using guards need a current rules core; if `test/mr_rules.core.stamp`'s fingerprint is
stale the driver rebuilds it (single-flight, ~3 s).

- [ ] **Step 5: Commit the tooling**

```bash
git add test/run_records.py test/p5_gate.py test/test_run_records.py test/corpus_driver.py \
        test/launch_class_shards.py test/merge_class_shards.py test/merge_timeout_rerun.py \
        test/matcher/test_mr_dispatch.mac
git commit -m "harness: P5 run tooling — switch arm on every record, entry stdin /dev/null, stale shards, gate script"
```

- [ ] **Step 6: Probe 09 — the harness's verdict on a fatal SBCL error**

```bash
cp $A/probes/09-harness-fault-verdict.sh probes/matcher/
```

Run with `run_in_background` (~1 min, 40 s of it an intended hang):
`sh probes/matcher/09-harness-fault-verdict.sh > probes/matcher/09-harness-fault-verdict.out 2>&1`

It runs probe 07's `matchq_cond_named` shape (a runaway recursion in a MatchQ condition) five
ways. Expected (pre-validation, 2026-09-13; walls vary):

| row | must hold |
|---|---|
| `A plain load, stdin /dev/null` | `rc=1`, `survived=0 fatal-pseudo=1 ldb=1`, wall under 5 s |
| `B plain load, stdin open pipe` | `rc=137` (killed at 40 s), `survived=0 fatal-pseudo=1 ldb=1` |
| `C rules core, stdin /dev/null` | `rc=0`, `survived=1 fatal-pseudo=0 ldb=0 guard-page=1` |
| `D driver, standard load, pipe` | `error t=… crash/c.mac e1` then `verified … e2` |
| `E driver, rules core, pipe` | `deferred t=… crash/c.mac e1` then `verified … e2` |

Before this task's patch row D read `timeout t=30.0s` (measured on the unpatched driver while
writing this plan). A different table is recorded as measured and reported at the task review:
deviation 2 cites it.

```bash
git add probes/matcher/09-harness-fault-verdict.sh probes/matcher/09-harness-fault-verdict.out
git commit -m "probe: matcher 09 — harness verdict on a fatal SBCL error (core survives; stdin decides ldb)"
```

- [ ] **Step 7: AGENTS.md — the Tests section**

Replace

```markdown
CRE input and the booleans) and `Results: 57 passed, 0 failed`
(dispatch: rule records, dispatcher outcomes, bindings / retry / head
symbols / CRE / G-6, the test entries, MatchQ; 45 at Plan 2's Task 4,
+4 at its review: the fault type excludes interrupts and timeouts, a
MatchQ pattern prepare rejects is an error, +8 at the final review:
MatchQ part folding and an out-of-range part error).
```

with

```markdown
CRE input and the booleans) and `Results: 58 passed, 0 failed`
(dispatch: rule records, dispatcher outcomes, bindings / retry / head
symbols / CRE / G-6, the test entries, MatchQ; 45 at Plan 2's Task 4,
+4 at its review: the fault type excludes interrupts and timeouts, a
MatchQ pattern prepare rejects is an error, +8 at the final review:
MatchQ part folding and an out-of-range part error, +1 at Plan 3: the
switch defaults).
```

Then insert, directly before the line that starts `**Record A/B** — the entry-level diff` (the
paragraph itself — an earlier line reads `**Record A/B** below).`):

````markdown
**Switch arm — matcher substrate P5** (Plan 3,
`docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.md`). The
three migration switches (`mr_flat_wide` false, `mr_cond_retry` true,
`mr_model_flags` true — the defaults in `maxima_rubi_dispatch.lisp`)
are set per run with `MR_SWITCHES` (space-separated
`<switch>=true|false`), e.g.
`MR_SWITCHES="mr_model_flags=false" python3 test/launch_class_shards.py …`.
The driver assigns them in every entry text and ends its `filter:`
line with `switches: …`; the mergers refuse shards that state no arm
or two arms. A launch first deletes the previous run's shard files and
refuses while one of its pids is alive. Entry subprocesses get stdin
`/dev/null` (`probes/matcher/09-harness-fault-verdict.out`: an
inherited open stdin held a fatal SBCL error in `ldb` until the cap).
The P5 gate and the winner rule:

```sh
python3 test/p5_gate.py gate <P0-record> <new-record>
python3 test/p5_gate.py winner <switch> <run-1 c1> <run-1 c2> <run-1 c3> <flip c1> <flip c2> <flip c3>
```

Guard (no Maxima): `python3 test/test_run_records.py` — green
`Results: 23 passed, 0 failed`.

````

- [ ] **Step 8: `todo/TODO.md` — carried items**

In § "Matcher substrate", replace the heading `## Matcher substrate — in prog (Plan 2 complete 2026-09-13)`
with `## Matcher substrate — in prog (Plan 3 executing)`, and replace the bullet that starts
`- Carried into Plan 3:` (through its `— open`) with:

```markdown
- Plan 3 (P5–P6,
  `docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.md`),
  Task 1: the switch arm written into every record's `filter:` line
  (`MR_SWITCHES`, `test/run_records.py`); the launcher deletes a
  previous run's shard files; the speed-gate definition and the
  crash-class counts (`test/p5_gate.py`); the crash verdict's stdin
  (`probes/matcher/09-harness-fault-verdict.out`) — done
- Carried into Plan 3's P5 runs: class 2 first in every run, its
  median wall and timeout class compared against P0 before class 1
  (probe 06: the full-table walk is exponential in Times arity); when
  attributing the `mr_model_flags` arm, nested integrate fall-throughs
  (depth cap, seen guard) run under the flags — look at the seen-guard
  path first; the MODEL-LOST figures (1,166 / 395 measured vs the
  spec's 1,142 / 312) explained only if that arm's attribution needs
  them; the spec §6 TLS-mechanism wording corrected in the P6
  acceptance record; P6: stale generator comments (`cap_name`
  docstring, `CAP_REMAP` rationale, ctx `decls`) and README.md's
  `defmatch` TLS text and deleted-file list — open
- Carried (plan-2 final review, parked): numeric folding in MatchQ
  part substitution (`Times[0,p]` → 0, `Power[1,e]` → 1, a Times/Plus
  left holding only Optionals → the Optional's default — `a_.*v_^0`
  currently errors instead of matching; unreachable today, 1_4_1
  r4/r68 guard `expon > 1`); a parts-keyed compiled-pattern cache for
  MatchQ calls with parts (hot conds; unmeasured — built only if a P5
  wall gate asks for it) — open
```

- [ ] **Step 9: The ledger**

Append to `.superpowers/sdd/progress.md` (every `<…>` a value copied from the run named — no
figure retyped from this plan):

```markdown
## Plan: 2026-09-13 matcher substrate plan 3 (P5–P6; branch matcher-substrate)

Spec: docs/superpowers/specs/2026-09-12-matcher-substrate-design.md
Plan: docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.md (+ .files/ attachments)

### Task 1 — P5 run tooling
- build: <build_info() version / timestamp> / SBCL 2.6.7
- red: <the last traceback line of Step 1>
- green: <every expected-column result of Step 4, in table order>
- probe 09 (probes/matcher/09-harness-fault-verdict.out, <its === line>): <rows A–E verbatim>
```

```bash
git add AGENTS.md todo/TODO.md .superpowers/sdd/progress.md
git commit -m "docs: P5 run tooling — AGENTS switch-arm paragraph and dispatch 58, TODO carried items, ledger plan 3"
```

### Task 2: P5 run 1 — all defaults, classes 2 → 3 → 1

Branch: `matcher-substrate`. Measurement only: no source file changes in this task.

**Files:**
- Create: `test/corpus_class2.p5-run1.out`, `test/corpus_class3.p5-run1.out`,
  `test/corpus_class1.p5-run1.out` (merged records)
- Modify: `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: Task 1's launcher / mergers / `test/p5_gate.py`; the P0 records
  `test/corpus_class{1,2,3}.pre-matcher.out` (PASS 20,125 / 614 / 2,058; median 1.3 / 4.3 / 3.9 s;
  timeouts 778 / 6 / 201; `error` 23 / 1 / 4).
- Produces: the run-1 records (`switches: mr_flat_wide=false mr_cond_retry=true mr_model_flags=true`),
  the base triple of Task 3's winner rule, and — when the winners equal run 1 — the final records.

The run procedure (this task and Task 3 repeat it with another `MR_SWITCHES` and run number):

```bash
# RUN=<k>  ARM="<MR_SWITCHES value, empty for the defaults>"
# C=<1|2|3>  SECTION="<1 Algebraic functions|2 Exponentials|3 Logarithms>"
# DRIVER=<test/corpus_class1_driver.py for class 1, test/corpus_driver.py otherwise>
ps -eo args | grep -E '^python3 .*(corpus_driver|corpus_class1_driver)\.py' | grep -v grep   # must print nothing
MR_SWITCHES="$ARM" python3 test/launch_class_shards.py "$SECTION" test/corpus_class$C.pre-matcher.out $DRIVER --launch < /dev/null
setsid sh test/wait_and_merge.sh test/corpus_class$C.shard-pids test/merge_class_shards.py \
    test/class${C}_merge.p5-run$RUN.log "$SECTION" test/corpus_class$C.p5-run$RUN.out $DRIVER \
    "corpus_class$C.shard*.out" < /dev/null > /dev/null 2>&1 &
```

then one `run_in_background` waiter:
`until grep -q 'merge rc=' test/class${C}_merge.p5-run$RUN.log 2>/dev/null; do sleep 60; done; cat test/class${C}_merge.p5-run$RUN.log`.

A class's run is read only when the waiter's output shows all of: `OK: <N>/<N> entries, … no
dupes/missing/extra` (N = 965 / 3,085 / 25,697), `switches: <the intended arm>`, `merge rc=0`, and
the launcher's own output showed `switches: <the intended arm>` and
`removed <n> shard files of the previous run`. A launcher refusal naming a pid that is not a
corpus driver (`ps -p <pid> -o args=`) is a stale pids file from a finished run whose pid was
reused: delete `test/corpus_class$C.shard-pids` and launch again. An `INCOMPLETE` merge is a
harness failure: report it, do not re-merge by hand. The merge logs (`test/class<N>_merge.p5-run<k>.log`) are gitignored working files
(`/test/class*_merge.*`).

- [ ] **Step 1: Preconditions**

```bash
git status --porcelain -- '*.py' '*.lisp' '*.mac' '*.sh' | grep -v '^??'   # must print nothing
sh test/build_rules_core.sh                                                 # a current core
head -1 test/mr_rules.core.stamp
```

Record the fingerprint line in the ledger: every Task 2–4 run uses this core, and Task 4's probe
10 checks it against its own header.

- [ ] **Step 2: Class 2** — the procedure with `RUN=1 ARM="" C=2 SECTION="2 Exponentials"
  DRIVER=test/corpus_driver.py` (~6 min wall).

Then: `python3 test/p5_gate.py gate test/corpus_class2.pre-matcher.out test/corpus_class2.p5-run1.out`

- `FAIL: wall ceiling …` → **stop and report to the user** (deviation 4: the head-index plan).
- `FAIL: complete` or `FAIL: switches` → a harness failure: stop and report.
- `FAIL: pass floor` → record it and continue: Task 3's arms may win it back; Task 4 judges the
  final records.

Scout expectation (the `master` tree before Task 1, same core, 2026-09-13 — not a gate): PASS 770,
median 0.60 s, p90 2.3 s, timeouts 6 → 20 (18 new, all in 2.3), `error` 1 → 0, PASS→FAIL 24 /
FAIL→PASS 180.

- [ ] **Step 3: Class 3** — `RUN=1 ARM="" C=3 SECTION="3 Logarithms" DRIVER=test/corpus_driver.py`,
  then `p5_gate.py gate test/corpus_class3.pre-matcher.out test/corpus_class3.p5-run1.out`, read
  as in Step 2.

Scout expectation (the `master` tree before Task 1, same core, 2026-09-13 — not a gate): PASS
2,288, median 1.20 s, p90 6.5 s, timeouts 201 → 136 (57 new), `error` 4 → 7 (all seven new:
3.1.5 e120/e121, 3.2.2 e260, 3.2.3 e77/e81, 3.4 e356, 3.5 e172 — subprocess deaths after 20–30 s,
not probe 07's shape, which the core survives), PASS→FAIL 181 / FAIL→PASS 411; merged 22 min after
the launch.

- [ ] **Step 4: Class 1** — `RUN=1 ARM="" C=1 SECTION="1 Algebraic functions"
  DRIVER=test/corpus_class1_driver.py` (~80 min wall on 24 shards at P0), then
  `p5_gate.py gate test/corpus_class1.pre-matcher.out test/corpus_class1.p5-run1.out`, read as in
  Step 2.

Scout expectation (the `master` tree before Task 1, same core, 2026-09-13 — not a gate): PASS
21,209, median 0.40 s, p90 4.2 s, timeouts 778 → 1,207 (931 new; 700 of them `verified` at P0),
`error` 23 → 66 (63 new, most in 1.1.3.2, dying after 6–29 s), PASS→FAIL 1,826 / FAIL→PASS 2,910;
merged 86 min after the launch (the timeout tail).

- [ ] **Step 5: Commit the records**

```bash
git add test/corpus_class2.p5-run1.out test/corpus_class3.p5-run1.out test/corpus_class1.p5-run1.out
git commit -m "record: P5 run 1 (all switch defaults) — classes 1-3"
```

- [ ] **Step 6: The ledger**

Append to the Plan 3 section:

```markdown
### Task 2 — P5 run 1 (defaults)
- core: <the fingerprint line of Step 1>
- class 2: <the merge log's OK and switches lines; merge rc>; gate: <every PASS:/FAIL:/INFO: line of p5_gate.py gate up to the first INFO: timeout entry list, and its Results line>
- class 3: <same>
- class 1: <same>
```

### Task 3: P5 runs 2–4 — one switch flipped per run; the winners; run 5 when they differ

Branch: `matcher-substrate`. Measurement only.

**Files:**
- Create: `test/corpus_class{2,3,1}.p5-run{2,3,4}.out`; when the winners differ from run 1, also
  `test/corpus_class{2,3,1}.p5-run5.out`
- Modify: `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: Task 2's run procedure and run-1 records; `p5_gate.py winner`.
- Produces: the three winners (ledger `WINNER` lines), the final arm `FINAL_ARM` (a
  `MR_SWITCHES` value) and the final records `test/corpus_class{1,2,3}.<final>.out` where
  `<final>` is `p5-run1` or `p5-run5` — Tasks 4–6 read both from the ledger.

| run | `ARM` (`MR_SWITCHES`) | flips |
|---|---|---|
| 2 | `mr_flat_wide=true` | G-6 wide run-grouping |
| 3 | `mr_cond_retry=false` | first complete binding only |
| 4 | `mr_model_flags=false` | Maxima's simplifier defaults inside `mr_top` |

Every run takes all three classes (spec §4 P5 "four full class 1–3 runs"; user decision
2026-09-13: no early stop, so the acceptance record has every arm-vs-arm table). On the scouts a
full run is ~2 h (class 2 ~6 min, class 3 ~22 min, class 1 ~86 min); a flipped arm may be slower.

- [ ] **Step 1: Run 2** — the Task 2 procedure with `RUN=2 ARM="mr_flat_wide=true"`, classes 2, 3,
  1 in that order; after each class `p5_gate.py gate <P0 record> <run-2 record>` (recorded; a
  wall-ceiling FAIL here is not a stop — a flipped arm's walls are judged only if it wins, in
  Task 4).
- [ ] **Step 2: Run 3** — the same with `RUN=3 ARM="mr_cond_retry=false"`.
- [ ] **Step 3: Run 4** — the same with `RUN=4 ARM="mr_model_flags=false"`.
- [ ] **Step 4: Commit runs 2–4**

```bash
git add test/corpus_class[123].p5-run[234].out
git commit -m "record: P5 runs 2-4 (mr_flat_wide, mr_cond_retry, mr_model_flags flipped) — classes 1-3"
```

- [ ] **Step 5: The winners**

```bash
R() { echo test/corpus_class1.p5-run$1.out test/corpus_class2.p5-run$1.out test/corpus_class3.p5-run$1.out; }
python3 test/p5_gate.py winner mr_flat_wide   $(R 1) $(R 2)
python3 test/p5_gate.py winner mr_cond_retry  $(R 1) $(R 3)
python3 test/p5_gate.py winner mr_model_flags $(R 1) $(R 4)
```

Each prints three PASS lines and one `WINNER <switch>=<value> (<reason>); same as|differs from run
1 (…)` line. `FINAL_ARM` is the space-separated list of the three winning `<switch>=<value>` items
that differ from the defaults (empty when all three read `same as`).

- [ ] **Step 6: Run 5 (only when `FINAL_ARM` is not empty)** — the Task 2 procedure with `RUN=5
  ARM="$FINAL_ARM"`, classes 2, 3, 1, each followed by `p5_gate.py gate`; a wall-ceiling FAIL is
  a **stop and report** (it is now a final record); then

```bash
git add test/corpus_class[123].p5-run5.out
git commit -m "record: P5 run 5 (the winning arm: $FINAL_ARM) — classes 1-3"
```

When `FINAL_ARM` is empty the final records are the run-1 records and no run 5 is taken.

- [ ] **Step 7: The arms' A/B tables** (no Maxima)

```bash
for k in 2 3 4; do for c in 2 3 1; do
  echo "== run 1 -> run $k, class $c"
  python3 test/ab_records.py test/corpus_class$c.p5-run1.out test/corpus_class$c.p5-run$k.out | sed -n '/PASS\/FAIL table/,/per file/p'
done; done
```

- [ ] **Step 8: The `mr_model_flags` reading**

From run 1 → run 4 (Step 7): if `mr_model_flags=false` won and a run-1 PASS became a run-4 FAIL in
any class, list those entries in the ledger with their class transitions; look at the seen-guard
path first when explaining them (nested `integrate` fall-throughs run under the flags in run 1 —
TODO carried item). The MODEL-LOST figures (deviation 6) are investigated only if this list's
explanation turns on a stored-shape difference; if it does, **stop and report to the user** with
the entries — the investigation is then scoped with them.

- [ ] **Step 9: The ledger**

```markdown
### Task 3 — P5 runs 2–4 (+5)
- run 2 (mr_flat_wide=true): per class <merge OK + switches lines; the p5_gate.py gate PASS:/FAIL: lines and Results>
- run 3 (mr_cond_retry=false): <same>
- run 4 (mr_model_flags=false): <same>
- winners: <the three WINNER lines verbatim>
- FINAL_ARM: "<value>"; final records: test/corpus_class{1,2,3}.<p5-run1|p5-run5>.out
- run 5: <per class, as above — or "not taken (FINAL_ARM empty)">
- arm A/B (run 1 -> run k): <the twelve PASS/FAIL tables, one line each: k, class, PASS->PASS, PASS->FAIL, FAIL->PASS, FAIL->FAIL>
- mr_model_flags reading: <Step 8's list, or "run 4 has no run-1 PASS->FAIL" / "mr_model_flags=true won">
```

```bash
git add .superpowers/sdd/progress.md
git commit -m "docs: ledger — P5 runs 2-4, winners, final arm"
```

### Task 4: P5 gate — the final records, the 100 s re-checks, attribution, the final tree; the user's acceptance

Branch: `matcher-substrate`. No source file changes. This task ends at a **stop**: the user
accepts (or rejects) every PASS→FAIL before Task 5 starts.

**Files:**
- Create: `probes/matcher/10-p5-attribution.py`, `probes/matcher/10-p5-attribution.summary.py`
  (attachments `probes/`) and their outputs `probes/matcher/10-p5-attribution.class<N>-{final30,p0,final120}.out`,
  `probes/matcher/10-p5-attribution.class<N>.summary.out` (N = 1, 2, 3)
- Create: `test/corpus_class<N>.p5-final.timeout-rerun/` (the launcher's `source`, `pids`, shard
  files, `wait.log`, `merge.out`, and the record `corpus_class<N>.<final>.timeout100s.out`)
- Regenerate: `test/matcher/{roundtrip,controls,spike01,gate}.out`, `test/matcher/{roundtrip,gate}.flags.out`
- Modify: `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: from the Task 3 ledger, `FINAL_ARM` and the final records `$F1 $F2 $F3`
  (`test/corpus_class<N>.<p5-run1|p5-run5>.out`); the P0 records; `test/p5_gate.py gate`;
  `test/launch_timeout_rerun.py` / `test/wait_timeout_rerun.sh` / `test/merge_timeout_rerun.py`
  (Task 1: the shards must run the source record's arm); the P0 commit `0a6664c`.
- Produces: the P5 gate evidence (spec §4 P5, §5 criterion 2); one summary table per class (the
  dispositions and groups of deviation 8, with a mechanism line per group); the user's per-entry
  acceptance in the ledger; the `rubi_hybrid` verdict (deviation 7) Task 5 reads.

Throughout: `export FINAL_ARM="<value from the ledger>"` and `F1 F2 F3` set to the final record
paths; every run in this task uses the Task 2 core (check `head -1 test/mr_rules.core.stamp`
against the Task 2 ledger line before each launch).

- [ ] **Step 1: The final-record gates**

```bash
python3 test/p5_gate.py gate test/corpus_class2.pre-matcher.out $F2
python3 test/p5_gate.py gate test/corpus_class3.pre-matcher.out $F3
python3 test/p5_gate.py gate test/corpus_class1.pre-matcher.out $F1
```

Each must end `Results: 4 passed, 0 failed` and its `switches:` line must equal the final arm
(the defaults plus `FINAL_ARM`). A `FAIL: pass floor` or `FAIL: wall ceiling` on a final record
is a spec §4 P5 gate failure: **stop and report to the user** (for the wall ceiling, deviation 4).

- [ ] **Step 2: The `rubi_hybrid` check (deviation 7)**

```bash
python3 test/ab_records.py test/corpus_class1.pre-matcher.out $F1 | sed -n '/^=== PASS->FAIL/,$p' \
  | grep -c '/1\.2\.1\.3 [^/]*\.mac e839$'
```

`0` → `rubi_hybrid` / `rubi_hybrid_exact` are deleted in Task 5. `1` → **stop and report to the
user** (the exact seen comparison as a translation fix is a design change outside this plan).
In the P0 record 1.2.1.3 e839 is `verified` (3.7 s), so the check is live.

- [ ] **Step 3: The 100 s timeout re-checks** (classes 2, 3, 1; one at a time; each detached)

```bash
# C=<N>  SECTION="<section>"  F=<the class's final record>
ps -eo args | grep -E '^python3 .*(corpus_driver|corpus_class1_driver)\.py' | grep -v grep   # nothing
D=test/corpus_class$C.p5-final.timeout-rerun
MR_SWITCHES="$FINAL_ARM" python3 test/launch_timeout_rerun.py $F 100 $D "$SECTION" --launch < /dev/null
setsid sh test/wait_timeout_rerun.sh $D >> $D/wait.log 2>&1 < /dev/null &
```

Waiter (`run_in_background`): `until grep -q 'merge rc=' $D/merge.out 2>/dev/null; do sleep 60; done; head -20 $D/merge.out`.

Must hold per class: `OK: <n>/<n> re-checked, no dupes/missing/extra` with n = the final record's
timeout count (`p5_gate.py gate`'s `INFO: timeout … -> new <n>`), `merge rc=0`, and the record's
description line ending `switches: <the final arm>`. The re-check of class 1 re-runs ~1,200 entries
(the scout's timeout count) at up to 100 s on 24 processes: ~1.5 h.

- [ ] **Step 4: The P0 core and probe 10**

```bash
A=docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.files
git worktree add --detach "${TMPDIR:-/tmp}/mr-p0-tree" 0a6664c
(cd "${TMPDIR:-/tmp}/mr-p0-tree" && sh test/build_rules_core.sh)
cp $A/probes/10-p5-attribution.py $A/probes/10-p5-attribution.summary.py probes/matcher/
```

Expected build line: `built test/mr_rules.core (172622464 bytes) rules=3514
fingerprint=5ef9b3bc5ee07ffac0e76f1fea54fbac` (the P0 records' core; measured while writing,
15 s).

Probe 10 (deviation 8) re-runs each selected entry through the driver's exact entry text with
`rubi_verbose` fire traces, on the tree's core or the core `MR_RULES_CORE_PATH` pins, with `WORKERS`
concurrent subprocesses; the summary joins the records and the runs into dispositions. Per class
(2, 3, 1), with nothing else running, each command detached through one `run_in_background` call
that runs the four in sequence:

```bash
P=probes/matcher/10-p5-attribution; P0R=test/corpus_class$C.pre-matcher.out
P0CORE="${TMPDIR:-/tmp}/mr-p0-tree/test/mr_rules.core"
REC=test/corpus_class$C.p5-final.timeout-rerun/$(basename $F .out).timeout100s.out
MR_SWITCHES="$FINAL_ARM" python3 $P.py "$SECTION" $P0R $F passfail $P.class$C-final30.out 30 24
MR_SWITCHES="$FINAL_ARM" MR_RULES_CORE_PATH=$P0CORE python3 $P.py "$SECTION" $P0R $F passfail $P.class$C-p0.out 30 24
MR_SWITCHES="$FINAL_ARM" python3 $P.py "$SECTION" $P0R $F passfail-timeout $P.class$C-final120.out 120 24
python3 $P.summary.py $P0R $F --final30 $P.class$C-final30.out --p0 $P.class$C-p0.out \
    --final120 $P.class$C-final120.out --recheck $REC > $P.class$C.summary.out
tail -1 $P.class$C.summary.out
```

(The P0 core ignores the three switch assignments: they set globals it never reads.) Each probe run
ends with its own `Results:` line (the count of PASS classes among the re-run entries — a record,
not a gate); the summary must end `Results: <n> passed, 0 failed` with n = the class's PASS→FAIL
count. When `p5_gate.py gate` listed `error in new only: <k>` with k > 0, also run
`MR_SWITCHES="$FINAL_ARM" python3 $P.py "$SECTION" $P0R $F newerror $P.class$C-newerror.out 30 24`.

Scout expectation for class 2 (probe 10 on the class-2 scout record, 4 workers, 2026-09-13):
`PASS->FAIL 24: deterministic 22, slow-correct 2, near-cap 0, noise 0, p0-noise 0, unmeasured 0`
in 12 groups — the largest: 5 × `deferred top=2_3_r34` (2.3 e202/e247/e248/e391/e392: the P0
route fired `2_3_r15` / `1_4_1_r29` / `1_4_1_r7` before `2_3_r34`; on the substrate `2_3_r34`
answers first with a noun), 4 × `contains-noun top=2_2_r2` (2.2 e86/e87/e92/e93, P0 `2_3_r70`),
3 × `deferred top=-` (no rule answers at the top level); the 2 slow-correct entries (2.3 e283,
e342) verify in ~60 s at 120 s.

- [ ] **Step 5: The mechanism lines**

For every `GROUP` of every class summary, write one ledger line: the group id, its entries, and
the mechanism read from the fire traces — which rule answers on the final core against the P0
route, and what the answer is (e.g. "`2_3_r34` now binds ahead of `2_3_r15`; its answer is the
no-answer noun", "`unexpected` with `self=1`: a correct antiderivative on a noun-expected entry —
a yardstick reclassification"). Every deterministic group also names the substrate change it
follows from where the traces show it (faithful Optional / Flat+Orderless binding, a moved inner
condition, condition retry, the model flags, the seen guard). For the `NEW TIMEOUTS` block, one
line per class with the 100 s transition counts; for new `error` entries, their probe-10 rows.

- [ ] **Step 6: The final tree's suites** (nothing else running)

| command | expected |
|---|---|
| `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null \| grep -a '^Results'` | `Results:  898  passed,  0  failed` |
| `maxima --very-quiet -b test/matcher/test_mr_match.mac < /dev/null \| grep -a '^Results'` | `Results: 53 passed, 0 failed` |
| `maxima --very-quiet -b test/matcher/test_mr_tree.mac < /dev/null \| grep -a '^Results'` | `Results: 51 passed, 0 failed` |
| `maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null \| grep -a '^Results'` | `Results:  58  passed,  0  failed` |
| `python3 test/check_generated_rules.py \| tail -1` | `Results: 11 passed, 0 failed` |
| `python3 test/test_run_records.py \| tail -1` | `Results: 23 passed, 0 failed` |

Then the matcher regression suite, the two arms one after the other, each with `run_in_background`
(~70 s wall):

```bash
MR_LEGS=tree,maxima MR_SPIKE=1 sh test/matcher/run.sh > "${TMPDIR:-/tmp}/p3t4-defaults.log" 2>&1
MR_LEGS=tree,maxima MR_MODEL_FLAGS=1 MR_SPIKE=1 sh test/matcher/run.sh > "${TMPDIR:-/tmp}/p3t4-flags.log" 2>&1
grep -a 'Results' "${TMPDIR:-/tmp}/p3t4-defaults.log" "${TMPDIR:-/tmp}/p3t4-flags.log"
for f in roundtrip.out roundtrip.flags.out controls.out spike01.out gate.out gate.flags.out; do
  printf '%s ' $f; git diff test/matcher/$f | grep '^[-+]' | grep -v '^[-+][-+]' \
    | grep -v -i 'judged\|git HEAD\|TIMING\|build\|shard0.log\|run:' | wc -l; done
```

Expected: `Results: 109 passed, 0 failed` twice, then `0` after every file name.

- [ ] **Step 7: Commit the evidence**

```bash
git add probes/matcher/10-p5-attribution.py probes/matcher/10-p5-attribution.summary.py \
        probes/matcher/10-p5-attribution.class[123]-*.out probes/matcher/10-p5-attribution.class[123].summary.out \
        test/corpus_class[123].p5-final.timeout-rerun/*.timeout100s.out \
        test/corpus_class[123].p5-final.timeout-rerun/merge.out \
        test/matcher/roundtrip.out test/matcher/roundtrip.flags.out test/matcher/controls.out \
        test/matcher/spike01.out test/matcher/gate.out test/matcher/gate.flags.out
git commit -m "probe: matcher 10 — P5 final-record attribution; 100 s re-checks; final-tree regression suite"
```

Remove the P0 worktree: `git worktree remove --force "${TMPDIR:-/tmp}/mr-p0-tree"`.

- [ ] **Step 8: The ledger**

```markdown
### Task 4 — P5 gate
- final arm: <FINAL_ARM>; final records: <F1 F2 F3>
- gates: <the three p5_gate.py gate outputs' PASS:/FAIL: lines, INFO: count lines and Results lines>
- rubi_hybrid (1.2.1.3 e839 PASS->FAIL count): <Step 2's number>
- 100 s re-checks: <per class, merge.out's OK line and the transitions block>
- attribution: <per class, the summary's PASS->FAIL totals line and Results line>
- mechanisms: <Step 5's lines>
- final tree: <Step 6's eight Results lines and the six diff counts>
```

```bash
git add .superpowers/sdd/progress.md
git commit -m "docs: ledger — P5 final-record gates, re-checks, attribution"
```

- [ ] **Step 9: Stop — the user's acceptance**

The executing session presents to the user, class by class: the gate lines; the summary's totals;
then every `GROUP` once — its id, disposition, size, mechanism line and two or three sample entries
(record transition, P0-core and final-core classes and top rules) — with the path of the committed
summary file that lists all its entries; then the new timeouts (count and 100 s transition counts
per class; the entries are in the summary's `NEW TIMEOUTS` block) and the new `error` entries. The
user accepts or rejects per group and may reject individual entries by id (`<file> e<n>`);
accepting a group accepts each entry the summary lists in it (user decision 2026-09-13). Record
the answer verbatim in the ledger:

```markdown
### Task 4 — user acceptance (<date>)
- class <N> <group id> (<size> entries): accepted | accepted except <entries> | rejected
- new timeouts: accepted | rejected: <entries>
```

Every PASS→FAIL accepted → Task 5. Any rejection → **stop**: the rejected entries are the input of
a fix plan written then; Tasks 5–6 wait for it.

### Task 5: P6 — the winners hard-wired; the switches, the losing runtime paths, the switch plumbing and `rubi_hybrid` deleted

Branch: `matcher-substrate`. **Starts only when** the ledger's `### Task 4 — user acceptance`
block accepts every PASS→FAIL and `rubi_hybrid (1.2.1.3 e839 PASS->FAIL count): 0`.

**Files:**
- Modify (by the attachment script `p6/p6_hardwire.py`): `maxima_rubi_match.lisp`,
  `maxima_rubi_dispatch.lisp`, `maxima_rubi_utils.mac`, `test/check_generated_rules.py`,
  `test/matcher/test_mr_match.lisp`, `test/matcher/test_mr_dispatch.mac`, `test_maxima_rubi.mac`
- Modify (by the attachment patch `tooling/p6-switch-plumbing.patch`): `test/run_records.py`,
  `test/test_run_records.py`, `test/corpus_driver.py`, `test/launch_class_shards.py`,
  `test/merge_class_shards.py`, `test/merge_timeout_rerun.py`, `probes/matcher/10-p5-attribution.py`
- Create: `test/corpus_class2.p6-noop.out`
- Modify: `.superpowers/sdd/progress.md`

**Interfaces:**
- Consumes: the three `WINNER` lines (Task 3 ledger) → `W_FLAT`, `W_RETRY`, `W_FLAGS`
  (`true`/`false`); the final class-2 record `$F2`.
- Produces:
  - `mr-match:match (compiled expr &key bindings cond-hook)` — plus `(retry t)` when
    `W_RETRY=false`, the dispatcher passing `:retry nil`; `mr-match:*cond-retry*` gone;
    `mr-match:*flat-wide*` kept, default `W_FLAT`, bound only by the regression suite;
  - no Maxima variable `mr_flat_wide`, `mr_cond_retry`, `mr_model_flags`; no `with-mr-switches`;
    `mr_top` hard-wired to `W_FLAGS`; no `rubi_hybrid`, `rubi_hybrid_exact`, `%mr_hybrid_body`;
  - counts Task 6 documents: `test_mr_match` 53 (`W_RETRY=true`) or 54 (`W_RETRY=false`);
    `test_mr_dispatch` 56; Layer A 897; `test_run_records` 15; regression suite 109;
  - the driver without switch plumbing (entry stdin `/dev/null` and the launcher's stale-shard
    cleanup stay); `test/run_records.py` keeps `SWITCHES`, `record_switches`,
    `clear_stale_shards`.

What `p6/p6_hardwire.py` does (its docstring is the reference; every edit is an exact replacement
that must match once, computed on in-memory copies before anything is written):

| file | edit | by winner |
|---|---|---|
| `maxima_rubi_match.lisp` | `*cond-retry*` out of the export list and deleted; `*flat-wide*`'s docstring states it is the suite's knob | `W_FLAT`: its default `nil` / `t`. `W_RETRY=true`: `match` drops the first-binding path; `false`: `match` takes `(retry t)` and tests `(not retry)` |
| `maxima_rubi_dispatch.lisp` | the three `defmvar`s and their comment block deleted; `with-mr-switches` deleted and its four call sites unwrapped; MatchQ's `let` binding the two specials removed; the docstrings naming `mr_cond_retry` rewritten | `W_RETRY=false`: `mr-accept`'s `match` call gets `:retry nil` |
| `maxima_rubi_utils.mac` | `mr_top`'s dispatch hard-wired; the block from `/* The legacy 9.1 re-dispatch entry.` through `rubi_hybrid_exact(f, x) := …$` deleted | `W_FLAGS=true`: `block([radexpand : false, logexpand : false], %mr_dispatch_tree(…))`; `false`: the bare `%mr_dispatch_tree(…)` |
| `test/check_generated_rules.py` | `ENTRY_CALL` without `rubi_hybrid|rubi_hybrid_exact` | — |
| `test/matcher/test_mr_dispatch.mac` | the switch-defaults check becomes `the migration switches are gone` (`[?boundp('mr_flat_wide), ?boundp('mr_cond_retry), ?boundp('mr_model_flags)]` = `[false, false, false]`); each switch-flipping pair becomes one check of the winner; the MatchQ retry check loses its assignments | the winner's check of each pair |
| `test/matcher/test_mr_match.lisp` | a check that `*flat-wide*` defaults to the winner | `W_FLAT=true`: the narrow check binds `*flat-wide*` to `nil`; `W_RETRY=true`: the no-retry check deleted; `false`: it passes `:retry nil` and the helper `m` gains `(retry t)` |
| `test_maxima_rubi.mac` | the `mr_model_flags` pair becomes one check of the winner and the restore check | `W_FLAGS=true`: `"false false"`; `false`: `"true true"` |

- [ ] **Step 1: The winners**

```bash
A=docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.files
grep -a '^- winners:' -A3 .superpowers/sdd/progress.md
grep -a 'user acceptance' -A12 .superpowers/sdd/progress.md
# from the three WINNER lines:
W_FLAT=<false|true>; W_RETRY=<true|false>; W_FLAGS=<true|false>
python3 $A/p6/p6_hardwire.py --check
```

Expected: `anchors ok: 8 combinations` (measured on the Task 1 tree while writing this plan). A
mismatch means a file changed since: stop and report.

- [ ] **Step 2: The failing checks**

```bash
python3 $A/p6/p6_hardwire.py --flat-wide $W_FLAT --cond-retry $W_RETRY --model-flags $W_FLAGS --tests-only
maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null | grep -a '^ *FAIL:  \|^Results'
maxima --very-quiet -b test/matcher/test_mr_match.mac < /dev/null | grep -a '^ *FAIL:\|^Results\|error'
maxima --very-quiet -b test_maxima_rubi.mac < /dev/null | grep -a '^ *FAIL:  \|^Results'
```

Expected red, whatever the winners: the dispatch suite prints
`FAIL:  the migration switches are gone (spec 3.6, hard-wired at P6)` and ends
`Results:  <55 or fewer>  passed,  <1 or more>  failed` (56 checks). By winner, also:
`W_RETRY=false` → `FAIL:  first binding only (the P5 winner): …` (dispatch) and the match suite
stops with a Lisp error naming `:RETRY` and no `Results:` line; `W_FLAT=true` →
`FAIL:  G-6 wide (the P5 winner): …` (dispatch) and `FAIL: *flat-wide* defaults to the wide
reading (the P5 winner)` (match); `W_FLAGS=false` → `FAIL:  Maxima defaults inside the dispatch
(the P5 winner)` (Layer A). Checks of the default arm that already hold are locks, not red.

- [ ] **Step 3: The code**

```bash
python3 $A/p6/p6_hardwire.py --flat-wide $W_FLAT --cond-retry $W_RETRY --model-flags $W_FLAGS --code-only
git apply $A/tooling/p6-switch-plumbing.patch
git diff --stat
```

Expected `git diff --stat`: the seven script files and the seven patch files (14).

The patch (replayed from `8764c2a` + Task 1 + probe 10 while writing: byte-identical to the
prototype) removes from the driver the `run_records` import, `SWITCH_SETTINGS`,
`switch_header()`, the three assignments in `build_text` and the header suffix; from the launcher
the `MR_SWITCHES` docstring line and the arm print (the stale-shard cleanup now imports
`run_records` itself); from both mergers the arm checks; from probe 10 its `switches:` header line;
and trims `run_records.py` / `test_run_records.py` to the P6 contract above.

- [ ] **Step 4: Green**

| command | expected |
|---|---|
| `maxima --very-quiet -b test/matcher/test_mr_match.mac < /dev/null \| grep -a '^Results'` | `Results: 53 passed, 0 failed` (`W_RETRY=true`) / `Results: 54 passed, 0 failed` (`false`) |
| `sbcl --non-interactive --load maxima_rubi_match.lisp --load test/matcher/test_mr_match.lisp --eval '(mr-match-test:run)' < /dev/null \| grep -a '^Results'` | the same line |
| `maxima --very-quiet -b test/matcher/test_mr_tree.mac < /dev/null \| grep -a '^Results'` | `Results: 51 passed, 0 failed` |
| `maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null \| grep -a '^Results'` | `Results:  56  passed,  0  failed` |
| `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null \| grep -a '^Results'` | `Results:  897  passed,  0  failed` |
| `python3 test/check_generated_rules.py \| tail -1` | `Results: 11 passed, 0 failed` |
| `for c in 1 2 3; do python3 generator/generate_rules.py --class $c > /dev/null; done; git status --porcelain rules/ \| wc -l` | `0` |
| `python3 test/test_run_records.py \| tail -1` | `Results: 15 passed, 0 failed` |
| `for t in test_merge_classes test_driver_core_pin test_ab_records test_record_medians test_driver_parens test_mr_sum_concrete test_head_rewrites; do python3 test/$t.py < /dev/null \| tail -1; done` | `Results: 2 passed, 0 failed` / `5 passed` / `6 passed` / `3 passed` / `2 passed` / `3 passed` / `20 passed`, each `0 failed` |
| `grep -rln 'mr_flat_wide\|mr_cond_retry\|mr_model_flags\|cond-retry\|with-mr-switches\|rubi_hybrid\|mr_hybrid_body\|MR_SWITCHES\|SWITCH_SETTINGS' maxima_rubi.mac maxima_rubi_utils.mac maxima_rubi_*.lisp test_maxima_rubi.mac test/matcher/*.mac test/matcher/*.lisp test/*.py generator/*.py` | exactly `test/matcher/test_mr_dispatch.mac` (the `?boundp` check), `test/p5_gate.py`, `test/run_records.py`, `test/test_run_records.py` |

Then the matcher regression suite, both arms in sequence (`run_in_background`), as in Task 4
Step 6: `Results: 109 passed, 0 failed` twice (its modes bind `*flat-wide*` themselves; nothing in
it read the deleted switches), and `git diff test/matcher/*.out` changing only judged / git HEAD /
TIMING / build lines.

- [ ] **Step 5: The class-2 no-op run**

The hard-wired tree must reproduce the final arm. `sh test/build_rules_core.sh` (the fingerprint
changed), then the Task 2 procedure for class 2 with `RUN` replaced by the record name
`test/corpus_class2.p6-noop.out` and no `MR_SWITCHES` (the driver no longer reads it):

```bash
python3 test/launch_class_shards.py "2 Exponentials" test/corpus_class2.pre-matcher.out test/corpus_driver.py --launch < /dev/null
setsid sh test/wait_and_merge.sh test/corpus_class2.shard-pids test/merge_class_shards.py \
    test/class2_merge.p6-noop.log "2 Exponentials" test/corpus_class2.p6-noop.out test/corpus_driver.py \
    "corpus_class2.shard*.out" < /dev/null > /dev/null 2>&1 &
```

After the merge (`OK: 965/965 …`, `merge rc=0`):

```bash
python3 test/ab_records.py $F2 test/corpus_class2.p6-noop.out --all
python3 probes/matcher/10-p5-attribution.py "2 Exponentials" $F2 test/corpus_class2.p6-noop.out passfail \
    "${TMPDIR:-/tmp}/p6-noop-passfail.out" 30 24
```

Must hold: every PASS→FAIL entry of the A/B is a PASS class on its probe-10 re-run (the re-run's
`Results:` line reads `<n> passed, 0 failed`); every FAIL→PASS entry has `t=` ≥ 15 s or is
`timeout` in `$F2` (cap-band). Anything else is a behaviour change P6 introduced: **stop and
report to the user**.

- [ ] **Step 6: Commit**

```bash
git add maxima_rubi_match.lisp maxima_rubi_dispatch.lisp maxima_rubi_utils.mac test/check_generated_rules.py \
        test/matcher/test_mr_match.lisp test/matcher/test_mr_dispatch.mac test_maxima_rubi.mac \
        test/run_records.py test/test_run_records.py test/corpus_driver.py test/launch_class_shards.py \
        test/merge_class_shards.py test/merge_timeout_rerun.py probes/matcher/10-p5-attribution.py \
        test/matcher/roundtrip.out test/matcher/roundtrip.flags.out test/matcher/controls.out \
        test/matcher/spike01.out test/matcher/gate.out test/matcher/gate.flags.out \
        test/corpus_class2.p6-noop.out
git commit -m "P6: hard-wire the P5 winners; delete the migration switches, their plumbing and rubi_hybrid"
```

- [ ] **Step 7: The ledger**

```markdown
### Task 5 — P6 code
- winners applied: flat-wide <W_FLAT>, cond-retry <W_RETRY>, model-flags <W_FLAGS>; anchors: <Step 1 line>
- red: <Step 2's FAIL and Results lines>
- green: <Step 4's expected-column results in table order; the grep's file list; the two regression-suite Results lines>
- no-op run: <merge OK line>; A/B <PASS->PASS / PASS->FAIL / FAIL->PASS / FAIL->FAIL>; re-run <Results line>; FAIL->PASS entries <t= list>
```

```bash
git add .superpowers/sdd/progress.md
git commit -m "docs: ledger — P6 hard-wiring"
```

### Task 6: P6 — TLS on the final tree, the standing records, the docs, the acceptance record

Branch: `matcher-substrate`. Starts after Task 5's commits. Every figure written into a document
in this task is copied from a committed record, probe output or ledger line, and the document
names that file. `F1 F2 F3` are the final records named in the Task 3 ledger; `W_FLAT`,
`W_RETRY`, `W_FLAGS` the winners (Task 5 Step 1). Where a replacement below shows `<a|b>`, write
the alternative the winner selects.

**Files:**
- Regenerate: `probes/matcher/08-runtime-load.out`
- Replace: `test/corpus_class1.out`, `test/corpus_class2.out`, `test/corpus_class3.out`
- Modify: `generator/generate_rules.py` (comments only), `README.md`, `docs/class-porting.md`,
  `AGENTS.md`, `todo/TODO.md`, `.superpowers/sdd/progress.md`
- Create: `docs/matcher-substrate-migration.md`

**Interfaces:**
- Consumes: the ledger's Plan 3 sections (Tasks 1–5): `FINAL_ARM` and the final records, the
  winners, the gate outputs, the attribution and acceptance blocks, the re-check transitions, the
  Task 5 counts (`test_mr_match` 53 or 54, dispatch 56, Layer A 897, `test_run_records` 15).
- Produces: spec §5 criteria 1–6 met, each checked in Step 9.

- [ ] **Step 1: Probe 08 on the final tree** (spec §5 criterion 5; nothing else running)

Run: `sh probes/matcher/08-runtime-load.sh > probes/matcher/08-runtime-load.out 2>&1; cat probes/matcher/08-runtime-load.out` (~20 s).

Must hold: both `LOAD` lines end `TLS lines 0`, each followed by `R load … rules 3513` and
`R smoke answered true radcan zero-chain true`; both `LAYER-A` lines read
`TLS lines 0: Results:  897  passed,  0  failed`; `DISPATCH-SUITE flagless … Results:  56  passed,  0  failed`;
`CORE-BUILD … exit 0: built test/mr_rules.core (<bytes> bytes) rules=3513 fingerprint=<md5>`. A
nonzero TLS count or a missing `Results:` → **stop and report to the user** (the TLS rule could
not be stated as measured).

```bash
git add probes/matcher/08-runtime-load.out
git commit -m "probe: matcher 08 re-run on the final tree (P6, spec §5 criterion 5)"
```

- [ ] **Step 2: The standing records**

`test/corpus_class1.out` and `test/corpus_class2.out` are byte-identical to their
`.pre-matcher.out` copies (checked while writing this plan: the P0 class-1/2 runs doubled as the
class-3 campaign's close records); `test/corpus_class3.out` is the campaign's 2026-09-04 record
(`docs/corpus-class3-deferred-uplift.md` §5.1), which stays in git history. Replace all three with
the final records:

```bash
cmp test/corpus_class1.out test/corpus_class1.pre-matcher.out && cmp test/corpus_class2.out test/corpus_class2.pre-matcher.out && echo same
cp $F1 test/corpus_class1.out; cp $F2 test/corpus_class2.out; cp $F3 test/corpus_class3.out
python3 test/record_medians.py test/corpus_class1.out test/corpus_class2.out test/corpus_class3.out
git add test/corpus_class1.out test/corpus_class2.out test/corpus_class3.out
git commit -m "record: the matcher substrate's final class 1-3 records become the standing records"
```

Expected: `same`, then three `record_medians.py` lines whose PASS and median agree with Task 4
Step 1's gate lines.

- [ ] **Step 3: Generator comments** (the P6 documentation carry; no generated output changes)

In `generator/generate_rules.py` make four exact replacements. First:

```python
    """The pattern-variable name for capture v of rule n of file key:
    `_mr_<key>_r<n>_v` (the brief's naming; pattern-variable status comes
    from matchdeclare, not from the leading underscore). cap_remap is
    applied before the name is built (see CAP_REMAP).
    """
```

becomes

```python
    """The capture name for pattern variable v of rule n of file key:
    `_mr_<key>_r<n>_v` (the brief's naming). The pattern string names the
    variable with it, so the dispatcher's binding list is the mm list
    (matcher substrate spec 3.4 "Captures"). CAP_REMAP is applied before
    the name is built.
    """
```

Second:

```python
# unchanged in value, only the names move.
CAP_REMAP = {
```

becomes

```python
# unchanged in value, only the names move.
# (Matcher substrate: the rationale above is the defmatch-era one. The remap
# stays a pure relabel so the rule files regenerate byte-identical to the P0
# tree, spec 3.4; whether MR-MATCH's Orderless binding still needs it is not
# measured.)
CAP_REMAP = {
```

Third:

```python
    "decls" (extra matchdeclare names, MatchQ), "markers" (the active
```

becomes

```python
    "decls" (extra names a MatchQ site declares), "markers" (the active
```

Fourth:

```python
                    # consuming the marker, no matchdeclare.
```

becomes

```python
                    # consuming the marker.
```

Run:

```bash
python3 -m py_compile generator/generate_rules.py
for c in 1 2 3; do python3 generator/generate_rules.py --class $c > /dev/null; done; git status --porcelain rules/ | wc -l
python3 test/check_generated_rules.py | tail -1
grep -c 'matchdeclare' generator/generate_rules.py
```

Expected: `0`, `Results: 11 passed, 0 failed`, `0`.

- [ ] **Step 4: README.md** — eleven exact replacements, old text first

(1)

```markdown
integration rules, ported as declarative Maxima patterns executed by a
first-match-wins rule runner, held to the Rubi Maxima-syntax test corpus
as the yardstick. Milestone 1 delivered the foundation (loader, runner,
```

→

```markdown
integration rules, ported as Mathematica-form patterns matched by a
Lisp matcher with Mathematica's semantics (first match wins), held to
the Rubi Maxima-syntax test corpus as the yardstick. Milestone 1
delivered the foundation (loader, runner,
```

(2)

```markdown
ported class 2 (exponentials) and class 3 (logarithms). Classes 4–8
are open runbook tickets (`todo/TODO.md`, `docs/class-porting.md`).
```

→

```markdown
ported class 2 (exponentials) and class 3 (logarithms), and the matcher
substrate (`docs/matcher-substrate-migration.md`) replaced Maxima's
`defmatch` under all three. Classes 4–8 are open runbook tickets
(`todo/TODO.md`, `docs/class-porting.md`).
```

(3)

```markdown
**Any `maxima` process that loads rule files must be started with
`-X "--tls-limit 100000"`** (two argv tokens — the flag takes no
`=`). The SBCL special-variable pool is a hard per-process cap; beyond
it, creating a `defmatch` slot dies with the uncatchable FATAL
"Thread local storage exhausted". The default limit holds only ~310
class-1 rules; 100000 covers the full loaded Rubi set at ~1.4x
headroom. The test harness and the rules-core build already pass the
flag; an interactive session that calls `mr_load_all()` or
`mr_load_class1_all()` must set it at startup.
```

→

```markdown
No special SBCL flag is needed: the full rule table loads and Layer A
runs green without `-X "--tls-limit 100000"`
(`probes/matcher/08-runtime-load.out`). Under the earlier `defmatch`
runtime every rule created special variables and the flag was
mandatory; the rule records the matcher substrate loads create none.
```

(4)

```text
mr_load_all()$                 /* classes 1-3, Rubi LoadRules order (3,514 rules) */
/* or: mr_load_class1_all()$      the class-1 rule set only (3,055 rules) */
```

→

```text
mr_load_all()$                 /* classes 1-3, Rubi LoadRules order (3,513 rules) */
/* or: mr_load_class1_all()$      the class-1 rule set only (3,054 rules) */
```

(5)

```markdown
`b`-suffixed 1.2.1 siblings + the manually ported 9.1), then class 2
```

→

```markdown
`b`-suffixed 1.2.1 siblings + the generated 9.1), then class 2
```

(6)

```markdown
`LoadRules` order. On a build without the TLS headroom, load single
files instead:
`%mr_load_sibling("rules/class1/<key>.mac", 'mr_witness_<key>)` then
concat the file's rule list onto `mr_rule_table` (`unload()` releases a
file's patterns).
```

→

```markdown
`LoadRules` order. A single file loads with
`%mr_load_sibling("rules/class1/<key>.mac", 'mr_witness_<key>)`; concat
its `mr_rules_<key>` list onto `mr_rule_table` to dispatch on it.
```

(7) — the second bullet of the new text only when `W_FLAGS=true`:

```markdown
- `rubi_verbose` prints the fired rule, boolean-leak misfires, and
  BOOLWALK crashes on each dispatch.
```

→

```markdown
- `rubi_verbose` prints each rule that fires, declines or misfires (with
  its binding) and each cond that does not accept a binding.
- The dispatch simplifies under `radexpand:false` and `logexpand:false`,
  which keep Mathematica's stored shapes. `rubi(f, x)` receives `f`
  already simplified by the caller: an integrand built under Maxima's
  defaults may have lost a shape a rule needs (`(b*x^2)^p` is stored as
  `b^p*abs(x)^(2*p)`); set both flags to false before building `f`.
```

(8) the Measured-state table and the paragraph under it —

```markdown
| class | integrals | package PASS | native `integrate` | record |
|---|---|---|---|---|
| 1 algebraic | 25,697 | **20,069 (78.1 %)** | 12,798 (49.8 %) | `docs/corpus-baseline-uplift.md`, `docs/corpus-class2-baseline-uplift.md` §8 |
| 2 exponentials | 965 | **594 (61.6 %)** | 593 (61.5 %) | `docs/corpus-class2-baseline-uplift.md` |
| 3 logarithms | 3,085 | **1,736 (56.3 %)** | 1,441 (46.7 %) | `docs/corpus-class3-baseline-uplift.md` |

The class-1 and class-2 figures are the 2026-08-28 re-measure under the
zero-chain `radcan(rat())` fallback (Maxima build 2026-08-20); class 3
is the milestone-3 acceptance (build 2026-08-29). The class-3 deferred
campaign (branch `class3-deferred`,
`docs/corpus-class3-deferred-uplift.md`) is re-measuring class 3; its
figure replaces the row above only once the campaign's acceptance
record is written.
```

→ (each `<…>` from Task 4 Step 1's gate lines and the Task 4 ledger's date; pct = PASS / integrals × 100, one decimal)

```markdown
| class | integrals | package PASS | native `integrate` | record |
|---|---|---|---|---|
| 1 algebraic | 25,697 | **<PASS1> (<pct1> %)** | 12,798 (49.8 %) | `test/corpus_class1.out`, `docs/matcher-substrate-migration.md` |
| 2 exponentials | 965 | **<PASS2> (<pct2> %)** | 593 (61.5 %) | `test/corpus_class2.out`, `docs/matcher-substrate-migration.md` |
| 3 logarithms | 3,085 | **<PASS3> (<pct3> %)** | 1,441 (46.7 %) | `test/corpus_class3.out`, `docs/matcher-substrate-migration.md` |

The package figures are the matcher substrate's final records (build
2026-08-31 13:27:47, <date>); on the same build the `defmatch` runtime
measured 20,125 / 614 / 2,058 (the P0 records,
`test/corpus_class{1,2,3}.pre-matcher.out`). The native `integrate`
column is the milestone baselines' (classes 1–2 on the 2026-08-20
build, class 3 on the 2026-08-29 build).
```

(9)

```markdown
- **Layer A** — unit suite, one batch run (the TLS flag is mandatory:
  without it the run dies at the class-3 tests):
  `maxima --very-quiet -X "--tls-limit 100000" -b test_maxima_rubi.mac`
  (892 targets).
```

→

```markdown
- **Layer A** — unit suite, one batch run:
  `maxima --very-quiet -b test_maxima_rubi.mac` (897 targets). The
  matcher, the converter and the dispatcher have their own unit suites
  and a regression suite under `test/matcher/`; `AGENTS.md` lists the
  commands.
```

(10)

```text
maxima_rubi_utils.mac       runner, %mr_ predicate/shim layer, noun forms
maxima_rubi_dispatch.lisp   table dispatcher (pass-2 matchreverse rescan)
maxima_rubi_implicit1.lisp  exponent-1 rescan (Maxima drops stored ^1)
maxima_rubi_pass4.lisp      pass-4 bare-factor sweep (class-3 deferred campaign)
rules/class{1,2,3}/<key>.mac  GENERATED rule files, one per Rubi .m (do not
                            edit; class1/9_1.mac is a manual port)
```

→

```text
maxima_rubi_utils.mac       mr_top / rubi, %mr_ predicate/shim layer, noun forms
maxima_rubi_match.lisp      mr-match: the pattern matcher (Mathematica semantics)
maxima_rubi_tree.lisp       mr-tree: Maxima <-> Mathematica-form trees
maxima_rubi_dispatch.lisp   rule records, the dispatcher, MatchQ
rules/class{1,2,3}/<key>.mac  GENERATED rule files, one per Rubi .m (do not
                            edit)
```

(11)

```markdown
(`generate_class1.py` is the class-1 shim). The one exception is
`rules/class1/9_1.mac`, a manual port (the section-9.1 legacy file is
absent from the pinned Rubi.m's LoadRules, so the generator does not
emit it).
```

→

```markdown
(`generate_class1.py` is the class-1 shim). `rules/class1/9_1.mac` is
generated from the section-9.1 legacy file, which the pinned Rubi.m's
LoadRules does not load but the 2018 corpus needs.
```

Run: `grep -n 'tls-limit\|defmatch\|manual\|pass4\|implicit1\|3,514\|3,055\|892' README.md` —
every hit is in replacement (2) or (3) (the replaced runtime named, the flag named as not needed).

- [ ] **Step 5: `docs/class-porting.md`** — old text first

(1) Insert after the paragraph that ends ``(commit `ff814e9`). The pilot's measured acceptance record:``
/ `` `docs/corpus-class2-baseline-uplift.md`. `` (a blank line, then):

```markdown
**Matcher substrate (2026-09, `docs/matcher-substrate-migration.md`).**
After the pilot, classes 1–3 were re-hosted from Maxima's `defmatch`
onto `mr-match`. Steps 1, 3, 5 and 6 below describe the substrate; the
class-2 evidence they cite is the `defmatch`-era execution.
```

(2)

```markdown
1. **TLS flag.** Every maxima process that loads rule files runs with
   `-X "--tls-limit 100000"` — **two argv tokens, not
   `--tls-limit=N`** (user decision 2026-08-22). The load-wall probes
   self-flag if the build moves (`probes/load_wall/probe-tls-calibration.out`,
   `probe-load-curve.out`; the pilot's full-table probe
   `probes/load_wall/probe-class2-load.{run,out}` — re-run it per class,
   it prints `TABLE_AT_LOAD <n>`).
```

→

```markdown
1. **TLS.** No flag is needed: rule records create no special
   variables (`probes/matcher/08-runtime-load.out`, re-measured at the
   matcher substrate's close). Re-run probe 08 after loading a new
   class — it loads the full table and runs Layer A with and without
   `-X "--tls-limit 100000"` and counts `Thread local storage` lines; a
   nonzero count restores the flag rule (AGENTS.md, TLS section).
```

(3)

```markdown
   upgrade, never carried over (current build: 5.50.0, build date
   2026-08-20 21:36:22, SBCL 2.6.7).
```

→

```markdown
   upgrade, never carried over (current build:
   `branch_5_50_base_84_g4204fb669`, build date 2026-08-31 13:27:47,
   SBCL 2.6.7).
```

(4) Insert after the Step 1 paragraph that starts `**Class-2 evidence.** Task 1 (commits` (a blank
line, then):

```markdown
**Matcher substrate additions.** (c) The pattern census: every Int
LHS through the reader's emulated evaluation —
`python3 probes/matcher/02-construct-census.py > probes/matcher/02-construct-census.out`
(all 199 LoadRules files, ~1 min); its `=== NAMED GAPS in the LHS
pattern language` section names any construct `mr-match` does not
support. (d) The G-9 risk scan: the `=== LHS evaluation effects`
section's `risk:` rows name every rule whose evaluated LHS the reader
does not emulate (none in classes 1–3; the known ones are in classes 4
and 8, e.g. `risk:Pi-arg:sin` 4.1.1.1.m L8). A risk rule is a
`GenError` at generation: decide each before Step 3 (spec
`docs/superpowers/specs/2026-09-12-matcher-substrate-design.md` §3.4).
```

(5)

```markdown
file/rule/head, never a silent pass-through). Head-position pattern
variables (Rubi `v_[…]`) are a pattern form in the **custom
`%mr_matchQ` matcher** — `defmatch` in this build rejects
head-position pattern variables ("defmatch: some pattern variables are
not atoms"); class-2's r96 case forced the matcher addition
(`70e6f58`).
```

→

```markdown
file/rule/head, never a silent pass-through). The generator emits each
rule as a `%mr_defrule` record: the LHS as the evaluated FullForm
pattern string `mr-match` prepares at load (head-position pattern
variables such as Rubi `F_[…]` included), a `/;` inside an RHS
`With`/`Module` moved into cond, and each `MatchQ` site as
`%mr_matchQ(u, "<pattern>", [<parts>], cond)` (spec §3.4); cond and
repl translation is unchanged.
```

(6)

```markdown
rule counts equal the census (`defmatch` counts); **no raw
```

→

```markdown
rule counts equal the census (`%mr_defrule` counts); **no raw
```

(7)

```markdown
**Acceptance.** Counts match the census exactly; 0 raw-`$` hits;
rename counts match the table.
```

→

```markdown
**Acceptance.** Counts match the census exactly; 0 raw-`$` hits;
rename counts match the table. A pattern `mr-match` cannot prepare is
a load error of `%mr_defrule`, so the Step-6 load is the prepare check
for the new class; `python3 test/check_generated_rules.py` stays
`Results: 11 passed, 0 failed` (it holds classes 1–3 to the P0 base
`0a6664c`).
```

(8)

```text
sh probes/load_wall/probe-class2-load.run     # full-table load under the TLS flag
```

→

```text
sh probes/matcher/08-runtime-load.sh > probes/matcher/08-runtime-load.out 2>&1   # full-table load + Layer A, flagless and flagged
```

(9)

```markdown
125, fingerprint `aa53741f7ac802e2c3b8bd93720b219d`); the TLS probe
prints `TABLE_AT_LOAD <n>`; Layer A green.
```

→

```markdown
125, fingerprint `aa53741f7ac802e2c3b8bd93720b219d`); probe 08's
`R load … rules <n>` lines show the new table and both `LAYER-A` lines
are green with `TLS lines 0`.
```

Run: `grep -n 'tls-limit\|TABLE_AT_LOAD\|probe-class2-load' docs/class-porting.md` — every hit
is in replacement (2) or in a `Class-2 evidence` paragraph.

- [ ] **Step 6: AGENTS.md** — old text first

(1)

```markdown
is green, with no TLS message (`probes/matcher/08-runtime-load.out`,
build `branch_5_50_base_84_g4204fb669`). **The flag is no longer
```

→

```markdown
is green, with no TLS message (`probes/matcher/08-runtime-load.out`,
build `branch_5_50_base_84_g4204fb669`; re-run on the final tree at the
matcher substrate's close, P6). **The flag is no longer
```

(2)

```markdown
898 targets (green: `Results: 898 passed, 0 failed`; the
```

→

```markdown
897 targets (green: `Results: 897 passed, 0 failed`; the
```

(3)

```markdown
892 → 875, and the generated MatchQ pattern shapes, 22 checks), → 898
plan-2 final review (1.4.2 r17 MatchQ exponent part folding)).
```

→

```markdown
892 → 875, and the generated MatchQ pattern shapes, 22 checks), → 898
plan-2 final review (1.4.2 r17 MatchQ exponent part folding), → 897
Plan 3 P6 (the `mr_model_flags` pair hard-wired to one check)).
```

(4)

```markdown
Green: `Results: 53 passed, 0 failed` (mr-match; 48 at Plan 1's Task 5,
+3 at the final-review fix wave: the last-absorber cost bounds and the
empty-leftover lock, +2 at Plan 2: the Power-exponent Optional
default), `Results: 51 passed, 0 failed` (mr-tree; 46, +5 at Plan 2:
```

→ when `W_RETRY=true`

```markdown
Green: `Results: 53 passed, 0 failed` (mr-match; 48 at Plan 1's Task 5,
+3 at the final-review fix wave: the last-absorber cost bounds and the
empty-leftover lock, +2 at Plan 2: the Power-exponent Optional
default, +1 and −1 at Plan 3 P6: the `*flat-wide*` default check, the
no-retry check deleted), `Results: 51 passed, 0 failed` (mr-tree; 46,
+5 at Plan 2:
```

→ when `W_RETRY=false`

```markdown
Green: `Results: 54 passed, 0 failed` (mr-match; 48 at Plan 1's Task 5,
+3 at the final-review fix wave: the last-absorber cost bounds and the
empty-leftover lock, +2 at Plan 2: the Power-exponent Optional
default, +1 at Plan 3 P6: the `*flat-wide*` default check),
`Results: 51 passed, 0 failed` (mr-tree; 46, +5 at Plan 2:
```

(5)

```markdown
CRE input and the booleans) and `Results: 58 passed, 0 failed`
```

→

```markdown
CRE input and the booleans) and `Results: 56 passed, 0 failed`
```

(6)

```markdown
MatchQ part folding and an out-of-range part error, +1 at Plan 3: the
switch defaults).
```

→

```markdown
MatchQ part folding and an out-of-range part error, +1 at Plan 3: the
switch defaults, −2 at P6: each switch pair hard-wired to one check, the
defaults check turned into the switches-gone check).
```

(7)

```markdown
MISS), 0 UNSOUND, 0 false mutation matches. `MR_WORK=<dir>` moves the
```

→

```markdown
MISS), 0 UNSOUND, 0 false mutation matches. Since P6 the wide mode and
the flags arm are suite-only knobs: the package runs the <narrow|wide>
reading <with|without> the simplifier flags
(`docs/matcher-substrate-migration.md`). `MR_WORK=<dir>` moves the
```

(8) the whole Task 1 paragraph, from its first line

```markdown
**Switch arm — matcher substrate P5** (Plan 3,
```

through its last line

```markdown
`Results: 23 passed, 0 failed`.
```

→

````markdown
**P5 records and gates** (Plan 3,
`docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.md`). The
P5 records `test/corpus_class<N>.p5-run<K>.out` state on their
`filter:` line the migration switch arm they ran; the switches were
hard-wired and deleted at P6 (`docs/matcher-substrate-migration.md`).
The gate and the winner rule over those records:

```sh
python3 test/p5_gate.py gate <P0-record> <new-record>
python3 test/p5_gate.py winner <switch> <run-1 c1> <run-1 c2> <run-1 c3> <flip c1> <flip c2> <flip c3>
```

A launch deletes the previous run's shard files first and refuses while
one of its pids is alive; entry subprocesses get stdin `/dev/null`
(`probes/matcher/09-harness-fault-verdict.out`). Guard (no Maxima):
`python3 test/test_run_records.py` — green `Results: 15 passed, 0 failed`.
````

Run: `grep -c 'MR_SWITCHES' AGENTS.md` — Expected: `0`.

- [ ] **Step 7: `todo/TODO.md`**

Replace the heading `## Matcher substrate — in prog (Plan 3 executing)` with
`## Matcher substrate — done (P0–P6, YYYY-MM-DD)` (`date +%F`). Keep the intro paragraphs; replace
every bullet under them with (the `<…>` copied from the ledger):

```markdown
Plan 3 (P5–P6,
`docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.md`) is
complete: the switch A/B chose <the three winners>; the final records
<PASS1> / <PASS2> / <PASS3> PASS (P0 20,125 / 614 / 2,058; median
<m1> / <m2> / <m3> s vs 1.3 / 4.3 / 3.9 s); every PASS→FAIL attributed
(probe 10) and accepted by the user <date>; the switches, their
plumbing and `rubi_hybrid` deleted; acceptance record
`docs/matcher-substrate-migration.md`. Ledger: plan 3 section.

- Next: merge `matcher-substrate` into `master` when the user says so;
  push once origin access works — open
- After the migration (user-endorsed 2026-09-11, raise with the user):
  class 4+ porting on the substrate; rubi-then-integrate as a user
  mode; an answer-size metric; right-sizing the process — open
- Carried: numeric folding in MatchQ part substitution; a parts-keyed
  MatchQ compiled-pattern cache (unbuilt: the P5 wall gates passed
  without it); the MODEL-LOST figures (1,166 / 395 vs the spec's
  1,142 / 312) <unexplained|explained in the acceptance record>;
  `test/test_driver_radcan_fallback.py`'s `[gate-blocks]` fixture
  (1.1.3.8 e541/e543/e544 verify on the substrate before the fallback
  runs — red since P4; new elliptic fixture entries needed); the plan-2
  final review's deferred minors (non-discriminating dispatch checks,
  the `max->tree` docstring, `(not (eql default 1))` type sensitivity,
  12 SBCL STYLE-WARNINGs, the capitalised-symbol head collision in
  `mr-binding-value`, conversions and the repl call outside
  `mr-guarded`) — open
- Deferred: the `MX_` plist re-read issue in `mr-tree` (not reachable)
  — open
- Known cost item: a collapsible claimer still enumerates every sub-run
  of a product's factors (`probes/matcher/06-dispatch-cost.out`); the
  P5 wall gates passed with it — open
```

- [ ] **Step 8: The acceptance record `docs/matcher-substrate-migration.md`**

Write it from the ledger, in this order. Every figure cites the committed file it comes from
(AGENTS.md research discipline), and no section is written ahead of its evidence:

1. **Header** — date, the final commit, build `branch_5_50_base_84_g4204fb669` (2026-08-31
   13:27:47) / SBCL 2.6.7, branch, spec (`48c61b8`), plans 1–3.
2. **What changed** — the substrate in four lines (`mr-match`, `mr-tree`, `%mr_defrule` records,
   `%mr_dispatch_tree`), and spec §7's deletions inventory as a table naming the commit that
   deleted each row (`git log --oneline --diff-filter=D -- <file>` for deleted files; the Plan 2
   ledger for the generator and utils families; Task 5's commit for the switches and
   `rubi_hybrid`).
3. **Records and stamps** — the P0 records (`0a6664c`, core `5ef9b3bc5ee07ffac0e76f1fea54fbac`)
   and every P5 record (merge date, core fingerprint, `switches:` line); the final arm and the
   final records.
4. **The switch A/B** — one table: run × class → PASS, median, timeouts, `error`; the three
   `WINNER` lines; the arm A/B tables (Task 3 Step 7); spec §6's caveats stated as such: G-6 has no
   Mathematica oracle (the A/B measures usefulness, not faithfulness), condition retry has no
   documented Wolfram statement; the `mr_model_flags` reading (Task 3 Step 8) and, when the flags
   arm won, the user-facing consequence README states.
5. **The P5 gates on the final records** — the three `p5_gate.py gate` outputs (PASS floor; wall
   ceiling, citing `probes/matcher/05-p0-wall-noise.out` when a median sits within 10 % of its
   ceiling), timeouts P0 → final, crashes P0 → final with probe 09's two findings (the core
   survives probe 07's shape; stdin decided `ldb`), the `rubi_hybrid` check.
6. **PASS→FAIL attribution and acceptance** — the method (probe 10; deviation 8), per class the
   disposition totals and one row per group (entries, mechanism line, P0 route → final route),
   the user's acceptance with its date.
7. **Timeouts** — the new timeouts per class with their 100 s transitions; the re-check records.
8. **The final tree** — Layer A, the three unit suites, the static gate, the regression suite
   (0 UNSOUND, 0 false mutation matches, G-2 and G-4 closed — quoting `test/matcher/gate.out` and
   `gate.flags.out`), the P6 no-op run (Task 5 Step 5).
9. **TLS** (criterion 5) — probe 08 on the final tree, and the corrected mechanism: interpreted
   cond/repl `block` locals take no TLS slot (`mbind-doit` binds them with `mset` + `mspeclist`,
   no special declaration); the `defmatch` slots came from compiled matcher code — spec §6's "TLS
   may not disappear" sentence stated the mechanism inaccurately. Probe walls (06, 08, 09, 10) are
   records, not gates; the corpus medians of section 5 are the performance gate.
10. **Acceptance scorecard** — spec §5 criteria 1–6, each with its evidence (Step 9).
11. **Carried and deferred** — Step 7's bullets; the MODEL-LOST figures as measured (explained
    only if Task 3 Step 8 did).

- [ ] **Step 9: Spec §5 criteria, checked**

| criterion | check | expected |
|---|---|---|
| 1 no `defmatch` / `matchdeclare` / pass 2–4 / workaround emitter | `grep -rln 'defmatch(\|matchdeclare(' maxima_rubi.mac maxima_rubi_utils.mac maxima_rubi_*.lisp rules generator \| wc -l`; `ls maxima_rubi_implicit1.lisp maxima_rubi_pass4.lisp 2>&1 \| grep -c 'No such file'`; `grep -c '%mr_dispatch_rev\|%mr_mq_\|%mr_binpowfactors\|%mr_mbp_\|%mr_headvar_match\|%mr_logpow_match\|%mr_logratio' maxima_rubi_utils.mac maxima_rubi_dispatch.lisp` | `0`; `2`; `…:0` twice |
| 2 final records ≥ P0, PASS→FAIL accepted, wall ≤ P0, timeouts attributed, 100 s re-check | the Task 4 ledger blocks; `ls test/corpus_class[123].p5-final.timeout-rerun/*.timeout100s.out` | three `Results: 4 passed, 0 failed`; the acceptance block; three files |
| 3 regression suite | `grep -a '^PASS: .*UNSOUND\|^PASS: .*false mutation\|^PASS: .*G-2\|^Results' test/matcher/gate.out test/matcher/gate.flags.out` | the UNSOUND (G-4 closed), false-mutation and G-2 checks `PASS:` in both files; `Results: 109 passed, 0 failed` twice |
| 4 Layer A and the static gate | re-run both | `Results:  897  passed,  0  failed`; `Results: 11 passed, 0 failed` |
| 5 the TLS rule on a measurement of the final tree | Step 1's record; AGENTS.md's TLS section cites it | `TLS lines 0` four times |
| 6 record, AGENTS.md, README, runbook | `git status --porcelain -- docs/matcher-substrate-migration.md AGENTS.md README.md docs/class-porting.md` before Step 10's commit | four modified/added paths |

- [ ] **Step 10: Commit and the ledger**

```bash
git add generator/generate_rules.py README.md docs/class-porting.md AGENTS.md todo/TODO.md docs/matcher-substrate-migration.md
git commit -m "docs: matcher substrate acceptance record; AGENTS, README, runbook, TODO, generator comments (P6)"
```

Append to the ledger:

```markdown
### Task 6 — P6 docs
- probe 08 (probes/matcher/08-runtime-load.out, <its === line>): <every LOAD / R / LAYER-A / DISPATCH-SUITE / CORE-BUILD line>
- standing records: <the three record_medians.py lines>
- generator comments: <the three expected values of Step 3>
- criteria: <Step 9's table, measured column>
- Plan 3 complete. Next: superpowers:finishing-a-development-branch (merge when the user says; push when origin access works); delete the plan-2 and plan-3 SDD workspaces after the final review.
```

```bash
git add .superpowers/sdd/progress.md
git commit -m "docs: ledger — P6 docs, Plan 3 complete"
```

