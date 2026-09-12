# Class-3 deferred campaign — measured uplift record

Phase-2 decision record for the class-3 deferred campaign (spec
`docs/superpowers/specs/2026-08-30-class3-deferred-campaign-design.md`;
plan `docs/superpowers/plans/2026-08-30-class3-deferred-campaign.md`,
Task 3). Every list below is data-bound to a committed probe output;
§1–§3 are the Phase-1/Phase-2 decision record, §4–§7 the campaign
close (Tasks 4–6: the landed fixes, the re-measurement A/Bs with every
PASS→FAIL attributed, the 788 recovery, the acceptance scorecard).

## Stamps

- Record dates: triage distribution merged 2026-08-31 11:23 UTC;
  fallback and split probes run 2026-09-01.
- Maxima: `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7,
  x86_64-pc-linux-gnu.
- **Two build stamps** — each measurement is quoted under its own:
  - §1 (the triage distribution and the 06 sweep-cost line): Maxima
    build **2026-08-29 17:58:20**.
  - §3.1 fallback measurements (probe 07) and §3.7 (probe 08): Maxima
    binary rebuilt **2026-08-31 13:27:47** — same branch hash, same
    SBCL; the rules core was NOT rebuilt (fingerprint unchanged).
- Rules core: `test/mr_rules.core` (3,513 rules, fingerprint
  `36b8bae7dba3c6e4fde614b6df70caa4`).
- Records: `test/corpus_class3.out` (1,033 deferred),
  `test/corpus_class3.baseline.out` (788 target-flagged).
- Probes (all under `probes/corpus/`, re-runnable):
  - 06 — the triage run (committed `.out`; 1,033/1,033; 24 shards
    merged; calibration 16/16 + 6/6 attribution proofs).
  - 07 — the sweep-cost fallbacks on the 37 swept entries (committed
    `.out`).
  - 08 — the verdict × target-flag split (committed `.out`).
- **Close (§4–§7)**: class-3 close record merged 2026-09-04 15:06 UTC;
  class-1/class-2 close records merged 2026-09-12; attribution probes
  09/10 run 2026-09-12 — all on build **2026-08-31 13:27:47**, rules
  core `5ef9b3bc5ee07ffac0e76f1fea54fbac` (3,514 rules). The full stamp
  is §7.

## 1. Triage distribution (measured)

Source: `probes/corpus/06-class3-deferred-mechanisms.out` (build
2026-08-29 17:58:20) — the committed record is the **re-measured
distribution** (commit 56102b9: the desync-buffered entry template
with the 120 s per-entry cap; 0 subprocess deaths). The first run
(2ef83f7, 60 s cap) died on 29 entries (reader desync — the measured
cause, commit 9e61da0); those deaths are the source of the 28
PENDING-REMEASURE entries of §3.6 (g1 1 + g2 4 + g3 23). The 29th
death (3.5 e11) was adjudicated directly from its trustworthy
re-measured label by the g4 wave (C-in-Rubi, M-implicit1). Label
semantics: `FIRE4` = the pass-4 sweep fired on a ported rule with a
non-noun, non-bool answer; `D-NEST` = a production rule fired but the
top-level answer is a noun (nested re-dispatch 0-fired);
`0FIRE-EXPL` / `0FIRE-POOL` = no rule fired, with / without a pass-4
DIAG factor pick.

### Label totals

| label        | total | verified | expected | unverified | no-answer | timeout | error |
|--------------|-------|----------|----------|------------|-----------|---------|-------|
| 0FIRE-POOL   |   691 |      186 |       15 |        335 |        88 |      48 |    19 |
| 0FIRE-EXPL   |   181 |       77 |        0 |         81 |         3 |      20 |     0 |
| D-NEST       |   144 |       45 |        1 |         35 |        55 |       8 |     0 |
| FIRE4        |    17 |        5 |        0 |          8 |         4 |       0 |     0 |
| **total**    | **1033** | **313** | **16** | **459** | **150** | **76** | **19** |

Target mass (788) = verified 313 + expected 16 + unverified 459;
certain mass (329) = verified 313 + expected 16.

### Label × file × target-flag cross-tab

The Phase-2 prioritization input (not recoverable from the two-way
projections above; quoted from the `.out`):

```
3.1.2 (9 deferred)
  no-answer  (  9): D-NEST=9
3.1.4 (230 deferred)
  verified   (128): 0FIRE-POOL=81  0FIRE-EXPL=47
  unverified ( 88): 0FIRE-POOL=84  0FIRE-EXPL=4
  no-answer  (  1): 0FIRE-EXPL=1
  timeout    ( 10): 0FIRE-POOL=10
  error      (  3): 0FIRE-POOL=3
3.1.5 (41 deferred)
  unverified ( 28): 0FIRE-POOL=14  0FIRE-EXPL=7  D-NEST=5  FIRE4=2
  no-answer  (  7): D-NEST=4  FIRE4=3
  timeout    (  6): 0FIRE-EXPL=3  0FIRE-POOL=3
3.2.1 (91 deferred)
  verified   ( 34): 0FIRE-POOL=19  D-NEST=10  FIRE4=5
  unverified ( 47): 0FIRE-EXPL=24  0FIRE-POOL=19  D-NEST=4
  no-answer  (  8): 0FIRE-POOL=6  D-NEST=2
  timeout    (  2): D-NEST=2
3.2.2 (138 deferred)
  verified   ( 61): 0FIRE-POOL=33  D-NEST=22  0FIRE-EXPL=6
  expected   (  5): 0FIRE-POOL=4  D-NEST=1
  unverified ( 65): 0FIRE-POOL=38  D-NEST=15  0FIRE-EXPL=12
  no-answer  (  7): 0FIRE-POOL=3  0FIRE-EXPL=2  D-NEST=2
3.2.3 (36 deferred)
  verified   (  7): D-NEST=7
  expected   (  1): 0FIRE-POOL=1
  unverified ( 14): 0FIRE-POOL=12  0FIRE-EXPL=2
  no-answer  (  6): 0FIRE-POOL=4  D-NEST=2
  timeout    (  2): 0FIRE-POOL=2
  error      (  6): 0FIRE-POOL=6
3.3 (160 deferred)
  verified   ( 17): 0FIRE-POOL=12  0FIRE-EXPL=5
  expected   (  1): 0FIRE-POOL=1
  unverified ( 92): 0FIRE-POOL=77  0FIRE-EXPL=7  D-NEST=7  FIRE4=1
  no-answer  ( 43): D-NEST=32  0FIRE-POOL=11
  timeout    (  5): 0FIRE-POOL=5
  error      (  2): 0FIRE-POOL=2
3.4 (235 deferred)
  verified   ( 39): 0FIRE-POOL=22  0FIRE-EXPL=13  D-NEST=4
  unverified ( 93): 0FIRE-POOL=76  0FIRE-EXPL=13  D-NEST=4
  no-answer  ( 53): 0FIRE-POOL=53
  timeout    ( 49): 0FIRE-POOL=26  0FIRE-EXPL=17  D-NEST=6
  error      (  1): 0FIRE-POOL=1
3.5 (93 deferred)
  verified   ( 27): 0FIRE-POOL=19  0FIRE-EXPL=6  D-NEST=2
  expected   (  9): 0FIRE-POOL=9
  unverified ( 32): 0FIRE-POOL=15  0FIRE-EXPL=12  FIRE4=5
  no-answer  ( 16): 0FIRE-POOL=11  D-NEST=4  FIRE4=1
  timeout    (  2): 0FIRE-POOL=2
  error      (  7): 0FIRE-POOL=7
