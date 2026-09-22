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
