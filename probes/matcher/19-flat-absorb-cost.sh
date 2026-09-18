#!/bin/sh
# probes/matcher/19-flat-absorb-cost.sh -- what the product-arity cost of
# spec 3.8's "claim<k>" case is actually made of, and what the flat-absorb
# committed-tail prune does to it.
#
# Usage (repo root):
#   sh probes/matcher/19-flat-absorb-cost.sh > probes/matcher/19-flat-absorb-cost.out 2>&1
# MR_BASE=<commit> compares the tree's matcher against that commit's
# maxima_rubi_match.lisp (default: the commit that introduced the prune's
# parent, i.e. the matcher before it).
#
# The SBCL leg needs no Maxima and takes seconds; the Maxima leg loads the full
# rule table and runs probe 06's claim12 walk, so it takes ~3 min and wants an
# otherwise idle machine.
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT=$(pwd)
W=${TMPDIR:-/tmp}/mr-19-flat-absorb-cost
rm -rf "$W"; mkdir -p "$W"
BASE=${MR_BASE:-}

echo "=== probes/matcher/19-flat-absorb-cost  git HEAD $(git rev-parse --short HEAD)  $(date -u '+%Y-%m-%d %H:%M UTC')"

# every generated rule pattern, as test/check_generated_rules.py collects them
python3 - "$ROOT" "$W/patterns.tsv" <<'PY'
import re, sys, pathlib
root, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
rows = []
for p in sorted(root.glob("rules/class*/*.mac")):
    for key, n, pat in re.findall(
            r'^_mr_rule_\w+ : %mr_defrule\("([0-9a-z_]+)", (\d+), "([^"]*)"',
            p.read_text(), re.M):
        rows.append("%s r%s\t%s" % (key, n, pat))
out.write_text("\n".join(rows) + "\n")
print("R patterns %d" % len(rows))
PY

if [ -n "$BASE" ]; then
  git show "$BASE:maxima_rubi_match.lisp" > "$W/base-match.lisp" || exit 1
  echo "R base $BASE"
fi

echo "=== SBCL leg: matcher search cost, binding count, full-enumeration wall"
for k in 6 8 10 12; do
  sbcl --script "$ROOT/probes/matcher/19-flat-absorb-cost.lisp" \
       "$ROOT/maxima_rubi_match.lisp" "$W/patterns.tsv" "$k" tree
  if [ -n "$BASE" ]; then
    sbcl --script "$ROOT/probes/matcher/19-flat-absorb-cost.lisp" \
         "$W/base-match.lisp" "$W/patterns.tsv" "$k" base
  fi
done

echo "=== Maxima leg: what probe 06's claim12 wall is made of"
maxima --very-quiet -b "$ROOT/probes/matcher/19-flat-absorb-cost.mac" < /dev/null 2>&1 | grep -a '^R '
echo "=== done"
