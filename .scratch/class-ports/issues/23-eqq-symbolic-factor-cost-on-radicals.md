# Symbolic EqQ: factor() on radical kernels runs past the cap

Status: needs-triage (a fix is proposed and measured)
Type: bug (cost; 37 entries)
Filed: 2026-09-26 (class-ports final attribution, `probes/class-ports/final/`)

## Finding

The symbolic zero test (`mr_eqq_symbolic`, issue matcher-translation-fixes/03, `d0f0237`) runs
the zero chain's `factor()` on differences whose kernels are radicals of symbols or numbers
(`a^(1/7)`, `2^(1/7)`). The main trigger is 1_4_1 r4/r5/r6's perfect-power test
`EqQ[Px, (Rt[a,n] + Rt[b,n] x)^n]`. A second trigger is `if unknown` conditionals leaked by
`%mr_pseudoRoot`'s bare `is(u < 0)`.

- Probe 03: `factor()` takes over 120 s on the `(a+bx)^4 (c+dx)^3` case. Probe 04: `radcan`
  answers "nonzero" on the same difference in 0.4 ms.
- 37 of the 182 final PASS->FAIL: class 1 32, class 2 3, class 4 1, class 6 1.

## Proposed fix (measured, not applied)

`probes/class-ports/final/fix-eqq-radcan.mac` and `fix-pseudoroot.mac`:

1. In `%mr_symbolicZeroQ`, add an exit after the ratsimp exit and before the zero chain. When
   every ratsimp kernel is a variable symbol, a positive rational, or a rational power of either,
   a NONZERO `radcan` ends the test as false. A zero `radcan` is not trusted and falls through, so
   branch identities stay nonzero as the user's EqQ decision requires.
2. `%mr_pseudoRoot` uses the two-valued `%mr_rt_ltQ` sign test.

Measured: it recovers 36 of the 164 losses that reproduce singly. It loses none of the 182, none
of the 29 earlier EqQ-fix wins, and none of a 75-entry PASS sample (`14-arm-fixRP.out`,
`07-*`). Failing check: `17-proposed-checks.mac` (RED 4/1 then no `Results:` line at the 90 s
cap; GREEN 7/0). Known residual: 1.3.1 e211, where the radical's base is a sum.
