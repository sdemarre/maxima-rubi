> Task 4 Step 5 mechanism lines for probe 10's groups — class 1, groups g81–g283, NEW TIMEOUTS, new errors, collapse family.
> Reads: probes/matcher/10-p5-attribution.class1.summary.out (groups g81–g283, NEW TIMEOUTS) and probes/matcher/10-p5-attribution.class1-newerror.out.
> Written 2026-09-14 by read-only analysis of the committed probe-10 outputs (commit 295effa); claims marked 'inferred' or 'not determined' are not measured.

# Task 4 Step 5 — mechanism lines, class 1, part C (g81–g283, NEW TIMEOUTS, new errors)

Inputs: `probes/matcher/10-p5-attribution.class1.summary.out` (GROUP g81 at line 4358 through the
`NEW TIMEOUTS 941` block), the raw runs `…class1-{final30,p0,final120,newerror}.out`, the arm records
`test/corpus_class1.p5-run{2,3,4}.out`, the 100 s re-check
`test/corpus_class1.p5-final.timeout-rerun/corpus_class1.p5-run1.timeout100s.out`, the rule files
`rules/class1/*.mac` (final tree and `0a6664c`), and the Rubi source (read through
`generator/generate_rules.py`'s own reader). Read-only analysis, 2026-09-14, HEAD 7726072.

The evidence conventions of `task4-mechanisms-class2-3.md` apply unchanged: traces, answers not recorded,
arms r2/r3/r4, table order, timeouts. So do its families OPT, DEG, NOUN, IGT, RETRY, 9.1, NEGQ, INNER,
VERIFY-TIMEOUT. "All arms X" means r2/r3/r4 all read X.

**Tags.** Every group line ends with `[defect: IGtQ]`, `[defect: negQ]`, both (two tags) or
`[defect: none seen]`. Criteria:

- **IGtQ:** a final-route rule's cond carries a translated IGtQ/ILtQ/ILeQ test, and the binding is a
  non-integer. The binding is read from the integrand, or from a direct substitution of it. Where it is
  inferred rather than evident, the line says so.
- **negQ:** a final-route rule's cond calls `%mr_negQ` on a positive-form symbolic argument (a symbol, a
  ratio of symbols, or a symbolic exponent n), or on `b^2-4*a*c` where the corpus answer shows that Rubi
  took the other branch. Rubi's `PosAux` reads a bare symbol, and products and powers of symbols, as
  positive (IntegrationUtilityFunctions.m:608–634). Uses whose reading agrees with Rubi's route are not
  tagged: numeric arguments, `-c/a`, and the `1/(q-x^2)` step of `1_1_2_1_r13`, whose atanh form the
  corpus answers show.

Two further translation defects that are neither IGtQ nor negQ are marked `[also: NE]` / `[also: MUL]`
(families below).

## Families (class 1, part C)

- **PF-EVEN (odd-n partial fractions on an even n).** The fire signature is `1_1_2_1_r13, 1_2_1_1_r12,
  1_2_1_2_r3, 1_2_1_2_r9, 1_1_1_1_r3`, followed by `1_1_3_1_r13/r14/r22` or `1_1_3_2_r35/r36`.
  - **Rubi's conditions.** These are Rubi's `1/(a+b x^n)` and `x^m/(a+b x^n)` rules for odd n
    (`IGtQ[(n-3)/2,0]`, `IGtQ[(n-1)/2,0]`, and `IGtQ[m,0]` for r35/r36) or n ≡ 2 mod 4 (r22:
    `IGtQ[(n-2)/4,0]`).
  - **Generated conds.** They read `is((n - 3)/2 > 0)`, `is((n - 1)/2 > 0) and is(m > 0)` and
    `is((n - 2)/4 > 0)` (IGT). They therefore fire on n = 4, 6, 8, 10, 12 and on m = 1/2.
  - **How these integrands arrive.** Directly, or after the x^(1/k) substitutions of `1_1_3_2_r71`,
    `1_1_2_2_r27`, `1_1_1_2_r32` and `1_1_2_4_r34`.
  - **Symbolic a/b.** `%mr_negQ(a/b)` additionally selects the NegQ branch (r14/r36).
  - **The answer.** A `%mr_rt(∓a/b, n)` / `cos((2k-1)π/n)` log-atan sum, not Rubi's route: the corpus
    answers for n = 4, 8 have the `a^(1/4)`, `atan(1±√2 x…)` form of `1_1_3_1_r23` and the
    `1_1_3_2_r17` gcd substitution.
  - **Outcomes.** Timeouts (usually with the top-level fire present), errors, and some `unverified`.
  - **P0.** P0 answered the same integrands with `1_4_1_r34`, `1_3_4_r1/r3`, `1_4_1_r23`, `1_3_3_r10`
    or `1_1_3_3_r60`, with nested fall-throughs. Its pass-1 trace never shows this chain.
- **NE (`!=` read as factorial-equals).** Rubi's `With[{k=GCD[m+1,n]}, … /; k!=1]` is generated as
  `is(k != 1)`.
  - **Where.** `1_1_3_2_r17` and `1_1_3_4_r30` on the final routes below. The same text is in
    `1_1_3_2_r18`, `1_1_3_6_r9`, `1_1_3_8_r15`, `1_2_2_4_r29/r30`, `1_2_3_2_r8` and `1_2_3_4_r29/r30`.
  - **The parser.** Maxima 5.50.0 `src/nparse.lisp:1310–1316` defines `!` as a postfix factorial
    (lbp 160) and has no `!=` token, so the test reads `is((k!) = 1)`. That is true for k = 1 and
    false for k ≥ 2, the inverse of Rubi's test.
  - **Consequence.** A fire of r17/r30 therefore means k = 1. Its repl re-dispatches the same integrand
    (x → x^1), which the seen guard returns as Maxima `integrate`. Where Rubi needs k ≥ 2 (for example
    x^5/(1-x^8)), the substitution is never taken.
  - **P0.** P0 had the same text in its repl (`if is(k != 1) = true then … else false`); the substrate
    moved it into the cond (INNER).
  - **Evidence status.** This reading comes from the parser source and was not run.
- **MUL (missing product).** `1_1_4_1_r1`'s repl reads `b*(n - j) (p + 1)*x^(n - 1)`. The Rubi source
  has the same space-as-multiplication, `…/(b*(n - j) (p + 1)*x^(n - 1))`, and the generator copied the
  space. Maxima does not read the space as a product (parse not run). Only r1 is confirmed.
- **EXPAND-NOUN.** A rule whose Rubi condition asks for an integer power before `ExpandIntegrand`
  (`IGtQ[p,0]`, `IGtQ[p,-2]`, `ILtQ[p,0]`) accepts a fractional power through the translated comparison
  (IGT).
  - **What the trace shows.** It answers alone (nfires=1) with a top-level noun.
  - **Consistent reading (not traced).** The expansion of a fractional power returns the integrand, and
    the seen guard hands it to Maxima `integrate`.
- **MFLAGS.** The fire lists are identical on both cores, and r4 (`mr_model_flags=false`) restores PASS.
  The model flags change the shape of an intermediate integrand or of the answer. Class 2/3 named this
  per group.
- **ZERO.** The integrand carries a coefficient written `2+2a-2(1+a)` (or with c), which is identically
  0. Maxima keeps it unsimplified, so rules bind it as a or c, divide by it, or read its sign. The corpus
  answers show that Rubi's input had it removed. P0 verified these entries on other routes.
- **CATCH-1 (class-1 Unintegrable catch-alls).** `1_1_1_4_r42`, `1_1_2_8_r123`, `1_1_2_9_r107`,
  `1_1_2_5_r39`, `1_2_1_3_r112`, `1_2_2_3_r100`, `1_2_2_7_r42`, `1_2_3_4_r102`, `1_2_3_5_r24`,
  `1_2_3_6_r28`. A nested (or top-level) catch-all answer gives contains-noun (or deferred). This is the
  NOUN family with class-1 rule ids.

## Group lines g81–g283

- class 1 g81 (4 entries, deterministic, final timeout top=1_1_3_4_r24): `x^k (A+Bx^3)/(a+bx^3)`,
  k = 7/2, 3/2, 1/2, -1/2.
  - **Substrate.** `1_1_3_4_r24` binds `(e x)^m` with e=1 through `e_.`. The P0 literal
    `(e*x)^m*(a+b*x^n)^p*(c+d*x^n)` has no default, so P0 answered with the x^(1/2) substitution
    `1_4_1_r34` and a fall-through.
  - **Nested.** r24's `Int[(e x)^m/(a+bx^3)]` runs `1_1_3_2_r63`/`r71` into PF-EVEN: `1_1_3_2_r36` with
    m = 1/2 or n = 6, or `1_1_3_1_r14` on n = 6, with a/b symbolic.
  - **Timing.** The top-level r24 fire is in every 30 s list; timeout at 120 s (VERIFY-TIMEOUT). All
    arms timeout.
  — follows from: faithful Optional binding, exposing the IGtQ and NegQ translations [defect: IGtQ] [defect: negQ]
- class 1 g82 (4 entries, deterministic, final timeout top=1_2_1_2_r119): `(a+bx+cx^2)^(3/2)/(d+ex)^7`,
  `^8`, `sqrt(quad)/(d+ex)^(5/2)`, `1/((d+ex)^(3/2) sqrt(quad))`. Both cores put r119 at top.
  - **Nested chains.** P0: `1_2_1_9b_r5/r27/r1`. Substrate: `1_4_1_r18` (e2353/e2354), or the elliptic
    chain `1_1_2_3_r48`, `1_2_1_2_r93`, `9_1_r8`, `1_2_1_9b_r32`, `1_4_1_r10` (e2445/e2466).
  - **Timing.** The top-level fire is in the 30 s list; timeout at 120 s.
  - **Arms.** r3 verifies e2353/e2445 in 0.9 s.
  — follows from: condition retry (e2353, e2445); not determined for e2354/e2466 [defect: none seen]
- class 1 g83 (4 entries, deterministic, final timeout top=1_2_1_2_r15; final120 top = the P0 top
  `1_2_2_2_r8` ×2, `1_2_2_4_r5`, `1_2_3_2_r6`): `x^3/sqrt(a±bx^2±cx^4)`, `x^5/(…)^(3/2)`,
  `x^5/sqrt(a+bx^3+cx^6)`.
  - **At 30 s.** Only the nested `1_1_2_1_r13, 1_2_1_1_r15, 1_2_1_2_r15` (+`1_2_1_2_r113`) have fired.
    The substitution's `(x)/sqrt(quad)` binds `1_2_1_2_r15` with d=0 through `d_.` (P0 literal
    `(d + e*x)*(a + b*x + c*x^2)^p`), then 1/sqrt(quad) → atanh: the corpus's own form.
  - **At 120 s.** The top-level substitution rule has fired, so rubi returned, and the entry still times
    out (VERIFY-TIMEOUT).
  - **P0.** `1_2_1_6_r1` + the substitution rule, or `1_3_4_r20`. All arms timeout.
  — follows from: faithful Optional binding [defect: none seen]
- class 1 g84 (4 entries, deterministic, final timeout top=1_2_1_2_r95; final120 top = the P0 top
  `1_2_2_2_r8` / `1_2_3_2_r6`): `(a+bx^k+cx^2k)^(j/2)/x^i`. Same shape as g83.
  - **Nested.** `1_1_2_1_r13, 1_2_1_2_r99, 1_2_1_2_r95`; r95 binds `sqrt(quad)/x^3` with d=0 (OPT).
  - **Timing.** At 120 s the top-level substitution has fired and the entries still time out
    (VERIFY-TIMEOUT).
  - **P0.** P0's top alone (`1_2_2_2_r8` / `1_3_3_r15`). All arms timeout.
  — follows from: faithful Optional binding [defect: none seen]
- class 1 g85 (4 entries, deterministic, final timeout top=1_2_2_2_r13; final120 error 114.3 / 117.9 /
  85.7 s, e632 timeout): `(d+ex)^2/(a+b(d+ex)^2+c(d+ex)^4)^k`, k = 2, 3.
  - **P0.** `1_4_2_r24` alone (the expandToSum normalization, nested fall-through).
  - **Substrate nested chain.** `1_4_1_r18`, `1_2_1_1_r12`, `1_2_1_2_r3/r9`, `1_2_2_3_r27` (+`r36`),
    `1_2_2_2_r13`.
  - **Wrong branch.** `1_2_2_3_r27` is Rubi's `NegQ[b^2-4*a*c]` split (q=Rt[a/c,2], r=Rt[2q-b/c,2]). The
    corpus answers have the real-root form `atan(…/sqrt(b-sqrt(b^2-4*a*c)))` of the other branch, and
    `%mr_negQ` reads the unknown-sign sum as negative.
  - **Fires and deaths.** The top-level linear-substitution fire is absent at 30 s and 120 s. At 120 s
    three entries die with error at 86–118 s; the kind is not recorded. All arms timeout.
  — follows from: not determined which change routes the substituted integrand to 1_2_2_2_r13; the
  r27 branch is the pre-existing NegQ reading [defect: negQ]
- class 1 g86 (4 entries, deterministic, final timeout top=1_2_2_2_r14; final120 error 72.1 / 96.2 /
  94.5 s; e646 is record error 23.8 s): `(d+ex)^4/(…)^2`, `(…)^3`. The g85 chain with `1_2_2_2_r14`
  (m>3).
  - **Arms.** e646: r2 error 24.2 s, r4 error 28.7 s, r3 timeout. The rest time out in all arms.
  — follows from: as g85 [defect: negQ]
- class 1 g87 (4 entries, deterministic, final timeout top=1_2_2_2_r17; final120 error 116.9 / 93.0 /
  95.6 s, e620 timeout): `1/((d+ex)^k (…))`, k = 2, 4. The g85 chain with `1_2_2_2_r17` (m<-1), plus
  `1_2_2_4_r39` for k = 4. r4 e620 error 24.2 s. — follows from: as g85 [defect: negQ]
- class 1 g88 (4 entries, deterministic, final timeout top=1_2_3_2_r6; final120 error 56.5–64.8 s ×4):
  `x^5/(a+bx^3+cx^6)`, `1/(x(…))`, and the n = 4 pair.
  - **Substrate.** The top-level x^n substitution `1_2_3_2_r6` has fired in the 30 s list, so rubi
    returned. Nested: `1_2_1_2_r9` → `r3` (log) and `1_2_1_1_r12` → `1_1_2_1_r13` (atanh), plus
    `1_1_1_1_r1`, `1_2_1_2_r80` for the 1/x pair. This is the corpus's log + atanh((b+2cx^n)/√(b²-4ac))
    shape.
  - **P0.** `1_3_4_r19` or `1_4_1_r29` alone; P0's r6 literal `x^m*(a+b*x^n+c*x^n2)^p` did not bind.
  - **Deaths.** All four die at 120 s; the error kind is not recorded. All arms timeout.
  — follows from: faithful binding; the cost is verification [defect: none seen]
- class 1 g89 (4 entries, deterministic, final unverified top=1_1_1_3_r25): `(a+bx)^n/(x^3(c+dx)^n)`,
  `(1-x)^n/(x^3(1+x)^n)`, `(a+bx)^m(c+dx)^(-1-m)/(e+fx)^2`, `…/(e+fx)`.
  - **Substrate.** `1_1_1_3_r25` binds x^-3 as `(a_.+b_.x)^m` with a=0 (the P0 literal
    `(a + b*x)^m*(c + d*x)^n*(e + f*x)^p` has no defaults). Its nested integral is answered by
    `1_1_1_3_r61` (hypergeometric).
  - **P0.** `1_1_1_6_r7` (Px rule) with a fall-through.
  - **Result.** The Rubi hypergeometric form, not closed by the zero chain. All arms unverified.
  — follows from: faithful Optional binding [defect: none seen]
