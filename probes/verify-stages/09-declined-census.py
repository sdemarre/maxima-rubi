#!/usr/bin/env python3
"""probes/verify-stages/09-declined-census.py -- why does the checker's
numeric check decline? (.scratch/corpus-harness/issues/06 item 2)

The entries: every `none/numeric-declined*` proof tag of probe 08's arm B
(rectform last = the checker's order since ac2fad6), unverified set. For
each, a STATIC reading of the corpus entry (integrand and corpus answer,
no rubi run): the identifiers left free after mr_numeric_subs and the
integration variable, and the function heads. The rubi answer is not
read, so a symbol only rubi's answer carries is missed; that is the
census's known blind spot.
"""
import collections, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "test"))
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
SUBS = set("a b c d e f g h A B C D p".split())
CONST = {"%pi", "%e", "%i", "inf", "minf", "und", "true", "false"}

tags = {}
for p in glob.glob(os.path.join(HERE, "08-stage-order", "armB", "unverified", "class*", "shard*.proof")):
    for l in open(p, encoding="utf-8"):
        t, rest = l.rstrip("\n").split(" ", 1)
        m = re.match(r"(.*) e(\d+) L(\d+)$", rest)
        if t.startswith("none/numeric-declined"):
            tags[(m.group(1), int(m.group(2)))] = (t, int(m.group(3)))

cache = {}
def entry(rel, line):
    if rel not in cache:
        cache[rel] = open(os.path.join(SUITE, rel), encoding="utf-8").read().splitlines()
    return cache[rel][line - 1]

IDENT = re.compile(r"%?[A-Za-z_][A-Za-z_0-9]*")
free_c, head_c, why_c, fam = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
rows = []
for (rel, e), (t, line) in sorted(tags.items()):
    text = entry(rel, line)
    m = re.match(r"\s*\[(.*?),\s*([a-z]+),\s*-?\d+,(.*)\]\s*,?\$?$", text)
    var = m.group(2) if m else "x"
    heads, free = set(), set()
    for mm in IDENT.finditer(text):
        w = mm.group(0)
        nxt = text[mm.end():mm.end() + 1]
        if nxt in "([":
            heads.add(w)
        elif w != var and w not in SUBS and w not in CONST:
            free.add(w)
    special = {h for h in heads if h.lower() in (
        "appellf1", "hypergeometric", "hypergeometric_regularized", "gamma_incomplete",
        "gamma_incomplete_regularized", "expintegral_ei", "expintegral_e", "expintegral_e1",
        "expintegral_si", "expintegral_ci", "expintegral_shi", "expintegral_chi",
        "fresnel_s", "fresnel_c", "erf", "erfi", "erfc", "li", "elliptic_f", "elliptic_e",
        "elliptic_pi", "polylog", "zeta", "psi", "beta_incomplete", "gamma", "lambert_w",
        "bessel_j", "bessel_y", "bessel_i", "bessel_k", "sinint", "cosint", "int", "integrate")}
    for s in free: free_c[s] += 1
    for h in heads: head_c[h] += 1
    why = ("free " + ",".join(sorted(free))) if free else (
          "special " + ",".join(sorted(special)) if special else "neither")
    why_c["free symbol" if free else ("special head only" if special else "neither")] += 1
    fam[rel.split("/")[-1][:40]] += 1
    rows.append(f"{t[:48]:48} {why[:40]:40} {rel} e{e}")

print(f"declined entries: {len(tags)}")
print("== reason (static): free symbol beats special head")
for k, v in why_c.most_common(): print(f"  {v:>5} {k}")
print("== free symbols (entries carrying each)")
for k, v in free_c.most_common(25): print(f"  {v:>5} {k}")
print("== function heads (entries carrying each), top 40")
for k, v in head_c.most_common(40): print(f"  {v:>5} {k}")
print("== files, top 25")
for k, v in fam.most_common(25): print(f"  {v:>5} {k}")
print("== per entry")
print("\n".join(rows))
