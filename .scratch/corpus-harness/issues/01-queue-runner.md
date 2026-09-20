# Corpus runs through one work queue instead of fixed shards

Status: done (2026-09-18, 95e86bf)
Type: task (decide the worker count, then build)
Filed: 2026-09-15 (exact seen test brainstorm; dropped from that plan by user decision the same day —
design `docs/superpowers/specs/2026-09-15-matcher-seen-test-intpart-design.md` §3.3)

## Problem

The sharded launchers (`test/launch_class_shards.py`, `test/launch_timeout_rerun.py`) pack entries into
24 fixed shards by the previous record's per-entry times. When routes change, those estimates go stale
and a run ends with a long tail of a few busy shards. P5b run 4 (2026-09-14, shard `.out` mtimes in
`test/corpus_class{1,2,3}.shard*.out`, gitignored — they survive only until the next launch of that
class): class 1 launched 20:32 UTC, shards finished between +6 and +87 min, mean ≈ 46 min, so all 24
processes were busy for about 53 % of the wall; class 3 last shard +20 min (mean ≈ 7); class 2 last
+4.6 min (mean ≈ 1).

## Prototype

`01-queue-runner.patch` (against `43eb81b`): `test/run_corpus_queue.py` (one manager, N worker threads
pulling single entries; worker k writes `corpus_<slug>.shard<kk>.out` in the driver's format, so
`merge_class_shards.py` / `wait_and_merge.sh` / `merge_timeout_rerun.py` read it unchanged; longest
previous time first; a subset mode for the timeout re-check), the `corpus_driver.py` refactor it needs
(`run_entry`, `header_lines`, `build_info_lines`, `classify_output`, a lock on `REWRITE_STATS`), and
six guards in `test/test_run_records.py` (23 → 29, green on the prototype).

## Measurements (ad hoc, scratch worktrees; NOT committed evidence)

Build `branch_5_50_base_84_g4204fb669` / SBCL 2.6.7, 2026-09-15 16:17–16:47 UTC, unchanged runtime
tree (core fingerprint `b98e4748784738cb78f0163a97d4cf5f`, switch defaults), against the sharded
`test/corpus_class{2,3}.p5b-run1.out`. The machine is a VM with 24 vCPUs on a 12-core / 24-thread
Ryzen 9 9900X.

| run | wall | median / p90 per entry | timeouts | PASS→FAIL vs P5b |
|---|---|---|---|---|
| class 2 sharded (P5b) | ~4.6 min | 0.6 / 2.1 s | 14 | — |
| class 2 queue, 24 workers | 88 s | 0.9 / 3.2 s | 18 | 3 (2.3 e527, e528, e575; 27–29 s in P5b) |
| class 2 queue, 12 workers | 130 s | 0.6 / 2.1 s | 17 | the same 3 |
| class 3 sharded (P5b) | ~20 min | 1.5 / 8.4 s | 160 | — |
| class 3 queue, 24 workers | 585 s | 1.8 / 10.6 s | 189 | 17, all `→ timeout` |

Twenty-four busy workers slow every entry (hyperthread contention): at the 30 s cap that is a fidelity
loss. Twelve workers keep the per-entry walls. Projection from P5b run 1's summed per-entry times
(class 1 1,211 core-min, class 3 205, class 2 25): class 1 at 12 workers ~101 min, at 24 ~76 min, sharded
87 min — at a fidelity-preserving count the queue gains nothing on class 1. The P5b / P0 records
themselves ran partly contended (24 shards busy early in each run).

## Options when this is picked up

- 12 workers for classes 2 and 3 (measured faithful on class 2, ~2× faster), sharded for class 1.
- Measure 16 workers on class 3 before choosing a count.
- Keep cost-aware shards and add tail rebalancing (a finished shard takes over entries of a busy one).

## Comments

### 2026-09-17 — the faithful-pair class-1 gate run: the tail is now 42 % of the wall, and the cost model missed its own headline metric by 13.6x

