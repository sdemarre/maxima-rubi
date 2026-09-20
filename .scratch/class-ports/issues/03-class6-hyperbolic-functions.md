# Class 6 (hyperbolic functions) port — 5,080 entries

Status: ready (Step 1 complete 2026-09-20)
Type: task (port, runbook-driven)
Filed: 2026-08-30 (milestone-3 close; the M2 TODO's class-6 item, now
against the instantiated runbook)

## Scope

Port the "6 Hyperbolic functions" section (section name VERIFIED
against `reference/maxima-syntax-test-suite/6 Hyperbolic
functions/` — 26 `.mac` files under subdirs 6.1 Sine … 6.7
Miscellaneous) and its rule files
(`reference/rubi/Rubi/IntegrationRules/6 Hyperbolic functions/`)
per `docs/class-porting.md` Steps 1–10. The milestone-3
instantiation (`docs/corpus-class3-baseline-uplift.md`) is the
template; its standing constraints bind (byte-identity gate for
every accepted class, 30 s per-entry cap, 100 s timeout re-check,
A/B vs the `integrate` baseline, acceptance record per the
class-2/class-3 template, TLS probe on the core rebuild).

## Recon numbers (measured 2026-08-30 — PRE-CENSUS; the runbook
Step-1 census probe is the first act of the port and supersedes
these)

- **Corpus: 5,080 entries** — counted over the section's 26 `.mac`
  files (lines starting with `[`); matches the M2 TODO's figure.
