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

## A cycle entered at the wrong point (2026-09-27)

The same refold also breaks a NESTED call whose integrand the top level answers. Traced with
`rubi_verbose : 'matches` (the steps list) on the full `mr_load_all` table:

- `rubi((e^2*x^2+2*d*e*x+d^2)/x^2, x)` answers `2*d*e*log(x)+e^2*x-d^2/x`
  (1_4_1 r4 -> 1_1_1_2 r12 -> 1_4_1 r7).
- `rubi((e*x+d)^2/x^2, x)` answers `'unintegrable((e^2*x^2+2*d*e*x+d^2)/x^2, x)`, and so does the
  user's `rubi(((e*x+d)^2*(b*log(c*x^n)+a))/x^2, x)`, whose 3_1_4 r3 takes that integral nested.

The three forms make a cycle: P = `(e*x+d)^2/x^2` -(1_1_1_2 r12)-> S = `2de/x + d^2/x^2 + e^2`
-(1_2_3_1 r1)-> Q = `(e^2x^2+2dex+d^2)/x^2` -(1_4_1 r4)-> P.

- Entered at Q, the path is Q, P, S: r1's refold of S reproduces Q, which is on the path, so the
  seen test cuts it and r1 declines. The next rule on S, 1_4_1 r7 (the sum split), answers.
- Entered at P, the path is P, S, Q: Q is new, so the refold goes through. At Q every route is
  cut (r4 reproduces P), so the give-up 9_3 r67 ANSWERS `'unintegrable(Q, x)`. r1 has "succeeded"
  on S, 1_4_1 r7 never runs, and the noun propagates up.

The seen cut declines a rule so its caller goes on down the table. A give-up reached only
because every ordinary route was cut turns that dead end into an answer.

## Possible workaround (not scheduled)

A nested dispatch in which ordinary rules were cut by the seen test and only a give-up remains
raises the seen cut instead of answering the noun. The rule above (here r1 on S) then misfires,
and the dispatcher continues to the next rule (1_4_1 r7). At depth 1 a genuine give-up still
answers. This covers every cycle of this shape, whichever rules form it, but does not remove the
refold itself. It changes dispatcher semantics: a run switch (default on, the `mr_giveup_last`
pattern) and a corpus A/B before acceptance. User decision 2026-09-27: recorded here, not worked on
now.
