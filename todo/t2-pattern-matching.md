# T2 — Pattern matching in Maxima

Status: open
Doc: `docs/pattern-matching-feasibility.md`
Depends on: T1 (the pattern grammar to probe against)

## Questions to answer

1. What exactly do `match` / `matchfix` / `matchfree` / `matchdeclare` and
   the `%` / `%%` wildcards do? (Probed, not assumed — see AGENTS.md
   for the lookup discipline.)
2. Per-feature verdict against T1's rule grammar — named subexpression
   capture, multiple wildcards, guarded conditions, whole-expression vs
   subexpression matching: each is `builtin ok` / `extendable` / `must build`.
3. Design sketch of the matcher we would build (Lisp-level is the working
   hypothesis — Maxima's expression trees are Lisp data), and its
   semantics contract.
4. Coverage: what fraction of the *actual* first-class patterns are
   expressible with builtins + the sketch?
5. Go/no-go and cost of the matcher as part of milestone 1.

## Evidence

