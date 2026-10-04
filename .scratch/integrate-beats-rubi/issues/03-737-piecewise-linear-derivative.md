# 7.3.7: Rubi's piecewise-linear rules divide by an unsimplified derivative

Status: needs-triage
Type: answer quality (grade B where the optimal is reached up to an identity factor)
Filed: 2026-10-04 (user caught the grade report's earlier explanation, "native
Maxima reduces atanh(tanh(a+b*x)) to a+b*x", as wrong: integrate keeps it)

## Symptom

114 entries of 7.3.7 are graded B for maxima-rubi and A for native Maxima.
Both arms keep `atanh(tanh(a+b*x))` in the answer:

    rubi(atanh(tanh(a+b*x)), x)       -((tanh(b*x+a)^2-1)*atanh(tanh(b*x+a))^2)/(2*b*sech(b*x+a)^2)
    optimal                           atanh(tanh(b*x+a))^2/(2*b)
    integrate(atanh(tanh(a+b*x)), x)  x*atanh(tanh(b*x+a)) - b*x^2/2

## Cause (measured 2026-10-04, probes/integrate-beats-rubi/06-737-piecewise-linear-derivative.py/.out)

The answer comes from Rubi 9.2 r1 (`rules/class9/9_2.mac`),
`Int[u^m, x] := With[{c = Simplify[D[u, x]]}, 1/c * Subst[Int[x^m, x], x, u]]`
(and its 9.2 siblings, which take `Simplify[D[u,x]]` / `D[v,x]` the same way).
Mathematica's `Simplify` reduces `D[atanh(tanh(a+b x)), x]` to `b`;
`%mr_simp(diff(atanh(tanh(a+b*x)), x))` gives `-(b*sech(b*x+a)^2)/(tanh(b*x+a)^2-1)`,
which `trigsimp` reduces to `b`.

Over the 119 entries (rubi below A, native A): 112 of the 114 B answers hold
`sech` (no integrand does) and fired a 9_2 rule; `trigsimp(answer)` grades A on
82 of them. e53 (`atanh(tanh(b*x+a))^2/x^5`) also keeps a factor
`b*x - atanh(tanh(b*x+a))`, whose derivative is 0 -- not attributed.

## Wanted

Decide where the reduction belongs: `%mr_simp` (Rubi's `Simplify`) reducing
hyperbolic/trig identities in a derivative (e.g. trigsimp when the input holds
trig/hyperbolic heads), or only the 9.2 rules' `c`. A/B-gated: `%mr_simp` is
used across all classes.
