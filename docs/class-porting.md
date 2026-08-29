# Class porting — the runbook

The repeatable process for porting one Rubi rule class to
`maxima-rubi`, **as executed for class 2 (exponentials) on
2026-08-28** (branch `milestone-2`, `b78d5aa..bb74cb6`). The
milestone-2 pilot's deliverable is this runbook: **classes 3–8 are
tickets against it** — a reader should be able to port a class from
this document alone, with the per-step acceptance checks as the
definition of done. The class-2 execution evidence for every step is
cited (ledger task + artifact); the measured-claims discipline
(AGENTS.md) applies to the follow-ups exactly as it applied to the
pilot.

Spec: `docs/superpowers/specs/2026-08-28-milestone-2-class2-pilot-design.md`
(commit `ff814e9`). The pilot's measured acceptance record:
`docs/corpus-class2-baseline-uplift.md`.

## Standing constraints (apply to every class, read first)

1. **TLS flag.** Every maxima process that loads rule files runs with
   `-X "--tls-limit 100000"` — **two argv tokens, not
   `--tls-limit=N`** (user decision 2026-08-22). The load-wall probes
   self-flag if the build moves (`probes/load_wall/probe-tls-calibration.out`,
   `probe-load-curve.out`; the pilot's full-table probe
   `probes/load_wall/probe-class2-load.{run,out}` — re-run it per class,
   it prints `TABLE_AT_LOAD <n>`).
2. **30 s per-entry cap STAYS the standard** (user decision
   2026-08-27). The route for slow-correct entries is matcher speed,
   not budget. The standing answer to "is 30 s at the limit?" for any
   merged record is the **timeout re-check**: re-run exactly the
    record's `timeout` class at a 100 s cap and read the transitions
   (now-PASS = slow-correct; still-timeout = genuine
   non-terminators; unverified = the chain, not the budget; error =
   subprocess-death census).
3. **Byte-identity gate for every class already accepted.** Before
   proceeding past Step 3 (and once more at close), regenerate every
   accepted class and require an empty `git status --porcelain
   rules/`. Any drift is a process bug, fixed before proceeding — the
   accepted records and their core fingerprints must stay reproducible
   from the new code.
4. **Reading protocol.** Every run ends with `Results: <n> passed,
   <m> failed` — read that line; a mid-run death prints no Results
   line and is itself a failure. Every corpus merge asserts
   completeness against the section entry count (N/N, no
   dupes/missing/extra).
5. **Measured-claims discipline.** Every non-trivial claim cites a
   committed, re-runnable probe under `probes/`; counts and timings
   are stamped with the date and the Maxima build (`build_info()`).
   The project does not pin to a build — baselines are re-measured on
   upgrade, never carried over (current build: 5.50.0, build date
   2026-08-20 21:36:22, SBCL 2.6.7).
6. **Git.** Default branch `master`; no remote configured — never
   `git push`; no `Co-Authored-By` trailers; one commit per task step
   group; the SDD ledger gets an entry per task (measurements,
   deviations, findings).

## Step 1 — Census (rule set + answer heads)

**What.** Two static censuses, no Maxima: (a) the rule-syntax census
over the class's `Rubi.m`-loaded files — file/rule counts, the
optional-capture histogram, the AUTO/MANUAL split, the
condition/replacement token table, and the **UNLISTIED token list**
(the closure to be decided); (b) the section's answer-head census over
the corpus files (distinct-head occurrences on entry lines) — the
input to Step 7's `HEAD_REWRITES` table.

**Commands (class-2 as executed).**
```
sh probes/translation/03-class2-syntax-census.run     # = python3 probes/translation/01-class1-syntax-census.py reference/rubi "2 "
sh probes/corpus/02-class2-answer-heads.run           # = python3 probes/corpus/02-class2-answer-heads.py
```
(Committed record naming: `probes/translation/<n>-classN-syntax-census.{run,out}` —
02 is taken by the support-surface probe, hence 03; `probes/corpus/<n>-classN-answer-heads.{py,run,out}`.)

