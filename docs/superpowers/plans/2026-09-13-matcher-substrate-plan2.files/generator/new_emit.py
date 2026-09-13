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


def emit_rule(run, key, n, rule_vars):
    """One rule run (lhs, rhs, cond) -> its cond and repl functions and its
    %mr_defrule registration, as Maxima text (spec 3.4). rule_vars is the
    set of capture names (from the lhs)."""
    lhs, rhs, cond = run
    if not re.match(r"^Int\[(.*),\s*x_Symbol\]$", lhs.strip(), re.DOTALL):
        raise GenError(f"{key} r{n}: cannot strip Int[...]: {lhs!r}")
    ctx = {"key": key, "n": n, "vars": rule_vars, "markers": None, "mq": 0}
    pattern = pattern_sexp(lhs, key, n, rule_vars)
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
        repl_txt = translate(drop_optionals(f"{head}[{decls},{body}]",
                                            rule_vars), ctx)
        locals_, assigns = _scope_locals(
            head, translate(drop_optionals(decls, rule_vars), ctx), key, n)
        test = translate(drop_optionals(inner_cond, rule_vars), ctx)
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
    return "\n".join([
        f"_mr_cond_{key}_r{n}(mm, x) := block([{locals_txt}],",
        f"  {bind_block},",
        f"  {cond_txt})$",
        f"_mr_repl_{key}_r{n}(mm, x) := block([{snap_locals_txt}],",
        f"  {snap_bind_block},",
        f"  {repl_txt})$",
        f'_mr_rule_{key}_r{n} : %mr_defrule("{key}", {n}, "{pattern}", '
        f"_mr_cond_{key}_r{n}, _mr_repl_{key}_r{n})$",
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
    for n, run in enumerate(runs, start=1):
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
        rule_names.append(f"_mr_rule_{key}_r{n}")
        body.append("")
    body.append(f"mr_rules_{key} : [ {', '.join(rule_names)} ]$")
    body.append(f"mr_rules_count_{key} : {len(runs)}$")
    body.append(f"mr_witness_{key}() := true$")
    return header + "\n".join(body) + "\n"
