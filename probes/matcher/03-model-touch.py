#!/usr/bin/env python3
"""probes/matcher/03-model-touch.py -- how many corpus integrands does
Maxima's simplifier store in a shape the Mathematica form does not have?
(02-FINDINGS G-5 counted witnesses; this counts the real class 1..3 corpus.)

For every entry of the class 1-3 sections (read with test/corpus_driver.py's
reader, as 01-corpus-arity.py does), ONE maxima process produces two trees
of the integrand string, both written in Mathematica-form FullForm:
  raw   parse_string with simp:false -- the source as written (the suite
        strings were generated from Mathematica input);
  simp  parse_string evaluated and simplified -- what the package receives
        (optionally under Maxima settings given with --flags).
The raw tree goes through 02-mma-reader.py's emulation of Mathematica's
evaluation (Sqrt/Exp -> Power, numeric folding, Flat/identity rules,
integer powers of products and powers), then both trees are compared order-
insensitively.  A difference means Maxima stores the integrand in a shape
Mathematica does not produce -- not necessarily a lost match.  Kinds are
the head-set change (02-roundtrip.change_kind) plus named signatures.

Run:  python3 probes/matcher/03-model-touch.py > probes/matcher/03-model-touch.out
      python3 probes/matcher/03-model-touch.py --flags "radexpand:false$ domain:complex$" > ...
"""
import argparse
import collections
import importlib.util
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "test"))
_argv, sys.argv = sys.argv, sys.argv[:1]   # corpus_driver reads argv at import
import corpus_driver as cd                # noqa: E402
sys.argv = _argv

_s = importlib.util.spec_from_file_location("rt02", HERE / "02-roundtrip.py")
rt = importlib.util.module_from_spec(_s)
_s.loader.exec_module(rt)
rd = rt.rd

SECTIONS = ["1 Algebraic functions", "2 Exponentials", "3 Logarithms"]

# maxima function name (as parsed or simplified, lower case) -> Mathematica head
HEADS = {m: h for (h, _n), m in rt.MAXIMA_FUN.items()}
HEADS.update({"sqrt": "Sqrt", "exp": "Exp", "polylog": "PolyLog", "li": "PolyLog",
              "mabs": "Abs", "mfactorial": "Factorial"})

LISP = r"""
(in-package :maxima)
(defparameter *mr-heads* (make-hash-table :test 'equal))
%HEADS%
(defun mr-name (sym)
  (let* ((s (symbol-name sym))
         (s (if (and (> (length s) 1) (find (char s 0) "$%")) (subseq s 1) s)))
    (cond ((string= s (string-upcase s)) (string-downcase s))
          ((string= s (string-downcase s)) (string-upcase s))
          (t s))))
(defun mr-sx (e s)
  (cond ((integerp e) (format s "~d" e))
        ((floatp e) (format s "~,,,,,,'eE" e))
        ((stringp e) (prin1 e s))
        ((symbolp e)
         (case e
           ($%e (write-string "E" s))
           ($%pi (write-string "Pi" s))
           ($%i (write-string "I" s))
           (t (write-string (mr-name e) s))))
        ((not (and (consp e) (consp (car e)))) (write-string "BADFORM" s))
        (t
         (let ((op (caar e)) (args (cdr e)))
           (flet ((node (h as)
                    (write-char #\( s) (write-string h s)
                    (dolist (a as) (write-char #\Space s) (mr-sx a s))
                    (write-char #\) s)))
             (case op
               (rat (format s "~d/~d" (first args) (second args)))
               (mplus (node "Plus" args))
               (mtimes (node "Times" args))
               ((mexpt mncexpt) (node "Power" args))
               (mquotient (write-string "(Times " s) (mr-sx (first args) s)
                          (write-string " (Power " s) (mr-sx (second args) s)
                          (write-string " -1))" s))
               (mminus (write-string "(Times -1 " s) (mr-sx (first args) s) (write-char #\) s))
               (t (let ((n (mr-name op)))
                    (node (or (gethash (string-downcase n) *mr-heads*)
                              (concatenate 'string "MX_" n))
                          args)))))))))
(defun mr-sxs (e) (with-output-to-string (s) (mr-sx e s)))
(with-open-file (out "%OUT%" :direction :output :if-exists :supersede)
  (with-open-file (in "%IN%")
    (loop for form = (read in nil) while form
          do (destructuring-bind (label text) form
               (let ((r (handler-case
                            (sb-ext:with-timeout 10
                              (let* ((raw (let (($simp nil))
                                            (meval (list (list '$parse_string) text))))
                                     (simp (meval (meval (list (list '$parse_string) text)))))
                                (format nil "~a~c~a" (mr-sxs raw) #\Tab (mr-sxs simp))))
                          (sb-ext:timeout () "TIMEOUT")
                          (error () "ERROR"))))
                 (format out "~a~c~a~%" label #\Tab r)
                 (finish-output out))))))
"""


