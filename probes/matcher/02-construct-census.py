#!/usr/bin/env python3
"""probes/matcher/02-construct-census.py -- static construct census of the
Rubi 4 rule set against mma4max's matcher (handoffs/2026-09-11-matcher-
design.md, move 2 part A).

Run from the repo root (~1 min):
  python3 probes/matcher/02-construct-census.py > probes/matcher/02-construct-census.out

Question: is every construct the rules (and the utility functions they call)
use expressible with the mma4max matcher?  Three layers, reported
separately:
  (i)   the pattern language: every construct on every Int LHS, in context;
  (ii)  the matching semantics the LHSs rely on (Flat+Orderless, Optional
        defaults and where they sit, repeated names, pattern-variable heads);
  (iii) what rides next to the matcher: outer /; conditions, conditions
        inside RHS With/Module/Block (a rule withdrawn after it matched), and
        every pattern use inside conditions, RHSs and
        IntegrationUtilityFunctions.m (MatchQ, /., Cases, Switch, definition
        dispatch, ...), with its consumer.

Method.  02-mma-reader.py parses every rule of the 199 files Rubi.m loads
(count asserted against probes/probe-rubi-anatomy/01-inventory.py) into
FullForm; each Int LHS goes through the reader's EMULATED Mathematica
evaluation (Int is not held when rule files are read -- see the reader's
docstring), because the evaluated LHS is what Mathematica's matcher sees.
Construct labels are collected by a tree walk; each label carries a matcher
status assigned by hand below (STATUS), with its evidence:
  TESTED       exercised by a spike-01 case (case ids)
  CODE         a newmatch.lisp code path exists, not exercised (file:line)
  DIFFERS      the code path exists but its semantics differ from
               Mathematica's (evidence)
  UNSUPPORTED  no code path, or one that errors / is known wrong (evidence)
  n/a          not a matcher construct (reported for the design)
"""

import importlib.util
import sys
from collections import Counter, defaultdict, OrderedDict
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("mmareader", HERE / "02-mma-reader.py")
rd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rd)

PAT_OBJECTS = {"Blank", "BlankSequence", "BlankNullSequence", "Pattern", "Optional",
               "PatternTest", "Alternatives", "Except", "Repeated", "RepeatedNull",
               "HoldPattern", "Verbatim", "Longest", "Shortest", "PatternSequence",
               "OptionsPattern", "KeyValuePattern", "OrderlessPatternSequence"}
BLANKS = {"Blank", "BlankSequence", "BlankNullSequence"}
NL = "newmatch.lisp"

# ----------------------------------------------------------------------
# matcher status per construct label (label prefix match, longest first)

