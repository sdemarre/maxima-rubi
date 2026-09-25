# EqQ / NeQ: the zero test does not expand, so equal-to-zero sums read nonzero

Status: needs-triage
Type: task (measure, then decide)
Filed: 2026-09-15 (matcher translation fixes, P5b attribution class 1 part A. It is outside the plan's
four defects; design §1 Out says an audit of every translated predicate is ticketed, not fixed.)

## Problem

The port (`maxima_rubi_utils.mac:369–372`, same text at P0 `0a6664c`):

```maxima
%mr_eqQ(u, v) := %mr_b(u - v = 0)$
%mr_neQ(u, v) := block([z],
  z : is(u - v = 0),
  if z = true then false else true)$
```

Rubi (`reference/rubi/Rubi/IntegrationUtilityFunctions.m:365`, `:370`, pinned clone):

```mathematica
EqQ[u_,v_] := Quiet[PossibleZeroQ[u-v]] || Refine[u==v]===True
NeQ[u_,v_] := Not[Quiet[PossibleZeroQ[u-v]] || Refine[u==v]===True]
```

`is(u - v = 0)` compares after simplification but does not expand. A bound coefficient that is an
unexpanded sum can make `u - v` identically 0 while the test reads it as nonzero. `EqQ` then reads
False and `NeQ` True where Rubi's `PossibleZeroQ` reads zero.

## Evidence (inferred from traces and rule text, not yet measured)

From `probes/matcher/10-p5b-attribution.mechanisms-class1-a.md:26–39`:

- It bites on the factorable quadratics `a d e + (c d^2 + a e^2) x + c d e x^2` and
  `c d^2 − b d e − b e^2 x − c e^2 x^2`.
  `c d^2 − b d e + a e^2` stays e.g. `c*d^3*e - d*e*(c*d^2+a*e^2) + a*d*e^3`.
- No fire of 1_2_1_3_r88 appears in any row of the three class-1 P5b probe 10 legs. The same holds for
  the 17 1_2_1_2 rules whose condition is `%mr_eqQ(c*d^2 - b*d*e + a*e^2, 0)`.
- The NeQ rule 1_2_1_2_r107 fires on all 16 entries of class 1 g12.
- 9 of those 16 answers divide by `a*d*e^3-d*e*(a*e^2+c*d^2)+c*d^3*e`, which expands to 0. These are
  wrong answers.
- Class 1 groups whose route turns on it: g3, g12, and entries of g4/g8/g10/g18 (tagged `none`, listed
  separately in that file's clearance summary).

## History that constrains the fix

The comment above the definitions records an earlier, "fire when the condition could hold" reading of
EqQ (`%mr_possible_zeroQ`, zero-substituting every symbol). It over-fired at scale in the 2026-08-24
full class-1 run (19,454 FAILs). The syntactic test replaced it.

A fix must therefore distinguish two cases:

- **Identically zero after expansion.** Rubi reads True, e.g. through `PossibleZeroQ`'s
  expansion/numeric check.
- **Zero for some parameter values.** Rubi reads False.

## What to do

1. Probe: evaluate `%mr_eqQ` / `%mr_neQ` on the g12 coefficient shapes, both as bound and fully
   expanded. Compare with candidate readings on the same shapes:
   - `is(ratsimp(u - v) = 0)`
   - `is(expand(u - v) = 0)`
   - a randomized-numeric zero test in the spirit of `PossibleZeroQ`

   Count every generated `%mr_eqQ(` / `%mr_neQ(` site per class.
2. Decide with the user: change the reading (named entries unchanged, so no regeneration), or record it
   as a deviation.
3. If changed: red/green probe, Layer A checks, and a corpus A/B, because it moves many 1.1.x/1.2.x
   routes.

## Comments

2026-09-25 (class-5 port, branch `class-ports`) — **a class-5 site.** 5.3.7 r27/r28 (the ShowSteps
pair `Int[u_*v_^n_., x]`, quadratic `v` of negative discriminant, `u` carrying ArcTan/ArcCot of a
linear argument) require `EqQ[Discriminant[v,x]*tmp[[1]]^2 + D[v,x]^2, 0]`, an identity in x. It
cancels on simplification for `v = 1+x^2` (the rule fires; Layer A `test_class5_e2e`), and not for a
shifted quadratic: `4x^2+4x+2` with `atan(2x+1)` gives `-16*(2*x+1)^2+(8*x+4)^2`, which
`%mr_eqQ` reads nonzero, so the rule declines. Details on
`.scratch/class-ports/issues/02-class5-inverse-trig-functions.md` (Steps 2-7, finding 1).

2026-09-25 (class-7 port, branch `class-ports`) — **a class-7 site, the ArcTanh/ArcCoth twin of the
class-5 one.** 7.3.7 r25/r26 (`Int[u_*v_^n_., x]`, quadratic `v` of positive discriminant, `u`
carrying ArcTanh/ArcCoth of a linear argument) require `EqQ[Discriminant[v,x]*tmp[[1]]^2 - D[v,x]^2,
0]`. For `v = 1-x^2` with `atanh(x)` it cancels and the rule fires; for `v = -4x^2-4x` with
`atanh(2x+1)` the residual `16*(2*x+1)^2-(-(8*x)-4)^2` reads nonzero to `%mr_eqQ` (ratsimp closes it)
and the rule declines to the `unintegrable` noun on a 1_1_1_1 + 7_3_7 table:
`probes/matcher/25-class7-eqq-shifted-quadratic.out` (build `branch_5_50_base_84_g4204fb669`).
Details on `.scratch/class-ports/issues/04-class7-inverse-hyperbolic-functions.md`.
