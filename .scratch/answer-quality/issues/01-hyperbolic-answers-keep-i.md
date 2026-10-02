# Hyperbolic answers keep an %i: sin(%i*a + %i*b*x) is never folded back to %i*sinh(a + b*x)

Status: ready-for-agent
Type: answer quality (grade C, verdict unaffected) — section 6, ~1,850 entries
Filed: 2026-10-01

## Symptom

Section 6 (hyperbolic functions) grades **C on 1,854 of 5,080** rubi answers
(36.5 %; `test/corpus_class6.grade.out`, records `e5e8f37`). 1,847 of them have
the optimal's ExpnType, so the C is the grade's `%i` rule: the answer carries
`%i`, the optimal does not. The answers are correct (they verify); they are
the wrong shape.

```
∫ (c+d x) sinh(a+b x) dx
optimal  (c+d*x)*cosh(a+b*x)/b - d*sinh(a+b*x)/b^2                              leaf 28
rubi     -(%i*(-((d*sin(%i*b*x+%i*a))/b^2)-(%i*(-(d*x)-c)*cos(%i*b*x+%i*a))/b))  leaf 52, C

∫ 2/(-1+3 cosh(4+6x)) dx
optimal  1/3*atan(sqrt(2)*tanh(2+3*x))/sqrt(2)                                  leaf 22
rubi     -((%i*atanh(sqrt(2)*tan((6*%i*x+4*%i)/2)))/(3*sqrt(2)))                leaf 32, C
```

It is also most of where native Maxima grades better than rubi: of the 3,793
entries where integrate+risch out-grades rubi, 1,598 are in section 6
(`test/grade_report.out`).

## Mechanism

Rubi 4 has few hyperbolic rules of its own; it integrates them through the
trig rules, by the identity Sinh[z] = -I Sin[I z] (and its siblings).
Mathematica's evaluator folds the result back on its own:
`Sin[I a + I b x]` evaluates to `I Sinh[a + b x]`, and `I*I` multiplies out. Maxima's
simplifier folds `sin(%i*z)` to `%i*sinh(z)` only when the argument is a
**product** with `%i`. A **sum** whose every term carries `%i`
(`%i*b*x + %i*a`) is left alone, and so is an `%i` outside a sum of `%i` terms
(`-%i*(%i*X + %i*Y)`). Rubi's answer keeps the trig-of-imaginary form and its
`%i`.

## Prototype measurement

`probes/leaf-size/04-ifold-class6-sample.py` (`76d04af`) passes rubi's answer
through a prototype fold, bottom-up, answer only:

1. a trig / hyperbolic / inverse function `f(u)` with `u = %i*v`, `v` %i-free
   (`v = ratsimp(u/%i)`), is rebuilt as `f(%i*v)`, which Maxima's simplifier
   then folds (`sin(%i*v) -> %i*sinh(v)`, `atan(%i*v) -> %i*atanh(v)`, ...);
2. a sum whose every term is `%i` times an %i-free term is rebuilt as
   `%i*(sum of those terms)`.

On a seeded sample of **48 section-6 C entries: 39 -> A, 2 -> B, 7 stay C**;
every folded answer still verified or matched the expected answer (the one
`unverified` was unverified before). Extrapolated: ~1,500-1,700 entries out
of C, section 6 from ~50 % A to ~80 %.

The 7 that stay C have not been looked at. Example of a partial fold:
`csch(c+d*x)^4*(a+b*tanh(c+d*x)^3)` keeps `log(tan(%i*d*x+%i*c))`-type terms
whose `%i` cancel only across a log.

## Decision needed (why needs-triage)

**Where the fold lives.** Options:

- **(a) a final answer normalisation in `mr_top`** (`maxima_rubi_utils.mac`
  :266), at depth 0 only: the prototype as is. Cheapest. Changes every answer
  rubi returns that contains `%i`, in every section, not only 6. Needs a check
  that it never makes an answer worse (leaf size up, or verification lost)
  outside section 6.
