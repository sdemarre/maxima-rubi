# Class-1 corpus — attribution of the 370 entries rescued by the
`radcan(rat())` zero-test fallback (2026-08-28)

Of the **370 entries** that flipped FAIL→PASS in the 2026-08-28
full-corpus A/B around the zero-chain `radcan(rat())` fallback
(commit `fe7f1c8`), **23 were victims of the Maxima `ratsimp`
`` `quotient' by `zero' `` crash** — the bug the harness change works
around. **344 were plain simplifier gaps**: no stage of the old
8-stage chain crashed, but none could reduce the zero-diff to 0 either.
**3 were budget victims**: the old run hit the 30 s per-entry cap
before `factor` finished a diff that `factor` does close. All 370
zero-diffs close under `radcan(rat())` (FB=true on every entry), so
every flip is credited to the fallback stage.

The 23 crash victims, their stages, and their captured messages: all
crashed with the identical message `` `quotient' by `zero' ``; 22 at
stage B5 (the first direct `ratsimp` of the raw diff) and 1 at B3
(`ratsimp(expand(…))`). That is the same message as the hand-minimal
repro (`probes/maxima/probe-ratsimp-zero-divisor.mac`), so the
upstream-bug attribution for those 23 is direct, not inferred.

## TL;DR

| old failure mode | count | share | meaning |
|---|---:|---:|---|
| plain non-closure (FINISHED) | 344 | 93.0 % | `factor`/`ratsimp`/`expand` (all 8 carried variants) neither crashed nor closed; `radcan(rat())` — a different algorithm (radical normalization + full rational reduction over the algebraic extension) — closes the diff |
| crash victim (DIED) | 23 | 6.2 % | the old chain's single outer errcatch was killed by a `ratsimp` stage throwing `` `quotient' by `zero' ``; the fallback (gated, errcatched) closes the diff |
| budget (CLOSED) | 3 | 0.8 % | the chain *does* close (at B1, `factor`) but the old run's 30 s cap fired first; the new run completed in time |

Cross-tabulated with the A/B transitions:

| | FINISHED | DIED | CLOSED | total |
|---|---:|---:|---:|---:|
| unverified → verified | 336 | 22 | 0 | 358 |
| unverified → expected | 4 | 0 | 0 | 4 |
| timeout → verified | 4 | 1 | 3 | 8 |
| total | 344 | 23 | 3 | 370 |

(For the 4 unverified → expected entries the E-chain — the
expected-answer diff — is the one that closed; it is the `E` chain in
the table below.)

## Inputs

- `test/corpus_class1.pre-radcan-fallback.out` — the pre-fallback
  merged record (2026-08-27 13:02 UTC; 19,731 passed / 5,966 failed);
- `test/corpus_class1.out` — the post-fallback merged record
  (2026-08-28 10:03 UTC; 20,097 passed / 5,600 failed);
- commit `fe7f1c8` (branch `harness-radcan-fallback`) — the harness
  change itself;
- `probes/maxima/probe-radcan-attribution.{py,run,out}` — the
  re-runnable probe and its stamped output (2026-08-28 11:02:37 UTC);
- build: Maxima 5.50.0 (build date 2026-08-20 21:36:22), SBCL 2.6.7.

## Method

`sh probes/maxima/probe-radcan-attribution.run` — 370 fresh maxima
subprocesses (one per entry, 24-way parallel, 150 s per-entry cap; no
entry came close to the cap), each running:

1. `rubi(f, x)` with the fixed 40-`pos`/20-`no` prompt answers — the
   same answers the corpus driver uses, so the reproduced answer is
   the one the A/B runs verified;
2. a **replay of the old zero-chain symbolic stages** on the zero-diff
   the new run closed (the self-diff for →verified entries, the
   expected-answer diff for →expected entries): the same 8 stages in
   the same order with the same carried values, but each stage in its
   own `errcatch` so a crash is *recorded* (DIED Bk) instead of
   killing the chain, and a closure is recorded (CLOSED Bk). A chain
   that neither crashes nor closes reports FINISHED. The replay stops
   at the first crash, matching the old chain's behaviour (its single
   outer errcatch aborted there);
3. the fallback exactly as the new harness runs it — elliptic-gated
   (`freeof` of the six `elliptic_*` functions), then
   `errcatch(radcan(rat(D)))` — recorded as FB=true (closes to exact
   0), FB=false, FB=GATED (elliptic), FB=CRASH. No entry was GATED or
   CRASH; all 370 are FB=true.

Replay result = the old failure mode, because the old run's symbolic
chain is this replay minus the per-stage detection (crash → its outer
errcatch returned `[]` → unverified; no crash, no closure → unverified;
still running at the 30 s cap → timeout).

Crash-message capture: in this build `errcatch` prints a caught error
as a bare line with no trailing anchor, and two crash classes (the
`expt` and `PTPTQUOTIENT` families) print nothing at all under
errcatch (measured 2026-08-28, `zc_errfmt` ad-hoc). The probe takes
the column-0 non-echo lines inside each chain window. All 23 DIED
entries printed the message; none were silent.

## The 23 crash victims (all `` `quotient' by `zero' ``)

