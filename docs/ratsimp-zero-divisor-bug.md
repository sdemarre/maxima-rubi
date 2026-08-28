# Maxima `ratsimp` zero-divisor bug — research record (2026-08-27/28)

`ratsimp` — and `radcan(rat())`, which runs the same algebraic-rational
machinery — can crash the process with the message `` `quotient' by
`zero' `` on algebraic expressions whose algebraic-number ring contains
zero divisors. Discovered in this project's class-1 corpus zero-test
harness (2026-08-27), minimized to a hand-typed four-term expression
(2026-08-28), root-caused in the Maxima source. **24 distinct
encountered expressions** trigger it: the original case, its minimal
form, 23 natural-occurrence class-1 corpus entries (crash via the
`ratsimp` zero-test stage), and 1 entry that reaches the same crash
through `radcan(rat())`. All measurements on Maxima 5.50.0 (build date
2026-08-20 21:36:22), SBCL 2.6.7.

Committed evidence:

- `probes/maxima/probe-ratsimp-zero-divisor.{mac,run,out}` — the
  hand-minimal repro, both `ratsimp` calls crash
  (`` `quotient' by `zero' ``), stamped;
- `probes/maxima/probe-ratsimp-zero-divisor-variants.{mac,run,out}` —
  the constant-variant sweep: the crash tracks the unit-power pattern
  across consecutive powers, not specific integers (§3.1);
- `probes/maxima/probe-radcan-attribution.{py,run,out}` +
  `docs/corpus-radcan-fallback-attribution.md` — the full-370
  attribution run that identified and message-confirmed the 23 corpus
  crash victims;
- Maxima source at `/home/serge/src/external/maxima/src/` (5.50.0).

The intermediate probes (repro → dump → bisect → trap → backtrace →
variant sweep) are untracked in the `test-ratsimp` worktree
(`.worktrees/test-ratsimp/`); their conclusions are promoted into the
committed probes cited above.

## 1. Symptom

```
`quotient' by `zero'
 -- an error. To debug this try: debugmode(true);
```

- Bare (no `errcatch`): kills the maxima batch (non-zero exit, no
  further output).
- Under `errcatch`: the message is printed as a bare line, the call
  returns `[]` (this build's convention — see
  `probes/maxima/probe-errcatch-semantics.out`), the process survives.
- Latency: ~20 s in the minimal repro (the crash is deep in the
  rational-reduction work, not at the top of the call).

## 2. Discovery context

The class-1 harness verifies `rubi`'s answers by differentiating:
`D := diff(rubi(f, x), x) - f`, then an 8-stage
`factor`/`ratsimp`/`expand` zero-chain must reduce `D` to 0. On
2026-08-27 the stage `ratsimp(D)` began crashing the whole chain (its
single outer `errcatch` absorbed the crash, the entry was classified
`unverified`, and the batch survived only because of that errcatch).
First case: `f = sqrt(x+2)/(3*x^2+4)` — `ratsimp(diff(rubi(f,x), x))`
crashed.

Probe chain (worktree `test-ratsimp`, untracked; `== ` prefixed
verdicts on stdout):

| probe | question | result |
|---|---|---|
| `repro_ratsimp.mac` | does it repro with rubi loaded? | yes, crash kills batch before `== GREEN` |
| `repro_dump.mac` | capture the answer as a raw Lisp tree (bypasses the crashing display path) | `ans.lisp` dumped |
| `probe_standalone.mac`, `probe_struct.mac` | is the reloaded tree corrupt (load/assign damage)? | no — tree reloads, parts string, structure intact |
| `probe_diff_ratsimp.mac` | does the crash reproduce with no rubi at all? | yes — `ratsimp(diff(ans, x))` on the dumped tree |
| `probe_minimize.mac` … `probe_minimize5.mac` | which part of the answer carries it? pair-bisect the answer's 4-term sum, then bisect the crashing diff's 4 summands | the crash needs the specific combination of all four terms of the diff |
| `repro_minimal.mac` | can it be typed by hand, no dump? | yes — the `t1..t4` below |
| (variant sweeps, iterated in the worktree; files were reused across iterations) | structure or constants? 56 structured variants of the minimal form | none of the 56 crash — the constants matter, not just the radical shape; the conclusive sweep is now committed: `probe-ratsimp-zero-divisor-variants.mac` (§3.1) |
| `probe_trap.mac`, `probe_bt.mac` | where exactly? traps on `ratinvert`/`ratreduce`; bare call with `*debugger-hook` backtrace | the crash is in the inversion path (`rainv`/`bprog`), not the reduce path |

## 3. The original case and its minimal form

Integrand: `sqrt(x+2)/(3*x^2+4)`. Crash: `ratsimp(diff(rubi(f, x), x))`.

Minimal hand-typed form (committed, `probe-ratsimp-zero-divisor.mac`;
`x` the variable; both calls crash):

```
t1 : (3^(1/4)*(2-sqrt(3))*sqrt(sqrt(3)+2)*(5822*sqrt(3)-10084))
     /(2*(sqrt(3)-2)*sqrt(x+2)*((3^(1/4)*sqrt(2-sqrt(3))*sqrt(x+2)+sqrt(2-sqrt(3))*sqrt(sqrt(3)+2))^2/(sqrt(3)-2)^2+1))
t2 : (3^(1/4)*(2-sqrt(3))*sqrt(sqrt(3)+2)*(5822*sqrt(3)-10084))
     /(2*(sqrt(3)-2)*sqrt(x+2)*((3^(1/4)*sqrt(2-sqrt(3))*sqrt(x+2)-sqrt(2-sqrt(3))*sqrt(sqrt(3)+2))^2/(sqrt(3)-2)^2+1))
t3 : ((10864*sqrt(3)-18817)*((sqrt(3)*sqrt(sqrt(3)+2))/sqrt(x+2)+3^(3/4)))
     /(2*sqrt(3)*sqrt(sqrt(3)+2)*sqrt(x+2)+3^(3/4)*x+2*3^(3/4)+4*3^(1/4))
t4 : ((18817-10864*sqrt(3))*(3^(3/4)-(sqrt(3)*sqrt(sqrt(3)+2))/sqrt(x+2)))
     /(-(2*sqrt(3)*sqrt(sqrt(3)+2)*sqrt(x+2))+3^(3/4)*x+2*3^(3/4)+4*3^(1/4))

ratsimp(t1+t2+t3+t4)                                                    -> `quotient' by `zero'
ratsimp(2*(t1+t2+t3+t4)*sqrt(sqrt(3)+2)*(150536*3^(3/4)-86912*3^(5/4))) -> `quotient' by `zero'
```

(exact text, verbatim from the committed probe; `x` the variable.)

Shared structure:

- **Redundant generators in one algebraic varlist**: `3^(1/4)` and
  `sqrt(3)` (its square root) both live in the same ring — the ring is
  not a field over the prime subfield; it contains zero divisors (it
  decomposes, ≅ K×K in the analysis).
- **Specific integer constants**, and they are not arbitrary — they
  are unit powers (measured 2026-08-28): with
  `u = 2+sqrt(3)`, the fundamental unit of Q(√3),
  `(2+sqrt(3))^8 = 18817 + 10864*sqrt(3)` and
  `2*(2+sqrt(3))^7 = 10084 + 5822*sqrt(3)`. The minimal form's t1/t2
  carry the pair `(10084, 5822) = 2u^7` and t3/t4 carry
  `(18817, 10864) = u^8`.

### 3.1 What the crash tracks (variant sweep, committed)

`probe-ratsimp-zero-divisor-variants.mac` re-targes the minimal form
at different constant pairs (the terms are parametrized on the pairs):

| variant | pairs (t1/t2, t3/t4) | result |
|---|---|---|
| V1 | `(10084,5822) = 2u^7`, `(18817,10864) = u^8` (original) | **RED** (crash) |
| V2 | `(10084,5822)`, `(18818,10864)` (neighbor integer) | green |
| V3 | `(10085,5822)`, `(18817,10864)` (neighbor integer) | green |
| V4 | `(10085,5822)`, `(18818,10864)` (both neighbors) | green |
| V5 | `(37634,21728) = 2u^8`, `(70226,40545) = u^9` (successor powers) | **RED** (crash) |
| V6 | the two original pairs swapped between t1/t2 and t3/t4 | green |
| V7 | `(2702,1560) = 2u^6`, `(5042,2911) = u^7` | **RED** (crash) |
| V8 | `(140452,81090) = 2u^9`, `(262087,151316) = u^10` | **RED** (crash) |

Measured conclusions:

- The crash is **not** structure-only (neighbor integers: green) and
  **not** an isolated constant pair: the unit-power pattern
  `(2u^k, u^(k+1))` crashes at every k tested (k = 6, 7, 8, 9 — V1,
  V7, V5, V8).
- Position matters: the `2u^k` pair must sit in the t1/t2 slot and
  `u^(k+1)` in t3/t4 (V6 swap: green).
- The two pairs are always linearly related,
  `u^(k+1) = (u/2)·(2u^k) = (1+sqrt(3)/2)·(2u^k)`; the trigger
  condition is that exact relationship between the constant pairs
  across the two term groups, at unit-power magnitude.

## 4. Root cause in the Maxima source

Crash path (all line numbers, 5.50.0 tree at
`/home/serge/src/external/maxima/src/`):

```
ratsimp → … → oldgcd (rat3c.lisp:198)
              → algnormal (rat3c.lisp:221)   ← UNGUARDED call site
                → rquotient (rat3a.lisp:949)
                  → rainv (rat3a.lisp:977)
                    → bprog (simp.lisp:3348) ← divides by the norm;
                                                norm ≡ 0 ⇒ `quotient' by `zero'
```

- `oldgcd` (rat3c.lisp:198) computes the reduced polynomial remainder
  sequence gcd; when the result needs algebraic normalization it calls
  `algnormal` **without** error protection (rat3c.lisp:221).
- The **same bug class was already fixed at the adjacent call site**:
  rat3c.lisp:210-212 guard the *other* inversion with
  `(unless (ignore-rat-err (rainv s)) (setq s 1))` under the comment
  *"Check for gcd that simplifies to 0. SourceForge bugs 831445 and
  1313987"* — i.e. Maxima upstream has met this failure mode before
  and patched one of the two call sites. The `algnormal` site was left
  unguarded.
- `ignore-rat-err` (merror.lisp:183) only catches the tagged
  `rat-error` throw — a raw division-by-zero inside `bprog` is a
  Lisp-level error that even the guarded site would not catch; the
  durable fix is for the inversion to *signal* (a tagged rat-err) when
  the norm vanishes, or to check the norm first.
- `rootof` is undefined in this build (measured), so the "rebuild the
  ring with a single generator" re-expressions are not available to
  the user at the Maxima level.

## 5. Explicit list of encountered triggering expressions

24 in total. The crashing *argument* in every corpus case is the
zero-diff `diff(rubi(f, x), x) - f` (regenerable: `rubi` with the
harness's fixed 40-`pos`/20-`no` prompts, then `diff`); the
identifying expression is the integrand `f`. Stage Bk refers to the
zero-chain stages; B5 = first direct `ratsimp` of the raw diff, B3 =
`ratsimp(expand(…))`.

### 5.1 Case 0 (discovery)

| # | expression (crashing argument) | via |
|---|---|---|
| 0a | `diff(rubi(sqrt(x+2)/(3*x^2+4), x), x)` | `ratsimp` |
| 0b | `t1+t2+t3+t4` and the scaled variant §3 (minimal form) | `ratsimp` |

### 5.2 The 23 corpus crash victims (all crashed with the identical
message `` `quotient' by `zero' ``; captured in
`probes/maxima/probe-radcan-attribution.out`)

