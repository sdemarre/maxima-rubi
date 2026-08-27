# TODO — index

One short entry per item: status + link. The questions to be answered
and the evidence live in the item's file. Items may reference each other.
Status: `open` / `in prog` / `done`.

| id  | title                            | status | item file                                  |
|-----|----------------------------------|--------|--------------------------------------------|
| T1  | Rubi anatomy                     | done   | [t1-rubi-anatomy.md](t1-rubi-anatomy.md)   |
| T2  | Pattern matching in Maxima       | done   | [t2-pattern-matching.md](t2-pattern-matching.md) |
| T3  | Corpus and Maxima baseline       | done   | [t3-corpus-baseline.md](t3-corpus-baseline.md)   |
| T4  | Rule translation (algebraic)     | done   | [t4-rule-translation.md](t4-rule-translation.md) |
| T5  | Package and harness architecture | done   | [t5-package-architecture.md](t5-package-architecture.md) |

Order: T1 first; T3's sample run in parallel with T1; T2 after T1;
T4 after T1 + T2; T5 last. See the design spec, section 5.

## Milestone 1 — closed 2026-08-27

Foundation + the algebraic-function class (plan
`docs/superpowers/plans/2026-08-20-milestone-1-implementation.md`,
Tasks 1-10 all done). Acceptance (user-confirmed 2026-08-27):
**19,731/25,697 (76.8 %) of the class-1 corpus PASS vs the T3
`integrate` baseline of 49.8 %**, no unexplained regressions. Record:
`docs/corpus-baseline-uplift.md` (accepted run
`test/corpus_class1.out`, commit `45fc9b8`); handoff
`handoff/2026-08-27-milestone-1-complete.md`; post-milestone tickets
`.scratch/class1-ab-remainders/`.

T5's open measurements, closed with values (Maxima 5.50.0 / SBCL
2.6.7):

- **Load wall** — the TLS pattern cap is unchanged on 5.50.0 (1200
  load / 1600 die, re-probed); resolution: `--tls-limit 100000` on
  every rule-loading process + the option-D rules core (entry-time
  avg 1.76 s vs 9.69 s; full-class-1 wall 46 min -> ~82 min as the
  rule set grew).
- **Recursion cap** — `%mr_max_depth : 16` (`maxima_rubi_utils.mac:73`),
  set against corpus-observed recursion depth.
- **Zero chain** — two-point numeric stage leading, then both exact
  stage orders, whole chain errcatch-wrapped; residual 643 unverified
  (2.5 %) is the verify-gap workstream.
- **30 s per-entry cap** — STAYS the standard (user decision
  2026-08-27); the timeout re-check (`test/launch_timeout_rerun.py`
  et seq.) is the standing verification (555/787 re-run timeouts are
  genuine non-terminators at 300 s).

## Pinned reference clones

- `reference/rubi` @ `61e9c18ea248061cd83c67882f7c91a73cef912d` (cloned 2026-08-17)
- `reference/maxima-syntax-test-suite` @ `60295e21c571ca210ecfbb695f4af99947454adf` (cloned 2026-08-17)
- `reference/rubi-5` @ `37a71d650aa1ff7903d4de9cdd1a20c115969f4d` (cloned 2026-08-17)
