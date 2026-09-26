#!/bin/sh
# probes/matcher/25-class7-eqq-shifted-quadratic.sh -- see the .mac header.
# Usage (repo root):
#   sh probes/matcher/25-class7-eqq-shifted-quadratic.sh > probes/matcher/25-class7-eqq-shifted-quadratic.out 2>&1
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT=$(pwd)
W=${TMPDIR:-/tmp}/mr-25-class7-eqq-shifted-quadratic
rm -rf "$W"; mkdir -p "$W"
printf 'load("%s/probes/matcher/25-class7-eqq-shifted-quadratic.mac")$\n' "$ROOT" > "$W/run.mac"
echo "=== probes/matcher/25-class7-eqq-shifted-quadratic  git HEAD $(git rev-parse --short HEAD)  $(date -u '+%Y-%m-%d %H:%M UTC')"
timeout -s KILL 600 maxima --very-quiet -b "$W/run.mac" < /dev/null 2>&1 | grep -a '^R '
echo "=== done"
