#!/bin/sh
# Attribute section 4's four PASS->FAIL (verified -> timeout at 30.0-30.6 s):
# the same entries, 4 workers, mr_ifold false then true, sequentially.
cd "$(dirname "$0")/../../.." || exit 1
A=.scratch/answer-quality/ifold_ab
for arm in false true; do
  for rep in 1 2; do
    d=$A/recheck_${arm}_$rep; rm -rf $d; mkdir -p $d
    MR_SWITCHES="mr_ifold=$arm" python3 test/run_corpus_queue.py "4 Trig functions" --entries-from $A/sec4_recheck.out --class recheck --out-dir $d --workers 4 --launch > $d/launch.log 2>&1
    pid=$(grep -o "launched the queue: pid [0-9]*" $d/launch.log | grep -o "[0-9]*$")
    while kill -0 $pid 2>/dev/null; do sleep 5; done
    echo "== mr_ifold=$arm rep $rep"; cat $d/*.shard*.out | grep -E "^[a-z-]+ +t=" | sort -k4
  done
done
echo RECHECK DONE
