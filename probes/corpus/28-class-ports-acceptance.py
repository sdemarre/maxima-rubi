#!/usr/bin/env python3
"""The Step-10 acceptance figures of the class 8/5/7/4 ports
(docs/corpus-class{8,5,7,4}-baseline-uplift.md), read from the committed
records only -- no Maxima:

  test/corpus_class<N>.final.out          the package record (core 89bec424)
  test/corpus_class<N>.baseline.out       the native-integrate baseline
  test/corpus_class<N>.ports.out          the pre-fix package record (core 4daae7ac)
  test/corpus_class<N>.final.timeout-rerun/corpus_class<N>.final.timeout100s.out
                                          the 100 s re-check of the record's timeouts

and the corpus files under reference/maxima-syntax-test-suite (the entry's
integrand and expected answer, located by the record's L<line>).

  python3 probes/corpus/28-class-ports-acceptance.py [8 5 7 4]

Per class: the verdict histograms, both A/Bs (test/ab_records.py's own
load_record/compare, so the tables agree with its output), the per-file
table, the 100 s re-check transitions, the residue -> expected-head census
(heads searched in the corpus's EXPECTED text, spelled as the corpus spells
them, counted once per entry), the Rubi-marker split (expected answer IS a
top-level Unintegrable/CannotIntegrate vs CARRIES one inside a partial
answer), and sample FAIL entries of the largest FAIL files.
"""

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "test"))
from ab_records import compare, driver_pass_classes, load_record  # noqa: E402

PASS = driver_pass_classes(str(ROOT / "test" / "corpus_driver.py"))
SUITE = ROOT / "reference" / "maxima-syntax-test-suite"
RESULT = re.compile(r"^(\S+)\s+t=\s*([\d.]+)s (.+?\.mac) e(\d+) L(\d+)")
HEADS = ["polylog(", "AppellF1(", "Zeta(", "Unintegrable(", "CannotIntegrate(",
         "elliptic_f(", "elliptic_e(", "elliptic_pi(", "hypergeometric(",
         "HypergeometricPFQ(", "Hypergeometric2F1(", "GAMMA(", "Ei(", "Si(",
         "Ci(", "Shi(", "Chi(", "FresnelS(", "FresnelC(", "erf(", "erfi(",
         "ProductLog(", "Derivative(", "HurwitzLerchPhi(", "Psi(", "lnGAMMA("]
ALL_CLASS_HEADS = ["AppellF1(", "polylog(", "Zeta(", "Derivative(", "HurwitzLerchPhi("]
MARKER = re.compile(r"(?<![A-Za-z_])(Unintegrable|CannotIntegrate)\(")
SECTIONS = {"8": "8 Special functions", "5": "5 Inverse trig functions",
            "7": "7 Inverse hyperbolic functions", "4": "4 Trig functions"}

_cache = {}


def corpus_line(rel, line):
    if rel not in _cache:
        _cache[rel] = (SUITE / rel).read_text(encoding="utf-8").split("\n")
    return _cache[rel][line - 1]


def split_entry(s):
    """The top-level fields of one `[integrand, x, steps, expected]` entry."""
    s = s.strip()
    depth = 0
    for i, ch in enumerate(s):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                break
    body, out, cur, depth = s[1:i], [], "", 0
    for ch in body:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def lines_of(path):
    """{(rel, entry): (class, t, L)} -- load_record plus the L<line> field."""
    rec = {}
    for ln in open(path, encoding="utf-8"):
        m = RESULT.match(ln)
        if m:
            rec[(m.group(3), int(m.group(4)))] = (m.group(1), float(m.group(2)),
                                                  int(m.group(5)))
    return rec


def has_head(h, text):
    return re.search(r"(?<![A-Za-z_])" + re.escape(h), text) is not None


def pct(a, b):
    return f"{100 * a / b:5.1f} %" if b else "  -  "


def hist_block(name, rec):
    h = Counter(v[0] for v in rec.values())
    n = len(rec)
    ps = sum(v for k, v in h.items() if k in PASS)
    print(f"  {name}: {n} entries, PASS {ps} ({pct(ps, n).strip()}), FAIL {n - ps}")
    for c, v in h.most_common():
        print(f"      {c:<14} {v:6d}  {pct(v, n)}  {'PASS' if c in PASS else 'FAIL'}")
    return ps


def ab_block(name, a, b):
    c = compare(a, b, PASS)
    print(f"  {name}: missing {len(c['missing'])} extra {len(c['extra'])}")
    for k in ("PASS->PASS", "PASS->FAIL", "FAIL->PASS", "FAIL->FAIL"):
        print(f"      {k:<11} {c['table'][k]:6d}")
    print("      class transitions (changed only):")
    for (x, y), v in c["classes"].most_common():
        print(f"      {v:6d}  {x} -> {y}")


