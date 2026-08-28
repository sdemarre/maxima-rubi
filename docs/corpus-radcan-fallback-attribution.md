# Class-1 corpus — attribution of the 370 entries flipped FAIL→PASS
in the 2026-08-28 A/B around the zero-chain `radcan(rat())` fallback
(v2 decomposition, 2026-08-28)

Of the **370 entries** that flipped FAIL→PASS in the 2026-08-28
full-corpus A/B around the zero-chain `radcan(rat())` fallback
(commit `fe7f1c8`), the corrected decomposition (probe v2 — which
adds the driver's leading numeric stage and the corrected elliptic
gate that v1 lacked) is:

- **367 closed by the fallback** — the post run's numeric stage
  declined, the 8-stage symbolic chain did not close (23 of them
  CRASHED a `ratsimp` stage with `` `quotient' by `zero' `` — the
  bug the harness change works around — and 344 finished without
  closing, plain simplifier gaps), and the **ungated**
  `radcan(rat())` fallback closed the diff. The post run's gate was
  a no-op — see "The no-op gate" below.
- **3 closed by the leading numeric stage** (1.2.1.5 e59/e66/e73) —
  their zero-diff evaluates to resid < 1e-9 at both sweep points
  under today's answer.
- **0 closed by a symbolic chain stage.**

**Corrected-gate impact**: 35 of the 367 fallback rescues carry
elliptic zero-diffs (ELL=false) — the corrected gate
(`apply(freeof, [the six elliptic_* symbols, diff])`, fixed
2026-08-28 after the no-op was found) blocks the fallback on them,
and those 35 entries revert to `unverified` (22 crash-rescues + 13
gap-rescues). 335 of the 370 survive the corrected gate.

## The no-op gate (why v2 exists)

The fallback shipped (fe7f1c8) gated on
`freeof([elliptic_f, …, elliptic_kc], MR_de)` — a **list first
argument**, which is not a documented `freeof` call (manual, 5.50.0:
the multi-argument form is `freeof(x1, …, xn, expr)` ==
`freeof(x1, expr) and … and freeof(xn, expr)`). The list form tests
"does the LIST occur in expr" and returns true on elliptic-carrying
diffs (measured 2026-08-28: `freeof([elliptic_f], elliptic_f(x, -4))`
= true) — a silently no-op gate. Consequences in the A/B:

- the 367 fallback rescues include elliptic-carrying diffs the gate
  was meant to keep out (35 of them);
- the gate's stated purpose — keeping `radcan(rat())` off
  elliptic-family zero-diffs that burn 30–100 s and crash with
  `PTPTQUOTIENT: Polynomial quotient is not exact` — failed: 28
  `unverified` entries regressed to `timeout` (18 in 1.2.1.3, 4 in
  1.1.2.4, 2 in 1.2.1.4, 1 each in 1.1.1.2, 1.1.1.3, 1.3.1). Traced:
  1.2.1.3 e455 (chain completes nz, fallback burns and returns
  nonzero, entry eats the cap) and 1.1.2.4 e800 (expected-diff chain
  dies in a `PTPTQUOTIENT` stage, fallback burns the rest of the cap;
  under the corrected gate the same entry completes in 5.1 s
  unverified).
- The 4 `verified`→`timeout` entries of the A/B (pre-t 24.8–30.0 s)
  are borderline cap variance, not the gate: their chains/numeric
  stages close just past the cap and the fallback never runs on
  them (traced: 1.2.2.3 e269 — self-diff closes numerically in
  21 s).

Fixed 2026-08-28 to `apply(freeof, [syms…, MR_de])` — the documented
variadic form spliced over the symbol list; see
`test/test_driver_radcan_fallback.py` (construction, gate-semantics,
rescue, and gate-blocks checks).

## Corrections to the v1 framing
(`probe-radcan-attribution`, run 2026-08-28 11:02 UTC)

