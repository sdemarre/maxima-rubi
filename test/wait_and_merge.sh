#!/bin/bash
# Wait for the shard driver processes (pids from the pids file) to
# exit, then run the completeness-checked merge. Launched detached
# (setsid) by the session that started the run.
#
# Usage: wait_and_merge.sh [pids-file] [merge-script] [merge-log]
# Defaults: the class-1 run (the documented AGENTS.md invocation).
cd "$(dirname "$0")/.." || exit 1
PIDS=${1:-test/corpus_class1.shard-pids}
MERGE=${2:-test/merge_class1_shards.py}
MERGELOG=${3:-test/full_core_merge.out}
pids=$(awk '{print $2}' "$PIDS")
echo "$(date -u '+%F %T UTC') watcher: waiting for pids: $pids"
for pid in $pids; do
  while kill -0 "$pid" 2>/dev/null; do sleep 120; done
done
echo "$(date -u '+%F %T UTC') watcher: all shards exited; merging"
python3 "$MERGE" > "$MERGELOG" 2>&1
rc=$?
echo "$(date -u '+%F %T UTC') watcher: merge rc=$rc" >> "$MERGELOG"
exit $rc
