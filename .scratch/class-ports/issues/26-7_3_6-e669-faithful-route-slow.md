# 7.3.6 e669: the faithful route costs 59 s of CPU (the PolyQ fix removed an accidental fast path)

Status: needs-triage
Type: performance (matcher / condition cost)
Filed: 2026-09-29 (the checker_measure.sh full re-run, arm 2 vs arm 1)

## What

`7 Inverse hyperbolic functions/7.3 Inverse hyperbolic tangent/7.3.6 Exponentials of inverse
hyperbolic tangent functions.mac` e669, `1/(%e^atanh(a*x)*(c-c/(a^2*x^2))^4)`, is the one
PASS -> FAIL of the rule fixes (`test/chk_attr_head_class7.out`: `FIX loss`, re-run on both
cores at 12 workers: timeout on coeff-together's rules, verified on master's).

Measured 2026-09-29, build branch_5_50_base_84_g4204fb669 / SBCL 2.6.7:

| rules | route | rubi CPU |
|---|---|---:|
| master `b62d6d7` (core f2cb4fc6) | 7_3_6 r35 -> **1_1_3_7 r45** -> 9_1 r13 (partial fractions) -> 7_3_6 r5/r7/r1 per term | 0.47 s |
| coeff-together `23d3c9a` (core c01ce534) | 7_3_6 r35 -> **7_3_6 r27** -> 1_1_2_8 r14 -> 1_1_2_10 r5 x3 -> 1_1_2_7 r5 -> 1_1_2_1 r17 | 59.2 s (the first step alone 58.2 s) |

Both answers are complete (no integrate noun). The corpus cap is 30 s, so the entry reads
`timeout`.

## Why

1_1_3_7 r45's condition requires `PolyQ(Pq, x)` with `Pq = %e^-atanh(a*x)*x^8` -- not a
polynomial in x. On master r45 fired only because PolyQ walked a product's FACTORS
(fixed in `b11a93f`, "PolyQ walks terms, not factors"). Master's fast answer was an accident
that happened to be right (the partial-fraction expansion carries the exponential along).
coeff-together takes Rubi's own route (7_3_6 r27), which is correct but slow here.

The cost is not in the 7 rules that fire: the verbose trace of the first step shows ~3,000
condition rejections (top: 1_2_3_2 r39 308, 1_4_1 r24 184, 1_2_3_5 r25 154, 1_4_1 r23 116,
1_1_1_7 r11 107, 1_1_1_7 r10 103). Matcher/condition speed, the standing route for
slow-correct entries (AGENTS.md: the 30 s cap stays).

## Next

- Profile the 7_3_6 r27 -> 1_1_2_8 r14 -> 1_1_2_10 r5 descent: which of the rejected records
  could the dispatch index skip (ticket 21), which conditions are expensive (ticket 23's
  EqQ-on-radicals cost is a candidate).
- Other 7.3.6 / 7.4.2 entries with a non-polynomial Pq that master solved through r45 may have
  the same shape; the arm-2 A/B shows only e669 crossing the cap.

## Reproduce

```
sbcl --tls-limit 100000 --core test/mr_rules.core --noinform --very-quiet -b <file>
```
with `rubi((%e^-atanh(a*x)*x^8)/(1-a^2*x^2)^4, x)` timed by `elapsed_run_time()`, against
`--core ../maxima-rubi-master-core/test/mr_rules.core` for the master side. Do NOT time it with
the checker's `mr_cpu_timed`: see `.scratch/corpus-harness/issues/09`.
