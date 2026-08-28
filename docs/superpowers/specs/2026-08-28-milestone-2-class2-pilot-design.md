# Milestone-2 pilot — design: classes 2+ as a repeatable process, proven on class 2

Date: 2026-08-28. Working branch: `milestone-2` (off `master` @ `55724a6`,
the "Merge branch 'milestone-1'" commit of 2026-08-28 00:12:53 +0200,
parents `6754be9` + `edd2aa1`), worktree `.worktrees/milestone-2`
(`reference/` symlinked to the main checkout's pinned clones, the
milestone-1-worktree precedent). Measurements stamped
Maxima 5.50.0 (build date 2026-08-20 21:36:22) / SBCL 2.6.7 — the
installed build; `build_info()` per the AGENTS.md discipline.

## 0. Context

Milestone 1 (foundation + the algebraic-function class) is closed and
merged: 3,055 rules (the 67-file class-1 port + five 1.2.1
`b`-suffixed corpus-tested siblings + `9_1.mac`'s 29 rules), corpus
acceptance
19,731/25,697 (76.8 %) vs the T3 `integrate` baseline of 49.8 %, Layer A
511/0. The research design
(`docs/superpowers/specs/2026-08-17-maxima-rubi-research-design.md`)
mandates that "extending to a second function class must then be a
documented, deliberate step." The 2026-08-27 close handoff lists the
step as open item #2 — "Classes 2+ as a repeatable process: the
generator + the loader's LoadRules list are the seam: a new class is a
new pinned-file set + generator run + loader list + corpus section."

This design is that documented step, scoped as a **process-first
pilot**: generalize the pipeline and prove it end-to-end on class 2
(exponentials — the smallest class-2+ corpus), so that classes 3–8
become runbook tickets rather than projects. (User decision
2026-08-28.)

## 1. Scope

**In**:

1. Pipeline generalization (generator, census, driver, loader, core).
2. Class 2 (exponentials) ported end-to-end: 3 rule files, 125 rules.
3. Class-2 yardstick: T3-style `integrate` baseline + package run +
   full A/B, merged record committed.
4. The runbook: the repeatable process written down with measured
   per-step costs, so classes 3–8 are tickets.
5. Close-out housekeeping: AGENTS.md test section, TODO index,
   milestone-2 handoff (the milestone-1 close pattern).

**Out** (separate, tracked): classes 3–8 themselves (runbook tickets,
section 6); ticket 04 (matcher backtracking); ticket 05 (harness
fixes); the section-9.3 port; ticket 02 (mailing-list repro). The
polylog derivative shim is a **go/no-go from the pilot's measured
unverified mass** (section 3.4), not upfront scope.

## 2. Measured basis

All measurements below were taken 2026-08-28 on the installed build
(5.50.0 / 2026-08-20 21:36:22 / SBCL 2.6.7). Those that the pilot
promotes to committed probes are marked **(probe)** — the plan makes
them re-runnable before any doc claim depends on them; the rest are
cited as session measurements superseded by the probe.

### 2.1 The class-2 rule set

From `Rubi.m`'s LoadRules list (parsed with the T1 inventory's
`parse_load_rules`): class 2 is **3 files, 125 rules** —
`2.1 (c+d x)^m (a+b (F^(g (e+f x)))^n)^p`,
`2.2 (c+d x)^m (F^(g (e+f x)))^n (a+b (F^(g (e+f x)))^n)^p`,
`2.3 Miscellaneous exponentials` (the T1 count of 125 confirmed).
Rule-file numbering does NOT align with the corpus-file numbering
(corpus 2.1 is `u (F^(c (a+b x)))^n`) — the two trees are numbered
independently, as the class-1 1.2.1.4 case already showed.

Re-classified with the T4 census parser against the milestone-1
generator's closed table: **80 AUTO / 45 MANUAL**. New tokens (absent
from the class-1 table, with call counts):

| token | calls | kind |
|---|---|---|
| `TrueQ` | 9 | predicate (trivial: `is(…)=true`) |
| `PowerOfLinearQ` | 6 | predicate — is `u = (a+b x)^m`? |
| `Exponent` | 7 (5 cond + 2 repl) | function — degree of `x` in a polynomial |
| `PowerOfLinearMatchQ` | 3 | predicate (match variant) |
| `NormalizePowerOfLinear` | 6 | support function |
| `FunctionOfExponentialQ` | 1 | predicate |
| `FunctionExpand` | 1 | support (Mathematica builtin) |
| `FunctionOfExponential` / `FunctionOfExponentialFunction` | 1 / 1 | support |
| `NormalizeIntegrand` | 1 | support |
| `PowerQ` | 2 | predicate |

