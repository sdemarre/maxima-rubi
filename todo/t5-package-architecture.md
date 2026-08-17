# T5 — Package and harness architecture

Status: open
Doc: `docs/package-architecture.md`
Depends on: T1–T4 (consumes all of them)

## Questions to answer

1. The public API: function name (working name `rubi(f, x)`), result shape
   (antiderivative, or the noun `%integrate` form when no rule fires),
   and a verboseness/debug switch.
2. The load story, in the diophantine mould: one `.mac` that loads its
   sibling `.lisp` file(s) itself, findable via search-path push or
   `~/.maxima/`.
3. The test harness: a `maxima --very-quiet -b` driver over the corpus
   sections, with a per-integral timeout, `PASS:`/`FAIL:` lines and a final
   `Results: <n> passed, <m> failed` line (the diophantine protocol);
   verification by differentiation, with exact-match against the expected
   answer as the secondary check.
4. The house rules the implementation will live under (symbol hygiene,
   quoting conventions) — informed by what T2's probes found to be traps.

## Evidence
