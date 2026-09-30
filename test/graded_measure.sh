#!/bin/sh
# test/graded_measure.sh -- rubi and the native baseline (integrate, then
# risch) over one or more corpus sections, with every census: the record, the
# checker's proof census, the grade census (leaf size and the A/B/C/F grade
# of the 12000.org independent integration tests, test/mr_grade.lisp,
# docs/grading-and-leaf-size.md) and, for
# the baseline, the integrator census. Per section N:
#   test/corpus_class<N>.out                  rubi         (+ .proof.out, .grade.out)
#   test/corpus_class<N>.baseline.out         integrate+risch (+ .proof.out, .grade.out, .via.out)
# 24 workers, 30 s CPU per integrator, 30 s CPU of verification.
#   setsid sh test/graded_measure.sh "0 Independent test suites" > test/graded_measure.log 2>&1 < /dev/null &
# An arm whose grade census exists and is newer than its record is kept.
set -u
cd "$(dirname "$0")/.." || exit 1
echo "$(date '+%F %T %Z') host check"; uptime
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 3 ]; then echo "REFUSING: 1-minute load $LOAD1 > 3"; exit 3; fi
echo "$(date '+%F %T %Z') tree: $(git rev-parse --short HEAD) $(git status --porcelain | wc -l) uncommitted paths"
sh test/build_rules_core.sh || exit 4

run_arm() {  # $1 section  $2 arm (rubi|baseline)
  n=$(echo "$1" | cut -d' ' -f1)
  if [ "$2" = baseline ]; then slug="class$n.baseline"; export MR_BASELINE=1
  else slug="class$n"; unset MR_BASELINE; fi
  out="test/corpus_$slug.out"
  base="${out%.out}"
  if [ -f "$base.grade.out" ] && [ "$base.grade.out" -nt "$out" ]; then
    echo "$(date '+%F %T %Z') keep $2 $1: $base.grade.out exists"; return 0
  fi
  echo "$(date '+%F %T %Z') start $2 $1 -> $out"
  python3 test/run_corpus_queue.py "$1" --workers 24 --launch || return 1
  sh test/wait_and_merge.sh "test/corpus_$slug.shard-pids" test/merge_class_shards.py \
     "test/graded_merge_$slug.out" "$1" "$out" test/corpus_driver.py "corpus_$slug.shard*.out" || return 1
  echo "$(date '+%F %T %Z') merged $out"; grep "Results:" "$out"
  python3 test/merge_proof.py "$out" "$base.proof.out" "corpus_$slug.shard*.proof" || echo "PROOF MERGE FAILED $2 $1"
  if [ "$2" = baseline ]; then
    python3 test/merge_via.py "$out" "$base.via.out" "corpus_$slug.shard*.via" || echo "VIA MERGE FAILED $2 $1"
  fi
  python3 test/merge_grade.py "$out" "$base.grade.out" "corpus_$slug.shard*.grade" || echo "GRADE MERGE FAILED $2 $1"
  echo "$(date '+%F %T %Z') done $2 $1"
}

rc=0
for section in "$@"; do
  for arm in rubi baseline; do
    run_arm "$section" "$arm" || { echo "$(date '+%F %T %Z') FAILED $arm $section"; rc=1; }
  done
done
echo "$(date '+%F %T %Z') ALL DONE rc=$rc"
exit $rc
