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

print(f"Results: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
