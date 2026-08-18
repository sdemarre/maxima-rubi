# T4 — Rule translation (algebraic class)

Status: done
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

All claims in `docs/rule-translation.md`; re-runnable:

- Q1/Q2 — `sh probes/translation/01-class1-syntax-census.run` (2,710
  rules / 67 loaded files; 2031 AUTO / 679 = C-tier-predicate rules;
  37 C-tier tokens; optional histogram; token tiers closed — zero
  unlisted).
- Q2 — `sh probes/translation/02-support-surface.run` (call-based;
  `boundp` is itself unbound so it is not usable for this).
- Q5 — SymPy port assessed at tag sympy-1.11 (`parsetools/parse.py`
  read in full; `github.com/sympy/rubi` confirmed); PRs #12978,
  #13257, #24315; removal noted in the 1.12 release notes.

Findings worth carrying into T5:
- `is(…)` returns a third value `unknown`; guards must treat it as
  not-true.
- Value-position comparisons stay unevaluated (`2 > 1` prints as
  `2 > 1`); guards must be `is(…)`-wrapped.
- The installed binary's manual lists names the binary has not bound
  (`atanh`, `elliptic_f`): manual lookup is not an existence test;
  the shim list is build-specific and must be re-measured on 5.50.
- SymPy's port was removed from sympy (2022) as broken — generation
  was never the hard part; verification against the corpus is.

