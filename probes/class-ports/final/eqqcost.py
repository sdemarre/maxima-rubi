#!/usr/bin/env python3
"""eqqcost.py KEYS OUT [OVERLAY] [-j N] -- for each entry, rubi on the final core with
ov-eqq-enter.mac (plus OVERLAY, e.g. fix-eqq-radcan.mac, loaded first) at a 30 s cap:
the number of symbolic-EqQ calls, their total and largest cpu, and whether the
run ended INSIDE one (the call it was stuck in, truncated)."""
import sys, os, re, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fa
keys = fa.keys_of(sys.argv[1]); out = sys.argv[2]
extra = [a for a in sys.argv[3:] if a.endswith(".mac")]
j = int(sys.argv[sys.argv.index("-j") + 1]) if "-j" in sys.argv else 1
d = fa.load_driver(fa.CORES['final'], 30)
pre = "".join(open(os.path.join(fa.HERE, p)).read() + "\n" for p in extra + ["ov-eqq-enter.mac"])
def one(k):
    els, _ = fa.entry_text(d, k[0], k[1])
    text = (pre + "".join(f"{a} : {b}$\n" for a, b in d.SWITCH_SETTINGS.items())
            + "display2d:false$ linel:100000$\n" + f"mr_r : rubi({d.normalize_heads(els[0])}, {els[1]})$\n"
            + 'print("DONE")$\n')
    cpu = []
    o, hit = d.maxima_run(text, 30, cpu)
    n = tot = mx = 0.0; last_in = None; stuck = False
    for l in o.splitlines():
        if l.startswith("EQQ-IN"):
            n += 1; last_in = l; stuck = True
        elif l.startswith("EQQ-OUT"):
            t = float(l.split()[1]); tot += t; mx = max(mx, t); stuck = False
    done = "DONE" in o
    s = f"calls={int(n):6d} eqq_cpu={tot:6.2f}s max={mx:6.2f}s run_cpu={cpu[0] if cpu else -1:6.1f}s done={done} stuck={stuck and not done}"
    if stuck and not done: s += " IN: " + last_in[:300]
    return f"{s}  {k[0]} e{k[1]}\n"
with open(out, "a") as fh, cf.ThreadPoolExecutor(j) as ex:
    fh.write(f"# eqqcost overlays {extra} cap 30\n")
    for line in ex.map(one, keys):
        fh.write(line); fh.flush()
