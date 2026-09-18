# maxima-rubi — project instructions

A rule-based symbolic integration package for Maxima in the spirit of
Rubi (rule-based integration): declarative integration rules executed by
a pattern-matching rule runner, held to the Rubi Maxima-syntax test
corpus. Milestone 1: foundation + the algebraic-function class.

Research-phase design: `docs/superpowers/specs/2026-08-17-maxima-rubi-research-design.md`.
Working state: `todo/TODO.md`.

## Git

- **The default branch is `master`. There is no `main`** — do not create one.
- The remote is `origin` (`git@github.com:sdemarre/maxima-rubi.git`).
  Push only when the user asks; `master` is the integration branch.
- Do not add `Co-Authored-By` trailers to commit messages.

## Handoffs

Cross-session handoff documents live in `handoffs/` (gitignored working
docs), named `YYYY-MM-DD-<slug>.md`. When told to pick up "the latest
handoff", read the most recent file there (ISO date in the filename) and
work through its **Next moves** section; it references the authoritative
artifacts (specs, plans, ledger, probe records) rather than duplicating
them.

## Reference clones

The research reads two reference repositories, cloned locally under
`reference/` (gitignored — working copies, not part of this project):

- `reference/rubi` — `RuleBasedIntegration/Rubi` (Rubi 4, the rule set being ported).
- `reference/maxima-syntax-test-suite` — `RuleBasedIntegration/MaximaSyntaxTestSuite`.

The pinned commit (full 40-digit hash) of each is recorded in
`todo/TODO.md`. Claims about Rubi refer to the pinned commits.

## Maxima version

