# Port SimplifyAntiderivative (Rubi's Subst normalisation)

Status: needs-triage
Type: port gap
Filed: 2026-10-03

## Symptom

11 section-6 answers keep `log(%i*tanh(u))` where Rubi's optimal has
`log(tanh(u))` (probe `probes/leaf-size/09-removecontent-ifold.out`, its `same`
lines; e.g. 6.7.1 e24, `csch(a+b*x)*sech(a+b*x)`): `4_1_0_3 r2` answers
`Subst[Int[1/x, x], x, Tan[c + d x]]`, i.e. `log(tan(%i*b*x+%i*a))`, folded at depth
0 to `log(%i*tanh(b*x+a))`.

## Cause

Rubi's `Subst` wraps every result in `SimplifyAntiderivative`
(`reference/rubi/Rubi/IntegrationUtilityFunctions.m:5147-5149`), whose rule
`SimplifyAntiderivative[Log[c_*u_], x] := SimplifyAntiderivative[Log[u], x] /;
FreeQ[c, x]` (`:5291`) drops the constant content of a log. SimplifyAntiderivative
is not ported: no occurrence in the package (`%mr_subst`, `maxima_rubi_utils.mac`,
does the replacement and its simplification only).

## Scope

About 40 rules from `:5265` plus their helpers (`SimplifyAntiderivativeSum`,
`:5600-5800`, the trig/hyperbolic ArcTan normalisations). 1,194 `%mr_subst` call
sites across the rule classes: a port changes answers in every class and needs its
own spec, a measurement on every entry it can act on, and a full re-run.
