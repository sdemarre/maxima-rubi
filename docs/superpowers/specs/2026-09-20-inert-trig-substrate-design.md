# Inert-trig substrate — design: the representation Rubi's section-4 rules are written against

Date: 2026-09-20. Designed on branch `master` @ `82627e5` (the class-6
port merged at `2cc114e`, the harness fix `dc0c920`, the bridge probe
`e748095`, the class-4 Step-1 census `82627e5`). Measurements stamped
Maxima `branch_5_50_base_84_g4204fb669` (build date 2026-08-31
13:27:47) / SBCL 2.6.7 / x86_64-pc-linux-gnu — the installed build, per
the AGENTS.md discipline. Reference clones pinned at Rubi
`61e9c18ea248061cd83c67882f7c91a73cef912d` and MaximaSyntaxTestSuite
`60295e21c571ca210ecfbb695f4af99947454adf`. Design brainstorm with the
user 2026-09-20.

## 0. Context

### 0.1 Why this is a substrate question and not a runbook step

The class-4 port (`.scratch/class-ports/issues/05`) follows
`docs/class-porting.md` Steps 1–10 like classes 2, 3 and 6. One thing in
it does not fit that mould: **Rubi's section-4 rules are not written
against `Sin`/`Cos`/`Tan`. They are written against six *inert*
lowercase heads**, and an integrand only reaches them after a conversion
step the port has no equivalent of.

Measured (`probes/rubi/02-hyperbolic-inert-trig-bridge.out`), occurrences
in Rubi's 221 rule files:

| inert head | uses | | active head | inert equivalent |
|---|---:|---|---|---|
| `sin[` | 1518 | | `Sin` | `sin` |
| `csc[` | 940 | | `Csc` | `csc` |
| `tan[` | 640 | | `Tan` | `tan` |
| `cos[` | 551 | | `Cos` | `cos` |
| `sec[` | 225 | | `Sec` | `sec` |
| `cot[` | 133 | | `Cot` | `cot` |

and `sinh[` / `cosh[` / `tanh[` / `coth[` / `sech[` / `csch[`: **0**.
There is no inert hyperbolic head.

Without the inert representation, the `4.7.1`/`4.7.2`/`4.7.3`
normalization files, `4.7.5 Inert trig functions` and every
`sin[…]`-patterned rule are unreachable. This is therefore the first
cluster of the class-4 port, not a tail item.

### 0.2 The bridge, and what it is worth

One rule performs the conversion, at the head of `4.1.0.1 (a sin)^m (b
trg)^n.m`, the first section-4 file `Rubi.m` loads:

```
Int[u_, x_Symbol] := Int[DeactivateTrig[u, x], x] /; FunctionOfTrigOfLinearQ[u, x]
```

`DeactivateTrigAux` (`IntegrationUtilityFunctions.m:6198-6218`) has two
branches. The `TrigQ` branch maps the six active trig heads onto the six
inert ones. The `HyperbolicQ` branch maps the six **hyperbolic** heads
onto the same six inert **trig** heads, by the imaginary-argument
identities, with the argument multiplied by `I`
(`ExpandToSum[I*u[[1]],x]`):

```
Sinh -> -I sin[I z]    Cosh ->    cos[I z]    Tanh -> -I tan[I z]
Coth ->  I cot[I z]    Sech ->    sec[I z]    Csch ->  I csc[I z]
```

So the inert representation is not only how class 4 is reached — it is
how Rubi answers the **class-6** shapes that have no section-6 rule file.
Measured over `test/corpus_class6.out`: the corpus's `6.1.7 … 6.6.7`
family is **1,173 entries, 1,166 of them `deferred` = 36.7 % of class 6's
3,173 deferred, with not one PASS**. Rubi has no `(a + b Sinh[…]^n)^p`
rule in any of its 221 files; the `.7` rule files with inert heads are
`4.1.7` (73 rules), `4.3.7` (25) and `4.5.7` (32), all in section 4.

That is the payoff this substrate buys beyond class 4 itself, and it is
why class 4 was chosen ahead of 5/7/8 (user decision 2026-09-20).

