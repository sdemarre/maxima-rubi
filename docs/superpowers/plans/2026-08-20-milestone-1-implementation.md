# maxima-rubi Milestone 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the rule-based integration package for Maxima — loader, runner,
ported predicate/shim layer, a Python rule generator, and the two-layer test
harness — and port Rubi 4's class-1 (algebraic) rules so the class-1 Rubi
Maxima-syntax corpus section (25,697 integrals) is measured against the T3
`integrate` baseline (49.8 % verified) with no regressions.

**Architecture:** Each Rubi rule becomes a self-contained Maxima function
`_mr_rule_<file>_r<n>(f, x)` (match → condition → replacement, first
non-`false` wins, in Rubi `LoadRules` order); a flat global ordered table
`mr_rule_table` is assembled from one generated `.mac` file per Rubi `.m` file.
Matching uses Maxima's measured `matchdeclare`/`defmatch` system at Maxima
level (0.007 ms/match, T2 §5 — no Lisp in milestone 1). Recursion is plain
re-evaluation into the public API `rubi(f, x)` under a depth cap; no rule
fires is Maxima's own `integrate(f, x)` noun.

**Optional slots (`a_.`), measured 2026-08-20.** The matcher's algebraic
decomposition fills *value* defaults — a Plus slot `a_.+rest` matches `rest`
with `a→0`, a Times slot `b_.*x` matches `x` with `b→1` — so Plus/Times
optionals work with the plain all-slots-present pattern. But it does **not**
fill a *structural* default: `x` (= `x^1`, Power head dropped) does **not**
match a `u_^m` pattern, because the Power head is absent. So the generator
emits the plain pattern for Plus/Times optionals, and **duplicates the
pattern for each optional Power exponent** (`u_^m_.` → two matchers: `u^m`
and bare `u` with `m` bound to 1). This keeps the fan-out to the (usually
few) optional exponents, not 2^(all optionals); the load wall is measured in
Task 6 and the corpus (Task 9) is the yardstick — the divergence loop adds
duplication for any further structural case that surfaces.

**Tech Stack:** Maxima (a 5.49-series dev build — see Global Constraints),
Python 3 (generator + corpus driver; the census parser under
`probes/translation/` is reused), the pinned reference clones under
`reference/` (gitignored).

## Global Constraints

These apply to every task. They are the measured-trap house rules (T5 §4),
the build stamp, and facts re-verified on this build on 2026-08-20.

1. **Build stamp.** All measurements run on the installed
   `branch_5_49_base_796_g60186bb22_dirty` (2026-07-28), SBCL 2.6.7 —
   stamp with `build_info()` (`version` is unbound in this build). Do not
   pin to 5.49; on a 5.50 upgrade re-run the probes, do not carry numbers.
2. **Quote data symbols on both sides.** Assoc keys and branch tags are
   data; a bare symbol means whatever the caller last bound it to
   (dynamic scoping).
3. **Booleans through `is(…)`; `unknown` is not true.** Every generated
   guard and every ported predicate dispatches on `true`/`false`/else. Use
   the utils helper `%mr_b` (Task 2) for any value-position boolean.
4. **Value-position comparisons do not evaluate.** `2 > 1` stays a noun.
   Guards are `is(a > b)` or a ported predicate, never a bare comparison
   used as a value. `if`-conditions do evaluate comparisons.
5. **Guards are value-carrying `if … then A else B`.** A bare
   `if cond then A` inside a `block` does not terminate the block — the
   block returns its last expression.
6. **No `filter`; use `map` or explicit recursion.** `filter` returns its
   unevaluated noun in this build even with a named function.
7. **Fresh names per rule, never killed at runtime.** Capture variables
   bind globally as a side effect of matching; `defmatch` from a killed
   name misbehaves nondeterministically. The generator's
   `_mr_<file>_r<n>_<var>` names satisfy both. The runner never `kill`s
   anything it loaded.
8. **Internal names carry `%mr_` (or the `_mr_` rule-name family); shims
   never take the native name.** This binary documents names it does not
   bind (`atanh`, `elliptic_f`, `coefficient`, …); a Maxima-level definition
   under the native name would mask the real builtin when 5.50 lands.
9. **The package never prompts.** No `asksign` in generated code; sign
   questions go through `is`/`sign` and their `unknown`/`pnz` outcomes.
10. **Noun discipline.** Three distinct no-answer objects are never
    conflated: the package fall-through noun (list-structured
    `integrate(f, x)`, detected by `is(string(op(r)) = "integrate")` after
    an `atom` guard — the part/length and quoted-equality detectors are both
    unsound, T3 §3.3.3); a rule's recursion call (`mr_int(smaller, x)`);
    and corpus-expected nouns (`Unintegrable(…)`/`CannotIntegrate(…)`,
    Maxima call form, detected by name prefix).
11. **Batch-parser traps (measured 2026-08-20 on this build):**
    - `rules` is a **protected symbol** — never a variable or parameter
      name (an assignment to it is a hard error; a `:=` definition with it
      as a parameter fails to parse). Use `rl` / `mr_rule_table`.
    - A quoted symbol after a comma **nested inside another call's
      argument list** is a syntax error (`' is not an infix operator`),
      even with a space: `string(f(m, 'a))` does not parse, while
      `y : f(m, 'a)` does. Generated code therefore assigns captures to
      block locals first (`a : geteqR(mm, 'name)` as a standalone
      statement) and never nests such a call in another call's arguments.
      Harness/test code follows the same rule.
    - A line ending in `,` continues; `;`/`$` terminate; `+` on strings is
      symbolic sum — use `concat`/`sconcat`; one Lisp error aborts the
      whole `-b` batch (hence one subprocess per integral in Layer B).
    - `:lisp` in a batch reads one line — multi-line Lisp is a sibling
      `.lisp` + `load` (not used in milestone 1).
12. **`?fboundp` only sees Lisp-level functions**, not Maxima `:=`
    functions (measured 2026-08-20: `?fboundp` of a defined Maxima function
    → `false`). The diophantine witness idiom therefore does not transfer
    to `.mac` siblings. The loader uses a **function witness + call check**
    (Task 2): the sibling ends with `mr_witness_<file>() := true$` and the
    loader verifies `is(apply(witness, []) = true)`.
13. **Pins.** Rubi clone @ `61e9c18ea248061cd83c67882f7c91a73cef912d`;
    test-suite clone @ `60295e21c571ca210ecfbb695f4af99947454adf`.
    Generated files carry the Rubi pin in their header.
14. **License.** Rubi is MIT; the ported rule files are a substantial
    portion — every generated file header carries the Rubi copyright
    notice (T1 §6), and the package README carries it too (Task 10).
15. **Git.** Default branch `master`; no remote configured (no `push`);
    logical commits; stage only intended files; no `Co-Authored-By`
    trailers.
16. **Reference clones are read-only.** Never modify `reference/`.
17. **Yardstick.** The class-1 corpus is ground truth (no independent
    oracle exists — T3 §5). T3 baseline (this build, 2026-08-18):
    12,798 (49.8 %) verified/expected, 8,297 no-answer (incl. 31/31
    corpus non-integrable agreement), 3,102 unverified, 1,260 timeout,
    240 error, 0 unexpected. Milestone 1 must not regress the verified
    set and reports its measured uplift.

## File structure

```
maxima_rubi.mac            public loader: loads utils, then every generated
                           rule file in Rubi LoadRules order (witness-checked),
                           then assembles the global mr_rule_table
maxima_rubi_utils.mac      runner (%mr_dispatch, rubi, mr_int), the boolean
                           helper %mr_b, geteqR, the noun forms
                           (mr_unintegrable, mr_sum), the shims, and the
                           ported Rubi predicates (the %mr_ utility layer)
rules/class1/<key>.mac     generator-emitted, one per Rubi .m file loaded by
                           Rubi.m (67 files, 2,710 rules). Rules as data +
                           matchers; per-file witness; per-file rule count.
                           <key> is the Rubi file number with dots stripped
                           (1_1_1_1, 1_1_2_x, …) — the generator emits it.
generator/generate_class1.py   Python generator (reuses the census parser);
                           emits rules/class1/*.mac
generator/translation_table.py   the closed token→Maxima-name table (T4 §2);
                           the generator fails loudly on an unknown token
test_maxima_rubi.mac       Layer A unit suite (diophantine Results protocol)
test/mr_preload.mac        Layer B preload: batch_answers_from_file + load
                           the package
test/corpus_class1_driver.py   Layer B driver (generalized from
                           probes/corpus/probe-integrate-sample.py):
                           one subprocess per integral, CLASS verdicts,
                           streaming + resume, Results line
```

Layout rationale (T5 §2, T4 §3): flat at the repo root (diophantine's
shape, not `share/`); 1:1 file correspondence between generated rule files,
Rubi `.m` files, and corpus `.mac` files so per-file selection, per-file
test runs, and per-file divergence reports share one key; rules are
regenerable (Rubi bump = re-run the generator over the diff), committed so
`git diff` shows which rules moved.

## The translation table (the generator's seam)

Complete for class 1 by the T4 census (122 distinct tokens; zero unlisted).
The generator maps every CamelCase token through this table and **fails
loudly on a token not in it** — that is how the table stays provably
complete as classes are added. State per T4 §2: `present` (direct Maxima),
`shim` (this binary lacks the name — `%mr_`-prefixed, never the native
name), `port` (Rubi utility, ported once into utils), `noun` (package noun
form). The right column is what the generator emits.

Conditions (Rubi token → emitted):

| Rubi token | emitted | state |
|---|---|---|
| FreeQ[e, x] / FreeQ[{a,b}, x] | `freeof(x, e)` / `freeof(x, a) and freeof(x, b)` | present |
| IntegerQ / OddQ | `integerp` / `oddp` | present |
| Not | `not` | present |
| GtQ/LtQ/LeQ/GeQ | `is(a > b)` / `is(a < b)` / `is(a <= b)` / `is(a >= b)` | present (guard form) |
| IGtQ/ILtQ/ILeQ | same, args integer-guarded by context | present (guard form) |
| PosQ / NegQ | `%mr_posQ(a)` / `%mr_negQ(a)` (via `sign`, maps `pos`/`neg`/`pnz`) | shim |
| RationalQ / IntegersQ / FractionQ | `%mr_rationalQ(r)` / list form / `%mr_fractionQ(r)` | shim |
| EqQ / NeQ | `%mr_eqQ(u, v)` / `%mr_neQ(u, v)` (via `%mr_possible_zeroQ`) | port |
| Coeff / Coefficient | `%mr_coeff(u, x, n)` | shim + port |
| Sqrt / Log / D | `sqrt` / `log` / `diff` | present |
| ReplaceAll | `subst` | present (pattern-shift use) |
| If | `if … then … else` (value-carrying) | present |
| PolyQ/LinearQ/QuadraticQ/TrinomialQ/BinomialQ/IntLinearQ/IntBinomialQ/IntQuadraticQ | `%mr_polyQ(u, x)` … (family, see Task 7) | port |
| *MatchQ / SumQ / SumSimplerQ / SimplerQ / SimplerSqrtQ / NiceSqrtQ / RationalFunctionQ / MatchQ / NonfreeFactors / SplitProduct / FractionalPowerFactorQ / LeafCount / MonomialQ / PerfectSquareQ / AtomQ / Generalized* / LinearPairQ / PseudoBinomialPairQ / InverseFunctionQ / AlgebraicFunctionQ | `%mr_<token>(…)` | port |
| PossibleZeroQ | `%mr_possible_zeroQ(e)` | port (see the clone-gap note below) |

Replacements (Rubi token → emitted):

