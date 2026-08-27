# 300 s re-check death signatures: heap cap, control stack, verification fatal

Status: needs-triage
Type: harness + research (three separate items under one measured census)
Filed: 2026-08-27 (from the 300 s timeout re-check of the 787
accepted-run `timeout` entries, 14:13-16:47 UTC; record
`test/corpus_class1.timeout5m.out`, merge transcript
`test/timeout_rerun_merge.out`; census = all 47 `error` entries
re-run individually with full output capture, 8-way parallel,
captures `/tmp/opencode/timeout_recheck/errtriage/`, script
`/tmp/opencode/timeout_recheck/err_triage.py` + `census.py`)

## The census

47/47 classified, zero unknowns:

| signature | count | what it is |
|---|---|---|
| heap-exhausted | 38 | per-process OOM at the SBCL default 1 GB dynamic-space cap |
| control-stack | 6 | recursion-depth overflow ("Control stack exhausted") |
| verify-integrate-fatal | 3 | HARNESS bug: numeric verification substitutes x:=0.35 into an interior `integrate(g, x)` term |

Per-entry table (death-time = wall time in the 300 s re-check run):

| family file | entry | death-time s | signature |
|---|---|---|---|
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1702 | 5.4 | control-stack |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1712 | 4.4 | control-stack |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e191 | 277.9 | heap-exhausted |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e206 | 239.2 | heap-exhausted |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e504 | 146.1 | heap-exhausted |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e517 | 119.2 | verify-integrate-fatal |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e519 | 160.9 | heap-exhausted |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e521 | 280.4 | verify-integrate-fatal |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e677 | 137.6 | heap-exhausted |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e678 | 139.6 | heap-exhausted |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e679 | 125.0 | heap-exhausted |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e680 | 82.0 | heap-exhausted |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e683 | 192.2 | verify-integrate-fatal |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e686 | 109.0 | heap-exhausted |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e688 | 98.7 | heap-exhausted |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e689 | 180.6 | heap-exhausted |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e695 | 96.3 | heap-exhausted |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2521 | 13.8 | control-stack |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2531 | 4.5 | control-stack |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2540 | 11.9 | control-stack |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2545 | 4.5 | control-stack |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1474 | 104.8 | heap-exhausted |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1475 | 139.6 | heap-exhausted |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1477 | 98.4 | heap-exhausted |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1478 | 104.7 | heap-exhausted |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1485 | 161.2 | heap-exhausted |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e639 | 93.2 | heap-exhausted |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e685 | 113.3 | heap-exhausted |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e858 | 283.8 | heap-exhausted |
| 1.2.1.5 (a+b x+c x^2)^p (d+e x+f x^2)^q | e9 | 211.6 | heap-exhausted |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e851 | 71.5 | heap-exhausted |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e852 | 75.7 | heap-exhausted |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e864 | 167.2 | heap-exhausted |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e878 | 206.2 | heap-exhausted |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e890 | 77.3 | heap-exhausted |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e891 | 93.5 | heap-exhausted |
| 1.2.2.4 (f x)^m (d+e x^2)^q (a+b x^2+c x^4)^p | e103 | 158.4 | heap-exhausted |
| 1.2.2.4 (f x)^m (d+e x^2)^q (a+b x^2+c x^4)^p | e115 | 108.7 | heap-exhausted |
| 1.2.2.4 (f x)^m (d+e x^2)^q (a+b x^2+c x^4)^p | e129 | 216.0 | heap-exhausted |
| 1.2.2.4 (f x)^m (d+e x^2)^q (a+b x^2+c x^4)^p | e345 | 146.7 | heap-exhausted |
| 1.2.2.5 P(x) (a+b x^2+c x^4)^p | e22 | 186.7 | heap-exhausted |
| 1.2.2.6 P(x) (d x)^m (a+b x^2+c x^4)^p | e27 | 73.2 | heap-exhausted |
| 1.2.2.6 P(x) (d x)^m (a+b x^2+c x^4)^p | e32 | 107.7 | heap-exhausted |
| 1.2.2.6 P(x) (d x)^m (a+b x^2+c x^4)^p | e35 | 235.2 | heap-exhausted |
| 1.3.1 Rational functions | e13 | 264.9 | heap-exhausted |
| 1.3.2 Algebraic functions | e479 | 296.4 | heap-exhausted |
| 1.3.2 Algebraic functions | e719 | 84.9 | heap-exhausted |

## Item 1: heap-exhausted (38) — the 1 GB default cap

Evidence (1.2.1.2 e680, death at 82 s):

    Heap exhausted during garbage collection: 0 bytes available, 16 requested.
    fatal error encountered in SBCL pid ... : Heap exhausted, game over.

