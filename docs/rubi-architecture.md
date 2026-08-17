# Rubi 4 architecture (T1)

Research track T1 of the maxima-rubi project. All claims below are
measured on the pinned reference clone
`reference/rubi` @ `61e9c18ea248061cd83c67882f7c91a73cef912d`
(2024-02-22, distribution version 4.17.3.0 per `Rubi/PacletInfo.m`)
unless stated otherwise; Maxima-dependent measurements are stamped
`branch_5_49_base_796_g60186bb22_dirty` (2026-07-28), SBCL 2.6.7.
Re-runnable probes: `probes/probe-rubi-anatomy/01-inventory.py` and
`02-utility-inventory.py` (outputs committed as `.out`).

## 1. What the package is

`Rubi/Rubi.m` is a 496-line driver. It

1. clears all `Int` downvalues,
2. reads each rule file of the `IntegrationRules/` tree **in a
   hard-coded `LoadRules[...]` order** (roughly 600 lines of calls,
   class 1 first, class 9.1 last),
3. optionally rewrites every rule through `StepFunction`
   (`ShowStepRoutines.m`, `ModifyRule`) so each applied rule records a
   `Step[...]` — the "show the steps" feature, driven by
   `$LoadShowSteps`/`$Steps`,
4. computes `$RuleCount = Length[DownValues[Int]]` immediately after
   the rule loading — the count is taken *before* the driver adds its
   own non-integration downvalues (comment in `Rubi.m:361-363`).

Dispatch is plain **Mathematica downvalue matching on the `Int` head**:
`Int[u_, x_] := replacement /; condition`. First matching downvalue
wins; rule files are loaded in a fixed order, so **file order = rule
priority** (a file's rules shadow later files'). There is no ranking,
no specificity ordering beyond Mathematica's own pattern evaluation,
and no rule database — priority is whatever the load order encodes.

Recursion is the algorithm: a replacement that cannot finish the job
re-invokes `Int` on a *simpler* integrand
(e.g. `... - d*m/(b*(n+1))*Int[(c+d*x)^(n-1)*..., x]`); the driver
does the fixed-point loop implicitly, because the downvalues re-fire
on the new expression. Depth is governed by the rules' own
simplification, not by the engine.

Loading is layered:

| layer | gated by | size |
|---|---|---|
| class 1 (algebraic) + 9.2 + 9.3 | always loaded | **2805 rules** |
| classes 2–8 + 9.1 | `$LoadElementaryFunctionRules` | 7432 − 2805 |

Both numbers measured by `01-inventory.py` (it replays the `Rubi.m`
load list, splits `LoadRules` calls at the `$LoadElementaryFunctionRules`
if-block, and counts `Int[...]:= ` downvalues per file). Class 1 is
by far the largest — this **confirms "algebraic functions" as the
milestone-1 seed class** (2710 of 2805 mandatory rules).

## 2. The rule grammar

A rule is `(pattern, condition) → replacement`:

```
Int[(a_. + b_.*x_)^m_.*Sinh[a_ + b_.*x_]... , x_Symbol] :=
    (c + d*x)^m*Sinh[a + b*x]^(n + 1)/(b*(n + 1))
  - d*m/(b*(n + 1))*Int[(c + d*x)^(m - 1)*..., x]
  /; FreeQ[{a, b, c, d, m, n}, x]        (* example: 6 Hyperbolic *)
```

The recurring shapes, with a concrete instance per function class
(measured by scanning the pinned clone; `01-inventory.out`):

- **class 1, algebraic** — polynomial GCD bookkeeping:
  `Int[u_.*P_^p_*Q_^q_, x_] := Module[{gcd = PolyGCD[P, Q, x]},
  Int[u*gcd^(p+q)*PolynomialQuotient[P,gcd,x]^p*PolynomialQuotient[Q,gcd,x]^q, x]]`
- **class 2, exponentials** — reduction of the exponential's power:
  `Int[(c_.+d_.*x_)^m_.*(b_.*F_^(g_.*(e_.+f_.*x_)))^n_., x_] :=
  (c+d*x)^m*(b*F^(g*(e+f*x)))^n/(f*g*n*Log[F]) - ...`
- **class 3, logarithms** — `PolyLog`/reciprocal rewrite:
  `Int[Pq_^m_.*Log[u_], x_] := With[{C = ...}, C*PolyLog[2, 1-u] /;
  FreeQ[C, x]] /; IntegerQ[m] && PolyQ[Pq, x] && ...`
- **class 4, trig** — exponential-form rewrite:
  `Int[(c_.+d_.*x_)^m_.*csc[e_.+k_.*Pi+f_.*x_], x_] :=
  -2*(c+d*x)^m*ArcTanh[E^(I*k*Pi)*E^(I*(e+f*x))]/f - ...`
- **class 5, inverse trig** — `Subst` round-trip:
  `Int[x_*(a_.+b_.*ArcSin[c_.*x_])^n_./(d_+e_.*x_^2), x_] :=
  -1/e*Subst[Int[(a+b*x)^n*Tan[x], x], x, ArcSin[c*x]] /; ...`
