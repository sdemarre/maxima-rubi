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
       - the With/Module local prefixing (ticket 08, the capture trap): a
         name declared in an expression-line block([...]) as
         _mr_<key>_r<n>_<name> is renamed back to <name> (the local Rubi
         calls D back to its old spelling diff), count pinned
       - the native inverse-hyperbolic heads (ticket 18, 2026-09-25): an
         atanh( / asinh( / acosh( call is undone to the %mr_ shim call the
         base emitted, count pinned
       - the two-argument Expand (ticket 19, 2026-09-25): a %mr_expand( call
         is undone to the expand( the base emitted, count pinned
       - the native polylogarithm (polylog-native-li issue 01, 2026-09-26):
         li[A](B) is undone to the polylog(A, B) the base emitted, count
         pinned
       - Rubi's real comparisons (matcher-translation-fixes issue 02,
         2026-09-25): %mr_gtQ/%mr_ltQ/%mr_leQ/%mr_geQ(A, B) undone to
         is(A op B), count pinned
       - the 29 manual 9.1 rules and the 52 rules that had a workaround
         emitter (no defmatch in the base) are exempt;
  4. the generator's reader self-test is green;
  5. every moved inner condition whose With/Module locals call a package
     entry (mr_int, rubi, ...) is listed and must be in RESOLVED;
  6. every %mr_defrule and %mr_matchQ pattern string prepares in MR-MATCH
     (plain SBCL, test/matcher/prepare_patterns.lisp) -- over EVERY class
     in the working tree, post-P0 classes included;
  7. every POST-P0 class (class 6 onward: ported after the P0 baseline, so
     it has no base text to diff against) carries exactly the rule total
     its generator configure() declares;
  8. the generated rewrite tables (rules/utils/inert_trig_rewrites.mac,
     inert-trig substrate design 3.2) are checked like a rule file: each
     mr_rw_<key> line present with the count the generator asserts (its
     REWRITE_FUNCTIONS), equal to mr_rw_count_<key> and to the number of
     %mr_defrewrite records; no defmatch; every bare-Blank catch-all at its
     table's end (a bare record mid-table would swallow the clauses after
     it); the file byte-identical to a fresh generation; and (check 6) every
     %mr_defrewrite pattern string prepares in MR-MATCH.

Scope note (2026-09-20). Checks 1-5 are a REGRESSION gate against P0 and
therefore run over the classes P0 had -- 1, 2 and 3 -- plus any class-1/2/3
file the working tree adds. They cannot run over a class ported after P0:
there is no base text, so "unchanged" and the pinned 3,513 total are not
meaningful. Before this split, rule_files() globbed rules/class*/*.mac and
the first post-P0 class turned the gate 14/0 -> 11/3 (measured with class 6:
counts-unchanged compared 13 files against an empty base, and the total
check saw 3,903 against its pinned 3,513). Check 7 is what covers those
classes instead; check 6 always covered them.

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
ENTRY_CALL = re.compile(r"\b(mr_int|mr_top|rubi|rubi_fallback)\(")
# Matcher translation fixes (docs/superpowers/specs/2026-09-14-matcher-
# translation-fixes-design.md 3.4): three generator fixes join the closed
# exception list, each checked as an exact text transformation -- undone on
# the new body (integer comparisons, notequal) or redone on the base body
# (juxtaposition) before the comparison. The counts are the sites in the
# compared (non-exempt) rules; probes/matcher/13-translation-shape-scan
# counts every emitted site.
INT_CMP_UNDO = {"%mr_iGtQ": ">", "%mr_iLtQ": "<", "%mr_iLeQ": "<=", "%mr_iGeQ": ">="}
INT_CMP_SITES = 1283
# Rubi's real comparisons (matcher-translation-fixes issue 02, user decision
# 2026-09-25): GtQ/LtQ/GeQ/LeQ emit the named two-valued entries %mr_gtQ ...
# where the base emitted is(A op B). Undone on the new body before the
# comparison, like the integer comparisons; the count is the sites in the
# compared rules.
REAL_CMP_UNDO = {"%mr_gtQ": ">", "%mr_ltQ": "<", "%mr_leQ": "<=", "%mr_geQ": ">="}
REAL_CMP_SITES = 1944
NOTEQUAL_SITES = 10
JUXTA_SITES = 1
# The With/Module local prefixing (.scratch/class-ports/issues/08): the
# generator names every With/Module local _mr_<key>_r<n>_<name>, since Maxima
# binds block locals dynamically and an unprefixed local captured the
# integrand's own symbol during a nested integration. Undone on the new body
# before the comparison; the count is the prefixed declarations in the
# compared rules. The unprefixed emission translated the local D to diff.
LOCAL_PREFIX_SITES = 1602
LOCAL_BASE_SPELLING = {"D": "diff"}
# The native inverse-hyperbolic heads (.scratch/class-ports/issues/18, option
# 1, user decision 2026-09-25): ArcTanh / ArcSinh / ArcCosh emit atanh /
# asinh / acosh in every class, where the base emitted the %mr_atanh /
# %mr_asinh / %mr_acosh log-form shims. Undone on the new body (native call
# -> shim call) before the comparison; the count is the sites in the
# compared rules (class 1's 51 and class 3's 2, all in repl lines).
NATIVE_HEADS = ("atanh", "asinh", "acosh")
NATIVE_HEAD_SITES = 53
# Two-argument Expand (.scratch/class-ports/issues/19, 2026-09-25): Rubi's
# Expand[u, x] emits %mr_expand(u, x) in every class, where the base emitted
# Maxima's expand(u, x) -- an expop error, so the rule always misfired.
# Undone on the new body before the comparison; class 2's 2_3 r58/r65.
EXPAND2_SITES = 2
# The native polylogarithm (.scratch/polylog-native-li/issues/01,
# 2026-09-26): PolyLog[s, z] emits Maxima's subscripted li[s](z) in every
# class, where the base emitted the unknown operator polylog(s, z). Undone on
# the new body before the comparison; class 3's sites.
POLYLOG_SITES = 37
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


# The classes the P0 baseline commit contains. A class ported later has no
# base text, so it belongs to check 7, not to the P0 diff (see the scope
# note in the module docstring).
BASE_CLASSES = ("class1", "class2", "class3")


def rule_files(base):
    """The P0-comparison set: the base commit's rule files, plus any file
    the working tree ADDS inside those same classes (so a newly added
    class-1 file is still caught). Post-P0 classes are deliberately not
    globbed in here -- see new_class_dirs()."""
    r = subprocess.run(["git", "ls-tree", "--name-only", base]
                       + ["rules/%s/" % c for c in BASE_CLASSES], cwd=ROOT,
                       capture_output=True, text=True, check=True)
    return sorted(set(r.stdout.split()) |
                  {p.relative_to(ROOT).as_posix()
                   for c in BASE_CLASSES
                   for p in ROOT.glob("rules/%s/*.mac" % c)})


def new_class_dirs():
    """The working tree's rule classes that the P0 baseline did not have,
    as {class_num: [paths]}, in class order."""
    out = {}
    for d in sorted(ROOT.glob("rules/class*")):
        if not d.is_dir() or d.name in BASE_CLASSES:
            continue
        m = re.fullmatch(r"class(\d+)", d.name)
        if m:
            out[int(m.group(1))] = sorted(d.glob("*.mac"))
    return out


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
    (likewise %mr_iLtQ <, %mr_iLeQ <=, %mr_iGeQ >=; and the real comparisons
    %mr_gtQ/%mr_ltQ/%mr_leQ/%mr_geQ the same way) and notequal(A, B) ->
    A != B; the generator emits both calls as NAME(A, B). Counts the sites."""
    names = list(INT_CMP_UNDO) + list(REAL_CMP_UNDO) + ["notequal"]
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
        elif m.group(1) in REAL_CMP_UNDO:
            rep, key = "is(%s %s %s)" % (a, REAL_CMP_UNDO[m.group(1)], b), "real_cmp"
        else:
            rep, key = "is(%s %s %s)" % (a, INT_CMP_UNDO[m.group(1)], b), "int_cmp"
        s = s[:m.start()] + rep + s[end:]
        stats[key] += 1


def undo_local_prefix(s, key, n, stats):
    """The new expression line with its With/Module locals unprefixed: each
    name a block([...]) list in the line declares as _mr_<key>_r<n>_<name>
    becomes <name> (LOCAL_BASE_SPELLING for D) wherever it occurs as a whole
    symbol. Only declared names are renamed, so a capture of the same shape
    is untouched and the comparison with the base stays exact. Counts the
    declarations."""
    pre = "_mr_%s_r%d_" % (key, n)
    names = set()
    for m in re.finditer(r"block\(\[([^\]]*)\]", s):
        names.update(nm for nm in (x.strip() for x in m.group(1).split(","))
                     if nm.startswith(pre))
    for nm in sorted(names, key=len, reverse=True):
        base = nm[len(pre):]
        s = re.sub(r"(?<![A-Za-z0-9_%])" + re.escape(nm) + r"(?![A-Za-z0-9_])",
                   LOCAL_BASE_SPELLING.get(base, base), s)
    stats["local_prefix"] += len(names)
    return s


def undo_native_heads(s, stats):
    """The new expression line with each native inverse-hyperbolic call
    atanh( / asinh( / acosh( back in its base shim spelling %mr_atanh( ...
    (ticket 18). A preceding identifier character or % excludes the shim
    itself and longer names. Counts the sites."""
    s, n = re.subn(r"(?<![A-Za-z0-9_%])(" + "|".join(NATIVE_HEADS) + r")\(", r"%mr_\1(", s)
    stats["native_heads"] += n
    return s


def undo_expand2(s, stats):
    """The new expression line with each %mr_expand( call back in the base
    spelling expand( (ticket 19; the generator emits %mr_expand only for a
    two-argument Expand). Counts the sites."""
    s, n = re.subn(r"%mr_expand\(", "expand(", s)
    stats["expand2"] += n
    return s


def _close(s, i, o, c):
    """The index just past the bracket that closes s[i] == o."""
    d = 0
    for j in range(i, len(s)):
        d += (s[j] == o) - (s[j] == c)
        if d == 0:
            return j + 1
    raise ValueError("unbalanced %s at %d" % (o, i))


def undo_polylog(s, stats):
    """The new expression line with each li[A](B) back in the base spelling
    polylog(A, B) (polylog-native-li issue 01). A preceding identifier
    character or % excludes longer names. Counts the sites."""
    out, k = [], 0
    for m in re.finditer(r"(?<![A-Za-z0-9_%])li\[", s):
        if m.start() < k:
            continue
        i = m.end() - 1
        j = _close(s, i, "[", "]")
        if j >= len(s) or s[j] != "(":
            raise ValueError("li[...] not called at %d" % m.start())
        e = _close(s, j, "(", ")")
        inner = undo_polylog(s[j + 1:e - 1], stats)
        out.append(s[k:m.start()] + "polylog(" + s[i + 1:j - 1] + ", " + inner + ")")
        stats["polylog"] += 1
        k = e
    out.append(s[k:])
    return "".join(out)


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


REWRITE_FILE = ROOT / "rules" / "utils" / "inert_trig_rewrites.mac"
BARE_PATTERN = re.compile(r"\(\w+( \(Pattern (\|[^|]*\||\w+) \(Blank\)\))+\)")


def check_rewrites(g):
    """Check 8: the generated rewrite tables (see the module docstring)."""
    sys.path.insert(0, str(ROOT / "generator"))
    import generate_rules as gen
    text = REWRITE_FILE.read_text() if REWRITE_FILE.exists() else ""
    records = {(k, int(n)): pat for k, n, pat in re.findall(
        r'^_mr_rw_\w+ : %mr_defrewrite\("([0-9a-z_]+)", (\d+), "([^"]*)"', text, re.M)}
    bad, bare_bad, want = [], [], []
    for key, fname, expected in gen.REWRITE_FUNCTIONS:
        want.append("%s %d" % (key, expected))
        lm = re.search(r"^mr_rw_%s : \[ (.*) \]\$$" % key, text, re.M)
        cm = re.search(r"^mr_rw_count_%s : (\d+)\$$" % key, text, re.M)
        names = lm.group(1).split(", ") if lm else []
        nrec = sum(1 for (k, _) in records if k == key)
        if not (lm and cm and int(cm.group(1)) == expected == len(names) == nrec
                and sorted(names) == sorted("_mr_rw_%s_r%d" % (key, n)
                                            for n in range(1, expected + 1))):
            bad.append("%s: list %s, count %s, records %d, expected %d" % (
                key, len(names) if lm else "missing", cm.group(1) if cm else "missing",
                nrec, expected))
            continue
        bare = [bool(BARE_PATTERN.fullmatch(records[(key, int(nm.rsplit("_r", 1)[1]))]))
                for nm in names]
        if True in bare and False in bare[bare.index(True):]:
            bare_bad.append("%s: %s" % (key, [nm for nm, b in zip(names, bare) if b]))
    if re.search(r"^(defmatch|matchdeclare)\(", text, re.M):
        bad.append("defmatch/matchdeclare present")
    g.check("rewrite tables: mr_rw_<key> lines and counts = mr_rw_count_<key> = records "
            "= generator (%s), no defmatch" % ", ".join(want), not bad, "; ".join(bad))
    g.check("rewrite tables: every bare-Blank catch-all at its table's end",
            bool(records) and not bare_bad, "; ".join(bare_bad) or "no records")
    try:
        fresh, _ = gen.emit_rewrites_file()
        same = fresh == text
        detail = "" if same else "the committed file differs from a fresh generation"
    except SystemExit as exc:
        same, detail = False, "generation failed (%s)" % exc
    g.check("rewrite tables: %s byte-identical to a fresh generation"
            % REWRITE_FILE.relative_to(ROOT), same, detail)


INT_BARE_U = re.compile(
    r"^\(Int \(Pattern (\|[^|]*\||\w+) \(Blank\)\) "
    r"\(Pattern x \(Blank Symbol\)\)\)$")
BODY_LIST_RE = re.compile(r"^mr_rules_(\w+) : \[ (.*) \]\$$", re.M)
TAIL_LIST_RE = re.compile(r"^mr_rules_(\w+)_tail : \[ (.*) \]\$$", re.M)

# The bare-u_ Int-record tail convention's closed exception list (inert-trig
# substrate design 3.3; generator/generate_rules.py carries the same list,
# under the same name -- a mismatch between the two would itself be a
# generator/gate disagreement the byte-identity check below would catch).
# Six legacy records sit in their class's body list, at source position;
# moving them changes accepted class-1/2/3 behaviour and needs a corpus A/B,
# out of this task's scope: .scratch/class-ports/issues/07-bare-u-records-
# mid-table.md.
BARE_U_BODY_EXCEPTIONS = {
    ("1_4_1", 7):  "mr_simplify_flag and SumQ[u] (issue 07)",
    ("1_4_1", 8):  "SumQ[u] (issue 07)",
    ("9_1", 8):    "FreeQ[a, x] (bare a_; issue 07)",
    ("9_1", 13):   "SumQ[u] (issue 07)",
    ("2_3", 96):   "FunctionOfExponentialQ[u, x] and not a MatchQ shape (issue 07)",
    ("3_5", 42):   "NonsumQ[u] and FunctionOfLog[Cancel[x u], x] not false (issue 07)",
}


def check_bare_u_tail(g):
    """Check 9: the bare-u_ Int-record tail convention (inert-trig
    substrate design 3.3; ledger R18), both directions, over every
    generated rule file (not just the P0 classes -- the convention applies
    to every class, present and future):

      - every record in a mr_rules_<key>_tail list has a bare-u_
        integrand -- strict, no exceptions;
      - no bare-u_ record sits in a mr_rules_<key> body list, except the
        closed, named BARE_U_BODY_EXCEPTIONS above -- a seventh such
        record anywhere fails this."""
    tail_wrong, body_wrong = [], []
    for p in sorted(ROOT.glob("rules/class*/*.mac")):
        text = p.read_text()
        patterns = {(k, int(n)): pat for k, n, pat in re.findall(
            r'^_mr_rule_\w+ : %mr_defrule\("([0-9a-z_]+)", (\d+), "([^"]*)"',
            text, re.M)}
        tail_names = set()
        for key, names_txt in TAIL_LIST_RE.findall(text):
            for nm in (n for n in names_txt.split(", ") if n):
                m = re.fullmatch(r"_mr_rule_%s_r(\d+)" % re.escape(key), nm)
                if not m:
                    tail_wrong.append("%s: malformed tail entry %r" % (p, nm))
                    continue
                n = int(m.group(1))
                tail_names.add((key, n))
                pat = patterns.get((key, n))
                if pat is None or not INT_BARE_U.fullmatch(pat):
                    tail_wrong.append(
                        "%s %s r%d: tail record is not a bare-u_ "
                        "integrand (%r)" % (p, key, n, pat))
        for key, names_txt in BODY_LIST_RE.findall(text):
            if key.endswith("_tail"):
                # the tail-list line itself also matches this regex
                # (mr_rules_<key>_tail : [ ... ]$ reads as a body list
                # whose "key" happens to end in _tail); skip it here, it
                # was already handled by TAIL_LIST_RE above.
                continue
            for nm in (n for n in names_txt.split(", ") if n):
                m = re.fullmatch(r"_mr_rule_%s_r(\d+)" % re.escape(key), nm)
                if not m:
                    continue
                n = int(m.group(1))
                if (key, n) in tail_names:
                    continue
                pat = patterns.get((key, n))
                if pat is not None and INT_BARE_U.fullmatch(pat) \
                        and (key, n) not in BARE_U_BODY_EXCEPTIONS:
                    body_wrong.append(
                        "%s %s r%d: bare-u_ record in a body list, not "
                        "in the closed exception list (%r)" % (p, key, n, pat))
    g.check("every mr_rules_<key>_tail record has a bare-u_ integrand",
            not tail_wrong, "\n    ".join(tail_wrong[:40]))
    g.check("no bare-u_ record sits in a body list except the closed "
            "exception list of %d (issue 07)" % len(BARE_U_BODY_EXCEPTIONS),
            not body_wrong, "\n    ".join(body_wrong[:40]))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=P0_BASE)
    a = ap.parse_args(argv)
    g = Gate()
    files = rule_files(a.base)
    counts_ok, lists_ok = [], []
    stats = dict(identical=0, guard=0, moved=0, matchq_old=0, workaround=0, nine=0,
                 no_defmatch=0, exempt_inner=0, exempt_matchq=0, int_cmp=0, real_cmp=0, notequal=0, juxta=0,
                 local_prefix=0, native_heads=0, expand2=0, polylog=0)
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
                         undo_polylog(undo_expand2(undo_native_heads(undo_fixes(
                             undo_local_prefix(parts[2][2], key, n, stats), stats), stats), stats), stats),
                         undo_polylog(undo_expand2(undo_native_heads(undo_fixes(
                             undo_local_prefix(parts[3][2], key, n, stats), stats), stats), stats), stats)]
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
    # Check 7: the post-P0 classes. They have no base text to diff, so the
    # standing claim is the one the generator itself declares -- each
    # class's committed rule total equals its configure() EXPECTED_TOTAL.
    # That is what catches a silently dropped or duplicated rule file in a
    # class the P0 checks above cannot see.
    for cls, paths in new_class_dirs().items():
        got = sum(int(m) for q in paths
                  for m in re.findall(r"^mr_rules_count_\w+ : (\d+)\$",
                                      q.read_text(), re.M))
        try:
            sys.path.insert(0, str(ROOT / "generator"))
            import generate_rules as _gen
            _gen.configure(cls)
            want = _gen.EXPECTED_TOTAL
        except (ImportError, KeyError) as exc:
            g.check("post-P0 class %d total readable from the generator" % cls,
                    False, "%s" % exc)
            continue
        g.check("post-P0 class %d: %d rules over %d files (generator "
                "EXPECTED_TOTAL %d)" % (cls, got, len(paths), want),
                got == want, "got %d, want %d" % (got, want))
    check_rewrites(g)
    check_bare_u_tail(g)
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
    g.check("real comparisons %%mr_gtQ/ltQ/geQ/leQ(A, B) undone to is(A op B): %d sites"
            % REAL_CMP_SITES,
            stats["real_cmp"] == REAL_CMP_SITES, str(stats["real_cmp"]))
    g.check("notequal(A, B) undone to A != B: %d sites" % NOTEQUAL_SITES,
            stats["notequal"] == NOTEQUAL_SITES, str(stats["notequal"]))
    g.check("juxtaposition ) ( redone to )*( in the base: %d sites" % JUXTA_SITES,
            stats["juxta"] == JUXTA_SITES, str(stats["juxta"]))
    g.check("With/Module locals _mr_<key>_r<n>_<name> undone to <name>: %d declarations"
            % LOCAL_PREFIX_SITES,
            stats["local_prefix"] == LOCAL_PREFIX_SITES, str(stats["local_prefix"]))
    g.check("native inverse-hyperbolic heads undone to the %%mr_ shims: %d sites"
            % NATIVE_HEAD_SITES,
            stats["native_heads"] == NATIVE_HEAD_SITES, str(stats["native_heads"]))
    g.check("two-argument %%mr_expand(u, x) undone to expand(u, x): %d sites" % EXPAND2_SITES,
            stats["expand2"] == EXPAND2_SITES, str(stats["expand2"]))
    g.check("native li[A](B) undone to polylog(A, B): %d sites" % POLYLOG_SITES,
            stats["polylog"] == POLYLOG_SITES, str(stats["polylog"]))
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
        for p in sorted(ROOT.glob("rules/class*/*.mac")) + sorted(ROOT.glob("rules/utils/*.mac")):
            text = p.read_text()
            for key, n, pat in re.findall(r'^_mr_rule_\w+ : %mr_defrule\("([0-9a-z_]+)", (\d+), "([^"]*)"',
                                          text, re.M):
                tsv.write("%s r%s\t%s\n" % (key, n, pat))
                n_pat += 1
            for key, n, pat in re.findall(r'^_mr_rw_\w+ : %mr_defrewrite\("([0-9a-z_]+)", (\d+), "([^"]*)"',
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
