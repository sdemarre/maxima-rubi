# P5b mechanism lines — class 1, part C (g172–g262, NEW ERRORS, NEW TIMEOUTS)

> Translation fixes, Task 7 Step 4. One line per probe-10 GROUP, plus NEW ERRORS and NEW TIMEOUTS, each
> group with its defect-clearance tag.
> Reads: `probes/matcher/10-p5b-attribution.class1.summary.out` lines 3781–4584 (groups g172–g262), 4585–4621
> (`NEW ERRORS 35`), 4622–5666 (`NEW TIMEOUTS 1044`), and the raw legs `…class1-{final30,p0,final120,newerror}.out`.
> Written 2026-09-15 by read-only analysis (no Maxima run). Cores: fixed `b98e4748784738cb78f0163a97d4cf5f`
> (P5b final record `test/corpus_class1.p5b-run1.out`), P0 `5ef9b3bc5ee07ffac0e76f1fea54fbac`.
> 1.2.1.4 e810 is not in this range (it is at summary line 2958).

Evidence used beyond the summary, and how to read the lines:

- **Arms and records.**
  - `r2`/`r3`/`r4` = `test/corpus_class1.p5b-run{2,3,4}.out` (mr_flat_wide=true / mr_cond_retry=false /
    mr_model_flags=false).
  - `p5` = the defective tree's record `test/corpus_class1.p5-run1.out`.
  - `rc100` = the 100 s re-check `test/corpus_class1.p5b-final.timeout-rerun/corpus_class1.p5b-run1.timeout100s.out`.
  - "All arms X" means r2/r3/r4 all read X.
- **Route comparison with the defective tree.** "Same route as p5" means the entry's P5b fire list equals its
  fire list in `10-p5-attribution.class1.summary.out`. That file's mechanism lines
  (`10-p5-attribution.mechanisms-class1-{a,b,c}.md`) are cited by their p5 group id.
- **Fix-induced entries** (PASS on p5, FAIL on P5b). Their defective-tree routes are not traced, because probe 10
  on the defective tree re-ran only P→F entries.
  - The 24 single-entry groups g172, g175, g178, g181, g183, g199, g200, g205, g206, g207, g208, g214, g215, g216,
    g223, g225, g229, g238, g241, g247, g249, g250, g251 and g261.
  - 33 of g259's 111 entries.
- **Sign readings.** Read from the code, not measured: `%mr_posAux` (`maxima_rubi_utils.mac:445–471`) and
  `%mr_negQ` (:476–478); Rubi `PosAux` as quoted there.
- **EQ-REWRITE.** As defined in `10-p5b-attribution.mechanisms-class2-3.md`. Every EQ-REWRITE group here has
  an ExpandIntegrand-type rewrite (or an equal-form `mr_sum` split) whose result is a sum, and no nested fire. A
  dispatched sum always fires 1_4_1_r7, so the competing explanation is always a `%mr_intSum` fault. Where P0
  fired the same rule, P0's nested 1_4_1_r7 fire is the P0 counter-example.
- **Ticket 02 (bare `is(A op B)` for GtQ/LtQ/GeQ/LeQ).**
  - Under `and`/`or` an `is(sym > 0)` reads `unknown` and does not accept. Rubi's GtQ on a symbol is False, so
    those sites agree with Rubi. Only a `not(is(…))` site with a symbolic argument can diverge.
  - Indirect evidence that the dispatcher does not accept `not(is(sym > 0))`: on the defective tree,
    `1_1_3_8_r29` (`… and not(is(m > 0))`) did not fire on 1.1.3.8 e586 (p5 nfires=0). The fixed
    `not(%mr_iGtQ(m, 0))` fires on the same binding (g190). This is inferred, not measured.
- **ZERO.** Some 1.2.2.2 integrands are written with `2+2a-2(1+a)` (or `2+2c-2(1+c)`) as a coefficient.
  - Maxima does not distribute that coefficient, so the pattern binds a trinomial whose coefficient is zero
    but does not look zero.
  - Mathematica evaluates it to 0, so Rubi sees a binomial.
  - `%mr_neQ` (utils:370) tests `is(u - v = 0)` syntactically and reads the coefficient as nonzero.
- **Strict EqQ/NeQ.** `%mr_eqQ` (utils:369) and `%mr_neQ` compare `is(u - v = 0)` without expanding (comment
  :355–368). A symbolic zero that needs expansion reads "not equal" where Rubi's EqQ holds. This is inferred from
  the rule text wherever it is used below. It is not among the fixed translations.
- **Catch-alls.** These rules answer `Unintegrable` unconditionally (repl `mr_unintegrable`, cond at most
  `%mr_polyQ`/`%mr_eqQ(n2,2n)`): 1_2_2_6_r9, 1_2_1_3_r112, 1_2_3_5_r24, 1_2_3_4_r102, 1_1_2_8_r123,
  1_2_2_3_r99, 1_1_2_5_r39, 1_1_1_4_r42.
- **Timing shapes.**
  - VERIFY-TIMEOUT: the 30 s fire list ends with the top-level rule, so rubi returned and the cap went to
    verification.
  - MID-CHAIN: the top-level rule is absent at 30 s and 120 s.
- **Split groups.** None in this range (every group but g259 has one entry).

## Class 1 (g172–g262)

- class 1 g172 (1 entry, deterministic, final contains-noun top=1_2_2_2_r16): **Fix-induced** (p5 verified
  3.8 s). 1.2.2.2 e994 `x^4/sqrt(2+2a-2(1+a)+bx^2+cx^4)` (ZERO; the corpus answer is a 3-step binomial form).
  - **Route.** 1_2_2_2_r16 (`is(m > 3)`, m=4) binds the ZERO trinomial. Its reduced integral reaches the 1.2.2.6
    catch-all 1_2_2_6_r9, which leaves the marker (2.1 s).
  - **P0.** 1_1_4_4_r11, 1_4_1_r34, 1_3_2_r1 (7.5 s).
  - **Arms.** All contains-noun.
  - **Defective route (plausible, not traced).** The 1.2.2.6 rule ahead of r9 that takes such a p=-1/2
    sub-integral is 1_2_2_6_r3 (`%mr_iGtQ(p,-2)`). It is False now, as Rubi's `IGtQ[p,-2]` is. Its defective
    form was `is(p > -2)`.

  — follows from: ZERO corpus form, with the IGT fix removing a defective-reading route (inferred) —
  [fixed-defect: none]
- class 1 g173 (1 entry, deterministic, final contains-noun top=1_2_2_2_r8): 1.2.2.2 e1115 `x^7(a+bx^2+cx^4)^p`.
  Same route as p5. 1_2_2_2_r8 (x^2 substitution) → 1_2_1_2_r117 (binds x^3 as `(0+1·x)^3`; `is(m > 1)`, m=3) →
  nested 1_2_1_3_r112 (catch-all) → marker (1.0 s). P0: r8 alone (2.5 s). All arms contains-noun. The corpus
  answer (4 steps) has no Unintegrable. No site reads a symbol. — follows from: faithful Optional binding (why the
  reduced 1.2.1.3 integral reaches the catch-all is not determined) — [fixed-defect: none]
- class 1 g174 (1 entry, deterministic, final contains-noun top=1_2_2_3_r23): 1.2.2.3 e6 `(2-3x^2)/(4+9x^4)`.
  Same route as p5 (p5 g176). 1_2_2_3_r23 replaces P0's r22, which bound b=0 (G-1). Its `%mr_negQ(d*e)` is
  NegQ[-6], True in both. Its quadratic sub-integrals reach 1_2_3_5_r24 (catch-all, `x^n` with n=1) → marker. All
  arms contains-noun. — follows from: faithful Optional binding (P0 degenerate binding lost) — [fixed-defect: none]
- class 1 g175 (1 entry, deterministic, final contains-noun top=1_2_2_3_r26): **Fix-induced** (p5 verified
  1.1 s). 1.1.3.8 e156 `(a+cx^2)/(2+3x^4)`.
  - **Route.** 1_2_2_3_r26 (`%mr_negQ(-a c)` = NegQ[-6], True in both) → `(q±3x^2)/(2+3x^4)` → 1_2_2_3_r23/r20,
    1_4_1_r24, 1_2_1_1_r11, 1_1_2_1_r11. A quadratic sub-integral reaches 1_2_3_5_r24 (catch-all) → marker (7.2 s).
  - **Arms.** r3 verified 1.9 s: the catch-all accepts only on a retried binding, as in class 2 g8. r2/r4
    contains-noun.
  - **P0.** 1_2_1_6_r1, 1_2_2_3_r19/r22/r26 (6.1 s).
  - **Sites.** The sign sites read numbers.

  — follows from: condition retry; the defective route is not traced — [fixed-defect: none]
- class 1 g176 (1 entry, deterministic, final contains-noun top=1_2_2_3_r64): 1.2.2.3 e400 `(c+ex^2)^3(a+cx^2+bx^4)^p`.
  Same route as p5 (p5 g177). r64 (`%mr_iGtQ(q,1)`, q=3) → nested 1_2_3_5_r24 (catch-all) → marker (10.1 s). r3
  verified 1.1 s; r2/r4 contains-noun. — follows from: condition retry — [fixed-defect: none]
- class 1 g177 (1 entry, deterministic, final contains-noun top=1_2_2_3_r66): 1.2.2.3 e228
  `sqrt(1+x^2+x^4)/(1+x^2)`. **The IGT fix changed the route.**
  - **p5.** 1_2_2_3_r11 alone (deferred). Its `is(p > 0)` accepted p=1/2 (p5 g23 [defect: IGtQ]).
  - **Fixed core.** r11 declines, as Rubi's `IGtQ[1/2,0]` does. Rubi's r66 answers (`%mr_iGtQ(p+1/2,0)`, p+1/2=1),
    which is also P0's top.
  - **Nested.** 1_2_2_3_r68, 1_2_2_7_r18, 1_1_2_1_r10 (atan), 1_2_2_1_r16 (`%mr_posQ(c/a)` on 1), then the 1.2.2.6
    catch-all 1_2_2_6_r9 → marker (2.6 s). At that point P0 fired 1_2_2_8_r18 and 9_1_r9.
  - **Arms.** All contains-noun.

  — follows from: the IGT fix (Rubi's route), plus a 1.2.2.6 catch-all binding on a sub-integral (which one is
  not traced) — [fixed-defect: none]
- class 1 g178 (1 entry, deterministic, final contains-noun top=1_2_2_3_r79): **Fix-induced** (p5 verified
  3.0 s). 1.2.2.3 e241 `1/((1+x^2)(1+x^2+x^4)^(3/2))`. The g177 chain, with top r79 (`%mr_iLtQ(p+1/2,0)`,
  p+1/2=-1). It ends in 1_2_2_6_r9 (catch-all) → marker (2.3 s), where P0 fired 1_2_1_6_r1, 1_2_2_6_r2,
  1_2_2_8_r20 (3.9 s). All arms contains-noun. As in g172, 1_2_2_6_r3's defective `is(p > -2)` is the plausible
  defective route (not traced). — follows from: as g177 — [fixed-defect: none]
- class 1 g179 (1 entry, deterministic, final contains-noun top=1_2_2_4_r10): 1.2.2.4 e5 `(d+ex^2)(a+cx^4)^5/x`.
  Same route as p5 (p5 g180). 1_2_2_4_r10 (x^2 substitution) → 1_1_2_8_r20 (`is(p > 0)`, p=5) → 1_1_2_8_r123
  (catch-all) → marker. P0: 1_2_2_6_r2 → 1_1_2_8_r20. All arms contains-noun. — follows from: faithful binding
  (NOUN) — [fixed-defect: none]
- class 1 g180 (1 entry, deterministic, final contains-noun top=1_2_2_5_r3): 1.3.1 e287
  `(1+2x+x^2+x^3)/(1+2x^2+x^4)`. Same route as p5 (p5 g181). 1_2_2_5_r3 (Pq split) → 1_2_1_6_r1
  (`%mr_iGtQ(p,-2)`, p=-1), 1_2_2_4_r5 → 1_2_2_3_r99 (catch-all) → marker. P0: 1_3_2_r13, 1_2_1_6_r1, 1_2_2_6_r2.
  All arms contains-noun. — follows from: not determined from the traces — [fixed-defect: none]
