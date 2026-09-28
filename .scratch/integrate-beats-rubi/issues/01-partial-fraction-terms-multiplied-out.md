# Partial-fraction terms come back multiplied out: SimplifyTerm and NormalizeIntegrand

Status: ready-for-agent
Type: bug (class-1 timeouts: 3 traced out of 228; the rest not yet attributed)
Filed: 2026-09-27

## Symptom

Class-1 rational integrands that `integrate` does in 0.1 s time out under
rubi. The record's `timeout` class covers the whole entry, rubi plus
verification. The rubi call alone takes:

| integrand | rubi alone |
|---|---|
| `1/((a+b*x)^2*(c+d*x)^3)` (1.1.1.2 e1360) | 27.4 s |
| `x^7/((a+b*x)^2*(c+d*x)^3)` (1.1.1.3 e259) | 32.4 s |
| `1/((a+b*x)*(c+d*x)^8)` (1.1.1.2 e1372) | > 90 s |

The answers that do come back carry `log((a^4*b*d^4-...)*x + ...)` where
`log(b*x+a)` belongs. That is, the linear factors were multiplied out.
Measured in `probes/integrate-beats-rubi/02-timeout-arms.{py,mac,out}` on build
`branch_5_50_base_84_g4204fb669`.

## Mechanism

1. 1.1.1.2 r13 (`ILtQ[m, 0] && IntegerQ[n]`,
   `Int[ExpandIntegrand[(a+b x)^m (c+d x)^n, x], x]`) fires. That is correct.
