#!/bin/sh
# test/section9_measure.sh -- the section-9 measurement, spec §4, chained
# in ONE detached script (memory: chain overnight follow-ups):
#   1. re-baseline classes 1/2/3/6 on the merge-base core (the reference);
#   2. the same four classes on the branch core;
#   3. ab_records.py per class;
#   4. the PAIRED rerun of every entry whose verdict CLASS differs (both
#      cores concurrently, 12 workers each, same load), for verdict
#      attribution.
# All runs: queue runner, 24 workers (user decision 2026-09-22), 30 s CPU cap.
#
#   setsid sh test/section9_measure.sh > test/section9_measure.log 2>&1 < /dev/null &
#
# Task-13 prep note (this differs from the original brief, written before
# prep): the reference worktree ../mr-s9-ref and its rules core already
# exist (built once, deliberately never rebuilt here -- see the pinned-core
# note in test/corpus_driver.py: a pinned core's fingerprint is never
# checked against this tree and it is never rebuilt). This script only
# verifies its stamp against the expected fingerprint and refuses if it
# does not match. The branch core IS rebuilt here every run (cheap, ~3 s;
# "never skip a rebuild to save time", test/build_rules_core.sh) and its
# resulting fingerprint is logged, not asserted against a fixed value --
# a later commit on this branch is expected to move it.
set -u
cd "$(dirname "$0")/.." || exit 1
REF=../mr-s9-ref
REF_CORE="$REF/test/mr_rules.core"
REF_STAMP="$REF_CORE.stamp"
EXPECT_REF_FP=0182d32ce35fda4b93d3f33d2ad8b43a

echo "$(date '+%F %T %Z') host check"
uptime; ps -eo pcpu,comm --sort=-pcpu | head -6
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 2 ]; then echo "REFUSING: 1-minute load $LOAD1 > 2 -- quiet the host first"; exit 3; fi

[ -f "$REF_CORE" ] && [ -f "$REF_STAMP" ] || { echo "REFUSING: reference core/stamp missing at $REF_CORE"; exit 4; }
REF_FP=$(awk '/^fingerprint /{print $2}' "$REF_STAMP")
if [ "$REF_FP" != "$EXPECT_REF_FP" ]; then
  echo "REFUSING: reference core fingerprint $REF_FP != expected $EXPECT_REF_FP"
  exit 4
fi
echo "$(date '+%F %T %Z') reference core OK: fingerprint $REF_FP ($(awk '/^rules /{print $2}' "$REF_STAMP") rules, $(awk '/^git_rev /{print $2}' "$REF_STAMP"))"

sh test/build_rules_core.sh || exit 4
BRANCH_FP=$(awk '/^fingerprint /{print $2}' test/mr_rules.core.stamp)
echo "$(date '+%F %T %Z') branch core: fingerprint $BRANCH_FP ($(awk '/^rules /{print $2}' test/mr_rules.core.stamp) rules)"

run_class() {  # $1 section  $2 prev-record  $3 out-record  $4 core-or-empty
  slug="class$(echo "$1" | cut -d' ' -f1)"
  echo "$(date '+%F %T %Z') start $1 -> $3 (core ${4:-branch})"
  if [ -n "$4" ]; then
    MR_RULES_CORE_PATH="$4" python3 test/run_corpus_queue.py "$1" --prev "$2" --workers 24 --launch || return 1
  else
    python3 test/run_corpus_queue.py "$1" --prev "$2" --workers 24 --launch || return 1
  fi
  sh test/wait_and_merge.sh "test/corpus_$slug.shard-pids" test/merge_class_shards.py \
     "test/section9_merge_$slug.out" "$1" "$3" test/corpus_driver.py "corpus_$slug.shard*.out" || return 1
  echo "$(date '+%F %T %Z') merged $3"
  grep "Results:" "$3" || echo "WARNING: no Results: line in $3"
}

for spec in "1 Algebraic functions" "2 Exponentials" "3 Logarithms" "6 Hyperbolic functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  run_class "$spec" "test/corpus_class$n.out" "test/corpus_class$n.s9-ref.out" "$REF_CORE" || exit 5
done
for spec in "1 Algebraic functions" "2 Exponentials" "3 Logarithms" "6 Hyperbolic functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  run_class "$spec" "test/corpus_class$n.s9-ref.out" "test/corpus_class$n.s9.out" "" || exit 6
done

for n in 1 2 3 6; do
  echo "== A/B class $n"
  python3 test/ab_records.py "test/corpus_class$n.s9-ref.out" "test/corpus_class$n.s9.out" --all \
    > "test/section9_ab_class$n.out" 2>&1
  tail -40 "test/section9_ab_class$n.out"
done

# 4. paired rerun: every entry whose verdict CLASS differs, both cores at
# once, 12 workers each (same total load as one 24-worker arm above).
# test/section9_changed.py labels every printed line `timeout` (not
# `changed`) so the existing wait_timeout_rerun.sh / merge_timeout_rerun.py
# path -- which hardcodes its completeness check to that literal class --
# runs unmodified; see that script's docstring.
for spec in "1 Algebraic functions" "2 Exponentials" "3 Logarithms" "6 Hyperbolic functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  python3 test/section9_changed.py "test/corpus_class$n.s9-ref.out" "test/corpus_class$n.s9.out" \
    > "test/section9_changed_class$n.out" || exit 7
  [ -s "test/section9_changed_class$n.out" ] || { echo "$(date '+%F %T %Z') class $n: no changed entries, skipping paired rerun"; continue; }
  for arm in ref new; do
    dir="test/section9_paired_class$n.$arm"
    mkdir -p "$dir"
    if [ "$arm" = ref ]; then core="$PWD/$REF_CORE"; else core="$PWD/test/mr_rules.core"; fi
    MR_RULES_CORE_PATH="$core" python3 test/run_corpus_queue.py "$spec" \
      --entries-from "test/section9_changed_class$n.out" --class timeout --out-dir "$dir" \
      --workers 12 --launch || exit 8
  done
  for arm in ref new; do
    dir="test/section9_paired_class$n.$arm"
    for pid in $(awk '{print $2}' "$dir/pids"); do while kill -0 "$pid" 2>/dev/null; do sleep 30; done; done
    sh test/wait_timeout_rerun.sh "$dir" >> "$dir/wait.log" 2>&1
  done
  echo "$(date '+%F %T %Z') paired class $n done"
done
echo "$(date '+%F %T %Z') ALL DONE"
