# Class 4 (trigonometric functions) port — 22,472 entries

Status: needs-triage
Type: task (port, runbook-driven)
Filed: 2026-08-30 (milestone-3 close; the M2 TODO's class-4 item, now
against the instantiated runbook)

## Scope

Port the "4 Trig functions" section (section name VERIFIED against
`reference/maxima-syntax-test-suite/4 Trig functions/` — 77 `.mac`
files under subdirs 4.1 Sine … 4.7 Miscellaneous) and its rule files
(`reference/rubi/Rubi/IntegrationRules/4 Trig functions/`) per
`docs/class-porting.md` Steps 1–10. The milestone-3 instantiation
(`docs/corpus-class3-baseline-uplift.md`) is the template; its
standing constraints bind (byte-identity gate for every accepted
class, 30 s per-entry cap, 100 s timeout re-check, A/B vs the
`integrate` baseline, acceptance record per the class-2/class-3
template, TLS probe on the core rebuild).

## Recon numbers (measured 2026-08-30 — PRE-CENSUS; the runbook
Step-1 census probe is the first act of the port and supersedes
these)

- **Corpus: 22,472 entries** — counted over the section's 77 `.mac`
  files (lines starting with `[`); matches the M2 TODO's figure.
  **The largest section in the suite** (class 1, the manually
  ported milestone-1 corpus, is 25,697 — class 4 is next in size).
- Rule files: **57 `.m` files in the tree, 56 `Rubi.m` LoadRules
  entries** — 1 `.m` file is NOT in the LoadRules list; the
  Step-1 census settles membership (the class-7 ticket carries the
  same note, 4 files there).
- Rule count: **2,095 `Int[... ] :=` lines** across the 57 `.m`
  files (recon count over ALL files in the tree, loaded or not; the
  Step-1 census probe is the authoritative loaded count).

## Known interactions

