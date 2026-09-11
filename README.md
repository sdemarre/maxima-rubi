# maxima-rubi

A rule-based symbolic integration package for Maxima, in the spirit of
[Rubi](https://github.com/RuleBasedIntegration/Rubi): Rubi 4's
integration rules, ported as declarative Maxima patterns executed by a
first-match-wins rule runner, held to the Rubi Maxima-syntax test corpus
as the yardstick. Milestone 1 delivered the foundation (loader, runner,
predicate/shim layer, Python rule generator, two-layer test harness)
plus Rubi's class-1 (algebraic functions) rule set; milestones 2 and 3
ported class 2 (exponentials) and class 3 (logarithms). Classes 4–8
are open runbook tickets (`todo/TODO.md`, `docs/class-porting.md`).

## Requirements

Measured on Maxima 5.50.0 / SBCL 2.6.7 (every number in this repo is
stamped with the build it was taken on; re-measure on a new build, do
not carry numbers).

**Any `maxima` process that loads rule files must be started with
`-X "--tls-limit 100000"`** (two argv tokens — the flag takes no
`=`). The SBCL special-variable pool is a hard per-process cap; beyond
it, creating a `defmatch` slot dies with the uncatchable FATAL
"Thread local storage exhausted". The default limit holds only ~310
class-1 rules; 100000 covers the full loaded Rubi set at ~1.4x
headroom. The test harness and the rules-core build already pass the
flag; an interactive session that calls `mr_load_all()` or
`mr_load_class1_all()` must set it at startup.

## Loading

```maxima
load("maxima_rubi.mac")$       /* utils + dispatcher + 1.1.1.1 core      */
mr_load_all()$                 /* classes 1-3, Rubi LoadRules order (3,514 rules) */
/* or: mr_load_class1_all()$      the class-1 rule set only (3,055 rules) */
```

`load("maxima_rubi.mac")` must be findable by one of four paths: load
by full path, run maxima from the package directory, push the package
directory onto `file_search_maxima`, or install the package under
`~/.maxima/`. Every sibling load is witness-checked: a missed or
truncated sibling fails loudly at load time with the four options
named.

The eager load is deliberately small (the 1.1.1.1 core — five rules —
plus the support layer). `mr_load_all()` loads the full table: the
73-file class-1 port (67 LoadRules files + the five corpus-tested
`b`-suffixed 1.2.1 siblings + the manually ported 9.1), then class 2
(3 files, 125 rules) and class 3 (11 files, 334 rules), in Rubi
`LoadRules` order. On a build without the TLS headroom, load single
files instead:
`%mr_load_sibling("rules/class1/<key>.mac", 'mr_witness_<key>)` then
concat the file's rule list onto `mr_rule_table` (`unload()` releases a
file's patterns).

## API

```maxima
rubi(f, x)                  /* the entry point */
rubi_fallback(f, x, fb)     /* explicit fall-through control (fb = true) */
rubi_verbose : true$        /* print the rule that fires / misfire diagnostics */
```

- `rubi(f, x)` returns an antiderivative, or the package no-answer noun
  `unintegrable[f, x]` when no top-level rule fires (or the recursion
  cap, `%mr_max_depth : 16`, is reached). It is rules-only: a top-level
  0-firing is a port/matcher-gap signal, not a job for native
  `integrate`.
- `rubi_fallback(f, x, true)` restores the status-quo behaviour: the
  same rule set, but a top-level 0-firing (or cap hit) falls through to
  native `integrate(f, x)` — the `integrate` noun is then Maxima's own.
  Generated rules call `mr_int` for NESTED sub-integrals, which always
  keeps the native fall-through.
- `rubi_verbose` prints the fired rule, boolean-leak misfires, and
  BOOLWALK crashes on each dispatch.

## Measured state

Accepted records against the Rubi Maxima-syntax corpus (30 s
per-entry cap, 24-shard runs, SBCL 2.6.7; PASS = verified, expected,
or a correct no-answer). Each record carries its own Maxima build
stamp in its header.

| class | integrals | package PASS | native `integrate` | record |
|---|---|---|---|---|
| 1 algebraic | 25,697 | **20,069 (78.1 %)** | 12,798 (49.8 %) | `docs/corpus-baseline-uplift.md`, `docs/corpus-class2-baseline-uplift.md` §8 |
| 2 exponentials | 965 | **594 (61.6 %)** | 593 (61.5 %) | `docs/corpus-class2-baseline-uplift.md` |
| 3 logarithms | 3,085 | **1,736 (56.3 %)** | 1,441 (46.7 %) | `docs/corpus-class3-baseline-uplift.md` |

The class-1 and class-2 figures are the 2026-08-28 re-measure under the
zero-chain `radcan(rat())` fallback (Maxima build 2026-08-20); class 3
is the milestone-3 acceptance (build 2026-08-29). The class-3 deferred
campaign (branch `class3-deferred`,
`docs/corpus-class3-deferred-uplift.md`) is re-measuring class 3; its
figure replaces the row above only once the campaign's acceptance
record is written.

## Testing

Two layers, one `Results: <n> passed, <m> failed` reading protocol
(read that line; individual assertions print `PASS:`/`FAIL:` above it,
and a run that dies mid-way prints no line at all — which is itself a
failure):

- **Layer A** — unit suite, one batch run (the TLS flag is mandatory:
  without it the run dies at the class-3 tests):
  `maxima --very-quiet -X "--tls-limit 100000" -b test_maxima_rubi.mac`
  (892 targets).
- **Layer B** — full corpus per class, sharded:
  `python3 test/launch_class_shards.py "<section>" <record> test/corpus_driver.py --launch`
  plus the `test/wait_and_merge.sh` watcher (class 1 ~80 min wall on
  24 cores). The full-run A/B against the previous merged record is
  the regression gate: `python3 test/ab_records.py <old> <new>` prints
  the transition table and every PASS→FAIL entry. The timeout re-check
  (`python3 test/launch_timeout_rerun.py … --launch`,
  `test/wait_timeout_rerun.sh`, `test/merge_timeout_rerun.py`) re-runs a
  record's `timeout` class at a larger cap and reads the transitions.

`AGENTS.md` (`## Tests`) carries the live protocol in detail.

## Layout

```
maxima_rubi.mac             public loader (diophantine mould, witness-checked)
maxima_rubi_utils.mac       runner, %mr_ predicate/shim layer, noun forms
maxima_rubi_dispatch.lisp   table dispatcher (pass-2 matchreverse rescan)
maxima_rubi_implicit1.lisp  exponent-1 rescan (Maxima drops stored ^1)
maxima_rubi_pass4.lisp      pass-4 bare-factor sweep (class-3 deferred campaign)
rules/class{1,2,3}/<key>.mac  GENERATED rule files, one per Rubi .m (do not
                            edit; class1/9_1.mac is a manual port)
generator/                  the Python generator (generate_rules.py)
test_maxima_rubi.mac        Layer A unit suite
test/                       Layer B driver, shard planner, mergers, A/B diff,
                            rules-core build, canary
probes/                     committed, re-runnable measurement probes
docs/                       research design + measured records + runbook
todo/                       milestone index and pinned reference clones
```

The generated rule files come from `generator/generate_rules.py` over
the pinned Rubi 4 clone (`reference/rubi`, gitignored working copy —
the pin is recorded in `todo/TODO.md` and in every generated file's
header). Regenerate, do not hand-edit:
`python3 generator/generate_rules.py --class <n> [--only <key>]`
(`generate_class1.py` is the class-1 shim). The one exception is
`rules/class1/9_1.mac`, a manual port (the section-9.1 legacy file is
absent from the pinned Rubi.m's LoadRules, so the generator does not
emit it).

## License

The generated rule files (`rules/class1/*.mac`) are a substantial
portion of Rubi, ported from the pinned commit, and carry the Rubi
copyright notice in their headers. Rubi is MIT:

```
MIT License

Copyright (c) 2018 Rule-Based-Integration Organization

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
