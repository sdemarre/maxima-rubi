# Class-1 corpus — rubi() uplift acceptance record (accepted 2026-08-27)

The milestone-1 acceptance run: the full 25,697-entry class-1 corpus under
the ported rule set (`rubi()`, rules-only default), on the final harness
(option-D rules core + cost-aware 24-shard planner). This document was
first written at the 2026-08-26 state (16,103 / 62.7 %, 3,026 rules,
fingerprint `5998e8712f69f016a2baa67efc0c546c`); it is now the record of
the **accepted A+B run** (19,731 / 76.8 %, 3,055 rules, fingerprint
`f1f0611f803b7b8799853e28e2e1793b`). Inputs:

- `test/corpus_class1.out` — the merged record (25,697/25,697 entries,
  40 files, no dupes/missing/extra; build-stamped header, merged
  2026-08-27 13:02 UTC);
- `test/full_core_merge.out` — the merge transcript (rc=0);
- `test/corpus_class1.run5-accept.out` — the run-5 A/B baseline
  (18,588 / 72.3 %, commit `98128c0`);
- `test/corpus_class1.timeout5m.out` + `test/timeout_rerun_merge.out` —
  the 300 s re-check of the accepted run's 787 timeouts (commit `0c5b6b1`);
- `docs/corpus-baseline.md` (T3) — the `integrate()` baseline this
  uplifts against;
- `.superpowers/sdd/progress.md` — the run history and the A/B triage
  (sections dated 2026-08-26/27).

