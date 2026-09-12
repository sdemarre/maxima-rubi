#!/usr/bin/env python3
"""Probe 09 summary — join the probe-09 per-core outputs into one
per-entry attribution table (docs/corpus-class3-deferred-uplift.md §5).

For every PASS->FAIL entry of a class (the .classN.shard order):
  rec      pre-campaign record class/t -> campaign-close record class/t
  cores    the probe-09 class on each core, in campaign order:
           f8d2fde (class-1/2 record rules; classes 1-2 only), 1d998cc
           (campaign base), 464d29f B1, d6cee4e B2, 3c04b2e B4, 52ffb6f C2,
           2fd677a C1, d2ae62d C4, 1c8a306 C3, 9533528 B3, 4702d4d C5,
           c25e8f6 C6, final (99e1eb1 C6b) — letter codes below
  first    the first core (in campaign order after 1d998cc) on which the
           entry is FAIL and stays FAIL through the final core; `-` if
           the entry is PASS on the final core or never PASS on 1d998cc
  cap120   the final-core class at a 120 s cap (timeouts and unexpected
           answers whose self-check did not finish), if measured
  fires    the pass-1 fired-rule sequence on 1d998cc and on the final core
  disp     (class 3 only; record §5.5) the disposition, mechanical:
           noise         PASS on the final core (first = '-')
           near-cap(a)   bisected, but the final core's 120 s cap run is a
                         PASS class within the standard 30 s cap — the close
                         core's own runs straddle the cap
           near-cap(b)   bisected, but the pass-1 fire trace is identical on
                         the base and final cores (no campaign route change)
                         and the base run itself is >= 20 s (within 10 s of
                         the cap) — timing evidence only
           deterministic <commit>  otherwise: the bisection's first-FAIL core
Letter codes: V verified, E expected, N no-answer, U unverified,
D deferred, X unexpected, C contains-noun, T timeout, R error, . not run.
Deterministic join of committed outputs (no Maxima subprocess).

Usage: python3 probes/corpus/09-deferred-close-passfail-attribution.summary.py
Output: probes/corpus/09-deferred-close-passfail-attribution.summary.out
"""

import os
import re
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "probes", "corpus", "09-deferred-close-passfail-attribution")
OUT = P + ".summary.out"
CORES = [("basef8d2fde", "M2"), ("base1d998cc", "base"), ("464d29f", "B1"),
         ("d6cee4e", "B2"), ("3c04b2e", "B4"), ("52ffb6f", "C2"),
         ("2fd677a", "C1"), ("d2ae62d", "C4"), ("1c8a306", "C3"),
         ("9533528", "B3"), ("4702d4d", "C5"), ("c25e8f6", "C6"),
         ("final", "C6b")]
CODE = {"verified": "V", "expected": "E", "no-answer": "N",
        "unverified": "U", "deferred": "D", "unexpected": "X",
        "contains-noun": "C", "timeout": "T", "error": "R"}
PASS = {"verified", "expected", "no-answer"}
ROW = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s (.+?) e(\d+) L\d+\s+self=(\S+)"
                 r"\s+nfires=(\d+)\s+fires=(\S+)")
REC = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s (.+) e(\d+) L\d+\s*$")
SECTION = {1: "1 Algebraic functions", 2: "2 Exponentials", 3: "3 Logarithms"}


def rows(path):
    d = OrderedDict()
    if not os.path.exists(path):
        return d
    for ln in open(path, encoding="utf-8"):
        m = ROW.match(ln.rstrip("\n"))
        if m:
            d[(m.group(3), int(m.group(4)))] = dict(
                cls=m.group(1), t=float(m.group(2)), self=m.group(5),
                fires=m.group(7))
    return d


def record(path):
    d = {}
    for ln in open(path, encoding="utf-8"):
        m = REC.match(ln.rstrip("\n"))
        if m:
            d[(m.group(3), int(m.group(4)))] = (m.group(1), float(m.group(2)))
    return d


def short(rel):
    return rel.split("/")[-1].split(" ", 1)[0]


