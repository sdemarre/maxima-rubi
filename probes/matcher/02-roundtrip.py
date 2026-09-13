#!/usr/bin/env python3
"""probes/matcher/02-roundtrip.py -- per-rule round trip of every Rubi LHS
through mma4max's matcher (handoffs/2026-09-11-matcher-design.md, move 2
part B).  Driver: sh probes/matcher/02-roundtrip.run (writes
probes/matcher/02-roundtrip.out).

Subcommands:
  selftest              the verify() oracle on hand-derived spike-01 cases
  gen <cases.tsv>       write the case file read by 02-roundtrip.lisp
  judge <work> <n>      read the n shard result files, print the report

No Mathematica oracle exists on this machine, so correctness is judged by
verify(pattern, target, bindings): an independent check that the pattern,
with its variables fixed to the given bindings, matches the target under
Mathematica's pattern semantics as documented -- a Blank matches exactly one
element (under Flat Plus/Times a named Blank takes one or more elements and
binds their Plus/Times), an Optional x_. under Plus/Times may take no
element and then binds Default[Plus]=0 / Default[Times]=1, Power[b, m_.]
matches a non-Power target through b with m bound to Default[Power, 2]=1, a
non-Flat head matches head and arguments in order, repeated names bind one
value.  verify() is a checker for a given binding, not a search; the matcher
under test does the search.

Cases per rule (from the reader's evaluated LHS, see 02-mma-reader.py):
  positives  witnesses built from the LHS: every pattern variable -> a fresh
             symbol of the same name (x_ -> x; the numeric slot of
             Complex[0, fz_] -> 2), each Optional present (its symbol) or
             omitted (its default); variants: all present, all omitted, each
             Optional alone omitted, each alone present (<= 10 Optionals);
             duplicates by tree dropped.  A witness must pass verify() with
             its own bindings; one that does not is reported, not used.
  mutations  from the all-present witness: x -> z at the first / last x;
             drop the first / last non-optional argument of a Plus or Times;
             literal number v -> v+1 (-1 -> -2) at the first / last literal;
             a repeated name's last occurrence -> a different symbol.
  legs       'tree': the Mathematica-form witness is matched directly;
             'maxima': the witness is written as a Maxima expression,
             simplified by Maxima, read back by a converter (no
             simplification of its own), and matched (positives only).
Each case is run with mma4max as published ('pub') and with the spike's
mblank1 nil-guard ('guard').

Verdicts
  positive, tree leg:  OK-EXACT (bindings = witness values), OK-ALT (other
    bindings that pass verify), WRONG (matched, bindings fail verify),
    MISS (no match: a false negative), TIMEOUT / ERROR.
  positive, maxima leg: as above, and MODEL-LOST = no match on the Maxima-
    simplified tree while the tree leg matched (expression-model gap).
  mutation: NOMATCH, LEGIT (matched and verify passes -- a real match of the
    mutated tree), FALSE (matched, verify fails -- a false match).
  collapsed witness (an omitted-default variant that is not a Mathematica
    match of its own bindings): judged like a mutation, on both legs.
  Every match whose bindings fail verify() (WRONG / FALSE) is split by
  nonverified_kind(): WIDE-OK (accepted under the wider Flat reading, see
  WIDE), OVERMATCH (the LHS instantiated with the bindings evaluates to the
  target: more matches than Mathematica, mathematically right bindings),
  UNSOUND (the instantiation is not the target: wrong bindings).
"""

import importlib.util
import os
import re
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("mmareader", HERE.parents[1] / "generator" / "mma_reader.py")
rd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rd)

BLANKS = {"Blank", "BlankSequence", "BlankNullSequence"}
DEFAULT = {"Plus": 0, "Times": 1}
MAX_SINGLE_VARIANTS = 10

# modes / legs the judge scores (default: probe 02 as committed; the
# matcher regression suite sets MR_MODES=narrow,wide and MR_LEGS=tree or tree,maxima)
MODES = tuple(os.environ.get("MR_MODES", "pub,guard").split(","))
LEGS = tuple(os.environ.get("MR_LEGS", "tree,maxima").split(","))

# Mathematica head, arity -> Maxima function.  Every Maxima name was measured
# to exist (its internal operator is re-derived at run time by
# 02-roundtrip.lisp from these calls; a failure prints HEAD-FAIL).  PolyLog and
# PolyGamma are Maxima's subscripted li[n](x) / psi[n](x).  Rubi's inert
# lowercase trig functions and every other head travel as mm_<Name>(...), an
# undefined function Maxima does not simplify.
MAXIMA_FUN = {
    ("Log", 1): "log", ("Sin", 1): "sin", ("Cos", 1): "cos", ("Tan", 1): "tan",
    ("Cot", 1): "cot", ("Sec", 1): "sec", ("Csc", 1): "csc", ("Sinh", 1): "sinh",
    ("Cosh", 1): "cosh", ("Tanh", 1): "tanh", ("Coth", 1): "coth", ("Sech", 1): "sech",
    ("Csch", 1): "csch", ("ArcSin", 1): "asin", ("ArcCos", 1): "acos",
    ("ArcTan", 1): "atan", ("ArcCot", 1): "acot", ("ArcSec", 1): "asec",
    ("ArcCsc", 1): "acsc", ("ArcSinh", 1): "asinh", ("ArcCosh", 1): "acosh",
    ("ArcTanh", 1): "atanh", ("ArcCoth", 1): "acoth", ("ArcSech", 1): "asech",
    ("ArcCsch", 1): "acsch", ("Erf", 1): "erf", ("Erfc", 1): "erfc", ("Erfi", 1): "erfi",
    ("FresnelS", 1): "fresnel_s", ("FresnelC", 1): "fresnel_c",
    ("ExpIntegralEi", 1): "expintegral_ei", ("ExpIntegralE", 2): "expintegral_e",
    ("SinIntegral", 1): "expintegral_si", ("CosIntegral", 1): "expintegral_ci",
    ("SinhIntegral", 1): "expintegral_shi", ("CoshIntegral", 1): "expintegral_chi",
    ("LogIntegral", 1): "expintegral_li", ("Gamma", 1): "gamma",
    ("Gamma", 2): "gamma_incomplete", ("LogGamma", 1): "log_gamma",
    ("ProductLog", 1): "lambert_w", ("BesselJ", 2): "bessel_j", ("Zeta", 1): "zeta",
    ("Factorial", 1): "factorial", ("Abs", 1): "abs",
}
SUBSCRIPTED = {("PolyLog", 2): "li", ("PolyGamma", 2): "psi"}
# names a witness symbol must not take (Mathematica literals, a CL export that
# the Lisp reader would resolve to CL:T, Maxima keywords and constants)
RESERVED = {"E", "Pi", "I", "T", "and", "or", "not", "if", "then", "else", "elseif",
            "do", "for", "from", "step", "thru", "while", "unless", "in", "inf",
            "minf", "infinity", "und", "ind", "zeroa", "zerob", "true", "false", "done"}


