#!/bin/sh
# test/baseline_measure.sh -- the native baseline of every class on the
# driver's own path (MR_BASELINE=1, test/corpus_driver.py run_entry_detail):
# stock Maxima's integrate, then risch where integrate did not pass, 30 s CPU
# each, the symbolic-first checker with its own 30 s budget (user decision
# 2026-09-30). Per class N:
#   test/corpus_class<N>.baseline.out        the merged record (replaces the
#                                            old probe's wall-capped record)
#   test/corpus_class<N>.baseline.proof.out  the checker's proof census
#   test/corpus_class<N>.baseline.via.out    which integrator, both runs
#   test/baseline_ab_class<N>.out            A/B against the rubi record
#                                            test/corpus_class<N>.chk2-head.out
# 24 workers, as the rubi records it is compared with. Resumes: a class whose
# record already states the integrate+risch arm is kept.
#   setsid sh test/baseline_measure.sh > test/baseline_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.." || exit 1
export MR_BASELINE=1
echo "$(date '+%F %T %Z') host check"; uptime
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 3 ]; then echo "REFUSING: 1-minute load $LOAD1 > 3"; exit 3; fi
echo "$(date '+%F %T %Z') tree: $(git rev-parse --short HEAD) $(git status --porcelain | wc -l) uncommitted paths"

CLASSES="2 Exponentials|8 Special functions|3 Logarithms|5 Inverse trig functions|6 Hyperbolic functions|7 Inverse hyperbolic functions|4 Trig functions|1 Algebraic functions"

run_class() {  # $1 section
  n=$(echo "$1" | cut -d' ' -f1)
  slug="class$n.baseline"
  out="test/corpus_class$n.baseline.out"
  if grep -q "integrate+risch baseline" "$out" 2>/dev/null; then
    echo "$(date '+%F %T %Z') keep $1: $out is already the integrate+risch record"
  else
    echo "$(date '+%F %T %Z') start $1 -> $out"
    python3 test/run_corpus_queue.py "$1" --prev "$out" --workers 24 --launch || return 1
    sh test/wait_and_merge.sh "test/corpus_$slug.shard-pids" test/merge_class_shards.py \
       "test/baseline_merge_class$n.out" "$1" "$out" test/corpus_driver.py \
       "corpus_$slug.shard*.out" || return 1
    echo "$(date '+%F %T %Z') merged $out"; grep "Results:" "$out"
  fi
  [ -f "test/corpus_class$n.baseline.proof.out" ] && grep -q "$out" "test/corpus_class$n.baseline.proof.out" \
    && [ "test/corpus_class$n.baseline.proof.out" -nt "$out" ] \
    || python3 test/merge_proof.py "$out" "test/corpus_class$n.baseline.proof.out" \
         "corpus_$slug.shard*.proof" || echo "PROOF MERGE FAILED $1"
  [ -f "test/corpus_class$n.baseline.via.out" ] && [ "test/corpus_class$n.baseline.via.out" -nt "$out" ] \
    || python3 test/merge_via.py "$out" "test/corpus_class$n.baseline.via.out" \
         "corpus_$slug.shard*.via" || echo "VIA MERGE FAILED $1"
  python3 test/ab_records.py "$out" "test/corpus_class$n.chk2-head.out" \
    > "test/baseline_ab_class$n.out" 2>&1
  echo "$(date '+%F %T %Z') done $1"
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
