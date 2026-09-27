# The generator carries per-rule special cases, and the load order is hand-wired

Status: needs-triage
Type: task (maintainability: regenerating from an updated Rubi)
Filed: 2026-09-27 (survey of `generator/generate_rules.py` during ticket
`.scratch/class-ports/issues/22`)

## Why

The rule files are meant to regenerate from Rubi's `.m` files with no
special casing, so that rules added upstream, or rule bugs fixed there,
come through by regeneration alone. The core translation meets that goal:
`mma_reader.py` feeds the closed token table `translation_table.py`, where
an unknown token is a `GenError`. The static gate
`test/check_generated_rules.py` pins the output. What is left is listed below,
grouped by how each item behaves when the upstream `.m` files change.

**Rule identity is file position.** A handle `(key, n)` is the n-th rule of its
file, so an upstream insertion renumbers every later rule of that file. Every
table below keyed by `(key, n)` then points at a different rule.

## Keyed to one rule

| item | where | on an upstream change |
|---|---|---|
| `CAP_REMAP`: 1_1_1_4 r28/r29 capture renames | `generate_rules.py:95` | **silent**: a renumbering renames another rule's captures |
| 3_5 r10: `ratsimp` wrapped around one cond's `diff` | `generate_rules.py:2139` | loud: `GenError` if the expected text is not found exactly once |
| `ACCEPTED_RISKS`: about 45 reviewed LHS-evaluation risks | `generate_rules.py:1258` | loud: a new or renumbered risk is a `GenError` |
| `BARE_U_BODY_EXCEPTIONS`: six bare-`u_` records kept mid-table (ticket 07) | `generate_rules.py:1384` | loud: a seventh fails the static gate |

`CAP_REMAP` works around `defmatch`'s commutative binding order (2026-08-25).
The matcher substrate replaced `defmatch` with Mathematica-semantics
matching, so it is probably obsolete. It is a pure relabel, harmless as long
as the numbering holds. It is the one silent item.

## File selection (mixing the pinned Rubi with the 2018 corpus)

- `EXTRA_CLASS1`: five class-1 `.m` files that Rubi.m does not load but the
  corpus tests (`generate_rules.py:2354`).
- `NINE_ONE`: the legacy 9.1 file, dropped upstream in 2023-12 (`f7fa0fd`).
- `NINE_ONE_DERIV` / key `9_1d`, and the class-9 skip in `load_class_files`:
  the two "9.1" files would otherwise share a key.

## Counts

`EXPECTED_TOTAL` per class (`configure`). An upstream change fails it
loudly and needs a bump. This is a useful tripwire, not a problem.

## Hand-wired load order

`mr_load_all` in `maxima_rubi.mac` lists the 212 `%mr_load_sibling` calls,
the class order and the tail lists by hand. The generator prints only the
class-1 table line. Upstream reordering or a new file means hand edits here.

## Ticket 22 adds one more if done as measured

The ticket-22 A/B (branch `ticket22-sum-split-first`, 2026-09-27) moves ONE
record, `_mr_rule_9_1_r13`, to the table head by name in `mr_load_all`. The
result was net +190, with one real loss (1.1.1.3 e945). The measurement
records are on the branch: `test/sumfirst_attr_class<N>.out`.
The special-case-free form is ticket 09: load the whole legacy 9.1 file
first, as the 2018 Rubi.m did. That is a different change and needs its own
A/B. `test/ticket22_measure.sh` on the branch can be reused for it.

## Possible moves (not scheduled)

1. Drop `CAP_REMAP` if regenerating without it is byte-identical in effect,
   meaning the matcher suites and Layer A stay green and the corpus A/B shows
   no transitions.
2. Do ticket 22 as ticket 09 (9.1 first as a file), not as a named record.
3. Key the per-rule tables by something stable across renumbering, for example
   the LHS text or a hash of it, so that a stale entry fails loudly.
4. Generate `mr_load_all`'s load list and class order from Rubi.m's
   `LoadRules`, keeping the version-mix additions (`EXTRA_CLASS1`,
   `NINE_ONE`) as the only declared exceptions.

User decision 2026-09-27: recorded, not worked on now.

## Comments