The installed build is **Maxima
`branch_5_50_base_84_g4204fb669`** (5.50-series, build date
2026-08-31 13:27:47) on SBCL 2.6.7. It replaced the 2026-08-29
17:58:20 build (the class-3 port build), which had in turn replaced
the 2026-08-20 21:36:22 build (milestones 1–2's measurement build)
during milestone 3, 2026-08-29. The research docs' 5.49-series
expectation is superseded. The project does **not** pin to any
build: every measurement is stamped with the build it was taken on
(the class-1/class-2 accepted records carry the 2026-08-20 stamp;
the class-3 triage record (probe 06) carries the 2026-08-29 stamp;
the class-3 sweep-cost fallback and verdict-split probes (07/08)
carry the 2026-08-31 stamp — the 2026-08-31 rebuild is the same
branch hash / SBCL with the rules core NOT rebuilt, fingerprint
`36b8bae7dba3c6e4fde614b6df70caa4` unchanged), and baselines are
re-measured on upgrade rather than carried over — the milestone-3
close re-validated the class-1/class-2 accepted classifications
under the new build via the Task-8 no-op slices (51/51 × 2, zero
diffs; `docs/corpus-class3-baseline-uplift.md` §6).

## Loading rule files: the TLS limit

The SBCL special-variable pool is a hard per-process cap (~4098 in the
installed core, `probes/load_wall/probe-tls-calibration.out`); creating a
special variable beyond it is the **uncatchable** FATAL "Thread local
storage exhausted". Under `defmatch` every generated rule's
`defmatch`/`matchdeclare` slots were special variables (~9.6 per class-1
rule, `probes/load_wall/probe-load-curve.out`), so from 2026-08-22 (user
decision) until the matcher substrate's P4 every maxima process that
loaded rule files ran with `-X "--tls-limit 100000"`.

The rule files are now `%mr_defrule` records: a pattern is a string the
Lisp matcher prepares, and no rule creates a pattern-variable slot.
Without the flag, `load("maxima_rubi.mac")` + `mr_load_all()` (3,513
rules) answers and verifies a smoke integral and the whole Layer A run
is green, with no TLS message (`probes/matcher/08-runtime-load.out`,
build `branch_5_50_base_84_g4204fb669`). **The flag is no longer
required** (spec `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`
§3.5). It is harmless: `test/build_rules_core.sh` and
`test/corpus_driver.py` still pass it. Interpreted cond/repl `block`
locals take no slot (`mbind-doit` binds them with `mset` + `mspeclist`,
no special declaration); the `defmatch` slots came from compiled matcher
code. Compiled or translated rule code is what could bring the error
back — if a later change compiles or translates the rule files, re-run
probe 08 and restore the flag rule (two argv tokens:
`-X "--tls-limit 100000"`, not `--tls-limit=N`).

## Looking up Maxima itself

The manual is in the running Maxima, not on the web — consult it before
guessing at a builtin's name, signature or behaviour. Two commands:

- `? subject` — exact lookup, prints the manual entry.
- `?? partial_subject` — inexact search across topic names.

These are shorthand for `describe(subject, exact)` and
`describe(subject, inexact)`; `describe` is equally fine and is the better
choice inside a script, being an ordinary function call with none of the
line-swallowing quirk below.

From a shell, one lookup per invocation:

```sh
maxima --very-quiet --batch-string='? match;'
maxima --very-quiet --batch-string='?? pattern;'
maxima --very-quiet --batch-string='describe("matchfix", exact);'
```

Four behaviours worth knowing, all measured here (Maxima 5.49, SBCL):

- **`?` and `??` swallow the rest of the LINE**, semicolons included. Put one
  on a line by itself: `?? sqrt; disp("hi");` looks up the subject
  `sqrt; disp("hi")` and finds nothing. `describe("sqrt", inexact)` has no
  such problem — it is parsed like any other call.
- **`??` with several matches prints a numbered list, then prompts.** Non
  interactively the prompt hits end-of-file and prints `Maxima encountered a
  Lisp error: end of file`. It is harmless — Maxima continues with the next
  statement — and the numbered list, which is the part you wanted, has
  already been printed.
- **The reliable two-step** is therefore `??` to find the exact name, then `?`
  on that name to read the entry. (Piping a selection — `printf '1\n' |
  maxima -b file.mac` — also answers the prompt, but only for `-b`; with
  `--batch-string` the prompt does not read stdin.)
- `??` with exactly one matching topic skips the prompt and prints the entry.

## Research discipline

- **Measured claims:** every non-trivial claim in a `docs/` research doc
  cites the measurement that produced it, and the measurement is a
  committed, re-runnable probe under `probes/` (a Maxima batch script or a
  shell script). A doc section is written when its evidence exists, not
  stubbed ahead of it.
- Counts and timings are stamped with the date and the Maxima build —
  obtained from `build_info()` (`version` is unbound in the installed
  5.50.0 build — measured 2026-08-27).
- "Maxima surely has X" is never a claim: look it up per the section above,
  or write a probe.

## Tests

Two layers, one reading protocol. Every run ends with
`Results: <n> passed, <m> failed`. **Read that line** — individual
assertions print `PASS:`/`FAIL:` above it, and a run can also die
mid-way with a Maxima error, in which case no `Results:` line is
printed at all, which is itself a failure.

**Layer A — unit suite** (the per-change gate), one batch run:

```sh
maxima --very-quiet -b test_maxima_rubi.mac
```

No TLS flag since the matcher substrate's P4 (the flagless run is
green, `probes/matcher/08-runtime-load.out`; see the TLS section above).
From 2026-09-01 (class-3 deferred campaign C1) until then the flag was
mandatory: the test set loads rule siblings cumulatively per process,
and the `defmatch` slots of 3_1_3/3_1_4/3_1_5 overran the special-var
cap.

957 targets (green: `Results: 957 passed, 0 failed`; the
milestone-3 close figure was 743 — growth 511 → 581 across the
pilot's clusters, 581 → 620 headvar checks, → 691 cluster A, → 743
cluster B, → 750/758/763 the campaign's B1/B2/B4, → 780 C2, → 798 C1,
→ 815 C4 (3_2_1 r16/r18/r20 log-arg structural match, 17 checks),
→ 835 C3 (ratio log-arg stored-Quotient structural match, 20 checks),
→ 851 B3 (3_3 cover-miss binpow/logpow slotting, 16 checks),
→ 862 C5 (3_4 slotted-inner-exponent mly/m1b slotting, 11 checks),
→ 869 C6-cassimp (3.5 r10 cond ratsimp, M-cas-simp e92/e93, 7 checks),
→ 892 C6b (3.5 r42 FunctionOfLog catch-all port + bare catch-all
pattern fix, e134/e139/e258, 23 checks), → 897 matcher substrate P4
(the matcher-coupled sections rewritten against the substrate entries,
892 → 875, and the generated MatchQ pattern shapes, 22 checks), → 898
plan-2 final review (1.4.2 r17 MatchQ exponent part folding), → 957 matcher translation fixes
(docs/superpowers/plans/2026-09-14-matcher-translation-fixes.md: the exact seen entry 5, integer
comparisons / notequal / juxtaposition 17, the PosAux port and the First/Rest siblings 37 checks)).