- class 1 g181 (1 entry, deterministic, final contains-noun top=1_2_2_8_r18): **Fix-induced** (p5 verified
  5.4 s). 1.2.2.3 e413 `(f+gx)/((d+ex)sqrt(-a+bx^2+cx^4))`.
  - **Route.** 1_2_2_8_r18 (`is(expon(Px) <= 3)`) → 1_2_2_7_r30, 1_2_2_3_r78, 1_2_2_1_r17, 1_1_2_3_r41,
    1_2_2_4_r93, then the 1.1.2.5 three-quadratic catch-all 1_1_2_5_r39 → marker (4.2 s).
  - **Sign branch.** 1_2_2_7_r30, 1_2_2_3_r78 and 1_2_2_1_r17 all read `%mr_negQ(c/a)` on `c/(-a)`, which is True
    in Rubi and in the port. The corpus answer's `1+2cx^2/(b∓sqrt(b^2+4ac))` elliptic form is that branch. The
    defective strict sign read it False.
  - **P0.** 1_4_2_r24, 1_2_2_8_r18 (1.7 s).
  - **Arms.** All contains-noun.

  — follows from: the NEGQ fix (Rubi's branch) exposing a 1.1.2.5 catch-all sub-integral (why it reaches the
  catch-all is not determined) — [fixed-defect: none]
- class 1 g182 (1 entry, deterministic, final contains-noun top=1_2_3_4_r101): 1.2.3.4 e91
  `(fx)^m(a+cx^2n)^p/(d+ex^n)^2`. Same route as p5 (p5 g183). r101 (`%mr_iLtQ(q,0)`, q=-2) expands. The sum
  dispatches (1_4_1_r7, 9_1_r12) and a term reaches 1_2_3_4_r102 (catch-all) → marker (26.4 s). P0: the manual
  9.1 r16. All arms contains-noun. — follows from: 9.1 regeneration — [fixed-defect: none]
- class 1 g183 (1 entry, deterministic, final contains-noun top=1_2_4_2_r19): **Fix-induced** (p5 verified
  13.1 s). 1.2.4.2 e116 `1/(x^(3/2)sqrt(ax+bx^3+cx^5))`.
  - **Route.** Rubi's 1_2_4_2_r19 → 1_4_1_r34 → 1_3_3_r19 → 1_2_3_6_r12 → 1_2_2_6_r9 (catch-all) → marker (3.3 s).
    The sites read numbers: r19's `%mr_posQ(n-q)`, `%mr_iGtQ(n,0)`, `is(p >= -1)`, `is(p < 0)`, and 1_3_3_r19's
    `%mr_posQ(s-r)`.
  - **P0.** 1_3_3_r10, 1_4_1_r34 (2.4 s).
  - **Arms.** All contains-noun.
  - **Defective route.** As g172 (1_2_2_6_r3, inferred).

  — follows from: faithful binding plus the 1.2.2.6 catch-all; the defective route is not traced —
  [fixed-defect: none]
- class 1 g184 (1 entry, deterministic, final deferred top=1_1_1_2_r34): 1.2.2.2 e1035
  `1/(x sqrt(a+(2+2c-2(1+c))x^4))` (ZERO; Rubi: `log(x)/sqrt(a)`). Same route as p5 (p5 g184). 1_1_2_1_r15, then
  1_1_1_2_r34 (hypergeometric), gives a top-level noun. P0: 1_2_2_8_r1 chain. All arms deferred. — follows from:
  ZERO corpus form — [fixed-defect: none]
- class 1 g185 (1 entry, deterministic, final deferred top=1_1_1_4_r42): 1.1.1.4 e129
  `(a+bx)^m(c+dx)^(-3-m)(e+fx)(g+hx)` (Rubi 3 steps). Same route as p5 (p5 g185).
  - **Final core.** The 1.1.1.4 catch-all 1_1_1_4_r42 answers `Unintegrable` alone (0.1 s).
  - **P0.** 1_1_1_4_r19 (2.3 s).
  - **Candidate Rubi rule.** 1_1_1_4_r4, ahead of r42, has cond `is(m < -2) or %mr_eqQ(m+n+3,0) and
    not(is(n < -2))`.
    - m+n+3 cancels to 0.
    - n=-3-m is symbolic, so Rubi's `Not[LtQ[n,-2]]` is True and r4 accepts in Rubi. Its
      `(…)(a+bx)^(m+1)(c+dx)^(n+1)` term has the shape of the corpus answer's first term.
    - The port reads `not(unknown)`, and r4 did not fire.
  - **Arms.** All deferred.

  — follows from: GeQ/GtQ reading (ticket 02) — inferred from the rule text — [fixed-defect: none]
- class 1 g186 (1 entry, deterministic, final deferred top=1_1_1_5_r5): 1.1.1.5 e29
  `(c+dx)^n(A+Bx+Cx^2+Dx^3)/(a+bx)`. Same route as p5.
  - **Final core.** 1_1_1_5_r5 fires alone (2.3 s): `%mr_iGtQ(m,-2)` with m=-1, and `is(expon(Px) > 2)` with 3;
    Rubi's conditions hold. Its ExpandIntegrand of a cubic over (a+bx), times (c+dx)^n, is a sum. No nested fire;
    the answer is a top-level noun.
  - **P0.** 1_1_1_5_r8 (3.6 s).
  - **Arms.** All deferred.

  — follows from: not determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at 1_1_1_5_r5,
  awaiting probe 16; competing: a `%mr_intSum` fault on the dispatched sum]
- class 1 g187 (1 entry, deterministic, final deferred top=1_1_2_11_r3): 1.1.2.8 e61 `(cx)^m(A+Bx+Cx^2)/(a+bx^2)`.
  Same route as p5.
  - **Final core.** 1_1_2_11_r3 (`%mr_iGtQ(p,-2)`, p=-1) fires alone (1.9 s); its ExpandIntegrand sum has no
    nested fire.
  - **P0.** 1_2_1_9b_r5 with 1_1_2_3_r1, 1_2_1_9b_r1 and 1_4_1_r7: the sum dispatched (7.4 s).
  - **Arms.** r3 verified 1.1 s; r2/r4 deferred.

  — follows from: condition retry (r3) — [fixed-defect: undetermined — EQ-REWRITE at 1_1_2_11_r3, awaiting probe
  16; competing: a `%mr_intSum` fault]
- class 1 g188 (1 entry, deterministic, final deferred top=1_1_2_9_r23): 1.2.1.4 e611 `sqrt(d+ex)/((a+cx^2)sqrt(f+gx))`.
  Same route as p5. 1_1_2_9_r23 (`%mr_iGtQ(m+1/2,0)`=1, 3-arg ExpandIntegrand into partial fractions) fires alone
  (0.4 s) with no nested fire. P0: 1_2_1_8_r2, 1_4_1_r7, r23 — the sum dispatched. All arms deferred. — follows
  from: not determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at 1_1_2_9_r23, awaiting probe
  16; competing: a `%mr_intSum` fault]
- class 1 g189 (1 entry, deterministic, final deferred top=1_1_3_8_r18): 1.1.3.8 e553 `x^3(c+dx+ex^2+fx^3)(a+bx^4)^p`.
  Same route as p5 (p5 g193). 1_1_3_8_r18 (`%mr_iGtQ(n/2,0)`=2) does an equal-form `mr_sum` split, a sum. It fires
  alone (2.5 s) with no nested fire. P0: 1_1_3_7_r46, 1_4_1_r20, 1_1_2_11_r1, 1_2_1_9b_r29, 1_2_2_6_r2, 1_2_2_5_r3
  (5.6 s). All arms deferred. — follows from: not determined from the traces — [fixed-defect: undetermined —
  EQ-REWRITE at 1_1_3_8_r18, awaiting probe 16; competing: a `%mr_intSum` fault]
- class 1 g190 (1 entry, deterministic, final deferred top=1_1_3_8_r29): 1.1.3.8 e586
  `(cx)^m(d+ex+fx^2+gx^3)(a+bx^n)^p`. **The IGT fix changed the route.**
  - **p5.** No fire (p5 g3).
  - **Fixed core.** 1_1_3_8_r29 now accepts: `not(%mr_iGtQ(m,0))` on symbolic m is True, as Rubi's
    `Not[IGtQ[m,0]]` is. It fires alone (1.7 s); its ExpandIntegrand sum has no nested fire.
  - **P0.** The manual 9.1 r16.
  - **Arms.** All deferred.

  — follows from: the IGT fix (Rubi's reading) — [fixed-defect: undetermined — EQ-REWRITE at 1_1_3_8_r29, awaiting
  probe 16; competing: a `%mr_intSum` fault]
- class 1 g191 (1 entry, deterministic, final deferred top=1_2_1_3_r24): 1.2.1.4 e851
  `sqrt(d+ex)/((a+bx+cx^2)sqrt(f+gx))`. Same route as p5. 1_2_1_3_r24 (`%mr_iGtQ(m+1/2,0)`, 3-arg ExpandIntegrand)
  fires alone (0.9 s). P0: 1_2_1_8_r2, 1_4_1_r7, r24 (3.2 s). All arms deferred. — follows from: not determined
  from the traces — [fixed-defect: undetermined — EQ-REWRITE at 1_2_1_3_r24, awaiting probe 16; competing: a
  `%mr_intSum` fault]
- class 1 g192 (1 entry, deterministic, final deferred top=1_2_1_9b_r2): 1.3.2 e569 `(1+x^3)sqrt(1+x)/(1+x^2)`.
  Same route as p5 (p5 g195). The top 1_2_1_9b_r2 divides Pq by d+ex, and its nested dispatch fires
  1_2_1_9b_r6 (`%mr_iGtQ(p,-2)`, p=-1). r6's ExpandIntegrand sum has no nested fire; the answer is a top-level
  noun (1.7 s). P0: 1_2_1_9b_r5, 1_2_1_9_r21, 1_2_1_9b_r1 (3.3 s). All arms deferred. — follows from: not
  determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at 1_2_1_9b_r6, awaiting probe 16;
  competing: a `%mr_intSum` fault]
- class 1 g193 (1 entry, deterministic, final deferred top=1_2_1_9b_r5): 1.2.1.9 e370
  `(d+ex)^m(2+x+3x^2-5x^3+4x^4)/(3+2x+5x^2)`. Same route as p5 (p5 g5). 1_2_1_9b_r5 (`%mr_iGtQ(p,-2)`, p=-1) fires
  alone (2.7 s). P0: the same r5 with nested 1_4_1_r7 (11.1 s). All arms deferred. — follows from: not determined
  from the traces — [fixed-defect: undetermined — EQ-REWRITE at 1_2_1_9b_r5, awaiting probe 16; competing: a
  `%mr_intSum` fault]
- class 1 g194 (1 entry, deterministic, final deferred top=1_2_2_7_r12): 1.2.2.7 e33
  `(A+Bx^2)(d+ex^2)^q/(a+bx^2+cx^4)`. Same route as p5. 1_2_2_7_r12 (`integerp(p)`, p=-1) fires alone (1.7 s). P0:
  r12 with nested 1_4_1_r7 (6.0 s). All arms deferred. — follows from: not determined from the traces —
  [fixed-defect: undetermined — EQ-REWRITE at 1_2_2_7_r12, awaiting probe 16; competing: a `%mr_intSum` fault]
- class 1 g195 (1 entry, deterministic, final deferred top=1_2_2_7_r13): 1.2.2.7 e15 `(A+Bx^2)(d+ex^2)^q/(a+cx^4)`.
  Same route as p5. 1_2_2_7_r13 fires alone (1.3 s). P0: r12 with b=0 (G-1), with nested 1_4_1_r7 (6.0 s). All
  arms deferred. — follows from: not determined from the traces — [fixed-defect: undetermined — EQ-REWRITE at
  1_2_2_7_r13, awaiting probe 16; competing: a `%mr_intSum` fault]
