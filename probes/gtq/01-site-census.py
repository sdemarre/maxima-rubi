#!/usr/bin/env python3
"""probes/gtq/01-site-census.py -- count the GtQ/LtQ/GeQ/LeQ sites.

(1) Rubi source (pinned clone reference/rubi, IntegrationRules/<class>/**.m):
    every GtQ[ / LtQ[ / GeQ[ / LeQ[ call, by class, head and arity, and how
    many sit directly under Not[...].
(2) The generated rule files (rules/class*/*.mac): every is(...) whose
    argument has a top-level real comparison (> < >= <=) -- the generator's
    CMP_OPS emission (generator/generate_rules.py) plus the raw-relation
    chains (_expand_chains) -- by class, operator, negation (the is() is the
    whole argument of not(...)), the definition kind it sits in
    (_mr_cond_ / _mr_repl_ / other), and the right-hand side shape (0, a
    literal number, other).  Also every is(...) WITHOUT a top-level
    comparison (not a GtQ-family site), for completeness.
Deterministic, no Maxima.  Usage: python3 probes/gtq/01-site-census.py
"""
import collections, glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEADS = ("GtQ", "LtQ", "GeQ", "LeQ")


def bracket_args(s, i):
    """s[i] == '['; return (list of top-level args, index after ']')."""
    depth, j, start, args = 0, i, i + 1, []
    while j < len(s):
        c = s[j]
        if c == '"':
            j = s.index('"', j + 1)
        elif c in "[({":
            depth += 1
        elif c in "])}":
            depth -= 1
            if depth == 0:
                args.append(s[start:j]); return args, j + 1
        elif c == "," and depth == 1:
            args.append(s[start:j]); start = j + 1
        j += 1
    return args, j


def rubi_census():
    tab = collections.Counter(); neg = collections.Counter(); ar3 = collections.Counter()
    base = os.path.join(ROOT, "reference", "rubi", "Rubi", "IntegrationRules")
    for path in glob.glob(os.path.join(base, "**", "*.m"), recursive=True):
        cls = os.path.relpath(path, base).split(" ")[0]
        s = open(path, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"(?<![A-Za-z0-9$])(GtQ|LtQ|GeQ|LeQ)\[", s):
            args, _ = bracket_args(s, m.end() - 1)
            tab[(cls, m.group(1))] += 1
            if len(args) == 3:
                ar3[(cls, m.group(1))] += 1
            if s[max(0, m.start() - 4):m.start()] == "Not[":
                neg[(cls, m.group(1))] += 1
    return tab, neg, ar3


def top_bool(s):
    """True when s has a top-level `and` / `or` (a boolean expression, not a
    single comparison: the raw-relation conds, e.g. 1_1_3_7 r40's
    is(%mr_neQ(..) and q - n >= 0 and ..) = true, a With-local condition)."""
    depth, i = 0, 0
    while i < len(s):
        c = s[i]
        if c == '"':
            i = s.index('"', i + 1)
        elif c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif depth == 0 and re.match(r"\s(and|or)\s", s[i:i + 5]):
            return True
        i += 1
    return False


def top_cmp(s):
    if top_bool(s):
        return None
    depth, i = 0, 0
    while i < len(s):
        c = s[i]
        if c == '"':
            i = s.index('"', i + 1)
        elif c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif depth == 0 and c in "<>":
            return s[i:i + 2] if s[i + 1:i + 2] == "=" else c
        i += 1
    return None


