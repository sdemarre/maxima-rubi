# Corpus and Maxima baseline (T3)

The class-1 yardstick and the state of today's `integrate` on it: the
test-suite format, the harness that measures it, the measured baseline,
and the gap profile milestone 1 plans against. Inputs:

- `probes/corpus/probe-corpus-load-sweep.{py,out}` (2026-08-17) —
  file-level load survey of the whole suite;
- `probes/corpus/probe-integrate-sample.{py,out}` (2026-08-17 sample,
  2026-08-18 full run) — the per-integral baseline driver; the
  canonical `.out` is the full 25,697-entry class-1 run, merged and
  completeness-verified (see §3.4);
- `probes/corpus/{resume-info,merge-shards}.py` — stream resume and
  shard-merge tooling, exercised by the runs below;
- `docs/pattern-matching-feasibility.md` (T2) — the measured Maxima
  semantics the harness template is built around;
- `~/src/diophantine` — the `Results:`/PASS/FAIL reading protocol this
  suite inherits (T5 §3).

Build for all measurements: `build_info()`
`branch_5_49_base_796_g60186bb22_dirty` (2026-07-28), SBCL 2.6.7
(stamped in each `.out`). Pins: suite commit in `todo/TODO.md`.

## 1. The corpus (Q1)

`reference/maxima-syntax-test-suite` @ pinned commit: 215 `.mac`
files, 8 function sections plus "Independent test suites". An entry is
one line

```
[integrand, var, steps, expected],
```

(`steps` = rule-step count from Rubi's derivation; 370 class-1
entries carry a **5th element** — two alternative expected forms,
accepted either). Class 1 ("1 Algebraic functions"): **40 files,
25,697 entries** (1.1 Binomial products 13,987; 1.2 Trinomial
products 10,330; 1.3 Miscellaneous 1,380).

*Correction*: the "17,260 integrands" quoted in T2/T4/T5 was a
pre-full-run figure; the full per-file count is 25,697,
cross-verified three ways (the load sweep's per-file `entries=`
column, a raw entry-line count, and the merge's completeness check,
§3.4). The three docs were updated.

**File-level load**: the sweep runs one fresh `maxima -b` per file —
205/215 load; **10 FATAL** (one class-1: 1.3.1 Rational functions).
Measured root cause: this build folds `(-1)^(1/3)` → `-1` and
`(-1)^(2/3)` → `1` (real-root convention), so Rubi cubic-factor
denominators like `(1+(-1)^(1/3))^2` fold to `0` and the parse dies
with `expt: undefined: 0 to a negative exponent`. Quoted lists do not
protect (constant subexpressions still fold). But per-integral
*text paste* isolates even those: 1.3.1, FATAL as a whole file,
contributes all 494 of its entries to the per-integral run below.

**"No elementary answer" marking**: class-1 noun expectations are
`CannotIntegrate(integrand, x)` in **Maxima call form** (31 entries,
7 files); other sections use `Unintegrable(integrand, x)` the same
way (suite-wide sweep: 3,047/355 occurrences). Both are plain
function nouns, not lists.

## 2. The harness (Q2, mechanics)

One fresh `maxima --very-quiet -b <one-entry batch>` **per integral**
(driver docstring explains why: a batch dies on its first Lisp error;
per-process wall cap = per-integral timeout; no flag leakage).
Per-integral template (after the §3.3 fixes):

- `mr_f: <integrand>$  mr_r: integrate(mr_f, <var>)$` — `mr_`-prefixed
  template variables (reason below);
- an answer pool (`pos$` ×6 / `no$` ×6) plus preloaded
  `batch_answers_from_file: true` — `integrate` prompts
  ("Is … positive or negative?" from `asksign`) on a query stream
  that never sees stdin; the batch file itself must answer (T3
  evidence, 2026-08-17);
- one `CLASS <class>` verdict per integral:
  - `expected` — `diff(candidate − expected, x)` closes to 0 in the
    zero-chain (equal up to a constant);
  - `verified` — `diff(candidate, x) − integrand` closes (derivative
    is the integrand) though the expected form differs;
  - `unverified` — Maxima answered but neither zero-test closed;
  - `no-answer` — Maxima returned its failed-integrate noun;
  - `unexpected` — noun-expected entry, Maxima answered;
  - `error` — subprocess died (parse/eval-time fatality, t=0.0 s);
  - `timeout` — 30 s wall hit (arbitrary cap; T5 keeps it for
    milestone 1, a tuned cap waits for this timing distribution).

