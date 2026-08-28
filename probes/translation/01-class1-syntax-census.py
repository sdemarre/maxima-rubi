#!/usr/bin/env python3
"""Probe: syntax census of Rubi 4's class-1 (algebraic) rules (T4).

Run from the repo root:
  sh probes/translation/01-class1-syntax-census.run

What it measures (claims recorded in docs/rule-translation.md):
  1. Re-parses only the class-1 rule files that Rubi.m actually
     LoadRules() (reusing 01-inventory's parser), so the census covers
     the milestone-1 rule set, not stale on-disk leftovers.
  2. Frequency of every distinct function token in conditions and in
     replacements (distinct rules using it / total uses).
  3. Pattern features (optional captures, Sqrt heads in patterns,
     powers of the variable).
  4. Token coverage tiers and a rule-level classification:
       BUILTIN  - has a direct Maxima builtin (freeof, integerp, ...)
       B_TIER   - small Rubi utility to port once (Coeff, Expon, ...)
       C_TIER   - structural shape tests / semantics-needing predicates
                  (PolyQ family, PossibleZeroQ inside EqQ, MatchQ, ...)
     A rule is AUTO iff every one of its tokens is BUILTIN or B_TIER;
     otherwise MANUAL, with the C-tier tokens and example rules listed.
  5. Per-file distribution of the manual bucket (the hand-port file
     list).

 Token extraction is deliberately crude (CamelCase name followed by '['):
 it is a census of what the translation script must recognize, not a
 parser. The rule-run parser (column-0 'Int[' to blank line, with the
 dangling-':=' interior-blank exception — see rule_runs) is the same
 convention as 01-inventory, whose totals it must reproduce.
"""

import importlib.util
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

_inv_path = Path(__file__).resolve().parents[1] / "probe-rubi-anatomy" \
    / "01-inventory.py"
_spec = importlib.util.spec_from_file_location("inv01", _inv_path)
assert _spec is not None and _spec.loader is not None
_inv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_inv)
strip_comments = _inv.strip_comments
parse_load_rules = _inv.parse_load_rules


def rule_runs(src_stripped):
    """Same rule-run convention as 01-inventory.count_rules: a blank line
    terminates a run, EXCEPT a run that still ends in a dangling ':='
    (a comment-only line between the ':=' and the rhs — 4 class-1 rules;
    see count_rules' docstring)."""
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
    return runs


def split_rule(text):
    lhs, rhsfull = text.split(":=", 1)
    if "/;" in rhsfull:
        rhs, cond = rhsfull.split("/;", 1)
    else:
        rhs, cond = rhsfull, ""
    return lhs.strip(), rhs.strip(), cond.strip()


