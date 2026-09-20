#!/usr/bin/env python3
"""probes/matcher/16-seen-guard-trace.py -- the EQ-REWRITE question of the
P5b attribution (matcher translation fixes, Task 7; the mechanism file
probes/matcher/10-p5b-attribution.mechanisms-class2-3.md): does mr_int's
ratsimp seen comparison (%mr_seenp) read a non-9.1 rule's equal-form rewrite
as a loop and send the nested call to the integrate fall-through?

Each entry runs through the corpus driver's EXACT per-entry text
(test/corpus_driver.py build_text, switch defaults) with `rubi_verbose : true$`
prepended (probe 15's method), plus a probe-local instrumentation that is
DERIVED FROM THE SOURCE of the core's own tree, not hand-copied:

- the dispatch entry (%mr_top_body at HEAD; mr_top and %mr_hybrid_body at
  P0 0a6664c) is extracted from maxima_rubi_utils.mac and patched at
  anchors, each asserted to occur exactly once, with trace calls only;
- %mr_seenp is replaced by %mr16_seenp, whose seen semantics are checked
  against the source text of both trees (normalized) before any run.

The trace records, per dispatch-entry call: id, nesting depth (a dynamically
bound path, which errcatch unwinds), depth_level, length(%mr_seen), the seen
hit (exact member or ratsimp, the matched %mr_seen element and whether that
element's call is still live), the outcome (the rule that fired, or the
fall-through branch) and the owner (the next rule-outcome line of the parent,
i.e. the rule attempt whose cond or repl made the call). P0 calls also record
which pass (1 %mr_dispatch, 2 %mr_dispatch_rev, 3 %mr_dispatch_i1) answered.

Arms:
  trace      fixed core (the tree's test/mr_rules.core), seen test as HEAD.
  exact-only fixed core, DIAGNOSTIC ARM, NOT A PROPOSED FIX: %mr_seenp is
             exact member only (mr_int_exact semantics on every call).
  p0         P0 core (MR16_P0_CORE, default ${TMPDIR:-/tmp}/mr-p0-tree/
             test/mr_rules.core), seen test as P0, class 2 g1 and class 3 g21.

Per-entry cap 30 s, stdin /dev/null (the driver's maxima_run), 8 workers.

Record (repo root; the P0 worktree core must exist):
  python3 probes/matcher/16-seen-guard-trace.py > probes/matcher/16-seen-guard-trace.out
MR16_RAW_DIR=<dir> also writes each run's raw output there.

Class-1 set (the P5b class-1 EQ-REWRITE groups; P0 arm on every entry):
  python3 probes/matcher/16-seen-guard-trace.py --set class1 \\
    --entries probes/matcher/16-seen-guard-trace.class1.tsv > probes/matcher/16-seen-guard-trace.class1.out
"""

import argparse
import concurrent.futures
import hashlib
import importlib.util
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
CAP = 30
WORKERS = 8
SUITE = "reference/maxima-syntax-test-suite"
P0_REV = "0a6664c"
P0_CORE = os.environ.get("MR16_P0_CORE") or os.path.join(
    os.environ.get("TMPDIR") or "/tmp", "mr-p0-tree", "test", "mr_rules.core")
RAW_DIR = os.environ.get("MR16_RAW_DIR")

F23 = "2 Exponentials/2.3 Exponential functions.mac"
F315 = "3 Logarithms/3.1.5 u (a+b log(c x^n))^p.mac"
F314 = "3 Logarithms/3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p.mac"
F34 = "3 Logarithms/3.4 u (a+b log(c (d+e x^m)^n))^p.mac"
F35 = "3 Logarithms/3.5 Logarithm functions.mac"
# (group, file, entry, scope): scope eq = the nine EQ-REWRITE groups,
# noroute = the no-route groups (brief: covered if the same run shows a route).
ENTRIES = (
    [("c2 g1", F23, e, "eq") for e in (202, 247, 248, 391, 392)]
    + [("c2 g5", F23, 726, "eq"), ("c2 g6", F23, 557, "eq")]
    + [("c3 g6", F315, e, "eq") for e in (24, 27, 50, 52, 90, 93, 94)]
    + [("c3 g11", F315, e, "eq") for e in (51, 119, 120, 121)]
    + [("c3 g12", F34, e, "eq") for e in (383, 384, 387, 388)]
    + [("c3 g14", F315, 207, "eq")]
    + [("c3 g21", F314, e, "eq") for e in (448, 449, 450)]
    + [("c3 g48", F314, 350, "eq")]
    + [("c2 g3", F23, e, "noroute") for e in (624, 767)]
    + [("c3 g20", F34, 625, "noroute"), ("c3 g20", F35, 292, "noroute"), ("c3 g20", F35, 293, "noroute")]
    + [("c3 g51", F35, 83, "noroute")]
)
P0_GROUPS = {"c2 g1", "c3 g21"}

