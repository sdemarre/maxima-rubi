# `rubi` leaves the rat package's global kernel list populated for the rest of the statement

Status: needs-triage
Type: task (bug)
Filed: 2026-09-26 (found while verifying the README examples)

## What happens

After `rubi(f, x)` returns, Maxima's rational-function globals `varlist` / `genvar` still hold
the kernels `rubi` put there (8 of them for `x/(%e^(2*x)+3*%e^x+3)`), until the top-level
statement ends, when Maxima binds them fresh again. A `ratsimp` later in the SAME statement
works against that stale list. On this integrand it then fails to reduce
`diff(rubi(f, x), x) - f` to 0, while the same `ratsimp` in the next statement, or after
resetting the two globals, gives 0.

Reproduction: `probes/readme-examples/02-rat-state-leak.mac` →
`probes/readme-examples/02-rat-state-leak.out` (2026-09-26, build
`branch_5_50_base_84_g4204fb669`):

```
top state [0,0]          -- length(varlist), length(genvar) at top level
before [0,0]
after rubi [8,8]         -- same statement, after rubi returned
no reset false           -- is(ratsimp(diff(rr, x) - g) = 0)
reset true               -- same, after (setq varlist nil genvar nil)
```

Ruled out: no Maxima option variable changes across the call (radexpand, logexpand, domain,
algebraic, ratvars, ... checked), the sign cache (`clearsign()` does not help), dynamic capture of
the caller's locals (the answer is `=`-equal inside and outside the block).

## Who is affected

- **Not the corpus harness**: the driver assigns `mr_r: rubi(...)$` in its own statement and
  verifies in later ones.
- A user who calls `rubi` inside a function, `block` or loop and simplifies the answer in the
  same statement: a correct answer can look unverifiable. Possibly also a nested `rubi` call
  inside the package: the rest of the outer computation runs with the inner call's varlist.

## Likely cause, to confirm

Some package code (Lisp, or a Maxima function calling a rat entry point that pushes onto
`varlist` without binding it, e.g. `newvar` / `ratsetup` paths reached outside `ratsimp`'s own
binding) extends the global `varlist`/`genvar`. Find it by bisecting: check the two lengths
before and after individual utility calls on this integrand's rule route.

## Fix direction

Bind `varlist` and `genvar` to nil around the `rubi` entry (the Lisp dispatcher's top-level
call), as Maxima's own top level does per statement. Then check that nested calls do not depend
on the leak. Gate: the probe's `no reset` line becomes true; Layer A; a corpus A/B, since the
package's internal `ratsimp` results could change.
