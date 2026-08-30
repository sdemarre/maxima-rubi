# Class 4 (trigonometric functions) port — 22,472 entries

Status: needs-triage
Type: task (port, runbook-driven)
Filed: 2026-08-30 (milestone-3 close; the M2 TODO's class-4 item, now
against the instantiated runbook)

## Scope

Port the "4 Trig functions" section (section name VERIFIED against
`reference/maxima-syntax-test-suite/4 Trig functions/` — 77 `.mac`
files under subdirs 4.1 Sine … 4.7 Miscellaneous) and its rule files
(`reference/rubi/Rubi/IntegrationRules/4 Trig functions/`) per
`docs/class-porting.md` Steps 1–10. The milestone-3 instantiation
(`docs/corpus-class3-baseline-uplift.md`) is the template; its
standing constraints bind (byte-identity gate for every accepted
class, 30 s per-entry cap, 100 s timeout re-check, A/B vs the
`integrate` baseline, acceptance record per the class-2/class-3
template, TLS probe on the core rebuild).

## Recon numbers (measured 2026-08-30 — PRE-CENSUS; the runbook
Step-1 census probe is the first act of the port and supersedes
these)

- **Corpus: 22,472 entries** — counted over the section's 77 `.mac`
  files (lines starting with `[`); matches the M2 TODO's figure.
  **The largest section in the suite** (class 1, the manually
  ported milestone-1 corpus, is 25,697 — class 4 is next in size).
- Rule files: **57 `.m` files in the tree, 56 `Rubi.m` LoadRules
  entries** — 1 `.m` file is NOT in the LoadRules list; the
  Step-1 census settles membership (the class-7 ticket carries the
  same note, 4 files there).
- Rule count: **2,095 `Int[... ] :=` lines** across the 57 `.m`
  files (recon count over ALL files in the tree, loaded or not; the
  Step-1 census probe is the authoritative loaded count).

## Known interactions

- **Deliberately LAST in the queue (8 → 5 → 6 → 7 → 4)** — largest
  corpus (22,472 entries), most files (77), and the class that
  exercises the ported machinery at the largest scale (run cost:
  class 3's 3,085 entries took 28 min 04 s wall under 24 processes;
  class 4 is ~7x — the launcher's cost model will shard heavily, as
  it did for class 3's 456-entry 3.1.4).
- The trig heads (`sin`/`cos`/`tan`/`cot`/`sec`/`csc`) are native;
  the class-3 headvar `F_` allow-list covers the inverse heads that
  4.1.5/4.3.x/4.5.x shapes pair with (`asin`/`acos`/`asinh`/…); the
  Step-1 census decides any new headvar allow-lists.
- Expect the class-3 residue profile at 7x scale: a `deferred`
  mass (2,095 rules against 22,472 shapes — a thinner
  rules/entries ratio than class 3), a special-function
  `unverified` mass (the trig-integral heads `si`/`ci`/`shi`/`chi`/
  `Ei` appear in 4.7 Miscellaneous expected texts — the class-3
  `HEAD_REWRITES` rows may already cover them; the Step-1
  answer-head census decides), and a non-terminator `timeout` mass
  (the class-3 96/117 confirmed-non-terminator rate).
- If the class-3 polylog-shim
  (`.scratch/class3-polylog-ceiling/issues/01`) lands first, class 4
  runs on the post-shim harness — no record re-baseline needed
  (the shim is a verification-harness change only, the M2
  radcan-fallback precedent: re-measure the earlier classes' no-op
  slices, not their full corpora, unless a class's expected texts
  exercise the new closure).

## Acceptance

Per the runbook: merged records complete (22,472/22,472), A/B
triaged with nothing unexplained, re-check read, acceptance record
committed, the byte-identity gates for classes 1–3 (and 8/5/6/7 if
accepted earlier) green, Layer A green.

## Comments