GC dump at death: `dynamic_space_size = 1073741824`,
`*GC-INHIBIT* = true`, GC running with nothing reclaimable (all live).
The core is built (`test/build_rules_core.sh`) without
`--dynamic-space-size`, so every subprocess from the image runs at
SBCL's default 1 GB dynamic space. The box had 53 GB free; no
OOM-killer activity in dmesg — this is a per-process cap, not system
OOM. Mechanism: a candidate answer's `ratsimp`/`factor` working set on
the diff holds >1 GB of live cons cells (the quartic/trinomial radical
families — 1.2.1.2, 1.2.2.2, 1.2.2.4, 1.2.2.6 dominate the table).

Directions (to be triaged):

1. Raise the per-process cap: `--dynamic-space-size N` on the driver's
   sbcl invocation AND the core build (probe first: does the cap take
   effect when restoring the image?). Memory budget: 24 parallel
   procs x N of the 62 GB (N = 2 GB -> 48 GB worst case, feasible;
   measure actual peak with a few known heap deaths).
2. Leave as-is: `error` is an honest FAIL class; the 38 are 0.15% of
   the corpus. A raised cap converts at most 38 entries and costs
   23 GB of headroom.

## Item 2: control-stack (6) — recursion depth, possibly ticket-02-related

Evidence (1.1.1.2 e1712, death at 4.4 s):

    INFO: Control stack guard page unprotected
    Control stack guard page temporarily disabled: proceed with caution
    Maxima encountered a Lisp error:
     Control stack exhausted (no more space for function call frames).

Deep-and-fast: 4 of the 6 die at 4.4-13.8 s. The 1.2.1.2 quartet
(e2521/e2531/e2540/e2545) sits ADJACENT to the ticket-02 matcher-state
region (e2514/e2567-e2573) — hypothesis: a lost rule chain leaves the
cascade in a recursion where the .m pipeline would have stopped (the
chain that would have produced the answer in run-5's 4.5 s is 0-fired,
and the cascade that instead recurses runs the control stack into the
ground). Check: re-run the 6 on the no-9.1 control core
(`/tmp/opencode/pabuild2/test/mr_rules.core` pattern) — if they
verify, the deaths are a symptom of the ticket-02 mechanism, not an
independent workload property.

## Item 3: verify-integrate-fatal (3) — harness bug, cheap fix

Entries: 1.1.3.8 e517/e521, 1.2.1.2 e683. The cascade SUCCEEDS (an
answer exists) but the numeric verification stage dies the process.
Sequence (1.1.3.8 e517, full capture):

    Unable to evaluate to requested number of digits   (x4)
    integrate: variable must not be a number; found: 0.35
    `quotient' by `zero'
    Unable to evaluate to requested number of digits   (x4)
    integrate: variable must not be a number; found: 0.35
    [process dies; no CLASS line]

The answer carries an INTERIOR explicit `integrate(g, x)` term
(legitimate — the driver's contains-noun logic only poisons the
`unintegrable` marker; a native `integrate[g, x]` interior term
normally verifies, since `diff` knows d/dx Int(g,x) = g). The numeric
stage `ev(diff(mr_r, x) - mr_f, [a=0.9, ..., x=0.35])` substitutes
0.35 into the term's VARIABLE slot -> `integrate(g[x:=0.35], 0.35)`
-> fatal arg error. In this build the first occurrence is caught by
`errcatch` (message printed, chain continues); the second (the
expected-diff chain after the self-diff chain) is uncatchable and
kills the batch before the CLASS line — same unstable errcatch
semantics as the `'quotient' by 'zero'` fatality that motivated the
outer guard (driver comment at test/corpus_class1_driver.py:247).

The driver already guards the DIFF analog (materialize `MR_de` once,
driver comment at test/corpus_class1_driver.py:270: "ev'd over a
still-unevaluated diff(mr_r, x) substitutes x into the diff's variable
argument and errors 'second argument must be a variable; found 0.35'").
The integrate-term analog is unguarded.

Fix (proposed): in `zero_chain`, before the numeric stages, detect an
interior `integrate(., x)` term in the candidate (a `freeof`-style
check, or simply attempt the substitution on a COPY first under
errcatch and skip the numeric stage if it errors) — falling back to
the symbolic stages, which handle `integrate` terms correctly.
Validation: the 3 entries re-run to a CLASS line (verified or
unverified), canary broad (120) + Layer A (511) unchanged.

## Acceptance (when worked)

- Item 3: the 3 entries produce a CLASS line; no new deaths on a
  re-run of the 47; canary + Layer A unchanged.
- Item 1 (if the cap is raised): a probe measuring the peak heap of a
  known heap death at the new cap, committed under probes/.
- Item 2 (if the no-9.1 core check is run): the outcome recorded here,
  and ticket 02 amended if the deaths are a ticket-02 symptom.

## Comments
