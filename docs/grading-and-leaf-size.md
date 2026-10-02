# Grading antiderivatives: leaf size and the A/B/C/F grade

Since 2026-09-30 (user request), every corpus run records, next to its PASS/FAIL
class, the **leaf size** of each answer and of the corpus's optimal
antiderivative, and a **grade** A/B/C/F. Both are taken from the *Computer
algebra independent integration tests* of Nasser M. Abbasi
(<https://www.12000.org/my_notes/CAS_integration_tests/>), so our results can be
read against the published results for Rubi in Mathematica, Maxima and the other
systems. This document says where the definitions come from, how they are
implemented here, how far the implementation reproduces the reference (measured),
and how to read the results.

Measurements are stamped with the build `branch_5_50_base_84_g4204fb669`
(2026-08-31 13:27:47) on SBCL 2.6.7, 2026-09-30.

## 1. The reference

The report's results page (summer 2021 edition, e.g.
[10_Hebisch/rese2.htm](https://12000.org/my_notes/CAS_integration_tests/reports/summer_2021/test_cases/10_Hebisch/rese2.htm#x4-30001.2))
describes the grades:

| grade | meaning |
|---|---|
| A | solved; the antiderivative is optimal in quality and leaf size |
| B | solved; optimal in quality, but its leaf size is more than twice the optimal's |
| C | solved; not optimal in quality: it holds a hypergeometric or special function, or the imaginary unit, that the optimal does not |
| F | not solved: returned unevaluated, timed out, crashed or raised an exception; F(-1) is a timeout, F(-2) an exception |

and one rule for integrals without a closed form: a system that returns such an
integral unevaluated within the time limit gets **A**, and one that returns an
antiderivative for it gets **A** too (the report lists those separately); a
timeout on it is F.

The exact definitions are the report's grading functions (summer 2022 edition,
section 4.2: [Mathematica and Rubi](https://www.12000.org/my_notes/CAS_integration_tests/reports/summer_2022/test_cases/0_Independent_test_suites/12_Wester_Problems/reportsubsection22.htm),
[SageMath](https://www.12000.org/my_notes/CAS_integration_tests/reports/summer_2022/test_cases/0_Independent_test_suites/12_Wester_Problems/reportsubsection25.htm)).
The Mathematica one is Albert Rich's `GradeAntiderivative` (emailed to Abbasi in
2017); the Maple, SymPy and SageMath versions are Abbasi's ports of it.

```
GradeAntiderivative[result, optimal]:
  ExpnType[result] <= ExpnType[optimal]:
      result has Complex, optimal has not          -> C
      LeafCount[result] <= 2 LeafCount[optimal]    -> A
      otherwise                                    -> B
  ExpnType[result] > ExpnType[optimal]:
      result free of Integrate and Int             -> C
      otherwise                                    -> F
```

`ExpnType` gives an expression its "highest function": 1 rational, 2 algebraic,
3 elementary, 4 special, 5 hypergeometric, 6 Appell, 7 RootSum, 8 unevaluated
integral, 9 unknown. A power with an integer exponent has its base's type; with a
rational exponent it is 1 on a numeric base (`Sqrt[2]` is rational) and at least 2
otherwise; any other power is at least 3. A sum or product takes the maximum of
its parts; an elementary function max(3, its first argument); special,
hypergeometric and Appell functions max(4/5/6, all arguments). The function lists
are fixed sets of names: elementary `Exp, Log`, the six trig functions, the six
hyperbolic ones and their twelve inverses; special `Erf, Erfc, Erfi, FresnelS,
FresnelC, ExpIntegralE, ExpIntegralEi, LogIntegral, SinIntegral, CosIntegral,
SinhIntegral, CoshIntegral, Gamma, LogGamma, PolyGamma, Zeta, PolyLog,
ProductLog, EllipticF, EllipticE, EllipticPi`; hypergeometric `Hypergeometric1F1,
Hypergeometric2F1, HypergeometricPFQ`; Appell `AppellF1`. Everything else (Bessel
functions, `EllipticK`, `Abs`, ...) is 9.

**Leaf size.** For Rubi, Mathematica and Maple the report uses the system's own
leaf count, i.e. Mathematica's `LeafCount` for Rubi. For Maxima, FriCAS and Giac
(run through SageMath) it uses SageMath's `tree_size` (section 1.9.3 of the
summer 2021 report): 1 for an atom, 1 plus the parts for a compound. The two are
**not the same unit**: `LeafCount` counts `1/2` as `Rational[1, 2]` (3 leaves)
and `I` as `Complex[0, 1]` (3), `tree_size` counts both as 1.

## 2. The implementation

`test/mr_grade.lisp`, loaded by every corpus entry (both arms: rubi, and the
native baseline in stock Maxima).

### Leaf size: `mr_leaf_count(e)`

Mathematica's `LeafCount`, for **every** system we run -- one ruler for rubi and
for Maxima's `integrate`, and the same ruler the reference uses for Rubi and for
the optimal antiderivatives.

It walks Maxima's simplified internal form, which already has Mathematica's shape
for everything common: `a - b` is `a + (-1)*b` (`Plus[a, Times[-1, b]]`, 5), `a/b`
is `a*b^(-1)` (`Times[a, Power[b, -1]]`, 5), `sqrt(x)` is `x^(1/2)`, `%e^x` is a
power of the atom `%e` (`Power[E, x]`, 3). An atom counts 1, a compound 1 plus its
parts, except where Mathematica holds something differently:

| Maxima | Mathematica | leaves |
|---|---|---:|
| `1/2` | `Rational[1, 2]` | 3 |
| `%i` | `Complex[0, 1]` | 3 |
| `2*%i*x` | `Times[Complex[0, 2], x]` -- the numeric parts carrying `%i` fold into one complex number | 5 |
| `1 + 2*%i + x` | `Plus[Complex[1, 2], x]` | 5 |
| `li[2](z)` | `PolyLog[2, z]` -- a subscripted function is one head, its subscripts leading arguments | 3 |
| `hypergeometric([a,b],[c],z)` | `Hypergeometric2F1[a, b, c, z]` (likewise 1F1; other pFq keep their lists) | 5 |

**The optimal is evaluated under `logexpand:false, radexpand:false`** (the
package's model flags) before it is counted. Under Maxima's defaults, evaluating
the corpus text already rewrites it: `log((x^2-a^2)^2)` becomes `2*log(x^2-a^2)`
and `sqrt(x^2)` becomes `abs(x)`, which Mathematica does not do. The answers are
counted as the integrator returned them.

### Expression type: `mr_expn_type(e)`

`ExpnType` over Maxima's names, one to one (`%atan` for `ArcTan`,
`expintegral_si` for `SinIntegral`, `li` for `PolyLog`, `lambert_w` for
`ProductLog`, `gamma_incomplete` for the two-argument `Gamma`, `elliptic_ec` for
the one-argument `EllipticE`, `hypergeometric` for all three hypergeometric
heads, the corpus's `AppellF1`, the `integrate` noun and our `unintegrable` noun
for an unevaluated integral). The elementary list is the **SageMath port's**,
which adds `abs`, `signum`, `floor` and `atan2` to Mathematica's (the report
grades Maxima with it); so `abs(x)` is 3 here, where Mathematica would say 9.

### The grade: `mr_grade(result, optimal)` and the driver

`mr_grade` is `GradeAntiderivative` as above, returning `[grade, leaf(result),
leaf(optimal), type(result), type(optimal)]`. The complex test is "contains
`%i`".

`test/corpus_driver.py` (`build_text`, `classify_entry`, `grade_of`,
`grade_line`) turns it into the entry's grade:

| our class | grade |
|---|---|
| `verified`, `expected`, `unverified` | `mr_grade` against the corpus optimal (the 4th entry element) |
| `deferred`, `contains-noun` | F |
| `timeout` | F(-1) |
| `error` | F(-2) |
| optimal is `Unintegrable`/`CannotIntegrate`: `no-answer` or `unexpected` | A (the reference's rule) |

`unverified` answers are graded like any answer: the reference does not verify
Maxima's answers at all. **The grade does not replace PASS/FAIL**: our class, and
so our PASS count, stays the verified verdict; the grade is a second, quality
reading of the same answer.

Each entry's Maxima text prints `OPTIMAL <leaf> <type>` (every entry with a
closed-form optimal that got an answer) and, for an answer, `GRADE <g> <leaf>
<type>`, both flushed **before** the checker, so a kill while verifying keeps
them. The shard's `.grade` sidecar holds one line per entry,

    <grade> leaf=<result>/<optimal> type=<result>/<optimal> <relpath> e<n> L<line>

with `-` for anything unknown (an entry that never answered has no result size;
a timeout has neither). `test/merge_grade.py RECORD OUT GLOB` checks it complete
against the merged record and writes the census the report's tables 1.3 and 1.5
show: the grade distribution, and over the solved entries (A/B/C) the mean time,
mean and median leaf size, and the normalized mean and median (per entry,
result's leaf size over the optimal's, then averaged). `test/graded_measure.sh
"<SECTION>"` runs rubi and the baseline over a section with every census.

Guards: `maxima --very-quiet -b test/test_mr_grade.mac` (the Lisp: leaf sizes,
types, grades) and `python3 test/test_driver_grade.py` (the driver, sidecar and
merger), both in AGENTS.md's gate list.

## 3. How well the leaf size reproduces Mathematica's

`probes/leaf-size/01-scrape-reference.py` scrapes, from the summer 2022 reports of
the twelve independent test suites, every integral's optimal leaf size (as
`LeafCount`) and the grades and sizes given for Rubi and Maxima
(`01-scrape-reference.tsv`, 1,891 rows). Problem N of a report is entry eN of the
corpus file, except in Welz: its report has 116 problems and the corpus 93, and
they part ways after problem 57, so later Welz rows are left out.

