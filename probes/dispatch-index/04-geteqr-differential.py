#!/usr/bin/env python3
"""probes/dispatch-index/04-geteqr-differential.py -- ticket 21 step 2.

The native geteqR (maxima_rubi_dispatch.lisp) must return what the retired
Maxima walk returned, object for object.  The unit witnesses cover the
documented cases; this probe covers the REAL calls: every geteqR a rule cond
or repl makes while rubi runs a corpus sample from every class -- the same
sample as probe 03 (03-boolcheck-differential.py's sample()).  See
04-geteqr-differential.lisp.

Usage (repo root):
  python3 probes/dispatch-index/04-geteqr-differential.py \\
      > probes/dispatch-index/04-geteqr-differential.out 2>&1
"""
import importlib.util, os, re, signal, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("p03", os.path.join(HERE, "03-boolcheck-differential.py"))
p03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p03)
ROOT, CORE, CAP, SBCL = p03.ROOT, p03.CORE, p03.CAP, p03.SBCL

REF = r'''ref_geteqR(mm, nm) := block([],
  if length(mm) = 0 then false
    else if is(part(part(mm, 1), 1) = nm) then part(part(mm, 1), 2)
         else ref_geteqR(rest(mm), nm))$
'''


def main():
    print("== core:", CORE)
    print(open(CORE + ".stamp").read())
    total = {"calls": 0, "mismatches": 0}
    for cls in range(1, 9):
        rows = p03.sample(cls)
        with tempfile.TemporaryDirectory() as w:
            mac = os.path.join(w, "d.mac")
            with open(mac, "w") as fh:
                fh.write('display2d : false$ linel : 10000$\n')
                fh.write('print("R build", build_info()@version, build_info()@timestamp)$\n')
                fh.write(f'load("{ROOT}/maxima_rubi_dispatch.lisp")$\n')
                # the core may still carry the retired Maxima geteqR, which
                # would shadow the native one: remove it
                fh.write('if member(\'geteqR, map(op, functions)) then remfunction(geteqR)$\n')
                fh.write(REF)
                fh.write(f'load("{ROOT}/probes/dispatch-index/04-geteqr-differential.lisp")$\n')
                for verdict, path, e, L in rows:
                    f, v = p03.integrand(path, L)
                    fh.write(f'mr_f : {f}$ mr_r : errcatch(rubi(mr_f, {v}))$\n')
                fh.write(f'gd_report("class {cls}: {len(rows)} entries")$\n')
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
            if ln.startswith(("GD ", "R build")) or "MISMATCH" in ln:
                print(ln)
            m = re.match(r"GD class .* calls (\d+) mismatches (\d+)", ln)
            if m:
                total["calls"] += int(m.group(1)); total["mismatches"] += int(m.group(2))
        print(f"class {cls}: lisp errors {out.count('Lisp error')}")
        sys.stdout.flush()
    print(f"TOTAL calls {total['calls']} mismatches {total['mismatches']}")


if __name__ == "__main__":
    main()
