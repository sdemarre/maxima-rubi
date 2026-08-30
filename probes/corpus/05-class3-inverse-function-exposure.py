#!/usr/bin/env python3
"""Class-3 F_ rules' corpus exposure (milestone-3 close-out): the four
F_ rules (rules/class3/3_1_5.mac r58/r59 + 3.3 r62 + 3.4 r41, the
milestone-3 headvar feature) match integrands of the shape
Px * F(linear-in-x)^m * (a + b*log(...)), with F from the closed
allowlists (r58: asin/acos/asinh/acosh, r59: atan/acot/atanh/acoth,
the others per the acceptance record section 2 table). This probe
measures, over the WHOLE "3 Logarithms" section (3,085 entries), the
two superset exposures an F_ rule needs to ever fire:

  (A) an entry whose integrand carries an inverse-function factor with
      a LINEAR argument — the rule's F(linear) domain: the
      paren-balanced argument of an allowlist F( call contains the
      entry's integration variable exactly once, standalone (not a
      longer name, not under a power), and not inside a deeper call;
  (B) an entry whose integrand carries ANY inverse-function factor
      (any argument) and log( on the same line — the rule's log-
      factor half.

(A) alone is the match domain minus the log factor; (B) alone is the
log half. Measured (2026-08-30, whole-branch review): 12 entries —
3.1.5 e186-e197, all of the shape (d+e*x^2)*F(a*x)^m*log(c*x^n)
(m = 1: the eight F's; m = 2: asin/acos/asinh/acosh). The package run
fired on them (docs/corpus-class3-baseline-uplift.md section 2): the
r59 family (atan/acot/atanh/acoth, e188/e189/e192/e193) verifies 4/4
against the baseline's 12 unverified + 3 timeout; the r58 m = 1 hits
(e186/e187/e190/e191) answer unverified — the expected texts carry
atanh(sqrt(1+-a^2*x^2)) / (1+-a^2*x^2)^(3/2) terms the zero chain
does not close (verification gap, not a wrong answer); the m = 2 hits
(e194-e197) defer the F^2 sub-integral by design. NOTE: the
milestone-3 generation smoke reported this exposure as 0 (task-3
report — untracked, its inline scan was wrong); this probe is the
committed, re-runnable anchor for the CORRECTED claim. The
assertions self-flag if the pinned corpus (todo/TODO.md commit)
drifts.

Cited by: docs/corpus-class3-baseline-uplift.md section 2 and
test_maxima_rubi.mac's test_class3_headvar comment.

Run:
  sh probes/corpus/05-class3-inverse-function-exposure.run
"""
import glob
import os
import re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECTION = "3 Logarithms"
# Pinned-corpus expectation (task-3 smoke, 2026-08-29): 3,085 entries.
EXPECTED_TOTAL = 3085

# The two F_ rules' head allowlists (rules/class3/3_1_5.mac r58/r59).
ALLOW = ["asin", "acos", "asinh", "acosh", "atan", "acot", "atanh", "acoth"]

# Maxima atom character set: a call preceded by one of these is part of
# a longer name (probe-04 convention).
ATOMB = r"(?<![A-Za-z0-9$_])"


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


def balanced_arg(text, open_idx):
    """text[open_idx] == '('; return the paren-balanced argument text
    (or None if the call is unbalanced — a corrupt line, which the
    bad-shape assert below would catch anyway)."""
    depth = 0
    for i in range(open_idx, len(text)):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[open_idx + 1:i]
    return None


def wrapped_in_call(arg, pos):
    """True if arg[pos] sits inside a NAMED call within arg (the
    innermost enclosing paren was opened by a function name) —
    distinguishes asin(sin(x)) (x is not a linear factor of the
    integrand) from asin(x+1) (grouping parens carry no name)."""
    i, stack = 0, []
    while i < pos:
        c = arg[i]
        if c == "(":
            j = i - 1
            while j >= 0 and arg[j] == " ":
                j -= 1
            k = j
            while j >= 0 and (arg[j].isalnum() or arg[j] in "_%"):
                j -= 1
            stack.append(arg[j + 1:k + 1] or None)
        elif c == ")" and stack:
            stack.pop()
        i += 1
    return bool(stack) and stack[-1] is not None


