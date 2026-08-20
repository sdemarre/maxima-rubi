#!/usr/bin/env python3
"""generate_class1.py — emit rules/class1/*.mac from Rubi 4's class-1 .m files.

Only the files Rubi.m actually LoadRules() (67 files, 2,710 rules — the T1
count; 22 stale on-disk files are skipped by construction). Usage:
    python3 generator/generate_class1.py [--only 1.1.1.1]
Fails loudly (exit 1, file+rule+token named) on an unlisted token, an
unparseable rule run, or a pattern variable it cannot rename.
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
rule_runs, split_rule = _cen.rule_runs, _cen.split_rule

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
    from matchdeclare, not from the leading underscore).
    """
    return f"_mr_{key}_r{n}_{v}"

_IDCH = ("0123456789abcdefghijklmnopqrstuvwxyz"
         "ABCDEFGHIJKLMNOPQRSTUVWXYZ_")

def _join_tokens(tokens):
    """Join the atom-walk tokens into one Maxima expression.

    FIX F6: the brief's `" ".join(out)` put a space between EVERY token
    (single characters included): `1/x` -> `1 / x`, a decimal `1.5` ->
    `1 . 5` (a Maxima parse error). Concatenate by default — the original
    spacing survives as tokens where it was not consumed by a marker — and
    insert a space only where gluing would (a) merge two identifiers into
    one, (b) turn `x (…)`-style juxtaposition into a call, or (c) turn
    `(…) x` / `[…] x` into a parse error / noun form.
    """
    out = ""
    for t in tokens:
        if not t:
            continue
        if not out:
            out = t
        elif out[-1] == " " or t[0] == " ":
            out += t
        else:
            a, b = out[-1], t[0]
            if ((a in _IDCH and b in _IDCH) or (a in _IDCH and b in "([")
                    or (a in ")]" and b in _IDCH)):
                out += " " + t
            else:
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

def drop_optionals(text, varset):
    """v_. and v_ -> the renamed capture (the plain pattern; the matcher's
    decomposition fills the Plus/Times identity defaults). Power-optional
    exponents are D-duplicated at the emit level, not here.

    Defensive: the translate_atom walk already consumes every v_ / v_.
    marker, so this is a no-op on translated text; it guards a raw call."""
    for v in sorted(varset, key=len, reverse=True):
        text = text.replace(v + "_.", v).replace(v + "_", v)
    return text

def translate_token(tok, key, n, varset):
    """A bare identifier -> renamed capture / table name / itself.
    Unknown tokens pass through here (legit constants/renamed vars in atom
    position); an unlisted HEAD is rejected loudly at the emit_head
    boundary, not here."""
    if tok in varset:
        return cap_name(key, n, tok)
    if tok in ("x", "Pi", "E", "I"):
        return tok
    if tok in RENAME or tok in RESTRUCTURE:
        return table_translate(tok)
    # unknown identifier that is not a capture: a Maxima symbol (a, b, c, …)
    # appearing in a cond/rhs but not the lhs — pass through.
    return tok

def translate(s, key, n, varset):
    """Recursive translator: .m expression -> Maxima expression.

    Walks a token stream; on `head[args]` it translates each top-level arg
    and applies the head's special form (FreeQ arg-flip, Int -> mr_int,
    With/Module -> block, the cmp family -> is(), Hypergeometric2F1 list
    form). Atoms rename captures and drop optionals.
    """
    s = s.strip()
    head, args = head_args(s)
    if head is not None:
        arglist = [translate(a, key, n, varset)
                   for a in split_top(args, ",")] if args.strip() else []
        return emit_head(head, arglist, key, n, varset)
    return translate_atom(s, key, n, varset)

