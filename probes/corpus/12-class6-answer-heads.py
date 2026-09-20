#!/usr/bin/env python3
"""Class-6 corpus answer-head census: which heads the 6 Hyperbolic
functions section carries in its expected answers, with arity, so the
driver's answer normalization (test/corpus_driver.py HEAD_REWRITES) is
built from measured need.

Two passes, because class 6 is the first section whose head set was not
known in advance:
  (a) the curated pass — the class-2/3 HEADS/NATS lists, kept so an
      absence stays on the record;
  (b) the DISCOVERY pass — every `name(` call head on an entry line,
      split into heads Maxima has natively (NATIVE, from the installed
      build's own list, recorded below) and the rest (UNKNOWN), which is
      the input Step 7 actually needs.
Unlike the class-2/3 probes this walks SUBDIRECTORIES: section 6 nests
its .mac files one level down (6.1 Hyperbolic sine/..., 26 files)."""
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECTION = sys.argv[1] if len(sys.argv) > 1 else "6 Hyperbolic functions"
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite", SECTION)

HEADS = ["GAMMA", "Ei", "E1", "E", "F0", "ProductLog", "FresnelC",
         "FresnelS", "Chi", "Shi", "Si", "Ci", "Li", "Erf", "Erfi", "Erfc",
         "PolyLog"]

NATS = ["gamma_incomplete(", "expintegral_ei(", "erf(", "erfi(",
        "lambert_w(", "exp(", "polylog(", "%e^"]

# Maxima atom character set: a head/nat match preceded by one of these is
# part of a longer name (e.g. Ei( inside ExpIntegralEi()
ATOMB = r"(?<![A-Za-z0-9$_%])"

# Heads the installed build resolves natively (verified in Maxima by
# probes/corpus/12-class6-answer-heads.run's second stage).
NATIVE = {
    "sin", "cos", "tan", "cot", "sec", "csc",
    "asin", "acos", "atan", "acot", "asec", "acsc", "atan2",
    "sinh", "cosh", "tanh", "coth", "sech", "csch",
    "asinh", "acosh", "atanh", "acoth", "asech", "acsch",
    "log", "exp", "sqrt", "abs", "signum", "max", "min",
    "gamma", "gamma_incomplete", "beta", "erf", "erfi", "erfc",
    "expintegral_ei", "expintegral_e1", "expintegral_li",
    "expintegral_si", "expintegral_ci", "expintegral_shi", "expintegral_chi",
    "polylog", "li", "psi", "zeta", "lambert_w",
    "integrate", "diff", "limit", "sum", "product",
    "hypergeometric", "bessel_j", "bessel_y", "bessel_i", "bessel_k",
    "elliptic_f", "elliptic_e", "elliptic_pi", "elliptic_kc", "elliptic_ec",
    "conjugate", "realpart", "imagpart", "floor", "ceiling", "round",
    "binomial", "factorial", "fresnel_s", "fresnel_c",
}


def call_arity(s, head):
    """Top-level argument counts of every head(… call in s."""
    out = []
    for m in re.finditer(ATOMB + re.escape(head) + r"\(", s):
        i, depth, args = m.end() - 1, 0, 0
        while i < len(s):
            c = s[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            elif c == "," and depth == 1:
                args += 1
            i += 1
        out.append(args + 1)
    return out


print(f"section: {SECTION!r}   date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
files = []
for dirpath, _dirs, fns in os.walk(SUITE):
    for fn in fns:
        if fn.endswith(".mac"):
            files.append(os.path.join(dirpath, fn))
files.sort()
if not files:
    raise SystemExit(f"no .mac files under {SUITE} — check the section name")
print(f"files: {len(files)} (walked, subdirectories included)")

total_entries = 0
arity = {h: {} for h in HEADS}
nat_counts = {n: 0 for n in NATS}
disc = {}
# entry lines only: the corpus's own [integrand, x, steps, answer] rows
for f in files:
    lines = [ln for ln in open(f, encoding="utf-8").read().splitlines()
             if ln.lstrip().startswith("[")]
    total_entries += len(lines)
    s = "\n".join(lines)
    for h in HEADS:
        for n in call_arity(s, h):
            arity[h][n] = arity[h].get(n, 0) + 1
    for nat in NATS:
        nat_counts[nat] += len(re.findall(ATOMB + re.escape(nat), s))
    for m in re.finditer(ATOMB + r"([A-Za-z_%][A-Za-z0-9_]*)\(", s):
        disc[m.group(1)] = disc.get(m.group(1), 0) + 1

print(f"entries: {total_entries}")
print("\n== (a) curated pass — class-2/3 HEADS/NATS ==")
for nat in NATS:
    if nat_counts[nat]:
        print(f"  {nat:22s} {nat_counts[nat]}")
hit = False
for h in HEADS:
    if arity[h]:
        hit = True
        print(f"  {h + '(':8s} {dict(sorted(arity[h].items()))}")
if not hit:
    print("  (no curated Rubi-notation head occurs in this section)")

print("\n== (b) discovery pass — every call head on an entry line ==")
unknown = {k: v for k, v in disc.items() if k not in NATIVE}
native = {k: v for k, v in disc.items() if k in NATIVE}
print(f"  NATIVE heads: {len(native)}")
for k, v in sorted(native.items(), key=lambda kv: -kv[1]):
    print(f"    {k + '(':24s} {v}")
print(f"  UNKNOWN heads (Step 7 HEAD_REWRITES input): {len(unknown)}")
for k, v in sorted(unknown.items(), key=lambda kv: -kv[1]):
    ar = {}
    for f in files:
        txt = "\n".join(ln for ln in open(f, encoding="utf-8").read().splitlines()
                        if ln.lstrip().startswith("["))
        for n in call_arity(txt, k):
            ar[n] = ar.get(n, 0) + 1
    print(f"    {k + '(':24s} {v:6d}   arity {dict(sorted(ar.items()))}")
if not unknown:
    print("    (none — every answer head is native)")
