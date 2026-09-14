> Task 4 Step 5 mechanism lines for probe 10's groups — class 1, groups g1–g17.
> Reads: probes/matcher/10-p5-attribution.class1.summary.out (groups g1–g17).
> Written 2026-09-14 by read-only analysis of the committed probe-10 outputs (commit 295effa); claims marked 'inferred' or 'not determined' are not measured.

# Task 4 Step 5 — mechanism lines, class 1 part A (g1–g17)

Inputs: `probes/matcher/10-p5-attribution.class1.summary.out` groups g1–g17 (864 entries), the raw
runs `…class1-{final30,p0,final120}.out`, the run 2–4 records `test/corpus_class1.p5-run{2,3,4}.out`,
the 100 s re-check `test/corpus_class1.p5-final.timeout-rerun/`, rule files on the final tree and at
`0a6664c` (P0), Rubi source under `reference/rubi/`, and the installed build's Maxima reader
`~/local/share/maxima/branch_5_50_base_84_g4204fb669/src/nparse.lisp`. Read-only analysis,
2026-09-14, HEAD 7726072. The evidence conventions (traces, arms r2/r3/r4, table order, timeouts) are
those of the class 2–3 document. The families OPT, DEG, NOUN, IGT, RETRY, 9.1, NEGQ, INNER and
VERIFY-TIMEOUT keep their class 2–3 meaning.

**How the traces were read.** Every entry's fire list, top rule and nfires were tabulated by script
for all 864 entries. Every integrand was pulled from the corpus by its `L` line. For the IGtQ tag, a
script checked every integrand of the 12 expansion-rule groups (g1, g4, g5, g9–g17) for a
non-integer exponent on the factor the rule's `p`/`m` slot binds. Only 3 + 1 entries have none
(named below). By hand: g1 21 entries across both files, g2 17 entries across 11 files, g3 all 80 P0
routes tabulated with 16 integrands read, and 11–44 entries in each other group.

## Families (class 1, part A)

- **EXPAND-NOUN (ExpandIntegrand rule answers alone with a noun).** A Rubi
  `Int[ExpandIntegrand[…], x]` rule is the only fire (nfires=1), and the top-level answer is a noun
  (deferred).
  - **What the rule does.** Its repl is `mr_int(%mr_expandIntegrand(u, x), x)`. The nested dispatch
    of the rewrite records no fire.
  - **Code unchanged since P0.** `%mr_expandIntegrand` / `%mr_expandIntegrand2`,
    `%mr_ei_pos_power_sum`, `%mr_ei_linear_power`, `%mr_expandLinearProduct` and `%mr_seenp` are
    byte-identical (diffed against `0a6664c`). So are `mr_top`'s seen push and check before the
    dispatch, and 1_4_1_r7's cond `mr_simplify_flag and %mr_sumQ(u)`.
  - **Two readings the traces cannot separate.**
    - (a) The seen guard: the rewrite is ratsimp-identical to the integrand already on the dispatch
      path, so `mr_top` returns Maxima `integrate(f, x)`, which is a noun for these algebraic
      integrands. `mr_top`'s own comment names "the 1.1.1.2 r12 ExpandIntegrand-identity repl" as a
      seen-guard case.
    - (b) The nested dispatch finds no rule.
  - **Against (a).** Where P0 fired the same rule at top level (g1 ×8, g5 ×61, g15 ×2), its nested
    dispatch did record fires (1_4_1_r7 splitting the sum, then per-term fall-through) under the same
    guard.
  - **Same shape** as class 2 g1 and class 3 g20.
- **IGT (extended).** Besides `IGtQ`→`>`, the generator maps `ILtQ`→`<` inside Simplify (1_1_3_2_r13
  `ILtQ[Simplify[(m+1)/n+p+1],0]` → `is(%mr_simp((m+1)/n+p+1) < 0)`). The same mapping covers
  integer-valued arguments (`IGtQ[(n-3)/2,0]` → `is((n - 3)/2 > 0)`, `IGtQ[(n-1)/2,0]`) and
  `IGtQ[p,-2]` → `is(p > -2)`.
- **NEGQ (Rubi side made precise).** Rubi's `PosAux` (IntegrationUtilityFunctions.m:608–634) returns
  True in each of these cases:
  - a symbol;
  - a power with an even integer exponent;
  - a power of a positive base;
  - a product whose factor signs combine to positive;
  - a sum whose first term is positive.
  So `NegQ[a/c]`, `NegQ[e^2 b^2]`, `NegQ[4 a c e^2]` and `NegQ[2(a+b)]` are False in Rubi.
  `%mr_negQ` is `not(sign = pos) and ≠ 0`, so it reads all of them true (an unknown sign or `pz` is
  not `pos`).
