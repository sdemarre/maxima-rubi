# Class-6 corpus — rubi() acceptance record (hyperbolic functions, closed 2026-09-20)

The measured acceptance of the "6 Hyperbolic functions" port: the full
5,080-entry section under the ported rule set (`rubi()`, rules-only
default, 3,903 rules), against a native-`integrate` baseline measured on
the SAME class scheme. Ported against `docs/class-porting.md` Steps 1–10;
the ticket is `.scratch/class-ports/issues/03-class6-hyperbolic-functions.md`.

Build for every figure below: **`branch_5_50_base_84_g4204fb669`**
(2026-08-31 13:27:47) on SBCL 2.6.7. Per-entry cap **30 s CPU**.

Inputs:

- `test/corpus_class6.out` — merged package record (5080/5080, 26 files,
  12 queue workers, wall 479.1 s, harness failures 0).
- `test/corpus_class6.baseline.out` — merged `integrate` baseline
  (5080/5080, 26 shards, re-measured 2026-09-20 under the FIXED probe;
  see §3).
- `test/corpus_class6.timeout-rerun/` — the 100 s re-check of the
  record's 5 `timeout` entries.

## 1. Rule set

13 rule files / **390 rules**, every one carrying a `/;` condition.
AUTO 103 (26.4 %) / MANUAL 287 (73.6 %) — markedly more MANUAL-heavy
than class 2 (64 % AUTO); the driver is optional-capture depth, whose
histogram peaks at 6 optional names (89 rules) and reaches 13.

All 13 of the pinned clone's section-6 `.m` files are loaded — nothing is
excluded — so no residue below is an unloaded-file artifact.

Census: `probes/translation/05-class6-syntax-census.out`. Table closure
(18 unlistied tokens, all adjudicated) on the ticket; the real porting
surface was **8 functions over 53 rule-uses**, the rest mechanical rows.

Core: **rules=3903** = 3,513 + 390, fingerprint
`d624cefbd491c0a111ed481442042e40`.

## 2. Normalization

**Zero new `HEAD_REWRITES` rows.** The answer-head census
(`probes/corpus/12-class6-answer-heads.out`) finds ten non-native call
heads over the 5,080 entry lines and every one is already disposed of:
`Chi(` 611, `Shi(` 605, `Si(` 32, `Ci(` 32 by class-3 rows; `GAMMA(` 266,
`Ei(` 6 by class-2 rows; `Unintegrable(` 364 and `CannotIntegrate(` 47 are
corpus markers read before normalization; `AppellF1(` 24 has no native
(§6); `F(` 8 is a free function symbol.

Both polarities are on the record: a `6.2.2` slice reports
`head rewrites: {'expintegral_chi(': 7, 'expintegral_shi(': 7}`, and the
only change to `test/corpus_driver.py` in the whole port is the
fingerprint glob — `HEAD_REWRITES` has **zero** row changes, so classes
1–3 are unaffected by construction rather than by test.

The section's own mass is native: `sqrt(` 14,432, `sinh(` 9,101,
`cosh(` 7,660, `tanh(` 4,556, `polylog(` 2,848, `sech(` 3,000,
`coth(` 2,859, `csch(` 2,007. All six hyperbolic heads differentiate
through the harness's own `zero_chain` and float-evaluate
(`probes/answer-side/03-class6-answer-side-identities.out`).

## 3. Baseline — and the yardstick defect this port exposed

**The Step-8 baseline probe was scoring itself PASS for failing to
integrate.** `probes/corpus/probe-integrate-sample.py` classified an
entry `no-answer` whenever `integrate` returned its own noun, in BOTH
branches of its classifier — including when the corpus expects a REAL
ANSWER. `test/corpus_driver.py` splits that case out as `deferred` (FAIL)
and has done since 2026-08-25; the split was never back-ported to the
probe, so every baseline since was scored on a looser ruler than the
package record it was compared against.

Class 6 is where that finally changed a verdict, because it is the first
section whose baseline inflation exceeds the package's lead. On the
uncorrected reading the port appeared to LOSE, 14.5 % against 25.9 %.

Fixed (commit `f5ab334`) and all three baselines re-run (`1024f15`):

| section | N | baseline was | baseline now | package |
|---|---:|---|---|---|
| 2 Exponentials | 965 | 593 (61.5 %) | 363 (37.6 %) | 707 (73.3 %) |
| 3 Logarithms | 3085 | 1441 (46.7 %) | 1190 (38.6 %) | 1657 (53.7 %) |
| **6 Hyperbolic** | **5080** | **1314 (25.9 %)** | **301 (5.9 %)** | **739 (14.5 %)** |