2. `%mr_expandIntegrand` reaches the catch-all `ExpandExpression`, and
   `%mr_smartApart` (Maxima's `partfrac`) returns the right partial fractions,
   e.g. `d^2/((a^2*d^2-2*a*b*c*d+b^2*c^2)*(d*x+c)^3)`.
3. `%mr_expandCleanup` maps `%mr_simplifyTerm` over the terms, and that
   **multiplies every denominator out**: `(d*x+c)^3` becomes a 12-term cubic.
4. No rule sees a linear power any more. Each term cascades: 1_4_1 r18/r20,
   1_3_3 r12, 1_2_1_1 r3, 9_1 r6, 1_4_2 r13 misfires. The flat-sum
   matcher enumerates splits of the long sums against `a + b*x` slots.
   1_1_1_1 r5 was tried 3,070 times in 25 s, and 1_2_3_1 r10 1,512 times.

`probes/integrate-beats-rubi/01-simplifyterm-stages.{mac,out}` has the stages
one by one.

### Defect A: SimplifyTerm canonicalises every term

`%mr_simplifyTerm(u, x)` = `%mr_normalizeIntegrand(%mr_together(%mr_simpCleanup(u, x)), x)`,
in `maxima_rubi_utils.mac`.

- `%mr_simpCleanup` is `ratsimp(expand(ratsimp(e)))`. This is a stated deviation of
  2026-09-16: the `factor()` stage of `%mr_simp` was dropped after heap
  exhaustion on 1.2.3.2 e637/e660. Its comment argues that expanded terms are
  "the form ExpandIntegrand exists to produce". That holds for a polynomial
  expansion, but not for a partial fraction, whose point is a constant over a
  power of a linear factor.
- `%mr_together` is `rat()`, which expands as well.

Mathematica's `Simplify` and `Together` never multiply `(c+d*x)^3` out.

**Measured.** Skipping both stages, i.e. `SimplifyTerm` reduced to
`NormalizeIntegrand` (an experiment, not a fix), gives 27.4 s -> 3.3 s and
32.4 s -> 7.6 s, both verified, with answers 60 % and 42 % shorter.
Skipping `%mr_simpCleanup` alone or swapping `Together` for `xthru` alone
changes nothing, because each of the two stages expands on its own.

### Defect B: NormalizeIntegrand expands 1/(k*(d*x+c)^n)

`%mr_normalizeIntegrand(1/(k*(d*x+c)^n), x)` multiplies the denominator out
for n = 1, 4, 6, 8, and keeps it for n = 2, 3, 5, 7. `k/(d*x+c)^n` is kept
for every n. This is a port bug, not a deviation; the code is not located yet.
With defect A removed it still expands 4 of the 9 partial fractions of
`1/((a+b*x)*(c+d*x)^8)` to degree 8, and that entry still takes > 90 s.

## Constraints on a fix

- `%mr_simplifyTerm` / `%mr_expandCleanup` run behind every
  `ExpandIntegrand` call site (291 generated lines). A fix is a
  corpus-wide change and needs the all-class A/B.
- The 2026-09-16 heap death must not come back. `factor()` on the dense
  coefficient polynomials of a wide product expansion is fatal and cannot
  be caught.
- `%mr_together` has 200+ other call sites (per its comment in
  `%mr_expandCleanup`). Fix SimplifyTerm's use of it, not the function.
- Even 3.3 s is slow for a few Rubi steps. There may be further overhead.

## Open

- How many of the 228 class-1 timeouts, and of the other classes' timeouts,
  have this cause.
- Where in `%mr_normalizeIntegrand` defect B lives.

## Comments

### 2026-09-28: first A/B, and a fix round

**The fix.** `dcdcf53` changes three things:

- B2: `%mr_trinomial_parts` now scans every interior coefficient.
- B1: `%mr_normalizeIntegrandFactorBase` reads a quotient as the product
  it is stored as.
- A: `%mr_simplifyTerm` has a no-larger guard.

**Timing.** 27.2 s -> 0.05 s, 29.1 s -> 0.08 s, > 90 s -> 0.23 s
(`probes/integrate-beats-rubi/03-fixed-timing`).

**First full-corpus A/B.** All eight classes against master's `*.sumfirst.out`
records, with every transition re-run on both cores (`c96e51d`,
`test/pfs_attr_class<N>.out`). Credited to the fix: **635 gains, 25 losses**.

**Fix round.** The 25 losses were attributed by undoing one fix at a time
in-session (master's definition loaded over the fixed code):

- `%mr_leafCount` died with "part: fell off the end" on a negative rational,
  which Maxima stores as one number but shows as the `"-"` node -(8/45).
  The guard reached it on a partial fraction's constant term, and
  1.1.1.3 e1384 answered WRONG (a numeric residual of 5.7). Fixed: a
  number counts 1, or 3 for a non-integer rational (Mathematica's
  LeafCount[Rational[-8, 45]] = 3).
- The no-larger guard also refused the NUMERATOR expansions that the sum
  split relies on. 9_3 r63's expansion of 3.1.5 e20 handed on
  `(b^2*e*log(e*x+1)-b^2*e)*log(c*x^n)^2` whole, and it fell to a noun.
  Master expanded it; Mathematica's Simplify would factor it. Both paths
  integrate. The guard is now `%mr_keep_denominator`: a stand-in's result
  is refused only when its DENOMINATOR is larger. That is the defect's
  actual mechanism, since Simplify and Together keep a denominator's
  factors.

Re-run through the driver on the fixed code, 16 of the 25 losses pass
again: 1.1.1.3 e1384/e1398, 1.2.1.3 e1609-e1612, 3.1.5 e20, 4.1.2.1
e70, 4.5.2.1 e138, and 4.3.7 e92/e93/e104/e105/e154/e155.

**The 9 still lost, with their cause.** "Undo X" means master's definition of
X loaded over the fixed code; 45 s kill.

| entry | integrand | now | cause |
|---|---|---|---|
| 4.3.7 e96 | `csc(e+f*x)^3*sqrt(a+b*tan(e+f*x)^2)` | noun | A (undo A: 6.2 s) |
| 4.3.7 e97 | `csc(e+f*x)^5*sqrt(a+b*tan(e+f*x)^2)` | noun | A (undo A: 11.0 s) |
| 1.1.1.4 e71 | `1/((a+b*x)*(c+d*x)^(3/2)*sqrt(e+f*x)*sqrt(g+h*x))` | timeout | A or B1 (either undo: 11-16 s) |
| 3.2.3 e17 | `(a+b*x)^3*log(e*(f*(a+b*x)^p*(c+d*x)^q)^r)^2` | timeout | B1 (undo B1: 2.0 s) |
| 3.2.3 e16 | `(a+b*x)^4*log(e*(f*(a+b*x)^p*(c+d*x)^q)^r)^2` | timeout (34 s) | B1 or B2 (either undo: ~2 s) |
| 2.1 e78 | `%e^(-a-b*x)*(a+b*x)^4/(c+d*x)` | timeout | B1 (undo B1: 1.1 s) |
| 8.8 e137 | `(d+e*x)^3*polylog(2,c*(a+b*x))` | timeout | B1 (undo B1: 1.0 s) |
| 5.3.4 e1270 | `x*(a+b*atan(c*x))^2/(d+e*x^2)^2` | noun | B1 or A |
| 7.3.6 e473 | `%e^(3*atanh(a*x))/(c-c/(a*x))^4` | unverified | B2 changes the answer |

6.3.7 e75, `sinh(c+d*x)^2/(a+b*tanh(c+d*x)^3)`, times out only in
verification. rubi itself is 5x faster on the fixed code, 2.4 s against
12 s, but the new answer shape takes longer to verify.

**Next.** B1 is the faithful reading: Mathematica has no quotient node.
Its six losses probably mark other port parts tuned, knowingly or not, to
the old whole-quotient reading. This is a hypothesis; none is traced yet,
and 2.1 e78 is the cleanest witness. User decision 2026-09-28: commit
with these 9 documented, re-run the full A/B, and treat the losses as
follow-ups.
