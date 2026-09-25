# Earlier classes' recursive Int calls go through the %mr_atanh/%mr_asinh/%mr_acosh log-form shims, so they cannot reach class 7

Status: needs-triage
Type: bug (a recursion that cannot reach the class written for it; answers
correct but in log form)
Filed: 2026-09-25 (class-7 port, Step 2 — ticket 04)

## The finding

`generator/translation_table.py` renames `ArcTanh` / `ArcSinh` / `ArcCosh`
to `%mr_atanh` / `%mr_asinh` / `%mr_acosh` (class 1: "this binary lacks the
name"). Those are `:=` functions (`maxima_rubi_utils.mac` L3125-3132) that
evaluate at once to their log forms: `%mr_atanh(u) = 1/2 log((1+u)/(1-u))`,
`%mr_asinh(u) = log(u + sqrt(u^2+1))`. The natives `atanh` / `asinh` /
`acosh` are bound in the installed build, differentiate through the zero
chain and float-evaluate (probes/answer-side/06-class7-answer-side-identities.out
A1-A3, E1-E3), so the reason for the shims no longer holds.

Class 7's rules recurse on the three heads, so the class-7 port emits the
natives through a per-class override (`CLASS_RENAME[7]`, ticket 04 Step 2).
The earlier classes keep the shims, which is harmless in an ANSWER (the log
form differentiates to the same thing) but not inside a recursive `mr_int`:
the integrand handed on no longer carries the head the class-7 patterns
name (probe 06 K1/K2). Measured 2026-09-25 on the committed rule files,
shim uses inside an `mr_int(...)` argument:

| class | shim uses | inside `mr_int` | site |
|---|---|---|---|
| 1 | 51 | 0 | — |
| 3 | 2 | 1 | 3_1_3 r14: `mr_int(%mr_asinh(Rt[e,2] x/Sqrt[d])/x, x)` — Rubi routes it to 7.1.2's `Int[(a+b ArcSinh[c x])^n/x]` |
| 5 | 4 | 1 | 5_3_2 r3: `mr_int((a+b atan(c x))^(p-1) %mr_atanh(1-2/(1+I c x))/(1+c^2 x^2), x)` |
| 9 | 2 | 0 | — |

(`grep -oP 'mr_int\(…%mr_a(tanh|sinh|cosh)\('` over `rules/class{1,3,5,9}`,
three levels of nested parentheses.)

The shims also make the earlier classes' answers log forms where the corpus
expects `atanh`/`asinh`/`acosh`: such an answer can verify by
differentiation but can never be `expected` (form-identical).

## Why not fixed in the class-7 port

Switching the shared RENAME rows to the natives changes the generated text
of classes 1/3/5/9 (59 sites), i.e. every accepted record's rule files and
core fingerprint: a re-measurement of four classes, not a small fix. Moving
only the two recursive sites is a generator exception list of its own. Both
are decisions for the coordinator / user.

## Options

1. Replace the three RENAME rows with the natives for every class
   (`CLASS_RENAME` then disappears), regenerate, re-run classes 1/3/5/9 and
   A/B.
2. Keep the shims in answers, natives inside `Int[...]` arguments only (an
   emitter rule: a shim head under an `Int` argument emits the native).
3. Leave as is (the two recursive sites decline into whatever the log form
   matches).
