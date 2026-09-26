# An expected answer that is Rubi's own partial answer can never PASS

Status: needs-triage
Type: question (verification harness, classification)
Filed: 2026-09-26 (class 8/5/7/4 ports, Step 10 records)

## Problem

Many corpus expectations are Rubi's PARTIAL answers: an antiderivative that
carries an `Unintegrable(…)` or `CannotIntegrate(…)` inside it, e.g. 8.1 e20

    erf(a+b*x)/(c+d*x)^2  ->  -erf(a+b*x)/(d*(c+d*x)) + 2*b*Unintegrable(1/(%e^((a+b*x)^2)*(c+d*x)),x)/d

`test/corpus_driver.py` builds the classifier so that any answer carrying a
no-answer noun is `contains-noun` BEFORE the zero chain is consulted (the
`has_noun` test ahead of `zv`/`ze`, the non-marker branch of `build_text`), and a
top-level noun against a non-marker expectation is `deferred`. So an answer
that reproduces Rubi's partial answer exactly is a FAIL, and no rule work can
change that. Ticket 04 is the narrow top-level case (`c * unintegrable(…)`
against a marker expectation); this one is the interior case.

## Measured (committed records, no Maxima)

`probes/corpus/28-class-ports-acceptance.out` ("Rubi markers in the expected
answer"), on the final class-ports records (core `89bec424`):

| class | expected answer carries an interior marker | of them `contains-noun` | `deferred` | share of the class's `contains-noun` |
|---|---:|---:|---:|---:|
| 8 Special functions | 141 | 138 | 1 | 138 / 368 |
| 5 Inverse trig | 286 | 283 | 3 | 283 / 665 |
| 7 Inverse hyperbolic | 202 | 140 | 61 | 140 / 604 |
| 4 Trig | 117 | 110 | 6 | 110 / 775 |

746 entries over the four classes; 5.3.4 alone has 216 of the `contains-noun`, 8.1 and 8.2 are
entirely this (45/45 and 38/38 of their FAIL). Classes 1/2/3/6 were not
counted (the probe covers only the four new sections).

## The question

Should the harness have a verdict for "the package's answer equals Rubi's
partial answer" — e.g. `expected` when `mr_r - (<e>)` is zero within the
chain with the nouns treated as opaque symbols (both sides carry the same
`unintegrable(g, x)` terms, so they cancel) — and is that a PASS? It could
move up to 671 `contains-noun` and 71 `deferred` entries in these four
classes. The risk to weigh:
a noun whose integrand DIFFERS from Rubi's (a different split) must not
cancel, and the verdict must stay distinct from a noun-free `expected`.
The answer changes every class's PASS count, so it is a user decision and
needs a re-measure of all eight classes.
