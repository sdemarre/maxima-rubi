# Class-7 corpus — rubi() acceptance record (inverse hyperbolic functions, Step 10 written 2026-09-26)

The measured acceptance of the "7 Inverse hyperbolic functions" port: the
full 6,552-entry section under the ported rule set (`rubi()`, rules-only
default, 7,776 rules — the four ports of branch `class-ports` together),
against a native-`integrate` baseline on the same class scheme. Ported
against `docs/class-porting.md` Steps 1–10, third in the queue
8 → 5 → 7 → 4; the ticket, which carries the Step 1–7 records, is
`.scratch/class-ports/issues/04-class7-inverse-hyperbolic-functions.md`.

Build for every figure below: **`branch_5_50_base_84_g4204fb669`**
(2026-08-31 13:27:47) on SBCL 2.6.7, stamped in every record header.
Per-entry cap **30 s CPU** (package), **30 s wall** (baseline, §3).

Inputs (all committed on `class-ports`):

- `test/corpus_class7.final.out` — the package record: 6,552/6,552,
  `test/run_corpus_queue.py`, 24 workers, merged 2026-09-25 20:54 UTC;
  rules core **`89bec424959947761abb9416d993bee6`** (7,776 rules, built
  at `c2deb32`; `test/class_ports_final.log`). Harness failures 0.
- `test/corpus_class7.baseline.out` — the native-`integrate` baseline:
  20 per-file shards, a 12-process pool (`test/run_baseline_pool.py`),
  merged 2026-09-25 13:09 UTC.
- `test/corpus_class7.ports.out` — the pre-fix package record (core
  `4daae7ac`, `4ed1877`), the same runner; the §4.3 A/B.
- `test/corpus_class7.final.timeout-rerun/` — the 100 s re-check of the
  record's 211 `timeout` entries.
- `test/final_ab_baseline_class7.out`, `test/final_ab_prefix_class7.out`.
- `probes/corpus/28-class-ports-acceptance.{py,run,out}` — the
  histograms, per-file tables, residue → expected-head census, the
  Rubi-marker split, the sample entries and the unloaded-file listing
  below. Static, no Maxima.

## 1. Rule set

