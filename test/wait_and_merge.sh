#!/bin/bash
# Wait for the class-1 shard driver processes (pids from
# test/corpus_class1.shard-pids, any count) to exit, then run the
# completeness-checked merge (test/merge_class1_shards.py).
# Launched detached (setsid) by the session that started the run.
# Merge transcript: test/full_core_merge.out

cd "$(dirname "$0")/.." || exit 1   # this script lives in test/
pids=$(awk '{print $2}' test/corpus_class1.shard-pids)
echo "$(date -u '+%F %T UTC') watcher: waiting for pids: $pids"
for pid in $pids; do
  while kill -0 "$pid" 2>/dev/null; do sleep 120; done
done
echo "$(date -u '+%F %T UTC') watcher: all shards exited; merging"
python3 test/merge_class1_shards.py > test/full_core_merge.out 2>&1
rc=$?
echo "$(date -u '+%F %T UTC') watcher: merge rc=$rc" >> test/full_core_merge.out
exit $rc
