# Class-4 corpus — rubi() acceptance record (trig functions, Step 10 written 2026-09-26)

The measured acceptance of the "4 Trig functions" port: the full
22,472-entry section — the largest after class 1 — under the ported rule
set (`rubi()`, rules-only default, 7,776 rules: the four ports of branch
`class-ports` together), against a native-`integrate` baseline on the
same class scheme. Ported against `docs/class-porting.md` Steps 1–10,
last in the queue 8 → 5 → 7 → 4, on top of the inert-trig substrate
merged 2026-09-21 (`0d7d0cc`: the bridge rule and the 4.7.5 tail
records); the ticket, which carries the Step 1–7 records, is
`.scratch/class-ports/issues/05-class4-trigonometric-functions.md`.

Build for every figure below: **`branch_5_50_base_84_g4204fb669`**
(2026-08-31 13:27:47) on SBCL 2.6.7, stamped in every record header.
Per-entry cap **30 s CPU** (package), **30 s wall** (baseline, §3).

Inputs (all committed on `class-ports`):

- `test/corpus_class4.final.out` — the package record: 22,472/22,472,
  `test/run_corpus_queue.py`, 24 workers, merged 2026-09-25 22:22 UTC;
  rules core **`89bec424959947761abb9416d993bee6`** (7,776 rules, built
  at `c2deb32`; `test/class_ports_final.log`). Harness failures 0.
- `test/corpus_class4.baseline.out` — the native-`integrate` baseline:
  77 per-file shards, a 12-process pool (`test/run_baseline_pool.py`),
  merged 2026-09-25 19:27 UTC.
- `test/corpus_class4.ports.out` — the pre-fix package record (core
  `4daae7ac`, `4ed1877`), the same runner; the §4.3 A/B.
- `test/corpus_class4.final.timeout-rerun/` — the 100 s re-check of ALL
  1,068 `timeout` entries of the record (under the script's
  1,500-entry sampling threshold, so not sampled).
- `test/final_ab_baseline_class4.out`, `test/final_ab_prefix_class4.out`.
- `probes/corpus/28-class-ports-acceptance.{py,run,out}` — the
  histograms, per-file tables, residue → expected-head census, the
  Rubi-marker split, the sample entries and the unloaded-file listing
  below. Static, no Maxima.

## 1. Rule set

**56 loaded rule files / 2,080 rules** — the census's 2,073
(`probes/translation/06-class4-syntax-census.out`: AUTO 1,106 (53.4 %) /
MANUAL 967, every rule with a `/;` condition) plus seven single-line
`If[TrueQ[$LoadShowSteps], …]` wrappers the census glues onto their
neighbours and the generator unwraps (the bridge in 4.1.0.1 and six 4.7.5
substitution catch-alls; a commented eighth at 4.7.5 L75). **2,070 body
records and 10 tail records** — the bare-`u_` bridge (`4_1_0_1` r1) and
`4_7_5` r21/r22/r47/r48/r58/r66/r70/r71/r72, which Mathematica sorts last
by specificity and the dispatcher must therefore walk after every class
(`test/test_rule_table_order.mac`, 18/0 at the final code). Three head
variables (`F` 23 uses, `G` 8, `H` 2); 24 G-9 risk flags over 21 rules,
all accepted with reasoning (ticket 05, Step 1: inert heads have no
definitions, pattern-coefficient Pi shifts do not auto-evaluate,
`Complex[0, fz_]` stays unevaluated).

