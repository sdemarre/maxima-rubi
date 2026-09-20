# P5b mechanism lines — classes 2 and 3

> Translation fixes, Task 7 Step 4. One line per probe-10 GROUP, plus NEW TIMEOUTS and NEW ERRORS,
> each group with its defect-clearance tag.
> Reads: `probes/matcher/10-p5b-attribution.class2.summary.out`, `probes/matcher/10-p5b-attribution.class3.summary.out`
> and their raw legs (`…class<N>-{final30,p0,final120,newerror}.out`).
> Written 2026-09-15 by read-only analysis (no Maxima run). Cores: fixed `b98e4748784738cb78f0163a97d4cf5f`
> (P5b final records `test/corpus_class<N>.p5b-run1.out`), P0 `5ef9b3bc5ee07ffac0e76f1fea54fbac`.

Evidence used beyond the summaries, and how to read the lines:

- **Arms.** `r2`/`r3`/`r4` = `test/corpus_class<N>.p5b-run{2,3,4}.out` (mr_flat_wide=true / mr_cond_retry=false /
  mr_model_flags=false). `p5` = the defective tree's record `test/corpus_class<N>.p5-run1.out`. An arm is
  named only where it changes the class.
- **Fix-induced entries.** 23 class-3 entries were PASS on the defective tree and FAIL on P5b: g3 e427–e429,
  g13, g31, g34, g36, g39, g41, g54–g58. No class-2 entry is: every class-2 P→F entry already failed with
  the same class on the defective tree.
- **Sign readings.** PosQ/NegQ values were read from the code: the port `%mr_posAux`
  (`maxima_rubi_utils.mac:445–471`) and Rubi `PosAux` (`IntegrationUtilityFunctions.m:608–634`). They were
  not measured.
- **Unported steps.** `mr_load_all` loads classes 1–3 only. Two Rubi rules the routes below need live in
  unloaded classes:
  - `(a+b ArcTan[c x])/x` is in 5.3.2 (class 5);
  - `PolyLog[n, a (b x^p)^q]/x` and `PolyLog[n, c (a+b x)^p]/(d+e x)` are in 8.8, lines 8–9 (class 8).
  An answer holding a leftover `'integrate(polylog(k,…)/…)` noun is therefore *unverifiable*. Where the
  integration variable of that noun reads `b*x^2+a` or `(d*x+c)/(b*x+a)`, `%mr_subst` has carried it
  through the substitution.
- **Utils call graph** (static, by name). These helpers reach the changed sign/sibling ports:
  - `%mr_intSum`/`%mr_intTerm` → `%mr_posQ`, `%mr_negQ`, `%mr_product_factors`, `%mr_removeContentAux`;
  - `%mr_rt` → the same plus `%mr_rt_negSumBaseQ`, `%mr_splitSum_aux`;
  - `%mr_expandToSum` → `%mr_posQ`;
  - `%mr_normalizeIntegrand` → `%mr_signOfFactor`, `%mr_unifySum`;
  - `%mr_functionOfExponential*` → `%mr_posQ`, `%mr_negQ`.

  These reach none of them: `%mr_expandIntegrand2/3`, `%mr_expandLinearProduct`, `%mr_subst`, `%mr_dist`,
  `%mr_algebraicFunctionQ`, `%mr_polyQ`, `%mr_rationalFunctionQ`, `%mr_derivativeDivides`.
- **Equal-form rewrites (EQ-REWRITE).** This is the candidate behind most `undetermined` tags. Some non-9.1
  rules rewrite the integrand to an algebraically equal form and call `mr_int` on it: 2_3_r34
  (`ExpandLinearProduct`), 3_1_4_r26 (`ExpandIntegrand`), 1_1_3_7_r45, 1_4_1_r3, 1_4_1_r18, 1_4_1_r26.
  - **Seen test.** `mr_int` keeps `%mr_seenp`'s ratsimp comparison (`maxima_rubi_utils.mac:201–211`,
    `:216–262`). The fix moved only the 9.1 `Int` calls to `mr_int_exact`. Such a rewrite therefore reads
    as a loop by construction, and the call returns `integrate(…)`. That is the collapse mechanism at a
    non-9.1 site.
  - **When the trace proves it.** Only when the rewrite is a *sum*. A dispatched sum always fires a rule:
    1_4_1_r7 answers any sum, since `mr_simplify_flag : true` (utils:11). A missing nested fire then leaves
    two exits: a seen hit, or a fault inside `%mr_intSum`.
  - **The P0 counter-example.** On P0 the same seen test (`0a6664c` utils:317–352), the same 2_3_r34 repl
    and an identical `%mr_expandLinearProduct` (diffed) let the sum dispatch. That is unexplained.
  - **Tag.** None of these groups is tagged `collapse`; each is `undetermined`, with a `%mr_seenp` trace on
    the nested call as the decider.
- **Split groups.** A group split into sub-bullets is counted in the summary under its most severe
  sub-tag.

## Class 2

- class 2 g1 (5 entries, deterministic, final deferred top=2_3_r34): **2_3_r34 alone.**
  - **Final core.** 2_3_r34 (`u F^(a+b(c+dx)^n)` → `mr_int(ExpandLinearProduct)`) fires alone (nfires=1,
    0.4–0.7 s). No rule fires on the nested expansion, and the top-level answer is the `integrate` noun.
  - **P0.** The expansion sum dispatched: 1_4_1_r7 split it, and 2_3_r15 / 1_4_1_r29 / a nested 2_3_r34
    answered the terms (9–15 s).
  - **Arms.** All deferred, and deferred on the defective tree too.
  - **Rule text.** No fixed-defect site: the cond is `freeof` + `%mr_polynomialQ`, and the repl is
    `mr_int(%mr_expandLinearProduct(…))`.
  - **Why the nested sum does not dispatch.** It is a sum and 1_4_1_r7 did not fire. The only exits are the
    seen test (EQ-REWRITE) and a `%mr_intSum` fault. P0 contradicts the seen-test reading.

  — follows from: not determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at 2_3_r34
  (collapse mechanism, non-9.1 site) vs a `%mr_intSum` fault; a `%mr_seenp` trace on 2_3_r34's nested
  `mr_int`, on both cores, decides it]
- class 2 g2 (4 entries, deterministic, final contains-noun top=2_2_r2): 2_2_r2 (Rubi 2.2 r5) now binds
  ahead of 2_3_r70. Its `Int[(c+dx)^(m-1)(a+bF)^(p+1)]` binds 2_1_r14, the 2.1 `Unintegrable` catch-all,
  which leaves the marker. This is Rubi's own 1-step shape: the corpus answers of e86/e87/e92/e93 contain
  `Unintegrable`, so this is a yardstick case. P0 answered with 2_3_r70 on a degenerate `a*x^n` binding,
  n=0. All arms contains-noun. Sites on the route: 2_2_r2 `%mr_neQ(p,-1)`, 2_1_r14 `freeof` only. — follows
  from: faithful Optional binding — [fixed-defect: none]
- class 2 g3 (3 entries, deterministic, final deferred top=-): No rule answers on the final core (nfires=0,
  a top-level noun). Each P0 route rested on a binding Mathematica does not make. All arms deferred, and
  deferred on the defective tree. The three entries do not share a cause:
  - **e19** `F^(c(a+bx))((d+ex)^n)^m`. P0's 1_4_1_r41 read the non-Optional `d_` as 1. Rubi's normalizing
    pair is 1_4_1_r43/r44 (`GeQ[a,0]` / `Not[GeQ[a,0]]`). The port emits `is(d >= 0)` /
    `not(is(d >= 0))`, while Rubi's `GeQ` is False on a symbol, so its `Not[GeQ]` is True. The port's r43
    cannot accept a symbolic d. Whether r44's `not(unknown)` accepts is not measured, and r44 did not fire.
    `GeQ` is not one of the fixed translations, and neither rule holds a fixed-defect site. — follows
    from: G-1 (P0 implicit-1 binding lost) plus an unlisted `GeQ` translation gap — [fixed-defect: none]
  - **e624** `%e^(a+bx+cx^2)(b+2cx)/(a+bx+cx^2)` (Rubi: 2 steps to `Ei`). P0's 1_2_1_3b_r68 bound only as
    `(d+0*x)^m`. Which Rubi rule answers first, and why it declines here, is not traced. — follows from:
    G-1 (P0 degenerate binding lost) — [fixed-defect: undetermined — Rubi's first step for e624 and its
    decline reason on the fixed core (a decline trace)]
  - **e767** `%e^(a+c+b x^n+d x^n)` (Rubi: 2 steps). P0's 2_3_r101 `u.*F^v*G^w` needed an absent second
    exponential. Rubi's first step is the exponent normalization; the port's candidates use
    `%mr_expandToSum` / `%mr_normalizeIntegrand`, which reach `%mr_posQ` / `%mr_signOfFactor` /
    `%mr_unifySum`. Nothing fired, and which rule declines is not traced. — follows from: G-1 (P0
    degenerate binding lost) — [fixed-defect: undetermined — which normalizing rule should take e767 and
    whether its decline turns on a changed sign/sibling port (a decline trace)]
- class 2 g4 (2 entries, deterministic, final unverified top=2_2_r2): 2_2_r2 binds first, as in g2.
  - **Chain.** It builds the corpus's `log(1+bF/a)` / `polylog(2)` / `polylog(3)` answer: 2_1_r9 and
    2_2_r1 (`%mr_iGtQ(m,0)`, m integer), 3_5_r14, and 2_3_r96 (FunctionOfExponential, which reaches
    `%mr_posQ`/`%mr_negQ`). e88 adds 3_3_r3, 2_3_r93 and 2_1_r10 (`%mr_iLtQ(p,0)`, `%mr_iGtQ(m,0)` on
    integers).
  - **Answer.** e82's answer term-matches the corpus answer once `li[3]` = `polylog(3)` and the brackets are
    expanded. It is unverifiable, not wrong: the zero chain does not close it. e88 has the same shape
    (cut).
  - **Arms and P0.** All arms unverified, and unverified on the defective tree. P0: 2_3_r70 alone,
    degenerate.
  - **Sites.** The integer tests read integers, and the FunctionOfExponential sites lead to the corpus
    answer.

  — follows from: faithful Optional binding (verdict: zero chain) — [fixed-defect: none]