**21 loaded rule files / 712 rules** (7.1.1 3, 7.1.2 7, 7.1.3 15,
7.1.4 30, 7.1.5 31, 7.1.6 21, 7.2.1 3, 7.2.2 7, 7.2.3 23, 7.2.4 50,
7.2.5 33, 7.2.6 26, 7.3.1 10, 7.3.2 24, 7.3.3 22, 7.3.4 161, 7.3.5 20,
7.3.6 82, 7.3.7 72, 7.5.1 36, 7.5.2 36), every rule with a `/;`
condition. The census counts 710
(`probes/translation/11-class7-syntax-census.out`); 7.3.7's two
single-line `If[TrueQ[$LoadShowSteps], …]` wrappers (L28/L29, the
ArcTanh/ArcCoth twins of class 5's 5.3.7 r27/r28) are unwrapped by the
generator, so the port total is 712. AUTO 386 / MANUAL 324 by the
census's tiers. No head variables, no bare-`u_` record. Rubi has no
separate arccoth/arccsch rule files (each file carries both members of
its pair), which is why 20 corpus files face 21 rule files, 7.4 and 7.6
having corpus files only.

**Four files excluded** — in the tree, absent from `Rubi.m`'s LoadRules
(probe 28's listing, `probes/translation/11-class7-excluded-files.py`),
all in `7.3 Inverse hyperbolic tangent/` and all the section's OLD
numbering:

| excluded file | `Int[` | what it is |
|---|---:|---|
| `7.3.1 u (a+b arctanh(c x^n))^p.m` | 193 | the old omnibus: 179 of its rule runs occur verbatim in loaded 7.3.2 (6), 7.3.3 (12), 7.3.4 (161); 14 in no loaded file |
| `7.3.2 u (a+b arctanh(c+d x))^p.m` | 20 | loaded 7.3.5, identical but for the header comment |
| `7.3.3 Exponentials of inverse hyperbolic tangent.m` | 82 | loaded 7.3.6, same |
| `7.3.4 Miscellaneous inverse hyperbolic tangent.m` | 70 | loaded 7.3.7, same |

Rubi excludes them, so the port does (the class-1/3 precedent); loading
them would register duplicates of rules already in the table.

Table after the port: **5,704** (4,992 + 712), fingerprint `dd5ebc48…`
at Step 6; class 7's bodies sit between class 6's last list and class
8's first (Rubi.m L318–341; `test/test_rule_table_order.mac` 18/0 at the
final code).

The one table decision (ticket 04, Step 1 B): the class-1 rows rename
`ArcTanh`/`ArcSinh`/`ArcCosh` to the `%mr_atanh`/`%mr_asinh`/`%mr_acosh`
log-form shims, which erase the head class 7's recursive rules match on.
The port first emitted the natives for class 7 only (`CLASS_RENAME`,
`cd238ae`); ticket 18 then made the natives the rule for **every** class
(`025c589`, option 1), so the final core has no shim in any generated
rule. Plus the `ArcSech` → `asech`, `ArcCsch` → `acsch` rows (bound,
differentiable, Mathematica's conventions — probe
`probes/answer-side/06-class7-answer-side-identities.out` A5/A6, C1–C8).
Nothing to port at Step 4 (class 5 had ported the utilities its 7.3.7
ShowSteps pair reuses).

## 2. Normalization

**No new `HEAD_REWRITES` row** (`probes/corpus/21-class7-answer-heads.out`):
`Unintegrable(` 618 / `CannotIntegrate(` 34 are markers; `Chi/Shi/Ci/Si(`
class-3 rows; `GAMMA(` (all 2-arg) the class-2 reading;
`HypergeometricPFQ(`, `FresnelS/C(` class-8 rows; `AppellF1(` 47 has no
native (§6). The six inverse-hyperbolic natives differentiate through
the zero chain and float-evaluate (probe 06 A1–A6, E1–E6); `asech`,
`acsch`, `acoth` are bound. `test/test_head_rewrites.py` 52 → 57; no-op
over every entry (`probes/corpus/22-class7-head-rewrite-noop.out`);
slice A/B (`probes/corpus/23-class7-slice-ab.out`, 81 entries of classes
1/2/3/5/6/8): 0 transitions.

Simplifier facts (probe 06): the odd heads absorb a negated argument
(`asinh(-x) = -asinh(x)`, …); `atanh(1)` and `acoth(1)` are Maxima
errors where Mathematica answers ComplexInfinity (N1/N2).

## 3. Baseline (native `integrate`)

`probes/corpus/probe-integrate-sample.py` through `test/run_baseline_pool.py`
(20 per-file shards, 12 processes, **30 s wall** cap — the class-6
record's probe; AGENTS.md measures the wall/cpu shift near the cap at
0.84–1.00).

| class | count | % |
|---|---:|---:|
| `deferred` | 2320 | 35.4 |
| `unverified` | 2078 | 31.7 |
| `timeout` | 904 | 13.8 |
| `verified` | 730 | 11.1 |
| `unexpected` | 272 | 4.2 |
| `no-answer` | 164 | 2.5 |
| `expected` | 59 | 0.9 |
| `error` | 25 | 0.4 |
| **total** | **6552** | **Results: 953 passed, 5599 failed** |

## 4. Package run

### 4.1 Verdicts

Queue runner, 24 workers, 30 s cpu cap, merged 16 min after launch
(`test/class_ports_final.log`), harness failures 0, merge clean
6552/6552 (`test/final_merge_class7.out`).

| class | count | % | verdict |
|---|---:|---:|---|
| `verified` | 4038 | 61.6 | PASS |
| `expected` | 919 | 14.0 | PASS |
| `no-answer` | 385 | 5.9 | PASS |
| `contains-noun` | 604 | 9.2 | FAIL |
| `unverified` | 324 | 4.9 | FAIL |
| `timeout` | 211 | 3.2 | FAIL |
| `deferred` | 69 | 1.1 | FAIL |
| `error` | 2 | 0.0 | FAIL |
| **total** | **6552** | | **Results: 5342 passed, 1210 failed** |

**5,342 / 6,552 (81.5 %) against the baseline's 953 (14.5 %): net
+4,389 (+67.0 pts).**

### 4.2 A/B against the baseline (`test/final_ab_baseline_class7.out`)

| | |
|---:|---:|
| PASS→PASS | 905 |
| PASS→FAIL | 48 |
| FAIL→PASS | 4437 |
| FAIL→FAIL | 1162 |

Key sets equal. Gains led by `deferred -> verified` 1,649,
`unverified -> verified` 1,181, `unverified -> expected` 542,
`timeout -> verified` 514, `unexpected -> no-answer` 230,
`deferred -> expected` 212. The 48 PASS→FAIL by class:
`verified -> contains-noun` 21, `no-answer -> contains-noun` 9,
`verified -> unverified` 7, `verified -> timeout` 7,
`expected -> timeout` 2, `expected -> error` 1,
`expected -> contains-noun` 1.

### 4.3 The class-ports fixes (pre-fix → final, `test/final_ab_prefix_class7.out`)

The fixes between the first run (core `4daae7ac`, `4ed1877`) and this
record: symbolic EqQ/NeQ (`d0f0237`), native inverse-hyperbolic heads in
every class (`025c589`, ticket 18), two-argument `Expand` (`e799ea6`),
the ExpandIntegrand reciprocal-atom guard (`3bb8c4f`), the `values` trim
(`1ebef70`, fix V), depth cap 32 (`2ee8fc4`), plain `Subst` (`e67e2eb`),
Rubi's GtQ (`39eba80`); the master merge brought no code (class-8 record
§4.3 has the list with its tickets).

