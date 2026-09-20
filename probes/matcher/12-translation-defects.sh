#!/bin/sh
# probes/matcher/12-translation-defects.sh -- runs 12-translation-defects.mac
# on the current tree and prints its stamped record (git HEAD, date, build).
# Red record (the unfixed tree):  sh probes/matcher/12-translation-defects.sh > probes/matcher/12-translation-defects.red.out
# Green record (the fixed tree):  sh probes/matcher/12-translation-defects.sh > probes/matcher/12-translation-defects.out
set -u
cd "$(dirname "$0")/../.." || exit 1
echo "=== probes/matcher/12-translation-defects  git HEAD $(git rev-parse --short HEAD)  $(date -u '+%Y-%m-%d %H:%M UTC')"
timeout -s KILL 300 maxima --very-quiet -b probes/matcher/12-translation-defects.mac < /dev/null 2>&1 \
  | grep -a -E '^(R |SECTION |PASS:|FAIL:|Results:)'
