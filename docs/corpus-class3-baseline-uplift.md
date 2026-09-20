# Class-3 corpus — rubi() acceptance record (milestone-3, closed 2026-08-30)

Milestone-3's measured acceptance: the full 3,085-entry class-3
(logarithms) corpus under the ported rule set (`rubi()`, rules-only
default, 3,513 rules), against the class-3 `integrate` baseline.
Milestone-3 scope (plan §1): **the first full runbook instantiation** —
`docs/class-porting.md` Steps 1–10 executed end-to-end on class 3,
the first class ported by the runbook rather than by a bespoke
plan, so that classes 4–8 are runbook tickets (the M2 pilot's goal,
now with a worked instantiation). The uplift is a *measurement, not a
target*. Inputs:

- `test/corpus_class3.out` — the merged package record (3,085/3,085
  entries, 9 files, 29 shards, no dupes/missing/extra; build-stamped
  header, merged 2026-08-30 00:18 UTC);
- `test/corpus_class3.baseline.out` — the merged `integrate`
  baseline (3,085/3,085, 3 per-file shards, merged 2026-08-29 23:34
  UTC);
- `test/corpus_class3.timeout-rerun/corpus_class3.timeout100s.out` +
  `merge.out` — the 100 s re-check of the package run's 117 `timeout`
  entries (117/117, merged 2026-08-30 00:36 UTC);
- `probes/translation/04-class3-syntax-census.out` — the rule-set
  census (Task 1);
- `probes/corpus/03-class3-answer-heads.out` — the section's
  answer-head census (Task 1);
- `probes/answer-side/01-answer-side-identities.out` — the
  answer-side identities probe (M2; the `GAMMA(`/`Ei(` conventions);
- `probes/load_wall/probe-class3-load.out` — the full-load TLS probe
  (ends `TABLE_AT_LOAD 3513`);
- `probes/corpus/04-class3-residue-answer-heads.{py,run,out}` — the
  residue census (this task: FAIL masses per file + the
  residue → expected-head census);
- `docs/superpowers/plans/2026-08-29-milestone-3-class3.md` — the
  plan (the runbook instantiated, 11 tasks);
- `.superpowers/sdd/progress.md` — the Tasks 1–10 ledger
  (measurements, deviations, the Task-10 A/B and death census).

