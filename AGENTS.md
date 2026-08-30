# maxima-rubi — project instructions

A rule-based symbolic integration package for Maxima in the spirit of
Rubi (rule-based integration): declarative integration rules executed by
a pattern-matching rule runner, held to the Rubi Maxima-syntax test
corpus. Milestone 1: foundation + the algebraic-function class.

Research-phase design: `docs/superpowers/specs/2026-08-17-maxima-rubi-research-design.md`.
Working state: `todo/TODO.md`.

## Git

- **The default branch is `master`. There is no `main`** — do not create one.
- A remote is **planned but not yet configured**; until it is set up,
  `git push` has nowhere to go. Do not assume pushing is possible; once
  it is configured, commits target `master`.
- Do not add `Co-Authored-By` trailers to commit messages.

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
2026-08-29 17:58:20) on SBCL 2.6.7. It replaced the 2026-08-20
21:36:22 build (milestones 1–2's measurement build) during
milestone 3, 2026-08-29. The research docs' 5.49-series expectation
is superseded. The project does **not** pin to any build: every
measurement is stamped with the build it was taken on (the class-1/
class-2 accepted records carry the 2026-08-20 stamp; class-3
records carry the 2026-08-29 stamp), and baselines are re-measured
on upgrade rather than carried over — the milestone-3 close
re-validated the class-1/class-2 accepted classifications under the
new build via the Task-8 no-op slices (51/51 × 2, zero diffs;
`docs/corpus-class3-baseline-uplift.md` §6).

## Loading rule files: the TLS limit

The SBCL special-variable pool is a hard per-process cap: creating a
`defmatch`/`matchdeclare` slot beyond it is the **uncatchable** FATAL
"Thread local storage exhausted". The installed core's baked-in limit is
~4098 special vars (`probes/load_wall/probe-tls-calibration.out`), and a
generated class-1 rule costs ~9.6 of them on average
(`probes/load_wall/probe-load-curve.out`) — the default limit holds only
~310 class-1 rules. **Any maxima process that loads rule files must be
run with `-X "--tls-limit 100000"`** (user decision 2026-08-22). The flag
takes two argv tokens — not `--tls-limit=N`. 100000 covers the full
loaded Rubi set (7,432 rules, T1 count) at ~1.4x headroom; the probes
above self-flag if the build moves.

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

581 targets (green at milestone-2 close: `Results: 581 passed,
0 failed`; the count grew 511 → 581 across the pilot's clusters).

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
against the previous merged record is the regression gate.** The
120-target canary (`python3 test/canary.py`, 60 s/target) is a smoke,
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

**Timeout re-check** — the standing answer to "is 30 s at the limit?"
for any merged record: re-run exactly the record's `timeout` class at
a larger cap (100 s standing value) and read the transitions:

```sh
python3 test/launch_timeout_rerun.py [record] [cap] [run-dir] --launch
setsid sh test/wait_timeout_rerun.sh <run-dir> >> <run-dir>/wait.log 2>&1 &
```

(the watcher runs `test/merge_timeout_rerun.py`; completeness is
asserted against the record's timeout class, the cap is read from the
shard headers). The 30 s per-entry cap STAYS the standard (user
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
