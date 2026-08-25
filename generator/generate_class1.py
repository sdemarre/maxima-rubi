#!/usr/bin/env python3
"""generate_class1.py — emit rules/class1/*.mac from Rubi 4's class-1 .m files.

Only the files Rubi.m actually LoadRules() (67 files, 2,710 rules — the T1
count; 22 stale on-disk files are skipped by construction). Usage:
    python3 generator/generate_class1.py [--only 1.1.1.1]
Fails loudly (exit 1, file+rule+token named) on an unlisted token, an
unparseable rule run, or a pattern variable it cannot rename. A full run
also prints the ordered maxima_rubi.mac load list (the one to paste).
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUBI = ROOT / "reference" / "rubi"
OUT = ROOT / "rules" / "class1"
PIN = "61e9c18ea248061cd83c67882f7c91a73cef912d"

# reuse the census parser verbatim (T4 §4 step 1)
def _load(name, rel):
    p = ROOT / "probes" / rel
    spec = importlib.util.spec_from_file_location(name, p)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

_inv = _load("inv01", "probe-rubi-anatomy/01-inventory.py")
_cen = _load("cen01", "translation/01-class1-syntax-census.py")
strip_comments, parse_load_rules = _inv.strip_comments, _inv.parse_load_rules
rule_runs = _cen.rule_runs

sys.path.insert(0, str(Path(__file__).resolve().parent))
# FIX F8/F9: the brief's `from translation_table import translate` is
# shadowed by this module's own recursive translate() below (and
# RENAME/RESTRUCTURE were never imported at all), so translate_token's
# table lookup would NameError/TypeError. Import under an alias.
from translation_table import translate as table_translate
from translation_table import RENAME, RESTRUCTURE

class GenError(SystemExit):
    def __init__(self, msg):
        print(f"generate_class1: {msg}", file=sys.stderr)
        super().__init__(1)

MIT = ("/* Ported from Rule-Based Integration (Rubi), "
       "https://github.com/RuleBasedIntegration/Rubi\n"
       " * Copyright (c) 2018 Rule-Based-Integration Organization (MIT). */")

def key_of(rel_m):
    # "1 Algebraic functions/.../1.1.1.1 (a+b x)^m.m" -> "1_1_1_1"
    base = rel_m.split("/")[-1]
    num = base.split(" ")[0]
    return num.replace(".", "_")

def cap_name(key, n, v):
    """The pattern-variable name for capture v of rule n of file key:
    `_mr_<key>_r<n>_v` (the brief's naming; pattern-variable status comes
    from matchdeclare, not from the leading underscore). cap_remap is
    applied before the name is built (see CAP_REMAP).
    """
    remap = CAP_REMAP.get((key, n), {})
    return f"_mr_{key}_r{n}_{remap.get(v, v)}"

# Maxima's matchfix binds commutatively-similar pattern factors by
# VARIABLE-NAME order, not by the .m's in-text order: the ascending-sorted
# pattern vars get the DESCENDING-sorted target factors (measured
# 2026-08-25, Maxima 5.50.0, three independent defmatch probes: for the
# 1.1.1.4 four-sqrt pattern the (g,h)-named slot always receives the
# first target sqrt, (e,f) the middle, (c,d) the last, regardless of the
# factors' written order). Rubi's .m rules assume in-text binding
# (Mathematica matches commutative factors in order), and some repls are
# slot-specific: for the 1.1.1.4 1/((a+b x) Sqrt[c+d x] Sqrt[e+f x]
# Sqrt[g+h x]) identity, (c,d) is the Subst point — verified numerically
# (invar5/invar6 probes, 2026-08-25): the chain-rule difference is ~1e-19
# iff (c,d) holds the .m-named first factor and (e,f)/(g,h) are free to
# swap, ~1e-2 otherwise. So the (c,d) slot's capture names are remapped
# to sort LAST (g,h), making matchfix hand that slot the first target
# factor; the (e,f)/(g,h) slots keep/swap names freely (the identity is
# symmetric in them). A pure relabel — the repl/cond formulas are
# unchanged in value, only the names move.
CAP_REMAP = {
    ("1_1_1_4", 28): {"c": "g", "d": "h", "g": "c", "h": "d"},
    ("1_1_1_4", 29): {"c": "g", "d": "h", "g": "c", "h": "d"},
}

_IDCH = ("0123456789abcdefghijklmnopqrstuvwxyz"
         "ABCDEFGHIJKLMNOPQRSTUVWXYZ_")
_IDSTART = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")

_GAP_WORDS = {"and", "or", "then", "else", "do", "if", "return",
              "block", "in", "for", "while", "true", "false"}

def _gap_join(out, t):
    """FIX P4: a whitespace gap between two expression terminals in Rubi
    source is juxtaposition; Maxima reads it as a parse error or a
    SILENT noun call (measured 2026-08-22, Maxima 5.50.0, one batch run
    per form):
      `2 n` `f1 g1` `x 2` `%pi 2` `2 (x+1)` `(x) 2` `(x) z`  -> parse error
      `n (2*n+1)` `x (y)`  -> noun call: n(2 n + 1) / x(y)
      `(x) (y)`            -> the only legal spaced form (a product)
    So a gap whose both sides are expression terminals becomes an
    explicit `*`; the single exception, `)`/`]` followed by `(`, keeps
    its space. A Maxima word on either side of the gap (and/or/...)
    keeps the space — the walk emits ` and ` / ` or ` as one token with
    embedded spaces, and True/False translate to true/false. The walk
    keeps source spacing as tokens, so this sees every gap at every
    bracket depth."""
    left = out.rstrip()
    if not left:
        return t
    right = t.lstrip()
    if not right:
        return t
    li = len(left) - 1
    while li > 0 and left[li-1] in _IDCH:
        li -= 1
    if left[li:] in _GAP_WORDS:
        return t
    ri = 0
    while ri + 1 < len(right) and right[ri+1] in _IDCH:
        ri += 1
    if right[:ri+1] in _GAP_WORDS:
        return t
    L, R = left[-1], right[0]
    if L.isdigit():
        if R in _IDSTART or R == "(" or R == "%":
            return "*" + right
        return t
    if L in _IDCH:
        if R in _IDSTART or R.isdigit() or R == "(" or R == "%":
            return "*" + right
        return t
    if L in ")]" and (R in _IDSTART or R.isdigit() or R == "%"):
        return "*" + right
    return t

def _join_tokens(tokens):
    """Join the atom-walk tokens into one Maxima expression.

    FIX F6: the brief's `" ".join(out)` put a space between EVERY token
    (single characters included): `1/x` -> `1 / x`, a decimal `1.5` ->
    `1 . 5` (a Maxima parse error). Concatenate by default — the original
    spacing survives as tokens where it was not consumed by a marker —
    and insert a space only where gluing would merge two identifiers
    into one. Juxtaposition (a value terminal on both sides of a token
    boundary) needs an explicit `*`: a spaced gap goes through
    _gap_join (FIX P4), and the no-space cases — `x(…)` (a spaced form
    is a SILENT noun call, measured 2026-08-22, not a juxtaposition) and
    `…)x` (measured parse error) — get `*` directly. A NUMBER next to an
    open paren, or a close next to a number, needs an explicit * too
    (`2(x+1)` and `(x+1)2` are both Maxima parse errors, measured
    2026-08-20); digit-digit glue (one number: `12`).
    """
    out = ""
    for t in tokens:
        if not t:
            continue
        if not out:
            out = t
        elif out[-1] == " " or t[0] == " ":
            rep = _gap_join(out, t)
            if rep != t:
                # a * was inserted: drop the gap's own space(s)
                out = out.rstrip(" ") + rep
            else:
                out += t
        else:
            a, b = out[-1], t[0]
            if a in _IDSTART and b in _IDCH:
                # merging two identifiers: `a` `b` -> `a b`
                out += " " + t
            elif a in _IDSTART and b in "([":
                # juxtaposition: `x (…)` spaced is a silent noun call in
                # Maxima (measured 2026-08-22) — emit an explicit *.
                out += "*" + t
            elif a in ")]" and b in _IDSTART:
                # juxtaposition after a close: `(...)a` -> `...*a`
                # (the spaced form is a measured parse error).
                out += "*" + t
            elif a.isdigit() and b in "([":
                # FIX: `2 (x+1)` and `2(x+1)` are BOTH Maxima parse errors
                # (measured 2026-08-20) — a number next to an open
                # paren needs an explicit *: `2*(x+1)`.
                out += "*" + t
            elif a in ")]" and b.isdigit():
                # `(...) 2` — same: explicit * (measured parse error).
                out += "*" + t
            else:
                # glue: digits of one number (`12`), decimal points
                # (`1.5`), operators — the original spacing survives as
                # tokens where the walk kept it.
                out += t
    return out

def pattern_vars(lhs):
    """Capture names in a rule lhs: v_ and v_. (x_Symbol excluded — the
    pattern argument)."""
    vs = set(re.findall(r"([A-Za-z][A-Za-z0-9]*)_\.", lhs))
    vs |= set(re.findall(r"(?<!\.)\b([A-Za-z][A-Za-z0-9]*)_(?![.\w])", lhs))
    return vs - {"x"}

def split_top(s, sep=","):
    """Split s on top-level sep, honouring [ ] ( ) { } nesting."""
    out, depth, cur = [], 0, []
    for ch in s:
        if ch in "[({":
            depth += 1
        elif ch in "])}":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out

def head_args(s):
    """If s (stripped) is exactly `head[args]`, return (head, args); else
    (None, s). The matching ] is the one at depth 0 for the first [.

    FIX F1: the brief's balance check walked the whole string and always
    "succeeded" at the first top-level ]: `FreeQ[m, x] && NeQ[m, -1]`
    (greedy regex to the last ]) came back as head FreeQ with args
    `m, x] && NeQ[m, -1`. The first [ must match the LAST ] — nothing but
    whitespace may follow it.
    """
    s = s.strip()
    m = re.match(r"^([A-Za-z][A-Za-z0-9]*)\[(.*)\]$", s, re.DOTALL)
    if not m:
        return (None, s)
    head = m.group(1)
    depth, close = 0, None
    for j in range(len(head), len(s)):
        ch = s[j]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                close = j
                break
    if close is None or s[close + 1:].strip():
        return (None, s)
    return (head, s[len(head) + 1:close])

def _find_top(s, pred):
    """Index of the LAST position i where pred(s[i]) holds at bracket
    depth 0, or -1."""
    depth, last = 0, -1
    for i, ch in enumerate(s):
        if ch in "[({":
            depth += 1
        elif ch in "])}":
            depth -= 1
        elif depth == 0 and pred(i, ch):
            last = i
    return last

def split_rule_outer(text):
    """(lhs, rhs, cond) split on the LAST top-level /; — the OUTER one.
    FIX E1: the census's split_rule splits at the FIRST /;, which is wrong
    for the 177 class-1 rules whose With/Module body carries its own inner
    /;: `With[{…}, body /; inner] /; outer` must split on the outer one."""
    lhs, rhsfull = text.split(":=", 1)
    last = _find_top(rhsfull, lambda i, ch: ch == "/" and rhsfull[i+1:i+2] == ";")
    if last >= 0:
        rhs, cond = rhsfull[:last], rhsfull[last+2:]
    else:
        rhs, cond = rhsfull, ""
    return lhs.strip(), rhs.strip(), cond.strip()

def clean_cond(cond, key, n):
    """Strip the 1.4.1 If[TrueQ[$LoadShowSteps], …] parser artifacts (FIX
    E8): a branch-separator ',' trailing the cond, and one unbalanced ']'
    (the If closer). Neither can occur in a well-formed cond; anything else
    unbalanced is a genuine parse failure — loud."""
    cond = cond.strip()
    if not cond:
        return ""
    if cond.endswith(","):
        cond = cond[:-1].rstrip()
    depth = 0
    for ch in cond:
        if ch in "[({":
            depth += 1
        elif ch in "])}":
            depth -= 1
    if depth == -1 and cond.endswith("]"):
        cond = cond[:-1].rstrip()
        depth = 0
    if depth != 0:
        raise GenError(f"{key} r{n}: unbalanced cond (depth {depth}): "
                       f"{cond[:60]!r}")
    return cond

def split_top_power(s):
    """(base, exp) if s is a top-level power `base^exp`; else (None, None)."""
    s = s.strip()
    pos = _find_top(s, lambda i, ch: ch == "^")
    if pos <= 0 or pos >= len(s) - 1:
        return (None, None)
    return (s[:pos].strip(), s[pos+1:].strip())

def _term_deg_coef(t):
    """(exp_str, coef) for a monomial-in-x term; exp None if x-free.
    exp_str is the literal text after x^ (a digit run) or '1' for a bare x;
    a non-digit exp (a capture var) is passed through so the caller can flag
    the factor ambiguous. coef is the text multiplying the x-part."""
    t = t.strip()
    if t[:1] in ("+", "-"):
        t = t[1:].strip()
    m = re.search(r"(?<![A-Za-z0-9_])x\^([A-Za-z0-9_]+|\d+)\s*$", t)
    if m:
        return (m.group(1), t[:m.start()])
    m = re.search(r"(?<![A-Za-z0-9_])x\s*$", t)
    if m:
        return ("1", t[:m.start()])
    return (None, t)

def _split_sum(s):
    """Top-level terms of a Plus/Minus sum (sign kept with the following
    term; bracket nesting honoured)."""
    terms, depth, cur = [], 0, []
    for i, ch in enumerate(s):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if depth == 0 and ch in "+-" and i > 0:
            if "".join(cur).strip():
                terms.append("".join(cur)); cur = []
            cur.append(ch)
        else:
            cur.append(ch)
    if "".join(cur).strip():
        terms.append("".join(cur))
    return terms

def _paren_groups(s):
    """Every balanced (start, end) paren group in s."""
    out, depth, start = [], 0, -1
    for i, ch in enumerate(s):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and start >= 0:
                out.append((start, i)); start = -1
    return out

def nonzero_guard_caps(pat):
    """Capture names whose degenerate 0-binding must be rejected by the
    matcher: (a) the LEADING coefficient of a parenthesized polynomial-in-x
    factor of numeric degree >= 2, and (b) any SYMBOLIC exponent of an x-term.

    Maxima's defmatch, unlike Mathematica's, binds a missing leading term of
    a lower-degree polynomial to 0, so a quadratic/quartic pattern matches a
    binomial/monomial (the flat first-match-wins table then lets the
    higher-form rule fire on the lower-form integrand — the measured
    2026-08-24 source of the wrong-answer misfires). Likewise a symbolic
    exponent n bound to 0 turns b*x^n into the constant b (a degenerate
    constant denominator, the 1_2_3_5_r20 case). Declaring such a capture to
    match only nonzero values makes the matcher itself reject the binding
    (probe /tmp/md4: rejects C=0, keeps the missing-middle-term case B=0).
    A numeric exponent (x^2, x^4) is never 0, so only symbolic ones are
    flagged; a numeric leading coefficient needs degree >= 2 (a binomial's
    b*x bound to b=0 against a constant is not the misfire seen)."""
    res = set()
    for (s, e) in _paren_groups(pat):
        content = pat[s+1:e]
        if "x" not in content:
            continue
        terms = _split_sum(content)
        if any(("(" in t) or ("[" in t) for t in terms):
            continue  # not a flat monomial-in-x sum
        infos = [_term_deg_coef(t) for t in terms]
        if all(exp is None for exp, _ in infos):
            continue  # no x term at all
        sym = [exp for exp, _ in infos
               if exp is not None and not re.fullmatch(r"-?\d+", exp)]
        for exp in sym:
            res.add(exp.strip())  # a genuine x-term requires n != 0
        if sym:
            continue  # degrees are symbolic: exponents guard the factor
        degs = [int(exp) for exp, _ in infos if exp is not None]
        mx = max(degs)
        if mx < 2:
            continue  # binomials/monomials: degenerate-0 is not the bug
        for exp, coef in infos:
            if exp is not None and int(exp) == mx:
                res.update(re.findall(r"_mr_[A-Za-z0-9_]+", coef))
    return res

def split_utility_def(text):
    """(rule_text, [utility def lines]) — a Rubi rule file may inline a
    C-tier utility definition (IntLinearQ/IntBinomialQ/IntQuadraticQ) on
    the line(s) after a rule; the line-based run parser glues it onto the
    rule run (5 class-1 runs, measured). A second top-level := in the run
    marks the definition: the rule is the text before it, the definition
    is provenance only (ported in Task 7 as the %mr_* predicate the rule
    cond calls; emitting it as a rule would be a parse error and as a
    live definition would collide with the Task 7 port)."""
    lines = text.split("\n")
    first, second = None, None
    depth = 0
    for li, ln in enumerate(lines):
        i = 0
        while i < len(ln):
            ch = ln[i]
            if ch in "[({":
                depth += 1; i += 1
            elif ch in "])}":
                depth -= 1; i += 1
            elif ln[i:i+2] == ":=" and depth == 0:
                if first is None:
                    first = li
                elif second is None:
                    second = li
                i += 2
            else:
                i += 1
    if second is None:
        return text, []
    return "\n".join(lines[:second]), lines[second:]

def drop_optionals(text, varset):
    """v_. and v_ -> the renamed capture (the plain pattern; the matcher's
    decomposition fills the Plus/Times identity defaults). Power-optional
    exponents are D-duplicated at the emit level, not here.

    DANGER: raw-text use only. The replaces are SUBSTRING replacements,
    not marker-aware: on translated text a capture named `r` makes
    replace("r_", "r") hit the `_mr_` prefix of every renamed capture
    (the 2026-08-24 dead-rule bug — see emit_rule). Never call this on
    translated text."""
    for v in sorted(varset, key=len, reverse=True):
        text = text.replace(v + "_.", v).replace(v + "_", v)
    return text

def translate_token(tok, ctx):
    """A bare identifier -> MatchQ fresh var / renamed capture / constant /
    table name / itself. Unknown tokens pass through here (legit
    constants/renamed vars in atom position); an unlisted HEAD is rejected
    loudly at the emit_head boundary, not here."""
    if ctx["markers"] and tok in ctx["markers"]:
        return ctx["markers"][tok]
    if tok in ctx["vars"]:
        return cap_name(ctx["key"], ctx["n"], tok)
    if tok in ("Pi", "E", "I"):
        # FIX E10: the Mathematica constants are %pi / %e / %i — passing
        # them through emitted the WRONG value as a bare Maxima symbol.
        return {"Pi": "%pi", "E": "%e", "I": "%i"}[tok]
    if tok in ("True", "False"):
        return "true" if tok == "True" else "false"
    if tok in RENAME or tok in RESTRUCTURE:
        return table_translate(tok)
    # unknown identifier that is not a capture: a Maxima symbol (a, b, c, …)
    # appearing in a cond/rhs but not the lhs — pass through.
    return tok

def translate(s, ctx):
    """Recursive translator: .m expression -> Maxima expression.

    ctx is the per-rule context: {"key", "n", "vars" (lhs captures),
    "decls" (extra matchdeclare names, MatchQ), "markers" (the active
    MatchQ pattern-var name map, or None), "mq" (occurrence counter)}.

    Walks a token stream; on `head[args]` it translates each top-level arg
    and applies the head's special form. Atoms rename captures and drop
    optionals.
    """
    s = s.strip()
    head, args = head_args(s)
    if head is not None:
        if head == "MatchQ":
            # The pattern arg must be translated in the FRESH MatchQ
            # marker scope (_emit_matchq mints the names), not the outer
            # scope: pre-translating the args raises on the pattern's own
            # markers (a_ is no capture of the rule). Pass the RAW args.
            parts = split_top(args, ",") if args.strip() else []
            return _emit_matchq(parts, ctx)
        arglist = [translate(a, ctx)
                   for a in split_top(args, ",")] if args.strip() else []
        return emit_head(head, arglist, ctx)
    return translate_atom(s, ctx)

def translate_atom(s, ctx):
    """A non-`head[...]` expression: rename captures, drop optionals,
    rewrite && / ||, and translate any nested head[args] sub-expressions.
    Works on a token walk so nested heads inside sums/products are
    handled."""
    out, i, L = [], 0, len(s)
    while i < L:
        m = re.match(r"[A-Za-z][A-Za-z0-9]*", s[i:])
        if m:
            name = m.group()
            j = i + len(name)
            if s[j:j+1] == "_":
                # A pattern-variable marker. MatchQ pattern scope first
                # (ctx["markers"] active), then the integration variable,
                # then this rule's lhs captures. FIX F11: a marker on a
                # name in none of those is a variable the emitter cannot
                # rename — fail loudly, never emit a bare underscore that
                # Maxima would read as a fresh pattern variable.
                if ctx["markers"] and name in ctx["markers"]:
                    end = j + 2 if s[j:j+2] == "_." else j + 1
                    out.append(ctx["markers"][name])
                    i = end
                    continue
                if name == "x":
                    # `x_Symbol` -> x (the pattern argument). FIX F10:
                    # require name == "x" — a capture named xs_ followed by
                    # _Symbol must not be swallowed as the integration
                    # variable. A capture named like the integration
                    # variable IS the integration variable (Mathematica
                    # same-named patterns must agree): `x_` -> x,
                    # consuming the marker, no matchdeclare.
                    if s[j:j+8] == "_Symbol":
                        out.append("x"); i = j + 8; continue
                    end = j + 2 if s[j:j+2] in ("_.", "_ ") else j + 1
                    out.append("x"); i = end; continue
                if name in ctx["vars"]:
                    end = j + 2 if s[j:j+2] in ("_.", "_ ") else j + 1
                    out.append(cap_name(ctx["key"], ctx["n"], name))
                    i = end
                    continue
                raise GenError(f"{ctx['key']} r{ctx['n']}: pattern variable "
                               f"{name!r} cannot be renamed (captures: "
                               f"{sorted(ctx['vars'])})")
            # a nested head[args]?
            k = j
            while k < L and s[k] in " \t":
                k += 1
            if k < L and s[k] == "[":
                # find the matching ]
                depth, t = 0, k
                while t < L:
                    if s[t] == "[":
                        depth += 1
                    elif s[t] == "]":
                        depth -= 1
                        if depth == 0:
                            break
                    t += 1
                argtxt = s[k+1:t]
                out.append(translate(name + "[" + argtxt + "]", ctx))
                i = t + 1; continue
            out.append(translate_token(name, ctx)); i = j; continue
        if s[i:i+2] == "&&":
            out.append(" and "); i += 2; continue
        if s[i:i+2] == "||":
            out.append(" or "); i += 2; continue
        # FIX P1: this build's parser rejects `==` in EVERY position
        # (measured 2026-08-22, Maxima 5.50.0: even `1 == 1` is
        # "incorrect syntax: = is not a prefix operator"). `=` carries the
        # syntactic-equality semantics `==` had classically — is(a = b) ->
        # true/false, never unknown (manual entry for `=`, value-probed) —
        # and mixes with and/or correctly: `n = 2 and q` values as
        # (n = 2) and q. Translate `==` to `=`. (This build's negation is
        # `#`, not `#=`; no class-1 source uses `#=`, so no mapping yet.)
        if s[i:i+2] == "==":
            out.append("="); i += 2; continue
        ch = s[i]
        # FIX F7: Mathematica list braces are Maxima brackets.
        if ch == "{":
            out.append("["); i += 1; continue
        if ch == "}":
            out.append("]"); i += 1; continue
        # FIX E3: Rubi's explicit-multiplication escape \[Star] is a parse
        # error in Maxima (measured: "\[Star is not an infix operator");
        # emit a bare *. Other \[Name] escapes pass through — in class 1
        # only \[CenterEllipsis] occurs, inside ShowStep strings that the
        # ShowStep handler drops; any live occurrence fails loudly at
        # Maxima load rather than being silently mangled.
        if ch == "\\" and s[i+1:i+2] == "[":
            t2 = s.find("]", i)
            if t2 > i + 2:
                if s[i+2:t2] == "Star":
                    out.append("*"); i = t2 + 1; continue
                out.append(s[i:t2+1]); i = t2 + 1; continue
            out.append(ch); i += 1; continue
        out.append(ch); i += 1
    return _expand_chains(_join_tokens(out))

def _expand_chains(s):
    """FIX P3: expand raw relational chains (`3 <= d <= 4`) — Maxima has
    no chained comparison (measured 2026-08-22: "Found LOGICAL expression
    where ALGEBRAIC expression expected"). Rubi's own chain semantics are
    conjunctive (LtQ[u,v,w] := LtQ[u,v] && LtQ[v,w], Rubi :468-:470), and
    the 3-arg CMP_OPS path already emits the same shape, so a k-op chain
    P0 op1 P1 ... opk Pk becomes
    is(P0 op1 P1) and is(P1 op2 P2) and ... and is(P(k-1) opk Pk).
    A lone comparison is untouched (a raw `a <= b` is a legal Maxima
    relation the rule runner's is(ok) evaluates). Runs at the end of
    translate_atom, at every bracket depth (recurses into groups). The
    operators seen in translated text are = <= >= < > (`==` is already
    folded to `=` by the walk); a `;`/`,`/`and`/`or` between two ops ends
    the chain. Class-1 sites: 1.2.1.1 r16 (cond) and r17 (inner /; cond)."""
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch in "([{":
            depth, j = 1, i + 1
            while j < n and depth:
                if s[j] in "([{":
                    depth += 1
                elif s[j] in ")]}":
                    depth -= 1
                j += 1
            out.append(ch + _expand_chains(s[i+1:j-1]) + s[j-1])
            i = j
            continue
        out.append(ch)
        i += 1
    s = "".join(out)
    # Partition the depth-0 text into a complete item sequence: relational
    # ops, chain terminators (';', ',', ' and ', ' or '), and the term runs
    # between them. A chain is a run  TERM OP TERM OP ... OP TERM  with
    # 2+ ops (k ops -> k+1 terms); spans never overlap, so forward
    # rewriting is position-stable within the scan.
    items = []
    i = 0
    n = len(s)
    depth = 0
    cur = None
    while i < n:
        ch = s[i]
        if ch in "([{":
            depth += 1
            if cur is None:
                cur = i
            i += 1
            continue
        if ch in ")]}":
            depth -= 1
            if cur is None:
                cur = i
            i += 1
            continue
        if depth == 0:
            two = s[i:i+2]
            hit = None
            if two in ("==", "#=", "<=", ">="):
                hit = (i, i + 2, "op")
            elif ch in "<>=" and s[i-1:i] != ":":
                hit = (i, i + 1, "op")
            elif ch in ";,":
                hit = (i, i + 1, "stop")
            elif ch == "a" and i > 0 and s[i-1] == " " and s[i:i+3] == "and" \
                    and s[i+3:i+4] == " ":
                hit = (i - 1, i + 4, "stop")
            elif ch == "o" and i > 0 and s[i-1] == " " and s[i:i+2] == "or" \
                    and s[i+2:i+3] == " ":
                hit = (i - 1, i + 3, "stop")
            if hit is not None:
                if cur is not None:
                    items.append([cur, hit[0], "term"])
                    cur = None
                items.append([hit[0], hit[1], hit[2]])
                i = hit[1]
                continue
        if cur is None:
            cur = i
        i += 1
    if cur is not None:
        items.append([cur, n, "term"])
    i = 0
    while i + 3 < len(items):
        if items[i][2] == "term" and items[i+1][2] == "op":
            k = 1
            while i + 2*k + 1 < len(items) \
                    and items[i + 2*k + 1][2] == "op":
                k += 1
            if k >= 2 and items[i + 2*k][2] == "term":
                parts = [items[i + 2*t] for t in range(k + 1)]
                ops = [items[i + 2*t + 1] for t in range(k)]
                seg = " and ".join(
                    "is(" + s[parts[t][0]:parts[t][1]].strip()
                    + " " + s[ops[t][0]:ops[t][1]]
                    + " " + s[parts[t+1][0]:parts[t+1][1]].strip() + ")"
                    for t in range(k))
                s = s[:parts[0][0]] + seg + s[parts[-1][1]:]
                i += 2 * k
                continue
        i += 1
    return s

def _maxima_stmts(body):
    """Top-level statement syntax of a Rubi With/Module body -> Maxima
    block syntax. Measured 2026-08-22 (Maxima 5.50.0):
    * a top-level ';' is a parse error in a block ("incorrect syntax:
      Missing )" at the ';' — block statements separate with ',');
    * a 'v = e' statement values to a discarded equation — the local is
      never bound (block([u], u = 5, u) -> unbound u); only ':' assigns.
    The 8 class-1 bodies (1.1.3.1 r13/14/21/22, 1.1.3.2 r35-38) are the
    'u = Int[...]; <expr>' shape. The caller splits the inner '/;'
    conditional FIRST, so no '/;' reaches here. A source 'v == e'
    statement arrives already folded to 'v = e' by the walk and is
    treated like any other statement (the local would be bound to the
    comparison result); no such statement occurs in class 1."""
    out, depth = [], 0
    for ch in body:
        if ch in "[({":
            depth += 1
            out.append(ch)
        elif ch in ")]}":
            depth -= 1
            out.append(ch)
        elif ch == ";" and depth == 0:
            out.append(",")
        else:
            out.append(ch)
    segs = []
    for seg in split_top("".join(out), ","):
        m = re.match(r"\s*([A-Za-z][A-Za-z0-9_]*)\s*=(?!=)", seg)
        if m:
            seg = m.group(1) + " :" + seg[m.end():]
        segs.append(seg)
    return ", ".join(segs)

def power_dups(pattern, key, n, varset):
    """Return the list of pattern texts to emit for one rule: the plain
    pattern, plus a duplicate with each optional Power exponent (`u_^m_.`)
    dropped and `m` bound to 1 — the structural case decomposition cannot
    fill (measured 2026-08-20). Most rules yield exactly one pattern.

    DEFERRED (human decision 2026-08-20): NOT wired into emit_rule; Task 9's
    divergence loop adds it where the corpus shows the gap."""
    pats = [pattern]
    for m in re.finditer(r"([A-Za-z][A-Za-z0-9]*)\^\s*("
                         + "|".join(sorted(varset, key=len, reverse=True))
                         + r")_\.\b", pattern):
        base, exp = m.group(1), m.group(2)
        dup = pattern.replace(base + f"^{exp}_.", base, 1)
        pats.append((dup, exp))
    # (dup, exp) pairs become extra matchers binding <exp> := 1; a single
    # element returns the plain pattern only.)
    return pats

CMP_OPS = {"GtQ": ">", "LtQ": "<", "LeQ": "<=", "GeQ": ">=",
           "IGtQ": ">", "ILtQ": "<", "ILeQ": "<="}

def _emit_polyq(arglist, key, n):
    """PolyQ overload dispatch (Task 6 Step 0, the F2 blocker):
    (u, x) -> %mr_polyQ · (u, x, n) -> %mr_polyDegQ ·
    (u, x^v) / (u, B^v) -> %mr_polyPowerQ · (u, x^v, n) / (u, B^v, n) ->
    %mr_polyDegPowerQ, where B is an expression (class 1 also passes a
    capture as the base: PolyQ[Pq, v^n]). A shape that cannot be mapped is
    a GenError — never a pass-through (which would silently treat the
    power form as a variable)."""
    if len(arglist) not in (2, 3):
        raise GenError(f"{key} r{n}: PolyQ arity {len(arglist)}")
    u, form = arglist[0].strip(), arglist[1].strip()
    deg = arglist[2].strip() if len(arglist) == 3 else None
    if form == "x":
        if deg is None:
            return f"%mr_polyQ({u}, x)"
        return f"%mr_polyDegQ({u}, x, {deg})"
    base, v = split_top_power(form)
    if base is None:
        raise GenError(f"{key} r{n}: unmappable PolyQ form {form!r}")
    if deg is None:
        return f"%mr_polyPowerQ({u}, {base}, {v})"
    return f"%mr_polyDegPowerQ({u}, {base}, {v}, {deg})"

def _emit_expon(arglist, key, n):
    """Expon (Rubi :1239/:1242 — Exponent[Together[expr], form[, h]]):
    (u, x) -> %mr_expon · (u, x^v) -> %mr_expon(u, x, v) (power-form:
    exponents that are multiples of v) · (u, x, Min|Max) ->
    %mr_exponMin / %mr_expon (Max is the default). Task 7 ports the three
    functions; the call shapes are pinned here."""
    if len(arglist) == 2:
        u, form = arglist[0].strip(), arglist[1].strip()
        if form == "x":
            return f"%mr_expon({u}, x)"
        base, v = split_top_power(form)
        if base == "x":
            return f"%mr_expon({u}, x, {v})"
        raise GenError(f"{key} r{n}: unmappable Expon form {form!r}")
    if len(arglist) == 3:
        u, form, h = (a.strip() for a in arglist)
        if form != "x":
            raise GenError(f"{key} r{n}: Expon headed by {h!r} needs bare x")
        # the table already maps Min/Max -> min/max (RESTRUCTURE)
        if h in ("Min", "min"):
            return f"%mr_exponMin({u}, x)"
        if h in ("Max", "max"):
            return f"%mr_expon({u}, x)"
        raise GenError(f"{key} r{n}: Expon head {h!r}")
    raise GenError(f"{key} r{n}: Expon arity {len(arglist)}")

def _emit_coeff(arglist, key, n):
    """Coeff/Coefficient (Rubi :1246) — every class-1 use is 3-arg with
    form x or the power form x^v (21 uses: Coeff[P3, x^(n/2), k] -> the
    4-arg %mr_coeff, a Task 7 port)."""
    if len(arglist) != 3:
        raise GenError(f"{key} r{n}: Coeff arity {len(arglist)}")
    u, form, k = (a.strip() for a in arglist)
    if form == "x":
        return f"%mr_coeff({u}, x, {k})"
    base, v = split_top_power(form)
    if base == "x":
        return f"%mr_coeff({u}, x, {v}, {k})"
    raise GenError(f"{key} r{n}: unmappable Coeff form {form!r}")

def _emit_matchq(arglist, ctx):
    """MatchQ[u, pat /; cond] — called from translate() with the RAW
    (untranslated) args, since the pattern must be translated in the
    fresh marker scope, not the outer one. Every class-1 use is this
    pattern-form (the pattern carries its own pattern variables). Fresh
    names per (file, rule, occurrence, variable), matchdeclare'd as
    pattern vars;
    the uniform 3-arg call %mr_matchQ(u, pattern, cond) is emitted with
    the pattern UNQUOTED so computed parts (renamed outer captures)
    evaluate at call time while the pattern vars stay literal (a bare
    symbol not matchdeclare'd in the active pattern is a literal in
    Maxima), and the cond as a LAMBDA over the binding list:
    lambda([%mr_mqb], <cond with each marker m rewritten to
    %mr_mk(m, %mr_mqb)>). Maxima evaluates call arguments eagerly, so
    an unquoted cond would evaluate its marker-dependent parts
    (IntegerQ[m], m > 1, FreeQ[m, x]) on the unbound marker symbols
    before the match; a quote does not help either — this build's ev()
    does not strip quotes (measured 2026-08-23, task 7a A3). A lambda
    body is held until called and keeps the lexical environment, so
    the cond's outer-capture references resolve when the matcher calls
    it with the binding list. Named lookups (%mr_mk) keep the marker
    order decoupled between generator and matcher. Task 7 ports
    %mr_matchQ. FIX E7."""
    key, n = ctx["key"], ctx["n"]
    if len(arglist) != 2:
        raise GenError(f"{key} r{n}: MatchQ arity {len(arglist)}")
    u_txt = translate(arglist[0].strip(), ctx)
    patpart = arglist[1].strip()
    last = _find_top(patpart,
                     lambda i, ch: ch == "/" and patpart[i+1:i+2] == ";")
    if last >= 0:
        pat, mcond = patpart[:last].strip(), patpart[last+2:].strip()
    else:
        pat, mcond = patpart, ""
    markers = set(re.findall(r"([A-Za-z][A-Za-z0-9]*)_\.", pat))
    markers |= set(re.findall(r"(?<!\.)\b([A-Za-z][A-Za-z0-9]*)_(?![.\w])",
                              pat))
    if not markers:
        raise GenError(f"{key} r{n}: MatchQ pattern without variables: "
                       f"{pat!r}")
    ctx["mq"] += 1
    mark = {v: f"_mr_{key}_r{n}mq{ctx['mq']}_{v}" for v in markers}
    ctx["decls"].update(mark.values())
    saved = ctx["markers"]
    ctx["markers"] = mark
    try:
        pat_txt = translate(pat, ctx)
        cond_txt = translate(mcond, ctx) if mcond else ""
    finally:
        ctx["markers"] = saved
    if not cond_txt:
        cond_emit = "true"
    else:
        # rewrite each marker to a named lookup in the binding list the
        # matcher passes; \b...\b guards the prefix-collision case
        # (one marker name beginning with another, e.g. Q vs Qx)
        for m in mark.values():
            cond_txt = re.sub(rf"\b{re.escape(m)}\b",
                              f"%mr_mk({m}, %mr_mqb)", cond_txt)
        cond_emit = f"lambda([%mr_mqb], {cond_txt})"
    return f"%mr_matchQ({u_txt}, {pat_txt}, {cond_emit})"

def emit_head(head, arglist, ctx):
    """Special forms first, then a plain renamed head(arglist)."""
    key, n = ctx["key"], ctx["n"]
    if head == "FreeQ":
        # FreeQ[e, x] -> freeof(x, e); FreeQ[{a,b}, x] -> and of freeof.
        # (FIX F7) the arg list may arrive as [a, b] (braces already
        # converted by translate_atom) or still as {a, b}.
        e, xv = arglist[0], arglist[1]
        if e.startswith("{") or e.startswith("["):
            e = e[1:-1]
        parts = [f"freeof({xv}, {p.strip()})" for p in split_top(e, ",")]
        return " and ".join(parts)
    if head in CMP_OPS:
        op = CMP_OPS[head]
        if len(arglist) == 2:
            return f"is({arglist[0]} {op} {arglist[1]})"
        if len(arglist) == 3:
            # Rubi :468-:470 chained form: LtQ[u,v,w] := LtQ[u,v] && LtQ[v,w]
            a, b, c = (p.strip() for p in arglist)
            return f"is({a} {op} {b}) and is({b} {op} {c})"
        raise GenError(f"{key} r{n}: {head} arity {len(arglist)}")
    if head in ("Int", "IntHide"):
        return f"mr_int({arglist[0]}, {arglist[1]})"
    if head in ("Unintegrable", "CannotIntegrate"):
        return f"mr_unintegrable({arglist[0]}, {arglist[1]})"
    if head == "With" or head == "Module":
        if len(arglist) != 2:
            raise GenError(f"{key} r{n}: {head} arity {len(arglist)}")
        decls_txt, body = arglist[0].strip(), arglist[1].strip()
        if not (decls_txt.startswith("[") and decls_txt.endswith("]")):
            raise GenError(f"{key} r{n}: {head} locals not a list: "
                           f"{decls_txt[:40]!r}")
        locals_, assigns = [], []
        for p in split_top(decls_txt[1:-1], ","):
            p = p.strip()
            parts = split_top(p, "=")
            name = parts[0].strip()
            if not name:
                raise GenError(f"{key} r{n}: empty {head} local: {p!r}")
            if len(parts) > 1 and parts[1].strip():
                # FIX E11: the arglist is ALREADY translated — re-translating
                # double-renames the captures (the walk sees `_mr_…_a` and
                # raises "pattern variable 'mr'") and mis-translates the
                # value. Use the text as is; a bare local (Module[{k, u}, …])
                # declares without an assignment.
                val = ", ".join(q.strip() for q in parts[1:])
                assigns.append(f"{name} : {val}")
            locals_.append(name)
        # FIX E1 (body half): a body may carry its own top-level /; (a
        # Conditional inside the With/Module). Emit the explicit guard —
        # false means the rule declines (Rubi's unevaluated Conditional
        # never yields an answer).
        last = _find_top(body,
                         lambda i, ch: ch == "/" and body[i+1] == ";")
        if last >= 0:
            inner, inner_cond = body[:last].strip(), body[last+2:].strip()
            # FIX P2/P5: statement syntax (';' / 'v = e') -> block
            # syntax (',' / 'v : e'); the '/;' is consumed by the split
            # above, so its ';' never reaches _maxima_stmts.
            inner = _maxima_stmts(inner)
            body = f"(if is({inner_cond}) = true then {inner} else false)"
        else:
            body = _maxima_stmts(body)
        lead = ", ".join(assigns) + ", " if assigns else ""
        return f"block([{', '.join(locals_)}], {lead}{body})"
    if head == "If":
        if len(arglist) != 3:
            raise GenError(f"{key} r{n}: If arity {len(arglist)}")
        # parenthesized: an If inside a && / || cond chain must bind as one
        # operand
        return f"(if {arglist[0]} then {arglist[1]} else {arglist[2]})"
    if head == "Boole":
        if len(arglist) != 1:
            raise GenError(f"{key} r{n}: Boole arity {len(arglist)}")
        return f"(if {arglist[0]} then 1 else 0)"
    if head == "Sum":
        # FIX E5: Rubi's finite Sum -> 4-arg mr_sum(fun, var, lo, hi);
        # the iterator {var, lo, hi} is the second arg. Single-iterator
        # only in class 1 (28 uses, measured). Maxima evaluates function
        # arguments eagerly, so a summand containing a total package
        # function of the index (e.g. %mr_coeff(Pq, x, 2*k)) would
        # collapse to 0 before mr_sum sees it: every NON-identifier
        # summand is wrapped in lambda([var], <summand>) so the body
        # survives to per-index evaluation — mr_sum concretizes constant
        # ranges (2026-08-25 divergence fix). Identifier summands (the
        # Module-local-u shape) are passed bare: mr_sum resolves the
        # symbol's value per index.
        if len(arglist) != 2:
            raise GenError(f"{key} r{n}: Sum arity {len(arglist)}")
        it = arglist[1].strip()
        if not (it.startswith("[") and it.endswith("]")):
            raise GenError(f"{key} r{n}: Sum iterator not a list: {it[:40]!r}")
        parts = split_top(it[1:-1], ",")
        if len(parts) != 3:
            raise GenError(f"{key} r{n}: multi-iterator Sum not in class 1: "
                           f"{it[:40]!r}")
        var, lo, hi = (p.strip() for p in parts)
        fun = arglist[0].strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", fun):
            return f"mr_sum({fun}, {var}, {lo}, {hi})"
        return f"mr_sum(lambda([{var}], {fun}), {var}, {lo}, {hi})"
    if head == "ShowStep":
        # Rubi ShowStepRoutines.m :221 — ShowStep[condStrg, lhsStrg,
        # rhsStrg, rhs] is a display wrapper that VALUES to ReleaseHold[rhs]:
        # emit the fourth arg, unwrapping Hold. (FIX E4 — the RESTRUCTURE
        # "drop" would have left a bare ShowStep noun.)
        if len(arglist) != 4:
            raise GenError(f"{key} r{n}: ShowStep arity {len(arglist)}")
        body = arglist[3].strip()
        m2 = re.fullmatch(r"%mr_hold\((.*)\)", body, re.DOTALL)
        if m2:
            body = m2.group(1).strip()
        return body
    if head == "PolyQ":
        return _emit_polyq(arglist, key, n)
    if head == "Expon":
        return _emit_expon(arglist, key, n)
    if head in ("Coeff", "Coefficient"):
        return _emit_coeff(arglist, key, n)
    if head == "ReplaceAll":
        # ReplaceAll[expr, x -> v] -> subst(v, x, expr) — Maxima's subst
        # takes (value, pattern, expression): the args REORDER (FIX E2;
        # `->` itself is a parse error in this build, measured). All 59
        # class-1 uses are the single-rule x -> v form.
        if len(arglist) != 2:
            raise GenError(f"{key} r{n}: ReplaceAll arity {len(arglist)}")
        expr, rule = arglist[0].strip(), arglist[1].strip()
        if rule.startswith("["):
            # rule-list form (2 class-1 uses, 1_2_2_3 r86/r87):
            # ReplaceAll[expr, {p1 -> v1, ...}] ->
            # subst([p1 = v1, ...], expr) — the equation-list form; the
            # equations apply serially left-to-right (manual: subst),
            # which is equivalent here: the p_i are fresh Module dummies
            # (aa/bb/cc) never appearing on the right sides. The
            # 3-arg list form subst([v..],[p..],e) does NOT substitute
            # (measured 2026-08-20).
            eqs = []
            for r in split_top(rule[1:-1], ","):
                r = r.strip()
                last = _find_top(r,
                                 lambda i, ch: ch == "-" and r[i+1] == ">")
                if last <= 0:
                    raise GenError(f"{key} r{n}: ReplaceAll rule without "
                                   f"arrow: {r[:40]!r}")
                eqs.append(f"{r[:last].strip()} = {r[last+2:].strip()}")
            return f"subst([{', '.join(eqs)}], {expr})"
        last = _find_top(rule,
                         lambda i, ch: ch == "-" and rule[i+1] == ">")
        if last <= 0:
            raise GenError(f"{key} r{n}: ReplaceAll rule without arrow: "
                           f"{rule[:40]!r}")
        pat, val = rule[:last].strip(), rule[last+2:].strip()
        return f"subst({val}, {pat}, {expr})"
    if head in ("IntegersQ", "RationalQ"):
        # Rubi :71/:97 — variadic (IntegersQ[__Integer], RationalQ[u__]).
        # 1 arg: scalar call; >= 2: a list call (the Task 7 ports accept
        # both; the committed scalar %mr_rationalQ keeps its 1-arg shape).
        name = "%mr_integersQ" if head == "IntegersQ" else "%mr_rationalQ"
        if len(arglist) == 1:
            return f"{name}({arglist[0]})"
        return f"{name}([{', '.join(arglist)}])"
    # (MatchQ is dispatched in translate() with RAW args — see there.)
    if head == "Hypergeometric2F1":
        a, b, c, z = arglist
        return f"hypergeometric([{a}, {b}], [{c}], {z})"
    if head in ("EllipticF", "EllipticE", "EllipticPi"):
        # Native Maxima noun (NOT a package mr_* spelling): `diff` knows
        # the native elliptic_f/e/pi derivatives, and the corpus's
        # expected answers use the native names (measured 2026-08-24).
        fn = {"EllipticF": "elliptic_f", "EllipticE": "elliptic_e",
              "EllipticPi": "elliptic_pi"}[head]
        return f"{fn}({', '.join(arglist)})"
    # A head absent from the table is a census miss: fail LOUDLY, never emit
    # a bare Maxima noun FooQ(...) — that makes is(ok) = true perpetually
    # false (a silently dead rule) or a silently noun-laden wrong answer.
    # The atom-position pass-through (translate_atom) is a separate,
    # legitimate path for constants/renamed vars, so the check lives here at
    # the head boundary, not in translate_token.
    if head not in RENAME and head not in RESTRUCTURE:
        raise GenError(f"{key} r{n}: unlisted head {head!r} — extend the "
                       f"translation table (T4 §2) before generating")
    name = translate_token(head, ctx)
    # FIX F2: Maxima function calls use parentheses; the brief emitted the
    # Mathematica bracket form name[args], which is a parse error / noun
    # form in Maxima.
    return f"{name}({', '.join(arglist)})"

def emit_rule(run, key, n, rule_vars):
    """One rule run (lhs, rhs, cond) -> the five Maxima functions as text.
    rule_vars is the set of capture names (from the lhs)."""
    lhs, rhs, cond = run
    # integrand pattern: strip Int[ ... , x_Symbol]
    m = re.match(r"^Int\[(.*),\s*x_Symbol\]$", lhs.strip(), re.DOTALL)
    if not m:
        raise GenError(f"{key} r{n}: cannot strip Int[...]: {lhs!r}")
    ctx = {"key": key, "n": n, "vars": rule_vars, "decls": set(),
           "markers": None, "mq": 0}
    # BUG FIX (2026-08-24, 138 dead rules): this used to be
    # drop_optionals(translate(...), rule_vars) — drop_optionals on
    # TRANSLATED text is NOT the no-op its docstring claims: its
    # text.replace(v + "_", v) hits any occurrence of v+"_" anywhere in
    # the text, and a capture named `r` corrupted the `_mr_` prefix of
    # every renamed capture in the pattern (`_mr_1_1_2_6_r3_g` ->
    # `_mr1_1_2_6_r3_g`). The corrupted names are never matchdeclare'd
    # (the decls use cap_name), so Maxima read them as LITERAL symbols
    # and every rule carrying an `r` capture matched no integrand — all
    # of 1.2.4.1/1.2.4.2 dead, 138 rules across 17 files. translate()
    # already consumes every v_ / v_. marker (and raises on a stray one),
    # so the pattern needs no optional-dropping at all.
    pat_text = translate(m.group(1), ctx)
    # Guard the class, not just this instance: every _mr* token in the
    # emitted pattern must be one of THIS rule's declared captures or
    # MatchQ markers — a corrupted/foreign name can never match.
    expected = {cap_name(key, n, v) for v in rule_vars} | set(ctx["decls"])
    for tok in re.findall(r"_mr[0-9A-Za-z_]*", pat_text):
        if tok not in expected:
            raise GenError(f"{key} r{n}: pattern token {tok!r} is not a "
                           f"declared capture or MatchQ marker of this "
                           f"rule (name corruption in the pattern text)")
    # Leading coefficients of degree>=2 polynomial factors (and symbolic
    # exponents) must be nonzero: see nonzero_guard_caps (the Maxima
    # degenerate-0-binding misfire).
    leadcaps = nonzero_guard_caps(pat_text)
    # declare each capture; freeof(x)-guarded if the cond has FreeQ[..., x].
    # FIX F4: the brief did set(re.findall(...)).split(",") — a set has no
    # split; split the group strings instead.
    freeq_guarded = set(v.strip()
                        for part in re.findall(r"FreeQ\[\{?([^}]*)\}?,\s*x\]",
                                               cond or "")
                        for v in part.split(","))
    decls = []
    for v in sorted(rule_vars):
        pred = "freeof(x)" if v in freeq_guarded else "true"
        decls.append(f"matchdeclare({cap_name(key, n, v)}, {pred})$")
    for d in sorted(ctx["decls"]):
        decls.append(f"matchdeclare({d}, true)$")
    # cond: translate; an empty cond -> true. A rule whose pattern can
    # degenerate-bind a leading coeff / symbolic exponent to 0 (see
    # nonzero_guard_caps) gets %mr_neQ(<cap>, 0) appended: evaluated once in
    # the cond per matched rule (a regular function) rather than as a match-
    # time matchdeclare lambda, which the 2026-08-24 e8 timing showed pushes
    # hard quartics past the 30 s cap (13.4 s -> 30 s).
    base_cond = (translate(drop_optionals(cond, rule_vars), ctx)
                 if cond else "true")
    if leadcaps:
        guards = "  and  ".join(f"%mr_neQ({c}, 0)"
                                for c in sorted(leadcaps))
        cond_txt = f"({base_cond})  and  {guards}"
    else:
        cond_txt = base_cond
    # FIX F12: the brief passed `varset` here — an undefined name in
    # emit_rule (the parameter is rule_vars); a NameError on every rule.
    repl_txt = translate(drop_optionals(rhs, rule_vars), ctx)
    # FIX F13: the brief bound the BARE capture names (a : geteqR(mm,
    # '_mr_…_a')) while the translated cond/repl read the RENAMED names —
    # the cond would then evaluate on unbound symbols (freeof vacuously
    # true) and the repl on symbols instead of the captured values. Bind
    # the renamed names, the ones the bodies actually reference.
    # The geteqR name argument uses the UNBALANCED Rubi quote idiom
    # geteqR(mm, 'name) — NO closing quote. Measured 2026-08-20
    # (branch_5_49_base_796_g60186bb22_dirty, nparse.lisp): this build's
    # quote NUD (def-nud |$'|) parses the quoted operand at lbp 190, which
    # stops after the atom and never consumes a closing quote; a balanced
    # 'name' leaves the closing ' in the input and raises
    # "' is not an infix operator" (repro: `t : 'v'$` fails; the brief's
    # own loader line uses the unbalanced idiom, as do the committed
    # Task-3 rules, which the 20/20 suite verifies behaviorally).
    caps = sorted(cap_name(key, n, v) for v in rule_vars)
    binds = [f"{c} : geteqR(mm, '{c})" for c in caps]
    bind_block = ", ".join(binds) if binds else "true"
    # FIX F5: the block locals are the renamed captures; the brief listed
    # the bare names, which are dead locals there (and would shadow the
    # mm/x parameters if a capture were ever named mm or x).
    locals_txt = ", ".join(caps) if caps else ""
    # Capture snapshots (2026-08-25, e44 wrong-answer fix). Maxima block
    # scoping is DYNAMIC, and a defmatch matcher assigns the pattern
    # symbols as a side effect of every match attempt. A repl whose body
    # makes a nested mr_int call re-dispatches the whole rule list, which
    # re-matches THIS rule's own pattern against the cascade's
    # intermediate integrands and clobbers the capture bindings the repl
    # still reads after the nested call. Measured on e44 (1.2.2.5 r3):
    # the even-part cascade rebound _mr_1_2_2_5_r3_b/_mr_1_2_2_5_r3_c to
    # -240/348 (a matched intermediate quartic 348x^4-240x^2+4), and the
    # odd-part integrand was then built from the wrong quartic — a
    # non-antiderivative answer that the zero-test rightly rejects. The
    # matchlist mm is an immutable value, so the repl reads each capture
    # from mm into a fresh local no matcher can assign and the body is
    # rewritten to those locals. The cond keeps the capture names: it
    # runs before any nested dispatch and its predicates never re-match
    # this rule's pattern. The __s suffix cannot collide: a capture name
    # is strictly shorter than its snapshot, and a Rubi variable named
    # v__s would be asserted against below.
    snaps = {c: c + "__s" for c in caps}
    if set(snaps.values()) & set(caps):
        raise GenError(f"{key} r{n}: a snapshot name collides with a "
                       f"capture name (a Rubi variable named __s?)")
    for c in caps:
        repl_txt = re.sub(
            r"(?<![0-9A-Za-z_])" + re.escape(c) + r"(?![0-9A-Za-z_])",
            snaps[c], repl_txt)
    snap_binds = [f"{snaps[c]} : geteqR(mm, '{c})" for c in caps]
    snap_bind_block = ", ".join(snap_binds) if snap_binds else "true"
    snap_locals_txt = ", ".join(snaps[c] for c in caps) if caps else ""
    pat_name = f"_mr_pat_{key}_r{n}"
    lines = list(decls)
    lines.append(f"defmatch({pat_name}, {pat_text}, x)$")
    lines.append(f"_mr_cond_{key}_r{n}(mm, x) := block([{locals_txt}],")
    lines.append(f"  {bind_block},")
    lines.append(f"  {cond_txt})$")
    lines.append(f"_mr_repl_{key}_r{n}(mm, x) := block([{snap_locals_txt}],")
    lines.append(f"  {snap_bind_block},")
    lines.append(f"  {repl_txt})$")
    lines.append(f"_mr_rule_{key}_r{n}(f, x) := block([mm, ok],")
    lines.append(f"  mm : {pat_name}(f, x),")
    lines.append("  if mm = false then return(false),")
    lines.append(f"  ok : _mr_cond_{key}_r{n}(mm, x),")
    lines.append(f"  if is(ok) = true then _mr_repl_{key}_r{n}(mm, x) else false)$")
    return "\n".join(lines)

def emit_file(rel_m, runs, key=None):
    # key defaults to the file's own number; the EXTRA_CLASS1 files
    # (measured 2026-08-25) are emitted under a `<key>b` suffix so their
    # rule names never collide with the same-numbered LoadRules sibling.
    if key is None:
        key = key_of(rel_m)
    header = (f"/* rules/class1/{key}.mac — GENERATED; do not edit.\n"
              f" * Source: Rubi 4 {PIN}\n"
              f" *          {rel_m}\n * Regenerate: "
              f"python3 generator/generate_class1.py --only {key} */\n"
              f"{MIT}\n\n")
    body = []
    rule_fns = []
    for n, run in enumerate(runs, start=1):
        # FIX F3: rule_runs yields LISTS OF LINES; the brief's emit_rule
        # unpacked them as a (lhs, rhs, cond) triple (ValueError on any
        # single-line rule) and pattern_vars(run[0]) saw only line 1. Join
        # the run and split it the way the census does.
        text = "\n".join(run)
        if ":=" not in text:
            raise GenError(f"{key} r{n}: unparseable rule run (no ':='): "
                           f"{text[:60]!r}")
        # 5 class-1 runs glue an inline C-tier utility definition
        # (IntLinearQ/IntBinomialQ/IntQuadraticQ) onto the rule run. The
        # definition is provenance: its port is Task 7 (%mr_intLinearQ &
        # co. in maxima_rubi_utils.mac); the rule conds call those %mr_*
        # names, which are nouns until then, so the affected rules decline
        # (is(noun) = false) — the same deliberate dead state a C-tier
        # predicate without its port gives.
        text, util_lines = split_utility_def(text)
        if any("*/" in ln for ln in util_lines):
            raise GenError(f"{key} r{n}: utility definition contains "
                           f"'*/' (would terminate the provenance comment)")
        lhs, rhs, cond = split_rule_outer(text)
        cond = clean_cond(cond, key, n)
        rule_vars = pattern_vars(lhs)
        try:
            body.append(emit_rule((lhs, rhs, cond), key, n, rule_vars))
        except GenError:
            raise
        except Exception as ex:
            # any other crash is a generator defect: name the file, rule
            # and lhs, exit nonzero.
            raise GenError(f"{key} r{n}: {type(ex).__name__}: {ex} "
                           f"(lhs {lhs[:60]!r})") from ex
        if util_lines:
            body.append("/* Inline Rubi utility definition (C-tier; ported in Task 7")
            body.append(" * as the corresponding %mr_* predicate). Until then, any")
            body.append(" * rule calling it either declines (call in a cond) or")
            body.append(" * returns a noun-laden answer (call in a repl):")
            for ln in util_lines:
                body.append(f" * {ln.strip()}")
            body.append(" */")
        rule_fns.append(f"_mr_rule_{key}_r{n}")
        body.append("")
    body.append(f"mr_rules_{key} : [ {', '.join(rule_fns)} ]$")
    body.append(f"mr_rules_count_{key} : {len(runs)}$")
    body.append(f"mr_witness_{key}() := true$")
    return header + "\n".join(body) + "\n"

def load_class1_files(rubi):
    """The 67 class-1 .m files, in Rubi.m LoadRules order, as paths relative
    to the Rubi clone root. parse_load_rules yields (parts, gated); the parts
    are relative to IntegrationRules/ and lack the .m extension (LoadRules
    appends it). Only the non-gated (mandatory) class-1 files are ported."""
    order = parse_load_rules((rubi / "Rubi" / "Rubi.m").read_text())
    out = []
    for parts, gated in order:
        if gated:
            continue                      # $LoadElementaryFunctionRules block
        if not parts or not parts[0].startswith("1 "):
            continue                      # class 1 only
        rel = "Rubi/IntegrationRules/" + "/".join(parts) + ".m"
        out.append(rel)
    return out

# Class-1 .m files ABSENT from Rubi.m's LoadRules that the Maxima-syntax
# corpus nonetheless tests (measured 2026-08-25): the 1.2.1.3/.4/.5/.6/.9
# corpus files name-match exactly these five dead .m files, while Rubi.m
# loads the same-numbered SIBLINGS instead (e.g. Rubi.m:145 loads
# "1.2.1.4 (a+b x+c x^2)^p (d+e x+f x^2)^q" — 35 rules — and the corpus
# "1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p.mac" — 958 entries — needs
# the 122-rule dead sibling). The generator's key_of collision made the
# loaded sibling win the shared key, so these five were silently never
# ported and their corpus entries mass-deferred. Ported under a `b` key
# suffix, table position right after the same-numbered sibling (Rubi
# family-block order). The other dead class-1 files (1.2.1.7/1.2.1.8
# siblings, the four 1.3.x files, 1.1.2.x/.y) have NO corpus file and
# stay unported until the full-corpus run shows deferral that needs them.
_QD = ("Rubi/IntegrationRules/1 Algebraic functions/"
       "1.2 Trinomial products/1.2.1 Quadratic/")
EXTRA_CLASS1 = [
    _QD + "1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p.m",
    _QD + "1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p.m",
    _QD + "1.2.1.5 (a+b x+c x^2)^p (d+e x+f x^2)^q.m",
    _QD + "1.2.1.6 (g+h x)^m (a+b x+c x^2)^p (d+e x+f x^2)^q.m",
    _QD + "1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p.m",
]
EXTRA_TOTAL = 316  # 82 + 122 + 31 + 48 + 33 (measured 2026-08-25)


def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].replace(".", "_")
    files = load_class1_files(RUBI)
    total = 0
    load_lines, table_terms = [], []
    for rel_m in files:
        key = key_of(rel_m)
        if only and key != only:
            continue
        text = strip_comments((RUBI / rel_m).read_text())
        runs = rule_runs(text)
        out = OUT / f"{key}.mac"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(emit_file(rel_m, runs))
        print(f"  {key}: {len(runs)} rules")
        total += len(runs)
        load_lines.append(
            f"%mr_load_sibling(\"rules/class1/{key}.mac\", "
            f"'mr_witness_{key})$")
        table_terms.append(f"mr_rules_{key}")
    # The five corpus-tested dead siblings (EXTRA_CLASS1), `b`-suffixed,
    # table position immediately after their same-numbered sibling.
    for rel_m in EXTRA_CLASS1:
        if not (RUBI / rel_m).exists():
            raise GenError(f"EXTRA_CLASS1 file missing: {rel_m}")
        base = key_of(rel_m)
        key = base + "b"
        if only and key != only:
            continue
        text = strip_comments((RUBI / rel_m).read_text())
        runs = rule_runs(text)
        out = OUT / f"{key}.mac"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(emit_file(rel_m, runs, key))
        print(f"  {key}: {len(runs)} rules (extra, corpus-matched dead file)")
        total += len(runs)
        load_lines.append(
            f"%mr_load_sibling(\"rules/class1/{key}.mac\", "
            f"'mr_witness_{key})$")
        sib = f"mr_rules_{base}"
        pos = table_terms.index(sib) + 1 if sib in table_terms \
            else len(table_terms)
        table_terms.insert(pos, f"mr_rules_{key}")
    expected = 2710 + EXTRA_TOTAL
    note = (f"OK (== {expected})" if (total == expected and not only)
            else ("partial (--only)" if only
                  else f"MISMATCH (expected {expected})"))
    print(f"TOTAL: {total} rules — {note}")
    if not only and total != expected:
        raise GenError(f"rule total {total} != {expected} "
                       "(2710 T1 census + 316 EXTRA_CLASS1); aborting")
    if not only:
        print()
        print("# maxima_rubi.mac load list (Rubi LoadRules order):")
        for line in load_lines:
            print(line)
        # flatten([...]), not "a concat b": concat is an atom/STRING
        # function in this build ("concat: argument must be an atom",
        # measured 2026-08-20) and `++` parses as two unary pluses;
        # flatten of a list of flat lists is the list concatenation.
        print("mr_rule_table : flatten(["
              + ", ".join(table_terms) + "])$")

if __name__ == "__main__":
    main()
