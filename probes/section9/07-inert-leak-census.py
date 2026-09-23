#!/usr/bin/env python3
"""probes/section9/07-inert-leak-census.py -- ticket 15: WHICH records fire
inside the inert-trig domain on the entries that leak?

WHY this probe exists. Probe 02 shows ONE witness (6.3.2 e13) where 9_3 r41
fires on a deactivated integrand and emits its prefactor outside the
recursive mr_int. Before choosing a fix shape we need to know whether r41 is
the whole story or one of several records, and whether any class-1/2/3/6
record also fires on an inert integrand.

METHOD. The leak set is the 286 `inert-leak` lines of the committed paired
rerun log (test/section9_paired_class6.new/queue.log). Each entry is re-run
on the core the driver resolves (MR_RULES_CORE_PATH, else test/mr_rules.core)
with rubi_verbose on, under the driver's own cap mechanism, and every
`rubi: rule K rN fired on <integrand>` line whose INTEGRAND carries one of
the six inert heads is tallied by record. Class-4 records (key 4_*) are the
bridge and are expected there; everything else is a record running inside
the inert domain.

  python3 probes/section9/07-inert-leak-census.py [workers]   (default 12)
"""

import os
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "test"))
_argv, sys.argv = sys.argv, sys.argv[:1]
import corpus_driver as cd  # noqa: E402
sys.argv = _argv

LOG = os.path.join(ROOT, "test", "section9_paired_class6.new", "queue.log")
LEAK_RX = re.compile(r"^inert-leak (.*) e(\d+) L(\d+): ")
FIRE_RX = re.compile(r"^rubi: rule (\S+) r(\d+) fired on (.*?) with \[")
HEADS = cd.INERT_HEADS

PRE = """display2d : false$
linel : 1000000$
mr_flat_wide : false$
mr_cond_retry : true$
mr_model_flags : true$
mr_nested_fallback : false$
mr_giveup_last : true$
mr_max_depth : 16$
"""


def leak_entries():
    out = []
    with open(LOG, encoding="utf-8") as fh:
        for line in fh:
            m = LEAK_RX.match(line)
            if m:
                out.append((m.group(1), int(m.group(2)), int(m.group(3))))
    return out


def run_one(key):
    rel, e, _ = key
    entries, _lines = cd.extract_entries(os.path.join(cd.SUITE_DIR, rel))
    els = cd.split_elements(entries[e - 1][1:-1])
    f_text = cd.normalize_heads(els[0])
    text = (PRE + f"mr_f : {f_text}$\nrubi_verbose : true$\n"
            f"mr_r : errcatch(rubi(mr_f, {els[1]}))$\n"
            "rubi_verbose : false$\nprint(\"CENSUS_DONE\")$\n")
    out, hit = cd.maxima_run(text, cd.TIMEOUT)
    fires = []
    for line in out.splitlines():
        m = FIRE_RX.match(line)
        if m and any(h in m.group(3) for h in HEADS):
            fires.append(f"{m.group(1)} r{m.group(2)}")
    return key, fires, hit, "CENSUS_DONE" in out


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    keys = leak_entries()
    print(f"# section-9 probe 07: records firing on an inert integrand, "
          f"over the {len(keys)} leak entries of {os.path.relpath(LOG, ROOT)}")
    print(f"# core: {cd.RULES_CORE}")
    with open(cd.RULES_CORE_STAMP, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith(("fingerprint ", "rules ")):
                print(f"# core stamp: {line.rstrip()}")
    print(f"# {cd.TIMEOUT} s {cd.CAP_KIND} cap, {workers} workers")
    with ThreadPoolExecutor(workers) as ex:
        results = list(ex.map(run_one, keys))
    per_rule = Counter()        # entries in which the record fired inert
    non4_entries = defaultdict(list)
    no_non4 = []
    unfinished = 0
    for key, fires, hit, done in results:
        if hit or not done:
            unfinished += 1
        for r in set(fires):
            per_rule[r] += 1
        non4 = sorted({r for r in fires if not r.startswith("4_")})
        if non4:
            non4_entries[tuple(non4)].append(key)
        else:
            no_non4.append((key, hit, done))
    print(f"entries run: {len(results)}; capped or unfinished: {unfinished}")
    print("records firing on an inert integrand (entries in which each fired):")
    for r, n in per_rule.most_common():
        print(f"  {n:4d}  {r}{'' if r.startswith('4_') else '   <- non-class-4'}")
    print("non-class-4 record sets (entries):")
    for rs, ks in sorted(non4_entries.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(ks):4d}  {', '.join(rs)}")
    print(f"entries with NO non-class-4 record firing inert: {len(no_non4)}")
    for (rel, e, l), hit, done in no_non4:
        print(f"    {rel} e{e} L{l}  cap={hit} finished={done}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
