#!/usr/bin/env python3
"""Option (a) of .scratch/answer-quality/issues/01: fold %i out of EVERY rubi
answer at depth 0 -- does it make any answer worse, in any section?

Probe 04 measured the fold on a sample of section 6's C entries. This one
measures it on every entry where it can act, in the sections given. By the
grade's own rule (test/mr_grade.lisp $mr_grade: same-or-lower ExpnType, the
answer carries %i and the optimal does not -> C), an A or B answer carries
%i only when its optimal does. So the fold, which leaves an %i-free
expression untouched, can only act on
  - the C entries, and
  - the A/B entries whose optimal (the corpus text, normalised) holds %i.
F and ungraded entries are skipped (no answer, or an integral in it).

Each entry runs the corpus driver's own entry text (build_text) with
  mr_r0: rubi(mr_f, x),  mr_r: mr_ifold(mr_r0)  (errcatch'd; mr_r0 on error)
and prints the grade of BOTH (GRADE0 unfolded, GRADE folded), IFOLD
same|changed (is(mr_r0 = mr_r)), and, only when the fold changed the answer,
the checker's verdict on the folded answer, read by the driver's own
classify_entry (so a kill while verifying is classed from the NUMERIC lines,
`/verify-timeout`, as in the records); an unchanged answer prints CLASS
unchanged (its verdict is the record's). The fold is probe 04's mr_ifold,
byte-identical, run under radexpand:false, logexpand:false -- the flags
mr_top binds around its dispatch, i.e. where an mr_top fold would run.
MR_IFOLD_FLAGS=default folds under Maxima's defaults instead: there the
simplifier splits the folded powers, (-%i*y)^(2/3) -> -y^(2/3), which is
wrong on the principal branch (6.4.2 e14: the folded answer mismatches). The
optional MR_IFOLD_ONLY=<file> keeps the candidates whose label is a line of it.

    setsid python3 probes/leaf-size/05-ifold-all-sections.py 0 1 2 3 4 5 6 7 8 \\
        > probes/leaf-size/05-ifold-all-sections.out 2> .../05.err < /dev/null &

Each line: the record's class, its proof tag (the shards' .proof sidecars)
and the sidecar's grade, then GRADE0 / GRADE / IFOLD / CLASS / PROOF of the
run, then the label. The census at the end counts, per section, changed
answers, grade transitions GRADE0 -> GRADE among them, and the entries whose
record class is PASS and whose folded class is not.
"""

import concurrent.futures as cf
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sections = sys.argv[1:]
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
LOADS = 'load("test/mr_verify.mac")$\n'
GRADE = 'errcatch(mr_say(mr_grade_line("GRADE", mr_r, MR_opt))), mr_check_entry('
FLAGS = os.environ.get("MR_IFOLD_FLAGS", "model")
assert FLAGS in ("model", "default"), FLAGS
CALL_FOLD = ("mr_ifold(mr_r0)" if FLAGS == "default"
             else "block([radexpand: false, logexpand: false], mr_ifold(mr_r0))")
FOLD = (f'mr_r: block([MR_e: errcatch({CALL_FOLD})], '
        'if MR_e = [] then (print("IFOLD error"), mr_r0) else first(MR_e))$\n'
        'MR_same: is(mr_r0 = mr_r)$\n'
        'print(if MR_same then "IFOLD same" else "IFOLD changed")$\n')
NEW_GRADE = ('errcatch(mr_say(mr_grade_line("GRADE", mr_r0, MR_opt))), '
             'errcatch(mr_say(mr_grade_line("GRADE", mr_r, MR_opt))), '
             'if MR_same then disp("CLASS unchanged") else mr_check_entry(')

_cache = {}


def elements(label):
    rel, e, _l = label.rsplit(" ", 2)
    if rel not in _cache:
        _cache[rel] = d.extract_entries(os.path.join(d.SUITE, rel))[0]
    return d.split_elements(_cache[rel][int(e[1:]) - 1][1:-1])


def proof_tags(s):
    tags = {}
    for f in glob.glob(f"test/corpus_class{s}.shard*.proof"):
        for l in open(f):
            t, lab = l.rstrip("\n").split(" ", 1)
            tags[lab.strip()] = t
    return tags


