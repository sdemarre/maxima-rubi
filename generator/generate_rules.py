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
OUT = ROOT / "rules" / "class1"   # set by configure(); class-1 default
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

# Values in the translation table that name an EMITTER CASE rather than a
# Maxima function. Reaching the generic `name(args)` emission with one of
# these means a table row exists whose handler nobody implemented — the
# class-6 `Integral -> "noun"` row did exactly that on 2026-09-20 and
# produced `noun(expr, x)` in 8 rules. Guarded at the head boundary below.
HANDLER_ONLY = frozenset({"noun", "block", "cmp", "if", "switch",
                          "loggamma", "power", "plus", "times",
                          "polygamma", "zeta", "derivative"})
import mma_reader as rd  # the evaluated-FullForm reader (spec 3.4)
from fractions import Fraction

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
    and `(x) (y)`, `(n - j) (p + 1)`, `[1] (2)` parse as an application
    of the left term to the right one, not a product: `(x) (y)` is the
    noun call x(y), and `(n - j) (p + 1)` on numbers is an evaluation
    error (probes/matcher/12-translation-defects MUL, 2026-09-14; the
    2026-08-22 note that `(x) (y)` is a product was wrong -- 1_1_4_1 r1's
    repl errored at runtime).
    So a gap whose both sides are expression terminals becomes an
    explicit `*`, `)`/`]` followed by `(` included. A Maxima word on
    either side of the gap (and/or/...)
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
    if L in ")]" and (R in _IDSTART or R.isdigit() or R == "%" or R == "("):
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

def _split_top_args(s, sep=","):
    """Top-level split of s on sep, respecting [ ] ( ) { } nesting."""
    parts, depth, cur = [], 0, []
    for ch in s:
        if ch in "[({":
            depth += 1
        elif ch in "])}":
            depth -= 1
        if depth == 0 and ch == sep:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return parts

_SHOWSTEPS_IF = re.compile(
    r"^If\[TrueQ\[\$LoadShowSteps\],(.+)\]\s*$", re.DOTALL)

def unwrap_showsteps_line(line):
    """The single-line Rubi rule wrapper

        If[TrueQ[$LoadShowSteps], <ShowStep rule>, <plain rule>]

    (3.5.m L46 in class 3; the same shape in classes 4/5/7/9 is
    single-line there too) -> the NON-ShowSteps branch (the 3rd arg).
    Branch selection (class-3 deferred campaign C6b, decision recorded
    in .superpowers/sdd/t4c6b-report.md): in the port the two branches
    are semantically identical — the ShowStep branch's body VALUES to
    its 4th argument, the held answer, which is exactly the plain
    branch's body (the generator's ShowStep handler, FIX E4, emits the
    4th arg unwrapping %mr_hold), and its extra `SimplifyFlag &&` gate
    is mr_simplify_flag, constant true in the port
    (maxima_rubi_utils.mac:11; MA's own ShowStepRoutines.m:3 default,
    its Block[{SimplifyFlag=False}] scoping the step machinery only,
    which the port has none of). Porting both would add a byte-
    redundant u_ catch-all rule (same pattern, same effective cond,
    same repl) that every integrand reaching this position pays for in
    TLS slots and match time. (The 1.4.1 r7/r8 both-branches shape is
    a by-product of that file's multi-line formatting — each branch
    starts its own Int[-leading line and so its own run — not an
    intentional double port.) The multi-line form does NOT match here
    (the line carries no complete If), so the rule_runs convention
    still splits each branch into its own run and the line is left
    untouched. A line that is JUST the opener (the 1.4.1 multi-line
    shape) passes through untouched; any other line that starts the
    wrapper without carrying both branches to a closing ] is a parse
    failure, not a pass-through."""
    s = line.strip()
    if not s.startswith("If[TrueQ[$LoadShowSteps],"):
        return line
    m = _SHOWSTEPS_IF.match(s)
    if m is None:
        if re.fullmatch(r"If\[TrueQ\[\$LoadShowSteps\],\s*", s):
            return line
        raise GenError(f"ShowSteps If wrapper is not self-contained on "
                       f"one line (multi-line form?) — {s[:60]!r}")
    args = _split_top_args(m.group(1))
    if len(args) != 2:
        raise GenError(f"ShowSteps If wrapper has {len(args)} branches "
                       f"(expected 2): {s[:60]!r}")
    plain = args[1].strip()
    if not re.match(r"^Int\[[^\[\]]*,\s*x_Symbol\]\s*:=", plain):
        raise GenError(f"ShowSteps If plain branch is not an Int rule: "
                       f"{plain[:60]!r}")
    return plain

def unwrap_showsteps_lines(text):
    """Map unwrap_showsteps_line over the comment-stripped .m text."""
    return "\n".join(unwrap_showsteps_line(ln) for ln in text.split("\n"))

_COMMENT_ONLY_LINE = re.compile(r"\s*\(\*(?:(?!\*\)).)*\*\)\s*")

def drop_comment_only_lines(text):
    r"""Spec 2026-09-22 A2.1: a whole-line Mathematica comment (9.2 r12's
    `(* ILtQ[n,0] && ILtQ[m,0] || *)` inside a multi-line condition) is
    dropped ENTIRELY, not just its comment text -- strip_comments leaves a
    blank line in its place, and rule_runs splits a run at a blank line, so
    the condition would be cut in half. Applied to the raw .m text before
    strip_comments, for every class (measured neutral on classes 1/2/3/6,
    probe 08 part C; Step 5 re-proves it). An inline comment (anything else
    on the line besides the comment) is left untouched, for strip_comments
    to handle.

    Fix round 1 (task review finding 1): the regex's inner run is
    `(?:(?!\*\)).)*`, not a bare `.*` -- a bare `.*` is greedy across the
    WHOLE line, so `(* a *) code (* b *)` fullmatches (the `.*` swallows
    ` code (* b ` too) and the real code between the two comments is
    silently dropped. The negative-lookahead run stops at the FIRST `*)`,
    so the line only fullmatches when that first `*)` is also the last
    character run before end-of-line (mod trailing whitespace) -- i.e. the
    line is exactly one comment and nothing else, no second `*)` (comment
    or code) anywhere after it. No 9.2/9.3 source line has two comments on
    one line (checked, see the fix-round-1 report), so this had no
    observed case in the port; the fix guards the general function.

    Fix round 2 (final review, section-9 port): dropping a line -- rather
    than blanking it, as strip_comments would -- loses whatever separator
    role that line was playing. That is harmless when the comment sits
    INSIDE a rule whose brackets are not yet balanced (9.2 r12: the run so
    far is `FreeQ[m,x] && (`, an unclosed paren, so the rule plainly is
    not over) -- rule_runs was never going to see a legitimate boundary
    there anyway once the line is gone. It is NOT harmless when the
    comment sits between two rules whose brackets ARE balanced at that
    point (rule A is syntactically complete): there, dropping is safe
    only because the NEXT surviving line reopens its own run on the
    literal column-0 `Int[` marker, which forcibly closes whatever came
    before and starts fresh regardless of what got dropped. Two rules
    separated ONLY by a comment-only line (no blank line) rely on exactly
    that today (measured neutral on classes 1/2/3/4/6/9,
    test/check_generated_rules.py) -- but nothing requires the NEXT rule
    to be so well-behaved in classes not yet ported (5/7/8), e.g. an
    indented continuation that does not start with `Int[`. Guard it
    directly: walk the lines tracking bracket depth and whether the run
    in progress dangles on a bare ':=' (rule_runs' own exception, a
    comment between ':=' and the rhs); at a comment-only line where the
    enclosing rule is balanced and not dangling, dropping is safe only if
    the next surviving line starts with `Int[` -- otherwise two runs would
    be joined (or one silently lost), and that is a GenError, not a
    silent corruption."""
    lines = text.split("\n")
    is_comment = [bool(_COMMENT_ONLY_LINE.fullmatch(ln)) for ln in lines]
    if _drop_would_join_runs(lines, is_comment):
        raise GenError(
            "drop_comment_only_lines: a comment-only line sits between two "
            "balanced, non-dangling rule runs whose next line does not "
            "reopen on Int[ -- dropping it would join or lose a run")
    return "\n".join(ln for ln, c in zip(lines, is_comment) if not c)

_BRACKET_DELTA = {"[": 1, "(": 1, "{": 1, "]": -1, ")": -1, "}": -1}

def _bracket_delta(line):
    return sum(_BRACKET_DELTA.get(ch, 0) for ch in line)

def _drop_would_join_runs(lines, is_comment):
    """See drop_comment_only_lines' fix-round-2 note. `depth` tracks
    bracket balance since the run's own `Int[` opener; `dangling` mirrors
    rule_runs' "ends in a bare ':='" exception."""
    cur_open, depth, dangling = False, 0, False
    n = len(lines)
    for i, line in enumerate(lines):
        if line.startswith("Int["):
            cur_open, depth = True, _bracket_delta(line)
            dangling = line.rstrip().endswith(":=")
            continue
        if is_comment[i]:
            if cur_open and depth == 0 and not dangling:
                j = i + 1
                while j < n and is_comment[j]:
                    j += 1
                nxt = lines[j] if j < n else ""
                # Fix 2026-09-25 (class-8 port): the guard tripped on
                # shapes that join nothing, and --class 1 / --class 3
                # aborted, so the byte-identity gate could not run at all.
                # Measured over the pinned clone: 1.1.3.1 L82 (a
                # commented-out rule, then a BLANK line), 1.2.1.2 L78/L90
                # (a one-line comment, then a MULTI-line comment opening at
                # column 0) and 3.5 L45 (a comment, then the single-line
                # If[TrueQ[$LoadShowSteps], Int[...]] wrapper that
                # unwrap_showsteps_line reopens on Int[). A next line that
                # is blank once its comment text is stripped is the run
                # separator rule_runs honours; the ShowSteps wrapper opens
                # a run exactly as Int[ does.
                if (strip_comments(nxt).strip()
                        and not nxt.startswith("Int[")
                        and not nxt.startswith("If[TrueQ[$LoadShowSteps]")):
                    return True
                cur_open, depth, dangling = False, 0, False
            continue
        if not cur_open:
            continue
        if line.strip() == "" and depth == 0 and not dangling:
            cur_open, depth, dangling = False, 0, False
            continue
        depth += _bracket_delta(line)
        dangling = line.rstrip().endswith(":=")
    return False

_SHOWSTEPS_IF_MULTILINE = "If[TrueQ[$LoadShowSteps],"

