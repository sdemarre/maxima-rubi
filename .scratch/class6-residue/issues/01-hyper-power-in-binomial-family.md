# Class-6 residue: the `.7` family reaches no rule at all — 1,173 entries

Status: open
Type: task (rule coverage)
Filed: 2026-09-20 (class-6 Step-10 close)

## Scope

Six corpus files defer at ~100 %:

| corpus file | N | FAIL | dominant |
|---|---:|---:|---|
| 6.1.7 `hyper^m (a+b sinh^n)^p` | 525 | 525 (100 %) | deferred 521 |
| 6.3.7 `(d hyper)^m (a+b (c tanh)^n)^p` | 263 | 263 (100 %) | deferred 262 |
| 6.5.7 `(d hyper)^m (a+b (c sech)^n)^p` | 220 | 220 (100 %) | deferred 219 |
| 6.2.7 `hyper^m (a+b cosh^n)^p` | 85 | 85 (100 %) | deferred 85 |
| 6.4.7 `(d hyper)^m (a+b (c coth)^n)^p` | 53 | 53 (100 %) | deferred 53 |
| 6.6.7 `(d hyper)^m (a+b (c csch)^n)^p` | 27 | 27 (100 %) | deferred 26 |
| **total** | **1173** | **1173** | |

**23 % of the section and 37 % of all its `deferred`.** These are the
single largest recoverable block in class 6 and the first thing to look
at for an uplift.

## What is already known

- **NOT an unloaded-file artifact.** The pinned clone has exactly 13
  section-6 `.m` files and all 13 are generated and loaded
  (`docs/corpus-class6-baseline-uplift.md` §1). Nothing was skipped.
- The shape is a power of one hyperbolic inside a binomial of another.
- **Likely cause, stated as a GUESS:** Rubi reaches these through
  machinery outside section 6 — substitution into the algebraic or trig
  sections — which this port has not yet ported. Not verified.

## First moves

1. Take ~5 entries from 6.1.7 and trace what Rubi 4 actually does with
   them (which rule fires, in which section). That decides whether this
   is a section-6 gap or a cross-section dependency.
2. If it is a cross-section dependency on class 4 (trig), it is a reason
   to sequence class 4 earlier than its corpus size alone suggests.

## Why it matters beyond class 6

If the answer is "hyperbolic integrands are reached through the trig
rules", the same will hold for class 7 (inverse hyperbolic, 6,552
entries) against class 5 (inverse trig), and the porting ORDER should
be reconsidered on that basis.

## ANSWERED — 2026-09-20: the inert-trig bridge, section 4

Probe `probes/rubi/02-hyperbolic-inert-trig-bridge.{py,run,out}` (static
analysis over the pinned clones + `test/corpus_class6.out`; no Maxima). The
guess in this ticket — "likely a cross-section dependency ... presumably
through the algebraic or trig sections" — is **confirmed as trig**, and the
mechanism is exact:

1. Rubi has **six inert function heads and they are all trig** (measured:
   `sin[` 1518, `csc[` 940, `tan[` 640, `cos[` 551, `sec[` 225, `cot[` 133;
   `sinh[`/`cosh[`/`tanh[`/`coth[`/`sech[`/`csch[` **0**). The `.7` rules are
   written against those inert heads.
2. `DeactivateTrigAux`'s `HyperbolicQ[u]` branch
   (`IntegrationUtilityFunctions.m:6210-6218`) carries all six hyperbolic
   heads onto the inert TRIG heads by the imaginary-argument identities:
   `Sinh -> -I sin[I z]`, `Cosh -> cos[I z]`, `Tanh -> -I tan[I z]`,
   `Coth -> I cot[I z]`, `Sech -> sec[I z]`, `Csch -> I csc[I z]`.
3. The conversion is invoked by **exactly one rule**, at the head of
   `4.1.0.1 (a sin)^m (b trg)^n.m`:
   `Int[u_, x_Symbol] := Int[DeactivateTrig[u, x], x] /; FunctionOfTrigOfLinearQ[u, x]`
