#!/usr/bin/env python3
"""probes/matcher/02-mma-reader.py -- Mathematica InputForm reader for the
matcher expressibility probes (handoffs/2026-09-11-matcher-design.md, move 2).

Library module, loaded by the other 02-* probes through importlib (the file
name is not an importable module name).  Run directly it executes its
self-test:  python3 probes/matcher/02-mma-reader.py

What it provides:

  tokenize / parse      Mathematica InputForm -> FullForm trees.  A tree is
                        an atom (str = Symbol, Str = String, int, Fraction,
                        Real) or a tuple (head, arg1, ...) whose head is an
                        atom or a tree.  Operator precedences are
                        Mathematica's (Precedence[]); the parser produces the
                        FullForm the Mathematica *parser* produces
                        (a-b -> Plus[a, Times[-1, b]], a/b -> Times[a,
                        Power[b, -1]], x_. -> Optional[Pattern[x, Blank[]]],
                        f'[x] -> Derivative[1][f][x], ...).  A newline at
                        bracket depth 0 ends a complete expression, as in a
                        Mathematica .m file read by Get.
  evaluate_lhs          An EMULATION of the evaluation Mathematica applies to
                        the arguments of a definition's left-hand side
                        (Int has no Hold attributes when the rule files are
                        read with Get: Rubi.m:114 Clear[Int]; the HoldAll at
                        IntegrationUtilityFunctions.m:7743 is Block-local to
                        FixIntRules and acts on DownValues whose LHSs are
                        already evaluated).  Emulated: Sqrt/Exp -> Power,
                        exact numeric folding, Flat flattening of Plus/Times,
                        identities (Times[1,x], Plus[0,x], x^1, x^0, 1^x),
                        like-term / like-base collection, integer powers of
                        powers and of products.  Anything else Mathematica's
                        evaluator might do to a pattern (odd-function sign
                        pulls such as Sin[-x] -> -Sin[x], numeric radicals,
                        I^2) is NOT emulated; evaluate_lhs reports it as a
                        risk label instead.  There is no Mathematica on this
                        machine: every claim built on this function is a
                        derived claim, labelled as such by the probes.
  loaded_rule_files     The rule files Rubi.m LoadRules (reusing
                        probes/probe-rubi-anatomy/01-inventory.py).
  load_rules            Every rule of those files: the inventory's rule runs
                        (count asserted per file against 01-inventory's
                        count_rules), plus the single-line
                        If[TrueQ[$LoadShowSteps], <ShowStep rule>, <rule>]
                        wrappers, which the inventory convention does not
                        count (they do not start with Int[ at column 0).
  fullform / to_sexp    Printers: Mathematica FullForm text, and the
                        s-expression notation read by the Lisp side
                        (readtable-case :preserve, package MMA).
"""

import importlib.util
import re
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


class Str(str):
    """A Mathematica String atom (plain str is a Symbol)."""
    __slots__ = ()


class Real:
    """A machine real, kept with its source text."""
    __slots__ = ("text",)

    def __init__(self, text):
        self.text = text

    def __eq__(self, other):
        return isinstance(other, Real) and other.text == self.text

    def __hash__(self):
        return hash(("Real", self.text))

    def __repr__(self):
        return "Real(%s)" % self.text


class ParseError(Exception):
    def __init__(self, msg, eof=False):
        super().__init__(msg)
        self.eof = eof


def is_atom(e):
    return not isinstance(e, tuple)


def is_number(e):
    return isinstance(e, (int, Fraction, Real)) and not isinstance(e, bool)


def is_exact(e):
    return isinstance(e, (int, Fraction)) and not isinstance(e, bool)


def head_of(e):
    if isinstance(e, tuple):
        return e[0]
    if isinstance(e, Str):
        return "String"
    if isinstance(e, bool):
        raise TypeError("bool in tree")
    if isinstance(e, int):
        return "Integer"
    if isinstance(e, Fraction):
        return "Rational"
    if isinstance(e, Real):
        return "Real"
    return "Symbol"


# ----------------------------------------------------------------------
# Tokenizer

_NAME = r"[A-Za-z$][A-Za-z0-9$]*(?:`[A-Za-z$][A-Za-z0-9$]*)*"
_TOKEN_RE = re.compile(r"""
  (?P<nl>\n)
 |(?P<ws>[ \t\r\f]+)
 |(?P<named>\\\[[A-Za-z]+\])
 |(?P<str>"(?:[^"\\]|\\.)*")
 |(?P<pat>(?:%(name)s)?_{1,3}(?:\.(?![0-9])|%(name)s)?)
 |(?P<num>[0-9]+\.[0-9]*(?![.])|[0-9]*\.[0-9]+|[0-9]+)
 |(?P<name>%(name)s)
 |(?P<slot>\#\#?[0-9]*)
 |(?P<op>\^:=|::|:=|//\.|/\.|//|/;|/@|->|:>|&&|\|\||===|=!=|==|!=|<=|>=|
        @@@|@@|\+\+|--|\+=|-=|\*=|/=|<>|\.\.\.|\.\.|;;|~~|
        [-+*/^=<>!&|?:;,()\[\]{}@'.~])
""" % {"name": _NAME}, re.X)

