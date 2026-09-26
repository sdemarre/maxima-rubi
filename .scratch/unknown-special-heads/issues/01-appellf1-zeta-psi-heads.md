# Answers carry heads Maxima does not know: `AppellF1`, 2-argument `Zeta`, `psi[-2]`

Status: needs-triage
Type: research (decide per head: leave inert, add derivative/numeric support, or port)
Filed: 2026-09-26 (user request, split off from `.scratch/polylog-native-li/issues/01`)
Sibling: `.scratch/polylog-native-li/issues/01` — `polylog` is the fourth such head, and the only
one with a native Maxima replacement (`li[s](z)`).

## The survey

Every function name the rule bodies call (`rules/class*/*.mac`, master `e83221a`) was checked in
the running Maxima for a definition (`fboundp`, `operators`, `mexpr`, `mfexpr*`, `grad`), and
the ones that are not internal (`%mr_*`, `mr_int`, `mr_sum`) were probed with `diff` and `float`
(2026-09-26, build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7). Known and working:
`hypergeometric`, `elliptic_e/f/pi`, `gamma_incomplete`, `expintegral_*`, `lambert_w`,
`fresnel_s/c`, `erf/erfi/erfc`, `poly_discriminant`, `zeta` (1-arg), `mod`, `floor`, `binomial`.
`mr_unintegrable` is inert by design. The rest:

| emitted head | rule sites | Maxima | `diff` | `float` |
|---|---|---|---|---|
| `polylog(s, z)` | classes 3/5/7/8, 155 | unknown (native is `li[s](z)`) | noun | stays |
| `AppellF1(a, b1, b2, c, z1, z2)` | 11: 1_1_1_3 ×4, 1_1_2_3, 1_1_2_4, 1_1_3_3, 1_1_3_4, 4_1_1_2, 4_5_1_4, 4_5_3_1 | unknown, no native | noun | stays |
| `Zeta(s, a)` (Hurwitz) | 3, all in 8_7 | unknown; `zeta` is 1-arg; `bfhzeta(s, h, n)` is bigfloat-numeric only | noun | stays |
| `psi[-2](z)` (negative-order PolyGamma) | 3, all in 8_6 (plus `psi[n-1]`, which is `psi[-1]` at n = 0) | `psi` known | works (`psi[-2]` -> `psi[-1]` -> `psi[0]`) | stays |

`AppellF1` and 2-arg `Zeta` are emitted in the corpus's own spelling on purpose
(`generator/translation_table.py` ~L434–449: "an inert noun (the AppellF1 precedent)").

## Corpus exposure

Entries whose corpus line (integrand or expected answer) carries the head, verdicts from the
promoted records `test/corpus_class<N>.out`:

| class | head | entries | verdicts |
|---|---|---:|---|
| 1 | AppellF1 | 503 | unverified 281, expected 159, timeout 52, deferred 5, verified 4, contains-noun 2 |
| 4 | AppellF1 | 605 | expected 340, unverified 142, timeout 69, contains-noun 52, error 1, deferred 1 |
| 5 | AppellF1 | 22 | expected 17, unverified 5 |
| 6 | AppellF1 | 24 | unverified 12, expected 11, contains-noun 1 |
| 7 | AppellF1 | 47 | unverified 36, expected 11 |
| 8 | Zeta (2-arg) | 14 | expected 7, contains-noun 4, no-answer 2, unverified 1 |

`psi[-2]` has no corpus witness (the class-8 PolyGamma entries are not in the Maxima-syntax
suite). **AppellF1 is the big one: 476 `unverified` entries**, more than twice polylog's 218.
They cannot be verified by differentiation today; a correct answer in a form other than Rubi's
is indistinguishable from a wrong one.

## Options, per head

- **AppellF1.** No Maxima function. Options: (a) leave inert (status quo); (b) give it
  derivative rules with `gradef` — ∂/∂z1 AppellF1(a,b1,b2,c,z1,z2) =
  (a·b1/c)·AppellF1(a+1,b1+1,b2,c+1,z1,z2), and symmetrically in z2 — so the zero chain's
  self-diff stage can close it (only if the rest of the difference simplifies; the shifted
  parameters may not cancel against the integrand); (c) a numeric evaluator (double series for
  |z1|,|z2| < 1) for the numeric stage. Measure (b) on a sample of the 476 before committing.
  Whether a `gradef` belongs in the package (user-visible) or only in the harness is a decision.
- **Hurwitz Zeta.** (a) inert; (b) `gradef(Zeta(s, a), <unknown in s>, -s*Zeta(s+1, a))`;
  (c) a numeric hook via `bfhzeta`. Only 14 entries.
- **psi[-2].** Differentiation already works; only a numeric value is missing. No corpus
  witness; lowest priority.

## Not in scope

The `contains-noun` / `timeout` masses among these entries are other problems.
