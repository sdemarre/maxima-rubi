#!/usr/bin/env python3
"""probes/matcher/13-translation-shape-scan.py -- the shape scans of the
matcher translation fixes (design docs/superpowers/specs/2026-09-14-matcher-
translation-fixes-design.md section 3.5). No Maxima.

Sections (each ends in PASS/FAIL lines; the run ends with a Results line):

  IGT    integer comparisons: per class and head (IGtQ, ILtQ, ILeQ, IGeQ),
         the source call count (the generator's own file list and comment
         stripping) against the emitted %mr_i<head> call count in
         rules/class<N>/*.mac. Equal once the heads translate to the named
         entries.
  OPS    leftover Mathematica operators in the generated cond/repl bodies
         (string literals masked): != === =!= prefix-! @ /@ -> :>.
  GAP    a whitespace gap between two expression terms in a cond/repl body
         (Maxima words such as `and` excepted) -- juxtaposition.
  FIRST  every Rubi utility function whose IntegrationUtilityFunctions.m
         definition reads First/Rest/Last, classified in TABLE below:
         internal (the port must read Maxima's internal order: inpart,
         inflag : true or %mr_args_in in its body), independent (the result
         does not depend on which part is first -- reason given), or
         unported. The table's names must equal the scanned set.

Usage (repo root):  python3 probes/matcher/13-translation-shape-scan.py
"""

import collections
import datetime
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "generator"))
import generate_rules as g  # noqa: E402

UTILS = ROOT / "maxima_rubi_utils.mac"
UTIL_M = ROOT / "reference" / "rubi" / "Rubi" / "IntegrationUtilityFunctions.m"
HEADS = {"IGtQ": "%mr_iGtQ", "ILtQ": "%mr_iLtQ", "ILeQ": "%mr_iLeQ", "IGeQ": "%mr_iGeQ"}
FUN = re.compile(r"^_mr_(cond|repl)_([0-9a-z_]+?)_r(\d+)\(mm, x\) := (.*?)\)\$\n", re.M | re.S)
UTIL_DEF = re.compile(r"^\s*([A-Z][A-Za-z0-9]*)\[[^\n]*?:=")
# rule-file utility definitions that use an integer comparison -> their
# hand ports in maxima_rubi_utils.mac (which call %mr_IGtQ / %mr_ILtQ)
UTIL_IGT_PORTS = {
    "IntLinearQ": ["%mr_intLinearQ"],
    "IntQuadraticQ": ["%mr_intQuadraticQ"],
    "IntBinomialQ": ["%mr_intBinomialQ7", "%mr_intBinomialQ8", "%mr_intBinomialQ10"],
}
WORDS = {"and", "or", "not", "then", "else", "elseif", "if", "do", "in", "block", "return",
         "true", "false", "for", "while", "unless", "thru", "step", "from"}

