# Corpus-limitation: 3 entries the package now integrates (corpus expects Unintegrable)

Status: needs-triage
Filed: 2026-08-27 (class-1 A+B acceptance run, core f1f0611f)
Evidence: `.superpowers/sdd/progress.md` (run #2 anatomy); numeric
verification probe `/tmp/opencode/noans2.mac` (disposable — to be
promoted to `probes/` if this ticket is worked).

## What

Three 1.2.3.4 entries carry a corpus expected answer of `Unintegrable`
(run-5 class `no-answer`, PASS). The A+B run returns a non-noun answer
for all three (class `unexpected` — the driver's noun-reference branch
has no verified path, so a correct answer is still a FAIL):

| entry | integrand | t5 | t6 |
|---|---|---|---|
| e86 | `(f*x)^m*(d+e*x^n)^q*(a+c*x^(2*n))^p` | 3.0 s | 4.0 s |
| e155 | `(f*x)^m*(a+b*x^n+c*x^(2*n))^p/(d+e*x^n)` | 2.7 s | 4.1 s |
| e156 | `(f*x)^m*(a+b*x^n+c*x^(2*n))^p/(d+e*x^n)^2` | 3.1 s | 4.3 s |

## Verification (measured 2026-08-27)

Each answer sampled at x = 0.3/0.6/0.9 with generic parameter values
(f=2, m=1, d=3, e=5, a=11, b=13, c=7, n=1/2, p/q per entry):
`abs(float(diff(ans, x)) - float(f))` <= 3e-10 at every point
(e86 at ~1e-10 — float rounding on its large rational coefficients;
e155/e156 at <= 3e-14). The answers are correct antiderivatives: the
package now integrates what the pinned 2018 corpus (2018 Rubi
matcher + the 2018 rule state) could not.

## Why it FAILs

The corpus expected value is `Unintegrable`; the driver's
noun-reference PASS class for such entries is `no-answer` only. A
correct integration is classified `unexpected`. This is a CORPUS
limitation (its expected values predate the matcher improvements),
not a package defect.

## Directions (to be triaged)

1. Accept the 3 as a known corpus limitation (they count against the
   pass total until the corpus is regenerated).
2. Regenerate/patch the corpus expected values for these 3 entries
   (the corpus is a git-tracked reference under
   `reference/maxima-syntax-test-suite` — a patch there needs a
   justification note per the pin-discipline in `todo/TODO.md`).
3. Driver policy: a `noun-reference` entry whose package answer
   self-verifies (zero chain closes) could be re-classed `verified`
   instead of `unexpected` — a harness change that would also absorb
   any FUTURE corpus-under-estimates automatically; decide whether
   that weakens the acceptance standard (it would: an incorrect
   answer that happens to close the chain on the sampled form would
   pass — the chain is the verifier, so the risk is the chain's own
   blind spots, e.g. branch cuts on complex forms).

## Acceptance (when worked)

Whichever direction is chosen, the decision is recorded in the
ledger and the ticket closed; no rule changes are expected.
