# Inert-trig substrate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the inert trig representation Rubi's section-4 rules are written against, so that class 4 can be ported at all and the 1,166 `deferred` class-6 `.7` entries become reachable.

**Architecture:** Six undefined Maxima operators `%mr_isin` … `%mr_icsc` carry Rubi's six inert lowercase trig heads; six rows in `mr-tree`'s `+functions+` map them to the tree heads `sin` … `csc`, which the pattern reader already keeps distinct from the active `Sin` … `Csc` because its readtable case is `:preserve`. A new `%mr_defrewrite` record plus a `%mr_rewrite` walker turn Rubi's `Name[pattern] := rhs /; cond` utility clauses into generated rewrite tables, reusing the emitter that already compiles `Int` rules. The bare-`u_` bridge rules go into a second per-file rule list that `mr_load_all` appends after every class, so they sit last in the dispatcher's linear walk.

**Tech Stack:** Maxima 5.50 (`branch_5_50_base_84_g4204fb669`) on SBCL 2.6.7; Common Lisp for `maxima_rubi_{match,tree,dispatch}.lisp`; Maxima for `maxima_rubi_utils.mac` and the generated rule files; Python 3 for `generator/generate_rules.py` and the static gates.

**Spec:** `docs/superpowers/specs/2026-09-20-inert-trig-substrate-design.md`

## Global Constraints

- Branch `class4-inert-substrate` off `master` @ `6138fce`. Commit per task. Push only when the user asks.
- **No `Co-Authored-By` trailer and no `Claude-Session:` trailer** on any commit. `git add -A` is banned — stage named paths.
- Every test run ends with `Results: <n> passed, <m> failed`. **Read that line.** A run that dies mid-way prints no `Results:` line at all, which is itself a failure.
- No TLS flag is needed (`--tls-limit` is historical). If a change ever compiles or translates the rule files, re-run `probes/matcher/08-runtime-load` and restore the flag rule.
- Maxima **nests** block comments: a glob path inside one (a directory name followed by slash-star) opens a comment that never closes and the run prints no `Results:` line. Never put a `*.mac` glob inside a `/* */`.
- `ratsimp` cannot close a hyperbolic multiple-angle identity — it treats `sinh(3*x)` and `sinh(x)` as unrelated atoms. Go through `exponentialize` first, and verify numerically before editing a target that fails.
- Every non-trivial claim in a `docs/` file cites a committed, re-runnable probe under `probes/`.
- Counts and timings are stamped with the date and `build_info()` (`version` is unbound in this build).
- Any exploratory `test/corpus_driver.py` slice **must** be given an out-file positional, and a non-class-1 section **must** be given the suite-dir positional (`FILTER PER_FILE TIMEOUT SUITE_DIR`) or `file_list()` silently resolves 0 files.

**Standing gates** — green before a task's commit is considered done:

```sh
maxima --very-quiet -b test_maxima_rubi.mac                     # Layer A
maxima --very-quiet -b test/matcher/test_mr_match.mac           # 57 passed, 0 failed
maxima --very-quiet -b test/matcher/test_mr_tree.mac            # 51 passed, 0 failed
maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null   # 66 passed, 0 failed
python3 test/check_generated_rules.py                           # 15 passed, 0 failed
python3 test/test_head_rewrites.py                              # 20 passed, 0 failed
python3 test/test_run_records.py                                # 43 passed, 0 failed
```

Layer A is `1066 passed, 0 failed` at `6138fce`; counts rise as tasks add targets, and each task states its own expected count. The three matcher suites and the three Python gates keep their counts unless a task says otherwise.

**Known-red, not a blocker:** `python3 test/test_driver_radcan_fallback.py` is `2 passed, 2 failed` on `master` with stale expectations (`.scratch/corpus-harness/issues/03`). Do not "fix" it in this plan and do not let it block a commit.

**Spec amendment this plan makes:** spec §1 lists `TryPureTanSubst` as out of scope, but the half-angle Weierstrass record — one of the seven tail records §0.3 requires — calls it. Task 10 brings `TryPureTanSubst` and `SubstFor` in scope for that one record. Everything else in §1's out-list stays out.

## File Structure

**Modified:**

- `maxima_rubi_tree.lisp` — `+functions+` gains six rows. Responsibility unchanged: the Maxima↔tree head map.
- `maxima_rubi_dispatch.lisp` — gains the rewrite record kind and its walker, beside the existing `Int` rule record. Responsibility unchanged: records, dispatch, and the Maxima-facing entry points.
- `maxima_rubi_utils.mac` — gains the hand-written members of the substrate. Already 5,591 lines; this plan adds to it rather than splitting it, because every ported predicate in the project lives there and splitting it is not this plan's job.
- `maxima_rubi.mac` — `mr_load_all` loads the rewrite tables and appends the `_tail` lists after every class.
- `generator/generate_rules.py` — learns to emit `%mr_defrewrite` records from utility-function clauses, and `_tail` lists for bare-`u_` records.
- `test/check_generated_rules.py` — learns about rewrite files and `_tail` lists.
- `test/corpus_driver.py` — the `%mr_i` leak guard.
- `test_maxima_rubi.mac`, `test/matcher/test_mr_tree.lisp`, `test/matcher/test_mr_dispatch.lisp` — targets.
- `probes/maxima/probe-inert-operator-inertness.mac` — extended to the remaining simplifiers.

**Created:**

- `rules/utils/inert_trig_rewrites.mac` — GENERATED. The three rewrite tables (`mr_rw_uitf`, `mr_rw_fitf`, `mr_rw_rit`) from `IntegrationUtilityFunctions.m`. One source file, one output file, as for every rule file.
- `rules/class4/4_1_0_1.mac`, `rules/class4/4_7_5.mac` — GENERATED. Only the bare-`u_` bridge records in this plan; the rest of those files' rules belong to the class-4 port proper.

---

### Task 1: Prove the six operator names survive every simplifier the rules call

The design's foundation is that `%mr_i*` operators are inert. `probes/maxima/probe-inert-operator-inertness` already measured `ratsimp`, `expand` and `trigsimp` (12/0, spec §2.5). The rules also call `trigreduce`, `trigexpand`, `exponentialize`, `radcan` and `factor`. Measure those **before** anything depends on the names, because a failure here means a rename, and a rename after Task 4 touches generated files.

**Files:**
- Modify: `probes/maxima/probe-inert-operator-inertness.mac`
- Regenerate: `probes/maxima/probe-inert-operator-inertness.out`

**Interfaces:**
- Consumes: nothing.
- Produces: the measured fact that `%mr_isin` … `%mr_icsc` are inert under `ratsimp`, `expand`, `trigsimp`, `trigreduce`, `trigexpand`, `exponentialize`, `radcan` and `factor`. Every later task depends on these six names.

- [ ] **Step 1: Add the failing checks**

Insert before the `print("========================================")$` line:

```maxima
/* The simplifiers the ported rules actually call. trigreduce/trigexpand and
 * exponentialize are the class-6 workhorses (maxima_rubi_utils.mac stamps two
 * deviations against them); radcan and factor appear in the zero chain and in
 * %mr_simp. An inert head must come back untouched from all of them. */
for f in ['%mr_isin, '%mr_icos, '%mr_itan, '%mr_icot, '%mr_isec, '%mr_icsc] do (
  check(concat("trigreduce keeps ", f), trigreduce(apply(f, [x])), apply(f, [x])),
  check(concat("trigexpand keeps ", f), trigexpand(apply(f, [x])), apply(f, [x])),
  check(concat("exponentialize keeps ", f), exponentialize(apply(f, [x])), apply(f, [x])),
  check(concat("radcan keeps ", f), radcan(apply(f, [x])), apply(f, [x])),
  check(concat("factor keeps ", f), factor(apply(f, [x])), apply(f, [x])))$

/* The discriminating pair again, for the multiple-angle simplifier: trigreduce
 * rewrites sin(x)^2 and must not touch the inert square. */
check("trigreduce does NOT reduce the inert square",
      trigreduce(%mr_isin(x)^2), %mr_isin(x)^2)$
check("trigreduce DOES reduce the active square (control)",
      trigreduce(sin(x)^2), (1 - cos(2*x))/2)$
```

