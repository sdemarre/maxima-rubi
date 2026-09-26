# An expansion that 1_2_3_1 r11 folds straight back is cut by the seen test

Status: needs-triage
Type: bug (route; 35 + 7 entries)
Filed: 2026-09-26 (class-ports final attribution, `probes/class-ports/final/attribution.out`)

## Finding

The ExpandIntegrand reciprocal-atom guard (fix A, `3bb8c4f`) is correct. It removes a `part`
error that had made the calling rule misfire into a route that happened to verify. The expansion
now completes, for example `a^2/x + 2ab + b^2 x`. Then **1_2_3_1 r11**
(`Int[(a + b x^-n + c x^n)^p_.]`, with p defaulting to 1) refolds that sum into
`(a^2 + 2abx + b^2 x^2)/x`, the integrand the expansion started from. The exact seen test cuts
the refold, every later rule misfires, and 9_3 r67 gives up.

- 78 of the final re-measure's 182 PASS->FAIL are fix A's (bucket A). 65 of them first fail at
  `3bb8c4f` in the commit bisect (`08-bisect-3bb8c4f.out`), and all 65 pass with the guard
  reverted (`09-revert-A.out`). 35 traces show the r11 refold (`10-trace-fixA-final.out`).
- The class-6 attribution's 7 "seen-test cycle" entries (1_1_2_2 r5 <-> 1_2_3_1 r1) are the same
  shape.

## Questions

- In Mathematica, which rule answers `Int[a^2/x + 2ab + b^2 x]`? Rubi's own order would expand
  the sum term by term (9.1's sum splitting, or IntSum) before a trinomial rule sees it. Check
  where the sum-splitting records sit relative to 1.2.3.1 in `mr_rule_table`. Ticket 07's bare-u_
  records and ticket 09's legacy 9.1 position are candidates.
- Whether r11's defaulted `p_.` should match p = 1 at all on a sum that is already expanded.
