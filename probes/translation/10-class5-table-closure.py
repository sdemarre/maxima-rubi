#!/usr/bin/env python3
"""Class-5 token closure against the generator's translation table, and its
TRANSITIVE closure through IntegrationUtilityFunctions.m
(docs/class-porting.md Step 1(a), the "UNLISTED" half).

  python3 probes/translation/10-class5-table-closure.py ["5 "]

Part 1 (the 09 probe's shape, section as argument): every call token of the
section's Rubi.m-loaded rule files, split into the tokens
generator/translation_table.py translates (RENAME + RESTRUCTURE) and the
UNLISTED ones, which the ticket adjudicates. A token that is a pattern
variable of its own rule (F_ in the LHS, F[...] on the RHS) is a HEAD
VARIABLE, not a table row. Also printed: per-file rule counts and the
If[TrueQ[$LoadShowSteps], ...] line count. Rules are counted AFTER the
generator's unwrap_showsteps_lines, i.e. as the generator numbers them.

Part 2 (the CENSUS TRAP of ticket 05): a rule-side scan misses utilities the
rules reach only THROUGH another utility (ReduceInertTrig has 0 rule-side
uses and 39 clauses). Starting from every rule token that
IntegrationUtilityFunctions.m defines, walk the definitions' own call tokens
to a fixed point. For every utility reached, print how it was reached (rule
token or the first utility that calls it) and whether the port has it:

  table   the token has a translation_table row (the generator emits it);
          Part 1 also names the EMITTER-dispatched tokens: no row, but
          generate_rules.py handles the token by name (ReplaceAll, IGeQ,
          PolyQ, ...);
  ported  a %mr_<name> function is defined in the package sources (house
          naming: lower-cased first letter; underscores ignored) — an
          internal helper the table need not list;
  ABSENT  neither. An ABSENT utility under a `table`/`ported` parent is a
          candidate semantic gap in that parent's port (the parent may
          still cover the case another way — the ticket reads each one).

Static, no Maxima.
"""

import importlib.util
import re
import sys
from collections import Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_c = importlib.util.spec_from_file_location(
    "census01", ROOT / "probes" / "translation" / "01-class1-syntax-census.py")
census = importlib.util.module_from_spec(_c)
_c.loader.exec_module(census)
sys.path.insert(0, str(ROOT / "generator"))
from translation_table import RENAME, RESTRUCTURE  # noqa: E402
import generate_rules  # noqa: E402  (unwrap_showsteps_lines only)

RUBI = ROOT / "reference" / "rubi"
RULE_DIR = RUBI / "Rubi" / "IntegrationRules"
UTILS = RUBI / "Rubi" / "IntegrationUtilityFunctions.m"
PACKAGE_SOURCES = ["maxima_rubi_utils.mac", "maxima_rubi.mac",
                   "maxima_rubi_dispatch.lisp", "maxima_rubi_tree.lisp",
                   "maxima_rubi_match.lisp"]


def loaded_files(prefix):
    rubi_m = (RUBI / "Rubi" / "Rubi.m").read_text()
    return [parts for parts, _g in
            census.parse_load_rules(census.strip_comments(rubi_m))
            if parts[0].startswith(prefix)]


def utility_definitions():
    """name -> concatenated text of its top-level definitions (usage
    strings and comments dropped). A definition starts at column 0 with
    `Name[` and runs until the next column-0 line."""
    src = census.strip_comments(UTILS.read_text())
    defs = {}
    cur = None
    for line in src.splitlines():
        if line and not line[0].isspace():
            m = re.match(r"([A-Z][A-Za-z0-9]*)\[", line)
            cur = m.group(1) if (m and "::usage" not in line) else None
            if cur is not None:
                defs.setdefault(cur, [])
        if cur is not None:
            defs[cur].append(line)
    return {k: "\n".join(v) for k, v in defs.items()}


