#!/usr/bin/env python3
"""Probe: generation-vs-inventory census cross-check (T6 Step 4, static).

Run from the repo root:
  sh probes/census/01-generation-vs-inventory.run

What it measures: that the generator's per-file rule counts (the rule-run
parser applied to the Rubi source, exactly as the generator emits the
files) equal the T1 inventory's per-file counts for all 67 class-1 files,
that the total is 2710, and — the committed-output half (Task-6 review
finding 3: the source-only check let a corrupted generated file pass) —
that each committed rules/class1/<key>.mac exists and its
defmatch(_mr_pat_<key>_r<N> indices are exactly 1..count, so a missing,
empty, duplicated, or gap-having generated file fails the probe.

A name-integrity half (2026-08-24 dead-rule bug) additionally checks that
every `_mr*` token in a committed defmatch pattern is a well-formed
capture or MatchQ marker of THAT rule. The generator's drop_optionals
used to run post-translate and its text.replace("r_", "r") corrupted the
`_mr_` prefix of every capture in any rule carrying an `r` variable
(138 dead rules across 17 files). A corrupted token (`_mr1_...`) or a
token from the wrong rule is a mismatch here.

A native-elliptic half (2026-08-24, 5.50.0) checks that elliptic answers
use Maxima's native `elliptic_f/e/pi` nouns, not package `mr_elliptic_*`
nouns: `diff` knows the native derivatives, so the package spelling makes
verification strictly harder.

Other CONTENT integrity of a rule body (cond/repl semantics) is OUT of
scope — it rides on the parse sweep (probes/load_wall/probe-parse-sweep),
the per-file witness, the suite, and regeneration diffs. Static — no
Maxima — because the installed build cannot hold the 2710 patterns in one
process to check them there (measured 2026-08-20,
probes/load_wall/probe-load-wall.out); the in-suite test_census checks
the loadable subset instead. Exits nonzero on any mismatch (a broken
generation must fail the probe, not just the diff).
"""

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INV_OUT = ROOT / "probes" / "probe-rubi-anatomy" / "01-inventory.out"
RULES_DIR = ROOT / "rules" / "class1"


def _load(name, rel):
    p = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, p)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def pattern_name_issues(text, key):
    """(rule_number, token) pairs where a defmatch pattern carries an
    `_mr*` token that is not a well-formed capture or MatchQ marker of
    that same rule. Catches the 2026-08-24 drop_optionals corruption
    (`_mr_` prefix mangled to `_mr` by a capture named `r`) and any
    foreign/corrupted name that would make Maxima read the token as a
    literal symbol (a silently dead rule)."""
    issues = []
    pat_re = re.compile(
        r"^defmatch\(_mr_pat_" + re.escape(key) + r"_r(\d+), (.*), x\)\$",
        re.M)
    for m in pat_re.finditer(text):
        n = m.group(1)
        pat = m.group(2)
        tok_re = (r"_mr_" + re.escape(key) + r"_r" + n
                  + r"(mq\d+)?_[A-Za-z_][0-9A-Za-z_]*")
        for tok in re.findall(r"_mr[0-9A-Za-z_]*", pat):
            if not re.fullmatch(tok_re, tok):
                issues.append((n, tok))
    return issues


def native_elliptic_issues(text):
    """`mr_elliptic_*` call tokens in a committed rule file. The elliptic
    answer-side functions are NOT package-defined shims: Maxima's native
    `elliptic_f/e/pi` nouns are differentiable by `diff` (measured
    2026-08-24 on 5.50.0), and the corpus's expected answers use the
    native names, so the `mr_` spelling blocks both the verified chain
    and expected-answer cancellation."""
    return re.findall(r"\bmr_elliptic_(?:f|e|pi)\s*\(", text)


