# T5 — Package and harness architecture

Status: done
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

All claims in `docs/package-architecture.md`; the inputs it consumes:

- T2 §3 trap catalog + §4 runner contract + §5 cost
  (`docs/pattern-matching-feasibility.md`);
- T4's generated format (T4 §3) and shim/`%mr_` decision (T4 §6);
- T3's harness mechanics and measurements
  (`todo/t3-corpus-baseline.md` evidence, the probe docstrings);
- `~/src/diophantine` read 2026-08-18: `%dio_load_sibling` + witness
  idiom, `diophantine_verbose`, the `Results:` protocol, the
  quote-on-both-sides house rule, the single-line `:lisp` constraint;
- same-session probe (2026-08-18): `?fboundp`/`errcatch`/
  `load_pathname`(=false under `-b`)/`sconcat` all work in the
  installed build.

Decisions recorded there: `rubi(f, x)` API with `integrate`
fall-through noun; flat diophantine-mould layout with no `.lisp` in
milestone 1; two-layer harness (batch unit suite + per-integral
subprocess corpus driver, shared `Results:` protocol); ten house
rules, each trap-cited. Open for the implementation phase: load-time
`defmatch` wall (first measurement), recursion cap, zero-chain
strengthening.