```

### Sweep cost (swept entries only)

The 37 entries whose sweep does work (17 FIRE4 + 19 0FIRE-POOL +
1 D-NEST; swept field ∈ {4, 6} = 2 directions × 2–3 bare factors):

```
n=37  mean= 13.06  p50=  8.90  p95= 46.50  max= 58.60
```

This line **includes** the triage drill (the 333-pattern clause drill +
conds) on the 0-firing entries — a triage-only artifact that has no
production pass-4 counterpart. §3.1 re-measures under production
semantics (probe 07).

### 788/329 recompute

313 + 16 + 459 = 788 (target); 313 + 16 = 329 (certain). Re-asserted
per-entry by probe 08 (§3.7).

## 2. Adjudication (per wave)

Verdicts per the campaign taxonomy: **A** (pass-4 sweep rescue; the
fired rule is a faithful port of its `.m` rule), **B-port** (the port
deviates from the `.m` — dropped/mistranslated clause, spurious
declaration → Task-4 fix list), **C-in-Rubi** (the `.m` covers the
shape; the ported rule exists but 0-binds → Task-4 re-transcription
list), **C-absent** (no `.m` rule in the pinned commit covers the
shape), **D** (documented set; B-faithful folds into D),
**PENDING-REMEASURE** (subprocess death in the committed record —
evidence-so-far only). The 2026-08-31 boundary policy (the
reclassification) is what splits the draft's D/B-port buckets into
B-port vs C-in-Rubi; per-wave details below.

`.m` citations are to the pinned Rubi tree (`reference/rubi/…`, pinned
commit recorded in `todo/TODO.md`); `e<n>` = n-th corpus entry,
`L<ln>` = suite source line.

### Wave 1 (g1) — 3_1_2 (9), 3_1_4 (230), 3_1_5 (41): 280 entries

| family  | A | B-port | C-in-Rubi | C-absent | D  | PENDING | total |
|---------|---|--------|-----------|----------|----|---------|-------|
| 3_1_2   | 0 | 0      | 3         | 0        | 6  | 0       | 9     |
| 3_1_4   | 0 | 2      | 194       | 0        | 34 | 0       | 230   |
| 3_1_5   | 4 | 0      | 15        | 0        | 21 | 1       | 41    |
| **tot** | **4** | **2** | **212** | **0** | **61** | **1** | **280** |

**A (4)** — all four are 3.1.5; every fired rule is a faithful port:

| entry | fired (dir, i) | sweep (first run) | `.m` cover |
|-------|----------------|-------------------|------------|
| e5 L18 | `3_3_r44` (0,2) | 11.8 s | 3.3 log-product family |
| e91 L116 | `3_5_r43` (1,2) | 30.0 s | 3.5.m L43 (dual-log IBP) |
| e209 L258 | `3_1_5_r56` (0,2) | 20.6 s | 3.1.5.m polylog rows |
| e215 L264 | `3_1_5_r56` (0,2) | 34.2 s | as above |

**C-in-Rubi (212):**

- **M1 ×209** — slotted inner exponent: the faithful 1:1 LHS
  (`x_^r_.` in a binomial base) 0-binds under the installed Maxima
  matcher even against a literal target exponent (decisive probe K1:
  symbolic r, `r2@x^5*(d+e*x^r)^2*(a+b log) [false]`; control Q4: the
  same family's literal-`x^2` LHS binds). The `.m` matcher binds it.
  Covers (all present and binding in `.m`): 3.1.4.m r2/L5
  (`x^m (d+e x^r)^q (a+b log)`, `IGtQ[q,0]&&IGtQ[m,0]`), r3/L6
  (`IntegerQ[m]`, m < 0), r19/L25, r23/L29
  (`IntegerQ[2q]&&(IntegerQ[m]&&IntegerQ[r]||IGtQ[q,0])`), r24/L30
  (`IntegerQ[q]&&(GtQ[q,0]||IntegerQ[m]&&IntegerQ[r])`); cross-family
  3.1.3.m r3/L6 (`EqQ[r(q+1)+1,0]`, TRUE for r = −1/(q+1)); 3.1.5.m
  L50/L51 (the dual-log answering rows). Split: 0FIRE-EXPL 3.1.4 ×52 +
  3.1.5 ×3; 0FIRE-POOL 3.1.4 ×142 + 3.1.5 ×12.
- **M6 ×3** — `(d*x)^m` head 0-bind (e65/e66 L82/83, e67 L84, 3.1.2
  D-NEST): a free-coefficient monomial head `(d*x)^m` (and nested
  `(d*x^q)^m`) + trailing `Power[Plus, p-slot]` is a deterministic
  0-bind, even for a unit-coefficient `x^m` head, and never matches a
  numeric-coefficient monomial (probe matrix b30–b32). In `.m` the head
  binds and m10/L13 (the unconditional Subst rule of 3.1.2.m) answers
  in 2 steps (the suite's step count). Port: `rules/class3/3_1_2.mac`
  r10 (`:181-200`) — table-first, but dead on the head.

**B-port (2)** — **M4**: e275 L352 (`x*log(x)*sqrt(4+x^2)`),
e317 L396 (`x*log(x)/sqrt(-1+x^2)`) — the `.m` cover is 3.5.m **L40
(#37)** `Int[v_*Log[u_], x] := With[{w = IntHide[v, x]}, …] /;
InverseFunctionFreeQ[u, x]` (the generic IBP rule; covers both rows in
`.m`: u = x, InverseFunctionFreeQ true; w inverse-function-free for
both v's). The ported r37_u (`rules/class3/3_5.mac:737-751`) carries
the spurious `matchdeclare(_mr_3_5_r37_u, freeof(x))$` (:737; no `.m`
counterpart — L40's guard is only `InverseFunctionFreeQ[u,x]`) and
0-binds the u = x rows. (Retraction on record: the draft's "gap — no
generic `u*Log[v]` IBP" attribution was a slot-name-specific grep miss
(`Int[u_*Log` vs the L40 spelling `Int[v_*Log[u_]]`); the drill
`3_5_r38 [T0F1]` is the faithful decline of the twin r38 = 3.5.m L41
(#38) `ProductQ[u]` row, not the cover.)

**D (61)** — M2 ×28 (bare-binomial factor: the `.m` cover 3.1.4.m
r19/L25 has the binomial as `Power[Plus, q-slot]`; the target factor is
bare (power 1 stripped) — faithful 0-bind in **both** systems, so
documented, not fixable), M5 ×4 (e194–e197, headvar e := 0
monomial-argument corner — documented strict decline, not a bug; cover
3.1.5.m L62 r58), `.m` coverage gap ×18 (catch-all only: [16] r6/L9
guard undecidable → m27/L33 `Unintegrable`; [51] 3.1.3.m L18–L20
undecidable → L24; [71] `.m` linearity is top-level-`Plus`-only, no
`(a+b Log)/Q` LHS exists; [82] L45/L46 guards undecidable → L47;
[89]/[90]/[91] monomial log-argument `c*(d x^m)^n` — no rule, grep 0
hits → m30/L34; [2]/[3] 3.1.2 log-power shapes — answering rule
unidentified), D-NEST faithful-outer ×9 (the fired rule IS a faithful
`.m` cover; the nested sub-integral 0-fires — the sub-shapes are
themselves M1/M4-class on the Task-4 lists, so these rows are
expected to resolve at the Phase-3 re-measurement), faithful reject ×1
(e191 — m10/L13 and m11/L14 both carry `FreeQ[m,x]` and reject m =
−1+n in `.m` too), unresolved open note ×1 (e180 — drill
`3_3_r54 [T15,U1,F0]`, no ALLTRUE, CONDE = 2).

**PENDING (1)** — e47 (3.1.5 L64): §3.6.

**Anomalies carried in g1:** the 3-arg `%mr_algebraicFunctionQ` arity
crashes (3_1_5_r30 measured; 3_3_r32, 3_3_r61 in the campaign CONDE
counts) — faithful 3-arg `.m` utility calls vs arity-2 Maxima
utilities; the crash misfires the rule (errcatch `[]`), it never
mis-covers; 3_1_4 r2's added `%mr_neQ(r,0)` is a harmless generator
artifact; the M3 (Quotient-storage-blocks-product-patterns) claim was
RETRACTED (b29: the matcher tolerates Quotient storage — the production
rule object fired on a Quotient-stored target).

### Wave 2 (g2) — 3_2_1 (91), 3_2_2 (138), 3_2_3 (36): 265 entries

| family  | A | B-port | C-in-Rubi | C-absent | D  | PENDING | total |
|---------|---|--------|-----------|----------|----|---------|-------|
| 3_2_1   | 5 | 28     | 31        | 12       | 15 | 0       | 91    |
| 3_2_2   | 0 | 19     | 79        | 2        | 38 | 0       | 138   |
| 3_2_3   | 0 | 0      | 2         | 3        | 27 | 4       | 36    |
| **tot** | **5** | **47** | **112** | **17** | **80** | **4** | **265** |

**A (5)** — e122, e150, e204, e265, e296 (all 3.2.1): fired
`_mr_rule_3_2_1_r14` (3.2.1.m L18) during the run, first-run fire
(0,2) per the 06 record (re-confirmed by the 07 full sweep); suite
closed form matches.

**B-port (47)** — **D1**: the ported `%mr_linearQ`
(`maxima_rubi_utils.mac:2157-2159`) dropped the list arm that `.m`'s
`LinearQ[{u,v}]` has — every `.m` rule guarded by the list form is
0-guarded in Maxima (probe: `%mr_linearQ([a+b*x,c+d*x],x) → [false]`,
scalar → `[true]`). Cover: 3.2.2.m L19 r15 clause 7
`LinearQ[{u,v}]` — 3_2_1 ×28 (e156–e158, e164–e166, e303, e304,
e309, e310 + the 0FIRE-POOL companions) and 3_2_2 ×19 (the M2
r14-cluster and r24-cluster rows). Rules carrying a
`Not[LinearMatchQ[…]]` clause (3_2_1 r5/r6/r23/r24, 3_2_2 r13/r14) are
NOT covers — that clause is a faithful reject for literal-linear
u/v/w. Fix: restore the list arm in
`generator/generate_rules.py` / `generator/translation_table.py`.

**C-in-Rubi (112):**

- **D2 ×99** — ratio log-arg pattern 0-binds: the stored suite
  ratio log-arg `e*(a+b*x)/(c+d*x)` is held as
  `Quotient[Times[e,Plus],Plus]` (e inside the quotient numerator);
  the ported ratio pattern is `Times[e,Power[Quotient,n]]` (e outside)
  → structural mismatch (probe pA). In `.m` there is no Quotient node
  (division = negative power), so the `.m` rules bind. Covers:
  3.2.1.m L19 r15 / L21 r17 / L23 r19 (×18); 3.2.2.m L6 r3
  (ratio-parallel Subst, ×77) + L8 r5 (×2, e214/e220); 3.2.3.m L8 r5
  (e104) / L10 r6 (e107) (×2). Fix: normalise the ratio log-arg to
  product-of-powers form in the generator, or a matcher pre-pass.
- **D3/D4 ×13** — 3_2_1 r16/r18/r20 pattern 0-binds on all numeric-n
  entries (probes pC/pD/pE; isolated explicit-linear log-arg patterns
  all 0-bind bare); the `.m` covers' conds ARE satisfiable under the
  natural binding (e124: `bf−ag ≡ 0, m = −2, p = 1` → `GtQ[p,0]`
  true). Covers: r16 (3.2.1.m L20) ×3 (e124/e131/e274), r18 (L22) ×9
  (e210–e218), r20 (L24) ×1 (e268). Fix: r16/r18/r20 pattern emission.

**C-absent (17)** — no `.m` rule in the pinned tree covers the shape
(the suite closed forms are the Rubi→Mathematica `Integrate` fallback):
3_2_1 ×12 (the Ei log-in-denominator-of-linear-power group — whole-tree
`Ei[` search: Ei-producing rules only in 2.1 L7, 2.3 L20/L51, 8.3 ×15,
8.9 ×3, all taking exponential/Ei input); 3_2_2 ×2 (e243/e247, same
search); 3_2_3 ×3 (e89 — r19 faithfully rejected, no other cover;
e102 — bare polylog over two linears; e106 — log²-ratio over two
linears, r13/r14 faithfully rejected by Not[LMQ]).

**D (80)** — 3_2_1 ×15 (e249: `.m`'s own 3.2.1 r21 `Unintegrable` fires
in `.m` rule order — suite closed form = fallback; + M3
`3_5_r13 [t,t,t]` shadow rows); 3_2_2 ×38 (M3 ×26 + 0FIRE-EXPL shadow
×12); 3_2_3 ×27 (r18-faithful ×7 — `3_2_3_r18 [11t]` all true; M3 ×5;
cross-family ×2; individual POOL ×3; M3 `3_5_r1 + 3_5_r38` ×10).

**PENDING (4)** — 3_2_3 e82(L113)/e83(L114)/e84(L115)/e87(L118):
subprocess died during the shard run (empty drill line).

**Anomalies carried in g2:** ported 3_2_3 r18 drops one clause
(11 vs the `.m`'s 12 — `NeQ[bc−ad,0]` missing; over-permissive);
`prod_fire` can point at a rule that fired on a nested sub-integral
(e243/e247); r14's swapped first binding on e124 (n = −2, mn = 2,
a↔c, b↔d).

### Wave 3 (g3) — 3_3 (160), 3_4 (235): 395 entries

| family | A | B-port | C-in-Rubi | C-absent | D  | PENDING | total |
|--------|---|--------|-----------|----------|----|---------|-------|
| 3_3    | 1 | 125    | 0         | 0        | 16 | 18      | 160   |
| 3_4    | 0 | 82     | 128       | 20       | 0  | 5       | 235   |
| **tot**| **1** | **207** | **128** | **20** | **16** | **23** | **395** |

Source note: the committed first-run record contains exactly 23 g3
`subprocess-died` MECH lines (18 in 3_3, 5 in 3_4); those entries are
PENDING-REMEASURE, not counted in A/B/C/D.

**A (1)** — e360 L505 (3.3): `x*log(f*x^m)*(a+b*log(c*(d+e*x)^n))` —
production fired `_mr_rule_3_3_r38` (first-run fire (1,1)); suite
closed form matches.

**B-port (207):**

- **3_3 ×125** (108 0FIRE-POOL + 12 0FIRE-EXPL + 5 reclassified D-NEST
  e88/e89/e90/e156/e402): misses of `.m` covers that are present in the
  ported table — port/matcher/storage 0-binds, not missing rules.
  Mechanisms (probe27, production rule environment): (1) Quotient
  storage 0-binds (`.m` cover 3.3.m L14 r11 0-binds in the port,
  numerator pattern alone binds; later `3_3_r29` fires and leaves a
  nested noun — the true cover was skipped); (2) uncombined
  fractional-power products (cover 3.3.m L13 r10 — `(f+g*x)^(1/2)`
  BINDS but the full product pattern NO BINDs); (3) bare-log /
  omitted-zero factor (the ported product pattern does not bind the
  stored bare `log(…)` factor; e402 falls to `3_3_r56` →
  `unintegrable`); (4) slotted inner exponents / fractional linear
  covers (3.3.m L50 r46-class; the same matcher-strictness class as
  g1's M1 — the decided split keeps the 3_3 bucket whole in B-port for
  fix-list placement; the Task-4 fix work is the same generator
  normalisation/re-transcription, so the Phase-3 expectation is
  identical either way).
- **3_4 spurious-freeof ×81** (70-row `3_5_r1 [true] 3_5_r38 [true]`
  POOL cluster + 13 r37-cover rows + e619, minus the 3 PENDING): the
  port adds a `freeof(x, u)` headvar constraint the `.m` rules do not
  have — sites `rules/class3/3_5.mac:737`
  (`matchdeclare(_mr_3_5_r37_u, freeof(x))$`) and
  `rules/class3/3_5.mac:26` (`matchdeclare(_mr_3_5_r2_u, freeof(x))$`);
  MA source 3.5.m L5 r2 (`FreeQ[{a,b},x] && InverseFunctionFreeQ[u,x]`)
  and L40 r37 (`InverseFunctionFreeQ[u,x]`) — neither has
  `FreeQ[u,x]`.
- **3_4 storage ×1** — e392 (`log((a+x^n)/x^n)/x`): the stored quotient
  form binds 3_5.r1 but `%mr_derivativeDivides` returns false, while
  the Plus form `log(1+a*x^-n)/x` fires 3_5.r1 and returns the polylog
  answer — a storage/normalization gap (port-side normalisation fix).

**C-in-Rubi (128)** — the **3_4 matcher-gap** cluster (pre-PENDING 129 −
e618): slotted inner exponents — `sqrt(x)`, `x^(1/3)`, `x^(2/3)`,
`1/sqrt(x)`, `1/x^(1/3)`, `1/x^(2/3)`, and the `/x^k` denominator
forms. The `.m` covers are present (3.4.m L12/L16/L33 and the 3.3
cross covers) but the ported patterns 0-bind on the stored Maxima
forms — matcher/re-transcription gap, same class as g1's M1.

**C-absent (20)** — 3_4 `0FIRE-POOL` rows for which the 3.4/3.5 `.m`
audit found no answering rule: the 14-row empty-signature POOL cluster
(e123–e128 L160–165, e535 L682, e547–e549 L696–698, e559 L712,
e585–e587 L742–744) + six individual POOL rows from the same audit
(row-level map in the wave worktable).

**D (16)** — all 3_3: e234 (r30/r31 both BIND cond `[true]`; the
nested sub-integral 0-fires — D-NEST); e283–e286, e293–e295
(`log(c+d*x)/(x^k*(a+b*x^3|x^4))` — production fired
`_mr_rule_3_2_3_r16`, nested 0-fire); e329/e330/e347/e348, e332/e350
(production fired `_mr_rule_3_2_3_r18`, nested 0-fire); e371/e372
(pass-1 r41 0-binds but production fired `_mr_rule_3_3_r41` on a
later pass; the suite `steps = −1` closed forms are the fallback
artifact).

**PENDING (23)** — 18 × 3_3 (all `subprocess-died`; evidence-so-far
D-NEST-shaped on `3_2_3_r16`) + 5 × 3_4 (e100 D-shaped — the `3_5_r8`
sign-prompt EOF crash chain; e292/e343/e354 B-port-shaped —
spurious-freeof; e618 C-in-Rubi-shaped — matcher-gap).

**Retractions carried in g3:** "3_3 missing r58 headvar" is false
(`rules/class3/3_3.mac:1351-1370`, table `:1435`); "3_4 missing r37
headvar" is false (`rules/class3/3_4.mac:870-881`, table `:931`);
`%mr_neQ` is MA-faithful (`maxima_rubi_utils.mac:538`) — the e88–e90
r11 blocker is a matcher 0-bind (quotient storage), not a guard
failure.

### Wave 4 (g4) — 3_5 (93): 93 entries

| family | A | B-port | C-in-Rubi | C-absent | D  | total |
|--------|---|--------|-----------|----------|----|-------|
| 3_5    | 0 | 41     | 31        | 4        | 17 | 93    |

No g4 entry is A. All six FIRE4 rows are adjudicated by their `.m`
cover, not by the sweep label (the A definition requires the production
miss to be a pattern 0-bind of a faithful fired rule): e49/e103 →
C-in-Rubi (the fired rule's production 0-bind is a matcher gap; the
sweep's non-noun answer is the native-`integrate` fallback, not the
suite form); e154/e157/e195/e198 → B-port (the true `.m` cover is r37/
L40; the port 0-binds on the spurious `freeof(x)`; the sweep fired
r43, whose shadow answer is the native `integrate`
gamma_incomplete form, not the suite Si/Ci form — measured on the e154
per-entry re-run).

**B-port (41)** — one mechanism, three rule sites. The port adds
`matchdeclare(…, freeof(x))` for the `u` slot of three 3.5 rules whose
`.m` original constrains the slot only in the cond
(`InverseFunctionFreeQ[u, x]`, which the port does evaluate faithfully
in the cond). `freeof(x)` is strictly stronger: it rejects every
x-dependent candidate at the pattern level, so the rule 0-binds before
the cond can run (the G battery measured the asymmetry: the pattern
binds with an x-independent u and 0-binds with an x-dependent u, for
r31/r35/r37).

| site | rule | `.m` | entries |
|------|------|------|---------|
| `rules/class3/3_5.mac:640` | r31_u | 3.5.m L34 (#31) `Int[Log[u_], x] := … /; InverseFunctionFreeQ[u, x]` | 10 — e116, e126, e193, e207, e211, e234, e294, e295, e297, e298 |
| `rules/class3/3_5.mac:706` | r35_u | 3.5.m L38 (#35) `Int[Log[u_]/Qx_] := … /; QuadraticQ[Qx, x] && InverseFunctionFreeQ[u, x]` | 5 — e94, e95, e276, e278, e279 |
| `rules/class3/3_5.mac:737` | r37_u | 3.5.m L40 (#37) `Int[v_*Log[u_], x] := With[{w = IntHide[v, x]}, …] /; InverseFunctionFreeQ[u, x]` | 26 — e113–e115, e154–e159, e179, e182, e184, e188–e192, e194–e200, e284, e285 |

**C-in-Rubi (31)** — grouped by the nine mechanism keys:

| key | n | entries | `.m` cover | mechanism |
|-----|---|---------|------------|-----------|
| M-implicit1 | 3 | e11, e49, e139 | L25 (#22), L8 (#5), L44 (#41) | stored factor has no power node (exponent 1 stripped at read time); the `.m` slot is a power; MA absorbs the identity, the Maxima matcher cannot |
| M-plus-identity | 2 | e56, e58 | L7 (#4) `(a_. + b_ Log[c Log[d x^n]^p])/x` | bare `Log[…]` numerator needs the Plus zero-identity `a := 0`; measured to fire in power-base position but NOT in numerator-sum position (P1/P1b; the generator's `drop_optionals` assumes the matcher fills it) |
| M-barelog-optional | 1 | e266 | L16 (#13) `RFx_*(a_. + b_.*Log[u_]) /; RationalFunctionQ[RFx, x]` | bare `Log[u]` into the sum slot (a = 0, b = 1); the matcher cannot express the MA Optional-blank absorption |
| M-cas-simp | 2 | e92, e93 | L13 (#10) `Log[c Px^n]/Qx /; QuadraticQ[{Qx,Px},x] && EqQ[D[Px/Qx,x],0]` | CAS auto-simplification divergence: MA auto-factors the bound denominator (derivative 0); Maxima keeps the binding as stored (nonzero derivative); `%mr_eqQ` is faithful |
| M-factored-quad | 3 | e103, e106, e107 | L21 (#18) `(g x)^m Log[d+e x+f √(a+b x+c x²)] /; EqQ[e²−cf²,0] && NeQ[m,−1] && IntegerQ[2m]` | √-argument stored factored (Times) vs the Plus slot; MA auto-expands `x(x−1)`, Maxima keeps the factorization |
| M-functionoflog | 12 | e134–e136, e140, e143, e149–e152, e225, e258, e261 | L46 — the FunctionOfLog catch-all, **active in `.m`, unported** (43 ported rules = L4–L44 + L47–L48) | `Int[u_, x] := With[{lst = FunctionOfLog[Cancel[x*u], x]}, …] /; Not[FalseQ[lst]] /; NonsumQ[u]`; the r43 drill decline on these rows is faithful (`IntegerQ[p]` false for fractional p) and is not the cover |
| M-class4 | 5 | e180, e181, e183, e186, e187 | 4 Trig/4.7.5 Inert trig functions.m L10/L11 | covered by class 4 (unported) — not rescuable by Task 4B/4C until class 4 is in scope; `.m`-covered, hence not C-absent |
| M-multistep | 1 | e98 | no single-rule cover — the suite's 28-step complex-factor derivation (3.2.3 complex-linear-factor path) | port r1 binds but its body declines faithfully |
| M-323 | 2 | e243, e244 | 3.2.3.m L6 (#4) `(g_.+h_. x_)^m_ Log[e f (a+bx)^p (c+dx)^q)^r] /; NeQ[bc−ad,0] && NeQ[m,−1]` | the Plus base `(g+h x)` cannot bind the bare atom `x` (Plus zero-identity absent); e244's first cover is 3.2.3 #4, not 3.5 r34 (which would also fire in MA but is second in rule order) |

**C-absent (4)** — e19 (`(a*m*x^m+b*n*q*log(c*x^n)^(-1+q))/x` — the
residual derivative form of the L25 derivation; no `.m` rule carries
the `a := 0 ∧ b := 0` double identity), e34 (same class, L18-family),
e272 (log of a ratio of quadratics over `x²`; the quadratics do not
factor over the rationals), e300 (`(log(x)^m)^p` — pure log-power;
FunctionOfLog CANNOT cover it: the leading `x` outside the log fails
`FunctionOfLog`).

**D (17)** — D-NEST ×6 (e13/e251/e252/e253 — the r43 fold rule rewrites
to a quotient-log form no ported rule reaches; e301/e302 — cross-family
`3_1_5_r34` fires, nested 0-fire) + faithful decline / documented gap
×11 (e40–e45 — r1/L4 binds, the body gate `%mr_derivativeDivides` is
false: the quotient is genuinely x-dependent, measured pole at x = 2;
the suite's 1-step `polylog(2, 1−F)` answer is reference-CAS-derived;
e238/e273 — r20's `QuadraticQ` degree-1 decline, false in BOTH
systems; e259 — r13's `RationalFunctionQ[RFx, x]` false — the RFx
contains `log`; e280/e281 — r1 body gate false on the stored form).

**Build facts measured in g4 (affecting how the probes read):**
defmatch auto-declaration is inactive in this build (an undeclared
trailing-underscore variable matches as a LITERAL symbol — ad-hoc probe
patterns must declare their slots; the port's own rules are unaffected,
the generator emits explicit `matchdeclare` for every slot); Quotient
tolerance is path-dependent (`(g*x)^m` binds `1/x` with m = −1 only in
the two-factor pattern context, 0-binds standalone); pass 4 is not
wired into production (`mr_top` runs passes 1–3 then the
integrate-fallback gate; `%mr_pass4_scan` is defined but never called);
Maxima does not auto-factor/auto-cancel stored bindings.

### Grand totals (machine-checked)

| wave | A | B-port | C-in-Rubi | C-absent | D   | PENDING | total |
|------|---|--------|-----------|----------|-----|---------|-------|
| g1   | 4 | 2      | 212       | 0        | 61  | 1       | 280   |
| g2   | 5 | 47     | 112       | 17       | 80  | 4       | 265   |
| g3   | 1 | 207    | 128       | 20       | 16  | 23      | 395   |
| g4   | 0 | 41     | 31        | 4        | 17  | 0       | 93    |
| **tot** | **10** | **297** | **483** | **41** | **174** | **28** | **1033** |

Machine-checked 2026-08-31 across the four wave files; the claim
totals are re-asserted against the enumerated entry sets by probe 08
(§3.7). The 17 FIRE4 lines reconcile: A 10 (g1 4 + g2 5 + g3 1) +
g4 non-A 6 + e47 (g1 PENDING, first-run FIRE4, A-shaped — §3.6).

## 3. Phase-2 decisions

### 3.1 A verdict: NO-GO — pass-4 production is not wired

Gate (plan Task 3 Step 3): pass-4 production ships IFF the FIRE4 mass
covers ≥ 1 target-mass (788-flagged) entry AND the measured sweep cost
clears **p95 added ≤ 3 s AND mean added ≤ 1 s** (the class-3 wall
stays ~≤ 1.5×).

- **Mass clause: PASSES.** FIRE4 = 17 entries, of which 13 are
  target-mass (5 verified + 8 unverified; the 4 no-answer entries are
  non-target).
- **Cost clause: FAILS on all three measured statements** (the swept
  37 entries; added = dt_total − record `t=`; the harness runs all
  scans with no early stop, so these are strict upper bounds on the
  production cost, which stops at the first fire):

| statement | n | mean (s) | p50 (s) | p95 (s) | max (s) | build stamp | drill |
|-----------|---|----------|---------|---------|---------|-------------|-------|
| 06 committed line | 37 | 13.06 | 8.90 | 46.50 | 58.60 | 2026-08-29 | inclusive |
| 07 full sweep (both directions, production semantics) | 37 | 8.78 | 5.41 | 34.69 | 37.34 | 2026-08-31 | free |
| 07 forward-only d=0 + k=3 (fallback b) | 37 | 3.51 | 1.97 | 15.25 | 20.01 | 2026-08-31 | free |

Gate: p95 ≤ 3 s AND mean ≤ 1 s. The 06 line fails 13.1× on mean /
15.5× on p95; the 07 full line 8.8× / 11.6×; the 07 forward-only line
3.5× / 5.1×. (Individual `added` values include a couple of small
negatives — machine noise on the dt subtraction; they are kept as
measured.)

- **Fallback (a) — the k = 3 factor bound — is a DERIVED no-op on this
  population, not a new measurement.** 06's swept field counts the
  scans run (2 directions × nbare bare factors); the committed record
  has max swept = 6 on all 37 swept entries ⇒ nbare ≤ 3 on every swept
  entry ⇒ "the first 3 factors in stored order" drops no scan for any
  entry ⇒ the k = 3 scan set is identical to the full-sweep scan set.
  Its cost IS the measured full-sweep cost (the 07 full row above).
- **Fallback (b) — forward-only + k = 3 — reduces to forward-only**
  (k = 3 drops nothing here): measured by 07 — mean 3.51 s, p95
  15.25 s; fails the gate on both clauses.
- **Rescue delta over the 17 first-run FIRE4 entries** (rescue = a
  sweep fire with a non-noun, non-bool answer op; the harness runs all
  scans, so an early noun fire does not preclude a later rescuing
  fire): the full sweep re-confirms **17/17** (cross-check against the
  committed record); forward-only rescues **15/17** — the sacrifices
  are e91 (3.1.5, first-run fire (1,2)) and e360 (3.3, first-run fire
  (1,1)), both reverse-direction-only fires. e47's first-run fire (0,2)
  is forward-direction: the forward-only sweep also rescues it
  (fires (0,1,integrate; 0,2,"+")), so the e47 100 s re-measure is
  meaningful under either wiring.
- **Disposition (the rule that fired on the numbers):** the mass
  clause passes but the cost clause fails on every measured variant,
  so **pass-4 production is NOT wired** (NO-GO). The 10 confirmed
  A-class entries (+ e47, A-shaped, PENDING) are documented as
  **prototype-only rescues**: the sweep mechanism (Task 1) is correct
  and the fires are real, but the added cost does not clear the
  plan's gate on this corpus. The prototype seam (`%mr_p4_once`,
  `maxima_rubi_utils.mac:285`) remains available for a future,
  cheaper-wiring decision; nothing here pre-wires it.
- **e47 (3.1.5 L64)** — in the first committed distribution
  (2ef83f7, 60 s cap) its subprocess died at the cap (label
  untrustworthy); in the committed HEAD distribution (56102b9,
  120 s cap) it re-measures as **FIRE4 t=66.9 s,
  `fire=0,2,_mr_rule_3_1_5_r48`** — A-shaped (a faithful ported rule
  fired; the sweep rescued). The adjudication keeps it in
  PENDING-REMEASURE (the verdict is owed; its baseline flag is
  no-answer, not target mass). The 100 s re-check (Task 5, the
  standing timeout re-check discipline) gates the final A count:
  **10 vs 11**.

### 3.2 B list (297) — the Task 4B fix inputs

Fix sites (entries ride on the sites; per-entry enumeration in §2 and
the wave files):

| # | site | defect (vs `.m`) | `.m` citation | entries |
|---|------|------------------|---------------|---------|
| B1 | `rules/class3/3_5.mac:26` (r2_u), `:640` (r31_u), `:690` (r34_u), `:706` (r35_u), `:737` (r37_u), `:769` (r39_v), `:786` (r40_v) — the seven spurious-`freeof` sites | spurious `matchdeclare(…, freeof(x))` on the slot the `.m` constrains only in the cond; the fix is to declare the slot `true` (the conds already carry the faithful `InverseFunctionFreeQ` checks) | 3.5.m L5 (r2), L34 (#31), L37 (#34), L38 (#35), L40 (#37), L42 (#39), L43 (#40) | 124 campaign entries: g1 2 (e275/e317, on r37_u) + g3 81 (spurious-freeof, on the r37_u/r2_u sites) + g4 41 (r31_u 10, r35_u 5, r37_u 26). r34_u/r39_v/r40_v carry 0 campaign entries but are fixed at the same time (the declaration is wrong regardless) |
| B2 | `maxima_rubi_utils.mac:2157-2159` (`%mr_linearQ`) + `generator/generate_rules.py` / `generator/translation_table.py` | the list arm of `.m`'s `LinearQ[{u,v}]` was dropped — list-form guards 0-guard in Maxima | 3.2.2.m L19 r15 clause 7 | 47 (g2 D1: 3_2_1 28 + 3_2_2 19) |
| B3 | `rules/class3/3_3.mac` (the 3_3 cover set) + generator normalisation | 3_3 misses: Quotient storage, uncombined fractional-power products, bare-log/omitted-zero factor, slotted inner exponents (the mechanism-4 subset is the same class as the C-in-Rubi matcher gaps — the fix work is the same generator normalisation) | 3.3.m L13 (r10), L14 (r11), L50 (r46-class) + the 3.3/3.5 cross covers | 125 (g3 3_3) |
| B4 | `rules/class3/3_5.mac` r1 path (storage normalisation) | the stored quotient form 0-binds the `%mr_derivativeDivides` path where the Plus form answers — port-side normalisation | 3.5.m L4 (r1) | 1 (g3 e392) |

124 + 47 + 125 + 1 = 297 ✓.

**Related open follow-up (not a campaign entry, recorded for Task 4A's
NO-GO record):** the 3-arg `%mr_algebraicFunctionQ(…, x, true)` calls
at `rules/class3/3_1_5.mac:679` (r30), `rules/class3/3_3.mac:732`
(r32), `rules/class3/3_3.mac:1422` (r61) against the 2-arg shim
(`maxima_rubi_utils.mac:3174`) — arity crash swallowed by the dispatch
errcatch (utils:152); the `.m` third argument is a flag
(`AlgebraicFunctionQ[u, x, flag_]`, IntegrationUtilityFunctions.m:
1680-1681) — the fix is arity + flag semantics, not a call-site edit.
And the `%mr_quadraticMatchQ` one-term-missing-quadratic divergence
(utils:2395-2411; e103 is the concrete case — the port's r20 fires and
loops to the depth guard where MA declines) — either extend the port's
QMatch to the missing-term corners or note the divergence as accepted
strictness.

And the **0^negative expt-warning rule set** (the Task-1 open-minor
item (f), attributed in the ledger to pass-3's lifted rescan):
`1_1_2_1_r33`, `1_1_3_1_r66`–`r70`, `1_1_3_4_r80`–`r81`, `2_3_r62`,
`2_3_r97`–`r98`, `3_4_r38`–`r39`. **Triage decision (recorded per the
open-minor item): OUT of this campaign's scope** — the adjudication
found no deferred entry whose verdict depends on this rule set (it
appears in no B-port / C-in-Rubi / C-absent list), so the item's
"unless the adjudication says otherwise" condition is not met; a
follow-up rule fix belongs to a class-1/2 campaign with its own A/B
against the class-1/class-2 records. Same category as the 3-arg
`%mr_algebraicFunctionQ` sites above.

### 3.3 C-in-Rubi list (483) — the Task 4C re-transcription inputs

| # | cluster | n | `.m` covers | target ported file | fix mechanism |
|---|---------|---|-------------|--------------------|---------------|
| C1 | g1 M1 — slotted inner exponent | 209 | 3.1.4.m r2/L5, r3/L6, r19/L25, r23/L29, r24/L30; 3.1.3.m r3/L6; 3.1.5.m L50/L51 | `rules/class3/3_1_4.mac`, `3_1_3.mac`, `3_1_5.mac` | pattern re-transcription (the faithful 1:1 LHS 0-binds under the installed matcher) |
| C2 | g1 M6 — `(d*x)^m` head | 3 | 3.1.2.m m10/L13 | `rules/class3/3_1_2.mac` (r10 `:181-200`) | pattern re-transcription (the head never matches) |
| C3 | g2 D2 — ratio log-arg | 99 | 3.2.1.m L19 (r15), L21 (r17), L23 (r19); 3.2.2.m L6 (r3), L8 (r5); 3.2.3.m L8 (r5), L10 (r6) | `rules/class3/3_2_1.mac`, `3_2_2.mac`, `3_2_3.mac` | normalise the stored `Quotient[Times[e,Plus],Plus]` ratio log-arg to product-of-powers form in the generator, or a matcher pre-pass |
| C4 | g2 D3/D4 — r16/r18/r20 | 13 | 3.2.1.m L20 (r16), L22 (r18), L24 (r20) | `rules/class3/3_2_1.mac` | pattern emission for the explicit-linear-power product log-arg |
| C5 | g3 3_4 matcher-gap | 128 | 3.4.m L12/L16/L33 + the 3.3 cross covers | `rules/class3/3_4.mac` (+ 3_3 cross) | same class as C1 (slotted inner exponents); e618 is PENDING |
| C6 | g4 — the nine mechanism groups | 31 | 3.5.m L7 (#4), L8 (#5), L13 (#10), L16 (#13), L21 (#18), L25 (#22), L44 (#41), L46 (catch-all — unported); 3.2.3.m L6 (#4); 4.7.5.m L10/L11 | `rules/class3/3_5.mac`, `3_2_3.mac` | re-transcription per mechanism (M-implicit1, M-plus-identity, M-barelog-optional, M-cas-simp, M-factored-quad, M-323) + **port the L46 FunctionOfLog catch-all** (M-functionoflog ×12); the 5 M-class4 rows are blocked on class 4 (unported) |

209 + 3 + 99 + 13 + 128 + 31 = 483 ✓.

### 3.4 C-absent list (41) — record only

No `.m` rule in the pinned commit covers the shape; the suite closed
forms are the Rubi→Mathematica `Integrate` fallback (upstream gap
recorded):

- **g2 ×17** — the Ei log-in-denominator group (3_2_1 ×12: e112,
  e113, e117, e118, e194, e195, e199, e200, e222, e223, e227, e228;
  3_2_2 ×2: e243, e247 — searched: all 11 `.m` files under
  `3 Logarithms` + whole-tree `Ei[` grep) + 3_2_3 ×3 (e89, e102, e106).
- **g3 ×20** — the 3_4 `.m` coverage audit: 14-row empty-signature
  POOL cluster (e123–e128, e535, e547–e549, e559, e585–e587) + 6
  individual POOL rows.
- **g4 ×4** — e19, e34 (residual derivative forms), e272 (log of a
  ratio of quadratics over `x²`), e300 (pure log-power —
  FunctionOfLog cannot cover it).

### 3.5 D set (174) — the documentation set (no code)

- **g1 ×61** — M2 ×28 (faithful 0-bind in both systems), M5 ×4
  (documented strictness), `.m` gap ×18 (catch-all only; suite answers
  reference-CAS-derived), D-NEST faithful-outer ×9 (nested sub-shapes
  are on the Task-4 lists — expected to resolve at Phase 3), faithful
  reject ×1, open note ×1.
- **g2 ×80** — the M3 `3_5_r13 [t,t,t]` families: 3_2_1 (M3 direct ×3
  + 0FIRE-EXPL shadow ×11), 3_2_2 (×26 + shadow ×12), 3_2_3 (×5 + the
  `3_5_r1 + 3_5_r38` variant ×10); e249 (`.m`'s own 3.2.1 r21
  `Unintegrable` fires in `.m` rule order — suite closed form =
  fallback); r18-faithful ×7; cross-family ×2; individual POOL ×3.
  (14 + 38 + 15 + 1 + 7 + 2 + 3 = 80 ✓)
- **g3 ×16** — all 3_3 D-NEST (nested 0-fires under faithful/real
  fired rules; e371/e372's suite closed forms are the fallback
  artifact).
- **g4 ×17** — D-NEST ×6 (the r43 fold rewrites to an unreachable
  quotient-log form; the cross-family `3_1_5_r34` nested 0-fires) +
  faithful decline ×11 (the body-gate declines measured faithful; the
  e40–e45 suite answers are reference-CAS-derived, algebraically
  unreachable under L4's condition).

### 3.6 PENDING (28) — the re-measurement bucket

Not counted in A/B/C/D; a re-run is required before a verdict:

- **g1 ×1** — e47 (3.1.5 L64): A-shaped (HEAD record: FIRE4 t=66.9 s,
  `fire=0,2,_mr_rule_3_1_5_r48`; first record: subprocess death at the
  60 s cap); baseline flag no-answer; the 100 s re-check gates the
  final A count of 10 vs 11 (§3.1).
- **g2 ×4** — 3_2_3 e82/e83/e84/e87 (subprocess deaths; empty drill
  lines).
- **g3 ×23** — 18 × 3_3 (subprocess deaths; evidence-so-far
  D-NEST-shaped on `3_2_3_r16`) + 5 × 3_4 (e100 D-shaped;
  e292/e343/e354 B-port-shaped; e618 C-in-Rubi-shaped).

### 3.7 Verdict × target-flag split (probe 08)

Method: the decision record's enumerated entry sets (the §2 cluster
membership, transcribed from the four wave files) joined per-entry to
`test/corpus_class3.baseline.out`. PARTIAL classes enumerate only the
entries the wave files list explicitly (the wave file carries the
cluster count + ellipsis) and are not asserted complete; the
enumerated portions are disjoint and every enumerated key is in the
deferred population (08 asserts all of this). Run on the 2026-08-31
binary; the join is against the committed records (build-stamp-neutral
flags).

| class | wave | enum/claim | status | verified | expected | unverified | target (of 788) | certain (of 329) |
|-------|------|-----------|--------|----------|----------|------------|----------------|------------------|
| A | g1 | 4/4 | complete | 0 | 0 | 2 | 2 | 0 |
| B-port | g1 | 2/2 | complete | 2 | 0 | 0 | 2 | 2 |
| C-in-Rubi | g1 | 120/212 | PARTIAL | 75 | 0 | 34 | 109 | 75 |
| D | g1 | 39/61 | PARTIAL | 7 | 0 | 20 | 27 | 7 |
| PENDING | g1 | 1/1 | complete | 0 | 0 | 0 | 0 | 0 |
| A | g2 | 5/5 | complete | 5 | 0 | 0 | 5 | 5 |
| B-port | g2 | 47/47 | complete | 8 | 2 | 30 | 40 | 10 |
| C-absent | g2 | 17/17 | complete | 0 | 1 | 4 | 5 | 1 |
| C-in-Rubi | g2 | 112/112 | complete | 62 | 2 | 47 | 111 | 64 |
| D | g2 | 80/80 | complete | 27 | 1 | 45 | 73 | 28 |
| PENDING | g2 | 4/4 | complete | 0 | 0 | 0 | 0 | 0 |
| A | g3 | 1/1 | complete | 0 | 0 | 1 | 1 | 0 |
| B-port | g3 | 1/207 | PARTIAL | 0 | 0 | 1 | 1 | 0 |
| C-absent | g3 | 14/20 | PARTIAL | 0 | 0 | 12 | 12 | 0 |
| C-in-Rubi | g3 | 0/128 | PARTIAL | 0 | 0 | 0 | 0 | 0 |
| D | g3 | 16/16 | complete | 0 | 0 | 6 | 6 | 0 |
| PENDING | g3 | 23/23 | complete | 0 | 0 | 0 | 0 | 0 |
| B-port | g4 | 41/41 | complete | 14 | 0 | 23 | 37 | 14 |
| C-absent | g4 | 4/4 | complete | 3 | 0 | 1 | 4 | 3 |
| C-in-Rubi | g4 | 31/31 | complete | 5 | 9 | 8 | 22 | 14 |
| D | g4 | 17/17 | complete | 5 | 0 | 0 | 5 | 5 |

Enumerated totals (579 of 1,033): target 462, certain 228. The 06
record's total row (313/16/459/150/76/19) is re-asserted by the probe
(313 + 16 + 459 = 788; 313 + 16 = 329).

Reading for Task 5 prioritisation: of the enumerated B/C mass, the
certain-flag share is heaviest in C-in-Rubi (153/228 enumerated
certain entries) — the re-transcription list is where the verified
recovery concentrates; the B-port fixes carry 26 enumerated certain
entries (plus the g3 3_3 mass, not enumerated row-by-row here).

## 4. Phase-2 fixes (Task 4)

Source: the per-sub-brief ledger entries in `.superpowers/sdd/progress.md`
(section `## Plan: 2026-08-30 class-3 deferred campaign`, Task 4 — each
entry records the main-session re-run of the Layer A gate, the
regeneration byte-identity check and the core fingerprint it names)
and, for C6b, the sub-brief report's gates (re-measured at this close:
§7). Dispatch order B1 → B2 → B4 → C2 → C1 → C4 → C3 → B3 → C5 → C6 →
C6b; every cycle rebuilt the rules core. The Layer A column is the
suite count after the sub-brief (all `0 failed`); the fingerprint is
the rules core built from that commit's tree (re-built from each
commit at this close for the §5 attribution matrix — every rebuilt
fingerprint equals the ledger's; probe 09).

