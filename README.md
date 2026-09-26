# maxima-rubi

A rule-based symbolic integration package for Maxima, in the spirit of
[Rubi](https://github.com/RuleBasedIntegration/Rubi). Rubi 4's integration
rules are ported as declarative rule records and executed by a Lisp pattern
matcher and a first-match-wins dispatcher. The Rubi Maxima-syntax test corpus
(70,385 integrals) is the yardstick.

All eight rule classes of Rubi 4 are ported: algebraic, exponential,
logarithmic, trigonometric, inverse trigonometric, hyperbolic, inverse
hyperbolic and special functions, plus Rubi's section-9 utility rules. That is
7,776 rules.

## Quick start

The fastest way in is the prebuilt rules core: an SBCL image with Maxima and
all 7,776 rules already loaded, which starts in under a second.

```sh
sh test/build_rules_core.sh        # (re)build test/mr_rules.core, a few seconds
rlwrap sbcl --tls-limit 100000 --core test/mr_rules.core --noinform
```

That gives an ordinary Maxima prompt (`rlwrap` is optional; it adds line
editing):

```maxima
rubi(sec(x)^3, x);                            /* atanh(sin(x))/2 + sec(x)^2*sin(x)/2 */
r : rubi(x^3/sqrt(a+b*x^2), x)$
ratsimp(diff(r, x) - x^3/sqrt(a+b*x^2));      /* 0 */
```

The core is built from the files on disk. Rebuild it after pulling or after
changing any rule or package file.

Without the core, from a plain Maxima started in the package directory (about
4 s to load):

```maxima
load("maxima_rubi.mac")$
mr_load_all()$
rubi(sec(x)^3, x);
```

`load("maxima_rubi.mac")` must be able to find its siblings, by one of four
routes: load it by full path, start Maxima in the package directory, push the
package directory onto `file_search_maxima`, or install it under `~/.maxima/`.
Every sibling load is witness-checked, so a missed or truncated file fails
loudly at load time and names the four options. The eager load is small (the
support layer and the five 1.1.1.1 rules); `mr_load_all()` loads the full
table, in Rubi's `LoadRules` order, which is rule priority here.

### Examples native `integrate` does not do

Each of these comes back unevaluated from Maxima's `integrate` and is answered
by `rubi` in about a second or less:

```maxima
rubi(1/(x^8+1), x);                         /* logs and atans with nested radicals */
rubi(sqrt(x^4+1), x);                       /* an elliptic_f term */
rubi(x/(%e^(2*x)+%e^x-1), x);               /* li[2](...) terms */
rubi(x/(%e^(2*x)+3*%e^x+3), x);             /* li[2](...) terms */
rubi(log(x^2/(x^2+1))/(x^2+1), x);          /* li[2](...) terms */
rubi(1/(x*log(7*x)^2+x*log(7*x)+x), x);     /* 2*atan((2*log(7*x)+1)/sqrt(3))/sqrt(3) */
rubi(1/(sin(x)^4+1), x);
rubi(cos(x)*sec(4*x), x);
rubi(asin(sqrt(x))/x, x);
rubi((x*acot(x))/(x^2+1), x);
rubi(1/(cosh(x)^4+1), x);
rubi(tanh(8*x)^(1/3), x);
rubi(asinh(sqrt(x))/x, x);
rubi(x/(sqrt(x^2+1)*asinh(x)), x);          /* expintegral_shi(asinh(x)) */
rubi(expintegral_si(2*x)*sin(5*x), x);
rubi(li[2](1+x)/(2+x), x);                  /* li[2] and li[3] terms */
```

Every answer is checked symbolically: the residual `diff(r, x) - f` reduces to
exactly `0` by the chain below, with no numeric evaluation. Compute the answer
in one statement and verify it in a later one (see the note after the table).

| integrand | reduces `diff(r, x) - f` to 0 |
|---|---|
| `1/(x^8+1)`, `x/(%e^(2*x)+%e^x-1)`, `x/(%e^(2*x)+3*%e^x+3)`, `log(x^2/(x^2+1))/(x^2+1)`, `1/(x*log(7*x)^2+x*log(7*x)+x)`, `(x*acot(x))/(x^2+1)`, `x/(sqrt(x^2+1)*asinh(x))`, `li[2](1+x)/(2+x)` | `radcan(d)` |
| `sqrt(x^4+1)` | `radcan(trigexpand(d))` |
| `cos(x)*sec(4*x)`, `1/(cosh(x)^4+1)`, `expintegral_si(2*x)*sin(5*x)` | `radcan(exponentialize(d))` |
| `1/(sin(x)^4+1)` | Weierstrass: `radcan(trigsimp(trigexpand(subst(x = 2*atan(t), d))))` |
| `tanh(8*x)^(1/3)` | `ratsimp(subst(tanh(8*x) = u^3, subst(sech(8*x) = sqrt(1-tanh(8*x)^2), d)))`: only `sech^2` occurs, and the result is a rational function of `u` |
| `asin(sqrt(x))/x` | `exp(i asin y) = sqrt(1-y^2) + i y`: `radcan(subst(%e^(2*%i*asin(sqrt(x))) = (sqrt(1-x)+%i*sqrt(x))^2, d))` |
| `asinh(sqrt(x))/x` | `exp(asinh y) = y + sqrt(y^2+1)`: `radcan(subst(%e^(2*asinh(sqrt(x))) = (sqrt(x)+sqrt(x+1))^2, d))` |

The run: `probes/readme-examples/01-symbolic-verification.mac` (`Results: 16
passed, 0 failed`, 2026-09-26). Why a separate statement: `rubi` currently
leaves Maxima's rational-function kernel list populated until the top-level
statement ends, and a `ratsimp` in the same statement can then fail to close a
residual it closes otherwise (`.scratch/rubi-rat-state-leak/issues/01`).

## API

```maxima
rubi(f, x)                 /* the entry point: rules only */
rubi_fallback(f, x, true)  /* the same, but fall through to integrate(f, x) */
rubi_verbose : true$       /* print every rule outcome: fired, declined, misfires */
rubi_verbose : 'matches$   /* print only the rules that fire */
```

- `rubi(f, x)` returns an antiderivative, or the no-answer noun
  `unintegrable[f, x]` when no rule applies. It never hands the integral to
  Maxima's own `integrate`. `rubi_fallback(f, x, true)` does, at the top level;
  nested sub-integrals follow the switch `mr_nested_fallback` either way.
- The answer can contain Rubi's own special functions in their Maxima
  spelling: `elliptic_f`/`elliptic_e`/`elliptic_pi`, the polylogarithm
  `li[s](z)`, `expintegral_ei`/`_si`/`_ci`/`_shi`/`_chi`, `gamma_incomplete`,
  `fresnel_s`/`fresnel_c`, `hypergeometric`, the polygamma `psi[n](z)`. Rubi's
  `AppellF1` and the two-argument (Hurwitz) `Zeta(s, a)` have no Maxima
  counterpart and stay nouns.
- `rubi_verbose` is `false` by default: nothing is printed. With `true`, every
  rule tried prints its outcome, including the error message of a rule that
  misfires. With `'matches` (or the string `"matches"`), only the rules that
  fire are printed, i.e. the chain of rules that built the answer.

Run switches, set at the prompt (the defaults are what the corpus records use):

| switch | default | meaning |
|---|---|---|
| `mr_max_depth` | 32 | the nested-dispatch depth cap |
| `mr_gtq_facts` | false | true: GtQ/LtQ/GeQ/LeQ also accept what Maxima's `is()` proves, so `assume()` facts count; false is Rubi's own purely numeric reading |
| `mr_eqq_symbolic` | true | EqQ/NeQ read an identically-zero difference as zero (ratsimp/expand/factor), as Rubi's `PossibleZeroQ` does |
| `mr_subst_simp` | false | true: simplify every `Subst` result (the milestone-1 behaviour) |
| `mr_nested_fallback` | false | true: nested sub-integrals no rule answers fall through to `integrate` |

The rest (`mr_flat_wide`, `mr_cond_retry`, `mr_model_flags`, `mr_giveup_last`,
`mr_inert_leak_misfire`, `mr_last_resort_tier`, `mr_general_after_giveups`)
are migration and ordering switches of the matcher; they are documented in
`maxima_rubi_dispatch.lisp`.

## Measured state

Full-corpus records on `master` (2026-09-26; Maxima
`branch_5_50_base_84_g4204fb669`, SBCL 2.6.7; 30 s CPU cap per integral; PASS
= the answer is verified by differentiation, matches the corpus answer, or is
a correct no-answer). Each record states its own build and switches in its
header.

| class | integrals | `rubi` PASS | native `integrate` | record |
|---|---:|---:|---:|---|
| 1 algebraic | 25,697 | **23,203 (90.3 %)** | — | `test/corpus_class1.out` |
| 2 exponentials | 965 | **863 (89.4 %)** | 363 | `test/corpus_class2.out` |
| 3 logarithms | 3,085 | **2,446 (79.3 %)** | 1,190 | `test/corpus_class3.out` |
| 4 trigonometric | 22,472 | **19,932 (88.7 %)** | 1,384 | `docs/corpus-class4-baseline-uplift.md` |
| 5 inverse trig | 4,585 | **3,629 (79.1 %)** | 1,234 | `docs/corpus-class5-baseline-uplift.md` |
| 6 hyperbolic | 5,080 | **4,314 (84.9 %)** | 301 | `docs/corpus-class6-baseline-uplift.md` |
| 7 inverse hyperbolic | 6,552 | **5,342 (81.5 %)** | 953 | `docs/corpus-class7-baseline-uplift.md` |
| 8 special functions | 1,949 | **1,537 (78.9 %)** | 327 | `docs/corpus-class8-baseline-uplift.md` |
| **all** | **70,385** | **61,266 (87.0 %)** | | |

The native-`integrate` baselines are scored the same way (classes 2, 3 and 6
re-measured 2026-09-20; classes 4, 5, 7 and 8 on 2026-09-25). The class-1
baseline is the older sample-based figure in `docs/corpus-baseline-uplift.md`
and is not comparable.

## Testing

Every suite ends with `Results: <n> passed, <m> failed`. Read that line: a run
that dies mid-way prints no such line, which is itself a failure, and a Lisp
error inside a test section silently drops that section's remaining checks,
so also grep the output for `Lisp error` and compare the pass count with the
expected figure.

- **Layer A**, the unit suite:
  `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null` (1,585 checks).
- **The gates on the real table**: `test/test_rule_table_order.mac`,
  `test/test_section9_e2e.mac`, and the matcher suites under `test/matcher/`.
- **The generator's static gate**: `python3 test/check_generated_rules.py`.
- **Layer B**, a full corpus class, through the queue runner (one Maxima
  process per integral, 24 workers):
  `python3 test/run_corpus_queue.py "<section>" --prev <record> --workers 24 --launch`,
  then `test/wait_and_merge.sh`; compare two records with
  `python3 test/ab_records.py <old> <new>`. Class 1 takes about 50 minutes.

`AGENTS.md` (`## Tests`) holds every gate with its current green figure and
the reading protocol in detail.

## Layout

```
maxima_rubi.mac             public loader (witness-checked sibling loads, mr_load_all)
maxima_rubi_utils.mac       mr_top / rubi, the %mr_ predicate and utility layer
maxima_rubi_match.lisp      the pattern matcher (MR-MATCH)
maxima_rubi_tree.lisp       Maxima expression <-> matcher tree conversion
maxima_rubi_dispatch.lisp   rule records, the dispatcher, the run switches
rules/class1 .. class8/     GENERATED rule files, one per Rubi .m file
rules/class9/               section 9 (9.2, 9.3), generated
rules/utils/                generated rewrite tables (the inert-trig functions)
generator/                  the Python rule generator (generate_rules.py)
test_maxima_rubi.mac        Layer A unit suite
test/                       corpus driver, queue runner, mergers, A/B diff, gates,
                            rules-core build, the committed corpus records
probes/                     committed, re-runnable measurement probes
docs/                       design specs, measured acceptance records, runbook
.scratch/                   issue tickets (see docs/agents/issue-tracker.md)
todo/                       milestone index and pinned reference clones
```

The rule files are generated from the pinned Rubi 4 clone (`reference/rubi`, a
gitignored working copy; the pin is recorded in `todo/TODO.md` and in every
generated file's header). Regenerate, don't hand-edit:
`python3 generator/generate_rules.py --class <1-9>` (and `--rewrites` for
`rules/utils/`). Regeneration is byte-identical, and the static gate checks
that.

## License

The generated rule files (`rules/class*/*.mac`) are a substantial
portion of Rubi, ported from the pinned commit, and carry the Rubi
copyright notice in their headers. Rubi is MIT:

```
MIT License

Copyright (c) 2018 Rule-Based-Integration Organization

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
