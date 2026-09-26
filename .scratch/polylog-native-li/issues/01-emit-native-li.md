# Emit Maxima's native polylogarithm `li[s](z)` instead of the unknown `polylog(s, z)`

Status: resolved (merged to master and records promoted, 2026-09-26)
Type: task (generator + driver + tests; full-corpus A/B)
Filed: 2026-09-26 (user request: make it a todo with enough information to pick it up later)
Supersedes: `.scratch/class3-polylog-ceiling/issues/01-polylog-derivative-shim.md`. Maxima
already differentiates `li`, so no shim is needed.

## The problem

Maxima has no function called `polylog`. Its polylogarithm is the subscripted function
`li[s](z)` (manual: `describe("li", exact)`). The generator translates Rubi's `PolyLog[s, z]` to
`polylog(s, z)` (`generator/translation_table.py`, the `"PolyLog": "polylog"` row and its
comment), because the corpus's expected answers spell it that way. To Maxima that is an unknown
operator, so:

- **In a user's session** an answer containing `polylog` is a dead end. It cannot be
  differentiated, evaluated numerically or simplified.
- **In the harness** a `polylog` answer passes only when its polylog terms are form-identical to
  the corpus answer, so they cancel before the diff. The self-diff and numeric stages of the zero
  chain can never close it. Measured below: of the entries whose expected answer contains
  `polylog`, **none is `verified`; every PASS is `expected`**.

## Measured (2026-09-26, build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7)

Native `li`, probed at the Maxima prompt:

| expression | result |
|---|---|
| `li[1](z)` | `-log(1-z)` (simplifies eagerly) |
| `li[2](1)`, `li[2](-1)`, `li[2](0)`, `li[3](1)` | `%pi^2/6`, `-%pi^2/12`, `0`, `zeta(3)` |
| `diff(li[s](z^2), z)` | `2*li[s-1](z^2)/z` (symbolic order works) |
| `diff(li[2](a*x+b), x)` | `-a*log(-a*x-b+1)/(a*x+b)` (chain rule) |
| `float(li[2](-2.5))`, `float(li[2](2.5))` | `-1.6989…`, `2.4208… - 2.8786…*%i` |
| `float(li[4](0.3))`, `float(li[s](0.3))` | `0.30599…`, stays `li[s](0.3)` |
| `li[2](x) - li[2](x)` | `0` |
| `op(li[2](x))`, `args(li[2](x))` | `li[2]`, `[x]` |

The unknown name, by contrast: `diff(polylog(2, x^2), x)` stays a noun, and
`float(polylog(2, 0.5))` stays `polylog(2.0, 0.5)`.

The rule side (rule files on master `82ca6ab`):

| class | `polylog(` emitted in rule bodies | rule files with `PolyLog` in a PATTERN |
|---|---:|---|
| 3 | 37 | 3_1_5, 3_2_3, 3_3 |
| 5 | 44 | 5_3_4 |
| 7 | 48 | 7_3_4 |
| 8 | 42 | 8_8 |

There are 42 `%mr_defrule` pattern strings with `PolyLog` on their left-hand side; classes 1, 2,
4, 6 and 9 emit none. `maxima_rubi_utils.mac` names `polylog` in the scan/inverse-function
helpers (~L2724, ~L7965–7980).

The corpus side (entries per class, verdicts from the promoted records `test/corpus_class<N>.out`):

| class | integrand has `polylog(` | expected answer has `polylog(` | of those FAIL | verdicts of those |
|---|---:|---:|---:|---|
| 2 | 0 | 67 | 12 | expected 55, deferred 8, unverified 3, contains-noun 1 |
| 3 | 26 | 1,194 | 365 | expected 827, contains-noun 213, timeout 75, unverified 57, deferred 19 |
| 4 | 0 | 456 | 234 | expected 222, contains-noun 172, timeout 49, error 7, unverified 6 |
| 5 | 0 | 1,112 | 424 | expected 688, contains-noun 258, timeout 107, unverified 44, deferred 14 |
| 6 | 0 | 476 | 234 | expected 242, contains-noun 153, deferred 38, timeout 30, unverified 9 |
| 7 | 0 | 1,125 | 419 | expected 706, contains-noun 259, unverified 88, timeout 66, deferred 6 |
| 8 | 198 | 197 | 145 | contains-noun 131, expected 41, no-answer 11, unverified 11, timeout 2 |

The **218 `unverified`** entries are the direct candidates. Their answers may be correct in a
different form from Rubi's; today nothing can differentiate them. The `contains-noun` and
`timeout` masses are other problems (`.scratch/corpus-harness/issues/05`, ticket 21), not this
one.

