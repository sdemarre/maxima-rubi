#!/usr/bin/env python3
"""diag.py OVERLAY REL N [CAP] [switch=v ..] -- run rubi on one entry on the final core with a
diagnostic overlay; print the overlay's EQQ/diagnostic lines (last 40)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fa
ov, rel, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
cap = int(sys.argv[4]) if len(sys.argv) > 4 else 20
core = fa.CORES['final']
sw = {}
for a in sys.argv[5:]:
    if a.startswith("core="): core = fa.CORES.get(a[5:], a[5:])
    else:
        k, v = a.split("="); sw[k] = v
d = fa.load_driver(core, cap)
d.SWITCH_SETTINGS.update(sw)
els, _ = fa.entry_text(d, rel, n)
pre = open(os.path.join(fa.HERE, ov)).read() if ov != "-" else ""
text = (pre + "".join(f"{k} : {v}$\n" for k, v in d.SWITCH_SETTINGS.items())
        + "display2d:false$ linel:100000$\n" + f"mr_r : rubi({d.normalize_heads(els[0])}, {els[1]})$\n"
        + 'print("DONE", slength(string(mr_r)))$\n')
cpu = []
out, hit = d.maxima_run(text, cap, cpu)
print("hit", hit, "cpu", cpu)
ls = [l[:700] for l in out.splitlines() if l.startswith(("EQQ", "DIAG", "DONE")) or "rror" in l]
print("\n".join(ls[-40:]))
print("n-lines", len(ls))