def inventory_counts(path):
    """Per-file class-1 counts from 01-inventory.out: key -> rule count.
    The per-file section rows:
      <count>  cond=<n> redisp=<n> subst=<n>   <rel path ending in .m>
    """
    counts = {}
    sec = False
    for ln in path.read_text().splitlines():
        if ln.startswith("=== per-file rule counts, class 1"):
            sec = True
            continue
        if ln.startswith("===") and sec:
            sec = False
            continue
        if not sec:
            continue
        m = re.match(r"\s+(\d+)\s+cond=\d+\s+redisp=\d+\s+subst=\d+\s+(.+)$",
                     ln)
        if not m:
            continue
        base = m.group(2).strip().split("/")[-1]
        key = base.split(" ")[0].replace(".", "_")
        counts[key] = int(m.group(1))
    return counts


def main():
    gen = _load("gen", "generator/generate_class1.py")
    inv = _load("inv01", "probes/probe-rubi-anatomy/01-inventory.py")
    cen = _load("cen01", "probes/translation/01-class1-syntax-census.py")

    files = gen.load_class1_files(gen.RUBI)
    gen_counts = {}
    for rel_m in files:
        key = gen.key_of(rel_m)
        text = inv.strip_comments((gen.RUBI / rel_m).read_text())
        gen_counts[key] = len(cen.rule_runs(text))

    inv_counts = inventory_counts(INV_OUT)

    print("=== generation-vs-inventory census cross-check ===")
    print(f"files: generator {len(gen_counts)}, inventory {len(inv_counts)}")
    bad = 0
    only_g = sorted(set(gen_counts) - set(inv_counts))
    only_i = sorted(set(inv_counts) - set(gen_counts))
    if only_g:
        print("only in generator:", only_g)
        bad += 1
    if only_i:
        print("only in inventory:", only_i)
        bad += 1
    for key in sorted(set(gen_counts) & set(inv_counts)):
        if gen_counts[key] != inv_counts[key]:
            print(f"count mismatch {key}: generator {gen_counts[key]} "
                  f"!= inventory {inv_counts[key]}")
            bad += 1
    total_g, total_i = sum(gen_counts.values()), sum(inv_counts.values())
    print(f"total: generator {total_g}, inventory {total_i}, expected 2710")
    if total_g != 2710 or total_i != 2710:
        bad += 1

    # Committed-output half: the generated files must carry exactly the
    # counted rules (defmatch indices 1..count, no dupes, no gaps).
    committed = {}
    name_bad = 0
    elliptic_bad = 0
    for key, count in gen_counts.items():
        path = RULES_DIR / f"{key}.mac"
        if not path.is_file():
            print(f"missing file {path.relative_to(ROOT)}")
            bad += 1
            continue
        text = path.read_text()
        idx = [int(m) for m in re.findall(
            r"^defmatch\(_mr_pat_" + re.escape(key) + r"_r(\d+),",
            text, re.M)]
        committed[key] = len(idx)
        if len(idx) != count:
            print(f"count mismatch {key}: committed {len(idx)} "
                  f"!= generator {count}")
            bad += 1
        elif sorted(idx) != list(range(1, count + 1)):
            print(f"index anomaly {key}: {sorted(idx)} is not 1..{count}")
            bad += 1
        issues = pattern_name_issues(text, key)
        if issues:
            name_bad += 1
            shown = ", ".join(f"r{n}:{t}" for n, t in issues[:5])
            more = f" (+{len(issues) - 5} more)" if len(issues) > 5 else ""
            print(f"name integrity {key}: {shown}{more}")
            bad += 1
        ell = native_elliptic_issues(text)
        if ell:
            elliptic_bad += 1
            shown = ", ".join(ell[:5])
            more = f" (+{len(ell) - 5} more)" if len(ell) > 5 else ""
            print(f"native elliptic nouns {key}: {shown}{more}")
            bad += 1
    total_c = sum(committed.values())
    print(f"committed: {len(committed)} files, {total_c} rules, "
          f"name-integrity bad files {name_bad}, "
          f"mr_elliptic_* files {elliptic_bad}")
    if len(committed) != len(gen_counts) or total_c != 2710:
        bad += 1
    print("VERDICT:", "MISMATCH" if bad else
          f"OK ({len(gen_counts)} files, {total_g} rules, all per-file "
          "counts equal; committed .mac carry exactly 1..N each; "
          "all defmatch pattern names are well-formed rule-local "
          "captures/markers; elliptic answers use the native "
          "elliptic_f/e/pi nouns)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
