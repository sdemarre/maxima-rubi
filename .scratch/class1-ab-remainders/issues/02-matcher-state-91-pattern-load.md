# Matcher-state: the 9.1 pattern load perturbs family-chain firings

Status: needs-triage
Filed: 2026-08-27 (class-1 A+B acceptance run, core f1f0611f)
Evidence: `.superpowers/sdd/progress.md` (run #2 anatomy, the
three-control-core bisect); control cores `/tmp/opencode/pa.core`
(no 9.1, pre-fix utils), `/tmp/opencode/pabuild2/test/mr_rules.core`
(no 9.1, current utils), `/tmp/opencode/pabuild3/test/mr_rules.core`
(9.1 loaded FIRST, family after, table order unchanged),
`/tmp/opencode/pabuild4` (9.1 r1-r14 only).

## What

Seven entries verified in run-5 now 0-fire at the top level (clean
scans, no misfire/BOOLWALK lines with `rubi_verbose: true`), ending as
timeout (run, 30 s budget) or deferred (canary solo):

| family | entry | integrand | run-5 | A+B run | canary solo (A+B) |
|---|---|---|---|---|---|
| 1.2.2.4 | e223 | `(f*x)^m*(d+e*x^2)/(a+b*x^2+c*x^4)` | verified 7.0 s | deferred 29.6 s | deferred 20.3 s |
| 1.2.1.2 | e2514 | `(a+b*x+c*x^2)^(1/4)/(d+e*x)` | verified 7.1 s | timeout 30.0 s | deferred 25.6 s |
| 1.2.1.2 | e2567 | `(a+b*x+c*x^2)^p/(d+e*x)` | verified 4.5 s | timeout 30.0 s | timeout 60 s |
| 1.2.1.2 | e2568 | `(a+b*x+c*x^2)^p/(d+e*x)^2` | verified 4.5 s | timeout 30.0 s | timeout 60 s |
| 1.2.1.2 | e2569 | `(a+b*x+c*x^2)^p/(d+e*x)^3` | verified 4.5 s | timeout 30.0 s | timeout 60 s |
| 1.2.1.2 | e2572 | `(a+b*x+c*x^2)^p/(d+e*x)^(1/2)` | verified 4.7 s | timeout 30.0 s | timeout 60 s |
| 1.2.1.2 | e2573 | `(a+b*x+c*x^2)^p/(d+e*x)^(3/2)` | verified 4.8 s | timeout 30.0 s | timeout 60 s |

The lost chains (measured on the no-9.1 controls, identical in both):

- e223: `1.2.2.6 r3` fires on the target via the **matchreverse
  pass-2 rescan** (`%mr_dispatch_rev`, `maxima_rubi_dispatch.lisp` —
  the lisp global `matchreverse` flip; pass 1 and pass 3 0-fire on
  both cores). The direct rule call `_mr_rule_1_2_2_6_r3(f, x)` and
  the direct pattern `_mr_pat_1_2_2_6_r3(f, x)` both 0-fire on both
  cores — the firing is a pass-2-rescan artifact of the mquot-vs-
  product stored form (the bare-factor wall class, commit 9f5ccef
  lineage).
- e2514/e2567-e2573: `1.2.1.2 r134` fires (top) with nested
  `1.4.2 r9` — the `(a+b x+c x^2)^p/(d+e x)^k` chain.

## Mechanism (measured — Maxima boundary)

Four same-day cores, same Maxima 5.50.0 / SBCL 2.6.7, same
`maxima_rubi_utils.mac` except the 9.1 wiring:

1. No 9.1 (3026 rules, pre-fix utils) — e223 and e2514/e2567 chains
   fire; targets verify.
2. No 9.1 (3026 rules, CURRENT utils incl. the `rubi_hybrid` split,
   commit 89054b0) — same firings. Rules out the utils edit.
3. A+B (3055 rules) — both chains 0-fire (20-60 s of clean scanning).
4. 9.1 loaded FIRST (3055 rules, family patterns compiled in the 9.1
   matcher state, table order unchanged) — still 0-fires. Load ORDER
   cannot fix it.
5. 9.1 FIRST HALF ONLY (r1-r14 loaded, 3040 rules) — the e223 result
   CHANGES A THIRD WAY: a different rule fires first under the
   rescan and embeds an `_mr_rule_9_1_r12(...)` noun in the answer.
   ANY 9.1 pattern load perturbs the rescan; it is not one bad rule.

The perturbation is in the installed Maxima's compiled matcher /
matchfix special-variable state (176 `defmatch`/`matchdeclare` slots
the 9.1 file creates): the family patterns are byte-identical across
all four cores (git-verified), the lisp is byte-identical, the table
prefix is identical — only the 9.1 load differs, and the rescan
result changes. Not reachable from Maxima-level rule code.

## Follow-up

1. Minimal repro for the Maxima mailing list (the `../maxima-lists`
   archive is the project's search ground): a fresh session, N
   `matchdeclare`/`defmatch` pairs (find the minimal N / slot shape
   that reproduces), a mquot-vs-product target, match the pattern
   with `matchreverse` nil then flipped — the flip's factor-order
   behavior (matrun.lisp `findfun`, "nil = reverse") is the suspect
   path.
2. If Maxima confirms a bug: the interim option is a pass-2 table
   reordering or a per-pattern rescue (a manual re-dispatch for the
   two affected chains) — to be decided after the repro lands.

## Acceptance (when worked)

All 7 entries `verified` in a full run; canary broad (120) and Layer A
(511) unchanged.

## Comments

2026-08-27 — 300 s timeout re-check (record test/corpus_class1.timeout5m.out):
the 6 entries in this ticket that were `timeout`-class in the accepted run
CONFIRMED structural — none recovered under the 300 s cap: 1.2.1.2 e2514
deferred t=44.4 s; e2567 deferred t=127.3 s; e2568 deferred t=126.9 s;
e2569 deferred t=121.7 s; e2572 timeout t=300.1 s; e2573 timeout t=300.1 s.
In run-5 all six were `verified` at 4.5-7.1 s. The lost r134+r9 chain
costs these entries either a 44-127 s wild cascade ending in a top-level
no-answer noun, or non-termination outright — budget is not the variable.
(The 7th entry, 1.2.2.4 e223, was `deferred`-class in the accepted run and
was not in the re-check set.)