| brief | commit(s) | what landed | rule-file / utils delta | Layer A | core |
|-------|-----------|-------------|-------------------------|---------|------|
| 4A | — | **skipped**: pass-4 production NO-GO (§3.1); no wiring, the `%mr_p4_once` seam stays unbaked; the 10 A entries (+ e47) stand as prototype-only rescues | none | 743 | `00e05dca` (campaign base 1d998cc) |
| B1 | `464d29f` + `2838c3a` | the generator's `freeq_guarded` regex scoped (negative lookbehind + `[^\]}]` argument class): the spurious `freeof(x)` slot declarations removed. `2838c3a` is the B1 test follow-up (the non-noun discriminant gains the `string(op)` disjunct for the listcons `unintegrable` noun; test-only) | 9 decl-only lines `freeof(x)` → `true`: `3_5` r2/r31/r34/r35/r37/r39/r40 + `1_1_1_7` r5 + `1_4_1` r18 (conds untouched) | 750 | `3fb9ba05` |
| B2 | `d6cee4e` | `%mr_linearQ` list arm restored (the `.m` `LinearQ[{u,v}]` ListQ arm, IntegrationUtilityFunctions.m:1373-1376) | utils only (shared by all classes) | 758 | `f486a7c1` |
| B4 | `3c04b2e` | `%mr_derivativeDivides` stored-quotient gap: `y : expand(y)` at the y binding (the `.m` EasyDQ strip sees Times, Maxima stored `/`) | utils only (1 line) | 763 | `7bce44cb` |
| C2 | `52ffb6f` | 3.1.2.m m10/L13 `(d*x)^m` head re-transcribed to `d*x^m` with `d` declared `is(u = 1)` (generator `dhead10_spec`) | `3_1_2` r10: 2 lines (decl + pattern) | 780 | `1ffbdc10` |
| C1 | `2fd677a` + `5fd0dce` | the M1 slotted-inner-exponent 0-bind: 14 rules re-transcribed with the whole binomial-power factor as one `m1b` slot (`%mr_mbp_isfac` / `%mr_mbp_unwrap` / `%mr_mbp_base`; generator `m1_spec`); `.m` conds/repls byte-identical. `5fd0dce`: AGENTS.md — the Layer A gate becomes TLS-flag-mandatory | `3_1_3` r1/r2/r3/r18, `3_1_4` r2/r3/r4/r23/r24, `3_1_5` r5/r21/r22/r46/r47 + utils helpers | 798 | `6d86a287` |
| C4 | `d2ae62d` | 3.2.1.m L20/L22/L24 (r16/r18/r20): defmatch replaced by the fail-closed structural matcher `%mr_logpow_match` (13 captures, `.m` natural orientation); conds/repls byte-identical | `3_2_1` r16/r18/r20 pattern lines + utils +273 | 815 | `20e3be6f` |
| C3 | `1c8a306` | the ratio log-arg stored-`Quotient` 0-bind: six rules read by `%mr_logratio_match` / `%mr_logratio_sq_match` (the 99/99 census shapes S1–S4); conds/repls byte-identical | `3_2_1` r15/r17/r19, `3_2_2` r3/r5, `3_2_3` r5/r6 + utils +425 | 835 | `a02da1f0` |
| B3 | `9533528` | 3_3 cover 0-binds, 3 of 4 mechanisms via the C1 `m1b` idiom: M1 quotient r11 (L14); M2 fractional-power products r2/r10/r12/r13; M4 slotted inner exponents r20/r21/r25/r26/r27. **Stopped** (entries stay deferred): M3 bare-log r46 (L50, two structured log factors), r24 (reciprocal-linear base), r28 (the `(h x)^m` head mis-bind) | `3_3` 10 rules | 851 | `128c4bf8` |
| C5 | `4702d4d` | 3_4 slotted-inner-exponent: r8/r12 slot the whole outer log-power factor (`_mly`, `%mr_lpfac`); r4/r5/r6 the `m1b` idiom; `%mr_mbp_mono2` guard lifted `or` → `and` (signed-exponent monomials — widens `%mr_mbp_isfac` to reciprocal-linear binomials for every `m1b` rule) | `3_4` r4/r5/r6/r8/r12 + utils +189 | 862 | `d2a9e03a` |
| C6 | `c25e8f6` + `69b3de1` | **1 of the 6 re-transcription groups**: M-cas-simp — 3_5 r10 cond `ratsimp` 0-bind fix (e92/e93); the two entries did not transition (root-caused in the ledger: `%mr_simp` log-branch rewrite on e92, the second nested integral's cost on e93). `69b3de1`: AGENTS.md count line | `3_5` r10 cond | 869 | `f882e9ae` |
| C6b | `99e1eb1` | M-functionoflog: the unported 3.5.m **L46 FunctionOfLog catch-all** ported as `3_5` r42 (old r42/r43 → r43/r44); 5 utility ports (`%mr_nonsumQ`, `%mr_logQ`, `%mr_functionOfLog` + aux/walk); the generator's bare catch-all emission fix (a single-slot pattern is emitted as a `:=` function — the re-defmatch atomic-pattern collapse), which re-emits the three pre-existing bare catch-alls `1_4_1` r7/r8 and `2_3` r96 | `3_5` (new rule, count 44), `1_4_1` r7/r8, `2_3` r96 + utils | 892 | `5ef9b3bc` (3,514 rules) |

**Not landed — out of campaign scope, superseded by the matcher
substrate.** The five remaining C6 mechanism groups were probed to their
0-bind points during C6 (ledger C6 entry) and are **not** ported:
M-implicit1 (e11, e49; e139 moved to C6b), M-plus-identity (e56, e58),
M-barelog-optional (e266), M-factored-quad (e103, e106, e107), M-323
(e243, e244). Every one is a Maxima-`defmatch` expressibility gap
(Optional/identity absorption, factored-argument binding, the Plus
zero-identity on a bare atom) — exactly the class the matcher substrate
replaces. User decision 2026-09-11: close the campaign at its current
state (spec `docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`
§0.1, on the `matcher-spike` branch). Their measured end state is in §6.
Recorded-only groups (no fix was planned): M-class4 (5 entries — covers
in the unported class 4) and M-multistep (e98 — no single-rule cover).
The other in-brief stops (B3 M3/r24/r28; C1's shadowed `3_1_5` r4; C4's
`3_2_1` r22 dead 0-binder) are likewise superseded.

## 5. Phase-3 re-measurement (Task 5)

### 5.1 The records

| class | pre-campaign record (`.campaign-baseline.out`) | campaign-close record (`test/corpus_class<n>.out`) |
|---|---|---|
| 3 | merged 2026-08-30 00:18 UTC, build 2026-08-29 17:58:20, core `00e05dca` — `Results: 1736 passed, 1349 failed` | merged 2026-09-04 15:06 UTC (24 shards, 3,085/3,085), build 2026-08-31 13:27:47, core `5ef9b3bc` — `Results: 2058 passed, 1027 failed` |
| 1 | merged 2026-08-28 18:32 UTC, build 2026-08-20 21:36:22 (`5.50.0`), core 3,180 rules (`aa53741f`, f8d2fde) — `Results: 20069 passed, 5628 failed` | merged 2026-09-12 09:22 UTC (24 shards, 25,697/25,697), build 2026-08-31 13:27:47, core `5ef9b3bc` — `Results: 20125 passed, 5572 failed` |
| 2 | merged 2026-08-28 18:45 UTC, build 2026-08-20 21:36:22, core `aa53741f` — `Results: 594 passed, 371 failed` | merged 2026-09-12 09:36 UTC (merge `OK: 965/965 entries, 3 files, no dupes/missing/extra`, rc=0), build 2026-08-31 13:27:47, core `5ef9b3bc` — `Results: 614 passed, 351 failed` |

The class-3 close record is the 2026-09-04 run on the final campaign
tree (the rules core has not changed since: §7). The class-1 and class-2
close runs were measured 2026-09-12 on the same tree and core (the
matcher-substrate plan's P0 runs, which double as this gate). Note the
**build confound**: every pre-campaign record was measured on an older
Maxima build (class 3: 2026-08-29; classes 1–2: 2026-08-20) — the
attribution below separates build/noise from rule changes by re-running
each PASS→FAIL entry on the old rules under the current build.

### 5.2 A/B tables (`python3 test/ab_records.py <campaign-baseline> <close record>`)

Class 3 (key set: 0 missing, 0 extra):

```
PASS->PASS   1605
PASS->FAIL    131
FAIL->PASS    453
FAIL->FAIL    896
```

Class 1 (key set: 0 missing, 0 extra):

```
PASS->PASS  20059
PASS->FAIL     10
FAIL->PASS     66
FAIL->FAIL   5562
```

Class 2 (key set: 0 missing, 0 extra):

```
PASS->PASS    593
PASS->FAIL      1
FAIL->PASS     21
FAIL->FAIL    350
```

The class-1/class-2 expected shape (spec §4 criterion 2: FAIL→PASS
only) does **not** hold: 10 + 1 PASS→FAIL, each attributed below
(§5.4). Class-3 FAIL→PASS: 442 of the 453 come from the deferred
population (probe 10 §1).

### 5.3 Attribution method (probe 09)

`probes/corpus/09-deferred-close-passfail-attribution.py` runs one entry
through the driver's exact per-entry text (`build_text`: same zero
chain, same classification, 30 s cap) on a named rules core, prepending
`rubi_verbose : true` so the pass-1 fired-rule sequence comes from the
same run, and (noun-expected entries only) appending the self-diff zero
chain after the CLASS line so an `unexpected` answer's correctness is
measured. All runs on build 2026-08-31 13:27:47, 2026-09-12. Cores, each
built with `test/build_rules_core.sh` from `git archive <commit>` (every
rebuilt fingerprint equals the ledger's):

- **base**: `1d998cc` (campaign base; `00e05dca`, the class-3
  pre-campaign record's rules — no core-file change between the record's
  commit f40d56b and 1d998cc) and, for classes 1–2, **`f8d2fde`**
  (`aa53741f`, the class-1/2 pre-campaign records' rules);
- **final**: the close core `5ef9b3bc` (99e1eb1, C6b);
- **per commit**: `464d29f` B1, `d6cee4e` B2, `3c04b2e` B4, `52ffb6f`
  C2, `2fd677a` C1, `d2ae62d` C4, `1c8a306` C3, `9533528` B3, `4702d4d`
  C5, `c25e8f6` C6.

Decision rule per entry: **PASS on the base core and FAIL on the final
core under the same build ⇒ a campaign rule change** (deterministic —
located by the per-commit cores: the full matrix for classes 1–2
(`.matrix.run`), a binary search over the ordered cores for class 3
(`.bisect.py`)); **PASS on the final core ⇒ run-to-run noise in the
close record** (a near-cap timeout or a verification-stage variance);
**FAIL on base and final ⇒ not a campaign change** (build or noise —
then a 120 s cap run decides slow-correct vs genuine). A class-3 entry
located by the bisection is **near-cap / indeterminate** rather than
deterministic when (a) the close core's 120 s cap run returns a PASS
class within the standard 30 s, or (b) its pass-1 fire trace is
identical on the base and close cores and its base run is itself
≥ 20 s: the close core's own runs straddle the cap (or no route
changed), so the single 30 s FAIL is not separable from timing noise.
The joined per-entry table is `…attribution.summary.out`
(`…summary.py`); its `disp=` column applies these rules mechanically
and its `disposition totals` line counts them.

### 5.4 Class-1 and class-2 PASS→FAIL — attributed (11/11)

Evidence: probe 09 `.class1-{final,base1d998cc,basef8d2fde}.out`,
`.class2-…` and the per-commit matrix `.class{1,2}-<commit>.out`
(`.matrix.run`); joined in `.summary.out`. Fired rules are listed in
completion order (the top-level rule prints last).

| entry | record (pre → close) | f8d2fde | 1d998cc | first FAIL core | mechanism (fire traces) | disposition |
|---|---|---|---|---|---|---|
| 1.2.2.3 e220, e221, e222 | verified 2.4–2.9 s → deferred 0.4–0.5 s | V | V | **B1 `464d29f`** | `1_4_1_r18` now binds and fires (B1 changed its `Qx` declaration `freeof(x)` → `true`, the `.m` 1.4.1 L174 guard) and returns a top-level no-answer; base route `1_2_2_3_r32` (verified) | deterministic regression from a faithful declaration fix: `1_4_1` precedes 1.2.2.3 in the table and its answer route declines. Not fixed in the campaign; route/table-order behaviour is inherited by the matcher substrate |
| 1.1.1.2 e1890 | verified 3.6 s → deferred 0.2 s | V | V | **B2 `d6cee4e`** | `1_1_1_4_r46` fires (its cond carries the list-form `%mr_linearQ([u, v], x)` that B2's list arm makes true) → top-level no-answer; base route `1_4_2_r7` → `1_1_1_2_r39` | deterministic regression from the faithful `LinearQ` list arm; as above |
| 1.2.1.2 e2387, 1.2.1.4 e882 | verified 3.8 / 2.8 s → timeout 30 s | V | V | **B2 `d6cee4e`** | top-level `1_2_1_2_r115` as before, but its nested dispatch now runs `1_1_2_1_r13` → `1_2_1_2_r99` → `9_1_r9` → `1_2_1_9b_r32` (list-form `LinearQ` guards now true): on the B2 core `rubi` itself exceeds 30 s; on the close core the answer returns and the zero chain exceeds 30 s | deterministic slowdown from B2 (route change); 120 s class in §5.5 |
| 1.1.3.3 e181 | verified 3.9 s → unverified 0.2 s | V | V | **C5 `4702d4d`** | final route `1_4_1_r7` + `1_1_3_1_r60`; base `1_4_2_r7` | C5's shared-utils change: the `%mr_mbp_mono2` guard lift (`or` → `and`, signed-exponent monomials) widens `%mr_mbp2` (utils:4225), the structural matcher of the class-1 binpow rules `1_1_3_1_r60` / `1_1_3_3_r61`; C5 touched no class-1 rule file. Deterministic; the rebound route's answer does not verify |
| 1.2.2.2 e1124, 1.2.2.3 e403 | verified 1.2 / 0.8 s → unverified 0.8 / 0.5 s | V | V | **C5 `4702d4d`** | final route `1_1_3_3_r61` + `1_2_2_1_r18`; base `1_4_2_r7` + `1_2_2_1_r18` | as e181 (the widened `%mr_mbp2` binds `1_1_3_3_r61` first) |
| 1.2.1.6 e22 | verified 23.8 s → timeout 30 s | T | T | none | timeout at 30 s on the class-1/2 pre-campaign rules, the campaign base and the close core (no pass-1 fire before the cap) | **not a campaign change**: the pre-campaign record's 23.8 s verified was measured on the 2026-08-20 build; under the current build it exceeds 30 s on every rule set — build/near-cap timing; 120 s class in §5.5 |
| 2.2 e52 | verified 9.9 s → unverified 10.8 s | **V** 7.2 s | U | **milestone 3** (f8d2fde → 1d998cc) | from the campaign base on, the class-3 rule `3_5_r14` (3.5.m `(f+g x)^m Log[1+e (F^(c(a+b x)))^n]`) fires inside the nested chain and the answer no longer verifies; unverified on every campaign core | **not a campaign change**: introduced by milestone 3's class-3 load into the shared table (the milestone-3 close validated classes 1–2 with 51-entry no-op slices only) |

So the campaign's shared-dispatch cost on class 1 is 9 PASS→FAIL (B1 3,
B2 3, C5 3), deterministic and located to the commit, against 66
FAIL→PASS; on class 2 it is 0 (e52 predates the campaign), against 21
FAIL→PASS. The spec's "FAIL→PASS only" expectation for classes 1–2
fails on these 9 — recorded, not fixed (the campaign closed at its
current state; §4).

**Ticket-01 / ticket-02 entries, checked explicitly** (campaign plan
Task 5 Step 4, spec §5.3; tickets
`.scratch/class1-ab-remainders/issues/01-slow-zero-chain-forms.md` and
`02-matcher-state-91-pattern-load.md`). Probe 11
(`probes/corpus/11-deferred-close-class1-ticket-entries.{py,out}`, no
Maxima subprocess) reads the 16 entries from the two class-1 records:
`totals over the 16: PASS->PASS=2 PASS->FAIL=0 FAIL->PASS=2
FAIL->FAIL=12`. Ticket 01 (9 slow-form entries): 1.2.1.5 e59 and
1.2.2.3 e149 timeout → verified (23.4 / 26.1 s); 1.2.1.5 e66 / e73
verified → verified (28.6 → 23.9 s, 29.7 → 23.7 s); 1.1.4.3 e228,
1.2.1.3 e1979, 1.2.1.4 e686 / e687, 1.2.1.9 e308 timeout → timeout.
Ticket 02 (the 7-entry matcher-state families): 1.2.2.4 e223 deferred →
deferred (27.6 → 29.0 s); 1.2.1.2 e2514, e2567–e2569, e2572, e2573
timeout → timeout. No ticket entry regresses; the two FAIL→PASS are
among the class-1 66.

### 5.5 Class-3 PASS→FAIL — attributed (131/131)

Evidence: probe 09 `.class3-{final,base1d998cc}.out` (all 131), the
per-commit binary search `.class3-bisect.out` (the 127 entries PASS on
the base core and FAIL on the close core in the probe's 30 s runs;
every run's class/time and the last-PASS / first-FAIL fire traces are
in the file), the 120 s cap runs `.class3-final-cap120.out` /
`.e47-final-cap120.out`, the 100 s re-check (§5.6); joined per entry,
with the §5.3 disposition in the `disp=` column, in `.summary.out`.
**All 131 are PASS on the campaign-base rules under the current build**
— none is a build effect. By disposition (`.summary.out`:
`disposition totals: deterministic 122 + near-cap 5 + noise 4 +
unclassified 0 = 131`): **122 deterministic campaign changes; 5
near-cap / indeterminate** (bisected, but the close core's own runs
straddle the 30 s cap); **4 PASS on the close core** (noise in the
close record).

| first FAIL core | n | entries | mechanism (fire traces: base → close) | disposition |
|---|---:|---|---|---|
| **B1 `464d29f`** | 5 | 3.1.4 e95, e96; 3.1.5 e46, e53, e122 | the de-spuriated slots bind: `3_5_r2` (e95/e96) and `3_5_r34` (e46/e53/e122) now enter the chain; the answers stop verifying (e95/e96/e46 unverified 2–14 s; e53 unverified, 36.1 s at 120 s; e122 still timeout at 100 s and 120 s) | route changes from the faithful B1 declaration fix (3.2.3 e61, also bisected to this step, is near-cap: last row) |
| **C2 `52ffb6f`** | 24 | 3.1.2 e73–e75, e78–e83, e86–e88, e168, e169 (14); 3.1.5 e36, e38, e39, e45, e104, e106, e107, e111, e113, e114 (10) | the re-transcribed `3_1_2_r10` now binds first: the 3.1.2 rows get its m10 Subst answer instead of the base `3_1_5_r27` / nested `3_1_2_r6` routes and it does not verify (unverified 2–5 s); the 3.1.5 rows run r10 inside the nested chain and the route slows from 13–16 s (base) / 18–22 s (B4 core) to > 30 s | 3.1.2: the route change the ledger's C2 entry predicted for the p < 0 rows (`.m` fires m9 first; the port now fires m10 — both valid antiderivatives, the zero chain does not close m10's form). 3.1.5: **slow-correct** — verified in 34–69 s at 120 s and in 51–61 s at the 100 s re-check |
| **C4 `d2ae62d`** | 6 | 3.2.1 e132, e140, e141, e145, e146; 3.2.2 e255 | e140/e141/e145/e146: the structural matcher `%mr_logpow_match` declines entries the old r16 defmatch bound; the r22 Unintegrable catch-all (kept as defmatch) fires → deferred 2–3 s. e132: r16 binds on a different route → unverified. e255: `3_2_1_r18` now fires ahead of the base cover `3_5_r1` → expected → unverified | deterministic: C4's acceptance boundary is narrower than the old defmatch on these shapes (4 entries) or reroutes (2) |
| **C3 `1c8a306`** | 26 | 3.2.1 e14, e22, e23, e27, e28, e42, e50, e51, e55, e56; 3.2.2 e189, e210, e211, e216, e217, e222–e225, e241, e242, e244–e246, e248; 3.2.3 e39 | `%mr_logratio_match` declines 17 entries the old r15/r17 (3.2.1) and r3 (3.2.2) defmatches bound → the catch-alls `3_2_1_r21` / `3_2_2_r11` (or `3_2_3_r18` on e39) answer with a noun (deferred 1–4 s: 3.2.1 e22/e23/e27/e28/e50/e51/e55/e56 ×8, 3.2.2 e224/e225/e241/e242/e244–e246/e248 ×8, 3.2.3 e39). 9 reroute: r15/r17 bind through the matcher on e14/e42/e189 instead of base `3_5_r7`; `3_2_2_r5` binds e210/e211/e216/e217/e222/e223 with a different nested chain (`3_1_2_r10` in place of `9_1_r16`) → unverified | deterministic: C3's census-bounded acceptance (§4) misses these stored shapes (17) or changes the binding route (9) |
| **B3 `9533528`** | 7 | 3.3 e130, e134, e135, e157, e158, e165, e166 | e130/e134/e135: the re-transcribed r12/r13 now bind first (base `3_3_r29`) → unverified; e157/e158: the base cover `3_3_r10`, re-transcribed, no longer binds (no pass-1 fire) → deferred; e165/e166: re-transcribed `3_3_r25` answers a noun-expected entry → **unexpected, and the answer self-verifies** (`self=1`) | e130–e158: deterministic regressions of the B3 re-emission. e165/e166: a correct antiderivative where the corpus expects a noun — a yardstick reclassification, not a wrong answer |
| **C5 `4702d4d`** | 51 | 3.3 e5–e8, e12–e16 (9); 3.4 e536–e605 (42) | 3.3: the re-transcribed `3_4_r6` now binds the 3.3 linear-log shapes ahead of the base route (`3_1_5_r35`) and returns a noun → deferred 0.7–1.7 s. 3.4: the re-transcribed `3_4_r12` (34) / `3_4_r5` (5) answer noun-expected entries → unexpected; e551/e589/e603: the base `3_4_r39` no-answer (1 s) is no longer reached and nothing completes within 30 s, 100 s or 120 s | 3.3: deterministic regression (C5's binding widened into 3.3). 3.4 unexpected answers, self-check at 30 s: closes on 18 (e536, e537, e560, e561, e566, e567, e570–e574, e579, e580, e582–e584, e588, e590), does not close on 5 (e542, e543, e577, e578, e581), cut by the cap on 16 — re-run at 120 s: 3 close (e594, e595, e599), 3 do not close (e600, e601, e605), 10 still cut (e544–e546, e550, e552, e596–e598, e602, e604); the 5 non-closing ones stay non-closing at 120 s. Of the 39 answers: 21 self-verify (correct antiderivatives on noun-expected entries — yardstick reclassifications), 8 do not close under the zero chain, 10 unresolved within 120 s; the 3 timeouts stay FAIL |
| **C6b `99e1eb1`** | 3 | 3.1.5 e57, e63; 3.3 e179 | e57/e63: the pass-1 fire trace does not change across the C6→C6b step (`.class3-bisect.out`: last-PASS = first-FAIL traces); the close core runs them past the cap — 30 s cut, 37.0 / 46.5 s at 120 s (one run each), 40.7 / 35.1 s in the loaded 100 s re-check — against 22.5 / 25.9 s on the C6 core (one run each); the slowdown accumulates over the campaign (base 10.0 / 20.6 s, C1 core 20.3 / 24.8 s). e179: `3_5_r42` fires inside the chain and leaves the `unintegrable` marker → contains-noun | e57/e63: **slow-correct on timing evidence only** — C6b is where the single-run bisection crosses the cap, not a traced route change; in the loaded mid-campaign records on the C5/C6 cores (`test/corpus_class3_c6base.out` / `_c6post.out`) e57 verified at 28.0 / 29.3 s and 3.1.5 e63 already timed out (30.0 s both). e179: deterministic route change of the catch-all port (the C6b report's performance note) |
| — (near-cap / indeterminate) | 5 | 3.1.5 e112, e126, e132; 3.2.3 e61, e63 | rule (a) — e112/e126/e132 and 3.2.3 e63, bisected to C6→C6b by one 30 s timeout: the close core's 120 s run completes them inside the cap (verified 22.9 / 21.4 / 24.5 s, no-answer 22.8 s), matching their C6-core runs (23.1 / 21.0 / 24.5 / 23.9 s); last-PASS and first-FAIL fire traces identical for e126/e132/3.2.3 e63, e112 differing only by the top-level `3_5_r43` print the cut run never reached. Rule (b) — 3.2.3 e61, bisected to base→B1: identical fire trace on the base and close cores (`3_3_r60, 3_2_3_r10, 1_1_1_1_r2, 3_1_2_r2`), base run 23.8 s (28.5 s in the pre-campaign record); close core no-answer 31.3 s at 120 s, 84.0 s in the loaded re-check | **near-cap, not attributed to a commit**: a single 30 s FAIL against runs that straddle the cap. The rule-(a) entries did slow during the campaign (e126 10.0 s base → 21.0 s on the C1 core; 3.2.3 e63 6.3 s → 23.0 s on the B3 core), but not past 30 s on the close core's own 120 s run |
| — (PASS on the close core) | 4 | 3.1.5 e22, e44; 3.3 e547; 3.5 e1 | close core at 30 s: verified 21.2 / 27.9 s, no-answer 10.3 s, verified 3.8 s; 100 s re-check: verified 26.7 / 40.2 s, no-answer 12.2 s, verified 6.0 s | **run-to-run noise** in the close record (timeouts at 30–33 s under the 24-shard load). e22/e44 sit near the cap: slower than on the base core (6.1 / 15.2 s) since C2 — recorded, not a class change |

No PASS→FAIL is attributed to B2, B4, C1 or C6. Deterministic, by first
FAIL core: B1 5, C2 24, C4 6, C3 26, B3 7, C5 51, C6b 3 (= 122) +
near-cap 5 + noise 4 = 131 (`.summary.out` `disposition counts`).
Every deterministic entry is dispositioned **accepted as recorded, not
fixed**: the campaign closed at its current state (user decision
2026-09-11; §4) and each mechanism is a `defmatch`-emission side effect
(a workaround matcher's acceptance boundary, a route order change, or a
catch-all's cost) that the matcher substrate re-hosts.

e47 (the PENDING A-shaped entry): close record timeout 30.0 s; the close
core at a 120 s cap returns **deferred** in 15.3 s and the 100 s
re-check deferred in 24.8 s — the record's timeout is cap-band noise and
its production class is deferred (pass 4 is not wired, §3.1).

Class-1 120 s runs (`.class1-final-cap120.out`): e2387 and e882 still
timeout at 120 s (the B2 slowdown is not a cap-band effect); e22
verifies in 30.8 s (just over the 30 s cap on the current build).

### 5.6 The 100 s timeout re-check (standing protocol)

Run 2026-09-12 (launched 13:10:10 UTC, 24 shards, merged 13:26:10 UTC,
`merge rc=0`) on the close record's `timeout` class, same build and
core. **Corrected command** (controller ruling R12 — the campaign
plan's form omits the launcher's 4th positional section argument and
fails the launcher's own file-list assertion against the class-1
section):

```bash
python3 test/launch_timeout_rerun.py test/corpus_class3.out 100 test/corpus_class3.timeout-rerun2 "3 Logarithms" --launch
setsid sh test/wait_timeout_rerun.sh test/corpus_class3.timeout-rerun2 >> test/corpus_class3.timeout-rerun2/wait.log 2>&1 &
```

Record `test/corpus_class3.timeout-rerun2/corpus_class3.timeout100s.out`
(`Results: 22 passed, 190 failed`), transcript `…/merge.out`:
`OK: 212/212 re-checked, no dupes/missing/extra`. Transitions of the
212 (all `timeout` at 30 s):

| at 100 s | n |
|---|---:|
| timeout | 130 |
| unverified | 30 |
| deferred | 19 |
| verified | 18 |
| error | 8 |
| no-answer | 4 |
| contains-noun | 2 |
| unexpected | 1 |
| **now PASS** | **22** |

Still timeout at 100 s by family: 3.3 40, 3.1.5 28, 3.1.4 19, 3.2.1 14,
3.4 13, 3.5 7, 3.2.2 5, 3.2.3 4. Reading: 190 of 212 remain FAIL at
100 s (130 still `timeout` at 100 s) — the 30 s cap is not the binding
constraint for the bulk; the 22 slow-correct entries (18 verified +
4 no-answer) are the matcher-speed route of the standing decision (the
cap STAYS). The merge transcript's "run-5 baseline status" block is the
class-1-era template of `merge_timeout_rerun.py` (0 / 0 here) and has
no class-3 meaning. The per-entry re-check class of every timed-out
PASS→FAIL entry is in the probe-09 summary (`recheck100=` column).

## 6. 788 recovery (Task 5)

Source: probe 10 (`probes/corpus/10-class3-deferred-close-recovery.{py,out}`,
no Maxima subprocess) — a deterministic join of the pre-campaign record
`test/corpus_class3.campaign-baseline.out` (the §1 population: 1,033
deferred; re-asserted 788 = 313 + 16 + 459), the integrate-baseline
flags `test/corpus_class3.baseline.out`, the campaign-close record
`test/corpus_class3.out` (merged 2026-09-04 15:06 UTC, build 2026-08-31
13:27:47, core `5ef9b3bc`) and probe 08's enumerated entry sets.
"Recovered" = a PASS class (verified / expected / no-answer) in the
close record. (The 06/07/08 probes now read the pre-campaign record from
its `.campaign-baseline.out` backup — byte-identical to the record they
ran on — so they stay re-runnable after this close commits the new
`test/corpus_class3.out`.)

### 6.1 The target mass (spec §4 criterion 1)

| population (pre record `deferred`) | n | recovered | → verified | → expected | still deferred | → unverified | → timeout |
|---|---:|---:|---:|---:|---:|---:|---:|
| all deferred | 1,033 | **442** | 438 | 4 | 429 | 107 | 55 |
| **target mass (788)** | 788 | **366** | 362 | 4 | 296 | 95 | 31 |
| **certain subset (329)** | 329 | **222** | 222 | 0 | 62 | 44 | 1 |
| unverified-flag (459) | 459 | 144 | 140 | 4 | 234 | 51 | 30 |
| non-target (245) | 245 | 76 | 76 | 0 | 133 | 12 | 24 |

**The 788 shrinks by 366 to 422** (296 still deferred + 95 unverified +
31 timeout); **the 329 by 222 to 107** (62 + 44 + 1). Counted afresh on
the close record, the deferred mass is **467 entries — target-flagged
315, certain 71**: the 429 carried from the population plus 38 newly
deferred entries (pre class verified 32 / unverified 1 / timeout 5; per
file 3.2.1 12, 3.2.2 8, 3.2.3 2, 3.3 16). The 32 pre-verified ones are
§5 PASS→FAIL entries and are attributed there.

### 6.2 Recovery per fix row (the per-mechanism view)

Rows are the fix's **input list** (the §3.2 / §3.3 enumerations as
transcribed by probe 08). A recovery is counted on the list, not
attributed to that row's commit: several fixes share routes (the §5
matrix attributes the regression direction per commit; the recovery
direction is not bisected). B3, C5 and the 81 3_4 spurious-freeof B1
rows were never enumerated per entry, so they appear as file rows.

| fix row (input list) | enumerated / claimed | recovered | target recovered | certain recovered | still deferred |
|---|---|---:|---:|---:|---:|
| B1 spurious freeof (g1 2 + g4 41) | 43 / 124 | 39 | 38 / 39 | 16 / 16 | 0 |
| B2 `%mr_linearQ` list arm (g2) | 47 / 47 | 41 | 35 / 40 | 10 / 10 | 1 |
| B4 e392 | 1 / 1 | 1 (deferred → expected) | 1 / 1 | 0 / 0 | 0 |
| C1 M1 slotted inner exponent (g1, PARTIAL) | 117 / 209 | 83 | 78 / 109 | 70 / 75 | 13 |
| C2 M6 `(d*x)^m` head | 3 / 3 | 3 | 0 / 0 | 0 / 0 | 0 |
| C3 D2 ratio log-arg | 99 / 99 | 21 | 21 / 98 | 18 / 58 | 0 |
| C4 D3/D4 r16/r18/r20 | 13 / 13 | 12 | 12 / 13 | 6 / 6 | 0 |
| C6 + C6b (g4 C-in-Rubi, 9 groups) | 31 / 31 | 20 | 16 / 22 | 10 / 14 | 9 |
| A — pass 4 not wired | 10 / 10 | 5 | 5 / 8 | 5 / 5 | 5 |
| file 3.3 (B3 125 + D 16 + A 1 + PENDING 18) | 160 / 160 | 5 | 5 / 110 | 2 / 18 | 149 |
| file 3.4 (B1 82 + C5 128 + C-absent 20 + PENDING 5) | 235 / 235 | 117 | 72 / 132 | 30 / 39 | 106 |

Readings: C3 removed every binding failure on its list (0 still
deferred), but 78 of its 99 entries are not recovered (probe 10 §9:
`3.2.1:timeout=5 3.2.1:unverified=2 3.2.2:unverified=70
3.2.3:timeout=1`): 72 `unverified` — rebound answers that do not close
under the zero chain — and 6 `timeout`. The C3 residue is
verification- and cost-stage, not matching. The five
g2 A entries (3.2.1, `3_2_1_r14`) PASS on the production path of the
close tree although pass 4 is not wired; the four g1 A entries and e360
(g3) remain deferred — their only measured rescue is the unwired sweep.

### 6.3 Per-file residue (target mass) and why not

The residue is the target-flagged population entries whose close class
is not PASS. The why-not column counts each §2 verdict class **inside
that residue** (probe 10 §10: the residue joined to the probe-08
enumerations and to the §2 per-family claims), with the residue
entries' close classes; residue entries in no enumerated set are
counted as *not enumerated* and named by elimination only where the
file leaves a single class unenumerated. A class not listed for a file
has no residue entry.

| file | target n | recovered | residue (close class) | why the residue was not recovered (verdict class × residue, probe 10 §10) |
|---|---:|---:|---|---|
| 3.1.2 | 0 | — | — | no target entries (the 9 deferred are non-target; 8 of 9 now PASS) |
| 3.1.4 | 216 | 115 | deferred 90, timeout 6, unverified 5 | C-in-Rubi C1 M1 23 enumerated (deferred 13, timeout 5, unverified 5; not re-triaged at this close); D 8 enumerated (deferred: e5, e31–e33, e41, e48, e174, e282 — §2 g1 D: M2 faithful 0-bind / `.m` coverage gap); **70 not enumerated** (deferred 69, timeout 1), drawn from the unenumerated C-in-Rubi (92) and D (22) remainders — not separable without re-triage |
| 3.1.5 | 28 | 3 | deferred 11, timeout 6, unverified 8 | D 15 (deferred 9, incl. the M5 strict declines e194/e195; timeout 1; unverified 5); C1 M1 8 (timeout 5: e95, e97–e99, e118; unverified 3: e92, e141, e147 — e92/e118/e141/e147 are the ledger C1 entry's C1a q = −1 rows); A 2 (e5, e91 deferred — rescued only by the unwired sweep) |
| 3.2.1 | 81 | 69 | deferred 4, timeout 5, unverified 3 | C3 D2 7 (timeout 5: e244–e248; unverified 2: e101, e186); C-absent Ei 4 (deferred: e117, e118, e199, e200 — no `.m` rule, §3.4; the group's other 8 are non-target); C4 1 (e214 unverified) |
| 3.2.2 | 131 | 45 | deferred 3, timeout 5, unverified 78 | C3 D2 70 `unverified` (rebound answers that do not close under the zero chain); D 11 (deferred 3: e230, e252, e261; unverified 8: e5–e9, e33, e41, e49); B2 B-port 5 `timeout` (e249–e251, e259, e260); C-absent e243/e247 are non-target |
| 3.2.3 | 22 | 1 | deferred 18, timeout 3 | D 20 (deferred 17; timeout 3: e1, e58, e69 — §2 g2 D: r18-faithful, M3, the `3_5_r1 + 3_5_r38` variant, cross-family, POOL); C-absent 1 (e89 deferred); the 4 PENDING are non-target |
| 3.3 | 110 | 5 | deferred 101, timeout 4 | **98 not enumerated** (deferred 94, timeout 4) = the B3 B-port cluster by elimination (125 claimed, none enumerated): B3 landed 10 rule binds, but the entries' answers stay nouns downstream (ledger B3: e88/e90 leave a 3.2.x nested sub-integral, e156's ExpandIntegrand no-ops; M3 r46/r24/r28 stopped); D 6 (deferred: e329, e330, e347, e348, e371, e372 — D-NEST); A 1 (e360 — unwired sweep only); the 18 PENDING are non-target |
| 3.4 | 132 | 72 | deferred 58, timeout 2 | C-absent 4 enumerated (deferred: e125–e128 — no `.m` cover, §3.4; 8 of the 14 enumerated C-absent entries now PASS, probe 10 §5); **56 not enumerated** (deferred 54, timeout 2), drawn from the unenumerated B1 spurious-freeof (81), C5 C-in-Rubi (128) and C-absent (6) remainders — not separable without re-triage |
| 3.5 | 68 | 56 | deferred 11, unverified 1 | C6 groups 6 deferred (M-implicit1 e11, e49 — superseded; M-class4 e180, e183, e186, e187 — class 4 unported); C-absent 3 (deferred: e19, e34, e300); D 2 (deferred: e301, e302 — D-NEST); B1 r31_u 1 (e126 `unverified`). e266 (M-barelog-optional), e98 (M-multistep), e92 (M-cas-simp) and e181 (M-class4) carry non-target flags |

### 6.4 The C6 mechanism groups — end state per entry

Probe 10 §7 (pre record / c6post record (C6 core, 2026-09-02) / close
record; baseline flag in parentheses):

| group | status at close | entries |
|---|---|---|
| M-functionoflog (C6b) | landed | e134 e135 e136 e140 e143 e149 e150 e151 e152 e225 e258 e261: deferred / deferred / **verified** (12/12) |
| M-implicit1 (e139 moved to C6b) | e139 landed in C6b; e11/e49 **superseded** | e11, e49: deferred / deferred / deferred; e139: deferred / deferred / **verified** |
| M-cas-simp (C6) | landed; no transition | e92: deferred / unverified / unverified; e93: deferred / timeout / timeout |
| M-plus-identity | **superseded** — PASS via another route | e56, e58: deferred / deferred / verified |
| M-barelog-optional | **superseded** | e266: deferred / deferred / deferred |
| M-factored-quad | **superseded** — PASS via another route | e103, e106, e107: deferred / verified / verified |
| M-323 | **superseded** — PASS via another route | e243, e244: deferred / verified / verified |
| M-class4 | recorded only | e180 e181 e183 e186 e187: deferred / deferred / deferred |
| M-multistep | recorded only | e98: deferred / deferred / deferred |

So of the five superseded groups' 10 entries (e139 excluded), 7 PASS on
the close tree through other rules (none of the five re-transcriptions
landed; the routes changed with B1–C5) and 3 remain deferred (e11, e49,
e266) — the residue the matcher substrate inherits.

### 6.5 PENDING (28) and the A count

The 28 PENDING-REMEASURE entries of §3.6 on the close record: g1 e47
**timeout** (30.0 s; pre record deferred 8.3 s); g2 ×4 — 0 recovered, 3
still deferred; g3 ×23 — 0 recovered, 22 still deferred. The A count's
10-vs-11 gate is moot for production: pass 4 is not wired (§3.1), so
e47's sweep rescue stays prototype-only whichever way it reads; e47's
close-core class at a 120 s cap is recorded in §5.5.

## 7. Regression gates and acceptance (Task 6)

### 7.1 Standing gates (re-measured at the close, 2026-09-12, tree `class3-deferred` @ d535e24 + the close's record/doc files — no rule, generator, utils or test-suite change)

- **Layer A** — `maxima --very-quiet -X "--tls-limit 100000" -b test_maxima_rubi.mac`:
  `Results:  892  passed,  0  failed` (0 `FAIL` lines; the count line
  of AGENTS.md already reads 892 — unchanged).
- **Byte-identity** — `python3 generator/generate_rules.py --class 1`,
  `--class 2`, `--class 3`, then `git status --porcelain rules/`: empty
  output (all three classes regenerate byte-identical).
- **Core fingerprint** — the tree fingerprint (md5 over the loader,
  utils, the dispatch / implicit-1 / pass-4 Lisp files and every
  class-1/2/3 rule file, the `build_rules_core.sh` list) vs the core
  stamp that measured every close record:
  `tree 5ef9b3bc5ee07ffac0e76f1fea54fbac` /
  `fingerprint 5ef9b3bc5ee07ffac0e76f1fea54fbac` — consistent.

### 7.2 Stamp

- Date of the close measurements: class-3 record 2026-09-04; class-1/2
  records, probes 09/10, gates 2026-09-12.
- `build_info()`: `Maxima-version: "branch_5_50_base_84_g4204fb669"`,
  `Maxima build date: "2026-08-31 13:27:47"`, `Host type:
  "x86_64-pc-linux-gnu"`, `Lisp implementation type: "SBCL"`, `Lisp
  implementation version: "2.6.7"`.
- Rules core **before** the campaign: `00e05dca117aefd8df3d266652b11e93`
  (3,513 rules; campaign base 1d998cc — the class-3 pre-campaign
  record's rules); the triage core with the pass-4 Lisp baked in:
  `36b8bae7dba3c6e4fde614b6df70caa4`. **After**:
  `5ef9b3bc5ee07ffac0e76f1fea54fbac` (3,514 rules; 99e1eb1). The
  class-1/2 pre-campaign records' core: `aa53741f7ac802e2c3b8bd93720b219d`
  (3,180 rules; f8d2fde).
- Record file hashes (md5):

| file | md5 |
|---|---|
| `test/corpus_class3.out` | `92565d7efafdd70879304b0551d22c5f` |
| `test/corpus_class1.out` | `386a0a316391ceec315944958a719f85` |
| `test/corpus_class2.out` | `2eb8f9c2703c8e855dad5c4f8e89fe06` |
| `test/corpus_class3.campaign-baseline.out` | `128013c3844636572ff5326a535a8caf` |
| `test/corpus_class1.campaign-baseline.out` | `6417dfd8be42c6a9a9eb9c9d169f5a89` |
| `test/corpus_class2.campaign-baseline.out` | `c28c9803d69bce7b26c7818764557775` |
| `test/corpus_class3.baseline.out` (integrate baseline) | `533e2d2291686b9cfee75d1950ea5f88` |

### 7.3 Acceptance scorecard (spec §4)

| # | criterion | result | evidence |
|---|---|---|---|
| 1 | **The 788 shrinks** — new target-mass count, per-mechanism recovery of the 788 and of the 329, per-family residue with why-not | **Met.** 788 → 366 recovered (422 remain: 296 deferred + 95 unverified + 31 timeout); 329 → 222 recovered (107 remain). The close record's own deferred mass: 467 (target 315, certain 71). Per fix row and per file with why-not lines (verdict classes counted inside the target residue): §6.2–§6.3; the C6 groups per entry: §6.4 | probe 10 (§5–§10); `test/corpus_class3.out` |
| 2 | **Regression gate** — zero unattributed PASS→FAIL on class 3; classes 1–2 expected FAIL→PASS only, same rule | **Met on attribution: 142 / 142 PASS→FAIL attributed and dispositioned** (class 3 131: 122 deterministic by commit — B1 5, C2 24, C4 6, C3 26, B3 7, C5 51, C6b 3 — + 5 near-cap / indeterminate + 4 noise; class 1 10: 9 deterministic — B1 3, B2 3, C5 3 — + 1 build/near-cap; class 2 1: milestone 3, pre-campaign; the ticket-01/02 class-1 entries: no PASS→FAIL). **Not met on shape:** classes 1–2 are not FAIL→PASS-only — 9 class-1 regressions come from campaign commits (shared utils / class-1 declarations). All deterministic regressions are accepted as recorded, not fixed (campaign closed at its current state) | §5.4–§5.5; probes 09, 11 |
| 3 | **Standing gates green** — Layer A, byte-identity, core fingerprint, the 100 s re-check executed | **Met.** Layer A 892/0; byte-identity ×3 clean; fingerprint tree = stamp `5ef9b3bc…`; 100 s re-check executed on the close record's 212 timeouts (22 now PASS) | §7.1, §5.6 |
| 4 | **Measured-claims discipline** — every non-trivial claim cites a committed, re-runnable probe | **Met.** §1–§3: probes 06/07/08; §4: the ledger's per-brief re-measured entries; §5: `ab_records.py` + probes 09 / 11 (+ the re-check record); §6: probe 10; §7: the gate commands | Provenance |
| 5 | **Ticket 04 updated** with the class-3 go/no-go number and the option-(ii) status | **Met.** Status → partially answered by this record: question 3 answered on the class-3 population (FIRE4 17 / 13 target; 0FIRE-EXPL 181), option (ii) implemented as pass 4 and NOT shipped (cost gate), remaining questions restated open | `.scratch/class1-ab-remainders/issues/04-matcher-backtracking-feasibility.md` |

**Campaign verdict: closed** (user decision 2026-09-11) — class 3
1,736 → 2,058 / 3,085 (+322 PASS; PASS→FAIL 131 all attributed), with
the five remaining C6 groups and every recorded deterministic regression
handed to the matcher substrate (`docs/superpowers/specs/2026-09-12-matcher-substrate-design.md`).

## Provenance

- Triage: `probes/corpus/06-class3-deferred-mechanisms.py` →
  `probes/corpus/06-class3-deferred-mechanisms.out` (committed; build
  2026-08-29 17:58:20; core `36b8bae7…`).
- Fallbacks: `probes/corpus/07-class3-deferred-sweep-cost-fallbacks.py`
  → `…fallbacks.out` (build 2026-08-31 13:27:47; 37 swept entries;
  production semantics).
- Split: `probes/corpus/08-class3-deferred-verdict-flag-split.py` →
  `…flag-split.out` (build 2026-08-31 13:27:47; joins the committed
  records).
- Adjudication wave files (the per-entry enumeration and probe
  evidence, gitignored working docs):
  `probes/corpus/06-class3-deferred-mechanisms.work/adjudication-g1.md`
  through `g4.md`; this record's §2 is self-contained against them.
- Records: `test/corpus_class3.out` (1,033 deferred),
  `test/corpus_class3.baseline.out` (788 target-flagged). **At the
  close** the pre-campaign package record moved to
  `test/corpus_class3.campaign-baseline.out` (byte-identical; probe 06's
  `PKG_RECORD` points there) and `test/corpus_class3.out` is the
  campaign-close record; likewise `test/corpus_class{1,2}.out` /
  `.campaign-baseline.out`.
- Close attribution: `probes/corpus/09-deferred-close-passfail-attribution.py`
  (+ `.run` base/final cores, `.matrix.run` per-commit cores for classes
  1–2, `.bisect.py` per-commit binary search for class 3, `.summary.py`
  the joined table; shards `.class{1,2,3}.shard`, `.class1-matrix.shard`,
  `.class{1,3}-cap120.shard`, `.e47.shard`; outputs `.class*-*.out`,
  `.class3-bisect.out`, `.summary.out`) — build 2026-08-31 13:27:47,
  run 2026-09-12.
- Close recovery join: `probes/corpus/10-class3-deferred-close-recovery.{py,out}`
  (no Maxima subprocess; §9 unrecovered classes per fix row, §10 the
  target residue per file × verdict class).
- Ticket-01/02 class-1 check: `probes/corpus/11-deferred-close-class1-ticket-entries.{py,out}`
  (no Maxima subprocess; the two class-1 records).
- Mid-campaign records cited: `test/corpus_class3_c6base.out`,
  `test/corpus_class3_c6post.out` (2026-09-02; ledger C6 entry).
- Pinned Rubi sources: `reference/rubi/Rubi/IntegrationRules/3
  Logarithms/*.m` (11 files) + `IntegrationUtilityFunctions.m` +
  `4 Trig functions/4.7.5 Inert trig functions.m`; the suite:
  `reference/maxima-syntax-test-suite/3 Logarithms/`.
- Spec: `docs/superpowers/specs/2026-08-30-class3-deferred-campaign-design.md`;
  plan: `docs/superpowers/plans/2026-08-30-class3-deferred-campaign.md`.