`probes/leaf-size/02-leaf-count-vs-reference.py` counts the corpus's optimal of
each problem with `mr_leaf_count` and compares
(`02-leaf-count-vs-reference.out`, 1,829 optimals):

| optimal evaluated under | exact | within 10 % | sum of \|diff\| / sum of reference |
|---|---:|---:|---:|
| Maxima's defaults | 1,632 (89.2 %) | 1,779 (97.3 %) | 1.7 % |
| `logexpand:false, radexpand:false` (**used**) | 1,692 (92.5 %) | 1,800 (98.4 %) | 1.0 % |

What remains is Maxima's own simplification of the expression, which no counting
rule can undo: `x*log(%e^cos(x))` is `x*cos(x)` as soon as it is evaluated
(Apostol e157: 15 leaves in Mathematica, 2 here after the whole optimal collapses
to `sin(x)`), Maxima writes `sqrt(2)/4` where Mathematica writes `1/(2*Sqrt[2])`,
and so on -- a leaf or two either way on most of the 137 inexact optimals.

## 4. First results: the independent test suites

`test/graded_measure.sh "0 Independent test suites"` (1,869 integrals, 24 workers,
30 s CPU per integrator plus 30 s of verification; the rubi column re-measured
2026-10-02 with the %i fold, section 5): records
`test/corpus_class0.out` and `test/corpus_class0.baseline.out`, grade censuses
`test/corpus_class0.grade.out` and `test/corpus_class0.baseline.grade.out`.

