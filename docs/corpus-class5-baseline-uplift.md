# Class-5 corpus — rubi() acceptance record (inverse trig functions, Step 10 written 2026-09-26)

The measured acceptance of the "5 Inverse trig functions" port: the full
4,585-entry section under the ported rule set (`rubi()`, rules-only
default, 7,776 rules — the four ports of branch `class-ports` together),
against a native-`integrate` baseline on the same class scheme. Ported
against `docs/class-porting.md` Steps 1–10, second in the queue
8 → 5 → 7 → 4; the ticket, which carries the Step 1–7 records, is
`.scratch/class-ports/issues/02-class5-inverse-trig-functions.md`.

Build for every figure below: **`branch_5_50_base_84_g4204fb669`**
(2026-08-31 13:27:47) on SBCL 2.6.7, stamped in every record header.
Per-entry cap **30 s CPU** (package), **30 s wall** (baseline, §3).

Inputs (all committed on `class-ports`):

- `test/corpus_class5.final.out` — the package record: 4,585/4,585,
  `test/run_corpus_queue.py`, 24 workers, merged 2026-09-25 20:26 UTC;
  rules core **`89bec424959947761abb9416d993bee6`** (7,776 rules, built
  at `c2deb32`; `test/class_ports_final.log`). Harness failures 0.
- `test/corpus_class5.baseline.out` — the native-`integrate` baseline:
  18 per-file shards, a 12-process pool (`test/run_baseline_pool.py`),
  merged 2026-09-25 11:42 UTC.
- `test/corpus_class5.ports.out` — the pre-fix package record (core
  `4daae7ac`, `4ed1877`), the same runner; the §4.3 A/B.
- `test/corpus_class5.final.timeout-rerun/` — the 100 s re-check of the
  record's 195 `timeout` entries.
- `test/final_ab_baseline_class5.out`, `test/final_ab_prefix_class5.out`.
- `probes/corpus/28-class-ports-acceptance.{py,run,out}` — the
  histograms, per-file tables, residue → expected-head census, the
  Rubi-marker split and the sample entries below. Static, no Maxima.

## 1. Rule set

**15 loaded rule files / 667 rules** (5.1.1 6, 5.1.2 14, 5.1.3 30,
5.1.4 60, 5.1.5 62, 5.1.6 43, 5.3.1 10, 5.3.2 24, 5.3.3 22, 5.3.4 161,
5.3.5 20, 5.3.6 76, 5.3.7 79, 5.5.1 36, 5.5.2 24), every rule with a `/;`
condition. The census counts 665
(`probes/translation/10-class5-syntax-census.out`); 5.3.7 carries two
single-line `If[TrueQ[$LoadShowSteps], …]` wrappers (L30/L31) that the
census glues onto the rule before them and the generator unwraps, so the
port total is 667. AUTO 361 / MANUAL 304 by the census's tiers. **No file
is excluded** — the tree has 15 `.m` files and `Rubi.m` loads all 15
(probe 28's listing). Rubi has no separate arccos/arccot/arccsc files:
each file carries both members of its pair, which is why 18 corpus files
face 15 rule files. No head variables, no bare-`u_` record.

Table after the port: **4,992** (4,325 + 667), fingerprint `8e57b290…` at
Step 6. In the final table class 5's bodies sit right after class 4's
last list and before class 6's first (Rubi.m's section order;
`test/test_rule_table_order.mac` 18/0 at the final code).

The porting surface (ticket 02, Steps 2–4): `ArcSec`/`ArcCsc` → the
native `asec`/`acsc` (conventions equal Mathematica's, probe
`probes/answer-side/05-class5-answer-side-identities.out` C1–C7),
`Discriminant` → `poly_discriminant`, `ExpandExpression` (ported since
class 1), and four Step-4 ports: `HalfIntegerQ`, `Head`,
`InverseFunctionOfLinear`, `SubstForInverseFunction`. The transitive
closure through `IntegrationUtilityFunctions.m` found no other class-5
gap (59 ABSENT names, each accounted for on the ticket).

