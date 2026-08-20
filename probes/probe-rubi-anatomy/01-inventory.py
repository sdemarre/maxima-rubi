#!/usr/bin/env python3
"""Probe: inventory of Rubi 4's rule files and rule counts (T1).

Run from the repo root:
  python3 probes/probe-rubi-anatomy/01-inventory.py [reference/rubi]

What it measures (claims recorded in docs/rubi-architecture.md):
  1. Every LoadRules[...] path in Rubi/Rubi.m: does the file exist on
     disk? (detects references to missing files)
  2. Every .m file under Rubi/IntegrationRules that is NOT referenced
     by Rubi.m (stale/renamed leftovers).
  3. Rule count per loaded file and per class. A rule is a maximal
     run of lines starting at column 0 with 'Int[' and continuing
     until a blank line or the next 'Int[' line; it must contain ':='
     somewhere in the run. After stripping (* ... *) comments, a
     commented-out rule block never counts.
  4. Per rule: whether it carries a /; condition (after ':='), whether
     the right-hand side re-dispatches (calls Int[...]), whether it
     uses Subst[...].

Driver cross-check target: Rubi.m sets
  $RuleCount = Length[DownValues[Int]]
immediately after all LoadRules calls; our per-file totals over the
ALWAYS-loaded files (no $LoadElementaryFunctionRules gating) must
equal that number when everything loads.
"""

import re
import sys
from collections import OrderedDict
from pathlib import Path


def strip_comments(src):
    """Remove (* ... *) comments, preserving newlines.

    FIX (2026-08-20, Task 6): NESTED, per Mathematica's comment
    semantics — a `(*` inside a comment raises the depth; the comment
    ends at the matching `*)`. The old non-nested scan (first `*)`
    wins) left a live-text tail whenever a comment contained its own
    `(* ... *)` (one class-1 file does: 1.1.1.3's commented-out rule
    carries an inner comment), which glued comment debris onto the
    preceding rule. Measured 2026-08-20: the per-file rule counts and
    the 2710 total are UNCHANGED by the fix (debris never started a
    new run); the census token histograms shed the debris tokens."""
    out = []
    i, n, depth = 0, len(src), 0
    while i < n:
        if depth > 0:
            if src.startswith("(*", i):
                depth += 1; i += 2
            elif src.startswith("*)", i):
                depth -= 1; i += 2
            else:
                out.append("\n" if src[i] == "\n" else " ")
                i += 1
        elif src.startswith("(*", i):
            j = i + 2
            depth = 1
            while j < n and depth > 0:
                if src.startswith("(*", j):
                    depth += 1; j += 2
                elif src.startswith("*)", j):
                    depth -= 1; j += 2
                else:
                    j += 1
            out.append("\n" * src.count("\n", i, j))
            i = j
        else:
            out.append(src[i])
            i += 1
    return "".join(out)


def parse_load_rules(rubi_m):
    """Return [(path_parts_tuple, gated_by_elementary_flag), ...] in order.

    Only recognises the two real call forms:
      LoadRules[FileNameJoin[{"a", "b", ...}]]
      LoadRules[$name]
    The fallback *definition* lines (LoadRules[fileName_String ...] and
    LoadRules[arg___]) must NOT match.
    """
    out = []
    # split Rubi.m at the $LoadElementaryFunctionRules If-block: rules
    # inside it are optional; outside, mandatory.
    flag_re = r"If\[\$LoadElementaryFunctionRules===True,"
    m_flag = re.search(flag_re, rubi_m)
    flag_start, flag_end = None, None
    if m_flag is not None:
        flag_start = m_flag.start()
        # closing ']' of that If: match brackets from the If[ itself
        depth = 0
        i = rubi_m.index("[", m_flag.start())
        for j in range(i, len(rubi_m)):
            if rubi_m[j] == "[":
                depth += 1
            elif rubi_m[j] == "]":
                depth -= 1
                if depth == 0:
                    flag_end = j
                    break
    for m in re.finditer(r"LoadRules\[FileNameJoin\[\{((?:\"[^\"]*\"\s*,\s*)*\"[^\"]*\")\}\]\]", rubi_m):
        parts = tuple(re.findall(r'"([^"]*)"', m.group(1)))
        gated = flag_start is not None and flag_start < m.start() < (flag_end or len(rubi_m))
        out.append((parts, gated))
    for m in re.finditer(r"LoadRules\[(\$[A-Za-z]+)\]", rubi_m):
        gated = flag_start is not None and flag_start < m.start() < (flag_end or len(rubi_m))
        out.append((("$" + m.group(1)[1:],), gated))
    return out


