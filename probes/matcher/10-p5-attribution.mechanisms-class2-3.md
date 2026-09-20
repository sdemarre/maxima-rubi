> Task 4 Step 5 mechanism lines for probe 10's groups — classes 2 and 3 (all groups, NEW TIMEOUTS, class-3 new errors).
> Reads: probes/matcher/10-p5-attribution.class2.summary.out, probes/matcher/10-p5-attribution.class3.summary.out.
> Written 2026-09-14 by read-only analysis of the committed probe-10 outputs (commit 295effa); claims marked 'inferred' or 'not determined' are not measured.

# Task 4 Step 5 — mechanism lines, classes 2 and 3

Inputs: `probes/matcher/10-p5-attribution.class{2,3}.summary.out` and the raw runs
`…-{final30,p0,final120}.out` (class 3 also `…-newerror.out`); the 100 s re-check records
`test/corpus_class{2,3}.p5-final.timeout-rerun/`; rule files `rules/class{1,2,3}/*.mac` on the
final tree and at `0a6664c` (the P0 tree); Rubi source under `reference/rubi/`. Read-only analysis,
2026-09-14, HEAD 7726072.

## Evidence conventions (both classes)

- **Traces.** `fires` lists rules in first-occurrence order. `top` is the last completed fire. A
  fire prints only after that rule's repl returned an answer; misfires and declines are not
  captured by probe 10. On the P0 core the trace covers pass 1 only. P0's passes 2/3 ran only at
  top level with `fb=false`, so P0's **nested** dispatches are fully traced; only a P0 top-level
  pass-2/3 answer would be missing.
- **Answers are not recorded.** The raw runs keep class, wall and fire names only. For
  `unverified` / `unexpected` the runs cannot say whether the answer is wrong or just not closed
  by the zero chain.
- **Arms.** The committed P5 records of runs 2–4 give each entry's class with exactly one switch
  flipped: `r2` mr_flat_wide=true, `r3` mr_cond_retry=false, `r4` mr_model_flags=false
  (`test/corpus_class{2,3}.p5-run{2,3,4}.out`). A switch is named only when its arm changes the
  class; "all arms" means r2/r3/r4 all read the final class.
- **Table order.** Class 1 (9.1 last) < 2.1 < 2.2 < 2.3 < 3.1.1 … 3.1.5 < **3.3 < 3.4** <
  3.2.1 < 3.2.2 < 3.2.3 < 3.5 (`maxima_rubi.mac` `mr_load_all`).
- **Timeouts.** A timeout whose fire list already holds the top-level rule means rubi returned
  before the cap. The rest of the wall went to the driver's zero chain. A missing fire at a
  timeout is weak evidence: stdout is a pipe, and the SIGKILL at the cap can drop output that was
  never flushed.

## Class 2

### Families

- **OPT (faithful Optional binding).** The final core's rule binds through Optional defaults
  (`c_.`=0, `e_.`=0, `g_.`=1, `n_.`=1, `m_.`, …). The P0 `defmatch` literal for the same rule
  had no defaults and did not bind, so P0's walk went on to a later rule. The P0 literals quoted
  below come from `git show 0a6664c:rules/…`.
- **DEG (P0 degenerate binding).** The P0 route's rule could bind only through a binding
  Mathematica does not make: a zero exponent or coefficient (`a*x^n` with n=0, `(d+e*x)^m` with
  e=0), or an absent non-Optional factor read as 1. mr-match does not produce these (spec G-1).
- **NOUN (integrate noun → catch-all marker).** P0's trace has fewer nested fires than its
  reductions need, i.e. P0's sub-integrals 0-fired and fell through to Maxima `integrate`
  (`mr_int`, fb=true). On the substrate the same sub-integral binds a Rubi `Unintegrable`
  catch-all. The driver classifies its `unintegrable` marker contains-noun (at top level:
  deferred). That P0's PASS carried a Maxima integrate noun, which differentiates back, is
  consistent with the traces but not recorded.
- **IGT (translation).** `generator/generate_rules.py` `CMP_OPS` maps `IGtQ`→`>` and `ILtQ`→`<`,
  dropping Rubi's integer requirement. Rubi 2.1 r9/r10 and 2.2 r4 have `IGtQ[m,0]`, but the
  generated conds read `is(m > 0)`. P0's bodies are byte-identical; the binding change exposes
  it.
- **RETRY.** The r3 arm (mr_cond_retry=false) restores PASS, so the change needs the condition
  hook to run on every complete binding.
- **9.1.** P0's `9_1_rN` ids are the manual port's numbering: P0 r28 = the double-root trinomial
  = generated r27; P0 r16 = `u*(a*x^n)^m` = generated r15; P0 r9 = the constant rule = generated
  r8. P0's repls re-dispatched through `rubi_hybrid` (passes 2/3) or `rubi_hybrid_exact` (exact
  `member` seen comparison). The generated repls call `mr_int`, whose seen guard compares by
  `ratsimp` (`%mr_seenp` is unchanged since P0; only a comment differs).

### Group lines

- class 2 g1 (5 entries, deterministic, final deferred top=2_3_r34): Both cores end with 2_3_r34
  (`u*F^(a+b*(c+d*x)^n)` → `mr_int(ExpandLinearProduct)`).
  - On P0 the expansion sum dispatched: 1_4_1_r7 split it, and 2_3_r15 / 1_4_1_r29 / a nested
    2_3_r34 answered the terms (9–16 s).
  - On the substrate 2_3_r34 is the only fire (nfires=1, 0.5–0.9 s) and the answer is a
    top-level noun: nothing answered the nested sum.
  - Deferred in all arms, so no switch.
  - The traces cannot separate two readings: (a) the seen guard, since the expansion
    ratsimp-equals the integrand — but P0 has the same guard and its sum dispatched; (b) the
    2_3_r34 fire was nested inside a top-level rule that then misfired, so the top dispatch
    returned no answer.
  — follows from: not determined from the traces
- class 2 g2 (4 entries, deterministic, final contains-noun top=2_2_r2): 2_2_r2 (Rubi 2.2 r5)
  now binds (P0 literal `(c+d*x)^m*(F^(g*(e+f*x)))^n*(a+b*(F^(g*(e+f*x)))^n)^p` cannot bind
  `1/x`, `F^(c+d*x)`) ahead of 2_3_r70; its `Int[(c+d x)^(m-1)(a+b F)^(p+1)]` binds 2_1_r14 (the
  2.1 Unintegrable catch-all) → marker. This is the corpus's own 1-step answer (the expected
  answers of e86/e87/e92/e93 contain `Unintegrable`), so it is a yardstick case: the driver fails
  the corpus's own shape. P0 answered via 2_3_r70 with `a*x^n` bound at n=0 (DEG) and nfires=1
  (NOUN). All arms contains-noun. — follows from: faithful Optional binding (with the P0 DEG
  binding lost)
- class 2 g3 (3 entries, deterministic, final deferred top=-): No rule answers on the substrate.
  Each P0 route rested on a binding Mathematica does not make:
  - **e19** `F^(c(a+bx))*((d+e*x)^n)^m`: P0 1_4_1_r41 `(c.*(d_*(a.+b.*x))^q)^p` read the
    non-Optional `d_` as 1. Rubi's piecewise pair 1_4_1_r43/r44 (`GeQ[a,0]` / `Not[GeQ[a,0]]`)
    has conds `is(d >= 0)` / `not(is(d >= 0))`; per the rule text neither is true for a symbolic
    d. Not traced.
  - **e624**: P0 1_2_1_3b_r68 could bind `%e^(a+bx+cx^2)` only as `(d+0*x)^m`.
  - **e767**: P0 2_3_r101 `u.*F^v*G^w` needs a second exponential factor (`G^w`=1).
  All arms deferred. — follows from: G-1 (P0 degenerate / implicit-1 bindings are no longer
  produced); why Rubi's own 2-step routes don't answer on the substrate is not determined from the
  traces
