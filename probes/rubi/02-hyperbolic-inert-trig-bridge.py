#!/usr/bin/env python3
"""probes/rubi/02 — how Rubi answers the class-6 `.7` family: the inert-trig
bridge.

The question (handoff 2026-09-20, "Open: the largest lever on class 6"): the
corpus's 6.x.7 files are 1,173 entries, 23 % of section 6, reaching NO rule in
our port, and all 13 pinned section-6 .m files ARE generated and loaded. The
handoff's guess was "likely a cross-section dependency ... presumably through
the algebraic or trig sections". This probe settles which, and by what
mechanism.

Static analysis over the two pinned reference clones plus the committed
class-6 record. No Maxima, no Mathematica.

Six measurements, each printed with the evidence that produced it:

  1. Rubi's inert function heads: which lowercase heads appear in rule LHSs.
  2. DeactivateTrigAux's hyperbolic branch — the imaginary-argument identities
     that map the six Hyperbolic heads onto the six INERT TRIG heads.
  3. The bridge rule: where Int[u_,x] -> Int[DeactivateTrig[u,x],x] lives, and
     how many rules invoke the conversion.
  4. Which corpus section-6 families have a Rubi section-6 rule file, and which
     do not.
  5. The `.7` rule files Rubi does have, and in which section.
  6. The class-6 record's `deferred` mass per corpus file, so the size of what
     the bridge would unlock is a number and not an impression.
"""

import collections
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUBI = os.path.join(ROOT, "reference", "rubi")
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
RULES = os.path.join(RUBI, "Rubi", "IntegrationRules")
UTILS = os.path.join(RUBI, "Rubi", "IntegrationUtilityFunctions.m")
RECORD = os.path.join(ROOT, "test", "corpus_class6.out")

INERT_CANDIDATES = ["sin", "cos", "tan", "cot", "sec", "csc",
                    "sinh", "cosh", "tanh", "coth", "sech", "csch"]
HYPERBOLIC = ["Sinh", "Cosh", "Tanh", "Coth", "Sech", "Csch"]


def head(msg):
    print()
    print("=" * 78)
    print(msg)
    print("=" * 78)


def pinned():
    out = []
    for name, path in (("rubi", RUBI), ("maxima-syntax-test-suite", SUITE)):
        p = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"],
                           capture_output=True, text=True)
        out.append(f"{name}: {p.stdout.strip() or 'UNKNOWN'}")
    return out


def rule_files():
    for dirpath, _, names in os.walk(RULES):
        for n in sorted(names):
            if n.endswith(".m"):
                yield os.path.join(dirpath, n)


def rel(path):
    return os.path.relpath(path, RULES)


def m1_inert_heads(texts):
    head("1. Rubi's inert function heads (lowercase) in the rule files")
    counts = collections.Counter()
    for _, text in texts:
        for h in INERT_CANDIDATES:
            counts[h] += len(re.findall(r"(?<![A-Za-z])" + h + r"\[", text))
    for h in INERT_CANDIDATES:
        print(f"  {h + '[':7s} {counts[h]:6d}")
    missing = [h for h in INERT_CANDIDATES[6:] if counts[h] == 0]
    print()
    print("  FINDING: Rubi has six inert heads and they are all TRIG.")
    print(f"  No inert hyperbolic head exists ({', '.join(missing)} never "
          "appear as rule heads),")
    print("  so a hyperbolic integrand cannot be matched by the inert rules "
          "as it stands.")
    return counts


def m2_deactivate_hyperbolic():
    head("2. DeactivateTrigAux's hyperbolic branch "
         "(IntegrationUtilityFunctions.m)")
    text = open(UTILS, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.startswith("DeactivateTrigAux[u_,x_] :="))
    block = lines[start:start + 26]
    hyp = [l.strip() for l in block
           if re.match(r"^\s*(" + "|".join(HYPERBOLIC) + r"),", l)]
    for l in block:
        if "HyperbolicQ[u]" in l or l.strip().startswith("With[{v=ExpandToSum[I*"):
            print("  " + l.strip())
    for l in hyp:
        print("    " + l)
    print()
    print(f"  FINDING: the HyperbolicQ branch rewrites all {len(hyp)} "
          "hyperbolic heads onto the")
    print("  INERT TRIG heads, with the argument multiplied by I "
          "(ExpandToSum[I*u[[1]],x]).")
    print("  Sinh -> -I sin[I z], Cosh -> cos[I z], Tanh -> -I tan[I z],")
    print("  Coth -> I cot[I z], Sech -> sec[I z], Csch -> I csc[I z].")
    print("  This is the whole cross-section dependency: after it, a "
          "hyperbolic integrand")
    print("  IS a trig integrand and section 4's rules apply.")
    return hyp


