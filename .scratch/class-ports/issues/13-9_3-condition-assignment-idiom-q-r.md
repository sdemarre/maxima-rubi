# 9.3 r18/r22/r23/r24: Rubi's condition-assignment idiom ported as an EQUATION — guard vacuous, `q`/`r` leak into the answer

Status: needs-triage
Type: bug (HIGH — unguarded rule + free symbols in the answer)
Filed: 2026-09-22 (found by the section-9 port's Task 12 end-to-end gate, branch `section9-port`, `346c513`)

## The finding

Four 9.3 records use Rubi's condition-assignment idiom, in which the `/;` test
BINDS a variable that the right-hand side then uses:

```mathematica
(* IntegrationRules 9.3, the "derivative divides" family, e.g. r18 *)
Int[u_*v_^m_.*(a_.+b_.*y_^n_)^p_., x_Symbol] :=
  q*r*Subst[Int[x^m*(a+b*x^n)^p, x], x, y] /;
 FreeQ[{a,b,m,n,p},x] && Not[FalseQ[r=Divides[y^m,v^m,x]]] &&
                         Not[FalseQ[q=DerivativeDivides[y,u,x]]]
```

The generated Maxima is (`rules/class9/9_3.mac:146,149`, r18; r22/r23/r24 are
identical in shape):

```maxima
/* cond */ ... and block([_mr_9_3_r18_q, _mr_9_3_r18_r],
             is(not(%mr_falseQ(_mr_9_3_r18_r=%mr_divides(_mr_9_3_r18_y^..., ..., x)))
            and not(%mr_falseQ(_mr_9_3_r18_q=%mr_derivativeDivides(...))) ) = true)
/* repl */ block([_mr_9_3_r18_q, _mr_9_3_r18_r],
             _mr_9_3_r18_q*_mr_9_3_r18_r * %mr_subst(mr_int(...), x, _mr_9_3_r18_y__s))
```

Two defects, both from `=` being EQUALITY in Maxima, not assignment:

1. **The guard is vacuous.** `_mr_9_3_r18_r = %mr_divides(...)` builds an
   *equation object*; `%mr_falseQ(u) := is(u = false)`
   (`maxima_rubi_utils.mac:5032`) is false for any equation, so
   `not(%mr_falseQ(...))` is TRUE whatever `%mr_divides` /
   `%mr_derivativeDivides` return. The record therefore fires on **every**
   integrand its pattern matches — including ones where the derivative does
   not divide, which is the whole point of the test.
2. **`q` and `r` leak.** The repl re-declares them as fresh block locals and
   never assigns them, so the answer is literally multiplied by two unbound
   symbols.

## Measured witness

MEASURED 2026-09-22, build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7,
`load("maxima_rubi.mac")$ mr_load_all()$`:

```maxima
rubi(((sqrt(x)+1)*x - 2*sqrt(x) - 2)/(sqrt(x)+1)^2, x)
```

| tree | answer |
|---|---|
| `master` (`c95c6ed`) | `'unintegrable[((sqrt(x)+1)*x-2*sqrt(x)-2)/(sqrt(x)+1)^2, x]`, 2 s |
| `section9-port` (`346c513`) | `_mr_9_3_r18_q*_mr_9_3_r18_r*(<a degree-49 numerator>)/(<a degree-48 denominator>)`, 2 s |

`rubi_verbose` shows `rule 9_3 r18 fired on ((sqrt(x)+1)*x-2*sqrt(x)-2)/(sqrt(x)+1)^2`.

Downstream cost: this is on the route of spec A4's r38 observation entry
`x/(1 + sqrt(2 + 3*x))`, which on `master` answers in 2 s (the malformed noun
`'unintegrable[(3*x)/(sqrt(3*x+2)+1),3*x+2]/9`) and on `section9-port` runs
280 s and then dies with SBCL "Heap exhausted, game over" — the trace's last two
firings are `9_3 r18` and then `9_1 r28` on the same expression in two
spellings (`(sqrt(x)+1)^2` vs `x+2*sqrt(x)+1`).

## Scope

Exactly four records, all in `rules/class9/9_3.mac`, found by scanning every
generated rule file for the equation-inside-`%mr_falseQ` shape:

```sh
grep -o "%mr_falseQ(_mr_[A-Za-z0-9_]*=" rules/class*/*.mac | sort | uniq -c
# => 9_3 r18 q,r ; 9_3 r22 q,r ; 9_3 r23 q,r ; 9_3 r24 q,r  (8 hits, one file)
```

A separate scan for repl-block locals that are *used but never assigned* finds
the same four records plus 28 class-1 records whose unassigned local is an
`mr_sum` lambda parameter (`_k`, `_i`, `_j`) — those are correct, not leaks.

## Suggested fix (NOT applied here — Task 12 is the gate, and its brief
regenerates no rule file)

The cond and the repl are separate Maxima functions, so the binding cannot be
carried across; each must do the assignment itself, in `and` order so the
short-circuit still holds:

```maxima
/* cond */ block([_mr_9_3_r18_q, _mr_9_3_r18_r],
             _mr_9_3_r18_r : %mr_divides(...),
             is(not(%mr_falseQ(_mr_9_3_r18_r))
                and (_mr_9_3_r18_q : %mr_derivativeDivides(...),
                     not(%mr_falseQ(_mr_9_3_r18_q)))) = true)
/* repl */ block([_mr_9_3_r18_q, _mr_9_3_r18_r],
             _mr_9_3_r18_r : %mr_divides(...),
             _mr_9_3_r18_q : %mr_derivativeDivides(...),
             _mr_9_3_r18_q*_mr_9_3_r18_r * %mr_subst(...))
```

That is a `generator/generate_rules.py` change plus a class-9 regeneration, a
new closed exception in the P3 static gate's list, and Layer A targets pinning
both the guard and the absence of free symbols in the answer.

## Guard to add with the fix

The end-to-end gate `test/test_section9_e2e.mac` should grow a target asserting
`freeof(<every rule-local symbol>, answer)`; the cheapest general form is to
reject an answer that mentions any symbol whose name starts `_mr_`.
