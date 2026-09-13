#!/bin/sh
# probes/matcher/06-dispatch-cost.sh -- dispatch cost of the matcher substrate
# on the full rule table (matcher substrate plan 2, Task 7).  Sequential runs,
# so run it on an otherwise idle machine; ~10 min wall (~11 with MR_P0_TREE).
# Usage (repo root):
#   sh probes/matcher/06-dispatch-cost.sh > probes/matcher/06-dispatch-cost.out 2>&1
# MR_P0_TREE=<a checkout of the P0 commit 0a6664c> adds the end-to-end rubi()
# wall of the P0 package on the same integrand (the A/B line).
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT=$(pwd)
W=${TMPDIR:-/tmp}/mr-06-dispatch-cost
rm -rf "$W"; mkdir -p "$W"
TLS='--tls-limit 100000'
now() { date +%s.%N; }
since() { python3 -c "print(round($(now) - $1, 1))"; }

run() { # <case> <cap seconds> [<tree>]
  tree=${3:-$ROOT}
  tag=$1${3:+-p0}
  printf 'mr_cost_case : "%s"$\nload("%s/probes/matcher/06-dispatch-cost.mac")$\n' "$1" "$ROOT" > "$W/$tag.mac"
  t=$(now)
  ( cd "$tree" && timeout -s KILL "$2" maxima --very-quiet -X "$TLS" -b "$W/$tag.mac" < /dev/null > "$W/$tag.out" 2>&1 )
  echo "CASE $tag (tree $tree) wall $(since $t) s"
  grep -a '^R ' "$W/$tag.out"
}

echo "=== probes/matcher/06-dispatch-cost  git HEAD $(git rev-parse --short HEAD)  $(date -u '+%Y-%m-%d %H:%M UTC')"
run walk 1800
for k in 6 8 10 12; do run claim$k 900; done
run attr 1800
run rubi 600
if [ -n "${MR_P0_TREE:-}" ]; then run rubi 600 "$MR_P0_TREE"; fi
echo "=== done"