- [ ] **Step 2: Run the probe and read the count**

```sh
sh probes/maxima/probe-inert-operator-inertness.run
grep -E "^(PASS|FAIL|Results)" probes/maxima/probe-inert-operator-inertness.out
```

Expected: `Results: 44 passed, 0 failed` (the existing 12 plus 30 loop checks plus 2 trigreduce checks).

**If any head FAILS**, stop and report before continuing: the name is not inert and the six names must change. `%mr_trigsin` … is the fallback set. Every later task in this plan names the six operators, so a rename is a plan edit, not a code patch.

The `trigreduce DOES reduce the active square` control may need its expected value adjusted to whatever this build actually returns — run `trigreduce(sin(x)^2);` once and use that exact form. The control exists to prove `trigreduce` is doing something, so it must assert the real value, not a guess.

- [ ] **Step 3: Commit**

```sh
git add probes/maxima/probe-inert-operator-inertness.mac probes/maxima/probe-inert-operator-inertness.out
git commit -m "probe: the %mr_i heads survive every simplifier the rules call

Extends the inertness probe from ratsimp/expand/trigsimp to trigreduce,
trigexpand, exponentialize, radcan and factor over all six heads, plus the
trigreduce multiple-angle control. Measured before anything depends on the
names, because a failure here is a rename.

Results: 44 passed, 0 failed."
```

---

### Task 2: The six inert heads in the tree

**Files:**
- Modify: `maxima_rubi_tree.lisp:22-35` (`+functions+`)
- Test: `test/matcher/test_mr_tree.lisp`

**Interfaces:**
- Consumes: the six operator names from Task 1.
- Produces: `%mr_isin(z)` ↔ tree `(sin z)`, and the same for `cos`/`tan`/`cot`/`sec`/`csc`. Tasks 3–10 rely on patterns containing lowercase tree heads matching Maxima expressions containing `%mr_i*`.

- [ ] **Step 1: Write the failing tests**

In `test/matcher/test_mr_tree.lisp`, following the file's existing target style (read a neighbouring target first and match it — the file has its own `check`-equivalent and its own naming):

```lisp
;; The inert trig heads (inert-trig substrate design 3.1). Rubi's section-4
;; rules pattern on the LOWERCASE heads; these are the Maxima operators that
;; carry them. The active heads must stay untouched: the reader's readtable
;; case is :preserve, so sin and Sin are different symbols.
(check-round-trip "inert sin" "%mr_isin(x)" '(|sin| |x|))
(check-round-trip "inert cos" "%mr_icos(x)" '(|cos| |x|))
(check-round-trip "inert tan" "%mr_itan(x)" '(|tan| |x|))
(check-round-trip "inert cot" "%mr_icot(x)" '(|cot| |x|))
(check-round-trip "inert sec" "%mr_isec(x)" '(|sec| |x|))
(check-round-trip "inert csc" "%mr_icsc(x)" '(|csc| |x|))
;; Inert and active in ONE expression, as a half-deactivated integrand is.
(check-round-trip "inert and active coexist" "sin(x) + %mr_isin(x)"
                  '(|Plus| (|Sin| |x|) (|sin| |x|)))
```

`check-round-trip` is illustrative: use whatever the file's existing helper is called, with its argument order, and keep the `'(|sin| |x|)` tree shape in the form the file's other targets use (read two existing targets before writing these).

- [ ] **Step 2: Run to verify they fail**

```sh
maxima --very-quiet -b test/matcher/test_mr_tree.mac
```

Expected: `Results: 51 passed, 7 failed` — the seven new targets fail because `%mr_isin` is not in the head table, so it reads as the default `MX_…` head rather than `sin`.

- [ ] **Step 3: Add the six rows**

In `maxima_rubi_tree.lisp`, append to `+functions+` (keep the existing rows untouched):

```lisp
    ;; Rubi's six INERT trig heads (inert-trig substrate design 3.1). The
    ;; Maxima side is an undefined operator, so the simplifier leaves it alone
    ;; (probes/maxima/probe-inert-operator-inertness, 44/0); the tree side is
    ;; the lowercase head section 4's rules pattern on. sin and Sin stay
    ;; distinct because read-tree's readtable case is :preserve.
    ("sin" 1 "%mr_isin") ("cos" 1 "%mr_icos") ("tan" 1 "%mr_itan")
    ("cot" 1 "%mr_icot") ("sec" 1 "%mr_isec") ("csc" 1 "%mr_icsc")
```

- [ ] **Step 4: Run to verify they pass**

```sh
maxima --very-quiet -b test/matcher/test_mr_tree.mac
maxima --very-quiet -b test/matcher/test_mr_match.mac
maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null
maxima --very-quiet -b test_maxima_rubi.mac
```

Expected: mr-tree `58 passed, 0 failed`; mr-match `57 passed, 0 failed`; dispatch `66 passed, 0 failed`; Layer A `1066 passed, 0 failed`.

`mr-head-verb` builds its table from `head-table` with "the smallest arity wins" — all six new rows are arity 1 and no existing head is named `sin`/`cos`/…, so no existing mapping changes. If Layer A or the matcher suites move at all, stop: something collided.

- [ ] **Step 5: Commit**

```sh
git add maxima_rubi_tree.lisp test/matcher/test_mr_tree.lisp
git commit -m "tree: the six inert trig heads

%mr_isin … %mr_icsc <-> the lowercase tree heads sin … csc that Rubi's
section-4 rules pattern on. Six rows in +functions+ and nothing else: the
pattern reader's readtable case is :preserve, so sin and Sin are distinct
symbols and the active heads are untouched.

