# RemoveContent folds %i out of its argument — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `%mr_removeContent` folds `%i` out of its argument before stripping the content, so `log(%i*sinh(u))` answers become `log(sinh(u))`, gated by the existing run switch `mr_ifold`, and every section is re-measured.

**Architecture:** the guarded fold `%mr_top_final` already applies to the depth-0 answer (switch check, `radexpand:false, logexpand:false`, `errcatch`) is factored into one helper `%mr_ifold_safe(e)` in `maxima_rubi_utils.mac`; `%mr_top_final` and `%mr_removeContent` both call it. Nothing else in RemoveContent changes. RemoveContent's value only ever lands inside a `log` (all 25 rule call sites are `log(%mr_removeContent(..))`), so the fold cannot change which rules match.

**Tech Stack:** Maxima (build `branch_5_50_base_84_g4204fb669`, SBCL 2.6.7), Python 3 harness.

**Spec:** `docs/superpowers/specs/2026-10-03-removecontent-ifold-design.md` (read it first; it cites the traces and probe 09). Ticket: `.scratch/answer-quality/issues/02-remaining-i-after-fold.md`. Background: the depth-0 fold's spec `docs/superpowers/specs/2026-10-02-ifold-answer-design.md`.

## Global Constraints

- **Switch: `mr_ifold`** (user decision 2026-10-03). No new switch. `mr_ifold : false` turns off both folds and reproduces the earlier answers.
- The fold always runs under `radexpand : false, logexpand : false`, bound by the helper itself (under Maxima's defaults the fold is unsound: `(-%i*y)^(2/3)` -> `-y^(2/3)`).
- The fold can never cost an answer: an error inside it returns its input unchanged (`errcatch`, `errormsg : false`).
- One helper for both callers — `%mr_top_final` and `%mr_removeContent` must not carry two copies of the wrapper.
- `%mr_removeContentAux`, `%mr_nonfreeFactors`, `%mr_freeFactors`, `%mr_together` are not touched; no rule file changes.
- Locals in Maxima functions are prefixed (`%mr_is_` for the helper, `%mr_rc_` in RemoveContent) — the project's capture-trap convention.
- Commits: no `Co-Authored-By` and no `Claude-Session:` trailers (AGENTS.md). Do not push.
- Test reading protocol (AGENTS.md "Tests"): read the `Results:` line, grep the output for `Lisp error`, and compare the PASS count with the expected figure.
- Maxima runs: redirect stdin from `/dev/null`.
- Work on a branch `rcfold` off `master` (Task 1 Step 1); `master` is merged into only after Task 4.

## Review Focus

- **The caller's `radexpand : true`** — Layer A and user sessions run with Maxima's defaults; the helper must bind its own flags and leave the caller's untouched (pinned in Task 1: the `cot(..)^(1/3)` folded base and the flags-untouched check).
- **A fold that errors inside RemoveContent** — the rule must still get the old RemoveContent value, not an error (pinned in Task 1 with a `local`-redefined `%mr_ifold`).
- **An `%i`-free argument** — the overwhelmingly common case (every class-1 call); must be returned exactly as before (pinned in Task 1: `3*(x+1)` and `sin(b*x+a)`).
- **`mr_ifold : false`** — both folds off; RemoveContent must answer the shipped value (pinned in Task 1: two switch-off checks, and the existing `test_ifold_top` switch check guards `%mr_top_final`).
- **The depth-0 fold after the refactor** — `%mr_top_final` must behave byte for byte as before (pinned by the existing `test_ifold_unit` / `test_ifold_top` checks staying green; Task 1 runs them).

---

### Task 1: `%mr_ifold_safe` and RemoveContent's fold

**Files:**
- Modify: `maxima_rubi_utils.mac:298-308` (the comment and body of `%mr_top_final`) — add `%mr_ifold_safe` above it, make `%mr_top_final` call it
- Modify: `maxima_rubi_utils.mac:2557-2561` (`%mr_removeContent`) and the family comment above it (`:2413-2416`)
- Test: `test_maxima_rubi.mac` — a new `test_removecontent_ifold()` defined right after `test_ifold_unit()` (ends near line 6038), and called from `run_all_tests` right after `test_ifold_unit(),` (line 170)

**Interfaces:**
- Consumes: `%mr_ifold(e)` (`maxima_rubi_utils.mac:281`, unchanged), the run switch `mr_ifold` (`maxima_rubi_dispatch.lisp`, `defmvar $mr_ifold`, default true).
- Produces: `%mr_ifold_safe(e)` — returns `e` when `mr_ifold # true`; else `%mr_ifold(e)` under `radexpand:false, logexpand:false` inside `errcatch` with `errormsg:false`, and `e` itself if that errors. `%mr_top_final(ans)` keeps its name and meaning (`mr_top` calls it).

- [ ] **Step 1: Branch**

```bash
git checkout -b rcfold master
```

- [ ] **Step 2: Write the failing tests.** In `test_maxima_rubi.mac`, right after the closing `)$` of `test_ifold_unit()` (the block that ends with the `radexpand : true` hazard check, near line 6038), add:

```maxima
/* RemoveContent folds %i out of its argument (answer-quality 02; spec
   docs/superpowers/specs/2026-10-03-removecontent-ifold-design.md).
   4_3_1_1 r3 builds log(RemoveContent(cos(%i*b*x+%i*a+%pi/2))); Mathematica
   evaluates the argument to -I Sinh[a+b x] before RemoveContent strips -I.
   Measured 2026-10-03 (probe 09's redefinition): both arguments below give
   sinh(b*x+a); shipped, sin(%i*b*x+%i*a). */
test_removecontent_ifold() := block([t_rc_sw, t_rc_r],
  print("--- the %i fold: RemoveContent's argument ---"),
  t_rc_sw : mr_ifold,
  mr_ifold : true,
  check("rc fold: sin of an imaginary sum",
        %mr_removeContent(sin(%i*b*x+%i*a), x), sinh(b*x+a)),
  check("rc fold: 4_3_1_1 r3's Pi/2-shifted cos",
        %mr_removeContent(cos(%i*b*x+%i*a+%pi/2), x), sinh(b*x+a)),
  check("rc fold: an %i-free argument, content stripped",
        %mr_removeContent(3*(x+1), x), x+1),
  check_bool("rc fold: an %i-free function is returned unchanged",
             is(%mr_removeContent(sin(b*x+a), x) = sin(b*x+a))),
  /* the switch off: the shipped value */
  check("rc fold: mr_ifold false, sin",
        block([mr_ifold : false], %mr_removeContent(sin(%i*b*x+%i*a), x)),
        sin(%i*b*x+%i*a)),
  check("rc fold: mr_ifold false, Pi/2-shifted cos",
        block([mr_ifold : false], %mr_removeContent(cos(%i*b*x+%i*a+%pi/2), x)),
        sin(%i*b*x+%i*a)),
  /* an erroring fold leaves RemoveContent's old value */
  t_rc_r : block([], local(%mr_ifold), %mr_ifold(t_rc_e) := error("rc fold test"),
                 %mr_removeContent(sin(%i*b*x+%i*a), x)),
  check("rc fold: a fold error gives the unfolded value", t_rc_r, sin(%i*b*x+%i*a)),
  /* the helper binds its own flags: the caller's radexpand:true neither
     splits the folded power nor is changed */
  t_rc_r : block([radexpand : true], %mr_ifold_safe(cot(%i*b*x+%i*a)^(1/3))),
  check_bool("rc fold: the helper keeps the folded power's base",
             is(op(t_rc_r) = "^") and is(part(t_rc_r, 1) = -%i*coth(b*x+a))),
  check("rc fold: the caller's flags are untouched", [radexpand, logexpand], [true, true]),
  check("rc fold: the helper with mr_ifold false is the identity",
        block([mr_ifold : false], %mr_ifold_safe(sin(%i*b*x+%i*a))), sin(%i*b*x+%i*a)),
  mr_ifold : t_rc_sw,
  true
)$
```

and in `run_all_tests`, after the line `  test_ifold_unit(),` add the line `  test_removecontent_ifold(),`.

- [ ] **Step 3: Run Layer A to verify the new checks fail**

Run: `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null > /tmp/la.out 2>&1; grep -E "rc fold|Results:|Lisp error" /tmp/la.out`
Expected: 4 `FAIL`s — "sin of an imaginary sum" and "Pi/2-shifted cos" (actual `sin(%i*b*x+%i*a)`), "the helper keeps the folded power's base" and "the helper with mr_ifold false is the identity" (`%mr_ifold_safe` does not exist yet, so the call stays unevaluated). The other 6 new checks PASS already (the `%i`-free, switch-off and error checks read the shipped value; the flags check holds trivially). `Results: 1694 passed, 4 failed` (1688 + 6), no `Lisp error` — if the figures differ, stop and recount before going on.

- [ ] **Step 4: Implement the helper.** In `maxima_rubi_utils.mac` replace the comment-and-definition of `%mr_top_final` (from `/* The top-level answer's last step:` through the `if %mr_tf_r = [] then %mr_tf_ans else first(%mr_tf_r))$` line) with:

```maxima
/* The guarded %i fold: %mr_ifold above under the run switch mr_ifold, with
   radexpand:false, logexpand:false bound here -- not by mr_model_flags:
   without them the fold is unsound. Inside errcatch, errormsg off: a fold
   that errors returns its input unfolded, so the fold can never cost an
   answer. Two callers: the depth-0 answer (%mr_top_final) and
   RemoveContent's argument (%mr_removeContent, answer-quality 02, spec
   docs/superpowers/specs/2026-10-03-removecontent-ifold-design.md). */
%mr_ifold_safe(%mr_is_e) :=
  if mr_ifold # true then %mr_is_e
  else block([%mr_is_r : block([errormsg : false],
                                errcatch(block([radexpand : false, logexpand : false],
                                               %mr_ifold(%mr_is_e))))],
    if %mr_is_r = [] then %mr_is_e else first(%mr_is_r))$

/* The top-level answer's last step: the guarded %i fold. */
%mr_top_final(%mr_tf_ans) := %mr_ifold_safe(%mr_tf_ans)$
```

- [ ] **Step 5: Implement RemoveContent's fold.** Replace `%mr_removeContent` (`maxima_rubi_utils.mac`, the five lines from `%mr_removeContent(u, x) := block([v, w],`) with:

```maxima
%mr_removeContent(u, x) := block([v, w, %mr_rc_u : %mr_ifold_safe(u)],
  v : %mr_nonfreeFactors(%mr_rc_u, x),
  w : %mr_together(v),
  if %mr_eqQ(%mr_freeFactors(w, x), 1) then %mr_removeContentAux(v, x)
  else %mr_removeContentAux(%mr_nonfreeFactors(w, x), x))$
```

and extend the family comment above `%mr_nonfreeFactors` — after its line ` *   else Aux[NonfreeFactors[w,x],x] */` add:

```maxima
/* RemoveContent's argument is %i-folded first (%mr_ifold_safe, under the
   run switch mr_ifold): Mathematica evaluates it before RemoveContent sees
   it -- 4_3_1_1 r3's Cos[I a + I b x + Pi/2] arrives as -I Sinh[a + b x]
   and the content -I is stripped -- while Maxima keeps sin(%i*b*x+%i*a),
   and the depth-0 fold then left log(%i*sinh(b*x+a)) (answer-quality 02,
   probes/leaf-size/09: 34 of 50 such answers cleared). Safe for matching:
   every rule call site is log(%mr_removeContent(..)), an answer term. */
```

- [ ] **Step 6: Run Layer A to verify everything passes**

Run: `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null > /tmp/la.out 2>&1; grep -E "FAIL|Results:|Lisp error" /tmp/la.out`
Expected: no `FAIL`, no `Lisp error`, `Results: 1698 passed, 0 failed`. The pre-existing `ifold:` and `top fold:` checks (in `test_ifold_unit` / `test_ifold_top`) must all still PASS — they pin `%mr_top_final`'s behaviour across the refactor.

- [ ] **Step 7: Run the real-table gates**

```sh
maxima --very-quiet -b test/test_rule_table_order.mac < /dev/null 2>&1 | grep -E "Results:|Lisp error"
maxima --very-quiet -b test/test_section9_e2e.mac < /dev/null 2>&1 | grep -E "Results:|Lisp error"
```
Expected: `Results: 18 passed, 0 failed` and `Results: 9 passed, 0 failed`, no `Lisp error`.

- [ ] **Step 8: Commit**

```bash
git add maxima_rubi_utils.mac test_maxima_rubi.mac
git commit -m "utils: RemoveContent folds %i out of its argument (%mr_ifold_safe, answer-quality 02)"
```

---

### Task 2: End to end — 6.1.1 e30 through the class-4 table

**Files:**
- Test: `test_maxima_rubi.mac`, `test_class4_e2e()` — after the four `ifold e2e:` checks (near line 5406)

**Interfaces:**
- Consumes: Task 1's `%mr_removeContent`; `test_class4_e2e`'s sibling table (it loads `1_1_1_1`, `1_4_1`, `9_1` and every class-4 file — e30's traced path is `4_1_0_1 r1`, `9_1 r10`, `4_5_10 r5`, `4_1_0_1 r1`, `9_1 r10`, `4_3_1_1 r3`) and its helpers `mr_c4e_clean(r)` / `mr_c4e_num(r, f)` (numeric derivative check at x = 0.3, 0.7 with a = 3, b = 2; c and d stay symbolic, so pass f with c, d substituted too — see below).

- [ ] **Step 1: Write the test.** After the line `block([mr_ifold : false], rubi(tanh(a+b*x), x)), log(cos(%i*b*x+%i*a))/b),` add:

```maxima
    /* RemoveContent's fold (answer-quality 02): 6.1.1 e30. Measured on the
       full table 2026-10-03 (probe 07/09): shipped
       (d*log(%i*sinh(b*x+a)))/b^2+((-(d*x)-c)*coth(b*x+a))/b, with the
       fold Rubi's optimal below. */
    mr_c4e_r : rubi((c+d*x)*csch(a+b*x)^2, x),
    check("rc fold e2e: 6.1.1 e30 Int (c+d x) csch(a+b x)^2",
          mr_c4e_r, (d*log(sinh(b*x+a)))/b^2+((-(d*x)-c)*coth(b*x+a))/b),
    check_bool("rc fold e2e: 6.1.1 e30 differentiates to the integrand",
               mr_c4e_clean(mr_c4e_r)
               and mr_c4e_num(subst([c = 5, d = 7], mr_c4e_r),
                              subst([c = 5, d = 7], (c+d*x)*csch(a+b*x)^2))),
```

- [ ] **Step 2: Run Layer A**

Run: `maxima --very-quiet -b test_maxima_rubi.mac < /dev/null > /tmp/la.out 2>&1; grep -E "FAIL|rc fold e2e|Results:|Lisp error" /tmp/la.out`
Expected: both `rc fold e2e` checks PASS, `Results: 1700 passed, 0 failed`, no `Lisp error`.
The first check is a real witness without a separate RED run: the shipped answer (probe 07, recorded in the comment above it) carries `log(%i*sinh(b*x+a))` and differs from the expected value. If the actual with the fold is NOT the expected value but is `%i`-free and the second check passes, the class-4 sibling table reaches a different but equivalent form: stop and report the actual value rather than editing the expectation silently.

- [ ] **Step 3: Commit**

```bash
git add test_maxima_rubi.mac
git commit -m "test: RemoveContent's fold end to end, 6.1.1 e30 on the class-4 table"
```

---

### Task 3: Acceptance — every section re-run and graded

**Files:**
- Create: `.scratch/answer-quality/rcfold_measure.sh`
- Output (overwritten by the run): `test/corpus_class{0..8}.out`, `.proof.out`, `.grade.out` (the rubi arm; the baseline records are not touched)
- Output: `.scratch/answer-quality/rcfold_ab/` (the old records and the A/B reports)

**Interfaces:**
- Consumes: `test/run_corpus_queue.py`, `test/wait_and_merge.sh`, `test/merge_class_shards.py`, `test/merge_proof.py`, `test/merge_grade.py`, `test/ab_records.py`, `test/ab_grades.py`, `test/grade_report.py`, `probes/leaf-size/07-remaining-i-answers.py`.

- [ ] **Step 1: Write the run script** `.scratch/answer-quality/rcfold_measure.sh` (the depth-0 fold's `ifold_measure.sh` with its names changed; BASE is the tree's HEAD, whose records are the ones being replaced — this branch does not touch them before this task):

```sh
#!/bin/sh
# RemoveContent's %i fold, acceptance run (plan
# docs/superpowers/plans/2026-10-03-removecontent-ifold.md Task 3): every
# section's rubi arm re-run and graded at HEAD, then the record A/B and the
# grade A/B against the records of BASE.
#   setsid sh .scratch/answer-quality/rcfold_measure.sh > .scratch/answer-quality/rcfold_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/../.." || exit 1
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 3 ]; then echo "REFUSING: 1-minute load $LOAD1 > 3"; exit 3; fi
BASE=$(git rev-parse --short HEAD)
AB=.scratch/answer-quality/rcfold_ab
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
     "test/rcfold_merge_$slug.out" "$section" "$out" test/corpus_driver.py "corpus_$slug.shard*.out" || { echo "MERGE FAILED $section"; continue; }
  python3 test/merge_proof.py "$out" "test/corpus_$slug.proof.out" "corpus_$slug.shard*.proof" || echo "PROOF MERGE FAILED $section"
  python3 test/merge_grade.py "$out" "test/corpus_$slug.grade.out" "corpus_$slug.shard*.grade" || echo "GRADE MERGE FAILED $section"
  python3 test/ab_records.py "$AB/old_$slug.out" "$out" > "$AB/ab_records_$slug.txt" 2>&1
  python3 test/ab_grades.py "$AB/old_$slug.grade.out" "test/corpus_$slug.grade.out" > "$AB/ab_grades_$slug.txt" 2>&1
  echo "$(date '+%F %T %Z') done $section: $(grep -m1 'Results:' "$out") | $(tail -1 "$AB/ab_grades_$slug.txt")"
done
echo "$(date '+%F %T %Z') RCFOLD MEASURE DONE"
```

- [ ] **Step 2: Launch it detached** (it refuses above a 1-minute load of 3 and rebuilds the rules core itself):

```sh
setsid sh .scratch/answer-quality/rcfold_measure.sh > .scratch/answer-quality/rcfold_measure.log 2>&1 < /dev/null &
```
Expected wall: about 3 h (the 2026-10-02 run of the same script shape). Wait on the log's `RCFOLD MEASURE DONE` line with a background waiter on the file (a `while ! grep -q ...; do sleep 60; done` loop), re-armed past the 2 h background cap; never `pgrep -f` a pattern from inside the waiter.

- [ ] **Step 3: Read the record A/Bs.** For each section: `grep -A6 "2x2\|PASS->FAIL" .scratch/answer-quality/rcfold_ab/ab_records_class$n.txt`.
Expected: the key-set check passes; **no PASS -> FAIL attributable to the change**. Known borderline: section 4's four entries at the 30 s cap (2026-10-03 handoff: verified at 29.7-29.9 s before the depth-0 fold). Every PASS -> FAIL is attributed: put those entries' lines from the NEW record into a file with their class word set to `recheck` (`sed -E 's/^[a-z-]+ /recheck /'`) and re-run them in both arms:

```sh
MR_SWITCHES="mr_ifold=false" python3 test/run_corpus_queue.py "<SECTION>" --entries-from <file> --class recheck --out-dir .scratch/answer-quality/rcfold_ab/recheck_off --workers 12 --launch
python3 test/run_corpus_queue.py "<SECTION>" --entries-from <file> --class recheck --out-dir .scratch/answer-quality/rcfold_ab/recheck_on --workers 12 --launch
```
(the `mr_ifold=false` arm turns off both folds; a FAIL that also occurs there or that is a 30 s-cap timeout in both arms is noise. For an entry that fails only with the fold on, check whether it was already FAIL under the depth-0 fold's records — `git show 8d1cb88:test/corpus_class<N>.out` — before blaming RemoveContent.) A FAIL caused by this change blocks acceptance — stop and report.

- [ ] **Step 4: Read the grade A/Bs.** `tail -3 .scratch/answer-quality/rcfold_ab/ab_grades_class*.txt` and every `WORSE` line.
Expected: section 6 `C -> A` (or `C -> B`) about 34 (probe 09); a few more possible outside section 6 (probe 09 only looked at section 6); **no `WORSE` line attributable to the change**, attributed as in Step 3 (the re-run shards' `.grade` sidecars hold each arm's grade).

- [ ] **Step 5: Re-run probe 07 on the remaining C's**

```sh
setsid python3 probes/leaf-size/07-remaining-i-answers.py > probes/leaf-size/07-remaining-i-answers.out 2> /dev/null < /dev/null &
```
Wait for its `## ` line count to equal the header's entry count (`grep -c '^## '`), then re-run probe 08:
`maxima --very-quiet -b probes/leaf-size/08-classify-remaining-i.mac < /dev/null > probes/leaf-size/08-classify-remaining-i.out`
and read its census.

- [ ] **Step 6: Regenerate the report**

Run: `python3 test/grade_report.py 0 1 2 3 4 5 6 7 8 > test/grade_report.out` and read its headline (rubi A %, solved %).

- [ ] **Step 7: Commit the records**

```bash
git add test/corpus_class[0-8].out test/corpus_class[0-8].proof.out test/corpus_class[0-8].grade.out test/grade_report.out
git add .scratch/answer-quality/rcfold_measure.sh probes/leaf-size/07-remaining-i-answers.out probes/leaf-size/08-classify-remaining-i.out
git commit -m "records: every section re-run with RemoveContent's %i fold"
```
Check `git show --stat HEAD`: only these paths.

---

### Task 4: Docs, tickets, merge

**Files:**
- Modify: `AGENTS.md` (Layer A's figure; the **Switch arm** sentence on `mr_ifold`)
- Modify: `docs/grading-and-leaf-size.md` (the rubi figures the new report changes; one paragraph on RemoveContent's fold)
- Modify: `.scratch/answer-quality/issues/02-remaining-i-after-fold.md` (triage correction, acceptance comment)
- Create: `.scratch/answer-quality/issues/03-port-simplifyantiderivative.md`

- [ ] **Step 1: `AGENTS.md`.** In the Layer A paragraph, after "...(`%mr_ifold`, `%mr_top_final`, `.scratch/answer-quality/issues/01`, 2026-10-02, 30 checks): **`Results: 1688 passed, 0 failed`**", turn that bold figure into plain text and append "; with RemoveContent's %i fold (`%mr_ifold_safe`, `.scratch/answer-quality/issues/02`, 2026-10-03, 12 checks): **`Results: 1700 passed, 0 failed`**" (use the figure Task 2 Step 2 measured). In the **Switch arm** paragraph change the `mr_ifold` sentence to: "`mr_ifold` (default true, 2026-10-02) folds `%i` out of the top-level answer and, since 2026-10-03, out of RemoveContent's argument (`.scratch/answer-quality/issues/01`, `02`); false reproduces the earlier answers."

- [ ] **Step 2: `docs/grading-and-leaf-size.md`.** Replace every rubi figure the new `test/grade_report.out` changes (headline A %, solved %, the per-section table, section 6's C count, the "native grades better" count), each stamped 2026-10-0x and the build, and add after the depth-0 fold's section a short "RemoveContent's %i fold (2026-10-03)": the mechanism (one paragraph citing the spec), and the measured effect (probe 09, the acceptance A/B in `.scratch/answer-quality/rcfold_ab/`).

- [ ] **Step 3: Ticket 02.** In its triage table move the 5 misfiled entries (6.3.7 e171/e173/e175, 6.4.7 e5/e50) from `log(%i*u)` to the complex-conjugate family (45 / 92), and add a `### 2026-10-0x -- RemoveContent fold accepted` comment: the per-section PASS/FAIL and grade transitions from the Task 3 log, the new probe 08 census, the commits. Status stays `needs-triage` (the `%pi/2` shift family and the others remain).

- [ ] **Step 4: File ticket 03** `.scratch/answer-quality/issues/03-port-simplifyantiderivative.md`, `Status: needs-triage`, `Type: port gap`: Rubi's `Subst` wraps every result in `SimplifyAntiderivative` (`reference/rubi/Rubi/IntegrationUtilityFunctions.m:5147-5149`), which is not ported (no occurrence in the package); its `Log[c_*u_] -> Log[u] /; FreeQ[c,x]` rule (`:5291`) would clear the 11 `log(%i*tanh(u))` section-6 C's (probe 09's `same` lines, e.g. 6.7.1 e24 via `4_1_0_3 r2`); about 40 rules from `:5265`, plus helpers; 1,194 `%mr_subst` call sites across the rule classes, so a port changes answers in every class and needs its own spec and full re-run.

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md docs/grading-and-leaf-size.md .scratch/answer-quality/issues/02-remaining-i-after-fold.md .scratch/answer-quality/issues/03-port-simplifyantiderivative.md
git commit -m "docs+issues: RemoveContent's %i fold accepted; SimplifyAntiderivative port ticketed"
```

- [ ] **Step 6: Merge** (only after the user accepts the Task 3 results)

```bash
git checkout master
git merge --no-ff rcfold -m "merge: RemoveContent folds %i out of its argument (rcfold, answer-quality 02)"
git branch -d rcfold
```
Do not push.
