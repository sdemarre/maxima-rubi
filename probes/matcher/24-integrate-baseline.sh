#!/bin/sh
# probes/matcher/24-integrate-baseline.sh -- see the .mac header.
# Usage (repo root):
#   sh probes/matcher/24-integrate-baseline.sh > probes/matcher/24-integrate-baseline.out 2>&1
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT=$(pwd)
W=${TMPDIR:-/tmp}/mr-24-integrate-baseline
rm -rf "$W"; mkdir -p "$W"
printf 'load("%s/probes/matcher/24-integrate-baseline.mac")$\n' "$ROOT" > "$W/run.mac"
echo "=== probes/matcher/24-integrate-baseline  git HEAD $(git rev-parse --short HEAD)  $(date -u '+%Y-%m-%d %H:%M UTC')"
timeout -s KILL 1800 maxima --very-quiet -b "$W/run.mac" < /dev/null 2>&1 | grep -a '^R '
echo "=== done"
