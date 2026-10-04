#!/usr/bin/env python3
"""probes/integrate-beats-rubi/06-737-piecewise-linear-derivative.py

Why does 7.3.7 have 119 entries graded A for native Maxima and not for
maxima-rubi? The grade report (2026-10-03) said native Maxima reduces
atanh(tanh(a+b*x)) to a+b*x before integrating. It does not, in general:
integrate(atanh(tanh(a+b*x)), x) = x*atanh(tanh(b*x+a)) - b*x^2/2.

Hypothesis: maxima-rubi answers through Rubi's piecewise-linear rule 9.2 r1,
    Int[u^m, x] := With[{c = Simplify[D[u, x]]}, 1/c * Subst[Int[x^m, x], x, u]]
Mathematica's Simplify reduces D[atanh(tanh(a+b x)), x] to b; maxima-rubi's
%mr_simp leaves b*sech(..)^2/(1 - tanh(..)^2), so the answer is Rubi's own
shape times an unreduced identity factor, and its leaf size passes twice the
optimal's.

For each of the 119 entries (rubi graded below A, native A, in the current
grade censuses) this re-runs rubi in the rules core with the trace on and
records: the grade; whether the answer holds sech (no integrand here does);
whether a 9_2 rule fired; and the grade of trigsimp(answer), an indication of
what the reduced derivative would give.

    python3 probes/integrate-beats-rubi/06-737-piecewise-linear-derivative.py \
        > probes/integrate-beats-rubi/06-737-piecewise-linear-derivative.out
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "test"))
sys.argv = ["corpus_driver.py"]
import corpus_driver as d  # noqa: E402

REL = ("7 Inverse hyperbolic functions/7.3 Inverse hyperbolic tangent/"
       "7.3.7 Inverse hyperbolic tangent functions.mac")
G = re.compile(r"^(\S+) leaf=\S+ type=\S+ (.*) e(\d+) L\d+$")


def grades(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        m = G.match(line.strip())
        if m and m.group(2) == REL:
            out[int(m.group(3))] = m.group(1)
    return out


rg = grades(os.path.join(ROOT, "test", "corpus_class7.grade.out"))
ng = grades(os.path.join(ROOT, "test", "corpus_class7.baseline.grade.out"))
keys = sorted(k for k in rg if ng.get(k) == "A" and rg[k] != "A")
ents, _ = d.extract_entries(os.path.join(ROOT, "reference", "maxima-syntax-test-suite", REL))

lines = ['display2d:false$', 'load("test/mr_grade.lisp")$', 'rubi_verbose:matches$',
         'mr_rules_in(s) := if not listp(s) then [] else '
         'append([first(s)], apply(append, map(mr_rules_in, last(s))))$']
for k in keys:
    els = d.split_elements(ents[k - 1][1:-1])
    f, opt = d.normalize_heads(els[0]), d.normalize_heads(els[3])
    lines.append(
        f'block([f: {f}, opt: {opt}, res, r, st, g, g2], res: errcatch(rubi(f, x)), '
        f'if res = [] then print("ROW e{k} error") else ('
        f'r: first(first(res)), st: apply(append, map(mr_rules_in, second(first(res)))), '
        f'g: first(mr_grade(r, opt)), g2: first(mr_grade(trigsimp(r), opt)), '
        f'print("ROW", "e{k}", g, "sech", not freeof(sech, r), '
        f'"r9_2", some(lambda([s], is(sequal(substring(s, 1, 5), "9_2 "))), st), '
        f'"trigsimp", g2)))$')
with tempfile.NamedTemporaryFile("w", suffix=".mac", delete=False, dir=ROOT) as fh:
    fh.write("\n".join(lines) + "\n")
try:
    out = subprocess.run(["sbcl", "--core", os.path.join(ROOT, "test", "mr_rules.core"),
                          "--noinform", "--very-quiet", "-b", fh.name],
                         capture_output=True, text=True, cwd=ROOT, stdin=subprocess.DEVNULL,
                         timeout=3600).stdout
finally:
    os.unlink(fh.name)

rows = [l.split() for l in out.splitlines() if l.startswith("ROW ")]
print(f"entries: {len(keys)} (7.3.7, rubi below A, native A)   rows: {len(rows)}")
for r in rows:
    print(" ".join(r[1:]))
ok = [r for r in rows if len(r) == 9]
sech = [r for r in ok if r[4] == "true"]
r92 = [r for r in ok if r[6] == "true"]
both = [r for r in ok if r[4] == "true" and r[6] == "true"]
fixed = [r for r in sech if r[8] == "A"]
print(f"answer holds sech: {len(sech)}   a 9_2 rule fired: {len(r92)}   both: {len(both)}")
print(f"of the sech answers, A after trigsimp: {len(fixed)}")
print(f"grades now: " + ", ".join(f"{g} {sum(1 for r in ok if r[2] == g)}"
                                  for g in sorted({r[2] for r in ok})))
