#!/usr/bin/env python3
"""probe-radcan-fallback-live — does the zero-chain radcan(rat()) fallback
still rescue anything, on TODAY's rules?

The question is `.scratch/corpus-harness/issues/03` #2. The fallback was added
2026-08-28 because four measured entries' zero-diffs closed under
`radcan(rat())` and under no ratsimp/factor stage. Its guard
(test/test_driver_radcan_fallback.py) went red on 2026-09-20 because its
witnesses no longer reach the zero-test at all — the rule set moved under it at
commit 29d237a — which left open whether the fallback is still load-bearing or
has become dead code to remove.

METHOD. For every entry of the two files the fallback's own docstring names as
its beneficiaries — 1.1.3.8 and 1.2.1.4 — that the committed class-1 record
classifies `verified` or `expected`, run one fresh Maxima on the rules core:

  1. answer the integral exactly as the driver does (same switches, same
     prompt budget, same rubi call);
  2. build the zero-diff the driver's classification actually used — the SELF
     diff diff(mr_r,x) - mr_f for a `verified` entry, the expected diff
     diff(mr_r - (<expected>), x) for an `expected` one;
  3. evaluate `zero_chain(..., fallback=False)` FIRST. If it closes, the
     fallback is irrelevant to this entry and the run stops there — that is
     what keeps the probe cheap;
  4. only if it did NOT close, evaluate `zero_chain(..., fallback=True)`.
     Closing now, and only now, is a RESCUE: the fallback is what verified the
     entry.

Both chains come from `test/corpus_driver.zero_chain`, so the probe cannot
drift from the harness it is measuring — the `fallback` parameter exists for
exactly this (and for the guard).

WHAT A NULL RESULT MEANS. These two files are where the fallback's rescues
were measured in 2026-08-28; they are not the whole corpus. Zero rescues here
is strong evidence that the fallback no longer carries the class-1 record, but
it is not proof over all 25,697 entries — that needs the full fallback-off arm
and an ab_records.py diff, which is named in the output as the escalation.

Re-runnable (from repo root):
  sh probes/maxima/probe-radcan-fallback-live.run
"""

import collections
import concurrent.futures
import importlib.util
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RECORD = os.path.join(ROOT, "test", "corpus_class1.out")
FILES = ("1.1.3.8 P(x) (c x)^m (a+b x^n)^p",
         "1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p")
CLASSES = ("verified", "expected")
CAP = 150
WORKERS = 12          # at or below the 12 physical cores (AGENTS.md)