- **(b) at the rule boundary**: wherever the port spells Rubi's
  hyperbolic -> trig conversion (find it: the section-6 files in the pinned
  Rubi are few, so the conversion is in a section-4 bridge or a utility),
  fold the result as Mathematica's evaluator would. Closer to Rubi; harder to
  find all the places.

Whichever is chosen, it must stay a simplification Mathematica's evaluator
does on its own (folding `I` out of a trig argument), not a new integration
step: the package's rule is Rubi's own rules, not extra machinery
([[no-default-integrate-fallthrough]] spirit).

## Acceptance

- Section 6 rubi arm re-run, graded: the C count falls by roughly the
  measured fraction; **0 PASS -> FAIL** against `test/corpus_class6.out`
  (`test/ab_records.py`).
- If option (a): every other section re-graded too, no entry's grade worse
  (A -> B/C, B -> C) attributable to the fold.
- Layer A unit targets for the fold (sum argument, nested `%i`, an inverse
  function, an answer without `%i` untouched, a CRE answer).
- The seven residual C's of the probe sample looked at and either folded or
  explained.

## Comments

### 2026-10-02 -- triage: option (a), measured; decided

**Where the conversion happens.** Rubi's `DeactivateTrigAux`
(`IntegrationUtilityFunctions.m:6198`; port `%mr_deactivateTrigAux`,
`maxima_rubi_utils.mac:6145`) rewrites `Sinh[u]` as `-I*sin[I*u]` and its
siblings. No Rubi rule or utility folds the `I` back out: `Simp`/`SimpHelp`
(`:2265`) keeps a trig argument as it is, and `SimpFixFactor` only pulls `I`
out of a power of a sum. The fold in Mathematica's output is its evaluator's,
wherever an expression is built -- so option (b) has no single boundary.

**Option (a) measured on every entry it can act on.** Probe
`probes/leaf-size/05-ifold-all-sections.py` (output `.out`): by the grade's
rule (`test/mr_grade.lisp:207`), an A/B answer carries `%i` only when its
optimal does, so the candidates are every C plus every A/B with `%i` in the
optimal -- 8,332 entries, sections 0-8. The fold is probe 04's `mr_ifold`, run
under `radexpand:false, logexpand:false`.

- Outside section 6: 5,918 candidates, 739 changed; C->A 343 (section 7:
  274), B->A 2, C->B 1; **no grade worse, 0 PASS lost**.
- Section 6: 2,414 candidates, 2,074 changed; C->A 1,511, C->B 60, B->A 10;
  **no grade worse**; 9 PASS lost (below). C 1,854 -> ~283.
- The fold costs 2-10 ms CPU.
- **The flags are required.** Folded under Maxima's defaults, the simplifier
  splits the folded powers -- `(-%i*y)^(2/3)` -> `-y^(2/3)`, wrong on the
  principal branch -- and the first run of the probe (not kept) had wrong
  answers and one A->B. `MR_IFOLD_FLAGS=default` reproduces it.

**The 9 PASS -> unverified** (6.4.2 e14/e22/e26/e47, 6.7.1
e57/e58/e64/e65/e66; cube roots of cot/sin of an imaginary argument) are the
checker's, not the fold's: their original answers already mismatch in the
numeric check and pass only by the symbolic chainA.1, which times out on the
folded shape. Probe `probes/leaf-size/06-ifold-principal-branch.py`
evaluates both answers and the integrand with principal-branch complex
arithmetic (cmath): R0 = R1 at all 27 points, and both differentiate to the
integrand (worst 8.4e-9).

**Decision (user, 2026-10-02):** option (a) -- the depth-0 fold in `mr_top`,
under `radexpand:false, logexpand:false`. The 9 entries above are accepted as
attributed checker artefacts: the acceptance's 0 PASS -> FAIL excludes exactly
them.