| Rubi token | emitted | state |
|---|---|---|
| Int[smaller, x] / IntHide | `mr_int(smaller, x)` | package core |
| Unintegrable / CannotIntegrate | `mr_unintegrable(f, x)` | package noun |
| Sum | `mr_sum(…)` (formal placeholder — Maxima `sum` evaluates) | package noun |
| Sqrt / ArcTan / ArcSin / ArcCos | `sqrt` / `atan` / `asin` / `acos` | present |
| ArcTanh / ArcSinh / ArcCosh | `%mr_atanh(z)` / `%mr_asinh(z)` / `%mr_acosh(z)` (log forms) | shim |
| EllipticF / EllipticE / EllipticPi | `elliptic_f(…)` / `elliptic_e(…)` / `elliptic_pi(…)` — **emit as package nouns** `mr_elliptic_f(…)` etc.; this build does not bind them, so differentiating an elliptic answer is at risk (T4 §2/§6) — the corpus verdict for those entries is the measurement | noun + verify |
| Hypergeometric2F1[a,b,c,z] | `hypergeometric([a, b], [c], z)` (list form; scalar args warn) | present (shape) |
| AppellF1 | `mr_appellf1(…)` (no Maxima equivalent) | package noun |
| With[{a = e}, b] / Module[{a = e}, b] | `block([a], a : e, b)` idiom | present |
| Subst / SubstFor / SubstPower | `%mr_subst(…)` / `%mr_substFor(…)` / `%mr_substPower(…)` | port |
| Simp / Simplify / SimplifyIntegrand | `%mr_simp(e)` — the zero-chain policy `ratsimp → ratsimp∘expand → factor → ratsimp∘factor` (`simplify` unbound here) | shim (policy) |
| Rt[u, n] | `%mr_rt(u, n)` (even n → sqrt-family; odd n → signed real root) | shim |
| ExpandToSum / ExpandIntegrand / ExpandLinearProduct | `%mr_expandToSum(…)` etc. (over `expand`) | port |
| FracPart / IntPart | `%mr_fracPart(u)` / `%mr_intPart(u)` (Laurent-part operators) | port |
| PolynomialQuotient / PolynomialRemainder / PolynomialDivide / Quotient | `%mr_polyQuotient(…)` etc. (3 small functions over `%mr_coeff`; `pquoto`/`pmodulo`/`quo` are nouns here) | shim |
| Denominator / Numerator / Denom / Numer | `denom` / `num` | present |
| GCD / PolyGCD | `gcd` / `%mr_polyGCD(…)` | present + port |
| Together | `%mr_together(e)` (`num(e)/den(e)` after `rat`; `together` unbound) | shim |
| Mod / Floor / Factor / Binomial / Cos | `mod` / `floor` / `factor` / `binomial` / `cos` | present |
| Sign | `%mr_sign(e)` (maps `pos`/`neg`/`zero` → 1/-1/0) | shim |
| RemoveContent[u, x] | `%mr_removeContent(u, x)` | port |
| Root | `%mr_root(…)` (`rootof` noun here; different construct anyway) | port |
| Cancel | `%mr_cancel(e)` (noun here) | shim |
| Hold | `%mr_hold(e)` (custom hold; `holdform` noun) | shim |
| Boole | `if … then 1 else 0` | shim |
| RationalFunctionExpand / NormalizePseudoBinomial | `%mr_rationalFunctionExpand(…)` etc. | port |
| IntSum / Integrate / ShowStep / Dist | `%mr_intSum(…)` / — / — / `%mr_dist(…)` | port |

