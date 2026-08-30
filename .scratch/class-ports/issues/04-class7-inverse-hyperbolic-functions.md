# Class 7 (inverse hyperbolic functions) port — 6,552 entries

Status: needs-triage
Type: task (port, runbook-driven)
Filed: 2026-08-30 (milestone-3 close; the M2 TODO's class-7 item, now
against the instantiated runbook)

## Scope

Port the "7 Inverse hyperbolic functions" section (section name
VERIFIED against `reference/maxima-syntax-test-suite/7 Inverse
hyperbolic functions/` — 20 `.mac` files under subdirs 7.1 Inverse
sine … 7.6 Inverse cosecant) and its rule files
(`reference/rubi/Rubi/IntegrationRules/7 Inverse hyperbolic
functions/`) per `docs/class-porting.md` Steps 1–10. The
milestone-3 instantiation (`docs/corpus-class3-baseline-uplift.md`)
is the template; its standing constraints bind (byte-identity gate
for every accepted class, 30 s per-entry cap, 100 s timeout
re-check, A/B vs the `integrate` baseline, acceptance record per the
class-2/class-3 template, TLS probe on the core rebuild).

## Recon numbers (measured 2026-08-30 — PRE-CENSUS; the runbook
Step-1 census probe is the first act of the port and supersedes
these)

- **Corpus: 6,552 entries** — counted over the section's 20 `.mac`
  files (lines starting with `[`); matches the M2 TODO's figure.
- Rule files: **25 `.m` files in the tree, 21 `Rubi.m` LoadRules
  entries** — 4 `.m` files are NOT in the LoadRules list; the
  Step-1 census (which counts only loaded files, the class-1/3
  precedent) settles membership, and the record must state which
  files are excluded and why (absent from Rubi.m, as class 3's
  corpus-less 3.1.1/3.1.3 were absent from the suite — the inverse
  situation).
- Rule count: **1,075 `Int[... ] :=` lines** across the 25 `.m`
  files (recon count over ALL files in the tree, loaded or not; the
  Step-1 census probe is the authoritative loaded count).

## Known interactions

- The inverse-hyperbolic heads (`asinh`/`acosh`/`atanh`) are the
  class-3 headvar allow-list spellings with the `%mr_` shims
  existing for class 1–2 byte-identity; `asech`/`acsch`/`acoth`-
  style spellings, if present in expected texts, need the
  Step-1 answer-head census to decide table/rewrite disposition
  (boundness probe first — the class-3 ArcCot/ArcCoth
  unbound-noun adjudication is the precedent).
- Queue position: fourth (8 → 5 → 6 → 7 → 4).

## Acceptance

Per the runbook: merged records complete (6,552/6,552), A/B
triaged with nothing unexplained, re-check read, acceptance record
committed, the byte-identity gates for classes 1–3 (and 8/5/6 if
accepted earlier) green, Layer A green.

## Comments
