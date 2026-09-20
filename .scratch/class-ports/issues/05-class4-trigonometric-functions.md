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
