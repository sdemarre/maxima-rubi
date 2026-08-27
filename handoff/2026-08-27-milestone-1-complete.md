# Handoff — maxima-rubi, milestone 1 complete (2026-08-27)

Milestone 1 (foundation + the algebraic-function class) is **CLOSED**.
Acceptance, user-confirmed 2026-08-27: **19,731/25,697 (76.8 %) of the
class-1 corpus PASS vs the T3 `integrate` baseline of 49.8 % (12,798)**,
no unexplained regressions — all 16 PASS->FAIL A/B remainders triaged to
tickets: the 9 slow-correct forms proved budget-limited by the 300 s
re-check, the 7 matcher-state entries a measured Maxima boundary (6
verified->timeout + 1 verified->deferred), the 3 no-answer->unexpected
corpus-limitation improvements. The post-milestone
workstreams (ticket 04, the section-9.3 port, the ticket-02 mailing-list
repro, ticket 05) were NOT pulled into milestone scope (user decision
2026-08-27: all post-milestone).

## Where everything lives

- Repo: `/home/serge/src/maxima-rubi`, default branch `master` (no
  `main`), **no remote configured — never `git push`**, no
  `Co-Authored-By` trailers. Milestone 1 was executed in the worktree
  `/home/serge/src/maxima-rubi/.worktrees/milestone-1` (branch
  `milestone-1`); merge state at close: see `git log` on that branch —
  the close commit is the last one.
- Plan (Tasks 1–10, all ticked):
  `docs/superpowers/plans/2026-08-20-milestone-1-implementation.md`.
- Ledger (the running record; read the tail): `.superpowers/sdd/progress.md`.
- Research design + milestone definition:
  `docs/superpowers/specs/2026-08-17-maxima-rubi-research-design.md`
  (§1 milestone definition, §8 done-when — all met).
- Acceptance record (committed): `test/corpus_class1.out`
  (19,731 passed / 5,966 failed; commit `45fc9b8`); run-5 A/B baseline
  `test/corpus_class1.run5-accept.out` (`98128c0`); the 300 s re-check
  `test/corpus_class1.timeout5m.out` + `test/timeout_rerun_merge.out`
  (`0c5b6b1`).
- Measured uplift record (trajectory, class table, A/B anatomy,
  re-check, cap policy): `docs/corpus-baseline-uplift.md`.
- Open tickets (all post-milestone): `.scratch/class1-ab-remainders/`
  (`spec.md` + `issues/01..05`). Statuses: 01 resolved-by-policy (known
  remainder); 02 needs-triage (Maxima boundary; mailing-list repro);
  03 needs-triage (corpus limitation); 04 **ready-for-agent** (matcher
  backtracking feasibility — the big lever on the 4,361 deferred
  entries); 05 needs-triage (38 heap-exhausted at the SBCL 1 GB default
  cap, 6 control-stack, 3 a driver `zero_chain` bug with a proposed
  fix).

## Measured state (all on Maxima 5.50.0 / SBCL 2.6.7, build date
2026-08-20 21:36:22 — the installed build; every claim below is stamped
in its source record)

Uplift trajectory (same 25,697 entries, 30 s per-entry cap, 24 shards):

| state | date (UTC) | passed | % |
|---|---|---|---|
| T3 `integrate()` baseline | 2026-08-18 | 12,798 | 49.8 |
| run 4 (rules core, 3,026 rules) | 2026-08-26 | 16,103 | 62.7 |
| run 5 (+ matchreverse pass-2 rescan) | 2026-08-27 | 18,588 | 72.3 |
| **accepted (run 5 + Phase A implicit-1 + Phase B 9.1 port + fixes)** | **2026-08-27** | **19,731** | **76.8** |

