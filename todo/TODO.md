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

## Milestone 3 — class 3 (logarithms) — closed 2026-08-30

The first full runbook instantiation (`docs/class-porting.md`
Steps 1–10 executed end-to-end; plan
`docs/superpowers/plans/2026-08-29-milestone-3-class3.md`, Tasks 1–11
done, branch `milestone-3`). Measured acceptance (3,085-entry
class-3 corpus, 30 s cap): **`integrate` baseline 1,441/3,085
(46.7 %) vs package 1,736/3,085 (56.3 %) — the first class where the
package beats the baseline** (+295, +9.6 pt; of the 525 PASS→FAIL,
343 genuine declines (329 `deferred`) + 182 yardstick
reclassifications; FAIL→PASS 820; 96 confirmed non-terminators at
the 100 s re-check, zero slow-correct answers). Record:
`docs/corpus-class3-baseline-uplift.md` (run
`test/corpus_class3.campaign-baseline.out` — committed at `f40d56b`
as `test/corpus_class3.out`, which since the class-3 deferred campaign
close holds the campaign record (below); baseline
`test/corpus_class3.baseline.out`, 100 s re-check
`test/corpus_class3.timeout-rerun/`). The 2026-08-29 rebuild
(`branch_5_50_base_84_g4204fb669`, built 2026-08-29 17:58:20, SBCL
2.6.7) is the measurement build for all class-3 numbers (record
headers are the stamp; the AGENTS.md 2026-08-20 stamp is superseded
for class 3); the class-1 (20,069/25,697) and class-2 (594/965)
accepted records stand under it — no-op slices 51/51×2 on the new
build + 3,513-rule core, zero diffs (record §6).

Open follow-ups (tickets against the runbook):

- Class 8 (special functions, 1,949 entries — shares class 2's head
  table) — open, `.scratch/class-ports/issues/01-class8-special-functions.md`
- Class 5 (inverse trig, 4,585 entries) — open,
  `.scratch/class-ports/issues/02-class5-inverse-trig-functions.md`
- Class 6 (hyperbolic, 5,080 entries) — open,
  `.scratch/class-ports/issues/03-class6-hyperbolic-functions.md`
- Class 7 (inverse hyperbolic, 6,552 entries) — open,
  `.scratch/class-ports/issues/04-class7-inverse-hyperbolic-functions.md`
- Class 4 (trig, 22,472 entries — largest, deliberately last) — open,
  `.scratch/class-ports/issues/05-class4-trigonometric-functions.md`
- polylog derivative shim (the class-3 ceiling decision: the ceiling
  does NOT stand — 638 unverified+deferred polylog-expected entries,
  53.4 % of the 1,195-entry mass) — open, research,
  `.scratch/class3-polylog-ceiling/issues/01-polylog-derivative-shim.md`
- Zero-chain verification-stage OOMs + matching control-stack
  overflow (13 OOMs + 2 control-stack deaths across the class-3
  run/re-check; `rubi()` alone answers the OOM entries — the blowup
  is the 8-stage verification chain at the 1 GiB cap) — open,
  research, `.scratch/class3-verification-stage-oops/issues/01-
  zero-chain-verification-stage-oops.md`
- `AlgebraicFunctionQ` 3-arg mis-arity (3 generated rules; 3.3 e492
  `error` in the accepted record) — ready-for-agent,
  `.scratch/class3-algebraicfunctionq-arity/issues/01` (blocks
  nothing — the class-3 record stands with e492 as a known error)
- PowerOfLinear semantics revisit — conditional (unchanged from M2):
  the strict reading is decline-consistent with upstream; revisit
  only if a follow-up class shows the shapes material
- Class-2 deferred-residue ticket (the 2.3 commented-out rules as a
  coverage source) — needs-triage,
  `.scratch/class2-deferred-remainders/issues/01`
- Class-1 A/B remainder tickets (5 open: 01/02/03/05 needs-triage,
  04 partially answered by the class-3 deferred campaign — see below)
  — `.scratch/class1-ab-remainders/issues/`
- SBCL heap exhaustion on quotients of exponentials (class-2 2.3
  e56/e57 under the 300 s re-check, e68 in the run; reproducible) —
  open; related but distinct from the class-3 verification-stage OOM
  ticket above (M2's locus is matching, M3's measured locus is the
  verification stage)
- Branch `maxima-zero-divisor-rootcause` (unmerged; ratsimp
  zero-divisor root-cause probe work) — a separate thread, not part
  of the class-port queue

## Class-3 deferred campaign — closed 2026-09-12