STATUS = OrderedDict([
    ("Blank named x_ (non-Flat parent)", ("TESTED", "every spike case (e.g. Log[..], PolyLog[k_, ..] G4-03)")),
    ("Blank named x_ directly under Plus", ("TESTED", "matchfol path, G1-G7; exponential search: SCALE series, 01-FINDINGS root cause 3")),
    ("Blank named x_ directly under Times", ("TESTED", "matchfol path, G1-G7; SCALE series; empty-remainder false match N-07/N-14/N-15 (mblank1, 01-FINDINGS root cause 1)")),
    ("Blank anonymous _", ("CODE", NL + ":1057-1063 mblank1 nameless branch")),
    ("Blank typed _Symbol", ("TESTED", "x_Symbol in every spike case (Int second argument)")),
    ("Blank typed", ("CODE", NL + ":1054 / :1317 head test (eq (Head e) h); eval.lisp:148 Head of integer/ratio/symbol")),
    ("BlankSequence", ("CODE", NL + ":1338 mblank2list (ordered); under Flat/Orderless " + NL + ":684-686 'probably wrong'; Fateman suite #149 fails")),
    ("BlankNullSequence", ("CODE", NL + ":1393 mblank3list (ordered); under Flat/Orderless " + NL + ":684-686 'probably wrong'")),
    ("Optional x_. under Plus", ("TESTED", "G1-04t G1-06 G3-02 (Default[Plus]=0, eval.lisp:728)")),
    ("Optional x_. under Times", ("TESTED", "G1-05 G1-09 G3-06 G7-01 (Default[Times]=1, eval.lisp:733)")),
    ("Optional x_. as Power exponent", ("TESTED", "G1-01 G3-01 (Default[Power]=1, eval.lisp:735)")),
    ("Optional x_. as Power base", ("DIFFERS", "remopts " + NL + ":583 uses Default[Power]=1 for any position; Mathematica defines Default[Power, 2] only")),
    ("Optional x_. under other head", ("DIFFERS", "remopts " + NL + ":583 falls back to Default[h]=(Sequence) (eval.lisp:983-984): the argument is dropped; Mathematica has no default for such a head")),
    ("Optional with explicit default x_:v", ("CODE", NL + ":583 (caddar rp)")),
    ("2+ Optionals directly under one head", ("UNSUPPORTED", "remopts rewrites only the first Optional of an argument list (" + NL + ":568-596, :2084-2091): spike control C-02 false negative")),
    ("named compound pattern x:pat", ("CODE", NL + ":865 mpattern")),
    ("PatternTest", ("CODE", NL + ":504 / :739 -- calls mma4max's evaluator (meval (test e))")),
    ("Condition inside a pattern", ("CODE", NL + ":471 / :703 -- calls mma4max's evaluator (meval cond)")),
    ("Alternatives", ("CODE", NL + ":477 / :710 / :1285")),
    ("Except", ("DIFFERS", NL + ":500 '(not (m1 ...)) not really right since bindings are lost'")),
    ("Repeated", ("UNSUPPORTED", NL + ":502-503 signals 'not installed'")),
    ("HoldPattern", ("UNSUPPORTED", "no handler in " + NL + " (would match as a literal head)")),
    ("Verbatim", ("UNSUPPORTED", "no handler in " + NL)),
    ("Longest", ("UNSUPPORTED", "no handler in " + NL)),
    ("Shortest", ("UNSUPPORTED", "no handler in " + NL)),
    ("PatternSequence", ("UNSUPPORTED", "no handler in " + NL)),
    ("OptionsPattern", ("UNSUPPORTED", "no handler in " + NL)),
    ("pattern-variable head F_[...]", ("CODE", NL + ":545-551 head matched recursively by m1; eval.lisp:997-1000 Attributes of a non-symbol head = (List)")),
    ("compound head h[..][..]", ("CODE", NL + ":545-551 same recursive head path")),
    ("pattern-variable Power base F_^(..)", ("TESTED", "G1-08 (2.1.m L8)")),
    ("Optional x_. at the top of a pattern", ("DIFFERS", "no governing head: remopts is only reached through an argument list (" + NL + ":2084-2091); Mathematica has no default either")),
    ("Complex[re, im] pattern", ("UNSUPPORTED", NL + ":424-437 extended-atom-match rebuilds the atom as (Complex re im) with an unescaped symbol (" + NL + ":436), not |Complex|; spike-01 SMOKE: Fateman suite #132 (Complex destructuring) fails; expression model: Maxima has no complex-number atom (2*%i is a product)")),
    ("Int second argument not x_Symbol", ("CODE", "an untyped named Blank (mblank1, " + NL + ":1041)")),
    ("literal E", ("CODE", NL + ":422 atom equality (target side: converter maps %e -> E, spike max2mm)")),
    ("literal Pi", ("CODE", NL + ":422 atom equality (converter maps %pi -> Pi)")),
    ("literal I", ("CODE", NL + ":422 atom equality; the converter has no %i mapping yet (spike max2mm)")),
    ("literal symbol", ("CODE", NL + ":422 atom equality")),
    ("literal integer", ("TESTED", "3.2.1.m L19 Power[.., -1] (G6), x_^2 (G1-09)")),
    ("literal rational", ("CODE", NL + ":422 atom equality of Lisp ratios; " + NL + ":424 Rational pattern vs ratio")),
    ("literal real", ("CODE", NL + ":422 atom equality (equal on floats)")),
    ("literal string", ("CODE", NL + ":422 atom equality")),
    ("repeated pattern name (not x)", ("TESTED", "N-06, C-01 (1.1.1.2.m L8 m_ twice)")),
    ("x_ repeated (integration variable)", ("TESTED", "every spike case")),
])


def status_of(label):
    best = None
    for k, v in STATUS.items():
        if label.startswith(k) and (best is None or len(k) > len(best[0])):
            best = (k, v)
    return best[1] if best else ("??", "no status assigned")