## 2. Normalization

**No new `HEAD_REWRITES` row.** Every non-native answer head is already
disposed of (`probes/corpus/18-class5-answer-heads.out`): `Unintegrable(`
1,168 / `CannotIntegrate(` 35 are corpus markers; `FresnelC/S(` class-8
rows; `Ci(`/`Si(` class-3 rows; `GAMMA(` (all 2-arg) the class-2 reading
of the arity-dispatched row; `HypergeometricPFQ(` the class-8 row;
`AppellF1(` 22 has no native (§6). The six inverse-trig natives
differentiate through the zero chain and float-evaluate (probe 05
A1–A6, E1–E6). `test/test_head_rewrites.py` 47 → 52 (five class-5
excerpts); no-op over every entry
(`probes/corpus/19-class5-head-rewrite-noop.out`); slice A/B
(`probes/corpus/20-class5-slice-ab.out`, 63 entries of classes
1/2/3/6/8): 0 transitions.

Simplifier fact the matcher sees (probe 05 S1–S8): a syntactically
negated argument is rewritten — `acos(-x) = %pi - acos(x)`,
`asec(-x) = %pi - asec(x)`, the other four odd — so the rules see the
same shape with shifted captures.

## 3. Baseline (native `integrate`)

`probes/corpus/probe-integrate-sample.py` through `test/run_baseline_pool.py`
(18 per-file shards, 12 processes, **30 s wall** cap — the class-6
record's probe; the package cap is cpu, AGENTS.md measures the shift
near the cap at 0.84–1.00).

| class | count | % |
|---|---:|---:|
| `unverified` | 1260 | 27.5 |
| `verified` | 954 | 20.8 |
| `deferred` | 720 | 15.7 |
| `error` | 587 | 12.8 |
| `timeout` | 582 | 12.7 |
| `no-answer` | 251 | 5.5 |
| `unexpected` | 202 | 4.4 |
| `expected` | 29 | 0.6 |
| **total** | **4585** | **Results: 1234 passed, 3351 failed** |

## 4. Package run

### 4.1 Verdicts

Queue runner, 24 workers, 30 s cpu cap, merged 14 min after launch
(`test/class_ports_final.log`), harness failures 0, merge clean
4585/4585 (`test/final_merge_class5.out`).

| class | count | % | verdict |
|---|---:|---:|---|
| `verified` | 2072 | 45.2 | PASS |
| `expected` | 817 | 17.8 | PASS |
| `no-answer` | 740 | 16.1 | PASS |
| `contains-noun` | 665 | 14.5 | FAIL |
| `timeout` | 195 | 4.3 | FAIL |
| `unverified` | 66 | 1.4 | FAIL |
| `deferred` | 26 | 0.6 | FAIL |
| `unexpected` | 3 | 0.1 | FAIL |
| `error` | 1 | 0.0 | FAIL |
| **total** | **4585** | | **Results: 3629 passed, 956 failed** |

**3,629 / 4,585 (79.1 %) against the baseline's 1,234 (26.9 %): net
+2,395 (+52.2 pts).**

### 4.2 A/B against the baseline (`test/final_ab_baseline_class5.out`)

| | |
|---:|---:|
| PASS→PASS | 1117 |
| PASS→FAIL | 117 |
| FAIL→PASS | 2512 |
| FAIL→FAIL | 839 |

Key sets equal. Gains led by `unverified -> verified` 611,
`unverified -> expected` 347, `deferred -> verified` 327,
`error -> no-answer` 243, `deferred -> expected` 241,
`timeout -> verified` 238. The 117 PASS→FAIL by class:
`verified -> contains-noun` 72, `no-answer -> contains-noun` 18,
`verified -> timeout` 14, `verified -> deferred` 5,
`verified -> unverified` 4, `expected -> timeout` 2,
`no-answer -> timeout` 1, `expected -> contains-noun` 1.

### 4.3 The class-ports fixes (pre-fix → final, `test/final_ab_prefix_class5.out`)