# token tiers; a token absent from all three sets is "unlistied" and
# counts as C-tier (the census prints unlistied tokens separately so a
# new one can never hide)
BUILTIN = {
    "FreeQ", "Not", "IntegerQ", "PosQ", "NegQ", "GtQ", "LtQ", "IGtQ",
    "ILtQ", "LeQ", "GeQ", "ILeQ", "OddQ", "Pi", "E", "I", "Abs", "Sign",
    "Sqrt", "Log", "D", "Mod", "Floor", "IntegerPart", "FractionalPart",
    "Cos", "Sin", "Tanh", "Sinh", "ArcTan", "ArcSin", "ArcCos", "ArcCosh",
    "ArcSinh", "ArcTanh", "Sum", "Factor", "If", "Hold", "ReplaceAll",
    "Coefficient", "Numerator", "Denominator", "PolynomialQuotient",
    "PolynomialRemainder", "PolynomialDivide", "GCD", "Together",
    "Expand", "Cancel", "Min", "Max", "Boole", "Piecewise", "EllipticF",
    "EllipticE", "EllipticPi", "Hypergeometric2F1", "AppellF1",
    "CannotIntegrate", "CoefficientList",
}
B_TIER = {
    "EqQ", "NeQ", "RationalQ", "IntegersQ", "FractionQ", "Coeff",
    "Expon", "Simp", "Simplify", "SimplifyIntegrand", "Rt", "Dist",
    "With", "Module", "Subst", "SubstFor", "SubstPower", "IntPart",
    "FracPart", "Int", "Unintegrable", "IntHide", "ShowStep", "Integrate",
    "ExpandIntegrand", "ExpandToSum", "ExpandLinearProduct", "IntSum",
    "RemoveContent", "Numer", "Denom", "PolyGCD", "RationalFunctionExpand",
    "NormalizePseudoBinomial", "Root", "Quotient", "Binomial",
    "Csc", "Sec", "FullSimplify", "Rationalize", "Power", "Plus",
    "Times",
}
C_TIER = {
    "PolyQ", "LinearQ", "BinomialQ", "QuadraticQ", "TrinomialQ",
    "IntLinearQ", "IntBinomialQ", "IntQuadraticQ", "LinearMatchQ",
    "BinomialMatchQ", "QuadraticMatchQ", "TrinomialMatchQ",
    "GeneralizedBinomialQ", "GeneralizedTrinomialQ",
    "GeneralizedBinomialMatchQ", "GeneralizedTrinomialMatchQ",
    "GeneralizedBinomialDegree", "GeneralizedTrinomialDegree",
    "BinomialDegree", "SumQ", "SumSimplerQ", "SimplerQ", "SimplerSqrtQ",
    "NiceSqrtQ", "RationalFunctionQ", "MatchQ", "SplitProduct",
    "NonfreeFactors", "FractionalPowerFactorQ", "LeafCount",
    "PolynomialQ", "AtomQ", "PerfectSquareQ", "MonomialQ",
    "LinearPairQ", "PseudoBinomialPairQ", "InverseFunctionQ",
    "AlgebraicFunctionQ", "PossibleZeroQ",
}


def tier_of(t):
    if t in BUILTIN:
        return "B"
    if t in B_TIER:
        return "b"
    return "C"