| entry | file | stage | old → new |
|---|---|---|---|
| e2588 | 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | B3 | unverified → verified |
| e826 | 1.1.3.2 (c x)^m (a+b x^n)^p | B5 | unverified → verified |
| e214 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified |
| e529 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified |
| e530 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified |
| e531 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified |
| e540 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | timeout → verified |
| e541 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified |
| e542 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified |
| e543 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified |
| e544 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified |
| e545 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified |
| e546 | 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | B5 | unverified → verified |
| e2060 | 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | B5 | unverified → verified |
| e660 | 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | B5 | unverified → verified |
| e1005 | 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | B5 | unverified → verified |
| e153 | 1.2.2.3 (d+e x^2)^m (a+b x^2+c x^4)^p | B5 | unverified → verified |
| e168 | 1.2.2.3 (d+e x^2)^m (a+b x^2+c x^4)^p | B5 | unverified → verified |
| e4 | 1.2.2.7 P(x) (d+e x^2)^q (a+b x^2+c x^4)^p | B5 | unverified → verified |
| e11 | 1.2.2.7 P(x) (d+e x^2)^q (a+b x^2+c x^4)^p | B5 | unverified → verified |
| e190 | 1.3.2 Algebraic functions | B5 | unverified → verified |
| e196 | 1.3.2 Algebraic functions | B5 | unverified → verified |
| e197 | 1.3.2 Algebraic functions | B5 | unverified → verified |

Notes:

- B5 = `ratsimp(MR_de)` (the first direct ratsimp of the raw diff);
  B3 = `ratsimp(expand(MR_d))`. In both cases the crash is the
  `ratsimp` call itself — consistent with the root-cause analysis
  (unguarded inversion at `oldgcd`→`algnormal`→`rainv` over redundant
  algebraic generators in the ring).
- e541/e543/e544 are the TDD RED targets that started the harness
  change; e540 is the timeout-class sibling in the same file.
- All 23 diffs close under the fallback (FB=true), so in the new
  run the (gated, errcatched) fallback runs where the old outer
  errcatch used to absorb the crash.

## The 3 budget victims

| entry | file | replay | old → new |
|---|---|---|---|
| e59 | 1.2.1.5 (a+b x+c x^2)^p (d+e x+f x^2)^q | CLOSED B1 | timeout → verified |
| e66 | 1.2.1.5 (a+b x+c x^2)^p (d+e x+f x^2)^q | CLOSED B1 | timeout → verified |
| e73 | 1.2.1.5 (a+b x+c x^2)^p (d+e x+f x^2)^q | CLOSED B1 | timeout → verified |

`factor` closes all three self-diffs (B1); the old runs hit the 30 s
cap before `factor` returned (old t = 30.0 s, at the cap), the new
runs completed in time. Load/borderline variance, not an algorithm
change — the fallback also closes them (FB=true), but the chain no
longer needs it.

## The 344 plain non-closures

No stage of the old chain crashed on these; none closed. The
`factor`/`ratsimp`/`expand` machinery cannot reduce the zero-diff to
0, but `radcan(rat())` can — it performs radical normalization and
full rational reduction over the algebraic extension, which the
8-stage chain's variants never reach. This is a simplifier coverage
gap, not a Maxima bug: fixing the zero-divisor bug alone would have
recovered 23 of the 370, not 370.

## Full list — all 370 entries

`chain`: S = self-diff (`diff(rubi(f,x), x) - f`), E = expected-answer
diff (`diff(rubi(f,x) - E, x)`); E2 where an entry has two expected
answers. `old-chain replay`: FINISHED (no crash, no closure), DIED Bk
(crashed at stage Bk), CLOSED Bk (closed at stage Bk). Re-runnable via
`sh probes/maxima/probe-radcan-attribution.run` (raw stamped output in
`probes/maxima/probe-radcan-attribution.out`).