class NotPosed(Exception):
    pass


# ----------------------------------------------------------------------
# canonical comparison and the verify() oracle

def cn(e):
    if isinstance(e, tuple):
        parts = [cn(a) for a in e]
        if parts[0] in ("Plus", "Times"):
            parts = [parts[0]] + sorted(parts[1:], key=repr)
        return tuple(parts)
    if isinstance(e, bool):
        raise TypeError("bool")
    if isinstance(e, Fraction):
        return e.numerator if e.denominator == 1 else e
    if isinstance(e, rd.Real):
        return float(e.text)
    if isinstance(e, rd.Str):
        return str(e)
    return e


def is_blank(e):
    return isinstance(e, tuple) and e[0] in BLANKS


def is_opt(e):
    return isinstance(e, tuple) and e[0] == "Optional"


def head_of(e):
    if isinstance(e, tuple):
        return e[0]
    if isinstance(e, bool):
        raise TypeError
    if isinstance(e, int):
        return "Integer"
    if isinstance(e, Fraction):
        return "Rational"
    if isinstance(e, float):
        return "Real"
    return "Symbol"


class Unsupported(Exception):
    pass


def blank_ok(b, e):
    if b[0] != "Blank":
        raise Unsupported("sequence blank outside a Flat head")
    return len(b) == 1 or head_of(e) == b[1]


def verify(p, e, B):
    """Pattern p matches expression e with variables fixed to B (canonical
    trees), under Mathematica semantics (module docstring)."""
    if not isinstance(p, tuple):
        return cn(p) == e
    h = p[0]
    if h == "Pattern":
        n, sub = p[1], p[2]
        if n not in B or B[n] != e:
            return False
        return blank_ok(sub, e) if is_blank(sub) else verify(sub, e, B)
    if h == "Optional":
        return verify(p[1], e, B)
    if h in BLANKS:
        return blank_ok(p, e)
    if h in DEFAULT:
        elems = list(e[1:]) if isinstance(e, tuple) and e[0] == h else [e]
        return _assign(list(p[1:]), elems, h, B)
    if h == "Power" and len(p) == 3:
        if isinstance(e, tuple) and e[0] == "Power" and len(e) == 3 and \
                verify(p[1], e[1], B) and verify(p[2], e[2], B):
            return True
        if is_opt(p[2]) and B.get(p[2][1][1]) == 1 and verify(p[1], e, B):
            return True
        return False
    if not isinstance(e, tuple) or len(e) != len(p):
        return False
    return all(verify(a, b, B) for a, b in zip(p, e))


def _remove(elems, parts):
    rest = list(elems)
    for x in parts:
        for j, y in enumerate(rest):
            if y == x:
                del rest[j]
                break
        else:
            return None
    return rest


def _assign(items, elems, h, B):
    if not items:
        return not elems
    it, rest = items[0], items[1:]
    opt = is_opt(it)
    q = it[1] if opt else it
    if isinstance(q, tuple) and q[0] == "Pattern" and is_blank(q[2]):
        n, bl = q[1], q[2]
        if bl[0] != "Blank":
            raise Unsupported("sequence blank under Flat head")
        if n not in B:
            return False
        val = B[n]
        choices = []
        if opt and val == DEFAULT[h]:
            choices.append([])
        if len(bl) > 1:
            if blank_ok(bl, val):
                choices.append([val])
        else:
            choices.append(list(val[1:]) if isinstance(val, tuple) and val[0] == h else [val])
        for c in choices:
            r = _remove(elems, c)
            if r is not None and _assign(rest, r, h, B):
                return True
        return False
    if is_blank(q):
        raise Unsupported("anonymous blank under Flat head")
    for j, el in enumerate(elems):
        if verify(q, el, B) and _assign(rest, elems[:j] + elems[j + 1:], h, B):
            return True
    # Flat: an item that becomes an h-expression once its Optional defaults
    # apply (Power[q, n_.] with n = 1 and q a Times, under Times) stands for a
    # run of the parent's elements -- Times[a, Times[b, c]] is Times[a, b, c].
    if _can_collapse_to(q, h, B) and len(elems) >= 2:
        idx = range(len(elems))
        for size in range(2, len(elems) + 1):
            for combo in combinations(idx, size):
                sub = (h,) + tuple(sorted((elems[j] for j in combo), key=repr))
                if verify(q, sub, B):
                    left = [elems[j] for j in idx if j not in combo]
                    if _assign(rest, left, h, B):
                        return True
    return False


# WIDE: the wider reading of Flat matching, used only to classify matches that
# fail verify() -- a Plus/Times item whose Optionals all take their defaults
# except one argument (Plus[g_., h_.*x_] with g = 0 is h_.*x_) may also take a
# run of the parent's elements.  Mathematica's documentation does not settle
# this case and there is no oracle here, so it is reported separately.
WIDE = False


def _can_collapse_to(q, h, B):
    if not isinstance(q, tuple):
        return False
    if q[0] == h:
        return True
    if q[0] == "Power" and len(q) == 3 and is_opt(q[2]) and B.get(q[2][1][1]) == 1:
        return _can_collapse_to(q[1], h, B)
    if WIDE and q[0] in DEFAULT and q[0] != h:
        rest = [a for a in q[1:]
                if not (is_opt(a) and isinstance(a[1], tuple) and a[1][0] == "Pattern"
                        and B.get(a[1][1]) == DEFAULT[q[0]])]
        return len(rest) == 1 and _can_collapse_to(rest[0], h, B)
    return False