# named characters that act as operators outside strings (the only one found
# live in the rule files and IntegrationUtilityFunctions.m is \[Star]; any
# other named character outside a string is a parse error, reported)
_NAMED_OPS = {"Star": "Star"}


class Tok:
    __slots__ = ("kind", "text", "nl", "pos")

    def __init__(self, kind, text, nl, pos):
        self.kind, self.text, self.nl, self.pos = kind, text, nl, pos

    def __repr__(self):
        return "Tok(%s,%r%s)" % (self.kind, self.text, ",nl" if self.nl else "")


def tokenize(src):
    toks = []
    pos, n, nl = 0, len(src), False
    while pos < n:
        m = _TOKEN_RE.match(src, pos)
        if m is None:
            raise ParseError("bad character %r at %d" % (src[pos], pos))
        kind = m.lastgroup
        text = m.group(kind)
        pos = m.end()
        if kind == "nl":
            nl = True
            continue
        if kind == "ws":
            continue
        if kind == "named":
            name = text[2:-1]
            if name not in _NAMED_OPS:
                raise ParseError("named character %s outside a string" % text)
            kind, text = "op", "\\[%s]" % name
        toks.append(Tok(kind, text, nl, m.start()))
        nl = False
    toks.append(Tok("eof", "", nl, n))
    return toks


# ----------------------------------------------------------------------
# Parser (Pratt), Mathematica precedences

_INFIX = {
    ";": 10, "=": 40, ":=": 40, "^:=": 40, "+=": 100, "-=": 100, "*=": 100,
    "/=": 100, "&": 90, "//": 70, "/.": 110, "//.": 110, "->": 120, ":>": 120,
    "/;": 130, "~~": 135, ":": 140, "|": 160, "..": 170, "...": 170,
    "||": 214, "&&": 215, "==": 290, "!=": 290, "<": 290, ">": 290,
    "<=": 290, ">=": 290, "===": 290, "=!=": 290, "+": 310, "-": 310,
    "\\[Star]": 390, "*": 400, "/": 470, ".": 490, "^": 590, "<>": 600,
    "!": 610, "@@": 620, "@@@": 620, "/@": 620, "@": 640, "'": 670,
    "?": 680, "[": 1000, "::": 1100, "++": 660, "--": 660,
}
_RIGHT = {"=", ":=", "^:=", "->", ":>", "^", "@@", "@@@", "/@", "@"}
_NARY = {"+": "Plus", "*": "Times", "||": "Or", "&&": "And", "|": "Alternatives",
         "<>": "StringJoin", "\\[Star]": "Star", ".": "Dot", "~~": "StringExpression"}
_BINARY = {"=": "Set", ":=": "SetDelayed", "^:=": "UpSetDelayed", "+=": "AddTo",
           "-=": "SubtractFrom", "*=": "TimesBy", "/=": "DivideBy",
           "/.": "ReplaceAll", "//.": "ReplaceRepeated", "->": "Rule",
           ":>": "RuleDelayed", "/;": "Condition", "==": "Equal",
           "!=": "Unequal", "<": "Less", ">": "Greater", "<=": "LessEqual",
           ">=": "GreaterEqual", "===": "SameQ", "=!=": "UnsameQ",
           "@@": "Apply", "/@": "Map", "?": "PatternTest"}
_START_KINDS = {"num", "str", "name", "pat", "slot"}
_PATTERN_HEADS = {"Pattern", "Blank", "BlankSequence", "BlankNullSequence",
                  "Optional"}


def _neg(e):
    if is_number(e) and not isinstance(e, Real):
        return -e
    if isinstance(e, Real):
        t = e.text
        return Real(t[1:] if t.startswith("-") else "-" + t)
    return ("Times", -1, e)


