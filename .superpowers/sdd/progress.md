# SDD progress ledger — milestone-1

Branch: milestone-1 (worktree .worktrees/milestone-1)
Plan: docs/superpowers/plans/2026-08-20-milestone-1-implementation.md
Merge base (master): 6754be9

## Completed tasks

Task 1: complete (commits 6754be9..ca98e3b, review clean — spec ✅, quality Approved)
Task 2: complete (commits c55cfba..f36d978, review clean after 1 fix — spec ✅, quality Approved)
  - Fixed during review: loader by-name fallback was inverted for this build
    (errcatch returns [RESULT] on success, [] on error — measured in
    probes/maxima/probe-errcatch-semantics.*). Now `if ok = []` (fire on error).
  - 9/9 + no file_search warning corroborated by report's verbatim output; batched
    path (load_pathname=false) untested — see Minor below.
Task 3: complete (commits 7781cee..c17c482, review clean after 1 fix — spec ✅, quality Approved)
  - Fixed during review: the "recursion re-dispatches" rubi() check was vacuous
    (integrate of the original and reduced integrand are equal on this build).
    Added direct firing assertions on the rec rule (fires on the product form,
    rejects x^2). Also made test_load_and_api save/restore mr_rule_table and
    removed the now-redundant D1 restore in test_runner.
  - Corrected the depth-cap premise: exp(x^2) is NOT a noun on this build
    (integrate returns an erf closed form); assertion accepts the integrate
    result or a noun.
Task 4: complete (commits 535dc07..8528996, review clean after 2 fixes — spec ✅, quality Approved)
  - Fixed during review (1): %mr_dispatch loop-level return bug — a return(value)
    inside a for loop is loop-level in this build, so dispatch ALWAYS returned
    false and rubi() was a silent pass-through to integrate. Fixed (track ans,
    bare return() to break the loop, return ans) + non-vacuous test_dispatch
    (unit + end-to-end rubi(x^7,x)=99 sentinel). CRITICAL runner defect, caught
    because the implementer measured it.
  - Fixed during review (2): generator's mandated "fail loudly on unlisted token"
    was unmet — unknown HEAD tokens passed through silently (dead KeyError).
    Fixed: emit_head fallback raises GenError naming file/rule/head for a head
    not in RENAME ∪ RESTRUCTURE ∪ {x,Pi,E,I}; atom pass-through preserved; dead
    m2m() deleted.