def verify_case(lhs, integrand, B, wide=False):
    """lhs = evaluated Int[p, x_Symbol]; integrand a tree; B raw bindings."""
    global WIDE
    Bc = {k: cn(v) for k, v in B.items()}
    WIDE = wide
    try:
        return verify(lhs, cn(("Int", integrand, "x")), Bc)
    except Unsupported:
        return None
    finally:
        WIDE = False


def subst_bindings(p, B):
    if not isinstance(p, tuple):
        return p
    if p[0] == "Pattern":
        return B[p[1]] if p[1] in B else ("Missing", p[1])
    if p[0] == "Optional":
        return subst_bindings(p[1], B)
    return tuple(subst_bindings(a, B) for a in p)


def nonverified_kind(lhs, target, B):
    """Classify a match whose bindings fail verify():
    WIDE-OK    accepted under the wider Flat reading (WIDE, above);
    OVERMATCH  not a Mathematica match, but the LHS instantiated with the
               bindings and evaluated (reader's emulation) is the target:
               the matcher accepts more than Mathematica, with bindings that
               are mathematically right;
    UNSOUND    the instantiated LHS is not the target: wrong bindings."""
    if verify_case(lhs, target, B, wide=True):
        return "WIDE-OK"
    try:
        inst = rd.Evaluator().ev(subst_bindings(lhs[1], B))
    except Exception:
        return "UNSOUND"
    return "OVERMATCH" if cn(inst) == cn(target) else "UNSOUND"


def head_placements(p, parent=None):
    """Where pattern-variable heads F_[..] and compound heads h[..][..] sit."""
    out = set()
    if isinstance(p, tuple):
        h = p[0]
        if isinstance(h, tuple):
            kind = "F_[..]" if h[0] == "Pattern" else "compound h[..][..]"
            out.add("%s under %s" % (kind, "Plus/Times" if parent in DEFAULT else "another head"))
        hn = head_name(h)
        for a in p[1:]:
            out |= head_placements(a, hn)
    return out


# ----------------------------------------------------------------------
# witnesses

def rename(n):
    return n + "w" if n in RESERVED else n


def rename_pattern(p):
    """Rename pattern variables whose names collide (RESERVED)."""
    if not isinstance(p, tuple):
        return p
    if p[0] == "Pattern":
        return ("Pattern", rename(p[1]), rename_pattern(p[2]))
    return tuple(rename_pattern(a) for a in p)


def default_for(parent, pos):
    if parent in DEFAULT:
        return DEFAULT[parent]
    if parent == "Power" and pos == 2:
        return 1
    return None


def head_name(h):
    while isinstance(h, tuple):
        h = h[0]
    return h


class Builder:
    def __init__(self, xname, omit=(), override=None):
        self.xname, self.omit = xname, set(omit)
        self.override = override or {}
        self.B = {}
        self.opt_i = 0
        self.occ = Counter()
        self.n_opts = 0

    def value_for(self, n, sub, parent):
        if n == self.xname:
            return "x"
        if parent == "Complex":
            return 2
        if len(sub) > 1:
            return {"Integer": 3, "Rational": Fraction(1, 3)}.get(sub[1], n)
        return n

    def bind(self, n, v):
        if n in self.B:
            return self.B[n]
        self.B[n] = v
        return v

    def build(self, p, parent=None, pos=None):
        if not isinstance(p, tuple):
            return p
        h = p[0]
        if h == "Optional":
            i = self.opt_i
            self.opt_i += 1
            inner = p[1]
            if i in self.omit:
                d = default_for(parent, pos)
                if d is not None:
                    self.occ[inner[1]] += 1
                    return self.bind(inner[1], d)
            return self.build(inner, parent, pos)
        if h == "Pattern":
            n, sub = p[1], p[2]
            occ = self.occ[n]
            self.occ[n] += 1
            if (n, occ) in self.override:
                return self.override[(n, occ)]
            if is_blank(sub):
                return self.bind(n, self.value_for(n, sub, parent))
            return self.bind(n, self.build(sub, parent, pos))
        head = self.build(h, "<head>", 0) if isinstance(h, tuple) else h
        hn = head_name(h)
        return (head,) + tuple(self.build(a, hn, i) for i, a in enumerate(p[1:], 1))


def count_optionals(p):
    if not isinstance(p, tuple):
        return 0
    return (p[0] == "Optional") + sum(count_optionals(a) for a in p)


def name_occurrences(p, acc=None):
    acc = Counter() if acc is None else acc
    if isinstance(p, tuple):
        if p[0] == "Pattern":
            acc[p[1]] += 1
        for a in p:
            name_occurrences(a, acc)
    return acc


def flat_drop_sites(p, path=()):
    """(path to a Plus/Times node, argument index) of non-optional arguments."""
    out = []
    if isinstance(p, tuple):
        if p[0] in DEFAULT and len(p) >= 3:
            for i, a in enumerate(p[1:], 1):
                if not is_opt(a):
                    out.append((path, i))
        for i, a in enumerate(p):
            out.extend(flat_drop_sites(a, path + (i,)))
    return out


def literal_sites(p, path=(), parent=None):
    out = []
    if isinstance(p, tuple):
        if p[0] in ("Pattern", "Optional", "Complex"):
            return out
        for i, a in enumerate(p):
            if i and isinstance(a, (int, Fraction)) and not isinstance(a, bool):
                out.append(path + (i,))
            out.extend(literal_sites(a, path + (i,), p[0]))
    return out


def edit(p, path, fn):
    if not path:
        return fn(p)
    i = path[0]
    return p[:i] + (edit(p[i], path[1:], fn),) + p[i + 1:]


def evaluate(t):
    return rd.Evaluator().ev(t)


def to_maxima(t):
    if isinstance(t, bool):
        raise TypeError
    if isinstance(t, int):
        return "(%d)" % t if t < 0 else str(t)
    if isinstance(t, Fraction):
        return "(%d/%d)" % (t.numerator, t.denominator)
    if isinstance(t, rd.Real):
        return t.text + "0" if t.text.endswith(".") else t.text
    if isinstance(t, str):
        return {"E": "%e", "Pi": "%pi", "I": "%i"}.get(t, t)
    h, args = t[0], t[1:]
    if isinstance(h, tuple):
        raise NotPosed("compound head")
    if h == "Complex" and all(isinstance(a, (int, Fraction)) for a in args):
        return "(%s+%s*%%i)" % (to_maxima(args[0]), to_maxima(args[1]))
    if h == "Plus":
        return "(" + "+".join(to_maxima(a) for a in args) + ")"
    if h == "Times":
        return "(" + "*".join(to_maxima(a) for a in args) + ")"
    if h == "Power":
        return "(%s)^(%s)" % (to_maxima(args[0]), to_maxima(args[1]))
    if (h, len(args)) in SUBSCRIPTED:
        return "%s[%s](%s)" % (SUBSCRIPTED[(h, len(args))], to_maxima(args[0]), to_maxima(args[1]))
    name = MAXIMA_FUN.get((h, len(args)), "mm_" + h)
    return "%s(%s)" % (name, ",".join(to_maxima(a) for a in args))