class Parser:
    def __init__(self, src):
        self.src = src
        self.toks = tokenize(src)
        self.i = 0
        self.depth = 0

    def peek(self):
        return self.toks[self.i]

    def next(self):
        t = self.toks[self.i]
        self.i += 1
        return t

    def expect(self, text):
        t = self.next()
        if t.text != text or t.kind == "str":
            raise ParseError("expected %r, got %r at %d" % (text, t.text, t.pos),
                             eof=t.kind == "eof")
        return t

    def at_stop(self, t):
        """A newline at bracket depth 0 ends a complete expression."""
        return t.kind == "eof" or (t.nl and self.depth == 0)

    def parse_statements(self):
        out = []
        while self.peek().kind != "eof":
            start = self.peek().pos
            e = self.parse_expr(0)
            out.append((start, e))
        return out

    def parse_one(self):
        e = self.parse_expr(0)
        t = self.peek()
        if t.kind != "eof":
            raise ParseError("trailing input %r at %d" % (t.text, t.pos))
        return e

    # -- expressions
    def parse_expr(self, rbp):
        t = self.next()
        left = self.nud(t)
        while True:
            t = self.peek()
            if self.at_stop(t):
                break
            if t.kind == "op":
                lbp = _INFIX.get(t.text)
                if lbp is None or lbp <= rbp:
                    # a juxtaposed "(" / "{" is implicit multiplication
                    if t.text in ("(", "{") and 400 > rbp:
                        left = self._nary("Times", left, self.parse_expr(400))
                        continue
                    if t.text in ("!",) and 400 > rbp and False:
                        pass
                    break
                self.next()
                left = self.led(t, left, lbp)
            elif t.kind in _START_KINDS:
                if 400 <= rbp:
                    break
                left = self._nary("Times", left, self.parse_expr(400))
            else:
                break
        return left

    def _nary(self, head, left, right):
        if isinstance(left, tuple) and left[0] == head and getattr(self, "_open_" + head, None) is not left:
            return left + (right,)
        return (head, left, right)

    def nud(self, t):
        k, s = t.kind, t.text
        if k == "num":
            if "." in s:
                return Real(s)
            return int(s)
        if k == "str":
            body = s[1:-1]
            return Str(re.sub(r'\\(.)', r'\1', body))
        if k == "name":
            return s
        if k == "slot":
            if s.startswith("##"):
                return ("SlotSequence", int(s[2:]) if s[2:] else 1)
            return ("Slot", int(s[1:]) if s[1:] else 1)
        if k == "pat":
            return self.pattern_token(s)
        if k == "op":
            if s == "(":
                self.depth += 1
                e = self.parse_expr(0)
                self.expect(")")
                self.depth -= 1
                return ("__paren__", e)
            if s == "{":
                self.depth += 1
                items = self.parse_seq("}")
                self.depth -= 1
                return ("List",) + tuple(items)
            if s == "-":
                return _neg(self.strip(self.parse_expr(480)))
            if s == "+":
                return self.parse_expr(480)
            if s == "!":
                return ("Not", self.strip(self.parse_expr(230)))
        raise ParseError("unexpected %r at %d" % (s, t.pos), eof=k == "eof")

    def pattern_token(self, s):
        m = re.fullmatch(r"(%s)?(_{1,3})(\.|%s)?" % (_NAME, _NAME), s)
        name, blanks, tail = m.group(1), m.group(2), m.group(3)
        bhead = {1: "Blank", 2: "BlankSequence", 3: "BlankNullSequence"}[len(blanks)]
        blank = (bhead,) if tail in (None, ".") else (bhead, tail)
        p = ("Pattern", name, blank) if name else blank
        if tail == ".":
            p = ("Optional", p)
        return p

    def parse_seq(self, closer):
        items = []
        if self.peek().text == closer and self.peek().kind == "op":
            self.next()
            return items
        while True:
            t = self.peek()
            if t.kind == "op" and t.text in (",", closer):
                items.append("Null")  # f[a,,b] / f[a,]
            else:
                items.append(self.strip(self.parse_expr(0)))
            t = self.next()
            if t.kind == "op" and t.text == closer:
                return items
            if not (t.kind == "op" and t.text == ","):
                raise ParseError("expected , or %s, got %r at %d" % (closer, t.text, t.pos),
                                 eof=t.kind == "eof")

    def strip(self, e):
        """Remove the paren marker at one level (parens only group)."""
        while isinstance(e, tuple) and e[0] == "__paren__":
            e = e[1]
        return e

    def led(self, t, left, lbp):
        s = t.text
        left_s = self.strip(left)
        if s == "[":
            if self.peek().kind == "op" and self.peek().text == "[" and \
                    self.peek().pos == t.pos + 1:
                self.next()
                self.depth += 1
                items = self.parse_seq("]")
                self.expect("]")
                self.depth -= 1
                return ("Part", left_s) + tuple(items)
            self.depth += 1
            items = self.parse_seq("]")
            self.depth -= 1
            return (left_s,) + tuple(items)
        if s == "'":
            n = 1
            while self.peek().kind == "op" and self.peek().text == "'":
                self.next()
                n += 1
            return (("Derivative", n), left_s)
        if s == "&":
            return ("Function", left_s)
        if s == "!":
            return ("Factorial", left_s)
        if s in ("..", "..."):
            return ("Repeated" if s == ".." else "RepeatedNull", left_s)
        if s in ("++", "--"):
            return ("Increment" if s == "++" else "Decrement", left_s)
        if s == "::":
            t2 = self.next()
            return ("MessageName", left_s, Str(t2.text))
        if s == ";":
            nt = self.peek()
            if self.at_stop(nt) or (nt.kind == "op" and nt.text in (")", "]", "}", ",")):
                right = "Null"
            else:
                right = self.strip(self.parse_expr(lbp))
            if isinstance(left, tuple) and left[0] == "CompoundExpression":
                return left + (right,)
            return ("CompoundExpression", left_s, right)
        if s == "//":
            right = self.strip(self.parse_expr(lbp))
            return (right, left_s)
        rbp = lbp - 1 if s in _RIGHT else lbp
        if s == "^":
            right = self.strip(self.parse_expr(rbp))
            return ("Power", left_s, right)
        if s == "/":
            right = self.strip(self.parse_expr(rbp))
            return self._times2(left, ("Power", right, -1))
        if s == "-":
            right = self.strip(self.parse_expr(rbp))
            return self._plus2(left, _neg(right))
        if s == ":":
            right = self.strip(self.parse_expr(lbp))
            if isinstance(left_s, str):
                return ("Pattern", left_s, right)
            return ("Optional", left_s, right)
        if s == "@":
            right = self.strip(self.parse_expr(rbp))
            return (left_s, right)
        if s == "@@@":
            right = self.strip(self.parse_expr(rbp))
            return ("Apply", left_s, right, ("List", 1))
        if s in _NARY:
            head = _NARY[s]
            right = self.strip(self.parse_expr(rbp))
            if isinstance(left, tuple) and left[0] == head:
                return left + (right,)
            return (head, left_s, right)
        if s in _BINARY:
            right = self.strip(self.parse_expr(rbp))
            return (_BINARY[s], left_s, right)
        raise ParseError("no infix rule for %r at %d" % (s, t.pos))

    def _times2(self, left, right):
        if isinstance(left, tuple) and left[0] == "Times":
            return left + (right,)
        return ("Times", self.strip(left), right)

    def _plus2(self, left, right):
        if isinstance(left, tuple) and left[0] == "Plus":
            return left + (right,)
        return ("Plus", self.strip(left), right)


