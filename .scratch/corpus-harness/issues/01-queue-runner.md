# Corpus runs through one work queue instead of fixed shards

Status: needs-triage
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