- class 1 g196 (1 entry, deterministic, final deferred top=1_2_3_4_r102): 1.2.3.4 e145
  `(fx)^m(d+ex^n)^q/(a+bx^n+cx^2n)` (Rubi 5 steps, AppellF1). Same route as p5 (p5 g198). The 1.2.3.4 catch-all
  1_2_3_4_r102 answers at top (6.9 s). P0: the manual 9.1 r16. All arms deferred. Which Rubi rule takes e145 is
  not traced. The 1.2.3.4 rules ahead of r102 include r45–r48, whose `not(is(2*c*q - b*c < 0))`-shaped sites read a
  symbolic q. — follows from: 9.1 regeneration — [fixed-defect: undetermined — Rubi's first step for e145 and its
  decline reason on the fixed core (a decline trace); ticket-02 sites in r45–r48 are candidates]
- class 1 g197 (1 entry, deterministic, final deferred top=1_4_3_r56): 1.3.2 e878
  `(1-x^2)/((1-x+x^2)(1-x^3)^(2/3))`. **The IGT fix changed the route.**
  - **p5.** 1_3_3_r7. Its `is(q < 0)` accepted q=-2/3 (p5 g105 [defect: IGtQ]).
  - **Fixed core.** r7 declines. Rubi's 1_4_3_r56 (`%mr_iLtQ(q,0)` with q=-1; denom(p)=3) fires alone (1.3 s). Its
    `1/c^q·Int[ExpandIntegrand[(c^3-d^3x^3)^q(a+bx^3)^p, Px/(c-dx)^q]]` is an equal form (c=1) whose expansion
    is a sum. No nested fire.
  - **P0.** 1_4_1_r7, 1_4_3_r55 (3.9 s).
  - **Arms.** All deferred.

  — follows from: the IGT fix (Rubi's rule) — [fixed-defect: undetermined — EQ-REWRITE at 1_4_3_r56, awaiting probe
  16; competing: a `%mr_intSum` fault]
- class 1 g198 (1 entry, deterministic, final timeout top=1_1_1_2_r14): 1.1.3.2 e2227 `1/(x(a+b sqrt x)^8)`. Same
  route as p5 (p5 g203). Nested 1_1_1_1_r1/r3 and 1_1_1_2_r3/r14 (`%mr_iLtQ(%mr_simp(m+n+2),0)` on integers) fire.
  The top-level sqrt(x) substitution is absent at 30 s and 120 s (MID-CHAIN). P0: 1_1_3_2_r110 (0.7 s). r3 verified
  0.5 s; r2/r4 timeout; rc100 timeout. — follows from: condition retry — [fixed-defect: none]
- class 1 g199 (1 entry, deterministic, final timeout top=1_1_1_3_r59): **Fix-induced** (p5 verified 8.3 s).
  1.1.1.3 e875 `(a+bx)^(1/4)/(x(c+dx)^(1/4))` (Rubi: 11 steps of atan and atanh).
  - **Route.** Rubi's top 1_1_1_3_r59 (`%mr_iLtQ(p,0)`, p=-1) fired at 30 s. Nested: 1_4_1_r18, 1_1_1_2_r32 (x^4
    substitution), 1_1_3_1_r52 (→ `Int[1/(1-bx^4)]`), and 1_1_3_1_r57, the hypergeometric last resort.
  - **Walls.** Timeout at 30 s and 120 s; rc100 timeout. r3 verified 0.9 s; r2/r4 timeout. P0: 1_1_1_3_r61/r62
    (1.8 s).
  - **IGT side.** r57 now accepts `1/(1-bx^4)`: `not(%mr_iLtQ(1/n+p,0))` with 1/n+p=-3/4 is True, as in Rubi. The
    defective `not(is(1/n+p < 0))` was False.
  - **GtQ side.**
    - In Rubi, 1_1_3_1_r24 (`Not[GtQ[a/b,0]]`) precedes r57 and gives the atan/atanh split the corpus shows,
      because a/b=-1/b is symbolic.
    - The port's r24 cond is `not(is(a/b > 0))`, i.e. `not(unknown)`. r23 (`%mr_posQ(-1/b)`) is False in both.

  — follows from: GeQ/GtQ reading (ticket 02), exposed by the IGT fix. The r57 integrand is inferred from r52's
  repl, not traced — [fixed-defect: none]
- class 1 g200 (1 entry, deterministic, final timeout top=1_1_1_3_r6): **Fix-induced** (p5 verified 0.2 s).
  1.1.1.3 e3019 `(a+bx)/((c+dx)^(1/3)(bc+ad+2bdx)^(4/3))` (Rubi 1 step: `3/2(c+dx)^(2/3)/(d^2(…)^(1/3))`).
  - **P0's route, now closed.** P0 answered with 1_1_1_3_r5 (ExpandIntegrand, 0.1 s). Its
    `%mr_iLtQ(n,0) and %mr_iLtQ(p,0) or … %mr_iGtQ(p,0)` is False for n=-1/3 and p=-4/3, as in Rubi.
  - **Rubi's 1-step rule declines.** Rubi's rule is 1_1_1_3_r2: `%mr_eqQ(a d f(n+p+2) - b(d e(n+1)+c f(p+1)), 0)`.
    With e=bc+ad and f=2bd that expression is zero only after expansion, which strict `%mr_eqQ` does not do
    (inferred).
  - **Final route.** r6 (`is(p < -1)`) is top at 30 s. Nested: 1_1_1_2_r31, 1_2_1_1_r17, and the cube-root family
    1_1_3_2_r45 / 1_1_3_7_r29 / 1_1_3_1_r30 (`%mr_posQ(a)`).
  - **Arms and walls.** Timeout; rc100 timeout. r4 verified 2.0 s; r2/r3 timeout.

  — follows from: the IGT fix removing P0's r5 route, plus the strict EqQ reading of Rubi's r2 (inferred); model
  flags (r4) — [fixed-defect: none]
- class 1 g201 (1 entry, deterministic, final timeout top=1_1_1_4_r29): 1.1.1.7 e4
  `(A+Bx)/((a+bx)sqrt(c+dx)sqrt(e+fx)sqrt(g+hx))`. Same route as p5 (slow-correct on p5, g281). 1_4_2_r9, then the
  top 1_1_1_4_r29 at 30 s and 120 s: VERIFY-TIMEOUT. rc100 timeout. P0: 1_4_2_r9, r29, 1_1_1_3_r55, 1_1_1_4_r35,
  9_1_r9, 1_1_1_7_r27 (5.2 s). r3 deferred 0.4 s; r2/r4 timeout. r29's cond holds no fixed-defect site. — follows
  from: not determined which change moves the cost; the cost is in verification — [fixed-defect: none]
- class 1 g202 (1 entry, deterministic, final timeout top=1_1_2_1_r26): 1.1.2.2 e908 `1/(-2+3x^2)^(3/4)`. Same route
  as p5 (p5 g206). The fire list equals P0's (1_1_3_1_r32, 1_1_2_1_r26; P0 0.2 s). The top fired: VERIFY-TIMEOUT.
  rc100 timeout. r4 verified 0.1 s; r2/r3 timeout. `%mr_negQ(a)` reads a=-2 and `%mr_posQ(b/a)` a number. —
  follows from: model flags — [fixed-defect: none]
- class 1 g203 (1 entry, deterministic, final timeout top=1_1_2_1_r30): 1.1.2.2 e1028 `1/(a+bx^2)^(5/6)`. Same route
  as p5 (p5 g207), and the fire list equals P0's (1_1_3_1_r31, 1_1_2_1_r28, r30). VERIFY-TIMEOUT; rc100 timeout.
  r4 verified 0.2 s. After the substitution, 1_1_3_1_r31's `%mr_negQ(a)` reads a number. — follows from: model
  flags — [fixed-defect: none]
- class 1 g204 (1 entry, deterministic, final timeout top=1_1_2_3_r32): 1.1.2.4 e1090
  `1/((-2+3x^2)(-1+3x^2)^(3/4))`. Same route as p5 (p5 g208), and the fire list equals P0's. VERIFY-TIMEOUT; rc100
  timeout. r4 verified 0.3 s. The sign sites read numbers. — follows from: model flags — [fixed-defect: none]
- class 1 g205 (1 entry, deterministic, final timeout top=1_1_2_3_r35): **Fix-induced** (p5 verified 0.3 s).
  1.1.2.3 e113 `(a-bx^2)^(2/3)/(3a+bx^2)^2`.
  - **Route.** The fire list equals P0's (1.8 s): top 1_1_2_3_r35 (`is(p < -1)` and `0 < q < 1` on numbers) at 30 s;
    nested 1_4_1_r23, 1_1_2_1_r27 (cube-root substitution), then 1_1_3_2_r46 / 1_1_3_7_r31 / 1_1_3_1_r31.
  - **Sign branch.** 1_1_3_2_r46, 1_1_3_7_r31 and 1_1_3_1_r31 read `%mr_negQ` on a negated symbol, which is True in
    Rubi and in the port. The strict sign read it False.
  - **Arms and walls.** Timeout; rc100 timeout. r4 verified 0.7 s; r3 deferred 0.5 s; r2 timeout.

  — follows from: the NEGQ fix (P0's and Rubi's branch), plus model flags (r4) — [fixed-defect: none]
- class 1 g206 (1 entry, deterministic, final timeout top=1_1_2_7_r47): **Fix-induced** (p5 verified 0.3 s).
  1.2.1.2 e700 `(2+3x)^3/(4+27x^2)^(1/3)`.
  - **P0.** 1_2_1_6_r1 → 1_2_1_9b_r29 (2.1 s). r1's `%mr_iGtQ(p,-2)` on p=-1/3 is False now, as in Rubi.
  - **Final route.** Rubi's 1_1_2_7_r47 (`is(n > 1)`, n=3) is top at 30 s. Nested: 1_1_2_9_r38 (`not(is(p <= -1))`
    on a number), 1_1_2_1_r27, 1_1_3_2_r46, 1_1_3_7_r31, 1_1_3_1_r31 (numeric a). This builds the corpus's
    elliptic_f / (1±sqrt3) shape.
  - **Arms and walls.** All arms and rc100 timeout.

  — follows from: the IGT fix (Rubi's route); the cost is in verification — [fixed-defect: none]
- class 1 g207 (1 entry, deterministic, final timeout top=1_1_2_7_r64): **Fix-induced** (p5 verified 0.2 s).
  1.2.1.2 e730 `(d+ex)^m/(a+cx^2)^(3/2)`.
  - **Route.** The fire list equals P0's: 1_1_1_4_r47, then Rubi's 2-step AppellF1 rule 1_1_2_7_r64 (P0 verified
    2.0 s). r64 fired at 30 s: VERIFY-TIMEOUT.
  - **Arms and walls.** All arms and rc100 timeout.
  - **Where the difference can be.** r64's cond holds no fixed-defect site. Its repl builds
    `q = %mr_rt(-a/b, 2)`, and `%mr_rt` reaches the changed ports `%mr_posQ`, `%mr_rt_negSumBaseQ`,
    `%mr_splitSum_aux` and `%mr_product_factors`. The corpus answer uses `sqrt(-a)/sqrt(c)`.

  — follows from: not determined from the traces — [fixed-defect: undetermined — the `%mr_rt(-a/c, 2)` form r64
  builds on the fixed core against Rubi's `sqrt(-a)/sqrt(c)` (r64's answer, taken without the verify step, decides
  it; candidate sibling:%mr_rt)]
- class 1 g208 (1 entry, deterministic, final timeout top=1_1_2_8_r106): **Fix-induced** (p5 verified 1.2 s).
  1.2.1.4 e331 `1/(x(d+ex)sqrt(a+cx^2))`.
  - **Route.** The fire list is P0's minus 1_1_1_4_r46 (P0 0.4 s): 1_1_2_1_r15, 1_1_1_2_r32, 1_1_1_3_r15,
    1_1_2_4_r20, 1_1_2_3_r12, and the top 1_1_2_8_r106 at 30 s: VERIFY-TIMEOUT.
  - **Sign branch.** 1_1_2_1_r15's `%mr_negQ(a/b)` reads the negated-symbol ratio as True in Rubi and in the port.
    That gives the corpus's `atanh(sqrt(a+cx^2)/sqrt(a))` form. The strict sign read False.
  - **Arms and walls.** All arms and rc100 timeout.

  — follows from: the NEGQ fix (P0's and Rubi's route); the cost is in verification — [fixed-defect: none]
