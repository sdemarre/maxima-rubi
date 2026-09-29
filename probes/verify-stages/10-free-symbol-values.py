#!/usr/bin/env python3
"""probes/verify-stages/10-free-symbol-values.py -- give the numeric check
values for the free symbols m, n, q, F (.scratch/corpus-harness/issues/06
item 2). The entries: the `free` rows of 09-declined-census.out (636 of the
968 declined). Each is re-run through the corpus driver with the checker's
mr_numeric_subs extended by one value set (the entry text is patched right
after the checker's load; nothing else changes), and the report reads the
entry's class and proof tag: what the numeric check says once it can
evaluate (a symbolic proof, if any, still wins and is unchanged by values).

Two value sets, positive and non-integer (the families' generic case; an
integer m or n lands on a pole or a degenerate case of many answers):
  V1: m=0.37, n=1.7, q=0.6, F=1.9
  V2: m=1.3, n=0.45, q=1.4, F=2.3

Usage (repo root):
  python3 probes/verify-stages/10-free-symbol-values.py > probes/verify-stages/10-free-symbol-values.out
"""
import collections, concurrent.futures, importlib.util, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = "reference/maxima-syntax-test-suite"
CENSUS = os.path.join(ROOT, "probes", "verify-stages", "09-declined-census.out")
SETS = {"V1": "[m=0.37, n=1.7, q=0.6, F=1.9]",
        "V2": "[m=1.3, n=0.45, q=1.4, F=2.3]"}
LOAD = 'load("test/mr_verify.mac")$\n'


def load_driver(section, key):
    real = sys.argv[:]
    sys.argv = ["corpus_driver.py", section + "/", "999999", "30", SUITE]
    try:
        spec = importlib.util.spec_from_file_location(
            f"drv_{key}_{section[0]}", os.path.join(ROOT, "test", "corpus_driver.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.argv = real
    orig = mod.build_text

    def patched(*a, **k):
        t = orig(*a, **k)
        assert t.count(LOAD) == 1
        return t.replace(LOAD, LOAD + f"mr_numeric_subs : append(mr_numeric_subs, {SETS[key]})$\n")
    mod.build_text = patched
    return mod


def main():
    items = []
    for line in open(CENSUS, encoding="utf-8"):
        m = re.match(r"^(none/numeric-declined\S*)\s+free (\S+)\s+(.*) e(\d+)$", line.rstrip("\n"))
        if m:
            items.append((m.group(3), int(m.group(4)), m.group(2)))
    print(f"entries: {len(items)}")
    for key in SETS:
        drivers = {}
        for rel, _e, _f in items:
            sec = rel.split("/")[0]
            if sec not in drivers:
                drivers[sec] = load_driver(sec, key)

        def run(item):
            rel, n, free = item
            d = drivers[rel.split("/")[0]]
            entries, line_nos = d.extract_entries(os.path.join(ROOT, SUITE, rel))
            cls, _l, _c, proof = d.run_entry_full(rel, n - 1, entries[n - 1], line_nos[n - 1])
            return rel, n, free, cls, proof

        with concurrent.futures.ThreadPoolExecutor(12) as ex:
            res = list(ex.map(run, items))
        tab = collections.Counter((cls, (proof or "-").split("/timeout")[0]) for *_x, cls, proof in res)
        print(f"\n==== {key} {SETS[key]}")
        for (c, p), v in tab.most_common():
            print(f"  {v:>5} {c:11s} {p}")
        for rel, n, free, cls, proof in res:
            print(f"  {key} {cls:11s} {proof or '-':50s} free {free:8s} {rel} e{n}")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
