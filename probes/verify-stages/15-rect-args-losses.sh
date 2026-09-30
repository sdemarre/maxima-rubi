#!/bin/sh
# probes/verify-stages/15-rect-args-losses.sh -- are arm 1's PASS->FAIL entries
# (test/checker_measure.sh: the new checker on master's rules vs the geteqr
# records, 69 losses, 65 reproduce) lost to the checker's 5 s per-stage cap?
# The old zero chain had no per-stage cap. Re-run exactly those entries
# (test/corpus_class<N>.chk-master.tr.out) on master's pinned core at the
# default caps (5 s per stage, 30 s verification) after the breadth-first order and mr_rect_args (probe 15). 12 workers.
#   MASTER_CORE=<dir> setsid sh probes/verify-stages/15-rect-args-losses.sh > probes/verify-stages/15-rect-args-losses.log 2>&1 < /dev/null &
set -u
: "${MASTER_CORE:?}"
OUT=probes/verify-stages/15-rect-args-losses
for n in 1 2 3 4 5 6 7 8; do
  src=test/corpus_class$n.chk-master.tr.out
  [ -f "$src" ] && [ "$(grep -c '^recheck' "$src")" -gt 0 ] || continue
  sec=$(ls reference/maxima-syntax-test-suite | grep "^$n ")
  dir=$OUT/class$n; mkdir -p "$dir"
  echo "== class $n $(date +%H:%M:%S)"
  MR_RULES_CORE_PATH="$MASTER_CORE/mr_rules.core" \
    python3 test/run_corpus_queue.py "$sec" --entries-from "$src" --class recheck \
      --out-dir "$dir" --workers 12 --launch > "$dir/launch.log" 2>&1 || { echo "LAUNCH FAILED $n"; continue; }
  pid=$(awk '{print $2}' "$dir/pids")
  while kill -0 "$pid" 2>/dev/null; do sleep 10; done
  rm -f "$dir/pids"
done
echo "ALL DONE $(date +%H:%M:%S)"