Accepted-run class split (from `test/corpus_class1.out`'s summary
block): verified 19,644 / deferred 4,361 / timeout 787 / unverified
643 / contains-noun 145 / expected 62 / error 27 / no-answer 25 /
unexpected 3. Rule set: 3,055 rules (67-file class-1 port + five
1.2.1 `b`-suffixed corpus-tested siblings + `9_1.mac`'s 29 rules);
accepted core fingerprint `f1f0611f803b7b8799853e28e2e1793b`
(`test/mr_rules.core.stamp`).

T5's open measurements, closed with values:

- **Load wall.** The TLS pattern cap is a hard per-process limit and is
  UNCHANGED on 5.50.0 (re-probed 2026-08-20/21: 1200 load / 1600 die;
  5.50's matcher-speed gains do not raise it). The resolution:
  `--tls-limit 100000` on every rule-loading process (user decision
  2026-08-22) + the option-D rules core (a prebuilt image the per-entry
  subprocesses load instead of recompiling patterns: entry-time avg
  1.76 s vs 9.69 s — 5.5x; full-class-1 wall 46 min no-9.1, ~82 min
  accepted A+B).
- **Recursion cap.** `%mr_max_depth : 16`
  (`maxima_rubi_utils.mac:73`), set against corpus-observed recursion
  depth; Layer A 511/0 at the cap.
- **Zero chain.** Final harness state: two-point numeric stage leading,
  then both exact stage orders, the whole chain errcatch-wrapped
  (ledger 2026-08-25/27). Residual: 643 unverified (2.5 %) at 30 s —
  the verify-gap workstream; the re-check's 88 are its
  budget-starved core.
- **30 s cap.** STAYS the standard (user decision 2026-08-27). The
  route for slow-correct entries is matcher speed (ticket 04), not
  budget; the timeout re-check is the standing verification (555 of
  787 re-run timeouts are genuine non-terminators at 300 s).

## Open items (post-milestone, in priority order suggested by the
measurements)

1. **Ticket 04 — matcher backtracking feasibility** (ready-for-agent).
   The installed matcher (matrun.lisp `findfun`) picks the first
   matching factor with no backtracking; the port works around it
   (pass-2 rescan, D-duplication, 9.1), and the workarounds cost
   coverage. The stratified recovery count over the 555
   still-timeout families (ledger 2026-08-27) is the go/no-go number.
2. **Classes 2+ as a repeatable process** — the generator
   (`generator/generate_class1.py`) + the loader's LoadRules list are
   the seam: a new class is a new pinned-file set + generator run +
   loader list + corpus section. The full loaded Rubi set is 7,432
   rules (T1 count) against class 1's 3,055.
3. **Ticket 05 — harness fixes**: the driver `zero_chain` interior-
   `integrate` guard (3 deaths); the SBCL 1 GB default dynamic-space
   cap probe (38 deaths); the 6 control-stack deaths (possible
   ticket-02 interaction — check against a no-9.1 core).
4. **Ticket 02 — mailing-list repro** of the measured Maxima
   compiled-matcher boundary (the 7 matcher-state 0-fires).
5. **Section-9.3 port** (research design §9.3).
6. **Elliptic-answer verification risk (T4 §2):** `elliptic_f/e/pi`
   are emitted as NATIVE answer-side nouns; verification relies on
   this build's `diff` knowing the native derivatives (measured
   2026-08-24). Re-verify on any build change before trusting
   elliptic-bearing answers.
7. Known remainder (ticket 01): the 9 slow zero-chain forms —
   budget-limited, correct; the zero-chain-form workstream.
8. Corpus limitation (ticket 03): the 3 entries the package now
   integrates numerically correctly but the 2018 corpus calls
   `Unintegrable`.

Note: the plan's "5.50 re-measurement" open item is closed by this
milestone — every acceptance measurement above is taken on 5.50.0
(itself the re-measurement the 5.49-era research docs anticipated).

## Known-derived predicate

`%mr_possible_zeroQ` (`maxima_rubi_utils.mac:453`) — referenced but
UNDEFINED in the pinned Rubi clone; derived from usage, flagged. Its
loose reading ("fire when the condition could hold") was REJECTED for
`%mr_eqQ` after the 2026-08-24 mass misfire (19,454 FAILs —
zero-substitution of every variable symbol over-fired the EqQ guards);
`%mr_eqQ` is now strict (`u-v` simplifies to 0) and `%mr_neQ` is
"not provably zero" (`is(u-v=0) # true`). Any future port that imports
a `PossibleZeroQ` call must keep the strict/loose distinction
deliberate.

## Operational notes (measured, still live)

- The accepted rules core is `test/mr_rules.core` @ fingerprint
  `f1f0611f803b7b8799853e28e2e1793b` (gitignored — rebuild with
  `bash test/build_rules_core.sh` only after rule edits; the driver
  refuses a stale core).
- Never modify `test/mr_rules.core` or any rule file while a sharded
  run is in flight (the run-6 contamination incident, ledger).
- Layer A: 511 targets (green at close: `Results: 511 passed,
  0 failed`). Full run: ~80-82 min on 24 shards. Canary:
  `python3 test/canary.py` (60 s/target) — biased toward
  currently-failing targets; the full-run A/B is the real gate.
- Rule-loading processes need `-X "--tls-limit 100000"` (two argv
  tokens).
- The installed Maxima's source tree is on this box (`~/src/external/
  maxima` per the ledger's 5.50.0 re-probe note) — the ticket-04
  matcher-path map reads `matrun.lisp`/`matcom.lisp` there.
- Reference clones are gitignored read-only: `reference/rubi` @
  `61e9c18ea248061cd83c67882f7c91a73cef912d`,
  `reference/maxima-syntax-test-suite` @
  `60295e21c571ca210ecfbb695f4af99947454adf`,
  `reference/rubi-5` @
  `37a71d650aa1ff7903d4de9cdd1a20c115969f4d` (pins also in
  `todo/TODO.md`).