### 0.3 What the census cannot see

Two measured facts that shape the work:

1. **The substrate functions are invisible to a rule-side token scan.**
   Occurrences in the section-4 rule files against
   `IntegrationUtilityFunctions.m`: `ActivateTrig` 129/11,
   `KnownSineIntegrandQ` 22/1, `KnownSecantIntegrandQ` 22/1,
   `InertTrigFreeQ` 10/3, `InertTrigQ` 7/6, `DeactivateTrig` 2/8,
   `FunctionOfTrigOfLinearQ` 2/3, and then **`ReduceInertTrig` 0/39,
   `FixInertTrigFunction` 0/98, `UnifyInertTrigFunction` 0/79**. The last
   three appear nowhere in the rules — they are reachable only *through*
   `DeactivateTrig`. The Step-1 census closure has to run transitively
   through the utilities.
2. **The bridge rules are invisible to the census parser.** Section 4
   carries **7** `If[TrueQ[$LoadShowSteps], …]` wrappers (classes 1/2/3/6
   have 1/0/1/0), which the census does not count and
   `unwrap_showsteps_lines` does recover — so `EXPECTED_TOTAL[4]` is
   **2,080**, not the census's 2,073. All 7 are this substrate and all
   have a bare `u_` LHS: the `4.1.0.1` bridge, plus `4.7.5`'s six
   substitution catch-alls (the two `Tan`/`Cot` `Subst` forms, the two
   `Sin`/`Cos` derivative-divides forms, and the half-angle Weierstrass
   substitution, which runs inside `Block[{$ShowSteps=False, …}]`).

### 0.4 Decisions made in the brainstorm (user, 2026-09-20)

1. **Six distinct `%mr_` operators** for the inert heads — not one tagged
   operator, not Maxima noun forms (section 3.1).
2. **The 136 pattern clauses of `FixInertTrigFunction` /
   `UnifyInertTrigFunction` are GENERATED as rewrite tables**, not
   hand-written and not partially ported (section 3.2).
3. **A second rule list per source file** puts the bare-`u_` records at
   the end of the table — not a separate tail file, not a priority field
   on the record (section 3.3).
4. **The rules activate; tests catch leaks.** No unconditional activation
   at the top of `rubi()` (section 3.4).

### 0.5 Preconditions

- Class 6 merged to `master` with its gates green (`2cc114e`: Layer A
  1066/0, P3 static 15/0, head rewrites 20/0, run-records 43/0, mr-match
  57/0, mr-tree 51/0, dispatch 66/0, byte-identity empty for classes
  1/2/3/6).
- The class-4 Step-1 census committed (`82627e5`).
- `.scratch/corpus-harness/issues/03` is open and NOT a blocker:
  `test_driver_radcan_fallback.py` is red on `master` with stale
  expectations. It guards the verification path, so it should be
  re-pointed before class 4's acceptance record is read, but it does not
  gate this substrate.

## 1. Scope

**In:** the inert representation; the rewrite-table mechanism and the
three tables it serves; the hand-written members of the substrate; the
dispatcher-position change; the answer-side activation and its leak
guard; the tests for all of it.

**Out** — ordinary runbook work once the substrate stands: the other
~2,000 class-4 rules, the `ExpandTrig` / `ExpandTrigReduce` /
`ExpandTrigToExp` family, `TryPureTanSubst`, `KnownSineIntegrandQ` /
`KnownSecantIntegrandQ` / `KnownTangentIntegrandQ` /
`KnownCotangentIntegrandQ`, `FreeFactors` beyond what the substrate
needs, the three new `HEAD_REWRITES` rows (`fresnel_c`, `fresnel_s`,
`hypergeometric`), the Step-8 baseline and Step-9 package runs, and the
acceptance record.

