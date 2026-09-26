# Class-8 corpus — rubi() acceptance record (special functions, Step 10 written 2026-09-26)

The measured acceptance of the "8 Special functions" port: the full
1,949-entry section under the ported rule set (`rubi()`, rules-only
default, 7,776 rules — the four ports of branch `class-ports` together),
against a native-`integrate` baseline on the same class scheme. Ported
against `docs/class-porting.md` Steps 1–10; the ticket, which carries the
Step 1–7 records, is `.scratch/class-ports/issues/01-class8-special-functions.md`.
Class 8 was ported first in the queue 8 → 5 → 7 → 4 (class 6 had been
ported before, 2026-09-20), and it takes 9.1 "Derivative integration
rules" with it (section-9 spec 2026-09-22 §0.3.3: its only corpus is
8.10 Formal derivatives).

Build for every figure below: **`branch_5_50_base_84_g4204fb669`**
(2026-08-31 13:27:47) on SBCL 2.6.7, stamped in every record header.
Per-entry cap **30 s CPU** (package), **30 s wall** (baseline, §3).

Inputs (all committed on `class-ports`):

- `test/corpus_class8.final.out` — the package record: 1,949/1,949,
  `test/run_corpus_queue.py`, 24 workers, merged 2026-09-25 20:02 UTC;
  rules core **`89bec424959947761abb9416d993bee6`** (7,776 rules, built
  at `c2deb32`; `test/class_ports_final.log`). Harness failures 0.
- `test/corpus_class8.baseline.out` — the native-`integrate` baseline:
  one shard per corpus file, a 12-process pool (`test/run_baseline_pool.py`),
  merged 2026-09-25 10:32 UTC.
- `test/corpus_class8.ports.out` — the pre-fix package record (core
  `4daae7ac`, 7,776 rules, `4ed1877`), the same runner; the §4.3 A/B.
- `test/corpus_class8.final.timeout-rerun/` — the 100 s re-check of the
  record's 27 `timeout` entries (`corpus_class8.final.timeout100s.out`,
  `merge.out`).
- `test/final_ab_baseline_class8.out`, `test/final_ab_prefix_class8.out` —
  the two A/Bs as `test/ab_records.py` printed them.
- `probes/corpus/28-class-ports-acceptance.{py,run,out}` — every count
  in §4–§6 not read off one of the files above: the histograms, per-file
  tables, the residue → expected-head census, the Rubi-marker split, the
  sample entries, and the unloaded-file listing. Static, no Maxima.

## 1. Rule set

**9 loaded rule files / 307 rules + 9.1 Derivative 21 rules = 328**
(8.1 69, 8.2 55, 8.3 26, 8.4 29, 8.5 29, 8.6 24, 8.7 5, 8.8 26, 8.9 44;
`probes/translation/09-class8-syntax-census.out` and its closure probe),
every rule with a `/;` condition, no `LoadShowSteps` wrapper. 9.1 is
generated as `rules/class8/9_1d.mac`, key `9_1d` (the key `9_1` belongs
to the legacy class-1 file). AUTO 1 / MANUAL 306 by the census's tiers —
meaningless here: nearly every C-tier token is a special-function head
the table maps 1:1 (ticket 01, Step 1 A).

**One file excluded:** `8.10 Bessel functions.m` (3 `Int[` lines, found
verbatim in no loaded file) — its `LoadRules` line in `Rubi.m` (L352) is
commented out, the only commented `LoadRules` in the pinned `Rubi.m`
(probe 28's listing; the census and the generator's `load_class_files`
now comment-strip `Rubi.m`, ticket 01 Step 1). The section's corpus has
no Bessel file, so no residue below is an unloaded-file artifact.

Table after the port: **4,325** (3,997 + 328), fingerprint
`412bfc4f…` at Step 6; the final core is the four ports together,
7,776 rules. 8.9 r44 (a bare-`u_` record) lands in the tail, between the
class-4 bridge records and 9.3 (`test/test_rule_table_order.mac`,
18/0 at the final code).