def unwrap_showsteps_multiline(text):
    """Spec 2026-09-22 A2.2: the multi-line
        If[TrueQ[$LoadShowSteps],
        <blank>
        <ShowStep rule ending in ".../;\\nSimplifyFlag,">
        <blank>
        <plain rule>]
    wrapper (nine in 9.3) -- the single-line unwrapper above
    (unwrap_showsteps_line, class-3 decision C6b: keep the plain branch)
    does not see it. Reduces each wrapper to its plain branch, dropping one
    trailing ']' (the If's own closer) from the branch's last line.
    Scoped to class 9 in _emit_source: applied to class 1 it would drop
    1_4_1 r7, since that file's ShowSteps wrapper carries BOTH branches as
    separate rules (ticket 07) rather than this reduce-to-one shape."""
    lines = text.split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        if lines[i].strip() == _SHOWSTEPS_IF_MULTILINE:
            wrapper_start = i
            i += 1
            # Fix round 1 (task review finding 2): bounded -- an
            # unbounded `while not ...: i += 1` runs off the end of
            # `lines` (a raw IndexError) when a wrapper is missing its
            # `SimplifyFlag,` line; fail loudly instead.
            while i < n and not lines[i].strip().startswith("SimplifyFlag"):
                i += 1
            if i >= n:
                raise GenError(
                    "unwrap_showsteps_multiline: no 'SimplifyFlag' line "
                    "found after the If[TrueQ[$LoadShowSteps], wrapper "
                    f"opened at source line {wrapper_start + 1}")
            i += 1
            while i < n and not lines[i].strip():
                i += 1
            blk = []
            while i < n and lines[i].strip():
                blk.append(lines[i])
                i += 1
            if not blk or not blk[-1].rstrip().endswith("]"):
                raise GenError(
                    "unwrap_showsteps_multiline: the plain branch does not "
                    f"end in ']': {blk[-1] if blk else ''!r}")
            blk[-1] = blk[-1].rstrip()[:-1]
            out += blk
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)

def split_top_power(s):
    """(base, exp) if s is a top-level power `base^exp`; else (None, None)."""
    s = s.strip()
    pos = _find_top(s, lambda i, ch: ch == "^")
    if pos <= 0 or pos >= len(s) - 1:
        return (None, None)
    return (s[:pos].strip(), s[pos+1:].strip())

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
    if ctx.get("locals") and tok in ctx["locals"]:
        return ctx["locals"][tok]
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
    m = re.search(r"\[\[([0-9]+)\]\]$", s)
    if m:
        # Mathematica Part, single integer index, at bracket depth 0 of
        # the WHOLE expression: expr[[i]] -> part(expr, i). The prefix
        # must be non-empty and end at depth 0 (counting [({ up / ])})
        # down) so that an INNER index (f[g[[1]]] — ends in a plain ])
        # is left to the recursive arg translation (g[[1]] reaches
        # translate as a whole expression) and a bare list literal
        # ([[2]] — empty prefix) is not mistaken for a Part.
        #
        # The bare-name sites are class 2's uu[[1]] / uu[[2]] (the
        # Module locals of 2.1 r18 / 2.3 r10) and class 3's lst[[1..4]]
        # (3.5 r13's With local) — byte-identical under the
        # generalization. The depth-0 prefix is what admits the
        # CALL-then-Part shape 3.4 r1's RationalFunctionExponents[u,
        # x][[2]] (3.4 .m :4), which the old bare-name-only regex passed
        # through as literal [[2]] — a Maxima list subscript that
        # hard-errors ("subscript must be an integer; found: [2]",
        # measured 2026-08-29 on branch_5_50_base_84_g4204fb669 built
        # 2026-08-29 17:58:20 / SBCL 2.6.7), errcaught by the dispatcher
        # (utils %mr_dispatch) into a safe decline: the rule was DEAD
        # (recorded by the Task-4 review; fixed here).
        #
        # Safety (2026-08-29 grep of the pinned clone's class 1-3 rule
        # sources, comment-stripped): the only LIVE call-then-Part is
        # 3.4 r1 itself; the 1.1.3.2 .m :34 BinomialParts[u, x][[1..3]]
        # hit sits inside a (* ... *) comment the parser strips; classes
        # 1/2 use only the bare-name form — so the generalization is
        # ADDITIVE and the class-1/2 byte-identity gate must stay EMPTY.
        #
        # The [0-9]+ guard keeps nested/comma indices (u[[1, 2]]) from
        # matching: they fall through to head_args, where the trailing
        # part mis-parses the arg list and emit_head raises "unlisted
        # head" — loud, not a mis-emit.
        p = m.start()
        if s[:p].strip():
            depth = 0
            for ch in s[:p]:
                if ch in "[({":
                    depth += 1
                elif ch in "])}":
                    depth -= 1
            if depth == 0:
                return f"part({translate(s[:p].strip(), ctx)}, {m.group(1)})"
    head, args = head_args(s)
    if head is not None:
        if head in ("With", "Module") and ctx.get("prefix_locals"):
            # Every class (class 4 from final fix wave I2, ruling R28; all
            # classes from ticket 08): the With/Module locals are renamed _mr_<key>_r<n>_<name> throughout the
            # scope (decls and body) -- a pure alpha-renaming of the
            # emitted block. See _push_scope_locals.
            parts = split_top(args, ",") if args.strip() else []
            saved = _push_scope_locals(head, parts[0] if parts else "", ctx)
            try:
                arglist = [translate(a, ctx) for a in parts]
                return emit_head(head, arglist, ctx)
            finally:
                ctx["locals"] = saved
        if head == "Block":
            # Block[{$ShowSteps = False, $StepCounter = Null}, body] — the
            # one Block shape in the emitted rules (4_7_5 r71, the
            # Weierstrass record, inert-trig substrate Task 10), and
            # verbatim the body of Rubi's IntHide (IntegrationUtilityFunctions.m
            # L16-17), which the table already maps to plain mr_int. The two
            # globals belong to the ShowSteps machinery ($ShowSteps displays
            # steps, $StepCounter counts applied rules; ShowStepRoutines.m
            # L4, L225-239): the port has neither steps nor a counter (the
            # generator takes the non-ShowSteps branch of every
            # If[TrueQ[$LoadShowSteps], ...] wrapper), so binding them
            # changes nothing a rule can observe, and the port emits the
            # BODY alone — the IntHide precedent, not a silent drop. Any
            # other Block (other globals, other values) is a GenError: its
            # bindings might be observable.
            parts = split_top(args, ",") if args.strip() else []
            if len(parts) < 2:
                raise GenError(f"{ctx['key']} r{ctx['n']}: Block arity "
                               f"{len(parts)}")
            if re.sub(r"\s+", "", parts[0]) != \
                    "{$ShowSteps=False,$StepCounter=Null}":
                raise GenError(f"{ctx['key']} r{ctx['n']}: unlisted Block "
                               f"bindings {parts[0].strip()!r}")
            return translate(",".join(parts[1:]), ctx)
        if head == "MatchQ":
            # The pattern arg must be translated in the FRESH MatchQ
            # marker scope (_emit_matchq mints the names), not the outer
            # scope: pre-translating the args raises on the pattern's own
            # markers (a_ is no capture of the rule). Pass the RAW args.
            parts = split_top(args, ",") if args.strip() else []
            return _emit_matchq(parts, ctx)
        if head == "MemberQ":
            # MemberQ[{ArcSin, ArcCos, ...}, F] with F a function-valued
            # capture (3_1_5 r58/r59, 3_3 r58, 3_4 r37): the dispatcher
            # binds F to the Maxima operator symbol of the matched head
            # (maxima_rubi_dispatch.lisp mr-binding-value), the symbol the
            # typed native name reads as (asin reads as %asin), so the list
            # carries the native spellings — not the %mr_ shims the RENAME
            # table maps ArcSinh/ArcCosh/ArcTanh to (the corpus integrands
            # carry the natives; probed 2026-08-29 and 2026-09-13).
            parts = split_top(args, ",") if args.strip() else []
            heads = parts[0].strip() if len(parts) == 2 else ""
            names = ([h.strip() for h in heads[1:-1].split(",")]
                     if heads.startswith("{") and heads.endswith("}") else [])
            if (names and all(h in NATIVE_FUNCTION_HEADS for h in names)
                    and parts[1].strip() in ctx["vars"]):
                return (f"%mr_memberQ([{', '.join(NATIVE_FUNCTION_HEADS[h] for h in names)}], "
                        f"{cap_name(ctx['key'], ctx['n'], parts[1].strip())})")
        if ctx["markers"] is not None and head in ctx["markers"]:
            # Marker-as-head, cond side (the r96 F[x]): the whole
            # sub-expression is a bare MatchQ pattern variable applied
            # to args — a head-position marker reference inside the
            # condition. Emit the raw-marker application (args
            # translated in the marker scope); _emit_matchq's existing
            # \b...\b post-pass rewrites the name to %mr_mk(<marker>,
            # %mr_mqb) — the ( is a word boundary, so the rewrite is
            # safe. (The pattern text takes no post-pass and keeps the
            # marker literal — the shape the %mr_matchQ marker-head
            # case consumes. This build's defmatch rejects pattern
            # variables in head position, measured 2026-08-28.)
            arglist = ([translate(a, ctx)
                        for a in split_top(args, ",")]
                       if args.strip() else [])
            return f"{ctx['markers'][head]}({', '.join(arglist)})"
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
                # A pattern-variable marker in cond/repl text (patterns are
                # emitted by pattern_sexp / _emit_matchq, never translated):
                # the integration variable, then this rule's lhs captures.
                # FIX F11: a marker on a name in neither is a variable the
                # emitter cannot rename — fail loudly, never emit a bare
                # underscore that Maxima would read as a fresh pattern
                # variable.
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
                if ctx["markers"] and name in ctx["markers"]:
                    # Marker-as-head, cond side (the r96 F[x]): a MatchQ
                    # pattern variable referenced bare in the condition —
                    # emit the same raw-marker application (args
                    # translated in the marker scope). _emit_matchq's
                    # existing \b...\b post-pass then rewrites the name
                    # to %mr_mk(<marker>, %mr_mqb) — the ( is a word
                    # boundary, so the rewrite is safe (the pattern text
                    # takes no post-pass and keeps the marker literal).
                    args = ([translate(p, ctx)
                             for p in split_top(argtxt, ",")]
                            if argtxt.strip() else [])
                    out.append(ctx["markers"][name]
                               + "(" + ", ".join(args) + ")")
                    i = t + 1; continue
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
        # Rubi control globals ($UseGamma): `$` is not in the atom
        # alphabet above, so the name regex never sees the full token
        # and the RENAME lookup in translate_token cannot fire for it
        # (the key is "$UseGamma", the walker yields "UseGamma").
        # Rename the whole $-word here through the same table — the
        # SimplifyFlag precedent, whose bare-symbol case works via
        # translate_token. Any other $-word is an unlisted token:
        # fail loudly, never pass through (a raw $ in the output is
        # either a Maxima parse error or a silent global reference).
        if ch == "$":
            m2 = re.match(r"\$[A-Za-z][A-Za-z0-9]*", s[i:])
            if m2 is not None and m2.group(0) in RENAME:
                out.append(RENAME[m2.group(0)])
                i += m2.end()
                continue
            tok = m2.group(0) if m2 is not None else s[i:i+12]
            raise GenError(f"{ctx['key']} r{ctx['n']}: unlisted $-token "
                           f"{tok!r} — extend the translation table "
                           f"(T4 §2) before generating")
        out.append(ch); i += 1
    return _expand_chains(_join_tokens(out))