def _unparen(e):
    if isinstance(e, tuple):
        if e[0] == "__paren__":
            return _unparen(e[1])
        return tuple(_unparen(x) for x in e)
    return e


def parse(src):
    """Parse one expression (the whole text)."""
    return _unparen(Parser(src).parse_one())


def parse_statements(src):
    """Parse a file body into [(offset, expr), ...]."""
    return [(o, _unparen(e)) for o, e in Parser(src).parse_statements()]


# ----------------------------------------------------------------------
# Printers

def fullform(e):
    if isinstance(e, tuple):
        return "%s[%s]" % (fullform(e[0]), ", ".join(fullform(a) for a in e[1:]))
    if isinstance(e, Str):
        return '"%s"' % e.replace("\\", "\\\\").replace('"', '\\"')
    if isinstance(e, Fraction):
        return "Rational[%d, %d]" % (e.numerator, e.denominator)
    if isinstance(e, Real):
        return e.text
    return str(e)


_LISP_PLAIN = re.compile(r"[A-Za-z][A-Za-z0-9$]*\Z")


def to_sexp(e):
    if isinstance(e, tuple):
        return "(%s)" % " ".join(to_sexp(a) for a in e)
    if isinstance(e, Str):
        return '"%s"' % e.replace("\\", "\\\\").replace('"', '\\"')
    if isinstance(e, bool):
        raise TypeError("bool")
    if isinstance(e, int):
        return str(e)
    if isinstance(e, Fraction):
        return "%d/%d" % (e.numerator, e.denominator)
    if isinstance(e, Real):
        t = e.text
        return t + "0" if t.endswith(".") else t
    if _LISP_PLAIN.match(e):
        return e
    return "|%s|" % e.replace("|", "\\|")


def key(e):
    """A total order on trees (not Mathematica's canonical order)."""
    if isinstance(e, tuple):
        return (5, key(e[0]), len(e), tuple(key(a) for a in e[1:]))
    if isinstance(e, bool):
        raise TypeError("bool")
    if isinstance(e, (int, Fraction)):
        return (0, e)
    if isinstance(e, Real):
        return (1, e.text)
    if isinstance(e, Str):
        return (3, str(e))
    return (2, e)


# ----------------------------------------------------------------------
# LHS evaluation (emulation -- see the module docstring)

# heads the evaluator leaves structurally alone (pattern objects hold their
# names; Condition/PatternTest/HoldPattern/Verbatim hold their bodies)
_HOLD_ALL = {"Condition", "HoldPattern", "Verbatim", "Hold", "HoldForm",
             "Function", "Blank", "BlankSequence", "BlankNullSequence"}
# heads whose numeric / negated / Pi-shifted arguments Mathematica may rewrite
_INERT_HEADS = {"Pattern", "Optional", "Alternatives", "Except", "PatternTest",
                "Repeated", "RepeatedNull", "List", "Int", "Derivative"}