- class 2 g5 (1 entry, deterministic, final contains-noun top=1_4_1_r7): **e726**
  `%e^((a+x)^2)/x^2 - 2 a %e^((a+x)^2)/x`.
  - **Final route.** 1_4_1_r7 splits the sum. 2_3_r28 (m=-2, `is(m < -1)`) reduces the first term to
    `-F/x + 2a Int[F/x] + 2 Int[F]`. 2_3_r11 gives `erfi` (`%mr_posQ(b)` with b=1, True in Rubi too).
    2_3_r32, the `F^…/(e+fx)` catch-all, gives one marker.
  - **What is missing.** In Rubi the two `Int[F/x]` pieces (+2a and −2a) cancel, and the corpus answer
    (3 steps) has no Unintegrable. nfires=5 with 5 distinct rules, so 2_3_r32 fired once: one of the two
    `F/x` integrals never reached the catch-all.
  - **Candidates for the other copy.** Either 1_4_1_r18 (fired once) bound the constant-factor term and
    its equal-form rewrite fell through (EQ-REWRITE), or `%mr_intTerm`'s constant split handed it on in
    another form. `%mr_intTerm` reaches `%mr_product_factors` / `%mr_removeContentAux`.
  - **Arms.** All contains-noun, and contains-noun on the defective tree. P0: 1_4_1_r7 alone.

  — follows from: faithful Optional binding (2_3_r28/r32 bind `x^-2`, `1/x`) — [fixed-defect: undetermined
  — trace the two `Int[%e^((a+x)^2)/x]` sub-calls: whether `%mr_intTerm`'s split (sibling-reachable)
  changes one copy's form, or 1_4_1_r18's rewrite takes a seen hit (EQ-REWRITE)]
- class 2 g6 (1 entry, deterministic, final deferred top=1_1_3_7_r45): **e557**
  `(F^(sqrt(1-ax)/sqrt(1+ax)))^n/(1-a^2x^2)`.
  - **Final core.** 1_1_3_7_r45 (`Pq (a+bx^n)^p` → `mr_int(ExpandIntegrand)`) fires alone and the answer is
    a top-level noun. P0 answered with the next rule, 1_1_3_7_r46.
  - **Arms.** All deferred, and deferred on the defective tree.
  - **Rule text.** The cond is `%mr_polyQ` / `%mr_polyPowerQ`, with no fixed-defect site. Which binding lets
    it accept is not traced.
  - **The nested call.** The repl's nested `mr_int` of the expansion has no fire: either a seen hit
    (EQ-REWRITE if ratsimp-equal, a real loop cut if stored-identical) or no rule.

  — follows from: not determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at
  1_1_3_7_r45 vs no rule; a `%mr_seenp` trace on its nested `mr_int` decides it]
- class 2 g7 (1 entry, deterministic, final deferred top=1_1_3_7_r46): **e50** `(F^(c(a+bx)))^n (d+ex)^(4/3)`.
  1_1_3_7_r46 (class 1, ahead of 2.1; repl a `%mr_subst` into a new variable, so not an equal form) answers
  with a top-level noun. P0's route was 2_1_r6/r7. r3 (cond_retry=false) reads verified 0.4 s, so r46
  accepts only on a non-first binding. r2/r4 deferred, as on the defective tree. Sites: `%mr_linearQ`,
  `%mr_polyPowerQ`; no fixed-defect site. — follows from: condition retry — [fixed-defect: none]
- class 2 g8 (1 entry, deterministic, final deferred top=1_2_3_5_r24): **e741** `(2-3x+x^2)/%e^(4x)`.
  1_2_3_5_r24 (the 1.2.3.5 `Unintegrable` catch-all, class 1) answers at top level. P0's route was 2_3_r3
  (expand). r3 verified 0.1 s, so the catch-all accepts only on a retried binding. r2/r4 deferred. Sites:
  `%mr_eqQ(n2,2n)`, `%mr_polyQ`/`%mr_polyPowerQ`; no fixed-defect site. — follows from: condition retry —
  [fixed-defect: none]
- class 2 g9 (2 entries, slow-correct, final timeout; final120 verified top=2_3_r19 / 2_3_r26): Same route on
  both cores (e283: 2_3_r16, 2_3_r19; e342: 2_3_r26). No fire was flushed before the 30 s kill.
  - **Walls.**

    | entry | P0 | final 30 s | final 120 s | 100 s re-check | r3 |
    |---|---|---|---|---|---|
    | e283 | 8.0 s | timeout | verified 57.7 s | verified 84.3 s | verified 0.4 s |
    | e342 | 4.0 s | timeout | verified 55.6 s | verified 86.6 s | verified 0.2 s |

    r2/r4 time out.
  - **Sites.** Neither rule's cond holds a fixed-defect site: 2_3_r19 uses `integerp` / `is` on integer n,
    2_3_r26 `%mr_eqQ`.

  — follows from: condition retry (cost) — [fixed-defect: none]
- class 2 NEW TIMEOUTS (14, all 2.3; P0 deferred 9, unverified 2, verified 2, error 1):
  - **100 s re-check.** Timeout 10, error 1 (e46, 63.2 s), unverified 1 (e255), verified 2 (e283, e342 =
    g9). Transitions: deferred→timeout 8, deferred→error 1, error→timeout 1, unverified→unverified 1,
    unverified→timeout 1, verified→verified 2.
  - **Arms over the 14.** r2 and r4 time out on all 14. r3 (cond_retry=false): verified 3, unverified 2,
    error 1, timeout 8. Most of the class-2 new-timeout cost is condition-retry work.
- class 2 new errors 2.3 e45, e56, e57 (shared cause):
  - **Error.** `err=Heap exhausted during garbage collection: 0 bytes available, 16 requested. | fatal
    error encountered in SBCL … | Heap exhausted, game over.`
  - **Fires.** e45 9.3 s: 1_1_2_1_r12, last completed 2_3_r57. e56 8.7 s and e57 13.5 s: 1_1_2_1_r12, last
    completed 2_3_r96.
  - **P0 and defective tree.** P0 was deferred 5.6 s (e45) and timeout (e56, e57), so none was a PASS.
    All three timed out on the defective tree.
  - **Fix site.** 1_1_2_1_r12 (`%mr_posQ(a/b)`, atan) is on all three routes. Whether the death comes
    before or after rubi returned is not determined from the trace.

## Class 3

- class 3 g1 (17 entries, deterministic, final unverified top=3_4_r8): All 17 have 3_4_r8 at top (subst x^n).
  - **Final nested chain.** 3_3_r8 → 3_3_r46 → 3_1_5_r45 (+ 3_1_5_r54 for p=3). e96/e97 take 3_1_4_r10,
    3_3_r3, 3_1_3_r6/r7, 3_1_4_r20, 3_3_r23, 3_3_r10.
  - **Answers.** All 17 read. Each still holds an unevaluated
    `'integrate(polylog(2|3,(b*x^2+a)/a)/(b*x^2+a), b*x^2+a)`-type noun. That is the class-8
    `PolyLog[n, c(a+bx)^p]/(d+ex)` step, not loaded. Unverifiable, not shown wrong.
  - **P0.** 11 entries share the 3_4_r8 top but stop at 3_3_r8/3_3_r31 (literal cannot bind 3_3_r46). 6
    entries (e80, e94, e95, e96, e97, e131) went through 3_5_r7/r8.
  - **Arms.** All unverified, except e96/e97, which r3 verifies (0.6 s).
  - **Sites.** The IGT sites on the route (3_1_5_r45, 3_3_r8, 3_4_r8, 3_1_3_r6, 3_1_4_r10/r20, 3_3_r23,
    3_3_r10) read integers p, q, (m+1)/n. The sibling site 1_1_1_1_r3 (`%mr_removeContent`) only sets a
    log argument's constant content.

  — follows from: faithful Optional binding; e96/e97 condition retry — [fixed-defect: none]
- class 3 g2 (13 entries, deterministic, final contains-noun top=3_2_2_r3): Both cores have 3_2_2_r3 at top.
  - **P0 nested.** 1_4_2_r25 (e122–e152) or 3_1_5_r29 (e173–e203).
  - **Final nested.** 3_1_4_r27, the 3.1.4 `Unintegrable` catch-all. 3_1_4_r26 (Rubi's ExpandIntegrand +
    `SumQ` rule, same LHS) does not answer. The 1_1_1_2_r12/r13 fires in the p=1 entries come from
    3_1_4_r23's cond sub-integral.
  - **Arms.** All contains-noun, as on the defective tree.
  - **Sites.** 1_1_1_2_r12/r13 and 3_1_4_r15 IGT sites read integers. `%mr_expandIntegrand2/3` reaches no
    changed port.

  — follows from: faithful Optional binding / MatchQ rewrite (1_4_2_r25 no longer answers); why 3_1_4_r26
  declines is not determined — [fixed-defect: none]
- class 3 g3 (13 entries, deterministic, final deferred top=3_1_4_r27): 3_1_4_r27 answers `Unintegrable` at
  top level alone (nfires=1). 3_1_4_r26 (same LHS, just ahead) declines. All arms deferred.
  - **e92–e119 (7)** `x^k (a+b log)^2/(d+ex)^q`. Rubi's r26 conds hold (`IGtQ[p,0]` with p=2 is True on
    both cores). P0's route was 3_1_5_r29; deferred on the defective tree too.
  - **e355/e363/e364 (3)** `(fx)^(m-1)(a+b log)^p/(d+e x^m)`. r26's integer conds fail in Rubi too. P0's
    route was the manual 9.1 `u*(a*x^n)^m` (P0 9_1_r16), which has no binding generated counterpart.
    Deferred on the defective tree.
  - **e427–e429 (3, fix-induced)** `(d+e x^r)^q (a+b log)^2/x`, q=1..3.
    - Defective tree: verified 0.3–0.5 s, route not traced. P5b: r27 alone.
    - r26's cond accepts by rule text: `is(q > 0)` holds, and the IGT branch is not needed. Its
      `%mr_expandIntegrand3` → `expand` path reaches no changed port. Why it declines is not determined.
    - The defective tree's fast PASS went through a rule the fix no longer lets accept. That rule is not
      traced. A plausible candidate is 1_4_1_r3 on the old strict NegQ of the symbol r, but it is not
      shown.

  — follows from: faithful Optional binding (P0 bound neither r26 nor r27) + the 9.1 regeneration
  (e355–e364); for e427–e429, a translation fix removed a defective-reading route (not traced) —
  [fixed-defect: none]
