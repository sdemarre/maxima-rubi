#!/bin/sh
# probes/verify-stages/12-values-appellf1-fixed.sh -- probe 11 re-measured on
# the checker after 1ffc606 (024c263's m, n, q, F value sets and AppellF1, and
# a stage timeout that no longer strands bindings or is swallowed) on probe 08's entry
# sets: the 1,551 `unverified` and the 1,000-entry control sample. The base
# is probe 08's arm B (rectform last = the checker's order since ac2fad6,
# same rules). 12 workers, 30 s cpu rubi + 30 s verification, 5 s per stage.
# From the repo root, detached:
#   setsid sh probes/verify-stages/12-values-appellf1-fixed.sh > probes/verify-stages/12-values-appellf1-fixed.log 2>&1 < /dev/null &
set -u
OUT=probes/verify-stages/12-values-appellf1-fixed
ENT=probes/verify-stages/08-stage-order/entries
for kind in unverified control; do
  cls=$kind; [ "$kind" = control ] && cls=verified
  for n in 1 2 3 4 5 6 7 8; do
    sec=$(ls reference/maxima-syntax-test-suite | grep "^$n ")
    dir=$OUT/$kind/class$n
    mkdir -p "$dir"
    echo "== $kind class $n $(date +%H:%M:%S)"
    python3 test/run_corpus_queue.py "$sec" --entries-from "$ENT/class$n.$kind.out" \
        --class "$cls" --out-dir "$dir" --workers 12 --launch > "$dir/launch.log" 2>&1 || { echo "   LAUNCH FAILED"; continue; }
    pid=$(awk '{print $2}' "$dir/pids")
    while kill -0 "$pid" 2>/dev/null; do sleep 10; done
    rm -f "$dir/pids"
  done
done
echo "ALL DONE $(date +%H:%M:%S)"