The fixes between the first run (core `4daae7ac`, `4ed1877`) and this
record — symbolic EqQ/NeQ (`d0f0237`), native inverse-hyperbolic heads in
every class (`025c589`, ticket 18), two-argument `Expand` (`e799ea6`,
ticket 19), the ExpandIntegrand reciprocal-atom guard (`3bb8c4f`), the
`values` trim (`1ebef70`, fix V), depth cap 32 (`2ee8fc4`), plain `Subst`
(`e67e2eb`), Rubi's GtQ (`39eba80`); the master merge brought no code
(class-8 record §4.3 has the commit list with its tickets):

| | |
|---:|---:|
| PASS→PASS | 2900 |
| PASS→FAIL | 15 |
| FAIL→PASS | 729 |
| FAIL→FAIL | 941 |

2,915 → 3,629 (+714). The largest moves: `contains-noun -> expected` 164,
`contains-noun -> verified` 129, `timeout -> expected` 128,
`timeout -> verified` 113, `unverified -> expected` 93. Timeouts 504 →
195; the record's cpu sum 43,937 s → 15,876 s, median entry 5.2 s → 1.2 s
(probe 28; sums truncated at the cap). The 5.3.7 r27/r28 ShowSteps pair,
which the ticket found limited by EqQ's syntactic zero test (finding 1),
is one site the EqQ fix reaches: 5.3.7 PASS 93 → 110. The per-fix split
is not measured here.

### 4.4 Timeout re-check (100 s)

All 195 `timeout` entries at a 100 s cap, 12 workers
(`test/corpus_class5.final.timeout-rerun/merge.out`, 195/195):

| at 100 s | n |
|---|---:|
| `timeout` | 74 |
| `error` | 40 |
| `verified` (now PASS) | 31 |
| `contains-noun` | 28 |
| `expected` (now PASS) | 21 |
| `unverified` | 1 |

**52 slow-correct entries (1.1 % of the section)**; at 100 s the section
would read 3,681. The 74 still timing out concentrate in 5.3.6 (18),
5.4.1 (17), 5.3.7 (14) and 5.1.5 (8). The re-check does not record why
the 40 `error`s died (likely heap exhaustion at the longer cap, the
`.scratch/class-ports/issues/11` mechanism — unmeasured).

## 5. Residues

FAIL mass **956 = `contains-noun` 665 (70 %) + `timeout` 195 (20 %) +
`unverified` 66 + `deferred` 26 + `unexpected` 3 + `error` 1**. Coverage
is not the limit (`deferred` 26).

**Half of the `contains-noun` mass is Rubi's own noun.** 789 entries
expect a top-level `Unintegrable`/`CannotIntegrate` (740 PASS as
`no-answer`, 45 `contains-noun`), and **286 expect a partial answer
carrying one inside**, of which 283 are `contains-noun` — the driver
classifies any noun-carrying answer `contains-noun` before comparing, so
Rubi's own partial answer cannot PASS (`.scratch/corpus-harness/issues/05`).
**328 of the 665 `contains-noun` (49 %)** are entries where Rubi returns
no noun-free answer; 216 of them are in 5.3.4 alone.

