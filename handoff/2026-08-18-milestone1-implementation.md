# Handoff — maxima-rubi, milestone 1 implementation

Session type: **implementation session with the user** (research phase T1–T5
is complete; this session builds the class-1 algebraic package per the
research docs). Date written: 2026-08-18.

## Where everything lives

- Repo: `/home/serge/src/maxima-rubi` (branch `master`; **no remote configured
  — no `git push`**; never create a `main`).
- Read first: `AGENTS.md` (project rules, Maxima manual lookup, probe
  discipline), then the five research docs:
  - `docs/rubi-architecture.md` (T1) — rule grammar, dispatch order
  - `docs/pattern-matching-feasibility.md` (T2) — route-A matcher matrix,
    §3 **measured-semantics trap catalog** (the code lives under these),
    §4 runner contract, §5 cost, N/D/M go/no-go
  - `docs/corpus-baseline.md` (T3) — yardstick + harness mechanics
  - `docs/rule-translation.md` (T4) — generated format, shim/predicate
    inventory, §6 build-drift caveat
  - `docs/package-architecture.md` (T5) — **the spec**: API, layout,
    two-layer harness, ten house rules, open measurements
- Working state per track: `todo/TODO.md` + `todo/t{1..5}-*.md`
  (all done + evidence).
- Reference clones (gitignored): `reference/rubi` @ 61e9c18ea…,
  `reference/maxima-syntax-test-suite` @ 60295e21c…, `reference/rubi-5`
  @ 37a71d650… (full hashes in `todo/TODO.md`).
- Read-only house mould: `~/src/diophantine` (loader/witness idiom,
  `Results:` protocol — do **not** modify).

## Repo/commit state

- Last commits (newest first): `edc9a05` T3 baseline, `8fb598b` T5,
  `d8abbb4` T4, `6135a63` T2, `9b026d1` T1, then research groundwork.
- Long-standing uncommitted WIP, left untouched since ~2026-08-17: the
  `M AGENTS.md` working copy adds an "## Agent skills" section (referencing
  `docs/agents/{issue-tracker,triage-labels,domain}.md`, `.scratch/`, and
  `CONTEXT.md`+`docs/adr/` — the latter three do not exist yet), and
  `docs/agents/` is untracked. It is in-progress agent-setup the user is
  driving in parallel with the research phase; there is no written rule
  against committing it — ask the user before staging anything here.
- House rules: no `Co-Authored-By` trailers; commit in logical units,
  stage only intended files; every non-trivial claim cites a re-runnable
  probe under `probes/` stamped with `build_info()`.

## Build (measurements are build-specific)

`branch_5_49_base_796_g60186bb22_dirty` (2026-07-28, SBCL 2.6.7) at
`/home/serge/local/bin/maxima`; 24-core box. **5.50 is expected soon** —
it adds matcher *speed*, not functionality; on upgrade re-run the probes
(`sh probes/.../*.run`) and re-measure rather than carrying baselines.
**Build drift** (T4 §6): this binary lacks staples its own manual
documents (`coefficient`, `maxexpt`, inverse hyperbolics, elliptic*,
`simplify`, `together`, …) — shims must take `%mr_`-prefixed names (T5
house rule 7), never the native name.

## The design as decided (do not relitigate without the user)

