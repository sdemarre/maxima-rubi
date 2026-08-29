# TODO — index

One short entry per item: status + link. The questions to be answered
and the evidence live in the item's file. Items may reference each other.
Status: `open` / `in prog` / `done`.

| id  | title                            | status | item file                                  |
|-----|----------------------------------|--------|--------------------------------------------|
| T1  | Rubi anatomy                     | done   | [t1-rubi-anatomy.md](t1-rubi-anatomy.md)   |
| T2  | Pattern matching in Maxima       | done   | [t2-pattern-matching.md](t2-pattern-matching.md) |
| T3  | Corpus and Maxima baseline       | done   | [t3-corpus-baseline.md](t3-corpus-baseline.md)   |
| T4  | Rule translation (algebraic)     | done   | [t4-rule-translation.md](t4-rule-translation.md) |
| T5  | Package and harness architecture | done   | [t5-package-architecture.md](t5-package-architecture.md) |

Order: T1 first; T3's sample run in parallel with T1; T2 after T1;
T4 after T1 + T2; T5 last. See the design spec, section 5.

## Milestone 1 — closed 2026-08-27

Foundation + the algebraic-function class (plan
`docs/superpowers/plans/2026-08-20-milestone-1-implementation.md`,
Tasks 1-10 all done). Acceptance (user-confirmed 2026-08-27):
**19,731/25,697 (76.8 %) of the class-1 corpus PASS vs the T3
`integrate` baseline of 49.8 %**, no unexplained regressions. Record:
`docs/corpus-baseline-uplift.md` (accepted run
`test/corpus_class1.out`, commit `45fc9b8`); handoff
`handoff/2026-08-27-milestone-1-complete.md`; post-milestone tickets
`.scratch/class1-ab-remainders/`.

T5's open measurements, closed with values (Maxima 5.50.0 / SBCL
2.6.7):

- **Load wall** — the TLS pattern cap is unchanged on 5.50.0 (1200
  load / 1600 die, re-probed); resolution: `--tls-limit 100000` on
  every rule-loading process + the option-D rules core (entry-time
  avg 1.76 s vs 9.69 s; full-class-1 wall 46 min -> ~82 min as the
  rule set grew).
- **Recursion cap** — `%mr_max_depth : 16` (`maxima_rubi_utils.mac:73`),
  set against corpus-observed recursion depth.
- **Zero chain** — two-point numeric stage leading, then both exact
  stage orders, whole chain errcatch-wrapped; residual 643 unverified
  (2.5 %) is the verify-gap workstream.
- **30 s per-entry cap** — STAYS the standard (user decision
  2026-08-27); the timeout re-check (`test/launch_timeout_rerun.py`
  et seq.) is the standing verification (555/787 re-run timeouts are
  genuine non-terminators at 300 s).

## Milestone 2 (pilot) — closed 2026-08-28

The pipeline generalized and proven end-to-end on class 2
(exponentials), so classes 3–8 are runbook tickets (spec
`docs/superpowers/specs/2026-08-28-milestone-2-class2-pilot-design.md`,
plan `docs/superpowers/plans/2026-08-28-milestone-2-class2-pilot.md`,
Tasks 1–11 done, branch `milestone-2`). Measured acceptance (965-entry
class-2 corpus, 30 s cap): **`integrate` baseline 593/965 (61.5 %) vs
package 500/965 (51.8 %)** (PASS = {expected, verified, no-answer}; of
the 309 PASS→FAIL, 178 are genuine `deferred` declines and 131 are
yardstick reclassifications — the probe-vs-driver yardstick errs
slightly conservative for the package, plan Task-10 margin note).
 Record: `docs/corpus-class2-baseline-uplift.md` (run
 `test/corpus_class2.out`, baseline `test/corpus_class2.baseline.out`,
 300 s re-check `test/corpus_class2.timeout-rerun/`); runbook:
 `docs/class-porting.md`. The class-1 accepted record stands untouched,
 as of the pilot close.

 Post-pilot (2026-08-28): the harness-radcan-fallback zero-chain fix
 (elliptic-gated `radcan(rat())` fallback + corrected `apply(freeof, …)`
 gate) was ported into `test/corpus_driver.py` and both classes
 re-measured on the 3,180-rule core under the fallback chain — a
 verification-harness change only (rules/package unchanged). Re-measured
 acceptance: **class-2 594/965 (61.6 %)** (was 500, +94, 0
 regressions; now at parity-with-the-integrate-baseline 593) and
 **class-1 20,069/25,697 (78.1 %)** (was 20,066 on the 3,055 table,
 +338 over the M1 19,731). Record: `docs/corpus-class2-baseline-uplift.md`
 §8; runs `test/corpus_class1.out` / `test/corpus_class2.out` (+
 `.pre-…` pre-snapshots), 300 s re-checks
 `test/corpus_class{1,2}.timeout-rerun-2026-08-28/`. Merged to master
 (`5035d4e`, `2f6ca1e`, `60c6f94`). The zero chain is now the harness
 for every class-N run.

 Open follow-ups (tickets against the runbook):

