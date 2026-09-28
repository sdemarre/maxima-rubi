#!/usr/bin/env python3
"""probes/verify-stages/02-mismatch-triage.py -- a closer look at the entries the
checker left `none/numeric-mismatch` (probes/verify-stages/01-unverified-subset).

A numeric mismatch is an indication, not a verdict (user, 2026-09-28): it can be
a wrong answer, or a branch, precision or evaluation problem of the numeric
check itself. This probe separates the two by asking the same numeric question
of the CORPUS answer: for each entry, at x = 0.35, 0.65 and 1.7 (the checker's
sweep parameters), it evaluates

    rubi    |diff(r, x) - f|       rubi's residual
    corpus  |diff(e, x) - f|       the corpus answer's own residual
    r-e     |diff(r - e, x)|       rubi against the corpus answer

and reads them:

    corpus-also   the corpus answer mismatches too at a point where rubi does:
                  the numeric check is not trustworthy there (branch / eval)
    rubi-only     the corpus answer checks out, rubi's does not: a candidate
                  wrong answer, for a hand look
    point-split   rubi mismatches at some points only (a branch cut crossing
                  the test interval is the usual cause)
    other         anything else (no corpus answer, declined points)

Each entry runs in a fresh process from the rules core, like the corpus driver
(its head text: switches, rubi call, ANSWERED), 30 s rubi cap + 30 s.

Usage (repo root):
  python3 probes/verify-stages/02-mismatch-triage.py > probes/verify-stages/02-mismatch-triage.out
"""

import concurrent.futures
import glob
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = "reference/maxima-syntax-test-suite"
SUBSET = os.path.join(ROOT, "probes", "verify-stages", "01-unverified-subset")
RERUN = os.path.join(ROOT, "probes", "verify-stages", "01-unverified-subset.out")
POINTS = [0.35, 0.65, 1.7]
TOL = 1e-9

MAC = r'''
mr_tr_subs : [a=0.9, b=1.3, c=0.5, d=0.9, e=1.1, f=0.8, g=1.7, h=0.3,
              A=0.6, B=1.4, C=0.4, D=0.9, p=2]$
mr_tr_val(mr_d, mr_x0) := block([mr_v],
  mr_v : mr_guarded(lambda([], block([mr_w],
    mr_w : rectform(float(mr_rect_li(float(ev(mr_d, append(mr_tr_subs, [x = mr_x0])))))),
    if numberp(realpart(mr_w)) and numberp(imagpart(mr_w)) then cabs(mr_w)
    else "declined"))),
  if listp(mr_v) and mr_v # [] then part(mr_v, 1) else "declined")$
mr_tr_es : EXPECTED$
mr_tr_e : if mr_tr_es[1] = [] then false else part(mr_tr_es[1], 1)$
mr_tr_dv : errcatch(diff(mr_r, x) - mr_f)$
mr_tr_de : if mr_tr_e = false then [] else errcatch(diff(mr_tr_e, x) - mr_f)$
mr_tr_dr : if mr_tr_e = false then [] else errcatch(diff(mr_r - mr_tr_e, x))$
for mr_x0 in POINTS do
  printf(true, "TRI ~a ~a ~a ~a~%", mr_x0,
         if mr_tr_dv = [] then "declined" else mr_tr_val(part(mr_tr_dv, 1), mr_x0),
         if mr_tr_de = [] then "declined" else mr_tr_val(part(mr_tr_de, 1), mr_x0),
         if mr_tr_dr = [] then "declined" else mr_tr_val(part(mr_tr_dr, 1), mr_x0))$
printf(true, "RUBI ~a~%", string(mr_r))$
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


def mismatch_labels():
    labels = []
    for path in sorted(glob.glob(os.path.join(SUBSET, "class*", "shard*.proof"))):
        for line in open(path, encoding="utf-8"):
            tag, _, label = line.rstrip("\n").partition(" ")
            if "numeric-mismatch" in tag:
                labels.append(label)
    # the 18 entries the first pass read `error`, re-run after the fixes
    for line in open(RERUN, encoding="utf-8"):
        if "numeric-mismatch" in line and " | " in line:
            labels.append(line.split(" | ", 1)[1].strip())
    return sorted(set(labels))


def run(drv, label):
    m = re.match(r"(.*) e(\d+) L(\d+)$", label)
    rel, n = m.group(1), int(m.group(2))
    entries, _ = drv.extract_entries(os.path.join(ROOT, SUITE, rel))
    els = drv.split_elements(entries[n - 1][1:-1])
    f_text = drv.normalize_heads(els[0])
    e_text = drv.normalize_heads(els[3])
    head = drv.build_text(f_text, els[1], e_text)
    cut = head.index('load("test/mr_verify.mac")$\n') + len('load("test/mr_verify.mac")$\n')
    text = (head[:cut] + MAC.replace("EXPECTED", f"[errcatch({e_text})]")
            .replace("POINTS", "[" + ", ".join(map(str, POINTS)) + "]"))
    out, _timed_out = drv.maxima_run(text, drv.TIMEOUT + drv.VERIFY_CAP)
    rows, rubi = [], None
    for line in out.splitlines():
        if line.startswith("TRI "):
            rows.append(line.split()[1:])
        elif line.startswith("RUBI "):
            rubi = line[5:]
    return label, f_text, e_text, rows, rubi


def num(s):
    try:
        return float(s)
    except ValueError:
        return None


def verdict(rows):
    if len(rows) != len(POINTS):
        return "other"
    bad_r = [num(r[1]) is not None and num(r[1]) > TOL for r in rows]
    bad_e = [num(r[2]) is not None and num(r[2]) > TOL for r in rows]
    ok_e = [num(r[2]) is not None and num(r[2]) <= TOL for r in rows]
    if not any(bad_r):
        return "other"
    if any(br and be for br, be in zip(bad_r, bad_e)):
        return "corpus-also"
    if all(br == (num(r[1]) is not None) for br, r in zip(bad_r, rows)) and all(ok_e):
        return "rubi-only"
    if any(num(r[1]) is not None and num(r[1]) <= TOL for r in rows):
        return "point-split"
    return "other"


def main():
    labels = mismatch_labels()
    drivers = {}
    for lab in labels:
        sec = lab.split("/")[0]
        if sec not in drivers:
            drivers[sec] = load_driver(sec)
    print(f"# {len(labels)} numeric-mismatch entries; points x = {POINTS}; tol {TOL}")
    print("# columns per point: x  |rubi resid|  |corpus resid|  |d(rubi - corpus)|")
    results = []
    with concurrent.futures.ThreadPoolExecutor(12) as ex:
        futs = [ex.submit(run, drivers[l.split("/")[0]], l) for l in labels]
        for fu in futs:
            results.append(fu.result())
    counts = {}
    for label, f_text, e_text, rows, rubi in results:
        v = verdict(rows)
        counts[v] = counts.get(v, 0) + 1
        print(f"\n== {v}  {label}")
        print(f"   f      {f_text}")
        print(f"   rubi   {rubi}")
        print(f"   corpus {e_text}")
        for r in rows:
            print("   " + "  ".join(f"{c:>22}" for c in r))
    print("\n# verdicts: " + "  ".join(f"{k} {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