- **class 6, hyperbolic** — power reduction, structurally a copy of
  class 4 with `Sinh`/`Cosh` (shown above).
- **class 7, inverse hyperbolic** — product rule + radical restatement:
  `Int[ArcSech[c_+d_.*x_], x_] := (c+d*x)*ArcSech[c+d*x]/d +
  Int[Sqrt[(1-c-d*x)/(1+c+d*x)]/(1-c-d*x), x] /; FreeQ[{c,d},x]`
- **class 8, special functions** — e.g. `ProductLog` reduction by one
  power, same shape as the class-2 exponential rule.
- **class 9, miscellaneous** — linearity of the outer integral:
  `Int[u_^m_., x_] := ...`, derivative rules `Int[Derivative[n_][f_][x_], x_] := ...`.

Grammar features the Maxima rule runner must support (every one of
these appears in the mandatory classes unless noted):

1. **One free symbol per capture** in patterns; captures may repeat
   (`x_Symbol` for the variable, `a_`/`b_`/… for parameters).
2. **Optional defaults with `.`**: `a_.` = "a, or 1 if absent"
   (e.g. `(a_.+b_.*x_)^m_.` must integrate `x^m` with `a:=1`);
   `F_^(g_.*(e_.+f_.*x_))` uses the same. This is the feature that
   makes 2710 rules cover 1.1.1.1–1.1.1.4 as one rule file.
3. **`/;` conditions** calling ~fifty support predicates
   (`FreeQ`, `EqQ`, `PolyQ`, `IntegerQ`, `GtQ`, `LinearQ`, …).
   `EqQ[u,v] := Quiet[PossibleZeroQ[u-v]] || Refine[u==v]===True`
   (`IntegrationUtilityFunctions.m:365`) — **`PossibleZeroQ` is the
   single hardest condition to port** (a full zero-equivalence
   decider); the rest are structural or arithmetic.
