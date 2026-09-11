#!/usr/bin/env python3
"""Entry-level A/B of two merged corpus records (the regression-gate
diff: plan Task-5 Steps 3-4, `docs/class-porting.md` Step 9).

Both records are merged `test/corpus_classN.out` files (or any
`.out` in the T3 result-line format
    <class>  t=<s>s <relpath> e<entry> L<line>
— shard files, timeout re-check records). Entries are keyed on
(relpath, entry); the L<line> field is ignored.

Report, in order:
  - the key-set check (entries missing from / extra in NEW) — a
    mismatch exits 2: the two records do not cover the same corpus;
  - the PASS/FAIL 2x2 table;
  - the class-level transition counts (every changed class pair);
  - per-file PASS->FAIL / FAIL->PASS counts;
  - every PASS->FAIL line (the gate: each must be attributed), and
    with --all every FAIL->PASS line too.

PASS classes are read from test/corpus_driver.py's PASS_CLASSES
literal (ast, not import — importing the driver runs its rules-core
check), so the A/B cannot drift from the driver's Results: line.

Usage:  python3 test/ab_records.py BASE NEW [--all]
"""

import ast
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L(\d+)$")


def driver_pass_classes(path=os.path.join(HERE, "corpus_driver.py")):
    """The driver's top-level PASS_CLASSES set literal."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in tree.body:
        if (isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "PASS_CLASSES"
                        for t in node.targets)
                and isinstance(node.value, ast.Set)):
            return {e.value for e in node.value.elts
                    if isinstance(e, ast.Constant)}
    raise ValueError(f"{path}: no top-level PASS_CLASSES set literal")


def load_record(path):
    """{(relpath, entry): (class, seconds)}; a duplicate key is an error."""
    rec = {}
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            m = RESULT.match(line.rstrip("\n"))
            if not m:
                continue
            key = (m.group(3), int(m.group(4)))
            if key in rec:
                raise ValueError(f"{path}:{lineno}: duplicate entry "
                                 f"{key[0]} e{key[1]}")
            rec[key] = (m.group(1), float(m.group(2)))
    return rec


def compare(base, new, pass_classes):
    """Transition summary of BASE -> NEW over their shared keys."""
    shared = sorted(base.keys() & new.keys())
    table = Counter({"PASS->PASS": 0, "PASS->FAIL": 0,
                     "FAIL->PASS": 0, "FAIL->FAIL": 0})
    classes = Counter()
    per_file = {}
    pass_fail, fail_pass = [], []
    for key in shared:
        a, b = base[key], new[key]
        pa = "PASS" if a[0] in pass_classes else "FAIL"
        pb = "PASS" if b[0] in pass_classes else "FAIL"
        table[f"{pa}->{pb}"] += 1
        if a[0] != b[0]:
            classes[(a[0], b[0])] += 1
        if pa != pb:
            row = per_file.setdefault(key[0], Counter())
            row[f"{pa}->{pb}"] += 1
            (pass_fail if pa == "PASS" else fail_pass).append((key, a, b))
    return {"table": dict(table), "classes": classes, "per_file": per_file,
            "pass_fail": pass_fail, "fail_pass": fail_pass,
            "missing": sorted(base.keys() - new.keys()),
            "extra": sorted(new.keys() - base.keys())}


def _lines(rows):
    for (rel, n), a, b in rows:
        yield (f"  {a[0]:<13} -> {b[0]:<13} t={a[1]:.1f}s -> t={b[1]:.1f}s "
               f"{rel} e{n}")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 64
    base_path, new_path = args
    base, new = load_record(base_path), load_record(new_path)
    r = compare(base, new, driver_pass_classes())

    print(f"base: {base_path} ({len(base)} entries)")
    print(f"new:  {new_path} ({len(new)} entries)")
    print(f"key set: {len(r['missing'])} missing from new, "
          f"{len(r['extra'])} extra in new")
    for label, keys in (("missing", r["missing"]), ("extra", r["extra"])):
        for rel, n in keys:
            print(f"  {label}: {rel} e{n}")

    print("\n=== PASS/FAIL table ===")
    for label in ("PASS->PASS", "PASS->FAIL", "FAIL->PASS", "FAIL->FAIL"):
        print(f"{label:<12}{r['table'][label]:>5}")

    print("\n=== class transitions (changed only) ===")
    for (a, b), n in sorted(r["classes"].items(), key=lambda kv: -kv[1]):
        print(f"{n:>5}  {a} -> {b}")

    print("\n=== per file (PASS->FAIL / FAIL->PASS) ===")
    for rel in sorted(r["per_file"]):
        row = r["per_file"][rel]
        print(f"{row['PASS->FAIL']:>5} {row['FAIL->PASS']:>5}  {rel}")

    print(f"\n=== PASS->FAIL ({len(r['pass_fail'])}) ===")
    for line in _lines(r["pass_fail"]):
        print(line)
    if "--all" in argv:
        print(f"\n=== FAIL->PASS ({len(r['fail_pass'])}) ===")
        for line in _lines(r["fail_pass"]):
            print(line)

    return 2 if r["missing"] or r["extra"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