def _relation_items(s):
    """Partition the depth-0 text of s into a complete item sequence
    [start, end, kind]: relational ops ("op": = <= >= < > == #= != =!=),
    chain terminators ("stop": ';', ',', ' and ', ' or '), and the term
    runs between them ("term").

    Spec 2026-09-22 A2.3: `=!=` (Rubi's UnsameQ, 9.3's only use) is read as
    ONE three-character op, checked before the two-character ops below --
    without this, the walk reads it as the single-char op `=` followed by
    the two-char op `!=` (two adjacent "op" items, no "term" between them),
    which the `!=` lone-relation guard in _expand_chains then rejects as
    "outside a lone relation". `===` (SameQ) is a different three-character
    sequence (no `!`) and is untouched by this check."""
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
            if s[i:i+3] == "=!=":
                hit = (i, i + 3, "op")
            elif two in ("==", "#=", "<=", ">=", "!="):
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
    return items

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
    # FIX (spec 2026-09-22 A2.3): Rubi's `=!=` (UnsameQ), 9.3's only use
    # (the NormalizeIntegrand record `v=!=u`) -- a SYNTACTIC test, unlike
    # `!=` below (Unequal, a value test). `%mr_unsameQ(L, R)` is
    # `not is(L = R)` (maxima_rubi_utils.mac). Mirrors the `!=` pass
    # exactly -- same lone-relation guard, same spacing handling, loud on
    # `=!=` inside a chain (Mathematica's chained UnsameQ has no
    # class-1-9 site) -- and runs FIRST: its token is three characters, and
    # _relation_items reads it as one "op" item only when it is checked
    # ahead of the two-character `!=`/`==` ops (see _relation_items).
    items = _relation_items(s)
    for i in range(len(items) - 1, -1, -1):
        if items[i][2] != "op" or s[items[i][0]:items[i][1]] != "=!=":
            continue
        if not (0 < i < len(items) - 1 and items[i-1][2] == "term"
                and items[i+1][2] == "term") \
                or (i >= 2 and items[i-2][2] == "op") \
                or (i + 2 < len(items) and items[i+2][2] == "op"):
            raise GenError(f"`=!=` outside a lone relation: {s!r}")
        lt = s[items[i-1][0]:items[i-1][1]]
        rt = s[items[i+1][0]:items[i+1][1]]
        s = (s[:items[i-1][0]] + lt[:len(lt) - len(lt.lstrip())]
             + "%mr_unsameQ(" + lt.strip() + ", " + rt.strip() + ")"
             + rt[len(rt.rstrip()):] + s[items[i+1][1]:])
    # FIX (matcher translation fixes design 3.1): Mathematica's `!=`
    # (Unequal) passed through the walk as the characters `!` `=`, which
    # Maxima reads as a factorial and an equation -- `k != 1` is `k! = 1`
    # (probes/matcher/12-translation-defects NE). A relation whose operator
    # is `!=` becomes notequal(L, R): numbers compare by value, a symbolic
    # operand gives unknown, which the dispatcher rejects (it accepts only
    # is(r) = true). A lone relation is left untouched by the chain pass
    # below, so this pass runs first, right to left (a rewrite shifts only
    # the items already done). `!=` inside a chain has no class 1-3 site
    # (Mathematica's chained Unequal means all-distinct, not the
    # conjunction) and fails loudly. The spacing outside the relation is
    # kept.
    items = _relation_items(s)
    for i in range(len(items) - 1, -1, -1):
        if items[i][2] != "op" or s[items[i][0]:items[i][1]] != "!=":
            continue
        if not (0 < i < len(items) - 1 and items[i-1][2] == "term"
                and items[i+1][2] == "term") \
                or (i >= 2 and items[i-2][2] == "op") \
                or (i + 2 < len(items) and items[i+2][2] == "op"):
            raise GenError(f"`!=` outside a lone relation: {s!r}")
        lt = s[items[i-1][0]:items[i-1][1]]
        rt = s[items[i+1][0]:items[i+1][1]]
        s = (s[:items[i-1][0]] + lt[:len(lt) - len(lt.lstrip())]
             + "notequal(" + lt.strip() + ", " + rt.strip() + ")"
             + rt[len(rt.rstrip()):] + s[items[i+1][1]:])
    # A chain is a run  TERM OP TERM OP ... OP TERM  with 2+ ops (k ops ->
    # k+1 terms); spans never overlap, so forward rewriting is
    # position-stable within the scan.
    items = _relation_items(s)
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
        # a leading _ too: class 4's prefixed locals (_mr_<key>_r<n>_d,
        # final fix wave I2) are statement targets in 4.7.5 r71's Module
        m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)", seg)
        if m:
            seg = m.group(1) + " :" + seg[m.end():]
        segs.append(seg)
    return ", ".join(segs)

CMP_OPS = {"GtQ": ">", "LtQ": "<", "LeQ": "<=", "GeQ": ">="}

# Rubi :379-:395  IGtQ[u_,n_] := IntegerQ[u] && u>n, likewise ILtQ, IGeQ,
# ILeQ: the integer test is part of the predicate. The heads translate to
# named utils entries (maxima_rubi_utils.mac %mr_iGtQ ...), never to a bare
# is(u > n), which dropped the test (matcher translation fixes design 3.1;
# probes/matcher/12-translation-defects IGT). IGeQ has no class 1-3 site.
INT_CMP = {"IGtQ": "%mr_iGtQ", "ILtQ": "%mr_iLtQ", "ILeQ": "%mr_iLeQ",
           "IGeQ": "%mr_iGeQ"}

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

def _emit_gamma(arglist, key, n):
    """Gamma arity dispatch (milestone-3 Task 2): 1-arg Gamma[v] ->
    gamma (the complete gamma function — class 3's 3.5 pattern
    Log[Gamma[v_]] and repl Log[Gamma[v]]), 2-arg Gamma[a, z] ->
    gamma_incomplete (the class-2 behavior, byte-unchanged: all 5/5
    class-2 uses are 2-arg UPPER). Any other arity is a GenError — the
    PolyQ dispatch's failure mode (file/rule/token named), never a
    silent pass-through (a wrong-arity Maxima call would be a noun).
    Probed 2026-08-29 on branch_5_50_base_84_g4204fb669: gamma bound
    (ev(gamma(0.5)) = 1.772453850905516), diff(log(gamma(x)),x) =
    psi[0](x) closing under ratsimp; gamma_incomplete(a,z) 2-arg UPPER
    with diff = -z^(a-1) %e^-z closing."""
    if len(arglist) == 1:
        return f"gamma({arglist[0].strip()})"
    if len(arglist) == 2:
        return (f"gamma_incomplete({arglist[0].strip()}, "
                f"{arglist[1].strip()})")
    raise GenError(f"{key} r{n}: Gamma arity {len(arglist)}")

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

# --- Patterns as evaluated FullForm s-expressions (matcher substrate spec
# docs/superpowers/specs/2026-09-12-matcher-substrate-design.md section
# 3.4). The reader (generator/mma_reader.py) parses a pattern text and
# emulates Mathematica's evaluation of it; maxima_rubi_dispatch.lisp
# prepares the s-expression with MR-MATCH.

_PATTERN_OBJECTS = {"Pattern", "Blank", "BlankSequence", "BlankNullSequence",
                    "Optional", "Condition", "PatternTest"}

# G-9 risk flags accepted after review (closed list; spec 3.4 makes every
# other risk flag a GenError). The reader flags any head with a numeric
# argument as possibly rewritten by evaluation; Complex[0, a_] has a pattern
# argument, so it stays the unevaluated Complex[0, a_] expression — the
# shape MR-MATCH matches against the converter's complex atoms (spec 3.2
# G-3). 9.1 is outside the probe-02 census (not in LoadRules).
ACCEPTED_RISKS = {
    ("9_1", 11, "risk:numeric-or-negated-arg:Complex"),   # 9.1.m L15
    # ReduceInertTrig's first two clauses (IntegrationUtilityFunctions.m
    # L6496/L6500; inert-trig substrate, Task 4). The Pi-arg flag guards a
    # BUILT-IN head whose evaluation rewrites a Pi-shifted argument
    # (Sin[x+Pi] -> -Sin[x]). ReduceInertTrig is a user function, and
    # SetDelayed never applies the function's own definitions to its LHS —
    # only the argument's Plus/Times/Power evaluation happens, which the
    # reader emulates. The Complex[0, mz_] / Complex[0, nz_] flag is the 9.1
    # L15 case above: a pattern argument keeps Complex unevaluated.
    ("rit", 1, "risk:Pi-arg:ReduceInertTrig"),
    ("rit", 2, "risk:Pi-arg:ReduceInertTrig"),
    ("rit", 2, "risk:numeric-or-negated-arg:Complex"),
}


def _evaluated(text, key, n, what):
    """Reader parse + evaluation of a pattern text. A G-9 risk effect (an
    evaluation the reader does not emulate) is a GenError."""
    try:
        tree = rd.parse(text)
    except rd.ParseError as ex:
        raise GenError(f"{key} r{n}: reader cannot parse the {what} "
                       f"{text[:60]!r}: {ex}")
    ev, effects = rd.evaluate_lhs(tree)
    risks = [e for e in effects if e.startswith("risk:")
             and (key, n, e) not in ACCEPTED_RISKS]
    if risks:
        raise GenError(f"{key} r{n}: {what} evaluation not emulated "
                       f"({', '.join(risks)}): {text[:60]!r}")
    return ev


def _sexp(tree, key, n):
    """The s-expression text of a pattern tree, checked to be a plain
    Maxima string literal body."""
    s = rd.to_sexp(tree)
    if '"' in s or "\\" in s:
        raise GenError(f"{key} r{n}: pattern s-expression carries a quote or "
                       f"a backslash: {s[:60]!r}")
    return s


def _has_pattern(e):
    return isinstance(e, tuple) and (
        e[0] in _PATTERN_OBJECTS or any(_has_pattern(a) for a in e))


def pattern_sexp(lhs, key, n, rule_vars):
    """The rule's Int[<pattern>, x_Symbol] LHS as the evaluated FullForm
    s-expression %mr_defrule prepares. Each capture's Pattern name becomes
    its Maxima capture name cap_name(key, n, v), so the dispatcher's
    binding list is the mm list the cond and repl read with geteqR; x keeps
    its name (the dispatcher pre-binds it to the integration variable)."""
    ev = _evaluated(lhs, key, n, "LHS")
    if not (isinstance(ev, tuple) and len(ev) == 3 and ev[0] == "Int"
            and ev[2] == ("Pattern", "x", ("Blank", "Symbol"))):
        raise GenError(f"{key} r{n}: LHS is not Int[<pattern>, x_Symbol]: "
                       f"{rd.fullform(ev)[:60]!r}")
    return _sexp(_rename_captures(ev, key, n, rule_vars), key, n)