test_mr_tree 51 -> 58 passed, 0 failed; mr-match 57/0, dispatch 66/0 and
Layer A 1066/0 unchanged."
```

---

### Task 3: The rewrite record and its walker

**Files:**
- Modify: `maxima_rubi_dispatch.lisp` (after the `Int` rule records, around line 175)
- Test: `test/matcher/test_mr_dispatch.lisp`

**Interfaces:**
- Consumes: `mr-match:prepare`, `mr-match:read-tree`, `mr-match:match` (`(compiled expr &key bindings cond-hook)` → `(values alist matchedp)`, cond-hook truthy accepts), `mr-binding-list`, `mr-call`, `mr-true-p`, `mr-guarded`, `with-mr-switches`, `mr-tree:max->tree`, `mr-match:sym`.
- Produces, for Tasks 4–10:
  - `%mr_defrewrite(key, n, pattern, cond, repl)` → integer handle. `pattern` is a Mathematica-syntax s-expression string whose outermost head is the utility function's name; `cond` is `true` or a Maxima function of `(mm, x)`; `repl` is a Maxima function of `(mm, x)`.
  - `%mr_rewrite(head, table, u, x)` → the first accepted record's replacement, or `u` unchanged. `head` is the function-name string, `table` a Maxima list of handles.

- [ ] **Step 1: Write the failing tests**

In `test/matcher/test_mr_dispatch.lisp`, following its existing target style:

```lisp
;; Rewrite records (inert-trig substrate design 3.2): the non-Int sibling of
;; %mr_defrule. Five behaviours, on a hand-written two-record table — no
;; generated content, no rule files.
;;
;; Table (in order):
;;   r1  F[a_*u_, x] := 99            /; FreeQ[a, x]
;;   r2  F[u_, x]    := 7
;;
;; so F[3*y, y] takes r1 (a=3 is free of y), F[y, y] falls to r2, and a cond
;; that rejects must not stop the walk.
(mr-dispatch-test-maxima "
  _mr_cond_t3_r1(mm, x) := freeof(x, geteqR(mm, '_mr_t3_r1_a))$
  _mr_repl_t3_r1(mm, x) := 99$
  _mr_cond_t3_r2(mm, x) := true$
  _mr_repl_t3_r2(mm, x) := 7$
  h1 : %mr_defrewrite(\"t3\", 1,
    \"(F (Times (Pattern |_mr_t3_r1_a| (Blank)) (Pattern |_mr_t3_r1_u| (Blank))) (Pattern x (Blank)))\",
    _mr_cond_t3_r1, _mr_repl_t3_r1)$
  h2 : %mr_defrewrite(\"t3\", 2,
    \"(F (Pattern |_mr_t3_r2_u| (Blank)) (Pattern x (Blank)))\",
    _mr_cond_t3_r2, _mr_repl_t3_r2)$
  tbl : [h1, h2]$")

(check-eq "rewrite: first record fires"      "%mr_rewrite(\"F\", tbl, 3*y, y)" 99)
(check-eq "rewrite: falls through to second" "%mr_rewrite(\"F\", tbl, y, y)"    7)
(check-eq "rewrite: cond rejects, walk continues"
          ;; a*u with a NOT free of x: r1's cond rejects, r2 answers
          "%mr_rewrite(\"F\", tbl, y*z, y)" 7)
(check-eq "rewrite: no record matches -> u unchanged"
          ;; a one-record table whose pattern cannot bind
          "%mr_rewrite(\"G\", [h1], y, y)" "y")
(check-error "rewrite: a pattern the preparer rejects errors at load"
             "%mr_defrewrite(\"t3\", 3, \"(F (Blank\", true, _mr_repl_t3_r2)")
```

`mr-dispatch-test-maxima`, `check-eq` and `check-error` are illustrative: use the file's real helpers with their real signatures (read three existing targets first). The five behaviours are what must be asserted, whatever the helpers are called.

- [ ] **Step 2: Run to verify they fail**

```sh
maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null
```

Expected: `Results: 66 passed, 5 failed`, the failures naming `%mr_defrewrite` as an undefined function.

- [ ] **Step 3: Implement the record and the walker**

In `maxima_rubi_dispatch.lisp`, after `mr-rule-of` (around line 175):

```lisp
;;; ------------------------------------------------------------------
;;; Rewrite records (inert-trig substrate design 3.2)
;;;
;;; %mr_defrewrite(key, n, pattern, cond, repl) is %mr_defrule's sibling for
;;; Rubi's utility functions whose clauses are `Name[pattern] := rhs /; cond`
;;; -- 136 of the 142 clauses of FixInertTrigFunction and
;;; UnifyInertTrigFunction are of exactly that shape. The pattern's outermost
;;; head is the function name rather than Int, and there is no
;;; integrand/variable split, so there is no mr-accept and no pre-binding.

(defstruct (mr-rewrite (:constructor make-mr-rewrite (key n pattern cond repl)))
  key n pattern cond repl)

(defvar *mr-rewrites* (make-array 256 :adjustable t :fill-pointer 0)
  "Every rewrite record %mr_defrewrite registered, in load order.")

(defmfun |$%MR_DEFREWRITE| (&rest args)
  (unless (= (length args) 5)
    (merror (intl:gettext "%mr_defrewrite: expected 5 args, found ~A")
            (length args)))
  (destructuring-bind (key n pattern cond repl) args
    (let ((compiled (handler-case (mr-match:prepare (mr-match:read-tree pattern))
                      (error (e)
                        (merror (intl:gettext "%mr_defrewrite: ~A r~A: ~A") key n
                                (princ-to-string e))))))
      (vector-push-extend (make-mr-rewrite key n compiled cond repl) *mr-rewrites*)
      (fill-pointer *mr-rewrites*))))

(defun mr-rewrite-of (handle)
  (if (and (integerp handle) (<= 1 handle (fill-pointer *mr-rewrites*)))
      (aref *mr-rewrites* (1- handle))
      (merror (intl:gettext "%mr_rewrite: not a rewrite handle: ~M") handle)))

(defmfun |$%MR_REWRITE| (head table u x)
  "Walk TABLE (a Maxima list of %mr_defrewrite handles) in order; the first
record whose pattern binds (HEAD u x) and whose cond accepts answers with its
repl's value. U unchanged when none does -- Mathematica's own behaviour for a
call with no applicable definition, which is what the callers rely on."
  (let ((expr (list (mr-match:sym head)
                    (mr-tree:max->tree u)
                    (mr-tree:max->tree x))))
    (with-mr-switches
      (dolist (h (cdr table) u)
        (let* ((rw (mr-rewrite-of h))
               (cond-fn (mr-rewrite-cond rw))
               (accepted nil))
          (mr-guarded (setf accepted nil)
            (mr-match:match
             (mr-rewrite-pattern rw) expr
             :cond-hook (lambda (b)
                          (let ((mb (mr-binding-list b nil)))
                            (when (or (eq cond-fn t)
                                      (multiple-value-bind (v ok)
                                          (mr-call cond-fn mb x)
                                        (and ok (mr-true-p v))))
                              (setf accepted mb))))))
          (when accepted
            (multiple-value-bind (r ok) (mr-call (mr-rewrite-repl rw) accepted x)
              (when (and ok r)
                (return r)))))))))
```

Two things to note while implementing:

- The cond-hook must return truthy for `match` to accept and stop; setting `accepted` and returning it does both, because a non-nil Maxima list is truthy in Lisp.
- `mr-guarded` around the match is what `mr-matchq` does (`maxima_rubi_dispatch.lisp:476-500`) — a fault in a cond makes the record not match rather than killing the process. Read that function before writing this one; it is the closest existing model.

- [ ] **Step 4: Run to verify they pass**

```sh
maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null
maxima --very-quiet -b test/matcher/test_mr_match.mac
maxima --very-quiet -b test/matcher/test_mr_tree.mac
maxima --very-quiet -b test_maxima_rubi.mac
```

Expected: dispatch `71 passed, 0 failed`; mr-match `57/0`; mr-tree `58/0`; Layer A `1066/0`.

- [ ] **Step 5: Commit**

```sh
git add maxima_rubi_dispatch.lisp test/matcher/test_mr_dispatch.lisp
git commit -m "dispatch: rewrite records, the non-Int sibling of %mr_defrule

%mr_defrewrite(key, n, pattern, cond, repl) prepares its pattern at load as
%mr_defrule does, and %mr_rewrite(head, table, u, x) walks a table in order and
answers with the first record whose pattern binds (head u x) and whose cond
accepts -- u unchanged when none does, which is Mathematica's behaviour for a
call with no applicable definition.

136 of the 142 clauses of FixInertTrigFunction and UnifyInertTrigFunction are
Name[pattern] := rhs /; cond, so they compile through the emitter that already
handles Int rules. Tested on a hand-written two-record table: first record
fires, fall-through, a rejecting cond does not stop the walk, no match returns u
unchanged, and a pattern the preparer rejects errors at load.

test_mr_dispatch 66 -> 71 passed, 0 failed."
```

---

### Task 4: Generate the three rewrite tables

**Files:**
- Modify: `generator/generate_rules.py`
- Create: `rules/utils/inert_trig_rewrites.mac` (generated)
- Modify: `maxima_rubi.mac` (load the file in `mr_load_all`)
- Modify: `maxima_rubi_utils.mac` (the three wrappers)
- Modify: `test/check_generated_rules.py`
- Test: `test_maxima_rubi.mac`

**Interfaces:**
- Consumes: `%mr_defrewrite` / `%mr_rewrite` from Task 3; the inert heads from Task 2.
- Produces: `%mr_unifyInertTrigFunction(u, x)`, `%mr_fixInertTrigFunction(u, x)`, `%mr_reduceInertTrig(f, v)` — each returning a rewritten expression or its input unchanged. Task 6 calls all three.

**Source:** `reference/rubi/Rubi/IntegrationUtilityFunctions.m`, the clauses of `UnifyInertTrigFunction` (75), `FixInertTrigFunction` (61) and `ReduceInertTrig` (4). Counts measured 2026-09-20; the generator asserts them, so a reference-clone change is a loud failure.

- [ ] **Step 1: Write the failing Layer A tests**

In `test_maxima_rubi.mac`, in a new section. Take the expected values from the `.m` clauses themselves, not from running the code:

```maxima
/* Inert-trig rewrite tables (inert-trig substrate design 3.2). One fired
 * clause and one non-matching input per table, so a table that loads empty
 * or matches everything both fail.
 *
 * FixInertTrigFunction[csc[v_]^m_.*(c_.*sin[w_])^n_., x] :=
 *     sin[v]^(-m)*(c*sin[w])^n /; FreeQ[{c,n},x] && IntegerQ[m]
 * so csc(x)^2*sin(x) -> sin(x)^(-2)*sin(x), with INERT heads throughout. */
check("fitf: csc^m (c sin)^n clause fires",
      %mr_fixInertTrigFunction(%mr_icsc(x)^2 * %mr_isin(x), x),
      %mr_isin(x)^(-2) * %mr_isin(x)),
/* FixInertTrigFunction[a_*u_, x] := a*FixInertTrigFunction[u,x] /; FreeQ[a,x]
 * is the self-recursive clause: the constant comes out and the walk re-enters. */
check("fitf: free factor comes out, recursion re-enters",
      %mr_fixInertTrigFunction(3 * %mr_icsc(x)^2 * %mr_isin(x), x),
      3 * %mr_isin(x)^(-2) * %mr_isin(x)),
check("fitf: an expression no clause matches is returned unchanged",
      %mr_fixInertTrigFunction(log(x), x), log(x)),
check("uitf: an expression no clause matches is returned unchanged",
      %mr_unifyInertTrigFunction(log(x), x), log(x)),
check_bool("uitf table is not empty", is(length(mr_rw_uitf) = 75)),
check_bool("fitf table is not empty", is(length(mr_rw_fitf) = 61)),
check_bool("rit table is not empty", is(length(mr_rw_rit) = 4)),
```

The two `fitf` expected values must be checked against the `.m` clause text before being written down, and the clause that actually fires must be confirmed to be the first matching one in source order — an earlier clause may claim the input. If a different clause fires, the expected value changes, not the code. Read the file's clauses in order and pick inputs that unambiguously reach the clause under test.

- [ ] **Step 2: Run to verify they fail**

```sh
maxima --very-quiet -b test_maxima_rubi.mac
```

Expected: `Results: 1066 passed, 7 failed`, the failures naming `%mr_fixInertTrigFunction` as undefined.

- [ ] **Step 3: Teach the generator to emit rewrite records**

In `generator/generate_rules.py`: a new emitter entry point that reads named function clauses out of `IntegrationUtilityFunctions.m` and emits `%mr_defrewrite` records with the **same** cond/repl body emitter the `Int` rules use. Reuse, do not copy: the body translation is the part that must not fork, because the P3 gate's whole value is that rule bodies are byte-stable.

Shape of the generated file:

```maxima
/* rules/utils/inert_trig_rewrites.mac — GENERATED; do not edit.
 * Source: Rubi 4 61e9c18ea248061cd83c67882f7c91a73cef912d
 *          Rubi/IntegrationUtilityFunctions.m
 * Regenerate: python3 generator/generate_rules.py --rewrites */

_mr_cond_uitf_r1(mm, x) := block([...], ...)$
_mr_repl_uitf_r1(mm, x) := block([...], ...)$
_mr_rw_uitf_r1 : %mr_defrewrite("uitf", 1, "(UnifyInertTrigFunction ...)", _mr_cond_uitf_r1, _mr_repl_uitf_r1)$
...
mr_rw_uitf : [ _mr_rw_uitf_r1, ... ]$
mr_rw_count_uitf : 75$
mr_rw_fitf : [ ... ]$
mr_rw_count_fitf : 61$
mr_rw_rit : [ ... ]$
mr_rw_count_rit : 4$
mr_witness_inert_trig_rewrites() := true$
```

Assert the three clause counts in the generator and fail generation if the source yields a different number — the counts are the guard that a reference-clone bump does not silently drop clauses.

- [ ] **Step 4: Generate, and add the three wrappers**

```sh
python3 generator/generate_rules.py --rewrites
```

In `maxima_rubi_utils.mac`:

```maxima
/* Rubi's inert-trig rewrite functions, ported as generated rewrite tables
   (inert-trig substrate design 3.2): 136 of their 142 clauses are
   Name[pattern] := rhs /; cond, so they compile through the same emitter as
   an Int rule instead of being hand-written. The tables live in
   rules/utils/inert_trig_rewrites.mac. Recursion is Rubi's own — a clause
   that calls itself re-enters through these wrappers, and there is no depth
   guard by design decision (spec 3.2). */
%mr_unifyInertTrigFunction(u, x) :=
  %mr_rewrite("UnifyInertTrigFunction", mr_rw_uitf, u, x)$
%mr_fixInertTrigFunction(u, x) :=
  %mr_rewrite("FixInertTrigFunction", mr_rw_fitf, u, x)$
%mr_reduceInertTrig(f, v) :=
  %mr_rewrite("ReduceInertTrig", mr_rw_rit, f, v)$
```

In `maxima_rubi.mac`'s `mr_load_all`, load the file **before** the class rule files, since nothing in it is an `Int` rule and the utilities must exist before a rule body calls them:

```maxima
  %mr_load_sibling("rules/utils/inert_trig_rewrites.mac",
                   'mr_witness_inert_trig_rewrites),
```

- [ ] **Step 5: Run to verify they pass**

```sh
maxima --very-quiet -b test_maxima_rubi.mac
```

Expected: `Results: 1073 passed, 0 failed`.

- [ ] **Step 6: Extend the static gate**

In `test/check_generated_rules.py`: the rewrite file is checked like a rule file — the three `mr_rw_<key>` lines present, the three counts matching `mr_rw_count_<key>`, no `defmatch`, every pattern string preparing in `MR-MATCH`, and regeneration byte-identical.

```sh
python3 test/check_generated_rules.py
python3 generator/generate_rules.py --rewrites && git status --porcelain rules/
```

Expected: the gate green at its new count with the rewrite checks added, and `git status --porcelain rules/` **empty**.

- [ ] **Step 7: Commit**

```sh
git add generator/generate_rules.py rules/utils/inert_trig_rewrites.mac \
        maxima_rubi.mac maxima_rubi_utils.mac test/check_generated_rules.py \
        test_maxima_rubi.mac
git commit -m "generate: the three inert-trig rewrite tables

UnifyInertTrigFunction (75 clauses), FixInertTrigFunction (61) and
ReduceInertTrig (4) emitted as %mr_defrewrite records from
IntegrationUtilityFunctions.m, through the same cond/repl body emitter the Int
rules use -- so the P3 byte-identity discipline covers them and they cannot
drift from their source. The generator asserts all three clause counts, so a
reference-clone bump that drops a clause fails generation.

Three one-line wrappers in maxima_rubi_utils.mac; the table file loads before
the class rule files. Recursion is Rubi's own and there is no depth guard, by
the spec's decision.

Layer A 1066 -> 1073 passed, 0 failed; check_generated_rules.py green with the
rewrite checks; regeneration byte-identical."
```

---

### Task 5: `ActivateTrig` and the inert predicates

The smaller hand-written half of the substrate, and the half the leak guard depends on. Done before `DeactivateTrig` so that Task 6 can assert a round trip.

**Files:**
- Modify: `maxima_rubi_utils.mac`
- Test: `test_maxima_rubi.mac`

**Interfaces:**
- Consumes: the inert heads from Task 2.
- Produces: `%mr_activateTrig(u)`, `%mr_inertTrigQ(f)`, `%mr_inertTrigFreeQ(u)`, `%mr_trigQ(f)`. Tasks 6, 9 and 10 use all four.

Rubi's definitions, for reference while porting:

```
InertTrigQ[f_] := MemberQ[{sin,cos,tan,cot,sec,csc},f]                    (L6160)
InertTrigFreeQ[u_] := FreeQ[u,sin] && FreeQ[u,cos] && ... && FreeQ[u,csc] (L6173)
ActivateTrig[u_] := ...                                                   (L6180)
```

- [ ] **Step 1: Write the failing tests**

```maxima
/* ActivateTrig and the inert predicates (inert-trig substrate design 3.2).
 * %mr_activateTrig is the inverse of the head map of design 3.1. */
check("activateTrig: one head", %mr_activateTrig(%mr_isin(x)), sin(x)),
check("activateTrig: all six",
      %mr_activateTrig(%mr_isin(x) + %mr_icos(x) + %mr_itan(x)
                       + %mr_icot(x) + %mr_isec(x) + %mr_icsc(x)),
      sin(x) + cos(x) + tan(x) + cot(x) + sec(x) + csc(x)),
check("activateTrig: nested, and leaves the rest alone",
      %mr_activateTrig(log(%mr_isin(2*x)^3 + y)), log(sin(2*x)^3 + y)),
check("activateTrig: an already-active expression is unchanged",
      %mr_activateTrig(sin(x) + log(y)), sin(x) + log(y)),
check_bool("inertTrigQ: an inert head", %mr_inertTrigQ(%mr_isin)),
check_not("inertTrigQ: an active head", %mr_inertTrigQ(sin)),
check_not("inertTrigQ: not a trig head at all", %mr_inertTrigQ(log)),
check_bool("inertTrigFreeQ: no inert head present",
           %mr_inertTrigFreeQ(sin(x) + log(y))),
check_not("inertTrigFreeQ: an inert head is present",
          %mr_inertTrigFreeQ(log(%mr_isin(x)))),
check_bool("trigQ: an active trig head", %mr_trigQ(sin)),
check_not("trigQ: an inert head is not an active one", %mr_trigQ(%mr_isin)),
```

Note `%mr_inertTrigQ` takes a **head**, not an expression — Rubi's `InertTrigQ[f_]` is a `MemberQ` on the head symbol, and several rules call it on a head variable bound by the pattern. `%mr_hyperbolicQ` (`maxima_rubi_utils.mac:3898`) is the model, including its `if atom(u) then u else op(u)` shape, which was a real defect fixed during the class-6 port — read it before writing this.

- [ ] **Step 2: Run to verify they fail**

Expected: `Results: 1073 passed, 11 failed`.

- [ ] **Step 3: Implement**

In `maxima_rubi_utils.mac`, beside `%mr_hyperbolicQ`:

```maxima
/* Rubi InertTrigQ[f_] := MemberQ[{sin,cos,tan,cot,sec,csc},f]
   (IntegrationUtilityFunctions.m L6160). Takes a HEAD, as upstream does:
   rules bind F_ over an inert head and test this on the binding. The
   %mr_hyperbolicQ shape (atom u -> u, else op(u)) is deliberate — the atom
   branch was wrong there until 2026-09-20 and this one is faithful from the
   start. */
%mr_inertTrigQ(u) := block([],
  is(member(if atom(u) then u else op(u),
            [%mr_isin, %mr_icos, %mr_itan, %mr_icot, %mr_isec, %mr_icsc]) = true))$

/* Rubi InertTrigFreeQ[u_] := FreeQ[u,sin] && ... && FreeQ[u,csc] (L6173).
   An EXPRESSION test, unlike InertTrigQ. */
%mr_inertTrigFreeQ(u) := block([],
  is(freeof(%mr_isin, %mr_icos, %mr_itan, %mr_icot, %mr_isec, %mr_icsc, u) = true))$

/* Rubi TrigQ[f_] — the ACTIVE heads. Deliberately disjoint from
   %mr_inertTrigQ: a deactivated expression must not satisfy both. */
%mr_trigQ(u) := block([],
  is(member(if atom(u) then u else op(u),
            [sin, cos, tan, cot, sec, csc]) = true))$

/* Rubi ActivateTrig[u_] (L6180): the inverse of the inert head map of the
   inert-trig substrate design 3.1. subst on the operator name rewrites every
   occurrence at any depth. */
%mr_activateTrig(u) := block([r],
  r : u,
  r : subst(sin, %mr_isin, r), r : subst(cos, %mr_icos, r),
  r : subst(tan, %mr_itan, r), r : subst(cot, %mr_icot, r),
  r : subst(sec, %mr_isec, r), r : subst(csc, %mr_icsc, r),
  r)$
```

`subst(sin, %mr_isin, e)` substituting an operator for an operator must be verified on this build before relying on it — if it does not rewrite the head, use `%mr_substOp`-style recursion over `op`/`args` instead. The tests are what settle it; do not assume `subst` handles operator positions.

- [ ] **Step 4: Run to verify they pass**

Expected: `Results: 1084 passed, 0 failed`.

- [ ] **Step 5: Commit**

```sh
git add maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "utils: ActivateTrig and the inert-trig predicates

%mr_activateTrig (the inverse of the design 3.1 head map), %mr_inertTrigQ and
%mr_trigQ (both HEAD tests, as upstream, since rules test them on a head
variable's binding) and %mr_inertTrigFreeQ (an expression test). The
%mr_hyperbolicQ atom-branch shape is followed deliberately — it was wrong
there until the class-6 port and this one is faithful from the start.

Layer A 1073 -> 1084 passed, 0 failed."
```

---

### Task 6: `DeactivateTrig` — the conversion itself

**Files:**
- Modify: `maxima_rubi_utils.mac`
- Test: `test_maxima_rubi.mac`

**Interfaces:**
- Consumes: `%mr_fixInertTrigFunction`, `%mr_unifyInertTrigFunction`, `%mr_reduceInertTrig` (Task 4); `%mr_trigQ`, `%mr_hyperbolicQ` (Task 5 and existing); `%mr_expandToSum`, `%mr_linearQ` (existing).
- Produces: `%mr_deactivateTrigAux(u, x)` and `%mr_deactivateTrig(u, x)`. Task 9's bridge record calls `%mr_deactivateTrig`.

**Source:** `IntegrationUtilityFunctions.m:6189-6226`. Both branches of `DeactivateTrigAux`, and the two clauses of `DeactivateTrig`.

- [ ] **Step 1: Write the failing tests**

The six hyperbolic identities individually — these are the class-6 unlock and each is worth its own target:

```maxima
/* DeactivateTrig (inert-trig substrate design 0.2, 3.2). The six hyperbolic
 * identities of IntegrationUtilityFunctions.m L6210-6218, each checked on its
 * own: this is the mapping that makes the class-6 .7 family reachable.
 *   Sinh -> -I sin[I z]   Cosh ->   cos[I z]   Tanh -> -I tan[I z]
 *   Coth ->  I cot[I z]   Sech ->   sec[I z]   Csch ->  I csc[I z]           */
check("deactivate: Sinh", %mr_deactivateTrigAux(sinh(x), x), -%i*%mr_isin(%i*x)),
check("deactivate: Cosh", %mr_deactivateTrigAux(cosh(x), x), %mr_icos(%i*x)),
check("deactivate: Tanh", %mr_deactivateTrigAux(tanh(x), x), -%i*%mr_itan(%i*x)),
check("deactivate: Coth", %mr_deactivateTrigAux(coth(x), x), %i*%mr_icot(%i*x)),
check("deactivate: Sech", %mr_deactivateTrigAux(sech(x), x), %mr_isec(%i*x)),
check("deactivate: Csch", %mr_deactivateTrigAux(csch(x), x), %i*%mr_icsc(%i*x)),
/* The trig branch: head for head, argument untouched. */
check("deactivate: Sin", %mr_deactivateTrigAux(sin(x), x), %mr_isin(x)),
check("deactivate: Cos", %mr_deactivateTrigAux(cos(x), x), %mr_icos(x)),
/* Non-linear argument: the LinearQ guard means the head is left ACTIVE. */
check("deactivate: a non-linear argument is left active",
      %mr_deactivateTrigAux(sin(x^2), x), sin(x^2)),
/* Structural: it maps over a compound expression. */
check("deactivate: maps over a product",
      %mr_deactivateTrigAux(sin(x)*cos(x), x), %mr_isin(x)*%mr_icos(x)),
/* The round trip both ways — the invariant of design 3.1. */
check("round trip: trig", %mr_activateTrig(%mr_deactivateTrig(sin(x)^2, x)), sin(x)^2),
check_bool("round trip: hyperbolic closes numerically",
  /* %i factors must cancel; ratsimp cannot close a hyperbolic identity
     (AGENTS.md / class-6 trap), so go through exponentialize and compare
     numerically at a point. */
  is(abs(float(ev(exponentialize(%mr_activateTrig(%mr_deactivateTrig(sinh(x), x))
                                 - sinh(x)), x = 0.7))) < 1e-9)),
```

The expected forms of the six identities are what `ReduceInertTrig` returns for a plain linear argument, which may not be literally `-%i*%mr_isin(%i*x)` once `ReduceInertTrig`'s own four clauses have run. Determine each expected value from the `.m` clauses **before** writing the target, and if `ReduceInertTrig` normalises the argument, assert the normalised form. Do not weaken a target to whatever the code produces — if code and `.m` disagree, the code is wrong.

- [ ] **Step 2: Run to verify they fail**

Expected: `Results: 1084 passed, 12 failed`.

- [ ] **Step 3: Implement**

```maxima
/* Rubi DeactivateTrigAux[u,x] (IntegrationUtilityFunctions.m L6198-6218).
   Both branches. The hyperbolic branch is the cross-section bridge: it maps
   the six hyperbolic heads onto the six INERT TRIG heads by the
   imaginary-argument identities, with the argument multiplied by %i. This is
   how Rubi answers the class-6 shapes that have no section-6 rule file
   (probes/rubi/02-hyperbolic-inert-trig-bridge). */
%mr_deactivateTrigAux(u, x) := block([v],
  if atom(u) then u
  elseif %mr_trigQ(u) and %mr_linearQ([part(u, 1)], x) then (
    v : %mr_expandToSum(part(u, 1), x),
    if op(u) = sin then %mr_reduceInertTrig(%mr_isin, v)
    elseif op(u) = cos then %mr_reduceInertTrig(%mr_icos, v)
    elseif op(u) = tan then %mr_reduceInertTrig(%mr_itan, v)
    elseif op(u) = cot then %mr_reduceInertTrig(%mr_icot, v)
    elseif op(u) = sec then %mr_reduceInertTrig(%mr_isec, v)
    else %mr_reduceInertTrig(%mr_icsc, v))
  elseif %mr_hyperbolicQ(u) and %mr_linearQ([part(u, 1)], x) then (
    v : %mr_expandToSum(%i * part(u, 1), x),
    if op(u) = sinh then -%i * %mr_reduceInertTrig(%mr_isin, v)
    elseif op(u) = cosh then %mr_reduceInertTrig(%mr_icos, v)
    elseif op(u) = tanh then -%i * %mr_reduceInertTrig(%mr_itan, v)
    elseif op(u) = coth then %i * %mr_reduceInertTrig(%mr_icot, v)
    elseif op(u) = sech then %mr_reduceInertTrig(%mr_isec, v)
    else %i * %mr_reduceInertTrig(%mr_icsc, v))
  else %mr_mapArgs(lambda([t], %mr_deactivateTrigAux(t, x)), u))$

/* Rubi DeactivateTrig[u,x] (L6189-6195): the fast (c+d x)^m (a+b trig)^n
   clause, then the general one. */
%mr_deactivateTrig(u, x) := block([],
  %mr_unifyInertTrigFunction(%mr_fixInertTrigFunction(
    %mr_deactivateTrigAux(u, x), x), x))$
```

`%mr_mapArgs` is a stand-in for whatever this file already uses to rebuild an expression from mapped arguments — Rubi's clause is `Map[Function[DeactivateTrigAux[#,x]],u]`, which maps over the arguments and keeps the head. Find the existing idiom in `maxima_rubi_utils.mac` (there will be one; `Map` is common in the ported utilities) and use it. If there is none, `apply(op(u), map(lambda([t], %mr_deactivateTrigAux(t, x)), args(u)))` is the shape, but beware that for `+` and `*` Maxima resimplifies on rebuild, which is correct here.

The two-clause form of `DeactivateTrig` upstream includes a fast path for `(c+d x)^m (a+b trig[e+f x])^n`. Port it only if a Layer A target distinguishes it; otherwise the general clause subsumes it and the fast path is an optimisation this plan does not need. State which you did in the commit message.

- [ ] **Step 4: Run to verify they pass**

Expected: `Results: 1096 passed, 0 failed`.

- [ ] **Step 5: Commit**

```sh
git add maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "utils: DeactivateTrig — the trig and hyperbolic conversion

%mr_deactivateTrigAux carries both branches of
IntegrationUtilityFunctions.m L6198-6218: the trig branch head for head, and
the hyperbolic branch onto the same six INERT TRIG heads by the
imaginary-argument identities with the argument multiplied by %i. That second
branch is the cross-section bridge that makes the class-6 .7 family reachable
(probes/rubi/02).

All six hyperbolic identities are checked individually, plus the LinearQ guard
leaving a non-linear argument active, the map over a compound expression, and
the round trip both ways -- the hyperbolic one numerically through
exponentialize, because ratsimp cannot close a hyperbolic identity.

Layer A 1084 -> 1096 passed, 0 failed."
```

---

### Task 7: `FunctionOfTrigOfLinearQ` and `FunctionOfTrig`

The bridge rule's condition, and the substitution records' locator.

**Files:**
- Modify: `maxima_rubi_utils.mac`
- Test: `test_maxima_rubi.mac`

**Interfaces:**
- Consumes: `%mr_trigQ`, `%mr_hyperbolicQ`, `%mr_linearQ`.
- Produces: `%mr_functionOfTrigOfLinearQ(u, x)` → boolean; `%mr_functionOfTrig(u, x)` → the linear argument found, or `false`. Tasks 9 and 10 use both.

- [ ] **Step 1: Write the failing tests**

```maxima
/* FunctionOfTrigOfLinearQ — the bridge rule's condition. It must be TRUE for
 * a trig and for a hyperbolic function of a linear argument (that second case
 * is what admits class-6 integrands), and FALSE where deactivation must not
 * happen, or the bare-u_ bridge record would swallow the table. */
check_bool("fotlq: trig of a linear argument", %mr_functionOfTrigOfLinearQ(sin(2*x+1), x)),
check_bool("fotlq: hyperbolic of a linear argument", %mr_functionOfTrigOfLinearQ(sinh(2*x+1), x)),
check_bool("fotlq: a product of them", %mr_functionOfTrigOfLinearQ(sin(x)^4*(1+sinh(x)^2), x)),
check_not("fotlq: no trig at all", %mr_functionOfTrigOfLinearQ((1+x)^3, x)),
check_not("fotlq: trig of a NON-linear argument", %mr_functionOfTrigOfLinearQ(sin(x^2), x)),
check_not("fotlq: two different linear arguments",
          /* Rubi requires ONE linear argument throughout */
          %mr_functionOfTrigOfLinearQ(sin(x)*cos(2*x+1), x)),
check_not("fotlq: an inert expression is not deactivated twice",
          %mr_functionOfTrigOfLinearQ(%mr_isin(x), x)),
check("fot: returns the linear argument", %mr_functionOfTrig(sin(2*x+1), x), 2*x+1),
check("fot: false when there is none", %mr_functionOfTrig((1+x)^3, x), false),
```

The `two different linear arguments` and `an inert expression` targets are the two that matter most: both are cases where a `true` would make the bridge rule fire where Rubi's does not, and the bridge rule is a bare `u_` at the end of the table, so a wrong `true` is an infinite deactivation loop or a swallowed integrand. Read Rubi's `FunctionOfTrigOfLinearQ` and `FunctionOfTrig` before writing the implementation and confirm the single-argument requirement from the source rather than from these targets.

- [ ] **Step 2: Run to verify they fail**

Expected: `Results: 1096 passed, 9 failed`.

- [ ] **Step 3: Implement**

Port both from `IntegrationUtilityFunctions.m`, following the house style of the neighbouring predicates: a `block` with explicit locals, `is(... = true)` on every boolean return, and a comment naming the upstream function and line. Both are recursive walks over the expression; `%mr_functionOfTrig` returns the argument it found so that the caller can reuse it, and `%mr_functionOfTrigOfLinearQ` is the boolean form. Keep them faithful — in particular, the inert heads must not satisfy them, or deactivation recurses.

- [ ] **Step 4: Run to verify they pass**

Expected: `Results: 1105 passed, 0 failed`.

- [ ] **Step 5: Commit**

```sh
git add maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "utils: FunctionOfTrigOfLinearQ and FunctionOfTrig

The bridge rule's condition and the substitution records' locator. The two
targets that matter are the negative ones: two different linear arguments, and
an already-inert expression. The bridge rule is a bare u_ at the END of the
table, so a wrong true is a deactivation loop or a swallowed integrand rather
than a wrong answer.

Layer A 1096 -> 1105 passed, 0 failed."
```

---

### Task 8: `_tail` rule lists and their position in the table

Built before any tail record exists, so the mechanism is tested on its own.

**Files:**
- Modify: `generator/generate_rules.py`
- Modify: `maxima_rubi.mac`
- Modify: `test/check_generated_rules.py`
- Test: `test_maxima_rubi.mac`

**Interfaces:**
- Consumes: nothing new.
- Produces: the convention that a generated file may define `mr_rules_<key>_tail` beside `mr_rules_<key>`, and that `mr_load_all` appends every `_tail` list to `mr_rule_table` after all classes. Task 9 emits the first tail records.

- [ ] **Step 1: Write the failing test**

```maxima
/* Tail rule lists (inert-trig substrate design 3.3). A bare-u_ record sits at
 * the END of mr_rule_table, because our dispatcher walks in load order and
 * stops at the first rule that answers (Mathematica orders it last by pattern
 * specificity instead). The regression this prevents: a catch-all swallowing
 * an integrand an earlier class answers. */
check_bool("tail records are last in the table",
  /* every tail handle is greater than every non-tail handle */
  is(lmin(mr_rule_table_tail_handles) > lmax(mr_rule_table_body_handles))),
```

Expose the two handle lists from `mr_load_all` (as `mr_rule_table_body_handles` and `mr_rule_table_tail_handles`) so the ordering is assertable rather than inspected by eye. Handles are the 1-based registration index, so "greater" is "registered later", and registration order is load order.

- [ ] **Step 2: Run to verify it fails**

Expected: `Results: 1105 passed, 1 failed` — the two lists do not exist.

- [ ] **Step 3: Implement**

In `generator/generate_rules.py`: when a source file yields a record whose integrand pattern is a bare `u_` (an unconstrained `(Pattern <name> (Blank))` in the `Int`'s first argument), emit its handle into `mr_rules_<key>_tail` instead of `mr_rules_<key>`, and emit both lists plus `mr_rules_count_<key>` covering the two together.

In `maxima_rubi.mac`'s `mr_load_all`: collect the tail lists and append them after every class's body lists, and set the two handle lists the test reads.

In `test/check_generated_rules.py`: assert that every record in a `_tail` list has a bare-`u_` integrand pattern, and that no record with a bare-`u_` integrand pattern appears in a body list. That is the check that makes the convention self-enforcing in both directions.

- [ ] **Step 4: Run to verify it passes**

```sh
maxima --very-quiet -b test_maxima_rubi.mac
python3 test/check_generated_rules.py
python3 generator/generate_rules.py --class 1 && python3 generator/generate_rules.py --class 2 \
  && python3 generator/generate_rules.py --class 3 && python3 generator/generate_rules.py --class 6 \
  && python3 generator/generate_rules.py --rewrites && git status --porcelain rules/
```

Expected: Layer A `1106 passed, 0 failed`; the static gate green at its new count; `git status --porcelain rules/` **empty** — classes 1/2/3/6 must regenerate byte-identically, because none of them has a bare-`u_` record and the new code path must not touch them. If any class-1/2/3/6 file changes, the bare-`u_` detector is too broad; narrow it until they are byte-identical again.

- [ ] **Step 5: Commit**

```sh
git add generator/generate_rules.py maxima_rubi.mac test/check_generated_rules.py test_maxima_rubi.mac
git commit -m "generate: tail rule lists for bare-u_ records

A generated file may now define mr_rules_<key>_tail beside mr_rules_<key>, and
mr_load_all appends every tail list to mr_rule_table after all classes. Our
dispatcher walks in load order and stops at the first rule that answers, so a
bare-u_ catch-all has to be last; Mathematica gets there by pattern
specificity.

The static gate enforces the convention both ways: every tail record has a
bare-u_ integrand, and no bare-u_ record sits in a body list. Classes 1/2/3/6
regenerate byte-identically -- none of them has such a record and the new path
must not touch them.

Layer A 1105 -> 1106 passed, 0 failed."
```

---

### Task 9: The six straightforward bridge records

Six of the seven: the `4.1.0.1` deactivation rule and `4.7.5`'s five `Subst`-based records. The Weierstrass record is Task 10.

**Files:**
- Modify: `generator/generate_rules.py` (class 4 registration, `EXPECTED_TOTAL`)
- Create: `rules/class4/4_1_0_1.mac`, `rules/class4/4_7_5.mac` (generated)
- Modify: `maxima_rubi.mac`
- Test: `test_maxima_rubi.mac`

**Interfaces:**
- Consumes: `%mr_deactivateTrig`, `%mr_functionOfTrigOfLinearQ`, `%mr_functionOfTrig`, `%mr_freeFactors` (existing), `%mr_subst` (existing), the tail mechanism from Task 8.
- Produces: the bridge, live. The chain of spec §3.5 is complete except the Weierstrass record.

- [ ] **Step 1: Write the failing test — the acceptance signal**

This is spec §5's second criterion, and it is the target the whole plan exists for:

```maxima
/* The inert-trig bridge, end to end (inert-trig substrate design 3.5, 5.2).
 * A 6.1.7 integrand: a power of one hyperbolic times a binomial in another.
 * Rubi has NO section-6 rule for this shape — it answers it through section
 * 4's rules via the inert bridge, and before this plan the package reached no
 * rule at all for the whole 1,173-entry family (1,166 deferred, zero PASS).
 *
 * Corpus entry, 6.1 Hyperbolic sine/6.1.7 hyper^m (a+b sinh^n)^p.mac:
 *   [sinh(c+d*x)*(a+b*sinh(c+d*x)^2), x, 2,
 *    (a-b)*cosh(c+d*x)/d + 1/3*b*cosh(c+d*x)^3/d]
 * Verified by differentiation, not by comparing to the expected text: the
 * package's form may differ and still be right. */
check_bool("6.1.7: the bridge answers a hyperbolic .7 integrand",
  block([f, r],
    f : sinh(c + d*x)*(a + b*sinh(c + d*x)^2),
    r : rubi(f, x),
    is(r # false) and
    is(ratsimp(exponentialize(diff(r, x) - f)) = 0))),
```

`ratsimp(exponentialize(...))` is the zero chain shape the class-6 port settled on — plain `ratsimp` cannot close a hyperbolic identity. If the residual will not close symbolically, fall back to a numeric check at two points, and say so in the target's comment.

- [ ] **Step 2: Run to verify it fails**

Expected: `Results: 1106 passed, 1 failed` — `rubi` returns `false`, because no rule matches the shape.

- [ ] **Step 3: Generate the two files**

Register class 4 in the generator with `EXPECTED_TOTAL[4]` covering only the records this plan emits, and generate `4_1_0_1` and `4_7_5` **restricted to their bare-`u_` records** — `--only` exists for exactly this. The rest of both files' rules belong to the class-4 port; emitting them here would pull in the whole unadjudicated token closure.

The `4.1.0.1` record is the `If[TrueQ[$LoadShowSteps], …]`-wrapped one, which the census parser does not see and `unwrap_showsteps_lines` recovers; confirm it is recovered rather than silently skipped — a missing record here is a silently absent bridge, and Step 1's target is what catches it.

Wire both files into `mr_load_all` after class 6, with their tail lists going to the table tail.

- [ ] **Step 4: Run to verify it passes**

```sh
maxima --very-quiet -b test_maxima_rubi.mac
python3 test/check_generated_rules.py
python3 generator/generate_rules.py --class 4 && git status --porcelain rules/
```

Expected: Layer A `1107 passed, 0 failed`; static gate green; regeneration byte-identical.

- [ ] **Step 5: Check for class regressions**

The bridge is a catch-all. Prove it did not capture anything it should not:

```sh
sh test/build_rules_core.sh
python3 test/corpus_driver.py "1.1.1.2" 20 30 "reference/maxima-syntax-test-suite" \
    0 "" 0 /tmp/claude-1000/inert-c1-slice.out
python3 test/corpus_driver.py "6.2.2 " 8 30 "reference/maxima-syntax-test-suite" \
    0 "" 0 /tmp/claude-1000/inert-c6-slice.out
```

Both slices need an out-file positional and the suite-dir positional — the driver's default is now a scratch path (`dc0c920`) but naming the out-file is the standing rule, and without the suite dir a non-class-1 filter resolves 0 files.

Compare each against the committed record for the same entries with `python3 test/ab_records.py`, and attribute every PASS→FAIL. A bare-`u_` record that fires where an earlier class answered would show up here as a wave of transitions.

- [ ] **Step 6: Commit**

```sh
git add generator/generate_rules.py rules/class4/4_1_0_1.mac rules/class4/4_7_5.mac \
        maxima_rubi.mac test_maxima_rubi.mac
git commit -m "rules: the inert-trig bridge, six of the seven tail records

4.1.0.1's deactivation rule and 4.7.5's five Subst-based records, generated
with --only so that neither file's remaining rules -- which need the
unadjudicated class-4 token closure -- come with them. All six are bare-u_ and
all six land in the table tail.

The acceptance signal of the spec's 5.2 is green: a 6.1.7 integrand now answers
and verifies. Before this commit the package reached no rule at all for that
1,173-entry family (1,166 deferred, zero PASS), because Rubi has no section-6
rule for the shape and answers it through section 4 via the bridge.

Layer A 1106 -> 1107 passed, 0 failed; class-1 and class-6 slices A/B'd against
their committed records with every transition attributed."
```

---

### Task 10: The Weierstrass record, and the leak guard

The seventh tail record needs `TryPureTanSubst` and `SubstFor`, which spec §1 lists as out of scope; this task amends that. The leak guard closes spec §3.4.

**Files:**
- Modify: `maxima_rubi_utils.mac`
- Modify: `rules/class4/4_7_5.mac` (regenerated with the seventh record)
- Modify: `test/corpus_driver.py`
- Test: `test_maxima_rubi.mac`, `test/test_driver_out_default.py`-style guard for the driver change

**Interfaces:**
- Consumes: everything above.
- Produces: `%mr_tryPureTanSubst(u, x)`, `%mr_substFor(...)`, and the `%mr_i`-leak classification in the driver.

- [ ] **Step 1: Write the failing leak-guard tests first**

The guard is the more important half, because it protects every later class-4 task:

```maxima
/* The inert-head leak guard (inert-trig substrate design 3.1 invariant, 3.4).
 * An inert head exists only between the bridge rule and activation. A rule
 * that forgot its %mr_activateTrig would otherwise return junk that
 * differentiates to nothing recognisable and lands in a deferred mass. */
check_not("no inert head leaks from a trig answer",
          is(%mr_inertTrigFreeQ(rubi(sin(x)^2, x)) = false)),
check_not("no inert head leaks from a hyperbolic answer",
          is(%mr_inertTrigFreeQ(rubi(sinh(c+d*x)*(a+b*sinh(c+d*x)^2), x)) = false)),
```

and for the driver, a guard test in the style of `test/test_driver_out_default.py`: an answer text containing a `%mr_i` head is classified `error`, not a FAIL class.

- [ ] **Step 2: Run to verify they fail**

The Layer A pair may already pass if no rule leaks — that is fine and expected for a guard, but the **driver** check must fail first: write it, watch it fail, then implement. If the Layer A pair passes immediately, say so in the commit message rather than pretending it was red.

- [ ] **Step 3: Implement the driver guard**

In `test/corpus_driver.py`, beside the existing class assignment: an answer containing a `%mr_i` head is classified `error` with a message naming the leak. Add `error` handling only — do not add a new class to `KNOWN_CLASSES`, since `error` is already one, and a new class would break the mergers' agreement with the driver.

- [ ] **Step 4: Port TryPureTanSubst and SubstFor, and emit the seventh record**

Port both from `IntegrationUtilityFunctions.m` with Layer A targets each, then regenerate `4_7_5.mac` with the Weierstrass record included. The record's `Block[{$ShowSteps = False, $StepCounter = Null}]` sets Rubi globals the port has no equivalent of: state in a comment what the port does with them rather than dropping them silently, following the deviation-stamp discipline of `maxima_rubi_utils.mac`. `mr_simplify_flag` (`maxima_rubi_utils.mac:11`) is the precedent for a ported Rubi global.

- [ ] **Step 5: Run every gate**

```sh
maxima --very-quiet -b test_maxima_rubi.mac
maxima --very-quiet -b test/matcher/test_mr_match.mac
maxima --very-quiet -b test/matcher/test_mr_tree.mac
maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null
python3 test/check_generated_rules.py
python3 test/test_head_rewrites.py
python3 test/test_run_records.py
python3 test/test_driver_out_default.py
for c in 1 2 3 6; do python3 generator/generate_rules.py --class $c; done
python3 generator/generate_rules.py --class 4
python3 generator/generate_rules.py --rewrites
git status --porcelain rules/
```

Expected: every suite green at its stated count, and `git status --porcelain rules/` empty.

- [ ] **Step 6: Commit**

```sh
git add maxima_rubi_utils.mac rules/class4/4_7_5.mac test/corpus_driver.py test_maxima_rubi.mac
git commit -m "rules: the Weierstrass record, and the inert-head leak guard

The seventh tail record — 4.7.5's half-angle substitution — with
TryPureTanSubst and SubstFor ported for it. That amends the spec's section 1,
which listed TryPureTanSubst out of scope before the seven tail records were
enumerated; nothing else moves in.

The leak guard closes the design's 3.1 invariant: an answer carrying a %mr_i
head is an ERROR in the driver, not a FAIL class, and Layer A asserts no leak
from a trig and from a hyperbolic answer. A rule that forgot its
%mr_activateTrig now fails loudly instead of hiding in a deferred mass."
```

---

## Self-Review

**Spec coverage.** §2.5 → Task 1. §3.1 → Task 2. §3.2's mechanism → Task 3; its three generated tables → Task 4; its hand-written members → Tasks 5, 6, 7. §3.3 → Task 8. §3.4 → Task 10. §3.5's end-to-end chain → Task 9's acceptance target. §4's six phases map to the tasks as P1→1+2, P2→3, P3→4, P4→5+6+7, P5→8, P6→9+10. §5's four acceptance criteria: (1) the standing gates, run at every task and in full at Task 10 Step 5; (2) the `6.1.7` target, Task 9 Step 1; (3) the class regression A/B, Task 9 Step 5; (4) the leak guard, Task 10.

**One spec gap found and closed:** §1 lists `TryPureTanSubst` out of scope while §0.3 requires the Weierstrass record that calls it. Task 10 brings it in, and says so in its commit message. This is flagged to the user rather than silently absorbed.

**One spec section deliberately not given a task:** §6's risks are not work items. Two of them are load-bearing during execution and are reproduced as constraints instead — the no-depth-guard decision (Task 4's comment) and the `ratsimp`-cannot-close-a-hyperbolic-identity trap (Global Constraints, and Tasks 6 and 9's zero chains).

**Type and name consistency.** `%mr_defrewrite(key, n, pattern, cond, repl)` and `%mr_rewrite(head, table, u, x)` are defined in Task 3 and used with those exact arities in Tasks 4 and beyond. `%mr_inertTrigQ` takes a **head** and `%mr_inertTrigFreeQ` an **expression** — asserted in Task 5, relied on in Tasks 6, 7 and 10. The tables are `mr_rw_uitf` / `mr_rw_fitf` / `mr_rw_rit` in Task 4 and nowhere renamed. The six operators are `%mr_isin` / `%mr_icos` / `%mr_itan` / `%mr_icot` / `%mr_isec` / `%mr_icsc` in Tasks 1, 2, 5, 6 and 10 with no variant spelling.

**Task 1 is deliberately first and deliberately cheap.** It can invalidate the six names that every other task hard-codes, and a rename after Task 4 would touch generated files.
