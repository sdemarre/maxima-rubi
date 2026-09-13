#!/usr/bin/env python3
"""probes/matcher/01-corpus-arity.py -- Plus/Times argument counts of the
class-1..3 corpus integrands, as Maxima stores them after simplification.

Why: the matcher spike (01-mma4max-feasibility) measured mma4max's
Flat+Orderless search (matchfol) growing ~3x per extra summand against a
3-term Plus pattern (SCALE lines of 01-mma4max-feasibility.out).  This probe
measures how many arguments the Plus/Times nodes of real corpus integrands
have, so the growth can be read against the corpus.

Reads every entry of the class 1-3 sections with test/corpus_driver.py's own
reader (extract_entries, split_elements, normalize_heads), simplifies each
integrand in ONE maxima process (parse_string + meval, 10 s cap each) and
records, per entry: the largest Plus argument count anywhere in the tree, the
largest Times argument count anywhere, and the top-level node kind/count.

Run:  python3 probes/matcher/01-corpus-arity.py > probes/matcher/01-corpus-arity.out
"""
import collections
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "test"))
_argv, sys.argv = sys.argv, sys.argv[:1]   # corpus_driver reads argv at import
import corpus_driver as cd                # noqa: E402
sys.argv = _argv

SECTIONS = ["1 Algebraic functions", "2 Exponentials", "3 Logarithms"]

LISP = r"""
(in-package :maxima)
(defun mr-arity-walk (e)
  (if (atom e)
      (values 0 0)
      (let ((mp 0) (mt 0))
        (case (caar e)
          (mplus (setf mp (length (cdr e))))
          (mtimes (setf mt (length (cdr e)))))
        (dolist (a (cdr e))
          (multiple-value-bind (p q) (mr-arity-walk a)
            (setf mp (max mp p) mt (max mt q))))
        (values mp mt))))
(with-open-file (out "%OUT%" :direction :output :if-exists :supersede)
  (with-open-file (in "%IN%")
    (loop for form = (read in nil) while form
          do (destructuring-bind (label text) form
               (let ((r (handler-case
                            (sb-ext:with-timeout 10
                              (let ((e (meval (meval (list (list '$parse_string) text)))))
                                (multiple-value-bind (mp mt) (mr-arity-walk e)
                                  (format nil "~a~c~a~c~a~c~a"
                                          mp #\Tab mt #\Tab
                                          (if (and (consp e) (member (caar e) '(mplus mtimes)))
                                              (if (eq (caar e) 'mplus) "plus" "times")
                                              "other")
                                          #\Tab
                                          (if (and (consp e) (member (caar e) '(mplus mtimes)))
                                              (length (cdr e)) 1)))))
                          (sb-ext:timeout () "TIMEOUT")
                          (error () "ERROR"))))
                 (format out "~a~c~a~%" label #\Tab r)
                 (finish-output out))))))
"""


def lisp_string(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def pct(sorted_vals, q):
    if not sorted_vals:
        return 0
    return sorted_vals[min(len(sorted_vals) - 1, int(q * len(sorted_vals)))]


def main():
    rows = []
    bad = 0
    for section in SECTIONS:
        base = os.path.join(cd.SUITE, section)
        files = []
        for dirpath, _dn, fns in os.walk(base):
            files += [os.path.join(dirpath, f) for f in fns if f.endswith(".mac")]
        for path in sorted(files, key=lambda p: os.path.relpath(p, cd.SUITE)):
            rel = os.path.relpath(path, cd.SUITE)
            try:
                entries, line_nos = cd.extract_entries(path)
            except (AssertionError, UnicodeDecodeError, IndexError):
                bad += 1
                continue
            for idx, ent in enumerate(entries):
                els = cd.split_elements(ent[1:-1])
                if len(els) not in (4, 5):
                    bad += 1
                    continue
                rows.append((section, f"{rel} e{idx + 1} L{line_nos[idx]}",
                             cd.normalize_heads(els[0])))

    with tempfile.TemporaryDirectory() as tmp:
        data = os.path.join(tmp, "integrands.lisp")
        result = os.path.join(tmp, "arity.tsv")
        script = os.path.join(tmp, "arity.lisp")
        with open(data, "w", encoding="utf-8") as f:
            for _s, label, text in rows:
                f.write(f"({lisp_string(label)} {lisp_string(text)})\n")
        with open(script, "w", encoding="utf-8") as f:
            f.write(LISP.replace("%IN%", data).replace("%OUT%", result))
        build = subprocess.run(
            ["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
            capture_output=True, text=True, timeout=120, cwd=ROOT).stdout
        subprocess.run(
            ["maxima", "--very-quiet", "--batch-string", f':lisp (load "{script}")\n'],
            capture_output=True, text=True, timeout=7200, cwd=ROOT)
        got = {}
        with open(result, encoding="utf-8") as f:
            for line in f:
                label, _, rest = line.rstrip("\n").partition("\t")
                got[label] = rest

    print("=== probes/matcher/01-corpus-arity  run: "
          + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    for line in build.splitlines():
        line = line.strip()
        if line.startswith(("Maxima", "Lisp ", "Host ")):
            print(f"maxima: {line}")
    print(f"entries read: {len(rows)}  bad entry shapes/files skipped: {bad}  "
          f"results: {len(got)}")
    print()
    thresholds = (4, 6, 8, 10, 12)
    for section in SECTIONS + ["ALL"]:
        mp_all, mt_all, top_all, fails = [], [], [], collections.Counter()
        for s, label, _t in rows:
            if section != "ALL" and s != section:
                continue
            r = got.get(label, "MISSING")
            if r in ("ERROR", "TIMEOUT", "MISSING"):
                fails[r] += 1
                continue
            mp, mt, kind, top = r.split("\t")
            mp_all.append(int(mp))
            mt_all.append(int(mt))
            top_all.append(int(top) if kind in ("plus", "times") else 1)
        n = len(mp_all)
        both = sorted(max(a, b) for a, b in zip(mp_all, mt_all))
        print(f"SECTION {section}: n={n} failures={dict(fails)}")
        for name, vals in (("max Plus args anywhere", sorted(mp_all)),
                           ("max Times args anywhere", sorted(mt_all)),
                           ("max Plus-or-Times args anywhere", both),
                           ("top-level Plus/Times args", sorted(top_all))):
            counts = "  ".join(
                f">={t}: {sum(1 for v in vals if v >= t)} "
                f"({100.0 * sum(1 for v in vals if v >= t) / max(n, 1):.2f}%)"
                for t in thresholds)
            print(f"  {name:34s} p50 {pct(vals, .5)} p90 {pct(vals, .9)} "
                  f"p99 {pct(vals, .99)} max {vals[-1] if vals else 0}   {counts}")
        print()


if __name__ == "__main__":
    main()