- class 1 g90 (4 entries, deterministic, final unverified top=1_1_2_8_r49): `1/(x^k(d+ex)sqrt(d^2-e^2x^2))`,
  k = 1, 3.
  - **Substrate.** `1_1_2_8_r49` (m, n = -1, -3 / -1, integers) binds, then `9_1_r8` + `1_1_3_8_r18`, or
    `1_1_2_11_r2`.
  - **P0.** The later `1_1_2_8_r54` (`x^m(a+bx^2)^p/(c+dx)` literal) after `1_4_2_r25` or a class-1
    chain. All arms unverified.
  — follows from: faithful binding [defect: none seen]
- class 1 g91 (4 entries, deterministic, final unverified top=1_2_1_2_r117):
  `(d+ex)^(k/2)/sqrt(ade+(cd^2+ae^2)x+cdex^2)` (the quadratic factors as (d+ex)(ae+cdx)). Both cores put
  r117 at top.
  - **P0 nested.** `1_2_1_9b_r5` → `9b_r1` (divide out d+ex).
  - **Substrate nested.** The elliptic chain `1_1_2_3_r48, 1_2_1_2_r93, 1_1_2_3_r42, 1_2_1_3_r89` (+`r56`).
  - **Result.** Unverified; the corpus answers (2–4 steps) are algebraic. All arms unverified.
  — follows from: not determined from the traces (why 9b_r1 no longer answers) [defect: none seen]
- class 1 g92 (4 entries, deterministic, final unverified top=1_2_1_3_r15):
  `(f+gx)(cd^2-bde-be^2x-ce^2x^2)^(3/2 or 5/2)/(d+ex)^(1 or 2)`.
  - **Substrate.** `1_2_1_3_r15` (Rubi `IGtQ[p,0]` → ExpandIntegrand) accepts p = 3/2, 5/2 through
    `is(p > 0)`. nfires=1; the answer is unverified.
  - **P0.** `1_4_2_r25` → `1_3_3_r6` (polyGCD cancel); P0's r15 literal did not bind. All arms unverified.
  — follows from: binding change exposing the IGtQ translation [defect: IGtQ]
- class 1 g93 (3 entries, deterministic, final contains-noun top=1_1_2_8_r20): `(A+Bx)(a+cx^2)^k/x`,
  k = 2, 3, 4. Both cores put r20 at top.
  - **Nested.** P0: fall-through (nfires=1). Substrate: `1_1_2_8_r123` (CATCH-1) → marker.
  - **Corpus.** 2 steps, no Unintegrable. All arms contains-noun.
  — follows from: faithful binding (NOUN); why r20's reduced integral reaches the catch-all is not
  determined [defect: none seen]
- class 1 g94 (3 entries, deterministic, final contains-noun top=1_2_1_3_r54):
  `(2-5x)x^(k/2)/(2+5x+3x^2)^(j/2)`.
  - **Substrate.** `1_2_1_3_r54` binds x^(k/2) as `(d+ex)^m` with d=0 (OPT). Its sub-integral runs
    `1_4_1_r34` (substitution), then `1_2_2_7_r42` (CATCH-1; e1077 `1_2_2_6_r9`) → marker.
  - **P0.** `1_4_1_r34` at top after a 1.2.2 chain.
  - **Corpus.** Elliptic answers, no Unintegrable. All arms contains-noun.
  — follows from: faithful Optional binding; why the quartic sub-integral reaches the catch-all is not
  determined [defect: none seen]
