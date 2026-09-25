# Class 2's 2_3 r58/r65 emit a two-argument expand(u, x) that errors: both records always misfire

Status: fixed (2026-09-25, branch `class-ports-fixes`)
Type: bug (two class-2 records can never answer)
Filed: 2026-09-25 (class-4 port, Step 4 — ticket 05)

## The finding

Rubi's `Expand[u, x]` (expand the parts of u that contain x) is translated
by the RENAME row `"Expand": "expand"` to Maxima's `expand(u, x)`. Maxima's
`expand` has a 1- and a 3-argument form (`expand(expr, maxposex, maxnegex)`);
the 2-argument call is an error, `expand: expop must be a nonnegative
integer; found: x` (probes/maxima/probe-class4-expand-two-arg.out E1, build
`branch_5_50_base_84_g4204fb669`). A repl error is a misfire to the
dispatcher, so the record declines every time it matches.

Class 4 met it first on 4.1.1.1 r1 (`Int[sin^n]`, n odd — the Cos
substitution) and fixed it for class 4 with a per-class row
(`CLASS_RENAME[4]`: `Expand -> %mr_expand`, which drops the pattern argument;
probe E2, E4).

**Class 2 carries the same emission, still:** `rules/class2/2_3.mac` r58
(`Int[G^(h(f+gx)) (a+b F^(e(c+dx)))^p]`) and r65 (the `H^(t(r+sx))` variant):
`mr_int(expand(<integrand>, x), x)`. Probe E3: r58 on `2^x (1+3^x)^2` prints
the expop error and answers `false`. Every other class emits no 2-argument
`expand` (grep of rules/, 2026-09-25: class 2 has these two, classes
1/3/5/6/7/8/9 none).

## Fix (not applied — it moves an accepted class's committed text)

Add `2: {"Expand": "%mr_expand"}` to `CLASS_RENAME` (or make `%mr_expand` the
shared RENAME row) and regenerate class 2; the P3 gate
(`test/check_generated_rules.py`) compares class 2 with the P0 base
byte-for-byte except a closed exception list, so the two repls need an
exception entry, and class 2's record should be re-measured (the two records
become live). Left for a decision because it changes accepted class-2
output.

## Resolution (2026-09-25, branch `class-ports-fixes`)

Made general rather than per class: the emitter (`generator/generate_rules.py` `emit_head`) maps EVERY
two-argument `Expand[u, x]` to `%mr_expand(u, x)`; a one-argument `Expand` keeps the RENAME row
`expand`. `CLASS_RENAME[4]` (which mapped every class-4 `Expand`, all three of them two-argument) is
gone, and `CLASS_RENAME` is empty. Regenerating every class (1-9, `--rewrites`) changes only
`rules/class2/2_3.mac` r58/r65; class 4's three sites are byte-identical.

- P3 static gate: one more closed exception, `undo_expand2` (`%mr_expand(` -> `expand(` on the new
  body), 2 sites pinned. `Results: 28 passed, 0 failed`.
- Layer A `test_expand_two_arg` (7 checks, 3 RED on the old `2_3.mac`): r58 accepts `2^x (1+3^x)^2` and
  its repl now answers (it errored with the expop message), derivative checked at two points; likewise
  r65 on `2^x 5^x (1+3^x)^2`; `rubi` end to end on a `2_1 + 2_3` table. Layer A 1527 -> 1534.
- Class 2's record re-measure is still owed; a slice A/B is `probes/corpus/27-class-ports-fixes-slice-ab`.