# ----------------------------------------------------------------------
# tree walks

def contains_pattern(e):
    if isinstance(e, tuple):
        h = e[0]
        if isinstance(h, str) and h in PAT_OBJECTS:
            return True
        return any(contains_pattern(a) for a in e)
    return False


def head_name(h):
    while isinstance(h, tuple):
        h = h[0]
    return h


def canon(e):
    """Sort Plus/Times arguments recursively (order-insensitive comparison)."""
    if not isinstance(e, tuple):
        return e
    parts = tuple(canon(a) for a in e)
    if parts[0] in ("Plus", "Times"):
        return (parts[0],) + tuple(sorted(parts[1:], key=rd.key))
    return parts


class Walk:
    """Collect construct labels over one pattern tree."""

    def __init__(self, xname="x"):
        self.labels = Counter()
        self.names = Counter()
        self.heads = Counter()
        self.max_flat = {"Plus": 0, "Times": 0}
        self.opt_under = []       # (head, number of Optionals, number of args)
        self.xname = xname

    def add(self, label):
        self.labels[label] += 1

    def walk(self, e, parent=None, pos=None, in_pattern_name=False):
        if not isinstance(e, tuple):
            self.atom(e, parent, pos)
            return
        h = e[0]
        args = e[1:]
        if isinstance(h, tuple):
            if isinstance(h[0], str) and h[0] == "Pattern":
                self.add("pattern-variable head F_[...]")
            else:
                self.add("compound head h[..][..]")
            self.walk(h, parent="<head>", pos=0)
        elif h in BLANKS:
            typ = " typed _%s" % args[0] if args else ""
            if h == "Blank":
                if in_pattern_name:
                    if typ:
                        self.add("Blank typed _%s" % args[0])
                    elif parent in ("Plus", "Times"):
                        self.add("Blank named x_ directly under %s" % parent)
                    else:
                        self.add("Blank named x_ (non-Flat parent)")
                else:
                    self.add("Blank anonymous _" + typ)
            else:
                self.add(h + (" (named)" if in_pattern_name else " (anonymous)") + typ +
                         (" under %s" % parent if parent in ("Plus", "Times") else ""))
            return
        elif h == "Pattern":
            self.names[args[0]] += 1
            if isinstance(args[1], tuple) and args[1][0] in BLANKS:
                self.walk(args[1], parent=parent, pos=pos, in_pattern_name=True)
            else:
                self.add("named compound pattern x:pat")
                self.walk(args[1], parent=parent, pos=pos)
            return
        elif h == "Optional":
            if len(args) == 2:
                self.add("Optional with explicit default x_:v")
            elif parent in ("Plus", "Times"):
                self.add("Optional x_. under %s" % parent)
            elif parent == "Power":
                self.add("Optional x_. as Power %s" % ("exponent" if pos == 2 else "base"))
            elif parent is None:
                self.add("Optional x_. at the top of a pattern")
            else:
                self.add("Optional x_. under other head (%s)" % parent)
            inner = args[0]
            if isinstance(inner, tuple) and inner[0] == "Pattern":
                self.names[inner[1]] += 1
                self.walk(inner[2], parent=parent, pos=pos, in_pattern_name=True)
            else:
                self.walk(inner, parent=parent, pos=pos)
            for a in args[1:]:
                self.walk(a, parent="Optional", pos=2)
            return
        elif h == "Condition":
            self.add("Condition inside a pattern")
            self.walk(args[0], parent=parent, pos=pos)
            return  # the condition body is code, not pattern
        elif h == "PatternTest":
            self.add("PatternTest")
            self.walk(args[0], parent=parent, pos=pos)
            return
        elif isinstance(h, str) and h in PAT_OBJECTS:
            self.add(h)
            if h in ("HoldPattern", "Verbatim"):
                return
            for i, a in enumerate(args, 1):
                self.walk(a, parent=parent, pos=pos)
            return
        else:
            self.heads[h] += 1
            if h == "Complex":
                self.add("Complex[re, im] pattern (matches complex-number atoms)")
            if h in ("Plus", "Times"):
                self.max_flat[h] = max(self.max_flat[h], len(args))
            if h == "Power" and len(args) == 2:
                b = args[0]
                if isinstance(b, tuple) and b[0] == "Pattern" and isinstance(args[1], tuple):
                    self.add("pattern-variable Power base F_^(..)")
        nopt = sum(1 for a in args if isinstance(a, tuple) and a[0] == "Optional")
        if nopt:
            self.opt_under.append((head_name(h), nopt, len(args)))
        if nopt >= 2:
            self.add("2+ Optionals directly under one head (%s)" % head_name(h))
        for i, a in enumerate(args, 1):
            self.walk(a, parent=head_name(h), pos=i)

    def atom(self, e, parent, pos):
        if isinstance(e, rd.Str):
            self.add("literal string")
        elif isinstance(e, bool):
            raise TypeError
        elif isinstance(e, int):
            self.add("literal integer (%s)" % _numctx(parent, pos))
        elif isinstance(e, Fraction):
            self.add("literal rational (%s)" % _numctx(parent, pos))
        elif isinstance(e, rd.Real):
            self.add("literal real")
        elif e in ("E", "Pi", "I"):
            self.add("literal %s" % e)
        else:
            self.add("literal symbol %s" % e)

    def finish(self):
        for n, c in self.names.items():
            if c > 1:
                self.add("x_ repeated (integration variable)" if n == self.xname
                         else "repeated pattern name (not x)")


