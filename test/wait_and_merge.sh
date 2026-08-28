#!/bin/bash
# Wait for the shard driver processes (pids from the pids file) to
# exit, then run the completeness-checked merge. Launched detached
# (setsid) by the session that started the run.
#
# Usage: wait_and_merge.sh [pids-file] [merge-script] [merge-log]
#        [merger-arg ...]
# Defaults: the class-1 run (the documented AGENTS.md invocation).
# Positionals 4..N are passed through to the merge script as its own
# positionals (e.g. merge_class_shards.py's [SECTION] [OUT] [DRIVER]
# [SHARD-GLOB]); with none, the merger runs on its own defaults.
cd "$(dirname "$0")/.." || exit 1
PIDS=${1:-test/corpus_class1.shard-pids}
MERGE=${2:-test/merge_class1_shards.py}
MERGELOG=${3:-test/full_core_merge.out}
# Drop the three watcher positionals so "$@" holds only the
# merger's own positionals (empty if fewer than three were given).
[ $# -gt 0 ] && shift
[ $# -gt 0 ] && shift
[ $# -gt 0 ] && shift
pids=$(awk '{print $2}' "$PIDS")
echo "$(date -u '+%F %T UTC') watcher: waiting for pids: $pids"
for pid in $pids; do
  while kill -0 "$pid" 2>/dev/null; do sleep 120; done
done
echo "$(date -u '+%F %T UTC') watcher: all shards exited; merging"
python3 "$MERGE" "$@" > "$MERGELOG" 2>&1
rc=$?
echo "$(date -u '+%F %T UTC') watcher: merge rc=$rc" >> "$MERGELOG"
exit $rc