def main():
    L = ["=== probe 09 summary — per-entry PASS->FAIL attribution table ===",
         "core order: " + " ".join(f"{c}={n}" for c, n in CORES), ""]
    for k in (3, 1, 2):
        pre = record(os.path.join(ROOT, "test", f"corpus_class{k}.campaign-baseline.out"))
        fin = record(os.path.join(ROOT, "test", f"corpus_class{k}.out"))
        per = {c: rows(f"{P}.class{k}-{c}.out") for c, _n in CORES}
        cap = rows(f"{P}.class{k}-final-cap120.out")
        rck_path = os.path.join(ROOT, "test", f"corpus_class{k}.timeout-rerun2",
                                f"corpus_class{k}.timeout100s.out")
        rck = record(rck_path) if os.path.exists(rck_path) else {}
        # Class 3 is attributed by the per-commit binary search
        # (.class3-bisect.out: "<file> e<n>  step X->Y (...)" + a runs line).
        bis = {}
        bpath = f"{P}.class{k}-bisect.out"
        if os.path.exists(bpath):
            cur = None
            for ln in open(bpath, encoding="utf-8"):
                mb = re.match(r"^(\S+) e(\d+)\s+step (\S+) \(", ln)
                if mb:
                    cur = (mb.group(1), int(mb.group(2)))
                    bis[cur] = {"step": mb.group(3), "runs": ""}
                elif cur and ln.startswith("    runs "):
                    bis[cur]["runs"] = ln.strip()[5:]
        keys = list(per["final"].keys())
        L.append(f"--- class {k} ({SECTION[k]}): {len(keys)} PASS->FAIL entries ---")
        firsts = Counter()
        disps = Counter()
        for key in keys:
            traj = "".join(CODE.get(per[c][key]["cls"], "?") if key in per[c]
                           else "." for c, _n in CORES)
            first = "-"
            if per["final"][key]["cls"] not in PASS and \
                    per["base1d998cc"].get(key, {}).get("cls") in PASS:
                seq = CORES[2:]
                for i, (c, n) in enumerate(seq):
                    ok = all(key in per[cc] and per[cc][key]["cls"] not in PASS
                             for cc, _nn in seq[i:])
                    if ok:
                        first = n
                        break
            elif per["final"][key]["cls"] not in PASS:
                m2 = per["basef8d2fde"].get(key, {}).get("cls")
                first = ("milestone-3 (PASS on f8d2fde only)" if m2 in PASS
                         else "none (FAIL on every core measured)")
            bkey = (short(key[0]), key[1])
            if bkey in bis:
                first = "bisect " + bis[bkey]["step"]
            firsts[first] += 1
            c120 = (f"{cap[key]['cls']}/{cap[key]['t']:.1f}s/self={cap[key]['self']}"
                    if key in cap else "-")
            b = per["base1d998cc"].get(key, {})
            f = per["final"][key]
            disp = ""
            if k == 3:
                if bkey in bis:
                    c = cap.get(key)
                    near_a = c is not None and c["cls"] in PASS and c["t"] <= 30.0
                    near_b = b.get("fires") == f["fires"] and b.get("t", 0.0) >= 20.0
                    if near_a or near_b:
                        disp = ("near-cap(" + ("a" if near_a else "")
                                + ("b" if near_b else "") + ")")
                    else:
                        disp = "deterministic " + bis[bkey]["step"].split("->")[1]
                elif first == "-":
                    disp = "noise"
                else:
                    disp = "unclassified"
                disps[disp] += 1
            L.append(f"{short(key[0]):8s} e{key[1]:<5d} rec {pre[key][0]}/{pre[key][1]:.1f}s"
                     f" -> {fin[key][0]}/{fin[key][1]:.1f}s  cores {traj}  first={first}"
                     f"  final={f['cls']}/{f['t']:.1f}s self={f['self']}  cap120={c120}"
                     + (f"  recheck100={rck[key][0]}/{rck[key][1]:.1f}s" if key in rck else "")
                     + (f"  disp={disp}" if disp else ""))
            if bkey in bis:
                L.append(f"         bisect runs: {bis[bkey]['runs']}")
            L.append(f"         base fires: {b.get('fires', '.')}")
            L.append(f"         final fires: {f['fires']}")
        L.append(f"first-FAIL core counts: {dict(firsts)}")
        if disps:
            L.append("disposition counts: " + ", ".join(
                f"{d}: {n}" for d, n in sorted(disps.items())))
            det = sum(n for d, n in disps.items() if d.startswith("deterministic"))
            near = sum(n for d, n in disps.items() if d.startswith("near-cap"))
            L.append(f"disposition totals: deterministic {det} + near-cap {near}"
                     f" + noise {disps['noise']} + unclassified {disps['unclassified']}"
                     f" = {sum(disps.values())}")
        L.append("")
    txt = "\n".join(L) + "\n"
    open(OUT, "w", encoding="utf-8").write(txt)
    print(txt, end="")


if __name__ == "__main__":
    main()