**Matcher substrate — unit suites** (the per-change gate for
`maxima_rubi_match.lisp` / `maxima_rubi_tree.lisp` /
`maxima_rubi_dispatch.lisp`; branch `matcher-substrate`, spec
`docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`). No
rule files are loaded:

```sh
maxima --very-quiet -b test/matcher/test_mr_match.mac
maxima --very-quiet -b test/matcher/test_mr_tree.mac
maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null
```

Green: `Results: 53 passed, 0 failed` (mr-match; 48 at Plan 1's Task 5,
+3 at the final-review fix wave: the last-absorber cost bounds and the
empty-leftover lock, +2 at Plan 2: the Power-exponent Optional
default), `Results: 51 passed, 0 failed` (mr-tree; 46, +5 at Plan 2:
CRE input and the booleans) and `Results: 58 passed, 0 failed`
(dispatch: rule records, dispatcher outcomes, bindings / retry / head
symbols / CRE / G-6, the test entries, MatchQ; 45 at Plan 2's Task 4,
+4 at its review: the fault type excludes interrupts and timeouts, a
MatchQ pattern prepare rejects is an error, +8 at the final review:
MatchQ part folding and an out-of-range part error, +1 at Plan 3: the
switch defaults).
`test_mr_match.lisp` has no Maxima dependency and also runs in plain
SBCL: `sbcl --non-interactive --load maxima_rubi_match.lisp --load
test/matcher/test_mr_match.lisp --eval '(mr-match-test:run)'`.

**Generator — P3 static gate** (the per-change gate for
`generator/generate_rules.py` and the regenerated rule files; spec
section 4 P3). No Maxima; `sbcl` must be on the PATH:

```sh
python3 test/check_generated_rules.py
```

Green: `Results: 14 passed, 0 failed` (11 + the three translation-fix exception counts, 2026-09-14).
It compares the working tree's
`rules/class{1,2,3}/*.mac` with the P0 commit `0a6664c` (`--base
<commit>` for another base): rule counts and `mr_rules_<key>` lines, no
`defmatch`, every cond/repl body byte-identical to the base except the
spec's closed exception list (each exception checked as the exact text
transformation it claims to be; the list includes the matcher translation
fixes' 1,283 integer comparisons, 10 `notequal` and 1 juxtaposition), the
reader self-test
(`python3 generator/mma_reader.py`), and every pattern string preparing
in `MR-MATCH`. Regeneration is byte-identical:
`python3 generator/generate_rules.py --class <1|2|3>` leaves
`git status --porcelain rules/` empty.

**Matcher substrate — regression suite** (spec section 4 P1/P2 gates:
the probe-02 round trip over all 7,444 Rubi LHSs in narrow and wide
modes, tree leg and Maxima leg through `mr-tree`, the probe-02
controls, the spike-01 cases). 20 Maxima shards, ~70 s wall per arm;
run the two arms sequentially, each detached (`setsid`) and polled:

```sh
MR_LEGS=tree,maxima MR_SPIKE=1 sh test/matcher/run.sh
MR_LEGS=tree,maxima MR_MODEL_FLAGS=1 MR_SPIKE=1 sh test/matcher/run.sh
```

The first (Maxima defaults) writes `test/matcher/roundtrip.out`,
`controls.out`, `spike01.out`, `gate.out`; the second (the
`radexpand:false` + `logexpand:false` arm) writes
`roundtrip.flags.out`, `gate.flags.out` and rewrites `controls.out` /
`spike01.out`. Each prints its gate's line — green is
`Results: 109 passed, 0 failed` in both arms; the gate
(`test/matcher/gate.py`) requires every rule OK in both modes (no
MISS), 0 UNSOUND, 0 false mutation matches. `MR_WORK=<dir>` moves the
shard work directory (default `${TMPDIR:-/tmp}/mr-matcher-suite[.flags]`).
A plain `sh test/matcher/run.sh` runs only the tree-leg P1 gate
(`Results: 37 passed, 0 failed`) and **overwrites the committed P2
records** `roundtrip.out` / `controls.out` / `gate.out` — run the two
commands above to regenerate them.