- **NEQ-BANG (`!=` in a generated condition).** Rubi's `k != 1` is emitted verbatim as
  `is(k != 1) = true` (7 generated class-1 lines contain `k != 1`).
  - **Reader source.** The installed build's `nparse.lisp` defines postfix `!` (`mfactorial`,
    lines 1310–1316) and infix `#` (`mnotequal`, 1409–1415), and no `!=` operator.
  - **Consequence.** The text therefore reads as `is(k! = 1)`: true for k = 1, false for k ≥ 2.
    That is the inverse of Rubi's test.
  - **Status.** This comes from reading the source; it was not measured. The g17 fires with k = 1
    are consistent with it.
- **NOFIRE.** The final core flushed no fire.
  - For a deferred entry this means no rule answered at top level. The dispatcher returned false, so
    `mr_top` returned the `mr_unintegrable` noun. Declines and misfires are not captured.
  - For a timeout it is weak evidence (an unflushed pipe at the kill).
- **MID-CHAIN (timeout).** The last flushed fire is a nested rule whose LHS is not the integrand's
  form. So the top-level rule had not completed by the cap. This is weak evidence, as for any
  timeout fire list.

## Group lines g1–g17

- class 1 g1 (147 entries, deterministic, final deferred top=1_2_1_3_r15): EXPAND-NOUN.
  - **Rule.** 1_2_1_3_r15 is Rubi 1.2.1.3 (the `(f+g x)^n` file) r15,
    `(d.+e.x)^m.(f.+g.x)^n.(a.+b.x+c.x^2)^p. → Int[ExpandIntegrand] /; FreeQ && IGtQ[p,0]`. Its cond
    is `… and is(p > 0)`.
  - **Final core.** All 147 read r15 alone (nfires=1) at 0.7–1.5 s. P0 verified in 1.2–17.5 s.
  - **139 entries** (P0 top 1_3_3_r6 40, 1_4_1_r34 32, 1_2_1_9_r22 31, 1_3_3_r17 16, 1_2_1_9b_r5 6,
    1_2_1_3_r49/r50/r51/r56/r57 14):
    - P0 has no r15 fire.
    - The substrate binds r15 through Optional `d.`/`n.` (e.g. e200
      `(A+B*x)*sqrt(b*x+c*x^2)/x^(5/2)`: d=0, n=1) with p = 1/2 … 7/2.
    - Rubi's `IGtQ[p,0]` is false for these p, so the rule is reached only through IGT.
  - **8 entries** (1.2.1.4 e809, e810, e886, e887, e893, e894, e922, e945):
    - P0's top was the same r15, with nested fires (e.g. e887 nfires=6: 1_2_1_9b_r5, 1_2_1_2_r109,
      1_4_1_r7). The substrate's r15 has none.
    - p = 1/2 in five of them (IGT, present on P0 too).
    - p = 1 in e809/e810/e922, where Rubi's own conditions hold. The no-nested-fire step is
      therefore independent of the translation.
  - **Sample.** 21 entries by hand (1.2.1.3 ×18, 1.2.1.4 ×3); all 147 fire lists and exponents by
    script; no deviating entry.
  - **Arms.** Deferred in all arms.
  — follows from: faithful Optional binding exposing the IGtQ translation (139); why the rewrite
  yields no nested fire (all 147) is not determined from the traces
  [defect: IGtQ] (144; e809/e810/e922 none seen) [collapse-family] e810 (P0 fires include 9_1_r28 =
  P0's double-root trinomial id, generated 9_1_r27; final fires: none)

- class 1 g2 (99 entries, deterministic, final timeout top=-): NOFIRE timeout.
  - **Fires.** No fire was flushed at 30 s (99/99) or at 120 s (97/99; two 1.1.2.4 entries show
    1_1_2_4_r28 at 120 s). The 100 s re-check reads timeout 99/99.
  - **P0.** Verified in 0.4–14.4 s.
  - **Files.** 1.2.1.2 48, 1.1.1.3 13, 1.2.1.4 8, 1.2.1.3 6, 1.3.1 5, 1.2.1.6 4, other files 15.
    P0 tops: 1_3_4_r1 41, 1_2_1_6_r4 8, 1_1_1_3_r18 6, 1_1_1_3_r19/1_2_1_6_r1 5 each, others 34.
  - **Arms.**
    - r3 (mr_cond_retry=false): verified 48 (up to 25.2 s), unverified 31 (30 of them 1.2.1.2 with
      P0 top 1_3_4_r1), deferred 3, timeout 17.
    - r2: timeout 99.
    - r4: timeout 97, verified 2.
  - **Reading.** The non-return depends on condition retry in 82 of 99 entries. With retry off, 48
    would PASS and 34 would still FAIL. Which rule's binding enumeration spends the time is not
    traced.
  - **Sample.** 17 entries by hand across 11 files, plus all 99 mechanically; all share the no-fire
    shape.
  — follows from: condition retry (cost), 82 entries; the 17 that also time out with retry off are
  not determined from the traces
  [defect: none seen — no final-core fire to inspect]

- class 1 g3 (80 entries, deterministic, final deferred top=-): NOFIRE deferred.
  - **Result.** No rule answers at top level on the substrate (0.1–10.5 s). Deferred in all arms.
    P0 verified in 0.1–7.4 s.
  - **Sub-bullets by P0 route (all 80 tabulated).** The first five subgroups (47 entries) rested on a
    binding Mathematica does not make, according to the Rubi LHS:
    - **9_1_r16 ×24** (1.1.3.2, 1.1.3.8, 1.1.4.2, 1.2.3.2, …; e.g. e2949
      `(d*x)^m*sqrt(a+b*(c*x^2)^(1/2))`): P0's manual 9.1 rule, literal `u*(a*x^n)^m`, bound `(d x)^m`
      with n read as 1. Rubi's own rule, and generated 9_1_r15, need a non-Optional `x_^n_` (9.1
      regeneration, DEG).
    - **1_1_2_2_r33 ×8** (`1/sqrt(±a±b*x^2)`): Rubi LHS `x_^m_.*(a_+b_.*x_^2)^p_` needs an x factor,
      so P0's m = 0 is an absent factor (DEG). P0's nested 1_1_2_1_r13 answered.
    - **1_1_3_2_r110 ×8** (`(a+b*x^k)/x`, `(a+b/x^k)/x`): Rubi LHS has a non-Optional `c_` in
      `(c_*x_)^n_`, and P0 read c=1 (DEG). On the substrate Rubi's own 1_1_3_2_r12 (p=1) does not
      answer either.
    - **1_1_4_1_r9 ×6** (`1/sqrt((a±b*x^k)/x^j)`): Rubi LHS `1/Sqrt[a_.*x_^2+b_.*x_^n_.]`. The
      integrand holds no such sum, and P0's defmatch matched it algebraically (DEG).
    - **1_1_2_2_r4 ×1** (e6 `(a+b*x^2)/x`): Rubi LHS has a non-Optional `p_`, and P0 read p=1 (DEG).
    - **33 others**, not determined: 1.4.2 ExpandToSum normalizers (r17 ×8, r20 ×4, r23 ×2,
      r16/r21 ×1), 1_2_1_1_r18 ×3, 1_4_1_r49/r50/r51 ×5, 1_4_3_r2 ×2, and one each of 1_2_2_1_r17,
      1_1_1_4_r44, 1_2_1_2_r109, 1_4_1_r23, 1_1_4_4_r10, 1_4_1_r29, 1_3_1_r15.
  - **Mixed.** The group mixes P0 mechanisms; on the final core all 80 share nfires=0.
  — follows from: G-1 (P0 degenerate bindings) for 47 entries by rule text; why Rubi's own routes do
  not answer (all 80) is not determined from the traces
  [defect: none seen — no final-core fire to inspect]

