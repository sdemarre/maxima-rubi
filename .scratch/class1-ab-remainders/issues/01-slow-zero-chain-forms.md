# Slow zero-chain forms: 9 verified->timeout remainders

Status: needs-triage
Filed: 2026-08-27 (class-1 A+B acceptance run, core f1f0611f)
Evidence: `.superpowers/sdd/progress.md` (run #2 anatomy), canary
solo timings below, `test/corpus_class1.out` vs
`test/corpus_class1.run5-accept.out`.

## What

Nine entries verified in run-5 (23.8-27.8 s under 24-way load,
i.e. already near the 30 s budget) time out at 30.0 s in the A+B run.
The canary (60 s cap, low contention) verifies every one at 25-35 s
SOLO — the answers are correct; the differentiation-based zero chain
on the new answer FORM overruns the budget under load.

| family | entry | integrand | t5 (run-5) | canary solo (A+B) |
|---|---|---|---|---|
| 1.1.4.3 | e228 | `(A+B*x^2)*sqrt(b*x^2+c*x^4)/x^(11/2)` | 27.8 s | 26.1 s |
| 1.2.1.3 | e1979 | `(a+b*x)*(a^2+2*a*b*x+b^2*x^2)^(3/2)/(d+e*x)^4` | 24.2 s | 35.2 s |
| 1.2.1.4 | e686 | `sqrt(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)/((f+g*x)^3*sqrt(d+e*x))` | 23.8 s | 28.0 s |
| 1.2.1.4 | e687 | same, `(f+g*x)^4` | 26.9 s | 30.0 s |
| 1.2.1.5 | e59 | `(2+3*x+5*x^2)^3*sqrt(3-x+2*x^2)` | 26.1 s | 31.5 s |
| 1.2.1.5 | e66 | `(3-x+2*x^2)^(3/2)*(2+3*x+5*x^2)^3` | 27.0 s | 30.0 s |
| 1.2.1.5 | e73 | `(3-x+2*x^2)^(5/2)*(2+3*x+5*x^2)^3` | 26.3 s | 29.3 s |
| 1.2.1.9 | e308 | `(2+x+3*x^2-5*x^3+4*x^4)/((d+e*x)*(3+2*x+5*x^2))` | 27.0 s | 26.3 s |
| 1.2.2.3 | e149 | `1/((d+e*x^2)^2*(a+c*x^4)^2)` | 26.2 s | 25.3 s |

## Mechanism (measured)

The section-9.1 rules (r16/r11-class reshapes) changed the quartic/
trinomial radical answer FORM these cascades produce. The new form's
`ratsimp(diff(ans, x) - f) = 0` closure runs 25-35 s solo where the
run-5 form closed in time; under 24-way load that crosses the driver's
30 s per-entry budget. No rule is wrong — the answers verify.

## Directions (to be triaged)

1. Zero-chain form simplification before the diff (the standing
   "verification-chain form" quality workstream — the ledger tracks it
   as the known remainder class for rule-form changes).
2. Per-entry budget policy (raise the 30 s cap for heavy families, or
   a class-conditional cap) — a harness decision, not a rule decision.
3. Accept as-is: 9/25,697 = 0.035% of the corpus, all correct answers.

## Acceptance (when worked)

All 9 entries `verified` in a full run at the current budget, with the
canary broad (120) and Layer A (511) unchanged.

## Comments

2026-08-27 — 300 s timeout re-check (record test/corpus_class1.timeout5m.out):
ALL 9 entries RECOVER to `verified` at the 300 s cap, measured at 24-way
load: 1.1.4.3 e228 40.3 s; 1.2.1.3 e1979 71.4 s; 1.2.1.4 e686 49.1 s /
e687 53.0 s; 1.2.1.5 e59 52.8 s / e66 54.3 s / e73 51.8 s; 1.2.1.9 e308
44.2 s; 1.2.2.3 e149 31.3 s. Direction 2 (per-entry budget policy) is
therefore sufficient for this set — the answers were always correct and
the zero chains always close, at 31-71 s under load. Cost of a blanket
300 s cap for the WHOLE corpus: the 555 genuine non-terminators of the
re-check would each burn the full cap (555 x 300 s / 24 procs ~= 9.2 h
of the 82-min typical run) — a class-conditional or per-entry budget is
the sane form if this direction is taken.