def _numctx(parent, pos):
    if parent == "Power":
        return "Power exponent" if pos == 2 else "Power base"
    if parent in ("Plus", "Times"):
        return "under " + parent
    return "argument of %s" % parent


# argument positions that Mathematica reads as a pattern
PATTERN_ARGS = {"MatchQ": {2}, "Cases": {2}, "DeleteCases": {2}, "FreeQ": {2},
                "MemberQ": {2}, "Count": {2}, "Position": {2}, "StringMatchQ": {2}}
REPLACERS = {"ReplaceAll", "ReplaceRepeated", "Replace", "ReplaceList"}


def pattern_occurrences(e):
    """Yield (pattern subtree, consumer label, parent head) for every pattern
    use in code (conditions, RHSs, utility bodies).  A consumer position
    (MatchQ[_, P], Switch[_, P, v, ...], a replacement rule's LHS, ...)
    yields its whole argument; a pattern object found anywhere else is
    reported as unattributed, with its parent head."""
    if not isinstance(e, tuple):
        return
    h = head_name(e[0])
    if isinstance(e[0], tuple):
        yield from pattern_occurrences(e[0])
    for i, a in enumerate(e[1:], 1):
        if not contains_pattern(a):
            continue
        if h in REPLACERS and i == 2:
            items = a[1:] if isinstance(a, tuple) and a[0] == "List" else (a,)
            for rule in items:
                if isinstance(rule, tuple) and rule[0] in ("Rule", "RuleDelayed"):
                    if contains_pattern(rule[1]):
                        yield rule[1], "%s rule LHS" % h, None
                    yield from pattern_occurrences(rule[2])
                elif contains_pattern(rule):
                    yield rule, "%s rules argument (not a Rule)" % h, None
            continue
        if i in PATTERN_ARGS.get(h, ()):
            yield a, "%s[pattern]" % h, None
            continue
        if h == "Switch" and i >= 2 and i % 2 == 0:
            yield a, "Switch[pattern]", None
            continue
        if h in ("Rule", "RuleDelayed") and i == 1:
            yield a, "%s LHS outside a replacement" % h, None
            continue
        if h in ("SetDelayed", "Set") and i == 1:
            yield a, "definition LHS inside code", None
            continue
        if isinstance(a, tuple) and isinstance(a[0], str) and a[0] in PAT_OBJECTS:
            yield a, "unattributed pattern object under %s" % h, h
            continue
        yield from pattern_occurrences(a)


def inner_conditions(rhs, path=()):
    """Condition nodes in an RHS, with the head of the construct holding
    them (With/Module/Block body = withdraws the rule after it matched)."""
    out = []
    if not isinstance(rhs, tuple):
        return out
    h = head_name(rhs[0])
    if h == "Condition":
        holder = path[-1][0] if path else "<rhs top>"
        out.append(holder)
    if h in ("MatchQ", "Cases", "ReplaceAll", "FreeQ", "DeleteCases", "Switch"):
        return out  # a Condition inside a pattern argument is a pattern construct
    for i, a in enumerate(rhs[1:], 1):
        out.extend(inner_conditions(a, path + ((h, i),)))
    return out