**Token closure.** Every UNLISTIED token is adjudicated before any
generation: new tokens → table entries (Step 2) or ports (Step 4);
**upstream-undefined utilities → the call-site contract + documented
decline-safe semantics** (class-2: the `PowerOfLinear` family is
defined nowhere in the pinned clone and its upstream effect is
decline — the port gives it the contract reading with the strict
Q/MatchQ duality; `$UseGamma`, undefined in `Rubi.m`, becomes the
package variable `mr_use_gamma_flag` with the upstream
`$UseGamma = False;` default).

**Acceptance.** Committed `.run`/`.out` with date stamp; the token
closure table complete (every U token adjudicated); rule counts match
the T1 inventory; the answer-head census identifies the renamable
heads (class-2: `GAMMA(` 191 all 2-arg, `Ei(` 237 all 1-arg — and
`F0(` 14 as a **free function symbol**, `polylog`/`AppellF1`
no-native: not renamed, the structural ceiling).

**Class-2 evidence.** Task 1 (commits `e78263c`, `bd0fa70`):
`probes/translation/03-class2-syntax-census.out` (3 files / 125
rules; AUTO 80 / MANUAL 45), `probes/corpus/02-class2-answer-heads.out`.
Cost: seconds (static parse, no Maxima).

## Step 2 — Translation-table additions

**What.** `generator/translation_table.py` gains the class's entries:
RENAME rows for answer-side heads → **natives with the measured
diff/float conventions** (probe each head in the installed build
first — `diff` must differentiate it for the zero chain to close;
the class-2 table: `Gamma`→`gamma_incomplete` (2-arg **UPPER**:
`diff(gamma_incomplete(a,z),z) = -z^(a-1) %e^-z` — the corpus
`GAMMA(a,z)` convention), `ExpIntegralEi`→`expintegral_ei`
(`diff = %e^z/z`), `Erf`→`erf`, `Erfi`→`erfi`, `Exp`→`exp`); `%mr_`
rows for predicates/support functions (Step 4 ports); `$`-globals →
package variables. Watch the **naming trap**: public names carry
underscores (`expintegral_ei`, `lambert_w`); the `%expintegral_ei` /
`lambertw` spellings read as unbound nouns; `describe(name, exact)`
in the running build is the arbiter.

**Acceptance.** The **byte-identity gate** for every already-accepted
class: `python3 generator/generate_rules.py --class <M> && git status
--porcelain rules/` EMPTY for each accepted class M (class-2:
`--class 1`, 3,026 rules over 72 generated files (67 LoadRules +
5 `EXTRA_CLASS1` b files)).

**Class-2 evidence.** Task 2 (commit `ae20582`): the generalized
generator is a drift-free copy + 6 edit sites; gate green on commit.

## Step 3 — Generate