### 1.1.1 Linear/1.1.1.2 (a+b x)^m (c+d x)^n.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e368 | unverified → verified | S | FINISHED |  | true |
| e739 | unverified → verified | S | FINISHED |  | true |
| e740 | unverified → verified | S | FINISHED |  | true |
| e1085 | unverified → verified | S | FINISHED |  | true |
| e1086 | unverified → verified | S | FINISHED |  | true |
| e1087 | unverified → verified | S | FINISHED |  | true |
| e1099 | unverified → verified | S | FINISHED |  | true |
| e1100 | unverified → verified | S | FINISHED |  | true |
| e1101 | unverified → verified | S | FINISHED |  | true |
| e1102 | unverified → verified | S | FINISHED |  | true |
| e1103 | unverified → verified | S | FINISHED |  | true |
| e1859 | unverified → verified | S | FINISHED |  | true |
| e1860 | unverified → verified | S | FINISHED |  | true |
| e1869 | unverified → verified | S | FINISHED |  | true |
| e1870 | unverified → verified | S | FINISHED |  | true |
| e1871 | unverified → verified | S | FINISHED |  | true |
| e1882 | unverified → verified | S | FINISHED |  | true |

### 1.1.1 Linear/1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e355 | unverified → verified | S | FINISHED |  | true |
| e356 | unverified → verified | S | FINISHED |  | true |
| e357 | unverified → verified | S | FINISHED |  | true |
| e361 | unverified → verified | S | FINISHED |  | true |
| e362 | unverified → verified | S | FINISHED |  | true |
| e363 | unverified → verified | S | FINISHED |  | true |
| e367 | unverified → verified | S | FINISHED |  | true |
| e368 | unverified → verified | S | FINISHED |  | true |
| e369 | unverified → verified | S | FINISHED |  | true |
| e799 | unverified → verified | S | FINISHED |  | true |
| e808 | unverified → verified | S | FINISHED |  | true |
| e809 | unverified → verified | S | FINISHED |  | true |
| e810 | unverified → verified | S | FINISHED |  | true |
| e811 | unverified → verified | S | FINISHED |  | true |
| e812 | unverified → verified | S | FINISHED |  | true |
| e813 | unverified → verified | S | FINISHED |  | true |
| e814 | unverified → verified | S | FINISHED |  | true |
| e815 | unverified → verified | S | FINISHED |  | true |
| e911 | unverified → verified | S | FINISHED |  | true |
| e912 | unverified → verified | S | FINISHED |  | true |
| e914 | unverified → verified | S | FINISHED |  | true |
| e921 | unverified → verified | S | FINISHED |  | true |
| e922 | unverified → verified | S | FINISHED |  | true |
| e2197 | unverified → verified | S | FINISHED |  | true |
| e2198 | unverified → verified | S | FINISHED |  | true |
| e2209 | unverified → verified | S | FINISHED |  | true |
| e2210 | unverified → verified | S | FINISHED |  | true |
| e2222 | unverified → verified | S | FINISHED |  | true |
| e2223 | unverified → verified | S | FINISHED |  | true |
| e2231 | unverified → verified | S | FINISHED |  | true |
| e2232 | unverified → verified | S | FINISHED |  | true |
| e2239 | unverified → verified | S | FINISHED |  | true |
| e2240 | unverified → verified | S | FINISHED |  | true |
| e2248 | unverified → verified | S | FINISHED |  | true |
| e2249 | unverified → verified | S | FINISHED |  | true |
| e2588 | unverified → verified | S | DIED B3 | ``quotient' by `zero'` | true |
| e3039 | unverified → verified | S | FINISHED |  | true |
| e3040 | unverified → verified | S | FINISHED |  | true |
| e3068 | unverified → verified | S | FINISHED |  | true |
| e3069 | unverified → verified | S | FINISHED |  | true |
| e3076 | unverified → verified | S | FINISHED |  | true |
| e3077 | unverified → verified | S | FINISHED |  | true |
| e3078 | unverified → verified | S | FINISHED |  | true |
| e3084 | unverified → verified | S | FINISHED |  | true |
| e3085 | unverified → verified | S | FINISHED |  | true |
| e3086 | unverified → verified | S | FINISHED |  | true |
| e3092 | unverified → verified | S | FINISHED |  | true |
| e3093 | unverified → verified | S | FINISHED |  | true |
| e3095 | unverified → verified | S | FINISHED |  | true |

### 1.1.1 Linear/1.1.1.4 (a+b x)^m (c+d x)^n (e+f x)^p (g+h x)^q.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e129 | unverified → verified | S | FINISHED |  | true |
| e132 | unverified → verified | S | FINISHED |  | true |
| e133 | unverified → verified | S | FINISHED |  | true |
| e134 | unverified → verified | S | FINISHED |  | true |
| e135 | unverified → verified | S | FINISHED |  | true |

### 1.1.1 Linear/1.1.1.5 P(x) (a+b x)^m (c+d x)^n.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e25 | unverified → verified | S | FINISHED |  | true |
| e26 | unverified → verified | S | FINISHED |  | true |

### 1.1.1 Linear/1.1.1.6 P(x) (a+b x)^m (c+d x)^n (e+f x)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e56 | unverified → verified | S | FINISHED |  | true |

### 1.1.2 Quadratic/1.1.2.6 (g x)^m (a+b x^2)^p (c+d x^2)^q (e+f x^2)^r.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e1 | unverified → verified | S | FINISHED |  | true |
| e2 | unverified → verified | S | FINISHED |  | true |
| e8 | unverified → verified | S | FINISHED |  | true |
| e9 | unverified → verified | S | FINISHED |  | true |
| e10 | unverified → verified | S | FINISHED |  | true |
| e11 | unverified → verified | S | FINISHED |  | true |
| e15 | unverified → verified | S | FINISHED |  | true |
| e16 | unverified → verified | S | FINISHED |  | true |
| e17 | unverified → verified | S | FINISHED |  | true |
| e18 | unverified → verified | S | FINISHED |  | true |

### 1.1.2 Quadratic/1.1.2.8 P(x) (c x)^m (a+b x^2)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e172 | unverified → verified | S | FINISHED |  | true |
| e173 | unverified → verified | S | FINISHED |  | true |

### 1.1.3 General/1.1.3.2 (c x)^m (a+b x^n)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e821 | unverified → verified | S | FINISHED |  | true |
| e826 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e862 | unverified → verified | S | FINISHED |  | true |
| e871 | unverified → verified | S | FINISHED |  | true |
| e2243 | unverified → verified | S | FINISHED |  | true |
| e2260 | unverified → verified | S | FINISHED |  | true |
| e2471 | unverified → verified | S | FINISHED |  | true |
| e2473 | unverified → verified | S | FINISHED |  | true |
| e2474 | unverified → verified | S | FINISHED |  | true |
| e2476 | unverified → verified | S | FINISHED |  | true |
| e2478 | unverified → verified | S | FINISHED |  | true |
| e2479 | unverified → verified | S | FINISHED |  | true |
| e2590 | unverified → verified | S | FINISHED |  | true |
| e2591 | unverified → verified | S | FINISHED |  | true |
| e2592 | unverified → verified | S | FINISHED |  | true |
| e2593 | unverified → verified | S | FINISHED |  | true |
| e2596 | unverified → verified | S | FINISHED |  | true |
| e2597 | unverified → verified | S | FINISHED |  | true |
| e2598 | unverified → verified | S | FINISHED |  | true |
| e2599 | unverified → verified | S | FINISHED |  | true |
| e2600 | unverified → verified | S | FINISHED |  | true |
| e2601 | unverified → verified | S | FINISHED |  | true |
| e2602 | unverified → verified | S | FINISHED |  | true |
| e2605 | unverified → verified | S | FINISHED |  | true |
| e2606 | unverified → verified | S | FINISHED |  | true |
| e2607 | unverified → verified | S | FINISHED |  | true |
| e2608 | unverified → verified | S | FINISHED |  | true |
| e2609 | unverified → verified | S | FINISHED |  | true |
| e2610 | unverified → verified | S | FINISHED |  | true |
| e2611 | unverified → verified | S | FINISHED |  | true |
| e2614 | unverified → verified | S | FINISHED |  | true |
| e2615 | unverified → verified | S | FINISHED |  | true |
| e2616 | unverified → verified | S | FINISHED |  | true |
| e2617 | unverified → verified | S | FINISHED |  | true |
| e2618 | unverified → verified | S | FINISHED |  | true |
| e2619 | unverified → verified | S | FINISHED |  | true |
| e2627 | unverified → verified | S | FINISHED |  | true |
| e2632 | unverified → verified | S | FINISHED |  | true |
| e2635 | unverified → verified | S | FINISHED |  | true |
| e2636 | unverified → verified | S | FINISHED |  | true |
| e2639 | unverified → verified | S | FINISHED |  | true |
| e2653 | unverified → verified | S | FINISHED |  | true |
| e2664 | unverified → verified | S | FINISHED |  | true |
| e2665 | unverified → verified | S | FINISHED |  | true |
| e2691 | unverified → verified | S | FINISHED |  | true |
| e2714 | unverified → verified | S | FINISHED |  | true |
| e2715 | unverified → verified | S | FINISHED |  | true |
| e2716 | unverified → verified | S | FINISHED |  | true |
| e2737 | unverified → verified | S | FINISHED |  | true |
| e2738 | unverified → verified | S | FINISHED |  | true |
| e2748 | unverified → verified | S | FINISHED |  | true |
| e2751 | unverified → verified | S | FINISHED |  | true |
| e2752 | unverified → verified | S | FINISHED |  | true |
| e2753 | unverified → verified | S | FINISHED |  | true |
| e2754 | unverified → verified | S | FINISHED |  | true |
| e2755 | unverified → verified | S | FINISHED |  | true |
| e2758 | unverified → verified | S | FINISHED |  | true |
| e2759 | unverified → verified | S | FINISHED |  | true |
| e2762 | unverified → verified | S | FINISHED |  | true |
| e2765 | unverified → verified | S | FINISHED |  | true |
| e2766 | unverified → verified | S | FINISHED |  | true |
| e2767 | unverified → verified | S | FINISHED |  | true |
| e2768 | unverified → verified | S | FINISHED |  | true |
| e2769 | unverified → verified | S | FINISHED |  | true |
| e2770 | unverified → verified | S | FINISHED |  | true |
| e2771 | unverified → verified | S | FINISHED |  | true |
| e2772 | unverified → verified | S | FINISHED |  | true |
| e2773 | unverified → verified | S | FINISHED |  | true |
| e2910 | unverified → verified | S | FINISHED |  | true |
| e2971 | unverified → verified | S | FINISHED |  | true |
| e2973 | unverified → verified | S | FINISHED |  | true |
| e2974 | unverified → verified | S | FINISHED |  | true |
| e2991 | unverified → verified | S | FINISHED |  | true |
| e2995 | unverified → verified | S | FINISHED |  | true |
| e3063 | unverified → verified | S | FINISHED |  | true |
| e3064 | unverified → verified | S | FINISHED |  | true |
| e3065 | unverified → verified | S | FINISHED |  | true |
| e3067 | unverified → verified | S | FINISHED |  | true |
| e3068 | unverified → verified | S | FINISHED |  | true |
| e3069 | unverified → verified | S | FINISHED |  | true |
| e3070 | unverified → verified | S | FINISHED |  | true |
| e3071 | unverified → verified | S | FINISHED |  | true |

### 1.1.3 General/1.1.3.3 (a+b x^n)^p (c+d x^n)^q.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e189 | unverified → verified | S | FINISHED |  | true |
| e190 | unverified → verified | S | FINISHED |  | true |
| e196 | unverified → verified | S | FINISHED |  | true |
| e197 | unverified → verified | S | FINISHED |  | true |
| e199 | unverified → verified | S | FINISHED |  | true |
| e200 | unverified → verified | S | FINISHED |  | true |
| e201 | unverified → verified | S | FINISHED |  | true |
| e202 | unverified → verified | S | FINISHED |  | true |
| e206 | unverified → verified | S | FINISHED |  | true |
| e207 | unverified → verified | S | FINISHED |  | true |
| e208 | unverified → verified | S | FINISHED |  | true |
| e209 | unverified → verified | S | FINISHED |  | true |

### 1.1.3 General/1.1.3.4 (e x)^m (a+b x^n)^p (c+d x^n)^q.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e856 | unverified → verified | S | FINISHED |  | true |
| e861 | unverified → verified | S | FINISHED |  | true |
| e864 | unverified → verified | S | FINISHED |  | true |
| e871 | unverified → verified | S | FINISHED |  | true |
| e872 | unverified → verified | S | FINISHED |  | true |
| e873 | unverified → verified | S | FINISHED |  | true |
| e874 | unverified → verified | S | FINISHED |  | true |
| e877 | unverified → verified | S | FINISHED |  | true |
| e878 | unverified → verified | S | FINISHED |  | true |
| e879 | unverified → verified | S | FINISHED |  | true |
| e880 | unverified → verified | S | FINISHED |  | true |
| e887 | unverified → verified | S | FINISHED |  | true |
| e913 | unverified → verified | S | FINISHED |  | true |

### 1.1.3 General/1.1.3.6 (g x)^m (a+b x^n)^p (c+d x^n)^q (e+f x^n)^r.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e5 | unverified → verified | S | FINISHED |  | true |
| e6 | unverified → verified | S | FINISHED |  | true |
| e12 | unverified → verified | S | FINISHED |  | true |
| e13 | unverified → verified | S | FINISHED |  | true |
| e19 | unverified → verified | S | FINISHED |  | true |
| e20 | unverified → verified | S | FINISHED |  | true |
| e21 | unverified → verified | S | FINISHED |  | true |
| e22 | unverified → verified | S | FINISHED |  | true |
| e23 | unverified → verified | S | FINISHED |  | true |
| e24 | unverified → verified | S | FINISHED |  | true |
| e25 | unverified → verified | S | FINISHED |  | true |
| e27 | unverified → verified | S | FINISHED |  | true |
| e29 | unverified → verified | S | FINISHED |  | true |
| e30 | unverified → verified | S | FINISHED |  | true |
| e31 | unverified → verified | S | FINISHED |  | true |
| e32 | unverified → verified | S | FINISHED |  | true |
| e33 | unverified → verified | S | FINISHED |  | true |

### 1.1.3 General/1.1.3.8 P(x) (c x)^m (a+b x^n)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e210 | unverified → verified | S | FINISHED |  | true |
| e213 | unverified → verified | S | FINISHED |  | true |
| e214 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e220 | unverified → verified | S | FINISHED |  | true |
| e529 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e530 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e531 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e540 | timeout → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e541 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e542 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e543 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e544 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e545 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e546 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e576 | unverified → verified | S | FINISHED |  | true |
| e592 | unverified → verified | S | FINISHED |  | true |
| e594 | unverified → verified | S | FINISHED |  | true |

### 1.1.4 Improper/1.1.4.2 (c x)^m (a x^j+b x^n)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e444 | unverified → verified | S | FINISHED |  | true |
| e445 | unverified → verified | S | FINISHED |  | true |
| e446 | unverified → verified | S | FINISHED |  | true |
| e451 | unverified → verified | S | FINISHED |  | true |
| e452 | unverified → verified | S | FINISHED |  | true |

### 1.1.4 Improper/1.1.4.3 (e x)^m (a x^j+b x^k)^p (c+d x^n)^q.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e252 | unverified → verified | S | FINISHED |  | true |
| e275 | unverified → verified | S | FINISHED |  | true |
| e283 | unverified → verified | S | FINISHED |  | true |

### 1.2.1 Quadratic/1.2.1.2 (d+e x)^m (a+b x+c x^2)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e112 | unverified → verified | S | FINISHED |  | true |
| e113 | unverified → verified | S | FINISHED |  | true |
| e114 | unverified → verified | S | FINISHED |  | true |
| e824 | unverified → verified | S | FINISHED |  | true |
| e894 | unverified → verified | S | FINISHED |  | true |
| e895 | unverified → verified | S | FINISHED |  | true |
| e896 | unverified → verified | S | FINISHED |  | true |
| e897 | unverified → verified | S | FINISHED |  | true |
| e901 | unverified → verified | S | FINISHED |  | true |
| e902 | unverified → verified | S | FINISHED |  | true |
| e903 | unverified → verified | S | FINISHED |  | true |
| e904 | unverified → verified | S | FINISHED |  | true |
| e905 | unverified → verified | S | FINISHED |  | true |
| e911 | unverified → verified | S | FINISHED |  | true |
| e912 | unverified → verified | S | FINISHED |  | true |
| e913 | unverified → verified | S | FINISHED |  | true |
| e918 | unverified → verified | S | FINISHED |  | true |
| e919 | unverified → verified | S | FINISHED |  | true |
| e920 | unverified → verified | S | FINISHED |  | true |
| e921 | unverified → verified | S | FINISHED |  | true |
| e922 | unverified → verified | S | FINISHED |  | true |
| e933 | unverified → verified | S | FINISHED |  | true |
| e934 | unverified → verified | S | FINISHED |  | true |
| e935 | unverified → verified | S | FINISHED |  | true |
| e936 | unverified → verified | S | FINISHED |  | true |
| e943 | unverified → verified | S | FINISHED |  | true |
| e945 | unverified → verified | S | FINISHED |  | true |
| e946 | unverified → verified | S | FINISHED |  | true |
| e1739 | unverified → verified | S | FINISHED |  | true |
| e2060 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |

### 1.2.1 Quadratic/1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e485 | unverified → verified | S | FINISHED |  | true |
| e486 | unverified → verified | S | FINISHED |  | true |
| e487 | unverified → verified | S | FINISHED |  | true |
| e495 | unverified → expected | E | FINISHED |  | true |
| e496 | unverified → expected | E | FINISHED |  | true |
| e497 | unverified → expected | E | FINISHED |  | true |
| e1083 | unverified → verified | S | FINISHED |  | true |
| e1084 | unverified → verified | S | FINISHED |  | true |
| e1774 | unverified → verified | S | FINISHED |  | true |
| e1890 | unverified → verified | S | FINISHED |  | true |
| e2146 | unverified → verified | S | FINISHED |  | true |
| e2147 | unverified → verified | S | FINISHED |  | true |
| e2148 | unverified → verified | S | FINISHED |  | true |
| e2153 | unverified → verified | S | FINISHED |  | true |
| e2163 | unverified → verified | S | FINISHED |  | true |
| e2169 | unverified → verified | S | FINISHED |  | true |
| e2170 | unverified → verified | S | FINISHED |  | true |

### 1.2.1 Quadratic/1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e619 | unverified → verified | S | FINISHED |  | true |
| e660 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e764 | unverified → verified | S | FINISHED |  | true |
| e765 | timeout → verified | S | FINISHED |  | true |
| e766 | timeout → verified | S | FINISHED |  | true |
| e843 | unverified → verified | S | FINISHED |  | true |
| e844 | unverified → verified | S | FINISHED |  | true |
| e845 | unverified → verified | S | FINISHED |  | true |
| e849 | unverified → verified | S | FINISHED |  | true |

### 1.2.1 Quadratic/1.2.1.5 (a+b x+c x^2)^p (d+e x+f x^2)^q.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e59 | timeout → verified | S | CLOSED B1 |  | true |
| e66 | timeout → verified | S | CLOSED B1 |  | true |
| e73 | timeout → verified | S | CLOSED B1 |  | true |

### 1.2.1 Quadratic/1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e365 | unverified → verified | S | FINISHED |  | true |
| e366 | unverified → verified | S | FINISHED |  | true |

### 1.2.2 Quartic/1.2.2.2 (d x)^m (a+b x^2+c x^4)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e367 | unverified → verified | S | FINISHED |  | true |
| e405 | unverified → verified | S | FINISHED |  | true |
| e787 | unverified → verified | S | FINISHED |  | true |
| e791 | unverified → verified | S | FINISHED |  | true |
| e792 | unverified → verified | S | FINISHED |  | true |
| e793 | unverified → verified | S | FINISHED |  | true |
| e1005 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e1007 | unverified → verified | S | FINISHED |  | true |
| e1107 | unverified → verified | S | FINISHED |  | true |

### 1.2.2 Quartic/1.2.2.3 (d+e x^2)^m (a+b x^2+c x^4)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e153 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e168 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |

### 1.2.2 Quartic/1.2.2.4 (f x)^m (d+e x^2)^q (a+b x^2+c x^4)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e55 | unverified → verified | S | FINISHED |  | true |
| e87 | unverified → verified | S | FINISHED |  | true |
| e88 | unverified → verified | S | FINISHED |  | true |
| e89 | unverified → verified | S | FINISHED |  | true |
| e220 | unverified → verified | S | FINISHED |  | true |

### 1.2.2 Quartic/1.2.2.6 P(x) (d x)^m (a+b x^2+c x^4)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e37 | unverified → verified | S | FINISHED |  | true |
| e38 | unverified → verified | S | FINISHED |  | true |

### 1.2.2 Quartic/1.2.2.7 P(x) (d+e x^2)^q (a+b x^2+c x^4)^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e4 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e11 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |

### 1.2.3 General/1.2.3.2 (d x)^m (a+b x^n+c x^(2 n))^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e120 | unverified → verified | S | FINISHED |  | true |
| e212 | unverified → verified | S | FINISHED |  | true |
| e248 | unverified → verified | S | FINISHED |  | true |
| e249 | unverified → verified | S | FINISHED |  | true |
| e493 | unverified → verified | S | FINISHED |  | true |
| e494 | unverified → verified | S | FINISHED |  | true |
| e495 | unverified → verified | S | FINISHED |  | true |
| e496 | unverified → verified | S | FINISHED |  | true |
| e498 | unverified → verified | S | FINISHED |  | true |
| e499 | unverified → verified | S | FINISHED |  | true |
| e502 | unverified → verified | S | FINISHED |  | true |
| e508 | unverified → verified | S | FINISHED |  | true |
| e509 | unverified → verified | S | FINISHED |  | true |
| e510 | unverified → verified | S | FINISHED |  | true |
| e511 | unverified → verified | S | FINISHED |  | true |
| e515 | unverified → verified | S | FINISHED |  | true |
| e522 | unverified → verified | S | FINISHED |  | true |
| e548 | unverified → verified | S | FINISHED |  | true |
| e552 | unverified → verified | S | FINISHED |  | true |
| e555 | unverified → verified | S | FINISHED |  | true |
| e561 | unverified → expected | E | FINISHED |  | true |
| e598 | unverified → verified | S | FINISHED |  | true |
| e600 | timeout → verified | S | FINISHED |  | true |

### 1.2.3 General/1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e108 | unverified → verified | S | FINISHED |  | true |
| e116 | unverified → verified | S | FINISHED |  | true |
| e124 | unverified → verified | S | FINISHED |  | true |
| e132 | unverified → verified | S | FINISHED |  | true |
| e136 | unverified → verified | S | FINISHED |  | true |
| e140 | unverified → verified | S | FINISHED |  | true |
| e142 | timeout → verified | S | FINISHED |  | true |

### 1.2.3 General/1.2.3.5 P(x) (d x)^m (a+b x^n+c x^(2 n))^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e16 | unverified → verified | S | FINISHED |  | true |

### 1.2.4 Improper/1.2.4.2 (d x)^m (a x^q+b x^n+c x^(2 n-q))^p.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e121 | unverified → verified | S | FINISHED |  | true |

### 1.3 Miscellaneous/1.3.1 Rational functions.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e176 | unverified → verified | S | FINISHED |  | true |
| e181 | unverified → verified | S | FINISHED |  | true |
| e187 | unverified → verified | S | FINISHED |  | true |
| e188 | unverified → verified | S | FINISHED |  | true |
| e191 | unverified → verified | S | FINISHED |  | true |
| e234 | unverified → verified | S | FINISHED |  | true |

### 1.3 Miscellaneous/1.3.2 Algebraic functions.mac

| entry | old → new | chain | old-chain replay | crash message | `radcan(rat())` closes |
|---|---|---|---|---|---|
| e151 | unverified → verified | S | FINISHED |  | true |
| e154 | unverified → verified | S | FINISHED |  | true |
| e190 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e191 | unverified → verified | S | FINISHED |  | true |
| e192 | unverified → verified | S | FINISHED |  | true |
| e196 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e197 | unverified → verified | S | DIED B5 | ``quotient' by `zero'` | true |
| e198 | unverified → verified | S | FINISHED |  | true |
| e199 | unverified → verified | S | FINISHED |  | true |
| e419 | unverified → verified | S | FINISHED |  | true |
| e420 | unverified → verified | S | FINISHED |  | true |
| e423 | unverified → verified | S | FINISHED |  | true |
| e424 | unverified → verified | S | FINISHED |  | true |
| e450 | unverified → verified | S | FINISHED |  | true |
| e799 | unverified → verified | S | FINISHED |  | true |
| e864 | unverified → verified | S | FINISHED |  | true |


## Caveats

- One run, deterministic (fixed prompt answers, committed rule set,
  fresh process per entry); no entry came close to the 150 s probe
  cap, so no replay was cut short.
- DIED Bk is the *first* crashing stage; later stages were not
  replayed — that matches the old chain, which aborted at the first
  crash (single outer errcatch).
- The replay grants the old chain unbounded time; a CLOSED Bk on an
  old-timeout entry means "would have closed given the time" (the
  three CLOSED entries needed only B1).
- The crash-message column is the line `errcatch` printed; two other
  crash classes (expt-0-neg, PTPTQUOTIENT) print nothing under
  errcatch in this build and would appear with an empty message —
  none occurred among the 370.
