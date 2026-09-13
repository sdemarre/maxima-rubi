#!/usr/bin/env python3
"""The P5 record gates and the per-switch winner rule (matcher substrate
spec docs/superpowers/specs/2026-09-12-matcher-substrate-design.md
section 4 P5).

gate P0_RECORD NEW_RECORD
    One class. Judged (PASS:/FAIL: lines and a Results: line):
      complete      the two records cover the same entries;
      switches      NEW states its arm on the filter: line;
      pass floor    NEW's PASS count >= P0's;
      wall ceiling  NEW's median per-entry wall <= P0's: the median of
                    the t= field over every entry (test/record_medians.py
                    prints the same figure to 0.1 s).
    Reported for the human gates (INFO: lines): the PASS->FAIL and
    FAIL->PASS counts (test/ab_records.py P0 NEW lists every entry; each
    PASS->FAIL is attributed and accepted by the user), the p90 wall, the
    timeout class P0 -> NEW with every entry that is timeout in NEW only,
    and the crash verdict (`error`: the subprocess died before its CLASS
    line) P0 -> NEW with every entry that is error in NEW only.

winner SWITCH BASE1 BASE2 BASE3 FLIP1 FLIP2 FLIP3
    The spec's rule for one switch, over the class 1, 2, 3 records of
    run 1 (BASE) and of the run that flips SWITCH (FLIP): the arm with
    more PASS in every class wins; on a tie or a split across classes
    mr_flat_wide and mr_cond_retry keep their documented defaults
    (false, true) and mr_model_flags takes Maxima's defaults (false).
    The two record sets must each state one arm, differing in SWITCH
    only.

Usage:  python3 test/p5_gate.py gate P0_RECORD NEW_RECORD
        python3 test/p5_gate.py winner SWITCH BASE1 BASE2 BASE3 FLIP1 FLIP2 FLIP3
"""

import importlib.util
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _module(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ab = _module("ab_records")
rr = _module("run_records")

TIE_VALUE = {"mr_flat_wide": "false", "mr_cond_retry": "true", "mr_model_flags": "false"}


def winning_value(switch, base_value, flip_value, base_pass, flip_pass):
    """(value, reason) for SWITCH given per-class PASS counts of both arms."""
    pairs = list(zip(base_pass, flip_pass))
    if pairs and all(f > b for b, f in pairs):
        return flip_value, "more PASS in every class"
    if pairs and all(b > f for b, f in pairs):
        return base_value, "more PASS in every class"
    return TIE_VALUE[switch], "tie or split across classes"


def summarize(rec, pass_classes):
    times = sorted(t for _cls, t in rec.values())
    n = len(times)
    return {"pass": sum(1 for cls, _t in rec.values() if cls in pass_classes),
            "median": statistics.median(times) if n else 0.0,
            "p90": times[min(n - 1, int(0.9 * n))] if n else 0.0}


def _new_in(cls, base, new):
    return sorted(k for k, (c, _t) in new.items()
                  if c == cls and k in base and base[k][0] != cls)


def gate(p0_path, new_path):
    pass_classes = ab.driver_pass_classes()
    p0, new = ab.load_record(p0_path), ab.load_record(new_path)
    r = ab.compare(p0, new, pass_classes)
    s0, s1 = summarize(p0, pass_classes), summarize(new, pass_classes)
    sw = rr.record_switches(new_path)
    print(f"P0:  {p0_path}")
    print(f"new: {new_path}")
    checks = [
        (f"complete: same entries (missing {len(r['missing'])}, extra {len(r['extra'])})",
         not r["missing"] and not r["extra"]),
        (f"switches: {sw}", sw is not None),
        (f"pass floor: PASS {s1['pass']} >= P0 {s0['pass']}", s1["pass"] >= s0["pass"]),
        (f"wall ceiling: median {s1['median']:.2f} s <= P0 {s0['median']:.2f} s",
         s1["median"] <= s0["median"]),
    ]
    for label, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}: {label}")
    print(f"INFO: PASS->FAIL {r['table']['PASS->FAIL']}  FAIL->PASS {r['table']['FAIL->PASS']}")
    print(f"INFO: p90 wall P0 {s0['p90']:.1f} s -> new {s1['p90']:.1f} s")
    for cls, label in (("timeout", "timeout"), ("error", "crash (error)")):
        n0 = sum(1 for c, _t in p0.values() if c == cls)
        n1 = sum(1 for c, _t in new.values() if c == cls)
        fresh = _new_in(cls, p0, new)
        print(f"INFO: {label} P0 {n0} -> new {n1}; {cls} in new only: {len(fresh)}")
        for key in fresh:
            print(f"INFO:   {p0[key][0]:<13} t={p0[key][1]:.1f}s -> {cls} t={new[key][1]:.1f}s "
                  f"{key[0]} e{key[1]}")
    failed = sum(1 for _l, ok in checks if not ok)
    print(f"Results: {len(checks) - failed} passed, {failed} failed")
    return 1 if failed else 0


def _arm(paths):
    texts = {rr.record_switches(p) for p in paths}
    if None in texts or len(texts) != 1:
        raise SystemExit(f"records do not state one arm: {sorted(map(str, texts))}")
    return dict(item.split("=") for item in texts.pop().split())


def winner(switch, base_paths, flip_paths):
    if switch not in rr.SWITCHES:
        raise SystemExit(f"unknown switch {switch!r}")
    base, flip = _arm(base_paths), _arm(flip_paths)
    differ = sorted(s for s in rr.SWITCHES if base[s] != flip[s])
    if differ != [switch]:
        raise SystemExit(f"the arms differ in {differ}, not in [{switch!r}] only")
    pass_classes = ab.driver_pass_classes()
    base_pass = [summarize(ab.load_record(p), pass_classes)["pass"] for p in base_paths]
    flip_pass = [summarize(ab.load_record(p), pass_classes)["pass"] for p in flip_paths]
    for bp, fp, b, f in zip(base_paths, flip_paths, base_pass, flip_pass):
        print(f"{switch}={base[switch]} PASS {b:6d} ({bp})  |  "
              f"{switch}={flip[switch]} PASS {f:6d} ({fp})")
    value, why = winning_value(switch, base[switch], flip[switch], base_pass, flip_pass)
    same = "same as" if value == base[switch] else "differs from"
    print(f"WINNER {switch}={value} ({why}); {same} run 1 ({switch}={base[switch]})")
    return 0


def main(argv):
    if len(argv) == 3 and argv[0] == "gate":
        return gate(argv[1], argv[2])
    if len(argv) == 8 and argv[0] == "winner":
        return winner(argv[1], argv[2:5], argv[5:8])
    print(__doc__.strip().splitlines()[-2], file=sys.stderr)
    print(__doc__.strip().splitlines()[-1], file=sys.stderr)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