**What.** `python3 generator/generate_rules.py --class N` — **no
generator code change for a new class is the point** of the pilot;
class-specific workarounds live in the class-1 override table inside
the one generator. If the class needs a new parser construct, add it
with a **loud failure mode** (class-2: the `Part` (`[[…]]`) handler,
commit `ae20582` — unknown tokens raise `GenError` naming
file/rule/head, never a silent pass-through). Head-position pattern
variables (Rubi `v_[…]`) are a pattern form in the **custom
`%mr_matchQ` matcher** — `defmatch` in this build rejects
head-position pattern variables ("defmatch: some pattern variables are
not atoms"); class-2's r96 case forced the matcher addition
(`70e6f58`).

**Acceptance.** Generation completes with **zero unlisted tokens**
(loud-failure gate); then the Step-5 statics.

**Class-2 evidence.** Task 3 (commit `70e6f58`): 14/4/107 = 125
generated; marker-head semantics documented (op(P) a registered
marker → strict arity, ordered args; the unary-minus storage
deviation).

## Step 4 — Utils ports

**What.** The Step-1 token closure's predicate/support list, ported
into `maxima_rubi_utils.mac` as `%mr_`-prefixed functions (house rule
7 — never the native name). **Layer A tests first** — the red→green
discipline: write the failing checks in `test_maxima_rubi.mac`, run
(FAIL; a mid-run death with no Results line is a parse error — fix
syntax first), implement, run (green). **Cluster-per-commit shape**
(class-2: cluster A small predicates, B NormalizeIntegrand chain, C
the FunctionOfExponential family). Every measured build quirk is
stamped in-code with date + build (class-2 accumulated: lambda comma
form, `for e in` iteration, the power op is the **string** `"^"`,
noun ops are internal symbols so test `string(op(u))`,
`(linear)^(1/2)` stores as a `'sqrt` node, negative products store as
unary-minus nodes, …).

**Acceptance.** Layer A green at every cluster
(`maxima --very-quiet -b test_maxima_rubi.mac`, read the Results
line); the ledger entry per cluster records RED/GREEN counts and the
deviations.

**Class-2 evidence.** Tasks 4–6 (commits `4cc259e`/`0850fb5`,
`9262b04`/`4a31b8d`, `c845057`/`0028d82`): RED 519/20 → GREEN 539/0
→ … → 578/0; five brief defects found by measurement in Task 4 alone;
9 documented deviations in Task 6.

## Step 5 — Generate + static sanity greps

**What.** Regenerate the class, then grep the committed files: per-file
rule counts equal the census (`defmatch` counts); **no raw
`$[A-Za-z]`** (`$` terminates a line in the Maxima reader — a
`$UseGamma` passed through verbatim is a guaranteed parse failure);
the renames landed (class-2: 8 `gamma_incomplete|expintegral_ei`
occurrences = 5 Gamma + 3 Ei).

**Acceptance.** Counts match the census exactly; 0 raw-`$` hits;
rename counts match the table.

**Class-2 evidence.** Task 3 Step 6 (ledger): all statics matched
(14/4/107; 9 `mr_use_gamma_flag`; 8 renames; `part()` sites; no
`$[A-Za-z]`).

## Step 6 — Loader + rules core

**What.** The class-N block in `mr_load_all()` (`maxima_rubi.mac`) in
**Rubi.m LoadRules order** (load order = rule priority; the
generator's printed ordered load list is the paste source; class 2
loads after all of class 1). `test/build_rules_core.sh` gains the
class-N files in its `FP` list; rebuild the core. **Fingerprint
mirror — BOTH sides, same sort**: the driver's `_core_fingerprint()`
file list must match `build_rules_core.sh`'s `FP` list (same top
files, same globs, C-locale sorted) — a mismatched core is a loud
driver failure, not a silent 0-rule run.

**Commands (class-2 as executed).**
```
bash test/build_rules_core.sh
sh probes/load_wall/probe-class2-load.run     # full-table load under the TLS flag
```

**Acceptance.** The stamp agrees with the driver fingerprint (rules
count = the accepted set + the new class — class-2: 3,180 = 3,055 +
125, fingerprint `aa53741f7ac802e2c3b8bd93720b219d`); the TLS probe
prints `TABLE_AT_LOAD <n>`; Layer A green.

**Class-2 evidence.** Task 7 (commit `d964fdb`): `mr_load_all()`
76-term flatten; the probe triplet committed (`TABLE_AT_LOAD 3180`,
`.out` 4,247 lines); Layer A 581/0; census spot check (2_2 count 4,
witness, 1.1.1.1 still 5).

## Step 7 — Driver normalization

**What.** The Step-1 answer-head census → `HEAD_REWRITES` entries in
`test/corpus_driver.py`: **native, differentiable targets only**
(each row's head must be probed: `diff` closes on it in the installed
build). Structural rewrites (e.g. `F0`→`hypergeometric`) are a
**separate, measured decision**, not a table row. The rewrites apply
to the integrand + primary + secondary expected texts (the `els[2]`
steps are display-only, never reach Maxima); they are idempotent and
lookbehind-guarded (longer names intact). Unit-test the table
(`test/test_head_rewrites.py` shape: pure Python, positive +
negative checks).

**The no-op check for class 1 (and every earlier class).** Run the
generalized driver over a small slice of each accepted class's
section: the record header must print `head rewrites: {}`, the
accepted merged record must carry 0 occurrences of the rewritten
heads, and an N-entry spot check must classify **identical** to the
accepted merged record (class-2: 50/50 (file,entry) → class, dict
diff).