- **Deliberately LAST in the queue (8 → 5 → 6 → 7 → 4)** — largest
  corpus (22,472 entries), most files (77), and the class that
  exercises the ported machinery at the largest scale (run cost:
  class 3's 3,085 entries took 28 min 04 s wall under 24 processes;
  class 4 is ~7x — the launcher's cost model will shard heavily, as
  it did for class 3's 456-entry 3.1.4).
- The trig heads (`sin`/`cos`/`tan`/`cot`/`sec`/`csc`) are native;
  the class-3 headvar `F_` allow-list covers the inverse heads that
  4.1.5/4.3.x/4.5.x shapes pair with (`asin`/`acos`/`asinh`/…); the
  Step-1 census decides any new headvar allow-lists.
- Expect the class-3 residue profile at 7x scale: a `deferred`
  mass (2,095 rules against 22,472 shapes — a thinner
  rules/entries ratio than class 3), a special-function
  `unverified` mass (the trig-integral heads `si`/`ci`/`shi`/`chi`/
  `Ei` appear in 4.7 Miscellaneous expected texts — the class-3
  `HEAD_REWRITES` rows may already cover them; the Step-1
  answer-head census decides), and a non-terminator `timeout` mass
  (the class-3 96/117 confirmed-non-terminator rate).
- If the class-3 polylog-shim
  (`.scratch/class3-polylog-ceiling/issues/01`) lands first, class 4
  runs on the post-shim harness — no record re-baseline needed
  (the shim is a verification-harness change only, the M2
  radcan-fallback precedent: re-measure the earlier classes' no-op
  slices, not their full corpora, unless a class's expected texts
  exercise the new closure).

## Acceptance

Per the runbook: merged records complete (22,472/22,472), A/B
triaged with nothing unexplained, re-check read, acceptance record
committed, the byte-identity gates for classes 1–3 (and 8/5/6/7 if
accepted earlier) green, Layer A green.

## Comments

## The inert-trig substrate is the load-bearing part (measured 2026-09-20)

Probe `probes/rubi/02-hyperbolic-inert-trig-bridge.{py,run,out}`. Rubi's
section-4 rules are **not** written against `Sin`/`Cos`/…; they are written
against six **inert** lowercase heads, `sin[…]` … `csc[…]` (measured
occurrences in the rule files: sin 1518, csc 940, tan 640, cos 551, sec 225,
cot 133). An active integrand enters that representation through ONE catch-all
rule at the head of `4.1.0.1`, the first section-4 file Rubi.m loads:

```
Int[u_, x_Symbol] := Int[DeactivateTrig[u, x], x] /; FunctionOfTrigOfLinearQ[u, x]
```

Two consequences for this port:

**1. It gates class 4 itself.** Without the inert representation, the
normalization files (`4.7.1` Sine / `4.7.2` Tangent / `4.7.3` Secant, `4.7.5`
Inert trig functions) and every `sin[…]`-patterned rule are unreachable. This
is not a tail item to defer to a later cluster — it is Step 4's first cluster.

**2. It unlocks 1,166 already-paid-for class-6 entries.**
`DeactivateTrigAux`'s `HyperbolicQ` branch maps the six hyperbolic heads onto
the same inert trig heads (`Sinh -> -I sin[I z]`, …), which is how Rubi answers
the class-6 `.7` family — 36.7 % of class 6's deferred mass, currently zero
PASS. See `.scratch/class6-residue/issues/01` (ANSWERED section). This is the
reason class 4 was chosen ahead of 5/7/8.

### CENSUS TRAP — a rule-side token scan will miss the substrate

Measured token counts, section-4 rule files vs `IntegrationUtilityFunctions.m`:

| token | in rules | in utils |
|---|---:|---:|
| `ActivateTrig` | 129 | 11 |
| `KnownSineIntegrandQ` | 22 | 1 |
| `KnownSecantIntegrandQ` | 22 | 1 |
| `InertTrigFreeQ` | 10 | 3 |
| `InertTrigQ` | 7 | 6 |
| `DeactivateTrig` | 2 | 8 |
| `FunctionOfTrigOfLinearQ` | 2 | 3 |
| **`ReduceInertTrig`** | **0** | 39 |
| **`FixInertTrigFunction`** | **0** | 98 |
| **`UnifyInertTrigFunction`** | **0** | 79 |

The last three appear **nowhere in the rules** — they are reachable only
*through* `DeactivateTrig` — yet they carry 39 / 98 / 79 clauses. The Step-1
census must therefore take its **transitive closure through the utility
functions**, not stop at the tokens the rule files mention, or the port will be
generated against a substrate that silently is not there. (The 2026-09-20 recon
listed 48 unlisted tokens from a rule-side scan; these three are not among
them and `DeactivateTrig`/`FunctionOfTrigOfLinearQ` sit in its tail at 2
occurrences each.)

### Adjudication order this implies

Cluster the Step-4 utility work as: (a) the inert representation + `InertTrigQ`
/ `InertTrigFreeQ` / `ActivateTrig` / `DeactivateTrig` / `DeactivateTrigAux` /
`ReduceInertTrig` / `FixInertTrigFunction` / `UnifyInertTrigFunction` /
`FunctionOfTrigOfLinearQ`; then (b) the volume tokens (`Tan` 387, `Cot` 318,
`FreeFactors` 156, `ExpandTrig` 50, `FunctionOfQ` 42, …); then (c) the
already-ported ones (`ExpandTrigReduce`, `ExpandTrigToExp`, `IndependentQ`,
`MemberQ`, `Coth`, `Cosh`).

**Dispatcher position:** the bridge rule has a bare `u_` LHS. Mathematica sorts
it last by specificity; our dispatcher walks the table in LOAD ORDER and stops
at the first rule that answers, so the ported record must sit at the **end of
the whole table**, after every class — not at the head of class 4 where its
source file sits. Cf. the class-6 close's conclusion 2 (load order is priority)
and probe 21's unreachable `3_5 r37`.

## Step 1 — census, 2026-09-20 (supersedes the 2026-08-30 recon numbers)

Probes: `probes/translation/06-class4-syntax-census.{run,out}` (Step 1a),
`probes/corpus/14-class4-answer-heads.{run,out}` (Step 1b — reuses the class-6
script, which takes the section as argv[1]).

### 1a — rule side

| | |
|---|---|
| Rubi.m-loaded rule files | **56** (of 57 `.m` in the tree — 1 unloaded, as the recon suspected) |
| rules, census count | **2,073**, every one with a `/;` condition |
| AUTO (all tokens BUILTIN/B-tier) | **1,106 (53.4 %)** |
| MANUAL (>=1 C-tier / exotic pattern) | **967 (46.6 %)** |
| unlistied token rows to adjudicate | **56** |

Easier per rule than class 6 (26.4 % AUTO) and ~5.3x the volume.

**`EXPECTED_TOTAL[4]` is 2,080, not 2,073.** Section 4 carries **7**
`If[TrueQ[$LoadShowSteps], …]` wrappers, which the census parser does not count
and `unwrap_showsteps_lines` does recover — the class-3 precedent (census 333,
emitter 334). Measured per class: class 1 → 1 wrapper, class 2 → 0, class 3 → 1,
class 6 → 0, **class 4 → 7**.

All 7 are in the inert-trig machinery, and all have a bare `u_` LHS:

- `4.1.0.1` ×1 — the bridge: `Int[u_,x] := Int[DeactivateTrig[u,x],x] /; FunctionOfTrigOfLinearQ[u,x]`
- `4.7.5 Inert trig functions` ×6 — the substitution catch-alls:
  `∫F[Tan[a+b x]]dx → 1/b Subst[∫F[x]/(1+x²)dx, x, Tan[a+b x]]` (and the `Cot`
  mirror), the two derivative-divides forms
  `∫F[Sin[a+b x]]Cos[a+b x]dx → Subst[∫F[x]dx,x,Sin[a+b x]]/b` (and `Cos`), a
  second `Tan` form, and the **half-angle Weierstrass substitution**
  (`Tan[FunctionOfTrig[u,x]/2]`, wrapped in `Block[{$ShowSteps=False,…}]`).

So the census-invisible rules are exactly the general trig machinery — the part
that answers everything the shape-specific files do not. They need
`FunctionOfTrig`, `FreeFactors`, `SubstFor`, `Block`, `TryPureTanSubst`, and
end-of-table dispatcher position (see the substrate section above).

### 1b — answer side

77 files, **22,472 entries** (both recon figures confirmed). 22 answer heads are
native to the installed build; 12 are not. Measured on
`branch_5_50_base_84_g4204fb669`:

| head | entries | arity | Maxima | verdict |
|---|---:|---|---|---|
| `AppellF1` | **823** | 6 | `appell_f1` exists as a NOUN | **`diff` does not evaluate** — a verification ceiling |
| `Si` | 742 | 1 | `expintegral_si` | HEAD_REWRITES row exists |
| `Ci` | 738 | 1 | `expintegral_ci` | row exists |
| `Unintegrable` | 657 | 2 | — | Rubi's own non-answer marker, not a rewrite |
| `GAMMA` | 462 | 2 | `gamma_incomplete` | row exists |
| `FresnelC` | 333 | 1 | `fresnel_c` | **differentiable**: `d/dx = cos(%pi x²/2)` — new row |
| `FresnelS` | 322 | 1 | `fresnel_s` | **differentiable**: `d/dx = sin(%pi x²/2)` — new row |
| `CannotIntegrate` | 57 | 2 | — | non-answer marker |
| `F` | 8 | 5 | — | free function in the expected text |
| `Ei` | 6 | 1 | `expintegral_ei` | row exists |
| `Hypergeometric2F1` | 3 | 4 | `hypergeometric([a,b],[c],z)` | **differentiable** — new row, arity reshape |
| `HurwitzLerchPhi` | 2 | 3 | `lerch_phi` exists | `diff` does not evaluate |

Native mass worth noting: `polylog(` 2,325, `elliptic_f(` 3,798, `elliptic_e(`
3,781, `%e^` 4,600.

**Three new HEAD_REWRITES rows to add at Step 7** (`fresnel_c`, `fresnel_s`,
`hypergeometric` with the arity reshape), covering 658 entries.

**The ceiling is `AppellF1`, 823 entries (3.7 % of the section).** `appell_f1`
is a bound noun with no derivative, so those expectations cannot close the zero
chain — the class-3 polylog-ceiling situation exactly
(`.scratch/class3-polylog-ceiling/issues/01`). Expect them as `unverified` /
`contains-noun` rather than PASS, and do NOT read them as a rule-side miss.

### Still to do before generating

- **Adjudicate the 56 unlistied token rows on this ticket** (Step 1c), taking
  the closure transitively through `IntegrationUtilityFunctions.m` — see the
  CENSUS TRAP table above, which is how `ReduceInertTrig` (39 clauses),
  `FixInertTrigFunction` (98) and `UnifyInertTrigFunction` (79) enter the
  closure despite 0 rule-side occurrences.
- Decide the **inert-head representation**: the six inert heads must be Maxima
  operators the simplifier leaves alone (not `sin`/`cos`/…, or Maxima evaluates
  them), matchable by `MR-MATCH`, and mapped back by `ActivateTrig`. This is
  the one genuinely new substrate question in the port and it is a design
  decision, not a runbook step.

## Carried from the inert-trig substrate (merged 2026-09-21, `0d7d0cc`)

The substrate is on `master`: the eight class-4 TAIL records (4.1.0.1 bridge; 4.7.5 r21, r22,
r47, r48, r58, r71, r72) are generated through `CLASS4_SUBSET` in `generator/generate_rules.py`,
with EVERY other class-4 rule still unported. The spec's "Amendments (2026-09-21, execution)"
section records what changed against the plan. The final whole-branch review deferred these
items to this port. None blocked the merge:

- **Class-4 body rules go in BEFORE class 6.** `mr_load_all` loads the class-4 files after class
  6, which is harmless only while their body lists are empty (Rubi.m loads section 4 before 5 and
  6). The comment in `mr_load_all` says so.
- **`test/test_rule_table_order.mac`'s universal check iterates `mr_rule_table`**, not every
  registered handle, so a `_tail` list that `mr_load_all` forgets never enters the table and goes
  unseen. Only the hard-coded "exactly the eight" check catches that, and only for class 4. Make
  it iterate 1..fill-pointer when class 4's body rules land.
- **Repl misfires on inert integrands:** `1_4_1` r18 and `1_1_1_7` r5 "misfire (repl error)" on
  inert-head integrands. They are caught, so the cost is time and log noise.
- **The hyperbolic branches of FunctionOfQ / SubstFor are not ported.** Maxima simplifies
  `cos(%i*z)` to `cosh(z)`, so records decline there. This is a reach limit on class 6 (and on
  class 4's hyperbolic re-entry).
- **The generated rit r4 duplicates the hand-ported `%mr_reduceInertTrig3`.** It is unreachable in
  a 2-arg walk, and the two copies differ on a Switch miss (`false` vs a noun).
- **radexpand vs PowerOfInertTrigSumQ:** `(b*sin(x)^2)^(1/2)` is rewritten before the predicate
  sees it. This is the `mr_model_flags` question.
- **Tests to add:** the fitf targets check the output, not WHICH clause fired; and there is no
  committed DeactivateTrig target on a sum or a quotient of trig calls.
- **Cost:** class-6 timeouts rose 5 → 191, attributed to (unmeasured split) r71's trial
  integration, the r71 split-With repl integrating twice more, r21/r22 going live, and the
  unbounded `factor(ratsimp(u))` in the 4-arg SubstFor. Run the standing 100 s timeout re-check
  (`test/launch_timeout_rerun.py`) on `test/corpus_class6.inert-substrate.out` to separate
  slow-but-correct entries from runaways.
- **Related tickets:**
  - `.scratch/class-ports/issues/07`: the six legacy bare-`u_` records sit mid-table. Also note
    there that `mr_giveup_last` runs the non-give-up tail records ahead of the body give-ups.
  - `.scratch/class-ports/issues/08`: unprefixed generated With locals in classes 1/2/3/6, and
    `mr_sum`'s own locals, which already give **silently wrong answers on master**.
  - `.scratch/corpus-harness/issues/04`: `c*'unintegrable` read as contains-noun.

### 2026-09-25 — Step 1 (census) COMPLETE, closure adjudicated; status needs-triage -> ready

Build `branch_5_50_base_84_g4204fb669` (2026-08-31 13:27:47), SBCL 2.6.7.
Branch `class-ports` (worktree `mr-ports`), on top of the class-8/5/7 ports
(`9dd5f16`).

**Re-run of the committed Step-1 probes:** `probes/translation/06-class4-syntax-census`
and `probes/corpus/14-class4-answer-heads` regenerate byte-identical apart
from their date line (56 files / 2,073 census rules / AUTO 1,106 / MANUAL
967; 77 corpus files / 22,472 entries). Not re-committed.

**New probe:** `probes/translation/12-class4-syntax-census.{run,out}` — the
class-5 closure script (`10-class5-table-closure.py "4 "`) and a generator
dry run over the WHOLE class with `CLASS4_SUBSET` bypassed
(`12-class4-generator-dryrun.py`: the emitter's own errors, every G-9 risk
flag on a class-4 LHS or MatchQ pattern, the bare-`u_` records).

**Counts.** 56 files, **2,080 rules the generator's way** (the census's 2,073
+ the seven single-line ShowSteps wrappers; the file has 8
`LoadShowSteps` lines, one — 4.7.5 L75 — commented out). 102 tokens have
rows; 5 are emitter-dispatched (`Complex` 11 rules, `PolyQ` 3, `IGeQ` 2,
`Block` 1 — r71's, `Sum` 1); three head variables (`F` 23 uses, `G` 8,
`H` 2). Ten bare-`u_` records: the eight committed tail records plus
**4.7.5 r66** (`Int[u_,x] := Int[TrigSimplify[u],x] /; TrigSimplifyQ[u]`)
and **r70** (`Int[u_,x] := With[{v=ExpandTrig[u,x]}, Int[v,x] /; SumQ[v]] /;
Not[InertTrigFreeQ[u]]`) — the two the substrate left out; the tail grows
to ten class-4 records.

**UNLISTED — 11 tokens, all adjudicated:**

| token | rules | disposition |
|---|---:|---|
| `ExpandTrig` | 50 | Step-4 port (a): `ActivateTrig[ExpandIntegrand[u,x]]` and the 3-arg `With[{w=ExpandTrig[v,x], z=ActivateTrig[u]}, If[SumQ[w], Map[z*#&, w], z*w]]` (L3362-3370) |
| `KnownSineIntegrandQ` / `KnownSecantIntegrandQ` / `KnownTangentIntegrandQ` / `KnownCotangentIntegrandQ` | 22 / 22 / 8 / 8 | Step-4 port (a): the four wrappers over `KnownTrigIntegrandQ[list,u,x]` (L7368-7391, `u===1` or six MatchQ shapes with a `func_` head variable in the list) |
| `TrigQ` | 11 | table row: `%mr_trigQ` is ported (substrate); every use is `TrigQ[F]` on a head variable |
| `InertTrigQ` | 7 | table row: `%mr_inertTrigQ` is ported; every use is the 1-arg `InertTrigQ[F]` (no rule uses the 2/3-arg forms) |
| `ComplexFreeQ` | 3 | Step-4 port (a), 4.1.10 r9/r10/r11's `ComplexFreeQ[f]` (L226: atoms not ComplexNumberQ, else every part complex-free) |
| `Apart` | 2 | table row -> `expand`: both uses (4.1.7 r51/r64) are the ONE-argument `Apart[a*(1+Tan[e+f*x]^2)^2 + b*Tan[e+f*x]^4]^p` — a polynomial in Tan, on which Apart only expands; the value is what the rule needs (the factor cancels against `(Sec^2)^(2p)` by value) |
| `TrigSimplifyQ`, `TrigSimplify` | 1, 1 | Step-4 port (a) for 4.7.5 r66: `TrigSimplifyQ[u] := ActivateTrig[u]=!=TrigSimplify[u]`, `TrigSimplify[u] := ActivateTrig[TrigSimplifyRecur[u]]`, and TrigSimplifyAux's clauses as a generated rewrite table (the substrate's mechanism, `REWRITE_FUNCTIONS`) |

