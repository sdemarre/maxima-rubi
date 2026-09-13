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