- class 2 g4 (2 entries, deterministic, final unexpected top=2_1_r10): Noun-expected
  `sqrt(c+d*x)/(a+%e^x*b)^k`. P0 was no-answer (literal
  `(c+d*x)^m*(a+b*(F^(g*(e+f*x)))^n)^p` cannot bind `%e^x`). The substrate binds 2_1_r10, which
  in Rubi requires `ILtQ[p,0] && IGtQ[m,0]`; it accepts m=1/2 because its cond is
  `is(p < 0) and is(m > 0)` (IGT). The chain 2_1_r13 → 2_1_r9 / 2_2_r2 / 2_2_r1 (IGtQ[m,0] in
  Rubi too) → 3_5_r34 → 9_1_r12 answers without a marker; self=1 in both. Arms: r2/r4 unexpected,
  r3 contains-noun. — follows from: faithful Optional binding exposing the IGtQ/ILtQ translation
  (generator, P0 bodies identical); condition retry shapes the chain (r3 contains-noun)
- class 2 g5 (2 entries, deterministic, final unverified top=2_2_r2): 2_2_r2 binds first, as in
  g2. Rubi's chain 2_1_r9 → 2_2_r1 → 3_5_r14 → 2_3_r96 (e88 also 3_3_r3, 2_3_r93, 2_1_r10)
  builds the corpus's own `log(1+b F/a)` / `polylog(2)` / `polylog(3)` shape, and the zero chain
  does not close it (answer not recorded). P0: 2_3_r70 alone with n=0 (DEG, NOUN). All arms
  unverified. — follows from: faithful Optional binding (with the P0 DEG binding lost)
- class 2 g6 (1 entry, deterministic, final contains-noun top=1_4_1_r7): e726. Both cores split
  the sum with 1_4_1_r7.
  - On P0 that was the only fire: both terms fell through to Maxima integrate (NOUN).
  - On the substrate the terms bind 1_4_1_r18 and 2_3_r28 (`F^(a+b(c+dx)^2)(e+fx)^m`, m<-1),
    giving 2_3_r11 (erfi) and 2_3_r32 (the `F^(...)/(e+f x)` Unintegrable catch-all) → marker.
  - P0's literals `(e+f*x)^m*F^(a+b*(c+d*x)^2)` and `F^(a+b*(c+d*x)^n)/(e+f*x)` cannot bind
    `x^-2`, `1/x`.
  - The corpus answer (3 steps) has no Unintegrable.
  All arms contains-noun. — follows from: faithful Optional binding
- class 2 g7 (1 entry, deterministic, final deferred top=1_1_3_7_r45): e557. 1_1_3_7_r45
  (`Pq*(a+b*x^n)^p` → `mr_int(ExpandIntegrand)`) answers alone with a top-level noun. P0
  answered with the next rule 1_1_3_7_r46 (subst), so r45 did not answer there. The only Pq
  candidate, `(F^(sqrt(1-a*x)/sqrt(1+a*x)))^n`, is not a polynomial. Which binding lets r45's
  `%mr_polyQ` / `%mr_polyPowerQ` cond accept, and why its nested `mr_int` has no fire, is not
  traced. All arms deferred. — follows from: not determined from the traces
- class 2 g8 (1 entry, deterministic, final deferred top=1_1_3_7_r46): e50
  `(F^(c(a+bx)))^n*(d+e*x)^(4/3)`. 1_1_3_7_r46 (class 1, ahead of 2.1) answers a top-level noun;
  P0 route 2_1_r6 / 2_1_r7. r3 (cond_retry=false) reads verified 0.4 s, so r46 accepts only on a
  non-first binding. r2/r4 deferred. — follows from: condition retry
- class 2 g9 (1 entry, deterministic, final deferred top=1_2_3_5_r24): e741
  `(2-3x+x^2)/%e^(4x)`. 1_2_3_5_r24 (the 1.2.3.5 Unintegrable catch-all, class 1) answers at top
  level; P0 route 2_3_r3 (expand). r3 verified 0.1 s: the catch-all accepts only on a retried
  binding. r2/r4 deferred. — follows from: condition retry
- class 2 g10 (1 entry, deterministic, final deferred top=9_1_r27): e15
  `F^(c(a+bx))/(d^2+2dex+e^2x^2)`. This is the same Rubi rule on both cores: the 9.1 double-root
  trinomial, P0 id 9_1_r28, generated 9_1_r27.
  - P0's repl was `rubi_hybrid_exact(u*cancel(…))`: an exact `member` seen test, so the rewrite
    dispatched and 2_1_r4 answered.
  - The generated repl is `mr_int(u*cancel((b/2+c*x)^(2p)/c^p))`. The rewrite is
    ratsimp-identical to the integrand already on the dispatch path, so the ratsimp seen guard
    returns `integrate(…)`: a single top-level noun, with no nested fire.
  - This is the collapse-rule family that spec §3.5 names for restoring the exact comparison.
  All arms deferred. — follows from: 9.1 regeneration (rubi_hybrid_exact → mr_int) meeting the
  seen guard
- class 2 g11 (1 entry, deterministic, final unexpected top=2_1_r9): e67, noun-expected
  `sqrt(c+d*x)/(a+%e^x*b)`. 2_1_r9 (Rubi `IGtQ[m,0]`) accepts m=1/2 via `is(m > 0)` (IGT). Chain
  9_1_r12, 3_5_r34, 2_2_r1 → answer, self=1. P0 was no-answer (literal
  `(c+d*x)^m/(a+b*(F^(g*(e+f*x)))^n)` cannot bind `%e^x`). All arms unexpected. — follows from:
  faithful Optional binding exposing the IGtQ translation
- class 2 g12 (2 entries, slow-correct, final120 verified top=2_3_r19 / 2_3_r26): Same route on
  both cores (e283: 2_3_r16, 2_3_r19; e342: 2_3_r26). Walls: P0 7.7 / 4.0 s; final 30 s timeout
  with no fire flushed before the kill; final 120 s verified 55.7 / 54.3 s. r3
  (cond_retry=false) verified 0.4 / 0.2 s while r2/r4 time out, so the 7–13× cost is
  condition-retry work, not a route change. — follows from: condition retry (cost)
- class 2 NEW TIMEOUTS (18; P0 deferred 13, unverified 2, verified 2, error 1): at 100 s,
  timeout 15 and verified 3. The three verified are e527 49.8 s, e528 48.1 s and e575 52.1 s;
  probe 11 read them as noise, and runs 2–4 verify them at 26.8–29.8 s, i.e. at the cap. With
  mr_cond_retry=false (r3) only 7 of the 18 still time out (verified 8, unverified 2, error 1),
  so most of the new class-2 timeouts are condition-retry cost; r4 leaves 13, r2 15. Whole-record
  re-check (all 20 final timeouts): timeout 17, verified 3.

## Class 3

### Families (in addition to the class-2 families OPT, DEG, NOUN, RETRY, 9.1)