## What already exists

The matcher's tree converter already knows both spellings (`maxima_rubi_tree.lisp` ~L45–60):

- `+subscripted+` maps `("PolyLog" maxima::$li)`: `li[n](x)`, an `mqapply` of the array op, is
  read as `(PolyLog n x)` and written back as `li[n](x)`.
- `+read-only-functions+` holds `("PolyLog" 2 "polylog")`: `polylog(n, x)` is also READ as
  PolyLog, but never written back.

So a `PolyLog` pattern should already match a `li[s](z)` integrand. **Verify that first** with a
unit check in `test/matcher/test_mr_tree.mac`, then with one 8.8 rule end to end.

`test/corpus_driver.py` (~L129–137) records why there is no `polylog(` rewrite row today: the
corpus is already "natively spelled" in the old sense. That reasoning is what changes here.

## The work

1. **Generator.** Emit `li[s](z)` for `PolyLog[s, z]`. This is a structural emission, not a
   plain rename: the first argument becomes the subscript. Look at how class 8's
   `Derivative[n][f][x]` got its own emitter (commit `2424269`, `%mr_derivative`); a
   `%mr_polylog(s, z)` helper that returns `li[s](z)` (subscripted-function call via
   `arraymake`/`funmake`) may be simpler than emitting the subscripted syntax in text. A
   3-argument `PolyLog[n, p, z]` (Nielsen polylog) is not a Maxima function. Check whether any
   rule emits one, and keep it as a noun if so.
2. **The P3 static gate** (`test/check_generated_rules.py`) needs a new closed exception: undo
   `li[s](z)` (or `%mr_polylog(s, z)`) back to `polylog(s, z)`, with the class-3 site count
   pinned. Model it on `undo_native_heads` / `undo_expand2`.
