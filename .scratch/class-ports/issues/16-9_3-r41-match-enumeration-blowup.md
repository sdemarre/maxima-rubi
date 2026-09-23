# `9_3 r41`'s pattern makes the matcher enumerate without bound — two class-1 entries go from 1.7 s to over 120 s

Status: open
Type: bug (performance — a verified entry becomes a timeout)
Filed: 2026-09-23 (section-9 port, Task 14 attribution; spec
`docs/superpowers/specs/2026-09-22-section9-port-design.md` A6.3)

## The finding

`9_3 r41` is Rubi's
`Int[u_.*(a_.*v_^m_.)^p_,x] := a^IntPart[p]*(a*v^m)^FracPart[p]/v^(m*FracPart[p]) * Int[u*v^(m*p),x]`
(`9 Miscellaneous/9.3 Miscellaneous integration rules.m:346-348`), pattern

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
120 s cpu cap — **committed probe `probes/section9/05-timing-ab.run`**, output
`probes/section9/05-timing-ab.out`; a concurrent pair never carries a timing
claim (memory: timing-ab-alternate-not-concurrent):

| entry | reference core `0182d32c` | branch core `434c241a` |
|---|---|---|
| `1.3.1` e190 `x*(2*c+3*d*x)*(a+c*x^2+d*x^3)^n` | 1.7 s verified | **120.1 s, cap hit** |
| `1.3.1` e238 `(a+b*x+c*x^2+d*x^3)^p*(b*(1+p)*x+c*(2+2*p)*x^2+d*(3+3*p)*x^3)/x` | 6.2 s verified | **120.1 s, cap hit** |

The same probe covers five further entries; three of them are a plain slowdown
(`1.2.1.2` e335 18.0 -> 27.8 s, `1.2.1.4` e585 18.4 -> 43.0 s, `1.2.1.9` e61
19.2 -> 29.1 s) and two are unchanged (`1.2.1.2` e404 21.5 -> 21.9 s,
`1.2.1.3` e1154 21.8 -> 22.2 s). Whether `9_3 r41` is behind the three
slowdowns too is NOT measured — only e190 was bisected.

Both are `verified -> timeout` in the full section-9 A/B
(`test/section9_ab_class1.out`).

Bisected on the branch core by removing handles from `mr_rule_table` and timing
`rubi(f, x)` on e190 — **committed probe
`probes/section9/03-r41-bisect.{mac,run,out}`**, one Maxima process per arm
under `timeout` (an arm that does not return inside the budget is recorded
HUNG, because these arms never return and Maxima has no per-call timeout):

| arm (9.3 handles KEPT) | elapsed |
|---|---|
| `none-removed` — the shipping table | **HUNG** (no return inside the 90 s budget) |
| `all-9_3-out` | 2.09 s, correct answer `(a+c x^2+d x^3)^(n+1)/(n+1)` |
| `body-out` (9.3 tail kept) | 15.88 s, same answer |
| `tail-out` (9.3 body kept) | **HUNG** |
| `body-first-28` | 1.86 s |
| `block-r30-r36` / `block-r46-r53` / `block-r54-r65` | 1.91 / 1.76 / 1.77 s |
| `block-r39-r45` | **HUNG** |
| `only-r39` / `only-r40` / `only-r42` / `only-r43` / `only-r44` / `only-r45` | 1.81 / 1.78 / 1.76 / 1.77 / 1.77 / 1.76 s |
| **`only-r41`** | **HUNG** |

Under `rubi_verbose` with only r41 added: exactly one
`rubi: rule 9_3 r41 cond not accepted` line, then 70 s of silence. So the cost
is the MATCH enumeration, not the condition body and not a firing.

Note the 9.3 TAIL also costs about 14 s on this entry on its own (2.09 s ->
15.88 s); that is separate and not investigated here.

## Why it matters beyond these two entries

`9_3 r41` is also the rule behind ticket 15 (the inert-trig head leak), so the
two tickets share a record. A fix that makes r41 unreachable in the inert domain
does NOT fix this one: e190 has no trig in it.

## Related

- Ticket 15 (class-9 body rules leak inert trig heads) — the same record,
  `9_3 r41`, is implicated in both tickets: it is the first place to look
  for either defect. They are not the same bug -- e190 here has no trig in
  it at all -- and ticket 15 does not claim r41 is the only leaker (five of
  the six inert heads leak across the 281 `error` entries there), so a fix
  for one is not expected to fix the other.

## Suggested next step (not applied here)

Measure the enumeration directly — `mr-match:match` on this pattern against the
converted integrand, counting alternatives — before changing anything. The
matcher already has a committed cost-bound mechanism (spec
`2026-09-12-matcher-substrate-design.md` §3.8, the flat-absorb committed-tail
prune) and its unit suite `test/matcher/test_mr_match.mac` has cost tests; this
looks like the same class of problem on a pattern with an `Optional` factor
wrapping an `Optional`-exponent Power.
