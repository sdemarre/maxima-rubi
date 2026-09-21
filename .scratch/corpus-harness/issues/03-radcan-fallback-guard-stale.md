# test_driver_radcan_fallback.py is red on master and is in no gate

Status: closed (2026-09-21)
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

## RESOLVED — 2026-09-21

Guard green: `Results: 4 passed, 0 failed`, and it is now IN the gate list
(`AGENTS.md`, the new **Harness guards** block, which lists all seven
`corpus_driver` guards with their counts — the sibling half of this ticket's
question 3).

### Root cause — the guard was testing the wrong thing

Checks 3/4 ran a measured corpus entry end to end and read the DRIVER'S
CLASSIFICATION. That classification is decided by the rule set, and
`corpus_driver.build_text` decides `deferred` and `contains-noun` **before the
zero chain is even constructed**. So an entry that stops reaching the zero-test
silently stops exercising the fallback, while the check goes on asserting a
class name. The fallback itself was never touched.

The commit is **`29d237a`** (2026-09-18, "matcher: the faithful pair — seen-cut
fall-through + give-up rules last", class 1 +3,310), traced by reading the four
entries out of every committed `test/corpus_class1.out` in turn:

| entry | fe7f1c8 → 1620828 | at 29d237a |
|---|---|---|
| 1.1.3.8 e541/e543/e544 | `verified` → `unverified` (88e41fa, the freeof-gate fix — correct, they carry elliptic) | → **`contains-noun`** |
| 1.2.1.4 e764 | `verified` | → **`deferred`** |

**Question 1 answered.** `unverified → contains-noun` is neither progress nor
regression at the record level — both are FAIL classes, so the PASS count did
not move for those three. `1.2.1.4 e764 verified → deferred` IS a PASS→FAIL,
from that same accepted +3,310 commit.

### Question 2 answered — the fallback rescues NOTHING today

Probe `probes/maxima/probe-radcan-fallback-live.{py,run,out}`. Every
`verified`/`expected` entry of the two files the fallback's own docstring names
as its beneficiaries — 1.1.3.8 and 1.2.1.4, **636 entries** — re-answered on the
rules core, each zero-diff run through `zero_chain` WITHOUT the fallback first:

```
  577  chain
   59  chain (gated)
    0  RESCUE
```

Every one closes on the stage chain alone. On today's rules the fallback is not
load-bearing in the files where it was measured to be in 2026-08-28.

**It is NOT being removed on this evidence.** 636 entries of 25,697 is not the
corpus, and the fallback is cheap (it runs only when the chain has already
failed). The escalation, if the question has to be closed outright, is now
runnable — `MR_ZC_FALLBACK=0` drops the stage for a whole run and the record's
`filter:` line states `zc-fallback: off`, so such a record can never be mistaken
for a normal one:

```sh
MR_ZC_FALLBACK=0 python3 test/run_corpus_queue.py "1 Algebraic functions" \
    --prev test/corpus_class1.out --workers 12 --launch
python3 test/ab_records.py test/corpus_class1.out <new-record>
```

Every PASS→FAIL line in that A/B is an entry the fallback rescues.

### The fix — synthetic, frozen witnesses

`zero_chain` gained a `fallback=True` parameter (default; **the emitted text is
byte-identical to `HEAD` for every real caller — verified against
`git show HEAD:` on `zero_chain` and `build_text`, 4-element and 5-element**),
so the guard can run ONE diff both ways instead of inferring the mechanism:

```
rescue      %e^(n*log(x)) - x^n
gate-blocks elliptic_f(x, 1/2)*(%e^(n*log(x)) - x^n)
```

Both are identically zero and depend on neither the rule set nor the corpus.
`n` is deliberately **not** one of the zero chain's sweep parameters
(a b c d e f g h A B C D p) — otherwise the chain's LEADING NUMERIC STAGE
closes any true zero at x=0.35/0.65 and the fallback is never reached. That is
why the first synthetic candidates (`log(x^n)-n*log(x)`, `sqrt(x)sqrt(u)-sqrt(xu)`)
were rejected as witnesses: measured nofb=1, i.e. vacuous.

Measured 2026-09-21, `branch_5_50_base_84_g4204fb669` / SBCL 2.6.7:

| witness | nofb | withfb | gate | ungated radcan |
|---|---|---|---|---|
| rescue | 0 | 1 | true | 0 |
| gate-blocks | 0 | 0 | false | **0** |

The bold 0 is the point of check 4: radcan(rat()) *would* close the gated
witness, so blocking it measures the GATE and not merely a fallback that failed
anyway. The old check asserted only a class name and could not tell those apart.

**Both new checks are anti-vacuous by construction**, and it was mutation-tested:
with `zero_chain` forced to emit the no-fallback chain, `[rescue]` fails with
"the radcan(rat()) fallback no longer closes a diff that nothing else closes".
Each check also fails loudly if its own witness stops exercising the fallback
(`nofb != 0` → "the witness must be replaced") rather than passing silently —
which is exactly how this guard rotted.

Status: **closed.**