New evidence from a real gate run (the seen-cut + `mr_giveup_last` pair, `MR_N_PROCS=33` to match
`c1-base.out`/`c1-after.out`'s contention profile). Build `branch_5_50_base_84_g4204fb669`, core
fingerprint `68e13698a15b2a97635b976a719001ec`, launched 2026-09-17 17:07:49 UTC, last shard finished
~21:00 UTC. Shard `.out` files are gitignored and survive only until the next class-1 launch.

**Wall: 3 h 52 min for 46.28 core-h of entry compute over 25,697 entries** (summed `t=`, 166,620 s).

| | |
|---|---|
| average concurrent entries (166,620 s / 13,930 s wall) | **12.0** of 33 processes launched |
| ...as a fraction of the 24 vCPUs | **~50 %** |
| entries done at +47 min / +2 h 14 / +3 h 52 | 62 % / 91 % / 100 % |
| **share of the wall spent on the last 9 % of entries** | **42 %** (1 h 38 min) |
| busiest shard vs idlest (summed compute) | shard08 13,919 s vs shard20 426 s = **32.7x** |
| planner's own prediction | `max job cost: 1021s (balance spread 1.25x)` |
| **actual max job vs predicted max** | **13.6x** |
| actual spread vs predicted spread | 26x worse |

Entry COUNT is not the driver, so a count-balanced partition would not help either: shard12 ran 2,762
entries in 4,161 s; shard31 ran 269 entries in 3,991 s; shard08 ran 1,009 in 13,919 s.

**Sharper root cause than "estimates go stale".** The planner's cost model is calibrated on the
PREVIOUS record's per-entry times (`cost-model: measured`). A full class-1 run is only ever done to
measure a behavioural change — and this change makes recovered entries 4-10x slower (1-3 s -> 13-15 s,
`handoffs/2026-09-17-rt-fix-ab-attribution.md`) and turns former timeouts into long-running verified
entries. So the estimates are wrong *precisely and worst in the entries the change touches*, which are
also the entries the run exists to measure. **Cost-model shards are least reliable exactly when they
matter most**, and a static partition has no mechanism to recover once it has mis-packed.

**The fidelity argument, which is stronger than the speed argument, and which this ticket did not yet
make.** A 12-worker queue would NOT have beaten this run on wall clock — 166,620 s / 12 = 231 min, and
this run took 232 min, because average concurrency already WAS 12. The defect is the SHAPE, not the
mean: 33 processes on 24 vCPUs early (1.4x over-subscribed, so every early entry ran contended and
slower than it would alone) collapsing to 1-5 processes late (cores idle). Per-entry wall therefore
depends on WHEN in the run an entry happened to be scheduled — under a 30 s WALL cap that decides
verdicts. It is the handoff's trap #4 ("a wall-clock cap measures the machine as much as the code")
applied to the harness itself, and it means a sharded record is not internally comparable, let alone
comparable with another record run at a different shard count. A fixed-worker queue holds concurrency
CONSTANT: same total compute, but every entry meets the same contention, and the idle tail disappears.

This also retires the projection above ("at a fidelity-preserving count the queue gains nothing on
class 1"): its sharded baseline was 87 min, measured before the routes changed. The same sharded
launcher now takes 232 min on class 1.

**Recommendation:** raise from `needs-triage`. Of the three options listed, tail rebalancing is the
cheap one but it does not fix the early over-subscription, so it buys back the 42 % tail and leaves the
fidelity problem. The fixed-worker queue (`01-queue-runner.patch`) fixes both. The open question the
2026-09-15 measurements left — the worker count — should be settled on class 1 rather than class 3,
since class 1 is where the 3 h 52 min is spent; and the count should be chosen at or below 24 so the
run is never over-subscribed.

### 2026-09-17 (b) — user's design call: workers <= cores, and DECOUPLE unit count from worker count. Simulated on the run above: 1.96x, and chunk-32 is as good as per-entry

User's reading of the run above (2026-09-17, after watching cores sit idle for two hours): *never run
more shards than there are cores, but increase the granularity of the shards.* That is the right fix
and it is two separate changes — the number of WORKERS (<= cores, for fidelity) and the number of WORK
UNITS (many more than workers, for the tail). The launcher today conflates them: one shard = one
process = one static partition.

Simulated on the 25,694 measured per-entry walls of the run above, dynamic pull (a free worker takes
the next unit; NO cost model, so nothing can go stale):

| workers | chunk | units | makespan | vs actual 232m | idle |
|---|---|---|---|---|---|
| 24 | 1 | 25,694 | 116m | 2.00x | 0.2% |
| 24 | 8 | 3,212 | 117m | 1.98x | 1.3% |
| **24** | **32** | **803** | **118m** | **1.96x** | **2.2%** |
| 24 | 128 | 201 | 129m | 1.80x | 10.0% |
| 24 | 512 | 51 | 183m | 1.27x | 36.6% |
| 24 | 2048 | 13 | 427m | 0.54x | 72.9% |
| 16 | 32 | 803 | 176m | 1.32x | 1.5% |
| 12 | 32 | 803 | 234m | 0.99x | 1.0% |

Floor (total compute / 24) = 116m. Findings:

1. **Granularity is the dominant term.** Today's effective granularity is ~779 entries/shard
   (25,697/33), which sits between the 512 and 2048 rows — exactly where the table collapses. Chunk-32
   recovers essentially all of it.
2. **Per-entry dispatch buys ~nothing over chunk-32** (116m vs 118m, 1.7%). This REFINES the prototype
   in `01-queue-runner.patch`, which dispatches per entry: chunks of ~32 get 98 % of the benefit at
   1/32 of the dispatch overhead, and a chunk-granular runner can keep writing one `.out` per worker,
   so `merge_class_shards.py` / `wait_and_merge.sh` still read it unchanged.
3. **Granularity alone is NOT enough — the worker count is the other half.** At 12 workers, chunk-32
   gives 234m, i.e. today's wall. So today's 33-shard run already achieved what a PERFECT 12-worker
   run would; its mean concurrency really was 12. The 2x needs fine chunks AND all 24 vCPUs busy
   throughout.
4. **workers <= cores is the FIDELITY fix, independent of speed.** 33 processes on 24 vCPUs meant early
   entries ran 1.4x over-subscribed and late entries ran alone, so per-entry wall depended on when an
   entry was scheduled — and that decides verdicts under a 30 s WALL cap.

**Caveats on the 118m.** The per-entry walls fed to the simulation were themselves measured under
VARYING contention (33-way early, 1-way late), so a uniform 24-worker run would be somewhat slower
than simulated — 118m is a floor-ish estimate, not a prediction. And 24 vCPUs is 12 physical cores +
SMT: the 2026-09-15 measurement in this ticket found 24 busy workers slow every entry and cost fidelity
at the 30 s cap (class 2: 3 PASS->FAIL, class 3: 17, all `-> timeout`). So 24-vs-16 remains a real
speed/fidelity tradeoff needing its own measurement; this simulation prices it at 118m vs 176m.

**Revised recommendation.** Build the chunk-granular runner (not per-entry), worker count a parameter
capped at the core count, chunk size ~32 entries, dynamic pull, no cost model. Settle the worker count
on class 1 by running one class-1 arm at 16 and one at 24 and comparing `ab_records.py` PASS->FAIL
against a known record — the count is a FIDELITY decision, so it must be gated on verdicts, not wall
clock.

### 2026-09-18 — built and landed (95e86bf)

`test/run_corpus_queue.py` is in, built from `01-queue-runner.patch` (which no
longer applied after the switch/caps work; the driver refactor was re-done
against current code and `run_entry` now carries the depth-cap count).

Two decisions differ from the prototype:

- **Dispatch stays per-entry.** The user asked for cost-sized jobs of ~10-30
  min. Simulated on the 25,697 per-entry walls of the 2026-09-17 run, that
  loses: per-entry 116 min, ~10-min units 120 min, ~30-min units 126 min at 24
  workers (floor 116). Makespan >= core-seconds/workers + largest unit, so the
  unit size is the tail bound, and every entry is already its own Maxima
  subprocess — a bigger unit amortises nothing. Sized from the previous record,
  a 10-min target produced a 35-min actual unit and a 30-min target a 91-min
  one. Kept as `--job-seconds` (default 0) so the trade can be re-measured.
- **`--workers` defaults to the core count and the planner warns above it**,
  per the user's call.

Class-2 acceptance, same code, merger-clean 965/965 in every arm: sharded 350 s
/ 710 PASS; queue 24 workers 112 s / 707 (3.1x, 3 PASS->FAIL); queue 12 workers
180 s / 708 (1.9x, 2 PASS->FAIL). All differing entries are verified->timeout
at 23-27 s against the 30 s cap, and 2.3 e527/e528 are the pair this ticket
already found in September — borderline, not a queue defect.

**Left open:** the worker count per class. 24 costs one extra borderline entry
over 12 on class 2 and is 1.7x faster; the machine is 12 physical cores + SMT.
Settle it on class 1 with `ab_records.py`, not wall clock, since it is a
fidelity decision. Also unmeasured: class 1 and class 3 through the queue.