Answer-side head renames (Rubi name → Maxima native, all measured
working in the installed build — section 2.3): `Gamma`→
`gamma_incomplete` (5), `ExpIntegralEi`→`expintegral_ei` (3),
`Erf`→`erf` (3), `Erfi`→`erfi` (1), `Exp`→`exp` (2). No class-2 rule
emits `polylog` (zero replacement-token occurrences) — the corpus's
polylog expectations are verification-side only.

**(probe)** the generalized census (section 3.2) with its `.run`/`.out`
under `probes/translation/`.

### 2.2 The class-2 corpus

`reference/maxima-syntax-test-suite/2 Exponentials/` — 3 files,
**965 entries** (measured: per-file entry-line count; the driver's
existing entry parser applies). Expected-answer function census
(distinct-head occurrences, entry lines): `Ei` 237, `GAMMA` 191,
`polylog` 200, `erfi` 175, `atan` 47, `Unintegrable` 68,
`CannotIntegrate` 38, `atanh` 37, `F0` 14, `hypergeometric` 10,
`erf` 10. Full-run cost: 965 × ~3.5 s serial-eq (class-1-measured
mean) ≈ 56 min serial; each file (~320 entries ≈ 18 min) exceeds the
per-process target, so the M1 cost-aware planner chunk-splits them
(the skip/cap mechanics, the 1.1.1.2/1.1.1.3 precedent) into ~24
jobs → ≈ 5–10 min wall.

### 2.3 Answer-side support in the installed build

The zero chain verifies by `diff`; an answer-side head verifies iff the
build's `diff` (and, for the numeric stage, `float`) handles it.
Measured 2026-08-28, head by head:

| Maxima name | diff | float | corpus head it serves |
|---|---|---|---|
| `expintegral_ei(z)` | `%e^z/z` ✓ | 1.8951… (z=1) ✓ | `Ei` |
| `expintegral_e1(z)` | `-%e^-z/z` ✓ | 0.2194… ✓ | `E1` |
| `expintegral_e(n, z)` | `-expintegral_e(n-1, z)` ✓ | 0.1485… (2,1) ✓ | `E` |
| `expintegral_li(z)` | `1/log(z)` ✓ | ✓ | `Li` |
| `expintegral_si(z)` | `sin(z)/z` ✓ | ✓ | `Si` |
| `expintegral_shi(z)` | `sinh(z)/z` ✓ | ✓ | `Shi` |
| `expintegral_ci(z)` | `cos(z)/z` ✓ | ✓ | `Ci` |
| `expintegral_chi(z)` | `cosh(z)/z` ✓ | ✓ | `Chi` |
| `gamma_incomplete(a, z)` | `-z^(a-1) e^-z` (a=0 and symbolic a) ✓ | 0.9513… (2, .35) ✓ | `GAMMA` (upper) |
| `lambert_w(z)` | `%e^-w/(1+w)` ✓ | 0.5671… (1) ✓ | `ProductLog` |
| `fresnel_c(z)` / `fresnel_s(z)` | `cos(πz²/2)` / `sin(πz²/2)` ✓ | ✓ | `FresnelC` / `FresnelS` |
| `erf` / `erfi` / `erfc` | `erfi`/`erfc` re-measured 2026-08-28; `erf` M1-era | ✓ | `Erf` / `Erfi` / `Erfc` |
| `hypergeometric` | ✓ (M1) | ✓ | `hypergeometric` |

**Missing from the build entirely** (no exact manual topic):
`polylog`, `AppellF1`, `F0` (the class-2 corpus's `F0` head needs its
spelling identified by the pilot's census; treat as no-native until
shown otherwise). These are the structural-only ceiling: entries whose
only verification route is a `diff` of such a head close only via
structural (canonical-form) match in the `expected` class, else
`unverified` — the same ceiling class 1 already lives with for
`AppellF1` (commit `9c87a3f` emits the corpus head there).

