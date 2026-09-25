#!/usr/bin/env python3
"""Class-7 rule files present in the pinned Rubi tree but NOT loaded by
Rubi.m (docs/class-porting.md Step 1(a): the census counts only
LoadRules'd files, and the record must say which files it leaves out and
why).

  python3 probes/translation/11-class7-excluded-files.py ["7 "]

For every `.m` file under the section's IntegrationRules directory that no
Rubi.m LoadRules line names, print its `^Int[` line count and its closest
LOADED sibling in the same subdirectory: the loaded file with the same
title after the `7.x.y ` number prefix, compared (a) byte for byte and
(b) with the one-line `(* 7.x.y title *)` header comment dropped. An
unmatched title is compared against every loaded file of the subdirectory
by rule set: the excluded file's `Int[` runs are counted as a union of
which loaded files carry them, byte-identical run by run.

Static, no Maxima.
"""

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_c = importlib.util.spec_from_file_location(
    "census01", ROOT / "probes" / "translation" / "01-class1-syntax-census.py")
census = importlib.util.module_from_spec(_c)
_c.loader.exec_module(census)

RUBI = ROOT / "reference" / "rubi"
RULE_DIR = RUBI / "Rubi" / "IntegrationRules"


def title(name):
    return re.sub(r"^[0-9.]+ ", "", name)


def runs(path):
    return ["\n".join(r) for r in
            census.rule_runs(census.strip_comments(path.read_text()))]


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "7 "
    rubi_m = (RUBI / "Rubi" / "Rubi.m").read_text()
    loaded = {tuple(parts) for parts, _g in
              census.parse_load_rules(census.strip_comments(rubi_m))
              if parts[0].startswith(prefix)}
    sec = [d for d in RULE_DIR.iterdir() if d.name.startswith(prefix)]
    assert len(sec) == 1, sec
    every = sorted(sec[0].rglob("*.m"))
    print(f"=== {sec[0].name}: .m files in the tree {len(every)}, "
          f"loaded {len(loaded)}, NOT loaded "
          f"{len(every) - len(loaded)} ===")
    for f in every:
        rel = f.relative_to(RULE_DIR).with_suffix("")
        if tuple(rel.parts) in loaded:
            continue
        n_int = sum(1 for ln in f.read_text().splitlines()
                    if ln.startswith("Int["))
        print(f"\nNOT LOADED  {rel.parts[-2]}/{f.name}   ^Int[ lines: {n_int}")
        sibs = [g for g in sorted(f.parent.glob("*.m"))
                if tuple(g.relative_to(RULE_DIR).with_suffix("").parts)
                in loaded]
        same = [g for g in sibs if title(g.stem) == title(f.stem)]
        if same:
            g = same[0]
            a, b = f.read_text(), g.read_text()
            a1 = re.sub(r"\(\* [0-9.]+ [^*]*\*\)", "", a)
            b1 = re.sub(r"\(\* [0-9.]+ [^*]*\*\)", "", b)
            print(f"  same title as LOADED {g.name}")
            print(f"    byte-identical: {a == b};  identical without the "
                  f"`(* <number> <title> *)` header comments: {a1 == b1}")
            ra, rb = runs(f), runs(g)
            print(f"    rule runs: excluded {len(ra)}, loaded {len(rb)}, "
                  f"excluded runs found verbatim in the loaded file: "
                  f"{sum(1 for r in ra if r in set(rb))}")
        else:
            ra = runs(f)
            cover = {}
            for g in sibs:
                rb = set(runs(g))
                k = sum(1 for r in ra if r in rb)
                if k:
                    cover[g.name] = k
            print(f"  no loaded file with the same title; its {len(ra)} "
                  f"rule runs found verbatim in loaded files:")
            for name, k in cover.items():
                print(f"    {k:4d}  {name}")
            print(f"    {len(ra) - sum(1 for r in ra if any(r in set(runs(g)) for g in sibs)):4d}  in no loaded file")


if __name__ == "__main__":
    main()
