#!/usr/bin/env python3
"""test/check_generated_rules.py -- the P3 static gate of the matcher
substrate migration (spec docs/superpowers/specs/2026-09-12-matcher-
substrate-design.md section 4, P3; section 3.4 closed exception list).

Compares the generated rule files of the working tree with those of a base
commit (default: the P0 baseline commit 0a6664c) without running Maxima:

  1. rule counts per file unchanged (9_1: 29 -> 28, the pinned source's
     commented-out L4 rule), every mr_rules_<key> list line unchanged
     (9_1 excepted);
  2. no defmatch / matchdeclare left in any rule file; one %mr_defrule per
     rule;
  3. every cond and repl body byte-identical to the base, except the closed
     exception list, each exception verified as the exact text
     transformation it claims to be:
       - removed nonzero guards: old cond == "(" + new + ")  and  " + guards
       - moved inner conditions: the repl loses its
         "(if is(C) = true then X else false)" guard and the cond gains
         "  and  block([L], A, is(C) = true)"
       - MatchQ sites: each %mr_matchQ(...) call is compared masked
       - the matcher translation fixes (design 2026-09-14 section 3.4):
         %mr_iGtQ/%mr_iLtQ/%mr_iLeQ/%mr_iGeQ(A, B) undone to is(A op B),
         notequal(A, B) undone to A != B, a base `) (` redone to `)*(`,
         each count pinned
       - the 29 manual 9.1 rules and the 52 rules that had a workaround
         emitter (no defmatch in the base) are exempt;
  4. the generator's reader self-test is green;
  5. every moved inner condition whose With/Module locals call a package
     entry (mr_int, rubi, ...) is listed and must be in RESOLVED;
  6. every %mr_defrule and %mr_matchQ pattern string prepares in MR-MATCH
     (plain SBCL, test/matcher/prepare_patterns.lisp).

Usage:  python3 test/check_generated_rules.py [--base <commit>]
Ends with "Results: <n> passed, <m> failed".
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P0_BASE = "0a6664c"
WORKAROUND_RULES = 52
MOVED_INNER = 227
MATCHQ_SITES = 23
ENTRY_CALL = re.compile(r"\b(mr_int|mr_int_exact|mr_top|rubi|rubi_fallback)\(")
# Matcher translation fixes (docs/superpowers/specs/2026-09-14-matcher-
# translation-fixes-design.md 3.4): three generator fixes join the closed
# exception list, each checked as an exact text transformation -- undone on
# the new body (integer comparisons, notequal) or redone on the base body
# (juxtaposition) before the comparison. The counts are the sites in the
# compared (non-exempt) rules; probes/matcher/13-translation-shape-scan
# counts every emitted site.
INT_CMP_UNDO = {"%mr_iGtQ": ">", "%mr_iLtQ": "<", "%mr_iLeQ": "<=", "%mr_iGeQ": ">="}
INT_CMP_SITES = 1283
NOTEQUAL_SITES = 10
JUXTA_SITES = 1
# user decision 2026-09-12 (Plan 2 writing session): move all 227 inner
# conditions, including those whose locals integrate (IntHide -> mr_int);
# their extra cost is watched by the P5 median-wall gate.
RESOLVED_ENTRY_LOCALS = {
    "3_1_3 r18", "3_1_4 r23", "3_1_5 r21", "3_3 r26", "3_5 r37", "3_5 r38", "3_5 r40",
}
FUN = re.compile(r"^_mr_(cond|repl)_([0-9a-z_]+?)_r(\d+)\(mm, x\) := (.*?)\)\$\n", re.M | re.S)
GUARDS = re.compile(r"%mr_neQ\(_mr_[0-9A-Za-z_]+, 0\)(  and  %mr_neQ\(_mr_[0-9A-Za-z_]+, 0\))*")


class Gate:
    def __init__(self):
        self.passed = self.failed = 0

    def check(self, name, ok, detail=""):
        if ok:
            self.passed += 1
            print("PASS: %s" % name)
        else:
            self.failed += 1
            print("FAIL: %s%s" % (name, ("\n    " + detail) if detail else ""))


def git_show(base, rel):
    r = subprocess.run(["git", "show", "%s:%s" % (base, rel)], cwd=ROOT,
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def rule_files(base):
    r = subprocess.run(["git", "ls-tree", "--name-only", base, "rules/class1/",
                        "rules/class2/", "rules/class3/"], cwd=ROOT,
                       capture_output=True, text=True, check=True)
    return sorted(set(r.stdout.split()) |
                  {p.relative_to(ROOT).as_posix() for p in ROOT.glob("rules/class*/*.mac")})


def bodies(text):
    return {(k, int(n), kind): body for kind, k, n, body in FUN.findall(text or "")}


def mask_matchq(s):
    """Replace every balanced %mr_matchQ(...) call by a marker; -> (text, count)."""
    out, i, count = [], 0, 0
    while True:
        j = s.find("%mr_matchQ(", i)
        if j < 0:
            out.append(s[i:])
            return "".join(out), count
        depth, k = 0, j + len("%mr_matchQ")
        in_str = False
        while k < len(s):
            ch = s[k]
            if ch == '"':
                in_str = not in_str
            elif not in_str:
                depth += ch == "("
                depth -= ch == ")"
                if depth == 0:
                    break
            k += 1
        out.append(s[i:j] + "%mr_matchQ(...)")
        count += 1
        i = k + 1


def unsnap(s):
    return re.sub(r"(_mr_[0-9A-Za-z_]+?)__s\b", r"\1", s)


def call_args(s, open_idx):
    """(index after the matching ')', [argument texts]) of the call whose '('
    is at open_idx; commas split at depth 1 only."""
    depth, start, args, in_str = 0, open_idx + 1, [], False
    for k in range(open_idx, len(s)):
        ch = s[k]
        if ch == '"':
            in_str = not in_str
        elif not in_str:
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
                if depth == 0:
                    args.append(s[start:k])
                    return k + 1, args
            elif ch == "," and depth == 1:
                args.append(s[start:k])
                start = k + 1
    raise ValueError("unbalanced call at %d" % open_idx)


def undo_fixes(s, stats):
    """The new body line in its base spelling: %mr_iGtQ(A, B) -> is(A > B)
    (likewise %mr_iLtQ <, %mr_iLeQ <=, %mr_iGeQ >=) and notequal(A, B) ->
    A != B; the generator emits both calls as NAME(A, B). Counts the sites."""
    names = list(INT_CMP_UNDO) + ["notequal"]
    pat = re.compile(r"(?<![A-Za-z0-9_%])(" + "|".join(re.escape(n) for n in names) + r")\(")
    while True:
        m = pat.search(s)
        if not m:
            return s
        end, args = call_args(s, m.end() - 1)
        if len(args) != 2 or not args[1].startswith(" "):
            raise ValueError("%s with %d arguments" % (m.group(1), len(args)))
        a, b = args[0], args[1][1:]
        if m.group(1) == "notequal":
            rep, key = "%s != %s" % (a, b), "notequal"
        else:
            rep, key = "is(%s %s %s)" % (a, INT_CMP_UNDO[m.group(1)], b), "int_cmp"
        s = s[:m.start()] + rep + s[end:]
        stats[key] += 1


def redo_juxtaposition(s, stats):
    """The base body line with the generator's juxtaposition fix applied: a
    `)`/`]` followed by a spaced `(` becomes `)*(`. Counts the sites."""
    s, n = re.subn(r"([)\]]) \(", r"\1*(", s)
    stats["juxta"] += n
    return s


def moved_inner(old_repl, new_repl, old_cond_base, new_cond):
    """None if (old, new) is not a moved inner condition; else the inner
    block text (for the entry-call listing) when the transformation is exact,
    or False when the shapes look moved but do not match exactly."""
    x = new_repl[:-1] if new_repl.endswith(")") else None
    if x is None:
        return None
    for k in [m.start() for m in re.finditer(r"\(if is\(", old_repl)]:
        pre = old_repl[:k]
        if not new_repl.startswith(pre):
            continue
        inner = new_repl[len(pre):-1]
        tail = ") = true then " + inner + " else false))"
        if not old_repl.endswith(tail) or len(old_repl) - len(tail) < k + 7:
            continue
        c = old_repl[k + 7:len(old_repl) - len(tail)]
        scope = pre[pre.rindex("block(["):]
        want = "(%s)  and  %sis(%s) = true)" % (old_cond_base, unsnap(scope), unsnap(c))
        return want if new_cond == want else False
    return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=P0_BASE)
    a = ap.parse_args(argv)
    g = Gate()
    files = rule_files(a.base)
    counts_ok, lists_ok = [], []
    stats = dict(identical=0, guard=0, moved=0, matchq_old=0, workaround=0, nine=0,
                 no_defmatch=0, exempt_inner=0, exempt_matchq=0, int_cmp=0, notequal=0, juxta=0)
    unexplained, entry_locals, bad_moves = [], [], []
    for rel in files:
        old = git_show(a.base, rel)
        new = (ROOT / rel).read_text() if (ROOT / rel).exists() else None
        key = Path(rel).stem
        oc = re.search(r"^mr_rules_count_\w+ : (\d+)\$", old or "", re.M)
        nc = re.search(r"^mr_rules_count_\w+ : (\d+)\$", new or "", re.M)
        want = (29, 28) if key == "9_1" else (oc and int(oc.group(1)), oc and int(oc.group(1)))
        counts_ok.append((rel, bool(oc and nc) and (int(oc.group(1)), int(nc.group(1))) == want))
        if key != "9_1":
            ol = re.search(r"^mr_rules_\w+ : \[.*\]\$$", old or "", re.M)
            nl = re.search(r"^mr_rules_\w+ : \[.*\]\$$", new or "", re.M)
            lists_ok.append((rel, bool(ol and nl) and ol.group(0) == nl.group(0)))
        if new is not None:
            if re.search(r"^(defmatch|matchdeclare)\(", new, re.M):
                unexplained.append("%s: defmatch/matchdeclare present" % rel)
            ndef = len(re.findall(r"^_mr_rule_\w+ : %mr_defrule\(", new, re.M))
            if nc and ndef != int(nc.group(1)):
                unexplained.append("%s: %d %%mr_defrule for %s rules" % (rel, ndef, nc.group(1)))
        ob, nb = bodies(old), bodies(new)
        n_rules = int(oc.group(1)) if oc else 0
        for n in range(1, n_rules + 1):
            rid = "%s r%d" % (key, n)
            has_defmatch = re.search(r"^defmatch\(_mr_pat_%s_r%d," % (re.escape(key), n), old, re.M)
            if key == "9_1" or not has_defmatch:
                # exempt; counted so the totals reconcile with the spec's
                # closed list (227 inner conditions, 52 workaround rules,
                # 23 MatchQ sites are counted over all 3,514 rules)
                stats["nine" if key == "9_1" else "workaround"] += 1
                stats["no_defmatch"] += not has_defmatch
                orep = ob.get((key, n, "repl")) or ""
                stats["exempt_inner"] += bool(re.search(r"\(if is\(.*= true then", orep, re.S))
                rfun = re.search(r"^_mr_rule_%s_r%d\(f, x\) := (.*?)\)\$\n" % (re.escape(key), n),
                                 old, re.M | re.S)
                stats["exempt_matchq"] += (mask_matchq(ob.get((key, n, "cond")) or "")[1]
                                           + mask_matchq(orep)[1]
                                           + (mask_matchq(rfun.group(1))[1] if rfun else 0))
                continue
            oc_, or_ = ob.get((key, n, "cond")), ob.get((key, n, "repl"))
            nc_, nr_ = nb.get((key, n, "cond")), nb.get((key, n, "repl"))
            if None in (oc_, or_, nc_, nr_):
                unexplained.append("%s: cond/repl missing" % rid)
                continue
            # a body is "block([<locals>],\n  <binds>,\n  <expression>": the
            # locals and binds lines must match; the exceptions live in the
            # expression line
            parts = [b.split("\n  ", 2) for b in (oc_, or_, nc_, nr_)]
            if any(len(p) != 3 for p in parts) or parts[0][:2] != parts[2][:2] \
                    or parts[1][:2] != parts[3][:2]:
                unexplained.append("%s: locals/binds lines differ" % rid)
                continue
            try:
                lines = [redo_juxtaposition(parts[0][2], stats), redo_juxtaposition(parts[1][2], stats),
                         undo_fixes(parts[2][2], stats), undo_fixes(parts[3][2], stats)]
            except ValueError as e:
                unexplained.append("%s: translation-fix undo: %s" % (rid, e))
                continue
            oc_m, qo1 = mask_matchq(lines[0])
            or_m, qo2 = mask_matchq(lines[1])
            nc_m, _ = mask_matchq(lines[2])
            nr_m, _ = mask_matchq(lines[3])
            stats["matchq_old"] += qo1 + qo2
            base = oc_m
            if oc_m.startswith("("):
                for m in re.finditer(r"\)  and  ", oc_m):
                    if GUARDS.fullmatch(oc_m[m.end():]):
                        base = oc_m[1:m.start()]
                        stats["guard"] += 1
                        break
            if nr_m == or_m and nc_m == base:
                stats["identical"] += 1
                continue
            mv = moved_inner(or_m, nr_m, base, nc_m)
            if mv:
                stats["moved"] += 1
                if ENTRY_CALL.search(mv[mv.index("  and  "):]):
                    entry_locals.append(rid)
                continue
            (bad_moves if mv is False else unexplained).append(
                "%s: cond %s, repl %s" % (rid, "same" if nc_m == base else "DIFF",
                                          "same" if nr_m == or_m else "DIFF"))
    bad_counts = [r for r, ok in counts_ok if not ok]
    g.check("rule counts per file unchanged (9_1: 29 -> 28), %d files" % len(counts_ok),
            not bad_counts, "differ: %s" % bad_counts)
    bad_lists = [r for r, ok in lists_ok if not ok]
    g.check("mr_rules_<key> list lines unchanged (9_1 excepted)", not bad_lists, "differ: %s" % bad_lists)
    total = sum(int(m) for rel in files if (ROOT / rel).exists()
                for m in re.findall(r"^mr_rules_count_\w+ : (\d+)\$", (ROOT / rel).read_text(), re.M))
    g.check("total rules 3,513 (3,514 - the dead 9.1 L4 rule)", total == 3513, "total %d" % total)
    g.check("no defmatch/matchdeclare; one %mr_defrule per rule; every cond/repl explained",
            not unexplained, "\n    ".join(unexplained[:40]))
    g.check("moved inner conditions are exact transformations", not bad_moves, "\n    ".join(bad_moves[:40]))
    print("INFO: bodies identical %(identical)d, nonzero guards removed %(guard)d, inner conditions "
          "moved %(moved)d (+%(exempt_inner)d in exempt rules), MatchQ sites compared %(matchq_old)d "
          "(+%(exempt_matchq)d in exempt rules), rules without defmatch %(no_defmatch)d "
          "(workaround emitters %(workaround)d of them outside 9.1), manual 9.1 rules %(nine)d" % stats)
    g.check("inner conditions: moved + in exempt rules = %d" % MOVED_INNER,
            stats["moved"] + stats["exempt_inner"] == MOVED_INNER,
            "%d + %d" % (stats["moved"], stats["exempt_inner"]))
    g.check("rules without defmatch in the base = %d" % WORKAROUND_RULES,
            stats["no_defmatch"] == WORKAROUND_RULES, str(stats["no_defmatch"]))
    g.check("MatchQ sites: compared + in exempt rules = %d" % MATCHQ_SITES,
            stats["matchq_old"] + stats["exempt_matchq"] == MATCHQ_SITES,
            "%d + %d" % (stats["matchq_old"], stats["exempt_matchq"]))
    g.check("integer comparisons %%mr_i*Q(A, B) undone to is(A op B): %d sites" % INT_CMP_SITES,
            stats["int_cmp"] == INT_CMP_SITES, str(stats["int_cmp"]))
    g.check("notequal(A, B) undone to A != B: %d sites" % NOTEQUAL_SITES,
            stats["notequal"] == NOTEQUAL_SITES, str(stats["notequal"]))
    g.check("juxtaposition ) ( redone to )*( in the base: %d sites" % JUXTA_SITES,
            stats["juxta"] == JUXTA_SITES, str(stats["juxta"]))
    for rid in entry_locals:
        print("INFO: moved inner condition with a package entry in its locals: %s%s" % (
            rid, " (resolved)" if rid in RESOLVED_ENTRY_LOCALS else " (UNRESOLVED)"))
    g.check("every moved inner condition calling a package entry is resolved (%d)" % len(entry_locals),
            set(entry_locals) <= RESOLVED_ENTRY_LOCALS and entry_locals,
            "unresolved: %s" % sorted(set(entry_locals) - RESOLVED_ENTRY_LOCALS))
    r = subprocess.run([sys.executable, str(ROOT / "generator" / "mma_reader.py")],
                       capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    g.check("reader self-test green (%s)" % last, re.fullmatch(r"Results: \d+ passed, 0 failed", last) is not None)
    with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False) as tsv:
        n_pat = 0
        for p in sorted(ROOT.glob("rules/class*/*.mac")):
            text = p.read_text()
            for key, n, pat in re.findall(r'^_mr_rule_\w+ : %mr_defrule\("([0-9a-z_]+)", (\d+), "([^"]*)"',
                                          text, re.M):
                tsv.write("%s r%s\t%s\n" % (key, n, pat))
                n_pat += 1
            for pat in re.findall(r'%mr_matchQ\([^"]*?, "([^"]*)"', text):
                tsv.write("%s matchq\t%s\n" % (p.stem, pat))
                n_pat += 1
    r = subprocess.run(["sbcl", "--script", str(ROOT / "test" / "matcher" / "prepare_patterns.lisp"),
                        str(ROOT / "maxima_rubi_match.lisp"), tsv.name], capture_output=True, text=True)
    out = r.stdout.strip().splitlines()
    last = out[-1] if out else r.stderr[-300:]
    g.check("every pattern string prepares in MR-MATCH (%d strings; %s)" % (n_pat, last),
            last == "Results: %d passed, 0 failed" % n_pat, "\n    ".join(out[-10:]))
    print("Results: %d passed, %d failed" % (g.passed, g.failed))
    return 1 if g.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