The porting surface (ticket 01, Steps 2–4): seven native RENAME rows
(`ProductLog` → `lambert_w`, `FresnelS/C` → `fresnel_s/c`, `Erfc`,
`SinIntegral`/`CosIntegral` → `expintegral_si/ci`, `ExpIntegralE`), 
`HypergeometricPFQ` → `hypergeometric`, and three emitter cases:
`PolyGamma[n,z]` → `psi[n](z)`; the 2-argument (Hurwitz) `Zeta[s,z]`
emitted as the corpus's own head `Zeta(s, z)`, an inert noun (Maxima has
no symbolic Hurwitz zeta); and `Derivative[n][f][u]` as Maxima's own
derivative noun `'diff(f(u), u, n)` (order 0 = `f(u)`), the
representation decided by measurement (probe
`probes/answer-side/04-class8-answer-side-identities.out` D1–D3,
N1–N17). Step 4 ported `FunctionOfExpnQ` (FunctionOfQ's general arm),
`SubstForAux`, the formal-derivative reading of `CalculusQ`, and fixed
two capture traps the 8.10 integrands hit (`rubi`/`mr_int`'s parameter
named `f`; `apply(op(u), …)` → `funmake`).

## 2. Normalization

`HEAD_REWRITES` (ticket 01 Step 7): `GAMMA(` and `Ei(` became
**arity-dispatched** (2-arg `Ei` → `expintegral_e`, 1-arg `GAMMA` →
`gamma`; measured no-op for the accepted sections, which carry only
1-arg `Ei` and 2-arg `GAMMA`), six new native rows (`ProductLog(`,
`FresnelS(`, `FresnelC(`, `lnGAMMA(` → `log_gamma(`,
`HypergeometricPFQ(` → `hypergeometric(`, `Factorial(`), and two
**structural** rewrites: `Derivative(A)(B)(C)` → `%mr_derivative(A, B, C)`
(balanced parentheses, nested derivatives included, on the integrand and
the expected texts) and `Psi(n,z)` → `psi[n](z)`.
`test/test_head_rewrites.py` 20 → 47 at the port (64/0 at the final code,
§7). No-op over every entry of every other section, measured without
Maxima (`probes/corpus/16-class8-head-rewrite-noop.out`): 0 normalized
texts differ from the base `cd0a421` in sections 1/2/3/6; section 8's
rewrite totals equal the Step-1 census (Derivative 320, Psi 77, GAMMA
18 + 690, Ei 472 + 334, ProductLog 1,695, …).

Not rewritten: `Si/Ci/Shi/Chi/Li` (class-3 rows), `Zeta(` (the inert
noun, §6), `Unintegrable(`/`CannotIntegrate(` (corpus markers), the free
function symbols `f(`/`g(`/`F(`.

## 3. Baseline (native `integrate`)

`probes/corpus/probe-integrate-sample.py` through `test/run_baseline_pool.py`
(10 per-file shards, 12 processes; the probe's cap is a **30 s wall**
cap — `probe-integrate-sample.py` L9 — where the package's is cpu; the
class-6 record's baseline is the same probe, so the two records compare
alike; AGENTS.md measures the wall/cpu shift near the cap at 0.84–1.00).
The probe carries the `deferred` split (class-6 record §3; guard
`probes/corpus/13-baseline-noanswer-conflation`).

| class | count | % |
|---|---:|---:|
| `deferred` | 1594 | 81.8 |
| `no-answer` | 241 | 12.4 |
| `verified` | 79 | 4.1 |
| `unverified` | 24 | 1.2 |
| `expected` | 7 | 0.4 |
| `unexpected` | 4 | 0.2 |
| **total** | **1949** | **Results: 327 passed, 1622 failed** |

`integrate` returns its own noun on 81.8 % of the section: the corpus's
special-function integrands are outside its reach, not slow (0 timeouts).

## 4. Package run

### 4.1 Verdicts

Queue runner, 24 workers, 30 s cpu cap, merged 4 min after launch
(`test/class_ports_final.log`), harness failures 0, merge clean
1949/1949 (`test/final_merge_class8.out`).

| class | count | % | verdict |
|---|---:|---:|---|
| `verified` | 1138 | 58.4 | PASS |
| `no-answer` | 220 | 11.3 | PASS |
| `expected` | 179 | 9.2 | PASS |
| `contains-noun` | 368 | 18.9 | FAIL |
| `timeout` | 27 | 1.4 | FAIL |
| `unverified` | 13 | 0.7 | FAIL |
| `deferred` | 4 | 0.2 | FAIL |
| **total** | **1949** | | **Results: 1537 passed, 412 failed** |

**1,537 / 1,949 (78.9 %) against the baseline's 327 (16.8 %): net +1,210
(+62.1 pts).**

### 4.2 A/B against the baseline (`test/final_ab_baseline_class8.out`)

| | |
|---:|---:|
| PASS→PASS | 300 |
| PASS→FAIL | 27 |
| FAIL→PASS | 1237 |
| FAIL→FAIL | 385 |

Key sets equal (0 missing, 0 extra). The gains are led by
`deferred -> verified` 1,032, `deferred -> expected` 177,
`unverified -> verified` 24. The 27 PASS→FAIL fall in 8.9 (20), 8.10 (4),
8.1 (2) and 8.3 (1); by class they are `no-answer -> contains-noun` 25 and
`verified -> contains-noun` 2.

### 4.3 The class-ports fixes (pre-fix → final, `test/final_ab_prefix_class8.out`)

Between the first run of the four ports (core `4daae7ac`, `4ed1877`) and
this record the branch took the class-ports fixes (`git log
4ed1877..39eba80`): the symbolic EqQ/NeQ zero test (`d0f0237`,
`.scratch/matcher-translation-fixes/issues/03`), native
`atanh`/`asinh`/`acosh` in every class (`025c589`, ticket 18),
two-argument `Expand[u, x]` → `%mr_expand` everywhere (`e799ea6`,
ticket 19), ExpandIntegrand's reciprocal-atom guard (`3bb8c4f`), the
rule-record globals kept off Maxima's `values` list (`1ebef70`, fix V),
the depth cap 16 → 32 (`2ee8fc4`, fix E), `Subst` a plain `subst`
(`e67e2eb`, fix D) and Rubi's two-valued GtQ/LtQ/GeQ/LeQ (`39eba80`,
`.scratch/matcher-translation-fixes/issues/02`); then the master merge
`96b2722`, which brought records and ticket 21 but no code.

