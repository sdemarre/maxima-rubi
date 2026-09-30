#!/bin/sh
# probes/verify-stages/01-unverified-subset.sh -- re-run exactly the
# `unverified` entries of master's current records (test/corpus_class<N>.pfs.out,
# 1,530 over classes 1-8) under the symbolic-first checker
# (.scratch/corpus-harness/issues/06): which stage proves each now, and what
# the rest look like numerically. Queue runner subset mode, 12 workers (the
# physical core count), 30 s cpu rubi cap + the driver's verification budget.
# From the repo root, detached:
#   setsid sh probes/verify-stages/01-unverified-subset.sh > probes/verify-stages/01-unverified-subset.log 2>&1 < /dev/null &
set -u
OUT=probes/verify-stages/01-unverified-subset
for n in 1 2 3 4 5 6 7 8; do
  sec=$(ls reference/maxima-syntax-test-suite | grep "^$n ")
  dir=$OUT/class$n
  mkdir -p "$dir"
  echo "== class $n ($sec) $(date -u +%H:%M:%S)"
  python3 test/run_corpus_queue.py "$sec" --entries-from test/corpus_class$n.pfs.out \
      --class unverified --out-dir "$dir" --workers 12 --launch || continue
  pid=$(awk '{print $2}' "$dir/pids")
  while kill -0 "$pid" 2>/dev/null; do sleep 10; done
  echo "   done $(date -u +%H:%M:%S)"
done
echo "ALL DONE $(date -u +%H:%M:%S)"