The follow-up to milestone 3's deferred remainder (the 1,033 class-3
`deferred` entries, target mass 788 / certain 329): spec
`docs/superpowers/specs/2026-08-30-class3-deferred-campaign-design.md`,
plan `docs/superpowers/plans/2026-08-30-class3-deferred-campaign.md`,
branch `class3-deferred`. Pass 4 (the backtracking sweep) measured and
NOT wired (cost gate); 11 port sub-briefs landed (B1–B4, C1–C6b). Closed
at its current state by user decision 2026-09-11 — the five remaining
C6 mechanism groups are superseded by the matcher substrate (spec
`docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`).
Measured close (30 s cap, build 2026-08-31 13:27:47, core `5ef9b3bc`):
**class 3 1,736 → 2,058 / 3,085 (66.7 %)**; of the 788 target entries
366 PASS (certain 329: 222); class 1 20,069 → 20,125 / 25,697; class 2
594 → 614 / 965. Every PASS→FAIL of the three A/Bs is attributed in the
record. Record: `docs/corpus-class3-deferred-uplift.md` (§4 fixes, §5
A/B + attribution + 100 s re-check, §6 recovery, §7 acceptance); runs
`test/corpus_class{1,2,3}.out` with the pre-campaign records kept as
`test/corpus_class{1,2,3}.campaign-baseline.out`. Ticket 04
(`.scratch/class1-ab-remainders/issues/04-…`) partially answered.

## Matcher substrate — in prog (Plan 3 executing)

Classes 1–3 re-hosted on a Mathematica-semantics matcher in place of
`defmatch` (spec
`docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`, phases
P0–P6). Plan 1 (P0–P2,
`docs/superpowers/plans/2026-09-12-matcher-substrate-plan1.md`) is
complete on branch `matcher-substrate`: P0 baseline records
`test/corpus_class{1,2,3}.pre-matcher.out` (PASS 20,125 / 614 / 2,058;
median per-entry wall 1.3 / 4.3 / 3.9 s — the P5 parity floor and
performance ceiling; class-3 same-core wall noise
`probes/matcher/05-p0-wall-noise.out`); `mr-match`
(`maxima_rubi_match.lisp`) and `mr-tree` (`maxima_rubi_tree.lisp`)
with unit suites 51/0 and 46/0; the P1/P2 regression gates green in
both simplifier arms (`test/matcher/gate.out`, `gate.flags.out`,
109/0). Suite commands: AGENTS.md, Tests. Ledger:
`.superpowers/sdd/progress.md` (plan 1 section).

Plan 2 (P3–P4,
`docs/superpowers/plans/2026-09-13-matcher-substrate-plan2.md`) is
complete on the same branch: the generator emits evaluated-FullForm
pattern records (`%mr_defrule`; 3,513 rules, 9.1 generated; P3 static
gate `test/check_generated_rules.py` 11/0);
`maxima_rubi_dispatch.lisp` dispatches on `mr-match` / `mr-tree` (unit
suite 57/0); passes 2–4, the `defmatch`-era matchers and
`maxima_rubi_implicit1.lisp` / `maxima_rubi_pass4.lisp` are deleted;
Layer A 898/0; the TLS flag is no longer required
(`probes/matcher/08-runtime-load.out`); dispatch cost
`probes/matcher/06-dispatch-cost.out`; fault survival
`probes/matcher/07-fault-survival.out`. Ledger: plan 2 section.

- Next: Plan 3 = P5 (four full class 1–3 runs, one switch flipped per
  run; gates against the P0 records) – P6 (close), written just in
  time — open
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
- Deferred: the `MX_` plist re-read issue in `mr-tree` (not reachable:
  the dispatcher never prints and re-reads a tree) — open
- Known cost item: a collapsible claimer (e.g. `(c_.*x_)^m_.` under
  Times) still enumerates every sub-run of a product's factors — the
  full-table walk on `x*y1*…*y12` takes minutes; on large products the
  walk is dominated by moved inner conditions that integrate or expand
  (3.5 r37, 3.1.5 r28, 3.5 r11) (`probes/matcher/06-dispatch-cost.out`)
  — open, judged by the P5 median-wall gate

## Pinned reference clones

- `reference/rubi` @ `61e9c18ea248061cd83c67882f7c91a73cef912d` (cloned 2026-08-17)
- `reference/maxima-syntax-test-suite` @ `60295e21c571ca210ecfbb695f4af99947454adf` (cloned 2026-08-17)
- `reference/rubi-5` @ `37a71d650aa1ff7903d4de9cdd1a20c115969f4d` (cloned 2026-08-17)
- `reference/fateman/lisp/mma4max` — Fateman's mma4max (assembled 2026-09-11;
  `reference/fateman/PROVENANCE.txt`): 19 files from the Wayback Machine
  snapshot of `people.eecs.berkeley.edu/~fateman/lisp/mma4max/` dated
  2022-01-18 (18 byte-identical to the mirror below; `init.lisp` is the
  Berkeley original), all other files from `nilqed/abcl_maxima` @
  `097b49b08aff958f72a3cf4449a7ac7912d9ef59` subdir `mma4max/`.
  `newmatch.lisp` listing date 2011-03-21.
- `reference/fateman/other/mixima` — `jlapeyre/mixima` @ `05e510b77bedae0841e81bfa3f5693fffaf7a53e`
- `reference/fateman/other/mockmma` — `dubrousky/mockmma` @ `036e7ba0773e43da50438a4f93774966cf82011f`
  (both copied 2026-09-11 without `.git`: the commits are recorded in
  `PROVENANCE.txt` only and cannot be re-read from the copies)
