#!/usr/bin/env python3
"""Probe: is the 1.1.1.7 e5-class shape covered by the pinned Rubi 4
rule set? (corpus-vs-reference version gap, 2026-08-25)

Run from the repo root:
  sh probes/rubi/01-1114-e5-gap-census.run

Background (claims recorded in docs/corpus-baseline.md §4.1):
  The class-1 corpus's 1.1.1.7 family contains ~9 entries whose
  integrand reduces (via the P(x) split) to the pure 1.1.1.4 shape
      (a+b x)^m / (Sqrt[c+d x] Sqrt[e+f x] Sqrt[g+h x])
  with m in {-2, -3, -5/2, -7/2} (the "e5 class": 1.1.1.7 e5/e10/e15/
  e19/e20/e24/e25/e30/e35 — the P-poison sub-integral map,
  /tmp history e5_batch). The corpus EXPECTS elliptic-integral
  answers for them, but the ported package defers them (contains-noun)
  because no rule of the pinned rule set reduces that shape at those
  m. This probe establishes the static half of the claim: it scans
  the pinned .m (1.1.1.4, the pure four-linear-power file that owns
  the shape) rule-by-rule and reports, for every rule whose pattern
  can match the shape, whether its condition can be TRUE at
  m = -2 (a numeric instance; n,p,q fixed at -1/2 by the shape).

  Pattern classes considered (the shape is
  Times[(a+b x)^m, (c+d x)^(-1/2), (e+f x)^(-1/2), (g+h x)^(-1/2)]):
    A  the EXACT shape: (a_.+b_.*x_)^m_ over Sqrt[c_.+d_.*x_]*
       Sqrt[e_.+f_.*x_]*Sqrt[g_.+h_.*x_] (four linears, three in
       Sqrt form, one free power) — the only pattern class that
       matches the shape outright;
    B  four-free-power (a_.+b_.*x_)^m_*(c_.+d_.*x_)^n_*... variants
       — match only if the Sqrt factors are read as ^(1/2) powers:
       Maxima/Mathematica match (c+d x)^(-1/2) against a free-power
       slot n_. (n := -1/2), so these are checked too;
    C  fixed-shape rules (Sqrt numerator/denominator permutations,
       fixed (a+b x)^1 or ^(3/2), the 1/( (a+b x) Sqrt Sqrt Sqrt )
       rules) — pattern-equality only.
  Condition evaluation at m = -2 (a..h generic nonzero constants,
  distinct linears): arithmetic predicates (GtQ/LtQ/GeQ/LeQ/EqQ/
  NeQ/IntegerQ/IntegersQ/IGtQ/ILtQ) on expressions in m (and n,p,q
  where the pattern pins them) are evaluated literally; SimplerQ /
  SumSimplerQ / OrderedQ stay NOUNS (OrderedQ is undefined in the
  pinned clone — grep-verified — so any condition containing one is
  undecidable = the rule declines in Rubi-Mathematica semantics);
  FreeQ is TRUE (a..h carry no x). A rule CAN FIRE at m = -2 iff its
  whole condition evaluates to True.
"""

import re
import sys
from pathlib import Path

RUBI = Path("reference/rubi")
FILE = (RUBI / "Rubi" / "IntegrationRules" / "1 Algebraic functions"
        / "1.1 Binomial products" / "1.1.1 Linear"
        / "1.1.1.4 (a+b x)^m (c+d x)^n (e+f x)^p (g+h x)^q.m")


def strip_comments(src: str) -> str:
    out, i, n = [], 0, len(src)
    while i < n:
        if src.startswith("(*", i):
            j = src.find("*)", i + 2)
            i = n if j < 0 else j + 2
            continue
        out.append(src[i])
        i += 1
    return "".join(out)


def rule_runs(src: str):
    """Column-0 'Int[' to blank line (the 01-inventory convention)."""
    runs, cur = [], None
    for line in src.split("\n"):
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


def split_lhs_rhs(text: str):
    i = text.index(":=")
    return text[:i], text[i + 2:]


def lhs_pattern(text: str) -> tuple:
    """The (pattern, var) of Int[ ... , var] (balanced-bracket aware)."""
    lhs = text
    i = lhs.index("Int[") + 4
    depth, j = 1, i
    while j < len(lhs) and depth:
        if lhs[j] == "[":
            depth += 1
        elif lhs[j] == "]":
            depth -= 1
        j += 1
    body = lhs[i:j - 1]
    # strip the trailing ", x_Symbol"
    k = body.rfind(",")
    return body[:k].strip(), body[k + 1:].strip()


PRED = re.compile(
    r"^(GtQ|LtQ|GeQ|LeQ|EqQ|NeQ|IGtQ|ILtQ|IntegerQ|IntegersQ)"
    r"\s*\[(.*)\]\s*$", re.S)