# The bare-u_ Int-record tail convention (inert-trig substrate design
# 3.3, Task 8). A generated file may route a rule into mr_rules_<key>_tail
# instead of mr_rules_<key>; mr_load_all appends every _tail list to
# mr_rule_table AFTER all classes, so our load-order-walking dispatcher
# tries such a record last (Mathematica gets there by pattern specificity
# instead). A bare-u_ record -- integrand (Pattern <name> (Blank)), the
# most general Int pattern there is -- matches every integrand, so it must
# never sit ahead of a more specific rule of a later-loading class.
#
# Six such records already exist, in classes 1/2/3, at their SOURCE
# position in the body list. Moving them changes accepted class-1/2/3
# behaviour and needs a corpus A/B, out of this task's scope
# (.scratch/class-ports/issues/07-bare-u-records-mid-table.md) -- so this
# CLOSED, NAMED exception list keeps exactly those six in the body; every
# OTHER bare-u_ record routes to the tail. The static gate
# (test/check_generated_rules.py) enforces the same list both ways: every
# tail record is bare-u_, and no bare-u_ record sits in a body list unless
# it is named here.
BARE_U_BODY_EXCEPTIONS = {
    ("1_4_1", 7):  "mr_simplify_flag and SumQ[u] (issue 07)",
    ("1_4_1", 8):  "SumQ[u] (issue 07)",
    ("9_1", 8):    "FreeQ[a, x] (bare a_; issue 07)",
    ("9_1", 13):   "SumQ[u] (issue 07)",
    ("2_3", 96):   "FunctionOfExponentialQ[u, x] and not a MatchQ shape (issue 07)",
    ("3_5", 42):   "NonsumQ[u] and FunctionOfLog[Cancel[x u], x] not false (issue 07)",
}


# Class 4 is emitted as a SUBSET (inert-trig substrate plan, Task 9): only
# the bridge's bare-u_ records, not section 4's ~2,070 body rules, which need
# the class-4 Step-1 token closure no one has adjudicated yet. Per source key,
# the run numbers (1-based, the same n every handle and the static gate use)
# of the records emitted. Every other run of the file is skipped; numbering
# is NOT compacted, so a handle keeps its source clause number when the rest
# of the file is ported later. Each listed record is asserted bare-u_ at
# generation time -- a reference-clone bump that moves a run fails loudly
# instead of emitting the wrong rule.
#   4_1_0_1 r1  Int[u_,x_Symbol] := Int[DeactivateTrig[u,x],x] /;
#               FunctionOfTrigOfLinearQ[u,x] -- the bridge (4.1.0.1.m L4,
#               the If[TrueQ[$LoadShowSteps], ...] wrapper that
#               unwrap_showsteps_line recovers).
#   4_7_5 r21/r22  the Cot/Tan Subst forms (4.7.5.m L24/L25).
#   4_7_5 r47/r48  the Sin/Cos derivative-divides forms (L50/L51).
#   4_7_5 r58   the Tan Subst form under InverseFunctionFreeQ (L61).
#   4_7_5 r71   the half-angle Weierstrass substitution (L74; Task 10) --
#               its trial Int sits in a Block[{$ShowSteps = False,
#               $StepCounter = Null}, ...], which translate() emits as the
#               body alone (the IntHide precedent; see the "Block" case).
#   4_7_5 r72   Int[u_,x_Symbol] := With[{v=ActivateTrig[u]},
#               CannotIntegrate[v,x]] /; Not[InertTrigFreeQ[u]] (L76; Task
#               10 fix round 1, ruling R26) -- the file's LAST record: the
#               integrand the bridge admitted and nothing finished is given
#               up RE-ACTIVATED, so the unintegrable noun carries no inert
#               head. It must stay last in the tail.
# 4_7_5 r66/r70 (L69/L73 -- TrigSimplify, ExpandTrig) are bare-u_ too but
# NOT wrapped; they are class-4 port work, outside this subset.
CLASS4_SUBSET = {
    "4_1_0_1": (1,),
    "4_7_5": (21, 22, 47, 48, 58, 71, 72),
}


_INT_X_UNTYPED = re.compile(r"^Int\[(.*),\s*x_\]$", re.DOTALL)

def _normalize_int_x(lhs):
    """Spec 2026-09-22 A2.4: 9.3's final give-up is written `Int[u_,x_]`,
    not `Int[u_,x_Symbol]` -- the dispatcher always passes a symbol as x,
    so the two match the same calls here. Read only the exact untyped
    `x_` in the SECOND argument position (a already-typed `x_Symbol` LHS,
    every class 1-6 rule, does not match: the trailing literal is `]`
    right after `x_`, which `x_Symbol]` is not), so this is a no-op on
    every existing rule."""
    m = _INT_X_UNTYPED.match(lhs.strip())
    return f"Int[{m.group(1)}, x_Symbol]" if m else lhs

def bare_int_clause(lhs, key, n):
    """True when the Int rule's integrand argument is the most general Int
    pattern there is: a bare named Blank, (Pattern <name> (Blank)) -- no
    head, no Optional, no type restriction. See BARE_U_BODY_EXCEPTIONS
    above for how such a record is routed."""
    lhs = _normalize_int_x(lhs)
    ev = _evaluated(lhs, key, n, "LHS")
    return (isinstance(ev, tuple) and len(ev) == 3 and ev[0] == "Int"
            and isinstance(ev[1], tuple) and len(ev[1]) == 3
            and ev[1][0] == "Pattern" and ev[1][2] == ("Blank",))


def rewrite_pattern_sexp(lhs, key, n, rule_vars, fname):
    """A utility clause's Name[<args>] LHS as the evaluated FullForm
    s-expression %mr_defrewrite prepares (inert-trig substrate design 3.2).
    The outermost head is the function name; %mr_rewrite matches the pattern
    against (Name u x), so the clause must be of arity 2 to be reachable —
    ReduceInertTrig's 3-argument clause is emitted all the same (it is one
    of the source's clauses) and simply never binds a 2-argument call. The
    captures are renamed exactly as an Int rule's (_rename_captures); an
    `x_` argument keeps the name x, and is the walker's x."""
    ev = _evaluated(lhs, key, n, "LHS")
    if not (isinstance(ev, tuple) and ev[0] == fname and len(ev) >= 2):
        raise GenError(f"{key} r{n}: LHS is not {fname}[...]: "
                       f"{rd.fullform(ev)[:60]!r}")
    return _sexp(_rename_captures(ev, key, n, rule_vars), key, n)


def _rename_captures(ev, key, n, rule_vars):
    """Each capture's Pattern name -> its Maxima capture name cap_name(key,
    n, v), so the dispatcher's binding list is the mm list the cond and repl
    read with geteqR; x keeps its name (the dispatcher pre-binds it to the
    integration variable). Every capture must survive evaluation."""
    seen = set()

    def rename(e):
        if not isinstance(e, tuple):
            return e
        if (e[0] == "Pattern" and len(e) == 3 and e[1] != "x"
                and not isinstance(e[1], (tuple, rd.Str))):
            if e[1] not in rule_vars:
                raise GenError(f"{key} r{n}: pattern variable {e[1]!r} is "
                               f"not a capture ({sorted(rule_vars)})")
            seen.add(e[1])
            return ("Pattern", cap_name(key, n, e[1]), rename(e[2]))
        return tuple(rename(a) for a in e)

    out = rename(ev)
    if seen != set(rule_vars):
        raise GenError(f"{key} r{n}: captures "
                       f"{sorted(set(rule_vars) - seen)} vanish from the "
                       f"evaluated LHS")
    return out


# Mathematica inverse-trig heads -> the NATIVE Maxima function names, for a
# head list compared with a function-valued capture (translate(), MemberQ).
# Maxima reads each typed name as the operator symbol the dispatcher binds
# the capture to (asin -> %asin; measured 2026-09-13). The corpus integrands
# carry the natives, and probed 2026-08-29 on
# branch_5_50_base_84_g4204fb669 / SBCL 2.6.7 asin/acos/atan/acot/asinh/
# acosh/atanh/acoth are all bound natives with closing diffs (arccot/arcoth
# are unbound nouns) — NOT the RENAME table's %mr_ shims.
NATIVE_FUNCTION_HEADS = {
    "ArcSin": "asin", "ArcCos": "acos", "ArcTan": "atan",
    "ArcCot": "acot", "ArcSinh": "asinh", "ArcCosh": "acosh",
    "ArcTanh": "atanh", "ArcCoth": "acoth",
}


def _input_form(e):
    """A pattern-free evaluated tree -> InputForm text translate() accepts
    (Plus/Times/Power as operators, every other head as a call)."""
    if isinstance(e, tuple):
        h, args = e[0], e[1:]
        if h == "Plus":
            return "(" + " + ".join(_input_form(a) for a in args) + ")"
        if h == "Times":
            return "(" + "*".join(_input_form(a) for a in args) + ")"
        if h == "Power" and len(args) == 2:
            # Plus/Times, fractions and negative integers carry their own
            # parentheses; a nested Power is the one operand that needs
            # them (x^2 stays x^2 — _emit_expon reads the power form)
            return "^".join(f"({_input_form(a)})" if isinstance(a, tuple)
                            and a[0] == "Power" else _input_form(a)
                            for a in args)
        if h == "List":
            return "{" + ", ".join(_input_form(a) for a in args) + "}"
        return (f"{_input_form(h)}["
                f"{', '.join(_input_form(a) for a in args)}]")
    if isinstance(e, rd.Str):
        return '"' + e + '"'
    if isinstance(e, Fraction):
        return f"({e.numerator}/{e.denominator})"
    if isinstance(e, int):
        return f"({e})" if e < 0 else str(e)
    if isinstance(e, rd.Real):
        return e.text
    return e