- class 1 g4 (62 entries, deterministic, final deferred top=1_2_1_2_r58): EXPAND-NOUN.
  - **Integrands.** All in 1.2.1.2: `(b*d+2*c*d*x)^m*(a+b*x+c*x^2)^p` and
    `(c*e+d*e*x)^m*(…)^p`, with p = 1/2, 3/2, 5/2, 4/3.
  - **Rule.** Rubi 1.2.1.2 r58 is ExpandIntegrand
    `/; EqQ[2cd-be,0] && IGtQ[p,0] && Not[EqQ[m,3] && NeQ[p,1]]`; its cond is `is(p > 0)` (IGT).
  - **Final core.** r58 alone at 0.4–2.4 s.
  - **P0.** 1_4_2_r6 (+ 1_4_1_r34) → 1_3_4_r1 at 1.6–2.4 s; P0 has no r58 fire. P0's literal is
    `(d + e*x)^m*(a + b*x+ c*x^2)^p`; why it did not answer is not traced.
  - **Sample and arms.** 13 entries by hand; deferred in all arms.
  — follows from: the substrate binding reaches r58 (P0 no fire) and exposes the IGtQ translation;
  the EXPAND-NOUN step is not determined from the traces
  [defect: IGtQ] (62)

- class 1 g5 (61 entries, deterministic, final deferred top=1_2_1_9b_r5): EXPAND-NOUN on the same
  top rule as P0.
  - **Rule.** Rubi 1.2.1.9 r5 is `(d.+e.x)^m. Pq (a.+b.x+c.x^2)^p. → ExpandIntegrand
    /; PolyQ[Pq,x] && IGtQ[p,-2]`; its cond is `is(p > -2)`.
  - **P0** (5.3–19.5 s). r5 at top with nested 1_4_1_r7 (46 entries nfires=2), then verified.
  - **Substrate** (2.5–3.2 s). r5 alone.
  - **Arms.**
    - r3: verified 48 (1.0–23.5 s), deferred 13.
    - r2/r4: deferred.
    - The substrate's r5 accepts only on a non-first binding. With retry off it declines, and an
      untraced route verifies.
  - **Exponents.** p = ±1/2, 3/2 in 60 entries (IGT, also present on the P0 route that passed).
    e370 `(d+e*x)^m*(…)/(3+2*x+5*x^2)` has p = −1, which meets Rubi's conditions.
  - **Sample.** 13 entries by hand.
  — follows from: condition retry (48 of 61); the EXPAND-NOUN step is not determined from the traces
  [defect: IGtQ] (60; e370 none seen)