- **API**: `rubi(f, x)` → antiderivative, else Maxima's own
  `integrate(f, x)` noun (the faithful Rubi fall-through). `rubi_verbose`
  flag. Recursion = plain `rubi(smaller, x)` evaluation ("the runner does
  not loop", T2 §4) + depth cap (value open).
- **Layout** (flat, diophantine-shaped): `maxima_rubi.mac` (loader,
  `%mr_load_sibling` witness idiom) + `maxima_rubi_utils.mac` (runner +
  shims + ported predicates) + `rules/class1/<file>.mac` (generator-
  emitted, one per Rubi `.m`, `[pattern, cond, repl]` triples, unique
  `_mr_<file>_r<n>` names, rule identity `<file> r<n>` for verbose) +
  `test_maxima_rubi.mac`. No `.lisp` in milestone 1 (0.007 ms/match
  measurement says Maxima-level is fine).
- **Harness, two layers**: (A) `maxima --very-quiet -b
  test_maxima_rubi.mac`, diophantine `Results: n passed, m failed`
  protocol (no Results line = failure); (B) the T3 per-integral-subprocess
  corpus driver, package in place of `integrate`, same CLASS vocabulary
  (T3 §2 / T5 §3).
- **Generation** (T4): all 2,710 loaded class-1 rules generate; 74.9 %
  have AUTO-translatable conditions; 37 Rubi predicates (PolyQ, IntBinomialQ,
  …) get ported once into utils with unit probes; ~15 shims for unbound
  names; the 122-token condition/replacement inventory is the seam table.

## The yardstick (T3, 2026-08-18, this build)

Class 1 = 40 corpus files, **25,697 entries**. Today's `integrate`:
12,798 (49.8 %) verified/expected · 8,297 no-answer (incl. 31/31 agreement
on the corpus's non-integrable entries) · 3,102 unverified · 1,260
timeout · 240 error · 0 unexpected. Canonical record:
`probes/corpus/probe-integrate-sample.out` (merged + completeness-
verified by `probes/corpus/merge-shards.py`). Re-run recipe (18 parallel
workers, 2.17 h wall for 12.03 h serial-eq.) is in T3 §3.4 — the planner
rules (partial parts get single-file ranges; whole-file chains cap at max
length; driver-simulation assert before launch) matter, because the
driver's `per-file` cap applies to **every** file in its range.

## Open measurements to make early (T5 §5)

1. **`defmatch` load wall** for 2,710 rules (+ the D-fan-out tail) — not
   measured yet; first build must measure it (if load > ~1 min, the
   optional-argument fan-out moves N-only).
2. Recursion cap value (candidate 16) vs corpus-observed recursion.
3. Zero-chain strengthening loop against the 3,102 unverified (T4 §4) —
   chain is `ratsimp → ratsimp∘expand → factor → ratsimp∘factor`
   (`simplify`/`together` unbound here).
4. 30 s per-integral cap (arbitrary; p95 = 24.2 s in the baseline).

## Measured traps the implementation must respect (T2 §3 + T3 §3.3)

- `is()` is three-valued (`unknown`); value-position comparisons do not
  evaluate; guards are value-carrying `if…else`; no `filter` (noun);
  `block` returns its last expression; capture vars bind globally — fresh
  never-killed names per rule; `defmatch` never from a killed name.
- Harness template names must be `mr_`/`MR_`-prefixed (corpus `f`/`r`
  collision corrupted a full run — T3 §3.3.2); noun detection is
  `is(string(op(r)) = "integrate")` (part/length and quoted-equality
  detectors are both unsound; T3 §3.3.3); corpus noun expectations are
  call-form `Unintegrable(…)`/`CannotIntegrate(…)`.
- `:lisp` in a batch reads one line; multi-line Lisp = sibling `.lisp` +
  `load`.

## Suggested skills for this session

- `writing-plans` — before touching code: turn T4+T5 into a stepwise
  implementation plan (per the project's issue-tracker convention, specs
  live under `.scratch/<feature-slug>/`).
- `test-driven-development` / `tdd` — each shim/predicate and the runner
  are unit-probed first (the T4 unit-probe requirement).
- `subagent-driven-development` or `executing-plans` — for executing the
  plan with review checkpoints.
- `verification-before-completion` — before any "done" claim: run the
  Layer-A suite (read the `Results:` line) and spot-check Layer B.
- `code-review` / `requesting-code-review` — at the end of a milestone.
- `systematic-debugging` / `diagnosing-bugs` — if a rule family or the
  matcher misbehaves (expect the T2 trap catalog to catch most first).

## Suggested first steps

1. Read `AGENTS.md`, T5, T4 §3–4, T2 §3 (≈30 min), skim the rest.
2. Write the milestone-1 plan (writing-plans); first tickets plausibly:
   utils skeleton + witness loader + Layer-A harness skeleton (Results
   protocol) → measure `defmatch` load wall (open item 1) → port the 37
   predicates with unit probes → generator for one small rule file →
   first Layer-B smoke run against 1.1.1.2 (1,917 entries, mostly fast).
3. Keep the probe discipline: every new measured fact gets a probe +
   date + build stamp before it goes into a doc.
