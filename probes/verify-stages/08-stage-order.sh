#!/bin/sh
# probes/verify-stages/08-stage-order.sh -- the checker's stage-order A/B
# (.scratch/corpus-harness/issues/06 items 1 and 4).
#   arm A: the checker's own stage list (rectform third in the radcan family);
#   arm B: MR_PROOF_STAGES with rectform moved LAST, after rat-radcan.
# Entries (08-stage-order-entries.py): every `unverified` entry of master's
# latest records (test/corpus_class<N>.geteqr.out, 1,551) and a seeded
# 1,000-entry control sample of their `verified` entries. The arms run one
# after the other, never concurrently, 12 workers (the physical core count),
# 30 s cpu rubi cap + 30 s verification, 5 s per stage.
# From the repo root, detached:
#   setsid sh probes/verify-stages/08-stage-order.sh > probes/verify-stages/08-stage-order.log 2>&1 < /dev/null &
set -u
OUT=probes/verify-stages/08-stage-order
ENT=$OUT/entries
B_ORDER="chainA.1,chainA.2,chainA.3,chainA.4,chainB.1,chainB.2,chainB.3,chainB.4,radcan,exponentialize,trigexpand,demoivre,logarc,rat-radcan,rectform"
run_arm() {
  arm=$1
  for kind in unverified control; do
    cls=$kind; [ "$kind" = control ] && cls=verified
    for n in 1 2 3 4 5 6 7 8; do
      sec=$(ls reference/maxima-syntax-test-suite | grep "^$n ")
      dir=$OUT/arm$arm/$kind/class$n
      mkdir -p "$dir"
      echo "== arm $arm $kind class $n $(date +%H:%M:%S)"
      python3 test/run_corpus_queue.py "$sec" --entries-from "$ENT/class$n.$kind.out" \
          --class "$cls" --out-dir "$dir" --workers 12 --launch > "$dir/launch.log" 2>&1 || { echo "   LAUNCH FAILED"; continue; }
      pid=$(awk '{print $2}' "$dir/pids")
      while kill -0 "$pid" 2>/dev/null; do sleep 10; done
    done
  done
}
run_arm A
MR_PROOF_STAGES=$B_ORDER run_arm B
echo "ALL DONE $(date +%H:%M:%S)"
