# `9_3 r41`'s pattern makes the matcher enumerate without bound — two class-1 entries go from 1.7 s to over 120 s

Status: open
Type: bug (performance — a verified entry becomes a timeout)
Filed: 2026-09-23 (section-9 port, Task 14 attribution; spec
`docs/superpowers/specs/2026-09-22-section9-port-design.md` A6.3)

## The finding

`9_3 r41` is Rubi's
`Int[u_.*(a_.*v_^m_.)^p_,x] := a^IntPart[p]*(a*v^m)^FracPart[p]/v^(m*FracPart[p]) * Int[u*v^(m*p),x]`
(`9.3 Miscellaneous integration rules.m:345`), pattern

```
(Int (Times (Optional (Pattern u (Blank)))
            (Power (Times (Optional (Pattern a (Blank)))
                          (Power (Pattern v (Blank)) (Optional (Pattern m (Blank)))))
                   (Pattern p (Blank))))
     (Pattern x (Blank Symbol)))
```

On `1 Algebraic functions/1.3 Miscellaneous/1.3.1 Rational functions.mac` e190
`x*(2*c+3*d*x)*(a+c*x^2+d*x^3)^n` the rule never FIRES — its condition is
rejected once, and the process then spends the whole budget inside the
matcher's `mr_cond_retry` alternative-binding enumeration for this pattern,
producing no further verbose line.

## Measured (2026-09-23, build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7)

ALTERNATING SEQUENTIAL timing A/B, one entry at a time, one process at a time,
120 s cpu cap (`test/section9_timing_ab.out`; a concurrent pair never carries a
timing claim — memory: timing-ab-alternate-not-concurrent):

| entry | reference core `0182d32c` | branch core `434c241a` |
|---|---|---|
| `1.3.1` e190 `x*(2*c+3*d*x)*(a+c*x^2+d*x^3)^n` | 1.7 s verified | **>120 s timeout** |
| `1.3.1` e238 `(a+b*x+c*x^2+d*x^3)^p*(b*(1+p)*x+c*(2+2*p)*x^2+d*(3+3*p)*x^3)/x` | 6.2 s verified | **>120 s timeout** |

Both are `verified -> timeout` in the full section-9 A/B
(`test/section9_ab_class1.out`).

Bisected on the branch core by removing handles from `mr_rule_table` and timing
`rubi(f, x)` on e190 (scratch probes, one Maxima process each):

| table | elapsed |
|---|---|
| all of 9.3 removed | 1.74 s, correct answer `(a+c x^2+d x^3)^(n+1)/(n+1)` |
| 9.3 body removed, tail kept | 13.56 s |
| 9.3 body kept, tail removed | no return (killed at 300 s) |
| first 28 body records kept, rest of 9.3 removed | 1.72 s |
| second half in blocks of 7: r30-r36 / r46-r53 / r54-r65 kept | 1.78 / 1.79 / 1.78 s |
| block r39-r45 kept | no return |
| each of r39, r40, r42, r43, r44, r45 kept ALONE | 1.78-1.85 s |
| **r41 kept alone** | **no return (killed at 90 s)** |

Under `rubi_verbose` with only r41 added: exactly one
`rubi: rule 9_3 r41 cond not accepted` line, then 70 s of silence. So the cost
is the MATCH enumeration, not the condition body and not a firing.

Note the 9.3 TAIL also costs ~12 s on this entry (1.7 s -> 13.6 s); that is
separate and not investigated here.

## Why it matters beyond these two entries

`9_3 r41` is also the rule behind ticket 15 (the inert-trig head leak), so the
two tickets share a record. A fix that makes r41 unreachable in the inert domain
does NOT fix this one: e190 has no trig in it.

## Suggested next step (not applied here)

Measure the enumeration directly — `mr-match:match` on this pattern against the
converted integrand, counting alternatives — before changing anything. The
matcher already has a committed cost-bound mechanism (spec
`2026-09-12-matcher-substrate-design.md` §3.8, the flat-absorb committed-tail
prune) and its unit suite `test/matcher/test_mr_match.mac` has cost tests; this
looks like the same class of problem on a pattern with an `Optional` factor
wrapping an `Optional`-exponent Power.
