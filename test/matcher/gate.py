#!/usr/bin/env python3
"""test/matcher/gate.py -- the matcher regression gate (matcher substrate
spec docs/superpowers/specs/2026-09-12-matcher-substrate-design.md section 4,
P1 and P2).

Inputs (all produced by test/matcher/*.run):
  --report    the round-trip judge report (02-roundtrip.py judge, modes narrow,wide)
  --controls  CONTROL lines from test/matcher/controls.mac
  --g2        probes/matcher/02-roundtrip.out -- the 41 G-2 rules (FAILRULES guard)
  --maxima    also gate the maxima leg (P2): its completeness; MODEL-LOST reported
  --spike     SPIKE lines from test/matcher/spike01.mac (P2)

Every check prints PASS:/FAIL:; the run ends with `Results: <n> passed, <m> failed`.
"""

import argparse
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("rt02", ROOT / "probes" / "matcher" / "02-roundtrip.py")
rt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rt)

RULE_ID = re.compile(r"(\d[\d.]*\.m L\d+) \[")
H_EXPECT = {
    "H1": {"F": "F", "x": "x"}, "H2": {"u": "u", "F": "F", "x": "x"},
    "H3": {"u": "u", "x": "x"}, "H4": {"u": "u", "F": "F", "x": "x"},
    "H5": {"F": "F", "m": "m", "x": "x"}, "H6": {"u": "u", "F": "F", "m": "m", "x": "x"},
    "H7": {"n": 2, "f": "f", "x": "x"}, "H8": {"u": "u", "n": 2, "f": "f", "x": "x"},
}
# Spec section 4 P2: "no new MISS on the tree leg".  P1's floor (7444 - 9,
# sparing the 9 G-3 Complex rules) was met in full -- 7444/7444 in both modes
# at the P1 and P2 gates (test/matcher/roundtrip.out) -- so a rule losing a
# positive in either mode is a new MISS.
REQUIRED_RULES_OK = 7444


class Gate:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, name, ok, detail=""):
        if ok:
            self.passed += 1
            print("PASS: %s" % name)
        else:
            self.failed += 1
            print("FAIL: %s%s" % (name, ("\n    " + detail) if detail else ""))


def line(report, pattern):
    m = re.search(pattern, report, re.M)
    return m


def kinds(text):
    return {k: int(c) for k, c in re.findall(r"([A-Z][A-Z/-]*) (\d+)", text)}


def gate_report(g, report, g2_ids, maxima):
    m = line(report, r"^completeness: rules (\d+); missing result lines (\d+)")
    g.check("round trip complete (7444 rules, 0 missing result lines)",
            bool(m) and m.group(1) == "7444" and m.group(2) == "0", m.group(0) if m else "no completeness line")
    for mode in ("narrow", "wide"):
        m = line(report, r"^SUMMARY %s positives \(tree leg\): (\d+) -- (.*)$" % mode)
        k = kinds(m.group(2)) if m else {}
        g.check("%s: 0 UNSOUND positives (tree leg)" % mode,
                bool(m) and k.get("WRONG/UNSOUND", 0) == 0, m.group(0) if m else "no positives line")
        m = line(report, r"^UNSOUNDRULES %s \((\d+)\)" % mode)
        g.check("%s: 0 rules with an UNSOUND binding (all legs, collapsed included; G-4 closed)" % mode,
                bool(m) and m.group(1) == "0", m.group(0) if m else "no UNSOUNDRULES line")
    for mode in ("narrow", "wide"):
        m = line(report, r"^SUMMARY %s rules with every positive OK \(tree leg\): (\d+)/(\d+)" % mode)
        g.check("%s: rules with every positive OK = %d (no MISS)" % (mode, REQUIRED_RULES_OK),
                bool(m) and int(m.group(1)) == REQUIRED_RULES_OK, m.group(0) if m else "no rules-OK line")
        m = line(report, r"^SUMMARY %s mutations: .*rules with a FALSE match: (\d+)$" % mode)
        g.check("%s: 0 false mutation matches" % mode, bool(m) and m.group(1) == "0",
                m.group(0) if m else "no mutations line")
    m = line(report, r"^SUMMARY narrow collapsed witnesses .*$")
    g.check("narrow: 0 UNSOUND collapsed witnesses (tree leg)",
            bool(m) and "tree/FALSE/UNSOUND" not in m.group(0), m.group(0)[:300] if m else "no collapsed line")
    m = line(report, r"^FAILRULES narrow \((\d+)\): (.*)$")
    failing = set(RULE_ID.findall(m.group(2))) if m else None
    g.check("narrow: none of the %d G-2 rules fails" % len(g2_ids),
            failing is not None and not (failing & g2_ids),
            "still failing: %s" % sorted(failing & g2_ids) if failing else "no FAILRULES line")
    if maxima:
        for mode in ("narrow", "wide"):
            m = line(report, r"^SUMMARY %s maxima leg: (\d+) -- (.*); witnesses changed by Maxima: (\d+); "
                             r"rules with MODEL-LOST: (\d+)$" % mode)
            k = kinds(m.group(2)) if m else {}
            g.check("%s: maxima leg ran (%s variants; MODEL-LOST %s in %s rules; changed by Maxima %s)" % (
                mode, m.group(1) if m else "?", k.get("MODEL-LOST", 0), m.group(4) if m else "?",
                m.group(3) if m else "?"),
                bool(m) and int(m.group(1)) > 70000 and k.get("MAXIMA-ERROR", 0) == 0,
                m.group(0) if m else "no maxima-leg line")


