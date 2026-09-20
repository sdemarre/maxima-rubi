#!/usr/bin/env python3
"""probes/matcher/15-collapse-exact.py -- the 9.1 collapse family's entries
on one rules core (matcher translation fixes design section 3.3/3.5): the
entries the P5 acceptance stop traced to the ratsimp seen comparison of the
regenerated 9.1 rules (2.1 e15, 1.2.1.2 e1734-e1736, 1.2.1.4 e810) and the
origin of the exact comparison (1.2.1.3 e839).

Each entry runs through the corpus driver's EXACT per-entry text
(test/corpus_driver.py build_text) with `rubi_verbose : true$` prepended
(probe 10's method), on the core the driver resolves -- MR_RULES_CORE_PATH
pins one. Output: the class, the wall, the fire trace and its top rule.

Records (repo root):
  MR_RULES_CORE_PATH=<P0 worktree>/test/mr_rules.core \\
    python3 probes/matcher/15-collapse-exact.py > probes/matcher/15-collapse-exact.p0.out
  MR_RULES_CORE_PATH=<unfixed worktree>/test/mr_rules.core \\
    python3 probes/matcher/15-collapse-exact.py > probes/matcher/15-collapse-exact.red.out
  python3 probes/matcher/15-collapse-exact.py > probes/matcher/15-collapse-exact.out
"""

import importlib.util
import os
import re
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
CAP = 30
ENTRIES = [
    ("2 Exponentials", "2.1 u (F^(c (a+b x)))^n.mac", 15),
    ("1 Algebraic functions", "1.2 Trinomial products/1.2.1 Quadratic/1.2.1.2 (d+e x)^m (a+b x+c x^2)^p.mac", 1734),
    ("1 Algebraic functions", "1.2 Trinomial products/1.2.1 Quadratic/1.2.1.2 (d+e x)^m (a+b x+c x^2)^p.mac", 1735),
    ("1 Algebraic functions", "1.2 Trinomial products/1.2.1 Quadratic/1.2.1.2 (d+e x)^m (a+b x+c x^2)^p.mac", 1736),
    ("1 Algebraic functions", "1.2 Trinomial products/1.2.1 Quadratic/1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p.mac", 810),
    ("1 Algebraic functions", "1.2 Trinomial products/1.2.1 Quadratic/1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p.mac", 839),
]
FIRE_RX = re.compile(r"rubi: rule\s+(\S+)(?:\s+(r\d+))?\s+fired on")


def driver(section):
    path = os.path.join(ROOT, "test", "corpus_driver.py")
    sys.argv = [path, section + "/", "999999", str(CAP), "reference/maxima-syntax-test-suite"]
    spec = importlib.util.spec_from_file_location("corpus_driver_" + section.split()[0], path)
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    assert d.USE_RULES_CORE, "no rules core in use (build one: sh test/build_rules_core.sh)"
    return d


def rule_name(m):
    return f"{m.group(1)}_{m.group(2)}" if m.group(2) else re.sub(r"^_mr_rule_", "", m.group(1))


def main():
    drivers = {}
    lines, passed = [], 0
    for section, rel, e in ENTRIES:
        d = drivers.get(section) or drivers.setdefault(section, driver(section))
        path = os.path.join(ROOT, "reference", "maxima-syntax-test-suite", section, rel)
        entries, line_nos = d.extract_entries(path)
        els = d.split_elements(entries[e - 1][1:-1])
        f_text, var_text, e_text = d.normalize_heads(els[0]), els[1], d.normalize_heads(els[3])
        e_text2 = d.normalize_heads(els[4]) if len(els) == 5 else None
        text = "rubi_verbose : true$\n" + d.build_text(f_text, var_text, e_text, e_text2)
        ts = time.time()
        out, timed_out = d.maxima_run(text, CAP)
        dt = time.time() - ts
        cls = next((s.strip()[6:].strip() for s in out.splitlines() if s.strip().startswith("CLASS ")), None)
        if cls is None:
            cls = "timeout" if timed_out else "error"
        fires = [rule_name(m) for m in FIRE_RX.finditer(out)]
        passed += cls in d.PASS_CLASSES
        lines.append(f"{cls:12s} t={dt:5.1f}s {section[0]}:{rel.split('/')[-1][:8]} e{e} L{line_nos[e - 1]}"
                     f"  nfires={len(fires)} top={fires[-1] if fires else '-'} fires={','.join(fires) or '-'}")
    d0 = next(iter(drivers.values()))
    stamp = open(d0.RULES_CORE_STAMP).read().split("\n")
    fp = next((s.split()[1] for s in stamp if s.startswith("fingerprint ")), "?")
    print("=== probes/matcher/15-collapse-exact  %s" % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    r = d0.subprocess.run(["maxima", "--very-quiet", "--batch-string", "disp(build_info());"],
                          capture_output=True, text=True, timeout=120)
    print("\n".join(f"maxima: {s.strip()}" for s in r.stdout.splitlines()
                    if s.strip().startswith(("Maxima", "Lisp "))))
    print(f"core: {d0.RULES_CORE}  fingerprint {fp}")
    print("\n".join(lines))
    print(f"Results: {passed} passed, {len(lines) - passed} failed")


if __name__ == "__main__":
    main()