**Naming trap (measured, the day's main finding):** the public names
carry the underscore — `expintegral_ei`, `lambert_w`,
`gamma_incomplete`, `fresnel_c` — while the *internal* op names are
`$%EXPINTEGRAL_EI`, `$%LAMBERT_W`, … (the op-cell of
`lambert_w(x)` prints head `$%LAMBERT_W`). The `%expintegral_ei` and
`lambertw` spellings are NOT public names and read as unbound nouns —
the first probe round of the day (on those spellings) wrongly
concluded the build lacked the functions. `describe(name, exact)` in
the running build is the arbiter; the defgrad registrations in the
source (`~/src/external/maxima`, `src/expintegral.lisp`,
`src/gamma.lisp`, `src/specfn.lisp`) target the internal names and are
correct. **(probe)** a committed answer-side matrix probe
(`probes/answer-side/`) re-running the table above with a stamp,
so any build change re-measures it in one shot.

## 3. Design

### 3.1 Generator generalization + the byte-identity gate

`generator/generate_class1.py` becomes class-parameterized (class
directory name, output directory, file set replayed from `Rubi.m`'s
LoadRules list — the existing `load_class1_files` mechanism generalized).
Class-1-specific workarounds (CAP_REMAP, SLOT_KEYS_PHASE1, the 1_1_1_7
exclusion and its re-inclusion note, the 1.4.1 show-steps parser
artifact strip) become a **class-1 override table** inside the one
generator. `translation_table.py`'s RENAME/RESTRUCTURE tables gain the
section-2.1 entries.

**Gate before any class-2 emission**: the generalized generator must
regenerate all 67 class-1 files **byte-identical** (`git diff` clean on
`rules/class1/`). Any drift is a process bug, fixed before proceeding —
the accepted class-1 record (`test/corpus_class1.out`) and its core
fingerprint `f1f0611f…` must remain reproducible from the new code.

### 3.2 Census probe generalization

The T4 census (`probes/translation/01-class1-syntax-census.*`) becomes
class-parameterized; the class-2 run is committed as
`probes/translation/02-class2-syntax-census.{py,run,out}` with the
usual date + `build_info()` stamp. Its output is the authoritative
token table for the generator/ports (the section-2.1 numbers are its
first reading).

### 3.3 Utils ports

The section-2.1 predicate/support list, ported into
`maxima_rubi_utils.mac` as `%mr_`-prefixed functions (house rule 7 —
never the native name), each with a unit probe in
`test_maxima_rubi.mac` written before the port (the T4 unit-probe
discipline). `Exponent` is checked against the existing
`coeff`/`degree` walkers (the Task-5 monic-term fixes) before any new
code is written.

### 3.4 Head normalization

Two sides, one table:

- **Generator side** — the translation table emits the Maxima-native
  head (`ExpIntegralEi`→`expintegral_ei`, `Gamma`→`gamma_incomplete`,
  `Erf`→`erf`, `Erfi`→`erfi`, `Exp`→`exp`, …), so `rubi()` answers are
  idiomatic Maxima.
- **Harness side** — the zero chain applies the same table to *both*
  the candidate and the corpus expectation before the diff, in
  `corpus_class2_driver.py`'s `build_text` (generalized from
  `corpus_class1_driver.py`, section 3.6). The rewrite is head-
  specific and idempotent (native forms are untouched), so it cannot
  touch integrand-side free symbols; it also protects the
  AppellF1-style case where the package emits a corpus head.