def candidates(s):
    only = os.environ.get("MR_IFOLD_ONLY")
    only = None if not only else {l.strip() for l in open(only) if l.strip()}
    tags = proof_tags(s)
    rec = {}
    for l in open(f"test/corpus_class{s}.out"):
        w = l.split()
        if len(w) > 3 and w[1] == "t=":
            rec[l.split("s ", 1)[1].strip()] = w[0]
    out = []
    for l in open(f"test/corpus_class{s}.grade.out"):
        g = l.split(" ", 1)[0]
        if g not in ("A", "B", "C") or " leaf=" not in l:
            continue
        label = l.split(" ", 3)[3].strip()
        if only is not None and label not in only:
            continue
        if g == "C" or "%i" in d.normalize_heads(elements(label)[3]):
            out.append((s, rec.get(label, "?"), tags.get(label, "-"), g, label))
    return out


def one(c):
    s, rcls, rtag, g, label = c
    els = elements(label)
    text = d.build_text(d.normalize_heads(els[0]), els[1], d.normalize_heads(els[3]),
                        d.normalize_heads(els[4]) if len(els) == 5 else None, None)
    call = f"mr_r: rubi(mr_f, {els[1]})$"
    for old in (call, LOADS, GRADE):
        if text.count(old) != 1:
            return c, {"IFOLD": "skipped"}
    text = text.replace(call, f"mr_r0: rubi(mr_f, {els[1]})$")
    text = text.replace(LOADS, LOADS + IFOLD + FOLD)
    text = text.replace(GRADE, NEW_GRADE)
    out, hit = d.maxima_run(text, d.TIMEOUT + d.VERIFY_CAP, [])
    # mr_grade_line prints its own tag, GRADE, whatever it is passed: the
    # first GRADE line is the unfolded answer's, the second the folded one's.
    # disp indents its line.
    get, grades = {}, []
    for ln in (x.strip() for x in out.splitlines()):
        if ln.startswith("GRADE "):
            grades.append(ln.split(" ", 1)[1])
        if ln.startswith("IFOLD ") and "IFOLD" not in get:
            get["IFOLD"] = ln.split(" ", 1)[1].strip()
    if len(grades) >= 2:
        get["GRADE0"], get["GRADE"] = grades[0], grades[1]
    if get.get("IFOLD") == "same":
        get["CLASS"] = "unchanged"
    else:
        r = d.classify_entry(out, hit)
        get["CLASS"], get["PROOF"] = r.cls, r.proof or "-"
    return c, get


def main():
    cands = [c for s in sections for c in candidates(s)]
    print(f"# sections {' '.join(sections)}: {len(cands)} candidates "
          f"(C, or A/B with %i in the optimal); answer folded by mr_ifold (probe 04), flags {FLAGS}")
    for l in open(f"test/corpus_class{sections[0]}.out"):
        if l.startswith("maxima: Maxima"):
            print("# " + l.strip())
    sys.stdout.flush()
    tally = {}
    with cf.ThreadPoolExecutor(12) as ex:
        for (s, rcls, rtag, g, label), get in ex.map(one, cands):
            g0 = get.get("GRADE0", "-").split(" ")[0]
            g1 = get.get("GRADE", "-").split(" ")[0]
            print(f"{rcls:12s} {rtag:24s} {g} -> GRADE0 {get.get('GRADE0', '-'):14s} "
                  f"GRADE {get.get('GRADE', '-'):14s} IFOLD {get.get('IFOLD', '-'):8s} "
                  f"CLASS {get.get('CLASS', '-'):12s} PROOF {get.get('PROOF', '-'):24s} "
                  f"{label}", flush=True)
            t = tally.setdefault(s, {"n": 0, "changed": 0, "trans": {}, "lost": 0, "err": 0})
            t["n"] += 1
            if get.get("IFOLD") == "changed":
                t["changed"] += 1
                k = f"{g0}->{g1}"
                t["trans"][k] = t["trans"].get(k, 0) + 1
                if rcls in d.PASS_CLASSES and get.get("CLASS") not in d.PASS_CLASSES:
                    t["lost"] += 1
            elif get.get("IFOLD") != "same":
                t["err"] += 1
    print("# census per section: candidates, changed, grade GRADE0->GRADE among changed, "
          "PASS lost (record PASS, folded CLASS not), no IFOLD line")
    for s in sections:
        t = tally.get(s, {"n": 0, "changed": 0, "trans": {}, "lost": 0, "err": 0})
        tr = " ".join(f"{k}:{v}" for k, v in sorted(t["trans"].items()))
        print(f"#   {s}: n={t['n']} changed={t['changed']} lost={t['lost']} "
              f"no-ifold={t['err']}  {tr}")


if __name__ == "__main__":
    main()
