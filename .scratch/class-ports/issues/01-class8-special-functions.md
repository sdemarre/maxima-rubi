# Class 8 (special functions) port — 1,949 entries

Status: needs-triage
Type: task (port, runbook-driven)
Filed: 2026-08-30 (milestone-3 close; the M2 TODO's class-8 item, now
against the instantiated runbook)

## Scope

Port the "8 Special functions" section (section name VERIFIED against
`reference/maxima-syntax-test-suite/8 Special functions/` — 10 `.mac`
files) and its rule files
(`reference/rubi/Rubi/IntegrationRules/8 Special functions/`) per
`docs/class-porting.md` Steps 1–10. The milestone-3 instantiation
(`docs/corpus-class3-baseline-uplift.md`, plan
`docs/superpowers/plans/2026-08-29-milestone-3-class3.md`) is the
template; its standing constraints bind (byte-identity gate for every
accepted class, 30 s per-entry cap, 100 s timeout re-check, A/B vs
the `integrate` baseline, acceptance record per the class-2/class-3
template, TLS probe on the core rebuild).

## Recon numbers (measured 2026-08-30 — PRE-CENSUS; the runbook
Step-1 census probe is the first act of the port and supersedes
these)

- **Corpus: 1,949 entries** — counted over the section's 10 `.mac`
  files (lines starting with `[`); matches the M2 TODO's figure.
- Rule files: 10 `.m` files; 10 `Rubi.m` LoadRules entries (all ten
  loaded, as in class 3's 11/11).
- Rule count: **310 `Int[... ] :=` lines** across the 10 `.m` files
  (recon count of rule-shaped lines; the Step-1 census probe is the
  authoritative count).
- Section files: 8.1 Error functions, 8.2 Fresnel integral
  functions, 8.3 Exponential integral functions, 8.4 Trig integral
  functions, 8.5 Hyperbolic integral functions, 8.6 Gamma functions,
  8.7 Zeta function, 8.8 Polylogarithm function, 8.9 Product
  logarithm function, 8.10 Formal derivatives.

## Known interactions

- **Shares class 2's head table** (M2 TODO): the existing
  `GAMMA(` → `gamma_incomplete(` and `Ei(` → `expintegral_ei(`
  `HEAD_REWRITES` rows cover 8.3/8.6 expected texts; the section's
  other special-function heads (`erf(`/`erfi(`/`lambert_w(`, 8.1/8.9)
  are already native-lowercase in the corpus — the Step-1 answer-head
  census decides whether any row is needed.
- **8.8 Polylogarithm function** is the natural home of the polylog
  mass the class-3 ceiling decision
  (`.scratch/class3-polylog-ceiling/issues/01`) targets — the
  derivative-shim ticket's where-does-it-live question
  (driver zero-chain vs Maxima-level `diff` simplification) should be
  resolved before this port's Step 8 (normalization) so 8.8 runs on
  the final harness.
- 8.10 Formal derivatives is a small odd file — census it; expect
  little corpus value (the M2 TODO listed this class first in the
  queue at 1,949 entries — the second-smallest section).

## Acceptance

Per the runbook: merged records complete (1,949/1,949), A/B
triaged with nothing unexplained, re-check read, acceptance record
committed, the byte-identity gates for classes 1–3 (and 4–7 if
accepted earlier) green, Layer A green.

## Comments
