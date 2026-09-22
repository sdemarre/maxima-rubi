# 9.3 r18/r22/r23/r24: Rubi's condition-assignment idiom ported as an EQUATION — guard vacuous, `q`/`r` leak into the answer

Status: fixed (Task 12b, 2026-09-22 — see Resolution)
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

## Resolution (Task 12b, 2026-09-22, branch `section9-port`)

Status: fixed.

**What changed.** `generator/generate_rules.py` now recognises the idiom
STRUCTURALLY — an assignment, inside a rule condition, to a name the
enclosing `With`/`Module` declares WITHOUT an initialiser — never by rule
number (`_condition_assignments`, `_scope_bare_locals`,
`_hoist_scope_assigns`, `_assign_in_test`):

* **cond**: the assignment stays exactly where the condition puts it and
  `=` becomes `:`. Maxima's `and` short-circuits, so the upstream `&&`
  order still holds and the expensive `DerivativeDivides` is skipped when
  `Divides` already declined (measured: `is(not(f(r:g(false))) and
  not(f(q:h(7))))` never calls `h`). An argument-position assignment is
  legal Maxima and values to the assigned value.
* **repl**: the cond and the repl are separate Maxima functions, so the
  binding cannot cross; the repl repeats the assignments as scope
  initialisers, leading the locals list in the condition's order, and
  `_scope_block` emits them as sequential `name : value` statements.

Anything else that looks like an assignment in a condition — to a
capture, to an already-initialised local, in the OUTER condition where no
scope exists, or the same name twice — is now a `GenError`, so a future
variant fails loudly instead of emitting an equation.

**Scope, re-confirmed.** `grep -rn "FalseQ\[[a-zA-Z]*="
reference/rubi/Rubi/IntegrationRules/` still hits only 9.3 (4 lines:
:145, :177, :185, :193). `grep -o "%mr_falseQ(_mr_[A-Za-z0-9_]*="
rules/class*/*.mac` was 8 hits in one file, now 0. Regenerating classes
1/2/3/4/6 and the rewrite table raised nothing and left them
byte-identical (`git status --porcelain rules/` names only
`rules/class9/9_3.mac`) — the generator's own loud check is a second,
independent confirmation that no other class carries the idiom. The
repl-block "used but never assigned" scan now finds only the 32 class-1
`mr_sum` loop variables (`_k`, `_i`, `_j`) and the 5 `1_2_2_3` r86/r87
`aa`/`bb`/`cc` placeholders, which are substituted by name and are
correct.

**Measured (2026-09-22, build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7).**

| gate | before | after |
|---|---|---|
| Layer A `test_maxima_rubi.mac` | `1287 passed, 5 failed` (7 new targets, 5 RED) | `1292 passed, 0 failed` |
| `test/test_section9_e2e.mac` | `4 passed, 1 failed` | `5 passed, 0 failed` |
| `test/test_rule_table_order.mac` | 11/0 | `11 passed, 0 failed` |
| `python3 test/check_generated_rules.py` | 23/0 | `23 passed, 0 failed` |

No new closed exception was needed in the P3 gate: class 9 is post-P0, so
checks 1-5 (the byte-identity diff and its exception list) do not run over
it; check 7 (the declared class total, 86) and check 6 (every pattern
string prepares) are unchanged by this fix.

Rules core rebuilt: 3,997 rules, fingerprint `434c241ad6c11e1b152b9b1bc1469214`.

**The witness.** `rubi(((sqrt(x)+1)*x - 2*sqrt(x) - 2)/(sqrt(x)+1)^2, x)`
no longer leaks `_mr_9_3_r18_q*_mr_9_3_r18_r`. It now answers
`((2*sqrt(x)-3)*x - 6*sqrt(x) + 6*log(sqrt(x)+1))/3`, which verifies
(`ratsimp(diff(F,x) - f) = 0`; residual 2e-16 at x = 0.3 and 1.7) — better
than `master`, which returns the unintegrable noun: with r18 no longer
firing unguarded, the integrand reaches the records that can do it.

**The downstream entry.** `rubi(x/(1 + sqrt(2 + 3*x)), x)` ran 280 s and
died with "Heap exhausted, game over" before the fix. It now answers in
**1.5 s** with `(6*log(sqrt(3*x+2)+1) + x*(6*sqrt(3*x+2)-9) -
2*sqrt(3*x+2) - 6)/27`, which verifies (`ratsimp(diff(F,x) - f) = 0`).
So for THIS entry the heap exhaustion was caused by this defect — r18
firing unguarded put the rule set into the two-spelling loop the trace
showed — and not by issue 11, which remains open on its own witnesses
(the e2e gate's amendment-A5 integrand still exhausts the heap on master
too, and is untouched by this fix).

**What remains.** Nothing for this ticket. The Task 13 A/B measurement can
now be taken against a guarded rule set.