**Explicitly not in scope:** the `AppellF1` ceiling. Measured on this
build, `appell_f1` is a bound noun whose `diff` does not evaluate, so the
823 `AppellF1`-carrying expectations (3.7 % of the section) cannot close
the zero chain whatever the rules do. Same for `HurwitzLerchPhi` (2).
They are a verification ceiling, not a rule-side miss, and the class-3
polylog-ceiling precedent applies
(`.scratch/class3-polylog-ceiling/issues/01`).

## 2. Measured basis

Every claim this design rests on, with the measurement that produced it.

### 2.1 The reader preserves case

`maxima_rubi_match.lisp:74-77`:

```lisp
(defvar *tree-readtable*
  (let ((rt (copy-readtable nil)))
    (setf (readtable-case rt) :preserve)
    rt))
```

So `sin` and `Sin` read as **distinct** symbols in package `:mrs`, and
`mr-tree`'s `*head->op*` is a hash table `:test 'equal` keyed by `(head
. arity)` (`maxima_rubi_tree.lisp:45`), which is case-sensitive on
strings. The inert/active distinction survives reading, matching and
printing with **no change to the matcher**. This is the fact that makes
the whole design cheap.

### 2.2 The tree head table is a three-column list

`maxima_rubi_tree.lisp:22-35`, `+functions+`: rows of `(MathematicaHead
arity MaximaCallName)`, e.g. `("Sin" 1 "sin") ("Sinh" 1 "sinh")`. Six
rows added gives the inert mapping; `function-operator` derives the
Maxima operator symbol by parsing a call, so a `%mr_`-prefixed name
needs no special handling.

### 2.3 `MR-MATCH` already runs on non-`Int` patterns

`maxima_rubi_dispatch.lisp:410-500`: `%mr_matchQ(u, "<pattern>",
[<parts>], cond)` reads, substitutes and prepares an arbitrary pattern,
matches it against `(mr-tree:max->tree u)` and returns the first
complete binding the condition accepts, as a Maxima binding list. It is
used 24 times in the generated rules. The rewrite tables of section 3.2
are this facility plus a replacement step.

### 2.4 The clause shapes of the substrate functions

Measured over `IntegrationUtilityFunctions.m`:

| function | clauses | of which `LHS := RHS /; cond` |
|---|---:|---:|
| `UnifyInertTrigFunction` | 75 | 74 |
| `FixInertTrigFunction` | 61 | 60 |
| `ReduceInertTrig` | 4 | 3 |
| `DeactivateTrigAux` | 1 | 0 (a `Switch` over heads) |
| `ActivateTrig` | 1 | 0 |

136 of the 142 clauses of the big two are exactly the shape the
generator already compiles into a (pattern string, cond function, repl
function) triple. That is why they are generated rather than
hand-written.

### 2.5 A `%mr_i*` operator is genuinely inert

The design's foundation, measured rather than assumed:
`probes/maxima/probe-inert-operator-inertness.{mac,run,out}`,
`Results: 12 passed, 0 failed` on this build.

- `%mr_isin(%pi/2)` parses and `op()` returns `%mr_isin` — a `%`-prefixed
  name is not swallowed by Maxima's `%e`/`%pi`/`%i`/`%o` conventions (the
  package already relies on this for `%mr_linearQ` and the rest).
- `ratsimp` and `expand` leave it untouched, for all six heads.
- The discriminating check: `trigsimp(%mr_isin(x)^2 + %mr_icos(x)^2)`
  returns the sum unchanged, while the control
  `trigsimp(sin(x)^2 + cos(x)^2)` returns `1`.
- Inert and active coexist on their own terms in one expression:
  `sin(%pi/2) + %mr_isin(%pi/2)` simplifies to `%mr_isin(%pi/2) + 1`.
  This is what lets a half-deactivated expression exist while
  `DeactivateTrig` works through it.

Recorded but not asserted: `diff(%mr_isin(x), x)` is an unevaluated
derivative. Harmless, because an inert head never reaches the
verification zero chain (the §3.1 invariant), and the §3.4 guard is what
holds that invariant.

### 2.6 The table is walked in load order

`maxima_rubi.mac:199-225`: `mr_load_all` loads each class's files and
`flatten`s their `mr_rules_<key>` lists onto `mr_rule_table` in
`Rubi.m`'s `LoadRules` order, and the dispatcher walks that list,
stopping at the first rule that answers. Position **is** priority. Probe
21 already measured a rule (`3_5 r37`) unreachable purely because of
class position, and the class-6 close's conclusion 2 records load order
as priority.

## 3. Design

### 3.1 The representation

Six Maxima operators, one per inert head:

```
%mr_isin  %mr_icos  %mr_itan  %mr_icot  %mr_isec  %mr_icsc
```

They are undefined functions — Maxima's simplifier does not touch them,
which is the whole point: `sin(%pi/2)` simplifies to 1 and
`%mr_isin(%pi/2)` does not, so an inert subexpression survives every
`ratsimp` / `expand` the rules perform on it.

Six rows added to `mr-tree`'s `+functions+`:

```lisp
("sin" 1 "%mr_isin") ("cos" 1 "%mr_icos") ("tan" 1 "%mr_itan")
("cot" 1 "%mr_icot") ("sec" 1 "%mr_isec") ("csc" 1 "%mr_icsc")
```

Nothing else in the matcher or the tree changes (section 2.1). A pattern
string `"(Times (Power (|sin| (Pattern …)) …) …)"` now matches a Maxima
expression containing `%mr_isin(…)`, and `tree->max` writes it back.

**The invariant.** An inert head exists only between the bridge rule and
activation. It never appears in a returned answer, in a corpus
expectation, or in a Layer A target's expected value. Section 3.4 makes
that testable rather than aspirational.

**Why not the two alternatives.** A single tagged operator
`%mr_inert(sin, z)` puts the function name in an *argument* position,
which breaks head-variable capture — several rules bind `F_[v_]` over an
inert head and test `InertTrigQ[F]`, and class 6 proved head-position
capture works (including two and three head variables in one pattern,
6.7.6/6.7.7). Maxima's own noun forms are native but can be re-verbed by
`ev`, and their behaviour through the zero chain's `diff`/`ratsimp` is
untested; the `%mr_` operators are inert by construction.

### 3.2 The rewrite-table mechanism

Two new pieces, both small:

**The record.** `%mr_defrewrite(key, n, pattern, cond, repl)`, the
non-`Int` sibling of `%mr_defrule`. Same fields, same load-time pattern
preparation (a pattern the matcher rejects is an error at load, as for
`%mr_defrule`), but the pattern's outermost head is the function name
rather than `Int`, and there is no integrand/variable split.

**The walker.** `%mr_rewrite(table, u, x)` walks `table` in order, and
for the first record whose pattern matches `u` and whose `cond` accepts
the binding, returns `repl`'s value. If no record matches it returns `u`
unchanged — which is Mathematica's own behaviour for a function call
with no applicable definition, and is what the callers rely on.

Each ported function is then a one-line wrapper:

```maxima
%mr_fixInertTrigFunction(u, x) := %mr_rewrite(mr_rw_fitf, u, x)$
```

**Generated, from the same emitter.** `FixInertTrigFunction[csc[v_]^m_.*(c_.*sin[w_])^n_., x] := sin[v]^(-m)*(c*sin[w])^n /; FreeQ[{c,n},x] && IntegerQ[m]`
compiles to a `_mr_cond_…` / `_mr_repl_…` pair and a
`%mr_defrewrite` record exactly as an `Int` rule compiles to a
`%mr_defrule` record. Three tables:

| table | source function | records |
|---|---|---:|
| `mr_rw_uitf` | `UnifyInertTrigFunction` | 75 |
| `mr_rw_fitf` | `FixInertTrigFunction` | 61 |
| `mr_rw_rit` | `ReduceInertTrig` | 4 |

**Recursion.** Many clauses call themselves —
`FixInertTrigFunction[a_*u_,x] := a*FixInertTrigFunction[u,x] /; FreeQ[a,x]`.
This works with no extra machinery: the repl body calls the wrapper,
which re-enters the walk. Termination is Rubi's own (each recursive call
is on a structurally smaller argument); **no depth guard is added**,
because a guard would silently change the answer where Rubi's own
recursion would have terminated. If a non-terminating case is found, it
is a porting defect to fix at the clause, and the existing `%mr_simp`
depth machinery is the precedent for how such a bound would be argued
for separately.

**Hand-written in `maxima_rubi_utils.mac`** — the clauses that are not of
the pattern-rewrite shape, or that are cheaper and clearer as Maxima
code:

- `%mr_deactivateTrigAux(u, x)` — one clause, a `Switch` over the head
  with the two `TrigQ` / `HyperbolicQ` branches. Both branches are
  written out; the hyperbolic one carries the `I`-argument identities of
  section 0.2 verbatim, with the deviation-stamp comment discipline the
  class-6 utilities use.
- `%mr_deactivateTrig(u, x)` — the two-clause wrapper
  (`UnifyInertTrigFunction[FixInertTrigFunction[DeactivateTrigAux[u,x],x],x]`,
  plus the `(c+d x)^m (a+b trig[e+f x])^n` fast clause).
- `%mr_activateTrig(u)` — the inverse map, six heads.
- `%mr_functionOfTrigOfLinearQ(u, x)`, `%mr_functionOfTrig(u, x)`,
  `%mr_freeFactors(u, x)`.
- The predicates `%mr_inertTrigQ`, `%mr_inertTrigFreeQ`, `%mr_trigQ`.

`%mr_hyperbolicQ` already exists and was corrected during the class-6
port (`a975465`); the `HyperbolicQ` branch depends on that fix.

### 3.3 Dispatcher position

The generator emits, for a source file containing bare-`u_` records, a
**second list** beside the ordinary one:

```maxima
mr_rules_4_1_0_1      : [ … the file's ordinary records … ]$
mr_rules_4_1_0_1_tail : [ _mr_rule_4_1_0_1_r1 ]$
```

`mr_load_all` appends every `_tail` list to `mr_rule_table` **after all
classes**, so the 7 catch-alls are the last records the dispatcher
reaches. Mathematica orders them last by pattern specificity; we do it by
position, because position is what our dispatcher has (section 2.6).

`test/check_generated_rules.py` currently asserts one `mr_rules_<key>`
line per generated file; it learns about `_tail` lines, and asserts that
every `_tail` record's pattern is a bare `u_` integrand — so a record
cannot be demoted to the tail by accident, and a bare-`u_` record cannot
be left in the body where it would swallow the table.

**Why not the alternatives.** A separate `rules/class4/4_tail.mac` reads
more clearly but breaks the one-source-`.m`-to-one-output-`.mac` mapping
the P3 gate asserts, widening the gate to buy readability. A priority
field on the record is the most general answer and would serve later
classes, but it changes the dispatcher for all 3,903 existing rules and
turns ordering from something visible in `mr_load_all` into data spread
across 3,900 records.

### 3.4 Answer side and the leak guard

The rules activate. Rubi calls `ActivateTrig` at 129 sites in the
section-4 rules and the generator emits `%mr_activateTrig` at each of
them; there is no global post-pass, so the ported rules stay faithful to
their sources and the P3 byte-identity discipline still applies to their
bodies.

The guard is a test, in two places:

1. **Layer A**: a target asserting that `rubi()`'s answer for a
   representative trig and a representative hyperbolic integrand
   contains no `%mr_i` head.
2. **`test/corpus_driver.py`**: an answer containing a `%mr_i` head is
   classified as an **`error`**, not as a FAIL class. A leak is a porting
   defect — a rule that forgot its activation — and must be loud. A FAIL
   would let thousands of them hide in a `deferred` mass.

Unconditional activation at the top of `rubi()` was considered and
rejected: it cannot leak, but it would mask exactly the defect the guard
exists to find.

### 3.5 What the inert representation does NOT do

It does not make the hyperbolic `.7` entries answer on its own. The chain
is: the bridge rule fires → `DeactivateTrig` produces an inert
expression → a section-4 rule matches it → its repl activates. **Every
link must be ported for one entry to pass**, which is why section 5's
acceptance criterion is an end-to-end one and not a per-function one.

## 4. Phases and gates

Each phase ends green on the gate named; no phase starts before its
predecessor's gate is green.

**P1 — the representation.** The six `%mr_i*` operators and the six
`+functions+` rows. Their inertness is already measured (section 2.5), so
this phase extends that probe to the remaining simplifiers the rules call
and wires the tree rows. Gate: `test/matcher/test_mr_tree.mac` extended with
the round trip `%mr_isin(x)` → tree `sin` → `%mr_isin(x)`, for all six
heads, and a target showing inert and active coexist in one expression
(`sin(x) + %mr_isin(x)` reads as two distinct heads). Green:
`test_mr_tree` at its new count, 0 failed; `test_mr_match` and
`test_mr_dispatch` unchanged.

**P2 — the rewrite mechanism, mechanism only.** `%mr_defrewrite` and
`%mr_rewrite`, tested against a hand-written two-record table — no
generated content yet. Gate: `test_mr_dispatch.mac` extended (a record
that matches, one that does not, a cond that rejects, an unmatched `u`
returned unchanged, a pattern the preparer rejects erroring at load).

**P3 — the generated tables.** The generator learns to emit
`%mr_defrewrite` records from `Name[…] := … /; …` clauses; the three
tables emitted; `%mr_fixInertTrigFunction`,
`%mr_unifyInertTrigFunction`, `%mr_reduceInertTrig` wrapped. Gate:
`python3 test/check_generated_rules.py` green with the new record kind,
regeneration byte-identical (`git status --porcelain rules/` empty), and
Layer A targets per table (a fired clause and a rejected one each).

**P4 — the hand-written members.** `%mr_deactivateTrigAux`,
`%mr_deactivateTrig`, `%mr_activateTrig`, `%mr_functionOfTrigOfLinearQ`,
`%mr_functionOfTrig`, `%mr_freeFactors`, the three predicates. Gate:
Layer A targets per function, including the six hyperbolic identities of
section 0.2 checked individually, and a `deactivateTrig`/`activateTrig`
round trip on a trig and on a hyperbolic integrand.

**P5 — the tail position.** The `_tail` emission, `mr_load_all`'s
append, the P3 gate's `_tail` assertions. Gate: `check_generated_rules.py`
green; a Layer A target showing a bare-`u_` tail record does **not**
answer an integrand an earlier class answers (the regression this
position exists to prevent).

**P6 — the bridge end to end.** The 7 bare-`u_` records ported, the
`4.1.0.1` and `4.7.5` files generated, the core rebuilt. Gate: all of
Layer A, the three matcher suites, the P3 static gate, head rewrites,
run-records — and the acceptance signal of section 5.

## 5. Acceptance criteria

1. Every gate of section 4 green, and the standing per-change gates
   green at the end: Layer A, `test_mr_match`, `test_mr_tree`,
   `test_mr_dispatch`, `check_generated_rules.py`,
   `test_head_rewrites.py`, `test_run_records.py`, byte-identity empty
   for classes 1/2/3/6.
2. **A `6.1.7` entry answers and verifies.** Nothing in the port can
   answer one today (1,166 `deferred`, zero PASS), so a single verified
   entry from that file is proof the whole chain of section 3.5 works.
   The target is taken from
   `reference/maxima-syntax-test-suite/6 Hyperbolic functions/6.1 Hyperbolic sine/6.1.7 hyper^m (a+b sinh^n)^p.mac`
   and added to Layer A.
3. **No class-1/2/3/6 regression.** An `ab_records.py` A/B of a class-6
   slice against `test/corpus_class6.out` on the substrate core, with
   every PASS→FAIL attributed. The full class-6 re-run belongs to the
   class-4 acceptance record, not here.
4. No `%mr_i` head in any answer (section 3.4's two guards green).

## 6. Risks and sharp edges

- **A `%mr_i*` operator that Maxima simplifies in a context this probe
  did not try.** Section 2.5 measured `ratsimp`, `expand` and `trigsimp`
  over all six heads; it did not try every simplifier the rules reach
  (`trigreduce`, `trigexpand`, `exponentialize`, `radcan`, `factor`). If
  one of those does touch an inert head, the head is renamed rather than
  the simplifier avoided. P1's gate extends the probe to whichever
  simplifiers the ported rules actually call.
- **Non-terminating recursion in a rewrite table.** No depth guard by
  decision (section 3.2). The failure mode is a hang, caught by the
  per-entry CPU cap as a `timeout`, which is indistinguishable in a
  record from a slow-but-correct entry. P3's Layer A targets are the
  defence; a table that hangs on a Layer A target fails visibly.
- **The half-angle Weierstrass record's `Block[{$ShowSteps=False, …}]`.**
  It sets Rubi globals the port has no equivalent of. Its port must state
  what it does with them rather than dropping them silently — the
  deviation-stamp discipline of `maxima_rubi_utils.mac`.
- **`I` in the hyperbolic identities.** The bridge multiplies the
  argument by `%i` and the answers carry `%i` factors that must cancel.
  Maxima's handling of complex intermediate forms through `ratsimp` is
  the class-6 lesson repeated (`ratsimp` could not close a hyperbolic
  multiple-angle identity; `exponentialize` first). Expect the same class
  of trap on the verification side and verify numerically before
  editing a failing target.
- **Table growth.** Three rewrite tables plus 2,080 class-4 rules against
  today's 3,903. The class-6 measurement (+11 % table, zero class
  transitions, cpu 0.94x over 80 class-1 entries) is weak evidence at
  this scale; the dispatcher walk is linear and unindexed
  (the `dolist`s at `maxima_rubi_dispatch.lisp:355-365`), so the cost question returns.
  It is not this spec's business — speed is not the current concern
  (user, 2026-09-19) — but the rewrite tables are walked *per call*
  inside `DeactivateTrig`, which is a new inner loop and the first place
  to look if class 4's runs time out.

## 7. Process

Branch `class4-inert-substrate` off `master` @ `6138fce` (this spec's
own commit). Commit per
phase. No `Co-Authored-By` and no `Claude-Session:` trailer; `git add -A`
banned. Push only when the user asks.

The implementation plan follows this spec via the writing-plans skill.

## Amendments (2026-09-21, execution)

Recorded after the plan's ten tasks and the final review's fix wave, on
branch `class4-inert-substrate`. Each entry names the commit that made the
change; the sections above are left as designed.

1. **The tail is EIGHT records, not seven (§0.3, §3.3).** 4.7.5 r72,
   `Int[u_,x_Symbol] := With[{v=ActivateTrig[u]}, CannotIntegrate[v,x]] /;
   Not[InertTrigFreeQ[u]]` (4.7.5.m L76), is Rubi's own last record: an
   integrand the bridge deactivated and nothing finished is given up
   RE-ACTIVATED, so the unintegrable noun carries no inert head. The design's
   seven omitted it. Added in `23855a8`; the tail is 4.1.0.1 r1, then 4.7.5
   r21/r22/r47/r48/r58/r71/r72, r72 last, gated by
   `test/test_rule_table_order.mac`.
2. **Six legacy bare-`u_` records stay in their body lists (§3.3).** §3.3
   says a bare-`u_` record cannot be left in the body. Classes 1/2/3 already
   carry six (`1_4_1` r7/r8, `9_1` r8/r13, `2_3` r96, `3_5` r42); the tail
   convention applies to NEW (class-4) records only, so classes 1/2/3/6 stay
   byte-identical, and the six are a CLOSED, NAMED exception list
   (`BARE_U_BODY_EXCEPTIONS`, generator/generate_rules.py; a seventh fails
   the gate). Commit `4087926`; the faithfulness question is
   `.scratch/class-ports/issues/07-bare-u-records-mid-table.md`.
3. **The rules-core fingerprint hashes `rules/*/*.mac`** (both
   `test/build_rules_core.sh` and the driver's `_core_fingerprint`, one
   sorted order), so a regenerated rewrite table or class-4 file can never
   leave a stale core looking fresh. Commit `49140a9`, guarded by
   `test/test_driver_core_pin.py`.
4. **The real-table ordering gate** `test/test_rule_table_order.mac`
   (outside Layer A, which never calls `mr_load_all`): body handles, then
   the tail, the tail exactly the eight records, r72 its only give-up, every
   bare-`u_` record in the tail or on the exception list. Commit `a05c43d`
   (4 checks), grown to 8 by `34814f4` and `23855a8`.
5. **Utility ports the plan did not list** — each a callee of a ported
   record or clause, brought in with it: the 3-argument `ReduceInertTrig`
   and `PowerOfInertTrigSumQ` (`826e134`); `InertReciprocalQ` (`7b3d58a`);
   `FunctionOfQ`'s circular-trig branches and `SubstFor`'s trig arms /
   `SubstForTrig` (`8c1807a`); `TryPureTanSubst` and `CalculusFreeQ`
   (`978f65b`). Their stamped deviations are in maxima_rubi_utils.mac (the
   Task-9 "DEVIATIONS" header, relabelled in `2b24471`).
6. **Task 7's mixed trig/hyperbolic target was corrected** (plan commit
   `d20d4ac`): `FunctionOfTrigOfLinearQ` of an integrand mixing a trig and
   a hyperbolic head is FALSE in Rubi (a hyperbolic argument is carried as
   `I*u`, and `b/d = -I` fails `RationalQ`) — the reason `DeactivateTrig`
   exists. Measured with `probes/rubi/03-hyperbolic-miscellany-bridge.py`.
7. **Class 4's With/Module locals are prefixed** `_mr_<key>_r<n>_<name>`
   (`de51845`). The 4.7.5 repls ran a nested `mr_int` inside an unprefixed
   `block([d])`, and Maxima's dynamic binding let the local replace the
   integrand's own `d` during the nested integration: `rubi(cos(x)/(d
   sin(x)^7+1), x)` answered with residual 1.08e-3, `sin(x)/(c+d cos(x)^5)`
   2.0e-2 — silently wrong where the port had answered the noun before
   (`probes/maxima/probe-class4-with-capture.out`, sections A and E). The
   renaming is a pure alpha-renaming of the emitted text, class 4 only;
   classes 1/2/3/6 carry the same exposure and are ticketed
   (`.scratch/class-ports/issues/08-generator-unprefixed-with-locals.md`,
   with the class-free mechanism in `mr_sum`, probe sections C and D).
8. **Corpus outcome** (queue runner, 12 workers, 30 s cpu cap, rules core
   `3d08a28a…`, 2026-09-21, build `branch_5_50_base_84_g4204fb669`; A/B by
   `python3 test/ab_records.py <accepted> <new>`):

   | class | accepted PASS | branch PASS | PASS→FAIL | FAIL→PASS | record |
   |---|---|---|---|---|---|
   | 2 | 707 | 708 | 0 | 1 | `test/corpus_class2.inert-substrate.out` |
   | 3 | 1,657 | 1,673 | 0 | 16 | `test/corpus_class3.inert-substrate.out` |
   | 6 | 739 | **1,636** | 23 | 920 | `test/corpus_class6.inert-substrate.out` |

   Class 6's 23 PASS→FAIL: 22 `no-answer → contains-noun`, the
   `c*'unintegrable[g,x]` form the driver does not read as a no-answer
   (`.scratch/corpus-harness/issues/04-noun-times-constant-no-answer.md`),
   and 6.5.3 e151 `verified → timeout` at the cap (29.8 s → 30.0 s). The
   named records do not replace the accepted `test/corpus_class{2,3,6}.out`;
   that is the acceptance decision.
   **Accepted 2026-09-21 (user decision):** the three named records were
   promoted byte-for-byte to `test/corpus_class{2,3,6}.out` (classes 2/3/6
   now 708 / 1,673 / 1,636); the named copies are kept as the citations
   above.