- class 1 g6 (47 entries, deterministic, final timeout top=1_1_3_2_r13): VERIFY-TIMEOUT after an
  ILtQ-translated recurrence.
  - **Integrands.** All in 1.1.3.2: `x^m/(a+c x^k)^j` with k = 4, 6, 8.
  - **Top rule.** 1_1_3_2_r13 is Rubi `x^m (a+b x^n)^p /; ILtQ[Simplify[(m+1)/n+p+1],0] && NeQ[m,-1]`.
    Its cond is `is(%mr_simp(…) < 0)`.
    - A script over all 47 gives (m+1)/n+p+1 values of −1/8 … −15/8, −1/3, −1/2, −2/3, … and never
      an integer. Rubi rejects r13 for all 47 (IGT).
    - r13's LHS is the integrand's own form, and it closes every 30 s fire list, so rubi returned.
  - **Nested chain.** The reduction `mr_int(x^(m+n)(a+b x^n)^p)` runs one of:
    - 1_1_3_2_r36 (`IGtQ[(n-1)/2,0] && NegQ[a/b]`);
    - its PosQ twin r35 (numeric 2+3x^4, 1+x^6, 1+x^8);
    - 1_1_3_1_r14 (`IGtQ[(n-3)/2,0] && NegQ[a/b]`).

    For n = 4/6/8, their `(n∓…)/2 > 0` tests accept non-integers (IGT). r36 and r14 accept symbolic
    `a/c`, where Rubi's PosQ is True (NEGQ, 32 entries). The chain then runs the cos/Rt
    partial-fraction integrals (1_2_1_1_r12, 1_2_1_2_r3/r9, 1_1_1_1_r3/r5).
  - **P0.** Verified in 0.4–1.6 s via 1_3_4_r1 (25), 1_4_1_r34 (15) and 1_2_2_2_r8 (7); no r13 fire.
  - **Walls.**
    - 120 s: timeout 36; unverified 5 (e1354, e1355, e1370, e1372, e1373 at 72.0–112.6 s); error 1
      (e1495, 84.5 s).
    - Five entries have no 120 s run: the record reads e1371 unverified 22.0 s, and
      e1476/e1487/e1496/e1506 error at 17.2–28.8 s.
    - 100 s re-check: timeout 39, unverified 3.
  - **Arms.** r2/r3: timeout 42, error 4, unverified 1. r4: timeout 37, unverified 6, error 4.
  - **Sample.** All 47 integrands computed by script; 12 traces by hand; one mechanism.
  — follows from: not determined from the traces which change reaches r13 (P0's literal
  `x^m*(a+ b*x^n)^p` gave no r13 fire); its acceptance is the ILtQ translation; the cost is
  verification (error kinds not recorded)
  [defect: IGtQ] (47) [defect: negQ] (32: the symbolic-coefficient entries whose chain fires r36 or
  1_1_3_1_r14)

