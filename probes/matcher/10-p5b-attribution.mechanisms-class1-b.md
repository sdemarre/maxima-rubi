# P5b mechanism lines — class 1, part B (g24–g171)

> Translation fixes, Task 7 Step 4. One line per probe-10 GROUP g24–g171, each with its defect-clearance tag.
> Reads: `probes/matcher/10-p5b-attribution.class1.summary.out` lines 1902–3780 and the raw legs
> `…class1-{final30,p0,final120,newerror}.out`. g1–g23, g172–g262, NEW TIMEOUTS and NEW ERRORS are other readers'.
> Written 2026-09-15 by read-only analysis (no Maxima run). Cores: fixed `b98e4748784738cb78f0163a97d4cf5f`
> (P5b final record `test/corpus_class1.p5b-run1.out`), P0 `5ef9b3bc5ee07ffac0e76f1fea54fbac`.

Evidence used beyond the summary, and how to read the lines:

- **Arms.** `r2`/`r3`/`r4` = `test/corpus_class1.p5b-run{2,3,4}.out` (mr_flat_wide=true / mr_cond_retry=false /
  mr_model_flags=false). `p5` = the defective tree's record `test/corpus_class1.p5-run1.out`; where a P5b entry
  also failed on P5, its P5 fire list is the defective tree's leg `probes/matcher/10-p5-attribution.class1-final30.out`.
  `t100` = `test/corpus_class1.p5b-final.timeout-rerun/corpus_class1.p5b-run1.timeout100s.out`.
- **Fix-induced** = P0 PASS, p5 PASS, P5b FAIL. The defective tree's route for these is never traced (probe 10 on
  P5 re-ran only P5 failures), so "the defective route is not traced" is said once per group, not argued.
- **Completion order.** A fire list is in completion order, so the first-listed rule has no completed child. When
  that rule is an equal-form rewrite (`mr_int(%mr_expandIntegrand…)`, `%mr_expandToSum`, `%mr_polyQuotient`), its
  nested `mr_int` recorded no fire: that is the EQ-REWRITE candidate (seen hit) against "no rule binds" (or a
  `%mr_intSum` fault when the rewrite is a sum, since 1_4_1_r7 answers any dispatched sum).
- **EqQ/NeQ gap (unlisted, not a fixed defect).** `%mr_eqQ(u,v)` is `%mr_b(u-v=0)` and `%mr_neQ(u,v)` is
  `is(u-v=0)` negated (`maxima_rubi_utils.mac:369–372`): both are syntactic. Rubi's `EqQ`/`NeQ` use
  `PossibleZeroQ` (`IntegrationUtilityFunctions.m:365, 370`). Two families follow:
  - **EQQ-FAMILY.** The quadratic `c d^2-b d e-b e^2 x-c e^2 x^2` or `a d e+(c d^2+a e^2)x+c d e x^2` has the factor
    `d+ex`, so `c d^2-b d e+a e^2` is identically 0, but only after expansion (e.g. `-c d^2 e^2+b d e^3+e^2(c d^2-b d e)`).
    The port's EqQ-case rules (`1_2_1_3_r31–r41, r62–r82, r88`; Rubi loads only this `(f+g x)^n` file, `Rubi.m:144`)
    read EqQ False, and the NeQ-case rules accept and divide by that zero. Several answers print the divisor
    literally: `(b*d*e^3-c*d^2*e^2+e^2*(c*d^2-b*d*e))` (g96), `(a*d*e^3-d*e*(a*e^2+c*d^2)+c*d^3*e)` (g58, g94, g95).
  - **ZERO.** The corpus coefficient `2+2a-2(1+a)` reads as nonzero.
- **Ticket-02 sites (GeQ/GtQ/LtQ reading).** A route counts here when a rule Rubi applies has a negated comparison
  on a symbolic argument, and the fires show that rule did not accept (a later rule answered instead).
  - `1_2_2_3_r58` `not(is(a > 0))` = Rubi 1.2.2.3 line 62 `Not[GtQ[a, 0]]`.
  - `1_1_3_1_r24` `not(is(a/b > 0))` = Rubi 1.1.3.1 line 29; `1_1_3_2_r40` = 1.1.3.2 line 46.
  - `1_1_2_5_r17` `not(is(d/c > 0)) and is(c > 0) and is(e > 0)…` and `1_1_2_5_r18` `not(is(c > 0))` = Rubi
    1.1.2.5 lines 135 and 141.
  - `1_2_2_3_r19` `… or not(is(2*d/e - b/c < 0)) and …` = Rubi 1.2.2.3 line 23 `Not[LtQ[…]]`.
  Whether a bare `not(is(…))` answers `unknown` and is rejected is not measured (ticket 02). Only the fact that the
  rule did not answer is observed.
- **IntPart/FracPart.** `%mr_intPart_aux` / `%mr_fracPart_aux` read a rational by `floor`
  (`maxima_rubi_utils.mac:2952–2990`). Rubi's `IntPart` uses `IntegerPart` (truncation, `.m:2957–2961`). The two
  differ for negative non-integer rationals: IntPart(-1/2) is -1 in the port and 0 in Rubi. For a bare rational this
  branch is unchanged by 843eb5f, since `atom(-1/2)` is true in Maxima and already short-circuited the old `m_*u_` arm.
- **Tables.** Per-group counts below were taken mechanically from the summary and the arm records.

## Class 1 (g24–g171)

- class 1 g24 (10 entries, deterministic, final unverified top=1_2_1_3_r57): EQQ-FAMILY, all fix-induced.
  - **Integrand.** 1.2.1.3 `(f+gx)sqrt(c d^2-b d e-b e^2x-c e^2x^2)/(d+ex)^k`.
  - **Final route.** Top 1_2_1_3_r57 (`is(m < -1)` + integer tests, no NeQ in its cond) accepts; the EqQ rule Rubi
    uses (`1_2_1_3_r40`: `LtQ[m,-1] && Not[IGtQ[m+p+1,0]]`) reads EqQ False. r57's repl divides by the
    identically-zero `c d^2-b d e+a e^2`, and its nested integral runs 1_4_1_r18 with no fire under it.
  - **Answers (10 read).** Expanded `640*e^7*x^7+…` denominators: the zero-divisor antiderivative, wrong.
  - **P0.** 1_4_2_r25 → 1_3_3_r6 (PolyGCD cancel), verified 2.4–3.2 s. p5 verified 0.8–1.0 s (route not traced).
  - **Arms.** All unverified. The r18 fall-through is an EQ-REWRITE candidate but does not decide the verdict.

  — follows from: EqQ/NeQ syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g25 (9 entries, deterministic, final deferred top=1_2_2_7_r41): 1_2_2_7_r41 (Rubi's
  `PolyQ[Px,x^2] && IntegerQ[p+1/2] && IntegerQ[q]` hold) answers `(A+Bx^2)(d+ex^2)^q/(a+cx^4)^(k/2)` alone
  (nfires=1, 1.2–1.8 s). Its 3-arg `%mr_expandIntegrand(1/sqrt(a+cx^4), …)` is a sum, and no nested 1_4_1_r7 fire
  follows. P0: 9_1_r9, 1_2_2_8_r18, 1_2_2_5_r9/r8, or 1_4_1_r7, 1_2_2_7_r40 (2.2–8.5 s). The defective tree was the
  same (deferred). All arms deferred. No fixed-defect site in the cond. — follows from: not determined from the traces —
  [fixed-defect: undetermined — EQ-REWRITE at 1_2_2_7_r41 (vs a `%mr_intSum` fault), awaiting probe 16]
- class 1 g26 (9 entries, deterministic, final timeout top=1_1_2_1_r13): MID-CHAIN.
  - **Integrands.** 1.2.1.4/1.2.1.5/1.2.1.6 `1/((quad)sqrt(1∓dx))`, `1/((d+ex+fx^2)sqrt(a+cx^2))`, `sqrt(Q1)/Q2`.
  - **Fires.** The only flushed fires are the nested 1_1_2_1_r13 (atanh; `NegQ[-4c]`-type, same in Rubi) and, for
    e102/e111, 1_2_1_1_r15, at 30 s and at 120 s. No top-level rule completes.
  - **P0.** 1_2_1_4_r24/r12 → 1_2_1_3_r8, 1_2_1_4_r27, 1_2_1_9_r18, or 1_4_2_r17, verified 2.2–5.6 s. On the defective
    tree there was no fire, 9_1_r8, or the same r13/r15.
  - **Timing.** t100 timeout 9; all arms timeout.

  — follows from: not determined from the traces — [fixed-defect: undetermined — no top-level route observed at 30 s
  or 120 s; a flushed trace (the rule running at the kill) decides it]
- class 1 g27 (9 entries, deterministic, final unverified top=1_2_3_2_r34):
  - **Final route.** 1_2_3_2_r34 (the `a^IntPart[p](…)^FracPart[p]/(…)^FracPart[p]` rewrite) → 1_1_3_4_r78 (AppellF1).
    This is Rubi's 2-step shape, but AppellF1 answers are not closed by the zero chain.
  - **P0.** The manual 9.1 `u*(a*x^n)^m` (9_1_r16).
  - **Defective tree.** e256/e606/e154 took the same route (unverified). e255 went 1_2_3_2_r15 (IGT, CN); e602/e603
    went 1_2_3_2_r2 (IGT, deferred). The IGT fix moved these onto r34. e254/e604/e605 are fix-induced (p5 verified
    0.7–3.4 s, route not traced).
  - **Arms.** All unverified.
  - **The entries split on the sign of p:**
    - **e254, e604 (p=-1/2), e255, e605 (p=-3/2).** r34's `%mr_intPart(p)`/`%mr_fracPart(p)` read floor: (-1, 1/2)
      and (-2, 1/2). Rubi reads (0, -1/2) and (-1, -1/2). The answers carry the floor form
      (`…sqrt(c*x^6+b*x^3+a))/(a*d…`, `a^2` for p=-3/2); the corpus answers carry Rubi's (`…/(d(1+m)sqrt(a+bx^3+cx^6))`).
      The two are algebraically equal. Whether the form decides the verdict is not measured, and this floor
      branch is unchanged by 843eb5f, so it does not explain the defective tree's PASS. — [fixed-defect:
      sibling:%mr_intPart_aux]
    - **e256, e606, e154 (symbolic p), e602 (p=3/2), e603 (p=1/2).** IntPart/FracPart read as Rubi. The answers are
      unverifiable AppellF1. — [fixed-defect: none]

  — follows from: the IGT translation fix (e255, e602, e603 onto Rubi's route) + the AppellF1 verdict — [fixed-defect:
  sibling:%mr_intPart_aux]
- class 1 g28 (8 entries, deterministic, final contains-noun top=1_1_1_2_r20): Fix-induced (p5 verified 0.2–0.3 s).
  - **Integrand.** 1.1.1.2 `1/((a+bx)^(3/2|1/2)(c+dx)^(1/4|5/4))`.
  - **Final chain.** r20 → 1_1_1_2_r32 (x^4 substitution) → 1_1_3_2_r49 (`%mr_negQ(b/a)`; NegQ in Rubi too, the
    first term of `bc-ad` is `-ad`). Its `Int[(1+q x^2)/sqrt(A+Bx^4)]` has `EqQ[c d^2+a e^2,0]` true, so Rubi's
    rule is 1_2_2_3_r58 `Not[GtQ[A,0]]` (True on the symbolic sum A). The port's `not(is(A > 0))` does not
    answer, r57 needs `GtQ`, r59 needs NeQ, and the catch-all 1_2_2_3_r100 gives the marker.
  - **Corpus.** Elliptic E/F, no Unintegrable.
  - **Arms and P0.** r3 verified 8/8 (0.1–0.2 s) on another route; r2/r4 CN. P0: 1_1_1_4_r46/1_1_3_1_r33 chains →
    1_1_1_2_r39/r11.

  — follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g29 (8 entries, deterministic, final contains-noun top=1_2_1_3_r53): CATCH-1, as on the defective tree
  (P5 g44/g94, same fires).
  - **Integrand.** `(2-5x)x^(k/2)/(2+5x+3x^2)^(j/2)`.
  - **Route.** 1_2_1_3_r53/r54/r56 reduce, and 1_4_1_r34 substitutes x^(1/2). The quartic `P(x)/(2+5x^2+3x^4)^(j/2)`
    reaches the catch-all 1_2_2_6_r9 or 1_2_2_7_r42.
  - **Corpus.** Elliptic, no Unintegrable. P0: 1_2_2_1/1_2_2_2/1_2_2_3/1_2_2_5 chain under 1_4_1_r34.
  - **Arms.** All CN.
  - **Sites.** The IGT sites (`not(%mr_iLtQ(m+2p+3,0))`) read numbers. Why Rubi's quartic rules decline is not
    traced.

  — follows from: faithful Optional binding — [fixed-defect: none]