Build for the measurement (stamped in the records' headers): Maxima
`branch_5_50_base_84_g4204fb669` (build date 2026-08-29 17:58:20),
SBCL 2.6.7, x86_64-pc-linux-gnu — the **2026-08-29 REBUILD** of the
same source revision (the AGENTS.md 2026-08-20 stamp is superseded
for class-3 measurements by the record headers; §6 carries the
earlier-class consequence). Code state: branch `milestone-3`
(`b9fecd0..78f62a8`). Rule set: **3,513 rules** — 3,180 (the accepted
class-1+2 set) + 333 (the class-3 port). Rules core fingerprint
`00e05dca117aefd8df3d266652b11e93` (`test/mr_rules.core.stamp`, 3,513
rules, 2026-08-29 21:29:11 UTC — gitignored, rebuilt by
`test/build_rules_core.sh`; the ledger records the prefix
`00e05dca…`).

## 1. Rule set

From `Rubi.m`'s LoadRules list (T1 inventory): class 3 is **11 files,
333 rules, 332 with `/;` conditions** (census line 3) — the one
conditionless rule is 3.5's `Int[u_*Log[Gamma[v_]], x]`
(`3.5 Miscellaneous logarithms.m:47`). Per-file rule counts in
LoadRules order (3.1.1→3.1.2→3.1.3→3.1.4→3.1.5→**3.3→3.4**→3.2.1→
3.2.2→3.2.3→3.5 — 3.3/3.4 load BEFORE the 3.2.x, NOT numeric order;
the order is corroborated by the Task-7 census spot-checks: 3.1.1 r1
at table index 3,181 = 3,180+1, the FIRST class-3 slot, and 3.4 r1
at 3,369 = 3,180+188+1 where the 188 preceding class-3 rules are
exactly 3.1.1–3.1.5 + 3.3):

| file (LoadRules order) | rules |
|---|---:|
| 3.1.1 `(a+b log(c x^n))^p` | 6 |
| 3.1.2 `(d x)^m (a+b log(c x^n))^p` | 12 |
| 3.1.3 `(d+e x^r)^q (a+b log(c x^n))^p` | 21 |
| 3.1.4 `(f x)^m (d+e x^r)^q (a+b log(c x^n))^p` | 29 |
| 3.1.5 `u (a+b log(c x^n))^p` | 59 |
| 3.3 `u (a+b log(c (d+e x)^n))^p` | 61 |
| 3.4 `u (a+b log(c (d+e x^m)^n))^p` | 39 |
| 3.2.1 `(f+g x)^m (A+B log(e ((a+b x)/(c+d x))^n))^p` | 24 |
| 3.2.2 `(f+g x)^m (h+i x)^q (A+B log(e ((a+b x)/(c+d x))^n))^p` | 19 |
| 3.2.3 `u log(e (f (a+b x)^p (c+d x)^q)^r)^s` | 20 |
| 3.5 `Miscellaneous logarithms` | 43 |
| **total** | **333** |

(Verified against the generated files: 57+60+38 `defmatch` lines in
3_1_5/3_3/3_4 respectively plus the four head-position rules, which
emit structural rules without `defmatch` — 59/61/39 unique rule
names.) Re-classified against the milestone-1 generator's closed
table: **AUTO 241 (72.4 %) / MANUAL 92 (27.6 %)** (census `rule
classification` lines). Corpus: 9 of the 11 files have a suite file
(3.1.1 and 3.1.3 have none — expected, per recon); 3,085 entries
(3.1.2 193, 3.1.4 456, 3.1.5 249, 3.2.1 314, 3.2.2 263, 3.2.3 108,
3.3 547, 3.4 641, 3.5 314).

The **four `F_` head-position capture rules** (the Task-3 recon blind
spot: the census's token column listed first-rules-per-token and
showed only 3.1.5; the generic detection — a capture followed by `[`
in the lhs head position — emitted all four through the same
mechanism):

| rule | lhs shape | allow-list (cond `MemberQ[… , F]`) |
|---|---|---|
| 3.1.5 L62 | `Px*F_[d*(e+f*x)]^m*(a+b Log[c*x^n])` — linear arg, free `m` (`IGtQ[m,0]`) | asin/acos/asinh/acosh |
| 3.1.5 L63 | same, bare (no `^m`) | atan/acot/atanh/acoth |
| 3.3 L62 | `Px*F_[f*(g+h*x)]*(a+b Log[c*(d+e*x)^n])` — linear arg bare, lpow log arg | all eight |
| 3.4 L41 | `F_[f*x]^m*(a+b Log[c*(d+e*x^n)^p])` — monomial arg, free `m`, bpow log arg, NO Px slot | asin/acos/asinh/acosh |

They are emitted structurally by the generator's headvar path
(`%mr_headvar_match` + the slot-spec grammar; the `MemberQ` clause is
consumed and the allow-list is closed-set-checked). The allow-lists
use the **native bound spellings** asin/acos/atan/acot/asinh/acosh/
atanh/acoth — the Task-3 adjudication (all ten spellings re-probed on
the 2026-08-29 build): `arccot`/`arcoth` are unbound nouns with
D-noun diffs, so a noun head could never close the zero chain; new
table rows `ArcCot`→`acot`, `ArcCoth`→`acoth` (the
`%mr_` hyperbolic shims stay for class 1–2 answer-side byte-identity).
**Corpus exposure: 12 of 3,085 entries** — 3.1.5 e186-e197, all the
`(d+e x^2) F(a x)^m log(c x^n)` shape (m = 1: e186 asin, e187 acos,
e188 atan, e189 acot, e190 asinh, e191 acosh, e192 atanh, e193
acoth; m = 2: e194 asin^2, e195 acos^2, e196 asinh^2, e197
acosh^2) — `probes/corpus/05-class3-inverse-function-exposure`
(2026-08-30; the Task-3 smoke's "0 of 3,085" under-reported and is
superseded — the throwaway scan is gone, so its failure mode is not
pinned; probe 05 is the authoritative scan). Measured mechanism
(2026-08-30, milestone-3 core, `rubi_verbose` + direct
`%mr_headvar_match` calls; the entry set is probe 05's): **the
ported F_ rules (r58/r59) fire on NONE of the twelve** — the headvar
matcher declines the identity-default corner e:=0 of the linear
F-argument `a*x` (direct: the r58/r59 specs bind the non-zero-e
control `2*(3+4*x)` and decline `a*x`), the recorded safe-direction
divergence (Task-3 finding 2: the matcher is STRICTER than MA on the
d:=1 / e:=0 / c:=1 / Px:=1 corners — a decline, never a false
positive). The m=1 rows are answered anyway, by the 3.5 catch-all
**`3_5_r43` on pass 3** (`rubi: rule _mr_rule_3_5_r43 fired`,
measured on all eight m=1 rows): its repl re-dispatches the factored
form, the F-only sub-integral (no log factor) 0-fires in every
family and falls to the native-integrate fall-through (the measured
answers carry the native `atan2(·,·)` / `li(·)` forms). Committed-
record outcomes: **verified 4** (e188/e189/e192/e193 — the
{atan,acot,atanh,acoth} rows: the zero chain closes the
log(1+a^2 x^2) / polylog(2,-a^2 x^2) residue) | **unverified 4**
(e186/e187/e190/e191 — the {asin,acos,asinh,acosh} rows: the
expected texts' atanh(sqrt(1+-a^2 x^2)) / (1+-a^2 x^2)^(3/2) terms
do not close against the native atan2/sqrt forms) | **deferred 4**
(e194-e197 — the m=2 rows 0-fire in all three passes: r58's free-m
slot is the F^2 home but the same e:=0 corner declines it, and r43's
pattern does not cover the F^2 shape). Baseline comparison:
unverified 9 + timeout 3 (e191/e196/e197) — the twelve add **+4
PASS**, all via r43, none via r58/r59. The 39 synthetic Layer A
checks (`test_class3_headvar`) remain the only committed gate on
r58/r59: none of the twelve hits binds d:=1, c:=1, Px:=1, or a
non-zero-e argument, so the finding-2 corner strictness is still
synthetic-gated. An optional-form capture (`F_.[`) is a loud
GenError at generation time (grep-verified zero `_.[` in the
eleven .m files; the fix-round caught a SILENT pass-through before
it could ship).

Unlisted-token resolution (the census's UNLISTIED list — 13/13 U
tokens, no others exist; adjudicated in Tasks 1–6, this table is what
made the generation loud-failure-free):

| token (rules/uses, side) | resolution |
|---|---|
| `PolyLog` (17/37, repl) | **1:1 RENAME** to native `polylog(` — the active corpus expected texts are natively spelled (2,793 occurrences over the 1,194 entries whose expected text carries `polylog(` — the whole-line grep is 1,195, the 1,195th, 3.1.5 e220, being integrand-only, `Unintegrable`-expected; `probes/corpus/03-class3-answer-heads.out`); the build's `diff(polylog(·,·),·)` AND `polylog(·,numeric)` are nouns (probed 2026-08-29) → no spurious self-diff closure. The 1,195-entry mass is the §5 polylog-ceiling input |
| `LogGamma` (1/2, repl) | **RESTRUCTURE** → `log(gamma(v))` — `loggamma` is an undifferentiable noun (`diff` stays `'diff(loggamma(x),x,1)`), while `diff(log(gamma(x)),x) = psi[0](x)` closes (probed) |
| `LogIntegral` (1/1, repl) | RENAME → `expintegral_li` (`diff` = `1/log(x)`, bound) |
| `Gamma` (1/1 repl + 1 pattern head) | **arity dispatch** in the generator — 1-arg → native `gamma`, 2-arg → `gamma_incomplete` (the existing class-2 row), other arity → loud GenError (the PolyQ precedent) |
| `Chi`/`Shi`/`Si`/`Ci`/`Li` (answer-side only — no class-3 rule emits them) | table RENAME rows for closure (inert for class 3) + Task-8 `HEAD_REWRITES` rows for the corpus expected texts (§2) |
| `InverseFunctionFreeQ` (13/17, cond), `MemberQ` (4/4, cond), `FalseQ` (3/3, cond), `ProductQ` (2/2, cond), `IntegralFreeQ` (1/1, cond), `RationalFunctionExponents` (1/1, cond), `DerivativeDivides` (2/2, repl), `SubstForFractionalPowerOfLinear` (1/1, repl) | **ported** `%mr_` utilities (Tasks 4–5; §7 item 2) |
| `F` (4/4, repl) | head-position pattern capture — the Task-3 mechanism, not a table token |

## 2. Answer-side normalization (two sides, one table)

- **Generator side** — the translation table emits the native Maxima
  head, so `rubi()` answers are idiomatic: `Gamma` → arity-dispatched
  (1-arg `gamma`, 2-arg `gamma_incomplete`), `LogGamma` →
  `log(gamma(·))`, `LogIntegral` → `expintegral_li`, `Chi`/`Shi`/
  `Si`/`Ci` → `expintegral_chi/shi/si/ci` (inert for class 3),
  `PolyLog` → `polylog` 1:1 (Task 2; the generated rule files carry
  45 `polylog(` occurrences = the 45 live source `PolyLog[` uses, 1:1,
  2 `log(gamma(` in 3_5, 1 `expintegral_li(` in 3_1_1 — Task-6
  statics).
- **Harness side** — `test/corpus_driver.py`'s `HEAD_REWRITES` applies
  the same table to *both* the candidate and the corpus expectation
  before the zero chain (integrand text + primary and secondary
  expected texts; the `els[2]` steps are display-only and never reach
  Maxima). The class-3 section's answer-head census
  (`probes/corpus/03-class3-answer-heads.out`) needed **seven rows** —
  the two class-2 rows plus five:
  - pre-existing: `GAMMA(` → `gamma_incomplete(` (census {2: 304} —
    all 2-arg), `Ei(` → `expintegral_ei(` (census {1: 220} — all
    1-arg);
  - class-3 (Task 8, `b916f69`): `Chi(` → `expintegral_chi(`, `Shi(`
    → `expintegral_shi(`, `Si(` → `expintegral_si(`, `Ci(` →
    `expintegral_ci(` (census {1: 8} each — all in 3.5), `Li(` →
    `expintegral_li(` (census {1: 22} — 3.1.2 6, 3.3 6, 3.4 6, 3.5 4).
    Same `(?<![A-Za-z0-9_])` atom-charset lookbehind; idempotent
    (native forms untouched). The measured identities the rows are
    justified by (`probes/answer-side/02-class3-answer-side-identities`
    — the committed re-runnable form, build-stamped 2026-08-30; plan
    §Task-2 "Native conventions probed"):
    d/dx `expintegral_shi(x)` = sinh(x)/x, d/dx
    `expintegral_chi(x)` = cosh(x)/x, d/dx `expintegral_si(x)` =
    sin(x)/x, d/dx `expintegral_ci(x)` = cos(x)/x, d/dx
    `expintegral_li(x)` = 1/log(x) — every residue closes to 0 within
    the harness zero chain; all five bound and float-evaluable; the
    short names `shi/chi/si/ci` are unbound nouns (the naming trap
    the lookbehind + the `expintegral_` prefix guard against).
  - **`li` is the bound native polylogarithm** (the Task-8 F1
    correction): lowercase `li[s](z)` is the documented, bound
    polylogarithm — `ev(li[2](0.5))` = 0.5822405264650125 measured —
    a distinct token (lowercase, subscript-arg form) from the
    uppercase `Li(` row, so no collision; the committed comment says
    exactly this.
  - **No `polylog(` row** — the polylog rename decision (Task 1,
    option D): the 1,195-entry polylog mass (whole-line grep; 1,194
    of them carry `polylog(` in the expected text — 3.1.5 e220's is
    integrand-only, `Unintegrable`-expected) is native-spelled in
    the ACTIVE entries (2,793 `polylog(` occurrences = whole-file
    count — none outside active entries), the package emits native
    `polylog(`, and the only Rubi-spelled `PolyLog` surface is the 10
    commented-out bracket-notation lines (75 occurrences, all 2-arg;
    span 3.1.5/3.3/3.4/3.5 = 3/3/3/1) that `extract_entries` never
    reads. The measured noun properties (Task 1/Task 2 probes,
    2026-08-29 build): `diff(polylog(2,x),x)` stays a noun and
    `polylog(2,0.5)` / `polylog(3,0.5)` stay nouns — so a polylog
    entry can PASS only through the **two-sided expected chain on a
    form-identical answer** (identical polylog terms cancel before
    the diff: `diff(polylog(2,-x) - polylog(2,-x), x) = 0` measured);
    the self-diff/numeric stages cannot close. The §5 ceiling
    decision carries the consequence.
  Measured totals (aggregated over the 29 shard .out files — the
  merger drops per-shard stats lines, M2 precedent; Task-10 report
  §4): `gamma_incomplete(` 304 + `expintegral_ei(` 220 +
  `expintegral_li(` 22 + `expintegral_{si,ci,chi,shi}(` 8 each =
  **578 firings** — exactly the census counts. The 8+8+8+8 all fired
  in shard27 (3.5 e129–e256). `test/test_head_rewrites.py`: 20/0 (7
  pre-existing + 13 new, negatives included: `Sin(` guards the `Si(`
  row, `LogGamma(` guards the `GAMMA(` row, `Li2(`/`MySi(`/`XChi(`
  longer names intact, already-native outputs untouched).
- **Class-1/class-2 no-op proof** (Task 8; the constraint-1 basis —
  the accepted records were measured on the 2026-08-20 build): the
  51-entry class-1 slice (17+17+17 over files of 1,917/3,189/159 —
  the plan's "17+17+16 = 50" expectation undercounted the third
  file, measured) → `head rewrites: {}`; **51/51 (rel, entry) →
  verdict identical to `test/corpus_class1.out`** (the slice's 3
  timeouts are the record's standing timeouts). The 51-entry
  class-2 slice (17+17+17 over 98/93/774) → `head rewrites:
  {'gamma_incomplete(': 1, 'expintegral_ei(': 8}` — only the two
  pre-existing rows, NO `expintegral_{shi,chi,si,ci,li}` key —
  **51/51 identical to `test/corpus_class2.out`**. Zero diffs both
  classes, both slices run on the 2026-08-29 build + the 3,513-rule
  core (`rules_core_state() = on`, fp `00e05dca…` == stamp — the
  reviewer verified); corroborated at text level by a pre-scan: zero
  lookbehind-guarded occurrences of the five new heads in all 40
  class-1 + 3 class-2 suite files. §6 states the role this proof
  plays under the rebuild.

## 3. Baseline (native `integrate`, T3 mechanics)

Task 9: `probes/corpus/probe-integrate-sample.py` (the section as 10th
positional), 3 per-file shards (sorted-index ranges (0,3)/(3,6)/(6,9)),
30 s per-entry cap; shard walls 1,223.7 / 310.4 / 3,559.6 s
concurrent (ledger Task 9). Merged record
`test/corpus_class3.baseline.out`, completeness asserted 3,085/3,085,
merged 2026-08-29 23:34 UTC.

| class | count | % | verdict |
|---|---|---|---|
| `verified` | 979 | 31.7 | PASS |
| `expected` | 65 | 2.1 | PASS |
| `no-answer` | 397 | 12.9 | PASS (probe reading: integrate fell to a noun) |
| `unverified` | 1288 | 41.8 | FAIL |
| `unexpected` | 177 | 5.7 | FAIL |
| `timeout` | 149 | 4.8 | FAIL |
| `error` | 30 | 1.0 | FAIL (subprocess death — below) |
| **total** | **3085** | | **Results: 1441 passed, 1644 failed** |

PASS total **1441/3085 (46.7 %)** — verified+expected 1,044 (33.8 %)
plus no-answer 397. The 30 `error` entries are fully triaged
(Task-9 review: all 30 re-fatal in isolation, zero escapes) — **18
fatal inside the `integrate()` call + 12 in the probe's UNGUARDED
e-side zero chain (`ze`)**; five distinct fatals: `expt: undefined:
0 to a negative exponent.` ×16 (6 integrate / 10 ze), `PQUOTIENT:
Quotient by a polynomial of higher degree (case 2a)` ×7 (5/2),
`PTPTQUOTIENT: Polynomial quotient is not exact` ×4 (integrate),
`Heap exhausted during garbage collection` ×3 (integrate, uncatchable
process death). Entry-specific hard-log integrands +
polylog/Unintegrable expectations — NOT one systemic defect; the
polylog-in-expected correlation (27/30) is a red herring for the 17
that die in `integrate` (the expected text is never evaluated
there). The Task-9 A/B prediction (the 12 `ze`-chain fatals
`error`→`unverified`, the 18 integrate-stage `error`→`error`) was
superseded by measurement: all 30 resolved — §4. Note the
yardstick's mechanics (probe: 4-stage symbolic zero-chain, no head
rewrites, noun-on-answer-expected = PASS `no-answer`) — the A/B
margin note in §4 carries it.

## 4. Package run (3,513 rules) and A/B

Task 10: the generalized launcher/driver/merger over the
`3 Logarithms/` section, 3,085/3,085 entries, 29 shards / 24
processes (first run for the section — the cost model fell back to
count-balancing, heavy files split into 128-entry chunks), wall 28
min 04 s; merged record `test/corpus_class3.out`, completeness
asserted 3,085/3,085, merged 2026-08-30 00:18 UTC. Pre-launch
`rules_core_state() = on` (fp `00e05dca…` matches the stamp). No
shard died; no shard was re-run.

| class | count | % | verdict |
|---|---|---|---|
| `verified` | 1367 | 44.3 | PASS |
| `expected` | 66 | 2.1 | PASS |
| `no-answer` | 303 | 9.8 | PASS |
| `deferred` | 1033 | 33.5 | FAIL (top-level 0-firing → `unintegrable` noun) |
| `unverified` | 158 | 5.1 | FAIL (answered, zero chain did not close) |
| `timeout` | 117 | 3.8 | FAIL |
| `unexpected` | 22 | 0.7 | FAIL (corpus expected a noun; package answered) |
| `contains-noun` | 13 | 0.4 | FAIL (answer carries the `unintegrable` residue) |
| `error` | 6 | 0.2 | FAIL (subprocess death — death census below) |
| **total** | **3085** | | **Results: 1736 passed, 1349 failed** |

PASS total **1736/3085 (56.3 %)**.

**Per-class A/B** (PASS = {expected, verified, no-answer}; computed
from the two records' entry lines — Task-10 report §5.1,
reviewer-recomputed with zero mismatches):

| class | baseline | package |
|---|---:|---:|
| verified | 979 | 1367 |
| expected | 65 | 66 |
| no-answer | 397 | 303 |
| **PASS** | **1441** | **1736** |
| deferred | 0 | 1033 |
| unverified | 1288 | 158 |
| timeout | 149 | 117 |
| unexpected | 177 | 22 |
| contains-noun | 0 | 13 |
| error | 30 | 6 |
| **FAIL** | **1644** | **1349** |
| **total** | **3085** | **3085** |

**Per-file A/B** (Task-10 report §5.2):

| corpus file | entries | baseline PASS/total (pct) | package PASS/total (pct) | delta (count, points) |
|---|---:|---|---|---|
| 3.1.2 `(d x)^m (a+b log(c x^n))^p` | 193 | 105/193 (54.4 %) | 179/193 (92.7 %) | +74 (+38.3 pt) |
| 3.1.4 `(f x)^m (d+e x^r)^q (a+b log(c x^n))^p` | 456 | 215/456 (47.1 %) | 191/456 (41.9 %) | −24 (−5.3 pt) |
| 3.1.5 `u (a+b log(c x^n))^p` | 249 | 67/249 (26.9 %) | 113/249 (45.4 %) | +46 (+18.5 pt) |
| 3.2.1 `(f+g x)^m (A+B log(e ((a+b x)/(c+d x))^n))^p` | 314 | 176/314 (56.1 %) | 209/314 (66.6 %) | +33 (+10.5 pt) |
| 3.2.2 `(f+g x)^m (h+i x)^q (A+B log(e ((a+b x)/(c+d x))^n))^p` | 263 | 141/263 (53.6 %) | 125/263 (47.5 %) | −16 (−6.1 pt) |
| 3.2.3 `u log(e (f (a+b x)^p (c+d x)^q)^r)^s` | 108 | 57/108 (52.8 %) | 60/108 (55.6 %) | +3 (+2.8 pt) |
| 3.3 `u (a+b log(c (d+e x)^n))^p` | 547 | 212/547 (38.8 %) | 276/547 (50.5 %) | +64 (+11.7 pt) |
| 3.4 `u (a+b log(c (d+e x^m)^n))^p` | 641 | 310/641 (48.4 %) | 386/641 (60.2 %) | +76 (+11.9 pt) |
| 3.5 `Logarithm functions` | 314 | 158/314 (50.3 %) | 197/314 (62.7 %) | +39 (+12.4 pt) |
| **TOTAL** | **3085** | **1441/3085 (46.7 %)** | **1736/3085 (56.3 %)** | **+295 (+9.6 pt)** |

> ### AMENDMENT 2026-09-20 — the baseline column above is SUPERSEDED
>
> **The 1441/3085 (46.7 %) is inflated.** The native-`integrate` baseline
> probe scored an entry `no-answer` whenever `integrate` returned its own
> noun — including when the corpus expects a REAL ANSWER, i.e. when
> `integrate` had simply failed. `test/corpus_driver.py` splits that case
> out as `deferred` (FAIL) and has done since 2026-08-25; the split was
> never back-ported to `probes/corpus/probe-integrate-sample.py`, so every
> baseline was scored on a looser ruler than the package record it was
> compared against. Fixed 2026-09-20 (commit `f5ab334`).
>
> Re-measured under the fixed probe, build
> `branch_5_50_base_84_g4204fb669`, 30 s cpu cap, one shard per corpus
> file through a pool of 12 (`test/corpus_class3.baseline.out`, merged
> 3085/3085): the baseline's `no-answer` 397 splits into **147** honest
> noun-matches and **250** `deferred`.
>
> | | as recorded above | re-measured |
> |---|---:|---:|
> | baseline PASS | **1441 (46.7 %)** | **1190 (38.6 %)** |
>
> The entry-level A/B of the two baselines is 250 `no-answer -> deferred`
> plus 5 entries drifting into `timeout` (4 `unverified`, 1 `verified`);
> 0 FAIL->PASS. The drift is NOT the fix — the re-run used a wider pool
> (12 over 38 shards, against 3 shards in 2026-08-30), so a few near-cap
> entries were charged more cpu. Exactly one of them crossed the PASS
> boundary, which is why the measured 1190 is one below the 1191 predicted
> analytically.
>
> **Corrected per-file A/B** (baseline re-measured, package = today's
> committed `test/corpus_class3.out`, 1657/3085):
>
> | corpus file | N | baseline | package | delta |
> |---|---:|---|---|---|
> | 3.1.2 | 193 | 87 (45.1 %) | 193 (100.0 %) | +106 (+54.9 pt) |
> | 3.1.4 | 456 | 206 (45.2 %) | 260 (57.0 %) | +54 (+11.8 pt) |
> | 3.1.5 | 249 | 23 (9.2 %) | 56 (22.5 %) | +33 (+13.3 pt) |
> | 3.2.1 | 314 | 162 (51.6 %) | 219 (69.7 %) | +57 (+18.2 pt) |
> | 3.2.2 | 263 | 121 (46.0 %) | 177 (67.3 %) | +56 (+21.3 pt) |
> | 3.2.3 | 108 | 51 (47.2 %) | 38 (35.2 %) | −13 (−12.0 pt) |
> | 3.3 | 547 | 161 (29.4 %) | 255 (46.6 %) | +94 (+17.2 pt) |
> | 3.4 | 641 | 246 (38.4 %) | 303 (47.3 %) | +57 (+8.9 pt) |
> | 3.5 | 314 | 133 (42.4 %) | 156 (49.7 %) | +23 (+7.3 pt) |
> | **TOTAL** | **3085** | **1190 (38.6 %)** | **1657 (53.7 %)** | **+467 (+15.1 pt)** |
>
> Against the 1736 figure this document records, the corrected margin is
> **+546 (+17.7 pt)** rather than +295 (+9.6 pt).
>
> **The claim immediately below is WITHDRAWN.** Class 3 is not "the first
> RUNBOOK-PORTED class to beat the baseline", and M2 did not come out
> below its baseline: class 2's pilot record was **+137 (+14.2 pts)**
> ahead of its corrected baseline (see the amendment in
> `docs/corpus-class2-baseline-uplift.md` §3). Class 3's result stands on
> its own numbers — it is simply not the first.
>
> Evidence: `probes/corpus/13-baseline-noanswer-conflation` (a standing
> guard — now 0 over-credited entries for classes 2, 3 and 6); commits
> `f5ab334` (fix) and `1024f15` (re-runs).

Unlike M2 (where the package PASS total came out BELOW the baseline,
−9.6 pt at the pilot), class 3 is net **positive: +295 entries /
+9.6 points — the first RUNBOOK-PORTED class to beat the baseline**
(class 1, ported bespoke before the runbook existed, beat it by
+27.0 pt from its accepted record; class 2, the first runbook port,
came out −9.6 pt at the pilot and reached parity-and-a-fraction
only after the radcan-fallback harness fix), with gains in 7 of 9
files; the two declines (3.1.4 −24, 3.2.2 −16) are the
log-ratio-heavy files, matching the genuine-decline distribution
below.

**Entry-level transitions** (Task-10 report §5.3; both records carry
exactly the same 3,085 keys, 0 missing either way): **PASS→FAIL 525
= 343 genuine declines + 182 yardstick reclassifications;
FAIL→PASS 820.**

- The **343 genuine declines** (baseline `expected`/`verified` →
  package FAIL), class pairs: verified→deferred 313,
  expected→deferred 16, verified→unverified 9, verified→timeout 3,
  verified→contains-noun 2. The 329 `deferred` are the M2 pattern —
  the rules return a top-level `unintegrable` noun where native
  `integrate` had an answer; per file 3.1.4 128, 3.2.2 66, 3.4 39,
  3.5 36, 3.2.1 34, 3.3 18, 3.2.3 8. The 14 non-deferred:

  | entry | baseline | package |
  |---|---|---|
  | 3.1.4 e133, e140, e147 | verified | timeout — confirmed non-terminators at 100 s (re-check below) |
  | 3.2.3 e94; 3.3 e374 | verified | contains-noun (answer carries an `unintegrable` residue) |
  | 3.3 e77, e78, e280; 3.4 e508, e509, e510, e513, e514, e515 | verified | unverified (answered, zero chain did not close) |

  The 9 unverified are verification gaps, not known wrong answers;
  the 3 timeouts are confirmed genuine non-terminators at 100 s.
- The **182 yardstick reclassifications** (baseline `no-answer` —
  PASS under the probe — → package FAIL), class pairs:
  no-answer→deferred 150, →unverified 20, →unexpected 8, →timeout 4.
- The **820 FAIL→PASS**, class pairs: unverified→verified 580,
  unexpected→no-answer 163, unverified→expected 33, timeout→verified
  31, error→verified 11, timeout→no-answer 2. The 163
  unexpected→no-answer are corpus noun-expected entries where the
  package declined honestly and native `integrate` had answered (the
  inverse of M2's 10); the 31+2 timeout→… are entries the package
  finished inside 30 s that the native probe hit its cap on.

**The 30 baseline `error` entries** (Task-10 report §5.4 — the
Task-9-predicted split ~12 error→unverified + ~18 error→error did
NOT materialize): measured **19 error→deferred + 11 error→verified —
0 error→error, 0 error→unverified.** Every one resolved: the
package's rules path avoids the native-`integrate` fatalities
entirely. The 11 verified form clusters (3.1.4 e238–e240/e324–e325,
3.4 e133–e137, 3.5 e153) — native `integrate` fatalities the ported
rules now resolve. (The package run's 6 new errors are a disjoint set
of entries — the death census below; none of its 15 deaths lands on
those 30.)

**Margin note** (plan Task-10 header, quoted per the M2 record §4):
"the baseline record was produced by the probe (4-stage symbolic
zero-chain, no head rewrites, noun-on-answer-expected = PASS
`no-answer`), while the package run uses the driver (8-stage +
numeric chain, head rewrites, `deferred`/`contains-noun` FAIL
classes). Net: **the yardstick errs slightly conservative for the
package** (2 of 3 asymmetries flatter it). A stricter comparison =
re-run the native baseline through the driver harness."

**The 100 s timeout re-check** (standing protocol; the record's 117
`timeout` entries re-run exactly at a 100 s per-entry cap, same rules
core — launcher-confirmed fp `00e05dca…`; 24 shards, wall ~10 min 05
s, `test/corpus_class3.timeout-rerun/`, 117/117, watcher merge
2026-08-30 00:36 UTC):

- **now-PASS: 1** — 3.2.3 e60 → `no-answer` (t=33.5 s; the corpus
  expects a noun and the package returned one). No `verified`/
  `expected` transitions: **zero slow-correct answers** — none of the
  117 was merely slow.
- **still-timeout at 100 s: 96** — genuine non-terminators; by family
  3.3 44, 3.1.5 22, 3.1.4 12, 3.4 5, 3.2.1 5, 3.5 5, 3.2.3 3 (the
  merge.out list, 96 relpaths). This includes all three
  genuine-decline timeouts (3.1.4 e133/e140/e147, t=100.0–100.1 s
  each) — those declines are confirmed rule-complexity, not 30 s
  budget.
- **unverified: 9** — answered, chain did not close: 3.1.4 e71,
  3.1.5 e140, 3.2.1 e62/e71/e267, 3.3 e56/e63/e439/e532.
- **error: 9** — each re-run at the 100 s cap to capture the raw
  subprocess output: 3.1.5 e30, 3.2.1 e73/e75, 3.3 e151/e328/e534,
  3.5 e9/e169/e172. **All 9 are reproducible SBCL "Heap exhausted,
  game over" OOMs** — the 1 GiB dynamic space exhausts in the driver's
  zero-chain VERIFICATION stage (below), not the matching.
- **contains-noun: 1** — 3.3 e183 (t=43.0 s); **deferred: 1** — 3.3
  e300 (t=34.1 s).

**Death census (15 = 6 package run + 9 re-check; reviewer isolated
re-runs, Task-10 report §7/§12):** **13 heap-exhausted OOMs + 2
control-stack-exhausted.** The OOMs blow up in the driver's zero-
chain VERIFICATION stage: `rubi()` alone answers e233/e74/e30 (the
reviewer re-ran 3.3 e233 at 12.7 s, 3.2.1 e74 at 16.4 s, 3.1.5 e30
at 48.1 s — the package answers exist), while the 8-stage chain dies
at the 1 GiB cap, `bytes_allocated` 99.8 % — matcher-speed work must
not be misdirected at matching. The 30 s cap policy is unaffected —
this is memory, not budget. The 2 control-stack deaths: 3.2.3 e79
(matching stack overflow, reproduced at 2.1 s — the integrand
`log(e*((a+b*x)/(c+d*x))^n)/(f-g*x^2)`) and 3.3 e492 (the
reproducible package rule-generation bug, below). The **only
reproducible non-resource package bug** in either run is the e492
`%mr_algebraicFunctionQ` 3-arg mis-arity in exactly three generated
rules (3_1_5 r30, 3_3 r32/r61 — the generator carried Rubi's flag arg
`AlgebraicFunctionQ[AFx, x, True]` through the 1:1 rename into a
2-arg utility; 3_3 r61 fired on e492, r32/r30 not yet exercised by
the corpus) — ticketed, ready-for-agent, at
`.scratch/class3-algebraicfunctionq-arity/issues/01`.

## 5. Residues (input to the follow-up tickets)

FAIL masses by corpus file (package run; the full per-class
breakdown + sample entries + head census are the committed,
re-runnable probe `probes/corpus/04-class3-residue-answer-heads.out`
— run `sh probes/corpus/04-class3-residue-answer-heads.run`):

| file | n | unverified | deferred | timeout | other FAIL |
|---|---:|---:|---:|---:|---|
| 3.1.2 | 193 | 5 | 9 | 0 | — |
| 3.1.4 | 456 | 11 | 230 | 13 | unexpected 11 |
| 3.1.5 | 249 | 68 | 41 | 24 | unexpected 3 |
| 3.2.1 | 314 | 3 | 91 | 10 | error 1 |
| 3.2.2 | 263 | 0 | 138 | 0 | — |
| 3.2.3 | 108 | 1 | 36 | 4 | contains-noun 6, error 1 |
| 3.3 | 547 | 44 | 160 | 53 | unexpected 3, contains-noun 7, error 4 |
| 3.4 | 641 | 10 | 235 | 5 | unexpected 5 |
| 3.5 | 314 | 16 | 93 | 8 | — |
| **total** | **3085** | **158** | **1033** | **117** | **22 / 13 / 6** |

First ~5 entries of each mass per file (entry, run t from the T3
line — probe `== first 5 sample entries ==`):

- **unverified** — 3.1.2: e113 4.4 s, e170 3.5 s, e172 5.6 s, e173
  9.8 s, e174 6.0 s; 3.1.4: e35 13.4 s, e43 16.9 s, e50 20.4 s, e59
  24.5 s, e104 11.2 s; 3.1.5: e6 9.6 s, e14 3.5 s, e21 4.2 s, e25
  9.9 s, e26 11.5 s; 3.2.1: e235 19.1 s, e275 3.8 s, e305 3.8 s;
  3.2.3: e20 9.5 s; 3.3: e24 8.7 s, e25 8.4 s, e26 6.5 s, e27 4.4 s,
  e28 5.7 s; 3.4: e59 2.1 s, e265 4.4 s, e357 1.5 s, e508 1.9 s,
  e509 2.1 s; 3.5: e118 1.9 s, e119 1.4 s, e120 3.4 s, e123 2.8 s,
  e124 2.3 s.
- **deferred** — 3.1.2: e65 1.7 s, e66 1.5 s, e67 1.4 s, e162 4.9 s,
  e163 4.3 s; 3.1.4: e1 11.0 s, e2 9.5 s, e5 9.3 s, e6 10.0 s, e7
  9.8 s; 3.1.5: e1 5.9 s, e5 4.2 s, e13 5.7 s, e20 4.6 s, e47 8.3 s;
  3.2.1: e91 3.8 s, e93 5.2 s, e97 6.9 s, e98 7.0 s, e99 6.8 s;
  3.2.2: e1 12.5 s, e2 10.4 s, e3 5.3 s, e4 4.6 s, e5 8.1 s; 3.2.3:
  e1 6.6 s, e2 7.5 s, e4 6.3 s, e5 10.4 s, e6 7.0 s; 3.3: e88 1.0 s,
  e89 1.0 s, e90 1.1 s, e156 4.6 s, e175 9.1 s; 3.4: e50 6.5 s, e67
  16.6 s, e73 6.9 s, e100 11.7 s, e102 7.8 s; 3.5: e11 13.0 s, e13
  5.1 s, e19 7.2 s, e34 7.6 s, e40 6.5 s.
- **timeout** — 3.1.4: e71 30.0 s, e133 30.0 s, e134 30.1 s, e140
  30.0 s, e141 30.0 s; 3.1.5: e28 30.0 s, e30 30.0 s, e31 30.0 s,
  e32 30.0 s, e40 30.0 s; 3.2.1: e62 30.0 s, e71 30.0 s, e72 30.1 s,
  e73 30.2 s, e75 30.1 s; 3.2.3: e60 30.0 s, e77 30.1 s, e81 30.1 s,
  e85 30.0 s; 3.3: e56 30.0 s, e58 30.0 s, e59 30.0 s, e62 30.0 s,
  e63 30.0 s; 3.4: e263 30.1 s, e264 30.1 s, e399 30.0 s, e616 30.0
  s, e617 30.0 s; 3.5: e7 30.1 s, e8 30.0 s, e9 30.1 s, e15 30.0 s,
  e36 30.0 s.
- **unexpected** — 3.1.4: e127 1.4 s, e166 6.7 s, e167 6.9 s, e250
  4.2 s, e322 6.5 s; 3.1.5: e69 9.8 s, e138 2.5 s, e143 13.5 s; 3.3:
  e108 2.2 s, e114 2.0 s, e120 2.0 s; 3.4: e161 4.1 s, e162 5.1 s,
  e211 2.8 s, e217 2.5 s, e218 3.3 s.
- **contains-noun** — 3.2.3: e3 7.1 s, e67 11.8 s, e68 12.0 s, e71
  11.1 s, e92 5.7 s; 3.3: e184 28.5 s, e185 22.8 s, e186 17.4 s,
  e187 7.7 s, e188 9.7 s.
- **error** — 3.2.1: e74 29.2 s; 3.2.3: e79 3.2 s; 3.3: e233 12.8 s,
  e327 8.7 s, e492 3.2 s, e494 21.5 s.

Likely-cause classification (grounded in the ledger decisions and the
probe's censuses; "likely" marks a guess — no per-entry traces were
performed for any of these families, the M2 precedent):

- **deferred 1,033 — rule coverage, with the ported-semantics
  declines inside it.** The deferred entries are top-level 0-firings:
  no ported rule matches (or every match is rejected by a cond), so
  `rubi()` returns the `unintegrable[f, x]` noun on an answer-
  expected entry.
  - **532 (51.5 %) carry `polylog(` in the expected text** (1,091
    occurrences — the probe's deferred census; matches the Task-10
    §8 mass split exactly). The 17 PolyLog-emitting rules do not
    reach these integrands; full Rubi reaches many through
    substitutions and normalization rules of other classes (a
    count-level inference — the class-1 1.2.1 `b`-suffixed / M2 2.3
    precedent). Likely cause: rule coverage.
  - **The remainder concentrates in the two log-ratio-heavy
    declines**: the genuine-decline distribution is 3.1.4 128 /
    3.2.2 66 — the files with 29 and 19 rules respectively (likely
    cause: rule coverage, as above).
  - **Ported-semantics declines** (safe directions, each a recorded
    ledger decision — "likely" attributions to specific entries):
    the **LogGamma restructure** (3.5 r42: the generated repl is
    `(log(gamma(v)) - log(gamma(v)))*mr_int(u,x) + mr_int(u*log(
    gamma(v)),x)` — the two terms Rubi keeps distinct
    (`LogGamma[v]` ≠ `Log[Gamma[v]]` in MA) are identical in Maxima,
    so the reduction collapses to a bounded self-recursion of the
    same integrand and declines under the runner's seen/depth
    guards — a likely contributor to the 3.5 deferred 93);
    **negative-power storage** (every negative power stores as a `/`
    node in this build, so the .m's Power-head tests are unreachable
    for negative fractional powers and `%mr_fractionalPowerQ`
    declines them — the Task-5 Sqrt-head decision on the Task-4
    minus-lift precedent); the **rat-mode factored slope**
    (`%mr_substForFractionalPowerOfLinear`'s v slot is the factored
    form in EVERY call context — the measured Task-5 rat-mode
    quirk; the reviewer adjudicated no correctness risk, only
    form-sensitive `mr_int` sub-integral coverage — a likely
    contributor to 3.5); `%mr_productQ` declining minus-lifted
    storage (the Task-4 decision; only 3.5 r32/r38 could notice).
    The **`F_` strictness corners** (Task-3 finding 2) contribute
    only the four m=2 deferred entries (e194-e197, §1): the
    corpus's twelve in-domain hits all sit at the e:=0 corner —
    answered by the 3.5 catch-all r43 on the m=1 rows, 0-firing on
    the m=2 rows — so no entry is lost to any corner OTHER than
    e:=0, and the e:=0 decline IS the recorded strictness.
  - The 3 `AlgebraicFunctionQ`-flag rules (3_1_5 r30, 3_3 r32/r61)
    FATAL rather than decline (3.3 e492 — the §4 death census);
    post-fix they are `Unintegrable`-answering fallbacks, so the fix
    can only convert `error` → a non-error class, never a verified
    answer (the ticket's exposure analysis).
- **unverified 158 — the zero chain does not close on the answer's
  special-function heads.** Residue census (the probe, this task):
  `polylog(` 354, `%e^` 72, `erfi(` 26, `GAMMA(` {2: 24},
  `hypergeometric(` 1, over the 158 expected texts. The
  **polylog-expected 106** are the noun-diff mechanism (§2): an
  answer not form-identical to the expected cannot close the
  self-diff chain — the structural-ceiling family, and the shim
  ticket's input (below). The **erfi/GAMMA/hypergeometric-expected
  remainder** is the M2 class-2 §5 precedent: the ratsimp/factor
  zero chain cannot close symbolic `gamma_incomplete`/`expintegral_*`/
  `erfi`/`hypergeometric` differences unless the answer is in the
  exact antiderivative form (the structural-ceiling family).
- **timeout 117 — 96 confirmed non-terminators at 100 s** (rule
  complexity — the §4 by-family counts, 3.3 44 / 3.1.5 22 leading;
  includes the 3.1.4 e133/e140/e147 genuine-decline cluster) **+ 21
  resolved below 100 s** (1 now-PASS, 9 unverified, 9 error — the
  OOM census, 1 contains-noun, 1 deferred). The 30 s cap STAYS the
  standard (standing policy); the 96 are not a budget question.
- **unexpected 22** — rubi returned an answer where the corpus
  expects a noun (the driver's class definition,
  `test/corpus_driver.py:24`). The corpus-limitation shape —
  improvements the 2018 corpus cannot accept (the M2 unexpected 4 +
  the class-1 ticket-03 precedent). No renamable head occurs in
  their expected texts (the probe's unexpected census is empty —
  `Unintegrable`-expected only).
- **contains-noun 13** — the answer carries the `unintegrable`
  catch-all residue: faithful Rubi `CannotIntegrate` markers and
  cascade coverage gaps (the class-1 uplift profile); 36 `polylog(`
  in their expected texts (the probe).
- **error 6** — the §4 death census: 4 OOM + 3.2.3 e79 matching
  control-stack overflow + 3.3 e492 the ticketed arity bug. All 6
  sit in the polylog mass (Task-10 §8).

**Residue → expected-head census** (the probe `04-class3-residue-
answer-heads.out`, this task — the 1,349 FAIL entries joined to the
suite files' expected texts; re-runnable). **Polylog-dominated**, as
predicted by the M2 deferral:

| head | occurrences (1,349 FAIL entries) |
|---|---:|
| `polylog(` | 1,782 |
| `%e^` | 468 |
| `GAMMA(` {2: 245} | 245 |
| `erfi(` | 57 |
| `Ei(` {1: 77} | 77 |
| `Chi(`/`Shi(`/`Si(`/`Ci(` {1: 8} each | 8 each |
| `Li(` {1: 6} | 6 |
| `erf(` | 1 |
| `hypergeometric(` | 4 |

Per FAIL class (the probe's per-class sections): deferred 1,091
`polylog(` / 221 `GAMMA(` / 77 `Ei(` / 31 `erfi(` / the 8+8+8+8
Chi-Shi-Si-Ci / 6 `Li(`; unverified 354 `polylog(` / 24 `GAMMA(` / 26
`erfi(`; timeout 282 `polylog(`; contains-noun 36; error 19.

### The polylog structural-ceiling decision (the M2-deferred decision,
now with class-3 numbers)

The polylog mass is **1,195 of 3,085 entries (38.7 %) / 2,793
occurrences** (per file: 3.1.4 187, 3.1.5 179, 3.2.1 91, 3.2.2 106,
3.2.3 65, 3.3 243, 3.4 237, 3.5 87; 3.1.2 0 — Task-1 grep, verified
by the Task-10 report §8 per-file re-grep) against the **17
PolyLog-emitting rules** (census: 17 rules / 37 uses). The measured
mechanism (2026-08-29 build, §2): `diff(polylog(·,·),·)` and
`polylog(·,numeric)` are nouns, so a polylog entry can PASS only
through the two-sided expected chain on a form-identical answer; the
self-diff/numeric stages cannot close.

The measured split of the 1,195 (Task-10 report §8): **PASS 440
(36.8 %: verified 379, expected 59, no-answer 2) | deferred 532
(44.5 %), unverified 106, timeout 103, contains-noun 8, error 6** —
vs the record-wide PASS 56.3 %. The **unverified+deferred polylog
mass is 638 — 53.4 % of the mass and 47.3 % of the class-3 FAIL mass
of 1,349**.

**Decision: the ceiling does NOT stand as-is.** That mass is
material, it is exactly where the M2 deferral said the polylog mass
would land ("class 3 is where polylog mass lands"), and it is not a
verification gap a stronger chain can close — the noun diff/numeric
property is structural, so no zero-chain fix reaches an entry whose
answer is not form-identical to the expected. It is a
derivative-simplification gap. A `polylog(2,·)` derivative shim (its
derivative `d/dz polylog(2,z) = -log(1-z)/z` is elementary) with the
higher-order recursion `d/dz polylog(s,z) = polylog(s-1,z)/z` would
let the self-diff stage close the verified/unverified split.
**Follow-up ticket:
`.scratch/class3-polylog-ceiling/issues/01-polylog-derivative-shim.md`
(research + possible port, needs-triage) with 638 as its go
number.** Open questions for triage, recorded in the ticket: WHERE a
shim lives in the harness (the driver's zero chain vs a Maxima-level
`diff` simplification); the interaction with the OOM mass (all 6
package-run errors + 8 of the 9 re-check OOMs sit in the polylog
families — the verification-stage blowup is worst where polylog
verification is attempted) and with the still-timeout concentrations
(3.3 44, 3.1.5 22). The AppellF1 half of the M2 deferral: 0
`AppellF1` in the class-3 rule files and 0 in the section's expected
texts (grep, 2026-08-30; it appears only as a `string(op)` guard
spelling in the ported `%mr_inverseFunctionFreeQ`) — that half
remains deferred, superseded as the measured mass by the polylog
number.

## 6. Earlier-class status — the accepted records stand

**The class-1 accepted record (20,069/25,697 = 78.1 %; `test/
corpus_class1.out` — the post-pilot re-measurement under the
radcan-fallback chain, `docs/corpus-class2-baseline-uplift.md` §8.2)
and the class-2 accepted record (594/965 = 61.6 %; `test/
corpus_class2.out`, §8.1) are untouched and stand.**

Per the runbook (standing constraint 1: byte-identity gate for
accepted classes), no full re-run was in the class-3 scope — the
shared-code changes are gated against the accepted records:

- **No commit on the branch touches `rules/class1/` or
  `rules/class2/`** — `git log b9fecd0..HEAD --name-only -- rules/
  class1 rules/class2` is empty; the earlier-class rule files are
  byte-identical across the whole branch.
- **Byte-identity gates green** (final gates below): `--class 1` →
  `TOTAL: 3026 rules — OK`, `--class 2` → `TOTAL: 125 rules — OK`,
  `git status --porcelain rules/` EMPTY after both regenerations.
- **The 2026-08-29 REBUILD.** The accepted records were measured on
  the 2026-08-20 21:36:22 build (their headers); the installed Maxima
  was rebuilt 2026-08-29 17:58:20 from the same source revision
  (`branch_5_50_base_84_g4204fb669`) before the class-3 work began
  (ledger plan header). A full re-measurement of the 25,697 + 965
  entries was not in the class-3 scope; the Task-8 **no-op slices are
  the earlier-class re-measurement evidence under the rebuild**: 51/
  51 class-1 + 51/51 class-2 (rel, entry) → verdict identical to the
  accepted records, run on the NEW build with the 3,513-rule core
  (`rules_core_state() = on`, fp `00e05dca…` == stamp — the reviewer
  verified), `head rewrites: {}` / only the two pre-existing rows
  firing, zero diffs both classes. The class-2 record §8 is the
  model of what a re-measurement section looks like; here the no-op
  proof plays that role — it pins VERDICTS (not just rule-file
  bytes) on the new build + grown core, which is the property the
  accepted records claim. The record headers remain the authoritative
  build stamps for each record's own numbers.

## 7. Ledger flags — shared-code changes and their no-regression
evidence

Every shared-code change the branch made, with the commit and the
no-regression evidence that gated it (full detail: the ledger's
Tasks 1–10 entries; `b9fecd0..78f62a8`):

1. **Generator — class-3 translation rows** (the 14 RENAME rows:
   the five `expintegral_*` answer natives, `PolyLog`→`polylog` 1:1,
   the eight `%mr_` port names; the `LogGamma` RESTRUCTURE row; the
   Gamma RENAME comment; `_emit_gamma` arity dispatch 1-arg →
   `gamma` / 2-arg → `gamma_incomplete` / other → loud GenError; the
   LogGamma emitter case). Commit `0f92fd7`. No-regression:
   loud failures reproduced 14/14 by the reviewer (naming
   file/rule/token, exit 1); class 1 has ZERO Gamma occurrences,
   class 2 5/5 two-arg taking the byte-identical 2-arg branch —
   the committed class-2 output holds exactly 5 `gamma_incomplete(`
   and no bare `gamma(`; the byte-identity gate (item 6) green.
2. **Generator — head-position capture (the `F_` rules) +
   `EXPECTED_TOTAL` 3:333.** Detection (capture followed by `[` in
   the lhs head position), `HEADVAR_HEADS`, the closed-set regexes,
   `headvar_spec`, `_emit_headvar_manual`, the `emit_head`
   `apply(F,[arg])` intercept. Commit `e54988d` (+ the fix-round
   loud GenError for the optional form `F_.[`, which was a SILENT
   generation-time pass-through, `28c665f`). No-regression: the
   byte-identity gate green (regeneration byte-identical, empty git
   status); class 3 → 333 OK, re-run byte-identical; the loud-
   failure path RUN through the real pipeline on synthetic rules
   (missing `MemberQ` / out-of-closed-set F-arg / wrong-variable
   `MemberQ` → exit 1); parse sweep 11/11 clean (fresh TLS process
   per file); Layer A 620/0 (581 + 39 `test_class3_headvar` checks).
3. **Generator — Part handler generalization (call-then-Part
   `expr[[i]]` → `part(<translated prefix>, <i>)`).** Commit
   `fd9d261` (scheduled by the Task-4 review, plan `8aed663`).
   No-regression: subsumes the bare-name sites byte-identically
   (class-2 `uu[[1]]`/`uu[[2]]`, class-3 `lst[[1..4]]`); the only
   LIVE call-then-Part in any class was 3.4 r1 — now FIRES
   end-to-end on the witness `log(x/(x+1))/(x+1)` to
   `polylog(2, 1 - x/(x+1))` (C = 1 x-free, measured) with a live
   negative control; the regeneration changed exactly ONE line
   (3_4.mac:14); the byte-identity gate green both classes.
4. **Utils — the class-3 port family** (pure addition,
   `maxima_rubi_utils.mac`): the headvar family (`%mr_headvar_match`
   + 12 `%mr_hv_*` sub-helpers, +353, commit `e54988d`); cluster A —
   six cond-side predicates (`%mr_memberQ`, `%mr_falseQ`,
   `%mr_productQ`, `%mr_integralFreeQ`, `%mr_inverseFunctionFreeQ`,
   `%mr_rationalFunctionExponents`, +191, commit `8783c0b`);
   cluster B — the Subst family (`%mr_easyDQ`,
   `%mr_derivativeDivides`, `%mr_fractionalPowerOfLinear`,
   `%mr_substForFractionalPower`,
   `%mr_substForFractionalPowerOfLinear` + helpers, +547, commit
   `56417c6`; the header-bullet correction `a3bd850` comment-only).
   Each predicate carries a pinned-clone `.m`-cited block comment +
   measured-quirk stamps (the Task-4/5 measured quirks: the
   memberQ argument-order reversal, the `booleanp` noun, the
   minus-lift `/` storage, the freeof product-noun opacity, the
   rat-mode factored-slope quirk, the `sqrt`-head symbol op).
   No-regression: TDD RED→GREEN at every cluster (Layer A 620/0 →
   691/0 → 743/0, re-verified by the reviewers); no class-1/2 rule
   file regenerated (item 6's gate); the class-1/2 no-op slices
   (§2/§6) run on the grown utils with zero verdict drift.
5. **Driver — five class-3 `HEAD_REWRITES` rows + the comment
   correction; the class-3 fingerprint glob** (`_core_fingerprint()`
   gains `rules/class3/*.mac`, same 4 top files, same C-locale sort).
   Commits `b916f69` / `4753bb7` / `9c58ae0`. No-regression: the
   head-rewrite unit 20/0; the no-op slices 51/51 × 2 (§2); the
   recomputed driver fp == the stamp fp
   `00e05dca117aefd8df3d266652b11e93` (the driver's stale-refusal
   gate accepts the core).
6. **Loader + rules core + TLS probe.** The class-3 block in
   `mr_load_all` (purely additive, pinned LoadRules order), the
   `build_rules_core.sh` FP-list mirror, the 3,513-rule core rebuild
   (stamp 2026-08-29 21:29:11 UTC, gitignored deliverable), the
   full-load TLS probe. Commit `9c58ae0`. No-regression:
   `TABLE_AT_LOAD 3513` with 0 error/exhausted/Thread-local lines
   (`probes/load_wall/probe-class3-load.out`, 5,313 lines); the
   census spot-checks (1/x → log(x) via `_mr_rule_1_1_1_1_r1` idx 1
   — class-1 undisturbed; log(x) → `x*log(x)-x` via
   `_mr_rule_3_1_1_r1` idx 3,181 = the FIRST class-3 slot; 3.4 r1
   via `_mr_rule_3_4_r1` idx 3,369 — corroborating both the
   composition 3,180+333 and the 3.3/3.4-before-3.2.x order, which
   under numeric order would be 3,432); the class-1/class-2 loader
   blocks + rule files byte-untouched (git diff stat empty).
7. **`.gitignore` — re-check-record re-inclusion for any cap name
   + the class-N merge logs.** Commit `d86a099` (the Task-10
   reviewer finding: the blanket ignore hid the 100 s record
   name; the negation verified precise against the run-dir shard
   names). No-regression: the re-check record + merge.out are
   committed artifacts, force-free from now on.
8. **Layer A growth** (the suite, not a rule change): 581 → 620
   (headvar, Task 3) → 691 (cluster A, Task 4) → 743 (cluster B,
   Task 5) → 743 at close (the final gate below) — 743/0 at every
   post-task stage, re-verified by the reviewers.

## 8. Final gates (run 2026-08-30, all green)

1. **Layer A** — `maxima --very-quiet -b test_maxima_rubi.mac`:
   `Results: 743 passed, 0 failed`.
2. **Byte-identity (every accepted class)** — `python3
   generator/generate_rules.py --class 1` → `TOTAL: 3026 rules — OK
   (== 3026)`; `python3 generator/generate_rules.py --class 2` →
   `TOTAL: 125 rules — OK (== 125)`; then `git status --porcelain
   rules/` → EMPTY (the regeneration left the tree byte-identical).
3. **Head-rewrite unit** — `python3 test/test_head_rewrites.py`:
   `Results: 20 passed, 0 failed`.
