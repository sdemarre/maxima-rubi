#!/usr/bin/env python3
"""probes/matcher/04-tree-counts.py -- static counts of today's tree that the
matcher substrate design cites (docs/superpowers/specs/
2026-09-12-matcher-substrate-design.md, section 2.3).

No Maxima run, no rule files loaded: it reads the generated rule files, the
utils and the Layer A suite as text.  Re-run from anywhere:

    python3 probes/matcher/04-tree-counts.py > probes/matcher/04-tree-counts.out
"""
import collections
import datetime
import glob
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(ROOT)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True,
                          text=True).stdout.strip()


def strip_comments(src):
    """Remove /* ... */ comments, keeping line numbers."""
    return re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"),
                  src, flags=re.S)


RULE_FILES = sorted(glob.glob("rules/class*/*.mac"))
TRACKED = RULE_FILES + ["maxima_rubi_utils.mac", "test_maxima_rubi.mac"]

print("=== probes/matcher/04-tree-counts  run: "
      + datetime.datetime.now(datetime.timezone.utc)
      .strftime("%Y-%m-%d %H:%M UTC"))
print(f"git HEAD: {git('rev-parse', 'HEAD')}")
dirty = git("status", "--porcelain", "--", *TRACKED)
print("counted files dirty vs HEAD: " + ("yes\n" + dirty if dirty else "no"))
print(f"rule files: {len(RULE_FILES)}")
print()

# --- rules per class --------------------------------------------------------
print("SECTION rules per class (sum of mr_rules_count_<key>)")
per_class = collections.Counter()
per_file = {}
for f in RULE_FILES:
    cls = f.split("/")[1]
    for m in re.finditer(r"^mr_rules_count_([0-9a-z_]+) : ([0-9]+)",
                         open(f).read(), flags=re.M):
        per_class[cls] += int(m.group(2))
        per_file[m.group(1)] = int(m.group(2))
for cls in sorted(per_class):
    print(f"  {cls}: {per_class[cls]}")
print(f"  total: {sum(per_class.values())}")
print(f"  9_1 (manual port): {per_file.get('9_1')}")
extra = {k: v for k, v in per_file.items() if k.endswith('b')}
print(f"  EXTRA_CLASS1 b files: {len(extra)} files, "
      f"{sum(extra.values())} rules {sorted(extra.items())}")
print()

# --- defmatch vs workaround emitters ------------------------------------------
print("SECTION pattern emission")
allrules = "".join(open(f).read() for f in RULE_FILES)
n_rulefn = len(re.findall(r"^_mr_rule_[0-9a-z_]+\(f, x\) :=", allrules,
                          flags=re.M))
n_defmatch = len(re.findall(r"^defmatch\(", allrules, flags=re.M))
print(f"  _mr_rule_* functions: {n_rulefn}")
print(f"  defmatch: {n_defmatch}")
print(f"  without defmatch (workaround emitters): {n_rulefn - n_defmatch}")
helpers = collections.Counter(re.findall(
    r"%mr_(mbp_base|binpowfactors|headvar_match|logpow_match"
    r"|logratio_match|logratio_sq_match|lpfac)\(", allrules))
for h, c in helpers.most_common():
    print(f"  call sites %mr_{h}: {c}")
n_matchdeclare = len(re.findall(r"^matchdeclare\(", allrules, flags=re.M))
print(f"  matchdeclare statements: {n_matchdeclare}")
print()

# --- inner conditions ---------------------------------------------------------
print("SECTION repl bodies carrying the inner-condition guard "
      "'(if is(<inner>) = true then ... else false)'")
tot = collections.Counter()
inner = collections.Counter()
inner_ids = collections.defaultdict(list)
for f in RULE_FILES:
    cls = f.split("/")[1]
    for m in re.finditer(r"^(_mr_repl_\w+)\(mm, x\) := (.*?)\)\$\n",
                         open(f).read(), flags=re.M | re.S):
        tot[cls] += 1
        if re.search(r"\(if is\(.*= true then", m.group(2), flags=re.S):
            inner[cls] += 1
            inner_ids[cls].append(m.group(1))
for cls in sorted(tot):
    print(f"  {cls}: repl bodies {tot[cls]}, with guard {inner[cls]}")
print(f"  total with guard: {sum(inner.values())}")
print()

# --- MatchQ -------------------------------------------------------------------
print("SECTION %mr_matchQ")
mq_files = collections.Counter()
for f in RULE_FILES:
    c = len(re.findall(r"%mr_matchQ\(", strip_comments(open(f).read())))
    if c:
        mq_files[f] = c
print(f"  rule files: {sum(mq_files.values())} calls in {len(mq_files)} files")
for f, c in sorted(mq_files.items()):
    print(f"    {f}: {c}")
utils = strip_comments(open("maxima_rubi_utils.mac").read()).split("\n")
defn, sites = [], []
for n, line in enumerate(utils, 1):
    for _ in re.finditer(r"%mr_matchQ\(", line):
        (defn if re.match(r"^%mr_matchQ\(", line) else sites).append(
            (n, line.strip()[:80]))
print(f"  maxima_rubi_utils.mac: definition at {[n for n, _ in defn]}; "
      f"{len(sites)} call sites outside comments")
for n, text in sites:
    print(f"    :{n}  {text}")
print()

# --- rubi_hybrid --------------------------------------------------------------
print("SECTION rubi_hybrid references")
for f in RULE_FILES:
    c = len(re.findall(r"rubi_hybrid", strip_comments(open(f).read())))
    if c:
        print(f"  {f}: {c} (outside comments)")
print()

# --- Layer A coupling ---------------------------------------------------------
print("SECTION test_maxima_rubi.mac lines containing each token")
suite = open("test_maxima_rubi.mac").read().split("\n")
for tok in ["_mr_pat_", "defmatch", "%mr_mbp_base", "%mr_matchQ",
            "matchdeclare", "_mr_rule_", "%mr_dispatch_rev",
            "%mr_dispatch_i1", "%mr_dispatch_p4", "rubi_hybrid"]:
    print(f"  {tok}: {sum(1 for l in suite if tok in l)}")