| | |
|---:|---:|
| PASS→PASS | 4299 |
| PASS→FAIL | 19 |
| FAIL→PASS | 1043 |
| FAIL→FAIL | 1191 |

4,318 → 5,342 (+1,024). Led by `timeout -> verified` 271,
`contains-noun -> verified` 225, `deferred -> verified` 202,
`timeout -> expected` 168. Timeouts 763 → 211; `deferred` 380 → 69; the
record's cpu sum 63,152 s → 20,645 s, median entry 5.6 s → 1.3 s (probe
28; sums truncated at the cap). The per-fix split is not measured here.

### 4.3a PASS->FAIL attribution (pre-fix -> final)

Evidence: `probes/class-ports/final/attribution.{py,out}` (`3deddb7`). Each fix was reverted
alone on the final core (switch arms and overlays), a commit bisect ran over cores built at every
class-ports-fixes commit, and timings are alternating sequential runs. Build
`branch_5_50_base_84_g4204fb669`, 2026-09-26.

19, all caused by fixes landed after the pre-fix run:
- **fix A** (`3bb8c4f`), 11 entries: 4 past the cap, 1 that passes singly near the cap, 3 refolded by 1_2_3_1 r11 and cut by the seen test (ticket 22), 3 ending in a partial answer or an unverified form.
- **two-valued GtQ**, 4 entries: 3 ending in a noun or a timeout, 1 with a numerically correct answer different from Rubi's.
- **symbolic EqQ**, 2 entries: Rubi's reading of an identically-zero condition opens a route that times out or ends in a noun.
- **fix A and symbolic EqQ together**, 1 entry.
- **plain Subst**, 1 entry, past the cap.

### 4.4 Timeout re-check (100 s)

All 211 `timeout` entries at a 100 s cap, 12 workers
(`test/corpus_class7.final.timeout-rerun/merge.out`, 211/211):

| at 100 s | n |
|---|---:|
| `timeout` | 78 |
| `contains-noun` | 41 |
| `verified` (now PASS) | 39 |
| `error` | 37 |
| `expected` (now PASS) | 9 |
| `unverified` | 7 |

**48 slow-correct entries (0.7 % of the section)**; at 100 s the section
would read 5,390. The 78 still timing out: 7.3.6 15, 7.4.2 13, 7.4.1 12,
7.3.7 8, 7.5.1 7, 7.3.4 5, 7.5.2 5, 7.6.2 4, and 9 more in six files. The
re-check does not record why the 37 `error`s died (likely heap
exhaustion at the longer cap — unmeasured).

## 5. Residues

FAIL mass **1,210 = `contains-noun` 604 (50 %) + `unverified` 324 (27 %)
+ `timeout` 211 (17 %) + `deferred` 69 + `error` 2**.

**Rubi's own nouns.** 438 entries expect a top-level
`Unintegrable`/`CannotIntegrate` (385 PASS `no-answer`, 53
`contains-noun`); **202 expect a partial answer carrying one inside** —
140 `contains-noun`, **61 `deferred`**, 1 timeout. The driver cannot PASS
an answer identical to Rubi's partial answer (a noun-carrying answer is
`contains-noun` before any comparison, and a top-level noun against a
non-marker expectation is `deferred`):
`.scratch/corpus-harness/issues/05`. 193 of the 604 `contains-noun`
(32 %) are entries where Rubi returns no noun-free answer.

