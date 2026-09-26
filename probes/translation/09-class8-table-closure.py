#!/usr/bin/env python3
"""Class-8 token closure against the generator's translation table
(docs/class-porting.md Step 1(a), the "UNLISTIED" half).

The syntax census (01-class1-syntax-census.py) tiers tokens against its
OWN static lists; what generation actually needs is the closure against
generator/translation_table.py (RENAME + RESTRUCTURE). This probe prints,
for the class-8 port's rule set, every call token and whether the table
translates it:

  * the "8 " files Rubi.m loads (Rubi.m comment-stripped: L352's
    commented-out "8.10 Bessel functions" is NOT loaded);
  * plus "9 Miscellaneous/9.1 Derivative integration rules" (Rubi.m L354),
    which belongs to this port (section-9 spec 2026-09-22 §0.3.3, ticket
    .scratch/class-ports/issues/01).

A token that is a pattern variable of the rule it occurs in (F_ in the
LHS, used as F[...] on the RHS) is a HEAD VARIABLE, not a table row.
Everything else not in the table is UNLISTED and is adjudicated on the
ticket. Also printed: per-file rule counts and the number of
If[TrueQ[$LoadShowSteps], ...] lines (the EXPECTED_TOTAL adjustment
class 3 and 9 needed).

  sh probes/translation/09-class8-syntax-census.run
"""

import importlib.util
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_c = importlib.util.spec_from_file_location(
    "census01", ROOT / "probes" / "translation" / "01-class1-syntax-census.py")
census = importlib.util.module_from_spec(_c)
_c.loader.exec_module(census)
sys.path.insert(0, str(ROOT / "generator"))
from translation_table import RENAME, RESTRUCTURE  # noqa: E402

RUBI = ROOT / "reference" / "rubi"
RULE_DIR = RUBI / "Rubi" / "IntegrationRules"
EXTRA = [("9 Miscellaneous", "9.1 Derivative integration rules")]


def loaded_files():
    rubi_m = (RUBI / "Rubi" / "Rubi.m").read_text()
    out = []
    for parts, _g in census.parse_load_rules(census.strip_comments(rubi_m)):
        if parts[0].startswith("8 ") or tuple(parts) in EXTRA:
            out.append(parts)
    return out


def main():
    files = loaded_files()
    per_file = []
    tok_rules = Counter()
    tok_uses = Counter()
    tok_first = {}
    headvars = Counter()
    showsteps = 0
    for parts in files:
        p = RULE_DIR.joinpath(*parts[:-1]) / (parts[-1] + ".m")
        src = p.read_text()
        showsteps += sum(1 for l in src.splitlines() if "LoadShowSteps" in l)
        n = 0
        for run in census.rule_runs(census.strip_comments(src)):
            text = "\n".join(run)
            if ":=" not in text:
                continue
            n += 1
            lhs, rhs, cond = census.split_rule(text)
            pvars = set(re.findall(r"\b([A-Za-z][A-Za-z0-9]*)_", lhs))
            seen = set()
            for part in (lhs, cond, rhs):
                for t in census.tokens(part):
                    if t in pvars:
                        headvars[t] += 1
                        continue
                    tok_uses[t] += 1
                    if t not in seen:
                        tok_rules[t] += 1
                        seen.add(t)
                    tok_first.setdefault(t, f"{parts[-1]} r{n}")
        per_file.append((parts[-1], n))
    print("=== class-8 port: token closure against translation_table.py ===")
    print(f"files: {len(files)}   rules: {sum(n for _, n in per_file)}   "
          f"LoadShowSteps lines: {showsteps}")
    for name, n in per_file:
        print(f"  {n:4d}  {name}")
    print()
    print("== head variables (pattern variables in head position) ==")
    for t, c in sorted(headvars.items(), key=lambda kv: -kv[1]):
        print(f"  {t:8s} uses={c}")
    listed = {t for t in tok_uses if t in RENAME or t in RESTRUCTURE}
    unlisted = [t for t in tok_uses if t not in listed]
    print()
    print(f"== tokens the table translates: {len(listed)} ==")
    for t in sorted(listed, key=lambda t: (-tok_rules[t], t)):
        row = RENAME.get(t, RESTRUCTURE.get(t))
        print(f"  rules={tok_rules[t]:4d} uses={tok_uses[t]:4d}  {t} -> {row}")
    print()
    print(f"== UNLISTED tokens (adjudicate on the ticket): {len(unlisted)} ==")
    for t in sorted(unlisted, key=lambda t: (-tok_rules[t], t)):
        print(f"  rules={tok_rules[t]:4d} uses={tok_uses[t]:4d}  {t:24s} first at {tok_first[t]}")


if __name__ == "__main__":
    main()