- class 1 g7 (45 entries, deterministic, final timeout top=1_2_2_3_r27): MID-CHAIN.
  - **Fire lists.** All 45 lists (nfires=9) are identical at 30 s and at 120 s: 1_4_1_r18 (40) or
    1_1_2_1_r13 (5), then 1_2_1_1_r12, 1_2_1_2_r3, 1_2_1_2_r9, 1_2_2_3_r27.
  - **Nesting.** r27's LHS `(d+e x^2)/(a+b x^2+c x^4)` is not the integrand's form
    (`(d+e*x)^k/(a+b*x+c*x^2)`, `x^(k/2)(A+Bx)/(…)`, `x^3 sqrt(d+e x^2)/(a+b x^2+c x^4)`). So r27 sits
    under Rubi's √-substitution, and the top rule had not completed by 120 s (weak).
  - **Rule.** Rubi 1.2.2.3 r27 is `NegQ[b^2-4ac]`; its PosQ branch is r24. The cond is
    `%mr_negQ(b^2 - 4*a*c)`.
  - **NegQ reading.** The substituted quartic's discriminant is e^2(b^2−4ac), b^2e^2 or 4ace^2.
    - For 42 entries Rubi's PosAux reads it positive, so NegQ is False; `%mr_negQ` reads true
      (NEGQ, inferred: the nested integrand is not traced).
    - e1464 and e1466 (`1+x^2`) have −4e^2, where NegQ is true in both.
    - e1463's discriminant 4B^2e^3(2ABd−A^2e) depends on Rubi's term order (not determined).
  - **P0.** Verified in 0.6–8.3 s via 1_4_1_r25 (14), 1_4_1_r34 (7), 1_1_2_9_r16 (5), …; no r27
    fire.
  - **Timing and arms.** 100 s re-check: timeout 45. All arms timeout.
  - **Sample.** 12 traces by hand, all 45 mechanically.
  — follows from: not determined from the traces (which change moves the route onto r27, and where
  the time goes after it)
  [defect: negQ] (42, inferred) [defect: none seen] (e1464, e1466) (e1463 not determined)

- class 1 g8 (44 entries, deterministic, final timeout top=1_1_3_1_r14):
  - **Rule.** 1_1_3_1_r14 is Rubi `1/(a+b x^n) /; IGtQ[(n-3)/2,0] && NegQ[a/b]` (PosQ twin r13). Its
    cond is `is((n - 3)/2 > 0) and %mr_negQ(a/b)`.
  - **Fire lists.** 42 of 44 read 1_2_1_1_r12, 1_2_1_2_r3, 1_2_1_2_r9, 1_1_1_1_r3 (+ r5 or
    1_1_2_1_r13), then r14. These are the Module's `u = Int[…cos((2k−1)π/n)…]` with symbolic k.
    The group mixes three timing shapes:
  - **12 top-level `1/(a+b x^n)`** (1.1.3.2 e653, e707, e708, e1274, e1324, e1350, e1376, e1445,
    e1468, e1483; 1.2.2.3 e141; 1.3.1 e397): VERIFY-TIMEOUT (r14 is the top rule).
    - n = 4/6/8 in 10 of them: (n−3)/2 = 1/2, 3/2 or 5/2 (IGT).
    - Symbolic a/b (`a/c`, `2(a+b)`) in 7: NEGQ.
    - e1445 `1/(a-b*x^7)` meets Rubi's conditions.
    - 120 s: timeout 11; e1483's record reads error 26.9 s.
  - **22 in 1.2.2.2** `(d x)^(k/2)/(a^2+2ab x^2+b^2 x^4)^j`: r14 is nested. At 120 s the top-level
    1_2_2_2_r6 (18) or r35 (4) has fired, so rubi returned and verification does not finish.
  - **10 others** (1.1.1.2 e1729, e1774, e1800; 1.1.1.3 e876, e877, e892; 1.1.3.2 e1219; 1.1.3.3
    e95, e108; 1.3.1 e113): r14 is nested and still the last fire at 120 s (MID-CHAIN, weak).
    e1774/e1800 end in error at 97–98 s (top 1_1_3_1_r52).
  - **P0.** Verified in 0.2–8.4 s via 1_3_4_r9 (22), 1_4_1_r23 (7), 1_2_2_1_r7 (5), …; no r14 fire.
  - **Timing and arms.**
    - 100 s re-check: timeout 41, error 2.
    - r2: timeout 43, error 1.
    - r3: timeout 40, deferred 2, verified 1, error 1.
    - r4: timeout 42, verified 1, error 1.
  - **Sample.** All 44 integrands by hand; 11 traces.
  — follows from: not determined from the traces which change reaches r14 (P0 no fire); on the
  top-level entries its acceptance is IGT/NEGQ; the cost is verification (34) or a non-returning
  chain (10)
  [defect: IGtQ] (10, top-level) [defect: negQ] (7, top-level; 6 of them also IGtQ) [defect: none
  seen] (e1445) (32 nested entries: binding not traced)