**G-9 risk flags — 24 (rule, flag) pairs over 21 rules, all to be ACCEPTED**
(Step 2, `ACCEPTED_RISKS`, the `rit` / 9.1 L15 precedents):

- `risk:Pi-arg:{sin,tan,csc}` (11): `sin[c_.+Pi/2+d_.*x_]`, `sin[e_.+k_.*Pi+f_.*x_]` —
  the INERT heads are user symbols with no definitions, so Mathematica's
  LHS evaluation leaves the Pi-shifted argument alone (the `rit` r1/r2
  argument); the reader emulates the Plus/Times evaluation itself.
- `risk:Pi-arg:{Sec,Csc}` (4.7.7 r19/r21): ACTIVE heads, but the shift is
  `k_.*Pi` with a PATTERN coefficient — Sec/Csc auto-evaluate only an
  explicit rational multiple of Pi, which a pattern is not (the class-8
  argument for `PolyLog[2, c_.*…]`).
- `risk:numeric-or-negated-arg:Complex` (11, incl. two MatchQ patterns
  `f1_.*Complex[0, j_]`): `Complex[0, fz_]` has a pattern argument, so it
  stays the unevaluated `Complex[0, fz_]` expression MR-MATCH matches against
  the converter's complex atoms (the 9.1 L15 precedent, spec G-3).

