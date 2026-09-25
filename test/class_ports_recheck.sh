#!/bin/sh
# test/class_ports_recheck.sh -- the tail of test/class_ports_measure.sh (its
# steps 4-5), run separately: the 100 s re-check of all 7,034 timeouts at 12
# workers could take ~16 h, so class 4's 5,716 are re-checked on a SEEDED
# 600-entry sample (test/corpus_class4.timeout-sample.out); 8/5/7 in full.
# Waits for the class-4 baseline pool (pid $1) first.
#   setsid sh test/class_ports_recheck.sh <baseline-pool-pid> >> test/class_ports_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.." || exit 1
while kill -0 "$1" 2>/dev/null; do sleep 60; done
echo "$(date '+%F %T %Z') class-4 baseline pool exited"; tail -3 test/ports_baseline_class4.log
for n in 8 5 7 4; do
  python3 test/ab_records.py "test/corpus_class$n.baseline.out" "test/corpus_class$n.out" \
    > "test/ports_ab_baseline_class$n.out" 2>&1
  echo "== class $n baseline vs package"; sed -n 1,10p "test/ports_ab_baseline_class$n.out"
done
for spec in "8 Special functions|test/corpus_class8.out" "5 Inverse trig functions|test/corpus_class5.out" \
            "7 Inverse hyperbolic functions|test/corpus_class7.out" "4 Trig functions|test/corpus_class4.timeout-sample.out"; do
  sec=${spec%%|*}; src=${spec#*|}; n=$(echo "$sec" | cut -d' ' -f1)
  dir="test/corpus_class$n.timeout-rerun"
  rm -rf "$dir"; mkdir -p "$dir"
  python3 test/run_corpus_queue.py "$sec" --entries-from "$src" --class timeout \
    --out-dir "$dir" --cap 100 --workers 12 --launch || { echo "FAILED re-check launch $n"; continue; }
  for pid in $(awk '{print $2}' "$dir/pids"); do while kill -0 "$pid" 2>/dev/null; do sleep 30; done; done
  sh test/wait_timeout_rerun.sh "$dir" >> "$dir/wait.log" 2>&1
  echo "$(date '+%F %T %Z') re-check class $n done"; tail -12 "$dir/merge.out" 2>/dev/null
done
echo "$(date '+%F %T %Z') RECHECK ALL DONE"