# Rubi name -> (kind, ports, reason)
TABLE = {
    "PosAux": ("internal", ["%mr_posAux"], "sum branch reads the first term"),
    "NegSumBaseQ": ("internal", ["%mr_rt_negSumBaseQ"], "NegQ of the first term"),
    "RemoveContentAux": ("internal", ["%mr_removeContentAux"], "NegQ of the first term"),
    "SignOfFactor": ("internal", ["%mr_signOfFactor"], "NumericFactor of the first term"),
    "ContentFactorAux": ("internal", ["%mr_contentFactor"], "power branch: NumericFactor of the base's first term"),
    "SplitProduct": ("internal", ["%mr_product_factors"], "the first factor passing func"),
    "RtAux": ("internal", ["%mr_product_factors"], "RtAux[-First[v],n]: the first factor of the factor list"),
    "SplitSum": ("internal", ["%mr_splitSum_aux"], "the first term passing func"),
    "UnifyTerm": ("internal", ["%mr_unifySum"], "the term list order (Apply[List, u])"),
    "UnifyTerms": ("internal", ["%mr_unifySum"], "the term list order (Apply[List, u])"),
    "AlgebraicFunctionQ": ("independent", ["%mr_algebraicFunctionQ"], "And over every part"),
    "AllNegTermQ": ("independent", ["%mr_rt_allNegTermQ"], "And over every term"),
    "SomeNegTermQ": ("independent", ["%mr_rt_someNegTermQ"], "Or over every term"),
    "BinomialParts": ("independent", ["%mr_binomial_parts"], "FreeQ[First]/FreeQ[Rest] split handles both orders"),
    "TrinomialParts": ("independent", ["%mr_trinomial_parts"], "symmetric split; First/Last of a coefficient list"),
    "EasyDQ": ("independent", ["%mr_easyDQ"], "symmetric FreeQ split; And over terms"),
    "FractionalPowerFactorQ": ("independent", ["%mr_fractionalPowerFactorQ"], "Or over factors"),
    "FunctionOfExponentialFunctionAux": ("independent", ["%mr_foEFunctionAux"], "product of both exponent parts' rewrites"),
    "FunctionOfExponentialTest": ("independent", ["%mr_foE_test2"], "And over both exponent parts"),
    "MinimumMonomialExponent": ("independent", ["%mr_minimumMonomialExponent"], "minimum over terms"),
    "NumericFactor": ("independent", ["%mr_numericFactor"], "gcd of first and rest"),
    "ProductOfLinearPowersQ": ("independent", ["%mr_productOfLinearPowersQ"], "And over factors"),
    "RationalFunctionExponents": ("independent", ["%mr_rationalFunctionExponents"], "sum / max over both parts"),
    "SumSimplerAuxQ": ("independent", ["%mr_sumSimplerAuxQ"], "And/Or over both parts"),
}
for _n in ("AbsurdNumberGCD AbsurdNumberGCDList CancelCommonFactors CombineExponents CommonFactors "
           "ConstantFactor FunctionOfExpnQ LeadFactor LeadTerm MakeAssocList MergeFactor MergeFactors "
           "MergeableFactorQ MonomialFactor PerfectPowerTest RemainingFactors RemainingTerms SimpHelp "
           "Smallest SqrtNumberSumQ SubstForAux").split():
    TABLE[_n] = ("unported", [], "")


class Gate:
    def __init__(self):
        self.passed = self.failed = 0

    def check(self, name, ok, detail=""):
        if ok:
            self.passed += 1
            print("PASS: %s" % name)
        else:
            self.failed += 1
            print("FAIL: %s%s" % (name, ("\n    " + detail) if detail else ""))


def mask_strings(s):
    return re.sub(r'"[^"]*"', '""', s)


def class_sources(c):
    g.configure(c)
    files = list(g.load_class_files(g.RUBI))
    if c == 1:
        files += g.EXTRA_CLASS1 + [g.NINE_ONE]
    return [g.unwrap_showsteps_lines(g.strip_comments((g.RUBI / rel).read_text()))
            for rel in files if (g.RUBI / rel).exists()]


def bodies(c):
    out = []
    for p in sorted((ROOT / "rules" / ("class%d" % c)).glob("*.mac")):
        for kind, key, n, body in FUN.findall(p.read_text()):
            out.append(("%s r%s %s" % (key, n, kind), mask_strings(body)))
    return out


def util_defs():
    """name -> body text (comments removed) of every top-level utils definition."""
    t = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), UTILS.read_text(), flags=re.S)
    lines = t.split("\n")
    starts = [(i, m.group(1)) for i, l in enumerate(lines)
              for m in [re.match(r"\s*(%mr_[A-Za-z0-9_]+)\(.*?\)\s*:=", l)] if m]
    starts.append((len(lines), None))
    return {name: "\n".join(lines[i:j]) for (i, name), (j, _) in zip(starts, starts[1:])}


def rubi_first_rest_names():
    t = re.sub(r"\(\*.*?\*\)", lambda m: "\n" * m.group(0).count("\n"), UTIL_M.read_text(), flags=re.S)
    names, cur = set(), None
    for l in t.split("\n"):
        m = re.match(r"^([A-Z][A-Za-z0-9]*)\[", l)
        if m:
            cur = m.group(1)
        if cur and re.search(r"\b(First|Rest|Last)\[", l):
            names.add(cur)
    return names