**Clone-gap note (measured 2026-08-20):** `PossibleZeroQ` is referenced by
`EqQ`/`NeQ` (`IntegrationUtilityFunctions.m:365,370`) but is **not defined
anywhere in the pinned clone** (2 occurrences repo-wide, both the
references). The port therefore derives its contract from usage:
`EqQ[u, v]` is true iff `u - v` is *possibly* zero, i.e. not provably
nonzero — in Maxima: `%mr_possible_zeroQ(e) := not is(e # 0)` (three-valued
`is`: provably nonzero → false; zero or undecidable → true).
`%mr_eqQ(u, v) := %mr_possible_zeroQ(u - v)`,
`%mr_neQ(u, v) := not %mr_possible_zeroQ(u - v)`. This is the faithful
loose-equality reading (Rubi prefers to fire a rule when the condition
*could* hold; the harness's derivative check catches over-firing). Flagged
in the Task 5 unit probes and in the Task 10 handoff as the one predicate
whose source had to be derived, not ported.

---

### Task 1: Layer-A harness skeleton

**Files:**
- Create: `test_maxima_rubi.mac`

**Interfaces:**
- Produces: `check(name, actual, expected)`, `check_bool(name, actual)`,
  `check_not(name, actual)`, `tests_passed`, `tests_failed`, and the
  `Results: <n> passed, <m> failed` line as the last output before `quit()`.
  Every later task's "Run: Layer A" step means
  `maxima --very-quiet -b test_maxima_rubi.mac` and reading that line
  (a run that dies mid-way prints no Results line — that is itself a
  failure, AGENTS.md).

- [ ] **Step 1: Write the harness skeleton**

```
/* test_maxima_rubi.mac — Layer A unit suite (diophantine protocol).
 * Gate: maxima --very-quiet -b test_maxima_rubi.mac
 * Ends with "Results: <n> passed, <m> failed"; a mid-run death prints no
 * Results line, which is itself a failure. */
display2d : false$

tests_passed : 0$
tests_failed : 0$

/* actual = expected (equations evaluate in if-conditions, T16). */
check(test_name, actual, expected) := block([],
  if actual = expected then (
    tests_passed : tests_passed + 1,
    print("  PASS: ", test_name)
  ) else (
    tests_failed : tests_failed + 1,
    print("  FAIL: ", test_name),
    print("    expected: ", expected),
    print("    actual:   ", actual)
  ),
  true
)$

/* Three-valued boolean assertion (diophantine item 19): is() gives
   true/false/unknown in this build; unknown is a broken assertion,
   counted as a failure so it cannot hide. */
check_bool(test_name, actual) := block([v],
  v : is(actual),
  if v = true then (
    tests_passed : tests_passed + 1,
    print("  PASS: ", test_name)
  ) elseif v = false then (
    tests_failed : tests_failed + 1,
    print("  FAIL: ", test_name)
  ) else (
    tests_failed : tests_failed + 1,
    print("  FAIL (non-boolean): ", test_name),
    print("    actual:   ", actual)
  ),
  true
)$

check_not(test_name, actual) := block([v],
  v : is(actual),
  if v = false then (
    tests_passed : tests_passed + 1,
    print("  PASS: ", test_name)
  ) elseif v = true then (
    tests_failed : tests_failed + 1,
    print("  FAIL: ", test_name)
  ) else (
    tests_failed : tests_failed + 1,
    print("  FAIL (non-boolean): ", test_name),
    print("    actual:   ", actual)
  ),
  true
)$

test_smoke() := block([],
  print("--- smoke ---"),
  check("smoke equality", 1 + 1, 2),
  check_bool("smoke true", true),
  check_not("smoke false", false),
  true
)$

run_all_tests() := block([],
  test_smoke(),
  print(""),
  print("========================================"),
  print("Results: ", tests_passed, " passed, ", tests_failed, " failed"),
  print("========================================"),
  tests_failed = 0
)$

run_all_tests();
quit();
```

- [ ] **Step 2: Run it**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: `Results: 3 passed, 0 failed` and a clean exit.

- [ ] **Step 3: Commit**

```sh
git add test_maxima_rubi.mac
git commit -m "test: Layer-A harness skeleton (diophantine Results protocol)"
```

---

### Task 2: Loader + utils skeleton + API fall-through

**Files:**
- Create: `maxima_rubi.mac`
- Create: `maxima_rubi_utils.mac`
- Modify: `test_maxima_rubi.mac` (load the package; add tests)

**Interfaces:**
- Consumes: Task 1's `check`/`check_bool`.
- Produces (exact names, used by every later task):
  - `rubi_verbose` — global flag, default `false`;
  - `rubi(f, x)` — public API: antiderivative, else `integrate(f, x)`;
  - `mr_int(f, x)` — the recursion entry (what generated replacements call);
  - `mr_unintegrable(f, x)`, `mr_sum(fun, var, lo, hi)` — package noun forms;
  - `geteqR(mm, nm)` — capture lookup on an equation list;
  - `%mr_b(e)` — boolean resolver (`unknown` → `false`);
  - `%mr_dispatch(f, x, rl, depth)` — ordered first-match-wins dispatch over
    a rule-function list `rl`; returns the replacement or `false`;
  - `%mr_max_depth` — recursion cap (starts at 16, the T5 candidate;
    re-tuned in Task 9 against corpus-observed recursion);
  - `mr_rule_table` — the global ordered rule list (empty in this task);
  - `%mr_load_sibling(fname, witness)` — the loader's witness-checked load.

- [ ] **Step 1: Write `maxima_rubi_utils.mac` (skeleton)**

```
/* maxima_rubi_utils.mac — runner + noun forms + (later) shims and ported
 * predicates. Loaded by maxima_rubi.mac. House rules: AGENTS.md + T5 §4;
 * the measured traps of T2 §3 are the reason for %mr_b, the block-local
 * rebind in the rule shape, and the never-kill naming policy. */

rubi_verbose : false$

/* Capture lookup on the [var = value] equation list (order unspecified,
 * measured T2 §3.6). Quoted symbol on both sides (house rule 1). */
geteqR(mm, nm) := block([],
  if length(mm) = 0 then false
    else if is(part(part(mm, 1), 1) = nm) then part(part(mm, 1), 2)
         else geteqR(rest(mm), nm))$

/* Boolean resolver (house rule 2): is()'s third value unknown is not true. */
%mr_b(e) := block([v],
  v : is(e),
  if v = true then true else false)$

/* Package noun forms (house rule 10 — distinct from the fall-through
 * integrate noun and from corpus-expected nouns). */
mr_unintegrable(f, x) := 'unintegrable[f, x]$
mr_sum(fun, var, lo, hi) := 'mr_sum[fun, var, lo, hi]$

/* Recursion cap (T5 §1 candidate; re-tuned in Task 9). A runaway
 * replacement becomes the fall-through noun, not a stack overflow. */
%mr_max_depth : 16$

/* Ordered first-match-wins whole-expression dispatch (T2 §4.2). rl is a
 * list of rule functions r(f, x) -> replacement | false. The parameter is
 * named rl, never rules (protected symbol, measured 2026-08-20). */
/* MEASURED Maxima gotcha (2026-08-20): a `return(value)` inside a `for` loop
   does NOT return from the enclosing block in this build — it is loop-level,
   so the block fell through to the trailing `false` and dispatch ALWAYS
   returned false (rubi() was a silent pass-through to integrate). The fix:
   track the firing result in `ans`, use a BARE `return()` to break the `for`
   loop, and return `ans` after the loop. Probed: the broken form returns
   false for [false, 42]; this form returns 42. */
%mr_dispatch(f, x, rl, depth) := block([i, r, res, ans],
  ans : false,
  for i : 1 thru length(rl) do (
    r : part(rl, i),
    res : apply(r, [f, x]),
    if res # false then (
      if rubi_verbose then
        print("rubi: rule ", string(r), " fired on ", string(f)),
      ans : res,
      return()
    )
  ),
  ans)$

/* The recursion counter increments on the way in and decrements on the way
 * out, so nested mr_int calls share one depth budget. A runaway replacement
 * becomes the fall-through noun, not a stack overflow. */
depth_level : 0$

mr_int(f, x) := block([ans],
  depth_level : depth_level + 1,
  if depth_level > %mr_max_depth then (
    depth_level : depth_level - 1,
    return(integrate(f, x))
  ),
  ans : %mr_dispatch(f, x, mr_rule_table, depth_level),
  depth_level : depth_level - 1,
  if ans = false then integrate(f, x) else ans)$

rubi(f, x) := mr_int(f, x)$
```

- [ ] **Step 2: Write `maxima_rubi.mac` (loader)**

```
/* maxima_rubi.mac — public loader (diophantine mould, T5 §2).
 *
 * Four load paths must work: by full path (load_pathname set), from the
 * directory, via file_search push, batched (load_pathname false). The
 * witness check is the point: a missed or truncated sibling load must fail
 * loudly here, not silently later.
 *
 * Witness idiom for .mac siblings (measured 2026-08-20): ?fboundp only
 * sees Lisp functions, so the witness is a Maxima FUNCTION defined at the
 * end of the sibling; an undefined function call stays a noun, so
 * is(apply(witness, []) = true) is true iff the sibling fully loaded. */
%mr_load_sibling(fname, witness) := block([dir, ok, w],
  dir : if load_pathname = false then "" else pathname_directory(load_pathname),
  /* errcatch in THIS build returns [RESULT] on success and [] on error
     (measured — probes/maxima/probe-errcatch-semantics.out). So the by-name
     fallback fires when the sibling-dir load FAILED (ok = []). When dir is ""
     (batched) the first load already IS load(fname); the fallback is then a
     harmless retry. */
  ok : errcatch(load(sconcat(dir, fname))),
  if ok = [] then ok : errcatch(load(fname)),
  w : apply(witness, []),
  if is(w = true) = false then
    error("maxima_rubi: could not load the sibling file ", fname,
          " (witness ", string(witness), " did not return true; the load ",
          "missed or truncated). Make it findable: (1) load this library ",
          "by full path, (2) run from its directory, (3) push its dir onto ",
          "file_search_maxima, or (4) install under ~/.maxima/."))$

%mr_load_sibling("maxima_rubi_utils.mac", 'mr_witness_utils)$

/* Generated rule files, Rubi LoadRules order (the generator emits this
 * list; one line per file). Empty until Task 4/6. */
mr_rule_table : []$

mr_witness_maxima_rubi() := true$
```

The witness is a **function** (a quoted LHS cannot be assigned, measured
2026-08-20; and `?fboundp` does not see Maxima functions, so the check is a
call, not an fboundp). Add the matching witness at the very end of
`maxima_rubi_utils.mac`:

```
mr_witness_utils() := true$
```

- [ ] **Step 3: Add Layer-A tests**

Append to `test_maxima_rubi.mac` before `run_all_tests()`:

```
load("maxima_rubi.mac")$

test_load_and_api() := block([r, saved_table],
  print("--- load + API fall-through ---"),
  check_bool("loader witness survived", is(mr_witness_maxima_rubi() = true)),
  /* no rules loaded yet: every call falls through to Maxima's integrate */
  check("fall-through x^2", rubi(x^2, x), integrate(x^2, x)),
  check("fall-through 5", rubi(5, x), integrate(5, x)),
  /* the fall-through noun is Maxima's own, list-structured */
  r : rubi(sin(x)^x, x),
  check_bool("fall-through noun detect",
             is(atom(r) = false) and is(string(op(r)) = "integrate")),
  /* noun forms are distinct from the fall-through noun */
  check_bool("mr_unintegrable is a noun", is(mr_unintegrable(f, x) = 'unintegrable[f, x])),
  /* empty table -> fall-through. Save/restore the table so a later test
     (Task 3+) is not run against a wiped table (measured landmine 2026-08-20). */
  saved_table : mr_rule_table,
  mr_rule_table : [],
  check_bool("empty table -> noun", is(string(op(rubi(1/x, x))) = "integrate")
             or is(rubi(1/x, x) = log(x))),
  mr_rule_table : saved_table,
  true
)$
```

Add `test_load_and_api(),` to the `run_all_tests` call list (after
`test_smoke(),`).

- [ ] **Step 4: Run Layer A**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: `Results: 9 passed, 0 failed` (3 smoke + 6 new) — or adjust the
count to the actual number of asserts; the gate is `0 failed` plus a clean
Results line.

- [ ] **Step 5: Commit**

```sh
git add maxima_rubi.mac maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "feat: loader (function-witness idiom) + utils skeleton + API fall-through"
```

---

### Task 3: Runner core proven with hand-written rules

**Files:**
- Modify: `test_maxima_rubi.mac` (add the hand-written rule block + tests)

**Interfaces:**
- Consumes: Task 2's `geteqR`, `%mr_b`, `%mr_dispatch`, `mr_int`,
  `mr_rule_table`.
- Produces: the **generated rule shape**, proven by hand — one Rubi rule
  becomes `matchdeclare(…)`, `defmatch(_mr_pat_<file>_r<n>, pattern, x)`,
  `_mr_cond_<file>_r<n>(mm, x)`, `_mr_repl_<file>_r<n>(mm, x)`,
  `_mr_rule_<file>_r<n>(f, x)`, appended into the file's rule list. The
  generator (Task 4) emits exactly this shape.

The rule shape (the contract the generator emits — note the block-local
capture rebind, the value-carrying guards, and no quoted symbol nested in a
call's argument list):

```
matchdeclare(_mr_1_1_1_1_r1_a, true)$
matchdeclare(_mr_1_1_1_1_r1_m, true)$
defmatch(_mr_pat_1_1_1_1_r1, _mr_1_1_1_1_r1_a^_mr_1_1_1_1_r1_m, x)$
_mr_cond_1_1_1_1_r1(mm, x) := block([a, m],
  a : geteqR(mm, '_mr_1_1_1_1_r1_a),
  m : geteqR(mm, '_mr_1_1_1_1_r1_m),
  freeof(x, a) and freeof(x, m))$
_mr_repl_1_1_1_1_r1(mm, x) := block([a, m],
  a : geteqR(mm, '_mr_1_1_1_1_r1_a),
  m : geteqR(mm, '_mr_1_1_1_1_r1_m),
  a^(m + 1)/(m + 1))$
_mr_rule_1_1_1_1_r1(f, x) := block([mm, ok],
  mm : _mr_pat_1_1_1_1_r1(f, x),
  if mm = false then return(false),
  ok : _mr_cond_1_1_1_1_r1(mm, x),
  if is(ok) = true then _mr_repl_1_1_1_1_r1(mm, x) else false)$
```

- [ ] **Step 1: Add two hand-written rules to `test_maxima_rubi.mac`**

Add after `load("maxima_rubi.mac")$`:

Rule A — the power rule. The pattern `a*x^m` was measured to match `x^3` →
a=1, m=3 and `5*x^2` → a=5, m=2 via the matcher's decomposition; the bare
`x` (= `x^1`, Power head dropped) does **not** match — the Power-optional
structural case the generator's Power D-duplication handles (Architecture
note above). Cond is `freeof` only; the full Rubi guards land with the
Task 5 predicate port.

```
/* hand-written runner proof (Task 3); replaced by generated 1.1.1.1 (Task 4) */
matchdeclare(_mr_t3_a, true)$
matchdeclare(_mr_t3_m, true)$
defmatch(_mr_pat_t3_power, _mr_t3_a*x^_mr_t3_m, x)$
_mr_cond_t3_power(mm, x) := block([a, m],
  a : geteqR(mm, '_mr_t3_a),
  m : geteqR(mm, '_mr_t3_m),
  freeof(x, a) and freeof(x, m))$
_mr_repl_t3_power(mm, x) := block([a, m],
  a : geteqR(mm, '_mr_t3_a'),
  m : geteqR(mm, '_mr_t3_m'),
  a*x^(m + 1)/(m + 1))$
_mr_rule_t3_power(f, x) := block([mm, ok],
  mm : _mr_pat_t3_power(f, x),
  if mm = false then return(false),
  ok : _mr_cond_t3_power(mm, x),
  if is(ok) = true then _mr_repl_t3_power(mm, x) else false)$
```

Rule B — recursion, using a real Rubi rule (1.1.1.2, line 5) whose
replacement re-dispatches `mr_int` onto a *different* integrand:
`1/((a+bx)(c+dx))` → `1/(ac + bd x^2)` when `bc + ad = 0`. The proof drops
the `EqQ[b*c + a*d, 0]` guard (the Task 5 predicate port) and uses a
`freeof`-only cond; the test input satisfies the dropped guard. The pattern
was measured to match `1/((1+2x)(3-6x))` → a=1, b=2, c=3, d=-6 (target
`1/(3-12x^2)`). Also defined: a self-recursive rule for the depth-cap test
(it has no matcher, so it "fires" on anything and re-dispatches on the same
integrand).

```
matchdeclare(_mr_t3_r_a, true)$
matchdeclare(_mr_t3_r_b, true)$
matchdeclare(_mr_t3_r_c, true)$
matchdeclare(_mr_t3_r_d, true)$
defmatch(_mr_pat_t3_rec, 1/((_mr_t3_r_a + _mr_t3_r_b*x)*(_mr_t3_r_c + _mr_t3_r_d*x)), x)$
_mr_cond_t3_rec(mm, x) := block([a, b, c, d],
  a : geteqR(mm, '_mr_t3_r_a'),
  b : geteqR(mm, '_mr_t3_r_b'),
  c : geteqR(mm, '_mr_t3_r_c'),
  d : geteqR(mm, '_mr_t3_r_d'),
  freeof(x, a) and freeof(x, b) and freeof(x, c) and freeof(x, d))$
_mr_repl_t3_rec(mm, x) := block([a, b, c, d],
  a : geteqR(mm, '_mr_t3_r_a'),
  b : geteqR(mm, '_mr_t3_r_b'),
  c : geteqR(mm, '_mr_t3_r_c'),
  d : geteqR(mm, '_mr_t3_r_d'),
  mr_int(1/(a*c + b*d*x^2), x))$
_mr_rule_t3_rec(f, x) := block([mm, ok],
  mm : _mr_pat_t3_rec(f, x),
  if mm = false then return(false),
  ok : _mr_cond_t3_rec(mm, x),
  if is(ok) = true then _mr_repl_t3_rec(mm, x) else false)$

/* depth-cap test only: no matcher, always re-dispatches on the same f. */
_mr_rule_t3_selfrec(f, x) := block([], mr_int(f, x))$

/* rec first (more specific), then the general power rule. */
mr_rule_table : [ _mr_rule_t3_rec, _mr_rule_t3_power ]$
```

- [ ] **Step 2: Add the tests**

```
test_runner() := block([r, sd, st],
  print("--- runner (hand-written rules) ---"),
  /* Rule A: power, via decomposition (a=1 for x^3, a=5 for 5x^2) */
  check("power x^3", rubi(x^3, x), x^4/4),
  check("power 5x^2", rubi(5*x^2, x), 5*x^3/3),
  /* direct firing assertions (not just answer-correctness — Maxima's own
     integrate gives the same x^4/4, so the rubi() checks above can't tell a
     firing rule from a fall-through). Prove the power rule actually fires and
     produces its replacement, and rejects a non-match. This exercises the
     %mr_dispatch `if res # false` (rule-fired) path. */
  check_bool("power rule fires on x^3", is(_mr_rule_t3_power(x^3, x) # false)),
  check("power rule returns x^4/4", _mr_rule_t3_power(x^3, x), x^4/4),
  check_bool("power rule rejects x+1", is(_mr_rule_t3_power(x + 1, x) = false)),
  /* bare x (= x^1) does NOT match a*x^m (Power head dropped) -> fall-through
     to Maxima's own answer; documents the Power-optional structural case */
  check("power x (fall-through)", rubi(x, x), x^2/2),
   /* Rule B, end-to-end: rubi() on the product form yields the reduced-form
      integral. NOTE this check alone is VACUOUS — integrate of the original
      1/((1+2x)(3-6x)) and of the reduced 1/(3-12x^2) are equal on this build
      (both log(2x+1)/12 - log(2x-1)/12, measured 2026-08-20), so it can't tell
      a firing rule from a fall-through. The firing assertions below fix that. */
   r : rubi(1/((1 + 2*x)*(3 - 6*x)), x),
   check_bool("recursion re-dispatches (end-to-end)",
              is(r = integrate(1/(3 - 12*x^2), x))),
   /* direct firing assertions on the rec rule (non-vacuous): prove it actually
      fires on the product form (match + cond + repl) and rejects a non-match. */
   check_bool("rec rule fires on 1/((1+2x)(3-6x))",
              is(_mr_rule_t3_rec(1/((1 + 2*x)*(3 - 6*x)), x) # false)),
   check_bool("rec rule rejects x^2", is(_mr_rule_t3_rec(x^2, x) = false)),
  /* no rule fires -> Maxima's own answer (fall-through, not a package noun) */
  check_bool("no-match -> fall-through",
             is(rubi(x + sin(x), x) = x^2/2 - cos(x))
             or is(string(op(rubi(x + sin(x), x))) = "integrate")),
   /* depth cap: a runaway self-recursive rule must hit the cap and return
      Maxima's own integrate(f,x) result — not stack-overflow or hang.
      exp(x^2) is used because on this build integrate solves it to an erf
      closed form (NOT a noun — measured 2026-08-20); the assertion accepts
      either the integrate result or a noun (other builds). */
   sd : %mr_max_depth, st : mr_rule_table,
   %mr_max_depth : 8,
   mr_rule_table : [ _mr_rule_t3_selfrec ],
   r : rubi(exp(x^2), x),
   check_bool("runaway recursion -> cap result, not overflow",
              is(r = integrate(exp(x^2), x)) or is(string(op(r)) = "integrate")),
   %mr_max_depth : sd,
   mr_rule_table : st,
  /* verbose flag prints the rule identity on fire (T5 §1) */
  rubi_verbose : true,
  rubi(x^3, x),
  rubi_verbose : false,
  true
)$
```

Add `test_runner(),` to `run_all_tests` (after `test_load_and_api(),`).

- [ ] **Step 3: Run Layer A**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: `0 failed`, Results line present. If the recursive rule's
matcher misbinds (the decomposition risk, T2 §3.5), do not paper over it —
that is the signal the lambda guard or the rule shape is wrong; fix the
rule, re-run.

- [ ] **Step 4: Commit**

```sh
git add test_maxima_rubi.mac
git commit -m "test: runner contract proven with hand-written rules (match/cond/rebind/recursion)"
```

---

### Task 4: The Python generator + first generated file (1.1.1.1)

**Files:**
- Create: `generator/generate_class1.py`
- Create: `generator/translation_table.py`
- Create (generated): `rules/class1/1_1_1_1.mac`
- Modify: `maxima_rubi.mac` (load 1_1_1_1, extend `mr_rule_table`)
- Modify: `test_maxima_rubi.mac` (drop the Task-3 hand-written rules; test
  the generated file)

**Interfaces:**
- Consumes: the census parser — `probes/probe-rubi-anatomy/01-inventory.py`
  (`strip_comments`, `parse_load_rules`) and
  `probes/translation/01-class1-syntax-census.py` (`rule_runs`,
  `split_rule`), imported by path exactly as the census does.
- Produces: `rules/class1/<key>.mac` files of the Task-3 shape; the file
  key is the Rubi file number, dots stripped (`1.1.1.1` → `1_1_1_1`;
  `1.1.2.x` → `1_1_2_x`); each file ends with
  `mr_witness_<key>() := true$` and defines `mr_rules_<key>` (its ordered
  rule-function list) and `mr_rules_count_<key>` (its rule count, for the
  T4 §4 census cross-check).

Generator algorithm (per T4 §4, steps 1–5):

1. Parse each loaded `.m` into rule runs (`Int[...], x_Symbol] := rhs /;
   cond`), same convention as the census (reproduces 2,710).
2. Per rule, number it r1…rn in file order. Two name rules, both measured:
   - **A capture named like the integration variable is the integration
     variable.** Rubi's integration variable is always `x_Symbol`; a capture
     written `x_` (same name) is the *same named pattern* in Mathematica,
     which must agree — so it is the pattern argument, not a free capture.
     Translate it to `x` (the pattern argument) and emit no `matchdeclare`
     for it. (Rule 1 of 1.1.1.1, `Int[1/x_, x_Symbol] := Log[x]`, is
     exactly this: the pattern is `1/x`, no captures.)
   - **Every other capture `v`** is renamed to `_mr_<key>_r<n>_v` and
     `matchdeclare`d (`freeof(x)` if the rule's cond has `FreeQ[{…v…}, x]`,
     else `true`).
   **Drop the `.` from optionals** (plain all-slots-present pattern — the
   matcher's decomposition fills the Plus/Times identity defaults, measured
   2026-08-20). The emitter emits the PLAIN pattern only. For an optional
   Power exponent `u_^m_.`, the Power head is dropped when the exponent is 1,
   which decomposition cannot fill; the bare-exponent-1 case therefore falls
   through to `integrate` (correct answer, not via the rule) — a coverage gap,
   not a correctness bug. The Power-optional D-duplication (`power_dups`: a
   second matcher with the exponent removed and `m` bound to 1) is DEFERRED to
   Task 9's divergence loop, which adds it where the corpus shows the gap
   (Architecture note). Translate the head `Int[expr, x_Symbol]` to the `(f, x)`
   call shape.
3. Conditions: split on top-level `&&`; each atom through the translation
   table (`FreeQ[{a,b}, x]` → `freeof(x, a) and freeof(x, b)`;
   `EqQ`/`NeQ` → `%mr_eqQ`/`%mr_neQ`; comparisons → `is(…)`); emit as the
   value of `_mr_cond_<key>_r<n>(mm, x)` with the block-local rebind
   preamble.
4. Replacements: token translation per the table; `Int[smaller, x]` →
   `mr_int(smaller, x)`; `With`/`Module` → the `block` idiom;
   `Simp`/`Simplify` → `%mr_simp`; `Sum` → `mr_sum`; emit as the value of
   `_mr_repl_<key>_r<n>(mm, x)` with the same preamble.
5. Emit the rule function, append to `mr_rules_<key>`, write the file with
   the pin header + MIT notice, `mr_witness_<key>() := true$` last, and
   `mr_rules_count_<key> : <n>$` (unquoted LHS — a value, checked by the
   loader against the census).

The generator **fails loudly** (nonzero exit, message naming the file,
rule, and token) on: a token not in the translation table; a pattern
variable it cannot rename; an unparseable rule run. It prints, per file,
the rule count; the total across the 67 files must be 2,710 (Task 6).

- [ ] **Step 1: Write `generator/translation_table.py`**

The closed table from the Global Constraints section, as two dicts plus
the argument-shape rules the emitter needs:

```python
# translation_table.py — the closed token->Maxima seam (T4 §2 census).
# A token absent from both dicts is a generator error by design.

# Direct renames / shims / ports: token -> emitted name (1:1 arity).
RENAME = {
    # present
    "FreeQ": "freeof",            # arg order flips: FreeQ[e, x] -> freeof(x, e)
    "IntegerQ": "integerp", "OddQ": "oddp", "Not": "not",
    "Sqrt": "sqrt", "Log": "log", "D": "diff", "ReplaceAll": "subst",
    "ArcTan": "atan", "ArcSin": "asin", "ArcCos": "acos",
    "Denominator": "denom", "Numerator": "num", "Denom": "denom", "Numer": "num",
    "GCD": "gcd", "Mod": "mod", "Floor": "floor", "Factor": "factor",
    "Binomial": "binomial", "Cos": "cos", "Sin": "sin", "Expand": "expand",
    # shims (this binary lacks the name; %mr_ prefix, house rule 8)
    "Rt": "%mr_rt", "Sign": "%mr_sign", "Cancel": "%mr_cancel",
    "Together": "%mr_together",
    "ArcTanh": "%mr_atanh", "ArcSinh": "%mr_asinh", "ArcCosh": "%mr_acosh",
    # ports (Rubi utilities, Task 4/5/7)
    "EqQ": "%mr_eqQ", "NeQ": "%mr_neQ", "PossibleZeroQ": "%mr_possible_zeroQ",
    "Coeff": "%mr_coeff", "Coefficient": "%mr_coeff",
    "PolyQ": "%mr_polyQ", "LinearQ": "%mr_linearQ", "QuadraticQ": "%mr_quadraticQ",
    "TrinomialQ": "%mr_trinomialQ", "BinomialQ": "%mr_binomialQ",
    "IntLinearQ": "%mr_intLinearQ", "IntBinomialQ": "%mr_intBinomialQ",
    "IntQuadraticQ": "%mr_intQuadraticQ",
    "Subst": "%mr_subst", "SubstFor": "%mr_substFor", "SubstPower": "%mr_substPower",
    "Simp": "%mr_simp", "Simplify": "%mr_simp", "SimplifyIntegrand": "%mr_simp",
    "ExpandToSum": "%mr_expandToSum", "ExpandIntegrand": "%mr_expandIntegrand",
    "ExpandLinearProduct": "%mr_expandLinearProduct",
    "FracPart": "%mr_fracPart", "IntPart": "%mr_intPart",
    "PolynomialQuotient": "%mr_polyQuotient",
    "PolynomialRemainder": "%mr_polyRemainder",
    "PolynomialDivide": "%mr_polyDivide", "Quotient": "%mr_polyQuotient",
    "PolyGCD": "%mr_polyGCD", "RationalFunctionExpand": "%mr_rationalFunctionExpand",
    "NormalizePseudoBinomial": "%mr_normalizePseudoBinomial",
    "Dist": "%mr_dist", "IntSum": "%mr_intSum", "RemoveContent": "%mr_removeContent",
    "RationalQ": "%mr_rationalQ", "IntegersQ": "%mr_integersQ", "FractionQ": "%mr_fractionQ",
    "PosQ": "%mr_posQ", "NegQ": "%mr_negQ",
    "LinearMatchQ": "%mr_linearMatchQ", "BinomialMatchQ": "%mr_binomialMatchQ",
    "QuadraticMatchQ": "%mr_quadraticMatchQ", "TrinomialMatchQ": "%mr_trinomialMatchQ",
    "GeneralizedBinomialQ": "%mr_generalizedBinomialQ",
    "GeneralizedTrinomialQ": "%mr_generalizedTrinomialQ",
    "GeneralizedBinomialMatchQ": "%mr_generalizedBinomialMatchQ",
    "GeneralizedTrinomialMatchQ": "%mr_generalizedTrinomialMatchQ",
    "GeneralizedBinomialDegree": "%mr_generalizedBinomialDegree",
    "GeneralizedTrinomialDegree": "%mr_generalizedTrinomialDegree",
    "BinomialDegree": "%mr_binomialDegree",
    "SumQ": "%mr_sumQ", "SumSimplerQ": "%mr_sumSimplerQ",
    "SimplerQ": "%mr_simplerQ", "SimplerSqrtQ": "%mr_simplerSqrtQ",
    "NiceSqrtQ": "%mr_niceSqrtQ", "RationalFunctionQ": "%mr_rationalFunctionQ",
    "MatchQ": "%mr_matchQ", "SplitProduct": "%mr_splitProduct",
    "NonfreeFactors": "%mr_nonfreeFactors",
    "FractionalPowerFactorQ": "%mr_fractionalPowerFactorQ",
    "LeafCount": "%mr_leafCount", "MonomialQ": "%mr_monomialQ",
    "PerfectSquareQ": "%mr_perfectSquareQ", "AtomQ": "%mr_atomQ",
    "LinearPairQ": "%mr_linearPairQ", "PseudoBinomialPairQ": "%mr_pseudoBinomialPairQ",
    "InverseFunctionQ": "%mr_inverseFunctionQ",
    "AlgebraicFunctionQ": "%mr_algebraicFunctionQ",
}

# Structural rewrites (not 1:1 renames): token -> handler name in the emitter.
RESTRUCTURE = {
    "GtQ": "cmp", "LtQ": "cmp", "LeQ": "cmp", "GeQ": "cmp",
    "IGtQ": "cmp", "ILtQ": "cmp", "ILeQ": "cmp",
    "Int": "mr_int",              # Int[smaller, x] -> mr_int(smaller, x)
    "Unintegrable": "noun", "CannotIntegrate": "noun",   # -> mr_unintegrable
    "IntHide": "mr_int",
    "Sum": "mr_sum",
    "With": "block", "Module": "block",
    "If": "if",
    "EllipticF": "mr_elliptic_f", "EllipticE": "mr_elliptic_e",
    "EllipticPi": "mr_elliptic_pi",
    "Hypergeometric2F1": "hypergeometric",   # list-form args
    "AppellF1": "mr_appellf1",
    "Root": "%mr_root", "Hold": "%mr_hold", "Boole": "if",
    "Integrate": "integrate", "ShowStep": "drop",
    "Pi": "Pi", "E": "E", "I": "I", "Abs": "abs",
    "Sinh": "sinh", "Tanh": "tanh", "Csc": "csc", "Sec": "sec",
    "Piecewise": "mr_piecewise", "Min": "min", "Max": "max",
    "CoefficientList": "%mr_coefficientList",
    "Power": "power", "Plus": "plus", "Times": "times",
}

def translate(token):
    if token in RENAME:
        return RENAME[token]
    if token in RESTRUCTURE:
        return RESTRUCTURE[token]
    raise KeyError(f"unlisted token {token!r} — extend the table (T4 §2) "
                   f"before generating")
```

- [ ] **Step 2: Write `generator/generate_class1.py`**

Reuse the census parser by path import (the census's own idiom):

```python
#!/usr/bin/env python3
"""generate_class1.py — emit rules/class1/*.mac from Rubi 4's class-1 .m files.

Only the files Rubi.m actually LoadRules() (67 files, 2,710 rules — the T1
count; 22 stale on-disk files are skipped by construction). Usage:
    python3 generator/generate_class1.py [--only 1.1.1.1]
Fails loudly (exit 1, file+rule+token named) on an unlisted token, an
unparseable rule run, or a pattern variable it cannot rename.
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUBI = ROOT / "reference" / "rubi"
OUT = ROOT / "rules" / "class1"
PIN = "61e9c18ea248061cd83c67882f7c91a73cef912d"

# reuse the census parser verbatim (T4 §4 step 1)
def _load(name, rel):
    p = ROOT / "probes" / rel
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

_inv = _load("inv01", "probe-rubi-anatomy/01-inventory.py")
_cen = _load("cen01", "translation/01-class1-syntax-census.py")
strip_comments, parse_load_rules = _inv.strip_comments, _inv.parse_load_rules
rule_runs, split_rule = _cen.rule_runs, _cen.split_rule

sys.path.insert(0, str(Path(__file__).resolve().parent))
from translation_table import translate

MIT = ("/* Ported from Rule-Based Integration (Rubi), "
       "https://github.com/RuleBasedIntegration/Rubi\n"
       " * Copyright (c) 2018 Rule-Based-Integration Organization (MIT). */")

def key_of(rel_m):
    # "1 Algebraic functions/.../1.1.1.1 (a+b x)^m.m" -> "1_1_1_1"
    base = rel_m.split("/")[-1]
    num = base.split(" ")[0]
    return num.replace(".", "_")

def m2m(tok):
    """Mathematica head -> Maxima head for the pattern/replacement text."""
    return {"Int": "mr_int", "Sqrt": "sqrt", "Log": "log",
            "ArcTan": "atan", "ArcSin": "asin", "ArcCos": "acos",
            "ArcTanh": "mr_atanh", "ArcSinh": "mr_asinh",
            "ArcCosh": "mr_acosh"}.get(tok, tok)

def rename_vars(text, key, n, varset):
    """v -> _mr_<key>_r<n>_v for every pattern variable in varset."""
    out = text
    for v in sorted(varset, key=len, reverse=True):
        out = re.sub(rf"\b{v}\b", f"_mr_{key}_r{n}_{v}", out)
    return out

def pattern_vars(lhs):
    """Capture names in a rule lhs: v_ and v_. (x_Symbol excluded — the
    pattern argument)."""
    vs = set(re.findall(r"([A-Za-z][A-Za-z0-9]*)_\.", lhs))
    vs |= set(re.findall(r"(?<!\.)\b([A-Za-z][A-Za-z0-9]*)_(?![.\w])", lhs))
    return vs - {"x"}

def split_top(s, sep=","):
    """Split s on top-level sep, honouring [ ] ( ) { } nesting."""
    out, depth, cur = [], 0, []
    for ch in s:
        if ch in "[({":
            depth += 1
        elif ch in "])}":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out

def head_args(s):
    """If s (stripped) is exactly `head[args]`, return (head, args); else
    (None, s). The matching ] is the one at depth 0 for the first [."""
    s = s.strip()
    m = re.match(r"^([A-Za-z][A-Za-z0-9]*)\[(.*)\]$", s, re.DOTALL)
    if not m:
        return (None, s)
    head, args = m.group(1), m.group(2)
    # verify the [ and ] are balanced (the regex is greedy to the last ])
    depth, ok = 0, True
    for ch in s:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                break
    else:
        ok = depth == 0
    return (head, args) if ok else (None, s)

def drop_optionals(text, varset):
    """v_. and v_ -> the renamed capture (the plain pattern; the matcher's
    decomposition fills the Plus/Times identity defaults). Power-optional
    exponents are D-duplicated at the emit level, not here."""
    for v in sorted(varset, key=len, reverse=True):
        text = text.replace(v + "_.", v).replace(v + "_", v)
    return text

def translate_token(tok, key, n, varset):
    """A bare identifier -> renamed capture / table name / itself.
    Raises on a head token the table does not list (loud failure)."""
    if tok in varset:
        return f"_mr_{key}_r{n}_{tok}"
    if tok in ("x", "Pi", "E", "I"):
        return tok
    if tok in RENAME or tok in RESTRUCTURE:
        return translate(tok)
    # unknown identifier that is not a capture: a Maxima symbol (a, b, c, …)
    # appearing in a cond/rhs but not the lhs — pass through.
    return tok

def translate(s, key, n, varset):
    """Recursive translator: .m expression -> Maxima expression.

    Walks a token stream; on `head[args]` it translates each top-level arg
    and applies the head's special form (FreeQ arg-flip, Int -> mr_int,
    With/Module -> block, the cmp family -> is(), Hypergeometric2F1 list
    form). Atoms rename captures and drop optionals.
    """
    s = s.strip()
    head, args = head_args(s)
    if head is not None:
        arglist = [translate(a, key, n, varset)
                   for a in split_top(args, ",")] if args.strip() else []
        return emit_head(head, arglist, key, n, varset)
    return translate_atom(s, key, n, varset)

def emit_head(head, arglist, key, n, varset):
    """Special forms first, then a plain renamed head[arglist]."""
    if head == "FreeQ":
        # FreeQ[e, x] -> freeof(x, e); FreeQ[{a,b}, x] -> and of freeof
        e, xv = arglist[0], arglist[1]
        inner = e[1:-1] if e.startswith("{") and e.endswith("}") else e
        parts = [f"freeof({xv}, {p.strip()})" for p in split_top(inner, ",")]
        return " and ".join(parts)
    if head in ("GtQ", "LtQ", "LeQ", "GeQ", "IGtQ", "ILtQ", "ILeQ"):
        op = {"GtQ": ">", "LtQ": "<", "LeQ": "<=", "GeQ": ">=",
              "IGtQ": ">", "ILtQ": "<", "ILeQ": "<="}[head]
        return f"is({arglist[0]} {op} {arglist[1]})"
    if head in ("Int", "IntHide"):
        return f"mr_int({arglist[0]}, {arglist[1]})"
    if head in ("Unintegrable", "CannotIntegrate"):
        return f"mr_unintegrable({arglist[0]}, {arglist[1]})"
    if head == "With" or head == "Module":
        # With[{a = e}, body] / Module[{a = e}, body] -> block([a], a : e, body)
        decls = arglist[0][1:-1]          # strip { }
        body = arglist[1]
        pairs = split_top(decls, ",")
        locals_, assigns = [], []
        for p in pairs:
            name, val = [q.strip() for q in split_top(p, "=")]
            rn = translate_token(name, key, n, varset)
            locals_.append(rn)
            assigns.append(f"{rn} : {translate(val, key, n, varset)}")
        return (f"block([{', '.join(locals_)}], "
                + ", ".join(assigns) + ", "
                + translate(body, key, n, varset) + ")")
    if head == "If":
        return f"if {arglist[0]} then {arglist[1]} else {arglist[2]}"
    if head == "Boole":
        return f"if {arglist[0]} then 1 else 0"
    if head == "Hypergeometric2F1":
        a, b, c, z = arglist
        return f"hypergeometric([{a}, {b}], [{c}], {z})"
    if head in ("EllipticF", "EllipticE", "EllipticPi"):
        fn = {"EllipticF": "mr_elliptic_f", "EllipticE": "mr_elliptic_e",
              "EllipticPi": "mr_elliptic_pi"}[head]
        return f"{fn}({', '.join(arglist)})"
    name = translate_token(head, key, n, varset)
    return f"{name}[{', '.join(arglist)}]"

def translate_atom(s, key, n, varset):
    """A non-`head[...]` expression: rename captures, drop optionals,
    rewrite && / || / Not, and translate any nested head[args] sub-expressions.
    Works on a token walk so nested heads inside sums/products are handled."""
    out, i, L = [], 0, len(s)
    while i < L:
        m = re.match(r"[A-Za-z][A-Za-z0-9]*", s[i:])
        if m:
            name = m.group()
            j = i + len(name)
            # `x_Symbol` -> x (the pattern argument)
            if s[j:j+8] == "_Symbol":
                out.append("x"); i = j + 8; continue
            # a capture named like the integration variable is the integration
            # variable (Mathematica same-named patterns must agree): `x_` -> x,
            # consuming the marker, no matchdeclare (see Generator algorithm 2).
            if name == "x" and s[j:j+2] in ("_.", "_ "):
                out.append("x"); i = j + 2; continue
            if name == "x" and s[j:j+1] == "_":
                out.append("x"); i = j + 1; continue
            # a free capture with an optional marker: v_. or v_
            if name in varset and s[j:j+2] in ("_.", "_ "):
                out.append(f"_mr_{key}_r{n}_{name}")
                i = j + 2; continue
            if name in varset and s[j:j+1] == "_":
                out.append(f"_mr_{key}_r{n}_{name}")
                i = j + 1; continue
            # a nested head[args]?
            k = j
            while k < L and s[k] in " \t":
                k += 1
            if k < L and s[k] == "[":
                # find the matching ]
                depth, t = 0, k
                while t < L:
                    if s[t] == "[":
                        depth += 1
                    elif s[t] == "]":
                        depth -= 1
                        if depth == 0:
                            break
                    t += 1
                argtxt = s[k+1:t]
                out.append(translate(name + "[" + argtxt + "]", key, n, varset))
                i = t + 1; continue
            out.append(translate_token(name, key, n, varset)); i = j; continue
        if s[i:i+2] == "&&":
            out.append(" and "); i += 2; continue
        if s[i:i+2] == "||":
            out.append(" or "); i += 2; continue
        out.append(s[i]); i += 1
    return " ".join(out).strip()

def power_dups(pattern, key, n, varset):
    """Return the list of pattern texts to emit for one rule: the plain
    pattern, plus a duplicate with each optional Power exponent (`u_^m_.`)
    dropped and `m` bound to 1 — the structural case decomposition cannot
    fill (measured 2026-08-20). Most rules yield exactly one pattern."""
    pats = [pattern]
    for m in re.finditer(r"([A-Za-z][A-Za-z0-9]*)\^\s*("
                         + "|".join(sorted(varset, key=len, reverse=True))
                         + r")_\.\b", pattern):
        base, exp = m.group(1), m.group(2)
        dup = pattern.replace(base + f"^{exp}_.", base, 1)
        pats.append((dup, exp))
    # (dup, exp) pairs become extra matchers binding <exp> := 1; a single
    # element returns the plain pattern only.)
    return pats
```

(The emitter above is complete: `split_top`/`head_args` are the paren-aware
splitters; `translate`/`emit_head`/`translate_atom` are the recursive
translator (FreeQ arg-flip, the cmp family to `is()`, `Int`→`mr_int`,
`With`/`Module`→`block`, `Hypergeometric2F1` list form, `Not`/`&&`/`||`);
`power_dups` handles the Power-optional structural case. The rule/file
emitters and the driver are the next block — written against 1.1.1.1 first
(the Task 4 Step 3 tracer) and extended as Task 6 pulls in the other 66,
each extension covered by that file's census row and its corpus section.)

Continue the module with the emitters and driver:

```python
def emit_rule(run, key, n, rule_vars):
    """One rule run (lhs, rhs, cond) -> the five Maxima functions as text.
    rule_vars is the set of capture names (from the lhs)."""
    lhs, rhs, cond = run
    # integrand pattern: strip Int[ ... , x_Symbol]
    m = re.match(r"^Int\[(.*),\s*x_Symbol\]$", lhs.strip(), re.DOTALL)
    if not m:
        raise GenError(f"{key} r{n}: cannot strip Int[...]: {lhs!r}")
    pat_text = drop_optionals(translate(m.group(1), key, n, rule_vars),
                              rule_vars)
    pat_text = pat_text.replace(f"_mr_{key}_r{n}_", f"_mr_{key}_r{n}_")  # identity
    # declare each capture; freeof(x)-guarded if the cond has FreeQ[... , x]
    freeq_guarded = set(re.findall(r"FreeQ\[\{?([^}]*)\}?,\s*x\]",
                                   cond or ""))
    freeq_guarded = set(v.strip() for v in freeq_guarded.split(","))
    decls = []
    for v in sorted(rule_vars):
        pred = "freeof(x)" if v in freeq_guarded else "true"
        decls.append(f"matchdeclare(_mr_{key}_r{n}_{v}, {pred})$")
    # cond: translate; an empty cond -> true
    cond_txt = (translate(drop_optionals(cond, rule_vars), key, n, rule_vars)
                if cond else "true")
    repl_txt = translate(drop_optionals(rhs, rule_vars), key, n, rule_vars)
    binds = [f"{v} : geteqR(mm, '_mr_{key}_r{n}_{v}')"
             for v in sorted(rule_vars)]
    bind_block = ", ".join(binds) if binds else "true"
    pat_name = f"_mr_pat_{key}_r{n}"
    lines = list(decls)
    lines.append(f"defmatch({pat_name}, {pat_text}, x)$")
    lines.append(f"_mr_cond_{key}_r{n}(mm, x) := block([{', '.join(sorted(rule_vars))}],")
    lines.append(f"  {bind_block},")
    lines.append(f"  {cond_txt})$")
    lines.append(f"_mr_repl_{key}_r{n}(mm, x) := block([{', '.join(sorted(rule_vars))}],")
    lines.append(f"  {bind_block},")
    lines.append(f"  {repl_txt})$")
    lines.append(f"_mr_rule_{key}_r{n}(f, x) := block([mm, ok],")
    lines.append(f"  mm : {pat_name}(f, x),")
    lines.append("  if mm = false then return(false),")
    lines.append(f"  ok : _mr_cond_{key}_r{n}(mm, x),")
    lines.append(f"  if is(ok) = true then _mr_repl_{key}_r{n}(mm, x) else false)$")
    return "\n".join(lines)

def emit_file(rel_m, runs):
    key = key_of(rel_m)
    header = (f"/* rules/class1/{key}.mac — GENERATED; do not edit.\n"
              f" * Source: Rubi 4 {PIN}\n"
              f" *          {rel_m}\n * Regenerate: "
              f"python3 generator/generate_class1.py --only {key_of(rel_m)} */\n"
              f"{MIT}\n\n")
    body = []
    rule_fns = []
    for n, run in enumerate(runs, start=1):
        rule_vars = pattern_vars(run[0])
        body.append(emit_rule(run, key, n, rule_vars))
        rule_fns.append(f"_mr_rule_{key}_r{n}")
        body.append("")
    body.append(f"mr_rules_{key} : [ {', '.join(rule_fns)} ]$")
    body.append(f"mr_rules_count_{key} : {len(runs)}$")
    body.append(f"mr_witness_{key}() := true$")
    return header + "\n".join(body) + "\n"

class GenError(SystemExit):
    def __init__(self, msg):
        print(f"generate_class1: {msg}", file=sys.stderr)
        super().__init__(1)

def load_class1_files(rubi):
    """The 67 class-1 .m files, in Rubi.m LoadRules order, as paths relative
    to the Rubi clone root. parse_load_rules yields (parts, gated); the parts
    are relative to IntegrationRules/ and lack the .m extension (LoadRules
    appends it). Only the non-gated (mandatory) class-1 files are ported."""
    order = parse_load_rules((rubi / "Rubi" / "Rubi.m").read_text())
    out = []
    for parts, gated in order:
        if gated:
            continue                      # $LoadElementaryFunctionRules block
        if not parts or not parts[0].startswith("1 "):
            continue                      # class 1 only
        rel = "Rubi/IntegrationRules/" + "/".join(parts) + ".m"
        out.append(rel)
    return out

def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].replace(".", "_")
    files = load_class1_files(RUBI)
    total = 0
    for rel_m in files:
        key = key_of(rel_m)
        if only and key != only:
            continue
        text = strip_comments((RUBI / rel_m).read_text())
        runs = rule_runs(text)
        out = OUT / f"{key}.mac"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(emit_file(rel_m, runs))
        print(f"  {key}: {len(runs)} rules")
        total += len(runs)
    note = "OK (== 2710)" if (total == 2710 and not only) else \
           ("partial (--only)" if only else f"MISMATCH (expected 2710)")
    print(f"TOTAL: {total} rules — {note}")
    if not only and total != 2710:
        raise GenError(f"rule total {total} != 2710 (T1 census); aborting")

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Generate 1.1.1.1 and inspect it**

Run: `python3 generator/generate_class1.py --only 1.1.1.1`
Expected: `rules/class1/1_1_1_1.mac` with 5 rules (the file has exactly 5
`Int` rules — count them in the source first: `grep -c "^Int\[" "reference/rubi/Rubi/IntegrationRules/1 Algebraic functions/1.1 Binomial products/1.1.1 Linear/1.1.1.1 (a+b x)^m.m"` → 5). The emitted file must show: the pin + MIT header; per-rule `matchdeclare`/`defmatch(_mr_pat_1_1_1_1_r<n>, …, x)`; `_mr_cond_…`/`_mr_repl_…` with the block-local `geteqR` preamble (standalone statements, never nested in a call's args); `_mr_rule_…`; `mr_rules_1_1_1_1 : [ … ]$`; `mr_rules_count_1_1_1_1 : 5$`; `mr_witness_1_1_1_1() := true$` last.

- [ ] **Step 4: Wire the loader**

In `maxima_rubi.mac`, after the utils load:

```
%mr_load_sibling("rules/class1/1_1_1_1.mac", 'mr_witness_1_1_1_1)$
mr_rule_table : mr_rules_1_1_1_1$
```

- [ ] **Step 5: Swap the hand-written rules for the generated file in Layer A**

In `test_maxima_rubi.mac`: delete the Task-3 hand-written rule block and
`mr_rule_table : [ _mr_rule_t3_rec, _mr_rule_t3_power ]$` (the loader now
sets the table). Add a **structural** test — the file loads, the witness
survives, and the rule count matches the source. (The *behavioral* test of
the five rules needs the Task 5 predicates and lands there.)

```
test_rules_1_1_1_1_struct() := block([],
  print("--- generated 1.1.1.1 (structural) ---"),
  check_bool("witness survived", is(mr_witness_1_1_1_1() = true)),
  check("count cross-check", mr_rules_count_1_1_1_1, 5),
  check_bool("table is the file's rules", is(mr_rule_table = mr_rules_1_1_1_1)),
  true
)$
```

Add `test_rules_1_1_1_1_struct(),` to `run_all_tests`.

- [ ] **Step 6: Run Layer A**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: `0 failed` with the Results line. A FAIL here is a generator
defect (bad emission, a parse error in the generated `.mac`, a wrong
count). The generated rules reference `%mr_*` predicates that are not yet
defined — that is fine at load time (they are noun references inside `:=`
bodies, not evaluated); their behavior is tested in Task 5 once ported.

- [ ] **Step 7: Commit**

```sh
git add generator/ rules/class1/1_1_1_1.mac maxima_rubi.mac test_maxima_rubi.mac
git commit -m "feat: class-1 generator (closed table, loud failure) + first generated file 1.1.1.1 (structural)"
```

---

### Task 5: Predicate cluster #1 — the 1.1.1.x / workhorse closure

**Files:**
- Modify: `maxima_rubi_utils.mac` (add the ported predicates + shims)
- Modify: `test_maxima_rubi.mac` (unit probes per function)

**Interfaces:**
- Produces (exact names — the generator's table already emits these):
  `%mr_subst`, `%mr_linearQ`, `%mr_polyQ`, `%mr_removeContent`,
  `%mr_coeff`, `%mr_posQ`, `%mr_negQ`, `%mr_sign`, **and the clone-gap
  equality pair** `%mr_possible_zeroQ`/`%mr_eqQ`/`%mr_neQ` (Global
  Constraints clone-gap note — referenced by `EqQ`/`NeQ` but undefined in
  the pinned clone, so derived from usage), plus their internal helpers
  (`%mr_degree`, `%mr_nonfreeFactors`, `%mr_freeFactors`, `%mr_together`,
  `%mr_simp`). Each gets unit probes against fixed input/output pairs drawn
  from its `.m` semantics before any generated rule that calls it is trusted
  (the T4 unit-probe requirement).

This task also carries the **first behavioral test of a generated file**
(1.1.1.1, Task 4's structural file): once the predicates are ported, the
five real rules are exercised end-to-end.

Porting sources (the pinned clone, read-only): `Rubi/IntegrationUtilityFunctions.m`
— `LinearQ` at :1373 (delegates to `PolyQ[u, x, 1]`), `RemoveContent` at
:1152 (via `NonfreeFactors`/`FreeFactors`/`Together`/`RemoveContentAux`),
`PolyQ` at :494, `Coeff`/`Coefficient` (Mathematica builtin — reimplement
over Maxima's `coefficient`, which is a **noun in this build**, hence the
`%mr_coeff` shim), `Subst` at :5140 (the back-substitution form used by
1.1.1.1's last rule).

- [ ] **Step 1: Write the unit probes first (red)**

Add to `test_maxima_rubi.mac`:

```
test_pred_cluster1() := block([],
  print("--- predicate cluster 1 ---"),
  /* %mr_coeff: Maxima's coefficient is a noun here; %mr_coeff works */
  check("coeff x^2+2x+1", %mr_coeff(x^2 + 2*x + 1, x, 1), 2),
  check("coeff 3x", %mr_coeff(3*x, x, 1), 3),
  check("coeff missing", %mr_coeff(3*x, x, 2), 0),
  /* %mr_polyQ / %mr_linearQ: degree tests */
  check_bool("polyQ x^2+x", %mr_polyQ(x^2 + x, x)),
  check_not("polyQ 1/x", %mr_polyQ(1/x, x)),
  check_bool("linearQ a+b x", %mr_linearQ(a + b*x, x)),
  check_not("linearQ x^2", %mr_linearQ(x^2, x)),
  /* %mr_removeContent: strips the x-free content factor */
  check("removeContent 3(x+1)", ratsimp(%mr_removeContent(3*(x + 1), x)), x + 1),
  /* %mr_sign / posQ / negQ: the pos/neg/pnz mapping */
  check("sign pos", %mr_sign(3), 1),
  check("sign neg", %mr_sign(-3), -1),
  check("sign zero", %mr_sign(0), 0),
  check_bool("posQ a (undecidable -> false)", not %mr_posQ(a)),
  check_bool("posQ 3", %mr_posQ(3)),
  /* %mr_subst: Rubi's back-substitution (Subst[ans, x, u]) */
  check("subst", ratsimp(%mr_subst(x^2/2, x, 2*y)), ratsimp(2*y^2)),
  /* clone-gap equality pair (derived from usage — see clone-gap note) */
  check_bool("possible_zero 0", %mr_possible_zeroQ(0)),
  check_bool("possible_zero (x-x)", %mr_possible_zeroQ(x - x)),
  check_not("possible_zero 5", %mr_possible_zeroQ(5)),
  check_bool("possible_zero a (undecidable)", %mr_possible_zeroQ(a)),
  check_bool("neQ 1 2", %mr_neQ(1, 2)),
  check_not("neQ 1 1", %mr_neQ(1, 1)),
  check_bool("neQ a b (undecidable -> loose true)", %mr_neQ(a, b)),
  check_bool("eqQ a a", %mr_eqQ(a, a)),
  check_not("eqQ 1 2", %mr_eqQ(1, 2)),
  true
)$
```

Add `test_pred_cluster1(),` to `run_all_tests`.

- [ ] **Step 2: Run to confirm red**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: FAILs naming the missing `%mr_*` functions (or no Results line —
a hard error on the first undefined call; both are "red").

- [ ] **Step 3: Implement the cluster in `maxima_rubi_utils.mac`**

Each function ports its `.m` source (cited above) to Maxima under the
house rules; the implementations are small (5–30 lines each). The two with
measured traps get their notes here:

```
/* Maxima's coefficient/degree/maxexpt are NOUNS in this build (T4 §6) —
   the shims take %mr_ names (house rule 8) and may become one-line
   pass-throughs on 5.50 after re-running 02-support-surface.run. */
%mr_coeff(u, x, n) := block([c],
  c : coefficient(u, x, n),
  if is(c = coefficient(u, x, n)) = false then c
  else if n > 0 then part(num(rat(u)), 1) /* fallback: exact rational form */
       else 0)$

/* clone-gap equality pair (referenced by EqQ/NeQ, undefined in the pinned
   clone — derived from usage, Global Constraints clone-gap note). "possibly
   zero" = "not provably nonzero" under Maxima's three-valued is(). */
%mr_possible_zeroQ(e) := block([nz],
  nz : is(e # 0),
  if nz = true then false else true)$
%mr_eqQ(u, v) := %mr_possible_zeroQ(u - v)$
%mr_neQ(u, v) := not %mr_possible_zeroQ(u - v)$
```

(Step 3 is written out fully against the `.m` sources during execution —
each function lands with its unit probes green before the next. The
`%mr_simp` policy is the zero-chain `ratsimp → ratsimp∘expand → factor →
ratsimp∘factor`, `simplify`/`together` unbound here; `%mr_together` is
`num(e)/den(e)` after `rat`.)

- [ ] **Step 4: First behavioral test — generated 1.1.1.1 end-to-end**

With cluster 1 ported, the five real 1.1.1.1 rules (Task 4's structural
file) now run. Add to `test_maxima_rubi.mac`:

```
test_rules_1_1_1_1_behavior() := block([r],
  print("--- generated 1.1.1.1 (behavioral) ---"),
  /* rule 2: the power rule x^m (m free of x, m # -1) */
  check("x^3", rubi(x^3, x), x^4/4),
  check("5x^2", rubi(5*x^2, x), 5*x^3/3),
  /* rule 1: 1/x -> log(x) */
  check("1/x", rubi(1/x, x), log(x)),
   /* rule 4: (a+b x)^m, m # -1. d/dx[(1+2x)^4/8] = (1+2x)^3 (verified 2026-08-20;
      the original /12 in this plan was a wrong antiderivative). */
   check("(1+2x)^3", ratsimp(rubi((1 + 2*x)^3, x)), ratsimp((1 + 2*x)^4/8)),
   /* rule 3: 1/(a+b x) -> log(RemoveContent[a+b x, x])/b */
   check("1/(a+b x)", ratsimp(rubi(1/(a + b*x), x)), ratsimp(log(a + b*x)/b)),
   /* rule 4 again: (1+2*(3x))^2 simplifies to (1+6x)^2 (linear in x), so rule 4
      handles it (NOT rule 5 — rule 5's (a+b*u)^m pattern is dead in this build,
      shadowed by rule 4; see ledger F1). d/dx[(1+6x)^3/18] = (1+6x)^2. */
   r : rubi((1 + 2*(3*x))^2, x),
   check_bool("linear base (1+6x)^2", is(ratsimp(r) = ratsimp((1 + 6*x)^3/18))),
  /* NeQ[m, -1]: the m = -1 case must NOT take the power rule (falls to 1/x) */
  check_bool("NeQ guard honored", is(rubi(1/x, x) = log(x))),
  true
)$
```

Add `test_rules_1_1_1_1_behavior(),` to `run_all_tests`.

- [ ] **Step 5: Run Layer A to green**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: `0 failed`, Results line. A FAIL is a predicate-port defect or a
generator defect (Power-optional D-duplication for the bare-`x` case, the
`freeof(x)` matchdeclare guards, the `%mr_subst`/`%mr_removeContent` ports).

- [ ] **Step 6: Commit**

```sh
git add maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "feat: predicate cluster 1 + clone-gap eq/neQ + first behavioral 1.1.1.1 test"
```

---

### Task 6: Generate all 67 files + load wall + census cross-check

**Files:**
- Modify: `generator/generate_class1.py` (full-class emission)
- Create (generated): `rules/class1/*.mac` (67 files)
- Modify: `maxima_rubi.mac` (the full load list, Rubi order)
- Create: `probes/load_wall/mac` or `.run` probe (the T5 §5 open item 1)

**Interfaces:**
- Consumes: Task 4's generator; the census (2,710 rules / 67 files).
- Produces: `rules/class1/` complete; the loader loads all 67 in Rubi
  `LoadRules` order and assembles `mr_rule_table : mr_rules_1_1_1_1 concat
  mr_rules_1_1_1_2 concat …`; the **measured `defmatch` load wall** (the
  first implementation milestone includes measuring it — T5 §5).

- [ ] **Step 1: Extend the generator to all 67 files**

Run: `python3 generator/generate_class1.py`
Expected: 67 files under `rules/class1/`; the generator prints per-file
counts; the total line is `rules: 2710`. Any loud failure (unlisted token,
unparseable run) is fixed at the source — extend `translation_table.py`
only if the census table was wrong (record it in the commit message);
fix the emitter if the emitter was wrong. Do not weaken the loud failure.

- [ ] **Step 2: Wire the full load list**

The generator also emits (or prints) the ordered load list; paste it into
`maxima_rubi.mac` between the utils load and the table assembly, one
`%mr_load_sibling("rules/class1/<key>.mac", 'mr_witness_<key>)$` per file
in Rubi order, then:

```
mr_rule_table : mr_rules_1_1_1_1 concat mr_rules_1_1_1_2 concat … $
```

(67 concat terms, generated — not hand-typed.)

- [ ] **Step 3: Measure the load wall (T5 §5 open item 1)**

Create `probes/load_wall/probe-load-wall.run` + the Maxima batch it runs:
time `load("maxima_rubi.mac")` cold (fresh `maxima --very-quiet -b`),
stamped with `build_info()`, output the wall to
`probes/load_wall/probe-load-wall.out`.

Run: `sh probes/load_wall/probe-load-wall.run`
Expected: a wall time. **Decision gate (T5 §5):** if load exceeds ~1
minute, the optional-slot strategy moves toward normalization (N) for the
high-fan-out rules before Task 9's full run — record the measurement and
the decision in the commit message and in `todo/TODO.md`'s T5 note.
(With the plain-pattern/decomposition strategy there is no D fan-out, so
the wall is the bare 2,710 `defmatch` compilations; the measurement
confirms that is loadable.)

- [ ] **Step 4: Census cross-check in Layer A**

Add to `test_maxima_rubi.mac`:

```
test_census() := block([n],
  print("--- census cross-check ---"),
  n : length(mr_rule_table),
  check("global rule count = 2710", n, 2710),
  check("1.1.1.2 count", mr_rules_count_1_1_1_2, <census count>),
  true
)$
```

(`<census count>` is read from
`probes/translation/01-class1-syntax-census.out`'s per-file table — the
census's own numbers, not re-derived.) Add `test_census(),` to
`run_all_tests`.

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: `0 failed`, `2710` confirmed.

- [ ] **Step 5: Commit**

```sh
git add generator/ rules/class1/ maxima_rubi.mac test_maxima_rubi.mac probes/load_wall/
git commit -m "feat: full class-1 generation (67 files, 2710 rules) + measured load wall"
```

---

### Task 7: Full utility layer — the remaining predicates and shims

**Files:**
- Modify: `maxima_rubi_utils.mac`
- Modify: `test_maxima_rubi.mac`

**Interfaces:**
- Produces: every remaining `%mr_*` name in the translation table (the
  37 C-tier structural predicates not yet ported, the B_TIER operators,
  the ~15 shims), each with unit probes. This is the finite utility layer
  of T4 §4 — none of it is per-rule work.

- [ ] **Step 1: Work the cluster order**

T4's concentration data orders the work: the 679 MANUAL-bucket rules
cluster — the top ten files hold 285 of them, and 23 of the 64 files carry
a single distinct token-set (clear in one pass once their one predicate is
ported). Port in census usage order (PolyQ 376, IntBinomialQ 78, LinearQ
61, SumSimplerQ 36, BinomialQ 32, SimplerQ 29, … down the
`01-class1-syntax-census.out` "C-tier tokens" list), each:

1. read its `.m` source in the pinned clone (read-only),
2. write its unit probes (2–5 fixed input/output pairs from the `.m`
   semantics) into `test_maxima_rubi.mac`,
3. run Layer A (red),
4. implement the `%mr_*` function under the house rules,
5. run Layer A (green),
6. commit per cluster (3–6 functions per commit, message naming them).

- [ ] **Step 2: The shims**

The ~15 this-binary shims (`%mr_atanh`/`%mr_asinh`/`%mr_acosh` log forms,
`%mr_ratroot` family via `%mr_rt`, `%mr_cancel`, `%mr_hold`, `%mr_boole`,
`%mr_gcf`, `%mr_degree`/`%mr_maxexpt`/`%mr_minexpt`, `%mr_nodecount` for
`LeafCount`, `%mr_rationalp` for `RationalQ`/`IntegersQ`/`FractionQ`,
`%mr_positivep`-family for `PosQ`/`NegQ`) each get the same red-green
probe cycle; on a future 5.50 upgrade, re-run
`sh probes/translation/02-support-surface.run` and delete whatever became
a builtin (the table names the shims; they may become pass-throughs).

- [ ] **Step 3: Completion gate**

Run: `maxima --very-quiet -b test_maxima_rubi.mac`
Expected: `0 failed`; every `%mr_*` name in `translation_table.py` either
exists in utils or is a Maxima builtin (the generator's loud-failure
contract makes any miss impossible to ship silently).

---

### Task 8: Layer B — the corpus driver + 1.1.1.2 smoke

**Files:**
- Create: `test/corpus_class1_driver.py`
- Create: `test/mr_preload.mac`

**Interfaces:**
- Consumes: the package (Tasks 2–7); the corpus
  (`reference/maxima-syntax-test-suite/1 Algebraic functions/`, pinned);
  T3's driver mechanics (`probes/corpus/probe-integrate-sample.py` — same
  per-integral-subprocess design, the package in place of `integrate`).
- Produces: one `PASS:`/`FAIL:` line per integral (from the batch's CLASS
  line) and a final `Results: <n> passed, <m> failed` line — the same
  reading protocol as Layer A. Verdict mapping (T5 §3): `expected` /
  `verified` / `no-answer` → PASS; `unverified` / `unexpected` / `error` /
  `timeout` → FAIL.

- [ ] **Step 1: Write `test/mr_preload.mac`**

```
batch_answers_from_file: true$
load("maxima_rubi.mac")$
```

- [ ] **Step 2: Write `test/corpus_class1_driver.py`**

Generalize `probes/corpus/probe-integrate-sample.py` (keep its measured
mechanics verbatim where they are load-bearing): one fresh
`maxima --very-quiet -p test/mr_preload.mac -b <one-entry batch>` per
integral; the `mr_`/`MR_`-prefixed template variables (the T3 §3.3.2
collision trap); the noun detector
`is(string(op(mr_r)) = "integrate")` behind an `atom` guard (T3 §3.3.3);
the 30 s per-process wall cap; the answer pool (`pos$`×6 / `no$`×6 —
harness safety net for the `integrate` fall-through, never a package
feature, house rule 9); streaming one line per integral with the same
`resume-info.py`/`merge-shards.py` compatibility; the CLASS body with the
package in place of `integrate`:

```
mr_f: <integrand>$
mr_r: rubi(mr_f, <var>)$
pos$ × 6, no$ × 6
… same noun/expected/verified/unverified chain, zero-chain
  ratsimp → ratsimp∘expand → factor → ratsimp∘factor …
```

Same CLI shape as the T3 driver (`[filter] [per-file] [timeout] [suite-dir]
[start-index] [append] [skip-first] [out-file] [stop-index]`) so the
18-shard planner and `merge-shards.py` carry over unchanged.

- [ ] **Step 3: Smoke — 1.1.1.2, first 20 entries**

Run: `python3 test/corpus_class1_driver.py "1.1.1.2" 20 30`
Expected: 20 CLASS lines, a `Results:` line, no subprocess deaths. This
file (1,917 entries, mostly fast — the handoff's suggested smoke) is the
first real contact between the generated rules and the corpus.

- [ ] **Step 4: Triage the smoke**

Every FAIL is one of: a rule that misfired (decomposition, T2 §3.5 — fix
the rule's predicates or D-duplicate that one rule), a predicate port
error (fix + re-probe), a zero-chain miss (the T4 §4 strengthen loop,
Task 9), or a genuine divergence (record it). Do not move to the full run
with untriaged FAILs.

- [ ] **Step 5: Commit**

```sh
git add test/corpus_class1_driver.py test/mr_preload.mac
git commit -m "feat: Layer-B corpus driver (package in place of integrate) + 1.1.1.2 smoke"
```

---

### Task 9: Full class-1 run + divergence loop + acceptance

**Files:**
- Modify: `rules/class1/*.mac` (per-rule fixes via generator re-run),
  `maxima_rubi_utils.mac` (predicate fixes, zero-chain),
  `generator/*` (D-duplication opt-in if triggered)
- Create: `docs/corpus-baseline-uplift.md` (the measured acceptance record)

**Interfaces:**
- Consumes: everything; the T3 baseline (the uplift yardstick).
- Produces: the measured class-1 verdict (the milestone's acceptance),
  committed as a re-runnable shard run + merged `.out` (T3 §3.4 machinery).

- [ ] **Step 1: Recursion cap + cap tuning (T5 §5 open items 2, 4)**

From the smoke and a timed sample, set `%mr_max_depth` against
corpus-observed recursion depth (candidate 16), and record whether the
30 s per-integral cap clips the package's own tail (the T3 p95 = 24.2 s
was `integrate`'s; the package's is measured here).

- [ ] **Step 2: Full run, sharded**

Use T3 §3.4's planner rules (partial parts get single-file ranges;
whole-file chains cap at max length; driver-simulation assert before
launch) to build an 18-worker shard plan over all 40 class-1 files /
25,697 entries; run it (≈2.2 h wall on this box); `merge-shards.py`
verifies completeness (25,697/25,697, no dupes/missing/extra).

- [ ] **Step 3: Divergence loop (T4 §4, manual step 3)**

Chase FAILs file-by-file using the corpus-file ≡ Rubi-file key:
misfired rule → fix the rule (predicates or D-duplication in the
generator) and re-run that file's shard; predicate error → fix + re-probe;
zero-chain miss → the strengthen loop `ratsimp → ratsimp∘expand → factor →
ratsimp∘factor` extended only with measured closures (the 23 unverified of
T3's sample are the expected first divergences). Each fix is committed
with its file key and the shard re-run that closed it.

- [ ] **Step 4: Acceptance measurement**

Write `docs/corpus-baseline-uplift.md`: the full-run verdict table
(expected/verified/no-answer/unverified/timeout/error/unexpected), the
uplift against the T3 baseline (12,798 verified/expected, 8,297
no-answer, 3,102 unverified, 1,260 timeout, 240 error, 0 unexpected), the
31/31 non-integrable agreement re-checked, and the per-section table.
Stamped with date + `build_info()`.

- [ ] **Step 5: Commit**

```sh
git add docs/corpus-baseline-uplift.md rules/ maxima_rubi_utils.mac generator/
git commit -m "feat: class-1 full run + divergence loop + measured uplift (milestone-1 acceptance)"
```

---

### Task 10: Milestone close

**Files:**
- Create: `README.md` (install, the API, the MIT notice per T1 §6)
- Modify: `AGENTS.md` (the `## Tests` section now points at the real
  harness — replace "when the test harness exists" with the two-layer
  protocol)
- Create: `handoff/<date>-milestone-1-complete.md`
- Modify: `todo/TODO.md` (record the milestone state; the T5 open
  measurements are now measured — load wall, recursion cap, zero-chain,
  cap)

**Interfaces:**
- Produces: the milestone-1 record a fresh session resumes from.

- [ ] **Step 1: README + license**

`README.md`: what the package is, `load("maxima_rubi.mac")`,
`rubi(f, x)` (antiderivative or the `integrate` noun), `rubi_verbose`,
the class-1 scope, the Rubi MIT copyright notice (T1 §6 — required), the
two-layer test protocol.

- [ ] **Step 2: Update AGENTS.md `## Tests`**

Replace the "when the test harness exists" paragraph with the live
protocol: Layer A `maxima --very-quiet -b test_maxima_rubi.mac` (read the
`Results:` line; no line = failure); Layer B
`python3 test/corpus_class1_driver.py …` (same reading protocol, sharded
per T3 §3.4).

- [ ] **Step 3: Handoff + TODO**

`handoff/<date>-milestone-1-complete.md`: where everything lives, the
measured state (uplift table, load wall, cap values), the open items
(class 2+ as a repeatable process — the generator + loader are the seam;
5.50 re-measurement; the elliptic-answer verification risk, T4 §2), the
known-derived predicate (`%mr_possible_zeroQ`, clone-gap note).
`todo/TODO.md`: T5's open-measurement rows close with their values.

- [ ] **Step 4: Final gate**

Run Layer A: `maxima --very-quiet -b test_maxima_rubi.mac` — read the
`Results:` line. Then code-review the milestone
(`code-review` / `requesting-code-review` skill) before calling it done
(`verification-before-completion`): no FAILs, Results line present,
uplift doc committed.

- [ ] **Step 5: Commit**

```sh
git add README.md AGENTS.md handoff/ todo/
git commit -m "docs: milestone-1 close (README + license, AGENTS tests, handoff, TODO)"
```

---

## Self-review notes (run when the plan is finished, per the skill)

- **Spec coverage:** T5 §1 API → Tasks 2/3; §2 load story → Task 2; §3
  Layer A → Tasks 1/3/4/5/6, Layer B → Tasks 8/9; §4 house rules → Global
  Constraints (all ten, plus the three 2026-08-20 measurements); §5 open
  measurements → Tasks 6 (load wall), 9 (recursion cap, zero-chain, 30 s
  cap). T4 §4 translation procedure → Tasks 4/5/6/7; §6 build drift →
  Task 7 step 2 + Global Constraint 1. T3 §3.4 run machinery → Task 9.
  Design spec §8 done-when: harness ✓, seed class confirmed (T1, 2,710
  rules) ✓, acceptance set = class-1 corpus ✓.
- **Placeholder scan:** the generator (Task 4) is complete code — parser
  reuse, the closed token table, the recursive translator, the Power-
  optional D-duplication, the file/rule emitters, and the loud-failure
  driver; it is developed against 1.1.1.1 first (the Task 4/5 tracer) and
  extended file-by-file in Task 6, each extension covered by that file's
  census row and corpus section. Task 5 step 3 and Task 7 step 1 are
  red-green porting cycles with the sources cited (pinned-clone line
  numbers) — bounded, testable porting instructions, not TBDs. Any other
  "TBD"/"similar to" is a plan failure.
- **Measured subtleties baked in (2026-08-20):** (a) the matcher's
  decomposition fills Plus/Times identity defaults but not the Power-
  optional structural case (`x` ≠ `x^1` match) → the generator
  D-duplicates optional Power exponents; (b) a capture named like the
  integration variable (`x_` with `x_Symbol`) is the pattern argument, not
  a free capture (Mathematica same-named patterns must agree) — 1.1.1.1
  rules 1 and 5 exercise both; (c) `rules` is protected; `?fboundp` does
  not see Maxima functions (witness is a call-check, not an fboundp); a
  quoted symbol nested in a call's arg list is a parse error (block-local
  rebind avoids it); (d) `PossibleZeroQ` is referenced but undefined in
  the pinned clone → derived from usage, flagged.
- **Type consistency:** the rule is a self-contained function
  `r(f, x)` (not a 3-tuple) — consistent across Tasks 2/3/4/6; the table
  name is `mr_rule_table` everywhere (never `rules` — protected); witness
  names `mr_witness_<key>()` are functions everywhere (never values);
  predicate names match `translation_table.py` exactly; the file key is
  the Rubi number with dots stripped (`1_1_1_1`), consistent across
  generator, loader, and tests.
