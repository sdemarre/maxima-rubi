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
