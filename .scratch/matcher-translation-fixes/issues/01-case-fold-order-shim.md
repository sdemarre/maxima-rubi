# Case-fold order shim for the internal-order First/Rest ports

Status: needs-triage
Type: task (measure, then decide)
Filed: 2026-09-14 (matcher translation fixes, user decision while writing the
plan: record Maxima's internal order as a stated deviation, ticket the shim)

## Problem

The PosAux port and its First/Rest siblings (`maxima_rubi_utils.mac`
`%mr_posAux`, `%mr_rt_negSumBaseQ`, `%mr_removeContentAux`,
`%mr_signOfFactor`, `%mr_contentFactor`, `%mr_product_factors`,
`%mr_splitSum_aux`, `%mr_unifySum`) read a sum's or product's parts in
Maxima's internal order (`inpart`, `inflag : true`), the canonical order
`orderlessp` tests. Rubi reads Mathematica's stored order. The two differ.

`probes/matcher/14-mma-order-agreement.out` measures the difference on every
expected answer of classes 1–3 (Mathematica's printed order is its stored
order). A flip is a sum node where PosAux of Mathematica's first term differs
from PosAux of Maxima's first term:

| class | comparable sums | first-term agreement | PosAux flips | removed by a case-fold rename |
|---|---|---|---|---|
| 1 | 279,107 | 92.5 % | 10,093 (3.6 %) | 3,265 |
| 2 | 5,421 | 95.0 % | 138 (2.5 %) | 1 |
| 3 | 41,899 | 95.8 % | 970 (2.3 %) | 0 |

(2026-09-14, build `branch_5_50_base_84_g4204fb669`; measured on the Task 4
review's fix-round-1 commit (`%mr_posAux` branch 2, `float(rectform(u))`),
`probes/matcher/14-mma-order-agreement.out`.)

Mathematica sorts symbols `a < A < b < B`; Maxima sorts every upper-case
symbol before every lower-case one. The case-fold rename (each symbol `v` ->
`<lowercase v>0` or `<lowercase v>1`) moves Maxima's symbol order to
Mathematica's and removes the class-1 flips of the `P(x)` coefficient files
(`A*b` vs `-(B*a)`). The remaining flips follow Mathematica's
product-ordering rules (a factor that contains a sum, radicals and `%i`),
which no small shim reproduces.

## What to decide

1. Whether the `matcher-substrate` P5b attribution
   (`probes/matcher/10-p5b-attribution.*`) shows PASS→FAIL groups in the
   `P(x)` coefficient files (1.1.1.5, 1.1.1.6, 1.1.2.8, 1.2.1.9, 1.2.2.6,
   1.2.3.5, …) whose mechanism is a PosQ/NegQ or First/Rest reading on a
   mixed-case sum or product.
2. If so: a helper that picks the first term (or factor) in case-folded order
   when the expression mixes upper- and lower-case symbols, used by every
   internal-order reader above; re-run probe 14 and the affected entries.

## Comments
