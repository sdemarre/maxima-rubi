# Rule translation of the algebraic class (T4)

Which of Rubi 4's class-1 (algebraic) rules translate mechanically into
Maxima, on what support surface, in what file format, by what procedure,
and what prior art to learn from. Built on, and citing:

- `probes/translation/01-class1-syntax-census.py` / `.run` / `.out` —
  token census of the 2,710 loaded class-1 rules (run
  `sh probes/translation/01-class1-syntax-census.run`);
- `probes/translation/02-support-surface.mac` / `.run` / `.out` —
  call-based audit of every Maxima name the translation needs in the
  installed binary (run `sh probes/translation/02-support-surface.run`);
- `probes/probe-rubi-anatomy/01-inventory.out` (T1) — the same 67-file /
  2,710-rule loaded set the census re-parses;
- `docs/pattern-matching-feasibility.md` (T2) — runner design, the
  `a_.`-optional decision (N+D), orderless emulation, 0.007 ms/match;
- SymPy's Rubi port, assessed 2026-08-18 against
  `sympy/integrals/rubi` at tag `sympy-1.11` (the last release shipping
  it): `parsetools/parse.py` fetched and read in full,
  `github.com/sympy/rubi` (the surviving copy) confirmed to exist;
  remaining claims per the research digest of that tag and of PR
  sympy/sympy#12978 / #24315 (see §5).

Everything below measured on the installed binary
`branch_5_49_base_796_g60186bb22_dirty` (2026-07-28), SBCL 2.6.7, on
2026-08-17/18 (the census .out is UTC-stamped 2026-08-17, the
support-surface .out 2026-08-18). **The support audit is against this
specific dirty dev binary, not against Maxima in general — see §6.**

## 1. Q1 — mechanical vs hand-ported

The census parses only the class-1 files that `Rubi.m` actually loads
(67 files, 2,710 rules — the T1 count — of the 3,258 on disk; 2,705
carry a `/;` condition) and extracts every CamelCase function token in
conditions, replacements and patterns. The token vocabulary is **closed
by the three tiers** the census defines: zero unlisted tokens across all
2,710 rules. Rule-level classification from
`01-class1-syntax-census.out`:

| class | rules | share |
|---|---|---|
| AUTO — tokens all BUILTIN/B_TIER (direct Maxima names or small Rubi utilities) | 2031 | 74.9% |
| MANUAL — ≥1 C-tier structural predicate or exotic pattern | 679 | 25.1% |

"MANUAL" does **not** mean hand-translated per rule. It means the rule's
*condition* calls a structural predicate (PolyQ family, MatchQ,
SimplerQ, …, 37 distinct C-tier tokens — census "C-tier tokens" list)
that exists only in Rubi's
`IntegrationUtilityFunctions.m`. Port each such predicate **once** and
the rule body stays mechanical — the generator emits `PolyQ(Px, x)` as
a call to the ported function, exactly as it emits `FreeQ` as `freeof`.
There is no rule in the class whose *syntax* the generator cannot
handle; the hand-translation surface is the finite utility layer:

- 37 C-tier predicates (census "C-tier tokens" list; largest users:
  PolyQ 376 rules, IntBinomialQ 78, LinearQ 61, SumSimplerQ 36,
  BinomialQ 32, SimplerQ 29);
- ~25 B_TIER utilities (Coeff, Expon, FracPart, IntPart, Rt, Simp,
  Subst, ExpandIntegrand, ExpandToSum, … — T1's utility inventory has
  the .m sources);
- ~15 shims for names missing from this binary (§2, §6).

Concentration: the 679 bucket spreads over 64 files but clusters — the
top ten files hold 285 of them (1.1.3.7 P(x)(a+bx^n)^p: 37, 1.2.1.7:
33, 1.1.3.8: 30, 1.2.2.7: 29, 1.4.2 normalization: 29 with 12 distinct
token-sets, 1.1.3.4: 27, 1.2.1.9: 26, 1.1.3.2: 25, 1.2.3.6: 25,
1.1.2.4: 24). Files with one distinct token-set (23 of the 64, e.g.
1.2.1.7: 33 rules / 1 set) clear in one pass once their one predicate
is ported.

