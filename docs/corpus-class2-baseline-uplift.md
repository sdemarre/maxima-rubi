# Class-2 corpus — rubi() acceptance record (milestone-2 pilot, closed 2026-08-28)

The milestone-2 pilot's measured acceptance: the full 965-entry class-2
(exponentials) corpus under the ported rule set (`rubi()`, rules-only
default, 3,180 rules), against the class-2 `integrate` baseline. The
pilot's scope (spec §1): **process-first — generalize the pipeline and
prove it end-to-end on class 2 (the smallest class-2+ corpus section),
so that classes 3–8 become runbook tickets rather than projects.** The
uplift is a *measurement of the pilot, not a target* (spec §4.7).
Inputs:

- `test/corpus_class2.out` — the merged package record (965/965 entries,
  3 files, 26 shards, no dupes/missing/extra; build-stamped header,
  merged 2026-08-28 13:26 UTC);
- `test/corpus_class2.baseline.out` — the merged `integrate` baseline
  (965/965, 3 per-file shards, merged 2026-08-28 12:53 UTC);
- `test/corpus_class2.timeout-rerun/corpus_class2.timeout5m.out` +
  `merge.out` — the 300 s re-check of the package run's 7 `timeout`
  entries (7/7, merged 2026-08-28 13:53 UTC — the 50cce22 fix round
  re-stamped the header; the 7/7 entry lines are byte-identical to the
  original merge);
- `probes/translation/03-class2-syntax-census.out` — the rule-set census
  (Task 1);
- `probes/corpus/02-class2-answer-heads.out` — the section's
  answer-head census (Task 1);
- `probes/answer-side/01-answer-side-identities.out` — the
  answer-side identities probe: the two normalization conventions
  (UPPER `gamma_incomplete`, the `expintegral_ei` derivative) measured
  within the harness zero chain (final-review close-out);
- `docs/superpowers/specs/2026-08-28-milestone-2-class2-pilot-design.md`
  (commit `ff814e9`) and
  `docs/superpowers/plans/2026-08-28-milestone-2-class2-pilot.md`
  (commit `b78d5aa`) — the pilot's design and plan;
- `.superpowers/sdd/progress.md` — the Tasks 1–10 ledger (measurements,
  deviations, the Task-10 A/B and heap-exhaustion findings).

