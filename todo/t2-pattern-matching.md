# T2 — Pattern matching in Maxima

Status: open
Doc: `docs/pattern-matching-feasibility.md`
Depends on: T1 (the pattern grammar to probe against)

## Questions to answer

0. (Answered 2026-08-17, correction to the initial assumption) There is
   no `match`/`matchfix`/`matchfree` + `%`/`%%` machinery in this build:
   `match` is unbound in a bare session, `matchfix` errors, and the
   manual has no topic "match". The real documented machinery is the
   rule system: `matchdeclare` (named pattern variables + lambda
   predicates), `defmatch`, `defrule`, `apply1`/`apply2`/`applyb1`,
   `letsimp`, rule packages (manual topic "Functions and Variables for
   Rules and Patterns"). Also measured the same day: in this build
   `'f(args)` quotes the function symbol only — arguments still
   evaluate (`f : 99; 'f(1+1)` displays `f(2)`) — a trap for any
   quoted pattern work; and `version`/`version()` are unbound —
   `build_info()` is the way to stamp builds.

1. Route A: how far does the rule system cover T1's Rubi rule grammar —
   named capture, multiple captures, conditions, subexpression vs
   whole-expression matching, bound-variable use in replacements?
   Per-feature verdict: `builtin ok` / `extendable` / `must build`.
2. Design sketch of whatever must be built (Lisp-level is the working
   hypothesis — Maxima's expression trees are Lisp data), its semantics
   contract, and coverage measured against the *actual* first-class
   patterns.
3. Route B: does the Rubi-5 if-then-else decomposition (42 `Int*nnn`
   for algebraic, only Int111/Int121 implemented, a claimed
   Mathematica→Maxima decision-tree translator) change the answer?
   Cost of obtaining the other 40 functions; does the top-level
   `Int[u, x]` classifier need pattern matching at all?
4. MockMathica: assess `jlapeyre/mixima` (Mathematica→Maxima porting
   tools, Common Lisp) and any other informative mockmma clone for
   pattern-matching / syntax-handling design ideas. Design transfer,
   not porting.
5. Go/no-go across routes — one, the other, or a mix (e.g. route B for
   milestone 1's class, route A for the long-term port) — and at what
   cost. Feeds T5.

## Evidence

