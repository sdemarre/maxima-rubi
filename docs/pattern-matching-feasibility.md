# Pattern-matching feasibility in Maxima (T2)

Answers, for the research phase, which pattern-matching route can execute
Rubi 4's rule grammar inside Maxima, at what cost. Built on, and citing:

- `probes/maxima/probe-rule-system.mac` / `.out` — route-A feature matrix
  (run `sh probes/maxima/probe-rule-system.run`);
- `probes/maxima/probe-rule-system-time.mac` / `.out` — per-match cost
  (run `sh probes/maxima/probe-rule-system-time.run`);
- `probes/maxima/probe-builtin-audit.mac` / `.out` — builtin availability;
- T1 doc `docs/rubi-architecture.md` — the grammar being probed;
- `jlapeyre/mixima` (master, last pushed 2024-05-08, GPLv2) — assessed
  2026-08-17 via its public files (README.md, README.translator, TODO,
  translator/match.lisp, translator/mma-to-mixima.lisp,
  translator/our_mma_tests/patterns.m).

Everything below was measured on
`branch_5_49_base_796_g60186bb22_dirty` (2026-07-28), SBCL 2.6.7,
2026-08-17. Maxima startup on this machine is 31–32 ms (measured,
`probe-rule-system-time.out`).

## 1. Q0 status — what machinery exists

There is **no `match`/`matchfix`/`matchfree` machinery** in this build
(`match` unbound, `matchfix` errors, no manual topic). The documented,
working machinery is the **rule system** (manual topic "Functions and
Variables for Rules and Patterns"): `matchdeclare` (declare pattern
variables with `true`, a predicate-function name, or a lambda),
`defmatch` (compile a pattern into a test function), plus the
subexpression-rewrite drivers `apply1`/`apply2`/`applyb1` and
`letsimp`. Measured same day: `version`/`version()` are unbound —
`build_info()` is the build stamp; `'f(args)` quotes the function symbol
only, arguments still evaluate.

## 2. Q1 — feature matrix, route A against the Rubi grammar

Verdicts: `builtin ok` (works as-is), `extendable` (works via a thin,
measured idiom), `must build` (no counterpart).

| Rubi grammar feature (T1 §2) | route A | probe |
|---|---|---|
| named capture `a_` | builtin ok | T1, T7 |
| capture predicates (`x_Symbol`-style, `FreeQ`-style, `IntegerQ`) | builtin ok — `matchdeclare` takes a lambda, a function name, or `true` | T5, T5b, T6 |
| multiple captures, nontrivial matched forms | builtin ok | T2, T9 |
| repeated capture must agree (`x__`-less reuse) | builtin ok — inconsistent binding is rejected | T3, T3b |
| undeclared symbol in pattern is a literal | builtin ok | T4a, T4c |
| integration variable referenced by pattern (`x_Symbol`) | builtin ok — `defmatch`'s pattern-argument slot binds it to the caller's variable and the capture list records `x = <var>` | T15a–c |
| function head (kernel) in the pattern (`Log[...]`, `Sinh[...]`) | builtin ok | T8 |
| class-1 workhorse `(a+b x)^m (c+d x)^n` | builtin ok — all five slots captured, capture in no order | T9 |
| failure returns `false` | builtin ok | T10 |
| replacement evaluated with the captures | extendable — rebind the captured values in a `block` before evaluating the replacement (measured idiom, T11); also defeats the global side-effect binding | T11 |
| whole-rule `/;` condition (a Maxima boolean over the captures) | must build — no pattern-level condition; the runner applies a per-rule condition function after a successful match (a trivial build; see §4) | — |
| ordered whole-expression dispatch, first match wins | must build — the runner; `apply1`/`apply2`/`applyb1` are subexpression-rewrite drivers, not whole-expression dispatch | T12 (dispatch model) |
| optional default `a_.` | **must build** — no counterpart exists; see §4.3, the dominant translation burden | — |

