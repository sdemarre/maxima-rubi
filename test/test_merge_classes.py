#!/usr/bin/env python3
"""Regression guard: the shard-merge script must classify every class the
corpus driver can emit.

Root cause guarded (2026-08-26): merge_class1_shards.py carries its own
KNOWN_CLASSES / PASS_CLASSES sets, copied from the driver at write time.
The driver gained two FAIL classes since — `deferred` (ddc88ef, top-level
no-answer on an answer-expected entry) and `contains-noun` (2a0ff92, a
CannotIntegrate marker in the answer) — without the merge following, so a
COMPLETE merged run would die on the `assert k in KNOWN_CLASSES` in the
summary loop (after the completeness check, i.e. at the acceptance gate).

Two construction checks (no Maxima, source-level):
  1. the merge's KNOWN_CLASSES is a superset of the driver's — every
     class the driver emits in a result line is classifiable.
  2. the merge's PASS_CLASSES is EXACTLY the driver's — the merge's
     `Results:` line must agree with the driver's per-line PASS:/FAIL:.

The sets are read with ast (not import): merge_class1_shards.py executes
its whole merge at module level (sys.exit on an incomplete corpus), so it
cannot be imported as a test dependency.

Re-runnable:  python3 test/test_merge_classes.py
Exits nonzero if any check fails.
"""

import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _sets(path, names):
    """The literal set(s) assigned to `names` at module top level."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id in names:
                vals = node.value
                if not isinstance(vals, ast.Set):
                    raise AssertionError(f"{path}: {t.id} is not a set literal")
                out[t.id] = {
                    e.value for e in vals.elts if isinstance(e, ast.Constant)
                }
    missing = names - set(out)
    if missing:
        raise AssertionError(f"{path}: no top-level literal for {sorted(missing)}")
    return out


def main():
    failures = []
    drv = _sets(os.path.join(HERE, "corpus_class1_driver.py"),
                {"KNOWN_CLASSES", "PASS_CLASSES"})
    mrg = _sets(os.path.join(HERE, "merge_class1_shards.py"),
                {"KNOWN_CLASSES", "PASS_CLASSES"})

    # 1. superset: every driver-emittable class is merge-classifiable.
    unclassifiable = drv["KNOWN_CLASSES"] - mrg["KNOWN_CLASSES"]
    if unclassifiable:
        failures.append(
            "merge KNOWN_CLASSES lacks driver classes: "
            + ", ".join(sorted(unclassifiable))
            + " (a complete merge would crash on the summary assert)")
    else:
        print("PASS [known] merge KNOWN_CLASSES covers every driver class "
              f"({sorted(drv['KNOWN_CLASSES'])})")

    # 2. identical pass mapping: the merge's Results line must agree with
    #    the driver's per-line PASS:/FAIL:.
    if mrg["PASS_CLASSES"] != drv["PASS_CLASSES"]:
        failures.append(
            "merge PASS_CLASSES "
            + str(sorted(mrg["PASS_CLASSES"]))
            + " != driver PASS_CLASSES "
            + str(sorted(drv["PASS_CLASSES"])))
    else:
        print("PASS [pass] merge PASS_CLASSES == driver PASS_CLASSES "
              f"({sorted(drv['PASS_CLASSES'])})")

    for msg in failures:
        print(f"FAIL {msg}")
    n = 2 - len(failures)
    print(f"\nResults: {n} passed, {2 - n} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