def package_function_names():
    names = set()
    for f in PACKAGE_SOURCES:
        p = ROOT / f
        if not p.exists():
            continue
        txt = p.read_text()
        for m in re.finditer(r"%mr_([A-Za-z0-9_]+)\s*\(", txt):
            names.add(m.group(1).replace("_", "").lower())
        for m in re.finditer(r"\$%MR_([A-Za-z0-9_]+)", txt, re.I):
            names.add(m.group(1).replace("_", "").lower())
    return names


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "5 "
    files = loaded_files(prefix)
    per_file = []
    tok_rules, tok_uses, tok_first = Counter(), Counter(), {}
    headvars = Counter()
    showsteps = 0
    for parts in files:
        p = RULE_DIR.joinpath(*parts[:-1]) / (parts[-1] + ".m")
        src = p.read_text()
        showsteps += sum(1 for l in src.splitlines() if "LoadShowSteps" in l)
        n = 0
        # The generator's own unwrap: a single-line
        # If[TrueQ[$LoadShowSteps], <ShowStep rule>, <plain rule>] becomes
        # its plain rule, so the counts and rule numbers here are the
        # GENERATED ones (the 01 census glues such a line onto the rule
        # before it, and counts 665 for class 5, not 667).
        text_all = generate_rules.unwrap_showsteps_lines(
            census.strip_comments(src))
        for run in census.rule_runs(text_all):
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

    print(f"=== class-{prefix.strip()} port: token closure against "
          "translation_table.py ===")
    print(f"files: {len(files)}   rules: {sum(n for _, n in per_file)}   "
          f"LoadShowSteps lines: {showsteps}")
    for name, n in per_file:
        print(f"  {n:4d}  {name}")
    print()
    print("== head variables (pattern variables in head position) ==")
    for t, c in sorted(headvars.items(), key=lambda kv: -kv[1]):
        print(f"  {t:8s} uses={c}")
    listed = {t for t in tok_uses if t in RENAME or t in RESTRUCTURE}
    gen_src = (ROOT / "generator" / "generate_rules.py").read_text()
    emitter = {t for t in tok_uses if t not in listed
               and f'"{t}"' in gen_src}
    unlisted = [t for t in tok_uses if t not in listed and t not in emitter]
    print()
    print(f"== tokens the table translates: {len(listed)} ==")
    for t in sorted(listed, key=lambda t: (-tok_rules[t], t)):
        row = RENAME.get(t, RESTRUCTURE.get(t))
        print(f"  rules={tok_rules[t]:4d} uses={tok_uses[t]:4d}  {t} -> {row}")
    print()
    print(f"== emitter-dispatched (no table row; generate_rules.py names the "
          f"token as a string literal — read the case): {len(emitter)} ==")
    for t in sorted(emitter, key=lambda t: (-tok_rules[t], t)):
        print(f"  rules={tok_rules[t]:4d} uses={tok_uses[t]:4d}  "
              f"{t:24s} first at {tok_first[t]}")
    print()
    print(f"== UNLISTED tokens (adjudicate on the ticket): {len(unlisted)} ==")
    for t in sorted(unlisted, key=lambda t: (-tok_rules[t], t)):
        print(f"  rules={tok_rules[t]:4d} uses={tok_uses[t]:4d}  "
              f"{t:24s} first at {tok_first[t]}")

    # ---- Part 2: transitive closure through the utility file ----------
    defs = utility_definitions()
    have = package_function_names()

    def status(t):
        if t in RENAME or t in RESTRUCTURE:
            return "table"
        if t.lower() in have:
            return "ported"
        return "ABSENT"

    via = {}
    q = deque()
    for t in sorted(tok_uses):
        if t in defs:
            via[t] = "rule"
            q.append(t)
    while q:
        u = q.popleft()
        for t in census.tokens(defs[u]):
            if t in defs and t not in via:
                via[t] = u
                q.append(t)
    print()
    print("== transitive closure through IntegrationUtilityFunctions.m ==")
    print(f"utilities reached: {len(via)}  (rule-side {sum(1 for v in via.values() if v == 'rule')}, "
          f"transitive-only {sum(1 for v in via.values() if v != 'rule')})")
    counts = Counter(status(t) for t in via)
    print(f"status: table {counts['table']}  ported {counts['ported']}  "
          f"ABSENT {counts['ABSENT']}")
    print()
    print("-- rule-side utilities --")
    for t in sorted((t for t in via if via[t] == "rule"),
                    key=lambda t: (status(t), t)):
        print(f"  {status(t):6s}  {t:36s} rules={tok_rules[t]}")
    print()
    print("-- transitive-only utilities (reached through a utility) --")
    for t in sorted((t for t in via if via[t] != "rule"),
                    key=lambda t: (status(t), t)):
        print(f"  {status(t):6s}  {t:36s} via {via[t]}")


if __name__ == "__main__":
    main()