The matcher is fast (0.007 ms per match, §5), so the decision is not
about speed: every matcher capability the grammar needs is either
present or a thin build. The one structural gap is `a_.` — the feature
used by 3210 of the 3258 column-0 `Int[... , x_Symbol]` rules in the
class-1 rule files (measured 2026-08-17).

## 3. Measured semantics that differ from the documentation's
    comfortable reading

Each item below is in the probe `.out`; each one bit a first draft of
this probe.

1. **`filter` does not evaluate.** `filter(lambda([qq], ...), list)` —
   and even `filter(namedfn, list)` — returns itself as an unevaluated
   noun (T13a). Do not use `filter` in runner code; use `map` (which
   does evaluate lambdas, measured) or explicit recursion.
2. **A `block` is a sequence; `if cond then A` without `else` does not
   terminate it.** The block returns the value of its last expression
   (T13b). Every guard must be a value-carrying `if ... then ... else`,
   or use an explicit `return`.
3. **`is()` does not re-evaluate symbols it receives raw.**
   `is(3 = 'va)` is `false` even with `va` bound to 3 (the quote stops
   evaluation; `is` then treats the bare symbol as an unknown).
   Same-name comparison of two raw symbols is true. Capture-value
   lookup therefore compares names as raw symbols:
   `is(part(eq, 1) = 'name)` (T1/T2, via `geteqR`).
4. **`=` in value position stays an equation** (`2 = 2`, `qp = qp`,
   even `false = false` all remain equations), but **`if`-conditions
   evaluate equation conditions** (`if 0 = 0` fires; `if 0 = 1` takes
   the else, T16a/b). Booleans in value position need `is(...)`.
5. **The matcher decomposes algebraically.** `log(5 + 2*z)` matches
   `log(a + b*x)` with `a -> 2*z+5, b -> 0` (T8b); a `true`-predicate
   wildcard absorbs `z+5` as `x + (z - x + 5)` (T12 INFO). A
   `freeof(x)`-style predicate vetoes both (T4b, T8c). **Predicates
   must encode every intended restriction** — the matcher will find a
   legitimate-looking solve otherwise.
6. **Pattern variables are bound globally** as a side effect of a
   successful match; the capture list order is unspecified
   (`[pb = 2, pa = 3, x = x]`, T1). Rebind under a `block` before use
   (T11) and look values up by name (`geteqR`).
7. **Never `defmatch` from a killed name.** After `kill(pk)` a
   re-`defmatch` of the same pattern misbehaves: the new function
   returned `false` in the probe run and `true` in an isolated run
   (T14 INFO, non-deterministic); functions compiled before the `kill`
   keep working. Use fresh pattern-variable names per rule.
8. Batch-parser contract (all measured): a line ending in `,`
   continues; a line ending in `do` does not; `;`/`$` terminate; `+` is
   sum, use `concat` for strings; one Lisp error aborts the whole
   `-b` batch. `printf` is not C-style — emit machine lines with
   `disp(concat("TAG ", string(v), ...))`.

## 4. Q2 — the runner (what must be built)

