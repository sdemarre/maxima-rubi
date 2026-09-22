# Class 1 exhausts the SBCL heap on a quintic rational integrand (pre-existing)

Status: needs-triage
Type: bug (fatal, unrecoverable — SBCL "Heap exhausted, game over" → `ldb`)
Filed: 2026-09-22 (found by the section-9 port's Task 12 end-to-end gate, branch `section9-port`)

## The finding

`rubi(2*x/(x^5+x^4+2*x^3+x-1), x)` — a plain rational integrand whose
denominator factors as `(x^2+1)*(x^3+x^2+x-1)` — does not terminate. It allocates
until the SBCL dynamic space (1 GB in the installed core) is exhausted and the
runtime dies with the **uncatchable** fatal error:

```
fatal error encountered in SBCL pid <n> tid <n>:
Heap exhausted, game over.
ldb> Welcome to LDB, a low-level debugger for the Lisp runtime environment.
```

MEASURED 2026-09-22, build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7,
`load("maxima_rubi.mac")$ mr_load_all()$`:

| tree | commit | wall to the fatal error |
|---|---|---|
| `section9-port` | `346c513` | 394.7 s |
| `master` (worktree `/home/serge/src/mr-s9-ref`) | `c95c6ed` | 402.2 s |

**It reproduces on master, with no class-9 rule loaded at all** — a pre-existing
class-1 defect. The section-9 port neither causes it nor makes it worse; it only
opens a new ROUTE to it (see below).

## Why it was found now

Spec `docs/superpowers/specs/2026-09-22-section9-port-design.md` A4 lists
`1/(x + sqrt((1+x)/(1-x)))` as a RED-on-master end-to-end target for the new
9.3 `SubstForFractionalPowerOfQuotientOfLinears` record (`9_3 r38`). The record
fires and substitutes CORRECTLY —

```maxima
%mr_substForFractionalPowerOfQuotientOfLinears(1/(x + sqrt((1+x)/(1-x))), x)
  =>  [x/(x^5+x^4+2*x^3+x-1), 2, (x+1)/(1-x), 2]
```

— i.e. it hands class 1 exactly the integrand above. So on `section9-port` that
spec target no longer returns `unintegrable` in 2 s; it runs 6-7 minutes and
kills the Maxima process. Task 12 therefore keeps the record's gate target but
uses `1/(1 + sqrt((1+x)/(1-x)))`, which routes through the same `9_3 r38`
(verbose-traced), is equally RED on master, and answers in 2 s.

## Why it matters

- **A fatal SBCL error is not a verdict.** The corpus driver caps CPU, and a
  process that dies in `ldb` waits on stdin rather than exiting — which is why
  the driver gives entry subprocesses `/dev/null` for stdin
  (AGENTS.md, `probes/matcher/09-harness-fault-verdict.out`). Anything that
  inherits an open stdin (a developer running a `.mac` file by hand) sees a
  process that burns no CPU and produces no output: indistinguishable from a
  hang. That is exactly how this defect first presented.
- Section 9's new substitution records will reach more integrands of this
  shape, so the Task 13 corpus A/B should be read with this in mind: entries
  that newly route through `9_3 r37`/`r38` can turn a fast `unintegrable` into
  a heap death.

## Reproduce

```sh
cd /home/serge/src/maxima-rubi
cat > /tmp/heap.mac <<'EOF'
load("maxima_rubi.mac")$
mr_load_all()$
print(rubi(2*x/(x^5+x^4+2*x^3+x-1), x))$
EOF
maxima --very-quiet -b /tmp/heap.mac < /dev/null     # ~400 s, then the fatal error
```

Always redirect stdin from `/dev/null`; and `timeout` does NOT kill the `sbcl`
grandchild (maxima forks it), so use `setsid` + `killpg`.

## Not yet done

Which class-1 rule loops is not established. The `rubi_verbose` trace
(2.8 MB for the section-9 route) churns in `1_2_1_3` r11/r15/r16/r18 over
algebraic-number coefficients such as
`(16*3^(3/2)*sqrt(11)+272)/3)^(1/3)` — i.e. after the cubic factor
`x^3+x^2+x-1` has been solved by radicals — so the partial-fraction /
`ExpandIntegrand` path over a non-rational splitting field is the place to
look first.
