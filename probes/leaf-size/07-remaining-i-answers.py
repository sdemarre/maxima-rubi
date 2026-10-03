#!/usr/bin/env python3
""".scratch/answer-quality/issues/02: the section-6 answers still graded C after
the %i fold -- what are they? Dumps each answer so the remaining %i can be
classified (probe 08 classifies this output).

The records keep no answer text, so each C entry of
test/corpus_class6.grade.out is re-run: the corpus driver's own entry text
(build_text, every switch at its current default, mr_ifold true among them) up
to and including the loads, then, instead of the checker,
  GRADE    <the grade line of the answer>
  ANSWER   string(mr_r)
  OPTIMAL1 string(the optimal under logexpand:false, radexpand:false)
No verification: the verdict is the record's.

    setsid python3 probes/leaf-size/07-remaining-i-answers.py \\
        > probes/leaf-size/07-remaining-i-answers.out 2> .../07.err < /dev/null &

Each entry prints a `## <label>` line and then those lines, in label order.
"""

import concurrent.futures as cf
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.argv = [sys.argv[0]]
sys.path.insert(0, os.path.join(ROOT, "test"))
os.chdir(ROOT)
import corpus_driver as d  # noqa: E402

CUT = 'load("test/mr_grade.lisp")$\n'
_cache = {}


def elements(label):
    rel, e, _l = label.rsplit(" ", 2)
    if rel not in _cache:
        _cache[rel] = d.extract_entries(os.path.join(d.SUITE, rel))[0]
    return d.split_elements(_cache[rel][int(e[1:]) - 1][1:-1])


def one(label):
    els = elements(label)
    e_text = d.normalize_heads(els[3])
    text = d.build_text(d.normalize_heads(els[0]), els[1], e_text,
                        d.normalize_heads(els[4]) if len(els) == 5 else None, None)
    if text.count(CUT) != 1:
        return label, ["SKIPPED"]
    text = text.split(CUT)[0] + CUT + (
        "MR_opt : block([errormsg : false, logexpand : false, radexpand : false], "
        f"errcatch({e_text}))$\n"
        'errcatch(mr_say(mr_grade_line("GRADE", mr_r, MR_opt)))$\n'
        'printf(true, "ANSWER ~a~%", string(mr_r))$\n'
        'printf(true, "OPTIMAL1 ~a~%", '
        'if MR_opt = [] then "-" else string(first(MR_opt)))$\n')
    out, _hit = d.maxima_run(text, d.TIMEOUT + 10, [])
    keep = [ln.strip() for ln in out.splitlines()
            if ln.strip().startswith(("GRADE ", "ANSWER ", "OPTIMAL1 "))]
    return label, keep or ["NO-OUTPUT"]


def main():
    labels = [l.split(" ", 3)[3].strip()
              for l in open("test/corpus_class6.grade.out") if l.startswith("C ")]
    print(f"# section 6: {len(labels)} C entries, answers dumped (all switches default)")
    for l in open("test/corpus_class6.out"):
        if l.startswith("maxima: Maxima"):
            print("# " + l.strip())
    sys.stdout.flush()
    with cf.ThreadPoolExecutor(12) as ex:
        for label, lines in ex.map(one, labels):
            print(f"## {label}")
            for ln in lines:
                print(ln)
            sys.stdout.flush()


if __name__ == "__main__":
    main()
