#!/usr/bin/env python3
"""probes/rubi/04-section9-load-and-legacy.py -- the section-9 facts behind
docs/superpowers/specs/2026-09-22-section9-port-design.md. Static, no Maxima.

A. Which section-9 files the pinned Rubi.m loads (line numbers) and the
   `^Int[` rule count of every section-9 file in the clone.
B. The Dec-2023 renumbering: the section-9 LoadRules lines commit f7fa0fd
   removed and added in Rubi.m.
C. Where the 27 `^Int[` left-hand sides of the legacy, no-longer-loaded
   `9.1 Integrand simplification rules.m` live in the pinned rule set
   (whitespace-insensitive; the four renumbered-away section-9 files
   excluded).
D. Constant-factor extraction: every loaded rule file with a rule whose LHS
   starts `Int[Complex[0,`, `Int[a_*u_` or `Int[-u_`.
E. Corpus entries carrying a formal derivative (`Derivative(`), per file.
F. Old-numbered (2018-era) section-9 files against their pinned successors:
   rules (whole `Int[...] := ...` text, whitespace-insensitive) present in
   the old file and absent from the new one, and vice versa.
"""
import glob, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUBI = os.path.join(ROOT, "reference", "rubi")
RULES = os.path.join(RUBI, "Rubi", "IntegrationRules")
S9 = os.path.join(RULES, "9 Miscellaneous")
SUITE = os.path.join(ROOT, "reference", "maxima-syntax-test-suite")
STALE = ("9.1 Integrand", "9.2 Derivative", "9.3 Piecewise", "9.4 Misc")
N = lambda s: re.sub(r"\s+", "", s)

print("pinned rubi:", subprocess.run(["git", "-C", RUBI, "rev-parse", "HEAD"],
                                     capture_output=True, text=True).stdout.strip())
print("\n== A. section-9 LoadRules lines in Rubi.m ==")
for i, l in enumerate(open(os.path.join(RUBI, "Rubi", "Rubi.m")), 1):
    if "9 Miscellaneous" in l:
        print(f"  Rubi.m:{i}: {l.strip()}")
print("  rule counts (^Int[ lines):")
for f in sorted(os.listdir(S9)):
    if f.endswith(".m"):
        n = sum(1 for l in open(os.path.join(S9, f)) if l.startswith("Int["))
        print(f"  {n:4d}  {f}")

print("\n== B. f7fa0fd: section-9 LoadRules lines removed/added ==")
diff = subprocess.run(["git", "-C", RUBI, "show", "f7fa0fd", "--", "Rubi/Rubi.m"],
                      capture_output=True, text=True).stdout
for l in diff.splitlines():
    if l[:1] in "+-" and "9 Miscellaneous" in l:
        print("  " + l.strip())

print("\n== C. legacy 9.1 Integrand simplification LHSs in the pinned rule set ==")
src = open(os.path.join(S9, "9.1 Integrand simplification rules.m")).read()
lhs = [N(l.split(":=")[0]) for l in src.splitlines() if l.startswith("Int[")]
loaded = {}
for f in glob.glob(os.path.join(RULES, "**", "*.m"), recursive=True):
    rel = os.path.relpath(f, RULES)
    if rel.startswith("9 Misc") and any(s in rel for s in STALE):
        continue
    loaded[rel] = N(open(f).read())
found = 0
for l in lhs:
    hits = sorted(os.path.basename(r) for r, t in loaded.items() if l in t)
    found += bool(hits)
    print(f"  {'FOUND ' if hits else 'absent'} {l[:62]:62s} {hits[:2]}")
print(f"  found {found} / {len(lhs)}")

print("\n== D. constant-factor LHSs (Int[Complex[0, / Int[a_*u_ / Int[-u_) ==")
pat = re.compile(r"^Int\[(Complex\[0,|a_\*u_|-u_)")
for f in sorted(glob.glob(os.path.join(RULES, "**", "*.m"), recursive=True)):
    rel = os.path.relpath(f, RULES)
    n = sum(1 for l in open(f) if pat.match(N(l)))
    if n:
        tag = " (NOT loaded: renumbered away)" if any(s in rel for s in STALE) else ""
        print(f"  {n:3d}  {rel}{tag}")

print("\n== E. corpus entries with a formal derivative ==")
for f in sorted(glob.glob(os.path.join(SUITE, "**", "*.mac"), recursive=True)):
    n = sum(1 for l in open(f, errors="replace") if l.startswith("[") and "Derivative(" in l)
    if n:
        print(f"  {n:4d}  {os.path.relpath(f, SUITE)}")

print("\n== F. old-numbered files vs their pinned successors (whole-rule text) ==")
def rules(f):
    out, cur = [], None
    for l in open(os.path.join(S9, f)):
        if l.startswith("Int["):
            if cur: out.append(N(cur))
            cur = l
        elif cur is not None:
            if l.startswith("(*") or not l.strip():
                out.append(N(cur)); cur = None
            else:
                cur += l
    if cur: out.append(N(cur))
    return out
for old, new in (("9.2 Derivative integration rules.m", "9.1 Derivative integration rules.m"),
                 ("9.3 Piecewise linear functions.m", "9.2 Piecewise linear functions.m"),
                 ("9.4 Miscellaneous integration rules.m", "9.3 Miscellaneous integration rules.m")):
    o, n = rules(old), rules(new)
    so, sn = set(o), set(n)
    print(f"  {old} ({len(o)}) -> {new} ({len(n)}): "
          f"only-old {len(so - sn)}, only-new {len(sn - so)}, shared {len(so & sn)}")
    ol = {r.split(":=")[0] for r in so - sn}; nl = {r.split(":=")[0] for r in sn}
    print(f"    only-old rules whose LHS is absent from the new file: {len(ol - nl)}")
    for r in sorted(ol - nl):
        print(f"      {r[:100]}")