def rule_cases(r):
    """-> (lhs, xname, positives, mutations, notes); positives =
    [(variant, tree, bindings, witness_valid, maxima_string)],
    mutations = [(variant, tree)]."""
    lhs, _eff = rd.evaluate_lhs(r.lhs)
    lhs = rename_pattern(lhs)
    p1, xp = lhs[1], lhs[2]
    xname = xp[1] if isinstance(xp, tuple) and xp[0] == "Pattern" else "x"
    notes = []
    k = count_optionals(p1)
    variants = [("all-present", ())]
    if k:
        variants.append(("all-omitted", tuple(range(k))))
        for i in range(k):
            variants.append(("omit-%d" % i, (i,)))
        if k <= MAX_SINGLE_VARIANTS:
            for i in range(k):
                variants.append(("only-%d" % i, tuple(j for j in range(k) if j != i)))
    seen = set()
    positives = []
    for name, omit in variants:
        b = Builder(xname, omit)
        t = evaluate(b.build(p1))
        c = cn(t)
        if c in seen:
            continue
        seen.add(c)
        B = dict(b.B)
        B[xname] = "x"
        valid = verify_case(lhs, t, B)
        try:
            ms = to_maxima(t)
        except NotPosed:
            ms = ""
        positives.append((name, t, B, valid, ms))
    muts = []
    occ = name_occurrences(p1)
    nx = occ.get(xname, 0)
    for label, o in (("xz-first", 0), ("xz-last", nx - 1)):
        if nx and (label == "xz-first" or nx > 1):
            muts.append((label, Builder(xname, override={(xname, o): "z"}).build(p1)))
    sites = flat_drop_sites(p1)
    for label, s in (("drop-first", sites[:1]), ("drop-last", sites[1:][-1:])):
        for path, i in s:
            muts.append((label, Builder(xname).build(edit(p1, path, lambda n: n[:i] + n[i + 1:]))))
    lits = literal_sites(p1)
    for label, s in (("lit-first", lits[:1]), ("lit-last", lits[1:][-1:])):
        for path in s:
            def bump(v):
                return -2 if v == -1 else v + 1
            muts.append((label, Builder(xname).build(edit(p1, path, bump))))
    reps = [n for n, c in occ.items() if c > 1 and n != xname]
    for n in sorted(reps)[:2]:
        muts.append(("rep-%s" % n, Builder(xname, override={(n, occ[n] - 1): n + "zz"}).build(p1)))
    mutations = []
    for label, t in muts:
        t = evaluate(t)
        if cn(t) in seen:
            notes.append("mutation %s equals a positive witness; dropped" % label)
            continue
        mutations.append((label, t))
    return lhs, xname, positives, mutations, notes


# ----------------------------------------------------------------------

def cmd_gen(path):
    rules, _counts = rd.load_rules()
    ok = [r for r in rules if not r.error]
    names = set()
    stats = Counter()
    with open(path, "w") as f:
        for (h, n), m in sorted(MAXIMA_FUN.items()):
            f.write("H\t%s\t%s(%s)\n" % (h, m, ",".join("q%d" % i for i in range(n))))
        for r in ok:
            lhs, xname, pos, muts, notes = rule_cases(r)
            names.update(name_occurrences(lhs))
            f.write("P\t%s\t%s\n" % (r.id, rd.to_sexp(lhs)))
            for v, t, _B, valid, ms in pos:
                stats["positive"] += 1
                stats["witness-collapsed" if valid is False else
                      "witness-unverifiable" if valid is None else "witness-valid"] += 1
                if not ms:
                    stats["maxima-leg-not-posed"] += 1
                f.write("C\t%s\t%s\t%s\t%s\n" % (r.id, v, rd.to_sexp(t), ms))
            for v, t in muts:
                stats["mutation"] += 1
                f.write("C\t%s\tmut-%s\t%s\t\n" % (r.id, v, rd.to_sexp(t)))
            stats["notes"] += len(notes)
    print("rules %d; %s" % (len(ok), dict(stats)))
    print("pattern variable names renamed (RESERVED): %s" % sorted(n for n in names if n.endswith("w") and n[:-1] in RESERVED))


# ----------------------------------------------------------------------
# judge

_TOK = re.compile(r'#C\(|\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')


def parse_sexp(s):
    toks = _TOK.findall(s)
    pos = [0]

    def atom(t):
        if re.fullmatch(r"-?\d+", t):
            return int(t)
        if re.fullmatch(r"-?\d+/\d+", t):
            a, b = t.split("/")
            return Fraction(int(a), int(b))
        if re.fullmatch(r"-?\d*\.\d+([edEDfFsS][-+]?\d+)?", t):
            return float(re.sub(r"[dDfFsS]", "e", t))
        if t.startswith('"'):
            return rd.Str(t[1:-1])
        return t

    def item():
        t = toks[pos[0]]
        pos[0] += 1
        if t == "(" or t == "#C(":
            out = []
            while toks[pos[0]] != ")":
                out.append(item())
            pos[0] += 1
            if t == "#C(":
                return ("Complex",) + tuple(out)
            return tuple(out)
        return atom(t)
    return item() if toks else ()


def pct(n, d):
    return "%.2f%%" % (100.0 * n / d) if d else "-"


def quant(v, q):
    if not v:
        return 0.0
    v = sorted(v)
    return v[min(len(v) - 1, int(q * len(v)))]


