#!/bin/sh
# probes/matcher/26-eqq-symbolic-zero-test.sh -- see the .mac header.
# Usage (repo root):
#   sh probes/matcher/26-eqq-symbolic-zero-test.sh > probes/matcher/26-eqq-symbolic-zero-test.out 2>&1
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT=$(pwd)
W=${TMPDIR:-/tmp}/mr-26-eqq-symbolic-zero-test
rm -rf "$W"; mkdir -p "$W"
printf 'load("%s/probes/matcher/26-eqq-symbolic-zero-test.mac")$\n' "$ROOT" > "$W/run.mac"
echo "=== probes/matcher/26-eqq-symbolic-zero-test  git HEAD $(git rev-parse --short HEAD)  $(TZ=Europe/Brussels date '+%Y-%m-%d %H:%M %Z')"
echo "S generated %mr_eqQ( / %mr_neQ( call sites per class (grep -o over rules/):"
for d in rules/class*; do
  printf 'S %s eqQ %s neQ %s\n' "$(basename "$d")" \
    "$(cat "$d"/*.mac | grep -o '%mr_eqQ(' | wc -l)" "$(cat "$d"/*.mac | grep -o '%mr_neQ(' | wc -l)"
done
timeout -s KILL 900 setsid -w maxima --very-quiet -b "$W/run.mac" < /dev/null 2>&1 | grep -a '^[ZECR] '
echo "=== done"
