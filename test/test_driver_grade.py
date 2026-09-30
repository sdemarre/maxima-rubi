#!/usr/bin/env python3
"""Regression guard: the corpus driver's grade (the A/B/C/F grade and leaf
size of the 12000.org independent CAS integration tests; test/mr_grade.lisp,
user request 2026-09-30; docs/grading-and-leaf-size.md). The Lisp itself has its own Maxima suite,
test/test_mr_grade.mac; this guard covers the driver around it.

  entry text (no Maxima) -- the optimal is evaluated under the model flags
    and its OPTIMAL line, and an answer's GRADE line, come before the
    checker; the marker branch has neither.
  classify (no Maxima) -- OPTIMAL / GRADE lines are read into the result.
  grade (no Maxima) -- the reference's F / F(-1) / F(-2) for no answer, a
    timeout and an error; A for a no-closed-form entry that answered the
    noun, or an antiderivative; the Lisp grade otherwise.
  sidecar (no Maxima) -- the queue runner writes every entry's .grade line;
    test/merge_grade.py censuses them and refuses an incomplete set.
  end to end (the rules core) -- one entry through rubi: its .grade line.

Re-runnable:  python3 test/test_driver_grade.py
Exits nonzero if any check fails.
"""

import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, argv=None):
    real = sys.argv[:]
    if argv is not None:
        sys.argv = argv
    try:
        spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.argv = real


passed = 0
failures = []


def check(name, actual, expected):
    global passed
    if actual == expected:
        passed += 1
        print(f"PASS [{name}]")
    else:
        failures.append(name)
        print(f"FAIL [{name}]\n    expected: {expected!r}\n    actual:   {actual!r}")


def text_checks(drv):
    text = drv.build_text("sin(x)", "x", "-cos(x)")
    i_opt = text.find('mr_grade_line("OPTIMAL"')
    i_grade = text.find('mr_grade_line("GRADE"')
    i_check = text.find("mr_check_entry(")
    check("text: the grade module is loaded", 'load("test/mr_grade.lisp")$' in text, True)
    check("text: OPTIMAL, then GRADE, then the checker",
          0 < i_opt < i_grade < i_check, True)
    check("text: the optimal is evaluated under the model flags",
          "logexpand : false, radexpand : false], errcatch(-cos(x))" in text, True)
    marker = drv.build_text("f(x)", "x", "Unintegrable(f(x),x)")
    check("text: the marker branch has no grade line", "mr_grade_line" in marker, False)


def classify_checks(drv):
    out = ("ANSWERED 0.5\nOPTIMAL 12 3\nGRADE B 30 3\nNUMERIC verified ok\n"
           "CLASS verified\nPROOF chainA.1\n")
    r = drv.classify_entry(out, False)
    check("classify: OPTIMAL and GRADE are read", (r.optimal, r.grade), (("12", "3"), ("B", "30", "3")))
    r = drv.classify_entry("ANSWERED 0.5\nCLASS deferred\n", False)
    check("classify: an entry without them", (r.optimal, r.grade), (None, None))


def grade_checks(drv):
    R = drv.EntryResult
    ans = R("verified", 0, "radcan", 0.5, ("12", "3"), ("B", "30", "3"))
    check("grade: an answer takes the Lisp grade", drv.grade_of("verified", ans, False), "B")
    check("grade: unverified is graded too", drv.grade_of("unverified", ans, False), "B")
    check("grade: timeout is F(-1)", drv.grade_of("timeout", R("timeout", 0, None, None), False),
          "F(-1)")
    check("grade: error is F(-2)", drv.grade_of("error", R("error", 0, None, None), False), "F(-2)")
    for cls in ("deferred", "contains-noun"):
        check(f"grade: {cls} is F", drv.grade_of(cls, R(cls, 0, None, 0.1), False), "F")
    check("grade: no closed form, answered the noun -> A",
          drv.grade_of("no-answer", R("no-answer", 0, None, 0.1), True), "A")
    check("grade: no closed form, answered an antiderivative -> A (the reference's rule)",
          drv.grade_of("unexpected", R("unexpected", 0, None, 0.1), True), "A")
    check("grade line: an answer",
          drv.grade_line("verified", ans, False, "f.mac e1 L7"),
          "B leaf=30/12 type=3/3 f.mac e1 L7")
    check("grade line: no answer keeps the optimal's size",
          drv.grade_line("deferred", R("deferred", 0, None, 0.1, ("12", "3")), False, "f.mac e1 L7"),
          "F leaf=-/12 type=-/3 f.mac e1 L7")
    check("grade line: a timeout knows nothing",
          drv.grade_line("timeout", R("timeout", 0, None, None), False, "f.mac e1 L7"),
          "F(-1) leaf=-/- type=-/- f.mac e1 L7")


def sidecar_checks(queue_mod, merge_grade):
    class Stub:
        PASS_CLASSES = {"verified"}
        FILTER = "x"

        def header_lines(self, title, detail, build):
            return [title, "filter: x", ""]

        def run_entry_detail(self, rel, idx, text, line_no):
            if idx == 0:
                return ("verified", f"verified       t=   0.4s {rel} e1 L{line_no}", 0, "radcan",
                        {"grade": f"A leaf=10/8 type=3/3 {rel} e1 L{line_no}"})
            return ("timeout", f"timeout        t=  30.0s {rel} e2 L{line_no}", 0, None,
                    {"grade": f"F(-1) leaf=-/- type=-/- {rel} e2 L{line_no}"})

    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "corpus_class9.shard00.out")
        jobs = [("f.mac", 0, "[]", 7, 1.0), ("f.mac", 1, "[]", 8, 1.0)]
        queue_mod.run_queue(Stub(), jobs, 1, [out], lambda k: "T", lambda k: "D", [],
                            log=lambda m: None)
        side = os.path.join(tmp, "corpus_class9.shard00.grade")
        text = open(side).read() if os.path.exists(side) else None
        check("sidecar: one .grade line per entry", text,
              "A leaf=10/8 type=3/3 f.mac e1 L7\nF(-1) leaf=-/- type=-/- f.mac e2 L8\n")
        census = os.path.join(tmp, "census.out")
        rc = merge_grade.main([out, census, side])
        body = open(census).read() if rc == 0 else ""
        check("merger: the census",
              (rc, "grades: A 1 (50.00%)  F(-1) 1 (50.00%)" in body,
               "mean time (s): 0.40" in body, "normalized mean: 1.25" in body),
              (0, True, True, True))
        open(side, "w").write("A leaf=10/8 type=3/3 f.mac e1 L7\n")
        saved = sys.stderr
        sys.stderr = open(os.devnull, "w")
        try:
            rc = merge_grade.main([out, census, side])
        finally:
            sys.stderr.close()
            sys.stderr = saved
        check("merger: an entry without a line is refused", rc, 1)


def end_to_end(drv):
    cls, _line, _caps, _proof, sides = drv.run_entry_detail(
        "9 T/f.mac", 0, "[x^3,x,1,x^4/4]", 7)
    check("end to end: rubi's answer is graded", (cls, sides["grade"]),
          ("verified", "A leaf=7/7 type=1/1 9 T/f.mac e1 L7"))


def main():
    drv = _load("corpus_driver", ["corpus_driver.py", "ZZ no such section ZZ", "1", "30"])
    queue_mod = _load("run_corpus_queue")
    merge_grade = _load("merge_grade")
    text_checks(drv)
    classify_checks(drv)
    grade_checks(drv)
    sidecar_checks(queue_mod, merge_grade)
    end_to_end(drv)
    print(f"Results: {passed} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
