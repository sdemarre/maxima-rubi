# Class 8 (special functions) port — 1,949 entries

Status: ready
Type: task (port, runbook-driven)
Filed: 2026-08-30 (milestone-3 close; the M2 TODO's class-8 item, now
against the instantiated runbook)

## Scope

Port the "8 Special functions" section (section name VERIFIED against
`reference/maxima-syntax-test-suite/8 Special functions/` — 10 `.mac`
files) and its rule files
(`reference/rubi/Rubi/IntegrationRules/8 Special functions/`) per
`docs/class-porting.md` Steps 1–10. The milestone-3 instantiation
(`docs/corpus-class3-baseline-uplift.md`, plan
`docs/superpowers/plans/2026-08-29-milestone-3-class3.md`) is the
template; its standing constraints bind (byte-identity gate for every
accepted class, 30 s per-entry cap, 100 s timeout re-check, A/B vs
the `integrate` baseline, acceptance record per the class-2/class-3
template, TLS probe on the core rebuild).

## Recon numbers (measured 2026-08-30 — PRE-CENSUS; the runbook
Step-1 census probe is the first act of the port and supersedes
these)

- **Corpus: 1,949 entries** — counted over the section's 10 `.mac`
  files (lines starting with `[`); matches the M2 TODO's figure.