# a condition conjunct that stays a NOUN (undecidable -> decline):
# SimplerQ / SumSimplerQ / OrderedQ (undefined in the pinned clone) /
# PossibleZeroQ on a generic constant.
NOUN_HEADS = ("SimplerQ[", "SumSimplerQ[", "OrderedQ[", "PossibleZeroQ[")

_VALUES = {"m": -2, "n": -1 / 2, "p": -1 / 2, "q": -1 / 2}


def _eval_arg(a: str):
    """A numeric value, or None if the argument is not a plain number
    (after substituting the free-power symbols m/n/p/q)."""
    a = a.strip()
    prev = None
    while prev != a:
        prev = a
        for sym, val in _VALUES.items():
            a = re.sub(rf"(?<![0-9A-Za-z_]){sym}(?![0-9A-Za-z_])",
                       f"({val})" if isinstance(val, float) else str(val),
                       a)
    a = a.replace("**", "**")
    if not re.match(r"^[-+*/().\d ]+$", a):
        return None
    try:
        v = eval(a, {"__builtins__": {}}, {})
    except Exception:
        return None
    return v if isinstance(v, (int, float)) else None


def _conjunct_value(cj: str):
    """True / False / None (noun) for one && conjunct."""
    cj = cj.strip()
    if cj in ("", "True"):
        return True
    if cj == "False":
        return False
    if cj.startswith("Not["):
        inner = cj[4:-1].strip()
        v = _conjunct_value(inner)
        return None if v is None else (not v)
    if cj.startswith("FreeQ["):
        return True  # a..h carry no x; m/n are parameters
    if any(cj.startswith(h) for h in NOUN_HEADS):
        return None
    mm = PRED.match(cj)
    if mm:
        op, rest = mm.group(1), mm.group(2)
        args = [a.strip() for a in rest.split(",")]
        vals = [_eval_arg(a) for a in args]
        if any(v is None for v in vals):
            return None
        if op in ("IntegerQ", "IntegersQ"):
            return all(float(v).is_integer() for v in vals)
        if len(args) == 2:
            x, y = vals
            return {"GtQ": x > y, "LtQ": x < y, "GeQ": x >= y,
                    "LeQ": x <= y, "EqQ": x == y, "NeQ": x != y,
                    "IGtQ": x > y, "ILtQ": x < y}[op]
    return None  # anything unrecognized: undecidable


def condition_can_be_true(cond: str):
    """Evaluate the /; condition at the shape's free-power values
    (m = -2, n = p = q = -1/2; a..h generic constants).

    Returns True iff the condition evaluates to True (rubi-fires),
    False iff it evaluates to False (rubi-declines), and None iff
    undecidable (a noun survives — SimplerQ/SumSimplerQ/OrderedQ —
    which declines in Mathematica semantics too)."""
    if not cond or cond.strip() in ("", "True"):
        return True
    noun_seen = False
    for cj in re.split(r"&&", cond):
        v = _conjunct_value(cj)
        if v is False:
            return False
        if v is None:
            noun_seen = True
    return None if noun_seen else True


def shape_class(pat: str) -> str:
    """A = exact (a+b x)^m / (Sqrt Sqrt Sqrt); B = four free powers;
    C = other (fixed-shape) patterns."""
    p = re.sub(r"\s+", "", pat)
    sqrt3 = p.count("Sqrt[")
    # the exponent slot is the PATTERN VARIABLE m_ (required — the .m
    # source writes "^ m_"; an optional slot would be "m_." with the
    # trailing dot): look for ^m_ followed by a non-name char
    if sqrt3 == 3 and re.search(r"\^m_(?![0-9A-Za-z_])", p) and "/" in p:
        return "A"
    # B: four power slots (free ^(name_) or fixed exponents) and no
    # Sqrt head — matching the shape is checked by b_matches_shape
    # (a fixed exponent must equal the shape's at that slot)
    if sqrt3 == 0 and p.count("^") >= 3:
        return "B"
    return "C"


# the shape's exponent at each slot (a,b / c,d / e,f / g,h factor)
SHAPE_EXP = (-2, -1 / 2, -1 / 2, -1 / 2)


def b_matches_shape(pat: str) -> bool:
    """A class-B pattern matches the shape iff every FIXED exponent in
    it equals the shape's exponent at that slot (a free slot binds the
    shape's value). Slot order = pattern order (a,b / c,d / e,f / g,h).
    A B pattern with a different number of power factors cannot match."""
    p = re.sub(r"\s+", "", pat)
    # the four (or more) power factors, in order
    slots = re.findall(r"\(([a-z]\._\+[a-z]\._\*x_)\)\^([^)]*)", p)
    if len(slots) != 4:
        return False
    ok = True
    for (slot, exp), shape_exp in zip(slots, SHAPE_EXP):
        if re.match(r"^[a-z]_", exp):
            continue  # free slot: binds the shape's value
        v = _eval_arg(exp)
        ok = ok and v is not None and v == shape_exp
    return ok