- class 1 g9 (43 entries, deterministic, final deferred top=1_1_2_2_r5): EXPAND-NOUN.
  - **Rule.** Rubi 1.1.2.2 r5 is `(c.x)^m.(a+b.x^2)^p. → ExpandIntegrand /; IGtQ[p,0]`; its cond is
    `is(p > 0)`.
  - **Integrands.** All in 1.1.2.2, with p = 1/2, 3/2, 1/3, 4/3, 1/4, 3/4, 1/6 (IGT).
  - **Final core.** r5 alone at 0.1–0.4 s.
  - **P0.** 1_3_4_r1 27, 1_1_2_2_r6 10, 1_1_2_11_r4 6, at 0.7–2.9 s; no r5 fire.
  - **Sample and arms.** 15 entries by hand; deferred in all arms.
  — follows from: the substrate binding reaches r5 (P0 no fire) and exposes the IGtQ translation;
  the EXPAND-NOUN step is not determined from the traces
  [defect: IGtQ] (43)

- class 1 g10 (41 entries, deterministic, final deferred top=1_1_2_8_r7): EXPAND-NOUN.
  - **Rule.** Rubi 1.1.2.8 r7 is `(e.x)^m.(c+d.x)^n.(a+b.x^2)^p. → ExpandIntegrand /; IGtQ[p,0]`;
    its cond is `is(p > 0)`.
  - **Integrands.** 1.2.1.4 (29) and 1.2.1.3 (12), e.g. `sqrt(d^2-e^2*x^2)/(x^2*(d+e*x))`, with
    p = 1/2 … 5/2. The 1.1.2.8 rules are ahead of 1.2.1.x in table order.
  - **Final core.** r7 alone at 0.3–0.5 s.
  - **P0.** 1_1_2_8_r51 13, 1_4_2_r23 11, 1_1_2_8_r37 9, r106 4, r42 3, 1_4_2_r25 1; no r7 fire.
  - **Sample and arms.** 14 entries by hand; deferred in all arms.
  — follows from: the substrate binding reaches r7 (P0 no fire) and exposes the IGtQ translation;
  the EXPAND-NOUN step is not determined from the traces
  [defect: IGtQ] (41)

- class 1 g11 (37 entries, deterministic, final deferred top=1_1_1_2_r12): EXPAND-NOUN.
  - **Rule.** Rubi 1.1.1.2 r12 is `(a.+b.x)^m.(c.+d.x)^n. → ExpandIntegrand /; IGtQ[m,0] && (…)`;
    its cond is `is(m > 0)`.
  - **Integrands.** 1.1.1.2 (35) and 1.1.1.3 (2). Every positive exponent is non-integer, e.g.
    `(a-%i*a*x)^(7/4)/(a+%i*a*x)^(1/4)` and `(a+b*x)^(1/3)/(c+d*x)^(1/3)` (IGT).
  - **Final core.** r12 alone at 0.1–0.2 s.
  - **P0.** 1_1_1_2_r19 27, r39 5, r18 4, 1_3_4_r1 1; no r12 fire.
  - **Arms.** r3 verifies e1888 `(1-x)^(7/3)*(1+x)^n` in 0.3 s; the other entries are deferred in
    all arms.
  - **Code comment.** `mr_top`'s comment cites this rule's identity repl as a seen-guard case.
  - **Sample.** 13 entries by hand.
  — follows from: the substrate binding reaches r12 (P0 no fire) and exposes the IGtQ translation;
  e1888 condition retry; the EXPAND-NOUN step is not determined from the traces
  [defect: IGtQ] (37)

- class 1 g12 (32 entries, deterministic, final deferred top=1_1_2_4_r21): EXPAND-NOUN.
  - **Rule.** Rubi 1.1.2.4 r21 is `(e.x)^m.(a+b.x^2)^p.(c+d.x^2)^q. → ExpandIntegrand
    /; IGtQ[p,0] && IGtQ[q,0]`; its cond is `is(p > 0) and is(q > 0)`.
  - **Integrands.** Every entry has p or q equal to 1/2 or 3/2, e.g.
    `(e*x)^(3/2)*(A+B*x^2)*sqrt(a+b*x^2)` (IGT).
  - **Final core.** r21 alone at 0.2–0.5 s.
  - **P0.** 1_3_4_r3 13, 1_4_1_r34 7, 1_1_2_4_r29 6, r25 6; no r21 fire.
  - **Sample and arms.** 11 entries by hand; deferred in all arms.
  — follows from: the substrate binding reaches r21 (P0 no fire) and exposes the IGtQ translation;
  the EXPAND-NOUN step is not determined from the traces
  [defect: IGtQ] (32)

