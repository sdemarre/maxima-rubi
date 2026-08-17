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

- 2026-08-17, builtins audit (probe `probes/maxima/probe-builtin-audit.run`
  → `.out`), build branch_5_49_base_796_g60186bb22_dirty (2026-07-28),
  SBCL 2.6.7. UNBOUND in this build (stays a noun): `head`, `car`,
  `cdr`, `boundp`, `functionp`, `position`, `index`, `element`,
  `null`, `lconcat`, `lappend`, `lpart`, `explode`, `together`,
  `apart`, `simplify`, `cancellist`, `fractpart`, `get_seconds`,
  `catch_error`, `file_namestring`, `den`. Manual confirms: no topic
  for `head`/`car`/`boundp`/`functionp`/`position` (list sense)/
  `null`/`together`/`apart` — these are not Maxima functions (the
  only `position` topic is a 3d-graphics object option). Workarounds
  that WORK and are measurement-verified: `part(x, i)`,
  `freeof`, `atom`, `listp`, `symbolp`, `member`, `delete`,
  `adjoin` (sets), `unique`, `sort`, `setdifference`, `intersection`,
  `is`, `integerp`, `numberp`, `ratsimp`, `rat`, `num`, `denom`,
  `expand`, `factor`, `trigsimp`, `resimplify`, `diff`, `mod`,
  `floor`,   `catch`/`throw`, `concat`/`sconcat` (string concat; `+`
  is SUM, never concatenation). 2026-08-17 addition from the corpus
  probes: `stringmatch` is also unbound (stays a noun). Traps: `numer`
  is an option variable
  — calling `numer(expr)` is a fatal Lisp error; `sublist` is bound
  but returned `[]` for both `sublist([a,b,c],{1,2})` and
  `sublist([a,b,c],[1,3])` (do not rely on it); `adjoin` needs set
  arguments (errors on lists); one Lisp error aborts a `-b` batch
  run. `string(build_info())` prints a `?%build_info(...)` form;
  `disp(build_info())` is the clean form.

