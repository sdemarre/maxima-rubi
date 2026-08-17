# maxima-rubi research phase — design

Date: 2026-08-17
Status: approved in design discussion with the user, 2026-08-17
Next step after this spec: user review of this document, then the
`writing-plans` skill plans the implementation of milestone 1.

## 1. What the project is

A rule-based symbolic integration package for Maxima in the spirit of
Rubi (rule-based integration, `RuleBasedIntegration/Rubi`, Rubi 4):
declarative if-then integration rules, executed by a pattern-matching
rule runner, held to the Rubi Maxima-syntax test corpus as the
acceptance standard.

**Milestone 1** — the first implementation milestone, planned after this
research phase: **foundation + the algebraic-function class**. That is:
pattern-matching support, a rule runner, verification, and a test
harness, plus the ported algebraic-function rules, with that class's
Rubi Maxima-syntax test section passing as the acceptance target.
Extending to a second function class must then be a documented,
repeatable process. The long-term goal (a full port) is assumed but
out of milestone 1's scope.

## 2. Decisions already made (with the user, 2026-08-17)

- **Rule-based (Rubi), not Risch's algorithm.** The Risch target was
  evaluated during scoping and set aside: it is a deep mathematical
  implementation (Maxima's in-tree `src/risch.lisp` covers only the
  transcendental case; the algebraic case is the real work), while
  Rubi offers a bounded, test-corpus-backed port whose hardest
  engineering piece — real pattern matching — is also the most
  reusable payoff.
- **The decision weighed:** utility for Maxima, tractability /
  finishability, and reusable payoff. Depth of intellectual challenge
  was explicitly *not* a deciding criterion.
- **Project name:** `maxima-rubi` (the original name `maxima-risch`
  died with the pivot; the directory was never created under it).
- **Standalone API.** The package never touches or hooks Maxima's
  builtin `integrate`. It exposes its own function. An integration
  hook is a documented follow-up, not part of milestone 1.
- **Inherit the `~/src/diophantine` conventions**, with these
  deliberate differences:
  - `AGENTS.md` instead of `CLAUDE.md` (multi-agent convention).
  - The TODO discipline is reorganised: `todo/TODO.md` holds the short
    index entries (status + link); each item has its own
    `todo/<id>-<slug>.md` file carrying the questions-to-answer and
    the evidence; items may reference each other.
  - A git remote is **planned but not yet configured** — "no remote"
    is not a rule for this project, only its current state.
  - The measured-claims culture and the SDD workflow for the
    implementation phase are inherited wholesale.

## 3. What exists (context, measured 2026-08-17)

- The installed Maxima is a 5.49-series development build
  (`branch_5_49_base_138_ge1dff5e3d`), SBCL.
- Maxima's in-tree `src/risch.lisp` (1424 lines) implements the
  *transcendental* Risch case; the manual states that the algebraic
  case has not been implemented. Recorded for the record; out of scope
  for this project.
- Maxima has limited pattern facilities: `match`, `matchfix`,
  `matchfree` with `%` / `%%` wildcards, and `matchdeclare` for
  function-definition argument patterns. Whether these cover Rubi's
  needs is the central open question (T2). Working hypothesis: they
  do not.
- Rubi 4 (repo pushed 2024): `Rubi/IntegrationRules/` (the .m rule
  files, organised per function class), `Rubi/IntegrationUtilityFunctions.m`
  (254 KB of support machinery), `Rubi/Rubi.m` (driver). Rubi is
  rule-based — "an if-then-else decision tree" per its own description —
  and is **not** a Risch implementation.
- `RuleBasedIntegration/MaximaSyntaxTestSuite`: the Rubi test corpus
  translated into Maxima syntax, organised as `0 Independent test
  suites`, then one folder per function class (1 algebraic, 2
  exponentials, 3 logarithms, 4 trig, 5 inverse trig, 6 hyperbolic,
  7 inverse hyperbolic, 8 special functions).
