#!/usr/bin/env python3
"""Probe: generation-vs-inventory census cross-check (T6 Step 4, static).

Run from the repo root:
  sh probes/census/01-generation-vs-inventory.run

What it measures: that the generator's per-file rule counts (the rule-run
parser applied to the Rubi source, exactly as the generator emits the
files) equal the T1 inventory's per-file counts for all 67 class-1 files,
and that the total is 2710. Static — no Maxima — because the installed
build cannot hold the 2710 patterns in one process to check them there
(measured 2026-08-20, probes/load_wall/probe-load-wall.out); the in-suite
test_census checks the loadable subset instead. Exits nonzero on any
mismatch (a broken generation must fail the probe, not just the diff).
"""

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INV_OUT = ROOT / "probes" / "probe-rubi-anatomy" / "01-inventory.out"


def _load(name, rel):
    p = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, p)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def inventory_counts(path):
    """Per-file class-1 counts from 01-inventory.out: key -> rule count.
    The per-file section rows:
      <count>  cond=<n> redisp=<n> subst=<n>   <rel path ending in .m>
    """
    counts = {}
    sec = False
    for ln in path.read_text().splitlines():
        if ln.startswith("=== per-file rule counts, class 1"):
            sec = True
            continue
        if ln.startswith("===") and sec:
            sec = False
            continue
        if not sec:
            continue
        m = re.match(r"\s+(\d+)\s+cond=\d+\s+redisp=\d+\s+subst=\d+\s+(.+)$",
                     ln)
        if not m:
            continue
        base = m.group(2).strip().split("/")[-1]
        key = base.split(" ")[0].replace(".", "_")
        counts[key] = int(m.group(1))
    return counts


def main():
    gen = _load("gen", "generator/generate_class1.py")
    inv = _load("inv01", "probes/probe-rubi-anatomy/01-inventory.py")
    cen = _load("cen01", "probes/translation/01-class1-syntax-census.py")

    files = gen.load_class1_files(gen.RUBI)
    gen_counts = {}
    for rel_m in files:
        key = gen.key_of(rel_m)
        text = inv.strip_comments((gen.RUBI / rel_m).read_text())
        gen_counts[key] = len(cen.rule_runs(text))

    inv_counts = inventory_counts(INV_OUT)

    print("=== generation-vs-inventory census cross-check ===")
    print(f"files: generator {len(gen_counts)}, inventory {len(inv_counts)}")
    bad = 0
    only_g = sorted(set(gen_counts) - set(inv_counts))
    only_i = sorted(set(inv_counts) - set(gen_counts))
    if only_g:
        print("only in generator:", only_g)
        bad += 1
    if only_i:
        print("only in inventory:", only_i)
        bad += 1
    for key in sorted(set(gen_counts) & set(inv_counts)):
        if gen_counts[key] != inv_counts[key]:
            print(f"count mismatch {key}: generator {gen_counts[key]} "
                  f"!= inventory {inv_counts[key]}")
            bad += 1
    total_g, total_i = sum(gen_counts.values()), sum(inv_counts.values())
    print(f"total: generator {total_g}, inventory {total_i}, expected 2710")
    if total_g != 2710 or total_i != 2710:
        bad += 1
    print("VERDICT:", "MISMATCH" if bad else
          f"OK ({len(gen_counts)} files, {total_g} rules, all per-file "
          "counts equal)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
