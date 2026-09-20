# P5b mechanism lines — class 1, part A (g1–g23)

> Translation fixes, Task 7 Step 4. One line per probe-10 GROUP, each with its defect-clearance tag.
> Reads: `probes/matcher/10-p5b-attribution.class1.summary.out` lines 4–1901 (GROUP g1 … g23, 605 entries)
> and its raw legs (`…class1-{final30,p0,final120,newerror}.out`). g24–g262, NEW TIMEOUTS and NEW ERRORS are
> covered by the other two class-1 readers. 1.2.1.4 e810 is not in g1–g23.
> Written 2026-09-15 by read-only analysis (no Maxima run). Cores: fixed `b98e4748784738cb78f0163a97d4cf5f`
> (P5b final record `test/corpus_class1.p5b-run1.out`), P0 `5ef9b3bc5ee07ffac0e76f1fea54fbac`.

Evidence used beyond the summary, and how to read the lines. The conventions of
`probes/matcher/10-p5b-attribution.mechanisms-class2-3.md` hold (families VERIFY-TIMEOUT, MID-CHAIN, NOFIRE,
EXPAND-NOUN; EQ-REWRITE; split groups counted under their most severe sub-tag).

- **Arms.** `r2`/`r3`/`r4` = `test/corpus_class1.p5b-run{2,3,4}.out` (mr_flat_wide=true / mr_cond_retry=false /
  mr_model_flags=false). 100 s re-check = `test/corpus_class1.p5b-final.timeout-rerun/`.
- **Defective tree.** Record `test/corpus_class1.p5-run1.out`; its traces are the P5 probe legs
  `probes/matcher/10-p5-attribution.class1-{final30,final120}.out`, which cover only entries that FAILED there.
  **Fix-induced** = PASS on the defective tree, FAIL on P5b: 180 entries in g1–g23, none with a
  defective-tree trace.
- **What was read.** Fire lists, walls, arm classes and the defective-tree class of all 605 entries, by
  script. Integrands of every entry of g2–g23 and of 28 g1 entries across 16 files, by hand. The
  `answer final:` lines of g6 and g12 (all 37). Rule text from `rules/class1/`, Rubi text from the pinned
  clone.
- **Fire logging.** `maxima_rubi_dispatch.lisp:248` logs a fire only after the repl returns. Declines and
  misfires are verbose-only, so probe 10 does not keep them.
- **EqQ reading (unlisted, not ticketed).** `%mr_eqQ(u, v) := %mr_b(u - v = 0)` (`maxima_rubi_utils.mac:369`,
  the same text at P0 `0a6664c`:537) and `%mr_neQ` = not `is(u - v = 0)`. `is(… = 0)` is Maxima's
  syntactic equality after simplification, with no expansion.
  - **Where it bites.** On the factorable quadratics `a d e + (c d^2 + a e^2) x + c d e x^2` and
    `c d^2 − b d e − b e^2 x − c e^2 x^2`, one bound coefficient is an unexpanded sum. `c d^2 − b d e + a e^2`
    then stays e.g. `c*d^3*e - d*e*(c*d^2+a*e^2) + a*d*e^3`, so EqQ reads False and NeQ True where the value
    is 0.
  - **Evidence (inferred, not measured).**
    1. No fire of 1_2_1_3_r88, nor of any of the 17 1_2_1_2 rules whose cond is
       `%mr_eqQ(c*d^2 - b*d*e + a*e^2, 0)`, in any row of the three class-1 P5b legs.
    2. The NeQ rule 1_2_1_2_r107 fires on all 16 g12 integrands.
    3. 9 of the 16 g12 answers divide by `a*d*e^3-d*e*(a*e^2+c*d^2)+c*d^3*e`, which expands to 0.
  - **Tagging.** It is none of the four fixed translations and not ticket 02. Groups whose route turns on it
    are tagged `none` and listed separately in the clearance summary.
- **GtQ reading (ticket 02).** The deciding sites here are 1_1_2_1_r18/r32, 1_1_2_2_r40, 1_1_3_1_r24 and
  1_1_3_2_r40: `not(is(… > 0))` on a symbol, where Rubi's `Not[GtQ[…,0]]` is True. The dispatcher's reading of
  `not(is(sym > 0))` is not measured (ticket 02), and the declines are not traced.
- **Sign readings.** Read from the code, as in the class 2–3 file. The sum-first-term sites of g10 and g23 are
  cross-checked against the branch constants in the corpus answers (grep of the corpus lines).

## Class 1 (g1–g23)

- class 1 g1 (192 entries, deterministic, final timeout top=-): **NOFIRE timeout.**
  - **Fires.** None at 30 s (192/192).
    - **120 s.** Timeout 179: 177 with no fire, plus e2202 and 1.2.1.9 e258 with 1_4_1_r18 only.
      Unverified 11 (1.2.1.3 e2237–e2261, 41.2–78.2 s): top 1_2_1_3_r49, or r50 for e2257, via
      1_4_2_r15 + 1_2_1_9b_r27 or 1_1_2_3_r48 … 1_4_1_r18. Not re-run: e1758 (record error 2.5 s) and 1.2.1.4
      e700 (record unverified 24.6 s).
    - **100 s re-check.** Timeout 179, unverified 11.
  - **Files.** 1.2.1.2 84, 1.1.1.3 31, 1.2.1.3 18, 1.1.1.2 15, 1.2.1.4 15, 1.3.1 6, 1.1.2.4 5, 1.2.1.6 4,
    1.2.1.5 3, 1.2.2.2 3, 1.1.3.8 2, 1.2.3.4 2, and one each in 1.1.1.4, 1.2.1.9, 1.2.2.4 and 1.2.2.7.
  - **Integrands and P0.** The 28 read are Rubi 1–10-step shapes, e.g. `(b d+2c d x)^7/(a+bx+cx^2)^k`,
    `x^2 sqrt(a+bx) sqrt(c+dx)`, `(b+2cx+3dx^2)(a+bx+cx^2+dx^3)^7`. P0 verified 0.2–21.3 s; tops 1_3_4_r1 77,
    1_1_1_3_r19 23, 1_3_3_r6 12, others ≤ 8.
  - **Arms.** r3 (mr_cond_retry=false): verified 91, unverified 80, deferred 4, timeout 17. r2: timeout 190,
    error 1, unverified 1. r4: timeout 191, unverified 1. So the non-return needs condition retry in 175 of 192.
  - **Defective tree.**
    - **Timeout 115**, no fire.
    - **Deferred 61.** 58 went through an ExpandIntegrand rule accepted on a bare `is(p > 0)` of a fractional
      p: 1_2_1_2_r58 36, 1_2_1_3_r15 16, 1_1_1_2_r12 5, 1_1_2_9_r14 1. Rubi's `IGtQ` rejects those, and so does
      `%mr_iGtQ` now. The other 3 (1.2.1.6 e78/e85/e87) had no fire.
    - **Verified 16, fix-induced, route not traced.** 1.1.1.2 e1568, e1569, e1573, e1574, e1752, e1753,
      e1758, e1759, e1764, e1765; 1.2.1.4 e700, e783, e900; 1.2.1.5 e114; 1.2.1.9 e258; 1.3.1 e223.
  - **Reading.** Which rule's binding enumeration uses up the cap is not traced. 1.2.1.3 e2237–e2261 are
    factorable-quadratic integrands, whose Rubi route is the EqQ family (EqQ reading).

  — follows from: condition retry (cost, 175 entries); for 58 entries the IGT translation fix removed a fast
  noun route (Rubi's reading) — [fixed-defect: undetermined — no route observed; a trace flushed at the kill
  (the rule enumerating bindings at 30 s) decides it]