| file | entry | stage | integrand `f` (crashing argument = `diff(rubi(f,x),x) - f`) |
|---|---|---|---|
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e2588 | B3 | `(2+3*x)^2*(3+5*x)^(5/2)/(1-2*x)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e826 | B5 | `x^2/sqrt(a+b*x^4)` |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e214 | B5 | `(c+d*x+e*x^2)/sqrt(a+b*x^4)` |
| 1.1.3.8 | e529 | B5 | `x^4*(c+d*x+e*x^2+f*x^3)/sqrt(a+b*x^4)` |
| 1.1.3.8 | e530 | B5 | `x^3*(c+d*x+e*x^2+f*x^3)/sqrt(a+b*x^4)` |
| 1.1.3.8 | e531 | B5 | `x^2*(c+d*x+e*x^2+f*x^3)/sqrt(a+b*x^4)` |
| 1.1.3.8 | e540 | B5 | `x^6*(c+d*x+e*x^2+f*x^3)/(a+b*x^4)^(3/2)` |
| 1.1.3.8 | e541 | B5 | `x^5*(c+d*x+e*x^2+f*x^3)/(a+b*x^4)^(3/2)` |
| 1.1.3.8 | e542 | B5 | `x^4*(c+d*x+e*x^2+f*x^3)/(a+b*x^4)^(3/2)` |
| 1.1.3.8 | e543 | B5 | `x^3*(c+d*x+e*x^2+f*x^3)/(a+b*x^4)^(3/2)` |
| 1.1.3.8 | e544 | B5 | `x^2*(c+d*x+e*x^2+f*x^3)/(a+b*x^4)^(3/2)` |
| 1.1.3.8 | e545 | B5 | `x*(c+d*x+e*x^2+f*x^3)/(a+b*x^4)^(3/2)` |
| 1.1.3.8 | e546 | B5 | `(c+d*x+e*x^2+f*x^3)/(a+b*x^4)^(3/2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2060 | B5 | `(d+e*x)^(1/2)/(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^(1/2)` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e660 | B5 | `sqrt(d+e*x)/sqrt(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e1005 | B5 | `x^2/sqrt(a+(2+2*b-2*(1+b))*x^2+c*x^4)` |
| 1.2.2.3 (d+e x^2)^m (a+b x^2+c x^4)^p | e153 | B5 | `(d+e*x^2)/sqrt(a+c*x^4)` |
| 1.2.2.3 | e168 | B5 | `(d+e*x^2)/sqrt(-a-c*x^4)` |
| 1.2.2.7 P(x) (d+e x^2)^q (a+b x^2+c x^4)^p | e4 | B5 | `(A+B*x^2)/sqrt(a+c*x^4)` |
| 1.2.2.7 | e11 | B5 | `(A+B*x^2)/(a+c*x^4)^(3/2)` |
| 1.3.2 Algebraic functions | e190 | B5 | `(d+e*x)^2/sqrt(a+c*x^4)` |
| 1.3.2 | e196 | B5 | `(d+e*x)^3/(a+c*x^4)^(3/2)` |
| 1.3.2 | e197 | B5 | `(d+e*x)^2/(a+c*x^4)^(3/2)` |

The 1.1.3.8 block (e214, e529–e546) is the family
`P(x)·(a+b·x⁴)^(±½,±¾)` — quartic binomials whose `rubi` answers
carry the `3^(1/4)`+`√3`-type generator mix.

### 5.3 Via `radcan(rat())` (the second entry point)

| file | entry | path | integrand `f` |
|---|---|---|---|
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1501 | `radcan(rat(diff(rubi(f,x),x) - f))` | `1/((a+b*x)^(11/2)*(c+d*x)^(1/2))` |

e1501 is a **double victim**: the old zero-chain died at B5 (pre-
fallback record: `unverified t=20.1s`) and the new harness's
`radcan(rat())` fallback crashes on the same diff too (post-fallback
record: `timeout t=30.0s` — the chain plus the crashing fallback
exhaust the 30 s cap). It remains unpassable by the current harness:
every algebraic-simplifier entry point available here hits the bug on
its zero-diff.

## 6. Harness consequences (measured)

- The zero-chain fallback is **errcatched** (a crash → 0 → entry
  unverified, never a false pass) and **elliptic-gated** (the elliptic
  family hits a different, slow crash class `PTPTQUOTIENT: Polynomial
  quotient is not exact` under `radcan(rat())` — 30–100 s each — and
  cannot close there anyway).
- The 23 crash victims §5.2 all now PASS via the fallback (their
  diffs close under `radcan(rat())` — `docs/corpus-radcan-fallback-attribution.md`); the remaining 344 of the 370 flips were plain
  simplifier gaps, not this bug.
- Distinct crash classes in the same harness (for disambiguation):
  `` `quotient' by `zero' `` (this bug, ~20 s in),
  `expt: undefined: 0 to a negative exponent` (1.3.1 e147's
  exp-diff, immediate), `PTPTQUOTIENT: Polynomial quotient is not
  exact` (elliptic family, 30–100 s).

## 7. Fix candidates (for upstream)

- **Fix A (minimal, local)**: make the algebraic inversion
  *signal* instead of crashing — in `rainv`/`bprog` (rat3a.lisp:977 /
  simp.lisp:3348) detect the vanishing norm and `rat-error` (the
  tagged throw `ignore-rat-err` already catches, merror.lisp:183),
  extending the treatment the source already applies for
  SourceForge bugs 831445/1313987 at rat3c.lisp:210-212 to the
  unguarded `algnormal` site (rat3c.lisp:221). `ratsimp`/`radcan`
  then fail the simplification instead of killing the process.
- **Fix B (structural, higher risk)**: keep one generator per
  algebraic ring (no redundant `3^(1/4)`+`√3` in one varlist) at
  `newvar` (rat3e.lisp:1035) — removes the zero divisors from the
  ring entirely, but touches the generator-management core.

## 8. Open items

- Upstream bug report: draft from this document; lead with
  `probes/maxima/probe-ratsimp-zero-divisor.mac` (standalone, no
  rubi), the §5.2 corpus evidence (23 natural occurrences, identical
  message), the e1501 `radcan(rat())` second entry point, and Fix A
  as the requested change (the existing 831445/1313987 guard at
  rat3c.lisp:210-212 makes the precedent explicit).
- e1501 (and any future entry whose zero-diff crashes both `ratsimp`
  and `radcan(rat())`) stays unpassable until Fix A lands; it is the
  standing canary for the fix.