def _emit_matchq(arglist, ctx):
    """MatchQ[u, pat /; cond] -> %mr_matchQ(u, "<pattern>", [<parts>],
    <cond>) — called from translate() with the RAW args.

    The pattern is the reader's evaluated s-expression with each pattern
    variable renamed to a fresh marker _mr_<key>_r<n>mq<k>_<v>. MatchQ
    evaluates its pattern argument, so every pattern-free part that is not
    a number or E/Pi/I — the integration variable x, an outer capture, a
    computed Expon[Px, x] — becomes the placeholder (MRArg <k>), and its
    translated Maxima text is the k-th element of the list argument,
    evaluated at call time (maxima_rubi_dispatch.lisp |$%mr_matchQ|
    substitutes the values). The cond is a lambda over the binding list
    with each marker rewritten to %mr_mk(<marker>, %mr_mqb) — held until
    the matcher calls it (Maxima evaluates call arguments eagerly, FIX E7);
    an empty cond is bare true."""
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
    ev = _evaluated(pat, key, n, "MatchQ pattern")
    ctx["mq"] += 1
    mq = ctx["mq"]
    mark, parts = {}, []

    def placeholder(e):
        parts.append(translate(_input_form(e), ctx))
        return ("MRArg", len(parts))

    def conv(e):
        if isinstance(e, tuple):
            if e[0] == "Pattern" and len(e) == 3:
                mark.setdefault(e[1], f"_mr_{key}_r{n}mq{mq}_{e[1]}")
                return ("Pattern", mark[e[1]], conv(e[2]))
            if e[0] in ("Blank", "BlankSequence", "BlankNullSequence"):
                return e
            if not _has_pattern(e):
                return placeholder(e)
            head = conv(e[0]) if isinstance(e[0], tuple) else e[0]
            return (head,) + tuple(conv(a) for a in e[1:])
        if (isinstance(e, (int, Fraction, rd.Real, rd.Str))
                or e in ("E", "Pi", "I")):
            return e
        return placeholder(e)

    tree = conv(ev)
    if not mark:
        raise GenError(f"{key} r{n}: MatchQ pattern without variables: "
                       f"{pat!r}")
    if mcond:
        saved = ctx["markers"]
        ctx["markers"] = mark
        try:
            cond_txt = translate(mcond, ctx)
        finally:
            ctx["markers"] = saved
        # \b...\b guards the prefix-collision case (Q vs Qx)
        for m in mark.values():
            cond_txt = re.sub(rf"\b{re.escape(m)}\b",
                              f"%mr_mk({m}, %mr_mqb)", cond_txt)
        cond_emit = f"lambda([%mr_mqb], {cond_txt})"
    else:
        cond_emit = "true"
    return (f'%mr_matchQ({u_txt}, "{_sexp(tree, key, n)}", '
            f'[{", ".join(parts)}], {cond_emit})')

def emit_head(head, arglist, ctx):
    """Special forms first, then a plain renamed head(arglist)."""
    key, n = ctx["key"], ctx["n"]
    if head in ctx["vars"]:
        # A function-valued capture applied (F[d*(e+f*x)] — 3_1_5 r58/r59,
        # 3_3 r58, 3_4 r37): the dispatcher binds F to the Maxima operator
        # symbol of the matched head (%asin), and apply builds the call
        # (the idiom probed 2026-08-29: apply works for a symbol holding a
        # native, a %mr_ port, or a noun function).
        return f"apply({cap_name(key, n, head)}, [{', '.join(arglist)}])"
    if head == "Complex":
        # Complex[re, im] in a repl (9.1 L15 Complex[Identity[0], a]): the
        # Mathematica complex number re + im I.
        if len(arglist) != 2:
            raise GenError(f"{key} r{n}: Complex arity {len(arglist)}")
        return f"({arglist[0]} + {arglist[1]}*%i)"
    if head == "FreeQ":
        # FreeQ[e, x] -> freeof(x, e); FreeQ[{a,b}, x] -> and of freeof.
        # (FIX F7) the arg list may arrive as [a, b] (braces already
        # converted by translate_atom) or still as {a, b}.
        e, xv = arglist[0], arglist[1]
        if e.startswith("{") or e.startswith("["):
            e = e[1:-1]
        parts = [f"freeof({xv}, {p.strip()})" for p in split_top(e, ",")]
        return " and ".join(parts)
    if head in INT_CMP:
        if len(arglist) != 2:
            raise GenError(f"{key} r{n}: {head} arity {len(arglist)}")
        return f"{INT_CMP[head]}({arglist[0]}, {arglist[1]})"
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
        # mr_int's seen test is exact membership for every source (exact
        # seen test design 3.1), so 9.1 needs no entry of its own.
        return f"mr_int({arglist[0]}, {arglist[1]})"
    if RESTRUCTURE.get(head) == "noun" or RENAME.get(head) == "noun":
        # Rubi's inert-integral heads. Keyed on the TABLE's handler value,
        # not on a hardcoded token tuple: class 6 added a third one
        # (Integral, 8 rules — 6.3.11/6.3.12/6.1.12) whose table row the
        # tuple did not know about, so translate() succeeded and the head
        # fell through to the generic call emission as `noun(expr, x)` — a
        # call to a function that does not exist, i.e. a silently wrong
        # answer at runtime. Caught 2026-09-20 by the Step-5 static greps
        # (mr_unintegrable came out 18, not the census's 18 + 8); see also
        # the HANDLER_ONLY guard below, which now makes this class of
        # mistake a generation error rather than a bad rule file.
        if len(arglist) != 2:
            raise GenError(f"{key} r{n}: {head} arity {len(arglist)}")
        return f"mr_unintegrable({arglist[0]}, {arglist[1]})"
    if head == "With" or head == "Module":
        if len(arglist) != 2:
            raise GenError(f"{key} r{n}: {head} arity {len(arglist)}")
        locals_, assigns = _scope_locals(head, arglist[0], key, n)
        body = arglist[1].strip()
        # An inner /; is moved into the cond by emit_rule
        # (split_inner_condition, spec 3.4); one that reaches here sits
        # below the top of the RHS — none in classes 1-3 (census
        # 2026-09-12) — and has no faithful cond placement: fail loudly.
        if _find_top(body, lambda i, ch: ch == "/" and body[i+1:i+2] == ";") >= 0:
            raise GenError(f"{key} r{n}: {head} with an inner condition "
                           f"below the top of the RHS")
        return _scope_block(locals_, assigns, _maxima_stmts(body))
    if head == "If":
        if len(arglist) != 3:
            raise GenError(f"{key} r{n}: If arity {len(arglist)}")
        # parenthesized: an If inside a && / || cond chain must bind as one
        # operand
        return f"(if {arglist[0]} then {arglist[1]} else {arglist[2]})"
    if head == "Switch":
        # Rubi's Switch[e, form1, value1, form2, value2, …] — 3 sites, all
        # of them in ReduceInertTrig's 3-argument clause (inert-trig
        # substrate, Task 4). Maxima has no switch, so it becomes a nested
        # if/elseif over EQUALITY with each form.
        #
        # Mathematica matches a Switch form as a PATTERN; at all three
        # sites every form is a bare inert head symbol (sin, cos, …),
        # which the translation table has already turned into the %mr_i*
        # OPERATOR SYMBOL the dispatcher binds a head-position capture to
        # (maxima_rubi_dispatch.lisp mr-binding-value), so `=` on symbols
        # is the faithful test. A form that is not a plain symbol would
        # need real pattern matching: GenError, never a silent mis-emit.
        #
        # The final else is `false`, not an error: Mathematica leaves a
        # Switch with no matching form unevaluated, and a rewrite repl that
        # values to false is declined by %mr_rewrite (its `(and ok r)`
        # test), which is the closest faithful behaviour available.
        if len(arglist) < 3 or (len(arglist) - 1) % 2 != 0:
            raise GenError(f"{key} r{n}: Switch arity {len(arglist)} "
                           f"(need a subject and form/value pairs)")
        subject = arglist[0].strip()
        parts = []
        for i in range(1, len(arglist), 2):
            form = arglist[i].strip()
            if not re.fullmatch(r"%?[A-Za-z_][A-Za-z0-9_]*", form):
                raise GenError(f"{key} r{n}: Switch form {form!r} is not a "
                               f"plain symbol — it would need pattern "
                               f"matching, which this emitter case does not do")
            parts.append((form, arglist[i + 1].strip()))
        out = "false"
        for form, value in reversed(parts):
            out = f"if {subject} = {form} then {value} else {out}"
        return f"({out})"
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
    if head == "Gamma":
        return _emit_gamma(arglist, key, n)
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
    if head == "LogGamma":
        # Structural rewrite (RESTRUCTURE handler "loggamma"), not a
        # rename: LogGamma[v] -> log(gamma(v)). loggamma itself is an
        # UNBOUND noun whose diff stays undifferentiated (a noun), while
        # diff(log(gamma(x)),x) = psi[0](x) closes under ratsimp (both
        # measured 2026-08-29 on branch_5_50_base_84_g4204fb669) — the
        # closed form is what lets the zero chain verify the answer.
        if len(arglist) != 1:
            raise GenError(f"{key} r{n}: LogGamma arity {len(arglist)}")
        return f"log(gamma({arglist[0].strip()}))"
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
    if name in HANDLER_ONLY:
        raise GenError(
            f"{key} r{n}: {head!r} maps to {name!r}, which is an EMITTER "
            f"HANDLER NAME, not a Maxima function — the translation table "
            f"has a row for it but no emitter case claims it, so this would "
            f"emit a call to a function that does not exist. Add the "
            f"emitter case (or map the token to a real name).")
    # FIX F2: Maxima function calls use parentheses; the brief emitted the
    # Mathematica bracket form name[args], which is a parse error / noun
    # form in Maxima.
    return f"{name}({', '.join(arglist)})"


def _scope_locals(head, decls_txt, key, n):
    """The translated locals list of a With/Module -> (names, assignment
    texts). FIX E11: the list is ALREADY translated — re-translating
    double-renames the captures; a bare local (Module[{k, u}, …]) declares
    without an assignment."""
    decls_txt = decls_txt.strip()
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
            assigns.append(f"{name} : {', '.join(q.strip() for q in parts[1:])}")
        locals_.append(name)
    return locals_, assigns


def _push_scope_locals(head, decls_raw, ctx):
    """With/Module local prefixing (final fix wave I2, ruling R28; every
    class since ticket .scratch/class-ports/issues/08).

    A generated repl binds its With/Module locals in a Maxima block and
    may run a nested mr_int inside it. Maxima binds block locals
    DYNAMICALLY, so an unprefixed local named like a corpus symbol (d, v,
    w) is live during the nested integration, and any re-evaluation there
    substitutes its value for the integrand's own symbol (measured: 4.7.5
    r47's block([d], d : 1) turned part of the answer to 1/(d x^7 + 1) into
    the d = 1 answer -- a silently wrong antiderivative). Renaming each
    local to _mr_<key>_r<n>_<name> makes the block name nothing a user
    integrand can contain.

    decls_raw is the RAW .m locals list ({v = ..., d}); every name it
    declares is mapped for the whole scope -- the decl values too, so the
    emitted text is exactly the unprefixed emission with the locals
    alpha-renamed (a value naming a same-named local reads it the same
    way). Returns the previous map, which the caller restores. Emitted for
    every Int rule (emit_rule sets ctx["prefix_locals"]); never for a
    rewrite-table clause. The P3 gate undoes it as a closed exception
    (test/check_generated_rules.py undo_local_prefix). The unprefixed
    emission translated the local D to diff; prefixed it is ..._D."""
    d = decls_raw.strip()
    if not (d.startswith("{") and d.endswith("}")):
        raise GenError(f"{ctx['key']} r{ctx['n']}: {head} locals not a "
                       f"list: {d[:40]!r}")
    saved = ctx.get("locals") or {}
    new = dict(saved)
    for p in split_top(d[1:-1], ","):
        name = split_top(p.strip(), "=")[0].strip()
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", name):
            raise GenError(f"{ctx['key']} r{ctx['n']}: {head} local "
                           f"{name!r} is not a plain symbol")
        if name in ctx["vars"]:
            raise GenError(f"{ctx['key']} r{ctx['n']}: {head} local "
                           f"{name!r} shadows a capture -- the prefixed "
                           f"name would collide with its capture name")
        new[name] = f"_mr_{ctx['key']}_r{ctx['n']}_{name}"
    ctx["locals"] = new
    return saved


