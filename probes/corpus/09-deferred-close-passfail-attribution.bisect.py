#!/usr/bin/env python3
"""Probe 09 bisection — for each class-3 PASS->FAIL entry that is PASS on
the campaign-base core (1d998cc) and FAIL on the final core (99e1eb1, C6b),
find the campaign commit whose rules core first makes it FAIL, by binary
search over the ordered per-commit cores (docs/corpus-class3-deferred-
uplift.md §5). Each probe is one probe-09 run of the single entry on one
core (the driver's exact per-entry text, 30 s cap, fired-rule trace).

Core sequence (index: core):
  0 1d998cc base (PASS, from .class3-base1d998cc.out)
  1 464d29f B1   2 d6cee4e B2   3 3c04b2e B4   4 52ffb6f C2   5 2fd677a C1
  6 d2ae62d C4   7 1c8a306 C3   8 9533528 B3   9 4702d4d C5  10 c25e8f6 C6
 11 final C6b (FAIL, from .class3-final.out)
Assumes a single PASS->FAIL step; the runs on both sides of the reported
step are recorded so a non-monotone entry is visible in the output.

Usage (repo root):
  CORE_DIR=<dir with core-<commit>/test/mr_rules.core> JOBS=2 \
    python3 probes/corpus/09-deferred-close-passfail-attribution.bisect.py
Output: probes/corpus/09-deferred-close-passfail-attribution.class3-bisect.out
"""

import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "probes", "corpus", "09-deferred-close-passfail-attribution")
OUT = P + ".class3-bisect.out"
CORE_DIR = os.environ["CORE_DIR"]
FINAL_CORE = os.environ.get("FINAL_CORE",
                            "/home/serge/src/maxima-rubi/test/mr_rules.core")
JOBS = int(os.environ.get("JOBS", "2"))
SEQ = [("1d998cc", "base"), ("464d29f", "B1"), ("d6cee4e", "B2"),
       ("3c04b2e", "B4"), ("52ffb6f", "C2"), ("2fd677a", "C1"),
       ("d2ae62d", "C4"), ("1c8a306", "C3"), ("9533528", "B3"),
       ("4702d4d", "C5"), ("c25e8f6", "C6"), ("99e1eb1", "C6b")]
PASS = {"verified", "expected", "no-answer"}
ROW = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s (.+?) e(\d+) L\d+\s+self=(\S+)"
                 r"\s+nfires=(\d+)\s+fires=(\S+)")


def core_path(i):
    if i == len(SEQ) - 1:
        return FINAL_CORE
    return os.path.join(CORE_DIR, f"core-{SEQ[i][0]}", "test", "mr_rules.core")


def rows(path):
    out = []
    for ln in open(path, encoding="utf-8"):
        m = ROW.match(ln.rstrip("\n"))
        if m:
            out.append((m.group(1), float(m.group(2)), m.group(7)))
    return out


def run_one(shard_line, i):
    with tempfile.TemporaryDirectory() as td:
        sh = os.path.join(td, "e.shard")
        out = os.path.join(td, "e.out")
        open(sh, "w").write(shard_line + "\n")
        env = dict(os.environ, MR_RULES_CORE_PATH=core_path(i))
        subprocess.run([sys.executable, P + ".py", "3 Logarithms", sh, out, "30"],
                       cwd=ROOT, env=env, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=600)
        r = rows(out)
        return r[0] if r else ("error", 0.0, "-")


def bisect(item):
    shard_line, base_row, final_row, label = item
    runs = {0: base_row, len(SEQ) - 1: final_row}
    lo, hi = 0, len(SEQ) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        runs[mid] = run_one(shard_line, mid)
        if runs[mid][0] in PASS:
            lo = mid
        else:
            hi = mid
    cells = " ".join(f"{SEQ[i][1]}:{runs[i][0]}/{runs[i][1]:.1f}s"
                     for i in sorted(runs))
    return (f"{label}  step {SEQ[lo][1]}->{SEQ[hi][1]} (first FAIL core "
            f"{SEQ[hi][0]} {SEQ[hi][1]})\n    runs {cells}\n"
            f"    last-PASS fires: {runs[lo][2]}\n"
            f"    first-FAIL fires: {runs[hi][2]}")


def main():
    shard = [ln.strip() for ln in open(P + ".class3.shard") if ln.strip()]
    base = rows(P + ".class3-base1d998cc.out")
    final = rows(P + ".class3-final.out")
    labels = [ln for ln in open(P + ".class3-final.out") if ROW.match(ln)]
    assert len(shard) == len(base) == len(final) == len(labels)
    items = []
    for s, b, f, lab in zip(shard, base, final, labels):
        if b[0] in PASS and f[0] not in PASS:
            m = ROW.match(lab)
            items.append((s, b, f, f"{m.group(3).split('/')[-1].split(' ')[0]} e{m.group(4)}"))
    head = [f"=== probe 09 bisection — class 3 ({len(items)} entries: base PASS, final FAIL) ===",
            f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "sequence: " + " ".join(f"{i}={c}/{n}" for i, (c, n) in enumerate(SEQ)),
            f"cores: {CORE_DIR}/core-<commit>/test/mr_rules.core; final {FINAL_CORE}", ""]
    with ThreadPoolExecutor(max_workers=JOBS) as ex:
        results = list(ex.map(bisect, items))
    txt = "\n".join(head + results) + "\n"
    open(OUT, "w", encoding="utf-8").write(txt)
    print(txt, end="")


if __name__ == "__main__":
    main()