- class 1 g30 (8 entries, deterministic, final deferred top=1_1_2_8_r102): 1.2.1.4 `sqrt(a+cx^2)/(x^2(d+ex))`-type.
  - **The IGT fix.** It removed the defective routes: 1_1_2_8_r7 `IGtQ[p,0]` (e322–e325) and r100 `ILtQ[p,0]`
    (e332–e341), which had accepted p=±1/2.
  - **Final core.** 1_1_2_8_r102 (`%mr_iLtQ(n,0) and integerp(m) and integerp(2p)`, n=-1, Rubi's reading) answers
    alone (nfires=1, 0.4–0.5 s). Its 2-arg ExpandIntegrand is a partial-fraction sum, and no nested 1_4_1_r7 follows.
  - **P0 and arms.** P0: 1_1_2_8_r106 after long chains. All arms deferred.

  — follows from: the IGT translation fix (Rubi's reading) — [fixed-defect: undetermined — EQ-REWRITE at
  1_1_2_8_r102 (vs a `%mr_intSum` fault), awaiting probe 16]
- class 1 g31 (8 entries, deterministic, final deferred top=1_2_1_3_r20): 1_2_1_3_r20 (`IntegersQ[n]`, Rubi's
  conditions hold) answers `(ex)^m(A+Bx)/(a+bx+cx^2)`, `(2+3x)^4(1+4x)^m/(1-5x+3x^2)` alone (nfires=1). No nested fire
  follows its expansion. The defective tree was the same. P0: 1_2_1_3b_r68 or 1_2_1_3_r109 after 1_4_1_r7
  (4.6–12.2 s). r3 verified e1086/e1657/e2643/e2645/e933 (0.6–0.9 s), so r20 is reached only on a retried binding;
  the others are deferred in all arms. — follows from: condition retry (5) — [fixed-defect: undetermined — EQ-REWRITE
  at 1_2_1_3_r20 (vs a `%mr_intSum` fault), awaiting probe 16]
- class 1 g32 (8 entries, deterministic, final deferred top=1_2_2_4_r96): CATCH-1, identical on the defective tree
  (P5 g42). The 1.2.2.4 catch-all answers `(fx)^m(d+ex^2)(1+2x^2+x^4)^5` at top. The quartic is a perfect square, and
  `%mr_neQ(b^2-4ac,0)` reads numbers, so rejecting 1_2_2_4_r19/r93 is Rubi's reading. The corpus answers are 3-step
  expansions. P0: 1_2_2_5_r1, 1_1_1_5_r4 or 1_2_2_6_r3. All arms deferred. — follows from: faithful Optional binding
  (`m_.`, `q_.`); why Rubi's `EqQ[b^2-4ac,0]` rule is not reached is not traced — [fixed-defect: none]
- class 1 g33 (8 entries, deterministic, final error top=1_2_2_2_r8): 1.2.3.2 `1/((d+ex)^k(a+b(d+ex)^2+c(d+ex)^4))`.
  - **Error.** `err=Heap exhausted during garbage collection … Heap exhausted, game over`, at 15.8–30.0 s.
  - **Fires.** Only a nested 1.2.2.2 chain (1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_2_r3/r9/r13/r80/r84/r115, 1_2_1_3_r89,
    1_2_2_2_r8), with no top-level fire. The route holds sibling-reachable sites (1_2_1_2_r3 `%mr_removeContent`,
    1_1_2_1_r13 `%mr_rt`).
  - **P0.** 1_4_2_r24, verified 1.3–1.5 s.
  - **Defective tree and arms.** Error or timeout with the same lists; error in all arms.

  — follows from: not determined from the traces — [fixed-defect: undetermined — where the heap is exhausted (the rule
  running at the death); the same death on the defective tree clears the fixes as its cause, not a residual site]
- class 1 g34 (8 entries, deterministic, final timeout top=1_1_3_4_r22): VERIFY-TIMEOUT.
  - **Integrand.** 1.1.3.4 `x^(k/2)(A+Bx^3)/(a+bx^3)^2`.
  - **Final route.** Top 1_1_3_4_r22 fired at 30 s and 120 s. The first completed fire is 1_1_3_7_r45
    (`mr_int(%mr_expandIntegrand(Pq(a+bx^n)^p))`, no child). Then 1_2_1_1_r12, 1_2_1_2_r3/r9, 1_1_2_1_r10 (atan),
    1_1_3_2_r37 (`%mr_iGtQ((n-2)/4,0)` n=6, `%mr_posQ(a/b)` True as in Rubi), 1_1_3_2_r71/r67/r32.
  - **Defective tree.** RT-SUM 1_1_3_2_r36/1_1_3_1_r14 (IGT + NEGQ). The fixes put the route on Rubi's PosQ branch.
  - **Timing.** P0 1.6–3.8 s; t100 timeout 8; all arms timeout.
  - **Why EQ-REWRITE.** The same r45 prefix yields the Maxima-integrate complex-log answers of g93 e1326 and g151.

  — follows from: the IGT/NEGQ translation fixes (Rubi's route) + verification cost — [fixed-defect: undetermined —
  EQ-REWRITE at 1_1_3_7_r45 (vs no rule), awaiting probe 16]
- class 1 g35 (7 entries, deterministic, final contains-noun top=1_1_1_2_r16): Fix-induced (p5 verified 0.1–0.3 s).
  1.1.1.2 `(a+bx)^(5/2)/(c+dx)^(5/4|1/4)`. r16 (+r19/r20) → 1_1_1_2_r32 → 1_1_3_2_r49 → 1_2_2_3_r100, as in g28:
  Rubi's 1_2_2_3_r58 `Not[GtQ[A,0]]` does not answer. The corpus answers are elliptic. r3 verified 7/7 (0.2 s);
  r2/r4 CN. P0: 1_1_3_1_r33 … 1_1_1_2_r10 chains (5.0–5.4 s). — follows from: GeQ/GtQ reading (ticket 02) —
  [fixed-defect: none]
- class 1 g36 (7 entries, deterministic, final deferred top=1_1_2_6_r3): 1_1_2_6_r3 (`%mr_iGtQ(p,-2)`,
  `%mr_iGtQ(q,0)`, `%mr_iGtQ(r,0)` on integers, Rubi's reading) answers `(ex)^m(A+Bx^2)(c+dx^2)^k/(a+bx^2)` alone
  (nfires=1). No nested fire follows its expansion sum. The defective tree was the same. P0: 1_2_1_9b_r5/1_1_2_3_r1/
  1_4_1_r7 or 1_1_2_6_r9/r12 (4.2–29.0 s). r3 unverified 4 (e5/e12/e19/e25); otherwise deferred. — follows from: not
  determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at 1_1_2_6_r3 (vs a `%mr_intSum` fault),
  awaiting probe 16]
- class 1 g37 (7 entries, deterministic, final deferred top=1_1_3_7_r46): 1_1_3_7_r46 (linear substitution
  `%mr_subst(mr_int(%mr_substFor…))`, not an equal form) answers `x^m/(a+bx)^(k/2)` alone with a top-level noun. The
  defective tree was the same. P0 e710–e723: 1_1_1_2_r38/r39 on `(0+1·x)^m` (DEG). P0 e731/e752: 1_1_1_4_r46,
  1_3_4_r1. r3 verified e723/e731/e752 (0.6 s). The cond (`%mr_linearQ`, `%mr_polyPowerQ`) has no fixed-defect site.
  — follows from: G-1 (P0 degenerate binding lost) + condition retry (3) — [fixed-defect: none]
- class 1 g38 (7 entries, deterministic, final timeout top=1_2_1_1_r15): At 30 s the list ends in the nested
  1_1_2_1_r13, 1_2_1_1_r15.
  - **120 s.** The top-level rule has fired (1_2_1_6_r4 `is(p < -1)` on numbers for 1.2.1.5 e116 and 1.2.1.9
    e182/e236; 1_2_4_2_r8/r4 for 1.2.4.2), so the entries are VERIFY-TIMEOUT at 120 s. e109 dies at 115.9 s (t100
    error 97.1 s).
  - **P0.** 1_2_1_6_r1 or 1_3_3_r15/r14/r10 → 1_4_1_r34 (1.1–4.7 s).
  - **Fix-induced.** e116/e182/e236 (p5 verified 0.6–0.8 s); the other 4 matched P5 g71.
  - **Arms.** r3 CN for e116/e182/e236/e109; otherwise timeout.
  - **Sites.** The route's sites (NegQ[-4c]-type, `is(p>0)`) read as Rubi.

  — follows from: not determined which change moves the route; cost is verification — [fixed-defect: none]
- class 1 g39 (7 entries, deterministic, final timeout top=1_2_1_3_r49): VERIFY-TIMEOUT. 1.2.1.3
  `(5-x)sqrt(2+5x+3x^2)/(3+2x)^k`. The defective tree answered 1_2_1_3_r15 (`IGtQ[p,0]` accepting p=1/2) with a noun.
  On the fixed core r15 declines, as Rubi's does. The top 1_2_1_3_r49 (`is(p>0)`, `is(m<-2)`, `not(%mr_iLtQ(m+2p+3,0))`
  on numbers) fired at 30 s and 120 s over 1_1_2_1_r13, 1_2_1_1_r15, 1_2_1_2_r99, 1_2_1_3_r89/r50 (Rubi's 6-step
  atanh route). P0 1_2_1_9_r22 2.5–2.8 s; t100 timeout 7; all arms timeout. — follows from: the IGT translation fix
  (Rubi's reading) + verification cost — [fixed-defect: none]
- class 1 g40 (7 entries, deterministic, final timeout top=1_2_1_3_r89): As on the defective tree (P5 g52, same fires).
  1_2_1_3_r89 (`not(%mr_iGtQ(m,0))`, m=-1) is top at 30 s for e1577/e2265/e2469/e2500 (VERIFY-TIMEOUT). For 1.2.2.4
  e172/e333 and 1.2.4.2 e108, r89 is nested (120 s top 1_2_2_4_r9 for e172). e2265 is EQQ-FAMILY: its elliptic chain
  (1_1_2_3_r48, 1_2_1_2_r93 with `%mr_neQ(c d^2-b d e+a e^2,0)`) is the NeQ-case route. P0 1_2_1_5_r40/r43,
  1_2_1_9_r22, 1_2_2_6_r2, 1_2_2_4_r9, 1_4_1_r34 (3.2–20.1 s). t100 timeout 7; r4 unverified e2265 2.1 s. — follows
  from: faithful Optional binding; cost; e2265 EqQ/NeQ syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g41 (7 entries, deterministic, final unverified top=1_2_1_3_r49): EQQ-FAMILY. 1.2.1.3
  `(f+gx)sqrt(c d^2-b d e-b e^2x-c e^2x^2)/(d+ex)^k`.
  - **Route.** The NeQ-case 1_2_1_3_r49 over 1_4_1_r18. e2236/e2246 run the elliptic chain 1_1_2_3_r48, 1_2_1_2_r93,
    9_1_r8, 1_2_1_9b_r32, 1_4_1_r18.
  - **Answers (7 read).** Wrong: r49's repl divides by the zero-equivalent `c d^2-b d e+a e^2`, and the answers carry
    `asin`/`sqrt` terms not in the corpus.
  - **Defective tree.** e2189/e2203/e2236/e2246 took 1_2_1_3_r15 (IGT p=1/2, deferred); the IGT fix moved them.
    e2177/e2190/e2204 are fix-induced (route not traced).
  - **Arms and P0.** All arms unverified. P0: 1_4_2_r25 → 1_3_3_r6.

  — follows from: EqQ/NeQ syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g42 (6 entries, deterministic, final deferred top=1_4_2_r20): 1_4_2_r20 (`u^q v^p` ExpandToSum normalizer,
  an equal-form rewrite) answers alone (nfires=1) on `P(x)/(a+bx^3)^(k/2)`, `P6/sqrt(a+bx^4)`,
  `(d+ex^2)/(unexpanded quartic)`. The defective tree was the same. P0: 1_3_4_r20/r21, 1_2_2_5_r3 or 1_2_2_3_r27
  chains (2.8–5.0 s). r3 verified e68/e69/e220 (0.5–1.1 s); otherwise deferred. — follows from: condition retry (3) —
  [fixed-defect: undetermined — EQ-REWRITE at 1_4_2_r20 (vs no rule), awaiting probe 16]
- class 1 g43 (6 entries, deterministic, final timeout top=1_1_2_2_r23): VERIFY-TIMEOUT (top fired at 30 s and 120 s).
  - **Integrand.** 1.1.2.2 `x^6/(a+bx^2)^(1/6|5/6)`.
  - **Route.** r23 reduces m → 1_1_2_1_r29/r8/r28/r30 substitutions → 1_1_2_1_r27 → 1_1_3_2_r46 / 1_1_3_1_r31 /
    1_1_3_7_r31 (`%mr_negQ(a)` on the numeric -1, True in both).
  - **Fix-induced.** e1018–e1020 (p5 verified 0.2–0.3 s).
  - **Arms and P0.** e1025–e1027 as P5 g43: r4 (model flags off) verified 0.3–0.4 s. t100 timeout 6. P0: 1_4_2_r6 →
    1_1_2_2_r29.

  — follows from: model flags (e1025–e1027); verification cost (e1018–e1020) — [fixed-defect: none]
- class 1 g44 (6 entries, deterministic, final timeout top=1_1_3_1_r22): MID-CHAIN.
  - **Integrand.** 1.1.1.2 `(a+bx)^(k/6)/(c+dx)^(k/6)`.
  - **Fires.** The 30 s list is 1_1_3_7_r45 (first, no child), 1_2_1_1_r12, 1_2_1_2_r3/r9, 1_1_2_1_r13, and the
    nested 1_1_3_1_r22 (`%mr_iGtQ((n-2)/4,0)` n=6, `%mr_negQ(a/b)` on `(bc-ad)/d`, True in both). The 120 s run
    errors at 57.7–59.1 s with the same list.
  - **Defective tree.** e1773/e1798 1_1_1_2_r12 (IGT); e1774/e1800/e1826 RT-SUM r14; e1799 verified (fix-induced).
  - **Timing and arms.** t100 error 6. r3 verified 5 (0.1–0.2 s), r3 error e1826; r2 error 6; r4 timeout 6.

  - **Candidate.** The first-listed 1_1_3_7_r45's nested fall-through is one candidate for where the time goes.

  — follows from: condition retry (5); e1826 not determined — [fixed-defect: undetermined — no top-level route
  observed (dies at ~60 s); a flushed trace decides it]
- class 1 g45 (6 entries, deterministic, final timeout top=1_2_1_3_r53): EQQ-FAMILY.
  - **Integrand.** 1.2.1.3 `(d+ex)^k(f+gx)/(c d^2-b d e-b e^2x-c e^2x^2)^(j/2)`.
  - **Final route.** The NeQ-case top 1_2_1_3_r53 (`is(p<-1)`, `is(m>1)`) fired at 30 s. For e2223/e2224 its only
    nested fire is 1_2_1_9b_r1 (`mr_int((d+ex)^(m+1)·PolyQuotient…)`, an equal-form rewrite, no child). e2268–e2271
    run the elliptic chain with 9_1_r8, 1_2_1_9b_r32, 1_4_1_r18.
  - **Timing.** 120 s: timeout e2223/e2224/e2268, unverified e2269 86.3 s / e2270 48.5 s / e2271 48.9 s. t100 the same
    split (unverified 42–82 s).
  - **Fix-induced and P0.** e2268–e2270 (p5 verified 10 s); the others as P5 g73. P0: 1_2_1_6_r1/r4 or r53 over
    1_2_1_9b_r5/r1.
  - **Arms.** r4 unverified 4; r2 unverified 2; r3 unverified e2270.

  — follows from: EqQ/NeQ syntactic reading (unlisted) puts the route on r53 — [fixed-defect: undetermined —
  EQ-REWRITE at 1_2_1_9b_r1 (e2223/e2224; vs no rule), awaiting probe 16; the 120 s unverified answers are not recorded]
- class 1 g46 (6 entries, deterministic, final unverified top=1_2_1_2_r119): EQQ-FAMILY, identical on the defective
  tree (P5 g27).
  - **Integrand.** 1.2.1.2 `(a d e+(c d^2+a e^2)x+c d e x^2)^(k/2)/(d+ex)^j`.
  - **Final route.** 1_2_1_2_r119's `%mr_neQ(c d^2-b d e+a e^2, 0)` reads True on the unexpanded zero. That answers
    the defective-tree note "why the cond accepted is not traced". Its repl divides by that zero; the nested
    1_4_1_r18 has no fire under it.
  - **Answers (6 read).** Expanded zero-divisor forms: wrong.
  - **Arms and P0.** All arms unverified. P0: 1_4_2_r25 → 1_3_3_r6.

  — follows from: EqQ/NeQ syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g47 (5 entries, deterministic, final deferred top=1_1_2_8_r68): 1_1_2_8_r68 (`%mr_eqQ(b c^2+a d^2,0)`
  reads the monomial zero, `%mr_iLtQ(n,0)` n=-1, Rubi's reading) rewrites `x^k(d^2-e^2x^2)^p/(d+ex)` to the equal form
  `c^(2n)/a^n·Int[(ex)^m(a+bx^2)^(n+p)/(c-dx)^n]` and answers alone (nfires=1). The defective tree was the same.
  P0: 1_1_2_8_r106. All arms deferred. — follows from: faithful Optional binding (`e_.`) — [fixed-defect: undetermined
  — EQ-REWRITE at 1_1_2_8_r68 (vs no rule), awaiting probe 16]
- class 1 g48 (5 entries, deterministic, final deferred top=1_2_2_3_r86): Both cores put 1_2_2_3_r86 at top
  (`%mr_iLtQ(q,0)`, q=-3 legit). On P0 its 2-arg ExpandIntegrand sum dispatched through 1_4_1_r7 (12.6–13.6 s). On the
  fixed core r86 is alone (nfires=1) and gives a noun at 0.4–0.5 s: the class 2 g1 shape. All arms deferred, as on the
  defective tree. — follows from: not determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at
  1_2_2_3_r86 (vs a `%mr_intSum` fault), awaiting probe 16]
- class 1 g49 (5 entries, deterministic, final deferred top=1_2_2_3_r98): The g48 shape with 1_2_2_3_r98
  (`(a+cx^4)^p/(d+ex^2)^q`, `%mr_iLtQ(q,0)` q=-1…-3). P0 split the expansion with 1_4_1_r7 (5.7–11.5 s); the fixed
  core has r98 alone and a noun at 0.2–0.4 s. All arms deferred, as on the defective tree. — follows from: not
  determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at 1_2_2_3_r98 (vs a `%mr_intSum` fault),
  awaiting probe 16]