- Class 8 (special functions, 1,949 entries — shares class 2's head
  table) — open
- Class 5 (inverse trig, 4,585 entries) — open
- Class 6 (hyperbolic, 5,080 entries) — open
- Class 7 (inverse hyperbolic, 6,552 entries) — open
- Class 4 (trig, 22,472 entries — largest, deliberately last) — open
- polylog/AppellF1 residue decision — deferred to the first class
  that needs it (spec §3.4; class-2 measured: no rule emits them, the
  structural ceiling stands)
- PowerOfLinear semantics revisit — conditional: the class-2 residue
  shows the strict reading is decline-consistent with upstream (the
  upstream condition is an undefined predicate → a symbol → the same
  shapes decline in Mathematica too); revisit only if a follow-up
  class shows the shapes material
- SBCL heap exhaustion on quotients of exponentials (2.3 e56/e57
  error at 71.4/95.4 s under the 300 s re-check, e68 error at 17.4 s
  in the run; reproducible; matcher/rule-bug candidate) — open, its
  own ticket
- Class-2 deferred residue (178 genuine declines: 2.3 154, 2.2 18,
  2.1 6 — all `deferred`) — ticket store
  `.scratch/class2-deferred-remainders/` (ticket 01: the 5
  commented-out rules in Rubi's `2.3 Miscellaneous exponentials.m` —
  incl. the two recursive quotient-of-exponentials reductions — as a
  candidate coverage source; needs-triage)
- Branch `maxima-zero-divisor-rootcause` (unmerged; ratsimp
  zero-divisor root-cause probe work, tip `e185953`) — a separate
  thread, not part of the class-3 path; `master` is the working
  branch

## Milestone 3 — class 3 (logarithms), not started

The next port: section "3 Logarithms" (3,085 entries), first of the
runbook queue. A new session starts here: runbook
`docs/class-porting.md` Step 1 (census); its standing constraints bind
(byte-identity gate for accepted classes 1–2, 30 s per-entry cap, 100 s
timeout re-check, A/B vs the `integrate` baseline, an acceptance record
per the class-2 template `docs/corpus-class2-baseline-uplift.md`). The
only mechanical harness change: the core-fingerprint file lists gain
`rules/class3/*.mac` on both sides (`test/build_rules_core.sh`,
`test/corpus_driver.py` `_core_fingerprint`); the driver rebuilds the
core itself when the fingerprint goes stale. Queue after class 3:
8 → 5 → 6 → 7 → 4 (class 4 last, deliberately).

## Pinned reference clones

- `reference/rubi` @ `61e9c18ea248061cd83c67882f7c91a73cef912d` (cloned 2026-08-17)
- `reference/maxima-syntax-test-suite` @ `60295e21c571ca210ecfbb695f4af99947454adf` (cloned 2026-08-17)
- `reference/rubi-5` @ `37a71d650aa1ff7903d4de9cdd1a20c115969f4d` (cloned 2026-08-17)
