# The legacy 9.1 Integrand simplification file loads last in class 1; the 2018-era Rubi loaded it first

Status: needs-triage
Type: task (faithfulness A/B)
Filed: 2026-09-22 (section-9 spec review)

## The finding

`rules/class1/9_1.mac` (28 rules, the legacy "9.1 Integrand simplification
rules", kept under the matcher-substrate spec §3.4 policy) is the LAST
entry of the class-1 table (`maxima_rubi.mac` `mr_rule_table`, after
`mr_rules_1_4_3`). The Rubi that still loaded it, the pre-renumbering
`Rubi.m` (`f7fa0fd^` = `a57f10f`, 2020-05-09), loads it FIRST: L100,
right after the utility package and before `1.1.1.1 (a+b x)^m` (L102).

Rule priority is table order, so where a 9.1 rule and a class-1 rule both
match, we pick the class-1 rule and the 2018 Rubi picked the 9.1 one.
The section-9 spec (§7) had claimed the current placement matched 2018;
that claim was corrected in review.

## To do

Measure, don't move blind: build a core with `mr_rules_9_1` first in the
table (its six bare-`u_` / issue-07 exceptions need checking against the
tail convention too) and A/B the four classes against the same-load
reference with `test/ab_records.py`. Every PASS->FAIL attributed before
the move is accepted. Related: ticket 07 (bare-`u_` records mid-table).

## Comments

- 2026-09-28 (wrong-answer triage, category 4 of `handoffs/2026-09-28-checker-wrong-answers.md`):
  **a witness.** `1.2.2.2 (d x)^m (a+b x^2+c x^4)^p.mac` e1000,
  `1/(x^2*sqrt(2+2*a-2*(1+a)+b*x^2+c*x^4))`, answers `0` today (wrong). Maxima keeps the constant
  unsimplified (`-(2*(a+1))+2*a+2`). 1_2_2_2 r17 (table position 1768) binds it as `a` and divides by
  it. The legacy 9.1 r3 (`Int[u.*(a+b x^n+c x^j)^p] /; EqQ[j,2n] && EqQ[a,0]`, position 3030) binds
  and accepts it (`%mr_rule_accept`: `%mr_eqQ` reads the constant as 0) but is never reached. With
  `mr_rules_9_1` moved to the head of `mr_rule_table` in a session, rubi answers
  `c*atanh(sqrt(b)*x/sqrt(c*x^4+b*x^2))/(2*b^(3/2)) - sqrt(c*x^4+b*x^2)/(2*b*x^3)` in one step
  (`9_1 r3`), exactly the corpus answer, and `radcan` proves the residual 0 (scratch probe on
  `215918b`'s core). The load order is confirmed on every `Rubi.m` in the clone's history up to
  `58a2225` (2020-05-07), including `a3afeee` (2018-06-25, the one current when the corpus was
  created on 2018-08-03: `LoadRules["9.1"]` right after the utilities). The full-table A/B this
  ticket prescribes is still the gate.