# ---------------------------------------------------------------------------
# Instrumentation, derived from the source.

SEENP_NORMALIZED = (
    "%mr_seenp(f) := block([looped, d, i], looped : false, if member(f, %mr_seen) then return(true), "
    "for i : 1 thru length(%mr_seen) do if is(looped) = false then ( d : errcatch(ratsimp(part(%mr_seen, i) - f)), "
    "if d # [] and is(part(d, 1) = 0) then looped : true ), looped)$")

COMMON = r'''
%mr16_n : 0$
%mr16_ids : []$
%mr16_path : []$
%mr16_emit_enter(f, kind, fb) := block([],
  %mr16_n : %mr16_n + 1,
  ?format(true, "~&MR16 ENTER id=~a kind=~a fb=~a dl=~a seenlen=~a path=~a f=~a~%",
          %mr16_n, kind, if fb then "true" else "false", depth_level, length(%mr_seen),
          string(%mr16_path), string(f)),
  ?finish\-output(),
  %mr16_n)$
%mr16_exit(outcome) := (
  ?format(true, "~&MR16 EXIT id=~a outcome=~a dl=~a seenlen=~a~%",
          %mr16_id, outcome, depth_level, length(%mr_seen)),
  ?finish\-output(), true)$
%mr16_hit(via, i) := block([mid],
  mid : if i <= length(%mr16_ids) then part(%mr16_ids, i) else "?",
  ?format(true, "~&MR16 SEEN id=~a via=~a idx=~a matchid=~a live=~a elem=~a~%",
          %mr16_id, via, i, mid, if member(mid, %mr16_path) then "yes" else "no",
          string(part(%mr_seen, i))),
  ?finish\-output(), true)$
%mr16_member(f) := block([i, k],
  if member(f, %mr_seen) then (
    k : 0,
    for i : 1 thru length(%mr_seen) do
      if k = 0 and member(f, [part(%mr_seen, i)]) then k : i,
    %mr16_hit("exact", k),
    true)
  else false)$
/* %mr_seenp's semantics (checked against the source), with the hit
   reported; %mr16_exact_only true = the diagnostic exact-only arm. */
%mr16_seenp(f) := block([looped, d, i, hit],
  looped : false, hit : 0,
  if %mr16_member(f) then return(true),
  if %mr16_exact_only then return(false),
  for i : 1 thru length(%mr_seen) do
    if is(looped) = false then (
      d : errcatch(ratsimp(part(%mr_seen, i) - f)),
      if d # [] and is(part(d, 1) = 0) then (looped : true, hit : i)
    ),
  if looped then %mr16_hit("ratsimp", hit),
  looped)$
%mr_seenp(f) := %mr16_seenp(f)$
%mr16_pass(n, ans) := (
  ?format(true, "~&MR16 PASS id=~a n=~a result=~a~%", %mr16_id, n,
          if ans = false then "false" else "answer"),
  ?finish\-output(), ans)$
%mr16_returned(r) := (
  ?format(true, "~&MR16 RETURNED t=~a answer=~a~%", elapsed_real_time(), string(r)),
  ?finish\-output(), r)$
'''

ENTER_VARS = "%mr16_id, %mr16_path : %mr16_path"
PUSH_ID = "  %mr16_ids : cons(%mr16_id, %mr16_ids),\n"
POP_ID = "  %mr16_ids : rest(%mr16_ids),\n"


def normalize(text):
    return re.sub(r"\s+", " ", re.sub(r"/\*.*?\*/", " ", text, flags=re.S)).strip()