def cmd_judge(work, nshards):
    work = Path(work)
    rules, _c = rd.load_rules()
    ok = [r for r in rules if not r.error]
    cases = {}
    for r in ok:
        lhs, xname, pos, muts, notes = rule_cases(r)
        cases[r.id] = (r, lhs, {v: (t, B, valid, ms) for v, t, B, valid, ms in pos},
                       {"mut-" + v: t for v, t in muts})
    results = defaultdict(dict)   # (id, variant, leg, mode) -> fields
    prep = {}
    done = 0
    for i in range(nshards):
        f = work / ("shard%d.tsv" % i)
        if not f.exists():
            print("SHARD %d MISSING" % i)
            continue
        for line in f.read_text().split("\n"):
            parts = line.split("\t")
            if parts[0] == "DONE":
                done += 1
            elif parts[0] == "PREP":
                prep[(parts[1], parts[2])] = (parts[3], float(parts[4]) if parts[4] else None)
            elif parts[0] == "R":
                _, rid, var, leg, mode, status, matched, ms, binds, conv = (parts + [""] * 10)[:10]
                results[(rid, var, leg, mode)] = (status, matched, float(ms) if ms else None, binds, conv)
    print("=== probes/matcher/02-roundtrip  (judge)")
    log0 = work / "shard0.log"
    if log0.exists():
        m = re.search(r'%build_info\("([^"]*)","([^"]*)".*?"SBCL","([^"]*)"', log0.read_text(), re.S)
        if m:
            print("Maxima %s (build %s), SBCL %s -- build_info() in shard0.log" % m.groups())
    gen_log = work / "gen.log"
    if gen_log.exists():
        print("gen: " + gen_log.read_text().strip().replace("\n", "\ngen: "))
    print("shards finished: %d/%d" % (done, nshards))

    # completeness
    missing = []
    for rid, (r, lhs, pos, muts) in cases.items():
        for mode in MODES:
            if (rid, mode) not in prep:
                missing.append("%s PREP %s" % (rid, mode))
                continue
            if prep[(rid, mode)][0] != "ok":
                continue
            for v, (t, B, valid, ms) in pos.items():
                if (rid, v, "tree", mode) not in results:
                    missing.append("%s %s tree %s" % (rid, v, mode))
                if ms and "maxima" in LEGS and (rid, v, "maxima", mode) not in results:
                    missing.append("%s %s maxima %s" % (rid, v, mode))
            for v in muts:
                if (rid, v, "tree", mode) not in results:
                    missing.append("%s %s tree %s" % (rid, v, mode))
    print("completeness: rules %d; missing result lines %d%s" % (
        len(cases), len(missing), (" e.g. " + "; ".join(missing[:5])) if missing else ""))
    prep_fail = [(k, v) for k, v in prep.items() if v[0] != "ok"]
    print("pattern preparation (fixopts+bindfix) failures: %d %s" % (len(prep_fail), prep_fail[:10]))
    pms = [v[1] for (rid, mode), v in prep.items() if mode == "pub" and v[1] is not None]
    print("pattern preparation time, pub pass: total %.1f ms over %d rules; p50 %.3f p99 %.3f max %.3f ms" % (
        sum(pms), len(pms), quant(pms, .5), quant(pms, .99), max(pms) if pms else 0))

    census_spec = importlib.util.spec_from_file_location("census", HERE / "02-construct-census.py")
    census = importlib.util.module_from_spec(census_spec)
    census_spec.loader.exec_module(census)
    census.rd = rd  # one reader module: its atom classes (Real, Str) must be shared

    def labels(lhs):
        w = census.Walk(lhs[2][1] if isinstance(lhs[2], tuple) else "x")
        w.walk(lhs[1], parent="Int", pos=1)
        w.finish()
        return {l for l in w.labels if not l.startswith("literal integer") and
                not l.startswith("literal rational")}

    wit = Counter((v.split("-")[0] if v != "all-present" else v, valid)
                  for rid, (r, lhs, pos, muts) in cases.items() for v, (t, B, valid, ms) in pos.items())
    print("positive witnesses by variant kind and verify() with their own bindings "
          "(False = collapsed, judged like mutations; None = unverifiable): %s" %
          dict(sorted(wit.items(), key=str)))

    for mode in MODES:
        print()
        print("=" * 72)
        print("MODE %s (%s)" % (mode, "mma4max as published" if mode == "pub" else "with the spike's mblank1 nil-guard"))
        verdicts = Counter()
        rule_bad = defaultdict(list)
        times = []
        slow = []
        mverd = Counter()
        model_rules = defaultdict(list)
        model_kinds = Counter()
        model_kind_rules = defaultdict(set)
        changed = 0
        change_kinds = Counter()
        change_examples = {}
        neg = Counter()
        neg_false = defaultdict(list)
        neg_legit = []
        collapsed = Counter()
        collapsed_false = defaultdict(list)
        unsound = defaultdict(list)
        rule_miss = set()
        not_run = 0
        for rid, (r, lhs, pos, muts) in cases.items():
            if (rid, mode) not in prep:
                not_run += 1
                continue
            if prep[(rid, mode)][0] != "ok":
                verdicts["PREP-FAIL"] += 1
                rule_bad[rid].append("prep")
                continue
            tree_ok = {}
            for v, (t, B, valid, ms) in pos.items():
                res = results.get((rid, v, "tree", mode))
                if res is None:
                    continue
                status, matched, tms, binds, _conv = res
                if tms is not None:
                    times.append(tms)
                    slow.append((tms, rid, v))
                if valid is False:
                    # collapsed witness: not a Mathematica match of its own
                    # bindings; judged like a mutation, on both legs
                    for leg in ("tree", "maxima"):
                        res2 = results.get((rid, v, leg, mode))
                        if res2 is None or res2[0] == "maxerror":
                            continue
                        st2, m2, _t2, b2, conv2 = res2
                        target = parse_sexp(conv2) if leg == "maxima" and conv2 else t
                        if st2 != "ok":
                            collapsed[(leg, st2.upper())] += 1
                        elif m2 != "T":
                            collapsed[(leg, "NOMATCH")] += 1
                        else:
                            bm2 = dict(parse_bindings(b2))
                            okb = verify_case(lhs, target, bm2)
                            k = "LEGIT" if okb else "UNVERIFIABLE" if okb is None else \
                                "FALSE/" + nonverified_kind(lhs, target, bm2)
                            collapsed[(leg, k)] += 1
                            if k.startswith("FALSE"):
                                collapsed_false[rid].append("%s/%s:%s" % (v, leg, k[6:]))
                            if k == "FALSE/UNSOUND":
                                unsound[rid].append("%s/%s" % (v, leg))
                    continue
                vd = judge_one(lhs, t, B, valid, status, matched, binds)
                verdicts[vd] += 1
                if vd == "MISS":
                    rule_miss.add(rid)
                if vd == "WRONG/UNSOUND":
                    unsound[rid].append("%s/tree" % v)
                tree_ok[v] = vd.startswith("OK")
                if not vd.startswith("OK") and vd != "SKIP-INVALID-WITNESS":
                    rule_bad[rid].append("%s:%s" % (v, vd))
                if not ms:
                    continue
                res = results.get((rid, v, "maxima", mode))
                if res is None:
                    continue
                status, matched, tms, binds, conv = res
                if status == "maxerror":
                    mverd["MAXIMA-ERROR"] += 1
                    continue
                ct = parse_sexp(conv) if conv else None
                if ct is not None and cn(ct) != cn(t):
                    changed += 1
                    kind = change_kind(t, ct)
                    change_kinds[kind] += 1
                    change_examples.setdefault(kind, "%s %s: %s -> %s" % (
                        rid, v, rd.fullform(t)[:80], rd.fullform(ct)[:80]))
                if status != "ok":
                    mverd[status.upper()] += 1
                    continue
                if matched == "T":
                    bm = dict(parse_bindings(binds))
                    okb = verify_case(lhs, ct, bm)
                    if okb:
                        mverd["OK"] += 1
                    elif okb is None:
                        mverd["UNVERIFIABLE"] += 1
                    else:
                        k = "WRONG/" + nonverified_kind(lhs, ct, bm)
                        mverd[k] += 1
                        if k == "WRONG/UNSOUND":
                            unsound[rid].append("%s/maxima" % v)
                else:
                    if tree_ok.get(v):
                        mverd["MODEL-LOST"] += 1
                        model_rules[rid].append(v)
                        mk = change_kind(t, ct) if ct is not None and cn(ct) != cn(t) else "unchanged tree"
                        model_kinds[mk] += 1
                        model_kind_rules[mk].add(rid)
                    else:
                        mverd["MISS-BOTH-LEGS"] += 1
            for v, t in muts.items():
                res = results.get((rid, v, "tree", mode))
                if res is None:
                    continue
                status, matched, tms, binds, _conv = res
                if status != "ok":
                    neg[status.upper()] += 1
                    continue
                if matched != "T":
                    neg["NOMATCH"] += 1
                    continue
                bm = dict(parse_bindings(binds))
                okb = verify_case(lhs, t, bm)
                if okb:
                    neg["LEGIT"] += 1
                    neg_legit.append("%s %s" % (rid, v))
                elif okb is False:
                    k = nonverified_kind(lhs, t, bm)
                    neg["FALSE/" + k] += 1
                    neg_false[rid].append("%s:%s" % (v, k))
                    if k == "UNSOUND":
                        unsound[rid].append("%s/tree" % v)
                else:
                    neg["UNVERIFIABLE"] += 1
        npos = sum(verdicts.values())
        if not_run:
            print("NOT RUN %s: %d rules have no result (limited or incomplete run)" % (mode, not_run))
        print("SUMMARY %s positives (tree leg): %d -- %s" % (mode, npos, ", ".join(
            "%s %d (%s)" % (k, c, pct(c, npos)) for k, c in verdicts.most_common())))
        nrules = len(cases) - not_run
        print("SUMMARY %s rules with every positive OK (tree leg): %d/%d (%s)" % (
            mode, nrules - len(rule_bad), nrules, pct(nrules - len(rule_bad), nrules)))
        nneg = sum(neg.values())
        print("SUMMARY %s mutations: %d -- %s; rules with a FALSE match: %d" % (
            mode, nneg, ", ".join("%s %d" % kv for kv in neg.most_common()), len(neg_false)))
        print("SUMMARY %s collapsed witnesses (omitted defaults collapse the integrand out of the LHS's "
              "Mathematica coverage; judged like mutations): %s; rules with a FALSE match: %d" % (
                  mode, ", ".join("%s/%s %d" % (leg, k, c) for (leg, k), c in sorted(collapsed.items())),
                  len(collapsed_false)))
        print("COLLAPSEDFALSE %s (%d): %s" % (mode, len(collapsed_false), "; ".join(
            "%s [%s]" % (rid, ",".join(vs[:4])) for rid, vs in sorted(collapsed_false.items(), key=lambda kv: rule_order(kv[0], cases)))))
        nm = sum(mverd.values())
        print("SUMMARY %s maxima leg: %d -- %s; witnesses changed by Maxima: %d; rules with MODEL-LOST: %d" % (
            mode, nm, ", ".join("%s %d" % kv for kv in mverd.most_common()), changed, len(model_rules)))
        print("TIMING %s tree-leg single match (ms): p50 %.4f p90 %.4f p99 %.4f max %.3f; >50 ms: %d" % (
            mode, quant(times, .5), quant(times, .9), quant(times, .99), max(times) if times else 0,
            sum(1 for x in times if x > 50)))
        print("TIMING %s slowest: %s" % (mode, "; ".join("%s %s %.1f ms" % (rid, v, ms)
                                                      for ms, rid, v in sorted(slow, reverse=True)[:8])))
        # attribution of failing rules to constructs
        lab_all, lab_bad = Counter(), Counter()
        for rid, (r, lhs, pos, muts) in cases.items():
            ls = labels(lhs)
            lab_all.update(ls)
            if rid in rule_bad:
                lab_bad.update(ls)
        print("positive failures by LHS construct (#failing rules carrying it / #rules carrying it):")
        for l, c in sorted(lab_bad.items(), key=lambda kv: -kv[1] / lab_all[kv[0]]):
            print("  %s: %d/%d (%s)" % (l, c, lab_all[l], pct(c, lab_all[l])))
        bad_kinds = Counter()
        for rid, vs in rule_bad.items():
            for x in vs:
                bad_kinds[x.split(":")[-1]] += 1
        print("failing positive verdict kinds: %s" % dict(bad_kinds))
        place_all, place_miss = Counter(), Counter()
        for rid, (r, lhs, pos, muts) in cases.items():
            for pl in head_placements(lhs[1]):
                place_all[pl] += 1
                if rid in rule_miss:
                    place_miss[pl] += 1
        print("MISS by head placement %s (#rules with a MISS / #rules with that placement): %s" % (
            mode, ", ".join("%s %d/%d" % (pl, place_miss[pl], place_all[pl]) for pl in sorted(place_all))))
        print("MISS %s rules with a MISS: %d; carrying no pattern-variable or compound head: %d; "
              "carrying one directly under Plus/Times: %d" % (
                  mode, len(rule_miss),
                  sum(1 for rid in rule_miss if not head_placements(cases[rid][1][1])),
                  sum(1 for rid in rule_miss
                      if any(pl.endswith("under Plus/Times") for pl in head_placements(cases[rid][1][1])))))
        print("MODEL-LOST %s by Maxima rewrite kind (variants/rules): %s" % (mode, ", ".join(
            "[%s] %d/%d" % (k, c, len(model_kind_rules[k])) for k, c in model_kinds.most_common())))
        print("UNSOUNDRULES %s (%d): %s" % (mode, len(unsound), "; ".join(
            "%s [%s]" % (rid, ",".join(vs[:4])) for rid, vs in sorted(unsound.items(), key=lambda kv: rule_order(kv[0], cases)))))
        print("FAILRULES %s (%d): %s" % (mode, len(rule_bad), "; ".join(
            "%s [%s]" % (rid, ",".join(vs[:4]) + (",..." if len(vs) > 4 else ""))
            for rid, vs in sorted(rule_bad.items(), key=lambda kv: rule_order(kv[0], cases)))))
        print("FALSERULES %s (%d): %s" % (mode, len(neg_false), "; ".join(
            "%s [%s]" % (rid, ",".join(vs)) for rid, vs in sorted(neg_false.items(), key=lambda kv: rule_order(kv[0], cases)))))
        print("LEGIT mutation matches %s (%d): %s" % (mode, len(neg_legit), "; ".join(neg_legit[:40]) +
                                                     (" ..." if len(neg_legit) > 40 else "")))
        print("Maxima rewrite kinds %s (witness variants): %s" % (mode, dict(change_kinds.most_common())))
        for kind, ex in change_examples.items():
            print("  e.g. [%s] %s" % (kind, ex))
        print("MODELRULES %s (%d): %s" % (mode, len(model_rules), "; ".join(
            "%s [%s]" % (rid, ",".join(vs[:3])) for rid, vs in sorted(model_rules.items(), key=lambda kv: rule_order(kv[0], cases)))))


