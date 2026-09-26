#!/usr/bin/env python3
"""probes/class-ports/15-attribution.py -- bucket the 190 class-6 PASS->FAIL
entries of the class-ports measurement (mr-ports test/ports_ab_class6.out)
from this directory's probe outputs. Writes the table to stdout
(committed as 15-attribution.out).

Inputs (all in probes/class-ports/):
  c6-pf-answer.entries / c6-pf-timeout.entries   the 93 + 97 entries (make_entries.py)
  00-noise-answer.out   the 93 answer entries re-run singly, new core, 30 s cpu
  01-timeout-ab.out               the 97 timeouts, ref then new, 120 s cpu, alternating
  06-fixAB-answer.out, 12-fixB-only-answer.out, 05-fixA-subst-rational.out,
  09-fixC-substfor-arg.out, 07-depthcap-64.out, 18-fixD-timeout.out,
  20-fixABCD-all190.out           runtime-overlay re-classifications (30 s cpu)
  16-trace-timeout-route.out      rubi-only traces of the route timeouts (new core, 60 s)
The ANSWER families are named by entry (the trace evidence is
trace-answer.out); the TIMEOUT buckets follow from 01-timeout-ab.out:
  noise  -- the new arm PASSes within 30 s cpu
  cost   -- the new arm PASSes, above 30 s cpu (ref vs new cpu listed)
  route  -- the new arm still FAILs at 120 s (timeout / error / other)
"""
import os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RES = re.compile(r"^(?:(ref|new)\s+)?(\S+)\s+t=\s*([\d.]+)s\s+(.*) e(\d+) L\d+")
PASS = {"verified", "expected", "no-answer"}


def read(path):
    out = {}
    for l in open(os.path.join(HERE, path)):
        m = RES.match(l)
        if m:
            out.setdefault((m.group(4), int(m.group(5))), {})[m.group(1) or "-"] = (
                m.group(2), float(m.group(3)))
    return out


def short(k):
    return f"{k[0].split('/')[-1].split(' ')[0]} e{k[1]}"


FAM = {
    "B  GtQ reading (Not[GtQ[a,0]] undecided) -- fix B": lambda k, f: (
        f in ("6.1.7", "6.2.7") and k[1] != 426),
    "A  ExpandIntegrand on P(x)/x -- fix A": lambda k, f: (
        (f == "6.3.7" and k[1] in (137, 147, 159)) or (f == "6.5.7" and k[1] == 105)
        or (f == "6.7.1" and k[1] in (74, 380))),
    "AB both A and B": lambda k, f: (f, k[1]) in (("6.5.3", 120), ("6.6.3", 117)),
    "C  SubstForHyperbolic EqQ -- fix C": lambda k, f: f == "6.7.1" and k[1] in (968, 969, 974, 975),
    "S  seen-test cycle 1_1_2_2 r5 <-> 1_2_3_1 r1 (pre-existing; after A)": lambda k, f: (
        (f == "6.7.1" and k[1] in (73, 76, 78, 104, 107, 109)) or (f == "6.1.7" and k[1] == 426)),
    "D  depth cap 16 (bridge ping-pong)": lambda k, f: (
        (f == "6.1.5" and k[1] in (46, 54, 152, 227)) or (f == "6.6.3" and k[1] in (36, 37, 38, 40, 41, 48))),
    "G  give-up form c*unintegrable (Rubi-faithful 4_5_10 r13 / 4_3_10 r24)": lambda k, f: (
        f in ("6.1.1", "6.3.1")),
    "W  wrong answer: bridged fractional power, Maxima radical branches (4_3_1_1)": lambda k, f: f == "6.4.2",
}


def rubi_only(path):
    """{key: 'rubi Xs len N' or 'rubi >60s'} from a trace_entry --batch file."""
    out = {}
    for b in open(os.path.join(HERE, path)).read().split("\n\n"):
        m = re.search(r"# entry (.*\.mac) e(\d+) ", b)
        if not m:
            continue
        k = ("6 Hyperbolic functions/" + m.group(1), int(m.group(2)))
        rc = re.search(r"RUBI-CPU ([\d.]+)", b); ln = re.search(r"ANSWER-LEN (\d+)", b)
        out[k] = (f"rubi {float(rc.group(1)):5.1f}s ans {int(ln.group(1)):>8d} ch" if rc and ln
                  else "rubi >60s (no answer)")
    return out


def main():
    ans = read("c6-pf-answer.entries")
    tmo = read("c6-pf-timeout.entries")
    noise = read("00-noise-answer.out")
    ab = read("01-timeout-ab.out")
    fixab = read("06-fixAB-answer.out")
    fixd = read("18-fixD-timeout.out")
    abcd = read("20-fixABCD-all190.out")
    ro = rubi_only("16-trace-timeout-route.out")
    print(f"answer entries {len(ans)}, timeout entries {len(tmo)}")
    n_noise = sum(1 for k in ans if noise.get(k, {}).get("-", ("?",))[0] in PASS)
    print(f"(a) noise among the answer entries (30 s single rerun PASSes): {n_noise}/{len(ans)}")
    print()
    print("(c) answer-entry families (93):")
    seen = set()
    for name, pred in FAM.items():
        ks = [k for k in ans if pred(k, short(k).split()[0])]
        seen.update(ks)
        rec = sum(1 for k in ks if fixab.get(k, {}).get("-", ("?",))[0] in PASS)
        rec4 = sum(1 for k in ks if abcd.get(k, {}).get("-", ("?",))[0] in PASS)
        print(f"  {len(ks):3d}  {name}   [A+B overlay PASS {rec}; A+B+C+D PASS {rec4}]")
        print("       " + " ".join(short(k) for k in sorted(ks, key=lambda k: (k[0], k[1]))))
    missing = [k for k in ans if k not in seen]
    print(f"  unassigned: {len(missing)} {' '.join(short(k) for k in missing)}")
    print()
    print("timeout entries (97), 120 s cpu alternating A/B:")
    buckets = defaultdict(list)
    for k in tmo:
        r = ab.get(k, {})
        if "new" not in r:
            buckets["not measured"].append(k); continue
        cls, t = r["new"]
        if cls in PASS:
            buckets["noise" if t <= 30.0 else "cost"].append(k)
        else:
            buckets[f"route/runaway: new {cls}"].append(k)
    for b, ks in sorted(buckets.items()):
        nd = sum(1 for k in ks if fixd.get(k, {}).get("-", ("?",))[0] in PASS)
        n4 = sum(1 for k in ks if abcd.get(k, {}).get("-", ("?",))[0] in PASS)
        print(f"  {len(ks):3d}  {b}   [D overlay PASS {nd}; A+B+C+D PASS {n4}]")
        for k in sorted(ks, key=lambda k: (k[0], k[1])):
            r = ab[k] if k in ab else {}
            ref = r.get("ref", ("-", 0)); new = r.get("new", ("-", 0))
            d = fixd.get(k, {}).get("-", ("?", 0))[0]
            print(f"       {short(k):14s} ref {ref[0]:13s} {ref[1]:6.1f}s   new {new[0]:13s} {new[1]:6.1f}s"
                  f"   D:{d:13s} {ro.get(k, '')}")
    tot = sum(1 for k in list(ans) + list(tmo) if abcd.get(k, {}).get("-", ("?",))[0] in PASS)
    print(f"\nall 190 with the A+B+C+D overlays (30 s cpu): {tot} PASS")
    fam = Counter(short(k).split()[0] for k in tmo)
    print("  per file: " + ", ".join(f"{f} {n}" for f, n in sorted(fam.items())))


if __name__ == "__main__":
    main()
