#!/usr/bin/env python3
"""probes/rubi/05-section9-utility-closure.py -- the transitive utility
closure behind the section-9 port (spec
docs/superpowers/specs/2026-09-22-section9-port-design.md section 3.3,
amendment A1). Static, no Maxima.

Starts from the eleven utility names the 9.2/9.3 rules call that the
translation table does not list (probes/translation/07, the spec's
section 2 "missing" row), and walks every capitalised identifier in each
missing name's IntegrationUtilityFunctions.m definition -- called
(`Name[`) or passed as a value (`Map[Name, lst]`) -- until no new name
appears. Each name is classified:

  table    a translation_table.py RENAME/RESTRUCTURE row (emittable);
  ported   a `%mr_<Name>(` definition in maxima_rubi_utils.mac
           (case-insensitive), reachable from a hand port;
  MISSING  defined in IntegrationUtilityFunctions.m, neither of the above:
           to port (or to replace inside a port, see the spec);
  builtin  a Mathematica builtin a hand port translates in place;
  UNKNOWN  none of these (must be 0).

Definitions are split at column-0 `Name[`/`Name :=` lines; a `Name::usage`
line closes the previous definition (without that, each usage string is
glued onto the definition above it and fakes a call edge -- the first
draft of this probe reported 47 with ConstantFactor and
FunctionOfInverseLinear in, both such fakes).
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "generator"))
from translation_table import RENAME, RESTRUCTURE  # noqa: E402

START = ("PiecewiseLinearQ Divides EulerIntegrandQ FunctionOfLinear "
         "FunctionOfSquareRootOfQuadratic PolynomialInQ PolynomialInSubst "
         "PowerVariableExpn SimplerIntegrandQ "
         "SubstForFractionalPowerOfQuotientOfLinears "
         "SubstForFractionalPowerQ").split()
MMA = set("""If With Module Block Catch Throw Scan Function Map Apply First
Rest Last Length Prepend Append ReplacePart ReplaceAll Return While Do Sow Reap
Drop Head Order OrderedQ SameQ UnsameQ Im Re LCM GCD Min Max True False Null
List Plus Times Power Log E I Pi Sqrt DeleteCases MemberQ Not And Or
Denominator Numerator Exponent Coefficient D Simplify FullSimplify
InverseFunction AtomQ IntegerQ FreeQ MatchQ Tan Cot Tanh Coth ArcTan ArcCot
ArcTanh ArcCoth ArcSec ArcCsc ArcSech ArcCsch Symbol Condition Complex Real
Integer Rational EvenQ ListQ N FactorInteger Flatten Sort ShowStep""".split())


def strip_comments(s):
    out, depth, i = [], 0, 0
    while i < len(s):
        if s.startswith("(*", i):
            depth += 1; i += 2; continue
        if s.startswith("*)", i) and depth:
            depth -= 1; i += 2; continue
        if not depth:
            out.append(s[i])
        i += 1
    return "".join(out)


def definitions(text):
    defs, first_line, cur = {}, {}, None
    for no, line in enumerate(text.split("\n"), 1):
        if re.match(r"[A-Z][A-Za-z0-9]*::usage", line):
            cur = None
            continue
        m = re.match(r"([A-Z][A-Za-z0-9]*)(\[|\s*:=|\s*=)", line)
        if m:
            cur = m.group(1)
            defs.setdefault(cur, []).append(line)
            first_line.setdefault(cur, no)
        elif cur:
            defs[cur].append(line)
    return {k: "\n".join(v) for k, v in defs.items()}, first_line


def main():
    raw = (ROOT / "reference/rubi/Rubi/IntegrationUtilityFunctions.m").read_text()
    # comments are blanked, not deleted, so line numbers survive
    text = re.sub(r"\(\*.*?\*\)", lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                  raw, flags=re.S)
    body, line_of = definitions(text)
    utils = (ROOT / "maxima_rubi_utils.mac").read_text()

    def ported(n):
        return re.search(r"^\s*%mr_" + n + r"\s*\(", utils, re.M | re.I) is not None

    seen, queue = {}, [(n, None) for n in START]
    while queue:
        n, parent = queue.pop(0)
        if n in seen or re.fullmatch(r"[A-Z]|Px|Common", n):
            continue
        if RENAME.get(n) or RESTRUCTURE.get(n):
            st = "table"
        elif ported(n):
            st = "ported"
        elif n in body:
            st = "MISSING"
        elif n in MMA:
            st = "builtin"
        else:
            st = "UNKNOWN"
        seen[n] = (st, parent)
        if st == "MISSING":
            toks = set(re.findall(r'(?<![A-Za-z0-9$`"#])([A-Z][A-Za-z0-9]*)(?![A-Za-z0-9_])',
                                  body[n])) - {n}
            queue += [(t, n) for t in sorted(toks)]
    print("# section-9 utility closure (IntegrationUtilityFunctions.m @ pinned clone)")
    print("# start: %d names: %s" % (len(START), " ".join(START)))
    for st in ("MISSING", "UNKNOWN", "ported", "table", "builtin"):
        rows = [(n, p) for n, (s, p) in seen.items() if s == st]
        print("\n== %s (%d)" % (st, len(rows)))
        for n, p in rows:
            where = ("  L%d" % line_of[n]) if n in line_of else ""
            print("  %-44s <- %-44s%s" % (n, p or "(start)", where))


if __name__ == "__main__":
    main()
