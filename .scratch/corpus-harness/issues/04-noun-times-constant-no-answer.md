# The driver misses a no-answer that is `c * unintegrable(...)`

Status: open
Type: bug (verification harness, classification)
Filed: 2026-09-21 (inert-trig substrate, Task 10 fix round 1)

## Problem

For an entry whose expected answer is `Unintegrable`/`CannotIntegrate`,
`corpus_driver.build_text` gives the PASS class `no-answer` only when the TOP-LEVEL
operator of the answer is the `unintegrable`/`integrate` noun. An answer of the form
`c * 'unintegrable[g, x]` with `c` free of x is the same no-answer, but it reads
`contains-noun` (FAIL).

## Where it shows

Porting 4.7.5 r72 (commit `23855a8`) brought 92 of the 114 class-6 `no-answer` entries
back. The other **22** now answer `c*'unintegrable[g,x]` with c ∈ {-1, %i, -%i}, and
c·g equals the integrand in value (measured on all 22). How they get that shape:
DeactivateTrig introduces the constant, then Rubi's own pull-out rules (`9_1` r11,
`1_4_1` r18) move it outside the nested Int before r72 gives up. Rubi would produce the
same shape; whether Mathematica's auto-simplification folds c back in is unverified.
Files: 6.1.1 ×7, 6.3.1 ×6, 6.4.1 ×6, 6.6.1 ×3. Record: the committed
`test/corpus_class6.inert-substrate.out` (the branch's final class-6 run, fix wave
of 2026-09-21; the same 22 entries as the Task-10 fix-round-1 run it supersedes);
list them with
`python3 test/ab_records.py test/corpus_class6.out test/corpus_class6.inert-substrate.out`
(the 22 `no-answer -> contains-noun` lines of its PASS->FAIL block).

## Fix direction

Before the noun test, strip an x-free multiplicative constant from the answer. This is
a HARNESS change: it can move verdicts in every class, so it needs a guard test (in the
AGENTS.md Harness guards block) and an A/B of classes 1/2/3/6 before acceptance.
