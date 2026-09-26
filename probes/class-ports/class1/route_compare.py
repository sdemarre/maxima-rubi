#!/usr/bin/env python3
"""probes/class-ports/class1/route_compare.py TRACE -- for a c1.py trace file
with two arms per entry (A then B), report per entry whether the rule-firing
sequences (key rN, integrand) are identical, and the first divergence."""
import re, sys
blocks = open(sys.argv[1]).read().split("## arm ")[1:]
same = diff = 0
for a, b in zip(blocks[0::2], blocks[1::2]):
    ent = re.search(r"# entry (.*) e(\d+) ", a)
    fa = [l for l in a.splitlines() if l.startswith("fired")]
    fb = [l for l in b.splitlines() if l.startswith("fired")]
    if fa == fb:
        same += 1; print(f"SAME  {len(fa):4d} firings  {ent.group(1).split('/')[-1][:10]} e{ent.group(2)}")
    else:
        diff += 1
        i = next((i for i, (x, y) in enumerate(zip(fa, fb)) if x != y), min(len(fa), len(fb)))
        print(f"DIFF  at firing {i} of {len(fa)}/{len(fb)}  {ent.group(1).split('/')[-1][:10]} e{ent.group(2)}")
print(f"same {same} diff {diff}")
