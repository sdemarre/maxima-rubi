#!/usr/bin/env python3
"""Unit tests for the section-9 generator fixes (spec
docs/superpowers/specs/2026-09-22-section9-port-design.md A2).
Pure Python, no Maxima."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "generator"))
sys.argv = [sys.argv[0]]
import generate_rules as g  # noqa: E402

passed = failed = 0
def check(name, actual, expected):
    global passed, failed
    if actual == expected:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name}\n  expected: {expected!r}\n  actual:   {actual!r}")

# A2.1 -- 9.2 r12: a whole-line comment inside a multi-line condition.
src = ("Int[u_,x_Symbol] :=\n  u /;\n"
       "FreeQ[m,x] && (\n  IGtQ[n,0] ||\n"
       "(* ILtQ[n,0] && ILtQ[m,0] || *)\n  IGtQ[m,0])\n")
out = g.drop_comment_only_lines(src)
check("A2.1 comment-only line removed", "(*" in out, False)
check("A2.1 the condition stays one run (no blank line inside it)",
      len(g.rule_runs(g.strip_comments(out))), 1)
check("A2.1 an inline comment is left to strip_comments",
      g.drop_comment_only_lines("a && (* b *) c\n"), "a && (* b *) c\n")
# Fix round 1 (task review finding 1): a greedy `.*` between `(*` and the
# FINAL `*)` on the line would fullmatch a line with code between two
# comments, silently dropping the code -- verified absent from the 9.2/9.3
# pinned sources (no line matches `(\*.*\*).*(\*`, checked with grep; see
# the fix-round-1 report), but the function must still refuse to drop it.
check("A2.1 code between two comments on one line survives",
      g.drop_comment_only_lines("(* a *) code (* b *)\n"),
      "(* a *) code (* b *)\n")
# Fix round 2 (final review): a comment-only line that is the SOLE
# separator between two rules must not be swallowed into one run. Rubi's
# own column-0 Int[ convention makes this safe today (the second rule's
# literal Int[ always closes the first run whatever a dropped line leaves
# behind); this pins that it stays safe, and that a rule NOT opening on
# Int[ at column 0 is caught loudly instead of silently merged.
two_rules_no_blank = ("Int[u_,x_Symbol] := u /; FreeQ[u,x]\n"
                      "(* a stray note *)\n"
                      "Int[v_,x_Symbol] := v /; FreeQ[v,x]\n")
out = g.drop_comment_only_lines(two_rules_no_blank)
check("A2.1 fix round 2: two Int[ rules split by a bare comment stay two runs",
      len(g.rule_runs(g.strip_comments(out))), 2)
indented_second_rule = ("Int[u_,x_Symbol] := u /; FreeQ[u,x]\n"
                        "(* a stray note *)\n"
                        "  Int[v_,x_Symbol] := v /; FreeQ[v,x]\n")
try:
    g.drop_comment_only_lines(indented_second_rule)
    a21_join_outcome = "no exception raised"
except SystemExit:
    a21_join_outcome = "SystemExit"
check("A2.1 fix round 2: a rule not opening on column-0 Int[ raises "
      "GenError instead of silently joining two runs",
      a21_join_outcome, "SystemExit")
# 2026-09-25 (class-8 port): a comment-only line followed by a BLANK line
# (1.1.3.1 L82, a commented-out rule) is not a join -- the blank line is the
# separator -- and must not raise; it tripped --class 1 / --class 3.
comment_then_blank = ("Int[u_,x_Symbol] := u /; FreeQ[u,x]\n"
                      "(* Int[w_,x_Symbol] := w *)\n"
                      "\n"
                      "Int[v_,x_Symbol] := v /; FreeQ[v,x]\n")
try:
    out = g.drop_comment_only_lines(comment_then_blank)
    runs_after = len(g.rule_runs(g.strip_comments(out)))
except SystemExit:
    runs_after = "SystemExit"
check("A2.1 guard: a comment-only line before a blank line is no join",
      runs_after, 2)
# ... nor before a comment opening at column 0 that runs over several lines
# (1.2.1.2 L78/L90), nor before the single-line ShowSteps wrapper (3.5 L45).
for label, nxt in (("a multi-line comment", "(* Int[w_,x_Symbol] :=\n  w *)\n"),
                   ("the ShowSteps wrapper",
                    "If[TrueQ[$LoadShowSteps], Int[v_,x_Symbol] := v /; FreeQ[v,x], "
                    "Int[v_,x_Symbol] := v /; FreeQ[v,x]]\n")):
    try:
        g.drop_comment_only_lines("Int[u_,x_Symbol] := u /; FreeQ[u,x]\n"
                                  "(* a note *)\n" + nxt)
        outcome = "no exception raised"
    except SystemExit:
        outcome = "SystemExit"
    check(f"A2.1 guard: a comment-only line before {label} is no join",
          outcome, "no exception raised")

# A2.2 -- the multi-line ShowSteps wrapper keeps its plain branch only.
wrapped = ("If[TrueQ[$LoadShowSteps],\n\n"
           "Int[u_,x_Symbol] :=\n  ShowStep[\"\",\"a\",\"b\",Hold[u]] /;\nSimplifyFlag,\n\n"
           "Int[u_,x_Symbol] :=\n  u /;\n FreeQ[u,x]]\n")
plain = g.unwrap_showsteps_multiline(wrapped)
check("A2.2 the ShowStep branch is gone", "ShowStep" in plain, False)
check("A2.2 the plain branch loses the If's closing bracket",
      plain.strip().splitlines()[-1].strip(), "FreeQ[u,x]")
check("A2.2 one rule run remains", len(g.rule_runs(plain)), 1)
check("A2.2 text without a wrapper passes through unchanged",
      g.unwrap_showsteps_multiline("Int[u_,x_Symbol] :=\n  u\n"),
      "Int[u_,x_Symbol] :=\n  u\n")
# Fix round 1 (task review finding 2): a wrapper missing its SimplifyFlag
# line must not run off the end of the line list (a raw IndexError) --
# it is a GenError (a SystemExit subclass, house convention).
try:
    g.unwrap_showsteps_multiline(
        "If[TrueQ[$LoadShowSteps],\n\nInt[u_,x_Symbol] := u\n")
    a22_missing_simplifyflag = "no exception raised"
except SystemExit:
    a22_missing_simplifyflag = "SystemExit"
except IndexError:
    a22_missing_simplifyflag = "IndexError"
check("A2.2 a wrapper missing SimplifyFlag raises GenError (not IndexError)",
      a22_missing_simplifyflag, "SystemExit")

# A2.3 -- UnsameQ.
g.CLASS, g.CLASS_PREFIX = 9, "9 "
cond = g.clean_cond("v=!=u", "t9", 1)
body = g.emit_rule(("Int[u_*v_,x_Symbol]", "u", cond), "t9", 1, {"u", "v"})
check("A2.3 =!= emits %mr_unsameQ", "%mr_unsameQ(" in body, True)
check("A2.3 no factorial or bare = left from =!=", "!" in body.split("_mr_repl_")[0], False)

# A2.4 -- Int[u_,x_].
body = g.emit_rule(("Int[u_,x_]", "CannotIntegrate[u,x]", ""), "t9", 2, {"u"})
check("A2.4 Int[u_,x_] emits the x_Symbol pattern",
      "(Pattern x (Blank Symbol))" in body, True)
check("A2.4 the record is a bare-u_ Int clause",
      g.bare_int_clause("Int[u_,x_]", "t9", 2), True)

# Task 12b -- Rubi's condition-assignment idiom (.scratch/class-ports/
# issues/13). The recogniser is structural: an assignment, inside a rule
# condition, to a name the enclosing With/Module declares WITHOUT an
# initialiser.
IDIOM = ("Not[FalseQ[r=Divides[y^m,v^m,x]]] && "
         "Not[FalseQ[q=DerivativeDivides[y,u,x]]]")
check("12b the idiom is found, in the condition's evaluation order",
      g._condition_assignments(IDIOM, ["q", "r"], "9_3", 18, "the cond"),
      [("r", "Divides[y^m,v^m,x]"), ("q", "DerivativeDivides[y,u,x]")])
check("12b bare locals are the ones declared without an initialiser",
      g._scope_bare_locals("{v=f[x], q, r}"), ["q", "r"])
for label, cond, bare in [
        ("a name no scope declares", "Not[FalseQ[q=D[y,x]]]", []),
        ("an already-initialised local", "Not[FalseQ[v=D[y,x]]]", ["q"]),
        ("the same name twice", "FalseQ[q=A[x]] && FalseQ[q=B[x]]", ["q"])]:
    try:
        g._condition_assignments(cond, bare, "9_3", 18, "the cond")
        outcome = "no exception raised"
    except SystemExit:
        outcome = "SystemExit"
    check(f"12b an assignment to {label} raises GenError", outcome,
          "SystemExit")
check("12b non-assignment operators are not assignments",
      g._condition_assignments("a==b && c=!=d && a>=1 && b<=2 && e!=f",
                               [], "9_3", 18, "the cond"), [])
# Fix round 1 (review item 1): Mathematica initialises the scope's own
# declarations on entry and evaluates the condition afterwards, so the
# condition assignments come LAST. Leading with them emitted `q : g(v)`
# off an UNBOUND v. Output-neutral on the four upstream sites, which
# declare no initialised local.
check("12b hoist: the scope's own initialisers come first",
      g._hoist_scope_assigns("{v=f[x], q}", [("q", "g[v]")], "9_3", 18),
      "{v=f[x], q=g[v]}")
check("12b hoist: with no initialised local, the condition's order stands",
      g._hoist_scope_assigns("{q,r}", [("r", "A[x]"), ("q", "B[x]")],
                             "9_3", 18),
      "{r=A[x], q=B[x]}")

print(f"Results: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