| corpus file | N | PASS base | PASS final | FAIL | FAIL by class |
|---|---:|---:|---:|---:|---|
| 7.3.6 Exponentials of inverse hyperbolic tangent | 1378 | 25 | 1160 | **218** | unverified 142, timeout 47, contains-noun 28, error 1 |
| 7.2.4a (f x)^m (d-c^2 d x^2)^p (a+b arccosh(c x))^n | 453 | 29 | 298 | 155 | contains-noun 91, deferred 57, timeout 5, unverified 2 |
| 7.4.2 Exponentials of inverse hyperbolic cotangent | 935 | 12 | 794 | 141 | contains-noun 62, unverified 51, timeout 27, deferred 1 |
| 7.1.4a (f x)^m (d+c^2 d x^2)^p (a+b arcsinh(c x))^n | 541 | 125 | 424 | 117 | contains-noun 114, timeout 3 |
| 7.5.1 u (a+b arcsech(c x))^n | 190 | 45 | 113 | 77 | contains-noun 40, timeout 23, unverified 14 |
| 7.4.1 Inverse hyperbolic cotangent functions | 300 | 96 | 230 | 70 | unverified 29, timeout 25, contains-noun 15, deferred 1 |
| 7.1.5 Inverse hyperbolic sine functions | 371 | 46 | 305 | 66 | contains-noun 52, timeout 7, unverified 5, error 1, deferred 1 |
| 7.2.5 Inverse hyperbolic cosine functions | 293 | 33 | 229 | 64 | contains-noun 51, timeout 6, unverified 5, deferred 2 |
| 7.6.1 u (a+b arccsch(c x))^n | 178 | 46 | 119 | 59 | contains-noun 29, timeout 20, unverified 10 |
| 7.3.4 u (a+b arctanh(c x))^p | 538 | 191 | 494 | 44 | contains-noun 29, timeout 6, deferred 6, unverified 3 |
| 7.3.7 Inverse hyperbolic tangent functions | 361 | 26 | 317 | 44 | timeout 20, unverified 17, contains-noun 7 |
| 7.2.4b (f x)^m (d+e x^2)^p (a+b arccosh(c x))^n | 109 | 30 | 76 | 33 | contains-noun 28, timeout 4, unverified 1 |
| 7.3.2, 7.3.3, 7.3.5, 7.5.2, 7.6.2, 7.1.2, 7.2.2, 7.1.4b | 905 | 249 | 783 | 122 | contains-noun 58, unverified 45, timeout 18, deferred 1 |