- **CATCH-3.1 (same-LHS expansion / catch-all pairs).** The pairs 3_1_4_r26/r27 and 3_1_3_r19/r20
  share one LHS each. Rubi 3.1.4 lines 32–33 and 3.1.3 lines 23–24 are
  `With[{u = ExpandIntegrand[(a+b Log)^p, …]}, Int[u,x] /; SumQ[u]]` followed by the
  `Unintegrable` catch-all.
  - P0's literals `(f*x)^m*(d+e*x^r)^q*(a+b*log(c*x^n))^p` / `(d+e*x^r)^q*(a+b*log(c*x^n))^p`
    bound neither rule on these integrands; the substrate binds both.
  - The expansion rule (inner `SumQ` test; 3-arg `%mr_expandIntegrand`, unchanged since P0) does
    not answer here — why is not traced. P0's own traces show 3_1_5_r28 (same 3-arg form, same
    LHS as and ahead of 3_1_5_r29) not answering the g4 integrands where r29 does.
  - The catch-all then answers: a top-level noun (deferred) or a nested marker (contains-noun).
  - P0 went on to 3.1.5 (r28/r29), 1_4_2_r25 or the manual 9.1 rule.
- **AFX (AFx catch-alls newly live).** 3_1_5_r30, 3_3_r32 and 3_3_r61 (`AFx*(a+b log …)^p` →
  `Unintegrable`) call `%mr_algebraicFunctionQ(AFx, x, true)`. At P0 that function had two
  parameters, so the 3-arg call errored and the cond could never accept. Commit 6a358db added the
  flag parameter ("conds the matcher substrate first makes reachable"); only these three rules
  call the 3-arg form.
- **NEGQ.** `%mr_negQ(e) := not %mr_posQ(e) and %mr_neQ(e,0)` with `%mr_posQ` =
  (`sign(e)` = pos). An unknown-sign symbol (sign `pnz`) therefore reads NegQ true. Rubi's
  `PosAux` returns True for a bare symbol or a positive multiple of one
  (IntegrationUtilityFunctions.m:608–634), so `NegQ[r]` is False there. Unchanged since P0.
- **INNER (moved inner conditions).** 3_1_4_r23's `With[{u = Int[(f x)^m (d+e x^r)^q]}, … /; …]`
  test now runs in cond; at P0 it was in repl, which declined on the same test.
  - Which rule answers does not change, but the sub-integral is computed in cond and again in
    repl.
  - Fires from inside the cond (1_1_1_2_r12/r13, 1_1_1_1_r*, 1_1_2_*, 1_4_1_r18) appear without
    an answering parent.
  - 3_3_r60's cond likewise runs `mr_int` for `%mr_integralFreeQ`, which tests only
    `mr_int` / `integrate`, not the `unintegrable` marker.
- **POLY (Rubi-form answer, zero chain not closed).** Nested integrals that P0 left to Maxima
  integrate now bind Rubi's log/polylog rules (3_3_r46, 3_1_5_r45, 3_1_5_r54, 3_1_3_r6/r7,
  3_1_4_r10/r20, …). The answer has the corpus's polylog/log shape, and the zero chain does not
  close it.