def emit_head(head, arglist, key, n, varset):
    """Special forms first, then a plain renamed head(arglist)."""
    if head == "FreeQ":
        # FreeQ[e, x] -> freeof(x, e); FreeQ[{a,b}, x] -> and of freeof.
        # (FIX F7) the arg list may arrive as [a, b] (braces already
        # converted by translate_atom) or still as {a, b}.
        e, xv = arglist[0], arglist[1]
        if e.startswith("{") or e.startswith("["):
            e = e[1:-1]
        parts = [f"freeof({xv}, {p.strip()})" for p in split_top(e, ",")]
        return " and ".join(parts)
    if head in ("GtQ", "LtQ", "LeQ", "GeQ", "IGtQ", "ILtQ", "ILeQ"):
        op = {"GtQ": ">", "LtQ": "<", "LeQ": "<=", "GeQ": ">=",
              "IGtQ": ">", "ILtQ": "<", "ILeQ": "<="}[head]
        return f"is({arglist[0]} {op} {arglist[1]})"
    if head in ("Int", "IntHide"):
        return f"mr_int({arglist[0]}, {arglist[1]})"
    if head in ("Unintegrable", "CannotIntegrate"):
        return f"mr_unintegrable({arglist[0]}, {arglist[1]})"
    if head == "With" or head == "Module":
        # With[{a = e}, body] / Module[{a = e}, body] -> block([a], a : e, body)
        decls = arglist[0][1:-1]          # strip { }
        body = arglist[1]
        pairs = split_top(decls, ",")
        locals_, assigns = [], []
        for p in pairs:
            name, val = [q.strip() for q in split_top(p, "=")]
            rn = translate_token(name, key, n, varset)
            locals_.append(rn)
            assigns.append(f"{rn} : {translate(val, key, n, varset)}")
        return (f"block([{', '.join(locals_)}], "
                + ", ".join(assigns) + ", "
                + translate(body, key, n, varset) + ")")
    if head == "If":
        return f"if {arglist[0]} then {arglist[1]} else {arglist[2]}"
    if head == "Boole":
        return f"if {arglist[0]} then 1 else 0"
    if head == "Hypergeometric2F1":
        a, b, c, z = arglist
        return f"hypergeometric([{a}, {b}], [{c}], {z})"
    if head in ("EllipticF", "EllipticE", "EllipticPi"):
        fn = {"EllipticF": "mr_elliptic_f", "EllipticE": "mr_elliptic_e",
              "EllipticPi": "mr_elliptic_pi"}[head]
        return f"{fn}({', '.join(arglist)})"
    # A head absent from the table is a census miss: fail LOUDLY, never emit
    # a bare Maxima noun FooQ(...) — that makes is(ok) = true perpetually
    # false (a silently dead rule) or a silently noun-laden wrong answer.
    # The atom-position pass-through (translate_atom) is a separate,
    # legitimate path for constants/renamed vars, so the check lives here at
    # the head boundary, not in translate_token.
    if (head not in RENAME and head not in RESTRUCTURE
            and head not in ("x", "Pi", "E", "I")):
        raise GenError(f"{key} r{n}: unlisted head {head!r} — extend the "
                       f"translation table (T4 §2) before generating")
    name = translate_token(head, key, n, varset)
    # FIX F2: Maxima function calls use parentheses; the brief emitted the
    # Mathematica bracket form name[args], which is a parse error / noun
    # form in Maxima.
    return f"{name}({', '.join(arglist)})"

def translate_atom(s, key, n, varset):
    """A non-`head[...]` expression: rename captures, drop optionals,
    rewrite && / || / Not, and translate any nested head[args]
    sub-expressions. Works on a token walk so nested heads inside
    sums/products are handled."""
    out, i, L = [], 0, len(s)
    while i < L:
        m = re.match(r"[A-Za-z][A-Za-z0-9]*", s[i:])
        if m:
            name = m.group()
            j = i + len(name)
            # `x_Symbol` -> x (the pattern argument). FIX F10: require
            # name == "x" — a capture named xs_ followed by _Symbol must
            # not be swallowed as the integration variable.
            if name == "x" and s[j:j+8] == "_Symbol":
                out.append("x"); i = j + 8; continue
            # a capture named like the integration variable is the integration
            # variable (Mathematica same-named patterns must agree): `x_` -> x,
            # consuming the marker, no matchdeclare (see Generator algorithm 2).
            if name == "x" and s[j:j+2] in ("_.", "_ "):
                out.append("x"); i = j + 2; continue
            if name == "x" and s[j:j+1] == "_":
                out.append("x"); i = j + 1; continue
            # a free capture with an optional marker: v_. or v_
            if name in varset and s[j:j+2] in ("_.", "_ "):
                out.append(cap_name(key, n, name))
                i = j + 2; continue
            if name in varset and s[j:j+1] == "_":
                out.append(cap_name(key, n, name))
                i = j + 1; continue
            # FIX F11: a pattern-variable marker on a name the lhs census
            # did not record (e.g. a typed _Integer pattern) is a variable
            # the emitter cannot rename — fail loudly, never emit a bare
            # underscore that Maxima would read as a fresh pattern variable.
            if s[j:j+1] == "_":
                raise GenError(f"{key} r{n}: pattern variable {name!r} "
                               f"cannot be renamed (captures: "
                               f"{sorted(varset)})")
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
                out.append(translate(name + "[" + argtxt + "]", key, n, varset))
                i = t + 1; continue
            out.append(translate_token(name, key, n, varset)); i = j; continue
        if s[i:i+2] == "&&":
            out.append(" and "); i += 2; continue
        if s[i:i+2] == "||":
            out.append(" or "); i += 2; continue
        ch = s[i]
        # FIX F7: Mathematica list braces are Maxima brackets.
        if ch == "{":
            out.append("["); i += 1; continue
        if ch == "}":
            out.append("]"); i += 1; continue
        out.append(ch); i += 1
    return _join_tokens(out)

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