def extract(src, head, tail):
    assert src.count(head) == 1, f"head count {src.count(head)}: {head!r}"
    i = src.index(head)
    return src[i:src.index(tail, i) + len(tail)]


def patch(text, pairs):
    for old, new in pairs:
        n = text.count(old)
        assert n == 1, f"anchor count {n}: {old!r}"
        text = text.replace(old, new)
    return text


def check_seenp(src, label):
    got = normalize(extract(src, "%mr_seenp(f) := block(", "  looped)$"))
    assert got == SEENP_NORMALIZED, f"{label} %mr_seenp differs from the probe's copy:\n{got}"


def fixed_instrumentation(src):
    check_seenp(src, "HEAD")
    body = extract(src, "%mr_top_body(f, x, fb, exact) := block([ans],", "  ) else ans)$")
    head = "%mr_top_body(f, x, fb, exact) := block([ans],\n  depth_level : depth_level + 1,\n"
    return patch(body, [
        (head, "%mr_top_body(f, x, fb, exact) := block([ans, " + ENTER_VARS + "],\n"
               "  depth_level : depth_level + 1,\n"
               "  %mr16_id : %mr16_emit_enter(f, if exact then \"exact\" else \"seenp\", fb),\n"
               "  %mr16_path : cons(%mr16_id, %mr16_path),\n"),
        ("  if depth_level > %mr_max_depth then (\n    depth_level : depth_level - 1,\n",
         "  if depth_level > %mr_max_depth then (\n    depth_level : depth_level - 1,\n"
         "    %mr16_exit(\"depthcap\"),\n"),
        ("  if (if exact then member(f, %mr_seen) else %mr_seenp(f)) then (\n    depth_level : depth_level - 1,\n",
         "  if (if exact then %mr16_member(f) else %mr16_seenp(f)) then (\n    depth_level : depth_level - 1,\n"
         "    %mr16_exit(\"seen-hit\"),\n"),
        ("  %mr_seen : cons(f, %mr_seen),\n", "  %mr_seen : cons(f, %mr_seen),\n" + PUSH_ID),
        ("  %mr_seen : rest(%mr_seen),\n", "  %mr_seen : rest(%mr_seen),\n" + POP_ID),
        ("  if ans = false then (\n    if fb then integrate(f, x)\n",
         "  %mr16_exit(if ans = false then \"nofire\" else \"fired\"),\n"
         "  if ans = false then (\n    if fb then integrate(f, x)\n"),
    ]) + "\n"