def linear_factor(f_text, var):
    """(name, arg) of the first allowlist inverse-function call in
    f_text whose paren-balanced argument is linear in var (var
    standalone exactly once, not under a power, not inside a deeper
    call), else None."""
    var_rx = re.compile(
        r"(?<![A-Za-z0-9_])" + re.escape(var) + r"(?![A-Za-z0-9_^])")
    for name in ALLOW:
        for m in re.finditer(ATOMB + re.escape(name) + r"\(", f_text):
            arg = balanced_arg(f_text, m.end() - 1)
            if arg is None:
                continue
            xs = list(var_rx.finditer(arg))
            if len(xs) != 1:
                continue
            if wrapped_in_call(arg, xs[0].start()):
                continue
            return name, arg
    return None


files = sorted(glob.glob(os.path.join(
    ROOT, "reference", "maxima-syntax-test-suite", SECTION, "*.mac")))
if not files:
    raise SystemExit(f"no .mac files under {SECTION!r} — check the clone")

# Pinned-corpus expectation (measured 2026-08-30, whole-branch
# review): the F_ domain entries are exactly 3.1.5 e186-e197.
EXPECTED_HITS = {("3.1.5 u (a+b log(c x^n))^p.mac", e)
                 for e in range(186, 198)}

total = 0
per_file = {}
var_hist = {}
lin_hits = []      # (rel, e, name, arg)
log_inv_hits = []  # (rel, e)
for path in files:
    rel = SECTION + "/" + os.path.basename(path)
    entries = extract_entries(path)
    per_file[rel] = len(entries)
    for i, ent in enumerate(entries, 1):
        total += 1
        els = split_elements(ent[1:-1])
        if len(els) not in (4, 5):
            raise SystemExit(f"{rel} e{i}: bad entry shape ({len(els)} fields)")
        f_text, var = els[0], els[1]
        var_hist[var] = var_hist.get(var, 0) + 1
        hit = linear_factor(f_text, var)
        if hit is not None:
            lin_hits.append((rel, i, hit[0], hit[1]))
        if re.search(ATOMB + r"log\(", f_text) and any(
                re.search(ATOMB + re.escape(n) + r"\(", f_text)
                for n in ALLOW):
            log_inv_hits.append((rel, i))

print(f"probe: class3-inverse-function-exposure   "
      f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print(f"section: {SECTION!r}")
print(f"entries: {total}   (by file: " +
      ", ".join(f"{os.path.basename(r)} {n}" for r, n in sorted(per_file.items()))
      + ")")
print(f"variables: {dict(sorted(var_hist.items()))}")
print(f"(A) linear-arg inverse-function factor: {len(lin_hits)}")
for rel, i, name, arg in lin_hits[:20]:
    print(f"  {rel} e{i}: {name}({arg})")
print(f"(B) inverse-function factor + log( same line: {len(log_inv_hits)}")
for rel, i in log_inv_hits[:20]:
    print(f"  {rel} e{i}")

lin_set = {(os.path.basename(rel), e) for rel, e, _, _ in lin_hits}
log_set = {(os.path.basename(rel), e) for rel, e in log_inv_hits}
assert total == EXPECTED_TOTAL, \
    f"corpus moved: {total} != {EXPECTED_TOTAL} — re-derive the exposure claim"
assert lin_set == EXPECTED_HITS, \
    f"linear-arg exposure moved: {sorted(lin_set ^ EXPECTED_HITS)} — re-derive"
assert log_set == EXPECTED_HITS, \
    f"log-half exposure moved: {sorted(log_set ^ EXPECTED_HITS)} — re-derive"
print("exposure: 12/12 — 3.1.5 e186-e197 are the F_ rules' corpus domain "
      "(outcomes: docs/corpus-class3-baseline-uplift.md section 2)")
