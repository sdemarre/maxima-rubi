# Class 6 (hyperbolic functions) port — 5,080 entries

Status: needs-triage
Type: task (port, runbook-driven)
Filed: 2026-08-30 (milestone-3 close; the M2 TODO's class-6 item, now
against the instantiated runbook)

## Scope

Port the "6 Hyperbolic functions" section (section name VERIFIED
against `reference/maxima-syntax-test-suite/6 Hyperbolic
functions/` — 26 `.mac` files under subdirs 6.1 Sine … 6.7
Miscellaneous) and its rule files
(`reference/rubi/Rubi/IntegrationRules/6 Hyperbolic functions/`)
per `docs/class-porting.md` Steps 1–10. The milestone-3
instantiation (`docs/corpus-class3-baseline-uplift.md`) is the
template; its standing constraints bind (byte-identity gate for
every accepted class, 30 s per-entry cap, 100 s timeout re-check,
A/B vs the `integrate` baseline, acceptance record per the
class-2/class-3 template, TLS probe on the core rebuild).

## Recon numbers (measured 2026-08-30 — PRE-CENSUS; the runbook
Step-1 census probe is the first act of the port and supersedes
these)

- **Corpus: 5,080 entries** — counted over the section's 26 `.mac`
  files (lines starting with `[`); matches the M2 TODO's figure.
- Rule files: 13 `.m` files; 13 `Rubi.m` LoadRules entries (all
  loaded, as in class 3's 11/11).
- Rule count: **390 `Int[... ] :=` lines** across the 13 `.m` files
  (recon count of rule-shaped lines; the Step-1 census probe is the
  authoritative count).

## Known interactions

- The hyperbolic heads (`sinh`/`cosh`/`tanh`/`coth`/`sech`/`csch`)
  are native in Maxima; the class-3 Task-3 note that the `%mr_`
  hyperbolic shims (`%mr_asinh`/`%mr_acosh`/`%mr_atanh`) exist for
  class 1–2 answer-side byte-identity — the Step-1 census decides
  whether class 6 reuses them or tables natives.
- Rule count per corpus entry is the thinnest of the queue
  (390/5,080 ≈ 0.077 vs class 3's 333/3,085 ≈ 0.108) — expect a
  larger `deferred` mass than class 3; the runbook's A/B
  genuine/yardstick triage (M2 178/131 worked-example method)
  applies unchanged.
- Queue position: third (8 → 5 → 6 → 7 → 4).

## Acceptance

Per the runbook: merged records complete (5,080/5,080), A/B
triaged with nothing unexplained, re-check read, acceptance record
committed, the byte-identity gates for classes 1–3 (and 8/5 if
accepted earlier) green, Layer A green.

## Comments