**One file excluded:** `4.7 Miscellaneous/(a sin(m x) + b cos(n x))^p.m`
(22 `Int[` lines, found verbatim in no loaded file) — in the tree, absent
from `Rubi.m`'s LoadRules (probe 28's listing,
`probes/translation/11-class7-excluded-files.py "4 "`). No corpus file
carries its title (the section's 4.7 corpus is 4.7.1–4.7.7), so no
residue below is an unloaded-file artifact.

Table after the port: **7,776** (5,704 + 2,072 new: the 2,070 bodies,
r66 and r70 — the substrate had already registered the other eight tail
records). Class 4's bodies sit between class 3's last list and class 5's
first (Rubi.m L223–281).

The porting surface (ticket 05, Steps 2–4): rows for the 11 unlisted
tokens (`TrigQ`, `InertTrigQ`, `ExpandTrig`, the four
`Known…IntegrandQ`, `ComplexFreeQ`, `TrigSimplify(Q)`, and one-argument
`Apart` → `expand`); four Step-4 clusters — (a) ComplexFreeQ, InertTrigQ's
MemberQ reading, ExpandTrig, KnownTrigIntegrandQ, TrigSimplify over
TrigSimplifyAux's 31 clauses as a generated rewrite table; (b)
FunctionOfQ's and SubstFor's **hyperbolic arms** (18 active-hyperbolic
4.7.5 records need them) and the FreeFactors/NonfreeFactors quotient
fix; (c) two-argument `Expand[u, x]` → `%mr_expand` (the RENAME row had
emitted Maxima's `expand(u, x)`, an error — made every-class by ticket
19); (d) DeactivateTrig's fast-path clause, load-bearing for
`(c+d x)^m sin/cos(a+b x)`. Layer A 1,400 → 1,495 across the port.

## 2. Normalization

One new driver rewrite, **structural**: `Hypergeometric2F1(a,b,c,z)` →
`hypergeometric([a,b],[c],z)` (the class-8 emitter's shape; 3 occurrences
over 2 entries, both in 4.1.1.3, both also carrying `AppellF1`).
`FresnelC(`/`FresnelS(` were already covered by class 8's rows,
`Si/Ci/Ei/GAMMA(` by the class-2/3 rows. `test/test_head_rewrites.py`
57 → 64. No-op over every entry (`probes/corpus/24-class4-head-rewrite-noop.out`):
0 normalized texts differ outside section 4, and in section 4 exactly the
2 Hypergeometric2F1 entries. Slice A/B (`probes/corpus/25-class4-slice-ab.out`,
101 entries of classes 1/2/3/5/6/7/8, one process at a time): 0
PASS→FAIL, 15 FAIL→PASS, attributed in `probes/corpus/26-class4-slice-attribution.out`.

The integrand side has one measured, unfixed reading (ticket 05, carried
item 6): the driver assigns the integrand at Maxima's defaults, so
`(a*sin(x)^2)^(3/2)` reaches `rubi` as `a^(3/2)*sin(x)^2*abs(sin(x))`
(`probes/maxima/probe-class4-carried-items.out` R1–R3); `mr_model_flags`
binds `radexpand:false` only around the dispatch. That is a harness-wide
question (every class's integrands), left for the `mr_model_flags`
decision; the 4.1.7 `(a sin^2)^p` family is its visible cost (§5).

## 3. Baseline (native `integrate`)

`probes/corpus/probe-integrate-sample.py` through `test/run_baseline_pool.py`
(77 per-file shards, 12 processes, **30 s wall** cap — the class-6
record's probe; AGENTS.md measures the wall/cpu shift near the cap at
0.84–1.00).

| class | count | % |
|---|---:|---:|
| `unverified` | 8820 | 39.2 |
| `deferred` | 7896 | 35.1 |
| `timeout` | 3169 | 14.1 |
| `error` | 1017 | 4.5 |
| `verified` | 683 | 3.0 |
| `no-answer` | 351 | 1.6 |
| `expected` | 350 | 1.6 |
| `unexpected` | 186 | 0.8 |
| **total** | **22472** | **Results: 1384 passed, 21088 failed** |

A caveat stated rather than hidden: the class-4 baseline ran 6 h 18 min,
2026-09-25 15:09 → 21:27 CEST (`test/class_ports_measure.log` L244–246),
concurrently with the class-ports-fixes work on the same host, under a
WALL cap. Its 3,169 timeouts are therefore likely inflated by contention
(unmeasured). The conclusion does not depend on them: were every
baseline timeout a PASS, the baseline would read 4,553, against the
package's 19,932.

## 4. Package run

### 4.1 Verdicts

Queue runner, 24 workers, 30 s cpu cap, merged 88 min after launch
(`test/class_ports_final.log`: 20:54:47 → 22:22:47 UTC), harness failures
0, merge clean 22472/22472 (`test/final_merge_class4.out`).

| class | count | % | verdict |
|---|---:|---:|---|
| `verified` | 17283 | 76.9 | PASS |
| `expected` | 2121 | 9.4 | PASS |
| `no-answer` | 528 | 2.3 | PASS |
| `timeout` | 1068 | 4.8 | FAIL |
| `contains-noun` | 775 | 3.4 | FAIL |
| `unverified` | 632 | 2.8 | FAIL |
| `deferred` | 56 | 0.2 | FAIL |
| `error` | 9 | 0.0 | FAIL |
| **total** | **22472** | | **Results: 19932 passed, 2540 failed** |

**19,932 / 22,472 (88.7 %) against the baseline's 1,384 (6.2 %): net
+18,548 (+82.5 pts)** — the third-highest PASS rate of the eight classes
on this core, after class 1 (23,203 / 25,697, 90.3 %) and class 2
(863 / 965, 89.4 %) (`test/class_ports_final.log`).

### 4.2 A/B against the baseline (`test/final_ab_baseline_class4.out`)

| | |
|---:|---:|
| PASS→PASS | 1226 |
| PASS→FAIL | 158 |
| FAIL→PASS | 18706 |
| FAIL→FAIL | 2382 |

Key sets equal. Gains led by `unverified -> verified` 7,980,
`deferred -> verified` 5,333, `timeout -> verified` 2,284,
`deferred -> expected` 1,313, `error -> verified` 818. The 158 PASS→FAIL
by class: `verified -> contains-noun` 56, `verified -> unverified` 34,
`no-answer -> contains-noun` 32, `no-answer -> timeout` 21,
`verified -> timeout` 6, `expected -> contains-noun` 3,
`verified -> error` 2, `expected -> deferred` 2, `verified -> deferred` 2.

### 4.3 The class-ports fixes (pre-fix → final, `test/final_ab_prefix_class4.out`)

The fixes between the first run (core `4daae7ac`, `4ed1877`) and this
record: symbolic EqQ/NeQ (`d0f0237`), native inverse-hyperbolic heads in
every class (`025c589`, ticket 18), two-argument `Expand` everywhere
(`e799ea6`, ticket 19), the ExpandIntegrand reciprocal-atom guard
(`3bb8c4f`), the `values` trim (`1ebef70`, fix V), depth cap 32
(`2ee8fc4`, fix E), plain `Subst` (`e67e2eb`, fix D), Rubi's GtQ
(`39eba80`); the master merge brought no code (class-8 record §4.3 has
the list with its tickets).

| | |
|---:|---:|
| PASS→PASS | 14621 |
| PASS→FAIL | 9 |
| FAIL→PASS | 5311 |
| FAIL→FAIL | 2531 |

**14,630 → 19,932 (+5,302).** The move is overwhelmingly cost:
`timeout -> verified` 4,061 and `timeout -> expected` 333; timeouts
**5,715 → 1,068**; the record's cpu sum 301,419 s → 115,132 s and the
median entry 8.7 s → 1.9 s (probe 28; sums truncated at the cap). Fix V
is the likely carrier (its commit measures ~74 % of rubi's cpu in the
`values` list walk on the doubled table, and ~3.5x on master); fix D is
the likely carrier of the answer-size cases (its commit: class-4 routes
through 1_1_2_3 r12 / 1_1_2_1 r13/r15 inflating answers to 5 KB – 7 MB
under the old `Subst` simplification). The per-fix split is not measured
here.

### 4.3a PASS->FAIL attribution (pre-fix -> final)

Evidence: `probes/class-ports/final/attribution.{py,out}` (`3deddb7`). Each fix was reverted
alone on the final core (switch arms and overlays), a commit bisect ran over cores built at every
class-ports-fixes commit, and timings are alternating sequential runs. Build
`branch_5_50_base_84_g4204fb669`, 2026-09-26.

9, all caused by fixes landed after the pre-fix run:
- **plain Subst** (`e67e2eb`), 6 entries. The answers are numerically correct (|dA/dx - f| of 1e-8 or less, `11-numcheck-final.out`), but unsimplified, so the zero chain cannot close them.
- **fix A**, 2 entries: one refolded by 1_2_3_1 r11 (ticket 22), one ending in a partial answer.
- **symbolic EqQ**, 1 entry: the zero chain's `factor()` on radical kernels runs past the cap (ticket 23; the proposed fix recovers it).

### 4.4 Timeout re-check (100 s)

All 1,068 `timeout` entries at a 100 s cap, 12 workers
(`test/corpus_class4.final.timeout-rerun/merge.out`, 1068/1068):

| at 100 s | n |
|---|---:|
| `verified` (now PASS) | 461 |
| `timeout` | 426 |
| `contains-noun` | 115 |
| `error` | 37 |
| `unverified` | 15 |
| `expected` (now PASS) | 14 |

**475 slow-correct entries — 2.1 % of the section**, against class 6's
0.04 %: at 100 s the section would read 20,407 (90.8 %). The cap binds
materially here, and the route is matcher speed, not budget (the 30 s
cap stays, AGENTS.md): `.scratch/class-ports/issues/21` (the dispatch
index). The likely reading, from ticket 05 (carried item 8, unmeasured):
an ACTIVE trig integrand walks the whole class-1–3 body before the tail
bridge deactivates it, retrying the general class-1 conditions over many
bindings. The 426 still timing out at 100 s concentrate in 4.1.2.2 (45),
4.7.7 (42), 4.1.1.2 (40), 4.3.4.2 (22), 4.5.1.2 (22), 4.3.1.2 (21),
4.3.2.1 (19); the 37 `error`s' cause is not recorded by the re-check
(likely heap exhaustion at the longer cap — unmeasured).

## 5. Residues

FAIL mass **2,540 = `timeout` 1,068 (42 %) + `contains-noun` 775 (31 %) +
`unverified` 632 (25 %) + `deferred` 56 + `error` 9**. Coverage is not
the limit (`deferred` 56, 0.2 %): the ticket's 2026-08-30 expectation of
class 3's deferred profile at 7x scale did not hold. What remains is cost, nouns, and verification.

**Rubi's own nouns** (probe 28): 587 entries expect a top-level
`Unintegrable`/`CannotIntegrate` (528 PASS `no-answer`, 38
`contains-noun`, 21 timeout); **117 expect a partial answer carrying one
inside** — 110 `contains-noun`, 6 `deferred`, 1 timeout. The driver
cannot PASS an answer identical to Rubi's partial answer
(`.scratch/corpus-harness/issues/05`); 148 of the 775 `contains-noun`
(19 %) are entries where Rubi returns no noun-free answer — a smaller
share than in classes 5/7/8.

The eighteen largest FAIL files (1,650 of the 2,540):

| corpus file | N | PASS base | PASS final | FAIL | FAIL by class |
|---|---:|---:|---:|---:|---|
| 4.7.3 (c+d x)^m trig^n trig^p | 397 | 26 | 265 | **132** | contains-noun 115, deferred 6, timeout 5, unverified 5, error 1 |
| 4.3.2.1 (a+b tan)^m (c+d tan)^n | 1328 | 15 | 1198 | **130** | contains-noun 67, timeout 47, unverified 16 |
| 4.7.7 Trig functions | 950 | 194 | 828 | **122** | timeout 53, contains-noun 49, deferred 10, unverified 10 |
| 4.1.2.2 (g cos)^p (a+b sin)^m (c+d sin)^n | 1563 | 55 | 1444 | **119** | timeout 91, unverified 16, contains-noun 12 |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | 1373 | 56 | 1262 | **111** | timeout 70, unverified 32, contains-noun 9 |
| 4.2.4.2 (a+b cos)^m (c+d cos)^n (A+B cos+C cos^2) | 1541 | 0 | 1436 | **105** | timeout 105 |
| 4.5.1.2 (d sec)^n (a+b sec)^m | 879 | 87 | 776 | **103** | unverified 53, timeout 44, contains-noun 5, error 1 |
| 4.1.2.1 (a+b sin)^m (c+d sin)^n | 837 | 18 | 743 | **94** | timeout 49, unverified 43, contains-noun 2 |
| 4.1.1.2 (g cos)^p (a+b sin)^m | 653 | 44 | 561 | **92** | timeout 61, unverified 28, contains-noun 3 |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | 499 | 28 | 412 | **87** | contains-noun 33, unverified 33, timeout 21 |
| 4.3.3.1 (a+b tan)^m (c+d tan)^n (A+B tan) | 855 | 1 | 770 | **85** | timeout 53, contains-noun 22, unverified 10 |
| 4.1.10 (c+d x)^m (a+b sin)^n | 348 | 49 | 266 | **82** | contains-noun 58, timeout 23, unverified 1 |
| 4.1.7 (d trig)^m (a+b (c sin)^n)^p | 594 | 64 | 520 | **74** | unverified 32, timeout 20, contains-noun 18, deferred 4 |
| 4.5.7 (d trig)^m (a+b (c sec)^n)^p | 471 | 14 | 402 | **69** | unverified 34, timeout 25, contains-noun 10 |
| 4.7.6 f^(a+b x+c x^2) trig(d+e x+f x^2)^n | 142 | 17 | 73 | **69** | contains-noun 59, unverified 9, deferred 1 |
| 4.3.4.2 (a+b tan)^m (c+d tan)^n (A+B tan+C tan^2) | 171 | 0 | 110 | **61** | timeout 55, contains-noun 6 |
| 4.5.1.3 (d sin)^n (a+b sec)^m | 306 | 12 | 245 | **61** | unverified 26, timeout 21, contains-noun 13, deferred 1 |
| 4.1.0 (a sin)^m (b trg)^n | 538 | 49 | 484 | **54** | unverified 52, error 1, timeout 1 |
| the other 59 files | 9027 | 655 | 8137 | 890 | timeout 324, contains-noun 294, unverified 232, deferred 34, error 6 |

Readings (sample entries from probe 28, with the record's cpu time):

- **Timeouts are elliptic-heavy.** At least 423 of the 1,068 (40 %)
  expect an elliptic integral (`elliptic_e(` 423, `elliptic_f(` 417,
  `elliptic_pi(` 258 of the timeouts, overlapping): the fractional-power
  `(a+b sin)^m (c+d sin)^n` / `sec` families —
  `sin(c+d*x)^4*sqrt(a+a*sin(c+d*x))` 4.1.2.1 e32,
  `(c+d*sin(e+f*x))^(9/2)/(a+b*sin(e+f*x))^3` e758,
  `cos(c+d*x)^2*sin(c+d*x)^3*sqrt(a+a*sin(c+d*x))` 4.1.2.2 e322,
  `(a+a*sec(c+d*x))^(2/3)*(A+C*sec(c+d*x)^2)` 4.5.4.2 e295. 4.2.4.2's
  entire FAIL mass (105) is timeout
  (`(A+C*cos(c+d*x)^2)*sec(c+d*x)^3/(a+b*cos(c+d*x))^4` e592).
- **4.7.3 `(c+d x)^m trig^n trig^p` — the noun block (115).**
  `(c+d*x)^4*cos(a+b*x)*csc(a+b*x)` e32 (1.9 s),
  `(c+d*x)^2*csc(a+b*x)*sec(a+b*x)^2` e268 expect `polylog`/`atanh(%e^(%i·))`
  answers; 27 of the 115 are interior-marker entries. Likely the
  `(c+d x)^m × csc/sec` sub-integrals Rubi routes through 4.1.10/4.5.10
  (`contains-noun` 58 in 4.1.10 and 9 in 4.5.10 point the same way) —
  unmeasured. `(c+d*x)^m*sec(a+b*x)*sin(a+b*x)^2` e215 is `deferred`
  (expects `GAMMA(1+m, …)` terms).
- **4.7.6 `f^(quadratic) trig(quadratic)` — erf/erfi.** 59 `contains-noun`;
  the section's `erf(`/`erfi(`-expected entries FAIL 34/42 and 44/64, all
  `contains-noun`. Likely the exponential-of-quadratic sub-integrals after
  `ExpandTrigToExp` (class 2's erf route) not closing — unmeasured.
- **`unverified` 632 — AppellF1 and hypergeometric answers.** 4.5.1.2
  `(e*sec(c+d*x))^(2/3)/sqrt(a+a*sec(c+d*x))` e280 and
  `(d*sec(e+f*x))^n/(a+a*sec(e+f*x))^(3/2)` e319 expect `AppellF1`;
  4.1.2.1 `(1+sin(e+f*x))^m*(3+sin(e+f*x))^(-1-m)` e624 and 4.3.2.1
  `cot(c+d*x)^2*(a+%i*a*tan(c+d*x))^m` e331 expect `hypergeometric`.
  Of the 632, 142 expect `AppellF1` (the ceiling, §6) and 277 expect
  `hypergeometric` (overlapping). 4.1.0 `(a sin)^m (b trg)^n`: 52 of its
  54 FAIL are `unverified` (the fractional-power products, likely the
  same verification limit).
- **4.1.7 `(d trig)^m (a+b (c sin)^n)^p` (74)** — the radexpand-at-read
  family of §2. PASS 350 (pre-fix) → 520 with the fixes.
- **The trinomial files 4.1.9 / 4.2.9 / 4.3.9 / 4.4.9** — PASS 9/19,
  9/20, 15/51, 12/32; mostly timeouts (4.3.9 also 16 `contains-noun`,
  4.4.9 18).
- **4.7.7 Trig functions (122)** — the section's miscellany:
  `x*sec(c+d*x)^2/(a+c*sec(c+d*x)^2+b*tan(c+d*x)^2)` e163 times out;
  `sin((a+b*x)/(c+d*x))` e36 answers a noun; `sin(a+b*x)/(c+d*x^2)` e31
  is `deferred`; `F(c,d,cos(a+b*x),r,s)*sin(a+b*x)` e644 (a free function,
  expected `CannotIntegrate`) answers a noun.

**Residue → expected-head census** (probe 28; `AppellF1` counted per
ENTRY here — the Step-1 census's 823 is occurrences):

| head | entries | in FAIL | FAIL % | FAIL classes |
|---|---:|---:|---:|---|
| `elliptic_f(` | 3744 | 462 | 12.3 | timeout 417, contains-noun 25, unverified 19, deferred 1 |
| `elliptic_e(` | 3733 | 469 | 12.6 | timeout 423, unverified 24, contains-noun 22 |
| `hypergeometric(` | 1734 | 418 | 24.1 | unverified 277, timeout 105, contains-noun 35, error 1 |
| `elliptic_pi(` | 1245 | 272 | 21.8 | timeout 258, contains-noun 13, deferred 1 |
| `AppellF1(` | 605 | 265 | 43.8 | unverified 142, timeout 69, contains-noun 52, error 1, deferred 1 |
| `polylog(` | 456 | 234 | 51.3 | contains-noun 172, timeout 49, error 7, unverified 6 |
| `Unintegrable(` | 647 | 158 | 24.4 | contains-noun 134, timeout 18, deferred 6 |
| `Si(` / `Ci(` | 363 / 361 | 97 / 97 | 26.7 / 26.9 | contains-noun 76, deferred 15, unverified 4, timeout 2 |
| `GAMMA(` | 161 | 46 | 28.6 | unverified 39, contains-noun 4, deferred 3 |
| `erfi(` / `erf(` | 64 / 42 | 44 / 34 | 68.8 / 81.0 | contains-noun |
| `CannotIntegrate(` | 57 | 18 | 31.6 | contains-noun 14, timeout 4 |
| `FresnelC(` / `FresnelS(` | 231 / 226 | 1 / 3 | 0.4 / 1.3 | contains-noun |
| `Hypergeometric2F1(` | 2 | 2 | 100 | contains-noun 2 |
| `HurwitzLerchPhi(` | 1 | 1 | 100 | contains-noun 1 |
| `Ei(` | 6 | 0 | 0.0 | — |

## 6. Structural ceilings (per spec §3.4, per class)

- **AppellF1: the ceiling stands, and class 4 is where it is largest.**
  605 entries expect `AppellF1`; 340 PASS `expected` (form-identical
  answers cancel in the zero chain), and **142 are `unverified`** —
  answers that do not close because `appell_f1` has no derivative (the
  reading the Step-1 census predicted; per entry it is likely, not
  measured, that the package answer carries `appell_f1`). No derivative
  shim is proposed: AppellF1's derivative is not elementary.
- **polylog: no trigger.** 456 entries, 222 PASS `expected`, 234 FAIL of
  which only **6 `unverified`** — the mass is `contains-noun` (172). The
  shim ticket (`.scratch/class3-polylog-ceiling/issues/01`) gains ≤ 6.
- **`HurwitzLerchPhi`** (1 entry) and the free function `F(` (4.7.7) FAIL
  as expected; `lerch_phi` does not differentiate (ticket 05, Step 1b).
- **hypergeometric is not a spec ceiling** — Maxima differentiates
  `hypergeometric` (ticket 05, Step 1b) — yet 277 class-4 entries (and
  119 class-7) expecting it are `unverified`. Whether those answers are
  correct and the zero chain merely fails to close them is the open
  question; unmeasured, listed in §9.

## 7. Earlier-class status

Byte-identity green for every class, 1–9 plus the rewrite tables (re-run
2026-09-26 at `e70ee89`). The port's slice A/B
(`probes/corpus/25-class4-slice-ab.out`, 101 entries of classes
1/2/3/5/6/7/8): **0 PASS→FAIL, 15 FAIL→PASS** — class 6 +7, class 8 +3,
class 1 +2, class 7 +2, class 5 +1 — attributed in
`probes/corpus/26-class4-slice-attribution.out` (nested sub-integrals
now answered through class-4 records; the class-1 pair through the
FreeFactors quotient fix, which also sent 3.1.5 e1 `unverified -> timeout`,
ticket `.scratch/class-ports/issues/20`).

The full re-measure of the earlier classes on the same core against
master's promoted records (`test/final_ab_master_class{1,2,3,6}.out`):

| class | master | final | PASS→FAIL | FAIL→PASS |
|---|---:|---:|---:|---:|
| 1 Algebraic | 18,400 | 23,203 | 85 | 4,888 |
| 2 Exponentials | 758 | 863 | 3 | 108 |
| 3 Logarithms | 1,692 | 2,446 | 5 | 759 |
| 6 Hyperbolic | 2,474 | 4,314 | 46 | 1,886 |

Class 6's +1,840 is the move ticket 05 predicted class 4 would unlock
(the inert-trig bridge answering the class-6 `.7` family); how much of it
is class 4's rather than the fixes' is the attribution's to say. All eight
classes: 61,266 of 70,385 entries PASS (87.0 %) on this core.

### 7.1 The earlier classes' PASS->FAIL, attributed

139 losses against master's promoted records (class 1 85, 2 3, 3 5, 6 46), from the same
attribution (`probes/class-ports/final/attribution.out`). Across all 182 losses of the final
re-measure, the buckets are:
- **fix A** (the ExpandIntegrand guard), 78: 35 refolded by 1_2_3_1 r11 and cut by the seen
  test (ticket 22), 17 ending in a partial answer or an unverified form, 14 past the cap.
- **symbolic EqQ**, 47: 37 are the zero chain's `factor()` on radical kernels (ticket 23;
  a proposed fix, measured, recovers 36 and loses none), and 9 or 10 follow Rubi's reading into
  a slow or noun route.
- **two-valued GtQ**, 13.
- **plain Subst**, 7.
- **carried**, 33: class 6's pre-existing families, identified by the class-6 attribution.
- **noise**, 1.
- **wrong answer**, 1: 1.2.2.2 e1035, a degenerate zero coefficient, which needs both plain
  Subst and the two-valued GtQ (ticket 24).

None blocks the merge. Against that: 4,888 / 108 / 759 / 1,886 FAIL->PASS in classes 1 / 2 / 3 / 6.

## 8. Final gates

As the class-8 record §8 (the same code and core): Layer A
`Results: 1583 passed, 0 failed`, rule-table order 18/0, section-9 e2e
9/0, dispatch 119/0, mr-match 57/0, mr-tree 84/0, run-records 43/0,
harness guards 0 failed (`39eba80`; code unchanged to `c2deb32`);
matcher regression suite 109/0 in both arms (`e70c00e`); P3 static 29/0,
head rewrites 64/0, byte-identity EMPTY for classes 1–9 + rewrites
(re-run 2026-09-26 at `e70ee89`).

## 9. Follow-ups

- `.scratch/class-ports/issues/21` — the dispatch index. Class 4 is its
  main weight: 1,068 timeouts, 475 of them slow-correct at 100 s.
- `.scratch/corpus-harness/issues/05` (new) — Rubi's partial answers
  cannot PASS: 117 class-4 entries.
- `.scratch/class-ports/issues/20` — the FreeFactors quotient fix's 3.1.5
  slowdown (class 3).
- `.scratch/class-ports/issues/07` / `09` — bare-`u_` placement.
- `.scratch/class3-polylog-ceiling/issues/01` — class 4 adds ≤ 6.
- The `mr_model_flags` / radexpand-at-read question (§2; 4.1.7).
- Not ticketed: the `hypergeometric`/`AppellF1` `unverified` block
  (277 + 142, overlapping; a numeric check of a sample would say whether
  the answers are right); 4.7.3's `(c+d x)^m` noun block (115); 4.7.6's
  erf route (59); the 37 `error`s at the 100 s re-check; ticket 05's
  carried item 5 (the generated rit r4 duplicating `%mr_reduceInertTrig3`).
