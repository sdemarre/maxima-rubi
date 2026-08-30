# Class 5 (inverse trig functions) port — 4,585 entries

Status: needs-triage
Type: task (port, runbook-driven)
Filed: 2026-08-30 (milestone-3 close; the M2 TODO's class-5 item, now
against the instantiated runbook)

## Scope

Port the "5 Inverse trig functions" section (section name VERIFIED
against `reference/maxima-syntax-test-suite/5 Inverse trig
functions/` — 18 `.mac` files under subdirs 5.1 Inverse sine … 5.6
Inverse cosecant) and its rule files
(`reference/rubi/Rubi/IntegrationRules/5 Inverse trig functions/`)
per `docs/class-porting.md` Steps 1–10. The milestone-3
instantiation (`docs/corpus-class3-baseline-uplift.md`) is the
template; its standing constraints bind (byte-identity gate for
every accepted class, 30 s per-entry cap, 100 s timeout re-check,
A/B vs the `integrate` baseline, acceptance record per the
class-2/class-3 template, TLS probe on the core rebuild).

## Recon numbers (measured 2026-08-30 — PRE-CENSUS; the runbook
Step-1 census probe is the first act of the port and supersedes
these)

- **Corpus: 4,585 entries** — counted over the section's 18 `.mac`
  files (lines starting with `[`); matches the M2 TODO's figure.
- Rule files: 15 `.m` files; 15 `Rubi.m` LoadRules entries (all
  loaded, as in class 3's 11/11).
- Rule count: **665 `Int[... ] :=` lines** across the 15 `.m` files
  (recon count of rule-shaped lines; the Step-1 census probe is the
  authoritative count).

## Known interactions

- The inverse-trig heads (`asin`/`acos`/`atan`/`acot`/`asinh`/
  `acosh`/`atanh`/`acoth`) are the class-3 headvar allow-list heads —
  the native bound spellings are already probed and tabled
  (class-3 Task 3; `arccot`/`arcoth` unbound-noun adjudication);
  the Step-1 answer-head census decides which `HEAD_REWRITES` rows
  (if any) the expected texts need (`ArcTan(`-style Rubi paren
  spellings may occur in expected answers — the class-3
  bracket-sweep precedent).
- Queue position: second (8 → 5 → 6 → 7 → 4).

## Acceptance

Per the runbook: merged records complete (4,585/4,585), A/B
triaged with nothing unexplained, re-check read, acceptance record
committed, the byte-identity gates for classes 1–3 (and 8 if
accepted earlier) green, Layer A green.

## Comments