The old-vs-new A/B isolates the fix: 230 / 250 / **1013**
`no-answer -> deferred` and **0 FAIL->PASS** in all three — the
correction only ever takes credit away. The reclassification counts are
exactly those predicted analytically before the re-run.

Drift, stated rather than hidden: the re-runs used a wider pool (12 over
38 shards, against 3/3/6 before), so 14 near-cap entries across 9,130
were charged more CPU and timed out. Exactly one crossed the PASS
boundary (a class-3 `verified -> timeout`). It is not the fix.

Class-6 baseline classes: `unverified` 3168, `deferred` 1013, `timeout`
276, `unexpected` 219, `verified` 114, `error` 103, `expected` 94,
`no-answer` 93. **Results: 301 passed, 4779 failed.**

Guard: `probes/corpus/13-baseline-noanswer-conflation` now reports 0
over-credited entries for all three sections. A nonzero count means a
record was produced without the `deferred` split.

## 4. Package run

`test/run_corpus_queue.py`, 12 workers (the host's PHYSICAL core count —
a cpu-capped verdict is only stable below the SMT threshold), 30 s cpu
cap, wall 479.1 s, harness failures 0, merge clean 5080/5080.

| class | count | % | verdict |
|---|---|---:|---|
| `verified` | 343 | 6.8 | PASS |
| `expected` | 83 | 1.6 | PASS |
| `no-answer` | 313 | 6.2 | PASS |
| `deferred` | 3173 | 62.5 | FAIL |
| `contains-noun` | 1149 | 22.6 | FAIL |
| `unverified` | 14 | 0.3 | FAIL |
| `timeout` | 5 | 0.1 | FAIL |
| **total** | **5080** | | **Results: 739 passed, 4341 failed** |

**A/B against the corrected baseline** (`test/ab_records.py`):

| | |
|---|---:|
| PASS→PASS | 104 |
| PASS→FAIL | 197 |
| FAIL→PASS | 635 |
| FAIL→FAIL | 4144 |

Net **+438 entries (+8.6 pts)**: 739 (14.5 %) against 301 (5.9 %).

**Every PASS→FAIL attributed** (197, i.e. entries `integrate` handles and
the package does not — all genuine, none yardstick, since both records
now share a ruler):

| transition | n | reading |
|---|---:|---|
| `verified -> contains-noun` | 108 | the package answers but leaves an unevaluated noun |
| `expected -> deferred` | 56 | no rule reached the integrand |
| `expected -> contains-noun` | 25 | as row 1, against a corpus-matching expectation |
| `verified -> deferred` | 6 | no rule reached it |
| `no-answer -> contains-noun` | 2 | declined cleanly before, now answers with a noun |

They are concentrated: **161 of 197 (82 %)** fall in the six catch-all
`… functions.mac` files (6.7.1 50, 6.4.2 33, 6.2.5 26, 6.1.5 21,
6.5.3 17, 6.3.2 14), which hold the least systematic integrands.

The 635 gains are led by `unverified -> verified` 287,
`unexpected -> no-answer` 212 (entries `integrate` ANSWERS though the
corpus expects a noun — the package correctly declines),
`unverified -> expected` 72, `deferred -> verified` 43.

**Timeout re-check** (100 s, the record's 5 `timeout` entries;
`test/corpus_class6.timeout-rerun/merge.out`): **now-PASS 2** —
6.1.3 e70 `expected` at 23.7 s and 6.2.5 e298 `verified` at 28.1 s, both
slow-correct just over the 30 s cap; 1 `contains-noun` at 28.4 s; 2 still
`timeout` at 100 s (6.7.1 e204/e233), i.e. genuine non-terminators. The
cap binds on 2 entries of 5,080 (0.04 %) — it is not the limiting factor
for this section.

## 5. Residues

FAIL mass is **`deferred` 3173 (73.1 %) + `contains-noun` 1149 (26.5 %)**;
`unverified` 14 and `timeout` 5 are negligible. This is a COVERAGE
profile, not a correctness one: 390 rules against 5,080 entries is
**0.077 rules per entry**, the thinnest ratio of any class ported so far
(class 3 is 0.108), and the ticket predicted a large deferred mass from
that number on 2026-08-30.

**The `.7` family is the single largest block and is ~100 % deferred:**