**The zero-chain** (Q3): `ratsimp` → `ratsimp∘expand` → `factor` →
`ratsimp∘factor`. `simplify`/`together` are *unbound* in this build
(measured, T2/T4), so the chain is what exists. Its measured adequacy:
every `expected`/`verified` below closed inside it; the 3,102
`unverified` are the remaining gap (chain too weak, or Maxima's
answer genuinely wrong — the milestone-1 loop, T4 §4, will tell them
apart file by file).

## 3. Measured baseline (Q2, results)

### 3.1 Final classes (25,697 entries)

| class      | count | %     | meaning |
|------------|-------|-------|---------|
| `verified` | 11,313 | 44.0 | derivative closes; expected form differs beyond the chain |
| `expected` | 1,485 | 5.8 | candidate − expected has zero derivative |
| `no-answer` | 8,297 | 32.3 | Maxima returned the failed-integrate noun |
| `unverified` | 3,102 | 12.1 | Maxima answered, zero-chain did not close |
| `timeout`  | 1,260 | 4.9 | 30 s cap hit |
| `error`    | 240 | 0.9 | subprocess died at parse/eval time |
| `unexpected` | 0 | 0.0 | (noun-expected, answered) |

**12,798 (49.8%)** of class 1 has a verified antiderivative from
today's `integrate`; **12,899 (50.2%)** does not — that is the
addressable pool for milestone 1 (§5). The 31 corpus
non-integrable (noun-expected) entries: Maxima returns the noun on
all 31 (31/31 agreement, `unexpected` = 0 is meaningful, not a
detection gap, after the §3.3 fixes).

By section:

| section | total | verified | expected | no-answer | unverified | timeout | error |
|---|---|---|---|---|---|---|---|
| 1.1 Binomial products | 13,987 | 6,388 | 915 | 4,382 | 1,454 | 730 | 118 |
| 1.2 Trinomial products | 10,330 | 4,458 | 417 | 3,314 | 1,538 | 493 | 110 |
| 1.3 Miscellaneous | 1,380 | 467 | 153 | 601 | 110 | 37 | 12 |

Worst files (2026-08-18 counts over the full run):
timeouts — 1.1.1.3 (319/3,189), 1.2.1.3 (164), 1.2.1.2 (122),
1.1.2.4 (118); unverified — 1.2.1.3 (496), 1.1.1.3 (474), 1.2.1.2
(445), 1.1.3.2 (221); errors — 1.1.1.3 (92), 1.2.1.3 (56), then
≤16 per file.

### 3.2 Timing

p50 = 0.1 s, p90 = 0.2 s, p95 = 24.2 s, p99 = 30.1 s, max = 30.2 s;
18% of entries are t=0.0 s at 18-way parallelism (startup-dominated;
serial single-process runs show ~49%). Sum of per-integral walls:
**12.10 h serial-equivalent**.

### 3.3 Template traps found while running (all measured, all fixed)

