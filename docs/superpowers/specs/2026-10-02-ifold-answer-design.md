# The %i fold of rubi's answer — design

Date: 2026-10-02. Ticket: `.scratch/answer-quality/issues/01-hyperbolic-answers-keep-i.md`
(ready-for-agent; decision recorded in its 2026-10-02 comment).
Evidence: `probes/leaf-size/04-ifold-class6-sample.py`, `05-ifold-all-sections.py`,
`06-ifold-principal-branch.py` (outputs beside them), build
`branch_5_50_base_84_g4204fb669`.

## 1. Goal

Rubi's answers keep the shape Rubi 4's hyperbolic -> trig route leaves them in:
`-%i*(... sin(%i*b*x+%i*a) ...)` where Mathematica's Rubi answers
`... sinh(a+b*x) ...`. They are correct (they verify) but grade C under the
grade's `%i` rule: section 6 grades C on 1,854 of 5,080 answers.

The fold rewrites rubi's **final answer** the way Mathematica's evaluator
canonicalises `Sin[I a + I b x]` to `I Sinh[a + b x]`. It is a simplification of
the answer, not an integration step (the package's rule is Rubi's own rules —
the spirit of the no-default-integrate decision).

### Why the answer, and not the rules

Rubi's `DeactivateTrigAux` (`IntegrationUtilityFunctions.m:6198`; port
`%mr_deactivateTrigAux`, `maxima_rubi_utils.mac:6145`) rewrites `Sinh[u]` as
`-I*sin[I*u]` and its siblings. No Rubi rule or utility folds the `I` back out
(`Simp`/`SimpHelp`, `:2265`, keeps a trig argument as is; `SimpFixFactor` only
pulls `I` out of a power of a sum): Mathematica's evaluator does it, wherever an
expression is built. There is no single rule boundary to fold at, and folding
intermediate integrands would change which rules match. User decision
2026-10-02: option (a), the depth-0 answer fold in `mr_top`.

### Measured (probe 05, every entry the fold can act on)

By the grade's rule (`test/mr_grade.lisp:207`) an A/B answer carries `%i` only
when its optimal does, so the candidates are every C plus every A/B whose
optimal holds `%i`: 8,332 entries, sections 0-8, the fold under
`radexpand:false, logexpand:false`:

| | outside section 6 | section 6 |
|---|---|---|
| candidates / changed | 5,918 / 739 | 2,414 / 2,074 |
| C->A, C->B, B->A | 343, 1, 2 | 1,511, 60, 10 |
| grade worse | 0 | 0 |
| PASS lost | 0 | 9 |

The 9 (6.4.2 e14/e22/e26/e47, 6.7.1 e57/e58/e64/e65/e66) are the checker's:
their original answers already mismatch in the numeric check and pass only by
the symbolic `chainA.1`, which times out on the folded shape; with
principal-branch arithmetic both answers are equal at every point and both
differentiate to the integrand (probe 06). User decision 2026-10-02: accepted
as attributed.

**The flags are part of the fold.** Under Maxima's default `radexpand:true` the
simplifier splits the folded powers — `(-%i*y)^(2/3)` -> `-y^(2/3)`, wrong on
the principal branch — and the fold produced wrong answers
(`MR_IFOLD_FLAGS=default` of probe 05).

## 2. The component: `%mr_ifold(e)`

In `maxima_rubi_utils.mac`, beside `mr_top`. Bottom-up over `e`:

1. **Fast path** — `freeof(%i, e)`: return `e` itself. A `%i`-free answer,
   CRE included, is untouched (the prototype disreps any CRE it walks:
   `rat(x^2/2+x)` came back `(x^2+2*x)/2`).
2. **Opaque nouns** — an expression whose operator is the `integrate` noun or
   `unintegrable` is returned as is, at any depth. The prototype folds inside
   them (`'integrate(sin(%i*x+%i*a),x)` -> `%i*'integrate(sinh(x+a),x)`), which
   would change the top-level no-answer noun's operator, the one the corpus
   driver's `deferred` test reads, and would rewrite an integrand that is not an
   answer.
3. **The fold** — probe 04's two rules, unchanged:
   - a trig / hyperbolic / inverse-trig / inverse-hyperbolic function `f(u)`
     (the 24 heads of the prototype) with `u` not `%i`-free and
     `v = ratsimp(u/%i)` `%i`-free is rebuilt as `f(%i*v)`, which Maxima's
     simplifier folds (`sin(%i*v)` -> `%i*sinh(v)`, `acot(%i*v)` ->
     `-%i*acoth(v)`, ...);
   - a sum whose every term divided by `%i` is `%i`-free is rebuilt as
     `%i*(the sum of those quotients)`, so `-%i*(%i*X + %i*Y)` multiplies out.
   Anything else is rebuilt from its folded arguments.