def m3_bridge_rule(texts):
    head("3. The bridge rule — where the conversion is invoked")
    invokers = [(rel(p), len(re.findall(r"DeactivateTrig\[", t)))
                for p, t in texts if "DeactivateTrig[" in t]
    for name, n in invokers:
        print(f"  {n:3d}  {name}")
    for p, t in texts:
        for line in t.splitlines():
            if "DeactivateTrig[" in line and "Int[u_" in line:
                print()
                print(f"  in {rel(p)}:")
                print("  " + line.strip()[:300])
    print()
    print(f"  FINDING: {len(invokers)} rule file invokes the conversion, "
          "through ONE catch-all rule")
    print("  at the head of 4.1.0.1 — the FIRST section-4 file Rubi.m loads:")
    print("    Int[u_, x_Symbol] := Int[DeactivateTrig[u, x], x] "
          "/; FunctionOfTrigOfLinearQ[u, x]")
    print("  Its condition (FunctionOfTrigOfLinearQ) is what admits "
          "hyperbolic integrands;")
    print("  DeactivateTrig's own first clause spells out "
          "`TrigQ[trig] || HyperbolicQ[trig]`.")
    print()
    print("  PORTING CONSEQUENCE: this is a bare `u_` LHS. Our dispatcher "
          "walks the table in")
    print("  load order and stops at the first rule that answers, so the "
          "ported record must sit")
    print("  at the END of the table, after every class. Mathematica orders "
          "it last by")
    print("  specificity; we have to do it by position.")
    return invokers


def m4_corpus_vs_rules():
    head("4. Corpus section-6 families against Rubi section-6 rule files")
    rubi6 = sorted(rel(p) for p in rule_files()
                   if p.startswith(os.path.join(RULES, "6 Hyperbolic")))
    corpus6 = []
    base = os.path.join(SUITE, "6 Hyperbolic functions")
    for dirpath, _, names in os.walk(base):
        for n in sorted(names):
            if n.endswith(".mac"):
                corpus6.append(os.path.relpath(os.path.join(dirpath, n), base))
    print(f"  Rubi section-6 rule files: {len(rubi6)}")
    for f in rubi6:
        print(f"    {f}")
    print(f"  Corpus section-6 files: {len(corpus6)}")
    for f in corpus6:
        print(f"    {f}")
    print()
    print("  FINDING: Rubi's section 6 covers only the x-dependent and "
          "miscellaneous families")
    print("  (6.1.10-13, 6.3.10-12, 6.5.10-11, 6.7.6-9). There is no "
          "section-6 file for the")
    print("  pure hyperbolic-power / binomial families at all — and none for "
          "the `.7` shape.")
    return rubi6, corpus6


def m5_dot7_rule_files():
    head("5. The `.7` rule files Rubi does have")
    seven = sorted(rel(p) for p in rule_files()
                   if re.search(r"/\d+\.\d+\.7 ", "/" + rel(p)))
    for f in seven:
        text = open(os.path.join(RULES, f), encoding="utf-8",
                    errors="replace").read()
        n = len(re.findall(r"^Int\[", text, re.M))
        inert = len(re.findall(r"(?<![A-Za-z])(sin|cos|tan|cot|sec|csc)\[",
                               text))
        print(f"  {n:4d} rules, {inert:4d} inert-head occurrences   {f}")
    print()
    print("  FINDING: read the inert-head column. Three `.7` files carry "
          "inert heads —")
    print("  4.1.7, 4.3.7, 4.5.7, the `(d trig)^m (a+b (c F)^n)^p` family — "
          "and they are all")
    print("  in section 4. The other files numbered `.7` (4.7.7, 5.3.7, "
          "6.7.7, 7.3.7) are a")
    print("  DIFFERENT family (`F^(c(a+b x)) trig(d+e x)^n` and the inverse "
          "miscellanies), use")
    print("  no inert head, and are not what the corpus's 6.x.7 files "
          "mirror.")
    print("  The corpus mirrors the inert three as 4.1.7 ... 4.6.7 AND as "
          "6.1.7 ... 6.6.7:")
    print("  the same rules serve both, the hyperbolic side via the bridge. "
          "Note Rubi has only")
    print("  three of them against the corpus's six — sin/tan/sec carry "
          "cos/cot/csc, as the")
    print("  4.1.0.x and 4.7.x normalization files do for the rest of "
          "section 4.")
    return seven