def main():
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    print("=== probes/matcher/13-translation-shape-scan  git HEAD %s  %s" % (
        head, datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))
    gate = Gate()

    print("SECTION IGT")
    defs = util_defs()
    for p in ("%mr_IGtQ", "%mr_ILtQ"):
        gate.check("IGT hand-written %s keeps the integer test" % p,
                   bool(re.search(r"%mr_integerQ\(|integerp\(", defs.get(p, ""))))
    for c in (1, 2, 3):
        src = class_sources(c)
        emitted = "".join(mask_strings(p.read_text())
                          for p in sorted((ROOT / "rules" / ("class%d" % c)).glob("*.mac")))
        # a rule file's own utility definitions (IntLinearQ[...] := ...) are
        # not generated: they are hand-ported in the utils (UTIL_IGT_PORTS)
        rule_lines, util_calls = [], collections.Counter()
        for t in src:
            for line in t.split("\n"):
                m = UTIL_DEF.match(line)
                if m and m.group(1) != "Int":
                    util_calls[m.group(1)] += len(re.findall(r"\b(?:IGtQ|ILtQ|ILeQ|IGeQ)\[", line))
                else:
                    rule_lines.append(line)
        for name, k in sorted(util_calls.items()):
            if not k:
                continue
            ports = UTIL_IGT_PORTS.get(name, [])
            print("INFO: class %d utility definition %s: %d integer comparisons, hand ports %s" % (
                c, name, k, ports))
            gate.check("IGT class %d %s hand ports call the integer-test entries" % (c, name),
                       bool(ports) and all(re.search(r"%mr_[iI][GL][te]Q\(", defs.get(p, "")) for p in ports))
        rules_text = "\n".join(rule_lines)
        for h, entry in HEADS.items():
            ns = len(re.findall(r"\b%s\[" % h, rules_text))
            ne = len(re.findall(re.escape(entry) + r"\(", emitted))
            print("INFO: class %d %s source %d emitted %s %d" % (c, h, ns, entry, ne))
            gate.check("IGT class %d %s: source %d = emitted %d" % (c, h, ns, ne), ns == ne)

    ops = [("!=", r"!="), ("===", r"==="), ("=!=", r"=!="), ("prefix !", r"(?<![A-Za-z0-9_%)\]!])!(?!=)"),
           ("@", r"@"), ("/@", r"/@"), ("->", r"->"), (":>", r":>")]
    gaps = re.compile(r"([A-Za-z0-9_%]+|[)\]])(\s+)(?=([A-Za-z0-9_%]+|\())")
    for c in (1, 2, 3):
        bs = bodies(c)
        print("SECTION OPS class %d (%d bodies)" % (c, len(bs)))
        for name, rx in ops:
            sites = [(rid, m.start()) for rid, b in bs for m in re.finditer(rx, b)]
            for rid, _pos in sites[:20]:
                print("SITE: OPS class %d %s %s" % (c, name, rid))
            gate.check("OPS class %d %s: 0 sites (%d)" % (c, name, len(sites)), not sites)
        print("SECTION GAP class %d" % c)
        sites = []
        for rid, b in bs:
            for m in gaps.finditer(b):
                if m.group(1) in WORDS or m.group(3) in WORDS:
                    continue
                sites.append((rid, b[max(0, m.start() - 30):m.end() + 30]))
        for rid, ctx in sites[:20]:
            print("SITE: GAP class %d %s ...%s..." % (c, rid, ctx))
        gate.check("GAP class %d: 0 juxtapositions (%d)" % (c, len(sites)), not sites)

    print("SECTION FIRST")
    names = rubi_first_rest_names()
    gate.check("FIRST table covers the %d Rubi First/Rest/Last functions" % len(names),
               names == set(TABLE),
               "missing %s; extra %s" % (sorted(names - set(TABLE)), sorted(set(TABLE) - names)))
    defs = util_defs()
    lowered = {k.replace("_", "").lower(): k for k in defs}
    for rubi in sorted(TABLE):
        kind, ports, reason = TABLE[rubi]
        if kind == "unported":
            hit = [v for k, v in lowered.items() if k.startswith("%mr" + rubi.lower())]
            gate.check("FIRST %s unported (no %%mr_ definition by name)" % rubi, not hit, str(hit))
            continue
        for p in ports:
            body = defs.get(p)
            if body is None:
                gate.check("FIRST %s -> %s defined" % (rubi, p), False)
                continue
            if kind == "internal":
                ok = bool(re.search(r"\binpart\(|inflag\s*:\s*true|%mr_args_in\(|%mr_rest_in\(", body))
                gate.check("FIRST %s -> %s reads internal order (%s)" % (rubi, p, reason), ok)
            else:
                print("INFO: FIRST %s -> %s independent: %s" % (rubi, p, reason))
                gate.check("FIRST %s -> %s defined" % (rubi, p), True)

    print("Results: %d passed, %d failed" % (gate.passed, gate.failed))
    return 1 if gate.failed else 0


if __name__ == "__main__":
    sys.exit(main())