1. **"23 crash victims of the old run" was wrong.** v1 replayed the
   symbolic chain on today's zero-diff but omitted the numeric stage
   that leads the driver's zero chain, and it mirrored the harness
   gate as it ran (the no-op list form). Timing forensics on the two
   records: only 4 of the 23 had pre-run times consistent with a
   pre-run crash (e540 30.0 s timeout, e541 20.7 s, e543 17.8 s,
   e544 17.4 s); the other 19 pre-times are 0.6–5.6 s (fast
   non-closures on the pre run's answer). All 23 post-times are
   0.6–6.0 s: the post run never spent crash time on them either
   (these diffs crash B5 in <1 s — the ~20 s figure is specific to
   the hand-minimal repro — and the fallback closes in 1–2 s).
   What is true: **today's** zero-diff of all 23 crashes the old
   symbolic chain (22 at B5, 1 at B3, identical message
   `` `quotient' by `zero' `` — the upstream-bug attribution for
   those 23 diffs is direct), and the post run passed them only via
   the (ungated) fallback.
2. **The A/B baseline is confounded with a rule change.** The
   pre-record (2026-08-27 13:02 UTC) ran on pre-`89054b0` rules;
   `89054b0` (13:22 UTC, 20 min after the pre merge) changed 1.1.3.8
   and related behavior (its own message cites 1.1.3.8 e156).
   Today's answer (current rules) is what the post run and probe v2
   measure; the pre run saw a different answer on the affected
   entries. A flip is therefore a rule-change and/or fallback
   effect: the 3 numeric-stage flips are rule-change effects
   (today's answer closes numerically); the 367 fallback rescues
   required the fallback on today's answer — chain crash or gap,
   then ungated `radcan(rat())` closing — whatever the pre run's own
   failure mode was.

## Inputs

- `test/corpus_class1.pre-radcan-fallback.out` — the pre-fallback
  merged record (2026-08-27 13:02 UTC; 19,731 passed / 5,966 failed;
  **pre-`89054b0` rules**);
- `test/corpus_class1.out` — the post-fallback merged record
  (2026-08-28 10:03 UTC; 20,097 passed / 5,600 failed; current
  rules);
- commit `fe7f1c8` (branch `harness-radcan-fallback`) — the harness
  change itself (fallback with the no-op list-form gate); the gate
  fix (2026-08-28, `apply(freeof, …)`) is uncommitted at the time of
  writing;
- `probes/maxima/probe-radcan-attribution-v2.{py,run,out}` — the
  re-runnable v2 probe and its stamped output (2026-08-28 16:48
  UTC);
- `probes/maxima/probe-radcan-attribution.{py,run,out}` — the v1
  probe and its stamped output (2026-08-28 11:02:37 UTC), kept as
  the record of the no-op-gate era (its FB column mirrors the
  gate as it ran);
- build: Maxima 5.50.0 (build date 2026-08-20 21:36:22), SBCL 2.6.7.

## Method (v2)

`sh probes/maxima/probe-radcan-attribution-v2.run` — 370 fresh
maxima subprocesses (one per entry, 24-way parallel, 150 s per-entry
cap; no entry came close to the cap), each running on the rules core:

1. `rubi(f, x)` with the fixed 40-`pos`/20-`no` prompt answers — the
   same answers the corpus driver uses, so the reproduced answer is
   the one the post run verified (answers verified deterministic
   across fresh processes, measured 2026-08-28);
2. for each zero-diff the post run could have closed (self-diff for
   →verified entries, expected-answer diff for →expected entries,
   in the driver's check order), in the driver's stage order:
   - `NUM` — the driver's **leading numeric stage**: float ev under
     the sweep subs (`a=0.9, b=1.3, c=0.5, d=0.9, e=1.1, f=0.8,
     g=1.7, h=0.3, A=0.6, B=1.4, C=0.4, D=0.9, p=2`) at x=0.35 and
     x=0.65, resid < 1e-9 at both points → CLOSES | decline.
     (v1 omitted this stage — the driver's zero chain leads with
     it, and it explains 3 of the 370.)
   - `ELL` — the **corrected gate** `apply(freeof, [the six
     elliptic_* symbols, diff])`: true = gate admits, false = gate
     blocks.
   - `CH` — a **replay of the old zero-chain symbolic stages**: the
     same 8 stages in the same order with the same carried values,
     each in its own `errcatch` so a crash is *recorded* (DIED Bk)
     instead of killing the chain, and a closure recorded (CLOSED
     Bk); neither → FINISHED. The replay stops at the first crash,
     matching the old chain's single outer errcatch.
   - `FB` — `errcatch(radcan(rat(diff)))` run **ungated** (the post
     run's broken gate let the fallback run on every diff) → CRASH |
     true (closes to exact 0) | false.
3. `MECH` — the post run's closing mechanism for the entry: NUM if
   the numeric stage closed; else CHAIN Bk if the replay closed;
   else FB if the ungated fallback closed; else INCONSISTENT (none
   occurred). `KEPT` — whether the entry still PASSes under the
   corrected gate (no iff MECH=FB and ELL=false).

Crash-message capture: in this build `errcatch` prints a caught
error as a bare line with no trailing anchor, and two crash classes
(the `expt` and `PTPTQUOTIENT` families) print nothing at all under
errcatch (measured 2026-08-28). The probe takes the column-0
non-echo lines inside each chain window. All 23 DIED entries
printed the message; none were silent.

## The 23 chain-crashing entries (all `` `quotient' by `zero' ``)

Today's zero-diff crashes the old symbolic chain on all 23 (v2
replay; identical message — the upstream-bug attribution is direct).
`gate` = the corrected gate; `kept` = still PASS under it.

| entry | file | stage | old → new | gate | kept |
|---|---|---|---|---|---|
| e2588 | 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | B3 | unverified → verified | admits | yes |
| e826 | 1.1.3.2 (c x)^m (a+b x^n)^p | B5 | unverified → verified | blocks | no |
| e214 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified | blocks | no |
| e529 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified | blocks | no |
| e530 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified | blocks | no |
| e531 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified | blocks | no |
| e540 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | timeout → verified | blocks | no |
| e541 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified | blocks | no |
| e542 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified | blocks | no |
| e543 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified | blocks | no |
| e544 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified | blocks | no |
| e545 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified | blocks | no |
| e546 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified | blocks | no |
| e2060 | 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | B5 | unverified → verified | blocks | no |
| e660 | 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | B5 | unverified → verified | blocks | no |
| e1005 | 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | B5 | unverified → verified | blocks | no |
| e153 | 1.2.2.3 (d+e x^2)^m (a+b x^2+c x^4)^p | B5 | unverified → verified | blocks | no |
| e168 | 1.2.2.3 (d+e x^2)^m (a+b x^2+c x^4)^p | B5 | unverified → verified | blocks | no |
| e4 | 1.2.2.7 P(x) (d+e x^2)^q (a+b x^2+c x^4)^p | B5 | unverified → verified | blocks | no |
| e11 | 1.2.2.7 P(x) (d+e x^2)^q (a+b x^2+c x^4)^p | B5 | unverified → verified | blocks | no |
| e190 | 1.3.2 Algebraic functions | B5 | unverified → verified | blocks | no |
| e196 | 1.3.2 Algebraic functions | B5 | unverified → verified | blocks | no |
| e197 | 1.3.2 Algebraic functions | B5 | unverified → verified | blocks | no |

Notes:

- B5 = `ratsimp(MR_de)` (the first direct ratsimp of the raw diff);
  B3 = `ratsimp(expand(MR_d))`. The crash is the `ratsimp` call
  itself — consistent with the root-cause analysis (unguarded
  inversion at `oldgcd`→`algnormal`→`rainv` over redundant
  algebraic generators in the ring). Crash latency is diff-
  dependent: <1 s on these diffs, ~20 s on the hand-minimal repro.
- e541/e543/e544 are the TDD RED targets that started the harness
  change; e540 is the timeout-class sibling in the same file.
- Only e2588's diff is free of the six elliptic functions — the
  other 22 carry elliptic answers (the quartic-binomial families
  `P(x)·(a+b·x⁴)^(±½,±¾)` and the 1.3.2 algebraic forms), so the
  corrected gate blocks the fallback on them and they revert to
  `unverified` (22 of the 35 in the next section).
- Of the 23, only 4 had pre-run times consistent with a pre-run
  crash (e540 30.0 s, e541 20.7 s, e543 17.8 s, e544 17.4 s); the
  other 19 pre-times are 0.6–5.6 s — the pre run (pre-`89054b0`
  rules, a different answer) never crashed on them.

## The 3 numeric-stage flips (rule-change effect)

| entry | file | v2 | old → new |
|---|---|---|---|
| e59 | 1.2.1.5 (a+b x+c x^2)^p (d+e x+f x^2)^q | NUM=CLOSES (also CH=CLOSED B1) | timeout → verified |
| e66 | 1.2.1.5 (a+b x+c x^2)^p (d+e x+f x^2)^q | NUM=CLOSES (also CH=CLOSED B1) | timeout → verified |
| e73 | 1.2.1.5 (a+b x+c x^2)^p (d+e x+f x^2)^q | NUM=CLOSES (also CH=CLOSED B1) | timeout → verified |

Today's self-diff evaluates to resid < 1e-9 at both sweep points
(NUM=CLOSES — the post run's verify, in ~28 s including the slow
float ev), and `factor` also closes it (CH=CLOSED B1, v1's
"CLOSED B1" reading). The pre run (different, pre-`89054b0`
answer) hit the 30 s cap before `factor` returned. Rule-change
effect (the new answer closes; the old one did not), not the
fallback — all three have ELL=true and KEPT=yes.

## The 35 the corrected gate gives back

MECH=FB and ELL=false: the post run rescued them via the (no-op-
gated) fallback on elliptic-carrying zero-diffs; the corrected gate
blocks the fallback, so under it these revert to `unverified`.
22 are the crash-rescues above (minus e2588); the other 13 are gap-
rescues (chain FINISHED, no crash):

| entry | file | chain replay |
|---|---|---|
| e821, e862, e871, e2910 | 1.1.3.2 (c x)^m (a+b x^n)^p | FINISHED |
| e210, e213 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | FINISHED |
| e252 | 1.1.4.3 (e x)^m (a x^j+b x^k)^p (c+d x^n)^q | FINISHED |
| e1007 | 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | FINISHED |
| e191, e192, e198, e199, e864 | 1.3.2 Algebraic functions | FINISHED |

Design note: these are exactly the class the gate was written for —
but `radcan(rat())` closes them in 1–2 s (the "rat() can never
close an elliptic-carrying diff" premise measured behind the gate's
comment is false for this subfamily; the 30–100 s PTPTQUOTIENT
burns are the 1.2.1.3 family's). A static elliptic gate cannot
separate the two; the trade is 35 PASS entries vs the 28
`unverified`→`timeout` budget-burners the broken gate produced.

## The 332 kept fallback rescues

344 chain-FINISHED gap-rescues (of which 13 are in the gated-out
list above → 331 kept) + the 1 crash-rescue e2588: numeric
declines, chain completes without closing, `radcan(rat())` closes —
it performs radical normalization and full rational reduction over
the algebraic extension, which the 8-stage chain's variants never
reach. A simplifier coverage gap, not a Maxima bug: fixing the
zero-divisor bug alone would have recovered 1 of the 332 kept
gap-rescues' mechanism (the crash), not the rest.

## Full list — all 370 entries (v2 decomposition)

Per chain in driver order (S = self-diff, E = expected-answer diff):
`NUM` = leading numeric stage (sweep subs, x=0.35/0.65, resid < 1e-9
both points); `ELL` = corrected gate `apply(freeof, [six elliptic_*
symbols, diff])` (true = gate admits); `CH` = 8-stage replay; `FB` =
ungated `errcatch(radcan(rat(diff)))` (the post run's actual
mechanism — its gate was a no-op); `MECH` = the post run's closing
mechanism for this entry (first closing chain in driver order);
`KEPT` = would still PASS under the corrected gate (no iff
MECH=FB and ELL=false). Re-runnable via
`sh probes/maxima/probe-radcan-attribution-v2.run` (raw stamped
output in `probes/maxima/probe-radcan-attribution-v2.out`).

### 1.1.1 Linear/1.1.1.2 (a+b x)^m (c+d x)^n.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e368 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e739 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e740 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1085 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1086 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1087 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1099 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1100 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1101 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1102 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1103 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1859 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1860 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1869 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1870 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1871 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1882 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.1 Linear/1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e355 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e356 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e357 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e361 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e362 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e363 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e367 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e368 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e369 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e799 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e808 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e809 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e810 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e811 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e812 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e813 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e814 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e815 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e911 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e912 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e914 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e921 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e922 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2197 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2198 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2209 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2210 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2222 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2223 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2231 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2232 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2239 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2240 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2248 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2249 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2588 | unverified → verified | S | decline | true | DIED B3 | true | FB | yes | ```quotient' by `zero'`` |
| e3039 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3040 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3068 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3069 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3076 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3077 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3078 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3084 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3085 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3086 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3092 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3093 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3095 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.1 Linear/1.1.1.4 (a+b x)^m (c+d x)^n (e+f x)^p (g+h x)^q.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e129 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e132 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e133 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e134 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e135 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.1 Linear/1.1.1.5 P(x) (a+b x)^m (c+d x)^n.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e25 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e26 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.1 Linear/1.1.1.6 P(x) (a+b x)^m (c+d x)^n (e+f x)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e56 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.2 Quadratic/1.1.2.6 (g x)^m (a+b x^2)^p (c+d x^2)^q (e+f x^2)^r.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e1 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e8 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e9 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e10 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e11 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e15 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e16 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e17 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e18 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.2 Quadratic/1.1.2.8 P(x) (c x)^m (a+b x^2)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e172 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e173 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.3 General/1.1.3.2 (c x)^m (a+b x^n)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e821 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e826 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e862 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e871 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e2243 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2260 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2471 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2473 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2474 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2476 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2478 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2479 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2590 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2591 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2592 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2593 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2596 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2597 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2598 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2599 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2600 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2601 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2602 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2605 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2606 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2607 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2608 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2609 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2610 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2611 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2614 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2615 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2616 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2617 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2618 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2619 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2627 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2632 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2635 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2636 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2639 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2653 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2664 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2665 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2691 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2714 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2715 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2716 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2737 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2738 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2748 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2751 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2752 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2753 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2754 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2755 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2758 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2759 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2762 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2765 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2766 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2767 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2768 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2769 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2770 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2771 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2772 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2773 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2910 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e2971 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2973 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2974 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2991 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2995 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3063 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3064 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3065 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3067 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3068 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3069 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3070 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e3071 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.3 General/1.1.3.3 (a+b x^n)^p (c+d x^n)^q.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e189 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e190 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e196 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e197 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e199 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e200 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e201 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e202 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e206 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e207 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e208 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e209 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.3 General/1.1.3.4 (e x)^m (a+b x^n)^p (c+d x^n)^q.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e856 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e861 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e864 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e871 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e872 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e873 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e874 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e877 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e878 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e879 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e880 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e887 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e913 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.3 General/1.1.3.6 (g x)^m (a+b x^n)^p (c+d x^n)^q (e+f x^n)^r.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e5 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e6 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e12 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e13 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e19 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e20 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e21 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e22 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e23 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e24 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e25 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e27 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e29 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e30 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e31 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e32 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e33 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.3 General/1.1.3.8 P(x) (c x)^m (a+b x^n)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e210 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e213 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e214 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e220 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e529 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e530 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e531 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e540 | timeout → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e541 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e542 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e543 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e544 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e545 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e546 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e576 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e592 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e594 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.4 Improper/1.1.4.2 (c x)^m (a x^j+b x^n)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e444 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e445 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e446 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e451 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e452 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.1.4 Improper/1.1.4.3 (e x)^m (a x^j+b x^k)^p (c+d x^n)^q.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e252 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e275 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e283 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.2.1 Quadratic/1.2.1.2 (d+e x)^m (a+b x+c x^2)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e112 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e113 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e114 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e824 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e894 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e895 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e896 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e897 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e901 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e902 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e903 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e904 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e905 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e911 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e912 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e913 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e918 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e919 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e920 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e921 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e922 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e933 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e934 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e935 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e936 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e943 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e945 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e946 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1739 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2060 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |

### 1.2.1 Quadratic/1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e485 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e486 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e487 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e495 | unverified → expected | E | decline | true | FINISHED | true | FB | yes |  |
| e496 | unverified → expected | E | decline | true | FINISHED | true | FB | yes |  |
| e497 | unverified → expected | E | decline | true | FINISHED | true | FB | yes |  |
| e1083 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1084 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1774 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1890 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2146 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2147 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2148 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2153 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2163 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2169 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e2170 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.2.1 Quadratic/1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e619 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e660 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e764 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e765 | timeout → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e766 | timeout → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e843 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e844 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e845 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e849 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.2.1 Quadratic/1.2.1.5 (a+b x+c x^2)^p (d+e x+f x^2)^q.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e59 | timeout → verified | S | CLOSES | true | CLOSED B1 | true | NUM | yes |  |
| e66 | timeout → verified | S | CLOSES | true | CLOSED B1 | true | NUM | yes |  |
| e73 | timeout → verified | S | CLOSES | true | CLOSED B1 | true | NUM | yes |  |

### 1.2.1 Quadratic/1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e365 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e366 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.2.2 Quartic/1.2.2.2 (d x)^m (a+b x^2+c x^4)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e367 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e405 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e787 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e791 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e792 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e793 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e1005 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e1007 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e1107 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.2.2 Quartic/1.2.2.3 (d+e x^2)^m (a+b x^2+c x^4)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e153 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e168 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |

### 1.2.2 Quartic/1.2.2.4 (f x)^m (d+e x^2)^q (a+b x^2+c x^4)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e55 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e87 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e88 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e89 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e220 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.2.2 Quartic/1.2.2.6 P(x) (d x)^m (a+b x^2+c x^4)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e37 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e38 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.2.2 Quartic/1.2.2.7 P(x) (d+e x^2)^q (a+b x^2+c x^4)^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e4 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e11 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |

### 1.2.3 General/1.2.3.2 (d x)^m (a+b x^n+c x^(2 n))^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e120 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e212 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e248 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e249 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e493 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e494 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e495 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e496 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e498 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e499 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e502 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e508 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e509 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e510 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e511 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e515 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e522 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e548 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e552 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e555 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e561 | unverified → expected | E | decline | true | FINISHED | true | FB | yes |  |
| e598 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e600 | timeout → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.2.3 General/1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e108 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e116 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e124 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e132 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e136 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e140 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e142 | timeout → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.2.3 General/1.2.3.5 P(x) (d x)^m (a+b x^n+c x^(2 n))^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e16 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.2.4 Improper/1.2.4.2 (d x)^m (a x^q+b x^n+c x^(2 n-q))^p.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e121 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.3 Miscellaneous/1.3.1 Rational functions.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e176 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e181 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e187 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e188 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e191 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e234 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |

### 1.3 Miscellaneous/1.3.2 Algebraic functions.mac

| entry | old → new | chain | NUM | gate | chain replay | `radcan(rat())` ungated | MECH | kept | crash message |
|---|---|---|---|---|---|---|---|---|---|
| e151 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e154 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e190 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e191 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e192 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e196 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e197 | unverified → verified | S | decline | false | DIED B5 | true | FB | no | ```quotient' by `zero'`` |
| e198 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e199 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |
| e419 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e420 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e423 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e424 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e450 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e799 | unverified → verified | S | decline | true | FINISHED | true | FB | yes |  |
| e864 | unverified → verified | S | decline | false | FINISHED | true | FB | no |  |


## Caveats

- One run, deterministic (fixed prompt answers, committed rule set,
  fresh process per entry); no entry came close to the 150 s probe
  cap, so no replay was cut short.
- DIED Bk is the *first* crashing stage; later stages were not
  replayed — that matches the old chain, which aborted at the first
  crash (single outer errcatch).
- The replay grants the old chain unbounded time; a CLOSED Bk on an
  old-timeout entry means "would have closed given the time".
- The crash-message column is the line `errcatch` printed; two other
  crash classes (expt-0-neg, PTPTQUOTIENT) print nothing under
  errcatch in this build and would appear with an empty message —
  none occurred among the 370.
- `FB` is the **ungated** fallback result — the post run's actual
  mechanism (its gate was the no-op list form). `ELL`/`KEPT` are
  properties of the **corrected** gate, applied to the same diffs;
  they predict the post-fix classification, not the post run's.
- MECH/KEPT use the first closing chain in the driver's check order
  (self-diff before expected diff). No entry's post-run verify is
  explained by a later chain when an earlier one closes — and no
  entry came out INCONSISTENT (every post-run verify is explained by
  today's diff under the post run's own mechanism).
- The pre-record was run on pre-`89054b0` rules (see "Corrections to
  the v1 framing"); `old → new` transitions therefore mix rule- and
  harness-effects, which is what the v2 columns decompose.