- class 1 g95 (3 entries, deterministic, final contains-noun top=1_2_2_8_r4): `1/((d+ex)^k sqrt(a+cx^4))`.
  - **Substrate.** `1_2_2_8_r4` (Rubi's own rule, ahead of 1.3.4) binds. Nested: `1_2_2_8_r19` (/r16),
    `1_2_2_7_r37`, `1_2_2_3_r87`, `1_2_2_3_r59` (`%mr_negQ(c/a)` on symbolic c/a), `1_2_2_3_r100`
    (CATCH-1) → marker, plus `1_2_2_4_r94`.
  - **P0.** `1_4_2_r19` → `1_3_4_r9`. All arms contains-noun.
  — follows from: faithful binding; the nested NegQ reading [defect: negQ]
- class 1 g96 (3 entries, deterministic, final deferred top=1_1_1_3_r17): `x^2(a+bx)^n/(c+dx)`,
  `(2+3x)^m(3+5x)^k/(1-2x)`.
  - **Substrate.** `1_1_1_3_r17` (ExpandIntegrand; x^2 bound as (0+x)^2) answers alone with a top-level
    noun.
  - **P0.** `1_1_1_3_r19` / `r29`.
  - **Arms.** r3 reads expected for e925 and e3182 (0.1 / 0.3 s), so r17 accepts only on a retried
    binding. e3181 is deferred in all arms.
  — follows from: condition retry (e925, e3182); e3181 not determined [defect: none seen]
- class 1 g97 (3 entries, deterministic, final deferred top=1_1_2_8_r107): `(a+bx^2)^p/(x^k(d+ex)^j)`.
  Both cores put r107 at top (`ILtQ[n,-1]`; n = -2, -3 are integers).
  - **P0.** The ExpandIntegrand sum dispatched through `1_4_1_r7`.
  - **Substrate.** nfires=1, a top-level noun: the class 2 g1 shape. All arms deferred.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g98 (3 entries, deterministic, final deferred top=1_1_3_4_r26): `(ex)^(k/2) sqrt(c+dx^4)/(a+bx^4)`.
  - **Substrate.** `1_1_3_4_r26` (Rubi `IGtQ[n,0] && IGtQ[p,0]`) accepts p = 1/2: EXPAND-NOUN.
  - **P0.** `1_4_2_r8` → `1_3_4_r3` (the corpus's 3-step AppellF1). All arms deferred.
  — follows from: binding change (P0's r26 literal did not bind) exposing the IGtQ translation [defect: IGtQ]
- class 1 g99 (3 entries, deterministic, final deferred top=1_1_3_4_r30): `x/((4c+dx^3)sqrt(c+dx^3))`,
  `x/((1-x^3)^(1/3)(1+x^3))`, `x/((1-x^3)^(2/3)(1+x^3))`.
  - **Substrate.** `1_1_3_4_r30` binds x as `x^m_.` (m=1), so k = gcd(2,3) = 1 and `is(k != 1)` reads
    true (NE). The x → x^1 substitution re-dispatches the integrand, which the seen guard returns as a
    top-level noun (nfires=1).
  - **P0.** Rubi's dedicated rules `1_1_3_4_r52` / `r56` / `r57`, which sit after r30 in 1.1.3.4. All
    arms deferred.
  — follows from: faithful Optional binding exposing the `!=` translation [defect: none seen] [also: NE]
- class 1 g100 (3 entries, deterministic, final deferred top=1_1_4_4_r11): `(-1+x^3)/(-4x+x^4)^(2/3)`,
  `(2-x^2)(6x-x^3)^(1/4)`, `(1+x^4)sqrt(5x+x^5)` (1-step derivative-divides in the corpus).
  - **P0.** `1_1_4_4_r2` alone.
  - **Substrate.** `1_1_4_4_r2` declines (its `integerp((m+1)/n)` with the Optional m=0), and the later
    `1_1_4_4_r11` (ExpandIntegrand) answers alone with a top-level noun. All arms deferred.
  — follows from: not determined from the traces (P0's r2 binding is not recorded) [defect: none seen]
- class 1 g101 (3 entries, deterministic, final deferred top=1_2_1_1_r5): `(bx+cx^2)^(5/4, 3/4, 1/4)`.
  - **Substrate.** `1_2_1_1_r5` (Rubi `IGtQ[p,0] && (EqQ[a,0] || …)`) binds a=0 through `a_.` and
    accepts p = 1/4..5/4 through `is(p > 0)`: EXPAND-NOUN.
  - **P0.** `1_2_1_1_r4` (non-Optional `a_`, bound a=0; PerfectSquareQ) → `1_1_1_2_r12`, verified. On the
    substrate r4's `a_` cannot bind the absent constant. All arms deferred.
  — follows from: G-1 plus faithful Optional binding, exposing the IGtQ translation [defect: IGtQ]
- class 1 g102 (3 entries, deterministic, final deferred top=1_2_2_1_r19):
  `(4ac+4c^2x^2+4cdx^3+d^2x^4)^(k/2)`. Both cores put r19 at top (the depressed-quartic substitution).
  - **Nested.** P0: `1_4_1_r29` / `1_2_2_5_r1`. Substrate: `1_4_2_r18` only, then a top-level noun.
  - **Arms.** r4 verified 0.5 / 0.6 / 4.1 s (MFLAGS); r2/r3 deferred.
  — follows from: model flags [defect: none seen]
- class 1 g103 (3 entries, deterministic, final deferred top=1_2_3_4_r100):
  `(fx)^m(d+ex^n)^k(a+cx^2n)^p`, k = 3, 2, 1.
  - **Substrate.** `1_2_3_4_r100` (IGtQ[q,0] with q = k, an integer, so Rubi applies it too) expands,
    and the sum yields no nested fire: a top-level noun (class 2 g1 shape).
  - **P0.** The manual 9.1 `u*(a*x^n)^m` (P0 `9_1_r16`). All arms deferred.
  — follows from: 9.1 regeneration; why the expansion yields no fire is not determined [defect: none seen]
- class 1 g104 (3 entries, deterministic, final deferred top=1_2_3_4_r99): `(fx)^m(d+ex^n)^k(a+bx^n+cx^2n)^p`.
  As g103 with `1_2_3_4_r99` (q = 1, 2, 1). — follows from: as g103 [defect: none seen]
- class 1 g105 (3 entries, deterministic, final deferred top=1_3_3_r7): `(1-x)/((2+x)sqrt(1∓x^3))`,
  `(1-x^2)/((1-x+x^2)(1-x^3)^(2/3))`.
  - **Substrate.** `1_3_3_r7` (Rubi `ILtQ[q,0]`) accepts q = -1/2, -2/3 through `is(q < 0)`. Its polyGCD
    rewrite ends in a top-level noun (e52/e53 add nested `1_4_1_r18`).
  - **P0.** Rubi's `1_4_3_r36` / `r55`.
  - **Arms.** r3 verified 0.3 s (e52, e53); r2/r4 deferred.
  — follows from: condition retry exposing the ILtQ translation (e52/e53); e878 not determined [defect: IGtQ]
- class 1 g106 (3 entries, deterministic, final deferred top=9_1_r27): 1.2.1.2 e1734–e1736,
  `(d+ex)^m/(a^2+2abx+b^2x^2)^k`, k = 1, 2, 3 (P0 expected). [collapse-family] See **Collapse family**.
  - **P0.** The collapse rule `9_1_r28` (`rubi_hybrid_exact`) → `1_1_1_2_r37`.
  - **Substrate.** The same Rubi rule, generated `9_1_r27`, alone: its rewrite hits the ratsimp seen
    guard and returns a Maxima noun. All arms deferred.
  — follows from: 9.1 regeneration (`rubi_hybrid_exact` → `mr_int`) meeting the ratsimp seen guard [defect: none seen]
- class 1 g107 (3 entries, deterministic, final error top=1_1_3_2_r13; all three are also new errors):
  `1/(x^3(1∓x^8))`, `1/(x^7(1-x^8))`.
  - **Top level.** `1_1_3_2_r13` (Rubi `ILtQ[Simplify[(m+1)/n+p+1],0]`) accepts -1/4 and -3/4. Its fire
    is in every list, so rubi returned.
  - **Nested.** `x^(m+8)/(1∓x^8)` runs `1_1_3_2_r35/r36` on n = 8 ((8-1)/2 = 7/2) and the PF-EVEN
    prefix. The coefficients are numeric, so NegQ reads correctly.
  - **Death.** error 6.2 / 28.6 / 6.5 s (record), 14.3–29.7 s (final30). The kind is not recorded.
  - **P0.** `1_3_4_r1` (P0's r13 literal did not bind `1-x^8`). All arms error.
  — follows from: faithful binding exposing the IGtQ translation [defect: IGtQ]
- class 1 g108 (3 entries, deterministic, final timeout top=1_1_2_4_r29): `x^k(A+Bx^2)/(a+bx^2)`,
  k = 7/2, 3/2, -1/2.
  - **Substrate.** `1_1_2_4_r29` binds e=1 through `e_.`. Nested: the x^(1/2) substitution `1_1_2_2_r27`
    (+`r23`), then PF-EVEN `1_1_3_1_r14` on 1/(a+bt^4) ((4-3)/2 = 1/2; a/b symbolic).
  - **Timing.** Top-level fire in the 30 s list; timeout at 120 s (VERIFY-TIMEOUT).
  - **P0.** `1_4_1_r34`. All arms timeout.
  — follows from: faithful Optional binding exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g109 (3 entries, deterministic, final timeout top=1_1_3_3_r21; e466 final120 top
  `1_1_2_4_r34`; e65/e615 final120 error 97.9 / 86.2 s): `1/((a+bx^2)(c+dx^2)sqrt(x))`,
  `1/((a+bx^4)(c+dx^4))` ×2.
  - **Substrate.** `1_1_3_3_r21` (partial fractions; no P0 defmatch record) → PF-EVEN `1_1_3_1_r14`
    (n = 4, symbolic).
  - **Timing.** For e466 the top-level x^(1/2) substitution fires only by 120 s.
  - **P0.** `1_4_1_r34` / `1_4_1_r29`. r4 e615 error 29.8 s; otherwise timeout.
  — follows from: faithful binding exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g110 (3 entries, deterministic, final timeout top=1_1_3_4_r18): `(A+Bx^3)/(x^(k/2)(a+bx^3))`,
  k = 3, 5, 7.
  - **Substrate.** `1_1_3_4_r18` (m<-1, e=1 through `e_.`) fired in the 30 s list. Nested: PF-EVEN
    through `1_1_3_2_r36`, or `1_1_3_2_r71` → t^6 → `1_1_3_1_r14`.
  - **P0.** `1_4_1_r34`. VERIFY-TIMEOUT; all arms timeout.
  — follows from: faithful Optional binding exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g111 (3 entries, deterministic, final timeout top=1_2_1_2_r113; e981 final120 top
  `1_2_2_2_r8`): `(d+ex)^4/(quad)^(3/2)`, `x^9/(quartic)^(3/2)`, `x^7/(quartic)^(3/2)`.
  - **Substrate.** `1_2_1_2_r113` binds (P0's literal did not; P0 answered with `1_2_1_6_r1` alone).
  - **Nested (e2382/e981).** `1_2_1_9b_r5` (Rubi `IGtQ[p,-2]`; accepts p = -3/2 through `is(p > -2)`),
    `9b_r32`, `1_2_1_2_r117`, `9_1_r8`, `1_2_1_3_r56`, `1_2_1_1_r15`, `1_2_1_2_r15`, `1_1_2_1_r13`.
  - **Nested (e982).** `1_2_1_3_r45` instead.
  - **Timing.** Top-level fire at 30 s for e2382/e982, by 120 s for e981 (VERIFY-TIMEOUT). All arms timeout.
  — follows from: faithful binding exposing the IGtQ translation (e2382, e981) [defect: IGtQ]
- class 1 g112 (3 entries, deterministic, final timeout top=1_4_1_r25): `(A+Bx^2)/(x^(k/2)(bx^2+cx^4))`.
  Both cores put `1_4_1_r25` (x^r content removal) at top.
  - **Nested.** P0: `1_4_1_r34` only. Substrate: `1_1_2_4_r25` (e=1 through `e_.`) → `1_1_2_2_r27` →
    PF-EVEN `1_1_3_1_r14` (n = 4, symbolic). e192/e194 add `1_1_2_2_r6` on a quarter-integer
    (m+1)/2+p+1.
  - **Timing.** Top-level fire at 30 s (VERIFY-TIMEOUT). All arms timeout.
  — follows from: faithful Optional binding exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g113 (3 entries, deterministic, final unverified top=1_1_1_3_r29):
  `x^k/((1-x)^(1/3)(2-x)^(1/3))`, k = 4, 3; `(1-x)^n x^3/(1+x)^n`.
  - **Top.** Both cores put r29 at top for e863/e864; e966 P0 `1_1_1_6_r7`.
  - **Substrate nested.** `1_1_3_2_r17` (NE: a fire means k = 1, an identity substitution and Maxima
    `integrate`), `1_2_1_1_r17`, `1_1_1_2_r30`, `1_1_1_4_r6/r12`; e966 `1_1_1_2_r38`, `1_1_1_4_r6`.
  - **P0 nested.** `1_1_1_4_r12` or none. All arms unverified.
  — follows from: not determined from the traces; the r17 fire carries the `!=` misreading [defect: none seen] [also: NE]
- class 1 g114 (3 entries, deterministic, final unverified top=1_1_1_3_r57): `(a+bx)^(1+n)/(x^2(a-bx)^n)`,
  `(a+bx)^(1∓n)(c+dx)^(1±n)/(bc+ad+2bdx)^2` (m+n = 1, 2 are integers).
  - **e995.** Both cores put r57 at top; the nested chain differs (substrate `1_1_1_4_r46, 1_1_1_2_r39,
    1_1_1_3_r61, 1_3_4_r3, 1_1_1_3_r25`).
  - **e3126/e3130.** r57 binds where P0's literal `(a+b*x)^m*(c+d*x)^n/(e+f*x)^2` did not (P0
    `1_1_1_6_r5`).
  - **Result.** Hypergeometric chains. All arms unverified.
  — follows from: faithful binding [defect: none seen]
- class 1 g115 (3 entries, deterministic, final unverified top=1_1_2_2_r6): `1/(x^k(-2-3x^2)^(3/4))`,
  k = 2, 4, 6.
  - **Fires.** The same fire list on both cores (`1_1_3_1_r32, 1_1_2_1_r26, 1_1_2_2_r6`).
  - **Arms.** r4 verified 0.1–0.2 s: MFLAGS.
  - **IGT on both cores.** `1_1_2_2_r6`'s `is((m+1)/2+p+1 < 0)` (Rubi ILtQ) accepts -1/4, -5/4, -9/4 on
    both cores; it is not the change.
  — follows from: model flags [defect: IGtQ]
- class 1 g116 (3 entries, deterministic, final unverified top=1_2_1_2_r105):
  `(ade+(cd^2+ae^2)x+cdex^2)^(k/2)/(d+ex)^(k+3)` (2-step algebraic corpus answers).
  - **Substrate.** `1_2_1_2_r105` binds (P0's literal did not; P0 `1_4_2_r25` → `1_3_3_r6` polyGCD
    cancel). Nested: `1_2_1_2_r133/r95`, `1_1_1_4_r46`, `1_1_2_1_r13`. All arms unverified.
  — follows from: faithful binding; why the Rubi-form answer is unverified is not determined [defect: none seen]
- class 1 g117 (3 entries, deterministic, final unverified top=1_2_1_2_r109): `sqrt(d+ex)sqrt(quad)`,
  `sqrt(quad)/sqrt(d+ex)` ×2 (1-step corpus answers).
  - **Substrate.** r109, with the g91 elliptic chain nested.
  - **P0.** r109 with the `9b_r1` cancel (e2030), or `1_1_1_2_r12` → `1_3_3_r6`. All arms unverified.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g118 (3 entries, deterministic, final unverified top=1_2_1_2_r111): `sqrt(d+ex)/(quad)^k`,
  k = 3, 3/2, 5/2. The three entries do not share a mechanism:
  - **e2068.** Identical fire lists on both cores; r4 verified 2.2 s (MFLAGS).
  - **e2025.** P0 `1_4_1_r18` alone; the substrate adds `1_2_1_3_r55` and top r111; all arms unverified.
  - **e2076.** The substrate adds the elliptic chain `1_1_2_3_r48, 1_2_1_2_r93, 9_1_r8, 1_2_1_9b_r32,
    1_4_1_r18, 1_2_1_3_r55`; all arms unverified.
  — follows from: model flags (e2068); faithful binding (e2025, e2076) [defect: none seen]
- class 1 g119 (3 entries, deterministic, final unverified top=1_2_1_2_r95):
  `(quad)^(k/2)/(d+ex)^(k+2)` (1-step corpus answers).
  - **Substrate.** r95 → `1_2_1_2_r133` → `1_1_1_4_r46` → `1_1_2_1_r13`.
  - **P0.** `1_4_2_r25` → `1_3_3_r6`. All arms unverified.
  — follows from: faithful binding (as g116) [defect: none seen]
- class 1 g120 (3 entries, deterministic, final unverified top=1_2_3_2_r34):
  `(dx)^m(a+bx^n+cx^2n)^p` (n = 3, n).
  - **Substrate.** `1_2_3_2_r34` (the FracPart rewrite) → `1_1_3_4_r78` (AppellF1): Rubi's 2-step
    AppellF1 answer, not closed by the zero chain.
  - **P0.** The manual 9.1 `u*(a*x^n)^m`. All arms unverified.
  — follows from: 9.1 regeneration [defect: none seen]
- class 1 g121 (2 entries, deterministic, final contains-noun top=1_1_1_3_r27): `(c+dx)^3/(x(a+bx)^k)`,
  k = 2, 3.
  - **Substrate.** `1_1_1_3_r27`; its nested integral binds `1_1_1_4_r42` (CATCH-1) → marker.
  - **P0.** `1_1_1_3_r29` / `r59`.
  - **Arms.** r3 verified 0.2 / 0.5 s.
  — follows from: condition retry [defect: none seen]
- class 1 g122 (2 entries, deterministic, final contains-noun top=1_1_1_3_r29):
  `(5-4x)^k(1+2x)^(-3-m)(2+3x)^m`.
  - **Substrate.** r29 → nested `1_1_1_4_r42` (CATCH-1; +`1_1_1_4_r12`) → marker.
  - **P0.** `1_1_1_4_r47` alone. r3 verified 1.0–1.2 s.
  — follows from: condition retry [defect: none seen]
- class 1 g123 (2 entries, deterministic, final contains-noun top=1_1_2_4_r20): `(c+dx^2)^3/(x(a+bx^2)^k)`.
  Both cores put r20 (x^2 substitution) at top.
  - **Nested.** Substrate: `1_1_1_4_r42` (CATCH-1) + `1_1_1_3_r13/r27`. P0: `1_1_1_3_r13/r29`.
  - **Arms.** r3 verified for e285 (0.2 s); CN for e224.
  — follows from: condition retry (e285); e224 not determined [defect: none seen]
- class 1 g124 (2 entries, deterministic, final contains-noun top=1_1_2_7_r47): `(d+ex)^3(a+cx^2)^p`.
  - **Substrate.** `1_1_2_7_r47` binds (P0's literal did not); its reduced integral reaches
    `1_1_2_9_r107` (CATCH-1) → marker.
  - **P0.** `1_2_1_9b_r29` after `1_2_1_1_r18, 1_1_2_3_r20, 1_1_2_11_r1`. All arms contains-noun.
  — follows from: faithful binding (NOUN); why the reduction reaches the catch-all is not determined [defect: none seen]
- class 1 g125 (2 entries, deterministic, final contains-noun top=1_2_1_2_r117): `(d+ex)^3(quad)^p`.
  Both cores put r117 at top.
  - **Nested.** P0 fell through. The substrate reaches `1_2_1_3_r112` (CATCH-1) → marker.
  - **Corpus.** 3-step hypergeometric, no Unintegrable. All arms contains-noun.
  — follows from: faithful binding (NOUN) [defect: none seen]
- class 1 g126 (2 entries, deterministic, final contains-noun top=1_2_1_3_r55): `(2-5x)/(x^(3/2)(…)^(3/2))`,
  `(2-5x)/((…)^(5/2)sqrt(x))`. As g94 with `1_2_1_3_r55` (+`r57`). All arms contains-noun.
  — follows from: faithful Optional binding [defect: none seen]
- class 1 g127 (2 entries, deterministic, final contains-noun top=1_2_2_3_r22): `(1-2x^2)/(1±2x^2+4x^4)`.
  Both cores put r22 at top.
  - **Nested.** P0 fell through. The substrate's quadratic sub-integrals bind `1_2_3_5_r24` (CATCH-1,
    through `x^n_.` n=1) → marker.
  - **Arms.** r3 verified 1.4 s for e63 (as class 2 g9: the catch-all accepts only on a retried
    binding); e59 CN in all arms.
  — follows from: condition retry (e63); e59 not determined [defect: none seen]
- class 1 g128 (2 entries, deterministic, final contains-noun top=1_2_2_3_r59): `(d+ex^2)/sqrt(a-cx^4)`,
  `/sqrt(-a+cx^4)`. Both cores put r59 at top.
  - **Nested.** P0: the long elliptic chain. Substrate: `1_2_2_3_r100` (CATCH-1) → marker.
  - **NegQ.** `NegQ[-c/a]` (and `c/(-a)`) is true in Rubi as well, so this is not tagged. All arms
    contains-noun.
  — follows from: not determined why r59's `mr_int((1+qx^2)/sqrt(a+cx^4))` reaches the catch-all [defect: none seen]
- class 1 g129 (2 entries, deterministic, final contains-noun top=1_2_2_7_r17):
  `(A+Bx^2)/((d+ex^2)^k sqrt(a+cx^4))`.
  - **Substrate.** `1_2_2_7_r17` (Rubi's binomial rule, q integer). Nested: `1_2_2_7_r37`,
    `1_2_2_3_r87`, `1_2_2_3_r59` (`%mr_negQ(c/a)` symbolic), `1_2_2_3_r100` (CATCH-1) → marker.
  - **P0.** `1_2_2_7_r16`, the trinomial variant, with b bound to 0 (DEG). All arms contains-noun.
  — follows from: G-1 / faithful binding; the nested NegQ reading [defect: negQ]
- class 1 g130 (2 entries, deterministic, final deferred top=1_1_1_3_r5): `x sqrt(a+bx)/(c+dx)^(5/2)`,
  `(A+Bx)(d+ex)^(7/2)/(a+bx)^(5/2)`.
  - **Substrate.** `1_1_1_3_r5` (Rubi `… || IGtQ[p,0] && (…)`) accepts p = 1/2 / 7/2 through
    `is(p > 0)`: EXPAND-NOUN.
  - **P0.** `1_1_1_3_r26` / `r6`. r3 verified 0.3 s for e2241.
  — follows from: faithful Optional binding (e581, x as (0+x)) / condition retry (e2241), exposing the
  IGtQ translation [defect: IGtQ]
- class 1 g131 (2 entries, deterministic, final deferred top=1_1_2_3_r11): `(a-bx^2)^(2/3 or 5/3)(3a+bx^2)`.
  - **Substrate.** `1_1_2_3_r11` (Rubi `IGtQ[p,0] && IGtQ[q,0]`) binds q=1 through `q_.` and accepts
    p = 2/3, 5/3: EXPAND-NOUN.
  - **P0.** `1_1_2_3_r20` after `1_1_2_1_r4`. All arms deferred.
  — follows from: faithful Optional binding exposing the IGtQ translation [defect: IGtQ]
- class 1 g132 (2 entries, deterministic, final deferred top=1_1_2_6_r12):
  `(ex)^m(A+Bx^2)/((a+bx^2)(c+dx^2))`, `(ex)^m(a+bx^2)^p(A+Bx^2)/(c+dx^2)`. Both cores put r12
  (ExpandIntegrand) at top.
  - **Nested.** P0's expansion dispatched (`1_1_2_3_r1, 1_4_1_r7`). The substrate has nfires=1: a
    top-level noun. All arms deferred.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g133 (2 entries, deterministic, final deferred top=1_1_2_8_r123): 1.2.1.3 e255
  `(A+Bx)(a+cx^2)/x`, 1.3.1 e261 `(3+2x^2)/((-1+x)^2 x)`.
  - **Substrate.** The catch-all `1_1_2_8_r123` (CATCH-1) binds `(a+bx^2)^p` with p=1 through `p_.` and
    answers at top level.
  - **P0.** `1_2_1_9b_r32` / `1_1_2_8_r91`.
  - **Rubi.** The 2-step reductions are not reached (e.g. r20 needs a non-Optional `p_` on an implicit
    exponent 1). All arms deferred.
  — follows from: faithful Optional binding / G-1 [defect: none seen]
- class 1 g134 (2 entries, deterministic, final deferred top=1_1_2_9_r19):
  `(A+Bx)(d+ex)^(m or 1+m)/(a+cx^2)`.
  - **Substrate.** `1_1_2_9_r19` (IntegersQ[n], n=1 through `n_.`) expands a symbolic power, giving
    nfires=1 and a top-level noun.
  - **P0.** `1_2_1_3b_r68`, whose 3-arg `%mr_expandIntegrand((d+ex)^m, (f+gx)/(quad))` dispatched. All
    arms deferred.
  — follows from: faithful Optional binding [defect: none seen]
- class 1 g135 (2 entries, deterministic, final deferred top=1_1_3_4_r77): `(ex)^m/((a+bx^4)(c+dx^4)^(k/2))`.
  - **Substrate.** `1_1_3_4_r77` (Rubi `IGtQ[p,-2] && (IGtQ[q,-2] || …)`) accepts q = -1/2, -3/2
    through `is(q > -2)`: EXPAND-NOUN.
  - **P0.** `1_4_2_r8` → `1_3_4_r3` (AppellF1). All arms deferred.
  — follows from: binding change exposing the IGtQ translation [defect: IGtQ]
- class 1 g136 (2 entries, deterministic, final deferred top=1_1_3_6_r31):
  `(ex)^m(A+Bx^n)/((a+bx^n)(c+dx^n))`, `(ex)^m(a+bx^n)^p(A+Bx^n)/(c+dx^n)`.
  - **Substrate.** `1_1_3_6_r31` (ExpandIntegrand) answers alone with a top-level noun.
  - **P0.** The manual 9.1 `u*(a*x^n)^m`. All arms deferred.
  — follows from: 9.1 regeneration; why the expansion yields no fire is not determined [defect: none seen]
- class 1 g137 (2 entries, deterministic, final deferred top=1_1_3_7_r37): `(c+dx)/sqrt(-a+bx^4)`,
  `(c+dx+ex^2+fx^3)(a+bx^4)^p`.
  - **Substrate.** `1_1_3_7_r37` (n = 4, so IGtQ[2,0] holds) splits Pq with `mr_sum(lambda…)`; the
    split has no nested fire, giving a top-level noun.
  - **P0.** `1_2_2_5_r3` (the same split for the quartic). All arms deferred.
  — follows from: faithful binding; why the `mr_sum` split yields no fire is not determined [defect: none seen]
- class 1 g138 (2 entries, deterministic, final deferred top=1_2_2_3_r100): `(√a+x^2√c)/sqrt(-a+cx^4)`,
  `(1+x^2 sqrt(c/a))/sqrt(-a+cx^4)`.
  - **Substrate.** `1_2_2_3_r100` (CATCH-1) answers at top level.
  - **P0.** `1_2_2_3_r60` (trinomial) with b bound to 0 (DEG).
  - **Rubi.** The 3-step elliptic_e rule is not reached; why is not determined. All arms deferred.
  — follows from: G-1 [defect: none seen]
- class 1 g139 (2 entries, deterministic, final deferred top=1_2_2_3_r12): `(2+3x^2)(5+x^4)^(1/2 or 3/2)`.
  - **Substrate.** `1_2_2_3_r12` (Rubi `IGtQ[p,0] && IGtQ[q,-2]`) accepts p = 1/2, 3/2: EXPAND-NOUN.
  - **P0.** `1_2_2_3_r34` (trinomial) with b=0 (DEG). All arms deferred.
  — follows from: G-1 exposing the IGtQ translation [defect: IGtQ]
- class 1 g140 (2 entries, deterministic, final deferred top=1_2_3_2_r2): `(dx)^m(a+bx^n+cx^2n)^(3/2 or 1/2)`.
  - **Substrate.** `1_2_3_2_r2` (Rubi `IGtQ[p,0]`) accepts p = 3/2, 1/2: EXPAND-NOUN.
  - **P0.** The manual 9.1 `u*(a*x^n)^m`. All arms deferred.
  — follows from: 9.1 regeneration exposing the IGtQ translation [defect: IGtQ]
- class 1 g141 (2 entries, deterministic, final deferred top=1_2_3_5_r24): `(1±x^4)/(1∓2x^4+x^8)`.
  - **Substrate.** `1_2_3_5_r24` (CATCH-1) answers at top level.
  - **P0.** `1_3_3_r10` (factor).
  - **Arms.** r3 verified 0.3 s: the catch-all accepts only on a retried binding (as class 2 g9).
  — follows from: condition retry [defect: none seen]
- class 1 g142 (2 entries, deterministic, final deferred top=1_3_4_r3): `(a+bx)^n(c+dx)^p/x`,
  `(a+bx)^m(c+dx)^(-1-m)(e+fx)^p`.
  - **Substrate.** `1_3_4_r3` answers alone in 8.8–10.6 s with a top-level noun; its substitution has no
    nested fire.
  - **P0.** `1_1_1_6_r7` alone. The corpus's 2–3-step AppellF1 rules are not reached.
  - **Arms.** r3 deferred 1.1–1.5 s.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g143 (2 entries, deterministic, final error top=-; both also new errors):
  `(b+2cx+3dx^2)(bx+cx^2+dx^3)^7`, `x^7(b+cx+dx^2)^7(b+2cx+3dx^2)` (1-step derivative-divides).
  - **Death.** No fire; error at 9.1 / 9.7 s (record), 16.0 / 15.5 s (final30), 8.7 / 9.2 s (newerror).
    The kind is not recorded.
  - **P0.** Verified through `1_4_1_r20` / `1_2_1_6_r1`.
  - **Arms.** r3 verified 0.4 / 1.5 s; r2/r4 error. The dispatch dies before any rule answers, and only
    with condition retry on.
  — follows from: condition retry [defect: none seen]
- class 1 g144 (2 entries, deterministic, final timeout top=1_1_1_2_r32): `1/(x(a±bx^4)^(3/4))`.
  - **Substrate nested.** `1_1_1_2_r32` (the t^4 linear-pair substitution) → PF-EVEN `1_1_3_1_r14` on
    n = 4 with symbolic a. The top-level x^4 substitution fire is absent at 30 s and 120 s.
  - **P0.** `1_2_2_2_r8`, with a nested r32 that led to `1_1_2_2_r4`.
  - **Arms.** r3 verified 0.1 s for e1237.
  — follows from: condition retry (e1237) exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g145 (2 entries, deterministic, final timeout top=1_1_1_3_r15):
  `1/(x(2-3x^2)^(3/4)(4-3x^2))`, `1/(x(-2+3x^2)(-1+3x^2)^(3/4))`.
  - **Substrate nested.** `1_1_1_2_r32/r13` → PF-EVEN `1_1_3_1_r14` / `r13` on n = 4. The coefficients
    are numeric, so NegQ reads exactly. The top-level fire is absent.
  - **P0.** `1_1_2_4_r20` at top, verified 0.2 / 1.3 s. r3 verified 0.1 s for e1085.
  — follows from: condition retry (e1085) exposing the IGtQ translation [defect: IGtQ]
- class 1 g146 (2 entries, deterministic, final timeout top=1_1_1_3_r6): `(A+Bx)sqrt(a+bx)/(d+ex)^(5/2)`
  and its mirror. Both cores put r6 at top (fired at 30 s: VERIFY-TIMEOUT).
  - **Nested.** P0: `1_1_1_2_r12`. Substrate: `1_1_1_2_r10` (Rubi `ILtQ[m,-1] && Not[IntegerQ[n]] &&
    GtQ[n,0]`), which accepts m = -3/2 through `is(m < -1)`, then `1_1_1_2_r23` → `1_1_2_1_r16`.
  - **Arms.** r3 verified 0.1 / 0.5 s and r4 verified 0.2 / 0.2 s, so both switches are needed.
  — follows from: condition retry + model flags, exposing the ILtQ translation [defect: IGtQ]
- class 1 g147 (2 entries, deterministic, final timeout top=1_1_3_1_r13; e1367 final120 unverified
  114.1 s): `1/(2+3x^4)`, `1/(1+x^6)`.
  - **Top level.** `1_1_3_1_r13` (Rubi `IGtQ[(n-3)/2,0] && PosQ[a/b]`, odd n) accepts n = 4, 6 ((n-3)/2
    = 1/2, 3/2) and fired in the 30 s list, so rubi returned.
  - **P0.** Rubi's n = 4 rule `1_1_3_1_r23` (it sits after r13) / `1_4_1_r23`. All arms timeout.
  — follows from: faithful binding (P0's r13 literal did not bind) exposing the IGtQ translation [defect: IGtQ]
- class 1 g148 (2 entries, deterministic, final timeout top=1_1_3_3_r14): `(a+bx^4)/(c+dx^4)^k`, k = 2, 3.
  - **Substrate.** The top-level `1_1_3_3_r14` (no P0 defmatch record) fired. Nested: `1_1_3_1_r4`
    (ILtQ on -3/4) and PF-EVEN `1_1_3_1_r14` (n = 4, symbolic).
  - **P0.** `1_1_3_3_r60` alone. VERIFY-TIMEOUT; all arms timeout.
  — follows from: faithful binding exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g149 (2 entries, deterministic, final timeout top=1_1_3_4_r11): `1/(x^k sqrt(a+bx^3)sqrt(c+dx^3))`.
  - **Substrate.** The top-level x^3 substitution `1_1_3_4_r11` fired → `1_1_1_3_r22` (+`r25`) →
    `1_1_2_1_r15` (atanh; the corpus's own form).
  - **P0.** `1_3_4_r3` alone. VERIFY-TIMEOUT; all arms timeout.
  — follows from: faithful binding; the cost is verification [defect: none seen]
- class 1 g150 (2 entries, deterministic, final timeout top=1_2_1_2_r111): `(d+ex)^(3/2 or 1/2)/(quad)^(5/2)`.
  Both cores put r111 at top (fired at 30 s: VERIFY-TIMEOUT).
  - **Nested.** P0: `1_2_1_9b_r5` only. Substrate: `1_1_2_3_r48`, `1_2_1_2_r93`, `1_2_1_9b_r5/r32`,
    `1_2_1_3_r54/r55`.
  - **IGT (inferred).** `9b_r5` accepts the reduced p = -3/2 through `is(p > -2)`. All arms timeout.
  — follows from: faithful binding [defect: IGtQ]
- class 1 g151 (2 entries, deterministic, final timeout top=1_2_1_2_r93):
  `1/(sqrt(d+ex)sqrt(quad))`, `1/(sqrt(f+gx)sqrt(quad))`.
  - **Substrate.** The top-level `1_2_1_2_r93` (elliptic substitution) fired after `1_1_2_3_r42`.
  - **P0.** `1_2_1_4_r30` after `1_1_1_3_r55`. VERIFY-TIMEOUT; all arms timeout.
  — follows from: faithful binding [defect: none seen]
- class 1 g152 (2 entries, deterministic, final timeout top=1_2_1_3_r55):
  - **e1647.** Both cores put r55 at top. Nested: P0 `9b_r5/9b_r1`; substrate the elliptic chain
    (`1_1_2_3_r48`, `1_2_1_2_r93`, `9_1_r8`, `1_2_1_9b_r32`, `1_4_1_r18`). The top-level fire is at 30 s.
  - **e130** `(A+Bx^2)/(x(quartic)^3)`. P0: `1_2_2_6_r2` alone. At 30 s the substrate list holds the
    nested log/atanh chain; at 120 s the top-level x^2 substitution `1_2_2_4_r9` has fired.
  VERIFY-TIMEOUT; all arms timeout. — follows from: faithful binding; the cost is verification [defect: none seen]
- class 1 g153 (2 entries, deterministic, final timeout top=1_2_1_3_r90): `sqrt(ade+…)/(x(d+ex))`,
  `(…)^(3/2)/(x(d+ex))`. Both cores put r90 at top (fired at 30 s).
  - **Nested.** P0: `1_2_1_1_r3, 1_2_1_2_r99` / `1_4_2_r25, 1_3_3_r6`. Substrate: `1_1_2_1_r13`,
    `1_2_1_2_r99`, `1_2_1_1_r15`, `1_2_1_3_r1` (+`r89`, `1_2_1_2_r109`, `1_1_1_4_r46`, `1_2_1_1_r4`).
  VERIFY-TIMEOUT; all arms timeout. — follows from: not determined which change moves the nested chain [defect: none seen]
- class 1 g154 (2 entries, deterministic, final timeout top=1_2_1_5_r26): `x(quad)^(k/2)/(d-fx^2)`.
  - **Substrate.** The top-level `1_2_1_5_r26` binds g=0 through `g_.` (P0 literal
    `(a+b*x+c*x^2)^p*(d+f*x^2)^q*(g+h*x)`); nested `1_4_1_r18`.
  - **P0.** `1_4_2_r17` alone. VERIFY-TIMEOUT; all arms timeout.
  — follows from: faithful Optional binding [defect: none seen]
- class 1 g155 (2 entries, deterministic, final timeout top=1_2_2_1_r5; e625 final120 error 85.8 s):
  `1/(a+b(d+ex)^2+c(d+ex)^4)^k`, k = 2, 3.
  - **Substrate.** The g85 chain (`1_2_2_3_r27` NegQ branch) ending in `1_2_2_1_r5`.
  - **P0.** `1_4_2_r18` alone. e634: r2/r4 error 24–25 s.
  — follows from: as g85 [defect: negQ]
- class 1 g156 (2 entries, deterministic, final timeout top=1_2_2_1_r7): `1/(sqrt(d+ex)(quad))`,
  `(b+2cx)sqrt(d+ex)/(quad)^2`.
  - **Both cores.** Both run the nested `1_2_1_1_r12`, `1_2_1_2_r3/r9` and `1_2_2_1_r7`. r7 is Rubi's
    `NegQ[b^2-4*a*c]` split; the corpus answers are the real-root atanh(√2√c√(d+ex)/√(2cd-e(b-√…))) form.
  - **P0.** Went on to the top-level `1_2_1_2_r82` (e2292) → `1_2_1_3_r42` (e1620) and verified.
  - **Substrate.** That top-level fire is absent at 30 s and 120 s. All arms timeout.
  — follows from: not determined from the traces; the NegQ branch is on both cores' routes [defect: negQ]
- class 1 g157 (2 entries, deterministic, final timeout top=1_2_2_2_r16; final120 error 95.1 / 94.5 s):
  `(d+ex)^4/(a+b(d+ex)^2+c(d+ex)^4)` (and the f-scaled form). The g85 chain with `1_2_2_2_r16`.
  r3 error 27.3 / 28.7 s. — follows from: as g85 [defect: negQ]
- class 1 g158 (2 entries, deterministic, final timeout top=1_2_2_6_r1):
  - **e30** `x^3(A+Bx+Cx^2)/(quartic)^2`. P0 answered with `1_2_2_5_r3` at top after a long chain. On
    the substrate `1_2_2_6_r1` (d=1 through `d_.`) answers, with nested `1_1_2_1_r13, 1_2_1_1_r12,
    1_2_1_3_r44, 1_2_2_4_r9, 1_4_1_r18`. r3 CN 12.2 s.
  - **e40** `(dx)^m(A+Bx+Cx^2)/(quartic)`. Both cores put r1 at top (P0 26.4 s, nfires=1). Substrate
    nested `1_1_2_2_r39` (p=-1), `1_2_2_4_r43`, `1_4_1_r18`.
  All arms timeout. — follows from: faithful Optional binding (e30); not determined (e40) [defect: none seen]
- class 1 g159 (2 entries, deterministic, final timeout top=1_2_3_1_r6): `1/(sqrt(x)(a+bx^2+cx^4)^k)`,
  k = 2, 3.
  - **Substrate nested.** The prefix, `1_2_2_3_r27` and `1_2_3_3_r33` (both `NegQ[b^2-4*a*c]`), `r40`,
    `1_2_3_1_r6`. The top-level sqrt(x) substitution fire is absent.
  - **Corpus.** `(-b-sqrt(b^2-4*a*c))^(1/4)` forms: the other branch.
  - **P0.** `1_4_1_r34` alone. All arms timeout.
  — follows from: not determined which change routes the substituted integrand; the NegQ reading [defect: negQ]
- class 1 g160 (2 entries, deterministic, final timeout top=1_2_3_2_r17): `1/(x^k(1-3x^4+x^8))`, k = 3, 7.
  - **Substrate.** The top-level `1_2_3_2_r17` fired → `1_2_3_4_r49` (+`r43`) partial fractions →
    PF-EVEN `1_1_3_2_r36` on n = 4 (numeric) + prefix.
  - **P0.** `1_3_3_r10` alone.
  - **Arms.** r3 deferred 0.4 s; r2/r4 timeout.
  — follows from: faithful binding exposing the IGtQ translation [defect: IGtQ]
- class 1 g161, g242, g243 (2 + 1 + 1 entries, deterministic, final timeout top=1_4_2_r26 / 1_4_1_r34 /
  1_4_2_r27): `1/(sqrt(x)sqrt(x(a+bx+cx^2)))`, `…(a+bx^2+cx^4)`, `sqrt(x)/sqrt(x^3(…))`.
  - **Substrate.** `1_4_2_r26/r27` (expandToSum of the generalized trinomial) → `1_2_4_1_r4` /
    `1_2_4_2_r3`, `1_1_2_1_r13`. The top-level `1_4_1_r34` fires by 30 s (g242) or by 120 s
    (g161, g243).
  - **P0.** `1_4_1_r34` alone.
  - **Arms.** r4 verified 0.7 s in every entry (MFLAGS); r2/r3 timeout.
  — follows from: model flags [defect: none seen]
- class 1 g162 (2 entries, deterministic, final timeout top=9_1_r8): `1/((quad)sqrt(1-dx)sqrt(1+dx))`,
  `1/((d+ex+fx^2)sqrt(a+cx^2))`.
  - **Fires.** Only `9_1_r8` (the constant rule; not a collapse rule) at 30 s and 120 s.
  - **P0.** `1_2_1_4_r24` (+`1_2_1_3_r8`).
  - **Arms.** e795 r4 verified 1.6 s (MFLAGS); e67 timeout in all arms.
  - **Reading.** Either the top-level dispatch does not return, or its fires stay in the unflushed pipe.
  — follows from: model flags (e795); not determined (e67) [defect: none seen]
- class 1 g163 (2 entries, deterministic, final unexpected top=1_3_3_r17): `F(x)sqrt(x-x^2)`,
  `F(x)/sqrt(x-x^2)`; noun-expected (CannotIntegrate, 0 steps).
  - **P0.** No-answer.
  - **Substrate.** `1_3_3_r17` removes the x content, and its nested integral has no fire. Maxima
    integrate then returns an answer that differentiates back (self=1): unexpected, a yardstick case.
    All arms unexpected.
  — follows from: not determined from the traces (P0's r17 literal / its moved `ExponMin` test) [defect: none seen]
- class 1 g164 (2 entries, deterministic, final unverified top=1_1_1_3_r61): `(1-x)^n/(x^2(1+x)^n)`,
  `(a+bx)^m(c+dx)^(-1-m)/(e+fx)`.
  - **Substrate.** `1_1_1_3_r61` (hypergeometric closed form; x^-2 as (0+x)^-2) answers at top: the
    corpus's own 1-step form, not closed by the zero chain.
  - **P0.** `1_1_1_6_r7`. All arms unverified.
  — follows from: faithful Optional binding [defect: none seen]
- class 1 g165 (2 entries, deterministic, final unverified top=1_1_2_7_r56): `(a+cx^2)^p/(d+ex)^2`,
  `(a+bx^2)^p/(d+ex)^2`. Both cores put r56 at top.
  - **NegQ.** r56 is Rubi `ILtQ[n,-1] && NegQ[a/b]`; symbolic a/c reads NegQ on both cores.
  - **Nested.** P0: `1_1_1_4_r47`. Substrate: `1_1_1_3_r65` (AppellF1).
  - **Result.** AppellF1, unverified. All arms unverified.
  — follows from: not determined from the traces [defect: negQ]
- class 1 g166, g167 (2 + 2 entries, deterministic, final unverified top=1_1_2_8_r12 / 1_1_2_8_r48):
  `x^2(d+ex)/(d^2-e^2x^2)^(3/2)`, `x^2/((d+ex)sqrt(d^2-e^2x^2))` (+ the a-forms).
  - **Substrate.** Rubi's `1_1_2_8_r12/r48` (integer m, n) bind; nested `1_1_3_2_r115`, `1_1_2_2_r2`.
  - **P0.** `1_2_1_3b_r35` / `1_1_2_8_r90`.
  - **Arms.** r3 verified 0.3–0.4 s in all four entries.
  — follows from: condition retry [defect: none seen]
- class 1 g168 (2 entries, deterministic, final unverified top=1_1_3_2_r107):
  - **e2762** `(cx)^(-1-3n/2)/(a+bx^n)`. The hypergeometric catch-all r107 (p=-1) answers at top; P0
    `1_1_3_2_r110`.
  - **e1024** `x/sqrt(2+2a-2(1+a)+cx^4)` (ZERO). r107 accepts p=-1/2 through `is(p < 0)`, where Rubi
    needs ILtQ or GtQ[a,0], with a the zero form. P0 `1_2_2_6_r2`.
  All arms unverified. — follows from: not determined (e2762); binding change exposing the ILtQ
  translation (e1024) [defect: IGtQ]
- class 1 g169, g279 (2 + 1 entries, deterministic, final unverified top=1_1_4_1_r1 / 1_4_2_r11):
  `sqrt(1/x+sqrt(1/x))`, `(ax^m+bx^(1+m+mp))^p`, `(x^m(a+bx^(1+mp)))^p`.
  - **Substrate.** `1_1_4_1_r1` answers (at top, or nested under `1_4_2_r11`). Its repl
    `b*(n - j) (p + 1)*x^(n - 1)` lacks a `*` (MUL), so the answer cannot equal Rubi's.
  - **P0.** `1_2_3_1_r2` / `1_1_4_4_r11` / `1_4_2_r11` alone. All arms unverified.
  — follows from: faithful binding reaching a repl with the MUL translation defect [defect: none seen] [also: MUL]
- class 1 g170 (2 entries, deterministic, final unverified top=1_2_2_2_r17):
  `1/(x^k sqrt(2+2a-2(1+a)+bx^2+cx^4))`, k = 2, 4 (ZERO).
  - **Substrate nested.** `1_1_4_4_r10`, `1_2_2_6_r3` (Rubi `IGtQ[p,-2]`; accepts p=-1/2 through
    `is(p > -2)`), `1_2_2_4_r39`, top r17.
  - **P0.** `1_3_3_r17`. All arms unverified.
  — follows from: binding change on the zero-form coefficient exposing the IGtQ translation [defect: IGtQ]
- class 1 g171 (2 entries, deterministic, final unverified top=1_2_3_1_r4): `1/(1±2x^4+x^8)`.
  - **Substrate.** The top-level `1_2_3_1_r4` (perfect square → `1/(1±x^4)^2`) → `1_1_3_1_r4` (ILtQ on
    -3/4) → PF-EVEN `1_1_3_1_r13/r14` on n = 4 (numeric).
  - **P0.** `1_3_3_r10`. r3 verified 0.2 s.
  — follows from: condition retry exposing the IGtQ translation [defect: IGtQ]
- class 1 g172, g173, g175 (1 entry each, deterministic, final contains-noun top=1_1_1_3_r13 /
  1_1_1_5_r8 / 1_2_2_2_r8): `(c+dx)^3/(x(a+bx))`, `(a+bx)^n(c+dx^3)/x`, `x^7(quartic)^p`. Each has the
  same top rule on both cores.
  - **P0.** Fell through (nfires=1).
  - **Substrate.** The nested integral reaches CATCH-1: `1_1_1_4_r42`, `1_1_2_8_r123`, and
    `1_2_1_2_r117` → `1_2_1_3_r112` → marker. All arms contains-noun.
  — follows from: faithful binding (NOUN) [defect: none seen]
- class 1 g174 (1 entry, deterministic, final contains-noun top=1_2_1_3_r57):
  `(2-5x)/(x^(5/2)sqrt(2+5x+3x^2))`. As g94 with r57. — follows from: faithful Optional binding [defect: none seen]
- class 1 g176 (1 entry, deterministic, final contains-noun top=1_2_2_3_r23): `(2-3x^2)/(4+9x^4)`.
  - **Substrate.** `1_2_2_3_r23` (binomial form; NegQ[de] numeric) replaces P0's `1_2_2_3_r22`, which
    bound b=0 (DEG). Nested `1_2_3_5_r24` (CATCH-1) → marker, as g127. All arms contains-noun.
  — follows from: G-1 (NOUN) [defect: none seen]
- class 1 g177 (1 entry, deterministic, final contains-noun top=1_2_2_3_r64): `(c+ex^2)^3(a+cx^2+bx^4)^p`.
  Both cores put r64 at top.
  - **Nested.** Substrate: `1_2_3_5_r24` (CATCH-1) → marker.
  - **Arms.** r3 verified 1.3 s.
  — follows from: condition retry [defect: none seen]
- class 1 g178, g179 (1 entry each, deterministic, final contains-noun top=1_2_2_3_r65 / 1_2_2_3_r82):
  `(d+ex^2)^2/sqrt(a+cx^4)`, `1/((d+ex^2)^3 sqrt(a+cx^4))`.
  - **Substrate.** Rubi's binomial rules bind where P0 used the trinomial variants with b=0 (DEG:
    `1_2_2_5_r9` / `1_2_2_3_r81`). Nested `1_2_2_3_r59` (`%mr_negQ(c/a)` symbolic; g179 also
    `1_2_2_7_r17/r37`, `r87`) → `1_2_2_3_r100` (CATCH-1) → marker. All arms contains-noun.
  — follows from: G-1; the nested NegQ reading [defect: negQ]
- class 1 g180 (1 entry, deterministic, final contains-noun top=1_2_2_4_r10): `(d+ex^2)(a+cx^4)^5/x`.
  - **Substrate.** `1_2_2_4_r10` (x^2 substitution) → `1_1_2_8_r20` → `1_1_2_8_r123` (CATCH-1), as g93.
  - **P0.** `1_2_2_6_r2` → `1_1_2_8_r20`. All arms contains-noun.
  — follows from: faithful binding (NOUN) [defect: none seen]
- class 1 g181 (1 entry, deterministic, final contains-noun top=1_2_2_5_r3): `(1+2x+x^2+x^3)/(1+2x^2+x^4)`.
  Both cores put r3 at top.
  - **Nested.** P0: `1_3_2_r13, 1_2_1_6_r1, 1_2_2_6_r2`. Substrate: `1_2_2_3_r99, 1_2_1_6_r1,
    1_2_2_4_r5`, which yields the marker. All arms contains-noun.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g182 (1 entry, deterministic, final contains-noun top=1_2_3_2_r15): `(dx)^m/(a+bx^3+cx^6)^(3/2)`.
  - **Substrate.** `1_2_3_2_r15` (Rubi `IGtQ[n,0] && ILtQ[p,-1]`) accepts p=-3/2 through `is(p < -1)`,
    then `1_2_3_6_r28` (CATCH-1) → marker.
  - **P0.** The manual 9.1 `u*(a*x^n)^m`. All arms contains-noun.
  — follows from: 9.1 regeneration exposing the ILtQ translation [defect: IGtQ]
- class 1 g183 (1 entry, deterministic, final contains-noun top=1_2_3_4_r101): `(fx)^m(a+cx^2n)^p/(d+ex^n)^2`.
  - **Substrate.** `1_2_3_4_r101` (q=-2) → `1_2_3_4_r102` (CATCH-1), `9_1_r12`, `1_4_1_r7`, at 26.6 s.
  - **P0.** The manual 9.1 rule. All arms contains-noun.
  — follows from: 9.1 regeneration [defect: none seen]
- class 1 g184 (1 entry, deterministic, final deferred top=1_1_1_2_r34):
  `1/(x sqrt(a+(2+2c-2(1+c))x^4))` (ZERO).
  - **Substrate.** `1_1_2_1_r15` then `1_1_1_2_r34` (hypergeometric) give a top-level noun.
  - **P0.** `1_2_2_8_r1` chain. All arms deferred.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g185 (1 entry, deterministic, final deferred top=1_1_1_4_r42):
  `(a+bx)^m(c+dx)^(-3-m)(e+fx)(g+hx)`. The catch-all `1_1_1_4_r42` answers at top level; P0 used
  `1_1_1_4_r19`. All arms deferred.
  — follows from: not determined why r19 no longer answers [defect: none seen]
- class 1 g186 (1 entry, deterministic, final deferred top=1_1_1_4_r7):
  `(7+5x)sqrt(2-3x)sqrt(1+4x)/sqrt(-5+2x)`.
  - **Substrate.** `1_1_1_4_r7` (Rubi `IntegersQ[m,n,p] || IGtQ[n,0] && IGtQ[p,0]`) accepts n = p = 1/2
    through `is(n > 0) and is(p > 0)`: EXPAND-NOUN.
  - **P0.** `1_1_1_4_r13`. All arms deferred.
  — follows from: binding change exposing the IGtQ translation [defect: IGtQ]
- class 1 g187, g188 (1 entry each, deterministic, final deferred top=1_1_1_5_r5 / 1_1_2_11_r3):
  `(c+dx)^n(A+Bx+Cx^2+Dx^3)/(a+bx)`, `(cx)^m(A+Bx+Cx^2)/(a+bx^2)`.
  - **Substrate.** ExpandIntegrand rules whose Rubi conditions hold for these integer bindings (m = -1;
    p = -1) answer alone with a top-level noun.
  - **P0.** `1_1_1_5_r8` / `1_2_1_9b_r5` chain.
  - **Arms.** r3 verified 1.1 s for g188.
  — follows from: not determined (g187); condition retry (g188) [defect: none seen]
- class 1 g189 (1 entry, deterministic, final deferred top=1_1_2_3_r53): `sqrt(4+x^2)/sqrt(c+dx^2)`.
  - **Substrate.** `1_1_2_3_r53` (Rubi `IGtQ[p,0]`) accepts p=1/2: EXPAND-NOUN.
  - **P0.** `1_1_2_5_r19`. All arms deferred.
  — follows from: binding change exposing the IGtQ translation [defect: IGtQ]
- class 1 g190 (1 entry, deterministic, final deferred top=1_1_2_4_r20): `sqrt(a+bx^2)/(x sqrt(c+dx^2))`.
  Both cores put the x^2 substitution r20 at top.
  - **Nested.** P0: `1_1_1_3_r61/r62`. Substrate: `1_1_1_2_r32, 1_4_1_r34, 1_1_1_3_r59`, ending in a
    top-level noun.
  - **Arms.** r3 verified 0.4 s.
  — follows from: condition retry [defect: none seen]
- class 1 g191 (1 entry, deterministic, final deferred top=1_1_2_7_r27): `1/((3-x)(1-x^2)^(1/3))`.
  - **Substrate.** `1_1_2_7_r27` (Rubi `ILtQ[p,0] && …`) accepts p=-1/3 through `is(p < 0)`: EXPAND-NOUN.
  - **P0.** Rubi's `1_1_2_7_r52`. All arms deferred.
  — follows from: binding change exposing the ILtQ translation [defect: IGtQ]
- class 1 g192, g194 (1 entry each, deterministic, final deferred top=1_1_2_9_r23 / 1_2_1_3_r24):
  `sqrt(d+ex)/((a+cx^2 or quad)sqrt(f+gx))` (m=1/2, m+1/2=1 integer). Each has the same top rule on both
  cores.
  - **Nested.** P0's 3-arg ExpandIntegrand sum dispatched (`1_2_1_8_r2, 1_4_1_r7`). The substrate has
    nfires=1: a top-level noun. All arms deferred.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g193 (1 entry, deterministic, final deferred top=1_1_3_8_r18): `x^3(c+dx+ex^2+fx^3)(a+bx^4)^p`.
  The g137 shape: the `mr_sum` split has no nested fire. P0: `1_2_2_5_r3` chain. All arms deferred.
  — follows from: faithful binding; the split's missing fire is not determined [defect: none seen]
- class 1 g195 (1 entry, deterministic, final deferred top=1_2_1_9b_r2): `(1+x^3)sqrt(1+x)/(1+x^2)`.
  - **Substrate.** `1_2_1_9b_r6` → `1_2_1_9b_r2` (divide out 1+x) → top-level noun.
  - **P0.** The trinomial variant `9b_r1` after `9b_r5`, `1_2_1_9_r21`. All arms deferred.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g196, g197 (1 entry each, deterministic, final deferred top=1_2_2_7_r12 / 1_2_2_7_r13):
  `(A+Bx^2)(d+ex^2)^q/(a+bx^2+cx^4)`, `…/(a+cx^4)`.
  - **Substrate.** The 1.2.2.7 ExpandIntegrand rules answer alone with a top-level noun.
  - **P0.** P0's r12 sum dispatched (`1_4_1_r7`); for g197 P0 used r12 with b=0 (DEG). All arms deferred.
  — follows from: not determined (g196); G-1 (g197) [defect: none seen]
- class 1 g198 (1 entry, deterministic, final deferred top=1_2_3_4_r102): `(fx)^m(d+ex^n)^q/(a+bx^n+cx^2n)`.
  - **Substrate.** `1_2_3_4_r102` (CATCH-1) answers at top level.
  - **P0.** The manual 9.1 rule; Rubi's 5-step route is not reached. All arms deferred.
  — follows from: 9.1 regeneration [defect: none seen]
- class 1 g199 (1 entry, deterministic, final deferred top=1_3_3_r12): `(-1+x^2)/((1+x^2)sqrt(x+x^3))`.
  Both cores put `1_3_3_r12` at top. Rubi's condition is `ILtQ[p,0]`, and the cond accepts p=-1/2 on both
  cores.
  - **P0.** Its expansion dispatched (`9_1_r9, 1_2_2_5_r3, 1_4_1_r34, 1_1_2_2_r6, 1_4_1_r7`).
  - **Substrate.** nfires=1: a top-level noun. The substrate cond also runs the moved `factor(Px)` test
    (INNER).
  - **Arms.** r3 verified 0.3 s and r4 verified 1.2 s.
  — follows from: condition retry + model flags [defect: IGtQ]
- class 1 g200, g201, g202 (1 entry each, deterministic, final error top=1_1_3_1_r14 / 1_1_3_2_r35 /
  1_1_3_2_r36; all three also new errors): `1/(1-x^10)`, `x^5/(9+x^12)`, `x^5/(9-x^12)`.
  - **Top level.** The top-level PF-EVEN rule accepts n = 10 / 12 ((n-3)/2 = 7/2, (n-1)/2 = 11/2;
    numeric coefficients) and fired, so rubi returned.
  - **Death.** error 7.1 / 9.6 / 9.0 s (record), 19.3–28.2 s (final30). The kind is not recorded.
  - **P0.** `1_4_1_r23` / `1_3_4_r1` (the x^6 substitution → atan, 2 steps). All arms error.
  — follows from: faithful binding exposing the IGtQ translation [defect: IGtQ]
- class 1 g203 (1 entry, deterministic, final timeout top=1_1_1_2_r14; final120 top 1_1_3_2_r15):
  `1/(x(a+b sqrt(x))^8)`.
  - **Fires.** Nested `1_1_1_1_r1/r3, 1_1_1_2_r3/r14` at 30 s; `1_1_3_2_r15` by 120 s. The top-level
    sqrt(x) substitution fire is absent.
  - **P0.** `1_1_3_2_r110` alone. r3 verified 0.5 s.
  — follows from: condition retry [defect: none seen]
- class 1 g204 (1 entry, deterministic, final timeout top=1_1_1_2_r19): `(a-bx^4)^(1/4)/x`.
  - **Substrate.** Nested `1_1_1_2_r32` (t^4) → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic a) → r19. The
    top-level fire is absent.
  - **P0.** `1_2_2_2_r8` after `1_1_1_2_r37, 1_1_2_2_r4`. r3 verified 0.1 s.
  — follows from: condition retry exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g205 (1 entry, deterministic, final timeout top=1_1_1_4_r15; final120 unverified 119.8 s):
  `(a+bx)^m(A+Bx)/((c+dx)^m(e+fx))`. Both cores put r15 at top (fired at 30 s).
  - **Nested.** P0: `1_1_1_6_r7`. Substrate: `1_1_1_3_r61, 1_1_1_4_r47`.
  VERIFY-TIMEOUT; all arms timeout. — follows from: not determined from the traces [defect: none seen]
- class 1 g206, g207, g208, g249 (1 entry each, deterministic, final timeout / timeout / timeout /
  unverified, top=1_1_2_1_r26 / 1_1_2_1_r30 / 1_1_2_3_r32 / 1_1_2_1_r26): `1/(-2+3x^2)^(3/4)`,
  `1/(a+bx^2)^(5/6)`, `1/((-2+3x^2)(-1+3x^2)^(3/4))`, `1/(-2-3x^2)^(3/4)`.
  - **Fires.** Identical fire lists on both cores. Each top-level rule fired, so rubi returned.
  - **Arms.** r4 verified 0.1–0.3 s in all four (MFLAGS).
  — follows from: model flags [defect: none seen]
- class 1 g209 (1 entry, deterministic, final timeout top=1_1_2_4_r25): `(A+Bx^2)/(x^(5/2)(a+bx^2))`.
  As g108/g112.
  - **Substrate.** The top-level `1_1_2_4_r25` (e=1 through `e_.`) fired → `1_1_2_2_r27` → PF-EVEN
    `1_1_3_1_r14` (n = 4, symbolic).
  - **P0.** `1_4_1_r34`. VERIFY-TIMEOUT.
  — follows from: faithful Optional binding exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g210 (1 entry, deterministic, final timeout top=1_1_2_7_r54; final120 unverified 116.2 s):
  `1/((a+bx)(c+dx^2)^(1/4))`. Both cores put r54 at top (fired at 30 s).
  - **Nested.** The substrate's `1_1_3_4_r30` (NE: k = 1, identity substitution, Maxima integrate)
    replaces P0's `1_2_2_3_r76, 1_1_3_4_r58`.
  - **Arms.** r4 verified 0.8 s.
  — follows from: model flags [defect: none seen] [also: NE]
- class 1 g211 (1 entry, deterministic, final timeout top=1_1_3_2_r71): `1/((a+cx^4)sqrt(x))`.
  - **Substrate.** The top-level `1_1_3_2_r71` (x^(1/2)) fired → t^8 → PF-EVEN `1_1_3_1_r14` (n = 8,
    symbolic).
  - **P0.** `1_4_1_r34`. VERIFY-TIMEOUT.
  — follows from: faithful binding exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g212 (1 entry, deterministic, final timeout top=1_1_3_2_r84; final120 top 1_1_3_2_r107):
  `x^(1/3)/(-1+x^(5/6))`.
  - **Substrate.** `1_1_3_2_r84` (x^(1/6) substitution) → nested `1_1_3_2_r17` (NE), `r44`, `r107` (p=-1).
  - **P0.** `1_1_3_2_r110` alone. All arms timeout.
  — follows from: not determined from the traces [defect: none seen] [also: NE]
- class 1 g213, g214, g259, g260 (1 entry each, deterministic, final timeout / timeout / unverified /
  unverified, top=1_1_3_3_r17 / r45 / r14 / r17): `(a+bx^4)/(c+dx^4)`, `(a+bx^4)^2/(c+dx^4)^3`,
  `(c+dx^4)/(a+bx^4)^2`, `(c+dx^4)/(a+bx^4)`.
  - **Substrate.** The top-level 1.1.3.3 reduction fired → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic) +
    prefix.
  - **Classes.** g213/g214 time out (VERIFY-TIMEOUT); g259/g260 read unverified at 2.4–4.7 s.
  - **P0.** `1_1_3_3_r19/r60` (division / expansion). r3 verified 0.2 s for g214 only.
  — follows from: faithful binding exposing IGtQ and NegQ (g214 also condition retry) [defect: IGtQ] [defect: negQ]
- class 1 g215, g261 (1 entry each, deterministic, final timeout / unverified, top=1_1_3_4_r25):
  `x^k(a+bx^2)/((-c+dx)^(j/2)(c+dx)^(j/2))`.
  - **Substrate.** The top-level `1_1_3_4_r25` fired. Nested: `1_1_2_2_r39` (hypergeometric; accepts
    p = -3/2 / -1/2 through `is(p < 0)` with a = -c^2; Rubi needs ILtQ or GtQ[a,0]; binding inferred),
    `1_1_1_6_r2`, `1_1_2_11_r3`, `1_1_1_3_r18/r54/r64`.
  - **P0.** `1_1_1_6_r2`.
  - **Arms.** r2 (`mr_flat_wide=true`) verified 1.0 s in both; r3 verified 0.1 s for g215.
  — follows from: the narrow Flat reading (both) + condition retry (g215), exposing the ILtQ translation [defect: IGtQ]
- class 1 g216, g217 (1 entry each, deterministic, final timeout top=1_1_3_4_r44 / r45; g216 final120 top
  1_1_2_4_r34): `x^(7/2)/((a+bx^2)(c+dx^2))`, `1/(x^(5/2)(a+bx^2)(c+dx^2))`.
  - **Substrate.** Nested `1_1_3_5_r2` (partial fractions) → PF-EVEN `1_1_3_1_r14` (n = 4, symbolic).
    g216's top-level x^(1/2) substitution fires by 120 s.
  - **P0.** `1_4_1_r34` / `1_1_2_4_r48`.
  - **Arms.** r4 verified 3.9 s for g217.
  — follows from: faithful binding exposing IGtQ and NegQ (g217 also model flags) [defect: IGtQ] [defect: negQ]
- class 1 g218, g262 (1 entry each, deterministic, final timeout / unverified, top=1_1_3_4_r47 / r46;
  record unverified 24.7 / 25.0 s): `x/((a+bx^4)(c+dx^4))`, `x^5/(…)`.
  - **Substrate.** The top-level partial-fraction rule fired → `1_1_3_2_r36` on `x/(a+bx^4)` ((4-1)/2 =
    3/2; symbolic a/b) + prefix.
  - **Walls.** 25–30 s; arms unverified at 14.7–26.2 s, i.e. at the cap.
  - **P0.** `1_3_4_r3`.
  — follows from: faithful binding exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g219, g220 (1 entry each, deterministic, final timeout top=1_1_3_7_r37 / 1_1_3_8_r13):
  `(c+dx+ex^2)/sqrt(a+bx^3)`, `x(c+dx+ex^2)/(a+bx^3)^(3/2)`.
  - **Top level.** The top-level rule fired; `1_1_3_7_r37` (Rubi `IGtQ[n/2,0]`) accepts n = 3.
  - **Nested.** `1_4_1_r23` and `1_1_3_1_r31`. r31's `%mr_negQ(a)` on symbolic a takes Rubi's NegQ
    branch; the corpus answers carry the `(1+√3)`, `a^(1/3)` form of the PosQ rule `1_1_3_1_r30`.
  - **P0.** `1_3_4_r20/r21` (P0 also ran r31).
  - **Arms.** r3 unverified 0.4 / 0.8 s. VERIFY-TIMEOUT.
  — follows from: faithful binding exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g221, g225 (1 entry each, deterministic, final timeout top=1_1_4_3_r1 / 1_2_1_3_r31):
  `x^5(A+Bx^2)/(bx^2+cx^4)^(3/2)`, `x^2(A+Bx)/(bx+cx^2)^(3/2)`.
  - **Substrate.** The top-level rule fired (g225: x^2 as (0+x)^2, OPT). Nested `1_2_1_3_r31`,
    `1_1_4_2_r21`, `1_2_1_2_r15`, `1_2_1_1_r14`, `1_1_2_1_r13`.
  - **P0.** `1_2_2_6_r2` / `1_2_1_6_r1`.
  - **Arms.** r3 verified 0.5 s in both.
  — follows from: condition retry [defect: none seen]
- class 1 g222 (1 entry, deterministic, final timeout top=1_2_1_2_r133):
  `1/((d+ex)(c^2d^2-bcde+b^2e^2+3bce^2x+3c^2e^2x^2)^(1/3))`. Both cores put r133 at top (fired).
  - **Nested.** P0: `9_1_r16, 1_4_1_r34, 1_4_1_r30`. Substrate: `1_1_1_4_r47`.
  - **Arms.** r4 verified 3.3 s.
  — follows from: model flags [defect: none seen]
- class 1 g223 (1 entry, deterministic, final timeout top=1_2_1_2_r99): `1/((d+ex)sqrt(a+bx^2+cx^4))`.
  - **Substrate nested.** `1_1_2_3_r42`, `1_1_2_5_r20/r31`, `1_2_2_3_r78` (`%mr_negQ(c/a)`, symbolic),
    `1_1_2_1_r13`, `1_2_1_2_r99`. The top-level `1_2_2_8_r1` (P0's top) is absent at 30 s and 120 s.
  - **P0.** P0 also ran r78. All arms timeout.
  — follows from: not determined from the traces [defect: negQ]
- class 1 g224, g229, g234 (1 entry each, deterministic, final timeout top=1_2_1_3_r104 / 1_2_1_4_r30 /
  1_2_2_4_r5): `sqrt(f+gx)/((d+ex)sqrt(quad))`, `1/(sqrt(2+3x+5x^2)sqrt(3-x+2x^2))`,
  `x/((d+ex^2)(a+bx^2+cx^4))`.
  - **Both cores.** Same top rule, fired at 30 s. The substrate's nested chain differs: g224 elliptic
    (`1_1_2_3_r42`, `1_2_1_2_r93`, `1_2_1_3_r99`); g229 `1_1_2_3_r54`, `1_2_2_1_r18`, `1_2_1_3_r100`;
    g234 the log/atanh prefix.
  VERIFY-TIMEOUT; all arms timeout. — follows from: not determined which change moves the nested chain [defect: none seen]
- class 1 g226 (1 entry, deterministic, final timeout top=1_2_1_3_r42): `(b+2cx)(d+ex)^4/(quad)^(3/2)`.
  - **Substrate.** The top-level `1_2_1_3_r42` fired. Nested `1_2_1_9b_r5` (accepts p=-3/2 through
    `is(p > -2)`), `9b_r32`, `1_2_1_2_r117`, `9_1_r8`, `1_2_1_2_r15`, `1_2_1_1_r15`, `1_1_2_1_r13`.
  - **P0.** `1_2_1_6_r1` alone. VERIFY-TIMEOUT.
  — follows from: faithful binding exposing the IGtQ translation [defect: IGtQ]
- class 1 g227, g228 (1 entry each, deterministic, final timeout top=1_2_1_3_r45 / 1_2_1_3_r48; final120
  top 1_2_2_4_r9): `x^3(A+Bx^2)/sqrt(quartic)`, `(A+Bx^2)/(x^3 sqrt(quartic))`. As g83/g84.
  - **At 30 s.** Nested `1_1_2_1_r13, 1_2_1_1_r15` / `1_2_1_2_r99` and `r45/r48`, binding the
    substitution's x through `d_.` (OPT).
  - **At 120 s.** The top-level x^2 substitution has fired and the entries still time out.
  - **P0.** `1_2_2_6_r2`.
  — follows from: faithful Optional binding [defect: none seen]
- class 1 g230, g231 (1 entry each, deterministic, final timeout top=1_2_1_9_r12 / 1_2_1_9_r19):
  `x^2/((quad)^(k/2)(d-fx^2))`.
  - **Substrate.** The top-level 1.2.1.9 rule fired; nested `1_4_1_r18` (+`1_1_2_1_r13, 1_2_1_1_r15`).
  - **P0.** `1_4_2_r17` alone. VERIFY-TIMEOUT.
  — follows from: faithful binding [defect: none seen]
- class 1 g232 (1 entry, deterministic, final timeout top=1_2_2_1_r17): `1/(sqrt(quad)sqrt(quad))`.
  - **Substrate nested.** `1_1_2_3_r42` → `1_2_2_1_r17` (`%mr_negQ(c/a)` on coefficients built from r30's
    substitution; Rubi's reading of that composite is not determined, so not tagged). The top-level
    `1_2_1_4_r30` (P0's top) is absent.
  All arms timeout. — follows from: not determined from the traces [defect: none seen]
- class 1 g233 (1 entry, deterministic, final timeout top=1_2_2_2_r35): `(dx)^(5/2)/(a^2+2abx^2+b^2x^4)^3`.
  - **Substrate.** The top-level FracPart rewrite `1_2_2_2_r35` fired. Nested: `1_1_3_2_r17` (NE),
    `1_1_2_2_r27/r13`, `1_1_2_2_r7`. r7 is Rubi `ILtQ[Simplify[(m+1)/2+p+1],0]` and accepts a
    quarter-integer.
  - **P0.** `1_3_3_r10, 1_4_1_r34, 1_3_4_r9`.
  - **Collapse.** The double-root trinomial never reaches 9.1 (neither core fires `9_1_r27/r28`).
  - **Arms.** r4 verified 2.2 s.
  — follows from: model flags, with IGtQ and NE on the route [defect: IGtQ] [also: NE]
- class 1 g235 (1 entry, deterministic, final timeout top=1_2_2_6_r2): `(d+ex^2+fx^4)/(x(a+bx^2+cx^4))`.
  Both cores put r2 at top (fired).
  - **Nested.** Substrate: the log/atanh prefix + `1_2_1_2_r80`, `1_2_1_3_r89`, `1_2_1_9b_r32`. P0:
    `1_2_1_6_r1, 1_4_1_r19, 1_2_1_9_r16`.
  - **Arms.** r3 verified 2.0 s.
  — follows from: condition retry [defect: none seen]
- class 1 g236 (1 entry, deterministic, final timeout top=1_2_3_1_r7): `1/(sqrt(x)(a+bx^2+cx^4))`.
  - **Substrate nested.** The prefix, `1_2_2_3_r27` and `1_2_3_1_r7` (both `NegQ[b^2-4*a*c]`). The corpus
    has the `(-b-sqrt(b^2-4ac))^(1/4)` form. The top-level sqrt(x) substitution fire is absent.
  - **P0.** `1_4_1_r34`. All arms timeout.
  — follows from: not determined which change routes the substituted integrand; the NegQ reading [defect: negQ]
- class 1 g237 (1 entry, deterministic, final timeout top=1_2_3_2_r1): `x^(n-1)/(a+bx^n+cx^2n)`.
  - **Substrate.** The top-level x^n substitution fired → `1_2_1_1_r12` → `1_1_2_1_r13`: the corpus's
    3-step atanh form.
  - **P0.** The manual 9.1 rule. VERIFY-TIMEOUT; all arms timeout.
  — follows from: 9.1 regeneration; the cost is verification [defect: none seen]
- class 1 g238, g239, g240 (1 entry each, deterministic, final timeout top=1_2_3_2_r16 / r23 / r24):
  `x^9`, `x^5`, `x` over `(1-3x^4+x^8)`.
  - **Substrate.** The top-level rule fired → partial fractions (`1_2_3_4_r49` for g238) → PF-EVEN
    `1_1_3_2_r36` on n = 4 (numeric) + prefix.
  - **P0.** `1_3_3_r10`.
  - **Arms.** r3 deferred 0.4 s (g238, g239) and verified 0.3 s (g240).
  — follows from: faithful binding exposing the IGtQ translation (g240 also condition retry) [defect: IGtQ]
- class 1 g241 (1 entry, deterministic, final timeout top=1_4_1_r23): `1/((cx)^(2/3)(a+bx^2)^(2/3))`.
  - **Substrate.** Nested `1_1_3_1_r37, r53, 1_4_1_r23`. P0's top-level x^(1/3) substitution
    `1_4_1_r34` is absent at 30 s and 120 s.
  - **Arms.** r3 verified 0.2 s.
  — follows from: condition retry [defect: none seen]
- class 1 g244 (1 entry, deterministic, final timeout top=1_4_3_r19): `(d+ex+f sqrt(…))^n/(…)`. Both cores
  put r19 at top (fired).
  - **Nested.** P0: `1_1_2_7_r35`. Substrate: `1_1_2_2_r39` (hypergeometric; binding not inferable).
  VERIFY-TIMEOUT; all arms timeout. — follows from: not determined from the traces [defect: none seen]
- class 1 g245, g246 (1 entry each, deterministic, final unexpected top=1_1_2_5_r30 / 1_1_2_5_r31, self=1):
  `(a+bx^2)^(±3/2)/(sqrt(c+dx^2)sqrt(e+fx^2))`; noun-expected (Unintegrable, 0 steps).
  - **P0.** No-answer through the catch-all `1_1_2_5_r39`.
  - **Substrate.** `1_1_2_5_r30` / `r31` (Rubi `ILtQ[p,0] && GtQ[q,0]` / `LeQ[q,-1]`) accept p=-1/2
    through `is(p < 0)`. They reduce through `1_1_2_5_r32` and `1_1_2_3_r42` to an answer that
    differentiates back: unexpected.
  - **Arms.** r3 no-answer 0.2 s.
  — follows from: condition retry exposing the ILtQ translation [defect: IGtQ]
- class 1 g247 (1 entry, deterministic, final unverified top=1_1_1_2_r14):
  `(a+bx)^((-2bc+ad)/(bc-ad))(c+dx)^((bc-2ad)/(-bc+ad))`. Identical fire lists on both cores. All arms
  unverified, including r4. — follows from: not determined from the traces (answers not recorded) [defect: none seen]
- class 1 g248 (1 entry, deterministic, final unverified top=1_1_1_3_r65): `(bx)^m(%pi+dx)^n(%e+fx)^p`.
  - **Substrate.** `1_1_1_3_r65` (AppellF1; c = π, e = %e > 0): the corpus's own 1-step answer, not closed
    by the zero chain.
  - **P0.** `1_1_1_6_r7`. All arms unverified.
  — follows from: faithful binding [defect: none seen]
- class 1 g250, g251 (1 entry each, deterministic, final unverified top=1_1_2_7_r13 / 1_1_2_7_r15):
  `(a^2-b^2x^2)^(3/2)/(a+bx)^3`, `(d^2-e^2x^2)^(7/2)/(d+ex)^7`.
  - **Substrate.** Rubi's `1_1_2_7_r13/r15` bind; nested `1_1_3_2_r115, 1_1_2_2_r2`.
  - **P0.** `1_4_2_r21` alone.
  - **Arms.** r3 verified 0.4 / 0.5 s.
  — follows from: condition retry [defect: none seen]
- class 1 g252 (1 entry, deterministic, final unverified top=1_1_3_1_r22): `1/(1+a+(-1+a)x^4)`.
  - **Substrate.** The top-level `1_1_3_1_r22` (Rubi `IGtQ[(n-2)/4,0] && NegQ[a/b]`) accepts n = 4 ((4-2)/4
    = 1/2) with `NegQ[(1+a)/(a-1)]` read true for an unknown sign. Then the prefix chain.
  - **Corpus.** Rubi's n = 4 form `atan((1-a)^(1/4)x/(1+a)^(1/4))`.
  - **P0.** `1_2_2_1_r7` chain. All arms unverified.
  — follows from: faithful binding exposing IGtQ and NegQ [defect: IGtQ] [defect: negQ]
- class 1 g253 (1 entry, deterministic, final unverified top=1_1_3_2_r112): `(dx)^m/sqrt(a+b/(c/x)^(3/2))`.
  Both cores put r112 at top.
  - **Nested.** Substrate: `1_1_3_2_r107` (accepts p=-1/2 through `is(p < 0)` with symbolic a), `r84`,
    `r86`. P0 nfires=1.
  — follows from: faithful binding exposing the ILtQ translation [defect: IGtQ]
- class 1 g254 (1 entry, deterministic, final unverified top=1_1_3_2_r114): `x^3/(a+b(c+dx)^3)`. Both
  cores put r114 at top.
  - **Nested.** Substrate: the prefix, `1_1_3_1_r12`, `1_1_3_3_r17`, `1_1_3_7_r37` (n = 3, IGtQ[3/2,0]).
    P0 nfires=1.
  — follows from: faithful binding exposing the IGtQ translation [defect: IGtQ]
- class 1 g255, g258 (1 entry each, deterministic, final unverified top=1_1_3_2_r13 / 1_1_3_2_r6):
  `1/(x^4 sqrt(2+2a-2(1+a)+cx^4))`, `1/(x^3 sqrt(…))` (ZERO).
  - **g255.** `1_1_3_2_r13` accepts (m+1)/n+p+1 = -1/4 through `is(… < 0)`, with a the zero form
    (binding inferred).
  - **g258.** `1_1_3_2_r6`'s closed form divides by the zero form.
  - **P0.** `1_3_3_r17` / `1_2_2_6_r2`. All arms unverified.
  — follows from: binding change on the zero-form coefficient (g255 exposing the ILtQ translation) [defect: IGtQ]
- class 1 g256 (1 entry, deterministic, final unverified top=1_1_3_2_r35): `sqrt(x)/(1+x^3)`.
  - **Substrate.** `1_1_3_2_r35` accepts m = 1/2 at top level through `is(m > 0)` (Rubi `IGtQ[m,0]`): an
    integer-m partial-fraction formula applied to m = 1/2, unverified at 0.5 s. The x^(1/2) substitution
    rule does not fire.
  - **P0.** `1_3_4_r1` → `1_4_1_r34`. All arms unverified.
  — follows from: faithful binding exposing the IGtQ translation [defect: IGtQ]
- class 1 g257 (1 entry, deterministic, final unverified top=1_1_3_2_r5): `x^(-1-3n/2)/(a+bx^n)`.
  - **Substrate.** The top-level `1_1_3_2_r5` (Rubi `IntegerQ[p] && NegQ[n]`) accepts symbolic n through
    `%mr_negQ(n)`. Its rewrite `x^(m+np)(b+ax^-n)^p` is algebraically the integrand, so the seen guard
    hands it to Maxima integrate (rule-text inference). Unverified at 0.1 s.
  - **P0.** `1_1_3_2_r110`. All arms unverified. The same shape underlies seven new errors (below).
  — follows from: faithful binding exposing the NegQ reading [defect: negQ]
- class 1 g263 (1 entry, deterministic, final unverified top=1_1_3_7_r37): `(c+dx+ex^2)(a+bx^3)^p`.
  - **Substrate.** The top-level `1_1_3_7_r37` accepts n = 3 (IGtQ[3/2,0]); nested `1_4_1_r23`, `1_3_1_r11`.
  - **P0.** `1_3_4_r20`.
  — follows from: faithful binding exposing the IGtQ translation [defect: IGtQ]
- class 1 g264 (1 entry, deterministic, final unverified top=1_1_3_8_r17): `(e+fx)/(x sqrt(-1-x^3))`.
  - **Substrate.** The top-level r17 → nested `1_1_3_1_r31` (numeric a = -1, exact), `1_4_1_r23`,
    `1_1_3_2_r8`, `1_1_1_2_r32`, `1_1_2_1_r11`.
  - **P0.** `1_4_3_r42`.
  - **Arms.** r4 verified 1.0 s; r3 timeout.
  — follows from: model flags [defect: none seen]
- class 1 g265, g267 (1 entry each, deterministic, final unverified top=1_2_1_1_r17 / 1_2_1_2_r13):
  `1/(quad)^(7/3)`, `(d+ex)/(quad)^(7/3)`. Each has the same top rule on both cores.
  - **Nested.** P0: `1_3_4_r1` (+`1_2_1_1_r17`). Substrate: `1_1_3_2_r17` (NE), `1_1_3_2_r13`, `1_2_1_1_r17`.
  - **Arms.** r4 verified 0.3 s for g267; g265 unverified in all arms.
  — follows from: not determined (g265); model flags (g267) [defect: none seen] [also: NE]
- class 1 g266, g268 (1 entry each, deterministic, final unverified top=1_2_1_2_r107 / 1_2_1_2_r93):
  `sqrt(ade+…)/(d+ex)^(3/2)`, `1/(sqrt(d+ex)sqrt(ade+…))`.
  - **Substrate.** The elliptic chain (`1_1_2_3_r42/r48`, `1_2_1_2_r93`, `1_2_1_3_r89`).
  - **P0.** `1_1_1_3_r55` → `1_3_3_r6` / `1_2_1_4_r30`.
  - **Arms.** r4 verified 2.2 / 0.6 s.
  — follows from: model flags [defect: none seen]
- class 1 g269 (1 entry, deterministic, final unverified top=1_2_1_3_r104, 14.7 s):
  `sqrt(d+ex)/((f+gx)sqrt(ade+…))`. Both cores put r104 at top.
  - **Nested.** Substrate: `1_1_2_3_r42`, `1_2_1_2_r93`, `1_1_2_5_r20/r31`, `1_1_1_4_r29`, `1_2_1_3_r99`.
    P0: `1_4_2_r25, 1_1_1_4_r29, 1_2_1_4_r30`.
  - **Arms.** r3 CN 1.6 s.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g270 (1 entry, deterministic, final unverified top=1_2_1_3_r55): `x/((d+ex)(ade+…)^(3/2))`.
  - **Substrate.** `1_2_1_3_r55` binds x as f+gx with f=0 (OPT); nested `1_4_1_r18`.
  - **P0.** `1_2_1_9b_r5` alone. All arms unverified.
  — follows from: faithful Optional binding [defect: none seen]
- class 1 g271, g272, g273, g274 (1 entry each, deterministic, final unverified top=1_2_2_1_r17 / r18 /
  1_2_2_2_r16 / r34): `1/sqrt(a+bx^2+(2+2c-2(1+c))x^4)`, `1/sqrt(2+2a-2(1+a)+bx^2+cx^4)`,
  `x^4/sqrt(…)`, `x^2/sqrt(…)` (ZERO).
  - **Substrate.** Quartic rules bind the zero form as a or c (NegQ/Rt/IntPart of it), with nested
    `1_1_2_3_r42/r48`, `1_2_2_3_r60`, `1_1_2_5_r4`, `1_1_2_4_r55`.
  - **P0.** `1_2_1_1_r15` / `1_1_4_1_r9` / `1_4_2_r6` → `1_1_2_2_r33`, verified. The corpus answers
    treat the x^4 or constant term as absent.
  All arms unverified. — follows from: not determined which binding change (ZERO) [defect: none seen]
- class 1 g275 (1 entry, deterministic, final unverified top=1_2_2_2_r35): `(dx)^m(a+bx^2+cx^4)^p`.
  - **Substrate.** `1_2_2_2_r35` (FracPart rewrite) → `1_1_2_4_r66` (AppellF1): Rubi's 2-step answer, not
    closed.
  - **P0.** `1_4_2_r19` → `1_3_4_r9`. All arms unverified.
  — follows from: faithful binding (as g120) [defect: none seen]
- class 1 g276 (1 entry, deterministic, final unverified top=1_2_2_7_r7):
  `(√a+x^2√c)/((d+ex^2)sqrt(a+bx^2+cx^4))` (1-step corpus).
  - **Substrate.** `1_2_2_7_r7` (Pr split) → nested `1_4_1_r18`, `9_1_r8`.
  - **P0.** `1_2_2_7_r30` after a chain.
  - **Arms.** r3 CN 0.6 s.
  — follows from: not determined from the traces [defect: none seen]
- class 1 g277 (1 entry, deterministic, final unverified top=1_2_4_2_r9, 18.6 s): `x^(3/2)(ax+bx^3+cx^5)^(3/2)`.
  - **Substrate.** The top-level r9 fired; nested `1_2_4_4_r6/r10`, `1_3_3_r6` (binding not inferable),
    `1_4_1_r34`.
  - **P0.** `1_3_3_r15/r14` → `1_4_1_r34`.
  - **Arms.** r4 verified 17.3 s; r3 unverified 4.5 s.
  — follows from: model flags [defect: none seen]
- class 1 g278, g280 (1 entry each, deterministic, final unverified top=1_3_3_r7 / 1_4_3_r37):
  `(1+x)/((1+x-√3)sqrt(1+x^3))`, `(e+fx)/((2+x)sqrt(1-x^3))`.
  - **Substrate.** The nested `1_3_3_r7` (Rubi `ILtQ[q,0]`) accepts q=-1/2 on the shared factor. Also
    nested: `1_1_3_1_r30`, `1_2_1_2_r88`, `1_4_3_r42/r34`, `1_2_1_3_r30/r104` (g278) and `1_4_1_r18`
    (g280).
  - **P0.** `1_4_3_r42` / `1_4_3_r36`.
  - **Arms.** r3 verified 0.6 / 0.4 s.
  — follows from: condition retry exposing the ILtQ translation [defect: IGtQ]
- class 1 g281 (85 entries, slow-correct): P0 core verified in all 85 (0.9–25.6 s, median 2.5 s).
  - **30 s.** final30 times out in all 85; 75 have no fire flushed.
  - **120 s.** final120 verifies all 85 at 30.5–118.9 s (q1 46.5, median 55.5, q3 62.1 s). Histogram by
    10 s bins: 30s 8, 40s 20, 50s 32, 60s 6, 70s 6, 80s 5, 90s 3, 100s 2, 110s 3. The median
    final120/P0 wall ratio is 26×.
  - **100 s re-check.** Verified 82, timeout 3.
  - **Arms.** r3 verified 75 (4 deferred, 6 timeout); r2 timeout 85; r4 timeout 83, verified 2.
  - **Sample (23 entries).** The 10 whose r3 arm is not verified, plus every 7th entry. The final120 top
    equals P0's top in 53 of 85.
  - **Deviations.** Of those 10, e34/e4/e139/e158 read deferred under r3, i.e. a different, still-failing
    route. e853/e888/e892/e11/e44 run the log/atanh prefix and stay slow without retry; e1653 has no fire.
  — follows from: condition retry (cost; 75/85 verify in 0.2–7.9 s with it off) [defect: none seen]
- class 1 g282 (6 entries, noise): the record reads timeout at 30.0–30.1 s. final30 verifies at 25.9–29.4 s
  and final120 at 26.4–31.0 s; the 100 s re-check verifies at 24.9–30.7 s.
  - **P0.** 1.0–14.5 s.
  - **Routes.** e832–e835 run `9_1_r12, 1_4_1_r7, 1_1_1_3_r5, 1_2_1_3_r7` against P0's `1_4_1_r34`; e262
    runs `1_1_3_7_r39, 1_1_3_8_r13`; e7 has a longer 1.1.1.4 chain.
  - **Arms.** r2/r4 verify at 24.4–28.8 s. r3 verifies at 1.7–3.4 s (e7: contains-noun 0.5 s).
  — follows from: condition retry (cost puts the walls at the cap) [defect: none seen]
- class 1 g283 (1 entry, p0-noise): 1.2.1.5 e112.
  - **P0.** The P0 record verified at 29.6 s, at the cap; the probe's P0 core times out at 30.0 s with no
    fire.
  - **Final.** 30.0 / 120.1 s timeout (only `9_1_r8` fired); 100 s re-check timeout 100.1 s. All arms timeout.
  — follows from: P0-side timing noise (P0's own PASS was at the cap) [defect: none seen]

## NEW TIMEOUTS

- class 1 NEW TIMEOUTS (941; P0 verified 708, deferred 195, contains-noun 18, unverified 15, error 5):
  - **100 s re-check.** Timeout 756, verified 121, error 41, unverified 22, contains-noun 1.
  - **By P0 class.**
    - P0 verified 708: timeout 577, verified 88, error 33, unverified 10.
    - P0 deferred 195: timeout 161, verified 24, error 7, unverified 2, contains-noun 1.
    - P0 contains-noun 18: verified 9, timeout 8, error 1.
    - P0 unverified 15: unverified 10, timeout 5.
    - P0 error 5: timeout 5.
  - **Group members.** 708 of the 941 are PASS→FAIL group members: the deterministic groups 616 (100 s:
    timeout 573, error 33, unverified 10), g281 85 (verified 82, timeout 3), g282 6 (verified 6),
    g283 1 (timeout).
  - **Verified at 100 s.** None of the 121 comes from a deterministic group: 82 from g281, 6 from g282 and
    33 from non-PASS P0 entries. Walls 24.9–99.9 s, median 51.8 s.
  - **Errors at 100 s.** 29 of the 41 are 1.2.3.2 (walls 29.8–99.7 s, median 70.0 s), consistent with the
    g85/g86/g87/g155/g157 deaths at 120 s; the kind is not recorded.
  - **Sections.** 1.1.3.2 137, 1.2.1.2 103, 1.2.3.2 87, 1.2.1.3 80, 1.2.2.2 78, 1.2.1.4 64, 1.1.2.2 48,
    1.1.1.3 47, the rest ≤ 41.
  - **Arms over the 941.**
    - r2: timeout 926 (verified 11, error 3, unverified 1).
    - r3: timeout 637 (verified 173, deferred 67, unverified 45, contains-noun 14, error 5).
    - r4: timeout 854 (verified 64, unverified 18, error 5).
  - **Reading.** Condition retry accounts for about a third of the new class-1 timeouts (304 leave
    timeout under r3). The model flags account for 87, and the wide Flat reading for 15.

## New errors

60 entries (`…class1-newerror.out`, final core, 30 s, fire lists only). The probe keeps no error text, no
stderr and no heap/stack message. For every entry the error kind is **not determined**. What can be read
is the wall, whether the top-level fire printed (rubi returned), and the arms.

- **PF-EVEN on even n: 1.1.3.2, 20 entries.**
  - **Entries.** e1377, e1469, e1471–e1477, e1483, e1487, e1488, e1490, e1492, e1494, e1496, e1502,
    e1506, e1538, e1541, e1542: `x^k/(1±x^8)`, `1/(x^k(1±x^8))`, `1/(1±x^8)`, `1/(1-x^10)`,
    `x^5/(9±x^12)`, `x^(1/3)/(1-x^6)`.
  - **Fires.** The prefix `1_1_2_1_r13, 1_2_1_1_r12, 1_2_1_2_r3, 1_2_1_2_r9, 1_1_1_1_r3`, then
    `1_1_3_1_r13/r14` or `1_1_3_2_r35/r36` (+`r13`, `r63`) on n = 6, 8, 10, 12 (IGT; numeric
    coefficients).
  - **P0 record.** Verified 0.6–5.1 s (19), deferred 0.6 s (e1502).
  - **Final record.** Error 6.2–28.8 s. The probe reads timeout 30.2–30.3 s (15) or error 18.8–28.8 s (5).
  - **Where it died.** In 19 of 20 the top-level rule for the integrand as written (r13 / r14 / r35 /
    r36 / r63) is in the fire list, so rubi returned and the process died afterwards, presumably while
    verifying. In e1377 the top-level x^(1/3) substitution fire is missing.
  - **Arms.** Error in r2/r3/r4 for all 20.
  - **Group membership.** e1475/e1477/e1494 = g107, e1538 = g200, e1541 = g201, e1542 = g202; the rest
    are g6/g8/g18/g29/g49 members or non-PASS.
  - **NE.** Rubi's own route for these (the `1_1_3_2_r17` gcd substitution, k = 2 or 4) is blocked by the
    NE misreading.
- **NegQ on a symbolic exponent n: 10 entries.**
  - **1.1.3.2, 7 entries.** e2622, e2633, e2637, e2638, e2640, e2641, e2761: `x^(-1-kn)/(a+bx^n)^p`.
    - **Fires.** `1_1_3_2_r5` only (e2761 also `r90`), and it is the top-level rule, so rubi returned.
      r5's `%mr_negQ(n)` reads true for symbolic n (Rubi False). Its rewrite is algebraically the
      integrand, so the seen guard hands it to Maxima integrate (rule-text inference).
    - **Walls.** P0 record timeout 30.0 s (not a PASS). Final error 1.1–4.2 s; probe 2.2–11.2 s; error in
      every arm at the same walls.
  - **1.2.3.3, 3 entries.** e46, e51, e73 `1/((d+ex^n)^k(a(+bx^n)+cx^2n)^j)`.
    - **Fires.** `1_2_3_3_r4/r3` only (`%mr_negQ(n)`, same rewrite shape).
    - **Walls.** P0 deferred 3.5–3.6 s. Final error 4.7–5.0 s; probe 7.4–7.9 s; error in every arm.
- **Symbolic 1/((a+bx^4)(c+dx^4)^k): 1.1.3.3, 3 entries.** e66, e72, e73.
  - **Fires.** The top-level `1_1_3_3_r46` fired, with nested `1_1_3_5_r2` and PF-EVEN `1_1_3_1_r14`
    (n = 4, symbolic: IGT + NEGQ). Rubi returned.
  - **Walls.** P0 deferred 5.6–6.1 s. Final error 11.8–23.3 s; probe error 28.9 / timeout 30.1 ×2.
  - **Arms.** r2 error; r3 timeout (e66, e73) / error (e72); r4 error.
- **Quartic via the x^2 substitution: 23 entries.** 1.2.2.2 e850, e851; 1.2.3.2 e614, e616, e617, e619,
  e622, e624, e626, e631, e633, e635, e639, e641, e642, e644, e646, e647, e649, e650, e655, e657, e658:
  `x^3/(quartic)`, `x/(quartic)`, `(d+ex)^k/(a+b(d+ex)^2+c(d+ex)^4)^j`.
  - **Fires.** `1_2_2_2_r8/r1` (x^2 substitution) over `1_2_1_2_r3/r9/r13/r80/r84/r115`, `1_2_1_1_r12/r8`,
    `1_1_2_1_r13`, `1_2_1_3_r89/r55`: the log + atanh((b+2cx^2)/√(b²-4ac)) form of the corpus answers.
    e646 instead takes the `1_2_2_3_r27` NegQ branch (g86).
  - **P0 record.** Verified 0.6–1.1 s (18; P0 routes `1_4_2_r24`, `1_3_3_r4`, `1_2_1_6_r1` + `1_2_2_2_r8`),
    deferred 0.6–1.0 s (4), timeout (e851).
  - **Final record.** Error 7.6–28.5 s.
  - **Where it died.** In e850/e851 the top-level rule fired, so rubi returned. In the 21 (d+ex) entries
    the top-level linear-substitution fire is absent, so whether the process died inside rubi or after it
    (with unflushed output) is not determined.
  - **Arms.** Error in every arm except r3 timeout for e850 and e646.
- **1.2.3.4 e39, e40, 2 entries.** `(a+bx^3+cx^6)/(d+ex^3)^(3/2 or 5/2)`.
  - **Fires.** The top-level `1_2_3_3_r19` fired (rubi returned), with nested `1_1_3_1_r31` (`%mr_negQ(d)`
    symbolic: NEGQ), `1_4_1_r23`, `1_1_3_7_r40/r9`.
  - **Walls.** P0 deferred 0.9 s. Final error 16.7 / 19.9 s; probe 10.9 / 13.8 s.
  - **Arms.** r2 error; r3 verified 0.6 / 0.5 s; r4 verified 1.6 / 1.7 s. The death needs both condition
    retry and the model flags.
- **1.3.1 e193, e194, 2 entries (g143).** No fire at all (nfires=0). Error 8.7 / 9.2 s (probe), 9.1 / 9.7 s
  (record); P0 verified 0.5 / 0.9 s. Error in r2/r4; verified 0.4 / 1.5 s in r3. The process dies during
  matching or cond evaluation with condition retry on, before any rule answers.

## Collapse family

Scope check: in part C only g106 has `9_1_r27` or `9_1_r28` in its P0 or final fires. The newerror file
has none, and g281–g283 have none (the 9.1 fires there are `9_1_r8/r12`).

- class 1 g106 (3 entries, deterministic, final deferred top=9_1_r27) [collapse-family]: 1.2.1.2
  e1734–e1736 `(d+ex)^m/(a^2+2abx+b^2x^2)^k`, k = 1, 2, 3, noun-free expected answers
  `e^(2k-1)(d+ex)^(1+m) hypergeometric([2k,1+m],[2+m], b(d+ex)/(bd-ae))/…`.
  - **Same Rubi rule on both cores.** The 9.1 double-root trinomial collapse is P0 id `9_1_r28` and
    generated id `9_1_r27`. Its pattern `u_.*(a_+b_.*x+c_.*x^2)^p_.` binds a→a², b→2ab, c→b², p=-k, u =
    (d+ex)^m; the cond `%mr_eqQ(b^2-4*a*c,0) and integerp(p)` holds (P0 used `%mr_integerQ(p)`, same result).
  - **P0 route.** The repl was `rubi_hybrid_exact(u*%mr_cancel((b/2+c*x)^(2p)/c^p))`, which re-dispatches
    `(d+ex)^m/(a+bx)^(2k)`. Its seen test is the exact `member` only (`%mr_hybrid_body`, mode "exact"),
    and the factored form is not a member, so it dispatched. `1_1_1_2_r37` (the hypergeometric
    `(a+bx)^m(c+dx)^n` rule) answered: expected, 1.1–1.3 s, fires `1_1_1_2_r37, 9_1_r28`.
  - **Substrate route.** No class-1 rule ahead of 9.1 binds the expanded trinomial, so `9_1_r27` fires. Its
    repl is `mr_int(u*%mr_cancel((b/2+c*x)^(2p)/c^p))`, i.e. `(d+ex)^m (b(a+bx))^(-2k)/(b^2)^(-k) =
    (d+ex)^m/(a+bx)^(2k)`, ratsimp-identical to the top-level integrand already on `%mr_seen`.
  - **Where it stops.** `mr_top` → `%mr_seenp` finds `ratsimp(seen − f) = 0`, and the fb=true branch
    returns `integrate(f, x)`. The answer is a single top-level noun: nfires=1 (only `9_1_r27`), deferred,
    1.0–1.4 s.
  - **Arms.** r2 1.1–1.2 s, r3 0.7–0.8 s, r4 1.0 s: deferred in every arm, so no switch is involved.
  - **What blocks the collapse.** The seen guard's ratsimp comparison, not the depth cap: the fire list
    has one fire and the walls are about 1 s.
  - **Verdict.** This is the spec §3.5 case: "a PASS→FAIL in the collapse-rule family … brings back the
    exact comparison as a translation fix". Restoring the exact `member` seen test for the 9.1 collapse
    re-dispatches (P0's `rubi_hybrid_exact` behaviour) is the indicated fix. Task 4 Step 2 checked only
    1.2.1.3 e839. Together with class 2 g10 (e15), this is the second measured collapse regression.
    [defect: none seen]

## Evidence gaps (part C)

- **Answers are not recorded.** No `unverified` / `unexpected` group can say whether the answer is wrong or
  just not closed by the zero chain: g89–g92, g113–g120, g164–g171, g245–g280.
  - **With a named defect.** For IGT/MUL/ZERO groups the rule text shows a defect on the route, but the
    wrongness of the specific answer is still inference.
- **Error kinds.** The kind of every final `error` (g107, g143, g200–g202, the 60 new errors), the
  120 s errors (g85–g88, g109, g155, g157) and the 41 100 s re-check errors is not recorded (no stderr, no
  Lisp text). "Rubi returned" rests on the top-level fire being printed; "died while verifying" is an
  inference from that.
- **Timeout fire lists.** An absent top-level fire (g85–g87, g144, g145, g155–g157, g159, g162, g203,
  g204, g223, g232, g236, g241, most of g281) is weak evidence: the SIGKILL can drop unflushed output.
- **Bindings.** The PF-EVEN n, the IGT bindings of `1_1_2_2_r39` (g215, g261), `1_2_1_9b_r5` (g111, g150,
  g226), `1_1_3_2_r13` (g255) and `1_3_3_r7` (g278, g280) are inferred from the integrand and the
  preceding substitution. Probe 10 does not record bindings.
- **NegQ against Rubi.** Two kinds of assessment:
  - **By `PosAux`.** For symbols and their products and powers (a/b, c/a, n, a) the reading follows
    `PosAux` (IntegrationUtilityFunctions.m:608–634).
  - **By corpus shape.** For `b^2-4*a*c` (g85–g87, g155–g157, g159, g236) the tag rests on the corpus
    answer's real-root form: the canonical first term of the sum, which `PosAux` inspects, could not be
    determined without Mathematica.
  - **Untagged.** g232 (a composite from a substitution), and the `1_1_2_3_r42/r48` `NegQ[d/c]` uses in
    the elliptic chains (g82, g91, g117, g118, g150–g152, g223, g224, g266, g268, g269, g273, g274), were
    not assessed and are not tagged.
- **NE and MUL.** Both findings come from reading `nparse.lisp` and the rule text; neither was run. Which
  class-1 PASS→FAIL entries lose Rubi's gcd substitution (k ≥ 2) is not visible in the traces, since
  declines are not captured.
- **Not determined by group.**
  - Why the expansion / `mr_sum` / subst rule answers alone with no nested fire (g97, g103, g104, g132,
    g136, g137, g142, g187, g192–g197), the class 2 g1 shape.
  - Why reductions reach a CATCH-1 catch-all ahead of Rubi's own rules (g93, g94, g121–g128, g133, g138,
    g141, g185, g198).
  - Which change moves an unchanged top rule's nested chain (g153, g205, g224, g229, g234, g244).
  - Why e67 / g162 fires only `9_1_r8`.
  - g100's P0 binding of `1_1_4_4_r2`; g163's Rubi 0-step outcome; the ZERO group bindings (g184, g271–g274).
- **g281 sample.** 23 of 85 traces were read, and the final120 fire lists are not in the summary (only the
  final120 top). The mechanism rests on the r3 arm (75/85) and the top comparison (53/85 same top).

## Defect tally (part C)

203 group lines (g81–g280 deterministic, g281 slow-correct, g282 noise, g283 p0-noise).

- **By tag:**
  - `[defect: IGtQ]` only: 45 groups.
  - `[defect: negQ]` only: 15 groups.
  - Both: 21 groups.
  - `[defect: none seen]`: 122 groups (119 deterministic + g281, g282, g283).
  - Groups carrying IGtQ: 66; groups carrying negQ: 36.
- **IGtQ only:** g92, g98, g101, g105, g107, g111, g115, g130, g131, g135, g139, g140, g145, g146, g147,
  g150, g160, g168, g170, g171, g182, g186, g189, g191, g199, g200, g201, g202, g215, g226, g233, g238,
  g239, g240, g245, g246, g253, g254, g255, g256, g258, g261, g263, g278, g280. g258 carries the tag
  through its batched g255 line; its own binding (a division by the zero form) is not an IGT case.
- **negQ only:** g85, g86, g87, g95, g129, g155, g156, g157, g159, g165, g178, g179, g223, g236, g257.
- **Both:** g81, g108, g109, g110, g112, g144, g148, g204, g209, g211, g213, g214, g216, g217, g218, g219,
  g220, g252, g259, g260, g262.
- **Also noted:**
  - `[also: NE]` on 7 lines: g99, g113, g210, g212, g233, g265, g267.
  - `[also: MUL]` on 2 lines: g169, g279.
  - `[collapse-family]`: g106 only.
- **New errors (not group lines).** IGtQ in 20 + 3 entries (the PF-EVEN 1.1.3.2 set, 1.1.3.3 e66/e72/e73).
  NegQ in 10 + 3 + 2 + 1 entries: 1_1_3_2_r5 / 1_2_3_3_r3/r4 on symbolic n, 1.1.3.3 e66/e72/e73,
  1.2.3.4 e39/e40, and 1.2.3.2 e646.