| corpus file | N | PASS base | PASS final | FAIL | FAIL by class |
|---|---:|---:|---:|---:|---|
| 5.3.4 u (a+b arctan(c x))^p | 1301 | 490 | 1006 | **295** | contains-noun 265, timeout 14, deferred 9, unverified 7 |
| 5.1.4a (f x)^m (d-c^2 d x^2)^p (a+b arcsin(c x))^n | 595 | 92 | 453 | 142 | contains-noun 128, unverified 4, timeout 4, deferred 3, unexpected 3 |
| 5.1.5 Inverse sine functions | 474 | 68 | 370 | 104 | contains-noun 73, timeout 19, deferred 6, unverified 5, error 1 |
| 5.4.1 Inverse cotangent functions | 234 | 90 | 172 | 62 | timeout 39, contains-noun 15, unverified 6, deferred 2 |
| 5.5.1 u (a+b arcsec(c x))^n | 174 | 45 | 121 | 53 | contains-noun 33, timeout 14, unverified 6 |
| 5.6.1 u (a+b arccsc(c x))^n | 178 | 45 | 125 | 53 | contains-noun 27, timeout 20, unverified 6 |
| 5.3.6 Exponentials of inverse tangent | 385 | 15 | 337 | 48 | timeout 35, contains-noun 9, unverified 4 |
| 5.3.7 Inverse tangent functions | 153 | 28 | 110 | 43 | timeout 34, contains-noun 5, unverified 4 |
| 5.1.4b (f x)^m (d+e x^2)^p (a+b arcsin(c x))^n | 108 | 37 | 72 | 36 | contains-noun 32, timeout 2, unverified 2 |
| 5.3.5 u (a+b arctan(c+d x))^p | 70 | 43 | 51 | 19 | contains-noun 10, timeout 6, unverified 2, deferred 1 |
| 5.2.5, 5.5.2, 5.6.2, 5.1.2, 5.2.2, 5.3.2, 5.3.3 | 901 | 281 | 800 | 101 | contains-noun 68 … |
| 5.4.2 Exponentials of inverse cotangent | 12 | 0 | 12 | 0 | — |