**Layer B — full class-1 corpus** (25,697 entries, 30 s per-entry cap,
one fresh maxima subprocess per integral, verification by
differentiation with the corpus expected answer as the secondary
check). Sharded over 24 processes, ~80 min wall:

```sh
python3 test/launch_class1_shards.py --launch
setsid sh test/wait_and_merge.sh
```

The watcher merges the shards to `test/corpus_class1.out` (completeness
asserted: 25,697/25,697, no dupes/missing/extra). **The full-run A/B
against the previous merged record is the regression gate** (see
**Record A/B** below). The 120-target canary (`python3 test/canary.py`, 60 s/target) is a smoke,
not a gate: its broad set is biased toward currently-failing targets
and cannot gate verified-target regressions.

**Layer B — full class-2 corpus** (965 entries, 30 s per-entry cap,
one fresh maxima subprocess per integral, verification by
differentiation with the corpus expected answer as the secondary
check). Sharded over 24 processes, ~8 min wall:

```sh
python3 test/launch_class_shards.py "2 Exponentials" test/corpus_class2.out test/corpus_driver.py --launch
setsid sh test/wait_and_merge.sh test/corpus_class2.shard-pids test/merge_class_shards.py test/class2_merge.out "2 Exponentials" test/corpus_class2.out test/corpus_driver.py "corpus_class2.shard*.out" &
```

The watcher merges the shards to `test/corpus_class2.out`
(completeness asserted: 965/965, no dupes/missing/extra). The
class-N mechanics are runbooked in `docs/class-porting.md`
(Steps 8-9); the measured acceptance is
`docs/corpus-class2-baseline-uplift.md`.

**Layer B — the queue runner** (`test/run_corpus_queue.py`), the preferred
launcher for any class. One manager process runs N worker threads that pull
from a single queue; worker k writes `corpus_<slug>.shard<kk>.out` in the
driver's format, so the mergers and `wait_and_merge.sh` read it unchanged.
Both paths call `corpus_driver.run_entry`, so they cannot drift.

```sh
python3 test/run_corpus_queue.py "2 Exponentials" --prev test/corpus_class2.out \
    --workers 24 --launch
```

Without `--launch` it prints the plan and exits. `--prev RECORD` orders the
queue longest-estimate-first (entries the record does not time go first);
`--entries-from/--class/--out-dir` is the subset mode for the timeout
re-check.

**Keep `--workers` at or below the core count.** Over-subscription is a
FIDELITY problem, not only a speed one: every entry then runs contended, its
wall depends on how many others happen to be running, and the 30 s cap is a
WALL cap, so it decides verdicts. The planner warns when asked for more. The
sharded launchers remain for reproducing an old record on its own path.

`--job-seconds N` sizes the dispatch unit in estimated seconds; the default,
0, is one entry per unit and is the measured best. Makespan >= (core-seconds
/ workers) + the largest unit, so the unit size IS the tail bound, and every
entry is already its own Maxima subprocess, so a larger unit amortises
nothing. MEASURED 2026-09-17 on the 25,697 per-entry walls of the
faithful-pair class-1 run (24 workers, floor 116 min): per-entry 116 min
whether ordered by corpus order, stale estimates or perfect foresight;
~10-minute units 120 min; ~30-minute units 126 min. Sized from the PREVIOUS
record, a 10-minute target produced a 35-minute actual unit and a 30-minute
target a 91-minute one — at one entry per unit the tail bound is the 30 s
cap however wrong the estimates are.

MEASURED 2026-09-18, class 2 (965 entries), same code, merger-clean at
965/965 in every arm:

| arm | wall | PASS | vs sharded |
|---|---|---|---|
| sharded, 22 shards | 350 s | 710 | — |
| queue, 24 workers | 112 s (3.1x) | 707 | 3 PASS->FAIL |
| queue, 12 workers | 180 s (1.9x) | 708 | 2 PASS->FAIL |