- class 1 g13 (29 entries, deterministic, final deferred top=1_1_3_4_r13): EXPAND-NOUN.
  - **Rule.** Rubi 1.1.3.4 r13 is `(e.x)^m.(a+b.x^n)^p.(c+d.x^n)^q. → ExpandIntegrand
    /; IGtQ[p,0] && IGtQ[q,0]`; its cond is `is(p > 0) and is(q > 0)`.
  - **Integrands.** `(e*x)^k (A+B*x^3)(a+b*x^3)^p` with p = 1/2 … 5/2 (IGT).
  - **Final core.** r13 alone at 0.2–0.4 s.
  - **P0.** 1_1_3_8_r30 27 (after 9_1_r16 or 1_4_1_r34), 1_4_1_r34 2; no r13 fire.
  - **Sample and arms.** 10 entries by hand; deferred in all arms.
  — follows from: the substrate binding reaches r13 (P0 no fire) and exposes the IGtQ translation;
  the EXPAND-NOUN step is not determined from the traces
  [defect: IGtQ] (29)

- class 1 g14 (28 entries, deterministic, final deferred top=1_1_3_2_r12): EXPAND-NOUN.
  - **Rule.** Rubi 1.1.3.2 r12 is `(c.x)^m.(a+b.x^n)^p. → ExpandIntegrand /; IGtQ[p,0]`; its cond is
    `is(p > 0)`.
  - **Integrands.** `x^k (a±b*x^4)^p` and `(c*x)^m (a+b*x^3)^p` with p = 1/4, 3/4, 5/4, 1/3, 4/3
    (IGT).
  - **Final core.** r12 alone at 0.1–0.2 s.
  - **P0.** 1_2_2_2_r8 21, r1 4, 1_3_4_r1 3; no r12 fire.
  - **Sample and arms.** 14 entries by hand; deferred in all arms.
  — follows from: the substrate binding reaches r12 (P0 no fire) and exposes the IGtQ translation;
  the EXPAND-NOUN step is not determined from the traces
  [defect: IGtQ] (28)

- class 1 g15 (26 entries, deterministic, final deferred top=1_1_2_9_r14): EXPAND-NOUN.
  - **Rule.** Rubi 1.1.2.9 r14 is `(d.+e.x)^m.(f.+g.x)^n.(a+c.x^2)^p. → ExpandIntegrand
    /; IGtQ[p,0]`; its cond is `is(p > 0)`.
  - **Integrands.** 1.2.1.3 (23) and 1.2.1.4 (3), e.g. `(5-x)*sqrt(2+3*x^2)/(3+2*x)^3`, with
    p = 1/2 … 5/2 (IGT).
  - **Final core.** r14 alone at 0.2–0.4 s.
  - **P0.**
    - 1_2_1_9_r22 20, 1_1_2_9_r49 2, r44 1, r42 1.
    - e629 and e630 (1.2.1.4) have P0 top = the same r14, with nested 1_4_1_r7, as in g1's
      8 entries.
  - **Sample and arms.** 13 entries by hand; deferred in all arms.
  — follows from: the substrate binding reaches r14 (24 entries; P0 no fire) and exposes the IGtQ
  translation; the EXPAND-NOUN step (all 26) is not determined from the traces
  [defect: IGtQ] (26)

