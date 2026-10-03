#!/bin/sh
cd "$(dirname "$0")/../../.." || exit 1
A=.scratch/answer-quality/rcfold_ab
for arm in off on off2 on2; do
  case $arm in off*) sw="mr_ifold=false";; *) sw="";; esac
  MR_SWITCHES="$sw" python3 test/run_corpus_queue.py "4 Trig functions" --entries-from $A/recheck4.txt --class recheck --out-dir $A/recheck4_$arm --workers 6 --launch
  while [ "$(cat $A/recheck4_$arm/shard*.out 2>/dev/null | grep -c ' e[0-9]* L')" -lt 6 ]; do sleep 10; done
  sleep 5
done
echo RECHECK4 DONE
