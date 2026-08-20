# Package and harness architecture (T5)

The shape the milestone-1 implementation takes: public API, load story,
test harness, and the house rules the code lives under. This is a design
document — every decision cites the measurement or trap that forces it:

- `docs/pattern-matching-feasibility.md` (T2) — runner contract, the
  measured-semantics trap catalog (T2 §3, seven matcher items plus the
  batch-parser contract), 0.007 ms/match, the N/D/M decision;
- `docs/rule-translation.md` (T4) — generated rule-file format, the
  shim layer and the §6 build-drift caveat;
- T3's established harness — `probes/corpus/probe-integrate-sample.py`
  (+ `resume-info.py`), whose docstring and `todo/t3-corpus-baseline.md`
  evidence section record the per-integral subprocess mechanics, the
  zero-test chain, the answer pool, and the noun-integral shape;
- `docs/rubi-architecture.md` (T1) — the rule grammar and dispatch
  order the runner reproduces;
- `~/src/diophantine` (read 2026-08-18) — the house this package is
  built in: `diophantine_solver.mac` (loader + witness idiom, verbose
  flag), `test_diophantine_solver.mac` (Results protocol, `is`-based
  three-valued assertions), `CLAUDE.md` (the quote-on-both-sides house
  rule);
- a same-session probe of the witness idiom's primitives in the
  installed build: `?fboundp(f)` → `false`, `errcatch(load("…"))` →
  `[]` on a miss, `load_pathname` → `false` under `-b`, `sconcat`
  works (2026-08-18, `branch_5_49_base_796_g60186bb22_dirty`).

## 1. Q1 — public API

```
rubi(f, x)       antiderivative, or else `integrate(f, x)` (which is
                 Maxima's own noun form when Maxima also fails)
rubi_verbose     global flag, default false (diophantine idiom);
                 when true the runner prints `rule: <file> r<n>` on
                 every fire
```

- **Name**: `rubi` (the working name from t5). One function is the
  whole public surface; rule sections, predicates and shims are
  internal.
- **Result shape**: the t5 spec — antiderivative, or the `%integrate`
  noun when no rule fires. Concretely, `rubi(f, x)` returns
  `integrate(f, x)` when the rule table does not fire, so the noun
  form is Maxima's own (T3 measured it: a list-structured noun,
  `atom(r)` false, `length(r) = 2`, parts `f` and `x`). This is the
  faithful Rubi semantics — Rubi's `Int` maps to the host system's
  `Integrate` when no rule fires — and it keeps the T3 vocabulary
  (expected/verified/unverified/no-answer) directly reusable as
  verdict classes.
- **Recursion**: a rule replacement containing `Int[smaller, x]` (87%
  of class-1 rules, T1) generates `rubi(smaller, x)` — plain
  evaluation into the same API, exactly as T2's runner contract
  prescribes ("the runner does not loop"). A depth counter with a
  cap (candidate: 16, to be set against corpus-observed recursion)
  turns a runaway into the fall-through noun instead of a Lisp
  stack overflow.
- **Verboseness**: `rubi_verbose` (diophantine's
  `diophantine_verbose` idiom), plus the rule identity
  `<file> r<n>` the generator already embeds in every rule name (T4 §3)
  — the print is the debug view, nothing else to build.

## 2. Q2 — load story (diophantine mould)

Flat layout at the repo root (diophantine's shape, not `share/`):

```
maxima_rubi.mac          public loader
maxima_rubi_utils.mac    runner + shims (T4 §6) + ported predicates
rules/class1/<file>.mac  generated table, one per Rubi .m (T4 §3)
test_maxima_rubi.mac     main suite (diophantine protocol)
```

`maxima_rubi.mac` resolves each sibling exactly like
`%dio_load_sibling` — first against `pathname_directory(load_pathname)`,
then bare — then **witness-checks** it:

```
%mr_load_sibling(fname, witness)
   dir : if load_pathname = false then "" else pathname_directory(load_pathname)
   errcatch(load(sconcat(dir, fname)))
   if ?fboundp(witness) = false then error("…could not load the sibling file …")
```

(All four primitives verified in this build this session; the error
text, like diophantine's, lists the four installation paths:
full-path load, run from the directory, push onto `file_search_maxima`,
install under `~/.maxima/`. The witness is a symbol defined only at
the end of the sibling file, so a truncated or mis-parsed load fails
loudly at load time — diophantine's measured history is that a missed
sibling load otherwise "carried on and was silent, which is the defect
class"). The rules files carry the same witness per file, and the
per-file rule count is checked against the T4 census at load time (the
`mr_rules_count` cross-check of T4 §4).

**No `.lisp` sibling in milestone 1.** T2's measurement (0.007 ms/match;
a 500-rule family is ~3.5 ms worst case, against 0.3 s–30 s
per-integral walls) is the evidence that the runner and the matcher
can stay at Maxima level; diophantine's compiled-Lisp siblings exist
because its elliptic scan hit 11 s of interpreted arithmetic — a
profile no part of milestone 1 has. If T2's option M (matcher
extension) is ever triggered, the constraint to remember is
diophantine's: multi-line Lisp cannot go through `:lisp` in a batch
file (single-line read), it must be a sibling `.lisp` + `load`.