def generated_census():
    sites = collections.Counter(); other = collections.Counter(); rhs = collections.Counter()
    rawrel = collections.Counter()
    files = collections.Counter()
    for path in sorted(glob.glob(os.path.join(ROOT, "rules", "class*", "*.mac"))):
        cls = os.path.basename(os.path.dirname(path))[5:]
        text = open(path).read()
        kinds = [(m.start(), m.group(1)) for m in
                 re.finditer(r"^(_mr_cond_|_mr_repl_|_mr_\w+|\S+)", text, re.M)]
        for m in re.finditer(r"(?<![A-Za-z0-9_%])is\(", text):
            j, depth = m.end(), 1
            while depth:
                if text[j] == "(": depth += 1
                elif text[j] == ")": depth -= 1
                j += 1
            inner = text[m.end():j - 1]
            op = top_cmp(inner)
            if op is None:
                if top_bool(inner) and re.search(r"[<>]", inner):
                    rawrel[cls] += 1
                else:
                    other[cls] += 1
                continue
            kind = "other"
            for pos, k in kinds:
                if pos > m.start(): break
                kind = k if k in ("_mr_cond_", "_mr_repl_") else "other"
            negd = text[max(0, m.start() - 4):m.start()] == "not(" and text[j:j + 1] == ")"
            r = inner.split(op, 1)[1].strip() if op else ""
            rs = "0" if r == "0" else ("number" if re.fullmatch(r"-?[0-9/.]+|\(-?[0-9/]+\)", r) else "expr")
            sites[(cls, op, negd, kind)] += 1; rhs[(cls, rs)] += 1
            files[(cls, os.path.basename(path)[:-4])] += 1
    return sites, other, rhs, files, rawrel


def main():
    tab, neg, ar3 = rubi_census()
    classes = sorted({c for c, _ in tab})
    print("== Rubi source (IntegrationRules), calls by class and head; (neg = directly under Not[), 3-arg")
    print(f"{'class':>5} " + " ".join(f"{h:>14}" for h in HEADS) + f" {'total':>6} {'neg':>5} {'3arg':>5}")
    T = collections.Counter()
    for c in classes:
        row = [tab[(c, h)] for h in HEADS]
        n = sum(neg[(c, h)] for h in HEADS); a = sum(ar3[(c, h)] for h in HEADS)
        for h in HEADS: T[h] += tab[(c, h)]
        T["neg"] += n; T["3"] += a
        print(f"{c:>5} " + " ".join(f"{v:>14}" for v in row) + f" {sum(row):>6} {n:>5} {a:>5}")
    print(f"{'all':>5} " + " ".join(f"{T[h]:>14}" for h in HEADS) + f" {sum(T[h] for h in HEADS):>6} {T['neg']:>5} {T['3']:>5}")

    sites, other, rhs, files, rawrel = generated_census()
    print("\n== generated rules/class*/*.mac: is(A op B) sites by class and op")
    ops = [">", "<", ">=", "<="]
    print(f"{'class':>5} " + " ".join(f"{o:>6}" for o in ops) + f" {'total':>6} {'not()':>6} {'cond':>6} {'repl':>6} {'other':>6} {'rhs=0':>6} {'rhs#':>6} {'rhsX':>6} {'non-cmp is()':>12}")
    G = collections.Counter()
    for c in sorted({k[0] for k in sites} | set(other)):
        byop = [sum(v for k, v in sites.items() if k[0] == c and k[1] == o) for o in ops]
        ng = sum(v for k, v in sites.items() if k[0] == c and k[2])
        kc = [sum(v for k, v in sites.items() if k[0] == c and k[3] == kk) for kk in ("_mr_cond_", "_mr_repl_", "other")]
        rr = [rhs[(c, x)] for x in ("0", "number", "expr")]
        vals = byop + [sum(byop), ng] + kc + rr + [other[c]]
        for i, v in enumerate(vals): G[i] += v
        print(f"{c:>5} " + " ".join(f"{v:>6}" for v in vals[:4]) + " " + " ".join(f"{v:>6}" for v in vals[4:-1]) + f" {vals[-1]:>12}")
    vals = [G[i] for i in range(len(G))]
    print(f"{'all':>5} " + " ".join(f"{v:>6}" for v in vals[:4]) + " " + " ".join(f"{v:>6}" for v in vals[4:-1]) + f" {vals[-1]:>12}")
    print("\n== boolean is(...) holding a RAW relation (Rubi's raw `q-n>=0` inside a With/Module\n"
          "   condition; not a GtQ-family call, already read `= true`), by class:",
          dict(sorted(rawrel.items())), "total", sum(rawrel.values()))
    print("\n== top 40 rule files by generated site count")
    for (c, f), v in files.most_common(40):
        print(f"{v:5d}  class {c}  {f}")


if __name__ == "__main__":
    main()