The differing entries are all `verified -> timeout` at 23-27 s against the
30 s cap; 2.3 e527/e528 (26.8/26.9 s) flip in both queue arms and were the
same pair the 2026-09-15 measurement found, i.e. borderline entries rather
than a queue defect. The 24-worker arm loses one extra such entry (the machine
is 12 physical cores + SMT), which is the speed/fidelity trade to settle per
class. Compare arms with `test/ab_records.py`, never on wall clock.

**Switch arm — matcher substrate P5** (Plan 3,
`docs/superpowers/plans/2026-09-13-matcher-substrate-plan3.md`). The
three migration switches (`mr_flat_wide` false, `mr_cond_retry` true,
`mr_model_flags` true — the defaults in `maxima_rubi_dispatch.lisp`)
are set per run with `MR_SWITCHES` (space-separated
`<switch>=true|false`), e.g.
`MR_SWITCHES="mr_model_flags=false" python3 test/launch_class_shards.py …`.
The driver assigns them in every entry text and ends its `filter:`
line with `switches: …`; the mergers refuse shards that state no arm
or two arms. A launch first deletes the previous run's shard files and
refuses while one of its pids is alive. Entry subprocesses get stdin
`/dev/null` (`probes/matcher/09-harness-fault-verdict.out`: an
inherited open stdin held a fatal SBCL error in `ldb` until the cap).
The P5 gate and the winner rule:

```sh
python3 test/p5_gate.py gate <P0-record> <new-record>
python3 test/p5_gate.py winner <switch> <run-1 c1> <run-1 c2> <run-1 c3> <flip c1> <flip c2> <flip c3>
```

Guard (no Maxima): `python3 test/test_run_records.py` — green
`Results: 41 passed, 0 failed`.

**Record A/B** — the entry-level diff of any two merged records (any
class, shard files and re-check records too); use it for every
regression gate instead of writing a one-off join:

```sh
python3 test/ab_records.py <old-record> <new-record> [--all]
```

It prints the key-set check (exit 2 when the records cover different
entries), the PASS/FAIL 2x2 table, class transitions, per-file counts,
and every PASS→FAIL line — each must be attributed before acceptance
(`--all` adds the FAIL→PASS lines). PASS classes are read from the
driver, so the table agrees with its `Results:` line.

**Pinned-core A/B** — to measure an older rule set (e.g. the tree
before a fix) against the current one, build its core in a worktree
at that commit (`sh test/build_rules_core.sh` there) and run the
normal launch with the env var pointing at it; the driver stays the
single copy:

```sh
MR_RULES_CORE_PATH=<worktree>/test/mr_rules.core python3 test/corpus_driver.py ...
MR_RULES_CORE_PATH=<worktree>/test/mr_rules.core python3 test/launch_class_shards.py ... --launch
```

The pinned core is used as-is (no fingerprint check against this
tree, no rebuild); a missing core or `.stamp` exits nonzero; the
record's `filter:` line ends `core: pinned <path>`.

**The per-entry cap is CPU seconds** (`corpus_driver.CAP_KIND`, default
`cpu`; 2026-09-18 user decision). A WALL cap measures the machine as much as
the code: an entry's verdict then depends on what else happened to be running.
MEASURED — the 2026-09-17 class-1 run put 33 processes on 24 vCPUs, so early
entries ran contended and late ones ran alone; and 2 Exponentials e527/e528,
at 26.8/26.9 s against the 30 s wall cap, VERIFY at 12 workers and TIME OUT at
24 on identical code. Under a CPU cap an entry is not charged for time it spent
waiting rather than computing, and the record's `t=` is the entry's CPU
seconds — the same quantity the cap bounds.

**What actually delivers reproducibility is the QUEUE, not the cap kind.**
MEASURED 2026-09-18 on class 2, same code, `ab_records.py` entry for entry:
two runs at 24 workers agree exactly under BOTH caps (0 transitions, wall and
cpu alike), because the queue holds concurrency constant; the old sharded runs
varied load THROUGH the run (33 processes early, a handful late), so an entry's
verdict depended on when it was scheduled. Neither cap is load-INDEPENDENT:
changing the worker count moves a few boundary entries either way (wall
24->12: 3 entries; cpu 24->8: 4), all of them out of `timeout` as contention
falls.