- class 1 g209 (1 entry, deterministic, final timeout top=1_1_3_1_r11): 1.1.3.2 e1337 `1/(a+bx^6)^2`. **The IGT fix
  changed the route.**
  - **p5.** 1_1_3_1_r4. Its `is(1/n+p+1 < 0)` accepted -5/6 (p5 g48 [defect: IGtQ]).
  - **Fixed core.** Rubi's r11 (`%mr_iGtQ(n,0)`, `is(p < -1)`) is top at 30 s → 1_1_3_1_r21 (`%mr_iGtQ((n-2)/4,0)`=1;
    `%mr_posQ(a/b)` True, as in Rubi). Its Module sub-integrals fire 1_1_3_7_r45 first, then 1_2_1_1_r12,
    1_2_1_2_r3/r9, 1_1_2_1_r10.
  - **Arms and walls.** VERIFY-TIMEOUT; rc100 timeout. r4 unverified 3.0 s; r2/r3 timeout. P0: 1_4_1_r23 (0.7 s).

  — follows from: the IGT fix (Rubi's RT-SUM route); the cost is in verification — [fixed-defect: none]
- class 1 g210 (1 entry, deterministic, final timeout top=1_1_3_1_r13): 1.1.3.2 e1274 `1/(a+bx^5)`. **The NEGQ fix
  changed the route.**
  - **p5.** 1_1_3_1_r14 (p5 g8): the strict sign read PosQ[a/b] False, so NegQ True.
  - **Fixed core.** r13 (`%mr_posQ(a/b)` True, as Rubi) is top at 30 s. Sub-integrals: 1_1_2_1_r11, 1_2_1_1_r12,
    1_2_1_2_r3/r9, 1_1_1_1_r3.
  - **Arms and walls.** VERIFY-TIMEOUT; all arms and rc100 timeout. P0: 1_4_1_r23 (0.7 s).

  — follows from: the NEGQ fix (Rubi's route) — [fixed-defect: none]
- class 1 g211 (1 entry, deterministic, final timeout top=1_1_3_1_r14): 1.1.3.2 e1445 `1/(a-bx^7)`. The top is r14 on
  both trees: `%mr_negQ` of `a/(-b)` reads -a/b, a product with leading -1, which is True in Rubi and in the port.
  The sub-integrals now take 1_1_2_1_r11 where p5 took r13. VERIFY-TIMEOUT; all arms and rc100 timeout. P0:
  1_4_1_r23 (0.6 s). — follows from: faithful binding (p5 g8's VERIFY-TIMEOUT shape) — [fixed-defect: none]
- class 1 g212 (1 entry, deterministic, final timeout top=1_1_3_1_r21): 1.1.3.2 e1324 `1/(a+bx^6)`. **The IGT and
  NEGQ fixes changed the route.**
  - **p5.** r14, through `is((n-3)/2 > 0)` on 3/2 and the strict NegQ (p5 g8).
  - **Fixed core.** Rubi's r21 is top at 30 s, with 1_1_3_7_r45, 1_2_1_1_r12, 1_2_1_2_r3/r9, 1_1_2_1_r10.
  - **Arms and walls.** VERIFY-TIMEOUT; all arms and rc100 timeout.

  — follows from: the IGT/NEGQ fixes (Rubi's route) — [fixed-defect: none]
- class 1 g213 (1 entry, deterministic, final timeout top=1_1_3_2_r112): 1.1.3.2 e2967 `x^2 sqrt(a+b(cx^3)^(3/2))`.
  **The IGT fix changed the route.**
  - **p5.** 1_1_3_2_r12 through `is(p > 0)` on p=1/2 (p5 g46).
  - **Fixed core.** r112 (fractional-power substitution) is top at 30 s → 1_1_3_2_r84, r17 (`notequal(gcd,1)`),
    r21 (`%mr_iGtQ(n,0)`, `is(p > 0)`) → 1_1_3_2_r45 / 1_1_3_7_r29 / 1_1_3_1_r30. Those three read `%mr_posQ(a)` on a
    symbol, True in both. This is the corpus's elliptic_f / (1±sqrt3) form.
  - **Arms and walls.** VERIFY-TIMEOUT; all arms and rc100 timeout. P0: 1_1_3_1_r67, 1_4_1_r23 (0.7 s).

  — follows from: the IGT fix (Rubi's route) — [fixed-defect: none]
- class 1 g214 (1 entry, deterministic, final timeout top=1_1_3_2_r30): **Fix-induced** (p5 verified 0.1 s).
  1.1.3.2 e1331 `x^6/(a+bx^6)^2`. Rubi's r30 (`%mr_iGtQ(n,0)`, `is(p < -1)`, `is(m+1 > n)`) is top at 30 s →
  1_1_3_1_r21 (`%mr_posQ(a/b)` True, as Rubi), with Module sub-integrals 1_1_3_7_r45, 1_2_1_1_r12, 1_2_1_2_r3/r9,
  1_1_2_1_r10. VERIFY-TIMEOUT; rc100 timeout. r4 unverified 2.8 s; r2/r3 timeout. P0: 1_3_4_r1 (1.2 s). The
  defective route is not traced. — follows from: Rubi's RT-SUM route; the cost is in verification — [fixed-defect:
  none]
- class 1 g215 (1 entry, deterministic, final timeout top=1_1_3_2_r37): **Fix-induced** (p5 verified 0.1 s).
  1.1.3.2 e1320 `x^4/(a+bx^6)`. Rubi's r37 (`%mr_iGtQ((n-2)/4,0)`, `%mr_iGtQ(m,0)`, `is(m < n-1)`,
  `%mr_posQ(a/b)`) is top at 30 s, with the g214 sub-integrals. VERIFY-TIMEOUT; rc100 timeout. r4 unverified
  10.6 s. P0: 1_3_4_r1 (1.2 s). — follows from: as g214 — [fixed-defect: none]
- class 1 g216 (1 entry, deterministic, final timeout top=1_1_3_2_r63): **Fix-induced** (p5 verified 0.1 s).
  1.1.3.2 e1318 `x^6/(a+bx^6)`. Rubi's r63 (`%mr_iGtQ(n,0)`, `is(m > n-1)`) is top at 30 s → 1_1_3_1_r21 and the
  g214 sub-integrals. VERIFY-TIMEOUT; rc100 timeout. r4 unverified 3.1 s. P0: 1_3_4_r1 (1.0 s). — follows from:
  as g214 — [fixed-defect: none]
- class 1 g217 (1 entry, deterministic, final timeout top=1_1_4_3_r1): 1.1.4.3 e147 `x^5(A+Bx^2)/(bx^2+cx^4)^(3/2)`.
  Same route as p5 (p5 g221). The top 1_1_4_3_r1 (x^2 substitution) fired at 30 s. Nested: 1_2_1_3_r31
  (`%mr_iGtQ` on integers m, n), 1_1_4_2_r21, 1_2_1_2_r15, 1_2_1_1_r14, 1_1_2_1_r13. VERIFY-TIMEOUT; rc100 timeout.
  r3 verified 0.5 s. — follows from: condition retry — [fixed-defect: none]
- class 1 g218 (1 entry, deterministic, final timeout top=1_2_1_1_r18): 1.2.1.2 e2492 `1/(a+bx+cx^2)^(7/3)`. **The
  NE fix changed the route.**
  - **p5.** 1_1_3_2_r17, 1_1_3_2_r13, 1_2_1_1_r17: unverified 0.6 s (p5 g265). r17's defective `(k!) = 1` read
    gcd=1 as True.
  - **Fixed core.** `notequal(gcd(m+1,n), 1)` is False, as Rubi's `!=` is. The fires are 1_1_3_2_r67
    (`is(m < -1)`) and 1_1_3_2_r45 / 1_1_3_7_r29 / 1_1_3_1_r30. The last three read `%mr_posQ(b^2-4ac)` True; the
    corpus's `(b^2-4ac)^(1/3)(1+sqrt3)` form is that branch.
  - **Top.** The hypergeometric 1_2_1_1_r18 answers at top.
  - **1_2_1_1_r17 is not logged.** It is Rubi's `3 <= Denominator[p] <= 4` substitution, and its repl dispatches
    exactly that `x^k/sqrt(b^2-4ac+4cx^3)` chain.
  - **Arms and walls.** VERIFY-TIMEOUT; rc100 timeout. r4 unverified 2.2 s; r2/r3 timeout. P0: 1_3_4_r1,
    1_2_1_1_r17 (2.0 s).

  — follows from: the NE fix (Rubi's reading). Why 1_2_1_1_r17 does not complete is not determined; the sites on
  its sub-chain read as Rubi's — [fixed-defect: none]
- class 1 g219 (1 entry, deterministic, final timeout top=1_2_1_2_r111): 1.2.1.2 e2479 `(d+ex)^(1/2)/(a+bx+cx^2)^(5/2)`.
  **The IGT fix changed the route.**
  - **p5.** Nested 1_2_1_9b_r5, through `is(p > -2)` on p=-3/2 (p5 g150 [defect: IGtQ]).
  - **Fixed core.** r5 declines, as in Rubi; 1_1_2_3_r42 and 9_1_r8 appear in its place. The top r111 (`is(p < -1)`,
    `is(m > 0)`, `is(m < 1)` on numbers) fired at 30 s, with 1_2_1_3_r55, 1_2_1_9b_r32, 1_2_1_2_r93.
  - **Arms and walls.** VERIFY-TIMEOUT; all arms and rc100 timeout. P0: 1_2_1_9b_r5, r111 (3.0 s).

  — follows from: the IGT fix (Rubi's route) — [fixed-defect: none]
- class 1 g220 (1 entry, deterministic, final timeout top=1_2_1_2_r13): 1.2.1.2 e2491 `(d+ex)/(a+bx+cx^2)^(7/3)`. The
  g218 change. p5: 1_1_3_2_r17, 1_2_1_1_r17, 1_2_1_2_r13, unverified 0.4 s (p5 g267). Fixed: the g218 chain ending
  in 1_2_1_1_r18, under the top r13 (`is(p < -1)`) at 30 s. VERIFY-TIMEOUT; all arms and rc100 timeout. P0:
  1_3_4_r1, 1_2_1_1_r17, r13 (2.2 s). — follows from: as g218 — [fixed-defect: none]
- class 1 g221 (1 entry, deterministic, final timeout top=1_2_1_2_r133): 1.2.1.2 e2496. Same route as p5 (p5 g222):
  1_1_1_4_r47, then r133 (`%mr_iLtQ(m,0)`, m=-1) at 30 s. rc100 timeout. r4 verified 23.0 s. P0 16.1 s. — follows
  from: model flags — [fixed-defect: none]
- class 1 g222 (1 entry, deterministic, final timeout top=1_2_1_2_r99): 1.2.2.8 e3 `1/((d+ex)sqrt(a+bx^2+cx^4))`. **The
  NEGQ fix changed the route.**
  - **p5.** 1_2_2_3_r78, through `%mr_negQ(c/a)`, which the strict sign read True (p5 g223 [defect: negQ]).
  - **Fixed core.** 1_2_2_3_r74, 1_2_2_7_r26 and 1_2_2_1_r16 fire. All read `%mr_posQ(c/a)` True, as Rubi; the
    corpus's `elliptic_f(2atan(c^(1/4)x/a^(1/4)),…)` is that branch.
  - **Top.** The top-level 1_2_2_8_r1 is absent at 30 s and 120 s (MID-CHAIN).
  - **Arms and walls.** All arms and rc100 timeout. P0 1.6 s.

  — follows from: the NEGQ fix (Rubi's branch) — [fixed-defect: none]
- class 1 g223 (1 entry, deterministic, final timeout top=1_2_1_3_r102): **Fix-induced** (p5 verified 8.0 s).
  1.2.1.4 e914 `1/((d+ex)^2 sqrt(f+gx) sqrt(a+bx+cx^2))`.
  - **Route.** Rubi's r102 (`integerp(2m)`, `is(m <= -2)`) is top at 30 s. Nested: 1_2_1_8_r3, 1_2_1_3_r99,
    1_1_1_4_r29, 1_4_2_r9, 1_2_1_3_r89 (`not(%mr_iGtQ(m,0))`), 1_1_2_3_r48/r42, 1_2_1_2_r93, giving the corpus's
    elliptic_e/elliptic_f forms.
  - **Sign branch.** 1_1_2_3_r48/r42 read `%mr_posQ(d/c)` and `%mr_posQ(b/a)` True, as in Rubi; the strict sign
    read False.
  - **Arms and walls.** VERIFY-TIMEOUT; rc100 timeout. r3 verified 1.1 s. P0: 1_2_1_8_r2, r102 (3.4 s).

  — follows from: the NEGQ fix (Rubi's elliptic route); condition retry (r3) — [fixed-defect: none]
- class 1 g224 (1 entry, deterministic, final timeout top=1_2_1_3_r104): 1.2.1.4 e904. Same route as p5 (p5 g224),
  the elliptic prefix of g223. VERIFY-TIMEOUT; all arms and rc100 timeout. — follows from: not determined which change
  moves the nested chain — [fixed-defect: none]
- class 1 g225 (1 entry, deterministic, final timeout top=1_2_1_3_r105): **Fix-induced** (p5 verified 7.1 s).
  1.2.1.4 e905. The g223 route under r105 (`integerp(2m)`, `is(m <= -2)`). VERIFY-TIMEOUT; rc100 timeout. r3
  verified 1.0 s. P0: 1_2_1_8_r2, r105 (2.6 s). — follows from: as g223 — [fixed-defect: none]
- class 1 g226 (1 entry, deterministic, final timeout top=1_2_1_3_r31): 1.2.1.3 e122 `x^2(A+Bx)/(bx+cx^2)^(3/2)`. Same
  route as p5 (p5 g225). Top r31 (`%mr_iGtQ` on integers) at 30 s. VERIFY-TIMEOUT; rc100 timeout. r3 verified
  0.5 s. — follows from: condition retry — [fixed-defect: none]
- class 1 g227 (1 entry, deterministic, final timeout top=1_2_1_3_r45): 1.2.2.4 e170 `x^3(A+Bx^2)/sqrt(a+bx^2+cx^4)`.
  Same route as p5 (p5 g227). At 120 s the top-level 1_2_2_4_r9 has fired: VERIFY-TIMEOUT. r45's
  `not(is(p <= -1))` reads a number. All arms and rc100 timeout. — follows from: faithful Optional binding —
  [fixed-defect: none]
- class 1 g228 (1 entry, deterministic, final timeout top=1_2_1_3_r48): 1.2.2.4 e173 `(A+Bx^2)/(x^3 sqrt(…))`. Same
  route as p5 (p5 g228). At 120 s 1_2_2_4_r9 has fired: VERIFY-TIMEOUT. All arms and rc100 timeout. — follows from:
  faithful Optional binding — [fixed-defect: none]
- class 1 g229 (1 entry, deterministic, final timeout top=1_2_1_3_r94): **Fix-induced** (p5 verified 1.5 s).
  1.2.1.4 e897 `sqrt(a+bx+cx^2)/((d+ex)sqrt(f+gx))`. The g223 route under r94. VERIFY-TIMEOUT; all arms and rc100
  timeout. P0: 1_2_1_3_r94 (1.9 s). — follows from: as g223 — [fixed-defect: none]
- class 1 g230 (1 entry, deterministic, final timeout top=1_2_1_4_r30): 1.2.1.5 e123
  `1/(sqrt(2+3x+5x^2)sqrt(3-x+2x^2))`. **The NEGQ fix changed the nested branch.**
  - **p5.** 1_1_2_3_r54, 1_2_2_1_r18.
  - **Fixed core.** 1_2_2_1_r16, whose `%mr_posQ(c/a)` reads a complex constant: constant branch,
    `float(rectform)`, as Rubi's NumericQ branch. The corpus's `elliptic_f(2atan(…))` is r16's form. The top r30
    (P0's top) fired at 30 s.
  - **Arms and walls.** VERIFY-TIMEOUT; all arms and rc100 timeout.

  — follows from: the NEGQ fix (Rubi's branch) — [fixed-defect: none]
- class 1 g231 (1 entry, deterministic, final timeout top=1_2_1_9_r12): 1.2.1.6 e104. Same route as p5 (p5 g230).
  1_4_1_r18, then the top r12 (`%mr_iLtQ(q,-1)`, `%mr_iGtQ(q,0)` on q=-1) at 30 s: VERIFY-TIMEOUT. All arms and rc100
  timeout. P0: 1_4_2_r17 (0.8 s). — follows from: faithful binding — [fixed-defect: none]
- class 1 g232 (1 entry, deterministic, final timeout top=1_2_1_9_r19): 1.2.1.6 e96. Same route as p5 (p5 g231): the
  top r19 at 30 s after 1_1_2_1_r13, 1_2_1_1_r15, 1_4_1_r18. VERIFY-TIMEOUT; all arms and rc100 timeout. — follows
  from: faithful binding — [fixed-defect: none]
- class 1 g233 (1 entry, deterministic, final timeout top=1_2_2_1_r5): 1.2.3.2 e634 `1/(a+b(d+ex)^2+c(d+ex)^4)^3`.
  **The NEGQ fix changed the nested branch.**
  - **p5.** 1_2_2_3_r27, through `%mr_negQ(b^2-4ac)`, which the strict sign read True (p5 g155 [defect: negQ]).
  - **Fixed core.** 1_2_2_3_r24 fires (`%mr_posQ(b^2-4ac)`), so PosAux read the sum True. Rubi took the same
    branch: the corpus's `atan(…/sqrt(b-sqrt(b^2-4ac)))` form. Then 1_1_2_1_r12, 1_2_2_3_r36, 1_2_2_1_r5.
  - **Top.** P0's top-level 1_4_2_r18 is absent at 30 s and 120 s (MID-CHAIN).
  - **Arms and walls.** All arms and rc100 timeout.

  — follows from: the NEGQ fix (Rubi's branch) — [fixed-defect: none]
- class 1 g234 (1 entry, deterministic, final timeout top=1_2_2_2_r1; record error 8.8 s): 1.2.3.2 e649
  `(df+efx)/(a+b(d+ex)^2+c(d+ex)^4)^2`. Same route as p5 (p5 g78).
  - **Fires.** Nested only: 1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_1_r8, 1_2_2_2_r1. No top-level fire.
  - **Error.** The newerror leg dies at 29.2 s with heap exhausted (see NEW ERRORS). Error in all arms and on p5
    (12.9 s).
  - **P0.** 1_3_3_r4 (1.1 s).
  - **Sites.** 1_1_2_1_r13's `%mr_negQ(a/b)` reads the atanh branch the corpus answer shows.

  — follows from: not determined from the traces — [fixed-defect: none]
- class 1 g235 (1 entry, deterministic, final timeout top=1_2_2_4_r5): 1.2.2.4 e299. Same route as p5 (p5 g234). The
  top r5 fired at 30 s: VERIFY-TIMEOUT. All arms and rc100 timeout. — follows from: not determined which change moves
  the nested chain — [fixed-defect: none]
- class 1 g236 (1 entry, deterministic, final timeout top=1_2_2_6_r2): 1.2.2.6 e51. Same route as p5 (p5 g235). The top
  r2 fired at 30 s; rc100 timeout. r3 verified 1.9 s. — follows from: condition retry — [fixed-defect: none]
- class 1 g237 (1 entry, deterministic, final timeout top=1_2_3_2_r1): 1.2.3.2 e552 `x^(n-1)/(a+bx^n+cx^2n)`. Same route
  as p5 (p5 g237). Rubi's 3-step atanh route: r1 → 1_2_1_1_r12 → 1_1_2_1_r13. VERIFY-TIMEOUT; all arms and rc100
  timeout. P0: the manual 9.1 r16. — follows from: 9.1 regeneration; the cost is in verification — [fixed-defect:
  none]
- class 1 g238 (1 entry, deterministic, final timeout top=1_4_1_r7): **Fix-induced** (p5 verified 0.7 s). 1.3.2 e624
  `(a+8x-8x^2+4x^3-x^4)^(3/2)`.
  - **Fires.** The last fire at 30 s and 120 s is 1_4_1_r7, with no top-level normalizer (MID-CHAIN). Nested:
    1_2_2_1_r4, 1_2_2_2_r10, 1_2_2_4_r37, 1_2_2_3_r60, 1_1_2_5_r11, 1_1_2_4_r54, 1_1_2_3_r34/r41.
  - **Sign sites.** They read sums whose first term is a constant (`1±sqrt(4+a)` shapes), the term Rubi's
    `First` also reads. The corpus's `1-sqrt(4+a)` and `elliptic_f(atan((x-1)/sqrt(1+sqrt(4+a))),…)` shapes match.
  - **P0.** 1_4_2_r19, 1_2_2_1_r3, 1_4_1_r7, 1_2_2_1_r19 (2.2 s).
  - **Arms and walls.** All arms and rc100 timeout.

  — follows from: the NEGQ fix (Rubi's readings); the cost is in integration — [fixed-defect: none]
- class 1 g239 (1 entry, deterministic, final timeout top=1_4_3_r19): 1.3.2 e348. Same route as p5 (p5 g244):
  1_1_2_2_r39, then r19 (`is(i/c > 0)` inside `integerp(m) or …`). VERIFY-TIMEOUT; all arms and rc100 timeout. —
  follows from: not determined from the traces — [fixed-defect: none]
- class 1 g240 (1 entry, deterministic, final unverified top=1_1_1_2_r14): 1.1.1.2 e1884
  `(a+bx)^((ad-2bc)/(bc-ad))(c+dx)^((bc-2ad)/(ad-bc))`.
  - **Route.** Same as p5 (p5 g247) and the same fire list as P0 (P0 verified 0.2 s): 1_1_1_4_r46 → 1_1_1_2_r39 →
    top r14.
  - **Sites on the route.**
    - r14's `%mr_iLtQ(%mr_simp(m+n+2),0)` reads -1.
    - Its `not(is(m < -1) and … and integerp(n))` is decided False by `integerp(n)`.
    - r39's `%mr_intPart(n)` / `%mr_fracPart(n)` on the symbolic quotient give 0 / n, as Rubi's IntPart/FracPart
      do.
  - **Answer.** r14's closed-form term plus a `%e^(…log…)` exp-log product. That product is a Maxima `integrate`
    result for the reduced `(a+bx)^(m+1)(c+dx)^n`, where (m+1)+n+2=0 and Rubi's 2-step route closes it by rule.
    Unverifiable, not shown wrong.
  - **Arms.** All unverified.

  — follows from: not determined from the traces (P0 verified the same fire list) — [fixed-defect: none]
- class 1 g241 (1 entry, deterministic, final unverified top=1_1_1_3_r10): **Fix-induced** (p5 verified 0.5 s).
  1.1.1.3 e985 `(1-x)^(p-1/2)(1+x)^(p+1/2)/(cx)^(2(1+p))` (Rubi 1 step).
  - **Why r10 answers now.** `not(%mr_iGtQ(m,0))` with m=p+1/2 is now True, Rubi's reading; the defective
    `not(is(m > 0))` did not accept, as in g190.
  - **Why Rubi would not use r10.** Rubi's r10 also needs `NeQ[m+n+p+2,0]`, but here
    m+n+p+2 = (p+1/2)+(p-1/2)-2(1+p)+2 = 0. The port's syntactic `%mr_neQ` reads the unexpanded zero as nonzero
    (inferred).
  - **Nested.** 1_1_1_3_r53, 1_1_2_2_r39, 1_1_1_3_r24.
  - **Answer.** A two-term hypergeometric form instead of the corpus's one-term 2F1 in (1-x)/(1+x): unverifiable
    (the zero chain does not close 2F1 identities), not shown wrong.
  - **Arms and P0.** All arms unverified. P0: 1_1_1_6_r7 (2.9 s).

  — follows from: the IGT fix exposing the syntactic NeQ reading of a zero exponent sum (inferred) — [fixed-defect:
  none]
- class 1 g242 (1 entry, deterministic, final unverified top=1_1_1_3_r25): 1.1.1.3 e972 `(1-x)^n/(x^3(1+x)^n)`.
  **The IGT fix changed the nested rule.**
  - **p5.** Nested 1_1_1_3_r61.
  - **Fixed core.** Nested r60, because `not(%mr_iLtQ(m,0))` on symbolic m is now True; the defective
    `not(is(m < 0))` did not accept. The top r25 binds x^-3 as `(0+x)^-3` (`is(m < -1)`, m=-3). r60 is Rubi's
    rule, with `%mr_iLtQ(n,0)` reading the x^-2 factor's n=-2.
  - **Answer.** It matches the corpus hypergeometric with (1-x)^n and (1+x)^-n exchanged. r60's `%mr_sumSimplerQ`
    tie admits both orders. Unverifiable.
  - **Arms and P0.** All arms unverified. P0: 1_1_1_6_r7 (2.9 s).

  — follows from: the IGT fix (Rubi's rule); binding order — [fixed-defect: none]
- class 1 g243 (1 entry, deterministic, final unverified top=1_1_1_3_r29): 1.1.1.3 e966 `(1-x)^n x^3/(1+x)^n`. Same route
  as p5 (p5 g113): r29 (`is(m > 1)`, m=3), 1_1_1_4_r6, 1_1_1_2_r38 (numeric `not(is(…))`). The hypergeometric answer
  has the factors exchanged against the corpus answer: unverifiable. All arms unverified. — follows from: not
  determined from the traces — [fixed-defect: none]
- class 1 g244 (1 entry, deterministic, final unverified top=1_1_1_3_r60): 1.1.1.3 e971 `(1-x)^n/(x^2(1+x)^n)`. The g242
  change (p5 1_1_1_3_r61 → r60). r60 alone, Rubi's 1-step rule. The answer is
  `2·hypergeometric([2,1-n],[2-n],(-x-1)/(x-1))(1-x)^(n-1)(x+1)^(1-n)/(1-n)`: the corpus's formula with the linear
  factors exchanged. Unverifiable. All arms unverified. — follows from: as g242 — [fixed-defect: none]
- class 1 g245 (1 entry, deterministic, final unverified top=1_1_1_3_r70): 1.1.1.3 e3156 `(4x-3)^n/(sqrt(1-x)sqrt(1+x))`.
  **The IGT fix changed the route.**
  - **p5.** 1_1_1_3_r55 alone (deferred; p5 g21 [defect: IGtQ]).
  - **Fixed core.** Rubi's 1-step AppellF1 rule r70 answers. Its `is(…)` / `not(is(…))` sites read numeric
    bindings.
  - **Answer.** `-(sqrt(2)AppellF1(1/2,-n,1/2,3/2,4(1-x),-(x-1)/2)sqrt(1-x))`: the corpus's AppellF1 with the two
    parameter/argument pairs exchanged, under which AppellF1 is symmetric. Unverifiable.
  - **Arms.** All unverified.

  — follows from: the IGT fix (Rubi's rule) — [fixed-defect: none]
- class 1 g246 (1 entry, deterministic, final unverified top=1_1_1_4_r15): 1.1.1.4 e137 `(a+bx)^m(A+Bx)/((c+dx)^m(e+fx))`.
  The g242 change in the nested rule (p5 1_1_1_3_r61 → r60; p5 timeout 30.0 s, p5 g205).
  - **Route.** Top r15 (`%mr_iGtQ(m+n+1,0)`=1) → 1_1_1_4_r47, 1_1_1_3_r60.
  - **Answer.** It holds `'integrate((b*x+a)^m*(d*x+c)^(-m-1)*((B*d*f^2*x^2)/(f*x+e)+…),x)`. r15's
    `%mr_expandToSum` of a quotient returned the expanded but undivided rational form (`%mr_expandToSum2`'s final
    `expand(u)`), and no rule takes it. Unverifiable.
  - **Arms and P0.** r3 timeout; r2/r4 unverified. P0: 1_1_1_6_r7, r15 (6.4 s).

  — follows from: the IGT fix (Rubi's rule) plus the ExpandToSum no-division form — [fixed-defect: none]
- class 1 g247 (1 entry, deterministic, final unverified top=1_1_2_10_r6): **Fix-induced** (p5 verified 1.1 s). 1.3.2
  e215 `sqrt(ax^4)/sqrt(1+x^2)`.
  - **Answer: wrong.** `(sqrt(a)*x*sqrt(x^2+1))/2`. It is the corpus's second term only; the
    `-sqrt(a)/2·asinh(x)` term is missing.
  - **Route.** The top 1_1_2_10_r6 (`not(is(p <= -1))` on p=-1/2) builds its closed-form term. Its reduced
    `Int[(1+x^2)^(-1/2)·ExpandToSum(…)]` goes through 1_1_2_10_r2 (`%mr_eqQ(%mr_coeff(Pq,x,0),0)`) and ends in
    9_1_r8 (`Int[a] = a·x`), contributing nothing.
  - **Sites.** The route's conds hold no fixed-defect site. `%mr_coeff3` reaches no changed port;
    `%mr_expandToSum2` reaches `%mr_posQ` (static call graph).
  - **Arms and P0.** All arms unverified. P0: 1_2_1_6_r1 (1.0 s).

  — follows from: not determined from the traces — [fixed-defect: undetermined — which sub-integral reads as zero
  before 9_1_r8 (a repl trace of r6's ExpandToSum and r2's PolyQuotient), and the defective tree's route; the same
  lost-term signature as g249/g250]
- class 1 g248 (1 entry, deterministic, final unverified top=1_1_2_1_r26): 1.1.2.2 e915 `1/(-2-3x^2)^(3/4)`. Same route as
  p5 (p5 g249), and the fire list equals P0's (0.2 s): 1_1_3_1_r32, r26 (`%mr_negQ(a)` on a=-2). The answer is an
  elliptic_f form. r4 verified 0.1 s; r2/r3 unverified. — follows from: model flags — [fixed-defect: none]
- class 1 g249 (1 entry, deterministic, final unverified top=1_1_2_8_r14): **Fix-induced** (p5 verified 4.1 s). 1.2.1.4
  e85 `x^3(d+ex)^3/(d^2-e^2x^2)^(7/2)`.
  - **Answer: wrong.** It reproduces the corpus's three algebraic terms but lacks `-atan(ex/sqrt(d^2-e^2x^2))/e^4`.
  - **Route.** The top 1_1_2_8_r14 (`%mr_iGtQ(n,0)`, `%mr_iGtQ(m,1)` on integers) → 1_2_1_9b_r12
    (`%mr_iLtQ(p+1/2,0)`) → 1_1_2_9_r27 (ExpandToSum of a quotient by (d-ex)) → 1_1_3_7_r37 (`mr_sum`/`%mr_coeff`
    split) → 9_1_r8.
  - **Arms and P0.** r3 verified 1.2 s; r2/r4 unverified. P0: 1_4_2_r23 (0.7 s).

  — follows from: condition retry (r3); the defective route is not traced — [fixed-defect: undetermined — as g247:
  which split term reads as zero before 9_1_r8 (a repl trace), and why the defective tree verified]
- class 1 g250 (1 entry, deterministic, final unverified top=1_1_2_8_r55): **Fix-induced** (p5 verified 4.8 s). 1.2.1.4
  e181 `x^3/((d+ex)^3 sqrt(d^2-e^2x^2))`. The top r55 (`%mr_iLtQ(n,-1)`; `not(is(p > 1))` on a number) rewrites to
  the g249 chain (r14 → 1_2_1_9b_r12 → 1_1_2_9_r27 → 1_1_3_7_r37 → 9_1_r8). The answer lacks
  `+atan(ex/sqrt(d^2-e^2x^2))/e^4`: wrong. r3 verified 0.2 s; r2/r4 unverified. P0: 1_4_2_r23 (0.7 s). — follows
  from: as g249 — [fixed-defect: undetermined — as g249]
- class 1 g251 (1 entry, deterministic, final unverified top=1_1_3_1_r36): **Fix-induced** (p5 verified 0.3 s). 1.2.2.2
  e1025 `1/sqrt(2+2a-2(1+a)+cx^4)` (ZERO; Rubi 1 step `-x/sqrt(cx^4)`).
  - **Route.** The top r36 (`not(is(a > 0))` on the ZERO coefficient) → 1_1_3_1_r57 (hypergeometric).
  - **Why r57 accepts now.** `not(%mr_iLtQ(1/n+p,0))` on -1/4 is True, as Rubi reads it; the defective
    `not(is(-1/4 < 0))` was False.
  - **Answer: wrong.** It divides by the ZERO coefficient: `…sqrt((cx^4)/(-(2(a+1))+2a+2)+1)/sqrt(…)`.
  - **Arms.** All unverified.

  — follows from: ZERO corpus form, with the IGT fix letting r57 accept (Rubi's reading) — [fixed-defect: none]
- class 1 g252 (1 entry, deterministic, final unverified top=1_1_3_2_r112): 1.1.3.2 e2989 `(dx)^m sqrt(a+b(c/x)^(1/2))`.
  **The IGT fix changed the route.**
  - **p5.** 1_1_3_2_r12 through `is(p > 0)` on p=1/2 (p5 g46).
  - **Fixed core.** r112 → 1_1_3_2_r86 (IntPart/FracPart of symbolic m: 0 and m, as Rubi) → r84 → r82
    (`%mr_iLtQ(n,0)`) → 1_3_4_r1 → 1_1_3_7_r46.
  - **Answer.** It holds `'integrate(x^(3/2)·sqrt(…)/…, (a·sqrt(c/x)·x+b·c)/(sqrt(c/x)·x))`: a fall-through carried
    by `%mr_subst`, not an equal-form rewrite. Unverifiable.
  - **Arms and P0.** All arms unverified. P0: 1_1_3_2_r110, r112 (0.5 s).

  — follows from: the IGT fix (Rubi's route); why the substituted integrand finds no rule is not determined —
  [fixed-defect: none]
- class 1 g253 (1 entry, deterministic, final unverified top=1_1_3_2_r6): 1.2.2.2 e1028 `1/(x^3 sqrt(2+2a-2(1+a)+cx^4))`
  (ZERO; Rubi 1 step). Same route as p5 (p5 g258). r6 (`%mr_eqQ((m+1)/n+p+1,0)` on numbers) returns
  `-(sqrt(cx^4-2(a+1)+2a+2)/(2(-(2(a+1))+2a+2)x^2))`, which divides by the ZERO coefficient: wrong. All arms
  unverified. — follows from: ZERO corpus form — [fixed-defect: none]
- class 1 g254 (1 entry, deterministic, final unverified top=1_1_3_8_r17): 1.3.2 e148 `(e+fx)/(x sqrt(-1-x^3))`. Same route
  as p5 (p5 g264). The answer is a long elliptic form. r4 verified 1.4 s; r3 timeout; r2 unverified. — follows from:
  model flags — [fixed-defect: none]
- class 1 g255 (1 entry, deterministic, final unverified top=1_2_1_3_r55): 1.2.1.4 e481
  `x/((d+ex)(ade+(cd^2+ae^2)x+cdex^2)^(3/2))`. Same route as p5 (p5 g270): 1_4_1_r18, then r55 (`is(p < -1)`) with
  x as f+gx, f=0.
  - **Answer: wrong.** Its denominator factor `(ade^3-de(ae^2+cd^2)+cd^3e)` is an unexpanded zero, namely r55's
    c·d^2-b·d·e+a·e^2 for this quadratic.
  - **Why r55 answers.** The degenerate-case rules that would catch c·d^2-b·d·e+a·e^2=0 test it with strict
    `%mr_eqQ` (inferred).
  - **Arms and P0.** All arms unverified. P0: 1_2_1_9b_r5 (3.4 s).

  — follows from: the strict EqQ reading (inferred) — [fixed-defect: none]
- class 1 g256 (1 entry, deterministic, final unverified top=1_2_2_2_r16): 1.2.2.2 e1012 `x^4/sqrt(a+bx^2+(2+2c-2(1+c))x^4)`
  (ZERO). Same route as p5 (p5 g273). The elliptic answer divides by `(-(2(c+1))+2c+2)`: wrong. All arms
  unverified. — follows from: ZERO corpus form — [fixed-defect: none]
- class 1 g257 (1 entry, deterministic, final unverified top=1_2_2_2_r34): 1.2.2.2 e1014 `x^2/sqrt(a+bx^2+(2+2c-2(1+c))x^4)`
  (ZERO). Same route as p5 (p5 g274). r34's `%mr_negQ(c/a)` on the ZERO c reads True on both trees; its NeQ part is
  syntactic. The answer divides by the ZERO coefficient: wrong. All arms unverified. — follows from: ZERO corpus form
  — [fixed-defect: none]
- class 1 g258 (1 entry, deterministic, final unverified top=1_2_2_7_r7): 1.2.2.7 e30
  `(sqrt(a)+x^2 sqrt(c))/((d+ex^2)sqrt(a+bx^2+cx^4))` (Rubi 1 step, 1.2.2.7 r26 with `EqQ[cA^2-aB^2,0]`). Same route
  as p5 (p5 g276).
  - **Why r7 answers.** 1_2_2_7_r7 (the Pr split, `not(%mr_polyPowerQ(Pr,x,2))`) accepts even though Pr is a
    polynomial in x^2. r3 verified 0.3 s, so r7 accepts on a retried binding.
  - **Split.** Its odd part is 0 (9_1_r8). Its even part goes to 1_4_1_r18.
  - **Answer.** `('integrate(x^2/(((e*x^2)/c+d/c)*sqrt(…)),x))/sqrt(c)`: only the sqrt(c)x^2 term remains, and as an
    integrate noun. Wrong.
  - **Arms and P0.** r2/r4 unverified. P0: 1_2_2_7_r30 (2.4 s).
  - **Secondary.** 1_4_1_r18's no-fire nested call is an EQ-REWRITE candidate, but r3 shows the first-binding route
    verifies.

  — follows from: condition retry — [fixed-defect: none]
- class 1 g259 (111 entries, slow-correct; all 111 final120 verified). Sample: all 111 rows read (fire lists, tops,
  walls) and the arm records joined by script.
  - **Walls.** P0 core 1.1–26.4 s (median 3.2 s). Final: timeout at 30 s in all 111; 120 s verified 31.2–116.8 s
    (median 66.3 s). rc100 verified 106, timeout 5.
  - **Files.** 1.1.2.2 21, 1.2.1.3 17, 1.2.1.4 12, 1.2.1.9 8, 1.1.2.4 7, 1.2.1.2 7, and 4 or fewer in each of 15 more.
  - **33 entries with the 30 s list `1_1_3_1_r32, 1_2_2_3_r54, 1_1_3_2_r47`** (1.1.2.2 e590–e636, 1.1.2.4
    e786–e814, 1.2.1.3 e434–e451).
    - 120 s tops are Rubi's 1_1_2_2_r8/r9/r13/r14/r23/r25/r27, 1_1_2_4_r25/r29 and 1_1_2_8_r37.
    - r4 verified all 33; r2/r3 timeout.
    - p5: deferred 20, verified 13.
    - The prefix is the `%mr_posQ(b/a)` branch, which verifies at 120 s.
  - **63 entries with no fire flushed at 30 s.** r3 verified 57 (deferred 5, timeout 1); r4 verified 7; r2 verified
    9. p5: timeout 41, verified 15, deferred 7.
  - **15 others** (1.2.1.2 e392/e399, 1.2.1.5 e3/e62/e83, 1.2.1.9 e207/e237, 1.2.2.2 e849–e892, 1.2.2.6 e26,
    1.2.3.4 e11/e44/e92). r3 verified 6; r4 verified 3. p5: timeout 8, verified 5, deferred 2.
  - **What the arms and p5 show.** The cost is condition retry (r3 verifies 63) and the model flags (r4 verifies
    43). The fixed readings give verified answers in all 111. 29 entries that were deferred on the defective tree
    are now slow but correct. No sampled entry deviates.

  — follows from: condition retry and model flags (cost) — [fixed-defect: none]
- class 1 g260 (1 entry, near-cap): 1.1.1.7 e27 `(a+bx)(A+Cx^2)/(sqrt(c+dx)sqrt(e+fx)sqrt(g+hx))`. P0 record 12.5 s (core
  13.2 s). Final: 30 s timeout with no fire flushed; 120 s verified 29.9 s (top 1_1_1_7_r20); rc100 verified 28.6 s.
  r2 verified 29.7 s, r3 1.5 s, r4 27.1 s; p5 timeout 30.0 s. — follows from: condition retry (cost at the cap) —
  [fixed-defect: none]
- class 1 g261 (1 entry, noise): **Fix-induced** (p5 verified 16.3 s). 1.2.1.2 e414 `(d+ex)^(7/2)/(bx+cx^2)^(3/2)`.
  Record timeout 30.0 s. Final30 verified 28.3 s and final120 verified 29.4 s (top 1_2_1_2_r113); rc100 verified
  29.5 s. r2 verified 26.9 s, r3 1.6 s, r4 25.5 s. P0 3.6 s (core 4.4 s). — follows from: condition retry (cost at the
  cap) — [fixed-defect: none]
- class 1 g262 (1 entry, p0-noise): 1.2.1.5 e112. P0 record verified 29.6 s, at the cap; the P0 core times out at 30.0 s
  with no fire. Final 30 s and 120 s timeout, the only fire 1_1_2_1_r13 (p5: 9_1_r8 only). rc100 timeout 100.2 s; all
  arms timeout. — follows from: P0-side timing noise — [fixed-defect: none]

## Class 1 NEW ERRORS

35 entries, no P0 error. The recorded message comes from the newerror leg; 15 of the 35 reran as timeouts and have
no message. Kinds: heap exhausted 16, control stack exhausted 4, not recorded 15. 25 of the 35 already read error
on p5; the 10 that did not are 1.1.1.2 ×6, 1.1.3.2 e2960, 1.1.3.8 e190 and 1.2.1.2 e2487/e2488.

- class 1 new errors, 1.2.3.2 ×20 (e614, e616, e617, e619, e622, e624, e626, e631, e633, e635, e639, e641, e642,
  e644, e647, e649, e650, e655, e657, e658; shared cause):
  - **Integrands.** `(d+ex)^k/(a+b(d+ex)^2+c(d+ex)^4)^j`, or with `df+efx` in place of `(d+ex)`.
  - **Error.** `err=Heap exhausted during garbage collection: 0 bytes available, 16 requested. | fatal error
    encountered in SBCL … | Heap exhausted, game over.` 13 entries died at 12.6–29.2 s (e619, e622, e624, e626,
    e631, e633, e644, e647, e649, e650, e655, e657, e658). The other 7 timed out on the rerun at 30.3 s.
  - **Fires.** Nested only: 1_1_2_1_r13, 1_2_1_1_r12, then 1_2_1_1_r8 / 1_2_1_2_r3, r9, r13, r80, r84, r115 /
    1_2_1_3_r89, r55, then 1_2_2_2_r8 or r1. P0's top-level normalizer (1_3_3_r4 / 1_4_2_r24) is absent.
  - **Not fix-related.** Error in all arms and on p5 (7.6–18.3 s), with the same fire list as p5 (e649, g234).
    P0: verified 16, deferred 4.
  - **Fix site on the route.** 1_1_2_1_r13's `%mr_negQ(a/b)` reads the atanh branch the corpus answers show
    (e614, e619, e649: `atanh(…/sqrt(b^2-4ac))`). 1_2_1_3_r89's `%mr_iGtQ(m,0)` reads an integer m. Neither
    decides the death.
- class 1 new errors, 1.2.3.3 e46, e51, e73 (shared cause):
  - **Error.** `err=Control stack exhausted (no more space for function call frames).` at 7.3–8.5 s.
  - **Fires.** One completed fire each: 1_2_3_3_r35 / r47 / r34, all ExpandIntegrand rewrites (`integerp(q)`; r47
    `%mr_iGtQ` on integers). The recursion is not observed.
  - **Not fix-related.** Error in all arms and on p5 (4.7–5.0 s). P0 deferred 3.5–3.6 s, so none was a PASS.
- class 1 new errors, 1.3.1 e193, e194 (shared cause):
  - **Integrands.** `(b+2cx+3dx^2)(bx+cx^2+dx^3)^7` and `x^7(b+cx+dx^2)^7(b+2cx+3dx^2)` (Rubi 1 step).
  - **Error.** `err=Heap exhausted during garbage collection: 0 bytes available, 64 requested. | … | Heap exhausted,
    game over.` at 7.5–8.2 s, nfires=0.
  - **Arms and P0.** Error on p5 (9.1 / 9.7 s) and in r2/r4. r3 verified 0.4 / 1.5 s. P0 verified 0.5 / 0.9 s.
  - **Route.** Not observed; the death is on the condition-retry path.
- class 1 new error, 1.1.3.2 e2960 `x^3 sqrt(a+b sqrt(cx^3))`:
  - **Error.** `err=Heap exhausted during garbage collection: 16 bytes available, 32 requested. | … | Heap exhausted,
    game over.` at 5.9 s.
  - **Fires.** 1_1_3_1_r30, 1_1_3_7_r29, 1_1_3_2_r45, r63, r21, r84: the g213 route.
  - **Arms and history.** Error in all arms. p5 deferred 0.2 s, through the IGT-defective 1_1_3_2_r12 path as in
    g213/g252. P0 deferred 3.7 s.
  - **Fix sites on the route.** `%mr_posQ(a)` on a symbol (True in both) and `%mr_iGtQ(n,0)` on integers: Rubi's
    readings. The IGT fix moved it onto this route.
- class 1 new errors, 1.1.1.2 e1566, e1736, e1739, e1749, e1758, e1779:
  - **Integrands and record.** `(a+bx)^j(c+dx)^k` with j, k in halves and sixths. Record errors at 2.4–3.1 s (e1779
    28.9 s).
  - **Recorded message.** Only e1736's rerun errored: `err=fatal error encountered in SBCL …: | Control stack exhausted
    while pseudo-atomic, fault: …` at 2.5 s, nfires=0.
  - **The other five reran as timeouts** at 30.2–30.3 s, nfires=0. The exception is e1779, whose rerun fires
    1_1_3_7_r45, 1_2_1_1_r12, 1_2_1_2_r3/r9, 1_1_2_1_r13 and 1_1_3_2_r38.
  - **Arms and history.** r3 verified all six in 0.2 s. r2 error (e1736, e1779) or timeout; r4 timeout. p5 deferred
    0.1 s (e1758 verified 0.4 s). P0: e1758 verified; e1736/e1739/e1779 deferred; e1566/e1749 timeout.
  - **Route.** No rule completes before the fault, so no route is observed. The runaway is on the retry path; whether
    it passes a fixed-defect site is not determined. The same file's no-fire timeout group g1 is another reader's.
- class 1 new error, 1.1.3.8 e190 `(c+dx+…+ix^6)/(a+bx^4)`: record error 28.2 s; the rerun timed out at 30.3 s after
  one fire, 1_4_2_r20 (ExpandToSum normalizer, no fixed site in its cond). P0 and p5 timeout, so it was never a PASS.
  r2 error; r3/r4 timeout. Near the cap; the kind is not recorded.
- class 1 new errors, 1.2.1.2 e2487, e2488 `(a+bx+cx^2)^(4/3)/(d+ex)^2`, `…/(d+ex)^3`: record error 27.1 / 26.5 s; the
  rerun timed out with nfires=0. P0 and p5 timeout. r3 verified 23.3 / 24.0 s; r2/r4 timeout. Near the cap under
  condition retry; the kind is not recorded.

## Class 1 NEW TIMEOUTS

- class 1 NEW TIMEOUTS (1044; P0 verified 710, deferred 285, unverified 23, contains-noun 20, error 6):
  - **100 s re-check.** Timeout 825, verified 146, unverified 28, error 27, expected 11, contains-noun 7.
  - **Transitions.**

    | P0 → 100 s | count |
    |---|---|
    | verified → timeout | 567 |
    | deferred → timeout | 237 |
    | verified → verified | 108 |
    | deferred → verified | 24 |
    | verified → unverified | 17 |
    | verified → error | 16 |
    | contains-noun → timeout | 11 |
    | deferred → error | 10 |
    | unverified → verified | 9 |
    | deferred → expected | 9 |
    | unverified → unverified | 8 |
    | error → timeout, unverified → timeout | 5 each |
    | contains-noun → verified | 4 |
    | contains-noun → contains-noun, deferred → unverified | 3 each |
    | deferred → contains-noun, verified → contains-noun | 2 each |
    | unverified → expected, contains-noun → expected, error → verified, contains-noun → error | 1 each |

  - **By file family** (entries: 100 s classes).

    | file | entries | 100 s classes |
    |---|---|---|
    | 1.2.1.2 | 170 | timeout 162, verified 8 |
    | 1.2.1.3 | 132 | timeout 85, unverified 24, verified 23 |
    | 1.2.1.4 | 76 | timeout 58, verified 14, contains-noun 4 |
    | 1.1.2.2 | 72 | timeout 51, verified 21 |
    | 1.1.1.2 | 70 | timeout 53, error 17 |
    | 1.1.3.2 | 68 | timeout 66, verified 2 |
    | 1.2.3.2 | 61 | timeout 47, verified 7, error 6, unverified 1 |
    | 1.1.1.3 | 51 | timeout 48, verified 2, expected 1 |
    | 1.1.3.4 | 51 | timeout 41, expected 10 |
    | 1.2.2.2 | 43 | timeout 37, verified 4, error 2 |
    | 1.1.4.2 | 27 | timeout 24, verified 3 |
    | 1.2.1.6 | 26 | timeout 26 |
    | 1.2.2.4 | 26 | timeout 22, verified 4 |
    | 1.1.2.4 | 20 | timeout 9, verified 11 |
    | 1.3.2 | 16 | timeout 11, verified 4, error 1 |
    | 1.1.2.3 | 14 | timeout 14 |
    | 1.2.3.4 | 14 | timeout 8, verified 6 |
    | 1.2.4.2 | 13 | timeout 12, error 1 |
    | 1.2.3.3 | 12 | timeout 12 |
    | 1.1.1.7 | 11 | verified 7, contains-noun 3, timeout 1 |
    | 1.2.1.5 | 11 | timeout 9, verified 2 |
    | 1.2.1.9 | 11 | verified 8, timeout 3 |
    | 11 other files (1.1.3.3, 1.1.3.8, 1.3.1 9 each; 1.2.2.6 7; 1.1.1.4, 1.1.4.3, 1.2.2.5 3 each; 1.2.2.7, 1.2.2.8 2 each; 1.1.1.5, 1.1.2.8 1 each) | 49 in total | 1.1.3.8 verified 7, timeout 2; 1.1.3.3 timeout 7, unverified 1, verified 1; 1.3.1 timeout 6, unverified 2, verified 1; 1.2.2.6 timeout 5, verified 2; 1.2.2.5 verified 3; 1.1.1.4 and 1.1.4.3 verified 2, timeout 1 each; 1.2.2.7 and 1.2.2.8 timeout 2 each; 1.1.1.5 and 1.1.2.8 verified 1 each |

    The 146 verified at 100 s include g259's slow-correct entries.

## Clearance summary (g172–g262)

Counts are per group. There are 91 groups; g259 is the only multi-entry group.

**Class 1 g172–g262:** none 75, IGT 0, NEGQ 0, NE 0, MUL 0, collapse 0, sibling:<port> 0, undetermined 16. Of the
undetermined, 11 are EQ-REWRITE and 5 are other.

**Ticket-02 groups** (tagged none, `— follows from: GeQ/GtQ reading (ticket 02)`): 2.

- g185 — 1_1_1_4_r4's `not(is(n < -2))` on symbolic n=-3-m (inferred from the rule text).
- g199 — 1_1_3_1_r24's `not(is(a/b > 0))` on a symbolic a/b, exposed by the IGT fix letting 1_1_3_1_r57 accept.

**Groups whose tag is not `none`:**

- EQ-REWRITE (11), each `[fixed-defect: undetermined — EQ-REWRITE at <rule>, awaiting probe 16]`, with a
  `%mr_intSum` fault as the competing explanation:
  - g186 at 1_1_1_5_r5;
  - g187 at 1_1_2_11_r3;
  - g188 at 1_1_2_9_r23;
  - g189 at 1_1_3_8_r18;
  - g190 at 1_1_3_8_r29 (the IGT fix made r29 accept);
  - g191 at 1_2_1_3_r24;
  - g192 at 1_2_1_9b_r6;
  - g193 at 1_2_1_9b_r5;
  - g194 at 1_2_2_7_r12;
  - g195 at 1_2_2_7_r13;
  - g197 at 1_4_3_r56 (the IGT fix moved it off 1_3_3_r7).
- Other undetermined (5):
  - g196 — no route observed: which Rubi 1.2.3.4 rule answers e145 and why it declines. The `not(is(…))` sites of
    r45–r48 are ticket-02 candidates.
  - g207 — fix-induced VERIFY-TIMEOUT on P0's own route. The `%mr_rt(-a/c,2)` form r64 builds (it reaches the changed
    sign and sibling ports) against Rubi's `sqrt(-a)/sqrt(c)`. Candidate sibling:%mr_rt.
  - g247, g249, g250 — fix-induced wrong answers sharing one signature: a `const/sqrt(quadratic)` term (asinh/atan) is
    lost, and the route ends in 9_1_r8 after an ExpandToSum/`%mr_coeff` step. Deciders: a repl trace of that step,
    and the defective tree's route. `%mr_expandToSum2` reaches `%mr_posQ`; `%mr_coeff3` reaches no changed port.

**Readings the fixes moved onto Rubi's**, all tagged none after checking the sites:

- IGT — g177, g190, g197, g199 (r57), g200 (r5), g206, g209, g212, g213, g219, g241, g242, g244, g245, g246, g251, g252,
  and inferred 1.2.2.6 r3 for g172/g178/g183.
- NEGQ — g181, g205, g208, g210, g212, g222, g223/g225/g229, g230, g233, g238.
- NE — g218, g220.
- The 1.2.3.2 heap errors and e2960 in NEW ERRORS pass fixed sites that read as Rubi's.

**Other translation gaps met here** (not fixed defects, not ticketed in this plan):

- ZERO corpus coefficients — g172, g184, g251, g253, g256, g257.
- Strict EqQ/NeQ on unexpanded symbolic zeros — g200, g241, g255 (inferred).
- `%mr_expandToSum` leaving an undivided quotient — g246.

## Diagnostic 16 re-reading (class 1)

> Evidence: `probes/matcher/16-seen-guard-trace.class1.out` (2026-09-15 12:34 UTC, Maxima
> branch_5_50_base_84_g4204fb669, SBCL 2.6.7, git HEAD 560b4a5, fixed core `b98e4748…`, P0 core `5ef9b3bc…`;
> entry set `probes/matcher/16-seen-guard-trace.class1.tsv`, parts A+B+C, 186 entries;
> `Results: 179 passed, 7 failed`, all 7 in part B). This re-run replaced the 12:22 A+C-only run. Every g186–g197
> row is unchanged from that run.
> Each row reads: ratsimp-only seen hit (trace arm), then the fixed-core class, then the class under the exact-only
> control (probe-local `%mr_seenp` = exact `member`: a DIAGNOSTIC ARM, not a proposed fix), then the P0 route.
> The rule is `collapse` when the hit cuts the route **and** the control moves the class toward PASS. Every group
> below takes a ratsimp hit on its rule's nested `mr_int`, against the live top-level integrand (#2@#1; g192 #3@#2),
> and every fixed-core class is deferred, as in probe 10's final30. In every group the nested call never dispatches,
> which excludes the competing `%mr_intSum` fault.

- class 1 g186: undetermined → **collapse(non-9.1 site 1_1_1_5_r5)**; control **unverified** (off the top-level
  noun, not PASS).
  - **Control route.** The four-term sum dispatches, and each term takes 1_4_1_r18 → 1_1_1_3_r17 / r8 / 1_1_1_2_r37.
    Two 1_1_1_3_r17 re-dispatches are identical and exact-cut.
  - **Control answer.** It holds `'integrate((x^3*(d*x+c)^n)/((b*x)/D+a/D),x)` terms next to hypergeometric ones.
  - **P0.** 1_1_1_5_r8 in pass 1.
- class 1 g187: undetermined → **collapse(non-9.1 site 1_1_2_11_r3)**; control **unverified**.
  - **Control route.** Each term takes 1_4_1_r18 → 1_1_2_9_r2 → 1_1_2_2_r39, giving a hypergeometric answer. No
    noun appears in its printed prefix; the full answer is in the .out.
  - **P0.** 1_2_1_9b_r5 in pass 2.
- class 1 g188: undetermined → **collapse(non-9.1 site 1_1_2_9_r23)**; control **verified**. P0: the same r23, in
  **pass 2**.
- class 1 g189: undetermined → **collapse(non-9.1 site 1_1_3_8_r18)**; control **verified**. P0: 1_2_2_5_r3 in pass
  1.
- class 1 g190: undetermined → **collapse(non-9.1 site 1_1_3_8_r29)**; control **verified**. P0: 9_1_r16 in pass 2.
- class 1 g191: undetermined → **collapse(non-9.1 site 1_2_1_3_r24)**; control **verified**. P0: the same r24, in
  **pass 2**.
- class 1 g192: undetermined → **collapse(non-9.1 site 1_2_1_9b_r6)**; control **verified**. The hit is on r6's
  nested call under the top 1_2_1_9b_r2. P0: 1_2_1_9b_r1 in pass 2.
- class 1 g193: undetermined → **collapse(non-9.1 site 1_2_1_9b_r5)**; control **verified**. P0: the same r5, in
  **pass 2**.
- class 1 g194: undetermined → **collapse(non-9.1 site 1_2_2_7_r12)**; control **contains-noun** (not PASS).
  - **Term B.** 1_4_1_r18 → 1_2_2_4_r61, whose identical re-dispatch is exact-cut to `'integrate`.
  - **Term A.** 1_4_1_r18 → 1_2_2_3_r99. Its nested call gets a 1_2_2_3_r32 misfire (repl error) and no fire,
    leaving `'unintegrable[(e*x^2+d)^q/((c*x^4)/A+(b*x^2)/A+a/A),x]`.
  - **P0.** The same r12, in **pass 2**.
- class 1 g195: undetermined → **collapse(non-9.1 site 1_2_2_7_r13)**; control **verified**. P0: 1_2_2_7_r12 in
  pass 2.
- class 1 g197: undetermined → **collapse(non-9.1 site 1_4_3_r56)**; control **unverified** (not PASS).
  - **Control route.** 17.2 s, 61 calls. The first summand's chain 1_4_1_r18 → 1_4_1_r18 → 1_4_3_r56 rescales
    `(x/2^k+1/2^k)` at every level, never an exact repeat, down to the depth cap (#17 depthcap).
  - **Control answer.** It carries an `'integrate` of the scaled form beside the closed atan/log part.
  - **P0.** 1_4_3_r55 in pass 2.

**P0 route, all eleven.** No P0 route took a seen hit that decided the verdict. Where P0 used the same rule (g188
r23, g191 r24, g193 r5, g194 r12) it fired in **pass 2**, after `%mr_seen` was popped, so its nested call entered
with seenlen 0.
