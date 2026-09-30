#!/usr/bin/env python3
"""probes/verify-stages/05-wrong-answer-traces.py -- the 36 entries still
wrong after the %mr_coeff Together fix (probes/verify-stages/04: `rubi-only`
in the 02 triage -- the corpus answer checks out numerically, rubi's does
not -- and still `unverified`). For each: the integrand, rubi's answer, the
corpus answer, the residuals at x = 0.35 / 0.65 / 1.7 (the checker's sweep
parameters; |rubi resid|, |corpus resid|), and rubi's rule trace
(rubi_verbose : 'matches), one line per step: depth, rule, integrand.

Usage (repo root):
  python3 probes/verify-stages/05-wrong-answer-traces.py > probes/verify-stages/05-wrong-answer-traces.out
"""
import concurrent.futures
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = "reference/maxima-syntax-test-suite"
RECHECK = os.path.join(ROOT, "probes", "verify-stages", "04-coeff-together-recheck.out")

MAC = r'''
display2d : false$
mr_tw_subs : [a=0.9, b=1.3, c=0.5, d=0.9, e=1.1, f=0.8, g=1.7, h=0.3,
              A=0.6, B=1.4, C=0.4, D=0.9, p=2]$
mr_tw_val(mr_d, mr_x0) := block([errormsg : false, mr_v],
  mr_v : errcatch(rectform(float(mr_rect_li(float(ev(mr_d, append(mr_tw_subs, [x = mr_x0]))))))),
  if mr_v = [] then "declined"
  else if numberp(realpart(part(mr_v, 1))) and numberp(imagpart(part(mr_v, 1)))
    then cabs(part(mr_v, 1)) else "declined")$
mr_tw_walk(s, dep) := if listp(s) and length(s) = 4 then (
    printf(true, "STEP ~a ~a | ~a~%", dep, s[1], string(s[2])),
    for c in s[4] do mr_tw_walk(c, dep + 1))$
mr_tw_f : FF$
mr_tw_e : EE$
rubi_verbose : 'matches$
mr_tw_rr : rubi(mr_tw_f, x)$
rubi_verbose : false$
mr_tw_r : mr_tw_rr[1]$
printf(true, "RUBI ~a~%", string(mr_tw_r))$
mr_tw_dv : diff(mr_tw_r, x) - mr_tw_f$
mr_tw_de : diff(mr_tw_e, x) - mr_tw_f$
for mr_x0 in [0.35, 0.65, 1.7] do
  printf(true, "RES ~a ~a ~a~%", mr_x0, mr_tw_val(mr_tw_dv, mr_x0), mr_tw_val(mr_tw_de, mr_x0))$
for mr_tw_s in mr_tw_rr[2] do mr_tw_walk(mr_tw_s, 0)$
printf(true, "DONE~%")$
'''


def load_driver(section):
    real = sys.argv[:]
    sys.argv = ["corpus_driver.py", section + "/", "999999", "30", SUITE]
    try:
        spec = importlib.util.spec_from_file_location(
            "drv_" + section[0], os.path.join(ROOT, "test", "corpus_driver.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.argv = real


def labels():
    out = []
    for line in open(RECHECK, encoding="utf-8"):
        parts = line.split(None, 3)
        if len(parts) == 4 and parts[0] == "rubi-only" and parts[1] == "unverified":
            out.append(parts[3].strip())
    return out


def run(drv, label):
    m = re.match(r"(.*) e(\d+) L(\d+)$", label)
    rel, n = m.group(1), int(m.group(2))
    entries, _ = drv.extract_entries(os.path.join(ROOT, SUITE, rel))
    els = drv.split_elements(entries[n - 1][1:-1])
    f_text, e_text = drv.normalize_heads(els[0]), drv.normalize_heads(els[3])
    text = ('load("test/mr_verify.mac")$\n'
            + MAC.replace("FF", "(" + f_text + ")").replace("EE", "(" + e_text + ")"))
    out, timed_out = drv.maxima_run(text, drv.TIMEOUT + drv.VERIFY_CAP)
    lines = [l for l in out.splitlines() if l.startswith(("RUBI ", "RES ", "STEP "))]
    done = any(l.strip() == "DONE" for l in out.splitlines())
    return label, f_text, e_text, lines, done, timed_out


def main():
    labs = labels()
    drivers = {}
    for lab in labs:
        sec = lab.split("/")[0]
        if sec not in drivers:
            drivers[sec] = load_driver(sec)
    with concurrent.futures.ThreadPoolExecutor(12) as ex:
        results = list(ex.map(lambda l: run(drivers[l.split("/")[0]], l), labs))
    results.sort(key=lambda r: r[0])
    print(f"# {len(results)} entries")
    for label, f_text, e_text, lines, done, timed_out in results:
        state = "" if done else ("  (TIMEOUT)" if timed_out else "  (INCOMPLETE)")
        print(f"\n== {label}{state}")
        print(f"   f      {f_text}")
        print(f"   corpus {e_text}")
        for l in lines:
            if l.startswith("RUBI "):
                print(f"   rubi   {l[5:]}")
            elif l.startswith("RES "):
                print(f"   res    {l[4:]}")
            else:
                _, dep, rest = l.split(" ", 2)
                print(f"   {'  ' * int(dep)}{rest}")


if __name__ == "__main__":
    main()