- class 3 g4 (7 entries, deterministic, final contains-noun top=3_1_4_r15): Both cores have 3_1_4_r15 at top
  (`%mr_iLtQ(q,-1)`, q=-2..-7 integer). P0 nfires=1: the nested integral fell through to Maxima integrate.
  On the final core the nested integral reaches the 3_1_4_r27 catch-all, and the 1_1_1_2_r12 fire comes
  from 3_1_4_r23's cond. All arms contains-noun, as on the defective tree. — follows from: faithful
  Optional binding — [fixed-defect: none]
- class 3 g5 (7 entries, deterministic, final timeout top=3_4_r8): VERIFY-TIMEOUT. Every 30 s fire list
  ends with the top-level 3_4_r8, which is also P0's top, so rubi returned.
  - **Chains.** Final: 3_1_5_r45, 3_1_4_r10, 3_3_r3, 3_1_3_r6/r7, 3_1_4_r20 (+1_1_1_*), 3_3_r23,
    3_3_r10. e438 instead takes 3_1_5_r54/r45, 3_3_r46, 3_3_r8. P0: 3_3_r31 (e438 3_3_r8) plus
    fall-throughs.
  - **Walls.**

    | cap | result |
    |---|---|
    | P0 | verified 2.8–6.7 s |
    | final 120 s | timeout ×5; e438 unverified 76.6 s (e525 not re-run: record unverified 23.1 s) |
    | 100 s re-check | e438 unverified 84.8 s, the rest timeout |

  - **Arms.** r3 verifies e484 (19.6 s) and times out on e525. The rest time out.
  - **Sites.** The IGT sites read integers.

  — follows from: faithful Optional binding (the cost is in verification); e484 partly condition retry —
  [fixed-defect: none]
- class 3 g6 (7 entries, deterministic, final unverified top=3_1_5_r47): Both cores have 3_1_5_r47 at top
  (`u = Int[(gx)^q log(d(e+fx^m)^r)]`, then `Dist` − `b n Int[Dist[1/x,u]]`).
  - **Final route.** `u` via 3_4_r8 → 3_3_r7 → 1_1_1_2_r12/r13 (or 1_1_1_1_r1/r3, 1_1_1_2_r3). Then
    `Int[Dist[1/x,u]]` via 1_4_1_r18 (+ 1_4_1_r7/r9 and 9_1_r12 in e50/e52). P0: 3_5_r34 / 3_5_r37 /
    1_4_1_r20.
  - **Answers (all 7 read).** Wrong in form. The `Int[u/x]` part holds `log(-X)*log(X+1)` and `li[2](X+1)`
    with X ∝ x·u, the inner antiderivative (which itself holds `log(d*f*x^2+1)`). No term of the corpus
    answer has that shape. No fire builds it, so it is consistent with an `integrate` fall-through.
  - **Arms.** All unverified, as on the defective tree.
  - **Sites.** 3_4_r8 and 1_1_1_2_r12/r13 IGT sites read integers. 9_1_r12 is exact-seen and appears only
    in e50/e52. 1_1_1_1_r3 (sibling) is only in e27/e93, while the wrong term also appears in e24/e90/e94.
    1_4_1_r18's rewrite is equal-form, so its nested call is an EQ-REWRITE candidate.

  — follows from: faithful Optional binding (3_4_r8 inner subst) — [fixed-defect: undetermined — trace
  the nested `Int[Dist[1/x,u]]`: whether 1_4_1_r18's `mr_int` takes a ratsimp seen hit (EQ-REWRITE) and
  hands Maxima `integrate` the rewrite that yields the `li[2](1+x·u)` term]
- class 3 g7 (6 entries, deterministic, final contains-noun top=3_2_1_r19): Both cores have 3_2_1_r19 at top.
  Nested on P0: 3_1_5_r28. On the final core 3_1_4_r29 binds first (3.1.4 is ahead of 3.1.5; its
  `%mr_iGtQ(p,0)` reads p=2,3, `is(q < -1)`). Its `Int[…(a+b log)^(p-1)/x]` reaches 3_1_5_r30 (AFx
  catch-all, live since 6a358db) and a marker. The corpus answers have no Unintegrable. All arms
  contains-noun, as on the defective tree. 3_2_1_r19's `%mr_iGtQ(p,0)` reads integers. — follows from:
  faithful Optional binding + AFx catch-all live — [fixed-defect: none]
- class 3 g8 (6 entries, deterministic, final contains-noun top=3_2_2_r15): Both cores have 3_2_2_r15 at
  top. Nested on P0: 3_5_r8 / 3_5_r11. On the final core the nested integral binds 3_2_1_r19 (3.2.1 is
  ahead of 3.5), then 3_1_4_r29 → 3_1_5_r30 (AFx) → marker. r3 deferred 0.2 s; r2/r4 contains-noun. IGT
  sites read integers. — follows from: faithful binding + AFx catch-all live; condition retry shapes the
  chain — [fixed-defect: none]
- class 3 g9 (6 entries, deterministic, final unverified top=3_2_2_r3): Both cores have 3_2_2_r3 at top.
  - **Final nested.** 3_1_5_r45, 3_1_4_r10, 3_3_r3, 3_1_3_r6/r7, 3_1_4_r20 (+ 3_1_3_r3/r8, 1_1_1_*), or
    3_1_2_r4/r5, 3_1_5_r45, 3_1_4_r10/r11.
  - **Answers (6 read).** Each holds an unevaluated
    `'integrate((polylog(2,(b*d*x+b*c)/(b*d*x+a*d))*…)` (the class-8 step). Unverifiable.
  - **Arms and P0.** r3 verifies e164 (0.7 s); the others are unverified in all arms. P0: nested
    3_1_5_r29 or none.
  - **Sites.** IGT sites read integers.

  — follows from: faithful Optional binding; e164 condition retry — [fixed-defect: none]
- class 3 g10 (4 entries, deterministic, final deferred top=3_1_3_r20): 3_1_3_r20 (3.1.3 catch-all) answers
  `(a+b log)^p/(d+e x^r)^2` (r=2,3) at top level alone. 3_1_3_r19's conds hold in Rubi (Rubi 16–26 steps),
  and its `%mr_expandIntegrand` `SumQ` test declines, as for 3_1_4_r26. P0's route was 3_1_5_r29. All arms
  deferred, as on the defective tree. — follows from: faithful Optional binding; why r19 declines is not
  determined — [fixed-defect: none]
- class 3 g11 (4 entries, deterministic, final timeout top=3_1_5_r47): The g6 route (1_1_1_2_r13, 3_3_r7,
  3_4_r8, 1_4_1_r18, top 3_1_5_r47 fired at 30 s), so rubi returned.
  - **Walls.**

    | entry | record | final 120 s | 100 s re-check |
    |---|---|---|---|
    | e51 | timeout | error 45.3 s | error 91.0 s |
    | e119 | timeout | error 47.2 s | error 63.2 s |
    | e120 | error 29.3 s (heap exhausted, see NEW ERRORS) | — | — |
    | e121 | timeout | error 50.9 s | error 69.1 s |

  - **Arms.** e51: r4 (model flags off) verified 1.5 s, r3 unverified 3.7 s. e119–e121 time out in the
    arms, as on the defective tree.
  - **Clearance.** Same as g6.

  — follows from: faithful Optional binding (the g6 route; verification cost / heap); e51 also model flags
  — [fixed-defect: undetermined — as g6: the nested `Int[Dist[1/x,u]]` trace (EQ-REWRITE at 1_4_1_r18)]
- class 3 g12 (4 entries, deterministic, final unexpected top=1_4_1_r3): Noun-expected entries (corpus
  `Unintegrable`, 0 steps). P0 no-answer: its literal `x^m (a+b x^n)^p Fx` did not bind.
  - **Binding.** The final core binds 1_4_1_r3 with n=−n (e383, e387) or −2n (e384, e388).
  - **NEGQ reading.** The cond `integerp(p) and %mr_negQ(n)` reads True on the fixed port, since
    TogetherSimplify(−n) = (−1)·n and PosAux of a product whose first factor is −1 is not PosAux(n). Rubi's
    `NegQ[-n]` reads the same, so the NEGQ reading is cleared. Rubi's r3 conds (1.4.1 line 50) hold as
    well. Why Rubi's own run returns a 0-step Unintegrable is not determined.
  - **Answer.** The rewrite's nested `mr_int` has no fire (nfires=1), so the answer is an `integrate`
    fall-through, not the marker. self=1 for e383/e384; cut for e387/e388.
  - **Arms.** All unexpected, as on the defective tree.
  - **EQ-REWRITE.** The rewrite is equal-form, so the fall-through is an EQ-REWRITE candidate.

  — follows from: faithful Optional binding — [fixed-defect: undetermined — NEGQ cleared; whether 1_4_1_r3's
  nested `mr_int` is a ratsimp seen hit (EQ-REWRITE) or finds no rule (a `%mr_seenp` trace)]
