> Task 4 Step 5 mechanism lines for probe 10's groups — class 1, groups g18–g80.
> Reads: probes/matcher/10-p5-attribution.class1.summary.out (groups g18–g80).
> Written 2026-09-14 by read-only analysis of the committed probe-10 outputs (commit 295effa); claims marked 'inferred' or 'not determined' are not measured.

# Task 4 Step 5 — mechanism lines, class 1, part B (groups g18–g80)

Inputs: `probes/matcher/10-p5-attribution.class1.summary.out` lines 2630–4357, the raw runs
`…class1-{final30,p0,final120,newerror}.out`, the arm records `test/corpus_class1.p5-run{2,3,4}.out`
(r2 mr_flat_wide=true, r3 mr_cond_retry=false, r4 mr_model_flags=false), rule files
`rules/class1/*.mac` on the final tree and at `0a6664c` (P0 literals), Rubi source under
`reference/rubi/`. Read-only analysis, 2026-09-14, HEAD 7726072. Evidence conventions (trace
semantics, "top", answers not recorded, arms, table order, timeout reading) are those of
`task4-mechanisms-class2-3.md`.

Class-wide fire counts quoted as "P0 n / F m" are the number of entries (of the 1833 re-run)
whose fire list contains the rule on the P0 core / the final core at 30 s.

## Families (class 1, part B)

Reused from classes 2–3: OPT, DEG, NOUN, IGT, NEGQ, RETRY, VERIFY-TIMEOUT. New here:

