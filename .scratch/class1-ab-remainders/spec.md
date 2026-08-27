# Spec: class-1 A+B acceptance-run remainders

Source run: the clean 24-shard A+B full run of 2026-08-27
(11:40-13:02 UTC, core `f1f0611f`, 3055 rules — Phase A implicit-1
pass-3 lift + Phase B section-9.1 port with the r11 top-level gate and
the collapse-rule exact seen check), accepted at
`test/corpus_class1.out` / `test/full_core_merge.out` (commit
`45fc9b8`): 19,731 passed / 5,966 failed.

Per-target A/B vs the run-5 baseline (`test/corpus_class1.run5-accept.out`,
commit `98128c0`): 25,697 matched, **1,162 improvements, 19
regressions** — 16 PASS->FAIL remainders in two classes plus 3
corpus-limitation cases. The full anatomy, including the pre-fix
85-regression set and the two fix mechanisms, is in
`.superpowers/sdd/progress.md` (section "Work item: Phase A implicit-1
matcher fix + Phase B section-9.1 port", the 2026-08-27 run entries).

A/B methodology (re-runnable): join on `(basename without .mac,
e-index)`; run-5 line regex
`^(\S+)\s+t=\s*[\d.]+s (.*) e(\d+) L(\d+)\s*$`; pass classes
`verified`, `expected`, `no-answer`.

## Tickets

- `issues/01-slow-zero-chain-forms.md` — 9 verified->timeout: correct
  answers whose zero chain runs 25-35 s solo, over the 30 s per-entry
  budget under 24-way load.
- `issues/02-matcher-state-91-pattern-load.md` — 7 verified->timeout/
  deferred: the section-9.1 PATTERN LOAD perturbs the installed Maxima's
  compiled matcher on specific family chains; Maxima-boundary,
  mailing-list repro is the follow-up.
- `issues/03-corpus-unintegrable-now-integrated.md` — 3 no-answer->
  unexpected: the package now returns NUMERICALLY CORRECT answers where
  the 2018 corpus expects Unintegrable; the corpus cannot accept them
  (its PASS class for those entries is `no-answer` only).
- `issues/04-matcher-backtracking-feasibility.md` — research
  (ready-for-agent): feasibility of adding backtracking to the
  Maxima matcher (the lever on the 4,361 `deferred` entries, 73% of
  the failures). Findings land in
  `docs/matcher-backtracking-feasibility.md` + `probes/matcher/`.
