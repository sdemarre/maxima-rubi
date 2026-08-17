#!/usr/bin/env python3
"""Probe: utility-function inventory of Rubi 4 (T1, feeds T4).

Run from the repo root:
  python3 probes/probe-rubi-anatomy/02-utility-inventory.py [reference/rubi]

What it measures (claims recorded in docs/rubi-architecture.md):
  * The set of support functions DEFINED by the loaded Rubi modules:
      - IntegrationUtilityFunctions.m   (Name::usage lines)
      - Rubi.m, ShowStepRoutines.m, ShowStepFormatting.m (usage lines)
  * Every Uppercase-identifier call site in the loaded rule files,
    counted for all loaded files and for the mandatory set
    (class 1 + class 9) separately. A call is an occurrence of
    'Name[' where Name starts uppercase and is not preceded by an
    identifier character (so 'F_[' pattern heads do not count).
  * For each called name: is it a Rubi-defined support function, a
    Rubi driver function, or something else (Mathematica built-in or
    inert head) -- the 'else' column is the manual-classification
    input for the porting-cost estimate.
  * Uses of $TimeLimit inside the utility file (the routines Rubi
    itself considers expensive).
"""

import importlib.util
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

USAGE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*)::usage", re.M)
CALL_RE = re.compile(r"(?<![A-Za-z0-9])([A-Z][A-Za-z0-9]*)\[")


def strip_comments(src):
    out = []
    i, n = 0, len(src)
    while i < n:
        if src.startswith("(*", i):
            j = src.find("*)", i + 2)
            j = n if j == -1 else j + 2
            out.append("\n" * src.count("\n", i, j))
            i = j
        else:
            out.append(src[i])
            i += 1
    return "".join(out)


def load_inventory_script():
    path = Path(__file__).parent / "01-inventory.py"
    spec = importlib.util.spec_from_file_location("inv", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "reference/rubi")
    rubi_dir = root / "Rubi"
    rule_dir = rubi_dir / "IntegrationRules"
    inv = load_inventory_script()

    rubi_m = (rubi_dir / "Rubi.m").read_text()
    loaded_files = []
    for parts, gated in inv.parse_load_rules(rubi_m):
        if parts[0].startswith("$"):
            continue
        p = rule_dir.joinpath(*parts)
        if not p.name.endswith(".m"):
            p = p.with_name(p.name + ".m")
        if p.exists():
            loaded_files.append((p.relative_to(rule_dir).as_posix(), p, gated))

    defined = {}
    for mod in ("IntegrationUtilityFunctions.m", "Rubi.m",
                "ShowStepRoutines.m", "ShowStepFormatting.m"):
        path = rubi_dir / mod
        if not path.exists():
            continue
        for n_ in USAGE_RE.findall(path.read_text()):
            defined.setdefault(n_, mod)

    calls_all = Counter()
    calls_core = Counter()  # mandatory set: class 1 + class 9
    for rel, p, gated in loaded_files:
        src = strip_comments(p.read_text())
        for n_ in CALL_RE.findall(src):
            calls_all[n_] += 1
            if not gated:
                calls_core[n_] += 1

    print("=== Rubi-defined support functions (Name::usage across loaded modules) ===")
    by_mod = defaultdict(list)
    for n_, mod in defined.items():
        by_mod[mod].append(n_)
    for mod in ("IntegrationUtilityFunctions.m", "Rubi.m",
                "ShowStepRoutines.m", "ShowStepFormatting.m"):
        names = sorted(by_mod.get(mod, []))
        print("  {} ({}):".format(mod, len(names)))
        print("    " + ", ".join(names))
    print()
    print("=== called names in rule files, ranked (core = mandatory classes 1+9) ===")
    print("  {:>6s} {:>6s}  {:24s} defined-in".format("all", "core", "name"))
    for n_, c in calls_all.most_common():
        d = defined.get(n_, "-")
        print("  {:6d} {:6d}  {:24s} {}".format(c, calls_core.get(n_, 0), n_, d))
    print()
    print("=== $TimeLimit uses in IntegrationUtilityFunctions.m ===")
    util_src = (rubi_dir / "IntegrationUtilityFunctions.m").read_text()
    for i, line in enumerate(util_src.split("\n"), 1):
        if "$TimeLimit" in line and i > 1:
            print("  {:5d}: {}".format(i, line.strip()))


if __name__ == "__main__":
    main()