- Rule files: 13 `.m` files; 13 `Rubi.m` LoadRules entries (all
  loaded, as in class 3's 11/11).
- Rule count: **390 `Int[... ] :=` lines** across the 13 `.m` files
  (recon count of rule-shaped lines; the Step-1 census probe is the
  authoritative count).

## Known interactions

- The hyperbolic heads (`sinh`/`cosh`/`tanh`/`coth`/`sech`/`csch`)
  are native in Maxima; the class-3 Task-3 note that the `%mr_`
  hyperbolic shims (`%mr_asinh`/`%mr_acosh`/`%mr_atanh`) exist for
  class 1–2 answer-side byte-identity — the Step-1 census decides
  whether class 6 reuses them or tables natives.
- Rule count per corpus entry is the thinnest of the queue
  (390/5,080 ≈ 0.077 vs class 3's 333/3,085 ≈ 0.108) — expect a
  larger `deferred` mass than class 3; the runbook's A/B
  genuine/yardstick triage (M2 178/131 worked-example method)
  applies unchanged.
- Queue position: third (8 → 5 → 6 → 7 → 4).

## Acceptance

Per the runbook: merged records complete (5,080/5,080), A/B
triaged with nothing unexplained, re-check read, acceptance record
committed, the byte-identity gates for classes 1–3 (and 8/5 if
accepted earlier) green, Layer A green.

## Comments

### 2026-09-20 — Step 1 (census) COMPLETE; status needs-triage -> ready

Build `branch_5_50_base_84_g4204fb669` (2026-08-31 13:27:47), SBCL 2.6.7.

**Probes committed (re-runnable):**

- `probes/translation/05-class6-syntax-census.{run,out}` — Step 1(a).
- `probes/corpus/12-class6-answer-heads.{py,run,out}` — Step 1(b). First
  answer-head probe to WALK SUBDIRECTORIES (section 6 nests one level;
  the class-2/3 probes' flat glob would have found 0 files) and the first
  with a DISCOVERY pass, since class 6's head set was not known in advance.
- `probes/answer-side/03-class6-answer-side-identities.{py,run,out}` — the
  evidence for the "no new rewrite row" claim below.

**Counts — the recon numbers are CONFIRMED, not superseded:** 13 rule
files / 390 rules / 5,080 entries over 26 `.mac` files, exactly the
2026-08-30 recon. All 390 rules carry a `/;` condition.

**AUTO/MANUAL: 103 (26.4%) / 287 (73.6%).** Class 2 was 80/125 = 64% AUTO.
Class 6 is markedly more MANUAL-heavy; the driver is the optional-capture
depth (the histogram peaks at 6 optional names, 89 rules, and reaches 13).

**Answer side: ZERO new `HEAD_REWRITES` rows needed.** The discovery pass
finds ten non-native call heads on the 5,080 entry lines; every one is
already disposed of:

| head | uses | disposition |
|---|---|---|
| `Chi(` 611, `Shi(` 605, `Si(` 32, `Ci(` 32 | 1,280 | existing class-3 rows |
| `GAMMA(` 266 (all 2-arg), `Ei(` 6 | 272 | existing class-2 rows |
| `Unintegrable(` 364, `CannotIntegrate(` 47 | 411 | corpus markers, read at `corpus_driver.py:655` before normalization |
| `AppellF1(` 24 (6-arg) | 24 | no native — the class-3 structural ceiling, unchanged |
| `F(` 8 (5-arg) | 8 | FREE function symbol (the class-2 `F0(` reading); its entries' answers are `CannotIntegrate(...)` |

The 26 native heads carry the mass (`sqrt(` 14,432, `sinh(` 9,101,
`cosh(` 7,660, `tanh(` 4,556, `polylog(` 2,848, …) and probe 03 measures
the six hyperbolic ones as differentiable through the harness's OWN
`zero_chain` (all six residuals close) and float-evaluable at 0.7.

**Token closure — all 18 UNLISTIED tokens adjudicated:**

*A. Hyperbolic head RENAMEs — 4 tokens, 285 rule-uses. Step 2, mechanical.*
`Cosh` 172, `Csch` 41, `Sech` 38, `Coth` 34 -> the natives `cosh`/`csch`/
`sech`/`coth`. (`Sinh`/`Tanh` already have rows.) Natives measured bound,
differentiable and float-evaluable: probe 03 H1-H6 / E1-E6.

*B. Special-function head RENAMEs — 2 tokens, 2 rule-uses. Step 2, mechanical.*
`CoshIntegral` 1 -> `expintegral_chi`, `SinhIntegral` 1 -> `expintegral_shi`.
Class 6 is the first section to emit these from a REPLACEMENT (class 3 met
them answer-side only), so probe 03 R1-R4 re-measures the derivatives
`cosh(z)/z` / `sinh(z)/z` on the rule side. Both close.

*C. Head pattern variables — 3 tokens, 18 rule-uses. NOT ports; a matcher
question. THE ONE GENUINE UNKNOWN.* `F` 9, `G` 8, `H` 1 are pattern
variables in HEAD position (`F_[c_. + d_.*x_]^n_.`). Head-position capture
already exists and is tested — `test_maxima_rubi.mac:602`
`test_class3_headvar()`, over class-3 `3_1_5` r58/r59, `3_3` r58, `3_4`
r37, including head-list membership. **What is new in class 6 is TWO and
THREE head variables in one pattern**: `F_[a+b x]^p_.*G_[c+d x]^q_.`
(6.7.6) and `F_^(c(a+b x))*G_[d+e x]^m_.*H_[d+e x]^n_.` (6.7.7). No
class-1-3 rule binds more than one. Resolve at Step 3 before generating
6.7.6/6.7.7; if the matcher declines, those ~18 rules are the deferral
candidate, not the class.

*D. Predicates to port — 4 tokens, 20 rule-uses. Step 4.* `HyperbolicQ` 11
(head-set membership over a Group-C bound head — port the two together),
`IndependentQ` 6, `QuotientOfLinearsQ` 2, `MemberQ` 1 (translation-table
row exists; verify it covers the `MemberQ[{Sinh, Cosh}, F]` head-list form).

*E. Support functions to port — 4 tokens, 33 rule-uses. Step 4.*
`ExpandTrigReduce` 26 (product-to-sum; the substantial one, and the only
Step-4 item likely to need its own cluster), `ExpandTrigToExp` 4,
`QuotientOfLinearsParts` 2, `ExpandTrigExpand` 1.

*F. Inert marker — 1 token, 8 rule-uses. Step 2.* `Integral` 8, Rubi's
inert integral head; sibling of `Unintegrable`, which already has a row.

**Read:** the real porting surface is D+E — **8 functions, 53 rule-uses**.
A+B+F are 7 mechanical table rows against natives already measured. The
schedule risk is concentrated in C (one matcher capability, 18 rules) and
in `ExpandTrigReduce` (26 rules).

**Not yet done (Step 1 has no opinion on these):** the 6.7.x manual bucket
is the fat one — `6.7.9 Active hyperbolic functions` alone is 71 rules /
20 distinct token-sets.

### 2026-09-20 — Steps 2-6 complete; the table-growth probe

Steps 2 (table), 3 (generate), 4 (utils, 3 clusters), 5 (statics),
6 (loader + core) are committed on branch `class6-port`. Core rebuilt:
**rules=3903 = 3,513 + 390**, fingerprint `d624cefbd491c0a111ed481442042e40`.
Layer A 1010 -> **1066/0**; P3 static **15/0** (check 7 added);
byte-identity green for classes 1-3 throughout.

**TABLE-GROWTH PROBE (directional, NOT the gate).** The standing worry
before this port was that the dispatcher is a bare `dolist` over every
handle, so a bigger table taxes every FAILED dispatch and every nested
sub-integral — and class 1 already loses 13.0 % of its entries to the
cap. Class 6 is the smallest available test of that: +390 rules, +11 %.

Measured 2026-09-20, build `branch_5_50_base_84_g4204fb669`, cpu cap 30 s,
80 class-1 entries (2 per file x 40 files) run with class 6 LOADED,
compared entry-for-entry against the committed `test/corpus_class1.out`
(2026-09-18, 24-worker queue, same cap kind):

| | |
|---|---|
| common entries | 80 |
| PASS | 64 -> **64** |
| class transitions | **NONE — identical verdict on every entry** |
| PASS->FAIL | 0 |
| cpu over the common entries | 451.5 s -> 426.4 s (**0.94x**) |

So a +11 % table cost nothing measurable here, and the 7 entries that
time out did so in both records.

**Read it as weak-but-real evidence, not an all-clear.** 80 of 25,697 is
a 0.3 % sample, biased to the first two entries of each file, and the
failure mode at issue is entries sitting just under the cap crossing it
— exactly what a small sample of mostly-fast entries cannot see. The
0.94x is also inside the +-13 % noise band the 2026-09-19 probe measured
for this dispatch path, so it is "no detectable cost", not "a speedup".
The gate remains a full 25,697-entry A/B via `test/ab_records.py`, which
belongs to Step 9.