The working hypothesis was "go to Common Lisp". **It is not needed**:
everything the runner needs was measured in pure Maxima (T1–T16).
Lisp-level matching (mixima's route, §7) is the fallback, not the plan.

### 4.1 Per-rule generated shape

Each Rubi rule `Int[<pattern>, x_Symbol] := <rhs> /; <cond>` becomes
(matcher + condition + replacement, all Maxima code):

```
matchdeclare(<pvars>, <predicates or true>)$
defmatch(<rmN>, <pattern-with-x-as-pattern-arg>, x)$
rcondN(p1, p2, ...) := <cond translated>$
rrepN(p1, p2, ...) := <rhs translated>$
```

### 4.2 Runner contract

Ordered, first-match-wins whole-expression dispatch (T12's model,
measured): for the family of rules matching an integrand shape, try
`rmN(u, x)` in file order; on the first non-`false` result, pull the
captures out of the equation list by name, evaluate the condition, and
on success rebind the captures in a fresh `block` and evaluate the
replacement (T11's idiom). No rule fires without its condition passing;
an unmatched integrand falls through to Maxima's own `integrate` (the
T3 baseline measures that fallback's yield). Rubi's re-dispatch (87% of
rules call `Int[...]` in the replacement) is plain expression
evaluation of the replacement — the runner does not loop.

Semantics contract for the generated code:

- a pattern variable with no predicate is declared `true` only when the
  Rubi rule intends an unbounded capture; every capture that Rubi
  guards with `FreeQ[{...}, x]` gets a `freeof(x)`, and captures
  Rubi leaves unguarded keep whatever restriction keeps the matcher's
  decomposition honest (§3.5) — this is checked rule-by-rule in T4,
  driven by the T3 corpus baseline as the yardstick;
- capture names are fresh per rule (T14);
- all booleans wrapped in `is(...)` (T13b);
- the replacement is evaluated with captures rebound locally, not with
  the matcher's global side effects (T11).

### 4.3 The `a_.` gap — options

`a_.` means: match the term, or omit it and bind the default (1).
Mathematica's matcher does this for Flat/Orderless heads; Maxima's does
not. Three emulations, in increasing order of mechanism cost:

- **N (normalize/slot extraction).** Before matching, the runner
  extracts the optional slot by computation: for the dominant shape
  `(a + b*x)^m`, test whether the base is linear in `x` (a
  freeof/structural check) and set `b` to the coefficient of `x` and
  `a` to the rest, binding the slot values directly instead of letting
  the matcher find them. Deterministic, no pattern blowup. Mirrors what
  Rubi 4 itself does in its normalization rules
  (`1.3.4 Normalizing algebraic functions`).
- **D (duplicate patterns).** Emit one `defmatch` per present/absent
  combination (2^n for n optional slots) and let the replacement
  supply the defaults. Simple; 8 variants for the workhorse, and
  several thousand extra matchers per 2710-rule class — paid at load
  time.
- **M (Lisp-level matcher extension).** Real Optional support in
  Maxima's matcher. This is exactly the design mixima's author sketched
  and abandoned (§7); it is the only option that handles exotic
  optionals uniformly, but it depends on internals of a matcher that
  5.50 is about to rewrite.

Recommendation for milestone 1 (feeds T4/T5): **N for the linear
shapes, D for the few-slot long tail, M only if T4's translation
measurements show N/D are the bottleneck.**

## 5. Cost of matching (measured)

`probe-rule-system-time.out` (2026-08-17): 2 × 100,000 calls of the
class-1 workhorse matcher — 100,000 matches, 100,000 non-matches — ran
in 1487 ms of work after subtracting the 32 ms startup: **0.007 ms per
match**, including the Maxima `for`-loop overhead. Even a family of
500 rules tried in the worst case is ~3.5 ms of matching, against
per-integral `integrate` walls of 0.3 s–30 s measured in the T3
baseline. **Matching cost is never the decision factor; rule-translation
effort and predicate correctness are.**

## 6. Q3 — route B: Rubi 5's if-then-else decomposition

From T1 §7 (Rubi-5.m at the pinned commit): 42 `Int*nnn` entry
functions for the algebraic classes; only **Int111 and Int121 are
implemented** (the other 40 are `Defer` placeholders); the 81
top-level dispatch rules are still written in Mathematica pattern
syntax; the plan doc claims a Mathematica→Maple/Maxima decision-tree
translator that is not in the repo and could not be verified.

Assessment: route B does not remove the matching problem — the
top-level classifier still needs either Mathematica patterns executed
somewhere or a re-derived structural classifier (a one-off case
analysis over integrand heads, feasible but a build in its own right),
and obtaining the other 40 functions means deriving their if-trees from
Rubi 4's rule files — i.e. doing T4's translation work in a more
verbose form, with no correctness advantage (if-trees and rule lists
are the same decision procedure in different notation). The if-tree
representation's real advantage (no matcher at all, uniform cost) pays
off only at full-classport scale. **Route B does not change the
milestone-1 answer; it is a re-visit candidate once class 1 is
measured on route A.**

## 7. Q4 — mixima (`jlapeyre/mixima`)

What it is: "Compatibility tools for porting from Mathematica to
Maxima" (README.md) — a Maxima-level compatibility-function layer
(`Table`, `Union`, …), a two-pass Common-Lisp source translator
(Mma source → Mma pseudo-lisp → Maxima pseudo-lisp → Maxima source),
and a Mockmma-derived interactive Mma shell. Version 0.25; last pushed
2024-05-08; the author scopes it explicitly: "DON'T EXPECT EVERYTHING
TO BE TRANSLATED WITHOUT MANUAL INTERVENTION", and its flagship
application "does not use advanced pattern matching" (README.md).
GPLv2; the Mockmma-derived parser files carry a separate permissive
notice.

Its pattern matcher (`translator/match.lisp`, self-described
"version 16") is a Common-Lisp recursive-descent matcher with
backtracking by frame-stack save/restore, per-head hash-table rule
sets, first-match-wins linear scan, and conditions evaluated at
rule-application time. Its documented capability list is the useful
artifact — and it **lacks exactly the feature Rubi depends on**:
"version ... does not include ... Optional", repeated names match
"identical items" only ("`f[x_,x_^2]` will match `f[a,a^2]`. But not
`f[3,9]`. (sorry)."), Orderless only at fixed arity, Flat+Orderless
not handled, no memoization. Its file translator handles two pattern
idioms only ("For single underscores, simply omit them; for double
underscores, …") and has no Optional, no `/;` (file-level), no
`SetAttributes` (grep-verified). Its **TODO** records the design the
author converged on but never shipped:

> `block([simp:false], matchdeclare([aa,bb,cc], all),
> tellsimp(myf(aa,[bb,cc]), internal([args]))); internal([args]) := …`
> "Actually, all functions should be defined this way so that they
> remain unevaluated if they don't match."

Transfer, not porting: (1) external validation of route A — an
independent author independently identified Maxima-native
`matchdeclare`/tellsimp-style rules as the right shape for mma-style
rules in Maxima; (2) the matcher capability list is a checklist of
what a naive CL matcher will still owe Rubi (Optional, identity-vs-
structural repeated names, orderless); (3) the negative lesson —
uncompiled brute-force rule scanning per evaluation is not a template
for "thousands of rules × 17,260 test integrals"; (4) no code transfer
(GPLv2; and the matcher misses Rubi's core feature anyway).

## 8. Q5 — go / no-go

- **Route A (Maxima rule system + generated runner): GO** for
  milestone 1 and as the standing route for the long-term port.
  Every matcher capability the grammar needs is measured present (§2);
  the build list is runner + conditions + `a_.` emulation (§4) + the
  ~fifty support predicates (T1 §2.3) — which is the T4/T5 work, not a
  matching-mechanism risk. Matching cost is 0.007 ms (§5).
- **Route B (Rubi-5 if-trees): NO for now.** 40/42 algebraic functions
  absent, the translator claim unverifiable, and the classifier still
  needs pattern matching (§6). Re-visit after class 1 is measured on
  route A.
- **mixima / mockmathica as host: NO.** Separate expression model,
  GPLv2, and its matcher lacks Optional; it validates the design and
  contributes nothing executable.
- **Mix (B for class 1, A for the rest): NO for milestone 1.** Porting
  Int111/Int121 plus a re-derived classifier buys no correctness edge
  over the rule list and adds a second maintenance surface.

Risk register for route A (to be driven down during T4/T5, each with a
measured probe already in hand): matcher decomposition/absorption
(§3.5 — the predicate-as-guard contract, yardstick: the T3 corpus
baseline); the T14 `kill`-reuse anomaly (avoided by naming convention);
5.50's matcher rewrite (re-run both probes on upgrade — they are
one-command).