Pattern-side features (census): `x_Symbol` in all 2,710; optional
captures `a_.` in 2,684 (histogram: 26 rules with 0, 205 with 1, 563
with 2, …, 6 with 12 — mean ≈ 4.2, worst cluster in the 1.4.x
normalization files); a power of the captured/variable slot in 2,387;
a `Sqrt` head in 505 patterns. The `a_.` handling is T2's call
(normalize-or-duplicate at the generator, no matcher extension) and is
purely mechanical: for each rule the generator expands the `k` optional
slots into the explicit cases (slot = default, slot present); the
histogram bounds the fan-out (2^12 only in 6 rules, 2^10 in 39).

**Answer:** all 2,710 rules generate; 74.9% need only the BUILTIN/B_TIER
layer, the remaining 25.1% additionally need the 37 structural
predicates ported once. No per-rule manual translation is required; per-rule
*verification* runs on the corpus (§4).

## 2. Q2 — the support-function surface this class needs

Census token counts (rules using the token) sliced by what the
support-surface audit found in the installed binary. Three states:

- **present** — Maxima name exists and evaluates (call test, audit .out);
- **shim** — name is a Maxima staple *documented in the manual of this
  binary but unbound here*, or absent entirely; a Maxima-level
  implementation is written and unit-tested (§6: may vanish on 5.50);
- **port** — Rubi utility, source in `IntegrationUtilityFunctions.m`.

Conditions (token → used by N rules → state):