# ----------------------------------------------------------------------

def table(title, rows, header):
    print()
    print("=== " + title)
    print("  " + " | ".join(header))
    for r in rows:
        print("  " + " | ".join(str(c) for c in r))


def ids_str(ids, limit=None):
    ids = list(ids)
    if limit is not None and len(ids) > limit:
        return ", ".join(ids[:limit]) + ", ... (+%d)" % (len(ids) - limit)
    return ", ".join(ids)


def main():
    print("=== probes/matcher/02-construct-census  run: %s" %
          datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    import subprocess
    pin = subprocess.run(["git", "-C", str(rd.rubi_root().parent), "rev-parse", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    print("reference/rubi HEAD: %s" % pin)
    print("python %s; no Maxima involved (static census)" % sys.version.split()[0])

    rules, counts = rd.load_rules()
    runs = [r for r in rules if r.source == "run"]
    wrapped = [r for r in rules if r.source == "showsteps-line"]
    print()
    print("=== completeness")
    print("files loaded by Rubi.m: %d" % len(counts))
    print("inventory rule runs: %d (01-inventory count_rules, asserted per file)" % len(runs))
    print("single-line If[TrueQ[$LoadShowSteps], .., ..] rules (outside the inventory convention): %d" % len(wrapped))
    for r in wrapped:
        print("  WRAPPED %s  %s" % (r.id, r.note or r.error))
    multi = [r for r in runs if r.note and r.note.startswith("multiline")]
    print("runs that are one branch of a multi-line If[TrueQ[$LoadShowSteps], .., ..]: %d -- %s" %
          (len(multi), ids_str(r.id for r in multi)))
    ext = [r for r in rules if r.note and r.note.startswith("run extended")]
    print("runs extended past a stripped comment line: %d -- %s" %
          (len(ext), ids_str("%s (%s)" % (r.id, r.note) for r in ext)))
    glued = [(r, e) for r in rules for e in r.extras]
    print("statements glued onto a run: %d" % len(glued))
    for r, e in glued:
        print("  GLUED %s: %s  %s" % (r.id, rd.classify_statement(e), rd.fullform(e)[:90]))
    errs = [r for r in rules if r.error]
    print("PARSE FAILURES: %d" % len(errs))
    for r in errs:
        print("  FAIL %s %s: %s" % (r.id, r.source, r.error))

    # whole-file statement parse cross-check
    stmt_classes = Counter()
    file_fail = []
    helper_defs = []
    for key_, rel, path in rd.loaded_rule_files():
        try:
            st = rd.file_statements(path)
        except rd.ParseError as ex:
            file_fail.append((rel, str(ex)))
            continue
        for line, e in st:
            c = rd.classify_statement(e)
            stmt_classes[c.split(":")[0] if c.startswith("definition") else c] += 1
            if c.startswith("definition"):
                helper_defs.append(("%s L%d" % (key_, line), c, e))
            if c == "showsteps-if":
                stmt_classes["showsteps-if branches"] += len(e) - 2
    print("whole-file parse (as Get reads the file): failures %d %s" % (len(file_fail), file_fail))
    print("  top-level statements by class: %s" % dict(stmt_classes))
    n_if_int = stmt_classes["showsteps-if branches"]
    print("  Int definitions at top level + inside ShowSteps If branches: %d + %d = %d"
          " (inventory runs %d + single-line wrapped %d x 2 branches = %d)" %
          (stmt_classes["int-rule"], n_if_int, stmt_classes["int-rule"] + n_if_int,
           len(runs), len(wrapped), len(runs) + 2 * len(wrapped)))
    print("  helper (non-Int) definitions in rule files: %d -- %s" %
          (len(helper_defs), ids_str("%s %s" % (i, c.split(':')[1]) for i, c, _e in helper_defs)))
    effective = len(runs) - len(multi) // 2 + len(wrapped)
    print("  Int DownValues Mathematica defines with $LoadShowSteps=True (one branch per If): %d" % effective)

    ok = [r for r in rules if not r.error]

    # ------------------------------------------------------------------
    # (i)+(ii) LHS census
    label_rules = defaultdict(list)
    label_files = defaultdict(set)
    label_count = Counter()
    heads_rules = defaultdict(set)
    effects_rules = defaultdict(list)
    flat_max = Counter()
    opt_hist = Counter()
    lhs_changed = []
    for r in ok:
        ev, eff = rd.evaluate_lhs(r.lhs)
        r.lhs_eval = ev
        for x in eff:
            effects_rules[x].append(r.id)
        if canon(ev) != canon(r.lhs):
            lhs_changed.append(r.id)
        second = ev[2] if len(ev) > 2 else None
        xname = second[1] if isinstance(second, tuple) and second[0] == "Pattern" else "x"
        w = Walk(xname)
        for i, a in enumerate(ev[1:], 1):
            w.walk(a, parent="Int", pos=i)
        w.finish()
        for lab, c in w.labels.items():
            label_rules[lab].append(r.id)
            label_files[lab].add(r.key)
            label_count[lab] += c
        for h in w.heads:
            heads_rules[h].add(r.id)
        m = max(w.max_flat.values())
        flat_max[m] += 1
        for hname, nopt, nargs in w.opt_under:
            opt_hist[(hname, nopt)] += 1
        if len(ev) != 3:
            label_rules["Int with %d arguments" % (len(ev) - 1)].append(r.id)
        if isinstance(second, tuple) and second != ("Pattern", xname, ("Blank", "Symbol")):
            label_rules["Int second argument not x_Symbol: %s" % rd.fullform(second)].append(r.id)

    rows = []
    for lab in sorted(label_rules, key=lambda l: (-len(label_rules[l]), l)):
        st, evid = status_of(lab)
        rows.append((lab, len(label_rules[lab]), len(label_files[lab]), label_count[lab], st, evid,
                     ids_str(label_rules[lab], 3)))
    table("(i) LHS pattern constructs (evaluated LHS; %d rules parsed)" % len(ok), rows,
          ["construct", "#rules", "#files", "#occurrences", "matcher status", "evidence", "example rules"])

    table("(ii) Optionals by parent head and count directly under that head (#heads-occurrences)",
          [(h, n, c) for (h, n), c in sorted(opt_hist.items(), key=lambda kv: (-kv[1], kv[0]))],
          ["parent head", "#Optionals among its arguments", "#occurrences"])

    # (ii-b) what sits directly under each Plus/Times pattern node -- sizes the
    # matcher's match-flat search (matcher substrate spec section 3.2)
    def flat_nodes(e):
        if isinstance(e, tuple):
            if e[0] in ("Plus", "Times"):
                yield e
            for a in e:
                yield from flat_nodes(a)

    node_hist = Counter()            # (head, #bare, #optional, #structured) -> #nodes
    two_bare = defaultdict(list)     # head -> rules with a node carrying >= 2 bare blanks
    max_struct = 0
    for r in ok:
        heads_two = set()
        for node in flat_nodes(r.lhs_eval[1]):
            bare = opt = struct = 0
            for a in node[1:]:
                if isinstance(a, tuple) and a[0] == "Optional":
                    opt += 1
                elif isinstance(a, tuple) and a[0] == "Pattern" and a[2] == ("Blank",):
                    bare += 1
                elif isinstance(a, tuple):
                    struct += 1
            node_hist[(node[0], bare, opt, struct)] += 1
            max_struct = max(max_struct, struct)
            if bare >= 2:
                heads_two.add(node[0])
        for h in heads_two:
            two_bare[h].append(r.id)
    table("(ii-b) Plus/Times pattern nodes by what sits directly under them",
          [(h, b, o, s, c) for (h, b, o, s), c in
           sorted(node_hist.items(), key=lambda kv: (kv[0][0], -kv[1]))],
          ["head", "#bare named blanks x_", "#Optionals x_.", "#structured children", "#nodes"])
    print("largest number of structured children directly under one Plus/Times node: %d" % max_struct)
    print("largest number of Optionals directly under one Plus/Times node: %d" %
          max((o for (_h, _b, o, _s) in node_hist), default=0))
    union_two = sorted({i for ids in two_bare.values() for i in ids})
    print("rules with a Plus/Times node carrying >= 2 bare named blanks: %d (%s) -- %s" % (
        len(union_two), ", ".join("%s %d" % (h, len(two_bare[h])) for h in sorted(two_bare)),
        ids_str(union_two, 5)))
    table("(ii) largest Plus/Times argument count in a rule's LHS pattern (#rules)",
          sorted(flat_max.items()), ["max args", "#rules"])
    table("heads appearing in LHS patterns (the converter's head table)",
          [(h if isinstance(h, str) else rd.fullform(h), len(s)) for h, s in
           sorted(heads_rules.items(), key=lambda kv: (-len(kv[1]), str(kv[0])))],
          ["head", "#rules"])
    table("LHS evaluation effects (emulated Mathematica evaluation; 'parse:' = notation "
          "normalisation, 'eval:' = structural rewrite, 'risk:' = not emulated)",
          [(x, len(v), ids_str(v, 8)) for x, v in sorted(effects_rules.items(), key=lambda kv: (kv[0].split(':')[0], -len(kv[1])))],
          ["effect", "#rules", "rules"])
    print("rules whose evaluated LHS differs from the parsed LHS (ignoring Plus/Times argument order): %d"
          % len(lhs_changed))

    gaps = [(lab, v) for lab, v in label_rules.items()
            if status_of(lab)[0] in ("UNSUPPORTED", "DIFFERS", "??")]
    print()
    print("=== NAMED GAPS in the LHS pattern language (status UNSUPPORTED / DIFFERS / unassigned): %d" % len(gaps))
    for lab, v in sorted(gaps, key=lambda kv: -len(kv[1])):
        st, evid = status_of(lab)
        print("GAP %s [%s] #rules=%d -- %s" % (lab, st, len(v), evid))
        print("    rules: %s" % ids_str(v))

    # ------------------------------------------------------------------
    # (iii) conditions and RHSs
    n_cond = sum(1 for r in ok if r.cond is not None)
    inner = defaultdict(list)
    occ_ctx = defaultdict(list)
    occ_labels = defaultdict(set)
    for r in ok:
        for holder in inner_conditions(r.rhs):
            inner[holder].append(r.id)
        for part, e in (("outer condition", r.cond), ("RHS", r.rhs)):
            if e is None:
                continue
            for sub, cons, parent in pattern_occurrences(e):
                occ_ctx[(part, cons)].append(r.id)
                w = Walk()
                w.walk(sub, parent=parent)
                w.finish()
                for lab in w.labels:
                    if not lab.startswith("literal"):
                        occ_labels[(part, lab)].add(r.id)
    print()
    print("=== (iii) conditions riding next to the matcher")
    print("rules with an outer /; condition: %d of %d" % (n_cond, len(ok)))
    print("rules with a Condition inside the RHS, by the construct holding it "
          "(With/Module/Block body: the rule is withdrawn after it matched):")
    inner_rules = set()
    for holder, v in sorted(inner.items(), key=lambda kv: -len(kv[1])):
        inner_rules.update(v)
        print("  %s: %d conditions in %d rules -- %s" % (holder, len(v), len(set(v)), ids_str(sorted(set(v)), 6)))
    print("  distinct rules with any inner Condition: %d" % len(inner_rules))
    table("(iii) pattern uses inside rule conditions and RHSs, by consumer",
          [(p, c, len(set(v)), ids_str(sorted(set(v)), 6)) for (p, c), v in
           sorted(occ_ctx.items(), key=lambda kv: -len(set(kv[1])))],
          ["where", "consumer", "#rules", "rules"])
    table("(iii) constructs in those pattern uses",
          [(p, lab, len(v), status_of(lab)[0], ids_str(sorted(v), 4)) for (p, lab), v in
           sorted(occ_labels.items(), key=lambda kv: -len(kv[1]))],
          ["where", "construct", "#rules", "matcher status", "rules"])

    # ------------------------------------------------------------------
    # utility functions (+ helper definitions found in rule files)
    util_path = rd.rubi_root() / "IntegrationUtilityFunctions.m"
    stripped = rd.INV.strip_comments(util_path.read_text())
    print()
    print("=== IntegrationUtilityFunctions.m")
    try:
        stmts = rd.parse_statements(stripped)
        util_fail = None
    except rd.ParseError as ex:
        stmts, util_fail = [], str(ex)
    print("whole-file parse: %s; top-level statements %d" % ("OK" if util_fail is None else "FAILED " + util_fail, len(stmts)))
    classes = Counter()
    defs = defaultdict(list)       # function -> [(line, expr)]
    usage = set()
    for off, e in stmts:
        line = stripped.count("\n", 0, off) + 1
        c = rd.classify_statement(e)
        classes[c.split(":")[0]] += 1
        if c.startswith("definition:"):
            name = c.split(":", 1)[1]
            lhs = e[1] if e[0] in ("Set", "SetDelayed") else e[1][1]
            if name == "MessageName" or (isinstance(lhs, tuple) and lhs[0] == "MessageName"):
                if lhs[2] == "usage":
                    usage.add(lhs[1])
                continue
            defs[name].append((line, e if e[0] != "CompoundExpression" else e[1]))
    print("statement classes: %s" % dict(classes))
    print("functions with ::usage: %d; functions defined: %d; definitions: %d" %
          (len(usage), len(defs), sum(len(v) for v in defs.values())))
    for i, c, e in helper_defs:
        defs[c.split(":", 1)[1]].append((i, e))

    def_labels = defaultdict(set)
    def_cond = set()
    multi_def = {f: len(v) for f, v in defs.items() if len(v) > 1}
    body_ctx = defaultdict(set)
    body_labels = defaultdict(set)
    for f, items in defs.items():
        for line, e in items:
            lhs, body = e[1], e[2]
            args = lhs[1:] if isinstance(lhs, tuple) else ()
            if isinstance(lhs, tuple) and isinstance(lhs[0], tuple):
                def_labels["compound definition head f[..][..]"].add(f)
            w = Walk(xname=None)
            for i, a in enumerate(args, 1):
                w.walk(a, parent=head_name(lhs[0]), pos=i)
            w.finish()
            for lab in w.labels:
                if not lab.startswith("literal"):
                    def_labels[lab].add(f)
            if isinstance(body, tuple) and body[0] == "Condition":
                def_cond.add(f)
            for sub, cons, parent in pattern_occurrences(body):
                body_ctx[cons].add(f)
                w = Walk(xname=None)
                w.walk(sub, parent=parent)
                w.finish()
                for lab in w.labels:
                    if not lab.startswith("literal"):
                        body_labels[lab].add(f)
    print("functions with more than one definition (pattern dispatch among definitions): %d" % len(multi_def))
    print("  %s" % ", ".join("%s x%d" % kv for kv in sorted(multi_def.items(), key=lambda kv: -kv[1])))
    print("functions with a /; condition on some definition: %d" % len(def_cond))
    table("utility definition LHS constructs (#functions)",
          [(lab, len(v), status_of(lab)[0], ids_str(sorted(v), 6)) for lab, v in
           sorted(def_labels.items(), key=lambda kv: -len(kv[1]))],
          ["construct", "#functions", "matcher status", "functions"])
    table("pattern uses inside utility function bodies, by consumer (#functions)",
          [(c, len(v), ids_str(sorted(v), 8)) for c, v in sorted(body_ctx.items(), key=lambda kv: -len(kv[1]))],
          ["consumer", "#functions", "functions"])
    table("constructs in utility body pattern uses (#functions)",
          [(lab, len(v), status_of(lab)[0], ids_str(sorted(v), 6)) for lab, v in
           sorted(body_labels.items(), key=lambda kv: -len(kv[1]))],
          ["construct", "#functions", "matcher status", "functions"])
    ugaps = sorted({lab for lab in list(def_labels) + list(body_labels)
                    if status_of(lab)[0] in ("UNSUPPORTED", "DIFFERS", "??")})
    print()
    print("=== NAMED GAPS in utility / condition pattern uses: %d" % len(ugaps))
    for lab in ugaps:
        st, evid = status_of(lab)
        print("UGAP %s [%s] defs=%s bodies=%s -- %s" % (lab, st, ids_str(sorted(def_labels.get(lab, ()))),
                                                      ids_str(sorted(body_labels.get(lab, ()))), evid))
    cgaps = sorted({lab for (_p, lab) in occ_labels if status_of(lab)[0] in ("UNSUPPORTED", "DIFFERS", "??")})
    for lab in cgaps:
        v = set()
        for (p, l2), s in occ_labels.items():
            if l2 == lab:
                v |= s
        print("CGAP %s [%s] rules=%s -- %s" % (lab, status_of(lab)[0], ids_str(sorted(v)), status_of(lab)[1]))


if __name__ == "__main__":
    main()
