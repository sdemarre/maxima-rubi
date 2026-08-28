# Port the harness-radcan-fallback fixes into the generalized driver; re-measure class-1 and class-2

Status: resolved
Resolved: 2026-08-28 — port `5035d4e`; merges `2f6ca1e` (harness-port) /
`60c6f94` (harness-radcan-fallback, the `corpus_class1_driver.py`
conflict resolved to the shim); re-measurement records `f8d2fde`
(class-1 20,069 / class-2 594 + both 300 s re-checks); docs `f146b35`
(uplift §8, TODO, handoff). Final gates green (Layer A 581/0, driver
guard 4/4).
Filed: 2026-08-28 (milestone-2 merge, commit 6bd782d; sequencing decision: pilot landed as measured, harness next)
Evidence: branch `harness-radcan-fallback` (5 commits on 55724a6, not yet merged);
`docs/ratsimp-zero-divisor-bug.md`, `docs/corpus-radcan-fallback-attribution.md`
(both committed on that branch); milestone-2 acceptance
`docs/corpus-class2-baseline-uplift.md`.

## What

The branch `harness-radcan-fallback` (in the main worktree, with an
uncommitted class-1 record re-run in progress) carries two zero-chain
fixes to the M1 driver that the milestone-2 generalization did NOT
inherit:

1. `fe7f1c8` — zero-test `radcan(rat())` fallback: **+366 PASS** on the
   class-1 A/B (of the 370 fallback-rescued entries: 23 crash victims,
   344 gap-closures, 3 budget; see that branch's attribution doc).
2. `5e451d8` — the `freeof` gate: the list-first-arg form was a **silent
   no-op**; the fix is the list-first-arg form's correction.

milestone-2's `test/corpus_driver.py` is a generalization of the
PRE-FIX M1 driver, so both fixes are missing from the driver that now
backs BOTH classes' corpus runs. The milestone-2 class-2 acceptance
(500/965; 125 `unverified`) was measured with the no-op gate in place —
part of that 125 may close under the fixed chain.

## Scope

1. Port both fixes from `harness-radcan-fallback`'s
   `test/corpus_class1_driver.py` into `test/corpus_driver.py`
   (the zero-chain code is the shared surface; keep the milestone-2
   deltas — head rewrites, suite-dir positional, shard-file chunks —
   intact).
2. Merge `harness-radcan-fallback` into master: the conflict in
   `test/corpus_class1_driver.py` (its in-place fixes vs the milestone-2
   shim) resolves to the SHIM once step 1 has landed the fixes into
   `corpus_driver.py`; the branch's research docs + probes + new
   class-1 record merge as-is. Commit the in-progress class-1 record
   re-run on that branch first (it is the branch's acceptance evidence).
3. Re-measure on the fixed chain (house rule: baselines are
   re-measured, not carried over): full class-1 (25,697) and full
   class-2 (965) runs via the runbook
   (`docs/class-porting.md` Steps 8-9 mechanics, both sections), plus
   the standing 300 s timeout re-checks. The class-2 uplift record's
   numbers (500/965, the 125 `unverified`, the 178-decline residue
   split) are HISTORICAL measurements, stamped as such; the re-run
   produces the corrected acceptance.
4. Update `docs/corpus-class2-baseline-uplift.md` /
   `todo/TODO.md` / the handoff only if the re-measured acceptance
   changes the stated numbers (add a re-measurement section rather
   than rewriting the stamped history).

## Notes

- The heap-exhaustion bug (2.3 e56/e57/e68) and the 178-decline
  coverage work are SEPARATE tickets (file under the class-2 follow-up
  slug when the classes 3-8 runbook tickets are cut); they are not
  part of this port.
- Layer A stays the per-change gate during the port
  (`Results: 581 passed, 0 failed` at 6bd782d).