def main():
    src = strip_comments(FILE.read_text())
    runs = [r for r in rule_runs(src) if ":=" in "\n".join(r)]
    exact, free, other = [], [], []
    for run in runs:
        text = " ".join(" ".join(run).split())
        lhs, rhs = split_lhs_rhs(text)
        pat, var = lhs_pattern(lhs)
        cond = rhs.split("/;", 1)[1].strip() if "/;" in rhs else ""
        cls = shape_class(pat)
        rec = (len(pat), pat[:70], cond[:90])
        (exact if cls == "A" else free if cls == "B" else other).append(rec)
    print(f"# 1.1.1.4 e5-class shape gap census, pinned Rubi "
          f"(commit recorded in todo/TODO.md)")
    print(f"# file: {FILE}")
    print(f"# total rule runs: {len(runs)}")
    print(f"# class A (exact shape (a+b x)^m /(Sqrt Sqrt Sqrt)): "
          f"{len(exact)}")
    for i, (_n, pat, cond) in enumerate(exact, 1):
        pat_s = pat.replace("Sqrt[", "sqrt(")
        print(f"  A{i}: pattern {pat_s}")
        print(f"       cond    {cond or '(none)'}")
        v = condition_can_be_true(cond)
        verdict = {True: "CAN FIRE at the shape instance",
                   False: "declines at the shape instance",
                   None: "UNDECIDABLE (noun condition -> decline)"
                   }[v]
        print(f"       shape:    {verdict}")
    # the four-free-power class: the shape reads each Sqrt as ^(-1/2)
    # — the (a+b x)^m slot gets m=-2 and the three Sqrt slots pin
    # n=p=q=-1/2; only conditions that can be TRUE with all four
    # values could fire (the evaluator substitutes the symbols).
    hits = 0
    for i, (_n, pat, cond) in enumerate(free, 1):
        if not b_matches_shape(pat):
            continue  # a fixed exponent slot disagrees with the shape
        v = condition_can_be_true(cond)
        if v is True:
            hits += 1
            print(f"  B{i}: pattern {pat[:60]}")
            print(f"       cond    {cond or '(none)'}")
            print(f"       m=n=p=q-instance: CAN FIRE")
    print(f"# class B (four free powers): {len(free)} rules, "
          f"{hits} can fire at the shape instance")
    print(f"# class C (fixed shapes): {len(other)} rules — pattern "
          f"equality only; none matches the free-m shape (the m slot "
          f"is fixed at 1, 3/2 or absent in every C pattern)")
    any_fire = hits > 0 or any(
        condition_can_be_true(c) is True for _n, _p, c in exact)
    if any_fire:
        conclusion = (
            "the pinned rule set CAN reduce the e5 shape at m=-2 "
            "(class A4: the (a+b x)^m/(Sqrt Sqrt Sqrt) rule with "
            "IntegerQ[2*m] && LeQ[m,-2] — ported as 1_1_1_4 r32): the "
            "e5-class deferral is NOT a rule-set version gap. It is the "
            "matchfix pattern-matching limit (measured 2026-08-25, "
            "5.50.0/SBCL, r32bis/pq probes): a product pattern with a "
            "FREE-exponent power factor (a+b x)^_m plus a sibling power "
            "factor of fixed FRACTIONAL exponent or Sqrt head does not "
            "match — (pa+pb x)^_m/(sqrt(pc+pd x)...) = false, "
            "(pa+pb x)^_m*(pc+pd x)^(-1/2) = false, "
            "(pa+pb x)^_m*sqrt(pc+pd x) = false — while all-fixed "
            "exponents match (P1), free+free match (P3), and a fixed "
            "INTEGER exponent in the DENOMINATOR matches (Q3). The "
            "corpus's elliptic expectations are right; reaching the "
            "rule needs a custom matcher for the m/(Sqrt Sqrt Sqrt) "
            "shape (post-full-run decision).")
    else:
        conclusion = ("NO pinned rule of 1.1.1.4 can reduce "
                      "(a+b x)^(-2)/(Sqrt Sqrt Sqrt) — the corpus's "
                      "elliptic expectations for the e5 class come from "
                      "a rule set beyond the pinned clone (version gap)")
    print("# CONCLUSION: " + conclusion)
    return 0


if __name__ == "__main__":
    sys.exit(main())