Build for the measurement (stamped in the records' headers): Maxima
5.50.0 (build date 2026-08-20 21:36:22), SBCL 2.6.7,
x86_64-pc-linux-gnu. Code state: branch `milestone-2`
(`b78d5aa..bb74cb6`). Rule set: **3,180 rules** — 3,055 (the accepted
class-1 set) + 125 (the class-2 port). Rules core fingerprint
`aa53741f7ac802e2c3b8bd93720b219d` (`test/mr_rules.core.stamp`, 3,180
rules, 2026-08-28 11:39:15 UTC — gitignored, rebuilt by
`test/build_rules_core.sh`; the ledger records the prefix `aa53741f…`).

## 1. Rule set

From `Rubi.m`'s LoadRules list (T1 inventory): class 2 is **3 files,
125 rules, all with `/;` conditions** (census line 3) —
`2.1 (c+d x)^m (a+b (F^(g (e+f x)))^n)^p` = 14,
`2.2 (c+d x)^m (F^(g (e+f x)))^n (a+b (F^(g (e+f x)))^n)^p` = 4,
`2.3 Miscellaneous exponentials` = 107. Re-classified against the
milestone-1 generator's closed table: **AUTO 80 (64.0 %) / MANUAL 45
(36.0 %)**; the manual bucket is 2.3 Miscellaneous = 37 rules / 22
distinct token-sets, 2.1 = 8 / 5 (census `== manual bucket by file ==`).
Rule-file numbering does not align with corpus-file numbering (corpus
2.1 is `u (F^(c (a+b x)))^n` — 98 entries; 2.2 — 93; 2.3 — 774; the
trees are numbered independently, as the class-1 1.2.1.4 case already
showed).

Token closure (the census's UNLISTIED list, adjudicated in Tasks 1–6 —
this table is what made the generation loud-failure-free):

| token (calls) | disposition |
|---|---|
| `TrueQ` (9) | ported `%mr_trueQ` (trivial: `is(…)=true`); used only on the `$UseGamma` control flag |
| `PowerOfLinearQ` (6), `PowerOfLinearMatchQ` (3), `NormalizePowerOfLinear` (6) | **upstream gap** — ported from the call-site contract (below) |
| `Exponent` (7: 5 cond + 2 repl) | reused the existing `%mr_degree` walker (no new code — the plan §3.3 "reuse, don't rewrite" check) |
| `PowerQ` (2) | ported `%mr_powerQ` |
| `FunctionOfExponentialQ` (1), `FunctionOfExponential` (1), `FunctionOfExponentialFunction` (1), `FunctionExpand` (1) | ported cluster C (state-threaded family, `%mr_functionExpand` gamma-integer case) |
| `NormalizeIntegrand` (1) | ported cluster B (the chain, two documented deviations) |
| `Gamma` (5, all 2-arg), `ExpIntegralEi` (3), `Erf` (3), `Erfi` (1), `Exp` (2) | answer-side RENAMEs to the natives (below) |
| `$UseGamma` (inside the 9 `TrueQ` sites) | package variable `mr_use_gamma_flag` |
| `Part` (`[[…]]`, 6 sites / 2 rules) | generator `Part` handler, loud failure mode (Task 2) |

The two documented upstream gaps (both measured 2026-08-28, plan Task 1)
and their port decisions:

1. **The `PowerOfLinear` family is defined nowhere** in the pinned
   clone (grep of all `.m` files, 0 matches) nor in the Rubi-5 stub
   (`Rubi-5.m`, 0 matches), yet is called by 2.1 r17/r18 and
   2.3 r8/r9/r10/r38 (upstream numbers; the generated call sites are
   2.1 r12/r13 and 2.3 r5/r6/r7/r35). Upstream effect: a condition
   carrying an undefined predicate stays a symbol in Mathematica, so
   those rules decline there. Port decision (Task 4, ledger): port from
   the **call-site contract** — `u` is a rational power of a linear
   form in `x`. `%mr_powerOfLinearQ` carries the implicit-exponent
   branches (bare linear — Maxima strips the `x^1` Power head — and
   sqrt-of-linear — `(linear)^(1/2)` stores as a `'sqrt` node);
   `%mr_powerOfLinearMatchQ` is the **strict stored-power test, not an
   alias** of the Q (the alias makes the 2.3 r35 condition
   `PowerOfLinearQ[v,x] && Not[PowerOfLinearMatchQ[v,x]]`
   unsatisfiable, killing the rule); `%mr_normalizePowerOfLinear` is the
   **identity** (the recursion's progress comes from Maxima's own power
   combining; a pathological no-progress self-refire is bounded by the
   runner depth cap — no wrong answers, bounded cost).
2. **`$UseGamma` is undefined** in `Rubi.m` and the utility files; the
   only upstream documentation is the file-level `$UseGamma = False;`
   assignment (`2.1 (…).m:4`) and the class-2 corpus file headers
   (the optimal antiderivatives assume `$UseGamma = false`). Port
   decision: the package variable `mr_use_gamma_flag : false` (the same
   default; a variable, not a function — the `mr_simplify_flag`
   precedent). The 9 gated sites split 7 `Not[TrueQ[$UseGamma]]` —
   **active** at the default: the 2.1 r1/r2/r5 recursive reductions,
   the 2.1 r3 `expintegral_ei` answer, the 2.3 r3/r6 `ExpandIntegrand`
   orderings, and the 2.3 r25 `gamma_incomplete` answer — and 2
   `TrueQ[$UseGamma]` (the 2.3 r2/r5 `ExpandIntegrand` orderings —
   **declined** at the default, firing only if the flag is set true).

## 2. Answer-side normalization (two sides, one table)

- **Generator side** — the translation table emits the native Maxima
  head, so `rubi()` answers are idiomatic: `Gamma` →
  `gamma_incomplete` (5/5 two-arg), `ExpIntegralEi` → `expintegral_ei`
  (3), `Erf` → `erf`, `Erfi` → `erfi`, `Exp` → `exp` (Task 2; the
  generated rule files carry 8 `gamma_incomplete|expintegral_ei`
  replacement occurrences — Task 3 statics).
- **Harness side** — `test/corpus_driver.py`'s `HEAD_REWRITES` applies
  the same table to *both* the candidate and the corpus expectation
  before the zero chain (integrand text + primary and secondary
  expected texts; the `els[2]` steps are display-only and never reach
  Maxima). The class-2 section's answer-head census
  (`probes/corpus/02-class2-answer-heads.out`) needed exactly two rows
  — `GAMMA(` 191 (all 2-arg), `Ei(` 237 (all 1-arg); no other renamable
  head occurs (`erf(`/`erfi(` are already native-lowercase in the
  corpus; `F0(` 14 is a **free function symbol**, not a 0F1
  hypergeometric, and `polylog`/`AppellF1` have no native — not
  renamed):
  - `GAMMA(` → `gamma_incomplete(` — the measured convention
    (`probes/answer-side/01-answer-side-identities.out`, A1–A5):
    `gamma_incomplete(a, z)` in this build is the **2-arg UPPER**
    incomplete gamma, `diff(gamma_incomplete(a, z), z) = -z^(a-1) %e^-z`,
    and the value pins `gamma_incomplete(1, z) = %e^-z` /
    `gamma_incomplete(2, z) = (z+1) %e^-z` close within the harness zero
    chain (they do not close symbolically — the build does not auto-
    reduce `gamma_incomplete(1, z)` — they close on the chain's numeric
    stage) — the corpus `GAMMA(a, z)` convention maps straight over;
  - `Ei(` → `expintegral_ei(` — the measured convention (the probe's
    B1–B3): `diff(expintegral_ei(z), z) = %e^z/z`, the residual
    closing to 0 within the chain.
  The rewrites are idempotent (native forms untouched) and guarded by a
  `(?<![A-Za-z0-9_])` lookbehind so longer names stay intact
  (`test/test_head_rewrites.py`: `XEi(2)` untouched, free `F0(x)`
  untouched, `gamma_incomplete(2, z)` untouched). Measured totals: the
  per-shard `head rewrites:` lines sum over the 26 shards to
  `gamma_incomplete(` 191 + `expintegral_ei(` 237 — exactly the census
  counts (the per-shard lines are on disk; the merged record carries no
  aggregate — the merger skips per-shard stats lines, a pre-existing
  Task-8 behavior the class-1 merged record shares).
- **Class-1 no-op proof** — the normalization cannot touch class 1:
  0 occurrences of every renamable head in the
  `1 Algebraic functions/*.mac` suite files (plan Task 1 measured
  basis, probed 2026-08-28); 0 occurrences of
  `gamma_incomplete(`/`expintegral_ei(` in the accepted class-1 merged
  record `test/corpus_class1.out` (measured 2026-08-28); and the
  driver's class-1 slice prints `head rewrites: {}` while the class-2
  slice prints `{'gamma_incomplete(': 1}` — the rewritten entry
  classified `expected`, i.e. the two-sided normalization closing its
  zero chain live (both polarities proven; commit `c00b5d9`).

## 3. Baseline (native `integrate`, T3 mechanics)

Task 9: `probes/corpus/probe-integrate-sample.py` (the section as 10th
positional), 3 per-file shards, 30 s per-entry cap; shard walls
5.6 / 38.2 / 46.3 s (ledger Task 9 — the maxima launch here is ~29 ms
image build; the per-entry cost is solve-dominated). Merged record
`test/corpus_class2.baseline.out`, completeness asserted 965/965,
merged 2026-08-28 12:53 UTC.

| class | count | % | verdict |
|---|---|---|---|
| `verified` | 186 | 19.3 | PASS |
| `expected` | 123 | 12.7 | PASS |
| `no-answer` | 284 | 29.4 | PASS (probe reading: integrate fell to a noun) |
| `unverified` | 357 | 37.0 | FAIL |
| `unexpected` | 14 | 1.5 | FAIL |
| `timeout` | 1 | 0.1 | FAIL (2.2 e58, t=30.1 s) |
| **total** | **965** | | **Results: 593 passed, 372 failed** |

PASS total **593/965 (61.5 %)** — verified+expected 309 (32.0 %) plus
no-answer 284. Note the yardstick's mechanics (probe: 4-stage symbolic
zero-chain, no head rewrites, noun-on-answer-expected = PASS
`no-answer`) — the A/B margin note in §4 carries it.