3. **Corpus driver.** Add a structural rewrite `polylog(A, B)` -> `li[A](B)` in
   `rewrite_structural` (next to class 8's `Derivative(A)(B)(C)`), applied to the integrand and
   to the expected answers, with unit checks in `test/test_head_rewrites.py`. The "no-op for
   earlier classes" check does not apply: classes 2–8 are all affected. A/B them all.
4. **Utils.** Re-read the `polylog` mentions in `maxima_rubi_utils.mac` (the inverse-function /
   scan helpers). They must recognise the `li[s]` operator: `op(li[2](x))` is `li[2]`, a
   subscripted op, not a symbol.
5. **Eager simplification.** `li[1](z)` becomes `-log(1-z)` at once, and special values
   evaluate (`li[2](1) = %pi^2/6`). That is mathematically right, but a rule that emits
   `PolyLog[1, …]` or recurses on a PolyLog integrand may now see a `log` instead and take
   another route. Watch the A/B for such routes.
6. **Measure.** Full-corpus run of classes 2, 3, 4, 5, 6, 7, 8 against the promoted records
   (`test/run_corpus_queue.py`, 24 workers, `ab_records.py`). Expect `unverified` -> `verified`
   gains among the 218 and some `expected` -> `verified` moves: an answer can stop being
   form-identical once the corpus text is `li` too, but it then verifies by differentiation.
   Attribute every PASS->FAIL, as for the class-ports merge
   (`probes/class-ports/final/attribution.py` is the template).
7. Close `.scratch/class3-polylog-ceiling/issues/01` as superseded, and update the README's
   answer-spelling list (`polylog` -> `li[s](z)`).

## Addenda (2026-09-26, probed before starting)

- **`part(u, 1)` changes meaning.** Rubi's `InverseFunctionOfLinear` tests `LinearQ[u[[1]], x]`;
  for `PolyLog[n, z]` that is the ORDER `n`, and `%mr_inverseFunctionOfLinear`
  (`maxima_rubi_utils.mac` ~L7970) ports it as `part(u, 1)`. On `li[n](a*x+b)` with
  `inflag:true`, `part(e, 1)` is `a*x+b` (the order lives in the operator `li[n]`). The helpers
  must special-case the `li` operator to keep Rubi's reading, not just rename the head.
- **Eager simplification reaches further than `li[1]`:** `li[0](x) = x/(1-x)`,
  `li[-1](x) = x/(1-x)^2`. A rule that emits order <= 1 yields a rational function or a log.
- **`subst` into the subscript works and re-simplifies:** `subst(n=2, li[n](z))` is `li[2](z)`,
  `subst(n=1, …)` is `-log(1-z)`; a function `f(k,z) := li[k](z)` behaves the same. Plain text
  emission of `li[n](z)` is viable; a helper is optional.
- **No 3-argument PolyLog** anywhere in `reference/rubi` (271 `PolyLog[` sites) or in the
  rule files: the Nielsen caveat in step 1 is moot.
- `li[2](z)` is complex for real z > 1, so a numeric check at a branch-sensitive point can
  disagree with a correct answer. Watch for it in the A/B.
- The sibling unknown heads (AppellF1, Hurwitz Zeta, psi[-2]) are
  `.scratch/unknown-special-heads/issues/01`.

## Gates

Everything in AGENTS.md `## Tests`: Layer A, rule-table order, section-9 e2e, the three matcher
suites, P3, generator section-9 unit, run-records, the harness guards (head rewrites),
regeneration byte-identical for classes 1–9, the matcher regression suite (both arms; mr-tree may
change).

## Results (2026-09-26, branch `polylog-native-li`, core fingerprint `4ba2b5813ba5c4288585c104a4bbf802`, build `branch_5_50_base_84_g4204fb669`)

Steps 1-4 and 7 done (commits `39e1fe7`, `471aaad`); step 5 watched in the A/B; step 6 below.

Full corpus, classes 2-8, queue runner, 24 workers, 30 s cpu cap (`test/polylog_li_measure.sh`,
log `test/polylog_li_measure.log`), each A/B'd against the promoted record
`test/corpus_class<N>.out` (`test/li_ab_class<N>.out`):

| class | PASS before -> after | PASS->FAIL | FAIL->PASS |
|---|---|---:|---:|
| 2 | 863 -> 866 | 0 | 3 |
| 3 | 2,446 -> 2,550 | 0 | 104 |
| 4 | 19,932 -> 19,955 | 23 | 46 |
| 5 | 3,629 -> 3,754 | 1 | 126 |
| 6 | 4,314 -> 4,343 | 6 | 35 |
| 7 | 5,342 -> 5,485 | 0 | 143 |
| 8 | 1,537 -> 1,676 | 1 | 140 |
| **all** | **38,063 -> 38,629 (+566)** | **31** | **597** |

Split by whether the corpus entry carries `polylog(` (`probes/polylog-native-li/01-transitions.out`):
the 4,629 polylog entries go 2,781 -> 3,371 PASS (+590; 2 PASS->FAIL), and **2,518 of their
`expected` (form-identical) PASSes become `verified`**: they now close by differentiation. The
40,059 other entries go 32,777 -> 32,753 (29 PASS->FAIL, 5 FAIL->PASS).

**PASS->FAIL attribution (31).** Every one was re-run on the same core at 12 workers
(`test/corpus_class<N>.li.recheck/`):

- **30 are cap-boundary noise**: old times 22.4-30.0 s (28 of them >= 28.8 s), new `timeout`
  at 30.0-30.1 s; all 30 PASS on the re-check (class 4: 23 verified, max 20.3 s; class 6: 4
  expected + 2 verified; class 5: 1 expected).
- **1 is real, and it is the step-5 eager simplification:** 8.8 e155,
  `polylog(-2, e*((a+b*x)/(c+d*x))^n)/((a+b*x)*(c+d*x))`. `li[-2](z)` simplifies on input
  to the rational `z*(1+z)/(1-z)^3`, so no 8.8 PolyLog rule sees it; the rational route
  times out at 30 s and at a 300 s cap ends `contains-noun` (84 s). It was `expected` only
  because the unknown `polylog(-2, …)` stayed a PolyLog. The sibling low orders do NOT
  regress: e152 (order 1), e153 (0) expected -> verified, e154 (-1) unverified -> verified.
  This is what a Maxima user typing `li[-2](…)` gets anyway; recovering it would mean
  recognising the rational form, i.e. new work, not part of this ticket.

Gates on the branch: Layer A 1591/0, rule-table order 18/0, section-9 e2e 9/0, mr-match 57/0,
mr-tree 88/0, dispatch 128/0, P3 30/0, generator section-9 28/0, run-records 43/0, harness
guards all green (head rewrites 70/0), regeneration byte-identical for classes 1-9 and
`--rewrites`, matcher regression suite 109/0 in both arms (records unchanged but for the
timing lines).

Merged to `master` and the `.li.out` records promoted as the baselines
`test/corpus_class<N>.out` for classes 2-8 (user decision, 2026-09-26). Class 1 carries no
PolyLog and keeps its record. 8.8 e155 is accepted as the one regression.