def lisp_string(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def heads_of(t, acc=None):
    acc = collections.Counter() if acc is None else acc
    if isinstance(t, tuple):
        acc[rt.head_name(t[0]) if not isinstance(t[0], tuple) else "<compound>"] += 1
        for a in t[1:]:
            heads_of(a, acc)
    return acc


def has(t, pred):
    if isinstance(t, tuple):
        return pred(t) or any(has(a, pred) for a in t)
    return pred(t)


def signatures(raw, simp):
    """Named rewrite signatures (raw = evaluated Mathematica form)."""
    sig = []
    if heads_of(simp)["Abs"] > heads_of(raw)["Abs"]:
        sig.append("abs introduced")
    if has(raw, lambda n: isinstance(n, tuple) and n[0] == "Log" and len(n) == 2
           and isinstance(n[1], tuple) and n[1][0] == "Power") and \
            not has(simp, lambda n: isinstance(n, tuple) and n[0] == "Log" and len(n) == 2
                    and isinstance(n[1], tuple) and n[1][0] == "Power"):
        sig.append("log of a power expanded")

    def numpow(n):
        return (isinstance(n, tuple) and n[0] == "Power" and isinstance(n[1], tuple)
                and n[1][0] == "Times" and not isinstance(n[2], int))
    if sum(1 for _ in iter_nodes(raw, numpow)) > sum(1 for _ in iter_nodes(simp, numpow)):
        sig.append("product base of a non-integer power split")
    if has(raw, lambda n: n == "I"):
        sig.append("involves I")
    trig = {"Sin", "Cos", "Tan", "Cot", "Sec", "Csc"}
    if any(heads_of(raw)[h] for h in trig) and heads_of(raw) != heads_of(simp):
        sig.append("trig heads rewritten")
    return sig or ["other structure"]


def iter_nodes(t, pred):
    if isinstance(t, tuple):
        if pred(t):
            yield t
        for a in t[1:]:
            yield from iter_nodes(a, pred)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flags", default="", help="Maxima statements run before the probe, e.g. 'radexpand:false$'")
    args = ap.parse_args()
    rows, bad = [], 0
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
    heads_lisp = "\n".join('(setf (gethash "%s" *mr-heads*) "%s")' % (m, h) for m, h in sorted(HEADS.items()))
    with tempfile.TemporaryDirectory() as tmp:
        data, result, script = (os.path.join(tmp, n) for n in ("in.lisp", "out.tsv", "probe.lisp"))
        with open(data, "w", encoding="utf-8") as f:
            for _s2, label, text in rows:
                f.write(f"({lisp_string(label)} {lisp_string(text)})\n")
        with open(script, "w", encoding="utf-8") as f:
            f.write(LISP.replace("%IN%", data).replace("%OUT%", result).replace("%HEADS%", heads_lisp))
        build = subprocess.run(["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
                               capture_output=True, text=True, timeout=120, cwd=ROOT).stdout
        batch = (args.flags + "\n" if args.flags else "") + f':lisp (load "{script}")\n'
        subprocess.run(["maxima", "--very-quiet", "--batch-string", batch],
                       capture_output=True, text=True, timeout=7200, cwd=ROOT)
        got = {}
        with open(result, encoding="utf-8") as f:
            for line in f:
                label, _, rest = line.rstrip("\n").partition("\t")
                got[label] = rest

    print("=== probes/matcher/03-model-touch  run: " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    for line in build.splitlines():
        if "build_info" in line or "branch_" in line:
            print("maxima: " + line.strip())
    print("settings before the probe: %s" % (args.flags or "(Maxima defaults)"))
    print("entries read: %d  bad entry shapes/files skipped: %d  results: %d" % (len(rows), bad, len(got)))
    total = collections.Counter()
    for section in SECTIONS + ["ALL"]:
        n = differ = 0
        fails = collections.Counter()
        kinds, sigs = collections.Counter(), collections.Counter()
        examples = {}
        risk = 0
        for s, label, text in rows:
            if section != "ALL" and s != section:
                continue
            r = got.get(label, "MISSING")
            if r in ("ERROR", "TIMEOUT", "MISSING") or "\t" not in r:
                fails[r if r in ("ERROR", "TIMEOUT", "MISSING") else "BADLINE"] += 1
                continue
            raw_s, simp_s = r.split("\t", 1)
            try:
                raw, eff = rd.evaluate_lhs(rt.parse_sexp(raw_s))
                simp = rt.parse_sexp(simp_s)
            except Exception as ex:           # noqa: BLE001 -- reported, not hidden
                fails["PARSE:" + type(ex).__name__] += 1
                if section == "ALL":
                    print("  PARSE-FAIL %s: %s: %s | %s" % (label, type(ex).__name__, ex, r[:160]))
                continue
            n += 1
            risk += any(x.startswith("risk:") for x in eff)
            if rt.cn(raw) != rt.cn(simp):
                differ += 1
                k = rt.change_kind(raw, simp)
                kinds[k] += 1
                for sg in signatures(raw, simp):
                    sigs[sg] += 1
                    examples.setdefault(sg, "%s: %s  ->  %s" % (label, text[:70], simp_s[:110]))
        print()
        print("SECTION %s: compared %d, stored differently from the Mathematica form %d (%s); failures %s; "
              "entries carrying evaluation the reader does not emulate: %d" % (
                  section, n, differ, "%.2f%%" % (100.0 * differ / n) if n else "-", dict(fails), risk))
        print("  signatures (an entry may carry several): %s" % ", ".join("%s %d" % kv for kv in sigs.most_common()))
        print("  head-set change kinds: %s" % ", ".join("[%s] %d" % kv for kv in kinds.most_common(12)))
        if section == "ALL":
            for sg, ex in examples.items():
                print("  e.g. [%s] %s" % (sg, ex))


if __name__ == "__main__":
    main()