class Evaluator:
    def __init__(self):
        self.effects = set()

    def ev(self, e):
        if not isinstance(e, tuple):
            if e == "I":
                self.effects.add("risk:I")
            return e
        head = e[0]
        if isinstance(head, str) and head in _HOLD_ALL:
            return e
        if head == "Pattern":
            return ("Pattern", e[1], self.ev(e[2]))
        if head == "PatternTest":
            return ("PatternTest", self.ev(e[1])) + e[2:]
        h = self.ev(head) if isinstance(head, tuple) else head
        args = [self.ev(a) for a in e[1:]]
        if h == "Sqrt" and len(args) == 1:
            self.effects.add("parse:Sqrt")
            return self.power(args[0], Fraction(1, 2))
        if h == "Exp" and len(args) == 1:
            self.effects.add("parse:Exp")
            return self.power("E", args[0])
        if h == "Plus":
            return self.plus(args)
        if h == "Times":
            return self.times(args)
        if h == "Power" and len(args) == 2:
            return self.power(args[0], args[1])
        if h == "Rational" and len(args) == 2 and all(isinstance(a, int) for a in args):
            return self.number(Fraction(args[0], args[1]))
        if isinstance(h, str) and h not in _INERT_HEADS:
            for a in args:
                if is_number(a) or (isinstance(a, tuple) and a[0] == "Times"
                                    and is_number(a[1]) and a[1] < 0 if not isinstance(a[1] if isinstance(a, tuple) and len(a) > 1 else None, Real) else False):
                    self.effects.add("risk:numeric-or-negated-arg:%s" % h)
                if _mentions(a, "Pi") and h not in ("Plus", "Times", "Power"):
                    self.effects.add("risk:Pi-arg:%s" % h)
        return (h,) + tuple(args)

    @staticmethod
    def number(q):
        if isinstance(q, Fraction) and q.denominator == 1:
            return q.numerator
        return q

    def plus(self, args):
        flat = []
        for a in args:
            if isinstance(a, tuple) and a[0] == "Plus":
                flat.extend(a[1:])
            else:
                flat.append(a)
        total = 0
        nums = 0
        terms = {}
        order = []
        for a in flat:
            if is_exact(a):
                total += a
                nums += 1
                continue
            c, rest = _coef(a)
            k = key(rest)
            if k in terms:
                self.effects.add("eval:Plus-collect")
                terms[k] = (terms[k][0] + c, rest)
            else:
                terms[k] = (c, rest)
                order.append(k)
        if nums > 1:
            self.effects.add("eval:numeric-fold")
        out = []
        for k in order:
            c, rest = terms[k]
            if c == 0:
                continue
            out.append(rest if c == 1 else self.times([self.number(Fraction(c)), rest]))
        if total != 0:
            out.append(self.number(Fraction(total)))
        if nums and total == 0 and len(out) + 1 == len(flat) and nums == 1:
            self.effects.add("eval:Plus-identity")
        out.sort(key=key)
        if not out:
            return 0
        if len(out) == 1:
            return out[0]
        return ("Plus",) + tuple(out)

    def times(self, args):
        for _ in range(8):
            flat = []
            for a in args:
                if isinstance(a, tuple) and a[0] == "Times":
                    flat.extend(a[1:])
                else:
                    flat.append(a)
            coef = Fraction(1)
            nums = 0
            bases = {}
            order = []
            for a in flat:
                if is_exact(a):
                    coef *= a
                    nums += 1
                    continue
                if isinstance(a, tuple) and a[0] == "Power" and len(a) == 3:
                    b, x = a[1], a[2]
                else:
                    b, x = a, 1
                k = key(b)
                if k in bases:
                    if not is_exact(b):
                        self.effects.add("eval:Times-collect")
                    bases[k][1].append(x)
                else:
                    bases[k] = (b, [x])
                    order.append(k)
            if nums > 1:
                self.effects.add("eval:numeric-fold")
            if coef == 0:
                self.effects.add("eval:Times-zero")
                return 0
            if coef == 1 and nums:
                self.effects.add("eval:Times-identity")
            rebuilt = []
            again = False
            for k in order:
                b, xs = bases[k]
                x = xs[0] if len(xs) == 1 else self.plus(xs)
                f = self.power(b, x) if len(xs) > 1 or x != 1 else b
                if is_exact(f):
                    coef *= f
                    again = again or False
                    continue
                if isinstance(f, tuple) and f[0] == "Times":
                    again = True
                rebuilt.append(f)
            if again:
                args = [self.number(coef)] + rebuilt
                continue
            break
        rebuilt.sort(key=key)
        c = self.number(coef)
        if c != 1:
            rebuilt.insert(0, c)
        if not rebuilt:
            return 1
        if len(rebuilt) == 1:
            return rebuilt[0]
        return ("Times",) + tuple(rebuilt)

    def power(self, b, x):
        if x == 1 and is_exact(x):
            self.effects.add("eval:Power-identity")
            return b
        if x == 0 and is_exact(x):
            self.effects.add("eval:Power-zero")
            return 1
        if b == 1 and is_exact(b):
            self.effects.add("eval:Power-one-base")
            return 1
        if is_exact(b) and isinstance(x, int):
            if b == 0 and x < 0:
                self.effects.add("risk:ComplexInfinity")
                return ("Power", b, x)
            self.effects.add("eval:numeric-fold")
            return self.number(Fraction(b) ** x)
        if is_exact(b) and isinstance(x, Fraction):
            r = _exact_root(Fraction(b), x)
            if r is not None:
                self.effects.add("eval:numeric-fold")
                return r
            if b < 0 or abs(x) > 1:
                self.effects.add("risk:numeric-radical")
            return ("Power", b, x)
        if isinstance(x, int) and isinstance(b, tuple):
            if b[0] == "Power" and len(b) == 3:
                self.effects.add("eval:Power-of-Power")
                return self.power(b[1], self.times([b[2], x]))
            if b[0] == "Times":
                self.effects.add("eval:Power-distribute")
                return self.times([self.power(f, x) for f in b[1:]])
        if b == "I" and isinstance(x, int):
            self.effects.add("risk:I-power")
        return ("Power", b, x)


