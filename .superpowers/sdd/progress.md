# SDD progress ledger — milestone-1

Branch: milestone-1 (worktree .worktrees/milestone-1)
Plan: docs/superpowers/plans/2026-08-20-milestone-1-implementation.md
Merge base (master): 6754be9

## Completed tasks

Task 1: complete (commits 6754be9..ca98e3b, review clean — spec ✅, quality Approved)
Task 2: complete (commits c55cfba..f36d978, review clean after 1 fix — spec ✅, quality Approved)
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
  - Fixed during review: loader by-name fallback was inverted for this build
    (errcatch returns [RESULT] on success, [] on error — measured in
    probes/maxima/probe-errcatch-semantics.*). Now `if ok = []` (fire on error).
  - ⚠️ resolved: 9/9 + no file_search warning corroborated by report's verbatim
    output; batched path (load_pathname=false) is untested — see Minor below.

## Minor findings (triage at final whole-branch review)

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