def gate_controls(g, text):
    for l in text.splitlines():
        if l.startswith("CONTROL-BUILD\t"):
            print("INFO: controls build: %s" % l.split("\t", 1)[1])
    rows = [l.split("\t") for l in text.splitlines() if l.startswith("CONTROL\t")]
    g.check("controls: 12 controls x 2 modes present", len(rows) == 24, "%d CONTROL lines" % len(rows))
    for _tag, mode, cid, matched, binds, target, pattern in rows:
        B = dict(rt.parse_bindings(binds)) if matched == "T" else {}
        if cid in H_EXPECT:
            ok = matched == "T" and {k: rt.cn(v) for k, v in B.items()} == H_EXPECT[cid]
            g.check("controls %s %s: matches with the Mathematica bindings" % (mode, cid), ok,
                    "matched=%s bindings=%s" % (matched, binds))
        else:
            lhs = rt.parse_sexp(pattern)
            ok = matched == "NIL" or rt.verify_case(lhs, rt.parse_sexp(target), B, wide=(mode == "wide")) is True
            g.check("controls %s %s: no match or a verified binding" % (mode, cid), ok,
                    "matched=%s bindings=%s" % (matched, binds))


def gate_spike(g, text):
    for l in text.splitlines():
        if l.startswith("SPIKE-BUILD\t"):
            print("INFO: spike-01 build: %s" % l.split("\t", 1)[1])
    rows = [l.split("\t") for l in text.splitlines() if l.startswith("SPIKE\t")]
    g.check("spike-01: 71 cases present", len(rows) == 71, "%d SPIKE lines" % len(rows))
    for _tag, cid, group, model, ok, detail in rows:
        if model == "T":
            print("INFO: spike-01 %s (model case, not gated) ok=%s %s" % (cid, ok, detail))
            continue
        g.check("spike-01 %s [%s]" % (cid, group), ok == "T", detail)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report")
    ap.add_argument("--controls")
    ap.add_argument("--g2", default=str(ROOT / "probes" / "matcher" / "02-roundtrip.out"))
    ap.add_argument("--maxima", action="store_true")
    ap.add_argument("--spike")
    a = ap.parse_args(argv)
    g = Gate()
    g2_line = re.search(r"^FAILRULES guard \((\d+)\): (.*)$", Path(a.g2).read_text(), re.M)
    g2_ids = set(RULE_ID.findall(g2_line.group(2)))
    g.check("G-2 reference list read (41 rules)", len(g2_ids) == 41, "%d ids" % len(g2_ids))
    if a.report:
        gate_report(g, Path(a.report).read_text(), g2_ids, a.maxima)
    if a.controls:
        gate_controls(g, Path(a.controls).read_text())
    if a.spike:
        gate_spike(g, Path(a.spike).read_text())
    print("Results: %d passed, %d failed" % (g.passed, g.failed))
    return 1 if g.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