def _coef(a):
    if isinstance(a, tuple) and a[0] == "Times" and len(a) >= 3 and is_exact(a[1]):
        rest = a[2:]
        return Fraction(a[1]), (rest[0] if len(rest) == 1 else ("Times",) + rest)
    return Fraction(1), a


def _exact_root(q, x):
    """q^x for rational q and rational x when the result is rational."""
    if q < 0:
        return None
    p, d = x.numerator, x.denominator

    def iroot(n):
        r = round(n ** (1.0 / d)) if n > 0 else 0
        for c in (r - 1, r, r + 1):
            if c >= 0 and c ** d == n:
                return c
        return None
    rn, rd = iroot(q.numerator), iroot(q.denominator)
    if rn is None or rd is None:
        return None
    v = Fraction(rn, rd) ** p
    return v.numerator if v.denominator == 1 else v


def _mentions(e, sym):
    if isinstance(e, tuple):
        return any(_mentions(a, sym) for a in e)
    return e == sym and not isinstance(e, Str)


def evaluate_lhs(e):
    """-> (evaluated tree, sorted effect labels)."""
    ev = Evaluator()
    out = ev.ev(e)
    return out, sorted(ev.effects)


# ----------------------------------------------------------------------
# Rule files

def _load_inventory():
    p = REPO / "probes" / "probe-rubi-anatomy" / "01-inventory.py"
    spec = importlib.util.spec_from_file_location("inv01", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


INV = _load_inventory()


def rubi_root():
    return REPO / "reference" / "rubi" / "Rubi"


def file_key(path):
    return path.name.split(" ", 1)[0] + ".m"


def loaded_rule_files():
    """[(key, rel, path)] in Rubi.m LoadRules order."""
    rd = rubi_root()
    out = []
    for parts, _gated in INV.parse_load_rules((rd / "Rubi.m").read_text()):
        if parts[0].startswith("$"):
            continue
        p = (rd / "IntegrationRules").joinpath(*parts)
        if not p.name.endswith(".m"):
            p = p.with_name(p.name + ".m")
        rel = p.relative_to(rd / "IntegrationRules").as_posix()
        out.append((file_key(p), rel, p))
    keys = [k for k, _r, _p in out]
    dup = {k for k in keys if keys.count(k) > 1}
    if dup:
        raise SystemExit("duplicate file keys: %s" % sorted(dup))
    return out


def rule_runs(stripped):
    """01-inventory.count_rules' run convention, with 1-based start lines."""
    lines = stripped.split("\n")
    runs, cur, start = [], None, 0
    for i, line in enumerate(lines, 1):
        if line.startswith("Int["):
            if cur is not None:
                runs.append((start, cur))
            cur, start = [line], i
        elif cur is not None:
            if line.strip() == "" and not "\n".join(cur).rstrip().endswith(":="):
                runs.append((start, cur))
                cur = None
            else:
                cur.append(line)
    if cur is not None:
        runs.append((start, cur))
    return [(s, "\n".join(r)) for s, r in runs if ":=" in "\n".join(r)]


_SHOWSTEPS_ONE_LINE = re.compile(r"^If\[TrueQ\[\$LoadShowSteps\],.*\]\s*$")


class Rule:
    __slots__ = ("id", "key", "rel", "line", "text", "source", "tree", "error",
                 "error_eof", "lhs", "rhs", "cond", "note", "extras", "lhs_eval")

    def __init__(self, **kw):
        for s in self.__slots__:
            setattr(self, s, kw.get(s))
        if self.extras is None:
            self.extras = []


def _clean_run(text):
    """The multi-line If[TrueQ[$LoadShowSteps], A, B] of 1.4.1 leaves a
    trailing branch separator ',' or the If's closing ']' on a run (the
    generator's clean_cond, FIX E8, does the same)."""
    t = text.rstrip()
    note = None
    if t.endswith(","):
        t, note = t[:-1], "multiline-ShowSteps-If branch 1"
    depth = 0
    in_str = False
    for ch in t:
        if ch == '"':
            in_str = not in_str
        elif not in_str:
            depth += ch in "[({"
            depth -= ch in "])}"
    if depth == -1 and t.endswith("]"):
        t, note = t[:-1], "multiline-ShowSteps-If branch 2"
    return t, note


def split_rule(tree):
    """SetDelayed[Int[...], rhs] -> (lhs, body, outer condition or None)."""
    if not (isinstance(tree, tuple) and tree[0] == "SetDelayed" and len(tree) == 3):
        raise ParseError("not a SetDelayed: %s" % fullform(tree)[:80])
    lhs, rhs = tree[1], tree[2]
    if not (isinstance(lhs, tuple) and lhs[0] == "Int"):
        raise ParseError("LHS head is not Int: %s" % fullform(lhs)[:80])
    cond = None
    if isinstance(rhs, tuple) and rhs[0] == "Condition" and len(rhs) == 3:
        rhs, cond = rhs[1], rhs[2]
    return lhs, rhs, cond


def load_rules():
    """Every rule of every loaded file.  Returns (rules, per_file_counts).

    A rule run is parsed as a sequence of statements: the first must be the
    Int definition; further statements glued onto the run (no blank line in
    between) are kept in Rule.extras -- helper definitions such as
    IntLinearQ[...] := ..., or single-line ShowSteps If wrappers (those are
    also collected on their own by the line scan below).  A run that ends
    syntactically incomplete (a comment-only line inside a condition strips
    to a blank line, which ends an inventory run) is extended line by line
    until it parses; Rule.note records the extension."""
    rules, counts = [], []
    for key_, rel, path in loaded_rule_files():
        stripped = INV.strip_comments(path.read_text())
        all_lines = stripped.split("\n")
        runs = rule_runs(stripped)
        inv_count = INV.count_rules(stripped)[0]
        if len(runs) != inv_count:
            raise SystemExit("%s: %d runs vs inventory %d" % (rel, len(runs), inv_count))
        n_wrapped = 0
        for line, text in runs:
            t, note = _clean_run(text)
            r = Rule(id="%s L%d" % (key_, line), key=key_, rel=rel, line=line,
                     text=t, source="run", note=note)
            end = line + text.count("\n")  # 1-based last line of the run
            for extra in range(0, 40):
                _parse_rule(r)
                if not (r.error and r.error_eof):
                    break
                nxt = end + extra  # index of the next line (0-based = 1-based end)
                if nxt >= len(all_lines) or all_lines[nxt].startswith(("Int[", "If[")):
                    break
                r.text = r.text + "\n" + all_lines[nxt]
                r.note = "run extended by %d line(s) past a stripped comment line" % (extra + 1)
            rules.append(r)
        for i, ln in enumerate(stripped.split("\n"), 1):
            if _SHOWSTEPS_ONE_LINE.match(ln):
                try:
                    tree = parse(ln)
                except ParseError as ex:
                    rules.append(Rule(id="%s L%d" % (key_, i), key=key_, rel=rel, line=i,
                                      text=ln, source="showsteps-line", error=str(ex)))
                    continue
                if not (tree[0] == "If" and len(tree) == 4):
                    raise SystemExit("%s L%d: unexpected If shape" % (rel, i))
                n_wrapped += 1
                show, plain = tree[2], tree[3]
                r = Rule(id="%s L%d" % (key_, i), key=key_, rel=rel, line=i,
                         text=ln, source="showsteps-line")
                r.tree = plain
                try:
                    r.lhs, r.rhs, r.cond = split_rule(plain)
                    s_lhs, _s_rhs, _s_cond = split_rule(show)
                    r.note = "ShowStep branch LHS %s" % (
                        "identical" if s_lhs == r.lhs else "DIFFERS")
                except ParseError as ex:
                    r.error = str(ex)
                rules.append(r)
        counts.append((key_, rel, inv_count, n_wrapped))
    return rules, counts


def _parse_rule(r):
    r.error, r.error_eof, r.extras = None, False, []
    try:
        stmts = parse_statements(r.text)
        if not stmts:
            raise ParseError("empty run")
        r.tree = stmts[0][1]
        r.extras = [e for _o, e in stmts[1:]]
        r.lhs, r.rhs, r.cond = split_rule(r.tree)
    except ParseError as ex:
        r.error, r.error_eof = str(ex), ex.eof


Rule.__slots__  # (error_eof is set dynamically below)


def file_statements(path):
    """Whole-file parse, as Get reads it: [(line, expr)] or raises."""
    stripped = INV.strip_comments(path.read_text())
    return [(stripped.count("\n", 0, o) + 1, e) for o, e in parse_statements(stripped)]


def classify_statement(e):
    """'int-rule' | 'showsteps-if' | 'definition:<name>' | 'other:<head>'."""
    if isinstance(e, tuple) and e[0] == "CompoundExpression":
        e = e[1]
    if isinstance(e, tuple) and e[0] in ("SetDelayed", "Set"):
        lhs = e[1]
        if isinstance(lhs, tuple) and lhs[0] == "Int":
            return "int-rule"
        h = lhs[0] if isinstance(lhs, tuple) else lhs
        while isinstance(h, tuple):
            h = h[0]
        return "definition:%s" % h
    if isinstance(e, tuple) and e[0] == "If" and len(e) >= 2 and \
            e[1] == ("TrueQ", "$LoadShowSteps"):
        return "showsteps-if"
    h = e[0] if isinstance(e, tuple) else e
    while isinstance(h, tuple):
        h = h[0]
    return "other:%s" % h


# ----------------------------------------------------------------------
# Self-test

def _selftest():
    cases = [
        ("Int[1/x_, x_Symbol]", True,
         "Int[Power[Pattern[x, Blank[]], -1], Pattern[x, Blank[Symbol]]]"),
        ("Int[(a_. + b_.*x_)^m_., x_Symbol]", True,
         "Int[Power[Plus[Optional[Pattern[a, Blank[]]], Times[Optional[Pattern[b, Blank[]]], "
         "Pattern[x, Blank[]]]], Optional[Pattern[m, Blank[]]]], Pattern[x, Blank[Symbol]]]"),
        ("Sqrt[a_ + b_.*x_]", True,
         "Power[Plus[Pattern[a, Blank[]], Times[Optional[Pattern[b, Blank[]]], Pattern[x, Blank[]]]], Rational[1, 2]]"),
        ("1/(c_*x_)", True, "Times[Power[Pattern[c, Blank[]], -1], Power[Pattern[x, Blank[]], -1]]"),
        ("(d_.*x_)^2", True, "Times[Power[Optional[Pattern[d, Blank[]]], 2], Power[Pattern[x, Blank[]], 2]]"),
        ("a - b*c", False, "Plus[a, Times[-1, Times[b, c]]]"),
        ("a - b*c", True, "Plus[a, Times[-1, b, c]]"),
        ("-x^2", False, "Times[-1, Power[x, 2]]"),
        ("x^-1", False, "Power[x, -1]"),
        ("a^b^c", False, "Power[a, Power[b, c]]"),
        ("f_'[x_]*g_[x_]", False,
         "Times[Derivative[1][Pattern[f, Blank[]]][Pattern[x, Blank[]]], Pattern[g, Blank[]][Pattern[x, Blank[]]]]"),
        ("Derivative[n_][f_][x_]", False,
         "Derivative[Pattern[n, Blank[]]][Pattern[f, Blank[]]][Pattern[x, Blank[]]]"),
        ('EqQ::usage = "a \\"b\\" c"', False, 'Set[MessageName[EqQ, "usage"], "a \\"b\\" c"]'),
        ("MatchQ[u, a_.+b_.*x /; FreeQ[{a,b},x]]", False,
         "MatchQ[u, Condition[Plus[Optional[Pattern[a, Blank[]]], Times[Optional[Pattern[b, Blank[]]], x]], FreeQ[List[a, b], x]]]"),
        ("lst[[3]]^(1/lst[[2]])", False,
         "Power[Part[lst, 3], Times[1, Power[Part[lst, 2], -1]]]"),
        ("Function[BinomialQ[#,x]]", False, "Function[BinomialQ[Slot[1], x]]"),
        ("x_:0", False, "Optional[Pattern[x, Blank[]], 0]"),
        ("u:_Plus|_Times", False, "Pattern[u, Alternatives[Blank[Plus], Blank[Times]]]"),
        ("a*b \\[Star] c", False, "Star[Times[a, b], c]"),
        ("a || b && c", False, "Or[a, And[b, c]]"),
        ("2 (a+b)", False, "Times[2, Plus[a, b]]"),
        ("x_^m_.*x_^n_.", True,
         "Power[Pattern[x, Blank[]], Plus[Optional[Pattern[m, Blank[]]], Optional[Pattern[n, Blank[]]]]]"),
        ("E^(a_.+b_.*x_)", True,
         "Power[E, Plus[Optional[Pattern[a, Blank[]]], Times[Optional[Pattern[b, Blank[]]], Pattern[x, Blank[]]]]]"),
        ("(a_+b_.*x_)^(1/2)*4^(1/2)", True,
         "Times[2, Power[Plus[Pattern[a, Blank[]], Times[Optional[Pattern[b, Blank[]]], Pattern[x, Blank[]]]], Rational[1, 2]]]"),
        ("With[{m = 2}, a /; b] /; c", False,
         "Condition[With[List[Set[m, 2]], Condition[a, b]], c]"),
    ]
    bad = 0
    for src, ev, want in cases:
        e = parse(src)
        if ev:
            e, _eff = evaluate_lhs(e)
        got = fullform(e)
        ok = got == want
        bad += not ok
        print("%s %s%s -> %s%s" % ("PASS:" if ok else "FAIL:", src, " (eval)" if ev else "",
                                   got, "" if ok else "\n      want " + want))
    # statement splitting at depth 0 newlines
    st = parse_statements("f[x_] :=\n  x+1\ng[y_] := y\n")
    ok = [fullform(e) for _o, e in st] == ["SetDelayed[f[Pattern[x, Blank[]]], Plus[x, 1]]",
                                           "SetDelayed[g[Pattern[y, Blank[]]], y]"]
    bad += not ok
    print("%s statement split -> %s" % ("PASS:" if ok else "FAIL:", [fullform(e) for _o, e in st]))
    print("Results: %d passed, %d failed" % (len(cases) + 1 - bad, bad))
    return bad


if __name__ == "__main__":
    sys.exit(1 if _selftest() else 0)