def _scope_block(locals_, assigns, body):
    lead = ", ".join(assigns) + ", " if assigns else ""
    return f"block([{', '.join(locals_)}], {lead}{body})"


def split_inner_condition(rhs):
    """A raw .m RHS With[{…}, body /; c] or Module[{…}, body /; c] ->
    (head, locals text, body, c); None for any other RHS. Spec 3.4: the
    inner condition moves from repl into cond, so it runs under the
    matcher's condition hook and takes part in the binding retry. All 227
    class 1-3 inner conditions have this top-level shape (census
    2026-09-12, 0 nested)."""
    head, args = head_args(rhs)
    if head not in ("With", "Module"):
        return None
    parts = split_top(args, ",")
    decls, body = parts[0], ",".join(parts[1:])
    last = _find_top(body, lambda i, ch: ch == "/" and body[i+1:i+2] == ";")
    if last < 0:
        return None
    return head, decls, body[:last], body[last+2:]


# Rubi's condition-assignment idiom. An assignment `name=<expr>` in a rule
# condition, with no `==`/`=!=`/`<=`/`>=`/`:=` in front of the `=`. The name
# is a plain Mathematica symbol, so the lookbehind rejects a suffix match.
_COND_ASSIGN = re.compile(r"(?<![A-Za-z0-9$_])([A-Za-z][A-Za-z0-9]*)\s*=(?![=!])")


def _scope_bare_locals(decls):
    """The names a raw .m With/Module locals list declares WITHOUT an
    initialiser ({q,r} -> ['q','r']; {v=…, d} -> ['d'])."""
    d = decls.strip()
    if not (d.startswith("{") and d.endswith("}")):
        return []
    out = []
    for p in split_top(d[1:-1], ","):
        parts = split_top(p.strip(), "=")
        if len(parts) == 1 and parts[0].strip():
            out.append(parts[0].strip())
    return out


def _condition_assignments(cond, bare, key, n, where):
    """Rubi's condition-assignment idiom -> [(name, raw rhs text), …] in the
    order the condition evaluates them.

    The idiom is a `/;` test that BINDS a name the replacement then reads
    (9.3 .m :145, :177, :185, :193 — the only four sites in the pinned
    clone, `grep -rn "FalseQ\\[[a-zA-Z]*=" reference/rubi/.../IntegrationRules/`):

        Module[{q,r}, q*r*Subst[…] /;
          Not[FalseQ[r=Divides[y^m,v^m,x]]] &&
          Not[FalseQ[q=DerivativeDivides[y,u,x]]]]

    Maxima's `=` is EQUALITY, not assignment, so emitting the assignment
    verbatim builds an equation object: %mr_falseQ of an equation is never
    true, the guard is vacuous and the record fires on every integrand its
    pattern matches, while the replacement's q and r stay unbound symbols
    that multiply the answer (.scratch/class-ports/issues/13).

    Recognised STRUCTURALLY — an assignment to a BARE local of the
    enclosing With/Module scope — never by rule number, so a later class
    carrying the idiom is handled too. Any other assignment in a condition
    (to a capture, to an already-initialised local, or anywhere outside a
    scope at all) has no such placement and is a GenError rather than a
    silent equation."""
    out = []
    for m in _COND_ASSIGN.finditer(cond):
        name = m.group(1)
        if name not in bare:
            raise GenError(
                f"{key} r{n}: assignment to {name!r} in {where} — not a bare "
                f"local of an enclosing With/Module scope, so it has no "
                f"faithful Maxima placement (issue 13)")
        i, depth = m.end(), 0
        while i < len(cond):
            ch = cond[i]
            if ch in "[({":
                depth += 1
            elif ch in "])}":
                if depth == 0:
                    break
                depth -= 1
            elif depth == 0 and (ch == "," or cond.startswith("&&", i)
                                 or cond.startswith("||", i)):
                break
            i += 1
        rhs = cond[m.end():i].strip()
        if not rhs:
            raise GenError(f"{key} r{n}: empty assignment right-hand side "
                           f"for {name!r} in {where}")
        out.append((name, rhs))
    names = [nm for nm, _ in out]
    if len(set(names)) != len(names):
        raise GenError(f"{key} r{n}: {where} assigns a name twice ({names}) "
                       f"— the replacement cannot repeat that order")
    return out


def _hoist_scope_assigns(decls, cassigns, key, n):
    """The repl's copy of a raw .m locals list, with each condition
    assignment repeated as a scope initialiser. The cond and the repl are
    separate Maxima functions, so the condition's binding cannot reach the
    replacement: each evaluates the assignments itself.

    ORDER (fix round 1). Mathematica enters the scope first — every
    declaration with an initialiser is evaluated at that point — and
    evaluates the `/;` condition afterwards, so the condition's
    assignments come LAST. The declarations therefore keep their own
    relative order and the condition assignments follow, in the
    condition's order. _scope_block emits the list as sequential
    `name : value` statements, so `Module[{v=f[x], q}, … /;
    Not[FalseQ[q=g[v]]]]` emits `v : f(x)` before `q : g(v)` and g reads
    a bound v. Leading with the condition assignments instead (the first
    cut here) emitted `q : g(v)` first, off an unbound v.

    Output-neutral on the four upstream sites, which are all
    `Module[{q,r}]` with no initialised local: `rest` is empty there and
    the emitted list is the same either way."""
    d = decls.strip()
    if not (d.startswith("{") and d.endswith("}")):
        raise GenError(f"{key} r{n}: locals not a list: {d[:40]!r}")
    done = {nm for nm, _ in cassigns}
    rest = [p.strip() for p in split_top(d[1:-1], ",")
            if split_top(p.strip(), "=")[0].strip() not in done]
    return "{" + ", ".join(rest + [f"{nm}={rhs}" for nm, rhs in cassigns]) + "}"


def _assign_in_test(test, cassigns, ctx, key, n):
    """The cond's copy: the assignments stay exactly where the condition
    puts them, so Maxima's short-circuiting `and` evaluates them in the
    upstream `&&` order and skips the ones after the first false test
    (measured: `is(not(f(r:g(false))) and not(f(q:h(7))))` never calls h).
    `=` becomes `:`; an argument-position assignment is legal Maxima and
    values to the assigned value (`f(a : b)` parses and binds)."""
    for name in dict.fromkeys(nm for nm, _ in cassigns):
        mapped = (ctx.get("locals") or {}).get(name, name)
        want = sum(1 for nm, _ in cassigns if nm == name)
        pat = re.compile(r"(?<![A-Za-z0-9_$])" + re.escape(mapped)
                         + r"\s*=(?![=<>])")
        test, cnt = pat.subn(mapped + " : ", test)
        if cnt != want:
            raise GenError(f"{key} r{n}: the translated condition has {cnt} "
                           f"assignment site(s) for {mapped!r}, expected "
                           f"{want}")
    return test