**Acceptance.** Rewrite unit 0 failed; the no-op checks green for
every accepted class; the spot check N/N.

**Class-2 evidence.** Task 8 (commits `a3ee89c`, `c00b5d9`): two rows
(`GAMMA(`→`gamma_incomplete(`, `Ei(`→`expintegral_ei(`); unit 7/0;
both polarities proven (class-1 slice → `{}`, class-2 slice →
`{'gamma_incomplete(': 1}` — the entry classified `expected`, the
two-sided normalization closing its zero chain live); 50/50 spot
check; the per-shard `head rewrites:` totals (191 + 237) equal the
census counts.

## Step 8 — Baseline (native `integrate`)

**What.** The T3 probe mechanics (`probes/corpus/probe-integrate-sample.py`,
section as 10th positional, the relative suite-dir form), one process
per file (or shard), 30 s cap, native `integrate`. Merge with the
generalized merger (`test/merge_class_shards.py` — the `SHARD_GLOB`
positional distinguishes baseline shards from package shards).
**Carry the yardstick's mechanics note** into the Step-9 readout: the
probe's 4-stage symbolic chain, no head rewrites, and
noun-on-answer-expected = PASS `no-answer` make the yardstick err
slightly conservative for the package (2 of 3 asymmetries flatter it)
— quote it wherever the A/B is read.

**Commands (class-2 as executed — 3 per-file shards, then merge).**
```
python3 probes/corpus/probe-integrate-sample.py "2 Exponentials/" 999999 30 reference/maxima-syntax-test-suite 0 "" 0 test/corpus_class2.baseline.shard00.out 1 "2 Exponentials" &   # shards 1,2 the same (indices 1,2 / 2,3)
python3 test/merge_class_shards.py "2 Exponentials" test/corpus_class2.baseline.out test/corpus_driver.py "corpus_class2.baseline.shard*.out"
```

The shard-plan bounds are **START/STOP file indices into the
section's sorted file list, STOP EXCLUSIVE** (slice semantics — the
pilot's 3-file section ran as (0,1), (1,2), (2,3)).

**Acceptance.** Merged record with build-stamped header; completeness
asserted N/N (class-2: 965/965); the Results line read.

**Class-2 evidence.** Task 9 (commit `ec62741`, + the suite-dir fixes
in `a2f54c1`): 965 entries, walls 5.6/38.2/46.3 s; **593/965 (61.5 %)**
(expected 123 / verified 186 / no-answer 284 / unverified 357 /
unexpected 14 / timeout 1).

## Step 9 — Package run + A/B + timeout re-check

**What.** The launcher instance over the section (cost-aware sharding
carries over; a fresh section balances by count until measured times
exist). Merge, read the Results line, then the **full A/B against the
Step-8 baseline** (per verdict class + entry-level transitions,
PASS = {expected, verified, no-answer} — the entry-level part is a
**(rel, entry)-keyed comparison of the two records' T3 lines**,
method as executed in the pilot (ledger Task-10; the uplift doc's
309/216 split is the worked example) — reconstructible from the two
records, not a committed script (the plan's Task-10 Step-3 python
does the per-class tallies only); every PASS→FAIL remainder triaged
into genuine declines vs yardstick reclassification — the milestone-1
discipline), then the **100 s timeout re-check** (read the
transitions; now-PASS 0 = the cap is not the limit; `error` = the
death census — a reproducible build bug is its own ticket).

**Commands (class-2 as executed).**
```
python3 test/launch_class_shards.py "2 Exponentials" test/corpus_class2.out test/corpus_driver.py --launch
setsid sh test/wait_and_merge.sh test/corpus_class2.shard-pids test/merge_class_shards.py test/class2_merge.out "2 Exponentials" test/corpus_class2.out test/corpus_driver.py "corpus_class2.shard*.out" &
# ...A/B (per-class: the plan's Task-10 Step-3 python; entry-level: the (rel,entry) join, method per the paragraph above)...
python3 test/launch_timeout_rerun.py test/corpus_class2.out 100 test/corpus_class2.timeout-rerun "2 Exponentials" --launch
setsid sh test/wait_timeout_rerun.sh test/corpus_class2.timeout-rerun >> test/corpus_class2.timeout-rerun/wait.log 2>&1 &
```