def p0_instrumentation(src):
    check_seenp(src, "P0")
    top = extract(src, "mr_top(f, x, fb) := block([ans],", "  ) else ans)$")
    top = patch(top, [
        ("mr_top(f, x, fb) := block([ans],\n  depth_level : depth_level + 1,\n",
         "mr_top(f, x, fb) := block([ans, " + ENTER_VARS + "],\n  depth_level : depth_level + 1,\n"
         "  %mr16_id : %mr16_emit_enter(f, \"p0-mr_top\", fb),\n"
         "  %mr16_path : cons(%mr16_id, %mr16_path),\n"),
        ("  if depth_level > %mr_max_depth then (\n    depth_level : depth_level - 1,\n",
         "  if depth_level > %mr_max_depth then (\n    depth_level : depth_level - 1,\n"
         "    %mr16_exit(\"depthcap\"),\n"),
        ("  if %mr_seenp(f) then (\n    depth_level : depth_level - 1,\n",
         "  if %mr16_seenp(f) then (\n    depth_level : depth_level - 1,\n    %mr16_exit(\"seen-hit\"),\n"),
        ("  %mr_seen : cons(f, %mr_seen),\n", "  %mr_seen : cons(f, %mr_seen),\n" + PUSH_ID),
        ("ans : %mr_dispatch(f, x, mr_rule_table, depth_level),",
         "ans : %mr16_pass(1, %mr_dispatch(f, x, mr_rule_table, depth_level)),"),
        ("  %mr_seen : rest(%mr_seen),\n", "  %mr_seen : rest(%mr_seen),\n" + POP_ID),
        ("ans : %mr_dispatch_rev(f, x, mr_rule_table, depth_level),",
         "ans : %mr16_pass(2, %mr_dispatch_rev(f, x, mr_rule_table, depth_level)),"),
        ("ans : %mr_dispatch_i1(f, x, mr_rule_table, depth_level),",
         "ans : %mr16_pass(3, %mr_dispatch_i1(f, x, mr_rule_table, depth_level)),"),
        ("  if ans = false then (\n    if fb then integrate(f, x)\n",
         "  %mr16_exit(if ans = false then \"nofire\" else \"fired\"),\n"
         "  if ans = false then (\n    if fb then integrate(f, x)\n"),
    ])
    hyb = extract(src, "%mr_hybrid_body(f, x, mode) := block([ans, sp],",
                  "if ans = false then integrate(f, x) else ans)$")
    hyb = patch(hyb, [
        ("%mr_hybrid_body(f, x, mode) := block([ans, sp],\n"
         "  sp : if mode = \"exact\" then is(member(f, %mr_seen) # false)\n       else %mr_seenp(f),\n",
         "%mr_hybrid_body(f, x, mode) := block([ans, sp, " + ENTER_VARS + "],\n"
         "  %mr16_id : %mr16_emit_enter(f, if mode = \"exact\" then \"p0-hybrid-exact\" else \"p0-hybrid-alg\", true),\n"
         "  %mr16_path : cons(%mr16_id, %mr16_path),\n"
         "  sp : if mode = \"exact\" then is(%mr16_member(f) # false)\n       else %mr16_seenp(f),\n"),
        ("    depth_level : depth_level - 1,\n    return(integrate(f, x))\n  ),\n  if is(sp)",
         "    depth_level : depth_level - 1,\n    %mr16_exit(\"depthcap\"),\n    return(integrate(f, x))\n  ),\n  if is(sp)"),
        ("  if is(sp) then (\n    depth_level : depth_level - 1,\n",
         "  if is(sp) then (\n    depth_level : depth_level - 1,\n    %mr16_exit(\"seen-hit\"),\n"),
        ("  %mr_seen : cons(f, %mr_seen),\n", "  %mr_seen : cons(f, %mr_seen),\n" + PUSH_ID),
        ("ans : %mr_dispatch(f, x, mr_rule_table, depth_level),",
         "ans : %mr16_pass(1, %mr_dispatch(f, x, mr_rule_table, depth_level)),"),
        ("ans : %mr_dispatch_rev(f, x, mr_rule_table, depth_level),",
         "ans : %mr16_pass(2, %mr_dispatch_rev(f, x, mr_rule_table, depth_level)),"),
        ("ans : %mr_dispatch_i1(f, x, mr_rule_table, depth_level),",
         "ans : %mr16_pass(3, %mr_dispatch_i1(f, x, mr_rule_table, depth_level)),"),
        ("  %mr_seen : rest(%mr_seen),\n", "  %mr_seen : rest(%mr_seen),\n" + POP_ID),
        ("  if ans = false then integrate(f, x) else ans)$",
         "  %mr16_exit(if ans = false then \"nofire\" else \"fired\"),\n"
         "  if ans = false then integrate(f, x) else ans)$"),
    ])
    return top + "\n" + hyb + "\n"


# ---------------------------------------------------------------------------
# Driver modules (one per core: the pin is read at import).

def load_driver(tag, pin, section="2 Exponentials"):
    path = os.path.join(ROOT, "test", "corpus_driver.py")
    saved_argv, saved_pin = sys.argv, os.environ.get("MR_RULES_CORE_PATH")
    sys.argv = [path, section + "/", "999999", str(CAP), SUITE]
    if pin:
        os.environ["MR_RULES_CORE_PATH"] = pin
    else:
        os.environ.pop("MR_RULES_CORE_PATH", None)
    try:
        spec = importlib.util.spec_from_file_location("corpus_driver_" + tag, path)
        d = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(d)
    finally:
        sys.argv = saved_argv
        if saved_pin is None:
            os.environ.pop("MR_RULES_CORE_PATH", None)
        else:
            os.environ["MR_RULES_CORE_PATH"] = saved_pin
    assert d.USE_RULES_CORE, f"{tag}: no rules core in use"
    return d


