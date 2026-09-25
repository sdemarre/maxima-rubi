#!/usr/bin/env python3
"""probes/class-ports/class1/18-attribution.py -- bucket the 534 class-1
PASS->FAIL entries of the class-ports measurement (mr-ports
test/ports_ab_class1.out: 524 new timeouts, 10 new contains-noun/unverified)
from this directory's probe outputs; prints the table (18-attribution.out).

Inputs:
  c1-pf-timeout.entries / c1-pf-answer.entries   (make_entries.py; base line + new class)
  11-timeout-ab.out    35 timeouts, ref/new/newV/refV alternating, 120 s cpu, sequential
  13-sweep-newV.out    all 524 timeouts on the new core + values_trim.lisp, 30 s cpu
  15-route2-bisect.out, 14-route5-bisect.out   overlay bisection of the non-V timeouts
  01-answer-ab.out, 08-answer-bisect.out, 10-fixE-answer.out   the 10 answer entries
Bucket rules (timeouts):
  V-noise  passes on the new core within 30 s cpu run alone (11-timeout-ab; MEASURED
           on the sample, MODELLED for the rest: base-record t x the sample's median
           new-sequential/base-record ratio <= 30 s)
  V-cost   same, > 30 s
  both are the `values` scan cost (fix V) iff the entry passes in 13-sweep-newV
  FF-*     fails or is slow in 13-sweep-newV and is restored by master FreeFactors
"""
import os, re, statistics
H = os.path.dirname(os.path.abspath(__file__))
PASS = {"verified", "expected", "no-answer"}
EN = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L\d+\s+-> (\S+) t=([\d.]+)s")
AB = re.compile(r"^(\S+)\s+(\S+)\s+t=\s*([\d.]+)s rubi=\s*\S+s (.*) e(\d+) L\d+")

def entries(p):
    return {(m.group(3), int(m.group(4))): (m.group(1), float(m.group(2)), m.group(5))
            for m in map(EN.match, open(os.path.join(H, p))) if m}

def ab(p):
    out = {}
    for l in open(os.path.join(H, p)):
        m = AB.match(l)
        if m:
            out.setdefault((m.group(4), int(m.group(5))), {})[m.group(1)] = (m.group(2), float(m.group(3)))
    return out

def short(k):
    return f"{k[0].split('/')[-1].split(' ')[0]} e{k[1]}"

tmo, ans = entries("c1-pf-timeout.entries"), entries("c1-pf-answer.entries")
sab, sweep = ab("11-timeout-ab.out"), ab("13-sweep-newV.out")
print(f"PASS->FAIL {len(tmo) + len(ans)}: new timeout {len(tmo)}, new answer-class {len(ans)}\n")

# --- sequential A/B figures
ok = [k for k in sab if all(sab[k][a][0] in PASS for a in ("ref", "new", "newV", "refV"))]
med = lambda xs: statistics.median(xs)
r_new_ref = med([sab[k]["new"][1] / sab[k]["ref"][1] for k in ok])
r_nv_rv = med([sab[k]["newV"][1] / sab[k]["refV"][1] for k in ok])
r_ref_rv = med([sab[k]["ref"][1] / sab[k]["refV"][1] for k in ok])
r_seq_rec = med([sab[k]["new"][1] / tmo[k][1] for k in ok])
print(f"sequential A/B (11-timeout-ab.out, {len(sab)} timeouts, {len(ok)} PASS in all four arms), medians:")
print(f"  new/ref {r_new_ref:.2f}   newV/refV {r_nv_rv:.2f}   ref/refV {r_ref_rv:.2f}   new(seq)/base-record {r_seq_rec:.2f}\n")

buckets = {}
def put(b, k, note=""):
    buckets.setdefault(b, []).append((k, note))

for k, (bc, bt, nc) in tmo.items():
    sw = sweep.get(k, {}).get("newV")
    if sw and sw[0] in PASS and sw[1] < 15:
        if k in sab:
            b = "V-noise (measured)" if sab[k]["new"][0] in PASS and sab[k]["new"][1] <= 30 else "V-cost (measured)"
            note = f"ref {sab[k]['ref'][1]:5.1f}s new {sab[k]['new'][1]:5.1f}s newV {sab[k]['newV'][1]:4.1f}s refV {sab[k]['refV'][1]:4.1f}s"
        else:
            pred = bt * r_seq_rec
            b = "V-noise (modelled)" if pred <= 30 else "V-cost (modelled)"
            note = f"base {bt:5.1f}s -> predicted new {pred:5.1f}s; newV {sw[1]:4.1f}s"
        put(b, k, note)
    else:
        put("FF-route/verify (timeout)", k, f"base {bt:5.1f}s; newV {sw[0] if sw else '?'} {sw[1] if sw else 0:.1f}s")

for k, (bc, bt, nc) in ans.items():
    fam = "FF-S seen-test cut on an ancestor (1.1.3.3 e271)" if k[1] == 271 else "FF-E EqQ/NeQ syntactic (fix E)"
    put(fam, k, f"new {nc}")

for b in sorted(buckets):
    print(f"{len(buckets[b]):4d}  {b}")
    for k, note in buckets[b][:12] if "modelled" in b else buckets[b]:
        print(f"        {short(k):14s} {note}")
    if "modelled" in b and len(buckets[b]) > 12:
        print(f"        ... {len(buckets[b]) - 12} more")
print()
v = sum(len(x) for b, x in buckets.items() if b.startswith("V-"))
print(f"values-scan cost (fix V) total {v}; FreeFactors-exposed (ticket 20) total {len(tmo) + len(ans) - v}")
fixE = ab("10-fixE-answer.out")
print(f"fix E recovers {sum(1 for k in fixE if fixE[k]['newE'][0] in PASS)}/{len(fixE)} answer entries (10-fixE-answer.out)")
print(f"fix V: 13-sweep-newV PASS {sum(1 for k in sweep if sweep[k]['newV'][0] in PASS)}/{len(sweep)} timeouts at 30 s cpu")