## 4. Package run (3,180 rules) and A/B

Task 10: the generalized launcher/driver/merger over the
`2 Exponentials/` section, 965/965 entries, 26 shards / 24 processes,
wall 8 min 07 s; merged record `test/corpus_class2.out`, completeness
asserted 965/965, merged 2026-08-28 13:26 UTC.

| class | count | % | verdict |
|---|---|---|---|
| `verified` | 320 | 33.2 | PASS |
| `expected` | 116 | 12.0 | PASS |
| `no-answer` | 64 | 6.6 | PASS |
| `deferred` | 314 | 32.5 | FAIL (top-level 0-firing → `unintegrable` noun) |
| `unverified` | 125 | 13.0 | FAIL (answered, zero chain did not close) |
| `contains-noun` | 14 | 1.5 | FAIL (answer carries the `unintegrable` residue) |
| `timeout` | 7 | 0.7 | FAIL |
| `unexpected` | 4 | 0.4 | FAIL (corpus expected a noun; package answered) |
| `error` | 1 | 0.1 | FAIL (subprocess death — §5, the heap-exhaustion finding) |
| **total** | **965** | | **Results: 500 passed, 465 failed** |

PASS total **500/965 (51.8 %)**.

**Per-class A/B delta** (PASS = {expected, verified, no-answer};
computed from the two records' entry lines, the file prefix of the T3
line; recomputed 2026-08-28):