Task 5: complete (commits 8528996..2c65051, review clean after 1 fix — spec ✅, quality Approved)
  - Fixed during review: two systematic term-walker mistranslations (wrong-answer
    paths in class 1) — Bug B: %mr_term_xexp dropped bare-power monomial terms
    (x^2 after expand fell to else false) -> coeff/degree/polyDegQ wrong on monic
    leading terms, and %mr_degree leaked a boolean; Bug A: %mr_term_coeff dropped
    the bare-x term at n=1 -> linearQ(x+1,x)=false (Rubi: true). Fixed + 10 monic-
    term probes added. Also corrected a false "measured" claim in the report and a
    stale test name.
  - F1 (rule 5 (a+b*u)^m pattern dead — rule 4 shadows it): confirmed real,
    correctness-HARMLESS (both rules give the identical antiderivative; rule 4 or
    fall-through always yields the right answer in 1.1.1.x). Coverage/redundancy
    gap + Subst path untested end-to-end. Track for Task 6/9; re-measure on 5.50.
  - F3 (plan's /12,/9 antiderivatives were wrong): corrected to /8,/18 (verified).
Task 6: complete (commits 1a85498..0ac99b5, pending review)
  - Full-class generation: 67 files, 2710 rules, every per-file count equal to
    the T1 inventory (static cross-check probes/census/01-generation-vs-
    inventory, no Maxima). Emitter dispatch E1-E5/E10/E11 closed the shapes
    the census tier table could not represent 1:1 (rule-list ReplaceAll ->
    equation-list subst, the 3-arg list form being a silent no-op; ShowStep
    -> 4th arg; Sum -> 4-arg mr_sum; MatchQ RAW args in the fresh-marker
    scope; digit/paren join — 2(x+1) and (x+1)2 are parse errors).
  - Load wall measured (T5 §5): a hard process-level defmatch BUDGET, not a
    timing problem — 1200 plain patterns load / 1600 FATAL; class-1 load
    list files 1-7 (294 rules) load / file 8 (361) dies with SBCL's fatal
    "Thread local storage exhausted" (errcatch cannot catch it); unload()
    releases the budget. The loader does NOT call mr_load_class1_all()
    (it exists for a build with the headroom); eager core = utils + 1.1.1.1.
    Probe: probes/load_wall/probe-load-wall.run (6 parts, self-flagging).
  - Fixed both rule-run parsers (01-inventory + 01-class1-syntax-census): a
    comment-only line between := and the rhs silently dropped 5 rule bodies
    (4 class-1 + 1 class-9); dangling-:= exception; evidence regenerated
    (class-1 cond 2705->2709, rule totals unchanged 2710/67).
  - %mr_load_sibling read load_pathname at CALL time (top level = the batch
    file, not the library — measured probes/maxima/probe-load-pathname.out)
    -> spurious file_search1 miss per sibling + fallback reliance. Now
    %mr_lib_dir captured at definition time; suite run has zero file_search1.
  - Brief deviations, all measurement-forced and recorded in the report:
    D1 full load list wrapped in the uncalled mr_load_class1_all(); D2 table
    assembly flatten([...]) (list concat is a hard error in this build); D3
    the ~1-minute decision gate moot (budget, not time); D4 test_census is
    the loadable subset (1.1.1.2 count 40 = T1 number, witness, restore)
    with the global 2710 check in the static census probe.
  - Suite 71/0; per-file parse+witness 67/67 (one process per file).

## Minor findings (triage at final whole-branch review)

- [Task 6] probes/load_wall/probe-load-wall.out part 5: the echoed
  continuation lines of the multi-line disp INPUT (+length(mr_rules_...)
  lines) leak into the .out because the input-echo filter only strips the
  first line of a wrapped statement. Cosmetic — the machine-readable
  PREFIX_TOTAL= marker is the authoritative value and is what the verdict
  checks.
- [Task 1] test_maxima_rubi.mac: Results line is not literally the last output
  before quit() — the closing `====` and the printed `run_all_tests()` return
  value (`0 = 0`) follow it. Plan-mandated (the brief's code returns
  `tests_failed = 0`). Functional intent intact (unique greppable marker; a
  mid-run death prints no Results line). Possible fix: return `true` instead of
  `tests_failed = 0` so the prose holds.
- [Task 1] test_maxima_rubi.mac: Results line renders with double spaces
  (`Results:  3  passed,  0  failed`) — inherent to Maxima `print`. All later
  "read that line" steps must use a spacing-tolerant pattern (e.g.
  `Results:.*passed.*failed`). Propagate to any task that hard-codes the literal.
- [Task 1] test_maxima_rubi.mac: only the passing paths of check/check_bool/
  check_not are exercised by the smoke suite; the FAIL branches are untested.
  Brief mandates exactly these three smoke checks. A later task that adds a
  deliberate-failure assert would cover the counters/FAIL-prints.
- [Task 2] maxima_rubi.mac:14-20 — 3-space indentation on the errcatch comment
  + ok:/if lines vs 2-space elsewhere (cosmetic, from the fix commit).
- [Task 2] maxima_rubi_utils.mac:36 — %mr_dispatch `if res # false` uses raw
  `#` in the if-condition (evaluated, so correct), not is()-wrapped. Forward
  note: Task 3's first rule should ASSERT a firing rule actually fires (not
  just that fall-through works), so this path is exercised.
- [Task 2] maxima_rubi_utils.mac:49-57 — mr_int increments global depth_level
  on entry, decrements before return; if %mr_dispatch throws, the decrement is
  skipped (budget left incremented). Robustness note for Task 3+ (real rules).
- [Task 2] maxima_rubi.mac:13 — batched path (load_pathname=false) untested;
  only the sibling-dir path is exercised. Coverage note for a later task.
- [Task 3] test_maxima_rubi.mac:130-131 — test_load_and_api's table wipe sits
  AFTER its fall-through checks, so with Task 3's top-level table the
  "fall-through x^2" check actually FIRES the power rule (a*x^m matches x^2);
  it still passes (answers coincide) but no longer tests what its name says.
  Optional fix: hoist `saved_table : mr_rule_table, mr_rule_table : []` to the
  TOP of test_load_and_api so all its checks run against a genuinely empty table.
- [Task 3] FORWARD NOTE for Task 4+: no committed assertion distinguishes the
  %mr_dispatch table-fired path from fall-through — every rubi() answer in the
  suite coincides with Maxima's own integrate on this build, the verbose line
  is printed but not asserted, and the direct firing asserts call rule
  functions (bypassing the table). A dispatch that never fired a table rule
  would pass 20/20 silently. Mitigate in Task 4+ with a rule whose answer
  differs from integrate, an assert on the verbose line, or direct firing
  asserts per generated rule (as done here for power/rec).