**Transitive closure (the CENSUS TRAP check).** 221 utilities reachable (71
rule-side, 150 transitive-only); by the probe's name test 85 table / 71
ported / 65 ABSENT. The substrate's three trap functions are now `table`
(`ReduceInertTrig`, `FixInertTrigFunction`, `UnifyInertTrigFunction` — the
generated rewrite tables). The 65 ABSENT:

1. **Rule-side (8):** the seven unlisted utilities above
   (`ComplexFreeQ`, `ExpandTrig`, `Known{Sine,Secant,Tangent,Cotangent}IntegrandQ`,
   `TrigSimplify(Q)`), which Step 4 ports.
2. **Reached through them (4):** `KnownTrigIntegrandQ`, `TrigSimplifyRecur`,
   `TrigSimplifyAux` — ported with their parents; `ComplexNumberQ` is
   ported (`%mr_complexNumberQ`).
3. **FunctionOfQ's HYPERBOLIC arms — NEEDED by class 4** (the carried item
   "hyperbolic branches of FunctionOfQ / SubstFor are not ported" becomes
   port work here): `FunctionOf{Sinh,Cosh,Tanh}Q`,
   `PureFunctionOf{Sinh,Cosh,Tanh,Coth}Q`, `OddHyperbolicPowerQ`, `ReapList`
   (FunctionOfTanhQ's helper), and `SubstForHyperbolic` (SubstFor's
   hyperbolic arm). 4.7.5 r5/r6/r9/r10/r15/r16/r19/r20/r27/r28/r31/r32/
   r37-r40/r43/r44 — 18 ACTIVE-hyperbolic derivative-divides records
   (`Int[u_*Cosh[c_.*(a_.+b_.*x_)],x] := … Subst[Int[SubstFor[1,
   Sinh[c(a+bx)]/d, u, x],x], x, Sinh[c(a+bx)]/d] /; FunctionOfQ[Sinh[…]/d,
   u, x, True]`) call `FunctionOfQ` and `SubstFor` with a hyperbolic `v`.
   Step-4 port (b).