- Rule files: 10 `.m` files; 10 `Rubi.m` LoadRules entries (all ten
  loaded, as in class 3's 11/11).
- Rule count: **310 `Int[... ] :=` lines** across the 10 `.m` files
  (recon count of rule-shaped lines; the Step-1 census probe is the
  authoritative count).
- Section files: 8.1 Error functions, 8.2 Fresnel integral
  functions, 8.3 Exponential integral functions, 8.4 Trig integral
  functions, 8.5 Hyperbolic integral functions, 8.6 Gamma functions,
  8.7 Zeta function, 8.8 Polylogarithm function, 8.9 Product
  logarithm function, 8.10 Formal derivatives.

## Known interactions

- **Shares class 2's head table** (M2 TODO): the existing
  `GAMMA(` → `gamma_incomplete(` and `Ei(` → `expintegral_ei(`
  `HEAD_REWRITES` rows cover 8.3/8.6 expected texts; the section's
  other special-function heads (`erf(`/`erfi(`/`lambert_w(`, 8.1/8.9)
  are already native-lowercase in the corpus — the Step-1 answer-head
  census decides whether any row is needed.
- **8.8 Polylogarithm function** is the natural home of the polylog
  mass the class-3 ceiling decision
  (`.scratch/class3-polylog-ceiling/issues/01`) targets — the
  derivative-shim ticket's where-does-it-live question
  (driver zero-chain vs Maxima-level `diff` simplification) should be
  resolved before this port's Step 8 (normalization) so 8.8 runs on
  the final harness.
- 8.10 Formal derivatives is a small odd file — census it; expect
  little corpus value (the M2 TODO listed this class first in the
  queue at 1,949 entries — the second-smallest section).

## Acceptance

Per the runbook: merged records complete (1,949/1,949), A/B
triaged with nothing unexplained, re-check read, acceptance record
committed, the byte-identity gates for classes 1–3 (and 4–7 if
accepted earlier) green, Layer A green.

## Comments

2026-09-22 — **9.1 Derivative integration rules (21) now belong to this
port** (user decision, section-9 spec
`docs/superpowers/specs/2026-09-22-section9-port-design.md` §0.3.3). The
evidence: its only corpus is `8 Special functions/8.10 Formal
derivatives.mac` (94 entries, `probes/rubi/04-section9-load-and-legacy.out`
§E); `Rubi.m` loads it at L354, after class 8 and inside the
`$LoadElementaryFunctionRules` block; and it needs a Maxima
representation of `Derivative[n][f][x]` (the corpus writes
`Derivative(1)(f)(x)`), which is a design question, so this port starts
with a brainstorm. Its census tokens outside the table: `Derivative`, `F`
(`probes/translation/07-section9-syntax-census.out`).

### 2026-09-25 — Step 1 (census) COMPLETE; status needs-triage -> ready

Build `branch_5_50_base_84_g4204fb669` (2026-08-31 13:27:47), SBCL 2.6.7.
Branch `class-ports` (worktree `mr-ports`), based on `section9-port` @ `cd0a421`.

**Probes committed (re-runnable):**

- `probes/translation/09-class8-syntax-census.{run,out}` — Step 1(a): the
  01 census over the loaded "8 " files, then
  `probes/translation/09-class8-table-closure.py`, the closure against
  `generator/translation_table.py` over those files **plus 9.1 Derivative**.
- `probes/corpus/15-class8-answer-heads.{run,out}` — Step 1(b) (reuses the
  class-6 script with the section as its argument).
- `probes/answer-side/04-class8-answer-side-identities.{py,run,out}` — the
  native heads through the harness's own zero chain, and the Derivative
  representation measurements (the design section below).

**A census defect, fixed first.** `Rubi.m` L352 is a COMMENTED-OUT
`LoadRules` for "8.10 Bessel functions" — the only commented `LoadRules` in
the pinned `Rubi.m`. The 01 census parsed `Rubi.m` raw and counted it (10
files / 310 rules — the recon's figure); it now comment-strips first. The six
earlier census records (classes 1/2/3/4/6, section 9) re-run byte-identical
after the fix (dates aside). The generator's `load_class_files` has the same
raw parse and gets the same fix at Step 2 (the byte-identity gate proves it a
no-op for the accepted classes).

**Counts.** 9 loaded files / **307 rules** (8.1 69, 8.2 55, 8.3 26, 8.4 29,
8.5 29, 8.6 24, 8.7 5, 8.8 26, 8.9 44), all with a `/;` condition, **0**
`LoadShowSteps` lines — so `EXPECTED_TOTAL` is the census count. Plus 9.1
Derivative: **21 rules** (`probes/translation/07-section9-syntax-census.out`
and the closure probe agree). Port total **328**. AUTO 1 / MANUAL 306 by the
census's own tiers — meaningless here: nearly every "C-tier" token is a
special-function head the table maps 1:1 (see A). The corpus is **1,949**
entries over 10 files (8.10 Formal derivatives has 97 entries; the
section-9 spec's 94 counts only the entries that spell `Derivative(`).

**Token closure — all 13 UNLISTED tokens adjudicated** (the other 45 tokens
already have rows, `09-class8-syntax-census.out`):

*A. Native special-function heads — 8 tokens, Step 2 table rows.* `ProductLog`
44 rules -> `lambert_w`; `FresnelS`/`FresnelC` 28 each -> `fresnel_s`/
`fresnel_c`; `Erfc` 22 -> `erfc`; `SinIntegral`/`CosIntegral` 14 each ->
`expintegral_si`/`expintegral_ci`; `ExpIntegralE` 10 -> `expintegral_e`;
`HypergeometricPFQ` 16 -> `hypergeometric` (list arguments, as
`Hypergeometric2F1`). Every one differentiates through the zero chain and
float-evaluates (probe 04 A1-A13, E1-E9). mr-tree already carries all of
them (`maxima_rubi_tree.lisp` `+functions+`), so patterns need nothing new.

*B. `PolyGamma` — 10 rules, a SUBSCRIPTED emission.* `PolyGamma[n, z]` ->
`psi[n](z)` (mr-tree's `+subscripted+` already reads `psi[n](z)` as
`PolyGamma`). Maxima's `psi[n]` differentiates for every order the rules
emit, negative ones included (`psi[-2]` -> `psi[-1]`, probe A9); `psi[-2]`
does not float-evaluate (E8), so those answers verify symbolically only.

*C. `Zeta` — 5 rules, 2-argument (Hurwitz) only.* Maxima has no symbolic
Hurwitz zeta (`describe("hurwitz", inexact)` finds nothing; `zeta` is
1-argument). Decision: the **AppellF1 precedent** — emit the corpus's own
head `Zeta(s, z)` as an inert noun. Identical answers cancel in the zero
chain (probe N14's shape); its derivative stays a noun (A17), so a
different-form answer cannot verify. The 1-argument `Zeta` keeps the tree's
`zeta` mapping.

*D. `Block` — 1 rule (8.6 r9), `Block[{$UseGamma = True}, …]`.* A DYNAMIC
binding of the package global `mr_use_gamma_flag` (the `$UseGamma` row) —
must NOT get the With/Module local prefix (ticket 08), which would rename the
global away. Step 3 emitter case.

*E. `PolyQ` — 4 rules.* Not a real gap: emitter-dispatched since class 1
(the table comment above `LinearQ`); the probe lists it only because it has
no row.

*F. `Derivative` — 18 rules of 9.1 (plus the `f_'[x_]` prime spelling in
9.1 r19-r21).* The design question; decided below.

*G. Head variables.* `F` (6 uses, 8.1/8.2 `F_[f_.*(a_.+b_.*Log[…])]` with
`MemberQ[{Erf, …, CoshIntegral}, F]`) — the class-3/6 head-capture shape.
9.1 adds LOWERCASE head captures `f_[x_]`/`g_[x_]` that must bind the SAME
symbol that appears as a value in `Derivative[1][f_]` (the census regex only
sees capitalised tokens, so they are not counted above).

**Transitive closure through `IntegrationUtilityFunctions.m`.** All the
listed utility tokens are already ported; three have semantic gaps class 8
reaches, and are Step-4 work:

1. `FunctionOfQ` (12 rules: 11 in 9.1, 8.9's bare-`u_` catch-all): the port
   covers only circular-trig `v` ("deviation (a)") and answers `false` for
   anything else. Rubi's `_` branch is `FunctionOfExpnQ[u, v, x] =!= False`
   (L4443-4516) — every class-8 `v` (`ProductLog[x]`, `f[x]*g[x]`,
   `Derivative[n-1][f][x]`) takes it. Port `FunctionOfExpnQ`.
2. `SubstFor` (same rules): the port's final fallback is `subst(x, v, u)`,
   which misses powers of a product `v` (probe N17: `f(x)*g(x)` is not found
   in `f(x)^2*g(x)^2`). Rubi's fallback is `SubstForAux` (L6004), after the
   free-factor step. Port `SubstForAux`.
3. `CalculusQ` (called by `FunctionOfExpnQ`): the port counts any `diff`
   noun as calculus. In Maxima that noun IS the evaluated formal derivative
   (Mathematica's `Derivative[n][f][x]`, head `Derivative[n][f]`, which is
   not in `$CalculusFunctions`), so the formal-derivative shape must not be.

**Answer side (Step 7 input).** 22 non-native heads (probe 15):
`ProductLog(` 1695, `FresnelS(` 424, `FresnelC(` 418 (new rows -> natives);
`Ei(` 806 = **472 1-arg + 334 2-arg** and `GAMMA(` 708 = **690 2-arg + 18
1-arg** — the existing class-2 rows are arity-blind and would turn `Ei(n,z)`
into `expintegral_ei(n,z)` and `GAMMA(z)` into `gamma_incomplete(z)`, so both
become arity-aware (2-arg `Ei` -> `expintegral_e`, 1-arg `GAMMA` -> `gamma`;
measured no-op for the accepted sections: classes 2/3/6 carry only 1-arg `Ei`
and 2-arg `GAMMA`, class 1 neither); `Psi(n,z)` 77 -> `psi[n](z)`;
`lnGAMMA(` 22 -> `log_gamma(`; `HypergeometricPFQ(` 137 -> `hypergeometric(`;
`Factorial(` 2 -> `factorial(`; `Derivative(` 320 — the structural rewrite
below. Not rewritten: `Si/Ci/Shi/Chi/Li` (existing rows), `Zeta(` 28 (C
above), `Unintegrable(`/`CannotIntegrate(` (markers), `f(`/`g(`/`F(` (free
function symbols), `int(` 1 (a single entry's inert integral).

### 2026-09-25 — DESIGN: the Maxima representation of `Derivative[n][f][u]`

Decided by measurement (probe 04 D1-D3, N1-N17), not asked: the ticket
directed that the call be made and recorded.

**The candidates.** (1) Keep the corpus spelling `Derivative(n)(f)(u)`.
(2) Maxima's own derivative noun `'diff(f(u), u, n)`. (3) A package function
`%mr_deriv(n, f, u)` with a `gradef`.

**(1) is out.** It parses to nested `mqapply` over an undefined `Derivative`
(D1/D2), and `diff` knows nothing about it: d/dx `Derivative(1)(f)(x)` does
not close against `Derivative(2)(f)(x)` (D3 = 0). Every answer the 9.1 rules
produce would be unverifiable.

**(3) is out.** A `gradef`'d package head verifies its own terms, but an
answer like `f(x)*g(x)` differentiates (natively) to `'diff(f(x),x,1)`, not
to `%mr_deriv(1, f, x)`; two spellings of one object would need a global
translation between them at every diff.

**(2) is chosen: `Derivative[n][f][u]` IS `'diff(f(u), u, n)`, with order 0
meaning `f(u)`.** It is what Maxima itself returns for the derivative of an
undeclared function (N3), so the answer side and the integrand side agree
without any help, and it closes the zero chain for every order the corpus
uses: 1 -> 2 (N4), symbolic `m` -> `m+1` (N5), `-1+m` -> `m` (N6), and the
NEGATIVE orders the formal-antiderivative entries use (N7 `-1` -> `f(x)`,
N8 `-3` -> `-2`): `diff()` itself refuses order -1 (N11) but the noun is
holdable (N10) and `diff` of it increments the order. Order 0 comes back as
`f(x)` (N9). The numeric first stage declines on the noun (N15), so these
entries verify on the symbolic stages. A composite argument has a spelling
too — Maxima's own `subst` produces `'diff(F(f(x)*g(x)), f(x)*g(x), 1)` (N12)
— so `SubstFor`/`Subst` round trips need no special case, and `subst` of the
noun by a symbol works (N16).

**The pieces.**
- `%mr_derivative(n, f, u)` (utils): order 0 -> `f(u)`, else the noun,
  built with `funmake` so nothing evaluates. The generator emits it for a
  curried `Derivative[a][b][c]` in a replacement or condition.
- The driver rewrites the corpus spelling `Derivative(A)(B)(C)` to
  `%mr_derivative(A, B, C)` (a balanced-parenthesis STRUCTURAL rewrite, not a
  regex row; nested derivatives inside `C` included), on the integrand and
  the expected texts, so both are the native noun after evaluation.
- mr-tree reads the noun `'diff(f(u), u, n)` (exactly three arguments, the
  first a one-argument call whose argument is the differentiation variable)
  as the curried tree `(((Derivative n) f) u)` — the shape Rubi's pattern
  `Derivative[n_][f_][x_]` has — and writes it back. The matcher already
  matches compound heads.
- mr-tree names a user-function head by the function's own name (`f(x)` ->
  `(f x)`), not the opaque `MX_$F` it used before, because 9.1's patterns
  bind ONE capture `f_` both as a value (`Derivative[1][f_]`) and as a head
  (`f_[x_]`). Guarded: a user function whose name and arity collide with a
  table head keeps the `MX_` head.

**The measured ceiling.** Maxima applies no chain rule to an undeclared
function of a composite argument (N13: d/dx `F(f(x)*g(x))` is the noun
`'diff(F(f(x)*g(x)),x,1)`, not `F'(f g)*(f g)'`). The 8.10 entries whose
answer is `F(<composite>)` or `f(sin(x))*g(%e^x)` (11 entries: 48, 79-81,
90-93, 100-102 by line) therefore cannot SELF-verify; they verify only when
the package answer is form-identical to the expected text (N14). A chain-rule
normaliser in the zero chain would lift this, but it changes verification for
every class and is left as a follow-up question, not part of this port.
