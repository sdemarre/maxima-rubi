# Dispatch index: stop trying every rule record against every integrand

Status: needs-triage
Type: design + implementation (matcher substrate / dispatcher)
Filed: 2026-09-25 (class-4 port, Step 9)

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
