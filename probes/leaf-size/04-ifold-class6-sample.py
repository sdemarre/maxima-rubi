#!/usr/bin/env python3
"""Why does rubi grade C on 36.5 % of class 6, and would folding %i fix it?

Class 6 (hyperbolic functions) is graded C on 1,854 of 5,080 entries
(test/corpus_class6.grade.out, 2026-10-01), 1,847 of them with the same
ExpnType as the optimal: the C is the grade's `%i` rule. Rubi 4 integrates
hyperbolics through the trig rules (Sinh[z] = -I Sin[I z]); Mathematica folds
Sin[I a + I b x] back to I Sinh[a + b x] on evaluation, Maxima folds
sin(%i*z) only when the argument is a product, not a sum whose every term
carries %i -- so the answer keeps sin(%i*b*x+%i*a) and its %i.

This probe re-runs a random sample (seed 1) of a grade sidecar's C entries
through the corpus driver's own entry text (build_text: rubi, the grade
lines, the checker), with rubi's answer passed through mr_ifold first:

  - a trig / hyperbolic / inverse function whose argument u is %i times an
    %i-free v (v = ratsimp(u/%i)) is rebuilt as f(%i*v), which Maxima's
    simplifier folds (sin(%i*v) -> %i*sinh(v), atan(%i*v) -> %i*atanh(v));
  - a sum whose every term is %i times an %i-free term is rebuilt as
    %i*(the sum of those terms), so -%i*(%i*X + %i*Y) multiplies out.

Bottom-up, answer-only: the integrand, the optimal and the checker are
untouched, so every printed CLASS is the checker's verdict on the folded
answer.

    python3 probes/leaf-size/04-ifold-class6-sample.py test/corpus_class6.grade.out 48 \\
        > probes/leaf-size/04-ifold-class6-sample.out

Each line: the sidecar's grade, then the folded answer's GRADE and CLASS.
The story these measurements belong to: docs/grading-and-leaf-size.md.
"""

import concurrent.futures as cf
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
grade_file, n = sys.argv[1], int(sys.argv[2])
sys.argv = [sys.argv[0]]
sys.path.insert(0, os.path.join(ROOT, "test"))
os.chdir(ROOT)
import corpus_driver as d  # noqa: E402

IFOLD = r'''mr_ifold(e) := if atom(e) then e else block([o: op(e), a: map(mr_ifold, args(e)), v],
  if member(o, [sin, cos, tan, cot, sec, csc, sinh, cosh, tanh, coth, sech, csch,
                asin, acos, atan, acot, asec, acsc, asinh, acosh, atanh, acoth, asech, acsch])
     and length(a) = 1 and not freeof(%i, a[1]) then
    (v: ratsimp(a[1]/%i), if freeof(%i, v) then apply(o, [%i*v]) else apply(o, a))
  else if o = "+" and not freeof(%i, a) then
    (v: map(lambda([t], t/%i), a), if freeof(%i, v) then %i*apply("+", v) else apply(o, a))
  else apply(o, a))$
'''
CALL = "mr_r: rubi(mr_f, x)$"


def one(line):
    parts = line.split(" ", 3)
    label = parts[3].strip()
    rel, e, _l = label.rsplit(" ", 2)
    els = d.split_elements(d.extract_entries(os.path.join(d.SUITE, rel))[0][int(e[1:]) - 1][1:-1])
    text = d.build_text(d.normalize_heads(els[0]), els[1], d.normalize_heads(els[3]),
                        d.normalize_heads(els[4]) if len(els) == 5 else None, None)
    assert CALL in text, "build_text no longer calls rubi as " + CALL
    text = text.replace(CALL, IFOLD + "mr_r: mr_ifold(rubi(mr_f, x))$")
    out, _timed_out = d.maxima_run(text, d.TIMEOUT + d.VERIFY_CAP, [])
    new = " ".join(l for l in out.splitlines() if l.startswith(("GRADE ", "CLASS ")))
    return " ".join(parts[:3]), new or "-", label


def main():
    random.seed(1)
    sample = random.sample([l for l in open(grade_file) if l.startswith("C ")], n)
    print(f"# {grade_file}: {n} of its C entries, seed 1; answer folded by mr_ifold")
    rec = grade_file.replace(".grade.out", ".out")
    for l in open(rec):
        if l.startswith("maxima: Maxima"):
            print("# " + l.strip())
    tally = {}
    with cf.ThreadPoolExecutor(12) as ex:
        for old, new, label in ex.map(one, sample):
            print(f"{old:30s} -> {new:40s} {label}")
            w = new.split()
            key = (w[1] if len(w) > 1 else "-", w[-1] if w else "-")
            tally[key] = tally.get(key, 0) + 1
    print("# folded grade / class:")
    for (g, c), k in sorted(tally.items()):
        print(f"#   {k:3d}  {g} {c}")


if __name__ == "__main__":
    main()
