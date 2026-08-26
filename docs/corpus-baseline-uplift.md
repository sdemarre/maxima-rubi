# Class-1 corpus — rubi() uplift acceptance record (2026-08-26)

The milestone-1 acceptance run: the full 25,697-entry class-1 corpus
under the ported rule set (`rubi()`, rules-only default), on the final
harness (option-D rules core + cost-aware 24-shard planner). Inputs:

- `test/corpus_class1.out` — the merged record (25,697/25,697 entries,
  40 files, no dupes/missing/extra; build-stamped header);
- `test/full_core_merge.out` — the merge transcript (rc=0);
- `docs/corpus-baseline.md` (T3) — the `integrate()` baseline this
  uplifts against;
- `.superpowers/sdd/progress.md` — the run history (run 1 mixed-state,
  run 2 killed, run 3 load-bound, the core run).

Build for the measurement: Maxima 5.50.0 (build date 2026-08-20
21:36:22), SBCL 2.6.7, x86_64-pc-linux-gnu (stamped in the record's
header). Code state: `85b7585` (branch milestone-1). Rule set: 3,026
rules (the 67-file class-1 port + the five corpus-tested 1.2.1 sibling
files; ledger 2026-08-25), rules-core fingerprint
`5998e8712f69f016a2baa67efc0c546c`.

## 1. The run

Final clean run (rules core, 24 processes, cost-balanced shards):
2026-08-26 20:24 -> 21:11 UTC, **46 min wall**. Heaviest shard 2,752 s
wall (plan estimate 3,847 s; balance spread 1.03x). Prior full runs on
the same 25,697 entries: run 3 (standard per-entry load, 18
count-balanced shards) = **13.2 h wall**, entry-time total 249,000 s
(avg 9.69 s/entry — ~6.2 s of it the per-entry rule load, paid by every
entry because the harness runs one fresh maxima process per integral);
the core run's entry-time total is 45,275 s (avg 1.76 s) — **5.5x on
entry-time, 17x on wall** on the same box.

## 2. Results (25,697 entries)

| class         | count | %     | verdict |
|---------------|-------|-------|---------|
| `verified`    | 16,041 | 62.4 | PASS |
| `deferred`    |  8,671 | 33.8 | FAIL |
| `timeout`     |   433 | 1.7 | FAIL |
| `unverified`  |   362 | 1.4 | FAIL |
| `contains-noun` | 111 | 0.4 | FAIL |
| `error`       |    14 | 0.1 | FAIL |
| `expected`    |    34 | 0.1 | PASS |
| `no-answer`   |    28 | 0.1 | PASS |
| `unexpected`  |     3 | 0.0 | FAIL |

**Results: 16,103 passed (62.7%) / 9,594 failed.**

## 3. Uplift vs the T3 integrate() baseline

T3 (`corpus-baseline.md` §3.1): verified 11,313 + expected 1,485 =
**12,798 (49.8%)** with a verified antiderivative from today's
`integrate`.

`rubi()`: verified 16,041 + expected 34 = **16,075 (62.6%)**.

**Uplift: +3,277 entries (+12.8 percentage points of the corpus).**
The verified+expected total is the comparison: the corpus driver checks
the self-diff before the expected-diff, so the verified/expected split
differs from T3's driver (T3 saw most matches land in `expected`; the
corpus driver lands them in `verified`).

The 31 corpus noun-expected entries: 28 `no-answer` (correctly
declined — PASS) + 3 `unexpected` (the package answered where the
corpus says non-integrable — the T5 disagreement watchlist).

## 4. The FAIL profile

- **deferred 8,671 (91% of all FAILs)** — the rule set declines
  (top-level 0-firing -> the `mr_unintegrable` noun on an
  answer-expected entry). Coverage gap, not wrong answers. Known
  components (ledger 2026-08-25/26): the unported N-factor matcher
  families (1.1.3.2/4/6/8, 1.2.3.x, 1.4.x — 922 rules), the remaining
  C-tier predicate surface, the 1.1.1.4 m/(Sqrt Sqrt Sqrt) matchfix
  pattern limit, and the documented suite-generation-vs-faithful-port
  gap (e.g. the 97 1.1.3.3 entries whose corpus expectations Rubi 4 at
  the pin cannot reproduce).
- **timeout 433** — 30 s cap. The canary-level analysis (ledger
  2026-08-25) found the sampled timeouts are verification-cost or
  wrong-answer cases, not package speed.
- **unverified 362** — answered but the zero-chain (incl. the two-point
  numeric stage) does not close; the verify-gap family.
- **contains-noun 111** — the answer carries the `unintegrable`
  residue (faithful Rubi `CannotIntegrate` markers and cascade
  coverage gaps).
- **error 14** — see §5.

## 5. The 14 error entries

1.1.1.2 e1700/e1702/e1712/e1723; 1.1.3.4 e156/e164/e172; 1.2.1.2
e1163/e1165/e2530/e2537/e2538/e2545; 1.2.2.3 e111. Eight are stable
across run 3 (load-bound) and this core run; four run-3 errors
(1.2.1.2 e2531/e2544, 1.3.2 e870/e871) did not recur and six are new —
the class is partially timing-sensitive (Maxima lisp errors in deep
evaluation, not rule mismatches). Triage pending.

## 6. Parity of the harness change (option D)

Run 3 (standard per-entry load) and the core run differ in exactly
three classes: timeout 438 -> 433, unverified 359 -> 362, error 12 ->
14 — five borderline entries whose 30 s budget the 6.2 s load used to
consume now finish. The other six classes are identical, verified
16,041 = 16,041: the rules image changes *how* rules load, not *what*
loads. 120-target canary parity (core vs standard): zero
classification diffs, ~10x faster on the core.

## 7. Standing cost and re-run discipline

- Full class-1: **46 min wall on 24 cores** (rules core, cost-balanced)
  — vs 13.2 h for the load-bound run on the same box. The per-change
  gate remains Layer A (511/0 at `85b7585`) + the 120-target canary.
- Re-run recipe: `test/build_rules_core.sh` (the driver's staleness
  guard auto-rebuilds the core on rule drift instead),
  `python3 test/launch_class1_shards.py --launch` (24 procs,
  cost-balanced from the previous merged `.out`), then the watcher
  merges to `test/corpus_class1.out`. The 30 s per-integral cap stayed
  at T3's arbitrary value; the measured distribution (max entry 30.1 s
  = the cap itself) suggests a tuned cap waits on the timeout triage.
