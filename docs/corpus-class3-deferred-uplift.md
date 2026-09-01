# Class-3 deferred campaign — measured uplift record

Phase-2 decision record for the class-3 deferred campaign (spec
`docs/superpowers/specs/2026-08-30-class3-deferred-campaign-design.md`;
plan `docs/superpowers/plans/2026-08-30-class3-deferred-campaign.md`,
Task 3). Every list below is data-bound to a committed probe output;
§4–§7 are stubs that Tasks 4–6 fill with their own measurements
(measured-claims discipline: no claim before its measurement).

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

## 4. Phase-2 fixes (Task 4) — STUB

Filled by Task 4 (4A: the pass-4 NO-GO record; 4B: the B list of §3.2;
4C: the C-in-Rubi list of §3.3) with its own measurements. Not
pre-written.

## 5. Phase-3 re-measurement (Task 5) — STUB

Filled by Task 5: the full class-3 corpus A/B re-run vs
`test/corpus_class3.out` (completeness 1,033/1,033 asserted), including
the PENDING re-measures of §3.6 (e47 at 100 s — the A count 10 vs 11
gate). Not pre-written.

## 6. 788 recovery (Task 5) — STUB

Filled by Task 5: the target-mass movement (verified/expected/
unverified) between the pre- and post-fix records, against the §3.7
split. Not pre-written.

## 7. Regression gates and acceptance (Task 6) — STUB

Filled by Task 6: the Layer A suite (`test_maxima_rubi.mac`), the
byte-identity check (`generator/generate_rules.py --class 1/2/3`), the
core rebuild + fingerprint sync, the class-1/class-2 A/B regression
gate, and the acceptance record. Not pre-written.

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
  `test/corpus_class3.baseline.out` (788 target-flagged).
- Pinned Rubi sources: `reference/rubi/Rubi/IntegrationRules/3
  Logarithms/*.m` (11 files) + `IntegrationUtilityFunctions.m` +
  `4 Trig functions/4.7.5 Inert trig functions.m`; the suite:
  `reference/maxima-syntax-test-suite/3 Logarithms/`.
- Spec: `docs/superpowers/specs/2026-08-30-class3-deferred-campaign-design.md`;
  plan: `docs/superpowers/plans/2026-08-30-class3-deferred-campaign.md`.
