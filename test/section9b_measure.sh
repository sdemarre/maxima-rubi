#!/bin/sh
# test/section9b_measure.sh -- the post-ticket-14/15 re-measure of classes
# 1/2/3/6 on the branch core (handoff 2026-09-24, next move 1), chained in
# ONE detached script. Unlike test/section9_measure.sh it does NOT re-run the
# reference arm: test/corpus_class{N}.s9-ref.out (core 0182d32c, quiet host,
# 24 workers) IS the baseline. Steps:
#   1. branch core, classes 2/3/6/1 (short classes first) -> .s9b.out;
#   2. ab_records.py s9-ref vs s9b, per class;
#   3. the PAIRED rerun of every verdict-class change (both cores
#      concurrently, 12 workers each), for attribution.
# .s9.out (the pre-fix branch records tickets 14/15 cite) is never touched.
#
#   setsid sh test/section9b_measure.sh > test/section9b_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.." || exit 1
REF=../mr-s9-ref
REF_CORE="$REF/test/mr_rules.core"
REF_STAMP="$REF_CORE.stamp"
EXPECT_REF_FP=0182d32ce35fda4b93d3f33d2ad8b43a
TAG=${MR_S9_TAG:-s9b}

echo "$(date '+%F %T %Z') host check"
uptime; ps -eo pcpu,comm --sort=-pcpu | head -6
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 2 ]; then echo "REFUSING: 1-minute load $LOAD1 > 2 -- quiet the host first"; exit 3; fi

[ -f "$REF_CORE" ] && [ -f "$REF_STAMP" ] || { echo "REFUSING: reference core/stamp missing at $REF_CORE"; exit 4; }
REF_FP=$(awk '/^fingerprint /{print $2}' "$REF_STAMP")
[ "$REF_FP" = "$EXPECT_REF_FP" ] || { echo "REFUSING: reference core fingerprint $REF_FP != $EXPECT_REF_FP"; exit 4; }

sh test/build_rules_core.sh || exit 4
echo "$(date '+%F %T %Z') branch core: fingerprint $(awk '/^fingerprint /{print $2}' test/mr_rules.core.stamp) ($(awk '/^rules /{print $2}' test/mr_rules.core.stamp) rules, $(git rev-parse --short HEAD))"

run_class() {  # $1 section  $2 prev-record  $3 out-record
  slug="class$(echo "$1" | cut -d' ' -f1)"
  echo "$(date '+%F %T %Z') start $1 -> $3"
  python3 test/run_corpus_queue.py "$1" --prev "$2" --workers 24 --launch || return 1
  sh test/wait_and_merge.sh "test/corpus_$slug.shard-pids" test/merge_class_shards.py \
     "test/section9b_merge_$slug.out" "$1" "$3" test/corpus_driver.py "corpus_$slug.shard*.out" || return 1
  echo "$(date '+%F %T %Z') merged $3"
  grep "Results:" "$3" || echo "WARNING: no Results: line in $3"
}

for spec in "2 Exponentials" "3 Logarithms" "6 Hyperbolic functions" "1 Algebraic functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  run_class "$spec" "test/corpus_class$n.s9-ref.out" "test/corpus_class$n.$TAG.out" || exit 5
  python3 test/ab_records.py "test/corpus_class$n.s9-ref.out" "test/corpus_class$n.$TAG.out" --all \
    > "test/section9b_ab_class$n.out" 2>&1
  head -30 "test/section9b_ab_class$n.out"
done

for spec in "2 Exponentials" "3 Logarithms" "6 Hyperbolic functions" "1 Algebraic functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  python3 test/section9_changed.py "test/corpus_class$n.s9-ref.out" "test/corpus_class$n.$TAG.out" \
    > "test/section9b_changed_class$n.out" || exit 7
  [ -s "test/section9b_changed_class$n.out" ] || { echo "$(date '+%F %T %Z') class $n: no changed entries"; continue; }
  echo "$(date '+%F %T %Z') paired class $n: $(wc -l < test/section9b_changed_class$n.out) entries"
  for arm in ref new; do
    dir="test/section9b_paired_class$n.$arm"
    rm -rf "$dir"; mkdir -p "$dir"
    if [ "$arm" = ref ]; then core="$PWD/$REF_CORE"; else core="$PWD/test/mr_rules.core"; fi
    MR_RULES_CORE_PATH="$core" python3 test/run_corpus_queue.py "$spec" \
      --entries-from "test/section9b_changed_class$n.out" --class timeout --out-dir "$dir" \
      --workers 12 --launch || exit 8
  done
  for arm in ref new; do
    dir="test/section9b_paired_class$n.$arm"
    for pid in $(awk '{print $2}' "$dir/pids"); do while kill -0 "$pid" 2>/dev/null; do sleep 30; done; done
    sh test/wait_timeout_rerun.sh "$dir" >> "$dir/wait.log" 2>&1
  done
  echo "$(date '+%F %T %Z') paired class $n done"
done
echo "$(date '+%F %T %Z') ALL DONE"
