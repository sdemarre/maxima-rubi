#!/usr/bin/env python3
"""probes/dispatch-index/03-boolcheck-differential.py -- ticket 21 step 1.

The native %mr_containsBoolean (maxima_rubi_dispatch.lisp) must answer what
the retired Maxima walk answered.  The unit witnesses cover the documented
cases; this probe covers the REAL inputs: every binding list and answer the
dispatcher checks while rubi runs a corpus sample from every class.  See
03-boolcheck-differential.lisp: each call computes both, counts
disagreements, and returns the old walk's answer.

Sample: from each class record test/corpus_class<N>.out, every entry whose
verdict is `verified` with t <= 3 s, taken at an even stride, PER_CLASS of
them (default 60), plus every entry of any class whose record verdict is
`unverified`, `contains-noun` or `no-answer` in the same stride (where a
misfire path is more likely).  One maxima process per class, entries in
sequence, each under errcatch; a class process is killed after CAP seconds
(its BD line is then missing, which the summary reports).

Starts from the rules core named by MR_RULES_CORE_PATH (default
test/mr_rules.core), which must carry the RETIRED walk as the Maxima
function %mr_containsBoolean or not -- either way the native dispatcher file
of this tree is loaded on top.

Usage (repo root):
  python3 probes/dispatch-index/03-boolcheck-differential.py \\
      > probes/dispatch-index/03-boolcheck-differential.out 2>&1
"""
import os, re, signal, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
CORE = os.environ.get("MR_RULES_CORE_PATH", os.path.join(ROOT, "test", "mr_rules.core"))
PER_CLASS = int(os.environ.get("PER_CLASS", "60"))
CAP = int(os.environ.get("CAP", "900"))
SBCL = subprocess.run(["sh", "-c", "command -v sbcl"], capture_output=True, text=True).stdout.strip()

REF = r'''ref_containsBoolean(e) := block([i, hit],
  if atom(e) then is(string(e) = "true") or is(string(e) = "false")
  else if op(e) = "if" or op(e) = "block" or op(e) = "lambda"
    or op(e) = "let" or op(e) = "letf" or op(e) = "do"
    or op(e) = "for" or op(e) = "while" or op(e) = "when"
  then false
  else if op(e) = "-" then (
    ref_containsBoolean(part(e, 1))
  )
  else (
    hit : false,
    for i : 1 thru length(e) do (
      if ref_containsBoolean(part(e, i)) then hit : true
    ),
    hit))$
'''

LINE = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s (.*\.mac) e(\d+) L(\d+)$")


def sample(cls):
    rec = os.path.join(ROOT, "test", f"corpus_class{cls}.out")
    rows = []
    for ln in open(rec, encoding="utf-8"):
        m = LINE.match(ln.rstrip("\n"))
        if not m:
            continue
        verdict, t, path, e, L = m.groups()
        if float(t) > 3.0:
            continue
        if verdict in ("verified", "unverified", "contains-noun", "no-answer"):
            rows.append((verdict, path, int(e), int(L)))
    stride = max(1, len(rows) // PER_CLASS)
    return rows[::stride][:PER_CLASS]


def integrand(path, L):
    full = os.path.join(SUITE, path)
    if not os.path.exists(full):  # records written relative to the class dir
        hits = [os.path.join(dp, f) for dp, _, fs in os.walk(SUITE) for f in fs
                if os.path.join(dp, f).endswith(path)]
        full = hits[0]
    line = open(full, encoding="utf-8").read().split("\n")[L - 1].strip()
    body = line[1:].rstrip(",").rstrip("]")
    # [integrand, var, steps, answer]: split on top-level commas
    depth, parts, cur = 0, [], ""
    for ch in body:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur); cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts[0].strip(), parts[1].strip()


def main():
    print("== core:", CORE)
    print(open(CORE + ".stamp").read())
    total = {"calls": 0, "hits": 0, "mismatches": 0}
    for cls in range(1, 9):
        rows = sample(cls)
        with tempfile.TemporaryDirectory() as w:
            mac = os.path.join(w, "d.mac")
            with open(mac, "w") as fh:
                fh.write('display2d : false$ linel : 10000$\n')
                fh.write('print("R build", build_info()@version, build_info()@timestamp)$\n')
                fh.write(f'load("{ROOT}/maxima_rubi_dispatch.lisp")$\n')
                fh.write(REF)
                fh.write(f'load("{ROOT}/probes/dispatch-index/03-boolcheck-differential.lisp")$\n')
                for verdict, path, e, L in rows:
                    f, v = integrand(path, L)
                    fh.write(f'mr_f : {f}$ mr_r : errcatch(rubi(mr_f, {v}))$\n')
                fh.write(f'bd_report("class {cls}: {len(rows)} entries")$\n')
            p = subprocess.Popen([SBCL, "--core", CORE, "--noinform", "--very-quiet", "-b", mac],
                                 stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, start_new_session=True)
            try:
                out, _ = p.communicate(timeout=CAP)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                out, _ = p.communicate()
                print(f"class {cls}: KILLED at {CAP}s")
        for ln in out.splitlines():
            if ln.startswith(("BD ", "R build")) or "MISMATCH" in ln:
                print(ln)
            m = re.match(r"BD .* calls (\d+) hits (\d+) mismatches (\d+)", ln)
            if m:
                for k, g in zip(("calls", "hits", "mismatches"), m.groups()):
                    total[k] += int(g)
        print(f"class {cls}: lisp errors {out.count('Lisp error')}")
        sys.stdout.flush()
    print(f"TOTAL calls {total['calls']} hits {total['hits']} mismatches {total['mismatches']}")


if __name__ == "__main__":
    main()
