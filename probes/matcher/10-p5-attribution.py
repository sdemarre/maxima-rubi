#!/usr/bin/env python3
"""Probe 10 -- matcher substrate P5: per-entry attribution runs for the
final record's A/B against the P0 record (spec
docs/superpowers/specs/2026-09-12-matcher-substrate-design.md section 4 P5;
the method of probes/corpus/09-deferred-close-passfail-attribution.py,
docs/corpus-class3-deferred-uplift.md section 5.3).

Selects entries from the two merged records and runs each through the
driver's EXACT per-entry text (test/corpus_driver.py build_text: the same
switch assignments from MR_SWITCHES, zero chain, classification and
answers filler) on the core the driver resolves (MR_RULES_CORE_PATH pins
one; otherwise the tree's current core), with two additions that cannot
change the class:

  * `rubi_verbose : true$` prepended: every dispatch that answers prints
    `rubi: rule <key> r<n> fired on ...` (the substrate) or
    `rubi: rule _mr_rule_<key>_r<n> fired on ...` (the P0 core, pass-1 fires
    only; its pass-2/3 fires ran in Lisp and are not traced). Fires print in
    completion order, so the last one is the top-level rule. Both spellings
    are written as `<key>_r<n>`.
  * noun-expected entries (corpus answer Unintegrable / CannotIntegrate):
    the self-diff zero chain on the answer is appended after the CLASS line
    (`self=1` closes, `self=0` does not, `self=cut` the cap hit first,
    `self=n/a` the answer is a noun).
  * the answer (cut at 300 characters) is printed after the CLASS line; a
    row of an `unverified` entry ends `ans=<answer>` (wrong vs unverifiable
    is read from it), and a row of an `error` entry ends `err=<the Maxima or
    Lisp error message>` (matcher translation fixes design section 4 step 5).

select:
  passfail    PASS in the P0 record, FAIL in the final record
  passfail-timeout  the passfail entries the final record classifies timeout
                    (the input of the 120 s cap run)
  newtimeout  timeout in the final record, not timeout in the P0 record
  newerror    error in the final record, not error in the P0 record

Walls are measured under WORKERS concurrent subprocesses (the corpus runs'
own condition is 24 shards); they are attribution evidence, not gates.

Usage (repo root):
  [MR_RULES_CORE_PATH=<core>] [MR_SWITCHES=...] python3 probes/matcher/10-p5-attribution.py \\
      <section> <P0-record> <final-record> <select> <out-file> [cap-seconds] [workers]
cap defaults to 30 (the record cap), workers to 8.
"""

import concurrent.futures
import importlib.util
import os
import re
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if len(sys.argv) < 6:
    raise SystemExit(__doc__)
SECTION, P0_REC, FINAL_REC, SELECT, OUT = sys.argv[1:6]
CAP = int(sys.argv[6]) if len(sys.argv) > 6 else 30
WORKERS = int(sys.argv[7]) if len(sys.argv) > 7 else 8
if SELECT not in ("passfail", "passfail-timeout", "newtimeout", "newerror"):
    raise SystemExit(f"unknown select {SELECT!r}")
P0_REC, FINAL_REC, OUT = (os.path.abspath(p) for p in (P0_REC, FINAL_REC, OUT))

os.chdir(ROOT)
DRIVER = os.path.join(ROOT, "test", "corpus_driver.py")
sys.argv = [DRIVER, SECTION + "/", "999999", str(CAP), "reference/maxima-syntax-test-suite"]
_spec = importlib.util.spec_from_file_location("corpus_driver", DRIVER)
d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d)
assert d.USE_RULES_CORE, "no rules core in use (build one: sh test/build_rules_core.sh)"
_spec = importlib.util.spec_from_file_location("ab_records", os.path.join(ROOT, "test", "ab_records.py"))
ab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ab)

FILLER = "pos$\n" * 40 + "no$\n" * 20
NOUN = ("block([], if atom(mr_r) then 0 else "
        "if is(string(op(mr_r)) = \"integrate\") "
        "or is(string(op(mr_r)) = \"unintegrable\") "
        "then 1 else 0)")
FIRE_RX = re.compile(r"rubi: rule\s+(\S+)(?:\s+(r\d+))?\s+fired on")
# the answer, cut at 300 characters, printed after the CLASS line (it cannot
# change the class); the row carries it for `unverified` entries
ANS_STMT = ("block([mr_s, linel : 100000], mr_s : string(mr_r), disp(concat(\"ANS \", "
            "if slength(mr_s) > 300 then concat(substring(mr_s, 1, 301), \"...\") else mr_s)))$\n")
ERR_RX = re.compile(r"fatal error|Heap exhausted|Control stack exhausted|Unhandled|RETRIEVE:")


def rule_name(m):
    if m.group(2):
        return f"{m.group(1)}_{m.group(2)}"
    return re.sub(r"^_mr_rule_", "", m.group(1))


def entry_text(f_text, var_text, e_text, e_text2):
    t = d.build_text(f_text, var_text, e_text, e_text2)
    assert t.endswith(FILLER)
    if e_text.startswith(("Unintegrable", "CannotIntegrate")):
        zv = d.zero_chain(f"diff(mr_r, {var_text}) - mr_f", var_text)
        self_stmt = (f"if is({NOUN} = 1) then disp(concat(\"SELF n/a\")) "
                     f"else disp(concat(\"SELF \", string({zv})))$\n")
        t = t[:-len(FILLER)] + self_stmt + FILLER
    t = t[:-len(FILLER)] + ANS_STMT + FILLER
    return "rubi_verbose : true$\n" + t