ENTER_RX = re.compile(r"^MR16 ENTER id=(\d+) kind=(\S+) fb=(\S+) dl=(-?\d+) seenlen=(\d+) path=\[([\d,]*)\] f=(.*)$")
SEEN_RX = re.compile(r"^MR16 SEEN id=(\d+) via=(\S+) idx=(\d+) matchid=(\S+) live=(\S+) elem=(.*)$")
EXIT_RX = re.compile(r"^MR16 EXIT id=(\d+) outcome=(\S+) dl=(-?\d+) seenlen=(\d+)$")
PASS_RX = re.compile(r"^MR16 PASS id=(\d+) n=(\d+) result=(\S+)$")
RET_RX = re.compile(r"^MR16 RETURNED t=(\S+) answer=(.*)$")
OUTCOME_RX = re.compile(r"rubi: rule\s+(\S+)(?:\s+(r\d+))?\s+(fired on|declined on|misfire|cond not accepted|matcher fault)")


def rule_name(key, n):
    return f"{key}_{n}" if n else re.sub(r"^_mr_rule_", "", key)


def parse(out):
    calls, pending, order = {}, {}, []
    cur, returned = None, None
    for line in out.splitlines():
        if line.startswith("MR16 "):
            m = ENTER_RX.match(line)
            if m:
                i = int(m.group(1))
                path = [int(p) for p in m.group(6).split(",") if p]
                calls[i] = dict(id=i, kind=m.group(2), fb=m.group(3), dl=int(m.group(4)),
                                seenlen=int(m.group(5)), path=path, f=m.group(7), seen=None,
                                outcome=None, fires=[], owner=None, passes=[], exit_seenlen=None)
                order.append(i)
                cur = i
                continue
            m = SEEN_RX.match(line)
            if m:
                calls[int(m.group(1))]["seen"] = dict(via=m.group(2), idx=int(m.group(3)), matchid=m.group(4),
                                                      live=m.group(5), elem=m.group(6))
                continue
            m = EXIT_RX.match(line)
            if m:
                c = calls[int(m.group(1))]
                c["outcome"], c["exit_seenlen"] = m.group(2), int(m.group(4))
                parent = c["path"][0] if c["path"] else None
                if parent is not None:
                    pending.setdefault(parent, []).append(c["id"])
                cur = parent
                continue
            m = PASS_RX.match(line)
            if m:
                c = calls[int(m.group(1))]
                c["passes"].append((int(m.group(2)), m.group(3), c["fires"][-1] if c["fires"] else None))
                continue
            m = RET_RX.match(line)
            if m:
                returned = dict(t=m.group(1), answer=m.group(2))
            continue
        m = OUTCOME_RX.search(line)
        if m and cur is not None:
            rule, kind = rule_name(m.group(1), m.group(2)), m.group(3).split()[0]
            c = calls[cur]
            if kind == "fired":
                c["fires"].append(rule)
            for ch in pending.pop(cur, []):
                calls[ch]["owner"] = f"{rule}:{kind}"
    for i in order:
        c = calls[i]
        if c["outcome"] == "fired":
            c["rule"] = c["fires"][-1] if c["fires"] else "?"
            answering = [p for p in c["passes"] if p[1] == "answer"]
            if answering:
                c["rule"] += f"@pass{answering[0][0]}"
        elif c["outcome"] is None:
            c["rule"] = "unwound" if returned else "open"
        else:
            c["rule"] = "fall-through:" + c["outcome"]
    return [calls[i] for i in order], returned


