# Handoff — maxima-rubi, milestone 2 (pilot) complete (2026-08-28)

Milestone 2 (pilot) is **CLOSED**: the class-porting pipeline was
generalized and proven end-to-end on class 2 (exponentials) — the
smallest class-2+ corpus section — so **classes 3–8 are runbook
tickets, not projects** (the pilot's scope was process-first, spec
§1). Measured acceptance (965-entry class-2 corpus, 30 s per-entry
cap, Maxima 5.50.0 / SBCL 2.6.7 — every claim stamped in its source
record): **`integrate` baseline 593/965 (61.5 %) vs package
500/965 (51.8 %)**; entry-level PASS→FAIL 309 = 178 genuine
`deferred` declines + 131 yardstick reclassifications, FAIL→PASS
216. Margin note: the baseline used the 4-stage probe yardstick
(noun-on-answer-expected = PASS), the package run the 8-stage driver
(`deferred`/`contains-noun` = FAIL) — the yardstick errs slightly
conservative for the package; a stricter comparison = re-run the
native baseline through the driver harness (not done, out of pilot
scope). The class-1 accepted record (19,731/25,697 = 76.8 % vs the
49.8 % T3 baseline) stands untouched.

## Where everything lives

- Repo: `/home/serge/src/maxima-rubi`, default branch `master` (no
  `main`), **no remote configured — never `git push`**, no
  `Co-Authored-By` trailers. Executed in the worktree
  `/home/serge/src/maxima-rubi/.worktrees/milestone-2` (branch
  `milestone-2`); design
  `docs/superpowers/specs/2026-08-28-milestone-2-class2-pilot-design.md`,
  plan (Tasks 1–11, all ticked)
  `docs/superpowers/plans/2026-08-28-milestone-2-class2-pilot.md`.
- Ledger (the running record; read the tail):
  `.superpowers/sdd/progress.md`.
- Acceptance records (committed): `test/corpus_class2.out` (package,
  965/965), `test/corpus_class2.baseline.out` (baseline, 965/965),
  `test/corpus_class2.timeout-rerun/corpus_class2.timeout5m.out` +
  `merge.out` (the 300 s re-check, 7/7).
- Measured acceptance record (trajectory, A/B anatomy, residues,
  ledger flags): `docs/corpus-class2-baseline-uplift.md`.
- The class-porting runbook (Steps 1–10 — the classes 3–8 template):
  `docs/class-porting.md`.
- Follow-up tickets (one per remaining class + the measured
  findings): `todo/TODO.md`, Milestone-2 section.
- Rule set: **3,180 rules** (3,055 class-1 + 125 class-2), core
  fingerprint `aa53741f7ac802e2c3b8bd93720b219d`
  (`test/mr_rules.core.stamp`, gitignored — rebuild with
  `bash test/build_rules_core.sh` only after rule edits; the driver
  refuses a stale core).

## Measured state (all stamped in the source records)

Accepted-run class split (from `test/corpus_class2.out`'s summary
block): verified 320 / expected 116 / no-answer 64 / deferred 314 /
unverified 125 / contains-noun 14 / timeout 7 / unexpected 4 /
error 1. The 300 s re-check of the 7 `timeout` entries: **error 2 +
unverified 5, now-PASS 0** — the 30 s cap is NOT the limit for class
2; none of the seven is slow-correct. Residues and their likely
causes (deferred 314 = rule coverage with per-file breakdown;
unverified 125 = largely the baseline-inherited verify gap; the 2
re-check `error`s + 2.3 e68 = the heap-exhaustion finding):
`docs/corpus-class2-baseline-uplift.md` §5.

### Post-pilot update — the radcan(rat()) fallback re-measurement
(2026-08-28)

The harness-radcan-fallback zero-chain fix (elliptic-gated
`radcan(rat())` fallback + the corrected `apply(freeof, …)` gate) was
ported into `test/corpus_driver.py` and merged to master
(`5035d4e`/`2f6ca1e`/`60c6f94`). Harness-only — no rule/package
change; the 3,180-rule core is untouched. Both classes re-measured on
it: **class-2 594/965 (61.6 %)** (was 500, +94, 0 regressions — 89
unverified→verified, 4 unverified→expected, 1 timeout→verified, 111
expected→verified; now at parity with the integrate baseline 593) and
**class-1 20,069/25,697 (78.1 %)** (was 20,066 on the 3,055 table;
+338 over the M1 19,731). Class-2 300 s re-check: 6/6, now-PASS 2
(e595, e610), 3 error (heap-exhaustion), 1 unverified, 0 still-timeout.
Full record: `docs/corpus-class2-baseline-uplift.md` §8. This is now
the going-forward zero chain for every class-N run.

## Open items (the follow-ups, in the runbook's order)

1. **Class 3** (logarithms, 3,085 entries) — runbook ticket, open.
2. **Class 8** (special functions, 1,949 — shares class 2's head
   table) — open.
3. **Class 5** (inverse trig, 4,585) — open.
4. **Class 6** (hyperbolic, 5,080) — open.
5. **Class 7** (inverse hyperbolic, 6,552) — open.
6. **Class 4** (trig, 22,472 — largest, deliberately last) — open.
7. **SBCL heap exhaustion on quotients of exponentials** — 2.3 e56 /
   e57 (error at 71.4 / 95.4 s under the 300 s re-check), e68 (error
   at 17.4 s in the run); reproducible, root cause not yet measured,
   matcher/rule-bug candidate — its own ticket. The pilot's
   principal finding.
8. **PowerOfLinear semantics revisit** — conditional: the strict
   reading is decline-consistent with upstream on the available
   evidence (undefined predicate → symbol → the same shapes decline
   in Mathematica too); revisit only if a follow-up class shows the
   shapes material.
9. **polylog/AppellF1 residue decision** — deferred to the first
   class that needs it (spec §3.4; class 2 measured: no rule emits
   them, the structural ceiling stands).

## Known carried minors (noted, not gating; not fixed in the pilot)

- The merged records carry no aggregate `head rewrites:` line — the
  merger skips per-shard stats lines (a pre-existing Task-8 behavior
  the class-1 merged record shares); the per-shard lines are on disk
  and sum to exactly the census counts (uplift §2).
- The residue→expected-head census (uplift §5) is a one-off join of
  the package record's unverified entry lines against the pinned
  suite files' expected texts — re-runnable (both inputs
  committed/pinned), not a committed probe; promote it if needed
  again.
- The A/B yardstick asymmetry was not re-measured through the driver
  harness (the margin note stands as the recorded reading).
- The ledger's "2.3 r1/r2" shorthand for the positive-TrueQ sites
  refers to generated rule numbers r2/r5 (the ledger is a working
  file, left as written; the committed docs use the generated
  numbering).

## Operational notes (measured, still live)

- Layer A: 581 targets (`Results: 581 passed, 0 failed` at close;
  grew 511 → 581 across the pilot's clusters); the head-rewrite unit
  suite `python3 test/test_head_rewrites.py` (7/0). Full class-2 run:
  ~8 min on 24 shards.
- Rule-loading processes need `-X "--tls-limit 100000"` (two argv
  tokens); the rules core is gitignored.
- The class-N mechanics: `docs/class-porting.md` Steps 8-9 are the
  baseline / package-run / re-check runbook; the AGENTS.md Tests
  section carries the class-2 run commands; the answer-side
  identities (the normalization's two conventions) are probed in
  `probes/answer-side/01-answer-side-identities`.