def rule_order(rid, cases):
    return list(cases).index(rid) if rid in cases else 1 << 30


def parse_bindings(s):
    t = parse_sexp(s) if s else ()
    return [(str(b[0]), b[1]) for b in t]


def judge_one(lhs, t, B, valid, status, matched, binds):
    if valid is not True:
        return "SKIP-INVALID-WITNESS"
    if status != "ok":
        return status.upper()
    if matched != "T":
        return "MISS"
    bm = dict(parse_bindings(binds))
    okb = verify_case(lhs, t, bm)
    if okb is None:
        return "UNVERIFIABLE"
    if not okb:
        return "WRONG/" + nonverified_kind(lhs, t, bm)
    exact = all(n in bm and cn(bm[n]) == cn(v) for n, v in B.items())
    return "OK-EXACT" if exact else "OK-ALT"


def heads_in(t, acc=None):
    acc = set() if acc is None else acc
    if isinstance(t, tuple):
        acc.add(head_name(t[0]) if not isinstance(t[0], tuple) else "<compound>")
        for a in t[1:]:
            heads_in(a, acc)
    return acc


def change_kind(t, ct):
    new = heads_in(ct) - heads_in(t)
    gone = heads_in(t) - heads_in(ct)
    parts = []
    if new:
        parts.append("+" + "+".join(sorted(new)))
    if gone:
        parts.append("-" + "-".join(sorted(gone)))
    return " ".join(parts) or "same heads, different structure"