| corpus file | entries | baseline | package | delta |
|---|---|---|---|---|
| 2.1 `u (F^(c (a+b x)))^n` | 98 | 58/98 (59.2 %) | 31/98 (31.6 %) | −27 (−27.6 pts) |
| 2.2 `(c+d x)^m (F^(g (e+f x)))^n (a+b (…))^p` | 93 | 33/93 (35.5 %) | 33/93 (35.5 %) | 0 |
| 2.3 `Exponential functions` | 774 | 502/774 (64.9 %) | 436/774 (56.3 %) | −66 (−8.5 pts) |
| **total** | **965** | **593/965 (61.5 %)** | **500/965 (51.8 %)** | **−93 (−9.6 pts)** |

Entry-level A/B (reviewer-verified arithmetic, ledger Task 10;
recomputed against the two records 2026-08-28): **PASS→FAIL 309 = 178
genuine declines + 131 yardstick reclassification; FAIL→PASS 216**.

- The 178 genuine declines (baseline `expected`/`verified` → package
  FAIL, **ALL `deferred`** — the rules return a top-level noun where
  native `integrate` had an answer): 2.1 six (all verified→deferred:
  e55, e60–e63, e78), 2.2 eighteen (all verified→deferred), 2.3
  one-fifty-four (expected 61 + verified 93 → deferred).