def error_text(out):
    """The Maxima / Lisp error messages of a subprocess's output, joined."""
    lines = [s.strip() for s in out.splitlines()]
    found = []
    for i, s in enumerate(lines):
        if s.startswith("-- an error"):
            prev = next((p for p in reversed(lines[:i]) if p and not p.startswith("#")), "")
            found.append(prev)
        elif s.startswith("Maxima encountered a Lisp error"):
            found.append(next((n for n in lines[i + 1:] if n), s))
        elif ERR_RX.search(s):
            found.append(s)
    text = " | ".join(dict.fromkeys(f for f in found if f))
    return re.sub(r"\s+", " ", text)[:300]


def selected_keys():
    pc = ab.driver_pass_classes()
    p0, fin = ab.load_record(P0_REC), ab.load_record(FINAL_REC)
    keys = []
    for k in sorted(p0.keys() & fin.keys()):
        a, b = p0[k][0], fin[k][0]
        if SELECT == "passfail" and a in pc and b not in pc:
            keys.append(k)
        elif SELECT == "passfail-timeout" and a in pc and b == "timeout":
            keys.append(k)
        elif SELECT == "newtimeout" and b == "timeout" and a != "timeout":
            keys.append(k)
        elif SELECT == "newerror" and b == "error" and a != "error":
            keys.append(k)
    return keys


def run_one(item):
    rel, e, path = item
    entries, line_nos = d.extract_entries(path)
    els = d.split_elements(entries[e - 1][1:-1])
    f_text, var_text = d.normalize_heads(els[0]), els[1]
    e_text = d.normalize_heads(els[3])
    e_text2 = d.normalize_heads(els[4]) if len(els) == 5 else None
    ts = time.time()
    out, timed_out = d.maxima_run(entry_text(f_text, var_text, e_text, e_text2), CAP)
    dt = time.time() - ts
    cls, selfv, ans = None, "-", None
    for s in out.splitlines():
        s = s.strip()
        if cls is None and s.startswith("CLASS "):
            cls = s[6:].strip()
        elif s.startswith("SELF "):
            selfv = s[5:].strip()
        elif ans is None and s.startswith("ANS "):
            ans = s[4:].strip()
    if cls is None:
        cls = "timeout" if timed_out else "error"
    if cls not in d.KNOWN_CLASSES:
        cls = "error"
    if e_text.startswith(("Unintegrable", "CannotIntegrate")) and selfv == "-":
        selfv = "cut"
    fires = [rule_name(m) for m in FIRE_RX.finditer(out)]
    seen = []
    for name in fires:
        if name not in seen:
            seen.append(name)
    top = fires[-1] if fires else "-"
    err = error_text(out) if cls == "error" else ""
    return (f"{cls:14s} t={dt:6.1f}s {rel} e{e} L{line_nos[e - 1]}"
            f"  self={selfv}  nfires={len(fires)}  top={top}"
            f"  fires={','.join(seen[:20]) or '-'}" + (",..." if len(seen) > 20 else "")
            + (f"  ans={ans.replace(' ', '')}" if cls == "unverified" and ans else "")
            + (f"  err={err}" if err else ""))


def main():
    rel_path = {rel: path for path, rel in d.file_list()}
    keys = selected_keys()
    stamp = open(d.RULES_CORE_STAMP).read().split("\n")
    fp = next((s.split()[1] for s in stamp if s.startswith("fingerprint ")), "?")
    head = [f"=== probe 10 -- P5 attribution runs (section {SECTION!r}, select {SELECT}) ===",
            f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"]
    r = d.subprocess.run(["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
                         capture_output=True, text=True, timeout=120)
    head += [f"maxima: {s.strip()}" for s in r.stdout.splitlines()
             if s.strip().startswith(("Maxima", "Lisp ", "Host "))]
    head += [f"core: {d.RULES_CORE}  fingerprint {fp}",
             f"switches: {d.run_records.switches_text(d.SWITCH_SETTINGS)}",
             f"P0 record: {os.path.relpath(P0_REC, ROOT)}  final record: {os.path.relpath(FINAL_REC, ROOT)}",
             f"entries: {len(keys)}  cap: {CAP}s  workers: {WORKERS}", ""]
    t0 = time.time()
    items = [(rel, e, rel_path[rel]) for rel, e in keys]
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        lines = list(pool.map(run_one, items))
    counts = {}
    for ln in lines:
        c = ln.split()[0]
        counts[c] = counts.get(c, 0) + 1
    passed = sum(v for c, v in counts.items() if c in d.PASS_CLASSES)
    tail = ["", "=== summary ==="] + [f"{c:14s} {counts[c]}" for c in sorted(counts)]
    tail += [f"total integrals: {len(lines)}", f"wall time: {time.time() - t0:.1f}s",
             f"Results: {passed} passed, {len(lines) - passed} failed"]
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(head + lines + tail) + "\n")
    print("\n".join(tail))


if __name__ == "__main__":
    main()
