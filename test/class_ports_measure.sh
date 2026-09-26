#!/bin/sh
# test/class_ports_measure.sh -- Steps 8-9 of the class 8/5/7/4 ports
# (docs/class-porting.md), chained in ONE detached script (memory: chain
# overnight follow-ups), on the class-ports core:
#   1. package runs of the four new sections (queue runner, 24 workers,
#      30 s cpu cap) -> test/corpus_class{8,5,7,4}.out;
#   2. the re-measure of classes 2/3/6/1 on the same core -> .ports.out,
#      A/B'd against the section-9 branch records (.s9b.out, main worktree);
#   3. the native-`integrate` baselines of the four new sections (one shard
#      per file, 12-process pool) -> test/corpus_class{N}.baseline.out;
#   4. ab_records.py baseline vs package per new section;
#   5. the 100 s timeout re-check of each new section's record.
#
#   setsid sh test/class_ports_measure.sh > test/class_ports_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.." || exit 1
S9B=${MR_S9B_DIR:-../maxima-rubi/test}

echo "$(date '+%F %T %Z') host check"
uptime
LOAD1=$(awk '{print int($1)}' /proc/loadavg)
if [ "$LOAD1" -gt 3 ]; then echo "REFUSING: 1-minute load $LOAD1 > 3 -- quiet the host first"; exit 3; fi

sh test/build_rules_core.sh || exit 4
echo "$(date '+%F %T %Z') core: $(awk '/^fingerprint /{print $2}' test/mr_rules.core.stamp) ($(awk '/^rules /{print $2}' test/mr_rules.core.stamp) rules, $(git rev-parse --short HEAD))"

run_class() {  # $1 section  $2 prev-record-or-empty  $3 out-record
  slug="class$(echo "$1" | cut -d' ' -f1)"
  echo "$(date '+%F %T %Z') start $1 -> $3"
  if [ -n "$2" ]; then
    python3 test/run_corpus_queue.py "$1" --prev "$2" --workers 24 --launch || return 1
  else
    python3 test/run_corpus_queue.py "$1" --workers 24 --launch || return 1
  fi
  sh test/wait_and_merge.sh "test/corpus_$slug.shard-pids" test/merge_class_shards.py \
     "test/ports_merge_$slug.out" "$1" "$3" test/corpus_driver.py "corpus_$slug.shard*.out" || return 1
  echo "$(date '+%F %T %Z') merged $3"
  grep "Results:" "$3" || echo "WARNING: no Results: line in $3"
}

# 1. the new sections
for spec in "8 Special functions" "5 Inverse trig functions" "7 Inverse hyperbolic functions" "4 Trig functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  run_class "$spec" "" "test/corpus_class$n.out" || echo "FAILED package run class $n"
done

# 2. the earlier sections on the same core
for spec in "2 Exponentials" "3 Logarithms" "6 Hyperbolic functions" "1 Algebraic functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  run_class "$spec" "$S9B/corpus_class$n.s9b.out" "test/corpus_class$n.ports.out" || { echo "FAILED re-measure class $n"; continue; }
  python3 test/ab_records.py "$S9B/corpus_class$n.s9b.out" "test/corpus_class$n.ports.out" --all \
    > "test/ports_ab_class$n.out" 2>&1
  head -30 "test/ports_ab_class$n.out"
done

# 3. baselines (native integrate, no rule core)
for spec in "8 Special functions" "5 Inverse trig functions" "7 Inverse hyperbolic functions" "4 Trig functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  echo "$(date '+%F %T %Z') baseline $spec"
  python3 test/run_baseline_pool.py "$spec" "test/corpus_class$n.baseline.out" 12 \
    > "test/ports_baseline_class$n.log" 2>&1 || echo "FAILED baseline class $n"
  tail -3 "test/ports_baseline_class$n.log"
  grep "Results:" "test/corpus_class$n.baseline.out"
done

# 4. A/B baseline vs package
for n in 8 5 7 4; do
  python3 test/ab_records.py "test/corpus_class$n.baseline.out" "test/corpus_class$n.out" \
    > "test/ports_ab_baseline_class$n.out" 2>&1
  echo "== class $n baseline vs package"; head -12 "test/ports_ab_baseline_class$n.out"
done

# 5. 100 s timeout re-check of each new record
for spec in "8 Special functions" "5 Inverse trig functions" "7 Inverse hyperbolic functions" "4 Trig functions"; do
  n=$(echo "$spec" | cut -d' ' -f1)
  grep -q "^timeout " "test/corpus_class$n.out" || { echo "class $n: no timeouts"; continue; }
  dir="test/corpus_class$n.timeout-rerun"
  rm -rf "$dir"; mkdir -p "$dir"
  python3 test/run_corpus_queue.py "$spec" --entries-from "test/corpus_class$n.out" --class timeout \
    --out-dir "$dir" --cap 100 --workers 12 --launch || { echo "FAILED re-check launch $n"; continue; }
  for pid in $(awk '{print $2}' "$dir/pids"); do while kill -0 "$pid" 2>/dev/null; do sleep 30; done; done
  sh test/wait_timeout_rerun.sh "$dir" >> "$dir/wait.log" 2>&1
  echo "$(date '+%F %T %Z') re-check class $n done"; tail -5 "$dir/merge.out" 2>/dev/null
done
echo "$(date '+%F %T %Z') ALL DONE"