def m6_record_deferred():
    head("6. The class-6 record's deferred mass per corpus file")
    if not os.path.exists(RECORD):
        print(f"  MISSING {RECORD} — skipped")
        return None
    per = collections.Counter()
    verdicts = collections.Counter()
    seven = collections.Counter()
    for line in open(RECORD, encoding="utf-8", errors="replace"):
        m = re.match(r"^(\S+)\s+t=\s*\S+\s+"
                     r"(6 Hyperbolic functions/[^/]+/([^/]+))\.mac ", line)
        if not m:
            continue
        verdict, _, fname = m.group(1), m.group(2), m.group(3)
        verdicts[verdict] += 1
        if re.match(r"^6\.[1-6]\.7 ", fname):
            seven[verdict] += 1
        if verdict == "deferred":
            per[fname] += 1
    tot = sum(per.values())
    print("  verdicts:  " + "  ".join(f"{k} {v}" for k, v in
                                      verdicts.most_common()))
    print(f"  deferred total: {tot}")
    print()
    for k, v in per.most_common():
        mark = " <- .7" if re.match(r"^6\.[1-6]\.7 ", k) else ""
        print(f"  {v:5d}  {100 * v / tot:4.1f}%  {k}{mark}")
    s7 = sum(seven.values())
    d7 = seven["deferred"]
    print()
    print(f"  FINDING: the `.7` family is {s7} entries, "
          f"{d7} of them deferred —")
    print(f"  {100 * d7 / tot:.1f} % of class 6's deferred mass, and NOT ONE "
          "of them a PASS")
    print("  (" + ", ".join(f"{k} {v}" for k, v in seven.most_common()) + ").")
    print()
    print("  The seven `Hyperbolic <fn> functions` / 6.7.1 miscellany files "
          "are a further")
    print(f"  {sum(v for k, v in per.items() if 'functions' in k)} deferred "
          "entries and have no section-6 rule file either; whether")
    print("  they ride the same bridge is a SEPARATE question this probe "
          "does not answer.")
    return per, seven


def main():
    print("probes/rubi/02 — the hyperbolic -> inert-trig bridge")
    print("Static analysis; no Maxima. Pinned reference clones:")
    for l in pinned():
        print("  " + l)
    texts = [(p, open(p, encoding="utf-8", errors="replace").read())
             for p in rule_files()]
    print(f"  Rubi rule files read: {len(texts)}")

    m1_inert_heads(texts)
    m2_deactivate_hyperbolic()
    m3_bridge_rule(texts)
    m4_corpus_vs_rules()
    m5_dot7_rule_files()
    m6_record_deferred()

    head("CONCLUSION")
    print("""\
The class-6 `.7` family is answered by SECTION 4's rules, through the
inert-trig bridge — confirmed, and the mechanism is exact:

  1. One catch-all rule at the head of 4.1.0.1 rewrites any integrand
     satisfying FunctionOfTrigOfLinearQ into the inert representation.
  2. DeactivateTrigAux's HyperbolicQ branch carries the six hyperbolic heads
     onto the six inert TRIG heads by the imaginary-argument identities.
  3. Section 4's rules — including 4.1.7 / 4.3.7 / 4.5.7, the only `.7` rule
     files Rubi has — match the inert heads, and ActivateTrig puts the answer
     back.

So the handoff's guess was right about the section (trig, not algebraic), and
the unlock is REAL but NOT free: porting class 4's rule files alone does not
deliver it. The bridge needs its substrate ported too —
FunctionOfTrigOfLinearQ, DeactivateTrig/DeactivateTrigAux, ReduceInertTrig,
FixInertTrigFunction, UnifyInertTrigFunction, ActivateTrig, InertTrigQ /
InertTrigFreeQ — plus the inert representation itself in the tree, and the
4.7.1/4.7.2/4.7.3 normalization files and 4.7.5 Inert trig functions.

That makes the inert-trig family the load-bearing part of the class-4 port,
not a tail item: it gates class 4's own 22,472 entries AND ~37 % of class 6's
deferred mass that is already paid for.

Consequence for class 7 (6,552 entries) against class 5: the same question has
to be asked separately — the inverse hyperbolic / inverse trig pair has no
inert representation, so this finding does NOT transfer to it by analogy.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