def emit_rule(run, key, n, rule_vars, fname=None):
    """One rule run (lhs, rhs, cond) -> its cond and repl functions and its
    %mr_defrule registration, as Maxima text (spec 3.4). rule_vars is the
    set of capture names (from the lhs).

    With fname (a Rubi utility function's name) the run is one CLAUSE of
    that function, `fname[<args>] := rhs /; cond`, and the registration is
    a %mr_defrewrite record instead (inert-trig substrate design 3.2). The
    cond and repl bodies are the SAME text either way — this one emitter
    produces both, so the P3 byte-stability of rule bodies covers the
    rewrite tables too. The one difference: a clause with no condition at
    all (no /; outer or inner) registers the literal Maxima `true` as its
    cond instead of a function returning true, and emits no cond function —
    %mr_rewrite's `(eq cond-fn t)` branch accepts every binding for it."""
    lhs, rhs, cond = run
    if fname is None:
        # A2.4: 9.3's `Int[u_,x_]` give-up read as `Int[u_,x_Symbol]` --
        # a no-op on every already-typed class 1-6 LHS (_normalize_int_x).
        lhs = _normalize_int_x(lhs)
        if not re.match(r"^Int\[(.*),\s*x_Symbol\]$", lhs.strip(), re.DOTALL):
            raise GenError(f"{key} r{n}: cannot strip Int[...]: {lhs!r}")
    # prefix_locals: every class renames its With/Module locals (ticket
    # 08; see _push_scope_locals). Never for a rewrite-table clause
    # (fname) -- those tables stay byte-identical.
    ctx = {"key": key, "n": n, "vars": rule_vars, "markers": None, "mq": 0,
           "locals": {}, "prefix_locals": fname is None}
    if fname is None:
        pattern = pattern_sexp(lhs, key, n, rule_vars)
    else:
        pattern = rewrite_pattern_sexp(lhs, key, n, rule_vars, fname)
    # An assignment in the OUTER condition binds nothing any scope
    # declares, so it has no faithful placement: loud, never an equation
    # (see _condition_assignments).
    if cond:
        _condition_assignments(cond, [], key, n, "the outer condition")
    base_cond = (translate(drop_optionals(cond, rule_vars), ctx)
                 if cond else "true")
    # M-cas-simp (3.5 r10, class-3 deferred campaign C6): the .m cond
    # EqQ[D[Px/Qx, x], 0] tests that the ratio Px/Qx is a constant (its
    # x-derivative is 0). Mathematica's D auto-simplifies the derivative of
    # a constant ratio to 0; Maxima's diff does not — the e92 binding
    # (Px = c*x^2+a over Qx = c*e*x^2+a*e) leaves a non-zero-looking
    # rational. The faithful analogue is ratsimp on the derivative: for
    # rational Px, Qx, ratsimp(diff(Px/Qx, x)) = 0 iff Px/Qx is constant.
    # Measured 2026-09-02 on branch_5_50_base_84_g4204fb669 / SBCL 2.6.7
    # (probes c6 D5/D7 positive; D12/D13 the negative shape a+c*x^2 over
    # 2+3*x^2 stays non-zero, so the cond stays false).
    if key == "3_5" and n == 10:
        old = "diff(_mr_3_5_r10_Px/_mr_3_5_r10_Qx, x)"
        new = "ratsimp(diff(_mr_3_5_r10_Px/_mr_3_5_r10_Qx, x))"
        if base_cond.count(old) != 1:
            raise GenError("3_5 r10: expected exactly one "
                           f"{old!r} in the translated cond, found "
                           f"{base_cond.count(old)} (M-cas-simp hook)")
        base_cond = base_cond.replace(old, new)
    inner = split_inner_condition(rhs)
    if inner is None:
        cond_txt = base_cond
        repl_txt = translate(drop_optionals(rhs, rule_vars), ctx)
    else:
        head, decls, body, inner_cond = inner
        # Rubi's condition-assignment idiom (issue 13): the repl repeats
        # the condition's assignments as scope initialisers, the cond
        # performs them in place.
        cassigns = _condition_assignments(
            inner_cond, _scope_bare_locals(decls), key, n,
            "the inner condition")
        decls_repl = (_hoist_scope_assigns(decls, cassigns, key, n)
                      if cassigns else decls)
        repl_txt = translate(drop_optionals(f"{head}[{decls_repl},{body}]",
                                            rule_vars), ctx)
        # the cond's copy of the scope takes the same local names as the
        # repl's (prefixed; see _push_scope_locals)
        saved = (_push_scope_locals(head, drop_optionals(decls, rule_vars),
                                    ctx)
                 if ctx["prefix_locals"] else None)
        locals_, assigns = _scope_locals(
            head, translate(drop_optionals(decls, rule_vars), ctx), key, n)
        test = translate(drop_optionals(inner_cond, rule_vars), ctx)
        if cassigns:
            test = _assign_in_test(test, cassigns, ctx, key, n)
        if ctx["prefix_locals"]:
            ctx["locals"] = saved
        # parenthesized: the outer cond may be an `or` chain
        cond_txt = (f"({base_cond})  and  "
                    f"{_scope_block(locals_, assigns, f'is({test}) = true')}")
    # The cond and repl bind each capture from the matchlist mm with
    # geteqR — the dispatcher builds mm from the matcher's bindings, one
    # [<capture name> = value] per capture. The geteqR name argument uses
    # the UNBALANCED Rubi quote idiom geteqR(mm, 'name) — NO closing quote
    # (this build's quote NUD parses the quoted operand at lbp 190; a
    # balanced 'name' raises "' is not an infix operator", measured
    # 2026-08-20).
    caps = sorted(cap_name(key, n, v) for v in rule_vars)
    binds = [f"{c} : geteqR(mm, '{c})" for c in caps]
    bind_block = ", ".join(binds) if binds else "true"
    locals_txt = ", ".join(caps) if caps else ""
    # Capture snapshots (2026-08-25, e44 wrong-answer fix): the repl reads
    # each capture into a fresh __s local and its body is rewritten to
    # those locals — a nested mr_int call can then never clobber a capture
    # the repl still reads. (The defmatch matcher that assigned the pattern
    # symbols is gone; the snapshots are kept so every repl regenerates
    # byte-identical — spec 3.4.)
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
    cond_fun = [
        f"_mr_cond_{key}_r{n}(mm, x) := block([{locals_txt}],",
        f"  {bind_block},",
        f"  {cond_txt})$",
    ]
    repl_fun = [
        f"_mr_repl_{key}_r{n}(mm, x) := block([{snap_locals_txt}],",
        f"  {snap_bind_block},",
        f"  {repl_txt})$",
    ]
    if fname is None:
        return "\n".join(cond_fun + repl_fun + [
            f'_mr_rule_{key}_r{n} : %mr_defrule("{key}", {n}, "{pattern}", '
            f"_mr_cond_{key}_r{n}, _mr_repl_{key}_r{n})$",
        ])
    unconditioned = not cond and inner is None
    if unconditioned:
        if cond_txt != "true":
            raise GenError(f"{key} r{n}: an unconditioned clause translated "
                           f"its cond to {cond_txt!r}, not true")
        cond_fun, cond_arg = [], "true"
    else:
        cond_arg = f"_mr_cond_{key}_r{n}"
    return "\n".join(cond_fun + repl_fun + [
        f'_mr_rw_{key}_r{n} : %mr_defrewrite("{key}", {n}, "{pattern}", '
        f"{cond_arg}, _mr_repl_{key}_r{n})$",
    ])

def emit_file(rel_m, runs, key=None):
    # key defaults to the file's own number; the EXTRA_CLASS1 files
    # (measured 2026-08-25) are emitted under a `<key>b` suffix so their
    # rule names never collide with the same-numbered LoadRules sibling.
    if key is None:
        key = key_of(rel_m)
    # Regenerate line: class 1 keeps its committed header byte-identical
    # (the generate_class1.py shim keeps working and is the documented
    # class-1 command); other classes document the --class form.
    if CLASS == 1:
        regen = f"python3 generator/generate_class1.py --only {key}"
    else:
        regen = (f"python3 generator/generate_rules.py --class {CLASS} "
                 f"--only {key}")
    header = (f"/* rules/class{CLASS}/{key}.mac — GENERATED; do not edit.\n"
              f" * Source: Rubi 4 {PIN}\n"
              f" *          {rel_m}\n * Regenerate: {regen} */\n"
              f"{MIT}\n\n")
    body = []
    rule_names = []
    tail_names = []
    subset = CLASS4_SUBSET.get(key) if CLASS == 4 else None
    for n, run in enumerate(runs, start=1):
        if subset is not None and n not in subset:
            continue
        # FIX F3: rule_runs yields LISTS OF LINES; join the run and split it
        # the way the census does.
        text = "\n".join(run)
        if ":=" not in text:
            raise GenError(f"{key} r{n}: unparseable rule run (no ':='): "
                           f"{text[:60]!r}")
        # 5 class-1 runs glue an inline C-tier utility definition
        # (IntLinearQ/IntBinomialQ/IntQuadraticQ) onto the rule run. The
        # definition is provenance: its port is the %mr_* predicate in
        # maxima_rubi_utils.mac the rule conds call.
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
        handle_name = f"_mr_rule_{key}_r{n}"
        if subset is not None and not bare_int_clause(lhs, key, n):
            raise GenError(f"{key} r{n}: listed in CLASS4_SUBSET but not a "
                           f"bare-u_ Int record -- the source moved; "
                           f"re-measure the subset")
        if bare_int_clause(lhs, key, n) and (key, n) not in BARE_U_BODY_EXCEPTIONS:
            tail_names.append(handle_name)
        else:
            rule_names.append(handle_name)
        body.append("")
    body.append(f"mr_rules_{key} : [ {', '.join(rule_names)} ]$")
    if tail_names:
        # Only emitted when this file actually has one -- an absent
        # mr_rules_<key>_tail line is how a class with no such record
        # (still every class as of Task 8) regenerates byte-identically
        # (inert-trig substrate design 3.3).
        body.append(f"mr_rules_{key}_tail : [ {', '.join(tail_names)} ]$")
    n_emitted = len(runs) if subset is None else len(subset)
    if subset is not None and len(rule_names) + len(tail_names) != n_emitted:
        raise GenError(f"{key}: CLASS4_SUBSET lists {n_emitted} runs, "
                       f"{len(rule_names) + len(tail_names)} emitted "
                       f"(a listed run number is past the file's "
                       f"{len(runs)} runs)")
    body.append(f"mr_rules_count_{key} : {n_emitted}$")
    body.append(f"mr_witness_{key}() := true$")
    return header + "\n".join(body) + "\n"

def load_class_files(rubi):
    """The class-<CLASS> .m files, in Rubi.m LoadRules order, as paths
    relative to the Rubi clone root. parse_load_rules yields (parts,
    gated); the parts are relative to IntegrationRules/ and lack the .m
    extension. The selector is the class prefix: class 1 selects the
    non-gated "1 " files, class 2 the gated "2 " files (the
    $LoadElementaryFunctionRules block) — the gated flag is not a filter
    (dropping it is a no-op for class 1: the gated block holds no "1 "
    files)."""
    # strip_comments first (class 8, 2026-09-25): Rubi.m L352 is a
    # commented-out LoadRules for "8.10 Bessel functions", the only one in
    # the pinned Rubi.m; the raw parse would generate its 3 dead rules.
    # A no-op for every other class (the byte-identity gate).
    order = parse_load_rules(strip_comments((rubi / "Rubi" / "Rubi.m").read_text()))
    out = []
    for parts, gated in order:
        if not parts or not parts[0].startswith(CLASS_PREFIX):
            continue
        rel = "Rubi/IntegrationRules/" + "/".join(parts) + ".m"
        # class 4: only the files CLASS4_SUBSET names (see there)
        if CLASS == 4 and key_of(rel) not in CLASS4_SUBSET:
            continue
        # class 9: "9.1 Derivative integration rules" belongs to class 8
        # (spec §0.3.3, ticket 01), not class 9. Its key is "9_1" -- the
        # SAME key as the legacy class-1 file (NINE_ONE, "9.1 Integrand
        # simplification rules.m", a different .m that happens to share
        # the number) -- so skipping it here is what keeps that key
        # exclusive to class 1; see the GenError guard in main() for the
        # case where this exclusion is ever removed or another class-9
        # file collides.
        if CLASS == 9 and key_of(rel) == "9_1":
            continue
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

# The legacy 9.1 integrand simplification rules (spec 3.4): absent from the
# pinned Rubi.m LoadRules (dropped 2023-12, f7fa0fd), but loaded by the 2018
# Rubi the Maxima-syntax corpus was generated with, after the 1.x files — so
# it is generated at the end of the class-1 table (the position of the
# manual port it replaces). The pinned file's first rule (L4,
# Int[u_.*(v_+w_)^p_., x_Symbol]) is commented out there, so the generated
# file carries 28 rules; the manual port carried it as a 29th, dead rule.
NINE_ONE = ("Rubi/IntegrationRules/9 Miscellaneous/"
            "9.1 Integrand simplification rules.m")
NINE_ONE_TOTAL = 28