| | |
|---:|---:|
| PASS→PASS | 1496 |
| PASS→FAIL | **0** |
| FAIL→PASS | 41 |
| FAIL→FAIL | 412 |

1,496 → 1,537. Timeouts 48 → 27; the sum of the record's per-entry cpu
fell 10,304 s → 3,167 s and the median entry 2.6 s → 0.6 s (probe 28;
both sums are truncated at the cap, so the ratio understates the
speed-up). Fix V is the likely main carrier of the speed (its commit
measures ~3.5x on master); the per-fix split is not measured here.

### 4.3a PASS->FAIL attribution (pre-fix -> final)

Evidence: `probes/class-ports/final/attribution.{py,out}` (`3deddb7`). Each fix was reverted
alone on the final core (switch arms and overlays), a commit bisect ran over cores built at every
class-ports-fixes commit, and timings are alternating sequential runs. Build
`branch_5_50_base_84_g4204fb669`, 2026-09-26.

None: the final record loses no entry against the pre-fix class-ports record (0 PASS->FAIL, 41 FAIL->PASS).

### 4.4 Timeout re-check (100 s)

All 27 `timeout` entries re-run at a 100 s cap, 12 workers
(`test/corpus_class8.final.timeout-rerun/merge.out`, 27/27):

| at 100 s | n |
|---|---:|
| `timeout` | 20 |
| `contains-noun` | 4 |
| `expected` (now PASS) | 1 |
| `unverified` | 1 |
| `error` | 1 |

