# Dispatch cost: the per-binding condition path, not the record walk

Status: needs-triage
Type: design + implementation (matcher substrate / dispatcher)
Filed: 2026-09-25 (class-4 port, Step 9)
Re-scoped: 2026-09-28, after step 1's profile (see **Comments**). Filed as "dispatch index: stop
trying every rule record against every integrand"; the profile puts the record walk at ~2 % of a
dispatch, so the index is deferred and the ticket now targets the per-binding condition path.
The file name keeps the original slug so existing references still resolve.

## Problem

`maxima_rubi_dispatch.lisp` tries every record of `mr_rule_table`, in table order, until one
answers. The table was 3,514 records when the matcher substrate was specified. It is now **7,776**
on `class-ports` (classes 1–9). Every recursive `Int` call walks it again from the top.

The matcher-substrate spec shipped this on purpose, as phase 1
(`docs/superpowers/specs/2026-09-12-matcher-substrate-design.md` §3.5, "No head index in phase
1"). It estimated about 70 ms per full walk at 3,514 records, from 0.021 ms per match attempt, and
named the fallback: *"a conservative root-head index that may skip records but never reorders
them; it must account for Optionals (`a_.*x^m_.` matches a bare `x`, whose head is not Times)"*.
The P5 median-wall gate did not trip then. At twice the table size and with class 4's recursion
depth, it is worth revisiting.

## Evidence so far (class-ports core `4daae7ac`, 7,776 rules, 2026-09-25)

*Superseded figures:* the current record `test/corpus_class4.out` (rules core at `e4311e6`, merged
2026-09-28) has **946** timeouts, not 5,716, and a median verified entry of 1.4 s cpu, not 5.2 s.
The top families are now 4.2.4.2 (96), 4.1.2.2 (80), 4.5.4.2 (67), 4.1.1.2 (58). The text below is
kept as filed.

- Class 4: **5,716 of 22,472 entries time out** (25 %). The median answered entry takes 5.2 s cpu,
  4,712 answered entries take over 10 s, and 1,501 finish between 20 and 30 s, right under the cap
  (`test/corpus_class4.out` on `class-ports`).
- The timeouts concentrate in the reduction-chain families: 4.2.4.2 has 938, 4.5.4.2 717,
  4.3.2.1 435, 4.3.3.1 410, 4.1.2.2 384 and 4.2.3.1 296. The top ten files hold about 4,000.
  Each chain step lowers m or n by one and calls `Int` again, and each call is a full walk.
- An active trig integrand walks every class 1–3 body record before it reaches the class-4
  bridge at the tail. The bridge deactivates it into the inert form, and each recursive call on
  the inert form starts from the top of the table again.
- Classes 2 and 3 on the same core lose a handful of PASSes to timeouts that already took
  19–29 s on the 3,997-record core (`test/ports_ab_class{2,3}.out`). That fits a per-dispatch
  cost that grows with the table.
- **Not yet measured:** where a dispatch actually spends its time. See step 1.

## Idea

Most records cannot match a given integrand at all. A record whose pattern roots at `Power`
cannot match a `Plus`. A record that needs an inert `%mr_isin` cannot match an integrand with no
inert head. Most of the walk is spent confirming that.

An **index over the pattern trees** can give each integrand the (usually short) list of records
that could possibly match. The walk then tries only those, **in their original table order**.
Load order is priority in this port (Rubi's specificity order, the tiers of ticket 14), so the
index may only skip records, never reorder them.

There are two levels, both order-preserving:

1. **Root-head index** (the spec's fallback). Key each record by the head of its pattern after
   Optional expansion. `a_.*x^m_.` indexes under `Times`, `Power` and the bare symbol. Unknown or
   variable heads (`F_[…]`, bare `u_`) go into an always-tried bucket. Lookup: the integrand's
   root head, merged with the always bucket by handle.
2. **Discrimination net** (the tree we discussed; Rubi 5's if-then-else compilation is the
   extreme form, `docs/rubi-architecture.md` §4). Descend a few levels: root head, argument heads,
   whether `x` occurs. Flat/orderless `Plus`/`Times` need care: index by the multiset of argument
   heads the pattern requires, never by argument position.

The trie is built once at `mr_load_all` from the prepared pattern trees, which `mr-match` already
holds. Lookup is per dispatch.

**Conditions are a separate cost.** An index removes pattern attempts that fail. It cannot remove
records whose pattern matches but whose `/;` condition fails. The substrate also enumerates
flat/Optional bindings, and each enumerated binding is retried against the condition
(`mr_cond_retry`). If the profile shows that cost is the larger one, the remedy is different:
hoisting cheap condition conjuncts such as `FreeQ[…, x]`, `IntegerQ[m]` or `EqQ[…]` so they run
before the expensive ones, or pruning enumeration. Measure before designing.

## Steps

(Steps 2-4 as filed assume an index. After step 1 they are replaced by **Revised steps** in the
comment of 2026-09-28; the original list is kept for the record.)

1. **Profile first.** Instrument a dispatch count and time split. For a few 4.2.4.2 / 4.5.4.2
   entries and a class-1 control: dispatches per entry, records tried per dispatch, how many fail
   at the root, fail deeper in the pattern, match but fail the condition, or misfire, and the time
   in each. Committed probe, alternating sequential runs for any timing.
2. From the profile, pick the level (root-head index, discrimination net, condition hoisting,
   or a combination) and write a short spec amendment to the matcher-substrate design.
3. **Correctness gate:** the index must be invisible to results. For every integrand in a large
   sample (at least the Layer A integrands and a corpus slice from every class), the indexed and
   the linear walk must pick the **same first-answering record**. Put the index behind a switch
   (`mr_dispatch_index`, default false until the gate passes) so both walks can run in one
   process. The matcher regression suite (`test/matcher/run.sh`) stays green.
4. Corpus A/B per class with the switch on vs off: the verdict changes should be timeout → PASS
   only, and every PASS→FAIL is a defect.

## Related

- Matcher substrate spec §3.5 (the deferred head index) and §3.8 (the flat-absorb prune).
- Ticket 16: `9_3 r41` match-enumeration blow-up, which is the condition/enumeration side of the
  same cost.
- Ticket 20: the FreeFactors fix and the 3.1.5 slowdown.
- Ticket 14: the four-pass give-up walk. An index must preserve its tiers.

## Comments

### 2026-09-28 — step 1 done: the time is in the conditions, not the walk

Probes: `probes/dispatch-index/01-profile.{lisp,sh,out}` (per-attempt categories, time split,
two static index oracles with a soundness count) and `02-cond-functions.{sh,out}` (Maxima's
`timer`, self time over all 16,516 user functions and inclusive time over the cond predicates).
Rules core `e4311e6` (7,776 rules), Maxima `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7; every run
sequential, none concurrent. Entries: a class-1 control (1.1.1.2 e1170), three slow-verified
class-4 chain entries (4.2.4.2 e18, 4.5.4.2 e108, 4.1.2.2 e88), and four current class-4
`timeout`s (4.2.4.2 e912, 4.5.4.2 e1328, 4.1.2.2 e1470, e1403).

**The walk is cheap.** 28k-328k attempts per entry, 1.7k-5.9k per dispatch; ~98 % bind nothing,
at 1-2 us each, 60-550 ms per entry in all. A root-head index plus a required-heads filter would
skip ~60 % of those failing attempts and save 40-170 ms of 3-31 s (<= 2 %). Neither oracle ever
skipped a record that went on to bind (0 violations over all eight entries), so the index
remains sound as specified, but it is not worth building now.

**The conditions are ~95 %.** Only 750-5,850 attempts per entry bind, but a flat Times/Plus
pattern enumerates many bindings (4k-33k per entry) and every one runs the condition path.
Inside that path (probe 01, direct timers; entry cpu with the probe loaded):

| entry | cpu (profiled) | bool-check calls | boolean check `%mr_containsBoolean` on the mm list | binding conversion |
|---|---|---|---|---|
| 1.1.1.2 e1170 | 3.3 s | 4,439 | 2.1 s (63 %) | 53 ms |
| 4.2.4.2 e18 | 5.9 s | 6,203 | 3.4 s (58 %) | 81 ms |
| 4.5.4.2 e108 | 5.1 s | 5,906 | 3.0 s (59 %) | 68 ms |
| 4.1.2.2 e88 | 8.8 s | 12,256 | 5.5 s (62 %) | 127 ms |
| 4.2.4.2 e912 (timeout) | 21.5 s | 14,561 | 14.2 s (66 %) | 257 ms |
| 4.5.4.2 e1328 (timeout) | 31.3 s | 33,019 | 18.2 s (58 %) | 383 ms |
| 4.1.2.2 e1470 (timeout) | 19.3 s | 23,913 | 10.0 s (52 %) | 151 ms |
| 4.1.2.2 e1403 (timeout) | 4.9 s | 7,986 | 2.8 s (56 %) | 70 ms |

The probe's own overhead is 2-8 % (each entry also runs unprofiled: e.g. e912 21.1 s plain).

- **The single largest cost is the dispatcher's boolean-leak guard.** `mr-accept` calls
  `mr-contains-boolean-p` on every binding list before the condition, which runs the interpreted
  Maxima walk `%mr_containsBoolean` (`maxima_rubi_utils.mac`) — one Maxima call per node,
  `string()` on every atom, nine `op(e) = ...` tests per node. Probe 02: 611k calls on e88, 1.5M
  on e912; ~0.4-1 ms per binding list.
- **Second: `geteqR`**, the binding lookup that opens every generated condition (and repl):
  250k calls / ~1.5 s self on e88 (timer-inflated).
- **Then the predicates themselves**, inclusive: LinearQ, PolyQ, PolyDegQ, DerivativeDivides,
  BinomialQ — 1-3 s on e88, ~6 s on e912. They are called by the generic `u^m v^p w^q` records
  (1_4_2 r3/r9/r15/r17, 1_1_1_4 r47, 1_3_4 r4) and 9_3 r13/r8, whose flat patterns bind a
  product of several factors in many ways.
- Ruled out: the EqQ symbolic zero test (e88 8.7 s with `mr_eqq_symbolic` true, 8.6 s false);
  tree->Maxima conversion of bindings (1-2 %).

**Side finding — not every `timeout` is rubi.** 4.1.2.2 e1403 is `timeout` in the current record
and at 100 s in the previous record's re-check, yet `rubi` answers it in 4.4 s cpu here; the
corpus driver on the same core still reads `timeout t=30.1s`. Its time goes to the harness's
verification, not to the rules. How many of the 946 are like that is unmeasured (a rubi-only
re-run of the timeout class would tell; ~40 min at 12 workers).

### Revised steps (proposed 2026-09-28, for triage)

1. **Native boolean check.** Reimplement `mr-contains-boolean-p` as a Lisp walk over the Maxima
   form with `%mr_containsBoolean`'s exact semantics (atoms whose printed name is `true`/`false`,
   the control heads opaque, a negation's part 1 only; an error still counts as a hit). Unit
   tests against the Maxima version on its documented witnesses, then Layer A, then a
   per-class corpus A/B: results must be identical entry for entry, timeouts may only improve.
   Alternative worth weighing: whether the pre-condition check on bound values is needed at all
   (bindings are sub-trees of the integrand), keeping only the post-repl check.
2. **`geteqR` in Lisp**, same gate.
3. **Re-profile** (probes 01/02). Then decide between predicate memoisation across the bindings
   of one attempt (the `u, v, w` permutations recompute the same LinearQ on the same factors),
   binding de-duplication for symmetric slots, and ticket 16's enumeration prune.
4. **Separate harness ticket** for verification-bound timeouts (e1403): measure the rubi-only
   share of the timeout class first.
5. The dispatch index (the original steps 2-4) stays deferred until the condition path is
   fixed; re-measure its share then.

### 2026-09-28 — revised step 1 done: native boolean check, `f80724a`

Full-corpus A/B, `test/boolnative_measure.sh` (queue runner, 24 workers, 30 s cpu cap) on
`f80724a`'s core against the promoted baselines `test/corpus_class<N>.out` (8de7080), every
transition re-run at 12 workers on both cores (`test/boolnative_attr_class<N>.out`):

| class | PASS before -> after | P->F | F->P | F->P credited to the change (FIX) | F->P drift |
|---|---|---|---|---|---|
| 1 | 23,672 -> 23,803 | 0 | 131 | 89 | 42 |
| 2 | 871 -> 871 | 0 | 0 | — | — |
| 3 | 2,619 -> 2,641 | 0 | 22 | 7 | 15 |
| 4 | 20,168 -> 20,530 | 0 | 362 | 112 | 250 |
| 5 | 3,787 -> 3,820 | 0 | 33 | 19 | 14 |
| 6 | 4,398 -> 4,418 | 1 | 21 | 7 | 14 |
| 7 | 5,557 -> 5,598 | 0 | 41 | 21 | 20 |
| 8 | 1,716 -> 1,716 | 0 | 0 | — | — |

62,788 -> 63,397 PASS (+609). Every F->P is a `timeout` that now finishes. FIX = at 12 workers
the old core still fails and the new one passes. Drift = both cores pass at 12 workers: these are
borderline entries that the faster code gets under the cap at 24 workers. The one P->F, 6.1.3
e71 (`expected` 29.3 s -> `timeout` 30.0 s), passes on both cores at 12 workers, so it is noise at
the cap, not a defect. Class 2 total cpu 1,203 s -> 819 s; median time of PASS entries >= 1 s
halved.

### 2026-09-28 — revised step 2 done: native geteqR, `259fc62`

Differential gate (probe 04): 6,473,833 real calls, 0 mismatches (same internal object). Probe 01
on the step-1 core, then on this one (`01-profile.step1.out` / `.step2.out`), plain cpu: e1170
1.14 -> 0.69 s, e18 2.15 -> 1.49, e88 3.00 -> 1.89, e912 6.79 -> 5.25, e1328 11.9 -> 8.37, e1470
8.90 -> 4.90 (the pre-step-1 figures were 3.19 / 5.52 / 8.44 / 21.1 / 30.2 / 18.8). On e88 the
boolean check is now 14 ms (from 5.4 s) and the condition path 1.8 s of 2.2 s, spent in the
predicates. The top rules are still the `u^m v^p w^q` family and 9_3 r8/r13, which is revised
step 3.

Full-corpus A/B, `test/geteqr_measure.sh`, against step 1's records
`test/corpus_class<N>.boolnative.out`, transitions re-run on the step-1 and step-2 cores:
PASS 63,397 -> 63,497 (+100). Class 1 +27 (30 F->P, 3 P->F), 4 +64 (65/1), 5 +3, 6 +1, 7 +1,
8 +4, 2 and 3 unchanged. 43 F->P credited to the change at 12 workers, 61 drift. The four P->F
(1.1.3.8 e584, 1.2.1.4 e765, 1.2.2.4 e224 `expected` at 28-29 s; 4.3.4.2 e121 `verified` at
30.0 s) sit at the cap and pass on both cores at 12 workers: noise.

Cumulative, steps 1+2 against the promoted baselines: 62,788 -> 63,497 PASS (+709).