| corpus file | N | FAIL | dominant |
|---|---:|---:|---|
| 6.1.7 `hyper^m (a+b sinh^n)^p` | 525 | 525 (100 %) | deferred 521 |
| 6.3.7 `(d hyper)^m (a+b (c tanh)^n)^p` | 263 | 263 (100 %) | deferred 262 |
| 6.5.7 `(d hyper)^m (a+b (c sech)^n)^p` | 220 | 220 (100 %) | deferred 219 |
| 6.2.7 `hyper^m (a+b cosh^n)^p` | 85 | 85 (100 %) | deferred 85 |
| 6.4.7 `(d hyper)^m (a+b (c coth)^n)^p` | 53 | 53 (100 %) | deferred 53 |
| 6.6.7 `(d hyper)^m (a+b (c csch)^n)^p` | 27 | 27 (100 %) | deferred 26 |
| **total** | **1173** | **1173** | |

1,173 entries — 23 % of the section, 37 % of all `deferred` — reach no
rule at all. **Likely cause (stated as a guess):** these integrands are
powers of one hyperbolic in a binomial of another, and the pinned Rubi 4
section-6 files carry no rule of that shape; Rubi presumably reaches them
through machinery outside section 6 (substitution into the algebraic or
trig sections) that this port has not yet ported. It is NOT an unloaded
file — all 13 section-6 `.m` files are generated and loaded (§1). This is
the first item to investigate for a class-6 uplift and is ticketed.

The other 100 %-FAIL file is 6.2.2 `(e x)^m (a+b x^n)^p cosh` (111
entries, `contains-noun` 57 / `deferred` 54): its expected answers are
dominated by `Chi(`/`Shi(`, i.e. the rules reach it but the nested
integration does not close.

**Residue → expected-head census** (entries whose corpus expectation
carries the head, and the share of those in FAIL):

| head | entries | in FAIL | FAIL % |
|---|---:|---:|---:|
| `polylog(` | 476 | 473 | 99.4 % |
| `expintegral_chi(` | 282 | 264 | 93.6 % |
| `expintegral_shi(` | 278 | 260 | 93.5 % |
| `elliptic_f(` | 223 | 203 | 91.0 % |
| `elliptic_e(` | 219 | 211 | 96.3 % |
| `erfi(` | 195 | 102 | 52.3 % |
| `erf(` | 179 | 92 | 51.4 % |
| `hypergeometric(` | 100 | 73 | 73.0 % |
| `gamma_incomplete(` | 98 | 70 | 71.4 % |
| `AppellF1(` | 24 | 24 | 100 % |

## 6. The structural-ceiling decision (per spec §3.4, per class)

**The ceiling stands for class 6; the polylog shim is NOT triggered.**

`polylog`-carrying expectations are 476 entries of which 473 FAIL —
materially larger than class 2's block (12 unverified + 51 deferred + 3
timeout), and on its face the "material unverified block" the runbook
says would make a `polylog(2,·)` derivative shim a follow-up with that
number as its go.

It does not trigger here, because the class is wrong: of those 473, the
overwhelming majority are `deferred` or `contains-noun` — the package
never produced a `polylog`-carrying ANSWER to verify. A derivative shim
closes an `unverified` zero-chain; it cannot close a gap where no answer
was produced. `unverified` is 14 entries in the whole section. The shim
would move ~0 entries today.

The decision is therefore **deferred again, and re-armed**: if the `.7`
coverage gap above is closed and those entries start producing
`polylog`-carrying answers, the shim's go condition should be re-tested
against the resulting `unverified` mass, not against the `polylog` head
count. Same reading for `AppellF1` (24 entries, all FAIL, all
deferred/contains-noun).

## 7. Earlier-class status

Byte-identity green for classes 1, 2, 3 and 6 throughout the port
(regenerating each leaves `git status --porcelain rules/` empty).

The class-1 **table-growth probe**: 80 class-1 entries run with class 6
loaded, entry-for-entry against the committed record — PASS 64 → 64,
**zero class transitions**, cpu 0.94x. A +11 % table (3,513 → 3,903) cost
nothing measurable. Read as weak-but-real: 0.3 % of the class, biased to
each file's first entries, and the failure mode at issue (entries just
under the cap crossing it) is what a small fast sample cannot detect. The
full class-1 A/B remains the gate and has not been re-run for this port.

The class-2 and class-3 acceptance records are **amended** for the §3
baseline fix; two of their conclusions changed and are stated there.

## 8. Final gates (2026-09-20)

| gate | result |
|---|---|
| Layer A | `Results: 1066 passed, 0 failed` |
| P3 static | `Results: 15 passed, 0 failed` |
| head rewrites | `Results: 20 passed, 0 failed` |
| run-records guard | `Results: 43 passed, 0 failed` |
| byte-identity, classes 1/2/3/6 | `git status --porcelain rules/` EMPTY |
