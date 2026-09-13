#!/usr/bin/env python3
"""Matcher substrate plan 2, T10: rewrite the matcher-coupled Layer A sections
of test_maxima_rubi.mac against the substrate entries (%mr_defrule handles,
%mr_rule_bindings / %mr_rule_accept / %mr_rule_apply, the 4-arg %mr_matchQ).

Run from the repo root:  python3 <this dir>/layerA_rewrite.py
Every edit is asserted: a whole-function replacement swaps the function (and
the comment block directly above it) for <this dir>/<name>.mac; a literal
replacement must occur exactly the stated number of times."""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
T = pathlib.Path("test_maxima_rubi.mac")

FUNCTIONS = [
    "test_dispatch",
    "test_matchQ_predicates",
    "test_class2_marker_head",
    "test_class3_headvar",
    "test_class3_c1_slotted",
    "test_class3_c4_321",
    "test_class3_c3_ratio",
    "test_class3_b3_33",
    "test_class3_c5_34",
]

# new sections: (inserted after function, section file / function name)
INSERTS = [
    ("test_class2_marker_head", "test_generated_matchq_shapes"),
]

LITERALS = [
    # binds() helper, before the first test function
    ("test_smoke() := block([],",
     (HERE / "binds_helper.mac").read_text() + "test_smoke() := block([],", 1),
    # the generated-MatchQ-shapes section runs after the marker-head section
    ("    test_class2_marker_head(),\n",
     "    test_class2_marker_head(),\n    test_generated_matchq_shapes(),\n", 1),
    # b1: pattern level through %mr_rule_bindings
    ("    mm : _mr_pat_3_5_r31(log(a + %e^x*b), x),",
     "    mm : %mr_rule_bindings(_mr_rule_3_5_r31, log(a + %e^x*b), x),", 1),
    ("    mm : _mr_pat_3_5_r35(log(g*(a + b*x + c*x^2)^n)/(d + e*x^2), x),",
     "    mm : %mr_rule_bindings(_mr_rule_3_5_r35, log(g*(a + b*x + c*x^2)^n)/(d + e*x^2), x),", 1),
    # c2: pattern level through %mr_rule_bindings; the free-d head now binds
    ("_mr_pat_3_1_2_r10(", "%mr_rule_bindings(_mr_rule_3_1_2_r10, ", 7),
    ("""    check_not("c2 r10 rejects the free-d head",
              %mr_rule_bindings(_mr_rule_3_1_2_r10, (dd*x)^mm2*(a + b*log(c*x^n))^2, x)),""",
     """    /* the faithful (d_.*x_)^m_. binds a free-d power head (d = dd,
       m = mm2) — the defmatch-era is(u = 1) gate went with the
       re-transcription (plan-2 pre-validation, 2026-09-13) */
    check_bool("c2 r10 binds the free-d head (d = dd, m = mm2)",
               binds(%mr_rule_bindings(_mr_rule_3_1_2_r10, (dd*x)^mm2*(a + b*log(c*x^n))^2, x),
                     ['_mr_3_1_2_r10_d = dd, '_mr_3_1_2_r10_m = mm2])),""", 1),
    # c6: the cond-accepted binding (the first complete binding's cond is false)
    ("      mm : _mr_pat_3_5_r10(log(d*(a+c*x^2)^n)/(a*e+c*e*x^2), x),",
     "      mm : %mr_rule_accept(_mr_rule_3_5_r10, log(d*(a+c*x^2)^n)/(a*e+c*e*x^2), x),", 1),
    ("      mm : _mr_pat_3_5_r10(log(d*(a+b*x+c*x^2)^n)/(a*e+b*e*x+c*e*x^2), x),",
     "      mm : %mr_rule_accept(_mr_rule_3_5_r10, log(d*(a+b*x+c*x^2)^n)/(a*e+b*e*x+c*e*x^2), x),", 1),
    ("      mm : _mr_pat_3_5_r10(log(d*(a+c*x^2)^n)/(2+3*x^2), x),",
     "      mm : %mr_rule_bindings(_mr_rule_3_5_r10, log(d*(a+c*x^2)^n)/(2+3*x^2), x),", 1),
    ("                 is(_mr_rule_3_5_r10(fc, x) # false)),",
     "                 is(%mr_rule_apply(_mr_rule_3_5_r10, fc, x) # false)),", 1),
    # c6b: pattern level through %mr_rule_bindings
    ("      mm : _mr_pat_3_5_r42(1/(x*sqrt(-3+log(x)^2)), x),",
     "      mm : %mr_rule_bindings(_mr_rule_3_5_r42, 1/(x*sqrt(-3+log(x)^2)), x),", 1),
    ("      mm : _mr_pat_3_5_r42(1 + 1/(x*sqrt(-3+log(x)^2)), x),",
     "      mm : %mr_rule_bindings(_mr_rule_3_5_r42, 1 + 1/(x*sqrt(-3+log(x)^2)), x),", 1),
]


def span(lines, name):
    """(start, end) line indices of function NAME plus the comment block
    directly above it (blank lines between are kept outside the span)."""
    hdr = [i for i, l in enumerate(lines)
           if re.match(r"\s*%s\(\) *:= *block\(" % re.escape(name), l)]
    assert len(hdr) == 1, (name, hdr)
    h = hdr[0]
    end = next(i for i in range(h + 1, len(lines)) if re.match(r"\s*\)\$\s*$", lines[i]))
    start = h
    j = h - 1
    if j >= 0 and lines[j].rstrip().endswith("*/"):
        while not lines[j].lstrip().startswith("/*"):
            j -= 1
        start = j
    return start, end


def main():
    text = T.read_text()
    for old, new, count in LITERALS:
        n = text.count(old)
        assert n == count, "literal %r: found %d, expected %d" % (old[:60], n, count)
        text = text.replace(old, new)
    lines = text.split("\n")
    for name in FUNCTIONS:
        start, end = span(lines, name)
        new = (HERE / (name + ".mac")).read_text().rstrip("\n").split("\n")
        lines[start:end + 1] = new
    for after, name in INSERTS:
        assert not any(re.match(r"\s*%s\(\) *:= *block\(" % re.escape(name), l) for l in lines), name
        _, end = span(lines, after)
        lines[end + 1:end + 1] = [""] + (HERE / (name + ".mac")).read_text().rstrip("\n").split("\n")
    text = "\n".join(lines)
    # the deleted entries may still be named in comments (history), not in code
    code = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    for gone in ("_mr_pat_", "%mr_mbp_", "%mr_logpow_match", "%mr_logratio",
                 "%mr_headvar_match", "%mr_register_markers", "%mr_isMQMarker",
                 "%mr_dispatch(", "%mr_lpfac", "_mr_rule_3_3_r11(", "_mr_rule_3_4_r8(",
                 "_mr_rule_3_5_r10("):
        assert gone not in code, "still referenced: " + gone
    T.write_text(text)
    print("rewrote %d functions, %d literal edits" % (len(FUNCTIONS), len(LITERALS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