Build for the measurement (stamped in the records' headers): Maxima
5.50.0 (build date 2026-08-20 21:36:22), SBCL 2.6.7,
x86_64-pc-linux-gnu. Code state: the `89054b0` lineage (the 9.1 top-level
gate + collapse-rule exact seen check), acceptance record commit `45fc9b8`
(branch milestone-1). Rule set: 3,055 rules — the 67-file class-1 port,
the five corpus-tested 1.2.1 `b`-suffixed sibling files, and the section
9.1 integrand-simplification port (`rules/class1/9_1.mac`, 29 rules,
commit `9d9a3e7`).

## 1. Trajectory (same 25,697 entries, 30 s per-entry cap, 24 shards)

| state | date (UTC) | passed | % | rule set |
|---|---|---|---|---|
| T3 `integrate()` baseline | 2026-08-18 | 12,798 | 49.8 | (none — native `integrate`) |
| run 4 (rules core, first full core run) | 2026-08-26 | 16,103 | 62.7 | 3,026 |
| run 5 (+ matchreverse pass-2 rescan fix) | 2026-08-27 | 18,588 | 72.3 | 3,026 |
| **accepted run (run 5 + Phase A implicit-1 pass + Phase B section-9.1 port + the r11 top-level gate / collapse exact seen check)** | **2026-08-27** | **19,731** | **76.8** | **3,055** |

The T3 row is verified+expected (11,313 + 1,485) as measured in
`docs/corpus-baseline.md` §3.1; the rubi rows are the `Results:` pass
total (verified + expected + no-answer). The split differs by driver: the
corpus driver checks the self-diff before the expected-diff, so verified
answers that T3's driver landed in `expected` land in `verified` here
(accepted run: verified 19,644 + expected 62 = 19,706 verified+expected,
76.7 % — the apples-to-apples comparison against T3's 12,798).

**Uplift vs the T3 baseline: +6,933 entries (+27.0 percentage points of
the corpus, 49.8 % → 76.8 %).**

## 2. Results of the accepted run (25,697 entries)

From the `=== summary ===` block of `test/corpus_class1.out`:

| class         | count | %     | verdict |
|---------------|-------|-------|---------|
| `verified`    | 19,644 | 76.4 | PASS |
| `deferred`    |  4,361 | 17.0 | FAIL |
| `timeout`     |    787 | 3.1 | FAIL |
| `unverified`  |    643 | 2.5 | FAIL |
| `contains-noun` | 145 | 0.6 | FAIL |
| `expected`    |     62 | 0.2 | PASS |
| `error`       |     27 | 0.1 | FAIL |
| `no-answer`   |     25 | 0.1 | PASS |
| `unexpected`  |      3 | 0.0 | FAIL |
| **total**     | **25,697** | | **Results: 19,731 passed, 5,966 failed** |

## 3. A/B against run 5 — no unexplained regressions

Per-target A/B of the accepted run against
`test/corpus_class1.run5-accept.out` (run 5 = the 3,026-rule set +
pass-2 rescan, fingerprint `f1deb0c9…`; accepted = the 3,055-rule set,
fingerprint `f1f0611f…` — the delta is Phase A + Phase B + the two
fixes, all on the same 25,697 entries): 25,697 matched, **1,162
improvements, 19 regressions** — every one of the 19 is measured and
triaged into a ticket under `.scratch/class1-ab-remainders/issues/`:

- **16 PASS->FAIL remainders** (0.09 % of run-5's 18,503 verifies):
  9 verified->timeout CORRECT-BUT-SLOW — the 9.1 rules changed the
  quartic/trinomial-radical answer FORM; the zero chain on the new form
  runs 25-35 s, over the 30 s budget under 24-way load (ticket 01; the
  300 s re-check recovers all 9 at 31-71 s); 7 verified->
  timeout-or-deferred MATCHER-STATE — the 9.1 pattern load perturbs the
  installed Maxima's compiled-matcher state on a small set of family
  patterns, which then 0-fire; bisected to the Maxima boundary with
  three same-day control cores (ticket 02; the 300 s re-check confirms
  budget does not touch them).
- **3 no-answer->unexpected** (1.2.3.4 e86/e155/e156): the package now
  returns an answer the corpus expects to be `Unintegrable`; sampled
  |diff(ans)-f| ≤ 3e-10 at three points each — improvements the 2018
  corpus cannot accept (ticket 03).

## 4. The 300 s timeout re-check

The accepted run's 787 `timeout` entries were re-run exactly at a 300 s
per-entry cap (24 shards, same core; `test/corpus_class1.timeout5m.out`
+ `test/timeout_rerun_merge.out`, commit `0c5b6b1`; procedure now
in-tree: `test/launch_timeout_rerun.py` / `test/wait_timeout_rerun.sh` /
`test/merge_timeout_rerun.py`, commit `cdadb1a`):

- 90 now-PASS (88 verified + 2 expected), 11.4 % — **all 9 ticket-01
  slow-correct forms recover to verified at 31-71 s** under 24-way load:
  300 s is a sufficient budget for them, so they are budget-limited, not
  broken (ticket 01 comments);
- 555 still timeout at 300 s, 70.5 % — genuine non-terminators, not
  budget starvation (the 300 s cap barely shrinks the class);
- 88 unverified — an answer was found; the zero chain did not close in
  budget (the second lever is the verification chain, not the rule set);
- 47 error — subprocess deaths, all 47 censused individually (ticket 05):
  38 heap-exhausted at the SBCL default 1 GB dynamic-space cap, 6
  control-stack, 3 a harness `zero_chain` bug (numeric stage substitutes
  into an interior `integrate(g, x)` term);
- 5 deferred, 2 contains-noun — the 6 ticket-02 matcher-state entries
  sit in the deferred/timeout split (4 deferred after 44-127 s of wild
  cascade; e2572/e2573 non-terminating at 300 s): budget does not touch
  them — structural, confirming the ticket-02 reading.

Still-timeout hotspots (555, by family): 1.2.1.2 (85), 1.1.2.4 (75),
1.2.1.3 (67), 1.1.3.8 (42), 1.2.2.2 (41) — the input set for the
ticket-04 stratified sample.

## 5. The 31 corpus noun-expected entries

The corpus has 31 entries expecting `Unintegrable`/`CannotIntegrate`
(20 + 11; T3 saw 31/31 agreement from `integrate`). Accepted run,
per-entry join of the 31 lines against `test/corpus_class1.out`:

- 25 `no-answer` — PASS, correctly declined;
- 3 `contains-noun` (1.1.2.5 e103/e107/e110) — a partial reduction whose
  interior carries the `unintegrable` catch-all marker (the pinned Rubi's
  own reduction shape); the markers' integrands survive diff, so the zero
  chains cannot close;
- 3 `unexpected` (1.2.3.4 e86/e155/e156) — the ticket-03 improvements.

## 6. The FAIL profile

- **deferred 4,361 (73 % of all FAILs)** — the rule set declines
  (top-level 0-firing -> the `unintegrable[f, x]` noun on an
  answer-expected entry). Coverage gap, not wrong answers. The largest
  single lever is matcher backtracking (ticket 04, ready-for-agent):
  the 555 still-timeout families above are its stratified input.
- **timeout 787** — 30 s cap; the §4 re-check is the standing reading of
  this class (555 genuine non-terminators, 90 budget-limited, 88
  verification-chain, 47 deaths).
- **unverified 643** — answered but the zero chain (two-point numeric
  stage + both exact stage orders) does not close; the verify-gap family
  (the re-check's 88 are the budget-starved core of it).
- **contains-noun 145** — the answer carries the `unintegrable` residue
  (faithful Rubi `CannotIntegrate` markers and cascade coverage gaps).
- **error 27** — subprocess deaths in the accepted run; the re-check's
  47-death census (ticket 05) covers the class at scale, including the
  driver `zero_chain` fix candidate.
- **unexpected 3** — the §5 ticket-03 entries.

## 7. Standing cost and re-run discipline

- Full class-1: **~82 min wall on 24 cores** (accepted run, 2026-08-27
  11:40-13:02 UTC — the 9.1 rules lengthen the cascades of formerly-
  deferred entries; the 2026-08-26 no-9.1 run was 46 min). The per-change
  gate remains Layer A (`test_maxima_rubi.mac`, 511 targets) + the
  120-target canary; the full-run A/B is the regression gate (the canary
  is biased toward currently-failing targets and cannot gate
  verified-target regressions — ledger second lesson).
- Re-run recipe: `bash test/build_rules_core.sh` (only after rule edits —
  the driver's staleness guard refuses a mismatched fingerprint),
  `python3 test/launch_class1_shards.py --launch` (24 procs,
  cost-balanced from the previous merged `.out`), then the watcher
  merges to `test/corpus_class1.out`. Never modify the core or any rule
  file while a sharded run is in flight (the run-6 contamination
  incident, ledger 2026-08-27).
- **30 s per-entry cap policy (user decision 2026-08-27):** the cap
  STAYS the standard. The route for the slow-correct entries is matcher
  speed (ticket 04), not budget. When "is 30 s just at the limit?" is
  live again, the standing verification is the timeout re-check (§4
  procedure).