- SymPy (with a complete Risch implementation and test suite) is
  installed locally. It has fallen off the critical path; it stays
  available as a reference for integration verification.

## 4. Research phase scope

Five tracks. Each is one `todo/` item with its own file and produces
one committed research doc, flat in `docs/`.

### T1 — Rubi anatomy → `docs/rubi-architecture.md`

- How `Rubi.m` dispatches rules: the `Int` head, rule order, show-steps.
- The rule grammar: what a rule is (pattern / condition / replacement),
  with concrete examples drawn from each function class.
- Rule counts per function class (measured on the pinned clone).
  Confirms or corrects "algebraic functions" as the milestone-1 seed class.
- The utility-function inventory: every helper the rules call, ranked by
  frequency, with a rough porting-cost estimate per function. This is the
  support-function gap list.
- License text verbatim + what a port must carry (attribution etc.).
- How Rubi verifies its own answers (derivative check? simplification?).

### T2 — Pattern matching in Maxima → `docs/pattern-matching-feasibility.md`

- Committed probes of the builtins: `match`, `matchfix`, `matchfree`,
  `matchdeclare`, `%`, `%%`, exercised against representative Rubi
  pattern shapes (from T1's grammar) — named subexpression capture,
  multiple wildcards, guarded conditions, whole-expression vs
  subexpression matching.
- Per-feature verdicts: `builtin ok` / `extendable` / `must build`.
- A design sketch of the matcher to build (Lisp-level is the working
  hypothesis — Maxima's expression trees are Lisp data), with its
  semantics contract.
- Coverage: what fraction of the *actual* first-class patterns are
  expressible with builtins + the sketch.
- Go/no-go and cost of the matcher as part of milestone 1.

### T3 — Corpus and baseline → `docs/corpus-baseline.md`

- The `MaximaSyntaxTestSuite` format: file layout, expected-answer
  convention, how "no elementary answer" is marked, what normalization
  comparison allows. Clone the repo and pin the commit in `todo/TODO.md`.
- A baseline of today's `integrate` over the algebraic section: a
  time-bounded sample run first, then the section under an established
  per-integral timeout and an overall wall-clock cap. Per-integral
  timing; outcome classes: expected-match / verified-by-derivative /
  no-answer / timeout.
- The verification-primitive survey: which Maxima operations
  (`diff`, `ratsimp`, `together`, `expand`, `factor`, …) suffice for
  "the derivative of the candidate equals the integrand".
- The gap profile: what milestone 1's acceptance set is, and what
  fraction `integrate` already passes today (the uplift baseline).

### T4 — Rule translation → `docs/rule-translation.md`

- The algebraic class's rules mapped to a Maxima representation:
  which translate mechanically from the .m syntax, which need
  hand-ported conditions.
- The support-function surface this one class actually needs (T1's
  list sliced down).
- The rule-file format and loader for the ported package (readable
  .mac data, a Lisp table, or a hybrid), with reasons.
- The translation procedure — mechanical (scriptable) vs manual
  steps — so that porting class 2 onward reuses it.

### T5 — Package and harness architecture → `docs/package-architecture.md`

- The public API: function name (working name `rubi(f, x)`), result
  shape (antiderivative, or the noun `%integrate` form when no rule
  fires), a verboseness/debug switch.
- The load story, diophantine-mould: one `.mac` that loads its sibling
  `.lisp` file(s) itself, findable by search-path push or by being
  under `~/.maxima/`.
- The test harness: a `maxima --very-quiet -b` driver over the corpus
  sections, with a per-integral timeout, `PASS:`/`FAIL:` lines and a
  final `Results: <n> passed, <m> failed` line (the diophantine
  protocol); verification by differentiation, with exact-match against
  the expected answer as the secondary check.
- The house rules the implementation will live under (symbol hygiene,
  quoting conventions) — informed by what T2's probes found to be traps.

## 5. Order and dependencies

- **T1 first:** the pattern grammar (T2's probe set) and the utility
  inventory (T4's input) both depend on it.
- **T3's sample run starts immediately, in parallel with T1** — the
  recon: it has no dependency on T1, and it surfaces hang risk early.
  The *full* algebraic-section baseline waits for the timeout/format
  design the sample run establishes.
- **T2 after T1** (it probes against T1's pattern inventory).
- **T4 after T1 + T2** (it needs the verdict on what the matcher
  provides).
- **T5 last** — it consumes T1–T4.

Dependency edges: T1 → {T2, T4}; (T3 sample) ∥ T1; (T3 full) → T5;
T2 → {T4, T5}; all of T1–T4 → T5.

## 6. Method conventions

- **Measured claims:** every non-trivial claim in a research doc cites
  the measurement that produced it, and the measurement is a committed,
  re-runnable probe under `probes/` (a Maxima batch script or a shell
  script), named so the doc can point at it.
- Doc sections are written when their evidence exists, not stubbed
  ahead of it.
- Counts and timings are stamped with date and Maxima build (`version()`
  string plus the installed tree name).
- "Maxima surely has X" is never a claim: look it up per `AGENTS.md`
  (`describe(..., exact)`) or write a probe.
- A probe's output, when cited, lives next to the probe (a `.out` file)
  or is summarised in the doc.

## 7. Repo layout (at bootstrapping)

```
maxima-rubi/
  AGENTS.md                          project instructions
  .gitignore
  todo/TODO.md                       short index: id, status, link
  todo/t1-...md  ...  t5-...md       item files: questions + evidence
  probes/                            committed re-runnable probes
  docs/                              research docs (flat)
  docs/superpowers/specs/            SDD design docs (this file)
  docs/superpowers/plans/            SDD plans (implementation phase)
  reference/                         local clones, gitignored; pins in todo/TODO.md
```

The implementation phase (post-research) adds: the package source (one
`.mac` plus sibling `.lisp`), `tests/` (vendored corpus subset + harness
driver). Whether exploratory work gets a tracked `scratch/`
(diophantine keeps one) or a gitignored working dir is an open
implementation-plan item; the default is gitignored.

## 8. Research phase done-when

- All five docs committed; every claim in them cites a re-runnable probe.
- The seed class confirmed or changed, with T1's counts as the evidence.
- T2 has a go/no-go with the matcher cost scoped.
- T3 has the baseline profile and the milestone-1 acceptance set.
- T4 has the translation procedure and the chosen rule format.
- T5 has the harness spec with the test protocol pinned.
- `todo/TODO.md` shows all five items `done`, and the user has read the docs.
- Then: the `writing-plans` skill plans milestone 1, and implementation
  proceeds via the SDD workflow, in TDD where the corpus sections give
  natural assertions.

## 9. Out of scope (this phase)

- Any implementation code beyond probes.
- Risch's algorithm (retargeted away; no Risch deliverables here).
- Hooking the package into Maxima's builtin `integrate`.
- Porting any function class beyond the algebraic one.
- Performance work — timings are measured as a baseline, not targeted,
  until the baseline exists.

## 10. Risks

- **The pattern matcher turns out to be a big build.** T2's sketch plus
  coverage numbers are the scoping instrument. If the matcher bloats,
  the fallback is to shrink milestone 1's class (e.g. rational rules
  only) while the harness and matcher stay — that trade belongs to the
  implementation plan, informed by T2.
- **Corpus hangs.** `integrate` can sit on hard integrals indefinitely.
  T3 designs per-integral timeouts from the sample run; nothing runs
  without one.
- **License.** Unread until T1. If it imposes anything beyond
  attribution, that is a blocker to report before porting starts.
- **Version drift.** All measurements are against the installed 5.49
  development build; a Maxima upgrade invalidates the baselines
  (re-measure and note, diophantine-style).