- [Task 3] Cosmetic: check name "recursion re-dispatches" (test) vs "recursion
  re-dispatches (end-to-end)" (plan); the vacuity rationale is stated in two
  adjacent comments. No behavior impact.
- [Task 4] DECISION (human, 2026-08-20): the emitter emits the PLAIN pattern
  only — the Power-optional D-duplication (power_dups) is NOT wired into
  emit_rule. Rules with an optional Power exponent (e.g. 1.1.1.1 rules 2,4,5)
  will not fire on the bare-exponent-1 case (Power head dropped: bare `x`,
  `(1+2x)`); those fall through to integrate (correct answer, not via the
  rule). This is a COVERAGE gap, not a correctness bug. FORWARD NOTE for Task 9:
  the divergence loop must add the Power-optional D-duplication where the corpus
  shows the coverage gap (plan step 2 updated to record the deferral).
- [Task 4] generate_class1.py:419 — `lhs, rhs, cond = split_rule(text)` sits
  OUTSIDE the try/except that wraps the other per-rule crashes. A run with `:=`
  that defeats split_rule exits 1 with a bare traceback naming no r<n>. Optional
  fix: move the split_rule call inside the try for the same GenError treatment.
- [Task 4] generate_class1.py:275-277 — a HEAD-position pattern variable
  (`v_[…]` in an lhs) bypasses both the new head check and F11 (translate_atom
  consumes `v_` as an ordinary capture, emitting a literal `_mr_…_v[…]`). No
  class-1 rule uses a head pattern (none in 1.1.1.1); the Task 6 sweep is where
  it would bite. Suggested fix: raise when a capture marker is immediately
  followed by `[`.
- [Task 4] translation_table.py — `translate()` KeyError still unreachable in
  the current call graph (harmless guard); `"Power"/"Plus"/"Times"` map to
  non-callable infix names (a noun call if ever written as an explicit head).
  Pre-existing brief-mandated table content; no 1.1.1.1 rule affected. Note only.
- [Task 5] Bug C: `%mr_termPower` (maxima_rubi_utils.mac:369) sign-strip guard is
  `not atom(t) and op(t) = "-"`, but `atom(-2)=true` in this build, so numeric
  signs are never stripped: termPower(-2,x)=[-2,1,1]. Consequence:
  removeContent(2x-2)=2x-2 (Rubi: 1-x). Masked in class 1 (consumed inside
  Log/b, a residual content is an additive constant). Fix: strip sign for any
  t with op(t)="-" (guard op per atom-first rule), or implement the source's
  a+b==0 integer pattern.
- [Task 5] Inaccurate deviation notes at maxima_rubi_utils.mac:406-414 (claim the
  .m pattern "matches a numeric base hiding in an integer"; it does not — Rubi's
  RemoveContent[4+2x,x] also returns input unchanged). Cosmetic; correct the note.
- [Task 5] `%mr_together` idiom (maxima_rubi_utils.mac:138-141) is behaviorally
  correct (verified on 9 inputs incl. cancellation) but cryptic — add one comment
  stating the measured rat-object shape so a future reader doesn't "simplify" it.
- [Task 5] Minor DRY: %mr_polyDegQ re-runs %mr_together on an already-together'd
  v; %mr_negQ's final `is(v)=true` coercion is redundant (operands already bool).
- [Task 5] FORWARD NOTE for Task 6 (F2, under-scoped in the report): the
  generator table maps ALL PolyQ arities 1:1 to the 2-arg %mr_polyQ. Beyond the
  3-arg Symbol form (~82-100 uses -> should map to %mr_polyDegQ, now correct after
  Bug B), there are ~100 TWO-ARG power-form uses `PolyQ[Pq, x^v]` (e.g. x^(n/2))
  that are a SILENT semantic error: %mr_polyQ(u, x^v) treats x^v as the variable
  -> PolyQ[x^4+1, x^2] -> false where Rubi -> true, flipping negated guards
  (Not[PolyQ[..., x^(n/2)]] in 1.1.3.7.m:41, 1.1.3.8.m:21) into wrong-answer paths.
  Task 6 FIRST STEP must add generator-side PolyQ overload dispatch:
  (u,x)->%mr_polyQ, (u,x,n)->%mr_polyDegQ, (u,x^v[,n])->a power-form port
  (polynomial in x^v) or an explicit loud generation error. MUST land before the
  67-file generation.
