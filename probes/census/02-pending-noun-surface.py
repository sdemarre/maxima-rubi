#!/usr/bin/env python3
"""Probe: pending-noun surface of the committed class-1 rules (static).

Run from the repo root:
  sh probes/census/02-pending-noun-surface.run

What it measures: of the 2710 committed rules, which call a %mr_*/mr_*
name that is not yet defined in maxima_rubi_utils.mac / maxima_rubi.mac
(a "pending noun"), and WHERE — a pending name in a rule's COND means the
rule declines (the guard can never evaluate to true); a pending name
only in the REPL means the rule fires and returns a noun-laden answer.
Two scopes are reported:
  C-tier  - pending names that are ports of census C_TIER predicates
            (probes/translation/01-class1-syntax-census.py C_TIER), the
            Task-7-predicate surface;
  full    - every pending name (C-tier + B_TIER operators + shims), the
            whole Task-7 surface the divergence loop (Task 9) must clear.
The split is what the Task-6 report's C-tier handoff wording must state
(review finding 2: "decline" was asserted for rules that actually fire
with noun-laden answers). Static — no Maxima. Exits nonzero only on
structural failure (missing file, unparseable rule, total != 2710);
the surface itself is a measurement, not a gate.
"""

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = ROOT / "rules" / "class1"


def _load(name, rel):
    p = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, p)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def defined_names():
    lib = (ROOT / "maxima_rubi_utils.mac").read_text() + "\n" + \
          (ROOT / "maxima_rubi.mac").read_text()
    return set(re.findall(r"^\s*(%?mr_\w+)\s*(?:[(:])", lib, re.M))


NAME = re.compile(r"(?<![A-Za-z0-9_])(%?mr_\w+)(?=\s*[(\[])")
DEFMATCH = re.compile(r"^defmatch\(_mr_pat_(\w+)_r(\d+),")


def parse_rules(path):
    """[(key, n, cond_text, repl_text)] per rule, in file order."""
    lines = path.read_text().splitlines()
    starts = [i for i, l in enumerate(lines) if DEFMATCH.match(l)]
    out = []
    for j, s in enumerate(starts):
        e = starts[j + 1] if j + 1 < len(starts) else len(lines)
        chunk = lines[s:e]
        key, n = DEFMATCH.match(chunk[0]).groups()

        def section(start, stop):
            out, on = [], False
            for l in chunk:
                if re.match(start, l):
                    on = True
                    continue
                if on and re.match(stop, l):
                    break
                if on:
                    out.append(l)
            return "\n".join(out)

        out.append((key, n,
                    section(rf"^_mr_cond_{key}_r{n}",
                            rf"^_mr_repl_{key}_r{n}"),
                    section(rf"^_mr_repl_{key}_r{n}",
                            rf"^_mr_rule_{key}_r{n}")))
    return out


def classify(rules, pset):
    stats = {"cond": 0, "repl": 0, "both": 0, "clean": 0}
    per = {}
    for key, n, cond, repl in rules:
        cn = {x for x in NAME.findall(cond) if x in pset}
        rn = {x for x in NAME.findall(repl) if x in pset}
        k = "both" if cn and rn else "cond" if cn else \
            "repl" if rn else "clean"
        stats[k] += 1
        for x in cn | rn:
            per[x] = per.get(x, 0) + 1
    return stats, per


def main():
    cen = _load("cen", "probes/translation/01-class1-syntax-census.py")
    tab = _load("tab", "generator/translation_table.py")

    files = sorted(RULES_DIR.glob("*.mac"))
    if len(files) != 67:
        print(f"structural: expected 67 rule files, found {len(files)}")
        return 1
    rules = []
    for p in files:
        rules.extend(parse_rules(p))
    total = len(rules)
    if total != 2710:
        print(f"structural: expected 2710 rules, parsed {total}")
        return 1

    defined = defined_names()
    refs = set()
    for _, _, cond, repl in rules:
        refs.update(NAME.findall(cond))
        refs.update(NAME.findall(repl))
    pending = {x for x in refs - defined
               if not x.startswith("mr_witness_")}
    ctier = {tab.RENAME[t] for t in cen.C_TIER if t in tab.RENAME} & pending

    print("=== pending-noun surface, committed rules/class1 (static) ===")
    print(f"rules: {total} | pending names: full {len(pending)}, "
          f"C-tier {len(ctier)}")
    for label, pset in (("C-tier", ctier), ("full", pending)):
        s, per = classify(rules, pset)
        decline, fire = s["cond"] + s["both"], s["repl"]
        print(f"[{label}] decline(cond, incl. both) {decline} | "
              f"fire-noun(repl-only) {s['repl']} | both {s['both']} | "
              f"clean {s['clean']}  "
              f"(cond-only {s['cond']}; columns overlap on 'both')")
        print(f"[{label}] top names: "
              + ", ".join(f"{n} {k}" for n, k in sorted(
                  per.items(), key=lambda kv: -kv[1])[:10]))
    print("VERDICT: OK (measurement; counts above are the handoff "
          "surface)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
