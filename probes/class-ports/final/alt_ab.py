#!/usr/bin/env python3
"""alt_ab.py OUT ROUNDS KEY|ARM,ARM[,..] ... -- sequential ALTERNATING timing A/B (one Maxima
process at a time, nothing else of ours running): for each entry, ROUNDS rounds, each round
every arm in the order given; `round arm class t= key` lines. Arms: fa.py arm syntax."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fa
out, rounds = sys.argv[1], int(sys.argv[2])
drivers = {}
with open(out, "a") as fh:
    fh.write("# alt_ab sequential, cap 30 s cpu\n")
    for spec in sys.argv[3:]:
        key, arms = spec.rsplit("|", 1)
        rel, n = key.rsplit(" e", 1)
        for r in range(rounds):
            for a in arms.split(";"):
                name, core, sw, pre = fa.parse_arm(a)
                if core not in drivers:
                    drivers[core] = fa.load_driver(core, 30)
                d = drivers[core]
                d.RULES_CORE = core
                saved = dict(d.SWITCH_SETTINGS); d.SWITCH_SETTINGS.update(sw)
                cls, t = fa.classify(d, rel, int(n), 30, pre)
                d.SWITCH_SETTINGS.clear(); d.SWITCH_SETTINGS.update(saved)
                fh.write(f"r{r+1} {name:8s} {cls:14s} t={t:6.1f}s {key}\n"); fh.flush()
