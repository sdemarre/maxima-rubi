#!/usr/bin/env python3
"""Summarize trace_entry.py --batch output: one line per (entry, core):
core tag, cpu, hit_cap, answer shape (noun?), and the firing chain TOP-DOWN
(reverse of print order; a nested dispatch prints before its parent), as
key:rN tokens. --giveups also lists the firings of the named give-up rules
with their integrands."""
import re, sys
blocks = open(sys.argv[1]).read().split("\n\n")
gu = set(a for a in sys.argv[2:] if not a.startswith("--"))
for b in blocks:
    ls = [l for l in b.splitlines() if l.strip()]
    if not ls or not ls[0].startswith("# entry"):
        continue
    m = re.match(r"# entry (\S+) .*\.mac e(\d+)", ls[0])
    fam = ls[0].split("/")[1].split(" ")[0] if "/" in ls[0] else "?"
    core = "base" if "mr-attr-base" in ls[1] else "new "
    cpu = re.search(r"cpu \[([\d.]+)\]", ls[1]); hit = "HIT" if "hit_cap True" in ls[1] else ""
    fired = [l.split()[1] + ":" + l.split()[2] for l in ls if l.startswith("fired")]
    ans = [l for l in ls if l.startswith("ANSWER ")]
    ln = [l.split()[1] for l in ls if l.startswith("ANSWER-LEN")]
    rc = [l.split()[1] for l in ls if l.startswith("RUBI-CPU")]
    shape = "none" if not ans else ("UNINT" if "unintegrable" in ans[0] else "ok")
    chain = " ".join(reversed(fired))
    extra = f"rubi {float(rc[0]):6.1f}s len {ln[0]:>7s} " if rc and ln else ""
    print(f"{fam:7s} e{m.group(2):<5s} {core} {float(cpu.group(1)) if cpu else -1:6.1f}s {hit:3s} {shape:5s} {extra}{chain[:400]}")
    if "--giveups" in sys.argv:
        for l in ls:
            if l.startswith("fired") and l.split()[1] + ":" + l.split()[2] in gu:
                print("      GIVEUP", l[:250])
