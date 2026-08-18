# maxima-rubi — project instructions

A rule-based symbolic integration package for Maxima in the spirit of
Rubi (rule-based integration): declarative integration rules executed by
a pattern-matching rule runner, held to the Rubi Maxima-syntax test
corpus. Milestone 1: foundation + the algebraic-function class.

Research-phase design: `docs/superpowers/specs/2026-08-17-maxima-rubi-research-design.md`.
Working state: `todo/TODO.md`.

## Git

- **The default branch is `master`. There is no `main`** — do not create one.
- A remote is **planned but not yet configured**; until it is set up,
  `git push` has nowhere to go. Do not assume pushing is possible; once
  it is configured, commits target `master`.
- Do not add `Co-Authored-By` trailers to commit messages.

## Reference clones

The research reads two reference repositories, cloned locally under
`reference/` (gitignored — working copies, not part of this project):

- `reference/rubi` — `RuleBasedIntegration/Rubi` (Rubi 4, the rule set being ported).
- `reference/maxima-syntax-test-suite` — `RuleBasedIntegration/MaximaSyntaxTestSuite`.

The pinned commit (full 40-digit hash) of each is recorded in
`todo/TODO.md`. Claims about Rubi refer to the pinned commits.

## Maxima version

The installed build is a 5.49-series development version; **5.50 is
expected soon** and brings significant improvements, including
pattern-matching *speed* (no new pattern-matching *functionality*).
The project does **not** pin to 5.49 as a target: every measurement
is stamped with the build it was taken on, and baselines are
re-measured on upgrade rather than carried over.

## Looking up Maxima itself

The manual is in the running Maxima, not on the web — consult it before
guessing at a builtin's name, signature or behaviour. Two commands:

- `? subject` — exact lookup, prints the manual entry.
- `?? partial_subject` — inexact search across topic names.

These are shorthand for `describe(subject, exact)` and
`describe(subject, inexact)`; `describe` is equally fine and is the better
choice inside a script, being an ordinary function call with none of the
line-swallowing quirk below.

From a shell, one lookup per invocation:

```sh
maxima --very-quiet --batch-string='? match;'
maxima --very-quiet --batch-string='?? pattern;'
maxima --very-quiet --batch-string='describe("matchfix", exact);'
```

Four behaviours worth knowing, all measured here (Maxima 5.49, SBCL):

- **`?` and `??` swallow the rest of the LINE**, semicolons included. Put one
  on a line by itself: `?? sqrt; disp("hi");` looks up the subject
  `sqrt; disp("hi")` and finds nothing. `describe("sqrt", inexact)` has no
  such problem — it is parsed like any other call.
- **`??` with several matches prints a numbered list, then prompts.** Non
  interactively the prompt hits end-of-file and prints `Maxima encountered a
  Lisp error: end of file`. It is harmless — Maxima continues with the next
  statement — and the numbered list, which is the part you wanted, has
  already been printed.
- **The reliable two-step** is therefore `??` to find the exact name, then `?`
  on that name to read the entry. (Piping a selection — `printf '1\n' |
  maxima -b file.mac` — also answers the prompt, but only for `-b`; with
  `--batch-string` the prompt does not read stdin.)
- `??` with exactly one matching topic skips the prompt and prints the entry.

## Research discipline

- **Measured claims:** every non-trivial claim in a `docs/` research doc
  cites the measurement that produced it, and the measurement is a
  committed, re-runnable probe under `probes/` (a Maxima batch script or a
  shell script). A doc section is written when its evidence exists, not
  stubbed ahead of it.
- Counts and timings are stamped with the date and the Maxima build —
  obtained from `build_info()` (`version` is unbound in the installed
  5.49-series development build).
- "Maxima surely has X" is never a claim: look it up per the section above,
  or write a probe.

## Tests

When the test harness exists (implementation phase), the main suite is one
batch run:

```sh
maxima --very-quiet -b test_maxima_rubi.mac
```

It ends with `Results: <n> passed, <m> failed`. Read that line — individual
assertions print `PASS:`/`FAIL:` above it, and a run can also die mid-way
with a Maxima error, in which case no `Results:` line is printed at all,
which is itself a failure. The harness protocol (per-integral timeout,
differentiation-based verification) is specified in
`docs/package-architecture.md` (T5) once that research is done.

The research phase has no suite; its discipline is the probe convention above.

## Agent skills

### Issue tracker

Local markdown: issues and specs live as files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary, label strings equal to role names. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root (neither exists yet; created lazily). See `docs/agents/domain.md`.