4. Rubi has **no** `(a + b Sinh[..]^n)^p` rule anywhere (measured: zero
   matches across all 221 rule files), and no section-6 rule file for the `.7`
   shape. The only `.7` files with inert heads are `4.1.7` (73 rules),
   `4.3.7` (25) and `4.5.7` (32) — all in section 4.

So the 1,173 entries are not an unloaded file and not a missing hyperbolic
rule: **the rules that answer them are section 4's**, and the hyperbolic side
reaches them through the bridge.

Size, re-measured from the record: `.7` is **1,173 entries, 1,166 deferred =
36.7 % of class 6's 3,173 deferred, with not one PASS** (7 `contains-noun`).

**The unlock is real but not free.** Porting class 4's rule files alone does
not deliver it — the bridge substrate has to come too. See
`.scratch/class-ports/issues/05` for the list and the census trap.

Separate, still open: the seven `Hyperbolic <fn> functions` / `6.7.1`
miscellany files are a **further 1,480 deferred entries** and also have no
section-6 rule file. Whether they ride the same bridge is not answered here.
Together with `.7` that is 83 % of class 6's deferred mass, which is why the
question is worth its own probe.

## ANSWERED — 2026-09-21: the miscellany files ride the SAME bridge (91.4 %)

The paragraph above left one question open: "whether they ride the same bridge
is not answered here". Probe
`probes/rubi/03-hyperbolic-miscellany-bridge.{py,run,out}` answers it.

**Method.** The bridge's admission condition is not a guess — it is
`FunctionOfTrigOfLinearQ[u,x]` (`IntegrationUtilityFunctions.m:4358-4361`).
The probe ports its **branch 2** (`FunctionOfTrig` 4365-4392 +
`AlgebraicTrigFunctionQ` 4396-4407, `LinearQ = PolyQ[u,x,1]` 1373-1376) to
Maxima clause for clause and runs it over all 5,080 class-6 corpus integrands,
joined entry-for-entry to `test/corpus_class6.out` (5,080/5,080 joined). Maxima
is the parser and expression walker only: no rule files, no integration.
Branch 1 is a Mathematica `MatchQ` with four `Optional` defaults and is NOT
ported, so every "admitted" count here is a **lower bound**.

**Controls — both hold**, which is what makes the rest readable:

| control | expectation | measured |
|---|---|---|
| `.7` family (probe 02: rides the bridge) | high | **1166 / 1166 = 100.0 %** |
| `(e x)^m (a+b hyper(c+d x^n))^p` (bare x, nonlinear arg) | low | **0 / 12 = 0.0 %** |

**The answer.** The seven miscellany files carry **1,480 deferred** entries;
**1,352 (91.4 %) are admitted by the bridge**, so after `DeactivateTrig` they
are section-4 problems on the same route as `.7`. The 128 rejects are
`non-algebraic` 57 (log / exp / non-trig factors) and `bare-x-or-angle` 71.

**A third family falls out of the same table.** `6.x.1 (c+d x)^m (a+b hyper)^n`
is 461 deferred, of which 60 are branch-2 admitted and **394 more carry branch
1's exact shape** — branch 1 being the one branch that admits a polynomial
factor. 454 of 461.

**Total: 2,972 of class 6's 3,173 deferred entries — 93.7 % — turn on the one
bridge rule** at the head of `4.1.0.1`.

**What this does NOT say.** That the bridge ADMITS an entry is not that section
4 ANSWERS it; that depends on section 4's rule files covering the shape, which
is what the class-4 port measures. Do not conflate the two in a planning
number.

Three defects were found and fixed while porting the condition, each of which
had produced plausible-but-wrong numbers; they are recorded in the probe's
`SELFTEST` (23 cases, run first, a single miss aborts the probe): a Maxima
`for` variable named `a` **captured the corpus's own `a`**; `op` reports the
DISPLAY form so `2/(...)` has head `/` (fixed with `inflag:true`); and
`is(equal(b,0))` is `unknown` for a free symbol, so `mr_linq` returned neither
true nor false and every downstream `if` silently took its else arm.