The guards only narrow what the fold touches: the fast path changes nothing
on an answer with `%i`, and the noun guard only differs from the prototype on
an answer that carries an `integrate`/`unintegrable` noun — no-answer and F
entries were not probe 05's candidates; an A/B/C answer with an interior
`integrate` term (legitimate, e.g. 1.2.2.7 e1) is rare, and the acceptance
re-run (section 5) measures the shipped fold either way.

The function binds nothing itself; its caller supplies the flags (section 3).

## 3. Placement and switch

- **Switch**: `defmvar $mr_ifold t` in `maxima_rubi_dispatch.lisp` with the
  other run switches. Added to `test/run_records.py` (SWITCHES and the
  defaults), so the corpus driver assigns it in every entry text and every
  record's `filter:` line states it; `test/test_run_records.py` updated.
  `mr_ifold : false` reproduces today's answers byte for byte.
- **Call site**: `%mr_top_final(ans)` applies the fold when `mr_ifold` is
  true, as `block([radexpand : false, logexpand : false], %mr_ifold(ans))`,
  inside `errcatch` — on an error the unfolded `ans` is returned, so the fold
  can never cost an answer. The flags are bound unconditionally, independent of
  `mr_model_flags`: without them the fold is unsound, so they belong to the
  fold, not to a run option.
- **Depth 0 only**: `mr_top` records whether it was entered at
  `depth_level = 0` (the `rubi` / `rubi_fallback` top-level call) before
  running the body, and only then passes the answer through `%mr_top_final`.
  A nested `mr_int` call is never folded: its result is an intermediate the
  enclosing rule keeps building on.
- **Verbose**: under `rubi_verbose : matches` the top-level call answers
  `[answer, steps]`; the fold applies to `answer` only. The steps keep what the
  rules produced.

## 4. Testing

Test-first, in Layer A (`test_maxima_rubi.mac`), a new section:

- the sum argument: `sin(%i*b*x+%i*a)` -> `%i*sinh(b*x+a)`, `cos` -> `cosh`;
- the outer `%i`: `-%i*(%i*X + %i*Y)` -> `X + Y`;
- nested `%i` (a folded function inside a folded sum);
- an inverse function: `atan(%i*x+%i*a)` -> `%i*atanh(x+a)`,
  `acot` -> `-%i*acoth`;
- untouched: a `%i`-free answer is returned identical (`is(r = e)`); a
  `%i`-free CRE answer is still CRE; the `unintegrable` and `integrate` nouns,
  at top level and inside a sum, keep their integrand;
- the flag witness: `(%i*cot(%i*z))^(1/3)`-type answers (6.4.2 e14's shape)
  fold without the `-y^(2/3)` split even when the global `radexpand` is true;
- the error fallback: a fold that errors returns the unfolded answer;
- the switch: `mr_ifold : false` answers today's form; `true` folds at depth 0
  and never in a nested call; the verbose `[answer, steps]` answer folds the
  answer and keeps the steps;
- end to end: one section-6 integral through `rubi` answers `sinh`/`cosh`
  without `%i` and verifies.

The other gates stay green: the rule-table order gate, the section-9 e2e gate,
the dispatch suite, `test/test_run_records.py` and the harness guards listed in
AGENTS.md.

## 5. Acceptance

A full rubi-arm re-run of sections 0-8 with the queue runner (24 workers,
detached, the follow-up merges and censuses chained in the same script), each
section graded (user decision 2026-10-02):

- `test/ab_records.py <old> <new>` per section: **0 PASS -> FAIL**, except the
  9 attributed section-6 entries; every other transition attributed;
- the grade census per section: **no entry's grade worse** because of the
  fold (A->B/C, B->C), checked entry by entry against the old `.grade.out`;
  section 6's C count down to about 280;
- the new records become the canonical `test/corpus_classN.out` (+ `.proof.out`,
  `.grade.out`); `test/grade_report.out` regenerated and
  `docs/grading-and-leaf-size.md` updated with the new figures;
- AGENTS.md: Layer A's and `test_run_records`' new counts, `mr_ifold` in the
  switch list;
- the ticket closed; a follow-up ticket for the C's that remain (probe 05's
  section-6 C->C, 222 entries, e.g. 6.3.7 e56's `%i` that cancels only across a
  `log`).

## 6. Out of scope

- The remaining C's (the follow-up ticket above).
- Folding intermediate integrands (section 1: it changes rule matching).
- The checker's numeric evaluation of fractional powers of imaginary products
  (the cause of the 9; a separate corpus-harness ticket if wanted).
- The baseline arm (native `integrate`/`risch`): unchanged, not re-run.