**Acceptance.** Record committed, completeness N/N; A/B remainders
triaged (none unexplained); re-check record committed with the
transitions read.

**Class-2 evidence.** Task 10 (commit `fe5364a`): 965/965, 26 shards /
24 procs, wall 8 min 07 s; **500/965 (51.8 %) vs 593/965 (61.5 %)**;
entry-level PASS→FAIL 309 (178 genuine, ALL `deferred` + 131
yardstick) / FAIL→PASS 216; re-check 7/7 → error 2 + unverified 5,
now-PASS 0; the SBCL heap-exhaustion finding (2.3 e56/e57/e68,
quotients of exponentials) as the principal output.

## Step 10 — Close

**What.** (a) The uplift record `docs/corpus-class<N>-baseline-uplift.md`
in the house shape (the class-1 record
`docs/corpus-baseline-uplift.md` is the template): header / rule set /
normalization / baseline / package run (per-class A/B + re-check
transitions) / residues / earlier-class status / ledger flags. (b) The
**residue analysis**: the FAIL masses per corpus file, ~5 sample
entries each with the T3-line timing, the likely-cause classification
(rule coverage vs ported-semantics decisions vs measured build bugs —
say "likely" where it is a guess), and the residue→expected-head
census — the **polylog/AppellF1 structural-ceiling decision** is
per-class, not upfront: if `polylog`-carrying entries form a material
unverified block, a `polylog(2,·)` derivative shim (its derivative
`-log(1-u)/u` is elementary) becomes a follow-up ticket with that
number as its go; otherwise the ceiling stands (spec §3.4). Class 2's
measured reading: no rule emits `polylog`/`AppellF1`; the polylog mass
(12 unverified + 51 deferred + 3 timeout entries) is present but the
ceiling stood, so the decision is **deferred to the first class that
needs it**. (c) The `todo/TODO.md` milestone entry (one short entry
per follow-up: status + link). (d) The final gates, run and recorded:
```
maxima --very-quiet -b test_maxima_rubi.mac        # Results: <total> passed, 0 failed
python3 generator/generate_rules.py --class <M> && git status --porcelain rules/   # EMPTY, every accepted class M
python3 test/test_head_rewrites.py                 # 0 failed
```

**Acceptance.** Record + runbook + TODO committed; gates green; the
ledger's per-task entries complete; follow-up tickets created (one per
remaining class against THIS runbook, one per measured finding).

**Class-2 evidence.** Task 11: `docs/corpus-class2-baseline-uplift.md`,
this runbook, `todo/TODO.md`'s Milestone-2 section (classes 3–8
ticketed in the spec's order: 3 logarithms 3,085 entries; 8 special
1,949; 5 inverse trig 4,585; 6 hyperbolic 5,080; 7 inverse hyperbolic
6,552; 4 trig 22,472 — last).

## Cost profile (class-2 measured)

| step | class-2 wall (measured) |
|---|---|
| 1 census | seconds (static, no Maxima) |
| 4 utils ports | Layer A per cluster: seconds to run, minutes to land (TDD red→green per cluster) |
| 8 baseline | 3 per-file shards, walls 5.6 / 38.2 / 46.3 s (965 entries, 30 s cap) |
| 9 package run | 8 min 07 s wall (26 shards / 24 procs, 965 entries) |
| 9 re-check | ~6 min wall (7 entries, 300 s cap — dominated by the 274.3 s entry) |
| full class-1 comparison point | ~82 min wall on 24 procs (25,697 entries, accepted run) |

The follow-class expectation: cost scales with the section's entry
count (the spec's per-class entry counts: 1,949–22,472), so the
largest classes (4 trig, 22,472) are multi-hour runs — the
cost-aware planner's chunk-splitting is what keeps every job under
the per-process target.