def tokens(s):
    return [m.group(1)
            for m in re.finditer(r"\b([A-Z][A-Za-z0-9]*)\s*(?=\[)", s)]


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "reference/rubi")
    classp = sys.argv[2] if len(sys.argv) > 2 else "1 "
    rubi_m = (root / "Rubi" / "Rubi.m").read_text()
    rule_dir = root / "Rubi" / "IntegrationRules"

    loaded = []
    for parts, _gated in parse_load_rules(rubi_m):
        if parts[0].startswith("$") or not parts[0].startswith(classp):
            continue
        p = rule_dir.joinpath(*parts)
        if not p.name.endswith(".m"):
            p = p.with_name(p.name + ".m")
        if p.exists():
            loaded.append(p)

    n_rules = n_cond = 0
    cond_rules = Counter(); cond_use = Counter()
    repl_rules = Counter(); repl_use = Counter()
    pat_feats = Counter()
    opt_hist = Counter()
    auto = manual = 0
    c_cond_tok = Counter(); c_repl_tok = Counter()
    unlistied = Counter()
    manual_files = Counter()
    manual_tokens_per_file = defaultdict(Counter)
    examples = {}

    def is_unlistied(t):
        return t not in BUILTIN and t not in B_TIER and t not in C_TIER

    for p in sorted(loaded):
        rel = p.relative_to(rule_dir).as_posix()
        for run in rule_runs(strip_comments(p.read_text())):
            text = "\n".join(run)
            if ":=" not in text:
                continue
            n_rules += 1
            lhs, rhs, cond = split_rule(text)
            label = f"{rel} :: {lhs[:70]}"
            if cond:
                n_cond += 1
                for t in set(tokens(cond)):
                    cond_rules[t] += 1
                for t in tokens(cond):
                    cond_use[t] += 1
            for t in set(tokens(rhs)):
                repl_rules[t] += 1
            for t in tokens(rhs):
                repl_use[t] += 1
            opts = set(re.findall(r"([A-Za-z][A-Za-z0-9]*)_\.", lhs))
            opt_hist[len(opts)] += 1
            if opts:
                pat_feats["optional captures"] += 1
            if "x_Symbol" in lhs:
                pat_feats["x_Symbol"] += 1
            heads = {m.group(1) for m in re.finditer(
                r"\b([A-Z][A-Za-z0-9]*)\s*\[", lhs)} - {"Int"}
            for h in heads:
                pat_feats[f"head in pattern: {h}"] += 1
            if re.search(r"x_\^|\^x_|x\^[a-zA-Z]", lhs):
                pat_feats["power of capture/x in pattern"] += 1

            cset = set(tokens(cond))
            rset = set(tokens(rhs))
            for t in cset:
                if tier_of(t) == "C":
                    c_cond_tok[t] += 1
                if is_unlistied(t):
                    unlistied[t] += 1
            for t in rset:
                if tier_of(t) == "C":
                    c_repl_tok[t] += 1
                if is_unlistied(t):
                    unlistied[t] += 1
            exotic = bool(re.search(
                r"(__|___|_\?|_Integer|_Real|_Complex|_Rational)", lhs))
            ctoks = {t for t in (cset | rset) if tier_of(t) == "C"}
            utoks = {t for t in (cset | rset) if is_unlistied(t)}
            if not ctoks and not utoks and not exotic:
                auto += 1
            else:
                manual += 1
                manual_files[rel] += 1
                manual_tokens_per_file[rel][
                    ",".join(sorted(ctoks | utoks)) +
                    (" +exotic-pattern" if exotic else "")
                ] += 1
                for t in sorted(ctoks):
                    n, _ = examples.get(t, (0, ""))
                    if n < 2:
                        examples[t] = (n + 1, label +
                                       "   | cond: " + cond[:80])

    print("=== class-1 rule syntax census (only Rubi.m-loaded files) ===")
    print(f"loaded rule files: {len(loaded)}   rules: {n_rules}   "
          f"with /; condition: {n_cond}")
    print("optional-capture histogram (rules by # distinct a_. names):")
    for k in sorted(opt_hist):
        print(f"  {k} optional names: {opt_hist[k]} rules")
    print()
    print(f"rule classification: AUTO (tokens all BUILTIN/B_TIER): "
          f"{auto} ({100*auto/n_rules:5.1f}%)")
    print(f"                      MANUAL (>=1 C-tier token/exotic "
          f"pattern): {manual} ({100*manual/n_rules:5.1f}%)")
    print()
    print("== condition tokens: tier | rules | uses | token "
          "(U = unlistied) ==")
    for t, c in cond_rules.most_common():
        mark = "U" if is_unlistied(t) else tier_of(t)
        print(f"  {mark}   rules={cond_rules[t]:4d}  uses={c:5d}  {t}")
    print()
    print("== replacement tokens: tier | rules | uses | token "
          "(U = unlistied) ==")
    for t, c in repl_rules.most_common():
        mark = "U" if is_unlistied(t) else tier_of(t)
        print(f"  {mark}   rules={repl_rules[t]:4d}  uses={c:5d}  {t}")
    print()
    print("== pattern features ==")
    for f_, c in sorted(pat_feats.items()):
        print(f"  {c:5d}  {f_}")
    print()
    print("== C-tier tokens in conditions/rules (rules containing) ==")
    for t, c in c_cond_tok.most_common():
        print(f"  {c:4d}  {t}")
    if c_repl_tok:
        print("== C-tier tokens in replacements ==")
        for t, c in c_repl_tok.most_common():
            print(f"  {c:4d}  {t}")
    if unlistied:
        print("== UNLISTIED tokens (not in any tier — need triage) ==")
        for t, c in unlistied.most_common():
            print(f"  {c:4d}  {t}")
    print()
    print("== manual bucket by file (rules / distinct token-sets) ==")
    for rel, c in manual_files.most_common():
        tsets = len(manual_tokens_per_file[rel])
        print(f"  rules={c:3d}  distinct-sets={tsets}  {rel}")
    print()
    print("== C-tier token examples (first 2 rules each) ==")
    for t in sorted(examples):
        print(f"  [{t}] {examples[t][1]}")


if __name__ == "__main__":
    main()
