# Handoff — maxima-rubi, research phase ready (2026-08-17)

For an agent resuming this project with fresh context. Read this file,
then `AGENTS.md`, then the research design spec, then start T1 (and T3's
sample run).

## What this project is

A rule-based symbolic integration package for Maxima in the spirit of
Rubi: declarative integration rules executed by a pattern-matching rule
runner, acceptance-tested against the Rubi Maxima-syntax test corpus.
The user chose the Rubi (rule-based) route over Risch's algorithm after
a scoping session on 2026-08-17. All decisions made so far are recorded
in section 2 of the spec.

**Milestone 1** (planned after research): foundation (pattern-matching
support, rule runner, verification, test harness) + the algebraic-
function class, its Rubi Maxima-syntax test section passing. Standalone
API — no hook into Maxima's builtin `integrate`.

## Current state

- Research-phase design is **approved and committed** (spec section 2
  is the decision record; the user's review verdict: "looking good",
  with the four corrections — mockmma, sympy_rubi, Rubi-5, 5.50
  non-pinning — already folded in).
- Repo bootstrapped on `master` (no remote configured yet, one is
  planned). No implementation code, no reference clones yet.
- All five research tracks (`todo/TODO.md`) are `open`.
- One probe has run: `probes/probe-pattern-facilities.mac` — it
  corrected a wrong scoping assumption about Maxima's pattern
  facilities and found two extra traps (see "Hard-won facts").

## What remains

1. **Execute the research tracks** — the todo items T1–T5, in the
   order given in spec section 5: T1 first; T3's sample corpus run in
   parallel with T1; T2 after T1; T4 after T1 + T2; T5 last. Each
   track: one committed research doc in `docs/`, its claims backed by
   committed re-runnable probes under `probes/` (the AGENTS.md
   measured-claims discipline). T1's first act: clone Rubi into
   `reference/rubi` and pin the 40-digit hash in `todo/TODO.md`. T3's
   first act: the same for `MaximaSyntaxTestSuite` into
   `reference/maxima-syntax-test-suite`.
2. **User reads the five research docs** — the done-when criterion (spec
   section 8); update `todo/TODO.md` statuses as each lands.
3. **New session: the implementation plan.** Invoke the
   `writing-plans` skill to plan milestone 1, then implement via the
   SDD workflow (`subagent-driven-development`), in TDD where the
   corpus sections give natural assertions — diophantine-style, with
   plan + spec artifacts under `docs/superpowers/`.

## Skills to use

- Now (research): no special skill — follow `AGENTS.md` (Maxima
  lookup discipline, measured claims, `build_info()` stamps).
- Next session: `writing-plans`, then `subagent-driven-development`
  and `test-driven-development`.
- The `brainstorming` skill is **done** for the research phase — do
  not re-brainstorm it. If research surfaces a decision that
  contradicts the spec, re-run brainstorming for that decision only.

## Files to read, in order

1. `AGENTS.md` — conventions, Maxima lookup, test protocol, maxims.
2. `docs/superpowers/specs/2026-08-17-maxima-rubi-research-design.md`
   — the research design: tracks, order, method, scope, risks.
3. `todo/TODO.md` and the `todo/t*.md` item files — the work index,
   including the pattern-matching correction (T2 item 0).
4. `probes/probe-pattern-facilities.mac` — the template for how probes
   are written and stamped.

## Reference repositories (not yet cloned)

- Rubi 4 (the rule set):
  https://github.com/RuleBasedIntegration/Rubi — key files
  `Rubi/IntegrationRules/`, `Rubi/IntegrationUtilityFunctions.m`,
  `Rubi/Rubi.m`.
- The corpus (Maxima syntax):
  https://github.com/RuleBasedIntegration/MaximaSyntaxTestSuite
- Rubi 5 (WIP, the if-then-else route — T2 route B, T4):
  https://github.com/RuleBasedIntegration/Rubi-5 — read *Plan for
  Implementing Rubi 5.md* first; `Int111`/`Int121` in `Rubi-5.m` are
  the only implemented functions.
- `sympy/sympy_rubi` — oracle (T3) and translation reference (T4).
- mockmma clones (T2 design sources): `jlapeyre/mixima`
  (Mathematica→Maxima porting tools, Common Lisp) and
  `dubrousky/mockmma`; `stblake/mockmma` is a README-only stub.
- SymPy with a complete Risch implementation + tests is installed
  locally (verification reference only).

## Hard-won facts (do not re-derive)

- Maxima has **no** `match`/`matchfix`/`matchfree` and no `%`/`%%`
  pattern wildcards in the installed build (probed and committed).
  The real machinery is the documented rule system: `matchdeclare`
  (named pattern variables + lambda predicates), `defmatch`,
  `defrule`, `apply1`/`apply2`/`applyb1`, `letsimp`, rule packages —
  manual topic "Functions and Variables for Rules and Patterns".
- Quote trap: in this build `'f(args)` quotes the function symbol
  only — the arguments still evaluate (`f : 99; 'f(1+1)` displays
  `f(2)`). Expect to meet this in every quoted rule pattern.
- Version comes from `build_info()`; the `version` symbol is unbound.
  Build at handoff: `branch_5_49_base_796_g60186bb22_dirty`
  (2026-07-28), SBCL 2.6.7.
- **Do not pin to 5.49.** 5.50 is expected soon (pattern-matching
  speed gains, no new functionality per project owner); re-measure
  baselines when it lands rather than carrying 5.49 numbers over.
- The Maxima manual is the running Maxima: `describe("x", exact)`;
  `?? name`-style inexact search swallows the rest of the line
  (full quirk list in AGENTS.md).
- "Algebraic functions" is the assumed seed class for milestone 1 —
  T1's rule counts confirm or correct it.

## Standing instructions from the user

- **Do not touch `~/src/diophantine`** — it is read-only reference
  material for this project's conventions; the work happens here.
- Default branch `master`; no `main`. A remote is planned, not yet
  configured — do not assume `git push` works.
- No `Co-Authored-By` trailers in commit messages.
- Measured claims only: no claim without a re-runnable probe; stamp
  counts/timings with date + `build_info()`.
- The research ends with a **user read** of the five docs; do not
  start implementing before that and before the new session's plan.
