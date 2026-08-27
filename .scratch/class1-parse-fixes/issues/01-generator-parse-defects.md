# Generator parse defects: 6 broken class-1 files, 5 root causes

Status: resolved
Claimed: 2026-08-22 (implementation session resuming the paused SDD plan)
Resolved: 2026-08-22 (same session; all five root causes fixed in the
generator, regenerated, all acceptance gates green)
Blocks: Task 9 (full class-1 run + divergence loop) — a full load stops at
the first parse-broken file (probe-parse-sweep.run header).

## What

`sh probes/load_wall/probe-parse-sweep.run` reports 6 of 67 generated
class-1 files parse-broken (Maxima 5.50.0, 2026-08-22):

| file | first error |
|---|---|
| `1_1_3_1` | `= is not a prefix operator` (r11) |
| `1_1_3_2` | `Missing )` (r35) |
| `1_1_3_7` | `= is not a prefix operator` (r5) |
| `1_2_1_1` | `Found LOGICAL expression where ALGEBRAIC expression expected` (r16) |
| `1_2_3_4` | `_mr_1_2_3_4_r57_n is not an infix operator` (r57) |
| `1_4_3` | `sqrt is not an infix operator` (r16) |

The sweep stops at the FIRST error per file, so the broken set understates
the damage. Root-cause work (this session) found **five** distinct
generator defects in `generator/generate_class1.py`; the true affected
counts are much larger than 6 files.

## Root causes (each measured, each with a repro)

### RC1 — `==` passes through untranslated (4 rules)

This build's parser rejects `==` in EVERY position — even `1 == 1` is
"incorrect syntax: = is not a prefix operator" (measured 2026-08-22,
Maxima 5.50.0). The manual entry for `=` (describe("=", exact)) states
`is(a = b)` evaluates to `true`/`false`, **never unknown** — syntactic
equality, i.e. exactly the semantics `==` had in classic Maxima and that
Rubi's source uses it for. Value-verified: `is(2 = 1+1)`→true,
`is(x = 2)`→false, `is((x+1)^2 = x^2+2*x+1)`→false; and `n = 2 and q`
associates as `(n = 2) and q` with correct values (probe
/tmp/opencode/probe-eq-assoc.mac, 2026-08-22).
Source sites: `1.1.3.1` r11 (`n == 2` twice), `1.1.3.7` r5 (`q == n - 1`),
r38 (`Expon[Pq, x] == n - 1`).
**Fix:** the atom walk emits `=` for a source `==`.
Forward note: the negation form in this build is `#` (manual), not `#=`;
no class-1 source uses `#=`, so no mapping is added until one appears.

### RC2 — `;` in With/Module bodies (185 rules)