def count_rules(src_stripped):
    """Count rule runs in comment-stripped source.

    Returns (rules, with_cond, rhs_int, rhs_subst). A rule run is the
    sequence of lines from a column-0 'Int[' line to the next column-0
    'Int[' line or blank line — EXCEPT a blank line does not terminate a
    run that still ends in a dangling ':=': a comment-only line (e.g.
    1.1.2.1 :93 — 4 class-1 rules) may sit between the ':=' and the rhs,
    and stripping the comment leaves a blank that would otherwise cut the
    run short and silently drop the rhs/cond lines. A complete rule never
    ends in ':=', so this cannot swallow the scaffolding that follows a
    complete rule (the If[TrueQ[$LoadShowSteps]] block in 1.4.1).
    """
    lines = src_stripped.split("\n")
    runs = []
    cur = None
    for line in lines:
        if line.startswith("Int["):
            if cur is not None:
                runs.append(cur)
            cur = [line]
        elif cur is not None:
            if line.strip() == "" and not "\n".join(cur).rstrip().endswith(":="):
                runs.append(cur)
                cur = None
            else:
                cur.append(line)
    if cur is not None:
        runs.append(cur)

    rules = cond = redispatch = subst = 0
    for run in runs:
        text = "\n".join(run)
        if ":=" not in text:
            continue  # not a definition (defensive; should not happen)
        rules += 1
        rhs_start = text.index(":=")
        rhs = text[rhs_start + 2:]
        if "/;" in rhs:
            cond += 1
        if "Int[" in rhs:
            redispatch += 1
        subst += rhs.count("Subst[")
    return rules, cond, redispatch, subst


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "reference/rubi")
    rubi_dir = root / "Rubi"
    rubi_m = (rubi_dir / "Rubi.m").read_text()
    rule_dir = rubi_dir / "IntegrationRules"

    per_file = OrderedDict()  # rel -> (path, gated, (rules, cond, rd, subst))
    per_class = OrderedDict()
    grand = [0, 0, 0, 0]
    mandatory = [0, 0, 0, 0]  # not behind $LoadElementaryFunctionRules
    missing = []
    referenced = set()

    for parts, gated in parse_load_rules(rubi_m):
        name = parts[0]
        if name.startswith("$"):
            continue  # $utilityPackage / $stepRoutines / $ruleFormatting
        p = rule_dir.joinpath(*parts)
        if not p.name.endswith(".m"):
            p = p.with_name(p.name + ".m")
        referenced.add(p)
        exists = p.exists()
        if not exists:
            missing.append(p.relative_to(rule_dir).as_posix())
            continue
        rel = p.relative_to(rule_dir).as_posix()
        counts = count_rules(strip_comments(p.read_text()))
        per_file[rel] = (p, gated, counts)
        cls = rel.split("/")[0]
        agg = per_class.setdefault(cls, [0, 0, 0, 0])
        for i in range(4):
            agg[i] += counts[i]
            grand[i] += counts[i]
        if not gated:
            for i in range(4):
                mandatory[i] += counts[i]

    stale = sorted(p for p in rule_dir.rglob("*.m") if p not in referenced)

    print("=== referenced-but-missing files ({})".format(len(missing)))
    for m_ in missing:
        print("  MISSING:", m_)
    print()
    print("=== stale .m files on disk, never loaded by Rubi.m ({})".format(len(stale)))
    for p in stale:
        print("  STALE:", p.relative_to(rule_dir).as_posix())
    print()
    def show(rels):
        for rel, (_p, _g, (r, c, rd, s)) in per_file.items():
            if any(rel.startswith(p) for p in rels):
                print("  {:5d}  cond={:<3d} redisp={:<3d} subst={:<3d}  {}".format(r, c, rd, s, rel))

    print("=== per-file rule counts, class 1 (algebraic) ===")
    show(("1 ",))
    print()
    print("=== per-file rule counts, class 9 (miscellaneous) ===")
    show(("9 ",))
    print()
    print("=== per-class rule counts (all rule files loaded by Rubi.m) ===")
    print("  {:42s} {:>6s} {:>8s} {:>8s} {:>7s}".format("class", "rules", "with /;", "re-disp", "Subst"))
    for cls in sorted(per_class):
        print("  {:42s} {:6d} {:8d} {:8d} {:7d}".format(cls, *per_class[cls]))
    print("  {:42s} {:6d} {:8d} {:8d} {:7d}".format("TOTAL (all loaded classes)", *grand))
    print()
    print("=== MANDATORY (no $LoadElementaryFunctionRules gating) ===")
    print("  rule files' Int downvalues, pre-StepFunction: {:d}".format(mandatory[0]))
    print("  (driver cross-check: Rubi.m sets $RuleCount = Length[DownValues[Int]])")


if __name__ == "__main__":
    main()
