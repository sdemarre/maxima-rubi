# --- Patterns as evaluated FullForm s-expressions (matcher substrate spec
# docs/superpowers/specs/2026-09-12-matcher-substrate-design.md section
# 3.4). The reader (generator/mma_reader.py) parses a pattern text and
# emulates Mathematica's evaluation of it; maxima_rubi_dispatch.lisp
# prepares the s-expression with MR-MATCH.

_PATTERN_OBJECTS = {"Pattern", "Blank", "BlankSequence", "BlankNullSequence",
                    "Optional", "Condition", "PatternTest"}


def _evaluated(text, key, n, what):
    """Reader parse + evaluation of a pattern text. A G-9 risk effect (an
    evaluation the reader does not emulate) is a GenError."""
    try:
        tree = rd.parse(text)
    except rd.ParseError as ex:
        raise GenError(f"{key} r{n}: reader cannot parse the {what} "
                       f"{text[:60]!r}: {ex}")
    ev, effects = rd.evaluate_lhs(tree)
    risks = [e for e in effects if e.startswith("risk:")]
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
    return _sexp(out, key, n)


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
            return f"({_input_form(args[0])})^({_input_form(args[1])})"
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