The 20 still timing out: 8.3 Exponential integral functions 15, 8.9 3,
8.6 2. **The cap binds on 1 entry of 1,949**; at 100 s the section would
read 1,538.

## 5. Residues

FAIL mass **412 = `contains-noun` 368 (89 %) + `timeout` 27 +
`unverified` 13 + `deferred` 4**. Unlike class 6 this is not a coverage
profile (`deferred` is 4 entries): the rules reach almost every
integrand, and what fails is the answer carrying a noun.

**Most of that noun mass is Rubi's own.** Probe 28 splits the entries by
the corpus's expected answer: 245 expect a top-level
`Unintegrable`/`CannotIntegrate` (220 of them PASS as `no-answer`, 25 are
`contains-noun`), and **141 expect a partial answer that carries one
inside** (`-erf(a+b*x)/(d*(c+d*x)) + 2*b*Unintegrable(…)`) — 138 of those
are `contains-noun`. The driver classifies any answer carrying a noun as
`contains-noun` before comparing (`test/corpus_driver.py`, the `has_noun`
branch ahead of the zero chain), so **an answer identical to Rubi's
partial answer cannot PASS**. 163 of the 368 `contains-noun` (44 %) are
entries where Rubi itself returns no noun-free answer. This is a
harness ceiling, filed as `.scratch/corpus-harness/issues/05`.

| corpus file | N | PASS base | PASS final | FAIL | FAIL by class |
|---|---:|---:|---:|---:|---|
| 8.8 Polylogarithm function | 198 | 13 | 52 | **146** | contains-noun 131, unverified 12, timeout 2, deferred 1 |
| 8.6 Gamma functions | 233 | 25 | 182 | 51 | contains-noun 45, deferred 3, timeout 3 |
| 8.3 Exponential integral functions | 208 | 26 | 159 | 49 | contains-noun 31, timeout 18 |
| 8.1 Error functions | 311 | 116 | 266 | 45 | contains-noun 45 |
| 8.2 Fresnel integral functions | 218 | 22 | 180 | 38 | contains-noun 38 |
| 8.10 Formal derivatives | 97 | 9 | 72 | 25 | contains-noun 24, timeout 1 |
| 8.9 Product logarithm function | 398 | 58 | 373 | 25 | contains-noun 22, timeout 3 |
| 8.4 Trig integral functions | 136 | 28 | 122 | 14 | contains-noun 14 |
| 8.5 Hyperbolic integral functions | 136 | 28 | 122 | 14 | contains-noun 14 |
| 8.7 Zeta function | 14 | 2 | 9 | 5 | contains-noun 4, unverified 1 |

