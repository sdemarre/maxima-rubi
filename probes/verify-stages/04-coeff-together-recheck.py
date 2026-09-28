#!/usr/bin/env python3
"""probes/verify-stages/04-coeff-together-recheck.py -- the 186 numeric-mismatch
entries of probes/verify-stages/02-mismatch-triage.out, re-run through the
corpus driver (symbolic-first checker) after %mr_coeff took Rubi's Together
fallback (branch coeff-together). Prints each entry's new class and proof tag
with its 02 triage verdict, then a cross-tab.

Usage (repo root):
  python3 probes/verify-stages/04-coeff-together-recheck.py > probes/verify-stages/04-coeff-together-recheck.out
"""
import collections, concurrent.futures, importlib.util, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = "reference/maxima-syntax-test-suite"
TRIAGE = os.path.join(ROOT, "probes", "verify-stages", "02-mismatch-triage.out")


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


def main():
    items = []
    for line in open(TRIAGE, encoding="utf-8"):
        m = re.match(r"^== (\S+)  (.*)$", line.rstrip("\n"))
        if m:
            items.append((m.group(1), m.group(2)))
    drivers = {}
    for _v, lab in items:
        sec = lab.split("/")[0]
        if sec not in drivers:
            drivers[sec] = load_driver(sec)

    def run(item):
        verdict, lab = item
        d = drivers[lab.split("/")[0]]
        m = re.match(r"(.*) e(\d+) L(\d+)$", lab)
        rel, n = m.group(1), int(m.group(2))
        entries, line_nos = d.extract_entries(os.path.join(ROOT, SUITE, rel))
        cls, _line, _caps, proof = d.run_entry_full(rel, n - 1, entries[n - 1], line_nos[n - 1])
        return verdict, lab, cls, proof

    with concurrent.futures.ThreadPoolExecutor(12) as ex:
        results = list(ex.map(run, items))
    tab = collections.Counter()
    for verdict, lab, cls, proof in results:
        print(f"{verdict:12s} {cls:11s} {proof or '-':45s} {lab}")
        tab[(verdict, cls if cls in ("verified", "expected") else cls)] += 1
    print("\n# 02 verdict -> new class")
    for (v, c), k in sorted(tab.items()):
        print(f"#   {v:12s} {c:11s} {k}")


if __name__ == "__main__":
    main()