| | maxima-rubi | Maxima 5.50 integrate+risch |
|---|---:|---:|
| A | 1,679 (89.8 %) | 1,385 (74.1 %) |
| B | 67 (3.6 %) | 155 (8.3 %) |
| C | 38 (2.0 %) | 33 (1.8 %) |
| F | 77 (4.1 %) | 280 (15.0 %) |
| F(-1) | 8 (0.4 %) | 11 (0.6 %) |
| F(-2) | 0 | 5 (0.3 %) |
| solved (A/B/C) | 1,784 (95.5 %) | 1,573 (84.2 %) |
| PASS (verified) | 1,783 | 1,561 |
| mean time | 0.18 s | 0.49 s |
| mean / median leaf size | 54.2 / 28 | 57.4 / 27 |
| normalized mean / median | 1.96 / 1.00 | 1.63 / 1.00 |

Every answer is graded. (The first census had one rubi answer at `-`, put down to its
optimal; it was an answer in CRE form, which the grade could not walk until
`mr-grade-general` was added, 2026-10-01 -- regraded, it is an A.)

`probes/leaf-size/03-compare-with-reference.py` sets these against the report,
integral by integral (`03-compare-with-reference.out`, 1,833 integrals; measured on
the records of 2026-10-01, before the %i fold):

| | reference | ours |
|---|---|---|
| Rubi 4.16.1 in Mathematica vs maxima-rubi | A 97.9 %, B 0.8 %, C 0.3 %, F 1.0 %; solved 99.0 % | A 89.6 %, B 3.5 %, C 2.3 %, F 4.3 %, F(-1) 0.4 %; solved 95.4 % |
| Maxima 5.45 via SageMath vs Maxima 5.50 integrate+risch | A 75.5 %, B 8.1 %, C 0.8 %, F 13.6 %, F(-1) 0.2 %, F(-2) 1.7 %; solved 84.4 % | A 75.5 %, B 8.5 %, C 1.8 %, F 13.4 %, F(-1) 0.6 %, F(-2) 0.3 %; solved 85.8 % |

