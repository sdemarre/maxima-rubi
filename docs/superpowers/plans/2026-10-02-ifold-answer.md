# The %i fold of rubi's answer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** fold `%i` out of trig/hyperbolic functions of an imaginary argument in rubi's final answer (`sin(%i*b*x+%i*a)` -> `%i*sinh(b*x+a)`), behind the run switch `mr_ifold`, and re-measure every section.

**Architecture:** a Maxima function `%mr_ifold` (probe 04's fold plus two guards) in `maxima_rubi_utils.mac`, applied by a new `%mr_top_final` to the answer of the depth-0 `mr_top` call only, under `radexpand:false, logexpand:false`, inside `errcatch`. The switch is a `defmvar` in `maxima_rubi_dispatch.lisp`, carried to every record's `filter:` line by `test/run_records.py`.

**Tech Stack:** Maxima (build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7), Common Lisp `defmvar`, Python 3 harness.

**Spec:** `docs/superpowers/specs/2026-10-02-ifold-answer-design.md` (read it first). Ticket: `.scratch/answer-quality/issues/01-hyperbolic-answers-keep-i.md`.

## Global Constraints

- The fold acts on the **depth-0 answer only** — never on a nested `mr_int` result, never on an intermediate integrand.
- The fold always runs under `radexpand : false, logexpand : false`, bound by `%mr_top_final` itself, independent of `mr_model_flags` (under Maxima's defaults it is unsound: `(-%i*y)^(2/3)` -> `-y^(2/3)`).
- A `%i`-free answer is returned **itself** (CRE stays CRE); an `integrate` or `unintegrable` noun is returned as is, at any depth.
- The fold can never cost an answer: any error inside it returns the unfolded answer.
- `mr_ifold : false` reproduces today's answers byte for byte.
- Locals in Maxima functions are prefixed (`%mr_if_`, `%mr_tf_`) — the project's capture-trap convention (rule-generated code binds short names).
- Commits: no `Co-Authored-By` and no `Claude-Session:` trailers (AGENTS.md). Do not push.
- Test reading protocol (AGENTS.md "Tests"): read the `Results:` line, grep the output for `Lisp error`, and compare the PASS count with the expected figure.
- Maxima runs: redirect stdin from `/dev/null`.

## Review Focus

- **A CRE answer that carries `%i`** — the fold walks it as general form and returns general form; the value must be preserved (pinned in Task 2: `radcan(fold - input) = 0`).
- **An answer whose `%i` cannot be folded** (`sqrt(%i*x+%i*a)`, `log(%i*...)`) — must come back with the same value, not an error (pinned in Task 2: the sum rule's `%i*(x+a)` inside `sqrt`).
- **`rubi_fallback`'s `integrate` result** — passes through the same depth-0 path; a Maxima `integrate` noun at top level must stay the top-level noun so the driver's `deferred` test still reads it (pinned in Task 2's noun checks and Task 3's fallback check).
- **The global `radexpand : true` at the caller** — the folded answer must not be split after `mr_top` returns (pinned in Task 3: the `cot(...)^(1/3)` witness through `rubi`).
- **A fold that errors** — the answer is still returned (pinned in Task 3 with a `local`-redefined `%mr_ifold`).

---

### Task 1: The run switch `mr_ifold`

**Files:**
- Modify: `maxima_rubi_dispatch.lisp` (after the `(defmvar $mr_gtq_facts ...)` form — find it with `grep -n "defmvar \$mr_gtq_facts" maxima_rubi_dispatch.lisp`)
- Modify: `test/run_records.py:54-67` (`SWITCHES`, `SWITCH_DEFAULTS`)
- Test: `test/test_run_records.py:300-316` (the two expected header/entry-text strings)

**Interfaces:**
- Produces: the Maxima option variable `mr_ifold` (default `true`); `run_records.SWITCHES[-1] == "mr_ifold"`, `SWITCH_DEFAULTS["mr_ifold"] == "true"`. Every corpus entry text then begins with the switch assignments ending `mr_gtq_facts : false$\nmr_ifold : true$\n`.

- [ ] **Step 1: Write the failing test** — in `test/test_run_records.py`, extend both expected strings of section 5:

```python
              "mr_eqq_symbolic=true mr_subst_simp=false mr_gtq_facts=false mr_ifold=true"),
```
and
```python
              "mr_eqq_symbolic : true$\nmr_subst_simp : false$\nmr_gtq_facts : false$\nmr_ifold : true$\n"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 test/test_run_records.py`
Expected: `Results: 41 passed, 2 failed` (the two header checks; the baseline is 43/0).

- [ ] **Step 3: Add the switch.** In `maxima_rubi_dispatch.lisp`, after the `mr_gtq_facts` defmvar:

```lisp
(defmvar $mr_ifold t
  "Run switch: true (default) = the top-level call's answer is passed through
%mr_ifold (maxima_rubi_utils.mac) under radexpand:false, logexpand:false,
which folds %i out of a trig / hyperbolic / inverse function of an imaginary
argument the way Mathematica's evaluator does (sin(%i*b*x+%i*a) ->
%i*sinh(b*x+a)); false = the answer as the rules built it, every record
before 2026-10-02.

WHY (.scratch/answer-quality/issues/01, user decision 2026-10-02). Rubi
integrates hyperbolics through the trig rules (DeactivateTrigAux,
Sinh[u] -> -I*sin[I*u]) and relies on Mathematica's evaluator to fold the I
back out; Maxima's %iargs folds sin(%i*v) only when the argument is literally
a multiple of %i. Section 6 graded C on 1,854 of 5,080 answers for it.
Measured on every entry it can act on (probes/leaf-size/05): no grade worse,
section 6 C->A 1,511, 0 PASS lost outside 9 attributed checker artefacts
(probe 06).")
```

In `test/run_records.py`, append to `SWITCHES` and `SWITCH_DEFAULTS`:

```python
SWITCHES = ("mr_flat_wide", "mr_cond_retry", "mr_model_flags",
            "mr_nested_fallback", "mr_giveup_last", "mr_inert_leak_misfire",
            "mr_last_resort_tier", "mr_general_after_giveups", "mr_max_depth",
            "mr_eqq_symbolic", "mr_subst_simp", "mr_gtq_facts", "mr_ifold")
```
and `"mr_gtq_facts": "false",` followed by `"mr_ifold": "true"}`.

- [ ] **Step 4: Run it to verify it passes**

Run: `python3 test/test_run_records.py`
Expected: `Results: 43 passed, 0 failed` (check 1, "driver switch defaults == dispatcher defmvar defaults", now also covers `mr_ifold`).

- [ ] **Step 5: The dispatch suite still loads the Lisp**

Run: `maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null 2>&1 | grep -E "Results:|Lisp error"`
Expected: the same `Results:` figure as before this task (read it first with the same command on the unmodified tree), no `Lisp error`.

- [ ] **Step 6: Commit**

```bash
git add maxima_rubi_dispatch.lisp test/run_records.py test/test_run_records.py
git commit -m "dispatch+records: the run switch mr_ifold (answer-quality 01)"
```

---

### Task 2: `%mr_ifold`, the fold

**Files:**
- Modify: `maxima_rubi_utils.mac` (insert directly above the `/* Under rubi_verbose : matches the top-level call ...` comment that precedes `mr_top`, around line 262)
- Test: `test_maxima_rubi.mac` (a new `test_ifold_unit()` and its call in `run_all_tests`, right before `test_census(),`)

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: `%mr_ifold(e)` — returns `e` folded, binds no flag (the caller binds them); `e` itself when `freeof(%i, e)`.

- [ ] **Step 1: Read the baseline.** Run `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null 2>&1 | grep -E "Results:|Lisp error"` and note the figure (`N passed, 0 failed`; AGENTS.md last recorded 1658).

- [ ] **Step 2: Write the failing test.** Add to `test_maxima_rubi.mac`, before `run_all_tests() :=` is called at the end (next to the other test functions, e.g. after `test_rubi_errata`'s definition):

```maxima
/* The %i fold of the top-level answer (.scratch/answer-quality/issues/01,
   spec docs/superpowers/specs/2026-10-02-ifold-answer-design.md). The fold
   itself: %mr_ifold under the flags %mr_top_final binds. Expected forms are
   the measured outputs of the build (2026-10-02). */
t_if(t_if_e) := block([radexpand : false, logexpand : false], %mr_ifold(t_if_e))$
test_ifold_unit() := block([t_if_r, t_if_e],
  print("--- the %i fold: %mr_ifold ---"),
  check("ifold: sin of an imaginary sum", t_if(sin(%i*b*x+%i*a)), %i*sinh(b*x+a)),
  check("ifold: cos of an imaginary sum", t_if(cos(%i*b*x+%i*a)), cosh(b*x+a)),
  check("ifold: the outer %i multiplies out", t_if(-%i*(%i*X+%i*Y)), X+Y),
  check("ifold: nested (6.1.1 e1's shape)",
        t_if(-(%i*((%i*x*cos(%i*b*x+%i*a))/b-sin(%i*b*x+%i*a)/b^2))),
        (x*cosh(b*x+a))/b-sinh(b*x+a)/b^2),
  check("ifold: a product of folded functions",
        t_if(-((%i*cos(%i*b*x+%i*a)*sin(%i*b*x+%i*a))/(2*b))-x/2),
        (cosh(b*x+a)*sinh(b*x+a))/(2*b)-x/2),
  check("ifold: inside a log", t_if(log(cos(%i*b*x+%i*a))/b), log(cosh(b*x+a))/b),
  check("ifold: atan -> %i atanh", t_if(atan(%i*x+%i*a)), %i*atanh(x+a)),
  check("ifold: acot -> -%i acoth", t_if(acot(%i*x+%i*a)), -%i*acoth(x+a)),
  /* untouched */
  t_if_e : x^2 + sin(x),
  check_bool("ifold: an %i-free answer is returned itself", is(t_if(t_if_e) = t_if_e)),
  check_bool("ifold: an %i-free CRE answer stays CRE", ratp(t_if(rat(x^2/2 + x)))),
  check("ifold: a CRE answer with %i keeps its value",
        radcan(t_if(rat(%i*x+%i*a)) - (%i*x+%i*a)), 0),
  check("ifold: an unfoldable %i keeps its value",
        radcan(t_if(sqrt(%i*x+%i*a)) - sqrt(%i*x+%i*a)), 0),
  t_if_e : 'unintegrable(sin(%i*x+%i*a), x),
  check_bool("ifold: the unintegrable noun is opaque", is(t_if(t_if_e) = t_if_e)),
  t_if_e : 'integrate(sin(%i*x+%i*a), x),
  check_bool("ifold: the integrate noun is opaque", is(t_if(t_if_e) = t_if_e)),
  t_if_r : t_if(sin(%i*x+%i*a) + 'integrate(cos(%i*x+%i*a), x)),
  check_bool("ifold: a noun inside a sum is opaque, its sibling folds",
             is(t_if_r = %i*sinh(x+a) + 'integrate(cos(%i*x+%i*a), x))),
  /* the flags: the folded power keeps its base whole under radexpand:false;
     under the defaults it splits onto the wrong branch (the hazard) */
  t_if_r : t_if(cot(%i*b*x+%i*a)^(1/3)),
  check_bool("ifold: under the flags the folded power keeps its base",
             is(op(t_if_r) = "^") and is(part(t_if_r, 2) = 1/3)
             and is(part(t_if_r, 1) = -%i*coth(b*x+a))),
  check_bool("ifold: under radexpand:true the same fold splits (the hazard)",
             freeof(%i, block([radexpand : true], %mr_ifold(cot(%i*b*x+%i*a)^(1/3))))),
  true
)$
```

and in `run_all_tests`, insert `test_ifold_unit(),` on the line before `test_census(),`.

- [ ] **Step 3: Run it to verify it fails**

Run: `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null 2>&1 | grep -E "Results:|Lisp error|FAIL"`
Expected: the new section's checks FAIL (`%mr_ifold` undefined returns its noun form `%mr_ifold(...)`); the run still prints a `Results:` line with the baseline count passed and 17 failed. If a `Lisp error` aborts the section instead, the count of failures is lower — that also counts as RED; note it.

- [ ] **Step 4: Write the implementation.** In `maxima_rubi_utils.mac`, above the `mr_top` verbose comment:

```maxima
/* ---- the %i fold of the top-level answer -------------------------------
   (.scratch/answer-quality/issues/01; spec
   docs/superpowers/specs/2026-10-02-ifold-answer-design.md.) Rubi
   integrates hyperbolics through the trig rules: DeactivateTrigAux
   (IntegrationUtilityFunctions.m:6198, %mr_deactivateTrigAux below)
   rewrites Sinh[u] as -I*sin[I*u], and Mathematica's evaluator folds the
   result back (Sin[I a + I b x] -> I Sinh[a + b x]). Maxima's %iargs
   folds sin(%i*v) only when the argument is literally a multiple of %i,
   so rubi's answers kept sin(%i*b*x+%i*a) and their %i (section 6 graded C
   on 1,854 of 5,080). %mr_ifold puts each such argument into the literal
   form %iargs folds, and pulls %i out of a sum whose every term carries
   one. Probe 04's fold, plus two guards: an %i-free expression is returned
   itself (a CRE answer stays CRE), and the integrate / unintegrable nouns
   are opaque (the top-level no-answer noun keeps its operator; an
   unintegrated integrand is not an answer). It binds no flag: its caller,
   %mr_top_final, binds radexpand:false, logexpand:false -- under the
   defaults the simplifier splits the folded powers onto the wrong branch,
   (-%i*y)^(2/3) -> -y^(2/3) (probes/leaf-size/05, MR_IFOLD_FLAGS=default).
   Measured on every entry it can act on (probe 05): no grade worse. */
%mr_ifold(%mr_if_e) :=
  if freeof(%i, %mr_if_e) or atom(%mr_if_e) then %mr_if_e
  else if member(string(op(%mr_if_e)), ["integrate", "unintegrable"]) then %mr_if_e
  else block([%mr_if_o : op(%mr_if_e), %mr_if_a : map('%mr_ifold, args(%mr_if_e)), %mr_if_v],
    if member(%mr_if_o, [sin, cos, tan, cot, sec, csc, sinh, cosh, tanh, coth, sech, csch,
                         asin, acos, atan, acot, asec, acsc,
                         asinh, acosh, atanh, acoth, asech, acsch])
       and length(%mr_if_a) = 1 and not freeof(%i, %mr_if_a[1]) then (
      %mr_if_v : ratsimp(%mr_if_a[1]/%i),
      if freeof(%i, %mr_if_v) then apply(%mr_if_o, [%i*%mr_if_v])
      else apply(%mr_if_o, %mr_if_a))
    else if %mr_if_o = "+" and not freeof(%i, %mr_if_a) then (
      %mr_if_v : map(lambda([%mr_if_t], %mr_if_t/%i), %mr_if_a),
      if freeof(%i, %mr_if_v) then %i*apply("+", %mr_if_v)
      else apply(%mr_if_o, %mr_if_a))
    else apply(%mr_if_o, %mr_if_a))$
```

- [ ] **Step 5: Run it to verify it passes**

Run: `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null 2>&1 | grep -E "Results:|Lisp error"`
Expected: `Results: <baseline + 17> passed, 0 failed`, no `Lisp error`. If a `check` with an exact expected form fails only on term order or sign layout, print the actual (`grep -A2 "FAIL:"`) and confirm `radcan(actual - expected) = 0` before re-pointing the expected value to the build's output — the spec's expected forms are the 2026-10-02 measurements.

- [ ] **Step 6: Commit**

```bash
git add maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "utils: %mr_ifold, the %i fold of an answer (answer-quality 01)"
```

---

### Task 3: `%mr_top_final` — the fold at depth 0

**Files:**
- Modify: `maxima_rubi_utils.mac` (`mr_top`, currently `:266-272`, and a new `%mr_top_final` right above it)
- Test: `test_maxima_rubi.mac` (a new `test_ifold_top()`, called right after `test_ifold_unit(),`; four checks in `test_class4_e2e`, which already integrates `sinh(2x)/x` and `cosh(x) sinh(x)^2` through the bridge)
- Gates (no change; they must stay green): `test/matcher/test_mr_dispatch.mac`, `test/test_rule_table_order.mac`, `test/test_section9_e2e.mac`, the matcher and harness suites

**Interfaces:**
- Consumes: `%mr_ifold(e)` (Task 2), `mr_ifold` (Task 1).
- Produces: `%mr_top_final(ans)` — `ans` folded when `mr_ifold` is true, else `ans`; never errors. `mr_top` at `depth_level = 0` returns `%mr_top_final(answer)` (verbose: `[%mr_top_final(answer), steps]`).

- [ ] **Step 1: Write the failing test.** Add to `test_maxima_rubi.mac`, after `test_ifold_unit`'s definition:

```maxima
/* The fold at depth 0 (mr_top / %mr_top_final), with synthetic rule records
   (the test_dispatch idiom): r7 answers x^7 with an imaginary-argument sin,
   r5 answers x^5 the same way, r57 answers x^7 by dispatching x^5 and
   recording the nested result. */
t_ifr_true(mm, x) := true$
t_ifr_sin(mm, x) := sin(%i*x+%i*a)$
t_ifr_cot(mm, x) := cot(%i*b*x+%i*a)^(1/3)$
t_ifr_nest(mm, x) := (t_ifr_seen : mr_int(x^5, x), 1)$
test_ifold_top() := block([t_ifr_p7, t_ifr_p5, h7, h5, h57, hcot, t_ifr_saved,
                           t_ifr_sw, t_ifr_vb, t_ifr_r],
  print("--- the %i fold: the top-level answer ---"),
  t_ifr_p7 : "(Int (Power (Pattern x (Blank)) 7) (Pattern x (Blank Symbol)))",
  t_ifr_p5 : "(Int (Power (Pattern x (Blank)) 5) (Pattern x (Blank Symbol)))",
  h7 : %mr_defrule("ifold", 1, t_ifr_p7, t_ifr_true, t_ifr_sin),
  h5 : %mr_defrule("ifold", 2, t_ifr_p5, t_ifr_true, t_ifr_sin),
  h57 : %mr_defrule("ifold", 3, t_ifr_p7, t_ifr_true, t_ifr_nest),
  hcot : %mr_defrule("ifold", 4, t_ifr_p7, t_ifr_true, t_ifr_cot),
  t_ifr_saved : mr_rule_table, t_ifr_sw : mr_ifold, t_ifr_vb : rubi_verbose,
  rubi_verbose : false,
  mr_rule_table : [h7],
  mr_ifold : true,
  check("top fold: the answer is folded", rubi(x^7, x), %i*sinh(x+a)),
  check("top fold: rubi_fallback folds too", rubi_fallback(x^7, x, true), %i*sinh(x+a)),
  mr_ifold : false,
  check("top fold: mr_ifold false answers the rules' form", rubi(x^7, x), sin(%i*x+%i*a)),
  mr_ifold : true,
  /* nested: the inner answer is NOT folded */
  mr_rule_table : [h57, h5],
  t_ifr_seen : false,
  rubi(x^7, x),
  check("top fold: a nested call's answer is not folded", t_ifr_seen, sin(%i*x+%i*a)),
  /* the caller's radexpand:true does not split the folded power */
  mr_rule_table : [hcot],
  t_ifr_r : rubi(x^7, x),
  check_bool("top fold: the folded power keeps its base at the caller",
             is(op(t_ifr_r) = "^") and is(part(t_ifr_r, 1) = -%i*coth(b*x+a))),
  check("top fold: the caller's flags are untouched", [radexpand, logexpand], [true, true]),
  /* an erroring fold returns the unfolded answer */
  mr_rule_table : [h7],
  t_ifr_r : block([], local(%mr_ifold), %mr_ifold(t_ifr_e) := error("ifold test"),
                  rubi(x^7, x)),
  check("top fold: a fold error returns the answer unfolded", t_ifr_r, sin(%i*x+%i*a)),
  check("top fold: %mr_ifold is restored after local", rubi(x^7, x), %i*sinh(x+a)),
  /* verbose matches: the answer folds, the steps keep the rules' form */
  rubi_verbose : 'matches,
  check("top fold: verbose folds the answer, keeps the steps",
        rubi(x^7, x),
        [%i*sinh(x+a), [["ifold r1", 'integrate(x^7, x), sin(%i*x+%i*a), []]]]),
  rubi_verbose : t_ifr_vb, mr_ifold : t_ifr_sw, mr_rule_table : t_ifr_saved,
  true
)$
```

and in `run_all_tests`, insert `test_ifold_top(),` right after `test_ifold_unit(),`.

Then, end to end through real rules: in `test_class4_e2e`, after the
`check("4.7.5 r5 (active cosh, pure-Sinh FunctionOfQ): ...")` line, add:

```maxima
    /* the %i fold (answer-quality 01): measured before the fold (2026-10-02)
       these three answered -(%i*((%i*x*cos(%i*b*x+%i*a))/b-sin(%i*b*x+%i*a)/b^2)),
       -((%i*cos(%i*b*x+%i*a)*sin(%i*b*x+%i*a))/(2*b))-x/2 and
       log(cos(%i*b*x+%i*a))/b */
    check("ifold e2e: Int x sinh(a+b x)", rubi(x*sinh(a+b*x), x),
          (x*cosh(b*x+a))/b-sinh(b*x+a)/b^2),
    check("ifold e2e: Int sinh(a+b x)^2", rubi(sinh(a+b*x)^2, x),
          (cosh(b*x+a)*sinh(b*x+a))/(2*b)-x/2),
    check("ifold e2e: Int tanh(a+b x)", rubi(tanh(a+b*x), x), log(cosh(b*x+a))/b),
    check("ifold e2e: mr_ifold false keeps the rules' form",
          block([mr_ifold : false], rubi(tanh(a+b*x), x)), log(cos(%i*b*x+%i*a))/b),
```

- [ ] **Step 2: Run it to verify it fails**

Run: `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null 2>&1 | grep -E "Results:|Lisp error|FAIL"`
Expected: FAIL on "the answer is folded", "rubi_fallback folds too", "the folded power keeps its base at the caller", "%mr_ifold is restored after local", "verbose folds the answer" and the three `ifold e2e: Int ...` checks (rubi answers unfolded today); the switch-off, nested, flags-untouched, error-fallback and `ifold e2e: mr_ifold false` checks already pass. `Results:` = previous total + 6 passed, 8 failed.

- [ ] **Step 3: Write the implementation.** In `maxima_rubi_utils.mac`, replace

```maxima
mr_top(%mr_top_f, x, %mr_top_fb) :=
  if depth_level = 0 and %mr_verbose_matches() then block([%mr_top_ans],
    %mr_take_steps(),
    %mr_top_ans : %mr_top_body(%mr_top_f, x, %mr_top_fb),
    [%mr_top_ans, %mr_take_steps()])
  else %mr_top_body(%mr_top_f, x, %mr_top_fb)$
```

with

```maxima
/* The top-level answer's last step: the %i fold (%mr_ifold above) under
   the run switch mr_ifold, with radexpand:false, logexpand:false bound
   here -- not by mr_model_flags: without them the fold is unsound. Inside
   errcatch, errormsg off: a fold that errors returns the answer unfolded,
   so the fold can never cost an answer. */
%mr_top_final(%mr_tf_ans) :=
  if mr_ifold # true then %mr_tf_ans
  else block([%mr_tf_r : block([errormsg : false],
                                errcatch(block([radexpand : false, logexpand : false],
                                               %mr_ifold(%mr_tf_ans))))],
    if %mr_tf_r = [] then %mr_tf_ans else first(%mr_tf_r))$

/* Under rubi_verbose : matches ... (keep the existing comment) */
mr_top(%mr_top_f, x, %mr_top_fb) :=
  if depth_level = 0 and %mr_verbose_matches() then block([%mr_top_ans],
    %mr_take_steps(),
    %mr_top_ans : %mr_top_body(%mr_top_f, x, %mr_top_fb),
    [%mr_top_final(%mr_top_ans), %mr_take_steps()])
  else if depth_level = 0 then %mr_top_final(%mr_top_body(%mr_top_f, x, %mr_top_fb))
  else %mr_top_body(%mr_top_f, x, %mr_top_fb)$
```

(The existing `/* Under rubi_verbose : matches ... */` comment stays directly above `mr_top`; add one sentence to it: "The depth-0 answer passes through %mr_top_final, the %i fold; the steps keep the rules' form.")

- [ ] **Step 4: Run it to verify it passes**

Run: `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null 2>&1 | grep -E "Results:|Lisp error|FAIL"`
Expected: `Results: <Task 2 total + 14> passed, 0 failed`, no `Lisp error`. If an OLDER check now fails because its expected answer carried an unfolded `%i` (the fold is on by default), do not weaken it: confirm with `radcan(new - old) = 0` that the value is unchanged, re-point the expected value to the folded form, and list each re-pointed check in the commit message.

- [ ] **Step 5: Run the gates**

```sh
maxima --very-quiet -b test/matcher/test_mr_dispatch.mac < /dev/null 2>&1 | grep -E "Results:|Lisp error"
maxima --very-quiet -b test/test_rule_table_order.mac < /dev/null 2>&1 | grep -E "Results:|Lisp error"
maxima --very-quiet -b test/test_section9_e2e.mac < /dev/null 2>&1 | grep -E "Results:|Lisp error"
maxima --very-quiet -b test/matcher/test_mr_match.mac < /dev/null 2>&1 | grep -E "Results:"
maxima --very-quiet -b test/matcher/test_mr_tree.mac < /dev/null 2>&1 | grep -E "Results:"
python3 test/test_run_records.py | tail -1
for t in test_driver_parens test_driver_core_pin test_driver_out_default test_driver_radcan_fallback \
         test_ab_records test_merge_classes test_record_medians test_driver_inert_leak \
         test_head_rewrites test_driver_proof test_merge_proof test_driver_baseline test_driver_grade; do
  printf '%s: ' $t; python3 test/$t.py | tail -1; done
maxima --very-quiet -b test/test_mr_verify.mac < /dev/null 2>&1 | grep Results:
maxima --very-quiet -b test/test_mr_grade.mac < /dev/null 2>&1 | grep Results:
```
Expected: dispatch at the Task 1 Step 5 figure (it exercises `rubi_verbose` through `mr_top`; its answers carry no `%i`); rule-table `18 passed, 0 failed`; section-9 e2e `9 passed, 0 failed` (if one of its answers now changes form it must still answer, carry no noun and verify — its checks are numeric, not exact); every other suite at its AGENTS.md figure, 0 failed; no `Lisp error` anywhere.

- [ ] **Step 6: Commit**

```bash
git add maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "utils: mr_top folds its depth-0 answer (%mr_top_final, answer-quality 01)"
```

---

### Task 4: `test/ab_grades.py` — the grade A/B

**Files:**
- Create: `test/ab_grades.py`
- Create: `test/test_ab_grades.py`
- Modify: `AGENTS.md` (the "Harness guards" list: add the guard line, as the section requires in the same commit)

**Interfaces:**
- Produces: `python3 test/ab_grades.py OLD.grade.out NEW.grade.out` — prints the grade transition table, every entry whose grade got worse (`WORSE <old> -> <new> <label>`), and ends `Results: <k> worse, <m> missing` (exit 1 when either is nonzero). Rank: `A` 0, `B` 1, `C` 2, `F`/`F(-1)`/`F(-2)` 3; ungraded `-` lines are skipped on both sides. Library: `read_grades(path) -> {label: grade}`.

- [ ] **Step 1: Write the failing test** — `test/test_ab_grades.py`:

```python
#!/usr/bin/env python3
"""Checks for test/ab_grades.py, the entry-level A/B of two grade sidecar
censuses (test/corpus_classN.grade.out). No Maxima; synthetic files.

Re-runnable:  python3 test/test_ab_grades.py
"""

import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test"))
import ab_grades  # noqa: E402

passed = failed = 0


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name} {detail}")


HEAD = ("=== maxima-rubi class6 grade census (24 sidecars merged) ===\n"
        "record: test/corpus_class6.out\n\n")
OLD = HEAD + ("C leaf=52/28 type=3/3 6 H/6.1.1 f.mac e1 L12\n"
              "A leaf=10/10 type=3/3 6 H/6.1.1 f.mac e2 L13\n"
              "B leaf=30/10 type=3/3 6 H/6.1.1 f.mac e3 L14\n"
              "- leaf=-/- type=-/- 6 H/6.1.1 f.mac e4 L15\n"
              "F(-1) leaf=-/17 type=-/1 6 H/6.1.1 f.mac e5 L16\n"
              "     A  4,055  79.8 %\n")
NEW = HEAD + ("A leaf=28/28 type=3/3 6 H/6.1.1 f.mac e1 L12\n"
              "B leaf=30/10 type=3/3 6 H/6.1.1 f.mac e2 L13\n"
              "B leaf=30/10 type=3/3 6 H/6.1.1 f.mac e3 L14\n"
              "A leaf=9/9 type=3/3 6 H/6.1.1 f.mac e4 L15\n"
              "F(-1) leaf=-/17 type=-/1 6 H/6.1.1 f.mac e5 L16\n")


def main():
    with tempfile.TemporaryDirectory() as d:
        o, n = os.path.join(d, "old.grade.out"), os.path.join(d, "new.grade.out")
        open(o, "w").write(OLD)
        open(n, "w").write(NEW)
        g = ab_grades.read_grades(o)
        check("entry lines parse, census and header lines skipped",
              g == {"6 H/6.1.1 f.mac e1 L12": "C", "6 H/6.1.1 f.mac e2 L13": "A",
                    "6 H/6.1.1 f.mac e3 L14": "B", "6 H/6.1.1 f.mac e4 L15": "-",
                    "6 H/6.1.1 f.mac e5 L16": "F(-1)"}, str(g))
        check("rank: A < B < C < F family",
              [ab_grades.RANK[x] for x in ("A", "B", "C", "F", "F(-1)", "F(-2)")]
              == [0, 1, 2, 3, 3, 3])
        p = subprocess.run([sys.executable, os.path.join(ROOT, "test", "ab_grades.py"), o, n],
                           capture_output=True, text=True)
        out = p.stdout
        check("the worse entry is listed", "WORSE A -> B 6 H/6.1.1 f.mac e2 L13" in out, out)
        check("a better entry is not listed as worse", "e1 L12" not in
              "".join(l for l in out.splitlines(True) if l.startswith("WORSE")), out)
        check("an ungraded side is skipped, not worse", "e4 L15" not in
              "".join(l for l in out.splitlines(True) if l.startswith("WORSE")), out)
        check("the transition table counts C->A", "C -> A: 1" in out, out)
        check("Results line and exit code", "Results: 1 worse, 0 missing" in out
              and p.returncode == 1, f"{out} rc={p.returncode}")
        open(n, "w").write(NEW.replace("A leaf=28/28 type=3/3 6 H/6.1.1 f.mac e1 L12\n", ""))
        p = subprocess.run([sys.executable, os.path.join(ROOT, "test", "ab_grades.py"), o, n],
                           capture_output=True, text=True)
        check("an entry missing from NEW is counted", "Results: 1 worse, 1 missing" in p.stdout,
              p.stdout)
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 test/test_ab_grades.py`
Expected: `ModuleNotFoundError: No module named 'ab_grades'`.

- [ ] **Step 3: Write `test/ab_grades.py`:**

```python
#!/usr/bin/env python3
"""Entry-level A/B of two grade censuses (test/merge_grade.py output,
test/corpus_classN.grade.out): the grade transition table and every entry
whose grade got WORSE (A -> B/C/F, B -> C/F, C -> F). Ungraded entries
(`-`, an optimal that failed to evaluate) are skipped on either side.

    python3 test/ab_grades.py OLD.grade.out NEW.grade.out

Ends `Results: <k> worse, <m> missing` (an entry graded in OLD and absent
from NEW is missing); exit 1 when either is nonzero. The record A/B of the
same two runs is test/ab_records.py.
"""

import re
import sys

RANK = {"A": 0, "B": 1, "C": 2, "F": 3, "F(-1)": 3, "F(-2)": 3}
LINE_RE = re.compile(r"^(A|B|C|F|F\(-1\)|F\(-2\)|-) leaf=\S+ type=\S+ (.+?)\s*$")


def read_grades(path):
    grades = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = LINE_RE.match(line)
            if m:
                grades[m.group(2)] = m.group(1)
    return grades


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    old, new = read_grades(argv[1]), read_grades(argv[2])
    trans, worse, missing = {}, [], 0
    for label, g0 in old.items():
        if g0 == "-":
            continue
        g1 = new.get(label)
        if g1 is None:
            missing += 1
            print(f"MISSING {g0} {label}")
            continue
        if g1 == "-":
            continue
        trans[(g0, g1)] = trans.get((g0, g1), 0) + 1
        if RANK[g1] > RANK[g0]:
            worse.append((g0, g1, label))
    print(f"# {argv[1]} -> {argv[2]}: {sum(trans.values())} entries graded in both")
    for (g0, g1), k in sorted(trans.items(), key=lambda kv: (RANK[kv[0][0]], kv[0][0], RANK[kv[0][1]], kv[0][1])):
        print(f"{g0} -> {g1}: {k}")
    for g0, g1, label in worse:
        print(f"WORSE {g0} -> {g1} {label}")
    print(f"Results: {len(worse)} worse, {missing} missing")
    return 1 if worse or missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Run it to verify it passes**

Run: `python3 test/test_ab_grades.py`
Expected: `Results: 8 passed, 0 failed`. Then a smoke on real data: `python3 test/ab_grades.py test/corpus_class2.grade.out test/corpus_class2.grade.out | tail -1` -> `Results: 0 worse, 0 missing`.

- [ ] **Step 5: List the guard.** In `AGENTS.md`, in the **Harness guards** code block, after the `test_driver_grade.py` line, add:

```
python3 test/test_ab_grades.py              # Results: 8 passed, 0 failed
```

- [ ] **Step 6: Commit**

```bash
git add test/ab_grades.py test/test_ab_grades.py AGENTS.md
git commit -m "test: ab_grades, the entry-level A/B of two grade censuses"
```

---

### Task 5: Acceptance — every section re-run and graded

**Files:**
- Create: `.scratch/answer-quality/ifold_measure.sh`
- Output (overwritten by the run): `test/corpus_class{0..8}.out`, `.proof.out`, `.grade.out` (the rubi arm; the baseline records are not touched)
- Output: `.scratch/answer-quality/ifold_ab/` (the old records and the A/B reports)

**Interfaces:**
- Consumes: `test/run_corpus_queue.py`, `test/wait_and_merge.sh`, the mergers (`merge_class_shards.py`, `merge_proof.py`, `merge_grade.py`), `test/ab_records.py`, `test/ab_grades.py` (Task 4).

- [ ] **Step 1: Write the run script** — `.scratch/answer-quality/ifold_measure.sh`. It runs the RUBI arm only, the way `test/graded_measure.sh`'s `run_arm` does (that script decides "keep" by file mtimes, which a git checkout leaves arbitrary, and would also re-run the baseline arm):

```sh
#!/bin/sh
# The %i fold's acceptance run (plan docs/superpowers/plans/2026-10-02-ifold-answer.md
# Task 5): every section's rubi arm re-run and graded at HEAD, then the
# record A/B and the grade A/B against the records of BASE.
#   setsid sh .scratch/answer-quality/ifold_measure.sh > .scratch/answer-quality/ifold_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/../.." || exit 1
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 3 ]; then echo "REFUSING: 1-minute load $LOAD1 > 3"; exit 3; fi
BASE=$(git log -1 --format=%h -- test/corpus_class6.grade.out)   # the records being replaced
AB=.scratch/answer-quality/ifold_ab
mkdir -p "$AB"
echo "$(date '+%F %T %Z') base records at $BASE, tree $(git rev-parse --short HEAD), $(git status --porcelain | wc -l) uncommitted paths"
sh test/build_rules_core.sh || exit 4
for section in "0 Independent test suites" "2 Exponentials" "8 Special functions" \
    "3 Logarithms" "5 Inverse trig functions" "6 Hyperbolic functions" \
    "7 Inverse hyperbolic functions" "4 Trig functions" "1 Algebraic functions"; do
  n=$(echo "$section" | cut -d' ' -f1); slug="class$n"; out="test/corpus_$slug.out"
  git show "$BASE:$out" > "$AB/old_$slug.out"
  git show "$BASE:test/corpus_$slug.grade.out" > "$AB/old_$slug.grade.out"
  echo "$(date '+%F %T %Z') start rubi $section"
  python3 test/run_corpus_queue.py "$section" --prev "$AB/old_$slug.out" --workers 24 --launch || { echo "LAUNCH FAILED $section"; continue; }
  sh test/wait_and_merge.sh "test/corpus_$slug.shard-pids" test/merge_class_shards.py \
     "test/ifold_merge_$slug.out" "$section" "$out" test/corpus_driver.py "corpus_$slug.shard*.out" || { echo "MERGE FAILED $section"; continue; }
  python3 test/merge_proof.py "$out" "test/corpus_$slug.proof.out" "corpus_$slug.shard*.proof" || echo "PROOF MERGE FAILED $section"
  python3 test/merge_grade.py "$out" "test/corpus_$slug.grade.out" "corpus_$slug.shard*.grade" || echo "GRADE MERGE FAILED $section"
  python3 test/ab_records.py "$AB/old_$slug.out" "$out" > "$AB/ab_records_$slug.txt" 2>&1
  python3 test/ab_grades.py "$AB/old_$slug.grade.out" "test/corpus_$slug.grade.out" > "$AB/ab_grades_$slug.txt" 2>&1
  echo "$(date '+%F %T %Z') done $section: $(grep -m1 'Results:' "$out") | $(tail -1 "$AB/ab_grades_$slug.txt")"
done
echo "$(date '+%F %T %Z') IFOLD MEASURE DONE"
```

- [ ] **Step 2: Launch it detached** (the script refuses above a 1-minute load of 3 and rebuilds the rules core itself):

```sh
setsid sh .scratch/answer-quality/ifold_measure.sh > .scratch/answer-quality/ifold_measure.log 2>&1 < /dev/null &
```
Expected wall: about 3 h (the 2026-09-30 rubi arm: section 1 64 min, section 4 78 min, the rest under 10 min each). Wait on the log's `IFOLD MEASURE DONE` line with a background waiter that re-arms past the 2 h cap; do not `pgrep -f` a pattern from inside the waiter.

- [ ] **Step 3: Read the record A/Bs.** For each section: `grep -A6 "2x2\|PASS->FAIL" .scratch/answer-quality/ifold_ab/ab_records_class$n.txt`.
Expected: the key-set check passes; **PASS -> FAIL only** the 9 attributed section-6 entries (6.4.2 e14/e22/e26/e47, 6.7.1 e57/e58/e64/e65/e66). Any other PASS -> FAIL must be attributed before acceptance. Put those entries' lines from the NEW record into a file with their class word set to `recheck` (e.g. `sed -E 's/^[a-z-]+ /recheck /'`) and re-run them in both arms with the queue's subset mode:

```sh
MR_SWITCHES="mr_ifold=false" python3 test/run_corpus_queue.py "<SECTION>" --entries-from <file> --class recheck --out-dir .scratch/answer-quality/ifold_ab/recheck_off --workers 12 --launch
python3 test/run_corpus_queue.py "<SECTION>" --entries-from <file> --class recheck --out-dir .scratch/answer-quality/ifold_ab/recheck_on --workers 12 --launch
```
A FAIL that also occurs with `mr_ifold=false` is run noise (a 30 s-cap borderline); one that occurs only with the fold is the fold's and blocks acceptance — stop and report.

- [ ] **Step 4: Read the grade A/Bs.** `tail -3 .scratch/answer-quality/ifold_ab/ab_grades_class*.txt` and every `WORSE` line.
Expected: section 6 `C -> A` about 1,500; **no `WORSE` line attributable to the fold**. A WORSE entry is attributed the same way as Step 3 (the two subset re-runs; their shards' `.grade` sidecars hold the grade under each arm; a C/F caused by a changed verdict — e.g. a timeout — that also occurs with the switch off is noise).

- [ ] **Step 5: Regenerate the report**

Run: `python3 test/grade_report.py 0 1 2 3 4 5 6 7 8 > test/grade_report.out` and read its headline (rubi A %, solved %).

- [ ] **Step 6: Commit the records**

```bash
git add test/corpus_class[0-8].out test/corpus_class[0-8].proof.out test/corpus_class[0-8].grade.out test/grade_report.out
git add .scratch/answer-quality/ifold_measure.sh
git commit -m "records: every section re-run with the %i fold (mr_ifold true)"
```
Check `git show --stat HEAD`: only these paths (a glob that also matches gitignored shard files prints an "ignored" list but stages the rest).

---

### Task 6: Docs, ticket, follow-up

**Files:**
- Modify: `docs/grading-and-leaf-size.md` (the figures and a paragraph on the fold)
- Modify: `AGENTS.md` (Layer A's new `Results:` figure and how it grew; `test_run_records` unchanged at 43; `mr_ifold` named among the run switches in the **Switch arm** paragraph)
- Modify: `.scratch/answer-quality/issues/01-hyperbolic-answers-keep-i.md` (Status: closed; an acceptance comment)
- Create: `.scratch/answer-quality/issues/02-remaining-i-after-fold.md`

- [ ] **Step 1: Update `docs/grading-and-leaf-size.md`.** Replace every rubi figure the new `test/grade_report.out` changes (headline A % and solved %, the per-section table, section 6's C count, the "native grades better" count) with the new values, each stamped with the date and build, and add a short section "The %i fold (2026-10-02)": mechanism (one paragraph, citing the spec), the switch, and the measured effect (probe 05 and the acceptance A/B, citing `.scratch/answer-quality/ifold_ab/`).

- [ ] **Step 2: Update `AGENTS.md`.** In the Layer A paragraph append "; with the %i fold of the top-level answer (`%mr_ifold`, `%mr_top_final`, answer-quality 01, <k> checks): **`Results: <n> passed, 0 failed`**" using the figure from Task 3 Step 4; in the **Switch arm** paragraph add one sentence: "`mr_ifold` (default true, 2026-10-02) folds `%i` out of the top-level answer (`.scratch/answer-quality/issues/01`); false reproduces the earlier answers."

- [ ] **Step 3: Close the ticket** — set `Status: closed` and add a `### 2026-10-0x -- accepted` comment with the per-section PASS/FAIL and grade transitions from the Task 5 logs, the 9 attributed entries, and the commits.

- [ ] **Step 4: File the follow-up** — `.scratch/answer-quality/issues/02-remaining-i-after-fold.md`, `Status: needs-triage`: the section-6 answers still graded C after the fold (count from `ab_grades_class6.txt`'s `C -> C`), with 6.3.7 e56's `log(tan(%i*d*x+%i*c))`-type `%i` that cancels only across a log as the named example, and probe 05's `C->C` lines as the list.

- [ ] **Step 5: Commit**

```bash
git add docs/grading-and-leaf-size.md AGENTS.md .scratch/answer-quality/issues/01-hyperbolic-answers-keep-i.md .scratch/answer-quality/issues/02-remaining-i-after-fold.md
git commit -m "docs+issues: the %i fold accepted; follow-up for the remaining C's"
```
