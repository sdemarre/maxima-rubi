# Earlier classes' recursive Int calls go through the %mr_atanh/%mr_asinh/%mr_acosh log-form shims, so they cannot reach class 7

Status: fixed (2026-09-25, branch `class-ports-fixes`, option 1)
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

## Resolution (2026-09-25, branch `class-ports-fixes`)

User decision: **option 1** -- native `atanh` / `asinh` / `acosh` in every class.

- `generator/translation_table.py`: the three RENAME rows emit the natives; `CLASS_RENAME[7]` is gone
  (redundant). Regenerating every class (1-9, `--rewrites`) changes 75 sites in 20 files: class 1 51,
  class 3 2, class 4 16 (not in the table above -- class 4 was ported after it was measured), class 5 4,
  class 9 2; classes 2/6/7/8 and the rewrite tables unchanged. Every changed line differs from the
  committed text only by `%mr_a(tanh|sinh|cosh)(` -> the native call (checked file by file).
- The P3 static gate admits it as a closed exception: `undo_native_heads` puts the shim spelling back on
  the new body before the byte comparison, count pinned at 53 (class 1's 51 + class 3's 2; the other
  classes have no P0 base text). `Results: 27 passed, 0 failed`.
- The shims stay defined in `maxima_rubi_utils.mac`: their own Layer A units (`test_cluster_h_shims`)
  still call them; no generated rule, rewrite table or utility does.
- Answer side. `atanh(1)` errors (probe 06 N1) exactly as the shim's log body did (division by zero), so
  no new error path; Maxima's odd-symmetry simplification (`atanh(-u) -> -atanh(u)`) and `logarc:false`
  leave the natives in place (probe 06 S11-S13). No condition used a shim (grep: 0 `_mr_cond_` sites).
- Layer A `test_native_inverse_hyperbolic` (8 checks, 5 RED on the old rule files): 3_1_3 r14 and
  5_3_2 r3 recurse on the native heads; 1_1_3_1 r20 / r27 answer `atanh(x)` / `asinh(x)` (were log
  forms); 3_1_3 r14 on `log(x)/sqrt(1+x^2)` now reaches 7.1.2 (no noun, keeps `asinh`, derivative
  checked at two points). Layer A 1519 -> 1527.
- The corpus re-measure of classes 1/3/4/5/9 is still owed; a slice A/B is
  `probes/corpus/27-class-ports-fixes-slice-ab`.