def run_one(d, instr, exact_only, section_file, e):
    path = os.path.join(ROOT, SUITE, section_file)
    entries, line_nos = d.extract_entries(path)
    els = d.split_elements(entries[e - 1][1:-1])
    f_text, var_text, e_text = d.normalize_heads(els[0]), els[1], d.normalize_heads(els[3])
    e_text2 = d.normalize_heads(els[4]) if len(els) == 5 else None
    body = d.build_text(f_text, var_text, e_text, e_text2)
    # The answer print goes AFTER the prompt-answer lines that follow the
    # mr_r line (batch_answers_from_file reads the lines after the current
    # statement as prompt answers); the second answer block, after the
    # classification, is left alone.
    answers = "pos$\n" * 40 + "no$\n" * 20
    i = body.index("\nmr_r: ")
    j = body.index(answers, i)
    assert body[i:j].count("\n") == 2, "answer-line anchor: the answer block must follow the mr_r line"
    j += len(answers)
    body = body[:j] + "%mr16_returned(mr_r)$\n" + body[j:]
    text = ("rubi_verbose : true$\n" + f"%mr16_exact_only : {'true' if exact_only else 'false'}$\n"
            + COMMON + instr + body)
    import time
    ts = time.time()
    out, timed_out = d.maxima_run(text, CAP)
    dt = time.time() - ts
    cls = next((s.strip()[6:].strip() for s in out.splitlines() if s.strip().startswith("CLASS ")), None)
    if cls is None:
        cls = "timeout" if timed_out else "error"
    calls, returned = parse(out)
    return dict(cls=cls, t=dt, calls=calls, returned=returned, line=line_nos[e - 1],
                fires=[rule_name(m.group(1), m.group(2)) for m in OUTCOME_RX.finditer(out)
                       if m.group(3) == "fired on"], out=out,
                faults=len(re.findall(r"misfire|matcher fault", out)))


def p10_final30():
    rec = {}
    for n in (1, 2, 3):
        p = f"probes/matcher/10-p5b-attribution.class{n}.summary.out"
        for s in open(p, encoding="utf-8"):
            m = re.match(r"^\s+(.+?\.mac) e(\d+)\s+record .*?\| final30 (\S+) ", s)
            if m:
                rec[(m.group(1), int(m.group(2)))] = m.group(3)
    return rec


def short(s, n=110):
    return s if len(s) <= n else s[:n] + "..."


def seen_text(c):
    s = c["seen"]
    if not s:
        return "-"
    return f"{s['via']}@#{s['matchid']}(idx{s['idx']},live={s['live']})"


def ratsimp_hits(r):
    return [c for c in r["calls"] if c["seen"] and c["seen"]["via"] == "ratsimp"]


def call_lines(r, limit=250):
    calls = r["calls"]
    keep = set(range(len(calls))) if len(calls) <= limit else (
        set(range(limit)) | {k for k, c in enumerate(calls) if c["seen"]})
    rows = []
    for k, c in enumerate(calls):
        if k not in keep:
            continue
        rows.append(f"    #{c['id']} d={len(c['path']) + 1} dl={c['dl']} {c['kind']} fb={c['fb']} "
                    f"seenlen={c['seenlen']} seen={seen_text(c)} out={c['rule']} owner={c['owner'] or '-'} "
                    f"f={short(c['f'])}")
        if c["seen"]:
            rows.append(f"        matched elem={short(c['seen']['elem'])}")
    if len(calls) > limit:
        rows.append(f"    ({len(calls) - len(keep)} further calls without a seen hit omitted)")
    return rows


def read_entry_tsvs(paths):
    """group<TAB>file path under the suite<TAB>e<n>, one entry per line."""
    out = []
    for p in paths:
        for n, s in enumerate(open(p, encoding="utf-8"), 1):
            if not s.strip():
                continue
            cols = s.rstrip("\n").split("\t")
            assert len(cols) == 3 and re.fullmatch(r"e\d+", cols[2]), f"{p}:{n}: bad row {s!r}"
            assert cols[1].startswith("1 Algebraic functions/"), f"{p}:{n}: not a class-1 file"
            assert os.path.exists(os.path.join(ROOT, SUITE, cols[1])), f"{p}:{n}: no such file"
            out.append(("c1 " + cols[0], cols[1], int(cols[2][1:]), "eq"))
    return out