| token | rules | Maxima name | state |
|---|---|---|---|
| FreeQ | 2683 | `freeof` | present |
| EqQ / NeQ | 1199 / 1095 | `is(a = b)` / `is(a # b)` … but see PossibleZeroQ | port + shim |
| IntegerQ | 888 | `integerp` | present |
| Not | 740 | `not` | present |
| GtQ / LtQ / IGtQ / ILtQ / LeQ / GeQ / ILeQ | 680 / 574 / 539 / 323 / 65 / 37 / 1 | `>` `<` … wrapped in `is(…)` (value-position comparison stays unevaluated: audit `2 > 1` → `2 > 1`) | present (guard form) |
| OddQ | 1 | `oddp` | present |
| PosQ / NegQ | 225 / 141 | `is(a > 0)` / `is(a < 0)` (`positivep`/`negativep` unbound; `sign(a)` returns `pos`/`neg`/`pnz` symbols, not numbers) | shim |
| RationalQ / IntegersQ / FractionQ | 107 / 79 / 83 | `rationalp` unbound → `integerp(numer(r)) and integerp(denom(r))`-style on rationals; list-form `integerp` per element | shim |
| Simplify | 136 | `ratsimp` / `expand` / `factor` chain (T2's zero-test chain) | shim (policy) |
| Coeff | 45 | `coefficient(x^2+x+4, x, 1)` **noun in this build** (manual: no topic) | shim |
| Expon | 57 | `maxexpt`/`minexpt` **nouns**; `part`-based or `degree` (also a noun here) | shim |
| Sqrt / Log / D (condition occurrences; the Arc* inverse-trig tokens occur in replacements only — counts in the table below) | 8 / 2 / 12 | `sqrt` `log` `diff` `cos` `atan`/`asin`/`acos` present; `acosh`/`asinh`/`atanh` (+ long spellings) **nouns** | port 3 inverse-hyperbolic shims |
| ReplaceAll | 2 | `subst` | present (pattern-shift use) |
| If | 3 | `if` | present |
| PolyQ / LinearQ / QuadraticQ / TrinomialQ / BinomialQ / IntLinearQ / IntBinomialQ / IntQuadraticQ / *MatchQ / SumQ / SimplerQ / SimplerSqrtQ / NiceSqrtQ / PolynomialQ / RationalFunctionQ / MatchQ / NonfreeFactors / SplitProduct / FractionalPowerFactorQ / LeafCount / MonomialQ / PerfectSquareQ / AtomQ / Generalized* / LinearPairQ / PseudoBinomialPairQ / InverseFunctionQ / AlgebraicFunctionQ | 376 / 61 / 10 / 17 / 32 / 5 / 78 / 22 / … / 3 / 3 / 1 / 1 | Rubi's own, from `IntegrationUtilityFunctions.m`; built on `part`/`args`/`length` (all present: `part(x^2+x,1)`→`x^2`, `args(x^2+x)`→`[x^2,x]`, `length(x^2+x)`→2), `nodecount` (**noun → own LeafCount shim**), `is` (returns **`unknown`** as third value — predicates must treat unknown as not-true) | port (37 predicates) |

Replacements (token → used by N rules → state):

| token | rules | Maxima name | state |
|---|---|---|---|
| Int / Unintegrable / CannotIntegrate / IntHide | 2409 / 26 / 1 / 1 | package nouns `mr_int(f, x)`, `mr_unintegrable(f, x)` | package core |
| Sqrt | 625 | `sqrt` | present |
| With / Module | 558 / 35 | `block([...], …, value)` idiom (T2) | present |
| Subst / SubstFor / SubstPower | 389 / 15 / 1 | `subst` for the atom case; For/Power forms = small ports | port |
| Simp / Simplify / SimplifyIntegrand | 346 / 58 / 8 | T2's chain `ratsimp` → `ratsimp∘expand` → `factor` → `ratsimp∘factor` (`simplify` **unbound**) | shim (policy) |
| Rt | 335 | `ratroot` **noun**; Maxima real-root folding gives the odd-n behaviour for `r^(1/n)`, so the shim is a tiny function handling even n → `sqrt`-family and odd n → signed real root | shim |
| ExpandToSum / ExpandIntegrand / ExpandLinearProduct | 230 / 203 / 1 | `expand` present; the "to sum / integrand" split logic is Rubi's (ports) | port |
| Coeff / Coefficient | 198 / 46 | `coefficient` **noun here** | shim + port (Rubi's `Coeff` = leading-ish coefficient with var order) |
| FracPart / IntPart / FractionalPart / IntegerPart | 180 / 121 / 1 / 1 | Laurent-part operators (Rubi's, not Maxima's numeric `fractpart` — **noun anyway**); `truncate`/`floor` present for the scalar cases | port |
| PolynomialQuotient / PolynomialRemainder / PolynomialDivide / Quotient | 108 / 74 / 8 / 2 | `pquoto`/`pmodulo`/`quo`/`(poly) rem` **all nouns** (the bound `rem` is the `put`-property remover and *errors* on polynomial args) | shim (3 small functions over `coefficient`) |
| Denominator / Denom / Numerator / Numer | 88 / 11 / 24 / 11 | `denom` / `num` | present |
| ArcTan / ArcSin / ArcCos | 78 / 43 / 6 | `atan` `asin` `acos` | present |
| ArcTanh / ArcSinh / ArcCosh | 35 / 2 / 1 | **nouns in this build** → log-form shims (`atanh(z) = log((1+z)/(1-z))/2` …) | shim |
| EllipticF / EllipticE / EllipticPi | 33 / 28 / 9 | `elliptic_f/e/pi` **nouns in this build but documented in its manual**; emit as package nouns, differentiation of the answer is at risk here (§6) | noun + verify |
| Sum | 28 | `sum` present but *evaluates definite sums* — Rubi's `Sum` is a formal placeholder → package noun `mr_sum` | package noun |
| Hypergeometric2F1 | 18 | `hypergeometric([a,b],[c],z)` **bound** (list form; warns on scalar args: audit) | present (shape translation) |
| AppellF1 | 8 | no Maxima equivalent at all | package noun (+ deriv rule if corpus needs it) |
| GCD / PolyGCD | 10 / 2 | `gcd` present; `gcf` noun | port (trivial) |
| Together | 12 | **unbound** (T2) → `ratsimp`/`rat`-form: `num(e)/den(e)` after `rat` | shim |
| Mod / Floor | 6 / 5 | `mod` `floor` | present |
| Factor / Sign / Binomial / Cos / D | 5 / 2 / 2 / 8 / 10 | `factor`; `sign` (maps `pos`/`neg`/`zero`→1/-1/0 in the shim); `binomial`; `cos`; `diff` | present (+ sign-map shim) |
| RemoveContent | 12 | `content(3x^2+6x)` → `[3, x^2+2x]` list pair | present (shape) |
| Root | 2 | `rootof` **noun**; Maxima's `rootof` is a different construct anyway | port (algebraic-number noun) |
| Cancel | 2 | `cancel` **noun in this build** | shim |
| Hold | 1 | `holdform` **noun** → custom hold | shim |
| Boole (not in class 1?) — `boole` noun here | — | `if` expression | shim |
| RationalFunctionExpand / NormalizePseudoBinomial | 2 / 2 | Rubi's (ports) | port |
| IntSum / Integrate / ShowStep / Dist | 2 / 1 / 1 / 8 | IntSum = package Sum-over; Dist = factor-linearity helper | port |

Total surface (census token lists, condition ∪ replacement): **67
condition tokens + 66 replacement tokens, 122 distinct functions**;
of those, ~50 are directly present, ~15 are shims on this binary, ~55
are one-time ports from Rubi's own utility file (the 37 structural
predicates + ~18 operators like FracPart, SubstFor, ExpandToSum,
PossibleZeroQ).

## 3. Q3 — rule-file format and loader

Recommendation: **generator-emitted `.mac` rule files, one per Rubi
`.m` file, `load`-ed by the package; rules as data, not as executed
definitions.**

Per emitted file (e.g. for Rubi's `1.1.1.2 (a+b x)^m (c+d x)^n.m`):

```
/* generated from Rubi/IntegrationRules/.../1.1.1.2 (a+b x)^m (c+d x)^n.m
 * pin 61e9c18e — do not edit */
mr_rules_1_1_1_2 : [
  [ _mr_pat_1_1_1_2_r1,   _mr_cond_1_1_1_2_r1, _mr_repl_1_1_1_2_r1 ],
  ...
]$
```

where each triple is a compiled pattern (unique per rule — the census
proves no name reuse is safe), a value-carrying guard `block([...], if …
then … else …)` (T2's idiom), and the replacement closure over the
capture names. Reasons:

1. **T2's runner is at Maxima level**: no Lisp tables to maintain; a
   `.mac` file is plain Maxima data that the runner walks in Rubi
   order. 0.007 ms/match (T2) makes a flat per-rule table fine at
   class-1 scale; a discrimination net is not worth it.
2. **1:1 file correspondence with both Rubi and the test corpus**:
   corpus files are named after Rubi rule files
   (`1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p` in both trees) → per-file
   selection, per-file test runs, and per-file divergence reports all
   share one key.
3. **Regenerable, not hand-edited**: files carry the Rubi pin; a
   Rubi-version bump re-runs the generator over the diff. Committed so
   `git diff` shows exactly which rules a Rubi change moved.
4. **Unique names per rule** (`_mr_<file>_r<n>`) sidestep T2's
   measured traps: global capture-variable binding and the
   defmatch-after-kill anomaly both require distinct, never-killed
   names.

## 4. Q4 — the translation procedure

Mechanical (a Python generator; the census script already contains the
`.m` rule-run parser it reuses):

1. Parse each loaded `.m` into rule runs (`Int[...], x_Symbol] := rhs
   /; cond`), same convention as T1's inventory (reproduces 2,710).
2. Per rule: rename pattern variables to `_mr_<file>_r<n>_<var>`;
   expand each `a_.` optional slot into explicit cases (T2's N; fan-out
   bounded by the census histogram); translate the head
   `Int[expr, x_Symbol]` to the runner's `(f, x)` call shape with the
   `freeof(x, …)` guard; translate every token through the closed
   table of §2 (generator fails loudly on an unknown token — the census
   made the table provably complete for class 1).
3. Conditions: split on `&&` into a value-carrying if/else chain;
   comparisons via `is(…)` (value-position comparisons stay unevaluated
   — audit; `is`'s third value `unknown` counts as not-true);
   `FreeQ[{a,b}, x]` → `freeof(x, a) and freeof(x, b)`; `EqQ`/`NeQ` →
   the ported predicates (§2 — 4.16 delegates them to PossibleZeroQ).
4. Replacements: `Subst[...]` → ported subst forms; `Simp[...]` → the
   package simplify policy; `Int[smaller, x]` → `mr_int(smaller, x)`
   (recursion handled by the runner's T2 dispatch, max-recursion
   capped); `Sum` → `mr_sum`; 2F1/AppellF1/elliptic in their Maxima
   forms.
5. Emit the `.mac` triple table; a loader `load`s one file per rule
   section and registers triples into the section's rule list; a
   `mr_rules_count` per section cross-checks the census (2,710).

Manual (finite, enumerable, all in the utility layer — none per rule):

1. Port the ~55 §2 functions marked "port": the 37 C-tier structural
   predicates + the B_TIER shape operators (Coeff, FracPart, IntPart,
   SubstFor/SubstPower, ExpandToSum/ExpandIntegrand/ExpandLinearProduct,
   EqQ, NeQ, PossibleZeroQ, …), from
   `IntegrationUtilityFunctions.m` (T1 inventory has each one's .m
   source and line range). Each is small; each gets a unit probe against
   its .m semantics before the generator's output that calls it is
   trusted.
2. Write the ~15 shims for names this binary lacks (§2/§6), with unit
   probes; on a Maxima upgrade re-run `02-support-surface.run` and
   delete whatever became a builtin.
3. Run the generated class-1 rules on the class-1 corpus section
   (25,697 integrands); chase divergences file-by-file using the
   corpus-file ≡ Rubi-file key. The 23 unverified answers of T3's
   sample (zero-test chain did not close) are the expected first
   divergences and drive the strengthen-the-chain loop.

Reuse for class 2 onward: same generator, same loader; only the
per-class predicate additions and the section pin change.

## 5. Q5 — translation references

**SymPy's Rubi port** (`sympy/integrals/rubi`, removed from sympy in
2022 by PR #24315, "the broken rubi package is removed", 1.12 release
notes; surviving copy `github.com/sympy/rubi`, confirmed to exist,
"Previously sympy.integrals.rubi"). At tag `sympy-1.11`:

- **It is a deterministic text-level generator**, exactly the shape §4
  proposes: Rubi's rules are dumped as
  `ToString@FullForm@DownValues@Int` (one consolidated dump, 5,974
  `RuleDelayed` rules, from Rubi's own `Int` downvalues — the
  `Upabjojr/RUBI_integration_rules` repo), `parse.py` (read in full
  2026-08-18) splits it by bracket balancing, rewrites tokens
  through a `replacements` dict (`Times`→`Mul`, `Plus`→`Add`,
  `ArcTanh`→`atanh`, `Module`→`With`, `Int`→`Integral`,
  `Rational[m,n]`→`S(m)/S(n)`, …), and emits one rules module per
  Rubi family file.
- **Constraints are split and de-duplicated**: every leaf of the rule's
  `And` becomes a named `CustomConstraint` in a shared
  `constraints.py` (a `cons_dict` cache), split deliberately "to
  backtrack earlier and improve the speed". Direct analogue: our
  per-rule guard chain; a shared predicate module is the analogue of the
  cache.
- **Optional defaults are matcher-injected, not rule-duplicated**:
  `get_default_values` finds `Optional[Pattern[a_]]` per slot (Plus→0,
  Times→1, Power→1), `add_wildcards` rewrites the slot to
  `WC('a', S(default))`, and matchpy's `ManyToOneMatcher` supplies the
  default when the slot is absent — i.e. T2's option **M** (matcher
  extension), which we rejected for Maxima in favour of N (generator
  duplication). The sympy port proves the default-context table
  (0/1/1 by head) is the right extraction, which the generator reuses.
- **Orderless `+`/`*`**: matchpy's commutative-associative automata
  drive matching, which is what makes Rubi's orderless assumptions hold
  in SymPy. Maxima's matcher does not do this (T2 §orderless); the
  package's canonicalization step must (T2's emulation).
- **Run loop**: `rubi_integrate` (standalone — `integrate()` never
  called it) wraps the integrand in `Integral`, then fixed-point
  `replace` on every `Integral` subexpression, ≤10 iterations,
  `max_count=10` per match. Same shape as T2's runner recursion cap.
- **Known weak spots to not repeat**: `With`/`Condition` parsing grew a
  follow-up PR (#13257); `FreeQ` needed a dedicated parser
  (parse_freeq) because it wraps arbitrary sub-expressions; the
  package was removed as broken — the failure mode to watch is
  *verification*, not generation: generated rules that match but whose
  RHS does not differentiate back to the integrand inside the
  zero-test chain.
- **Version gap**: its inputs are Rubi **4.10.8**'s flat file layout,
  older than our **4.16**: the 1.1.4 improper
  binomials and the 1.3 polynomial-products module it would need do not
  exist there, and its hand-written `utility_function.py` (7,336 lines,
  471 defs) predates the predicates 4.16's rules assume
  (GtQ/LtQ/IGtQ/ILtQ/NeQ, PossibleZeroQ inside EqQ/NeQ, SubstPower) —
  confirming §2's port list is the current Rubi's, not the sympy
  port's.

**Rubi-5** (route B): already assessed and rejected as a *translation
template* in T2 (Int111/Int121 only, dispatch still Mathematica) —
nothing added here.

## 6. Build-drift caveat (read before trusting §2)

The installed binary is a dirty development build, and **its own manual
does not agree with its function table**: `? atanh` prints a manual
entry ("Hyperbolic Arc Tangent") and `?? elliptic` lists `elliptic_f`,
yet both calls stay nouns in the same binary; the source tree at the
stamped commit `60186bb22` has no `frob` macro (which `trigi.lisp`
uses to define the inverse-hyperbolic functions) and no
`coefficient`/`maxexpt` definitions at all, and carries uncommitted
local edits. Consequences, all measured 2026-08-18:

- Existence of a name must be tested by **calling it** (a noun
  result = unusable); `?`/`??` lookups are not existence tests here
  (and `boundp`/`functionp` are themselves unbound, so there is no
  introspection call).
- The shim list of §2 (coefficient, degree/maxexpt/minexpt, nodecount,
  rationalp, positivep, together, atanh family, elliptic family,
  ratroot, pquoto/pmodulo/quo/polynomial-rem, cancel, holdform, boole,
  gcf, factorterm, rootof) is a property of **this binary**. On the
  5.50 release, re-run `sh probes/translation/02-support-surface.run`
  and shrink the shims to whatever still nouns; the generator's
  translation table does not change either way (it names the shims;
  the shims may become one-line pass-throughs).
- `is(…)` returns `unknown` as a third value (audit: `is(x > 0)` →
  `unknown`); every generated guard and every C-tier port must treat
  unknown as not-true.
- Value-position comparisons stay unevaluated (`2 > 1` prints as
  `2 > 1`); all guards must use `is(…)` / the ported predicates, never
  a bare comparison as the guard's value.
