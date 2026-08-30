#!/usr/bin/env python3
"""Class-3 residue census: the FAIL entries of a corpus record, joined
back to the suite files' expected texts — the FAIL masses per corpus
file and the expected-answer head distribution of the residue (the
residue -> expected-head census of the class-3 acceptance record §5).
A variant of 03-class3-answer-heads.py restricted to the entries
classified FAIL in a source record (argv[1], default
test/corpus_class3.out; PASS = {expected, verified, no-answer}).

Entry/field parsing mirrors test/corpus_driver.py (extract_entries +
split_elements): entry = the line text minus the outer brackets;
els[3] the primary expected text, els[4] the secondary (5-field
entries). Both expected texts are counted (the harness normalizes both).
NATS extends 03's list with hypergeometric( — 03 excludes it as a common
native, but the residue census tracks verify-gap heads (the class-2
record §5 precedent), and the Task-1 supplementary sweep measured 49
hypergeometric( occurrences in the section's expected texts."""
import glob
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RECORD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "test", "corpus_class3.out")
RECORD_REL = os.path.relpath(RECORD, ROOT)

PASS = {"expected", "verified", "no-answer"}
FAIL_ORDER = ["unverified", "deferred", "timeout", "unexpected",
              "contains-noun", "error"]

HEADS = ["GAMMA", "Ei", "E1", "E", "F0", "ProductLog", "FresnelC",
         "FresnelS", "Chi", "Shi", "Si", "Ci", "Li", "Erf", "Erfi", "Erfc",
         "PolyLog"]
NATS = ["gamma_incomplete(", "expintegral_ei(", "erf(", "erfi(",
        "lambert_w(", "exp(", "polylog(", "%e^", "hypergeometric("]

# Maxima atom character set: a head/nat match preceded by one of these is
# part of a longer name (e.g. Ei( inside ExpIntegralEi()
ATOMB = r"(?<![A-Za-z0-9$_])"

T3 = re.compile(r'^(?P<cls>\S+)\s+t=\s*(?P<t>[\d.]+)s '
                r'(?P<rel>.*) e(?P<e>\d+) L(?P<ln>\d+)\s*$')
FILTER = re.compile(r"^filter: '(.*)/'")


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


def split_elements(entry_text):
    """Depth-aware split at top-level commas (mirror of the driver's)."""
    parts, depth, cur = [], 0, ""
    for ch in entry_text:
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts]


def extract_entries(path):
    """Entry texts (outer brackets, no trailing comma/$) (driver mirror)."""
    lines = open(path, encoding="utf-8").read().splitlines()
    entries = []
    for l in lines:
        if l.strip().startswith("["):
            t = l.rstrip()
            if t.endswith("$"):
                t = t[:-1]
            if t.endswith(","):
                t = t[:-1]
            entries.append(t)
    assert entries and entries[-1].endswith("]]"), path
    entries[-1] = entries[-1][:-1]
    return entries


rec = open(RECORD, encoding="utf-8").read().splitlines()
section = None
fails = {}  # (rel, e) -> (cls, t)
total = 0
for ln in rec:
    m = FILTER.match(ln)
    if m:
        section = m.group(1)
        continue
    m = T3.match(ln)
    if m:
        total += 1
        if m.group("cls") not in PASS:
            fails[(m.group("rel"), int(m.group("e")))] = (
                m.group("cls"), m.group("t"))
if section is None:
    raise SystemExit(f"no `filter: '…/'` line in {RECORD_REL} — not a merged record?")

suite_root = os.path.join(ROOT, "reference", "maxima-syntax-test-suite", section)
files = sorted(glob.glob(os.path.join(suite_root, "*.mac")))
if not files:
    raise SystemExit(f"no .mac files under {suite_root} — check the section name")

print(f"record: {RECORD_REL}")
print(f"section: {section!r}   date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print(f"entries: {total}   FAIL: {len(fails)}")

# Expected texts per (rel, e); per-file masses / samples in record order.
exp_texts = {}
per_file = {}  # rel -> {cls: [(e, t) in record order]}
for path in files:
    rel = section + "/" + os.path.basename(path)
    entries = extract_entries(path)
    per_file[rel] = {c: [] for c in FAIL_ORDER}
    for i, ent in enumerate(entries, 1):
        els = split_elements(ent[1:-1])
        if len(els) not in (4, 5):
            raise SystemExit(f"{rel} e{i}: bad entry shape ({len(els)} fields)")
        exp_texts[(rel, i)] = [els[3]] + ([els[4]] if len(els) == 5 else [])
        if (rel, i) in fails:
            per_file[rel][fails[(rel, i)][0]].append((i, fails[(rel, i)][1]))

print()
print("== FAIL masses by corpus file ==")
print("file" + "".join(f" {c:>13s}" for c in FAIL_ORDER) + "   n  FAIL")
for rel in sorted(per_file):
    suite_n = len([1 for k in exp_texts if k[0] == rel])
    cells = "".join(f" {len(per_file[rel][c]):13d}" for c in FAIL_ORDER)
    fail_n = sum(len(v) for v in per_file[rel].values())
    print(f"{os.path.basename(rel)}{cells}  {suite_n:4d}  {fail_n:4d}")
tot = {c: sum(len(per_file[rel][c]) for rel in per_file) for c in FAIL_ORDER}
print("total" + "".join(f" {tot[c]:13d}" for c in FAIL_ORDER) +
      f"  {total:4d}  {sum(tot.values()):4d}")

print()
print("== first 5 sample entries per (file, FAIL class) ==")
for rel in sorted(per_file):
    for c in FAIL_ORDER:
        s = per_file[rel][c]
        if not s:
            continue
        sample = ", ".join(f"e{e} {t}s" for e, t in s[:5])
        if len(s) > 5:
            sample += f" (+{len(s) - 5} more)"
        print(f"{os.path.basename(rel)} {c}: {sample}")


def census(texts):
    nat = {n: 0 for n in NATS}
    head = {h: {} for h in HEADS}
    for t in texts:
        for n in NATS:
            nat[n] += len(re.findall(ATOMB + re.escape(n), t))
        for h in HEADS:
            for a in call_arity(t, h):
                head[h][a] = head[h].get(a, 0) + 1
    return nat, head


print()
print("== expected-answer heads of FAIL entries (per FAIL class + total) ==")
for c in FAIL_ORDER:
    if tot[c] == 0:
        continue
    texts = [t for (rel, e), ts in exp_texts.items() if (rel, e) in fails
             and fails[(rel, e)][0] == c for t in ts]
    nat, head = census(texts)
    print(f"{c} ({tot[c]}):")
    for n in NATS:
        if nat[n]:
            print(f"  {n:22s} {nat[n]}")
    for h in HEADS:
        if head[h]:
            print(f"  {h + '(':8s} {dict(sorted(head[h].items()))}")
fail_texts = [t for (rel, e), ts in exp_texts.items() if (rel, e) in fails
              for t in ts]
nat, head = census(fail_texts)
print(f"TOTAL ({sum(tot.values())}):")
for n in NATS:
    if nat[n]:
        print(f"  {n:22s} {nat[n]}")
for h in HEADS:
    if head[h]:
        print(f"  {h + '(':8s} {dict(sorted(head[h].items()))}")