The first full run (this template's predecessor) was invalidated by
three defects, each caught by measurement — the trap list T2 §3
already carries for *package* code applies to harness code too:

1. **Noun-expected detection missed the call form.** The corpus
   writes `CannotIntegrate(f, x)` / `Unintegrable(f, x)` (Maxima
   call form); the first template only matched `Unintegrable[…]`.
   Fixed: detect by name prefix.
2. **Template symbol collision (the big one).** The template bound
   the integrand to `f` and the answer to `r` — but `f` (and `r`)
   are routine corpus coefficients/exponents. Pasted integrand/
   expected text is re-parsed *in scope of those bindings*, so every
   `f`/`r` inside pasted text re-evaluates to the integrand/answer
   it should have been compared against. Measured signature: for a
   noun `r`, `is(part(r,1) = <re-pasted integrand text>)` →
   **false** while `is(part(r,1) = <bound symbol>)` → **true**.
   Consequence in the first run: f-containing noun entries fell into
   the zero-chain on corrupted expressions (contributing to 2,110
   timeouts and 3,019 unverified there), and 12 noun-expected
   entries were mislabeled `unexpected`. Fixed: all template
   variables carry the `mr_`/`MR_` prefix (never a corpus symbol).
3. **`part`/`length` noun detection false-positives on products.**
   `length(5*x)` → 2 and `part(5*x,1)`/`part(5*x,2)` match the
   noun's `[f, x]` shape, so a product answer `integrand*x`
   (every constant integrand) was misread as a failed noun.
   Candidate detectors measured for the fix: `islist`/`isatom`
   stay unevaluated on the noun (same trap as T2);
   `is(equal(op(r), integrate))` → `unknown` (the noun's op
   *prints* `integrate` but is not the bare symbol);
   quoted equality `is(r = 'integrate(f, x))` is **true for
   successful integrations too** (`is(5*x = 'integrate(5,x))` →
   true). What works: **`is(string(op(mr_r)) = "integrate")`** —
   `string(op())` reads "integrate" for the noun, `"*"`/`"+"`/`"^"`
   for answers. That is the detector in use.

Transition accounting (first run → fixed run, over 25,697 shared
keys): 23,092 unchanged; the rest moved mostly
timeout→no-answer (620), verified→no-answer (194),
timeout→verified (168), error→no-answer (50) — i.e., the corrupted
comparisons are what had hidden 873 Maxima nouns.

### 3.4 Run history and the parallel machinery

All wall times on this 24-core box, the build stamped above:

1. **Sample** (2026-08-17): 199 integrals, 969 s, established the
   classification + zero-chain + answer-pool mechanics.
2. **First full run** (buggy template): serial phase 1 6 h wall cap →
   7,284 entries; serial resume ~3 h → 13,175; then an 8-way shard of
   the tail: 3.28 h wall for 9.75 h serial-equivalent (max
   single-shard 11,809.5 s). Result: complete but invalidated (§3.3).
3. **Second full run** (fixed template, 2026-08-18, the numbers in
   §3.1): **18 parallel workers, 2.17 h wall for 12.03 h
   serial-equivalent (≈5.5×)**.

Sharding mechanics (committing this because it took two attempts to
get right): the driver's `per-file` cap applies to **every** file in
its range, so a range spanning several files can only cap the last
file when the cap ≥ every intermediate file's length. First attempt
violated that (a 1,708-entry overlap, caught by the merge's dupe
check); the valid plan used: split any file >1,700 entries into
parts, give each partial part its **own single-file range**
(`start=stop-1`, `skip`, `per-file` = part end), and chain whole
files under `per-file` = max file length, with a driver-simulation
assertion per segment before launch (the planner prints
`VALID`). `merge-shards.py` then parses all shard `.out`s, asserts
the (file, entry) key set is exactly the full corpus
(25,697/25,697, no dupes/missing/extra), re-sorts into corpus order,
and writes one canonical `.out` with a single header and summary.
On a 24-core box, 16–18 workers is the sweet spot; the critical
path is the slowest single-file part (here 2 of 1.1.1.3).

## 4. Gap profile (Q4)

Milestone 1's acceptance yardstick = the class-1 corpus; the uplift
baseline, per entry:

- **12,798 (49.8%)** — `integrate` already has a verified
  antiderivative. Rubi must at least not regress these (the Layer-B
  suite, T5 §3, watches them).
- **12,899 (50.2%)** — no verified antiderivative today:
  8,297 noun failures (of which 31 are the corpus's own
  non-integrable entries, where failing is *correct*), 3,102
  unverifiable answers, 1,260 timeouts, 240 parse/eval fatalities.
  Rubi's win is a fraction of these — expected to concentrate where
  the timeouts/unverified cluster (1.1.1.3, 1.2.1.2/1.2.1.3,
  1.1.3.2).
- The 240 fatal entries are the harness's hard edge: they kill the
  30 s subprocess at t=0.0 s (parse-time constant folds, §1). The
  milestone-1 driver must count them as `error` (FAIL-able) but
  survive them — one subprocess each already guarantees that; the
  per-entry bisect tool from the load sweep is the diagnostic if a
  batch form is ever needed.

Q5 (sympy_rubi as oracle for doubtful expected-answers): superseded
by T4 §5 — sympy's Rubi port is dead prior art (removed 2022,
generator and utility layer buggy), so no independent oracle exists
to cross-check corpus expectations; the corpus is taken as ground
truth, and `unexpected`-class entries are the disagreement watchlist.

## 5. Standing cost and re-run discipline

- Full class-1 suite: **≈12 h serial-equivalent ≈ 2.2 h wall at 18
  workers** (this box, this build) — paid a few times per class, not
  per change; the per-change gate is the Layer-A unit suite (T5).
- The baseline is **build-specific** (T4 §6 build drift: staples
  missing from this binary return in later ones). On the 5.50
  upgrade: re-run the sample probe, then the 18-shard plan, then
  `merge-shards.py`; the doc's tables are the diff.
- The 30 s cap stayed at T3's arbitrary value (kept for milestone 1
  by T5's decision); the p95=24.2 s measured here says the cap clips
  a long tail that no cap below ~60 s removes.