- **RT-SUM (IGT on the Rt/Sum partial-fraction rules).** 1_1_3_1_r13/r14 (`1/(a+b x^n)`, Rubi
  `IGtQ[(n-3)/2,0] && PosQ/NegQ[a/b]`) and 1_1_3_2_r35/r36 (`x^m/(a+b x^n)`, Rubi
  `IGtQ[(n-1)/2,0] && IGtQ[m,0] && LtQ[m,n-1] && PosQ/NegQ[a/b]`).
  - The generated conds read `is((n-3)/2 > 0)` / `is((n-1)/2 > 0) and is(m > 0)`. They accept
    even n (4, 6 or 8 in every part-B entry after the rules' substitutions) and non-integer m.
    Rubi needs n odd.
  - Class-wide: r13 P0 0 / F 27, r14 P0 0 / F 135, r35 P0 0 / F 22, r36 P0 0 / F 93. Whether the
    P0 literals (`1/(a+b*x^n)`, `x^m/(a+b*x^n)`) never bound or their repls failed is not traced.
    The conds are byte-identical apart from P0's added `%mr_neQ(n,0)`.
  - The repl builds `mr_sum(u, k, 1, (n-1)/2)`. With numeric bounds `mr_sum` sums
    k = ceiling(1)..floor((n-1)/2) (`maxima_rubi_utils.mac:53-69`, unchanged since 0a6664c), so for
    n = 4 only k = 1 is kept: a wrong partial-fraction decomposition.
  - The repl's sub-integrals are the recurring fire chain `1_2_1_1_r12, 1_2_1_2_r3, 1_2_1_2_r9`
    (the cos-coefficient quadratic `u`) and `1_1_1_1_r3/r5` (`1/(r∓s x)`), often with 1_1_2_1_r13.
    Class-wide 1_2_1_1_r12 is P0 10 / F 407 and 1_1_1_1_r5 P0 0 / F 142.
  - For r14/r36 on a bare-symbol ratio `a/b`, NegQ reads true (NEGQ), where Rubi's `PosAux` gives
    PosQ true. That is what selects r14/r36 over r13/r35 for symbolic coefficients.
- **MID-CHAIN.** A timeout whose 30 s (and 120 s) fire list ends in a nested rule, not the
  top-level one: rubi had not returned, so the cap went to integration, not verification (the
  opposite of VERIFY-TIMEOUT). Stdout loss at the kill makes this weaker evidence than a present
  top-level fire.
- **CATCH-1 (catch-all ahead of Rubi's rule).** A class-1 `Unintegrable` catch-all of an earlier
  table section binds through Optional defaults and answers before the later-section rule the P0
  route used: 1_2_1_3_r112, 1_2_2_3_r99, 1_2_2_4_r96, 1_2_2_6_r9, 1_2_2_7_r42 (all P0 0 fires
  class-wide). The P0 literals had no defaults, so P0 walked on.
- **EXPAND-NOUN.** An `ExpandIntegrand` rule answers alone (nfires=1) with a top-level noun
  (deferred), the same shape as class 2 g1 / class 3 g20. Where the rule's IGtQ/ILtQ condition
  is translated and the power is non-integer, the expansion is plausibly a no-op that the seen
  guard stops. That is not traced.

Defect tags follow the controller's definitions, checked per entry against the integrand:

- `IGtQ` is tagged only for an accepting positive-context IGtQ/ILtQ in a fired rule. A negated
  one (`Not[IGtQ…]`) cannot over-accept.
- `negQ` is tagged only where the NegQ argument is a bare-symbol ratio/sum/product, where
  Rubi's `PosAux` is True. NegQ on computed arguments (`b^2-4ac`, a substitution's `-a`) is not
  tagged; see gaps.
- A group line gives per-entry counts when the tag does not cover the whole group.

## Group lines g18–g80

- class 1 g18 (19 entries, deterministic, final timeout top=1_1_3_2_r36): RT-SUM +
  VERIFY-TIMEOUT. `x^m/(a+c x^n)`, n = 4/6/8. 1_1_3_2_r36 is the top-level rule on the substrate
  and its repl's sub-integral chain precedes it in every list.
  - **P0:** 1_2_2_2_r1 (subst x^2), 1_2_2_2_r23, 1_4_1_r34 or 1_3_4_r1, verified 0.3–5.6 s.
  - **Final 120 s:** timeout 13, unverified e1348 72.9 s / e1349 119.9 s. e1377 and e1471–e1473
    are record error 12.9–27.1 s; the newerror probe reads timeout 30.2 s, and error kind is not
    recorded.
  - **Arms:** timeout in r2/r3/r4 (the four errors are error in all arms); e646 is r4 unverified
    1.4 s.
  — follows from: the IGtQ translation, reachable once the rule binds/returns on the substrate
  (P0 0 fires class-wide); no switch [defect: IGtQ 19, negQ 12 (the symbolic a/c, a/b, 2a+2b
  entries; e1347–e1349, e1377, e1471–e1473 have a/b = -1)]
- class 1 g19 (18 entries, deterministic, final timeout top=1_1_2_2_r6): Both cores put
  1_1_2_2_r6 (`x^m (a+bx^2)^p`, Rubi `ILtQ[Simplify[(m+1)/2+p+1],0]`) at top. It accepts
  (m+1)/2+p+1 = -3/4, -1/4, -1/3 … on both cores (IGT, present at P0 too).
  - **e294–e335 (12):** P0 nested 9_1_r9 / 1_2_2_5_r3 / 1_4_1_r34 (or the 1_1_2_1_r11 chain). On
    the substrate the nested integral goes through 1_1_2_2_r27 (subst k=2), then RT-SUM (r14 for
    a+bx^2, r13 for 1+x^2) and 1_1_3_1_r13/r14, 1_1_2_2_r13. Top-level fire present → VERIFY-TIMEOUT.
    120 s timeout; all arms timeout.
  - **e909–e911, e1029–e1031 (6):** identical fire lists on both cores
    (1_1_3_1_r32/1_1_2_1_r26 or 1_1_3_1_r31/1_1_2_1_r28/r30). P0 verified 0.2–0.4 s; final
    timeout at 30 s and 120 s. r4 (model_flags=false) verifies in 0.1–0.4 s, r2/r3 time out.
  — follows from: RT-SUM (12); the model flags (6) [defect: IGtQ 18 (r6's ILtQ in all 18, RT-SUM
  in 12), negQ 6 (e294–e310)]
- class 1 g20 (18 entries, deterministic, final timeout top=1_2_2_2_r6): VERIFY-TIMEOUT on
  Rubi's route.
  - **Final:** 1_2_2_2_r6 (the `EqQ[b^2-4ac,0]` perfect-square rule; P0 0 / F 18) answers
    `(dx)^m/(a^2+2abx^2+b^2x^4)^k` at top level. Nested: 1_1_3_2_r17, 1_1_2_2_r27,
    1_1_2_2_r23/r25/r13/r7. The corpus answers carry the matching `(a+bx^2)/sqrt(…)` factor.
  - **P0:** 1_3_3_r10, 1_4_1_r34, top 1_3_4_r9, verified 4.2–8.4 s.
  - **Timing and arms:** the top-level fire is in the 30 s list; 120 s timeout 18. r4 verifies
    e774/e776 in 1.6 s; the others time out in all arms.
  — follows from: the P0 literal `(d*x)^m*(a+b*x^2+c*x^4)^p` never completing 1_2_2_2_r6 (why is
  not traced) versus the substrate binding it; e774/e776 the model flags [defect: none seen
  (1_1_2_2_r7's ILtQ binding inside the chain is not determinable)]
- class 1 g21 (17 entries, deterministic, final deferred top=1_1_1_3_r55): EXPAND-NOUN + IGT.
  - **Rule and binding:** 1_1_1_3_r55 (`(a.+bx)^m (c.+dx)^n (e.+fx)^p` → ExpandIntegrand; Rubi
    `IGtQ[m,0] || ILtQ[m,0] && ILtQ[n,0]`, cond `is(m > 0) or is(m < 0) and is(n < 0)`) accepts
    m = 5/2, 3/2, 1/2, 1/3 or m = n = -1/2. It answers alone with a top-level noun; e2625/e2626
    get 1_1_1_4_r47 normalization first.
  - **P0:** 1_1_1_6_r7/r5 (13 entries); 1_1_1_4_r38 (e2288, e3164, e3165, where P0 also fired
    r55 but finished with r38); 1_1_1_4_r28/r29 (e2625/e2626).
  - **Arms:** r3 (cond_retry=false) verified 7 (e938, e939, e951, e952, e957, e2288, e3161),
    unverified 2 (e956, e3156), deferred 8. r2/r4 deferred.
  — follows from: condition retry exposing the IGtQ/ILtQ translation of r55 (a retried binding
  accepts; r3 restores an answer for 9); for the other 8 the moving change is not determined
  [defect: IGtQ 17]
- class 1 g22 (17 entries, deterministic, final timeout top=1_2_2_2_r8): Both cores run
  1_2_2_2_r8 (subst x^2).
  - **Nested chain.** P0: 1_2_1_6_r1 (`Pq (a+bx+cx^2)^p` expansion, P0 83 / F 1) or nothing.
    Substrate: 1_2_1_2_r9/r13/r97/r80 → 1_2_1_1_r12 → 1_1_2_1_r13 (atanh), Rubi's route (corpus
    atanh((b+2cx^2)/sqrt(b^2-4ac))). 1.2.1.2 is ahead of 1.2.1.6; the substrate binds `d_.`=0 in
    `(d.+e.x)/(a+bx+cx^2)`, while the P0 literal is `(d + e*x)/(a+ b*x+ c*x^2)`.
  - **1.2.2.2 (10):** the top-level fire is in the 30 s list → VERIFY-TIMEOUT. 120 s: timeout 9,
    error e889 76.3 s. All arms timeout; e850 is record error 28.5 s, error in r2/r4.
  - **1.2.3.2 (7; P0 top 1_4_2_r24, verified 0.6–1.0 s):** the 30 s list has only the nested
    1_2_2_2_r8, with no top-level fire. The record reads error 12.5–18.3 s; the newerror probe
    error 14.6–26.7 s (e619, e635, e644, e658) or timeout 30.1 s (e617, e642). Error in all arms,
    so the process dies during integration. The error kind is not recorded.
  — follows from: faithful Optional binding (Rubi's route); the cost and the deaths are not
  attributed to a switch [defect: none seen]
- class 1 g23 (16 entries, deterministic, final deferred top=1_2_2_3_r11): EXPAND-NOUN + IGT.
  1_2_2_3_r11 (Rubi `IGtQ[p,0] && IGtQ[q,-2]`, cond `is(p > 0) and is(q > -2)`) accepts p = 1/2,
  3/2 on `(d+ex^2)^q sqrt(a+bx^2+cx^4)` and answers alone with a top-level noun. It has P0 0
  fires class-wide; the P0 literal `(d+e*x^2)^q*(…)^p` has no `q_.` default for a bare factor
  (OPT). P0 routes: 1_2_2_3_r34 (p>0 fractional) and 1_2_2_3_r66, Rubi's rules for half-integer
  p. All arms deferred. — follows from: faithful Optional binding exposing the IGtQ translation
  [defect: IGtQ 16]
- class 1 g24 (15 entries, deterministic, final deferred top=1_2_2_4_r19): The g23 shape with
  `(f x)^m`: 1_2_2_4_r19 (IGtQ[p,0] && IGtQ[q,-2]; P0 0) accepts p = 1/2, 3/2 and answers alone
  with a noun. P0 routes: 1_2_2_4_r31 (e154–e168) and 1_2_2_6_r3 (e204–e226). All arms deferred.
  — follows from: faithful Optional binding exposing the IGtQ translation [defect: IGtQ 15]
- class 1 g25 (15 entries, deterministic, final timeout top=1_1_1_2_r11): 1_1_1_2_r11 (Rubi
  `ILtQ[m,-1]`, cond `is(m < -1)`).
  - **1.1.1.2, 11 entries** `1/((a+bx)^(k/3|k/4)(c+dx)^(j/3|j/4))`: r11 accepts m = -4/3 … -11/4
    (IGT) as the top-level rule, after 1_1_3_2_r17 (most entries), 1_2_1_1_r17 and 1_1_1_2_r31.
    - VERIFY-TIMEOUT: the top fire is in the 30 s list; 120 s timeout.
    - P0: 1_1_1_2_r39 at top, and P0 itself finished with r11 in e1626/e1627/e1727/e1728.
    - Arms: r4 verified e1598–e1600, e1626, e1627 (0.3 s); r3 verified e1626, e1627, e1727,
      e1728 (0.2 s); e1703/e1704/e1715/e1716 time out in all arms.
  - **1.1.3.2 e1114/e1115/e1238/e1239** `1/(x^k (a±bx^4)^(3/4))` (MID-CHAIN): the list ends in the
    nested r11 at 30 s and at 120 s, after RT-SUM r14 and 1_1_1_2_r32. P0: 1_1_1_2_r13,
    1_1_2_2_r4, top 1_2_2_2_r8. r3 verifies e1238/e1239 in 0.1 s.
  — follows from: the ILtQ translation (1.1.1.2) and RT-SUM (1.1.3.2). The model flags (r4, 5
  entries) and condition retry (r3, 6 entries) each restore a subset; the change that moves the
  route for the 4 entries no arm verifies is not determined [defect: IGtQ 15]
- class 1 g26 (15 entries, deterministic, final timeout top=1_1_3_1_r52): MID-CHAIN + RT-SUM.
  - **Fires:** 1_1_3_1_r52 (`(a+bx^n)^p` subst) is nested in every entry: the top-level forms are
    1.1.1.2/1.1.1.3/1.1.2.x/1.1.3.2 binomials. No top-level fire at 30 s or 120 s (120 s: timeout
    14, error e1826 96.9 s).
  - **Chain:** r52's sub-integral `1/(1-b x^4)` (or x^6) runs RT-SUM r13/r14.
  - **P0:** 1_1_1_2_r32 / r10, 1_1_1_6_r7, 1_3_4_r1, 1_1_2_4_r23/r28/r29, 1_2_2_1_r18; verified
    0.6–3.5 s.
  - **Arms:** r3 reads deferred for e1213/e1224/e1718 (0.1–0.3 s); otherwise timeout.
  — follows from: RT-SUM in the nested chain; why the top level does not return by 120 s is not
  determined [defect: IGtQ 15]
- class 1 g27 (15 entries, deterministic, final unverified top=1_2_1_2_r119): The substrate
  answers `(ade+(cd^2+ae^2)x+cdex^2)^p/(d+ex)^m` with 1_2_1_2_r119. 1.2.1.2 is ahead of 1.3.3.
  - **Condition.** Rubi's r119 needs `NeQ[c d^2-b d e+a e^2,0]`. That expression is identically 0
    here (the quadratic has d+ex as a factor), so why the cond accepted is not traced.
  - **Nested:** 1_4_1_r18 (6); 1_1_2_3_r48/r42, 1_2_1_2_r93/r109, 1_2_1_3_r89, 9_1_r8,
    1_2_1_9b_r32, 1_4_1_r10 (e2033); 1_2_1_9b_r5/r27 + 1_4_1_r18 (e2034, e2043); 1_4_2_r15 +
    1_2_1_9b_r27 (6).
  - **P0:** 1_4_2_r25 or 1_1_1_3_r55, then top 1_3_3_r6 (common-factor cancel), verified 1.0–1.9 s.
  - **Arms:** all unverified. The answer is not recorded.
  — follows from: not determined from the traces [defect: IGtQ 2 (e2034, e2043: 1_2_1_9b_r5 with
  p = 1/2); none seen 13]
- class 1 g28 (14 entries, deterministic, final timeout top=1_1_3_4_r22): RT-SUM + VERIFY-TIMEOUT.
  - **Final:** 1_1_3_4_r22 (`(ex)^m (a+bx^n)^p (c+dx^n)`, P0 0 / F 14) is the top-level rule on
    `x^(k/2)(A+Bx^3)/(a+bx^3)^j`. Nested: 1_1_3_2_r63/r30/r13/r71 (subst k=2 → x^6) → RT-SUM
    r36/r14 (+1_1_3_1_r14 chain).
  - **P0:** 1_4_1_r34 (+1_3_4_r21, 1_1_3_3_r60), verified 1.0–4.1 s.
  - **Arms:** the top fire is in the 30 s list; 120 s timeout 14; all arms timeout.
  — follows from: faithful binding of r22 (P0 literal never fired) + RT-SUM [defect: IGtQ 14,
  negQ 14]
- class 1 g29 (13 entries, deterministic, final timeout top=1_1_3_2_r63): RT-SUM + VERIFY-TIMEOUT.
  - **Final:** 1_1_3_2_r63 (P0 0 / F 16) reduces `x^m/(a+bx^n)` (m > n-1) as the top-level rule.
    The remainder goes to r36 (symbolic or 1-x^k), r35 (2+3x^4, 1+x^k) or r14 (e737).
  - **P0:** 1_2_2_2_r8, 1_3_4_r1, 1_4_1_r34, 1_2_2_2_r22.
  - **Final 120 s:** timeout 8; unverified e1342 73.1 s / e1360 79.8 s. e1469/e1488 are record
    error 22.5/16.8 s (newerror probe timeout 30.2 s); e1359 is record unverified 23.3 s
    (unverified in all arms).
  - **Arms:** e644 r4 unverified 1.5 s; the rest timeout/error as in the record.
  — follows from: the IGtQ translation (RT-SUM) with faithful binding of r63 [defect: IGtQ 13,
  negQ 6 (e644, e736, e737, e1316, e1317, e1449)]
- class 1 g30 (11 entries, deterministic, final deferred top=1_2_1_3_r112): CATCH-1.
  1_2_1_3_r112 (the 1.2.1.3 `Unintegrable` catch-all; P0 0) answers at top level. It binds
  `(ex)^m (A+Bx)/(…)` with `d_.`=0 or `n_.`=1.
  - **Corpus:** the answers (AppellF1 or elementary, 1–5 steps) have no Unintegrable.
  - **P0 routes:** 1_2_1_9b_r5/r25/r32 (1.2.1.9b, later in the table) and 1_4_2_r15.
  - **Arms:** all deferred.
  — follows from: faithful Optional binding (catch-all reached ahead of 1.2.1.9b); why Rubi's own
  route does not answer first is not determined [defect: none seen]
- class 1 g31 (10 entries, deterministic, final deferred top=1_2_2_2_r2): EXPAND-NOUN + IGT.
  1_2_2_2_r2 (Rubi `IGtQ[p,0] && Not[IntegerQ[(m+1)/2]]`, cond `is(p > 0)`) accepts p = 1/2, 3/2
  on `(dx)^m (a+bx^2+cx^4)^p` and answers alone with a noun. P0 route: 1_3_3_r15/r14 → 1_4_1_r34
  → 1_3_4_r9 (or 1_4_2_r19 → 1_3_4_r9), verified 2.7–5.6 s. P0 fired r2 in 6 other entries with
  the same cond, so which binding difference makes it answer here is not traced. All arms
  deferred. — follows from: the IGtQ translation; the enabling binding change is not determined
  [defect: IGtQ 10]
- class 1 g32 (10 entries, deterministic, final deferred top=1_2_2_3_r99): CATCH-1.
  1_2_2_3_r99 (the 1.2.2.3 catch-all; P0 0) answers at top level on perfect-square quartics
  (b^2-4ac = 0: 1±4x^2+4x^4, 1±2x^2+x^4) with p = -1 or 5. 1_2_2_3_r11 is rightly excluded
  (`NeQ[b^2-4ac,0]`). The corpus answers (atan/atanh/rational/polynomial, 2–3 steps) have no
  Unintegrable. P0 routes: 1_3_2_r13, 1_3_3_r4, 1_4_2_r24, 1_2_2_5_r1 (all later in the table).
  All arms deferred. — follows from: faithful Optional binding (`q_.`, `p_.`) [defect: none seen]
- class 1 g33 (10 entries, deterministic, final deferred top=1_2_2_4_r93): EXPAND-NOUN.
  1_2_2_4_r93 (`IGtQ[p,0] || IGtQ[q,0] || IntegersQ[m,q]`) accepts q = 1 as Rubi does on
  `(fx)^m (d+ex^2)/(a+bx^2+cx^4)^(k/2)` and answers alone with a noun (P0 0). P0 route:
  1_2_2_6_r3 → 1_4_1_r7 / 1_1_2_3_r1, verified 5.8–8.8 s. All arms deferred. — follows from:
  faithful Optional binding (`q_.`); why the expansion yields no nested fire is not determined
  [defect: none seen]
- class 1 g34 (10 entries, deterministic, final deferred top=1_4_1_r18): 1_4_1_r18
  (`u Px^p Qx^q` → quotient rewrite; P0 4 / F 109) answers alone with a top-level noun.
  - **Integrands:** `x^2/((a+bx) sqrt(c x^2))`, `b^2 x^m/(b+ax^2)^2`, `A (cx)^m/(a+bx^2)`,
    `(ac+adx+bcx^3+bdx^4)/(a+bx^3)^k`, `P(x)/(a+bx^2+cx^4)^2`.
  - **P0 routes:** manual 9.1 `u*(a*x^n)^m` (P0 id 9_1_r16; e879–e889), 1_1_2_9_r104,
    1_2_1_9b_r5, 1_3_4_r21 (3), 1_2_2_5_r3.
  - **Arms:** r3 verified e881, e889, e58 (0.2–0.4 s) and expected e373; the other 6 are
    deferred in all arms.
  — follows from: faithful Optional binding (`u_.`, `p_.`, `q_.`) with condition retry (r3
  answers 4); for the other 6 not determined [defect: none seen]
- class 1 g35 (10 entries, deterministic, final timeout top=1_1_3_2_r30): RT-SUM + VERIFY-TIMEOUT.
  - **Final:** 1_1_3_2_r30 (P0 0 / F 35; `(cx)^m (a+bx^n)^p`, p<-1) is the top-level rule on
    `x^k/(a+cx^4)^j`, `x^k/(a+bx^6)^2`. Nested: 1_1_3_2_r63/r71 → RT-SUM r36 or r14.
  - **P0:** 1_2_2_2_r8 (after 1_1_2_1_r15, 1_2_1_6_r4), 1_4_1_r34, 1_3_4_r1.
  - **Arms:** 120 s timeout 10. r4 unverified e657/e659/e671 (1.5–1.8 s); the rest timeout.
  — follows from: faithful binding of r30 + the IGtQ translation [defect: IGtQ 10, negQ 10]
- class 1 g36 (10 entries, deterministic, final timeout top=1_2_1_2_r109): Both cores reach
  1_2_1_2_r109 (`(d+ex)^m Q^p`, p>0; P0 20 / F 18).
  - **Nested integrals.** P0 went through 1_2_1_9b_r5 (class-wide P0 186 / F 81). The substrate
    runs 1_2_1_2_r99 → 1_2_1_1_r15 → 1_1_2_1_r13 and 1_2_1_3_r89 (e2337, e857, e924, e313,
    e190); the elliptic 1_1_2_3_r48/r42 + 1_2_1_2_r93 (e2442, e889, e2443, e896, with
    1_2_1_9b_r5/r32, 1_2_1_3_r56 in e2442/e889); or 1_1_3_2_r17, 1_2_1_1_r17, 1_1_1_4_r47,
    1_2_1_2_r133 (e2520).
  - **Timing.** r109 is the top-level rule for the 1.2.1.2/1.2.1.4 entries (VERIFY-TIMEOUT). For
    e924 (P0 top 1_2_2_2_r8), e313 (1_2_2_4_r5) and e190 (1_3_3_r15) it is nested at 30 s and at
    120 s (MID-CHAIN). 120 s timeout 10.
  - **Arms:** r4 verifies e2442 in 7.9 s; otherwise timeout.
  — follows from: not determined which binding change moves the nested chain off P0's
  1_2_1_9b_r5 expansion; e2442 the model flags [defect: IGtQ 2 (e2442, e889: 1_2_1_9b_r5 with
  p = 1/2); none seen 8]
- class 1 g37 (10 entries, deterministic, final timeout top=1_2_2_2_r23): MID-CHAIN.
  - **Top level.** `sqrt(d+ex)/(a+bx+cx^2)`, `sqrt(c+dx)/(a±cx^2)`: P0 finishes with the
    top-level subst rule 1_2_1_2_r74 or 1_1_2_7_r33, with 1_2_2_2_r23 nested (P0 13 / F 10) and
    nothing below it (NOUN). On the substrate the list ends in the nested r23 at 30 s and at 120 s.
  - **Nested chain.** r23's sub-integrals `x^(m-1)/(q∓rx+x^2)` now run 1_2_1_2_r3/r9 →
    1_2_1_1_r12 → 1_1_2_1_r13, after 1_4_1_r18 (e364, e2291, e529, e1619) or 1_1_2_1_r13.
  - **Arms:** all timeout.
  — follows from: faithful Optional binding in r23's sub-integrals (1_2_1_2_r9 `d_.`); why the top
  level does not return by 120 s is not determined [defect: none seen (r23's `NegQ[b^2-4ac]` is on
  a computed argument, not tagged)]
- class 1 g38 (9 entries, deterministic, final deferred top=1_2_2_7_r41): EXPAND-NOUN.
  - **Rule:** 1_2_2_7_r41 (P0 0 / F 9) answers `(A+Bx^2)(d+ex^2)^q/(a+cx^4)^(k/2)` alone with a
    noun. Rubi's conditions hold (PolyQ[Px,x^2], IntegerQ[p+1/2], IntegerQ[q]). Its repl is the
    3-arg `%mr_expandIntegrand(1/sqrt(a+cx^4), …, x)`.
  - **P0:** 9_1_r9, 1_2_2_8_r18, 1_2_2_5_r9/r8 (e1–e10), or 1_4_1_r7, 1_2_2_7_r40 (e12–e14);
    verified 1.7–7.9 s.
  - **Why r41 wins.** 1_2_2_5_r9 (earlier) does not answer on the substrate. Its `Pq_` would have
    to absorb two factors; r2 (flat-wide) is still deferred, so this is not traced.
  - **Arms:** all deferred.
  — follows from: faithful Optional binding (`q_.`); why the expansion yields no nested fire is not
  determined [defect: none seen]
- class 1 g39 (9 entries, deterministic, final timeout top=1_1_2_2_r27): RT-SUM.
  - **1.1.2.2 e292/e317 and 1.3.2 e814** `1/((a+bx^2)√x)`: 1_1_2_2_r27 (subst k=2; P0 4 / F 58) is
    the top-level rule; its `1/(a+bx^4)` runs RT-SUM r14/r13 (VERIFY-TIMEOUT). P0 used
    1_1_2_7_r34, whose literal `1/(sqrt(c+d*x)*(a+b*x^2))` read √x as c=0 (DEG; Rubi `c_` is not
    Optional).
  - **1.2.1.2 e1291–e1326** `(bd+2cdx)^k/(a+bx+cx^2)`: P0 top 1_2_1_4_r24 / 1_3_4_r1. On the
    substrate r27 is nested at 30 s and 120 s (MID-CHAIN); 120 s error for e1291 86.8 s and e1293
    89.9 s.
  - **Arms:** all timeout.
  — follows from: G-1 (P0 degenerate binding lost) + the IGtQ translation [defect: IGtQ 9, negQ 1
  (e292)]
- class 1 g40 (9 entries, deterministic, final timeout top=1_1_3_2_r5): NEGQ.
  - **Rule:** 1_1_3_2_r5 (`x^m (a+bx^n)^p` → `x^(m+np)(b+a x^-n)^p`; Rubi
    `IntegerQ[p] && NegQ[n]`; P0 0 / F 10) is the only fire on `x^m/(a+bx^n)^k` with symbolic n.
    `%mr_negQ(n)` is true for the unknown-sign n, while Rubi's NegQ[n] is False.
  - **Timing.** The top fire is present, so rubi returned; the rewrite's nested dispatch has no
    fire. Timeout at 30 s and 120 s.
  - **P0:** 1_1_3_2_r110 at top, verified 1.3–6.1 s.
  - **Arms:** all timeout.
  — follows from: faithful binding (P0 literal `x^m*(a+b*x^n)^p` never completed r5) exposing the
  `%mr_negQ` reading; where the cap is spent after rubi returns is not determined [defect: negQ 9]
- class 1 g41 (8 entries, deterministic, final deferred top=1_2_1_3_r20): EXPAND-NOUN.
  1_2_1_3_r20 (`(d+ex)^m (f+gx)^n/(a+bx+cx^2)`, `IntegersQ[n]`; P0 0) accepts n = 1…4 as Rubi
  does and answers alone with a noun. P0: 1_2_1_3b_r68 (e1086, e1657, e2643, e2645, e933, after
  1_2_1_9b_r5 / 1_4_1_r7) or 1_2_1_3_r109 (e930–e932); verified 3.0–11.2 s. All arms deferred.
  — follows from: faithful Optional binding (`d_.`, `m_.`, `n_.`); why the expansion yields no
  nested fire is not determined [defect: none seen]
- class 1 g42 (8 entries, deterministic, final deferred top=1_2_2_4_r96): CATCH-1. 1_2_2_4_r96
  (the 1.2.2.4 catch-all; P0 0) answers `(fx)^m (d+ex^2)(1+2x^2+x^4)^5` at top level. The
  quartic is a perfect square, so 1_2_2_4_r19/r93 rightly reject on `NeQ[b^2-4ac,0]`. The corpus
  answers are 3-step polynomials/expansions with no Unintegrable. P0: 1_2_2_5_r1 (e57–e69),
  1_1_1_5_r4 (e63, e73), 1_2_2_6_r3 (e55, e65), all later in the table. All arms deferred.
  — follows from: faithful Optional binding (`m_.`, `q_.`) [defect: none seen]
- class 1 g43 (8 entries, deterministic, final timeout top=1_1_2_2_r23):
  - **e288–e315** `x^(k/2)/(a+bx^2)`: 1_1_2_2_r23 (P0 1 / F 15) is the top-level rule, then
    1_1_2_2_r27 → RT-SUM r14/r13 (VERIFY-TIMEOUT). P0: 9_1_r9, 1_2_2_5_r3, 1_4_1_r34 (+1_1_2_2_r36).
    All arms timeout.
  - **e1025–e1027** `x^k/(a+bx^2)^(5/6)`: 1_1_3_1_r31, 1_1_2_1_r28/r30, top r23. P0: 1_4_2_r6 +
    top 1_1_2_2_r29, verified 0.7 s. r4 verifies in 0.3–0.4 s.
  - **e2382** `√x/(1+x^(2/3))`: r23 nested at 30 s and 120 s (MID-CHAIN; P0 top 1_1_3_2_r110);
    r4 error 14.5 s.
  — follows from: RT-SUM (5); the model flags (e1025–e1027) [defect: IGtQ 5 (e288, e290, e313,
  e315, e2382), negQ 2 (e288, e290); none seen 3]
- class 1 g44 (7 entries, deterministic, final contains-noun top=1_2_1_3_r53): CATCH-1 (NOUN).
  - **Final:** 1_2_1_3_r53 / 1_2_1_3_r56 reduce `(2-5x)x^(k/2)/(2+5x+3x^2)^(j/2)` at top level.
    The `x^m Fx` subst 1_4_1_r34 gives `x^i P(x^2)/(2+5x^2+3x^4)^(j/2)`, and that reaches the
    1.2.2.6 / 1.2.2.7 catch-alls 1_2_2_6_r9 (P0 0 / F 7) or 1_2_2_7_r42 (P0 0 / F 9) → marker.
  - **P0:** under the same 1_4_1_r34, 1_2_2_1_r13, 1_2_2_2_r30, 1_2_2_3_r47, 1_2_2_5_r9/r8;
    verified 3.2–5.2 s.
  - **Corpus:** the answers (6–9 steps, elliptic) have no Unintegrable.
  - **Arms:** all contains-noun (r3 0.9 s).
  — follows from: faithful Optional binding (catch-alls reached ahead of 1.2.2.5) [defect: none
  seen]
- class 1 g45 (7 entries, deterministic, final deferred top=1_1_2_6_r3): EXPAND-NOUN.
  1_1_2_6_r3 (P0 0) answers `(ex)^m (A+Bx^2)(c+dx^2)^k/(a+bx^2)` alone with a noun. Rubi's
  `IGtQ[p,-2] && IGtQ[q,0] && IGtQ[r,0]` holds (p = -1, q/r positive integers). P0: 1_2_1_9b_r5,
  1_1_2_3_r1, 1_4_1_r7, or 1_1_2_6_r9/r12; verified 3.7–28.1 s. r3 reads unverified for e5, e25,
  e12, e19 (0.3–1.0 s); otherwise deferred. — follows from: faithful Optional binding (`g_.`,
  `m_.`); condition retry shapes 4; why the expansion yields no nested fire is not determined
  [defect: none seen]
- class 1 g46 (7 entries, deterministic, final deferred top=1_1_3_2_r112): Both cores put
  1_1_3_2_r112 (subst for fractional `(c x^q)^n`) at top.
  - **Substrate:** the substituted integral binds 1_1_3_2_r12 (ExpandIntegrand; Rubi `IGtQ[p,0]`,
    cond `is(p > 0)` accepts p = 1/2; P0 0 / F 35), and r112 returns a noun.
  - **P0 nested:** 1_1_3_1_r67 / 1_4_1_r23 (e2967), manual 9.1 (e2971, e2972), 1_1_3_2_r110
    (e2989), or nothing (e2973, e2974, e2991: fall-through, NOUN); verified 0.5–5.4 s.
  - **Arms:** r4 verified e2973, e2974, e2991 (0.2 s); otherwise deferred.
  — follows from: Optional binding (`c_.`, `m_.`) exposing the IGtQ translation of 1_1_3_2_r12;
  the model flags for e2973/e2974/e2991 [defect: IGtQ 7]
- class 1 g47 (7 entries, deterministic, final deferred top=1_1_3_7_r46):
  - **Final:** 1_1_3_7_r46 (`Pq (a+b v^n)^p`, subst v; P0 6 / F 7) answers `x^m/(a+bx)^(k/2)` /
    `(cx)^m (a+bx)^n` alone with a top-level noun. How the symbolic power x^m passes
    `%mr_polyPowerQ(Pq, v, n)` is not traced; class 2 g8 has the same top rule.
  - **P0 (e710–e723):** 1_1_1_2_r38/r39 (hypergeometric) on `(a+b*x)^m*(c+d*x)^n`, reading x^m
    as (0+1·x)^m. Rubi's `c_` is not Optional (DEG).
  - **P0 (e731, e752):** 1_1_1_4_r46, 1_3_4_r1.
  - **Arms:** r3 verified e723, e731, e752 (0.6–0.7 s); otherwise deferred.
  — follows from: G-1 (P0 degenerate binding lost) + condition retry (3 of 7) [defect: none seen]
- class 1 g48 (7 entries, deterministic, final timeout top=1_1_3_1_r4): 1_1_3_1_r4 (Rubi
  `ILtQ[Simplify[1/n+p+1],0]`; P0 0 / F 11) accepts 1/n+p+1 = -3/4, -7/4, -5/6 (IGT) on
  `1/(a+cx^4)^k`, `1/(a+bx^6)^2` as the top-level rule.
  - **Chain:** its `1/(a+cx^n)` sub-integral runs RT-SUM r14 (r13 for 2+3x^4).
  - **P0:** 1_2_2_1_r5 at top (after 1_1_2_1_r11 chains, 1_2_2_3_r22/r19, 1_4_1_r23), or
    1_4_1_r23 (e1337); verified 0.7–7.3 s.
  - **Timing and arms:** VERIFY-TIMEOUT; 120 s timeout 7; all arms timeout.
  — follows from: the ILtQ/IGtQ translation (r4 + RT-SUM) [defect: IGtQ 7, negQ 6 (not e703)]
- class 1 g49 (7 entries, deterministic, final timeout top=1_1_3_2_r35): RT-SUM + VERIFY-TIMEOUT
  on numeric positive `x^m/(k+x^n)` (2+3x^4, 1+x^6, 1+x^8). 1_1_3_2_r35 (PosQ legitimately
  true, n even) is the top-level rule.
  - **P0:** 1_2_2_2_r1 (e689), 1_3_4_r1.
  - **Final 120 s:** timeout e689, unverified e1364 89.5 s / e1366 80.9 s, error e1491 73.3 s.
    e1365 is record unverified 22.2 s (all arms unverified). e1490/e1492 are record error
    14.8/18.2 s (newerror probe timeout 30.3/30.2 s).
  - **Arms:** as the record.
  — follows from: the IGtQ translation [defect: IGtQ 7]
- class 1 g50 (7 entries, deterministic, final timeout top=1_2_1_2_r117): 1_2_1_2_r117 (P0 8 /
  F 24).
  - **e2374, e955, e956, e968, e969** (P0 top 1_2_1_6_r1 / 1_2_2_2_r8): the substrate chain is
    1_1_2_1_r13, 1_2_1_1_r15, 1_2_1_2_r15, 9_1_r8, 1_2_1_9b_r32, r117, with 1_2_1_9b_r5 in e2374,
    e955, e968. 1_2_1_9b_r5 is Rubi `IGtQ[p,-2]`, cond `is(p > -2)`, and accepts p = -1/2.
    r117 is top-level for e2374. For the 1.2.2.2 entries it is nested at 30 s, and the top-level
    1_2_2_2_r8 has fired by 120 s: MID-CHAIN, then verification past 120 s.
  - **e2440, e2441:** P0 also finishes with r117 (21.8 / 5.5 s). The chain grows by 1_2_2_1_r17,
    1_2_2_3_r60, 1_1_2_5_r4, 1_2_1_3_r60/r61 (e2440) or 1_2_1_9b_r5 (e2441). r3: e2440
    contains-noun 0.6 s, e2441 verified 1.4 s; r4 verified e2441 12.9 s.
  - **Timing:** 120 s timeout 7.
  — follows from: the IGtQ translation of 1_2_1_9b_r5 (4); condition retry and the model flags
  (e2441); e2440 not determined [defect: IGtQ 4 (e2374, e2441, e955, e968); none seen 3]
- class 1 g51 (7 entries, deterministic, final timeout top=1_2_1_3_r56):
  - **Final:** 1_2_1_3_r56 (P0 7 / F 23) reduces `(d+ex)^m(f+gx)/sqrt(Q)` at top level.
    Nested: 1_2_1_9b_r5 (p = -1/2; e952, e1573, e2466, e902, e169), 1_2_1_9b_r1 (e2209), or
    1_1_2_3_r48, 1_2_1_2_r93, 9_1_r8, 1_2_1_9b_r32, 1_4_1_r18 (e2264).
  - **P0:** 1_2_1_6_r1 at top (e952, e1573, e2466, e2209; class-wide P0 83 / F 1), 1_2_2_6_r2
    (e169), or r56 at top (e2264, e902); verified 0.7–5.3 s.
  - **Timing.** e169 (1.2.2.4) reaches its top-level 1_2_2_4_r9 only by 120 s. 120 s: timeout 6,
    unverified e2264 45.6 s.
  - **Arms:** r2 (flat-wide) verified e952 1.7 s; r3/r4 unverified e2264; r4 verified e902 5.9 s.
  — follows from: faithful Optional binding (1.2.1.3 reductions ahead of P0's 1_2_1_6_r1
  expansion) + the IGtQ translation of 1_2_1_9b_r5; e952 narrow Flat binding (r2 verified),
  e902 the model flags [defect: IGtQ 5; none seen 2]
- class 1 g52 (7 entries, deterministic, final timeout top=1_2_1_3_r89):
  - **Final:** 1_2_1_3_r89 (split by `Not[IGtQ[m,0]]`; P0 1 / F 45) is top-level for e1577,
    e2469, e2500, e2265. Its sub-integrals run 1_2_1_2_r99 → 1_2_1_1_r15 → 1_1_2_1_r13, or the
    elliptic 1_1_2_3_r48/r42 + 1_2_1_2_r93 (e2265).
  - **MID-CHAIN:** for e172, e333 (1.2.2.4) and e108 (1.2.4.2) r89 is nested at 30 s and 120 s.
  - **P0:** 1_2_1_5_r40/r43 (later in the table), 1_2_1_9_r22, 1_2_2_6_r2, 1_2_2_4_r9, 1_4_1_r34;
    verified 2.0–19.0 s.
  - **Timing and arms:** 120 s timeout 6, error e2469 115.2 s. r4 unverified e2265 2.3 s.
  — follows from: faithful Optional binding (`f_.`, `p_.` put 1.2.1.3 ahead of P0's 1.2.1.5
  rules); the cost is not attributed [defect: none seen]
- class 1 g53 (7 entries, deterministic, final timeout top=1_2_2_4_r9): VERIFY-TIMEOUT.
  - **Final:** 1_2_2_4_r9 (subst x^2; P0 7 / F 8) is the top-level rule on
    `x^k(A+Bx^2)/(a+bx^2+cx^4)^j`, ahead of P0's top 1_2_2_6_r2 (the Pq form, later in the table).
    Nested: the 1.2.1.3 reductions 1_2_1_3_r53/r44/r47/r54/r89/r55, 1_2_1_2_r97/r3/r9/r80,
    1_2_1_1_r12/r8, 1_1_2_1_r13.
  - **P0 nested:** 1_2_1_6_r1/r4 expansion; verified 2.5–4.7 s.
  - **Timing and arms:** 120 s timeout 7; all arms timeout.
  — follows from: faithful Optional binding (`m_.`, `q_.`); the cost is verification of the
  reduction-form answer (not recorded) [defect: none seen]
- class 1 g54 (7 entries, deterministic, final unverified top=1_4_1_r7): Both cores split the
  sum with 1_4_1_r7.
  - **Terms on the substrate:** 1_1_3_2_r107 (hypergeometric; Rubi
    `Not[IGtQ[p,0]] && (ILtQ[p,0] || GtQ[a,0])`, cond `… (is(p < 0) or is(a > 0))`; P0 0 / F 10)
    accepts p = -3/2, -1/2 in e2679, e2692 (+9_1_r12), e2690 (+1_4_1_r18) and e234
    (+1_4_1_r43).
  - **e212/e213:** 1_4_1_r18 + RT-SUM r14 on 1/(1-x^4).
  - **e500:** 1_4_1_r18, 1_1_2_2_r39 (p = -2, legit).
  - **P0 terms:** 1_4_2_r25/r6, 1_1_2_1_r13/r10, 1_1_3_1_r24, 1_4_1_r18, 1_1_3_1_r68, 1_4_1_r23,
    manual 9.1, 1_1_3_2_r110; verified 0.7–4.0 s.
  - **Corpus:** four entries are steps=-5 rows (sums whose closed form is the answer), so
    term-wise answers need not combine.
  - **Arms:** r3 expected e500; otherwise unverified in all arms.
  — follows from: faithful binding exposing the ILtQ translation (4) and RT-SUM (2); e500
  condition retry [defect: IGtQ 6 (not e500)]
- class 1 g55 (6 entries, deterministic, final deferred top=1_1_1_3_r16): EXPAND-NOUN + IGT.
  1_1_1_3_r16 (Rubi `IGtQ[n,0] && LtQ[p,-1] && FractionQ[p]`, cond `is(n > 0) …`; P0 2 / F 6)
  accepts n = 1/2, 3/2, 5/2 on `(1-2x)^(k/2)/((2+3x)(3+5x)^(j/2))` and answers alone with a noun.
  P0: 1_1_1_3_r32 (5) or r25 (e2311) after 1_1_1_6_r7 etc.; verified 0.9–3.7 s. All arms
  deferred. — follows from: faithful Optional binding (`c_.`, `n_.`) exposing the IGtQ
  translation [defect: IGtQ 6]
- class 1 g56 (6 entries, deterministic, final deferred top=1_1_1_6_r1):
  - **Final:** 1_1_1_6_r1 (`Px(a+bx)^m(c+dx)^n(e+fx)^p` → `Px(ac+bdx^2)^m(e+fx)^p`; P0 0 / F 6)
    now binds `(A+Bx+Cx^2)/((e+fx)^k sqrt(1-dx) sqrt(1+dx))`.
  - **Sub-integral:** binds 1_2_1_9b_r6 (ExpandIntegrand; Rubi `IGtQ[p,-2]`, cond `is(p > -2)`
    accepts p = -1/2; P0 0 / F 31) → noun → deferred at 5.4–6.7 s.
  - **P0:** 1_1_1_6_r7 / r5, verified 2.8–6.9 s.
  - **Arms:** all deferred (r3 0.6 s).
  — follows from: faithful Optional binding exposing the IGtQ translation of 1_2_1_9b_r6
  [defect: IGtQ 6]
- class 1 g57 (6 entries, deterministic, final deferred top=1_1_2_8_r100): EXPAND-NOUN.
  - **Rule:** 1_1_2_8_r100 (`(ex)^m(c+dx)^n(a+bx^2)^p`; Rubi `ILtQ[p,0]`, cond `is(p < 0)`;
    P0 1 / F 6) answers alone with a noun. It accepts p = -1/2 or -3/2 in e332, e333, e340, e341
    (IGT) and p = -1, -2 in e366, e380 (legit).
  - **P0:** long chains ending in 1_1_2_8_r106 (e332–e341) or 1_1_2_8_r109 (e366). For e380 P0
    also finished with r100, over a nested manual 9.1 `u*(a*x^n)^m` (9_1_r16) that has no fire on
    the substrate.
  - **Arms:** all deferred.
  — follows from: faithful Optional binding (`m_.`) exposing the ILtQ translation (4); e380 is
  consistent with the 9.1 regeneration; e366 not determined [defect: IGtQ 4; none seen 2]
- class 1 g58 (6 entries, deterministic, final deferred top=1_4_2_r20): 1_4_2_r20 (`u^q v^p`
  ExpandToSum normalizer; P0 4 / F 6) answers alone with a top-level noun.
  - **Integrands:** `P4(x)/(a+bx^3)^(k/2)` (e68, e69), `P6(x)/sqrt(a+bx^4)` (e220), and
    `(d+ex^2)/(unexpanded quartic)` (e36, e362, e363).
  - **P0:** 1_3_4_r20/r21, 1_2_2_5_r3 (after 9_1_r9, 1_2_2_8_r18, 1_2_2_5_r9, 1_2_1_6_r1,
    1_2_2_6_r2), or 1_2_2_3_r27 (after 1_4_1_r25, 1_1_2_1_r15, 1_4_1_r23, 1_2_1_1_r12, 1_2_1_2_r3/r9);
    verified 1.8–4.4 s.
  - **Arms:** r3 verified e68 10.2 s, e69 1.0 s, e220 0.5 s; otherwise deferred.
  — follows from: condition retry (3 of 6); which binding of `u`/`v` the cond accepts is not traced
  [defect: none seen]
- class 1 g59 (6 entries, deterministic, final error top=1_2_2_2_r8): 1.2.3.2
  `(d+ex)^k/(a+b(d+ex)^2+c(d+ex)^4)^j`.
  - **P0:** top-level normalizer 1_4_2_r24, verified 0.6–1.0 s.
  - **Substrate:** only a nested 1.2.2.2 route (1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_2_r13, or
    1_2_1_2_r3/r9/r80/r115, 1_2_1_3_r89, 1_2_1_1_r8, then 1_2_2_2_r8), with no top-level fire.
  - **Error:** the record reads error 8.5–9.1 s, the final30 probe 16.0–29.1 s, the newerror probe
    14.6–23.3 s (same lists). Error in all arms, so the process dies during integration. The kind
    is not recorded. g22's 1.2.3.2 half and g78 have the same shape.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g60 (6 entries, deterministic, final timeout top=1_1_1_2_r10): MID-CHAIN.
  `(a±bx^4)^(k/4)/x^j`.
  - **Substrate:** the list ends in the nested 1_1_1_2_r10 at 30 s and 120 s, after RT-SUM r14 and
    1_1_1_2_r32 (/r11/r19). The top-level `x^m(a+bx^4)^p` rule has not fired.
  - **P0:** 1_1_1_2_r12, 1_1_2_2_r4, top 1_2_2_2_r8, verified 0.4 s.
  - **Arms:** r3 verifies e1179/e1180 in 0.1 s; otherwise timeout.
  — follows from: RT-SUM in the chain; condition retry for e1179/e1180; why the top level does not
  return is not determined [defect: IGtQ 6]
- class 1 g61 (6 entries, deterministic, final timeout top=1_1_2_2_r13): RT-SUM + VERIFY-TIMEOUT.
  - **Final:** 1_1_2_2_r13 (P0 3 / F 25) is the top-level reduction of `x^(k/2)/(a+bx^2)^j`,
    then 1_1_2_2_r23 → r27 → RT-SUM r14 (a+bx^2) or r13 (1+x^2).
  - **P0:** 9_1_r9, 1_2_2_5_r3, top 1_4_1_r34, verified 1.6–1.8 s.
  - **Timing and arms:** 120 s timeout 6; all arms timeout.
  — follows from: the IGtQ translation [defect: IGtQ 6, negQ 3 (e296, e298, e304)]
- class 1 g62 (6 entries, deterministic, final timeout top=1_2_1_2_r105): 1_2_1_2_r105 (P0 0 /
  F 9) and r95/r99 bind `x^m Q^p` with `d_.`=0 after the x^2 (x^3) substitution.
  - **Fire list:** 1_1_2_1_r13, 1_2_1_2_r99, (r95), r105, with no top-level fire at 30 s.
  - **At 120 s:** the 1.2.2.2 entries e927/e945/e960/e973 still end in r105 (MID-CHAIN). For the
    1.2.3.2 e193/e211 the top-level 1_2_3_2_r6 has fired, so verification runs past 120 s.
  - **P0:** top 1_2_2_2_r8 / 1_3_3_r15, verified 1.8–2.8 s.
  - **Arms:** all timeout.
  — follows from: faithful Optional binding (`d_.`); the cost is not further determined [defect:
  none seen]
- class 1 g63 (6 entries, deterministic, final timeout top=1_2_2_2_r15): 1.2.3.2
  `1/((d+ex)^k(a+b(d+ex)^2+c(d+ex)^4)^j)`.
  - **P0:** 1_4_2_r24, verified 0.7–1.0 s.
  - **Substrate:** only a nested chain (1_4_1_r18, 1_2_1_1_r12, 1_2_1_2_r3/r9, 1_2_2_3_r27,
    1_2_2_4_r39 (/r35), 1_2_2_2_r15); no top-level fire.
  - **Timing:** at 120 s all 6 read error at 75.4–97.4 s with the same top.
  - **Arms:** timeout (e651 r3 error 29.8 s).
  — follows from: not determined from the traces (dies during integration; error kind not
  recorded) [defect: none seen (1_2_2_3_r27's NegQ[b^2-4ac] is on a computed argument)]
- class 1 g64 (5 entries, deterministic, final contains-noun top=1_2_1_3_r56): CATCH-1 (NOUN).
  - **e1056–e1058** `(2-5x)x^(k/2)/sqrt(2+5x+3x^2)`: the g44 route, 1_4_1_r34 → 1_2_2_6_r9 or
    1_2_2_7_r42 → marker. P0 top 1_4_1_r34, verified 3.5–4.7 s.
  - **e1095, e1096** `x^k(A+Bx)(a+bx+cx^2)^p`: 1_2_1_3_r56 reduces, and its sub-integral reaches
    1_2_1_3_r112 (the 1.2.1.3 catch-all) → marker. P0 top was r56 with a fall-through (NOUN),
    verified 4.4–5.3 s.
  - **Corpus:** none of the answers contains Unintegrable.
  - **Arms:** all contains-noun.
  — follows from: faithful Optional binding [defect: none seen]
- class 1 g65 (5 entries, deterministic, final deferred top=1_1_2_8_r68): 1_1_2_8_r68
  (`EqQ[bc^2+ad^2,0] && ILtQ[n,0]`, n = -1 legit; P0 0 / F 5) rewrites
  `x^k(d^2-e^2x^2)^p/(d+ex)` and answers alone with a noun. P0: 1_1_2_8_r106 after 1_4_2_r6 /
  1_1_1_2_r37 / 1_1_2_2_r4, verified 0.4–2.0 s. All arms deferred. — follows from: faithful
  Optional binding (`e_.`); why the rewritten integral has no nested fire is not determined
  [defect: none seen]
- class 1 g66 (5 entries, deterministic, final deferred top=1_2_2_3_r86): Both cores put
  1_2_2_3_r86 at top (`ILtQ[q,0]`, q = -3 legit; 2-arg ExpandIntegrand over
  `1/sqrt(a+bx^2+cx^4)`). On P0 the expansion sum dispatched: 1_4_1_r7 split it, verified
  8.6–12.4 s. On the substrate r86 is the only fire (nfires=1) and gives a top-level noun at
  0.9–1.3 s. This is the class 2 g1 shape. All arms deferred. — follows from: not determined from
  the traces [defect: none seen]
- class 1 g67 (5 entries, deterministic, final deferred top=1_2_2_3_r98): The g66 shape with
  1_2_2_3_r98 (`(a+cx^4)^p/(d+ex^2)^q`, `ILtQ[q,0]`, q = -1…-3 legit). P0 split the expansion
  with 1_4_1_r7 (+1_4_2_r25), verified 3.8–10.5 s. The substrate has r98 alone → noun at 0.2 s.
  All arms deferred. — follows from: not determined from the traces [defect: none seen]
- class 1 g68 (5 entries, deterministic, final deferred top=1_3_4_r1): `x^(k+m)/sqrt(a+bx)`.
  - **P0:** expected at 0.1 s via 1_1_1_2_r38/r39 (hypergeometric) on `(a+b*x)^m*(c+d*x)^n`,
    reading x^(k+m) as (0+1·x)^(k+m). Rubi's `c_` is not Optional (DEG).
  - **Substrate:** 1_3_4_r1 (P0 229 / F 5) substitutes g+hx = a+bx, giving a top-level noun at
    1.1–1.9 s.
  - **Arms:** all deferred.
  — follows from: G-1 (P0 degenerate binding lost); why Rubi's 2-step route is not reached is not
  determined [defect: none seen]
- class 1 g69 (5 entries, deterministic, final deferred top=1_4_2_r19): 1_4_2_r19 (`(dx)^m u^p`,
  TrinomialQ[u] && Not[TrinomialMatchQ[u]]) answers alone with a noun.
  - **Integrands:** the 1.3.1/1.3.2 quartics `a+8x-8x^2+4x^3-x^4`, `1+(x^2-1)^2`, and
    `a+bc^4+…+bd^4x^4`. How the full quartics pass `%mr_trinomialQ` is not traced.
  - **P0:** 1_2_2_5_r10 (depressed-quartic subst; e127, e631, e633, e863) or 1_2_2_2_r21 (e491);
    verified 1.5–23.1 s.
  - **Arms:** all deferred.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g70 (5 entries, deterministic, final timeout top=1_1_2_4_r20): VERIFY-TIMEOUT.
  - **Final:** both cores put 1_1_2_4_r20 (subst x^2) at top on
    `(a+bx^2)^(k/2)/(x^j sqrt(c+dx^2))`. The substrate's nested integral runs 1_1_1_3_r22
    (P0 0 / F 7) with r23/r25 and 1_1_2_1_r15 (atanh).
  - **P0:** 1_1_1_3_r61 / r55 / 1_1_1_6_r7, verified 0.2–3.6 s.
  - **Timing and arms:** the top fire is in the 30 s list; 120 s timeout 5; all arms timeout.
  — follows from: faithful Optional binding (1_1_1_3_r22 `a_.`, `e_.`); the cost is verification
  [defect: none seen (1_1_2_1_r15's NegQ is on a substitution's computed ratio)]
- class 1 g71 (5 entries, deterministic, final timeout top=1_2_1_1_r15): MID-CHAIN.
  - **1.2.1.5/1.2.1.6 e102, e111** `sqrt(Q1)/Q2`: P0 finishes with 1_2_1_4_r27, verified
    1.1–1.7 s. The substrate list ends in the nested 1_2_1_1_r15 at 30 s and 120 s.
  - **1.2.4.2 e106, e111, e113** `x^k(ax+bx^3+cx^5)^(j/2)`: P0 1_3_3_r15/r14/r10 → top 1_4_1_r34,
    verified 1.8–2.8 s. On the substrate r15 is nested at 30 s; the top-level 1_2_4_2_r8/r4 has
    fired by 120 s.
  - **Arms:** all timeout.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g72 (5 entries, deterministic, final timeout top=1_2_1_2_r107): 1_2_1_2_r107 (P0 0 /
  F 6).
  - **Fire list:** 1_1_2_1_r13, 1_2_1_1_r15, then 1_2_1_2_r99 or 1_1_1_4_r46 + 1_2_1_2_r133, then
    1_2_1_3_r89 (+r51), then r107.
  - **Timing:** r107 is top-level only for e1913 (P0 top 1_3_3_r6: VERIFY-TIMEOUT). For e925/e941
    (P0 top 1_2_2_2_r8) and the 1.2.3.2 e191/e207 (P0 top 1_3_3_r15) it is nested at 30 s and
    120 s (MID-CHAIN).
  - **Arms:** all timeout.
  — follows from: faithful Optional binding (`d_.`=0 on `x^m Q^p`); the cost is not further
  determined [defect: none seen]
- class 1 g73 (5 entries, deterministic, final timeout top=1_2_1_3_r53):
  - **Final:** 1_2_1_3_r53 (P0 1 / F 14) is the top-level reduction. Nested: 1_2_1_9b_r5 (p = -3/2,
    IGT) with 1_2_1_2_r117/r15, 9_1_r8, 1_2_1_9b_r32 (e962, e2473); 1_2_1_9b_r1 (e2223, e2224);
    or 1_1_2_3_r48, 1_2_1_2_r93, 9_1_r8, 1_2_1_9b_r32, 1_4_1_r18 (e2271).
  - **P0:** 1_2_1_6_r1 (/r4) at top, or r53 at top (e2271); verified 0.7–4.5 s.
  - **Timing:** VERIFY-TIMEOUT; 120 s timeout 4, unverified e2271 52.8 s.
  - **Arms:** r2 verified e962 2.5 s; r4 unverified e2271 12.7 s.
  — follows from: faithful Optional binding (1.2.1.3 ahead of P0's 1_2_1_6_r1) + the IGtQ
  translation of 1_2_1_9b_r5; e962 narrow Flat binding (r2 verified) [defect: IGtQ 2 (e962,
  e2473); none seen 3]
- class 1 g74 (5 entries, deterministic, final unverified top=1_1_3_8_r18): 1_1_3_8_r18 (Rubi
  `IGtQ[n/2,0]`, cond `is(n/2 > 0)` accepts n = 3; P0 0 / F 8) splits `P2(x)/(a±x^3)` into parts.
  The parts go to 1_1_3_2_r17 (e307, e311, e312) or 1_1_3_2_r107 (hypergeometric; e366, e368).
  P0: Rubi's `P2/(a+bx^3)` rules 1_1_3_7_r25/r26/r14 (later in the table), verified 1.1–1.6 s.
  Unverified in all arms; the answer is not recorded. — follows from: faithful Optional binding
  (`c_.`, `m_.`) exposing the IGtQ translation [defect: IGtQ 5]
- class 1 g75 (4 entries, deterministic, final deferred top=1_1_2_5_r1): EXPAND-NOUN + IGT.
  1_1_2_5_r1 (`IGtQ[p,0] && IGtQ[q,0] && IGtQ[r,0]`; P0 0 / F 4) accepts q, r = 1/2, 3/2 on
  `(a+bx^2)(c+dx^2)^(k/2)(e+fx^2)^(j/2)` and gives a noun. P0: 1_1_2_5_r8, verified 1.3 s. All
  arms deferred. — follows from: faithful Optional binding (`p_.`) exposing the IGtQ translation
  [defect: IGtQ 4]
- class 1 g76 (4 entries, deterministic, final deferred top=1_2_1_2_r89):
  `sqrt(d+ex)^±1/sqrt(±2x-3x^2)`. Both cores fire 1_1_1_3_r55 (IGT: m or n = ±1/2).
  - **Substrate:** 1_2_1_2_r89 (P0 0 / F 4; `LtQ[c,0] && RationalQ[b]` legit) then answers with a
    top-level noun.
  - **P0:** 1_3_3_r17 (e428, e430) or 1_4_2_r25 / 1_4_1_r34 / 1_2_1_4_r30 (e429, e431); verified
    1.2–2.9 s.
  - **Arms:** r4 verifies all 4 (4.5–18.9 s); r3 verifies e428, e430 (0.8 s).
  — follows from: the model flags (all 4) and condition retry (2) [defect: IGtQ 4]
- class 1 g77 (4 entries, deterministic, final deferred top=1_2_2_4_r20): EXPAND-NOUN + IGT.
  1_2_2_4_r20 (`IGtQ[p,0] && IGtQ[q,-2]`; P0 0 / F 4) accepts p = 1/2, 3/2 on
  `(2+3x^2)(5+x^4)^(k/2)/x^j` and gives a noun. P0: 1_1_3_1_r32, 1_2_2_3_r53/r55, 1_2_2_4_r39,
  top 1_2_2_4_r31, verified 4.2–5.4 s. All arms deferred. — follows from: faithful Optional
  binding exposing the IGtQ translation [defect: IGtQ 4]
- class 1 g78 (4 entries, deterministic, final error top=1_2_2_2_r1): 1.2.3.2
  `(d+ex)/(a+b(d+ex)^2+c(d+ex)^4)^j`.
  - **P0:** top-level normalizer 1_3_3_r4, verified 1.1 s.
  - **Substrate:** only a nested route (1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_1_r8, 1_2_2_2_r1); no
    top-level fire.
  - **Error:** record error 7.6–14.7 s; final30 probe 14.5–27.5 s; newerror probe 12.5–21.3 s.
    Error in all arms. The kind is not recorded. The g59 shape.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g79 (4 entries, deterministic, final timeout top=1_1_3_2_r15): 1_1_3_2_r15 (Rubi
  `ILtQ[Simplify[(m+1)/n+p+1],0]`; P0 0 / F 7) accepts -1/2, -2/3 (IGT) as the top-level rule on
  `x/(a+cx^4)^k`, `x/(a+bx^6)^2`.
  - **Chain:** its sub-integral runs RT-SUM r36 (r35 for 2+3x^4). VERIFY-TIMEOUT.
  - **P0:** 1_1_2_1_r15/r10, 1_1_2_1_r3, top 1_2_2_2_r1 (e661, e675, e698), or 1_3_4_r1 (e1336);
    verified 0.3–5.6 s.
  - **Timing and arms:** 120 s timeout 4. r4 unverified e661/e675 (1.5/1.8 s).
  — follows from: the ILtQ/IGtQ translation [defect: IGtQ 4, negQ 3 (not e698)]
- class 1 g80 (4 entries, deterministic, final timeout top=1_1_3_3_r46): MID-CHAIN, then
  verification. `1/((a+bx^2)^j(c+dx^2)^k √x)`.
  - **Chain:** 1_1_3_5_r2 (partial fractions over x^4) → RT-SUM r14 on `1/(a+bx^4)` and
    `1/(c+dx^4)`.
  - **Timing:** 1_1_3_3_r46 is nested at 30 s; by 120 s the top-level 1_1_2_4_r34 (subst k=2) has
    fired, and the entries still time out.
  - **P0:** top 1_4_1_r34, verified 2.0–4.9 s.
  - **Arms:** r3 unverified e476 1.2 s / e484 3.4 s (still FAIL); otherwise timeout.
  — follows from: the IGtQ translation (RT-SUM) [defect: IGtQ 4, negQ 4]

## Evidence gaps (part B)

- **Answers not recorded.** For the unverified groups (g27, g54, g74) and every VERIFY-TIMEOUT
  line, the runs cannot say whether the answer is wrong or just slow to verify. The RT-SUM answer
  is wrong by construction (`mr_sum` keeps k = 1..floor((n-1)/2) for even n).
- **RT-SUM on P0.** 1_1_3_1_r13/r14 and 1_1_3_2_r35/r36 have zero completed fires in the whole
  class-1 P0 run. Whether P0's literals never bound or their repls failed is not traced (misfires
  are not captured).
- **MID-CHAIN** (g25 1.1.3.2 entries, g26, g36 e924/e313/e190, g37, g39 1.2.1.2 entries, g43
  e2382, g50 1.2.2.2 entries, g52 e172/e333/e108, g60, g62, g63, g71, g72, g80). A missing
  top-level fire is weak evidence: the SIGKILL at the cap can drop unflushed stdout. Which rule
  keeps integration from returning is not traced.
- **Deaths.** The error kind of g22's 1.2.3.2 half, g59, g63 (120 s) and g78, and of the record
  errors in g18/g29/g49, is not recorded: no stderr, no Lisp error text.
- **EXPAND-NOUN** (g21's 8 non-retry entries, g23, g24, g31, g33, g38, g41, g45, g55, g57, g66,
  g67, g75, g77). The traces cannot separate the seen guard stopping a no-op expansion from a
  misfired parent. g66/g67 are the class 2 g1 shape exactly: P0's sum dispatched.
- **CATCH-1** (g30, g32, g42, g44, g64). Why Rubi's own rules for these integrands do not answer
  first is not traced.
- **Single-group questions.**
  - g27: why 1_2_1_2_r119's `%mr_neQ(c*d^2-b*d*e+a*e^2, 0)` accepts an identically-zero
    expression.
  - g31: P0 fired 1_2_2_2_r2 in 6 other entries with the same cond.
  - g47: how `x^m` passes `%mr_polyPowerQ`.
  - g58: which `u`/`v` binding of 1_4_2_r20 is accepted.
  - g69: how a full quartic passes `%mr_trinomialQ`.
  - g38: whether narrow Flat binding keeps 1_2_2_5_r9 from binding (r2 is still deferred).
- **negQ not tagged (argument computed, Rubi's reading not checkable).** Rubi's `PosAux` on a sum
  depends on Mathematica's canonical term order, which cannot be evaluated here. The untagged
  uses:
  - 1_1_2_1_r13 (F 288) on `b^2-4ac`-type arguments from 1_2_1_1_r12;
  - 1_1_2_1_r15 (g70); 1_2_2_2_r23 (g37); 1_2_2_3_r27 (g63);
    1_2_2_1_r17 / 1_2_2_2_r34 / 1_2_2_3_r60 (g50 e2440);
  - 1_1_3_1_r31 (g19 e1029–e1031, g43 e1025–e1027; the same route fired on P0);
  - RT-SUM r14 on substituted arguments in g25/g26/g39/g60 (`-a`, `-b/d`), where Rubi's NegQ reads
    True as well.
- **IGtQ not tagged (binding not recoverable).** Nested ILtQ/IGtQ uses whose binding cannot be
  read from the integrand: 1_1_2_2_r7 (g20), 1_1_3_2_r13 (g28, already tagged via RT-SUM), and the
  `ILtQ[Simplify[m+2p+3],0]` disjunct of 1_2_1_2_r119 (g27).
- **Switch attribution.** Switches are named only where the committed r2/r3/r4 arm changes the
  class. "Model flags" / "condition retry" / "narrow Flat binding" mean that arm verifies or
  otherwise reclassifies the entry. They do not say which rule the flag moves.
- **Collapse family.** No part-B entry has 9_1_r27 or 9_1_r28 in its P0 or final fires, so no group
  is tagged `[collapse-family]`.

## Defect tally (part B)

534 entries in 63 groups.

- `[defect: IGtQ]`: 271 entries in 33 groups (g18, g19, g21, g23–g29, g31, g35, g36, g39, g43,
  g46, g48–g51, g54–g57, g60, g61, g73–g77, g79, g80). The rules carrying them: the RT-SUM four,
  1_1_2_2_r6, 1_1_1_2_r11, 1_1_3_1_r4, 1_1_3_2_r15, 1_2_1_9b_r5/r6, 1_1_3_2_r12/r107,
  1_1_1_3_r16/r55, 1_1_2_5_r1, 1_2_2_4_r19/r20, 1_2_2_3_r11, 1_2_2_2_r2, 1_1_3_8_r18 and
  1_1_2_8_r100.
- `[defect: negQ]`: 76 entries in 12 groups (g18 12, g19 6, g28 14, g29 6, g35 10, g39 1, g40 9,
  g43 2, g48 6, g61 3, g79 3, g80 4). 67 of them also carry IGtQ; the 9 of g40 are negQ-only
  (1_1_3_2_r5 `NegQ[n]` on symbolic n).
- `[defect: none seen]`: 254 entries. 29 groups carry no defect tag at all (g20, g22, g30, g32–g34,
  g37, g38, g41, g42, g44, g45, g47, g52, g53, g58, g59, g62–g72, g78).
- `[collapse-family]`: 0 groups.
