#!/bin/sh
# test/baseline_measure.sh -- the native baseline of every class on the
# driver's own path (MR_BASELINE=1, test/corpus_driver.py run_entry_detail):
# stock Maxima's integrate, then risch where integrate did not pass, the two
# sharing ONE 30 s CPU budget, timed without printf's stringproc autoload
# (`timing: printf-free+one-budget`, .scratch/corpus-harness/issues/11), the
# symbolic-first checker with its own 30 s budget. Per class N:
#   test/corpus_class<N>.baseline.out        the merged record
#   test/corpus_class<N>.baseline.proof.out  the checker's proof census
#   test/corpus_class<N>.baseline.via.out    which integrator, both runs
#   test/corpus_class<N>.baseline.grade.out  the grade census
#   test/baseline_ab_class<N>.out            A/B against the rubi record
#                                            test/corpus_class<N>.out
#   test/baseline11_ab_class<N>.out          A/B, records, against the record
#   test/baseline11_abgrade_class<N>.out     A/B, grades,   before issue 11
#   test/baseline11_attrib_class<N>.out      its PASS -> FAIL attributed to
#                                            the one budget (attrib_one_budget.py)
# The before-issue-11 records are read from git (BASE_REV, default 4a90538,
# where they are the 2026-09-30/10-01 records) into BASE_DIR.
# 24 workers, as the rubi records it is compared with. Resumes: a class whose
# record states the issue-11 timing mode and whose grade census is newer is
# kept (its A/Bs are re-written).
#   setsid sh test/baseline_measure.sh > test/baseline_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.." || exit 1
export MR_BASELINE=1
echo "$(date '+%F %T %Z') host check"; uptime
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 3 ]; then echo "REFUSING: 1-minute load $LOAD1 > 3"; exit 3; fi
echo "$(date '+%F %T %Z') tree: $(git rev-parse --short HEAD) $(git status --porcelain | wc -l) uncommitted paths"

BASE_REV=${BASE_REV:-4a90538}
BASE_DIR=.scratch/corpus-harness/baseline-pre11
mkdir -p "$BASE_DIR"
for n in 0 1 2 3 4 5 6 7 8; do
  for suf in out via.out grade.out; do
    f="corpus_class$n.baseline.$suf"
    [ -s "$BASE_DIR/$f" ] || git show "$BASE_REV:test/$f" > "$BASE_DIR/$f" \
      || { echo "REFUSING: no $f at $BASE_REV"; exit 5; }
  done
done

CLASSES="0 Independent test suites|2 Exponentials|8 Special functions|3 Logarithms|5 Inverse trig functions|6 Hyperbolic functions|7 Inverse hyperbolic functions|4 Trig functions|1 Algebraic functions"

run_class() {  # $1 section
  n=$(echo "$1" | cut -d' ' -f1)
  slug="class$n.baseline"
  out="test/corpus_class$n.baseline.out"
  base="${out%.out}"
  if grep -q "timing: printf-free+one-budget" "$out" 2>/dev/null \
     && [ -f "$base.grade.out" ] && [ "$base.grade.out" -nt "$out" ]; then
    echo "$(date '+%F %T %Z') keep $1: $out is already the issue-11 record"
  else
    echo "$(date '+%F %T %Z') start $1 -> $out"
    python3 test/run_corpus_queue.py "$1" --prev "$BASE_DIR/corpus_class$n.baseline.out" \
      --workers 24 --launch || return 1
    sh test/wait_and_merge.sh "test/corpus_$slug.shard-pids" test/merge_class_shards.py \
       "test/baseline_merge_class$n.out" "$1" "$out" test/corpus_driver.py \
       "corpus_$slug.shard*.out" || return 1
    echo "$(date '+%F %T %Z') merged $out"; grep "Results:" "$out"
    python3 test/merge_proof.py "$out" "$base.proof.out" "corpus_$slug.shard*.proof" \
      || echo "PROOF MERGE FAILED $1"
    python3 test/merge_via.py "$out" "$base.via.out" "corpus_$slug.shard*.via" \
      || echo "VIA MERGE FAILED $1"
    python3 test/merge_grade.py "$out" "$base.grade.out" "corpus_$slug.shard*.grade" \
      || echo "GRADE MERGE FAILED $1"
  fi
  [ -f "test/corpus_class$n.out" ] && python3 test/ab_records.py "$out" "test/corpus_class$n.out" \
    > "test/baseline_ab_class$n.out" 2>&1
  python3 test/ab_records.py "$BASE_DIR/corpus_class$n.baseline.out" "$out" \
    > "test/baseline11_ab_class$n.out" 2>&1
  python3 test/ab_grades.py "$BASE_DIR/corpus_class$n.baseline.grade.out" "$base.grade.out" \
    > "test/baseline11_abgrade_class$n.out" 2>&1
  python3 test/attrib_one_budget.py "$BASE_DIR/corpus_class$n.baseline.out" \
    "$BASE_DIR/corpus_class$n.baseline.via.out" "$out" "$base.via.out" \
    > "test/baseline11_attrib_class$n.out" 2>&1
  echo "$(date '+%F %T %Z') done $1: $(tail -1 "test/baseline11_attrib_class$n.out")"
}

rc=0
OLDIFS=$IFS; IFS='|'
for section in $CLASSES; do
  IFS=$OLDIFS
  run_class "$section" || { echo "$(date '+%F %T %Z') FAILED $section"; rc=1; }
  IFS='|'
done
IFS=$OLDIFS
echo "$(date '+%F %T %Z') ALL DONE rc=$rc"
exit $rc
