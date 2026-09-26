#!/usr/bin/env python3
"""matrix.py -- one row per loss: record classes (base/prefix/final) and every
rerun arm's verdict (P/F + t); prints the table."""
import re, sys, os
H = os.path.dirname(os.path.abspath(__file__))
P = {"verified", "expected", "no-answer", "unexpected"}
def rd(p):
    d = {}
    if not os.path.exists(p): return d
    for l in open(p):
        if l.startswith('#'): continue
        m = re.match(r"(\S+)\s+(\S+)\s+t=\s*([\d.-]+)s (.*)$", l.rstrip())
        if m: d[m.group(4)] = (m.group(2), float(m.group(3)))
    return d
def losses():
    rows = []
    for l in open(os.path.join(H, "losses.tsv")):
        if l.startswith('#'): continue
        c, b, bt, p, pt, f, ft, k = l.rstrip("\n").split("\t")
        rows.append(dict(cls=int(c), base=b, bt=float(bt), pre=p, pt=float(pt), fin=f, ft=float(ft), key=k))
    return rows
ARMS = sys.argv[1:] or ["01-noise-final.out", "02-arm-eqqF.out", "02-arm-substT.out",
                        "02-arm-depth16.out", "02-arm-gtqIs.out", "02-arm-prefix.out"]
def main():
    A = [(os.path.basename(a), rd(os.path.join(H, a))) for a in ARMS]
    for r in losses():
        cells = []
        for n, d in A:
            v = d.get(r["key"])
            cells.append("   ---   " if v is None else f"{'P' if v[0] in P else 'F'}{v[0][:4]}{v[1]:5.1f}")
        print(f"{r['cls']} {r['base'][:4]}{r['bt']:5.1f} {r['pre'][:4]}{r['pt']:5.1f} {r['fin'][:4]}{r['ft']:5.1f} | "
              + " ".join(cells) + " | " + r["key"][-60:])
if __name__ == "__main__":
    main()