def emit_rule(run, key, n, rule_vars):
    """One rule run (lhs, rhs, cond) -> the five Maxima functions as text.
    rule_vars is the set of capture names (from the lhs)."""
    lhs, rhs, cond = run
    # integrand pattern: strip Int[ ... , x_Symbol]
    m = re.match(r"^Int\[(.*),\s*x_Symbol\]$", lhs.strip(), re.DOTALL)
    if not m:
        raise GenError(f"{key} r{n}: cannot strip Int[...]: {lhs!r}")
    pat_text = drop_optionals(translate(m.group(1), key, n, rule_vars),
                              rule_vars)
    # declare each capture; freeof(x)-guarded if the cond has FreeQ[... , x].
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
    # cond: translate; an empty cond -> true
    cond_txt = (translate(drop_optionals(cond, rule_vars), key, n, rule_vars)
                if cond else "true")
    # FIX F12: the brief passed `varset` here — an undefined name in
    # emit_rule (the parameter is rule_vars); a NameError on every rule.
    repl_txt = translate(drop_optionals(rhs, rule_vars), key, n, rule_vars)
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
    binds = [f"{cap_name(key, n, v)} : geteqR(mm, '{cap_name(key, n, v)})"
             for v in sorted(rule_vars)]
    bind_block = ", ".join(binds) if binds else "true"
    # FIX F5: the block locals are the renamed captures; the brief listed
    # the bare names, which are dead locals there (and would shadow the
    # mm/x parameters if a capture were ever named mm or x).
    locals_txt = ", ".join(cap_name(key, n, v) for v in sorted(rule_vars))
    pat_name = f"_mr_pat_{key}_r{n}"
    lines = list(decls)
    lines.append(f"defmatch({pat_name}, {pat_text}, x)$")
    lines.append(f"_mr_cond_{key}_r{n}(mm, x) := block([{locals_txt}],")
    lines.append(f"  {bind_block},")
    lines.append(f"  {cond_txt})$")
    lines.append(f"_mr_repl_{key}_r{n}(mm, x) := block([{locals_txt}],")
    lines.append(f"  {bind_block},")
    lines.append(f"  {repl_txt})$")
    lines.append(f"_mr_rule_{key}_r{n}(f, x) := block([mm, ok],")
    lines.append(f"  mm : {pat_name}(f, x),")
    lines.append("  if mm = false then return(false),")
    lines.append(f"  ok : _mr_cond_{key}_r{n}(mm, x),")
    lines.append(f"  if is(ok) = true then _mr_repl_{key}_r{n}(mm, x) else false)$")
    return "\n".join(lines)

def emit_file(rel_m, runs):
    key = key_of(rel_m)
    header = (f"/* rules/class1/{key}.mac — GENERATED; do not edit.\n"
              f" * Source: Rubi 4 {PIN}\n"
              f" *          {rel_m}\n * Regenerate: "
              f"python3 generator/generate_class1.py --only {key_of(rel_m)} */\n"
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
        lhs, rhs, cond = split_rule(text)
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

def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].replace(".", "_")
    files = load_class1_files(RUBI)
    total = 0
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
    note = "OK (== 2710)" if (total == 2710 and not only) else \
           ("partial (--only)" if only else f"MISMATCH (expected 2710)")
    print(f"TOTAL: {total} rules — {note}")
    if not only and total != 2710:
        raise GenError(f"rule total {total} != 2710 (T1 census); aborting")

if __name__ == "__main__":
    main()
