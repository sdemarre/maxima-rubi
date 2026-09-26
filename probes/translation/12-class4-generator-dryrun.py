#!/usr/bin/env python3
"""probes/translation/12-class4-generator-dryrun.py -- what the generator
needs before it can emit the WHOLE of class 4 (the "4 " files Rubi.m loads,
not the CLASS4_SUBSET the inert-trig substrate ported). Static, no Maxima;
never writes into rules/ (it calls emit_rule per rule, not _emit_source).

  python3 probes/translation/12-class4-generator-dryrun.py

For every rule run (numbered as the generator numbers them, after
unwrap_showsteps_lines), emit_rule is called with CLASS4_SUBSET bypassed.
Printed:

A. the generator errors, grouped: `unlisted head` per token (the closure
   probe's UNLISTED list, seen from the emitter), and G-9 "evaluation not
   emulated" refusals;
B. every G-9 risk flag the reader raises on a class-4 LHS or MatchQ
   pattern, per rule, with the pattern text -- ACCEPTED_RISKS entries
   included (a flag the table already accepts is marked `accepted`);
C. the bare-u_ Int records (bare_int_clause), i.e. what the tail gains.
"""
import collections
import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "generator"))
sys.argv = [sys.argv[0]]
import generate_rules as g  # noqa: E402

g.configure(4)
RISKS = []          # (key, n, effect, text)
_orig_eval = g.rd.evaluate_lhs
_cur = {}


def _recording_eval(tree):
    ev, effects = _orig_eval(tree)
    for e in effects:
        if e.startswith("risk:"):
            RISKS.append((_cur["key"], _cur["n"], e, _cur.get("text", "")))
    return ev, effects


g.rd.evaluate_lhs = _recording_eval
_orig_evaluated = g._evaluated


def _tracking_evaluated(text, key, n, what):
    _cur["text"] = f"{what}: {text}"
    return _orig_evaluated(text, key, n, what)


g._evaluated = _tracking_evaluated

files = []
for parts, _gated in g.parse_load_rules(
        g.strip_comments((g.RUBI / "Rubi" / "Rubi.m").read_text())):
    if parts and parts[0].startswith("4 "):
        files.append("Rubi/IntegrationRules/" + "/".join(parts) + ".m")

errors = collections.Counter()
error_first = {}
bare = []
total = 0
for rel in files:
    key = g.key_of(rel)
    stripped = g.strip_comments(g.drop_comment_only_lines((g.RUBI / rel).read_text()))
    runs = g.rule_runs(g.unwrap_showsteps_lines(stripped))
    for n, run in enumerate(runs, 1):
        total += 1
        _cur.update(key=key, n=n)
        text, _util = g.split_utility_def("\n".join(run))
        lhs, rhs, cond = g.split_rule_outer(text)
        err = io.StringIO()
        try:
            with contextlib.redirect_stderr(err):
                cond = g.clean_cond(cond, key, n)
                g.emit_rule((lhs, rhs, cond), key, n, g.pattern_vars(lhs))
        except SystemExit:
            msg = err.getvalue().strip().splitlines()[-1]
            msg = msg.split(": ", 2)[-1]
            if msg.startswith("unlisted head"):
                msg = msg.split(" — ")[0]
            else:
                msg = msg.split(": '")[0]
            errors[msg] += 1
            error_first.setdefault(msg, f"{key} r{n}")
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                if g.bare_int_clause(lhs, key, n):
                    bare.append(f"{key} r{n}")
        except SystemExit:
            pass

print(f"=== class 4: {len(files)} loaded files, {total} rule runs ===")
print()
print(f"== A. generator errors (CLASS4_SUBSET bypassed): "
      f"{sum(errors.values())} rules ==")
for msg, c in errors.most_common():
    print(f"  {c:4d}  {msg}   first at {error_first[msg]}")
print()
seen = set()
rows = []
for key, n, e, text in RISKS:
    if (key, n, e) in seen:
        continue
    seen.add((key, n, e))
    rows.append((key, n, e, text))
print(f"== B. G-9 risk flags on class-4 patterns: {len(rows)} "
      f"(rule, flag) pairs over {len({(k, n) for k, n, _, _ in rows})} rules ==")
by_flag = collections.Counter(e for _, _, e, _ in rows)
for e, c in by_flag.most_common():
    print(f"  {c:4d}  {e}")
for key, n, e, text in rows:
    acc = "accepted" if (key, n, e) in g.ACCEPTED_RISKS else "REFUSED "
    print(f"  {acc}  {key} r{n}  {e}  {text[:110]}")
print()
print(f"== C. bare-u_ Int records: {len(bare)} ==")
for b in bare:
    print(f"  {b}")