4. **Recursion** via `Int[...]` in replacements (87% of all rules
   re-dispatch, per `01-inventory.out`'s `re-disp` column).
5. **`Subst[Aux...]`** — substitute a new variable in the *answer* and
   back-substitute (1221 call sites; `Subst` is Rubi's own,
   `IntegrationUtilityFunctions.m:5140`).
6. **`Module`/`With` local bindings** in replacements
   (`Module[{gcd = PolyGCD[P, Q, x]}, ...]`) — evaluated once at rule
   application, not at rule definition.
7. **Inert/active trig toggles** (files 4.7.5, 4.7.9, 6.7.9, and the
   `DeactivateTrig`/`ReduceInertTrig` helpers) — class 4 only.

## 3. Rule counts (measured, `01-inventory.out`)

```
class                                       rules  with /;  re-disp  Subst
1 Algebraic functions                        2710     2705     2409     393
2 Exponentials                                125      125       94      18
3 Logarithms                                  333      332      288      57
4 Trig functions                             2073     2073     1851     357
5 Inverse trig functions                      665      665      589     121
6 Hyperbolic functions                        390      390      346      52
7 Inverse hyperbolic functions                710      710      626     126
8 Special functions                           310      310      207      31
9 Miscellaneous                               116      114       96      66
TOTAL (all loaded classes)                   7432     7424     6506    1221
mandatory (always loaded)                    2805
```

The inventory also found **22 stale `.m` files on disk that `Rubi.m`
never loads** (an old 1.3 "Miscellaneous" folder, 1.1.2.x/.y files
superseded by 1.1.2.1–1.1.2.9, and 9.1/9.3/9.4 duplicates), and **0
files referenced but missing**. The stale list is in
`01-inventory.out`; it matters because a naive "port everything in the
tree" would port rules that Rubi 4 itself does not use.

## 4. Support-function inventory (the porting gap list)

`02-utility-inventory.py` extracts the 226 `Name::usage` entries from
`IntegrationUtilityFunctions.m` (17 more in `Rubi.m`, 3 in the
ShowStep files) and ranks every name called from rule files, split
"all classes" vs "core" (mandatory classes 1+9.2+9.3). Top of the core
column (what the algebraic seed class actually needs):

| calls (all / core) | name | porting cost tier |
|---|---|---|
| 2767 | `EqQ` (uses `PossibleZeroQ`) | **hard** — needs a zero-equivalence decider |
| 1473 | `NeQ` | easy — `Not[EqQ]` |
| 1247 | `IntegerQ` (Mathematica builtin) | trivial — integerp |
| 1215 / 64 | `IGtQ`, `GtQ` etc. (6 comparisons) | easy — numeric comparisons |
| 1215→447 `Subst`, 675 `Rt`, 655 `LtQ`… | | |
| 425 | `PolyQ` (is-polynomial p(x) test) | moderate — rational-function degree logic |
| 393 `Simp` | `Simp` = Rubi's own "simpler?" comparator | moderate |
| … | `LinearQ`, `QuadraticQ`, `TrinomialQ`, `BinomialQ`, `FractionalPowerQ`, `NiceSqrtQ`, `FractionalPowerFactorQ`, `Rt`, `RemoveContent`, `NormalizeSumFactors`, `ContentFactorAux`, `SquareRootOfQuadraticSubst`, … | mixed |

Cost tiers used in `docs/` discussion: **trivial** (direct Maxima
builtin: `FreeQ`→`freeof`, `IntegerQ`, `Exp`, `Sqrt`, `With`→`block`,
`Module`→`block`); **easy** (structural predicate, tens of lines:
`LinearQ`, `MonomialQ`, `SumQ`, `PowerQ`, `HalfIntegerQ`); **moderate**
(arithmetic over rationals/powers: `Rt`, `RemoveContent`, `PolyGCD`,
`PolynomialDivide`, `Simp`, `Subst`+aux); **hard** (`EqQ`/
`PossibleZeroQ`, `SimplifyIntegrand` with its `TimeConstrained(5s)`
guards, `ContentFactorAux`, `SmartApart`). Full ranked table with
definition sites: `02-utility-inventory.out`.

## 5. How (un)verified Rubi's answers are

**Rubi does not verify its own answers.** There is no derivative check
anywhere in the package: the acceptance test is the external
`MaximaSyntaxTestSuite` (and the original Rubi test corpus), where each
expected answer is checked by the *test harness* (in our milestone, by
differentiation — see T3/T5). What Rubi does do internally:

- `SimplerIntegrandQ[u, v]` (`IntegrationUtilityFunctions.m:804`)
  decides, before a rule fires, whether re-dispatching `Int` on a
  simplified integrand would help;
- `SimplifyAntiderivative[expr, x]` (`…:5268`) is a
  **derivative-preserving** normalizer applied to *intermediate*
  answers (`Subst`'s back-substitution and the show-steps path use it),
  explicitly documented to only ever apply transformations that keep
  the derivative intact.

Neither substitutes for a final verification; neither is part of any
rule replacement, so a port can omit both in milestone 1 and re-derive
equivalence at the harness instead.

## 6. License

`reference/rubi/LICENSE` — MIT, verbatim:

```
MIT License

Copyright (c) 2018 Rule-Based-Integration Organization

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

A port must therefore carry the copyright notice — the rule files (the
substantial part of the work) are "a substantial portion of the
Software".

## 7. Rubi 5 — the if-then-else reference

`reference/rubi-5` @ `37a71d650aa1ff7903d4de9cdd1a20c115969f4d`
(2021-03-19; single-file prototype `Rubi-5.m`, 1928 lines, plus a 21-line
plan document). Measured state:

- 42 `Int*nnn` functions, one per algebraic integrand shape
  (`Int111` … the 1.3.x misc shapes), each with a `::usage`;
  **only `Int111` and `Int121` are implemented**; the other 40 are
  one-line `Defer[Int*nnn][...]` placeholders.
- The top level still uses 81 Mathematica pattern rules to *dispatch*
  to the `Int*nnn` (e.g. `Int[(a_.+b_.*x_)^m_., x_] := Int111[a,b,m,x]
  /; FreeQ[{a,b,m},x]`); the point of the project is that the *bodies*
  are pure if-then-else, so a host CAS needs pattern matching only for
  the 81 dispatch rules (or none, using the decision-tree classifier
  sketched in the plan doc).
- `Int111` is the 1.1.1 rule file compiled by hand:
  ```
  Int111[a_,b_,m_,x_] :=
    If[EqQ[m,0] || EqQ[b,0], (a+b*x)^m*x,
    If[EqQ[m,-1], Log[a+b*x]/b,
     (a+b*x)^(m+1)/(b*(m+1))]]
  ```
  — three leaves, exactly the three 1.1.1 rules, conditions intact.
- `Int121` (quadratic) is a ~30-deep if-tree with mutual recursion
  into `Int111`/`Int151`/`Int152`, `Subst`, `Apart`,
  `Hypergeometric2F1`, `With`-bindings, and the same predicate
  vocabulary (`EqQ`, `GtQ`, `LtQ`, `IntegerQ`, `RationalQ`,
  `NiceSqrtQ`, `FractionalPowerFactorQ`, `Rt`, …) — i.e. the
  if-then-else compilation does **not** change the support-function
  gap list of §4, it changes only the dispatch.
- The plan doc's categorization for a no-pattern-matching host: type
  numbers 1=linear … 6=trinomial, 7=unknown; linearity + constant
  factor pull-out; sort base/degree pairs by type; descend a 42-leaf
  tree. It also claims the author "already written programs that
  translatex if-then-else decision trees in Mathematica syntax into
  equivalent decision trees in Maple and Maxima syntax" — no such
  program exists in the repo; the claim is unverified.
- The plan doc's disclaimer (quoted): implementing all 42 by hand is
  "challenging"; a pattern-matching-to-if-then-else *compiler* is the
  intended automation.

Relevance to this project: Rubi 5 is a **porting template for route B**
in T2 — milestone 1's algebraic scope is exactly the 42-function scope,
and two of the 42 (the simplest and the hardest) already exist in
portable form. It is also the strongest evidence that the Rubi 4
grammar of §2 compiles to a decision tree without loss.
