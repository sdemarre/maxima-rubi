# T4 — Rule translation (algebraic class)

Status: open
Doc: `docs/rule-translation.md`
Depends on: T1 (rule grammar + utility inventory), T2 (route decision:
rule-system/matcher vs if-then-else vs mix, and what each provides)

## Questions to answer

1. Which of the algebraic class's rules translate mechanically from the
   .m syntax, and which need hand-ported conditions?
2. The support-function surface this one class actually needs (T1's
   inventory, sliced down).
3. The rule-file format and loader for the ported package (readable .mac
   data, a Lisp table, or a hybrid), with reasons.
4. The translation procedure — mechanical (scriptable) vs manual steps —
   so that porting class 2 onward reuses it.
5. Translation references: `sympy_rubi`'s mapping of the .m rules onto
   SymPy's `Wild` machinery; if route B, Rubi-5's `Int111`/`Int121`
   as manually-compiled templates.

## Evidence

