#!/bin/sh
# probes/matcher/21-r37-attribution.sh -- attribute the 3_5 r37 cost
# regression across the two commits between probe 06's two records, and test
# whether r37 is on a real dispatch path at all.
#
# Usage (repo root):
#   sh probes/matcher/21-r37-attribution.sh > probes/matcher/21-r37-attribution.out 2>&1
#
# Sequential; run it on an otherwise idle machine.  ~35 min wall.
#
# Three trees, so the two semantic commits between 46dffa2 (probe 06's 19.0 s
# record) and dfbff5f (its 350.0 s record) are separated:
#   T0  46dffa2  before both
#   T1  04d95a9  exact seen test + rules-only switches + ExpandExpression + Rt
#   T2  HEAD     + 29d237a, the faithful pair (seen-cut fall-through and
#                mr_giveup_last), + the section 3.8 prune
# MR_T0_TREE / MR_T1_TREE are checkouts of those commits; without them only
# the HEAD arm runs.
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT=$(pwd)
W=${TMPDIR:-/tmp}/mr-21-r37
rm -rf "$W"; mkdir -p "$W"
now() { date +%s.%N; }
since() { python3 -c "print(round($(now) - $1, 1))"; }

run() { # <case> <cap seconds> [<tree>] [<tag suffix>]
  tree=${3:-$ROOT}
  tag=$1${4:-}
  printf 'mr_r37_case : "%s"$\nload("%s/probes/matcher/21-r37-attribution.mac")$\n' \
         "$1" "$ROOT" > "$W/$tag.mac"
  t=$(now)
  ( cd "$tree" && timeout -s KILL "$2" maxima --very-quiet -b "$W/$tag.mac" \
      < /dev/null > "$W/$tag.out" 2>&1 )
  echo "CASE $tag (tree $tree) wall $(since $t) s"
  grep -a '^R ' "$W/$tag.out" || echo "R NO OUTPUT (cap $2 s?)"
}

echo "=== probes/matcher/21-r37-attribution  git HEAD $(git rev-parse --short HEAD)  $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "=== T2 = HEAD"
run nested     1800
run nested_gl0 1800
run accept37   1800
run rubi       1800
run rubi_no37  1800
if [ -n "${MR_T1_TREE:-}" ]; then
  echo "=== T1 = 04d95a9 (exact seen test, before the faithful pair)"
  run nested 1800 "$MR_T1_TREE" -t1
  run rubi   1800 "$MR_T1_TREE" -t1
fi
if [ -n "${MR_T0_TREE:-}" ]; then
  echo "=== T0 = 46dffa2 (before both)"
  run nested 1800 "$MR_T0_TREE" -t0
  run rubi   1800 "$MR_T0_TREE" -t0
fi
echo "=== done"