- class 3 g13 (4 entries, deterministic, final unverified top=3_1_4_r16): **Fix-induced** (defective tree
  verified 4.0–7.5 s). `(a+b log)/(x^k (d+ex^2)^q)`, q=−2,−3.
  - **Final route.** Top 3_1_4_r16 (`%mr_iLtQ(q,-1)`, `%mr_iLtQ(m,0)` on integers). Nested: 3_1_4_r11 →
    3_1_3_r13 → `u = Int[1/(d+ex^2)]` via 1_1_2_1_r12 (atan) → `Int[u/x]`.
  - **NEGQ.** 1_1_2_1_r12's `%mr_posQ(d/e)` is True on the fixed port (PosAux d → PosAux e^−1 → PosAux e).
    Rubi's third 1.1.2.1 rule (`PosQ[a/b]`, 1.1.2.1.m:92–96) reads the same. On the defective tree the
    strict sign made `%mr_negQ(d/e)` True, so 1_1_2_1_r15 (atanh) answered. P0's trace also shows r15 (in
    g36). The fix now takes Rubi's route.
  - **Why unverified.** `Int[atan(x/Rt)/x]` needs Rubi 5.3.2 (class 5, not loaded) and falls through to
    Maxima integrate. The answers (4 read) hold `%i*li[2](…)`, `%pi*log(e*x^2+d)` and `sqrt(abs(e))`:
    unverifiable, not shown wrong.
  - **Arms and sibling.** All arms unverified. The `%mr_rt(d/e,2)` sibling form (`sqrt(d)*sqrt(1/e)`) does
    not decide the verdict.

  — follows from: the NEGQ translation fix (Rubi's reading) exposing the unported class-5 step —
  [fixed-defect: none]
- class 3 g14 (3 entries, deterministic, final contains-noun top=1_4_1_r7): Sum integrands; both cores split
  with 1_4_1_r7 (`%mr_intSum`, which reaches the sign/sibling ports). Contains-noun in all arms and on the
  defective tree. The entries do not share a mechanism:
  - **e207** (P0 expected). The terms take 3_1_5_r55 (once), the 3_1_5_r57 polylog catch-all (once) and
    1_4_1_r18. In Rubi the two `q/(bn)·Int[polylog(k-1,e x^q)/(x(a+b log))]` pieces cancel, and the
    corpus answer (2 steps) has none. Only one copy reached the catch-all, the same signature as class 2
    g5. — follows from: faithful Optional binding (P0 literal cannot bind the `1/x` form) —
    [fixed-defect: undetermined — trace the two polylog sub-calls: `%mr_intTerm`'s split
    (sibling-reachable) vs 1_4_1_r18's equal-form rewrite (EQ-REWRITE)]
  - **e74/e75** (P0 nfires=1). The terms run 1_1_1_1_r2, 3_1_2_r2, 3_2_2_r3 → 3_2_2_r11 (3.2.2 catch-all)
    and a marker. There is one catch-all and no cancelling pair; this is the NOUN family (P0 fell through
    to Maxima integrate). 3_2_2_r3's repl is a `%mr_subst`. — follows from: faithful Optional binding —
    [fixed-defect: none]
- class 3 g15 (3 entries, deterministic, final contains-noun top=3_1_5_r56):
  `(dx)^m (a+b log) polylog(k, e x^q)`, k=1,2,3. 3_1_5_r56 (`%mr_iGtQ(k,0)`, k integer) reduces to nested
  integrals that reach 3_1_5_r30 (AFx) and a marker. The corpus answers of e220/e221/e222 all contain
  `Unintegrable`: a yardstick case. P0's route was the manual 9.1 `u*(a*x^n)^m`. All arms contains-noun. —
  follows from: 9.1 regeneration + AFx catch-all live — [fixed-defect: none]
- class 3 g16 (3 entries, deterministic, final contains-noun top=3_2_1_r20):
  `(f+gx)^m (A+B log(e(a+bx)^2/(c+dx)^2))^2`. 3_2_1_r20 (`%mr_iGtQ(n,0)`, n=2; `%mr_iGtQ(p,0)`, p=2) binds,
  then nested 3_1_4_r29 → 3_1_5_r30 (AFx) → marker. P0: workaround 3_2_1_r19, nested 3_1_5_r28. All arms
  contains-noun. — follows from: faithful binding + AFx catch-all live — [fixed-defect: none]
- class 3 g17 (3 entries, deterministic, final contains-noun top=3_3_r10): `(a+b log)^(k/2)/(f+gx)^3`.
  3_3_r10 is Rubi's 1-step rule; its cond reads `%mr_integersQ([2p,2q])` and `not(%mr_iGtQ(q,0))` with q=−3,
  the same as Rubi. Its sub-integral reaches 3_3_r32 (AFx) and a marker. The corpus answers contain
  `Unintegrable`: a yardstick case. P0's route was 3_5_r8. All arms contains-noun. — follows from:
  faithful Optional binding + AFx catch-all live — [fixed-defect: none]
- class 3 g18 (3 entries, deterministic, final contains-noun top=3_3_r9): `(a+b log)^(k/2)/(f+gx)^2`. Both
  cores have 3_3_r9 at top (no fixed-defect site). The sub-integral reaches 3_3_r32 (AFx) and a marker,
  the corpus shape (`Unintegrable` in the expected answers). All arms contains-noun. — follows from: AFx
  catch-all live — [fixed-defect: none]
- class 3 g19 (3 entries, deterministic, final contains-noun top=3_4_r11): 3_4_r11 (`%mr_iGtQ(q,1)`, q=2,3)
  binds; P0's literal did not. All arms contains-noun.
  - **e158/e159.** The sub-integral reaches 3_4_r34. The corpus answers (1 step) contain `Unintegrable`: a
    yardstick case. P0's route was the manual 9.1 `u*(a*x^n)^m`.
  - **e136.** The sub-integral `Int[log(c(d+ex^3)^p)/(d+ex^3)]` reaches 3_4_r27. Rubi needs a
    partial-fraction expansion of `1/(d+ex^3)` (39 steps). 3_4_r25's `%mr_expandIntegrand` (the `expand`
    path, reaching no changed port) cannot produce one, so its `SumQ` test declines. This is inferred from
    the rule text, not traced.

  — follows from: faithful Optional binding (+ 9.1 regeneration for e158/e159) — [fixed-defect: none]
- class 3 g20 (3 entries, deterministic, final deferred top=-): No rule answers (nfires=0).
  - **P0.** 3_5_r44 `u.*(a.*x^m.+b.*x^r.*log(c x^n)^q.)^p.`, which on these integrands needs an absent
    `x^r` or a zero coefficient.
  - **Rubi.** e625's corpus answer contains `Unintegrable`; e292/e293 are Rubi 2/8 steps.
  - **Arms.** All deferred, as on the defective tree.
  - **Unknown.** Rubi's own first rule, and why it declines, is not traced.

  — follows from: G-1 (P0 degenerate binding lost) — [fixed-defect: undetermined — Rubi's first step for
  e292/e293/e625 and its decline reason on the fixed core (a decline trace)]
- class 3 g21 (3 entries, deterministic, final deferred top=3_1_4_r26):
  `(fx)^m (d+ex^r)^q (a+b log)^p`, q=1..3.
  - **Final core.** 3_1_4_r26 (ExpandIntegrand + `SumQ`; `is(q > 0)` holds, IGT branch unused) fires alone
    (nfires=1), and the answer is a top-level noun. Its `mr_int(u)` gets an expansion sum, and no nested
    1_4_1_r7 fire follows.
  - **P0.** The manual 9.1 `u*(a*x^n)^m`.
  - **Arms.** All deferred, as on the defective tree.

  — follows from: 9.1 regeneration + faithful binding — [fixed-defect: undetermined — EQ-REWRITE at
  3_1_4_r26 (collapse mechanism, non-9.1 site) vs a `%mr_intSum` fault; a `%mr_seenp` trace on r26's
  nested `mr_int` decides it]
- class 3 g22 (3 entries, deterministic, final timeout top=3_1_4_r20): The 30 s fire list is mid-chain,
  ending with the g5 prefix and 1_1_1_2_r14. At 120 s the top-level 3_4_r8 has fired and the entries still
  time out: verification of 62-step Rubi forms. P0: 3_3_r31 + 3_4_r8 at 3.0–4.4 s. All arms time out, as
  on the defective tree. IGT sites read integers. — follows from: faithful Optional binding (cost in
  integration and verification) — [fixed-defect: none]
- class 3 g23 (3 entries, deterministic, final unverified top=3_1_4_r11): `(a+b log)^2/(x^k(d+ex))`.
  3_1_4_r11 (`%mr_iGtQ(p,0)` p=2, `%mr_iGtQ(r,0)` r=1, `%mr_iLtQ(m,-1)` m=−2..−4) binds, then 3_1_2_r4/r5,
  3_1_5_r45, 3_1_4_r10. The answers (3 read) end in `'integrate(polylog(2,-(d/(e*x)))/x,x)`, the class-8
  step: unverifiable. P0's route was 3_1_5_r29. All arms unverified. — follows from: faithful Optional
  binding — [fixed-defect: none]
- class 3 g24 (3 entries, deterministic, final unverified top=3_2_1_r2): Both cores have 3_2_1_r2 at top.
  Nested on the final core: 3_1_5_r45, 3_1_3_r6/3_1_4_r10, 3_2_1_r16/r17/r18 (IGT sites on n=2, p=3). The
  answers (3 read) hold `'integrate(polylog(2,…)…)` nouns, some with variable `(a*x+b)/x` or `x/(a*x+b)`:
  unverifiable. r3: e311 verified 0.4 s, e98 contains-noun; otherwise unverified. — follows from: faithful
  binding; e311 condition retry — [fixed-defect: none]
- class 3 g25 (3 entries, deterministic, final unverified top=3_2_2_r15): Both cores have 3_2_2_r15 at top.
  Nested on P0: 3.5 rules. On the final core, 3.2.1 rules (3_2_1_r15 / r19) → 3_1_4_r10 / 3_1_3_r6/r7 →
  3_1_5_r45/r54. The answers (read, e313's cut before the tail) hold `'integrate(polylog(k,…)…)` nouns:
  unverifiable. r3 deferred 0.2–0.3 s; r2/r4 unverified. — follows from: faithful binding; the final route
  needs condition retry — [fixed-defect: none]
- class 3 g26 (3 entries, deterministic, final unverified top=3_3_r6; P0 expected):
  `(a+b log(c(d+ex)^n))/(f+gx)` (e40, e220, e245 are the same integrand). Both cores have 3_3_r6 at top
  (`%mr_neQ` only).
  - **P0.** The sub-integral `Int[log(e(f+gx)/(ef-dg))/(d+ex)]` bound 3_4_r1 (`C polylog(2,1-u)`).
  - **Final core.** No nested fire (nfires=1); the sub-integral falls to Maxima integrate. The answer (read)
    holds `log(log((e*(g*x+f))/(e*f-d*g))/(e*x+d)+g*x)`, a log of a log expression: wrong in form. It is
    not an equal-form rewrite, so not EQ-REWRITE.
  - **3_4_r1.** Its cond (`%mr_polyQ`, `%mr_rationalFunctionQ`, `%mr_rationalFunctionExponents`, a
    `ratsimp` C) holds no changed-port site. By hand C = −1/e is free of x. Why it declines is not traced.
  - **Arms.** All unverified, as on the defective tree.

  — follows from: not determined from the traces — [fixed-defect: none]
- class 3 g27 (3 entries, deterministic, final unverified top=3_5_r15): `x^k log(a+%e^x b)`. 3_5_r15 binds,
  then 3_5_r14 (polylog), and 2_3_r96 for e115. e115's answer term-matches the corpus answer (x²/2 logs,
  `-x polylog(2)`, `li[3]`): unverifiable, not wrong. e113/e114 hold
  `'integrate(polylog(2,-((%e^x*b)/a))*x^k,x)`, the class-8 `PolyLog` step: unverifiable. The
  FunctionOfExponential site in 2_3_r96 (reaches `%mr_posQ`) produces e115's correct answer. P0's route was
  3_5_r34 / 3_5_r37. All arms unverified. — follows from: faithful Optional binding —
  [fixed-defect: none]
- class 3 g28 (2 entries, deterministic, final contains-noun top=3_1_4_r29): `(f+gx)(a+b log)^p/(d+ex)^3`.
  3_1_4_r29 (IGT on p=2,3) binds, and its `Int[…(a+b log)^(p-1)/x]` reaches 3_1_5_r30 (AFx) and a marker.
  P0 verified via 3_1_5_r28. All arms contains-noun. — follows from: faithful Optional binding + AFx
  catch-all live — [fixed-defect: none]
- class 3 g29 (2 entries, deterministic, final contains-noun top=3_1_5_r42):
  `(a+b log)^2 log(d(e+fx^2)^m)`. 3_1_5_r42 (`%mr_iGtQ(p,0)` p=2; 3.1.5 is ahead of 3.5) answers:
  `u = Int[(a+b log)^2]` (3_1_1 fires), then the `Dist`-ed `Int[x/(e+fx^2) u]` (1_4_1_r7, 1_4_1_r18)
  reaches the 3_1_4_r27 catch-all (r26 declines). There is one catch-all and no cancelling pair. P0: 3_5_r44
  at top (21–23 s). All arms contains-noun. — follows from: faithful Optional binding —
  [fixed-defect: none]
- class 3 g30 (2 entries, deterministic, final contains-noun top=3_3_r38): Both cores have 3_3_r38 at top.
  On the final core, the nested `Int[(gx)^(q+1) log(f x^m)/(d+ex)]` gets 1_1_1_2_r12 (from 3_1_4_r23's
  cond) → 3_1_4_r27 → marker. P0: 1_1_1_2_r13 plus a fall-through. All arms contains-noun. — follows from:
  faithful Optional binding — [fixed-defect: none]
- class 3 g31 (2 entries, deterministic, final contains-noun top=3_4_r36): **Fix-induced** (defective tree
  verified 1.8–2.3 s). `(a+b log(c(d+ex^m)^n))/(x log(f x^p)^k)`, k=2,3.
  - **Route.** 3_4_r36 (`%mr_neQ` only) → `Int[x^(m-1) log(f x^p)^(1-k)/(d+ex^m)]` → 3_1_4_r27 → marker.
  - **Rubi.** The corpus answers are Rubi's own 1-step shape with `Unintegrable(x^(-1+m)/((d+e*x^m)*log(…)^…))`:
    a yardstick case.
  - **P0 and the defective tree.** P0: 3_5_r44 (degenerate). The defective tree's verified route is not
    traced; the route on the fixed core has no fixed-defect site.
  - **Arms.** All arms contains-noun.

  — follows from: faithful Optional binding — [fixed-defect: none]
- class 3 g32 (2 entries, deterministic, final deferred top=3_2_2_r15):
  `1/((f+gx)(ah+bhx)(A+B log(…))^k)`. 3_2_2_r15's sub-integral reaches 3_2_2_r11 (the 3.2.2 catch-all), and
  the subst leaves a top-level noun. The corpus answers are `_subst(…, Unintegrable(…))`, 1 step: a
  yardstick case. P0: 3_2_2_r15 alone with a nested fall-through. r3 deferred 0.3 s; all arms deferred. —
  follows from: faithful Optional binding (NOUN) — [fixed-defect: none]
- class 3 g33 (2 entries, deterministic, final deferred top=3_3_r60): Both cores have 3_3_r60 at top.
  Final chain 3_1_5_r54/r45, 3_1_3_r6, 3_2_3_r8, 3_3_r61 (AFx), 1_1_1_1_r2, 3_1_2_r2 gives a top-level noun
  at 22.7–27.4 s. P0 verified via 3_3_r8, 3_2_3_r8 at 15–16 s. 3_3_r60's cond runs the sub-integral for
  `%mr_integralFreeQ` (moved inner condition), which does not reject the marker. IGT sites read integers.
  r3 deferred 2.2–2.3 s. — follows from: AFx catch-all live + moved inner condition — [fixed-defect: none]
- class 3 g34 (2 entries, deterministic, final timeout top=3_1_4_r21): **Fix-induced** (defective tree
  verified 4.2/5.0 s). `(a+b log)/(x (d+ex^2)^q)`, q=−3/2, −5/2.
  - **IGT fix.** 3_1_4_r16's `%mr_iLtQ(q,-1)` is now False for q=−3/2; Rubi 3.1.4 line 22 reads
    `ILtQ[q,-1] && ILtQ[m,0]`, so the reading is Rubi's. P0 and the defective tree read `is(q < -1)`, and
    r16 answered.
  - **Final route.** 3_1_4_r21 (Rubi line 27, `IntegerQ[q-1/2]`) with nested 1_1_2_2_r4, 1_1_1_2_r20/r32,
    1_1_2_1_r15 and 1_4_1_r18. `%mr_negQ(-d)` reads True in both Rubi and the port. The top-level r21
    fired at 30 s and 120 s, so rubi returned and the cap goes to verifying Rubi's route.
  - **Walls.** Timeout at 120 s and at the 100 s re-check. All arms time out.

  — follows from: the IGT translation fix (Rubi's reading; verification cost) — [fixed-defect: none]
- class 3 g35 (2 entries, deterministic, final timeout top=3_4_r5): VERIFY-TIMEOUT. Both cores have 3_4_r5
  at top. Final nested: 3_4_r8 → 3_3_r10/r23 → 3_1_4_r20 / 3_1_3_r6/r7 / 3_3_r3 / 3_1_4_r10 / 3_1_5_r45. The
  top-level fire is in the 30 s list. Walls: P0 4.0/5.2 s, final120 timeout. r3: e504 verified 6.0 s, e437
  timeout. IGT sites read integers. — follows from: faithful Optional binding; e504 condition retry —
  [fixed-defect: none]
- class 3 g36 (2 entries, deterministic, final unverified top=3_1_3_r12): **Fix-induced** (defective tree
  verified 1.4 s). `(a+b log)/(d+ex^2)^q`, q=−2,−3.
  - **Route.** 3_1_3_r12 → 1_1_2_1_r12 (atan; `%mr_posQ(d/e)` True, as in Rubi) → 3_1_3_r13 →
    `Int[atan(…)/x]`, which is class 5 (not loaded) and falls to Maxima integrate.
  - **P0.** 1_1_2_1_r15 (atanh), through the strict-sign reading.
  - **Answers (2 read).** `%i*li[2]`, `sqrt(abs(e))`: unverifiable.
  - **Arms.** All arms unverified.

  — follows from: the NEGQ translation fix exposing the unported class-5 step — [fixed-defect: none]
- class 3 g37 (2 entries, deterministic, final unverified top=3_1_4_r18):
  `(a+b log) x^k/(sqrt(d-ex) sqrt(d+ex))`. 3_1_4_r18 binds and feeds 3_1_4_r23 (cond sub-integral fires
  1_1_2_1_r15/r17, 1_1_1_2_r32/r11, 1_1_2_2_r4/r23, 1_4_1_r18).
  - **Sign readings.** `%mr_negQ(-d^2/e^2)` and `%mr_negQ(-e^2/d^2)` read True in both Rubi and the port.
  - **Answers.** `'integrate((log(d-sqrt(…))-log(…))/x,x)` (e312) and
    `'integrate(atan2(e*x,sqrt(d-e*x)*sqrt(e*x+d))/x,x)` (e313): inverse-function/x steps outside classes
    1–3, unverifiable.
  - **Arms and P0.** P0: 1_4_2_r25 alone. r4 times out on e312; otherwise unverified, as on the defective
    tree.

  — follows from: faithful Optional binding — [fixed-defect: none]
- class 3 g38 (2 entries, deterministic, final unverified top=3_2_3_r8): e51 has 3_2_3_r8 at top on both
  cores. For e52 P0's top was 3_2_3_r9; 3_2_3_r8 (`%mr_iGtQ(m,0)`) binds ahead of it. Nested: 3_1_5_r54/r45,
  3_3_r46, 3_3_r8. e52's answer holds
  `'integrate(polylog(2,-((d*h*x+d*g)/(c*h-d*g)))/(h*x+g),h*x+g)`, the class-8 step: unverifiable. All arms
  unverified. — follows from: faithful Optional binding — [fixed-defect: none]
- class 3 g39 (2 entries, deterministic, final unverified top=3_4_r36): **Fix-induced** (defective tree
  verified 2.0–2.1 s). `log(f x^p)^k (a+b log(c(d+ex^m)^n))/x`.
  - **Route.** 3_4_r36 → `Int[x^(m-1) log(f x^p)^(k+1)/(d+ex^m)]` → 3_1_4_r6 (`%mr_iGtQ(p,0)` on integer
    k) → 3_1_5_r45 → 3_1_5_r54. The answers end in `'integrate(polylog(4|3,-((e*x^m)/d))/x,x)`, the
    class-8 `PolyLog[n,a x^q]/x` step: unverifiable.
  - **Sign reading on m.** PosAux reads the symbol m as True, so NegQ[m] is False in Rubi and on the fixed
    port. On the defective tree NegQ[m] was True, which lets 1_4_1_r3 accept this sub-integrand. That
    defective route is plausible but not traced.
  - **Arms and P0.** P0: 3_5_r44 (degenerate). All arms unverified.

  — follows from: the NEGQ translation fix exposing the unported class-8 step — [fixed-defect: none]
- class 3 g40 (2 entries, deterministic, final unverified top=3_4_r38): `(a+b log(c(d+e/(f+gx))^p))^k`. Both
  cores run 3_4_r38 → 3_4_r3 → 3_4_r8 → 3_3_r8. The final core adds 3_3_r46, 3_1_5_r45 (+r54), and the
  answers (2 read) hold `'integrate((polylog(k,…)…)` nouns: unverifiable. IGT sites read integer q. All
  arms unverified. — follows from: faithful Optional binding — [fixed-defect: none]
- class 3 g41 (2 entries, deterministic, final unverified top=3_5_r35): **Fix-induced** (defective tree
  verified 2.3/2.7 s). `log(u)/(d+ex^2)`, with Rubi's own answer a 1-step `polylog(2,1-u)`.
  - **Rubi's rule.** The `Pq^m log(u)` rule (3_4_r1) answers on neither core.
  - **Both cores.** 3_5_r35: `v = Int[1/(d+ex^2)]`, then `v log u − Int[v u'/u]`.
  - **Final core.** v is atan (1_1_2_1_r12, `%mr_posQ(d/e)` True, as in Rubi). P0 and the defective tree
    took 1_1_2_1_r15 (atanh) through the strict-sign reading.
  - **Second integral.** It runs 1_4_1_r18, 9_1_r27, 9_1_r10 and ends in Maxima-integrate forms
    (`sqrt(d*e)`, logs of `sqrt(d)*sqrt(e)*sqrt(d*e)` expressions). Unverified at 12.5/18.2 s.
  - **Collapse sites.** The 9.1 fires call `mr_int_exact`, whose seen test is exact-member only, so the
    collapse misreading cannot occur there. Which sub-integral falls through is not traced.
  - **Arms.** All arms unverified.

  — follows from: the NEGQ translation fix (atan route) with Rubi's 1-step polylog rule not answering on
  either core — [fixed-defect: none]
- class 3 g42 (1 entry, deterministic, final contains-noun top=3_1_3_r7): e128 `sqrt(a+b log)/(d+ex)^2`; the
  corpus answer (1 step) contains `Unintegrable`. Both cores have 3_1_3_r7 at top. Its nested
  `Int[(a+b log)^(-1/2)/(d+ex)]` reaches 3_1_3_r20. 3_1_3_r19 declines, correctly: `is(q > 0)` fails for
  q=−1 and `%mr_iGtQ(-1/2,0)` is False, as `IGtQ` is in Rubi. The result is the corpus shape (yardstick).
  All arms contains-noun. — follows from: faithful Optional binding (NOUN) — [fixed-defect: none]
- class 3 g43 (1 entry, deterministic, final contains-noun top=3_1_3_r8): e129 `sqrt(a+b log)/(d+ex)^3`; the
  corpus answer contains `Unintegrable`. 3_1_3_r8 answers. Its cond `%mr_integersQ([2p,2q])` and
  `not(%mr_iGtQ(q,0))` (q=−3) reads as Rubi. Its nested integral reaches 3_1_4_r27 and a marker, the corpus
  shape (yardstick). P0: 3_5_r8 at top. All arms contains-noun. — follows from: faithful Optional binding —
  [fixed-defect: none]
- class 3 g44 (1 entry, deterministic, final contains-noun top=3_3_r34): e361
  `log(f x^m)(a+b log(c(d+ex)^n))`. Both cores have 3_3_r34 at top. On the final core, nested 1_1_1_2_r12
  (from 3_1_4_r23's cond) → 3_1_4_r27 → marker. P0: a nested fall-through. The corpus answer (8 steps) has
  none. All arms contains-noun. — follows from: faithful Optional binding — [fixed-defect: none]
- class 3 g45 (1 entry, deterministic, final contains-noun top=3_3_r39): e370. Both cores have 3_3_r39 at
  top (`%mr_iGtQ(p,0)`, p=2). On the final core the nested integral reaches 3_3_r56, the 3.3 two-log
  catch-all, and a marker. The corpus answer has none. All arms contains-noun. — follows from: faithful
  Optional binding — [fixed-defect: none]
- class 3 g46 (1 entry, deterministic, final contains-noun top=3_3_r54): e391
  `(a+b log(c(d+ex)^n))(f+g log(h(i+jx)^m))/x^2`. 3_3_r54 (`%mr_iGtQ(p,0)` p=1, `integerp(r)` r=−2) binds
  ahead of P0's 3_3_r55. Its sub-integral runs 1_1_1_1_r1/r3 and 1_1_1_2_r3 → 3_3_r32 (AFx) → marker. The
  1_1_1_1_r3 sibling site only sets a log's constant content; the verdict comes from the catch-all. All
  arms contains-noun. — follows from: faithful Optional binding + AFx catch-all live — [fixed-defect: none]
- class 3 g47 (1 entry, deterministic, final contains-noun top=3_4_r5): e522
  `(a+b log(c(d+e/x^(2/3))^n))^2`. Both cores have 3_4_r5 at top. On the final core the subst sub-integral
  runs 3_4_r11 (`%mr_iGtQ(q,1)`, q=2) → 3_4_r27 → marker. P0: a fall-through. The corpus answer (14 steps)
  has none. That 3_4_r25's `expand`-only `%mr_expandIntegrand` cannot split the rational factor, as for g19
  e136, is inferred and not traced. All arms contains-noun. — follows from: faithful Optional binding —
  [fixed-defect: none]
- class 3 g48 (1 entry, deterministic, final deferred top=1_4_1_r26): e350 `log(a x^(1-n))/(a x - x^n)`.
  - **Final core.** 1_4_1_r26 (`Fx (a x^r + b x^s)^p` → `x^(pr)(a+b x^(s-r))^p Fx`) fires alone
    (nfires=1), and the answer is a top-level noun.
  - **PosQ reading.** The cond `integerp(p) and %mr_posQ(s-r)` accepts on the retried binding s−r = 1−n,
    whose internal first term is 1, so PosAux reads True. Rubi's `PosQ[1-n]` (1.4.1 line 236, first term
    of `Plus[1,-n]`) reads True too. The other order, n−1, reads False on both. On the defective tree
    posQ(1−n) was False (strict), r26 did not accept, and it read deferred via 3_1_5_r30. So the NEGQ
    reading is cleared.
  - **The nested call.** The rewrite is equal-form, so its no-fire nested `mr_int` is an EQ-REWRITE
    candidate. Rubi's route is 3 steps to `polylog(2,1-a x^(1-n))`.
  - **P0.** Expected, via 3_5_r1.

  — follows from: the NEGQ translation fix (Rubi's reading) — [fixed-defect: undetermined — NEGQ
  cleared; whether 1_4_1_r26's nested `mr_int` is a ratsimp seen hit (EQ-REWRITE) or finds no rule (a
  `%mr_seenp` trace)]
- class 3 g49 (1 entry, deterministic, final deferred top=3_1_5_r30): e270 `(b+2cx) log(x)/(x(b+cx))`.
  3_1_5_r30 (AFx; `%mr_algebraicFunctionQ` reaches no changed port; 3.1.5 is ahead of 3.2.3) answers
  `Unintegrable` alone. P0 verified via its manual 9.1 rule (P0 id 9_1_r9) + 3_2_3_r16. No generated 9.1
  rule fired on the final core, so this is not a collapse fall-through. All arms deferred. — follows from:
  AFx catch-all made live (6a358db) + the 9.1 regeneration — [fixed-defect: none]
- class 3 g50 (1 entry, deterministic, final deferred top=3_3_r32): e223 `log(c(a+bx)^p)/(x(d+ex))`. 3_3_r32
  (AFx; 3.3 is ahead of 3.2.3) answers `Unintegrable` at top level. The 1_1_1_1_r1/r3 and 1_1_1_2_r3 fires
  have no answering parent (a cond sub-integral), and their sibling site does not decide the verdict. P0
  verified via its manual 9.1 rule + 3_2_3_r16. All arms deferred. — follows from: AFx catch-all live +
  faithful binding — [fixed-defect: none]
- class 3 g51 (1 entry, deterministic, final timeout top=-): 3.5 e83 `(d+ex)^3 log(d(a+bx+cx^2)^n)`. No fire
  was captured at 30 s or 120 s; P0 answered with 1_2_1_6_r1 → 3_5_r34 in 2.6 s. Either the top-level
  dispatch does not return, or its fires stayed in the unflushed pipe at the kill. The 100 s re-check and
  all arms time out, as on the defective tree. — follows from: not determined from the traces —
  [fixed-defect: undetermined — no route observed; a flushed trace (or the rule running at the kill)
  decides it]
- class 3 g52 (1 entry, deterministic, final timeout top=3_1_4_r23): e291
  `(a+b log)/(x^3 (d+ex^2)^(3/2))`. P0 took 3_1_4_r16 through `is(q < -1)`. On the fixed core
  `%mr_iLtQ(-3/2,-1)` is False, as Rubi's `ILtQ` is. 3_1_4_r23 (Rubi's `IntHide` rule) fired at top at 30 s
  and 120 s, so rubi returned and verification exceeds the cap (nested 1_1_2_1_r15 NegQ[−d] True in both;
  1_4_1_r25 IGT on integers). All arms time out, and it timed out on the defective tree too. — follows
  from: the IGT reading (Rubi's) + faithful binding; verification cost — [fixed-defect: none]
- class 3 g53 (1 entry, deterministic, final timeout top=3_4_r2): **Fix-induced** (defective tree unverified
  1.3 s, P0 verified 11.0 s). e29 `(a+b log) log(d(1/d+fx^2))`.
  - **Fires.** The last completed fires are 1_1_2_1_r12 (atan; `%mr_posQ(1/(d f))` True, as in Rubi),
    1_1_2_2_r23 and 3_4_r2. The enclosing rule does not complete by 120 s (P5 route: 3_1_5_r41).
  - **Why.** The atan form sends the `Dist`-ed `Int[u/x]` into the unported class-5 step and Maxima
    integrate, which does not return within the cap. Before, the strict sign gave the atanh route.
  - **Walls.** 100 s re-check timeout; all arms time out.

  — follows from: the NEGQ translation fix exposing the unported class-5 step — [fixed-defect: none]
- class 3 g54 (1 entry, deterministic, final unverified top=3_1_3_r13): **Fix-induced** (defective tree
  verified 0.8 s). e218 `(a+b log)/(d+ex^2)`. 3_1_3_r13 → `u = Int[1/(d+ex^2)]` via 1_1_2_1_r12 (atan,
  PosQ[d/e] True in both) → `Int[u/x]` (class 5) → Maxima integrate (`%i*li[2]`, `sqrt(abs(e))`). The
  corpus answer itself uses `%i polylog(2,…)`, Rubi's class-5 step. Unverifiable. P0 took 1_1_2_1_r15. All
  arms unverified. — follows from: the NEGQ translation fix exposing the unported class-5 step —
  [fixed-defect: none]
- class 3 g55 (1 entry, deterministic, final unverified top=3_1_4_r10): **Fix-induced** (defective tree
  verified 0.6 s). e430 `(a+b log)^2/(x(d+ex^r))`. 3_1_4_r10 (`%mr_iGtQ(p,0)`, p=2) → 3_1_5_r45. The answer
  ends in `'integrate(polylog(2,-(d/(e*x^r)))/x,x)`, the class-8 step: unverifiable. NegQ[r] on the symbol
  r is False in both Rubi and the fixed port; it was True on the defective tree, where the fast route is
  not traced (see g39). P0: 3_5_r44. All arms unverified. — follows from: the NEGQ translation fix exposing
  the unported class-8 step — [fixed-defect: none]
- class 3 g56 (1 entry, deterministic, final unverified top=3_1_4_r22): **Fix-induced** (defective tree
  verified 0.8 s). e431 `(a+b log)^2/(x(d+ex^r)^2)`. 3_1_4_r22 (`%mr_iGtQ(p,0)`, `%mr_iLtQ(q,-1)`: p=2, q=−2,
  as Rubi line 28) → 3_1_4_r7, 3_3_r3, 3_1_4_r10, 3_1_5_r45. The answer holds
  `'integrate(polylog(2,-(d/(e*x^r)))/x,x)`: unverifiable. P0: 3_5_r44. All arms unverified. — follows
  from: as g55 — [fixed-defect: none]
- class 3 g57 (1 entry, deterministic, final unverified top=3_1_4_r6): **Fix-induced** (defective tree
  verified 0.4 s). e620 `x^(m-1) log(f x^p)^2/(d+ex^m)`. 3_1_4_r6 (`%mr_iGtQ(p,0)`, p=2) → 3_1_5_r45. The
  answer holds `'integrate(polylog(2,-((e*x^m)/d))/x,x)`: unverifiable. P0: manual 9.1 `u*(a*x^n)^m`. All
  arms unverified. — follows from: as g55 (NegQ[m]) — [fixed-defect: none]
- class 3 g58 (1 entry, deterministic, final unverified top=3_1_5_r46): **Fix-induced** (defective tree
  verified 1.1 s). e389 `log(x) log(d+ex^m)/x`. 3_1_5_r46 (`%mr_iGtQ(p,0)`, p=1) → 3_1_4_r6 → 3_1_5_r45.
  The answer holds `'integrate(polylog(2,-((e*x^m)/d))/x,x)`: unverifiable. P0: 3_5_r42/r44 + 3_1_5_r46.
  All arms unverified. — follows from: as g55 — [fixed-defect: none]
- class 3 g59 (1 entry, deterministic, final unverified top=3_2_1_r1): e95 `log(c(b+ax)/x)^3`. 3_2_1_r1
  (`%mr_iGtQ(p,0)`, p=3) binds ahead of P0's 3_2_1_r2, then 3_1_5_r45, 3_1_3_r6, 3_2_1_r17. The answer holds
  `'integrate((polylog(2,(a*x+b)/(a*x))*x)/(a*x+b),(a*x+b)/x)`: unverifiable. All arms unverified. —
  follows from: faithful Optional binding — [fixed-defect: none]
- class 3 g60 (1 entry, deterministic, final unverified top=3_2_1_r17): e104. 3_2_1_r17 binds ahead of P0's
  3_2_1_r18, then 3_1_5_r45, 3_1_3_r6. The answer holds `'integrate(…polylog(2,…)…,(d*x+c)/(b*x+a))`:
  unverifiable. All arms unverified. — follows from: faithful binding — [fixed-defect: none]
- class 3 g61 (1 entry, deterministic, final unverified top=3_3_r37): e362. Both cores have 3_3_r37 at top.
  Nested on the final core: 3_1_5_r45, 3_1_3_r6. The answer holds `'integrate(polylog(2,-((e*x)/d))/x,x)`:
  unverifiable. All arms unverified. — follows from: faithful Optional binding — [fixed-defect: none]
- class 3 g62 (1 entry, deterministic, final unverified top=3_3_r47): e382. Both cores have 3_3_r47 at top
  (P0 nfires=1). Nested on the final core: 3_3_r46, 3_1_5_r46, 3_1_3_r6, 3_1_5_r45. The answer holds
  `'integrate(polylog(2,(e*x+d)/d)/(e*x+d),e*x+d)`: unverifiable. All arms unverified. — follows from:
  faithful Optional binding — [fixed-defect: none]
- class 3 g63 (1 entry, deterministic, final unverified top=3_3_r60; P0 expected): e433. Both cores run
  3_3_r60 → 3_3_r9 → 3_3_r6. P0 adds 3_4_r1 (`polylog(2,1-u)`); on the final core the sub-integral falls to
  Maxima integrate. The answer holds `li[2]`/`log` of expressions containing `log(-((f*h*x+f*g)/(e*h-f*g)))`:
  wrong in form, as in g26. All arms unverified. — follows from: not determined from the traces (as g26) —
  [fixed-defect: none]
- class 3 g64 (1 entry, deterministic, final unverified top=3_3_r9; P0 expected): e49. Both cores run
  3_3_r9 → 3_3_r6. P0 adds 3_4_r1. The final answer holds `log(log((e*(g*x+f))/(e*f-d*g))/(e*x+d)+g*x)`:
  wrong in form, as in g26. All arms unverified. — follows from: not determined from the traces (as g26) —
  [fixed-defect: none]
- class 3 g65 (1 entry, slow-correct, final timeout; final120 verified top=3_4_r12): e528
  `x^2 (a+b log(c(d+e/x^(2/3))^n))^3`.
  - **Walls.** P0 verified 5.2 s. Final 30 s timeout with the top-level 3_4_r12 fired (nested 1_4_1_r3,
    3_4_r11), so rubi returned. Final 120 s verified 73.7 s; 100 s re-check verified 72.6 s.
  - **Arms.** All arms time out at 30 s, as on the defective tree.
  - **Sites.** 1_4_1_r3's `%mr_negQ(n)` is on a number (n=−2 after the subst): True in both. 3_4_r11 IGT
    reads q=3.

  — follows from: not determined from the traces (which change alters the nested chain); the cost is
  verification — [fixed-defect: none]
- class 3 NEW TIMEOUTS (70; P0 deferred 31, verified 20, unverified 15, error 3, contains-noun 1; files
  3.4 22, 3.1.4 20, 3.3 17, 3.1.5 8, 3.5 2, 3.2.2 1):
  - **100 s re-check.** Timeout 56, error 4, unverified 4, verified 6.
    - The 6 verified: 3.1.4 e135 79.0 s, e156 37.4 s; 3.2.2 e106 66.0 s; 3.3 e150 57.6 s; 3.4 e528 72.6 s
      (g65); 3.5 e44 28.0 s.
    - The 4 errors: 3.1.5 e51/e119/e121 (g11) and e249.
  - **Transitions.**

    | P0 → 100 s | count |
    |---|---|
    | deferred → timeout | 26 |
    | verified → timeout | 15 |
    | unverified → timeout | 12 |
    | error → timeout | 3 |
    | verified → error | 3 |
    | unverified → verified | 3 |
    | deferred → verified | 2 |
    | deferred → unverified | 2 |
    | deferred → error | 1 |
    | contains-noun → unverified | 1 |
    | verified → unverified | 1 |
    | verified → verified | 1 |

  - **Group members.** The 20 P0-verified entries are all members of the timeout groups: g5 (6), g11 (3),
    g22 (3), g34 (2), g35 (2), g51, g52, g53 and g65.
  - **Arms over the 70.**
    - r2: timeout 64, unverified 3, error 2, verified 1.
    - r3: timeout 59, unverified 7, verified 2, contains-noun 1, error 1.
    - r4: timeout 63, verified 3, unverified 3, error 1.
- class 3 new errors (same error text for all three:
  `err=Heap exhausted during garbage collection: 0 bytes available, 16 requested. | fatal error encountered
  in SBCL … | Heap exhausted, game over.`):
  - **3.1.5 e120** (g11 member). P0 verified 10.3 s; defective tree error 26.1 s; P5b record error 29.3 s;
    newerror leg 26.1 s. Fires: the g11 route with 3_1_5_r47 last, consistent with a death while
    verifying.
  - **3.4 e356** `log(c(d+ex^2)^p)/(x^2 (f+gx^2)^2)`. P0 deferred 9.5 s; defective tree timeout 30.1 s;
    newerror leg 26.4 s with nfires=0. The death comes before any rule completed; where is not determined.
  - **3.5 e172** `log(a*cot(x)^n)`. P0 timeout 30.1 s (not a PASS); defective tree error 27.5 s; newerror
    leg 24.6 s. Fires: 9_1_r12, 9_1_r10, then 3_5_r31 last (the exact-seen 9.1 entry, both fired).

## Clearance summary

Counts are per group; a split group counts under its most severe sub-tag.

**Class 2 (9 groups):** none 5, IGT 0, NEGQ 0, NE 0, MUL 0, collapse 0, sibling:<port> 0, undetermined 4.

- g1 — undetermined. EQ-REWRITE at 2_3_r34 (collapse mechanism at a non-9.1 site) vs a `%mr_intSum` fault.
  Elimination on the fixed core points at the seen test, but P0's identical guard let the same rewrite
  dispatch.
- g3 — undetermined. e19 is none (unlisted `GeQ` gap); e624 and e767 have no route observed. For e767, the
  normalizing candidates reach `%mr_posQ` / `%mr_signOfFactor` / `%mr_unifySum`.
- g5 — undetermined. e726: a `%mr_intTerm` split (sibling-reachable) vs 1_4_1_r18 EQ-REWRITE.
- g6 — undetermined. e557: EQ-REWRITE at 1_1_3_7_r45 vs no rule.

**Class 3 (65 groups):** none 57, IGT 0, NEGQ 0, NE 0, MUL 0, collapse 0, sibling:<port> 0, undetermined 8.

- g6 — undetermined. A wrong `li[2](1+x·u)` term; 1_4_1_r18 EQ-REWRITE candidate.
- g11 — undetermined. The g6 route (verification timeout / heap).
- g12 — undetermined. NEGQ cleared; EQ-REWRITE at 1_4_1_r3 vs no rule.
- g14 — undetermined. e207: `%mr_intTerm` split vs 1_4_1_r18 EQ-REWRITE. e74/e75 are none.
- g20 — undetermined. No route observed (e292/e293/e625).
- g21 — undetermined. EQ-REWRITE at 3_1_4_r26 vs a `%mr_intSum` fault.
- g48 — undetermined. NEGQ cleared; EQ-REWRITE at 1_4_1_r26 vs no rule.
- g51 — undetermined. No fire captured at 30 s or 120 s.

**No group is explained by a fixed defect** under the checked readings.

- **The 23 fix-induced class-3 entries.** They moved onto Rubi's reading in each of these groups: IGT in
  g34 (and g52's route); NEGQ in g13, g36, g39, g41, g53–g58; route not traced in g3's e427–e429 and g31.
  They fail afterwards because a step is unported (class 5 `ArcTan/x`, class 8 `PolyLog`), verification
  exceeds the cap, or the result is Rubi's own `Unintegrable` shape.
- **The shared open question.** Nine undetermined groups (class 2 g1/g5/g6, class 3 g6/g11/g12/g14 e207/
  g21/g48) turn on EQ-REWRITE: does `mr_int`'s ratsimp seen test still read a non-9.1 equal-form rewrite
  as a loop? That is the collapse mechanism outside the 9.1 scope the fix covered. A `%mr_seenp` trace on
  2_3_r34's nested call would settle class 2 g1 and class 3 g21 and bound the rest.

## Diagnostic 16 re-reading

> Evidence: `probes/matcher/16-seen-guard-trace.out` (2026-09-15 11:49 UTC, Maxima branch_5_50_base_84_g4204fb669,
> SBCL 2.6.7, git HEAD 560b4a5, fixed core `b98e4748…`, P0 core `5ef9b3bc…`; `Results: 32 passed, 1 failed`).
> A row reads: ratsimp-only seen hit (trace arm) → class on the fixed core → class under the exact-only control
> (probe-local `%mr_seenp` = exact `member`: a DIAGNOSTIC ARM, not a proposed fix) → P0 route. Every trace-arm
> class equals probe 10's final30 class, except 3.1.5 e119 (error here, timeout there; heap exhausted in both arms).
> "Identity re-dispatch" = a rule's repl calls `mr_int` on the stored-identical integrand, and the exact
> `member` test cuts it in both arms (a true repeat, not a ratsimp reading).

- class 2 g1: undetermined → **collapse(non-9.1 site 2_3_r34)**. e202/e247/e248/e391/e392: ratsimp hit on
  2_3_r34's nested `mr_int` of the `%mr_expandLinearProduct` sum, matched against the live top-level integrand
  (#2@#1). Fixed deferred → control verified (5/5). A `%mr_intSum` fault is excluded: the call never dispatches.
  P0: 2_3_r34 answered in **pass 2**, which runs after `mr_top` has popped `%mr_seen`. The nested sum entered with
  seenlen=0, so no seen hit was possible, and 1_4_1_r7 split it. On e391/e392 each term's nested 2_3_r34
  re-dispatch was exact-cut to the integrate fall-through.
- class 2 g3: undetermined → **undetermined** (e19 stays none). e624, e767: one call, no rule fires, no nested
  call, no seen test involved. Control identical. The seen guard is excluded. Still missing: which rule should
  accept, and its decline reason (a decline trace).
- class 2 g5: undetermined → **none**. e726: no ratsimp hit. The missing `F/x` copy is 1_4_1_r18's identity
  re-dispatch of `(2*%e^(x+a)^2*a)/x`. Its cond accepts a constant `Qx`, so `u*Quotient^p*Qx^(p+q)` rebuilds the
  same integrand (#6 exact@#5). The copy returns as `'integrate(%e^(x+a)^2/x,x)`, while the other copy reaches
  2_3_r32's marker, so the pair cannot cancel. Control: same class, same answer. `%mr_intTerm` is not involved.
- class 2 g6: undetermined → **none**. e557: no ratsimp hit. 1_1_3_7_r45's expansion returns the integrand
  unchanged, and the exact test cuts it (#2 exact@#1). Control: same class, same answer. Why r45 accepts with an
  identity expansion is not traced; its cond holds no fixed-defect site.
- class 3 g6: undetermined → **none**. All 7 entries: 1_4_1_r18's identity re-dispatch of `Int[Dist[1/x,u]]`
  (exact hit, both arms) hands Maxima `integrate` the rewrite. That builds the wrong `li[2](1+x·u)` term.
  e50/e52/e94 also take a ratsimp hit at 1_1_1_2_r13 (`1/(x^2(fx+1/d))` → `1/(fx^3+x^2/d)`, #5@#4). That hit is
  collapse-type, but under the control 1_4_1_r25 rewrites back, the exact test cuts it one level down, and the
  answer is byte-identical (same sha1). Fixed unverified = control unverified (7/7).
- class 3 g11: undetermined → **none**. e51/e119/e120/e121: the g6 route, with a ratsimp hit at 1_1_1_2_r13 on
  all 4 (collapse-type, verdict and answer unchanged) and the 1_4_1_r18 identity re-dispatch. Fixed = control:
  timeout (e51/e120/e121), error (e119: `Heap exhausted`).
- class 3 g12: undetermined → **collapse(non-9.1 site 1_4_1_r3)**. All 4 entries: ratsimp hit on 1_4_1_r3's
  nested `mr_int` of its rewrite, against the live top-level integrand (#2@#1). The fixed core answers Maxima
  `integrate` of the rewrite (unexpected). Control:
  - e383, e384 → **no-answer (PASS)**, via 3_4_r34, the corpus's `Unintegrable` shape;
  - e387 → **contains-noun** (FAIL): 3_4_r29 → 3_3_r32 gives `'unintegrable[…,x^n]/n`, the marker inside a subst;
  - e388 → **unexpected**, the same FAIL class. Its answer differs: 3_4_r29 → 3_3_r28, whose identity
    re-dispatch is exact-cut, leaves a partial reduction holding `'integrate(…,x^n)` nouns, instead of Maxima's
    antiderivative of the rewrite.
- class 3 g14: undetermined → **none** (e74/e75 stay none). e207: no ratsimp hit. One polylog copy goes through
  1_4_1_r18's identity re-dispatch (#3 exact@#2) to `'integrate(li[k-1](e*x^q)/(x*(b*log(c*x^n)+a)),x)`. The
  other copy reaches 3_1_5_r57's marker, so the cancelling pair does not cancel. Control: same class, same answer.
- class 3 g20: undetermined → **undetermined**. e625, e292, e293: one call, no rule fires, no nested call,
  control identical. The seen guard is excluded. Still missing: Rubi's first rule and its decline reason (a decline
  trace).
- class 3 g21: undetermined → **collapse(non-9.1 site 3_1_4_r26)**. e448/e449/e450: ratsimp hit on 3_1_4_r26's
  nested `mr_int` of the `ExpandIntegrand` sum, against the live top-level integrand (#2@#1). A `%mr_intSum` fault
  is excluded. Fixed deferred → control verified (3/3; route 1_4_1_r7 → 1_4_1_r33 → 3_1_2_r10 → 2_1_r6).
  - **P0 route.** P0 never ran 3_1_4_r26: 9_1_r16 answered in **pass 2**, after the pop. Its nested
    `rubi_hybrid` call (seenlen=0) re-fired 9_1_r16, whose re-dispatch was an exact hit and fell through to
    integrate.
  - **P0 answer.** `((f*x)^m*'integrate(x^m*(e*x^r+d)^3*(b*log(c*x^n)+a)^p,x))/x^m` verifies only through the
    derivative of the integrate noun.
- class 3 g48: undetermined → **collapse(non-9.1 site 1_4_1_r26)**. e350: ratsimp hit on 1_4_1_r26's nested
  `mr_int` of `log(a*x^(1-n))/(x^n*(a*x^(1-n)-1))`, against the live top-level integrand (#2@#1). Fixed deferred
  → control verified (3_1_4_r5 → 1_1_3_7_r46, the corpus `li[2](a x^(1-n))` form).
- class 3 g51: undetermined → **undetermined** (narrowed). e83: the route is now observed up to the stall.
  - **Route.** The top call declines 3_5_r6/r8. The next rule attempt makes nested call #2,
    `Int[(2c e^4 x^5+…+b d^4)/(c x^2+b x+a)]`, which enters no deeper `mr_int` and is still inside dispatch at the
    30 s kill (last flushed lines: 1.1.1.2 / 1.1.3.3 cond declines). Both arms time out; no seen hit.
  - **Still missing.** Which top-level rule made call #2, and where its dispatch spends the time. P0 answered via
    1_2_1_6_r1 → 3_5_r34. Rubi does not return within 30 s here, and did not in probe 10's 120 s leg, so a 30 s
    re-run cannot complete it.

**Re-read summary.** collapse 4 (class 2 g1; class 3 g12, g21, g48), none 5 (class 2 g5, g6; class 3 g6, g11,
g14), undetermined 3 (class 2 g3 e624/e767; class 3 g20, g51, where the seen guard is excluded for g3/g20). Under
the exact-only control, 9 entries verify that do not on the fixed core (class 2 g1 ×5, class 3 g21 ×3, g48 e350).
2 more reach PASS as no-answer (class 3 g12 e383/e384).
