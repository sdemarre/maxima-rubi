# 1.2.2.2 e1035: a zero coefficient left unsimplified gives an infinite answer

Status: needs-triage
Type: bug (wrong answer; 1 entry, degenerate input)
Filed: 2026-09-26 (class-ports final attribution, `probes/class-ports/final/12-e1035-combos.out`)

The integrand is `1/(x*sqrt(a + (2+2c-2(1+c))*x^4))`. The x^4 coefficient is identically 0, so
the integral is `log(x)/sqrt(a)`, which master answers through 9_1 r2 (`EqQ[b, 0]`).

On class-ports the answer is `-atanh(1)/(2 sqrt(a))`, which is infinite. The loss needs BOTH plain
Subst (`mr_subst_simp` false) and the two-valued GtQ. Plain Subst leaves the zero coefficient
unsimplified, so the division by zero that used to make the binomial rule misfire, and let 9_1 r2
answer, no longer happens. The two-valued GtQ then lets a binomial reduction fire on b = 0.

A candidate is to read a capture that simplifies to 0 as 0 before binomial rules test it (Rubi
normalises its integrand before matching, so it never sees b = 0 as a binomial). Measure before
choosing.