# ----------------------------------------------------------------------

def cmd_selftest():
    def pat(s):
        return rd.evaluate_lhs(rd.parse(s))[0]

    def tgt(s):
        return rd.evaluate_lhs(rd.parse(s))[0]

    def B(s):
        out = {"x": "x"}
        for tok in s.split():
            k, v = tok.split("=", 1)
            out[k] = tgt(v)
        return out

    L7 = "Int[(a_. + b_.*x_)^m_, x_Symbol]"
    cases = [
        ("G1-04t", L7, "(2*x)^m", "a=0 b=2 m=m", True),
        ("G1-06", L7, "x^3", "a=0 b=1 m=3", True),
        ("G3-01", "Int[x_^m_., x_Symbol]", "x", "m=1", True),
        ("N-15", "Int[(a_ + b_.*x_)^m_.*(c_ + d_.*x_), x_Symbol]", "x^m*(c+d*x)",
         "a=0 b=1 m=m c=c d=d", False),
        ("N-07", "Int[(d_ + e_.*x_^r_.)^q_.*(a_. + b_.*Log[c_.*x_^n_.]), x_Symbol]",
         "x^5*(a+b*Log[c*x^n])", "d=0 e=1 r=1 q=5 a=a b=b c=c n=n", False),
        ("N-14", "Int[(f_*x_)^m_*(a_. + b_.*Log[c_.*(d_ + e_.*x_^n_)^p_.])^q_., x_Symbol]",
         "x^m*Log[c*(d+e*x^n)^p]", "f=1 m=m a=0 b=1 c=c d=d e=e n=n p=p q=1", False),
        ("C-02", "Int[a_.*b_.*x_^m_, x_Symbol]", "x^3", "a=1 b=1 m=3", True),
        ("G3-05", "Int[x_^m_.*(d_ + e_.*x_^r_.)^q_.*(a_. + b_.*Log[c_.*x_^n_.]), x_Symbol]",
         "x^5*(d+e*x^2)*(a+b*Log[c*x^n])", "m=5 d=d e=e r=2 q=1 a=a b=b c=c n=n", True),
        ("G6-01", "Int[(f_. + g_.*x_)^m_.*(A_. + B_.*Log[e_.*((a_. + b_.*x_)/(c_. + d_.*x_))^n_.])^p_., x_Symbol]",
         "(A+B*Log[e*(a+b*x)/(c+d*x)])/(a*g+b*g*x)^2",
         "f=a*g g=b*g m=-2 A=A B=B e=e a=a b=b c=c d=d n=1 p=1", True),
        ("G1-08", "Int[(c_. + d_.*x_)^m_.*F_^(g_.*(e_. + f_.*x_)), x_Symbol]", "x*E^(2*x)",
         "c=0 d=1 m=1 F=E g=2 e=0 f=1", True),
        ("wrong-coef", L7, "(3+2*x)^4", "a=3 b=3 m=4", False),
        ("x-mismatch", "Int[x_^m_., x_Symbol]", "z^3", "m=3", False),
        ("sum-absorb", "Int[(a_. + b_.*x_ + c_.*x_^2)^p_, x_Symbol]", "(1+2*x+3*x^2+z1+z2)^(1/2)",
         "a=1+z1+z2 b=2 c=3 p=1/2", True),
    ]
    bad = 0
    for cid, p, t, b, want in cases:
        got = verify(pat(p), cn(("Int", tgt(t), "x")), {k: cn(v) for k, v in B(b).items()})
        ok = got == want
        bad += not ok
        print("%s verify %s -> %s (want %s)" % ("PASS:" if ok else "FAIL:", cid, got, want))
    # witness construction self-consistency: an all-present witness (no
    # default applied, so nothing collapses) must verify with its own
    # bindings for every rule; variants with omitted Optionals may collapse
    # into integrands the LHS does not cover in Mathematica (counted only)
    rules, _ = rd.load_rules()
    ok_rules = [r for r in rules if not r.error]
    present_bad, kinds = [], Counter()
    for r in ok_rules:
        _l, _x, pos, _m, _n = rule_cases(r)
        for v, t, Bw, valid, ms in pos:
            kinds[(v.split("-")[0] if v != "all-present" else v, valid)] += 1
            if v == "all-present" and valid is not True:
                present_bad.append(r.id)
    ok = not present_bad
    bad += not ok
    print("%s all-present witnesses verify with their own bindings: %d rules, failures %d %s" % (
        "PASS:" if ok else "FAIL:", len(ok_rules), len(present_bad), present_bad[:10]))
    print("      witness validity by variant kind (kind, valid): %s" % dict(sorted(kinds.items(), key=str)))
    print("Results: %d passed, %d failed" % (len(cases) + 1 - bad, bad))
    return bad