def load_driver():
    real = sys.argv[:]
    sys.argv = ["corpus_driver.py", "1 Algebraic functions/", "1", "30"]
    try:
        spec = importlib.util.spec_from_file_location(
            "corpus_driver", os.path.join(ROOT, "test", "corpus_driver.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.argv = real


drv = load_driver()


def targets():
    """[(short_file, entry_no, record_class)] from the committed record."""
    out = []
    rx = re.compile(r"^(\S+)\s+t=\s*\S+\s+.*/([^/]+)\.mac e(\d+) ")
    for line in open(RECORD, encoding="utf-8", errors="replace"):
        m = rx.match(line)
        if m and m.group(2) in FILES and m.group(1) in CLASSES:
            out.append((m.group(2), int(m.group(3)), m.group(1)))
    return out


def entry_index():
    """{short_file: (path, entries, line_nos)} for the files in play."""
    idx = {}
    for path, rel in drv.file_list():
        short = os.path.splitext(os.path.basename(rel))[0]
        if short in FILES:
            entries, lines = drv.extract_entries(path)
            idx[short] = (rel, entries, lines)
    return idx


IDX = None


def one(target):
    short, n, rec_cls = target
    rel, entries, lines = IDX[short]
    els = drv.split_elements(entries[n - 1][1:-1])
    f_text = drv.normalize_heads(els[0])
    var = els[1]
    e_text = drv.normalize_heads(els[3])
    label = f"{short} e{n}"

    if rec_cls == "verified":
        diff = f"diff(mr_r, {var}) - mr_f"
    else:
        diff = f"diff(mr_r - ({e_text}), {var})"

    no_fb = drv.zero_chain(diff, var, fallback=False)
    with_fb = drv.zero_chain(diff, var, fallback=True)
    switches = "".join(f"{k} : {v}$\n"
                       for k, v in drv.SWITCH_SETTINGS.items())
    text = (switches
            + "mr_depth_cap_hits : 0$\n"
            + f"mr_f: {f_text}$\n"
            + f"mr_r: rubi(mr_f, {var})$\n"
            + "pos$\n" * 40 + "no$\n" * 20
            + "MR_N: (" + no_fb + ")$\n"
            + "MR_W: if is(MR_N = 1) then 1 else (" + with_fb + ")$\n"
            + "MR_G: apply(freeof, [elliptic_f, elliptic_e, elliptic_pi, "
              "elliptic_ec, elliptic_eu, elliptic_kc, (" + diff + ")])$\n"
            + 'disp(concat("RES ", string(MR_N), " ", string(MR_W), '
              '" ", string(MR_G)))$\n'
            + "pos$\n" * 40 + "no$\n" * 20)
    t0 = time.time()
    out, hit_cap = drv.maxima_run(text, CAP)
    dt = time.time() - t0
    res = None
    for line in out.splitlines():
        m = re.match(r"^RES (\S+) (\S+) (\S+)\s*$", line.strip())
        if m:
            res = m.groups()
    if res is None:
        return (label, rec_cls, "timeout" if hit_cap else "error", dt)
    n_, w_, g_ = res
    if n_ == "1":
        verdict = "chain"
    elif w_ == "1":
        verdict = "RESCUE"
    else:
        verdict = "neither"
    return (label, rec_cls, verdict + ("" if g_ == "true" else " (gated)"), dt)


def main():
    global IDX
    print("probe-radcan-fallback-live — is the zero-chain radcan(rat()) "
          "fallback still load-bearing?")
    for line in drv.build_info_lines():
        print("  " + line)
    print(f"  cap kind: {drv.CAP_KIND}   per-entry cap: {CAP}s   "
          f"workers: {WORKERS}")
    print(f"  record:   {os.path.relpath(RECORD, ROOT)}")
    print(f"  files:    {', '.join(FILES)}")
    print(f"  classes:  {', '.join(CLASSES)}")
    IDX = entry_index()
    tg = targets()
    # `--limit N` is the smoke form: the first N targets only. A committed
    # .out is always a full run (no --limit on its .run line).
    if "--limit" in sys.argv:
        tg = tg[:int(sys.argv[sys.argv.index("--limit") + 1])]
        print("  *** --limit: SMOKE RUN, not a full measurement ***")
    print(f"  targets:  {len(tg)}")
    print()

    counts = collections.Counter()
    rescues = []
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(WORKERS) as ex:
        for i, (label, rec, verdict, dt) in enumerate(
                ex.map(one, tg), 1):
            counts[verdict] += 1
            if verdict.startswith("RESCUE"):
                rescues.append((label, rec, dt))
                print(f"  RESCUE  {label}  (record {rec}, {dt:.1f}s)")
            if i % 100 == 0:
                print(f"  ... {i}/{len(tg)}  {time.time() - t0:.0f}s elapsed")
    print()
    print("=" * 78)
    print("RESULT")
    print("=" * 78)
    for k, v in counts.most_common():
        print(f"  {v:5d}  {k}")
    print(f"  wall: {time.time() - t0:.0f}s")
    print()
    if rescues:
        print(f"  The fallback is LOAD-BEARING: it is the only stage that "
              f"closes {len(rescues)} of")
        print(f"  these {len(tg)} entries' zero-diffs. Any one of them is a "
              "witness the guard can")
        print("  be re-pointed at:")
        for label, rec, dt in rescues:
            print(f"    {label}  (record {rec}, {dt:.1f}s)")
    else:
        print("  NO RESCUE in this set. On today's rules the fallback closes "
              "nothing that the")
        print("  stage chain does not already close, across every "
              "`verified`/`expected` entry of")
        print("  the two files its own docstring names as its beneficiaries.")
        print()
        print("  This is NOT proof over all 25,697 class-1 entries. The "
              "escalation, if the")
        print("  question has to be closed outright, is the full "
              "fallback-off arm:")
        print("    MR_ZC_FALLBACK=0 python3 test/run_corpus_queue.py "
              "\"1 Algebraic functions\" \\")
        print("        --prev test/corpus_class1.out --workers 12 --launch")
        print("    python3 test/ab_records.py test/corpus_class1.out "
              "<new-record>")
        print("  Every PASS->FAIL line in that A/B is an entry the fallback "
              "rescues.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
