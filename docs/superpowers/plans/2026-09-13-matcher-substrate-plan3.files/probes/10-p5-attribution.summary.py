#!/usr/bin/env python3
"""Probe 10 summary -- join a class's P5 attribution runs into the per-entry
disposition table the user reviews (matcher substrate plan 3).

Inputs: the P0 record, the final record, and the probe-10 outputs of the
passfail selection on the final core at the record cap (--final30) and on
the P0 core (--p0), optionally the final core at a 120 s cap (--final120,
the timeouts among them) and the 100 s timeout re-check record of the final
record (--recheck).

Disposition of a PASS->FAIL entry (mechanical, first rule that applies):
  unmeasured     no --final30 or no --p0 row
  noise          PASS on the final core at 30 s: the final record's FAIL is
                 run-to-run noise
  p0-noise       FAIL on the P0 core at 30 s too: the P0 record's PASS is not
                 reproducible on its own rules under this build
  near-cap       the final core's 120 s run is a PASS class within 30 s
  slow-correct   the final core's 120 s run is a PASS class after 30 s
  deterministic  otherwise -- a substrate change, grouped by the final core's
                 class and top-level rule (the rule that answered, `-` when
                 no rule answered at the top level)

New timeouts (timeout in the final record, not in the P0 record) are listed
with their P0 class and, with --recheck, their class at 100 s.

Usage:
  python3 probes/matcher/10-p5-attribution.summary.py P0_RECORD FINAL_RECORD \\
      --final30 OUT --p0 OUT [--final120 OUT] [--recheck RECORD]
Ends with `Results: <attributed> passed, <unmeasured> failed`.
"""

import argparse
import importlib.util
import os
import re
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_spec = importlib.util.spec_from_file_location("ab_records", os.path.join(ROOT, "test", "ab_records.py"))
ab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ab)
ROW = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s (.+?) e(\d+) L\d+\s+self=(\S+)\s+nfires=(\d+)"
                 r"\s+top=(\S+)\s+fires=(\S+)")


def rows(path):
    out = OrderedDict()
    if path:
        for line in open(path, encoding="utf-8"):
            m = ROW.match(line.rstrip("\n"))
            if m:
                out[(m.group(3), int(m.group(4)))] = {
                    "cls": m.group(1), "t": float(m.group(2)), "self": m.group(5),
                    "top": m.group(7), "fires": m.group(8)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("p0_record")
    ap.add_argument("final_record")
    ap.add_argument("--final30", required=True)
    ap.add_argument("--p0", required=True)
    ap.add_argument("--final120")
    ap.add_argument("--recheck")
    a = ap.parse_args()
    pc = ab.driver_pass_classes()
    p0, fin = ab.load_record(a.p0_record), ab.load_record(a.final_record)
    f30, p0r, f120 = rows(a.final30), rows(a.p0), rows(a.final120)
    recheck = ab.load_record(a.recheck) if a.recheck else {}
    keys = sorted(k for k in p0.keys() & fin.keys() if p0[k][0] in pc and fin[k][0] not in pc)

    disp = OrderedDict()
    for k in keys:
        if k not in f30 or k not in p0r:
            disp[k] = ("unmeasured", "")
        elif f30[k]["cls"] in pc:
            disp[k] = ("noise", "")
        elif p0r[k]["cls"] not in pc:
            disp[k] = ("p0-noise", "")
        elif k in f120 and f120[k]["cls"] in pc and f120[k]["t"] <= 30:
            disp[k] = ("near-cap", "")
        elif k in f120 and f120[k]["cls"] in pc:
            disp[k] = ("slow-correct", "")
        else:
            disp[k] = ("deterministic", f"{f30[k]['cls']} top={f30[k]['top']}")

    def fmt(r):
        return f"{r['cls']} {r['t']:.1f}s top={r['top']}" if r else "-"

    print(f"=== probe 10 summary: {os.path.relpath(a.final_record, ROOT)} vs "
          f"{os.path.relpath(a.p0_record, ROOT)} ===")
    totals = Counter(v[0] for v in disp.values())
    print(f"PASS->FAIL {len(keys)}: " + ", ".join(
        f"{name} {totals.get(name, 0)}"
        for name in ("deterministic", "slow-correct", "near-cap", "noise", "p0-noise", "unmeasured")))
    groups = OrderedDict()
    for k, (name, key) in disp.items():
        groups.setdefault((name != "deterministic", name, key), []).append(k)
    for gi, ((_order, name, key), members) in enumerate(sorted(groups.items(), key=lambda kv: (kv[0][0], -len(kv[1]), kv[0][1], kv[0][2])), 1):
        print(f"\nGROUP g{gi}  {name}  {len(members)} entries" + (f"  final {key}" if key else ""))
        for k in members:
            c0, t0 = p0[k]
            c1, t1 = fin[k]
            print(f"  {k[0]} e{k[1]}  record {c0} {t0:.1f}s -> {c1} {t1:.1f}s"
                  f"  | P0 core {fmt(p0r.get(k))}  | final30 {fmt(f30.get(k))}"
                  f"  | final120 {fmt(f120.get(k))}")
            if k in p0r and k in f30:
                print(f"      fires P0: {p0r[k]['fires']}")
                print(f"      fires final: {f30[k]['fires']}  self={f30[k]['self']}")
    new_to = sorted(k for k in p0.keys() & fin.keys() if fin[k][0] == "timeout" and p0[k][0] != "timeout")
    print(f"\nNEW TIMEOUTS {len(new_to)}"
          + (": at 100 s " + ", ".join(f"{c} {n}" for c, n in sorted(Counter(
              recheck[k][0] for k in new_to if k in recheck).items())) if recheck else ""))
    for k in new_to:
        rc = f"{recheck[k][0]} {recheck[k][1]:.1f}s" if k in recheck else "-"
        print(f"  {k[0]} e{k[1]}  P0 {p0[k][0]} {p0[k][1]:.1f}s  recheck100 {rc}")
    unmeasured = totals.get("unmeasured", 0)
    print(f"Results: {len(keys) - unmeasured} passed, {unmeasured} failed")


if __name__ == "__main__":
    main()