- class 1 g50 (5 entries, deterministic, final deferred top=1_3_4_r1): `x^(k+m)/sqrt(a+bx)`. P0 reached expected at
  0.5–0.6 s via 1_1_1_2_r38/r39 on `(0+1·x)^(k+m)` (DEG; Rubi's `c_` is not Optional). The fixed core's 1_3_4_r1
  (substitution into a new variable, not an equal form) answers with a noun, as on the defective tree. All arms
  deferred. — follows from: G-1 (P0 degenerate binding lost); why Rubi's 2-step rule is not reached is not traced —
  [fixed-defect: none]
- class 1 g51 (5 entries, deterministic, final deferred top=1_4_2_r19): 1_4_2_r19 (`(dx)^m u^p` ExpandToSum
  normalizer, an equal-form rewrite) answers the 1.3.1/1.3.2 quartics alone (nfires=1). The defective tree was the
  same. P0: 1_2_2_5_r10 / 1_2_2_2_r21 (2.5–17.3 s). All arms deferred. — follows from: not determined from the traces —
  [fixed-defect: undetermined — EQ-REWRITE at 1_4_2_r19 (vs no rule), awaiting probe 16]
- class 1 g52 (5 entries, deterministic, final timeout top=1_1_1_2_r19): VERIFY-TIMEOUT (top fired at 30 s and 120 s).
  - **Integrand.** 1.1.1.2/1.1.1.3 `(a+bx)^(5/4|7/4)/(c+dx)^(1/4|3/4)`.
  - **Defective tree.** 1_1_1_2_r12 (`IGtQ[m,0]` on m=5/4, a noun); the IGT fix removed it.
  - **Final chain.** r19 → 1_1_1_2_r32 → 1_1_3_1_r52 (e1705/e1706: 1_1_3_2_r74) → `1/(1-bx^4)` (`x^m/(1-bx^4)`).
    Rubi's rule there is 1_1_3_1_r24 `Not[GtQ[a/b,0]]` (1_1_3_2_r40), True on `-1/b`: the atan+atanh corpus answer.
    It does not answer; the hypergeometric 1_1_3_1_r57 / 1_1_3_2_r107 does, and verification exceeds the cap.
  - **Arms.** r3 verified 5/5 (0.1–0.2 s); t100 timeout 5.

  — follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g53 (5 entries, deterministic, final timeout top=1_1_1_2_r20): VERIFY-TIMEOUT (top fired at 30 s and 120 s).
  - **Integrand.** 1.1.1.2 `1/((a+bx)^(k/3)(c+dx)^(j/3))`.
  - **Defective tree.** 1_1_1_2_r11 over 1_1_3_2_r17 (NE: the `!=` misreading accepted k=1).
  - **Final chain.** The NE fix removes the r17 fire; the route is Rubi's elliptic chain: 1_1_1_2_r31 → 1_2_1_1_r17
    → 1_1_3_2_r45 / 1_1_3_7_r29 / 1_1_3_1_r30. Their `%mr_posQ(a)` reads the expanded `(bc-ad)^2` positive, as Rubi.
  - **Arms.** r3 verified e1626/e1627 (0.2 s); t100 timeout 5.

  — follows from: the NE translation fix (Rubi's reading) + verification cost; condition retry (2) — [fixed-defect: none]
- class 1 g54 (5 entries, deterministic, final timeout top=1_1_2_2_r8): VERIFY-TIMEOUT (top fired at 30 s and 120 s).
  1.1.2.2 `(a+bx^2)^(k/3|1/6)/x^j`. The defective tree answered 1_1_2_2_r5 (IGT p=2/3, a noun). The final route is Rubi's
  1_1_2_2_r8/r25 → 1_1_2_1_r27/r28/r30 → 1_1_3_2_r46 / 1_1_3_1_r31 (`%mr_negQ` on numbers). r4 (model flags off)
  verified 5/5 (0.3–0.7 s). t100 timeout 5. — follows from: the IGT translation fix + model flags — [fixed-defect: none]
- class 1 g55 (5 entries, deterministic, final timeout top=1_2_1_2_r105): As P5 g62.
  - **Fires.** 1_1_2_1_r13, 1_2_1_2_r99, (r95), 1_2_1_2_r105 (`d_.`=0 after the x^2/x^3 substitution) are nested at
    30 s.
  - **120 s.** The top-level 1_2_2_2_r8 (e927/e945/e960) or 1_2_3_2_r6 (e193/e211) has fired: VERIFY-TIMEOUT.
  - **Timing and sites.** P0 1_2_2_2_r8 / 1_3_3_r15 (2.3–3.1 s). t100 timeout 5; all arms timeout. No fixed-defect site
    on the route.

  — follows from: faithful Optional binding; verification cost — [fixed-defect: none]
- class 1 g56 (5 entries, deterministic, final timeout top=1_2_2_3_r55): MID-CHAIN (1_2_2_3_r55 is a quartic rule under
  a √-substitution; the top-level rule is absent at 30 s and 120 s).
  - **e641/e642/e650/e651** `sqrt(f+gx)/((d+ex)^2 sqrt(a+cx^2))`: fix-induced (p5 verified 5.1–6.3 s).
    - **Fires.** 1_2_2_1_r16, 1_2_2_3_r53, r55 (+ 1_1_2_7_r60, 1_2_2_7_r26, 1_2_2_3_r74, 1_1_2_9_r92). All are PosQ
      branches on `c/(c d^2+a e^2)`, True in Rubi and on the fixed port. The defective strict sign read them False.
    - **Arms.** r3 verified 4/4 (0.8–1.0 s).
    - — follows from: the NEGQ translation fix (Rubi's branch) + condition retry — [fixed-defect: none]
  - **e1479** `(A+Bx)(a+cx^2)^(3/2)/(d+ex)^(7/2)` (defective tree: 1_1_2_9_r14, IGT noun). Same prefix; timeout in all
    arms including r3. — follows from: not determined from the traces — [fixed-defect: undetermined — no top-level
    route observed]
- class 1 g57 (5 entries, deterministic, final unverified top=1_1_2_2_r25): 1.1.2.2 `1/(x^k(-2-3x^2)^(1/4|3/4))`.
  - **Route.** r25 (`is(m < -1)`) → 1_1_2_1_r22/r26 (`%mr_negQ(-2)`) → 1_1_3_2_r47 / 1_2_2_3_r54 / 1_1_3_1_r32 (PosQ
    on numbers, True in both). This is Rubi's elliptic route.
  - **Answers (5 read).** Unverifiable elliptic_e/elliptic_f forms with nested radicals.
  - **Fix-induced.** e903/e904 (p5 verified 0.2–0.3 s; route not traced).
  - **Arms and P0.** e916–e918 as P5 g115: r4 verified 0.2 s (model flags). P0: 1_4_2_r6/1_1_3_1_r32 chains →
    1_1_2_2_r6.

  — follows from: model flags (e916–e918); not determined which change moves e903/e904 — [fixed-defect: none]
- class 1 g58 (5 entries, deterministic, final unverified top=1_2_1_3_r110): EQQ-FAMILY, fix-induced (p5 verified
  0.9–1.2 s).
  - **Integrand.** 1.2.1.4 `(f+gx)^k(a d e+(c d^2+a e^2)x+c d e x^2)^(j/2)/(d+ex)^(i/2)`.
  - **Route.** The NeQ-case 1_2_1_3_r110 (`%mr_iGtQ(n,1)`, `is(m<-1)`) over 1_4_2_r15.
  - **Answers (5 read).** Wrong: they divide by `(a*d*e^3-d*e*(a*e^2+c*d^2)+c*d^3*e)`, which is identically 0.
  - **Arms and P0.** All arms unverified. P0: 1_2_1_3_r15 over 1_4_1_r7 (9.8–16.4 s).

  — follows from: EqQ/NeQ syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g59 (4 entries, deterministic, final contains-noun top=1_2_1_3_r49): CATCH-1, the g29 shape.
  `(2-5x)x^(k/2)/(2+5x+3x^2)^(j/2)`: 1_2_1_3_r49/r50/r57 → 1_4_1_r34 → 1_2_2_7_r42 → marker. The defective tree
  answered 1_2_1_3_r15 (IGT p=1/2, a noun); the IGT fix moved the route onto Rubi's reduction. P0 1_4_1_r34 (3.3–3.7 s).
  All arms CN. — follows from: the IGT translation fix + faithful Optional binding; why Rubi's quartic rules decline is
  not traced — [fixed-defect: none]
- class 1 g60 (4 entries, deterministic, final deferred top=1_2_2_3_r61): Fix-induced (p5 verified 1.4–1.5 s).
  - **Integrand.** 1.2.2.3 `(d+ex^2)/(d^2+bx^2+e^2x^4)`; `c d^2-a e^2` = 0 reads EqQ True.
  - **Rubi's rule.** 1_2_2_3_r19: `GtQ[2d/e-b/c,0] || Not[LtQ[2d/e-b/c,0]] && EqQ[d-e Rt[a/c,2],0]`; the second
    disjunct is True here, giving the corpus atan with `sqrt(2de-b)`. The port's
    `is(…>0) or not(is(… < 0)) and …` does not answer. r22 (`not(is(b^2-4ac > 0))`, a ticket-02 site too) does not
    answer either, and the ExpandIntegrand rule 1_2_2_3_r61 answers alone with a noun.
  - **Arms and P0.** All arms deferred. P0: 1_4_1_r25, 1_4_1_r18, 1_2_1_1_r12, 1_2_1_2_r3/r9, 1_2_2_3_r27 (2.4–2.6 s).

  - **Head.** The site is the `LtQ` head of the same reading.

  — follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g61 (4 entries, deterministic, final error top=-): No fire on any leg. The entries do not share a cause:
  - **1.1.1.2 e1572, e1757** `1/((a+bx)^(1/2)(c+dx)^(2/3))`: fix-induced (p5 verified 0.3–0.4 s).
    - **Error.** `err=fatal error … Control stack exhausted while pseudo-atomic` at 2.6–2.7 s (final120 2.4 s).
    - **Record.** Timeout 30.0 s; t100 timeout 100 s.
    - **Arms.** r3 verified 0.1–0.2 s; r2/r4 timeout.
    - **Reading.** An unbounded recursion before any rule completes, only with condition retry on, and new since the
      defective tree. The recursive fixed ports (`%mr_posAux`, `%mr_intPart_aux`, `%mr_product_factors`) are
      candidates.
    - — follows from: condition retry (the switch) — [fixed-defect: undetermined — which recursion exhausts the
      stack; a backtrace at the death decides whether a fixed port (NEGQ or sibling) recurses]
  - **1.3.1 e193, e194** `(b+2cx+3dx^2)(bx+cx^2+dx^3)^7`, `x^7(…)^7(…)`: as P5 g143.
    - **Error.** `err=Heap exhausted during garbage collection … 64 requested` at 16.6–16.8 s.
    - **Arms and P0.** r3 verified 0.4/1.5 s; r2/r4 error. P0 1_4_1_r20 / 1_2_1_6_r1.
    - — follows from: condition retry — [fixed-defect: none]

  — follows from: condition retry (r3 verifies all 4) — [fixed-defect: undetermined — the control-stack exhaustion of
  e1572/e1757 (a backtrace decides whether a fixed port recurses)]
- class 1 g62 (4 entries, deterministic, final timeout top=1_1_3_1_r53): MID-CHAIN.
  - **Integrand.** 1.2.1.2 `(a+bx+cx^2)^(4/3)/(bd+2cdx)^(2/3)`.
  - **Fires.** 30 s: nested 1_1_3_1_r37, 1_1_3_1_r53 (`%mr_iGtQ(n,0)`, `-1<p<0`). 120 s: still nested 1.1.2.2
    reductions (1_1_2_2_r9/r8/r25) under an unfired `EqQ[2cd-be,0]` substitution.
  - **Defective tree.** 1_2_1_2_r58 (IGT p=4/3, a noun); the IGT fix removed it.
  - **Timing.** P0 1_4_2_r5/r6 → 1_3_4_r1 (2.8–3.0 s). t100 timeout 4; all arms timeout.

  — follows from: the IGT translation fix (Rubi's reading); the rest not determined — [fixed-defect: undetermined — no
  top-level route observed at 120 s]
- class 1 g63 (4 entries, deterministic, final timeout top=1_2_1_1_r6): Fix-induced (p5 verified 0.3–0.6 s).
  1.2.2.2 `x sqrt(a+bx^2+cx^4)`, 1.2.3.2 `x^2 sqrt(a+bx^3+cx^6)`. At 30 s the nested 1_1_2_1_r13, 1_2_1_1_r15,
  1_2_1_1_r6 (`is(p>0)` p=1/2) have fired. At 120 s the top-level 1_2_2_2_r1 / 1_2_3_2_r1 has fired: VERIFY-TIMEOUT,
  Rubi's atanh route. P0 1_2_2_2_r1 / 1_3_3_r15 (0.8–2.7 s). t100 timeout 4; all arms timeout. — follows from: not
  determined which change moves the route (not traced); cost is verification — [fixed-defect: none]
- class 1 g64 (4 entries, deterministic, final timeout top=1_2_1_2_r95): As P5 g84. `sqrt(a+bx^k+cx^2k)/x^i`: the
  nested 1_1_2_1_r13, 1_2_1_2_r99, r95 (`d_.`=0) at 30 s. At 120 s the top-level 1_2_2_2_r8 / 1_2_3_2_r6 has fired
  (VERIFY-TIMEOUT). P0 2.3–3.2 s. t100 timeout 4; all arms timeout. No fixed-defect site. — follows from: faithful
  Optional binding; cost — [fixed-defect: none]
- class 1 g65 (4 entries, deterministic, final timeout top=1_2_3_2_r6): As P5 g88. `x^5/(a+bx^3+cx^6)`-type: the
  top-level x^n substitution 1_2_3_2_r6 fired at 30 s over 1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_2_r3/r9 (+1_1_1_1_r1,
  1_2_1_2_r80): the corpus log+atanh shape. 1_2_1_2_r3's `%mr_removeContent` (a sibling port) only sets the log's
  constant content. final120 error 55–61 s; t100 error 4; all arms timeout (r4 error e316). — follows from: faithful
  binding; verification cost — [fixed-defect: none]
- class 1 g66 (4 entries, deterministic, final timeout top=1_4_1_r34): VERIFY-TIMEOUT (top 1_4_1_r34 fired at 30 s and
  120 s). 1.2.1.3 `(ex)^(7/2)(A+Bx)sqrt(a+cx^2)`, via the long chain 1_1_3_1_r32 … 9_1_r12 (exact seen), 1_1_3_7_r40.
  The defective tree answered 1_1_2_8_r7 (IGT p=1/2, a noun). r3 verified 4/4 (0.7–0.8 s). t100 timeout 4. — follows
  from: the IGT translation fix + condition retry (cost) — [fixed-defect: none]
- class 1 g67 (4 entries, deterministic, final unverified top=1_1_2_8_r48): 1.2.1.4 `x^k/((d+ex)sqrt(d^2-e^2x^2))`.
  The entries split:
  - **e122, e152** (fix-induced, p5 verified 0.8–1.2 s). Route 9_1_r8, 1_1_3_7_r37, 1_1_2_8_r48
    (`%mr_iGtQ(m,0)`, `%mr_iLtQ(n,0)` on integers).
    - **Answers.** `sqrt(d^2-e^2x^2)/(e^2(ex+d))`: the corpus `atan(ex/sqrt(…))` term is missing, so wrong.
    - **Mechanism (inferred from the fires and rule text).** r48's `mr_int(1/sqrt(a+bx^2)·%mr_expandToSum(<rational
      equal to a constant>))` goes to 1_1_3_7_r37. Its `%mr_polyQ` accepts the uncancelled quotient while its
      `%mr_coeff` split returns 0, so 9_1_r8 integrates 0.
    - **Arms.** r3 unverified.
    - — [fixed-defect: none]
  - **e121, e151** (as P5 g167). The same missing term via 1_1_2_2_r2, 1_1_3_2_r115; r3 verified 0.4 s. — follows
    from: condition retry — [fixed-defect: none]

  — follows from: an unlisted `%mr_polyQ`/`%mr_coeff` gap on an uncancelled constant (inferred); condition retry (2) —
  [fixed-defect: none]
- class 1 g68 (4 entries, deterministic, final unverified top=1_1_2_8_r49): As on the defective tree (P5 g90).
  - **Integrand.** 1.2.1.4 `1/(x^k(d+ex)sqrt(d^2-e^2x^2))`.
  - **Route.** 9_1_r8 + 1_1_3_8_r18 (e124/e154) or 1_1_2_11_r2 (e126/e156) under 1_1_2_8_r49.
  - **Answers (4 read).** `sqrt(d^2-e^2x^2)/(d^2(ex+d))` etc.; the corpus `atanh(sqrt(…)/d)` term is missing, the
    g67 loss (inferred).
  - **Arms and sites.** All arms unverified. The IGT sites read integers.

  — follows from: the unlisted `%mr_polyQ`/`%mr_coeff` gap (inferred) — [fixed-defect: none]
- class 1 g69 (4 entries, deterministic, final unverified top=1_2_1_3_r50): EQQ-FAMILY.
  - **Route.** 1_4_2_r15 (normalizer), 1_2_1_9b_r27 (NeQ-case, `%mr_neQ(c d^2-b d e+a e^2,0)`), top 1_2_1_3_r50.
  - **Answers (4 read).** Wrong: they carry the zero-equivalent `(b*d*e^3-c*d^2*e^2+e^2*(c…` divisor.
  - **Defective tree.** e2245/e2256 took 1_2_1_3_r15 (IGT p=3/2, 5/2; a noun). e2255/e703 are fix-induced.
  - **Arms and P0.** All arms unverified. P0: 1_3_3_r6 (1.7–5.0 s).

  — follows from: EqQ/NeQ syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g70 (3 entries, deterministic, final contains-noun top=1_1_1_2_r19): 1.1.1.2 `(a+bx)^(5/2)/(c+dx)^(1/4)`. The
  defective tree answered 1_1_1_2_r12 (IGT m=5/2, a noun); the fix removed it. The final chain is g28's: 1_1_1_2_r32 →
  1_1_3_2_r49 → 1_2_2_3_r100, where Rubi's 1_2_2_3_r58 `Not[GtQ[A,0]]` does not answer. r3 verified 3/3 (0.2 s).
  — follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g71 (3 entries, deterministic, final contains-noun top=1_1_2_8_r20): As P5 g93. `(A+Bx)(a+cx^2)^k/x`:
  r20 (`is(p > 0)`, integer 2p) → 1_1_2_8_r123 (catch-all) → marker. The corpus answers are 2 steps with no
  Unintegrable. All arms CN. — follows from: faithful binding (NOUN); why r20's reduced integral reaches the catch-all is
  not traced — [fixed-defect: none]
- class 1 g72 (3 entries, deterministic, final contains-noun top=1_2_1_3_r50): The g59 shape (CATCH-1 via 1_4_1_r34 →
  1_2_2_7_r42). The defective tree answered 1_2_1_3_r15 (IGT); the fix moved the route. All arms CN. — follows from:
  the IGT translation fix + faithful Optional binding — [fixed-defect: none]
- class 1 g73 (3 entries, deterministic, final deferred top=1_1_1_3_r17): 1_1_1_3_r17 (`IntegersQ[m,n] &&
  (IntegerQ[p] || GtQ[m,0] && GeQ[n,-1])`, which holds on the numbers here) answers `x^2(a+bx)^n/(c+dx)`,
  `(2+3x)^m(3+5x)^k/(1-2x)` alone (nfires=1). The defective tree was the same. r3 expected e925/e3182 (0.1–0.3 s).
  — follows from: condition retry (2) — [fixed-defect: undetermined — EQ-REWRITE at 1_1_1_3_r17 (vs a `%mr_intSum`
  fault), awaiting probe 16]
- class 1 g74 (3 entries, deterministic, final deferred top=1_1_2_8_r107): Both cores put r107 at top (`%mr_iLtQ(n,-1)`,
  n=-2,-3). The P0 expansion sum dispatched via 1_4_1_r7 (11.9–14.3 s); the fixed core has nfires=1 and a noun. All arms
  deferred, as on the defective tree. — follows from: not determined from the traces — [fixed-defect: undetermined —
  EQ-REWRITE at 1_1_2_8_r107 (vs a `%mr_intSum` fault), awaiting probe 16]
- class 1 g75 (3 entries, deterministic, final deferred top=1_1_4_4_r11): 1.3.2 `(-1+x^3)/(-4x+x^4)^(2/3)`-type
  (1-step derivative-divides in the corpus). P0's 1_1_4_4_r2 declines (`%mr_polyPowerQ(Pq,x,n)` fails with the
  Optional m=0). The ExpandIntegrand rule 1_1_4_4_r11 answers alone (nfires=1). The defective tree was the same. All
  arms deferred. — follows from: not determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at
  1_1_4_4_r11 (vs a `%mr_intSum` fault), awaiting probe 16]
- class 1 g76 (3 entries, deterministic, final deferred top=1_2_1_3_r15): Both cores put 1_2_1_3_r15 at top. The
  1.2.1.4 integrands `(f+gx)^n(a+2cdx+cex^2)/(d+ex)^j` have p=1, where `%mr_iGtQ(p,0)` is Rubi's reading. On P0 the
  expansion sum dispatched (1_4_1_r7 and term rules, 6.8–14.2 s); on the fixed core r15 is alone (nfires=1, 0.7–0.8 s).
  All arms deferred, as on the defective tree.
  - **e809, e922.** P0 terms: 1_1_1_4_r40, 9_1_r9, 1_1_1_7_r27 (e809).
  - **e810 (separate line below).**

  — follows from: not determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at 1_2_1_3_r15 (vs a
  `%mr_intSum` fault), awaiting probe 16]
- class 1 g76 e810 (1 entry, deterministic, final deferred top=1_2_1_3_r15): 1.2.1.4 `(f+gx)^n(a+2cdx+cex^2)/(d+ex)^2`.
  - **P0.** 1_1_1_4_r40, 9_1_r9, 1_1_1_7_r27, 9_1_r28 (P0's double-root trinomial collapse id; generated 9_1_r27),
    1_4_1_r7, top 1_2_1_3_r15: verified 14.2 s. The 9.1 fires sit inside the dispatched expansion sum.
  - **Fixed core.** Fires only 1_2_1_3_r15 (p=1, Rubi's conditions hold) and answers deferred at 0.7 s. The expansion
    sum never reaches 1_4_1_r7.
  - **Collapse cleared on the visible route.** No 9.1 rule fires, so the 9.1 `mr_int_exact` fix is not on it. The
    divergence is r15's own nested `mr_int`, a `mr_int` (ratsimp seen test) call.
  - **Arms.** All deferred, as on the defective tree.

  — follows from: not determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at 1_2_1_3_r15 (vs a
  `%mr_intSum` fault), awaiting probe 16]
- class 1 g77 (3 entries, deterministic, final deferred top=1_2_2_1_r19): 1.3.2 `(4ac+4c^2x^2+4cdx^3+d^2x^4)^(k/2)`.
  Top 1_2_2_1_r19 (depressed-quartic substitution); its nested integral fires only 1_4_2_r18 (ExpandToSum normalizer,
  an equal-form rewrite, no child), then a noun. The defective tree was the same. r4 (model flags off) verified e617 0.5 s
  and e620 7.9 s; e618 r4 timeout. — follows from: model flags (2) — [fixed-defect: undetermined — EQ-REWRITE at
  1_4_2_r18 (vs a model-flag shape no rule binds), awaiting probe 16]
- class 1 g78 (3 entries, deterministic, final deferred top=1_2_3_4_r100): 1_2_3_4_r100 (`%mr_iGtQ(q,0)`, q=3,2,1:
  Rubi's reading) expands `(fx)^m(d+ex^n)^k(a+cx^2n)^p` alone (nfires=1). The defective tree was the same. P0: the manual
  9.1 `u*(a*x^n)^m`. All arms deferred. — follows from: 9.1 regeneration — [fixed-defect: undetermined — EQ-REWRITE at
  1_2_3_4_r100 (vs a `%mr_intSum` fault), awaiting probe 16]
- class 1 g79 (3 entries, deterministic, final deferred top=1_2_3_4_r99): As g78 with 1_2_3_4_r99 (q=1,2,1). — follows
  from: 9.1 regeneration — [fixed-defect: undetermined — EQ-REWRITE at 1_2_3_4_r99 (vs a `%mr_intSum` fault), awaiting
  probe 16]
- class 1 g80 (3 entries, deterministic, final error top=1_2_2_2_r1): As P5 g78, the g33 shape. 1.2.3.2
  `(d+ex)/(a+b(d+ex)^2+c(d+ex)^4)^j`: only the nested 1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_1_r8, 1_2_2_2_r1, then `err=Heap
  exhausted during garbage collection … game over` (13.3–25.7 s). P0 1_3_3_r4 (2.0–2.1 s). Error in all arms. —
  follows from: not determined from the traces — [fixed-defect: undetermined — where the heap is exhausted (no
  top-level fire; the same death on the defective tree)]
- class 1 g81 (3 entries, deterministic, final timeout top=1_1_1_2_r32): VERIFY-TIMEOUT (top fired at 30 s and 120 s).
  - **Integrand.** 1.1.1.2/1.1.1.3 `1/((a+bx)^(3/4)(c+dx)^(1/4))`-type.
  - **Final chain.** 1_1_1_2_r32 → 1_1_3_1_r52 → the hypergeometric 1_1_3_1_r57 (e1707: 1_1_3_2_r74 →
    1_1_3_2_r107). As in g52, Rubi's `Not[GtQ[a/b,0]]` rule on `1/(1-bx^4)` / `x^m/(1-bx^4)` (1_1_3_1_r24 /
    1_1_3_2_r40) does not answer. The corpus has atan+atanh.
  - **Defective tree.** e1695/e891 RT-SUM 1_1_3_1_r14; e1707 verified (fix-induced).
  - **Arms.** t100 timeout 3; all arms timeout.

  — follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g82 (3 entries, deterministic, final timeout top=1_1_1_3_r29): VERIFY-TIMEOUT (top fired at 30 s and 120 s).
  1.1.1.3 `x^k/((1-x)^(1/3)(2-x)^(1/3))`, `x^3(a+bx)^(1/4)/(c+dx)^(1/4)`. The defective tree's e863/e864 fired
  1_1_3_2_r17 (NE identity, unverified); the NE fix removes it. The route is Rubi's elliptic chain (1_1_3_1_r30,
  1_1_3_7_r29, 1_1_3_2_r45, `%mr_posQ(a)` on numbers). e871 is fix-induced (p5 verified 2.4 s; chain 1_1_3_1_r57/r52,
  9_1_r8, 1_1_1_7_r27). r3 verified e871 0.3 s. t100 timeout 3. — follows from: the NE translation fix (Rubi's
  reading) + verification cost — [fixed-defect: none]
- class 1 g83 (3 entries, deterministic, final timeout top=1_1_3_2_r38): MID-CHAIN, the g44 prefix (1_1_3_7_r45 first,
  1_2_1_1_r12, 1_2_1_2_r3/r9, 1_1_2_1_r13) with the nested 1_1_3_2_r38 (`%mr_iGtQ((n-2)/4,0)` n=6,
  `%mr_negQ(a/b)` True in both). 1.1.1.2 `(a+bx)^(5/6)/(c+dx)^(5/6)`. final120 error 59.5–59.9 s; t100 error 3.
  Fix-induced e1781/e1807 (p5 verified 1.3–2.0 s). r3 verified e1780/e1781 (0.2 s); e1807 errors in all arms. —
  follows from: condition retry (2); e1807 not determined; the first-listed 1_1_3_7_r45's fall-through is one
  candidate — [fixed-defect: undetermined — no top-level route observed (death at ~60 s)]
- class 1 g84 (3 entries, deterministic, final timeout top=1_2_1_2_r119): VERIFY-TIMEOUT (top fired at 30 s and 120 s),
  as P5 g82.
  - **e2353, e2354** `(a+bx+cx^2)^(3/2)/(d+ex)^(7|8)`. The only nested fire is 1_4_1_r18 (first, no child). r3
    verified e2353 4.8 s. — [fixed-defect: undetermined — EQ-REWRITE at 1_4_1_r18 (vs no rule), awaiting probe 16]
  - **e2466** `1/((d+ex)^(3/2)sqrt(quad))`. The elliptic chain 1_1_2_3_r48, 1_2_1_2_r93, 9_1_r8, 1_2_1_9b_r32,
    1_4_1_r10. — [fixed-defect: none]

  — follows from: condition retry (e2353); verification cost — [fixed-defect: undetermined — EQ-REWRITE at 1_4_1_r18,
  awaiting probe 16]
- class 1 g85 (3 entries, deterministic, final timeout top=1_2_1_3_r90): VERIFY-TIMEOUT. 1.2.1.4
  `(a d e+(c d^2+a e^2)x+c d e x^2)^(k/2)/(x(d+ex))`. Both cores put r90 (`%mr_fractionQ(p) and is(p>0)`) at top, and
  P0 verified through the same top.
  - **e441, e450.** The atanh chain 1_1_2_1_r13, 1_2_1_2_r99, 1_2_1_1_r15, 1_2_1_3_r1 (+r89, 1_2_1_2_r109,
    1_2_1_1_r6), as P5 g153. — [fixed-defect: none]
  - **e461.** Fix-induced (p5 verified 4.5 s). The first fire is 1_4_1_r18 (no child). — [fixed-defect: undetermined —
    EQ-REWRITE at 1_4_1_r18, awaiting probe 16]
  - **Arms.** r3 CN e450 4.5 s, e461 15.0 s; t100 timeout 3.

  — follows from: verification cost — [fixed-defect: undetermined — EQ-REWRITE at 1_4_1_r18 (e461), awaiting probe 16]
- class 1 g86 (3 entries, deterministic, final timeout top=1_2_2_2_r23): MID-CHAIN, as P5 g37. 1.2.1.2
  `sqrt(d+ex)/(a+cx^2)`: the nested 1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_2_r3/r9, 1_2_2_2_r23 at 30 s and 120 s. r23's
  `%mr_negQ(b^2-4ac)` reads `-4ace^2` negative, as Rubi. The top-level √-substitution never completes. P0
  1_1_2_7_r33 (1.6–1.7 s). t100 timeout 3; all arms timeout. — follows from: not determined from the traces —
  [fixed-defect: undetermined — no top-level route observed at 120 s]
- class 1 g87 (3 entries, deterministic, final timeout top=1_2_2_2_r33): MID-CHAIN. `(A+Bx)sqrt(d+ex)sqrt(a+cx^2)`-type:
  the nested 1_2_2_1_r16, 1_2_2_3_r53, 1_2_2_2_r33 (PosQ[c/a] branches, True in Rubi) at 30 s and 120 s. The defective
  tree answered 1_1_2_9_r14 (IGT p=1/2, a noun); the IGT and NEGQ fixes put the route on Rubi's branches. P0 1_1_2_9_r49/
  r44 chains (6.5–6.8 s). t100 timeout 3; all arms timeout. — follows from: the IGT/NEGQ translation fixes (Rubi's
  reading); the rest not determined — [fixed-defect: undetermined — no top-level route observed at 120 s]
- class 1 g88 (3 entries, deterministic, final timeout top=1_2_2_3_r27): MID-CHAIN, as P5 g7.
  - **Fires.** 1_1_2_1_r13 or 1_4_1_r18 (e1464), 1_2_1_1_r12, 1_2_1_2_r3/r9, 1_2_2_3_r27 at 30 s and 120 s.
  - **NegQ.** Here r27's `%mr_negQ(b^2-4ac)` reads the substituted discriminant `-4ac/e^2` (e623) or `-4e^2`
    (e1464/e1466) negative, as Rubi. The P5 NEGQ tag does not carry over to these 3.
  - **Timing.** P0 3.2–3.3 s; t100 timeout 3; all arms timeout.

  — follows from: not determined from the traces — [fixed-defect: undetermined — no top-level route observed at 120 s]
- class 1 g89 (3 entries, deterministic, final timeout top=1_4_1_r23): MID-CHAIN. `(a+bx^2)^(1/3)/(cx)^(2/3)`: the
  nested 1_1_3_1_r37, 1_1_3_1_r53 (+r7), 1_4_1_r23 at 30 s and 120 s; P0's top-level 1_4_1_r34 never fires.
  Fix-induced e748/e764 (p5 verified 0.6 s). r3 verified 3/3 (0.2 s). — follows from: condition retry — [fixed-defect: none]
- class 1 g90 (3 entries, deterministic, final unverified top=1_1_1_3_r57): As P5 g114.
  - **Integrands.** `(a+bx)^(1+n)/(x^2(a-bx)^n)`, `(a+bx)^(1∓n)(c+dx)^(1±n)/(bc+ad+2bdx)^2`.
  - **Route.** 1_1_1_3_r57 (`%mr_iGtQ(m+n,0)`, m+n integer) over 1_1_1_2_r39 and 1_1_1_3_r60/r25. The first fire is
    1_1_1_4_r46 (`%mr_expandToSum` linear normalizer, an equal form, no child).
  - **Answers.** e3126/e3130 hold `'integrate((d*x+c)^n/((b*d*x)/(a*d-b*c)+(a*d)/(a*d-b*c))^n,x)`: the normalized
    rewrite handed to Maxima integrate (unverifiable). e995 is hypergeometric (cut).
  - **Sibling site.** r39's IntPart/FracPart act on symbolic n, as Rubi.
  - **Arms.** All unverified.

  — follows from: faithful binding — [fixed-defect: undetermined — EQ-REWRITE at 1_1_1_4_r46 (vs no rule), awaiting
  probe 16]
- class 1 g91 (3 entries, deterministic, final unverified top=1_1_2_7_r13): 1.2.1.2 `sqrt(a^2-b^2x^2)/(a+bx)^2`,
  `(…)^(3/2)/(a+bx)^3`, `sqrt(1-x^2)/(1-x)^…`.
  - **e782, e824** (fix-induced, p5 verified 0.5–0.7 s).
    - **Route.** 9_1_r8, 1_1_3_7_r37, 1_1_2_7_r13 (`%mr_iLtQ(n,0)` n=-2, `%mr_eqQ(n+p,-3/2)`).
    - **Answers.** `-2 sqrt(a^2-b^2x^2)/(b(bx+a))`: only r13's first term; the corpus `atan` term is lost. This is
      g67's inferred `%mr_polyQ`/`%mr_coeff` loss.
    - **Arms.** r3 unverified.
    - — [fixed-defect: none]
  - **e793** (as P5 g250). 1_1_2_2_r2, 1_1_3_2_r115; the same missing atan term; r3 verified 0.3 s. — follows from:
    condition retry — [fixed-defect: none]

  — follows from: the unlisted `%mr_polyQ`/`%mr_coeff` gap (inferred); condition retry (e793) — [fixed-defect: none]
- class 1 g92 (3 entries, deterministic, final unverified top=1_1_2_7_r15): The g91 shape with 1_1_2_7_r13 nested under
  r15 (`is(p>0)`, `is(n<-2)`). e794/e810 are fix-induced (p5 verified 0.7–0.8 s; 9_1_r8, 1_1_3_7_r37 route; the answers
  lack the corpus atan term; r3 unverified). e809 is as P5 g251 (r3 verified 0.3 s). — follows from: the unlisted
  `%mr_polyQ`/`%mr_coeff` gap (inferred); condition retry (e809) — [fixed-defect: none]
- class 1 g93 (3 entries, deterministic, final unverified top=1_1_3_2_r67): The entries do not share a mechanism:
  - **1.1.3.2 e1326** `1/(x^2(a+bx^6))`: fix-induced (p5 verified 0.1 s; defective tree RT-SUM).
    - **Route.** r67 (`%mr_iGtQ(n,0)`, `is(m<-1)`) → 1_1_3_2_r37 (the PosQ n≡2 mod 4 rule, Rubi's reading) and its
      atan chain. The first fire is 1_1_3_7_r45 (ExpandIntegrand, no child).
    - **Answer.** `%i*(1/b)^(5/6)*log((x^3+(%i/2+…))…)`: Maxima-integrate complex logs, unverifiable.
    - **Arms.** r3 unverified 7.0 s, r4 2.9 s.
    - — follows from: the IGT/NEGQ translation fixes (Rubi's route) — [fixed-defect: undetermined — EQ-REWRITE at
      1_1_3_7_r45 (vs no rule), awaiting probe 16]
  - **1.2.2.2 e1027** (fix-induced, p5 verified 0.1 s), **e1029** (as P5 g255). ZERO `1/(x^2 sqrt(2+2a-2(1+a)+cx^4))`:
    1_1_3_2_r107/r108 or 1_1_3_1_r57/r36 → r67. The answers divide by `(2*(a+1)-2*a-2)`: wrong. — follows from:
    EqQ/NeQ syntactic reading (ZERO) — [fixed-defect: none]

  — follows from: see the sub-bullets — [fixed-defect: undetermined — EQ-REWRITE at 1_1_3_7_r45 (e1326; vs no rule),
  awaiting probe 16]
- class 1 g94 (3 entries, deterministic, final unverified top=1_2_1_2_r105): EQQ-FAMILY, identical on the defective tree
  (P5 g116). 1.2.1.2 `(a d e+…)^(k/2)/(d+ex)^(k+3)`: the NeQ-case 1_2_1_2_r105 over 1_1_2_1_r13, 1_1_1_4_r46,
  1_2_1_2_r133/r95. The answers (3 read) divide by `(a*d*e^3-d*e*(a*e^2+c*d^2)+c*d^3*e)`, which is identically 0: wrong.
  All arms unverified. — follows from: EqQ/NeQ syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g95 (3 entries, deterministic, final unverified top=1_2_1_2_r95): As g94 with top 1_2_1_2_r95 (P5 g119); the
  answers carry the same zero divisor. — follows from: EqQ/NeQ syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g96 (3 entries, deterministic, final unverified top=1_2_1_3_r48): EQQ-FAMILY, fix-induced (p5 verified
  0.8–0.9 s). 1.2.1.3 `(f+gx)sqrt(c d^2-b d e-b e^2x-c e^2x^2)/(d+ex)^k`: 1_2_1_3_r48 over the g94 chain. The answers
  (3 read) divide by `(b*d*e^3-c*d^2*e^2+e^2*(c*d^2-b*d*e))` = 0: wrong. All arms unverified. — follows from: EqQ/NeQ
  syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g97 (2 entries, deterministic, final contains-noun top=1_1_1_3_r27): As P5 g121. `(c+dx)^3/(x(a+bx)^k)`:
  r27's nested integral binds 1_1_1_4_r42 (catch-all) → marker. r3 verified 0.2/0.5 s. — follows from: condition retry —
  [fixed-defect: none]
- class 1 g98 (2 entries, deterministic, final contains-noun top=1_1_1_3_r29): As P5 g122. r29 → 1_1_1_4_r42
  (+1_1_1_4_r12) → marker. r3 verified 1.6–2.4 s. — follows from: condition retry — [fixed-defect: none]
- class 1 g99 (2 entries, deterministic, final contains-noun top=1_1_2_4_r20): As P5 g123. `(c+dx^2)^3/(x(a+bx^2)^k)`:
  x^2 substitution → 1_1_1_3_r13/r27 → 1_1_1_4_r42 → marker. r3 verified e285 0.3 s; e224 CN in all arms. — follows
  from: condition retry (e285); e224 not determined (why 1.1.1.3 declines is not traced, route unchanged since P5) —
  [fixed-defect: none]
- class 1 g100 (2 entries, deterministic, final contains-noun top=1_1_2_7_r47): As P5 g124. `(d+ex)^3(a+cx^2)^p`: r47
  binds and its reduction reaches 1_1_2_9_r107 (catch-all) → marker. All arms CN. — follows from: faithful binding;
  why the reduction reaches the catch-all is not traced — [fixed-defect: none]
- class 1 g101 (2 entries, deterministic, final contains-noun top=1_1_3_2_r32): Fix-induced (p5 verified 0.2 s).
  - **Integrand.** 1.1.3.2 `x^k/(2+3x^4)^2`.
  - **Route.** r32 → 1_1_3_2_r39 (`is(a/b > 0)`, 2/3) → 1_2_2_3_r20/r23 (PosQ/NegQ[d e] on `±sqrt(6)`, as Rubi). Their
    radical-coefficient quadratic sub-integrals bind 1_2_3_5_r12 (ExpandIntegrand) and the catch-all 1_2_3_5_r24 →
    marker.
  - **Defective tree.** The RT-SUM IGT rules (1_1_3_2_r35/r36 `IGtQ[(n-1)/2,0]`) accepted n=4; the IGT fix removed
    them.
  - **Arms.** r3 verified 2.6–2.8 s, so the 1.2.3.5 bindings are retried ones.

  — follows from: the IGT translation fix + condition retry — [fixed-defect: none]
- class 1 g102 (2 entries, deterministic, final contains-noun top=1_1_3_2_r49): The entries do not share a mechanism:
  - **1.1.3.2 e846** `x^2/sqrt(a-bx^4)`. The defective tree answered 1_1_3_2_r17 (NE identity, deferred); the NE fix
    removes it. Rubi's r49 → `(1+qx^2)/sqrt(a-bx^4)` then needs 1_2_2_3_r58 `Not[GtQ[a,0]]`, which does not answer →
    1_2_2_3_r100 → marker. — follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
  - **1.2.2.2 e1032** `x^2/sqrt(a+(2+2c-2(1+c))x^4)` (fix-induced, p5 verified 0.1 s). ZERO: the corpus answer
    `x^3/(3sqrt(a))` treats the coefficient as 0, while the port binds it as b and runs the e846 route. — follows from:
    EqQ/NeQ syntactic reading (ZERO) — [fixed-defect: none]

  All arms CN.
- class 1 g103 (2 entries, deterministic, final contains-noun top=1_1_3_2_r63): The g101 shape. 1.1.3.2 `x^(6|4)/(2+3x^4)`:
  r63 → r39 → 1_2_2_3_r20/r23 → 1_2_3_5_r12/r24 (+1_1_3_1_r23). Fix-induced (p5 verified 0.1 s). r3 verified
  2.8–2.9 s. — follows from: the IGT translation fix + condition retry — [fixed-defect: none]
- class 1 g104 (2 entries, deterministic, final contains-noun top=1_1_3_2_r67): Both entries are fix-induced (p5
  verified 0.1 s):
  - **1.1.3.2 e696** `1/(x^2(2+3x^4))`: the g101 route under r67; r3 verified 2.7 s. — follows from: condition retry —
    [fixed-defect: none]
  - **1.2.2.2 e1036** `1/(x^2 sqrt(a+(2+2c-2(1+c))x^4))`: ZERO; r67 → 1_1_3_2_r49 → 1_2_2_3_r100; CN in all arms. —
    follows from: EqQ/NeQ syntactic reading (ZERO) — [fixed-defect: none]
- class 1 g105 (2 entries, deterministic, final contains-noun top=1_2_1_2_r117): As P5 g125. EQQ-FAMILY
  `(d+ex)^3(a d e+(c d^2+a e^2)x+c d e x^2)^p`: the NeQ-case r117 (`%mr_neQ(c d^2-b d e+a e^2,0)` True on the zero) →
  1_2_1_3_r112 (catch-all) → marker. The corpus answers are 3-step hypergeometric. All arms CN. — follows from: EqQ/NeQ
  syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g106 (2 entries, deterministic, final contains-noun top=1_2_1_3_r106): EQQ-FAMILY, fix-induced (p5 verified
  4.0–6.4 s). 1.2.1.4 `(a d e+…)^(3/2)/((d+ex)^(3/2)(f+gx))`: Rubi's `EqQ[m+p,0]` rules (`1_2_1_3_r67–r73`) read EqQ
  False. The NeQ-case r106 → the elliptic chain → 1_1_1_4_r29 → 1_1_2_5_r39 (catch-all) → marker. All arms CN. — follows
  from: EqQ/NeQ syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g107 (2 entries, deterministic, final contains-noun top=1_2_1_3_r51): The g59 shape (1_4_1_r34 →
  1_2_2_7_r42). The defective tree answered 1_2_1_3_r15 (IGT). — follows from: the IGT translation fix + faithful
  Optional binding — [fixed-defect: none]
- class 1 g108 (2 entries, deterministic, final contains-noun top=1_2_1_3_r54): As P5 g94 (CATCH-1 via 1_4_1_r34 →
  1_2_2_7_r42). All arms CN. — follows from: faithful Optional binding — [fixed-defect: none]
- class 1 g109 (2 entries, deterministic, final contains-noun top=1_2_1_3_r55): As P5 g126 (CATCH-1; +1_2_1_3_r57). All
  arms CN. — follows from: faithful Optional binding — [fixed-defect: none]
- class 1 g110 (2 entries, deterministic, final contains-noun top=1_2_1_3_r95): EQQ-FAMILY. 1.2.1.4
  `sqrt(a d e+…)/((f+gx)^(5/2)sqrt(d+ex))` (1 step in the corpus): the NeQ-case r95 → 1_4_1_r18, 9_1_r8, 1_2_1_8_r3
  (+1_2_1_3_r105) → 1_2_1_3_r112 (catch-all). e739 is fix-induced (p5 verified 18.8 s; r3 verified 1.6 s). e738
  timed out on the defective tree. — follows from: EqQ/NeQ syntactic reading (unlisted); condition retry (e739) —
  [fixed-defect: none]
- class 1 g111 (2 entries, deterministic, final contains-noun top=1_2_2_2_r17): ZERO
  `1/(x^k sqrt(2+2a-2(1+a)+bx^2+cx^4))`. The defective tree took 1_2_2_6_r3 (`IGtQ[p,-2]` accepting p=-1/2,
  unverified); the IGT fix removes it (Rubi's reading) and the route reaches 1_2_2_6_r9 (catch-all). All arms CN. —
  follows from: the IGT translation fix + EqQ/NeQ syntactic reading (ZERO) — [fixed-defect: none]
- class 1 g112 (2 entries, deterministic, final contains-noun top=1_2_2_3_r22): As P5 g127. `(1-2x^2)/(1±2x^2+4x^4)`:
  r22 (`not(is(b^2-4ac > 0))` on the number -12, True) → the radical quadratic sub-integrals bind 1_2_3_5_r24
  (catch-all), the g101 mechanism. r3 verified e63 1.4 s; e59 CN in all arms. — follows from: condition retry (e63);
  e59 not determined (route unchanged since P5) — [fixed-defect: none]
- class 1 g113 (2 entries, deterministic, final contains-noun top=1_2_2_3_r59): As P5 g128. `(d+ex^2)/sqrt(±a∓cx^4)`:
  r59 (`%mr_negQ(c/a)`, `%mr_neQ`) → `e/q·Int[(1+qx^2)/sqrt(a+cx^4)]`. Rubi's 1_2_2_3_r58 `Not[GtQ[a,0]]` does not
  answer → 1_2_2_3_r100 → marker. The first term's `1/sqrt(a+cx^4)` has the same site (1_1_3_1_r36). All arms CN. —
  follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g114 (2 entries, deterministic, final contains-noun top=1_2_2_3_r78): Fix-induced (p5 verified 1.3–1.6 s).
  1.2.2.3 `1/((d+ex^2)sqrt(a+bx^2-cx^4))`. r78 (`%mr_negQ(c/a)`) normalizes to
  `Int[1/((d+ex^2)sqrt(1+Ax^2)sqrt(1+Bx^2))]`, where Rubi takes 1_1_2_5_r17 (`Not[GtQ[A,0]] && GtQ[1,0] && GtQ[1,0]
  && …`, EllipticPi; the corpus `elliptic_pi`, 2 steps). The port's r17 does not answer → 1_1_2_5_r39 (catch-all) →
  marker. All arms CN. — follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g115 (2 entries, deterministic, final deferred top=1_1_2_6_r12): As P5 g132. Both cores put 1_1_2_6_r12
  (ExpandIntegrand) at top. P0's expansion dispatched (1_1_2_3_r1, 1_4_1_r7); the fixed core has nfires=1 and a noun.
  All arms deferred. — follows from: not determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at
  1_1_2_6_r12 (vs a `%mr_intSum` fault), awaiting probe 16]
- class 1 g116 (2 entries, deterministic, final deferred top=1_1_2_7_r55): `(a+cx^2)^p/(d+ex)^2`.
  - **Defective tree.** 1_1_2_7_r56 (`NegQ[a/b]` on the symbolic ratio, true under the strict sign) → AppellF1,
    unverified.
  - **Final core.** The NEGQ fix reads PosQ[a/c] True, as Rubi's PosAux. 1_1_2_7_r55 (`%mr_iLtQ(n,-1)` n=-2, `%mr_posQ`)
    expands alone (nfires=1) → noun.
  - **P0 and arms.** P0 1_1_1_4_r47 → r56 (2.5–2.6 s). All arms deferred.

  — follows from: the NEGQ translation fix (Rubi's branch) — [fixed-defect: undetermined — EQ-REWRITE at 1_1_2_7_r55
  (vs a `%mr_intSum` fault), awaiting probe 16]
- class 1 g117 (2 entries, deterministic, final deferred top=1_1_2_8_r100): As P5 g57 (e366, e380). 1_1_2_8_r100
  (`%mr_iLtQ(p,0)`, p=-1/-2 legit) answers `x(d+ex)^n/(a+cx^2)`-type alone. P0: 1_1_2_8_r109 / r100 over 9_1_r16. All
  arms deferred. — follows from: not determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at
  1_1_2_8_r100 (vs a `%mr_intSum` fault), awaiting probe 16]
- class 1 g118 (2 entries, deterministic, final deferred top=1_1_2_8_r123): As P5 g133. The catch-all binds
  `(A+Bx)(a+cx^2)/x`, `(3+2x^2)/((-1+x)^2x)` with p=1 through `p_.` and answers at top. P0: 1_2_1_9b_r32 / 1_1_2_8_r91.
  All arms deferred. — follows from: faithful Optional binding / G-1 — [fixed-defect: none]
- class 1 g119 (2 entries, deterministic, final deferred top=1_1_2_9_r19): As P5 g134. 1_1_2_9_r19 (`IntegersQ[n]`, n=1
  through `n_.`) expands `(A+Bx)(d+ex)^m/(a+cx^2)` alone (nfires=1). r3 verified 0.3 s. P0 1_2_1_3b_r68 over 1_4_1_r7.
  — follows from: condition retry — [fixed-defect: undetermined — EQ-REWRITE at 1_1_2_9_r19 (vs a `%mr_intSum` fault),
  awaiting probe 16]
- class 1 g120 (2 entries, deterministic, final deferred top=1_1_3_6_r31): As P5 g136. 1_1_3_6_r31 (ExpandIntegrand)
  answers `(ex)^m(A+Bx^n)/((a+bx^n)(c+dx^n))` alone. P0: the manual 9.1 `u*(a*x^n)^m`. All arms deferred. — follows
  from: 9.1 regeneration — [fixed-defect: undetermined — EQ-REWRITE at 1_1_3_6_r31 (vs a `%mr_intSum` fault), awaiting
  probe 16]
- class 1 g121 (2 entries, deterministic, final deferred top=1_1_3_7_r29): Fix-induced (p5 verified 1.3 s).
  - **Integrand.** 1.1.3.8 `(b^(1/3)x+a^(1/3)(1∓sqrt 3))/sqrt(a+bx^3)`. Rubi's 1-step elliptic-E rule needs
    `EqQ[b c^3-2(5∓3√3)a d^3,0]`, which is true by hand.
  - **Final core.** The port's `%mr_eqQ` reads the unexpanded `(1-sqrt(3))^3` form False. The NeQ twin 1_1_3_7_r29
    (`%mr_posQ(a)`, True for the symbol a as in Rubi) accepts at top. Its second sub-integral is the same shape, so
    the chain ends in a noun (nested 1_1_3_1_r30).
  - **Defective tree.** The strict sign read PosQ[a] False and took the NegQ twin 1_1_3_7_r31 (P0's route).
  - **Arms.** All deferred.

  — follows from: the NEGQ translation fix (Rubi's branch) exposing the EqQ/NeQ syntactic reading (unlisted) —
  [fixed-defect: none]
- class 1 g122 (2 entries, deterministic, final deferred top=1_1_3_7_r37): As P5 g137. 1_1_3_7_r37
  (`%mr_iGtQ(n/2,0)` n=4) splits Pq with `mr_sum(lambda…)` into an equal-form sum; no nested fire, a noun. P0
  1_2_2_5_r3. All arms deferred. — follows from: faithful binding — [fixed-defect: undetermined — EQ-REWRITE at
  1_1_3_7_r37 (vs a `%mr_intSum` fault), awaiting probe 16]
- class 1 g123 (2 entries, deterministic, final deferred top=1_2_2_3_r100): As P5 g138.
  `(√a+x^2√c)/sqrt(-a+cx^4)`, `(1+x^2 sqrt(c/a))/sqrt(-a+cx^4)`: `EqQ[c d^2+a e^2,0]` holds. Rubi takes 1_2_2_3_r58
  `Not[GtQ[-a,0]]` (the corpus elliptic_e, 3 steps); the port's r57/r58 do not answer and the catch-all answers at top.
  All arms deferred. — follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g124 (2 entries, deterministic, final deferred top=1_2_3_5_r24): As P5 g141. `(1±x^4)/(1∓2x^4+x^8)`:
  catch-all at top; r3 verified 0.2 s. — follows from: condition retry — [fixed-defect: none]
- class 1 g125 (2 entries, deterministic, final deferred top=1_3_4_r3): As P5 g142. 1_3_4_r3 (a linear substitution
  into a new variable, not an equal form) answers alone in 9.5–10.9 s with a noun. P0 1_1_1_6_r7. r3 deferred 1.0–1.2 s.
  — follows from: not determined from the traces (the corpus AppellF1 rules are not reached) — [fixed-defect: none]
- class 1 g126 (2 entries, deterministic, final timeout top=1_1_1_2_r16): VERIFY-TIMEOUT, the g52 chain (1_1_1_2_r32 →
  1_1_3_1_r52 → 1_1_3_1_r57 on `1/(1-bx^4)`, where Rubi's 1_1_3_1_r24 `Not[GtQ[a/b,0]]` does not answer). Top r16
  fired at 30 s and 120 s. e1717 is fix-induced; e1718 was RT-SUM on the defective tree. r3 verified 0.1–0.2 s. t100
  timeout 2. — follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g127 (2 entries, deterministic, final timeout top=1_1_1_3_r19): Fix-induced (p5 verified 0.2 s).
  VERIFY-TIMEOUT (top fired at 30 s and 120 s). `x^2/((1-x)^(1/3)(2-x)^(1/3))`: the g53/g82 Rubi elliptic chain after
  the NE fix (1_1_3_1_r30, 1_1_3_7_r29, 1_1_3_2_r45, 1_2_1_1_r17, 1_1_1_2_r30/r31, 1_1_1_3_r8). All arms timeout. —
  follows from: the NE translation fix (Rubi's reading) + verification cost — [fixed-defect: none]
- class 1 g128 (2 entries, deterministic, final timeout top=1_1_2_3_r20): VERIFY-TIMEOUT. `(a-bx^2)^(2/3|5/3)(3a+bx^2)`.
  The defective tree answered 1_1_2_3_r11 (IGT p=2/3, a noun). The final route is Rubi's (1_1_3_1_r31, 1_1_3_7_r31,
  1_1_3_2_r46, 1_1_2_1_r27/r5, top r20). r4 verified 0.7–0.8 s. t100 timeout 2. — follows from: the IGT translation fix
  + model flags — [fixed-defect: none]
- class 1 g129 (2 entries, deterministic, final timeout top=1_1_3_3_r3): Fix-induced (p5 verified 0.2 s).
  VERIFY-TIMEOUT. 1.1.3.3 `sqrt(a+b/x)/(c+d/x)^(1/2)`: 1_1_3_3_r3 (`%mr_iLtQ(n,0)` n=-1) → 1_1_1_3_r22/r23(/r25) →
  1_1_2_1_r15 (atanh; its NegQ on the substituted ratio picks the corpus's atanh branch). final120 error e168 118.8 s;
  t100 timeout 2; r3 verified e169 0.9 s. — follows from: verification cost; condition retry (e169) — [fixed-defect: none]
- class 1 g130 (2 entries, deterministic, final timeout top=1_1_3_4_r18): VERIFY-TIMEOUT, the g34 route under
  1_1_3_4_r18 (1_1_3_7_r45 first, 1_1_2_1_r10, 1_1_3_2_r37 or 1_1_3_1_r21, 1_1_3_2_r71). The defective tree took RT-SUM
  1_1_3_2_r36 / 1_1_3_1_r14. All arms timeout. — follows from: the IGT/NEGQ translation fixes (Rubi's route) +
  verification cost — [fixed-defect: undetermined — EQ-REWRITE at 1_1_3_7_r45 (vs no rule), awaiting probe 16]
- class 1 g131 (2 entries, deterministic, final timeout top=1_1_3_4_r24): As g130 with top 1_1_3_4_r24 (P5 g81 took
  RT-SUM). All arms timeout. — follows from: as g130 — [fixed-defect: undetermined — EQ-REWRITE at 1_1_3_7_r45 (vs no
  rule), awaiting probe 16]
- class 1 g132 (2 entries, deterministic, final timeout top=1_2_1_2_r113): As P5 g111, except that 1_2_1_9b_r5's IGT
  acceptance (P5's tag) is gone from the route. The 30 s top is the nested 1_2_1_2_r113.
  - **e981** `x^9/(quartic)^(3/2)`: the top-level 1_2_2_2_r8 has fired by 120 s: VERIFY-TIMEOUT. — [fixed-defect: none]
  - **e982**: r113 is still the last fire at 120 s (MID-CHAIN). — [fixed-defect: undetermined — no top-level route
    observed]

  All arms timeout. — follows from: faithful binding; cost — [fixed-defect: undetermined — no top-level route observed
  (e982)]
- class 1 g133 (2 entries, deterministic, final timeout top=1_2_1_2_r93): As P5 g151. VERIFY-TIMEOUT (top-level
  elliptic substitution fired). `1/(sqrt(d+ex)sqrt(quad))`: nested 1_1_2_3_r42 (`is(c > 0) and is(a > 0)` on the
  substitution's unit coefficients). All arms timeout. — follows from: faithful binding; cost — [fixed-defect: none]
- class 1 g134 (2 entries, deterministic, final timeout top=1_2_1_3_r55): As P5 g152. e1647: r55 top at 30 s over the
  elliptic chain. e130 `(A+Bx^2)/(x(quartic)^3)`: the log/atanh chain at 30 s; the top-level 1_2_2_4_r9 has fired at
  120 s. VERIFY-TIMEOUT; all arms timeout. — follows from: faithful binding; cost — [fixed-defect: none]
- class 1 g135 (2 entries, deterministic, final timeout top=1_2_1_5_r26): As P5 g154. VERIFY-TIMEOUT. 1.2.1.6
  `x sqrt(quad)/(d-fx^2)`: the top 1_2_1_5_r26 (`is(p>0)`, g=0 through `g_.`) fired; its only nested fire is 1_4_1_r18
  (first, no child). All arms timeout. — follows from: faithful Optional binding; cost — [fixed-defect: undetermined —
  EQ-REWRITE at 1_4_1_r18 (vs no rule), awaiting probe 16]
- class 1 g136 (2 entries, deterministic, final timeout top=1_2_1_8_r3): Fix-induced (p5 verified 8.4–10.1 s).
  1.2.1.4 `sqrt(f+gx)/((d+ex)^3 sqrt(a+bx+cx^2))`. 1_2_1_8_r3's PolyQuotient split is top at 30 s over the elliptic
  chain; at 120 s P0's top 1_2_1_3_r105/r102 has fired. r3 verified 1.0–1.2 s; t100 timeout 2. — follows from:
  condition retry (cost) — [fixed-defect: none]
- class 1 g137 (2 entries, deterministic, final timeout top=1_2_2_2_r13): MID-CHAIN. 1.2.3.2
  `(d+ex)^2/(a+b(d+ex)^2+c(d+ex)^4)^3`: the nested 1_1_2_1_r12, 1_2_2_3_r24, 1_2_2_3_r36, 1_2_2_2_r13 at 30 s and
  120 s. The defective tree took 1_2_2_3_r27 (the NegQ[b^2-4ac] branch; P5 tag negQ). The NEGQ fix reads
  PosQ[b^2-4ac] True (first term b^2, as Rubi) and takes r24, the corpus's real-root branch. P0's top-level 1_4_2_r24
  never fires. All arms timeout. — follows from: the NEGQ translation fix (Rubi's branch); the rest not determined —
  [fixed-defect: undetermined — no top-level route observed at 120 s]
- class 1 g138 (2 entries, deterministic, final timeout top=1_2_2_2_r14): As g137 with 1_2_2_2_r14 (`(d+ex)^4/(…)^3`).
  — follows from: as g137 — [fixed-defect: undetermined — no top-level route observed at 120 s]
- class 1 g139 (2 entries, deterministic, final timeout top=1_2_2_2_r15): As g137 with 1_2_2_4_r39/r35, 1_2_2_2_r15
  (`1/((d+ex)^2(…)^3)`). — follows from: as g137 — [fixed-defect: undetermined — no top-level route observed at 120 s]
- class 1 g140 (2 entries, deterministic, final timeout top=1_2_2_6_r1): As P5 g158. VERIFY-TIMEOUT (top 1_2_2_6_r1
  fired at 30 s and 120 s).
  - **e30.** The atanh chain + 1_2_1_3_r44, 1_2_2_4_r9, 1_4_1_r18.
  - **e40.** 1_1_2_2_r39 (p=-1 through `%mr_iLtQ`), 1_2_2_4_r43, 1_4_1_r18.
  - **Why EQ-REWRITE is not asserted.** 1_4_1_r18 is not first-listed, so a child may exist.
  - **Arms.** r3 CN e30 11.5 s; otherwise timeout.

  — follows from: faithful Optional binding; cost — [fixed-defect: none]
- class 1 g141 (2 entries, deterministic, final timeout top=1_4_2_r26): As P5 g161. 1.2.4.2
  `1/(sqrt(x)sqrt(x(a+bx+cx^2)))`: 1_1_2_1_r13, 1_2_4_1_r4 (`%mr_posQ(n-2)` on numbers), 1_4_2_r26 at 30 s; at 120 s
  P0's top 1_4_1_r34 has fired. r4 verified 0.7 s (model flags). — follows from: model flags — [fixed-defect: none]
- class 1 g142 (2 entries, deterministic, final timeout top=1_4_2_r27): As g141 with 1_2_4_2_r3, 1_4_2_r27; r4 verified
  0.6 s. — follows from: model flags — [fixed-defect: none]
- class 1 g143 (2 entries, deterministic, final timeout top=1_4_3_r31): Fix-induced (p5 verified 2.3–2.4 s).
  VERIFY-TIMEOUT. 1.3.2 `sqrt(2x^2+sqrt(3+4x^4))/((c+dx)sqrt(3+4x^4))`.
  - **Route.** Top 1_4_3_r31 (`is(a > 0)`, a=3) fired over 1_1_2_1_r11 (atan) / 1_1_2_7_r38(/r41) / 1_1_2_1_r13
    (atanh) on complex coefficients.
  - **Sign readings.** The NEGQ fix's PosAux reads complex numbers by Re/Im, as Rubi. The corpus answer is the
    `(1/2-%i/2)atan` form.
  - **Arms.** All timeout.

  — follows from: the NEGQ translation fix (Rubi's reading) + verification cost — [fixed-defect: none]
- class 1 g144 (2 entries, deterministic, final timeout top=9_1_r8): Fix-induced (p5 verified 20.4–23.7 s).
  EQQ-FAMILY. 1.2.1.4 `sqrt(a d e+…)/((f+gx)^(9/2)sqrt(d+ex))`. At 30 s only 1_4_1_r18, 9_1_r8. final120 CN
  43.9/74.6 s with top 1_2_1_3_r95 (the g110 NeQ-case route to the catch-all); t100 CN. r3 verified 1.6–1.7 s. —
  follows from: EqQ/NeQ syntactic reading (unlisted) + condition retry (cost) — [fixed-defect: none]
- class 1 g145 (2 entries, deterministic, final unexpected top=1_3_3_r17): As P5 g163. `F(x)sqrt(x-x^2)`,
  `F(x)/sqrt(x-x^2)` are noun-expected (CannotIntegrate, 0 steps).
  - **Route.** 1_3_3_r17 removes the x content (its FracPart(±1/2) reads floor: (1/2, 1/2) against Rubi's (1/2, -1/2),
    an equal form either way). Its nested integral has no fire.
  - **Answer.** The Maxima noun differentiates back (self=1): unexpected, a yardstick case. All arms unexpected.
  - **Clearance.** Both the IntPart reading and the seen-vs-no-rule question lead to the same noun.

  — follows from: yardstick (noun forms) — [fixed-defect: none]
- class 1 g146 (2 entries, deterministic, final unverified top=1_1_1_3_r65): `(bx)^m(%pi+dx)^n(%e+fx)^p`. 1_1_1_3_r65
  (AppellF1; `is(%pi > 0)`, `is(%e > 0)` true as Rubi's N reading) gives the corpus's own 1-step AppellF1 answer,
  unverifiable. e956 took 1_1_1_3_r55 (IGT) on the defective tree; e954 was as now. All arms unverified. — follows from:
  the IGT translation fix (e956) + faithful binding — [fixed-defect: none]
- class 1 g147 (2 entries, deterministic, final unverified top=1_1_2_7_r18): Fix-induced (p5 verified 0.4–0.5 s).
  `(d+ex)^(5|7)/(d^2-e^2x^2)^(5/2|7/2)`: 1_1_3_2_r115, 1_1_2_2_r2, 1_1_2_7_r12 (`%mr_iGtQ(n,2)`) under r18. The
  answers lack the corpus atan term (the g91 loss). r3 verified 0.3–0.4 s. — follows from: condition retry —
  [fixed-defect: none]
- class 1 g148 (2 entries, deterministic, final unverified top=1_1_2_8_r12): As P5 g166.
  `x^2(d+ex)/(d^2-e^2x^2)^(3/2)`: 1_1_3_2_r115, 1_1_2_2_r2 under r12; the atan term is missing; r3 verified 0.3–0.4 s.
  — follows from: condition retry — [fixed-defect: none]
- class 1 g149 (2 entries, deterministic, final unverified top=1_1_3_2_r107): `x^(-1-3n/2)/(a+bx^n)`,
  `(cx)^(-1-3n/2)/(a+bx^n)`.
  - **Final core.** The hypergeometric r107 (`%mr_iLtQ(p,0)` p=-1) answers at top:
    `-2 hypergeometric([-3/2,1],[-1/2],-bx^n/a)/(3a n x^(3n/2))`, unverifiable. The corpus has 5-step atan.
  - **Defective tree.** e2639 took 1_1_3_2_r5 (`%mr_negQ(n)` True on the symbol under the strict sign; an identity
    rewrite). The NEGQ fix reads NegQ[n] False, as Rubi. e2762 took the same r107.
  - **Arms.** All unverified.

  — follows from: the NEGQ translation fix (e2639); why Rubi's substitution rules are not reached ahead of r107 is not
  traced — [fixed-defect: none]
- class 1 g150 (2 entries, deterministic, final unverified top=1_1_3_2_r108): ZERO `x^k/sqrt(2+2a-2(1+a)+cx^4)`.
  - **Route.** r108 (`not(%mr_iLtQ(p,0) or is(a > 0))` reads the zero form as not positive) over 1_1_3_2_r107
    (+1_1_2_1_r13, 1_1_3_1_r57/r58 in e1024).
  - **Answers (2 read).** Divide by `(-(2*(a+1))+2*a+2)`: wrong.
  - **Sibling site.** r108's `a^IntPart(p)` reads floor on p=-1/2 (a^-1; Rubi a^0). The zero form also divides inside
    `(1+cx^4/a)^FracPart(p)` and the hypergeometric argument, so this reading does not decide.
  - **Fix-induced and arms.** e1023 (p5 verified 0.1 s, route not traced). All arms unverified.

  — follows from: EqQ/NeQ syntactic reading (ZERO) — [fixed-defect: none]
- class 1 g151 (2 entries, deterministic, final unverified top=1_1_3_2_r32): Fix-induced (p5 verified 0.2 s).
  1.1.3.2 `1/(x^k(a+bx^6)^2)`: the g93 e1326 route (1_1_3_7_r45 first, 1_1_2_1_r10, 1_1_3_2_r37, r67, top r32). The
  answers hold `%i*(1/b)^(5/6)*log(…)` Maxima-integrate forms, unverifiable. r4 timeout e1333 / unverified e1339 2.9 s;
  r3 unverified 7.3 s. — follows from: the IGT/NEGQ translation fixes (Rubi's route) — [fixed-defect: undetermined —
  EQ-REWRITE at 1_1_3_7_r45 (vs no rule), awaiting probe 16]
- class 1 g152 (2 entries, deterministic, final unverified top=1_1_3_2_r63): Fix-induced (p5 verified 0.1 s). ZERO
  `x^4/sqrt(2+2a-2(1+a)+cx^4)`, `x^4/sqrt(a+(2+2c-2(1+c))x^4)`: r63 (+1_1_3_1_r57/r36). The answers divide by the zero
  form, e.g. `(x*sqrt(…))/(3*(-(2*(c+1))+2*c+2))`: wrong. All arms unverified. — follows from: EqQ/NeQ syntactic reading
  (ZERO) — [fixed-defect: none]
- class 1 g153 (2 entries, deterministic, final unverified top=1_2_1_2_r111): As P5 g118. EQQ-FAMILY
  `sqrt(d+ex)/(a d e+(c d^2+a e^2)x+c d e x^2)^k`: 1_4_1_r18, the NeQ-case 1_2_1_3_r55 (divides by
  `c d^2-b d e+a e^2`), top r111 (e2076 via the elliptic chain). All arms unverified. — follows from: EqQ/NeQ syntactic
  reading (unlisted) — [fixed-defect: none]
- class 1 g154 (2 entries, deterministic, final unverified top=1_2_2_1_r17): As P5 g271/g272. ZERO
  `1/sqrt(2+2a-2(1+a)+bx^2+cx^4)`: 1_2_2_1_r17 (`%mr_negQ(c/a)`) with 1_1_2_3_r41/r42. The elliptic answers divide by the
  zero form. All arms unverified. — follows from: EqQ/NeQ syntactic reading (ZERO) — [fixed-defect: none]
- class 1 g155 (2 entries, deterministic, final unverified top=1_4_1_r7): As P5 g54 (e500, e234).
  - **Route.** Sum integrands split by 1_4_1_r7.
  - **e500.** 1_4_1_r18 (first, no child), 1_1_2_2_r39. The answer holds `'integrate(x^(m+1)/(1/a-a*x^2)^2,x)`: r18's
    quotient rewrite handed to Maxima integrate.
  - **e234.** 1_4_1_r18, 1_1_3_2_r107, 1_4_1_r43 (`is(a >= 0)` on a=0, true in both). The answer holds
    `'integrate(sqrt(a*x^(2*n))/(x^n*sqrt(x^n+1)),x)`.
  - **Corpus and arms.** Unverifiable steps=-5 rows. All arms unverified.

  — follows from: faithful binding — [fixed-defect: undetermined — EQ-REWRITE at 1_4_1_r18 (vs no rule), awaiting probe 16]
- class 1 g156 (1 entry, deterministic, final contains-noun top=1_1_1_2_r32): Fix-induced (p5 verified 0.2 s). 1.1.1.2
  e1651 `1/((a+bx)^(1/2)(c+dx)^(1/4))`: r32 → 1_1_3_2_r49 → 1_2_2_3_r100, the g28 mechanism. r3 verified 0.2 s. —
  follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g157 (1 entry, deterministic, final contains-noun top=1_1_1_3_r13): As P5 g172. e195 `(c+dx)^3/(x(a+bx))`:
  r13 (`is(p>1)` p=3) → 1_1_1_4_r42 (catch-all) → marker; CN in all arms. — follows from: faithful Optional binding;
  why 1.1.1.3 declines the reduced integrand is not traced (route unchanged since P5) — [fixed-defect: none]
- class 1 g158 (1 entry, deterministic, final contains-noun top=1_1_1_4_r25): Fix-induced (p5 verified 1.4 s).
  1.1.1.4 e108 `sqrt(a+bx)/(sqrt(c+dx)sqrt(e+fx)sqrt(g+hx))`. r25 substitutes to
  `1/((h-bx^2)sqrt(1+Ax^2)sqrt(1+Bx^2))`. Rubi's 1_1_2_5_r17 (`Not[GtQ[A,0]] && GtQ[1,0] && GtQ[1,0] && …`;
  the corpus `elliptic_pi`, 2 steps) does not answer → 1_1_2_5_r39 (catch-all). CN in all arms. — follows from:
  GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g159 (1 entry, deterministic, final contains-noun top=1_1_1_5_r8): As P5 g173. e154 `(a+bx)^n(c+dx^3)/x`:
  r8 (`is(expon(Px) > 2)`) → 1_1_2_8_r123 (catch-all) → marker; CN in all arms. — follows from: faithful binding; why
  the reduction reaches the catch-all is not traced — [fixed-defect: none]
- class 1 g160 (1 entry, deterministic, final contains-noun top=1_1_1_7_r15): 1.1.1.7 e7
  `(a+bx)^(1/2)(A+Bx)/(sqrt·sqrt·sqrt)`.
  - **Route.** The elliptic chain with 1_1_1_4_r25's `1/((h-bx^2)sqrt(1+Ax^2)sqrt(1+Bx^2))` reaching 1_1_2_5_r39 (the
    g158 site 1_1_2_5_r17 does not answer).
  - **Defective tree.** The record timed out at 30.0 s; its probe leg verified at 25.9 s via 1_1_2_5_r20/r31 (P5 g282,
    noise). The NEGQ fix removes r20's `%mr_negQ(d/c)` acceptance (Rubi reads the symbolic ratio positive).
  - **Arms.** P0 15.2 s. All arms CN.

  — follows from: GeQ/GtQ reading (ticket 02) — [fixed-defect: none]
- class 1 g161 (1 entry, deterministic, final contains-noun top=1_1_2_2_r22): Fix-induced (p5 verified 0.2 s). 1.1.2.2
  e639 `sqrt(cx)/sqrt(3a-2ax^2)`: r22 (`is(-b/a > 0)`, 2/3) → 1_1_2_2_r27 → 1_1_3_2_r49 on `x^2/sqrt(3a-2ax^4)` →
  Rubi's 1_2_2_3_r58 `Not[GtQ[3a,0]]` does not answer → 1_2_2_3_r100. CN in all arms. — follows from: GeQ/GtQ reading
  (ticket 02) — [fixed-defect: none]
- class 1 g162 (1 entry, deterministic, final contains-noun top=1_1_2_5_r33): Fix-induced (p5 verified 2.4 s). 1.1.2.5
  e113 `sqrt(a+bx^2)/(sqrt(c+dx^2)sqrt(e+fx^2))`: r33 substitutes to
  `1/((1-bx^2)sqrt(1-(bc-ad)x^2/c)sqrt(1-(be-af)x^2/e))`. Rubi's 1_1_2_5_r17 (EllipticPi; the corpus
  `a·elliptic_pi(…)`, 2 steps) does not answer → 1_1_2_5_r39. CN in all arms. — follows from: GeQ/GtQ reading
  (ticket 02) — [fixed-defect: none]
- class 1 g163 (1 entry, deterministic, final contains-noun top=1_1_2_5_r37): Fix-induced (p5 verified 4.9 s). e108
  `sqrt(a+bx^2)sqrt(c+dx^2)/(e+fx^2)^(3/2)`: r37 → r33 (g162's site, → r39) and r34 → 1_1_2_3_r41/r34/r45, 1_1_2_4_r54
  (PosQ on symbolic ratios, True as Rubi). CN in all arms. — follows from: GeQ/GtQ reading (ticket 02) —
  [fixed-defect: none]
- class 1 g164 (1 entry, deterministic, final contains-noun top=1_1_3_1_r11): 1.1.3.2 e703 `1/(2+3x^4)^2`.
  - **Defective tree.** RT-SUM 1_1_3_1_r13/r4 (IGT, timeout); the IGT fix removes them.
  - **Final route.** Top 1_1_3_1_r11 (`%mr_iGtQ(n,0)`, `is(p<-1)`) → 1_1_3_1_r23 → 1_2_2_3_r20/r23 → 1_2_3_5_r12/r24
    (catch-all), the g101 mechanism.
  - **Arms.** r3 verified 2.7 s.

  — follows from: the IGT translation fix + condition retry — [fixed-defect: none]
- class 1 g165 (1 entry, deterministic, final contains-noun top=1_1_3_1_r23): e695 `1/(2+3x^4)`: as g164 with top r23
  (the defective tree took RT-SUM 1_1_3_1_r13); r3 verified 2.8 s. — follows from: the IGT translation fix + condition
  retry — [fixed-defect: none]
- class 1 g166 (1 entry, deterministic, final contains-noun top=1_1_3_2_r30): e701 `x^4/(2+3x^4)^2`, fix-induced (p5
  verified 0.1 s): the g101 route under r30; r3 verified 2.8 s. — follows from: the IGT translation fix + condition
  retry — [fixed-defect: none]
- class 1 g167 (1 entry, deterministic, final contains-noun top=1_1_3_2_r39): e694 `x^2/(2+3x^4)`, fix-induced (p5
  verified 0.1 s): r39 → 1_2_2_3_r20/r23 → 1_2_3_5_r12/r24; r3 verified 2.7 s. — follows from: the IGT translation fix
  + condition retry — [fixed-defect: none]
- class 1 g168 (1 entry, deterministic, final contains-noun top=1_2_1_3_r104): EQQ-FAMILY. 1.2.1.4 e661
  `sqrt(d+ex)/((f+gx)sqrt(a d e+(c d^2+a e^2)x+c d e x^2))` (Rubi 2 steps, atan).
  - **Route.** The NeQ-case r104 → the elliptic chain → 1_1_1_4_r29 → 1_1_2_5_r39 (catch-all). The 1_1_2_5_r18
    `Not[GtQ[c,0]]` site is on the way, but Rubi never reaches it for this integrand.
  - **Defective tree.** Unverified via 1_1_2_5_r20/r31.
  - **Arms.** All CN.

  — follows from: EqQ/NeQ syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g169 (1 entry, deterministic, final contains-noun top=1_2_1_3_r57): As P5 g174 (CATCH-1 via 1_4_1_r34 →
  1_2_2_7_r42). — follows from: faithful Optional binding — [fixed-defect: none]
- class 1 g170 (1 entry, deterministic, final contains-noun top=1_2_1_3_r94): Fix-induced (p5 verified 3.4 s). 1.2.1.4
  e684 `sqrt(a d e+…)/((f+gx)sqrt(d+ex))`: as g168 with top r94 (elliptic chain → 1_1_1_4_r29 → 1_1_2_5_r39). All arms
  CN. — follows from: EqQ/NeQ syntactic reading (unlisted) — [fixed-defect: none]
- class 1 g171 (1 entry, deterministic, final contains-noun top=1_2_1_4_r31): Fix-induced (p5 verified 1.4 s). 1.2.1.5
  e13 `1/(sqrt(a+bx+cx^2)sqrt(d+fx^2))`.
  - **Final route.** 1_2_1_4_r31 (`%mr_neQ(b^2-4ac,0)`; repl through `%mr_rt(b^2-4ac,2)`, which reaches
    `%mr_rt_negSumBaseQ` / `%mr_splitSum_aux`) gives
    `Int[1/(sqrt(b+r+2cx)sqrt(2a+(b+r)x)sqrt(d+fx^2))]`. That integral reaches the catch-all 1_1_2_9_r107.
  - **What should answer.** 1_1_2_9_r95, the unconditioned rule for exactly this shape, does not complete: neither
    it nor a child appears in the fires.
  - **P0.** 1_2_1_4_r30 alone. All arms CN.

  — follows from: not determined from the traces — [fixed-defect: undetermined — why 1_1_2_9_r95 does not answer (a
  decline/fault trace), and whether r31's Rt form (a sibling port) changed its sub-integrand]

## Clearance summary (g24–g171)

Counts are per group (148 groups; the e810 line is inside g76). A split group counts under its most severe sub-tag.

**Class 1 g24–g171 (148 groups):** none 98, IGT 0, NEGQ 0, NE 0, MUL 0, collapse 0, sibling:%mr_intPart_aux 1,
undetermined 49 (of which EQ-REWRITE 33, other 16).

**Ticket-02 groups (GeQ/GtQ reading, tagged none, counted inside the 98): 17.** They are g28, g35, g52, g60, g70, g81,
g102 (e846), g113, g114, g123, g126, g156, g158, g160, g161, g162, g163.

**Unlisted EqQ/NeQ syntactic gap (tagged none, informational): 25 groups.** EQQ-FAMILY: g24, g40 (e2265), g41, g45
(the route; tag undetermined), g46, g58, g69, g94, g95, g96, g105, g106, g110, g121, g144, g153, g168, g170. ZERO: g93
(e1027/e1029), g102 (e1032), g104 (e1036), g111, g150, g152, g154.

Every group whose tag is not `none`:

- **sibling:%mr_intPart_aux** — g27. On e254, e255, e604 and e605 (p<0), 1_2_3_2_r34 reads IntPart/FracPart by floor
  where Rubi uses IntegerPart. The answers carry the floor form and the corpus carries Rubi's. That branch is unchanged
  by 843eb5f, so the defective tree's PASS on e254/e604/e605 is not explained by it. The other 5 entries are none.
- **undetermined — EQ-REWRITE, awaiting probe 16 (33):**
  - `%mr_expandIntegrand` / `%mr_expandToSum` / `mr_sum`-split rules alone with a noun: g25 (1_2_2_7_r41), g30
    (1_1_2_8_r102), g31 (1_2_1_3_r20), g36 (1_1_2_6_r3), g42 (1_4_2_r20), g47 (1_1_2_8_r68), g48 (1_2_2_3_r86), g49
    (1_2_2_3_r98), g51 (1_4_2_r19), g73 (1_1_1_3_r17), g74 (1_1_2_8_r107), g75 (1_1_4_4_r11), g76 incl. e810
    (1_2_1_3_r15), g77 (1_4_2_r18), g78 (1_2_3_4_r100), g79 (1_2_3_4_r99), g115 (1_1_2_6_r12), g116 (1_1_2_7_r55), g117
    (1_1_2_8_r100), g119 (1_1_2_9_r19), g120 (1_1_3_6_r31), g122 (1_1_3_7_r37).
  - The first-listed equal-form rewrite on a longer route: g34, g130, g131 (1_1_3_7_r45, verification timeouts); g93
    e1326, g151 (1_1_3_7_r45, Maxima complex-log answers); g84, g85 e461, g135 (1_4_1_r18); g155 (1_4_1_r18, `'integrate`
    nouns); g90 (1_1_1_4_r46, `'integrate` nouns); g45 (1_2_1_9b_r1, e2223/e2224).
- **undetermined — other (16):**
  - No top-level route observed (MID-CHAIN at 120 s): g26, g56 (e1479), g62, g86, g87, g88, g132 (e982), g137, g138,
    g139.
  - MID-CHAIN ending in a death at about 60 s: g44, g83 (e1826 / e1807 have no switch; r45 is one candidate).
  - Heap exhaustion with no top-level fire, identical on the defective tree: g33, g80.
  - A new control-stack exhaustion with no fire, new since the defective tree and only with condition retry on: g61
    (e1572/e1757). A recursive fixed port is a candidate.
  - The unconditioned 1_1_2_9_r95 does not answer the r31 sub-integral (sibling-reachable `%mr_rt` form): g171.

**No group is explained by a residual IGT, NEGQ, NE, MUL or collapse reading.**

- **Where the fixes moved routes onto Rubi's reading.**
  - IGT: g30, g39, g52, g54, g59, g62, g66, g72, g87, g101, g103, g107, g111, g128, g146, g164–g167, and part of g27/g41/g69.
  - NEGQ: g56, g116, g121, g137–g139, g143, g149, g160.
  - NE: g53, g82, g102 e846, g127.
  - Collapse: e810 has no 9.1 fire on the fixed core.
- **What they fail on afterwards.**
  - The GeQ/GtQ gap (ticket 02).
  - The syntactic EqQ/NeQ gap.
  - An equal-form rewrite with no nested fire (probe 16).
  - Verification cost.
  - Condition retry or model flags (an arm verifies).
  - An unported step or catch-all.

## Diagnostic 16 re-reading (class 1)

> Evidence: `probes/matcher/16-seen-guard-trace.class1.out` (2026-09-15 12:34 UTC, Maxima
> branch_5_50_base_84_g4204fb669, SBCL 2.6.7, git HEAD 560b4a5, fixed core `b98e4748…`, P0 core `5ef9b3bc…`;
> entry set `probes/matcher/16-seen-guard-trace.class1.tsv`, parts A+B+C, 186 entries;
> `Results: 179 passed, 7 failed`).
>
> **How a row reads.** Ratsimp-only seen hit (trace arm), then the fixed-core class, then the class under the
> exact-only control (probe-local `%mr_seenp` = exact `member`: a DIAGNOSTIC ARM, not a proposed fix), then the P0
> route.
>
> **The rule** (the class 2/3 one). `collapse` when the hit cuts the route **and** the control moves the class
> toward PASS. A hit that cuts the route but leaves the class unchanged is called collapse-type and tagged `none`.
> "Identity re-dispatch" = the rule's repl hands `mr_int` the stored-identical integrand, and the exact test cuts it
> in both arms. A group whose entries split is tagged by its most severe sub-reading.
>
> **INCOMPLETE rows.** The 7 failures are all in this part:
> - the control arm did not return in 30 s: g25 e14, g36 e22, g45 e2223, g84 e2353/e2354, g135 e79/e86;
> - for g45 e2223, the trace arm's verification also timed out.
>
> **Trace class vs probe 10's final30.** They match, except g45 e2270/e2271: unverified at 26.3/25.4 s here, timeout
> in the record (near the cap).

- class 1 g25: undetermined → **collapse(non-9.1 site 1_2_2_7_r41)**; control **PASS 8/9**. Hit #2@#1 on 9/9;
  deferred → verified (e1–e3, e8–e10, e12, e13). e14's control does not return in 30 s. P0: 1_2_2_5_r9/r8 in pass
  1, 1_2_2_7_r40 in pass 2.
- class 1 g30: undetermined → **none** (a collapse-type hit that does not decide the verdict).
  - **Hit.** 8/8 at 1_1_2_8_r102.
  - **Control.** The rewrite dispatches to 1_4_1_r25, which refactors it to the original `…/(x^k*(e*x+d))` form.
    Its re-dispatch is exact-cut, so every entry stays deferred with `'integrate` of that form.
  - **Mechanism.** r102's expansion is a single term, not a partial-fraction sum (as class 1 g9). No `%mr_intSum`
    fault.
  - **P0.** 1_1_2_8_r106 in pass 1.
- class 1 g31: undetermined → **collapse(non-9.1 site 1_2_1_3_r20)**; control **verified 8/8**. P0: 1_2_1_3b_r68 /
  1_2_1_3_r109 in pass 2.
- class 1 g34: undetermined → **none**. No ratsimp hit (8/8). 1_1_3_7_r45's ExpandIntegrand hands back the
  identical integrand twice per entry, and the exact test cuts both. rubi returns in about 5 s, and the entry times
  out verifying. The control is identical (same answer). P0: 1_4_1_r34 in pass 1.
- class 1 g36: undetermined → **collapse(non-9.1 site 1_1_2_6_r3)**; control **not PASS**.
  - **Control.** Deferred → unverified 6. The hypergeometric route is 1_4_1_r18 → 1_1_2_9_r2 → 1_1_2_2_r39, as class 1
    g187. e22's control does not return in 30 s.
  - **P0.** 1_2_1_9b_r5 / 1_1_2_6_r9 / 1_1_2_6_r12 in pass 2.
- class 1 g42: undetermined → **collapse(non-9.1 site 1_4_2_r20)** (split).
  - **1.2.2.3 e36.** Ratsimp hit, deferred → **verified**.
  - **e68, e69, e220, e362, e363: none.** No ratsimp hit. The `u^q v^p` ExpandToSum normalizer hands back the
    identical integrand, the exact test cuts it, and the entry stays deferred with the same answer in both arms.
  - **P0.** 1_3_4_r21 / 1_2_2_5_r3 / 1_2_2_3_r27, all in pass 1.
- class 1 g45: undetermined → **collapse(non-9.1 site 1_2_1_9b_r1)** (split).
  - **e2224.** Ratsimp hit #3@#2, timeout → **verified**.
  - **e2223.** The same hit, but the control does not return in 30 s: undetermined.
  - **e2268–e2271: none.** No seen hit; the elliptic chain costs verification time (timeout 2, unverified 2 in both
    arms).
  - **P0.** 1_2_1_6_r4 in pass 1, 1_2_1_3_r53 in pass 2.
- class 1 g47: undetermined → **collapse(non-9.1 site 1_1_2_8_r68)**; control **verified 5/5**. P0: 1_1_2_8_r106 in
  pass 1.
- class 1 g48: undetermined → **collapse(non-9.1 site 1_2_2_3_r86)**; control **verified 5/5**. P0: the same r86, in
  **pass 2**.
- class 1 g49: undetermined → **collapse(non-9.1 site 1_2_2_3_r98)**; control **PASS 3/5**.
  - **PASS.** Verified e180, e188; expected e186.
  - **Not PASS.** e181, e187 → contains-noun, via the 1_2_3_4_r102 / 1_2_3_3_r49 catch-all markers.
  - **P0.** The same r98, in **pass 2**.
- class 1 g51: undetermined → **collapse(non-9.1 site 1_4_2_r19)** (split).
  - **1.3.1 e491.** Ratsimp hit, deferred → **verified**.
  - **e127, e631, e633, e863: none.** The `(dx)^m u^p` ExpandToSum normalizer re-dispatches the identical
    integrand (exact cut). Same answer in both arms.
  - **P0.** 1_2_2_5_r10 / 1_2_2_2_r21 in pass 1.
- class 1 g73: undetermined → **collapse(non-9.1 site 1_1_1_3_r17)** (split; control **not PASS**).
  - **e3181, e3182.** Ratsimp hit on r17's expansion sum, deferred → unverified.
  - **e925: none.** Identity re-dispatch at r17 (exact cut), the same answer.
  - **P0.** 1_1_1_3_r19 / r29 in pass 1.
- class 1 g74: undetermined → **collapse(non-9.1 site 1_1_2_8_r107)**; control **PASS 2/3**.
  - **PASS.** Verified e428, e429.
  - **Not PASS.** e422 → contains-noun (the 1_2_2_3_r99 marker).
  - **P0.** The same r107, in **pass 2**.
- class 1 g75: undetermined → **collapse(non-9.1 site 1_1_4_4_r11)**; control **verified 3/3**. P0: 1_1_4_4_r2 in
  pass 1.
- class 1 g76: undetermined → **collapse(non-9.1 site 1_2_1_3_r15)**; control **not PASS**.
  - **Control.** e809, e810 and e922 all go deferred → unverified. Each answer still holds `'integrate` terms from
    exact-cut identity re-dispatches at 1_1_1_3_r17/r18 and 1_2_1_3_r4, next to hypergeometric terms.
  - **P0.** The same r15, in **pass 3**. For e810, P0's own ratsimp hits (#6, #11 at 1_1_1_4_r40) did not stop it
    verifying.
- class 1 g76 **e810** (own row, attributed here by user decision): undetermined → **collapse(non-9.1 site
  1_2_1_3_r15)**; control **not PASS**.
  - **Row.** `1.2.1.4 e810 | c1 g76 | yes #2@1_2_1_3_r15 | deferred | unverified | differs`. P0: verified via
    1_2_1_3_r15 in pass 3.
  - **Control route.** 21 calls, 9.7 s, over 1_1_1_4_r47, 1_1_1_3_r18, 1_2_1_3_r4, 1_1_1_3_r6, 1_1_1_2_r37, 9_1_r27
    and 1_4_1_r18. Two exact cuts leave `a*'integrate((g*x+f)^n/(e*x+d)^2,x)` and a nested `'integrate` in the
    answer, so the zero chain cannot close it.
- class 1 g77: undetermined → **collapse(non-9.1 site 1_4_2_r18)**; control **verified 3/3**. The competing
  model-flag reading is excluded: the rewrite dispatches under the control. P0: 1_2_2_1_r19 in pass 1.
- class 1 g78: undetermined → **collapse(non-9.1 site 1_2_3_4_r100)**; control **verified 3/3**. P0: 9_1_r16 in pass
  2.
- class 1 g79: undetermined → **collapse(non-9.1 site 1_2_3_4_r99)**; control **not PASS**.
  - **Control.** e141, e152: timeout, with rubi returning at 6.2/3.1 s, so the time goes to verifying hypergeometric
    / AppellF1 forms. e153: unverified (AppellF1).
  - **P0.** 9_1_r16 in pass 2.
- class 1 g84: undetermined → **undetermined** (split).
  - **e2353, e2354.** Ratsimp hit #3@#2 at 1_4_1_r18. The trace arm returns in 2.3/4.1 s and times out verifying.
    The control arm does not return in 30 s (10–11 open calls, no fire). Still missing: whether the dispatched
    rewrite ends at all.
  - **e2466: none** (as read): no seen hit, verification cost.
  - **P0.** 1_2_1_2_r119 in pass 2.
- class 1 g85: undetermined → **none**. e441, e450: no seen hit (the atanh chain). e461: 1_4_1_r18's identity
  re-dispatch (#5 exact@#4), with no ratsimp hit. All three: rubi returns in 2.5–4.4 s, verification times out, and
  the control is identical. P0: the same r90, in pass 1.
- class 1 g90: undetermined → **collapse(non-9.1 site 1_1_1_4_r46)**; control **PASS 1/3**.
  - **Hit.** #4@#3 on 3/3; fixed class unverified.
  - **PASS.** e995 → expected.
  - **Not PASS.** e3126, e3130 stay unverified with a different answer (a nested `'integrate` remains).
  - **P0.** 1_1_1_3_r57 / 1_1_1_6_r5 in pass 1.
- class 1 g93: undetermined → **none**.
  - **e1326.** No ratsimp hit; 1_1_3_7_r45's identity re-dispatch is exact-cut twice, and the answer is
    Maxima-integrate logs, identical under the control.
  - **e1027, e1029.** Stay none (ZERO).
  - **P0.** 1_3_4_r1 / 1_3_3_r17 in pass 1.
- class 1 g115: undetermined → **collapse(non-9.1 site 1_1_2_6_r12)**; control **PASS 1/2**.
  - **PASS.** e27 → verified.
  - **Not PASS.** e47 → contains-noun: the 1_1_3_4_r81 route leaves `'unintegrable`.
  - **P0.** The same r12, in **pass 2**.
- class 1 g116: undetermined → **collapse(non-9.1 site 1_1_2_7_r55)**; control **not PASS**. e737, e420 → contains-noun,
  via the 1_2_2_4_r96 / 1_2_2_3_r99 markers. P0: 1_1_2_7_r56 in pass 2.
- class 1 g117: undetermined → **collapse(non-9.1 site 1_1_2_8_r100)** (split).
  - **e380.** Ratsimp hit, deferred → **verified**.
  - **e366: none.** Identity re-dispatch at r100 (exact cut), the same answer.
  - **P0.** 1_1_2_8_r109 / r100 in pass 2.
- class 1 g119: undetermined → **collapse(non-9.1 site 1_1_2_9_r19)**; control **verified 2/2**. P0: 1_2_1_3b_r68 in
  pass 2.
- class 1 g120: undetermined → **collapse(non-9.1 site 1_1_3_6_r31)**; control **verified 2/2**. P0: 9_1_r16 in pass
  2.
- class 1 g122: undetermined → **collapse(non-9.1 site 1_1_3_7_r37)**; control **verified 2/2**. P0: 1_2_2_5_r3 in
  pass 1.
- class 1 g130: undetermined → **none**. The g34 route under top 1_1_3_4_r18: 1_1_3_7_r45 identity re-dispatches,
  exact-cut, then the verification timeout. No ratsimp hit, and the control is identical. P0: 1_4_1_r34 in pass 1.
- class 1 g131: undetermined → **none**. As g130, with top 1_1_3_4_r24.
- class 1 g135: undetermined → **undetermined**.
  - **Trace arm.** Ratsimp hit at 1_4_1_r18 on e79 and e86. It returns in 1.4/1.6 s (top 1_2_1_5_r26) and times out
    verifying.
  - **Control arm.** It does not return in 30 s: 1_1_2_1_r13 / 1_2_1_1_r15 fire, with 5–6 calls still open.
  - **Still missing.** The control's end state.
  - **P0.** 1_4_2_r17 in pass 3.
- class 1 g151: undetermined → **none**. As g93 e1326 (1_1_3_7_r45 identity re-dispatch, exact cut, no ratsimp hit),
  with the same answer in both arms. P0: 1_3_4_r1 in pass 1.
- class 1 g155: undetermined → **none** (a collapse-type hit that does not decide the verdict).
  - **Hit.** #3 at 1_4_1_r18.
  - **Control.** Unverified stays unverified. e500's answer still holds `'integrate(x^(m+1)/(1-a^2*x^2)^2,x)`, and
    e234's is hypergeometric only.
  - **P0.** 1_4_1_r7 in pass 1.

**Part-B summary.**
- **Tags (33 groups).** collapse 23 (g25, g31, g36, g42, g45, g47, g48, g49, g51, g73, g74, g75, g76, g77, g78,
  g79, g90, g115, g116, g117, g119, g120, g122); none 8 (g30, g34, g85, g93, g130, g131, g151, g155);
  undetermined 2 (g84, g135).
- **Control reaching PASS.** 52 part-B entries: 50 verified, 2 expected.
- **Collapse groups where no entry reaches PASS.** g36, g73, g76 (incl. e810), g79, g116.