def main():
    ap = argparse.ArgumentParser(description="probe 16: seen-guard trace")
    ap.add_argument("--set", choices=("class23", "class1"), default="class23",
                    help="class23 (default): the built-in class 2/3 ENTRIES; class1: --entries TSVs, P0 arm on all")
    ap.add_argument("--entries", nargs="+", help="class-1 entry TSV(s): group<TAB>suite file path<TAB>e<n>")
    args = ap.parse_args()
    if args.set == "class1":
        assert args.entries, "--set class1 needs --entries <tsv> [...]"
        entries = read_entry_tsvs(args.entries)
        p0_wanted = lambda group: True
        label = lambda sf: sf.split("/")[-1].split()[0]
    else:
        assert not args.entries, "--entries is for --set class1"
        entries = ENTRIES
        p0_wanted = lambda group: group in P0_GROUPS
        label = lambda sf: sf.split("/")[-1][:5].strip()
    head_src = open("maxima_rubi_utils.mac", encoding="utf-8").read()
    p0_src = subprocess.run(["git", "show", f"{P0_REV}:maxima_rubi_utils.mac"], capture_output=True,
                            text=True, check=True).stdout
    fixed_instr, p0_instr = fixed_instrumentation(head_src), p0_instrumentation(p0_src)
    assert os.path.exists(P0_CORE), f"P0 core missing: {P0_CORE}"
    drivers = {}

    def drv(kind, sf):
        # One driver module per core and corpus section: the driver's section
        # argument follows the entry's class.
        section = sf.split("/")[0]
        key = (kind, section)
        if key not in drivers:
            drivers[key] = load_driver(f"{kind}_{section.split()[0]}", P0_CORE if kind == "p0" else None, section)
        return drivers[key]

    d_fixed, d_p0 = drv("fixed", entries[0][1]), drv("p0", entries[0][1])

    jobs = []
    for idx, (group, sf, e, scope) in enumerate(entries):
        jobs.append((idx, "trace", drv("fixed", sf), fixed_instr, False, sf, e))
        jobs.append((idx, "exact-only", drv("fixed", sf), fixed_instr, True, sf, e))
        if p0_wanted(group):
            jobs.append((idx, "p0", drv("p0", sf), p0_instr, False, sf, e))
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(run_one, j[2], j[3], j[4], j[5], j[6]): (j[0], j[1]) for j in jobs}
        for fu in concurrent.futures.as_completed(futs):
            results[futs[fu]] = fu.result()
    if RAW_DIR:
        os.makedirs(RAW_DIR, exist_ok=True)
        for (idx, arm), r in results.items():
            group, sf, e, _ = entries[idx]
            name = f"{group.replace(' ', '-')}-{label(sf)}-e{e}-{arm}.out"
            with open(os.path.join(RAW_DIR, name), "w", encoding="utf-8") as fh:
                fh.write(r["out"])

    git_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "maxima_rubi_utils.mac",
                            "maxima_rubi_dispatch.lisp", "maxima_rubi_match.lisp", "maxima_rubi_tree.lisp",
                            "rules", "test/corpus_driver.py"], capture_output=True, text=True).stdout.strip()

    def stamp(d):
        s = open(d.RULES_CORE_STAMP).read().split("\n")
        get = lambda k: next((x.split(None, 1)[1] for x in s if x.startswith(k + " ")), "?")
        return f"{d.RULES_CORE}  fingerprint {get('fingerprint')}  git_rev {get('git_rev')}"

    print("=== probes/matcher/16-seen-guard-trace  %s" % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    r = subprocess.run(["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
                       capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    print("\n".join(f"maxima: {s.strip()}" for s in r.stdout.splitlines()
                    if s.strip().startswith(("Maxima", "Lisp "))))
    print(f"git HEAD: {git_head}  (tracked runtime sources vs HEAD: {'clean' if not dirty else 'DIRTY ' + dirty})")
    print(f"core fixed: {stamp(d_fixed)}")
    print(f"core p0:    {stamp(d_p0)}")
    print(f"driver switches: {d_fixed.SWITCH_SETTINGS}   cap {CAP} s, {WORKERS} workers, stdin /dev/null")
    print(f"instrumentation: HEAD %mr_top_body / P0 {P0_REV} mr_top + %mr_hybrid_body, patched at asserted anchors;"
          f" %mr_seenp checked equal (normalized) in both trees; fixed sha1 "
          f"{hashlib.sha1(fixed_instr.encode()).hexdigest()[:12]}, p0 sha1 {hashlib.sha1(p0_instr.encode()).hexdigest()[:12]}")
    print("arms: trace = fixed core, seen test as HEAD; exact-only = fixed core, %mr_seenp exact member only "
          "(DIAGNOSTIC ARM, NOT A PROPOSED FIX); p0 = P0 core, seen test as P0.")
    if args.set == "class1":
        tsv_bytes = b"".join(open(p, "rb").read() for p in args.entries)
        print(f"entry set: class1 from {' '.join(args.entries)} ({len(entries)} entries, sha1 "
              f"{hashlib.sha1(tsv_bytes).hexdigest()[:12]}); p0 arm on every entry")
    print("call line: #id d=<nesting depth> dl=<depth_level> <entry kind> fb seenlen=<length(%mr_seen) at entry> "
          "seen=<via>@#<matched call>(live=<matched call still on the path>) out=<rule[@pass] | fall-through:<branch>> "
          "owner=<parent's next rule-outcome line: the rule attempt that made the call>")
    rec = p10_final30()
    passed = failed = 0
    table, p0table = [], []
    for idx, (group, sf, e, scope) in enumerate(entries):
        print()
        print(f"--- {group} {sf} e{e} ({scope})")
        rows_ok = True
        for arm in ("trace", "exact-only", "p0"):
            if (idx, arm) not in results:
                continue
            r = results[(idx, arm)]
            hits = ratsimp_hits(r)
            ex_hits = [c for c in r["calls"] if c["seen"] and c["seen"]["via"] == "exact"]
            open_calls = [c for c in r["calls"] if c["outcome"] is None]
            top = r["calls"][0]["rule"] if r["calls"] else "-"
            print(f"  [{arm}] class={r['cls']} t={r['t']:.1f}s L{r['line']} returned={'yes t=' + r['returned']['t'] if r['returned'] else 'NO'}"
                  f" calls={len(r['calls'])} ratsimp-hits={len(hits)} exact-hits={len(ex_hits)}"
                  f" unexited={len(open_calls)} misfire/fault-lines={r['faults']} top={top}")
            print(f"    fires={','.join(r['fires']) or '-'}")
            if r["returned"]:
                print(f"    answer sha1={hashlib.sha1(r['returned']['answer'].encode()).hexdigest()[:12]} "
                      f"{short(r['returned']['answer'], 160)}")
            print("\n".join(call_lines(r)))
            if not r["returned"] or not r["calls"]:
                rows_ok = False
        tr, ctl = results[(idx, "trace")], results[(idx, "exact-only")]
        hits = ratsimp_hits(tr)
        hit_txt = "yes " + ",".join(f"#{c['id']}@{c['owner'] or '?'}" for c in hits) if hits else "no"
        same = ("same" if tr["returned"] and ctl["returned"] and tr["returned"]["answer"] == ctl["returned"]["answer"]
                else "differs" if tr["returned"] and ctl["returned"] else "n/a")
        table.append((f"{label(sf)} e{e}", group, hit_txt, tr["cls"], ctl["cls"], same,
                      rec.get((sf, e), "?"), "ok" if rows_ok else "INCOMPLETE"))
        if (idx, "p0") in results:
            p = results[(idx, "p0")]
            ph = ratsimp_hits(p)
            p0table.append((f"{label(sf)} e{e}", group, p["cls"],
                            p["calls"][0]["rule"] if p["calls"] else "-",
                            "yes " + ",".join(f"#{c['id']}@{c['owner'] or '?'}" for c in ph) if ph else "no",
                            "ok" if p["returned"] and p["calls"] else "INCOMPLETE"))
        if rows_ok:
            passed += 1
        else:
            failed += 1
    print()
    print("=== table (fixed core)")
    print("| entry | group | ratsimp-seen-hit (trace arm): #call@owner rule | class trace | class exact-only | answer trace vs exact-only | probe-10 final30 class | trace |")
    print("|---|---|---|---|---|---|---|---|")
    for row in table:
        print("| " + " | ".join(row) + " |")
    print()
    print("=== table (P0 core)")
    print("| entry | group | class p0 | top rule @ pass | ratsimp-seen-hit | trace |")
    print("|---|---|---|---|---|---|")
    for row in p0table:
        print("| " + " | ".join(row) + " |")
    print(f"Results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    main()
