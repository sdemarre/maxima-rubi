# test_driver_radcan_fallback.py is red on master and is in no gate

Status: open
Type: bug (verification harness, expectations vs. behaviour)
Filed: 2026-09-20 (found while running the harness guards before the class-6 merge)

## Problem

`python3 test/test_driver_radcan_fallback.py` reports
`Results: 2 passed, 2 failed` on `master` at `2cc114e`. Measured 2026-09-20;
reproduced with `test/corpus_driver.py` stashed to its committed state, so it is
**not** caused by the out-file default change of issue 02.

The four failing assertions (they roll up into 2 named failures):

| entry | test expects | driver classifies |
|---|---|---|
| 1.2.1.4 e764 L973 | a PASS class (`unverified` before the fallback) | `deferred` |
| 1.1.3.8 e541 L698 | `unverified` | `contains-noun` |
| 1.1.3.8 e543 L700 | `unverified` | `contains-noun` |
| 1.1.3.8 e544 L701 | `unverified` | `contains-noun` |

The `[rescue]` check is the one that matters: it exists to prove the
`radcan(rat())` fallback in `zero_chain` rescues an entry that plain
verification cannot close. It now reports the entry never reaching a rule at
all (`deferred`), so **the check no longer exercises the fallback it guards**.
The `[gate-blocks]` check is the negative control — that an elliptic diff is
gated *out* of the fallback and lands as `unverified` — and it too is now
looking at a different outcome.

## It is stale expectations, not a fresh regression

The committed full class-1 record `test/corpus_class1.out` (merged 2026-09-18,
i.e. **before** any class-6 work) already carries exactly these
classifications:

```
13191:contains-noun  t=   4.9s …/1.1.3.8 … e541 L698
13193:contains-noun  t=   3.7s …/1.1.3.8 … e543 L700
13194:contains-noun  t=   3.4s …/1.1.3.8 … e544 L701
20139:deferred       t=   5.2s …/1.2.1.4 … e764 L973
```

So the drift happened at or before 2026-09-18 and went unnoticed because this
guard is **in none of the gate lists** — not in `AGENTS.md`'s per-change gate
set, not in the class-porting runbook's Step-10 checklist. Every other harness
guard is green (`test_driver_parens` 2/0, `test_driver_core_pin` 5/0,
`test_run_records` 43/0, `test_ab_records` 6/0, `test_merge_classes` 2/0,
`test_record_medians` 3/0).

## Why it matters now

The fallback this guard protects is part of the **verification** path
(`zero_chain`), which decides `verified` vs `unverified` for every entry of
every class. Class 4 (22,472 entries) will be measured through it. An unguarded
verification path is the one place where a silent change rewrites an acceptance
figure without any record disagreeing.

## Open questions

1. **Was the `unverified` -> `contains-noun` move progress or regression?**
   `contains-noun` means the package now returns an answer carrying an
   unevaluated integral where it previously returned a complete answer that
   merely failed to verify. That is a rule-behaviour change, and the record A/B
   history between 2026-09-01 and 2026-09-18 should name the commit.
2. **Does the radcan fallback still rescue anything?** If no class-1 entry
   exercises it any more, the guard needs a new witness entry (pick one from
   the current record) or the fallback itself is dead code to be removed.
3. Once re-pointed, **add it to the gate list** in `AGENTS.md` next to
   `test_run_records`, so the next drift is caught by a run rather than by a
   reader.

## Reproduce

```sh
python3 test/test_driver_radcan_fallback.py     # Results: 2 passed, 2 failed
grep -nE "e764 L973|e541 L698" test/corpus_class1.out
```