The reason the cpu cap does not fix that is SMT. The kernel charges scheduled
time, and a thread sharing a physical core executes fewer instructions per
CPU-second, so a CPU-second is not a constant unit of work on this 12-core /
24-thread host. MEASURED over the 748 class-2 entries above 0.5 s that finished
in both arms: total CPU 1648 s at 24 workers against 1219 s at 8 — a **1.35x
inflation**, i.e. a 30 CPU-second budget at 24 workers buys about 22
CPU-seconds' worth of 8-worker work. Running at or below the PHYSICAL core
count (12 here) is what would make the CPU-second a stable unit; that is
untested.

The cap kind is kept as cpu because it is still the more principled unit on a
shared machine — an unrelated process burning CPU penalises a wall-capped entry
and not a cpu-capped one — but that benefit is unquantified, and the cpu cap
was NOT what made the records reproducible.

Mechanism (`maxima_run`): `ulimit -S -t <cap>` in a `/bin/sh` wrapper, with
the hard limit a few seconds above as a backstop. A soft limit kills SBCL with
SIGXCPU, which reaches the wrapper as exit 128+SIGXCPU — unambiguous, unlike
the SIGKILL of a hard limit or the OOM killer. The wrapper does not `exec`, so
it survives its child and reports the child's CPU with `times`; a wall
backstop (4x the cap, min 120 s) catches a process blocked rather than
computing, and kills the process GROUP so the Maxima process is never
orphaned. `ulimit` rather than `preexec_fn=resource.setrlimit` because
preexec_fn is unsafe in a threaded process and the queue runner is one.

**Records state the kind** (`timeout: 30s cpu` on the `filter:` line) and the
mergers refuse shards that disagree. **A cpu record and a wall record are NOT
comparable**, but the shift is SMALL. Measured 2026-09-18 over the 4,414
entries that finished in both the 33-shard wall record and the 24-worker cpu
run, cpu/wall by old-wall band: 0-0.3 s 2.00, 0.3-1 s 1.25, 1-3 s 1.24,
3-10 s 1.00, 10-31 s 0.84. The small bands are dominated by the records' 0.1 s
resolution (0.10 vs 0.20 is one tick against two); the bands near the cap, where
it actually acts, give 0.84-1.00. So an entry using 12.2 s wall then uses
10.3 s cpu now: the old 30 s wall cap was worth about 25 s of cpu work and the
new cap is roughly 19 % more generous, flat to slightly tighter in the mid
bands — call it within +-25 %, not a doubling. (An earlier note here claimed
"roughly twice", generalised from 12 entries of 1.1.1.3 all under 1.8 s, i.e.
from the band where the ratio is resolution noise. It was wrong.) The 33-shard
run averaged 12 concurrent entries on 24 vCPUs — about 50 % utilisation,
because of the tail — so most of its entries were NOT heavily contended and
their wall was close to their cpu. Expect some timeout entries to flip, not a
wave; a higher PASS count is still partly a cap redefinition rather than a code
improvement, and the two kinds must never be A/B'd.
`MR_CAP_KIND=wall` reproduces a pre-2026-09-18 record on its own terms and is
byte-identical to the old driver.

**Timeout re-check** — the standing answer to "is 30 s at the limit?"
for any merged record: re-run exactly the record's `timeout` class at
a larger cap (100 s standing value) and read the transitions:

```sh
python3 test/launch_timeout_rerun.py [record] [cap] [run-dir] --launch
setsid sh test/wait_timeout_rerun.sh <run-dir> >> <run-dir>/wait.log 2>&1 &
```

(the watcher runs `test/merge_timeout_rerun.py`; completeness is
asserted against the record's timeout class, the cap is read from the
shard headers). The 30 s per-entry cap STAYS the standard, now in CPU
seconds (see above; the 30 s figure itself is the user
decision 2026-08-27); the route for slow-correct entries is matcher
speed, not budget.

The harness protocol (verdict classes, zero-chain verification,
driver mechanics) is specified in `docs/package-architecture.md` (T5);
the measured acceptance record and re-run discipline are in
`docs/corpus-baseline-uplift.md`.

## Agent skills

### Issue tracker

Local markdown: issues and specs live as files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary, label strings equal to role names. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root (neither exists yet; created lazily). See `docs/agents/domain.md`.