Rubi's Module/With body statement separator is `;`; Maxima's `block`
separates statements with `,`. Measured: `block([a], a : 1; a + 1)` →
"incorrect syntax: Missing )" at the `;` (the misleading message is the
sweep's 1_1_3_2 r35 error, col 373 = the `;`); `block([a], a : 1, a + 1)`
works. The Module/With handler emits the translated body verbatim, so the
`;` survives. Census of all 67 files (counting only a `;` NOT preceded by
`/` — an earlier census pass counted the `/;` of inner conditionals and
over-reported 185): exactly **8 rules** carry a statement `;`, all the
same Module-body shape `u = Int[...]; <expr>`: 1.1.3.1 r13/r14/r21/r22,
1.1.3.2 r35/r36/r37/r38. The sweep only saw r35 because each file dies
at its first error.
**Fix:** in the handler, convert top-level `;` in the body to `,` — the
inner `/;` conditional is split off first by the handler, so its `;`
never reaches the converter; depth-aware over `()`/`[]`/`{}`.

### RC3 — raw comparison chains (2 rules)

Rubi source may write `a <= b <= c` as raw infix (not the `LtQ[a,b,c]`
head, which the 3-arg CMP_OPS path already expands). Maxima has no
chained comparison: `3 <= denom(p) <= 4` → "Found LOGICAL expression
where ALGEBRAIC expression expected" (measured). Rubi's own chain
semantics are conjunctive (`LtQ[u,v,w] := LtQ[u,v] && LtQ[v,w]`, Rubi
:468-:470), so the expansion is `is(a <= b) and is(b <= c)` — the
generator's existing 3-arg CMP_OPS convention.
Source sites: `1.2.1.1` r16 (cond `3 <= Denominator[p] <= 4`), r17 (rhs).
**Fix:** a post-join pass in `translate_atom` expands any run of ≥2
top-level relational operators (at any bracket depth) into the
`is()`-wrapped conjunction; a lone comparison is untouched.

### RC4 — Mathematica whitespace juxtaposition (≈15 rules)

In the Rubi source, whitespace between two expressions is implicit
multiplication; Maxima requires `*`. Measured: `2 n` → "n is not an
infix operator", `f sqrt(v)` → "sqrt is not an infix operator".
`_join_tokens` preserves source spacing as-is for space-separated atoms.
True sites in class 1 (whitespace form; a no-space census found none —
earlier `]x`/`](` hits were census artifacts from cond+rhs
concatenation): `2 n` (1.2.3.4 r57/r58), `f Sqrt[v]` in the lhs pattern
(1.4.3 r16), `(f*x)^m (d+e*x^n)^q` (1.2.2.4 r19/r20, 1.2.3.4
r27/r28/r79/r80), `n (2*p + 1)` (1.2.3.4 r41-r44).
**Fix:** in `_join_tokens`, a whitespace-only gap between two
expression-atomic tokens (digit / identifier char / `)` / `]` / `%` on
either end) emits `*`; spaces adjacent to operators/keywords are
preserved as before. No-space gluing rules (F6) are unchanged.

### RC5 — `var = expr` body statements (8 rules, semantic)

Rubi Module/With bodies assign with `=` (Mathematica Set); Maxima block
statements assign with `:`. Measured: `block([u], u = 5, u)` → `u`
(unbound global — the `=` statement values to a discarded equation);
`block([u], u : 5, u)` → 5. Not a parse error, so the sweep cannot see
it — but the 8 affected rules would compute on an unbound local.
Affected rules: the SAME 8 as RC2 (1.1.3.1 r13/r14/r21/r22,
1.1.3.2 r35/r36/r37/r38, all `u = Int[...]`) — RC2 and RC5 are one
defect class (Rubi statement syntax passed through untranslated) on one
set of bodies. Note: a source body statement `u == v` would be
RC1-converted to `u = v` and then mis-converted to `u : v`; no such
body exists in class 1 (a bare comparison as a whole statement is not a
Rubi idiom).
**Fix:** in the handler, a top-level body statement `ident = expr`
(`=` not followed by `=`) becomes `ident : expr`.

## Acceptance (the red/green gate)

1. `sh probes/load_wall/probe-parse-sweep.run` → **0 parse-fail**
   (currently 6).
2. `sh probes/load_wall/probe-load-curve.run` → clean 67-file run, no
   "skip" lines, all 2,710 rules measured directly (the curve probe
   asserts the total and the `maxima_rubi.mac` load order).
3. `maxima --very-quiet -X "--tls-limit 100000" -b test_maxima_rubi.mac`
   → `Results: 71 passed, 0 failed` (baseline 2026-08-22).
4. Regenerate the whole class (`python3 generator/generate_class1.py` →
   `TOTAL: 2710 rules — OK`); the diff vs the committed `rules/class1/`
   touches ONLY the five defect patterns — the 61 currently-clean files
   contain none of the patterns (a parse error would have surfaced them),
   so any other changed line is a regression to be explained.

## Out of scope

- The noun-laden C-tier state (rules declining or firing with pending
  `%mr_*`/`mr_*` nouns until Tasks 7-8 port them) — pre-existing and
  deliberate.
- The three pending Task 6 review fixes (decline wording, census
  hardening, `%mr_polyDegPowerQ` exact degree) — separate work item.
- `#=` → `#` (no class-1 occurrence; RC1 forward note).

## Answer (2026-08-22)

All five root causes fixed in `generator/generate_class1.py`, class
regenerated, all four acceptance gates green:

- RC1: the atom walk emits `=` for a source `==` (FIX P1 comment).
- RC2/RC5: new `_maxima_stmts` (top-level `;`→`,`; top-level body
  `v = e`→`v : e`) applied in the With/Module handler after the inner
  `/;` split (FIX P2/P5 comment).
- RC3: new `_expand_chains` at the end of `translate_atom` — a run of ≥2
  relational ops at any bracket depth becomes the `is()`-wrapped
  conjunction; `;`/`,`/`and`/`or` terminate a run (FIX P3 comment).
- RC4: new `_gap_join` consulted by `_join_tokens` at every whitespace
  gap — a gap between two expression terminals becomes `*`, except
  `)`/`]`-`(` (the only legal spaced juxtaposition); word-guarded on both
  sides. The F6 no-space branches `x(…` and `…)ident` now also emit `*`
  — measured this session: the spaced form `x (…)` is a SILENT noun call
  in Maxima 5.50.0 (`x (y)` reads `x(y)`), so the old space insertion
  was semantically wrong, not conservative (FIX P4 comment).

Regeneration diff: exactly 7 files / 28 rule lines changed
(1.1.3.1, 1.1.3.2, 1.1.3.7, 1.2.1.1, 1.2.2.4, 1.2.3.4, 1.4.3); the other
60 files byte-identical. Gates (all re-run after the final regeneration,
Maxima 5.50.0, 2026-08-22):

1. `sh probes/load_wall/probe-parse-sweep.run` → `sweep: 67 files, 0
   parse-fail, 67 clean` (was 6 fails).
2. `sh probes/load_wall/probe-load-curve.run` → `VERDICT: curve clean on
   this build` (2,710 rules, c = 9.35 vars/rule, no broken files).
3. `maxima --very-quiet -X "--tls-limit 100000" -b test_maxima_rubi.mac`
   → `Results: 71 passed, 0 failed` (baseline preserved).
4. Diff review: only the five defect patterns appear.
