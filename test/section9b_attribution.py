#!/usr/bin/env python3
"""Section-9 port, post-ticket-14/15 re-measure (handoff 2026-09-24, next
move 2): attribute every PASS->FAIL of the `.s9b` records against the
promoted `.s9-ref` baselines, from committed records only (no Maxima).

    python3 test/section9b_attribution.py [> test/section9b_attribution.out]

Inputs, under test/:

  corpus_class<N>.s9-ref.out   the baseline (core 0182d32c, master c95c6ed)
  corpus_class<N>.s9.out       the PRE-fix branch arm (core 434c241a), whose
                               PASS->FAIL were attributed in
                               section9_attribution.out
  corpus_class<N>.s9b.out      the branch arm after tickets 14/15 (cd0a421)
  section9b_paired_class<N>.{ref,new}/section9b_changed_class<N>.timeout30s.out
                               the paired rerun of every changed entry, both
                               cores concurrently at 12 workers each
  ../probes/section9/11-timing-ab.out (optional)
                               the alternating sequential timing A/B of the
                               entries left `timeout` on the branch

Buckets, in order:

  noise        the paired rerun has the branch core PASS it (the 24-worker
               verdict did not reproduce at 12 workers with the reference
               running alongside), or the reference core FAILs it there.
  cap / cost   branch `timeout` on an entry the reference answered: the
               sequential A/B (when present) splits them -- `cost` when the
               branch is at or over 30 s or 1.2x the reference, `cap`
               otherwise; with no timing row the entry is `timeout?`.
  carried      FAIL in the pre-fix `.s9` record too (so already attributed in
               section9_attribution.out) and not a timeout now.
  new          everything else: a genuine verdict change the fixes introduced,
               listed entry by entry for hand attribution.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ab_records as ab  # noqa: E402
from corpus_driver import PASS_CLASSES  # noqa: E402

CLASSES = (1, 2, 3, 6)
ORDER = ("noise", "cap", "cost", "timeout?", "carried", "new")


def read(path, missing_ok=False):
    full = os.path.join(ROOT, path)
    if missing_ok and not os.path.exists(full):
        return {}
    return ab.load_record(full)


def timing():
    out = {}
    path = os.path.join(ROOT, "probes", "section9", "11-timing-ab.out")
    if not os.path.exists(path):
        return out
    rx = re.compile(r"^(ref|new)\s+(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L\d+\s*$")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = rx.match(line.rstrip("\n"))
            if m:
                out.setdefault((m.group(4), int(m.group(5))), {})[m.group(1)] = (
                    m.group(2), float(m.group(3)))
    return out


def npass(rec):
    return sum(1 for v in rec.values() if v[0] in PASS_CLASSES)


def main():
    times = timing()
    grand = {}
    for n in CLASSES:
        base = read(f"test/corpus_class{n}.s9-ref.out")
        old = read(f"test/corpus_class{n}.s9.out")
        new = read(f"test/corpus_class{n}.s9b.out")
        pref = read(f"test/section9b_paired_class{n}.ref/"
                    f"section9b_changed_class{n}.timeout30s.out", True)
        pnew = read(f"test/section9b_paired_class{n}.new/"
                    f"section9b_changed_class{n}.timeout30s.out", True)
        pf = sorted(k for k in base if k in new and base[k][0] in PASS_CLASSES
                    and new[k][0] not in PASS_CLASSES)
        fp = sum(1 for k in base if k in new and base[k][0] not in PASS_CLASSES
                 and new[k][0] in PASS_CLASSES)
        print(f"=== class {n}: PASS ref {npass(base)} -> pre-fix {npass(old)}"
              f" -> now {npass(new)}  (vs ref: PASS->FAIL {len(pf)}, FAIL->PASS {fp})")
        buckets = {}
        for k in pf:
            b, w = base[k][0], new[k][0]
            if (k in pnew and pnew[k][0] in PASS_CLASSES) or (
                    k in pref and pref[k][0] not in PASS_CLASSES):
                cause = "noise"
            elif w == "timeout" and b in ("verified", "expected"):
                if k in times and "ref" in times[k] and "new" in times[k]:
                    tr, tn = times[k]["ref"][1], times[k]["new"][1]
                    cause = "cost" if tn >= 30.0 or tn >= 1.2 * tr else "cap"
                else:
                    cause = "timeout?"
            elif k in old and old[k][0] not in PASS_CLASSES:
                cause = "carried"
            else:
                cause = "new"
            buckets.setdefault(cause, []).append(k)
            grand[cause] = grand.get(cause, 0) + 1
        for cause in ORDER:
            ks = buckets.get(cause, [])
            if not ks:
                continue
            print(f"  {cause:<9} {len(ks)}")
            for k in ks:
                extra = ""
                if k in times:
                    t = times[k]
                    extra = "  [seq A/B: " + ", ".join(
                        f"{a} {t[a][1]}s {t[a][0]}" for a in ("ref", "new") if a in t) + "]"
                if k in pnew:
                    extra += f"  [paired: ref {pref.get(k, ('?',))[0]}, new {pnew[k][0]}]"
                oldc = old[k][0] if k in old else "?"
                print(f"      {base[k][0]} {base[k][1]}s -> {new[k][0]} {new[k][1]}s"
                      f" (pre-fix {oldc})  {k[0]} e{k[1]}{extra}")
        print()
    print("=== all four classes ===")
    for cause in ORDER:
        print(f"  {cause:<9} {grand.get(cause, 0)}")
    print(f"  {'TOTAL':<9} {sum(grand.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