- The 131 yardstick reclassifications (baseline `no-answer` — PASS
  under the probe — → package FAIL: deferred 74, unverified 44,
  contains-noun 8, timeout 5): 2.1 twenty-one, 2.2 zero, 2.3 one-ten.
- The 216 FAIL→PASS: unverified→verified 156, unverified→expected 50,
  unexpected→no-answer 10 (the corpus expected `Unintegrable`; the
  package declined honestly where `integrate` had answered — 2.2 six,
  2.3 four).

**Margin note** (plan Task-10 header, quoted per the ledger Task-9
carry-over): the baseline record was produced by the probe (4-stage
symbolic zero-chain, no head rewrites, noun-on-answer-expected = PASS
`no-answer`), while the package run uses the driver (8-stage + numeric
chain, head rewrites, `deferred`/`contains-noun` FAIL classes). Net:
**the yardstick errs slightly conservative for the package** (2 of 3
asymmetries flatter it). A stricter comparison = re-run the native
baseline through the driver harness.

**The 300 s timeout re-check** (standing protocol; the record's 7
`timeout` entries re-run exactly at a 300 s per-entry cap, same rules
core; `test/corpus_class2.timeout-rerun/`, 7/7, watcher merge
2026-08-28 13:37:36 UTC, record re-stamped 13:53 UTC):

| entry | run t (30 s) | 300 s t | transition |
|---|---|---|---|
| 2.2 e60 | 30.0 s | 274.3 s | `unverified` |
| 2.3 e56 | 30.1 s | 71.4 s | `error` |
| 2.3 e57 | 30.1 s | 95.4 s | `error` |
| 2.3 e195 | 30.0 s | 32.3 s | `unverified` |
| 2.3 e595 | 30.0 s | 29.8 s | `unverified` |
| 2.3 e610 | 30.0 s | 26.0 s | `unverified` |
| 2.3 e612 | 30.0 s | 22.8 s | `unverified` |

Transitions: **error 2 + unverified 5; now-PASS 0** — the 30 s cap is
NOT the limit for class 2: every entry terminates with an answer or a
measured death well inside 300 s, and none of the seven is
slow-correct. The two `error`s (plus 2.3 e68 below) are the
heap-exhaustion finding; the five `unverified` are the zero chain not
closing in 300 s (e60 at 274.3 s is the longest).

## 5. Residues (input to the follow-up tickets)

FAIL masses by corpus file (package run):

| file | n | unverified | deferred | timeout | other FAIL |
|---|---|---|---|---|---|
| 2.1 | 98 | 36 | 31 | 0 | — |
| 2.2 | 93 | 18 | 31 | 1 | contains-noun 6, unexpected 4 |
| 2.3 | 774 | 71 | 252 | 6 | contains-noun 8, error 1 |
| **total** | **965** | **125** | **314** | **7** | **14 / 1 / 4** |

First ~5 entries of each mass per file (entry, run t from the T3 line):

- **unverified** — 2.1: e2 5.8 s, e3 4.0 s, e4 5.5 s, e5 3.6 s, e8 4.8 s;
  2.2: e32 17.2 s, e33 13.6 s, e39 19.2 s, e40 17.1 s, e46 3.6 s;
  2.3: e70 3.8 s, e71 3.7 s, e96 6.0 s, e97 6.3 s, e126 5.1 s.
- **deferred** — 2.1: e16 1.5 s, e17 6.7 s, e18 0.9 s, e20 6.2 s,
  e21 9.5 s; 2.2: e1 12.9 s, e2 10.0 s, e3 4.8 s, e4 6.3 s, e7 8.0 s;
  2.3: e1 6.8 s, e2 5.4 s, e3 5.2 s, e5 5.0 s, e6 5.5 s.
- **timeout** — 2.2: e60 30.0 s; 2.3: e56 30.1 s, e57 30.1 s,
  e195 30.0 s, e595 30.0 s, e610 30.0 s (e612 30.0 s the seventh).