Readings (sample entries from probe 28, with the record's cpu time):

- **5.3.4: mostly the harness ceiling.** 216 of its 265 `contains-noun`
  expect an interior marker (`atan(a*x)^(5/2)/(x^4*(c+a^2*c*x^2))` e863:
  `2/7*a^3*atan(a*x)^(7/2)/c + Unintegrable(…)`). The rest are genuine
  noun answers (`x*(a+b*atan(c*x))/(d+%i*c*d*x)^3` e61, 9.3 s) and a few
  `deferred` on complex-linear denominators
  (`(a+b*atan(c*x))^2/(d+%i*c*d*x)^2` e107) — likely the `%i`-coefficient
  shapes, unmeasured.
- **5.1.4a / 5.1.4b: the `(d - c^2 d x^2)^p` products.** 38 interior-marker
  entries; the rest answer with a noun
  (`(d-c^2*d*x^2)^2*(a+b*asin(c*x))/x^2` e16, 7.5 s) or time out on the
  symbolic-`m` expansions (`x^m*(d-c^2*d*x^2)^2*(a+b*asin(c*x))` e144).
  The 3 `unexpected` (e276/e277 among them) answer where the corpus
  expects `Unintegrable` — the package reduces further than Rubi.
- **5.1.5 / 5.5.1 / 5.6.1: the sub-integral families.**
  `(d+e*x)^2/(a+b*asin(c*x))^2` e22 expects `Ci`/`Si` terms and answers a
  noun; `(a+b*asec(c*x))^2/x^2` e20, `(a+b*acsc(c*x))^2/x^2` e20 likewise.
  Rubi routes these through `x tan(x)` / `x cot(x)`-type sub-integrals;
  class 4 is now ported, so the remaining nouns are likely specific
  sub-integrals rather than the whole trig section (unmeasured).
- **5.3.6 / 5.4.1 / 5.3.7: cost.** 108 of the 195 timeouts; 49 of them
  still time out at 100 s (5.3.6 18, 5.4.1 17, 5.3.7 14):
  `%e^(1/2*%i*atan(a*x))*x^2` e61, `acot(a*x)/(c+d*x^2)` e57,
  `x^2*atan(c+d*tan(a+b*x))` e48. The dispatch cost ticket
  (`.scratch/class-ports/issues/21`) is the standing route.
- **`unverified` 66:** `(a+b*asec(c*x))/x` e8, `acot(a*x)^2/x` e18,
  `asin(a+b*x)^2/x` e135 — answers whose expected form carries
  `polylog`/`log(1-%e^(%i·))` terms (below). Likely the missing
  `SimplifyAntiderivative` (ticket 02 finding 2: a discontinuous `atan` is
  not rectified) or the polylog ceiling; unmeasured per entry.

**Residue → expected-head census** (probe 28):

| head | entries | in FAIL | FAIL % | FAIL classes |
|---|---:|---:|---:|---|
| `polylog(` | 1112 | 424 | 38.1 | contains-noun 258, timeout 107, unverified 44, deferred 14, error 1 |
| `Unintegrable(` | 1040 | 322 | 31.0 | contains-noun 318, unexpected 3, timeout 1 |
| `hypergeometric(` | 187 | 58 | 31.0 | contains-noun 32, unverified 13, timeout 12, deferred 1 |
| `Ci(` / `Si(` | 204 / 200 | 42 / 42 | 20.6 / 21.0 | contains-noun |
| `CannotIntegrate(` | 35 | 13 | 37.1 | contains-noun 10, deferred 3 |
| `FresnelC(` / `FresnelS(` | 240 / 231 | 12 / 9 | 5.0 / 3.9 | contains-noun |
| `elliptic_f(` / `elliptic_e(` / `elliptic_pi(` | 87 / 65 / 23 | 9 / 9 / 7 | 10.3 / 13.8 / 30.4 | timeout |
| `AppellF1(` | 22 | 5 | 22.7 | unverified 5 |
| `HypergeometricPFQ(` | 35 | 2 | 5.7 | contains-noun 2 |
| `GAMMA(` | 23 | 0 | 0.0 | — |

## 6. Structural ceilings (per spec §3.4, per class)

- **polylog: the ceiling stands for class 5.** 1,112 entries expect
  `polylog`; 688 PASS `expected` (form-identical answers close the chain
  without a derivative), 424 FAIL, of which **44 `unverified`** — the only
  class a derivative shim could move. It is an upper bound (the record
  does not say whether the package answer itself carries `polylog`), and
  the shim is already ticketed (`.scratch/class3-polylog-ceiling/issues/01`,
  go number 638 from class 3). No new ticket; the 44 add to its go.
- **AppellF1: 22 entries — `expected` 17, `unverified` 5.** The 5 are the
  ceiling (`appell_f1` has no derivative): e.g. 5.3.4 e1241
  `x^(-3-2*p)*(d+e*x^2)^p*(a+b*atan(c*x))`.

## 7. Earlier-class status

Byte-identity green for every class, 1–9 plus the rewrite tables (re-run
2026-09-26 at `e70ee89`). The port's own slice A/B
(`probes/corpus/20-class5-slice-ab.out`, 63 entries of classes
1/2/3/6/8): 0 transitions. The full re-measure of the earlier classes on
the same core against master's promoted records
(`test/final_ab_master_class{1,2,3,6}.out`): class 1 18,400 → 23,203
(PASS→FAIL 85), class 2 758 → 863 (3), class 3 1,692 → 2,446 (5), class 6
2,474 → 4,314 (46) — the four ports and the fixes together, not
attributed to class 5 alone.

## 8. Final gates

As the class-8 record §8 (the same code and core): Layer A
`Results: 1583 passed, 0 failed`, rule-table order 18/0, section-9 e2e
9/0, dispatch 119/0, mr-match 57/0, mr-tree 84/0, run-records 43/0,
harness guards 0 failed (`39eba80`; the code is unchanged to `c2deb32`);
matcher regression suite 109/0 in both arms (`e70c00e`); P3 static 29/0,
head rewrites 64/0 and byte-identity EMPTY for classes 1–9 + rewrites,
re-run 2026-09-26 at `e70ee89`.

## 9. Follow-ups

- `.scratch/corpus-harness/issues/05` (new) — Rubi's partial answers
  cannot PASS: 286 class-5 entries, 216 of them in 5.3.4.
- `.scratch/class-ports/issues/21` — the dispatch index; the timeout mass
  (195, 74 still at 100 s) is its class-5 weight.
- `.scratch/class3-polylog-ceiling/issues/01` — class 5 adds ≤ 44
  `unverified`.
- Not ticketed: `SimplifyAntiderivative` (`RectifyTangent`/`Cotangent`),
  ticket 02 finding 2 — visible only as `verified` vs `expected` and in
  some `unverified`; the 40 `error`s at the 100 s re-check (cause not
  recorded).