- **VERIFY-TIMEOUT.** The 30 s fire list already contains the top-level rule (P0's top as well),
  so rubi returned. The cap was spent in the zero chain on the larger Rubi-form answer.

### Group lines

- class 3 g1 (17 entries, deterministic, final unverified top=3_4_r8): All 17 read on the
  substrate with 3_4_r8 at top (`x^m (a+b log(c(d+e x^n)^p))^q`, subst x^n).
  - **Nested chain.** The log/x sub-integral runs 3_3_r8 → 3_3_r46 → 3_1_5_r45 (plus 3_1_5_r54
    for p=3), or for e96/e97 3_1_4_r10, 3_3_r3, 3_1_3_r6/r7, 3_1_4_r20, 3_3_r23, 3_3_r10 (POLY).
  - **P0, 11 entries** (e411–e526): same top 3_4_r8, but the fires stop at 3_3_r8 (or
    3_3_r31, 3_3_r8). P0's literal
    `(k+l*x)^r*(a+b*log(c*(d+e*x)^n))^p*(f+g*log(h*(i+j*x)^m))` cannot bind 3_3_r46 on
    `log(e x/(-d))` (NOUN).
  - **P0, 6 entries** (e80/e94/e131 via 3_5_r7, e95/e96/e97 via 3_5_r8): the bare `log(...)^q`
    integrands have no explicit `a+b*`, and P0 did not bind 3_4_r8 there, while the explicit
    `(a+b*log…)` entries got 3_4_r8 on P0.
  - **Arms.** All unverified, except e96/e97, which read verified under r3 (0.7 / 0.8 s).
  — follows from: faithful Optional binding; e96/e97 condition retry
- class 3 g2 (13 entries, deterministic, final contains-noun top=3_2_2_r3): Both cores put
  3_2_2_r3 at top (subst `(a+bx)/(c+dx)` → `Int[x^m (A+B log(e x^n))^p/(b-dx)^k]`).
  - **P0 nested:** answered by 1_4_2_r25 (e122–e152) or 3_1_5_r29 (e173–e203).
  - **Substrate nested:** 3_1_4_r27 answers (CATCH-3.1). The 1_1_1_2_r12/r13 fires in the p=1
    entries come from 3_1_4_r23's cond (INNER). 1_4_2_r25 (class 1, ahead of 3.1.4) no longer
    answers; its cond carries `Not[BinomialMatchQ[z] && BinomialMatchQ[u]]`, a MatchQ site now
    on mr-match.
  All arms contains-noun. — follows from: faithful binding / MatchQ rewrite (the traces do not
  separate them); why 3_1_4_r26 does not answer is not determined
- class 3 g3 (11 entries, deterministic, final unexpected top=1_4_1_r3): Noun-expected
  (`Unintegrable`, 0 steps). P0 was no-answer (literal `x^m*(a+b*x^n)^p*Fx`).
  - **Binding.** The substrate binds 1_4_1_r3 (Rubi 1.4.1:
    `x^m (a+b x^n)^p Fx /; IntegerQ[p] && NegQ[n]`) with n = r (3.1.4 e413–e419), 2n (e385) or
    n (e386). Those accept only through NEGQ; Rubi's `NegQ[r]` is False.
  - **e383/e384/e387/e388** have n = −n / −2n, where NegQ is True in Rubi too.
  - **Result.** The rewrite's nested dispatch has no fire (nfires=1), so the answer is `mr_int`'s
    Maxima-integrate fall-through, not a noun → unexpected. self=1 in 7 entries; cut in 4
    (e385–e388: the self-diff hit the cap).
  All arms unexpected. — follows from: faithful Optional binding exposing `%mr_negQ`'s sign-based
  reading (utility unchanged since P0); why Rubi itself gives a 0-step Unintegrable on
  e383/e384/e387/e388 is not determined from the traces
- class 3 g4 (10 entries, deterministic, final deferred top=3_1_4_r27): 3_1_4_r27 answers the
  top-level `Unintegrable` (CATCH-3.1).
  - **e92–e119** `x^k (a+b log)^2/(d+ex)^q`: Rubi's r26 conditions
    (`IntegerQ[q] && IGtQ[p,0] && IntegerQ[m] && IntegerQ[r]`) hold, and Rubi expands (8–26
    steps). On the substrate r26 does not answer. P0 route: 3_1_5_r29.
  - **e355/e363/e364** `(f x)^(m-1) (a+b log)^p/(d+e x^m)^q`: r26's integer conditions fail in
    Rubi too. P0 route: the manual 9.1 `u*(a*x^n)^m` (P0 id 9_1_r16); the generated 9_1_r15
    `u_.*(a_.*x_^n_)^m_` (non-Optional n) does not bind `(f*x)^(m-1)`. Rubi's 3–4-step rule is
    not reached.
  All arms deferred. — follows from: faithful Optional binding (the P0 literal bound neither r26
  nor r27) + the 9.1 regeneration (e355–e364); why r26 and the earlier 3.1.4 rule do not answer is
  not determined
- class 3 g5 (7 entries, deterministic, final contains-noun top=3_1_4_r15): Both cores put
  3_1_4_r15 at top (`x^m (a+b log)/(d+ex)^q` → `Int[(f x)^(m-1)(d+ex)^(q+1)(a m+b n+b m log)]`).
  P0 nfires=1 (the nested integral fell through, NOUN). On the substrate the nested integral
  reaches 3_1_4_r27 (CATCH-3.1; 1_1_1_2_r12 fires inside 3_1_4_r23's cond, INNER) → marker. All
  arms contains-noun. — follows from: faithful Optional binding
- class 3 g6 (7 entries, deterministic, final timeout top=3_4_r8; final120 timeout ×5,
  unverified e438 71.6 s; e525 is record-unverified 24.5 s / final30 timeout): VERIFY-TIMEOUT.
  - **Fires.** Every 30 s list ends with the top-level 3_4_r8 (P0's top).
  - **Nested chain.** Substrate: 3_1_5_r45, 3_1_4_r10, 3_3_r3, 3_1_3_r6/r7, 3_1_4_r20 (+
    1_1_1_*), 3_3_r23, 3_3_r10; e438 instead 3_1_5_r54/r45, 3_3_r46, 3_3_r8. P0 had only
    3_3_r31 (e438 3_3_r8) plus fall-throughs (POLY).
  - **Walls.** P0 verifies in 2–7 s.
  - **Arms.** r2/r4 time out; under r3 e484 verifies in 18.6 s, and e525 times out (it reads
    unverified 22–24 s in r1/r2/r4).
  — follows from: faithful Optional binding (the cost is in verification); e484 partly condition
  retry
- class 3 g7 (7 entries, deterministic, final unverified top=3_1_5_r47): Both cores put 3_1_5_r47
  at top (`u = Int[(g x)^q log(d(e+f x^m)^r)]`, Dist).
  - **Substrate:** the inner integral binds 3_4_r8 (subst) → 3_3_r7 → 1_1_1_2_r12/r13 (or
    1_1_1_1_r1/r3, 1_1_1_2_r3). The Dist'ed `Int[u/x]` runs 1_4_1_r18 (+ 1_4_1_r7/r9, 9_1_r12).
  - **P0:** 3_5_r34 (+ 1_2_1_6_r1 / 1_4_1_r25), 3_5_r37, 1_4_1_r20. As in g1, P0 did not bind
    3_4_r8 on `log(d*(1/d+f*x^2))` (a=0, b=1).
  All arms unverified. — follows from: faithful Optional binding
- class 3 g8 (6 entries, deterministic, final contains-noun top=3_2_1_r19): Both cores put
  3_2_1_r19 at top (subst). Nested: P0 3_1_5_r28 answered. On the substrate 3_1_4_r29 (3.1.4,
  ahead of 3.1.5) binds first, and its `Int[… (a+b log)^(p-1)/x]` reaches 3_1_5_r30 (AFX) →
  marker. All arms contains-noun. — follows from: faithful Optional binding (3_1_4_r29 nested) +
  the AFx catch-all made live (6a358db)
- class 3 g9 (6 entries, deterministic, final contains-noun top=3_2_2_r15): Both cores put
  3_2_2_r15 at top. Nested: P0 3_5_r8 / 3_5_r11. On the substrate the nested integral binds
  3_2_1_r19 (3.2.1 is ahead of 3.5; P0 has no defmatch record for it, i.e. a workaround-emitted
  rule), then 3_1_4_r29 → 3_1_5_r30 (AFX) → marker. r3 reads deferred 0.2 s (still FAIL); r2/r4
  contains-noun. — follows from: faithful binding + AFx catch-all live; condition retry shapes the
  chain
- class 3 g10 (6 entries, deterministic, final unverified top=3_2_2_r3): Both cores put 3_2_2_r3
  at top.
  - **P0 nested:** no fires (e163/e172/e182) or 3_1_5_r29 (e164/e174/e185), with
    fall-throughs.
  - **Substrate nested:** 3_1_5_r45, 3_1_4_r10, 3_3_r3, 3_1_3_r6/r7, 3_1_4_r20 (+ 3_1_3_r3/r8,
    1_1_1_*), or 3_1_2_r4/r5, 3_1_5_r45, 3_1_4_r10/r11 (POLY).
  - **Arms.** e164 verifies 0.7 s under r3; all others unverified in all arms.
  — follows from: faithful Optional binding; e164 condition retry
- class 3 g11 (4 entries, deterministic, final deferred top=3_1_3_r20): 3_1_3_r20 (the 3.1.3
  catch-all) answers `(a+b log)^p/(d+e x^r)^2` (r=2,3) at top level (CATCH-3.1). Rubi's r19
  conditions (`IntegerQ[q] && IGtQ[p,0] && IntegerQ[r]`) hold, so Rubi expands (16–26 steps); on
  the substrate r19 does not answer. P0 route: 3_1_5_r29. All arms deferred. — follows from:
  faithful Optional binding (P0 bound neither of the pair); why r19 does not answer is not
  determined
- class 3 g12 (4 entries, deterministic, final timeout top=3_1_5_r47; final120 error 45.1–46.4 s
  ×3; e120 is record error 26.1 s): VERIFY-TIMEOUT on the g7 route (1_1_1_2_r13, 3_3_r7, 3_4_r8,
  1_4_1_r18, top 3_1_5_r47 fired).
  - **Deaths.** At 120 s three die without a CLASS line at 45–46 s. The 100 s re-check has
    e51/e119/e121 as error at 99.1 / 71.9 / 73.8 s.
  - **Arms.** e51 verifies 1.5 s under r4 (mr_model_flags=false) and reads unverified 3.4 s
    under r3; e119/e120/e121 time out in r2/r3/r4.
  - **Error kind.** Not recorded.
  — follows from: faithful Optional binding (the g7 route); e51 also the model flags (r4 verified)
- class 3 g13 (3 entries, deterministic, final contains-noun top=1_4_1_r7): Sum integrands; both
  cores split with 1_4_1_r7.
  - **e207** (P0 expected): the terms reach 3_1_5_r55 and 3_1_5_r57, the polylog catch-all (P0
    literal `(d*x)^m*polylog(k,e*x^q)*(a+b*log(c*x^n))^p` cannot bind the `1/x` form), plus
    1_4_1_r18. P0 answered one term with 3_1_5_r55 and let the other fall through.
  - **e74/e75** (P0 nfires=1): 1_1_1_1_r2, 3_1_2_r2, 3_2_2_r3 → 3_2_2_r11 (the 3.2.2 catch-all;
    P0 literal `(f+g*x)^m*(h+i*x)^q*(A+B*log(…))^p`).
  - **Corpus.** None of the three corpus answers carries Unintegrable (NOUN).
  All arms contains-noun. — follows from: faithful Optional binding
- class 3 g14 (3 entries, deterministic, final contains-noun top=3_1_5_r56):
  `(d x)^m (a+b log) polylog(k, e x^q)`. P0 answered via the manual 9.1 `u*(a*x^n)^m` (P0
  9_1_r16). On the substrate that rule is gone (generated 9_1_r15 needs a non-Optional `x^n`), and
  3_1_5_r56 reduces to nested integrals that reach 3_1_5_r30 (AFX) → marker. The corpus answers of
  e220/e221/e222 contain `Unintegrable`, so this reproduces Rubi's noun (yardstick). All arms
  contains-noun. — follows from: 9.1 regeneration + AFx catch-all live
- class 3 g15 (3 entries, deterministic, final contains-noun top=3_2_1_r20):
  `(f+gx)^m (A+B log(e (a+bx)^2/(c+dx)^2))^2`. The substrate binds 3_2_1_r20, whose LHS
  `Log[e (a+bx)^n (c+dx)^mn]` is this integrand's form. P0's workaround-emitted 3_2_1_r19 (no
  defmatch record) bound it instead. Nested 3_1_4_r29 → 3_1_5_r30 (AFX) → marker; P0 nested
  3_1_5_r28. All arms contains-noun. — follows from: faithful binding + AFx catch-all live
- class 3 g16 (3 entries, deterministic, final contains-noun top=3_3_r10):
  `(a+b log(c(d+ex)^n))^(k/2)/(f+gx)^3`; the corpus answers (1 step) contain `Unintegrable`.
  - **Substrate:** 3_3_r10 (Rubi's 1-step rule; P0's slot literal
    `m1b*(a+b*log(c*(d+e*x)^n))^p` did not bind). Its sub-integral reaches 3_3_r32 (AFX, e110) or,
    via 3_3_r23 / 3_1_4_r20 / 3_1_3_r6/r7 / 3_1_4_r10 / 3_1_5_r45, the catch-alls 3_1_5_r50 /
    3_1_5_r57 (e116/e122) → marker. This is the corpus shape (yardstick).
  - **P0:** 3_5_r8, verified.
  All arms contains-noun. — follows from: faithful Optional binding (+ AFx live for e110)
- class 3 g17 (3 entries, deterministic, final contains-noun top=3_3_r9):
  `(a+b log(…))^(k/2)/(f+gx)^2`; the corpus answers contain `Unintegrable`. Both cores put 3_3_r9
  at top. The sub-integral `Int[(a+b log)^(p-1)/(f+gx)]` falls through on P0 (or 3_5_r7 / 3_3_r8).
  On the substrate it reaches 3_3_r32 (AFX; e109/e115) or 3_1_5_r57 (e121) → marker, the corpus
  shape. All arms contains-noun. — follows from: AFx catch-all live (e109/e115); faithful Optional
  binding (e121)
- class 3 g18 (3 entries, deterministic, final contains-noun top=3_4_r11): 3_4_r11 binds on the
  substrate (P0 literal `(f*x)^m*(a+b*log(c*(d+e*x^n)^p))^q` did not bind `x^-3` or a bare
  `log^q`).
  - **e136:** the sub-integral reaches 3_4_r27 (3.4 catch-all). The corpus answer (39 steps) has
    none; P0 answered via 3_5_r8 and a long class-1 chain.
  - **e158/e159:** the sub-integral reaches 3_4_r34. The corpus answers (1 step) contain
    `Unintegrable` (yardstick); P0 answered via the manual 9.1 `u*(a*x^n)^m`.
  All arms contains-noun. — follows from: faithful Optional binding (+ 9.1 regeneration for
  e158/e159); why Rubi's route for e136's sub-integral does not answer before 3_4_r27 is not
  determined
- class 3 g19 (3 entries, deterministic, final deferred top=-): No rule answers (a top-level
  noun). P0 answered with 3_5_r44 `u.*(a.*x^m.+b.*x^r.*log(c x^n)^q.)^p.`. On
  `x*log(f x^p)` / `x+log(x)` that needs an absent `x^r` (r=0) or a zero coefficient (DEG).
  e625's corpus answer contains `Unintegrable`; e292/e293 are Rubi 2/8 steps. All arms deferred.
  — follows from: G-1 (P0 degenerate binding); Rubi's own route is not reached, why is not
  determined
- class 3 g20 (3 entries, deterministic, final deferred top=3_1_4_r26):
  `(f x)^m (d+e x^r)^q (a+b log)^p`, q=1..3. 3_1_4_r26 (the q>0 expansion branch) answers alone
  (nfires=1) with a top-level noun: its ExpandIntegrand sum has no nested fire, the same shape as
  class 2 g1. P0 route: the manual 9.1 `u*(a*x^n)^m`. All arms deferred. — follows from: 9.1
  regeneration + faithful binding; why the nested sum yields no fire is not determined
- class 3 g21 (3 entries, deterministic, final timeout top=3_1_4_r20; final120 timeout
  top=3_4_r8): At 30 s the fire list is mid-chain (the g6 prefix, last 1_1_1_2_r14). At 120 s
  the top-level 3_4_r8 has fired and the entries still time out: the corpus answers are 62-step
  Rubi forms, and verification does not finish. P0: 3_3_r31 + 3_4_r8 at 2.4–4.4 s. All arms
  timeout. — follows from: faithful Optional binding (POLY; cost in integration and
  verification)
- class 3 g22 (3 entries, deterministic, final unverified top=3_1_4_r11):
  `(a+b log)^2/(x^k (d+ex))`. The substrate binds 3_1_4_r11 (P0 literal
  `x^m*(a+b*log(c*x^n))^p/(d+e*x^r)` cannot bind r=1), then 3_1_2_r4/r5, 3_1_5_r45, 3_1_4_r10
  (POLY). P0: 3_1_5_r29. All arms unverified. — follows from: faithful Optional binding
- class 3 g23 (3 entries, deterministic, final unverified top=3_2_1_r2): Both cores put 3_2_1_r2
  at top.
  - **Substrate nested chains (POLY):** e311 3_1_5_r45, 3_1_3_r6, 3_2_1_r17; e98 3_1_5_r45,
    3_1_4_r10, 3_2_1_r16; e101 3_1_5_r45, 3_1_3_r6, 3_2_1_r18.
  - **P0:** 3_2_2_r15 / 3_3_r3, 1_1_1_1_r1, 3_1_3_r6, 3_2_1_r18 / … 3_1_5_r15, 3_2_1_r16.
  - **3_2_1_r15..r18** have no P0 defmatch record (workaround-emitted).
  - **Arms.** r3: e311 verified 0.4 s, e98 contains-noun, e101 unverified.
  — follows from: faithful binding; e311 condition retry
- class 3 g24 (3 entries, deterministic, final unverified top=3_2_2_r15): Both cores put
  3_2_2_r15 at top. Nested: P0 3.5 rules (3_5_r7, 3_5_r11, 3_5_r8, 1_3_3_r13). On the substrate,
  3.2.1 rules ahead of 3.5 (3_2_1_r15 / 3_2_1_r19) → 3_1_4_r10 / 3_1_3_r6/r7 → 3_1_5_r45 (POLY).
  r3 reads deferred 0.2–0.3 s; r2/r4 unverified. — follows from: faithful binding; the final
  route needs condition retry (r3 deferred)
- class 3 g25 (3 entries, deterministic, final unverified top=3_3_r6; P0 expected):
  `(a+b log(c(d+ex)^n))/(f+gx)`. Both cores put 3_3_r6 at top.
  - **P0:** the sub-integral `Int[log(e(f+gx)/(ef-dg))/(d+ex)]` bound 3_4_r1
    (`Pq^m log(u)` → `C polylog(2, 1-u)`), giving the corpus form.
  - **Substrate:** no nested fire (nfires=1), so the sub-integral falls through to Maxima
    integrate and the zero chain no longer closes against the expected form. Why 3_4_r1 does not
    answer (its cond needs `ratsimp(Pq^m (1-u)/u')` free of x) is not traced.
  All arms unverified. — follows from: not determined from the traces
- class 3 g26 (3 entries, deterministic, final unverified top=3_5_r15): `x^k log(a+%e^x b)`. The
  substrate binds 3_5_r15 (P0 literal `(f+g*x)^m*log(d+e*(F^(c*(a+b*x)))^n)` cannot bind `x^k` or
  `%e^x`), then 3_5_r14 (polylog) and 2_3_r96 (e115): the corpus's polylog(k+2) route. P0: 3_5_r34
  / 3_5_r37 with fall-throughs. All arms unverified. — follows from: faithful Optional binding
- class 3 g27 (2 entries, deterministic, final contains-noun top=3_1_4_r29):
  `(f+gx)(a+b log)^p/(d+ex)^3`. 3_1_4_r29 binds (P0 literal
  `(f+g*x)^m*(d+e*x)^q*(a+b*log(c*x^n))^p` needs an explicit `(f+g*x)^m`), and its
  `Int[…(a+b log)^(p-1)/x]` reaches 3_1_5_r30 (AFX) → marker. P0: 3_1_5_r28, verified. All arms
  contains-noun. — follows from: faithful Optional binding + AFx catch-all live
- class 3 g28 (2 entries, deterministic, final contains-noun top=3_1_5_r42):
  `(a+b log)^2 log(d(e+f x^2)^m)`. P0 answered at top with 3_5_r44 after 3_1_1_r1 / 1_4_1_r7 /
  3_1_1_r2 (21–23 s). On the substrate 3_1_5_r42 (3.1.5, ahead of 3.5) answers: `u = Int[(a+b
  log)^2]` (the same 3_1_1 fires), then the Dist'ed `Int[x/(e+fx^2) u]` reaches 3_1_4_r27
  (CATCH-3.1) → marker. All arms contains-noun. — follows from: faithful Optional binding
- class 3 g29 (2 entries, deterministic, final contains-noun top=3_3_r38):
  `x^k log(f x^m)(a+b log(c(d+ex)^n))`. Both cores put 3_3_r38 at top. The nested
  `Int[(gx)^(q+1) log(f x^m)/(d+ex)]` gets 1_1_1_2_r13 and a fall-through on P0. On the substrate
  it gets 1_1_1_2_r12 (inside 3_1_4_r23's cond, INNER) → 3_1_4_r27 (CATCH-3.1) → marker. All arms
  contains-noun. — follows from: faithful Optional binding
- class 3 g30 (2 entries, deterministic, final deferred top=3_1_5_r30): 3_1_5_r30 (AFX, 3.1.5,
  ahead of 3.2.3 and 3.5) answers `Unintegrable` at top level.
  - **e350** `log(a x^(1-n))/(a x - x^n)`: AFx with a symbolic exponent, accepted by the new
    flag. P0 reached expected via 3_5_r1.
  - **e270** `(b+2cx) log(x)/(x(b+cx))`: P0 verified via the manual 9.1 constant rule + 3_2_3_r16.
  All arms deferred. — follows from: AFx catch-all made live (6a358db) + faithful binding
- class 3 g31 (2 entries, deterministic, final deferred top=3_2_2_r15):
  `1/((f+gx)(ah+bhx)(A+B log(…))^k)`. 3_2_2_r15's sub-integral reaches 3_2_2_r11 (the 3.2.2
  catch-all); the subst leaves a top-level noun → deferred. The corpus answers are
  `_subst(…, Unintegrable(…))`, 1 step, so this is Rubi's own form (yardstick). P0: 3_2_2_r15
  alone (nfires=1, nested fall-through), verified. All arms deferred. — follows from: faithful
  Optional binding (NOUN)
- class 3 g32 (2 entries, deterministic, final deferred top=3_3_r60):
  `log(i(j(hx)^t)^u)^k log(e(f(a+bx)^p(c+dx)^q)^r)/x`. Both cores put 3_3_r60 at top.
  - **Substrate chain:** 3_1_5_r54/r45, 3_1_3_r6, 3_2_3_r8, 3_3_r61 (AFX), 1_1_1_1_r2,
    3_1_2_r2 → top-level noun at 22–28 s.
  - **P0:** 3_3_r8, 3_2_3_r8 → verified 15–20 s.
  - **Why the noun survives.** 3_3_r60's cond runs the sub-integral for `%mr_integralFreeQ`
    (INNER), and that test does not reject the marker. r3 deferred 2.1–2.3 s.
  — follows from: AFx catch-all live; how the marker becomes the top-level noun through
  3_3_r60's subst is not determined
- class 3 g33 (2 entries, deterministic, final timeout top=3_1_4_r16; final120 timeout):
  VERIFY-TIMEOUT. Both cores put 3_1_4_r16 at top (P0 nfires=1).
  - **Substrate nested:** 3_1_4_r23, whose cond (INNER) runs `Int[(f x)^m (d+e x^2)^q]` (fires
    1_1_2_1_r15, 1_1_1_2_r32/r11, 1_1_2_2_r4, 1_4_1_r18); the repl then runs it again.
  - **Timing.** The top-level fire is in the 30 s list, so rubi returned; the zero chain does
    not finish by 120 s. P0 verifies 8.4–8.5 s.
  All arms timeout. — follows from: faithful Optional binding (3_1_4_r23 nested) with the moved
  inner condition doubling its sub-integral; the remaining cost is verification
- class 3 g34 (2 entries, deterministic, final timeout top=3_4_r5; final120 timeout):
  VERIFY-TIMEOUT. Both cores put 3_4_r5 at top.
  - **Substrate nested:** 3_4_r8 → 3_3_r10/r23 → 3_1_4_r20 / 3_1_3_r6/r7 / 3_3_r3 /
    3_1_4_r10 / 3_1_5_r45 (POLY). P0 nested: 3_3_r31, 3_4_r8, fall-throughs.
  - **Timing.** The top-level fire is in the 30 s list, so rubi returned.
  - **Arms.** r3: e504 verified 5.7 s, e437 timeout.
  — follows from: faithful Optional binding; e504 condition retry
- class 3 g35 (2 entries, deterministic, final unverified top=3_1_4_r18):
  `(a+b log) x^k/(sqrt(d-ex) sqrt(d+ex))`. The substrate binds 3_1_4_r18 (P0 literal
  `x^m*(d1+e1*x)^q*(d2+e2*x)^q*(a+b*log(c*x^n))`, shared q slot, did not bind). It feeds nested
  3_1_4_r23 (INNER; cond fires 1_1_2_1_r15/r17, 1_1_1_2_r32/r11, 1_1_2_2_r4/r23, 1_4_1_r18) →
  Dist answer. P0: 1_4_2_r25 alone (fall-through). r4 e312 timeout; otherwise unverified. —
  follows from: faithful Optional binding
- class 3 g36 (2 entries, deterministic, final unverified top=3_2_3_r8): e51 has 3_2_3_r8 at top on
  both cores. e52 (power 1) has P0 top 3_2_3_r9; on the substrate 3_2_3_r8 (`m_.`=1, ahead of r9)
  binds. Nested: 3_1_5_r54/r45, 3_3_r46, 3_3_r8 (POLY) versus P0 3_3_r31 / 3_3_r8. All arms
  unverified. — follows from: faithful Optional binding
- class 3 g37 (2 entries, deterministic, final unverified top=3_4_r17): `(d+ex)^k log(c(a+bx^3)^p)`.
  3_4_r17 binds (P0 literal `(f+g*x)^r*(a+b*log(c*(d+e*x^n)^p))` needs explicit a, b and r), then
  1_1_3_8_r18 (+ 1_1_1_2_r12, 1_1_3_4_r9 / 1_4_1_r18). P0: 3_5_r34 / 3_5_r37. All arms unverified.
  — follows from: faithful Optional binding
- class 3 g38 (2 entries, deterministic, final unverified top=3_4_r38):
  `(a+b log(c(d+e/(f+gx))^p))^k`. Both cores run 3_4_r38 → 3_4_r3 → 3_4_r8 → 3_3_r8. The
  substrate adds 3_3_r46 and 3_1_5_r45 (e636 also 3_1_5_r54), as in g1 (POLY); P0 verified with
  a fall-through below 3_3_r8. All arms unverified. — follows from: faithful Optional binding
- class 3 g39 (1 entry, deterministic, final contains-noun top=3_1_3_r7): e128
  `sqrt(a+b log)/(d+ex)^2`; the corpus answer (1 step) contains `Unintegrable`. Both cores put
  3_1_3_r7 at top. The nested `Int[(a+b log)^(-1/2)/(d+ex)]` falls through on P0. On the substrate
  it reaches 3_1_3_r20 (r19's `IGtQ[p,0]` rightly fails) → marker, the corpus's own shape
  (yardstick). All arms contains-noun. — follows from: faithful Optional binding (NOUN)
- class 3 g40 (1 entry, deterministic, final contains-noun top=3_1_3_r8): e129
  `sqrt(a+b log)/(d+ex)^3`; the corpus answer contains `Unintegrable`. The substrate answers with
  3_1_3_r8 (P0 answered at top with the later 3_5_r8). Its nested
  `Int[(d+ex)^(q+1)(a+b log)^(p-1)/x]` reaches 3_1_4_r27 (r26's `IGtQ[p,0]` fails in Rubi too) →
  marker, the corpus shape (yardstick). All arms contains-noun. — follows from: faithful Optional
  binding
- class 3 g41 (1 entry, deterministic, final contains-noun top=3_3_r34): e361
  `log(f x^m)(a+b log(c(d+ex)^n))`. Both cores put 3_3_r34 at top. The nested
  `Int[x log(f x^m)/(d+ex)]` falls through on P0. On the substrate: 1_1_1_2_r12 (INNER) →
  3_1_4_r27 (CATCH-3.1) → marker. The corpus answer (8 steps) has none. All arms contains-noun. —
  follows from: faithful Optional binding
- class 3 g42 (1 entry, deterministic, final contains-noun top=3_3_r39): e370. Both cores put
  3_3_r39 at top. The nested `Int[log(f x^m)^2 (a+b log)/(d+ex)]` falls through on P0. On the
  substrate it reaches 3_3_r56 (the 3.3 two-log catch-all; P0 literal needs explicit
  `(k+l*x)^r`, `i+j*x`) → marker. The corpus answer has none. All arms contains-noun. — follows
  from: faithful Optional binding
- class 3 g43 (1 entry, deterministic, final contains-noun top=3_3_r54): e391
  `(a+b log(c(d+ex)^n))(f+g log(h(i+jx)^m))/x^2`. P0 top was 3_3_r55. On the substrate 3_3_r54
  (`x^r`·two logs, ahead of r55) binds; its sub-integral runs 1_1_1_1_r1/r3, 1_1_1_2_r3 → 3_3_r32
  (AFX) → marker. The corpus answer (15 steps) has none. All arms contains-noun. — follows from:
  faithful Optional binding + AFx catch-all live
- class 3 g44 (1 entry, deterministic, final contains-noun top=3_4_r5): e522
  `(a+b log(c(d+e/x^(2/3))^n))^2`. Both cores put 3_4_r5 at top. The subst sub-integral falls
  through on P0. On the substrate it runs 3_4_r11 → 3_4_r27 (3.4 catch-all) → marker. The corpus
  answer (14 steps) has none. All arms contains-noun. — follows from: faithful Optional binding;
  why Rubi's route for 3_4_r11's sub-integral does not answer before 3_4_r27 is not determined
- class 3 g45 (1 entry, deterministic, final deferred top=3_3_r32): e223
  `log(c(a+bx)^p)/(x(d+ex))`. 3_3_r32 (AFX; AFx = `1/(x(d+ex))`; 3.3 is ahead of 3.2.3) answers
  `Unintegrable` at top level. The preceding 1_1_1_1_r1/r3 and 1_1_1_2_r3 fires have no
  answering parent (a condition's sub-integral). P0 verified via the manual 9.1 constant rule +
  3_2_3_r16. All arms deferred. — follows from: AFx catch-all made live (6a358db) + faithful
  binding
- class 3 g46 (1 entry, deterministic, final timeout top=-; final120 timeout top=-): 3.5 e83
  `(d+ex)^3 log(d(a+bx+cx^2)^n)`. No fire captured at 30 s or 120 s; P0 answered with
  1_2_1_6_r1 → 3_5_r34 in 2.2 s. Either the top-level dispatch does not return (some rule's
  match / cond / repl ahead of 3_5_r34 runs unbounded), or its fires stay in the unflushed pipe
  buffer at the kill. All arms timeout. — follows from: not determined from the traces
- class 3 g47 (1 entry, deterministic, final timeout top=3_5_r42; final120 timeout): 3.5 e253
  `1/(ax + bx log(cx^n)^4)`. Both cores put 3_5_r42 at top (FunctionOfLog).
  - **Nested partial-fraction chains differ:** P0 1_1_2_1_r11, 1_2_1_1_r11, 1_2_1_2_r3/r9,
    1_2_2_1_r7; substrate 1_2_1_1_r12, 1_2_1_2_r3/r9, 1_1_1_1_r3/r5, 1_1_3_1_r14.
  - **Timing.** The top-level fire is in the 30 s list, so rubi returned; the zero chain does
    not finish by 120 s (P0 verified 2.4 s).
  All arms timeout. — follows from: not determined from the traces (which change moves the
  class-1 chain); the cost is verification
- class 3 g48 (1 entry, deterministic, final unverified top=3_1_5_r41): e29
  `(a+b log) log(d(1/d+fx^2))`. P0 answered at top with 3_5_r44 (after 3_1_1_r1 / 1_4_1_r7). The
  substrate binds 3_1_5_r41 (3.1.5, ahead of 3.5; P0 literal
  `log(d*(e+f*x^m)^r)*(a+b*log(c*x^n))^p` needs an explicit r). `u = Int[log(…)]` runs 3_4_r2
  (+ 1_1_2_1_r15, 1_1_2_2_r23, 1_4_1_r18/r7), then Dist gives the atan/polylog Rubi form. All arms
  unverified. — follows from: faithful Optional binding
- class 3 g49 (1 entry, deterministic, final unverified top=3_2_1_r1): e95 `log(c(b+ax)/x)^3`. P0
  top was 3_2_1_r2 (20.9 s, long chain). On the substrate 3_2_1_r1 (`(A.+B.*Log[e.*((a.+b.*x)/(c.+d.*x))^n.])^p.`
  with the A=0, B=1, n=1 defaults; ahead of r2) binds, then 3_1_5_r45, 3_1_3_r6, 3_2_1_r17 (POLY). All arms
  unverified. — follows from: faithful Optional binding
- class 3 g50 (1 entry, deterministic, final unverified top=3_2_1_r17): e104. P0 top was 3_2_1_r18
  (via 3_3_r51, 3_1_3_r6). On the substrate 3_2_1_r17 (`Log[e((a+bx)/(c+dx))^n]` form, ahead of
  r18; both have no P0 defmatch record) binds, then 3_1_5_r45 and 3_1_3_r6 (POLY). All arms
  unverified. — follows from: faithful binding
- class 3 g51 (1 entry, deterministic, final unverified top=3_3_r37): e362. Both cores put 3_3_r37
  at top. The nested `Int[log(f x^m)^2/(d+ex)]` runs 3_3_r3, 1_1_1_1_r1, 3_1_3_r6 on P0 and
  3_1_5_r45, 3_1_3_r6 on the substrate (P0 literal for 3_1_5_r45
  `log(d*(e+f*x^m))*(a+b*log(c*x^n))^p/x`) (POLY). All arms unverified. — follows from: faithful
  Optional binding
- class 3 g52 (1 entry, deterministic, final unverified top=3_3_r47): e382. Both cores put 3_3_r47
  at top. The nested integral falls through on P0 (nfires=1). On the substrate it runs 3_3_r46,
  3_1_5_r46, 3_1_3_r6, 3_1_5_r45 (POLY). All arms unverified. — follows from: faithful Optional
  binding
- class 3 g53 (1 entry, deterministic, final unverified top=3_3_r60; P0 expected): e433. Both
  cores run 3_3_r60 → 3_3_r9 → 3_3_r6. P0 adds 3_4_r1 (the `polylog(2,1-u)` step) and reads
  expected; the substrate lacks it and the sub-integral falls through, as in g25. All arms
  unverified. — follows from: not determined from the traces
- class 3 g54 (1 entry, deterministic, final unverified top=3_3_r9; P0 expected): e49. Both cores
  run 3_3_r9 → 3_3_r6. P0 adds 3_4_r1 and reads expected; the substrate lacks it, as in g25. All
  arms unverified. — follows from: not determined from the traces
- class 3 g55 (1 entry, slow-correct, final120 verified top=3_4_r12): e528
  `x^2 (a+b log(c(d+e/x^(2/3))^n))^3`. Walls: P0 4.4 s; final 30 s timeout with the top-level
  3_4_r12 fired (nested 1_4_1_r3, 3_4_r11); final 120 s verified 65.7 s; 100 s re-check verified
  57.9 s. rubi returns within the cap, so the extra time is verification of a different answer.
  Runs 2–4 all time out at 30 s. — follows from: not determined from the traces (which change
  alters the nested chain); the cost is verification
- class 3 NEW TIMEOUTS (62; P0 deferred 33, verified 19, unverified 7, error 2, contains-noun 1):
  - **100 s re-check:** timeout 46, error 6, unverified 6, verified 4. The verified four are
    3.1.4 e135 67.3 s, e156 32.8 s, 3.3 e487 65.5 s and 3.4 e528 57.9 s.
  - **Group members:** all 19 P0-verified entries belong to the timeout groups above (g6, g12,
    g21, g33, g34, g46, g47, g55).
  - **Arms over the 62:** r2 timeout 59 (3.3 e190 / e218 / e525 unverified at 26–28 s, at the
    cap); r3 timeout 45 (unverified 9, verified 5, deferred / contains-noun / error 1 each); r4
    timeout 55 (verified 2, error 2, unverified 3).
  - **Whole-record re-check** (all 145 final timeouts): timeout 113, error 16, unverified 8,
    verified 8. The re-check keeps only the class, so error kinds are not recorded.
- class 3 new error 3.1.5 e120 (g12 member): The final record reads error 26.1 s; probe newerror
  reads error 25.9 s. Fires are g12's chain with the top-level 3_1_5_r47 fired, so rubi returned
  and the process dies without a CLASS line while verifying. Its siblings e51/e119/e121 on the same
  route die as error at 45–46 s (120 s cap) and 72–99 s (100 s re-check). P0 verified 10.3 s; runs
  2–4 time out at 30 s. The error text is not recorded, so the kind is not determined.
- class 3 new error 3.2.3 e81 `log(e((a+bx)/(c+dx))^n)/(x^2(f-gx^2))`: P0 timed out at 30.1 s (not
  a PASS). The final reads error 22.5 s (probe 20.1 s, nfires=9: 1_1_2_1_r15, 1_1_2_2_r6, 3_3_r28,
  top-level 3_2_3_r16 fired), so rubi now answers before the cap and the process dies afterwards.
  Also error in r2 (19.6 s) and r4 (20.3 s); timeout in r3. The kind is not recorded.
- class 3 new error 3.5 e172 `log(a*cot(x)^n)`: P0 timed out at 30.1 s. The final reads error
  27.5 s (probe 24.7 s: 9_1_r12, 9_1_r10, top-level 3_5_r31 fired), so rubi returned and the
  process dies afterwards. Error in every arm (r2 22.4, r3 22.6, r4 24.2 s). The kind is not
  recorded.

## Evidence gaps

- **Answers not recorded.** Probe 10 keeps class, wall and fire names only. For every
  `unverified` / `unexpected` group the runs cannot say whether the answer is wrong or just not
  closed by the zero chain: class 2 g4, g5, g11; class 3 g1, g3, g7, g10, g22, g23, g24, g26, g35,
  g36, g37, g38, g48–g52. The same applies to "P0's PASS carried a Maxima integrate noun" (NOUN):
  consistent with P0's low fire counts, not observed.
- **Error kinds.** The error kind of class 3 g12 (120 s), the three new errors, and the 16 errors
  of the 100 s re-check is not recorded: no stderr and no Lisp error text is kept.
- **Class 2 g1 / class 3 g20** (expansion rule answers alone with a top-level noun). The traces
  cannot separate the seen guard catching the ratsimp-identical expansion (P0 has the same guard,
  yet its sum dispatched) from a misfired parent rule (misfires are not captured).
- **Class 2 g3.** P0's degenerate bindings are clear from rule text. Why Rubi's own 2-step routes
  do not answer on the substrate is not traced. For e19 the 1_4_1_r43/r44 `GeQ` reading comes from
  rule text only.
- **Class 2 g7.** Which binding lets 1_1_3_7_r45's polynomial cond accept, and why its nested
  dispatch has no fire.
- **CATCH-3.1** (class 3 g2, g4, g5, g11, g28, g29, g40, g41). Why 3_1_4_r26 / 3_1_3_r19 (inner
  `SumQ` of the 3-arg `%mr_expandIntegrand`) do not answer where Rubi's conditions hold. The only
  hint is P0's trace of 3_1_5_r28 not answering the g4 integrands. For g2, whether 1_4_2_r25 stops
  answering because of binding or because of the rewritten `BinomialMatchQ` is also not separated.
- **Class 3 g4 e355/e363/e364, g18 e136, g44.** Which earlier Rubi rule should answer before the
  catch-all.
- **Class 3 g19.** Rubi's own route is not reached; why is not traced.
- **Class 3 g25, g53, g54.** Why P0's nested 3_4_r1 (`Pq^m log(u)` → polylog) does not answer on
  the substrate.
- **Class 3 g32.** How 3_3_r61's marker turns into a top-level noun through 3_3_r60's subst.
- **Class 3 g46.** No fire at 30 s or 120 s: an unbounded rule before 3_5_r34, or a lost
  unflushed buffer.
- **Class 3 g47, g55.** Which substrate change moves the nested class-1 chain; the traces only
  show that rubi returned and verification ran past the cap.
- **Timeout fire lists.** Stdout is a pipe and the cap kill can drop unflushed fire lines. A
  present top-level fire is strong evidence; an absent fire (class 2 g12 at 30 s, class 3 g46) is
  weak.
- **Pre-existing defects, not substrate changes, exposed by the binding change** (the user should
  know they are behind some groups):
  - the IGtQ/ILtQ → `>`/`<` translation (class 2 g4, g11);
  - `%mr_negQ`'s sign-based reading of unknown-sign symbols (class 3 g3);
  - the AFx catch-alls that only became callable in 6a358db (class 3 g8, g9, g14, g15, g16,
    g17, g27, g30, g32, g43, g45);
  - the ratsimp seen guard meeting a regenerated 9.1 collapse rule (class 2 g10). Spec §3.5
    makes a collapse-family PASS→FAIL the trigger for restoring the exact comparison, and Task 4
    Step 2 checked only 1.2.1.3 e839.
