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

### 2026-09-25 — Steps 2-7 complete (branch `class-ports`)

Build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7. Steps 8-9 (baseline and
package corpus runs) are the coordinator's.

- **Step 2** (`0c99f7a`): 7 RENAME rows (the natives), HypergeometricPFQ
  -> hypergeometric, and three emitter handlers (PolyGamma, Zeta,
  Derivative). The generator's `load_class_files` comment-strips Rubi.m
  (the 8.10 Bessel line). Byte-identity EMPTY for 1/2/3/4/6/9 + rewrites —
  after fixing a PRE-EXISTING abort (`a6713a4`): on the base `cd0a421`,
  `--class 1` and `--class 3` died on `drop_comment_only_lines`' join
  guard (7df5f9d), so that gate could not run at all.
- **Step 3** (`2424269`): 328 rules = 307 (9 files) + 21 (9.1 Derivative as
  `rules/class8/9_1d.mac`, key `9_1d` — `9_1` belongs to the legacy
  class-1 file). The 17 class-8 G-9 risk rules accepted with reasoning;
  `Block[{$UseGamma = True}, …]` is a dynamic `block([mr_use_gamma_flag :
  true], …)`. P3 static 24/0. 8.9 r44 (bare `u_`) lands in the tail.
  Upstream quirk, ported faithfully: 8.4 r29 and 8.5 r29 test
  `MemberQ[{SinIntegral, CosIntegral}, x]` — `x`, not the head capture
  `F` — so both rules are dead in Rubi and here.
- **Step 4** (`f85c9ec`, `3b0f000`, `37b2e3a`): mr-tree (user-function heads
  by name; `'diff(f(u),u,n)` <-> `(((Derivative n) f) u)`), then
  `%mr_derivative`, `%mr_functionOfExpnQ` + FunctionOfQ's general arm,
  `%mr_substForAux` + SubstFor's general fallback, `%mr_formalDerivativeQ`
  in CalculusQ, and TWO CAPTURE TRAPS the 8.10 integrands hit (rubi/mr_int
  took the integrand as a parameter named `f`; `apply(op(u), …)` evaluated
  an operator symbol like `f` — now `funmake`). Layer A 1293 -> 1350/0;
  mr-tree 58 -> 84/0.
- **Step 5**: P3 24/0 (with Step 3). No raw `$` in the class-8 files.
- **Step 6** (`e96ec4c`): `mr_load_all` loads class 8 then `9_1d` after
  class 6 / class 4's subset, before 9.3; tail gains 8.9 r44. Table 4,325.
  Core rebuilt in the `mr-ports` worktree: `rules=4325`, fingerprint
  `412bfc4f5e433d077041d4f882b43a4a` (the driver's fingerprint agrees:
  `test_driver_core_pin` 7/0). Rule-table order 14/0.
- **Step 7**: `HEAD_REWRITES` — `GAMMA(`/`Ei(` arity-dispatched, six new
  native rows, and two structural rewrites (`Derivative(A)(B)(C)` ->
  `%mr_derivative(A, B, C)`, `Psi(n,z)` -> `psi[n](z)`); unit
  `test/test_head_rewrites.py` 20 -> 47/0. No-op, measured over EVERY entry
  without Maxima (`probes/corpus/16-class8-head-rewrite-noop.out`): 0
  normalized texts differ from `cd0a421` in sections 1/2/3/6; section 8's
  rewrite totals equal the Step-1 census (Derivative 320, Psi 77, GAMMA 18 +
  690, Ei 472 + 334, ProductLog 1695, …). Slice A/B
  (`probes/corpus/17-class8-slice-ab.out`, 53 entries of classes 1/2/3/6 on
  a core built at `cd0a421` vs the class-8 core): 0 PASS->FAIL, 2 FAIL->PASS
  (2.2 e1/e2 `contains-noun -> expected`, class 8's 8.8 polylog rules
  finishing class-2 sub-integrals — the rubi_verbose trace shows 8_8 firing
  twice). The 3-per-file class-8 slice: 17/30 PASS (15 verified, 2
  expected), 12 contains-noun (8.2/8.4/8.5/8.8 first entries: nested
  sub-integrals need the unported trig class), 1 unverified (8.7 e1).

**Findings for Step 9 / follow-ups.**

1. **Issue 07 meets 9.1.** On the full table `f'(x) g(x) + f(x) g'(x)`
   does not reach 9.1 r19: `1.4.1 r7` (a bare-`u_` BODY exception, issue 07)
   splits the sum first, where Rubi's specificity order tries r19 first;
   each term is then unintegrable. On a 9_1d-only table r19 answers
   `f(x) g(x)` (Layer A `test_class8_e2e`). Expect the 8.10 product-rule
   entries to fail until issue 07 / ticket 09 settle bare-`u_` placement.
2. **9.3 r36 is now live.** `FunctionOfQ[x^(m+1), u, x]` was always false
   under the port's old general arm; it is Rubi-faithful now. Whether it
   moves class 1-6 entries is a Step-9 A/B question.
3. **Three older Layer A checks flipped to the faithful reading**
   (`calculusQ`/`inverseFunctionFreeQ`/`calculusFreeQ` on `diff(f(x), x)`):
   under the Derivative design that noun is Mathematica's evaluated
   `Derivative[1][f][x]`, not an unevaluated `D`.
4. **The capture fixes reach every class** (the renamed entry parameters,
   `funmake` at 16 rebuild sites). Measured neutral on 53 accepted-class
   entries and Layer A; the class-wide A/B is Step 9's. Ticket 17 (symbols
   in the integrand shadowed by utility parameters) remains open.
5. **Verification ceilings** (probe 04): the composite-argument chain rule
   (11 8.10 entries), 2-arg `Zeta` (inert), `psi[-k]` (no float).

**Decided by judgment** (recorded here, not asked): the `9_1d` key; `Zeta`
2-arg as an inert noun; SubstFor's new fallback gated on FunctionOfExpnQ
(old `subst` kept otherwise); FunctionOfQ's hyperbolic arms left unported
(still decline); `funmake` for every generic-head rebuild rather than only
the class-8 paths; the Derivative representation (above).