## 3. Q3 — test harness, two layers

### Layer A — unit suite (diophantine protocol)

`maxima --very-quiet -b test_maxima_rubi.mac` is the gate for every
change; it ends

```
Results: <n> passed, <m> failed
```

with `quit()`; individual assertions print `PASS:`/`FAIL:` above it,
and a run that dies mid-way with a Maxima error prints **no** Results
line, which is itself a failure (AGENTS.md). Assertions use
diophantine's `check`/`check_bool` shape with `is()`-based three-valued
dispatch — required here as well, since this build's `is` was measured
to return `unknown` (T4 support-surface: `is(x > 0)` → `unknown`), the
same third value diophantine's item 19 was built for.

Contents: (a) each ported predicate and shim against fixed
input/output pairs drawn from its .m semantics (T4's unit-probe
requirement); (b) the T2 trap catalog as regression tests (T8
decomposition/veto, T11 rebind, T13a/b `is`-wrapping and
`filter`-noun, T14 kill-redefine, capture-list order); (c) a handful
of hand-verified integrals pinning the API end to end.

### Layer B — corpus suite (Python driver)

The class-1 yardstick is the 25,697-integrand corpus section
(`docs/corpus-baseline.md`); the
driver is the generalization of T3's `probe-integrate-sample.py`
(same mechanics, package instead of `integrate`):

- one **fresh `maxima --very-quiet -b` subprocess per integral** — a
  batch dies on its first Lisp error, and a per-process wall cap is
  the per-integral timeout (30 s — T3's arbitrary value, kept for
  milestone 1; the full-run timing distribution, when it lands, is
  what a tuned cap would be set from);
- a `--preload` file sets `batch_answers_from_file: true` and the
  batch carries the `pos$/no$` answer pool (T3's measured mechanics;
  the package itself must never prompt — see §4.8);
- per integral the driver prints one `PASS:`/`FAIL:` line from the
  batch's CLASS line, and the run ends with the same
  `Results: <n> passed, <m> failed` line Layer A uses, so both layers
  share one reading protocol:

| T3 CLASS (inside Maxima) | verdict  |
|--------------------------|----------|
| `expected`    candidate − corpus expectation closes to 0 under the zero-test chain | PASS |
| `verified`    `diff(candidate, x) − f` closes to 0 (expected did not) | PASS |
| `no-answer`   corpus expects a noun and `rubi(f, x)` falls through to one | PASS |
| `unverified`  neither zero-test closed | FAIL |
| `unexpected`  corpus expects a noun, package answered | FAIL |
| `error` / `timeout` | FAIL (subprocess died / cap hit) |

- **Verification**: differentiation is primary
  (`diff(rubi(f, x), x) − f`), exact-match against the corpus
  expectation secondary (computed on `candidate − expectation`), both
  through the **zero-test chain `ratsimp` → `ratsimp(expand)` →
  `factor` → `ratsimp(factor)`** (T2: `simplify` and `together` are
  unbound in this build). 5-element entries (two alternative expected
  forms) pass if either closes (T3).
- **Streaming + resume**: one line per integral appended as it
  completes; `probes/corpus/resume-info.py` + the driver's
  start-index/skip-entries arguments resume a capped run exactly
  (implemented and smoke-tested for T3 this session; the full class-1
  run is ~10 h at the measured rate, so a resumed batched run is the
  only feasible form).

## 4. Q4 — house rules (measured traps → rules)

The code lives under these, each one earned by a measurement:

1. **Quote data symbols on both sides** — assoc keys and branch tags
   are data; a bare symbol means whatever the caller last bound it to
   (dynamic scoping). Diophantine's house rule and its measured
   corruptions (symmetric key corruption that still "matched by
   accident"; a branch tag leaking into the emitted answer).
2. **Booleans through `is(…)`; the third value `unknown` is not
   true.** T2 §3.4 (booleans in value position need `is(...)`) and T4
   (this build's `is(x > 0)` → `unknown` — a third value, not an
   error). Every generated guard and every ported predicate dispatches
   on `true`/`false`/else.
3. **Value-position comparisons do not evaluate** — `2 > 1` prints as
   `2 > 1`, `2 = 2` stays an equation (T2, T4). A guard is
   `is(a > b)` or a ported predicate, never a bare comparison used as
   a value; `if`-conditions do evaluate them, which is exactly why
   the difference is a trap rather than a break.
4. **Guards are value-carrying `if … then A else B`.** A bare `if cond
   then A` inside a `block` does not terminate the block — the block
   returns the last expression (T2, the bug that produced 24 false
   FAILs in the first feature probe).
5. **No `filter`; use `map`.** `filter` returns its unevaluated noun in
   this build even with a named function (T2); `map(lambda(…))`
   evaluates.
6. **Fresh names per rule, never killed at runtime.** Capture
   variables are bound globally as a side effect of matching (T11),
   and `defmatch` from a killed name misbehaves nondeterministically
   (T14). The generator's `_mr_<file>_r<n>_<var>` names (T4 §3) satisfy
   both; the runner must not `kill` anything it loaded.
7. **Internal names carry `%mr_`; shims never take the native name.**
   The installed binary documents names it does not bind (`atanh`,
   `elliptic_f` — T4 §6), so this build's absent staples may return in
   a later one; a Maxima-level definition under the native name would
   mask the real builtin the moment it appears. `%mr_coeff`,
   `%mr_atanh`, … + the generator's translation table is the
   seam; the re-audit on upgrade is one `.run` command.
8. **The package never prompts.** No `asksign` in generated code —
   sign questions go through `is`/`sign` and their `unknown`/`pnz`
   outcomes (T4). T3's answer pool is a harness safety net for
   Maxima's own `integrate` fall-through, never a package feature.
9. **Noun discipline.** Three distinct no-answer objects must never
   be conflated: the package fall-through noun (a list-structured
   `integrate(f, x)`, `atom`-guarded, T3), a rule's `Int[smaller, x]`
   (translated to `rubi(smaller, x)`), and corpus-expected noun
   entries (`Unintegrable[...]`/`CannotIntegrate[...]`).
10. **`:lisp` in a batch reads one line** — multi-line Lisp is a
    sibling `.lisp` + `load` (diophantine's stated constraint; kept
    for the day option M is triggered).

## 5. Scale and open measurements

- Load: `defmatch` compilation happens at load time, and its wall is
  MEASURED (2026-08-20, build branch_5_49_base_796_g60186bb22_dirty,
  probes/load_wall/probe-load-wall.out). It is a hard process-level
  PATTERN BUDGET, not a timing problem: 1,200 plain `defmatch`
  patterns load, 1,600 die with SBCL's fatal "Thread local storage
  exhausted" (uncatchable by `errcatch`). A real class-1 rule costs
  between about 3.3 and about 5.4 plain patterns (the two bounds from
  the 1200/1600 budget and the 294/361 wall). Consequences on this
  build: the class-1 load list holds files 1-7 (294 rules, ~0.6 s) in
  one process; file 8 (361 cumulative) is FATAL; so the loader does
  NOT call `mr_load_class1_all()` (it exists, for a build with the
  headroom — 5.50 is expected to improve pattern matching). Each
  generated file loads fine alone (67/67 verified, one process per
  file), and `unload()` releases a file's patterns from the budget, so
  files can be swapped. The D-fan-out tail question (2,684 rules carry
  ≥1 optional; histogram in the T4 census) is moot on this build — the
  wall is hit on pattern count long before it is a time problem.
- Test wall: the class-1 corpus suite is ~12.1 h serial-equivalent at
  T3's measured rate; the full run took 2.2 h wall on 18 parallel
  workers (T3 §3.4) — the standing cost of the yardstick, paid a few
  times per class, not per change. The per-change gate is Layer A
  (seconds).
- Open (implementation-phase, not research-phase): the recursion cap
  value, the zero-test chain's adequacy against the T3 23-unverified
  sample (the strengthen-the-chain loop of T4 §4), and whether
  corpus-expected elliptic answers differentiate back in this build
  (T4 §2 flagged `elliptic_f`'s missing binding as a verification
  risk, not an answer-emission risk).