def run(n):
    sec = SECTIONS[n]
    t = ROOT / "test"
    fin_path = t / f"corpus_class{n}.final.out"
    fin = load_record(str(fin_path))
    base = load_record(str(t / f"corpus_class{n}.baseline.out"))
    pre = load_record(str(t / f"corpus_class{n}.ports.out"))
    rr_path = (t / f"corpus_class{n}.final.timeout-rerun"
               / f"corpus_class{n}.final.timeout100s.out")
    rr = load_record(str(rr_path))
    full = lines_of(fin_path)
    print(f"\n######## class {n}: {sec}\n")
    print("== verdict histograms")
    hist_block("final package  (corpus_class%s.final.out)" % n, fin)
    hist_block("baseline       (corpus_class%s.baseline.out)" % n, base)
    hist_block("pre-fix package (corpus_class%s.ports.out)" % n, pre)
    tf = sorted(v[1] for v in fin.values())
    tp = sorted(v[1] for v in pre.values())
    print(f"  cpu seconds, sum of t= over the record: final {sum(tf):.0f}, "
          f"pre-fix {sum(tp):.0f}; median final {tf[len(tf) // 2]:.1f}, "
          f"pre-fix {tp[len(tp) // 2]:.1f}")

    print("\n== A/B")
    ab_block("baseline -> final", base, fin)
    ab_block("pre-fix -> final", pre, fin)

    print("\n== per file: N | PASS baseline | PASS pre-fix | PASS final | FAIL final by class")
    for f in sorted({k[0] for k in fin}):
        ks = [k for k in fin if k[0] == f]
        pb = sum(base[k][0] in PASS for k in ks)
        pp = sum(pre[k][0] in PASS for k in ks)
        pf = sum(fin[k][0] in PASS for k in ks)
        fc = Counter(fin[k][0] for k in ks if fin[k][0] not in PASS)
        short = f.split("/")[-1][:-4]
        print(f"  {short:<62} {len(ks):5d} | {pb:5d} | {pp:5d} | {pf:5d} | "
              + " ".join(f"{c} {v}" for c, v in fc.most_common()))

    print("\n== 100 s timeout re-check (%s)" % rr_path.relative_to(ROOT))
    nt = sum(1 for v in fin.values() if v[0] == "timeout")
    print(f"  record timeouts {nt}; re-checked {len(rr)}; "
          f"keys equal: {set(rr) == {k for k, v in fin.items() if v[0] == 'timeout'}}")
    h = Counter(v[0] for v in rr.values())
    for c, v in h.most_common():
        print(f"      {c:<14} {v:5d}  {'PASS' if c in PASS else 'FAIL'}")
    now = sum(v for c, v in h.items() if c in PASS)
    print(f"  now-PASS at 100 s: {now}; PASS at a 100 s cap would be "
          f"{sum(v[0] in PASS for v in fin.values()) + now} / {len(fin)}")
    still = Counter(k[0].split("/")[-1][:-4] for k, v in rr.items() if v[0] == "timeout")
    print("  still timeout at 100 s, by file:")
    for f, v in still.most_common():
        print(f"      {v:4d}  {f}")

    print("\n== residue -> expected-head census (entries whose EXPECTED text carries the head)")
    tot, fail, fcls = Counter(), Counter(), defaultdict(Counter)
    allc = defaultdict(Counter)
    marker = {"top": Counter(), "interior": Counter()}
    interior_cn_files = Counter()
    for k, (c, _t, ln) in full.items():
        exp = split_entry(corpus_line(k[0], ln))[3].strip()
        for hd in HEADS:
            if has_head(hd, exp):
                tot[hd] += 1
                if c not in PASS:
                    fail[hd] += 1
                    fcls[hd][c] += 1
        for hd in ALL_CLASS_HEADS:
            if has_head(hd, exp):
                allc[hd][c] += 1
        if exp.startswith(("Unintegrable", "CannotIntegrate")):
            marker["top"][c] += 1
        elif MARKER.search(exp):
            marker["interior"][c] += 1
            if c == "contains-noun":
                interior_cn_files[k[0].split("/")[-1][:-4]] += 1
    print(f"  {'head':<20} {'entries':>7} {'inFAIL':>6} {'FAIL %':>7}  FAIL classes")
    for hd, v in tot.most_common():
        print(f"  {hd:<20} {v:7d} {fail[hd]:6d} {pct(fail[hd], v)}  "
              + " ".join(f"{c} {x}" for c, x in fcls[hd].most_common()))
    print("  every class, the ceiling heads:")
    for hd, c in allc.items():
        print(f"      {hd:<18} " + " ".join(f"{x} {v}" for x, v in c.most_common()))

    print("\n== Rubi markers in the expected answer")
    for kind, label in (("top", "IS a top-level Unintegrable/CannotIntegrate"),
                        ("interior", "CARRIES one inside a partial answer")):
        c = marker[kind]
        print(f"  {label}: {sum(c.values())} entries -- "
              + " ".join(f"{x} {v}" for x, v in c.most_common()))
    cn = sum(1 for v in fin.values() if v[0] == "contains-noun")
    print(f"  contains-noun in the record: {cn}; of them with an interior marker "
          f"in the expected answer: {marker['interior']['contains-noun']}")
    for f, v in interior_cn_files.most_common(8):
        print(f"      {v:4d}  {f}")

    print("\n== sample FAIL entries, the eight largest FAIL files (<= 2 per FAIL class)")
    per = Counter(k[0] for k, v in full.items() if v[0] not in PASS)
    for f, nf in per.most_common(8):
        print(f"  -- {f.split('/')[-1][:-4]}  (FAIL {nf})")
        byc = defaultdict(list)
        for k in sorted((k for k in full if k[0] == f and full[k][0] not in PASS),
                        key=lambda k: k[1]):
            byc[full[k][0]].append(k)
        for c, ks in sorted(byc.items(), key=lambda kv: -len(kv[1])):
            step = max(1, len(ks) // 2)
            for k in ks[::step][:2]:
                fields = split_entry(corpus_line(k[0], full[k][2]))
                print(f"     {c:<13} t={full[k][1]:5.1f}s e{k[1]:<5} {fields[0][:70]}"
                      f"   | expected: {fields[3].strip()[:50]}")


def main(argv):
    classes = argv or ["8", "5", "7", "4"]
    print("class-ports Step-10 acceptance figures (probes/corpus/28-class-ports-acceptance.py)")
    print("PASS classes (test/corpus_driver.py):", sorted(PASS))
    for n in classes:
        run(n)


if __name__ == "__main__":
    main(sys.argv[1:])