4. **Named differently / inlined** (the class-5 reading):
   `PureFunctionOf{Sin,Cos,Tan,Cot}Q` = the generic `%mr_pureFunctionOfTrigQ`;
   `InverseTrigQ`/`InverseHyperbolicQ` inlined in `%mr_inverseFunctionQ`.
5. **The algebra substrate approximated since class 1** (the rest, 41 +
   `HeldFormQ`, `StopFunctionQ`, `Map2`, `RealNumberQ`,
   `SqrtNumber(Sum)Q`, `NthRoot`, `NormalizeHyperbolic`/`NormalizeTrig`
   inside SimpHelp): their parents (`Simp`, `Subst`, `ExpandIntegrand`,
   `SmartApart`, `ContentFactor`, `Rt`, `CalculusFreeQ`) are ported as
   wholes on Maxima's simplifier (house deviation). `SimplifyAntiderivative`
   (RectifyTangent/Cotangent) is class 5's finding 2 again: a discontinuous
   arctan in a class-4 answer is not rectified.

**Answer side: one new driver rewrite** (Step 7). `FresnelC(` / `FresnelS(`
are covered by the class-8 rows; `Si`/`Ci`/`Ei`/`GAMMA` by the class-2/3
rows. **`Hypergeometric2F1(a,b,c,z)`** (3 occurrences over 2 entries, both in 4.1.1.3) has no
row: the rules emit `hypergeometric([a,b],[c],z)` (the class-8 emitter
case), so the corpus text needs the same STRUCTURAL rewrite (a list
reshape, not a table row — `rewrite_structural`, the Derivative/Psi
precedent). All three entries also carry `AppellF1`, so they stay
unverifiable either way (the ceiling, 823 entries).