Likely-cause classification (grounded in the ledger; "likely" marks a
guess, and per-entry traces were not performed for any of these
families):

- **deferred 314 — rule coverage, with a per-file breakdown.** The
  deferred entries are top-level 0-firings: no ported rule matches
  (or every match is rejected by a cond), so `rubi()` returns the
  `unintegrable[f, x]` noun on an answer-expected entry.
   - 2.1 (31; 6 genuine declines): the deferred set splits into two
     populations. **8 PowerOfLinear-gated shapes** (e16–e18, e20–e22,
     e25–e26 — `F^(c (a+b x)) (d+e x)^k` and `…^m`): the suite stores
     the base **expanded** (`d^4+4 d^3 e x+…`, e.g. e20–e22), so the
     ported `%mr_powerOfLinearQ(u, x)` stored-form test
     (`maxima_rubi_utils.mac:4638`) — the first PowerOfLinear-family
     clause in 2.1 r12/r13's conditions — declines them before the
     rules' `integerp(m)` / `Not[LinearMatchQ[v,x] &&
     PowerOfLinearMatchQ[u,x]]` clauses are ever reached. **Likely
     cause: the ported PowerOfLinear semantics — but decline-consistent
     with upstream**: the identical upstream condition carries a
     predicate undefined in the pinned clone, which stays a symbol in
     Mathematica, so the rule declines there too (the §1 upstream-gap
     measurement). Not a port bug on the available evidence; the
     revisit ticket stays conditional (TODO). **23 coverage gaps**
     (e55, e60–e64, e69–e73, e78–e89 — the `e^(-a-b x)(a+b x)^k / x^j`,
     `F^(a+b (c+d x))(e+f x)^2 / x^j`, `e^(-a-b x)(a+b x)^4 /
     (c+d x)^k`, and `F^(c (a+b x)) x^j log(d x)^n (…)` shapes): no
     rule of the 14-rule 2.1 set covers them (likely cause: rule
     coverage, as 2.3).
   - 2.2 (31; 18 genuine declines): the 2.2 rule file is **4 rules**;
     the deferred shapes include the squared/cubed denominators
     `(a+b (F^(g (e+f x)))^n)^k` (k ≥ 2): the 12 deferred entries
     e9–e12, e15–e20, e23–e24 (`x^j/(a+b F^(…))^2` and
     `x^j/(a+b F^(…))^3`, j = 0…3 incl. the sign variants — the
     in-range e13/e14/e21/e22 are the 4 `Unintegrable`-expected
     entries, `no-answer` PASS), and the `(a+b F^x)^k sqrt(c+d x)`
     numerator powers e64–e66. Likely cause: rule coverage (4 rules
     against 93 corpus shapes).
  - 2.3 (252; 154 genuine declines): 107 rules against 774 shapes whose
    expected answers span the section's full head variety (the
    `Ei`/`GAMMA`/`polylog`/`erfi`/`hypergeometric` mix of
    §2/§3). Likely cause: rule coverage — full Rubi reaches many of
    these shapes through substitutions and normalization rules of other
    classes (the class-1 1.2.1 `b`-suffixed precedent: the corpus file
    name-matches a `.m` file absent from LoadRules). This is a
    count-level inference; the per-entry rule traces were not done.
- **unverified 125 — the zero chain does not close on the answer's
  special-function heads.** The residue→expected-head census (this
  task, joining the record's entry lines against the suite files'
  expected texts; inputs committed/pinned): erfi 47, `Ei` 8, `polylog`
  12, `GAMMA` 7, `hypergeometric` 6 (an entry may carry several). The
  mass is largely **baseline-inherited verify gap**: 2.1 carries 23 of
  its 36 that were `unverified` in the baseline (and 2.1 has ZERO
  FAIL→PASS transitions — the driver's stronger chain closed nothing
  the probe missed there), 2.2 carries 17 of 18, 2.3 carries 40 of 71.
  Likely cause: the ratsimp/factor zero chain cannot close
  symbolic `gamma_incomplete`/`expintegral_ei`/`erfi`/
  `hypergeometric` differences unless the answer is in the exact
  antiderivative form (the structural-ceiling family, spec §2.3/§3.4).
  The 12 `polylog`-expected unverified entries are the class-2 instance
  of the polylog ceiling (no `polylog` in the build — spec §2.3: no
  exact manual topic; `diff` of such a head closes only via structural
  match in the `expected` class).
- **timeout 7 + error 1 — not the cap; one measured build bug.**
  Re-checked at 300 s: now-PASS 0 (§4). The 5 `unverified` transitions
  are the chain not closing in 300 s. The 2 `error`s (2.3 e56
  `x^2/(b/f^x+a f^x)`, e57 `x^3/(b/f^x+a f^x)`) plus **2.3 e68
   (`F^(e (f+d x)) H^(t (r+s x))/(a+b F^(e (c+d x)))`, `error` at
   17.4 s in the run)** are the **reproducible SBCL heap exhaustion on
  quotient-of-exponentials integrands** (ledger Task 10 finding):
  matcher/rule-bug candidate, root cause not yet measured — a
  standalone follow-up item (TODO), the pilot's principal finding.
- **contains-noun 14** (2.2 e36–e38/e43–e45; 2.3 e200/e201/e389/e390/
  e431/e437/e448/e449) — the answer carries the `unintegrable`
  catch-all residue: faithful Rubi `CannotIntegrate` markers and
  cascade coverage gaps (the class-1 uplift §6 profile).
- **unexpected 4** (2.2 e56/e57/e62/e63: the corpus expects
  `Unintegrable(…)`; the package answered) — the class-1 ticket-03
  shape (improvements the 2018 corpus cannot accept). The baseline was
  `unexpected` on these too (10 in 2.2: 6 became `no-answer` PASS
  under the package's honest decline, 4 stayed).

## 6. Class-1 status — the accepted record stands

**The class-1 accepted record (19,731/25,697 = 76.8 % vs the T3 49.8 %
baseline; `docs/corpus-baseline-uplift.md`, accepted run
`test/corpus_class1.out`, commit `45fc9b8`) is untouched and stands.**
Per the pilot design (§3.6), the class-1 record was not re-run — no
build change, no class-1 rule change — and the pilot's shared-code
changes are gated against it:

- **No commit on the branch touches `rules/class1/`**
  (`git log master..HEAD --name-only` over that path is empty) — the
  class-1 rule files are byte-identical across the whole branch.
- **Byte-identity gate green** at the generator generalization
  (`ae20582`: 3,026 rules over 72 generated files (67 LoadRules + 5
  `EXTRA_CLASS1` b files), empty `git status --porcelain
  rules/`), re-verified at the table closure + marker-head work
  (`70e6f58`, controller-verified "class-1 gate clean (generate
  `--class 1`, empty git status)"), and re-asserted by this task's
  final gate (Step 4 of the plan).
- **50-entry spot check** (ledger Task 8): a 50-entry class-1 slice
  (17+17+16 over stop-indices 1/2/3) run through the generalized
  driver — all 50 (file, entry) → verdict class **identical** to
  `test/corpus_class1.out` (dict diff).
- **Normalization no-op proof** — §2: 0 renamable-head occurrences in
  the class-1 suite files (Task 1 probe), 0 in `test/corpus_class1.out`
  (measured 2026-08-28), class-1 driver slice `head rewrites: {}`
  (`c00b5d9`).
- The core grew 3,055 → 3,180 (`d964fdb`); class 2 loads **after** all
  of class 1 in LoadRules order (rule priority unchanged for class-1
  integrands); `TABLE_AT_LOAD 3180`
  (`probes/load_wall/probe-class2-load.out`); Layer A 581/0 (the 511
  class-1 targets unchanged + 70 new class-2 and marker-head checks).

## 7. Ledger flags — shared-code changes and their no-regression evidence

Every shared-code change the pilot made, with the commit and the
no-regression evidence that gated it (full detail: the ledger's
Tasks 2–10 entries):

1. **Generalized generator** — `generator/generate_rules.py`
   (`--class N`), `generate_class1.py` → shim. Commit `ae20582`.
   No-regression: class-1 byte-identity gate green (3,026 rules over
   72 generated files (67 LoadRules + 5 `EXTRA_CLASS1` b files),
   empty `git status` on `rules/`).
2. **Generator table closure + `Part` handler + the `%mr_matchQ`
   marker-head case** (shared matcher — the runtime of all 16 class-1
   MatchQ rules). Commit `70e6f58`. No-regression: Layer A 519/0
   (511 + 8 new marker-head checks); class-1 gate clean (regeneration
   byte-identical, empty git status).
3. **Utils additions** (clusters A/B/C; `maxima_rubi_utils.mac`
   +947 lines, pure addition — Task 5's M1 `%mr_numericFactor`
   collision resolved by dropping the brief's duplicate definition,
   0 deletions verified). Commits `4cc259e`/`0850fb5` (A),
   `9262b04`/`4a31b8d` (B), `c845057`/`0028d82` (C). No-regression:
   Layer A green at every cluster (542/0 → 561/0 → 578/0); no class-1
   rule file regenerated (item 1's gate + §6).
4. **Loader + rules core** — `mr_load_all()` (76-term flatten,
   3,180 = 3,055 + 125), `build_rules_core.sh` FP list + image script,
   driver `_core_fingerprint` class-2 glob (BOTH sides, same sort),
   the TLS full-load probe. Commit `d964fdb`. No-regression:
   `TABLE_AT_LOAD 3180` (`probes/load_wall/probe-class2-load.out`);
   core rebuilt with stamp 3,180 rules / fingerprint
   `aa53741f7ac802e2c3b8bd93720b219d`; Layer A 581/0; census spot
   check (2_2 count 4, witness present, 1.1.1.1 still 5).
5. **Driver/launcher/merger generalization + two-sided answer-head
   normalization** (`corpus_driver.py` = class-1 copy + 4 deltas;
   shims re-exporting 7 attrs + loud `__getattr__`;
   `wait_and_merge.sh` parameterized). Commit `a3ee89c` (+ `c00b5d9`
   the stats-line post-loop fix, `7afde83` the `test_merge_classes`
   re-point). No-regression: head-rewrite unit 7/0; the 50-entry
   class-1 spot check (§6); class-1 slice `head rewrites: {}`;
   class-1 launcher dry-run plan byte-identical (40 files / 25,697
   entries, relative sets byte-compared); the no-arg
   `wait_and_merge.sh` invocation byte-identical (POSIX).
6. **Suite-dir fixes** (the in-process driver needs the suite-dir
   positional — the default walk is bounded to the class-1 section):
   merger `ec62741`, launcher `a2f54c1`, re-check record header slug
   `50cce22`. No-regression: a REAL re-merge of the still-on-disk
   class-1 shards (787/787, all lines identical); class-1 merge line
   byte-identical; class-1 walk unchanged (full suite walk + FILTER
   yields the same rel set).
7. **Task-10 script fixes** (`wait_and_merge.sh` merge-argument
   pass-through — the brief's `${@:4}` is dash-incompatible and the
   while-loop replacement off-by-one; final form three guarded
   `shift`s; `launch_timeout_rerun.py` section positional + the
   in-process driver exec's relative suite-dir; DRIVER stays an
   absolute path). Commit `fe5364a`. No-regression: dump-tested both
   polarities; class-1 merge line byte-identical; `sh -n` clean.
