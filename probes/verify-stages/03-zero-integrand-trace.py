#!/usr/bin/env python3
"""probes/verify-stages/03-zero-integrand-trace.py -- for every `rubi-only`
entry of probes/verify-stages/02-mismatch-triage.out (the corpus answer passes
the numeric check at all three points, rubi's does not), trace rubi with
rubi_verbose : 'matches and name every rule step with a 9_1 r8 child
(Int[0, x] -> 0) -- a rule whose result carries an integral of zero, which
vanishes and takes its term out of the answer.

The first case found by hand (2026-09-28): 1.2.1.4 e122,
x/((d+e*x)*sqrt(d^2-e^2*x^2)): 1_1_3_7 r37 matched Pq = -(e*x)/(e*x+d) -
d/(e*x+d) (the constant -1 in fraction form); %mr_polyQ reads it through
Together and accepts it, %mr_coeff reads it WITHOUT Together and gets 0 for
every coefficient -- Rubi's Coeff (IntegrationUtilityFunctions.m:1249) takes
the Together coefficient when the two differ; the port does not.

Usage (repo root):
  python3 probes/verify-stages/03-zero-integrand-trace.py > probes/verify-stages/03-zero-integrand-trace.out
"""

import collections
import concurrent.futures
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = "reference/maxima-syntax-test-suite"
TRIAGE = os.path.join(ROOT, "probes", "verify-stages", "02-mismatch-triage.out")

MAC = r'''
display2d : false$
rubi_verbose : 'matches$
/* a step is [rule, integrand, result, children]; a child that is 9_1 r8
   (Int[0, x] -> 0) means its parent produced the zero integral */
mr_zt_walk(s) := if listp(s) and length(s) = 4 then (
    if some(lambda([c], listp(c) and length(c) = 4 and c[1] = "9_1 r8"), s[4])
      and s[1] # "9_1 r8" then
      printf(true, "ZERO ~a~%", s[1]),
    map(mr_zt_walk, s[4]))$
mr_zt_r : rubi(F, x)$
for mr_zt_s in mr_zt_r[2] do mr_zt_walk(mr_zt_s)$
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


def rubi_only():
    labels = []
    for line in open(TRIAGE, encoding="utf-8"):
        m = re.match(r"^== rubi-only  (.*)$", line.rstrip("\n"))
        if m:
            labels.append(m.group(1))
    return labels


def run(drv, label):
    m = re.match(r"(.*) e(\d+) L(\d+)$", label)
    rel, n = m.group(1), int(m.group(2))
    entries, _ = drv.extract_entries(os.path.join(ROOT, SUITE, rel))
    els = drv.split_elements(entries[n - 1][1:-1])
    text = MAC.replace("F", "(" + drv.normalize_heads(els[0]) + ")", 1)
    out, timed_out = drv.maxima_run(text, drv.TIMEOUT + drv.VERIFY_CAP)
    zeros = [l.split()[1] + " " + l.split()[2] for l in out.splitlines()
             if l.startswith("ZERO ")]
    done = any(l.strip() == "DONE" for l in out.splitlines())
    return label, zeros, done, timed_out


def main():
    labels = rubi_only()
    drivers = {}
    for lab in labels:
        sec = lab.split("/")[0]
        drivers.setdefault(sec, None)
    for sec in drivers:
        drivers[sec] = load_driver(sec)
    with concurrent.futures.ThreadPoolExecutor(12) as ex:
        results = list(ex.map(lambda l: run(drivers[l.split("/")[0]], l), labels))
    by_rule = collections.Counter()
    with_zero = 0
    for label, zeros, done, timed_out in results:
        state = "" if done else ("  (TIMEOUT)" if timed_out else "  (NO TRACE)")
        print(f"{', '.join(sorted(set(zeros))) or '-':40s} {label}{state}")
        if zeros:
            with_zero += 1
        for z in set(zeros):
            by_rule[z] += 1
    print(f"\n# {with_zero} of {len(results)} rubi-only entries have a rule step "
          f"whose result carries an integral of zero (a 9_1 r8 child)")
    for rule, n in by_rule.most_common():
        print(f"#   {n:4d}  {rule}")


if __name__ == "__main__":
    main()
