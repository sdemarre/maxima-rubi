# %mr_coeff drops a constant term that is not an atom (Coefficient[u,x,0] wrong for log/sqrt constants)

Status: needs-triage
Type: bug (silently wrong coefficient, pre-existing, all classes)
Filed: 2026-09-22 (found by the section-9 port's Task 9 review, branch `section9-port`)

## The finding

`%mr_coeff(u, x, 0)` — the port of Rubi's `Coefficient[u, x, 0]` — returns 0 for a
constant term that is x-free but NOT an atom. MEASURED 2026-09-22 on
`branch_5_50_base_84_g4204fb669`, full `load("maxima_rubi.mac")`:

| call | `%mr_coeff` | correct | Maxima's `ratcoef` |
|---|---|---|---|
| `%mr_coeff(log(4)+x, x, 0)` | **0** | `log(4)` | `log(4)` |
| `%mr_coeff(sqrt(2)+3*x, x, 0)` | **0** | `sqrt(2)` | `sqrt(2)` |
| `%mr_coeff(a+x, x, 0)` | `a` | `a` | `a` |
| `%mr_coeff(2+x, x, 0)` | `2` | `2` | `2` |

Root cause: the term walker `%mr_term_xexp` (`maxima_rubi_utils.mac:1343-1390`)
has cases for an atom and for `-`/`*`/`/`/`^` nodes, and falls through to
`false` for any other x-free term, which the caller reads as "not a constant
term". A bare `log(4)`, `sqrt(2)`, `atan(3)` or similar is exactly that shape.

## Why it matters beyond section 9

`Coefficient` is one of the most-used tokens in the rule set, and the linear /
binomial / quadratic coefficient predicates are built on it. A wrong constant
term is a SILENTLY WRONG answer, not an error: the rule fires and returns an
antiderivative that differs by the dropped constant's contribution. The
section-9 Task 9 review found it through `%mr_functionOfLinear(4^(2*x+1), x)`,
which answered `[%e^x, 0, 2*log(4))]` (a = 0) where upstream gives
`a = log(4)`; the same walker is reached from class 1/2/3/6 conditions.

## To do

Not fixed in the section-9 port (ruling 2026-09-22): the blast radius is every
class, so it needs its OWN four-class A/B rather than riding along with a port
whose A/B is being read for other reasons. The section-9 ports work around it
locally instead (see `%mr_functionOfLinear`'s comment).

1. Add the generic x-free fallback to `%mr_term_xexp` (or re-point `%mr_coeff`'s
   degree-0 case at a `freeof` test) with Layer A targets for `log`/`sqrt`/
   `atan` constant terms.
2. A/B classes 1/2/3/6 against the pre-fix core with `test/ab_records.py`, and
   attribute every transition — some currently-verified entries may be passing
   BECAUSE both sides drop the same constant.

## Comments