- class 1 g16 (24 entries, deterministic, final deferred top=1_2_1_9b_r6): EXPAND-NOUN.
  - **Rule.** Rubi 1.2.1.9 r6 is `(d+e.x)^m. Pq (a+c.x^2)^p. → ExpandIntegrand
    /; PolyQ[Pq,x] && IGtQ[p,-2]`; its cond is `is(p > -2)`.
  - **Integrands.** 1.2.1.9 (23) and 1.3.2 e675, with p = ±1/2, 3/2 (IGT).
  - **Final core.** r6 alone at 1.5–1.8 s.
  - **P0.**
    - 22 entries: the b≠0 twin 1_2_1_9b_r5, whose literal `(a + b*x+ c*x^2)^p` bound `a+c*x^2`
      only with b = 0 (DEG), with nested 1_4_1_r7.
    - 2 entries: 1_2_2_8_r18.
  - **Arms.** r3: verified 19 (0.6–2.7 s), deferred 5. r2/r4: deferred.
  - **Sample.** 12 entries by hand.
  — follows from: faithful Optional binding (P0's b=0 binding lost) with condition retry
  (19 of 24); the EXPAND-NOUN step is not determined from the traces
  [defect: IGtQ] (24)

- class 1 g17 (19 entries, deterministic, final deferred top=1_1_3_2_r17): NEQ-BANG.
  - **Integrands.** All in 1.1.3.2: `x^m (a+b x^n)^p` with (m, n) ∈ {(1,3), (2,4), (−2,4), (4,6),
    (2,8)}. So k = gcd(m+1, n) = 1 in all 19.
  - **Rubi.** r17 is `With[{k=GCD[m+1,n]}, 1/k Subst[Int[x^((m+1)/k-1)(a+b x^(n/k))^p], x, x^k]
    /; k != 1] /; FreeQ[{a,b,p},x] && IGtQ[n,0] && IntegerQ[m]`, so Rubi rejects every one of them.
  - **Generated cond.** It carries the moved inner test (INNER), `block([k], k : gcd(m + 1, n),
    is(k != 1) = true)`. The fire shows the cond accepted with k = 1.
  - **Answer.** The repl then re-dispatches the identical integrand. The seen guard's
    `integrate(f, x)` gives the top-level noun (nfires=1, 0.1–0.3 s).
  - **P0.** P0 had the same `is(k != 1) = true` in the repl. Its top was 1_1_3_2_r45 … r55 / r29,
    and it has no r17 fire.
  - **Sample and arms.** All 19 by hand; deferred in all arms.
  — follows from: faithful Optional binding (bare `x` as `x^m.`; P0 no fire) with the inner
  condition moved into cond, exposing the `!=` translation (a third pre-existing translation defect)
  [defect: none seen] (19; IGtQ[n,0] has integer n and there is no NegQ; the `!=` defect applies to
  all 19)

## Evidence gaps (part A)

- **EXPAND-NOUN, 530 entries** (g1, g4, g5, g9–g16).
  - **The unresolved step.** The traces do not show why the ExpandIntegrand rewrite produces no
    nested fire: seen guard or no nested rule.
  - **Against the seen-guard reading.** The utilities, the seen guard and 1_4_1_r7's cond are
    unchanged since P0. The same top rule dispatched its rewrite on P0 in g1 ×8, g5 ×61 and g15 ×2.
  - **Retry evidence.** For g5 and g16 the r3 arm shows the substrate accepts a non-first binding,
    but which binding is not traced.
  - **What would settle it.** A probe that prints the seen-guard hit and the accepted mm list.
- **g2 (99).** No fire is flushed at 30 s or 120 s, so which rule's binding enumeration consumes the
  retry cost is unknown. The r3 arm only shows that retry is required (82 entries).
- **g3 (80).** Misfires and declines are not captured, so why Rubi's own routes do not answer on the
  substrate is unknown. That includes 1_1_3_2_r12 on `(a+b*x^k)/x`, where p=1 meets Rubi's
  conditions. Four of the five DEG readings rest on rule-text comparison with Rubi's LHS. The fifth,
  1_1_4_1_r9, rests also on defmatch's algebraic matching.
- **g6, g7, g8.** The traces do not show which substrate change first reaches 1_1_3_2_r13,
  1_2_2_3_r27 and 1_1_3_1_r14 (P0 never fired them).
  - The g7 NegQ tags are inferred from Rubi's √-substitution discriminant; the nested integrand is
    not traced.
  - The IGtQ/NegQ bindings of g8's 32 nested entries are not traced.
  - Error kinds are not recorded: g6 record errors ×4 and e1495 at 120 s; g8 e1483 (record),
    e1774/e1800 (120 s).
- **g17.** The `is(k! = 1)` reading of `!=` comes from `nparse.lisp` (build
  `branch_5_50_base_84_g4204fb669`), not from a measurement. The k = 1 fires are consistent with it.
  Whether P0's literal bound r17 is not traced.
- **Exponent checks.** The IGtQ tag counts rest on a regex over the corpus integrand text: the
  exponent of the factor the rule slot binds. Hand checks agreed on every sampled entry.
- **Answers not recorded.** Probe 10 keeps class, wall and fire names only.

## Defect tally (part A)

Every count below comes from checking all entries of its group mechanically (fire lists and
integrands for all 864 entries), not from extrapolating a sample. "Inferred" marks tags that rest on
an untraced nested integrand.

- **[defect: IGtQ]: 583 entries.**
  - g1 144, g4 62, g5 60, g6 47, g8 10, g9 43, g10 41, g11 37, g12 32, g13 29, g14 28, g15 26,
    g16 24.
  - The IGtQ family here includes ILtQ (g6 r13) and IGtQ on computed arguments.
- **[defect: negQ]: 81 entries.**
  - g6 32, g7 42 (inferred), g8 7.
  - 38 of these carry both tags (g6 32, g8 6).
  - Entries with at least one of the two tags: 626 (42 of them inferred).
- **[defect: none seen]: 205 entries.**
  - g1 3 (e809, e810, e922), g5 1 (e370), g7 2 (e1464, e1466), g8 1 (e1445), g17 19.
  - g2 99 and g3 80 have no final-core fire to inspect.
- **Not determined: 33 entries.** g7 1 (e1463); g8 32 nested entries.
- **[collapse-family]: 1 entry** (g1 e810; 9_1_r28 in P0's fires only). No other g1–g17 entry has
  9_1_r27 or 9_1_r28 in either fire list.
- **Other pre-existing translation defect (`!=` → `is(k! = 1)`): 19 entries** (g17).