Readings (sample entries from probe 28, with the record's cpu time):

- **7.3.6 / 7.4.2 — the exponential families, an `unverified` block
  (193 of the class's 324).** `%e^(3*atanh(a*x))/x` e22 (3.5 s) expects
  `-asin(a*x)-atanh(sqrt(1-a^2*x^2))+4*sqrt(…)…`;
  `%e^(3*acoth(a*x))/x` e21 expects `acsc(a*x)+atanh(sqrt(1+(-1)/(a^2*x^2)))…`;
  `%e^(n*acoth(a*x))*(c-a*c*x)^(3/2)` e373. The package answers in seconds
  and neither zero test closes. Likely cause (unmeasured): the answers are
  correct up to radical-branch forms (`sqrt(1-a x) sqrt(1+a x)` vs
  `sqrt(1-a^2 x^2)`) the zero chain's symbolic stages do not identify, or
  carry `hypergeometric` (119 of the class's 163 `hypergeometric(`-expected
  FAIL entries are `unverified`). The second item to trace for a class-7
  uplift, after the harness ceiling.
- **7.2.4a / 7.1.4a / 7.2.4b — the `(d ∓ c^2 d x^2)^p` products.** 44 and
  36 of their `contains-noun` expect an interior marker; the `deferred` 57
  of 7.2.4a are likely the partial-answer case above
  (`(f*x)^m*(a+b*acosh(c*x))^2/(d-c^2*d*x^2)^(1/2)` e236 expects
  `sqrt(-1+c*x)*sqrt(1+c*x)*Unintegrable(…)`; the class-wide count is 61).
  The rest answer with a noun (`(d-c^2*d*x^2)^2*(a+b*acosh(c*x))/x^2` e16,
  7.3 s) or time out on symbolic `m`
  (`x^m*(d-c^2*d*x^2)^3*(a+b*acosh(c*x))` e145).
- **7.5.1 / 7.6.1 / 7.4.1 — timeouts and nouns.**
  `(a+b*asech(c*x))/x^7` e32, `acoth(a*x)/(c+d*x^2)` e39 time out;
  `asech(a*x)^2/x^2` e7 answers a noun in 0.7 s.
- **7.1.5 / 7.2.5:** `(d+e*x)^2/(a+b*asinh(c*x))^2` e25 expects
  `Chi`/`Shi` terms and answers a noun; `sqrt(a+b*asinh(c+d*x))/(c*e+d*e*x)`
  e185 is an interior-marker entry.

**Residue → expected-head census** (probe 28):

| head | entries | in FAIL | FAIL % | FAIL classes |
|---|---:|---:|---:|---|
| `polylog(` | 1125 | 419 | 37.2 | contains-noun 259, unverified 88, timeout 66, deferred 6 |
| `Unintegrable(` | 606 | 245 | 40.4 | contains-noun 183, deferred 61, timeout 1 |
| `hypergeometric(` | 358 | 163 | 45.5 | unverified 119, timeout 35, contains-noun 9 |
| `Chi(` / `Shi(` | 258 / 250 | 39 / 40 | 15.1 / 16.0 | contains-noun |
| `AppellF1(` | 47 | 36 | 76.6 | unverified 36 |
| `elliptic_f(` / `elliptic_e(` / `elliptic_pi(` | 76 / 56 / 23 | 17 / 17 / 7 | 22.4 / 30.4 / 30.4 | timeout |
| `CannotIntegrate(` | 34 | 10 | 29.4 | contains-noun 10 |
| `GAMMA(` | 42 | 5 | 11.9 | contains-noun 5 |
| `erf(` / `erfi(` | 301 / 309 | 4 / 4 | 1.3 / 1.3 | contains-noun |
| `FresnelS(` / `FresnelC(` | 24 / 24 | 4 / 4 | 16.7 | timeout 3, error 1 |

## 6. Structural ceilings (per spec §3.4, per class)

- **polylog: 88 `unverified` — the largest polylog block of the four
  classes, still not a trigger on its own.** 1,125 entries expect
  `polylog`; 706 PASS `expected`, 419 FAIL, of which 88 `unverified` (the
  class a derivative shim could move; an upper bound, since the record
  does not say whether the package's own answer carries `polylog`). The
  shim is already ticketed (`.scratch/class3-polylog-ceiling/issues/01`,
  go number 638 from class 3); class 7 adds ≤ 88 to it. The decision stays
  with that ticket.
- **AppellF1: 47 entries — `expected` 11, `unverified` 36.** The 36 are
  the ceiling (`appell_f1` has no derivative): 77 % of the class's
  AppellF1 entries, all of them answered.

## 7. Earlier-class status

Byte-identity green for every class, 1–9 plus the rewrite tables (re-run
2026-09-26 at `e70ee89`) — including after ticket 18 moved classes 1/3
onto the native heads (its closed P3 exception `undo_native_heads`, 53
class-1/3 sites pinned). The port's own slice A/B
(`probes/corpus/23-class7-slice-ab.out`, 81 entries): 0 transitions. The
full re-measure on the same core against master's promoted records
(`test/final_ab_master_class{1,2,3,6}.out`): class 1 18,400 → 23,203
(PASS→FAIL 85), class 2 758 → 863 (3), class 3 1,692 → 2,446 (5), class 6
2,474 → 4,314 (46) — the four ports and the fixes together.

## 8. Final gates

As the class-8 record §8 (the same code and core): Layer A
`Results: 1583 passed, 0 failed`, rule-table order 18/0, section-9 e2e
9/0, dispatch 119/0, mr-match 57/0, mr-tree 84/0, run-records 43/0,
harness guards 0 failed (`39eba80`; code unchanged to `c2deb32`);
matcher regression suite 109/0 in both arms (`e70c00e`); P3 static 29/0,
head rewrites 64/0, byte-identity EMPTY for classes 1–9 + rewrites
(re-run 2026-09-26 at `e70ee89`).

## 9. Follow-ups

- `.scratch/corpus-harness/issues/05` (new) — Rubi's partial answers
  cannot PASS: 202 class-7 entries (140 `contains-noun`, 61 `deferred`).
- `.scratch/class-ports/issues/21` — the dispatch index; 78 entries still
  time out at 100 s.
- `.scratch/class3-polylog-ceiling/issues/01` — class 7 adds ≤ 88
  `unverified`.
- `.scratch/class-ports/issues/18` — fixed on this branch (`025c589`).
- Not ticketed: the 7.3.6/7.4.2 `unverified` block (193 entries) —
  the first measured question is whether the answers are correct (a
  numeric check of a sample would settle it); the 37 `error`s at the
  100 s re-check; `atanh(1)`/`acoth(1)` raising (ticket 04 finding 3;
  not observed as a cause here, since `error` is 2 entries at 30 s).