Read with care:

- **The setups differ.** The reference caps an integral at 3 minutes; we cap each
  integrator at 30 s of CPU. The reference ran Maxima through SageMath with
  `domain:complex` and other settings (report section 1.9.1), and counts a Maxima
  question to the user as an exception (F(-2)); our batch answers the questions.
  That is the likely reason for most of the 32 reference F(-2), 19 of which are A
  here (not traced one by one).
- **Maxima's sizes are not comparable across the two columns**: the report sizes
  Maxima's answers with `tree_size`, we with `LeafCount` (section 1). Where both
  solved, the reference's normalized Maxima size is 0.88 (mean) and ours 1.12 --
  largely the unit, not the answers.
- **Rubi's sizes are comparable** (both `LeafCount`). Where both solved (1,732
  integrals), Rubi's normalized mean is 1.01 and ours 1.26; the medians are both
  1.00. The 57 A -> B and 41 A -> C integrals are where maxima-rubi's answer is
  larger than, or of a higher type than, the answer Rubi gives in Mathematica
  (15 of rubi's C grades on the section are a `hypergeometric` answer where the
  optimal is elementary): port work, like the 56 A -> F.

## 5. The %i fold (2026-10-02)

Rubi integrates hyperbolic functions through the trig rules: `DeactivateTrigAux`
rewrites `Sinh[u]` as `-I*sin[I*u]`, and Mathematica's evaluator folds the result
back (`Sin[I a + I b x]` -> `I Sinh[a + b x]`). Maxima's `%iargs` folds `sin(%i*v)`
only when the argument is literally a multiple of `%i`, so rubi's answers kept
`sin(%i*b*x+%i*a)` and its `%i` -- correct, but graded C by the grade's `%i` rule
(section 6: 1,854 C of 5,080). The top-level answer now passes through `%mr_ifold`
under `radexpand:false, logexpand:false` (run switch `mr_ifold`, default true; spec
`docs/superpowers/specs/2026-10-02-ifold-answer-design.md`, ticket
`.scratch/answer-quality/issues/01`). Measured before shipping on every entry it can
act on (`probes/leaf-size/05`, `06`), then by re-running every section's rubi arm
(build `branch_5_50_base_84_g4204fb669`, 24 workers, 30 s CPU;
`.scratch/answer-quality/ifold_ab/`):

| | before | with the fold |
|---|---:|---:|
| rubi A, all sections | 60,716 (84.0 %) | 62,583 (86.6 %) |
| rubi C, all sections | 3,102 (4.3 %) | 1,187 (1.6 %) |
| section 6 A / C | 2,534 / 1,854 | 4,057 / 283 |
| entries integrate+risch grades better than rubi | 3,793 | 2,482 |

No PASS -> FAIL outside nine section-6 entries whose answers the checker cannot prove
in the folded shape (their original answers pass only by a symbolic stage; both
forms agree point for point with principal-branch arithmetic and differentiate to
the integrand, probe 06) and four section-4 entries at the 30 s cap (verified at
29.7-29.9 s before; they verify at ~18 s in both switch arms at 4 workers). No grade
got worse but those four. The whole-corpus numbers: `test/grade_report.out`.

## 6. Where this lives

| what | where |
|---|---|
| leaf size, type, grade | `test/mr_grade.lisp` |
| the entry's grade, the `.grade` line | `test/corpus_driver.py` (`build_text`, `classify_entry`, `grade_of`, `grade_line`) |
| the sidecar in the queue runner | `test/run_corpus_queue.py` |
| the census | `test/merge_grade.py` |
| both arms of a section, every census | `test/graded_measure.sh` |
| guards | `test/test_mr_grade.mac`, `test/test_driver_grade.py`, `test/test_ab_grades.py` |
| the grade A/B of two runs | `test/ab_grades.py` |
| the %i fold | `maxima_rubi_utils.mac` (`%mr_ifold`, `%mr_top_final`), switch `mr_ifold` |
| the reference data and the measurements | `probes/leaf-size/01`-`06` |
