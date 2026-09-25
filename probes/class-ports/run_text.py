#!/usr/bin/env python3
"""probes/class-ports/run_text.py CORE CAP FILE.mac -- run a Maxima batch
text on CORE through the corpus driver's maxima_run (cpu cap helper, stdin
/dev/null, process-group kill); the driver's switch settings are prepended.
Prints the output."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trace_entry import load_driver
core, cap, path = os.path.abspath(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
d = load_driver(cap)
d.RULES_CORE = core
switches = "".join(f"{k} : {v}$\n" for k, v in d.SWITCH_SETTINGS.items())
text = switches + "display2d : false$\nlinel : 100000$\n" + open(path).read() + "\n" + "pos$\n" * 40 + "no$\n" * 20
cpu = []
out, hit = d.maxima_run(text, cap, cpu)
print(f"# core {core} cap {cap} hit_cap {hit} cpu {cpu}")
print(out)