Full table (class-2 needs the first five rows; the rest are the
runbook's standing rows for classes 3–8, measured section 2.3):
`Ei→expintegral_ei`, `E1→expintegral_e1`, `E(n,z)→expintegral_e(n,z)`
(two-argument form only — bare `E` is the integrand's exponential
base), `GAMMA(a,z)→gamma_incomplete(a,z)`, `ProductLog→lambert_w`,
`FresnelC→fresnel_c`, `FresnelS→fresnel_s`, `Chi→expintegral_chi`,
`Shi→expintegral_shi`, `Si→expintegral_si`, `Ci→expintegral_ci`,
`Erf→erf`, `Erfi→erfi`, `Erfc→erfc`. Not renamed: `polylog`,
`AppellF1`, `F0` (no native; structural-only ceiling).

**Residue policy**: the pilot's merged record reports the
`unverified` mass split by answer-side head. If `polylog`-carrying
entries form a material unverified block, a `polylog(2,·)` derivative
shim (its derivative `-log(1-u)/u` is elementary) becomes a follow-up
ticket with that number as its go; otherwise the structural ceiling
stands.

### 3.5 Loader + rules core

`maxima_rubi.mac`'s load list gains the class-2 files **in Rubi.m
LoadRules order** (load order = rule priority; Rubi.m loads class 2
after all of class 1). The generator's printed ordered load list is
the paste source, as in class 1. `test/build_rules_core.sh` gains the
class-2 files; the rebuilt core gets a new fingerprint — the
driver's stale-core guard makes a forgotten rebuild a loud failure,
not a silent 0-rule run. Rule-load processes keep
`-X "--tls-limit 100000"` (125 new rules ≈ trivial against the 1200-
slot cap, but the load-wall probe is re-run per the load_wall
discipline — the probe self-flags if the build moves).

### 3.6 Yardstick

- **Baseline**: the class-2 `integrate` run, the T3
  probe-integrate-sample mechanics (the class-1 baseline precedent),
  965 entries, 30 s cap, merged record
  `test/corpus_class2.baseline.out`.
- **Package run**: the class-1 driver generalized with the section
  (corpus directory) and record name as parameters — one
  parameterized driver, the class-1 launcher/record untouched; the
  class-2 run is a launcher instance over the
  `2 Exponentials/` section. Cost-aware sharding carries over, with
  chunk-splitting per section 2.2 (~24 jobs).
- **A/B**: full-run A/B against the baseline, the regression gate
  (AGENTS.md); every PASS→FAIL remainder triaged to a ticket or a
  recorded explanation, the milestone-1 discipline. The class-1
  record is **not** re-run for the pilot (no build change, no
  class-1 rule change — the byte-identity gate covers that); it is
  re-run at milestone-2 close if any shared code (utils, runner,
  zero chain) changes in a way that touches class-1 behavior —
  flagged per-change in the ledger.

### 3.7 Runbook + close

`docs/class-porting.md` (new): the repeatable process, one section
per step (census → table extension → predicate ports + probes →
generate → loader list → core rebuild → baseline → run → A/B →
record), each with the class-2 measured cost and the class-specific
decision points (new-token triage, matchfix traps, normalization
table rows, corpus-spelling checks). The 2026-08-28 handoff pattern
repeats at close: `handoff/2026-08-2x-milestone-2-*.md`, AGENTS.md
test section updated (Layer A target count, the class-2 run
commands), TODO index gains the milestone-2 entry.

## 4. Acceptance (pilot done-when)

1. Layer A green: `Results: <n> passed, 0 failed` with n = 511 + the
   new class-2 targets (per-change gate, AGENTS.md).
2. **Byte-identity gate**: generalized generator reproduces
   `rules/class1/` byte-identical (clean `git diff`).
3. Class-2 generation: 125/125 rules, zero unlisted tokens (the
   generator's loud-failure gate holds).
4. Class-2 corpus: 965/965 entries run, completeness asserted at
   merge, record committed.
5. A/B vs the class-2 baseline: no unexplained regressions (each
   remainder ticketed or explained in the record).
6. Runbook + records + close housekeeping committed.
7. Uplift (package % vs baseline %) **reported** in the record — it is
   a measurement of the pilot, not a target.

## 5. Risks and open measurements (made early in the plan)

- **Matchfix binding quirks**: class-2 optional-capture patterns
  (`F_^(g_.*(e_.+f_.*x_))^n_.`) may hit the variable-name-order
  binding trap the 1.1.1.4 CAP_REMAP workarounds exist for. The
  first Layer-A behavioral targets (one per rule-file family, the
  M1 pattern) are the tripwire; the generator's CAP_REMAP machinery
  generalizes to a per-class table.
- **`Exponent` port**: measured against the existing degree walkers
  before writing (section 3.3) — the Task-5 monic-term bug history
  says "reuse, don't rewrite."
- **Load cost**: 125 rules re-measured on the load-wall curve
  (section 3.5); expected trivial, must be measured.
- **`F0` corpus head**: spelling/meaning unidentified (section 2.3);
  the pilot's census resolves it or tickets it.
- **Zero-chain interaction**: the normalization table rewrites
  expectations carrying `%i`-bearing trig-form expint answers (the
  `expintrep` identities are complex-valued); if a class-2 expectation
  normalizes to a form the chain cannot close that the raw form
  could, the record's unverified triage will show it — the table is
  per-head and individually reversible, so a bad row is removable
  without touching the rest.

## 6. Follow-ups (post-pilot, in the runbook's ticket form)

- **Classes 3–8**, one ticket each, ordered by the pilot's measured
  per-class cost: 3 logarithms (333 rules / 3,085 entries), 8 special
  functions (310 / 1,949 — shares class 2's head table), 5 inverse
  trig (665 / 4,585), 6 hyperbolic (390 / 5,080), 7 inverse
  hyperbolic (710 / 6,552), 4 trig (2,073 / 22,472 — the largest, the
  inert-trig machinery, deliberately last). (Rule counts T1; entry
  counts measured 2026-08-28.)
- `polylog(2,·)` derivative shim — go/no-go from the pilot's
  unverified mass (section 3.4).
- The standing post-milestone-1 tickets (04, 05, 02, 9.3) are
  unaffected and keep their own trackers.
