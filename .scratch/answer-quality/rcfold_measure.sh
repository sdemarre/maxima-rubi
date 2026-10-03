#!/bin/sh
# RemoveContent's %i fold, acceptance run (plan
# docs/superpowers/plans/2026-10-03-removecontent-ifold.md Task 3): every
# section's rubi arm re-run and graded at HEAD, then the record A/B and the
# grade A/B against the records of BASE.
#   setsid sh .scratch/answer-quality/rcfold_measure.sh > .scratch/answer-quality/rcfold_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/../.." || exit 1
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 3 ]; then echo "REFUSING: 1-minute load $LOAD1 > 3"; exit 3; fi
BASE=$(git rev-parse --short HEAD)
AB=.scratch/answer-quality/rcfold_ab
mkdir -p "$AB"
echo "$(date '+%F %T %Z') base records at $BASE, tree $(git rev-parse --short HEAD), $(git status --porcelain | wc -l) uncommitted paths"
sh test/build_rules_core.sh || exit 4
for section in "0 Independent test suites" "2 Exponentials" "8 Special functions" \
    "3 Logarithms" "5 Inverse trig functions" "6 Hyperbolic functions" \
    "7 Inverse hyperbolic functions" "4 Trig functions" "1 Algebraic functions"; do
  n=$(echo "$section" | cut -d' ' -f1); slug="class$n"; out="test/corpus_$slug.out"
  git show "$BASE:$out" > "$AB/old_$slug.out"
  git show "$BASE:test/corpus_$slug.grade.out" > "$AB/old_$slug.grade.out"
  echo "$(date '+%F %T %Z') start rubi $section"
  python3 test/run_corpus_queue.py "$section" --prev "$AB/old_$slug.out" --workers 24 --launch || { echo "LAUNCH FAILED $section"; continue; }
  sh test/wait_and_merge.sh "test/corpus_$slug.shard-pids" test/merge_class_shards.py \
     "test/rcfold_merge_$slug.out" "$section" "$out" test/corpus_driver.py "corpus_$slug.shard*.out" || { echo "MERGE FAILED $section"; continue; }
  python3 test/merge_proof.py "$out" "test/corpus_$slug.proof.out" "corpus_$slug.shard*.proof" || echo "PROOF MERGE FAILED $section"
  python3 test/merge_grade.py "$out" "test/corpus_$slug.grade.out" "corpus_$slug.shard*.grade" || echo "GRADE MERGE FAILED $section"
  python3 test/ab_records.py "$AB/old_$slug.out" "$out" > "$AB/ab_records_$slug.txt" 2>&1
  python3 test/ab_grades.py "$AB/old_$slug.grade.out" "test/corpus_$slug.grade.out" > "$AB/ab_grades_$slug.txt" 2>&1
  echo "$(date '+%F %T %Z') done $section: $(grep -m1 'Results:' "$out") | $(tail -1 "$AB/ab_grades_$slug.txt")"
done
echo "$(date '+%F %T %Z') RCFOLD MEASURE DONE"