Readings (sample entries from probe 28, with the record's cpu time):

- **8.8 Polylogarithm — the one real block (146, 35 % of the FAIL mass).**
  `x^4*polylog(2,a*x)` e1 (0.3 s), `(d*x)^(3/2)*polylog(2,a*x^2)` e72
  (0.4 s) — `contains-noun` in under a second, so a reach question, not
  cost; none of the file's 131 `contains-noun` is an interior-marker
  entry. `polylog(2,c*(a+b*x))` e126 answers but does not verify
  (`unverified`, 0.4 s); `polylog(2,c*(a+b*x))/(d+e*x)^4` e144 times out.
  Likely cause (unmeasured): the order-lowering chain
  `Int[x^m PolyLog[n, a x^q]]` → `PolyLog[n-1, …]` reaches a sub-integral
  the port leaves as a noun — the first item to trace for a class-8
  uplift. Of the section's 35 `hypergeometric(`-expected entries, 34 FAIL
  `contains-noun`.
- **8.1 / 8.2: entirely Rubi's partial answers.** All 45 (8.1) and all 38
  (8.2) FAIL entries expect an interior marker (`erf(a+b*x)/(c+d*x)^2` e20,
  `FresnelS(b*x)^2/x^2` e40) — the harness ceiling above, not a port gap.
- **8.3 / 8.6: the `Ei(-n, ·)` / `GAMMA(-n, ·)` families.**
  `Ei(-1,a+b*x)/(c+d*x)^2` e105, `(c+d*x)^4*Ei(-3,a+b*x)` e115,
  `GAMMA(-2,a+b*x)/(c+d*x)^4` e152 time out; 15 of 8.3's 18 still do at
  100 s — non-terminators on the 2-argument `expintegral_e` recursions
  (likely). 8.6 e13/e115 `GAMMA(1,a*x)/x`, `GAMMA(1,a+b*x)/(c+d*x)` are
  `deferred` (no rule reached them; unmeasured why).
- **8.10 Formal derivatives (9.1): the product rule.**
  `g(x)*Derivative(1)(f)(x)+f(x)*Derivative(1)(g)(x)` e24 answers with a
  noun in 0.2 s — the finding recorded at Step 7 (ticket 01, finding 1):
  on the full table `1.4.1 r7`, a bare-`u_` BODY exception
  (`.scratch/class-ports/issues/07`), splits the sum before 9.1 r19 is
  tried, where Rubi's specificity order tries r19 first. 15 of the 24
  `contains-noun` are interior-marker entries
  (`sin(a+b*x)*Derivative(1)(f)(x)` e54 expects `-b*CannotIntegrate(…)+…`).
- **8.9 ProductLog:** 22 `contains-noun` expect `CannotIntegrate(…)` times
  a factor (`1/(x*sqrt(c*ProductLog(a+b*x)))` e41); 3 timeouts on
  `x^m*ProductLog(a*x)` e145 and kin, still timing out at 100 s.

**Residue → expected-head census** (entries whose corpus expectation
carries the head, corpus spelling; probe 28):

| head | entries | in FAIL | FAIL % |
|---|---:|---:|---:|
| `polylog(` | 197 | 145 | 73.6 |
| `Unintegrable(` | 203 | 101 | 49.8 |
| `CannotIntegrate(` | 183 | 65 | 35.5 |
| `Ei(` | 339 | 58 | 17.1 |
| `GAMMA(` | 213 | 44 | 20.7 |
| `hypergeometric(` | 35 | 34 | 97.1 |
| `ProductLog(` | 398 | 25 | 6.3 |
| `FresnelS(` / `FresnelC(` | 140 / 139 | 25 / 25 | 17.9 / 18.0 |
| `erf(` / `erfi(` | 203 / 183 | 24 / 15 | 11.8 / 8.2 |
| `Ci(` / `Si(` / `Shi(` / `Chi(` | 105 / 110 / 91 / 90 | 21 / 13 / 13 / 11 | 20.0 / 11.8 / 14.3 / 12.2 |
| `Derivative(` | 54 | 19 | 35.2 |
| `Psi(` | 30 | 9 | 30.0 |
| `Zeta(` | 7 | 2 | 28.6 |
| `HypergeometricPFQ(` | 109 | 0 | 0.0 |

## 6. Structural ceilings (per spec §3.4, per class)

- **polylog: the ceiling stands for class 8; no shim is triggered here.**
  Of the 145 `polylog`-expected FAIL entries only **11 are `unverified`**
  (131 `contains-noun`, 2 timeout, 1 deferred); a `polylog(2,·)` derivative
  shim closes an `unverified` zero chain and cannot close an answer that
  carries a noun. The shim is already ticketed
  (`.scratch/class3-polylog-ceiling/issues/01`, needs-triage); class 8
  adds at most 11 to its go number (an upper bound: the record does not
  say whether those answers themselves carry `polylog`).
- **Hurwitz `Zeta(s, z)` — the inert noun works as designed.** 7 entries
  expect it: `expected` 4 (form-identical answers cancel in the zero
  chain), `no-answer` 1, `contains-noun` 2. A different-form answer
  cannot verify (its derivative stays a noun, probe 04 A17).
- **Free functions and the chain rule (8.10).** Maxima applies no chain
  rule to an undeclared function of a composite argument (probe 04 N13),
  so the 11 8.10 entries whose answer is `F(<composite>)` verify only when
  form-identical. `Derivative(`-expected entries: `verified` 26, `expected`
  7, `no-answer` 2, `contains-noun` 19 (the product rule and the interior
  markers above).
- **`psi[-k]`** does not float-evaluate (probe 04 E8): such answers verify
  on the symbolic stages only. 9 of the 30 `Psi(` entries FAIL
  (`contains-noun` 8, `unverified` 1).
- **AppellF1** does not occur in section 8.

## 7. Earlier-class status

Byte-identity green for every class, 1–9 plus the rewrite tables:
regenerating each leaves `git status --porcelain rules/` empty (re-run
2026-09-26 at `e70ee89`). The class-8 port's own no-regression evidence
was the Step-7 slice A/B (`probes/corpus/17-class8-slice-ab.out`, 53
entries of classes 1/2/3/6: 0 PASS→FAIL, 2 FAIL→PASS — 2.2 e1/e2, class
8's 8.8 rules finishing class-2 sub-integrals).

The full re-measure of the earlier classes on the SAME core (`89bec424`,
same runner, `test/class_ports_final.log`) against master's promoted
records (`test/final_ab_master_class{1,2,3,6}.out`):

| class | master | final | PASS→FAIL | FAIL→PASS |
|---|---:|---:|---:|---:|
| 1 Algebraic | 18,400 | 23,203 | 85 | 4,888 |
| 2 Exponentials | 758 | 863 | 3 | 108 |
| 3 Logarithms | 1,692 | 2,446 | 5 | 759 |
| 6 Hyperbolic | 2,474 | 4,314 | 46 | 1,886 |

All eight classes: 61,266 of 70,385 entries PASS (87.0 %) on this core.
These moves are the four ports and the class-ports fixes together; they
are not attributed to class 8 alone.

## 8. Final gates

The code is unchanged from `39eba80` (the last fix) to `c2deb32` (the
measured core): `git diff 39eba80 c2deb32` touches records, logs, a
ticket and a spec only.

| gate | result | where |
|---|---|---|
| Layer A | `Results: 1583 passed, 0 failed` | `39eba80` commit message |
| rule-table order | 18/0 | same |
| section-9 e2e | 9/0 | same |
| dispatch / mr-match / mr-tree | 119/0, 57/0, 84/0 | same |
| generator section-9 unit | 28/0 | same |
| run-records guard | 43/0 | same |
| harness guards | all 0 failed | same |
| matcher regression suite (P1/P2) | 109/0 in both arms | `e70c00e` |
| P3 static | `Results: 29 passed, 0 failed` | re-run 2026-09-26 at `e70ee89` |
| head rewrites | `Results: 64 passed, 0 failed` | re-run 2026-09-26 at `e70ee89` |
| byte-identity, classes 1–9 + rewrites | `git status --porcelain rules/` EMPTY | re-run 2026-09-26 at `e70ee89` |

## 9. Follow-ups

- `.scratch/class-ports/issues/07` / `09` — bare-`u_` placement; blocks the
  8.10 product-rule entries (§5).
- `.scratch/corpus-harness/issues/05` (new) — expectations that are
  Rubi's own partial answers cannot PASS: 141 class-8 entries (§5).
- `.scratch/class3-polylog-ceiling/issues/01` — the polylog shim; class 8
  adds ≤ 11 `unverified` (§6).
- Not ticketed, the first items for a class-8 uplift: the 8.8 order-lowering
  chain (131 fast `contains-noun`), the `Ei(-n,·)`/`GAMMA(-n,·)`
  non-terminators (17 at 100 s), a chain-rule normaliser in the zero
  chain (11 8.10 entries; it would change verification for every class).