- class 1 g2 (66 entries, deterministic, final deferred top=-): **NOFIRE deferred.**
  - **Overview.** No rule answers at top level (nfires=0, 0.1–10.9 s). P0 verified 0.5–8.4 s. All arms
    deferred. The defective tree was deferred with no fire on 63; e1060/e1062/e1064 verified there
    (fix-induced). The entries split into two families.
  - **GtQ reading, 14 entries.**
    - **`1/sqrt(±a±b x^2)`, 8** (1.1.2.2 e490, e584–e588; 1.1.2.3 e77; 1.2.1.1 e59). Rubi 1.1.2.1.m:118–132
      puts asinh/asin on `GtQ[a,0]` and the Subst rule on `Not[GtQ[a,0]]`. On a symbol (e588: a^2) GtQ is
      False, so the Subst rule answers (corpus: atanh/atan, 2 steps). The port's 1_1_2_1_r16/r17 need
      `is(a > 0)`, and r18's `not(is(a > 0))` is not true. P0: 1_1_2_1_r13/r10 + 1_1_2_2_r33 (m = 0, G-1).
    - **`(a+b x^2)^p`, 3** (1.1.2.2 e1048, 1.1.2.3 e342, 1.2.1.2 e735). Rubi 1.1.2.1.m:214–216
      `Not[IntegerQ[2p]] && Not[GtQ[a,0]]` is 1_1_2_1_r32 `not(is(a > 0))`: the same reading. P0: 1_2_1_1_r18.
    - **`x^(−8−2p|−6−2p|−4−2p) (a+bx^2)^p`, 3** (1.1.2.2 e1060/e1062/e1064, fix-induced).
      - **Old route.** P0 and the defective tree answered with 1_1_2_2_r6, whose `ILtQ[(m+1)/2+p+1,0]` is
        −5/2, −3/2 or −1/2 here. `%mr_iLtQ` now rejects it, as Rubi does.
      - **Rubi's next rule.** 1.1.2.2.m:277 `Not[IGtQ[p,0]] && Not[ILtQ[p,0] || GtQ[a,0]]` (1_1_2_2_r40)
        carries `not(… or is(a > 0))`.

    — follows from: GeQ/GtQ reading (ticket 02; declines inferred from rule text, not traced) —
    [fixed-defect: none]
  - **The other 52.**
    - **P0 on bindings Mathematica does not make (G-1), 26.** The manual 9.1 `u*(a*x^n)^m` 13,
      1_1_3_2_r110 8, 1_1_4_1_r9 4, 1_1_2_2_r4 1.
    - **1.4.2 ExpandToSum normalizers, 13.** r17 6, r20 4, r23 2, r21 1.
    - **Other P0 tops, 13.** 1_4_1_r49/r50/r51 5, 1_4_3_r2 2, and one each of 1_2_2_1_r17, 1_1_1_4_r44,
      1_2_1_2_r109, 1_4_1_r23, 1_4_1_r29, 1_3_1_r15.
    - **Rubi's own first rules are not traced.** For `(a+bx^k)/x` (1.1.3.2 ×8, 1.1.2.2 e6, 1.2.1.2 e2179),
      Rubi's `IGtQ[p,0]` ExpandIntegrand rules (e.g. 1_1_3_2_r12; p = 1 holds) do not fire. The 1.1.3.8
      e41–e47/e370/e372 routes carry EqQ tests on symbolic radical coefficients (EqQ reading; not checked per
      rule).

    — follows from: G-1 (26) / not determined from the traces — [fixed-defect: undetermined — no route
    observed; a decline trace of Rubi's first rule per family decides it]
- class 1 g3 (38 entries, deterministic, final deferred top=1_2_1_3_r112): **Catch-all alone.** 1_2_1_3_r112
  (the 1.2.1.3 `Unintegrable` rule) answers alone (nfires=1, 1.3–2.2 s).
  - **Integrands.** 1.2.1.4 factorable quadratics `(a d e+(c d^2+a e^2)x+c d e x^2)^p (d+ex)^m (f+gx)^n`, with
    p and m half-integers. n is an integer, a half-integer or a symbol (e764–e766, e775). e781 is a variant.
  - **P0.** Verified 4.1–26.0 s via 1_2_1_3_r12 27 (`IGtQ[p,0] && ILtQ[n,0] && IntegerQ[m+1/2]`), r14 6
    (`IGtQ[p,0]`), r111 4 (`IGtQ[n,1]`) and 1_4_2_r15 1. On p = 1/2…5/2 and n = 3/2, 5/2 those integer tests
    fail in Rubi, and in `%mr_iGtQ`/`%mr_iLtQ` now.
  - **Defective tree.** Verified 32 (2.8–27.3 s; fix-induced). Timed out on e720/e721/e727 (120 s: 9_1_r6,
    1_3_3_r6, r111) and e765/e766 (r14). Deferred e781 via r112.
  - **Rubi's route.** By hand c d^2 − b d e + a e^2 = 0 for these bindings, so Rubi 1.2.1.3.m:682 applies (the
    FracPart factorization; EqQ only). That rule is 1_2_1_3_r88.
  - **Why r88 does not fire.** Its cond `%mr_eqQ(c*d^2-b*d*e+a*e^2, 0)` reads False on the unexpanded `b`
    (EqQ reading). Its repl's `%mr_fracPart` (sibling port) is never reached; FracPart[3/2] = 1/2 in both codes.
  - **Arms.** All deferred.

  — follows from: the IGT translation fix (Rubi's reading removes the P0 and defective-tree routes), with
  Rubi's r88 blocked by the EqQ reading (inferred, not traced) — [fixed-defect: none]
- class 1 g4 (26 entries, deterministic, final timeout top=1_2_1_3_r50): **VERIFY-TIMEOUT.**
  - **Integrands.** 1.2.1.3 `(f+gx)(d+ex)^m (a+bx+cx^2)^p`, p = 1/2…7/2:
    - `(A+Bx) q^p/x^j`, `(b+2cx) q^p/(d+ex)^j`, `(5−x)(2+5x+3x^2)^p/(3+2x)^j`;
    - 3 factorable `(f+gx)(cd^2−bde−be^2x−ce^2x^2)^p/(d+ex)^(3/2)` (e2235, e2244, e2254).
  - **Final.** The top-level r50 (Rubi's `GtQ[p,0] && (LtQ[m,−1] || …)` reduction) closes the 30 s fire list in
    26/26, unchanged at 120 s, so rubi returned.
    - **Nested, 22.** 1_1_2_1_r13, 1_2_1_1_r15, 1_2_1_2_r99, 1_2_1_3_r89 (+ r51/r49).
    - **Nested, e1634/e2235/e2244/e2254.** 1_1_2_3_r48/r42, 1_2_1_2_r93, 9_1_r8, 1_2_1_9b_r32 (+ r56/r89,
      1_2_1_2_r109).
  - **Walls.** P0 verified 1.5–6.7 s. Timeout at 30 s, 120 s and the 100 s re-check (26/26).
  - **Arms.** r2/r3 timeout 26. r4: timeout 23, unverified 3 (e2235/e2244/e2254).
  - **P0.** Top r50 with nested 1_2_1_9b_r5 (10; its `IGtQ[p,−2]` ExpandIntegrand read bare), 1_2_1_9_r22 13,
    1_3_3_r6 3.
  - **Defective tree.** Verified 12 (0.5–0.8 s; fix-induced, route not traced). Deferred 14 via 1_2_1_3_r15
    alone (bare `is(p > 0)`).
  - **Sites.**
    - r50's `is(p > 0)` and `is(m < -1)` compare numbers, as Rubi's GtQ/LtQ do.
    - 1_1_2_1_r13's NegQ and `is(a > 0) or is(b < 0)` act on the Subst integrand `1/(A − x^2)` (b = −1). The
      corpus answers are atanh forms, the branch taken.
    - The 3 factorable entries miss Rubi's EqQ family (EqQ reading).

  — follows from: the IGT translation fix (Rubi's reading) routing onto Rubi's reduction chain; the cost is
  verification — [fixed-defect: none]
- class 1 g5 (21 entries, deterministic, final timeout top=1_1_3_2_r47): **MID-CHAIN.**
  - **Integrands.** 1.1.4.2 17 `x^k (b x^(1/3)+a x)^(±1/2|±3/2)`; 1.1.1.2 4
    `1/((a+bx)^(5/4|9/4)(c+dx)^(1/4|5/4))`.
  - **Final.** 1_1_3_1_r32, 1_2_2_3_r54, 1_1_3_2_r47 in 21/21, at 30 s and at 120 s. r47's LHS
    `x^2/sqrt(a+bx^4)` is not the integrand's form, so the enclosing rule has not completed by 120 s. 100 s
    re-check: timeout 21.
  - **Sign readings.** r47, r32 and r54 test `%mr_posQ(b/a)` on the substituted quartic with symbolic
    coefficients; r54 also tests Rt[c/a,4]. PosAux reads a symbol ratio positive, in Rubi and in the fixed port.
    So these are Rubi's elliptic rules (corpus answers: elliptic forms, 6–13 steps).
  - **P0.** Verified 0.6–2.1 s via 1_1_4_4_r2/1_1_4_2_r1 → 1_1_4_2_r6/1_1_4_1_r3 (17) and 1_1_1_4_r46 →
    1_1_1_2_r39/r11 (4). No r47 fire.
  - **Defective tree.** The 17 1.1.4.2 entries verified 0.7–2.3 s (fix-induced, route not traced; the strict
    sign read a symbol ratio as not positive). The 4 1.1.1.2 entries timed out via 1_1_3_2_r17, 1_2_1_1_r17,
    1_1_1_2_r31/r11.
  - **Arms.** r3: verified 17, deferred 2 (e134, e162), timeout 2 (e1703, e1704). r2/r4: timeout 21. The
    enclosing rule's cost needs condition retry; which rule is not traced.

  — follows from: the NEGQ translation fix (Rubi's PosQ reading reaches the elliptic rules) + condition retry
  (cost) — [fixed-defect: none]
- class 1 g6 (21 entries, deterministic, final unverified top=1_2_2_2_r35): 1_1_2_4_r66 → 1_2_2_2_r35 in 21/21
  (0.9–1.8 s).
  - **Rule.** r35 is Rubi 1.2.2.2's last rule (no condition). It rewrites
    `a^IntPart[p](…)^FracPart[p]/(…) Int[(dx)^m (1+2cx^2/(b+q))^p (1+2cx^2/(b−q))^p]`, q = Rt[b^2−4ac,2].
    1_1_2_4_r66 then answers AppellF1.
  - **Integrands.** 1.2.2.2 `(dx)^m (a+bx^2+cx^4)^p`, with m ∈ {±1/2, ±3/2, m} and p ∈ {±1/2, ±3/2, p}.
  - **Answers (21 read).** AppellF1, with the two arguments and the two √ factors in swapped order against the
    corpus answer. F1(α;β,β;γ;u,v) is symmetric in (u,v), and `sqrt(b^2-4*a*c)` appears as in the corpus. This
    is the corpus's own 2-step shape: unverifiable, not wrong.
  - **P0.** Verified 3.2–6.6 s via 1_3_3_r15/r14/r10 + 1_4_1_r34 → 1_3_4_r9 (16) or 1_4_2_r19 → 1_3_4_r9 (5).
  - **Defective tree.**
    - Deferred 10 via 1_2_2_2_r2 alone (ExpandIntegrand on a bare `is(p > 0)`; p = 1/2, 3/2: e1089–e1096,
      e1110, e1111).
    - Verified 10 with p = −1/2, −3/2 (e1097–e1104, e1112, e1113; fix-induced, route not traced).
    - Unverified e1114 on today's route.
  - **Sites.** r35's `%mr_intPart`/`%mr_fracPart` (sibling ports) act on a numeric p or on a symbol
    (FracPart[p] = p), giving Rubi's values. `%mr_rt(b^2−4ac,2)` gives `sqrt(b^2-4*a*c)` as in the corpus.
  - **Arms.** All unverified.

  — follows from: the IGT translation fix (10) and an untraced defective-tree route (10), giving way to Rubi's
  1-step rule; verdict: the zero chain does not close AppellF1 — [fixed-defect: none]
- class 1 g7 (20 entries, deterministic, final deferred top=1_2_2_4_r93): **EXPAND-NOUN.**
  - **Final.** 1_2_2_4_r93 alone (nfires=1, 0.4–0.5 s). Rubi 1.2.2.4 r93 is ExpandIntegrand
    `/; NeQ[b^2−4ac,0] && (IGtQ[p,0] || IGtQ[q,0] || IntegersQ[m,q])`; q = 1, so Rubi accepts too.
  - **Integrands.** 1.2.2.4 `(fx)^m (d+ex^2)(a+bx^2+cx^4)^p`, with m ∈ {±1/2, ±3/2, m} and p ∈ {±1/2, ±3/2}.
  - **Nested call.** The expansion distributes `(d+ex^2)` into a two-term equal-form sum. The nested `mr_int`
    records no fire, while a dispatched sum fires 1_4_1_r7.
  - **P0.** Verified 5.9–19.0 s via 1_2_2_2_r2 / 1_3_3_r15 + 9_1_r13 / 1_4_1_r34 → 1_1_2_3_r1 → 1_4_1_r7 →
    1_2_2_6_r3 (its `IGtQ[p,−2]` read bare).
  - **Defective tree.** Deferred 20: 1_2_2_4_r19 alone 10 (bare `is(p > 0)` on p = 1/2, 3/2; now rejected, as in
    Rubi) and r93 alone 10.
  - **Arms.** All deferred.

  — follows from: the IGT translation fix (r19 → r93 for 10); the no-answer is not determined from the traces —
  [fixed-defect: undetermined — EQ-REWRITE at 1_2_2_4_r93, awaiting probe 16; competing: `%mr_expandIntegrand`
  returns the product unexpanded (an exact repeat), or a `%mr_intSum` fault]
- class 1 g8 (20 entries, deterministic, final timeout top=1_2_1_3_r56): **VERIFY-TIMEOUT.**
  - **Integrands.**
    - 1.2.1.3, 17: factorable `(d+ex)^k (f+gx)(cd^2−bde−be^2x−ce^2x^2)^(j/2)` 16 (e2172–e2264), plus e1628
      `(b+2cx) sqrt(d+ex) sqrt(q)`.
    - 1.2.1.4: e888 `(d+ex) sqrt(f+gx) sqrt(q)` and e902 `(d+ex) sqrt(f+gx)/sqrt(q)`.
    - 1.2.2.4: e169 `x^5(A+Bx^2)/sqrt(a+bx^2+cx^4)`.
  - **Final.** r56 (Rubi's `GtQ[m,0]` reduction) is in every 30 s list. It is the top-level rule in 19; for
    e169 the subst top 1_2_2_4_r9 fires at 120 s.
    - **Nested, 4** (e2172, e2183, e2195, e2209). 1_2_1_9b_r1.
    - **Nested, the rest.** 1_1_2_3_r48/r42, 1_2_1_2_r93, 9_1_r8, 1_2_1_9b_r32/r1, 1_2_1_3_r89/r51,
      1_2_1_2_r109/r117, 1_4_1_r18.
  - **Walls.** P0 verified 1.6–6.5 s. 120 s: timeout 18, unverified e2263 (72.0 s) and e2264 (40.3 s). The
    100 s re-check matches.
  - **Arms.** r2/r3: timeout 19, unverified 1. r4: unverified 11 (factorable entries), timeout 9.
  - **P0.** Top r56 15, nested 1_2_1_9b_r5 (its `IGtQ[p,−2]` read bare) or r1; 1_2_1_6_r1 4 (the same
    `IGtQ[p,−2]`); 1_2_2_6_r2 1.
  - **Defective tree.** Verified 14 (fix-induced, route not traced). Deferred e1628/e888 via 1_2_1_3_r15 (bare
    `is(p > 0)`). Timeout 4 on today's chains.
  - **Factorable entries.** Rubi's first rules are the 1.2.1.3 EqQ family (e.g. r31
    `EqQ && IGtQ[m,0] && IGtQ[n,0]` for e2172). `%mr_eqQ` reads the zero False (EqQ reading), so the general
    recurrence runs.

  — follows from: the IGT translation fix (Rubi's reading) + the EqQ reading on 16 entries (inferred); the cost
  is verification (r4: the model flags) — [fixed-defect: none]
- class 1 g9 (18 entries, deterministic, final deferred top=1_2_1_3_r109): **EXPAND-NOUN.**
  - **Final.** 1_2_1_3_r109 alone (nfires=1, 1.4–1.7 s). The rule is ExpandIntegrand
    `/; IntegerQ[p] || ILtQ[m,0] && ILtQ[n,0]`. With x^−j (j = 2…9) and (d+ex)^−1 both exponents are negative
    integers, so Rubi accepts too. The partial-fraction expansion times `q^(k/2)` is an equal-form sum, and it
    records no nested fire.
  - **Integrands.** 1.2.1.4 `(ade+(cd^2+ae^2)x+cdex^2)^(1/2|3/2|5/2)/(x^j (d+ex))`.
  - **Upstream.** Rubi's first rule is the factorization 1_2_1_3_r88 (as in g3), blocked by the EqQ reading. r109
    answers only because r88 declines.
  - **P0.** Verified 2.1–2.7 s via 1_4_2_r25 → 1_3_3_r6 (its `IGtQ[p,0] && ILtQ[q,0]` read bare).
  - **Defective tree.** Deferred 18 via 1_2_1_3_r15 alone (bare `is(p > 0)`); now rejected, as in Rubi.
  - **Arms.** All deferred.

  — follows from: the IGT translation fix (r15 → r109), with the EqQ reading upstream (inferred) —
  [fixed-defect: undetermined — EQ-REWRITE at 1_2_1_3_r109, awaiting probe 16; competing: a `%mr_intSum` fault
  on the expansion]
- class 1 g10 (18 entries, deterministic, final timeout top=1_2_1_2_r107): **VERIFY-TIMEOUT / MID-CHAIN.**
  - **Integrands.**
    - 1.2.1.2, 12: 9 `(a+bx+cx^2)^(k/2|k/4)/(d+ex)^j`, and 3 factorable `q^(1/2|3/2|5/2)/(d+ex)^j` (e1913,
      e1925, e1939).
    - 1.2.2.2: e925, e941, e942 `(a+bx^2+cx^4)^(k/2)/x^j`.
    - 1.2.3.2: e191, e207, e208 `(a+bx^3+cx^6)^(k/2)/x^j`.
  - **Final.** r107 ends every 30 s list, unchanged at 120 s. r107 is Rubi's
    `NeQ[cd^2−bde+ae^2,0] && GtQ[p,0] && (IntegerQ[p] || LtQ[m,−1])` reduction.
    - For the 9 general 1.2.1.2 entries it is the top-level rule, so rubi returned.
    - For the 1.2.2.2 and 1.2.3.2 entries the subst top has not fired by 120 s (MID-CHAIN).
  - **Nested.**
    - 11 entries: 1_1_2_1_r13, 1_2_1_1_r15, 1_2_1_2_r99, 1_2_1_3_r89 (+ r50/r51).
    - e1913, e1925, e1939: 1_1_1_4_r46 + 1_2_1_2_r133.
    - e2445, e2456, e2457: 1_1_2_3_r48/r42, 1_2_1_2_r93, 9_1_r8, 1_2_1_9b_r32.
    - e2515, e2527: 1_1_3_1_r32 + 1_2_1_1_r17.
  - **Factorable entries.** On e1913/e1925/e1939, r107's `%mr_neQ(c*d^2 - b*d*e + a*e^2, 0)` reads True where the
    value is 0, and Rubi's NeQ is False. Rubi's 1.2.1.2 EqQ-family rules do not fire (EqQ reading).
  - **Sites.**
    - 1_1_3_1_r32 reads `%mr_posQ(4c/(b^2−4ac))` True through a sum's first term (sibling:%mr_posAux). The
      corpus answers of e2515/e2527 carry `elliptic_f(2*atan(…),1/2)`, which is r32's form, so Rubi reads the
      same.
    - 1_1_2_1_r13 acts on `1/(A − x^2)`, and the corpus answers have atanh forms.
  - **Walls.** P0 verified 2.3–29.8 s. Timeout at 30 s, 120 s and the 100 s re-check (18/18). All arms time out.
  - **P0.** Top r107 7 (nested 1_2_1_9b_r5 / 1_2_1_1_r5, their `IGtQ` read bare), 1_3_3_r6 3 (the same),
    1_2_2_2_r8 3, 1_3_3_r15 3, 1_2_1_2_r119 2.
  - **Defective tree.** Verified 12 (fix-induced, route not traced). Timeout 6 on today's chains (e1913, e2445,
    e925, e941, e191, e207).

  — follows from: the IGT translation fix (Rubi's reading) routing onto Rubi's reduction; the cost is
  verification/integration; e1913/e1925/e1939 also the EqQ reading (inferred) — [fixed-defect: none]
- class 1 g11 (17 entries, deterministic, final timeout top=1_1_3_2_r50): **MID-CHAIN.**
  - **Integrands.** 1.1.3.4 13 `(ex)^(±3/2)(A+Bx^3)(a+bx^3)^(±1/2|±3/2|±5/2)` and an `x^(−9/2)` variant;
    1.1.4.2 4 `x^k/sqrt(a x^2+b x^5)`.
  - **Final.** 1_1_3_1_r37, 1_1_3_7_r32, 1_1_3_7_r33, 1_1_3_2_r50 in 17/17 at 30 s. These are the
    `sqrt(a+bx^6)` elliptic rules after the x^(1/2) substitution; r50's LHS `x^4/sqrt(a+bx^6)` is not the
    integrand. At 120 s, e299 adds 1_1_3_2_r71 and the top 1_1_4_2_r20; the other 16 are unchanged. 100 s
    re-check: timeout 17.
  - **Arms.** r4 (mr_model_flags=false) verified 17/17; r2/r3 timeout 17. The non-completion depends on the model
    flags.
  - **Sites.** r37 and r50 have no condition. 1_1_3_7_r32/r33 test `EqQ/NeQ[2 Rt[b/a,3]^2 c − (1−√3) d, 0]` on
    symbols; NeQ is True in both. 1_1_4_2_r20 tests `%mr_posQ(n−j)` on numbers.
  - **P0.** Verified 2.2–8.3 s via 1_4_1_r34 → 1_1_3_8_r30 (12) or 1_4_1_r34 (5).
  - **Defective tree.** Deferred 7 (e518–e540; p = 1/2…5/2) via 1_1_3_4_r13 alone: ExpandIntegrand on a bare
    `is(p > 0) and is(q > 0)`, now rejected as in Rubi. Verified 10 (p < 0; fix-induced, route not traced).

  — follows from: the IGT translation fix (7) and an untraced defective-tree route (10), giving way to Rubi's
  elliptic route; the model flags (r4 verifies 17) — [fixed-defect: none]
- class 1 g12 (16 entries, deterministic, final unverified top=1_2_1_2_r107): **NeQ misroute.**
  - **Integrands.** 1.2.1.2 factorable `(ade+(cd^2+ae^2)x+cdex^2)^(1/2|3/2|5/2)/(d+ex)^(j|j/2)`.
  - **Final.** Top-level r107 in 16/16 (2.6–25.0 s). Nested: 1_4_1_r18 + 1_2_1_3_r49/r57/r50, through either
    1_4_2_r15 + 1_2_1_9b_r27 or 1_1_2_3_r48, 1_2_1_2_r93, 9_1_r8, 1_2_1_9b_r32 (+ 1_1_2_3_r42, 1_2_1_3_r89,
    1_2_1_2_r109).
  - **Why r107.** It is Rubi's `NeQ[c d^2 − b d e + a e^2, 0]` reduction. By hand the value is 0, so Rubi rejects
    it and takes its EqQ family (1_2_1_2 r37, r39, r47, …). None of those fires (EqQ reading).
  - **Answers (16 read, cut at 300 characters).**
    - 9 divide by `(a*d*e^3-d*e*(a*e^2+c*d^2)+c*d^3*e)`, which expands to 0: wrong. They are e1926, e1941,
      e2035, e2044, e2045, e2051, e2054, e2055, e2056.
    - 4 hold `elliptic_e` terms (e2033, e2034, e2042, e2043), where the corpus answers are atan plus algebraic
      terms.
    - e1940, e2052 and e2053 are cut before either.
  - **P0.** Verified 1.5–2.5 s via 1_4_2_r25 or 1_1_1_3_r55/r16 → 1_3_3_r6 (its `IGtQ[p,0] && ILtQ[q,0]` read
    bare, with p = k/2).
  - **Defective tree.** Verified 7 (e1926, e1940, e1941, e2042, e2051, e2052, e2053; fix-induced, route not
    traced). Unverified 9, via 1_4_2_r15 / 1_2_1_9b_r27 / 1_2_1_2_r119 chains.
  - **Arms.** All unverified.

  — follows from: the IGT translation fix (P0's 1_3_3_r6 removed) + the EqQ/NeQ reading (unlisted; corroborated
  by the zero-valued denominators) — [fixed-defect: none]
- class 1 g13 (15 entries, deterministic, final timeout top=1_1_3_2_r8): **VERIFY-TIMEOUT via hypergeometric
  forms.**
  - **Integrands.** 1.1.3.2 `x^(−5|−9|−1)(a+bx^4)^(±1/4|±3/4|±5/4)`.
  - **Final.** The top-level r8 (subst x^4) is in every 30 s list, unchanged at 120 s. Timeout at 120 s and at
    the 100 s re-check.
  - **Chain.** 1_1_1_2_r10/r11/r19/r20 → 1_1_1_2_r32 (subst x → (a+bx)^(1/4)) → one of the
    `a^p x Hypergeometric2F1` rules: 1_1_3_1_r57 (7) or 1_1_3_2_r107 (8).
  - **Why hypergeometric.**
    - **The substituted integrand.** `x^(0|2)/(A + B x^4)` with A/B = −a, symbolic.
    - **Rubi.** Its partial-fraction pairs split on `GtQ[a/b,0]`: 1.1.3.1 r23/r24 and 1.1.3.2 r39/r40. GtQ is
      False on a symbol, so r24 and r40 (`Not[GtQ[a/b,0]]`) answer with atan+atanh, the corpus answers' form,
      ahead of the hypergeometric rules.
    - **Port.** `not(is(a/b > 0))` is not true, so r24 and r40 decline. r57/r107 answer; their
      IntegerQ[p]/ILtQ[p,0] tests read as in Rubi.
  - **P0.** Top 1_2_2_2_r8 in 15/15 (subst x^2 first), 0.7–1.4 s.
  - **Defective tree.** Verified 8 (0.1–0.2 s; fix-induced, route not traced). Timeout 7 via 1_1_3_1_r14
    (`IGtQ[(n−3)/2,0] && NegQ[a/b]` under the defective readings).
  - **Arms.** All time out.

  — follows from: GeQ/GtQ reading (ticket 02; the substituted integrand is inferred from the route rules'
  repls, and the declines are not traced) — [fixed-defect: none]
- class 1 g14 (14 entries, deterministic, final timeout top=1_2_2_2_r8): **Unchanged by the fixes.**
  - **Integrands.** 1.2.2.2 10 `x^(3|5|7|9)/(a±bx^2+cx^4)^k` and `1/(x(a+bx^2+cx^4)^k)`; 1.2.3.2 4
    `1/((d+ex)(a+b(d+ex)^2+c(d+ex)^4)^k)` (e617, e635, e642, e658).
  - **Final.** r8 (subst x^2) ends the 30 s list in 14/14; it is the top-level rule for the 1.2.2.2 entries.
    Nested: 1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_2_r3/r9/r13/r97 (+ r80/r103/r113/r115, 1_2_1_3_r89/r55, 1_1_1_1_r1).
  - **Classes.** Record: timeout 10, error 4 (the 1.2.3.2 entries, 12.5–18.3 s). 120 s: timeout 8, error 2
    (e850 58.7 s, e889 68.5 s). The 100 s re-check matches. The error text is not in these legs. All arms:
    timeout 10, error 4.
  - **Defective tree.** The same classes (timeout 9, error 5) and the same fire lists in the P5 probe legs, so
    no translation fix changed these routes.
  - **P0.** Verified 1.3–3.9 s via 1_2_1_6_r1/r4 → 1_2_2_2_r8, or 1_4_2_r24.
  - **Sites.** 1_1_2_1_r13 acts on `1/(b^2−4ac − x^2)`. LtQ[b,0] holds (b = −1). NegQ on `−(b^2−4ac)` reads a
    sum's first term; the corpus answers are atanh forms (e850 `atanh((b+2cx^2)/sqrt(b^2−4ac))`), the branch
    taken.

  — follows from: not determined from the traces (the P0 → final route change predates the fixes); the cost is
  verification or an error — [fixed-defect: none]
- class 1 g15 (13 entries, deterministic, final contains-noun top=1_2_1_3_r56): The top-level r56 (the
  `GtQ[m,0]` reduction on x^(k/2) or x^k) runs, then an `Unintegrable` catch-all answers.
  - **Integrands.** 1.2.1.3:
    - `(A+Bx) sqrt(x) sqrt(q)` (e1029);
    - `(2−5x) x^(k/2)(2+5x+3x^2)^(±1/2|3/2)` (e1034–e1058);
    - `x^(3|2)(A+Bx)(a+bx+cx^2)^p` with a symbolic p (e1095, e1096).
  - **Final.** r56 → 1_4_1_r34 (x → x^2) → a catch-all: 1_2_2_7_r42 (6) or 1_2_2_6_r9 (5), the 1.2.2.7 / 1.2.2.6
    `Unintegrable` rules. For e1095/e1096: r56 → 1_2_1_3_r112. The corpus answers (Rubi 2–9 steps; elliptic and
    hypergeometric forms) contain no Unintegrable.
  - **P0.** Verified 2.4–5.5 s via 1_2_2_5_r1 + 1_4_1_r34 (8; its `IGtQ[p,0]` read bare for p = 1/2, 3/2),
    1_2_2_1_r13 … 1_4_1_r34 (3), or r56 (2).
  - **Defective tree.** Deferred 8 via 1_2_1_3_r15 alone (bare `is(p > 0)`). Contains-noun 5, on today's routes.
  - **Arms.** All contains-noun.
  - **Unknown.** Which 1.2.2.6/1.2.2.7 elliptic rule Rubi applies to the substituted
    `x^j (linear in x^2) sqrt(2+5x^2+3x^4)` (and to e1095/e1096), and why it declines, is not traced. Those
    conditions carry PosQ/NegQ and GtQ tests.

  — follows from: the IGT translation fix (the former noun route of 8 entries); the catch-all is not determined
  from the traces — [fixed-defect: undetermined — a decline trace of the 1.2.2.6/1.2.2.7 rules on e1034's
  substituted integrand, and of the 1.2.1.3 symbolic-p rules on e1095]
- class 1 g16 (13 entries, deterministic, final timeout top=1_2_1_2_r109): **VERIFY-TIMEOUT / MID-CHAIN.**
  - **Integrands.**
    - 1.2.1.2, 7: `(d+ex)^(±1/2|3/2|−1)(a+bx+cx^2)^(1/2|3/2|5/2)`.
    - 1.2.1.4: e857 `sqrt(q)/(d+ex)`, e889 `sqrt(f+gx) sqrt(q)`, e896 `sqrt(q)/sqrt(f+gx)`.
    - 1.2.2.2 e924 `sqrt(a+bx^2+cx^4)/x`; 1.2.2.4 e313; 1.2.3.2 e190.
  - **Final.** r109 (Rubi's `GtQ[p,0]` reduction) ends every 30 s list; at 120 s e2447 adds 1_2_1_3_r51 and
    1_2_1_2_r117.
    - r109 is top-level for the 1.2.1.2 and 1.2.1.4 entries, so rubi returned.
    - For e924/e313/e190 it is nested under a subst top that has not fired by 120 s.
  - **Nested.** 1_1_2_1_r13, 1_2_1_1_r15, 1_2_1_2_r99, 1_2_1_3_r89 (5); or 1_1_2_3_r48/r42, 1_2_1_2_r93
    (+ 9_1_r8, 1_2_1_9b_r32, 1_2_1_3_r56/r89/r51) (8).
  - **Walls.** P0 verified 2.1–5.9 s. Timeout at 30 s, 120 s and the 100 s re-check. All arms time out.
  - **P0.** 1_2_1_9b_r5 → r109 (9; its `IGtQ[p,−2]` read bare), and one each of 1_2_1_2_r117, 1_2_2_2_r8,
    1_2_2_4_r5, 1_3_3_r15.
  - **Defective tree.** Timeout 9 on today's chains. Verified 4 (e2447, e2448, e2449, e2455; fix-induced, route
    not traced).

  — follows from: the IGT translation fix (Rubi's reading) routing onto Rubi's reduction; the cost is
  verification/integration — [fixed-defect: none]
- class 1 g17 (12 entries, deterministic, final timeout top=1_2_1_2_r117): **VERIFY-TIMEOUT.**
  - **Integrands.**
    - 1.2.2.2, 7: `x^(5|7)(a+bx^2+cx^4)^(1/2|3/2)`, `x^(5|7)/sqrt(…)`, `x^5(…)^p`.
    - 1.2.3.2, 4: `x^(8|11)(a+bx^3+cx^6)^(1/2|3/2)`.
    - 1.2.1.2: e2441 `(d+ex)^(3/2) sqrt(q)`.
  - **Final.** r117 (Rubi's `GtQ[m,1]` reduction) ends every 30 s list.
    - **At 120 s.** The subst top fires for 9 (1_2_2_2_r8 ×6, 1_2_3_2_r6 ×3), so rubi returned.
    - **Still ending in r117 (MID-CHAIN).** e936, e202.
    - **Top-level r117.** e2441.
  - **Nested.** 1_1_2_1_r13, 1_2_1_1_r15/r6/r18, 1_2_1_2_r15, 9_1_r8, 1_2_1_9b_r32.
  - **Walls.** P0 verified 2.3–6.3 s. Timeout at 120 s and at the 100 s re-check. All arms time out.
  - **P0.** 1_2_1_6_r1 → 1_2_2_2_r8 (7; its `IGtQ[p,−2]` read bare), 1_3_3_r15 (4), r117 (1).
  - **Defective tree.** Verified 8 (fix-induced, route not traced). Timeout 4 on today's chains (e2441, e955,
    e956, e1116).

  — follows from: the IGT translation fix (Rubi's reading); the cost is verification — [fixed-defect: none]
- class 1 g18 (12 entries, deterministic, final timeout top=1_2_1_3_r51): **VERIFY-TIMEOUT.**
  - **Integrands.**
    - 1.2.1.3, 10: `(b+2cx) q^(k/2)/(d+ex)^j` (e1551, e1570, e1633); `(5−x)(2+5x+3x^2)^(k/2)/(3+2x)` (e2411,
      e2423, e2437, e2452); factorable `(f+gx)(cd^2−bde−be^2x−ce^2x^2)^(k/2)/sqrt(d+ex)` (e2234, e2243, e2253).
    - 1.2.1.4: e856/e864 `(f+gx) q^(1/2|3/2)/(d+ex)`.
  - **Final.** The top-level r51 (Rubi's `GtQ[p,0]` reduction) is in all 12 30 s lists; e1570 adds r50 at 120 s.
  - **Nested.** 1_1_2_1_r13, 1_2_1_1_r15, 1_2_1_2_r99, 1_2_1_3_r89 (6); 1_1_2_3_r48, 1_2_1_2_r93, 9_1_r8,
    1_2_1_9b_r32 (+ 1_4_1_r18, 1_1_2_3_r42, 1_2_1_3_r56/r89, 1_2_1_2_r109) (4); 1_4_1_r18 (e856, e864).
  - **Walls.** P0 verified 1.7–12.1 s. 120 s: timeout 11, e2234 unverified 41.7 s; the 100 s re-check matches.
  - **Arms.** r2: timeout 12. r3: timeout 11, unverified 1. r4: timeout 10, unverified 2.
  - **P0.** r51/r50 top 5 (nested 1_2_1_9b_r5 or 1_2_1_1_r5, their `IGtQ` read bare), 1_2_1_9_r22 4,
    1_3_3_r6 3.
  - **Defective tree.** Verified 11 (fix-induced, route not traced). Deferred e1633 via 1_2_1_3_r15 (bare
    `is(p > 0)`).
  - **Factorable entries.** Rubi's EqQ family is not taken (EqQ reading).

  — follows from: the IGT translation fix (Rubi's reading); e2234/e2243/e2253 also the EqQ reading (inferred);
  the cost is verification — [fixed-defect: none]
- class 1 g19 (12 entries, deterministic, final timeout top=1_2_2_4_r9): **VERIFY-TIMEOUT.**
  - **Integrands.** 1.2.2.4:
    - `x^(3|5|7|9)(A+Bx^2)/(a+bx^2+cx^4)^(2|3)` (e113, e114, e125–e128);
    - `(A+Bx^2)/(x(…)^2)` (e116);
    - `(2+3x^2)(3+5x^2+x^4)^(1/2|3/2)/x^j` (e146, e147, e161, e162);
    - `x^3 sqrt(1−x^2)/(a+bx^2+cx^4)` (e377).
  - **Final.** The top-level r9 (subst x^2, `IntegerQ[(m−1)/2]`) is in all 12 30 s lists. Timeout at 120 s and
    at the 100 s re-check.
  - **Nested.** 1_1_2_1_r13, 1_2_1_1_r12/r15, 1_2_1_2_r3/r9/r97/r99/r80, 1_2_1_3_r44/r47/r49/r50/r53/r54/r55/r89.
    For e377: 1_1_2_1_r15, 1_2_2_3_r24, 1_2_1_3_r17/r16. The corpus answers are atanh/atan forms, consistent
    with the 1_1_2_1_r13 branch taken.
  - **P0.** Verified 3.1–5.3 s via 1_2_1_6_r1/r4 → 1_2_2_6_r2 (6), 1_2_2_6_r2 (5), or 1_2_1_9b_r5 → r9 (e377).
  - **Defective tree.** Timeout 8 on today's chains. Verified 4 (e146, e147, e161, e162; fix-induced, route not
    traced).
  - **Arms.** All time out.

  — follows from: not determined from the traces which change moved the 4 fix-induced entries; the 8 others time
  out on the same chain on the defective tree; the cost is verification — [fixed-defect: none]
- class 1 g20 (11 entries, deterministic, final timeout top=1_1_2_2_r25): **VERIFY-TIMEOUT.**
  - **Integrands.** 1.1.2.2 `x^(−2|−4|−6)(a+bx^2)^(−1/3|−1/6|−5/6)` and `x^(−2|−4|−6)(−2+3x^2)^(−3/4)`.
  - **Final.** The top-level r25 (Rubi's `LtQ[m,−1]` reduction) is in all 11 30 s lists. Timeout at 120 s and at
    the 100 s re-check.
  - **Nested.** 1_1_2_1_r27/r28/r30/r26/r8/r29 substitutions, then either 1_1_3_2_r46, 1_1_3_7_r31, 1_1_3_1_r31
    (`%mr_negQ(a)`, elliptic with `2−sqrt(3)`) or 1_1_3_1_r32 (`%mr_posQ(b/a)`).
  - **Sign readings.** The substituted constant is −a, or −2 (e909–e911). NegQ is True under Rubi's PosAux and
    the fixed port.
  - **P0.** Verified 0.6–3.8 s with top 1_1_2_2_r6 (9), 1_1_2_11_r4 or 1_1_2_2_r29.
  - **Defective tree.**
    - **Timeout 6, top 1_1_2_2_r6.** Its `ILtQ[Simplify[(m+1)/2+p+1],0]` was read `is(… < 0)` on −1/4 … −7/3
      (e909–e911, e1029–e1031). `%mr_iLtQ` now rejects r6, as Rubi does, and Rubi's r25 answers.
    - **Verified 5** (e712, e713, e1022–e1024; fix-induced, route not traced).
  - **Arms.** r4 (mr_model_flags=false): verified 8 (e712, e713, e909–e911, e1029–e1031), timeout 3
    (e1022–e1024). r2/r3: timeout 11.

  — follows from: the IGT translation fix (Rubi's reading) + the model flags (r4 verifies 8); the cost is
  verification — [fixed-defect: none]
- class 1 g21 (10 entries, deterministic, final deferred top=1_2_2_3_r99): **Catch-all alone.** 1_2_2_3_r99 (the
  1.2.2.3 `Unintegrable` rule, no condition) answers alone (nfires=1, 0.2–0.4 s).
  - **Integrands.** 1.2.2.3 8 `(d+ex^2)/(1±4x^2+4x^4)` and `(d+ex^2)/(1±2x^2+x^4)` (b^2−4ac = 0, p = −1);
    1.2.2.4 e61/e71 `(d+ex^2)(1+2x^2+x^4)^5`.
  - **Port rules for b^2−4ac = 0.** 1_2_2_1_r1/r2 and 1_2_2_3_r5/r6 test `%mr_eqQ(b^2 - 4*a*c, 0)` on numbers,
    which reads True, but they require a non-integer p. Rubi's first rule for these integer-p entries is not
    identified here.
  - **P0.** Verified 1.9–6.3 s via 1_3_3_r4 (5), 1_3_2_r13 (2), 1_2_2_5_r1 (2) or 1_4_2_r24 (1).
  - **Defective tree.** Deferred 10 via r99 alone, so the fixes did not change the route.
  - **Arms.** All deferred.

  — follows from: not determined from the traces — [fixed-defect: undetermined — Rubi's first rule for these
  perfect-square quartics (and for e61/e71, p = 5) and its decline reason on the fixed core (a decline trace)]
- class 1 g22 (10 entries, deterministic, final deferred top=1_4_1_r18): **EXPAND-NOUN.**
  - **Final.** 1_4_1_r18 alone (nfires=1, 0.2–3.3 s). r18 is Rubi 1.4.1's
    `u Px^p Qx^q → u PolyQuotient[Px,Qx]^p Qx^(p+q) /; PolyRemainder = 0 && IntegerQ[p] && LtQ[p q,0]`. The
    rewrite is algebraically equal, and its nested `mr_int` has no fire.
  - **Integrands.**
    - 1.1.1.2, 4: `x^k/((a+bx)(cx^2)^(1/2|3/2))`.
    - 1.1.1.3 e373 `b^2 x^m/(b+ax^2)^2`; 1.1.2.8 e58 `A(cx)^m/(a+bx^2)`.
    - 1.1.3.8 e63–e65 `(ac+adx+bcx^3+bdx^4)/(a+bx^3)^(5/2|7/2|9/2)`; 1.2.2.5 e64.
  - **P0.** Verified 3.7–11.1 s via the manual 9.1 `u*(a*x^n)^m` (4), 1_3_4_r21 (3), 1_1_2_9_r104, 1_2_1_9b_r5 or
    1_2_2_5_r3.
  - **Defective tree.** Deferred 10 via r18 alone.
  - **Arms.** r3 (mr_cond_retry=false) verified 4 (e881, e889, e373, e58) and deferred 6; r2/r4 deferred. So for
    those 4, r18 accepts only on a retried binding.

  — follows from: condition retry (r18 on a non-first binding, 4 entries); the no-answer is not determined from
  the traces — [fixed-defect: undetermined — EQ-REWRITE at 1_4_1_r18, awaiting probe 16; competing: the
  retried binding's nested integrand has no rule]
- class 1 g23 (10 entries, deterministic, final timeout top=1_2_1_2_r15): **VERIFY-TIMEOUT.**
  - **Integrands.**
    - 1.2.1.2, 3: `(d+ex)(a+bx+cx^2)^(4/3|1/4|5/4)` (e2484, e2512, e2524).
    - 1.2.2.2, 4: `x^3(a+bx^2+cx^4)^(1/2|3/2)`, `x^3/sqrt(…)`, `x^5/(…)^(3/2)` (e922, e938, e957, e983).
    - 1.2.3.2, 3: `x^5(a+bx^3+cx^6)^(1/2|3/2)`, `x^5/sqrt(…)` (e188, e204, e222).
  - **Final.** r15 (Rubi's `NeQ[2cd−be,0] && NeQ[p,−1]` rule) ends the 30 s list.
    - It is top-level for the 3 1.2.1.2 entries, so rubi returned.
    - For the other 7 the subst top fires at 120 s (1_2_2_2_r8 ×3, 1_2_3_2_r6 ×3, 1_2_2_4_r5 for e983).
    - Timeout at 120 s and at the 100 s re-check.
  - **Nested.**
    - e2484: 1_2_1_1_r17 (the denominator-3/4 substitution) → 1_1_3_2_r63 → 1_1_3_1_r30.
    - e2512, e2524: 1_2_1_1_r17 → 1_1_3_1_r32 + 1_2_1_1_r6.
    - The others: 1_1_2_1_r13, 1_2_1_1_r15, 1_2_1_1_r6.
  - **Sign readings.** 1_1_3_1_r30 reads `%mr_posQ(b^2−4ac)` True, and 1_1_3_1_r32 reads
    `%mr_posQ(4c/(b^2−4ac))` True, both through a sum's first term (sibling:%mr_posAux). The corpus answers
    show Rubi reads the same:
    - e2484 carries `2+sqrt(3)` and `-7-4*sqrt(3)` (r30's branch);
    - e2512/e2524 carry `elliptic_f(2*atan(…),1/2)` (r32's).
  - **P0.** Verified 0.9–5.4 s via 1_2_1_1_r5 → r15 (3; its `IGtQ[p,0]` read bare for p = 1/4, 4/3, 5/4),
    1_2_1_6_r1 → 1_2_2_2_r8 (3; its `IGtQ[p,−2]` read bare), 1_3_3_r15 (2), 1_3_4_r20 or 1_2_2_5_r3.
  - **Defective tree.** Verified 7 (fix-induced, route not traced). Timeout 3 (e957, e983, e222) on today's
    chains.
  - **Arms.** r4 verified e2484; otherwise timeout.

  — follows from: the IGT translation fix (Rubi's reading) routing onto Rubi's elliptic reduction; the cost is
  verification — [fixed-defect: none]

## Clearance summary (g1–g23)

Counts are per group; a split group counts under its most severe sub-tag.

**Class 1, g1–g23 (23 groups, 605 entries):** none 16, IGT 0, NEGQ 0, NE 0, MUL 0, collapse 0,
sibling:<port> 0, undetermined 7 (EQ-REWRITE 3, other 4).

Groups whose tag is not `none`:

- g1 — undetermined. NOFIRE timeout: no route observed on any of the 192 entries (16 fix-induced).
- g2 — undetermined (split). 14 entries are `none` via ticket 02; the other 52 have no route observed.
- g7 — undetermined, EQ-REWRITE at 1_2_2_4_r93 (awaiting probe 16).
- g9 — undetermined, EQ-REWRITE at 1_2_1_3_r109 (awaiting probe 16). Upstream, r88 is blocked by the EqQ
  reading.
- g15 — undetermined. The declines of the 1.2.2.6/1.2.2.7 elliptic rules and of the 1.2.1.3 symbolic-p rules are
  not traced.
- g21 — undetermined. Rubi's first rule for the perfect-square quartics is not identified; no route observed.
- g22 — undetermined, EQ-REWRITE at 1_4_1_r18 (awaiting probe 16).

**Ticket 02 (GeQ/GtQ reading): 2 groups.** g13 as a whole (15 entries; 1_1_3_1_r24 / 1_1_3_2_r40), and g2's
sub-bullet (14 of 66 entries; 1_1_2_1_r18/r32, 1_1_2_2_r40).

**EqQ/NeQ reading (unlisted, not ticketed; inferred, not measured).** `%mr_eqQ`/`%mr_neQ` use a syntactic zero
test, which misreads the unexpanded factorable-quadratic coefficients.

- **Whole groups.** g3 (38) and g12 (16; 9 answers divide by a zero-valued expression).
- **Sub-entries.** g4 (3), g8 (16), g10 (3), g18 (3).
- **Also on the route.** Upstream of g9 (18), and in g1's 1.2.1.3 e2237–e2261.

These groups carry `none` on the fix clearance; the reading needs a ticket and a measurement.

**Fix-induced entries (PASS on the defective tree): 180.** g1 16, g2 3, g3 32, g4 12, g5 17, g6 10, g8 14,
g10 12, g11 10, g12 7, g13 8, g16 4, g17 8, g18 11, g19 4, g20 5, g23 7.

- **Defective-tree routes.** None is traced. Where the P0 route rested on an integer test read as a bare
  comparison, the fixed `%mr_iGtQ`/`%mr_iLtQ` reading rejects it, as Rubi does: g2 e1060–e1064, g3, g4, g8, g10,
  g11, g12, g16–g18, g20, g23. g5 moved onto Rubi's PosQ reading.
- **Why they fail afterwards.**
  - Rubi's own route costs more than the cap (VERIFY-TIMEOUT / MID-CHAIN).
  - The EqQ reading blocks Rubi's factorization.
  - The GtQ reading (ticket 02) blocks Rubi's partial-fraction or Subst rule.
  - The verdict is the zero chain on AppellF1 (g6).

**No group is explained by a fixed defect** under the checked readings.

## Diagnostic 16 re-reading (class 1)

> Evidence: `probes/matcher/16-seen-guard-trace.class1.out` (2026-09-15 12:34 UTC, Maxima
> branch_5_50_base_84_g4204fb669, SBCL 2.6.7, git HEAD 560b4a5, fixed core `b98e4748…`, P0 core `5ef9b3bc…`;
> entry set `probes/matcher/16-seen-guard-trace.class1.tsv`, parts A+B+C, 186 entries;
> `Results: 179 passed, 7 failed`, all 7 in part B). This re-run replaced the 12:22 A+C-only run. Every g7/g9/g22 row
> (hit, trace class, control class, answer, P0 route) is unchanged from that run.
> Each row reads: ratsimp-only seen hit (trace arm), then the fixed-core class, then the class under the exact-only
> control (probe-local `%mr_seenp` = exact `member`: a DIAGNOSTIC ARM, not a proposed fix), then the P0 route.
> The rule is the one the class 2/3 re-reading used: `collapse` when the hit cuts the route **and** the control moves
> the class toward PASS. A hit that cuts the route but leaves the class unchanged is called collapse-type and tagged
> `none`. Every trace-arm class equals probe 10's final30 class.

- class 1 g7: undetermined → **collapse(non-9.1 site 1_2_2_4_r93)**, with the control **not reaching PASS** (0/20).
  - **Hit.** All 20 entries: ratsimp hit on r93's nested `mr_int` of its two-term `(d+ex^2)` distribution,
    against the live top-level integrand (#2@#1).
  - **Control.** The sum dispatches (1_4_1_r7) and the class leaves the top-level noun: deferred → unverified 6
    (e204, e205, e208, e209, e225, e226) or contains-noun 14.
    - The unverified entries answer AppellF1 terms (1_2_2_2_r35 → 1_1_2_4_r66), the g6 zero-chain case.
    - The contains-noun entries end in the 1_2_2_6_r9 `Unintegrable` catch-all, e.g. e206
      `'unintegrable[(e*(f*x)^(3/2)*sqrt(…))/f^2,x]+'unintegrable[(d*sqrt(…))/sqrt(f*x),x]`.
  - **Excluded.** The competing readings: the expansion is a sum, not an exact repeat, and there is no
    `%mr_intSum` fault.
  - **P0.** 1_2_2_6_r3 in **pass 2** (after the `%mr_seen` pop), verified. P0 never ran r93.
- class 1 g9: undetermined → **none** (a collapse-type hit that does not decide the verdict).
  - **Hit.** All 18 entries: ratsimp hit on r109's nested `mr_int` (#2@#1).
  - **The expansion is not a sum.** It returns the single term `sqrt(q)/(e*x^3+d*x^2)`, the denominator
    multiplied out, so no partial fractions.
  - **Control.** That term dispatches to 1_4_1_r25, which refactors it to `sqrt(q)/(x^2*(e*x+d))`. 1_4_2_r15 then
    re-dispatches the identical integrand, and the exact test cuts it (e442 #4 exact@#3). Still deferred, now with
    `'integrate` of the refactored form (18/18).
  - **Mechanism.** r109's `%mr_expandIntegrand` does not produce the partial-fraction sum, and an identity
    re-dispatch at 1_4_2_r15 follows. There is no `%mr_intSum` fault. The EqQ reading upstream (r88 declining)
    stands as before.
  - **P0.** 1_3_3_r6 in pass 1, via 1_4_2_r25, verified (P0 shows its own ratsimp hit #3@1_4_2_r25).
- class 1 g22: undetermined → **collapse(non-9.1 site 1_4_1_r18)**, with the control **reaching PASS on 8/10**.
  - **Hit.** All 10 entries: ratsimp hit on r18's nested `mr_int` of the `PolyQuotient` rewrite (#2@#1).
  - **Control, 8 PASS.** Verified: 1.1.1.2 e879, e887; 1.1.3.8 e63, e64, e65; 1.2.2.5 e64. Expected: 1.1.1.3 e373,
    1.1.2.8 e58.
  - **Control, 2 unchanged.** 1.1.1.2 e881 and e889 stay deferred with the same answer. Their rewrite
    `1/((b*sqrt(c)*x+a*sqrt(c))*abs(x))` (the `abs(x)` coming from `sqrt(c*x^2)`) finds no rule: nofire, then the
    integrate fall-through. That is a no-rule mechanism, independent of the seen test.
  - **P0.** Pass 2 for 7 of the 10 (9_1_r16 ×4, 1_1_2_9_r104, 1_2_1_9b_r5, 1_2_2_5_r3). 1.1.3.8 e63–e65 went via
    1_3_4_r21 in pass 1. P0 never ran r18 at the top.