def rename_syms(t):
    """Double every witness symbol name (heads, x, E, Pi, I kept)."""
    if isinstance(t, tuple):
        return tuple((rename_syms(a) if isinstance(a, tuple) else a) if i == 0 else rename_syms(a)
                     for i, a in enumerate(t))
    if isinstance(t, str) and not isinstance(t, rd.Str) and t not in ("x", "E", "Pi", "I"):
        return t + t
    return t


def cmd_controls():
    """Emit the data file for 02-controls.lisp (Lisp source on stdout)."""
    rules, _ = rd.load_rules()
    byid = {r.id: r for r in rules}

    def ev(s):
        return rd.evaluate_lhs(rd.parse(s))[0]

    def esc(s):
        return s.replace("\\", "\\\\").replace('"', '\\"')
    rows = []
    lhs, _x, pos, _m, _n = rule_cases(byid["4.1.12.m L82"])
    t = {v: w for v, w, _B, _valid, _ms in pos}["only-1"]
    rows.append(("U1", "4.1.12.m L82 only-1 witness (collapsed; tree leg)", lhs, t,
                 "02-roundtrip (guard): bindings e=Sin[u] u=e, which fail verify() and do not reproduce the target"))
    rows.append(("U1r", "U1, every witness symbol renamed", lhs, rename_syms(t),
                 "name-collision control: an artifact of symbol names would change the result"))
    lhs2 = rule_cases(byid["6.5.11.m L10"])[0]
    t2 = ev("b^p*Sech[u]^p")
    rows.append(("U2", "6.5.11.m L10 omit-0 witness after Maxima: (b*sech(u))^p -> b^p*sech(u)^p", lhs2, t2,
                 "02-roundtrip (guard): bindings u=Sech[u]^p b=b^p p=1, which do not reproduce the target"))
    rows.append(("U2r", "U2, every witness symbol renamed", lhs2, rename_syms(t2), "name-collision control"))
    for hid, p, target, note in (
            ("H1", "Int[F_[x_], x_Symbol]", "F[x]", "Mathematica: F=F (pattern head, non-Flat parent)"),
            ("H2", "Int[u_*F_[x_], x_Symbol]", "u*F[x]", "Mathematica: u=u F=F (pattern head under Times)"),
            ("H3", "Int[u_*Sin[x_], x_Symbol]", "u*Sin[x]", "Mathematica: u=u (fixed head under Times: control)"),
            ("H4", "Int[u_+F_[x_], x_Symbol]", "u+F[x]", "Mathematica: u=u F=F (pattern head under Plus)"),
            ("H5", "Int[F_[x_]^m_, x_Symbol]", "F[x]^m", "Mathematica: F=F m=m (pattern head under Power)"),
            ("H6", "Int[u_*F_[x_]^m_, x_Symbol]", "u*F[x]^m", "Mathematica: u=u F=F m=m (under Power under Times)"),
            ("H7", "Int[Derivative[n_][f_][x_], x_Symbol]", "Derivative[2][f][x]", "Mathematica: n=2 f=f (compound head, non-Flat parent)"),
            ("H8", "Int[u_*Derivative[n_][f_][x_], x_Symbol]", "u*Derivative[2][f][x]", "Mathematica: u=u n=2 f=f (compound head under Times)")):
        rows.append((hid, p, ev(p), ev(target), note))
    print(";;; generated by: python3 probes/matcher/02-roundtrip.py controls")
    print("(in-package :cl-user)")
    print("(defparameter *controls* '(")
    for cid, label, p, t, note in rows:
        print('  ("%s" "%s" "%s" "%s" "%s")' % (cid, esc(label), rd.to_sexp(p), rd.to_sexp(t), esc(note)))
    print("))")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "selftest":
        sys.exit(1 if cmd_selftest() else 0)
    elif cmd == "controls":
        cmd_controls()
    elif cmd == "gen":
        cmd_gen(sys.argv[2])
    elif cmd == "judge":
        cmd_judge(sys.argv[2], int(sys.argv[3]))
    else:
        raise SystemExit("usage: selftest | gen <cases.tsv> | judge <work> <nshards>")