def configure(class_num):
    """Point the generator at class <class_num> (1, 2, 3, 4, 6 or 9)."""
    global CLASS, CLASS_PREFIX, OUT, EXPECTED_TOTAL
    CLASS = class_num
    CLASS_PREFIX = f"{CLASS} "
    OUT = ROOT / "rules" / f"class{CLASS}"
    # class 3: 334 — the 333 census count + the 3.5.m L46 FunctionOfLog
    # catch-all (class-3 deferred campaign C6b; the single-line
    # If[TrueQ[$LoadShowSteps], …] wrapper the census parser never
    # picked up — unwrap_showsteps_line).
    # class 6: 390 — the census count with no adjustment. Unlike class 3
    # this section has NO If[TrueQ[$LoadShowSteps], …] wrapper at all
    # (measured 2026-09-20: 0 LoadShowSteps lines over the 13 .m files),
    # so unwrap_showsteps_line finds nothing to recover and the census
    # and the emitter agree exactly
    # (probes/translation/05-class6-syntax-census.out).
    # class 4: 8 — NOT the section's 2,080 (spec 0.3): only the
    # CLASS4_SUBSET records, the bridge and six of 4.7.5's substitution
    # catch-alls (inert-trig substrate plan, Task 9; r71, Task 10) and
    # 4.7.5's re-activating give-up r72 (Task 10 fix round 1). It grows with the
    # subset until the class-4 port replaces it with the full total.
    # class 9: 86 — 19 (9.2 Piecewise linear functions) + 67 (9.3
    # Miscellaneous integration rules), spec 2026-09-22 A3.
    # `grep -c '^Int\['` over the two .m files gives 95, not 86: it counts
    # BOTH branches of 9.3's nine single-line
    # If[TrueQ[$LoadShowSteps], …] wrappers (unwrap_showsteps_line keeps
    # only the plain branch — 9 fewer records, 95 - 9 = 86).
    EXPECTED_TOTAL = {1: 2710 + EXTRA_TOTAL + NINE_ONE_TOTAL, 2: 125,
                      3: 334, 4: sum(len(v) for v in CLASS4_SUBSET.values()),
                      6: 390, 9: 86}[class_num]


def _emit_source(rel_m, key, only, total, load_lines, note=""):
    # A2.1: every class, before strip_comments. A2.2: class 9 only, after
    # strip_comments and before unwrap_showsteps_lines (applied to class 1
    # it would drop 1_4_1 r7 -- see unwrap_showsteps_multiline).
    stripped = strip_comments(drop_comment_only_lines((RUBI / rel_m).read_text()))
    if CLASS == 9:
        stripped = unwrap_showsteps_multiline(stripped)
    text = unwrap_showsteps_lines(stripped)
    runs = rule_runs(text)
    out = OUT / f"{key}.mac"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(emit_file(rel_m, runs, key))
    if CLASS == 4:
        n = len(CLASS4_SUBSET[key])
        print(f"  {key}: {n} of {len(runs)} rules (CLASS4_SUBSET){note}")
        load_lines.append(f"%mr_load_sibling(\"rules/class{CLASS}/{key}.mac\", "
                          f"'mr_witness_{key})$")
        return total + n
    print(f"  {key}: {len(runs)} rules{note}")
    load_lines.append(f"%mr_load_sibling(\"rules/class{CLASS}/{key}.mac\", "
                      f"'mr_witness_{key})$")
    return total + len(runs)


# ----------------------------------------------------------------------
# Rewrite tables (inert-trig substrate design 3.2, Task 4)
#
# Three of Rubi's utility functions are written as `Name[pattern] := rhs /;
# cond` clauses — the shape an Int rule has — so they are generated through
# the SAME emitter (emit_rule with fname) into %mr_defrewrite records, one
# table per function, in source order (the order IS priority: %mr_rewrite
# answers with the first clause that binds and whose cond accepts).

REWRITE_SOURCE = "Rubi/IntegrationUtilityFunctions.m"
REWRITE_OUT = ROOT / "rules" / "utils" / "inert_trig_rewrites.mac"

# (table key, Rubi function, clause count). The counts were MEASURED
# 2026-09-20 over the pinned clone (spec 2.4: 75 / 61 / 4, of which
# 74 / 60 / 3 carry a condition) and are ASSERTED here: a reference-clone
# bump that adds or drops a clause fails generation loudly instead of
# silently changing a table.
REWRITE_FUNCTIONS = [
    ("uitf", "UnifyInertTrigFunction", 75),
    ("fitf", "FixInertTrigFunction", 61),
    ("rit", "ReduceInertTrig", 4),
    # Section 9 (spec 2026-09-22 A1): EulerIntegrandQ's five
    # `EulerIntegrandQ[<pattern>, x_Symbol] := True/False [/; cond]` clauses
    # (IntegrationUtilityFunctions.m L5017, L5022, L5028, L5034, L5038; L5022
    # and L5028 are identical in the source and both stay, since the table
    # is faithful to the file). MEASURED 2026-09-20 over the pinned clone: 5.
    ("eiq", "EulerIntegrandQ", 5),
]


def utility_runs(src_stripped, fname):
    """The clause runs of utility function fname in a comment-stripped
    source: rule_runs' convention (a run starts at a column-0 line and a
    blank line ends it, except after a dangling ':='), with the column-0
    marker `fname[` instead of `Int[`. `fname::usage = …` and
    `Clear[fname]` lines do not start with `fname[`, so they never open a
    run."""
    lines = src_stripped.split("\n")
    runs, cur = [], None
    for line in lines:
        if line.startswith(fname + "["):
            if cur is not None:
                runs.append(cur)
            cur = [line]
        elif cur is not None:
            if line.strip() == "" and \
                    not "\n".join(cur).rstrip().endswith(":="):
                runs.append(cur)
                cur = None
            else:
                cur.append(line)
    if cur is not None:
        runs.append(cur)
    return runs


def bare_clause(lhs, key, n):
    """True when every argument of the clause's LHS is a bare named Blank
    (UnifyInertTrigFunction[u_, x_], ReduceInertTrig[func_, m_, u_]): the
    most general pattern of its arity.

    Such a clause goes to the END of its table, after the others in source
    order. Mathematica does not try a function's definitions in source
    order: it places a more specific definition before a more general one,
    and a bare-Blank definition is the most general there is, so it is tried
    last whatever its position in the file. %mr_rewrite walks the table in
    list order, so position is the only way to say it — the same argument
    the design makes for the Int rules' bare-u_ records (inert-trig
    substrate design 3.3). It matters here: UnifyInertTrigFunction's
    catch-all u_ is clause 68 of 75 (IntegrationUtilityFunctions.m L7294),
    and in source order it would make clauses 69-75 unreachable. Record
    numbers stay the source clause numbers; only the table order moves."""
    ev = _evaluated(lhs, key, n, "LHS")
    return all(isinstance(a, tuple) and len(a) == 3 and a[0] == "Pattern"
               and a[2] == ("Blank",) for a in ev[1:])


def emit_rewrites_file(rubi=None):
    """The whole rules/utils/inert_trig_rewrites.mac text."""
    rubi = rubi or RUBI
    src = strip_comments((rubi / REWRITE_SOURCE).read_text())
    header = ("/* rules/utils/inert_trig_rewrites.mac — GENERATED; do not "
              "edit.\n"
              f" * Source: Rubi 4 {PIN}\n"
              f" *          {REWRITE_SOURCE}\n"
              " * Regenerate: python3 generator/generate_rules.py --rewrites "
              "*/\n"
              f"{MIT}\n\n")
    body, tables, counts = [], [], []
    for key, fname, expected in REWRITE_FUNCTIONS:
        runs = utility_runs(src, fname)
        if len(runs) != expected:
            raise GenError(f"{fname}: {len(runs)} clauses in "
                           f"{REWRITE_SOURCE}, expected {expected} "
                           f"(measured 2026-09-20) — the reference clone "
                           f"changed; re-measure before regenerating")
        names, tail = [], []
        for n, run in enumerate(runs, start=1):
            text = "\n".join(run)
            if ":=" not in text:
                raise GenError(f"{key} r{n}: unparseable clause (no ':='): "
                               f"{text[:60]!r}")
            lhs, rhs, cond = split_rule_outer(text)
            cond = clean_cond(cond, key, n)
            rule_vars = pattern_vars(lhs)
            try:
                body.append(emit_rule((lhs, rhs, cond), key, n, rule_vars,
                                      fname=fname))
            except GenError:
                raise
            except Exception as ex:
                raise GenError(f"{key} r{n}: {type(ex).__name__}: {ex} "
                               f"(lhs {lhs[:60]!r})") from ex
            (tail if bare_clause(lhs, key, n) else names).append(
                f"_mr_rw_{key}_r{n}")
            body.append("")
        tables.append(f"mr_rw_{key} : [ {', '.join(names + tail)} ]$")
        tables.append(f"mr_rw_count_{key} : {len(runs)}$")
        counts.append(f"{key} {len(runs)}")
    return (header + "\n".join(body + tables)
            + "\nmr_witness_inert_trig_rewrites() := true$\n"), counts


def generate_rewrites():
    text, counts = emit_rewrites_file()
    REWRITE_OUT.parent.mkdir(parents=True, exist_ok=True)
    REWRITE_OUT.write_text(text)
    print(f"  {REWRITE_OUT.relative_to(ROOT)}: " + ", ".join(counts))


def main(class_num=None):
    if class_num is None and "--rewrites" in sys.argv:
        generate_rewrites()
        return
    if class_num is None:
        class_num = (int(sys.argv[sys.argv.index("--class") + 1])
                     if "--class" in sys.argv else 1)
    configure(class_num)
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].replace(".", "_")
    total = 0
    load_lines, table_terms = [], []
    for rel_m in load_class_files(RUBI):
        key = key_of(rel_m)
        if only and key != only:
            continue
        # class 9: a class-9 key silently overwriting a class-1 file
        # (rules/class1/9_1.mac, the legacy "9.1 Integrand simplification
        # rules" port) would define a second mr_rules_9_1 and neither
        # loader would notice -- loud instead (Task 10).
        if CLASS == 9 and (ROOT / "rules" / "class1" / f"{key}.mac").exists():
            raise GenError(f"class-9 key {key} collides with "
                           f"rules/class1/{key}.mac")
        total = _emit_source(rel_m, key, only, total, load_lines)
        table_terms.append(f"mr_rules_{key}")
    if CLASS == 1:
        # The five corpus-tested dead siblings (EXTRA_CLASS1), `b`-suffixed,
        # table position immediately after their same-numbered sibling.
        for rel_m in EXTRA_CLASS1:
            if not (RUBI / rel_m).exists():
                raise GenError(f"EXTRA_CLASS1 file missing: {rel_m}")
            base = key_of(rel_m)
            key = base + "b"
            if only and key != only:
                continue
            total = _emit_source(rel_m, key, only, total, load_lines,
                                 " (extra, corpus-matched dead file)")
            sib = f"mr_rules_{base}"
            pos = table_terms.index(sib) + 1 if sib in table_terms \
                else len(table_terms)
            table_terms.insert(pos, f"mr_rules_{key}")
        if not (RUBI / NINE_ONE).exists():
            raise GenError(f"9.1 source missing: {NINE_ONE}")
        if not only or only == "9_1":
            total = _emit_source(NINE_ONE, "9_1", only, total, load_lines,
                                 " (legacy 9.1, end of the class-1 table)")
            table_terms.append("mr_rules_9_1")
    expected = EXPECTED_TOTAL
    note = (f"OK (== {expected})" if (total == expected and not only)
            else ("partial (--only)" if only
                  else f"MISMATCH (expected {expected})"))
    print(f"TOTAL: {total} rules — {note}")
    if not only and total != expected:
        raise GenError(f"rule total {total} != {expected} "
                       f"(T1 census + EXTRA_CLASS1 + 9.1 for class 1); "
                       f"aborting")
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
